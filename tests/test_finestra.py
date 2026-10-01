# MeTeOra, le prove della finestra principale, sul desktop nascosto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import os
import re
import time

import pytest
import wx

import finestra as modulo
from playlist import Brano

HVSC = r"E:\C64Music"
TURBO_OUTRUN = os.path.join(HVSC, r"MUSICIANS\T\Tel_Jeroen\Turbo_Outrun.sid")


def _tasto(f, carattere=None, codice=None, maiuscolo=False):
    """Manda alla finestra un tasto come lo manderebbe Windows a EVT_CHAR_HOOK."""
    evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
    if carattere is not None:
        evento.SetUnicodeKey(ord(carattere.upper()))
        evento.SetKeyCode(ord(carattere.upper()))
    else:
        evento.SetKeyCode(codice)
    evento.SetShiftDown(maiuscolo)
    evento.SetEventObject(f)
    f._tasto(evento)


def _etichette(f, voce):
    return [f.albero.GetItemText(v) for v in f._figli(voce)]


def _senza_ora(riga):
    """Una riga della console senza l'ora che ha in fondo."""
    return re.sub(r" \d\d:\d\d$", "", riga)


def _ultima(f):
    return _senza_ora(f._righe[-1])


def test_aree_nell_ordine_di_tabulazione(finestra):
    focalizzabili = [c for c in finestra.albero.GetParent().GetChildren() if c.AcceptsFocus()]
    assert focalizzabili == [finestra.albero, finestra.console, finestra.cruscotto]
    assert [c.GetName() for c in focalizzabili] == ["Plancia dei comandi", "Console", "Cruscotto"]


def test_rami_principali(finestra):
    assert _etichette(finestra, finestra.albero.GetRootItem()) == ["Preferiti, brani: 0, totali: 0", "Playlist", "Questo PC", "Apri file", "Impostazioni"]
    assert _etichette(finestra, finestra.nodo_playlist) == ["Nuova playlist"]


def test_questo_pc_si_carica_all_espansione(finestra):
    assert not list(finestra._figli(finestra.nodo_pc))
    finestra.albero.Expand(finestra.nodo_pc)
    unita = _etichette(finestra, finestra.nodo_pc)
    assert unita and all(":\\" in u for u in unita)


def test_nuova_playlist_aggiungi_sposta_togli(finestra, suoni_annotati):
    finestra._comando_nuova_playlist()
    pl = finestra.archivio.playlist[0]
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "Playlist, brani: 0, totali: 0"
    finestra._aggiungi(pl, [r"C:\m\uno.mp3", r"C:\m\due.mp3", r"C:\m\tre.mp3"])
    assert _ultima(finestra) == "Aggiunti alla playlist Playlist: 3 brani, ora 3 brani."
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    # Il filtro non e' una voce della playlist: NVDA conta solo i brani.
    assert _etichette(finestra, nodo) == ["uno.mp3", "due.mp3", "tre.mp3"]
    finestra._sposta(pl, pl.brani[2], "cima")
    nodo = next(finestra._figli(finestra.nodo_playlist))
    assert _etichette(finestra, nodo) == ["tre.mp3", "uno.mp3", "due.mp3"]
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "tre.mp3"
    finestra._salta(pl, pl.brani[1])
    assert _etichette(finestra, nodo)[1] == "uno.mp3, saltato"
    finestra._togli(pl, pl.brani[0])
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "uno.mp3, saltato"
    assert os.path.isfile(finestra.archivio.percorso)
    assert "brano_tolto" in suoni_annotati


def test_tasti_futuri_e_numpad(finestra, suoni_annotati):
    _tasto(finestra, "a")
    assert "velocità" in _ultima(finestra)
    assert suoni_annotati[-1] == "non_disponibile"
    righe = len(finestra._righe)
    _tasto(finestra, codice=wx.WXK_NUMPAD_ADD)
    assert len(finestra._righe) == righe


def test_senza_niente_in_corso(finestra, suoni_annotati):
    _tasto(finestra, "c")
    assert _ultima(finestra) == "Non sta suonando niente."
    _tasto(finestra, "x")
    assert _ultima(finestra) == "I Preferiti sono vuoti: F4 ci mette il brano selezionato."
    finestra._seleziona(finestra.nodo_pc)
    _tasto(finestra, "x")
    assert _ultima(finestra).startswith("Niente da riprodurre")
    _tasto(finestra, "b")
    assert _ultima(finestra) == "Non c'è una playlist in riproduzione."


def test_volume_e_muto(finestra):
    finestra.motore.volume = 95
    _tasto(finestra, "+")
    assert _ultima(finestra) == "Volume 100."
    _tasto(finestra, "+")
    assert _ultima(finestra) == "Volume 105, amplificato oltre il 100."
    finestra.motore.volume = 298
    _tasto(finestra, "+")
    _tasto(finestra, "+")
    assert _ultima(finestra) == "Volume già al massimo, 300."
    _tasto(finestra, "m")
    assert _ultima(finestra) == "Muto."
    _tasto(finestra, "m")
    assert _ultima(finestra).startswith("Audio di nuovo acceso")
    assert finestra.impostazioni["volume"] == 300


def test_console_tiene_le_ultime_righe_e_il_cursore(finestra):
    # Le righe le dicono le impostazioni.
    assert finestra.impostazioni["righe_della_console"] == 2000
    finestra.impostazioni["righe_della_console"] = 150
    finestra.console.SetInsertionPoint(0)
    for i in range(400):
        finestra.scrivi(f"riga {i}")
    assert 150 <= len(finestra._righe) <= 250
    assert finestra._righe[-1].startswith("riga 399")
    testo = finestra.console.GetValue().replace("\r\n", "\n").replace("\r", "\n")
    assert testo.split("\n") == finestra._righe
    assert finestra.console.GetInsertionPoint() == 0


def test_cruscotto_secondo_il_contesto(finestra):
    finestra._area_precedente = "albero"
    finestra._seleziona(finestra.nodo_pc)
    assert finestra.righe_del_cruscotto()[0] == "Tasti per Questo PC."
    finestra._area_precedente = "console"
    assert finestra.righe_del_cruscotto()[0] == "Tasti per la console."
    assert len(finestra.righe_del_cruscotto()) >= 5


def _aspetta(condizione, secondi=5):
    fine = time.time() + secondi
    while time.time() < fine:
        wx.Yield()
        if condizione():
            return True
        time.sleep(0.05)
    return False


@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_riproduzione_di_una_cartella_e_selezione_ferma(finestra, suoni_annotati):
    cartella = os.path.dirname(TURBO_OUTRUN)
    finestra._seleziona(finestra.nodo_pc)
    finestra._suona_file(TURBO_OUTRUN, cartella)
    assert _ultima(finestra).startswith(f"In riproduzione: {TURBO_OUTRUN}, ")
    assert "Sottobrano 1 di 12." in _ultima(finestra)
    assert _aspetta(lambda: (finestra.motore.posizione or 0) > 0.2)
    selezione = finestra._voce_corrente()
    _tasto(finestra, "b")
    assert finestra._voce_corrente() == selezione
    assert suoni_annotati[-1] == "successivo"
    _tasto(finestra, "c")
    assert _ultima(finestra).startswith("Pausa a")
    _tasto(finestra, "x")
    assert _ultima(finestra).startswith("Riprende da")
    _tasto(finestra, "v")
    assert finestra.motore.in_corso is None
    finestra._brano_finito()


def test_esc_chiude_e_salva(finestra, suoni_annotati):
    finestra._comando_nuova_playlist()
    _tasto(finestra, codice=wx.WXK_ESCAPE)
    assert finestra._chiusa
    assert suoni_annotati[-1] == "uscita"
    assert os.path.isfile(finestra.impostazioni.percorso)


