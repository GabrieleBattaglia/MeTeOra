# MeTeOra, i MIDI: FluidSynth con un banco di suoni General MIDI, resa in RAM come i SID.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 8 (issue 16). Nella 1.67.4 solo i banchi General MIDI, e la cartella dei temporanei saltata.

"""I MIDI di MeTeOra (tappa 8, issue 16).

Fino alla 1.64.0 i MIDI li leggeva libmodplug dentro libmpv, che senza i
patch di TiMidity suona ogni voce con lo stesso suono di ripiego. Adesso li
rende FluidSynth con un banco di suoni General MIDI, nello stesso modo dei
SID: un filo in disparte rende il brano in RAM, piu' in fretta del tempo
reale, e libmpv lo legge come un WAV virtuale.
Il banco lo sceglie chi ascolta: al primo MIDI MeTeOra cerca nei dischi i
banchi validi e li propone; se non ce ne sono, scarica FluidR3, il banco
storico di FluidSynth. FluidSynth stesso si scarica al primo MIDI.
"""

import contextlib
import ctypes
import hashlib
import io
import os
import string
import struct
import tempfile
import threading
import time
import urllib.request
import zipfile
from ctypes import wintypes

import numpy as np

import percorsi
import sid

# I file dei banchi di suoni, e le cartelle che la ricerca non visita.
ESTENSIONI_DEI_BANCHI = (".sf2", ".sf3")
CARTELLE_DA_SALTARE = frozenset({"windows", "$recycle.bin", "system volume information", "recovery", "config.msi", "$windows.~bt", "$windows.~ws",
    "$winreagent", "node_modules", ".git", "__pycache__"})
_DISCO_FISSO = 3


def e_un_banco(percorso):
    """Vero se il file e' un banco di suoni SoundFont, sf2 o sf3:
    un RIFF di tipo sfbk."""
    try:
        with open(percorso, "rb") as f:
            testa = f.read(12)
    except OSError:
        return False
    return len(testa) == 12 and testa[:4] == b"RIFF" and testa[8:12] == b"sfbk"


def general_midi(percorso):
    """Vero se il banco ha tutti gli strumenti del General MIDI: i 128
    programmi nel banco 0 e una batteria nel banco 128. Lo dice l'elenco dei
    preset, il chunk phdr dentro la lista pdta; i campioni, che possono
    pesare un gigabyte, si saltano senza leggerli (1.67.4)."""
    try:
        with open(percorso, "rb") as f:
            testa = f.read(12)
            if len(testa) < 12 or testa[:4] != b"RIFF" or testa[8:12] != b"sfbk":
                return False
            fine = 8 + struct.unpack("<I", testa[4:8])[0]
            while f.tell() + 8 <= fine:
                intestazione = f.read(8)
                if len(intestazione) < 8:
                    return False
                nome, dimensione = intestazione[:4], struct.unpack("<I", intestazione[4:])[0]
                if nome == b"LIST" and f.read(4) == b"pdta":
                    fine_della_lista = f.tell() + dimensione - 4
                    while f.tell() + 8 <= fine_della_lista:
                        sotto = f.read(8)
                        if len(sotto) < 8:
                            return False
                        nome_sotto, dimensione_sotto = sotto[:4], struct.unpack("<I", sotto[4:])[0]
                        if nome_sotto == b"phdr":
                            return _preset_general_midi(f.read(dimensione_sotto))
                        f.seek(dimensione_sotto + (dimensione_sotto & 1), 1)
                    return False
                if nome == b"LIST":
                    f.seek(dimensione - 4 + (dimensione & 1), 1)
                else:
                    f.seek(dimensione + (dimensione & 1), 1)
    except (OSError, struct.error):
        return False
    return False


