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
    assert finestra.albero.GetItemText(finestra.albero.GetSelection()) == "Playlist, brani: 0, totali: 0"
    finestra._aggiungi(pl, [r"C:\m\uno.mp3", r"C:\m\due.mp3", r"C:\m\tre.mp3"])
    assert _ultima(finestra) == "Aggiunti alla playlist Playlist: 3 brani, ora 3 brani."
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    assert _etichette(finestra, nodo) == ["Filtro (Tutto)", "uno.mp3", "due.mp3", "tre.mp3"]
    finestra._sposta(pl, pl.brani[2], "cima")
    nodo = next(finestra._figli(finestra.nodo_playlist))
    assert _etichette(finestra, nodo) == ["Filtro (Tutto)", "tre.mp3", "uno.mp3", "due.mp3"]
    assert finestra.albero.GetItemText(finestra.albero.GetSelection()) == "tre.mp3"
    finestra._salta(pl, pl.brani[1])
    assert _etichette(finestra, nodo)[2] == "uno.mp3, saltato"
    finestra._togli(pl, pl.brani[0])
    assert finestra.albero.GetItemText(finestra.albero.GetSelection()) == "uno.mp3, saltato"
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
    finestra.albero.SelectItem(finestra.nodo_pc)
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
    finestra.console.SetInsertionPoint(0)
    for i in range(modulo.RIGHE_DELLA_CONSOLE + 150):
        finestra.scrivi(f"riga {i}")
    assert len(finestra._righe) <= modulo.RIGHE_DELLA_CONSOLE + 100
    testo = finestra.console.GetValue().replace("\r\n", "\n").replace("\r", "\n")
    assert testo.split("\n") == finestra._righe
    assert finestra.console.GetInsertionPoint() == 0


def test_cruscotto_secondo_il_contesto(finestra):
    finestra._area_precedente = "albero"
    finestra.albero.SelectItem(finestra.nodo_pc)
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
    finestra.albero.SelectItem(finestra.nodo_pc)
    finestra._suona_file(TURBO_OUTRUN, cartella)
    assert _ultima(finestra).startswith(f"In riproduzione: {TURBO_OUTRUN}, ")
    assert "Sottobrano 1 di 12." in _ultima(finestra)
    assert _aspetta(lambda: (finestra.motore.posizione or 0) > 0.2)
    selezione = finestra.albero.GetSelection()
    _tasto(finestra, "b")
    assert finestra.albero.GetSelection() == selezione
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
    finestra.albero.SelectItem(finestra.nodo_playlist)
    _tasto(finestra, codice=wx.WXK_F10)
    nodo = next(finestra._figli(finestra.nodo_playlist))
    assert finestra.albero.IsExpanded(nodo)
    assert _ultima(finestra).startswith("Aperto tutto dentro Playlist")
    finestra.albero.SelectItem(list(finestra._figli(nodo))[1])
    _tasto(finestra, codice=wx.WXK_F9)
    assert not finestra.albero.IsExpanded(nodo)
    assert finestra.albero.GetSelection() == nodo
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
    finestra.albero.SelectItem(list(finestra._figli(voce_file))[2])
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
    assert _etichette(finestra, nodo_pl) == ["Filtro (Tutto)", "Turbo_Outrun.sid, sottobrano 5 di 12"]
    assert not finestra.albero.ItemHasChildren(list(finestra._figli(nodo_pl))[1])
    assert pl.brani[0].sottobrano == 5


def test_loop_a_b_con_maiuscolo_x(finestra, suoni_annotati):
    finestra._aggiungi(None, [os.path.join(r"C:\m", f"{n}.mp3") for n in range(1, 6)])
    pl = finestra.archivio.playlist[0]
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)

    def scegli(n):
        finestra.albero.SelectItem(_voce(finestra, nodo, lambda d: d.get("brano") is pl.brani[n - 1]))

    scegli(2)
    assert _premi(finestra, "x", maiuscolo=True).startswith("Punto A del loop su 2.mp3.")
    scegli(4)
    assert _premi(finestra, "x", maiuscolo=True) == "Loop fra 2.mp3 e 4.mp3: 3 brani."
    assert _etichette(finestra, nodo)[2] == "2.mp3, punto A del loop"
    assert _etichette(finestra, nodo)[4] == "4.mp3, punto B del loop"
    scegli(5)
    assert "fuori dal loop" in _premi(finestra, "x")
    assert suoni_annotati[-1] == "fuori_dal_loop"
    scegli(4)
    assert _premi(finestra, "x", maiuscolo=True) == "Punto B tolto; resta il punto A su 2.mp3."
    scegli(2)
    assert _premi(finestra, "x", maiuscolo=True).startswith("Loop tolto")
    assert _etichette(finestra, nodo)[2] == "2.mp3"
    finestra.albero.SelectItem(finestra.nodo_pc)
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
    primo = list(finestra._figli(nodo))[1]
    finestra._al_cestino(primo)
    assert _ultima(finestra) == "Il file resta dov'è." and not cestinati
    finestra._al_cestino(list(finestra._figli(next(finestra._figli(finestra.nodo_playlist))))[1])
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
    assert finestra.albero.GetItemText(finestra.albero.GetSelection()) == "b.mp3"
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
        selezione = finestra.albero.GetSelection()
        assert finestra.albero.GetItemText(selezione) == "due.mp3, in riproduzione"
        assert finestra._dati(finestra.albero.GetItemParent(selezione))["percorso"] == os.path.join(base, "Dentro")
        finestra.motore._in_corso = None


