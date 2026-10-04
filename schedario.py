# MeTeOra, lo schedario: durata, dimensione e tag dei file, ricordati fra un avvio e l'altro.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la 1.7.0, per le durate delle playlist (issue 4) e poi per il filtro (issue 2). Nella 1.62.4 le durate da libmpv per i formati che mutagen non conosce, e quella esatta dell'AAC grezzo. Nella 1.66.0 le schede della musica delle console, con i sottobrani. Nella 1.67.0 la scheda segue un file rinominato. Nella 1.69.0 i tag letti con tag.py, anche di WAV, AIFF, WMA e TTA. Nella 1.83.1 le variazioni delle schede, per i totali delle cartelle, e il filo che cede il passo alla finestra.

"""Lo schedario dei file.

Per ogni file suonabile tiene dimensione, data di modifica, durata e tag.
Leggerli costa: un MP3 va aperto con mutagen, un SID va letto per intero per
cercarne la durata nel database di HVSC. Percio' lo schedario li ricorda in
un file JSON e li rilegge solo quando il file cambia.
Il lavoro lo fa un filo a parte: chi chiede una scheda la trova subito se
c'e', altrimenti la chiede e viene avvisato quando arriva. In ogni sessione
ogni file si ricontrolla una volta, confrontando dimensione e data.
"""

import atexit
import contextlib
import json
import mmap
import os
import queue
import threading
import time

import formati
import sottobrani
import tag

# La versione della lettura dei tag, e quella che serve a ogni formato:
# prima della 1.69.0 lo schedario non leggeva i tag di WAV, AIFF, WMA, WMV e
# TTA, e prima della 1.70.0 il blocco INFO dei WAV. Le schede piu' vecchie si
# rileggono.
VERSIONE_DEI_TAG = 2
TAG_DA_RILEGGERE = {".wav": 2, ".aif": 1, ".aiff": 1, ".wma": 1, ".wmv": 1, ".asf": 1, ".tta": 1}

VERSIONE_DEL_FILE = 1
# Le chiavi dei tag, come le usa il filtro.
TAG = ("titolo", "autore", "album", "genere", "anno")
# Si avvisa chi aspetta al massimo una volta ogni tanti secondi, e alla fine.
INTERVALLO_DEGLI_AVVISI = 1.0
# Quanto aspetta il filo, a ogni giro, mentre deve cedere il passo.
PAUSA_PER_CEDERE = 0.005


def _anno(testo):
    """Il primo anno di quattro cifre in un testo, come numero; None se non c'e'."""
    for i in range(len(testo) - 3):
        pezzo = testo[i:i + 4]
        if pezzo.isdigit() and 1900 <= int(pezzo) <= 2100:
            return int(pezzo)
    return None


# Le frequenze dell'AAC grezzo (ADTS), per indice.
_FREQUENZE_ADTS = (96000, 88200, 64000, 48000, 44100, 32000, 24000, 22050, 16000, 12000, 11025, 8000, 7350)
# Quanto si aspetta libmpv per un file, al massimo.
ATTESA_DELLA_SONDA = 5.0


def durata_adts(percorso):
    """La durata vera di un AAC grezzo (ADTS), contando i fotogrammi: il
    formato non la scrive, e mutagen e FFmpeg la stimano dal bitrate,
    sbagliando di molto (tappa 6, 1.62.4). None se non e' un ADTS."""
    with open(percorso, "rb") as f:
        if os.fstat(f.fileno()).st_size < 7:
            return None
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as dati:
            posizione = 0
            if dati[:3] == b"ID3" and len(dati) >= 10:
                posizione = 10 + ((dati[6] & 0x7F) << 21 | (dati[7] & 0x7F) << 14 | (dati[8] & 0x7F) << 7 | (dati[9] & 0x7F))
            campioni, frequenza = 0, None
            while posizione + 7 <= len(dati):
                testa = dati[posizione:posizione + 7]
                indice = (testa[2] >> 2) & 0x0F
                lunghezza = ((testa[3] & 0x03) << 11) | (testa[4] << 3) | (testa[5] >> 5)
                if testa[0] != 0xFF or (testa[1] & 0xF6) != 0xF0 or lunghezza < 7 or indice >= len(_FREQUENZE_ADTS):
                    break
                frequenza = frequenza or _FREQUENZE_ADTS[indice]
                campioni += 1024 * ((testa[6] & 0x03) + 1)
                posizione += lunghezza
    return campioni / frequenza if frequenza else None


