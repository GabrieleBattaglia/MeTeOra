# MeTeOra, le prove del modello delle playlist.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# Nella 1.109.0 le prove di Ordina, Inverti l'ordine, Mescola e Ordine di prima.

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


# Ordina, Inverti l'ordine, Mescola e Ordine di prima (tappa 14 c).


def _scheda(durata=None, traccia=None, disco=None, **tag):
    scheda = {"dim": 1, "mod": 0, "durata": durata, "tag": tag, "sottobrani": None, "durate_sid": None}
    if traccia is not None:
        scheda["traccia"] = traccia
    if disco is not None:
        scheda["disco"] = disco
    return scheda


def _con_le_schede(*voci):
    """(playlist, scheda_di) da coppie (percorso o Brano, scheda o None)."""
    brani = [v if isinstance(v, Brano) else Brano(v) for v, _s in voci]
    schede = {id(b): s for b, (_v, s) in zip(brani, voci, strict=True)}
    return Playlist("Rock", brani), lambda b: schede[id(b)]


def _nomi(pl):
    return [b.percorso + (f" {b.sottobrano}" if b.sottobrano else "") for b in pl.brani]


def test_la_chiave_naturale_conta_i_numeri_e_ignora_maiuscole_e_accenti():
    from playlist import chiave_naturale

    assert sorted(["Traccia 10", "traccia 2", "Traccia 1"], key=chiave_naturale) == ["Traccia 1", "traccia 2", "Traccia 10"]
    assert chiave_naturale("Città")[0] == chiave_naturale("CITTA")[0]
    # Nessuna regola sugli articoli; fra 2 e 02 decide il testo, sempre allo stesso modo.
    assert sorted(["The Beatles", "Abba", "Queen"], key=chiave_naturale) == ["Abba", "Queen", "The Beatles"]
    assert sorted(["a 2", "a 02"], key=chiave_naturale) == sorted(["a 02", "a 2"], key=chiave_naturale)


def test_per_percorso_come_crea_playlist_da_qui():
    pl, scheda_di = _con_le_schede(*((p, None) for p in (r"C:\m\b\1.mp3", r"C:\m\a 10.mp3", r"E:\x.mp3", r"C:\m\a\x.mp3", r"C:\m\a 2.mp3")),
        (Brano(r"C:\m\Z.sid", sottobrano=3), None), (r"c:/m/z.sid", None), (Brano(r"C:\m\z.sid", sottobrano=2), None))
    assert pl.ordina("percorso", scheda_di) == (True, 0)
    # I file della cartella prima delle sottocartelle, i numeri per valore,
    # e i sottobrani dopo il loro file.
    assert _nomi(pl) == [r"C:\m\a 2.mp3", r"C:\m\a 10.mp3", r"c:/m/z.sid", r"C:\m\z.sid 2", r"C:\m\Z.sid 3", r"C:\m\a\x.mp3", r"C:\m\b\1.mp3", r"E:\x.mp3"]
    assert pl.ordina("percorso", scheda_di) == (False, 0)


def test_per_nome_del_file_poi_la_cartella():
    pl, scheda_di = _con_le_schede((r"C:\x\b.mp3", None), (r"C:\z\A.mp3", None), (r"C:\a\b.mp3", None), (r"C:\a\b 10.mp3", None), (r"C:\a\b 9.mp3", None))
    pl.ordina("nome", scheda_di)
    assert _nomi(pl) == [r"C:\z\A.mp3", r"C:\a\b 9.mp3", r"C:\a\b 10.mp3", r"C:\a\b.mp3", r"C:\x\b.mp3"]


