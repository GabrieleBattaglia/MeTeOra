# MeTeOra, le prove della musica delle console: libgme, i file a piu' brani, la resa e il motore.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 8.

"""I file delle prove li scrive la prova stessa: un VGM del Sega con un la
a 440 Hz, e un NSF del NES a piu' brani, muti o con un la. Il motore suona
a uscita nulla: nessun suono dagli altoparlanti."""

import struct
import time

import pytest

import chip
import formati
import motore
import sottobrani

pytestmark = pytest.mark.skipif(not chip.presente(), reason="manca lib/libgme.dll: la mette strumenti/prepara_ambiente.py")


def vgm_di_prova(percorso, secondi=1):
    """Un VGM 1.50 con il chip SN76489 del Sega: un la a 440 Hz per i secondi
    dati, poi il silenzio; il file dice la sua durata."""
    campioni = 44100 * secondi
    dati = bytes([0x50, 0x8E, 0x50, 0x0F, 0x50, 0x90])
    resto = campioni
    while resto:
        passo = min(resto, 0xFFFF)
        dati += bytes([0x61]) + struct.pack("<H", passo)
        resto -= passo
    dati += bytes([0x50, 0x9F, 0x66])
    testa = bytearray(0x40)
    testa[0:4] = b"Vgm "
    struct.pack_into("<I", testa, 0x08, 0x150)
    struct.pack_into("<I", testa, 0x0C, 3579545)
    struct.pack_into("<I", testa, 0x18, campioni)
    struct.pack_into("<I", testa, 0x24, 60)
    struct.pack_into("<HBB", testa, 0x28, 0x0009, 16, 0)
    struct.pack_into("<I", testa, 0x34, 0x0C)
    struct.pack_into("<I", testa, 0x04, len(testa) + len(dati) - 4)
    percorso.write_bytes(bytes(testa) + dati)
    return str(percorso)


# Il la del NES: il primo canale a onda quadra, volume pieno, periodo 253,
# acceso dall'init; il play non fa niente.
_LA_DEL_NES = bytes([0xA9, 0x01, 0x8D, 0x15, 0x40, 0xA9, 0xBF, 0x8D, 0x00, 0x40, 0xA9, 0xFD, 0x8D, 0x02, 0x40, 0xA9, 0x00, 0x8D, 0x03, 0x40, 0x60])


def nsf_di_prova(percorso, brani=3, tono=False):
    """Un NSF con i brani dati, muti (init e play sono un RTS) o con un la
    che non finisce mai."""
    testa = bytearray(0x80)
    testa[0:5] = b"NESM\x1a"
    testa[5], testa[6], testa[7] = 1, brani, 1
    codice = _LA_DEL_NES if tono else b"\x60"
    struct.pack_into("<HHH", testa, 8, 0x8000, 0x8000, 0x8000 + len(codice) - 1)
    testa[0x0E:0x0E + 5] = b"Prova"
    testa[0x2E:0x2E + 7] = b"ClaudIA"
    testa[0x4E:0x4E + 4] = b"2026"
    struct.pack_into("<H", testa, 0x6E, 16666)
    struct.pack_into("<H", testa, 0x78, 20000)
    percorso.write_bytes(bytes(testa) + codice + b"\x60" * 0x100)
    return str(percorso)


def test_i_formati_delle_console():
    assert formati.e_chip(r"C:\m\Mega Man 2.nsf") and formati.e_chip(r"C:\m\sonic.VGZ")
    assert formati.ha_sottobrani(r"C:\m\Commando.sid") and formati.ha_sottobrani(r"C:\m\zelda.spc")
    assert not formati.ha_sottobrani(r"C:\m\canzone.mid") and not formati.ha_sottobrani(r"C:\m\brano.mp3")
    assert formati.CHIP <= formati.TUTTI


def test_le_informazioni_di_un_nsf(tmp_path):
    percorso = nsf_di_prova(tmp_path / "prova.nsf")
    info = sottobrani.info(percorso)
    assert info["sottobrani"] == 3 and info["iniziale"] == 1
    assert (info["titolo"], info["autore"], info["copyright"]) == ("Prova", "ClaudIA", "2026")
    # Un NSF non dice quanto dura: due minuti e mezzo, piu' la dissolvenza.
    assert sottobrani.durate(percorso) == [150 + chip.DISSOLVENZA] * 3
    assert motore.durata_del_sottobrano(percorso, 2) == 150 + chip.DISSOLVENZA


