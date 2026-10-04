# MeTeOra, la finestra del video: due pannelli per i due lettori, e la barra dei comandi con la linea del tempo per chi vede.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 7. Nella 1.66.36 Esc a schermo intero ha il riscontro di Maiuscolo con F5. Nella 1.88.0 la barra dei comandi con la linea del tempo, al posto del cursore.

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
Per chi vede (piano 5.5.1, Gabriele): dalla 1.88.0 la barra dei comandi
per il mouse di barra.py, con in piu' la linea del tempo: un clic salta in
quel punto. Compare quando il mouse si muove sopra il video, in finestra e a
schermo intero, e non prende mai il fuoco. Prima c'era un cursore di
Windows, che al clic avanzava a passi invece di saltare, toglieva spazio al
video quando compariva, e prendeva il fuoco al clic.
"""

import wx

from barra import BarraDeiComandi

# Ogni quanti millisecondi si guarda il fuoco.
PASSO_DEL_CONTROLLO = 200


class FinestraVideo(wx.Frame):
    """principale riceve i tasti; posizione() e durata() danno i secondi del
    brano, None se non si sanno; salta(secondi) ci va; nascondi() e'
    quello che fa Esc fuori dallo schermo intero, e la chiusura della
    finestra."""

    def __init__(self, principale, posizione, durata, salta, nascondi):
        super().__init__(None, title="MeTeOra, video", style=wx.DEFAULT_FRAME_STYLE)
        self._principale = principale
        self._nascondi = nascondi
        self.SetBackgroundColour(wx.BLACK)
        self.pannelli = []
        sizer = wx.BoxSizer(wx.VERTICAL)
        for numero in (1, 2):
            pannello = wx.Panel(self, name=f"Video, lettore {numero}")
            pannello.SetBackgroundColour(wx.BLACK)
            sizer.Add(pannello, 1, wx.EXPAND)
            self.pannelli.append(pannello)
        self.SetSizer(sizer)
        self._attivo = 0
        self.pannelli[1].Hide()
        # La barra sopra il video, con la linea del tempo: compare solo quando
        # questa finestra e' attiva, quindi mai insieme a quella della
        # finestra principale.
        self.barra = BarraDeiComandi(principale, acceso=principale.impostazioni["barra_dei_comandi"], sopra=self,
            tempo=(posizione, durata, salta), anche_sotto_il_puntatore=True)
        self._orologio = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._controllo, self._orologio)
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.Bind(wx.EVT_CLOSE, self._alla_chiusura)

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
        # La barra guarda il mouse solo a video aperto, se la voce delle
        # impostazioni la vuole.
        self.barra.accendi(self._principale.impostazioni["barra_dei_comandi"])

    def chiudi(self):
        """Nasconde la finestra, togliendo prima lo schermo intero."""
        self._orologio.Stop()
        if self.IsFullScreen():
            self.ShowFullScreen(False)
        self.barra.ferma()
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
        self.barra.ferma()
        self.Destroy()

    def _controllo(self, _evento):
        """Il fuoco torna sul pannello se e' finito nella finestra di libmpv."""
        if not self.IsShown():
            return
        if self.IsActive() and wx.Window.FindFocus() is None:
            self.pannelli[self._attivo].SetFocus()
