# MeTeOra, le prove dei moduli senza finestre: formati, Questo PC, suoni, impostazioni, songlengths.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import ctypes
import json
import os

import pytest

import formati
import questo_pc
import songlengths
import suoni
from finestra import durata_lunga, leggi_tempo, secondi_da_leggere, tempo
from impostazioni import PREDEFINITE, Impostazioni

HVSC = r"E:\C64Music"


def test_formati():
    assert formati.supportato("a.MP3")
    assert formati.e_sid("x.SID")
    assert not formati.supportato("nota.txt")
    assert "*.sid" in formati.filtro_dialogo()


def test_contenuto_filtra_e_ordina(tmp_path):
    (tmp_path / "b.mp3").write_bytes(b"")
    (tmp_path / "A.flac").write_bytes(b"")
    (tmp_path / "nota.txt").write_bytes(b"")
    (tmp_path / "Sotto").mkdir()
    (tmp_path / "Sotto" / "c.sid").write_bytes(b"")
    nascosto = tmp_path / "nascosto.mp3"
    nascosto.write_bytes(b"")
    ctypes.windll.kernel32.SetFileAttributesW(str(nascosto), 0x2)
    cartelle, files = questo_pc.contenuto(str(tmp_path))
    assert [os.path.basename(c) for c in cartelle] == ["Sotto"]
    assert [os.path.basename(f) for f in files] == ["A.flac", "b.mp3"]
    assert [os.path.basename(f) for f in questo_pc.file_ricorsivi(str(tmp_path))] == ["A.flac", "b.mp3", "c.sid"]


def test_unita_hanno_lettera_e_nome():
    elenco = questo_pc.unita()
    assert elenco
    for radice, etichetta in elenco:
        assert radice.endswith(":\\")
        assert etichetta.startswith(radice) and len(etichetta) > len(radice)


def test_ogni_evento_ha_un_preset_suo_che_esiste():
    from GBUtils import Acusticator

    preset = list(suoni.EVENTI.values())
    assert len(preset) == len(set(preset)), "due eventi con lo stesso suono"
    esistenti = set(Acusticator.list())
    mancanti = [p for p in preset if p not in esistenti]
    assert not mancanti, f"preset che non esistono nella collezione: {mancanti}"


def test_impostazioni_scartano_i_valori_sbagliati(tmp_path):
    percorso = tmp_path / "imp.json"
    percorso.write_text(json.dumps({"volume": "alto", "passo_avanti": 30, "volume_effetti": 1, "passo_volume": True}), encoding="utf-8")
    imp = Impostazioni(str(percorso))
    imp.carica()
    assert imp["volume"] == PREDEFINITE["volume"]
    assert imp["passo_avanti"] == 30
    assert imp["volume_effetti"] == 1.0
    assert imp["passo_volume"] == PREDEFINITE["passo_volume"]


def test_tempi():
    assert tempo(75) == "1:15"
    assert tempo(3725) == "1:02:05"
    assert tempo(None) == "?"
    assert secondi_da_leggere(10.0) == "10"
    assert durata_lunga(3723.456) == "1:02:03.456"
    assert durata_lunga(245) == "4:05"
    assert durata_lunga(7.25) == "0:07.250"
    assert secondi_da_leggere(1.25) == "1.25"
    assert leggi_tempo("1:30") == 90
    assert leggi_tempo("90") == 90
    assert leggi_tempo("1.2") == 1.2
    assert leggi_tempo("2,5") == 2.5
    assert leggi_tempo("1:30,25") == 90.25
    assert leggi_tempo("1:75") is None
    assert leggi_tempo("a") is None
    assert leggi_tempo("-5") is None


@pytest.mark.skipif(not os.path.isdir(HVSC), reason="serve la collezione HVSC")
def test_songlengths_della_collezione():
    sid = os.path.join(HVSC, r"MUSICIANS\T\Tel_Jeroen\Turbo_Outrun.sid")
    assert songlengths.durate_del_file(sid)[:2] == [475.0, 218.0]
    info = songlengths.leggi_intestazione(sid)
    assert info["titolo"] == "Turbo Outrun" and info["sottobrani"] == 12


MP3 = r"E:\Audio\AudioDescritti\Alla ricerca di Nemo.mp3"


@pytest.mark.skipif(not os.path.isfile(MP3), reason="serve un MP3 di prova")
def test_scheda_di_un_mp3():
    from schedario import leggi_scheda

    scheda = leggi_scheda(MP3)
    assert scheda["durata"] and scheda["durata"] > 60
    assert scheda["dim"] == os.path.getsize(MP3)


@pytest.mark.skipif(not os.path.isdir(HVSC), reason="serve la collezione HVSC")
def test_schedario_ricorda_e_rilegge(tmp_path):
    import shutil

    from playlist import Brano
    from schedario import Schedario

    sid = tmp_path / "t.sid"
    shutil.copy(os.path.join(HVSC, r"MUSICIANS\T\Tel_Jeroen\Turbo_Outrun.sid"), sid)
    archivio = str(tmp_path / "schede.json")
    s = Schedario(archivio)
    s.chiedi([str(sid)])
    s.aspetta()
    assert s.scheda(str(sid))["tag"]["autore"] == "Jeroen Tel"
    # Fuori dalla collezione il database delle durate non si trova.
    assert s.durata(Brano(str(sid))) is None
    s.salva()
    di_nuovo = Schedario(archivio)
    di_nuovo.carica()
    assert di_nuovo.scheda(str(sid))["sottobrani"] == 12
