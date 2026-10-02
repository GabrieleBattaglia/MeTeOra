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
# cartelle aperte che non spariscono, playlist che si ricaricano, Risultati cestinati, emoji e jolly nella console;
# nella 1.36.1 Backspace e Maiuscolo con Backspace, e Maiuscolo e Ctrl con le frecce senza il nome della plancia ripetuto da NVDA;
# nella 1.36.2 dopo Ctrl con le frecce i comandi agiscono sulla voce selezionata; nella 1.39.0 i marker, issue 12; nella 1.39.1 il singolare nelle righe della console; nella 1.40.0 Maiuscolo con le cifre; nella 1.40.2 Maiuscolo con R e Y risparmiano il marker su cui si e';
# nella 1.41.0 i suoni dei rami aperti e chiusi con le frecce; nella 1.42.0 il beep dei livelli; nella 1.43.0 Maiuscolo con Backspace che risale all'antenato;
# nella 1.51.0 la finestra delle impostazioni, con caratteri e colori delle tre aree, la scheda audio, la console salvata e la finestra dei marcatori;
# nella 1.55.0 velocita', tono, equalizzatore e dissolvenza incrociata, con i tasti, le voci delle impostazioni e il passaggio fra due brani (tappa 4, issue 15). Nella 1.58.0 la dissolvenza anche su stop, pausa, X da capo e marker, i suoni al volo dell'equalizzatore e il loop a giro su Maiuscolo+X; nella 1.58.1 F e H scambiati.

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
import copy
import ctypes
import datetime
import os
import random
import re
import sys
import threading
import traceback
import warnings
from ctypes import wintypes

import wx

import formati
import marcatori
import percorsi
import questo_pc
import schede_audio
import songlengths
import suoni
import valori
import version
from contatore import Contatore
from dialoghi import DialogoTesto, FinestraImpostazioni, FinestraMarcatori, FinestraScelta
from filtro import COMMENTO, ErroreFiltro, Filtro, modello_della_console
from impostazioni import Impostazioni
from marcatori import Marcatori
from motore import VOLUME_MASSIMO, durata_del_sottobrano, sottobrano_risolto
from playlist import Archivio, Brano, Coda, Playlist
from ricerca import AlberoDeiRisultati, Ricerca
from schedario import Schedario
from valori import AREE, ErroreValore, leggi_tempo, secondi_da_leggere

FILE_PLAYLIST = "MeTeOra - Playlist.json"
FILE_IMPOSTAZIONI = "MeTeOra - Impostazioni.json"
FILE_SCHEDARIO = "MeTeOra - Schedario.json"
FILE_MARCATORI = "MeTeOra - Marcatori.json"
# Il nome proposto per l'esportazione dei marcatori, e il filtro dei dialoghi
# che la scrivono e la leggono.
FILE_DELL_ESPORTAZIONE = "MeTeOra - Marcatori esportati.json"
FILTRO_DEI_MARCATORI = "Marcatori di MeTeOra (*.json)|*.json"
# I dialoghi dei file passano da questo nome, che le prove sostituiscono.
DialogoDiFile = wx.FileDialog
# I messaggi dell'albero di Windows che wx non espone come servono: spostare
# il cursore senza toccare le altre selezioni, e quante voci stanno in una pagina.
_manda_messaggio = ctypes.WinDLL("user32").SendMessageW
_manda_messaggio.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
_manda_messaggio.restype = ctypes.c_ssize_t
_TVM_SELECTITEM = 0x1100 + 11
_TVM_GETVISIBLECOUNT = 0x1100 + 16
_TVGN_CARET = 0x0009
# I tasti che, premuti da soli, arrivano alla plancia ma non sono comandi.
_SOLO_MODIFICATORI = (wx.WXK_SHIFT, wx.WXK_CONTROL, wx.WXK_RAW_CONTROL, wx.WXK_ALT, wx.WXK_WINDOWS_LEFT, wx.WXK_WINDOWS_RIGHT, wx.WXK_CAPITAL)
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
    # I marker, issue 12.
    ("t", False): "marker",
    ("r", False): "marker_precedente",
    ("y", False): "marker_successivo",
    ("t", True): "togli_i_marker",
    ("r", True): "togli_i_marker_prima",
    ("y", True): "togli_i_marker_dopo",
    # Velocita', tono, equalizzatore e dissolvenza, tappa 4 (issue 15). La E
    # accentata arriva come e' anche con il Maiuscolo: Windows da' il tasto,
    # non la e acuta che il Maiuscolo scriverebbe.
    ("a", False): "velocita_giu",
    ("s", False): "velocita_normale",
    ("d", False): "velocita_su",
    # Come A e D per la velocita': a sinistra si scende, a destra si sale
    # (Gabriele, collaudo della 1.55.2).
    ("f", False): "tono_giu",
    ("g", False): "tono_normale",
    ("h", False): "tono_su",
    ("u", False): "banda_precedente",
    ("i", False): "banda_successiva",
    ("o", False): "banda_su",
    ("p", False): "banda_giu",
    ("è", False): "azzera_la_banda",
    ("è", True): "azzera_le_bande",
    ("l", False): "dissolvenza",
    ("l", True): "durata_della_dissolvenza",
}
# I segni sopra le cifre nella tastiera italiana: Maiuscolo con 1 e' il punto
# esclamativo, e cosi' via fino a Maiuscolo con 0, l'uguale.
CIFRE_COL_MAIUSCOLO = {"!": 1, '"': 2, "£": 3, "$": 4, "%": 5, "&": 6, "/": 7, "(": 8, ")": 9, "=": 10}
# I tasti gia' assegnati nel piano a funzioni delle tappe successive: per ora
# dicono di non essere ancora disponibili.
FUTURI = {"'": "scelta della traccia audio", "ì": "scelta della traccia audio"}
FUTURI_MAIUSCOLI = {}

TASTI_COMUNI = [
    "X riproduce la voce selezionata o riprende, C pausa, V stop, Z e B brano precedente e successivo, N brano a caso.",
    "Q ed E indietro e avanti nel brano, Maiuscolo con Q ed E ne cambiano i secondi, W va a un tempo, + e - volume, Maiuscolo+M il passo del volume, M muto.",
    "A e D rallentano e accelerano, S torna alla velocità normale; F e H abbassano e alzano il tono di un semitono, G lo riporta al normale.",
    "U e I scelgono la banda dell'equalizzatore, O e P la alzano e la abbassano di un dB, È la azzera, Maiuscolo con È le azzera tutte.",
    "L accende e spegne la dissolvenza incrociata: con lei sfumano i cambi di brano, lo stop, la pausa, X da capo e i marker; Maiuscolo con L ne chiede la durata.",
    "Maiuscolo+X, a giro: punto A del loop sul brano selezionato, poi punto B, poi toglie il loop.",
    "J e K aprono e suonano la playlist precedente e successiva, le cifre da 1 a 0 le prime dieci playlist.",
    "Nella plancia Backspace chiude il ramo in cui sei e risale di un livello, Maiuscolo con Backspace risale di colpo all'unità o alla playlist, Preferiti compresi, e chiude i rami al suo interno.",
    "T mette un marker dove sei, o rinomina quello su cui sei; R e Y vanno al marker precedente e successivo; Maiuscolo con R, Y e T tolgono i marker prima, dopo e tutti; Maiuscolo con le cifre da 1 a 0 va ai primi dieci marker del brano della plancia.",
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
    "brano": ("un brano di una playlist", "Invio, Applicazioni o Spazio: menu con Riproduci, Sposta e Saltato. Canc toglie il brano dalla playlist, Maiuscolo+Canc manda il file nel cestino. Un SID con più sottobrani, o un brano con dei marker, si apre con freccia destra."),
    "pc": ("Questo PC", "Freccia destra mostra le unità. Invio, Applicazioni o Spazio: menu con Aggiorna."),
    "unita": ("un'unità", "Freccia destra mostra il contenuto. Invio, Applicazioni o Spazio: menu con Crea playlist da qui."),
    "cartella": ("una cartella", "Freccia destra mostra il contenuto. Invio, Applicazioni o Spazio: menu con Riproduci e Crea playlist da qui."),
    "file": ("un file", "Invio, Applicazioni o Spazio: menu con Riproduci e Aggiungi alla playlist. Maiuscolo+Canc manda il file nel cestino. Un SID con più sottobrani, o un file con dei marker, si apre con freccia destra."),
    "sottobrano": ("un sottobrano di un SID", "Invio, Applicazioni o Spazio: menu con Riproduci e Aggiungi alla playlist. Se ha dei marker, freccia destra li mostra."),
    "marker": ("un marker", "Invio rinomina il marker, Canc lo elimina, X fa come sul suo brano. Applicazioni o Spazio: menu con Vai al marker, che suona il brano da lì, Rinomina ed Elimina."),
    "comando": ("un comando", "Invio esegue il comando."),
}
# Le voci della finestra delle impostazioni, in ordine: chiave -> (etichetta,
# participio per dire che non e' cambiata; None per le voci che fanno
# un'azione invece di cambiare un valore).
VOCI_DELLE_IMPOSTAZIONI = {
    "volume": ("Volume della musica", "cambiato"),
    "passo_volume": ("Passo del volume", "cambiato"),
    "volume_effetti": ("Volume degli effetti", "cambiato"),
    "scheda_audio": ("Scheda audio", "cambiata"),
    "passo_indietro": ("Salto indietro di Q", "cambiato"),
    "passo_avanti": ("Salto avanti di E", "cambiato"),
    "velocita": ("Velocità", "cambiata"),
    "tono": ("Tono", "cambiato"),
    "bande": ("Equalizzatore", "cambiato"),
    "dissolvenza": ("Dissolvenza", "cambiata"),
    "insegui": ("Inseguimento della plancia (Maiuscolo+F8)", "cambiato"),
    "caratteri": ("Dimensioni dei caratteri", "cambiate"),
    "colori_testo": ("Colori dei caratteri", "cambiati"),
    "colori_sfondo": ("Colori dello sfondo", "cambiati"),
    "righe_della_console": ("Righe della console", "cambiate"),
    "salva_console": ("Salva console", None),
    "marcatori": ("Marcatori", None),
    "importa_marcatori": ("Importa marcatori", None),
}
# L'ultima riga delle istruzioni di ogni campo.
REGOLA_DEL_DOLLARO = "Le righe che cominciano con il dollaro non contano: scrivi nell'ultima riga."
# La prova della scheda audio degli effetti: un centesimo di secondo di
# silenzio alla frequenza del mixer, 44100, che la apre senza suonare niente,
# anche con il volume degli effetti a zero.
SILENZIO_DI_PROVA = 441
# Perche' la scheda audio scelta non e' quella in uso, come lo dice la riga
# della finestra delle impostazioni: si usa l'automatica, e la scelta resta.
SCHEDA_MANCANTE = "non c'è"
SCHEDA_CHE_NON_SI_APRE = "non si apre"


