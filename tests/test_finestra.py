# MeTeOra, le prove della finestra principale, sul desktop nascosto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.55.0 le prove di velocita', tono, equalizzatore e dissolvenza, e del passaggio fra due brani (tappa 4, issue 15).

import datetime
import os
import re
import time
import types

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
    # Dalla 1.55.0 restano futuri solo l'apostrofo e la ì.
    _tasto(finestra, "'")
    assert "scelta della traccia audio" in _ultima(finestra)
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


def test_maiuscolo_c_non_tocca_il_loop(finestra):
    # Dalla 1.58.0 il loop si toglie con Maiuscolo con X, a giro: Maiuscolo
    # con C e' libero.
    finestra.coda.loop_playlist = finestra.archivio.preferiti
    _tasto(finestra, "c", maiuscolo=True)
    assert finestra.coda.loop_playlist is finestra.archivio.preferiti


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

    finestra._seleziona(finestra.nodo_pc)
    assert _premi(finestra, "x", maiuscolo=True).startswith("Il loop si mette su un brano")
    assert suoni_annotati[-1] == "loop_non_qui"
    # Maiuscolo con X, a giro (1.58.0): punto A, punto B, loop tolto.
    scegli(2)
    assert _premi(finestra, "x", maiuscolo=True).startswith("Punto A del loop su 2.mp3.")
    assert suoni_annotati[-1] == "loop_a_messo"
    scegli(4)
    assert _premi(finestra, "x", maiuscolo=True) == "Loop fra 2.mp3 e 4.mp3: 3 brani. Maiuscolo+X lo toglie."
    assert suoni_annotati[-1] == "loop_b_messo"
    assert _etichette(finestra, nodo)[1] == "2.mp3, punto A del loop"
    assert _etichette(finestra, nodo)[3] == "4.mp3, punto B del loop"
    scegli(5)
    assert "fuori dal loop" in _premi(finestra, "x")
    assert suoni_annotati[-1] == "fuori_dal_loop"
    # Con A e B, Maiuscolo con X toglie tutti e due, da qualsiasi punto.
    finestra._seleziona(finestra.nodo_pc)
    assert _premi(finestra, "x", maiuscolo=True).startswith("Loop tolto")
    assert suoni_annotati[-1] == "loop_tolto" and finestra.coda.loop_playlist is None
    assert _etichette(finestra, nodo)[1] == "2.mp3" and _etichette(finestra, nodo)[3] == "4.mp3"
    # Il punto B sullo stesso brano del punto A: quel brano si ripete da solo.
    scegli(3)
    _tasto(finestra, "x", maiuscolo=True)
    assert _premi(finestra, "x", maiuscolo=True) == "Loop fra 3.mp3 e 3.mp3: 1 brano. Maiuscolo+X lo toglie."
    _tasto(finestra, "x", maiuscolo=True)
    # Maiuscolo con C e' libero.
    assert finestra.coda.loop_playlist is None and ("c", True) not in modulo.TASTI


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

    def suona(percorso, sottobrano=None, inizio=None, sfuma_lo_stesso=False):
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

    def suona(percorso, sottobrano=None, inizio=None, sfuma_lo_stesso=False):
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


def _nomi(candidati):
    return [os.path.basename(c[1].percorso) for c in candidati]


def test_maiuscolo_n_accende_e_spegne_la_riproduzione_casuale(finestra, suoni_annotati):
    _tasto(finestra, "n", maiuscolo=True)
    assert finestra.impostazioni["casuale"] is True and _salvate(finestra)["casuale"] is True
    assert suoni_annotati[-1] == "casuale_acceso"
    assert _ultima(finestra) == "Riproduzione casuale accesa: a fine brano il seguente si sceglie a caso."
    _tasto(finestra, "n", maiuscolo=True)
    assert finestra.impostazioni["casuale"] is False and _salvate(finestra)["casuale"] is False
    assert suoni_annotati[-1] == "casuale_spento"
    assert _ultima(finestra) == "Riproduzione casuale spenta: a fine brano si va avanti in ordine."


def test_riproduzione_casuale_nella_plancia(finestra, monkeypatch, suoni_annotati):
    suonati = _finto_motore(finestra, monkeypatch)
    rock, _jazz = _playlist_di_prova(finestra, ("a.mp3", "b.mp3", "c.mp3"), ("x.mp3", "y.mp3"))
    prima, seconda = finestra.archivio.playlist
    finestra.impostazioni["casuale"] = True
    scelte = []

    def a_caso(candidati):
        scelte.append(_nomi(candidati))
        return candidati[-1]

    finestra._a_caso = a_caso
    finestra._suona(prima, prima.brani[0])
    finestra._brano_finito()
    # Fra tutte le voci suonabili che si vedono, tranne quella che suona.
    assert scelte == [["b.mp3", "c.mp3", "x.mp3", "y.mp3"]]
    assert suonati[-1] == ("y.mp3", None) and finestra.coda.playlist is seconda
    assert suoni_annotati[-1] == "brano_seguente_da_solo"
    # Una playlist chiusa esce dal campo.
    finestra.albero.Collapse(rock)
    finestra._brano_finito()
    assert scelte[-1] == ["x.mp3"] and suonati[-1] == ("x.mp3", None)
    # Z e B restano in ordine.
    _tasto(finestra, "b")
    assert suonati[-1] == ("y.mp3", None) and len(scelte) == 2


def test_riproduzione_casuale_nella_lista_e_nel_loop(finestra, monkeypatch, suoni_annotati):
    suonati = _finto_motore(finestra, monkeypatch)
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("a.mp3", "b.mp3", "c.mp3", "d.mp3")])
    pl = finestra.archivio.playlist[0]
    finestra.impostazioni["casuale"] = True
    scelte = []

    def a_caso(candidati):
        scelte.append(_nomi(candidati))
        return candidati[0]

    finestra._a_caso = a_caso
    # La playlist e' chiusa: decide la lista.
    finestra._suona(pl, pl.brani[2])
    finestra._brano_finito()
    assert scelte[-1] == ["a.mp3", "b.mp3", "d.mp3"] and suonati[-1] == ("a.mp3", None)
    # Nel loop si sceglie fra A e B, e tornare indietro non e' il ritorno al
    # punto A.
    finestra.coda.loop_playlist, finestra.coda.punto_a, finestra.coda.punto_b = pl, pl.brani[1], pl.brani[2]
    finestra._suona(pl, pl.brani[2])
    finestra._brano_finito()
    assert scelte[-1] == ["b.mp3"] and suonati[-1] == ("b.mp3", None)
    assert suoni_annotati[-1] == "brano_seguente_da_solo"
    # Il loop su un brano solo lo ripete, come in ordine.
    finestra.coda.punto_a = finestra.coda.punto_b = pl.brani[3]
    finestra._suona(pl, pl.brani[3])
    finestra._brano_finito()
    assert len(scelte) == 2 and suonati[-1] == ("d.mp3", None)
    assert suoni_annotati[-1] == "ritorno_al_punto_a"
    # Senza altri brani nella lista, la riproduzione finisce.
    finestra.coda.togli_loop()
    for brano in pl.brani[:3]:
        brano.saltato = True
    finestra._brano_finito()
    assert _ultima(finestra).startswith("Fine")


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


def test_w_va_a_un_tempo_anche_dalla_fine(finestra, monkeypatch, suoni_annotati):
    salti = []
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda _self: r"C:\m\a.mp3"))
    monkeypatch.setattr(type(finestra.motore), "durata", property(lambda _self: 252.0))
    monkeypatch.setattr(finestra.motore, "vai_a", salti.append)
    for scritto, atteso, frase in (("4:00", 240.0, "Vado a 4:00 di 4:12."), ("-12", 240.0, "Vado a 4:00 di 4:12."), ("-1:30", 162.0, "Vado a 2:42 di 4:12.")):
        monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto(scritto))
        assert _premi(finestra, "w") == frase
        assert salti[-1] == atteso and suoni_annotati[-1] == "vai_a_tempo"
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("-5:00"))
    assert _premi(finestra, "w") == "-5:00 non è un tempo dentro il brano." and len(salti) == 3


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
    for tasto in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F12", "Esc", "Barra rovesciata", "Barra verticale", "Canc", "Backspace"):
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
    monkeypatch.setattr(finestra.motore, "pausa", lambda valore=None, sfumando=False: False)
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
    assert _ultima(finestra) == "Tolti 2 brani, eliminata 1 playlist."
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


def _nell_albero(finestra, codice, maiuscolo=False, ctrl=False):
    evento = wx.KeyEvent(wx.wxEVT_KEY_DOWN)
    evento.SetKeyCode(codice)
    evento.SetShiftDown(maiuscolo)
    evento.SetControlDown(ctrl)
    finestra._tasto_nell_albero(evento)


def _selezionate(finestra):
    return sorted(finestra.albero.GetItemText(v) for v in finestra._voci_selezionate())


def test_maiuscolo_e_ctrl_con_le_frecce_senza_passare_dall_albero(finestra):
    rock, = _playlist_di_prova(finestra, ("a.mp3", "b.mp3", "c.mp3", "d.mp3"))
    finestra.albero.SetFocus()
    finestra._seleziona(_voce_di(finestra, rock, "b.mp3"))
    _nell_albero(finestra, wx.WXK_DOWN, maiuscolo=True)
    # Maiuscolo lasciato e ripremuto arriva da solo alla plancia: l'ancora resta.
    _nell_albero(finestra, wx.WXK_SHIFT, maiuscolo=True)
    _nell_albero(finestra, wx.WXK_DOWN, maiuscolo=True)
    assert _selezionate(finestra) == ["b.mp3", "c.mp3", "d.mp3"]
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "d.mp3"
    # Tornando indietro la selezione si restringe verso l'ancora, e la supera.
    for _ in range(3):
        _nell_albero(finestra, wx.WXK_UP, maiuscolo=True)
    assert _selezionate(finestra) == ["a.mp3", "b.mp3"]
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "a.mp3"
    # Ctrl muove solo il fuoco: le selezioni restano, la voce d'arrivo no.
    _nell_albero(finestra, wx.WXK_DOWN, ctrl=True)
    _nell_albero(finestra, wx.WXK_DOWN, ctrl=True)
    assert _selezionate(finestra) == ["a.mp3", "b.mp3"]
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "c.mp3"
    # Dopo Ctrl l'ancora resta, come in Esplora risorse: Maiuscolo con Fine
    # seleziona da b fino in fondo.
    _nell_albero(finestra, wx.WXK_END, maiuscolo=True)
    assert _selezionate(finestra) == sorted(["b.mp3", "c.mp3", "d.mp3", "Nuova playlist", "Questo PC", "Apri file", "Impostazioni"])
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "Impostazioni"
    # Un altro tasto lascia l'ancora: si riparte dalla voce col fuoco.
    _nell_albero(finestra, wx.WXK_LEFT)
    _nell_albero(finestra, wx.WXK_UP, maiuscolo=True)
    assert _selezionate(finestra) == ["Apri file", "Impostazioni"]


def test_dopo_ctrl_i_comandi_agiscono_sulla_voce_selezionata(finestra, monkeypatch):
    rock, = _playlist_di_prova(finestra, ("a.mp3", "b.mp3", "c.mp3"))
    pl = finestra.archivio.playlist[0]
    finestra._seleziona(_voce_di(finestra, rock, "a.mp3"))
    _nell_albero(finestra, wx.WXK_DOWN, ctrl=True)
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "b.mp3"
    # Canc toglie a, la voce selezionata, non b che ha solo il fuoco.
    _nell_albero(finestra, wx.WXK_DELETE)
    assert [b.nome_del_file for b in pl.brani] == ["b.mp3", "c.mp3"]


def test_backspace_risale_chiudendo(finestra, suoni_annotati):
    rock, _jazz = _playlist_di_prova(finestra, ("a.mp3", "b.mp3"), ("x.mp3",))
    finestra._seleziona(_voce_di(finestra, rock, "b.mp3"))
    _nell_albero(finestra, wx.WXK_BACK)
    assert finestra._voce_corrente() == rock and not finestra.albero.IsExpanded(rock)
    assert suoni_annotati[-1] == "risali" and _ultima(finestra).startswith("Chiuso Playlist, brani: 2")
    _nell_albero(finestra, wx.WXK_BACK)
    assert finestra._voce_corrente() == finestra.nodo_playlist and not finestra.albero.IsExpanded(finestra.nodo_playlist)
    # Le due righe sono una sola, riscritta.
    assert sum(r.startswith("Chiuso ") for r in finestra._righe) == 1
    _nell_albero(finestra, wx.WXK_BACK)
    assert _ultima(finestra) == "Sei già al primo livello della plancia."