class _Sonda:
    """Un'istanza di libmpv muta e in pausa, che apre un file solo per
    leggerne la durata: per i formati che mutagen non conosce, come Matroska,
    AU, CAF e i tracker (tappa 6, 1.62.4)."""

    def __init__(self):
        import motore

        self._mpv_modulo = motore.mpv
        # Muta per l'uscita nulla e la pausa: con audio=no mpv chiuderebbe il
        # file senza dire la durata.
        self._mpv = motore.mpv.MPV(**{**motore.OPZIONI_DI_BASE, "ao": "null", "pause": True})
        self._caricato = threading.Event()
        self._mpv.register_event_callback(self._evento)

    def _evento(self, evento):
        # Il file e' aperto, o non si apre: la fine per lo stop del file di
        # prima non conta.
        identita = evento.event_id.value
        errore = identita == self._mpv_modulo.MpvEventID.END_FILE and evento.data.reason == self._mpv_modulo.MpvEventEndFile.ERROR
        if identita == self._mpv_modulo.MpvEventID.FILE_LOADED or errore:
            self._caricato.set()

    def durata(self, percorso):
        self._caricato.clear()
        try:
            self._mpv.loadfile(percorso)
            if not self._caricato.wait(ATTESA_DELLA_SONDA):
                return None
            durata = self._mpv.duration
        except Exception:  # noqa: BLE001 - un file rovinato non deve fermare lo schedario
            return None
        finally:
            with contextlib.suppress(Exception):
                self._mpv.stop()
        return float(durata) if durata else None

    def chiudi(self):
        self._mpv.terminate()


_SONDA = []
_SONDA_BLOCCO = threading.Lock()


def durata_da_mpv(percorso):
    """La durata letta da libmpv, con la sonda aperta alla prima richiesta e
    chiusa all'uscita; None se libmpv non la sa."""
    with _SONDA_BLOCCO:
        if not _SONDA:
            _SONDA.append(_Sonda())
            atexit.register(_SONDA[0].chiudi)
        return _SONDA[0].durata(percorso)


def leggi_scheda(percorso):
    """La scheda di un file: dimensione, data di modifica, durata in secondi
    (None se non si sa), tag, e per i SID e le console il numero dei
    sottobrani."""
    stato = os.stat(percorso)
    scheda = {"dim": stato.st_size, "mod": stato.st_mtime, "durata": None, "tag": {}, "sottobrani": None, "durate_sid": None}
    if formati.ha_sottobrani(percorso):
        # SID e console. La chiave durate_sid tiene il suo nome anche per le
        # console: e' quello degli schedari gia' salvati.
        info = sottobrani.info(percorso)
        if info:
            scheda["tag"] = {"titolo": info["titolo"], "autore": info["autore"], "anno": _anno(info["copyright"])}
            scheda["tag"] = {chiave: valore for chiave, valore in scheda["tag"].items() if valore}
            scheda["sottobrani"] = info["sottobrani"]
            durate = sottobrani.durate(percorso)
            scheda["durate_sid"] = durate
            iniziale = info["iniziale"] or 1
            if durate and iniziale <= len(durate):
                scheda["durata"] = durate[iniziale - 1]
        return scheda
    try:
        import mutagen

        # I formati di cui MeTeOra scrive i tag si leggono come li legge tag.py,
        # senza la modalita' easy, che per WAV, AIFF, WMA e TTA non ha i nomi
        # comuni (1.69.0).
        audio = mutagen.File(percorso, easy=not tag.modificabile(percorso))
    except Exception:  # noqa: BLE001 - un file rovinato non deve fermare lo schedario
        audio = None
    if formati.estensione(percorso) == ".aac":
        with contextlib.suppress(OSError, ValueError):
            scheda["durata"] = durata_adts(percorso)
    elif formati.estensione(percorso) in formati.MIDI:
        # mutagen.File non riconosce i MIDI: la durata la da' la sua classe
        # SMF, dalla mappa dei tempi (1.65.0).
        import midi

        scheda["durata"] = midi.durata(percorso)
    if audio is not None and scheda["durata"] is None and getattr(audio, "info", None) is not None and getattr(audio.info, "length", None):
        scheda["durata"] = float(audio.info.length)
    if scheda["durata"] is None:
        scheda["durata"] = durata_da_mpv(percorso)
    if audio is not None and tag.modificabile(percorso):
        comuni = tag.comuni_del_file(audio)
        anno = comuni.get("anno")
        scheda["tag"] = {"titolo": comuni.get("titolo"), "autore": comuni.get("artista"), "album": comuni.get("album"),
            "genere": comuni.get("genere"), "anno": _anno(anno) if anno else None}
        scheda["tag"] = {k: v for k, v in scheda["tag"].items() if v}
        # Il segno della lettura dei tag con tag.py: le schede di prima della
        # 1.69.0 dei formati che la modalita' easy non leggeva si rifanno.
        scheda["tag_v"] = VERSIONE_DEI_TAG
    elif audio is not None:
        tags = audio.tags or {}

        def primo(chiave):
            with contextlib.suppress(Exception):
                valore = tags.get(chiave)
                if valore:
                    return str(valore[0] if isinstance(valore, list) else valore)
            return None

        anno = primo("date") or primo("year")
        scheda["tag"] = {"titolo": primo("title"), "autore": primo("artist"), "album": primo("album"), "genere": primo("genre"),
            "anno": _anno(anno) if anno else None}
        scheda["tag"] = {k: v for k, v in scheda["tag"].items() if v}
    return scheda