def test_per_autore_con_gli_album_per_traccia_e_i_senza_autore_in_fondo():
    pl, scheda_di = _con_le_schede(
        (r"C:\m\senza.mp3", _scheda(titolo="Niente autore")),
        (r"C:\q\Hits\03.mp3", _scheda(autore="Queen", album="Greatest Hits", traccia=3)),
        (r"C:\a\Hits\b.mp3", _scheda(autore="abba", album="Greatest Hits", traccia=1, disco=2)),
        (r"C:\q\Hits\10.mp3", _scheda(autore="Queen", album="Greatest Hits", traccia=1)),
        (r"C:\a\Hits\a.mp3", _scheda(autore="ABBA", album="Greatest Hits", traccia=5, disco=1)),
        (r"C:\a\Hits\c.mp3", _scheda(autore="Abba", album="Greatest Hits", traccia=2, disco=1)),
        # Un album con una scheda vecchia, senza traccia, va per percorso.
        (r"C:\a\Arrival\2.mp3", _scheda(autore="Abba", album="Arrival", traccia=1)),
        (r"C:\a\Arrival\1.mp3", _scheda(autore="Abba", album="Arrival")),
        (r"C:\a\sciolto.mp3", _scheda(autore="Abba")),
        (r"C:\m\mai letto.mp3", None))
    assert pl.ordina("autore", scheda_di) == (True, 2)
    assert _nomi(pl) == [r"C:\a\Arrival\1.mp3", r"C:\a\Arrival\2.mp3", r"C:\a\Hits\c.mp3", r"C:\a\Hits\a.mp3", r"C:\a\Hits\b.mp3",
        r"C:\a\sciolto.mp3", r"C:\q\Hits\10.mp3", r"C:\q\Hits\03.mp3", r"C:\m\mai letto.mp3", r"C:\m\senza.mp3"]


def test_per_album_lo_stesso_nome_in_due_cartelle_sono_due_album():
    pl, scheda_di = _con_le_schede(
        (r"C:\q\Hits\x.mp3", _scheda(album="Greatest Hits", traccia=1)),
        (r"C:\a\Hits\y.mp3", _scheda(album="greatest hits", traccia=2)),
        (r"C:\a\Hits\z.mp3", _scheda(album="Greatest Hits", traccia=1)),
        (r"C:\m\nessuno.mp3", _scheda(autore="Abba")))
    assert pl.ordina("album", scheda_di) == (True, 1)
    assert _nomi(pl) == [r"C:\a\Hits\z.mp3", r"C:\a\Hits\y.mp3", r"C:\q\Hits\x.mp3", r"C:\m\nessuno.mp3"]


def test_per_titolo_non_usa_il_nome_del_file():
    pl, scheda_di = _con_le_schede((r"C:\m\a.mp3", _scheda()), (r"C:\m\z.mp3", _scheda(titolo="Brano 10", autore="B")),
        (r"C:\m\y.mp3", _scheda(titolo="brano 2")), (r"C:\m\x.mp3", _scheda(titolo="Brano 10", autore="A")))
    assert pl.ordina("titolo", scheda_di) == (True, 1)
    assert _nomi(pl) == [r"C:\m\y.mp3", r"C:\m\x.mp3", r"C:\m\z.mp3", r"C:\m\a.mp3"]


def test_il_segnaposto_della_hvsc_e_un_dato_che_manca():
    # <?> e' il titolo o l'autore che la HVSC non conosce: va in fondo con i
    # senza dato, e si conta con loro, come nelle statistiche, invece di
    # passare prima della A.
    sid = {"dim": 1, "mod": 0, "durata": None, "sottobrani": 1, "durate_sid": None}
    pl, scheda_di = _con_le_schede((r"C:\h\Zorro.sid", {**sid, "tag": {"titolo": "Zorro", "autore": "Rob Hubbard"}}),
        (r"C:\h\Anon.sid", {**sid, "tag": {"titolo": "<?>", "autore": " <?> "}}), (r"C:\h\Bdash.sid", {**sid, "tag": {"titolo": "Boulder Dash", "autore": "Peter Liepa"}}),
        (r"C:\h\Senza.sid", {**sid, "tag": {}}))
    assert pl.ordina("autore", scheda_di) == (True, 2)
    assert _nomi(pl) == [r"C:\h\Bdash.sid", r"C:\h\Zorro.sid", r"C:\h\Anon.sid", r"C:\h\Senza.sid"]
    assert pl.ordina("titolo", scheda_di) == (False, 2)
    # Anche dopo il criterio: l'autore <?> va dopo quelli che l'autore ce l'hanno.
    pl, scheda_di = _con_le_schede((r"C:\h\a.sid", {**sid, "tag": {"titolo": "Commando", "autore": "<?>"}}),
        (r"C:\h\b.sid", {**sid, "tag": {"titolo": "Commando", "autore": "Rob Hubbard"}}))
    assert pl.ordina("titolo", scheda_di) == (True, 0)
    assert _nomi(pl) == [r"C:\h\b.sid", r"C:\h\a.sid"]