def test_maiuscolo_backspace_risale_all_antenato(finestra, tmp_path, suoni_annotati):
    # In Questo PC: dal fondo di una cartella annidata all'unita', che resta
    # aperta con i rami dentro di lei chiusi.
    base = tmp_path / "Disco"
    (base / "Musica" / "Album").mkdir(parents=True)
    (base / "Libri").mkdir()
    (base / "Musica" / "Album" / "x.mp3").write_bytes(b"")
    (base / "Libri" / "y.mp3").write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    unita = finestra.albero.AppendItem(finestra.nodo_pc, "Disco", data={"tipo": "unita", "percorso": str(base), "caricato": False})
    finestra.albero.SetItemHasChildren(unita, True)
    finestra.albero.Expand(unita)
    musica = _voce(finestra, unita, lambda d: d.get("percorso") == str(base / "Musica"))
    finestra.albero.Expand(musica)
    album = next(finestra._figli(musica))
    finestra.albero.Expand(album)
    finestra._seleziona(next(finestra._figli(album)))
    _nell_albero(finestra, wx.WXK_BACK, maiuscolo=True)
    assert finestra._voce_corrente() == unita and finestra.albero.IsExpanded(unita)
    assert not finestra.albero.IsExpanded(musica) and not finestra.albero.IsExpanded(album)
    assert suoni_annotati[-1] == "risali_all_antenato" and _ultima(finestra) == "Risalito a Disco."
    # Nel ramo Playlist l'antenato e' la playlist.
    rock, = _playlist_di_prova(finestra, ("a.mp3",))
    finestra._seleziona(next(finestra._figli(rock)))
    _nell_albero(finestra, wx.WXK_BACK, maiuscolo=True)
    assert finestra._voce_corrente() == rock and finestra.albero.IsExpanded(rock)
    # Gia' sull'antenato non si sale: si dice, con il suono del limite.
    _nell_albero(finestra, wx.WXK_BACK, maiuscolo=True)
    assert finestra._voce_corrente() == rock
    assert suoni_annotati[-1] == "nessun_altro_brano" and _ultima(finestra) == f"Sei già su {finestra._dati(rock)['playlist'].nome}, non si risale oltre."
    # I Preferiti sono una playlist al primo livello: da un loro brano si va a loro.
    finestra._seleziona(next(finestra._figli(rock)))
    _tasto(finestra, codice=wx.WXK_F4)
    finestra.albero.Expand(finestra.nodo_preferiti)
    finestra._seleziona(next(finestra._figli(finestra.nodo_preferiti)))
    _nell_albero(finestra, wx.WXK_BACK, maiuscolo=True)
    assert finestra._voce_corrente() == finestra.nodo_preferiti and finestra.albero.IsExpanded(finestra.nodo_preferiti)
    assert suoni_annotati[-1] == "risali_all_antenato"
    finestra._seleziona(finestra.nodo_pc)
    _nell_albero(finestra, wx.WXK_BACK, maiuscolo=True)
    assert _ultima(finestra) == "Sei già al primo livello della plancia."


def _in_pausa_a(finestra, secondi):
    finestra.motore.vai_a(secondi)
    assert _aspetta(lambda: abs((finestra.motore.posizione or -1) - secondi) < 0.002)


def test_marker_t_r_y_e_le_varianti_con_maiuscolo(finestra, monkeypatch, suoni_annotati, tmp_path):
    brano = tmp_path / "canzone.wav"
    _wav(brano, secondi=5)
    finestra._aggiungi(None, [str(brano)])
    pl = finestra.archivio.playlist[0]
    finestra._suona(pl, pl.brani[0])
    finestra.motore.pausa(True)
    assert _aspetta(lambda: finestra.motore.posizione is not None)
    _in_pausa_a(finestra, 1.0)
    assert _premi(finestra, "t") == "Marker M1 a 0:01."
    assert suoni_annotati[-1] == "marker_messo"
    _in_pausa_a(finestra, 3.25)
    assert _premi(finestra, "t") == "Marker M2 a 0:03.250."
    # Il brano nella plancia dice quanti marker ha, e li mostra aperto.
    nodo = finestra._nodo_della_playlist(pl)
    finestra.albero.Expand(finestra.nodo_playlist)
    finestra.albero.Expand(nodo)
    voce = next(finestra._figli(nodo))
    assert finestra.albero.GetItemText(voce).startswith("canzone.wav, 0:05, 2 marker")
    finestra.albero.Expand(voce)
    assert _etichette(finestra, voce) == ["M1, 0:01", "M2, 0:03.250"]
    # R va al marker prima e porta li' il fuoco della plancia; Y a quello dopo.
    assert _premi(finestra, "r") == "M1, 0:01."
    assert suoni_annotati[-1] == "marker_indietro"
    assert _aspetta(lambda: abs((finestra.motore.posizione or -1) - 1.0) < 0.002)
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "M1, 0:01"
    assert _premi(finestra, "r") == "È il primo marker."
    # T sul marker lo rinomina.
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("Intro"))
    assert _premi(finestra, "t") == "Il marker M1, a 0:01, ora si chiama Intro."
    assert suoni_annotati[-1] == "marker_rinominato"
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "Intro, 0:01"
    assert _premi(finestra, "y") == "M2, 0:03.250."
    assert _premi(finestra, "y") == "È l'ultimo marker."
    # Invio sul marker lo rinomina, Canc lo elimina.
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("Ritornello"))
    evento = wx.TreeEvent(wx.wxEVT_TREE_ITEM_ACTIVATED, finestra.albero, finestra._voce_corrente())
    finestra._invio(evento)
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "Ritornello, 0:03.250"
    _nell_albero(finestra, wx.WXK_DELETE)
    assert _ultima(finestra) == "Eliminato il marker Ritornello, a 0:03.250."
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "Intro, 0:01"
    # Le varianti con Maiuscolo. Restano Intro a 1 secondo e due marker
    # nuovi; il nome automatico riparte dal numero piu' alto rimasto.
    for t in (2.5, 4.0):
        _in_pausa_a(finestra, t)
        _premi(finestra, "t")
    assert [m["nome"] for m in finestra.marcatori.elenco(finestra._contesto_dei_marker("")[0])] == ["Intro", "M1", "M2"]
    # Fermi su M1: Maiuscolo con R e con Y tolgono gli altri, ma non lui.
    _in_pausa_a(finestra, 2.5)
    assert _premi(finestra, "r", maiuscolo=True) == "Tolto 1 marker prima di 0:02.500."
    assert suoni_annotati[-1] == "marker_tolti_prima"
    assert _premi(finestra, "y", maiuscolo=True) == "Tolto 1 marker dopo 0:02.500."
    assert suoni_annotati[-1] == "marker_tolti_dopo"
    assert _premi(finestra, "y", maiuscolo=True) == "Non ci sono marker da togliere dopo 0:02.500."
    assert [m["nome"] for m in finestra.marcatori.elenco(finestra._contesto_dei_marker("")[0])] == ["M1"]
    # Maiuscolo con T li toglie tutti, anche quello su cui si e'.
    assert _premi(finestra, "t", maiuscolo=True) == "Tolto 1 marker in tutto il brano."
    assert suoni_annotati[-1] == "marker_tolti_tutti"
    etichetta = finestra.albero.GetItemText(next(finestra._figli(finestra._nodo_della_playlist(pl))))
    assert etichetta.startswith("canzone.wav, 0:05") and "marker" not in etichetta
    # Il file dei marker si salva.
    from marcatori import Marcatori

    salvati = Marcatori(finestra.marcatori.percorso)
    salvati.carica()
    assert not salvati.voci


def test_marker_condivisi_dalle_copie_identiche(finestra, tmp_path):
    import shutil

    prima = tmp_path / "uno" / "canzone.wav"
    seconda = tmp_path / "due" / "canzone.wav"
    prima.parent.mkdir()
    seconda.parent.mkdir()
    _wav(prima, secondi=3)
    shutil.copy(prima, seconda)
    finestra._aggiungi(None, [str(prima)])
    finestra._aggiungi(None, [str(seconda)])
    uno, due = finestra.archivio.playlist
    finestra._suona(uno, uno.brani[0])
    finestra.motore.pausa(True)
    assert _aspetta(lambda: finestra.motore.posizione is not None)
    _in_pausa_a(finestra, 1.5)
    _premi(finestra, "t")
    # La seconda copia, in un'altra playlist e in un'altra cartella, ha lo stesso marker.
    finestra.schedario.leggi_subito(str(seconda))
    finestra.albero.Expand(finestra.nodo_playlist)
    nodo = finestra._nodo_della_playlist(due)
    finestra.albero.Expand(nodo)
    voce = next(finestra._figli(nodo))
    assert finestra.albero.GetItemText(voce).endswith("1 marker")
    finestra.albero.Expand(voce)
    assert _etichette(finestra, voce) == ["M1, 0:01.500"]


def _brano_con_marker(finestra, tmp_path, tempi, secondi=6, nome="canzone.wav"):
    """Una playlist con un WAV e i suoi marker, il brano in pausa e aperto nella plancia."""
    brano = tmp_path / nome
    _wav(brano, secondi=secondi)
    finestra._aggiungi(None, [str(brano)])
    pl = finestra.archivio.playlist[-1]
    finestra._suona(pl, pl.brani[0])
    finestra.motore.pausa(True)
    assert _aspetta(lambda: finestra.motore.posizione is not None)
    for t in tempi:
        _in_pausa_a(finestra, t)
        _premi(finestra, "t")
    finestra.albero.Expand(finestra.nodo_playlist)
    nodo = finestra._nodo_della_playlist(pl)
    finestra.albero.Expand(nodo)
    voce = next(finestra._figli(nodo))
    finestra.albero.Expand(voce)
    return pl, voce


def test_marker_correzioni_della_revisione(finestra, tmp_path, suoni_annotati):
    # Un'altra playlist aperta, che Canc sui marker non deve chiudere.
    finestra._aggiungi(None, [os.path.join(r"C:\m", "altro.mp3")])
    _pl, voce = _brano_con_marker(finestra, tmp_path, (1.0, 2.0, 3.0))
    altro = finestra._nodo_della_playlist(finestra.archivio.playlist[0])
    finestra.albero.Expand(altro)
    marker = list(finestra._figli(voce))
    # Ai capi, fuori da un marker, il messaggio dice com'e'.
    _in_pausa_a(finestra, 0.5)
    assert _premi(finestra, "r") == "Prima di qui non ci sono marker."
    _in_pausa_a(finestra, 4.0)
    assert _premi(finestra, "y") == "Dopo di qui non ci sono marker."
    # X su un marker fa come sul suo brano: in pausa lo riprende dal punto.
    finestra._seleziona(marker[2])
    _tasto(finestra, "x")
    assert not finestra.motore.in_pausa and suoni_annotati[-1] == "ripresa"
    # E mentre suona lo fa ripartire da capo.
    _tasto(finestra, "x")
    assert suoni_annotati[-1] == "da_capo"
    assert _aspetta(lambda: (finestra.motore.posizione or 9) < 1.0)
    finestra.motore.pausa(True)
    # Ctrl porta il fuoco su M2, Canc elimina M1 selezionato: il fuoco resta su M2.
    finestra._seleziona(marker[0])
    _nell_albero(finestra, wx.WXK_DOWN, ctrl=True)
    _nell_albero(finestra, wx.WXK_DELETE)
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == "M2, 0:02"
    # Canc sui due marker rimasti: l'altra playlist resta aperta, il fuoco va sul brano.
    rimasti = list(finestra._figli(voce))
    finestra._seleziona(rimasti[0])
    finestra.albero.SelectItem(rimasti[1])
    finestra._cancella_selezione()
    assert _ultima(finestra) == "Eliminati 2 marker."
    assert finestra.albero.IsExpanded(altro)
    assert finestra._voce_corrente() == voce
    # Senza brano in corso, i messaggi dicono cosa fare.
    finestra.motore.stop()
    assert _premi(finestra, "r").startswith("Non sta suonando niente: R e Y saltano")
    assert _premi(finestra, "t", maiuscolo=True).endswith("si tolgono con Canc sulla loro voce nella plancia.")


def test_r_mentre_suona_va_oltre_il_marker_appena_raggiunto(finestra, tmp_path):
    _brano_con_marker(finestra, tmp_path, (2.0, 5.0), secondi=12)
    _in_pausa_a(finestra, 8.0)
    finestra.motore.pausa(False)
    assert _premi(finestra, "r") == "M2, 0:05."
    assert _aspetta(lambda: (finestra.motore.posizione or 0) > 5.2)
    assert _premi(finestra, "r") == "M1, 0:02."
    finestra.motore.pausa(True)


def test_copia_aperta_prima_della_scheda_diventa_un_ramo(finestra, monkeypatch, tmp_path):
    import shutil

    (tmp_path / "due").mkdir()
    _brano_con_marker(finestra, tmp_path, (1.0,), secondi=3)
    copia = tmp_path / "due" / "canzone.wav"
    shutil.copy(tmp_path / "canzone.wav", copia)
    # Lo schedario non ha ancora letto la copia quando la plancia la mostra.
    monkeypatch.setattr(finestra.schedario, "chiedi", lambda _percorsi: None)
    finestra._aggiungi(None, [str(copia)])
    nodo = finestra._nodo_della_playlist(finestra.archivio.playlist[-1])
    finestra.albero.Expand(nodo)
    voce = next(finestra._figli(nodo))
    assert not finestra.albero.ItemHasChildren(voce)
    finestra.schedario.leggi_subito(str(copia))
    finestra._schede_arrivate()
    assert finestra.albero.ItemHasChildren(voce) and finestra.albero.GetItemText(voce).endswith("1 marker")
    finestra.albero.Expand(voce)
    assert _etichette(finestra, voce) == ["M1, 0:01"]


def test_le_cifre_e_j_k_non_aprono_i_marker(finestra, monkeypatch, tmp_path):
    pl, voce = _brano_con_marker(finestra, tmp_path, (1.0,), secondi=3)
    finestra.motore.stop()
    finestra.albero.Collapse(voce)
    finestra.albero.Collapse(finestra._nodo_della_playlist(pl))
    _finto_motore(finestra, monkeypatch)
    finestra._seleziona(finestra.nodo_pc)
    _tasto(finestra, "1")
    nodo = finestra._nodo_della_playlist(pl)
    assert finestra.albero.IsExpanded(nodo)
    assert not finestra.albero.IsExpanded(next(finestra._figli(nodo)))


@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_sid_fuori_dalla_collezione_usa_il_percorso(finestra, tmp_path):
    import shutil

    durata, numero = finestra._durata_dei_marker(TURBO_OUTRUN, 1)
    assert durata == 475.0 and numero == 1
    copia = tmp_path / "Turbo_Outrun.sid"
    shutil.copy(TURBO_OUTRUN, copia)
    # Fuori dal database la durata non si sa: i tre minuti predefiniti non valgono.
    assert finestra._durata_dei_marker(str(copia), 1) == (None, 1)
    assert finestra._chiave_dei_marker(str(copia), 1).startswith("percorso|")


