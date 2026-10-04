# MeTeOra, le prove delle librerie native: la cartella lib e il caricamento di libmpv.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.85.1.

"""Il caricamento e' finto: le prove non toccano le DLL vere."""

import pytest

import librerie


def _carica_che_fallisce(percorso):
    raise OSError(f"[WinError 126] Impossibile trovare il modulo specificato: {percorso}")


def test_senza_vulkan_l_avvio_lo_dice(monkeypatch):
    monkeypatch.setattr(librerie, "_carica", _carica_che_fallisce)
    monkeypatch.setattr(librerie, "_vulkan_presente", lambda: False)
    with pytest.raises(librerie.LibrerieMancanti) as errore:
        librerie.prepara()
    testo = str(errore.value)
    assert testo.startswith("Manca vulkan-1.dll, la libreria di Vulkan che libmpv usa per il video")
    assert "driver della scheda video" in testo and "https://vulkan.lunarg.com" in testo


def test_un_altro_motivo_si_dice_com_e(monkeypatch):
    monkeypatch.setattr(librerie, "_carica", _carica_che_fallisce)
    monkeypatch.setattr(librerie, "_vulkan_presente", lambda: True)
    with pytest.raises(librerie.LibrerieMancanti, match=r"libmpv-2\.dll, nella cartella .*, non si carica: \[WinError 126\]"):
        librerie.prepara()


def test_con_libmpv_che_si_carica_va_tutto_bene(monkeypatch):
    caricate = []
    monkeypatch.setattr(librerie, "_carica", caricate.append)
    assert librerie.prepara() == librerie.LIB
    assert caricate and caricate[0].endswith("libmpv-2.dll")
