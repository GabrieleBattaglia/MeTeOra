# MeTeOra, i dialoghi: il campo da una riga, la domanda con Si' e No, la finestra delle impostazioni, la scelta da una lista, la finestra dei marcatori e l'invito a offrire un caffe'.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.51.0, per la finestra delle impostazioni (tappa 3, issue 14, piano 5.8); DialogoTesto arriva da finestra.py. Nella 1.66.36 la domanda con Sì e No, che si chiude con Esc. Nella 1.75.0 l'invito a offrire un caffe', come in Tornello. Nella 1.81.0 il filtro delle impostazioni. Nella 1.84.0 la proposta dell'aggiornamento.

"""I dialoghi di MeTeOra, fuori dalla finestra principale.

Sono tutti wx.Dialog: un dialogo ferma la risalita di EVT_CHAR_HOOK verso
la finestra principale, quindi le lettere scritte qui dentro non fanno
partire i comandi del lettore. I tasti propri di un dialogo li intercetta
il suo EVT_CHAR_HOOK, che arriva prima della gestione dei dialoghi di
Windows: Invio non finisce cosi' sul pulsante predefinito.
Lo schema e' quello di GBwx: STILE_ADATTABILE, pannello_scorrevole e
adatta_finestra con un minimo in pixel al cento per cento, che vale come
minimo e non come misura fissa; GBwx si importa dentro __init__. Ogni
controllo ha un nome, ed Esc chiude con il pulsante wx.ID_CANCEL.
Le azioni vere, come rinominare o eliminare un marker, le fa la finestra
principale: i dialoghi mostrano, chiedono e chiamano.
"""

import contextlib

import wx

from filtro import normale

# La riga della lista dei marcatori quando non ce n'e' nessuno: una lista
# vuota, per NVDA, non dice niente.
NESSUN_MARCATORE = "Nessun marcatore."
# Il PayPal.Me dell'autore, lo stesso di Tornello.
INDIRIZZO_PAYPAL = "https://paypal.me/GabrieleBattaglia780"


def _premuto_invio(evento):
    return evento.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and evento.GetModifiers() == wx.MOD_NONE


class DialogoTesto(wx.TextEntryDialog):
    """Un campo da una riga con il testo di prima gia' selezionato: scrivendo
    lo si sostituisce, con le frecce lo si corregge."""

    def ShowModal(self):
        campo = next((c for c in self.GetChildren() if isinstance(c, wx.TextCtrl)), None)
        if campo is not None:
            wx.CallAfter(campo.SelectAll)
        return super().ShowModal()


