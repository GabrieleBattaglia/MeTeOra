# MeTeOra, il collaudo sistematico dei formati audio comuni (tappa 6).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 02/10/2026: nasce con la tappa 6.

"""Ogni formato audio che MeTeOra riconosce e che FFmpeg sa anche scrivere:
il file di prova si fa al momento con la codifica di libmpv, da un la di sei
secondi, in una cartella temporanea; poi il motore, muto, lo apre, ne legge la
durata, ci salta dentro e arriva alla fine. APE, TAK, Musepack e DSD, che
FFmpeg legge ma non scrive, restano fuori; MIDI, tracker e video hanno le
loro tappe."""

import threading
import time
import wave

import numpy as np
import pytest

import formati
import motore
import schedario

SECONDI = 6.0
# Le codifiche allungano un poco il file: i PCM di libmpv arrivano a un
# multiplo di 1024 campioni, 6.144 secondi, e TTA ai suoi blocchi.
DURATA_MASSIMA = 6.3
# L'AAC grezzo, senza contenitore (ADTS), non scrive la durata: FFmpeg la
# stima dal bitrate, e sui sei secondi di prova dice quasi sedici. Nel motore
# si controlla solo che si apra, che ci si salti dentro e che finisca; lo
# schedario, che da' la durata alla plancia, la conta giusta (1.62.4).
DURATA_STIMATA = {"aac"}
# Estensione: (codificatore, contenitore) per la codifica di libmpv.
FORMATI = {
    "wav": ("pcm_s16le", "wav"),
    "mp3": ("libmp3lame", "mp3"),
    "mp2": ("mp2", "mp2"),
    "ogg": ("libvorbis", "ogg"),
    "oga": ("libvorbis", "ogg"),
    "opus": ("libopus", "ogg"),
    "flac": ("flac", "flac"),
    "m4a": ("aac", "ipod"),
    "aac": ("aac", "adts"),
    "alac": ("alac", "ipod"),
    "wma": ("wmav2", "asf"),
    "ac3": ("ac3", "ac3"),
    "aiff": ("pcm_s16be", "aiff"),
    "aif": ("pcm_s16be", "aiff"),
    "wv": ("wavpack", "wv"),
    "tta": ("tta", "tta"),
    "mka": ("libopus", "matroska"),
    "au": ("pcm_s16be", "au"),
    "caf": ("pcm_s16le", "caf"),
}


def _aspetta(condizione, secondi=5):
    fine = time.perf_counter() + secondi
    while time.perf_counter() < fine:
        if condizione():
            return True
        time.sleep(0.01)
    return condizione()


def _codifica(sorgente, uscita, codificatore, contenitore):
    finito = threading.Event()
    m = motore.mpv.MPV(o=str(uscita), oac=codificatore, of=contenitore, ao="null", vo="null", video="no", config=False)
    try:
        m.register_event_callback(lambda evento: finito.set() if evento.event_id.value == motore.mpv.MpvEventID.END_FILE else None)
        m.play(str(sorgente))
        assert finito.wait(30), uscita
    finally:
        m.terminate()


@pytest.fixture(scope="module")
def file_di_prova(tmp_path_factory):
    cartella = tmp_path_factory.mktemp("formati")
    sorgente = cartella / "sorgente.wav"
    t = np.arange(int(48000 * SECONDI)) / 48000
    with wave.open(str(sorgente), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(48000)
        onda = (0.3 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        f.writeframes(np.repeat(onda, 2).tobytes())
    file = {}
    for estensione, (codificatore, contenitore) in FORMATI.items():
        file[estensione] = cartella / f"prova.{estensione}"
        _codifica(sorgente, file[estensione], codificatore, contenitore)
    return file


@pytest.mark.parametrize("estensione", list(FORMATI))
def test_il_formato_si_riconosce_si_apre_si_salta_e_finisce(file_di_prova, estensione):
    percorso = str(file_di_prova[estensione])
    assert formati.supportato(percorso)
    # La durata della plancia: mutagen, libmpv per i formati che mutagen non
    # conosce, e per l'AAC grezzo il conto dei fotogrammi (1.62.4).
    assert SECONDI <= schedario.leggi_scheda(percorso)["durata"] <= DURATA_MASSIMA, estensione
    finiti, errori = [], []
    m = motore.Motore(ao="null", alla_fine=lambda: finiti.append(True), all_errore=errori.append)
    try:
        m.suona(percorso)
        assert _aspetta(lambda: (m.posizione or 0) > 0), estensione
        if estensione not in DURATA_STIMATA:
            assert SECONDI <= m.durata <= DURATA_MASSIMA, (estensione, m.durata)
        m.vai_a(3.0)
        assert _aspetta(lambda: 3.0 <= (m.posizione or 0) < 3.5, 2), (estensione, m.posizione)
        m.vai_a(SECONDI - 0.4)
        assert _aspetta(lambda: finiti, 3), estensione
        assert not errori
    finally:
        m.chiudi()