class Schedario:
    def __init__(self, percorso, avvisa=None):
        """avvisa() viene chiamata dal filo dello schedario quando arrivano
        schede nuove: chi la passa deve riportarla nel suo filo."""
        self.percorso = percorso
        self.avvisa = avvisa
        self.schede = {}
        self._verificati = set()
        self._coda = queue.Queue()
        self._in_coda = set()
        self._lucchetto = threading.Lock()
        self._modificato = False
        self._fermo = False
        self._filo = None
        # Le durate cambiate, (numero, percorso, vecchia, nuova), per chi tiene
        # dei totali: la finestra, per le etichette delle cartelle (1.83.1).
        self._variazioni = []
        self._generazione = 0
        # Quando e' alzato, il filo aspetta prima del file seguente: la
        # finestra lo alza mentre rinfresca la plancia, che altrimenti, con
        # il lucchetto di Python conteso, andava venti volte piu' piano (1.83.1).
        self.cedi = threading.Event()

    def _metti(self, percorso, scheda):
        """Con il lucchetto: la scheda nuova del file, o None per toglierla;
        la variazione si annota, con la durata di prima e quella nuova, anche
        se e' la stessa: la scheda puo' avere tag nuovi."""
        vecchia = (self.schede.get(percorso) or {}).get("durata")
        if scheda is None:
            self.schede.pop(percorso, None)
        else:
            self.schede[percorso] = scheda
        self._generazione += 1
        self._variazioni.append((self._generazione, percorso, vecchia, (scheda or {}).get("durata")))

    def variazioni(self):
        """Le schede cambiate dall'ultima volta, (numero, percorso, durata di
        prima, durata nuova), in ordine; chi le prende le toglie."""
        with self._lucchetto:
            variazioni, self._variazioni = self._variazioni, []
        return variazioni

    def totale_delle_durate(self, percorsi):
        """(quanti file hanno la durata, la loro somma, il numero dell'ultima
        variazione), letti insieme sotto il lucchetto: le variazioni con un
        numero piu' alto non sono comprese."""
        with self._lucchetto:
            note = [d for d in ((self.schede.get(p) or {}).get("durata") for p in percorsi) if d is not None]
            return len(note), sum(note), self._generazione

    def carica(self):
        if not os.path.isfile(self.percorso):
            return
        try:
            with open(self.percorso, encoding="utf-8") as f:
                dati = json.load(f)
        except (OSError, ValueError):
            return
        if dati.get("versione") == VERSIONE_DEL_FILE and isinstance(dati.get("schede"), dict):
            # Dalla 1.62.4 le durate che mutagen non sapeva le legge libmpv, e
            # quella dell'AAC grezzo si conta: le schede senza durata, e quelle
            # degli AAC, si rileggono.
            # Dalla 1.69.0 i tag di WAV, AIFF, WMA, WMV e TTA si leggono: le
            # loro schede di prima si rileggono.
            self.schede = {chiave: scheda for chiave, scheda in dati["schede"].items()
                if formati.ha_sottobrani(chiave) or (scheda.get("durata") is not None and formati.estensione(chiave) != ".aac"
                    and scheda.get("tag_v", 0) >= TAG_DA_RILEGGERE.get(formati.estensione(chiave), 0))}

    def salva(self):
        if not self._modificato:
            return
        with self._lucchetto:
            dati = {"versione": VERSIONE_DEL_FILE, "schede": dict(self.schede)}
            self._modificato = False
        provvisorio = self.percorso + ".tmp"
        with open(provvisorio, "w", encoding="utf-8") as f:
            json.dump(dati, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(provvisorio, self.percorso)

    def durata(self, brano):
        """La durata di un brano in secondi, dalla scheda; None se non si sa.
        Per un sottobrano di un SID e' la durata di quel sottobrano."""
        scheda = self.schede.get(brano.percorso)
        if scheda is None:
            return None
        if brano.sottobrano:
            durate = scheda.get("durate_sid")
            return durate[brano.sottobrano - 1] if durate and brano.sottobrano <= len(durate) else None
        return scheda.get("durata")

    def scheda(self, percorso):
        """La scheda del file se lo schedario ce l'ha, anche se non e' ancora
        stata ricontrollata; None se non c'e'."""
        return self.schede.get(percorso)

    def rinomina(self, vecchio, nuovo):
        """Un file rinominato sul disco: la sua scheda passa al nome nuovo."""
        with self._lucchetto:
            scheda = self.schede.get(vecchio)
            if scheda is not None:
                self._metti(vecchio, None)
                self._metti(nuovo, scheda)
                self._modificato = True

    def leggi_subito(self, percorso):
        """Legge adesso la scheda di un file, per chi ne ha bisogno subito,
        come i marker, e la tiene come le altre. None se il file non si legge."""
        try:
            scheda = leggi_scheda(percorso)
        except OSError:
            return None
        with self._lucchetto:
            self._metti(percorso, scheda)
            self._modificato = True
        return scheda

    def in_attesa(self):
        """Quanti file aspettano di essere letti o ricontrollati."""
        return len(self._in_coda)

    def chiedi(self, percorsi):
        """Mette in coda i file che in questa sessione non sono ancora stati
        ricontrollati. Torna subito; il lavoro lo fa il filo."""
        nuovi = 0
        with self._lucchetto:
            for p in percorsi:
                if p not in self._verificati and p not in self._in_coda:
                    self._in_coda.add(p)
                    self._coda.put(p)
                    nuovi += 1
        if nuovi and (self._filo is None or not self._filo.is_alive()):
            self._filo = threading.Thread(target=self._lavora, name="schedario", daemon=True)
            self._filo.start()
        return nuovi

    def _aggiornata(self, percorso):
        """Vero se la scheda che c'e' corrisponde al file com'e' adesso."""
        scheda = self.schede.get(percorso)
        if scheda is None:
            return False
        try:
            stato = os.stat(percorso)
        except OSError:
            return True
        return scheda.get("dim") == stato.st_size and scheda.get("mod") == stato.st_mtime

    def _lavora(self):
        fatti = 0
        ultimo_avviso = time.monotonic()
        while not self._fermo:
            while self.cedi.is_set() and not self._fermo:
                time.sleep(PAUSA_PER_CEDERE)
            try:
                percorso = self._coda.get(timeout=0.5)
            except queue.Empty:
                break
            if not self._aggiornata(percorso):
                try:
                    scheda = leggi_scheda(percorso)
                except OSError:
                    scheda = None
                with self._lucchetto:
                    self._metti(percorso, scheda)
                    self._modificato = True
                fatti += 1
            with self._lucchetto:
                self._verificati.add(percorso)
                self._in_coda.discard(percorso)
            if fatti and time.monotonic() - ultimo_avviso >= INTERVALLO_DEGLI_AVVISI:
                fatti = 0
                ultimo_avviso = time.monotonic()
                if self.avvisa:
                    self.avvisa()
        if self.avvisa and not self._fermo:
            self.avvisa()

    def ferma(self):
        self._fermo = True
        if self._filo is not None:
            self._filo.join(timeout=2)

    def aspetta(self, secondi=30):
        """Aspetta che la coda si svuoti; per le prove."""
        if self._filo is not None:
            self._filo.join(timeout=secondi)
