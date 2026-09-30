# MeTeOra, prototipo: l'albero a selezione multipla, da provare con NVDA prima di portarlo nella plancia.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce per decidere se la selezione multipla si puo' usare con NVDA.

"""Una finestra con un albero a selezione multipla (wx.TR_MULTIPLE) e un'area
di testo che dice, a ogni cambio, quali voci sono selezionate e quale ha il
fuoco. Da provare:
- freccia su e giu' muovono il fuoco e la selezione, come oggi;
- Maiuscolo con le frecce su e giu' allargano la selezione alle voci contigue;
- Ctrl con le frecce su e giu' muovono il fuoco senza cambiare la selezione;
- Ctrl+Spazio accende e spegne la selezione della voce che ha il fuoco;
- freccia destra e sinistra aprono e chiudono i rami.
Tab porta all'area di testo, Esc chiude.
Avvio: python prova_selezione_multipla.py
"""

import wx

CONTENUTO = {
    "Playlist Rock": ["uno.mp3", "due.mp3", "tre.mp3", "quattro.mp3", "cinque.mp3"],
    "Playlist Jazz": ["alfa.flac", "beta.flac", "gamma.flac"],
    "Cartella SID": ["Commando.sid", "Wizball.sid", "Turbo_Outrun.sid"],
}


class Prova(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Prova della selezione multipla")
        pannello = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(pannello, label="Albero di prova"), 0, wx.ALL, 4)
        self.albero = wx.TreeCtrl(pannello, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_MULTIPLE)
        self.albero.SetName("Albero di prova")
        sizer.Add(self.albero, 1, wx.EXPAND | wx.ALL, 4)
        sizer.Add(wx.StaticText(pannello, label="Selezione"), 0, wx.ALL, 4)
        self.stato = wx.TextCtrl(pannello, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.stato.SetName("Selezione")
        self.stato.SetMinSize(wx.Size(-1, self.stato.GetCharHeight() * 6))
        sizer.Add(self.stato, 0, wx.EXPAND | wx.ALL, 4)
        pannello.SetSizer(sizer)
        radice = self.albero.AddRoot("radice")
        for ramo, voci in CONTENUTO.items():
            nodo = self.albero.AppendItem(radice, ramo)
            for voce in voci:
                self.albero.AppendItem(nodo, voce)
        primo = self.albero.GetFirstChild(radice)[0]
        self.albero.Expand(primo)
        self.albero.SelectItem(primo)
        self.albero.Bind(wx.EVT_TREE_SEL_CHANGED, self._cambiata)
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self._cambiata(None)
        self.Maximize()

    def _cambiata(self, evento):
        if evento is not None:
            evento.Skip()
        # Mentre la finestra si chiude l'albero manda ancora qualche evento.
        if self.IsBeingDeleted() or not self.albero:
            return
        selezionate = [self.albero.GetItemText(v) for v in self.albero.GetSelections()]
        fuoco = self.albero.GetFocusedItem()
        testo_fuoco = self.albero.GetItemText(fuoco) if fuoco.IsOk() else "nessuna"
        righe = [
            f"Voci selezionate: {len(selezionate)}.",
            ", ".join(selezionate) if selezionate else "Nessuna.",
            f"Fuoco su: {testo_fuoco}.",
        ]
        self.stato.SetValue("\n".join(righe))

    def _tasto(self, evento):
        if evento.GetKeyCode() == wx.WXK_ESCAPE:
            self.Close()
            return
        evento.Skip()


if __name__ == "__main__":
    app = wx.App(False)
    Prova().Show()
    app.MainLoop()
