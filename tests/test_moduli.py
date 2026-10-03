# MeTeOra, le prove dei moduli senza finestre: formati, Questo PC, suoni, impostazioni, songlengths.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import ctypes
import json
import os
import re

import pytest

import formati
import questo_pc
import songlengths
import suoni
from finestra import durata_lunga, leggi_tempo, secondi_da_leggere, tempo
from impostazioni import PREDEFINITE, Impostazioni

HVSC = r"E:\C64Music"
# Il suona vero, preso all'import: nelle prove una fixture lo sostituisce.
_SUONA_VERO = suoni.suona


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


def test_ogni_evento_suona_diverso():
    from GBUtils import Acusticator

    # Due nomi diversi non bastano: anche onda, note e inviluppo devono
    # cambiare. I suoni nati per MeTeOra non sono mai a onda quadra.
    contenuti = {}
    for preset in suoni.EVENTI.values():
        score, kind, adsr = Acusticator.preset(preset)
        contenuti.setdefault(repr((kind, score, adsr)), []).append(preset)
        if preset.startswith("meteora_"):
            assert kind != 2, f"{preset} e' a onda quadra"
    uguali = [nomi for nomi in contenuti.values() if len(nomi) > 1]
    assert not uguali, f"preset che suonano uguali: {uguali}"


def test_suona_fissa_l_attesa_sulla_durata_del_preset(monkeypatch):
    from GBUtils import Acusticator

    # Il beep dei livelli aspetta il suono del comando: attesa() deve dire
    # quanto manca alla fine dell'ultimo preset suonato, letto dallo score.
    monkeypatch.setattr(Acusticator, "play", lambda *_a, **_k: True)
    monkeypatch.setattr(suoni, "_FINE_DELL_ULTIMO", [0.0])
    score, _kind, _adsr = Acusticator.preset(suoni.EVENTI["risali"])
    durata = sum(score[1::4])
    assert durata > 0
    _SUONA_VERO("risali")
    assert abs(suoni.attesa() - durata) < 0.05
    assert not _SUONA_VERO("risali", volume=0)
    assert abs(suoni.attesa() - durata) < 0.1


def test_ogni_preset_porta_la_firma_di_meteora():
    from GBUtils import Acusticator

    # Chi crea un suono lo firma nel nome, chi lo usa e basta nella descrizione:
    # cosi' Gabriele lo ritrova in Acu_Maker cercando meteora.
    firma = re.compile(r"Usato da: [^.]*\bmeteora\b")
    senza = [p for p in suoni.EVENTI.values() if not p.startswith("meteora_") and not firma.search(Acusticator.descrizione(p))]
    assert not senza, f"preset senza la firma di MeTeOra: {senza}"


def test_impostazioni_scartano_i_valori_sbagliati(tmp_path):
    percorso = tmp_path / "imp.json"
    percorso.write_text(json.dumps({"volume": "alto", "passo_avanti": 30, "volume_effetti": 1, "passo_volume": True}), encoding="utf-8")
    imp = Impostazioni(str(percorso))
    imp.carica()
    assert imp["volume"] == PREDEFINITE["volume"]
    assert imp["passo_avanti"] == 30
    assert imp["volume_effetti"] == 1.0
    assert imp["passo_volume"] == PREDEFINITE["passo_volume"]


def test_impostazioni_illeggibili_non_si_sovrascrivono(tmp_path):
    # Tappa 9: un file che non si legge resta com'e', e le impostazioni nuove
    # vanno accanto, con .nuovo, da cui si riparte la volta dopo.
    percorso = tmp_path / "imp.json"
    for contenuto in ("{rotto", "[1, 2]"):
        percorso.write_text(contenuto, encoding="utf-8")
        for nuovo in tmp_path.glob("*.nuovo"):
            nuovo.unlink()
        imp = Impostazioni(str(percorso))
        imp.carica()
        assert imp.errore and imp.percorso == str(percorso) + ".nuovo" and imp["volume"] == PREDEFINITE["volume"]
        imp["volume"] = 42
        imp.salva()
        assert percorso.read_text(encoding="utf-8") == contenuto
        assert not imp.da_nuovo
        di_nuovo = Impostazioni(str(percorso))
        di_nuovo.carica()
        assert di_nuovo["volume"] == 42 and di_nuovo.da_nuovo
    sano = Impostazioni(str(tmp_path / "sano.json"))
    sano.carica()
    assert sano.errore is None


def test_righe_della_console_dal_file(tmp_path):
    percorso = tmp_path / "imp.json"
    assert PREDEFINITE["righe_della_console"] == 2000
    for scritto, letto in ((5000, 5000), (50, 2000), ("tante", 2000), (True, 2000)):
        percorso.write_text(json.dumps({"righe_della_console": scritto}), encoding="utf-8")
        imp = Impostazioni(str(percorso))
        imp.carica()
        assert imp["righe_della_console"] == letto, scritto


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