def test_preferiti(finestra, suoni_annotati):
    finestra._aggiungi(None, [os.path.join(r"C:\m", f"{n}.mp3") for n in range(1, 4)])
    pl = finestra.archivio.playlist[0]
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    finestra.albero.SelectItem(list(finestra._figli(nodo))[2])
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
    finestra._cancella(list(finestra._figli(finestra.nodo_preferiti))[1])
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
    finestra._modifica_filtro(pl)
    assert any(r.startswith("Nel filtro non capisco") for r in finestra._righe)
    assert _ultima(finestra) == "Filtro di Playlist: rock -tre. Passano 1 brano su 3."
    nodo = next(finestra._figli(finestra.nodo_playlist))
    assert _etichette(finestra, nodo) == ["Filtro: rock -tre", "rock uno.mp3"]
    assert finestra.albero.GetItemText(finestra.albero.GetSelection()) == "Filtro: rock -tre"
    assert finestra.albero.GetItemText(nodo).startswith("Playlist, brani: 1 (senza durata), totali: 3")
    assert finestra.coda.primo(pl) is pl.brani[0]
    finestra.coda.imposta(pl, pl.brani[0])
    assert finestra.coda.successivo() is None
    finestra._cancella(finestra.albero.GetSelection())
    assert _ultima(finestra).startswith("Filtro di Playlist svuotato")
    assert pl.filtro == ""
    from playlist import Archivio

    finestra._imposta_filtro(pl, "jazz")
    di_nuovo = Archivio(finestra.archivio.percorso)
    di_nuovo.carica()
    assert di_nuovo.playlist[0].filtro == "jazz"


def test_campo_del_filtro_ctrl_invio_va_a_capo(finestra):
    dialogo = modulo.FinestraFiltro(finestra, "Prova", "rock")
    try:
        evento = wx.KeyEvent(wx.wxEVT_KEY_DOWN)
        evento.SetKeyCode(wx.WXK_RETURN)
        evento.SetControlDown(True)
        # Il testo di prima arriva selezionato: si va in fondo prima di andare a capo.
        assert dialogo.campo.GetStringSelection() == "rock"
        dialogo.campo.SetInsertionPointEnd()
        dialogo._tasto(evento)
        assert dialogo.testo.replace(chr(13), "") == "rock" + chr(10)
        assert dialogo.campo.GetName() == "Filtro di Prova"
    finally:
        dialogo.Destroy()


def test_durate_nella_plancia(finestra):
    percorso = os.path.join(r"C:\m", "lungo.mp3")
    finestra._aggiungi(None, [percorso])
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    assert _etichette(finestra, nodo)[1] == "lungo.mp3"
    finestra.schedario.schede[percorso] = {"dim": 1, "mod": 0, "durata": 125.5, "tag": {}, "sottobrani": None, "durate_sid": None}
    finestra._schede_arrivate()
    assert _etichette(finestra, nodo)[1] == "lungo.mp3, 2:05.500"


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
    finestra.albero.SelectItem(finestra.nodo_pc)
    _tasto(finestra, codice=wx.WXK_F8, maiuscolo=True)
    assert finestra.impostazioni["insegui"] is True
    assert suoni_annotati[-1] == "insegui_acceso"
    finestra._suona(pl, pl.brani[1])
    assert finestra.albero.GetItemText(finestra.albero.GetSelection()) == "b.mp3, in riproduzione"
    _tasto(finestra, codice=wx.WXK_F8, maiuscolo=True)
    assert finestra.impostazioni["insegui"] is False
    finestra.albero.SelectItem(finestra.nodo_pc)
    finestra._suona(pl, pl.brani[0])
    assert finestra.albero.GetSelection() == finestra.nodo_pc
    from impostazioni import Impostazioni

    salvate = Impostazioni(finestra.impostazioni.percorso)
    salvate.carica()
    assert salvate["insegui"] is False