def test_cruscotto_ricorda_il_cursore(finestra):
    finestra._area_precedente = "console"
    finestra._rinfresca_cruscotto()
    finestra.cruscotto.SetInsertionPoint(20)
    finestra._rinfresca_cruscotto()
    assert finestra.cruscotto.GetInsertionPoint() == 20
    finestra._area_precedente = "albero"
    finestra._rinfresca_cruscotto()
    assert finestra.cruscotto.GetInsertionPoint() == 0
    # Il fuoco che se ne va e ritorna: il cursore torna dove era.
    finestra.cruscotto.SetInsertionPoint(30)
    finestra._cruscotto_lasciato(wx.FocusEvent(wx.wxEVT_KILL_FOCUS))
    finestra.cruscotto.SetInsertionPoint(0)
    finestra._fuoco_al_cruscotto(wx.FocusEvent(wx.wxEVT_SET_FOCUS))
    wx.Yield()
    assert finestra.cruscotto.GetInsertionPoint() == 30


def test_console_riscrive_la_riga_della_stessa_categoria(finestra):
    finestra.motore.volume = 50
    righe = len(finestra._righe)
    _tasto(finestra, "+")
    _tasto(finestra, "+")
    _tasto(finestra, "-")
    assert len(finestra._righe) == righe + 1
    assert _ultima(finestra) == "Volume 55."
    testo = finestra.console.GetValue().replace("\r\n", "\n").replace("\r", "\n")
    assert testo.split("\n") == finestra._righe
    finestra.scrivi("altro")
    _tasto(finestra, "+")
    assert [_senza_ora(r) for r in finestra._righe[-2:]] == ["altro", "Volume 60."]


def test_f9_e_f10(finestra, suoni_annotati):
    finestra._aggiungi(None, [os.path.join(r"C:\m", "uno.mp3")])
    finestra._seleziona(finestra.nodo_playlist)
    _tasto(finestra, codice=wx.WXK_F10)
    nodo = next(finestra._figli(finestra.nodo_playlist))
    assert finestra.albero.IsExpanded(nodo)
    assert _ultima(finestra).startswith("Aperto tutto dentro Playlist")
    finestra._seleziona(next(finestra._figli(nodo)))
    _tasto(finestra, codice=wx.WXK_F9)
    assert not finestra.albero.IsExpanded(nodo)
    assert finestra._voce_corrente() == nodo
    assert suoni_annotati[-1] == "chiudi_tutto"


def test_maiuscolo_c_toglie_il_loop(finestra):
    _tasto(finestra, "c", maiuscolo=True)
    assert _ultima(finestra) == "Non c'è un loop da togliere."
    finestra.coda.loop_playlist = finestra.archivio.preferiti
    _tasto(finestra, "c", maiuscolo=True)
    assert finestra.coda.loop_playlist is None


def _voce(f, radice, condizione):
    return next(v for v in f._tutte_le_voci(radice) if condizione(f._dati(v) or {}))


def _premi(f, carattere, maiuscolo=False):
    _tasto(f, carattere, maiuscolo=maiuscolo)
    return _ultima(f)


@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_sottobrani_nella_plancia(finestra, suoni_annotati, tmp_path):
    import shutil

    cartella = tmp_path / "sid"
    cartella.mkdir()
    shutil.copy(TURBO_OUTRUN, cartella)
    # Questo PC si carica prima: aprendosi dopo, cancellerebbe la cartella finta.
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "sid", data={"tipo": "cartella", "percorso": str(cartella), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra.albero.Expand(nodo)
    voce_file = next(finestra._figli(nodo))
    assert finestra.albero.ItemHasChildren(voce_file)
    finestra.albero.Expand(voce_file)
    sottobrani = _etichette(finestra, voce_file)
    assert len(sottobrani) == 12 and sottobrani[2] == "Sottobrano 3 di 12, 3:00"
    finestra._seleziona(list(finestra._figli(voce_file))[2])
    assert "Sottobrano 3 di 12." in _premi(finestra, "x")
    assert _etichette(finestra, voce_file)[2].endswith(", in riproduzione")
    # Con il SID aperto, B e Z passano da un sottobrano all'altro.
    assert _premi(finestra, "b").endswith("Sottobrano 4 di 12.")
    assert suoni_annotati[-1] == "successivo"
    _premi(finestra, "z")
    assert finestra.motore.sottobrano == 3
    finestra.motore.stop()
    brano = finestra._dati(voce_file)["brano"]
    finestra._aggiungi(None, [Brano(brano.percorso, sottobrano=5)])
    pl = finestra.archivio.playlist[0]
    nodo_pl = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo_pl)
    assert _etichette(finestra, nodo_pl) == ["Turbo_Outrun.sid, sottobrano 5 di 12"]
    assert not finestra.albero.ItemHasChildren(next(finestra._figli(nodo_pl)))
    assert pl.brani[0].sottobrano == 5


def test_loop_a_b_con_maiuscolo_x(finestra, suoni_annotati):
    finestra._aggiungi(None, [os.path.join(r"C:\m", f"{n}.mp3") for n in range(1, 6)])
    pl = finestra.archivio.playlist[0]
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)

    def scegli(n):
        finestra._seleziona(_voce(finestra, nodo, lambda d: d.get("brano") is pl.brani[n - 1]))

    scegli(2)
    assert _premi(finestra, "x", maiuscolo=True).startswith("Punto A del loop su 2.mp3.")
    scegli(4)
    assert _premi(finestra, "x", maiuscolo=True) == "Loop fra 2.mp3 e 4.mp3: 3 brani."
    assert _etichette(finestra, nodo)[1] == "2.mp3, punto A del loop"
    assert _etichette(finestra, nodo)[3] == "4.mp3, punto B del loop"
    scegli(5)
    assert "fuori dal loop" in _premi(finestra, "x")
    assert suoni_annotati[-1] == "fuori_dal_loop"
    scegli(4)
    assert _premi(finestra, "x", maiuscolo=True) == "Punto B tolto; resta il punto A su 2.mp3."
    scegli(2)
    assert _premi(finestra, "x", maiuscolo=True).startswith("Loop tolto")
    assert _etichette(finestra, nodo)[1] == "2.mp3"
    finestra._seleziona(finestra.nodo_pc)
    assert _premi(finestra, "x", maiuscolo=True).startswith("Il loop si mette su un brano")


def test_maiuscolo_canc_manda_nel_cestino(finestra, suoni_annotati, tmp_path, monkeypatch):
    import questo_pc

    cestinati = []
    monkeypatch.setattr(questo_pc, "nel_cestino", lambda p: cestinati.append(p) or True)
    risposte = [False, True, True]
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo: risposte.pop(0))
    for nome in ("a.mp3", "b.mp3"):
        (tmp_path / nome).write_bytes(b"")
    finestra._aggiungi(None, [str(tmp_path / "a.mp3"), str(tmp_path / "b.mp3")])
    pl = finestra.archivio.playlist[0]
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    primo = next(finestra._figli(nodo))
    finestra._al_cestino(primo)
    assert _ultima(finestra) == "Il file resta dov'è." and not cestinati
    finestra._al_cestino(next(finestra._figli(next(finestra._figli(finestra.nodo_playlist)))))
    assert cestinati == [str(tmp_path / "a.mp3")]
    assert [b.nome_del_file for b in pl.brani] == ["b.mp3"]
    assert _ultima(finestra) == "a.mp3 è nel cestino di Windows."
    finestra.albero.Expand(finestra.nodo_pc)
    cartella = finestra.albero.AppendItem(finestra.nodo_pc, "prova", data={"tipo": "cartella", "percorso": str(tmp_path), "caricato": False})
    finestra.albero.SetItemHasChildren(cartella, True)
    finestra.albero.Expand(cartella)
    assert _etichette(finestra, cartella) == ["a.mp3", "b.mp3"]
    finestra._al_cestino(next(finestra._figli(cartella)))
    assert _etichette(finestra, cartella) == ["b.mp3"]
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "b.mp3"
    assert suoni_annotati[-1] == "cestino"


