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

Con l'attesa di Alt con R sempre accesa la registrazione segue la sorgente
(Gabriele, 15 novembre 2026): la finestra la mette in pausa quando la
sorgente tace e la riprende nello stesso file, e qui la pausa ha il suo
motivo, a mano, la sorgente o la rete. Una diretta che perde la connessione
lo dice ad alla_caduta, e la finestra la ricollega. Dalla sua connessione
arrivano i titoli in onda, che con le riprese diventano i marker del file
finale, contati sul suo tempo, senza le pause e senza la riserva tagliata.
L'unione non ricodifica: MP3 e AAC si accodano a fotogrammi, il WAV a
campioni, l'Opus a pacchetti in un Ogg solo; solo il FLAC si riscrive, senza
perdere niente. Un'ora si salva in pochi secondi, e secondi, byte e
avanzamento si leggono senza il lucchetto, che l'unione tiene. Accanto alle
parti il file .parti.json le descrive: le parti rimaste da un crollo si
recuperano all'avvio, con i loro tagli e i loro marker.
"""

import contextlib
import datetime
import functools
import json
import mmap
import os
import re
import struct
import threading
import time
import zlib

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
# Ogni quanto l'unione dice a che punto e', e guarda se deve fermarsi.
SGUARDO_DELL_UNIONE = 0.25
# Allo spegnimento di Windows la parte in corso si chiude in fretta, e le
# parti diventano subito file: Windows non aspetta (Gabriele, 15 novembre 2026).
ATTESA_IN_FRETTA = 2.0
# I marker automatici (Gabriele, 15 novembre 2026): il nome e' il titolo in
# onda, con gli spazi ridotti e al piu' tanti caratteri, come il nome del
# file; due marker automatici stanno ad almeno DISTANZA_DEI_MARKER secondi
# d'orologio, e un titolo che arriva prima rinomina quello di prima, che
# resta dov'e': certe radio mandano un segnaposto e poi il titolo vero, o
# alternano il loro nome e il brano.
LUNGHEZZA_DEL_MARKER = 80
DISTANZA_DEI_MARKER = 20.0
# Il primo titolo, se arriva entro tanti secondi di registrazione, va
# all'inizio del file: e' il titolo di partenza.
PRIMO_MARKER = 20.0
# I blocchi della copia dell'unione, e il file che descrive le parti.
BLOCCO_DELLA_COPIA = 1 << 20
FILE_DELLE_PARTI = ".parti.json"
VERSIONE_DELLE_PARTI = 1
_NON_VALIDI = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
_PARTE_RIMASTA = re.compile(r"^(?P<base>.+)\.parziale(?P<numero>\d+)$")


def cartella():
    """Dove MeTeOra mette le registrazioni: la cartella Registrazioni, accanto ai dati."""
    return percorsi.percorso_dati("Registrazioni")


def estensioni():
    """Le estensioni dei file delle registrazioni."""
    return {dati[3] for dati in FORMATI.values()}


def _occupato(percorso):
    """Vero se il percorso e' gia' di una registrazione: il file, la sua
    prima parte o il file delle parti, che nasce con la prima parte. Prima
    del 15 novembre 2026 si guardava .parziale, mentre le parti sono
    .parziale1 e seguenti, e due registrazioni dello stesso titolo nello
    stesso secondo avevano lo stesso file."""
    return any(os.path.exists(percorso + coda) for coda in ("", ".parziale", ".parziale1", FILE_DELLE_PARTI))


def nome_del_file(titolo, quando, estensione, dove=None):
    """Il percorso libero di una registrazione: il titolo senza i caratteri
    che Windows non vuole, la data e l'ora, e un numero se c'e' gia'."""
    pulito = " ".join(_NON_VALIDI.sub(" ", titolo or "").split())[:80].rstrip(". ") or _("Registrazione")
    base = os.path.join(dove or cartella(), f"{pulito} {quando:%Y-%m-%d %H.%M.%S}")
    percorso, n = base + estensione, 2
    while _occupato(percorso):
        percorso, n = f"{base} {n}{estensione}", n + 1
    return percorso


def nome_del_marker(testo):
    """Il nome di un marker automatico: il testo con gli spazi ridotti, al
    piu' LUNGHEZZA_DEL_MARKER caratteri; vuoto se non resta niente, e allora
    il marker si chiama come quelli di T, M e il numero."""
    nome = " ".join(str(testo or "").split())
    return nome[:LUNGHEZZA_DEL_MARKER].rstrip() if len(nome) > LUNGHEZZA_DEL_MARKER else nome


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
    all'unione. Dal 15 novembre 2026 anche i suoi marker, come liste [secondi
    dal suo inizio, nome, di ripresa, nome di base]; quando e' partita e
    finita, sull'orologio; e per una parte nata da un ricollegamento il buco
    d'orologio fra la caduta e lei, che della riserva non si toglie."""

    def __init__(self, file, inizio=0.0):
        self.file, self.inizio = file, inizio
        self.secondi = self.taglio = 0.0
        # L'ultima posizione detta da libmpv, che a fine flusso non la dice piu'.
        self.posizione = inizio
        self.marker = []
        self.partita = self.finita = 0.0
        self.buco = 0.0


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
    dell'orologio sono la riserva. Dopo un ricollegamento si toglie solo il
    doppione: i secondi della caduta, che la riserva riporta, restano
    (Gabriele, 15 novembre 2026). Una puntata, che si salta, riprende invece
    dal punto a cui era arrivata, e finisce da se' quando finisce lei.
    All'unione MP3 e AAC si accodano a fotogrammi, anche con la riserva da
    togliere, il WAV a campioni e l'Opus a pacchetti, in un Ogg solo; il
    FLAC si riscrive, senza perdere niente.
    al_termine(registrazione), se c'e', arriva da un filo a parte quando il
    flusso finisce da se': una puntata registrata tutta, con lo stato
    completa, o una radio che cade, con lo stato interrotta. Con
    alla_caduta(registrazione, secondi della parte) una diretta che cade va
    invece in pausa per la rete, e chi la riceve decide se ricollegarla.
    al_marker(registrazione, numero, nome, secondi) dice ogni titolo nuovo
    diventato marker, dal filo che legge la rete: non deve aspettare niente.
    I comandi che chiudono una parte aspettano libmpv: chi li chiama da una
    finestra li fa in disparte."""

    def __init__(self, sorgente, titolo, flusso, formato=FORMATO_PREDEFINITO, kbps=QUALITA_PREDEFINITA, canali=2, frequenza=FREQUENZA, al_termine=None,
            quando=None, dove=None, bit=BIT_PREDEFINITI, dal_vivo=None, al_marker=None, alla_caduta=None, capitoli=(), percorso=None):
        self.sorgente, self.titolo, self.flusso = sorgente, titolo, flusso
        self.formato, self.canali, self.frequenza = formato, canali, frequenza
        # I kbps valgono solo per i formati con perdita.
        self.kbps = kbps if FORMATI[formato][4] else None
        # I bit di FLAC e WAV (3.15.0), None per i formati con perdita.
        self.bit = bit_per(formato, bit)
        self.percorso = percorso or nome_del_file(titolo, quando or datetime.datetime.now(), FORMATI[formato][3], dove)
        self.stato = "pronta"
        # Una diretta la riconosce anche il motore, da un flusso di rete che
        # non si salta: chi lo sa lo dice con dal_vivo (Gabriele, 15 novembre 2026).
        self.dal_vivo = bool(getattr(flusso, "dal_vivo", False) if dal_vivo is None else dal_vivo)
        # I capitoli di una puntata, [(secondi, titolo)], dalla sua scheda:
        # il file ha il tempo della sorgente, e diventano marker all'unione.
        self.capitoli = [(float(c[0]), str(c[1] or "")) for c in capitoli or () if isinstance(c, (list, tuple)) and len(c) >= 2]
        # Il motivo della pausa: mano, sorgente o rete; None fuori dalla pausa.
        self.motivo = None
        # Durante l'unione, da 0 a 1, e se si sta salvando; quanti secondi ha
        # preso l'ultimo salvataggio.
        self.avanzamento = None
        self.in_salvataggio = False
        self.salvataggio = None
        # I file delle parti che non si sono unite, se e' successo (3.13.2).
        self.parti_separate = []
        # I marker per il file finale, (file, secondi, nome), pronti dopo
        # l'unione; quanti ne sono nati, e l'ultimo, come (numero, nome).
        self.marker_finali = []
        self.numero_dei_marker = 0
        self.ultimo_marker = None
        # Le parti trovate all'avvio, per una registrazione recuperata; i
        # secondi delle parti rimaste file separati, che non sono piu' parti.
        self.recuperate = 0
        self._secondi_separati = None
        self._al_termine, self._al_marker, self._alla_caduta = al_termine, al_marker, alla_caduta
        self._blocco = threading.RLock()
        # Il lucchetto dei marker, che il filo della rete prende e il blocco
        # no: non aspetta mai niente. Quello del file delle parti, ancora piu' sotto.
        self._blocco_dei_marker = threading.Lock()
        self._blocco_delle_parti = threading.Lock()
        self._annotazione = self.percorso + FILE_DELLE_PARTI
        self._annotazione_tolta = False
        # Le parti chiuse, quella in corso con il suo libmpv e l'evento della
        # sua fine, e quella che si sta chiudendo, che conta nei secondi.
        self._parti = []
        self._parte = self._lettore = self._finita = None
        self._chiudendo = None
        # L'ultimo titolo visto, contro i doppioni delle connessioni nuove, e
        # l'ultimo marker automatico, (orologio, voce), per la distanza minima.
        self._ultimo_titolo = None
        self._ultimo_marker = None
        # In fretta, allo spegnimento di Windows: l'unione si ferma.
        self._in_fretta = False
        # Per una registrazione recuperata senza il file delle parti, o con il
        # file finale gia' scritto: le parti diventano file, senza unirle.
        self._solo_parti = False

    @property
    def parziale(self):
        """Il file della parte in corso, o None."""
        parte = self._parte
        return parte.file if parte is not None else None

    @property
    def descrizione(self):
        return descrizione(self.formato, self.kbps, self.canali, self.frequenza, self.bit)

    @property
    def file_finali(self):
        """I file che la registrazione ha lasciato: il suo, o le parti separate."""
        if self.parti_separate:
            return list(self.parti_separate)
        return [self.percorso] if os.path.exists(self.percorso) else []

    def _registrati(self, parte, lettore):
        """(secondi registrati, taglio) della parte in corso, letti da libmpv."""
        with contextlib.suppress(Exception):
            adesso = lettore.time_pos
            if adesso is not None:
                parte.posizione = max(parte.posizione, float(adesso))
        secondi = max(0.0, parte.posizione - parte.inizio)
        return secondi, self._taglio(parte, secondi)

    def _taglio(self, parte, secondi):
        """I secondi da togliere in testa a una parte di una diretta che non
        e' la prima: la riserva, i secondi registrati in piu' dell'orologio,
        senza il buco d'orologio di un ricollegamento, che la riserva
        riporta e non e' un doppione."""
        if not self.dal_vivo or not self._parti:
            return 0.0
        riserva = secondi - (time.monotonic() - parte.partita)
        return min(secondi, max(0.0, riserva - parte.buco))

    def _apri_la_parte(self, ricollegamento=False):
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
        parte.partita = time.monotonic()
        if ricollegamento and self._parti:
            parte.buco = max(0.0, parte.partita - self._parti[-1].finita)
        # La parte e' in corso prima che libmpv apra la rete: il primo titolo
        # puo' arrivare subito.
        self._parte, self._lettore, self._finita = parte, lettore, finita
        prima = self.stato
        try:
            if self.flusso.intestazioni:
                lettore["http-header-fields"] = list(self.flusso.intestazioni)
            lettore.register_event_callback(lambda evento: self._evento(lettore, finita, evento))
            lettore.observe_property("time-pos", lambda _nome, valore: setattr(parte, "posizione", max(parte.posizione, float(valore)))
                if valore is not None else None)
            # Di un video con l'audio a parte si registra l'audio.
            indirizzo = self.flusso.audio[0] if self.flusso.audio else self.flusso.indirizzo
            # Una diretta HTTP la legge MeTeOra, come nel motore (issue 46,
            # 3.11.0), e i titoli in onda arrivano dai suoi metadati ICY; di
            # una che legge libmpv da' l'icy-title dei metadati (15 novembre 2026).
            if self.dal_vivo and not self.flusso.intestazioni and not self.flusso.audio and diretta.da_leggere(indirizzo):
                al_titolo = functools.partial(self._titolo_nella_parte, parte)
                lettore.register_stream_protocol(diretta.SCHEMA, lambda uri: _lettura_della_diretta(uri, al_titolo))
                indirizzo = diretta.indirizzo_per_mpv(indirizzo)
            elif self.dal_vivo:
                lettore.observe_property("metadata", lambda _nome, metadati: self._metadati(parte, metadati))
            self._annota()
            # In corso prima di aprire: una connessione rifiutata arriva alla
            # fine in un attimo, e una fine prima di in_corso non contava, e
            # la registrazione restava viva senza flusso (15 novembre 2026).
            self.stato = "in_corso"
            if inizio:
                lettore.command("loadfile", indirizzo, "replace", "-1", f"start={inizio:.3f}")
            else:
                lettore.command("loadfile", indirizzo)
        except Exception as e:
            self._parte = self._lettore = self._finita = None
            self.stato = prima
            lettore.terminate()
            self._annota()
            raise OSError(str(e)) from e

    def _chiudi_la_parte(self, attesa=ATTESA_DELLA_CHIUSURA):
        """libmpv chiude il file della parte in corso e se ne va; la parte va
        fra quelle chiuse, se ha qualcosa."""
        parte, lettore, finita = self._parte, self._lettore, self._finita
        if lettore is None:
            return
        parte.secondi, parte.taglio = self._registrati(parte, lettore)
        parte.finita = time.monotonic()
        # Mentre si chiude conta ancora nei secondi, letti senza il lucchetto.
        self._chiudendo = parte
        self._parte = self._lettore = self._finita = None
        with contextlib.suppress(Exception):
            lettore.command("stop")
        finita.wait(attesa)
        with contextlib.suppress(Exception):
            lettore.terminate()
        try:
            vuota = not os.path.getsize(parte.file)
        except OSError:
            self._chiudendo = None
            return
        if vuota:
            with contextlib.suppress(OSError):
                os.remove(parte.file)
            self._chiudendo = None
            self._annota()
            return
        if not parte.secondi:
            # Un file breve si scrive prima che libmpv dica una posizione.
            parte.secondi = _durata_del_file(parte.file)
        self._parti = [*self._parti, parte]
        self._chiudendo = None
        self._annota()

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
        """Il flusso e' finito da se'. Una diretta con alla_caduta va in pausa
        per la rete, con la parte chiusa, e chi la riceve decide; le altre
        finiscono, complete o interrotte, come prima."""
        caduta = None
        with self._blocco:
            if lettore is not self._lettore or self.stato != "in_corso":
                return
            if self.dal_vivo and self._alla_caduta is not None:
                parte = self._parte
                self._chiudi_la_parte()
                self.stato, self.motivo = "in_pausa", "rete"
                caduta = max(0.0, parte.finita - parte.partita)
            else:
                self.stato = "completa" if completa else "interrotta"
                self._finisci()
        if caduta is not None:
            self._alla_caduta(self, caduta)
        elif self._al_termine is not None:
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
        delle riprese. Senza il lucchetto (15 novembre 2026): la finestra e gli
        avvisi li leggono mentre una pausa chiude una parte, o un'unione di
        ore tiene il lucchetto, e prima R fermava la finestra finche' l'unione
        non finiva."""
        chiudendo, parti, parte = self._chiudendo, self._parti, self._parte
        if not parti and parte is None and chiudendo is None and self._secondi_separati is not None:
            # Le parti diventate file separati, con la loro riserva.
            return self._secondi_separati
        secondi = sum(p.secondi - p.taglio for p in parti)
        if chiudendo is not None and chiudendo not in parti:
            secondi += chiudendo.secondi - chiudendo.taglio
        if parte is not None and parte is not chiudendo:
            registrati = max(0.0, parte.posizione - parte.inizio)
            secondi += registrati - self._taglio(parte, registrati)
        return max(0.0, secondi)

    @property
    def byte(self):
        """I byte scritti, anche questi senza il lucchetto."""
        parte = self._parte
        file = [p.file for p in self._parti] + ([parte.file] if parte is not None else []) + list(self.parti_separate)
        if self.stato in ("finita", "completa", "interrotta"):
            file.append(self.percorso)
        totale = 0
        for percorso in dict.fromkeys(file):
            with contextlib.suppress(OSError):
                totale += os.path.getsize(percorso)
        return totale

    def capitoli_passati(self):
        """Quanti capitoli di una puntata la registrazione ha gia' passato."""
        if self.dal_vivo or not self.capitoli:
            return 0
        secondi = self.secondi
        return sum(1 for inizio, _titolo in self.capitoli if inizio <= secondi)

    def pausa(self, valore, motivo="mano", flusso=None):
        """La pausa chiude la parte in corso; la ripresa ne apre una nuova.
        La pausa ha un motivo, mano, sorgente o rete; una pausa che c'e' gia'
        prende quello nuovo. La ripresa di una diretta dopo la rete e' un
        ricollegamento; dopo le altre pause ha un marker, come Ripresa alle
        16.05 (Gabriele, 15 novembre 2026). flusso, se c'e', e' quello fresco
        della sorgente, da riaprire. OSError se la ripresa non riesce."""
        with self._blocco:
            if valore and self.stato == "in_corso":
                self.stato, self.motivo = "in_pausa", motivo
                self._chiudi_la_parte()
            elif valore and self.stato == "in_pausa":
                self.motivo = motivo
            elif not valore and self.stato == "in_pausa":
                prima = self.motivo
                if flusso is not None:
                    self.flusso = flusso
                self._apri_la_parte(ricollegamento=prima == "rete")
                self.stato, self.motivo = "in_corso", None
                if self.dal_vivo and prima != "rete":
                    self._marker_di_ripresa()

    def metti_il_motivo(self, motivo):
        """Il motivo nuovo di una pausa che c'e' gia', senza toccare le parti."""
        if self.stato == "in_pausa":
            self.motivo = motivo

    def _metadati(self, parte, metadati):
        """metadata della libmpv della parte, nel suo filo: l'icy-title."""
        titolo = next((str(v) for k, v in (metadati or {}).items() if str(k).lower() == "icy-title"), "")
        if titolo:
            self._titolo_nella_parte(parte, titolo)

    def _titolo_nella_parte(self, parte, titolo):
        """Un titolo in onda arrivato dalla connessione della parte, dal filo
        che legge la rete o da quello degli eventi di libmpv: un marker nuovo,
        o il nome nuovo dell'ultimo se e' piu' vicino di DISTANZA_DEI_MARKER
        secondi d'orologio. Il primo titolo, nei primi secondi, va
        all'inizio del file. Non prende il lucchetto della registrazione."""
        nome = nome_del_marker(titolo)
        if not nome:
            return
        with self._blocco_dei_marker:
            if parte is not self._parte or nome == self._ultimo_titolo:
                return
            self._ultimo_titolo = nome
            adesso = time.monotonic()
            if self._ultimo_marker is not None and adesso - self._ultimo_marker[0] < DISTANZA_DEI_MARKER:
                voce = self._ultimo_marker[1]
                if voce[2]:
                    # Su una ripresa il titolo si aggiunge: Ripresa alle 16.05: Caruso.
                    voce[1] = f"{voce[3]}: {nome}"
                else:
                    voce[1] = voce[3] = nome
            else:
                secondi = max(0.0, parte.posizione - parte.inizio)
                if not self.numero_dei_marker and not self._parti and secondi < PRIMO_MARKER:
                    secondi = 0.0
                voce = [secondi, nome, False, nome]
                parte.marker.append(voce)
                self.numero_dei_marker += 1
                self._ultimo_marker = (adesso, voce)
            self.ultimo_marker = (self.numero_dei_marker, voce[1])
            numero = self.numero_dei_marker
        self._annota()
        if self._al_marker is not None:
            self._al_marker(self, numero, voce[1], self.secondi)

    def _marker_di_ripresa(self):
        """Il marker all'inizio della parte appena aperta da una ripresa."""
        # Traduttori: il nome del marker messo dove una registrazione riprende dopo una pausa, come Ripresa alle 16.05.
        nome = _("Ripresa alle {ora}").format(ora=f"{datetime.datetime.now():%H.%M}")
        with self._blocco_dei_marker:
            parte = self._parte
            if parte is None:
                return
            voce = [0.0, nome, True, nome]
            parte.marker.append(voce)
            self.numero_dei_marker += 1
            self._ultimo_marker = (time.monotonic(), voce)
            self.ultimo_marker = (self.numero_dei_marker, nome)
        self._annota()

    def _avanza(self, frazione):
        self.avanzamento = frazione

    def _fermata(self):
        return self._in_fretta

    def _unisci(self):
        """Le parti chiuse in un file solo, quello della registrazione, con i
        marker portati sul suo tempo."""
        parti = list(self._parti)
        if not parti:
            return
        tagli = any(parte.taglio > 0 for parte in parti)
        provvisorio = self.percorso + ".unione"
        if len(parti) == 1 and not tagli:
            os.replace(parti[0].file, self.percorso)
            tratti = [(0.0, 0.0, parti[0].secondi)]
        else:
            try:
                try:
                    tratti = _accoda(parti, provvisorio, self.formato, self._avanza, self._fermata)
                except _DaRiscrivere:
                    tratti = _riscrivi(parti, provvisorio, self.formato, self.kbps, self.canali, self.frequenza, self.bit, self._avanza, self._fermata)
                os.replace(provvisorio, self.percorso)
            except BaseException:
                with contextlib.suppress(OSError):
                    os.remove(provvisorio)
                raise
        totale = sum(tratto[2] for tratto in tratti)
        self.marker_finali = self._marker_sul_file(parti, tratti, totale)
        for parte in parti:
            if parte.file != self.percorso:
                with contextlib.suppress(OSError):
                    os.remove(parte.file)
        unita = Parte(self.percorso)
        unita.secondi = totale
        self._parti = [unita]
        self._togli_l_annotazione()

    def _marker_sul_file(self, parti, tratti, totale):
        """I marker delle parti sul tempo del file finale, (file, secondi,
        nome), in ordine: ogni parte comincia dove dice il suo tratto, senza
        i secondi tolti in testa, e un marker caduto nella riserva tagliata va
        sulla giunzione. Per una puntata anche i capitoli della sorgente gia'
        registrati, che hanno il tempo del file."""
        voci = []
        for parte, (inizio, taglio, _tenuti) in zip(parti, tratti, strict=True):
            voci.extend((inizio + max(0.0, voce[0] - taglio), voce[1]) for voce in parte.marker)
        if not self.dal_vivo:
            voci.extend((inizio, nome_del_marker(titolo)) for inizio, titolo in self.capitoli if 0.0 <= inizio < totale)
        voci.sort(key=lambda voce: voce[0])
        finali = []
        for tempo, nome in voci:
            tempo = min(max(0.0, tempo), max(0.0, totale))
            if finali and abs(finali[-1][1] - tempo) < 0.01:
                # Due marker nello stesso punto sono uno, con il nome del secondo.
                finali[-1] = (self.percorso, finali[-1][1], nome or finali[-1][2])
                continue
            finali.append((self.percorso, tempo, nome))
        return finali

    def _finisci(self):
        """Chiude la parte in corso e unisce le parti; se l'unione non
        riesce, o si ferma per la fretta, le parti diventano file."""
        with self._blocco:
            self._chiudi_la_parte()
            if not self._parti or (len(self._parti) == 1 and self._parti[0].file == self.percorso):
                return
            self.in_salvataggio, self.avanzamento = True, 0.0
            inizio = time.monotonic()
            try:
                if self._solo_parti:
                    self._salva_le_parti()
                else:
                    self._unisci()
            except OSError:
                self._salva_le_parti()
            finally:
                self.salvataggio = time.monotonic() - inizio
                self.in_salvataggio, self.avanzamento = False, None

    def _salva_le_parti(self):
        """Le parti che non si sono unite diventano file da ascoltare, uno per
        parte, come Rai Radio 3 2026-11-14 10.00.00 parte 1.mp3: niente di
        registrato si perde (3.13.2). Il percorso della registrazione e'
        quello della prima; parti_separate dice tutti i file. I marker restano
        sulla loro parte, con la riserva, che qui non si taglia."""
        base, estensione = os.path.splitext(self.percorso)
        salvate, voci, tutte = [], [], True
        self._secondi_separati = sum(parte.secondi for parte in self._parti)
        for numero, parte in enumerate(self._parti, 1):
            arrivo = _libero(f"{base} parte {numero}", estensione)
            try:
                os.replace(parte.file, arrivo)
            except OSError:
                tutte = False
                continue
            salvate.append(arrivo)
            voci.extend((arrivo, voce[0], voce[1]) for voce in parte.marker)
            if not self.dal_vivo:
                voci.extend((arrivo, inizio - parte.inizio, nome_del_marker(titolo)) for inizio, titolo in self.capitoli
                    if parte.inizio <= inizio < parte.inizio + max(parte.secondi, 0.0))
        self._parti = []
        self.marker_finali = voci
        if salvate:
            self.parti_separate = salvate
            self.percorso = salvate[0]
        if tutte:
            # Una parte che non si e' spostata resta al recupero dell'avvio.
            self._togli_l_annotazione()

    def ferma(self):
        """Ferma la registrazione e chiude il file. Torna il percorso del
        file, o None se non e' arrivato niente."""
        with self._blocco:
            if self.stato in ("in_corso", "in_pausa"):
                self.stato, self.motivo = "finita", None
            self._finisci()
        return self.percorso if os.path.exists(self.percorso) else None

    def salva_in_fretta(self, attesa=ATTESA_IN_FRETTA):
        """Allo spegnimento di Windows, che non aspetta (Gabriele, 15 novembre
        2026): la parte in corso si chiude in fretta e le parti diventano
        subito file, come quando l'unione non riesce; un'unione in corso in un
        altro filo si ferma e fa lo stesso. Torna i file. Una parte che
        intanto non si chiude resta, con il file delle parti, al recupero
        dell'avvio: non si perde niente."""
        self._in_fretta = True
        if not self._blocco.acquire(timeout=attesa + 1.0):
            return self.file_finali
        try:
            if self.stato == "eliminata":
                return []
            self._chiudi_la_parte(attesa)
            if self.stato in ("in_corso", "in_pausa"):
                self.stato, self.motivo = "finita", None
            if self._parti and not (len(self._parti) == 1 and self._parti[0].file == self.percorso):
                self._salva_le_parti()
            return self.file_finali
        finally:
            self._blocco.release()

    def elimina(self):
        """Ferma la registrazione e ne cancella i file."""
        with self._blocco:
            self.stato = "eliminata"
            self._chiudi_la_parte()
            for percorso in [parte.file for parte in self._parti] + [self.percorso, self.percorso + ".unione"]:
                with contextlib.suppress(OSError):
                    os.remove(percorso)
            self._parti = []
            self.marker_finali = []
            self._togli_l_annotazione()

    # Il file delle parti, per il recupero dopo un crollo (15 novembre 2026).

    def _annota(self):
        """Il file delle parti accanto alla registrazione, riscritto a ogni
        parte aperta o chiusa e a ogni marker: i parametri, e di ogni parte il
        file, l'inizio, i secondi, il taglio e i marker. Senza di lui le parti
        di un crollo si recuperano solo come file separati."""
        parte = self._parte
        dati = {"versione": VERSIONE_DELLE_PARTI, "sorgente": self.sorgente, "titolo": self.titolo, "formato": self.formato, "kbps": self.kbps,
            "canali": self.canali, "frequenza": self.frequenza, "bit": self.bit, "dal_vivo": self.dal_vivo, "capitoli": [list(c) for c in self.capitoli],
            "parti": [_descrizione_della_parte(p) for p in self._parti], "in_corso": _descrizione_della_parte(parte) if parte is not None else None}
        with self._blocco_delle_parti:
            if self._annotazione_tolta or self.stato == "eliminata":
                return
            provvisorio = self._annotazione + ".tmp"
            with contextlib.suppress(OSError):
                with open(provvisorio, "w", encoding="utf-8") as f:
                    json.dump(dati, f, ensure_ascii=False)
                os.replace(provvisorio, self._annotazione)

    def _togli_l_annotazione(self):
        with self._blocco_delle_parti:
            self._annotazione_tolta = True
            for percorso in (self._annotazione, self._annotazione + ".tmp"):
                with contextlib.suppress(OSError):
                    os.remove(percorso)

    @classmethod
    def da_recuperare(cls, percorso):
        """La registrazione rimasta a meta' con il file percorso, dalle parti
        .parzialeN che ha accanto, ferma e pronta per ferma, che la unisce:
        con il file delle parti tornano i parametri, i tagli e i marker; senza,
        o con il file finale gia' scritto, le parti diventano file separati.
        None se non ha parti, o il formato non si riconosce."""
        cartella_della_registrazione = os.path.dirname(percorso)
        file = sorted((int(trovato["numero"]), os.path.join(cartella_della_registrazione, nome)) for nome in _elenco(cartella_della_registrazione)
            if (trovato := _PARTE_RIMASTA.match(nome)) and os.path.join(cartella_della_registrazione, trovato["base"]) == percorso)
        if not file:
            return None
        dati = {}
        with contextlib.suppress(OSError, ValueError), open(percorso + FILE_DELLE_PARTI, encoding="utf-8") as f:
            dati = json.load(f)
        if not isinstance(dati, dict):
            dati = {}
        formato = dati.get("formato") if dati.get("formato") in FORMATI else next((k for k, v in FORMATI.items() if percorso.lower().endswith(v[3])), None)
        if formato is None:
            return None
        titolo = str(dati.get("titolo") or os.path.splitext(os.path.basename(percorso))[0])
        reg = cls(str(dati.get("sorgente") or percorso), titolo, None, formato, dati.get("kbps") or QUALITA_PREDEFINITA, dati.get("canali") or 2,
            dati.get("frequenza") or FREQUENZA, dove=cartella_della_registrazione, bit=dati.get("bit") or BIT_PREDEFINITI, dal_vivo=bool(dati.get("dal_vivo")),
            capitoli=dati.get("capitoli") or (), percorso=percorso)
        descritte = {str(voce.get("file")): voce for voce in [*(dati.get("parti") or []), dati.get("in_corso") or {}] if isinstance(voce, dict)}
        parti = []
        for _numero, nome in file:
            voce = descritte.get(os.path.basename(nome)) or {}
            parte = Parte(nome, float(voce.get("inizio") or 0.0))
            parte.secondi = float(voce.get("secondi") or 0.0) or _durata_del_file(nome)
            parte.taglio = min(parte.secondi, float(voce.get("taglio") or 0.0))
            parte.marker = [[float(m[0]), str(m[1]), False, str(m[1])] for m in voce.get("marker") or [] if isinstance(m, list) and len(m) >= 2]
            parti.append(parte)
        reg._parti = parti
        reg.stato = "finita"
        reg.recuperate = len(parti)
        reg._solo_parti = not dati or os.path.exists(percorso)
        return reg