def test_marker_non_salvati_si_salvano_all_uscita(app, tmp_path):
    from finestra import Finestra
    from marcatori import Marcatori

    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        f.marcatori.aggiungi("a.mp3|1.000", 0.5, r"C:\a.mp3", 1.0)
        assert f.marcatori.modificato
        f.Close(force=True)
    finally:
        f.Destroy()
    salvati = Marcatori(str(tmp_path / modulo.FILE_MARCATORI))
    salvati.carica()
    assert [m["nome"] for m in salvati.elenco("a.mp3|1.000")] == ["M1"]


def test_maiuscolo_con_le_cifre_va_ai_primi_dieci_marker(finestra, tmp_path, suoni_annotati):
    pl, voce = _brano_con_marker(finestra, tmp_path, (1.0, 2.0, 3.0))
    finestra._seleziona(voce)
    # Maiuscolo con 2, come lo da' Windows con la cifra.
    assert _premi(finestra, "2", maiuscolo=True) == "M2, 0:02."
    assert _aspetta(lambda: abs((finestra.motore.posizione or -1) - 2.0) < 0.05)
    # Il fuoco resta sul brano: X lo fa ancora ripartire da capo.
    assert finestra._voce_corrente() == voce
    _tasto(finestra, "x")
    assert suoni_annotati[-1] == "da_capo"
    assert _aspetta(lambda: (finestra.motore.posizione or 9) < 1.0)
    finestra.motore.pausa(True)
    # Maiuscolo con 3, come lo da' con il segno della tastiera italiana.
    assert _premi(finestra, "£", maiuscolo=True) == "M3, 0:03."
    finestra.motore.pausa(True)
    assert _premi(finestra, "5", maiuscolo=True) == "Non c'è il marker 5: canzone.wav ne ha 3."
    assert suoni_annotati[-1] == "nessun_altro_brano"
    # Il brano fermo riparte dal marker.
    finestra.motore.stop()
    finestra._seleziona(voce)
    _tasto(finestra, "!", maiuscolo=True)
    assert finestra.motore.in_corso == pl.brani[0].percorso
    assert _aspetta(lambda: abs((finestra.motore.posizione or -1) - 1.0) < 0.05)
    finestra.motore.pausa(True)
    finestra._seleziona(finestra.nodo_pc)
    assert _premi(finestra, "1", maiuscolo=True).startswith("Maiuscolo con le cifre va ai marker del brano su cui sta la plancia")


def test_maiuscolo_con_le_cifre_resta_sulla_copia_della_plancia(finestra, tmp_path):
    pl, _voce_in_playlist = _brano_con_marker(finestra, tmp_path, (1.0, 2.0, 3.0))
    # Lo stesso file nei Preferiti, mentre suona dalla playlist.
    finestra._ai_preferiti(pl.brani[0])
    finestra.albero.Expand(finestra.nodo_preferiti)
    preferito = next(finestra._figli(finestra.nodo_preferiti))
    finestra._seleziona(preferito)
    assert _premi(finestra, "3", maiuscolo=True) == "M3, 0:03."
    finestra.motore.pausa(True)
    assert finestra._voce_corrente() == preferito
    # Con il brano fermo la console dice anche da quale marker parte.
    finestra.motore.stop()
    finestra._seleziona(preferito)
    _tasto(finestra, "1", maiuscolo=True)
    assert _ultima(finestra) == "Dal marker M1, 0:01."
    finestra.motore.pausa(True)


def test_frecce_aprono_e_chiudono_i_rami_con_un_suono(finestra, suoni_annotati):
    finestra._aggiungi(None, [os.path.join(r"C:\m", "a.mp3")])
    finestra.albero.Expand(finestra.nodo_playlist)
    nodo = next(finestra._figli(finestra.nodo_playlist))
    suoni_annotati.clear()
    # La freccia vale finche' dura la sua pressione; i comandi non suonano.
    _nell_albero(finestra, wx.WXK_RIGHT)
    assert finestra._freccia_nell_albero
    finestra.albero.Expand(nodo)
    assert suoni_annotati == ["ramo_aperto"]
    finestra.albero.Collapse(nodo)
    assert suoni_annotati == ["ramo_aperto", "ramo_chiuso"]
    wx.Yield()
    assert not finestra._freccia_nell_albero
    finestra.albero.Expand(nodo)
    finestra.albero.Collapse(nodo)
    assert suoni_annotati == ["ramo_aperto", "ramo_chiuso"]


def test_beep_del_livello_quando_cambia_livello(finestra, livelli_annotati):
    import suoni

    assert round(suoni.frequenza_del_livello(1), 2) == 261.63
    assert round(suoni.frequenza_del_livello(5), 2) == 523.25
    finestra._aggiungi(None, [os.path.join(r"C:\m", "a.mp3")])
    finestra.albero.Expand(finestra.nodo_playlist)
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    # Un tasto che porta il fuoco dal secondo al terzo livello suona il terzo.
    finestra._seleziona(nodo)
    _nell_albero(finestra, wx.WXK_DOWN)
    finestra._seleziona(next(finestra._figli(nodo)))
    wx.Yield()
    assert livelli_annotati == [3]
    # Restando allo stesso livello, niente beep.
    _nell_albero(finestra, wx.WXK_DOWN)
    wx.Yield()
    assert livelli_annotati == [3]
    # Backspace risale al secondo livello.
    _nell_albero(finestra, wx.WXK_BACK)
    wx.Yield()
    assert livelli_annotati == [3, 2]


def test_beep_del_livello_dopo_dialoghi_comandi_e_non_dalla_console(finestra, monkeypatch, tmp_path, livelli_annotati):
    import questo_pc
    import suoni

    assert suoni.frequenza_del_livello(30) == suoni.frequenza_del_livello(17)
    for nome in ("a.mp3", "b.mp3"):
        (tmp_path / nome).write_bytes(b"")
    finestra._aggiungi(None, [str(tmp_path / "a.mp3")])
    finestra._aggiungi(None, [str(tmp_path / "b.mp3")])
    finestra.albero.Expand(finestra.nodo_playlist)
    prima, seconda = (finestra._nodo_della_playlist(pl) for pl in finestra.archivio.playlist)
    finestra.albero.Expand(prima)
    finestra.albero.Expand(seconda)
    # Un tasto che apre una conferma: il livello si guarda quando ha finito.
    monkeypatch.setattr(finestra, "_conferma", lambda *_a: True)
    monkeypatch.setattr(questo_pc, "nel_cestino", lambda _p: True)
    finestra._seleziona(next(finestra._figli(prima)))
    _nell_albero(finestra, wx.WXK_DELETE, maiuscolo=True)
    assert livelli_annotati == [2]
    # Un comando della finestra, F9, dal brano alla sua playlist. La
    # cancellazione ha ricostruito il ramo Playlist: le voci si riprendono.
    seconda = finestra._nodo_della_playlist(finestra.archivio.playlist[1])
    finestra.albero.Expand(seconda)
    finestra._seleziona(next(finestra._figli(seconda)))
    _tasto(finestra, codice=wx.WXK_F9)
    assert livelli_annotati == [2, 2]
    # Dalla console il livello della plancia non suona.
    finestra.albero.Expand(seconda)
    finestra._seleziona(next(finestra._figli(seconda)))
    finestra.console.SetFocus()
    wx.Yield()
    _tasto(finestra, codice=wx.WXK_F9)
    assert livelli_annotati == [2, 2]


def test_maiuscolo_con_le_cifre_dal_marker_col_fuoco(finestra, tmp_path):
    _pl, voce = _brano_con_marker(finestra, tmp_path, (1.0, 2.0, 3.0))
    marker = list(finestra._figli(voce))
    finestra._seleziona(marker[0])
    assert _premi(finestra, "3", maiuscolo=True) == "M3, 0:03."
    assert finestra._voce_corrente() == marker[0]
    finestra.motore.pausa(True)


def _beep_rimandato(finestra, monkeypatch, ritardi):
    """Il suono del comando dura ancora per i ritardi dati, e il fuoco e'
    dove dice la lista fuoco: sul desktop nascosto la finestra non e'
    attiva, e FindFocus non troverebbe la plancia."""
    import suoni

    monkeypatch.setattr(suoni, "attesa", lambda: ritardi.pop(0) if ritardi else 0.0)
    fuoco = [finestra.albero]
    monkeypatch.setattr(wx.Window, "FindFocus", staticmethod(lambda: fuoco[0]))
    return fuoco


def test_beep_del_livello_aspetta_il_suono_del_comando(finestra, monkeypatch, livelli_annotati):
    rock, = _playlist_di_prova(finestra, ("a.mp3",))
    finestra._seleziona(next(finestra._figli(rock)))
    # Il suono di Backspace dura ancora: il beep arriva dopo, non sopra.
    _beep_rimandato(finestra, monkeypatch, [0.1])
    _nell_albero(finestra, wx.WXK_BACK)
    assert livelli_annotati == []
    assert _aspetta(lambda: livelli_annotati == [2])


def test_beep_rimandato_superato_dal_tasto_dopo_tace(finestra, monkeypatch, livelli_annotati):
    rock, = _playlist_di_prova(finestra, ("a.mp3",))
    finestra._seleziona(next(finestra._figli(rock)))
    # Due Backspace di fila, mentre suona ancora il primo: il beep del
    # livello intermedio non arriva sopra il secondo suono, tace.
    _beep_rimandato(finestra, monkeypatch, [0.1, 0.1, 0.1])
    _nell_albero(finestra, wx.WXK_BACK)
    _nell_albero(finestra, wx.WXK_BACK)
    assert _aspetta(lambda: livelli_annotati == [1])
    _aspetta(lambda: False, secondi=0.4)
    assert livelli_annotati == [1]


def test_beep_rimandato_tace_se_il_fuoco_lascia_la_plancia(finestra, monkeypatch, livelli_annotati):
    rock, = _playlist_di_prova(finestra, ("a.mp3",))
    finestra._seleziona(next(finestra._figli(rock)))
    fuoco = _beep_rimandato(finestra, monkeypatch, [0.1])
    _nell_albero(finestra, wx.WXK_BACK)
    # Mentre il beep aspetta si apre un dialogo, che prende il fuoco.
    fuoco[0] = None
    _aspetta(lambda: False, secondi=0.4)
    assert livelli_annotati == []


# La finestra delle impostazioni, 1.51.0.

AUTOMATICA = {"indice": 18, "dispositivo": "Altoparlanti (Realtek(R) Audio)", "interfaccia": "Windows WASAPI", "breve": "WASAPI", "latenza": 3.0,
    "esclusiva": False}
ASIO = {"indice": 16, "dispositivo": "Realtek ASIO", "interfaccia": "ASIO", "breve": "ASIO", "latenza": 23.219954648526077, "esclusiva": True}


class _CampoFinto:
    """Il campo di una voce delle impostazioni, che risponde da solo: una
    risposta per ogni apertura, None per Annulla. Annota titolo, testo di
    partenza e istruzioni di ogni apertura, e sa se e' aperto."""

    def __init__(self, *risposte):
        self.risposte = list(risposte)
        self.aperture = []
        self.aperto = False

    def __call__(self, genitore, titolo, testo, istruzioni):
        self.aperture.append({"titolo": titolo, "testo": testo, "istruzioni": list(istruzioni)})
        self.risposta = self.risposte.pop(0)
        return self

    def __enter__(self):
        self.aperto = True
        return self

    def __exit__(self, *_a):
        self.aperto = False
        return False

    def ShowModal(self):
        return wx.ID_CANCEL if self.risposta is None else wx.ID_OK

    @property
    def testo(self):
        return self.risposta


class _ListaFinta:
    """La finestra delle impostazioni, che annota le righe riscritte e se il
    campo era ancora aperto quando e' successo."""

    def __init__(self, campo=None):
        self.campo = campo
        self.righe = {}
        self.a_campo_aperto = []

    def aggiorna(self, chiave, testo):
        self.righe[chiave] = testo
        self.a_campo_aperto.append(bool(self.campo and self.campo.aperto))


def _cambia(finestra, monkeypatch, chiave, *risposte):
    """Cambia una voce delle impostazioni scrivendo le risposte nel campo."""
    campo = _CampoFinto(*risposte)
    monkeypatch.setattr(modulo, "FinestraFiltro", campo)
    lista = _ListaFinta(campo)
    finestra._cambia_impostazione(chiave, lista)
    return campo, lista


def _salvate(finestra):
    from impostazioni import Impostazioni

    salvate = Impostazioni(finestra.impostazioni.percorso)
    salvate.carica()
    return salvate


def test_impostazioni_si_aprono_con_le_loro_voci(finestra, monkeypatch, suoni_annotati):
    monkeypatch.setattr(modulo.schede_audio, "in_uso", lambda elenco=None: AUTOMATICA)
    aperte = []

    class Finta:
        def __init__(self, genitore, voci, al_cambio):
            aperte.append((genitore, voci, al_cambio))

        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

        def ShowModal(self):
            return wx.ID_CANCEL

    monkeypatch.setattr(modulo, "FinestraImpostazioni", Finta)
    voce = _voce(finestra, finestra.albero.GetRootItem(), lambda d: d.get("comando") == "impostazioni")
    finestra._seleziona(voce)
    finestra._invio(wx.TreeEvent(wx.wxEVT_TREE_ITEM_ACTIVATED, finestra.albero, voce))
    assert suoni_annotati[-1] == "impostazioni"
    genitore, voci, al_cambio = aperte[0]
    assert genitore is finestra and al_cambio == finestra._cambia_impostazione
    assert voci == [
        ("volume", "Volume della musica: 80"),
        ("passo_volume", "Passo del volume: 5"),
        ("volume_effetti", "Volume degli effetti: 50%"),
        ("scheda_audio", "Scheda audio: Automatica (Altoparlanti (Realtek(R) Audio), WASAPI)"),
        ("passo_indietro", "Salto indietro di Q: 10 secondi"),
        ("passo_avanti", "Salto avanti di E: 10 secondi"),
        ("velocita", "Velocità: 1"),
        ("tono", "Tono: 0 semitoni"),
        ("bande", "Equalizzatore: piatto, tutte le bande a 0 dB"),
        ("dissolvenza", "Dissolvenza: spenta, 4 secondi"),
        ("casuale", "Riproduzione casuale (Maiuscolo+N): no"),
        ("insegui", "Inseguimento della plancia (Maiuscolo+F8): no"),
        ("caratteri", "Dimensioni dei caratteri: quelle di Windows"),
        ("colori_testo", "Colori dei caratteri: quelli di Windows"),
        ("colori_sfondo", "Colori dello sfondo: quelli di Windows"),
        ("righe_della_console", "Righe della console: 2000"),
        ("salva_console", "Salva console: scrive la console in un file di testo"),
        ("marcatori", "Marcatori: nessuno"),
        ("importa_marcatori", "Importa marcatori: da un file esportato da MeTeOra"),
    ]