def test_cartella_suona_con_le_sottocartelle_e_f8_la_ritrova(finestra, monkeypatch):
    import tempfile

    suonati = []

    def suona(percorso, sottobrano=None):
        suonati.append(percorso)
        finestra.motore._in_corso = percorso

    monkeypatch.setattr(finestra.motore, "suona", suona)
    # Una cartella visibile: le cartelle temporanee di Windows stanno sotto
    # AppData, che e' nascosta e in Questo PC non compare.
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) as radice:
        base = os.path.join(radice, "Musica")
        os.makedirs(os.path.join(base, "Dentro"))
        for percorso in (os.path.join(base, "uno.mp3"), os.path.join(base, "Dentro", "due.mp3")):
            open(percorso, "wb").close()
        finestra._riproduci_cartella(base)
        assert suonati == [os.path.join(base, "uno.mp3")]
        assert "1 di 2, cartella Musica" in _ultima(finestra)
        _tasto(finestra, "b")
        assert suonati[-1] == os.path.join(base, "Dentro", "due.mp3")
        finestra._vai_al_brano()
        selezione = finestra._voce_corrente()
        assert finestra.albero.GetItemText(selezione) == "due.mp3, in riproduzione"
        assert finestra._dati(finestra.albero.GetItemParent(selezione))["percorso"] == os.path.join(base, "Dentro")
        finestra.motore._in_corso = None


def test_preferiti(finestra, suoni_annotati):
    finestra._aggiungi(None, [os.path.join(r"C:\m", f"{n}.mp3") for n in range(1, 4)])
    pl = finestra.archivio.playlist[0]
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    finestra._seleziona(list(finestra._figli(nodo))[1])
    _tasto(finestra, codice=wx.WXK_F4)
    assert _ultima(finestra) == "2.mp3 è nei Preferiti, che ora hanno 1 brano."
    assert finestra.albero.GetItemText(finestra.nodo_preferiti) == "Preferiti, brani: 1 (senza durata), totali: 1 (senza durata)"
    _tasto(finestra, codice=wx.WXK_F4)
    assert _ultima(finestra) == "2.mp3 è già nei Preferiti."
    preferito = finestra.archivio.preferiti.brani[0]
    assert preferito is not pl.brani[1] and preferito.percorso == pl.brani[1].percorso
    finestra._cancella(finestra.nodo_preferiti)
    assert _ultima(finestra).startswith("I Preferiti non si eliminano")
    finestra.albero.Expand(finestra.nodo_preferiti)
    finestra._cancella(next(finestra._figli(finestra.nodo_preferiti)))
    assert not finestra.archivio.preferiti.brani
    assert finestra.albero.GetItemText(finestra.nodo_preferiti) == "Preferiti, brani: 0, totali: 0"
    finestra.archivio.preferiti.brani.append(preferito)
    finestra._salva_archivio()
    from playlist import Archivio

    di_nuovo = Archivio(finestra.archivio.percorso)
    di_nuovo.carica()
    assert [b.percorso for b in di_nuovo.preferiti.brani] == [preferito.percorso]


@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_durate_delle_playlist(finestra):
    finestra._aggiungi(None, [TURBO_OUTRUN, Brano(TURBO_OUTRUN, sottobrano=3)])
    finestra.schedario.aspetta()
    finestra._schede_arrivate()
    nodo = next(finestra._figli(finestra.nodo_playlist))
    assert finestra.albero.GetItemText(nodo) == "Playlist, brani: 2 (8:34), totali: 2 (8:34)"
    assert os.path.isfile(finestra.schedario.percorso)


def test_filtro_nella_plancia_e_nella_riproduzione(finestra, suoni_annotati, monkeypatch):
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("rock uno.mp3", "jazz due.mp3", "rock tre.mp3")])
    pl = finestra.archivio.playlist[0]
    risposte = iter(["rock|", "rock -tre"])

    class Finto:
        def __init__(self, *_a):
            self.testo = next(risposte)

        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

        def ShowModal(self):
            return wx.ID_OK

    monkeypatch.setattr(modulo, "FinestraFiltro", Finto)
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra._seleziona(nodo)
    finestra._modifica_filtro(pl)
    assert any(r.startswith("Nel filtro non capisco") for r in finestra._righe)
    assert _ultima(finestra) == "Filtro di Playlist: rock -tre. Passano 1 brano su 3."
    # Il filtro sta nell'etichetta della playlist, e il fuoco resta lì.
    nodo = next(finestra._figli(finestra.nodo_playlist))
    assert finestra._voce_corrente() == nodo
    assert finestra.albero.GetItemText(nodo) == "Playlist, brani: 1 (senza durata), totali: 3 (senza durata), filtro: rock -tre"
    finestra.albero.Expand(nodo)
    assert _etichette(finestra, nodo) == ["rock uno.mp3"]
    assert finestra.coda.primo(pl) is pl.brani[0]
    finestra.coda.imposta(pl, pl.brani[0])
    assert finestra.coda.successivo() is None
    # Il menu della playlist ha il filtro, e Togli il filtro quando c'è.
    voci = dict(finestra._voci_del_menu(finestra._dati(nodo)))
    assert list(voci) == ["Riproduci", "Filtro", "Togli il filtro", "Rinomina", "Elimina"]
    voci["Togli il filtro"]()
    assert _ultima(finestra).startswith("Filtro di Playlist svuotato")
    assert pl.filtro == ""
    assert [n for n, _a in finestra._voci_del_menu(finestra._dati(finestra.nodo_preferiti))] == ["Riproduci", "Filtro"]
    from playlist import Archivio

    finestra._imposta_filtro(pl, "jazz")
    di_nuovo = Archivio(finestra.archivio.percorso)
    di_nuovo.carica()
    assert di_nuovo.playlist[0].filtro == "jazz"


def test_campo_del_filtro_ctrl_invio_va_a_capo(finestra):
    dialogo = modulo.FinestraFiltro(finestra, "Filtro di Prova", "rock", modulo.ISTRUZIONI_DEL_FILTRO)
    try:
        evento = wx.KeyEvent(wx.wxEVT_KEY_DOWN)
        evento.SetKeyCode(wx.WXK_RETURN)
        evento.SetControlDown(True)
        # In cima le istruzioni come commenti; il testo di prima arriva
        # selezionato nell'ultima riga.
        valore = dialogo.campo.GetValue().replace(chr(13), "")
        assert valore.startswith("$ Puoi usare questi comandi per comporre il filtro.\n$ ")
        assert valore.endswith("\nrock")
        assert dialogo.campo.GetStringSelection() == "rock"
        dialogo.campo.SetInsertionPointEnd()
        dialogo._tasto(evento)
        assert dialogo.campo.GetValue().replace(chr(13), "").endswith("rock" + chr(10))
        # Le righe di commento non contano.
        assert dialogo.testo == "rock"
        assert dialogo.campo.GetName() == "Filtro di Prova"
    finally:
        dialogo.Destroy()
    dialogo = modulo.FinestraFiltro(finestra, "Ricerca", "", modulo.ISTRUZIONI_DELLA_RICERCA)
    try:
        # Senza testo di prima il cursore aspetta sull'ultima riga, vuota.
        assert dialogo.campo.GetValue().endswith(chr(10))
        assert dialogo.campo.GetInsertionPoint() == dialogo.campo.GetLastPosition()
        assert dialogo.testo == ""
        assert "per comporre la ricerca" in dialogo.campo.GetValue()
    finally:
        dialogo.Destroy()


def test_gli_esempi_delle_istruzioni_funzionano():
    """Ogni esempio delle istruzioni del filtro c'è davvero, e si capisce."""
    from filtro import Filtro

    istruzioni = " ".join(modulo.ISTRUZIONI_DEL_FILTRO)
    for esempio in ("rob hubbard", "hubbard|galway", "-remix", "comm*do", "vol#", '"last ninja"', "t<=3:00", "t>90", "d>5m", "d<700k",
            "y<1990", "r>1", "k=sid", "k=audio", "k=video", "k=tracker", "k=midi", "k=flac", "a=hubbard", "n=commando", "p=c64music", "s=1", "s=0"):
        assert esempio in istruzioni, esempio
        Filtro(esempio)