def _preset_general_midi(dati):
    """Dai record del phdr, 38 byte l'uno con l'ultimo che chiude l'elenco:
    vero se ci sono i 128 programmi del banco 0 e una batteria nel 128."""
    programmi, batteria = set(), False
    for indice in range(len(dati) // 38 - 1):
        programma, banco = struct.unpack_from("<HH", dati, indice * 38 + 20)
        if banco == 0 and programma < 128:
            programmi.add(programma)
        elif banco == 128:
            batteria = True
    return len(programmi) == 128 and batteria


def dimensione_da_leggere(byte):
    """La dimensione di un banco in MB: con un decimale sotto i 10 MB, il punto
    come separatore, perche' sotto il mezzo MB l'arrotondamento dava 0 MB."""
    mega = byte / 1_000_000
    return f"{mega:.1f} MB" if mega < 10 else f"{round(mega)} MB"


def dischi_fissi():
    """Le radici dei dischi fissi del computer, per esempio C:\\ ed E:\\."""
    kernel32 = ctypes.windll.kernel32
    maschera = kernel32.GetLogicalDrives()
    radici = []
    for indice, lettera in enumerate(string.ascii_uppercase):
        radice = f"{lettera}:\\"
        if maschera & (1 << indice) and kernel32.GetDriveTypeW(wintypes.LPCWSTR(radice)) == _DISCO_FISSO:
            radici.append(radice)
    return radici


def cerca_banchi(radici=None, avvisa=None, fermo=None):
    """I banchi General MIDI nelle radici, di partenza tutti i dischi fissi:
    lista di (percorso, dimensione in byte), in ordine di nome. I banchi di
    pochi strumenti, che suonerebbero un MIDI con strumenti sbagliati o
    mancanti, restano fuori (Gabriele, 3 ottobre 2026).
    avvisa(cartelle) arriva ogni tanto con le cartelle visitate fin li';
    fermo(), se c'e' e torna vero, interrompe la ricerca. Le cartelle di
    sistema, nascoste o illeggibili si saltano, e anche quella dei file
    temporanei, dove i banchi sono di passaggio."""
    trovati = []
    visitate = 0
    temporanei = os.path.normcase(tempfile.gettempdir())
    for radice in radici if radici is not None else dischi_fissi():
        for cartella, sottocartelle, files in os.walk(radice, onerror=lambda _errore: None):
            if fermo is not None and fermo():
                return sorted(trovati, key=lambda t: os.path.basename(t[0]).casefold())
            visitate += 1
            if avvisa is not None and visitate % 2000 == 0:
                avvisa(visitate)
            sottocartelle[:] = [s for s in sottocartelle if s.casefold() not in CARTELLE_DA_SALTARE and not s.startswith("$")
                and os.path.normcase(os.path.join(cartella, s)) != temporanei]
            for nome in files:
                if nome.lower().endswith(ESTENSIONI_DEI_BANCHI):
                    percorso = os.path.join(cartella, nome)
                    if general_midi(percorso):
                        with contextlib.suppress(OSError):
                            trovati.append((percorso, os.path.getsize(percorso)))
    return sorted(trovati, key=lambda t: os.path.basename(t[0]).casefold())


def durata(percorso):
    """I secondi di un file MIDI secondo la sua mappa dei tempi, o None se
    non si legge: mutagen.File non riconosce i MIDI, la sua classe SMF si'."""
    try:
        from mutagen.smf import SMF

        secondi = SMF(percorso).info.length
    except Exception:  # noqa: BLE001 - un MIDI rovinato non deve fermare chi chiede
        return None
    return float(secondi) if secondi else None


# FluidSynth, la versione provata il 3 ottobre 2026: lo zip ufficiale per
# Windows a 64 bit, la sua impronta, e le due DLL che servono.
FLUIDSYNTH_URL = "https://github.com/FluidSynth/fluidsynth/releases/download/v2.6.1/fluidsynth-v2.6.1-win10-x64-cpp11.zip"
FLUIDSYNTH_SHA256 = "fab7a2e4b85675b66970f97a39bbc239729c5e0f237198b5922a6a73cbc8677c"
FLUIDSYNTH_DLL = ("libfluidsynth-3.dll", "sndfile.dll")
# FluidR3 GM, il banco che MeTeOra scarica quando nei dischi non ne trova:
# licenza MIT, le fonti in ordine di preferenza e la dimensione giusta.
FLUIDR3_NOME = "FluidR3_GM.sf2"
FLUIDR3_URL = (
    "https://github.com/pianobooster/fluid-soundfont/releases/download/v3.1/FluidR3_GM.sf2",
    "https://github.com/fhunleth/midi_synth/releases/download/v0.1.0/FluidR3_GM.sf2",
)
FLUIDR3_DIMENSIONE = 148398306
# FluidSynth aspetta due secondi dopo l'ultimo evento prima di dire finito:
# la coda delle note che si spengono.
CODA = 2.0
_SUONA = 1
# La stima dell'attesa dopo un salto: FluidSynth rende un MIDI piu' di cento
# volte piu' in fretta del tempo reale (misura del 3 ottobre 2026).
VELOCITA_STIMATA = 50.0
VELOCITA_MASSIMA_STIMATA = 100.0
# I livelli dei messaggi di FluidSynth che si tacciono: avvisi, informazioni
# e messaggi di debug, che finirebbero sulla console.
_LIVELLI_TACIUTI = (2, 3, 4)
_PEZZO_DELLO_SCARICAMENTO = 1 << 20


def cartella_fluidsynth():
    """Dove MeTeOra tiene FluidSynth scaricato: accanto ai suoi dati."""
    return percorsi.percorso_dati("fluidsynth")


def cartella_dei_banchi():
    """Dove MeTeOra mette i banchi che scarica."""
    return percorsi.percorso_dati("banchi")


def fluidsynth_presente():
    return all(os.path.isfile(os.path.join(cartella_fluidsynth(), dll)) for dll in FLUIDSYNTH_DLL)


def _scarica(url, avanza=None):
    """I byte di un URL, a pezzi: avanza(scaricati, totale) a ogni pezzo,
    con totale None se il server non lo dice."""
    if not url.startswith("https://"):
        raise ValueError(f"solo indirizzi https: {url}")
    richiesta = urllib.request.Request(url, headers={"User-Agent": "MeTeOra"})  # noqa: S310 - indirizzi https fissi, controllati sopra
    with urllib.request.urlopen(richiesta, timeout=60) as risposta:  # noqa: S310 - idem
        totale = int(risposta.headers.get("Content-Length") or 0) or None
        pezzi, scaricati = [], 0
        while pezzo := risposta.read(_PEZZO_DELLO_SCARICAMENTO):
            pezzi.append(pezzo)
            scaricati += len(pezzo)
            if avanza is not None:
                avanza(scaricati, totale)
    return b"".join(pezzi)


def scarica_fluidsynth(avanza=None):
    """Scarica FluidSynth, ne controlla l'impronta e ne mette le DLL nella
    sua cartella. Solleva OSError se qualcosa non va."""
    dati = _scarica(FLUIDSYNTH_URL, avanza)
    if hashlib.sha256(dati).hexdigest() != FLUIDSYNTH_SHA256:
        raise OSError("lo zip di FluidSynth scaricato non è quello atteso")
    cartella = cartella_fluidsynth()
    os.makedirs(cartella, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(dati)) as archivio:
        for nome in archivio.namelist():
            if os.path.basename(nome) in FLUIDSYNTH_DLL and "/bin/" in nome:
                with open(os.path.join(cartella, os.path.basename(nome)), "wb") as f:
                    f.write(archivio.read(nome))
    if not fluidsynth_presente():
        raise OSError("nello zip di FluidSynth mancano le DLL attese")


def scarica_fluidr3(avanza=None):
    """Scarica FluidR3 GM dalla prima fonte che risponde, controlla dimensione
    e intestazione, e restituisce il percorso del banco. OSError se nessuna
    fonte va."""
    cartella = cartella_dei_banchi()
    os.makedirs(cartella, exist_ok=True)
    destinazione = os.path.join(cartella, FLUIDR3_NOME)
    errori = []
    for url in FLUIDR3_URL:
        try:
            dati = _scarica(url, avanza)
        except OSError as e:
            errori.append(str(e))
            continue
        if len(dati) != FLUIDR3_DIMENSIONE or dati[:4] != b"RIFF" or dati[8:12] != b"sfbk":
            errori.append(f"{url}: il file non è FluidR3 GM")
            continue
        parziale = destinazione + ".parziale"
        with open(parziale, "wb") as f:
            f.write(dati)
        os.replace(parziale, destinazione)
        return destinazione
    raise OSError("; ".join(errori) or "nessuna fonte di FluidR3 GM risponde")


# La libreria di FluidSynth, caricata alla prima resa.
_LIBRERIA = []
_LIBRERIA_BLOCCO = threading.Lock()


def _fluid():
    with _LIBRERIA_BLOCCO:
        if _LIBRERIA:
            return _LIBRERIA[0]
        dll = ctypes.CDLL(os.path.join(cartella_fluidsynth(), FLUIDSYNTH_DLL[0]))
        p = ctypes.c_void_p
        firme = {
            "new_fluid_settings": (p, []),
            "fluid_settings_setnum": (ctypes.c_int, [p, ctypes.c_char_p, ctypes.c_double]),
            "fluid_settings_setint": (ctypes.c_int, [p, ctypes.c_char_p, ctypes.c_int]),
            "fluid_settings_setstr": (ctypes.c_int, [p, ctypes.c_char_p, ctypes.c_char_p]),
            "new_fluid_synth": (p, [p]),
            "fluid_synth_sfload": (ctypes.c_int, [p, ctypes.c_char_p, ctypes.c_int]),
            "fluid_synth_system_reset": (ctypes.c_int, [p]),
            "new_fluid_player": (p, [p]),
            "fluid_player_add": (ctypes.c_int, [p, ctypes.c_char_p]),
            "fluid_player_play": (ctypes.c_int, [p]),
            "fluid_player_get_status": (ctypes.c_int, [p]),
            "fluid_player_stop": (ctypes.c_int, [p]),
            "fluid_synth_write_s16": (ctypes.c_int, [p, ctypes.c_int, p, ctypes.c_int, ctypes.c_int, p, ctypes.c_int, ctypes.c_int]),
            "delete_fluid_player": (None, [p]),
            "delete_fluid_synth": (None, [p]),
            "delete_fluid_settings": (None, [p]),
            "fluid_set_log_function": (p, [ctypes.c_int, p, p]),
        }
        for nome, (risultato, argomenti) in firme.items():
            funzione = getattr(dll, nome)
            funzione.restype, funzione.argtypes = risultato, argomenti
        for livello in _LIVELLI_TACIUTI:
            dll.fluid_set_log_function(livello, None, None)
        _LIBRERIA.append(dll)
        return dll


# I synth con il banco gia' caricato, pronti per il brano dopo: caricare
# FluidR3, 148 MB, a ogni MIDI ritarderebbe ogni partenza.
_SYNTH = {}
_SYNTH_BLOCCO = threading.Lock()
_SYNTH_TENUTI = 2


def _prendi_il_synth(banco):
    """(settings, synth) con il banco caricato, dalla scorta o nuovo.
    OSError se il banco non si carica."""
    with _SYNTH_BLOCCO:
        scorta = _SYNTH.get(banco)
        if scorta:
            return scorta.pop()
    fs = _fluid()
    settings = fs.new_fluid_settings()
    fs.fluid_settings_setnum(settings, b"synth.sample-rate", float(sid.FREQUENZA))
    fs.fluid_settings_setstr(settings, b"player.timing-source", b"sample")
    fs.fluid_settings_setint(settings, b"synth.lock-memory", 0)
    synth = fs.new_fluid_synth(settings)
    if not synth or fs.fluid_synth_sfload(synth, banco.encode("utf-8"), 1) < 0:
        if synth:
            fs.delete_fluid_synth(synth)
        fs.delete_fluid_settings(settings)
        raise OSError(f"il banco di suoni {banco} non si carica")
    return settings, synth


def _rendi_il_synth(banco, coppia):
    """Rimette il synth nella scorta del suo banco, azzerato, o lo chiude."""
    _fluid().fluid_synth_system_reset(coppia[1])
    with _SYNTH_BLOCCO:
        scorta = _SYNTH.setdefault(banco, [])
        if len(scorta) < _SYNTH_TENUTI:
            scorta.append(coppia)
            return
    _chiudi_il_synth(coppia)


def _chiudi_il_synth(coppia):
    fs = _fluid()
    fs.delete_fluid_synth(coppia[1])
    fs.delete_fluid_settings(coppia[0])


def svuota_la_scorta(tranne=None):
    """Chiude i synth tenuti da parte, tranne quelli del banco dato: per
    quando il banco cambia."""
    with _SYNTH_BLOCCO:
        da_chiudere = [coppia for banco, scorta in _SYNTH.items() if banco != tranne for coppia in scorta]
        for banco in [b for b in _SYNTH if b != tranne]:
            del _SYNTH[banco]
    for coppia in da_chiudere:
        _chiudi_il_synth(coppia)


class BranoMidi(sid.BranoSid):
    """Un MIDI reso in memoria con FluidSynth, da un filo che corre in
    anticipo: come un sottobrano dei SID, di cui riprende l'attesa e la
    lettura. secondi e' la durata dalla mappa dei tempi, piu' la coda."""

    VELOCITA_STIMATA = VELOCITA_STIMATA
    VELOCITA_MASSIMA_STIMATA = VELOCITA_MASSIMA_STIMATA

    def __init__(self, percorso, banco, secondi):
        self._banco = banco
        self._coppia = _prendi_il_synth(banco)
        fs = _fluid()
        self._player = fs.new_fluid_player(self._coppia[1])
        if not self._player or fs.fluid_player_add(self._player, percorso.encode("utf-8")) != 0 or fs.fluid_player_play(self._player) != 0:
            if self._player:
                fs.delete_fluid_player(self._player)
            _rendi_il_synth(banco, self._coppia)
            raise OSError(f"FluidSynth non apre {percorso}")
        self.totale = int(secondi * sid.FREQUENZA) * sid.CANALI
        self.dati = np.zeros(self.totale, dtype=np.int16)
        self.pronti = 0
        self._fermo = False
        self._condizione = threading.Condition()
        self._partenza = time.perf_counter()
        self._filo = threading.Thread(target=self._lavora, name="MeTeOra, resa del MIDI", daemon=True)
        self._filo.start()

    def _lavora(self):
        fs = _fluid()
        synth = self._coppia[1]
        try:
            while self.pronti < self.totale and not self._fermo and fs.fluid_player_get_status(self._player) == _SUONA:
                n = min(sid.BLOCCO, self.totale - self.pronti)
                indirizzo = self.dati[self.pronti:].ctypes.data
                fs.fluid_synth_write_s16(synth, n // sid.CANALI, indirizzo, 0, 2, indirizzo, 1, 2)
                with self._condizione:
                    self.pronti += n
                    self._condizione.notify_all()
        finally:
            # Finito prima della durata attesa: il resto e' silenzio, gia'
            # zero, e chi legge non deve aspettarlo.
            with self._condizione:
                self.pronti = self.totale
                self._condizione.notify_all()
            fs.fluid_player_stop(self._player)
            fs.delete_fluid_player(self._player)
            _rendi_il_synth(self._banco, self._coppia)


# I MIDI aperti, per chiave (percorso, banco, secondi), come i SID.
_CONDIVISI = {}
_CONDIVISI_BLOCCO = threading.Lock()


def apri_flusso(percorso, banco, secondi):
    """Un flusso WAV sul MIDI reso con il banco dato; i flussi aperti insieme
    sullo stesso MIDI condividono la resa, come i SID."""
    chiave = (os.path.normcase(os.path.abspath(percorso)), banco, secondi)
    with _CONDIVISI_BLOCCO:
        voce = _CONDIVISI.get(chiave)
        if voce is None:
            voce = [BranoMidi(percorso, banco, secondi), 0]
            _CONDIVISI[chiave] = voce
        voce[1] += 1
    return sid.FlussoSid(voce[0], lambda: _lascia(chiave))


def _lascia(chiave):
    with _CONDIVISI_BLOCCO:
        voce = _CONDIVISI[chiave]
        voce[1] -= 1
        if voce[1]:
            return
        del _CONDIVISI[chiave]
    voce[0].ferma()