def _descrizione_della_parte(parte):
    return {"file": os.path.basename(parte.file), "inizio": parte.inizio, "secondi": parte.secondi, "taglio": parte.taglio,
        "marker": [[voce[0], voce[1]] for voce in list(parte.marker)]}


def _elenco(cartella_da_guardare):
    try:
        return os.listdir(cartella_da_guardare)
    except OSError:
        return []


def _libero(base, estensione):
    """Il primo percorso libero: base con l'estensione, o con un numero."""
    percorso, n = base + estensione, 2
    while os.path.exists(percorso):
        percorso, n = f"{base} {n}{estensione}", n + 1
    return percorso


def rimaste(cartella_da_guardare):
    """Le registrazioni rimaste a meta' nella cartella, dopo un crollo o uno
    spegnimento a forza: i percorsi finali di quelle che hanno parti
    .parzialeN, da recuperare con Registrazione.da_recuperare. I file
    .unione rimasti a meta' si tolgono, e cosi' il file delle parti di una
    registrazione senza piu' parti. Da chiamare solo all'avvio, quando
    nessuna registrazione scrive."""
    nomi = _elenco(cartella_da_guardare)
    basi = {os.path.join(cartella_da_guardare, trovato["base"]) for nome in nomi if (trovato := _PARTE_RIMASTA.match(nome))}
    for nome in nomi:
        percorso = os.path.join(cartella_da_guardare, nome)
        if nome.endswith(".unione") or (nome.endswith(FILE_DELLE_PARTI) and percorso[:-len(FILE_DELLE_PARTI)] not in basi):
            with contextlib.suppress(OSError):
                os.remove(percorso)
    return sorted(basi)