def test_durate_nella_plancia(finestra):
    percorso = os.path.join(r"C:\m", "lungo.mp3")
    finestra._aggiungi(None, [percorso])
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    assert _etichette(finestra, nodo)[0] == "lungo.mp3"
    finestra.schedario.schede[percorso] = {"dim": 1, "mod": 0, "durata": 125.5, "tag": {}, "sottobrani": None, "durate_sid": None}
    finestra._schede_arrivate()
    assert _etichette(finestra, nodo)[0] == "lungo.mp3, 2:05.500"


def _finto_motore(finestra, monkeypatch):
    suonati = []

    def suona(percorso, sottobrano=None):
        suonati.append((os.path.basename(percorso), sottobrano))
        finestra.motore._in_corso = percorso
        finestra.motore.sottobrano = sottobrano

    monkeypatch.setattr(finestra.motore, "suona", suona)
    return suonati


def test_avanzamento_segue_la_plancia(finestra, monkeypatch):
    suonati = _finto_motore(finestra, monkeypatch)
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("a.mp3", "b.mp3")])
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("c.mp3", "d.mp3")])
    prima, seconda = finestra.archivio.playlist
    # Si vede cio' che sta dentro rami tutti aperti, compreso il ramo Playlist.
    finestra.albero.Expand(finestra.nodo_playlist)
    nodi = list(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodi[0])
    finestra.albero.Expand(nodi[1])
    finestra._suona(prima, prima.brani[0])
    finestra._brano_finito()
    assert suonati[-1] == ("b.mp3", None)
    # Finita la prima playlist aperta, si entra nella seconda, aperta anche lei.
    finestra._brano_finito()
    assert suonati[-1] == ("c.mp3", None)
    assert finestra.coda.playlist is seconda
    finestra._brano_finito()
    finestra._brano_finito()
    assert suonati[-1] == ("d.mp3", None)
    assert _ultima(finestra) == "Fine: davanti non c'è altro da suonare."


def test_avanzamento_con_la_playlist_chiusa_segue_la_lista(finestra, monkeypatch):
    suonati = _finto_motore(finestra, monkeypatch)
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("a.mp3", "b.mp3")])
    finestra._aggiungi(None, [os.path.join(r"C:\m", "c.mp3")])
    prima = finestra.archivio.playlist[0]
    finestra._suona(prima, prima.brani[0])
    finestra._brano_finito()
    assert suonati[-1] == ("b.mp3", None)
    finestra._brano_finito()
    assert _ultima(finestra).startswith("Fine")


def test_avanzamento_con_la_playlist_aperta_si_ferma_dove_non_c_e_altro_di_aperto(finestra, monkeypatch):
    suonati = _finto_motore(finestra, monkeypatch)
    finestra._aggiungi(None, [os.path.join(r"C:\m", "a.mp3")])
    finestra._aggiungi(None, [os.path.join(r"C:\m", "c.mp3")])
    prima = finestra.archivio.playlist[0]
    finestra.albero.Expand(finestra.nodo_playlist)
    finestra.albero.Expand(next(finestra._figli(finestra.nodo_playlist)))
    finestra._suona(prima, prima.brani[0])
    finestra._brano_finito()
    # La seconda playlist e' chiusa: davanti non c'e' niente di aperto.
    assert suonati == [("a.mp3", None)]


@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_avanzamento_nei_sottobrani_aperti(finestra, monkeypatch, tmp_path):
    import shutil

    suonati = _finto_motore(finestra, monkeypatch)
    cartella = tmp_path / "sid"
    cartella.mkdir()
    shutil.copy(TURBO_OUTRUN, cartella)
    (cartella / "zeta.mp3").write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "sid", data={"tipo": "cartella", "percorso": str(cartella), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra.albero.Expand(nodo)
    voce_sid = next(finestra._figli(nodo))
    dati = finestra._dati(voce_sid)
    finestra.albero.Expand(voce_sid)
    finestra._suona(dati["playlist"], dati["brano"], sottobrano=11)
    finestra._brano_finito()
    assert suonati[-1] == ("Turbo_Outrun.sid", 12)
    finestra._brano_finito()
    assert suonati[-1] == ("zeta.mp3", None)
    # Con il SID chiuso, dal SID si passa subito al file dopo.
    finestra.albero.Collapse(voce_sid)
    finestra._suona(dati["playlist"], dati["brano"])
    finestra._brano_finito()
    assert suonati[-1] == ("zeta.mp3", None)


def test_maiuscolo_f8_aggancia_la_selezione(finestra, monkeypatch, suoni_annotati):
    _finto_motore(finestra, monkeypatch)
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("a.mp3", "b.mp3")])
    pl = finestra.archivio.playlist[0]
    finestra._seleziona(finestra.nodo_pc)
    _tasto(finestra, codice=wx.WXK_F8, maiuscolo=True)
    assert finestra.impostazioni["insegui"] is True
    assert suoni_annotati[-1] == "insegui_acceso"
    finestra._suona(pl, pl.brani[1])
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "b.mp3, in riproduzione"
    _tasto(finestra, codice=wx.WXK_F8, maiuscolo=True)
    assert finestra.impostazioni["insegui"] is False
    finestra._seleziona(finestra.nodo_pc)
    finestra._suona(pl, pl.brani[0])
    assert finestra._voce_corrente() == finestra.nodo_pc
    from impostazioni import Impostazioni

    salvate = Impostazioni(finestra.impostazioni.percorso)
    salvate.carica()
    assert salvate["insegui"] is False


def test_ricerca_globale(finestra, monkeypatch, suoni_annotati, tmp_path):
    from filtro import Filtro

    monkeypatch.setattr(modulo, "PAGINA_DEI_RISULTATI", 2)
    cartella = tmp_path / "Musica"
    (cartella / "Dentro").mkdir(parents=True)
    for nome in ("rock uno.mp3", "jazz.mp3", "rock due.mp3", "Dentro/rock tre.flac", "Dentro/rock quattro.mp3", "Dentro/rock cinque.mp3"):
        (cartella / nome).write_bytes(b"")
    finestra._aggiungi(None, [str(cartella / "rock uno.mp3"), os.path.join(r"C:\m", "rock in playlist.mp3")])
    finestra._avvia_ricerca("rock", Filtro("rock"), unita=[str(cartella)])
    finestra._ricerca.aspetta()
    finestra._risultati_arrivati()
    radice = finestra.albero.GetRootItem()
    assert _etichette(finestra, radice)[:2] == ["Preferiti, brani: 0, totali: 0", "Risultati di rock: 6 trovati"]
    assert _ultima(finestra) == "Ricerca di rock finita: 6 risultati."
    # I risultati stanno dove stavano: sotto la loro playlist, o lungo il percorso della cartella.
    finestra.albero.Expand(finestra.nodo_risultati)
    rami = _etichette(finestra, finestra.nodo_risultati)
    assert rami[0] == "Playlist Playlist, 2 risultati"
    assert rami[1].endswith(", 4 risultati") and len(rami) == 2
    playlist = next(finestra._figli(finestra.nodo_risultati))
    finestra.albero.Expand(playlist)
    assert _etichette(finestra, playlist) == ["rock uno.mp3", "rock in playlist.mp3"]
    # Fino a Dentro con i rami veri: tre risultati, due alla volta.
    def risultato(nome):
        return next(b for b in finestra.risultati.brani if b.nome_del_file == nome)

    cinque = risultato("rock cinque.mp3")
    gruppo = finestra._albero_dei_risultati.gruppo_del_brano[id(cinque)]
    assert [g.nome for g in finestra._albero_dei_risultati.catena(gruppo)][-2:] == ["Musica", "Dentro"]
    dentro = finestra.albero.GetItemParent(finestra._apri_fino_al_risultato(cinque))
    assert finestra.albero.GetItemText(dentro) == "Dentro, 3 risultati"
    assert _etichette(finestra, dentro) == ["rock cinque.mp3", "rock quattro.mp3", "Mostra l'ultimo risultato"]
    musica = finestra.albero.GetItemParent(dentro)
    assert _etichette(finestra, musica) == ["Dentro, 3 risultati", "rock due.mp3"]
    finestra._seleziona(list(finestra._figli(dentro))[-1])
    finestra._altri_risultati()
    assert _etichette(finestra, dentro) == ["rock cinque.mp3", "rock quattro.mp3", "rock tre.flac"]
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "rock tre.flac"
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("rock di dentro"))
    finestra._salva_risultati(finestra._dati(dentro)["gruppo"])
    assert finestra.archivio.playlist[-1].nome == "rock di dentro"
    assert len(finestra.archivio.playlist[-1].brani) == 3
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("tutti i rock"))
    finestra._salva_risultati()
    assert len(finestra.archivio.playlist[-1].brani) == 6
    # Una nuova ricerca sostituisce i Risultati.
    finestra._avvia_ricerca("jazz", Filtro("jazz"), unita=[str(cartella)])
    finestra._ricerca.aspetta()
    finestra._risultati_arrivati()
    assert finestra.albero.GetItemText(finestra.nodo_risultati) == "Risultati di jazz: 1 trovato"


