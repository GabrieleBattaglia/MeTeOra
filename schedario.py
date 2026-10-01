# MeTeOra, lo schedario: durata, dimensione e tag dei file, ricordati fra un avvio e l'altro.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la 1.7.0, per le durate delle playlist (issue 4) e poi per il filtro (issue 2).

"""Lo schedario dei file.

Per ogni file suonabile tiene dimensione, data di modifica, durata e tag.
Leggerli costa: un MP3 va aperto con mutagen, un SID va letto per intero per
cercarne la durata nel database di HVSC. Percio' lo schedario li ricorda in
un file JSON e li rilegge solo quando il file cambia.
Il lavoro lo fa un filo a parte: chi chiede una scheda la trova subito se
c'e', altrimenti la chiede e viene avvisato quando arriva. In ogni sessione
ogni file si ricontrolla una volta, confrontando dimensione e data.
"""

import contextlib
import json
import os
import queue
import threading
import time

import formati
import songlengths

VERSIONE_DEL_FILE = 1
# Le chiavi dei tag, come le usa il filtro.
TAG = ("titolo", "autore", "album", "genere", "anno")
# Si avvisa chi aspetta al massimo una volta ogni tanti secondi, e alla fine.
INTERVALLO_DEGLI_AVVISI = 1.0


def _anno(testo):
    """Il primo anno di quattro cifre in un testo, come numero; None se non c'e'."""
    for i in range(len(testo) - 3):
        pezzo = testo[i:i + 4]
        if pezzo.isdigit() and 1900 <= int(pezzo) <= 2100:
            return int(pezzo)
    return None


def leggi_scheda(percorso):
    """La scheda di un file: dimensione, data di modifica, durata in secondi
    (None se non si sa), tag, e per i SID il numero dei sottobrani."""
    stato = os.stat(percorso)
    scheda = {"dim": stato.st_size, "mod": stato.st_mtime, "durata": None, "tag": {}, "sottobrani": None, "durate_sid": None}
    if formati.e_sid(percorso):
        info = songlengths.info_del_sid(percorso)
        if info:
            scheda["tag"] = {"titolo": info["titolo"], "autore": info["autore"], "anno": _anno(info["copyright"])}
            scheda["sottobrani"] = info["sottobrani"]
            durate = songlengths.durate_del_file(percorso)
            scheda["durate_sid"] = durate
            iniziale = info["iniziale"] or 1
            if durate and iniziale <= len(durate):
                scheda["durata"] = durate[iniziale - 1]
        return scheda
    try:
        import mutagen

        audio = mutagen.File(percorso, easy=True)
    except Exception:  # noqa: BLE001 - un file rovinato non deve fermare lo schedario
        audio = None
    if audio is not None:
        if getattr(audio, "info", None) is not None and getattr(audio.info, "length", None):
            scheda["durata"] = float(audio.info.length)
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

    def carica(self):
        if not os.path.isfile(self.percorso):
            return
        try:
            with open(self.percorso, encoding="utf-8") as f:
                dati = json.load(f)
        except (OSError, ValueError):
            return
        if dati.get("versione") == VERSIONE_DEL_FILE and isinstance(dati.get("schede"), dict):
            self.schede = dati["schede"]

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

    def leggi_subito(self, percorso):
        """Legge adesso la scheda di un file, per chi ne ha bisogno subito,
        come i marker, e la tiene come le altre. None se il file non si legge."""
        try:
            scheda = leggi_scheda(percorso)
        except OSError:
            return None
        with self._lucchetto:
            self.schede[percorso] = scheda
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
                    if scheda is None:
                        self.schede.pop(percorso, None)
                    else:
                        self.schede[percorso] = scheda
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