def _lettura_della_diretta(uri, al_titolo=None):
    """La diretta letta da MeTeOra, per il protocollo del lettore della
    registrazione, con i titoli in onda ad al_titolo; ValueError, per libmpv,
    se non si apre."""
    try:
        # Senza riconnessioni: una ricollegata infilerebbe nel file la riserva
        # dei secondi gia' mandati. Dal 15 novembre 2026 la ricollega la
        # finestra, con una parte nuova, e la riserva doppia si toglie.
        return diretta.Lettura(diretta.indirizzo_vero(uri), al_titolo=al_titolo, riconnetti=False)
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


def _durata_vera(parte, formato):
    """La durata di una parte da riscrivere, dal suo file: mutagen la sa
    giusta per FLAC e Opus; per gli altri valgono i secondi registrati."""
    with contextlib.suppress(Exception):
        if formato == "flac":
            import mutagen.flac

            return float(mutagen.flac.FLAC(parte.file).info.length)
        if formato == "opus":
            import mutagen.oggopus

            return float(mutagen.oggopus.OggOpus(parte.file).info.length)
    return parte.secondi


def _riscrivi(parti, uscita, formato, kbps, canali, frequenza, bit=BIT_PREDEFINITI, avanza=None, fermata=None):
    """Le parti di una registrazione in un file solo, ognuna senza i secondi
    da togliere in testa, con un libmpv in modo codifica che le legge di
    seguito, come una lista EDL. Torna i tratti, come _accoda; avanza riceve
    a che punto e', e con fermata vera ci si ferma, con OSError."""
    durate = [_durata_vera(parte, formato) for parte in parti]
    voci = []
    for parte in parti:
        voce = f"%{len(parte.file.encode('utf-8'))}%{parte.file}"
        if parte.taglio > 0:
            voce += f",start={parte.taglio:.3f}"
        voci.append(voce)
    tratti, inizio = [], 0.0
    for durata, parte in zip(durate, parti, strict=True):
        tenuti = max(0.0, durata - parte.taglio)
        tratti.append((inizio, parte.taglio, tenuti))
        inizio += tenuti
    totale = max(inizio, 0.001)
    finita = threading.Event()
    motivi = []
    opzioni = {**motore.OPZIONI_DI_BASE, "o": uscita, **_codifica(formato, kbps, bit_per(formato, bit)), "audio_channels": "mono" if canali == 1 else "stereo",
        "audio_samplerate": frequenza}
    lettore = mpv.MPV(**opzioni)

    def evento(e):
        if e.event_id.value == mpv.MpvEventID.END_FILE:
            motivi.append(e.data.reason)
            finita.set()

    fermato = False
    try:
        lettore.register_event_callback(evento)
        if avanza is not None:
            lettore.observe_property("time-pos", lambda _nome, valore: avanza(min(1.0, max(0.0, float(valore) / totale))) if valore is not None else None)
        lettore.command("loadfile", "edl://" + ";".join(voci))
        # Si aspetta finche' il file cresce: un'unione lunga non si tronca.
        peso, fermo_da, guardato = -1, time.monotonic(), 0.0
        while not finita.wait(SGUARDO_DELL_UNIONE):
            if fermata is not None and fermata():
                fermato = True
                break
            if time.monotonic() - guardato < PASSO_DELL_UNIONE:
                continue
            guardato = time.monotonic()
            with contextlib.suppress(OSError):
                adesso = os.path.getsize(uscita)
                if adesso != peso:
                    peso, fermo_da = adesso, time.monotonic()
            if time.monotonic() - fermo_da > ATTESA_DELL_UNIONE_FERMA:
                break
    finally:
        lettore.terminate()
    if fermato or not finita.is_set() or motivi[:1] != [mpv.MpvEventEndFile.EOF] or not os.path.exists(uscita):
        with contextlib.suppress(OSError):
            os.remove(uscita)
        raise OSError(_("le parti della registrazione non si uniscono"))
    return tratti


