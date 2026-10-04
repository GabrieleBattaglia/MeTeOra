# MeTeOra, le prove delle copie dei dati: una per sessione, le ultime tre, solo se cambiate.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.90.0.

import os

import copie

NOME = "MeTeOra - Playlist.json"


def _scrivi(cartella, testo):
    (cartella / NOME).write_text(testo, encoding="utf-8")


def _copie(cartella):
    return {p.name: p.read_text(encoding="utf-8") for p in (cartella / copie.CARTELLA).iterdir()}


def test_le_ultime_tre_versioni_diverse(tmp_path):
    assert copie.ruota(str(tmp_path), [NOME, "manca.json"]) == []
    assert not (tmp_path / copie.CARTELLA).exists()
    for versione in ("uno", "due", "due", "tre", "quattro"):
        _scrivi(tmp_path, versione)
        assert copie.ruota(str(tmp_path), [NOME]) == []
    # La versione uguale all'ultima copia non ruota: le tre piu' recenti, diverse.
    assert _copie(tmp_path) == {f"{NOME}.1": "quattro", f"{NOME}.2": "tre", f"{NOME}.3": "due"}
    # Il file vero non si tocca.
    assert (tmp_path / NOME).read_text(encoding="utf-8") == "quattro"


def test_meno_copie_tolgono_quella_in_piu(tmp_path):
    for versione in ("uno", "due", "tre"):
        _scrivi(tmp_path, versione)
        copie.ruota(str(tmp_path), [NOME])
    _scrivi(tmp_path, "quattro")
    copie.ruota(str(tmp_path), [NOME], quante=2)
    assert _copie(tmp_path) == {f"{NOME}.1": "quattro", f"{NOME}.2": "tre"}


def test_un_errore_del_disco_non_ferma_l_avvio(tmp_path, monkeypatch):
    _scrivi(tmp_path, "uno")

    def guasta(*_argomenti, **_chiavi):
        raise OSError("disco pieno")

    monkeypatch.setattr(copie.shutil, "copy2", guasta)
    assert copie.ruota(str(tmp_path), [NOME]) == [NOME]
    assert os.path.isfile(tmp_path / NOME)
