# MeTeOra, la vista del karaoke: il testo da cantare a tutto schermo, per chi canta guardando lo schermo.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 14/11/2026: nasce con la 3.18.0, chiesta da Gabriele per una persona vedente che cantava il karaoke.

"""La vista del karaoke (Gabriele, 3.18.0).

Con il video acceso, Maiuscolo con F1, un brano da cantare senza un video
suo, come un MIDI, un KAR o un audio con il suo LRC, apre questa finestra a
tutto schermo, sopra MeTeOra; Ctrl con F1 spegne il video e la chiude. In
alto c'e' la riga da cantare, alta circa un decimo dello schermo, in
grassetto e in un colore che sullo sfondo risalta piu' del testo; sotto
arrivano le tre prossime, alte due terzi di lei, nei colori della console.
Quelle gia' cantate spariscono. Le misure seguono lo schermo, non i
caratteri della console, perche' si legga da qualche metro (Gabriele).
 Prima del canto sono tutte prossime; fra due righe resta in alto
l'ultima cominciata, finche' non comincia la seguente, che arriva con
l'anticipo del karaoke.
I tasti passano tutti alla finestra principale, come per il video, tranne
Esc, che nasconde la vista per il brano in corso; Maiuscolo con F1 la
riapre. La finestra guarda la posizione del brano dieci volte al secondo, e
si ridisegna solo quando cambia la riga, o la finestra.
"""

import bisect

import wx

from lingua import _

# Ogni quanti millisecondi si guarda la posizione del brano.
PASSO = 100
# L'altezza dei caratteri della riga da cantare, in parti dell'altezza dello
# schermo, e quella delle prossime rispetto a lei; quante prossime (Gabriele).
ALTEZZA_DELLA_RIGA = 0.1
ALTEZZA_DELLE_PROSSIME = 2 / 3
PROSSIME = 3
# Il margine attorno al testo, in parti della larghezza dello schermo.
MARGINE = 0.04
# Lo spazio fra la riga da cantare e le prossime, in righe delle prossime.
STACCO = 0.8
# I colori fra cui si sceglie quello della riga da cantare, in [r, g, b] da 0
# a 255: sugli sfondi scuri il giallo del karaoke, poi il bianco; su quelli
# chiari il blu scuro, poi il nero.
SUGLI_SCURI = ((255, 255, 0), (255, 255, 255))
SUI_CHIARI = ((0, 0, 140), (0, 0, 0))


def righe_da_mostrare(blocchi, posizione):
    """(la riga da cantare, o None prima del canto, e le PROSSIME seguenti)
    dei blocchi del karaoke [(inizio, fine, testo)] ai secondi posizione."""
    if not blocchi:
        return None, []
    if posizione is None:
        return None, [testo for _inizio, _fine, testo in blocchi[:PROSSIME]]
    indice = bisect.bisect_right([inizio for inizio, _fine, _testo in blocchi], posizione) - 1
    corrente = blocchi[indice][2] if indice >= 0 else None
    return corrente, [testo for _inizio, _fine, testo in blocchi[indice + 1:indice + 1 + PROSSIME]]