# L'unione senza ricodificare (Gabriele, 15 novembre 2026).


class _DaRiscrivere(Exception):
    """Le parti non si accodano senza ricodificare: si riscrivono con libmpv."""


class _Scrittore:
    """Il file dell'unione, scritto a blocchi: dice a che punto e', sul peso
    delle parti, e si ferma con OSError se l'unione va interrotta."""

    def __init__(self, f, totale, avanza, fermata):
        self._f, self._totale, self._avanza, self._fermata = f, max(1, totale), avanza, fermata
        self._scritti = 0

    def scrivi(self, dati, inizio=0, fine=None):
        fine = len(dati) if fine is None else fine
        while inizio < fine:
            if self._fermata():
                raise OSError(_("il salvataggio della registrazione si è fermato"))
            pezzo = min(fine, inizio + BLOCCO_DELLA_COPIA)
            self._f.write(dati[inizio:pezzo])
            self._scritti += pezzo - inizio
            inizio = pezzo
            self._avanza(min(1.0, self._scritti / self._totale))


@contextlib.contextmanager
def _mappa(percorso):
    """Il file in memoria, in sola lettura, senza leggerlo tutto: le parti
    di ore pesano centinaia di MB."""
    with open(percorso, "rb") as f:
        if not os.fstat(f.fileno()).st_size:
            yield b""
            return
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as dati:
            yield dati