def test_ricerca_globale(finestra, monkeypatch, suoni_annotati, tmp_path):
    from filtro import Filtro

    monkeypatch.setattr(modulo, "PAGINA_DEI_RISULTATI", 2)
    cartella = tmp_path / "Musica"
    (cartella / "Dentro").mkdir(parents=True)
    for nome in ("rock uno.mp3", "jazz.mp3", "rock due.mp3", "Dentro/rock tre.flac", "Dentro/rock quattro.mp3"):
        (cartella / nome).write_bytes(b"")
    finestra._aggiungi(None, [str(cartella / "rock uno.mp3"), os.path.join(r"C:\m", "rock in playlist.mp3")])
    finestra._avvia_ricerca("rock", Filtro("rock"), unita=[str(cartella)])
    finestra._ricerca.aspetta()
    finestra._risultati_arrivati()
    radice = finestra.albero.GetRootItem()
    assert _etichette(finestra, radice)[:2] == ["Preferiti, brani: 0, totali: 0", "Risultati di rock: 5 trovati"]
    assert _ultima(finestra) == "Ricerca di rock finita: 5 risultati."
    # Prima quelli delle playlist, senza doppioni con quelli del disco.
    percorsi = [b.percorso for b in finestra.risultati.brani]
    assert percorsi[:2] == [str(cartella / "rock uno.mp3"), os.path.join(r"C:\m", "rock in playlist.mp3")]
    assert len(set(percorsi)) == 5
    finestra.albero.Expand(finestra.nodo_risultati)
    etichette = _etichette(finestra, finestra.nodo_risultati)
    assert etichette == [str(cartella / "rock uno.mp3"), os.path.join(r"C:\m", "rock in playlist.mp3"), "Mostra altri 2 risultati, ne restano 3"]
    altri = list(finestra._figli(finestra.nodo_risultati))[-1]
    finestra.albero.SelectItem(altri)
    finestra._altri_risultati()
    assert len(_etichette(finestra, finestra.nodo_risultati)) == 5
    assert _etichette(finestra, finestra.nodo_risultati)[-1] == "Mostra l'ultimo risultato"
    assert finestra.albero.GetSelection() == list(finestra._figli(finestra.nodo_risultati))[2]
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("rock salvati"))
    finestra._salva_risultati()
    assert finestra.archivio.playlist[-1].nome == "rock salvati"
    assert len(finestra.archivio.playlist[-1].brani) == 5
    # Una nuova ricerca sostituisce i Risultati.
    finestra._avvia_ricerca("jazz", Filtro("jazz"), unita=[str(cartella)])
    finestra._ricerca.aspetta()
    finestra._risultati_arrivati()
    assert finestra.albero.GetItemText(finestra.nodo_risultati) == "Risultati di jazz: 1 trovato"


class _DialogoFinto:
    def __init__(self, risposta):
        self.risposta = risposta

    def __call__(self, *_a, **_k):
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
    for tasto in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F12", "Esc", "Barra rovesciata", "Canc"):
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
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("volume"))
    _tasto(finestra, "\\", maiuscolo=True)
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
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("inesistente"))
    finestra._comando_cerca_in_console()
    assert _ultima(finestra) == "Nella console non c'è inesistente."


def test_conti_delle_cartelle(finestra, tmp_path):
    base = tmp_path / "Disco"
    (base / "Barzellette" / "Vecchie").mkdir(parents=True)
    (base / "Vuota").mkdir()
    for nome in ("Barzellette/una.mp3", "Barzellette/due.mp3", "Barzellette/Vecchie/tre.mp3", "Barzellette/nota.txt"):
        (base / nome).write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Disco", data={"tipo": "cartella", "percorso": str(base), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra.albero.Expand(nodo)
    finestra.contatore.aspetta()
    finestra.schedario.aspetta()
    finestra._conti_arrivati()
    assert _etichette(finestra, nodo) == ["Barzellette, 3 file", "Vuota, nessun file da suonare"]
    una = str(base / "Barzellette" / "una.mp3")
    finestra.schedario.schede[una] = {"dim": 1, "mod": 0, "durata": 61.5, "tag": {}, "sottobrani": None, "durate_sid": None}
    finestra._schede_arrivate()
    assert _etichette(finestra, nodo)[0] == "Barzellette, 3 file, 1:01.500 in tutto, 2 senza durata"
