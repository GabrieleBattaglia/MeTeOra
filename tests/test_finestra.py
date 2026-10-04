# MeTeOra, le prove della finestra principale, sul desktop nascosto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.55.0 le prove di velocita', tono, equalizzatore e dissolvenza, e del passaggio fra due brani (tappa 4, issue 15).

import datetime
import os
import re
import threading
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
    assert _etichette(finestra, finestra.albero.GetRootItem()) == ["Preferiti, brani: 0, totali: 0", "Playlist", "Questo PC", "Questa rete", "Apri file", "Impostazioni"]
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


def test_tasti_liberi_e_numpad(finestra, suoni_annotati):
    # Un tasto senza comando lo dice, con il suo suono, e non arriva
    # all'albero (tappa 9); il tastierino resta a NVDA, in silenzio.
    assert _premi(finestra, "'") == "Il tasto apostrofo non ha un comando." and suoni_annotati[-1] == "non_disponibile"
    assert _premi(finestra, "ì") == "Il tasto i accentata non ha un comando."
    assert _premi(finestra, "a", maiuscolo=True) == "Maiuscolo+A non ha un comando."
    righe, suonati = len(finestra._righe), len(suoni_annotati)
    _tasto(finestra, codice=wx.WXK_NUMPAD_ADD)
    assert len(finestra._righe) == righe and len(suoni_annotati) == suonati
    # Canc, con il suo codice 127, va all'albero come prima: non e' un
    # carattere senza comando.
    for maiuscolo in (False, True):
        evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
        evento.SetKeyCode(wx.WXK_DELETE)
        evento.SetUnicodeKey(wx.WXK_DELETE)
        evento.SetShiftDown(maiuscolo)
        assert finestra._esegui_il_tasto(evento) is False and evento.GetSkipped()
    assert len(finestra._righe) == righe and len(suoni_annotati) == suonati
    # I caratteri che arrivano fino all'albero, per esempio con AltGr, si fermano li'.
    for carattere, fermato in (("[", True), (" ", False)):
        evento = wx.KeyEvent(wx.wxEVT_CHAR)
        evento.SetUnicodeKey(ord(carattere))
        finestra._carattere_nell_albero(evento)
        assert evento.GetSkipped() is not fermato


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
    assert _ultima(finestra).startswith("Pausa")
    _tasto(finestra, "x")
    assert _ultima(finestra).startswith("Riprende")
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


def test_sottobrani_delle_console_nella_plancia(finestra, tmp_path):
    import chip

    if not chip.presente():
        pytest.skip("manca lib/libgme.dll: la mette strumenti/prepara_ambiente.py")
    from test_chip import nsf_di_prova

    cartella = tmp_path / "nes"
    cartella.mkdir()
    nsf_di_prova(cartella / "gioco.nsf")
    (cartella / "gioco.m3u").write_text("gioco.nsf::NSF,2,Il secondo,0:42,,3\ngioco.nsf::NSF,1,,1:05,,\n", encoding="cp1252")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "nes", data={"tipo": "cartella", "percorso": str(cartella), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra.albero.Expand(nodo)
    voce_file = next(finestra._figli(nodo))
    assert finestra.albero.GetItemText(voce_file).startswith("gioco.nsf")
    assert finestra.albero.ItemHasChildren(voce_file)
    finestra.albero.Expand(voce_file)
    # Il titolo del brano, se il .m3u lo dice; la durata comprende la dissolvenza.
    assert _etichette(finestra, voce_file) == ["Sottobrano 1 di 2, Il secondo, 0:45", "Sottobrano 2 di 2, 1:13"]


def test_il_fuoco_resta_sul_sottobrano_dopo_una_ricostruzione(finestra, tmp_path):
    import chip

    if not chip.presente():
        pytest.skip("manca lib/libgme.dll: la mette strumenti/prepara_ambiente.py")
    from test_chip import nsf_di_prova

    finestra._aggiungi(None, [nsf_di_prova(tmp_path / "gioco.nsf"), str(tmp_path / "altro.mp3")])
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    gioco, altro = list(finestra._figli(nodo))
    finestra.albero.Expand(gioco)
    finestra._seleziona(list(finestra._figli(gioco))[1])
    # F4 su un altro brano rifa' il ramo Playlist: il fuoco torna sul
    # sottobrano, non sul suo file (tappa 9).
    finestra._ai_preferiti(finestra._dati(altro)["brano"])
    dati = finestra._dati(finestra._voce_corrente())
    assert dati["tipo"] == "sottobrano" and dati["numero"] == 2


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
    assert _ultima(finestra) == "Filtro di Playlist: rock -tre. Passa 1 brano su 3."
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
    assert list(voci) == ["Riproduci", "Filtro", "Togli il filtro", "Rinomina", "Elimina", "Leggi i dettagli"]
    voci["Togli il filtro"]()
    assert _ultima(finestra).startswith("Filtro di Playlist svuotato")
    assert pl.filtro == ""
    assert [n for n, _a in finestra._voci_del_menu(finestra._dati(finestra.nodo_preferiti))] == ["Riproduci", "Filtro", "Leggi i dettagli"]
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
    assert _ultima(finestra) == "Riproduzione casuale accesa: una volta per brano, poi ricomincia."
    _tasto(finestra, "n", maiuscolo=True)
    assert finestra.impostazioni["casuale"] is False and _salvate(finestra)["casuale"] is False
    assert suoni_annotati[-1] == "casuale_spento"
    assert _ultima(finestra) == "Riproduzione casuale spenta: a fine brano si va avanti in ordine."


def test_riproduzione_casuale_nella_plancia(finestra, monkeypatch, suoni_annotati):
    suonati = _finto_motore(finestra, monkeypatch)
    rock, _jazz = _playlist_di_prova(finestra, ("a.mp3", "b.mp3", "c.mp3"), ("x.mp3", "y.mp3"))
    prima, seconda = finestra.archivio.playlist
    finestra.impostazioni["casuale"] = True
    finestra.impostazioni["modello_casuale"] = "totale"
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
    # Dalla 1.74.0 anche B sceglie a caso, nello stesso campo, con il suo suono.
    _tasto(finestra, "b")
    assert scelte[-1] == ["y.mp3"] and suonati[-1] == ("y.mp3", None) and suoni_annotati[-1] == "successivo"


def test_riproduzione_casuale_nella_lista_e_nel_loop(finestra, monkeypatch, suoni_annotati):
    suonati = _finto_motore(finestra, monkeypatch)
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("a.mp3", "b.mp3", "c.mp3", "d.mp3")])
    pl = finestra.archivio.playlist[0]
    finestra.impostazioni["casuale"] = True
    finestra.impostazioni["modello_casuale"] = "totale"
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


def test_con_il_casuale_b_sceglie_a_caso_e_z_torna_indietro(finestra, monkeypatch, suoni_annotati):
    # 1.74.0, Gabriele: con la riproduzione casuale accesa B sceglie a caso,
    # con il mazzo, e Z torna ai brani suonati prima; dopo Z, B e
    # l'avanzamento automatico ripercorrono la storia prima di scegliere.
    pl, suonati, scelte = _mazzo_di_quattro(finestra, monkeypatch, "a_giro")
    finestra._suona(pl, pl.brani[0])
    _tasto(finestra, "b")
    _tasto(finestra, "b")
    assert scelte == [["b.mp3", "c.mp3", "d.mp3"], ["c.mp3", "d.mp3"]]
    assert [s[0] for s in suonati] == ["a.mp3", "b.mp3", "c.mp3"]
    _tasto(finestra, "z")
    assert suonati[-1] == ("b.mp3", None) and suoni_annotati[-1] == "precedente"
    _tasto(finestra, "z")
    assert suonati[-1] == ("a.mp3", None)
    _tasto(finestra, "z")
    assert _ultima(finestra) == "È il primo brano suonato a caso." and suoni_annotati[-1] == "nessun_altro_brano" and len(suonati) == 5
    # Avanti nella storia, senza nuove scelte: con B e a fine brano.
    _tasto(finestra, "b")
    assert suonati[-1] == ("b.mp3", None)
    finestra._brano_finito()
    assert suonati[-1] == ("c.mp3", None) and len(scelte) == 2
    # In fondo alla storia B torna a scegliere, dal mazzo: resta d.
    _tasto(finestra, "b")
    assert scelte[-1] == ["d.mp3"] and suonati[-1] == ("d.mp3", None)
    # Tornati indietro, un brano scelto da chi ascolta fa dimenticare il resto della storia.
    _tasto(finestra, "z")
    _tasto(finestra, "z")
    assert suonati[-1] == ("b.mp3", None)
    finestra._suona(pl, pl.brani[3])
    _tasto(finestra, "z")
    assert suonati[-1] == ("b.mp3", None)
    _tasto(finestra, "b")
    assert suonati[-1] == ("d.mp3", None)
    # Riaccendere il casuale fa ricominciare la storia da cio' che suona.
    finestra.motore._in_corso = pl.brani[3].percorso
    _tasto(finestra, "n", maiuscolo=True)
    _tasto(finestra, "n", maiuscolo=True)
    _tasto(finestra, "z")
    assert _ultima(finestra) == "È il primo brano suonato a caso."
    # A casuale spento Z e B vanno in ordine.
    _tasto(finestra, "n", maiuscolo=True)
    _tasto(finestra, "z")
    assert suonati[-1] == ("c.mp3", None)


def test_con_il_casuale_b_dice_la_fine_del_mazzo(finestra, monkeypatch, suoni_annotati):
    pl, suonati, _scelte = _mazzo_di_quattro(finestra, monkeypatch, "una_volta")
    finestra._suona(pl, pl.brani[0])
    for _ in range(3):
        _tasto(finestra, "b")
    assert [s[0] for s in suonati] == ["a.mp3", "b.mp3", "c.mp3", "d.mp3"]
    _tasto(finestra, "b")
    assert _ultima(finestra) == "Ogni brano del mazzo ha suonato una volta: B ricomincia un giro nuovo." and len(suonati) == 4
    _tasto(finestra, "b")
    assert len(suonati) == 5 and suonati[-1][0] != "d.mp3"


def _mazzo_di_quattro(finestra, monkeypatch, modello):
    """Una playlist chiusa di quattro brani, la riproduzione casuale accesa
    con il modello dato, e la scelta che prende sempre il primo candidato."""
    suonati = _finto_motore(finestra, monkeypatch)
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("a.mp3", "b.mp3", "c.mp3", "d.mp3")])
    finestra.impostazioni["casuale"] = True
    finestra.impostazioni["modello_casuale"] = modello
    scelte = []

    def a_caso(candidati):
        scelte.append(_nomi(candidati))
        return candidati[0]

    finestra._a_caso = a_caso
    return finestra.archivio.playlist[0], suonati, scelte


def test_riproduzione_casuale_una_volta_per_brano_poi_si_ferma(finestra, monkeypatch, suoni_annotati):
    pl, suonati, scelte = _mazzo_di_quattro(finestra, monkeypatch, "una_volta")
    finestra._suona(pl, pl.brani[0])
    for _ in range(3):
        finestra._brano_finito()
    # Ogni brano esce dal mazzo appena suona.
    assert scelte == [["b.mp3", "c.mp3", "d.mp3"], ["c.mp3", "d.mp3"], ["d.mp3"]]
    assert [s[0] for s in suonati] == ["a.mp3", "b.mp3", "c.mp3", "d.mp3"]
    # L'ultimo brano e' finito davvero: il motore non ha piu' niente.
    finestra.motore._in_corso = None
    finestra._brano_finito()
    assert _ultima(finestra) == "Fine: ogni brano del mazzo ha suonato una volta." and suoni_annotati[-1] == "fine_playlist"
    assert len(suonati) == 4
    # Il mazzo si e' rifatto: il brano scelto da chi ascolta esce, gli altri ci sono tutti.
    finestra._suona(pl, pl.brani[2])
    finestra._brano_finito()
    assert scelte[-1] == ["a.mp3", "b.mp3", "d.mp3"] and suonati[-1] == ("a.mp3", None)


def test_riproduzione_casuale_una_volta_per_brano_poi_ricomincia(finestra, monkeypatch, suoni_annotati):
    pl, suonati, scelte = _mazzo_di_quattro(finestra, monkeypatch, "a_giro")
    finestra._suona(pl, pl.brani[3])
    for _ in range(4):
        finestra._brano_finito()
    # Finito il mazzo si rimescola, e l'ultimo brano non torna subito.
    assert scelte == [["a.mp3", "b.mp3", "c.mp3"], ["b.mp3", "c.mp3"], ["c.mp3"], ["a.mp3", "b.mp3", "d.mp3"]]
    assert [s[0] for s in suonati] == ["d.mp3", "a.mp3", "b.mp3", "c.mp3", "a.mp3"]
    # Riaccendere la riproduzione casuale rifa' il mazzo: esce solo cio' che suona.
    _tasto(finestra, "n", maiuscolo=True)
    _tasto(finestra, "n", maiuscolo=True)
    finestra.motore._in_corso = pl.brani[0].percorso
    finestra._ricomincia_il_mazzo()
    finestra._brano_finito()
    assert scelte[-1] == ["b.mp3", "c.mp3", "d.mp3"]


def test_impostazioni_modello_della_riproduzione_casuale(finestra, monkeypatch, suoni_annotati):
    scelta = _SceltaFinta(0)
    monkeypatch.setattr(modulo, "FinestraScelta", scelta)
    lista = _ListaFinta()
    finestra._cambia_impostazione("modello_casuale", lista)
    titolo, righe, partenza = scelta.aperture[0]
    assert titolo == "Modello della riproduzione casuale" and partenza == 2
    assert righe == [
        "Casualità totale: ogni volta un brano qualsiasi, mai lo stesso due volte di fila",
        "Una volta per brano, poi si ferma: ogni brano suona una volta, poi la riproduzione finisce",
        "Una volta per brano, poi ricomincia: ogni brano suona una volta, poi si rimescola e si ricomincia",
    ]
    assert finestra.impostazioni["modello_casuale"] == "totale" and _salvate(finestra)["modello_casuale"] == "totale"
    assert lista.righe["modello_casuale"] == "Modello della riproduzione casuale: casualità totale"
    assert _ultima(finestra) == "La riproduzione casuale ora va con il modello casualità totale." and suoni_annotati[-1] == "impostazione_cambiata"
    _tasto(finestra, "n", maiuscolo=True)
    assert _ultima(finestra) == "Riproduzione casuale accesa: casualità totale."
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaFinta(None))
    finestra._cambia_impostazione("modello_casuale", lista)
    assert _ultima(finestra) == "Modello della riproduzione casuale non cambiato." and finestra.impostazioni["modello_casuale"] == "totale"


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
    altri = list(finestra._figli(dentro))[-1]
    finestra._seleziona(altri)
    # Un aggiornamento della ricerca non ricrea la voce, e il fuoco resta su
    # di lei (tappa 9).
    finestra._riempi_gruppo(dentro)
    assert list(finestra._figli(dentro))[-1] == altri and finestra._voce_corrente() == altri
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


def test_la_ricerca_ovunque_cerca_anche_in_rete(finestra, monkeypatch, suoni_annotati, tmp_path):
    # 1.73.0: Ctrl con la barra rovesciata passa alla ricerca le radici di
    # rete aggiunte a mano, per ultime; una ricerca in un ramo no. Alla fine la console dice
    # quali non hanno risposto, con il nome di Questa rete.
    from filtro import Filtro

    class RicercaFinta:
        def __init__(self, filtro, brani, schedario, avvisa=None, unita=None, rete=(), lettere_di_rete=False):
            self.rete, self.unita, self.lettere_di_rete = list(rete), unita, lettere_di_rete
            self.finita, self.fermata, self.senza_risposta, self.cartelle_mute = False, False, [], []

        def avvia(self):
            pass

        def ferma(self):
            self.fermata = True

        def quanti(self):
            return 0

        def pezzo(self, _inizio, _fine):
            return []

    monkeypatch.setattr(modulo, "Ricerca", RicercaFinta)
    monkeypatch.setattr(modulo.questa_rete, "percorsi_salvati", lambda: [("La box", "\\\\box\\dati")])
    finestra.impostazioni["percorsi_di_rete"] = ["\\\\nas\\musica"]
    finestra._avvia_ricerca("rock", Filtro("rock"))
    # Le condivisioni intere salvate in Windows no: solo i percorsi aggiunti a mano.
    assert finestra._ricerca.unita is None and finestra._ricerca.rete == ["\\\\nas\\musica"] and finestra._ricerca.lettere_di_rete
    assert _ultima(finestra) == "Cerco rock nelle playlist, nei dischi e in rete. I Risultati si riempiono mentre cerco."
    # Allo schedario non vanno i file delle radici mute, che lo terrebbero fermo.
    chiesti = []
    monkeypatch.setattr(finestra.schedario, "chiedi", chiesti.extend)
    finestra.risultati.brani[:] = [Brano(os.path.join(str(tmp_path), "rock.mp3")), Brano("\\\\nas\\musica\\rock.mp3")]
    finestra._ricerca.finita, finestra._ricerca.senza_risposta = True, ["\\\\box\\dati", "\\\\nas\\musica"]
    finestra._ricerca.cartelle_mute = ["\\\\box\\dati\\uno", "\\\\box\\dati\\due"]
    finestra._risultati_arrivati()
    assert _ultima(finestra) == ("Ricerca di rock finita: 2 risultati. In rete non hanno risposto: La box, \\\\nas\\musica. "
        "In rete 2 cartelle non hanno risposto, e la ricerca è andata avanti senza.")
    assert chiesti == [os.path.join(str(tmp_path), "rock.mp3")]
    finestra._avvia_ricerca("rock", Filtro("rock"), unita=[str(tmp_path)], dove="in Musica")
    assert finestra._ricerca.rete == [] and not finestra._ricerca.lettere_di_rete


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


class _DialogoAnnullato(_DialogoFinto):
    """Un campo, o un dialogo, chiuso con Esc."""

    def __init__(self):
        super().__init__("")

    def ShowModal(self):
        return wx.ID_CANCEL


def test_esc_nei_campi_lo_dice_con_il_suo_suono(finestra, monkeypatch, suoni_annotati):
    # Tappa 9: un campo chiuso con Esc non esce muto.
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoAnnullato())
    monkeypatch.setattr(modulo, "FinestraFiltro", _DialogoAnnullato())
    monkeypatch.setattr(modulo, "DialogoDiFile", _FileFinto(None))
    finestra._comando_nuova_playlist()
    pl = finestra.archivio.playlist[0]
    for comando, frase in (
            (lambda: _tasto(finestra, "m", maiuscolo=True), "Passo del volume non cambiato."),
            (lambda: _tasto(finestra, "q", maiuscolo=True), "Il salto indietro resta di 10 secondi."),
            (lambda: _tasto(finestra, "l", maiuscolo=True), "La durata della dissolvenza resta di 4 secondi."),
            (lambda: finestra._rinomina(pl), "Nome della playlist non cambiato."),
            (finestra._comando_apri_file, "Nessun file aperto."),
            (finestra._comando_aggiungi_percorso_di_rete, "Nessun percorso aggiunto."),
            (finestra._comando_cerca_in_console, "Ricerca nella console annullata."),
            (lambda: finestra._modifica_filtro(pl), "Filtro non cambiato.")):
        comando()
        assert _ultima(finestra) == frase and suoni_annotati[-2:] == ["domanda", "annullamento"]
    # Invio nella console senza una ricerca lo dice.
    evento = wx.KeyEvent(wx.wxEVT_KEY_DOWN)
    evento.SetKeyCode(wx.WXK_RETURN)
    finestra._tasto_nella_console(evento)
    assert _ultima(finestra) == "Nella console non c'è una ricerca: la barra rovesciata ne apre una." and suoni_annotati[-1] == "non_disponibile"


def test_le_conferme_hanno_si_e_no_e_si_chiudono_con_esc(finestra, monkeypatch, suoni_annotati):
    aperte = []

    class Conferma(_DialogoFinto):
        def __init__(self, genitore, domanda, titolo):
            aperte.append((genitore, domanda, titolo))
            super().__init__("")

        def ShowModal(self):
            return wx.ID_NO

    monkeypatch.setattr(modulo, "DialogoConferma", Conferma)
    assert finestra._conferma("Eliminare?", "Elimina playlist") is False
    assert aperte == [(finestra, "Eliminare?", "Elimina playlist")] and suoni_annotati[-1] == "domanda"
    # Un No a Elimina playlist ha il suono dell'annullamento.
    finestra._comando_nuova_playlist()
    finestra._elimina_playlist(finestra.archivio.playlist[0])
    assert _ultima(finestra) == "Eliminazione annullata." and suoni_annotati[-1] == "annullamento" and finestra.archivio.playlist


def test_una_voce_senza_menu_lo_dice(finestra, suoni_annotati):
    comando = next(v for v in finestra._figli(finestra.nodo_playlist) if finestra._dati(v).get("tipo") == "comando")
    finestra._menu(comando)
    assert _ultima(finestra) == "Nuova playlist non ha un menu: Invio lo esegue." and suoni_annotati[-1] == "non_disponibile"


