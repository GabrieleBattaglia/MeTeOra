# MeTeOra, le registrazioni: le radio e gli indirizzi in rete scritti su file.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 10/11/2026: nasce con la 3.5.0, issue 42. Nella 3.11.0 le dirette HTTP lette da diretta.py, senza riconnessioni. Nella 3.13.2 le unioni lunghe senza troncare, e le parti salvate a file se l'unione fallisce. Nella 3.15.0 bit, frequenza e canali scelti, e il WAV con RF64.

"""Le registrazioni (3.5.0, issue 42).

Si registra cio' che arriva dalla rete, le radio e gli indirizzi dei siti, e
non i file, che sono gia' sul disco (Gabriele, 10 novembre 2026). La
registrazione la fa un libmpv suo, in modo codifica, che apre lo stesso
flusso del brano che suona, con le sue intestazioni, e lo scrive nella
cartella Registrazioni accanto ai dati: il brano puo' cambiare, e la
registrazione va avanti finche' non la si ferma. Mentre scrive il file ha
in fondo .parziale, cosi' la plancia non lo mostra; fermata, prende il suo
nome, con il titolo e la data, come Rai Radio 3 2026-11-10 16.05.12.mp3.

I formati sono quelli che la libmpv di MeTeOra sa scrivere, provati il 10
novembre 2026: MP3, il predefinito, Opus, AAC, e senza perdita FLAC e WAV,
come ha chiesto Gabriele. La qualita' di partenza e' MP3 a 128 kbps, 44,1
kHz, stereo, e si adatta alla sorgente per risparmiare spazio: mono se la
sorgente e' mono, con meta' dei kbps, mai piu' kbps della sorgente, mai piu'
campioni al secondo della sorgente. Opus vuole i 48 kHz, e i formati senza
perdita tengono la frequenza della sorgente, fino a 96 kHz.
Dalla 3.15.0, per la post-produzione (Gabriele), si scelgono anche i canali,
della sorgente, mono o stereo, per tutti i formati; e per FLAC e WAV i bit,
16, 24 o, solo per il WAV, 32 in virgola mobile, e la frequenza, della
sorgente o fissa a 44.1, 48 o 96 kHz. Il WAV passa a RF64 oltre i 4 GB.
"""

import contextlib
import datetime
import os
import re
import shutil
import threading
import time

import librerie  # noqa: F401

# isort: split
import mpv

import diretta
import motore
import percorsi
import valori
from lingua import _

# Il formato -> (nome da dire, codificatore di FFmpeg, contenitore,
# estensione, con perdita).
FORMATI = {
    "mp3": ("MP3", "libmp3lame", "mp3", ".mp3", True),
    "opus": ("Opus", "libopus", "ogg", ".opus", True),
    "aac": ("AAC", "aac", "adts", ".aac", True),
    "flac": ("FLAC", "flac", "flac", ".flac", False),
    "wav": ("WAV", "pcm_s16le", "wav", ".wav", False),
}
FORMATO_PREDEFINITO = "mp3"
# I kbps che si possono scegliere, da valori, e quelli di partenza.
QUALITA = valori.QUALITA_DI_REGISTRAZIONE
QUALITA_PREDEFINITA = 128
FREQUENZA = 44100
# Senza perdita, con la frequenza della sorgente, al piu' questa (3.15.0: prima 48).
FREQUENZA_SENZA_PERDITA = 96000
# I parametri scelti nelle impostazioni (Gabriele, 3.15.0): i bit di FLAC e
# WAV, 32 in virgola mobile solo per il WAV; la frequenza senza perdita, 0
# quella della sorgente; i canali, della sorgente, mono o stereo.
BIT = valori.BIT_DI_REGISTRAZIONE
BIT_PREDEFINITI = 16
FREQUENZE = valori.FREQUENZE_DI_REGISTRAZIONE
CANALI = valori.CANALI_DI_REGISTRAZIONE
CANALI_DELLA_SORGENTE = "sorgente"
# Quanto si aspetta, al piu', che libmpv chiuda il file. L'unione che
# riscrive le parti si aspetta finche' il file cresce, perche' su otto ore
# ci mette minuti (141 volte il tempo reale, misura del 14 novembre 2026), e
# si da' per bloccata se non cresce per ATTESA_DELL_UNIONE_FERMA secondi; la
# si guarda ogni PASSO_DELL_UNIONE (3.13.2: prima si troncava dopo dieci minuti).
ATTESA_DELLA_CHIUSURA = 10.0
ATTESA_DELL_UNIONE_FERMA = 60.0
PASSO_DELL_UNIONE = 2.0
_NON_VALIDI = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')


