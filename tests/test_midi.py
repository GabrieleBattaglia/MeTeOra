# MeTeOra, le prove dei MIDI: i banchi, le durate, gli scaricamenti finti e la resa con FluidSynth.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 8.

"""Nessuna prova scarica davvero o suona: gli scaricamenti sono finti, e la
resa vera usa FluidSynth e GeneralUser GS del banco degli ascolti, se ci
sono, a motore muto."""

import hashlib
import io
import os
import struct
import time
import zipfile

import pytest

import midi
import motore

BANCO_DEGLI_ASCOLTI = r"E:\git\tmp\player-accessibile\ascolti_midi\scaricati"
FLUIDSYNTH_DEGLI_ASCOLTI = os.path.join(BANCO_DEGLI_ASCOLTI, "bin")
GENERALUSER = os.path.join(BANCO_DEGLI_ASCOLTI, "GeneralUser-GS.sf2")
CI_SONO = os.path.isfile(os.path.join(FLUIDSYNTH_DEGLI_ASCOLTI, "libfluidsynth-3.dll")) and os.path.isfile(GENERALUSER)


def _varlen(n):
    uscita = [n & 0x7F]
    n >>= 7
    while n:
        uscita.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(uscita)


def midi_di_prova(percorso, battiti=8):
    """Un MIDI di formato 0, a 120 bpm, con un pianoforte che suona una nota
    per battito: battiti mezzi secondi."""
    eventi = _varlen(0) + bytes([0xFF, 0x51, 3]) + (500000).to_bytes(3, "big") + _varlen(0) + bytes([0xC0, 0])
    for indice in range(battiti):
        nota = 60 + indice % 12
        eventi += _varlen(0) + bytes([0x90, nota, 100]) + _varlen(480) + bytes([0x80, nota, 0])
    eventi += _varlen(0) + bytes([0xFF, 0x2F, 0])
    percorso.write_bytes(b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + b"MTrk" + struct.pack(">I", len(eventi)) + eventi)
    return str(percorso)


def banco_di_prova(percorso, general_midi=True):
    """Un banco SoundFont senza campioni, con il solo elenco dei preset: i
    128 programmi del banco 0 e la batteria del 128 se general_midi,
    altrimenti un pianoforte solo, come i banchi di uno strumento."""
    percorso.parent.mkdir(parents=True, exist_ok=True)
    preset = [*((p, 0) for p in range(128)), (0, 128)] if general_midi else [(0, 0)]
    record = b"".join(struct.pack("<20sHHHIII", f"P{n}".encode(), p, b, 0, 0, 0, 0) for n, (p, b) in enumerate(preset))
    record += struct.pack("<20sHHHIII", b"EOP", 0, 0, 0, 0, 0, 0)

    def lista(tipo, contenuto):
        return b"LIST" + struct.pack("<I", 4 + len(contenuto)) + tipo + contenuto

    corpo = b"sfbk" + lista(b"INFO", b"ifil" + struct.pack("<IHH", 4, 2, 1)) + lista(b"sdta", b"") + lista(b"pdta", b"phdr" + struct.pack("<I", len(record)) + record)
    percorso.write_bytes(b"RIFF" + struct.pack("<I", len(corpo)) + corpo)
    return str(percorso)


_banco = banco_di_prova


def test_e_un_banco(tmp_path):
    assert midi.e_un_banco(_banco(tmp_path / "buono.sf2"))
    # General MIDI: i 128 programmi e la batteria; un banco di uno strumento no.
    assert midi.general_midi(str(tmp_path / "buono.sf2"))
    assert midi.e_un_banco(banco_di_prova(tmp_path / "piano.sf2", general_midi=False)) and not midi.general_midi(str(tmp_path / "piano.sf2"))
    (tmp_path / "corto.sf2").write_bytes(b"RIFF\0\0\0\0sfbk" + bytes(20))
    assert not midi.general_midi(str(tmp_path / "corto.sf2"))
    assert (midi.dimensione_da_leggere(4_200_000), midi.dimensione_da_leggere(148_398_306), midi.dimensione_da_leggere(200_000)) == ("4.2 MB", "148 MB", "0.2 MB")
    (tmp_path / "falso.sf2").write_bytes(b"RIFF\0\0\0\0WAVEfmt ")
    assert not midi.e_un_banco(str(tmp_path / "falso.sf2"))
    assert not midi.e_un_banco(str(tmp_path / "manca.sf2"))


def test_cerca_banchi(tmp_path, monkeypatch):
    _banco(tmp_path / "Musica" / "Banchi" / "Zeta.sf2")
    _banco(tmp_path / "Alfa.SF3")
    _banco(tmp_path / "Windows" / "Nascosto.sf2")
    _banco(tmp_path / "$Recycle.Bin" / "Cestinato.sf2")
    (tmp_path / "Musica" / "falso.sf2").write_bytes(b"niente")
    # Un banco di uno strumento solo, e uno nella cartella dei temporanei, restano fuori.
    banco_di_prova(tmp_path / "Strumenti" / "Piano.sf2", general_midi=False)
    _banco(tmp_path / "Temp" / "Di passaggio.sf2")
    monkeypatch.setattr(midi.tempfile, "gettempdir", lambda: str(tmp_path / "Temp"))
    trovati = midi.cerca_banchi([str(tmp_path)])
    assert [os.path.basename(p) for p, _d in trovati] == ["Alfa.SF3", "Zeta.sf2"] and trovati[0][1] == os.path.getsize(tmp_path / "Alfa.SF3")
    # fermo interrompe la ricerca.
    assert midi.cerca_banchi([str(tmp_path)], fermo=lambda: True) == []


