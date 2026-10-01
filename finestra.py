# MeTeOra, la finestra principale: plancia dei comandi, console e cruscotto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.2.0 i sottobrani dei SID, nella 1.3.0 il loop A-B, nella 1.4.0 il cestino,
# nella 1.5.0 le cartelle suonate con le sottocartelle, nella 1.6.0 i Preferiti, nella 1.7.0 conti e durate delle playlist, nella 1.8.0 il filtro,
# nella 1.12.0 durate nella plancia, riga della console riscritta, F9 e F10, Maiuscolo+C;
# nella 1.13.0 l'avanzamento automatico che segue la plancia, nella 1.14.0 l'inseguimento con Maiuscolo+F8,
# nella 1.15.0 la ricerca globale, nella 1.17.0 Z, B e N che seguono la plancia e F12,
# nella 1.20.0 F1, F2 e F3 nella console, l'ora in fondo alle scritte e la ricerca nella console;
# nella 1.21.0 il volume fino a 300, nella 1.22.0 i conti delle cartelle, nella 1.23.0 i Risultati ad albero;
# nella 1.26.0 la ripresa all'avvio, J e K e i tasti da 1 a 0; nella 1.28.0 la selezione multipla e X da capo;
# nella 1.28.1 una barra rovesciata sola per le due ricerche; nella 1.34.0 il filtro nel menu della playlist e con la barra
# verticale, le istruzioni come commenti nei campi, la ricerca nella console con i jolly, le cartelle senza niente da suonare
# nascoste, i problemi interni nella console e le righe della console impostabili; nella 1.34.6 le correzioni della revisione:
# cartelle aperte che non spariscono, playlist che si ricaricano, Risultati cestinati, emoji e jolly nella console.

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
import datetime
import os
import random
import re
import sys
import threading
import traceback
import warnings

import wx

import formati
import percorsi
import questo_pc
import songlengths
import suoni
import version
from contatore import Contatore
from filtro import COMMENTO, ErroreFiltro, Filtro, modello_della_console
from impostazioni import Impostazioni
from motore import VOLUME_MASSIMO, durata_del_sottobrano
from playlist import Archivio, Brano, Coda, Playlist
from ricerca import AlberoDeiRisultati, Ricerca
from schedario import Schedario

FILE_PLAYLIST = "MeTeOra - Playlist.json"
FILE_IMPOSTAZIONI = "MeTeOra - Impostazioni.json"
FILE_SCHEDARIO = "MeTeOra - Schedario.json"
# Quanti caratteri al massimo del messaggio di un problema interno: la
# console riceve una riga breve, non un registro.
MESSAGGIO_DEL_PROBLEMA = 200
# Quanti rami al massimo apre F10 in una volta.
MASSIMO_DI_RAMI = 2000
# Quanti risultati della ricerca si mostrano alla volta.
PAGINA_DEI_RISULTATI = 1000

# I tasti a lettera: (carattere, maiuscolo) -> comando.
TASTI = {
    ("z", False): "precedente",
    ("x", False): "play",
    ("j", False): "playlist_precedente",
    ("k", False): "playlist_successiva",
    ("x", True): "loop",
    ("c", False): "pausa",
    ("c", True): "togli_loop",
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
    ("\\", False): "ricerca",
    # La barra verticale: Maiuscolo con la barra rovesciata nella tastiera
    # italiana, che a seconda di Windows arriva in un modo o nell'altro.
    ("\\", True): "filtro",
    ("|", False): "filtro",
    ("|", True): "filtro",
    ("m", True): "passo_volume",
}
# I tasti gia' assegnati nel piano a funzioni delle tappe successive: per ora
# dicono di non essere ancora disponibili.
FUTURI = {
    "a": "velocità", "s": "velocità", "d": "velocità", "f": "tono", "g": "tono", "h": "tono",
    "l": "dissolvenza",
    "r": "segnalibri", "t": "segnalibri", "y": "segnalibri",
    "u": "equalizzatore", "i": "equalizzatore", "o": "equalizzatore", "p": "equalizzatore", "è": "equalizzatore",
    "'": "scelta della traccia audio", "ì": "scelta della traccia audio",
}
FUTURI_MAIUSCOLI = {"l": "durata della dissolvenza"}