def cartella():
    """Dove MeTeOra mette le registrazioni: la cartella Registrazioni, accanto ai dati."""
    return percorsi.percorso_dati("Registrazioni")


def estensioni():
    """Le estensioni dei file delle registrazioni."""
    return {dati[3] for dati in FORMATI.values()}


def nome_del_file(titolo, quando, estensione, dove=None):
    """Il percorso libero di una registrazione: il titolo senza i caratteri
    che Windows non vuole, la data e l'ora, e un numero se c'e' gia'."""
    pulito = " ".join(_NON_VALIDI.sub(" ", titolo or "").split())[:80].rstrip(". ") or _("Registrazione")
    base = os.path.join(dove or cartella(), f"{pulito} {quando:%Y-%m-%d %H.%M.%S}")
    percorso, n = base + estensione, 2
    while os.path.exists(percorso) or os.path.exists(percorso + ".parziale"):
        percorso, n = f"{base} {n}{estensione}", n + 1
    return percorso


def parametri(formato, kbps, sorgente_kbps=None, canali=None, frequenza=None, scelta_canali=CANALI_DELLA_SORGENTE, scelta_frequenza=0):
    """(kbps o None per i formati senza perdita, canali, frequenza) di una
    registrazione: la qualita' scelta, adattata alla sorgente, quando se ne
    sanno i kbps, i canali e la frequenza. scelta_canali, mono o stereo,
    vince sui canali della sorgente; scelta_frequenza, se non e' 0, e' la
    frequenza dei formati senza perdita (3.15.0)."""
    if scelta_canali in ("mono", "stereo"):
        canali = 1 if scelta_canali == "mono" else 2
    canali = 1 if canali == 1 else 2
    if not FORMATI[formato][4]:
        return None, canali, scelta_frequenza or min(frequenza or FREQUENZA, FREQUENZA_SENZA_PERDITA)
    if canali == 1:
        kbps = kbps // 2
    if sorgente_kbps and sorgente_kbps > 0:
        kbps = min(kbps, sorgente_kbps)
    kbps = max([q for q in QUALITA if q <= kbps] or [QUALITA[0]])
    frequenza = 48000 if formato == "opus" else min(frequenza or FREQUENZA, FREQUENZA)
    return kbps, canali, frequenza


def bit_per(formato, bit):
    """I bit di una registrazione nel formato dato: None per quelli con
    perdita; il FLAC arriva a 24, il WAV anche a 32 in virgola mobile."""
    if FORMATI[formato][4]:
        return None
    if formato == "flac":
        return 24 if bit in (24, 32) else 16
    return bit if bit in BIT else BIT_PREDEFINITI


def nome_dei_bit(bit):
    """I bit come si dicono: 24 bit, o 32 bit in virgola mobile."""
    if bit == 32:
        # Traduttori: la profondita' di una registrazione WAV a 32 bit in virgola mobile.
        return _("32 bit in virgola mobile")
    # Traduttori: la profondita' di una registrazione senza perdita, come 24 bit.
    return _("{n} bit").format(n=bit)


def _codifica(formato, kbps, bit):
    """Le opzioni di libmpv in modo codifica per il formato: il codificatore,
    il formato dei campioni, le opzioni del codificatore e del contenitore.
    Il WAV a 24 bit vuole campioni a 32, di cui tiene i 24 piu' alti, come il
    FLAC a 24 con bits_per_raw_sample; il WAV ha rf64=auto, che resta un WAV
    normale fino ai 4 GB e passa a RF64 oltre, dove la sua intestazione non
    basta piu' (prove del 14 novembre 2026)."""
    _nome, codificatore, contenitore, _estensione, _perdita = FORMATI[formato]
    opzioni = {"of": contenitore, "oac": codificatore}
    if formato == "wav":
        opzioni["oac"], opzioni["audio_format"] = {16: ("pcm_s16le", "s16"), 24: ("pcm_s24le", "s32"), 32: ("pcm_f32le", "float")}[bit or BIT_PREDEFINITI]
        opzioni["ofopts"] = "rf64=auto"
    elif formato == "flac":
        opzioni["audio_format"] = "s32" if bit == 24 else "s16"
        if bit == 24:
            opzioni["oacopts"] = "bits_per_raw_sample=24"
    elif kbps:
        opzioni["oacopts"] = f"b={kbps}k"
    return opzioni