def test_un_suono_aspetta_la_fine_di_quello_prima(finestra, monkeypatch, suoni_annotati):
    # Due suoni nello stesso istante si fondono: la domanda dopo un errore
    # aspetta che l'errore finisca (tappa 9).
    rimandati = []
    attesa = [0.2]
    monkeypatch.setattr(modulo.suoni, "attesa", lambda: attesa[0])
    monkeypatch.setattr(modulo.wx, "CallLater", lambda millesimi, funzione, *argomenti: rimandati.append((millesimi, funzione, argomenti)))
    finestra._domanda()
    assert "domanda" not in suoni_annotati and rimandati[0][0] == 230
    # Allo scadere si guarda di nuovo, e senza altri suoni parte.
    attesa[0] = 0.0
    _millesimi, funzione, argomenti = rimandati.pop()
    funzione(*argomenti)
    assert suoni_annotati[-1] == "domanda"
    # Se intanto il campo ha avuto un esito, per esempio Esc, la domanda
    # rimandata non suona piu'.
    attesa[0] = 0.2
    finestra._domanda()
    attesa[0] = 0.0
    finestra._annullato("Filtro non cambiato.")
    _millesimi, funzione, argomenti = rimandati.pop()
    funzione(*argomenti)
    assert suoni_annotati[-2:] == ["domanda", "annullamento"]


def test_v_ferma_il_brano_che_parte_dopo_un_errore(finestra, monkeypatch, suoni_annotati):
    suonati = _finto_motore(finestra, monkeypatch)
    rimandati = []
    monkeypatch.setattr(modulo.suoni, "attesa", lambda: 0.3)
    monkeypatch.setattr(modulo.wx, "CallLater", lambda millesimi, funzione, *argomenti: rimandati.append((funzione, argomenti)))
    _playlist_di_prova(finestra, ("a.mp3", "b.mp3"))
    pl = finestra.archivio.playlist[0]
    finestra.coda.imposta(pl, pl.brani[0])
    finestra._brano_in_errore(pl.brani[0].percorso)
    assert suoni_annotati[-1] == "errore" and not suonati
    # V prima della fine del suono dell'errore: il brano seguente non parte.
    finestra._comando_stop()
    assert _ultima(finestra) == "Stop: il brano seguente non parte." and suoni_annotati[-1] == "stop"
    funzione, argomenti = rimandati.pop(0)
    funzione(*argomenti)
    assert not suonati


def test_all_uscita_quello_che_non_si_salva_lo_dice_una_finestra(finestra, monkeypatch, suoni_annotati):
    messaggi = []
    monkeypatch.setattr(modulo.wx, "MessageBox", lambda testo, titolo, stile, genitore: messaggi.append((testo, titolo)))

    def guasto():
        raise OSError(28, "Spazio esaurito")

    monkeypatch.setattr(finestra.impostazioni, "salva", guasto)
    _tasto(finestra, codice=wx.WXK_ESCAPE)
    assert finestra._chiusa
    assert messaggi == [("MeTeOra non è riuscito a salvare le impostazioni: Spazio esaurito.", "MeTeOra, uscita")]
    assert suoni_annotati[-2:] == ["errore", "uscita"]


def _wav_di_prova(percorso, secondi=4):
    """Un WAV di silenzio, stereo a 48 kHz."""
    import wave

    with wave.open(str(percorso), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(bytes(4 * 48000 * secondi))
    return str(percorso)


def test_rinomina_file(finestra, monkeypatch, suoni_annotati, tmp_path):
    import json

    cartella = tmp_path / "Musica"
    cartella.mkdir()
    canzone = _wav_di_prova(cartella / "canzone.wav", 1)
    (cartella / "canzone.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nCiao\n", encoding="utf-8")
    (cartella / "canzone.it.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nCiao\n", encoding="utf-8")
    (cartella / "canzone.flac").write_bytes(b"")
    finestra._aggiungi(None, [canzone])
    pl = finestra.archivio.playlist[0]
    brano = pl.brani[0]
    k = finestra._chiave_dei_marker(canzone, leggi=True)
    finestra.marcatori.aggiungi(k, 0.5, canzone, finestra._durata_dei_marker(canzone)[0])
    # Esc, e lo stesso nome, non cambiano niente.
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoAnnullato())
    finestra._rinomina_file(brano)
    assert _ultima(finestra) == "Nome del file non cambiato." and suoni_annotati[-1] == "annullamento"
    # Un carattere che Windows non accetta, o un nome gia' preso, si rifiutano.
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("canzone: bis"))
    finestra._rinomina_file(brano)
    assert _ultima(finestra) == "Nel nome di un file non possono stare: due punti. Il nome resta canzone.wav." and suoni_annotati[-1] == "errore"
    _wav_di_prova(cartella / "occupato.wav", 1)
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("occupato"))
    finestra._rinomina_file(brano)
    assert _ultima(finestra) == f"In {cartella} c'è già occupato.wav: il nome resta canzone.wav."
    # L'estensione scritta per abitudine non si raddoppia; i sottotitoli
    # seguono il file, l'altro audio con lo stesso nome no.
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("Ballata.WAV"))
    finestra._rinomina_file(brano)
    nuovo = str(cartella / "Ballata.wav")
    assert _ultima(finestra) == "canzone.wav ora si chiama Ballata.wav. Con lui anche Ballata.it.srt, Ballata.srt." and suoni_annotati[-1] == "file_rinominato"
    assert sorted(os.listdir(cartella)) == ["Ballata.it.srt", "Ballata.srt", "Ballata.wav", "canzone.flac", "occupato.wav"]
    # La playlist, lo schedario e i marker seguono il nome nuovo.
    with open(finestra.archivio.percorso, encoding="utf-8") as f:
        salvate = f.read()
    assert brano.percorso == nuovo and json.dumps(nuovo)[1:-1] in salvate and json.dumps(canzone)[1:-1] not in salvate
    assert finestra.schedario.scheda(nuovo) is not None and finestra.schedario.scheda(canzone) is None
    assert [m["tempo"] for m in finestra.marcatori.elenco(finestra._chiave_dei_marker(nuovo))] == [0.5]
    # Un file che non c'e' piu' lo dice.
    os.remove(nuovo)
    finestra._rinomina_file(brano)
    assert _ultima(finestra) == f"Non trovo {nuovo} sul disco."


def test_rinomina_un_file_che_suona(finestra, monkeypatch, suoni_annotati, tmp_path):
    # mpv apre i file lasciando che Windows li rinomini: il brano continua,
    # con il nome nuovo. Se invece il file e' tenuto aperto, MeTeOra lo
    # lascia, lo rinomina e lo fa ripartire dal suo punto, in pausa se era
    # in pausa.
    canzone = _wav_di_prova(tmp_path / "canzone.wav", 6)
    finestra._aggiungi(None, [canzone])
    pl = finestra.archivio.playlist[0]
    finestra._suona(pl, pl.brani[0])
    fine = time.monotonic() + 10
    while time.monotonic() < fine and not (finestra.motore.posizione or 0) > 0.3:
        wx.Yield()
        time.sleep(0.02)
    finestra.motore.pausa(True)
    prima = finestra.motore.posizione
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("rinominata"))
    finestra._rinomina_file(pl.brani[0])
    nuovo = str(tmp_path / "rinominata.wav")
    assert os.path.isfile(nuovo) and not os.path.exists(canzone)
    assert _ultima(finestra) == "canzone.wav ora si chiama rinominata.wav."
    assert finestra.motore.in_corso == nuovo and finestra.motore.in_pausa
    fine = time.monotonic() + 10
    while time.monotonic() < fine and finestra.motore.posizione is None:
        wx.Yield()
        time.sleep(0.02)
    assert finestra.motore.posizione == pytest.approx(prima, abs=0.3)
    # Il file tenuto aperto: il primo tentativo fallisce come con Windows.
    vero_rename, tentativi, lasciati = os.rename, [], []
    lascia = finestra.motore.lascia_il_file

    def rename(vecchio, nuovo):
        tentativi.append(vecchio)
        if len(tentativi) == 1:
            raise PermissionError(32, "Il file è in uso da un altro processo")
        vero_rename(vecchio, nuovo)

    monkeypatch.setattr(modulo.os, "rename", rename)
    monkeypatch.setattr(finestra.motore, "lascia_il_file", lambda percorso: lasciati.append(percorso) or lascia(percorso))
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("di nuovo"))
    finestra._rinomina_file(pl.brani[0])
    monkeypatch.setattr(modulo.os, "rename", vero_rename)
    ancora = str(tmp_path / "di nuovo.wav")
    assert lasciati == [nuovo] and os.path.isfile(ancora) and _ultima(finestra) == "rinominata.wav ora si chiama di nuovo.wav."
    assert finestra.motore.in_corso == ancora and finestra.motore.in_pausa
    fine = time.monotonic() + 10
    while time.monotonic() < fine and finestra.motore.posizione is None:
        wx.Yield()
        time.sleep(0.02)
    assert finestra.motore.posizione == pytest.approx(prima, abs=0.3)
    finestra.motore.stop()


def test_i_tag_con_f11_e_il_sottomenu(finestra, monkeypatch, suoni_annotati, tmp_path):
    import tag

    canzone = _wav_di_prova(tmp_path / "canzone.wav", 1)
    altra = _wav_di_prova(tmp_path / "altra.wav", 1)
    finestra._aggiungi(None, [canzone, altra])
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    prima, seconda = list(finestra._figli(nodo))
    finestra._seleziona(prima)
    # F11 scrive i tag nella console.
    _tasto(finestra, codice=wx.WXK_F11)
    righe = [_senza_ora(r) for r in finestra._righe]
    assert "Tag di canzone.wav." in righe and "Titolo: vuoto." in righe and suoni_annotati[-1] == "tag_letti"
    # Il menu del brano ha Leggi i tag e il sottomenu Tag, una voce per tag.
    voci = dict(finestra._voci_del_menu(finestra._dati(prima)))
    assert "Leggi i tag" in voci and voci["Tag"][0][0] == "Titolo: vuoto"
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("Ballata & co"))
    voci["Tag"][0][1]()
    assert _ultima(finestra) == "Titolo di canzone.wav: Ballata & co." and suoni_annotati[-2:] == ["domanda", "tag_cambiato"]
    assert finestra.schedario.scheda(canzone)["tag"]["titolo"] == "Ballata & co"
    voci = dict(finestra._voci_del_menu(finestra._dati(prima)))
    assert voci["Tag"][0][0] == "Titolo: Ballata && co"
    # Un anno scritto male non si scrive; lo stesso valore e Esc non cambiano niente.
    anno = next(azione for etichetta, azione in voci["Tag"] if etichetta.startswith("Anno"))
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("99"))
    anno()
    assert _ultima(finestra).startswith("99 non è un anno") and _ultima(finestra).endswith("Il tag Anno resta com'era.") and suoni_annotati[-1] == "errore"
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("Ballata & co"))
    voci["Tag"][0][1]()
    assert _ultima(finestra) == "Tag Titolo non cambiato." and suoni_annotati[-1] == "annullamento"
    # Il campo vuoto cancella il tag.
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto(""))
    voci["Tag"][0][1]()
    assert _ultima(finestra) == "Tag Titolo cancellato da canzone.wav." and suoni_annotati[-1] == "tag_cancellato"
    assert finestra.schedario.scheda(canzone)["tag"].get("titolo") is None
    # Piu' file insieme: dove i valori sono diversi la voce lo dice, e il
    # valore nuovo va in tutti.
    tag.scrivi(canzone, "album", "Uno")
    finestra.albero.SelectItem(seconda)
    # Il menu della selezione non legge i tag mentre si apre: li legge la voce scelta.
    voci = dict(finestra._voci_del_menu_della_selezione())
    assert voci["Leggi i tag"] == finestra._comando_leggi_i_tag and voci["Modifica i tag"] == finestra._comando_modifica_i_tag
    album = next((etichetta, azione) for etichetta, azione in finestra._sottomenu_dei_tag(finestra._file_dei_tag()) if etichetta.startswith("Album"))
    assert album[0] == "Album: valori diversi"
    # Svuotare un tag con valori diversi chiede conferma: con No resta.
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto(""))
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo, genitore=None: False)
    album[1]()
    assert _ultima(finestra) == "Tag Album non cambiato." and suoni_annotati[-1] == "annullamento"
    assert next(t["valore"] for t in tag.leggi(canzone) if t["chiave"] == "album") == "Uno"
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("Raccolta"))
    album[1]()
    assert _ultima(finestra) == "Album di 2 file: Raccolta." and suoni_annotati[-1] == "tag_cambiato"
    assert [next(t["valore"] for t in tag.leggi(p) if t["chiave"] == "album") for p in (canzone, altra)] == ["Raccolta", "Raccolta"]
    # Maiuscolo+F11 apre subito il menu dei tag.
    aperti = []
    monkeypatch.setattr(finestra.albero, "PopupMenu", lambda menu, posizione: aperti.append([v.GetItemLabelText() for v in menu.GetMenuItems()]))
    finestra.albero.UnselectAll()
    finestra._seleziona(prima)
    _tasto(finestra, codice=wx.WXK_F11, maiuscolo=True)
    assert aperti and aperti[0][:3] == ["Titolo: vuoto", "Artista: vuoto", "Album: Raccolta"]
    # Un file senza tag che MeTeOra sappia leggere lo dice.
    finestra._aggiungi(None, [os.path.join(r"C:\m", "canzone.mid")])
    nodo_midi = list(finestra._figli(finestra.nodo_playlist))[1]
    finestra.albero.Expand(nodo_midi)
    finestra.albero.UnselectAll()
    finestra._seleziona(next(finestra._figli(nodo_midi)))
    _tasto(finestra, codice=wx.WXK_F11)
    assert _ultima(finestra).startswith("F11 legge i tag di un brano o di un file audio o video") and suoni_annotati[-1] == "non_disponibile"


def test_un_tag_scritto_mentre_il_brano_suona(finestra, monkeypatch, suoni_annotati, tmp_path):
    # mpv legge il file mentre mutagen lo riscrive: il brano si ferma un
    # istante e riparte dal suo punto, in pausa se era in pausa.
    import tag

    canzone = _wav_di_prova(tmp_path / "canzone.wav", 6)
    finestra._aggiungi(None, [canzone])
    pl = finestra.archivio.playlist[0]
    finestra._suona(pl, pl.brani[0])
    fine = time.monotonic() + 10
    while time.monotonic() < fine and not (finestra.motore.posizione or 0) > 0.3:
        wx.Yield()
        time.sleep(0.02)
    finestra.motore.pausa(True)
    prima = finestra.motore.posizione
    titolo = next(t for t in tag.leggi(canzone) if t["chiave"] == "titolo")
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("Mentre suona"))
    finestra._cambia_tag([canzone], titolo)
    assert _ultima(finestra) == "Titolo di canzone.wav: Mentre suona."
    assert finestra.motore.in_corso == canzone and finestra.motore.in_pausa
    fine = time.monotonic() + 10
    while time.monotonic() < fine and finestra.motore.posizione is None:
        wx.Yield()
        time.sleep(0.02)
    assert finestra.motore.posizione == pytest.approx(prima, abs=0.3)
    finestra.motore.stop()


class _RicercaFinta(_DialogoFinto):
    """Il campo della ricerca, che annota titolo e prima istruzione."""

    def __init__(self, risposta):
        super().__init__(risposta)
        self.aperture = []

    def __call__(self, genitore, titolo, testo, istruzioni):
        self.aperture.append((titolo, istruzioni[0]))
        return self


def test_la_barra_rovesciata_cerca_nel_ramo(finestra, monkeypatch, tmp_path):
    # 1.71.0: la barra rovesciata cerca nel ramo della plancia, Ctrl con la
    # barra rovesciata ovunque.
    cartella = tmp_path / "Amiga giochi"
    (cartella / "Turrican").mkdir(parents=True)
    (cartella / "Turrican" / "titolo.mp3").write_bytes(b"")
    campo = _RicercaFinta("titolo")
    avviate = []
    monkeypatch.setattr(modulo, "FinestraFiltro", campo)
    monkeypatch.setattr(finestra, "_avvia_ricerca", lambda testo, filtro, unita=None, brani=None, dove=modulo.OVUNQUE: avviate.append((testo, unita, brani, dove)))
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Amiga giochi", data={"tipo": "cartella", "percorso": str(cartella), "caricato": False})
    finestra._seleziona(nodo)
    _tasto(finestra, "\\")
    assert campo.aperture[-1] == ("Ricerca in Amiga giochi", "Puoi usare questi comandi per comporre la ricerca, in Amiga giochi.")
    assert avviate[-1] == ("titolo", [str(cartella)], [], "in Amiga giochi")
    # Un brano di una playlist: la sua playlist sola.
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("a.mp3", "b.mp3")])
    nodo_pl = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo_pl)
    finestra._seleziona(next(finestra._figli(nodo_pl)))
    _tasto(finestra, "\\")
    pl = finestra.archivio.playlist[0]
    assert avviate[-1] == ("titolo", [], [(b, "Playlist Playlist") for b in pl.brani], "nella playlist Playlist")
    # Questo PC: tutti i dischi, e nessuna playlist.
    finestra._seleziona(finestra.nodo_pc)
    _tasto(finestra, "\\")
    assert avviate[-1] == ("titolo", None, [], "in Questo PC")
    # Ctrl con la barra rovesciata: ovunque, come prima la barra da sola.
    evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
    evento.SetKeyCode(ord("\\"))
    evento.SetUnicodeKey(ord("\\"))
    evento.SetControlDown(True)
    finestra._tasto(evento)
    assert campo.aperture[-1][0] == "Ricerca in tutto MeTeOra" and avviate[-1] == ("titolo", None, None, modulo.OVUNQUE)


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


MANUALE_DI_PROVA = """<!doctype html>
<html lang="it"><head><meta charset="utf-8"><title>Prova</title><style>h2 { color: red; }</style></head>
<body>
<h1>Manuale di prova</h1>
<nav aria-label="Indice"><ul><li><a href="#guida-rapida">Guida rapida</a></li><li><a href="#altro">Altro</a></li></ul></nav>
<h2 id="guida-rapida">Guida   rapida</h2>
<h3 id="tasti">I tasti</h3>
<h4>L'aiuto</h4>
<ul>
<li><kbd>F1</kbd>: apre il manuale
    nel browser.</li>
<li><kbd>Maiuscolo con F8</kbd>: aggancia &amp; sgancia, e t&lt;=3:00 &egrave; giusto.</li>
<li>   </li>
<li>Una voce<ul><li>con un elenco dentro</li></ul>e la sua coda.</li>
</ul>
<p>Per esempio: k=sid <em>a=hubbard</em><br>t&gt;2:00.</p>
<h2 id="altro">Un altro capitolo</h2>
<p>Questo non c'entra.</p>
<h3>Neanche questo</h3>
</body></html>"""


def test_guida_rapida_su_un_html_piccolo():
    assert modulo.guida_rapida(MANUALE_DI_PROVA) == [
        "Guida rapida", "I tasti", "L'aiuto", "F1: apre il manuale nel browser.",
        "Maiuscolo con F8: aggancia & sgancia, e t<=3:00 è giusto.",
        "Una voce", "con un elenco dentro", "e la sua coda.",
        "Per esempio: k=sid a=hubbard t>2:00."]
    # Una guida in fondo al file finisce con il file; un file senza guida non ne ha.
    assert modulo.guida_rapida('<h2 id="guida-rapida">Guida</h2><ul><li>Ultima voce.</li></ul>') == ["Guida", "Ultima voce."]
    assert modulo.guida_rapida('<h1>Senza guida</h1><h2 id="altro">Altro</h2><p>Testo.</p>') == []
    assert modulo.guida_rapida("") == []


def test_guida_rapida_del_manuale_vero(finestra):
    righe = modulo.guida_rapida(finestra._leggi_risorsa("manuale.html"))
    assert len(righe) > 100
    assert righe[0] == "Guida rapida"
    for titolo in ("I tasti", "I comandi della ricerca e del filtro", "I colori"):
        assert titolo in righe, titolo
    assert righe.index("I tasti") < righe.index("I comandi della ricerca e del filtro") < righe.index("I colori")
    for riga in righe:
        assert riga and riga == riga.strip() and "  " not in riga and "\n" not in riga, riga
        assert not re.search(r"</?[A-Za-z][^>]*>", riga), riga
        assert not re.search(r"&(#\d+|#x[0-9a-fA-F]+|[A-Za-z]+);", riga), riga
    assert any(r.startswith("F12:") for r in righe) and any(r.startswith("X:") for r in righe)
    # La guida finisce dove comincia il secondo capitolo.
    assert "La finestra" not in righe


def test_f12_scrive_la_guida_rapida(finestra, suoni_annotati):
    _tasto(finestra, codice=wx.WXK_F12)
    righe = modulo.guida_rapida(finestra._leggi_risorsa("manuale.html"))
    stampate = finestra._righe[-len(righe):]
    assert stampate[:-1] == righe[:-1] and _senza_ora(stampate[-1]) == righe[-1]
    assert re.search(r" \d\d:\d\d$", stampate[-1]) and not re.search(r" \d\d:\d\d$", stampate[0])
    assert suoni_annotati[-1] == "elenco_dei_tasti"
    inizio = finestra._posizione_della_console
    testo = finestra.console.GetValue().replace("\r\n", "\n").replace("\r", "\n")
    assert testo[inizio:].startswith("Guida rapida\n")