def _luminanza(rgb):
    """La luminanza relativa di un colore da 0 a 255, come la conta il WCAG."""
    def lineare(valore):
        valore /= 255
        return valore / 12.92 if valore <= 0.03928 else ((valore + 0.055) / 1.055) ** 2.4

    r, g, b = (lineare(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrasto(primo, secondo):
    """Il rapporto di contrasto del WCAG fra due colori, da 1 a 21."""
    chiara, scura = sorted((_luminanza(primo), _luminanza(secondo)), reverse=True)
    return (chiara + 0.05) / (scura + 0.05)


def colore_in_evidenza(testo, sfondo):
    """Il colore della riga da cantare: il primo dei candidati per lo sfondo
    che sullo sfondo risalta piu' del colore del testo; se nessuno lo fa,
    quello che risalta di piu'."""
    candidati = SUGLI_SCURI if _luminanza(sfondo) < 0.18 else SUI_CHIARI
    di_partenza = contrasto(testo, sfondo)
    for candidato in candidati:
        if candidato != tuple(testo) and contrasto(candidato, sfondo) > di_partenza:
            return candidato
    return max(candidati + SUGLI_SCURI + SUI_CHIARI, key=lambda c: contrasto(c, sfondo))


def a_capo(testo, larghezza, misura):
    """Le righe dello schermo di un testo, che va a capo fra le parole per
    stare in larghezza; misura(testo) da' la sua larghezza. Una parola sola
    piu' larga resta intera. Gli a capo del testo, come nelle strofe, restano."""
    righe = []
    for pezzo in testo.split("\n"):
        riga = ""
        for parola in pezzo.split():
            prova = f"{riga} {parola}" if riga else parola
            if riga and misura(prova) > larghezza:
                righe.append(riga)
                riga = parola
            else:
                riga = prova
        righe.append(riga)
    return righe


class FinestraKaraoke(wx.Frame):
    """principale riceve i tasti; blocchi() da' i blocchi del karaoke del
    brano in corso, o None; posizione() i suoi secondi, o None; nascondi() e'
    quello che fa Esc, e la chiusura della finestra."""

    def __init__(self, principale, blocchi, posizione, nascondi):
        # Traduttori: il titolo della vista del karaoke, prima che ne prenda uno del brano.
        super().__init__(None, title=_("MeTeOra, karaoke"), style=wx.DEFAULT_FRAME_STYLE)
        self._principale, self._blocchi, self._posizione, self._nascondi = principale, blocchi, posizione, nascondi
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        # Traduttori: il nome del pannello dove si disegna il testo da cantare.
        self.pannello = wx.Panel(self, name=_("Testo da cantare"))
        self.pannello.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.pannello, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self._colori = ((0, 200, 200), (0, 0, 0), (255, 255, 0))
        self._mostrate = None
        self._orologio = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._passo, self._orologio)
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.Bind(wx.EVT_CLOSE, self._alla_chiusura)
        self.pannello.Bind(wx.EVT_PAINT, self._disegna)
        self.pannello.Bind(wx.EVT_SIZE, lambda evento: (self.pannello.Refresh(), evento.Skip()))

    def apri(self, titolo, testo, sfondo, rettangolo):
        """Mostra la vista a tutto schermo sullo schermo di rettangolo, con i
        colori della console in [r, g, b] da 0 a 255, e le da' il fuoco."""
        self.SetTitle(titolo)
        self._colori = (tuple(testo), tuple(sfondo), colore_in_evidenza(testo, sfondo))
        self._mostrate = None
        if not self.IsShown():
            self.SetRect(rettangolo)
            self.Show()
        if not self.IsFullScreen():
            self.ShowFullScreen(True)
        self.Raise()
        self.pannello.SetFocus()
        self.pannello.Refresh()
        if not self._orologio.IsRunning():
            self._orologio.Start(PASSO)

    def chiudi(self):
        """Toglie lo schermo intero e nasconde la vista."""
        self._orologio.Stop()
        if self.IsFullScreen():
            self.ShowFullScreen(False)
        self.Hide()

    def mostrate(self):
        """(la riga da cantare, le prossime) di adesso, come le disegna."""
        return righe_da_mostrare(self._blocchi() or [], self._posizione())

    def _passo(self, _evento):
        if not self.IsShown():
            return
        adesso = self.mostrate()
        if adesso != self._mostrate:
            self._mostrate = adesso
            self.pannello.Refresh()
        if self.IsActive() and wx.Window.FindFocus() is None:
            self.pannello.SetFocus()

    @staticmethod
    def _carattere(pixel, grassetto=False):
        return wx.Font(wx.FontInfo(wx.Size(0, max(8, int(pixel)))).Family(wx.FONTFAMILY_SWISS).Bold(grassetto))

    def _disegna(self, _evento):
        self.disegna_su(wx.AutoBufferedPaintDC(self.pannello), *self.pannello.GetClientSize())

    def disegna_su(self, dc, larghezza, altezza):
        """Disegna la vista su dc, grande larghezza per altezza: sul pannello,
        o su un'immagine per le prove."""
        testo, sfondo, evidenza = (wx.Colour(*c) for c in self._colori)
        dc.SetBackground(wx.Brush(sfondo))
        dc.Clear()
        margine = max(8, int(larghezza * MARGINE))
        utile = max(1, larghezza - 2 * margine)
        corrente, prossime = self._mostrate if self._mostrate is not None else self.mostrate()
        y = margine
        alta = altezza * ALTEZZA_DELLA_RIGA
        if corrente:
            dc.SetFont(self._carattere(alta, grassetto=True))
            dc.SetTextForeground(evidenza)
            for riga in a_capo(corrente, utile, lambda t: dc.GetTextExtent(t)[0]):
                dc.DrawText(riga, margine, y)
                y += dc.GetCharHeight()
        dc.SetFont(self._carattere(alta * ALTEZZA_DELLE_PROSSIME))
        dc.SetTextForeground(testo)
        y += int(dc.GetCharHeight() * STACCO) if corrente else 0
        for prossima in prossime:
            for riga in a_capo(prossima, utile, lambda t: dc.GetTextExtent(t)[0]):
                if y + dc.GetCharHeight() > altezza - margine:
                    return
                dc.DrawText(riga, margine, y)
                y += dc.GetCharHeight()

    def _tasto(self, evento):
        if evento.GetKeyCode() == wx.WXK_ESCAPE and evento.GetModifiers() == wx.MOD_NONE:
            self._nascondi()
            return
        self._principale._tasto(evento)

    def _alla_chiusura(self, evento):
        # La vista si chiude davvero solo con MeTeOra: qui si nasconde.
        if evento.CanVeto():
            evento.Veto()
            self._nascondi()
            return
        self._orologio.Stop()
        self.Destroy()
