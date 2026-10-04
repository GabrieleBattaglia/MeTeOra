# MeTeOra, le prove dei dettagli dei contenitori e della cartella cambiata del contatore (1.77.0).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import ctypes
import os
import time

import dettagli
from contatore import Contatore


def _nascondi(percorso):
    # 2 e' FILE_ATTRIBUTE_HIDDEN.
    assert ctypes.windll.kernel32.SetFileAttributesW(str(percorso), 2)


def test_censisci(tmp_path):
    (tmp_path / "Rock" / "Live").mkdir(parents=True)
    (tmp_path / ".nascosta").mkdir()
    (tmp_path / "Rock" / "a.mp3").write_bytes(b"x" * 100)
    (tmp_path / "Rock" / "Live" / "b.flac").write_bytes(b"x" * 50)
    (tmp_path / "copertina.jpg").write_bytes(b"x" * 10)
    (tmp_path / ".nascosta" / "c.mp3").write_bytes(b"x" * 7)
    _nascondi(tmp_path / ".nascosta")
    vecchio = time.time() - 3600
    for nome in ("Rock/a.mp3", "Rock/Live/b.flac", ".nascosta/c.mp3"):
        os.utime(tmp_path / nome, (vecchio, vecchio))
    censimento = dettagli.censisci(str(tmp_path))
    # I file da suonare come li conta il contatore, senza la cartella nascosta;
    # tutti i file, nascosti compresi, come Esplora risorse.
    assert sorted(os.path.basename(p) for p in censimento["suonabili"]) == ["a.mp3", "b.flac"]
    assert (censimento["byte_suonabili"], censimento["file"], censimento["byte"]) == (150, 4, 167)
    assert (censimento["dirette"], censimento["sottocartelle"]) == (2, 3)
    # Il piu' recente fra i visibili: la copertina, non il file nascosto.
    assert os.path.basename(censimento["piu_recente"][1]) == "copertina.jpg"
    assert not censimento["interrotto"] and censimento["illeggibili"] == 0
    assert dettagli.censisci(str(tmp_path), fermo=lambda: True)["interrotto"]


def test_righe_della_cartella(tmp_path):
    (tmp_path / "Vuota" / "Dentro").mkdir(parents=True)
    vuota = str(tmp_path / "Vuota")
    righe = dettagli.righe_della_cartella(vuota, dettagli.censisci(vuota), lambda p: None, str)
    assert righe[:2] == [f"Cartella Vuota: {vuota}.", "È vuota: ha solo sottocartelle vuote."]
    (tmp_path / "Vuota" / "a.mp3").write_bytes(b"x" * 2048)
    (tmp_path / "Vuota" / "Dentro" / "b.sid").write_bytes(b"x" * 1024)
    durate = {"a.mp3": 90.0, "b.sid": 30.0}
    righe = dettagli.righe_della_cartella(vuota, dettagli.censisci(vuota), lambda p: durate[os.path.basename(p)], lambda s: f"{s:g} s")
    assert righe[1:5] == ["Da suonare: 2 file, sottocartelle comprese, 3.0 KB.", "Tipi: mp3 1, sid 1.", "Durata: 120 s.", "Il più lungo: a.mp3, 90 s."]
    assert "Il più corto: b.sid, 30 s." in righe and "Sottocartelle: 1 qui dentro, 1 in tutto." in righe
    assert any(r.startswith("Creata il ") for r in righe)


def test_parole_dei_dettagli():
    assert dettagli.dimensione(512) == "512 byte" and dettagli.dimensione(1536) == "1.5 KB"
    assert dettagli.per_tipo(["a.mp3", "b.MP3", "c.sid", "d"]) == "mp3 2, senza estensione 1, sid 1"
    assert dettagli.percentuale(1, 4) == "25.0%" and dettagli.percentuale(1, 0) == "0%"
    istante = time.mktime((2026, 10, 4, 9, 5, 0, 0, 0, -1))
    assert dettagli.quando(istante) == "4 ottobre 2026 alle 9:05"
    unita = {"radice": "E:\\", "tipo": "disco locale", "pronta": True, "nome": "Dati", "file_system": "NTFS", "totale": 4096, "libero": 1024, "occupato": 3072}
    assert dettagli.righe_dell_unita(unita) == ["Unità E:, Dati: disco locale, file system NTFS.", "Capacità: 4.0 KB.",
        "Spazio libero: 1.0 KB, 25.0% del totale.", "Spazio occupato: 3.0 KB, 75.0% del totale."]
    # Una data che Windows non converte non ferma i dettagli.
    assert dettagli.quando(4e10) == "una data non valida"


def test_la_cartella_cambiata_si_riconta(tmp_path):
    # Dopo il cestino: si rilegge la cartella, e si rifanno i conti suoi e di
    # chi la contiene, senza rileggere le sottocartelle.
    (tmp_path / "A" / "B").mkdir(parents=True)
    for nome in ("A/uno.mp3", "A/due.mp3", "A/B/tre.mp3"):
        (tmp_path / nome).write_bytes(b"")
    contatore = Contatore()
    radice, a, b = str(tmp_path), str(tmp_path / "A"), str(tmp_path / "A" / "B")
    contatore.chiedi([radice, a, b])
    contatore.aspetta()
    assert len(contatore.files(radice)) == 3
    (tmp_path / "A" / "due.mp3").unlink()
    assert sorted(contatore.cambiata(a)) == sorted([radice, a])
    assert contatore.files(b) is not None and contatore.files(a) is None
    contatore.chiedi([radice, a])
    contatore.aspetta()
    assert len(contatore.files(radice)) == 2 and len(contatore.files(a)) == 2


def test_una_cartella_che_non_si_legge_non_e_vuota(tmp_path):
    # Revisione 1.77.0: un percorso che non si legge non si dice vuoto.
    sparita = str(tmp_path / "sparita")
    censimento = dettagli.censisci(sparita)
    assert censimento["errore"] and not censimento["file"]
    righe = dettagli.righe_della_cartella(sparita, censimento, lambda p: None, str)
    assert len(righe) == 2 and righe[1].startswith("Non riesco a leggerla: ")


def test_censisci_brani(tmp_path):
    (tmp_path / "a.mp3").write_bytes(b"x" * 10)
    esito = dettagli.censisci_brani([str(tmp_path / "a.mp3"), str(tmp_path / "a.mp3"), str(tmp_path / "manca.mp3")])
    assert esito == {"byte": 10, "mancanti": [str(tmp_path / "manca.mp3")], "lontani": 0, "interrotto": False}
    assert dettagli.censisci_brani([str(tmp_path / "a.mp3")], fermo=lambda: True)["interrotto"]


def test_il_contatore_dimentica_senza_toccare_chi_sta_sopra(tmp_path):
    (tmp_path / "A" / "B").mkdir(parents=True)
    (tmp_path / "A" / "B" / "uno.mp3").write_bytes(b"")
    contatore = Contatore()
    radice, a, b = str(tmp_path), str(tmp_path / "A"), str(tmp_path / "A" / "B")
    contatore.chiedi([radice, a, b])
    contatore.aspetta()
    contatore.dimentica(b, anche_sopra=False)
    assert contatore.files(b) is None and contatore.files(a) is not None and contatore.files(radice) is not None