def test_impostazioni_nella_finestra_vera(finestra, monkeypatch):
    """Invio sulla lista vera apre il campo, e la riga cambia prima che il campo si chiuda."""
    monkeypatch.setattr(modulo.schede_audio, "in_uso", lambda elenco=None: None)
    dialogo = modulo.FinestraImpostazioni(finestra, finestra._voci_delle_impostazioni(), finestra._cambia_impostazione)
    try:
        assert dialogo.lista.GetString(3) == "Scheda audio: Automatica"
        campo = _CampoFinto("7")
        monkeypatch.setattr(modulo, "FinestraFiltro", campo)
        dialogo.lista.SetSelection(1)
        evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
        evento.SetKeyCode(wx.WXK_RETURN)
        evento.SetEventObject(dialogo.lista)
        dialogo._tasto(evento)
        assert dialogo.lista.GetString(1) == "Passo del volume: 7"
        assert dialogo.lista.GetSelection() == 1
        assert campo.aperture[0]["titolo"] == "Passo del volume"
    finally:
        dialogo.Destroy()


def test_impostazioni_valori_buoni_corretti_e_sbagliati(finestra, monkeypatch, suoni_annotati):
    # Un valore sbagliato riapre il campo con l'errore in testa al titolo e il
    # testo scritto; uno oltre il limite si corregge, e la console lo dice.
    campo, lista = _cambia(finestra, monkeypatch, "passo_volume", " x ", "70")
    errore = "Passo del volume: x non è un numero; scrivi un numero intero da 1 a 50."
    assert [a["titolo"] for a in campo.aperture] == ["Passo del volume", f"{errore} Passo del volume"]
    assert [a["testo"] for a in campo.aperture] == ["5", "x"]
    istruzioni = campo.aperture[0]["istruzioni"]
    assert "Adesso è 5." in istruzioni and istruzioni[-1] == modulo.REGOLA_DEL_DOLLARO
    assert finestra.impostazioni["passo_volume"] == 50 and _salvate(finestra)["passo_volume"] == 50
    assert suoni_annotati[-4:] == ["domanda", "errore", "domanda", "impostazione_cambiata"]
    assert _senza_ora(finestra._righe[-2]) == errore
    assert _ultima(finestra) == "Più e meno ora cambiano il volume di 50. Passo del volume: 70 è oltre il massimo, ho messo 50."
    # La riga della lista si riscrive mentre il campo e' ancora li'.
    assert lista.righe == {"passo_volume": "Passo del volume: 50"} and lista.a_campo_aperto == [True]
    # Annulla non cambia niente.
    _campo, lista = _cambia(finestra, monkeypatch, "passo_volume", None)
    assert _ultima(finestra) == "Passo del volume non cambiato." and finestra.impostazioni["passo_volume"] == 50 and not lista.righe
    # Il volume della musica vale subito, e si salva subito.
    _cambia(finestra, monkeypatch, "volume", "150")
    assert finestra.motore.volume == 150 and _salvate(finestra)["volume"] == 150
    assert _ultima(finestra) == "Il volume della musica ora è 150, amplificato oltre il 100."
    campo, lista = _cambia(finestra, monkeypatch, "volume_effetti", "35%")
    assert campo.aperture[0]["testo"] == "50"
    assert finestra.impostazioni["volume_effetti"] == 0.35 and lista.righe["volume_effetti"] == "Volume degli effetti: 35%"
    assert _ultima(finestra) == "Gli effetti sonori ora suonano al 35%."
    # I salti di Q ed E, anche con la virgola, almeno di un decimo.
    _campo, lista = _cambia(finestra, monkeypatch, "passo_indietro", "2,5")
    assert finestra.impostazioni["passo_indietro"] == 2.5 and lista.righe["passo_indietro"] == "Salto indietro di Q: 2.5 secondi"
    _cambia(finestra, monkeypatch, "passo_avanti", "0.05")
    assert finestra.impostazioni["passo_avanti"] == 0.1
    assert _ultima(finestra) == "Il salto avanti ora è di 0.1 secondi. Salto avanti di E: 0.05 è sotto il minimo, ho messo 0.1."
    campo, _lista = _cambia(finestra, monkeypatch, "passo_indietro", "1:30")
    assert campo.aperture[0]["testo"] == "2.5" and finestra.impostazioni["passo_indietro"] == 90
    salvate = _salvate(finestra)
    assert (salvate["volume_effetti"], salvate["passo_indietro"], salvate["passo_avanti"]) == (0.35, 90, 0.1)


def test_impostazioni_inseguimento(finestra, monkeypatch, suoni_annotati):
    inseguiti = []
    monkeypatch.setattr(finestra, "_insegui", lambda: inseguiti.append(True))
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda _self: r"C:\m\a.mp3"))
    campo, lista = _cambia(finestra, monkeypatch, "insegui", "forse", "Sì")
    assert [a["testo"] for a in campo.aperture] == ["no", "forse"]
    assert campo.aperture[1]["titolo"].startswith("Inseguimento della plancia: forse non è né sì né no; scrivi sì o no.")
    assert finestra.impostazioni["insegui"] is True and _salvate(finestra)["insegui"] is True and inseguiti == [True]
    assert lista.righe["insegui"] == "Inseguimento della plancia (Maiuscolo+F8): sì"
    assert _ultima(finestra) == "Inseguimento agganciato: la selezione della plancia segue il brano che suona."
    _cambia(finestra, monkeypatch, "insegui", "spento")
    assert finestra.impostazioni["insegui"] is False and inseguiti == [True]
    assert _ultima(finestra) == "Inseguimento sganciato: la selezione resta dove la lasci."


def test_impostazioni_riproduzione_casuale(finestra, monkeypatch, suoni_annotati):
    campo, lista = _cambia(finestra, monkeypatch, "casuale", "forse", "acceso")
    assert [a["testo"] for a in campo.aperture] == ["no", "forse"]
    assert campo.aperture[1]["titolo"].startswith("Riproduzione casuale: forse non è né sì né no; scrivi sì o no.")
    assert "Adesso è spenta." in campo.aperture[0]["istruzioni"]
    assert finestra.impostazioni["casuale"] is True and _salvate(finestra)["casuale"] is True
    assert lista.righe["casuale"] == "Riproduzione casuale (Maiuscolo+N): sì"
    assert _ultima(finestra) == "Riproduzione casuale accesa: a fine brano il seguente si sceglie a caso."
    _cambia(finestra, monkeypatch, "casuale", "no")
    assert finestra.impostazioni["casuale"] is False
    assert _ultima(finestra) == "Riproduzione casuale spenta: a fine brano si va avanti in ordine."


def test_impostazioni_righe_della_console_tagliano_subito(finestra, monkeypatch):
    for i in range(400):
        finestra.scrivi(f"riga {i}")
    finestra.console.SetInsertionPoint(finestra.console.GetLastPosition())
    _campo, lista = _cambia(finestra, monkeypatch, "righe_della_console", "150")
    # Le 150 righe piu' recenti, senza il margine di 100, piu' quella che lo dice.
    assert len(finestra._righe) == 151 and finestra._righe[0].startswith("riga 250")
    testo = finestra.console.GetValue().replace("\r\n", "\n").replace("\r", "\n")
    assert testo.split("\n") == finestra._righe
    assert _ultima(finestra) == "La console ora tiene 150 righe." and lista.righe["righe_della_console"] == "Righe della console: 150"
    _cambia(finestra, monkeypatch, "righe_della_console", "50")
    assert len(finestra._righe) == 101 and finestra.impostazioni["righe_della_console"] == 100
    assert _ultima(finestra) == "La console ora tiene 100 righe. Righe della console: 50 è sotto il minimo, ho messo 100."


def _colore_del_testo(controllo, posizione=0):
    attributi = wx.TextAttr()
    controllo.GetStyle(posizione, attributi)
    return tuple(attributi.GetTextColour())[:3]


def _minimo_del_cruscotto(f):
    """Cinque righe del suo carattere, ma non oltre un terzo della finestra,
    e non meno di due righe."""
    riga = f.cruscotto.GetCharHeight()
    terzo = f.albero.GetParent().GetClientSize().height // 3
    return max(riga * 2 + 8, min(riga * 6 + 8, terzo)) if terzo > 0 else riga * 6 + 8


def test_cruscotto_al_massimo_un_terzo_della_finestra(finestra, monkeypatch):
    # Con caratteri a 72 punti in una finestra bassa, come un portatile, il
    # cruscotto non si mangia plancia e console (Gabriele, 1 ottobre 2026).
    finestra.SetSize(wx.Size(1200, 700))
    wx.Yield()
    _cambia(finestra, monkeypatch, "caratteri", "72")
    wx.Yield()
    pannello = finestra.albero.GetParent()
    riga = finestra.cruscotto.GetCharHeight()
    assert finestra.cruscotto.GetMinSize().GetHeight() == max(riga * 2 + 8, pannello.GetClientSize().height // 3)
    assert finestra.albero.GetSize().GetHeight() > riga and finestra.console.GetSize().GetHeight() > riga
    # Con un carattere che ci sta, le cinque righe tornano.
    _cambia(finestra, monkeypatch, "caratteri", "12")
    riga = finestra.cruscotto.GetCharHeight()
    assert riga * 6 + 8 <= pannello.GetClientSize().height // 3
    assert finestra.cruscotto.GetMinSize().GetHeight() == riga * 6 + 8


def test_impostazioni_caratteri_e_colori(finestra, monkeypatch):
    di_sistema = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).GetPointSize()
    campo, lista = _cambia(finestra, monkeypatch, "caratteri", "12 14 16")
    assert campo.aperture[0]["testo"] == ""
    assert [c.GetFont().GetPointSize() for c in (finestra.albero, finestra.console, finestra.cruscotto)] == [12, 14, 16]
    # Il cruscotto si rimisura sul carattere nuovo.
    assert finestra.cruscotto.GetMinSize().GetHeight() == _minimo_del_cruscotto(finestra)
    assert lista.righe["caratteri"] == "Dimensioni dei caratteri: plancia 12, console 14, cruscotto 16"
    assert _ultima(finestra) == "Dimensioni dei caratteri: plancia 12, console 14, cruscotto 16."
    assert _salvate(finestra)["caratteri"] == {"p": 12, "c": 14, "t": 16}
    campo, lista = _cambia(finestra, monkeypatch, "colori_testo", "p31.31.31 c0.50.0 t100.0.0")
    assert campo.aperture[0]["testo"] == ""
    assert [tuple(c.GetForegroundColour())[:3] for c in (finestra.albero, finestra.console, finestra.cruscotto)] == [(79, 79, 79), (0, 128, 0), (255, 0, 0)]
    assert lista.righe["colori_testo"] == "Colori dei caratteri: plancia 31.31.31, console 0.50.0, cruscotto 100.0.0"
    # Il testo che arriva nella console, e quello del cruscotto riscritto, hanno il colore.
    finestra.scrivi("una riga colorata")
    assert _colore_del_testo(finestra.console, finestra.console.GetLastPosition() - 3) == (0, 128, 0)
    finestra._area_precedente = "console"
    assert finestra._rinfresca_cruscotto()
    assert _colore_del_testo(finestra.cruscotto) == (255, 0, 0)
    # Un carattere nuovo, dopo i colori, non li porta via.
    campo, _lista = _cambia(finestra, monkeypatch, "caratteri", "20")
    assert campo.aperture[0]["testo"] == "12 14 16"
    assert finestra.console.GetFont().GetPointSize() == 20
    assert _colore_del_testo(finestra.console) == (0, 128, 0) and _colore_del_testo(finestra.cruscotto) == (255, 0, 0)
    _cambia(finestra, monkeypatch, "colori_sfondo", "t100.100.80")
    assert tuple(finestra.cruscotto.GetBackgroundColour())[:3] == (255, 255, 204)
    # La lettera da sola riporta l'area ai colori di Windows; le altre restano.
    campo, lista = _cambia(finestra, monkeypatch, "colori_testo", "p")
    assert campo.aperture[0]["testo"] == "p31.31.31 c0.50.0 t100.0.0"
    assert finestra.albero.GetForegroundColour() == wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
    assert tuple(finestra.console.GetForegroundColour())[:3] == (0, 128, 0)
    assert lista.righe["colori_testo"] == "Colori dei caratteri: console 0.50.0, cruscotto 100.0.0; le altre aree di Windows"
    assert _salvate(finestra)["colori_testo"] == {"c": [0, 50, 0], "t": [100, 0, 0]}
    # Il campo vuoto riporta i caratteri a quelli di Windows.
    _cambia(finestra, monkeypatch, "caratteri", "")
    assert {c.GetFont().GetPointSize() for c in (finestra.albero, finestra.console, finestra.cruscotto)} == {di_sistema}
    assert _ultima(finestra) == "Dimensioni dei caratteri: quelle di Windows."
    # Un valore sbagliato non tocca niente.
    campo, _lista = _cambia(finestra, monkeypatch, "colori_sfondo", "x50.50.50", None)
    assert campo.aperture[1]["titolo"].startswith("Colori dello sfondo: in x50.50.50, x non è un'area")
    assert _ultima(finestra) == "Colori dello sfondo non cambiati."