def descrizione(formato, kbps, canali, frequenza, bit=None):
    """Il formato come si dice: MP3 a 128 kbps, stereo, 44.1 kHz, o WAV a 24
    bit, stereo, 48 kHz."""
    nome = FORMATI[formato][0]
    # Traduttori: i canali di una registrazione.
    voci = _("mono") if canali == 1 else _("stereo")
    khz = f"{frequenza / 1000:g}"
    if kbps:
        # Traduttori: il formato di una registrazione, come MP3 a 128 kbps, stereo, 44.1 kHz; i decimali col punto.
        return _("{nome} a {kbps} kbps, {canali}, {khz} kHz").format(nome=nome, kbps=kbps, canali=voci, khz=khz)
    # Traduttori: il formato di una registrazione senza perdita, come FLAC a 24 bit, stereo, 48 kHz.
    return _("{nome} a {bit}, {canali}, {khz} kHz").format(nome=nome, bit=nome_dei_bit(bit or BIT_PREDEFINITI), canali=voci, khz=khz)


class Parte:
    """Una parte di una registrazione: il suo file, i secondi del flusso da
    cui comincia, quelli registrati, e quanti se ne tolgono in testa
    all'unione."""

    def __init__(self, file, inizio=0.0):
        self.file, self.inizio = file, inizio
        self.secondi = self.taglio = 0.0
        # L'ultima posizione detta da libmpv, che a fine flusso non la dice piu'.
        self.posizione = inizio


