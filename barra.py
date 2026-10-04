# MeTeOra, la barra dei comandi per il mouse: i comandi principali, per chi vede, sopra la finestra quando il mouse si muove.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.87.0, chiesta da Gabriele per chi vede. Nella 1.88.0 anche sopra il video, con la linea del tempo.

"""La barra dei comandi per il mouse (1.87.0).

Gabriele la vuole per chi vede, che con i soli tasti trova MeTeOra insolito,
ma senza il minimo costo per chi usa uno screen reader. Per questo:
- e' una finestrella a parte, sovrapposta in basso al centro della finestra
  su cui compare, che Windows non attiva mai (WS_EX_NOACTIVATE) e che non
  accetta il fuoco: un clic non sposta il fuoco ne' la finestra attiva, e
  NVDA non ha niente da annunciare;
- non e' nell'ordine di tabulazione e non ha tasti; quando e' nascosta, per
  Windows non e' visibile, e nemmeno la navigazione a oggetti la trova;
- compare solo quando il mouse si muove davvero sopra la sua finestra, se e'
  la finestra attiva, come nei player: un movimento lungo almeno
  MOVIMENTI_PER_COMPARIRE giri del timer; sopra la finestra principale mai
  sotto il puntatore. Il mouse portato da NVDA su un oggetto fa un salto
  solo: la barra non compare, e il clic di NVDA che segue non la trova
  (revisione della 1.87.0);
- sparisce dopo NASCONDI_DOPO secondi di mouse fermo fuori da lei, quando il
  puntatore esce dalla finestra, con un menu aperto e mentre la finestra si
  sposta o si ridimensiona;
- un pulsante risponde solo al puntatore arrivato muovendosi sulla barra, e
  chiama lo stesso comando del suo tasto, con gli stessi suoni e le stesse
  righe nella console; il nome e il tasto del pulsante sotto il puntatore si
  scrivono nella barra stessa, al posto dei suggerimenti di Windows, che NVDA
  potrebbe leggere.
Dalla 1.88.0 la stessa barra sta anche sopra la finestra del video, in
finestra e a schermo intero, con in piu' la linea del tempo, larga quasi
quanto il video: un clic salta in quel punto, e trascinando si salta dove si
lascia. Ogni finestra ha la sua barra, che compare solo quando lei e' attiva:
le due non sono mai visibili insieme. Nel video la barra puo' comparire
anche sotto il puntatore fermo: sotto c'e' solo l'immagine, niente che NVDA
voglia cliccare.
Le icone sono i simboli dei font di Windows, Segoe Fluent Icons su Windows 11
e Segoe MDL2 Assets su Windows 10: nessun file da distribuire, nitide a ogni
dimensione. Le misure vengono dai caratteri di Windows, mai in pixel fissi,
per chi usa i caratteri grandi.
"""

import ctypes
import time
from ctypes import wintypes

import wx

from valori import tempo as scrivi_il_tempo

