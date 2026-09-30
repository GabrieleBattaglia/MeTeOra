# MeTeOra, la finestra principale: plancia dei comandi, console e cruscotto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.2.0 i sottobrani dei SID, nella 1.3.0 il loop A-B, nella 1.4.0 il cestino,
# nella 1.5.0 le cartelle suonate con le sottocartelle, nella 1.6.0 i Preferiti, nella 1.7.0 conti e durate delle playlist.

"""La finestra di MeTeOra.

Tre aree, nell'ordine di tabulazione: la plancia dei comandi (F5), un albero;
la console (F6), dove scorrono i riscontri di ogni azione; il cruscotto
(F7), che mostra i tasti del contesto da cui ci si e' arrivati.
I tasti a lettera valgono in tutta la finestra e li intercetta EVT_CHAR_HOOK,
prima dei controlli: per questo l'albero non ha la ricerca per iniziale.
Il brano in riproduzione e la voce selezionata sono due cose distinte: la
riproduzione non sposta mai la selezione; lo fa F8, su richiesta.
"""

import contextlib
import os

import wx

import formati
import percorsi
import questo_pc
import songlengths
import suoni
import version
from impostazioni import Impostazioni
from motore import durata_del_sottobrano
from playlist import Archivio, Brano, Coda, Playlist
from schedario import Schedario

FILE_PLAYLIST = "MeTeOra - Playlist.json"
FILE_IMPOSTAZIONI = "MeTeOra - Impostazioni.json"
FILE_SCHEDARIO = "MeTeOra - Schedario.json"
RIGHE_DELLA_CONSOLE = 2000

# I tasti a lettera: (carattere, maiuscolo) -> comando.
TASTI = {
    ("z", False): "precedente",
    ("x", False): "play",
    ("x", True): "loop",
    ("z", True): "sottobrano_precedente",
    ("b", True): "sottobrano_successivo",
    ("c", False): "pausa",
    ("v", False): "stop",
    ("b", False): "successivo",
    ("n", False): "casuale",
    ("m", False): "muto",
    ("q", False): "indietro",
    ("e", False): "avanti",
    ("q", True): "passo_indietro",
    ("e", True): "passo_avanti",
    ("w", False): "vai_a_tempo",
    ("+", False): "volume_su",
    ("-", False): "volume_giu",
    ("m", True): "passo_volume",
}
# I tasti gia' assegnati nel piano a funzioni delle tappe successive: per ora
# dicono di non essere ancora disponibili.
FUTURI = {
    "a": "velocità", "s": "velocità", "d": "velocità", "f": "tono", "g": "tono", "h": "tono",
    "j": "playlist precedente", "k": "playlist successiva", "l": "dissolvenza",
    "r": "segnalibri", "t": "segnalibri", "y": "segnalibri",
    "u": "equalizzatore", "i": "equalizzatore", "o": "equalizzatore", "p": "equalizzatore", "è": "equalizzatore",
    "'": "playlist precedente", "ì": "playlist successiva", "\\": "ricerca nella plancia",
    **{str(n): "scelta della playlist" for n in range(10)},
}
FUTURI_MAIUSCOLI = {"l": "durata della dissolvenza"}

TASTI_COMUNI = [
    "X riproduce la voce selezionata o riprende, C pausa, V stop, Z e B brano precedente e successivo, N brano a caso.",
    "Q ed E indietro e avanti nel brano, Maiuscolo con Q ed E ne cambiano i secondi, W va a un tempo, + e - volume, Maiuscolo+M il passo del volume, M muto.",
    "Maiuscolo con Z e con B sottobrano precedente e successivo di un SID, Maiuscolo+X mette e toglie i punti A e B del loop sul brano selezionato.",
    "F4 mette nei Preferiti il brano selezionato. F5 plancia, F6 console, F7 cruscotto, F8 porta la selezione sul brano in riproduzione, F9 dice cosa suona.",
    "F1 manuale, F2 novità, F3 crediti, Esc esce salvando tutto.",
]
# Le righe del cruscotto proprie di ogni tipo di voce della plancia.
TASTI_DEL_CONTESTO = {
    "preferiti": ("i Preferiti", "Invio, Applicazioni o Spazio: menu con Riproduci. Canc su un loro brano lo toglie dai Preferiti."),
    "radice_playlist": ("il ramo Playlist", "Invio, Applicazioni o Spazio: menu con Nuova playlist."),
    "playlist": ("una playlist", "Invio, Applicazioni o Spazio: menu con Riproduci e Rinomina. Canc elimina la playlist, dopo una conferma."),
    "brano": ("un brano di una playlist", "Invio, Applicazioni o Spazio: menu con Riproduci, Sposta e Saltato. Canc toglie il brano dalla playlist, Maiuscolo+Canc manda il file nel cestino. Un SID con più sottobrani si apre con freccia destra."),
    "pc": ("Questo PC", "Freccia destra mostra le unità. Invio, Applicazioni o Spazio: menu con Aggiorna."),
    "unita": ("un'unità", "Freccia destra mostra il contenuto. Invio, Applicazioni o Spazio: menu con Crea playlist da qui."),
    "cartella": ("una cartella", "Freccia destra mostra il contenuto. Invio, Applicazioni o Spazio: menu con Riproduci e Crea playlist da qui."),
    "file": ("un file", "Invio, Applicazioni o Spazio: menu con Riproduci e Aggiungi alla playlist. Maiuscolo+Canc manda il file nel cestino. Un SID con più sottobrani si apre con freccia destra."),
    "sottobrano": ("un sottobrano di un SID", "Invio, Applicazioni o Spazio: menu con Riproduci e Aggiungi alla playlist."),
    "comando": ("un comando", "Invio esegue il comando."),
}


def tempo(secondi):
    """m:ss, oppure h:mm:ss oltre l'ora."""
    if secondi is None:
        return "?"
    secondi = max(0, int(secondi))
    ore, resto = divmod(secondi, 3600)
    minuti, secondi = divmod(resto, 60)
    return f"{ore}:{minuti:02d}:{secondi:02d}" if ore else f"{minuti}:{secondi:02d}"


def leggi_tempo(testo):
    """Da '90', '1.5', '1:30', '1:30,25' o '1:02:03' a secondi; None se non si
    capisce. I due punti separano ore, minuti e secondi; il punto o la
    virgola separano i decimali, solo nell'ultima parte."""
    parti = testo.strip().replace(",", ".").split(":")
    try:
        numeri = [int(p) for p in parti[:-1]] + [float(parti[-1])]
    except ValueError:
        return None
    if not 1 <= len(numeri) <= 3 or any(n < 0 for n in numeri) or any(n >= 60 for n in numeri[1:]):
        return None
    totale = 0.0
    for n in numeri:
        totale = totale * 60 + n
    return totale


def secondi_da_leggere(secondi):
    """Un numero di secondi come si legge in italiano: 10, oppure 1,5."""
    testo = f"{secondi:.3f}".rstrip("0").rstrip(".")
    return testo.replace(".", ",")


def durata_lunga(secondi):
    """Una durata come ore:minuti:secondi.millesimi, con le ore solo se ci
    sono e i millesimi solo se non sono zero: 1:02:03.456, 4:05, 0:07.250."""
    millesimi = round(secondi * 1000)
    ore, resto = divmod(millesimi, 3600000)
    minuti, resto = divmod(resto, 60000)
    secondi, millesimi = divmod(resto, 1000)
    testo = f"{ore}:{minuti:02d}:{secondi:02d}" if ore else f"{minuti}:{secondi:02d}"
    return testo + (f".{millesimi:03d}" if millesimi else "")


def brani_al_plurale(n):
    return "1 brano" if n == 1 else f"{n} brani"


