# MeTeOra, le prove del modello delle playlist.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import json
import os

from playlist import Archivio, Brano, Coda, Playlist


def _norm(p):
    # La forma concordata degli insiemi di percorsi spariti (1.104.0).
    return os.path.normcase(os.path.abspath(p))


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


def test_loop_gira_in_tondo_fra_a_e_b():
    pl = _pl(6, saltati=(3,))
    coda = Coda()
    coda.loop_playlist, coda.punto_a, coda.punto_b = pl, pl.brani[4], pl.brani[1]
    assert coda.intervallo(pl) == (1, 4)
    coda.imposta(pl, pl.brani[4])
    assert coda.successivo() is pl.brani[1]
    coda.imposta(pl, pl.brani[2])
    assert coda.successivo() is pl.brani[4]
    coda.imposta(pl, pl.brani[1])
    assert coda.precedente() is pl.brani[4]
    assert coda.primo(pl) is pl.brani[1]
    assert not coda.nel_loop(pl, pl.brani[5])
    assert coda.nel_loop(pl, pl.brani[2])
    assert coda.casuale(scelta=lambda c: c[0]) in pl.brani[1:5]
    assert coda.casuale(scelta=lambda c: c[-1]) in pl.brani[1:5]


def test_loop_senza_b_non_limita_e_vale_solo_sulla_sua_playlist():
    pl, altra = _pl(3), _pl(3)
    coda = Coda()
    coda.loop_playlist, coda.punto_a = pl, pl.brani[1]
    assert coda.intervallo(pl) is None
    coda.punto_b = pl.brani[2]
    assert coda.nel_loop(altra, altra.brani[0])
    coda.imposta(pl, pl.brani[0])
    assert coda.successivo() is pl.brani[1]


def test_sottobrano_si_salva():
    b = Brano.da_dati(Brano("x.sid", sottobrano=3).come_dati())
    assert b.sottobrano == 3
    assert "sottobrano" not in Brano("y.sid").come_dati()
    assert Brano.da_dati({"percorso": "z.sid", "sottobrano": "tre"}).sottobrano is None


def test_togli_i_percorsi_toglie_anche_doppioni_e_sottobrani():
    # La pulizia all'avvio, 1.104.0: lo stesso file scritto con altre
    # maiuscole o con le barre dritte, e tutti i sottobrani di un SID.
    pl = Playlist("prova", [Brano(r"C:\m\a.mp3"), Brano(r"C:\m\Z.sid", sottobrano=1), Brano(r"C:\M\A.MP3"), Brano(r"C:\m\b.mp3"), Brano("c:/m/z.sid", sottobrano=2)])
    brani, resta = pl.brani, pl.brani[3]
    tolti = pl.togli_i_percorsi({_norm(r"C:\m\a.mp3"), _norm(r"C:\m\Z.sid")})
    assert [(b.percorso, b.sottobrano) for b in tolti] == [(r"C:\m\a.mp3", None), (r"C:\m\Z.sid", 1), (r"C:\M\A.MP3", None), ("c:/m/z.sid", 2)]
    # La lista e' la stessa, cambiata sul posto.
    assert pl.brani is brani and pl.brani == [resta]
    assert pl.togli_i_percorsi({_norm(r"C:\m\x.mp3")}) == [] and pl.togli_i_percorsi(set()) == [] and pl.brani == [resta]


def test_l_archivio_toglie_i_file_spariti_e_tiene_le_playlist_vuote(tmp_path):
    percorso = str(tmp_path / "pl.json")
    archivio = Archivio(percorso)
    rock = archivio.nuova("Rock", [r"C:\m\a.mp3", r"C:\m\b.flac", r"C:\m\a.mp3"])
    vuota = archivio.nuova("Solo a", [r"c:\M\A.mp3"])
    archivio.preferiti.brani = [Brano(r"C:\m\a.mp3"), Brano(r"C:\m\c.ogg")]
    # I percorsi tornano cosi' come sono scritti, Preferiti compresi.
    assert archivio.percorsi() == {r"C:\m\a.mp3", r"C:\m\b.flac", r"c:\M\A.mp3", r"C:\m\c.ogg"}
    tolti = archivio.togli_i_percorsi({_norm(r"C:\m\a.mp3")})
    assert [(pl.nome, b.percorso) for pl, b in tolti] == [("Rock", r"C:\m\a.mp3"), ("Rock", r"C:\m\a.mp3"), ("Solo a", r"c:\M\A.mp3"), ("Preferiti", r"C:\m\a.mp3")]
    assert tolti[0][0] is rock and tolti[2][0] is vuota and tolti[3][0] is archivio.preferiti
    # La playlist rimasta vuota non si elimina.
    assert [pl.nome for pl in archivio.playlist] == ["Rock", "Solo a"] and vuota.brani == []
    assert archivio.togli_i_percorsi({_norm(r"C:\m\a.mp3")}) == []
    archivio.salva()
    di_nuovo = Archivio(percorso)
    di_nuovo.carica()
    assert [[b.percorso for b in pl.brani] for pl in di_nuovo.playlist] == [[r"C:\m\b.flac"], []]
    assert [b.percorso for b in di_nuovo.preferiti.brani] == [r"C:\m\c.ogg"] and di_nuovo.percorsi() == {r"C:\m\b.flac", r"C:\m\c.ogg"}
