# MeTeOra, le prove della barra dei comandi per il mouse: quando compare, quando sparisce, i clic, il fuoco.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.87.0; dopo la revisione, i clic veri e il mouse portato da NVDA.

"""Il mouse e il tempo sono finti; la finestra e la barra sono vere, sul
desktop nascosto, e i clic veri arrivano come messaggi di Windows."""

import ctypes
from ctypes import wintypes

import wx

import barra

WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0200, 0x0201, 0x0202


class _Mondo:
    """Il mouse, l'orologio, la finestra attiva e i menu, decisi dalla prova."""

    def __init__(self, finestra):
        self.finestra = finestra
        area = finestra.barra._area_della_finestra()
        self.dentro = wx.Point(area.x + area.width // 2, area.y + area.height // 3)
        self.fuori = wx.Point(area.x + area.width + 50, area.y + area.height + 50)
        self.mouse = self.dentro
        self.adesso = 100.0
        self.attiva = True
        self.occupata = False
        b = finestra.barra
        b._posizione_del_mouse = lambda: self.mouse
        b._orologio = lambda: self.adesso
        b._finestra_attiva = lambda: self.attiva
        b._occupata = lambda: self.occupata

    def muovi(self, passi=2):
        """Il mouse si muove dentro la finestra per qualche giro del timer;
        senza una posizione di prima, il primo giro fa da riferimento."""
        if self.finestra.barra._ultima_posizione is None:
            self.finestra.barra.guarda()
        for _ in range(passi):
            self.mouse = wx.Point(self.mouse.x + 3, self.mouse.y)
            self.finestra.barra.guarda()


def _user32():
    user32 = ctypes.WinDLL("user32")
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.GetFocus.restype = wintypes.HWND
    user32.GetActiveWindow.restype = wintypes.HWND
    return user32


def _manda(barra_, messaggio, punto):
    _user32().SendMessageW(barra_.GetHandle(), messaggio, 1 if messaggio == WM_LBUTTONDOWN else 0, (punto.y << 16) | (punto.x & 0xFFFF))


def test_la_barra_non_prende_mai_il_fuoco(finestra):
    b = finestra.barra
    assert isinstance(b, barra.BarraDeiComandi) and not b.IsShown() and b.GetName() == "Barra dei comandi per il mouse"
    assert barra.stile_esteso(b.GetHandle()) & 0x08000000
    _Mondo(finestra).muovi()
    assert b.IsShown()
    # Le domande che wx fa davvero, dal C++: l'override in Python vale.
    assert not b.CanAcceptFocus() and not b.IsFocusable()
    # Per la navigazione con Tab di wx e' una finestra a se', che salta.
    assert b.IsTopLevel()
    focalizzabili = [c for c in finestra.albero.GetParent().GetChildren() if c.AcceptsFocus()]
    assert focalizzabili == [finestra.albero, finestra.console, finestra.cruscotto]
    assert b.comandi() == ["precedente", "indietro", "play", "pausa", "stop", "avanti", "successivo", "volume_giu", "muto", "volume_su",
        "velocita_giu", "velocita_normale", "velocita_su", "tono_giu", "tono_normale", "tono_su"]
    for comando in b.comandi():
        assert callable(getattr(finestra, f"_comando_{comando}")), comando
    # Nel sorgente i simboli sono scritti in chiaro, non come caratteri invisibili.
    with open(barra.__file__, encoding="utf-8") as f:
        assert not any(0xE000 <= ord(c) <= 0xF8FF for c in f.read())


def test_compare_col_mouse_che_si_muove_e_sparisce(finestra):
    mondo = _Mondo(finestra)
    b = finestra.barra
    b.guarda()
    b.guarda()
    assert not b.IsShown()
    # Un movimento di un giro solo non basta: e' il salto del mouse portato da NVDA.
    mondo.muovi(1)
    b.guarda()
    assert not b.IsShown()
    mondo.muovi(2)
    assert b.IsShown()
    assert b.GetPosition() == b._dove_compare().GetPosition()
    area = b._area_della_finestra()
    assert b.GetScreenRect().bottom <= area.bottom
    # Fermo per piu' di NASCONDI_DOPO secondi: sparisce.
    mondo.adesso += barra.NASCONDI_DOPO + 0.1
    b.guarda()
    assert not b.IsShown()
    # Torna con il mouse che si muove, e sparisce quando il mouse esce.
    mondo.muovi()
    assert b.IsShown()
    mondo.mouse = mondo.fuori
    b.guarda()
    assert not b.IsShown()
    # Il puntatore arrivato sulla barra muovendosi la tiene, anche oltre il tempo.
    mondo.mouse = mondo.dentro
    mondo.muovi()
    rettangolo = b.GetScreenRect()
    mondo.mouse = wx.Point(rettangolo.x + 3, rettangolo.y + 3)
    b.guarda()
    b._passi_sulla_barra = 2
    mondo.adesso += barra.NASCONDI_DOPO * 3
    b.guarda()
    assert b.IsShown()
    # Con un menu aperto, o la finestra che si sposta, sparisce.
    mondo.occupata = True
    b.guarda()
    assert not b.IsShown()
    mondo.occupata = False
    # Con MeTeOra non attivo sparisce, e non compare.
    mondo.attiva = False
    mondo.muovi()
    assert not b.IsShown()


def test_il_mouse_portato_da_nvda_non_la_fa_comparire_sotto_di_se(finestra):
    # Revisione della 1.87.0: NVDA porta il mouse al centro del cruscotto, dove
    # comparirebbe la barra: anche muovendosi li', la barra non compare sotto
    # il puntatore, e il clic che segue va al cruscotto, non a Muto.
    mondo = _Mondo(finestra)
    b = finestra.barra
    dove = b._dove_compare()
    mondo.mouse = wx.Point(dove.x + dove.width // 2, dove.y + dove.height // 2)
    b.guarda()
    for _ in range(3):
        mondo.mouse = wx.Point(mondo.mouse.x + 1, mondo.mouse.y)
        b.guarda()
    assert not b.IsShown()


def test_al_ritorno_della_finestra_il_mouse_fermo_non_la_mostra(finestra):
    # Revisione della 1.87.0: dopo Alt con Tab, o un dialogo, la posizione
    # vecchia del mouse non conta come movimento.
    mondo = _Mondo(finestra)
    b = finestra.barra
    b.guarda()
    mondo.attiva = False
    b.guarda()
    mondo.mouse = wx.Point(mondo.dentro.x + 40, mondo.dentro.y + 10)
    b.guarda()
    mondo.attiva = True
    for _ in range(3):
        b.guarda()
    assert not b.IsShown()


def test_la_barra_segue_la_finestra(finestra):
    mondo = _Mondo(finestra)
    b = finestra.barra
    mondo.muovi()
    assert b.IsShown()
    finestra.SetClientSize(finestra.GetClientSize() + wx.Size(80, 60))
    prima = b.GetPosition()
    mondo.muovi(1)
    assert b.GetPosition() == b._dove_compare().GetPosition() != prima


def test_il_clic_vero_fa_il_comando_senza_spostare_il_fuoco(finestra, monkeypatch):
    # Revisione della 1.87.0: la finestra mostrata e attiva sul desktop
    # nascosto, il fuoco nella plancia, e il clic come messaggio di Windows.
    finestra.Show()
    finestra.albero.SetFocus()
    wx.Yield()
    user32 = _user32()
    fuoco, attiva = user32.GetFocus(), user32.GetActiveWindow()
    assert fuoco == finestra.albero.GetHandle()
    mondo = _Mondo(finestra)
    b = finestra.barra
    fatti = []
    monkeypatch.setattr(finestra, "_comando_pausa", lambda: fatti.append("pausa"))
    mondo.muovi()
    assert b.IsShown()
    pausa = b._celle[b.comandi().index("pausa")][0]
    # Arrivato muovendosi: il clic vale.
    _manda(b, WM_MOUSEMOVE, pausa.GetPosition() + wx.Point(2, 2))
    _manda(b, WM_MOUSEMOVE, pausa.GetPosition() + wx.Point(4, 4))
    _manda(b, WM_LBUTTONDOWN, pausa.GetPosition() + wx.Point(4, 4))
    _manda(b, WM_LBUTTONUP, pausa.GetPosition() + wx.Point(4, 4))
    assert fatti == ["pausa"]
    assert user32.GetFocus() == fuoco and user32.GetActiveWindow() == attiva and wx.Window.FindFocus() is finestra.albero
    # Arrivato con un salto solo, come il mouse portato da NVDA: il clic non vale.
    b.nascondi()
    mondo.muovi()
    assert b.IsShown()
    _manda(b, WM_MOUSEMOVE, pausa.GetPosition() + wx.Point(3, 3))
    _manda(b, WM_LBUTTONDOWN, pausa.GetPosition() + wx.Point(3, 3))
    _manda(b, WM_LBUTTONUP, pausa.GetPosition() + wx.Point(3, 3))
    assert fatti == ["pausa"]
    # Il nome e il tasto del pulsante sotto il puntatore si scrivono nella barra.
    assert b._sotto == b.comandi().index("pausa")
    finestra.Hide()


def test_la_voce_delle_impostazioni_la_spegne(finestra):
    mondo = _Mondo(finestra)
    b = finestra.barra
    assert finestra.impostazioni["barra_dei_comandi"] is True
    assert finestra._applica_l_impostazione("barra_dei_comandi", False) == "Barra dei comandi per il mouse spenta."
    assert finestra.impostazioni["barra_dei_comandi"] is False and not b._timer.IsRunning()
    mondo.muovi()
    assert not b.IsShown()
    frase = finestra._applica_l_impostazione("barra_dei_comandi", True)
    assert b._timer.IsRunning() and frase == "Barra dei comandi per il mouse accesa: compare quando il mouse si muove sopra MeTeOra."


def test_alla_chiusura_la_barra_si_ferma(app, tmp_path):
    from finestra import Finestra

    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    timer = f.barra._timer
    assert timer.IsRunning()
    f.Close(force=True)
    assert not timer.IsRunning()
    f.Destroy()