class DialogoConferma(wx.Dialog):
    """Una domanda con Si' e No, e No come risposta predefinita: Esc vale No,
    e le lettere S e N rispondono senza cercare il pulsante. ShowModal da'
    wx.ID_YES o wx.ID_NO. Prende il posto della domanda di Windows, che con i
    soli Si' e No non si chiude con Esc (tappa 9, 1.66.36)."""

    def __init__(self, genitore, domanda, titolo):
        from GBwx import STILE_ADATTABILE, adatta_finestra, pannello_scorrevole

        super().__init__(genitore, title=titolo, style=STILE_ADATTABILE)
        pannello = pannello_scorrevole(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # SetLabelText: una & nel nome di una playlist o di un file resta
        # com'e', invece di diventare la lettera di un tasto.
        self.domanda = wx.StaticText(pannello)
        self.domanda.SetLabelText(domanda)
        # Le righe vanno a capo a una sessantina di caratteri, misurati sul
        # carattere in uso.
        self.domanda.Wrap(self.domanda.GetCharWidth() * 60)
        self.si = wx.Button(pannello, wx.ID_YES, "&Sì")
        self.no = wx.Button(pannello, wx.ID_NO, "&No")
        pulsanti = wx.BoxSizer(wx.HORIZONTAL)
        for pulsante in (self.si, self.no):
            pulsanti.Add(pulsante, 0, wx.LEFT, 5)
        sizer.Add(self.domanda, 0, wx.ALL, 5)
        sizer.Add(pulsanti, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        pannello.SetSizer(sizer)
        adatta_finestra(self, pannello, (480, 160))
        self.SetEscapeId(wx.ID_NO)
        self.no.SetDefault()
        self.Bind(wx.EVT_BUTTON, lambda evento: self.EndModal(evento.GetId()))
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.no.SetFocus()

    def _tasto(self, evento):
        codice = evento.GetUnicodeKey()
        lettera = chr(codice).lower() if codice != wx.WXK_NONE and evento.GetModifiers() == wx.MOD_NONE else ""
        if lettera in ("s", "n"):
            self.EndModal(wx.ID_YES if lettera == "s" else wx.ID_NO)
            return
        evento.Skip()


class DialogoDonazione(wx.Dialog):
    """L'invito a offrire un caffe', come in Tornello: il testo di Donazione
    di GBUtils in un campo di sola lettura, che ha il fuoco all'apertura, e
    i pulsanti Dona con PayPal, che apre PayPal nel browser, e Chiudi, il
    predefinito: Invio nel testo ed Esc chiudono. ShowModal da' wx.ID_YES se
    si e' aperto PayPal, wx.ID_NO altrimenti (1.75.0)."""

    def __init__(self, genitore, testo):
        from GBwx import STILE_ADATTABILE, adatta_finestra, pannello_scorrevole

        super().__init__(genitore, title="Offri un caffè", style=STILE_ADATTABILE)
        pannello = pannello_scorrevole(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.testo = wx.TextCtrl(pannello, value=testo, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.testo.SetName("Offri un caffè")
        self.dona = wx.Button(pannello, wx.ID_YES, "&Dona con PayPal")
        self.chiudi = wx.Button(pannello, wx.ID_NO, "&Chiudi")
        pulsanti = wx.BoxSizer(wx.HORIZONTAL)
        for pulsante in (self.dona, self.chiudi):
            pulsanti.Add(pulsante, 0, wx.LEFT, 5)
        sizer.Add(self.testo, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(pulsanti, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        pannello.SetSizer(sizer)
        adatta_finestra(self, pannello, (480, 240))
        self.SetEscapeId(wx.ID_NO)
        self.chiudi.SetDefault()
        self.dona.Bind(wx.EVT_BUTTON, self._dona)
        self.chiudi.Bind(wx.EVT_BUTTON, lambda _evento: self.EndModal(wx.ID_NO))
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.testo.SetFocus()

    def _tasto(self, evento):
        """Invio nel testo, un campo su piu' righe che se lo terrebbe, preme
        Chiudi, come nelle finestre di messaggio; sui pulsanti Invio resta
        loro. Un Invio tenuto giu' non preme niente."""
        nel_testo = evento.GetEventObject() is self.testo
        if _premuto_invio(evento) and not evento.IsAutoRepeat() and nel_testo:
            self.EndModal(wx.ID_NO)
            return
        evento.Skip()

    def _dona(self, _evento):
        import webbrowser

        # Un browser che non parte non deve tenere aperto l'invito.
        with contextlib.suppress(Exception):
            webbrowser.open(INDIRIZZO_PAYPAL)
        self.EndModal(wx.ID_YES)


class FinestraAggiornamento(wx.Dialog):
    """La proposta dell'aggiornamento (1.84.0): in un campo di sola lettura,
    che ha il fuoco all'apertura, la versione nuova, quella che si ha, e le
    novita' dalla propria versione alla nuova; i pulsanti Aggiorna adesso e
    Non adesso. Esc, e Invio nel testo, valgono Non adesso: aggiornare si
    sceglie solo con il suo pulsante. Con attesa, in secondi, la finestra si
    chiude da sola come Non adesso allo scadere, e l'aggiornamento torna al
    prossimo avvio. ShowModal da' wx.ID_YES per aggiornare, wx.ID_NO
    altrimenti."""

    def __init__(self, genitore, attuale, nuova, novita, attesa=None):
        from GBwx import STILE_ADATTABILE, adatta_finestra, pannello_scorrevole

        super().__init__(genitore, title="Aggiornamento di MeTeOra", style=STILE_ADATTABILE)
        pannello = pannello_scorrevole(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        righe = [f"È disponibile MeTeOra {nuova}; tu hai la {attuale}.",
            "Aggiorna adesso scarica la versione nuova, chiude MeTeOra e lo riapre aggiornato; playlist, impostazioni e marker restano."]
        if attesa:
            righe.append(f"Se non rispondi entro {durata_dell_attesa(attesa)}, la finestra si chiude da sola e te lo ripropongo al prossimo avvio.")
        righe += ["Le novità:", (novita or "").strip() or "Nessuna novità scritta per questa versione."]
        self.testo = wx.TextCtrl(pannello, value="\n".join(righe), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.testo.SetName("Aggiornamento di MeTeOra")
        self.aggiorna = wx.Button(pannello, wx.ID_YES, "&Aggiorna adesso")
        self.non_adesso = wx.Button(pannello, wx.ID_NO, "&Non adesso")
        pulsanti = wx.BoxSizer(wx.HORIZONTAL)
        for pulsante in (self.aggiorna, self.non_adesso):
            pulsanti.Add(pulsante, 0, wx.LEFT, 5)
        sizer.Add(self.testo, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(pulsanti, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        pannello.SetSizer(sizer)
        adatta_finestra(self, pannello, (560, 420))
        self.SetEscapeId(wx.ID_NO)
        self.non_adesso.SetDefault()
        self.aggiorna.Bind(wx.EVT_BUTTON, lambda _evento: self.EndModal(wx.ID_YES))
        self.non_adesso.Bind(wx.EVT_BUTTON, lambda _evento: self.EndModal(wx.ID_NO))
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.testo.SetFocus()
        if attesa:
            wx.CallLater(round(attesa * 1000), self._scaduta)

    def _tasto(self, evento):
        """Invio nel testo vale Non adesso, come nelle finestre di messaggio;
        sui pulsanti Invio resta loro."""
        if evento.GetEventObject() is self.testo and _premuto_invio(evento) and not evento.IsAutoRepeat():
            self.EndModal(wx.ID_NO)
            return
        evento.Skip()

    def _scaduta(self):
        # La finestra puo' essere gia' chiusa, o distrutta.
        if self and self.IsModal():
            self.EndModal(wx.ID_NO)


def durata_dell_attesa(secondi):
    """Il tempo dell'attesa a parole: 2 minuti, 1 minuto, 90 secondi."""
    if secondi % 60:
        return f"{int(secondi)} secondi"
    minuti = int(secondi // 60)
    return "1 minuto" if minuti == 1 else f"{minuti} minuti"


class FinestraImpostazioni(wx.Dialog):
    """La finestra delle impostazioni: una lista piatta, una riga per voce,
    "Etichetta: valore". voci e' una lista di (chiave, testo della riga).
    Invio sulla lista, o il doppio clic, chiama al_cambio(chiave, dialogo):
    e' la finestra principale a chiedere il valore nuovo, ad applicarlo e a
    riscrivere la riga con aggiorna. Il pulsante Chiudi, o Esc, chiude.
    Prima della lista, con Maiuscolo e Tab, il filtro (1.81.0): restano solo
    le voci il cui nome, la parte prima dei due punti, contiene il testo
    scritto, senza badare a maiuscole e accenti, come il filtro della
    plancia. Invio nel filtro torna alla lista."""

    def __init__(self, genitore, voci, al_cambio):
        from GBwx import STILE_ADATTABILE, adatta_finestra, pannello_scorrevole

        super().__init__(genitore, title="Impostazioni", style=STILE_ADATTABILE)
        self._chiavi = [chiave for chiave, _testo in voci]
        self._testi = dict(voci)
        # Le voci mostrate dalla lista, nel suo ordine: tutte, finche' il
        # filtro e' vuoto.
        self._visibili = list(self._chiavi)
        # La voce scelta da chi usa la lista: resta anche quando il filtro la
        # nasconde, e ritorna selezionata quando ricompare.
        self._scelta = self._chiavi[0] if self._chiavi else None
        self._al_cambio = al_cambio
        pannello = pannello_scorrevole(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # L'ordine di creazione e' quello del Tab, e Windows da' a un
        # controllo il nome del testo creato subito prima: il filtro, poi le
        # istruzioni, che sono il nome della lista, poi la lista. Il sizer
        # mette comunque le istruzioni in cima.
        etichetta_del_filtro = wx.StaticText(pannello, label="Filtro delle voci:")
        self.filtro = wx.TextCtrl(pannello)
        self.filtro.SetName("Filtro delle voci")
        etichetta = wx.StaticText(pannello, label="Impostazioni. Invio cambia la voce, Esc chiude, Maiuscolo con Tab va al filtro.")
        self.lista = wx.ListBox(pannello, choices=[testo for _chiave, testo in voci], style=wx.LB_SINGLE)
        self.lista.SetName("Impostazioni")
        # Almeno tante righe quante sono le voci, misurate sul carattere.
        self.lista.SetMinSize(wx.Size(-1, self.lista.GetCharHeight() * (len(voci) + 2)))
        chiudi = wx.Button(pannello, wx.ID_CANCEL, "Chiudi")
        sizer.Add(etichetta, 0, wx.ALL, 5)
        riga_del_filtro = wx.BoxSizer(wx.HORIZONTAL)
        riga_del_filtro.Add(etichetta_del_filtro, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        riga_del_filtro.Add(self.filtro, 1)
        sizer.Add(riga_del_filtro, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        sizer.Add(self.lista, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        sizer.Add(chiudi, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        pannello.SetSizer(sizer)
        adatta_finestra(self, pannello, (560, 420))
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.lista.Bind(wx.EVT_LISTBOX_DCLICK, lambda _evento: self._cambia())
        self.lista.Bind(wx.EVT_LISTBOX, lambda _evento: self._ricorda_la_scelta())
        self.filtro.Bind(wx.EVT_TEXT, lambda _evento: self._filtra())
        if voci:
            self.lista.SetSelection(0)
        self.lista.SetFocus()

    def _tasto(self, evento):
        if evento.GetEventObject() is self.lista and _premuto_invio(evento):
            self._cambia()
            return
        if evento.GetEventObject() is self.filtro and _premuto_invio(evento):
            self.lista.SetFocus()
            return
        evento.Skip()

    def _ricorda_la_scelta(self):
        """La selezione l'ha mossa chi usa la lista, con le frecce, le
        lettere o il mouse: la voce si ricorda. SetSelection, su Windows,
        non arriva qui."""
        indice = self.lista.GetSelection()
        if 0 <= indice < len(self._visibili):
            self._scelta = self._visibili[indice]

    def _filtra(self):
        """Il testo del filtro e' cambiato: la lista mostra le voci il cui
        nome lo contiene, con selezionata la voce scelta, se c'e', altrimenti
        la prima, che pero' non diventa la scelta: un errore di battitura
        non fa perdere il posto. Senza voci, una riga lo dice: una lista
        vuota, per NVDA, non dice niente."""
        scritto = " ".join(self.filtro.GetValue().split())
        cercato = normale(scritto)
        self._visibili = [chiave for chiave in self._chiavi if cercato in normale(self._testi[chiave].split(": ", 1)[0])]
        if self._visibili:
            self.lista.Set([self._testi[chiave] for chiave in self._visibili])
            self.lista.SetSelection(self._visibili.index(self._scelta) if self._scelta in self._visibili else 0)
        else:
            self.lista.Set([f"Nessuna voce contiene {scritto}."])
            self.lista.SetSelection(0)

    def _cambia(self):
        indice = self.lista.GetSelection()
        if 0 <= indice < len(self._visibili):
            self._scelta = self._visibili[indice]
            self._al_cambio(self._scelta, self)

    def aggiorna(self, chiave, testo):
        """Riscrive la riga della voce senza spostare la selezione; una voce
        nascosta dal filtro ha il testo nuovo quando ricompare."""
        if chiave not in self._testi:
            return
        self._testi[chiave] = testo
        if chiave not in self._visibili:
            return
        indice = self._visibili.index(chiave)
        if self.lista.GetString(indice) == testo:
            return
        selezionata = self.lista.GetSelection()
        self.lista.SetString(indice, testo)
        if selezionata != wx.NOT_FOUND and self.lista.GetSelection() != selezionata:
            self.lista.SetSelection(selezionata)


class FinestraScelta(wx.Dialog):
    """Una scelta da una lista: voci sono le righe, scelta l'indice di
    partenza. Invio o Conferma confermano, Esc o Annulla annullano; la riga
    scelta la dice GetSelection."""

    def __init__(self, genitore, titolo, voci, scelta=0):
        from GBwx import STILE_ADATTABILE, adatta_finestra, pannello_scorrevole

        super().__init__(genitore, title=titolo, style=STILE_ADATTABILE)
        pannello = pannello_scorrevole(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        etichetta = wx.StaticText(pannello, label=f"{titolo}. Invio conferma, Esc annulla.")
        self.lista = wx.ListBox(pannello, choices=list(voci), style=wx.LB_SINGLE)
        self.lista.SetName(titolo)
        self.lista.SetMinSize(wx.Size(-1, self.lista.GetCharHeight() * (min(len(voci), 16) + 2)))
        pulsanti = wx.StdDialogButtonSizer()
        conferma = wx.Button(pannello, wx.ID_OK, "Conferma")
        conferma.SetDefault()
        pulsanti.AddButton(conferma)
        pulsanti.AddButton(wx.Button(pannello, wx.ID_CANCEL, "Annulla"))
        pulsanti.Realize()
        sizer.Add(etichetta, 0, wx.ALL, 5)
        sizer.Add(self.lista, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        sizer.Add(pulsanti, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        pannello.SetSizer(sizer)
        adatta_finestra(self, pannello, (560, 360))
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.lista.Bind(wx.EVT_LISTBOX_DCLICK, lambda _evento: self.EndModal(wx.ID_OK))
        if voci:
            self.lista.SetSelection(max(0, min(scelta, len(voci) - 1)))
        self.lista.SetFocus()

    def _tasto(self, evento):
        if evento.GetEventObject() is self.lista and _premuto_invio(evento):
            self.EndModal(wx.ID_OK)
            return
        evento.Skip()

    def GetSelection(self):
        return self.lista.GetSelection()


def riga_del_marcatore(voce, marker):
    """La riga di un marker nella finestra dei marcatori: "cartella\\file\\nome,
    tempo"; senza un percorso conosciuto solo "file\\nome, tempo"; per un
    sottobrano di un SID "file, sottobrano n\\nome, tempo"."""
    # durata_lunga sta nella finestra principale, che importa questo modulo:
    # la si prende qui, quando la finestra e' gia' tutta caricata.
    from finestra import durata_lunga

    percorsi = voce.get("percorsi") or []
    file = percorsi[0] if percorsi else voce.get("file") or ""
    if voce.get("sottobrano"):
        file += f", sottobrano {voce['sottobrano']}"
    return f"{file}\\{marker['nome']}, {durata_lunga(marker['tempo'])}"


class FinestraMarcatori(wx.Dialog):
    """La finestra dei marcatori, piano 5.8.5: tutti i marker in una lista
    piatta a selezione multipla, raggruppati per provenienza come li ordina
    Marcatori.tutti, e i pulsanti Cancella tutto, Esporta selezionati e
    Chiudi. Nella lista valgono i tasti di Windows (Maiuscolo con le frecce
    allarga la selezione, Ctrl con le frecce sposta il fuoco, Ctrl+Spazio
    accende e spegne la riga), piu' tre: la barra rovesciata cerca, Canc
    elimina le righe selezionate, Invio rinomina la riga col fuoco.
    azioni e' un dizionario di funzioni della finestra principale, che fa il
    lavoro vero e dice com'e' andata; le ultime riceventi sono questo
    dialogo, da usare come genitore dei loro dialoghi:
      rinomina(chiave, marker, genitore)
      elimina(scelti, genitore), con scelti una lista di (chiave, marker)
      cancella_tutto(genitore)
      esporta(scelti, genitore)
      suono(evento) e riscontro(evento, testo), per la ricerca.
    Dopo ogni azione la lista si rifa' con rinfresca."""

    def __init__(self, genitore, marcatori, azioni):
        from GBwx import STILE_ADATTABILE, adatta_finestra, pannello_scorrevole

        super().__init__(genitore, title="Marcatori", style=STILE_ADATTABILE)
        self._marcatori = marcatori
        self._azioni = azioni
        self._righe = []
        self._cercato = ""
        pannello = pannello_scorrevole(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        etichetta = wx.StaticText(pannello, label="Marcatori. Barra rovesciata cerca, Invio rinomina, Canc elimina le righe selezionate, Esc chiude.")
        self.lista = wx.ListCtrl(pannello, style=wx.LC_REPORT | wx.LC_NO_HEADER)
        self.lista.SetName("Marcatori")
        self.lista.InsertColumn(0, "Marcatori")
        self.lista.SetMinSize(wx.Size(self.lista.GetCharWidth() * 60, self.lista.GetCharHeight() * 16))
        pulsanti = wx.BoxSizer(wx.HORIZONTAL)
        cancella = wx.Button(pannello, label="Cancella tutto")
        esporta = wx.Button(pannello, label="Esporta selezionati")
        chiudi = wx.Button(pannello, wx.ID_CANCEL, "Chiudi")
        for pulsante in (cancella, esporta, chiudi):
            pulsanti.Add(pulsante, 0, wx.LEFT, 5)
        sizer.Add(etichetta, 0, wx.ALL, 5)
        sizer.Add(self.lista, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        sizer.Add(pulsanti, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        pannello.SetSizer(sizer)
        self.rinfresca()
        adatta_finestra(self, pannello, (720, 480))
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.lista.Bind(wx.EVT_LIST_ITEM_ACTIVATED, lambda _evento: self._rinomina())
        cancella.Bind(wx.EVT_BUTTON, lambda _evento: self._cancella_tutto())
        esporta.Bind(wx.EVT_BUTTON, lambda _evento: self._esporta())
        self.lista.SetFocus()

    # La lista.

    def rinfresca(self):
        """Rifa' le righe dall'archivio. Il fuoco resta sul marker che lo
        aveva, se c'e' ancora, altrimenti sulla riga che ha preso il suo
        posto, la piu' vicina; restano selezionati i marker che lo erano,
        e se non ne resta nessuno la riga col fuoco."""
        fuoco = self.lista.GetFocusedItem()
        marker_col_fuoco = self._righe[fuoco][2] if 0 <= fuoco < len(self._righe) else None
        # I marker selezionati, tenuti per riferimento: finche' la lista li
        # tiene, i loro id non possono passare ad altri oggetti.
        prima = [self._righe[i][2] for i in self._selezionate() if i < len(self._righe)]
        selezionati = {id(m) for m in prima}
        vecchie = self._righe
        self._righe = self._marcatori.tutti()
        self.lista.DeleteAllItems()
        if not self._righe:
            self.lista.InsertItem(0, NESSUN_MARCATORE)
        for i, (_k, voce, marker) in enumerate(self._righe):
            self.lista.InsertItem(i, riga_del_marcatore(voce, marker))
        self.lista.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        nuovo = next((i for i, (_k, _v, m) in enumerate(self._righe) if m is marker_col_fuoco), None)
        if nuovo is None:
            # Il marker col fuoco non c'e' piu': il fuoco va sulla prima riga
            # rimasta dopo di lui, il cui indice e' quante righe rimaste
            # stavano prima di lui. L'indice vecchio non basta: dopo un blocco
            # eliminato col fuoco in fondo saltava le righe che lo seguivano.
            # vecchie tiene i marker di prima, quindi i loro id restano loro.
            presenti = {id(m) for _k, _v, m in self._righe}
            nuovo = sum(1 for _k, _v, m in vecchie[:max(fuoco, 0)] if id(m) in presenti)
            nuovo = max(0, min(nuovo, self.lista.GetItemCount() - 1))
        rimasti = [i for i, (_k, _v, m) in enumerate(self._righe) if id(m) in selezionati]
        for i in rimasti or [nuovo]:
            self.lista.Select(i)
        self.lista.Focus(nuovo)
        self.lista.EnsureVisible(nuovo)

    def _selezionate(self):
        indice = self.lista.GetFirstSelected()
        while indice != -1:
            yield indice
            indice = self.lista.GetNextSelected(indice)

    def scelti(self):
        """I marker delle righe selezionate, come (chiave, marker)."""
        return [(self._righe[i][0], self._righe[i][2]) for i in self._selezionate() if i < len(self._righe)]

    def _col_fuoco(self):
        """(chiave, marker) della riga col fuoco, o None."""
        fuoco = self.lista.GetFocusedItem()
        return (self._righe[fuoco][0], self._righe[fuoco][2]) if 0 <= fuoco < len(self._righe) else None

    # I tasti e i pulsanti.

    def _tasto(self, evento):
        if evento.GetEventObject() is self.lista:
            if _premuto_invio(evento):
                self._rinomina()
                return
            if evento.GetKeyCode() == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_NONE:
                self._elimina()
                return
            if evento.GetUnicodeKey() == ord("\\") and evento.GetModifiers() == wx.MOD_NONE:
                self._cerca()
                return
        evento.Skip()

    def _niente(self):
        self._azioni["riscontro"]("non_disponibile", "Non ci sono marcatori.")

    def _rinomina(self):
        scelta = self._col_fuoco()
        if scelta is None:
            self._niente()
            return
        self._azioni["rinomina"](*scelta, self)
        self.rinfresca()

    def _elimina(self):
        scelti = self.scelti()
        if not scelti:
            if self._righe:
                self._azioni["riscontro"]("non_disponibile", "Nessuna riga selezionata: Canc elimina le righe selezionate.")
            else:
                self._niente()
            return
        self._azioni["elimina"](scelti, self)
        self.rinfresca()

    def _cancella_tutto(self):
        if not self._righe:
            self._niente()
            return
        self._azioni["cancella_tutto"](self)
        self.rinfresca()

    def _esporta(self):
        scelti = self.scelti()
        if not scelti:
            if self._righe:
                self._azioni["riscontro"]("non_disponibile", "Nessuna riga selezionata: seleziona i marcatori da esportare.")
            else:
                self._niente()
            return
        self._azioni["esporta"](scelti, self)
        self.rinfresca()

    def _cerca(self):
        """La barra rovesciata: chiede un testo e porta fuoco e selezione
        sulla riga seguente che lo contiene, maiuscole indifferenti; arrivata
        in fondo riparte dalla cima."""
        if not self._righe:
            self._niente()
            return
        self._azioni["suono"]("domanda")
        with DialogoTesto(self, "Testo da cercare nei marcatori:", "Cerca nei marcatori", self._cercato) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._azioni["riscontro"]("annullamento", "Ricerca nei marcatori annullata.")
                return
            testo = " ".join(dialogo.GetValue().split())
        if not testo:
            self._azioni["riscontro"]("annullamento", "Ricerca nei marcatori annullata: il testo è vuoto.")
            return
        self._cercato = testo
        cercato = testo.casefold()
        righe = [self.lista.GetItemText(i).casefold() for i in range(self.lista.GetItemCount())]
        fuoco = max(self.lista.GetFocusedItem(), -1)
        trovata = next((i for i in range(fuoco + 1, len(righe)) if cercato in righe[i]), None)
        ripartita = trovata is None
        if ripartita:
            trovata = next((i for i in range(fuoco + 1) if cercato in righe[i]), None)
        if trovata is None:
            self._azioni["riscontro"]("non_trovato_nei_marcatori", f"Nei marcatori non c'è {testo}.")
            return
        for i in list(self._selezionate()):
            self.lista.Select(i, False)
        self.lista.Select(trovata)
        self.lista.Focus(trovata)
        self.lista.EnsureVisible(trovata)
        self._azioni["suono"]("ripartito_nei_marcatori" if ripartita else "trovato_nei_marcatori")