def test_f12_senza_guida_lo_dice(finestra, suoni_annotati, monkeypatch):
    monkeypatch.setattr(finestra, "_leggi_risorsa", lambda nome: "<h1>Manuale</h1><p>Niente guida.</p>")
    _tasto(finestra, codice=wx.WXK_F12)
    assert _ultima(finestra) == "Nel manuale non trovo la guida rapida."
    assert suoni_annotati[-1] == "errore"


def test_ogni_tasto_e_nella_guida_rapida(finestra):
    """Ogni tasto a lettera e ogni tasto funzione ha la sua riga nella guida
    rapida, che comincia con il suo nome."""
    righe = modulo.guida_rapida(finestra._leggi_risorsa("manuale.html"))
    tasti = [f"F{n}" for n in range(1, 13)] + [f"Maiuscolo con F{n}" for n in (1, 2, 3, 5, 6, 8, 10, 11)] + [
        "Esc", "Alt con F4", "Tab", "Maiuscolo con Tab", "Barra rovesciata", "Ctrl con la barra rovesciata", "Barra verticale",
        "Canc", "Maiuscolo con Canc", "Backspace", "Maiuscolo con Backspace", "Meno", "Più", "Cifre da 1 a 0", "Maiuscolo con le cifre da 1 a 0"]
    for (carattere, maiuscolo), _comando in modulo.TASTI.items():
        if carattere.isalpha():
            tasti.append(f"Maiuscolo con {carattere.upper()}" if maiuscolo else carattere.upper())
    for tasto in tasti:
        assert any(r.startswith(f"{tasto}:") for r in righe), tasto


def test_f12_porta_il_cursore_all_inizio_della_guida(finestra):
    finestra.scrivi("una riga qualsiasi")
    finestra.console.SetInsertionPoint(0)
    _tasto(finestra, codice=wx.WXK_F12)
    for _ in range(5):
        wx.Yield()
    inizio = finestra._posizione_della_console
    assert finestra.console.GetInsertionPoint() == inizio
    testo = finestra.console.GetValue().replace("\r\n", "\n").replace("\r", "\n")
    assert testo[inizio:].startswith("Guida rapida")


def test_f1_apre_il_manuale_nel_browser(finestra, suoni_annotati, monkeypatch):
    # Il browser non si apre mai davvero: os.startfile annota soltanto.
    aperti = []
    monkeypatch.setattr(modulo.os, "startfile", aperti.append, raising=False)
    righe = len(finestra._righe)
    _tasto(finestra, codice=wx.WXK_F1)
    assert aperti == [modulo.percorsi.percorso_risorsa("manuale.html")]
    assert os.path.basename(aperti[0]) == "manuale.html" and os.path.isfile(aperti[0])
    # Il manuale non si scrive piu' nella console: una riga sola, che lo dice.
    assert len(finestra._righe) == righe + 1
    assert _ultima(finestra) == "Il manuale si apre nel browser."
    assert suoni_annotati[-1] == "manuale"


def test_f1_che_non_apre_il_browser_lo_dice(finestra, suoni_annotati, monkeypatch):
    def fallisce(percorso):
        raise OSError(1155, "Nessuna applicazione associata al file")

    monkeypatch.setattr(modulo.os, "startfile", fallisce, raising=False)
    _tasto(finestra, codice=wx.WXK_F1)
    assert _ultima(finestra) == "Non riesco ad aprire manuale.html: Nessuna applicazione associata al file."
    assert suoni_annotati[-1] == "errore"


def test_f1_senza_il_manuale_lo_dice(finestra, suoni_annotati, monkeypatch, tmp_path):
    aperti = []
    monkeypatch.setattr(modulo.os, "startfile", aperti.append, raising=False)
    monkeypatch.setattr(modulo.percorsi, "percorso_risorsa", lambda nome: str(tmp_path / nome))
    _tasto(finestra, codice=wx.WXK_F1)
    assert aperti == []
    assert _ultima(finestra) == "Non riesco ad aprire manuale.html: il file non c'è."
    assert suoni_annotati[-1] == "errore"


def test_f2_f3_scrivono_nella_console(finestra):
    for codice, prima in ((wx.WXK_F2, "Novità di MeTeOra"), (wx.WXK_F3, "Crediti di MeTeOra")):
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
    # 1.88.1: F2 scrive le versioni recenti, a versioni intere, e in fondo
    # dove leggere il changelog intero.
    scritte = [_senza_ora(r) for r in finestra._righe]
    inizio = len(scritte) - 1 - scritte[::-1].index("Novità di MeTeOra")
    righe_f2 = [r for r in scritte[inizio:] if not r.startswith("Crediti")]
    righe_f2 = righe_f2[:next(i for i, r in enumerate(righe_f2) if r.startswith("Le versioni precedenti"))  + 1]
    assert righe_f2[-1].startswith("Le versioni precedenti sono nel changelog intero: il file CHANGELOG.md, nella cartella ")
    assert righe_f2[-1].endswith("https://github.com/GabrieleBattaglia/MeTeOra/blob/main/CHANGELOG.md")
    assert len(righe_f2) <= modulo.RIGHE_DEL_CHANGELOG + 2 and righe_f2[2].startswith("Versione ")


def test_novita_recenti_a_versioni_intere():
    righe = ["Intro.", "Versione 3 del c", "a", "b", "Versione 2 del b", "c", "d", "e", "Versione 1 del a", "f"]
    assert modulo.novita_recenti(righe, 6) == (["Intro.", "Versione 3 del c", "a", "b"], True)
    assert modulo.novita_recenti(righe, 8) == (righe[:8], True)
    assert modulo.novita_recenti(righe, 100) == (righe, False)
    # La versione piu' recente c'e' sempre, anche lunga.
    assert modulo.novita_recenti(righe, 2) == (["Intro.", "Versione 3 del c", "a", "b"], True)


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
    # Le schede arrivano dal filo dello schedario, con la loro variazione.
    with finestra.schedario._lucchetto:
        finestra.schedario._metti(una, {"dim": 1, "mod": 0, "durata": 61.5, "tag": {}, "sottobrani": None, "durate_sid": None})
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
    assert _ultima(finestra).startswith("Riprende")


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
    assert _selezionate(finestra) == sorted(["b.mp3", "c.mp3", "d.mp3", "Nuova playlist", "Questo PC", "Questa rete", "Apri file", "Impostazioni"])
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
    assert suoni_annotati[-1] == "risali" and _ultima(finestra) == "Chiuso Playlist."
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

    def IsShown(self):
        return True


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
        ("modello_casuale", "Modello della riproduzione casuale: una volta per brano, poi ricomincia"),
        ("video", "Video (Maiuscolo+F1): no"),
        ("sottotitoli", "Sottotitoli letti (Maiuscolo+F2): no"),
        ("sintesi", "Sintesi di sottotitoli e karaoke: automatica, adesso NVDA"),
        ("destinazione", "Dove vanno sottotitoli e karaoke: alla sintesi e al braille"),
        ("karaoke", "Testo del karaoke: per riga"),
        ("anticipo_karaoke", "Anticipo del karaoke: 0 ms"),
        ("celle_braille", "Celle della barra braille: 0, il testo intero"),
        ("lettura_minima", "Tempo minimo di lettura in braille: 2000 ms"),
        ("banco_midi", "Banco dei suoni MIDI: nessuno, si sceglie al primo MIDI"),
        ("insegui", "Inseguimento della plancia (Maiuscolo+F8): no"),
        ("ripresa_oltre", "Punto lasciato dei file lunghi: oltre 10 minuti"),
        ("caratteri", "Dimensioni dei caratteri: quelle di Windows"),
        ("colori_testo", "Colori dei caratteri: quelli di Windows"),
        ("colori_sfondo", "Colori dello sfondo: quelli di Windows"),
        ("barra_dei_comandi", "Barra dei comandi per il mouse: sì"),
        ("righe_della_console", "Righe della console: 2000"),
        ("salva_console", "Salva console: scrive la console in un file di testo"),
        ("marcatori", "Marcatori: nessuno"),
        ("importa_marcatori", "Importa marcatori: da un file esportato da MeTeOra"),
        ("associazioni", "Associazioni dei formati: solo dal programma compilato"),
        ("impressi", "Sottotitoli impressi: letti al volo, mentre il video suona, con circa mezzo secondo di ritardo"),
        ("dona", "Dona per questo progetto: offri un caffè all'autore, con PayPal"),
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
    assert _ultima(finestra) == "Riproduzione casuale accesa: una volta per brano, poi ricomincia."
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
        # Il suono arriva dopo quello dell'avvio (tappa 9).
        wx.Yield()
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
    finestra.impostazioni["modello_casuale"] = "totale"
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


def test_dopo_un_salto_lontano_la_console_dice_l_attesa_del_sid(finestra, monkeypatch, suoni_annotati):
    salti = []
    attese = {"secondi": 9.2}
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda _self: r"C:\m\a.sid"))
    monkeypatch.setattr(type(finestra.motore), "posizione", property(lambda _self: 0.5))
    monkeypatch.setattr(type(finestra.motore), "durata", property(lambda _self: 180.0))
    monkeypatch.setattr(finestra.motore, "salta", salti.append)
    monkeypatch.setattr(finestra.motore, "vai_a", salti.append)
    monkeypatch.setattr(finestra.motore, "attesa_del_sid", lambda secondi: attese["secondi"])
    _tasto(finestra, "e")
    assert [_senza_ora(r) for r in finestra._righe[-2:]] == ["Avanti a 0:10 di 3:00.", "Il SID si prepara fino a 0:10: circa 9 secondi."]
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("2:48"))
    assert _premi(finestra, "w") == "Il SID si prepara fino a 2:48: circa 9 secondi."
    # Sotto il secondo e mezzo non si dice niente.
    attese["secondi"] = 1.4
    assert _premi(finestra, "w") == "Vado a 2:48 di 3:00." and suoni_annotati[-1] == "vai_a_tempo"


def _video_finto(finestra, monkeypatch, tracce):
    """Il motore finto del video: un brano in corso con le tracce date, e le
    chiamate annotate in una lista."""
    chiamate = []
    stato = {"in_corso": r"C:\m\film.mkv", "tracce": tracce, "indice": 0}
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda _self: stato["in_corso"]))
    monkeypatch.setattr(finestra.motore, "tracce", lambda: stato["tracce"] if stato["in_corso"] else None)
    monkeypatch.setattr(finestra.motore, "indice_attivo", lambda: stato["indice"])
    monkeypatch.setattr(finestra.motore, "imposta_il_video", lambda finestre: chiamate.append(("video", finestre)))
    monkeypatch.setattr(finestra.motore, "scegli_traccia", lambda tipo, numero: chiamate.append((tipo, numero)))
    monkeypatch.setattr(finestra.motore, "rapporto", lambda valore: chiamate.append(("rapporto", valore)))
    return stato, chiamate


def _tracce(video=True, audio=1, sottotitoli=0, scelto_audio=0, scelto_sub=None):
    return {"video": video,
            "audio": [{"id": i + 1, "lang": "ita" if i == 0 else "eng", "selected": i == scelto_audio, "codec": "aac"} for i in range(audio)],
            "sub": [{"id": i + 1, "lang": "ita", "title": f"Traccia {i + 1}", "selected": i == scelto_sub, "codec": "subrip"} for i in range(sottotitoli)]}


def test_il_video_aspetta_la_chiusura_dei_dialoghi_e_la_ripresa(finestra, monkeypatch, suoni_annotati):
    stato, _chiamate = _video_finto(finestra, monkeypatch, _tracce())
    finestra.impostazioni["video"] = True
    # Con un dialogo aperto la finestra principale e' disabilitata: il video
    # aspetta che torni attiva, per non rubare il fuoco al dialogo (tappa 9).
    finestra.Enable(False)
    try:
        finestra._aggiorna_il_video()
        assert (finestra._video is None or not finestra._video.IsShown()) and finestra._video_rimandato
    finally:
        finestra.Enable(True)
    finestra._all_attivazione(wx.ActivateEvent(wx.wxEVT_ACTIVATE, True))
    wx.Yield()
    assert finestra._video.IsShown() and not finestra._video_rimandato
    # Esc nella finestra la nasconde per il brano, e lo dice.
    finestra._nascondi_a_mano()
    assert not finestra._video.IsShown() and suoni_annotati[-1] == "video_nascosto"
    # Il brano ripreso all'avvio in pausa apre la finestra con X, non subito.
    pausa = [True]
    monkeypatch.setattr(type(finestra.motore), "in_pausa", property(lambda _self: pausa[0]))
    stato["in_corso"] = r"C:\m\altro.mkv"
    finestra._video_in_attesa = stato["in_corso"]
    finestra._aggiorna_il_video()
    assert not finestra._video.IsShown()
    pausa[0] = False
    finestra._riprende_il_video()
    assert finestra._video.IsShown() and finestra._video_in_attesa is None
    finestra._nascondi_il_video()


def test_maiuscolo_f1_accende_il_video_e_la_finestra_si_apre_e_si_chiude(finestra, monkeypatch, suoni_annotati):
    stato, chiamate = _video_finto(finestra, monkeypatch, _tracce())
    _tasto(finestra, codice=wx.WXK_F1, maiuscolo=True)
    assert finestra.impostazioni["video"] is True and _salvate(finestra)["video"] is True
    assert "video_acceso" in suoni_annotati
    assert any(_senza_ora(r) == "Video acceso: i video si vedono in una finestra sopra MeTeOra." for r in finestra._righe)
    video = finestra._video
    assert video is not None and video.IsShown() and video.GetTitle() == "film.mkv, video, MeTeOra"
    assert chiamate[0] == ("video", video.finestre())
    # Un brano senza video la chiude; uno con il video la riapre, senza ridare
    # al motore le finestre.
    stato["tracce"] = _tracce(video=False)
    finestra._aggiorna_il_video()
    assert not video.IsShown()
    stato["tracce"] = _tracce()
    finestra._aggiorna_il_video()
    assert video.IsShown() and chiamate.count(("video", video.finestre())) == 1
    # Con la dissolvenza il pannello segue il lettore che suona.
    stato["indice"] = 1
    finestra._aggiorna_il_video()
    assert video.pannelli[1].IsShown() and not video.pannelli[0].IsShown()
    # Allo stop sparisce.
    stato["in_corso"] = None
    finestra._aggiorna_il_video()
    assert not video.IsShown()
    # Spento, il motore smette di disegnare, e dei video si sente l'audio.
    stato["in_corso"] = r"C:\m\film.mkv"
    _tasto(finestra, codice=wx.WXK_F1, maiuscolo=True)
    assert finestra.impostazioni["video"] is False and chiamate[-1] == ("video", None)
    assert suoni_annotati[-1] == "video_spento" and not video.IsShown()
    assert _ultima(finestra) == "Video spento: dei video si sente solo l'audio."


def test_esc_nella_finestra_del_video_la_nasconde_per_quel_brano(finestra, monkeypatch, suoni_annotati):
    stato, _chiamate = _video_finto(finestra, monkeypatch, _tracce())
    finestra.impostazioni["video"] = True
    finestra._aggiorna_il_video()
    video = finestra._video
    evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
    evento.SetKeyCode(wx.WXK_ESCAPE)
    video._tasto(evento)
    assert not video.IsShown() and not finestra._chiusa
    # Per lo stesso brano non si riapre; per il brano dopo si'.
    finestra._aggiorna_il_video()
    assert not video.IsShown()
    stato["in_corso"] = r"C:\m\altro.mkv"
    finestra._aggiorna_il_video()
    assert video.IsShown()
    # Gli altri tasti passano alla finestra principale.
    evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
    evento.SetUnicodeKey(ord("+"))
    evento.SetKeyCode(ord("+"))
    volume = finestra.motore.volume
    video._tasto(evento)
    assert finestra.motore.volume > volume


def test_maiuscolo_f2_sottotitoli_a_giro(finestra, monkeypatch, suoni_annotati):
    stato, chiamate = _video_finto(finestra, monkeypatch, _tracce(video=False, sottotitoli=2))
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert chiamate[-1] == ("sid", "1") and finestra.impostazioni["sottotitoli"] is True
    assert _ultima(finestra) == "Sottotitoli letti, traccia 1 di 2, italiano, Traccia 1, subrip." and suoni_annotati[-1] == "sottotitoli_accesi"
    stato["tracce"] = _tracce(video=False, sottotitoli=2, scelto_sub=0)
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert chiamate[-1] == ("sid", "2")
    stato["tracce"] = _tracce(video=False, sottotitoli=2, scelto_sub=1)
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert chiamate[-1] == ("sid", "no") and finestra.impostazioni["sottotitoli"] is False
    assert _ultima(finestra) == "Sottotitoli letti spenti." and suoni_annotati[-1] == "sottotitoli_spenti"
    assert _salvate(finestra)["sottotitoli"] is False
    # Su un brano senza sottotitoli si accendono per i brani dopo.
    stato["tracce"] = _tracce(video=False)
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert _ultima(finestra) == "Sottotitoli letti accesi; questo brano non ne ha." and finestra.impostazioni["sottotitoli"] is True
    # Accesi, un brano con i sottotitoli prende la prima traccia da solo.
    stato["tracce"] = _tracce(video=False, sottotitoli=1)
    finestra._aggiorna_il_video()
    assert chiamate[-1] == ("sid", "1")


def test_i_sottotitoli_letti_vanno_alla_sintesi_e_nella_console(finestra, sintesi_finta):
    finestra._sottotitolo("Prima riga\ndi prova")
    assert not sintesi_finta.detti
    finestra.impostazioni["sottotitoli"] = True
    finestra._sottotitolo("Prima riga\ndi prova")
    assert sintesi_finta.detti == [("nvda", "Prima riga di prova")] and _ultima(finestra) == "Prima riga di prova"
    # Senza screen reader attivi va alla voce di Windows; scelta a mano, a quella.
    sintesi_finta.attive["nvda"] = False
    finestra._sottotitolo("Seconda")
    assert sintesi_finta.detti[-1] == ("sapi5", "Seconda")
    finestra.impostazioni["sintesi"] = "jaws"
    sintesi_finta.attive["jaws"] = True
    finestra._sottotitolo("Terza")
    assert sintesi_finta.detti[-1] == ("jaws", "Terza")


def test_maiuscolo_f3_traccia_audio_a_giro(finestra, monkeypatch, suoni_annotati):
    stato, chiamate = _video_finto(finestra, monkeypatch, _tracce(audio=1))
    _tasto(finestra, codice=wx.WXK_F3, maiuscolo=True)
    assert _ultima(finestra) == "Questo brano ha una traccia audio sola." and suoni_annotati[-1] == "non_disponibile"
    stato["tracce"] = _tracce(audio=2, scelto_audio=0)
    _tasto(finestra, codice=wx.WXK_F3, maiuscolo=True)
    assert chiamate[-1] == ("aid", "2") and _ultima(finestra) == "Traccia audio 2 di 2, inglese, aac." and suoni_annotati[-1] == "traccia_audio"
    stato["tracce"] = _tracce(audio=2, scelto_audio=1)
    _tasto(finestra, codice=wx.WXK_F3, maiuscolo=True)
    assert chiamate[-1] == ("aid", "1")
    stato["in_corso"] = None
    _tasto(finestra, codice=wx.WXK_F3, maiuscolo=True)
    assert _ultima(finestra) == "Non sta suonando niente."


def test_maiuscolo_f5_e_f6_schermo_intero_e_rapporto(finestra, monkeypatch, suoni_annotati):
    _stato, chiamate = _video_finto(finestra, monkeypatch, _tracce())
    _tasto(finestra, codice=wx.WXK_F5, maiuscolo=True)
    assert _ultima(finestra) == "La finestra del video non è aperta." and suoni_annotati[-1] == "non_disponibile"
    finestra.impostazioni["video"] = True
    finestra._aggiorna_il_video()
    _tasto(finestra, codice=wx.WXK_F5, maiuscolo=True)
    assert finestra._video.IsFullScreen() and suoni_annotati[-1] == "schermo_intero"
    _tasto(finestra, codice=wx.WXK_F5, maiuscolo=True)
    assert not finestra._video.IsFullScreen() and suoni_annotati[-1] == "schermo_in_finestra" and _ultima(finestra) == "Video in finestra."
    for _ in range(4):
        _tasto(finestra, codice=wx.WXK_F6, maiuscolo=True)
    assert [c for c in chiamate if c[0] == "rapporto"] == [("rapporto", "16:9"), ("rapporto", "4:3"), ("rapporto", "2.33:1"), ("rapporto", "-1")]
    assert _ultima(finestra) == "Rapporto dell'immagine: quello del video." and suoni_annotati[-1] == "rapporto"