class _DialogoFinto:
    """Un DialogoTesto, o un campo del filtro, che risponde da solo. Con piu'
    risposte le da' una per volta, ripetendo l'ultima."""

    def __init__(self, *risposte):
        self.risposte = list(risposte)
        self.risposta = self.risposte[0]

    @property
    def testo(self):
        return self.risposta

    def __call__(self, *_a, **_k):
        self.risposta = self.risposte.pop(0) if len(self.risposte) > 1 else self.risposte[0]
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def ShowModal(self):
        return wx.ID_OK

    def GetValue(self):
        return self.risposta


def test_z_b_n_seguono_la_plancia(finestra, monkeypatch):
    suonati = _finto_motore(finestra, monkeypatch)
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("a.mp3", "b.mp3")])
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("c.mp3", "d.mp3")])
    prima, seconda = finestra.archivio.playlist
    finestra.albero.Expand(finestra.nodo_playlist)
    for nodo in list(finestra._figli(finestra.nodo_playlist))[:2]:
        finestra.albero.Expand(nodo)
    finestra._suona(prima, prima.brani[1])
    _tasto(finestra, "b")
    assert suonati[-1] == ("c.mp3", None)
    _tasto(finestra, "z")
    assert suonati[-1] == ("b.mp3", None)
    _tasto(finestra, "z")
    _tasto(finestra, "z")
    assert _ultima(finestra) == "È il primo brano."
    finestra._comando_casuale(scelta=lambda candidati: candidati[-1])
    assert suonati[-1] == ("d.mp3", None)
    assert finestra.coda.playlist is seconda


def test_f12_scrive_i_tasti_dal_manuale(finestra, suoni_annotati):
    _tasto(finestra, codice=wx.WXK_F12)
    righe = modulo.sezione_del_manuale(finestra._leggi_risorsa("manuale.txt"), "I tasti")
    stampate = finestra._righe[-len(righe):]
    assert stampate[:-1] == righe[:-1] and _senza_ora(stampate[-1]) == righe[-1]
    assert re.search(r" \d\d:\d\d$", stampate[-1]) and not re.search(r" \d\d:\d\d$", stampate[0])
    assert righe[0] == "I tasti" and any(r.startswith("F12:") for r in righe)
    assert not any(r == "I SID" for r in righe)
    assert suoni_annotati[-1] == "elenco_dei_tasti"
    inizio = finestra._posizione_della_console
    testo = finestra.console.GetValue().replace("\r\n", "\n").replace("\r", "\n")
    assert testo[inizio:].startswith("I tasti")


def test_ogni_tasto_e_nel_manuale(finestra):
    """Ogni tasto a lettera e ogni tasto funzione ha la sua riga nella sezione I tasti."""
    righe = modulo.sezione_del_manuale(finestra._leggi_risorsa("manuale.txt"), "I tasti")
    testo = " ".join(righe)
    for tasto in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F12", "Esc", "Barra rovesciata", "Barra verticale", "Canc"):
        assert tasto in testo, tasto
    for (carattere, maiuscolo), _comando in modulo.TASTI.items():
        if carattere.isalpha():
            nome = f"Maiuscolo con {carattere.upper()}" if maiuscolo else carattere.upper()
            assert any(r.startswith(nome) or f" {nome} " in r or f"{nome}:" in r or f" e {carattere.upper()}" in r for r in righe), nome


def test_f12_porta_il_cursore_all_inizio_dell_elenco(finestra):
    finestra.scrivi("una riga qualsiasi")
    finestra.console.SetInsertionPoint(0)
    _tasto(finestra, codice=wx.WXK_F12)
    for _ in range(5):
        wx.Yield()
    inizio = finestra._posizione_della_console
    assert finestra.console.GetInsertionPoint() == inizio
    testo = finestra.console.GetValue().replace("\r\n", "\n").replace("\r", "\n")
    assert testo[inizio:].startswith("I tasti")


def test_f1_f2_f3_scrivono_nella_console(finestra):
    for codice, prima in ((wx.WXK_F1, "Manuale di MeTeOra"), (wx.WXK_F2, "Novità di MeTeOra"), (wx.WXK_F3, "Crediti di MeTeOra")):
        _tasto(finestra, codice=codice)
        for _ in range(5):
            wx.Yield()
        inizio = finestra._posizione_della_console
        testo = finestra.console.GetValue().replace("\r\n", "\n").replace("\r", "\n")
        assert testo[inizio:].startswith(prima)
        assert finestra.console.GetInsertionPoint() == inizio
    novita = modulo.righe_del_changelog(finestra._leggi_risorsa("CHANGELOG.md"))
    assert novita[0] == "Tutti i cambiamenti e le novità introdotte nelle versioni di MeTeOra."
    assert any(r.startswith("Versione 1.17.4 del 2026-09-30") for r in novita)
    assert not any(r.startswith(("#", "- ")) for r in novita)


def test_ricerca_nella_console(finestra, suoni_annotati, monkeypatch):
    finestra.scrivi("primo volume")
    finestra.scrivi("niente")
    finestra.scrivi("secondo VOLUME")
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoFinto("volume"))
    # La stessa barra rovesciata: con il fuoco nella console cerca li'.
    finestra.console.SetFocus()
    wx.Yield()
    _tasto(finestra, "\\")
    testo = "\n".join(finestra._righe).lower()
    primo = testo.find("volume")
    for _ in range(5):
        wx.Yield()
    assert finestra.console.GetInsertionPoint() == primo
    assert suoni_annotati[-1] == "trovato_in_console"
    invio = wx.KeyEvent(wx.wxEVT_KEY_DOWN)
    invio.SetKeyCode(wx.WXK_RETURN)
    finestra._tasto_nella_console(invio)
    secondo = testo.find("volume", primo + 1)
    assert finestra.console.GetInsertionPoint() == secondo
    finestra._tasto_nella_console(invio)
    assert finestra.console.GetInsertionPoint() == primo
    assert suoni_annotati[-1] == "ripartito_in_console"
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoFinto("inesistente"))
    finestra._comando_cerca_in_console()
    assert _ultima(finestra) == "Nella console non c'è inesistente."
    # Fra virgolette le maiuscole contano; le virgolette aperte si spiegano
    # e il campo si riapre.
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoFinto('"VOLUME', '"VOLUME"'))
    finestra._comando_cerca_in_console()
    assert any(r.startswith("Nella ricerca non capisco: Le virgolette non sono chiuse.") for r in finestra._righe)
    testo = "\n".join(finestra._righe)
    assert finestra.console.GetInsertionPoint() == testo.find("VOLUME")
    # Anche l'ora in fondo alle righe si trova, con il cancelletto per le cifre.
    ora = finestra._righe[0][-5:]
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoFinto(f"{ora[:3]}#"))
    finestra._comando_cerca_in_console()
    assert finestra.console.GetInsertionPoint() == testo.find(ora)