def _accoda(parti, uscita, formato, avanza, fermata):
    """Le parti in un file solo senza ricodificare: MP3 e AAC a fotogrammi,
    anche con la riserva da togliere, il WAV a campioni, l'Opus a pacchetti
    in un Ogg solo, cosi' un salvataggio di ore dura secondi. Torna i tratti
    delle parti: (secondi del file finale in cui comincia la parte, secondi
    tolti in testa, secondi tenuti). _DaRiscrivere per il FLAC, o se una parte
    non e' come la scrive libmpv."""
    accoda = {"mp3": _accoda_mp3, "aac": _accoda_aac, "wav": _accoda_wav, "opus": _accoda_opus}.get(formato)
    if accoda is None:
        raise _DaRiscrivere(formato)
    totale = sum(os.path.getsize(parte.file) for parte in parti)
    try:
        with open(uscita, "wb") as f, contextlib.ExitStack() as pila:
            mappe = [pila.enter_context(_mappa(parte.file)) for parte in parti]
            return accoda(parti, mappe, _Scrittore(f, totale, avanza, fermata))
    except (ValueError, IndexError, KeyError, struct.error) as e:
        with contextlib.suppress(OSError):
            os.remove(uscita)
        raise _DaRiscrivere(str(e)) from e


# I fotogrammi di MP3 e AAC, con le intestazioni di diretta._testa.
_FREQUENZE_ADTS = (96000, 88200, 64000, 48000, 44100, 32000, 24000, 22050, 16000, 12000, 11025, 8000, 7350)


