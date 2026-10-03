# MeTeOra, la finestra del video: due pannelli per i due lettori, e la barra del tempo per chi vede.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 7. Nella 1.66.36 Esc a schermo intero ha il riscontro di Maiuscolo con F5.

"""La finestra del video (tappa 7, piano 5.5).

Si apre sopra la finestra principale, grande come lei, quando parte un
brano con il video e il video e' acceso (Maiuscolo con F1); chi guarda puo'
spostarla, ridimensionarla o metterla a schermo intero (Maiuscolo con F5).
Dentro ci sono due pannelli, uno per ciascun lettore del motore: libmpv
disegna in quello del lettore che suona, e con la dissolvenza la finestra
mostra quello che entra.
I tasti passano tutti alla finestra principale (piano 5.5.5), tranne Esc,
che qui toglie lo schermo intero o nasconde il video invece di chiudere
MeTeOra. libmpv disegna con un suo filo, in una finestra sua dentro il
pannello: se il fuoco ci finisce, per esempio con un clic, il controllo
periodico lo riporta sul pannello, dove i tasti arrivano.
La barra del tempo (piano 5.5.1) e' per chi vede: compare quando il mouse
arriva sul bordo inferiore, resta un poco e si nasconde; trascinandola si
salta nel brano.
"""

import time

import wx

# Ogni quanti millisecondi si guardano il mouse, il fuoco e il tempo.
PASSO_DEL_CONTROLLO = 200
# La fascia del bordo inferiore in cui il mouse fa comparire la barra, come
# parte dell'altezza della finestra: niente misure fisse in pixel.
FASCIA_DELLA_BARRA = 0.12
# Per quanti secondi la barra resta, dopo che il mouse ha lasciato la fascia.
DURATA_DELLA_BARRA = 2.5
# I passi della barra.
PASSI_DELLA_BARRA = 1000


class FinestraVideo(wx.Frame):
    """principale riceve i tasti; posizione() e durata() danno i secondi del
    brano, None se non si sanno; salta(secondi) ci va; nascondi() e'
    quello che fa Esc fuori dallo schermo intero, e la chiusura della
    finestra."""

    def __init__(self, principale, posizione, durata, salta, nascondi):
        super().__init__(None, title="MeTeOra, video", style=wx.DEFAULT_FRAME_STYLE)
        self._principale = principale
        self._posizione, self._durata, self._salta, self._nascondi = posizione, durata, salta, nascondi
        self.SetBackgroundColour(wx.BLACK)
        self.pannelli = []
        sizer = wx.BoxSizer(wx.VERTICAL)
        for numero in (1, 2):
            pannello = wx.Panel(self, name=f"Video, lettore {numero}")
            pannello.SetBackgroundColour(wx.BLACK)
            sizer.Add(pannello, 1, wx.EXPAND)
            self.pannelli.append(pannello)
        self.barra = wx.Slider(self, minValue=0, maxValue=PASSI_DELLA_BARRA, name="Tempo del video")
        sizer.Add(self.barra, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.barra.Hide()
        self._attivo = 0
        self.pannelli[1].Hide()
        self._barra_fino_a = 0
        self._trascinando = False
        self._orologio = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._controllo, self._orologio)
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.Bind(wx.EVT_CLOSE, self._alla_chiusura)
        self.barra.Bind(wx.EVT_SCROLL_THUMBTRACK, self._trascina)
        self.barra.Bind(wx.EVT_SCROLL_CHANGED, self._lascia)

    def finestre(self):
        """Le maniglie dei due pannelli, nell'ordine dei lettori del motore."""
        return tuple(pannello.GetHandle() for pannello in self.pannelli)

    def mostra_il_lettore(self, indice):
        """Mostra il pannello del lettore che suona e nasconde l'altro."""
        if indice == self._attivo:
            return
        self._attivo = indice
        for numero, pannello in enumerate(self.pannelli):
            pannello.Show(numero == indice)
        self.Layout()

    def apri(self, titolo, rettangolo):
        """Mostra la finestra sopra la principale, grande come lei se non era
        gia' aperta, e le da' il fuoco."""
        self.SetTitle(titolo)
        if not self.IsShown():
            self.SetRect(rettangolo)
            self.Show()
        self.Raise()
        self.pannelli[self._attivo].SetFocus()
        if not self._orologio.IsRunning():
            self._orologio.Start(PASSO_DEL_CONTROLLO)

    def chiudi(self):
        """Nasconde la finestra, togliendo prima lo schermo intero."""
        self._orologio.Stop()
        if self.IsFullScreen():
            self.ShowFullScreen(False)
        self.barra.Hide()
        self.Hide()

    def schermo_intero(self):
        """Mette e toglie lo schermo intero; vero se adesso e' a schermo intero."""
        self.ShowFullScreen(not self.IsFullScreen())
        return self.IsFullScreen()

    def _tasto(self, evento):
        if evento.GetKeyCode() == wx.WXK_ESCAPE and evento.GetModifiers() == wx.MOD_NONE:
            if self.IsFullScreen():
                # Come Maiuscolo con F5, con il suo suono e la sua riga.
                self._principale._comando_schermo_intero()
            else:
                self._nascondi()
            return
        self._principale._tasto(evento)

    def _alla_chiusura(self, evento):
        # La finestra si chiude davvero solo con MeTeOra: qui si nasconde.
        if evento.CanVeto():
            evento.Veto()
            self._nascondi()
            return
        self._orologio.Stop()
        self.Destroy()

    def _controllo(self, _evento):
        """Il fuoco torna sul pannello se e' finito nella finestra di libmpv;
        la barra compare con il mouse sul bordo inferiore e segue il tempo."""
        if not self.IsShown():
            return
        if self.IsActive() and wx.Window.FindFocus() is None:
            self.pannelli[self._attivo].SetFocus()
        rettangolo = self.GetScreenRect()
        mouse = wx.GetMousePosition()
        fascia = rettangolo.GetBottom() - rettangolo.GetHeight() * FASCIA_DELLA_BARRA
        adesso = time.monotonic()
        if rettangolo.Contains(mouse) and mouse.y >= fascia:
            self._barra_fino_a = adesso + DURATA_DELLA_BARRA
        mostra = adesso < self._barra_fino_a or self._trascinando
        if mostra != self.barra.IsShown():
            self.barra.Show(mostra)
            self.Layout()
        if mostra and not self._trascinando:
            posizione, durata = self._posizione(), self._durata()
            if posizione is not None and durata:
                self.barra.SetValue(round(min(1.0, posizione / durata) * PASSI_DELLA_BARRA))

    def _trascina(self, evento):
        self._trascinando = True
        evento.Skip()

    def _lascia(self, evento):
        self._trascinando = False
        durata = self._durata()
        if durata:
            self._salta(self.barra.GetValue() / PASSI_DELLA_BARRA * durata)
        evento.Skip()