def test_caratteri_e_colori_all_avvio(app, tmp_path):
    """I caratteri e i colori salvati si danno alle aree gia' nella costruzione,
    prima di misurare il cruscotto."""
    import json

    from finestra import Finestra

    (tmp_path / modulo.FILE_IMPOSTAZIONI).write_text(json.dumps({"caratteri": {"t": 18}, "colori_testo": {"c": [100, 0, 0]}}), encoding="utf-8")
    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        assert f.cruscotto.GetFont().GetPointSize() == 18
        assert f.cruscotto.GetMinSize().GetHeight() == _minimo_del_cruscotto(f)
        assert tuple(f.console.GetForegroundColour())[:3] == (255, 0, 0)
        assert _colore_del_testo(f.console) == (255, 0, 0)
        # Le aree senza impostazioni restano di Windows, mai toccate.
        assert not f.albero.UseForegroundColour() and not f.console.UseBackgroundColour()
        f.Close(force=True)
    finally:
        f.Destroy()


class _Fermo(datetime.datetime):
    """Un orologio fermo alle 15:42 del 1 ottobre 2026."""

    @classmethod
    def now(cls, tz=None):
        return cls(2026, 10, 1, 15, 42)


def test_salva_console(finestra, monkeypatch, tmp_path, suoni_annotati):
    monkeypatch.setattr(modulo, "datetime", types.SimpleNamespace(datetime=_Fermo))
    finestra.scrivi("Una riga con un'emoji 🎵")
    righe = list(finestra._righe)
    lista = _ListaFinta()
    finestra._cambia_impostazione("salva_console", lista)
    nome = f"MeTeOra-V{modulo.version.VERSION.replace('.', '_')}-2026_10_01-15_42.txt"
    assert (tmp_path / nome).read_text(encoding="utf-8") == "\n".join(righe)
    assert suoni_annotati[-1] == "console_salvata"
    assert _ultima(finestra) == f"Console salvata in {nome}, nella cartella del programma: {len(righe)} righe."
    # Nello stesso minuto il secondo file ha -2 in fondo, il terzo -3.
    finestra._cambia_impostazione("salva_console", lista)
    finestra._cambia_impostazione("salva_console", lista)
    secondo, terzo = tmp_path / nome.replace(".txt", "-2.txt"), tmp_path / nome.replace(".txt", "-3.txt")
    assert terzo.is_file() and secondo.read_text(encoding="utf-8") == "\n".join([*righe, finestra._righe[-3]])
    assert not lista.righe
    # Una cartella che non si scrive: la console lo dice.
    percorso = finestra.impostazioni.percorso
    finestra.impostazioni.percorso = str(tmp_path / "manca" / "imp.json")
    try:
        finestra._salva_console()
    finally:
        finestra.impostazioni.percorso = percorso
    assert suoni_annotati[-1] == "errore" and _ultima(finestra).startswith("Non riesco a salvare la console: ")


class _FileFinto:
    """Il dialogo di un file, che risponde da solo con un percorso, o con
    Annulla se il percorso e' None; annota le sue aperture."""

    def __init__(self, percorso):
        self.percorso = percorso
        self.aperture = []

    def __call__(self, genitore, messaggio, **opzioni):
        self.aperture.append((genitore, messaggio, opzioni))
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def ShowModal(self):
        return wx.ID_CANCEL if self.percorso is None else wx.ID_OK

    def GetPath(self):
        return str(self.percorso)


def _finestra_delle_impostazioni(finestra, monkeypatch):
    """La finestra delle impostazioni vera, mai mostrata, genitore dei dialoghi veri."""
    monkeypatch.setattr(modulo.schede_audio, "in_uso", lambda elenco=None: None)
    return modulo.FinestraImpostazioni(finestra, finestra._voci_delle_impostazioni(), finestra._cambia_impostazione)


def test_finestra_dei_marcatori(finestra, monkeypatch, tmp_path, suoni_annotati):
    import dialoghi
    from marcatori import Marcatori

    _pl, voce = _brano_con_marker(finestra, tmp_path, (1.0, 2.0, 3.0))
    lista = _finestra_delle_impostazioni(finestra, monkeypatch)
    viste = []
    conferme = []
    cercati = []

    def righe(dialogo):
        return [dialogo.lista.GetItemText(i) for i in range(dialogo.lista.GetItemCount())]

    def copione(dialogo):
        viste.append(righe(dialogo))
        # La barra rovesciata cerca con i suoi tre suoni, non con quelli della
        # ricerca nella console: trovato, ripartito dalla cima, non trovato.
        monkeypatch.setattr(dialoghi, "DialogoTesto", _DialogoFinto("m2", "m2", "assolo"))
        for _ in range(3):
            dialogo._cerca()
            cercati.append((dialogo.lista.GetFocusedItem(), suoni_annotati[-1]))
        dialogo.lista.Select(1, False)
        dialogo.lista.Select(0)
        dialogo.lista.Focus(0)
        # Invio rinomina la riga col fuoco.
        monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("Intro"))
        dialogo._rinomina()
        viste.append(righe(dialogo))
        # Canc su una riga sola la elimina senza chiedere.
        dialogo.lista.Select(0, False)
        dialogo.lista.Select(1)
        dialogo.lista.Focus(1)
        dialogo._elimina()
        viste.append(righe(dialogo))
        # Esporta selezionati, nel file scelto, senza percorsi.
        dialogo.lista.Select(0)
        monkeypatch.setattr(modulo, "DialogoDiFile", _FileFinto(tmp_path / "esportati"))
        dialogo._esporta()
        # Canc su due righe chiede conferma, con la finestra dei marcatori come genitore.
        monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo, genitore: conferme.append((domanda, genitore)) or True)
        dialogo._elimina()
        viste.append(righe(dialogo))
        return wx.ID_CANCEL

    monkeypatch.setattr(dialoghi.FinestraMarcatori, "ShowModal", copione)
    try:
        finestra._cambia_impostazione("marcatori", lista)
        assert lista.lista.GetString(list(modulo.VOCI_DELLE_IMPOSTAZIONI).index("marcatori")) == "Marcatori: nessuno"
    finally:
        lista.Destroy()
    brano = str(tmp_path / "canzone.wav")
    assert viste[0] == [f"{brano}\\M1, 0:01", f"{brano}\\M2, 0:02", f"{brano}\\M3, 0:03"]
    assert cercati == [(1, "trovato_nei_marcatori"), (1, "ripartito_nei_marcatori"), (1, "non_trovato_nei_marcatori")]
    assert any(_senza_ora(r) == "Nei marcatori non c'è assolo." for r in finestra._righe)
    assert viste[1][0] == f"{brano}\\Intro, 0:01"
    assert viste[2] == [f"{brano}\\Intro, 0:01", f"{brano}\\M3, 0:03"]
    assert viste[3] == ["Nessun marcatore."]
    assert len(conferme) == 1 and conferme[0][0] == "Eliminare 2 marker?" and isinstance(conferme[0][1], dialoghi.FinestraMarcatori)
    # L'esportazione: un file .json, con i due marker scelti e senza percorsi.
    _genitore, messaggio, opzioni = modulo.DialogoDiFile.aperture[0]
    assert messaggio == "Esporta marcatori" and opzioni["defaultFile"] == modulo.FILE_DELL_ESPORTAZIONE and opzioni["defaultDir"] == str(tmp_path)
    assert opzioni["style"] == wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
    esportate = Marcatori.leggi_esportazione(str(tmp_path / "esportati.json"))
    assert [(v["file"], [m["nome"] for m in v["marker"]]) for v in esportate] == [("canzone.wav", ["Intro", "M3"])]
    assert "percorsi" not in (tmp_path / "esportati.json").read_text(encoding="utf-8")
    # I suoni, le righe della console e la plancia rinfrescata.
    assert [s for s in suoni_annotati if s != "domanda"][-8:] == ["marcatori", "trovato_nei_marcatori", "ripartito_nei_marcatori", "non_trovato_nei_marcatori",
        "marker_rinominato", "marker_eliminato", "marcatori_esportati", "marker_eliminato"]
    assert any(_senza_ora(r) == "Esportati 2 marker di 1 file in esportati.json." for r in finestra._righe)
    assert _ultima(finestra) == "Eliminati 2 marker."
    etichetta = finestra.albero.GetItemText(voce)
    assert etichetta.startswith("canzone.wav, 0:06") and "marker" not in etichetta
    salvati = Marcatori(finestra.marcatori.percorso)
    salvati.carica()
    assert not salvati.voci


def test_marcatori_cancella_tutto(finestra, monkeypatch, tmp_path, suoni_annotati):
    import dialoghi

    _pl, voce = _brano_con_marker(finestra, tmp_path, (1.0, 2.0))
    finestra.marcatori.aggiungi("altro.mp3|9.000", 4.0, r"C:\m\altro.mp3", 9.0)
    lista = _finestra_delle_impostazioni(finestra, monkeypatch)
    risposte = [False, True]
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo, genitore: risposte.pop(0))

    def copione(dialogo):
        for _ in range(3):
            dialogo._cancella_tutto()
        return wx.ID_CANCEL

    monkeypatch.setattr(dialoghi.FinestraMarcatori, "ShowModal", copione)
    assert finestra._riga_dell_impostazione("marcatori") == "Marcatori: 3 in 2 file"
    try:
        finestra._cambia_impostazione("marcatori", lista)
        assert lista.lista.GetString(list(modulo.VOCI_DELLE_IMPOSTAZIONI).index("marcatori")) == "Marcatori: nessuno"
    finally:
        lista.Destroy()
    righe = [_senza_ora(r) for r in finestra._righe[-3:]]
    # La terza volta la lista dice gia' che non ci sono marcatori.
    assert righe == ["I marcatori restano dove sono.", "Cancellati tutti i marcatori: 3 marker in 2 file.", "Non ci sono marcatori."]
    assert suoni_annotati[-1] == "non_disponibile" and "marcatori_cancellati" in suoni_annotati
    assert not finestra.marcatori.voci and not list(finestra._figli(voce))


def test_importa_marcatori(finestra, monkeypatch, tmp_path, suoni_annotati):
    import json

    from marcatori import Marcatori

    _pl, voce = _brano_con_marker(finestra, tmp_path, (1.0,))
    k = next(iter(finestra.marcatori.voci))
    durata = finestra.marcatori.voci[k]["durata"]
    # Un marker entro la tolleranza di quello che c'e' gia', e uno nuovo.
    esportazione = tmp_path / "da importare.json"
    esportazione.write_text(json.dumps({"formato": "MeTeOra - Marcatori", "versione": 1, "marcatori": [{"file": "Canzone.WAV", "durata": durata,
        "sottobrano": None, "marker": [{"tempo": 1.002, "nome": "Doppione"}, {"tempo": 2.5, "nome": "Strofa"}]}]}), encoding="utf-8")
    monkeypatch.setattr(modulo, "DialogoDiFile", _FileFinto(esportazione))
    lista = _ListaFinta()
    finestra._cambia_impostazione("importa_marcatori", lista)
    assert modulo.DialogoDiFile.aperture[0][2]["style"] == wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    assert suoni_annotati[-1] == "marcatori_importati" and _ultima(finestra) == "Importato 1 marcatore, 1 c'era già."
    assert _etichette(finestra, voce) == ["M1, 0:01", "Strofa, 0:02.500"]
    assert lista.righe == {"marcatori": "Marcatori: 2 in 1 file"}
    salvati = Marcatori(finestra.marcatori.percorso)
    salvati.carica()
    assert [m["nome"] for m in salvati.elenco(k)] == ["M1", "Strofa"]
    # La seconda volta non aggiunge niente.
    finestra._cambia_impostazione("importa_marcatori", lista)
    assert _ultima(finestra) == "Importati 0 marcatori, 2 c'erano già."
    # Un file che non e' un'esportazione, e Annulla.
    rotto = tmp_path / "rotto.json"
    rotto.write_text("non è json", encoding="utf-8")
    monkeypatch.setattr(modulo, "DialogoDiFile", _FileFinto(rotto))
    finestra._cambia_impostazione("importa_marcatori", lista)
    assert suoni_annotati[-1] == "errore" and _ultima(finestra) == "rotto.json non è un'esportazione dei marcatori di MeTeOra: non è un file JSON."
    monkeypatch.setattr(modulo, "DialogoDiFile", _FileFinto(None))
    finestra._cambia_impostazione("importa_marcatori", lista)
    assert _ultima(finestra) == "Importazione annullata."


class _SceltaFinta:
    """La scelta da una lista, che risponde da sola con un indice, o con
    Annulla se l'indice e' None; annota titolo, righe e scelta di partenza."""

    def __init__(self, indice):
        self.indice = indice
        self.aperture = []

    def __call__(self, genitore, titolo, voci, scelta):
        self.aperture.append((titolo, list(voci), scelta))
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def ShowModal(self):
        return wx.ID_CANCEL if self.indice is None else wx.ID_OK

    def GetSelection(self):
        return self.indice


def _esito(uscita, automatica=False, mancante=False, musica=True):
    return {"uscita": uscita, "dispositivo": uscita["dispositivo"] if uscita else None, "interfaccia": uscita["interfaccia"] if uscita else None,
        "automatica": automatica, "mancante": mancante, "musica": musica, "mpv": "auto"}


class _ProvaFinta:
    """Acusticator.riproduci, che non apre niente: annota la forma del
    buffer di silenzio e dice se la scheda si e' aperta come le si chiede."""

    def __init__(self, aperta=True):
        self.aperta = aperta
        self.prove = []

    def __call__(self, buffer, fs=None, sync=False):
        assert not buffer.any(), "la prova deve essere silenzio"
        self.prove.append(buffer.shape)
        return self.aperta


