# MeTeOra, le prove della finestra principale, sul desktop nascosto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import os
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


def _ultima(f):
    return f._righe[-1]


def test_aree_nell_ordine_di_tabulazione(finestra):
    focalizzabili = [c for c in finestra.albero.GetParent().GetChildren() if c.AcceptsFocus()]
    assert focalizzabili == [finestra.albero, finestra.console, finestra.cruscotto]
    assert [c.GetName() for c in focalizzabili] == ["Plancia dei comandi", "Console", "Cruscotto"]


def test_rami_principali(finestra):
    assert _etichette(finestra, finestra.albero.GetRootItem()) == ["Preferiti, 0 brani", "Playlist", "Questo PC", "Apri file", "Impostazioni"]
    assert _etichette(finestra, finestra.nodo_playlist) == ["Nuova playlist"]


def test_questo_pc_si_carica_all_espansione(finestra):
    assert not list(finestra._figli(finestra.nodo_pc))
    finestra.albero.Expand(finestra.nodo_pc)
    unita = _etichette(finestra, finestra.nodo_pc)
    assert unita and all(":\\" in u for u in unita)


def test_nuova_playlist_aggiungi_sposta_togli(finestra, suoni_annotati):
    finestra._comando_nuova_playlist()
    pl = finestra.archivio.playlist[0]
    assert finestra.albero.GetItemText(finestra.albero.GetSelection()) == "Playlist, 0 brani"
    finestra._aggiungi(pl, [r"C:\m\uno.mp3", r"C:\m\due.mp3", r"C:\m\tre.mp3"])
    assert _ultima(finestra) == "Aggiunti alla playlist Playlist: 3 brani, ora 3 brani."
    nodo = next(finestra._figli(finestra.nodo_playlist))
    finestra.albero.Expand(nodo)
    assert _etichette(finestra, nodo) == ["uno.mp3", "due.mp3", "tre.mp3"]
    finestra._sposta(pl, pl.brani[2], "cima")
    nodo = next(finestra._figli(finestra.nodo_playlist))
    assert _etichette(finestra, nodo) == ["tre.mp3", "uno.mp3", "due.mp3"]
    assert finestra.albero.GetItemText(finestra.albero.GetSelection()) == "tre.mp3"
    finestra._salta(pl, pl.brani[1])
    assert _etichette(finestra, nodo)[1] == "uno.mp3, saltato"
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
    finestra.motore.volume = 98
    _tasto(finestra, "+")
    assert _ultima(finestra) == "Volume 100."
    _tasto(finestra, "+")
    assert _ultima(finestra) == "Volume già al massimo, 100."
    _tasto(finestra, "m")
    assert _ultima(finestra) == "Muto."
    _tasto(finestra, "m")
    assert _ultima(finestra).startswith("Audio di nuovo acceso")
    assert finestra.impostazioni["volume"] == 100


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
    finestra._informazioni()
    assert "di 7:55" in _ultima(finestra)
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
    assert _premi(finestra, "b", maiuscolo=True) == "Sottobrano 4 di 12, 3:00."
    assert suoni_annotati[-1] == "sottobrano_successivo"
    _premi(finestra, "z", maiuscolo=True)
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
        finestra.albero.SelectItem(_voce(finestra, nodo, lambda d: d.get("brano") is pl.brani[n - 1]))

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
    finestra.albero.SelectItem(list(finestra._figli(nodo))[1])
    _tasto(finestra, codice=wx.WXK_F4)
    assert _ultima(finestra) == "2.mp3 è nei Preferiti, che ora hanno 1 brano."
    assert finestra.albero.GetItemText(finestra.nodo_preferiti) == "Preferiti, 1 brano"
    _tasto(finestra, codice=wx.WXK_F4)
    assert _ultima(finestra) == "2.mp3 è già nei Preferiti."
    preferito = finestra.archivio.preferiti.brani[0]
    assert preferito is not pl.brani[1] and preferito.percorso == pl.brani[1].percorso
    finestra._cancella(finestra.nodo_preferiti)
    assert _ultima(finestra).startswith("I Preferiti non si eliminano")
    finestra.albero.Expand(finestra.nodo_preferiti)
    finestra._cancella(next(finestra._figli(finestra.nodo_preferiti)))
    assert not finestra.archivio.preferiti.brani
    assert finestra.albero.GetItemText(finestra.nodo_preferiti) == "Preferiti, 0 brani"
    finestra.archivio.preferiti.brani.append(preferito)
    finestra._salva_archivio()
    from playlist import Archivio

    di_nuovo = Archivio(finestra.archivio.percorso)
    di_nuovo.carica()
    assert [b.percorso for b in di_nuovo.preferiti.brani] == [preferito.percorso]