class Registrazione:
    """Una registrazione di un flusso in rete: avvia, pausa, ferma, elimina.
    Va a parti: la pausa chiude la parte in corso e la ripresa ne apre una
    nuova, perche' in pausa libmpv continua a leggere la diretta, e alla
    ripresa registrerebbe anche il pezzo saltato; e un salto in avanti fino
    alla diretta la ferma (prove del 10 novembre 2026). Ogni connessione a una
    radio Icecast riceve subito una riserva di secondi gia' trasmessi, venti
    e piu' per Rai Radio 3: nelle parti dopo la prima e' audio della pausa o
    gia' registrato, e all'unione si toglie. Si misura cosi': dopo la riserva
    libmpv registra al passo dell'orologio, e i secondi registrati in piu'
    dell'orologio sono la riserva. Una puntata, che si salta, riprende invece
    dal punto a cui era arrivata, e finisce da se' quando finisce lei.
    Senza tagli MP3, AAC e Opus si accodano cosi' come sono, perche' MP3 e
    AAC sono fatti di pezzi che stanno da soli e piu' Ogg Opus di seguito
    sono un Ogg concatenato; con un taglio, o per FLAC e WAV, le parti si
    riscrivono in un file solo, che per FLAC e WAV non perde niente.
    al_termine(registrazione), se c'e', arriva da un filo a parte quando il
    flusso finisce da se': una puntata registrata tutta, con lo stato
    completa, o una radio che cade, con lo stato interrotta. I comandi che
    chiudono una parte aspettano libmpv: chi li chiama da una finestra li fa
    in disparte."""

    def __init__(self, sorgente, titolo, flusso, formato=FORMATO_PREDEFINITO, kbps=QUALITA_PREDEFINITA, canali=2, frequenza=FREQUENZA, al_termine=None,
            quando=None, dove=None, bit=BIT_PREDEFINITI):
        self.sorgente, self.titolo, self.flusso = sorgente, titolo, flusso
        self.formato, self.canali, self.frequenza = formato, canali, frequenza
        # I kbps valgono solo per i formati con perdita.
        self.kbps = kbps if FORMATI[formato][4] else None
        # I bit di FLAC e WAV (3.15.0), None per i formati con perdita.
        self.bit = bit_per(formato, bit)
        self.percorso = nome_del_file(titolo, quando or datetime.datetime.now(), FORMATI[formato][3], dove)
        self.stato = "pronta"
        self.dal_vivo = getattr(flusso, "dal_vivo", False)
        # I file delle parti che non si sono unite, se e' successo (3.13.2).
        self.parti_separate = []
        self._al_termine = al_termine
        self._blocco = threading.RLock()
        # Le parti chiuse, e quella in corso con il suo libmpv, l'evento della
        # sua fine e il momento in cui e' partita.
        self._parti = []
        self._parte = self._lettore = self._finita = None
        self._partita = 0.0

    @property
    def parziale(self):
        """Il file della parte in corso, o None."""
        return self._parte.file if self._parte is not None else None

    @property
    def descrizione(self):
        return descrizione(self.formato, self.kbps, self.canali, self.frequenza, self.bit)

    def _registrati(self, parte, lettore):
        """(secondi registrati, taglio) della parte in corso, letti da libmpv."""
        with contextlib.suppress(Exception):
            adesso = lettore.time_pos
            if adesso is not None:
                parte.posizione = max(parte.posizione, float(adesso))
        secondi = max(0.0, parte.posizione - parte.inizio)
        taglio = 0.0
        if self.dal_vivo and self._parti:
            taglio = min(secondi, max(0.0, secondi - (time.monotonic() - self._partita)))
        return secondi, taglio

    def _apri_la_parte(self):
        os.makedirs(os.path.dirname(self.percorso), exist_ok=True)
        # Una puntata riprende dal punto a cui era arrivata.
        inizio = 0.0 if self.dal_vivo else sum(parte.secondi for parte in self._parti)
        parte = Parte(f"{self.percorso}.parziale{len(self._parti) + 1}", inizio)
        opzioni = {**motore.OPZIONI_DI_BASE, "o": parte.file, **_codifica(self.formato, self.kbps, self.bit),
            "audio_channels": "mono" if self.canali == 1 else "stereo", "audio_samplerate": self.frequenza}
        try:
            lettore = mpv.MPV(**opzioni)
        except Exception as e:
            # libmpv che non parte e' un errore da dire.
            raise OSError(str(e)) from e
        finita = threading.Event()
        try:
            if self.flusso.intestazioni:
                lettore["http-header-fields"] = list(self.flusso.intestazioni)
            lettore.register_event_callback(lambda evento: self._evento(lettore, finita, evento))
            lettore.observe_property("time-pos", lambda _nome, valore: setattr(parte, "posizione", max(parte.posizione, float(valore)))
                if valore is not None else None)
            # Di un video con l'audio a parte si registra l'audio.
            indirizzo = self.flusso.audio[0] if self.flusso.audio else self.flusso.indirizzo
            # Una diretta HTTP la legge MeTeOra, come nel motore (issue 46, 3.11.0).
            if self.dal_vivo and not self.flusso.intestazioni and not self.flusso.audio and diretta.da_leggere(indirizzo):
                lettore.register_stream_protocol(diretta.SCHEMA, lambda uri: _lettura_della_diretta(uri))
                indirizzo = diretta.indirizzo_per_mpv(indirizzo)
            if inizio:
                lettore.command("loadfile", indirizzo, "replace", "-1", f"start={inizio:.3f}")
            else:
                lettore.command("loadfile", indirizzo)
        except Exception as e:
            lettore.terminate()
            raise OSError(str(e)) from e
        self._parte, self._lettore, self._finita, self._partita = parte, lettore, finita, time.monotonic()

    def _chiudi_la_parte(self):
        """libmpv chiude il file della parte in corso e se ne va; la parte va
        fra quelle chiuse, se ha qualcosa."""
        parte, lettore, finita = self._parte, self._lettore, self._finita
        if lettore is None:
            return
        parte.secondi, parte.taglio = self._registrati(parte, lettore)
        self._parte = self._lettore = self._finita = None
        with contextlib.suppress(Exception):
            lettore.command("stop")
        finita.wait(ATTESA_DELLA_CHIUSURA)
        with contextlib.suppress(Exception):
            lettore.terminate()
        try:
            vuota = not os.path.getsize(parte.file)
        except OSError:
            return
        if vuota:
            with contextlib.suppress(OSError):
                os.remove(parte.file)
            return
        if not parte.secondi:
            # Un file breve si scrive prima che libmpv dica una posizione.
            parte.secondi = _durata_del_file(parte.file)
        self._parti.append(parte)

    def _evento(self, lettore, finita, evento):
        """Il filo degli eventi di libmpv: non prende il lucchetto, perche' chi
        chiude una parte lo tiene mentre terminate aspetta questo filo."""
        if evento.event_id.value != mpv.MpvEventID.END_FILE:
            return
        finita.set()
        if lettore is self._lettore and self.stato == "in_corso":
            # Il flusso e' finito da se': il file si chiude in un altro filo,
            # perche' libmpv non si chiude dal filo dei suoi eventi.
            completa = evento.data.reason == mpv.MpvEventEndFile.EOF and not self.dal_vivo
            threading.Thread(target=self._finito_da_se, args=(lettore, completa), name="MeTeOra, registrazione finita da se'", daemon=True).start()

    def _finito_da_se(self, lettore, completa):
        with self._blocco:
            if lettore is not self._lettore or self.stato != "in_corso":
                return
            self.stato = "completa" if completa else "interrotta"
            self._finisci()
        if self._al_termine is not None:
            self._al_termine(self)

    def avvia(self):
        """Comincia a scrivere. OSError se la cartella non si crea, o libmpv
        non parte."""
        with self._blocco:
            self._apri_la_parte()
            self.stato = "in_corso"

    @property
    def secondi(self):
        """I secondi registrati, che non crescono in pausa, senza la riserva
        delle riprese."""
        with self._blocco:
            secondi = sum(parte.secondi - parte.taglio for parte in self._parti)
            if self._lettore is not None:
                registrati, taglio = self._registrati(self._parte, self._lettore)
                secondi += registrati - taglio
        return secondi

    @property
    def byte(self):
        with self._blocco:
            file = [parte.file for parte in self._parti] + ([self._parte.file] if self._parte else [])
            if self.stato in ("finita", "completa", "interrotta"):
                file.append(self.percorso)
        totale = 0
        for percorso in dict.fromkeys(file):
            with contextlib.suppress(OSError):
                totale += os.path.getsize(percorso)
        return totale

    def pausa(self, valore):
        """La pausa chiude la parte in corso; la ripresa ne apre una nuova.
        OSError se la ripresa non riesce."""
        with self._blocco:
            if valore and self.stato == "in_corso":
                self.stato = "in_pausa"
                self._chiudi_la_parte()
            elif not valore and self.stato == "in_pausa":
                self._apri_la_parte()
                self.stato = "in_corso"

    def _unisci(self):
        """Le parti chiuse in un file solo, quello della registrazione."""
        parti = self._parti
        if not parti:
            return
        tagli = any(parte.taglio > 0 for parte in parti)
        if len(parti) == 1 and not tagli:
            os.replace(parti[0].file, self.percorso)
        elif not tagli and self.formato in ("mp3", "aac", "opus"):
            # A pezzi, perche' una parte di ore pesa centinaia di MB (3.13.2).
            with open(self.percorso + ".unione", "wb") as uscita:
                for parte in parti:
                    with open(parte.file, "rb") as f:
                        shutil.copyfileobj(f, uscita, 1 << 20)
            os.replace(self.percorso + ".unione", self.percorso)
        else:
            _riscrivi(parti, self.percorso + ".unione", self.formato, self.kbps, self.canali, self.frequenza, self.bit)
            os.replace(self.percorso + ".unione", self.percorso)
        secondi = sum(parte.secondi - parte.taglio for parte in parti)
        for parte in parti:
            with contextlib.suppress(OSError):
                os.remove(parte.file)
        unita = Parte(self.percorso)
        unita.secondi = secondi
        self._parti = [unita]

    def _finisci(self):
        with self._blocco:
            self._chiudi_la_parte()
            try:
                self._unisci()
            except OSError:
                self._salva_le_parti()

    def _salva_le_parti(self):
        """Le parti che non si sono unite diventano file da ascoltare, uno per
        parte, come Rai Radio 3 2026-11-14 10.00.00 parte 1.mp3: niente di
        registrato si perde (3.13.2). Il percorso della registrazione e'
        quello della prima; parti_separate dice tutti i file."""
        base, estensione = os.path.splitext(self.percorso)
        salvate = []
        for numero, parte in enumerate(self._parti, 1):
            arrivo = f"{base} parte {numero}{estensione}"
            with contextlib.suppress(OSError):
                os.replace(parte.file, arrivo)
                salvate.append(arrivo)
        self._parti = []
        if salvate:
            self.parti_separate = salvate
            self.percorso = salvate[0]

    def ferma(self):
        """Ferma la registrazione e chiude il file. Torna il percorso del
        file, o None se non e' arrivato niente."""
        with self._blocco:
            if self.stato in ("in_corso", "in_pausa"):
                self.stato = "finita"
            self._finisci()
        return self.percorso if os.path.exists(self.percorso) else None

    def elimina(self):
        """Ferma la registrazione e ne cancella i file."""
        with self._blocco:
            self.stato = "eliminata"
            self._chiudi_la_parte()
            for percorso in [parte.file for parte in self._parti] + [self.percorso]:
                with contextlib.suppress(OSError):
                    os.remove(percorso)
            self._parti = []