def _lunghezza_id3(dati):
    """I byte del tag ID3v2 in testa, che il contenitore MP3 di libmpv scrive; 0 se non c'e'."""
    if len(dati) < 10 or dati[:3] != b"ID3":
        return 0
    lunghezza = 10 + ((dati[6] & 0x7F) << 21 | (dati[7] & 0x7F) << 14 | (dati[8] & 0x7F) << 7 | (dati[9] & 0x7F))
    return lunghezza + (10 if dati[5] & 0x10 else 0)


def _xing(dati, i):
    """Dove sta Xing o Info nel fotogramma MP3 che comincia a i, l'intestazione
    che libmpv scrive in testa, con i conti di tutta la parte; None se il
    fotogramma e' audio."""
    versione, mono = (dati[i + 1] >> 3) & 3, (dati[i + 3] >> 6) == 3
    lato = (17 if mono else 32) if versione == 3 else (9 if mono else 17)
    j = i + 4 + lato
    return j if bytes(dati[j:j + 4]) in (b"Xing", b"Info") else None


def _scorri(dati, i, taglio=0.0, uno_in_piu=False):
    """I fotogrammi MP3 o AAC ADTS di dati da i, fino al primo che non lo e'
    o non e' intero. Con il taglio si saltano quelli dei primi taglio
    secondi e, con uno_in_piu, uno ancora: nell'MP3 il primo dopo il taglio
    prende bit dai fotogrammi saltati, il serbatoio di bit, e suonerebbe
    rotto. Torna (primo byte tenuto, fine, fotogrammi tenuti, campioni
    tolti, campioni tenuti, frequenza)."""
    n = len(dati)
    misure = {}
    primo, fotogrammi, tolti, tenuti, frequenza, da_togliere = None, 0, 0, 0, None, 0
    while i + 7 <= n and dati[i] == 0xFF:
        if dati[i + 1] & 0xF6 == 0xF0:
            # AAC ADTS: la lunghezza e i blocchi sono in ogni intestazione.
            lunghezza = ((dati[i + 3] & 3) << 11) | (dati[i + 4] << 3) | (dati[i + 5] >> 5)
            indice = (dati[i + 2] >> 2) & 0x0F
            if lunghezza < 7 or indice >= len(_FREQUENZE_ADTS):
                break
            campioni, hz = 1024 * ((dati[i + 6] & 3) + 1), _FREQUENZE_ADTS[indice]
        else:
            chiave = (dati[i + 1] << 8) | dati[i + 2]
            misura = misure.get(chiave)
            if misura is None:
                testa = diretta._testa(dati, i)
                if testa is None or testa is diretta._POCO or testa[1][0] != "mp3":
                    break
                _genere, versione, strato, indice = testa[1]
                misura = misure[chiave] = (testa[0], 384 if strato == 3 else (576 if strato == 1 and versione != 3 else 1152),
                    diretta._FREQUENZE_MP3[versione][indice])
            lunghezza, campioni, hz = misura
        if i + lunghezza > n:
            break
        if frequenza is None:
            frequenza = hz
            da_togliere = round(taglio * hz) if taglio > 0 else 0
        if primo is None:
            if tolti < da_togliere:
                tolti += campioni
                i += lunghezza
                continue
            if uno_in_piu and tolti:
                uno_in_piu = False
                tolti += campioni
                i += lunghezza
                continue
            primo = i
        fotogrammi += 1
        tenuti += campioni
        i += lunghezza
    return (i if primo is None else primo), i, fotogrammi, tolti, tenuti, frequenza or FREQUENZA


