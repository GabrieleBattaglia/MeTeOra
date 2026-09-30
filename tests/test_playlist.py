# MeTeOra, le prove del modello delle playlist.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import json

from playlist import Archivio, Brano, Coda, Playlist


def _pl(n=4, saltati=()):
    pl = Playlist.da_percorsi("prova", [f"C:\\m\\{i}.mp3" for i in range(n)])
    for i in saltati:
        pl.brani[i].saltato = True
    return pl


def test_successivo_e_precedente_saltano_i_brani_saltati():
    pl = _pl(5, saltati=(1, 3))
    coda = Coda()
    coda.imposta(pl, pl.brani[0])
    assert coda.successivo() is pl.brani[2]
    coda.imposta(pl, pl.brani[4])
    assert coda.precedente() is pl.brani[2]
    assert coda.successivo() is None


def test_la_coda_segue_il_brano_anche_se_la_playlist_cambia():
    pl = _pl(4)
    coda = Coda()
    coda.imposta(pl, pl.brani[1])
    pl.sposta(pl.brani[1], "fondo")
    assert coda.posizione() == (4, 4)
    assert coda.successivo() is None
    assert coda.precedente() is pl.brani[2]


def test_brano_corrente_tolto_riparte_dal_primo():
    pl = _pl(3)
    coda = Coda()
    tolto = pl.brani[1]
    coda.imposta(pl, tolto)
    pl.togli(tolto)
    assert coda.successivo() is pl.brani[0]
    assert coda.precedente() is None


def test_casuale_evita_il_corrente_e_i_saltati():
    pl = _pl(3, saltati=(2,))
    coda = Coda()
    coda.imposta(pl, pl.brani[0])
    assert coda.casuale(scelta=lambda c: c[0]) is pl.brani[1]
    assert coda.casuale(scelta=lambda c: c[-1]) is pl.brani[1]


def test_sposta_ai_limiti_non_muove():
    pl = _pl(3)
    primo = pl.brani[0]
    assert not pl.sposta(primo, "su")
    assert not pl.sposta(primo, "cima")
    assert pl.sposta(primo, "giu")
    assert pl.brani[1] is primo


def test_archivio_salva_e_ricarica(tmp_path):
    percorso = str(tmp_path / "pl.json")
    archivio = Archivio(percorso)
    pl = archivio.nuova("Rock", ["a.mp3", "b.flac"])
    pl.brani[1].saltato = True
    archivio.salva()
    dati = json.loads((tmp_path / "pl.json").read_text(encoding="utf-8"))
    assert dati["versione"] == 1
    di_nuovo = Archivio(percorso)
    di_nuovo.carica()
    assert [p.nome for p in di_nuovo.playlist] == ["Rock"]
    assert [(b.percorso, b.saltato) for b in di_nuovo.playlist[0].brani] == [("a.mp3", False), ("b.flac", True)]


def test_nomi_liberi():
    archivio = Archivio("x")
    assert archivio.nuova().nome == "Playlist"
    assert archivio.nuova().nome == "Playlist 2"
    assert archivio.nuova("playlist").nome == "playlist 3"


def test_nome_del_brano_senza_estensione():
    assert Brano(r"E:\C64Music\Turbo_Outrun.sid").nome == "Turbo_Outrun"


def test_temporanea():
    assert Playlist("x", cartella="C:\\").temporanea
    assert Playlist("x", cartella="").temporanea
    assert not Playlist("x").temporanea