def test_conti_delle_cartelle(finestra, tmp_path):
    base = tmp_path / "Disco"
    for cartella in ("Barzellette/Vecchie", "Profonda/a/b", "Testi", "Vuota/Anche questa"):
        (base / cartella).mkdir(parents=True)
    for nome in ("Barzellette/una.mp3", "Barzellette/due.mp3", "Barzellette/Vecchie/tre.mp3", "Barzellette/nota.txt", "Profonda/a/b/giu.mp3", "Testi/nota.txt"):
        (base / nome).write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Disco", data={"tipo": "cartella", "percorso": str(base), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra.albero.Expand(nodo)
    # Prima dei conti si vedono tutte; il fuoco sta su una cartella vuota.
    assert _etichette(finestra, nodo) == ["Barzellette", "Profonda", "Testi", "Vuota"]
    finestra._seleziona(list(finestra._figli(nodo))[3])
    finestra.contatore.aspetta()
    finestra.schedario.aspetta()
    finestra._conti_arrivati()
    # Le cartelle senza niente da suonare, nemmeno sotto, spariscono; il
    # fuoco passa alla vicina che resta.
    assert _etichette(finestra, nodo) == ["Barzellette, 3 file", "Profonda, 1 file"]
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "Profonda, 1 file"
    # Riaprendo, quelle gia' contate non compaiono nemmeno.
    finestra.albero.Collapse(nodo)
    finestra.albero.DeleteChildren(nodo)
    finestra._dati(nodo)["caricato"] = False
    finestra.albero.Expand(nodo)
    assert _etichette(finestra, nodo) == ["Barzellette, 3 file", "Profonda, 1 file"]
    una = str(base / "Barzellette" / "una.mp3")
    finestra.schedario.schede[una] = {"dim": 1, "mod": 0, "durata": 61.5, "tag": {}, "sottobrani": None, "durate_sid": None}
    finestra._schede_arrivate()
    assert _etichette(finestra, nodo)[0] == "Barzellette, 3 file, 1:01.500 in tutto, 2 senza durata"


def test_j_k_e_cifre_aprono_e_suonano(finestra, monkeypatch):
    suonati = _finto_motore(finestra, monkeypatch)
    finestra._aggiungi(None, [os.path.join(r"C:\m", "a.mp3")])
    finestra.archivio.nuova("Vuota")
    finestra.archivio.nuova("Terza", [os.path.join(r"C:\m", "c.mp3")])
    finestra._popola_playlist()
    prima, vuota, _terza = finestra.archivio.playlist
    finestra._seleziona(finestra.nodo_pc)
    _tasto(finestra, "k")
    assert suonati[-1] == ("a.mp3", None)
    nodo = finestra._nodo_della_playlist(prima)
    assert finestra._voce_corrente() == nodo and finestra.albero.IsExpanded(nodo)
    _tasto(finestra, "k")
    assert _ultima(finestra) == f"La playlist {vuota.nome} non ha niente da suonare."
    assert finestra._voce_corrente() == finestra._nodo_della_playlist(vuota)
    _tasto(finestra, "k")
    assert suonati[-1] == ("c.mp3", None)
    _tasto(finestra, "k")
    assert _ultima(finestra) == "È l'ultima playlist."
    _tasto(finestra, "j")
    _tasto(finestra, "j")
    assert suonati[-1] == ("a.mp3", None)
    _tasto(finestra, "3")
    assert suonati[-1] == ("c.mp3", None)
    _tasto(finestra, "0")
    assert _ultima(finestra) == "Non c'è la playlist numero 10: ne hai 3."


def _wav(percorso, secondi=3):
    import wave

    with wave.open(str(percorso), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(8000)
        f.writeframes(b"\0\0" * 8000 * secondi)


def test_ripresa_all_avvio_in_pausa(app, tmp_path):
    from finestra import Finestra

    brano = tmp_path / "canzone.wav"
    _wav(brano, secondi=5)
    dati = tmp_path / "dati"
    dati.mkdir()
    prima = Finestra(ao="null", cartella_dati=str(dati))
    try:
        prima._aggiungi(None, [str(tmp_path / "altro.wav"), str(brano)])
        pl = prima.archivio.playlist[0]
        prima._suona(pl, pl.brani[1])
        # Un secondo pieno: la ripresa riparte dal punto salvato, e un margine
        # largo tiene la prova ferma anche sotto carico.
        assert _aspetta(lambda: (prima.motore.posizione or 0) > 1.0)
        prima.Close(force=True)
    finally:
        prima.Destroy()
    stato = prima.impostazioni["ripresa"]
    assert stato["tipo"] == "playlist" and stato["indice"] == 0 and stato["numero"] == 1 and stato["posizione"] > 1.0
    dopo = Finestra(ao="null", cartella_dati=str(dati))
    try:
        dopo.riprendi()
        assert dopo.coda.corrente is dopo.archivio.playlist[0].brani[1]
        assert dopo.motore.in_pausa
        assert _aspetta(lambda: (dopo.motore.posizione or 0) > 0.5)
        assert _ultima(dopo).startswith(f"Riprendo da dove eri: {brano}, in pausa a 0:0")
        assert dopo.albero.GetItemText(dopo._voce_corrente()) == "canzone.wav, 0:05, in riproduzione"
    finally:
        dopo.Close(force=True)
        dopo.Destroy()


def _playlist_di_prova(finestra, *gruppi):
    for nomi in gruppi:
        finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in nomi])
    finestra.albero.Expand(finestra.nodo_playlist)
    nodi = [finestra._nodo_della_playlist(pl) for pl in finestra.archivio.playlist]
    for nodo in nodi:
        finestra.albero.Expand(nodo)
    return nodi


def _voce_di(finestra, nodo, nome):
    return next(v for v in finestra._figli(nodo) if finestra.albero.GetItemText(v).startswith(nome))


def test_selezione_multipla_suona_come_playlist_invisibile(finestra, monkeypatch):
    suonati = _finto_motore(finestra, monkeypatch)
    rock, jazz = _playlist_di_prova(finestra, ("a.mp3", "b.mp3", "c.mp3"), ("x.mp3", "y.mp3"))
    finestra._seleziona(_voce_di(finestra, rock, "c.mp3"))
    # Un ramo selezionato vale per tutto cio' che contiene.
    finestra.albero.SelectItem(jazz)
    _tasto(finestra, "x")
    assert suonati[-1] == ("c.mp3", None)
    assert "1 di 3 della selezione" in _ultima(finestra)
    _tasto(finestra, "b")
    assert suonati[-1] == ("x.mp3", None)
    _tasto(finestra, "b")
    _tasto(finestra, "b")
    assert _ultima(finestra) == "È l'ultimo brano."
    finestra._brano_finito()
    assert _ultima(finestra).startswith("Fine")
    _tasto(finestra, "v")
    assert finestra.coda.playlist is None
    assert _ultima(finestra).startswith("Stop. La selezione suonata è chiusa")


def test_x_su_cio_che_suona_riparte_da_capo(finestra, monkeypatch, suoni_annotati):
    suonati = _finto_motore(finestra, monkeypatch)
    rock, = _playlist_di_prova(finestra, ("a.mp3", "b.mp3"))
    voce = _voce_di(finestra, rock, "a.mp3")
    finestra._seleziona(voce)
    _tasto(finestra, "x")
    _tasto(finestra, "x")
    assert suonati == [("a.mp3", None), ("a.mp3", None)]
    assert suoni_annotati[-1] == "da_capo"
    # In pausa, X riprende dal punto: e' cio' che usa la ripresa all'avvio.
    monkeypatch.setattr(type(finestra.motore), "in_pausa", property(lambda _self: True))
    monkeypatch.setattr(finestra.motore, "pausa", lambda valore=None: False)
    _tasto(finestra, "x")
    assert _ultima(finestra).startswith("Riprende da")