def test_il_m3u_ordina_nomina_e_dice_le_durate(tmp_path):
    percorso = nsf_di_prova(tmp_path / "gioco.nsf")
    (tmp_path / "gioco.m3u").write_text("# commento\ngioco.nsf::NSF,2,Il secondo,0:42,,3\ngioco.nsf::NSF,1,Il primo,1:05,0:20,\n", encoding="cp1252")
    info = sottobrani.info(percorso)
    assert info["sottobrani"] == 2 and info["titoli"] == ["Il secondo", "Il primo"]
    # La durata scritta e' l'inizio della dissolvenza, che e' quella scritta o di otto secondi.
    assert info["durate"] == [45.0, 65 + chip.DISSOLVENZA]


def test_il_m3u_di_un_altro_file_non_si_carica(tmp_path):
    percorso = vgm_di_prova(tmp_path / "gioco.vgm", 2)
    (tmp_path / "gioco.m3u").write_text("gioco.nsf::NSF,2,Il secondo,0:42,,3\n", encoding="cp1252")
    assert chip.info(percorso)["durate"] == [2 + chip.CODA]
    # Con il nome cambiato, basta il tipo.
    (tmp_path / "rinominato.m3u").write_text("vecchio nome.vgm::VGM,1,Il primo,0:30,,2\n", encoding="cp1252")
    rinominato = vgm_di_prova(tmp_path / "rinominato.vgm", 2)
    assert chip.info(rinominato)["titoli"] == ["Il primo"]


def test_un_file_che_libgme_non_legge(tmp_path):
    percorso = tmp_path / "rotto.nsf"
    percorso.write_bytes(b"niente di buono")
    assert sottobrani.info(str(percorso)) is None and sottobrani.durate(str(percorso)) is None
    assert motore.sottobrano_risolto(str(percorso), None) is None


def test_la_resa_di_un_vgm(tmp_path):
    import numpy as np

    percorso = vgm_di_prova(tmp_path / "prova.vgm", 2)
    info = chip.info(percorso)
    assert info["sottobrani"] == 1 and info["durate"] == [2 + chip.CODA]
    brano = chip.BranoChip(percorso, 1, info["durate"][0])
    try:
        assert brano.aspetta(brano.totale, 10)
        dati = brano.dati.astype(np.float64)
        assert np.abs(dati[:chip.sid.FREQUENZA * 2]).max() > 1000
        # Un brano che finisce da se' non sfuma: il volume resta quello.
        mezzo_secondo = chip.sid.FREQUENZA
        inizio = np.sqrt(np.mean(dati[mezzo_secondo // 5:mezzo_secondo] ** 2))
        fine = np.sqrt(np.mean(dati[3 * mezzo_secondo:7 * mezzo_secondo // 2] ** 2))
        assert fine == pytest.approx(inizio, rel=0.1)
        # Finito il la, la coda e' silenzio.
        assert np.abs(dati[-chip.sid.FREQUENZA // 2:]).max() < 50
    finally:
        brano.ferma()


def test_un_brano_che_gira_in_tondo_sfuma(tmp_path):
    import numpy as np

    percorso = nsf_di_prova(tmp_path / "tono.nsf", 1, tono=True)
    (tmp_path / "tono.m3u").write_text("tono.nsf::NSF,1,Il la,0:01,,1\n", encoding="cp1252")
    assert chip.info(percorso)["durate"] == [2.0]
    brano = chip.BranoChip(percorso, 1, 2.0)
    try:
        assert brano.aspetta(brano.totale, 10)
        dati = brano.dati.astype(np.float64)
        decimo = chip.sid.FREQUENZA * chip.sid.CANALI // 10
        prima = np.sqrt(np.mean(dati[5 * decimo:9 * decimo] ** 2))
        durante = np.sqrt(np.mean(dati[14 * decimo:15 * decimo] ** 2))
        alla_fine = np.sqrt(np.mean(dati[-decimo:] ** 2))
        assert prima > 1000 and alla_fine < durante < prima
    finally:
        brano.ferma()


def test_i_flussi_sullo_stesso_brano_condividono_la_resa(tmp_path):
    percorso = vgm_di_prova(tmp_path / "prova.vgm", 1)
    primo = chip.apri_flusso(percorso, 1, 2.0)
    secondo = chip.apri_flusso(percorso, 1, 2.0)
    try:
        assert primo.brano is secondo.brano
    finally:
        primo.close()
        secondo.close()
    assert not chip._CONDIVISI


def test_il_motore_suona_un_vgm(tmp_path):
    percorso = vgm_di_prova(tmp_path / "prova.vgm", 2)
    m = motore.Motore(ao="null")
    try:
        m.suona(percorso)
        fine = time.perf_counter() + 10
        while time.perf_counter() < fine and not (m.posizione or 0) > 0:
            time.sleep(0.01)
        assert (m.posizione or 0) > 0 and m.durata == pytest.approx(2 + chip.CODA, abs=0.05)
        assert m.sottobrano == 1 and isinstance(m._attivo.flusso.brano, chip.BranoChip)
    finally:
        m.chiudi()