def test_durata_di_un_midi(tmp_path):
    assert midi.durata(midi_di_prova(tmp_path / "otto.mid")) == pytest.approx(4.0, abs=0.01)
    (tmp_path / "rotto.mid").write_bytes(b"MThd rotto")
    assert midi.durata(str(tmp_path / "rotto.mid")) is None


def test_lo_scaricamento_accetta_solo_https():
    with pytest.raises(ValueError):
        midi._scarica("http://example.invalid/x")


def test_scarica_fluidsynth_controlla_l_impronta(tmp_path, monkeypatch):
    zip_finto = io.BytesIO()
    with zipfile.ZipFile(zip_finto, "w") as archivio:
        for nome in midi.FLUIDSYNTH_DLL:
            archivio.writestr(f"fluidsynth/bin/{nome}", b"dll finta")
        archivio.writestr("fluidsynth/bin/SDL3.dll", b"non serve")
    dati = zip_finto.getvalue()
    monkeypatch.setattr(midi, "cartella_fluidsynth", lambda: str(tmp_path / "fluidsynth"))
    monkeypatch.setattr(midi, "_scarica", lambda url, avanza=None: dati)
    with pytest.raises(OSError, match="non è quello atteso"):
        midi.scarica_fluidsynth()
    monkeypatch.setattr(midi, "FLUIDSYNTH_SHA256", hashlib.sha256(dati).hexdigest())
    midi.scarica_fluidsynth()
    assert sorted(os.listdir(tmp_path / "fluidsynth")) == sorted(midi.FLUIDSYNTH_DLL) and midi.fluidsynth_presente()


def test_scarica_fluidr3_prova_le_fonti_in_ordine(tmp_path, monkeypatch):
    buono = b"RIFF\0\0\0\0sfbk" + bytes(20)
    monkeypatch.setattr(midi, "cartella_dei_banchi", lambda: str(tmp_path / "banchi"))
    monkeypatch.setattr(midi, "FLUIDR3_DIMENSIONE", len(buono))
    risposte = {midi.FLUIDR3_URL[0]: OSError("non risponde"), midi.FLUIDR3_URL[1]: buono}

    def scarica(url, avanza=None):
        risposta = risposte[url]
        if isinstance(risposta, Exception):
            raise risposta
        return risposta

    monkeypatch.setattr(midi, "_scarica", scarica)
    percorso = midi.scarica_fluidr3()
    assert percorso == str(tmp_path / "banchi" / midi.FLUIDR3_NOME) and midi.e_un_banco(percorso)
    risposte[midi.FLUIDR3_URL[1]] = b"pagina d'errore"
    with pytest.raises(OSError, match=r"non risponde.*non è FluidR3 GM"):
        midi.scarica_fluidr3()


@pytest.mark.skipif(not CI_SONO, reason="servono FluidSynth e GeneralUser GS del banco degli ascolti")
def test_la_resa_con_fluidsynth(tmp_path, monkeypatch):
    import numpy as np

    monkeypatch.setattr(midi, "cartella_fluidsynth", lambda: FLUIDSYNTH_DEGLI_ASCOLTI)
    percorso = midi_di_prova(tmp_path / "prova.mid")
    brano = midi.BranoMidi(percorso, GENERALUSER, 4.0 + midi.CODA)
    try:
        assert brano.aspetta(brano.totale, 10)
        assert np.abs(brano.dati).max() > 1000
        # Dopo la coda e' silenzio.
        assert np.abs(brano.dati[-midi.sid.FREQUENZA // 10:]).max() < 50
    finally:
        brano.ferma()
    # La seconda apertura prende il synth dalla scorta: niente banco da ricaricare.
    inizio = time.perf_counter()
    secondo = midi.BranoMidi(percorso, GENERALUSER, 1.0)
    assert time.perf_counter() - inizio < 0.05
    secondo.ferma()


@pytest.mark.skipif(not CI_SONO, reason="servono FluidSynth e GeneralUser GS del banco degli ascolti")
def test_il_motore_suona_un_midi_con_il_banco(tmp_path, monkeypatch):
    monkeypatch.setattr(midi, "cartella_fluidsynth", lambda: FLUIDSYNTH_DEGLI_ASCOLTI)
    percorso = midi_di_prova(tmp_path / "prova.mid", battiti=16)
    m = motore.Motore(ao="null")
    try:
        m.banco_midi = GENERALUSER
        m.suona(percorso)
        fine = time.perf_counter() + 10
        while time.perf_counter() < fine and not (m.posizione or 0) > 0:
            time.sleep(0.01)
        assert (m.posizione or 0) > 0 and m.durata == pytest.approx(8.0 + midi.CODA, abs=0.05)
        assert m._attivo.flusso is not None and isinstance(m._attivo.flusso.brano, midi.BranoMidi)
    finally:
        m.chiudi()