def test_contatore_rinfresca_le_letture_vecchie(tmp_path):
    from contatore import Contatore

    (tmp_path / "Dentro").mkdir()
    contatore = Contatore()
    contatore.chiedi([str(tmp_path)])
    contatore.aspetta()
    assert contatore.files(str(tmp_path)) == []
    nuovo = str(tmp_path / "Dentro" / "nuovo.mp3")
    open(nuovo, "wb").close()
    # La lettura fresca di Dentro cambia: il conto di chi la contiene si rifa'.
    assert contatore.rinfresca(str(tmp_path / "Dentro"), questo_pc.contenuto(str(tmp_path / "Dentro"))) == [str(tmp_path)]
    contatore.chiedi([str(tmp_path)])
    contatore.aspetta()
    assert contatore.files(str(tmp_path)) == [nuovo]
    contatore.dimentica_tutto()
    assert contatore.files(str(tmp_path)) is None


def test_marcatori_nomi_tolleranza_e_salvataggio(tmp_path):
    import marcatori
    from marcatori import Marcatori

    archivio = Marcatori(str(tmp_path / "marcatori.json"))
    k = marcatori.chiave(r"C:\musica\Canzone.MP3", 200.1234)
    # Due copie identiche hanno la stessa chiave; senza durata conta il percorso.
    assert k == marcatori.chiave(r"D:\altrove\canzone.mp3", 200.1234) == "canzone.mp3|200.123"
    assert marcatori.chiave(r"C:\a\x.mod", None).startswith("percorso|")
    assert marcatori.chiave(r"C:\sid\Commando.sid", 250.0, 3).endswith("|3")
    primo = archivio.aggiungi(k, 10.0, r"C:\musica\Canzone.MP3", 200.1234)
    secondo = archivio.aggiungi(k, 5.0, r"C:\musica\Canzone.MP3", 200.1234)
    assert (primo["nome"], secondo["nome"]) == ("M1", "M2")
    assert [m["nome"] for m in archivio.elenco(k)] == ["M2", "M1"]
    assert archivio.trova(k, 10.004) is primo and archivio.trova(k, 10.006) is None
    assert archivio.precedente(k, 10.0)["nome"] == "M2" and archivio.precedente(k, 5.0) is None
    assert archivio.successivo(k, 5.0)["nome"] == "M1" and archivio.successivo(k, 10.0) is None
    archivio.rinomina(k, primo, "Ritornello")
    archivio.aggiungi(k, 20.0, r"D:\altrove\canzone.mp3", 200.1234)
    # Il nome automatico segue il numero piu' alto.
    assert archivio.elenco(k)[-1]["nome"] == "M3"
    archivio.salva()
    di_nuovo = Marcatori(archivio.percorso)
    di_nuovo.carica()
    assert [m["nome"] for m in di_nuovo.elenco(k)] == ["M2", "Ritornello", "M3"]
    assert di_nuovo.forse(r"E:\ovunque\CANZONE.mp3")
    assert di_nuovo.voci[k]["percorsi"] == [r"C:\musica\Canzone.MP3", r"D:\altrove\canzone.mp3"]
    assert di_nuovo.togli_prima(k, 10.0) == 1 and [m["nome"] for m in di_nuovo.elenco(k)] == ["Ritornello", "M3"]
    assert di_nuovo.togli_dopo(k, 10.0) == 1 and [m["nome"] for m in di_nuovo.elenco(k)] == ["Ritornello"]
    assert di_nuovo.togli_tutti(k) == 1 and k not in di_nuovo.voci
    assert di_nuovo.togli_tutti(k) == 0


def test_marcatori_file_illeggibile_e_tempi_vicini(tmp_path):
    from marcatori import Marcatori

    percorso = tmp_path / "marcatori.json"
    # Forme sbagliate: nessuna fa cadere il programma.
    for contenuto in ("[]", '{"marcatori": {"a|1.000": {"marker": [{"tempo": "1:30", "nome": "M1"}]}}}', "{troncato"):
        percorso.write_text(contenuto, encoding="utf-8")
        archivio = Marcatori(str(percorso))
        archivio.carica()
        assert archivio.errore and archivio.percorso.endswith(".nuovo") and not archivio.voci
    # I marker nuovi vanno nel .nuovo, e la volta dopo si ritrovano.
    archivio.aggiungi("a|1.000", 1.0, r"C:\a.mp3", 1.0)
    assert archivio.modificato
    archivio.salva()
    assert not archivio.modificato
    di_nuovo = Marcatori(str(percorso))
    di_nuovo.carica()
    assert di_nuovo.errore and [m["nome"] for m in di_nuovo.elenco("a|1.000")] == ["M1"]
    # Una voce senza percorsi, scritta a mano, si completa da sola.
    percorso.write_text('{"marcatori": {"b|2.000": {"marker": [{"tempo": 1, "nome": "X"}]}}}', encoding="utf-8")
    sano = Marcatori(str(percorso))
    sano.carica()
    assert not sano.errore
    sano.aggiungi("b|2.000", 1.5, r"C:\b.mp3", 2.0)
    # Due marker a 5,4 millesimi l'uno dall'altro restano due, e si raggiungono.
    sano.aggiungi("c|9.000", 1.0, r"C:\c.mp3", 9.0)
    secondo = sano.aggiungi("c|9.000", 1.0054, r"C:\c.mp3", 9.0)
    assert sano.successivo("c|9.000", 1.0) is secondo and sano.trova("c|9.000", 1.0054) is secondo