def tempo(secondi):
    """m:ss, oppure h:mm:ss oltre l'ora."""
    if secondi is None:
        return "?"
    secondi = max(0, int(secondi))
    ore, resto = divmod(secondi, 3600)
    minuti, secondi = divmod(resto, 60)
    return f"{ore}:{minuti:02d}:{secondi:02d}" if ore else f"{minuti}:{secondi:02d}"


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
    REGOLA_DEL_DOLLARO,
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
    REGOLA_DEL_DOLLARO,
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

        # Gli avvisi del motore arrivano dai suoi fili: wx.CallAfter li porta
        # nel filo della finestra.
        self.motore = Motore(alla_fine=lambda: wx.CallAfter(self._brano_finito),
            all_errore=lambda p: wx.CallAfter(self._brano_in_errore, p), ao=ao, volume=self.impostazioni["volume"],
            chiedi_il_seguente=lambda: wx.CallAfter(self._prepara_il_seguente),
            al_passaggio=lambda percorso, sottobrano: wx.CallAfter(self._passaggio, percorso, sottobrano))
        # Velocita', tono, equalizzatore e dissolvenza salvati valgono per tutti
        # i brani, dal primo.
        self._applica_la_riproduzione()
        # Il brano che esce quando il motore ha chiesto il seguente, come
        # (playlist, brano, sottobrano), e il seguente preparato, come
        # (playlist, brano, sottobrano chiesto): servono al passaggio, per
        # ricontrollare. None fuori da un passaggio preparato.
        self._uscente = None
        self._preparato = None
        # La banda dell'equalizzatore scelta con U e I, contata da zero: si
        # parte dalla prima, quella dei 60 Hz.
        self._banda = 0
        # La scheda audio scelta, appena c'e' il motore; con la scelta
        # automatica non si tocca niente. La console, che ancora non c'e',
        # dira' com'e' andata.
        esito_della_scheda, errore_della_scheda = self._applica_la_scheda_all_avvio()
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
        self.marcatori = Marcatori(os.path.join(cartella_dati, FILE_MARCATORI))
        self.marcatori.carica()
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
        # Vero mentre una freccia, destra o sinistra, apre o chiude un ramo.
        self._freccia_nell_albero = False
        # Maiuscolo con le frecce allarga la selezione dall'ancora; l'ancora
        # vale finche' il fuoco resta dove l'hanno lasciato Maiuscolo o Ctrl
        # con le frecce, o Ctrl+Spazio.
        self._ancora = None
        self._fuoco_atteso = None
        self._righe = []
        self._chiusa = False
        # Il turno dell'ultimo beep dei livelli: un beep rimandato che nel
        # frattempo e' stato superato da un altro non suona piu'.
        self._turno_del_beep = 0
        # Caratteri e colori gia' dati alle tre aree: _applica_aspetto tocca
        # solo cio' che cambia, e un'area mai toccata resta di Windows.
        self._aspetto = {"caratteri": {}, "colori_testo": {}, "colori_sfondo": {}}
        self._costruisci()
        self._popola_albero()
        self.Bind(wx.EVT_CHAR_HOOK, self._tasto)
        self.Bind(wx.EVT_CLOSE, self._alla_chiusura)
        self.scrivi(f"MeTeOra {version.VERSION} del {version.DATE}. Pronto: F1 apre il manuale, F7 apre il cruscotto con i tasti del punto in cui ti trovi.")
        fuori_dal_normale = self._riproduzione_fuori_dal_normale()
        if fuori_dal_normale:
            self.scrivi(fuori_dal_normale)
        if errore_archivio:
            self.scrivi(f"Il file delle playlist non si legge, e parto senza playlist: {errore_archivio}")
            # Il file illeggibile non va sovrascritto alla prima modifica.
            self.archivio.percorso += ".nuovo"
        if self.marcatori.errore:
            self.scrivi(f"Il file dei marker non si legge, e resta com'è: {self.marcatori.errore}. I marker nuovi vanno in {os.path.basename(self.marcatori.percorso)}.")
        self._scrivi_la_scheda_all_avvio(esito_della_scheda, errore_della_scheda)
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
        # Caratteri e colori delle impostazioni, prima di misurare il
        # cruscotto: la sua misura la calcola _applica_aspetto.
        self._applica_aspetto()
        tutto.Add(self.cruscotto, 0, wx.EXPAND | wx.ALL, 4)
        pannello.SetSizer(tutto)
        pannello.Bind(wx.EVT_SIZE, self._pannello_ridimensionato)
        self.albero.Bind(wx.EVT_TREE_ITEM_EXPANDING, self._in_espansione)
        self.albero.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self._chiusa_una_voce)
        self.albero.Bind(wx.EVT_TREE_ITEM_EXPANDED, self._aperta_una_voce)
        self.albero.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._invio)
        self.albero.Bind(wx.EVT_TREE_ITEM_MENU, self._menu_da_evento)
        self.albero.Bind(wx.EVT_KEY_DOWN, self._tasto_nell_albero)
        self.albero.Bind(wx.EVT_SET_FOCUS, self._fuoco_all_albero)
        self.console.Bind(wx.EVT_SET_FOCUS, self._fuoco_alla_console)
        self.console.Bind(wx.EVT_KILL_FOCUS, self._console_lasciata)
        self.console.Bind(wx.EVT_KEY_DOWN, self._tasto_nella_console)
        self.cruscotto.Bind(wx.EVT_SET_FOCUS, self._fuoco_al_cruscotto)
        self.cruscotto.Bind(wx.EVT_KILL_FOCUS, self._cruscotto_lasciato)

    def _aree(self):
        """Le tre aree, con la lettera che le indica nelle impostazioni."""
        return {"p": self.albero, "c": self.console, "t": self.cruscotto}

    def _applica_aspetto(self):
        """Da' a plancia, console e cruscotto le dimensioni dei caratteri e i
        colori delle impostazioni, toccando solo cio' che cambia: un'area che
        non ne ha mai avuti resta di Windows. Il carattere e' quello di
        sistema alla dimensione scelta; un'area che torna a Windows riprende
        il carattere di sistema e i colori di sistema del testo e dello
        sfondo delle finestre. Le etichette delle aree non cambiano. Alla
        fine il cruscotto si rimisura sul suo carattere."""
        aree = self._aree()
        sistema = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        for area, controllo in aree.items():
            punti = self.impostazioni["caratteri"].get(area)
            if punti != self._aspetto["caratteri"].get(area):
                carattere = wx.Font(sistema)
                if punti:
                    carattere.SetPointSize(punti)
                controllo.SetFont(carattere)
        # I colori vengono dopo i caratteri: nei controlli RichEdit, console e
        # cruscotto, un carattere nuovo riporta il testo al colore di Windows
        # (verificato sul desktop nascosto).
        for chiave, imposta, di_sistema in (("colori_testo", "SetForegroundColour", wx.SYS_COLOUR_WINDOWTEXT),
                ("colori_sfondo", "SetBackgroundColour", wx.SYS_COLOUR_WINDOW)):
            for area, controllo in aree.items():
                percentuali = self.impostazioni[chiave].get(area)
                if percentuali != self._aspetto[chiave].get(area):
                    colore = wx.Colour(*valori.colore_da_percentuali(percentuali)) if percentuali else wx.SystemSettings.GetColour(di_sistema)
                    getattr(controllo, imposta)(colore)
        self._aspetto = copy.deepcopy({chiave: self.impostazioni[chiave] for chiave in self._aspetto})
        for controllo in (self.console, self.cruscotto):
            self._ricolora(controllo)
        self._misura_il_cruscotto()
        self.albero.GetParent().Layout()
        for controllo in aree.values():
            controllo.Refresh()

    def _misura_il_cruscotto(self):
        """L'altezza minima del cruscotto, misurata sul suo carattere e non in
        pixel: cinque righe, ma non oltre un terzo della finestra; due righe
        pero' sempre, anche oltre il terzo in una finestra bassa. Con caratteri molto grandi le cinque righe si
        mangiavano plancia e console (Gabriele, 1 ottobre 2026): il cruscotto
        allora ne mostra meno e scorre. Vero se la misura e' cambiata."""
        riga = self.cruscotto.GetCharHeight()
        terzo = self.albero.GetParent().GetClientSize().height // 3
        altezza = max(riga * 2 + 8, min(riga * 6 + 8, terzo)) if terzo > 0 else riga * 6 + 8
        if self.cruscotto.GetMinSize().height == altezza:
            return False
        self.cruscotto.SetMinSize(wx.Size(-1, altezza))
        return True

    def _pannello_ridimensionato(self, evento):
        # Il terzo della finestra cambia con la finestra: alla partenza, che e'
        # massimizzata, e a ogni cambio di misura. Il gestore di wx che segue
        # rifa' la disposizione con il minimo nuovo.
        self._misura_il_cruscotto()
        evento.Skip()

    @staticmethod
    def _ricolora(controllo):
        """Rida' a tutto il testo di una console il colore dei caratteri, se
        ne ha uno suo: un carattere nuovo, o un testo riscritto, lo possono
        riportare a quello di Windows. SetForegroundColour con il colore di
        prima non fa niente, per questo il colore va per un'altra strada,
        quella di SetFont, che non tocca la selezione."""
        if controllo.UseForegroundColour():
            controllo.SetStyle(-1, -1, wx.TextAttr(controllo.GetForegroundColour()))

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
            posizione = max(0, posizione - self._taglia_la_console(limite))
        self.console.SetInsertionPoint(posizione)

    def _taglia_la_console(self, limite):
        """Toglie dalla cima della console le righe oltre il limite e
        restituisce quante posizioni del controllo ha tolto, per chi deve
        rimettere il cursore."""
        togliere = len(self._righe) - limite
        if togliere <= 0:
            return 0
        caratteri = self._unita("".join(r + "\n" for r in self._righe[:togliere]))
        self.console.Remove(0, caratteri)
        del self._righe[:togliere]
        if self._posizione_della_console is not None:
            self._posizione_della_console = max(0, self._posizione_della_console - caratteri)
        return caratteri

    def _suono(self, evento):
        """Suona l'effetto dell'evento; vero se e' partito, falso se il
        volume degli effetti e' a zero."""
        return suoni.suona(evento, self.impostazioni["volume_effetti"])

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
        # Un controllo RichEdit riscritto puo' perdere il colore dei caratteri.
        self._ricolora(self.cruscotto)
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
                "Canc toglie i brani dalle playlist ed elimina le playlist e i marker, Maiuscolo+Canc manda i file nel cestino, F4 li mette nei Preferiti.",
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
        """I tasti di tutta la finestra. Quando un comando ha finito il suo
        lavoro, dialoghi compresi, il beep dice se ha portato il fuoco della
        plancia a un altro livello."""
        prima = self._profondita(self._voce_corrente())
        if self._esegui_il_tasto(evento):
            self._controlla_il_livello(prima)

    def _esegui_il_tasto(self, evento):
        """Esegue il tasto, se e' un comando, e torna vero; altrimenti lo
        lascia passare e torna falso."""
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
            return True
        if modificatori == wx.MOD_SHIFT and codice == wx.WXK_F8:
            self._aggancia()
            return True
        # Il tastierino numerico resta a NVDA, e Ctrl e Alt ai comandi di Windows.
        if modificatori not in (wx.MOD_NONE, wx.MOD_SHIFT) or wx.WXK_NUMPAD0 <= codice <= wx.WXK_NUMPAD_DIVIDE:
            evento.Skip()
            return False
        unicode = evento.GetUnicodeKey()
        if unicode == wx.WXK_NONE or unicode <= 32:
            evento.Skip()
            return False
        carattere = chr(unicode).lower()
        maiuscolo = modificatori == wx.MOD_SHIFT
        if carattere.isdigit() and not maiuscolo:
            self._playlist_numero(int(carattere) or 10)
            return True
        # Maiuscolo con le cifre: i primi dieci marker. Windows puo' dare la
        # cifra con il Maiuscolo o il segno che la tastiera italiana ci mette sopra.
        if maiuscolo and (carattere.isdigit() or carattere in CIFRE_COL_MAIUSCOLO):
            self._marker_numero((int(carattere) or 10) if carattere.isdigit() else CIFRE_COL_MAIUSCOLO[carattere])
            return True
        comando = TASTI.get((carattere, maiuscolo))
        if comando:
            getattr(self, f"_comando_{comando}")()
            return True
        futuro = FUTURI_MAIUSCOLI.get(carattere) if maiuscolo else FUTURI.get(carattere)
        if futuro:
            self._riscontro("non_disponibile", f"Il tasto {chr(unicode)} sarà per: {futuro}. Non ancora disponibile.")
            return True
        evento.Skip()
        return False

    def _tasto_nell_albero(self, evento):
        codice = evento.GetKeyCode()
        prima = self._profondita(self._voce_corrente())
        if self._esegui_nell_albero(evento):
            self._controlla_il_livello(prima)
        elif codice not in _SOLO_MODIFICATORI:
            # Le frecce e gli altri tasti del controllo spostano il fuoco dopo
            # questo gestore: si guarda quando hanno finito.
            wx.CallAfter(self._controlla_il_livello, prima)

    def _esegui_nell_albero(self, evento):
        """I tasti propri della plancia: torna vero se ne ha eseguito uno,
        falso se lo lascia al controllo."""
        codice = evento.GetKeyCode()
        modificatori = evento.GetModifiers()
        spostamento = codice in (wx.WXK_UP, wx.WXK_DOWN, wx.WXK_HOME, wx.WXK_END, wx.WXK_PAGEUP, wx.WXK_PAGEDOWN)
        con_ancora = spostamento and modificatori in (wx.MOD_SHIFT, wx.MOD_CONTROL)
        if codice in (wx.WXK_LEFT, wx.WXK_RIGHT) and modificatori == wx.MOD_NONE:
            # Le frecce aprono e chiudono i rami dopo questo gestore, nel
            # controllo: i suoni li danno gli eventi dell'albero, finche'
            # dura questa pressione.
            self._freccia_nell_albero = True
            wx.CallAfter(self._fine_della_freccia)
        if codice == wx.WXK_SPACE and modificatori == wx.MOD_CONTROL:
            # Ctrl+Spazio, che seleziona e deseleziona da se', fissa l'ancora
            # sulla voce col fuoco, come in Esplora risorse.
            self._ancora = self._fuoco_atteso = self._voce_corrente()
        elif not con_ancora and codice not in _SOLO_MODIFICATORI:
            # Gli altri tasti lasciano l'ancora: il prossimo Maiuscolo con le
            # frecce riparte dalla voce col fuoco. Maiuscolo o Ctrl premuti
            # da soli arrivano anche loro qui, e non contano.
            self._ancora = None
        if con_ancora:
            self._muovi_il_fuoco(codice, allarga=modificatori == wx.MOD_SHIFT)
        elif codice == wx.WXK_BACK and modificatori == wx.MOD_NONE:
            self._risali()
        elif codice == wx.WXK_BACK and modificatori == wx.MOD_SHIFT:
            self._risali_all_antenato()
        elif codice == wx.WXK_SPACE and evento.GetModifiers() == wx.MOD_NONE:
            # Il livello lo guarda chi ha chiamato, quando il menu ha finito.
            self._menu(self._voce_di_lavoro())
        elif codice == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_NONE and len(self._voci_selezionate()) > 1:
            self._cancella_selezione()
        elif codice == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_SHIFT and len(self._voci_selezionate()) > 1:
            self._cestina_selezione()
        elif codice == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_NONE:
            self._cancella(self._voce_di_lavoro())
        elif codice == wx.WXK_DELETE and evento.GetModifiers() == wx.MOD_SHIFT:
            self._al_cestino(self._voce_di_lavoro())
        else:
            evento.Skip()
            return False
        return True

    # L'albero.

    def _voce_corrente(self):
        """La voce che ha il fuoco nella plancia. Con la selezione multipla non
        c'e' piu' "la voce selezionata": c'e' questa, piu' l'insieme delle
        selezionate."""
        return self.albero.GetFocusedItem()

    def _profondita(self, voce):
        """Il livello della voce nella plancia: 1 per le voci principali,
        2 per quelle dentro di loro e cosi' via; 0 se non c'e' una voce."""
        radice = self.albero.GetRootItem()
        livello = 0
        while voce.IsOk() and voce != radice:
            livello += 1
            voce = self.albero.GetItemParent(voce)
        return livello

    def _controlla_il_livello(self, prima):
        """Se un tasto ha portato il fuoco della plancia a un altro livello,
        un beep breve ne dice la profondita'. Non quando si lavora nella
        console o nel cruscotto: li' il livello della plancia non c'entra."""
        if not self or self._chiusa or wx.Window.FindFocus() in (self.console, self.cruscotto):
            return
        dopo = self._profondita(self._voce_corrente())
        if not dopo or dopo == prima:
            return
        self._turno_del_beep += 1
        self._beep_del_livello(self._turno_del_beep, dopo)

    def _beep_del_livello(self, turno, profondita, rimandato=False):
        """Il beep aspetta che finisca il suono del comando, come quello di
        Backspace: sovrapposti stridono (Gabriele, collaudo della 1.42.2). Se
        intanto un altro tasto ha cambiato di nuovo livello, tace: suona solo
        il beep dell'ultimo. Tace anche se, mentre aspettava, il fuoco ha
        lasciato la plancia, per esempio per un dialogo."""
        if not self or self._chiusa or turno != self._turno_del_beep:
            return
        fuoco = wx.Window.FindFocus()
        if fuoco in (self.console, self.cruscotto) or (rimandato and fuoco is not self.albero):
            return
        attesa = suoni.attesa()
        if attesa > 0:
            # Un timer di Python che poi torna nel filo della finestra; se nel
            # frattempo il programma si chiude, non trattiene l'uscita.
            timer = threading.Timer(attesa + 0.02, lambda: wx.GetApp() and wx.CallAfter(self._beep_del_livello, turno, profondita, True))
            timer.daemon = True
            timer.start()
        else:
            suoni.livello(profondita, self.impostazioni["volume_effetti"])

    def _voce_di_lavoro(self):
        """La voce su cui agiscono i comandi per una voce sola, come Canc, X,
        F4 e il menu: quella col fuoco; ma se Ctrl con le frecce ha portato
        il fuoco su una voce non selezionata, e di selezionate ce n'e' una,
        e' lei, come in Esplora risorse."""
        voce = self._voce_corrente()
        selezionate = self._voci_selezionate()
        if len(selezionate) == 1 and voce.IsOk() and not self.albero.IsSelected(voce):
            return selezionate[0]
        return voce

    def _sposta_il_cursore(self, voce):
        """Porta il fuoco della plancia sulla voce come fa Windows con le
        frecce. wx, per spostarlo da una voce selezionata, toglie per un
        istante la selezione a tutto l'albero: il fuoco cade sull'albero
        stesso e NVDA ne legge il nome a ogni pressione. Il messaggio diretto
        a Windows lo evita; le selezioni le rimette poi chi chiama."""
        _manda_messaggio(self.albero.GetHandle(), _TVM_SELECTITEM, _TVGN_CARET, int(voce.GetID()))

    def _voci_visibili_per_pagina(self):
        return max(1, _manda_messaggio(self.albero.GetHandle(), _TVM_GETVISIBLECOUNT, 0, 0))

    def _ultima_visibile(self):
        """L'ultima voce della plancia che si legge scendendo, dentro i rami aperti."""
        voce = self.albero.GetLastChild(self.albero.GetRootItem())
        while voce.IsOk() and self.albero.IsExpanded(voce) and self.albero.GetChildrenCount(voce, False):
            voce = self.albero.GetLastChild(voce)
        return voce if voce.IsOk() else None

    def _cammino(self, da, a):
        """Le voci fra da e a nell'ordine della plancia, estremi compresi, o
        None se a non si vede da da. Si parte da da e si confronta soltanto
        a: cosi' a puo' essere una voce che la plancia ha gia' tolto."""
        for passo in (self._dopo, self._prima):
            voci = [da]
            while voci[-1] != a:
                seguente = passo(voci[-1])
                if seguente is None:
                    break
                voci.append(seguente)
            if voci[-1] == a:
                return voci
        return None

    def _muovi_il_fuoco(self, codice, allarga):
        """Maiuscolo o Ctrl con le frecce, Inizio, Fine, Pagina su e giu',
        come in Esplora risorse. Con Maiuscolo la selezione va dall'ancora,
        la voce da cui si e' cominciato ad allargare, fino alla voce
        d'arrivo; con Ctrl si muove solo il fuoco e le selezioni restano."""
        voce = self._voce_corrente()
        if not voce.IsOk():
            return
        if codice in (wx.WXK_HOME, wx.WXK_END):
            arrivo = next(self._figli(self.albero.GetRootItem()), None) if codice == wx.WXK_HOME else self._ultima_visibile()
        else:
            passo = self._dopo if codice in (wx.WXK_DOWN, wx.WXK_PAGEDOWN) else self._prima
            arrivo = voce
            for _ in range(self._voci_visibili_per_pagina() if codice in (wx.WXK_PAGEUP, wx.WXK_PAGEDOWN) else 1):
                seguente = passo(arrivo)
                if seguente is None:
                    break
                arrivo = seguente
        if arrivo is None or arrivo == voce:
            return
        # L'ancora vale finche' il fuoco sta dove l'hanno lasciato Maiuscolo
        # o Ctrl con le frecce, e finche' si vede ancora: si cerca partendo
        # dalla voce col fuoco, perche' l'ancora puo' essere sparita.
        if self._ancora is None or self._fuoco_atteso != voce or self._cammino(voce, self._ancora) is None:
            self._ancora = voce
        # Con Maiuscolo la selezione e' l'intervallo dall'ancora; con Ctrl
        # restano le selezioni di prima.
        da_selezionare = set(self._cammino(self._ancora, arrivo) or [arrivo]) if allarga else set(self._voci_selezionate())
        self._sposta_il_cursore(arrivo)
        self._fuoco_atteso = arrivo
        if allarga:
            for altra in self._voci_selezionate():
                if altra not in da_selezionare:
                    self.albero.SelectItem(altra, False)
        elif arrivo not in da_selezionare:
            self.albero.SelectItem(arrivo, False)
        for scelta in da_selezionare:
            self.albero.SelectItem(scelta)

    def _risali(self):
        """Backspace: chiude il ramo in cui sta la voce col fuoco e ci porta il
        fuoco; premuto ancora risale di un livello, chiudendo anche quello."""
        voce = self._voce_corrente()
        ramo = self.albero.GetItemParent(voce) if voce.IsOk() else None
        if ramo is None or not ramo.IsOk() or ramo == self.albero.GetRootItem():
            self._riscontro("nessun_altro_brano", "Sei già al primo livello della plancia.")
            return
        self.albero.Collapse(ramo)
        self._seleziona(ramo)
        self._riscontro("risali", f"Chiuso {self.albero.GetItemText(ramo)}.", "risali")

    def _risali_all_antenato(self):
        """Maiuscolo con Backspace: risale di colpo al ramo antenato, quello
        di secondo livello che contiene la voce col fuoco, come l'unita' in
        Questo PC o la playlist nel ramo Playlist; nei Preferiti, che sono
        una playlist al primo livello, i Preferiti stessi. L'antenato resta
        aperto e i rami dentro di lui si chiudono, cosi' le sue voci si
        scorrono subito per scendere in un ramo fratello (Gabriele, collaudo
        della 1.42.2)."""
        voce = self._voce_corrente()
        if not voce.IsOk() or self._profondita(voce) < 2:
            self._riscontro("nessun_altro_brano", "Sei già al primo livello della plancia.")
            return
        antenato = voce
        while self._profondita(antenato) > 2:
            antenato = self.albero.GetItemParent(antenato)
        if self.albero.GetItemParent(antenato) == self.nodo_preferiti:
            antenato = self.nodo_preferiti
        # Il fuoco va sull'antenato prima di chiudere i rami in cui stava.
        self._seleziona(antenato)
        chiusi = False
        for figlio in list(self._figli(antenato)):
            if self.albero.ItemHasChildren(figlio):
                chiusi = chiusi or self.albero.IsExpanded(figlio)
                self.albero.CollapseAllChildren(figlio)
        self.albero.EnsureVisible(antenato)
        # Della playlist il nome soltanto, senza i conti dell'etichetta.
        pl = (self._dati(antenato) or {}).get("playlist")
        nome = pl.nome if pl is not None else self.albero.GetItemText(antenato)
        if antenato == voce:
            # Gia' sull'antenato: non si sale, si chiudono solo i rami dentro.
            dentro = " Chiusi i rami aperti al suo interno." if chiusi else ""
            self._riscontro("nessun_altro_brano", f"Sei già su {nome}, non si risale oltre.{dentro}")
            return
        self._riscontro("risali_all_antenato", f"Risalito a {nome}.", "risali")

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
        if dati["tipo"] == "marker":
            return f"{dati['marker']['nome']}, {durata_lunga(dati['marker']['tempo'])}"
        suona = bool(self.motore.in_corso) and brano is self.coda.corrente
        quanti = len(self._marker_della_voce(dati))
        if dati["tipo"] == "sottobrano":
            n = dati["numero"]
            parti = [f"Sottobrano {n} di {dati['totale']}, {tempo(durata_del_sottobrano(brano.percorso, n))}"]
            if quanti:
                parti.append(f"{quanti} marker")
            if suona and self.motore.sottobrano == n:
                parti.append("in riproduzione")
            return ", ".join(parti)
        parti = [brano.percorso if dati.get("completo") else brano.nome_del_file]
        if brano.sottobrano:
            info = songlengths.info_del_sid(brano.percorso)
            parti[0] += f", sottobrano {brano.sottobrano} di {info['sottobrani'] if info else '?'}"
        parti.extend(self._durata_nella_plancia(brano))
        if quanti:
            parti.append(f"{quanti} marker")
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
        if self._ha_sottobrani(brano) or self._marker_della_voce(dati):
            dati["caricato"] = False
            self.albero.SetItemHasChildren(voce, True)
        return voce

    def _aggiorna_etichette(self):
        """Rinfresca le etichette di brani, file e sottobrani: saltato, loop, marker, in riproduzione."""
        for voce in self._tutte_le_voci():
            dati = self._dati(voce)
            if not dati or dati["tipo"] not in ("brano", "file", "sottobrano"):
                continue
            nuova = self._etichetta(dati)
            if self.albero.GetItemText(voce) != nuova:
                self.albero.SetItemText(voce, nuova)
                if dati["tipo"] != "marker" and not self.albero.ItemHasChildren(voce) and self._marker_della_voce(dati):
                    dati["caricato"] = False
                    self.albero.SetItemHasChildren(voce, True)

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
        passano il filtro, non solo i conti dell'etichetta. Chiusa con la
        freccia sinistra, ha il suo suono."""
        evento.Skip()
        dati = self._dati(evento.GetItem()) or {}
        if dati.get("tipo") == "playlist":
            dati["caricato"] = False
        if self._freccia_nell_albero:
            self._suono("ramo_chiuso")

    def _aperta_una_voce(self, evento):
        """Un ramo aperto con la freccia destra ha il suo suono, ogni volta e
        per ogni ramo. I rami che aprono i comandi, come F10, J e K, no:
        quei comandi hanno gia' il loro."""
        evento.Skip()
        if self._freccia_nell_albero:
            self._suono("ramo_aperto")

    def _fine_della_freccia(self):
        self._freccia_nell_albero = False

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
        if tipo in ("brano", "file") and self._ha_sottobrani(dati["brano"]):
            brano = dati["brano"]
            totale = songlengths.info_del_sid(brano.percorso)["sottobrani"]
            for n in range(1, totale + 1):
                figlio = {"tipo": "sottobrano", "playlist": dati["playlist"], "brano": brano, "numero": n, "totale": totale}
                sotto = self.albero.AppendItem(voce, self._etichetta(figlio), data=figlio)
                if self._marker_della_voce(figlio):
                    figlio["caricato"] = False
                    self.albero.SetItemHasChildren(sotto, True)
            return
        if tipo in ("brano", "file", "sottobrano"):
            for marker in self._marker_della_voce(dati):
                figlio = {"tipo": "marker", "playlist": dati["playlist"], "brano": dati["brano"], "numero": dati.get("numero") or dati["brano"].sottobrano,
                    "chiave": self._chiave_della_voce(dati), "marker": marker}
                self.albero.AppendItem(voce, self._etichetta(figlio), data=figlio)
            if not self.albero.GetChildrenCount(voce, False):
                self.albero.SetItemHasChildren(voce, False)
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
            self._riscontro("niente_da_suonare", "Niente da suonare qui dentro.")

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
        prima = self._profondita(self._voce_corrente())
        self._esegui_invio(evento)
        self._controlla_il_livello(prima)

    def _esegui_invio(self, evento):
        voce = self._voce_di_lavoro() if evento.GetItem() == self._voce_corrente() else evento.GetItem()
        dati = self._dati(voce)
        if len(self._voci_selezionate()) > 1:
            self._menu(voce)
        elif dati and dati["tipo"] == "comando":
            getattr(self, f"_comando_{dati['comando']}")()
        elif dati and dati["tipo"] == "altri":
            self._altri_risultati()
        elif dati and dati["tipo"] == "marker":
            self._rinomina_il_marker(dati["chiave"], dati["marker"])
        else:
            self._menu(voce)

    def _menu_da_evento(self, evento):
        # Dalla tastiera la voce dell'evento e' quella col fuoco; col mouse e'
        # quella su cui si e' cliccato.
        prima = self._profondita(self._voce_corrente())
        self._menu(self._voce_di_lavoro() if evento.GetItem() == self._voce_corrente() else evento.GetItem())
        self._controlla_il_livello(prima)

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
                ("Aggiungi ai preferiti", lambda: self._ai_preferiti(brano)), ("Manda nel cestino", lambda: self._al_cestino(self._voce_di_lavoro()))]
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
                ("Aggiungi ai preferiti", lambda: self._ai_preferiti(brano)), ("Manda nel cestino", lambda: self._al_cestino(self._voce_di_lavoro()))]
        if tipo == "marker":
            return [("Vai al marker", lambda: self._vai_al_marker(dati)), ("Rinomina", lambda: self._rinomina_il_marker(dati["chiave"], dati["marker"])),
                ("Elimina", lambda: self._elimina_il_marker(dati["chiave"], dati["marker"], self._voce_di_lavoro()))]
        if tipo == "sottobrano":
            pl, brano, n = dati["playlist"], dati["brano"], dati["numero"]
            return [("Riproduci", lambda: self._riproduci(pl, brano, n)),
                ("Aggiungi alla playlist", self._menu_aggiungi(lambda: [Brano(brano.percorso, sottobrano=n)])),
                ("Aggiungi ai preferiti", lambda: self._ai_preferiti(Brano(brano.percorso, sottobrano=n)))]
        return []

    def _conferma(self, domanda, titolo, genitore=None):
        """Una domanda con Si' e No, e No come risposta predefinita. Da un
        dialogo, il genitore e' lui: chiudendosi, la domanda gli rende il
        fuoco."""
        self._suono("domanda")
        with wx.MessageDialog(genitore or self, domanda, titolo, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dialogo:
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
        elif dati.get("tipo") == "marker":
            self._elimina_il_marker(dati["chiave"], dati["marker"], voce)
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
            ("Togli dalle playlist, ed elimina le playlist e i marker selezionati", self._cancella_selezione), ("Manda nel cestino", self._cestina_selezione)]

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
        marker = [(v, d["chiave"], d["marker"]) for v, d in voci if d.get("tipo") == "marker"]
        if not (da_eliminare or da_togliere or marker):
            self._riscontro("non_disponibile", "Nella selezione non c'è niente che Canc possa togliere: brani di playlist, playlist o marker.")
            return
        if da_eliminare and not self._conferma(f"Eliminare {len(da_eliminare)} playlist? I file restano sul disco.", "Elimina playlist"):
            self.scrivi("Eliminazione annullata.")
            return
        approdo = self._approdo([v for v, d in voci if d.get("tipo") == "playlist" and d["playlist"] in da_eliminare] + [v for v, _pl, _b in da_togliere]
            + [v for v, _k, _m in marker])
        for pl in da_eliminare:
            self.archivio.elimina(pl)
        for _voce, pl, brano in da_togliere:
            pl.togli(brano)
            if self.coda.loop_playlist is pl and brano in (self.coda.punto_a, self.coda.punto_b):
                self.coda.togli_loop()
        # Lo stesso marker puo' comparire sotto piu' copie dello stesso file.
        tolti_marker = sum(self.marcatori.togli(k, m) for k, m in {(k, m["tempo"]): (k, m) for _v, k, m in marker}.values())
        if da_eliminare or da_togliere:
            self._salva_archivio()
            self._ricostruisci_dopo_la_cancellazione(approdo)
        elif approdo is not None:
            # Solo marker: le playlist restano come sono, il fuoco va sulla
            # voce vicina, e se e' un marker lo ritrova il rinfresco.
            self.albero.UnselectAll()
            self._seleziona(approdo)
        if marker:
            self._salva_i_marker(*{k for _v, k, _m in marker})
        parti = []
        if da_togliere:
            parti.append(f"{'tolto' if len(da_togliere) == 1 else 'tolti'} {brani_al_plurale(len(da_togliere))}")
        if da_eliminare:
            parti.append(f"{'eliminata' if len(da_eliminare) == 1 else 'eliminate'} {len(da_eliminare)} playlist")
        if tolti_marker:
            parti.append(f"{'eliminato' if tolti_marker == 1 else 'eliminati'} {tolti_marker} marker")
        self._riscontro("brano_tolto" if da_togliere or da_eliminare else "marker_eliminato", ", ".join(parti).capitalize() + ".")

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
        figlio = next((v for v in self._figli(voce) if (self._dati(v) or {}).get("tipo") == "sottobrano" and self._dati(v).get("numero") == numero), None)
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
        dati = self._dati(self._voce_di_lavoro()) or {}
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

    def _suona(self, pl, brano, evento="play", sottobrano=None, inizio=None, sfuma_lo_stesso=False):
        """Suona il brano e lo dice. Con la dissolvenza accesa il motore lo fa
        entrare sfumando, se qualcosa si sente; un seguente preparato non
        conta piu'. Con sfuma_lo_stesso sfuma anche ripartendo con il brano
        in corso, come X da capo."""
        self._uscente = self._preparato = None
        self.coda.imposta(pl, brano)
        self.motore.suona(brano.percorso, sottobrano or brano.sottobrano, inizio=inizio, sfuma_lo_stesso=sfuma_lo_stesso)
        self._annuncia(pl, brano, evento)

    def _annuncia(self, pl, brano, evento):
        """Il riscontro del brano appena partito, con la sua posizione nella
        lista e il sottobrano, le etichette della plancia e l'inseguimento."""
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
            # Un SID con i sottobrani aperti lascia il posto a loro; i marker no.
            return not dati["brano"].saltato and not (self.albero.IsExpanded(voce) and self._ha_sottobrani(dati["brano"]))
        return False

    def _voce_che_suona(self, sottobrano=None):
        """La voce visibile della plancia che corrisponde a cio' che suona, o
        None se non si vede: il sottobrano, se il SID e' aperto, altrimenti il
        brano o il file. Il sottobrano e' quello del motore, se non lo si da':
        al passaggio della dissolvenza il motore ha gia' quello che entra,
        mentre la coda e' ancora sul brano che esce."""
        corrente = self.coda.corrente
        if corrente is None:
            return None
        numero = self.motore.sottobrano if sottobrano is None else sottobrano
        for voce in self._tutte_le_voci():
            dati = self._dati(voce) or {}
            if dati.get("tipo") in ("brano", "file") and dati["brano"] is corrente and self._visibile(voce):
                if self.albero.IsExpanded(voce):
                    return next((v for v in self._figli(voce) if self._dati(v).get("tipo") == "sottobrano" and self._dati(v).get("numero") == numero), voce)
                return voce
        return None

    def _voce_da_seguire(self, sottobrano=None):
        """La voce visibile di cio' che suona, se a decidere il brano dopo e'
        la plancia; None se decide la lista, perche' non si vede, perche'
        c'e' il loop A-B o perche' suona una selezione."""
        if self.coda.intervallo() is not None or getattr(self.coda.playlist, "selezione", False):
            return None
        return self._voce_che_suona(sottobrano)

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

    def _seguente_automatico(self, sottobrano=None):
        """Cosa suonare quando un brano finisce da solo: (playlist, brano,
        sottobrano) o None. Se cio' che suona si vede nella plancia, decide la
        plancia: la voce suonabile che viene dopo, dentro i rami aperti,
        sottobrani compresi, anche in un'altra cartella o playlist. Se non si
        vede, per esempio una cartella suonata chiusa o un file aperto con
        Apri file, decide la lista. Con il loop A-B decide il loop.
        sottobrano e' quello del brano che finisce, se non e' quello del
        motore, come al passaggio della dissolvenza."""
        voce = self._voce_da_seguire(sottobrano)
        if voce is not None:
            return self._passo_in_plancia(voce, 1)
        seguente = self.coda.successivo()
        return (self.coda.playlist, seguente, None) if seguente else None

    def _evento_del_seguente(self, nuova, brano):
        """Il suono del passaggio automatico al brano della playlist nuova:
        nel loop, dopo il punto B si torna al punto A, e ha un suono suo. Da
        chiedere prima di spostare la coda."""
        pl = self.coda.playlist
        prima = pl.indice(self.coda.corrente) if pl else None
        dopo = nuova.indice(brano)
        ritorno = self.coda.intervallo() and nuova is pl and prima is not None and dopo is not None and dopo <= prima
        return "ritorno_al_punto_a" if ritorno else "brano_seguente_da_solo"

    def _brano_finito(self):
        """Il brano e' finito da solo, senza un seguente preparato che
        entrasse con la dissolvenza: si suona il seguente, se c'e'."""
        if self._chiusa:
            return
        self._uscente = self._preparato = None
        seguente = self._seguente_automatico()
        if seguente:
            nuova, brano, sottobrano = seguente
            self._suona(nuova, brano, self._evento_del_seguente(nuova, brano), sottobrano)
        else:
            self._fine_della_lista()

    def _fine_della_lista(self):
        self._aggiorna_etichette()
        self._riscontro("fine_playlist", "Fine: davanti non c'è altro da suonare.")

    # Il passaggio con la dissolvenza incrociata.

    def _prepara_il_seguente(self):
        """chiedi_il_seguente del motore: con la dissolvenza accesa, poco
        prima della fine del brano, il motore vuole il seguente da caricare in
        anticipo, che entrera' sfumando. Si sceglie come a fine brano; se non
        c'e', non si prepara niente e alla fine arriva _brano_finito."""
        if self._chiusa or not self.motore.in_corso:
            return
        seguente = self._seguente_automatico()
        if seguente is None:
            return
        _playlist, brano, sottobrano = seguente
        if self.motore.prepara(brano.percorso, sottobrano or brano.sottobrano):
            self._uscente = (self.coda.playlist, self.coda.corrente, self.motore.sottobrano)
            self._preparato = seguente

    def _passaggio(self, percorso, sottobrano):
        """al_passaggio del motore: il brano preparato e' entrato, sfumando o,
        se e' stato pronto tardi, alla fine di quello di prima. Il motore ha
        gia' il brano nuovo, la coda e' ancora su quello che esce. Si
        ricontrolla il seguente, perche' nel frattempo la plancia puo' essere
        cambiata: se e' lo stesso, o lo stesso file con lo stesso sottobrano
        in un altro posto della plancia, la coda passa a lui e lo si dice, e
        il motore non lo richiede, perche' lo farebbe ripartire da capo; se
        e' un altro si suona quello giusto, che entra sfumando dal punto in
        cui si e'; se non c'e' piu' niente da suonare, il brano che entra si
        scarta e quello che
        esce finisce da solo, e il Fine lo dice _brano_finito alla sua fine
        vera. Un avviso superato, perche' nel frattempo e' partito altro, non
        conta."""
        uscente, preparato = self._uscente, self._preparato
        self._uscente = self._preparato = None
        if self._chiusa or uscente is None or preparato is None or preparato[1].percorso != percorso:
            return
        # Un brano nuovo molto breve puo' essere gia' finito: in_corso e' None,
        # e il passaggio vale lo stesso.
        attivo = self.motore.in_corso
        if attivo is not None and (attivo != percorso or self.motore.sottobrano != sottobrano):
            return
        pl, corrente, sottobrano_uscente = uscente
        if self.coda.playlist is not pl or self.coda.corrente is not corrente:
            return
        seguente = self._seguente_automatico(sottobrano_uscente)
        if seguente is None:
            # La plancia non ha piu' niente dopo: come a fine lista, il brano
            # che esce arriva in fondo, e solo dopo si dice Fine. Se era gia'
            # finito, il motore ferma tutto e la lista finisce qui.
            if not self.motore.annulla_il_passaggio():
                self._fine_della_lista()
            return
        nuova, brano, numero = seguente
        evento = self._evento_del_seguente(nuova, brano)
        # Lo stesso file del preparato, per esempio in un'altra playlist, suona
        # gia' dall'inizio: si sposta solo la coda, senza farlo ripartire. Il
        # sottobrano si confronta come lo sceglie il motore: un SID suonato
        # come brano entra con il suo sottobrano iniziale.
        gia_entrato = brano.percorso == percorso and sottobrano_risolto(brano.percorso, numero or brano.sottobrano) == sottobrano
        if not gia_entrato and (nuova is not preparato[0] or brano is not preparato[1] or numero != preparato[2]):
            self._suona(nuova, brano, evento, numero)
            return
        self.coda.imposta(nuova, brano)
        self._annuncia(nuova, brano, evento)

    def _brano_in_errore(self, percorso):
        if self._chiusa:
            return
        self._uscente = self._preparato = None
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
        dati = self._dati(self._voce_di_lavoro()) or {}
        tipo = dati.get("tipo")
        corrente = self.coda.corrente
        if tipo == "marker":
            # X su un marker vale come X sul suo brano: lo suona dall'inizio, o
            # lo fa ripartire da capo se suona gia'. Da un marker suonano R, Y,
            # le cifre e Vai al marker (Gabriele, collaudo della 1.42.2).
            tipo = "sottobrano" if self._ha_sottobrani(dati["brano"]) else "brano"
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
            self.motore.pausa(False, sfumando=True)
            self._riscontro("ripresa", f"Riprende da {tempo(self.motore.posizione)}.")
        elif self.motore.in_corso:
            # Come in Winamp: X su cio' che sta suonando lo fa ripartire da capo;
            # con la dissolvenza accesa, sfumando (Gabriele, 2 ottobre 2026).
            self._suona(self.coda.playlist, corrente, "da_capo", self.motore.sottobrano if self.motore.sottobrani else None, sfuma_lo_stesso=True)
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
        self._apri_ramo(nodo, con_i_marker=False)
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

    def _comando_loop(self):
        """Maiuscolo con X, a giro (Gabriele, 2 ottobre 2026): senza loop mette
        il punto A sul brano selezionato; con il solo punto A mette il punto B,
        anche sullo stesso brano, che allora si ripete da solo; con A e B li
        toglie tutti e due, da qualsiasi punto."""
        coda = self.coda
        if coda.loop_playlist is not None and coda.punto_b is not None:
            coda.togli_loop()
            self._aggiorna_etichette()
            self._riscontro("loop_tolto", "Loop tolto: si suona di nuovo tutta la lista.")
            return
        dati = self._dati(self._voce_di_lavoro()) or {}
        if dati.get("tipo") not in ("brano", "file", "sottobrano"):
            self._riscontro("loop_non_qui", "Il loop si mette su un brano: scegline uno in una playlist o in una cartella.")
            return
        pl, brano = dati["playlist"], dati["brano"]
        if coda.loop_playlist is None:
            coda.loop_playlist, coda.punto_a, coda.punto_b = pl, brano, None
            self._riscontro("loop_a_messo", f"Punto A del loop su {brano.nome_del_file}. Maiuscolo+X su un altro brano mette il punto B.")
        elif coda.loop_playlist is not pl:
            self._riscontro("loop_non_qui", f"Il punto A sta in {coda.loop_playlist.nome}: il punto B va su un brano della stessa lista.")
            return
        else:
            coda.punto_b = brano
            primo, ultimo = coda.intervallo(pl)
            self._riscontro("loop_b_messo", f"Loop fra {coda.punto_a.nome_del_file} e {brano.nome_del_file}: {brani_al_plurale(ultimo - primo + 1)}. Maiuscolo+X lo toglie.")
        self._aggiorna_etichette()

    def _comando_pausa(self):
        if self._niente_in_corso():
            return
        if self.motore.pausa(sfumando=True):
            self._riscontro("pausa", f"Pausa a {tempo(self.motore.posizione)}.")
        else:
            self._riscontro("ripresa", f"Riprende da {tempo(self.motore.posizione)}.")

    def _comando_stop(self):
        if self._niente_in_corso():
            return
        # Con la dissolvenza accesa il brano si spegne piano, e il motore e'
        # subito libero (Gabriele, 2 ottobre 2026).
        self.motore.stop(sfumando=True)
        self._uscente = self._preparato = None
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

    # Velocita', tono, equalizzatore e dissolvenza, tappa 4 (issue 15): valgono
    # per tutti i brani, e ogni cambio si salva subito. Le righe della console
    # si riscrivono, una categoria per famiglia, e stanno nei quaranta
    # caratteri del display braille.

    def _applica_la_riproduzione(self):
        """Da' al motore velocita', tono, bande e dissolvenza delle impostazioni."""
        imp = self.impostazioni
        self.motore.velocita = imp["velocita"]
        self.motore.tono = imp["tono"]
        self.motore.bande = imp["bande"]
        self._applica_la_dissolvenza()

    def _applica_la_dissolvenza(self):
        dissolvenza = self.impostazioni["dissolvenza"]
        self.motore.dissolvenza = dissolvenza["secondi"] if dissolvenza["accesa"] else 0

    def _riproduzione_fuori_dal_normale(self):
        """La riga dell'avvio su velocita' e tono, se non sono quelli normali;
        vuota se lo sono."""
        velocita, tono = self.impostazioni["velocita"], self.impostazioni["tono"]
        if velocita != 1 and tono:
            return f"Velocità {valori.scrivi_velocita(velocita)} e tono {valori.scrivi_tono(tono)}: S e G li riportano al normale."
        if velocita != 1:
            return f"Velocità {valori.scrivi_velocita(velocita)}: S la riporta al normale."
        if tono:
            return f"Tono {valori.scrivi_tono(tono)}: G lo riporta al normale."
        return ""

    @staticmethod
    def _riga_della_velocita(velocita):
        return f"Velocità {valori.scrivi_velocita(velocita)}{', la normale' if velocita == 1 else ''}."

    @staticmethod
    def _riga_del_tono(tono):
        return f"Tono {valori.scrivi_tono(tono)}{', il normale' if tono == 0 else ''}."

    def _velocita(self, nuova, evento):
        """Porta la velocita' a nuova, nei limiti; ai limiti lo dice con il
        suono suo."""
        attuale = self.impostazioni["velocita"]
        nuova = max(valori.VELOCITA_MINIMA, min(valori.VELOCITA_MASSIMA, round(nuova, 2)))
        if nuova == attuale and evento != "velocita_normale":
            limite = "massimo" if nuova >= valori.VELOCITA_MASSIMA else "minimo"
            self._riscontro("velocita_al_limite", f"Velocità già al {limite}, {valori.scrivi_velocita(attuale)}.", "velocita")
            return
        self.motore.velocita = nuova
        self.impostazioni["velocita"] = nuova
        self._salva_impostazioni()
        self._riscontro(evento, self._riga_della_velocita(nuova), "velocita")

    def _comando_velocita_su(self):
        self._velocita(self.impostazioni["velocita"] + valori.PASSO_VELOCITA, "velocita_su")

    def _comando_velocita_giu(self):
        self._velocita(self.impostazioni["velocita"] - valori.PASSO_VELOCITA, "velocita_giu")

    def _comando_velocita_normale(self):
        self._velocita(1.0, "velocita_normale")

    def _tono(self, nuovo, evento):
        """Porta il tono a nuovo semitoni, nei limiti; ai limiti lo dice con il
        suono suo."""
        attuale = self.impostazioni["tono"]
        nuovo = max(-valori.TONO_MASSIMO, min(valori.TONO_MASSIMO, nuovo))
        if nuovo == attuale and evento != "tono_normale":
            limite = "massimo" if nuovo > 0 else "minimo"
            self._riscontro("tono_al_limite", f"Tono già al {limite}, {valori.scrivi_tono(attuale)}.", "tono")
            return
        self.motore.tono = nuovo
        self.impostazioni["tono"] = nuovo
        self._salva_impostazioni()
        self._riscontro(evento, self._riga_del_tono(nuovo), "tono")

    def _comando_tono_su(self):
        self._tono(self.impostazioni["tono"] + 1, "tono_su")

    def _comando_tono_giu(self):
        self._tono(self.impostazioni["tono"] - 1, "tono_giu")

    def _comando_tono_normale(self):
        self._tono(0, "tono_normale")

    def _riga_della_banda(self, aggiunta=""):
        """La riga della banda scelta: Banda 3, 400 Hz: +2 dB. La maiuscola
        non viene da capitalize, che scriverebbe hz."""
        nome = valori.nome_della_banda(self._banda)
        guadagno = valori.scrivi_guadagno(self.impostazioni["bande"][self._banda])
        return f"{nome[0].upper()}{nome[1:]}: {guadagno}{aggiunta}."

    def _scegli_la_banda(self, passo):
        """U e I: la banda prima o dopo; si fermano alla prima e all'ultima. Il
        suono, fatto al volo, dice la banda con una nota della scala."""
        nuova = self._banda + passo
        if not 0 <= nuova < len(valori.FREQUENZE_DELLE_BANDE):
            self._riscontro("banda_al_limite", self._riga_della_banda(". È la prima" if passo < 0 else ". È l'ultima"), "banda")
            return
        self._banda = nuova
        suoni.banda(nuova, self.impostazioni["volume_effetti"])
        self.scrivi(self._riga_della_banda(), "banda")

    def _comando_banda_precedente(self):
        self._scegli_la_banda(-1)

    def _comando_banda_successiva(self):
        self._scegli_la_banda(1)

    def _metti_le_bande(self, bande):
        """Scrive i guadagni nel motore e nelle impostazioni, e li salva."""
        self.motore.bande = bande
        self.impostazioni["bande"] = list(bande)
        self._salva_impostazioni()

    def _guadagno(self, passo):
        """O e P: la banda scelta su o giu' di un dB; ai limiti lo dicono. Il
        suono, fatto al volo, dice il guadagno con l'altezza della nota."""
        bande = list(self.impostazioni["bande"])
        nuovo = max(-valori.GUADAGNO_MASSIMO, min(valori.GUADAGNO_MASSIMO, bande[self._banda] + passo))
        if nuovo == bande[self._banda]:
            self._riscontro("guadagno_al_limite", self._riga_della_banda(", il massimo" if passo > 0 else ", il minimo"), "banda")
            return
        bande[self._banda] = nuovo
        self._metti_le_bande(bande)
        suoni.guadagno(nuovo, self.impostazioni["volume_effetti"])
        self.scrivi(self._riga_della_banda(), "banda")

    def _comando_banda_su(self):
        self._guadagno(1)

    def _comando_banda_giu(self):
        self._guadagno(-1)

    def _comando_azzera_la_banda(self):
        bande = list(self.impostazioni["bande"])
        bande[self._banda] = 0
        self._metti_le_bande(bande)
        self._riscontro("banda_azzerata", self._riga_della_banda(", azzerata"), "banda")

    def _comando_azzera_le_bande(self):
        self._metti_le_bande([0] * len(valori.FREQUENZE_DELLE_BANDE))
        self._riscontro("bande_azzerate", "Equalizzatore azzerato, tutte a 0 dB.", "banda")

    def _comando_dissolvenza(self):
        """L: accende e spegne la dissolvenza; la durata resta."""
        dissolvenza = self.impostazioni["dissolvenza"]
        dissolvenza["accesa"] = not dissolvenza["accesa"]
        self._applica_la_dissolvenza()
        self._salva_impostazioni()
        evento = "dissolvenza_accesa" if dissolvenza["accesa"] else "dissolvenza_spenta"
        self._riscontro(evento, f"Dissolvenza {valori.scrivi_dissolvenza(dissolvenza)}.", "dissolvenza")

    def _comando_durata_della_dissolvenza(self):
        """Maiuscolo con L: chiede la durata della dissolvenza in secondi. La
        dissolvenza resta accesa o spenta com'era."""
        self._suono("domanda")
        dissolvenza = self.impostazioni["dissolvenza"]
        attuale = dissolvenza["secondi"]
        da_leggere = valori.scrivi_durata(attuale)
        # Nel campo e nella domanda i numeri soli, senza la parola secondi.
        minimo, massimo, numero = (valori.scrivi_durata(s).split()[0] for s in (valori.DISSOLVENZA_MINIMA, valori.DISSOLVENZA_MASSIMA, attuale))
        with DialogoTesto(self, f"Quanti secondi dura la dissolvenza? Da {minimo} a {massimo}, anche con i decimali, per esempio 2,5.",
                "Durata della dissolvenza", numero) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            testo = dialogo.GetValue()
        try:
            secondi, correzioni = valori.leggi_durata_della_dissolvenza(testo)
        except ErroreValore as e:
            self._riscontro("errore", f"{e} La durata resta di {da_leggere}.")
            return
        dissolvenza["secondi"] = secondi
        self._applica_la_dissolvenza()
        self._salva_impostazioni()
        self._riscontro("dissolvenza_durata", " ".join([f"Dissolvenza {valori.scrivi_dissolvenza(dissolvenza)}.", *correzioni]), "dissolvenza")

    def _comando_apri_file(self):
        with DialogoDiFile(self, "Apri file", wildcard=formati.filtro_dialogo(), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                return
            percorso = dialogo.GetPath()
        # Il file aperto non entra in nessuna playlist: resta finche' non si
        # suona altro. La sua cartella vuota lo tiene fuori da Questo PC.
        pl = Playlist("file aperto", [Brano(percorso)], cartella="")
        self._suona(pl, pl.brani[0], "file_aperto")

    # Le impostazioni, piano 5.8.

    def _comando_impostazioni(self):
        """La finestra delle impostazioni: una lista piatta, una riga per voce;
        Invio su una voce la cambia, o fa la sua azione."""
        self._suono("impostazioni")
        with FinestraImpostazioni(self, self._voci_delle_impostazioni(), self._cambia_impostazione) as dialogo:
            dialogo.ShowModal()

    def _voci_delle_impostazioni(self):
        """Le righe della finestra delle impostazioni, come (chiave, "Etichetta: valore")."""
        return [(chiave, self._riga_dell_impostazione(chiave)) for chiave in VOCI_DELLE_IMPOSTAZIONI]

    def _riga_dell_impostazione(self, chiave):
        imp = self.impostazioni
        valore = {
            "volume": lambda: str(imp["volume"]),
            "passo_volume": lambda: str(imp["passo_volume"]),
            "volume_effetti": lambda: f"{round(imp['volume_effetti'] * 100)}%",
            "scheda_audio": self._scheda_da_leggere,
            "passo_indietro": lambda: f"{secondi_da_leggere(imp['passo_indietro'])} secondi",
            "passo_avanti": lambda: f"{secondi_da_leggere(imp['passo_avanti'])} secondi",
            "velocita": lambda: valori.scrivi_velocita(imp["velocita"]),
            "tono": lambda: valori.scrivi_tono(imp["tono"]),
            "bande": self._bande_da_leggere,
            "dissolvenza": lambda: valori.scrivi_dissolvenza(imp["dissolvenza"]),
            "insegui": lambda: "sì" if imp["insegui"] else "no",
            "caratteri": self._caratteri_da_leggere,
            "colori_testo": lambda: self._colori_da_leggere("colori_testo"),
            "colori_sfondo": lambda: self._colori_da_leggere("colori_sfondo"),
            "righe_della_console": lambda: str(imp["righe_della_console"]),
            "salva_console": lambda: "scrive la console in un file di testo",
            "marcatori": self._marcatori_da_leggere,
            "importa_marcatori": lambda: "da un file esportato da MeTeOra",
        }[chiave]()
        return f"{VOCI_DELLE_IMPOSTAZIONI[chiave][0]}: {valore}"

    def _bande_da_leggere(self):
        """I guadagni dell'equalizzatore come li scrive il campo, in dB, o
        piatto se sono tutti a zero."""
        bande = self.impostazioni["bande"]
        return f"{valori.scrivi_bande(bande)} dB" if any(bande) else "piatto, tutte le bande a 0 dB"

    def _caratteri_da_leggere(self):
        caratteri = self.impostazioni["caratteri"]
        if not caratteri:
            return "quelle di Windows"
        return ", ".join(f"{nome} {caratteri[area]}" if area in caratteri else f"{nome} di Windows" for area, nome in AREE.items())

    def _colori_da_leggere(self, chiave):
        colori = self.impostazioni[chiave]
        if not colori:
            return "quelli di Windows"
        testo = ", ".join(f"{nome} {'.'.join(str(p) for p in colori[area])}" for area, nome in AREE.items() if area in colori)
        return testo + ("; le altre aree di Windows" if len(colori) < len(AREE) else "")

    def _marcatori_da_leggere(self):
        voci = self.marcatori.voci
        quanti = sum(len(voce["marker"]) for voce in voci.values())
        return f"{quanti} in {len(voci)} file" if quanti else "nessuno"

    def _cambia_impostazione(self, chiave, genitore):
        """Invio su una voce della finestra delle impostazioni, genitore: le
        voci di valore aprono il loro campo, le altre fanno la loro azione."""
        azioni = {
            "scheda_audio": self._scegli_la_scheda_audio,
            "salva_console": lambda _genitore: self._salva_console(),
            "marcatori": self._finestra_dei_marcatori,
            "importa_marcatori": self._importa_i_marcatori,
        }
        if chiave in azioni:
            azioni[chiave](genitore)
        else:
            self._campo_dell_impostazione(chiave, genitore)

    def _campo_dell_impostazione(self, chiave, genitore):
        """Il campo di una voce di valore, come quello dei filtri: in cima le
        righe col dollaro, che spiegano la voce, i limiti e il valore di
        adesso; nell'ultima riga il valore, gia' selezionato. Il testo lo
        legge valori.py: se non va la console dice perche' e il campo si
        riapre, con l'errore in testa al titolo, che NVDA legge, e con il
        testo scritto. Un valore buono si applica e si salva subito."""
        etichetta, participio = VOCI_DELLE_IMPOSTAZIONI[chiave]
        leggi, istruzioni, testo = self._campo(chiave)
        errore = ""
        while True:
            self._suono("domanda")
            with FinestraFiltro(genitore, f"{errore} {etichetta}" if errore else etichetta, testo, istruzioni) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self.scrivi(f"{etichetta} non {participio}.")
                    return
                # Piu' righe valgono come una, unite da spazi.
                testo = " ".join(dialogo.testo.splitlines()).strip()
                try:
                    valore, correzioni = leggi(testo)
                except ErroreValore as e:
                    errore = str(e)
                    self._riscontro("errore", errore)
                    continue
                frase = self._applica_l_impostazione(chiave, valore)
                self._salva_impostazioni()
                # La riga si riscrive prima che il campo se ne vada: tornando
                # sulla lista, NVDA legge gia' il valore nuovo.
                genitore.aggiorna(chiave, self._riga_dell_impostazione(chiave))
            self._riscontro("impostazione_cambiata", " ".join([frase, *correzioni]))
            return

    def _campo(self, chiave):
        """(lettura, istruzioni, testo di adesso) del campo di una voce di
        valore: la lettura e' la funzione di valori.py che legge il testo."""
        imp = self.impostazioni
        if chiave == "volume":
            return valori.leggi_volume_musica, [
                "Il volume della musica, da 0 a 300: oltre il 100 amplifica, per gli audio registrati troppo bassi.",
                "Per esempio 80 o 150. Anche più e meno lo cambiano, dalla finestra principale.",
                f"Adesso è {imp['volume']}.", REGOLA_DEL_DOLLARO], str(imp["volume"])
        if chiave == "passo_volume":
            return valori.leggi_passo_volume, [
                "Di quanto cambiano il volume più e meno: un numero intero da 1 a 50.",
                "Per esempio 5. Anche Maiuscolo+M lo cambia, dalla finestra principale.",
                f"Adesso è {imp['passo_volume']}.", REGOLA_DEL_DOLLARO], str(imp["passo_volume"])
        if chiave == "volume_effetti":
            percentuale = round(imp["volume_effetti"] * 100)
            return valori.leggi_volume_effetti, [
                "Quanto forte suonano gli effetti sonori, in percentuale, da 0 a 100: 0 li zittisce. Il volume della musica non cambia.",
                "Per esempio 50, oppure 35%.",
                f"Adesso è {percentuale}%.", REGOLA_DEL_DOLLARO], str(percentuale)
        if chiave in ("passo_indietro", "passo_avanti"):
            nome, verso, tasto = VOCI_DELLE_IMPOSTAZIONI[chiave][0], *(("indietro", "Q") if chiave == "passo_indietro" else ("avanti", "E"))
            attuale = secondi_da_leggere(imp[chiave])
            return (lambda testo: valori.leggi_secondi(testo, nome)), [
                f"Di quanti secondi salta {verso} il tasto {tasto}: almeno 0.1, anche con i decimali.",
                f"Per esempio 10, 2.5 o 2,5, oppure minuti e secondi come 1:30. Anche Maiuscolo+{tasto} lo cambia, dalla finestra principale.",
                f"Adesso è di {attuale} secondi.", REGOLA_DEL_DOLLARO], attuale
        if chiave == "velocita":
            minima, massima, passo = (valori.scrivi_velocita(v) for v in (valori.VELOCITA_MINIMA, valori.VELOCITA_MASSIMA, valori.PASSO_VELOCITA))
            return valori.leggi_velocita, [
                f"La velocità di riproduzione, da {minima} a {massima}: 1 è la normale, meno di 1 rallenta, più di 1 accelera. Il tono non cambia.",
                f"Va a passi di {passo}: un valore fra due passi va al più vicino. Per esempio 1,05 o 0,9, con la virgola o con il punto.",
                "Anche A e D la cambiano, e S la riporta a 1, dalla finestra principale.",
                f"Adesso è {valori.scrivi_velocita(imp['velocita'])}.", REGOLA_DEL_DOLLARO], valori.scrivi_velocita(imp["velocita"])
        if chiave == "tono":
            return valori.leggi_tono, [
                f"Il tono in semitoni, da -{valori.TONO_MASSIMO} a +{valori.TONO_MASSIMO}: 0 è il normale. La velocità non cambia, e l'equalizzatore segue il tono.",
                "Per esempio +2 per alzarlo di due semitoni, -3 per abbassarlo di tre.",
                "Anche F e H lo cambiano, e G lo riporta a 0, dalla finestra principale.",
                f"Adesso è di {valori.scrivi_tono(imp['tono'])}.", REGOLA_DEL_DOLLARO], valori.scrivi_tono(imp["tono"]).split()[0]
        if chiave == "bande":
            frequenze = ", ".join(str(f) for f in valori.FREQUENZE_DELLE_BANDE[:-1])
            return valori.leggi_bande, [
                f"I guadagni delle {len(valori.FREQUENZE_DELLE_BANDE)} bande dell'equalizzatore, in dB interi da -{valori.GUADAGNO_MASSIMO} a +{valori.GUADAGNO_MASSIMO}, "
                f"separati da spazi, dalla banda più bassa alla più alta: {frequenze} e {valori.FREQUENZE_DELLE_BANDE[-1]} Hz.",
                "Un numero solo vale per tutte le bande, e il campo vuoto le riporta tutte a 0. Per esempio 0 0 +2 0 0 0 -3, oppure 3.",
                "Contro la saturazione il volume scende da solo quanto la banda più alzata: con una banda sola il suono non satura, "
                "con più bande vicine alzate, o tutte, sale fino a circa 5,6 dB oltre, e dal volume 80 o 90 in su conviene abbassare il volume.",
                "Anche U e I scelgono la banda, O e P la alzano e la abbassano, È la azzera e Maiuscolo con È le azzera tutte, dalla finestra principale.",
                f"Adesso: {self._bande_da_leggere()}.", REGOLA_DEL_DOLLARO], valori.scrivi_bande(imp["bande"])
        if chiave == "dissolvenza":
            secondi = imp["dissolvenza"]["secondi"]
            minima, massima = (valori.scrivi_durata(s).split()[0] for s in (valori.DISSOLVENZA_MINIMA, valori.DISSOLVENZA_MASSIMA))
            return (lambda testo: valori.leggi_dissolvenza(testo, secondi)), [
                "La dissolvenza incrociata: il brano che finisce sfuma mentre il seguente entra. Vale a ogni cambio di brano, da solo o con i tasti.",
                f"Scrivi no per spegnerla, sì per accenderla, oppure i secondi, da {minima} a {massima}, anche con i decimali, per accenderla con quella durata. Per esempio 4 o 2,5.",
                "Anche L la accende e la spegne, e Maiuscolo con L ne cambia la durata, dalla finestra principale.",
                f"Adesso è {valori.scrivi_dissolvenza(imp['dissolvenza'])}.", REGOLA_DEL_DOLLARO], valori.scrivi_dissolvenza(imp["dissolvenza"])
        if chiave == "insegui":
            return valori.leggi_si_no, [
                "Con l'inseguimento agganciato, a ogni cambio di brano la selezione della plancia va da sola su ciò che suona, senza spostare il fuoco.",
                "Scrivi sì per agganciarlo, no per sganciarlo; valgono anche s, n, 1, 0, acceso e spento. Anche Maiuscolo+F8 lo aggancia e lo sgancia.",
                f"Adesso è {'agganciato' if imp['insegui'] else 'sganciato'}.", REGOLA_DEL_DOLLARO], "sì" if imp["insegui"] else "no"
        if chiave == "caratteri":
            caratteri = imp["caratteri"]
            di_sistema = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).GetPointSize()
            attuale = " ".join(str(caratteri.get(area, di_sistema)) for area in AREE) if caratteri else ""
            return valori.leggi_caratteri, [
                f"La dimensione dei caratteri in punti, da {valori.CARATTERI_MINIMI} a {valori.CARATTERI_MASSIMI}: tre numeri separati da spazi, per plancia, console e cruscotto.",
                f"Un numero solo vale per tutte e tre le aree. Per esempio 12, oppure 12 14 12. Il carattere di Windows è di {di_sistema} punti.",
                "Il campo vuoto torna al carattere di Windows in tutte e tre le aree.",
                f"Adesso: {self._caratteri_da_leggere()}.", REGOLA_DEL_DOLLARO], attuale
        if chiave in ("colori_testo", "colori_sfondo"):
            nome = VOCI_DELLE_IMPOSTAZIONI[chiave][0]
            cosa, esempi = ("dei caratteri", "p31.31.31 è un grigio scuro, c100.100.100 il bianco") if chiave == "colori_testo" else (
                "dello sfondo", "t0.0.0 è il nero, c100.100.80 un giallo chiaro")
            return (lambda testo: valori.leggi_colori(testo, nome)), [
                f"Il colore {cosa} di ogni area: la lettera dell'area, p plancia, c console, t cruscotto, e tre percentuali da 0 a 100 di rosso, verde e blu, separate dal punto.",
                f"Più aree si separano con lo spazio. Per esempio {esempi}.",
                "La lettera da sola torna ai colori di Windows; le aree che non scrivi restano come sono.",
                f"Adesso: {self._colori_da_leggere(chiave)}.", REGOLA_DEL_DOLLARO], valori.scrivi_colori(imp[chiave])
        return valori.leggi_righe_della_console, [
            f"Quante righe tiene la console: da {valori.RIGHE_MINIME} in su. Le più vecchie si tolgono dalla cima.",
            "Per esempio 2000, il valore di partenza. Un testo lungo, come il manuale, resta comunque intero.",
            f"Adesso ne tiene {imp['righe_della_console']}.", REGOLA_DEL_DOLLARO], str(imp["righe_della_console"])

    def _applica_l_impostazione(self, chiave, valore):
        """Applica il valore letto dal campo e restituisce la frase che lo dice."""
        imp = self.impostazioni
        if chiave in ("colori_testo", "colori_sfondo"):
            # Dal campo dei colori arrivano i cambi, da unire a quelli di adesso.
            valore = valori.unisci_colori(imp[chiave], valore)
        imp[chiave] = valore
        if chiave == "volume":
            self.motore.volume = valore
            return f"Il volume della musica ora è {valore}{', amplificato oltre il 100' if valore > 100 else ''}."
        if chiave == "passo_volume":
            return f"Più e meno ora cambiano il volume di {valore}."
        if chiave == "volume_effetti":
            return f"Gli effetti sonori ora suonano al {round(valore * 100)}%." if valore else "Gli effetti sonori ora tacciono."
        if chiave in ("passo_indietro", "passo_avanti"):
            return f"Il salto {'indietro' if chiave == 'passo_indietro' else 'avanti'} ora è di {secondi_da_leggere(valore)} secondi."
        if chiave == "velocita":
            self.motore.velocita = valore
            return f"La velocità ora è {valori.scrivi_velocita(valore)}{', la normale' if valore == 1 else ''}."
        if chiave == "tono":
            self.motore.tono = valore
            return f"Il tono ora è di {valori.scrivi_tono(valore)}{', il normale' if valore == 0 else ''}."
        if chiave == "bande":
            self.motore.bande = valore
            return f"L'equalizzatore ora è {self._bande_da_leggere()}."
        if chiave == "dissolvenza":
            self._applica_la_dissolvenza()
            return f"La dissolvenza ora è {valori.scrivi_dissolvenza(valore)}."
        if chiave == "insegui":
            if not valore:
                return "Inseguimento sganciato: la selezione resta dove la lasci."
            if self.motore.in_corso:
                self._insegui()
            return "Inseguimento agganciato: la selezione della plancia segue il brano che suona."
        if chiave == "righe_della_console":
            # Il taglio e' subito, senza il margine che scrivi lascia.
            posizione = self.console.GetInsertionPoint()
            self.console.SetInsertionPoint(max(0, posizione - self._taglia_la_console(valore)))
            return f"La console ora tiene {valore} righe."
        self._applica_aspetto()
        if chiave == "caratteri":
            return f"Dimensioni dei caratteri: {self._caratteri_da_leggere()}."
        return f"{VOCI_DELLE_IMPOSTAZIONI[chiave][0]}: {self._colori_da_leggere(chiave)}."

    # La scheda audio, piano 5.8.9.

    def _applica_la_scheda(self, scelta, avvio=False):
        """schede_audio.applica, senza mai fermare il programma: PortAudio e
        mpv sollevano eccezioni loro, e una scheda che non va non deve
        impedire l'avvio ne' chiudere la finestra. Restituisce (esito,
        None), o (None, l'eccezione)."""
        try:
            return schede_audio.applica(scelta, self.motore, avvio=avvio), None
        except Exception as e:  # noqa: BLE001 - la scheda audio fallisce in molti modi, e lo dice la console
            return None, e

    def _applica_la_scheda_all_avvio(self):
        """La scheda scelta, appena c'e' il motore. Con la scelta automatica
        non si tocca e non si prova niente: il mixer sceglie da se' alla
        prima apertura. Una scheda scelta che c'e' si prova come quando la si
        sceglie, con _effetti_si_aprono: se gli effetti non la aprono, per
        esempio perche' un altro programma la tiene tutta per se', si usa
        l'automatica, e la scelta salvata resta, per quando la scheda torna
        libera. Restituisce (esito, errore) come _applica_la_scheda, e
        _scheda_in_disparte dice se la scheda scelta manca o non si apre; la
        console, che ancora non c'e', lo dira' con
        _scrivi_la_scheda_all_avvio."""
        scelta = self.impostazioni["scheda_audio"]
        esito, errore = self._applica_la_scheda(scelta, avvio=True)
        # Perche' la scheda scelta non e' quella in uso, o None.
        self._scheda_in_disparte = None
        if errore is not None:
            return esito, errore
        if esito["mancante"]:
            self._scheda_in_disparte = SCHEDA_MANCANTE
        elif scelta and not self._effetti_si_aprono():
            self._scheda_in_disparte = SCHEDA_CHE_NON_SI_APRE
            esito, errore = self._applica_la_scheda({})
        return esito, errore

    def _effetti_si_aprono(self):
        """Vero se il mixer degli effetti apre la sua scheda. La prova manda
        un attimo di silenzio con Acusticator.riproduci, che apre la scheda
        prima di tornare e dice se c'e' riuscito: cosi' non dipende dal
        volume degli effetti, che a zero non fa partire nessun suono, e non
        si fida di Acusticator.play, che dice di aver suonato anche quando
        la scheda non si apre."""
        import numpy
        from GBUtils import Acusticator

        try:
            return bool(Acusticator.riproduci(numpy.zeros((SILENZIO_DI_PROVA, 2), dtype=numpy.float32)))
        except Exception:  # noqa: BLE001 - la scheda audio fallisce in molti modi: per la prova vuol dire che non si apre
            return False

    @staticmethod
    def _nome_della_scheda(dispositivo, interfaccia):
        """Il nome di una scheda da leggere, come "Altoparlanti (Realtek(R)
        Audio), WASAPI": l'interfaccia ha il nome breve, senza Windows davanti."""
        return f"{dispositivo}, {(interfaccia or '').removeprefix('Windows ')}"

    def _scheda_dell_esito(self, esito):
        """La scheda su cui suonano gli effetti dopo applica, da leggere."""
        nome = self._nome_della_scheda(esito["dispositivo"], esito["interfaccia"]) if esito["dispositivo"] else ""
        if not esito["automatica"]:
            return nome
        return f"Automatica ({nome})" if nome else "Automatica"

    def _scheda_da_leggere(self):
        scelta = self.impostazioni["scheda_audio"]
        if scelta:
            nome = self._nome_della_scheda(scelta["dispositivo"], scelta["interfaccia"])
            return f"{nome}, {self._scheda_in_disparte}: uso quella automatica" if self._scheda_in_disparte else nome
        # Con la scelta automatica, la scheda che il mixer usa gia', senza
        # aprire niente per provarla.
        uscita = None
        with contextlib.suppress(Exception):
            uscita = schede_audio.in_uso()
        return f"Automatica ({self._nome_della_scheda(uscita['dispositivo'], uscita['interfaccia'])})" if uscita else "Automatica"

    def _scrivi_la_scheda_all_avvio(self, esito, errore):
        scelta = self.impostazioni["scheda_audio"]
        if self._scheda_in_disparte == SCHEDA_CHE_NON_SI_APRE:
            # Con il suono dell'errore: senza, gli effetti tacerebbero per
            # tutta la sessione senza dire perche'.
            if errore is not None:
                self._riscontro("errore", f"La scheda audio scelta, {scelta['dispositivo']}, non si apre, e non riesco a usare quella automatica: {errore}.")
            else:
                self._riscontro("errore", f"La scheda audio scelta, {scelta['dispositivo']}, non si apre: uso quella automatica.")
        elif errore is not None:
            self.scrivi(f"Non riesco a usare la scheda audio scelta, {scelta.get('dispositivo', 'automatica')}: {errore}.")
        elif esito["mancante"]:
            dove = f", {self._nome_della_scheda(esito['dispositivo'], esito['interfaccia'])}" if esito["dispositivo"] else ""
            self.scrivi(f"La scheda audio scelta, {scelta['dispositivo']}, non c'è: uso quella automatica{dove}.")
        elif not esito["musica"]:
            self.scrivi(f"La musica non ritrova la scheda audio {esito['dispositivo']} e suona sulla scheda di Windows.")

    def _scegli_la_scheda_audio(self, genitore):
        """La scelta della scheda audio, una per musica ed effetti: in cima la
        scelta automatica, poi le uscite in ordine di latenza."""
        scelta = self.impostazioni["scheda_audio"]
        try:
            elenco = schede_audio.uscite()
            # La scelta automatica: con l'automatica in uso e' la scheda del
            # mixer, senza aprire niente; altrimenti la si rifa' per provarla.
            automatica = (None if scelta else schede_audio.in_uso(elenco)) or schede_audio.automatica()
        except Exception as e:  # noqa: BLE001 - PortAudio fallisce in molti modi, e lo dice la console
            self._riscontro("errore", f"Non riesco a leggere le schede audio: {e}.")
            return
        righe = [f"Automatica: {schede_audio.etichetta(automatica)}" if automatica else "Automatica", *(schede_audio.etichetta(u) for u in elenco)]
        attuale = schede_audio.ritrova(scelta, elenco)
        self._suono("domanda")
        with FinestraScelta(genitore, "Scheda audio", righe, elenco.index(attuale) + 1 if attuale is not None else 0) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self.scrivi("Scheda audio non cambiata.")
                return
            indice = dialogo.GetSelection()
        self._usa_la_scheda(schede_audio.da_salvare(elenco[indice - 1]) if indice > 0 else {}, genitore)

    def _usa_la_scheda(self, nuova, genitore):
        """Applica la scheda scelta e la salva; il suono della scheda arriva
        gia' da quella nuova. Se gli effetti non riescono ad aprirla si torna
        all'automatica, e la console lo dice. La prova d'apertura vale anche
        con il volume degli effetti a zero."""
        esito, errore = self._applica_la_scheda(nuova)
        aperta = errore is None and self._effetti_si_aprono()
        evento = None
        if aperta:
            self._suono("scheda_audio")
            testo = f"Scheda audio: {self._scheda_dell_esito(esito)}."
            if not esito["musica"]:
                testo += " La musica non la ritrova, e suona sulla scheda di Windows."
        else:
            perche = f": {errore}" if errore is not None else ""
            nome = self._nome_della_scheda(nuova["dispositivo"], nuova["interfaccia"]) if nuova else "automatica"
            evento = "errore"
            if nuova:
                nuova = {}
                esito, errore = self._applica_la_scheda(nuova)
                if errore is not None:
                    torno = f", ma neanche lei va: {errore}"
                else:
                    torno = f", {self._nome_della_scheda(esito['dispositivo'], esito['interfaccia'])}" if esito["dispositivo"] else ""
                testo = f"La scheda audio {nome} non si apre{perche}. Torno alla scelta automatica{torno}."
            else:
                testo = f"La scheda audio automatica non si apre{perche}."
        self.impostazioni["scheda_audio"] = nuova
        self._scheda_in_disparte = None
        self._salva_impostazioni()
        genitore.aggiorna("scheda_audio", self._riga_dell_impostazione("scheda_audio"))
        if evento:
            self._riscontro(evento, testo)
        else:
            self.scrivi(testo)

    # Salva console, piano 5.8.6.

    def _salva_console(self):
        """Scrive la console in un file di testo nella cartella dei dati,
        che nel programma compilato e' quella dell'eseguibile, con un nome
        che porta versione, data e ora, cosi' i file si ordinano da soli. Due
        nello stesso minuto: il secondo ha -2 in fondo, il terzo -3."""
        cartella = os.path.dirname(self.impostazioni.percorso)
        base = f"MeTeOra-V{version.VERSION.replace('.', '_')}-{datetime.datetime.now():%Y_%m_%d-%H_%M}"
        nome, numero = f"{base}.txt", 1
        while os.path.exists(os.path.join(cartella, nome)):
            numero += 1
            nome = f"{base}-{numero}.txt"
        try:
            with open(os.path.join(cartella, nome), "x", encoding="utf-8") as f:
                f.write("\n".join(self._righe))
        except OSError as e:
            self._riscontro("errore", f"Non riesco a salvare la console: {e.strerror or e}.")
            return
        quante = len(self._righe)
        self._riscontro("console_salvata", f"Console salvata in {nome}, nella cartella del programma: {'1 riga' if quante == 1 else f'{quante} righe'}.")

    # La finestra dei marcatori e l'importazione, piano 5.8.5 e 5.8.7.

    def _finestra_dei_marcatori(self, genitore):
        self._suono("marcatori")
        azioni = {"rinomina": self._rinomina_il_marker, "elimina": self._elimina_i_marcatori, "cancella_tutto": self._cancella_tutti_i_marcatori,
            "esporta": self._esporta_i_marcatori, "suono": self._suono, "riscontro": self._riscontro}
        with FinestraMarcatori(genitore, self.marcatori, azioni) as dialogo:
            dialogo.ShowModal()
        genitore.aggiorna("marcatori", self._riga_dell_impostazione("marcatori"))

    def _elimina_i_marcatori(self, scelti, genitore):
        """Canc nella finestra dei marcatori: uno solo si elimina subito, come
        nella plancia; piu' d'uno dopo una conferma."""
        # Lo stesso marker scelto due volte conta una volta.
        unici = list({(k, m["tempo"], m["nome"]): (k, m) for k, m in scelti}.values())
        if len(unici) == 1:
            self._elimina_il_marker(*unici[0])
            return
        if not self._conferma(f"Eliminare {len(unici)} marker?", "Elimina marcatori", genitore):
            self.scrivi("Eliminazione annullata.")
            return
        tolti = sum(self.marcatori.togli(k, m) for k, m in unici)
        self._salva_i_marker(*dict.fromkeys(k for k, _m in unici))
        self._riscontro("marker_eliminato", f"Eliminati {tolti} marker.")

    def _cancella_tutti_i_marcatori(self, genitore):
        """Cancella tutto nella finestra dei marcatori, dopo una conferma con
        No come risposta predefinita."""
        voci = self.marcatori.voci
        quanti, file = sum(len(voce["marker"]) for voce in voci.values()), len(voci)
        if not quanti:
            self._riscontro("non_disponibile", "Non ci sono marcatori da cancellare.")
            return
        if not self._conferma(f"Cancellare tutti i marcatori, {quanti} marker in {file} file? Non si possono recuperare.", "Cancella tutto", genitore):
            self.scrivi("I marcatori restano dove sono.")
            return
        # Le chiavi da rinfrescare nella plancia si prendono prima di cancellare.
        chiavi = list(voci)
        tolti = self.marcatori.cancella_tutto()
        self._salva_i_marker(*chiavi)
        self._riscontro("marcatori_cancellati", f"Cancellati tutti i marcatori: {tolti} marker in {file} file.")

    def _esporta_i_marcatori(self, scelti, genitore):
        """Esporta selezionati: i marker scelti in un file JSON senza
        percorsi, che un'altra copia di MeTeOra puo' importare."""
        dati, saltati = self.marcatori.esporta(scelti)
        esportati = sum(len(voce["marker"]) for voce in dati["marcatori"])
        if not esportati:
            self._riscontro("non_disponibile", "I marker scelti non si esportano: MeTeOra non conosce una durata valida dei loro file, e senza la durata un altro computer non li ritroverebbe.")
            return
        with DialogoDiFile(genitore, "Esporta marcatori", defaultDir=os.path.dirname(self.impostazioni.percorso), defaultFile=FILE_DELL_ESPORTAZIONE,
                wildcard=FILTRO_DEI_MARCATORI, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self.scrivi("Esportazione annullata.")
                return
            percorso = dialogo.GetPath()
        if not os.path.splitext(percorso)[1]:
            percorso += ".json"
        try:
            Marcatori.scrivi_esportazione(dati, percorso)
        except OSError as e:
            self._riscontro("errore", f"Non riesco a esportare i marcatori: {e.strerror or e}.")
            return
        file = len(dati["marcatori"])
        testo = f"{'Esportato' if esportati == 1 else 'Esportati'} {esportati} marker di {file} file in {os.path.basename(percorso)}."
        if saltati:
            testo += f" {saltati} non {'esportato' if saltati == 1 else 'esportati'}: MeTeOra non conosce una durata valida dei loro file."
        self._riscontro("marcatori_esportati", testo)

    def _importa_i_marcatori(self, genitore):
        """Importa marcatori: i marker di un file esportato vanno sui file con
        lo stesso nome e la stessa durata, copie comprese; quelli che ci
        sono gia' restano come sono."""
        with DialogoDiFile(genitore, "Importa marcatori", defaultDir=os.path.dirname(self.impostazioni.percorso), wildcard=FILTRO_DEI_MARCATORI,
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self.scrivi("Importazione annullata.")
                return
            percorso = dialogo.GetPath()
        try:
            voci = Marcatori.leggi_esportazione(percorso)
        except ValueError as e:
            self._riscontro("errore", str(e))
            return
        aggiunti, gia_presenti, chiavi = self.marcatori.importa(voci)
        if chiavi:
            self._salva_i_marker(*chiavi)
        presenti = {0: "nessuno c'era già", 1: "1 c'era già"}.get(gia_presenti, f"{gia_presenti} c'erano già")
        self._riscontro("marcatori_importati", f"{'Importato 1 marcatore' if aggiunti == 1 else f'Importati {aggiunti} marcatori'}, {presenti}.")
        genitore.aggiorna("marcatori", self._riga_dell_impostazione("marcatori"))

    # I marker, issue 12.

    # Mentre il brano suona, R considera gia' passato un marker superato da
    # meno di questo: appena saltati su un marker si e' gia' oltre, e R deve
    # andare a quello prima.
    MARGINE_DI_R = 1.5

    def _durata_dei_marker(self, percorso, sottobrano=None, leggi=False):
        """(durata, sottobrano) con cui un file si riconosce per i suoi marker:
        per un SID la durata del sottobrano dal database della collezione,
        per gli altri quella dello schedario. Una durata che non si conosce
        e' None, e allora vale il percorso: per un SID fuori dal database la
        durata predefinita di tre minuti non e' una durata vera. Con leggi,
        se lo schedario non ha ancora letto il file, lo legge subito."""
        if formati.e_sid(percorso):
            info = songlengths.info_del_sid(percorso)
            numero = sottobrano or (info or {}).get("iniziale") or 1
            durate = songlengths.durate_del_file(percorso)
            return (durate[numero - 1] if durate and numero <= len(durate) else None), numero
        scheda = self.schedario.scheda(percorso)
        if scheda is None and leggi:
            scheda = self.schedario.leggi_subito(percorso)
        return (scheda or {}).get("durata"), None

    def _chiave_dei_marker(self, percorso, sottobrano=None, leggi=False):
        durata, numero = self._durata_dei_marker(percorso, sottobrano, leggi)
        return marcatori.chiave(percorso, durata, numero)

    def _chiave_della_voce(self, dati):
        """La chiave dei marker di una voce della plancia, o None: un SID con
        piu' sottobrani ha i marker sui sottobrani, non sul file."""
        tipo = dati.get("tipo")
        if tipo == "marker":
            return dati["chiave"]
        if tipo == "sottobrano":
            return self._chiave_dei_marker(dati["brano"].percorso, dati["numero"])
        if tipo in ("brano", "file") and not self._ha_sottobrani(dati["brano"]):
            return self._chiave_dei_marker(dati["brano"].percorso, dati["brano"].sottobrano)
        return None

    def _marker_della_voce(self, dati):
        """I marker di un brano, di un file o di un sottobrano della plancia.
        Prima un controllo sul solo nome del file, che costa poco."""
        if dati.get("tipo") not in ("brano", "file", "sottobrano") or not self.marcatori.forse(dati["brano"].percorso):
            return []
        k = self._chiave_della_voce(dati)
        return self.marcatori.elenco(k) if k else []

    def _contesto_dei_marker(self, senza_brano):
        """(chiave, percorso, durata, sottobrano) di cio' che suona, o None
        con il riscontro senza_brano se non suona niente."""
        percorso = self.motore.in_corso
        if not percorso:
            self._riscontro("niente_da_suonare", f"Non sta suonando niente: {senza_brano}")
            return None
        sottobrano = self.motore.sottobrano if self.motore.sottobrani else None
        durata, numero = self._durata_dei_marker(percorso, sottobrano, leggi=True)
        return marcatori.chiave(percorso, durata, numero), percorso, durata, numero

    def _salva_i_marker(self, *chiavi):
        """Salva i marker, una volta sola, e rinfresca nella plancia le voci
        delle chiavi; se il salvataggio non riesce lo dice, e ci si riprova
        al prossimo cambiamento o all'uscita."""
        try:
            self.marcatori.salva()
        except OSError as e:
            self._riscontro("errore", f"Non riesco a salvare i marker, riprovo all'uscita: {e}")
        for k in chiavi:
            self._rinfresca_i_marker(k)

    def _comando_marker(self):
        """T: un marker nuovo dove si e'; se li' c'e' gia' un marker, lo rinomina."""
        contesto = self._contesto_dei_marker("i marker si mettono nel brano che suona.")
        if contesto is None:
            return
        k, percorso, durata, numero = contesto
        posizione = self.motore.posizione or 0.0
        esistente = self.marcatori.trova(k, posizione)
        if esistente is not None:
            self._rinomina_il_marker(k, esistente)
            return
        marker = self.marcatori.aggiungi(k, posizione, percorso, durata, numero)
        self._salva_i_marker(k)
        self._riscontro("marker_messo", f"Marker {marker['nome']} a {durata_lunga(marker['tempo'])}.")

    def _salta_al_marker(self, verso):
        contesto = self._contesto_dei_marker("R e Y saltano fra i marker del brano che suona.")
        if contesto is None:
            return
        k = contesto[0]
        if not self.marcatori.elenco(k):
            self._riscontro("non_disponibile", "Questo brano non ha marker: T ne mette uno dove sei.")
            return
        posizione = self.motore.posizione or 0.0
        if verso > 0:
            marker = self.marcatori.successivo(k, posizione)
        else:
            margine = marcatori.TOLLERANZA if self.motore.in_pausa else self.MARGINE_DI_R
            marker = self.marcatori.precedente(k, posizione, margine)
        if marker is None:
            sopra = self.marcatori.trova(k, posizione) is not None
            if verso > 0:
                testo = "È l'ultimo marker." if sopra else "Dopo di qui non ci sono marker."
            else:
                testo = "È il primo marker." if sopra else "Prima di qui non ci sono marker."
            self._riscontro("nessun_altro_brano", testo)
            return
        self._vai_nel_brano(marker["tempo"])
        self._riscontro("marker_avanti" if verso > 0 else "marker_indietro", f"{marker['nome']}, {durata_lunga(marker['tempo'])}.")
        self._fuoco_sul_marker(k, marker)

    def _vai_nel_brano(self, secondi):
        """Un salto a un marker del brano in corso: con la dissolvenza accesa e
        il brano che suona, il punto di partenza e il marker si incrociano
        sui due lettori (Gabriele, 2 ottobre 2026); altrimenti un salto netto."""
        if self.impostazioni["dissolvenza"]["accesa"] and self.motore.in_corso and not self.motore.in_pausa:
            sottobrano = self.motore.sottobrano if self.motore.sottobrani else None
            self.motore.suona(self.motore.in_corso, sottobrano, inizio=secondi, sfuma_lo_stesso=True)
        else:
            self.motore.vai_a(secondi)

    def _comando_marker_precedente(self):
        self._salta_al_marker(-1)

    def _comando_marker_successivo(self):
        self._salta_al_marker(1)

    def _marker_numero(self, numero):
        """Maiuscolo con le cifre da 1 a 0: il marker numero, nell'ordine del
        tempo, del brano su cui sta il fuoco della plancia, o del brano di cui
        e' il marker o il sottobrano. Lo suona da li', come Vai al marker. Il
        fuoco della plancia resta dov'e': X sul brano continua a farlo
        ripartire da capo (Gabriele, collaudo della 1.41.0)."""
        voce = self._voce_di_lavoro()
        dati = self._dati(voce) or {}
        tipo = dati.get("tipo")
        if tipo not in ("brano", "file", "sottobrano", "marker"):
            self._riscontro("non_disponibile", "Maiuscolo con le cifre va ai marker del brano su cui sta la plancia: porta il fuoco su un brano.")
            return
        brano = dati["brano"]
        multiplo = self._ha_sottobrani(brano)
        if tipo in ("sottobrano", "marker"):
            sottobrano = dati.get("numero")
        elif multiplo:
            # Di un SID con piu' sottobrani conta quello che suona, se suona
            # lui, altrimenti l'iniziale.
            info = songlengths.info_del_sid(brano.percorso) or {}
            sottobrano = self.motore.sottobrano if self.motore.in_corso == brano.percorso else (info.get("iniziale") or 1)
        else:
            sottobrano = brano.sottobrano
        k = dati["chiave"] if tipo == "marker" else self._chiave_dei_marker(brano.percorso, sottobrano, leggi=True)
        elenco = self.marcatori.elenco(k)
        if numero > len(elenco):
            chi = f"il sottobrano {sottobrano} di {brano.nome_del_file}" if multiplo and sottobrano else brano.nome_del_file
            testo = f"{chi[:1].upper()}{chi[1:]} non ha marker." if not elenco else f"Non c'è il marker {numero}: {chi} ne ha {len(elenco)}."
            self._riscontro("nessun_altro_brano", testo)
            return
        self._vai_al_marker({"playlist": dati["playlist"], "brano": brano, "numero": sottobrano, "marker": elenco[numero - 1]})

    def _togli_i_marker(self, quali):
        contesto = self._contesto_dei_marker("Maiuscolo con R, Y e T tolgono i marker del brano che suona; quelli di un altro brano si tolgono con Canc sulla loro voce nella plancia.")
        if contesto is None:
            return
        k = contesto[0]
        posizione = self.motore.posizione or 0.0
        if quali == "prima":
            tolti, evento, dove = self.marcatori.togli_prima(k, posizione), "marker_tolti_prima", f"prima di {durata_lunga(posizione)}"
        elif quali == "dopo":
            tolti, evento, dove = self.marcatori.togli_dopo(k, posizione), "marker_tolti_dopo", f"dopo {durata_lunga(posizione)}"
        else:
            tolti, evento, dove = self.marcatori.togli_tutti(k), "marker_tolti_tutti", "in tutto il brano"
        if not tolti:
            self._riscontro("non_disponibile", f"Non ci sono marker da togliere {dove}.")
            return
        self._salva_i_marker(k)
        self._riscontro(evento, f"{'Tolto' if tolti == 1 else 'Tolti'} {tolti} marker {dove}.")

    def _comando_togli_i_marker_prima(self):
        self._togli_i_marker("prima")

    def _comando_togli_i_marker_dopo(self):
        self._togli_i_marker("dopo")

    def _comando_togli_i_marker(self):
        self._togli_i_marker("tutti")

    def _rinomina_il_marker(self, k, marker, genitore=None):
        with DialogoTesto(genitore or self, f"Nome del marker a {durata_lunga(marker['tempo'])}:", "Rinomina il marker", marker["nome"]) as dialogo:
            self._suono("domanda")
            if dialogo.ShowModal() != wx.ID_OK:
                self.scrivi("Nome del marker non cambiato.")
                return
            nome = " ".join(dialogo.GetValue().split())
        if not nome or nome == marker["nome"]:
            self.scrivi("Nome del marker non cambiato.")
            return
        vecchio = marker["nome"]
        self.marcatori.rinomina(k, marker, nome)
        self._salva_i_marker(k)
        self._riscontro("marker_rinominato", f"Il marker {vecchio}, a {durata_lunga(marker['tempo'])}, ora si chiama {nome}.")

    def _elimina_il_marker(self, k, marker, voce=None):
        """Canc su un marker della plancia, la sua voce: lo toglie. Se il
        fuoco stava proprio su di lui, passa al marker vicino, o al brano se
        era l'ultimo; altrimenti resta dov'e'."""
        if voce is not None and voce == self._voce_corrente():
            vicina = self.albero.GetNextSibling(voce)
            if not vicina.IsOk():
                vicina = self.albero.GetPrevSibling(voce)
            self._seleziona(vicina if vicina.IsOk() else self.albero.GetItemParent(voce))
        self.marcatori.togli(k, marker)
        self._salva_i_marker(k)
        self._riscontro("marker_eliminato", f"Eliminato il marker {marker['nome']}, a {durata_lunga(marker['tempo'])}.")

    def _vai_al_marker(self, dati):
        """Vai al marker, e Maiuscolo con le cifre: suona il brano dal marker, rispettando il loop
        A-B. Se il brano e' quello caricato ci salta, e riparte se era in
        pausa; il suono dice se il salto va avanti o indietro. Vero se ha
        suonato."""
        brano, numero, marker = dati["brano"], dati.get("numero"), dati["marker"]
        stesso = self.motore.in_corso == brano.percorso and (numero is None or self.motore.sottobrano == numero)
        if stesso:
            avanti = marker["tempo"] >= (self.motore.posizione or 0.0)
            if self.motore.in_pausa:
                self.motore.vai_a(marker["tempo"])
                self.motore.pausa(False, sfumando=True)
            else:
                self._vai_nel_brano(marker["tempo"])
            self._riscontro("marker_avanti" if avanti else "marker_indietro", f"{marker['nome']}, {durata_lunga(marker['tempo'])}.")
            return True
        if not self.coda.nel_loop(dati["playlist"], brano):
            self._riscontro("fuori_dal_loop", f"{brano.nome_del_file} è fuori dal loop: si suona solo fra il punto A e il punto B.")
            return False
        self._suona(dati["playlist"], brano, sottobrano=numero, inizio=marker["tempo"])
        self.scrivi(f"Dal marker {marker['nome']}, {durata_lunga(marker['tempo'])}.")
        return True

    def _rinfresca_i_marker(self, k):
        """Dopo un cambio ai marker di una chiave, rinfresca nella plancia
        tutte le voci di quel file, in ogni playlist e cartella: etichetta,
        ramo e marker che mostra. Il fuoco su un marker rinato si ritrova
        dal suo tempo. Prima si raccolgono le voci, poi si rifanno: rifacendo
        una voce i suoi marker spariscono, e non vanno piu' toccati."""
        corrente = self._voce_corrente()
        dati_correnti = self._dati(corrente) or {}
        tempo_corrente = dati_correnti["marker"]["tempo"] if dati_correnti.get("tipo") == "marker" else None
        genitore_del_fuoco = self.albero.GetItemParent(corrente) if tempo_corrente is not None else None
        # Prima il nome del file, che costa poco; la chiave solo per quelli.
        nome = os.path.basename(k.split("|")[1]).casefold() if k.startswith("percorso|") else k.split("|")[0]
        da_rifare = []
        for voce in self._tutte_le_voci():
            dati = self._dati(voce) or {}
            if dati.get("tipo") in ("brano", "file", "sottobrano") and os.path.basename(dati["brano"].percorso).casefold() == nome \
                    and self._chiave_della_voce(dati) == k:
                da_rifare.append((voce, dati))
        ha_marker = bool(self.marcatori.elenco(k))
        for voce, dati in da_rifare:
            self.albero.SetItemText(voce, self._etichetta(dati))
            fuoco_dentro = genitore_del_fuoco is not None and genitore_del_fuoco == voce
            if fuoco_dentro:
                # Il marker col fuoco sta per rinascere: il fuoco passa un
                # attimo sul brano, e poi ritrova il marker dal suo tempo.
                self._seleziona(voce)
            aperta = self.albero.IsExpanded(voce)
            self.albero.DeleteChildren(voce)
            dati["caricato"] = False
            self.albero.SetItemHasChildren(voce, ha_marker)
            if not (aperta and ha_marker):
                continue
            self._carica(voce, dati)
            self.albero.Expand(voce)
            if fuoco_dentro:
                figlio = next((v for v in self._figli(voce) if abs((self._dati(v) or {})["marker"]["tempo"] - tempo_corrente) < 1e-6), None)
                if figlio is not None:
                    self._seleziona(figlio)

    def _fuoco_sul_marker_della_voce(self, voce, marker):
        """Apre la voce, un brano, un file o un sottobrano, e porta il fuoco
        della plancia sul suo marker."""
        dati = self._dati(voce) or {}
        if not self.albero.ItemHasChildren(voce):
            # La voce e' nata prima che si sapesse dei suoi marker.
            dati["caricato"] = False
            self.albero.SetItemHasChildren(voce, True)
        self.albero.Expand(voce)
        figlio = next((v for v in self._figli(voce) if (self._dati(v) or {}).get("marker", {}).get("tempo") == marker["tempo"]), None)
        if figlio is not None:
            self.albero.EnsureVisible(figlio)
            self._seleziona(figlio)

    def _fuoco_sul_marker(self, k, marker):
        """R e Y: il fuoco della plancia va sul marker raggiunto, aprendo i
        rami che servono, se cio' che suona sta nella plancia."""
        voce = self._trova_voce_che_suona()
        if voce is None:
            return
        dati = self._dati(voce) or {}
        if dati.get("tipo") in ("brano", "file") and self._ha_sottobrani(dati["brano"]):
            # Di un SID con piu' sottobrani i marker stanno sul sottobrano.
            self.albero.Expand(voce)
            voce = next((v for v in self._figli(voce) if (self._dati(v) or {}).get("numero") == self.motore.sottobrano), None)
            if voce is None:
                return
            dati = self._dati(voce)
        if self._chiave_della_voce(dati) != k:
            return
        self._fuoco_sul_marker_della_voce(voce, marker)

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
            voce = next((v for v in self._figli(voce) if self._dati(v).get("tipo") == "sottobrano" and self._dati(v).get("numero") == self.motore.sottobrano), voce)
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

    def _apri_ramo(self, voce, con_i_marker=True):
        """Apre la voce e tutti i rami che ha dentro, caricandoli, fino a
        MASSIMO_DI_RAMI. Torna (rami aperti, vero se si e' fermato prima).
        Senza con_i_marker restano chiusi i brani che dentro hanno solo
        marker: J e K aprono la playlist per suonarla, non per leggerli."""
        aperti = 0
        da_aprire = [voce]
        with wx.BusyCursor():
            while da_aprire and aperti < MASSIMO_DI_RAMI:
                ramo = da_aprire.pop(0)
                if not self.albero.ItemHasChildren(ramo):
                    continue
                dati = self._dati(ramo) or {}
                if not con_i_marker and dati.get("tipo") in ("brano", "file", "sottobrano") and not (
                        dati["tipo"] != "sottobrano" and self._ha_sottobrani(dati["brano"])):
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
        if self.marcatori.modificato:
            with contextlib.suppress(OSError):
                self.marcatori.salva()
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