class FinestraTesto(wx.Dialog):
    """Una grande area di testo da leggere: manuale, novita', crediti. Esc chiude."""

    def __init__(self, genitore, titolo, testo):
        from GBwx import STILE_ADATTABILE, adatta_finestra, pannello_scorrevole

        super().__init__(genitore, title=titolo, style=STILE_ADATTABILE)
        pannello = pannello_scorrevole(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        etichetta = wx.StaticText(pannello, label=titolo)
        self.testo = wx.TextCtrl(pannello, value=testo, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.testo.SetName(titolo)
        chiudi = wx.Button(pannello, wx.ID_CANCEL, "Chiudi")
        sizer.Add(etichetta, 0, wx.ALL, 5)
        sizer.Add(self.testo, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        sizer.Add(chiudi, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        pannello.SetSizer(sizer)
        adatta_finestra(self, pannello, (700, 500))
        self.SetEscapeId(wx.ID_CANCEL)
        self.Maximize()
        self.testo.SetInsertionPoint(0)
        self.testo.SetFocus()


class Finestra(wx.Frame):
    def __init__(self, ao="wasapi", cartella_dati=None):
        super().__init__(None, title=f"MeTeOra {version.VERSION}")
        cartella_dati = cartella_dati or percorsi.cartella_programma()
        self.impostazioni = Impostazioni(os.path.join(cartella_dati, FILE_IMPOSTAZIONI))
        self.impostazioni.carica()
        self.archivio = Archivio(os.path.join(cartella_dati, FILE_PLAYLIST))
        errore_archivio = None
        try:
            self.archivio.carica()
        except (OSError, ValueError, KeyError) as e:
            errore_archivio = e
        from motore import Motore

        self.motore = Motore(alla_fine=lambda: wx.CallAfter(self._brano_finito),
            all_errore=lambda p: wx.CallAfter(self._brano_in_errore, p), ao=ao, volume=self.impostazioni["volume"])
        self.coda = Coda()
        self.schedario = Schedario(os.path.join(cartella_dati, FILE_SCHEDARIO), avvisa=lambda: wx.CallAfter(self._schede_arrivate))
        self.schedario.carica()
        # Le playlist temporanee nate dalle cartelle di Questo PC, per cartella:
        # rigiocando un file della stessa cartella si riusa la stessa.
        self._temporanee = {}
        self._area_precedente = None
        self._posizione_della_console = None
        self._righe = []
        self._chiusa = False
        self._costruisci()
        self._popola_albero()
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.Bind(wx.EVT_CLOSE, self._alla_chiusura)
        self.scrivi(f"MeTeOra {version.VERSION} del {version.DATE}. Pronto: F1 apre il manuale, F7 apre il cruscotto con i tasti del punto in cui ti trovi.")
        if errore_archivio:
            self.scrivi(f"Il file delle playlist non si legge, e parto senza playlist: {errore_archivio}")
            # Il file illeggibile non va sovrascritto alla prima modifica.
            self.archivio.percorso += ".nuovo"
        self._chiedi_schede(*self.archivio.playlist, self.archivio.preferiti)

    # La costruzione.

    def _costruisci(self):
        pannello = wx.Panel(self)
        sopra = wx.BoxSizer(wx.HORIZONTAL)
        colonna_sinistra = wx.BoxSizer(wx.VERTICAL)
        colonna_sinistra.Add(wx.StaticText(pannello, label="Plancia dei comandi"), 0, wx.ALL, 2)
        self.albero = wx.TreeCtrl(pannello, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        self.albero.SetName("Plancia dei comandi")
        colonna_sinistra.Add(self.albero, 1, wx.EXPAND)
        colonna_destra = wx.BoxSizer(wx.VERTICAL)
        colonna_destra.Add(wx.StaticText(pannello, label="Console"), 0, wx.ALL, 2)
        self.console = wx.TextCtrl(pannello, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.console.SetName("Console")
        colonna_destra.Add(self.console, 1, wx.EXPAND)
        sopra.Add(colonna_sinistra, 1, wx.EXPAND | wx.ALL, 4)
        sopra.Add(colonna_destra, 1, wx.EXPAND | wx.ALL, 4)
        tutto = wx.BoxSizer(wx.VERTICAL)
        tutto.Add(sopra, 1, wx.EXPAND)
        tutto.Add(wx.StaticText(pannello, label="Cruscotto"), 0, wx.LEFT | wx.RIGHT, 6)
        self.cruscotto = wx.TextCtrl(pannello, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.cruscotto.SetName("Cruscotto")
        # Almeno cinque righe, misurate sul carattere e non in pixel.
        self.cruscotto.SetMinSize(wx.Size(-1, self.cruscotto.GetCharHeight() * 6 + 8))
        tutto.Add(self.cruscotto, 0, wx.EXPAND | wx.ALL, 4)
        pannello.SetSizer(tutto)
        self.albero.Bind(wx.EVT_TREE_ITEM_EXPANDING, self._in_espansione)
        self.albero.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._invio)
        self.albero.Bind(wx.EVT_TREE_ITEM_MENU, self._menu_da_evento)
        self.albero.Bind(wx.EVT_KEY_DOWN, self._tasto_nell_albero)
        self.albero.Bind(wx.EVT_SET_FOCUS, self._fuoco_all_albero)
        self.console.Bind(wx.EVT_SET_FOCUS, self._fuoco_alla_console)
        self.console.Bind(wx.EVT_KILL_FOCUS, self._console_lasciata)
        self.cruscotto.Bind(wx.EVT_SET_FOCUS, self._fuoco_al_cruscotto)

    def _popola_albero(self):
        radice = self.albero.AddRoot("MeTeOra")
        self.nodo_preferiti = self.albero.AppendItem(radice, "Preferiti", data={"tipo": "playlist", "playlist": self.archivio.preferiti, "caricato": False})
        self.nodo_playlist = self.albero.AppendItem(radice, "Playlist", data={"tipo": "radice_playlist"})
        self.nodo_pc = self.albero.AppendItem(radice, "Questo PC", data={"tipo": "pc", "caricato": False})
        self.albero.SetItemHasChildren(self.nodo_pc, True)
        self.albero.AppendItem(radice, "Apri file", data={"tipo": "comando", "comando": "apri_file"})
        self.albero.AppendItem(radice, "Impostazioni", data={"tipo": "comando", "comando": "impostazioni"})
        self._popola_playlist()
        self.albero.SelectItem(self.nodo_preferiti)

    # La console.

    def scrivi(self, testo):
        """Aggiunge una riga in fondo alla console senza spostarne il
        cursore, e tiene le ultime RIGHE_DELLA_CONSOLE righe."""
        posizione = self.console.GetInsertionPoint()
        self.console.AppendText(("\n" if self._righe else "") + testo)
        self._righe.append(testo)
        if len(self._righe) > RIGHE_DELLA_CONSOLE + 100:
            togliere = len(self._righe) - RIGHE_DELLA_CONSOLE
            caratteri = sum(len(r) for r in self._righe[:togliere]) + togliere
            self.console.Remove(0, caratteri)
            del self._righe[:togliere]
            posizione = max(0, posizione - caratteri)
            if self._posizione_della_console is not None:
                self._posizione_della_console = max(0, self._posizione_della_console - caratteri)
        self.console.SetInsertionPoint(posizione)

    def _suono(self, evento):
        suoni.suona(evento, self.impostazioni["volume_effetti"])

    def _riscontro(self, evento, testo):
        self._suono(evento)
        self.scrivi(testo)

    # Il fuoco e il cruscotto.

    def _fuoco_all_albero(self, evento):
        evento.Skip()
        self._area_precedente = "albero"

    def _fuoco_alla_console(self, evento):
        evento.Skip()
        self._area_precedente = "console"
        if self._posizione_della_console is not None:
            wx.CallAfter(self._rimetti_posizione_della_console, self._posizione_della_console)

    def _rimetti_posizione_della_console(self, posizione):
        if self and self.console:
            self.console.SetInsertionPoint(min(posizione, self.console.GetLastPosition()))

    def _console_lasciata(self, evento):
        evento.Skip()
        self._posizione_della_console = self.console.GetInsertionPoint()

    def _fuoco_al_cruscotto(self, evento):
        evento.Skip()
        self._rinfresca_cruscotto()

    def _rinfresca_cruscotto(self):
        """Riscrive il cruscotto solo se il testo cambia: tornando dallo stesso
        punto il cursore resta dove era."""
        testo = "\n".join(self.righe_del_cruscotto())
        attuale = self.cruscotto.GetValue().replace("\r\n", "\n").replace("\r", "\n")
        if attuale != testo:
            self.cruscotto.SetValue(testo)
            self.cruscotto.SetInsertionPoint(0)

    def righe_del_cruscotto(self):
        """Le righe del cruscotto per l'area da cui si arriva."""
        if self._area_precedente == "console":
            righe = ["Tasti per la console.", "Frecce, Pagina su e giù, Home e Fine per leggere; i messaggi nuovi arrivano in fondo."]
        else:
            dati = self._dati(self.albero.GetSelection()) or {}
            tipo = "preferiti" if dati.get("tipo") == "playlist" and dati["playlist"] is self.archivio.preferiti else dati.get("tipo")
            nome, riga = TASTI_DEL_CONTESTO.get(tipo, ("la plancia", ""))
            righe = [f"Tasti per {nome}."] + ([riga] if riga else [])
        return righe + TASTI_COMUNI

    def _vai(self, controllo, evento):
        self._suono(evento)
        if controllo is self.cruscotto and self.cruscotto.HasFocus():
            self._rinfresca_cruscotto()
        controllo.SetFocus()

    # I tasti.

    def _tasto(self, evento):
        codice = evento.GetKeyCode()
        modificatori = evento.GetModifiers()
        tasti_funzione = {
            wx.WXK_F1: self._manuale, wx.WXK_F2: self._changelog, wx.WXK_F3: self._crediti,
            wx.WXK_F5: lambda: self._vai(self.albero, "plancia"), wx.WXK_F6: lambda: self._vai(self.console, "console"),
            wx.WXK_F7: lambda: self._vai(self.cruscotto, "cruscotto"), wx.WXK_F4: lambda: self._ai_preferiti(self._preferito_selezionato()), wx.WXK_F8: self._vai_al_brano, wx.WXK_F9: self._informazioni,
            wx.WXK_ESCAPE: self.Close,
        }
        if modificatori == wx.MOD_NONE and codice in tasti_funzione:
            tasti_funzione[codice]()
            return
        # Il tastierino numerico resta a NVDA, e Ctrl e Alt ai comandi di Windows.
        if modificatori not in (wx.MOD_NONE, wx.MOD_SHIFT) or wx.WXK_NUMPAD0 <= codice <= wx.WXK_NUMPAD_DIVIDE:
            evento.Skip()
            return
        unicode = evento.GetUnicodeKey()
        if unicode == wx.WXK_NONE or unicode <= 32:
            evento.Skip()
            return
        carattere = chr(unicode).lower()
        maiuscolo = modificatori == wx.MOD_SHIFT
        comando = TASTI.get((carattere, maiuscolo))
        if comando:
            getattr(self, f"_comando_{comando}")()
            return
        futuro = FUTURI_MAIUSCOLI.get(carattere) if maiuscolo else FUTURI.get(carattere)
        if futuro:
            self._riscontro("non_disponibile", f"Il tasto {chr(unicode)} sarà per: {futuro}. Non ancora disponibile.")
            return
        evento.Skip()

    def _tasto_nell_albero(self, evento):
        codice = evento.GetKeyCode()
        if codice == wx.WXK_SPACE and evento.GetModifiers() == wx.MOD_NONE:
            self._menu(self.albero.GetSelection())
        elif codice == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_NONE:
            self._cancella(self.albero.GetSelection())
        elif codice == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_SHIFT:
            self._al_cestino(self.albero.GetSelection())
        else:
            evento.Skip()

    # L'albero.

    def _dati(self, voce):
        return self.albero.GetItemData(voce) if voce and voce.IsOk() else None

    def _figli(self, voce):
        figlio, cookie = self.albero.GetFirstChild(voce)
        while figlio.IsOk():
            yield figlio
            figlio, cookie = self.albero.GetNextChild(voce, cookie)

    def _tutte_le_voci(self, voce=None):
        for figlio in self._figli(voce or self.albero.GetRootItem()):
            yield figlio
            yield from self._tutte_le_voci(figlio)

    def _ha_sottobrani(self, brano):
        """Vero per un SID con piu' sottobrani, che nella plancia diventa un ramo."""
        if brano.sottobrano is not None or not formati.e_sid(brano.percorso):
            return False
        info = songlengths.info_del_sid(brano.percorso)
        return bool(info) and info["sottobrani"] > 1

    def _etichetta(self, dati):
        """L'etichetta di un brano, di un file o di un sottobrano, con le sue indicazioni."""
        brano = dati["brano"]
        suona = bool(self.motore.in_corso) and brano is self.coda.corrente
        if dati["tipo"] == "sottobrano":
            n = dati["numero"]
            parti = [f"Sottobrano {n} di {dati['totale']}, {tempo(durata_del_sottobrano(brano.percorso, n))}"]
            if suona and self.motore.sottobrano == n:
                parti.append("in riproduzione")
            return ", ".join(parti)
        parti = [brano.nome_del_file]
        if brano.sottobrano:
            info = songlengths.info_del_sid(brano.percorso)
            parti[0] += f", sottobrano {brano.sottobrano} di {info['sottobrani'] if info else '?'}"
        if brano.saltato:
            parti.append("saltato")
        if self.coda.loop_playlist is dati["playlist"]:
            if brano is self.coda.punto_a:
                parti.append("punto A del loop")
            if brano is self.coda.punto_b:
                parti.append("punto B del loop")
        if suona:
            parti.append("in riproduzione")
        return ", ".join(parti)

    def _aggiungi_voce(self, genitore, tipo, pl, brano):
        """Aggiunge alla plancia un brano (di una playlist) o un file (di una
        cartella); un SID con piu' sottobrani diventa un ramo da aprire."""
        dati = {"tipo": tipo, "playlist": pl, "brano": brano}
        voce = self.albero.AppendItem(genitore, self._etichetta(dati), data=dati)
        if self._ha_sottobrani(brano):
            dati["caricato"] = False
            self.albero.SetItemHasChildren(voce, True)
        return voce

    def _aggiorna_etichette(self):
        """Rinfresca le etichette di brani, file e sottobrani: saltato, loop, in riproduzione."""
        for voce in self._tutte_le_voci():
            dati = self._dati(voce)
            if not dati or dati["tipo"] not in ("brano", "file", "sottobrano"):
                continue
            nuova = self._etichetta(dati)
            if self.albero.GetItemText(voce) != nuova:
                self.albero.SetItemText(voce, nuova)

    def _ammesso(self, pl, brano):
        """Vero se il brano passa il filtro della sua playlist."""
        return True

    def _conto(self, brani):
        """'numero (durata)' di una lista di brani; i brani di cui la durata
        non si sa ancora, o non si sapra', sono detti a parte."""
        if not brani:
            return "0"
        durate = [self.schedario.durata(b) for b in brani]
        note = [d for d in durate if d is not None]
        if not note:
            return f"{len(brani)} (senza durata)"
        ignote = len(durate) - len(note)
        return f"{len(brani)} ({durata_lunga(sum(note))}{f', {ignote} senza durata' if ignote else ''})"

    def _etichetta_della_playlist(self, pl):
        filtrati = [b for b in pl.brani if self._ammesso(pl, b)]
        return f"{pl.nome}, brani: {self._conto(filtrati)}, totali: {self._conto(pl.brani)}"

    def _chiedi_schede(self, *playlist):
        """Chiede allo schedario le schede dei brani delle playlist date."""
        self.schedario.chiedi([b.percorso for pl in playlist for b in pl.brani])

    def _schede_arrivate(self):
        """Lo schedario ha letto nuove schede: si rinfrescano le etichette
        delle playlist e, a coda vuota, lo schedario si salva."""
        if self._chiusa:
            return
        for voce in [self.nodo_preferiti, *self._figli(self.nodo_playlist)]:
            dati = self._dati(voce) or {}
            if dati.get("tipo") == "playlist":
                nuova = self._etichetta_della_playlist(dati["playlist"])
                if self.albero.GetItemText(voce) != nuova:
                    self.albero.SetItemText(voce, nuova)
        if not self.schedario.in_attesa():
            try:
                self.schedario.salva()
            except OSError as e:
                self._riscontro("errore", f"Non riesco a salvare lo schedario: {e}")

    def _sotto(self, voce, radice):
        """Vero se la voce sta dentro il ramo radice."""
        while voce.IsOk():
            if voce == radice:
                return True
            voce = self.albero.GetItemParent(voce)
        return False

    def _popola_playlist(self, seleziona=None):
        """Ricostruisce il ramo Playlist dall'archivio. Tiene aperte le
        playlist che lo erano, e se la selezione stava nel ramo la rimette
        sulla stessa voce, o su seleziona quando e' dato (una playlist o un
        brano). I brani di una playlist si caricano quando la si apre."""
        aperte = set()
        selezionato = None
        voce_selezionata = self.albero.GetSelection()
        dentro = False
        for voce in self._figli(self.nodo_playlist):
            dati = self._dati(voce)
            if dati.get("tipo") == "playlist" and self.albero.IsExpanded(voce):
                aperte.add(id(dati["playlist"]))
        preferiti_aperti = self.albero.IsExpanded(self.nodo_preferiti)
        if voce_selezionata.IsOk() and self._sotto(voce_selezionata, self.nodo_preferiti):
            dati = self._dati(voce_selezionata) or {}
            dentro = True
            selezionato = dati.get("brano") or dati.get("playlist")
        elif voce_selezionata.IsOk() and voce_selezionata != self.nodo_playlist and self._sotto(voce_selezionata, self.nodo_playlist):
            dati = self._dati(voce_selezionata) or {}
            dentro = True
            selezionato = "nuova_playlist" if dati.get("comando") == "nuova_playlist" else (dati.get("brano") or dati.get("playlist"))
        if seleziona is not None:
            selezionato, dentro = seleziona, True
        if dentro:
            # La selezione passa sul ramo mentre i figli spariscono, senza
            # rimbalzi su voci che stanno per essere cancellate.
            self.albero.SelectItem(self.nodo_playlist)
        preferiti = self.archivio.preferiti
        self.albero.SetItemText(self.nodo_preferiti, self._etichetta_della_playlist(preferiti))
        self.albero.DeleteChildren(self.nodo_preferiti)
        self._dati(self.nodo_preferiti)["caricato"] = False
        self.albero.SetItemHasChildren(self.nodo_preferiti, bool(preferiti.brani))
        da_selezionare = None
        if selezionato is preferiti:
            da_selezionare = self.nodo_preferiti
        if preferiti_aperti or (isinstance(selezionato, Brano) and preferiti.indice(selezionato) is not None):
            self.albero.Expand(self.nodo_preferiti)
            if isinstance(selezionato, Brano):
                da_selezionare = next((v for v in self._figli(self.nodo_preferiti) if self._dati(v)["brano"] is selezionato), da_selezionare)
        self.albero.DeleteChildren(self.nodo_playlist)
        for pl in self.archivio.playlist:
            nodo = self.albero.AppendItem(self.nodo_playlist, self._etichetta_della_playlist(pl), data={"tipo": "playlist", "playlist": pl, "caricato": False})
            self.albero.SetItemHasChildren(nodo, bool(pl.brani))
            if pl is selezionato:
                da_selezionare = nodo
            elif isinstance(selezionato, Brano) and pl.indice(selezionato) is not None:
                aperte.add(id(pl))
            if id(pl) in aperte:
                self.albero.Expand(nodo)
                if isinstance(selezionato, Brano):
                    da_selezionare = next((v for v in self._figli(nodo) if self._dati(v)["brano"] is selezionato), da_selezionare)
        comando = self.albero.AppendItem(self.nodo_playlist, "Nuova playlist", data={"tipo": "comando", "comando": "nuova_playlist"})
        if selezionato == "nuova_playlist":
            da_selezionare = comando
        if dentro:
            if da_selezionare is None or self._sotto(da_selezionare, self.nodo_playlist):
                self.albero.Expand(self.nodo_playlist)
            self.albero.SelectItem(da_selezionare or self.nodo_playlist)

    def _in_espansione(self, evento):
        voce = evento.GetItem()
        dati = self._dati(voce)
        if dati and dati.get("caricato") is False:
            self._carica(voce, dati)

    def _carica(self, voce, dati):
        """Riempie un ramo quando si apre: le unita' di Questo PC, il contenuto
        di una cartella, i brani di una playlist, i sottobrani di un SID."""
        self.albero.DeleteChildren(voce)
        dati["caricato"] = True
        tipo = dati["tipo"]
        if tipo == "pc":
            for radice, etichetta in questo_pc.unita():
                figlio = self.albero.AppendItem(voce, etichetta, data={"tipo": "unita", "percorso": radice, "etichetta": etichetta, "caricato": False})
                self.albero.SetItemHasChildren(figlio, True)
            return
        if tipo == "playlist":
            for brano in dati["playlist"].brani:
                self._aggiungi_voce(voce, "brano", dati["playlist"], brano)
            return
        if tipo in ("brano", "file"):
            brano = dati["brano"]
            totale = songlengths.info_del_sid(brano.percorso)["sottobrani"]
            for n in range(1, totale + 1):
                figlio = {"tipo": "sottobrano", "playlist": dati["playlist"], "brano": brano, "numero": n, "totale": totale}
                self.albero.AppendItem(voce, self._etichetta(figlio), data=figlio)
            return
        try:
            cartelle, files = questo_pc.contenuto(dati["percorso"])
        except OSError as e:
            self._riscontro("errore", f"Non riesco a leggere {dati['percorso']}: {e.strerror or e}")
            self.albero.SetItemHasChildren(voce, False)
            return
        for cartella in cartelle:
            figlio = self.albero.AppendItem(voce, os.path.basename(cartella), data={"tipo": "cartella", "percorso": cartella, "caricato": False})
            self.albero.SetItemHasChildren(figlio, True)
        pl = self._temporanea(dati["percorso"], files)
        for brano in pl.brani:
            self._aggiungi_voce(voce, "file", pl, brano)
        if not cartelle and not files:
            self.albero.SetItemHasChildren(voce, False)
            self._riscontro("cartella_aperta", "Niente da suonare qui dentro.")
        else:
            self._suono("cartella_aperta")

    def _aggiorna_ramo(self, voce):
        dati = self._dati(voce)
        aperto = self.albero.IsExpanded(voce)
        self.albero.Collapse(voce)
        self.albero.DeleteChildren(voce)
        dati["caricato"] = False
        self.albero.SetItemHasChildren(voce, True)
        if aperto:
            self.albero.Expand(voce)
        self.scrivi("Aggiornato.")

    # Invio, menu contestuale e Canc.

    def _invio(self, evento):
        voce = evento.GetItem()
        dati = self._dati(voce)
        if dati and dati["tipo"] == "comando":
            getattr(self, f"_comando_{dati['comando']}")()
        else:
            self._menu(voce)

    def _menu_da_evento(self, evento):
        self._menu(evento.GetItem())

    def _menu(self, voce):
        dati = self._dati(voce)
        if not dati:
            return
        voci = self._voci_del_menu(dati)
        if not voci:
            return
        menu = wx.Menu()
        self._riempi_menu(menu, voci)
        self._suono("menu")
        rettangolo = self.albero.GetBoundingRect(voce, textOnly=True)
        self.albero.PopupMenu(menu, rettangolo.GetBottomLeft() if rettangolo else wx.DefaultPosition)
        menu.Destroy()

    def _riempi_menu(self, menu, voci):
        """voci: lista di (etichetta, azione) o (etichetta, [sottovoci]);
        un'azione che e' una tupla (funzione, spuntato) fa una voce a spunta."""
        for etichetta, azione in voci:
            if isinstance(azione, list):
                sottomenu = wx.Menu()
                self._riempi_menu(sottomenu, azione)
                menu.AppendSubMenu(sottomenu, etichetta)
            elif isinstance(azione, tuple):
                funzione, spuntato = azione
                voce = menu.AppendCheckItem(wx.ID_ANY, etichetta)
                voce.Check(spuntato)
                menu.Bind(wx.EVT_MENU, lambda _e, f=funzione: f(), voce)
            else:
                voce = menu.Append(wx.ID_ANY, etichetta)
                menu.Bind(wx.EVT_MENU, lambda _e, f=azione: f(), voce)

    def _menu_aggiungi(self, brani_da_aggiungere):
        """Il sottomenu Aggiungi alla playlist: le playlist dell'archivio e una
        nuova. brani_da_aggiungere e' una funzione che da' i brani, chiamata
        solo quando la voce viene scelta."""
        voci = [(pl.nome, lambda pl=pl: self._aggiungi(pl, brani_da_aggiungere())) for pl in self.archivio.playlist]
        voci.append(("Nuova playlist", lambda: self._aggiungi(None, brani_da_aggiungere())))
        return voci

    def _voci_del_menu(self, dati):
        tipo = dati["tipo"]
        if tipo == "radice_playlist":
            return [("Nuova playlist", self._comando_nuova_playlist)]
        if tipo == "playlist" and dati["playlist"] is self.archivio.preferiti:
            return [("Riproduci", lambda: self._riproduci_playlist(self.archivio.preferiti))]
        if tipo == "playlist":
            pl = dati["playlist"]
            return [("Riproduci", lambda: self._riproduci_playlist(pl)), ("Rinomina", lambda: self._rinomina(pl)),
                ("Elimina", lambda: self._elimina_playlist(pl))]
        if tipo == "brano":
            pl, brano = dati["playlist"], dati["brano"]
            return [("Riproduci", lambda: self._riproduci(pl, brano)),
                ("Sposta su", lambda: self._sposta(pl, brano, "su")), ("Sposta giù", lambda: self._sposta(pl, brano, "giu")),
                ("Sposta in cima", lambda: self._sposta(pl, brano, "cima")), ("Sposta in fondo", lambda: self._sposta(pl, brano, "fondo")),
                ("Saltato", (lambda: self._salta(pl, brano), brano.saltato)), ("Togli dalla playlist", lambda: self._togli(pl, brano)),
                ("Aggiungi ai preferiti", lambda: self._ai_preferiti(brano)), ("Manda nel cestino", lambda: self._al_cestino(self.albero.GetSelection()))]
        if tipo == "pc":
            return [("Aggiorna", lambda: self._aggiorna_ramo(self.nodo_pc))]
        if tipo in ("unita", "cartella"):
            voce = self.albero.GetSelection()
            cartella = dati["percorso"]
            nome = dati.get("etichetta", "").split("\\", 1)[-1] if tipo == "unita" else os.path.basename(cartella)
            return [("Riproduci", lambda: self._riproduci_cartella(cartella)), ("Crea playlist da qui", lambda: self._crea_da_qui(cartella, nome)),
                ("Aggiungi alla playlist", self._menu_aggiungi(lambda: [Brano(p) for p in questo_pc.file_ricorsivi(cartella)])), ("Aggiorna", lambda: self._aggiorna_ramo(voce))]
        if tipo == "file":
            pl, brano = dati["playlist"], dati["brano"]
            return [("Riproduci", lambda: self._riproduci(pl, brano)), ("Aggiungi alla playlist", self._menu_aggiungi(lambda: [Brano(brano.percorso)])),
                ("Aggiungi ai preferiti", lambda: self._ai_preferiti(brano)), ("Manda nel cestino", lambda: self._al_cestino(self.albero.GetSelection()))]
        if tipo == "sottobrano":
            pl, brano, n = dati["playlist"], dati["brano"], dati["numero"]
            return [("Riproduci", lambda: self._riproduci(pl, brano, n)),
                ("Aggiungi alla playlist", self._menu_aggiungi(lambda: [Brano(brano.percorso, sottobrano=n)])),
                ("Aggiungi ai preferiti", lambda: self._ai_preferiti(Brano(brano.percorso, sottobrano=n)))]
        return []

    def _conferma(self, domanda, titolo):
        """Una domanda con Si' e No, e No come risposta predefinita."""
        self._suono("domanda")
        with wx.MessageDialog(self, domanda, titolo, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dialogo:
            return dialogo.ShowModal() == wx.ID_YES

    def _al_cestino(self, voce):
        """Maiuscolo+Canc: il file del brano va nel cestino di Windows, e il
        brano esce dalla playlist o dalla cartella in cui sta."""
        dati = self._dati(voce) or {}
        tipo = dati.get("tipo")
        if tipo == "sottobrano":
            self._riscontro("non_disponibile", "Un sottobrano non si cestina da solo: Maiuscolo+Canc si usa sul file del SID.")
            return
        if tipo not in ("brano", "file"):
            self._riscontro("non_disponibile", "Maiuscolo+Canc manda nel cestino un file, da una playlist o da una cartella.")
            return
        pl, brano = dati["playlist"], dati["brano"]
        dove = "" if pl.temporanea else f" Si toglie anche dalla playlist {pl.nome}."
        if not self._conferma(f"Mandare nel cestino di Windows il file {brano.percorso}?{dove}", "Manda nel cestino"):
            self.scrivi("Il file resta dov'è.")
            return
        if self.motore.in_corso == brano.percorso:
            self.motore.stop()
        if not questo_pc.nel_cestino(brano.percorso):
            self._riscontro("errore", f"Non riesco a mandare nel cestino {brano.percorso}.")
            return
        if pl.temporanea:
            genitore = self.albero.GetItemParent(voce)
            vicina = self.albero.GetNextSibling(voce)
            if not vicina.IsOk():
                vicina = self.albero.GetPrevSibling(voce)
            pl.togli(brano)
            self.albero.SelectItem(vicina if vicina.IsOk() else genitore)
            self.albero.Delete(voce)
        else:
            self._togli(pl, brano, annuncia=False)
        self._riscontro("cestino", f"{brano.nome_del_file} è nel cestino di Windows.")

    def _cancella(self, voce):
        dati = self._dati(voce) or {}
        if dati.get("tipo") == "playlist" and dati["playlist"] is self.archivio.preferiti:
            self._riscontro("non_disponibile", "I Preferiti non si eliminano; Canc su un loro brano lo toglie.")
        elif dati.get("tipo") == "playlist":
            self._elimina_playlist(dati["playlist"])
        elif dati.get("tipo") == "brano":
            self._togli(dati["playlist"], dati["brano"])
        else:
            self._riscontro("non_disponibile", "Qui Canc non cancella niente.")

    # Le playlist.

    def _salva_archivio(self):
        try:
            self.archivio.salva()
        except OSError as e:
            self._riscontro("errore", f"Non riesco a salvare le playlist: {e}")

    def _salva_impostazioni(self):
        try:
            self.impostazioni.salva()
        except OSError as e:
            self._riscontro("errore", f"Non riesco a salvare le impostazioni: {e}")

    def _comando_nuova_playlist(self):
        pl = self.archivio.nuova()
        self._salva_archivio()
        self._popola_playlist(seleziona=pl)
        self._riscontro("nuova_playlist", f"Creata la playlist {pl.nome}, vuota. Si riempie da Questo PC, con Aggiungi alla playlist.")

    def _aggiungi(self, pl, percorsi_da_aggiungere):
        if not percorsi_da_aggiungere:
            self._riscontro("niente_da_suonare", "Non c'è niente da aggiungere: nessun file supportato.")
            return
        nuova = pl is None
        if nuova:
            pl = self.archivio.nuova()
        pl.brani.extend(b if isinstance(b, Brano) else Brano(b) for b in percorsi_da_aggiungere)
        self._chiedi_schede(pl)
        self._salva_archivio()
        self._popola_playlist()
        cosa = "Creata la playlist" if nuova else "Aggiunti alla playlist"
        self._riscontro("brano_aggiunto", f"{cosa} {pl.nome}: {brani_al_plurale(len(percorsi_da_aggiungere))}, ora {brani_al_plurale(len(pl.brani))}.")

    def _ai_preferiti(self, brano):
        """Mette nei Preferiti una copia del brano: stesso file e sottobrano."""
        if brano is None:
            self._riscontro("non_disponibile", "F4 mette nei Preferiti il brano selezionato: scegline uno in una playlist o in una cartella.")
            return
        if self.archivio.nei_preferiti(brano):
            self._riscontro("gia_nei_preferiti", f"{brano.nome_del_file} è già nei Preferiti.")
            return
        self.archivio.preferiti.brani.append(Brano(brano.percorso, sottobrano=brano.sottobrano))
        self._chiedi_schede(self.archivio.preferiti)
        self._salva_archivio()
        self._popola_playlist()
        self._riscontro("preferito_aggiunto", f"{brano.nome_del_file} è nei Preferiti, che ora hanno {brani_al_plurale(len(self.archivio.preferiti.brani))}.")

    def _preferito_selezionato(self):
        """F4: il brano da mettere nei Preferiti, dalla voce selezionata."""
        dati = self._dati(self.albero.GetSelection()) or {}
        if dati.get("tipo") == "sottobrano":
            return Brano(dati["brano"].percorso, sottobrano=dati["numero"])
        if dati.get("tipo") in ("brano", "file"):
            return dati["brano"]
        return None

    def _crea_da_qui(self, cartella, nome):
        with wx.BusyCursor():
            files = questo_pc.file_ricorsivi(cartella)
        if not files:
            self._riscontro("niente_da_suonare", f"In {cartella} non c'è niente da suonare.")
            return
        pl = self.archivio.nuova(nome or "Playlist", files)
        self._chiedi_schede(pl)
        self._salva_archivio()
        self._popola_playlist()
        self._riscontro("playlist_da_cartella", f"Creata la playlist {pl.nome} con {brani_al_plurale(len(files))}.")

    def _rinomina(self, pl):
        with wx.TextEntryDialog(self, "Nuovo nome della playlist:", "Rinomina", pl.nome) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            nome = dialogo.GetValue().strip()
        if not nome or nome == pl.nome:
            return
        if any(p is not pl and p.nome.casefold() == nome.casefold() for p in self.archivio.playlist):
            self._riscontro("errore", f"C'è già una playlist che si chiama {nome}.")
            return
        vecchio, pl.nome = pl.nome, nome
        self._salva_archivio()
        self._popola_playlist(seleziona=pl)
        self._riscontro("playlist_rinominata", f"La playlist {vecchio} ora si chiama {nome}.")

    def _elimina_playlist(self, pl):
        domanda = f"Eliminare la playlist {pl.nome}, con {brani_al_plurale(len(pl.brani))}? I file restano sul disco."
        if not self._conferma(domanda, "Elimina playlist"):
            self.scrivi("Eliminazione annullata.")
            return
        indice = self.archivio.playlist.index(pl)
        self.archivio.elimina(pl)
        self._salva_archivio()
        vicina = self.archivio.playlist[min(indice, len(self.archivio.playlist) - 1)] if self.archivio.playlist else "nuova_playlist"
        self._popola_playlist(seleziona=vicina)
        self._riscontro("playlist_eliminata", f"Eliminata la playlist {pl.nome}.")

    def _sposta(self, pl, brano, dove):
        if not pl.sposta(brano, dove):
            self._riscontro("nessun_altro_brano", "Il brano è già lì.")
            return
        self._salva_archivio()
        self._popola_playlist(seleziona=brano)
        i = pl.indice(brano)
        self._riscontro("brano_spostato", f"{brano.nome} ora è il {i + 1} di {len(pl.brani)}.")

    def _salta(self, pl, brano):
        brano.saltato = not brano.saltato
        self._salva_archivio()
        self._aggiorna_etichette()
        if brano.saltato:
            self._riscontro("saltato_acceso", f"{brano.nome} resta nella playlist ma non verrà suonato.")
        else:
            self._riscontro("saltato_spento", f"{brano.nome} torna a essere suonato.")

    def _togli(self, pl, brano, annuncia=True):
        i = pl.togli(brano)
        if i is None:
            return
        if self.coda.loop_playlist is pl and brano is self.coda.punto_a:
            self.coda.togli_loop()
        elif self.coda.loop_playlist is pl and brano is self.coda.punto_b:
            self.coda.punto_b = None
        self._salva_archivio()
        vicino = pl.brani[min(i, len(pl.brani) - 1)] if pl.brani else pl
        self._popola_playlist(seleziona=vicino)
        if annuncia:
            self._riscontro("brano_tolto", f"Tolto {brano.nome_del_file}; nella playlist {pl.nome} restano {brani_al_plurale(len(pl.brani))}.")

    # La riproduzione.

    def _temporanea(self, cartella, files=None):
        """La playlist temporanea di una cartella: i suoi file supportati.
        Se i file sono gli stessi resta la stessa playlist, con gli stessi
        brani: cosi' il brano che suona, e il loop, non si perdono quando la
        cartella si riapre o si aggiorna."""
        pl = self._temporanee.get(cartella)
        if files is None:
            if pl is not None:
                return pl
            try:
                files = questo_pc.contenuto(cartella)[1]
            except OSError:
                files = []
        if pl is None or [b.percorso for b in pl.brani] != files:
            nome = os.path.basename(cartella.rstrip("\\")) or cartella
            pl = self._temporanee[cartella] = Playlist.da_percorsi(nome, files, cartella)
        return pl

    def _suona(self, pl, brano, evento="play", sottobrano=None):
        self.coda.imposta(pl, brano)
        self.motore.suona(brano.percorso, sottobrano or brano.sottobrano)
        numero, totale = self.coda.posizione()
        dove = f"{numero} di {totale}, {'cartella' if pl.temporanea else 'playlist'} {pl.nome}" if totale > 1 else pl.nome
        testo = f"In riproduzione: {brano.percorso}, {dove}."
        if self.motore.sottobrani:
            testo += f" Sottobrano {self.motore.sottobrano} di {self.motore.sottobrani}."
        self._riscontro(evento, testo)
        self._aggiorna_etichette()

    def _riproduci(self, pl, brano, sottobrano=None):
        """Suona un brano scelto nella plancia, se il loop lo permette."""
        if not self.coda.nel_loop(pl, brano):
            self._riscontro("fuori_dal_loop", f"{brano.nome_del_file} è fuori dal loop: si suona solo fra il punto A e il punto B.")
            return
        self._suona(pl, brano, sottobrano=sottobrano)

    def _suona_file(self, percorso, cartella):
        pl = self._temporanea(cartella)
        brano = next((b for b in pl.brani if b.percorso == percorso), None)
        if brano is None:
            # La cartella e' cambiata sul disco da quando la si e' letta.
            pl = self._temporanea(cartella, questo_pc.contenuto(cartella)[1])
            brano = next((b for b in pl.brani if b.percorso == percorso), None)
        if brano is None:
            self._riscontro("errore", f"{os.path.basename(percorso)} non c'è più.")
            return
        self._riproduci(pl, brano)

    def _riproduci_playlist(self, pl):
        brano = self.coda.primo(pl)
        if brano is None and pl is self.archivio.preferiti:
            self._riscontro("niente_da_suonare", "I Preferiti sono vuoti: F4 ci mette il brano selezionato.")
            return
        if brano is None:
            self._riscontro("niente_da_suonare", f"La playlist {pl.nome} non ha brani da suonare.")
            return
        self._suona(pl, brano)

    def _riproduci_cartella(self, cartella):
        """Suona una cartella con tutto l'albero che le sta sotto: i suoi file,
        poi quelli delle sottocartelle. Z, B e N girano su tutti. I brani sono
        quelli delle playlist temporanee di ciascuna cartella, cosi' nella
        plancia il brano che suona si riconosce anche dentro le sottocartelle."""
        with wx.BusyCursor():
            contenuti = questo_pc.contenuti_ricorsivi(cartella)
        if not contenuti:
            self._riscontro("errore", f"Non riesco a leggere {cartella}.")
            return
        brani = [b for sotto, files in contenuti for b in self._temporanea(sotto, files).brani]
        nome = os.path.basename(cartella.rstrip("\\")) or cartella
        pl = Playlist(nome, brani, cartella=cartella)
        brano = self.coda.primo(pl)
        if brano is None:
            self._riscontro("niente_da_suonare", "Né in questa cartella né nelle sue sottocartelle ci sono file da suonare.")
            return
        self._suona(pl, brano)

    def _apri_fino_a(self, cartella):
        """Apre in Questo PC i rami fino alla cartella e ne restituisce la
        voce; None se non la trova."""
        self.albero.Expand(self.nodo_pc)
        voce = self.nodo_pc
        chiave = os.path.normcase(os.path.abspath(cartella))
        while True:
            figlio = next((v for v in self._figli(voce) if (self._dati(v) or {}).get("tipo") in ("unita", "cartella")
                and (chiave == os.path.normcase(self._dati(v)["percorso"].rstrip("\\")) or chiave.startswith(os.path.normcase(self._dati(v)["percorso"].rstrip("\\")) + "\\"))), None)
            if figlio is None:
                return None
            self.albero.Expand(figlio)
            if os.path.normcase(self._dati(figlio)["percorso"].rstrip("\\")) == chiave.rstrip("\\"):
                return figlio
            voce = figlio

    def _brano_finito(self):
        if self._chiusa:
            return
        pl = self.coda.playlist
        prima = pl.indice(self.coda.corrente) if pl else None
        seguente = self.coda.successivo()
        if seguente:
            # Nel loop, dopo il punto B si torna al punto A: ha un suono suo.
            dopo = pl.indice(seguente)
            evento = "ritorno_al_punto_a" if self.coda.intervallo() and prima is not None and dopo is not None and dopo <= prima else "brano_seguente_da_solo"
            self._suona(pl, seguente, evento)
        else:
            self._aggiorna_etichette()
            self._riscontro("fine_playlist", f"Fine di {pl.nome}.")

    def _brano_in_errore(self, percorso):
        if self._chiusa:
            return
        self._riscontro("errore", f"Non riesco a suonare {os.path.basename(percorso or '')}.")
        seguente = self.coda.successivo()
        if seguente:
            self._suona(self.coda.playlist, seguente, "brano_seguente_da_solo")
        else:
            self._aggiorna_etichette()

    def _niente_in_corso(self):
        if self.motore.in_corso:
            return False
        self._riscontro("niente_da_suonare", "Non sta suonando niente.")
        return True

    def _comando_play(self):
        dati = self._dati(self.albero.GetSelection()) or {}
        tipo = dati.get("tipo")
        corrente = self.coda.corrente
        if tipo in ("brano", "file", "sottobrano"):
            numero = dati.get("numero")
            gia_suona = self.motore.in_corso and dati["brano"] is corrente and (numero is None or self.motore.sottobrano == numero)
            if not gia_suona:
                self._riproduci(dati["playlist"], dati["brano"], numero)
                return
        elif tipo == "playlist" and self.coda.playlist is not dati["playlist"]:
            self._riproduci_playlist(dati["playlist"])
            return
        elif tipo in ("cartella", "unita") and not (self.coda.playlist and self.coda.playlist.cartella == dati["percorso"]):
            self._riproduci_cartella(dati["percorso"])
            return
        if self.motore.in_corso and self.motore.in_pausa:
            self.motore.pausa(False)
            self._riscontro("ripresa", f"Riprende da {tempo(self.motore.posizione)}.")
        elif self.motore.in_corso:
            self._riscontro("niente_da_suonare", f"Sta già suonando {corrente.nome_del_file}.")
        elif corrente:
            self._suona(self.coda.playlist, corrente)
        else:
            self._riscontro("niente_da_suonare", "Niente da riprodurre: scegli un brano, una playlist o una cartella nella plancia.")

    def _comando_sottobrano(self, passo):
        if self._niente_in_corso():
            return
        totale = self.motore.sottobrani
        if not totale or totale == 1:
            self._riscontro("nessun_altro_brano", "Il brano che suona non ha sottobrani.")
            return
        n = self.motore.sottobrano + passo
        if not 1 <= n <= totale:
            quale = "il primo" if passo < 0 else "l'ultimo"
            self._riscontro("nessun_altro_brano", f"È {quale} sottobrano, {self.motore.sottobrano} di {totale}.")
            return
        percorso = self.motore.in_corso
        self.motore.suona(percorso, n)
        evento = "sottobrano_successivo" if passo > 0 else "sottobrano_precedente"
        self._riscontro(evento, f"Sottobrano {n} di {totale}, {tempo(durata_del_sottobrano(percorso, n))}.")
        self._aggiorna_etichette()

    def _comando_sottobrano_precedente(self):
        self._comando_sottobrano(-1)

    def _comando_sottobrano_successivo(self):
        self._comando_sottobrano(1)

    def _comando_loop(self):
        dati = self._dati(self.albero.GetSelection()) or {}
        if dati.get("tipo") not in ("brano", "file", "sottobrano"):
            self._riscontro("loop_non_qui", "Il loop si mette su un brano: scegline uno in una playlist o in una cartella.")
            return
        pl, brano = dati["playlist"], dati["brano"]
        coda = self.coda
        if coda.loop_playlist is pl and brano is coda.punto_a:
            coda.togli_loop()
            self._riscontro("loop_tolto", "Loop tolto: si suona di nuovo tutta la lista.")
        elif coda.loop_playlist is pl and brano is coda.punto_b:
            coda.punto_b = None
            self._riscontro("loop_b_tolto", f"Punto B tolto; resta il punto A su {coda.punto_a.nome_del_file}.")
        elif coda.loop_playlist is pl:
            coda.punto_b = brano
            primo, ultimo = coda.intervallo(pl)
            self._riscontro("loop_b_messo", f"Loop fra {coda.punto_a.nome_del_file} e {brano.nome_del_file}: {brani_al_plurale(ultimo - primo + 1)}.")
        else:
            prima = coda.loop_playlist is not None
            coda.loop_playlist, coda.punto_a, coda.punto_b = pl, brano, None
            tolto = " Il loop di prima è tolto." if prima else ""
            self._riscontro("loop_a_messo", f"Punto A del loop su {brano.nome_del_file}.{tolto} Maiuscolo+X su un altro brano mette il punto B.")
        self._aggiorna_etichette()

    def _comando_pausa(self):
        if self._niente_in_corso():
            return
        if self.motore.pausa():
            self._riscontro("pausa", f"Pausa a {tempo(self.motore.posizione)}.")
        else:
            self._riscontro("ripresa", f"Riprende da {tempo(self.motore.posizione)}.")

    def _comando_stop(self):
        if self._niente_in_corso():
            return
        self.motore.stop()
        self._aggiorna_etichette()
        self._riscontro("stop", "Stop. X riparte dall'inizio del brano.")

    def _vicino(self, trova, evento, limite):
        if not self.coda.playlist:
            self._riscontro("niente_da_suonare", "Non c'è una playlist in riproduzione.")
            return
        brano = trova()
        if brano is None:
            self._riscontro("nessun_altro_brano", limite)
            return
        self._suona(self.coda.playlist, brano, evento)

    def _comando_successivo(self):
        self._vicino(self.coda.successivo, "successivo", "È l'ultimo brano.")

    def _comando_precedente(self):
        self._vicino(self.coda.precedente, "precedente", "È il primo brano.")

    def _comando_casuale(self):
        self._vicino(self.coda.casuale, "casuale", "Non ci sono brani da scegliere.")

    def _salto(self, secondi, evento):
        if self._niente_in_corso():
            return
        prima = self.motore.posizione or 0
        durata = self.motore.durata
        arrivo = max(0, prima + secondi)
        if durata is not None:
            arrivo = min(arrivo, durata)
        self.motore.salta(secondi)
        self._riscontro(evento, f"{'Avanti' if secondi > 0 else 'Indietro'} a {tempo(arrivo)} di {tempo(durata)}.")

    def _comando_avanti(self):
        self._salto(self.impostazioni["passo_avanti"], "avanti")

    def _comando_indietro(self):
        self._salto(-self.impostazioni["passo_indietro"], "indietro")

    def _chiedi_secondi(self, chiave, verso):
        self._suono("domanda")
        attuale = self.impostazioni[chiave]
        with wx.TextEntryDialog(self, f"Di quanti secondi salta {verso}? Anche con i decimali, per esempio 2,5.", "Passo di salto", secondi_da_leggere(attuale)) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            testo = dialogo.GetValue()
        secondi = leggi_tempo(testo)
        if not secondi or secondi < 0.1:
            self._riscontro("errore", f"{testo} non è un numero di secondi valido; il passo resta {secondi_da_leggere(attuale)}.")
            return
        self.impostazioni[chiave] = round(secondi, 3)
        self._salva_impostazioni()
        self._riscontro("passo_di_salto", f"Il salto {verso} ora è di {secondi_da_leggere(secondi)} secondi.")

    def _comando_passo_indietro(self):
        self._chiedi_secondi("passo_indietro", "indietro")

    def _comando_passo_avanti(self):
        self._chiedi_secondi("passo_avanti", "avanti")

    def _comando_vai_a_tempo(self):
        if self._niente_in_corso():
            return
        self._suono("domanda")
        durata = self.motore.durata
        with wx.TextEntryDialog(self, f"A che tempo andare? Minuti e secondi, per esempio 1:30. Il brano dura {tempo(durata)}.", "Vai al tempo") as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            testo = dialogo.GetValue()
        secondi = leggi_tempo(testo)
        if secondi is None or (durata is not None and secondi > durata):
            self._riscontro("errore", f"{testo} non è un tempo dentro il brano.")
            return
        self.motore.vai_a(secondi)
        self._riscontro("vai_a_tempo", f"Vado a {tempo(secondi)} di {tempo(durata)}.")

    def _volume(self, passo):
        attuale = self.motore.volume
        nuovo = max(0, min(100, attuale + passo))
        if nuovo == attuale:
            self._riscontro("volume_al_limite", f"Volume già al {'massimo' if passo > 0 else 'minimo'}, {attuale}.")
            return
        self.motore.volume = nuovo
        self.impostazioni["volume"] = nuovo
        self._riscontro("volume_su" if passo > 0 else "volume_giu", f"Volume {nuovo}.")

    def _comando_volume_su(self):
        self._volume(self.impostazioni["passo_volume"])

    def _comando_volume_giu(self):
        self._volume(-self.impostazioni["passo_volume"])

    def _comando_passo_volume(self):
        self._suono("domanda")
        attuale = self.impostazioni["passo_volume"]
        with wx.TextEntryDialog(self, "Di quanto cambiano il volume più e meno? Da 1 a 50.", "Passo del volume", str(attuale)) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            testo = dialogo.GetValue().strip()
        if not testo.isdigit() or not 1 <= int(testo) <= 50:
            self._riscontro("errore", f"{testo} non è un passo da 1 a 50; resta {attuale}.")
            return
        self.impostazioni["passo_volume"] = int(testo)
        self._salva_impostazioni()
        self._riscontro("passo_del_volume", f"Più e meno ora cambiano il volume di {testo}.")

    def _comando_muto(self):
        self.motore.muto = not self.motore.muto
        if self.motore.muto:
            self._riscontro("muto_acceso", "Muto.")
        else:
            self._riscontro("muto_spento", f"Audio di nuovo acceso, volume {self.motore.volume}.")

    def _comando_apri_file(self):
        with wx.FileDialog(self, "Apri file", wildcard=formati.filtro_dialogo(), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            percorso = dialogo.GetPath()
        # Il file aperto non entra in nessuna playlist: resta finche' non si
        # suona altro. La sua cartella vuota lo tiene fuori da Questo PC.
        pl = Playlist("file aperto", [Brano(percorso)], cartella="")
        self._suona(pl, pl.brani[0], "file_aperto")

    def _comando_impostazioni(self):
        self._riscontro("non_disponibile", "La finestra delle impostazioni arriva con la tappa 3.")

    # F8 e F9.

    def _vai_al_brano(self):
        corrente, pl = self.coda.corrente, self.coda.playlist
        if not corrente or not self.motore.in_corso:
            self._riscontro("niente_da_suonare", "Non sta suonando niente.")
            return
        if not pl.temporanea:
            # Una playlist mai aperta non ha ancora i suoi brani nella plancia.
            nodo = self.nodo_preferiti if pl is self.archivio.preferiti else next((v for v in self._figli(self.nodo_playlist) if self._dati(v).get("playlist") is pl), None)
            if nodo is not None and self._dati(nodo).get("caricato") is False:
                self._carica(nodo, self._dati(nodo))
        voce = next((v for v in self._tutte_le_voci() if (self._dati(v) or {}).get("tipo") in ("brano", "file")
            and self._dati(v)["brano"] is corrente), None)
        if voce is None and pl.temporanea and pl.cartella:
            # Suonando una cartella con le sottocartelle, il brano puo' stare
            # in una sottocartella mai aperta nella plancia.
            cartella = self._apri_fino_a(os.path.dirname(corrente.percorso))
            if cartella is not None:
                voce = next((v for v in self._figli(cartella) if (self._dati(v) or {}).get("brano") is corrente), None)
        if voce is None:
            self._riscontro("niente_da_suonare", f"{corrente.nome_del_file} non è nella plancia: è stato aperto con Apri file.")
            return
        # Se i sottobrani del SID sono aperti, la selezione va su quello che suona.
        if self.albero.IsExpanded(voce):
            voce = next((v for v in self._figli(voce) if self._dati(v).get("numero") == self.motore.sottobrano), voce)
        self.albero.EnsureVisible(voce)
        self.albero.SelectItem(voce)
        self._suono("vai_al_brano")
        self.albero.SetFocus()

    def _informazioni(self):
        corrente, pl = self.coda.corrente, self.coda.playlist
        if not corrente or not self.motore.in_corso:
            self._riscontro("informazioni", f"Non sta suonando niente. Volume {self.motore.volume}{', muto' if self.motore.muto else ''}.")
            return
        stato = "In pausa" if self.motore.in_pausa else "In riproduzione"
        numero, totale = self.coda.posizione()
        testo = f"{stato}: {corrente.percorso}, {tempo(self.motore.posizione)} di {tempo(self.motore.durata)}."
        if self.motore.sottobrani:
            testo += f" Sottobrano {self.motore.sottobrano} di {self.motore.sottobrani}."
        if totale > 1:
            testo += f" Brano {numero} di {totale}, {'cartella' if pl.temporanea else 'playlist'} {pl.nome}."
        limiti = self.coda.intervallo()
        if limiti:
            testo += f" Loop fra il brano {limiti[0] + 1} e il {limiti[1] + 1}."
        testo += f" Volume {self.motore.volume}{', muto' if self.motore.muto else ''}."
        self._riscontro("informazioni", testo)

    # F1, F2, F3.

    def _mostra_testo(self, evento, titolo, testo):
        self._suono(evento)
        with FinestraTesto(self, titolo, testo) as finestra:
            finestra.ShowModal()

    def _leggi_risorsa(self, nome):
        try:
            with open(percorsi.percorso_risorsa(nome), encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            return f"Non riesco a leggere {nome}: {e}"

    def _manuale(self):
        self._mostra_testo("manuale", "Manuale di MeTeOra", self._leggi_risorsa("manuale.txt"))

    def _changelog(self):
        self._mostra_testo("changelog", "Novità di MeTeOra", self._leggi_risorsa("CHANGELOG.md"))

    def _crediti(self):
        testo = "\n".join([
            f"MeTeOra {version.VERSION} del {version.DATE}.",
            f"Autori: {version.AUTHOR}.",
            "MeTeOra è formato da tre parole italiane, una dedica di Gabriele alla sua ragazza Ginevra.",
            "Riproduzione: libmpv, dal progetto mpv, con FFmpeg e libopenmpt.",
            "SID del Commodore 64: libsidplayfp, con l'emulazione reSIDfp.",
            "Durate dei SID: il database Songlengths della High Voltage SID Collection.",
            "Effetti sonori: Acusticator, della libreria GBUtils di Gabriele.",
            "Durate e tag dei file audio: mutagen.",
            "Interfaccia: wxPython.",
            "Licenza: GPL 3.",
        ])
        self._mostra_testo("crediti", "Crediti", testo)

    # L'uscita.

    def _alla_chiusura(self, evento):
        if self._chiusa:
            evento.Skip()
            return
        self._chiusa = True
        self._salva_archivio()
        self.schedario.ferma()
        with contextlib.suppress(OSError):
            self.schedario.salva()
        with contextlib.suppress(OSError):
            self.impostazioni.salva()
        self.motore.chiudi()
        # Il suono dell'uscita si ascolta intero prima che il processo finisca.
        suoni.suona("uscita", self.impostazioni["volume_effetti"], sync=True)
        evento.Skip()
