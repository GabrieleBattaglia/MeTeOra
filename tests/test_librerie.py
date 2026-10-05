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


def test_mpv_si_importa_con_il_path_ridotto_a_lib(monkeypatch):
    # 1.97.9: un mpv-2.dll di un altro programma, nel PATH, non vince sulla
    # libmpv-2.dll di lib; dopo, il PATH torna com'era.
    import builtins
    import os
    import sys

    visti = []
    vero_import = builtins.__import__

    def importa(nome, *argomenti, **opzioni):
        if nome == "mpv":
            visti.append(os.environ["PATH"])
            return object()
        return vero_import(nome, *argomenti, **opzioni)

    monkeypatch.delitem(sys.modules, "mpv", raising=False)
    monkeypatch.setattr(builtins, "__import__", importa)
    prima = os.environ["PATH"]
    librerie._importa_mpv(r"C:\cartella\lib")
    assert visti == [r"C:\cartella\lib"] and os.environ["PATH"] == prima


def test_da_compilato_le_librerie_mancanti_dicono_di_reinstallare(monkeypatch, tmp_path):
    # 1.97.9: nel pacchetto non c'e' prepara_ambiente.py.
    import sys

    monkeypatch.setattr(librerie.percorsi, "cartella_librerie", lambda: str(tmp_path))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    with pytest.raises(librerie.LibrerieMancanti, match="reinstalla MeTeOra") as errore:
        librerie.prepara()
    assert "prepara_ambiente" not in str(errore.value)


def test_vulkan_di_scorta_solo_se_windows_non_ce_l_ha(monkeypatch, tmp_path):
    # 1.99.0: la cartella lib/vulkan si aggiunge solo quando Windows non ha
    # vulkan-1.dll; chi ha i driver giusti usa la sua.
    import os

    (tmp_path / "libmpv-2.dll").write_bytes(b"")
    (tmp_path / "sidshim.dll").write_bytes(b"")
    (tmp_path / "vulkan").mkdir()
    (tmp_path / "vulkan" / "vulkan-1.dll").write_bytes(b"")
    aggiunte = []
    monkeypatch.setattr(librerie.percorsi, "cartella_librerie", lambda: str(tmp_path))
    monkeypatch.setattr(librerie.os, "add_dll_directory", lambda cartella: aggiunte.append(cartella))
    monkeypatch.setattr(librerie, "_carica", lambda _percorso: None)
    monkeypatch.setattr(librerie, "_importa_mpv", lambda _cartella: None)
    monkeypatch.setenv("PATH", os.environ["PATH"])
    monkeypatch.setattr(librerie, "_vulkan_presente", lambda: True)
    librerie.prepara()
    assert str(tmp_path / "vulkan") not in aggiunte
    monkeypatch.setattr(librerie, "_vulkan_presente", lambda: False)
    librerie.prepara()
    assert aggiunte[-1] == str(tmp_path / "vulkan")