def test_scheda_audio(finestra, monkeypatch, suoni_annotati):
    import GBUtils

    applicate = []
    esiti = {"Realtek ASIO": _esito(ASIO, musica=False), "": _esito(AUTOMATICA, automatica=True), AUTOMATICA["dispositivo"]: _esito(AUTOMATICA)}

    def applica(scelta, motore, avvio=False):
        assert motore is finestra.motore and not avvio
        applicate.append(dict(scelta))
        return esiti[scelta.get("dispositivo", "")]

    monkeypatch.setattr(modulo.schede_audio, "uscite", lambda: [AUTOMATICA, ASIO])
    monkeypatch.setattr(modulo.schede_audio, "in_uso", lambda elenco=None: AUTOMATICA)
    monkeypatch.setattr(modulo.schede_audio, "automatica", lambda: AUTOMATICA)
    monkeypatch.setattr(modulo.schede_audio, "applica", applica)
    prova = _ProvaFinta()
    monkeypatch.setattr(GBUtils.Acusticator, "riproduci", prova)
    # La scheda ASIO: la musica non la ritrova, e la console lo dice.
    scelta = _SceltaFinta(2)
    monkeypatch.setattr(modulo, "FinestraScelta", scelta)
    lista = _ListaFinta()
    finestra._cambia_impostazione("scheda_audio", lista)
    assert scelta.aperture == [("Scheda audio", ["Automatica: Altoparlanti (Realtek(R) Audio), WASAPI, 3 ms", "Altoparlanti (Realtek(R) Audio), WASAPI, 3 ms",
        "Realtek ASIO, ASIO, 23.2 ms, esclusiva: può zittire NVDA"], 0)]
    assert applicate == [{"dispositivo": "Realtek ASIO", "interfaccia": "ASIO"}]
    assert finestra.impostazioni["scheda_audio"] == {"dispositivo": "Realtek ASIO", "interfaccia": "ASIO"}
    assert _salvate(finestra)["scheda_audio"] == {"dispositivo": "Realtek ASIO", "interfaccia": "ASIO"}
    assert suoni_annotati[-2:] == ["domanda", "scheda_audio"]
    assert _ultima(finestra) == "Scheda audio: Realtek ASIO, ASIO. La musica non la ritrova, e suona sulla scheda di Windows."
    assert lista.righe == {"scheda_audio": "Scheda audio: Realtek ASIO, ASIO"}
    # La scheda si e' provata con un centesimo di secondo di silenzio stereo.
    assert prova.prove == [(modulo.SILENZIO_DI_PROVA, 2)]
    # La scheda che gli effetti non aprono: si torna all'automatica. Il suono
    # della scheda non parte, tanto non si sentirebbe: suona l'errore.
    prova.aperta = False
    scelta = _SceltaFinta(1)
    monkeypatch.setattr(modulo, "FinestraScelta", scelta)
    finestra._cambia_impostazione("scheda_audio", lista)
    assert scelta.aperture[0][2] == 2
    assert applicate[1:] == [{"dispositivo": AUTOMATICA["dispositivo"], "interfaccia": "Windows WASAPI"}, {}]
    assert finestra.impostazioni["scheda_audio"] == {} and _salvate(finestra)["scheda_audio"] == {}
    assert suoni_annotati[-2:] == ["domanda", "errore"]
    assert _ultima(finestra) == ("La scheda audio Altoparlanti (Realtek(R) Audio), WASAPI non si apre. "
        "Torno alla scelta automatica, Altoparlanti (Realtek(R) Audio), WASAPI.")
    assert lista.righe["scheda_audio"] == "Scheda audio: Automatica (Altoparlanti (Realtek(R) Audio), WASAPI)"
    # L'automatica, scelta di nuovo, e Annulla.
    prova.aperta = True
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaFinta(0))
    finestra._cambia_impostazione("scheda_audio", lista)
    assert applicate[-1] == {} and _ultima(finestra) == "Scheda audio: Automatica (Altoparlanti (Realtek(R) Audio), WASAPI)."
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaFinta(None))
    finestra._cambia_impostazione("scheda_audio", lista)
    assert _ultima(finestra) == "Scheda audio non cambiata." and len(applicate) == 4

    # Un elenco che non si legge: la console lo dice.
    def guasto():
        raise OSError("PortAudio non risponde")

    monkeypatch.setattr(modulo.schede_audio, "uscite", guasto)
    finestra._cambia_impostazione("scheda_audio", lista)
    assert suoni_annotati[-1] == "errore" and _ultima(finestra) == "Non riesco a leggere le schede audio: PortAudio non risponde."


def test_scheda_audio_con_gli_effetti_a_zero(finestra, monkeypatch, suoni_annotati):
    import GBUtils

    import suoni

    # Con il volume degli effetti a zero nessun suono parte, come in suoni.suona
    # vero: la prova d'apertura della scheda deve farsi lo stesso.
    annota = suoni.suona
    monkeypatch.setattr(suoni, "suona", lambda evento, volume=0.5, sync=False: volume > 0 and annota(evento, volume, sync))
    finestra.impostazioni["volume_effetti"] = 0.0
    applicate = []

    def applica(scelta, motore, avvio=False):
        applicate.append(dict(scelta))
        return _esito(ASIO, musica=False) if scelta else _esito(AUTOMATICA, automatica=True)

    monkeypatch.setattr(modulo.schede_audio, "uscite", lambda: [AUTOMATICA, ASIO])
    monkeypatch.setattr(modulo.schede_audio, "in_uso", lambda elenco=None: AUTOMATICA)
    monkeypatch.setattr(modulo.schede_audio, "applica", applica)
    prova = _ProvaFinta(aperta=False)
    monkeypatch.setattr(GBUtils.Acusticator, "riproduci", prova)
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaFinta(2))
    lista = _ListaFinta()
    finestra._cambia_impostazione("scheda_audio", lista)
    # La scheda ASIO non si apre: si torna all'automatica, e la console lo dice.
    assert prova.prove == [(modulo.SILENZIO_DI_PROVA, 2)]
    assert applicate == [{"dispositivo": "Realtek ASIO", "interfaccia": "ASIO"}, {}]
    assert finestra.impostazioni["scheda_audio"] == {} and _salvate(finestra)["scheda_audio"] == {}
    assert _ultima(finestra) == "La scheda audio Realtek ASIO, ASIO non si apre. Torno alla scelta automatica, Altoparlanti (Realtek(R) Audio), WASAPI."
    assert lista.righe["scheda_audio"] == "Scheda audio: Automatica (Altoparlanti (Realtek(R) Audio), WASAPI)"
    # Muti anche il suono della scheda e quello dell'errore.
    assert suoni_annotati == []


def test_scheda_audio_all_avvio(app, tmp_path, monkeypatch, suoni_annotati):
    import json

    import GBUtils

    from finestra import Finestra

    cuffie = {"dispositivo": "Cuffie USB", "interfaccia": "Windows WASAPI"}
    (tmp_path / modulo.FILE_IMPOSTAZIONI).write_text(json.dumps({"scheda_audio": cuffie}), encoding="utf-8")
    chiamate = []
    # Una scheda che manca, o che non si applica, non si prova.
    prova = _ProvaFinta()
    monkeypatch.setattr(GBUtils.Acusticator, "riproduci", prova)

    def mancante(scelta, motore, avvio=False):
        chiamate.append((dict(scelta), avvio))
        return _esito(AUTOMATICA, automatica=True, mancante=True)

    monkeypatch.setattr(modulo.schede_audio, "applica", mancante)
    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        assert chiamate == [(cuffie, True)] and prova.prove == []
        righe = [_senza_ora(r) for r in f._righe]
        assert "La scheda audio scelta, Cuffie USB, non c'è: uso quella automatica, Altoparlanti (Realtek(R) Audio), WASAPI." in righe
        # La scelta resta, per quando le cuffie tornano.
        assert f.impostazioni["scheda_audio"] == cuffie
        assert f._riga_dell_impostazione("scheda_audio") == "Scheda audio: Cuffie USB, WASAPI, non c'è: uso quella automatica"
        f.Close(force=True)
    finally:
        f.Destroy()

    def guasta(scelta, motore, avvio=False):
        raise RuntimeError("PortAudio non risponde")

    monkeypatch.setattr(modulo.schede_audio, "applica", guasta)
    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        assert "Non riesco a usare la scheda audio scelta, Cuffie USB: PortAudio non risponde." in [_senza_ora(r) for r in f._righe]
        assert prova.prove == []
        f.Close(force=True)
    finally:
        f.Destroy()


def test_scheda_audio_all_avvio_che_non_si_apre(app, tmp_path, monkeypatch, suoni_annotati):
    import json

    import GBUtils

    from finestra import Finestra

    cuffie = {"dispositivo": "Cuffie USB", "interfaccia": "Windows WASAPI"}
    percorso = tmp_path / modulo.FILE_IMPOSTAZIONI
    percorso.write_text(json.dumps({"scheda_audio": cuffie}), encoding="utf-8")
    chiamate = []
    uscita = {**AUTOMATICA, "indice": 30, "dispositivo": "Cuffie USB"}

    def applica(scelta, motore, avvio=False):
        chiamate.append((dict(scelta), avvio))
        return _esito(uscita) if scelta else _esito(AUTOMATICA, automatica=True)

    monkeypatch.setattr(modulo.schede_audio, "applica", applica)
    monkeypatch.setattr(modulo.schede_audio, "in_uso", lambda elenco=None: AUTOMATICA)
    # Le cuffie ci sono, ma un altro programma le tiene: gli effetti non le aprono.
    prova = _ProvaFinta(aperta=False)
    monkeypatch.setattr(GBUtils.Acusticator, "riproduci", prova)
    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        assert prova.prove == [(modulo.SILENZIO_DI_PROVA, 2)]
        assert chiamate == [(cuffie, True), ({}, False)]
        assert "La scheda audio scelta, Cuffie USB, non si apre: uso quella automatica." in [_senza_ora(r) for r in f._righe]
        assert "errore" in suoni_annotati
        # La scelta resta, anche nel file, per quando le cuffie tornano libere.
        assert f.impostazioni["scheda_audio"] == cuffie
        assert f._riga_dell_impostazione("scheda_audio") == "Scheda audio: Cuffie USB, WASAPI, non si apre: uso quella automatica"
        f.Close(force=True)
    finally:
        f.Destroy()
    assert json.loads(percorso.read_text(encoding="utf-8"))["scheda_audio"] == cuffie
    # Quando si aprono, niente da dire e niente da cambiare.
    chiamate.clear()
    suoni_annotati.clear()
    prova.aperta = True
    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        assert chiamate == [(cuffie, True)] and len(prova.prove) == 2
        assert not any("Cuffie USB" in r for r in f._righe) and "errore" not in suoni_annotati
        assert f._riga_dell_impostazione("scheda_audio") == "Scheda audio: Cuffie USB, WASAPI"
        f.Close(force=True)
    finally:
        f.Destroy()
    # Con la scelta automatica, all'avvio non si prova niente.
    percorso.write_text(json.dumps({"scheda_audio": {}}), encoding="utf-8")
    chiamate.clear()
    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        assert chiamate == [({}, True)] and len(prova.prove) == 2
        f.Close(force=True)
    finally:
        f.Destroy()


# Velocita', tono, equalizzatore e dissolvenza, 1.55.0 (tappa 4, issue 15).


def test_velocita_e_tono_coi_tasti(finestra, suoni_annotati):
    righe = len(finestra._righe)
    assert _premi(finestra, "d") == "Velocità 1.05."
    assert _premi(finestra, "d") == "Velocità 1.1."
    assert finestra.motore.velocita == 1.1 and finestra.impostazioni["velocita"] == 1.1
    # La riga della velocita' si riscrive: una sola, per il display braille.
    assert len(finestra._righe) == righe + 1
    assert _premi(finestra, "a") == "Velocità 1.05."
    assert _premi(finestra, "s") == "Velocità 1, la normale."
    assert suoni_annotati[-4:] == ["velocita_su", "velocita_su", "velocita_giu", "velocita_normale"]
    assert finestra.motore.velocita == 1.0
    for _ in range(11):
        _tasto(finestra, "a")
    assert _ultima(finestra) == "Velocità già al minimo, 0.5." and suoni_annotati[-1] == "velocita_al_limite"
    assert finestra.motore.velocita == 0.5 and _salvate(finestra)["velocita"] == 0.5
    # Una velocita' fuori passo, scritta a mano nel file, arriva al limite.
    finestra.impostazioni["velocita"] = 1.98
    assert _premi(finestra, "d") == "Velocità 2."
    assert _premi(finestra, "d") == "Velocità già al massimo, 2."
    assert len(finestra._righe) == righe + 1
    # H alza e F abbassa, come D e A per la velocita' (1.58.1).
    assert _premi(finestra, "h") == "Tono +1 semitono."
    assert _premi(finestra, "h") == "Tono +2 semitoni."
    assert finestra.motore.tono == 2 and len(finestra._righe) == righe + 2
    assert _premi(finestra, "f") == "Tono +1 semitono."
    assert _premi(finestra, "g") == "Tono 0 semitoni, il normale."
    assert suoni_annotati[-4:] == ["tono_su", "tono_su", "tono_giu", "tono_normale"]
    for _ in range(13):
        _tasto(finestra, "f")
    assert _ultima(finestra) == "Tono già al minimo, -12 semitoni." and suoni_annotati[-1] == "tono_al_limite"
    assert finestra.motore.tono == -12 and _salvate(finestra)["tono"] == -12
    for _ in range(25):
        _tasto(finestra, "h")
    assert _ultima(finestra) == "Tono già al massimo, +12 semitoni." and finestra.motore.tono == 12
    # Le righe di stato stanno nei quaranta caratteri del display braille.
    assert all(len(_senza_ora(r)) <= 40 for r in finestra._righe[righe:])