def test_canc_maiuscolo_canc_f4_e_crea_sulla_selezione(finestra, monkeypatch):
    import questo_pc

    rock, jazz, _terza = _playlist_di_prova(finestra, ("a.mp3", "b.mp3", "c.mp3"), ("x.mp3",), ("z.mp3",))
    pl_rock = finestra.archivio.playlist[0]
    finestra._seleziona(_voce_di(finestra, rock, "a.mp3"))
    finestra.albero.SelectItem(_voce_di(finestra, rock, "c.mp3"))
    finestra.albero.SelectItem(jazz)
    _tasto(finestra, codice=wx.WXK_F4)
    assert _ultima(finestra) == "Aggiunti ai Preferiti 3 brani."
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("mix"))
    finestra._crea_dalla_selezione()
    assert [b.nome_del_file for b in finestra.archivio.playlist[-1].brani] == ["a.mp3", "c.mp3", "x.mp3"]
    risposte = iter([True, True])
    monkeypatch.setattr(finestra, "_conferma", lambda *_a: next(risposte))
    rock = finestra._nodo_della_playlist(pl_rock)
    finestra.albero.Expand(rock)
    finestra._seleziona(_voce_di(finestra, rock, "a.mp3"))
    finestra.albero.SelectItem(_voce_di(finestra, rock, "b.mp3"))
    finestra.albero.SelectItem(finestra._nodo_della_playlist(finestra.archivio.playlist[2]))
    finestra._cancella_selezione()
    assert _ultima(finestra) == "Tolti 2 brani, eliminate 1 playlist."
    assert [b.nome_del_file for b in pl_rock.brani] == ["c.mp3"]
    # Il fuoco resta nella playlist su cui si lavorava, sulla voce che resta.
    voce = finestra._voce_corrente()
    assert finestra.albero.GetItemText(voce) == "c.mp3"
    assert finestra.albero.GetItemParent(voce) == finestra._nodo_della_playlist(pl_rock)
    assert finestra._voci_selezionate() == [voce]
    cestinati = []
    monkeypatch.setattr(questo_pc, "nel_cestino", lambda p: cestinati.append(os.path.basename(p)) or True)
    rock = finestra._nodo_della_playlist(pl_rock)
    finestra.albero.Expand(rock)
    finestra._seleziona(_voce_di(finestra, rock, "c.mp3"))
    finestra.albero.SelectItem(_voce_di(finestra, finestra._nodo_della_playlist(finestra.archivio.playlist[1]), "x.mp3"))
    finestra._cestina_selezione()
    assert sorted(cestinati) == ["c.mp3", "x.mp3"]
    assert _ultima(finestra) == "Nel cestino di Windows 2 file."
    assert not pl_rock.brani
    # La playlist e' rimasta vuota: il fuoco va su di lei.
    assert finestra._voce_corrente() == finestra._nodo_della_playlist(pl_rock)


def test_togli_con_il_filtro_resta_fra_i_brani_visibili(finestra):
    rock, = _playlist_di_prova(finestra, ("rock a.mp3", "jazz b.mp3", "rock c.mp3", "jazz d.mp3"))
    pl = finestra.archivio.playlist[0]
    finestra._seleziona(rock)
    finestra._imposta_filtro(pl, "rock")
    rock = finestra._nodo_della_playlist(pl)
    finestra.albero.Expand(rock)
    finestra._seleziona(_voce_di(finestra, rock, "rock c.mp3"))
    finestra._togli(pl, pl.brani[2])
    # Dopo c'e' solo jazz d.mp3, che il filtro nasconde: si torna su rock a.mp3.
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "rock a.mp3"
    finestra._togli(pl, pl.brani[0])
    assert finestra._voce_corrente() == finestra._nodo_della_playlist(pl)


def test_barra_verticale_apre_il_filtro_della_plancia_anche_dalla_console(finestra, monkeypatch, suoni_annotati):
    rock, = _playlist_di_prova(finestra, ("rock a.mp3", "jazz b.mp3"))
    pl = finestra.archivio.playlist[0]
    finestra._seleziona(_voce_di(finestra, rock, "jazz b.mp3"))
    finestra.console.SetFocus()
    wx.Yield()
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoFinto("rock"))
    _tasto(finestra, "|")
    assert pl.filtro == "rock"
    # Il brano col fuoco non passa piu' il filtro: il fuoco va sulla sua playlist.
    nodo = finestra._nodo_della_playlist(pl)
    assert finestra._voce_corrente() == nodo
    assert finestra.albero.GetItemText(nodo).endswith(", filtro: rock")
    # Maiuscolo con la barra rovesciata e' lo stesso tasto.
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoFinto(""))
    _tasto(finestra, "\\", maiuscolo=True)
    assert pl.filtro == "" and suoni_annotati[-1] == "filtro_tolto"
    finestra._seleziona(finestra.nodo_pc)
    _tasto(finestra, "|")
    assert _ultima(finestra).startswith("Il filtro c'è nelle playlist e nei Preferiti")


def test_problemi_interni_nella_console(finestra, monkeypatch, suoni_annotati):
    import sys
    import threading

    def problema():
        try:
            {}["chiave"]
        except KeyError as e:
            return type(e), e, e.__traceback__

    finestra._problema(*problema())
    riga = _ultima(finestra)
    assert riga.startswith("Problema interno: KeyError, 'chiave', in test_finestra.py alla riga ")
    assert riga.endswith(", problema.") and suoni_annotati[-1] == "problema"
    # Lo stesso problema di seguito riscrive la sua riga, senza suono.
    suoni_annotati.clear()
    finestra._problema(*problema())
    assert _ultima(finestra) == riga[:-1] + ", 2 volte." and not suoni_annotati
    # Agganciati i fili, un problema in un altro filo arriva nella console.
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(threading, "excepthook", lambda _argomenti: None)
    finestra.ascolta_i_problemi()
    filo = threading.Thread(target=lambda: 1 / 0)
    filo.start()
    filo.join()
    assert _aspetta(lambda: _ultima(finestra).startswith("Problema interno: ZeroDivisionError, division by zero"))


def test_ricerca_nella_console_jolly_emoji_e_non_trovato(finestra, monkeypatch):
    finestra.scrivi("In riproduzione: \U0001f3b5 Intro.mp3")
    finestra.scrivi("Volume 60.")
    finestra.scrivi("Volume 75.")
    invio = wx.KeyEvent(wx.wxEVT_KEY_DOWN)
    invio.SetKeyCode(wx.WXK_RETURN)
    testo = "\n".join(finestra._righe)
    finestra.console.SetFocus()
    wx.Yield()
    # Il cancelletto in fondo: Invio passa al numero seguente, non a un suo pezzo.
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoFinto("volume #"))
    finestra._comando_cerca_in_console()
    for _ in range(5):
        wx.Yield()
    primo = testo.find("Volume 60")
    # L'emoji vale due posizioni nel controllo: il cursore cade comunque sulla V.
    punto = finestra.console.GetInsertionPoint()
    assert finestra.console.GetRange(punto, punto + 6) == "Volume"
    assert finestra._dalla_console(punto) == primo
    finestra._tasto_nella_console(invio)
    assert finestra._dalla_console(finestra.console.GetInsertionPoint()) == testo.find("Volume 75")
    # Con il cancelletto in testa Invio salta da un numero all'altro, interi.
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoFinto("#."))
    finestra._comando_cerca_in_console()
    trovate = [finestra._occorrenza]
    for _ in range(3):
        finestra._tasto_nella_console(invio)
        trovate.append(finestra._occorrenza)
    assert trovate == [m.span() for m in re.finditer(r"\d+\.", testo)][:4]
    # La riga che dice che il testo non c'e' non viene ritrovata dopo.
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoFinto("inesistente"))
    finestra._comando_cerca_in_console()
    finestra._comando_cerca_in_console()
    assert sum(r.startswith("Nella console non c'è inesistente.") for r in finestra._righe) == 1
    # L'asterisco da solo si spiega e il campo si riapre.
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoFinto("*", ""))
    finestra._comando_cerca_in_console()
    assert any("l'asterisco da solo trova qualsiasi cosa" in r for r in finestra._righe)