def _crc16(dati):
    """La CRC-16 del tag LAME, quella di FFmpeg: polinomio 0x8005 rovesciato, da zero."""
    crc = 0
    for b in dati:
        crc ^= b
        for _bit in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def _xing_aggiornato(fotogramma, j, fotogrammi, byte, riempimento):
    """Il fotogramma Info o Xing della prima parte con i conti del file
    intero: i fotogrammi, i byte, l'indice lineare di un file a bitrate
    costante, e nel tag LAME il riempimento in coda dell'ultima parte, la
    lunghezza e la CRC. Senza, mutagen e lo schedario leggevano la durata
    della sola prima parte (misura del 15 novembre 2026)."""
    f = bytearray(fotogramma)
    bandiere = struct.unpack(">I", f[j + 4:j + 8])[0]
    k = j + 8
    if bandiere & 1:
        f[k:k + 4] = struct.pack(">I", fotogrammi)
        k += 4
    if bandiere & 2:
        f[k:k + 4] = struct.pack(">I", byte)
        k += 4
    if bandiere & 4:
        f[k:k + 100] = bytes(256 * n // 100 for n in range(100))
        k += 100
    if bandiere & 8:
        k += 4
    if bytes(f[k:k + 4]) in (b"LAME", b"Lavf", b"Lavc") and len(f) >= k + 36:
        if riempimento is not None:
            ritardo = int.from_bytes(f[k + 21:k + 24], "big") >> 12
            f[k + 21:k + 24] = ((ritardo << 12) | (riempimento & 0xFFF)).to_bytes(3, "big")
        f[k + 28:k + 32] = struct.pack(">I", byte)
        f[k + 34:k + 36] = b"\0\0"
        f[k + 34:k + 36] = struct.pack(">H", _crc16(bytes(f[:190])))
    return bytes(f)


def _riempimento_xing(dati, j):
    """Il riempimento in coda scritto nel tag LAME del fotogramma Info, o None."""
    bandiere = struct.unpack(">I", bytes(dati[j + 4:j + 8]))[0]
    k = j + 8 + (4 if bandiere & 1 else 0) + (4 if bandiere & 2 else 0) + (100 if bandiere & 4 else 0) + (4 if bandiere & 8 else 0)
    if bytes(dati[k:k + 4]) in (b"LAME", b"Lavf", b"Lavc"):
        return int.from_bytes(dati[k + 21:k + 24], "big") & 0xFFF
    return None


def _accoda_mp3(parti, mappe, scrittore):
    """Gli MP3: il tag ID3 e il fotogramma Info della prima parte, rifatto con
    i conti di tutto il file, poi i fotogrammi audio di ogni parte, senza i
    suoi Info e senza la riserva."""
    misure, testa, info, riempimento = [], b"", None, None
    for numero, (parte, dati) in enumerate(zip(parti, mappe, strict=True)):
        i = _lunghezza_id3(dati)
        if i + 7 > len(dati) or dati[i] != 0xFF:
            raise ValueError("una parte non comincia con un fotogramma MP3")
        primo = diretta._testa(dati, i)
        if primo is None or primo is diretta._POCO or primo[1][0] != "mp3":
            raise ValueError("una parte non comincia con un fotogramma MP3")
        j = _xing(dati, i)
        if j is not None:
            if numero == 0:
                testa, info = bytes(dati[:i]), (bytes(dati[i:i + primo[0]]), j - i)
            riempimento = _riempimento_xing(dati, j)
            i += primo[0]
        elif numero == 0:
            testa = bytes(dati[:i])
        misure.append(_scorri(dati, i, parte.taglio, uno_in_piu=True))
    fotogrammi = sum(misura[2] for misura in misure)
    audio = sum(misura[1] - misura[0] for misura in misure)
    scrittore.scrivi(testa)
    if info is not None:
        scrittore.scrivi(_xing_aggiornato(info[0], info[1], fotogrammi, len(info[0]) + audio, riempimento))
    return _scrivi_i_fotogrammi(mappe, misure, scrittore)


def _scrivi_i_fotogrammi(mappe, misure, scrittore):
    tratti, inizio = [], 0.0
    for dati, (primo, fine, _fotogrammi, tolti, tenuti, hz) in zip(mappe, misure, strict=True):
        scrittore.scrivi(dati, primo, fine)
        tratti.append((inizio, tolti / hz, tenuti / hz))
        inizio += tenuti / hz
    return tratti


def _accoda_aac(parti, mappe, scrittore):
    """Gli AAC ADTS: ogni fotogramma sta da se', e si accodano quelli dopo la riserva."""
    misure = []
    for parte, dati in zip(parti, mappe, strict=True):
        i = _lunghezza_id3(dati)
        if i + 7 > len(dati) or dati[i] != 0xFF or dati[i + 1] & 0xF6 != 0xF0:
            raise ValueError("una parte non comincia con un fotogramma ADTS")
        misure.append(_scorri(dati, i, parte.taglio))
    return _scrivi_i_fotogrammi(mappe, misure, scrittore)


def _wav(dati):
    """(il blocco fmt, inizio dei campioni, loro byte, frequenza, byte per campione) di un WAV o di un RF64."""
    if bytes(dati[:4]) not in (b"RIFF", b"RF64") or bytes(dati[8:12]) != b"WAVE":
        raise ValueError("una parte non e' un WAV")
    i, fmt, ds64 = 12, None, None
    while i + 8 <= len(dati):
        nome, lunghezza = bytes(dati[i:i + 4]), struct.unpack("<I", dati[i + 4:i + 8])[0]
        if nome == b"ds64":
            ds64 = struct.unpack("<Q", dati[i + 16:i + 24])[0]
        elif nome == b"fmt ":
            fmt = bytes(dati[i + 8:i + 8 + lunghezza])
        elif nome == b"data":
            if fmt is None or len(fmt) < 16:
                raise ValueError("un WAV senza il blocco fmt")
            inizio = i + 8
            if lunghezza == 0xFFFFFFFF and ds64 is not None:
                lunghezza = ds64
            # Un WAV non chiuso, da un crollo, ha la lunghezza a zero o sbagliata.
            if not lunghezza or inizio + lunghezza > len(dati):
                lunghezza = len(dati) - inizio
            blocco = struct.unpack("<H", fmt[12:14])[0] or 1
            return fmt, inizio, lunghezza - lunghezza % blocco, struct.unpack("<I", fmt[4:8])[0], blocco
        i += 8 + lunghezza + (lunghezza & 1)
    raise ValueError("un WAV senza campioni")


def _accoda_wav(parti, mappe, scrittore):
    """I WAV: l'intestazione nuova, RIFF o RF64 oltre i 4 GB, e i campioni di
    ogni parte, senza la riserva, tagliata al campione, e senza il silenzio
    che libmpv aggiunge in coda a ogni parte, fino a un terzo di secondo:
    con una parte per ogni pausa le giunzioni si allungherebbero."""
    misure, fmt = [], None
    for parte, dati in zip(parti, mappe, strict=True):
        formato_della_parte, inizio, lunghezza, frequenza, blocco = _wav(dati)
        if fmt is None:
            fmt = formato_della_parte
        elif formato_della_parte != fmt:
            raise ValueError("parti WAV con formati diversi")
        tolti = min(lunghezza, round(parte.taglio * frequenza) * blocco) if parte.taglio > 0 else 0
        fine = inizio + lunghezza
        if parte.secondi > 0:
            # Si toglie solo lo zero oltre i secondi registrati: e' il
            # riempimento, mai l'audio; e si guardano al piu' gli ultimi due secondi.
            minimo = max(inizio + tolti, min(fine, inizio + round(parte.secondi * frequenza) * blocco), fine - 2 * frequenza * blocco)
            coda = bytes(dati[minimo:fine]).rstrip(b"\0")
            fine = min(inizio + lunghezza, minimo + -(-len(coda) // blocco) * blocco)
        misure.append((inizio + tolti, fine, tolti // blocco, (fine - inizio - tolti) // blocco, frequenza))
    campioni = sum(fine - primo for primo, fine, _tolti, _tenuti, _hz in misure)
    if 20 + len(fmt) + campioni + 1 > 0xFFFFFFFF:
        blocco = struct.unpack("<H", fmt[12:14])[0] or 1
        ds64 = b"ds64" + struct.pack("<IQQQI", 28, 56 + len(fmt) + campioni + (campioni & 1), campioni, campioni // blocco, 0)
        testa = b"RF64" + struct.pack("<I", 0xFFFFFFFF) + b"WAVE" + ds64 + b"fmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", 0xFFFFFFFF)
    else:
        testa = b"RIFF" + struct.pack("<I", 4 + 8 + len(fmt) + 8 + campioni + (campioni & 1)) + b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt
        testa += b"data" + struct.pack("<I", campioni)
    scrittore.scrivi(testa)
    tratti, inizio = [], 0.0
    for dati, (primo, fine, tolti, tenuti, frequenza) in zip(mappe, misure, strict=True):
        scrittore.scrivi(dati, primo, fine)
        tratti.append((inizio, tolti / frequenza, tenuti / frequenza))
        inizio += tenuti / frequenza
    if campioni & 1:
        scrittore.scrivi(b"\0")
    return tratti


# L'Ogg Opus: le pagine, la CRC e i campioni dei pacchetti.
_ROVESCIATI = bytes(int(f"{n:08b}"[::-1], 2) for n in range(256))
OPUS_HZ = 48000
# Una pagina d'uscita tiene al piu' un secondo, come quelle di libmpv.
_PAGINA_OGG = OPUS_HZ


def _crc_ogg(dati):
    """La CRC delle pagine Ogg, polinomio 0x04C11DB7 senza rovesciamenti,
    fatta con quella di zlib sui byte rovesciati: in C, anche per centinaia
    di MB (verificata sulle pagine di libmpv il 15 novembre 2026)."""
    grezza = zlib.crc32(dati.translate(_ROVESCIATI), 0xFFFFFFFF) ^ 0xFFFFFFFF
    return int(f"{grezza:032b}"[::-1], 2)


def _pacchetti_ogg(dati):
    """I pacchetti di un Ogg, in ordine, anche a cavallo delle pagine, con il
    granulo dell'ultima pagina, e il seriale: (pacchetti, granulo, seriale);
    i pacchetti sono un generatore, da consumare prima di chiedere il resto."""
    stato = {"granulo": 0, "seriale": None}

    def genera():
        i, n, resto = 0, len(dati), b""
        while i + 27 <= n:
            if bytes(dati[i:i + 4]) != b"OggS":
                raise ValueError("una pagina Ogg rotta")
            granulo, seriale = struct.unpack("<qI", dati[i + 6:i + 18])
            quanti = dati[i + 26]
            segmenti = dati[i + 27:i + 27 + quanti]
            j = i + 27 + quanti
            if j + sum(segmenti) > n:
                # L'ultima pagina di una parte non chiusa, da un crollo.
                break
            if stato["seriale"] is None:
                stato["seriale"] = seriale
            elif seriale != stato["seriale"]:
                raise ValueError("un Ogg con piu' flussi")
            inizio = j
            for lunghezza in segmenti:
                j += lunghezza
                if lunghezza < 255:
                    yield resto + bytes(dati[inizio:j])
                    resto, inizio = b"", j
            resto += bytes(dati[inizio:j])
            if granulo >= 0:
                stato["granulo"] = granulo
            i = j

    return genera(), stato


def _campioni_opus(pacchetto):
    """I campioni a 48 kHz di un pacchetto Opus, dal suo primo byte."""
    toc = pacchetto[0]
    configurazione = toc >> 3
    if configurazione < 12:
        durata = (480, 960, 1920, 2880)[configurazione % 4]
    elif configurazione < 16:
        durata = (480, 960)[configurazione % 2]
    else:
        durata = (120, 240, 480, 960)[configurazione % 4]
    codice = toc & 3
    if codice == 0:
        return durata
    if codice in (1, 2):
        return 2 * durata
    return durata * (pacchetto[1] & 0x3F) if len(pacchetto) > 1 else durata


class _PagineOgg:
    """Le pagine dell'Ogg d'uscita, di un flusso solo: la testata a parte, poi
    i pacchetti audio, un secondo o 255 segmenti per pagina, con il
    granulo, il numero e la CRC. L'ultima pagina aspetta la fine, che le da'
    il segno e il granulo con il taglio in coda."""

    def __init__(self, scrittore, seriale):
        self._scrittore, self._seriale = scrittore, seriale
        self._numero = 0
        self._pacchetti, self._segmenti, self._campioni = [], 0, 0
        self.granulo = 0

    def pagina(self, tipo, granulo, pacchetti):
        segmenti = []
        for pacchetto in pacchetti:
            segmenti += [255] * (len(pacchetto) // 255) + [len(pacchetto) % 255]
        dati = bytearray(b"OggS" + bytes([0, tipo]) + struct.pack("<qII", granulo, self._seriale, self._numero) + b"\0\0\0\0" + bytes([len(segmenti)])
            + bytes(segmenti) + b"".join(pacchetti))
        dati[22:26] = struct.pack("<I", _crc_ogg(bytes(dati)))
        self._numero += 1
        self._scrittore.scrivi(bytes(dati))

    def aggiungi(self, pacchetto, campioni):
        segmenti = len(pacchetto) // 255 + 1
        if self._pacchetti and (self._segmenti + segmenti > 255 or self._campioni >= _PAGINA_OGG):
            self.pagina(0, self.granulo, self._pacchetti)
            self._pacchetti, self._segmenti, self._campioni = [], 0, 0
        self._pacchetti.append(pacchetto)
        self._segmenti += segmenti
        self._campioni += campioni
        self.granulo += campioni

    def fine(self, taglio_in_coda):
        self.pagina(4, max(0, self.granulo - taglio_in_coda), self._pacchetti)


def _accoda_opus(parti, mappe, scrittore):
    """Gli Opus, in un Ogg solo e non piu' in un Ogg concatenato, dove libmpv
    non salta oltre la prima parte e mutagen ne legge solo la durata: le
    intestazioni OpusHead e OpusTags della prima parte, poi i pacchetti
    audio di tutte, senza la riserva, con i granuli rifatti. In coda il
    taglio dell'ultima parte, che toglie il riempimento del codificatore."""
    pagine, preskip_iniziale, canali, tratti, taglio_in_coda = None, 0, None, [], 0
    for numero, (parte, dati) in enumerate(zip(parti, mappe, strict=True)):
        pacchetti, stato = _pacchetti_ogg(dati)
        testa = next(pacchetti, b"")
        etichette = next(pacchetti, b"")
        if testa[:8] != b"OpusHead" or len(testa) < 19 or etichette[:8] != b"OpusTags":
            raise ValueError("una parte non e' un Ogg Opus")
        preskip = struct.unpack("<H", testa[10:12])[0]
        if pagine is None:
            pagine, preskip_iniziale, canali = _PagineOgg(scrittore, stato["seriale"]), preskip, testa[9]
            pagine.pagina(2, 0, [testa])
            pagine.pagina(0, 0, [etichette])
        elif testa[9] != canali:
            raise ValueError("parti Opus con canali diversi")
        da_togliere = preskip + round(parte.taglio * OPUS_HZ) if parte.taglio > 0 else 0
        posizione, tolti, tutti = pagine.granulo, 0, 0
        for pacchetto in pacchetti:
            if not pacchetto:
                continue
            campioni = _campioni_opus(pacchetto)
            tutti += campioni
            if tolti < da_togliere:
                tolti += campioni
                continue
            pagine.aggiungi(pacchetto, campioni)
        taglio_in_coda = max(0, tutti - stato["granulo"])
        tenuti = pagine.granulo - posizione
        inizio = (posizione - preskip_iniziale + max(0, preskip - tolti)) / OPUS_HZ
        tagliati = max(0, tolti - preskip) / OPUS_HZ
        tratti.append([inizio, tagliati, (tenuti - (preskip_iniziale if numero == 0 else 0)) / OPUS_HZ])
    if pagine is None:
        raise ValueError("nessuna parte Opus")
    pagine.fine(taglio_in_coda)
    tratti[-1][2] = max(0.0, tratti[-1][2] - taglio_in_coda / OPUS_HZ)
    return [tuple(tratto) for tratto in tratti]