def test_equalizzatore_coi_tasti(finestra, suoni_annotati, equalizzatore_annotato):
    righe = len(finestra._righe)
    # Si parte dalla prima banda, e U li' si ferma.
    assert _premi(finestra, "u") == "Banda 1, 60 Hz: 0 dB. È la prima."
    assert suoni_annotati[-1] == "banda_al_limite"
    assert _premi(finestra, "i") == "Banda 2, 150 Hz: 0 dB."
    assert _premi(finestra, "i") == "Banda 3, 400 Hz: 0 dB."
    assert _premi(finestra, "p") == "Banda 3, 400 Hz: +1 dB."
    # I suoni al volo: la banda scelta e il guadagno dato (1.58.0).
    assert equalizzatore_annotato == [("banda", 1), ("banda", 2), ("guadagno", 1)]
    assert finestra.motore.bande == [0, 0, 1, 0, 0, 0, 0]
    for _ in range(12):
        _tasto(finestra, "p")
    assert _ultima(finestra) == "Banda 3, 400 Hz: +12 dB, il massimo." and suoni_annotati[-1] == "guadagno_al_limite"
    assert _premi(finestra, "o") == "Banda 3, 400 Hz: +11 dB." and equalizzatore_annotato[-1] == ("guadagno", 11)
    for _ in range(4):
        _tasto(finestra, "i")
    assert _premi(finestra, "i") == "Banda 7, 12000 Hz: 0 dB. È l'ultima."
    for _ in range(13):
        _tasto(finestra, "o")
    assert _ultima(finestra) == "Banda 7, 12000 Hz: -12 dB, il minimo."
    assert finestra.motore.bande == [0, 0, 11, 0, 0, 0, -12] and _salvate(finestra)["bande"] == [0, 0, 11, 0, 0, 0, -12]
    assert _premi(finestra, "u") == "Banda 6, 6000 Hz: 0 dB." and equalizzatore_annotato[-1] == ("banda", 5)
    _tasto(finestra, "i")
    assert _premi(finestra, "è") == "Banda 7, 12000 Hz: 0 dB, azzerata." and suoni_annotati[-1] == "banda_azzerata"
    assert finestra.motore.bande == [0, 0, 11, 0, 0, 0, 0]
    assert _premi(finestra, "è", maiuscolo=True) == "Equalizzatore azzerato, tutte a 0 dB." and suoni_annotati[-1] == "bande_azzerate"
    assert finestra.motore.bande == [0] * 7 and _salvate(finestra)["bande"] == [0] * 7
    # Una riga sola, riscritta, e nei quaranta caratteri.
    assert len(finestra._righe) == righe + 1 and len(_ultima(finestra)) <= 40


def test_dissolvenza_coi_tasti(finestra, monkeypatch, suoni_annotati):
    assert finestra.motore.dissolvenza == 0
    assert _premi(finestra, "l") == "Dissolvenza accesa, 4 secondi."
    assert suoni_annotati[-1] == "dissolvenza_accesa" and finestra.motore.dissolvenza == 4.0
    assert _salvate(finestra)["dissolvenza"] == {"accesa": True, "secondi": 4.0}
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("2,5"))
    assert _premi(finestra, "l", maiuscolo=True) == "Dissolvenza accesa, 2.5 secondi."
    assert suoni_annotati[-2:] == ["domanda", "dissolvenza_durata"] and finestra.motore.dissolvenza == 2.5
    # Oltre i limiti si corregge, e la console lo dice.
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("20"))
    assert _premi(finestra, "l", maiuscolo=True) == "Dissolvenza accesa, 15 secondi. Dissolvenza: 20 è oltre il massimo, ho messo 15."
    assert finestra.motore.dissolvenza == 15
    # Un testo che non e' un numero di secondi lascia la durata com'era.
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("presto"))
    _tasto(finestra, "l", maiuscolo=True)
    assert suoni_annotati[-1] == "errore" and _ultima(finestra).startswith("Dissolvenza: presto non è un numero di secondi;")
    assert _ultima(finestra).endswith("La durata resta di 15 secondi.") and finestra.motore.dissolvenza == 15
    # Spenta, la durata resta per quando si riaccende; Maiuscolo con L la
    # cambia senza accenderla.
    assert _premi(finestra, "l") == "Dissolvenza spenta, 15 secondi."
    assert suoni_annotati[-1] == "dissolvenza_spenta" and finestra.motore.dissolvenza == 0
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("3"))
    assert _premi(finestra, "l", maiuscolo=True) == "Dissolvenza spenta, 3 secondi."
    assert finestra.motore.dissolvenza == 0
    assert _salvate(finestra)["dissolvenza"] == {"accesa": False, "secondi": 3.0}
    assert _premi(finestra, "l") == "Dissolvenza accesa, 3 secondi." and finestra.motore.dissolvenza == 3


def test_impostazioni_di_velocita_tono_equalizzatore_e_dissolvenza(finestra, monkeypatch, suoni_annotati):
    campo, lista = _cambia(finestra, monkeypatch, "velocita", "1.07")
    assert campo.aperture[0]["testo"] == "1" and "Adesso è 1." in campo.aperture[0]["istruzioni"]
    assert campo.aperture[0]["istruzioni"][-1] == modulo.REGOLA_DEL_DOLLARO
    assert finestra.motore.velocita == 1.05 and _salvate(finestra)["velocita"] == 1.05
    assert lista.righe["velocita"] == "Velocità: 1.05"
    assert _ultima(finestra) == "La velocità ora è 1.05. Velocità: 1.07 va a passi di 0.05, ho messo 1.05."
    campo, lista = _cambia(finestra, monkeypatch, "tono", "su", "+15")
    assert [a["testo"] for a in campo.aperture] == ["0", "su"]
    assert campo.aperture[1]["titolo"] == "Tono: su non è un numero; scrivi un numero intero da -12 a +12. Tono"
    assert finestra.motore.tono == 12 and _salvate(finestra)["tono"] == 12 and lista.righe["tono"] == "Tono: +12 semitoni"
    assert _ultima(finestra) == "Il tono ora è di +12 semitoni. Tono: +15 è oltre il massimo, ho messo +12."
    campo, _lista = _cambia(finestra, monkeypatch, "tono", "0")
    assert campo.aperture[0]["testo"] == "+12" and _ultima(finestra) == "Il tono ora è di 0 semitoni, il normale."
    campo, lista = _cambia(finestra, monkeypatch, "bande", "1 2 3", "0 0 +2 0 0 0 -3")
    assert campo.aperture[0]["testo"] == "0 0 0 0 0 0 0"
    assert campo.aperture[1]["titolo"].startswith("Equalizzatore: 1 2 3 sono 3 valori;")
    assert finestra.motore.bande == [0, 0, 2, 0, 0, 0, -3] and _salvate(finestra)["bande"] == [0, 0, 2, 0, 0, 0, -3]
    assert lista.righe["bande"] == "Equalizzatore: 0 0 +2 0 0 0 -3 dB"
    assert _ultima(finestra) == "L'equalizzatore ora è 0 0 +2 0 0 0 -3 dB."
    campo, _lista = _cambia(finestra, monkeypatch, "bande", "")
    assert campo.aperture[0]["testo"] == "0 0 +2 0 0 0 -3"
    assert finestra.motore.bande == [0] * 7 and _ultima(finestra) == "L'equalizzatore ora è piatto, tutte le bande a 0 dB."
    campo, lista = _cambia(finestra, monkeypatch, "dissolvenza", "2,5")
    assert campo.aperture[0]["testo"] == "spenta, 4 secondi"
    assert finestra.motore.dissolvenza == 2.5 and _salvate(finestra)["dissolvenza"] == {"accesa": True, "secondi": 2.5}
    assert lista.righe["dissolvenza"] == "Dissolvenza: accesa, 2.5 secondi"
    assert _ultima(finestra) == "La dissolvenza ora è accesa, 2.5 secondi."
    # No la spegne, e la durata resta per quando si riaccende.
    _cambia(finestra, monkeypatch, "dissolvenza", "no")
    assert finestra.motore.dissolvenza == 0 and finestra.impostazioni["dissolvenza"] == {"accesa": False, "secondi": 2.5}
    assert _ultima(finestra) == "La dissolvenza ora è spenta, 2.5 secondi."
    assert suoni_annotati.count("impostazione_cambiata") == 7


def test_avvio_con_velocita_tono_equalizzatore_e_dissolvenza_salvati(app, tmp_path):
    import json

    from finestra import Finestra

    percorso = tmp_path / modulo.FILE_IMPOSTAZIONI
    percorso.write_text(json.dumps({"velocita": 1.25, "tono": -2, "bande": [3, 0, 0, 0, 0, 0, -4], "dissolvenza": {"accesa": True, "secondi": 2.5}}),
        encoding="utf-8")
    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        assert (f.motore.velocita, f.motore.tono, f.motore.bande, f.motore.dissolvenza) == (1.25, -2, [3, 0, 0, 0, 0, 0, -4], 2.5)
        assert [_senza_ora(r) for r in f._righe][1] == "Velocità 1.25 e tono -2 semitoni: S e G li riportano al normale."
        assert f._riga_dell_impostazione("bande") == "Equalizzatore: +3 0 0 0 0 0 -4 dB"
        assert f._riga_dell_impostazione("dissolvenza") == "Dissolvenza: accesa, 2.5 secondi"
        f.Close(force=True)
    finally:
        f.Destroy()
    # Solo il tono fuori dal normale, e la dissolvenza spenta: il motore non la fa.
    percorso.write_text(json.dumps({"tono": 3, "dissolvenza": {"accesa": False, "secondi": 2.5}}), encoding="utf-8")
    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        assert f.motore.velocita == 1.0 and f.motore.dissolvenza == 0
        assert [_senza_ora(r) for r in f._righe][1] == "Tono +3 semitoni: G lo riporta al normale."
        f.Close(force=True)
    finally:
        f.Destroy()


def test_avvio_normale_non_dice_niente_di_velocita_e_tono(finestra):
    assert not any(r.startswith(("Velocità", "Tono")) for r in finestra._righe)
    assert (finestra.motore.velocita, finestra.motore.tono, finestra.motore.bande, finestra.motore.dissolvenza) == (1.0, 0, [0] * 7, 0)


def _motore_che_prepara(finestra, monkeypatch):
    """Il motore finto, che sa anche preparare il seguente."""
    suonati = _finto_motore(finestra, monkeypatch)
    preparati = []

    def prepara(percorso, sottobrano=None):
        preparati.append((os.path.basename(percorso), sottobrano))
        return True

    monkeypatch.setattr(finestra.motore, "prepara", prepara)
    return suonati, preparati


def _entra(finestra, percorso, sottobrano=None, sottobrani=None):
    """Il preparato entra, come lo fa entrare il motore: il motore passa a lui
    e poi avvisa la finestra."""
    finestra.motore._in_corso = percorso
    finestra.motore.sottobrano = sottobrano
    finestra.motore.sottobrani = sottobrani
    finestra._passaggio(percorso, sottobrano)


def test_passaggio_con_la_dissolvenza(finestra, monkeypatch, suoni_annotati):
    suonati, preparati = _motore_che_prepara(finestra, monkeypatch)
    rock, jazz = _playlist_di_prova(finestra, ("a.mp3", "b.mp3"), ("x.mp3", "y.mp3"))
    prima, seconda = finestra.archivio.playlist
    finestra._suona(prima, prima.brani[0])
    finestra._prepara_il_seguente()
    assert preparati == [("b.mp3", None)]
    # Il preparato entra: la coda passa a lui, senza suonarlo di nuovo, e la
    # plancia lo dice.
    _entra(finestra, prima.brani[1].percorso)
    assert finestra.coda.corrente is prima.brani[1] and suonati == [("a.mp3", None)]
    assert suoni_annotati[-1] == "brano_seguente_da_solo"
    assert _ultima(finestra) == f"In riproduzione: {prima.brani[1].percorso}, 2 di 2, playlist {prima.nome}."
    assert finestra.albero.GetItemText(_voce_di(finestra, rock, "b.mp3")) == "b.mp3, in riproduzione"
    # La plancia cambia dopo la preparazione: x diventa saltato, e al passaggio
    # si suona il giusto, y, che entra sfumando dal punto in cui si e'.
    finestra._prepara_il_seguente()
    assert preparati[-1] == ("x.mp3", None)
    seconda.brani[0].saltato = True
    _entra(finestra, seconda.brani[0].percorso)
    assert suonati[-1] == ("y.mp3", None) and finestra.coda.corrente is seconda.brani[1]
    assert suoni_annotati[-1] == "brano_seguente_da_solo"
    # Un avviso superato non conta: dopo la preparazione, B ha suonato altro.
    seconda.brani[0].saltato = False
    finestra._suona(prima, prima.brani[1])
    finestra._prepara_il_seguente()
    assert preparati[-1] == ("x.mp3", None)
    _tasto(finestra, "b")
    righe = list(finestra._righe)
    _entra(finestra, seconda.brani[0].percorso)
    assert finestra._righe == righe and finestra.coda.corrente is seconda.brani[0]
    # Senza piu' niente da suonare nella plancia, al passaggio il brano che
    # entra si scarta: il motore rimette quello che esce, che finisce da solo,
    # e solo alla sua fine vera la console dice Fine.
    annullati = []

    def annulla_il_passaggio():
        annullati.append(os.path.basename(finestra.motore.in_corso))
        finestra.motore._in_corso = prima.brani[1].percorso
        return True

    finestra._suona(prima, prima.brani[1])
    finestra._prepara_il_seguente()
    finestra.albero.Collapse(jazz)
    righe = list(finestra._righe)
    with monkeypatch.context() as patch:
        patch.setattr(finestra.motore, "annulla_il_passaggio", annulla_il_passaggio)
        _entra(finestra, seconda.brani[0].percorso)
    assert annullati == ["x.mp3"] and finestra._righe == righe
    assert finestra.motore.in_corso == prima.brani[1].percorso and finestra.coda.corrente is prima.brani[1]
    finestra.motore._in_corso = None
    finestra._brano_finito()
    assert suoni_annotati[-1] == "fine_playlist" and _ultima(finestra) == "Fine: davanti non c'è altro da suonare."
    # Se chi esce non c'e' piu', il motore ferma tutto e il Fine arriva subito.
    finestra.albero.Expand(jazz)
    finestra._suona(prima, prima.brani[1])
    finestra._prepara_il_seguente()
    finestra.albero.Collapse(jazz)
    _entra(finestra, seconda.brani[0].percorso)
    assert finestra.motore.in_corso is None and finestra.coda.corrente is prima.brani[1]
    assert suoni_annotati[-1] == "fine_playlist" and _ultima(finestra) == "Fine: davanti non c'è altro da suonare."
    # Alla fine della lista non c'e' niente da preparare.
    preparati.clear()
    finestra._suona(seconda, seconda.brani[1])
    finestra._prepara_il_seguente()
    assert not preparati