# Ogni quanto si guarda il mouse; quanti giri di fila il mouse deve muoversi
# perche' la barra compaia; dopo quanti secondi di mouse fermo sparisce; quanti
# movimenti sulla barra servono perche' un clic valga.
INTERVALLO = 150
MOVIMENTI_PER_COMPARIRE = 2
NASCONDI_DOPO = 3.0
MOVIMENTI_PER_CLICCARE = 2
# Con la linea del tempo, la barra e' larga questa parte della finestra.
LARGHEZZA_CON_IL_TEMPO = 0.9
NOME = "Barra dei comandi per il mouse"
# I font dei simboli di Windows, nell'ordine di preferenza.
FONT_DEI_SIMBOLI = ("Segoe Fluent Icons", "Segoe MDL2 Assets")
# I gruppi della barra: (titolo, [(comando della finestra, simbolo, nome, tasto)]).
# I comandi sono quelli dei tasti, _comando_<nome> della finestra principale.
GRUPPI = [
    ("Riproduzione", [
        ("precedente", "\ue892", "Brano precedente", "Z"),
        ("indietro", "\ueb9e", "Indietro nel brano", "Q"),
        ("play", "\ue768", "Suona", "X"),
        ("pausa", "\ue769", "Pausa", "C"),
        ("stop", "\ue71a", "Stop", "V"),
        ("avanti", "\ueb9d", "Avanti nel brano", "E"),
        ("successivo", "\ue893", "Brano successivo", "B"),
    ]),
    ("Volume", [
        ("volume_giu", "\ue993", "Volume giù", "meno"),
        ("muto", "\ue74f", "Muto", "M"),
        ("volume_su", "\ue995", "Volume su", "più"),
    ]),
    ("Velocità", [
        ("velocita_giu", "\ue738", "Più lenta", "A"),
        ("velocita_normale", "\ue72c", "Velocità normale", "S"),
        ("velocita_su", "\ue710", "Più veloce", "D"),
    ]),
    ("Tono", [
        ("tono_giu", "\ue738", "Tono più basso", "F"),
        ("tono_normale", "\ue72c", "Tono normale", "G"),
        ("tono_su", "\ue710", "Tono più alto", "H"),
    ]),
]

_GWL_EXSTYLE = -20
_WS_EX_NOACTIVATE = 0x08000000
_WM_NCACTIVATE = 0x0086
# GetGUIThreadInfo: un menu aperto, o la finestra che si sposta o si ridimensiona.
_GUI_INMOVESIZE = 0x0002
_GUI_INMENUMODE = 0x0004
_GUI_POPUPMENUMODE = 0x0010


class _GUITHREADINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("flags", wintypes.DWORD), ("hwndActive", wintypes.HWND), ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND), ("hwndMenuOwner", wintypes.HWND), ("hwndMoveSize", wintypes.HWND), ("hwndCaret", wintypes.HWND),
        ("rcCaret", wintypes.RECT)]


def _user32():
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
    user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
    user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
    user32.GetGUIThreadInfo.argtypes = [wintypes.DWORD, ctypes.POINTER(_GUITHREADINFO)]
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    return user32


def _non_attivabile(maniglia):
    """Windows non attiva mai la finestra, nemmeno al clic."""
    user32 = _user32()
    stile = user32.GetWindowLongPtrW(maniglia, _GWL_EXSTYLE)
    user32.SetWindowLongPtrW(maniglia, _GWL_EXSTYLE, stile | _WS_EX_NOACTIVATE)


def stile_esteso(maniglia):
    """Lo stile esteso di una finestra, per le prove."""
    return _user32().GetWindowLongPtrW(maniglia, _GWL_EXSTYLE)


def font_dei_simboli():
    """Il nome del font dei simboli di Windows che c'e', o None."""
    for nome in FONT_DEI_SIMBOLI:
        if wx.FontEnumerator.IsValidFacename(nome):
            return nome
    return None


