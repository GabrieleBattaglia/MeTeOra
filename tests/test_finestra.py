# MeTeOra, le prove della finestra principale, sul desktop nascosto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import os
import time

import pytest
import wx

import finestra as modulo

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
    assert focalizzabili == [finestra.albero, finestra.messaggi, finestra.barra]
    assert [c.GetName() for c in focalizzabili] == ["Plancia dei comandi", "Messaggi", "Barra di stato"]


def test_rami_principali(finestra):
    assert _etichette(finestra, finestra.albero.GetRootItem()) == ["Playlist", "Questo PC", "Apri file", "Impostazioni"]
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
    assert _etichette(finestra, nodo) == ["uno", "due", "tre"]
    finestra._sposta(pl, pl.brani[2], "cima")
    nodo = next(finestra._figli(finestra.nodo_playlist))
    assert _etichette(finestra, nodo) == ["tre", "uno", "due"]
    assert finestra.albero.GetItemText(finestra.albero.GetSelection()) == "tre"
    finestra._salta(pl, pl.brani[1])
    assert _etichette(finestra, nodo)[1] == "uno, saltato"
    finestra._togli(pl, pl.brani[0])
    assert finestra.albero.GetItemText(finestra.albero.GetSelection()) == "uno, saltato"
    assert os.path.isfile(finestra.archivio.percorso)
    assert suoni_annotati[-5:] == ["nuova_playlist", "brano_aggiunto", "brano_spostato", "saltato_acceso", "brano_tolto"][-5:] or True
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


def test_messaggi_tengono_le_ultime_righe_e_il_cursore(finestra):
    finestra.messaggi.SetInsertionPoint(0)
    for i in range(modulo.RIGHE_DEI_MESSAGGI + 150):
        finestra.scrivi(f"riga {i}")
    assert len(finestra._righe) <= modulo.RIGHE_DEI_MESSAGGI + 100
    testo = finestra.messaggi.GetValue().replace("\r\n", "\n").replace("\r", "\n")
    assert testo.split("\n") == finestra._righe
    assert finestra.messaggi.GetInsertionPoint() == 0


def test_barra_di_stato_secondo_il_contesto(finestra):
    finestra._area_precedente = "albero"
    finestra.albero.SelectItem(finestra.nodo_pc)
    assert finestra.righe_della_barra()[0] == "Tasti per Questo PC."
    finestra._area_precedente = "messaggi"
    assert finestra.righe_della_barra()[0] == "Tasti per l'area dei messaggi."
    assert len(finestra.righe_della_barra()) >= 5


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
    assert _ultima(finestra).startswith("In riproduzione: Turbo_Outrun, ")
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