def test_impostazioni_video_sottotitoli_e_sintesi(finestra, monkeypatch, suoni_annotati, sintesi_finta):
    _stato, chiamate = _video_finto(finestra, monkeypatch, _tracce())
    _campo, lista = _cambia(finestra, monkeypatch, "video", "sì")
    assert finestra.impostazioni["video"] is True and finestra._video.IsShown()
    assert lista.righe["video"] == "Video (Maiuscolo+F1): sì"
    _cambia(finestra, monkeypatch, "video", "no")
    assert chiamate[-1] == ("video", None) and not finestra._video.IsShown()
    _campo, lista = _cambia(finestra, monkeypatch, "sottotitoli", "acceso")
    assert finestra.impostazioni["sottotitoli"] is True and lista.righe["sottotitoli"] == "Sottotitoli letti (Maiuscolo+F2): sì"
    # La sintesi: l'automatica e le uscite che rispondono adesso.
    scelta = _SceltaFinta(2)
    monkeypatch.setattr(modulo, "FinestraScelta", scelta)
    lista = _ListaFinta()
    finestra._cambia_impostazione("sintesi", lista)
    titolo, righe, partenza = scelta.aperture[0]
    assert titolo == "Sintesi di sottotitoli e karaoke" and partenza == 0
    assert righe == ["Automatica: lo screen reader attivo, altrimenti la voce di Windows", "NVDA", "La voce di Windows, SAPI5"]
    assert finestra.impostazioni["sintesi"] == "sapi5" and _salvate(finestra)["sintesi"] == "sapi5"
    assert lista.righe["sintesi"] == "Sintesi di sottotitoli e karaoke: la voce di Windows, SAPI5"
    # Una scelta che non risponde piu' resta in fondo alla lista, e lo dice.
    finestra.impostazioni["sintesi"] = "jaws"
    scelta = _SceltaFinta(None)
    monkeypatch.setattr(modulo, "FinestraScelta", scelta)
    finestra._cambia_impostazione("sintesi", _ListaFinta())
    assert scelta.aperture[0][1][-1] == "JAWS, che adesso non risponde" and scelta.aperture[0][2] == 3
    assert _ultima(finestra) == "Sintesi di sottotitoli e karaoke non cambiata."

def _mouse_finto(barra_, posizione):
    """Il mouse, l'orologio, la finestra attiva e i menu di una barra, finti:
    posizione e' una lista con il punto di adesso."""
    barra_._posizione_del_mouse = lambda: posizione[0]
    barra_._finestra_attiva = lambda: True
    barra_._occupata = lambda: False


def _messaggio(barra_, messaggio, punto):
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32")
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.SendMessageW(barra_.GetHandle(), messaggio, 1 if messaggio == 0x0201 else 0, (punto.y << 16) | (punto.x & 0xFFFF))


def test_la_barra_del_tempo_della_finestra_del_video(finestra, monkeypatch, suoni_annotati):
    # 1.88.0 (Gabriele): sopra il video la barra dei comandi, con la linea del
    # tempo larga quasi quanto il video; un clic salta in quel punto, con il
    # riscontro di W, e trascinando si salta dove si lascia. Il cursore di
    # Windows di prima non c'e' piu'.
    import barra as modulo_barra

    _video_finto(finestra, monkeypatch, _tracce())
    salti = []
    durata = [120.0]
    monkeypatch.setattr(type(finestra.motore), "posizione", property(lambda _self: 30.0))
    monkeypatch.setattr(type(finestra.motore), "durata", property(lambda _self: durata[0]))
    monkeypatch.setattr(finestra.motore, "vai_a", salti.append)
    finestra.impostazioni["video"] = True
    finestra._aggiorna_il_video()
    video = finestra._video
    b = video.barra
    assert isinstance(b, modulo_barra.BarraDeiComandi) and b._sopra is video and b._linea is not None
    assert not any(isinstance(c, wx.Slider) for c in video.GetChildren())
    assert not b.CanAcceptFocus() and b.comandi()[:7] == ["precedente", "indietro", "play", "pausa", "stop", "avanti", "successivo"]
    video.SetClientSize(1200, 700)
    area = b._area_della_finestra()
    posizione = [wx.Point(area.x + area.width // 2, area.y + area.height // 3)]
    _mouse_finto(b, posizione)
    for passo in range(3):
        posizione[0] = wx.Point(posizione[0].x + 4 * passo, posizione[0].y)
        b.guarda()
    assert b.IsShown() and b.GetClientSize().width == round(area.width * modulo_barra.LARGHEZZA_CON_IL_TEMPO)
    linea = b._linea
    meta = wx.Point(linea.x + linea.width // 2, linea.y + linea.height // 2)
    # Un clic a meta' della linea, arrivato muovendosi: salta a meta' del brano.
    _messaggio(b, 0x0200, meta - wx.Point(3, 0))
    _messaggio(b, 0x0200, meta)
    assert b._sul_tempo is not None
    _messaggio(b, 0x0201, meta)
    _messaggio(b, 0x0202, meta)
    assert len(salti) == 1 and abs(salti[0] - 60.0) < 0.5
    assert _ultima(finestra).startswith("Vado a 1:00 di 2:00") and suoni_annotati[-1] == "vai_a_tempo"
    # Trascinando da un quarto a tre quarti si salta dove si lascia; intanto
    # la barra resta, anche con il tempo che passa.
    quarto = wx.Point(linea.x + linea.width // 4, meta.y)
    tre_quarti = wx.Point(linea.x + linea.width * 3 // 4, meta.y)
    _messaggio(b, 0x0201, quarto)
    _messaggio(b, 0x0200, tre_quarti)
    b._orologio = lambda: 10 ** 6
    b.guarda()
    assert b.IsShown() and b._trascinando is not None
    _messaggio(b, 0x0202, tre_quarti)
    assert len(salti) == 2 and abs(salti[1] - 90.0) < 0.5 and b._trascinando is None
    # Dopo il rilascio la barra scrive il punto lasciato.
    assert abs(b._sul_tempo - 0.75) < 0.01
    # Un doppio clic sulla linea salta una volta sola.
    _messaggio(b, 0x0200, meta)
    _messaggio(b, 0x0201, meta)
    _messaggio(b, 0x0202, meta)
    _messaggio(b, 0x0203, meta)
    _messaggio(b, 0x0202, meta)
    assert len(salti) == 3
    # Il brano che cambia durante il trascinamento: il salto non si fa.
    _messaggio(b, 0x0201, quarto)
    durata[0] = 300.0
    _messaggio(b, 0x0202, tre_quarti)
    assert len(salti) == 3
    durata[0] = 120.0
    # La barra nascosta a meta' trascinamento lascia il mouse, e non salta.
    _messaggio(b, 0x0201, quarto)
    assert b.HasCapture()
    b.nascondi()
    assert not b.HasCapture() and b._trascinando is None and len(salti) == 3
    # Senza la durata, la linea non salta.
    b._mostra()
    durata[0] = None
    _messaggio(b, 0x0200, meta - wx.Point(2, 0))
    _messaggio(b, 0x0200, meta)
    _messaggio(b, 0x0201, meta)
    _messaggio(b, 0x0202, meta)
    assert len(salti) == 3
    # Chiudere MeTeOra con il mouse preso dalla linea non fa cadere wx.
    durata[0] = 120.0
    _messaggio(b, 0x0200, meta - wx.Point(2, 0))
    _messaggio(b, 0x0200, meta)
    _messaggio(b, 0x0201, meta)
    assert b.HasCapture()
    finestra.Close(force=True)
    assert not b.HasCapture()


def test_la_barra_del_video_e_quella_principale_non_si_incontrano(finestra, monkeypatch):
    # 1.88.0: ognuna compare solo quando la sua finestra e' attiva.
    _video_finto(finestra, monkeypatch, _tracce())
    finestra.impostazioni["video"] = True
    finestra._aggiorna_il_video()
    principale, video = finestra.barra, finestra._video.barra
    area = principale._area_della_finestra()
    posizione = [wx.Point(area.x + area.width // 2, area.y + area.height // 3)]
    attiva = ["video"]
    for b, nome in ((principale, "principale"), (video, "video")):
        _mouse_finto(b, posizione)
        b._finestra_attiva = lambda nome=nome: attiva[0] == nome

    def muovi():
        for passo in range(3):
            posizione[0] = wx.Point(posizione[0].x + 3 + passo, posizione[0].y)
            principale.guarda()
            video.guarda()

    muovi()
    assert video.IsShown() and not principale.IsShown()
    attiva[0] = "principale"
    muovi()
    assert principale.IsShown() and not video.IsShown()
    # La voce delle impostazioni le spegne tutte e due.
    finestra._applica_l_impostazione("barra_dei_comandi", False)
    assert not principale._timer.IsRunning() and not video._timer.IsRunning()
    assert not principale.IsShown() and not video.IsShown()


def _rete_finta(finestra, monkeypatch, tmp_path):
    """Questa rete senza rete: un percorso salvato che e' una cartella
    temporanea con un brano, un computer con una cartella condivisa, e le
    ricerche in disparte che aspettano la prova."""
    import questa_rete

    musica = tmp_path / "musica"
    musica.mkdir()
    (musica / "canzone.mp3").write_bytes(b"")
    stato = {"raggiungibile": True, "ricerche": []}

    def leggi_in_rete(cartella, attesa=None, fermo=None):
        # 1.85.5: i rami di rete si leggono sempre, con la lettura protetta.
        if not stato["raggiungibile"]:
            raise modulo.NonRisponde(cartella)
        return modulo.questo_pc.contenuto(cartella)

    monkeypatch.setattr(modulo, "leggi_in_rete", leggi_in_rete)
    monkeypatch.setattr(questa_rete, "percorsi_salvati", lambda cartella=None: [("nas (server)", str(musica))])
    monkeypatch.setattr(questa_rete, "computer", lambda: [("NAS", r"\\NAS")])
    monkeypatch.setattr(questa_rete, "condivisioni", lambda server: [("film", str(musica))])
    monkeypatch.setattr(questa_rete, "raggiungibile", lambda percorso, attesa=3.0: stato["raggiungibile"])
    monkeypatch.setattr(questa_rete, "in_disparte", lambda lavoro, al_termine: stato["ricerche"].append((lavoro, al_termine)))
    return stato


def test_questa_rete_mostra_i_percorsi_i_computer_e_il_comando(finestra, monkeypatch, tmp_path, suoni_annotati):
    stato = _rete_finta(finestra, monkeypatch, tmp_path)
    finestra.impostazioni["percorsi_di_rete"] = [r"\\server\video"]
    finestra.albero.Expand(finestra.nodo_rete)
    assert _etichette(finestra, finestra.nodo_rete) == ["nas (server)", r"\\server\video", "Computer della rete", "Aggiungi un percorso di rete"]
    # Il percorso salvato si apre come una cartella di Questo PC, e tiene il suo nome.
    salvato = next(finestra._figli(finestra.nodo_rete))
    finestra.albero.Expand(salvato)
    assert _etichette(finestra, salvato) == ["canzone.mp3"]
    finestra._aggiorna_cartelle()
    assert finestra.albero.GetItemText(salvato).startswith("nas (server)")
    # Una cartella che non risponde non si apre, e lo si dice.
    stato["raggiungibile"] = False
    a_mano = list(finestra._figli(finestra.nodo_rete))[1]
    finestra.albero.Expand(a_mano)
    assert _ultima(finestra).startswith(r"\\server\video non risponde") and _ultima(finestra).endswith("Riaprendo il ramo si riprova.")
    assert suoni_annotati[-1] == "errore"
    assert finestra._dati(a_mano)["caricato"] is False
    # I computer si cercano in disparte, con una voce d'attesa.
    computer = list(finestra._figli(finestra.nodo_rete))[2]
    finestra.albero.Expand(computer)
    assert _etichette(finestra, computer) == ["Cerco i computer della rete..."] and suoni_annotati[-1] == "ricerca_avviata"
    lavoro, _al_termine = stato["ricerche"].pop()
    finestra._trovati_nella_rete(finestra._dati(computer), lavoro())
    assert _etichette(finestra, computer) == ["NAS"] and _ultima(finestra) == "Trovato 1 computer nella rete." and suoni_annotati[-1] == "ricerca_finita"
    nas = next(finestra._figli(computer))
    finestra.albero.Expand(nas)
    lavoro, _al_termine = stato["ricerche"].pop()
    finestra._trovati_nella_rete(finestra._dati(nas), lavoro())
    assert _etichette(finestra, nas) == ["film"] and _ultima(finestra) == "NAS: 1 cartella condivisa."
    # Una ricerca finita dopo che il suo ramo e' stato rifatto non tocca niente.
    finestra._aggiorna_ramo(finestra.nodo_rete)
    finestra._trovati_nella_rete({"tipo": "computer_della_rete"}, [("Altro", r"\\Altro")])


def test_aggiungere_e_togliere_un_percorso_di_rete(finestra, monkeypatch, tmp_path, suoni_annotati):
    _rete_finta(finestra, monkeypatch, tmp_path)
    finestra.albero.Expand(finestra.nodo_rete)
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto("server"))
    finestra._comando_aggiungi_percorso_di_rete()
    assert _ultima(finestra) == r"server non è un percorso di rete: si scrive come \\server\cartella." and not finestra.impostazioni["percorsi_di_rete"]
    import questa_rete

    monkeypatch.setattr(questa_rete, "raggiungibile", lambda percorso, attesa=3.0: False)
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto(r" \\server\video/ "))
    finestra._comando_aggiungi_percorso_di_rete()
    assert finestra.impostazioni["percorsi_di_rete"] == [r"\\server\video"] and _salvate(finestra)["percorsi_di_rete"] == [r"\\server\video"]
    assert _ultima(finestra) == r"Aggiunto a Questa rete \\server\video. Adesso non risponde, ma lo tengo." and suoni_annotati[-1] == "percorso_aggiunto"
    assert r"\\server\video" in _etichette(finestra, finestra.nodo_rete)
    assert finestra.albero.GetItemText(finestra._voce_corrente()) == r"\\server\video"
    finestra._comando_aggiungi_percorso_di_rete()
    assert _ultima(finestra) == r"\\server\video è già in Questa rete."
    # Il menu del percorso scritto a mano ha Togli il percorso; Canc lo toglie.
    voce = finestra._voce_corrente()
    assert "Togli il percorso" in [nome for nome, _azione in finestra._voci_del_menu(finestra._dati(voce))]
    finestra._cancella(voce)
    assert finestra.impostazioni["percorsi_di_rete"] == [] and r"\\server\video" not in _etichette(finestra, finestra.nodo_rete)
    assert _ultima(finestra) == r"Tolto da Questa rete \\server\video. I file restano dove sono." and suoni_annotati[-1] == "percorso_tolto"
    # Canc su un percorso salvato in Windows non toglie niente.
    finestra._cancella(next(finestra._figli(finestra.nodo_rete)))
    assert _ultima(finestra) == "Qui Canc non cancella niente."


def _banco_finto(cartella, nome="Banco.sf2"):
    """Un banco General MIDI senza campioni: basta a e_un_banco e a general_midi."""
    from test_midi import banco_di_prova

    return banco_di_prova(cartella / nome)


def _midi_finti(finestra, monkeypatch, presente=True):
    """FluidSynth finto e il lavoro in disparte fatto subito, con wx.CallAfter
    che chiama al momento: la preparazione dei MIDI senza fili ne' rete."""
    stato = {"presente": presente, "scaricati": []}
    monkeypatch.setattr(modulo.midi, "fluidsynth_presente", lambda: stato["presente"])
    monkeypatch.setattr(modulo.midi, "scarica_fluidsynth", lambda avanza=None: stato.update(presente=True) or stato["scaricati"].append("fluidsynth"))
    monkeypatch.setattr(modulo, "midi_in_disparte", lambda lavoro, al_termine: al_termine(lavoro()))
    monkeypatch.setattr(modulo.wx, "CallAfter", lambda funzione, *argomenti, **chiavi: funzione(*argomenti, **chiavi))
    monkeypatch.setattr(type(finestra.motore), "banco_midi", property(lambda self: stato.get("banco"), lambda self, banco: stato.update(banco=banco)))
    return stato


def test_il_primo_midi_scarica_fluidsynth_cerca_i_banchi_e_poi_suona(finestra, monkeypatch, tmp_path, suoni_annotati):
    suonati = _finto_motore(finestra, monkeypatch)
    stato = _midi_finti(finestra, monkeypatch, presente=False)
    banco = _banco_finto(tmp_path)
    monkeypatch.setattr(modulo.midi, "cerca_banchi", lambda radici=None, avvisa=None, fermo=None: [(banco, 30_000_000)])
    finestra._aggiungi(None, [str(tmp_path / "canzone.mid")])
    pl = finestra.archivio.playlist[0]
    # Chi rifiuta non sente niente, e sa dove prepararli.
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo, genitore=None: False)
    finestra._suona(pl, pl.brani[0])
    assert not suonati and _ultima(finestra).startswith("I MIDI restano da preparare")
    domande = []
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo, genitore=None: domande.append(domanda) or True)
    scelta = _SceltaFinta(0)
    monkeypatch.setattr(modulo, "FinestraScelta", scelta)
    finestra._suona(pl, pl.brani[0])
    assert "Scarico FluidSynth e cerco nei dischi" in domande[0] and stato["scaricati"] == ["fluidsynth"]
    titolo, righe, _partenza = scelta.aperture[0]
    assert titolo == "Banco dei suoni MIDI" and righe == [f"Banco, 30 MB, in {tmp_path}", "Scarica FluidR3 GM, circa 148 MB"]
    for evento in ("scaricamento_avviato", "scaricamento_finito", "ricerca_avviata", "ricerca_finita", "impostazione_cambiata"):
        assert evento in suoni_annotati
    assert finestra.impostazioni["banco_midi"] == banco and _salvate(finestra)["banco_midi"] == banco and stato["banco"] == banco
    assert suonati == [("canzone.mid", None)]


def test_senza_banchi_nei_dischi_si_scarica_fluidr3(finestra, monkeypatch, tmp_path, suoni_annotati):
    suonati = _finto_motore(finestra, monkeypatch)
    _midi_finti(finestra, monkeypatch)
    banco = _banco_finto(tmp_path, "FluidR3_GM.sf2")
    monkeypatch.setattr(modulo.midi, "cerca_banchi", lambda radici=None, avvisa=None, fermo=None: [])
    monkeypatch.setattr(modulo.midi, "scarica_fluidr3", lambda avanza=None: avanza(50, 100) or banco)
    domande = []
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo, genitore=None: domande.append(domanda) or True)
    finestra._aggiungi(None, [str(tmp_path / "canzone.mid")])
    pl = finestra.archivio.playlist[0]
    finestra._suona(pl, pl.brani[0])
    assert domande[1].startswith("Scarico FluidR3 GM") and finestra.impostazioni["banco_midi"] == banco
    assert any(_senza_ora(r) == "FluidR3 GM: 50 per cento." for r in finestra._righe)
    assert suonati == [("canzone.mid", None)] and "scaricamento_finito" in suoni_annotati


def test_un_midi_senza_banco_non_si_prepara_per_la_dissolvenza(finestra, monkeypatch, tmp_path):
    _suonati, preparati = _motore_che_prepara(finestra, monkeypatch)
    _midi_finti(finestra, monkeypatch)
    _playlist_di_prova(finestra, ("a.mp3", "b.mid"))
    pl = finestra.archivio.playlist[0]
    finestra._suona(pl, pl.brani[0])
    finestra._prepara_il_seguente()
    assert preparati == []


def test_impostazioni_banco_dei_suoni_midi(finestra, monkeypatch, tmp_path, suoni_annotati):
    _midi_finti(finestra, monkeypatch)
    banco = _banco_finto(tmp_path)
    # Scrivi il percorso: un file che non e' un banco si rifiuta.
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaFinta(1))
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto(str(tmp_path / "niente.sf2")))
    lista = _ListaFinta()
    finestra._cambia_impostazione("banco_midi", lista)
    assert _ultima(finestra).endswith("non è un banco di suoni: serve un file sf2 o sf3.") and not finestra.impostazioni["banco_midi"]
    monkeypatch.setattr(modulo, "DialogoTesto", _DialogoFinto(f'"{banco}"'))
    finestra._cambia_impostazione("banco_midi", lista)
    assert finestra.impostazioni["banco_midi"] == banco and lista.righe["banco_midi"] == "Banco dei suoni MIDI: Banco.sf2"
    assert _ultima(finestra) == "I MIDI suonano con il banco Banco.sf2." and suoni_annotati[-1] == "impostazione_cambiata"
    os.remove(banco)
    assert finestra._riga_dell_impostazione("banco_midi") == f"Banco dei suoni MIDI: {banco}, che non si trova più"


class _InvitoFinto:
    """La finestra dell'invito a offrire un caffe', senza finestra: annota i
    testi e risponde come le si dice."""

    def __init__(self, risposta=wx.ID_NO):
        self.risposta = risposta
        self.testi = []

    def __call__(self, genitore, testo):
        self.testi.append(testo)
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_argomenti):
        return False

    def ShowModal(self):
        return self.risposta


def _donazione(monkeypatch, esito):
    """Donazione di GBUtils sostituita: annota gli argomenti e restituisce
    esito, o lo solleva se e' un'eccezione."""
    import GBUtils

    chiamate = []

    def finta(**argomenti):
        chiamate.append(argomenti)
        if isinstance(esito, Exception):
            raise esito
        return esito

    monkeypatch.setattr(GBUtils, "Donazione", finta)
    return chiamate


def test_alla_chiusura_l_invito_a_offrire_un_caffe(finestra, monkeypatch, suoni_annotati):
    # 1.75.0, Gabriele: alla chiusura una volta su cinque, per ultimo, con
    # il suo suono, prima di quello dell'uscita.
    chiamate = _donazione(monkeypatch, "Offrimi un caffè.")
    invito = _InvitoFinto()
    monkeypatch.setattr(modulo, "DialogoDonazione", invito)
    finestra._alla_chiusura(types.SimpleNamespace(Skip=lambda: None))
    assert chiamate == [{"lang": "it", "probabilita": 20, "stampa": False}]
    assert invito.testi == ["Offrimi un caffè."] and suoni_annotati[-2:] == ["donazione", "uscita"]