def _lettura_della_diretta(uri):
    """La diretta letta da MeTeOra, per il protocollo del lettore della
    registrazione; ValueError, per libmpv, se non si apre."""
    try:
        # Senza riconnessioni: una ricollegata infilerebbe nel file la riserva
        # dei secondi gia' mandati, e la caduta si dice come prima.
        return diretta.Lettura(diretta.indirizzo_vero(uri), riconnetti=False)
    except Exception as e:
        # La rete fallisce in molti modi.
        raise ValueError(str(e)) from e


def _durata_del_file(percorso):
    """I secondi di un file scritto, letti da libmpv; zero se non si sa."""
    pronto = threading.Event()
    lettore = mpv.MPV(**{**motore.OPZIONI_DI_BASE, "ao": "null", "pause": True})
    try:
        lettore.register_event_callback(lambda evento: pronto.set() if evento.event_id.value in (mpv.MpvEventID.FILE_LOADED, mpv.MpvEventID.END_FILE)
            else None)
        lettore.command("loadfile", percorso)
        pronto.wait(ATTESA_DELLA_CHIUSURA)
        return float(lettore.duration or 0.0)
    except Exception:  # noqa: BLE001 - un file che non si legge non ha durata
        return 0.0
    finally:
        lettore.terminate()


def _riscrivi(parti, uscita, formato, kbps, canali, frequenza, bit=BIT_PREDEFINITI):
    """Le parti di una registrazione in un file solo, ognuna senza i secondi
    da togliere in testa, con un libmpv in modo codifica che le legge di
    seguito, come una lista EDL."""
    voci = []
    for parte in parti:
        voce = f"%{len(parte.file.encode('utf-8'))}%{parte.file}"
        if parte.taglio > 0:
            voce += f",start={parte.taglio:.3f}"
        voci.append(voce)
    finita = threading.Event()
    motivi = []
    opzioni = {**motore.OPZIONI_DI_BASE, "o": uscita, **_codifica(formato, kbps, bit_per(formato, bit)), "audio_channels": "mono" if canali == 1 else "stereo",
        "audio_samplerate": frequenza}
    lettore = mpv.MPV(**opzioni)

    def evento(e):
        if e.event_id.value == mpv.MpvEventID.END_FILE:
            motivi.append(e.data.reason)
            finita.set()

    try:
        lettore.register_event_callback(evento)
        lettore.command("loadfile", "edl://" + ";".join(voci))
        # Si aspetta finche' il file cresce: un'unione lunga non si tronca.
        peso, fermo_da = -1, time.monotonic()
        while not finita.wait(PASSO_DELL_UNIONE):
            with contextlib.suppress(OSError):
                adesso = os.path.getsize(uscita)
                if adesso != peso:
                    peso, fermo_da = adesso, time.monotonic()
            if time.monotonic() - fermo_da > ATTESA_DELL_UNIONE_FERMA:
                break
    finally:
        lettore.terminate()
    if not finita.is_set() or motivi[:1] != [mpv.MpvEventEndFile.EOF] or not os.path.exists(uscita):
        with contextlib.suppress(OSError):
            os.remove(uscita)
        raise OSError(_("le parti della registrazione non si uniscono"))