TASTI_COMUNI = [
    "X riproduce la voce selezionata o riprende, C pausa, V stop, Z e B brano precedente e successivo, N brano a caso.",
    "Q ed E indietro e avanti nel brano, Maiuscolo con Q ed E ne cambiano i secondi, W va a un tempo, + e - volume, Maiuscolo+M il passo del volume, M muto.",
    "Maiuscolo+X mette e toglie i punti A e B del loop sul brano selezionato, Maiuscolo+C toglie il loop.",
    "J e K aprono e suonano la playlist precedente e successiva, le cifre da 1 a 0 le prime dieci playlist.",
    "F4 mette nei Preferiti il brano selezionato. F5 plancia, F6 console, F7 cruscotto, F8 porta la selezione sul brano in riproduzione e Maiuscolo+F8 ce la tiene agganciata, F9 chiude e F10 apre tutto il ramo selezionato.",
    "Barra rovesciata: nella console cerca nella console, altrove in tutte le playlist e in tutte le unità. Barra verticale: il filtro della playlist in cui sta la plancia, anche dalla console.",
    "F1 manuale, F2 novità, F3 crediti e F12 elenco dei tasti, tutti nella console. Esc esce salvando tutto.",
]
# Le righe del cruscotto proprie di ogni tipo di voce della plancia.
TASTI_DEL_CONTESTO = {
    "risultati": ("i Risultati della ricerca", "Invio, Applicazioni o Spazio: menu con Riproduci, Salva come playlist, Nuova ricerca e Ferma la ricerca."),
    "altri": ("la voce che mostra altri risultati", "Invio mostra i risultati seguenti."),
    "gruppo_risultati": ("un ramo dei Risultati", "Freccia destra lo apre: i risultati stanno come stavano, sotto la loro playlist o lungo il percorso della loro cartella."),
    "preferiti": ("i Preferiti", "Invio, Applicazioni o Spazio: menu con Riproduci e Filtro. Barra verticale: il filtro. Canc su un loro brano lo toglie dai Preferiti."),
    "radice_playlist": ("il ramo Playlist", "Invio, Applicazioni o Spazio: menu con Nuova playlist."),
    "playlist": ("una playlist", "Invio, Applicazioni o Spazio: menu con Riproduci, Filtro, Rinomina ed Elimina. Barra verticale: il filtro. Canc elimina la playlist, dopo una conferma."),
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
    """Un numero di secondi da leggere: 10, oppure 1.5."""
    return f"{secondi:.3f}".rstrip("0").rstrip(".")


def durata_lunga(secondi):
    """Una durata come ore:minuti:secondi.millesimi, con le ore solo se ci
    sono e i millesimi solo se non sono zero: 1:02:03.456, 4:05, 0:07.250."""
    millesimi = round(secondi * 1000)
    ore, resto = divmod(millesimi, 3600000)
    minuti, resto = divmod(resto, 60000)
    secondi, millesimi = divmod(resto, 1000)
    testo = f"{ore}:{minuti:02d}:{secondi:02d}" if ore else f"{minuti}:{secondi:02d}"
    return testo + (f".{millesimi:03d}" if millesimi else "")


def e_un_titolo(riga):
    """Nel manuale i titoli sono le righe che non finiscono con un segno di
    punteggiatura: tutte le altre sono frasi."""
    riga = riga.strip()
    return bool(riga) and riga[-1] not in ".:;!?)"


def sezione_del_manuale(testo, titolo):
    """Le righe della sezione del manuale che ha quel titolo, titolo
    compreso, fino al titolo seguente; lista vuota se non c'e'."""
    righe = [r.strip() for r in testo.splitlines()]
    if titolo not in righe:
        return []
    inizio = righe.index(titolo)
    fine = next((i for i in range(inizio + 1, len(righe)) if e_un_titolo(righe[i])), len(righe))
    return [r for r in righe[inizio:fine] if r]


def righe_del_changelog(testo):
    """Il changelog da leggere nella console: senza i segni del Markdown, con
    i titoli delle versioni scritti come frasi."""
    righe = []
    for riga in testo.splitlines():
        riga = riga.strip()
        versione = re.match(r"^#+\s*\[([^\]]+)\]\s*-\s*(\S+)", riga)
        if versione:
            riga = f"Versione {versione.group(1)} del {versione.group(2)}"
        elif riga.startswith("#"):
            continue
        elif riga.startswith("- "):
            riga = riga[2:]
        if riga:
            righe.append(riga)
    return righe


def brani_al_plurale(n):
    return "1 brano" if n == 1 else f"{n} brani"


def _passo_nostro(nome_del_file):
    """Vero se un passo della traccia sta nel codice di MeTeOra. Dai sorgenti
    i nomi sono percorsi interi; nel pacchetto di PyInstaller sono solo nomi
    come finestra.py, e si riconoscono dai moduli caricati dalla cartella del
    programma."""
    cartella = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
    nome = os.path.normcase(nome_del_file)
    if os.path.isabs(nome):
        return nome.startswith(cartella)
    nostri = {os.path.splitext(os.path.basename(m.__file__))[0].lower() for m in list(sys.modules.values())
        if isinstance(getattr(m, "__file__", None), str) and os.path.normcase(os.path.dirname(os.path.abspath(m.__file__))) == cartella}
    return os.path.splitext(os.path.basename(nome))[0] in nostri


_PASSO_NEL_TESTO = re.compile(r'File "([^"]+)", line (\d+), in (\S+)')


def _breve(messaggio):
    messaggio = " ".join(messaggio.split())
    if len(messaggio) > MESSAGGIO_DEL_PROBLEMA:
        messaggio = messaggio[:MESSAGGIO_DEL_PROBLEMA].rstrip() + "..."
    return messaggio


def riga_dell_avviso(messaggio):
    """Una riga sola per un'eccezione che python-mpv ha trasformato in un
    avviso: la prima riga del suo testo e il punto del codice di MeTeOra da
    cui viene, se la traccia ci passa."""
    testo = str(messaggio)
    riga = f"Problema interno nel motore: {_breve(testo.splitlines()[0] if testo else '')}"
    passi = [p for p in _PASSO_NEL_TESTO.finditer(testo) if _passo_nostro(p.group(1))]
    if passi:
        riga += f", in {os.path.basename(passi[-1].group(1))} alla riga {passi[-1].group(2)}, {passi[-1].group(3)}"
    return riga + "."


def riga_del_problema(tipo, valore, traccia):
    """Una riga sola per un problema interno: che cosa e' successo e dove,
    nel codice di MeTeOra se ci e' passato, altrimenti nell'ultimo punto."""
    passi = traceback.extract_tb(traccia) if traccia else []
    nostri = [p for p in passi if _passo_nostro(p.filename)]
    passo = (nostri or passi or [None])[-1]
    testo = f"Problema interno: {tipo.__name__}"
    # Anche un messaggio che non si lascia scrivere non deve fermare la riga.
    messaggio = ""
    with contextlib.suppress(Exception):
        messaggio = _breve(str(valore))
    if messaggio:
        testo += f", {messaggio}"
    if passo is not None:
        testo += f", in {os.path.basename(passo.filename)} alla riga {passo.lineno}, {passo.name}"
    return testo + "."


class DialogoTesto(wx.TextEntryDialog):
    """Un campo da una riga con il testo di prima gia' selezionato: scrivendo
    lo si sostituisce, con le frecce lo si corregge."""

    def ShowModal(self):
        campo = next((c for c in self.GetChildren() if isinstance(c, wx.TextCtrl)), None)
        if campo is not None:
            wx.CallAfter(campo.SelectAll)
        return super().ShowModal()


# Le istruzioni in cima ai campi dei filtri e delle ricerche, scritte come
# righe di commento, che cominciano con il dollaro e non contano.
_GRAMMATICA_DEL_FILTRO = [
    "Spazio: tutti i termini insieme, come rob hubbard. Andare a capo vale come uno spazio.",
    "Barra verticale: l'uno o l'altro, come hubbard|galway.",
    "Meno davanti a un termine: escluso, come -remix.",
    "Asterisco: qualsiasi testo, come comm*do. Cancelletto: una o più cifre, come vol#.",
    'Virgolette: la sequenza esatta, spazi compresi, come "last ninja".',
    "Maiuscole e accenti non contano. Un termine senza comando cerca nel nome del file e nei tag.",
    "I comandi sono una lettera, un segno fra < > = <= >= e un valore:",
    "t tempo, come t<=3:00 o t>90.",
    "d dimensione, come d>5m o d<700k.",
    "y anno, come y<1990.",
    "r sottobrani dei SID, come r>1.",
    "Questi solo con l'uguale:",
    "k tipo: k=sid, k=audio, k=video, k=tracker, k=midi, o un'estensione come k=flac.",
    "a autore, come a=hubbard.",
    "n titolo, come n=commando.",
    "l album.",
    "g genere.",
    "p percorso della cartella, come p=c64music.",
    "s saltato: s=1 i brani saltati, s=0 gli altri.",
    "Le righe che cominciano con il dollaro non contano: scrivi nell'ultima riga.",
]
ISTRUZIONI_DEL_FILTRO = ["Puoi usare questi comandi per comporre il filtro.", *_GRAMMATICA_DEL_FILTRO]
ISTRUZIONI_DELLA_RICERCA = ["Puoi usare questi comandi per comporre la ricerca, in tutte le playlist e in tutte le unità.", *_GRAMMATICA_DEL_FILTRO]
ISTRUZIONI_DELLA_CONSOLE = [
    "Puoi usare questi segni per comporre la ricerca nella console.",
    "Il testo si cerca così com'è, spazi compresi; maiuscole e minuscole non contano. Andare a capo vale come uno spazio.",
    "Asterisco: qualsiasi testo nella stessa riga, come non*suonare.",
    "Cancelletto: una o più cifre, come volume #.",
    'Virgolette: la sequenza esatta, maiuscole comprese, come "SID".',
    "I messaggi finiscono con l'ora: 07:13 trova ciò che è accaduto alle 7 e 13, e 07:# tutta l'ora delle 7; trovano anche i tempi dei brani che contengono quelle cifre, come 1:07:13.",
    "Invio, dalla console, passa all'occorrenza seguente.",
    "Le righe che cominciano con il dollaro non contano: scrivi nell'ultima riga.",
]


class FinestraFiltro(wx.Dialog):
    """Il campo multiriga dei filtri e delle ricerche. In cima le istruzioni,
    come righe di commento che cominciano con il dollaro; in fondo la riga in
    cui si scrive, con il testo di prima selezionato: scrivendo lo si
    sostituisce, con le frecce lo si corregge. Invio conferma, Ctrl+Invio va
    a capo, Esc annulla."""

    def __init__(self, genitore, titolo, testo, istruzioni):
        from GBwx import STILE_ADATTABILE, adatta_finestra, pannello_scorrevole

        super().__init__(genitore, title=titolo, style=STILE_ADATTABILE)
        pannello = pannello_scorrevole(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        etichetta = wx.StaticText(pannello, label=f"{titolo}. Invio conferma, Ctrl+Invio va a capo, Esc annulla.")
        self._commenti = sorted((f"{COMMENTO} {riga}" for riga in istruzioni), key=len, reverse=True)
        # Senza a capo automatici: ogni istruzione resta una riga intera, con
        # il suo dollaro, quando NVDA e il display braille la leggono.
        self.campo = wx.TextCtrl(pannello, value="".join(f"{COMMENTO} {riga}\n" for riga in istruzioni), style=wx.TE_MULTILINE | wx.HSCROLL)
        self.campo.SetName(titolo)
        self.campo.SetMinSize(wx.Size(-1, self.campo.GetCharHeight() * 12))
        # L'inizio della riga in cui si scrive, misurato dal controllo: le
        # posizioni di Windows contano i ritorni a capo a modo loro.
        self._inizio = self.campo.GetLastPosition()
        self.campo.AppendText(testo)
        pulsanti = wx.StdDialogButtonSizer()
        pulsanti.AddButton(wx.Button(pannello, wx.ID_OK, "Conferma"))
        pulsanti.AddButton(wx.Button(pannello, wx.ID_CANCEL, "Annulla"))
        pulsanti.Realize()
        sizer.Add(etichetta, 0, wx.ALL, 5)
        sizer.Add(self.campo, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        sizer.Add(pulsanti, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        pannello.SetSizer(sizer)
        adatta_finestra(self, pannello, (600, 400))
        self.campo.Bind(wx.EVT_KEY_DOWN, self._tasto)
        self._sulla_riga_da_scrivere()
        self.campo.SetFocus()

    def _sulla_riga_da_scrivere(self):
        if self and self.campo:
            self.campo.SetSelection(self._inizio, self.campo.GetLastPosition())
            self.campo.ShowPosition(self.campo.GetLastPosition())

    def ShowModal(self):
        # Mostrandosi il campo potrebbe spostare la selezione: la si rimette
        # sulla riga in cui si scrive.
        wx.CallAfter(self._sulla_riga_da_scrivere)
        return super().ShowModal()

    def _tasto(self, evento):
        if evento.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            if evento.GetModifiers() == wx.MOD_CONTROL:
                self.campo.WriteText("\n")
            elif evento.GetModifiers() == wx.MOD_NONE:
                self.EndModal(wx.ID_OK)
            return
        evento.Skip()

    @property
    def testo(self):
        """Cio' che e' stato scritto, senza le righe di commento. Un
        Backspace di troppo in testa all'ultima riga la attacca all'ultima
        istruzione: cio' che segue un'istruzione si riprende."""
        righe = []
        for riga in self.campo.GetValue().splitlines():
            istruzione = next((c for c in self._commenti if riga.startswith(c)), None)
            if istruzione is not None and len(riga) > len(istruzione):
                righe.append(riga[len(istruzione):])
            elif not riga.lstrip().startswith(COMMENTO):
                righe.append(riga)
        return "\n".join(righe)


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
        self.coda.ammesso = self._ammesso
        # I filtri compilati, per playlist: (testo, Filtro).
        self._filtri = {}
        # La ricerca in corso o l'ultima fatta, i suoi risultati come
        # playlist temporanea, e quanti se ne mostrano nella plancia.
        self._ricerca = None
        self._testo_della_ricerca = ""
        self.risultati = None
        # Quanti risultati della ricerca sono gia' passati nella plancia.
        self._risultati_letti = 0
        self.nodo_risultati = None
        self._albero_dei_risultati = None
        self.schedario = Schedario(os.path.join(cartella_dati, FILE_SCHEDARIO), avvisa=lambda: wx.CallAfter(self._schede_arrivate))
        self.schedario.carica()
        self.contatore = Contatore(self.schedario, avvisa=lambda: wx.CallAfter(self._conti_arrivati))
        # Le playlist temporanee nate dalle cartelle di Questo PC, per cartella:
        # rigiocando un file della stessa cartella si riusa la stessa.
        self._temporanee = {}
        self._area_precedente = None
        self._posizione_della_console = None
        self._posizione_del_cruscotto = None
        # La categoria dell'ultima riga della console: una riga nuova della
        # stessa categoria la sostituisce invece di aggiungersi.
        self._categoria = None
        # Il testo dell'ultima ricerca nella console e la sua espressione
        # regolare, per Invio.
        self._cercato_in_console = ""
        self._modello_della_console = None
        # Inizio e fine dell'ultima occorrenza trovata, nel testo delle righe.
        self._occorrenza = None
        # Quante righe in fondo non si tagliano mentre F1, F2, F3 o F12 scrivono.
        self._da_tenere = 0
        # Quante volte di seguito e' arrivato l'ultimo problema interno.
        self._ripetizioni = 0
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
        # A selezione multipla, come in Esplora risorse: Maiuscolo con le
        # frecce allarga la selezione, Ctrl con le frecce muove il fuoco
        # senza selezionare, Ctrl+Spazio accende e spegne la voce col fuoco.
        self.albero = wx.TreeCtrl(pannello, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_MULTIPLE)
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
        self.albero.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self._chiusa_una_voce)
        self.albero.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._invio)
        self.albero.Bind(wx.EVT_TREE_ITEM_MENU, self._menu_da_evento)
        self.albero.Bind(wx.EVT_KEY_DOWN, self._tasto_nell_albero)
        self.albero.Bind(wx.EVT_SET_FOCUS, self._fuoco_all_albero)
        self.console.Bind(wx.EVT_SET_FOCUS, self._fuoco_alla_console)
        self.console.Bind(wx.EVT_KILL_FOCUS, self._console_lasciata)
        self.console.Bind(wx.EVT_KEY_DOWN, self._tasto_nella_console)
        self.cruscotto.Bind(wx.EVT_SET_FOCUS, self._fuoco_al_cruscotto)
        self.cruscotto.Bind(wx.EVT_KILL_FOCUS, self._cruscotto_lasciato)

    def _popola_albero(self):
        radice = self.albero.AddRoot("MeTeOra")
        self.nodo_preferiti = self.albero.AppendItem(radice, "Preferiti", data={"tipo": "playlist", "playlist": self.archivio.preferiti, "caricato": False})
        self.nodo_playlist = self.albero.AppendItem(radice, "Playlist", data={"tipo": "radice_playlist"})
        self.nodo_pc = self.albero.AppendItem(radice, "Questo PC", data={"tipo": "pc", "caricato": False})
        self.albero.SetItemHasChildren(self.nodo_pc, True)
        self.albero.AppendItem(radice, "Apri file", data={"tipo": "comando", "comando": "apri_file"})
        self.albero.AppendItem(radice, "Impostazioni", data={"tipo": "comando", "comando": "impostazioni"})
        self._popola_playlist()
        self._seleziona(self.nodo_preferiti)

    # La console.

    def scrivi(self, testo, categoria=None, ora=True):
        """Aggiunge una riga in fondo alla console senza spostarne il
        cursore, e tiene le ultime righe, quante ne dicono le impostazioni. Con una
        categoria, per esempio il volume, se anche l'ultima riga era di quella
        categoria la riga si riscrive invece di aggiungersene un'altra.
        In fondo alla riga va l'ora, ore e minuti; chi scrive piu' righe di
        seguito la chiede solo per l'ultima."""
        if ora:
            testo = f"{testo} {datetime.datetime.now():%H:%M}"
        posizione = self.console.GetInsertionPoint()
        if categoria is not None and categoria == self._categoria and self._righe:
            # Le posizioni del controllo: le emoji valgono due.
            inizio = self._unita("".join(r + "\n" for r in self._righe[:-1]))
            self.console.Remove(inizio, self.console.GetLastPosition())
            self.console.AppendText(testo)
            self._righe[-1] = testo
            self.console.SetInsertionPoint(min(posizione, self.console.GetLastPosition()))
            return
        self._categoria = categoria
        self.console.AppendText(("\n" if self._righe else "") + testo)
        self._righe.append(testo)
        limite = max(self.impostazioni["righe_della_console"], self._da_tenere)
        if len(self._righe) > limite + 100:
            togliere = len(self._righe) - limite
            caratteri = self._unita("".join(r + "\n" for r in self._righe[:togliere]))
            self.console.Remove(0, caratteri)
            del self._righe[:togliere]
            posizione = max(0, posizione - caratteri)
            if self._posizione_della_console is not None:
                self._posizione_della_console = max(0, self._posizione_della_console - caratteri)
        self.console.SetInsertionPoint(posizione)

    def _suono(self, evento):
        suoni.suona(evento, self.impostazioni["volume_effetti"])

    def _riscontro(self, evento, testo, categoria=None):
        self._suono(evento)
        self.scrivi(testo, categoria)

    # I problemi interni.

    def ascolta_i_problemi(self):
        """Le eccezioni che nessuno gestisce, nel filo della finestra e negli
        altri fili, arrivano nella console con una riga breve e un suono loro;
        e continuano ad andare dove andavano prima, cioe' sul terminale se
        c'e'."""
        precedente, precedente_dei_fili = sys.excepthook, threading.excepthook

        def manda(tipo, valore, traccia):
            if issubclass(tipo, (KeyboardInterrupt, SystemExit)):
                return
            # Senza wx.App, per esempio durante l'uscita, la console non c'e'
            # piu': il problema resta solo dove andava prima.
            with contextlib.suppress(Exception):
                wx.CallAfter(self._problema, tipo, valore, traccia)

        def nel_filo_della_finestra(tipo, valore, traccia):
            with contextlib.suppress(Exception):
                precedente(tipo, valore, traccia)
            manda(tipo, valore, traccia)

        def negli_altri_fili(argomenti):
            with contextlib.suppress(Exception):
                precedente_dei_fili(argomenti)
            manda(argomenti.exc_type, argomenti.exc_value, argomenti.exc_traceback)

        precedente_degli_avvisi = warnings.showwarning

        def negli_avvisi(messaggio, categoria, nome_del_file, riga, file=None, line=None):
            with contextlib.suppress(Exception):
                precedente_degli_avvisi(messaggio, categoria, nome_del_file, riga, file, line)
            # python-mpv trasforma in avvisi le eccezioni dei callback che
            # chiama, compresi quelli del motore di MeTeOra.
            if os.path.basename(nome_del_file).lower().startswith("mpv") and str(messaggio).startswith("Unhandled"):
                with contextlib.suppress(Exception):
                    wx.CallAfter(self._scrivi_il_problema, riga_dell_avviso(messaggio))

        sys.excepthook = nel_filo_della_finestra
        threading.excepthook = negli_altri_fili
        warnings.showwarning = negli_avvisi

    def _problema(self, tipo, valore, traccia):
        self._scrivi_il_problema(riga_del_problema(tipo, valore, traccia))

    def _scrivi_il_problema(self, riga):
        """Scrive il problema nella console. Lo stesso problema ripetuto di
        seguito riscrive la sua riga con il conto delle volte, senza suono:
        un errore che torna a ogni istante non deve riempire la console."""
        if not self or self._chiusa:
            return
        categoria = ("problema", riga)
        if self._categoria == categoria:
            self._ripetizioni += 1
            self.scrivi(f"{riga[:-1]}, {self._ripetizioni} volte.", categoria)
            return
        self._ripetizioni = 1
        # Se il problema sta nei suoni, la riga arriva lo stesso.
        with contextlib.suppress(Exception):
            self._suono("problema")
        self.scrivi(riga, categoria)

    # Il fuoco e il cruscotto.

    def _fuoco_all_albero(self, evento):
        evento.Skip()
        self._area_precedente = "albero"

    def _fuoco_alla_console(self, evento):
        evento.Skip()
        self._area_precedente = "console"
        if self._posizione_della_console is not None:
            wx.CallAfter(self._rimetti_posizione, self.console, self._posizione_della_console)

    def _rimetti_posizione(self, controllo, posizione):
        if self and controllo:
            controllo.SetInsertionPoint(min(posizione, controllo.GetLastPosition()))

    def _console_lasciata(self, evento):
        evento.Skip()
        self._posizione_della_console = self.console.GetInsertionPoint()

    def _fuoco_al_cruscotto(self, evento):
        evento.Skip()
        # Il controllo, quando riceve il fuoco, rimette il cursore in cima:
        # se il testo non cambia, lo si riporta dove era.
        if not self._rinfresca_cruscotto() and self._posizione_del_cruscotto is not None:
            wx.CallAfter(self._rimetti_posizione, self.cruscotto, self._posizione_del_cruscotto)

    def _cruscotto_lasciato(self, evento):
        evento.Skip()
        self._posizione_del_cruscotto = self.cruscotto.GetInsertionPoint()

    def _rinfresca_cruscotto(self):
        """Riscrive il cruscotto solo se il testo cambia: tornando dallo stesso
        punto il cursore resta dove era."""
        testo = "\n".join(self.righe_del_cruscotto())
        attuale = self.cruscotto.GetValue().replace("\r\n", "\n").replace("\r", "\n")
        if attuale == testo:
            return False
        self.cruscotto.SetValue(testo)
        self.cruscotto.SetInsertionPoint(0)
        self._posizione_del_cruscotto = None
        return True

    def righe_del_cruscotto(self):
        """Le righe del cruscotto per l'area da cui si arriva."""
        if self._area_precedente == "console":
            righe = ["Tasti per la console.", "Frecce, Pagina su e giù, Home e Fine per leggere; i messaggi nuovi arrivano in fondo, con l'ora. "
                "La barra rovesciata cerca nella console, anche con i jolly e le virgolette, e Invio passa all'occorrenza seguente."]
        elif len(self._voci_selezionate()) > 1:
            righe = [f"Tasti per {len(self._voci_selezionate())} voci selezionate: un ramo selezionato vale per tutto ciò che contiene.",
                "X suona la selezione come una playlist invisibile, che resta finché non premi V. Invio, Applicazioni o Spazio: menu della selezione. "
                "Canc toglie i brani dalle playlist ed elimina le playlist, Maiuscolo+Canc manda i file nel cestino, F4 li mette nei Preferiti.",
                "Maiuscolo con le frecce allarga la selezione, Ctrl con le frecce muove il fuoco senza selezionare, Ctrl+Spazio accende e spegne la voce col fuoco."]
        else:
            dati = self._dati(self._voce_corrente()) or {}
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
            wx.WXK_F7: lambda: self._vai(self.cruscotto, "cruscotto"), wx.WXK_F4: self._f4, wx.WXK_F8: self._vai_al_brano, wx.WXK_F9: self._chiudi_tutto, wx.WXK_F10: self._apri_tutto, wx.WXK_F12: self._elenco_dei_tasti,
            wx.WXK_ESCAPE: self.Close,
        }
        if modificatori == wx.MOD_NONE and codice in tasti_funzione:
            tasti_funzione[codice]()
            return
        if modificatori == wx.MOD_SHIFT and codice == wx.WXK_F8:
            self._aggancia()
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
        if carattere.isdigit() and not maiuscolo:
            self._playlist_numero(int(carattere) or 10)
            return
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
            self._menu(self._voce_corrente())
        elif codice == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_NONE and len(self._voci_selezionate()) > 1:
            self._cancella_selezione()
        elif codice == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_SHIFT and len(self._voci_selezionate()) > 1:
            self._cestina_selezione()
        elif codice == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_NONE:
            self._cancella(self._voce_corrente())
        elif codice == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_SHIFT:
            self._al_cestino(self._voce_corrente())
        else:
            evento.Skip()

    # L'albero.

    def _voce_corrente(self):
        """La voce che ha il fuoco nella plancia. Con la selezione multipla non
        c'e' piu' "la voce selezionata": c'e' questa, piu' l'insieme delle
        selezionate."""
        return self.albero.GetFocusedItem()

    def _seleziona(self, voce):
        """Seleziona soltanto questa voce e le da' il fuoco, come una freccia."""
        self.albero.UnselectAll()
        self.albero.SelectItem(voce)
        self.albero.SetFocusedItem(voce)

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
        parti = [brano.percorso if dati.get("completo") else brano.nome_del_file]
        if brano.sottobrano:
            info = songlengths.info_del_sid(brano.percorso)
            parti[0] += f", sottobrano {brano.sottobrano} di {info['sottobrani'] if info else '?'}"
        parti.extend(self._durata_nella_plancia(brano))
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

    def _durata_nella_plancia(self, brano):
        """La durata da mostrare accanto al brano, se si sa: per un SID con piu'
        sottobrani, quanti sono e quanto durano in tutto."""
        if self._ha_sottobrani(brano):
            totale = songlengths.info_del_sid(brano.percorso)["sottobrani"]
            durate = (self.schedario.scheda(brano.percorso) or {}).get("durate_sid")
            return [f"{totale} sottobrani" + (f", {durata_lunga(sum(durate))} in tutto" if durate else "")]
        durata = self.schedario.durata(brano)
        return [durata_lunga(durata)] if durata is not None else []

    def _aggiungi_voce(self, genitore, tipo, pl, brano, completo=False):
        """Aggiunge alla plancia un brano (di una playlist) o un file (di una
        cartella); un SID con piu' sottobrani diventa un ramo da aprire. Con
        completo l'etichetta ha il percorso intero, come nei Risultati."""
        dati = {"tipo": tipo, "playlist": pl, "brano": brano}
        if completo:
            dati["completo"] = True
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

    def _filtro_di(self, pl):
        """Il filtro compilato della playlist, o None se non ne ha. Un testo
        che non si capisce, arrivato per esempio da un file scritto a mano,
        vale come nessun filtro."""
        if not pl.filtro:
            return None
        testo, compilato = self._filtri.get(id(pl), (None, None))
        if testo != pl.filtro:
            try:
                compilato = Filtro(pl.filtro)
            except ErroreFiltro:
                compilato = None
            self._filtri[id(pl)] = (pl.filtro, compilato)
        return compilato

    def _ammesso(self, pl, brano):
        """Vero se il brano passa il filtro della sua playlist."""
        filtro = self._filtro_di(pl)
        return filtro is None or filtro.ammette(brano, self.schedario.scheda(brano.percorso))

    def _comando_filtro(self):
        """La barra verticale: il filtro della playlist, o dei Preferiti, in
        cui sta il fuoco della plancia, anche se il fuoco della tastiera e'
        in un'altra area."""
        voce = self._voce_corrente()
        while voce.IsOk() and voce != self.albero.GetRootItem():
            dati = self._dati(voce) or {}
            if dati.get("tipo") == "playlist":
                self._modifica_filtro(dati["playlist"])
                return
            voce = self.albero.GetItemParent(voce)
        self._riscontro("non_disponibile", "Il filtro c'è nelle playlist e nei Preferiti: porta la plancia su una playlist o su un suo brano.")

    def _modifica_filtro(self, pl):
        """Il campo del filtro; se il testo non si capisce lo spiega e lo ripropone."""
        testo = pl.filtro
        while True:
            self._suono("domanda")
            with FinestraFiltro(self, f"Filtro di {pl.nome}", testo, ISTRUZIONI_DEL_FILTRO) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self.scrivi("Filtro non cambiato.")
                    return
                testo = " ".join(dialogo.testo.split())
            try:
                Filtro(testo)
            except ErroreFiltro as e:
                self._riscontro("errore", f"Nel filtro non capisco: {e}")
                continue
            break
        self._imposta_filtro(pl, testo)

    def _imposta_filtro(self, pl, testo):
        # Il fuoco della plancia resta sulla sua voce; un brano che il filtro
        # nuovo nasconde lascia il posto alla sua playlist.
        dati = self._dati(self._voce_corrente()) or {}
        dentro = dati.get("playlist") is pl
        brano = dati.get("brano") if dentro else None
        pl.filtro = testo
        self._salva_archivio()
        self._chiedi_schede(pl)
        if brano is not None and self._ammesso(pl, brano):
            self._popola_playlist(seleziona=brano)
            self._al_sottobrano(dati.get("numero"))
        else:
            self._popola_playlist(seleziona=pl if dentro else None)
        passano = sum(1 for b in pl.brani if self._ammesso(pl, b))
        if testo:
            self._riscontro("filtro_messo", f"Filtro di {pl.nome}: {testo}. Passano {brani_al_plurale(passano)} su {len(pl.brani)}.")
        else:
            self._riscontro("filtro_tolto", f"Filtro di {pl.nome} svuotato: passano tutti i {brani_al_plurale(len(pl.brani))}.")

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

    def _etichetta_della_cartella(self, cartella):
        """Il nome della cartella con quanti file suonabili ha, sottocartelle
        comprese, e quanto durano in tutto, appena il contatore e lo schedario
        lo sanno."""
        nome = os.path.basename(cartella.rstrip("\\")) or cartella
        files = self.contatore.files(cartella)
        if not files:
            return nome
        durate = [(self.schedario.scheda(f) or {}).get("durata") for f in files]
        note = [d for d in durate if d is not None]
        testo = f"{nome}, {len(files)} file"
        if note:
            testo += f", {durata_lunga(sum(note))} in tutto"
            if len(note) < len(files):
                testo += f", {len(files) - len(note)} senza durata"
        return testo

    def _aggiorna_cartelle(self):
        """Rinfresca le etichette delle cartelle caricate nella plancia, e
        toglie quelle che il contatore ha trovato senza niente da suonare,
        sottocartelle comprese, anche se il fuoco ci sta sopra o dentro."""
        vuote = set()
        for voce in self._tutte_le_voci(self.nodo_pc):
            dati = self._dati(voce) or {}
            if dati.get("tipo") != "cartella":
                continue
            # Una cartella aperta che mostra dei file non e' vuota, qualunque
            # cosa dica un conto fatto su una lettura vecchia.
            mostra_file = dati.get("caricato") and any((self._dati(f) or {}).get("tipo") == "file" for f in self._figli(voce))
            if self.contatore.files(dati["percorso"]) == [] and not mostra_file:
                # Le voci arrivano prima dei loro figli: basta togliere il
                # ramo piu' in alto.
                if not self._dentro_una_di(voce, vuote):
                    vuote.add(voce)
                continue
            nuova = self._etichetta_della_cartella(dati["percorso"])
            if self.albero.GetItemText(voce) != nuova:
                self.albero.SetItemText(voce, nuova)
        if vuote:
            self._togli_dalla_plancia(vuote)

    def _togli_dalla_plancia(self, voci):
        """Toglie dalla plancia dei rami interi. Se il fuoco stava su uno di
        loro o dentro, passa prima alla voce vicina che resta."""
        corrente = self._voce_corrente()
        if corrente.IsOk() and self._dentro_una_di(corrente, voci):
            approdo = self._approdo(voci)
            if approdo is not None:
                self._seleziona(approdo)
        for voce in voci:
            self.albero.Delete(voce)

    def _dentro_una_di(self, voce, rami):
        """Vero se la voce e' uno dei rami, un insieme di voci, o sta dentro
        uno di loro: si risale una volta sola, anche con migliaia di rami."""
        radice = self.albero.GetRootItem()
        while voce.IsOk() and voce != radice:
            if voce in rami:
                return True
            voce = self.albero.GetItemParent(voce)
        return False

    def _approdo(self, togliere):
        """Dove resta il fuoco quando le voci togliere spariscono dalla
        plancia, con tutto cio' che contengono: sulla voce che ce l'ha, se
        resta; altrimenti sulla prima voce sorella che resta, prima in avanti
        e poi all'indietro, oppure sul ramo che la contiene, salendo finche'
        serve. None se non resta niente."""
        togliere = set(togliere)

        def sparisce(voce):
            return self._dentro_una_di(voce, togliere)

        radice = self.albero.GetRootItem()
        voce = self._voce_corrente()
        while voce.IsOk() and voce != radice:
            if not sparisce(voce):
                return voce
            for passo in (self.albero.GetNextSibling, self.albero.GetPrevSibling):
                vicina = passo(voce)
                while vicina.IsOk() and sparisce(vicina):
                    vicina = passo(vicina)
                if vicina.IsOk():
                    return vicina
            voce = self.albero.GetItemParent(voce)
        return None

    def _conti_arrivati(self):
        if not self._chiusa:
            self._aggiorna_cartelle()

    def _etichetta_della_playlist(self, pl):
        """Nome, brani che passano il filtro, brani totali e il filtro, se
        c'e': il filtro non e' una voce della playlist, cosi' NVDA conta solo
        i brani."""
        filtrati = [b for b in pl.brani if self._ammesso(pl, b)]
        etichetta = f"{pl.nome}, brani: {self._conto(filtrati)}, totali: {self._conto(pl.brani)}"
        return f"{etichetta}, filtro: {pl.filtro}" if pl.filtro else etichetta

    def _chiedi_schede(self, *playlist):
        """Chiede allo schedario le schede dei brani delle playlist date."""
        self.schedario.chiedi([b.percorso for pl in playlist for b in pl.brani])

    def _schede_arrivate(self):
        """Lo schedario ha letto nuove schede: si rinfrescano le etichette
        delle playlist e, a coda vuota, lo schedario si salva."""
        if self._chiusa:
            return
        # Le schede nuove possono cambiare cosa passa i filtri che guardano
        # durate e tag: per non cambiare la plancia sotto le mani di chi la
        # sta leggendo si rinfrescano solo i conti; l'elenco dei brani si
        # aggiorna riaprendo la playlist.
        for voce in [self.nodo_preferiti, *self._figli(self.nodo_playlist)]:
            dati = self._dati(voce) or {}
            if dati.get("tipo") == "playlist":
                nuova = self._etichetta_della_playlist(dati["playlist"])
                if self.albero.GetItemText(voce) != nuova:
                    self.albero.SetItemText(voce, nuova)
        self._aggiorna_etichette()
        self._aggiorna_cartelle()
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
        voce_selezionata = self._voce_corrente()
        dentro = False
        # Le altre voci selezionate delle playlist e dei Preferiti, per
        # riselezionarle dopo: una selezione multipla non va persa.
        altre_selezionate = set()
        for voce in self._voci_selezionate():
            if voce != voce_selezionata and (self._sotto(voce, self.nodo_playlist) or self._sotto(voce, self.nodo_preferiti)):
                dati = self._dati(voce) or {}
                oggetto = dati.get("brano") if dati.get("tipo") == "brano" else dati.get("playlist") if dati.get("tipo") == "playlist" else None
                if oggetto is not None:
                    altre_selezionate.add(id(oggetto))
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
            self._seleziona(self.nodo_playlist)
        preferiti = self.archivio.preferiti
        self.albero.SetItemText(self.nodo_preferiti, self._etichetta_della_playlist(preferiti))
        self.albero.DeleteChildren(self.nodo_preferiti)
        self._dati(self.nodo_preferiti)["caricato"] = False
        self.albero.SetItemHasChildren(self.nodo_preferiti, True)
        da_selezionare = None
        if selezionato is preferiti:
            da_selezionare = self.nodo_preferiti
        if preferiti_aperti or (isinstance(selezionato, Brano) and preferiti.indice(selezionato) is not None):
            self.albero.Expand(self.nodo_preferiti)
            if isinstance(selezionato, Brano):
                da_selezionare = next((v for v in self._figli(self.nodo_preferiti) if self._dati(v).get("brano") is selezionato), da_selezionare)
        self.albero.DeleteChildren(self.nodo_playlist)
        for pl in self.archivio.playlist:
            nodo = self.albero.AppendItem(self.nodo_playlist, self._etichetta_della_playlist(pl), data={"tipo": "playlist", "playlist": pl, "caricato": False})
            self.albero.SetItemHasChildren(nodo, True)
            if pl is selezionato:
                da_selezionare = nodo
            elif isinstance(selezionato, Brano) and pl.indice(selezionato) is not None:
                aperte.add(id(pl))
            if id(pl) in aperte:
                self.albero.Expand(nodo)
                if isinstance(selezionato, Brano):
                    da_selezionare = next((v for v in self._figli(nodo) if self._dati(v).get("brano") is selezionato), da_selezionare)
        comando = self.albero.AppendItem(self.nodo_playlist, "Nuova playlist", data={"tipo": "comando", "comando": "nuova_playlist"})
        if selezionato == "nuova_playlist":
            da_selezionare = comando
        if dentro:
            if da_selezionare is None or self._sotto(da_selezionare, self.nodo_playlist):
                self.albero.Expand(self.nodo_playlist)
            self._seleziona(da_selezionare or self.nodo_playlist)
        if altre_selezionate:
            for radice in (self.nodo_preferiti, self.nodo_playlist):
                for voce in self._tutte_le_voci(radice):
                    dati = self._dati(voce) or {}
                    oggetto = dati.get("brano") if dati.get("tipo") == "brano" else dati.get("playlist") if dati.get("tipo") == "playlist" else None
                    if oggetto is not None and id(oggetto) in altre_selezionate:
                        self.albero.SelectItem(voce)

    def _in_espansione(self, evento):
        voce = evento.GetItem()
        dati = self._dati(voce)
        # Una playlist aperta senza brani da mostrare non resta aperta, e
        # quindi non si chiude: si ricarica ogni volta che la si riapre.
        vuota = dati and dati.get("tipo") == "playlist" and not self.albero.GetChildrenCount(voce, False)
        if dati and (dati.get("caricato") is False or vuota):
            self._carica(voce, dati)

    def _chiusa_una_voce(self, evento):
        """Una playlist chiusa si ricarica alla prossima apertura: cosi' le
        schede arrivate nel frattempo cambiano anche l'elenco dei brani che
        passano il filtro, non solo i conti dell'etichetta."""
        evento.Skip()
        dati = self._dati(evento.GetItem()) or {}
        if dati.get("tipo") == "playlist":
            dati["caricato"] = False

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
        if tipo in ("risultati", "gruppo_risultati"):
            self._riempi_gruppo(voce)
            return
        if tipo == "playlist":
            pl = dati["playlist"]
            for brano in pl.brani:
                if self._ammesso(pl, brano):
                    self._aggiungi_voce(voce, "brano", pl, brano)
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
        # La lettura appena fatta vale piu' di quella che il contatore tiene
        # per la sessione: se sono diverse, i conti di questa cartella e di
        # chi la contiene si rifanno.
        self.contatore.chiedi(self.contatore.rinfresca(dati["percorso"], (cartelle, files)))
        # Le cartelle che il contatore sa gia' senza niente da suonare, nemmeno
        # sotto, non si mostrano; le altre spariscono quando arriva il conto.
        cartelle = [c for c in cartelle if self.contatore.files(c) != []]
        for cartella in cartelle:
            figlio = self.albero.AppendItem(voce, self._etichetta_della_cartella(cartella), data={"tipo": "cartella", "percorso": cartella, "caricato": False})
            self.albero.SetItemHasChildren(figlio, True)
        self.contatore.chiedi(cartelle)
        pl = self._temporanea(dati["percorso"], files)
        self._chiedi_schede(pl)
        for brano in pl.brani:
            self._aggiungi_voce(voce, "file", pl, brano)
        if not cartelle and not files:
            self.albero.SetItemHasChildren(voce, False)
            self._riscontro("cartella_aperta", "Niente da suonare qui dentro.")
        else:
            self._suono("cartella_aperta")

    def _aggiorna_cartella(self, cartella):
        """Aggiorna dal menu: la voce si cerca quando la si sceglie, perche'
        mentre il menu e' aperto una cartella vuota puo' sparire."""
        voce = next((v for v in self._tutte_le_voci(self.nodo_pc) if (self._dati(v) or {}).get("percorso") == cartella), None)
        if voce is None:
            self._riscontro("non_disponibile", f"{cartella} non è più nella plancia: dentro non c'è niente da suonare.")
            return
        self._aggiorna_ramo(voce)

    def _aggiorna_ramo(self, voce):
        dati = self._dati(voce)
        if dati.get("tipo") == "pc":
            self.contatore.dimentica_tutto()
        elif dati.get("percorso"):
            self.contatore.dimentica(dati["percorso"])
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
        if len(self._voci_selezionate()) > 1:
            self._menu(voce)
        elif dati and dati["tipo"] == "comando":
            getattr(self, f"_comando_{dati['comando']}")()
        elif dati and dati["tipo"] == "altri":
            self._altri_risultati()
        else:
            self._menu(voce)

    def _menu_da_evento(self, evento):
        self._menu(evento.GetItem())

    def _menu(self, voce):
        dati = self._dati(voce)
        if not dati:
            return
        voci = self._voci_del_menu_della_selezione() if len(self._voci_selezionate()) > 1 else self._voci_del_menu(dati)
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
        if tipo == "risultati":
            return [("Riproduci", lambda: self._riproduci_playlist(self.risultati)), ("Salva come playlist", self._salva_risultati),
                ("Nuova ricerca", self._ricerca_globale), ("Ferma la ricerca", self._ferma_ricerca)]
        if tipo == "altri":
            return [("Mostra altri risultati", self._altri_risultati)]
        if tipo == "gruppo_risultati":
            gruppo = dati["gruppo"]
            return [("Salva come playlist", lambda: self._salva_risultati(gruppo))]
        if tipo == "playlist":
            pl = dati["playlist"]
            voci = [("Riproduci", lambda: self._riproduci_playlist(pl)), ("Filtro", lambda: self._modifica_filtro(pl))]
            if pl.filtro:
                voci.append(("Togli il filtro", lambda: self._imposta_filtro(pl, "")))
            if pl is not self.archivio.preferiti:
                voci += [("Rinomina", lambda: self._rinomina(pl)), ("Elimina", lambda: self._elimina_playlist(pl))]
            return voci
        if tipo == "brano":
            pl, brano = dati["playlist"], dati["brano"]
            return [("Riproduci", lambda: self._riproduci(pl, brano)),
                ("Sposta su", lambda: self._sposta(pl, brano, "su")), ("Sposta giù", lambda: self._sposta(pl, brano, "giu")),
                ("Sposta in cima", lambda: self._sposta(pl, brano, "cima")), ("Sposta in fondo", lambda: self._sposta(pl, brano, "fondo")),
                ("Saltato", (lambda: self._salta(pl, brano), brano.saltato)), ("Togli dalla playlist", lambda: self._togli(pl, brano)),
                ("Aggiungi ai preferiti", lambda: self._ai_preferiti(brano)), ("Manda nel cestino", lambda: self._al_cestino(self._voce_corrente()))]
        if tipo == "pc":
            return [("Aggiorna", lambda: self._aggiorna_ramo(self.nodo_pc))]
        if tipo in ("unita", "cartella"):
            cartella = dati["percorso"]
            nome = dati.get("etichetta", "").split("\\", 1)[-1] if tipo == "unita" else os.path.basename(cartella)
            return [("Riproduci", lambda: self._riproduci_cartella(cartella)), ("Crea playlist da qui", lambda: self._crea_da_qui(cartella, nome)),
                ("Aggiungi alla playlist", self._menu_aggiungi(lambda: [Brano(p) for p in questo_pc.file_ricorsivi(cartella)])),
                ("Aggiorna", lambda: self._aggiorna_cartella(cartella))]
        if tipo == "file":
            pl, brano = dati["playlist"], dati["brano"]
            return [("Riproduci", lambda: self._riproduci(pl, brano)), ("Aggiungi alla playlist", self._menu_aggiungi(lambda: [Brano(brano.percorso)])),
                ("Aggiungi ai preferiti", lambda: self._ai_preferiti(brano)), ("Manda nel cestino", lambda: self._al_cestino(self._voce_corrente()))]
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
            if pl is self.risultati:
                self._togli_dai_risultati(voce, brano)
            self._seleziona(vicina if vicina.IsOk() else genitore)
            self.albero.Delete(voce)
            if pl is self.risultati:
                self._aggiorna_risultati()
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

    # La selezione multipla.

    def _voci_selezionate(self):
        return [v for v in self.albero.GetSelections() if v.IsOk()]

    def _brani_della_voce(self, voce):
        """Cosa contiene una voce, come terne (playlist, brano, sottobrano):
        un ramo vale per tutto cio' che ha dentro, anche se e' chiuso."""
        dati = self._dati(voce) or {}
        tipo = dati.get("tipo")
        if tipo in ("brano", "file"):
            return [(dati["playlist"], dati["brano"], None)]
        if tipo == "sottobrano":
            return [(dati["playlist"], dati["brano"], dati["numero"])]
        if tipo == "playlist":
            pl = dati["playlist"]
            return [(pl, b, None) for b in pl.brani if self._ammesso(pl, b)]
        if tipo == "radice_playlist":
            return [(pl, b, None) for pl in self.archivio.playlist for b in pl.brani if self._ammesso(pl, b)]
        if tipo in ("cartella", "unita"):
            with wx.BusyCursor():
                contenuti = questo_pc.contenuti_ricorsivi(dati["percorso"])
            terne = []
            for cartella, files in contenuti:
                pl = self._temporanea(cartella, files)
                terne.extend((pl, b, None) for b in pl.brani)
            return terne
        if tipo in ("risultati", "gruppo_risultati"):
            return [(self.risultati, b, None) for b in self._brani_del_gruppo(dati["gruppo"])]
        return []

    def _brani_della_selezione(self):
        """I brani di tutte le voci selezionate, nell'ordine della plancia e
        senza doppioni: una voce dentro un ramo selezionato conta una volta."""
        visti = set()
        terne = []
        for voce in self._voci_selezionate():
            for pl, brano, sottobrano in self._brani_della_voce(voce):
                chiave = (id(brano), sottobrano)
                if chiave not in visti:
                    visti.add(chiave)
                    terne.append((pl, brano, sottobrano))
        return terne

    def _copie_della_selezione(self):
        """I brani della selezione come brani nuovi, per playlist e Preferiti."""
        return [Brano(b.percorso, sottobrano=n or b.sottobrano) for _pl, b, n in self._brani_della_selezione()]

    def _suona_selezione(self):
        """X su piu' voci: la selezione diventa una playlist invisibile, che
        vive finche' non si preme V. I brani sono quelli della plancia, cosi'
        l'indicazione in riproduzione e F8 funzionano; un sottobrano diventa
        un brano a se'."""
        terne = self._brani_della_selezione()
        brani = [b if n is None else Brano(b.percorso, sottobrano=n) for _pl, b, n in terne]
        pl = Playlist("Selezione", brani, cartella="")
        pl.selezione = True
        primo = self.coda.primo(pl)
        if primo is None:
            self._riscontro("niente_da_suonare", "Nella selezione non c'è niente da suonare.")
            return
        self._suona(pl, primo)

    def _voci_del_menu_della_selezione(self):
        n = len(self._voci_selezionate())
        return [(f"Riproduci le {n} voci selezionate", self._suona_selezione), ("Crea playlist dalla selezione", self._crea_dalla_selezione),
            ("Aggiungi alla playlist", self._menu_aggiungi(self._copie_della_selezione)), ("Aggiungi ai preferiti", self._selezione_ai_preferiti),
            ("Togli dalle playlist, ed elimina le playlist selezionate", self._cancella_selezione), ("Manda nel cestino", self._cestina_selezione)]

    def _crea_dalla_selezione(self):
        brani = self._copie_della_selezione()
        if not brani:
            self._riscontro("niente_da_suonare", "Nella selezione non c'è niente da mettere in una playlist.")
            return
        with DialogoTesto(self, "Nome della nuova playlist:", "Crea playlist dalla selezione", "Selezione") as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            nome = dialogo.GetValue().strip() or "Selezione"
        self._aggiungi(None, brani, nome=nome)

    def _f4(self):
        if len(self._voci_selezionate()) > 1:
            self._selezione_ai_preferiti()
        else:
            self._ai_preferiti(self._preferito_selezionato())

    def _selezione_ai_preferiti(self):
        nuovi = [b for b in self._copie_della_selezione() if not self.archivio.nei_preferiti(b)]
        gia = len(self._brani_della_selezione()) - len(nuovi)
        if not nuovi:
            self._riscontro("gia_nei_preferiti", "I brani selezionati sono già tutti nei Preferiti.")
            return
        self.archivio.preferiti.brani.extend(nuovi)
        self._chiedi_schede(self.archivio.preferiti)
        self._salva_archivio()
        self._popola_playlist()
        altri = f"; {gia} c'erano già" if gia else ""
        self._riscontro("preferito_aggiunto", f"Aggiunti ai Preferiti {brani_al_plurale(len(nuovi))}{altri}.")

    def _cancella_selezione(self):
        """Canc su piu' voci: toglie i brani dalle loro playlist ed elimina le
        playlist selezionate, dopo una conferma. Il fuoco resta li' dove si
        lavorava, sulla prima voce vicina che resta."""
        voci = [(v, self._dati(v) or {}) for v in self._voci_selezionate()]
        da_eliminare = [d["playlist"] for _v, d in voci if d.get("tipo") == "playlist" and d["playlist"] in self.archivio.playlist]
        da_togliere = [(v, d["playlist"], d["brano"]) for v, d in voci if d.get("tipo") == "brano" and d["playlist"] not in da_eliminare]
        if not (da_eliminare or da_togliere):
            self._riscontro("non_disponibile", "Nella selezione non c'è niente che Canc possa togliere: brani di playlist o playlist.")
            return
        if da_eliminare and not self._conferma(f"Eliminare {len(da_eliminare)} playlist? I file restano sul disco.", "Elimina playlist"):
            self.scrivi("Eliminazione annullata.")
            return
        approdo = self._approdo([v for v, d in voci if d.get("tipo") == "playlist" and d["playlist"] in da_eliminare] + [v for v, _pl, _b in da_togliere])
        for pl in da_eliminare:
            self.archivio.elimina(pl)
        for _voce, pl, brano in da_togliere:
            pl.togli(brano)
            if self.coda.loop_playlist is pl and brano in (self.coda.punto_a, self.coda.punto_b):
                self.coda.togli_loop()
        self._salva_archivio()
        self._ricostruisci_dopo_la_cancellazione(approdo)
        parti = []
        if da_togliere:
            parti.append(f"tolti {brani_al_plurale(len(da_togliere))}")
        if da_eliminare:
            parti.append(f"eliminate {len(da_eliminare)} playlist")
        self._riscontro("brano_tolto", ", ".join(parti).capitalize() + ".")

    def _ricostruisci_dopo_la_cancellazione(self, approdo, voci_da_togliere=()):
        """Dopo una cancellazione: toglie dalla plancia le voci delle cartelle
        e dei Risultati, ricostruisce il ramo Playlist e rimette il fuoco
        sull'approdo, da solo nella selezione. Le voci delle playlist e dei
        Preferiti rinascono, e si ritrovano dal brano o dalla playlist che
        mostrano; le altre restano le stesse."""
        rinasce = approdo is not None and approdo not in (self.nodo_preferiti, self.nodo_playlist) and (
            self._sotto(approdo, self.nodo_preferiti) or self._sotto(approdo, self.nodo_playlist))
        oggetto = numero = None
        if rinasce:
            dati = self._dati(approdo) or {}
            oggetto = "nuova_playlist" if dati.get("comando") == "nuova_playlist" else (dati.get("brano") or dati.get("playlist"))
            numero = dati.get("numero")
        self.albero.UnselectAll()
        if approdo is not None and not rinasce:
            self._seleziona(approdo)
        for voce in voci_da_togliere:
            self.albero.Delete(voce)
        self._popola_playlist(seleziona=oggetto)
        self._al_sottobrano(numero)
        if approdo is not None and not rinasce:
            self._seleziona(approdo)

    def _al_sottobrano(self, numero):
        """Dopo una ricostruzione che ha ritrovato il SID, riapre il SID e
        porta il fuoco sul sottobrano numero, se c'era."""
        voce = self._voce_corrente()
        dati = self._dati(voce) or {}
        if not numero or dati.get("tipo") != "brano" or not self.albero.ItemHasChildren(voce):
            return
        self.albero.Expand(voce)
        figlio = next((v for v in self._figli(voce) if (self._dati(v) or {}).get("numero") == numero), None)
        if figlio is not None:
            self._seleziona(figlio)

    def _cestina_selezione(self):
        """Maiuscolo+Canc su piu' voci: i file dei brani e dei file selezionati
        vanno nel cestino, dopo una sola conferma."""
        voci = [(v, self._dati(v) or {}) for v in self._voci_selezionate()]
        bersagli = [(v, d["playlist"], d["brano"]) for v, d in voci if d.get("tipo") in ("brano", "file")]
        if not bersagli:
            self._riscontro("non_disponibile", "Maiuscolo+Canc manda nel cestino i file: seleziona brani o file.")
            return
        if not self._conferma(f"Mandare nel cestino di Windows {len(bersagli)} file? I brani escono anche dalle loro playlist.", "Manda nel cestino"):
            self.scrivi("I file restano dove sono.")
            return
        riusciti, falliti = 0, 0
        cestinate, cancellate = [], []
        for voce, pl, brano in bersagli:
            if self.motore.in_corso == brano.percorso:
                self.motore.stop()
            if not questo_pc.nel_cestino(brano.percorso):
                falliti += 1
                continue
            riusciti += 1
            pl.togli(brano)
            if pl is self.risultati:
                self._togli_dai_risultati(voce, brano)
            cestinate.append(voce)
            if pl.temporanea:
                cancellate.append(voce)
        approdo = self._approdo(cestinate)
        self._salva_archivio()
        self._ricostruisci_dopo_la_cancellazione(approdo, cancellate)
        if any(pl is self.risultati for _v, pl, _b in bersagli):
            self._aggiorna_risultati()
        testo = f"Nel cestino di Windows {riusciti} file."
        if falliti:
            testo += f" {falliti} non ci sono andati."
        self._riscontro("cestino", testo)

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

    def _aggiungi(self, pl, percorsi_da_aggiungere, nome=None):
        if not percorsi_da_aggiungere:
            self._riscontro("niente_da_suonare", "Non c'è niente da aggiungere: nessun file supportato.")
            return
        nuova = pl is None
        if nuova:
            pl = self.archivio.nuova(nome)
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
        dati = self._dati(self._voce_corrente()) or {}
        if dati.get("tipo") == "sottobrano":
            return Brano(dati["brano"].percorso, sottobrano=dati["numero"])
        if dati.get("tipo") in ("brano", "file"):
            return dati["brano"]
        return None

    # La ricerca globale.

    def _comando_ricerca(self):
        """La barra rovesciata: dalla console cerca nella console, da ogni
        altro punto fa la ricerca in tutto MeTeOra."""
        if wx.Window.FindFocus() is self.console:
            self._comando_cerca_in_console()
        else:
            self._ricerca_globale()

    def _ricerca_globale(self):
        """Il campo della ricerca, uguale a quello del filtro; con Invio parte
        la ricerca e i Risultati si riempiono mentre procede."""
        testo = self._testo_della_ricerca
        while True:
            self._suono("domanda")
            with FinestraFiltro(self, "Ricerca in tutto MeTeOra", testo, ISTRUZIONI_DELLA_RICERCA) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self.scrivi("Ricerca annullata.")
                    return
                testo = " ".join(dialogo.testo.split())
            if not testo:
                self._riscontro("errore", "Scrivi cosa cercare.")
                continue
            try:
                filtro = Filtro(testo)
            except ErroreFiltro as e:
                self._riscontro("errore", f"Nella ricerca non capisco: {e}")
                continue
            break
        self._avvia_ricerca(testo, filtro)

    def _avvia_ricerca(self, testo, filtro, unita=None):
        if self._ricerca is not None:
            self._ricerca.ferma()
        self._testo_della_ricerca = testo
        self.risultati = Playlist("Risultati", cartella="")
        self._risultati_letti = 0
        brani = [(b, "Preferiti") for b in self.archivio.preferiti.brani]
        brani += [(b, f"Playlist {pl.nome}") for pl in self.archivio.playlist for b in pl.brani]
        self._ricerca = Ricerca(filtro, brani, self.schedario, avvisa=lambda: wx.CallAfter(self._risultati_arrivati), unita=unita)
        self._albero_dei_risultati = AlberoDeiRisultati(dict(questo_pc.unita()))
        if self.nodo_risultati is None:
            self.nodo_risultati = self.albero.InsertItem(self.albero.GetRootItem(), self.nodo_preferiti, "Risultati")
        else:
            self.albero.Collapse(self.nodo_risultati)
            self.albero.DeleteChildren(self.nodo_risultati)
        self.albero.SetItemData(self.nodo_risultati, self._dati_del_gruppo("risultati", self._albero_dei_risultati.radice))
        self.albero.SetItemHasChildren(self.nodo_risultati, True)
        self._aggiorna_risultati()
        self._ricerca.avvia()
        self._riscontro("ricerca_avviata", f"Cerco {testo} nelle playlist e nelle unità. I Risultati si riempiono mentre cerco.")

    def _etichetta_dei_risultati(self):
        trovati = self._ricerca.quanti() if self._ricerca else 0
        stato = "" if self._ricerca is None or self._ricerca.finita else (", ricerca fermata" if self._ricerca.fermata else ", ricerca in corso")
        return f"Risultati di {self._testo_della_ricerca}: {trovati} {'trovato' if trovati == 1 else 'trovati'}{stato}"

    def _dati_del_gruppo(self, tipo, gruppo):
        """I dati di un ramo dei Risultati: quanti suoi rami e brani sono gia'
        nella plancia, e fin dove arriva la sua pagina."""
        return {"tipo": tipo, "playlist": self.risultati, "gruppo": gruppo, "caricato": False, "rami": 0, "brani": 0,
            "pagina": PAGINA_DEI_RISULTATI}

    def _etichetta_del_gruppo(self, gruppo):
        return f"{gruppo.nome}, {gruppo.totale} {'risultato' if gruppo.totale == 1 else 'risultati'}"

    def _aggiorna_risultati(self):
        """Porta dentro i risultati nuovi della ricerca: nella playlist, nel
        loro ramo dell'albero e, per i rami gia' aperti, nella plancia."""
        if self._ricerca is None:
            return
        # Si riparte da quanti risultati sono gia' arrivati, non da quanti
        # ne restano: quelli andati nel cestino non tornano.
        quanti = self._ricerca.quanti()
        for brano, origine in self._ricerca.pezzo(self._risultati_letti, quanti):
            self.risultati.brani.append(brano)
            self._albero_dei_risultati.aggiungi(brano, origine)
        self._risultati_letti = max(self._risultati_letti, quanti)
        self.albero.SetItemText(self.nodo_risultati, self._etichetta_dei_risultati())
        for voce in [self.nodo_risultati, *self._tutte_le_voci(self.nodo_risultati)]:
            dati = self._dati(voce) or {}
            if dati.get("tipo") == "gruppo_risultati":
                self.albero.SetItemText(voce, self._etichetta_del_gruppo(dati["gruppo"]))
            if dati.get("tipo") in ("risultati", "gruppo_risultati") and dati.get("caricato"):
                self._riempi_gruppo(voce)

    def _togli_dai_risultati(self, voce, brano):
        """Un risultato andato nel cestino esce anche dal suo ramo, e il ramo
        della plancia che lo mostrava ne mostra uno di meno."""
        tolto = self._albero_dei_risultati.togli(brano) if self._albero_dei_risultati is not None else None
        ramo = self._dati(self.albero.GetItemParent(voce)) or {}
        if tolto is not None and ramo.get("tipo") in ("risultati", "gruppo_risultati") and tolto[1] < ramo["brani"]:
            ramo["brani"] -= 1

    def _riempi_gruppo(self, voce):
        """Porta nella plancia cio' che manca di un ramo dei Risultati: prima
        i rami che contiene, poi i suoi brani fino alla pagina, e in fondo la
        voce per vederne altri se ce ne sono. Si puo' chiamare di nuovo quando
        arrivano risultati nuovi: aggiunge soltanto."""
        dati = self._dati(voce)
        dati["caricato"] = True
        gruppo = dati["gruppo"]
        figli = list(self._figli(voce))
        if figli and (self._dati(figli[-1]) or {}).get("tipo") == "altri":
            self.albero.Delete(figli[-1])
        for sotto in gruppo.elenco_dei_gruppi[dati["rami"]:]:
            ramo = self.albero.InsertItem(voce, dati["rami"], self._etichetta_del_gruppo(sotto), data=self._dati_del_gruppo("gruppo_risultati", sotto))
            self.albero.SetItemHasChildren(ramo, True)
            dati["rami"] += 1
        for brano in gruppo.brani[dati["brani"]:dati["pagina"]]:
            self._aggiungi_voce(voce, "file", self.risultati, brano)
            dati["brani"] += 1
        restano = len(gruppo.brani) - dati["brani"]
        if restano > 0:
            testo = "Mostra l'ultimo risultato" if restano == 1 else f"Mostra altri {min(restano, PAGINA_DEI_RISULTATI)} risultati, ne restano {restano}"
            self.albero.AppendItem(voce, testo, data={"tipo": "altri", "ramo": voce})

    def _altri_risultati(self):
        altri = self._voce_corrente()
        ramo = (self._dati(altri) or {}).get("ramo")
        if ramo is None:
            return
        dati = self._dati(ramo)
        prima = dati["rami"] + dati["brani"]
        dati["pagina"] += PAGINA_DEI_RISULTATI
        self._riempi_gruppo(ramo)
        # La selezione va sul primo dei risultati appena mostrati.
        figli = list(self._figli(ramo))
        if len(figli) > prima:
            self._seleziona(figli[prima])
        self._riscontro("altri_risultati", f"Mostrati {dati['brani']} risultati su {len(dati['gruppo'].brani)} in {dati['gruppo'].nome}.")

    def _risultati_arrivati(self):
        if self._chiusa or self._ricerca is None:
            return
        self._aggiorna_risultati()
        if self._ricerca.finita:
            self._riscontro("ricerca_finita", f"Ricerca di {self._testo_della_ricerca} finita: {len(self.risultati.brani)} risultati.")
            self._chiedi_schede(self.risultati)

    def _ferma_ricerca(self):
        if self._ricerca is None or self._ricerca.finita or self._ricerca.fermata:
            self._riscontro("non_disponibile", "Non c'è una ricerca in corso.")
            return
        self._ricerca.ferma()
        self._aggiorna_risultati()
        self._riscontro("ricerca_fermata", f"Ricerca fermata: {len(self.risultati.brani)} risultati.")

    def _brani_del_gruppo(self, gruppo):
        """I risultati di un ramo e di tutti quelli che contiene, in ordine."""
        brani = list(gruppo.brani)
        for sotto in gruppo.elenco_dei_gruppi:
            brani.extend(self._brani_del_gruppo(sotto))
        return brani

    def _salva_risultati(self, gruppo=None):
        """Salva come playlist tutti i Risultati, o soltanto un loro ramo."""
        if not self.risultati or not self.risultati.brani:
            self._riscontro("niente_da_suonare", "Non ci sono risultati da salvare.")
            return
        proposta = f"Ricerca {self._testo_della_ricerca}" if gruppo is None else f"{gruppo.nome} {self._testo_della_ricerca}"
        with DialogoTesto(self, "Nome della nuova playlist:", "Salva i risultati", proposta) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            nome = dialogo.GetValue().strip() or "Ricerca"
        self._aggiorna_risultati()
        brani = self.risultati.brani if gruppo is None else self._brani_del_gruppo(gruppo)
        self._aggiungi(None, [Brano(b.percorso, sottobrano=b.sottobrano) for b in brani], nome=nome)

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
        with DialogoTesto(self, "Nuovo nome della playlist:", "Rinomina", pl.nome) as dialogo:
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
        # Il fuoco va sul brano che seguiva, o se non c'e' su quello prima,
        # fra quelli che il filtro lascia vedere; senza brani, sulla playlist.
        dopo = [b for b in pl.brani[i:] if self._ammesso(pl, b)]
        prima = [b for b in pl.brani[:i] if self._ammesso(pl, b)]
        vicino = dopo[0] if dopo else prima[-1] if prima else pl
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
        if getattr(pl, "selezione", False):
            dove = f"{numero} di {totale} della selezione"
        else:
            dove = f"{numero} di {totale}, {'cartella' if pl.temporanea else 'playlist'} {pl.nome}" if totale > 1 else pl.nome
        testo = f"In riproduzione: {brano.percorso}, {dove}."
        if self.motore.sottobrani:
            testo += f" Sottobrano {self.motore.sottobrano} di {self.motore.sottobrani}."
        self._riscontro(evento, testo)
        self._aggiorna_etichette()
        self._insegui()

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
        pl.ricorsiva = True
        brano = self.coda.primo(pl)
        if brano is None:
            self._riscontro("niente_da_suonare", "Né in questa cartella né nelle sue sottocartelle ci sono file da suonare.")
            return
        self._suona(pl, brano)

    def _apri_fino_al_risultato(self, brano):
        """Apre i rami dei Risultati fino a quello del brano, con le pagine
        che servono per vederlo, e ne restituisce la voce."""
        gruppo = self._albero_dei_risultati.gruppo_del_brano.get(id(brano))
        if gruppo is None:
            return None
        voce = self.nodo_risultati
        self.albero.Expand(voce)
        for anello in self._albero_dei_risultati.catena(gruppo):
            voce = next((v for v in self._figli(voce) if (self._dati(v) or {}).get("gruppo") is anello), None)
            if voce is None:
                return None
            self.albero.Expand(voce)
        dati = self._dati(voce)
        posizione = gruppo.brani.index(brano)
        if posizione >= dati["pagina"]:
            dati["pagina"] = (posizione // PAGINA_DEI_RISULTATI + 1) * PAGINA_DEI_RISULTATI
            self._riempi_gruppo(voce)
        return next((v for v in self._figli(voce) if (self._dati(v) or {}).get("brano") is brano), None)

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

    def _visibile(self, voce):
        """Vero se tutti i rami che contengono la voce sono aperti."""
        radice = self.albero.GetRootItem()
        genitore = self.albero.GetItemParent(voce)
        while genitore.IsOk() and genitore != radice:
            if not self.albero.IsExpanded(genitore):
                return False
            genitore = self.albero.GetItemParent(genitore)
        return True

    def _dopo(self, voce):
        """La voce che viene dopo nella plancia, come la si legge scendendo
        con la freccia giu': dentro i rami aperti, poi avanti e fuori. None
        alla fine."""
        if self.albero.IsExpanded(voce):
            figlio = next(self._figli(voce), None)
            if figlio is not None:
                return figlio
        radice = self.albero.GetRootItem()
        while voce.IsOk() and voce != radice:
            fratello = self.albero.GetNextSibling(voce)
            if fratello.IsOk():
                return fratello
            voce = self.albero.GetItemParent(voce)
        return None

    def _prima(self, voce):
        """La voce che viene prima nella plancia, come la si legge salendo con
        la freccia su: la precedente, o l'ultima voce visibile dentro di lei se
        e' aperta, oppure il ramo che la contiene. None all'inizio."""
        precedente = self.albero.GetPrevSibling(voce)
        if not precedente.IsOk():
            genitore = self.albero.GetItemParent(voce)
            return genitore if genitore.IsOk() and genitore != self.albero.GetRootItem() else None
        while self.albero.IsExpanded(precedente) and self.albero.GetChildrenCount(precedente, False):
            precedente = self.albero.GetLastChild(precedente)
        return precedente

    def _suonabile_in_plancia(self, voce):
        """Vero per un brano, un file o un sottobrano che l'avanzamento puo'
        suonare. Un SID con i sottobrani aperti lascia il posto a loro."""
        dati = self._dati(voce) or {}
        tipo = dati.get("tipo")
        if tipo == "sottobrano":
            return not dati["brano"].saltato
        if tipo in ("brano", "file"):
            return not dati["brano"].saltato and not (self.albero.IsExpanded(voce) and self.albero.GetChildrenCount(voce, False))
        return False

    def _voce_che_suona(self):
        """La voce visibile della plancia che corrisponde a cio' che suona, o
        None se non si vede: il sottobrano, se il SID e' aperto, altrimenti il
        brano o il file."""
        corrente = self.coda.corrente
        if corrente is None:
            return None
        for voce in self._tutte_le_voci():
            dati = self._dati(voce) or {}
            if dati.get("tipo") in ("brano", "file") and dati["brano"] is corrente and self._visibile(voce):
                if self.albero.IsExpanded(voce):
                    return next((v for v in self._figli(voce) if self._dati(v).get("numero") == self.motore.sottobrano), voce)
                return voce
        return None

    def _voce_da_seguire(self):
        """La voce visibile di cio' che suona, se a decidere il brano dopo e'
        la plancia; None se decide la lista, perche' non si vede, perche'
        c'e' il loop A-B o perche' suona una selezione."""
        if self.coda.intervallo() is not None or getattr(self.coda.playlist, "selezione", False):
            return None
        return self._voce_che_suona()

    def _passo_in_plancia(self, voce, verso):
        """La voce suonabile prima (verso -1) o dopo (verso 1), come dati
        (playlist, brano, sottobrano); None se non ce n'e'."""
        muovi = self._dopo if verso > 0 else self._prima
        voce = muovi(voce)
        while voce is not None and not self._suonabile_in_plancia(voce):
            voce = muovi(voce)
        if voce is None:
            return None
        dati = self._dati(voce)
        return dati["playlist"], dati["brano"], dati.get("numero")

    def _seguente_automatico(self):
        """Cosa suonare quando un brano finisce da solo: (playlist, brano,
        sottobrano) o None. Se cio' che suona si vede nella plancia, decide la
        plancia: la voce suonabile che viene dopo, dentro i rami aperti,
        sottobrani compresi, anche in un'altra cartella o playlist. Se non si
        vede, per esempio una cartella suonata chiusa o un file aperto con
        Apri file, decide la lista. Con il loop A-B decide il loop."""
        voce = self._voce_da_seguire()
        if voce is not None:
            return self._passo_in_plancia(voce, 1)
        seguente = self.coda.successivo()
        return (self.coda.playlist, seguente, None) if seguente else None

    def _brano_finito(self):
        if self._chiusa:
            return
        pl = self.coda.playlist
        prima = pl.indice(self.coda.corrente) if pl else None
        seguente = self._seguente_automatico()
        if seguente:
            nuova, brano, sottobrano = seguente
            # Nel loop, dopo il punto B si torna al punto A: ha un suono suo.
            dopo = nuova.indice(brano)
            ritorno = self.coda.intervallo() and nuova is pl and prima is not None and dopo is not None and dopo <= prima
            self._suona(nuova, brano, "ritorno_al_punto_a" if ritorno else "brano_seguente_da_solo", sottobrano)
        else:
            self._aggiorna_etichette()
            self._riscontro("fine_playlist", "Fine: davanti non c'è altro da suonare.")

    def _brano_in_errore(self, percorso):
        if self._chiusa:
            return
        self._riscontro("errore", f"Non riesco a suonare {os.path.basename(percorso or '')}.")
        seguente = self._seguente_automatico()
        if seguente:
            nuova, brano, sottobrano = seguente
            self._suona(nuova, brano, "brano_seguente_da_solo", sottobrano)
        else:
            self._aggiorna_etichette()

    def _niente_in_corso(self):
        if self.motore.in_corso:
            return False
        self._riscontro("niente_da_suonare", "Non sta suonando niente.")
        return True

    def _comando_play(self):
        if len(self._voci_selezionate()) > 1:
            self._suona_selezione()
            return
        dati = self._dati(self._voce_corrente()) or {}
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
            # Come in Winamp: X su cio' che sta suonando lo fa ripartire da capo.
            self._suona(self.coda.playlist, corrente, "da_capo", self.motore.sottobrano if self.motore.sottobrani else None)
        elif corrente:
            self._suona(self.coda.playlist, corrente)
        else:
            self._riscontro("niente_da_suonare", "Niente da riprodurre: scegli un brano, una playlist o una cartella nella plancia.")

    def _nodo_della_playlist(self, pl):
        return next((v for v in self._figli(self.nodo_playlist) if (self._dati(v) or {}).get("playlist") is pl), None)

    def _playlist_selezionata(self):
        """La playlist salvata in cui sta la selezione, o quella che suona."""
        voce = self._voce_corrente()
        while voce.IsOk() and voce != self.albero.GetRootItem():
            dati = self._dati(voce) or {}
            if dati.get("tipo") == "playlist" and dati["playlist"] in self.archivio.playlist:
                return dati["playlist"]
            voce = self.albero.GetItemParent(voce)
        return self.coda.playlist if self.coda.playlist in self.archivio.playlist else None

    def _apri_e_suona(self, pl, evento):
        """Porta il fuoco sulla playlist, la apre tutta e suona il primo
        elemento che si puo' suonare, sottobrani compresi."""
        self.albero.Expand(self.nodo_playlist)
        nodo = self._nodo_della_playlist(pl)
        self._apri_ramo(nodo)
        self._seleziona(nodo)
        self.albero.EnsureVisible(nodo)
        self.albero.SetFocus()
        voce = self._dopo(nodo)
        while voce is not None and self._sotto(voce, nodo) and not self._suonabile_in_plancia(voce):
            voce = self._dopo(voce)
        if voce is None or not self._sotto(voce, nodo):
            self._riscontro("niente_da_suonare", f"La playlist {pl.nome} non ha niente da suonare.")
            return
        dati = self._dati(voce)
        self._suona(dati["playlist"], dati["brano"], evento, dati.get("numero"))

    def _playlist_vicina(self, passo):
        playlist = self.archivio.playlist
        if not playlist:
            self._riscontro("niente_da_suonare", "Non ci sono playlist salvate.")
            return
        attuale = self._playlist_selezionata()
        # Senza una playlist di partenza, K parte dalla prima e J dall'ultima.
        partenza = playlist.index(attuale) if attuale is not None else (-1 if passo > 0 else len(playlist))
        indice = partenza + passo
        if not 0 <= indice < len(playlist):
            self._riscontro("nessun_altro_brano", "È la prima playlist." if passo < 0 else "È l'ultima playlist.")
            return
        self._apri_e_suona(playlist[indice], "playlist_precedente" if passo < 0 else "playlist_successiva")

    def _comando_playlist_precedente(self):
        self._playlist_vicina(-1)

    def _comando_playlist_successiva(self):
        self._playlist_vicina(1)

    def _playlist_numero(self, numero):
        if numero > len(self.archivio.playlist):
            self._riscontro("nessun_altro_brano", f"Non c'è la playlist numero {numero}: ne hai {len(self.archivio.playlist)}.")
            return
        self._apri_e_suona(self.archivio.playlist[numero - 1], "playlist_numero")

    def _comando_togli_loop(self):
        if self.coda.loop_playlist is None:
            self._riscontro("loop_non_qui", "Non c'è un loop da togliere.")
            return
        self.coda.togli_loop()
        self._aggiorna_etichette()
        self._riscontro("loop_tolto", "Loop tolto: si suona di nuovo tutta la lista.")

    def _comando_loop(self):
        dati = self._dati(self._voce_corrente()) or {}
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
        if getattr(self.coda.playlist, "selezione", False):
            # La playlist invisibile della selezione vive fino allo stop.
            self.coda.imposta(None, None)
            self._aggiorna_etichette()
            self._riscontro("stop", "Stop. La selezione suonata è chiusa: X suona di nuovo ciò che selezioni.")
            return
        self._aggiorna_etichette()
        self._riscontro("stop", "Stop. X riparte dall'inizio del brano.")

    def _vicino(self, verso, evento, limite):
        """Z e B: il brano prima o dopo, dalla plancia se cio' che suona si
        vede, altrimenti dalla lista."""
        if not self.coda.playlist:
            self._riscontro("niente_da_suonare", "Non c'è una playlist in riproduzione.")
            return
        voce = self._voce_da_seguire()
        if voce is not None:
            scelta = self._passo_in_plancia(voce, verso)
        else:
            brano = self.coda.successivo() if verso > 0 else self.coda.precedente()
            scelta = (self.coda.playlist, brano, None) if brano else None
        if scelta is None:
            self._riscontro("nessun_altro_brano", limite)
            return
        playlist, brano, sottobrano = scelta
        self._suona(playlist, brano, evento, sottobrano)

    def _comando_successivo(self):
        self._vicino(1, "successivo", "È l'ultimo brano.")

    def _comando_precedente(self):
        self._vicino(-1, "precedente", "È il primo brano.")

    def _comando_casuale(self, scelta=random.choice):
        """N: a caso fra le voci suonabili che si vedono nella plancia, se cio'
        che suona si vede; altrimenti a caso nella sua lista."""
        if not self.coda.playlist:
            self._riscontro("niente_da_suonare", "Non c'è una playlist in riproduzione.")
            return
        voce = self._voce_da_seguire()
        if voce is None:
            brano = self.coda.casuale(scelta)
            if brano is None:
                self._riscontro("nessun_altro_brano", "Non ci sono brani da scegliere.")
                return
            self._suona(self.coda.playlist, brano, "casuale")
            return
        candidati = [v for v in self._tutte_le_voci() if v != voce and self._visibile(v) and self._suonabile_in_plancia(v)]
        if not candidati:
            self._riscontro("nessun_altro_brano", "Nella plancia non si vede nient'altro da suonare.")
            return
        dati = self._dati(scelta(candidati))
        self._suona(dati["playlist"], dati["brano"], "casuale", dati.get("numero"))

    def _salto(self, secondi, evento):
        if self._niente_in_corso():
            return
        prima = self.motore.posizione or 0
        durata = self.motore.durata
        arrivo = max(0, prima + secondi)
        if durata is not None:
            arrivo = min(arrivo, durata)
        self.motore.salta(secondi)
        self._riscontro(evento, f"{'Avanti' if secondi > 0 else 'Indietro'} a {tempo(arrivo)} di {tempo(durata)}.", "salto")

    def _comando_avanti(self):
        self._salto(self.impostazioni["passo_avanti"], "avanti")

    def _comando_indietro(self):
        self._salto(-self.impostazioni["passo_indietro"], "indietro")

    def _chiedi_secondi(self, chiave, verso):
        self._suono("domanda")
        attuale = self.impostazioni[chiave]
        with DialogoTesto(self, f"Di quanti secondi salta {verso}? Anche con i decimali, per esempio 2.5.", "Passo di salto", secondi_da_leggere(attuale)) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            testo = dialogo.GetValue()
        secondi = leggi_tempo(testo)
        if not secondi or secondi < 0.1:
            self._riscontro("errore", f"{testo} non è un numero di secondi valido; il passo resta {secondi_da_leggere(attuale)}.")
            return
        self.impostazioni[chiave] = round(secondi, 3)
        self._salva_impostazioni()
        self._riscontro("passo_di_salto", f"Il salto {verso} ora è di {secondi_da_leggere(secondi)} secondi.", "passo_di_salto")

    def _comando_passo_indietro(self):
        self._chiedi_secondi("passo_indietro", "indietro")

    def _comando_passo_avanti(self):
        self._chiedi_secondi("passo_avanti", "avanti")

    def _comando_vai_a_tempo(self):
        if self._niente_in_corso():
            return
        self._suono("domanda")
        durata = self.motore.durata
        with DialogoTesto(self, f"A che tempo andare? Minuti e secondi, per esempio 1:30. Il brano dura {tempo(durata)}.", "Vai al tempo") as dialogo:
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
        nuovo = max(0, min(VOLUME_MASSIMO, attuale + passo))
        if nuovo == attuale:
            self._riscontro("volume_al_limite", f"Volume già al {'massimo' if passo > 0 else 'minimo'}, {attuale}.", "volume")
            return
        self.motore.volume = nuovo
        self.impostazioni["volume"] = nuovo
        amplificato = ", amplificato oltre il 100" if nuovo > 100 else ""
        self._riscontro("volume_su" if passo > 0 else "volume_giu", f"Volume {nuovo}{amplificato}.", "volume")

    def _comando_volume_su(self):
        self._volume(self.impostazioni["passo_volume"])

    def _comando_volume_giu(self):
        self._volume(-self.impostazioni["passo_volume"])

    def _comando_passo_volume(self):
        self._suono("domanda")
        attuale = self.impostazioni["passo_volume"]
        with DialogoTesto(self, "Di quanto cambiano il volume più e meno? Da 1 a 50.", "Passo del volume", str(attuale)) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            testo = dialogo.GetValue().strip()
        if not testo.isdigit() or not 1 <= int(testo) <= 50:
            self._riscontro("errore", f"{testo} non è un passo da 1 a 50; resta {attuale}.")
            return
        self.impostazioni["passo_volume"] = int(testo)
        self._salva_impostazioni()
        self._riscontro("passo_del_volume", f"Più e meno ora cambiano il volume di {testo}.", "passo_del_volume")

    def _comando_muto(self):
        self.motore.muto = not self.motore.muto
        if self.motore.muto:
            self._riscontro("muto_acceso", "Muto.", "volume")
        else:
            self._riscontro("muto_spento", f"Audio di nuovo acceso, volume {self.motore.volume}.", "volume")

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

    # F8.

    def _trova_voce_che_suona(self):
        """La voce della plancia di cio' che suona, caricando la playlist o
        aprendo le cartelle se serve; None se non c'e', per esempio per un
        file aperto con Apri file."""
        corrente, pl = self.coda.corrente, self.coda.playlist
        if not pl.temporanea:
            # Una playlist mai aperta non ha ancora i suoi brani nella plancia.
            nodo = self.nodo_preferiti if pl is self.archivio.preferiti else next((v for v in self._figli(self.nodo_playlist) if self._dati(v).get("playlist") is pl), None)
            if nodo is not None and self._dati(nodo).get("caricato") is False:
                self._carica(nodo, self._dati(nodo))
        voce = next((v for v in self._tutte_le_voci() if (self._dati(v) or {}).get("tipo") in ("brano", "file")
            and self._dati(v)["brano"] is corrente), None)
        if voce is None and pl is self.risultati and self._albero_dei_risultati is not None:
            voce = self._apri_fino_al_risultato(corrente)
        if voce is None and pl.temporanea and pl.cartella:
            # Suonando una cartella con le sottocartelle, il brano puo' stare
            # in una sottocartella mai aperta nella plancia.
            cartella = self._apri_fino_a(os.path.dirname(corrente.percorso))
            if cartella is not None:
                voce = next((v for v in self._figli(cartella) if (self._dati(v) or {}).get("brano") is corrente), None)
        # Se i sottobrani del SID sono aperti, la voce e' quella del sottobrano che suona.
        if voce is not None and self.albero.IsExpanded(voce):
            voce = next((v for v in self._figli(voce) if self._dati(v).get("numero") == self.motore.sottobrano), voce)
        return voce

    def _vai_al_brano(self):
        corrente = self.coda.corrente
        if not corrente or not self.motore.in_corso:
            self._riscontro("niente_da_suonare", "Non sta suonando niente.")
            return
        voce = self._trova_voce_che_suona()
        if voce is None:
            self._riscontro("niente_da_suonare", f"{corrente.nome_del_file} non è nella plancia: è stato aperto con Apri file.")
            return
        self.albero.EnsureVisible(voce)
        self._seleziona(voce)
        self._suono("vai_al_brano")
        self.albero.SetFocus()

    def _insegui(self):
        """Con l'inseguimento agganciato porta la selezione su cio' che suona,
        senza spostare il fuoco e senza suoni: il suono del brano nuovo c'e' gia'."""
        if not self.impostazioni["insegui"] or not self.coda.corrente:
            return
        voce = self._trova_voce_che_suona()
        if voce is not None and voce != self._voce_corrente():
            self.albero.EnsureVisible(voce)
            self._seleziona(voce)

    def _aggancia(self):
        self.impostazioni["insegui"] = not self.impostazioni["insegui"]
        self._salva_impostazioni()
        if self.impostazioni["insegui"]:
            self._riscontro("insegui_acceso", "Inseguimento agganciato: la selezione della plancia segue il brano che suona.")
            if self.motore.in_corso:
                self._insegui()
        else:
            self._riscontro("insegui_spento", "Inseguimento sganciato: la selezione resta dove la lasci.")

    # F9 e F10.

    def _ramo_di_lavoro(self):
        """Il ramo su cui lavorano F9 e F10: la voce selezionata, o quella che
        la contiene se non ha niente dentro."""
        voce = self._voce_corrente()
        if voce.IsOk() and not self.albero.ItemHasChildren(voce):
            voce = self.albero.GetItemParent(voce)
        return voce if voce.IsOk() and voce != self.albero.GetRootItem() else None

    def _chiudi_tutto(self):
        voce = self._ramo_di_lavoro()
        if voce is None:
            self._riscontro("non_disponibile", "Qui non c'è niente da chiudere.")
            return
        self.albero.CollapseAllChildren(voce)
        self._seleziona(voce)
        self._riscontro("chiudi_tutto", f"Chiuso tutto dentro {self.albero.GetItemText(voce)}.")

    def _apri_ramo(self, voce):
        """Apre la voce e tutti i rami che ha dentro, caricandoli, fino a
        MASSIMO_DI_RAMI. Torna (rami aperti, vero se si e' fermato prima)."""
        aperti = 0
        da_aprire = [voce]
        with wx.BusyCursor():
            while da_aprire and aperti < MASSIMO_DI_RAMI:
                ramo = da_aprire.pop(0)
                if not self.albero.ItemHasChildren(ramo):
                    continue
                self.albero.Expand(ramo)
                aperti += 1
                da_aprire.extend(self._figli(ramo))
        return aperti, bool(da_aprire)

    def _apri_tutto(self):
        """Apre la voce e tutti i rami che ha dentro, caricandoli; si ferma a
        MASSIMO_DI_RAMI, perche' sotto Questo PC ci sono dischi interi."""
        voce = self._ramo_di_lavoro()
        if voce is None:
            self._riscontro("non_disponibile", "Qui non c'è niente da aprire.")
            return
        aperti, fermato = self._apri_ramo(voce)
        nome = self.albero.GetItemText(voce)
        if fermato:
            self._riscontro("apri_tutto", f"Aperti {aperti} rami dentro {nome}; mi fermo qui, gli altri restano chiusi.")
        else:
            self._riscontro("apri_tutto", f"Aperto tutto dentro {nome}: {aperti} rami.")

    # F1, F2, F3.

    def _stampa(self, evento, righe):
        """Scrive nella console un testo lungo, riga per riga, con l'ora solo
        in fondo, e ci porta il fuoco con il cursore sulla prima riga."""
        righe = [r for r in righe if r.strip()]
        if not righe:
            return
        self._suono(evento)
        # Il testo resta intero anche se e' piu' lungo delle righe che la
        # console tiene: si taglia prima di lui, mai dentro.
        self._da_tenere = len(righe)
        try:
            for i, riga in enumerate(righe):
                self.scrivi(riga, ora=i == len(righe) - 1)
        finally:
            self._da_tenere = 0
        self._porta_il_cursore(len("".join(r + "\n" for r in self._righe[:-len(righe)])))

    @staticmethod
    def _unita(testo):
        """Quante posizioni occupa il testo nel controllo della console, che
        conta come Windows: i caratteri fuori dal piano base, come le emoji,
        valgono due."""
        return len(testo.encode("utf-16-le")) // 2

    def _nella_console(self, posizione):
        """Dalla posizione nel testo delle righe a quella del controllo."""
        return self._unita("\n".join(self._righe)[:posizione])

    def _dalla_console(self, nativa):
        """Dalla posizione del controllo a quella nel testo delle righe."""
        return len("\n".join(self._righe).encode("utf-16-le")[:2 * nativa].decode("utf-16-le", errors="ignore"))

    def _porta_il_cursore(self, posizione):
        """Porta il fuoco nella console con il cursore sulla posizione data,
        contata nel testo delle righe. Arrivando nella console il cursore
        torna dove era rimasto: per questo la posizione si mette anche in
        quella da ricordare."""
        posizione = self._nella_console(posizione)
        self._posizione_della_console = posizione
        if self.console.HasFocus():
            self.console.SetInsertionPoint(posizione)
        else:
            self.console.SetFocus()
        self.console.ShowPosition(posizione)

    def _leggi_risorsa(self, nome):
        try:
            with open(percorsi.percorso_risorsa(nome), encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            return f"Non riesco a leggere {nome}: {e}"

    def _comando_cerca_in_console(self):
        """Il campo della ricerca nella console, con le sue istruzioni come
        commenti; se il testo non si capisce lo spiega e lo ripropone."""
        testo = self._cercato_in_console
        while True:
            self._suono("domanda")
            with FinestraFiltro(self, "Cerca nella console", testo, ISTRUZIONI_DELLA_CONSOLE) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    return
                # Andare a capo vale come uno spazio; gli spazi dentro il
                # testo contano, perche' si cerca cosi' com'e'.
                testo = " ".join(dialogo.testo.splitlines()).strip()
            if not testo:
                return
            try:
                modello = modello_della_console(testo)
            except ErroreFiltro as e:
                self._riscontro("errore", f"Nella ricerca non capisco: {e}")
                continue
            break
        self._cercato_in_console = testo
        self._modello_della_console = modello
        self._cerca_in_console(0)

    def _cerca_in_console(self, da):
        """Porta il cursore sulla prima occorrenza del testo cercato dalla
        posizione da in poi; arrivata in fondo riparte dall'inizio. Le righe
        dei messaggi hanno l'ora in fondo, quindi si cercano anche gli orari.
        La riga che dice che il testo non c'e' lo ripete, e non conta."""
        righe = self._righe[:-1] if self._categoria == "non_trovato_in_console" else self._righe
        testo = "\n".join(righe)
        trovato = self._modello_della_console.search(testo, da)
        ripartito = trovato is None and da > 0
        if ripartito:
            trovato = self._modello_della_console.search(testo)
        if trovato is None:
            self._occorrenza = None
            self._riscontro("non_trovato_in_console", f"Nella console non c'è {self._cercato_in_console}.", "non_trovato_in_console")
            return
        self._occorrenza = trovato.span()
        self._suono("ripartito_in_console" if ripartito else "trovato_in_console")
        self._porta_il_cursore(trovato.start())

    def _tasto_nella_console(self, evento):
        if evento.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and evento.GetModifiers() == wx.MOD_NONE and self._modello_della_console:
            # Dall'occorrenza su cui sta il cursore si riparte dalla sua fine:
            # con un jolly in testa, ripartendo dal carattere dopo, si
            # ritroverebbe un pezzo della stessa.
            posizione = self._dalla_console(self.console.GetInsertionPoint())
            if self._occorrenza is not None and posizione == self._occorrenza[0]:
                self._cerca_in_console(max(self._occorrenza[1], posizione + 1))
            else:
                self._cerca_in_console(posizione + 1)
        else:
            evento.Skip()

    def _elenco_dei_tasti(self):
        """F12: scrive nella console la sezione I tasti del manuale, cosi' la
        documentazione dei tasti e' una sola, e porta il fuoco nella console,
        con il cursore sulla prima riga dell'elenco."""
        righe = sezione_del_manuale(self._leggi_risorsa("manuale.txt"), "I tasti")
        if not righe:
            self._riscontro("errore", "Nel manuale non trovo la sezione I tasti.")
            return
        self._stampa("elenco_dei_tasti", righe)

    def _manuale(self):
        self._stampa("manuale", self._leggi_risorsa("manuale.txt").splitlines())

    def _changelog(self):
        self._stampa("changelog", ["Novità di MeTeOra", *righe_del_changelog(self._leggi_risorsa("CHANGELOG.md"))])

    def _crediti(self):
        righe = [
            "Crediti di MeTeOra",
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
        ]
        self._stampa("crediti", righe)

    # La ripresa all'avvio.

    def _stato_da_riprendere(self):
        """Cosa suonava, per ritrovarlo alla riapertura: da quale lista, quale
        brano e a che punto. Vuoto se non c'era niente."""
        pl, brano = self.coda.playlist, self.coda.corrente
        if pl is None or brano is None:
            return {}
        stato = {"percorso": brano.percorso, "sottobrano": self.motore.sottobrano if self.motore.sottobrani else None,
            "numero": pl.indice(brano), "posizione": (self.motore.posizione or 0) if self.motore.in_corso else 0}
        if pl is self.archivio.preferiti:
            stato["tipo"] = "preferiti"
        elif pl in self.archivio.playlist:
            stato.update(tipo="playlist", indice=self.archivio.playlist.index(pl))
        elif pl.cartella:
            stato.update(tipo="ricorsiva" if getattr(pl, "ricorsiva", False) else "cartella", cartella=pl.cartella)
        else:
            stato["tipo"] = "file"
        return stato

    def _lista_da_riprendere(self, stato):
        tipo = stato.get("tipo")
        if tipo == "preferiti":
            return self.archivio.preferiti
        if tipo == "playlist" and isinstance(stato.get("indice"), int) and 0 <= stato["indice"] < len(self.archivio.playlist):
            return self.archivio.playlist[stato["indice"]]
        if tipo == "cartella" and os.path.isdir(stato.get("cartella", "")):
            return self._temporanea(stato["cartella"])
        if tipo == "ricorsiva" and os.path.isdir(stato.get("cartella", "")):
            contenuti = questo_pc.contenuti_ricorsivi(stato["cartella"])
            brani = [b for sotto, files in contenuti for b in self._temporanea(sotto, files).brani]
            pl = Playlist(os.path.basename(stato["cartella"].rstrip("\\")) or stato["cartella"], brani, cartella=stato["cartella"])
            pl.ricorsiva = True
            return pl
        return None

    def riprendi(self):
        """All'avvio: rimette in pausa, al suo punto, cio' che suonava
        all'uscita, e ci porta la selezione della plancia. X riparte."""
        stato = self.impostazioni.get("ripresa") or {}
        percorso = stato.get("percorso")
        if not percorso:
            return
        if not os.path.isfile(percorso):
            self.scrivi(f"Non trovo più {percorso}, che suonava l'ultima volta.")
            return
        pl = self._lista_da_riprendere(stato)
        brano = None
        if pl is not None:
            numero = stato.get("numero")
            if isinstance(numero, int) and 0 <= numero < len(pl.brani) and pl.brani[numero].percorso == percorso:
                brano = pl.brani[numero]
            else:
                brano = next((b for b in pl.brani if b.percorso == percorso), None)
        if brano is None:
            pl = Playlist("file aperto", [Brano(percorso)], cartella="")
            brano = pl.brani[0]
        posizione = stato.get("posizione") or 0
        self.coda.imposta(pl, brano)
        sottobrano = stato.get("sottobrano") if isinstance(stato.get("sottobrano"), int) else None
        self.motore.suona(percorso, sottobrano, inizio=posizione, in_pausa=True)
        voce = self._trova_voce_che_suona()
        if voce is not None:
            self.albero.EnsureVisible(voce)
            self._seleziona(voce)
        self._aggiorna_etichette()
        self._riscontro("ripresa_all_avvio", f"Riprendo da dove eri: {percorso}, in pausa a {tempo(posizione)}. X riparte.")

    # L'uscita.

    def _alla_chiusura(self, evento):
        if self._chiusa:
            evento.Skip()
            return
        self._chiusa = True
        if self._ricerca is not None:
            self._ricerca.ferma()
        self.impostazioni["ripresa"] = self._stato_da_riprendere()
        self._salva_archivio()
        self.contatore.ferma()
        self.schedario.ferma()
        with contextlib.suppress(OSError):
            self.schedario.salva()
        with contextlib.suppress(OSError):
            self.impostazioni.salva()
        self.motore.chiudi()
        # Il suono dell'uscita si ascolta intero prima che il processo finisca.
        suoni.suona("uscita", self.impostazioni["volume_effetti"], sync=True)
        evento.Skip()