def test_alla_chiusura_senza_invito_o_con_un_guasto(finestra, monkeypatch, suoni_annotati):
    invito = _InvitoFinto()
    monkeypatch.setattr(modulo, "DialogoDonazione", invito)
    _donazione(monkeypatch, RuntimeError("guasto finto"))
    finestra._alla_chiusura(types.SimpleNamespace(Skip=lambda: None))
    # Il guasto non ferma l'uscita, e senza testo la finestra non si apre.
    assert invito.testi == [] and suoni_annotati[-1] == "uscita" and "donazione" not in suoni_annotati


def test_la_voce_dona_per_questo_progetto(finestra, monkeypatch, suoni_annotati):
    # Dalle impostazioni l'invito compare sempre.
    chiamate = _donazione(monkeypatch, "Offrimi un caffè.")
    invito = _InvitoFinto(wx.ID_YES)
    monkeypatch.setattr(modulo, "DialogoDonazione", invito)
    assert finestra._riga_dell_impostazione("dona") == "Dona per questo progetto: offri un caffè all'autore, con PayPal"
    finestra._cambia_impostazione("dona", None)
    assert chiamate == [{"lang": "it", "probabilita": 100, "stampa": False}]
    assert invito.testi == ["Offrimi un caffè."] and suoni_annotati[-1] == "donazione"
    assert _ultima(finestra) == "PayPal si apre nel browser: grazie di cuore!"
    # Chiuso con Chiudi, la console non dice niente di nuovo.
    invito.risposta = wx.ID_NO
    righe = len(finestra._righe)
    finestra._cambia_impostazione("dona", None)
    assert len(finestra._righe) == righe and len(invito.testi) == 2

def test_cartella_vuota_e_cestino(tmp_path):
    # 1.76.0: vuota anche con sottocartelle vuote o i soli file di servizio;
    # un file vero, anche nascosto o che MeTeOra non suona, la rende piena.
    import questo_pc

    vuota = tmp_path / "vuota"
    (vuota / "dentro" / "piu dentro").mkdir(parents=True)
    (vuota / "desktop.ini").write_text("[.ShellClassInfo]")
    (vuota / "dentro" / "Thumbs.db").write_bytes(b"")
    assert questo_pc.cartella_vuota(str(vuota))
    (vuota / "dentro" / "piu dentro" / "note.txt").write_text("una nota")
    assert not questo_pc.cartella_vuota(str(vuota))
    assert questo_pc.ha_il_cestino(str(tmp_path)) and not questo_pc.ha_il_cestino("\\\\server\\cartella\\a.mp3")


def test_maiuscolo_canc_su_una_cartella_vuota(finestra, suoni_annotati, tmp_path, monkeypatch):
    import questo_pc

    cestinati, domande = [], []
    monkeypatch.setattr(questo_pc, "nel_cestino", lambda p: cestinati.append(p) or True)
    risposte = [False, True]
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo: domande.append((domanda, titolo)) or risposte.pop(0))
    (tmp_path / "Vuota" / "Dentro").mkdir(parents=True)
    (tmp_path / "Piena").mkdir()
    (tmp_path / "Piena" / "copertina.jpg").write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    vuota = finestra.albero.AppendItem(finestra.nodo_pc, "Vuota", data={"tipo": "cartella", "percorso": str(tmp_path / "Vuota"), "caricato": False})
    piena = finestra.albero.AppendItem(finestra.nodo_pc, "Piena", data={"tipo": "cartella", "percorso": str(tmp_path / "Piena"), "caricato": False})
    # Una cartella con dei file resta, senza domande.
    finestra._al_cestino(piena)
    assert not domande and suoni_annotati[-1] == "non_disponibile"
    assert _ultima(finestra) == "Piena non è vuota: ci sono dei file, anche se MeTeOra magari non li suona. Maiuscolo+Canc manda nel cestino solo le cartelle vuote."
    # Quella vuota chiede, con No che la lascia dov'e'.
    finestra._al_cestino(vuota)
    assert domande[-1] == (f"Mandare nel cestino di Windows la cartella vuota {tmp_path / 'Vuota'}?", "Manda nel cestino")
    assert _ultima(finestra) == "La cartella resta dov'è." and not cestinati
    finestra._seleziona(vuota)
    finestra._al_cestino(vuota)
    assert cestinati == [str(tmp_path / "Vuota")] and suoni_annotati[-1] == "cestino"
    assert _ultima(finestra) == "La cartella Vuota è nel cestino di Windows."
    # La voce sparisce, e la selezione va sulla vicina.
    assert "Vuota" not in _etichette(finestra, finestra.nodo_pc) and finestra.albero.GetItemText(finestra._voce_corrente()) == "Piena"


def test_maiuscolo_canc_dove_il_cestino_non_c_e(finestra, suoni_annotati, tmp_path, monkeypatch):
    # In rete e sulle chiavette Windows cancella per sempre: la domanda e la
    # risposta lo dicono, invece di parlare del cestino.
    import questo_pc

    domande = []
    monkeypatch.setattr(questo_pc, "nel_cestino", lambda p: True)
    monkeypatch.setattr(questo_pc, "ha_il_cestino", lambda p: False)
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo: domande.append((domanda, titolo)) or True)
    (tmp_path / "a.mp3").write_bytes(b"")
    finestra._aggiungi(None, [str(tmp_path / "a.mp3")])
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    finestra._al_cestino(next(finestra._figli(nodo)))
    assert domande[-1][1] == "Cancella per sempre" and domande[-1][0].startswith(f"Cancellare per sempre il file {tmp_path / 'a.mp3'}? Lì il cestino di Windows non c'è.")
    assert _ultima(finestra) == "a.mp3 è cancellato per sempre."
    # Un percorso di Questa rete non e' una cartella da cestinare.
    finestra.albero.Expand(finestra.nodo_rete)
    radice = finestra.albero.AppendItem(finestra.nodo_rete, "nas", data={"tipo": "cartella", "percorso": "\\\\nas\\musica", "nome": "nas", "caricato": False})
    finestra._al_cestino(radice)
    assert _ultima(finestra) == "nas è un percorso di rete, non una cartella da cestinare." and len(domande) == 1


def _dettagli_subito(finestra, monkeypatch):
    """I dettagli raccolti subito, nel filo della prova."""
    monkeypatch.setattr(finestra, "_in_disparte", lambda lavoro, al_termine: al_termine(lavoro()))


def test_f11_su_una_cartella_scrive_i_dettagli(finestra, monkeypatch, suoni_annotati, tmp_path):
    # 1.77.0, Gabriele: su un contenitore F11 scrive i dettagli nella console.
    _dettagli_subito(finestra, monkeypatch)
    (tmp_path / "Disco" / "Dentro").mkdir(parents=True)
    (tmp_path / "Disco" / "a.mp3").write_bytes(b"x" * 2048)
    (tmp_path / "Disco" / "Dentro" / "note.txt").write_bytes(b"x")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Disco", data={"tipo": "cartella", "percorso": str(tmp_path / "Disco"), "caricato": False})
    finestra._seleziona(nodo)
    _tasto(finestra, codice=wx.WXK_F11)
    assert suoni_annotati[-1] == "dettagli"
    righe = [r.split(" - ")[0] for r in finestra._righe[-8:]]
    assert f"Cartella Disco: {tmp_path / 'Disco'}." in "\n".join(finestra._righe[-10:])
    assert any("Da suonare: 1 file, sottocartelle comprese, 2.0 KB." in r for r in finestra._righe[-10:])
    assert any("Tutti i file: 2, 2.0 KB, nascosti e di ogni tipo compresi." in r for r in finestra._righe[-10:]), righe
    # Il menu della cartella ha la voce che fa lo stesso.
    assert "Leggi i dettagli" in [nome for nome, _azione in finestra._voci_del_menu(finestra._dati(nodo))]


def test_f11_su_una_playlist_e_sul_ramo_playlist(finestra, monkeypatch, suoni_annotati, tmp_path):
    _dettagli_subito(finestra, monkeypatch)
    for nome in ("a.mp3", "b.sid"):
        (tmp_path / nome).write_bytes(b"x" * 1024)
    finestra._aggiungi(None, [str(tmp_path / "a.mp3"), str(tmp_path / "b.sid"), os.path.join(r"C:\sparito", "c.mp3")])
    pl = finestra.archivio.playlist[0]
    pl.brani[1].saltato = True
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra._seleziona(nodo)
    _tasto(finestra, codice=wx.WXK_F11)
    testo = "\n".join(finestra._righe[-8:])
    assert f"Playlist {pl.nome}: 3 brani." in testo and "Sul disco: 2.0 KB." in testo and "Tipi: mp3 2, sid 1." in testo
    assert "Saltati: 1." in testo and f"Mancanti sul disco: 1; il primo è {os.path.join(r'C:\sparito', 'c.mp3')}." in testo
    finestra._seleziona(finestra.nodo_playlist)
    _tasto(finestra, codice=wx.WXK_F11)
    assert any(f"{pl.nome}: 3 brani" in r for r in finestra._righe[-3:]) and any("Playlist: 1, con 3 brani in tutto." in r for r in finestra._righe[-5:])


def test_il_cestino_rifa_i_conti_e_la_cartella_dice_vuota(finestra, monkeypatch, suoni_annotati, tmp_path):
    # 1.77.0, Gabriele: dopo il cestino i conti delle cartelle si rifanno, e
    # una cartella rimasta senza niente da suonare resta, e dice (vuota).
    import questo_pc

    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo: True)

    def nel_cestino(percorso):
        os.remove(percorso)
        return True

    monkeypatch.setattr(questo_pc, "nel_cestino", nel_cestino)
    base = tmp_path / "Disco"
    (base / "Musica").mkdir(parents=True)
    for nome in ("uno.mp3", "due.mp3"):
        (base / "Musica" / nome).write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Disco", data={"tipo": "cartella", "percorso": str(base), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra.albero.Expand(nodo)
    finestra.contatore.aspetta()
    finestra._conti_arrivati()
    musica = next(finestra._figli(nodo))
    assert finestra.albero.GetItemText(musica) == "Musica, 2 file"
    finestra.albero.Expand(musica)
    for _ in range(2):
        finestra._al_cestino(next(finestra._figli(musica)))
        finestra.contatore.aspetta()
        finestra._conti_arrivati()
    # La cartella resta, e dice (vuota).
    assert finestra.albero.GetItemText(musica) == "Musica (vuota)"


def test_il_cestino_di_una_cartella_non_perde_i_conti_di_sopra(finestra, monkeypatch, suoni_annotati, tmp_path):
    # Revisione 1.77.0: svuotata e poi cestinata una cartella, la cartella che
    # la conteneva dice ancora i suoi conti.
    import shutil

    import questo_pc

    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo: True)

    def nel_cestino(percorso):
        if os.path.isdir(percorso):
            shutil.rmtree(percorso)
        else:
            os.remove(percorso)
        return True

    monkeypatch.setattr(questo_pc, "nel_cestino", nel_cestino)
    base = tmp_path / "Disco"
    (base / "Musica" / "X").mkdir(parents=True)
    (base / "Musica" / "X" / "a.mp3").write_bytes(b"")
    (base / "Musica" / "b.mp3").write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Disco", data={"tipo": "cartella", "percorso": str(base), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra.albero.Expand(nodo)
    finestra.contatore.aspetta()
    finestra._conti_arrivati()
    musica = next(finestra._figli(nodo))
    finestra.albero.Expand(musica)
    finestra.contatore.aspetta()
    finestra._conti_arrivati()
    x = next(v for v in finestra._figli(musica) if (finestra._dati(v) or {}).get("tipo") == "cartella")
    finestra.albero.Expand(x)
    finestra._al_cestino(next(finestra._figli(x)))
    finestra.contatore.aspetta()
    finestra._conti_arrivati()
    assert finestra.albero.GetItemText(x) == "X (vuota)" and finestra.albero.GetItemText(musica) == "Musica, 1 file"
    # Il nome nella frase e' quello della cartella, senza l'etichetta.
    finestra._al_cestino(x)
    assert _ultima(finestra) == "La cartella X è nel cestino di Windows."
    finestra.contatore.aspetta()
    finestra._conti_arrivati()
    assert finestra.albero.GetItemText(musica) == "Musica, 1 file"


def test_i_dettagli_del_menu_e_quelli_in_ritardo(finestra, monkeypatch, suoni_annotati, tmp_path):
    # Revisione 1.77.0: la voce del menu vale per la voce del menu, anche se
    # il fuoco si sposta; i dettagli che arrivano quando il fuoco e' altrove
    # si scrivono senza portarlo via.
    rimandati = []
    monkeypatch.setattr(finestra, "_in_disparte", lambda lavoro, al_termine: rimandati.append((lavoro, al_termine)))
    portati = []
    monkeypatch.setattr(finestra, "_porta_il_cursore", portati.append)
    (tmp_path / "Disco").mkdir()
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Disco", data={"tipo": "cartella", "percorso": str(tmp_path / "Disco"), "caricato": False})
    voci = dict(finestra._voci_del_menu(finestra._dati(nodo)))
    finestra._seleziona(finestra.nodo_playlist)
    voci["Leggi i dettagli"]()
    lavoro, al_termine = rimandati[-1]
    righe = lavoro()
    assert righe[0] == f"Cartella Disco: {tmp_path / 'Disco'}."
    al_termine(righe)
    assert not portati and suoni_annotati[-1] == "dettagli"
    assert any(r.startswith(f"Cartella Disco: {tmp_path / 'Disco'}.") for r in finestra._righe[-3:])
    # Un F11 sui tag interrompe i dettagli chiesti prima: quando arrivano, tacciono.
    finestra._seleziona(nodo)
    _tasto(finestra, codice=wx.WXK_F11)
    lavoro, al_termine = rimandati[-1]
    righe_prima = len(finestra._righe)
    finestra._dettagli_attesi = None
    al_termine(lavoro())
    assert len(finestra._righe) == righe_prima


def test_le_cartelle_di_rete_che_non_rispondono(finestra, monkeypatch, suoni_annotati, tmp_path):
    # 1.77.1: un conto parziale lo dice l'etichetta, e la cartella non
    # sparisce. 1.85.5: l'etichetta dice che e' una cartella a non rispondere,
    # non la rete; un ramo di una radice lasciata perdere si apre lo stesso, e
    # la radice torna viva, con i conti parziali da rifare (collaudo della
    # 1.85.2: l'Iliadbox rispondeva, e MeTeOra diceva il contrario).
    (tmp_path / "Rete" / "Muta").mkdir(parents=True)
    (tmp_path / "Rete" / "canzone.mp3").write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Muta", data={"tipo": "cartella", "percorso": str(tmp_path / "Rete" / "Muta"), "caricato": False})
    finestra.contatore.conti[str(tmp_path / "Rete" / "Muta")] = []
    finestra.contatore.parziali.add(str(tmp_path / "Rete" / "Muta"))
    finestra._aggiorna_cartelle()
    assert finestra.albero.GetItemText(nodo) == "Muta (conto incompleto: una cartella di rete non risponde)"
    finestra.contatore.conti[str(tmp_path / "Rete" / "Muta")] = [str(tmp_path / "a.mp3")]
    finestra._aggiorna_cartelle()
    assert finestra.albero.GetItemText(nodo) == "Muta, almeno 1 file: una cartella di rete non risponde"
    monkeypatch.setattr(modulo, "in_rete", lambda percorso: True)
    richiesti = []
    vero_chiedi = finestra.contatore.chiedi
    monkeypatch.setattr(finestra.contatore, "chiedi", lambda cartelle: (richiesti.extend(cartelle), vero_chiedi([]))[1])
    radice = os.path.splitdrive(str(tmp_path))[0].lower()
    finestra.contatore.mute.add(radice)
    # Il conto parziale di chi contiene il ramo: lo rifa' solo la radice tornata viva.
    finestra.contatore.conti[str(tmp_path)] = []
    finestra.contatore.parziali.add(str(tmp_path))
    # La prova dei tre secondi non si fa piu': la prima lettura dell'Iliadbox ne chiede quasi tre.
    sondate = []
    monkeypatch.setattr(modulo.questa_rete, "raggiungibile", lambda percorso, attesa=3.0: sondate.append(percorso) or False)
    figlio = finestra.albero.AppendItem(finestra.nodo_pc, "Altra", data={"tipo": "cartella", "percorso": str(tmp_path / "Rete"), "caricato": False})
    finestra.albero.SetItemHasChildren(figlio, True)
    finestra.albero.Expand(figlio)
    assert "canzone.mp3" in _etichette(finestra, figlio) and radice not in finestra.contatore.mute and sondate == []
    assert str(tmp_path) in richiesti and str(tmp_path) not in finestra.contatore.parziali
    assert str(tmp_path / "Rete" / "Muta") in richiesti and str(tmp_path / "Rete" / "Muta") not in finestra.contatore.parziali
    # Un ramo che tace lo dice, si riapre per riprovare, e il contatore non lo rilegge.
    monkeypatch.setattr(modulo, "leggi_in_rete", lambda cartella, attesa=None, fermo=None: (_ for _ in ()).throw(modulo.NonRisponde(cartella)))
    altro = finestra.albero.AppendItem(finestra.nodo_pc, "Spenta", data={"tipo": "cartella", "percorso": str(tmp_path / "Spenta"), "caricato": False})
    finestra.albero.SetItemHasChildren(altro, True)
    finestra.albero.Expand(altro)
    assert suoni_annotati[-1] == "errore" and _ultima(finestra) == (f"{tmp_path / 'Spenta'} non risponde: il computer o il disco di rete sono "
        "spenti, la rete non c'è, o la condivisione si è fermata. Riaprendo il ramo si riprova.")
    assert not list(finestra._figli(altro)) and finestra._dati(altro)["caricato"] is False
    assert str(tmp_path / "Spenta").lower() in finestra.contatore.cartelle_mute and radice not in finestra.contatore.mute


def _plancia_di_prova(finestra, monkeypatch, tmp_path):
    """Una playlist con tre brani e un'unita' finta in Questo PC, con due
    cartelle; il lavoro a pezzi dell'apertura si fa tutto subito."""
    for cartella in ("Uno/Dentro", "Due"):
        (tmp_path / "Disco" / cartella).mkdir(parents=True)
    for nome in ("Uno/a.mp3", "Uno/Dentro/b.mp3", "Due/c.mp3"):
        (tmp_path / "Disco" / nome).write_bytes(b"")
    monkeypatch.setattr(modulo.questo_pc, "unita", lambda: [(str(tmp_path / "Disco"), "Prova")])
    # Gli avvisi dei fili del contatore e dello schedario si mettono in fila,
    # e li esegue il filo della finestra; l'apertura aspetta i conti delle
    # cartelle, qui con l'attesa del contatore, mai mentre il contatore le
    # cede il passo.
    rimandate = []

    def subito(funzione, *argomenti):
        if threading.current_thread() is threading.main_thread():
            funzione(*argomenti)
        else:
            rimandate.append((funzione, argomenti))

    def piu_tardi(_ms, funzione, *argomenti):
        if threading.current_thread() is threading.main_thread() and not finestra._cedi.is_set():
            finestra.contatore.aspetta()
            while rimandate:
                rimandata, suoi = rimandate.pop(0)
                rimandata(*suoi)
        funzione(*argomenti)

    monkeypatch.setattr(modulo.wx, "CallAfter", subito)
    monkeypatch.setattr(modulo.wx, "CallLater", piu_tardi)
    finestra._aggiungi(None, [os.path.join(r"C:\m", n) for n in ("a.mp3", "b.mp3", "c.mp3")])


def test_maiuscolo_f10_apre_tutta_la_plancia_e_maiuscolo_f9_la_chiude(finestra, monkeypatch, suoni_annotati, tmp_path):
    # 1.79.0, Gabriele: Maiuscolo con F10 apre tutto, con un suono all'inizio
    # e uno alla fine; Maiuscolo con F9 chiude tutto. Dalla 1.83.1 Questo PC
    # resta chiuso, come Questa rete: i dischi interi fermavano la finestra.
    _plancia_di_prova(finestra, monkeypatch, tmp_path)
    _tasto(finestra, codice=wx.WXK_F10, maiuscolo=True)
    # Istantanea: solo il suono di fine, che non si sovrappone a quello d'inizio (1.83.2).
    assert "apri_la_plancia" not in suoni_annotati and suoni_annotati[-1] == "plancia_aperta"
    assert _ultima(finestra).startswith("Aperta tutta la plancia, tranne Questo PC e Questa rete: ")
    playlist = next(finestra._figli(finestra.nodo_playlist))
    assert finestra.albero.IsExpanded(finestra.nodo_playlist) and finestra.albero.IsExpanded(playlist)
    assert not finestra.albero.IsExpanded(finestra.nodo_pc) and not finestra.albero.IsExpanded(finestra.nodo_rete)
    # Aperto a mano fino in fondo, Maiuscolo con F9 chiude anche lui.
    finestra.albero.Expand(finestra.nodo_pc)
    disco = next(finestra._figli(finestra.nodo_pc))
    finestra.albero.Expand(disco)
    uno = next(v for v in finestra._figli(disco) if finestra.albero.GetItemText(v).startswith("Uno"))
    finestra.albero.Expand(uno)
    dentro = next(v for v in finestra._figli(uno) if (finestra._dati(v) or {}).get("tipo") == "cartella")
    finestra.albero.Expand(dentro)
    finestra._seleziona(next(finestra._figli(dentro)))
    _tasto(finestra, codice=wx.WXK_F9, maiuscolo=True)
    assert suoni_annotati[-1] == "chiudi_la_plancia" and _ultima(finestra) == "Chiusa tutta la plancia."
    assert not any(finestra.albero.IsExpanded(v) for v in finestra._figli(finestra.albero.GetRootItem()))
    # Il fuoco sulla voce di primo livello che conteneva quella di prima.
    assert finestra._voce_corrente() == finestra.nodo_pc