def test_campo_del_filtro_riprende_il_testo_attaccato_a_un_commento(finestra):
    dialogo = modulo.FinestraFiltro(finestra, "Filtro di Prova", "", modulo.ISTRUZIONI_DEL_FILTRO)
    try:
        # Un Backspace di troppo: l'ultima riga finisce in coda all'ultima istruzione.
        valore = dialogo.campo.GetValue().replace(chr(13), "").rstrip(chr(10)) + "jazz"
        dialogo.campo.SetValue(valore)
        assert dialogo.testo == "jazz"
        dialogo.campo.SetValue(valore + "\n$ un mio commento\nrock")
        assert dialogo.testo == "jazz\nrock"
        # Le istruzioni restano righe intere, senza a capo automatici.
        assert dialogo.campo.HasFlag(wx.HSCROLL)
    finally:
        dialogo.Destroy()


def test_playlist_chiusa_si_ricarica_quando_la_si_riapre(finestra):
    nodo, = _playlist_di_prova(finestra, ("a.mp3", "b.mp3"))
    pl = finestra.archivio.playlist[0]
    finestra._seleziona(nodo)
    finestra._imposta_filtro(pl, "t<3:00")
    nodo = finestra._nodo_della_playlist(pl)
    finestra.albero.Expand(nodo)
    # Senza schede nessun brano passa, ma la playlist resta un ramo.
    assert not list(finestra._figli(nodo)) and finestra.albero.ItemHasChildren(nodo)
    for brano in pl.brani:
        finestra.schedario.schede[brano.percorso] = {"dim": 1, "mod": 0, "durata": 60.0, "tag": {}, "sottobrani": None, "durate_sid": None}
    finestra._schede_arrivate()
    finestra.albero.Collapse(nodo)
    finestra.albero.Expand(nodo)
    assert _etichette(finestra, nodo) == ["a.mp3, 1:00", "b.mp3, 1:00"]
    # Chiusa e riaperta, la playlist ricarica l'elenco con il filtro di adesso.
    pl.filtro = "a.mp3"
    finestra.albero.Collapse(nodo)
    finestra.albero.Expand(nodo)
    assert _etichette(finestra, nodo) == ["a.mp3, 1:00"]


def test_cartella_aperta_con_file_nuovi_non_sparisce(finestra, tmp_path):
    base = tmp_path / "Disco"
    (base / "Musica" / "Download").mkdir(parents=True)
    (base / "Musica" / "vecchio.mp3").write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Disco", data={"tipo": "cartella", "percorso": str(base), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra.albero.Expand(nodo)
    finestra.contatore.aspetta()
    finestra._conti_arrivati()
    # Il contatore ha letto Download vuota; poi ci arriva un file.
    (base / "Musica" / "Download" / "nuovo.mp3").write_bytes(b"")
    musica = next(finestra._figli(nodo))
    finestra.albero.Expand(musica)
    download = _voce(finestra, musica, lambda d: d.get("tipo") == "cartella")
    finestra.albero.Expand(download)
    finestra._seleziona(next(finestra._figli(download)))
    finestra.contatore.aspetta()
    finestra._conti_arrivati()
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "nuovo.mp3"
    assert finestra.albero.GetItemText(download).startswith("Download, 1 file")
    # Aggiorna su Questo PC rifa' tutti i conti.
    finestra.contatore.conti[str(base)] = []
    finestra._aggiorna_ramo(finestra.nodo_pc)
    assert str(base) not in finestra.contatore.conti


def test_cestino_nei_risultati_senza_doppioni(finestra, monkeypatch, tmp_path):
    import questo_pc
    from filtro import Filtro

    cartella = tmp_path / "Musica"
    cartella.mkdir()
    for nome in ("rock a.mp3", "rock b.mp3", "rock c.mp3", "rock d.mp3"):
        (cartella / nome).write_bytes(b"")
    finestra._avvia_ricerca("rock", Filtro("rock"), unita=[str(cartella)])
    finestra._ricerca.aspetta()
    finestra._risultati_arrivati()
    gruppo = finestra._albero_dei_risultati.radice
    while not gruppo.brani:
        gruppo = gruppo.elenco_dei_gruppi[0]
    voce = finestra._apri_fino_al_risultato(gruppo.brani[0])
    ramo = finestra.albero.GetItemParent(voce)
    finestra._seleziona(voce)
    finestra.albero.SelectItem(finestra.albero.GetNextSibling(voce))
    monkeypatch.setattr(questo_pc, "nel_cestino", lambda _p: True)
    monkeypatch.setattr(finestra, "_conferma", lambda *_a: True)
    finestra._cestina_selezione()
    finestra._aggiorna_risultati()
    assert [b.nome_del_file for b in finestra.risultati.brani] == ["rock c.mp3", "rock d.mp3"]
    assert _etichette(finestra, ramo) == ["rock c.mp3", "rock d.mp3"]
    assert finestra.albero.GetItemText(ramo).endswith(", 2 risultati")
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "rock c.mp3"


def test_stampa_intera_anche_con_poche_righe(finestra):
    finestra.impostazioni["righe_della_console"] = 100
    for i in range(200):
        finestra.scrivi(f"riga {i}")
    _tasto(finestra, codice=wx.WXK_F2)
    for _ in range(5):
        wx.Yield()
    inizio = finestra._posizione_della_console
    testo = finestra.console.GetValue().replace("\r\n", "\n").replace("\r", "\n")
    assert testo[inizio:].startswith("Novità di MeTeOra")


def test_problemi_riconosciuti_anche_nel_pacchetto():
    # Nel pacchetto di PyInstaller i passi hanno solo il nome del file.
    assert modulo._passo_nostro("finestra.py")
    assert not modulo._passo_nostro("random.py")
    avviso = ("Unhandled exception on python-mpv event loop: boom\nTraceback (most recent call last):\n"
        f'  File "{os.path.abspath(modulo.__file__)}", line 12, in _evento\nValueError: boom')
    assert modulo.riga_dell_avviso(avviso) == "Problema interno nel motore: Unhandled exception on python-mpv event loop: boom, in finestra.py alla riga 12, _evento."


@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_dopo_canc_il_fuoco_resta_sul_sottobrano(finestra, monkeypatch):
    finestra._aggiungi(None, [TURBO_OUTRUN, os.path.join(r"C:\m", "a.mp3"), os.path.join(r"C:\m", "b.mp3")])
    pl = finestra.archivio.playlist[0]
    nodo, = _playlist_di_prova(finestra)
    sid = _voce_di(finestra, nodo, "Turbo_Outrun.sid")
    finestra.albero.Expand(sid)
    finestra._seleziona(_voce_di(finestra, nodo, "a.mp3"))
    finestra.albero.SelectItem(_voce_di(finestra, nodo, "b.mp3"))
    # Con Ctrl e le frecce il fuoco va su un sottobrano, fuori dalla selezione.
    finestra.albero.SetFocusedItem(list(finestra._figli(sid))[3])
    finestra._cancella_selezione()
    assert [b.nome_del_file for b in pl.brani] == ["Turbo_Outrun.sid"]
    assert finestra.albero.GetItemText(finestra._voce_corrente()).startswith("Sottobrano 4 di 12")