def test_per_anno_dal_piu_vecchio():
    pl, scheda_di = _con_le_schede((r"C:\m\a.mp3", _scheda(anno=1999, autore="B")), (r"C:\m\b.mp3", _scheda(anno=1985)),
        (r"C:\m\c.mp3", _scheda(anno=1999, autore="A")), (r"C:\m\d.mp3", _scheda(anno="1970")))
    assert pl.ordina("anno", scheda_di) == (True, 1)
    assert _nomi(pl) == [r"C:\m\b.mp3", r"C:\m\c.mp3", r"C:\m\a.mp3", r"C:\m\d.mp3"]


def test_per_durata_come_la_mostra_la_plancia():
    sid = {"dim": 1, "mod": 0, "durata": 10.0, "tag": {}, "sottobrani": 3, "durate_sid": [10.0, 20.0, 30.0]}
    pl, scheda_di = _con_le_schede((r"C:\m\Lungo.sid", sid), (r"C:\m\canzone.mp3", _scheda(durata=30.5)), (Brano(r"C:\m\Lungo.sid", sottobrano=2), sid),
        (r"C:\m\ignota.mp3", _scheda()), (r"C:\m\Corto.sid", {**sid, "sottobrani": 1, "durate_sid": [5.0]}))
    assert pl.ordina("durata", scheda_di) == (True, 1)
    # Il SID con tre sottobrani vale il totale, il sottobrano a se' il suo.
    assert _nomi(pl) == [r"C:\m\Corto.sid", r"C:\m\Lungo.sid 2", r"C:\m\canzone.mp3", r"C:\m\Lungo.sid", r"C:\m\ignota.mp3"]


def test_l_ordine_e_stabile_e_tiene_saltati_e_doppioni():
    pl, scheda_di = _con_le_schede((r"C:\m\b.mp3", None), (r"C:\m\a.mp3", None), (r"C:\m\b.mp3", None))
    primo_b, a, secondo_b = pl.brani
    secondo_b.saltato = True
    pl.ordina("percorso", scheda_di)
    assert pl.brani == [a, primo_b, secondo_b] and secondo_b.saltato


def test_inverti_mescola_e_l_ordine_di_prima_con_gli_stessi_brani():
    pl = _pl(4)
    brani, lista = list(pl.brani), pl.brani
    assert pl.ordine_di_prima is None
    assert pl.inverti()
    assert pl.brani is lista and pl.brani == brani[::-1] and pl.ordine_di_prima == brani
    # Mescola: il brano in cima e gli altri mescolati, con il mescolamento dato.
    assert pl.mescola(lambda altri: altri.sort(key=lambda b: b.percorso), in_cima=brani[2])
    assert pl.brani == [brani[2], brani[0], brani[1], brani[3]] and pl.ordine_di_prima == brani[::-1]
    # Lo stesso ordine non cambia niente, nemmeno l'ordine di prima.
    assert not pl.mescola(lambda altri: altri.sort(key=lambda b: b.percorso), in_cima=brani[2])
    assert pl.ordine_di_prima == brani[::-1]
    # Un brano aggiunto dopo resta in fondo, uno tolto non torna.
    nuovo = Brano(r"C:\m\nuovo.mp3")
    pl.brani.append(nuovo)
    pl.togli(brani[0])
    assert pl.rimetti_l_ordine_di_prima()
    assert pl.brani is lista and pl.brani == [brani[3], brani[2], brani[1], nuovo]
    assert all(any(b is c for c in [*brani, nuovo]) for b in pl.brani)
    # Poi l'ordine di prima si dimentica.
    assert pl.ordine_di_prima is None and not pl.rimetti_l_ordine_di_prima()
    # L'ordine di prima non si salva.
    assert "ordine_di_prima" not in json.dumps(pl.come_dati())


def test_mescola_senza_in_cima_e_con_un_brano_che_non_c_e():
    from playlist import mescolati

    pl = _pl(3)
    assert mescolati(pl.brani, lambda altri: altri.reverse()) == pl.brani[::-1]
    assert mescolati(pl.brani, lambda altri: altri.reverse(), in_cima=Brano("x.mp3")) == pl.brani[::-1]
    assert mescolati(pl.brani, lambda altri: altri.reverse(), in_cima=pl.brani[1]) == [pl.brani[1], pl.brani[2], pl.brani[0]]