def test_maiuscolo_f10_si_ferma_al_massimo_e_con_un_tasto(finestra, monkeypatch, suoni_annotati, tmp_path):
    _plancia_di_prova(finestra, monkeypatch, tmp_path)
    monkeypatch.setattr(modulo, "MASSIMO_DI_RAMI", 2)
    _tasto(finestra, codice=wx.WXK_F10, maiuscolo=True)
    assert _ultima(finestra).startswith("Aperti 2 rami, ") and _ultima(finestra).endswith(" voci; mi fermo qui, gli altri restano chiusi.")
    # Un tasto qualsiasi, mentre l'apertura lavora, la ferma.
    finestra._apertura_della_plancia = object()
    _tasto(finestra, codice=wx.WXK_DOWN)
    assert finestra._apertura_della_plancia is None and "annullamento" in suoni_annotati
    assert any("Apertura della plancia fermata" in r for r in finestra._righe[-3:])


class _LetturaFinta:
    """Una lettura di sottotitoli_ocr finta: annota chi la crea e la ferma."""

    create = None

    def __init__(self, motore, dici, lingua, guasto=None):
        self.lingua, self.dici, self.guasto, self.fermata = lingua, dici, guasto, False
        _LetturaFinta.create.append(self)

    def avvia(self):
        return self

    def ferma(self):
        self.fermata = True

    def nuovo_sottotitolo(self):
        self.dici("letto")


def _ocr_finto(finestra, monkeypatch):
    import ocr
    import sottotitoli_ocr

    _LetturaFinta.create = []
    immagini = type("LetturaDelleImmaginiFinta", (_LetturaFinta,), {"tipo": "immagini"})
    impressi = type("LetturaDegliImpressiFinta", (_LetturaFinta,), {"tipo": "impressi"})
    monkeypatch.setattr(sottotitoli_ocr, "LetturaDelleImmagini", immagini)
    monkeypatch.setattr(sottotitoli_ocr, "LetturaDegliImpressi", impressi)
    monkeypatch.setattr(ocr, "disponibile", lambda: True)
    monkeypatch.setattr(ocr, "lingua_per", lambda etichetta: "en-US" if etichetta == "eng" else "it-IT")
    video_letto = []
    monkeypatch.setattr(finestra.motore, "leggi_il_video", lambda serve, oscura=False: video_letto.append(serve))
    return video_letto


def test_maiuscolo_f2_con_le_immagini_e_gli_impressi(finestra, monkeypatch, suoni_annotati):
    # 1.80.0, Gabriele: una traccia a immagini la legge il riconoscimento; in
    # fondo al giro, sui video, i sottotitoli impressi, letti al volo.
    tracce = _tracce(sottotitoli=2)
    tracce["sub"][1].update(codec="dvd_subtitle", lang="eng", title="")
    stato, chiamate = _video_finto(finestra, monkeypatch, tracce)
    video_letto = _ocr_finto(finestra, monkeypatch)
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert chiamate[-1] == ("sid", "1") and finestra._lettura is None
    stato["tracce"] = _tracce(sottotitoli=2, scelto_sub=0)
    stato["tracce"]["sub"][1].update(codec="dvd_subtitle", lang="eng", title="")
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert chiamate[-1] == ("sid", "2") and finestra._lettura.tipo == "immagini" and finestra._lettura.lingua == "en-US"
    assert _ultima(finestra).endswith("È fatta di immagini: la legge il riconoscimento dei caratteri di Windows.") and video_letto[-1] is True
    # Il sottotitolo che comincia arriva alla lettura, che lo legge.
    finestra._sottotitolo_a_immagini()
    stato["tracce"] = _tracce(sottotitoli=2, scelto_sub=1)
    stato["tracce"]["sub"][1].update(codec="dvd_subtitle", lang="eng", title="")
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert chiamate[-1] == ("sid", "no") and finestra.impostazioni["impressi_scelti"] and finestra._lettura.tipo == "impressi"
    assert _ultima(finestra) == "Sottotitoli impressi, letti al volo." and finestra.impostazioni["sottotitoli"] is True
    assert _LetturaFinta.create[0].fermata
    stato["tracce"] = _tracce(sottotitoli=2)
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert _ultima(finestra) == "Sottotitoli letti spenti." and finestra._lettura is None and not finestra.impostazioni["impressi_scelti"]
    assert video_letto[-1] is False and finestra.impostazioni["sottotitoli"] is False


def test_gli_impressi_con_la_passata(finestra, monkeypatch, suoni_annotati, tmp_path):
    # Con la passata scelta nelle impostazioni: senza file la passata parte e
    # intanto si legge al volo; finita, il file diventa la traccia del video.
    import sottotitoli_ocr

    stato, chiamate = _video_finto(finestra, monkeypatch, _tracce())
    _ocr_finto(finestra, monkeypatch)
    finestra.impostazioni["impressi"] = "passata"
    passate = []

    class PassataFinta:
        def __init__(self, video, lingua, avanza, finita):
            self.video, self.lingua, self.avanza, self.finita = video, lingua, avanza, finita
            passate.append(self)

        def avvia(self):
            return self

        def ferma(self):
            pass

    monkeypatch.setattr(sottotitoli_ocr, "PassataDegliImpressi", PassataFinta)
    aggiunti = []
    monkeypatch.setattr(finestra.motore, "aggiungi_sottotitoli", lambda percorso, titolo, lingua, scegli=True: aggiunti.append((percorso, titolo, lingua, scegli)))
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert len(passate) == 1 and passate[0].video == stato["in_corso"] and finestra._lettura.tipo == "impressi"
    assert "passata_avviata" in suoni_annotati
    assert _ultima(finestra) == "Sottotitoli impressi, letti al volo mentre la passata li prepara per le volte dopo."
    file_scritto = tmp_path / "film.impressi.it.srt"
    file_scritto.write_text("1\n00:00:01,000 --> 00:00:02,000\nCiao\n", encoding="utf-8")
    finestra._passata_avanza(stato["in_corso"], 50)
    assert _ultima(finestra) == "Passata dei sottotitoli impressi di film.mkv: 50%."
    finestra._passata_finita(stato["in_corso"], str(file_scritto))
    assert aggiunti == [(str(file_scritto), "Sottotitoli impressi", "it", True)] and finestra._lettura is None and suoni_annotati[-1] == "passata_finita"
    # Con il file gia' fatto, che il motore ha aggiunto come traccia, il passo
    # degli impressi sceglie quello; e il giro dopo arriva a spenti.
    stato["tracce"] = _tracce(sottotitoli=1)
    stato["tracce"]["sub"][0]["title"] = "Sottotitoli impressi"
    finestra.impostazioni["sottotitoli"] = False
    finestra.impostazioni["impressi_scelti"] = False
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert chiamate[-1] == ("sid", "1") and _ultima(finestra) == "Sottotitoli impressi, dal file della passata fatta prima." and len(passate) == 1
    stato["tracce"] = _tracce(sottotitoli=1, scelto_sub=0)
    stato["tracce"]["sub"][0]["title"] = "Sottotitoli impressi"
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert _ultima(finestra) == "Sottotitoli letti spenti." and chiamate[-1] == ("sid", "no")


def test_l_impostazione_degli_impressi(finestra, monkeypatch, suoni_annotati):
    lista = _ListaFinta()
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaFinta(1))
    finestra._cambia_impostazione("impressi", lista)
    assert finestra.impostazioni["impressi"] == "passata" and _salvate(finestra)["impressi"] == "passata"
    assert finestra._riga_dell_impostazione("impressi") == "Sottotitoli impressi: letti prima, con una passata che salva accanto al video un file usato le volte dopo"


def test_il_motore_aggiunge_i_file_delle_passate(finestra, tmp_path):
    # Un video appena aperto: i file delle passate fatte prima diventano tracce.
    (tmp_path / "Film.impressi.it.srt").write_text("")
    comandi, avvisi = [], []

    def comando(*argomenti, risposta=None):
        comandi.append(argomenti)
        if risposta is not None:
            risposta(None, None)

    film = str(tmp_path / "Film.mkv")
    lettore = types.SimpleNamespace(percorso=film, _richieste=1, comando=comando)
    # L'avviso del caricamento arriva quando mpv ha aggiunto il file: chi
    # legge le tracce lo trova.
    finestra.motore._aggiungi_le_passate(lettore, film, 1, lambda: avvisi.append(len(comandi)))
    assert comandi == [("sub-add", str(tmp_path / "Film.impressi.it.srt"), "auto", "Sottotitoli impressi", "it")] and avvisi == [1]
    finestra.motore._aggiungi_le_passate(lettore, str(tmp_path / "Film.mp3"), 1, lambda: avvisi.append(len(comandi)))
    assert len(comandi) == 1 and avvisi == [1, 1]
    # Revisione 1.83.0: un video ricaricato intanto non prende le passate.
    lettore._richieste = 2
    finestra.motore._aggiungi_le_passate(lettore, film, 1, lambda: avvisi.append(len(comandi)))
    assert len(comandi) == 1 and avvisi == [1, 1, 1]


def test_senza_riconoscimento_il_giro_arriva_a_spenti(finestra, monkeypatch, suoni_annotati):
    # Revisione 1.80.0: senza il riconoscimento, sui video il passo degli
    # impressi non c'e', e Maiuscolo con F2 spegne come prima.
    import ocr

    stato, _chiamate = _video_finto(finestra, monkeypatch, _tracce(sottotitoli=1))
    monkeypatch.setattr(ocr, "disponibile", lambda: False)
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    stato["tracce"] = _tracce(sottotitoli=1, scelto_sub=0)
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert _ultima(finestra) == "Sottotitoli letti spenti." and finestra.impostazioni["sottotitoli"] is False
    stato["tracce"] = _tracce()
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert _ultima(finestra) == "Sottotitoli letti accesi; questo brano non ne ha."


def test_la_traccia_a_immagini_scelta_all_apertura_si_legge(finestra, monkeypatch, suoni_annotati):
    # Revisione 1.80.0: la prima traccia scelta da MeTeOra all'apertura del
    # brano, se e' a immagini, fa partire la lettura.
    tracce = _tracce(sottotitoli=1)
    tracce["sub"][0].update(codec="hdmv_pgs_subtitle", lang="eng")
    _stato, chiamate = _video_finto(finestra, monkeypatch, tracce)
    video_letto = _ocr_finto(finestra, monkeypatch)
    finestra.impostazioni["sottotitoli"] = True
    finestra._aggiorna_il_video()
    assert ("sid", "1") in chiamate and finestra._lettura.tipo == "immagini" and finestra._lettura.lingua == "en-US" and video_letto[-1] is True


def test_la_passata_finita_non_toglie_la_traccia_scelta(finestra, monkeypatch, suoni_annotati, tmp_path):
    # Revisione 1.80.0: chi durante la passata ha scelto un'altra traccia la
    # tiene; il file si aggiunge per le volte dopo.
    import sottotitoli_ocr

    stato, _chiamate = _video_finto(finestra, monkeypatch, _tracce(sottotitoli=1))
    _ocr_finto(finestra, monkeypatch)
    aggiunti = []
    monkeypatch.setattr(finestra.motore, "aggiungi_sottotitoli", lambda percorso, titolo, lingua, scegli=True: aggiunti.append(scegli))
    finestra._passata = types.SimpleNamespace(video=stato["in_corso"], lingua="it-IT", ferma=lambda: None)
    finestra.impostazioni["sottotitoli"] = True
    finestra.impostazioni["impressi_scelti"] = False
    file_scritto = tmp_path / "film.impressi.it.srt"
    file_scritto.write_text("1\n00:00:01,000 --> 00:00:02,000\nCiao\n", encoding="utf-8")
    finestra._passata_finita(stato["in_corso"], str(file_scritto))
    assert aggiunti == [False] and "Maiuscolo con F2 li sceglie" in _ultima(finestra)
    # Una passata che non trova niente non si rifa' nella stessa sessione.
    finestra._passata = types.SimpleNamespace(video=stato["in_corso"], lingua="it-IT", ferma=lambda: None)
    finestra._passata_finita(stato["in_corso"], None)
    assert stato["in_corso"] in finestra._passate_vuote
    assert sottotitoli_ocr.VELOCITA_DELLA_PASSATA == 5


def test_le_impostazioni_del_karaoke(finestra, monkeypatch, suoni_annotati, sintesi_finta):
    impostati = []
    monkeypatch.setattr(finestra.motore, "imposta_il_karaoke", lambda modo, anticipo: impostati.append((modo, anticipo)))
    # Dove vanno sottotitoli e karaoke: solo al braille.
    scelta = _SceltaFinta(2)
    monkeypatch.setattr(modulo, "FinestraScelta", scelta)
    lista = _ListaFinta()
    finestra._cambia_impostazione("destinazione", lista)
    assert scelta.aperture[0] == ("Dove vanno sottotitoli e karaoke", ["Alla sintesi e al braille", "Solo alla sintesi", "Solo al braille"], 0)
    assert finestra.impostazioni["destinazione"] == "braille" and _salvate(finestra)["destinazione"] == "braille"
    assert lista.righe["destinazione"] == "Dove vanno sottotitoli e karaoke: solo al braille"
    assert _ultima(finestra) == "Sottotitoli e karaoke ora vanno solo al braille."
    finestra.impostazioni["sottotitoli"] = True
    finestra._sottotitolo("Prima riga")
    assert sintesi_finta.braille == [("nvda", "Prima riga")] and not sintesi_finta.detti and _ultima(finestra) == "Prima riga"
    # Il testo del karaoke per strofa: il motore rifa' la traccia.
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaFinta(1))
    finestra._cambia_impostazione("karaoke", lista)
    assert finestra.impostazioni["karaoke"] == "strofa" and impostati[-1] == ("strofa", 0)
    assert lista.righe["karaoke"] == "Testo del karaoke: per strofa, dove il file le segna; altrimenti per riga"
    # Annullata, la scelta resta.
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaFinta(None))
    finestra._cambia_impostazione("karaoke", lista)
    assert finestra.impostazioni["karaoke"] == "strofa" and len(impostati) == 1 and _ultima(finestra) == "Testo del karaoke: non cambiato."
    # L'anticipo, in millesimi, con il limite.
    _campo, lista = _cambia(finestra, monkeypatch, "anticipo_karaoke", "500")
    assert finestra.impostazioni["anticipo_karaoke"] == 500 and impostati[-1] == ("strofa", 500)
    assert lista.righe["anticipo_karaoke"] == "Anticipo del karaoke: 500 ms"
    assert _ultima(finestra) == "Il testo del karaoke ora arriva 500 millesimi prima del canto."
    _cambia(finestra, monkeypatch, "anticipo_karaoke", "20000")
    assert finestra.impostazioni["anticipo_karaoke"] == 10000
    _cambia(finestra, monkeypatch, "anticipo_karaoke", "0")
    assert _ultima(finestra) == "Il testo del karaoke ora arriva quando comincia il canto."


def test_maiuscolo_f2_sul_testo_del_karaoke(finestra, monkeypatch, suoni_annotati):
    tracce = _tracce(video=False, sottotitoli=1)
    tracce["sub"][0].update(title="Testo del karaoke, dal MIDI", lang=None)
    stato, chiamate = _video_finto(finestra, monkeypatch, tracce)
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert chiamate[-1] == ("sid", "1") and _ultima(finestra) == "Testo del karaoke letto, dal MIDI."
    stato["tracce"] = _tracce(video=False, sottotitoli=1, scelto_sub=0)
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert _ultima(finestra) == "Sottotitoli letti spenti."
    # Accesi, il prossimo brano con il testo lo prende da solo.
    stato["tracce"] = tracce
    finestra.impostazioni["sottotitoli"] = True
    finestra._aggiorna_il_video()
    assert chiamate[-1] == ("sid", "1")


class _LettoreDelKaraoke:
    """Un lettore del motore finto: annota i comandi, tiene la lista delle
    tracce come farebbe mpv, e con trattieni tiene in sospeso le risposte."""

    def __init__(self, percorso):
        import motore

        self.percorso, self._richieste, self.pronto = percorso, 1, True
        self.karaoke = self.formato_imposto = None
        self.karaoke_in_volo = self.karaoke_da_rifare = False
        self.comandi, self.in_sospeso, self.trattieni = [], [], False
        self.mpv = types.SimpleNamespace(track_list=[])
        self.aggiungi_testo = types.MethodType(motore._Lettore.aggiungi_testo, self)

    def comando(self, *argomenti, risposta=None):
        self.comandi.append(argomenti)
        tracce = self.mpv.track_list
        if argomenti[0] == "sub-add":
            tracce.append({"type": "sub", "id": max((t["id"] for t in tracce), default=0) + 1, "title": argomenti[3], "selected": argomenti[2] == "select"})
        elif argomenti[0] == "sub-remove":
            tracce[:] = [t for t in tracce if str(t["id"]) != argomenti[1]]
        elif argomenti[:2] == ("set", "sid"):
            for traccia in tracce:
                traccia["selected"] = str(traccia["id"]) == argomenti[2]
        if risposta is not None:
            if self.trattieni:
                self.in_sospeso.append(risposta)
            else:
                risposta(None, None)


def test_il_motore_aggiunge_il_testo_del_karaoke(finestra, tmp_path, monkeypatch):
    brano = tmp_path / "Canzone.mp3"
    brano.write_bytes(b"")
    (tmp_path / "Canzone.lrc").write_text("[00:01.00]Prima\n[00:02.00]Seconda\n", encoding="utf-8")
    avvisi = []
    lettore = _LettoreDelKaraoke(str(brano))
    finestra.motore._aggiungi_le_tracce(lettore, str(brano), 1, lambda: avvisi.append(len(lettore.comandi)))
    comandi = lettore.comandi
    assert comandi[0][0] == "sub-add" and comandi[0][2:] == ("auto", "Testo del karaoke, dal file LRC") and avvisi == [1]
    assert comandi[0][1].startswith("memory://1\n00:00:01,000 --> 00:00:02,000\nPrima\n") and lettore.karaoke[0] == "lrc"
    assert not lettore.karaoke_in_volo
    # Un brano ricaricato intanto, anche lo stesso, non prende il testo del
    # caricamento di prima: lo mette il suo.
    lettore._richieste = 2
    finestra.motore._aggiungi_le_tracce(lettore, str(brano), 1, lambda: avvisi.append(len(lettore.comandi)))
    assert len(comandi) == 1 and avvisi == [1, 1]
    # Un brano reso in RAM ha il formato WAV imposto: per l'aggiunta diventa
    # quello dei sottotitoli, fino al brano dopo.
    lettore = _LettoreDelKaraoke(str(brano))
    lettore.formato_imposto = "wav"
    finestra.motore._aggiungi_le_tracce(lettore, str(brano), 1)
    assert [c[:3] for c in lettore.comandi] == [("set", "file-local-options/demuxer-lavf-format", "srt"), ("sub-add", lettore.comandi[1][1], "auto")]
    # Un video, anche musicale, con il suo .lrc: le passate, poi il testo.
    video = tmp_path / "Clip.mkv"
    video.write_bytes(b"")
    (tmp_path / "Clip.lrc").write_text("[00:01.00]Dal video\n", encoding="utf-8")
    lettore = _LettoreDelKaraoke(str(video))
    finestra.motore._aggiungi_le_tracce(lettore, str(video), 1, lambda: avvisi.append("video"))
    assert [t["title"] for t in lettore.mpv.track_list] == ["Testo del karaoke, dal file LRC"] and avvisi[-1] == "video"


def test_il_karaoke_si_rifa_una_traccia_alla_volta(finestra, tmp_path, monkeypatch):
    # Revisione 1.82.0: due aggiunte insieme lasciavano due tracce, una con
    # l'anticipo vecchio; ora la seconda aspetta la prima, e resta l'ultima.
    brano = tmp_path / "Canzone.mp3"
    brano.write_bytes(b"")
    (tmp_path / "Canzone.lrc").write_text("[00:01.00]Prima\n[00:02.00]Seconda\n", encoding="utf-8")
    lettore = _LettoreDelKaraoke(str(brano))
    monkeypatch.setattr(finestra.motore, "_lettori", (lettore,))
    lettore.trattieni = True
    finestra.motore._aggiungi_le_tracce(lettore, str(brano), 1)
    assert lettore.karaoke_in_volo and len(lettore.mpv.track_list) == 1
    finestra.motore.imposta_il_karaoke("riga", 500)
    assert lettore.karaoke_da_rifare and len(lettore.mpv.track_list) == 1
    # Arriva la prima: la traccia si sceglie, e parte la seconda, con l'anticipo.
    lettore.mpv.track_list[0]["selected"] = True
    lettore.in_sospeso.pop(0)(None, None)
    assert len(lettore.mpv.track_list) == 2 and lettore.comandi[-1][1].startswith("memory://1\n00:00:00,500 --> ")
    # Arriva la seconda: la vecchia se ne va, e la scelta passa alla nuova.
    lettore.in_sospeso.pop(0)(None, None)
    assert [(t["id"], t["selected"]) for t in lettore.mpv.track_list] == [(2, True)]
    assert not lettore.karaoke_in_volo and not lettore.karaoke_da_rifare
    # Senza niente in volo si rifa' subito.
    lettore.trattieni = False
    finestra.motore.imposta_il_karaoke("strofa", 500)
    assert [(t["id"], t["selected"]) for t in lettore.mpv.track_list] == [(3, True)]