def test_passaggio_con_la_dissolvenza_nel_loop(finestra, monkeypatch, suoni_annotati):
    _suonati, preparati = _motore_che_prepara(finestra, monkeypatch)
    _playlist_di_prova(finestra, ("a.mp3", "b.mp3", "c.mp3"))
    pl = finestra.archivio.playlist[0]
    finestra.coda.loop_playlist, finestra.coda.punto_a, finestra.coda.punto_b = pl, pl.brani[0], pl.brani[1]
    finestra._suona(pl, pl.brani[1])
    finestra._prepara_il_seguente()
    assert preparati == [("a.mp3", None)]
    _entra(finestra, pl.brani[0].percorso)
    assert finestra.coda.corrente is pl.brani[0] and suoni_annotati[-1] == "ritorno_al_punto_a"


def test_riproduzione_casuale_con_la_dissolvenza_tiene_la_scelta(finestra, monkeypatch, suoni_annotati):
    suonati, preparati = _motore_che_prepara(finestra, monkeypatch)
    _playlist_di_prova(finestra, ("a.mp3", "b.mp3", "c.mp3", "d.mp3"))
    pl = finestra.archivio.playlist[0]
    finestra.impostazioni["casuale"] = True
    estratti = iter([2, 0, 1])
    finestra._a_caso = lambda candidati: candidati[next(estratti)]
    finestra._suona(pl, pl.brani[0])
    finestra._prepara_il_seguente()
    assert preparati == [("d.mp3", None)]
    # Al passaggio il ricontrollo trova la stessa scelta, senza estrarre di
    # nuovo: entra il preparato, e non si suona altro.
    _entra(finestra, pl.brani[3].percorso)
    assert finestra.coda.corrente is pl.brani[3] and suonati == [("a.mp3", None)]
    assert suoni_annotati[-1] == "brano_seguente_da_solo"
    # Se il brano scelto non si puo' piu' suonare, si estrae di nuovo.
    finestra._prepara_il_seguente()
    assert preparati[-1] == ("a.mp3", None)
    pl.brani[0].saltato = True
    _entra(finestra, pl.brani[0].percorso)
    assert suonati[-1] == ("c.mp3", None) and finestra.coda.corrente is pl.brani[2]


def test_passaggio_al_giusto_che_e_lo_stesso_file(finestra, monkeypatch, suoni_annotati):
    """Al ricontrollo il seguente giusto e' lo stesso file del preparato, in
    un'altra playlist: suona gia' dall'inizio, e si sposta solo la coda,
    senza farlo ripartire."""
    suonati, preparati = _motore_che_prepara(finestra, monkeypatch)
    _playlist_di_prova(finestra, ("a.mp3", "b.mp3"), ("b.mp3", "y.mp3"))
    prima, seconda = finestra.archivio.playlist
    finestra._suona(prima, prima.brani[0])
    finestra._prepara_il_seguente()
    assert preparati == [("b.mp3", None)]
    prima.brani[1].saltato = True
    _entra(finestra, prima.brani[1].percorso)
    assert suonati == [("a.mp3", None)]
    assert finestra.coda.playlist is seconda and finestra.coda.corrente is seconda.brani[0]
    assert suoni_annotati[-1] == "brano_seguente_da_solo"
    assert _ultima(finestra) == f"In riproduzione: {seconda.brani[0].percorso}, 1 di 2, playlist {seconda.nome}."


def _sid_finto(percorso, sottobrani, iniziale):
    """Un SID con la sola intestazione PSID, che basta per i sottobrani: il
    motore finto non lo suona."""
    intestazione = bytearray(0x7C)
    intestazione[0:4] = b"PSID"
    intestazione[0x04:0x06] = (2).to_bytes(2, "big")
    intestazione[0x06:0x08] = (0x7C).to_bytes(2, "big")
    intestazione[0x0E:0x10] = sottobrani.to_bytes(2, "big")
    intestazione[0x10:0x12] = iniziale.to_bytes(2, "big")
    percorso.write_bytes(bytes(intestazione) + b"\x00\x10\x60")
    return str(percorso)


def test_passaggio_al_sid_come_brano_in_un_altra_playlist(finestra, monkeypatch, tmp_path, suoni_annotati):
    """Il preparato e' un SID suonato come brano, che il motore fa entrare con
    il suo sottobrano iniziale; al ricontrollo il seguente giusto e' lo
    stesso SID, come brano, in un'altra playlist: e' gia' entrato, e si
    sposta solo la coda, senza suonarlo di nuovo. Prima la guardia vedeva
    un sottobrano diverso (nessuno contro l'iniziale) e lo richiedeva al
    motore, che lo fa ripartire da capo."""
    suonati, preparati = _motore_che_prepara(finestra, monkeypatch)
    sid = _sid_finto(tmp_path / "s.sid", sottobrani=3, iniziale=2)
    _playlist_di_prova(finestra, ("a.mp3", sid), (sid, "y.mp3"))
    prima, seconda = finestra.archivio.playlist
    finestra._suona(prima, prima.brani[0])
    finestra._prepara_il_seguente()
    assert preparati == [("s.sid", None)]
    prima.brani[1].saltato = True
    _entra(finestra, sid, 2, 3)
    assert suonati == [("a.mp3", None)]
    assert finestra.coda.playlist is seconda and finestra.coda.corrente is seconda.brani[0]
    assert suoni_annotati[-1] == "brano_seguente_da_solo"
    assert _ultima(finestra) == f"In riproduzione: {sid}, 1 di 2, playlist {seconda.nome}. Sottobrano 2 di 3."


@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_passaggio_con_la_dissolvenza_fra_i_sottobrani(finestra, monkeypatch, tmp_path, suoni_annotati):
    """Al passaggio il motore ha gia' il sottobrano che entra: il ricontrollo
    parte da quello che esce, o troverebbe il seguente del seguente."""
    import shutil

    suonati, preparati = _motore_che_prepara(finestra, monkeypatch)
    cartella = tmp_path / "sid"
    cartella.mkdir()
    shutil.copy(TURBO_OUTRUN, cartella)
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "sid", data={"tipo": "cartella", "percorso": str(cartella), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra.albero.Expand(nodo)
    voce_sid = next(finestra._figli(nodo))
    dati = finestra._dati(voce_sid)
    finestra.albero.Expand(voce_sid)
    finestra._suona(dati["playlist"], dati["brano"], sottobrano=3)
    finestra._prepara_il_seguente()
    assert preparati == [("Turbo_Outrun.sid", 4)]
    _entra(finestra, dati["brano"].percorso, 4, 12)
    assert suonati == [("Turbo_Outrun.sid", 3)]
    assert suoni_annotati[-1] == "brano_seguente_da_solo" and _ultima(finestra).endswith("Sottobrano 4 di 12.")


def test_passaggio_vero_con_la_dissolvenza(finestra, tmp_path, suoni_annotati):
    """Il motore vero, sull'uscita nulla: il seguente si prepara, entra
    sfumando e la coda lo segue; alla fine dell'ultimo la lista finisce."""
    a, b = tmp_path / "a.wav", tmp_path / "b.wav"
    _wav(a, secondi=2)
    _wav(b, secondi=2)
    finestra._aggiungi(None, [str(a), str(b)])
    pl = finestra.archivio.playlist[0]
    finestra.impostazioni["dissolvenza"] = {"accesa": True, "secondi": 0.5}
    finestra._applica_la_dissolvenza()
    finestra._suona(pl, pl.brani[0])
    assert _aspetta(lambda: finestra.coda.corrente is pl.brani[1], secondi=10)
    assert finestra.motore.in_corso == str(b)
    assert suoni_annotati[-1] == "brano_seguente_da_solo"
    assert _ultima(finestra) == f"In riproduzione: {b}, 2 di 2, playlist {pl.nome}."
    assert _aspetta(lambda: _ultima(finestra) == "Fine: davanti non c'è altro da suonare.", secondi=10)
    assert suoni_annotati[-1] == "fine_playlist"


def test_passaggio_vero_ricontrolla_la_plancia(finestra, tmp_path, suoni_annotati):
    """Il motore vero: preparato b, b diventa saltato prima del passaggio, e
    al passaggio si suona c, che entra sfumando al posto di b."""
    wav = [tmp_path / f"{nome}.wav" for nome in "abc"]
    for percorso in wav:
        _wav(percorso, secondi=2)
    nodo, = _playlist_di_prova(finestra, [str(p) for p in wav])
    pl = finestra.archivio.playlist[0]
    finestra.impostazioni["dissolvenza"] = {"accesa": True, "secondi": 0.5}
    finestra._applica_la_dissolvenza()
    finestra._suona(pl, pl.brani[0])
    assert _aspetta(lambda: finestra._preparato is not None, secondi=10)
    assert finestra._preparato[1] is pl.brani[1]
    pl.brani[1].saltato = True
    assert _aspetta(lambda: finestra.coda.corrente is pl.brani[2], secondi=10)
    assert _aspetta(lambda: finestra.motore.in_corso == str(wav[2]) and (finestra.motore.posizione or 0) > 0.2, secondi=10)
    assert suoni_annotati[-1] == "brano_seguente_da_solo"
    assert finestra.albero.GetItemText(_voce_di(finestra, nodo, "c.wav")).endswith("in riproduzione")


def test_passaggio_vero_senza_piu_un_seguente(finestra, monkeypatch, tmp_path, suoni_annotati):
    """Il motore vero: preparato b, b diventa saltato prima del passaggio, e
    davanti non c'e' altro. b si scarta, a arriva in fondo, e solo dopo la
    console dice Fine, come senza la dissolvenza."""
    wav = [tmp_path / f"{nome}.wav" for nome in "ab"]
    for percorso in wav:
        _wav(percorso, secondi=3)
    _playlist_di_prova(finestra, [str(p) for p in wav])
    pl = finestra.archivio.playlist[0]
    finestra.impostazioni["dissolvenza"] = {"accesa": True, "secondi": 1.0}
    finestra._applica_la_dissolvenza()
    passaggi = []
    passaggio = finestra._passaggio

    def spia(percorso, sottobrano):
        passaggi.append(os.path.basename(percorso))
        passaggio(percorso, sottobrano)

    monkeypatch.setattr(finestra, "_passaggio", spia)
    inizio = time.time()
    finestra._suona(pl, pl.brani[0])
    assert _aspetta(lambda: finestra._preparato is not None, secondi=10)
    pl.brani[1].saltato = True
    posizioni = []

    def finito():
        if finestra.motore.in_corso == str(wav[0]):
            posizioni.append(finestra.motore.posizione or 0)
        return _ultima(finestra) == "Fine: davanti non c'è altro da suonare."

    assert _aspetta(finito, secondi=10)
    # Il passaggio e' cominciato a 1,5 secondi dalla fine di a; prima Fine
    # arrivava li', e a si interrompeva di colpo.
    assert passaggi == ["b.wav"]
    assert time.time() - inizio > 2.3 and max(posizioni) > 2.3
    assert suoni_annotati[-1] == "fine_playlist" and finestra.coda.corrente is pl.brani[0]
    assert finestra.motore.in_corso is None and all(lettore.percorso is None for lettore in finestra.motore._lettori)


def test_con_la_dissolvenza_sfumano_stop_pausa_da_capo_e_marker(finestra, monkeypatch, tmp_path):
    """Con la dissolvenza accesa (1.58.0) V, C, X da capo e i salti ai marker
    del brano in corso chiedono la sfumatura al motore; spenta, restano
    netti. Il motore e' quello vero, su ao=null; qui si guarda cosa chiede
    la finestra."""
    pl, _voce = _brano_con_marker(finestra, tmp_path, [1.0, 3.0])
    finestra.motore.vai_a(0.5)
    finestra.motore.pausa(False)
    assert _aspetta(lambda: not finestra.motore.in_pausa and 0.4 < (finestra.motore.posizione or 0) < 0.9)
    chiamate = []
    vero_suona, vera_pausa, vero_stop = finestra.motore.suona, finestra.motore.pausa, finestra.motore.stop
    monkeypatch.setattr(finestra.motore, "suona", lambda *a, **k: chiamate.append(("suona", k.get("inizio"), k.get("sfuma_lo_stesso"))) or vero_suona(*a, **k))
    monkeypatch.setattr(finestra.motore, "vai_a", lambda s: chiamate.append(("vai_a", s)))
    monkeypatch.setattr(finestra.motore, "pausa", lambda valore=None, sfumando=False: chiamate.append(("pausa", sfumando)) or vera_pausa(valore, sfumando))
    monkeypatch.setattr(finestra.motore, "stop", lambda sfumando=False: chiamate.append(("stop", sfumando)) or vero_stop(sfumando))
    # Spenta: il marker e' un salto netto.
    _tasto(finestra, "y")
    assert chiamate[-1][0] == "vai_a"
    _premi(finestra, "l")
    assert finestra.motore.dissolvenza > 0
    _tasto(finestra, "y")
    assert chiamate[-1] == ("suona", 1.0, True)
    # X sul brano che suona lo fa ripartire da capo, sfumando.
    finestra._seleziona(next(finestra._figli(finestra._nodo_della_playlist(pl))))
    _tasto(finestra, "x")
    assert chiamate[-1] == ("suona", None, True)
    _tasto(finestra, "c")
    assert chiamate[-1] == ("pausa", True)
    _tasto(finestra, "v")
    assert chiamate[-1] == ("stop", True)