class BarraDeiComandi(wx.PopupWindow):
    """La barra. principale e' la finestra di MeTeOra, che ha i comandi;
    sopra e' la finestra sopra cui compare, di partenza la principale; tempo,
    per la linea del tempo, e' la terna (posizione(), durata(), salta(secondi)),
    con i secondi del brano, None se non si sanno; anche_sotto_il_puntatore la
    lascia comparire sotto il puntatore fermo. acceso dice se la voce delle
    impostazioni la vuole; orologio e' time.monotonic, sostituibile nelle
    prove."""

    def __init__(self, principale, acceso=True, orologio=time.monotonic, sopra=None, tempo=None, anche_sotto_il_puntatore=False):
        sopra = sopra or principale
        super().__init__(sopra, wx.BORDER_SIMPLE)
        self._principale = principale
        self._sopra = sopra
        self._tempo = tempo
        self._anche_sotto_il_puntatore = anche_sotto_il_puntatore
        self._orologio = orologio
        self._acceso = False
        self._ultima_posizione = None
        self._di_fila = 0
        self._ultimo_movimento = 0.0
        self._passi_sulla_barra = 0
        self._sotto = None
        # Sulla linea del tempo: la frazione sotto il puntatore, e quella a cui
        # si sta trascinando.
        self._sul_tempo = None
        self._trascinando = None
        # La durata del brano quando il trascinamento e' cominciato: se il
        # brano cambia intanto, il salto non si fa (revisione della 1.88.0).
        self._durata_al_via = None
        self._celle = []
        self._titoli = []
        self._linea = None
        self._larghezza = 0
        # Il nome per chi la incontra con il mouse e NVDA: wx le darebbe "panel".
        self.SetName(NOME)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        _non_attivabile(self.GetHandle())
        self._misura()
        self._disponi(self._larghezza_voluta())
        self.Bind(wx.EVT_PAINT, self._disegna)
        self.Bind(wx.EVT_MOTION, self._movimento)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._uscito)
        # Il doppio clic vale due clic: due pressioni veloci di Volume su
        # alzano due volte.
        self.Bind(wx.EVT_LEFT_DOWN, self._clic)
        self.Bind(wx.EVT_LEFT_DCLICK, self._clic)
        self.Bind(wx.EVT_LEFT_UP, self._rilascio)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self._cattura_persa)
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, lambda _evento: self.guarda(), self._timer)
        # Distrutta con la finestra senza passare da ferma(): il timer non
        # deve suonare per una finestra che non c'e' piu'.
        self.Bind(wx.EVT_WINDOW_DESTROY, self._distrutta)
        self.accendi(acceso)

    # Mai il fuoco: niente da tastiera, niente al clic.
    def AcceptsFocus(self):
        return False

    def AcceptsFocusFromKeyboard(self):
        return False

    def accendi(self, acceso):
        """La voce delle impostazioni: spenta, la barra sparisce e non si
        guarda piu' il mouse."""
        self._acceso = bool(acceso)
        if self._acceso:
            if not self._timer.IsRunning():
                self._timer.Start(INTERVALLO)
        else:
            self._timer.Stop()
            self._dimentica_il_mouse()
            self.nascondi()

    def ferma(self):
        """Alla chiusura di MeTeOra."""
        self._timer.Stop()
        self.nascondi()

    def _distrutta(self, evento):
        if evento.GetEventObject() is self:
            self._timer.Stop()
        evento.Skip()

    # Le misure, dai caratteri di Windows.

    def _misura(self):
        di_sistema = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._testo = wx.Font(di_sistema)
        nome = font_dei_simboli()
        self._simboli = wx.Font(wx.FontInfo(round(di_sistema.GetPointSize() * 1.8)).FaceName(nome)) if nome else None
        dc = wx.ClientDC(self)
        dc.SetFont(self._testo)
        self._alto_testo = dc.GetTextExtent("Ag")[1]
        self._largo_tempo = dc.GetTextExtent("88:88:88")[0]
        if self._simboli is not None:
            dc.SetFont(self._simboli)
            self._lato = max(dc.GetTextExtent(GRUPPI[0][1][2][1])) + self._alto_testo
        else:
            self._lato = self._alto_testo * 3
        self._margine = self._alto_testo // 2
        self._stacco = self._alto_testo
        celle = sum(len(comandi) for _titolo, comandi in GRUPPI)
        self._larghezza_dei_comandi = celle * self._lato + (len(GRUPPI) - 1) * self._stacco

    def _larghezza_voluta(self):
        minima = self._larghezza_dei_comandi + 2 * self._margine
        if self._tempo is None:
            return minima
        return max(minima, round(self._area_della_finestra().width * LARGHEZZA_CON_IL_TEMPO))

    def _disponi(self, larghezza):
        """Le righe della barra per questa larghezza: la linea del tempo, se
        c'e', i titoli dei gruppi, i pulsanti al centro e la riga del nome."""
        self._larghezza = larghezza
        alto, margine = self._alto_testo, self._margine
        y = margine
        self._linea = None
        if self._tempo is not None:
            sinistra = margine + self._largo_tempo + margine
            self._linea = wx.Rect(sinistra, y, larghezza - 2 * sinistra, alto + margine)
            y += alto + margine + margine
        x = (larghezza - self._larghezza_dei_comandi) // 2
        self._celle, self._titoli = [], []
        for titolo, comandi in GRUPPI:
            inizio = x
            for comando, simbolo, nome, tasto in comandi:
                self._celle.append((wx.Rect(x, y + alto, self._lato, self._lato), comando, simbolo, nome, tasto))
                x += self._lato
            self._titoli.append((titolo, wx.Rect(inizio, y, x - inizio, alto)))
            x += self._stacco
        self._riga_del_nome = wx.Rect(margine, y + alto + self._lato, larghezza - 2 * margine, alto)
        self.SetClientSize(larghezza, y + alto + self._lato + alto + margine)

    # Quando si vede.

    def _posizione_del_mouse(self):
        return wx.GetMousePosition()

    def _finestra_attiva(self):
        f = self._sopra
        return f.IsShown() and f.IsActive() and not f.IsIconized()

    def _occupata(self):
        """Vero con un menu aperto, o mentre la finestra si sposta o si
        ridimensiona: la barra non deve coprire il menu, ne' restare indietro."""
        info = _GUITHREADINFO(cbSize=ctypes.sizeof(_GUITHREADINFO))
        if not _user32().GetGUIThreadInfo(0, ctypes.byref(info)):
            return False
        return bool(info.flags & (_GUI_INMOVESIZE | _GUI_INMENUMODE | _GUI_POPUPMENUMODE))

    def _area_della_finestra(self):
        """L'area interna della finestra su cui compare, sullo schermo: senza
        la barra del titolo e i bordi, anche quelli invisibili di Windows 11."""
        f = self._sopra
        return wx.Rect(f.ClientToScreen(wx.Point(0, 0)), f.GetClientSize())

    def _dove_compare(self):
        """Il rettangolo della barra sullo schermo, in basso al centro."""
        area = self._area_della_finestra()
        mia_larghezza, mia_altezza = self.GetSize()
        x = area.x + max(0, (area.width - mia_larghezza) // 2)
        y = area.y + max(0, area.height - mia_altezza - mia_altezza // 4)
        return wx.Rect(x, y, mia_larghezza, mia_altezza)

    def _dimentica_il_mouse(self):
        # Al ritorno, la prima posizione non conta come movimento.
        self._ultima_posizione = None
        self._di_fila = 0

    def guarda(self):
        """Il giro del timer: mostra la barra quando il mouse si muove davvero
        sopra la finestra attiva, e la nasconde quando il mouse esce, resta
        fermo fuori dalla barra, o la finestra e' occupata. Con la linea del
        tempo, la ridisegna con il tempo di adesso."""
        if not self._acceso or not self._finestra_attiva() or self._occupata():
            self._dimentica_il_mouse()
            self.nascondi()
            return
        posizione = self._posizione_del_mouse()
        adesso = self._orologio()
        mosso = self._ultima_posizione is not None and posizione != self._ultima_posizione
        self._ultima_posizione = posizione
        self._di_fila = self._di_fila + 1 if mosso else 0
        if mosso:
            self._ultimo_movimento = adesso
        dentro = self._area_della_finestra().Contains(posizione)
        if not self.IsShown():
            if self._di_fila >= MOVIMENTI_PER_COMPARIRE and dentro and (self._anche_sotto_il_puntatore or not self._dove_compare().Contains(posizione)):
                self._mostra()
            return
        # La finestra spostata o ridimensionata: la barra la segue. Si
        # confronta la posizione: il rettangolo sullo schermo ha il bordo.
        if self._larghezza_voluta() != self._larghezza:
            self._disponi(self._larghezza_voluta())
        dove = self._dove_compare().GetPosition()
        if self.GetPosition() != dove:
            self.SetPosition(dove)
        if self._tempo is not None:
            self.Refresh()
        if self._trascinando is not None or (self.GetScreenRect().Contains(posizione) and self._passi_sulla_barra):
            return
        if not dentro or adesso - self._ultimo_movimento > NASCONDI_DOPO:
            self.nascondi()

    def _mostra(self):
        if self._larghezza_voluta() != self._larghezza:
            self._disponi(self._larghezza_voluta())
        self.SetPosition(self._dove_compare().GetPosition())
        self._sotto = self._sul_tempo = None
        self._passi_sulla_barra = 0
        self.Show()

    def nascondi(self):
        if self._trascinando is not None:
            self._trascinando = None
            if self.HasCapture():
                self.ReleaseMouse()
        if self.IsShown():
            self.Hide()
            self._didascalia_giusta()
        self._sotto = self._sul_tempo = None
        self._passi_sulla_barra = 0

    def _didascalia_giusta(self):
        """wx disegna attiva la barra del titolo della finestra mentre la
        barra e' visibile, e la lascia cosi' anche dopo, se intanto si e'
        passati a un'altra finestra: qui la si ridisegna com'e' davvero."""
        user32 = _user32()
        maniglia = self._sopra.GetHandle()
        if maniglia and user32.GetForegroundWindow() != maniglia:
            user32.SendMessageW(maniglia, _WM_NCACTIVATE, 0, 0)

    # La linea del tempo.

    def _durata(self):
        if self._tempo is None:
            return None
        durata = self._tempo[1]()
        return durata if durata and durata > 0 else None

    def _frazione_in(self, punto):
        """La frazione della linea del tempo sotto il punto, fra 0 e 1, o
        None se il punto non e' sulla linea o la durata non si sa."""
        if self._linea is None or not self._linea.Contains(punto) or self._durata() is None:
            return None
        return self._frazione_di(punto)

    def _frazione_di(self, punto):
        return min(1.0, max(0.0, (punto.x - self._linea.x) / max(1, self._linea.width)))

    # Il disegno.

    def _disegna(self, _evento):
        dc = wx.AutoBufferedPaintDC(self)
        sfondo = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        testo = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT)
        evidenza = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        spento = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        dc.SetBackground(wx.Brush(sfondo))
        dc.Clear()
        dc.SetTextForeground(testo)
        dc.SetFont(self._testo)
        didascalia = None
        if self._linea is not None:
            didascalia = self._disegna_il_tempo(dc, testo, evidenza, spento)
        dc.SetFont(self._testo)
        for titolo, riquadro in self._titoli:
            dc.DrawLabel(titolo, riquadro, wx.ALIGN_CENTER)
        for indice, (riquadro, _comando, simbolo, nome, _tasto) in enumerate(self._celle):
            if indice == self._sotto:
                dc.SetPen(wx.Pen(evidenza, 2))
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                dc.DrawRoundedRectangle(riquadro.Deflate(2, 2), 4)
            if self._simboli is not None:
                dc.SetFont(self._simboli)
                dc.DrawLabel(simbolo, riquadro, wx.ALIGN_CENTER)
            else:
                dc.SetFont(self._testo)
                dc.DrawLabel(nome[:3], riquadro, wx.ALIGN_CENTER)
        if self._sotto is not None:
            _riquadro, _comando, _simbolo, nome, tasto = self._celle[self._sotto]
            didascalia = f"{nome}, tasto {tasto}"
        if didascalia:
            dc.SetFont(self._testo)
            dc.DrawLabel(didascalia, self._riga_del_nome, wx.ALIGN_CENTER)

    def _disegna_il_tempo(self, dc, testo, evidenza, spento):
        """La linea del tempo, con il tempo passato a sinistra e la durata a
        destra; torna la didascalia del punto indicato o trascinato."""
        linea, margine = self._linea, self._margine
        durata = self._durata()
        posizione = self._tempo[0]() if durata is not None else None
        dc.DrawLabel(scrivi_il_tempo(posizione), wx.Rect(margine, linea.y, self._largo_tempo, linea.height), wx.ALIGN_CENTER)
        dc.DrawLabel(scrivi_il_tempo(durata), wx.Rect(linea.right + margine, linea.y, self._largo_tempo, linea.height), wx.ALIGN_CENTER)
        binario = wx.Rect(linea.x, linea.y + linea.height // 2 - margine // 2, linea.width, max(2, margine))
        dc.SetPen(wx.Pen(spento if durata is None else testo, 1))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(binario)
        if durata is None:
            return None
        frazione = self._trascinando if self._trascinando is not None else min(1.0, max(0.0, (posizione or 0) / durata))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(evidenza))
        dc.DrawRectangle(wx.Rect(binario.x, binario.y, round(binario.width * frazione), binario.height))
        x = binario.x + round(binario.width * frazione)
        dc.DrawCircle(x, binario.y + binario.height // 2, linea.height // 3)
        indicata = self._trascinando if self._trascinando is not None else self._sul_tempo
        if indicata is None:
            return None
        return f"Vai a {scrivi_il_tempo(indicata * durata)} di {scrivi_il_tempo(durata)}"

    def _cella_in(self, punto):
        return next((i for i, cella in enumerate(self._celle) if cella[0].Contains(punto)), None)

    # Il mouse sulla barra.

    def _movimento(self, evento):
        self._ultimo_movimento = self._orologio()
        self._passi_sulla_barra += 1
        punto = evento.GetPosition()
        if self._trascinando is not None:
            self._trascinando = self._frazione_di(punto)
            self.Refresh()
            return
        sotto, sul_tempo = self._cella_in(punto), self._frazione_in(punto)
        if sotto != self._sotto or sul_tempo != self._sul_tempo:
            self._sotto, self._sul_tempo = sotto, sul_tempo
            self.Refresh()

    def _uscito(self, _evento):
        if self._trascinando is not None:
            return
        self._passi_sulla_barra = 0
        if self._sotto is not None or self._sul_tempo is not None:
            self._sotto = self._sul_tempo = None
            self.Refresh()

    def _clic(self, evento):
        """Il comando del pulsante, come il suo tasto; sulla linea del tempo,
        l'inizio di un salto, che si fa al rilascio. Senza Skip: il clic non
        deve dare il fuoco a niente. Vale solo se il puntatore e' arrivato
        muovendosi: un salto solo, come quello del mouse portato da NVDA, non
        basta."""
        self._ultimo_movimento = self._orologio()
        if self._passi_sulla_barra < MOVIMENTI_PER_CLICCARE:
            return
        punto = evento.GetPosition()
        frazione = self._frazione_in(punto)
        if frazione is not None:
            # Il secondo clic di un doppio clic sulla linea non salta di nuovo
            # nello stesso punto (revisione della 1.88.0).
            if evento.GetEventType() == wx.wxEVT_LEFT_DCLICK:
                return
            self._trascinando = frazione
            self._durata_al_via = self._durata()
            if not self.HasCapture():
                self.CaptureMouse()
            self.Refresh()
            return
        indice = self._cella_in(punto)
        if indice is not None:
            getattr(self._principale, f"_comando_{self._celle[indice][1]}")()

    def _rilascio(self, _evento):
        """Il salto sulla linea del tempo: dove si lascia il pulsante."""
        if self._trascinando is None:
            return
        frazione, self._trascinando = self._trascinando, None
        if self.HasCapture():
            self.ReleaseMouse()
        # La didascalia dice il punto lasciato, finche' il mouse non si muove.
        self._sul_tempo = frazione
        durata = self._durata()
        if durata is not None and durata == self._durata_al_via:
            self._tempo[2](frazione * durata)
        self.Refresh()

    def _cattura_persa(self, _evento):
        self._trascinando = None
        self.Refresh()

    def comandi(self):
        """I comandi della barra, nell'ordine: per le prove e per il manuale."""
        return [cella[1] for cella in self._celle]