def test_gli_impressi_scelti_non_fermano_il_karaoke(finestra, monkeypatch, suoni_annotati):
    # Revisione 1.82.0: gli impressi scelti su un video valgono solo sui video.
    tracce = _tracce(video=False, sottotitoli=1)
    tracce["sub"][0].update(title="Testo del karaoke, dal MIDI", lang=None)
    stato, chiamate = _video_finto(finestra, monkeypatch, tracce)
    finestra.impostazioni["impressi_scelti"] = True
    finestra.impostazioni["sottotitoli"] = True
    finestra._aggiorna_il_video()
    assert chiamate[-1] == ("sid", "1")
    stato["tracce"] = _tracce(video=False, sottotitoli=1)
    stato["tracce"]["sub"][0].update(title="Testo del karaoke, dal MIDI", lang=None)
    _tasto(finestra, codice=wx.WXK_F2, maiuscolo=True)
    assert _ultima(finestra) == "Testo del karaoke letto, dal MIDI."


def test_la_destinazione_dice_se_il_braille_non_arriva(finestra, monkeypatch, suoni_annotati, sintesi_finta):
    sintesi_finta.attive["nvda"] = False
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaFinta(2))
    finestra._cambia_impostazione("destinazione", _ListaFinta())
    assert _ultima(finestra) == ("Sottotitoli e karaoke ora vanno solo al braille. Con la voce di Windows, SAPI5, il braille non arriva: "
        "ce l'hanno NVDA e JAWS.")
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaFinta(1))
    finestra._cambia_impostazione("destinazione", _ListaFinta())
    assert _ultima(finestra) == "Sottotitoli e karaoke ora vanno solo alla sintesi."


def test_la_barra_braille_a_blocchi(finestra, monkeypatch, suoni_annotati, sintesi_finta):
    # 1.83.0: alla voce il testo intero, subito; al braille i blocchi in fila.
    monkeypatch.setattr(finestra.motore, "resto_del_sottotitolo", lambda: 9.0)
    _campo, lista = _cambia(finestra, monkeypatch, "celle_braille", "20")
    assert finestra.impostazioni["celle_braille"] == 20 and lista.righe["celle_braille"] == "Celle della barra braille: 20"
    assert _ultima(finestra) == "Sottotitoli e karaoke ora arrivano al braille in blocchi di 20 celle al più."
    _campo, lista = _cambia(finestra, monkeypatch, "lettura_minima", "50")
    assert finestra.impostazioni["lettura_minima"] == 100 and lista.righe["lettura_minima"] == "Tempo minimo di lettura in braille: 100 ms"
    _cambia(finestra, monkeypatch, "lettura_minima", "1500")
    assert _ultima(finestra) == "Ogni blocco ora resta sulla barra braille almeno 1500 millesimi."
    finestra.impostazioni["sottotitoli"] = True
    finestra._sottotitolo("Partir effacer sur le Gange la douleur pouvoir parler à un ange")
    assert sintesi_finta.detti == [("nvda", "Partir effacer sur le Gange la douleur pouvoir parler à un ange")]
    assert sintesi_finta.braille == [("nvda", "Partir effacer sur")] and finestra._braille.in_fila == 3
    assert _ultima(finestra) == "Partir effacer sur le Gange la douleur pouvoir parler à un ange"
    # Spenti i sottotitoli, la fila si svuota; e anche a ogni salto del motore.
    finestra._applica_l_impostazione("sottotitoli", False)
    assert finestra._braille.in_fila == 0
    finestra.impostazioni["sottotitoli"] = True
    finestra._sottotitolo("Partir effacer sur le Gange la douleur pouvoir parler à un ange")
    assert finestra._braille.in_fila == 3
    finestra.motore.salta(5)
    assert finestra._braille.in_fila == 0
    finestra._sottotitolo("Partir effacer sur le Gange la douleur pouvoir parler à un ange")
    finestra.motore.stop()
    assert finestra._braille.in_fila == 0
    finestra.impostazioni["sottotitoli"] = False
    # Con 0 celle il testo arriva intero; solo alla sintesi, al braille niente.
    finestra.impostazioni.update(sottotitoli=True, celle_braille=0)
    finestra._braille.svuota()
    finestra._sottotitolo("Seconda riga")
    assert sintesi_finta.braille[-1] == ("nvda", "Seconda riga")
    finestra.impostazioni["destinazione"] = "sintesi"
    finestra._braille.svuota()
    finestra._sottotitolo("Terza riga")
    assert sintesi_finta.braille[-1] == ("nvda", "Seconda riga") and sintesi_finta.detti[-1] == ("nvda", "Terza riga")


def test_f10_su_un_disco_tace_le_cartelle_vuote(finestra, monkeypatch, suoni_annotati, tmp_path):
    # 1.83.1: aprendo un ramo intero le cartelle vuote non suonano una per
    # una, la cacofonia del collaudo della 1.83.0: la fine le conta.
    base = tmp_path / "Disco"
    for cartella in ("Musica", "Vuota", "Anche questa"):
        (base / cartella).mkdir(parents=True)
    (base / "Musica" / "a.mp3").write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Disco", data={"tipo": "cartella", "percorso": str(base), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra._seleziona(nodo)
    _tasto(finestra, codice=wx.WXK_F10)
    assert "niente_da_suonare" not in suoni_annotati and suoni_annotati[-1] == "apri_tutto"
    assert _ultima(finestra).startswith("Aperto tutto dentro ") and "Trovate 2 cartelle senza niente da suonare." in _ultima(finestra)
    assert finestra._taciuti is None
    # Aperta a mano, una cartella vuota suona come prima.
    vuota = next(v for v in finestra._figli(nodo) if finestra.albero.GetItemText(v).startswith("Vuota"))
    finestra.albero.Collapse(vuota)
    finestra._dati(vuota)["caricato"] = False
    finestra.albero.SetItemHasChildren(vuota, True)
    finestra.albero.Expand(vuota)
    assert suoni_annotati[-1] == "niente_da_suonare"


def test_i_totali_delle_cartelle_si_ricordano(finestra, monkeypatch, tmp_path):
    # 1.83.1: il totale si somma una volta, e lo aggiornano le variazioni
    # dello schedario; risommare tutto a ogni rinfresco fermava la finestra.
    base = tmp_path / "Disco"
    (base / "Musica").mkdir(parents=True)
    for nome in ("a.mp3", "b.mp3"):
        (base / "Musica" / nome).write_bytes(b"")
    finestra.albero.Expand(finestra.nodo_pc)
    nodo = finestra.albero.AppendItem(finestra.nodo_pc, "Disco", data={"tipo": "cartella", "percorso": str(base), "caricato": False})
    finestra.albero.SetItemHasChildren(nodo, True)
    finestra.albero.Expand(nodo)
    # Il conto del disco lo chiederebbe chi lo contiene, aprendosi.
    finestra.contatore.chiedi([str(base)])
    finestra.contatore.aspetta()
    finestra.schedario.aspetta()
    finestra._aggiorna_cartelle()
    somme = []
    vera = finestra.schedario.totale_delle_durate
    monkeypatch.setattr(finestra.schedario, "totale_delle_durate", lambda percorsi: somme.append(len(percorsi)) or vera(percorsi))
    finestra._aggiorna_cartelle()
    assert somme == []
    with finestra.schedario._lucchetto:
        finestra.schedario._metti(str(base / "Musica" / "a.mp3"), {"dim": 1, "mod": 0, "durata": 30.0, "tag": {}, "sottobrani": None, "durate_sid": None})
        finestra.schedario._metti(str(base / "Musica" / "b.mp3"), {"dim": 1, "mod": 0, "durata": 90.0, "tag": {}, "sottobrani": None, "durate_sid": None})
    finestra._aggiorna_cartelle()
    assert somme == [] and finestra.albero.GetItemText(nodo) == "Disco, 2 file, 2:00 in tutto"
    musica = next(finestra._figli(nodo))
    assert finestra.albero.GetItemText(musica) == "Musica, 2 file, 2:00 in tutto"
    # Una durata che cambia, o che sparisce, si toglie dal totale.
    with finestra.schedario._lucchetto:
        finestra.schedario._metti(str(base / "Musica" / "b.mp3"), {"dim": 2, "mod": 0, "durata": 60.0, "tag": {}, "sottobrani": None, "durate_sid": None})
        finestra.schedario._metti(str(base / "Musica" / "a.mp3"), None)
    finestra._aggiorna_cartelle()
    assert finestra.albero.GetItemText(nodo) == "Disco, 2 file, 1:00 in tutto, 1 senza durata"


def test_i_rinfreschi_si_accorpano_e_i_fili_cedono_il_passo(finestra, monkeypatch):
    # 1.83.1: piu' avvisi ravvicinati fanno un rinfresco solo, a distanza dal
    # precedente, e mentre rinfresca la finestra i fili aspettano.
    pianificati, visti = [], []
    monkeypatch.setattr(modulo.wx, "CallLater", lambda ms, funzione, *argomenti: pianificati.append((ms, funzione)))
    monkeypatch.setattr(finestra, "_schede_arrivate", lambda: visti.append(("schede", finestra.schedario.cedi.is_set(), finestra.contatore.cedi.is_set())))
    monkeypatch.setattr(finestra, "_conti_arrivati", lambda: visti.append(("conti", finestra._cedi.is_set())))
    finestra._rinfresco_chiesto("conti")
    finestra._rinfresco_chiesto("schede")
    finestra._rinfresco_chiesto("conti")
    assert len(pianificati) == 1
    pianificati.pop()[1]()
    assert visti == [("schede", True, True)] and not finestra._cedi.is_set()
    # Il prossimo aspetta tre volte la durata dell'ultimo.
    finestra._prossimo_rinfresco = time.monotonic() + 2
    finestra._rinfresco_chiesto("conti")
    assert pianificati[-1][0] > 1500
    pianificati.pop()[1]()
    assert visti[-1] == ("conti", True)


def test_f10_lungo_dice_l_inizio_e_la_fine_dopo(finestra, monkeypatch, suoni_annotati, tmp_path):
    # 1.83.2: un'apertura che dura suona l'inizio, e la fine aspetta che
    # l'inizio sia finito; F10 lavora a fette come Maiuscolo con F10.
    _plancia_di_prova(finestra, monkeypatch, tmp_path)
    monkeypatch.setattr(modulo, "RITARDO_DELL_AVVIO", 0)
    rimandati = []
    monkeypatch.setattr(finestra, "_dopo_il_suono", lambda funzione, *argomenti: rimandati.append((funzione, argomenti)))
    finestra.albero.Expand(finestra.nodo_pc)
    disco = next(finestra._figli(finestra.nodo_pc))
    finestra._seleziona(disco)
    _tasto(finestra, codice=wx.WXK_F10)
    assert suoni_annotati[-1] == "apri_la_plancia" and any(r.startswith("Apro tutto dentro ") for r in finestra._righe)
    assert _ultima(finestra).startswith("Aperto tutto dentro ") and [f.__name__ for f, _a in rimandati] == ["_suono"]
    assert rimandati[0][1] == ("apri_tutto",)
    uno = next(v for v in finestra._figli(disco) if finestra.albero.GetItemText(v).startswith("Uno"))
    assert finestra.albero.IsExpanded(uno)


def test_la_durata_vera_di_musepack_e_dsf(finestra, monkeypatch, tmp_path):
    # 1.83.3: libmpv stima male la durata dei Musepack SV8 e dei DSF; quella
    # vera la sa mutagen, e il motore la usa anche per la dissolvenza.
    import motore

    monkeypatch.setattr(motore, "_durata_da_mutagen", lambda percorso: 84.976)
    brano = tmp_path / "Choral.mpc"
    brano.write_bytes(b"")
    lettore = _LettoreDelKaraoke(str(brano))
    lettore.durata_vera = None
    finestra.motore._aggiungi_le_tracce(lettore, str(brano), 1)
    assert lettore.durata_vera == 84.976
    lettore.mpv = types.SimpleNamespace(time_pos=10.0, duration=83.592)
    assert motore._Lettore.leggi(lettore) == (10.0, 84.976)
    # Gli altri formati tengono la durata di libmpv.
    altro = _LettoreDelKaraoke(str(tmp_path / "a.mp3"))
    altro.durata_vera = None
    finestra.motore._aggiungi_le_tracce(altro, str(tmp_path / "a.mp3"), 1)
    assert altro.durata_vera is None


def test_l_aggiornamento_nella_finestra(finestra, monkeypatch, suoni_annotati):
    # 1.84.0: la proposta, l'avanzamento e la chiusura senza l'invito alla donazione.
    risposte = [wx.ID_NO, wx.ID_YES]
    aperte = []

    class Finta:
        def __init__(self, genitore, attuale, nuova, novita, attesa=None):
            aperte.append((attuale, nuova, novita, attesa))

        def __enter__(self):
            return self

        def __exit__(self, *_argomenti):
            return False

        def ShowModal(self):
            return risposte.pop(0)

    monkeypatch.setattr(modulo, "FinestraAggiornamento", Finta)
    assert finestra.proponi_l_aggiornamento("1.83.3", "1.84.0", "novita'", 120) is False
    assert suoni_annotati[-1] == "annullamento" and _ultima(finestra) == "Aggiornamento rimandato: te lo ripropongo al prossimo avvio."
    assert finestra.proponi_l_aggiornamento("1.83.3", "1.84.0", "novita'", 120) is True
    assert suoni_annotati[-1] == "aggiornamento" and aperte[0] == ("1.83.3", "1.84.0", "novita'", 120)
    finestra.avanzamento_dell_aggiornamento(30, 100)
    finestra.avanzamento_dell_aggiornamento(60, 100)
    assert _ultima(finestra) == "Aggiornamento: 60%." and not any(r.startswith("Aggiornamento: 30%") for r in finestra._righe)
    inviti = []
    monkeypatch.setattr(finestra, "_invito_alla_donazione", lambda genitore, probabilita=20: inviti.append(probabilita))
    finestra.chiudi_per_aggiornare()
    assert finestra.chiusa and inviti == []


def test_dopo_l_aggiornamento_la_console_lo_dice(app, tmp_path):
    import json

    from finestra import Finestra

    (tmp_path / "MeTeOra - Impostazioni.json").write_text(json.dumps({"versione": "1.0.0"}), encoding="utf-8")
    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        assert any(r.startswith(f"MeTeOra è stato aggiornato dalla 1.0.0 alla {modulo.version.VERSION}: F2") for r in f._righe)
        assert f.impostazioni["versione"] == modulo.version.VERSION
    finally:
        f.Close(force=True)
        f.Destroy()
    g = Finestra(ao="null", cartella_dati=str(tmp_path))
    try:
        assert not any("è stato aggiornato" in r for r in g._righe)
    finally:
        g.Close(force=True)
        g.Destroy()


def test_i_crediti_dicono_licenza_garanzia_e_sorgenti(finestra):
    # 1.85.0: la GPL 3 chiede nell'interfaccia il copyright, la licenza, la garanzia assente e dove leggere la licenza.
    finestra._crediti()
    testo = "\n".join(_senza_ora(r) for r in finestra._righe)
    assert "Copyright (C) 2026 Gabriele Battaglia (IZ4APU)." in testo
    assert "GNU General Public License, versione 3 o, a tua scelta, qualunque versione successiva. È distribuito senza alcuna garanzia." in testo
    assert "nel file LICENSE accanto al programma" in testo and "licenze\\SORGENTI.txt" in testo
    assert "Licenza: GPL 3." not in testo


def test_restano_le_uscite_libere():
    # 1.85.0: ZDSR, Dolphin, System Access e PC-Talker hanno DLL proprietarie, fuori dal pacchetto.
    import sintesi

    assert list(sintesi.USCITE) == ["nvda", "jaws", "sapi5"]
    assert {"nvda", "jaws"} == sintesi.CON_IL_BRAILLE


def test_una_cartella_di_rete_parziale_resta_da_riaprire(finestra, monkeypatch, tmp_path):
    # Revisione della 1.85.5: una cartella con il conto parziale e vuoto resta
    # nella plancia quando si rilegge chi la contiene, per poterla riaprire.
    (tmp_path / "Rete" / "Backup").mkdir(parents=True)
    (tmp_path / "Rete" / "Vuota").mkdir()
    monkeypatch.setattr(modulo, "in_rete", lambda percorso: True)
    finestra.contatore.conti[str(tmp_path / "Rete" / "Backup")] = []
    finestra.contatore.parziali.add(str(tmp_path / "Rete" / "Backup"))
    finestra.contatore.conti[str(tmp_path / "Rete" / "Vuota")] = []
    finestra.albero.Expand(finestra.nodo_pc)
    voce = finestra.albero.AppendItem(finestra.nodo_pc, "Rete", data={"tipo": "cartella", "percorso": str(tmp_path / "Rete"), "caricato": False})
    finestra.albero.SetItemHasChildren(voce, True)
    finestra.albero.Expand(voce)
    assert _etichette(finestra, voce) == ["Backup (conto incompleto: una cartella di rete non risponde)"]


def test_un_ramo_di_rete_che_sbaglia_subito_resta_da_riaprire(finestra, monkeypatch, suoni_annotati, tmp_path):
    # Revisione della 1.85.5: la rete che manca del tutto risponde subito con
    # un errore, come il percorso di rete non trovato (53): il ramo resta da
    # riaprire; l'accesso negato (5) resta un errore della cartella.
    monkeypatch.setattr(modulo, "in_rete", lambda percorso: True)
    errore = [53]

    def leggi_in_rete(cartella, attesa=None, fermo=None):
        raise OSError(None, "Impossibile trovare il percorso di rete", None, errore[0])

    monkeypatch.setattr(modulo, "leggi_in_rete", leggi_in_rete)
    finestra.albero.Expand(finestra.nodo_pc)
    voce = finestra.albero.AppendItem(finestra.nodo_pc, "Box", data={"tipo": "cartella", "percorso": str(tmp_path / "Box"), "caricato": False})
    finestra.albero.SetItemHasChildren(voce, True)
    finestra.albero.Expand(voce)
    assert suoni_annotati[-1] == "errore" and _ultima(finestra).endswith("Riaprendo il ramo si riprova.")
    assert finestra._dati(voce)["caricato"] is False and finestra.albero.ItemHasChildren(voce)
    assert str(tmp_path / "Box").lower() not in finestra.contatore.cartelle_mute
    errore[0] = 5
    altra = finestra.albero.AppendItem(finestra.nodo_pc, "Chiusa", data={"tipo": "cartella", "percorso": str(tmp_path / "Chiusa"), "caricato": False})
    finestra.albero.SetItemHasChildren(altra, True)
    finestra.albero.Expand(altra)
    assert _ultima(finestra).startswith(f"Non riesco a leggere {tmp_path / 'Chiusa'}") and not finestra.albero.ItemHasChildren(altra)


def test_aggiorna_su_questa_rete_riprova_le_cartelle_di_rete(finestra, monkeypatch):
    # Revisione della 1.85.5: Aggiorna su Questa rete dimentica i conti di
    # rete e le mute, come promette il manuale; i conti dei dischi restano.
    import contatore as modulo_contatore

    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith("\\\\"))
    conta = finestra.contatore
    rete, disco = "\\\\box\\dati\\Video", "C:\\Musica"
    conta.conti.update({rete: [], disco: ["C:\\Musica\\a.mp3"]})
    conta.parziali.add(rete)
    conta.non_risponde("\\\\box\\dati\\Backup")
    conta.mute.add("\\\\box\\dati")
    finestra._aggiorna_ramo(finestra.nodo_rete)
    assert rete not in conta.conti and not conta.parziali and not conta.mute and not conta.cartelle_mute
    assert conta.conti[disco] == ["C:\\Musica\\a.mp3"]


def test_il_ramo_di_rete_dice_l_errore_di_windows(finestra, monkeypatch, suoni_annotati, tmp_path):
    # Revisione della 1.85.5: un errore di rete lascia il ramo da riaprire e ne
    # dice il testo; un errore che non e' della rete, come 1117, e' della
    # cartella.
    monkeypatch.setattr(modulo, "in_rete", lambda percorso: True)
    errore = [OSError(None, "Impossibile trovare il percorso di rete", None, 53)]

    def leggi_in_rete(cartella, attesa=None, fermo=None):
        raise errore[0]

    monkeypatch.setattr(modulo, "leggi_in_rete", leggi_in_rete)
    finestra.albero.Expand(finestra.nodo_pc)
    voce = finestra.albero.AppendItem(finestra.nodo_pc, "Box", data={"tipo": "cartella", "percorso": str(tmp_path / "Box"), "caricato": False})
    finestra.albero.SetItemHasChildren(voce, True)
    finestra.albero.Expand(voce)
    assert _ultima(finestra) == f"{tmp_path / 'Box'} non risponde: Impossibile trovare il percorso di rete. Riaprendo il ramo si riprova."
    errore[0] = OSError(None, "Errore di I/O sul dispositivo", None, 1117)
    altra = finestra.albero.AppendItem(finestra.nodo_pc, "Guasta", data={"tipo": "cartella", "percorso": str(tmp_path / "Guasta"), "caricato": False})
    finestra.albero.SetItemHasChildren(altra, True)
    finestra.albero.Expand(altra)
    assert _ultima(finestra) == f"Non riesco a leggere {tmp_path / 'Guasta'}: Errore di I/O sul dispositivo" and not finestra.albero.ItemHasChildren(altra)


def test_aggiorna_su_un_ramo_di_rete_rifa_i_conti_delle_sorelle(finestra, monkeypatch, tmp_path):
    # Revisione della 1.85.5: Aggiorna su un ramo di una radice lasciata
    # perdere la fa tornare viva, e i conti parziali delle altre sue cartelle
    # si rifanno.
    (tmp_path / "Rete" / "Video").mkdir(parents=True)
    monkeypatch.setattr(modulo, "in_rete", lambda percorso: True)
    richiesti = []
    vero_chiedi = finestra.contatore.chiedi
    monkeypatch.setattr(finestra.contatore, "chiedi", lambda cartelle: (richiesti.extend(cartelle), vero_chiedi([]))[1])
    radice = os.path.splitdrive(str(tmp_path))[0].lower()
    sorella = str(tmp_path / "Rete" / "Musica")
    finestra.contatore.mute.add(radice)
    finestra.contatore.conti[sorella] = []
    finestra.contatore.parziali.add(sorella)
    finestra.albero.Expand(finestra.nodo_pc)
    voce = finestra.albero.AppendItem(finestra.nodo_pc, "Video", data={"tipo": "cartella", "percorso": str(tmp_path / "Rete" / "Video"), "caricato": False})
    finestra.albero.SetItemHasChildren(voce, True)
    finestra._aggiorna_ramo(voce)
    assert sorella in richiesti and radice not in finestra.contatore.mute and sorella not in finestra.contatore.parziali


def test_il_cestino_rifa_i_conti_che_dimentica_restituisce(finestra, suoni_annotati, tmp_path, monkeypatch):
    # Revisione della 1.85.5: le cartelle che dimentica torna da ricontare,
    # quando la radice di rete torna viva, si chiedono al contatore.
    import questo_pc

    monkeypatch.setattr(questo_pc, "nel_cestino", lambda p: True)
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo: True)
    monkeypatch.setattr(finestra.contatore, "dimentica", lambda percorso, anche_sopra=True: ["\\\\box\\dati\\Musica"])
    richiesti = []
    monkeypatch.setattr(finestra.contatore, "chiedi", richiesti.extend)
    (tmp_path / "Vuota").mkdir()
    finestra.albero.Expand(finestra.nodo_pc)
    vuota = finestra.albero.AppendItem(finestra.nodo_pc, "Vuota", data={"tipo": "cartella", "percorso": str(tmp_path / "Vuota"), "caricato": False})
    finestra._seleziona(vuota)
    finestra._al_cestino(vuota)
    assert suoni_annotati[-1] == "cestino" and "\\\\box\\dati\\Musica" in richiesti


def test_aggiorna_su_questa_rete_riconta_le_unita_di_rete_di_questo_pc(finestra, monkeypatch):
    # Revisione della 1.85.5: le cartelle di rete aperte sotto Questo PC, come
    # un'unita' di rete con la lettera, si ricontano dopo Aggiorna su Questa rete.
    import contatore as modulo_contatore

    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith("Z:"))
    richiesti = []
    monkeypatch.setattr(finestra.contatore, "chiedi", richiesti.extend)
    finestra.albero.Expand(finestra.nodo_pc)
    voce = finestra.albero.AppendItem(finestra.nodo_pc, "Video", data={"tipo": "cartella", "percorso": "Z:\\Video", "caricato": True})
    finestra.albero.AppendItem(voce, "film.mkv", data={"tipo": "attesa"})
    finestra.contatore.conti.update({"Z:\\Video": ["Z:\\Video\\film.mkv"], "Z:\\Altro": []})
    finestra._aggiorna_ramo(finestra.nodo_rete)
    assert richiesti == ["Z:\\Video"] and "Z:\\Video" not in finestra.contatore.conti


def test_f11_in_rete_aspetta_come_la_plancia(finestra, monkeypatch, tmp_path):
    # Revisione della 1.85.5: F11 su una cartella di rete aspetta otto secondi,
    # non tre; anche il censimento dei brani.
    import dettagli

    attese = []
    monkeypatch.setattr(modulo.questa_rete, "raggiungibile", lambda percorso, attesa=3.0: attese.append(attesa) or False)
    monkeypatch.setattr(modulo, "in_rete", lambda percorso: True)
    righe = finestra._dettagli_della_cartella(str(tmp_path), False, lambda: False)
    assert righe[-1].endswith("non risponde: la rete o il disco sono spenti, o lontani.")
    monkeypatch.setattr(dettagli, "in_rete", lambda percorso: True)
    assert dettagli.censisci_brani([str(tmp_path / "a.mp3")])["lontani"] == 1
    assert attese == [modulo.questa_rete.ATTESA_IN_SOTTOFONDO] * 2 and modulo.questa_rete.ATTESA_IN_SOTTOFONDO == 8.0


def test_maiuscolo_f12_spegne_e_riaccende_i_tasti_rapidi(finestra, suoni_annotati):
    # 1.86.0 (Gabriele): spenti, lettere, cifre e segni vanno ai controlli; i
    # tasti funzione restano; a ogni avvio sono accesi.
    assert finestra._tasti_rapidi is True
    _tasto(finestra, codice=wx.WXK_F12, maiuscolo=True)
    assert finestra._tasti_rapidi is False and suoni_annotati[-1] == "tasti_spenti"
    assert _ultima(finestra) == "Tasti rapidi spenti: le lettere cercano nella plancia per iniziale. Maiuscolo con F12 li riaccende."
    righe, suonati = len(finestra._righe), len(suoni_annotati)
    finestra._fuoco_nella_plancia = lambda: True
    for carattere, maiuscolo in (("x", False), ("b", True), ("1", False), ("\\", False), ("[", False)):
        evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
        evento.SetUnicodeKey(ord(carattere.upper()))
        evento.SetKeyCode(ord(carattere.upper()))
        evento.SetShiftDown(maiuscolo)
        assert finestra._esegui_il_tasto(evento) is False and evento.GetSkipped(), carattere
    assert len(finestra._righe) == righe and len(suoni_annotati) == suonati
    # Fuori dalla plancia il carattere non arriva al controllo, che suonerebbe
    # l'avviso di Windows: lo dice la console, sempre sulla stessa riga.
    finestra._fuoco_nella_plancia = lambda: False
    for carattere in ("x", "y"):
        evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
        evento.SetUnicodeKey(ord(carattere.upper()))
        evento.SetKeyCode(ord(carattere.upper()))
        assert finestra._esegui_il_tasto(evento) is True and not evento.GetSkipped()
    assert len(finestra._righe) == righe + 1 and suoni_annotati[-1] == "non_disponibile"
    assert _ultima(finestra) == "Tasti rapidi spenti: le lettere cercano solo nella plancia, F5. Maiuscolo con F12 li riaccende."
    # Nella plancia il carattere arriva all'albero, per la ricerca per iniziale.
    evento = wx.KeyEvent(wx.wxEVT_CHAR)
    evento.SetUnicodeKey(ord("p"))
    finestra._carattere_nell_albero(evento)
    assert evento.GetSkipped()
    # Il cruscotto lo dice per primo.
    assert finestra.righe_del_cruscotto()[0] == "Tasti rapidi spenti: lettere, cifre e segni vanno alla plancia, che cerca per iniziale; Maiuscolo con F12 li riaccende."
    # I tasti funzione restano: F7 porta al cruscotto.
    _tasto(finestra, codice=wx.WXK_F7)
    assert suoni_annotati[-1] == "cruscotto"
    _tasto(finestra, codice=wx.WXK_F12, maiuscolo=True)
    assert finestra._tasti_rapidi is True and suoni_annotati[-1] == "tasti_accesi" and _ultima(finestra) == "Tasti rapidi accesi."
    assert not finestra.righe_del_cruscotto()[0].startswith("Tasti rapidi spenti")
    evento = wx.KeyEvent(wx.wxEVT_CHAR)
    evento.SetUnicodeKey(ord("p"))
    finestra._carattere_nell_albero(evento)
    assert not evento.GetSkipped()
    _tasto(finestra, "z", maiuscolo=True)
    assert _ultima(finestra) == "Maiuscolo+Z non ha un comando."


def test_con_i_tasti_spenti_l_albero_cerca_per_iniziale(finestra):
    # 1.86.0: la prova vera della ricerca per iniziale dell'albero di Windows,
    # con un carattere mandato al controllo come lo manda la tastiera.
    import ctypes

    wm_char = 0x0102
    radice = finestra.albero.AppendItem(finestra.albero.GetRootItem(), "Prova delle iniziali", data={"tipo": "comando", "comando": "impostazioni"})
    voci = {nome: finestra.albero.AppendItem(radice, nome, data={"tipo": "comando", "comando": "impostazioni"}) for nome in ("Alfa", "Beta", "Gamma")}
    finestra.albero.Expand(radice)
    finestra._seleziona(voci["Alfa"])

    def scrivi(lettera):
        ctypes.windll.user32.SendMessageW(finestra.albero.GetHandle(), wm_char, ord(lettera), 0)
        wx.Yield()

    scrivi("g")
    assert finestra.albero.GetItemText(finestra.albero.GetFocusedItem()) == "Alfa"
    finestra._tasti_rapidi = False
    scrivi("g")
    assert finestra.albero.GetItemText(finestra.albero.GetFocusedItem()) == "Gamma"
    # La selezione segue il fuoco: i comandi agiscono su Gamma, non su Alfa.
    assert finestra.albero.GetItemText(finestra._voce_di_lavoro()) == "Gamma"
    assert [finestra.albero.GetItemText(v) for v in finestra._voci_selezionate()] == ["Gamma"]


def test_i_file_aperti_da_windows(finestra, monkeypatch, suoni_annotati, tmp_path):
    # 1.91.0: dalla riga di comando, da un'altra copia o trascinati, i file
    # arrivati insieme suonano come una lista sola, che non entra fra le playlist.
    suonati = _finto_motore(finestra, monkeypatch)
    for nome in ("b.mp3", "a.flac", "testo.txt"):
        (tmp_path / nome).write_bytes(b"")
    (tmp_path / "album").mkdir()
    (tmp_path / "album" / "c.ogg").write_bytes(b"")
    finestra.apri_dall_esterno([str(tmp_path / "b.mp3"), str(tmp_path / "testo.txt")])
    finestra.apri_dall_esterno([str(tmp_path / "a.flac"), str(tmp_path / "album"), str(tmp_path / "b.mp3")])
    assert finestra._apertura_esterna_pianificata
    finestra._apri_i_percorsi()
    assert suonati == [("b.mp3", None)]
    pl = finestra.coda.playlist
    assert pl.nome == "file aperti" and [os.path.basename(b.percorso) for b in pl.brani] == ["b.mp3", "a.flac", "c.ogg"]
    assert pl not in finestra.archivio.playlist
    assert any(_senza_ora(r) == "MeTeOra non suona testo.txt: non è un formato che conosce, o non c'è." for r in finestra._righe)
    # Una cartella sola suona come X su di lei.
    cartelle = []
    monkeypatch.setattr(finestra, "_riproduci_cartella", cartelle.append)
    finestra.apri_dall_esterno([str(tmp_path / "album")])
    finestra._apri_i_percorsi()
    assert cartelle == [str(tmp_path / "album")]
    # Niente da suonare: lo si dice.
    finestra.apri_dall_esterno([str(tmp_path / "testo.txt")])
    finestra._apri_i_percorsi()
    assert suoni_annotati[-1] == "niente_da_suonare" and _ultima(finestra) == "Niente da suonare in quello che arriva da Windows."


def test_il_trascinamento_sulla_finestra(finestra, monkeypatch):
    arrivati = []
    monkeypatch.setattr(finestra, "apri_dall_esterno", arrivati.append)
    for controllo in (finestra.albero, finestra.console, finestra.cruscotto):
        bersaglio = controllo.GetDropTarget()
        assert isinstance(bersaglio, modulo._Trascinamento)
        assert bersaglio.OnDropFiles(0, 0, ["C:\\m\\a.mp3"]) is True
    wx.Yield()
    assert arrivati == [["C:\\m\\a.mp3"]] * 3


def test_le_associazioni_dalle_impostazioni(finestra, monkeypatch, suoni_annotati):
    # 1.91.0: solo dal programma compilato; registra, poi la pagina delle app
    # predefinite; oppure toglie.
    import sys as modulo_sys

    finestra._associa_i_formati(None)
    assert suoni_annotati[-1] == "non_disponibile" and "solo dal programma compilato" in _ultima(finestra)
    monkeypatch.setattr(modulo_sys, "frozen", True, raising=False)
    fatti, scelte = [], [0, 1]

    class Scelta:
        def __init__(self, _genitore, titolo, righe, selezione):
            fatti.append(("scelta", titolo, len(righe), selezione))

        def __enter__(self):
            return self

        def __exit__(self, *_argomenti):
            return False

        def ShowModal(self):
            return wx.ID_OK

        def GetSelection(self):
            return scelte.pop(0)

    monkeypatch.setattr(modulo, "FinestraScelta", Scelta)
    monkeypatch.setattr(modulo.associazioni, "registra", lambda eseguibile: fatti.append(("registra", eseguibile)) or 150)
    monkeypatch.setattr(modulo.associazioni, "togli", lambda: fatti.append(("togli",)))
    monkeypatch.setattr(modulo.associazioni, "apri_le_app_predefinite", lambda: fatti.append(("pagina",)))
    finestra._associa_i_formati(None)
    assert fatti == [("scelta", "Associazioni dei formati", 2, 0), ("registra", modulo_sys.executable), ("pagina",)]
    assert _ultima(finestra).startswith("MeTeOra ora compare in Apri con per 150 formati.")
    finestra._associa_i_formati(None)
    assert fatti[-1] == ("togli",) and _ultima(finestra) == "MeTeOra non è più nelle associazioni dei formati."


def test_i_file_lunghi_riprendono_dal_punto_lasciato(finestra, monkeypatch, tmp_path):
    # 1.92.0: un file piu' lungo del limite riprende dal punto lasciato; X da
    # capo, i file corti e la fine del brano no.
    chiamate = []
    stato = {"in_corso": None, "durata": 3600.0, "posizione": 0.0}
    monkeypatch.setattr(finestra.motore, "suona", lambda percorso, sottobrano=None, inizio=None, **_altro: chiamate.append((percorso, inizio))
        or stato.update(in_corso=percorso))
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda _self: stato["in_corso"]))
    monkeypatch.setattr(type(finestra.motore), "durata", property(lambda _self: stato["durata"]))
    monkeypatch.setattr(type(finestra.motore), "posizione", property(lambda _self: stato["posizione"]))
    finestra.motore.sottobrani = None
    libro = r"C:\m\libro.m4b"
    pl = modulo.Playlist("prova", [modulo.Brano(libro), modulo.Brano(r"C:\m\canzone.mp3")], cartella="")
    finestra.posizioni.ricorda(libro, 1500, 3600)
    finestra._suona(pl, pl.brani[0])
    assert chiamate[-1] == (libro, 1500.0)
    assert any(_senza_ora(r) == "Riprendo da 25:00, dove l'avevi lasciato: X lo fa ripartire da capo." for r in finestra._righe)
    # X da capo riparte dall'inizio.
    finestra._suona(pl, pl.brani[0], "da_capo")
    assert chiamate[-1] == (libro, None)
    # Mentre suona, il giro ricorda il punto; lo stop anche.
    stato["posizione"] = 2000.0
    finestra._ricorda_la_posizione()
    assert finestra.posizioni.dove(libro) == 2000.0
    stato["posizione"] = 2100.0
    monkeypatch.setattr(finestra.motore, "stop", lambda sfumando=False: None)
    finestra._comando_stop()
    assert finestra.posizioni.dove(libro) == 2100.0
    # Un file corto non ha un punto.
    stato["durata"] = 200.0
    stato["in_corso"] = r"C:\m\canzone.mp3"
    stato["posizione"] = 100.0
    finestra._ricorda_la_posizione()
    assert finestra.posizioni.dove(r"C:\m\canzone.mp3") is None
    # Con il limite a 0 nessun file riprende.
    finestra.impostazioni["ripresa_oltre"] = 0
    finestra._suona(pl, pl.brani[0])
    assert chiamate[-1] == (libro, None)
    finestra.impostazioni["ripresa_oltre"] = 10
    # Arrivato alla fine, il file dimentica il punto.
    finestra.coda.imposta(pl, pl.brani[0])
    monkeypatch.setattr(finestra, "_seguente_automatico", lambda: None)
    monkeypatch.setattr(finestra, "_fine_della_lista", lambda: None)
    finestra._brano_finito()
    assert finestra.posizioni.dove(libro) is None


def test_le_posizioni_si_salvano_ogni_tanto(finestra, tmp_path):
    finestra.posizioni.ricorda(r"C:\m\film.mkv", 600, 7200)
    for _ in range(modulo.GIRI_PER_SALVARE):
        finestra._giro_delle_posizioni(None)
    assert (tmp_path / modulo.FILE_POSIZIONI).exists() and not finestra.posizioni.modificate


def test_virgola_e_punto_vanno_ai_capitoli(finestra, monkeypatch, suoni_annotati):
    # 1.93.0: virgola e punto, con i capitoli di libmpv; oltre i primi secondi
    # la virgola torna all'inizio del capitolo.
    stato = {"posizione": 700.0}
    salti = []
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda _self: r"C:\m\libro.m4b"))
    monkeypatch.setattr(type(finestra.motore), "posizione", property(lambda _self: stato["posizione"]))
    monkeypatch.setattr(finestra.motore, "capitoli", lambda: [(0.0, "Uno"), (600.0, "Due"), (1200.0, "")])
    monkeypatch.setattr(finestra.motore, "vai_a", lambda secondi: salti.append(secondi) or stato.update(posizione=secondi))
    _tasto(finestra, ".")
    assert salti == [1200.0] and suoni_annotati[-1] == "capitolo_successivo" and _ultima(finestra) == "Capitolo 3 di 3, 20:00."
    _tasto(finestra, ".")
    assert _ultima(finestra) == "È l'ultimo capitolo." and len(salti) == 1
    stato["posizione"] = 1210.0
    _tasto(finestra, ",")
    assert salti[-1] == 1200.0 and suoni_annotati[-1] == "capitolo_precedente"
    _tasto(finestra, ",")
    assert salti[-1] == 600.0 and _ultima(finestra) == "Capitolo 2 di 3: Due, 10:00."
    _tasto(finestra, ",")
    _tasto(finestra, ",")
    assert salti[-1] == 0.0 and _ultima(finestra) == "È il primo capitolo."
    # Senza capitoli, lo si dice; e con i capitoli dei tag nello schedario si va lo stesso.
    monkeypatch.setattr(finestra.motore, "capitoli", lambda: [])
    _tasto(finestra, ".")
    assert _ultima(finestra) == "libro.m4b non ha capitoli."
    finestra.schedario.schede[r"C:\m\libro.m4b"] = {"durata": 1800.0, "capitoli": [[0, "A"], [900, "B"]]}
    _tasto(finestra, ".")
    assert salti[-1] == 900.0


def test_i_capitoli_nella_plancia(finestra, monkeypatch):
    # 1.93.0: un file con i capitoli nella scheda diventa un ramo; X su un
    # capitolo suona il file da li'.
    chiamate = []
    monkeypatch.setattr(finestra.motore, "suona", lambda percorso, sottobrano=None, inizio=None, **_altro: chiamate.append((percorso, inizio)))
    libro = r"C:\m\libro.m4b"
    finestra.schedario.schede[libro] = {"dim": 1, "mod": 0, "durata": 1800.0, "tag": {}, "capitoli": [[0, "Inizio"], [900, "Meta'"]]}
    finestra._aggiungi(None, [libro, r"C:\m\canzone.mp3"])
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    file_libro, file_canzone = list(finestra._figli(nodo))
    assert finestra.albero.ItemHasChildren(file_libro) and not finestra.albero.ItemHasChildren(file_canzone)
    finestra.albero.Expand(file_libro)
    assert _etichette(finestra, file_libro) == ["Capitolo 1 di 2: Inizio, 0:00", "Capitolo 2 di 2: Meta', 15:00"]
    secondo = list(finestra._figli(file_libro))[1]
    finestra._seleziona(secondo)
    _tasto(finestra, "x")
    assert chiamate[-1] == (libro, 900.0)
    assert any(_senza_ora(r) == "Dal capitolo 2 di 2: Meta', 15:00." for r in finestra._righe)
