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
# nella 1.55.0 velocita', tono, equalizzatore e dissolvenza incrociata, con i tasti, le voci delle impostazioni e il passaggio fra due brani (tappa 4, issue 15). Nella 1.58.0 la dissolvenza anche su stop, pausa, X da capo e marker, i suoni al volo dell'equalizzatore e il loop a giro su Maiuscolo+X; nella 1.58.1 F e H scambiati. Nella 1.59.0 la riproduzione casuale con Maiuscolo+N (issue 17). Nella 1.60.0 W anche dalla fine, con il meno. Nella 1.60.1 O abbassa e P alza. Nella 1.61.0 i modelli della riproduzione casuale, con il mazzo. Nella 1.62.0 l'attesa del SID dopo un salto. Nella 1.63.0 il video: Maiuscolo con F1, F2, F3, F5 e F6, la finestra del video e i sottotitoli letti (tappa 7). Nella 1.64.0 il ramo Questa rete. Nella 1.65.0 i MIDI con FluidSynth e il banco dei suoni (tappa 8). Nella 1.66.0 la musica delle console, con i sottobrani come i SID. Nella 1.66.36 le rifiniture della tappa 9: riscontro per ogni tasto e annullamento, domande con Esc, fuoco che non si sposta da solo. Nella 1.67.0 Rinomina file; nella 1.67.4 solo i banchi General MIDI. Nella 1.69.0 i tag: F11, Maiuscolo+F11 e il sottomenu Tag. Nella 1.71.0 la barra rovesciata cerca nel ramo, Ctrl con la barra rovesciata ovunque. Nella 1.72.0 F1 apre manuale.html nel browser e F12 scrive la sua guida rapida. Nella 1.73.0 Ctrl con la barra rovesciata cerca anche in rete, dopo i dischi. Nella 1.74.0, con la riproduzione casuale, B sceglie a caso e Z torna ai brani suonati prima. Nella 1.75.0 l'invito a offrire un caffe', alla chiusura e dalle impostazioni. Nella 1.76.0 Maiuscolo con Canc manda nel cestino una cartella vuota, e dove il cestino non c'e' lo dice. Nella 1.77.0 F11 scrive i dettagli dei contenitori, e i conti delle cartelle si rifanno dopo il cestino. Nella 1.77.1 il contatore e l'apertura dei rami di rete con la lettura protetta. Nella 1.79.0 Maiuscolo con F9 chiude tutta la plancia e Maiuscolo con F10 la apre tutta. Nella 1.80.0 i sottotitoli a immagini e quelli impressi, letti con il riconoscimento dei caratteri di Windows. Nella 1.82.0 il testo del karaoke, con Maiuscolo con F2, e le voci Dove vanno sottotitoli e karaoke, Testo del karaoke e Anticipo del karaoke. Nella 1.83.0 la barra braille a blocchi, con le celle e il tempo minimo di lettura. Nella 1.83.1 Maiuscolo con F10 lascia chiuso Questo PC, e la plancia molto aperta non ferma piu' la finestra. Nella 1.83.2 F10 a fette, e i suoni delle aperture che non si sovrappongono.

"""La finestra di MeTeOra.

Tre aree, nell'ordine di tabulazione: la plancia dei comandi (F5), un albero;
la console (F6), dove scorrono i riscontri di ogni azione; il cruscotto
(F7), che mostra i tasti del contesto da cui ci si e' arrivati.
I tasti a lettera valgono in tutta la finestra e li intercetta EVT_CHAR_HOOK,
prima dei controlli: per questo l'albero non ha la ricerca per iniziale. Un
carattere senza comando lo dice, con il suo suono, e all'albero non arriva.
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
import time
import traceback
import warnings
from ctypes import wintypes
from html.parser import HTMLParser

import wx

import braille
import dettagli
import formati
import karaoke
import marcatori
import midi
import ocr
import percorsi
import questa_rete
import questo_pc
import schede_audio
import sintesi
import sottobrani
import sottotitoli_ocr
import suoni
import tag
import valori
import version
from contatore import Contatore
from dialoghi import DialogoConferma, DialogoDonazione, DialogoTesto, FinestraImpostazioni, FinestraMarcatori, FinestraScelta
from filtro import COMMENTO, ErroreFiltro, Filtro, modello_della_console
from impostazioni import Impostazioni
from marcatori import Marcatori
from motore import VOLUME_MASSIMO, durata_del_sottobrano, sottobrano_risolto
from playlist import Archivio, Brano, Coda, Playlist
from ricerca import AlberoDeiRisultati, NonRisponde, Ricerca, in_rete, leggi_in_rete, senza_annidati
from schedario import Schedario
from valori import AREE, ErroreValore, leggi_tempo, leggi_tempo_nel_brano, secondi_da_leggere
from video import FinestraVideo

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
# E al piu' tante voci in tutto: una cartella aperta porta con se' tutti i suoi
# file, e con centinaia di migliaia di voci ogni rinfresco della plancia
# fermava la finestra (collaudo della 1.83.0).
MASSIMO_DI_VOCI = 10000
# Fra un rinfresco della plancia e il seguente passa almeno tante volte il
# tempo dell'ultimo: con una plancia molto aperta un rinfresco dura anche un
# secondo, e farne uno a ogni avviso del contatore e dello schedario fermava
# la finestra (collaudo della 1.83.0).
PAUSA_FRA_I_RINFRESCHI = 3
# Le aperture in blocco, F10 e Maiuscolo con F10, dicono il loro inizio, con
# il suono, solo se durano piu' di tanti secondi (1.83.2).
RITARDO_DELL_AVVIO = 0.4
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
    ("n", True): "riproduzione_casuale",
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
    # Anche qui a sinistra si scende e a destra si sale: O abbassa la banda,
    # P la alza (Gabriele, collaudo della 1.60.0).
    ("o", False): "banda_giu",
    ("p", False): "banda_su",
    ("è", False): "azzera_la_banda",
    ("è", True): "azzera_le_bande",
    ("l", False): "dissolvenza",
    ("l", True): "durata_della_dissolvenza",
}
# I segni sopra le cifre nella tastiera italiana: Maiuscolo con 1 e' il punto
# esclamativo, e cosi' via fino a Maiuscolo con 0, l'uguale.
CIFRE_COL_MAIUSCOLO = {"!": 1, '"': 2, "£": 3, "$": 4, "%": 5, "&": 6, "/": 7, "(": 8, ")": 9, "=": 10}
# I nomi da leggere dei segni che arrivano come tasti senza comando: la
# punteggiatura, con la lettura predefinita di NVDA, spesso non si sente.
NOMI_DEI_SEGNI = {
    "'": "apostrofo", ",": "virgola", ".": "punto", ";": "punto e virgola", ":": "due punti", "-": "trattino", "_": "trattino basso",
    "+": "più", "*": "asterisco", "<": "minore", ">": "maggiore", "?": "punto interrogativo", "^": "accento circonflesso",
    "ì": "i accentata", "é": "e accentata acuta", "ò": "o accentata", "à": "a accentata", "ù": "u accentata", "ç": "c con la cediglia",
    "°": "grado", "§": "paragrafo", "[": "parentesi quadra aperta", "]": "parentesi quadra chiusa", "{": "parentesi graffa aperta",
    "}": "parentesi graffa chiusa", "@": "chiocciola", "#": "cancelletto", "€": "euro", "~": "tilde", "`": "accento grave",
}

TASTI_COMUNI = [
    "X suona la voce selezionata, riprende dalla pausa o fa ripartire da capo il brano che suona già; C pausa, V stop, Z e B brano precedente e successivo, N brano a caso, "
    "Maiuscolo con N la riproduzione casuale, con cui B sceglie a caso e Z torna ai brani suonati prima.",
    "Q ed E indietro e avanti nel brano, Maiuscolo con Q ed E ne cambiano i secondi, W va a un tempo, più e meno volume, Maiuscolo con M il passo del volume, M muto.",
    "A e D rallentano e accelerano, S torna alla velocità normale; F e H abbassano e alzano il tono di un semitono, G lo riporta al normale.",
    "U e I scelgono la banda dell'equalizzatore, O e P la abbassano e la alzano di un dB, È la azzera, Maiuscolo con È le azzera tutte.",
    "L accende e spegne la dissolvenza incrociata: con lei sfumano i cambi di brano, lo stop, la pausa, X da capo e i marker; Maiuscolo con L ne chiede la durata.",
    "Maiuscolo con X, a giro: punto A del loop sul brano selezionato, poi punto B, poi toglie il loop.",
    "Il video, con Maiuscolo e i tasti funzione: F1 lo accende e lo spegne, F2 sceglie i sottotitoli letti a giro, F3 la traccia audio a giro, F5 lo schermo intero, F6 il rapporto dell'immagine a giro.",
    "J e K aprono e suonano la playlist precedente e successiva, le cifre da 1 a 0 le prime dieci playlist.",
    "Nella plancia Backspace chiude il ramo in cui sei e risale di un livello, Maiuscolo con Backspace risale di colpo all'unità o alla playlist, Preferiti compresi, e chiude i rami al suo interno.",
    "T mette un marker dove sei, o rinomina quello su cui sei; R e Y vanno al marker precedente e successivo; Maiuscolo con R, Y e T tolgono i marker prima, dopo e tutti; Maiuscolo con le cifre da 1 a 0 va ai primi dieci marker del brano della plancia.",
    "F4 mette nei Preferiti il brano selezionato. F5 plancia, F6 console, F7 cruscotto, F8 porta la selezione e il fuoco della plancia sul brano in riproduzione e Maiuscolo con F8 ce la tiene agganciata, "
    "F9 chiude e F10 apre tutto il ramo col fuoco, Maiuscolo con F9 chiude tutta la plancia e Maiuscolo con F10 la apre tutta, tranne Questo PC e Questa rete; "
    "F11 legge i tag del brano selezionato, o i dettagli di una cartella, di un'unità o di una playlist, e Maiuscolo con F11 apre il menu dei tag.",
    "Barra rovesciata: nella console cerca nella console, altrove nel ramo della plancia in cui sei, e da Apri file o Impostazioni in tutto MeTeOra; Ctrl con la barra rovesciata cerca in tutto MeTeOra, anche dalla console. "
    "Barra verticale: il filtro della playlist o dei Preferiti in cui sta la plancia, anche dalla console.",
    "F1 apre il manuale nel browser; F12 scrive nella console la guida rapida dei tasti, F2 le novità e F3 i crediti, sempre nella console. Esc esce salvando tutto.",
]
# Le righe del cruscotto proprie di ogni tipo di voce della plancia.
TASTI_DEL_CONTESTO = {
    "risultati": ("i Risultati della ricerca", "Invio, Applicazioni o Spazio: menu con Riproduci, Salva come playlist, Nuova ricerca, che cerca in tutto MeTeOra, e Ferma la ricerca."),
    "altri": ("la voce che mostra altri risultati", "Invio mostra i risultati seguenti."),
    "gruppo_risultati": ("un ramo dei Risultati", "Freccia destra lo apre: i risultati stanno come stavano, sotto la loro playlist o lungo il percorso della loro cartella. Invio, Applicazioni o Spazio: menu con Salva come playlist."),
    "preferiti": ("i Preferiti", "Invio, Applicazioni o Spazio: menu con Riproduci, Filtro e, se c'è un filtro, Togli il filtro. Barra verticale: il filtro. Canc su un loro brano lo toglie dai Preferiti."),
    "radice_playlist": ("il ramo Playlist", "Invio, Applicazioni o Spazio: menu con Nuova playlist."),
    "playlist": ("una playlist", "Invio, Applicazioni o Spazio: menu con Riproduci, Filtro, Togli il filtro se c'è un filtro, Rinomina ed Elimina. Barra verticale: il filtro. Canc elimina la playlist, dopo una conferma."),
    "brano": ("un brano di una playlist", "Invio, Applicazioni o Spazio: menu con Riproduci, Sposta su, giù, in cima e in fondo, Saltato, Togli dalla playlist, Aggiungi ai preferiti, Rinomina file, Leggi i tag e Tag per i formati che li hanno, e Manda nel cestino. "
        "Canc toglie il brano dalla playlist, Maiuscolo con Canc manda il file nel cestino. Un SID o un file delle console con più sottobrani, o un brano con dei marker, si apre con freccia destra."),
    "pc": ("Questo PC", "Freccia destra mostra le unità. Invio, Applicazioni o Spazio: menu con Aggiorna."),
    "rete": ("Questa rete", "Freccia destra mostra i percorsi di rete, i computer della rete e il comando per aggiungere un percorso. Invio, Applicazioni o Spazio: menu con Aggiungi un percorso di rete e Aggiorna."),
    "computer_della_rete": ("i computer della rete", "Freccia destra li cerca, in disparte: può volerci qualche secondo. Invio, Applicazioni o Spazio: menu con Cerca di nuovo."),
    "computer": ("un computer della rete", "Freccia destra mostra le sue cartelle condivise. Invio, Applicazioni o Spazio: menu con Aggiorna."),
    "attesa": ("una ricerca in corso", "Aspetta: la voce sparisce quando la ricerca finisce."),
    "unita": ("un'unità", "Freccia destra mostra il contenuto. Invio, Applicazioni o Spazio: menu con Riproduci, Crea playlist da qui, Aggiungi alla playlist e Aggiorna."),
    "cartella": ("una cartella", "Freccia destra mostra il contenuto. Invio, Applicazioni o Spazio: menu con Riproduci, Crea playlist da qui, Aggiungi alla playlist e Aggiorna. "
        "Maiuscolo con Canc la manda nel cestino, se è vuota."),
    "file": ("un file", "Invio, Applicazioni o Spazio: menu con Riproduci, Aggiungi alla playlist, Aggiungi ai preferiti, Rinomina file, Leggi i tag e Tag per i formati che li hanno, e Manda nel cestino. "
        "Maiuscolo con Canc manda il file nel cestino. Un SID o un file delle console con più sottobrani, o un file con dei marker, si apre con freccia destra."),
    "sottobrano": ("un sottobrano di un SID o di un file delle console", "Invio, Applicazioni o Spazio: menu con Riproduci, Aggiungi alla playlist e Aggiungi ai preferiti. Se ha dei marker, freccia destra li mostra."),
    "marker": ("un marker", "Invio rinomina il marker, Canc lo elimina, X fa come sul suo brano. Applicazioni o Spazio: menu con Vai al marker, che suona il brano da lì, Rinomina ed Elimina."),
    "comando": ("un comando", "Invio esegue il comando."),
}
# Le voci della finestra delle impostazioni, in ordine: chiave -> (etichetta,
# participio per dire che non e' cambiata; None per le voci che fanno
# un'azione invece di cambiare un valore).
def _stesso_posto(a, b):
    """Vero se due (playlist, brano, sottobrano) sono lo stesso posto: la
    stessa playlist e lo stesso brano, non due uguali, e lo stesso numero."""
    return a[0] is b[0] and a[1] is b[1] and a[2] == b[2]


def _frase_della_casuale(accesa, modello):
    if accesa:
        return f"Riproduzione casuale accesa: {valori.MODELLI_CASUALI[modello]}."
    return "Riproduzione casuale spenta: a fine brano si va avanti in ordine."


# Le righe della lista dei modelli della riproduzione casuale.
SPIEGAZIONI_DEI_MODELLI = {
    "totale": "ogni volta un brano qualsiasi, mai lo stesso due volte di fila",
    "una_volta": "ogni brano suona una volta, poi la riproduzione finisce",
    "a_giro": "ogni brano suona una volta, poi si rimescola e si ricomincia",
}
# Quanti secondi la plancia aspetta una cartella di rete senza che arrivi
# niente: la finestra intanto e' ferma, quindi meno della ricerca (1.77.1).
ATTESA_NELLA_PLANCIA = 8.0
# I contenitori di cui F11 scrive i dettagli, invece dei tag (1.77.0).
TIPI_CON_I_DETTAGLI = ("cartella", "unita", "pc", "playlist", "radice_playlist", "risultati", "gruppo_risultati")
# Quanti brani ricorda la storia della riproduzione casuale, che Z ripercorre.
MASSIMO_DELLA_STORIA = 1000
# Il segno che il mazzo della riproduzione casuale e' finito, e che la
# riproduzione si ferma.
FINE_DEL_MAZZO = object()


# Su quanti file insieme si leggono e si modificano i tag.
MASSIMO_DI_FILE_PER_I_TAG = 1000
# La frase dei MIDI lasciati da preparare, con un No a una delle domande.
MIDI_DA_PREPARARE = "I MIDI restano da preparare: si può fare anche dalle impostazioni, con Banco dei suoni MIDI."
# Da quanti secondi d'attesa in su la console dice che il SID, il MIDI o il
# brano della console si prepara.
ATTESA_DA_DIRE = 1.5


# I rapporti dell'immagine di Maiuscolo con F6, a giro: il valore per mpv e
# il nome da leggere. -1 e' quello del file.
RAPPORTI = (("-1", "quello del video"), ("16:9", "16:9"), ("4:3", "4:3"), ("2.33:1", "21:9"))
# I nomi delle lingue piu' comuni nelle tracce, dai codici di tre lettere.
LINGUE = {"ita": "italiano", "eng": "inglese", "fre": "francese", "fra": "francese", "ger": "tedesco", "deu": "tedesco", "spa": "spagnolo",
    "por": "portoghese", "jpn": "giapponese", "chi": "cinese", "zho": "cinese", "rus": "russo", "dut": "olandese", "nld": "olandese",
    "swe": "svedese", "pol": "polacco", "kor": "coreano", "ara": "arabo", "und": None}


def _descrivi_traccia(traccia, indice, totale):
    """Una traccia audio o di sottotitoli da leggere: "2 di 3, italiano,
    Commento del regista, ac3"."""
    lingua = traccia.get("lang")
    parti = [f"{indice + 1} di {totale}", LINGUE.get(lingua, lingua), traccia.get("title"), traccia.get("codec")]
    return ", ".join(str(parte) for parte in parti if parte)


def midi_in_disparte(lavoro, al_termine):
    """Fa lavoro() in un filo a parte e passa il risultato ad al_termine:
    gli scaricamenti e la ricerca dei banchi non fermano la finestra."""
    threading.Thread(target=lambda: al_termine(lavoro()), name="MeTeOra, preparazione dei MIDI", daemon=True).start()


def _frase_del_video(acceso):
    if acceso:
        return "Video acceso: i video si vedono in una finestra sopra MeTeOra."
    return "Video spento: dei video si sente solo l'audio."


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
    "casuale": ("Riproduzione casuale (Maiuscolo+N)", "cambiata"),
    "modello_casuale": ("Modello della riproduzione casuale", "cambiato"),
    "video": ("Video (Maiuscolo+F1)", "cambiato"),
    "sottotitoli": ("Sottotitoli letti (Maiuscolo+F2)", "cambiati"),
    "sintesi": ("Sintesi di sottotitoli e karaoke", "cambiata"),
    "destinazione": ("Dove vanno sottotitoli e karaoke", "cambiato"),
    "karaoke": ("Testo del karaoke", "cambiato"),
    "anticipo_karaoke": ("Anticipo del karaoke", "cambiato"),
    "celle_braille": ("Celle della barra braille", "cambiate"),
    "lettura_minima": ("Tempo minimo di lettura in braille", "cambiato"),
    "banco_midi": ("Banco dei suoni MIDI", "cambiato"),
    "insegui": ("Inseguimento della plancia (Maiuscolo+F8)", "cambiato"),
    "caratteri": ("Dimensioni dei caratteri", "cambiate"),
    "colori_testo": ("Colori dei caratteri", "cambiati"),
    "colori_sfondo": ("Colori dello sfondo", "cambiati"),
    "righe_della_console": ("Righe della console", "cambiate"),
    "salva_console": ("Salva console", None),
    "marcatori": ("Marcatori", None),
    "importa_marcatori": ("Importa marcatori", None),
    "impressi": ("Sottotitoli impressi", "cambiati"),
    "dona": ("Dona per questo progetto", None),
}
# Come si leggono i sottotitoli impressi nel video, 1.80.0: le righe della scelta.
MODI_DEGLI_IMPRESSI = {
    "al_volo": "letti al volo, mentre il video suona, con circa mezzo secondo di ritardo",
    "passata": "letti prima, con una passata che salva accanto al video un file usato le volte dopo",
}
# Il testo del karaoke, 1.82.0: le righe della scelta.
MODI_DEL_KARAOKE = {
    "riga": "per riga",
    "strofa": "per strofa, dove il file le segna; altrimenti per riga",
}
# Il titolo della traccia che fa un file scritto dalla passata.
TITOLO_DELLA_PASSATA = "Sottotitoli impressi"
# Per _aggiorna_la_lettura: la traccia scelta la dicono le tracce.
_DALLE_TRACCE = object()


def _traccia_della_passata(tracce):
    """La traccia del file di una passata dei sottotitoli impressi, o None."""
    return next((t for t in tracce["sub"] if t.get("title") == TITOLO_DELLA_PASSATA), None) if tracce else None
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


# L'id del primo capitolo di manuale.html, la guida rapida che F12 scrive
# nella console (1.72.0).
ID_DELLA_GUIDA = "guida-rapida"


class _LettoreDellaGuida(HTMLParser):
    """Legge la guida rapida di manuale.html: dal titolo h2 con l'id della
    guida, compreso, fino al titolo h2 seguente. Ogni titolo, voce di elenco
    e paragrafo diventa una riga, senza i tag, con le entita' decodificate e
    gli spazi ridotti a uno."""

    BLOCCHI = ("h2", "h3", "h4", "li", "p")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.righe = []
        # prima della guida, dentro, o dopo: dopo non si legge piu' niente.
        self._stato = "prima"
        self._aperti = []
        self._pezzi = []

    def handle_starttag(self, tag, attrs):
        if tag == "h2" and self._stato == "dentro":
            self._a_capo()
            self._aperti = []
            self._stato = "dopo"
        elif tag == "h2" and self._stato == "prima" and dict(attrs).get("id") == ID_DELLA_GUIDA:
            self._stato = "dentro"
        if self._stato != "dentro":
            return
        if tag in self.BLOCCHI:
            # Un blocco dentro un altro, come un elenco dentro una voce: il
            # testo fin qui e' una riga, quello dentro un'altra.
            self._a_capo()
            self._aperti.append(tag)
        elif tag == "br":
            self._pezzi.append(" ")

    def handle_endtag(self, tag):
        if self._stato != "dentro" or tag not in self._aperti:
            return
        self._a_capo()
        while self._aperti.pop() != tag:
            pass

    def handle_data(self, data):
        if self._stato == "dentro" and self._aperti:
            self._pezzi.append(data)

    def close(self):
        super().close()
        self._a_capo()

    def _a_capo(self):
        riga = " ".join("".join(self._pezzi).split())
        if riga:
            self.righe.append(riga)
        self._pezzi = []


def guida_rapida(testo):
    """Le righe della guida rapida del manuale in HTML, titolo compreso;
    lista vuota se il manuale non ce l'ha."""
    lettore = _LettoreDellaGuida()
    lettore.feed(testo)
    lettore.close()
    return lettore.righe


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


def al_plurale(n, singolare, plurale):
    """'1 brano', '3 brani': il numero con la parola giusta."""
    return f"1 {singolare}" if n == 1 else f"{n} {plurale}"


def brani_al_plurale(n):
    return al_plurale(n, "brano", "brani")


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
    "r sottobrani dei SID e della musica delle console, come r>1.",
    "Questi solo con l'uguale:",
    "k tipo: k=sid, k=audio, k=video, k=tracker, k=midi, k=chip, o un'estensione come k=flac.",
    "a autore, come a=hubbard.",
    "n titolo, come n=commando.",
    "l album.",
    "g genere.",
    "p percorso della cartella, come p=c64music.",
    "s saltato: s=1 i brani saltati, s=0 gli altri.",
    REGOLA_DEL_DOLLARO,
]
ISTRUZIONI_DEL_FILTRO = ["Puoi usare questi comandi per comporre il filtro.", *_GRAMMATICA_DEL_FILTRO]
ISTRUZIONI_DELLA_RICERCA = ["Puoi usare questi comandi per comporre la ricerca, in tutte le playlist, in tutte le unità e nei percorsi di rete aggiunti a mano.", *_GRAMMATICA_DEL_FILTRO]
# Dove cerca Ctrl con la barra rovesciata, la ricerca in tutto MeTeOra.
OVUNQUE = "nelle playlist, nei dischi e in rete"
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
            al_passaggio=lambda percorso, sottobrano: wx.CallAfter(self._passaggio, percorso, sottobrano),
            al_caricamento=lambda: wx.CallAfter(self._aggiorna_il_video),
            ai_sottotitoli=lambda testo: wx.CallAfter(self._sottotitolo, testo), ai_sottotitoli_a_immagini=self._sottotitolo_a_immagini,
            al_salto=self._testo_superato)
        # Velocita', tono, equalizzatore e dissolvenza salvati valgono per tutti
        # i brani, dal primo.
        self._applica_la_riproduzione()
        # Il brano che esce quando il motore ha chiesto il seguente, come
        # (playlist, brano, sottobrano), e il seguente preparato, come
        # (playlist, brano, sottobrano chiesto): servono al passaggio, per
        # ricontrollare. None fuori da un passaggio preparato.
        self._uscente = None
        self._preparato = None
        # La scelta della riproduzione casuale, come (cio' che suona, il
        # seguente scelto): vedi _seguente_casuale.
        self._casuale_ricordato = None
        # Il segno dei dettagli che F11 sta raccogliendo: un altro F11 lo cambia (1.77.0).
        self._dettagli_attesi = None
        # La lettura dei sottotitoli fatti di immagini in corso, una di
        # sottotitoli_ocr, o None; la passata in anticipo in corso, o None
        # (1.80.0). La scelta degli impressi sta nelle impostazioni.
        self._lettura = None
        self._passata = None
        # I video su cui la passata non ha trovato niente: in questa sessione
        # non si rifa'.
        self._passate_vuote = set()
        # Il segno dell'apertura di tutta la plancia in corso, Maiuscolo con
        # F10: un tasto qualsiasi lo toglie, e l'apertura si ferma (1.79.0).
        self._apertura_della_plancia = None
        # Il mazzo della riproduzione casuale (1.61.0): i brani gia' usciti,
        # come (id della playlist, id del brano, sottobrano), con le
        # playlist e i brani tenuti in vita, perche' un id non torni a un
        # oggetto nuovo. _mazzo_finito dice a _fine_della_lista perche' ci si
        # ferma.
        self._mazzo = set()
        self._mazzo_tenuti = []
        self._mazzo_finito = False
        # La storia della riproduzione casuale (1.74.0): i posti (playlist,
        # brano, sottobrano) suonati con il casuale acceso, e l'indice di
        # quello in cui si e'. Z ci torna indietro; B e l'avanzamento
        # automatico, dopo Z, ci rivanno avanti prima di scegliere a caso,
        # come in Winamp. Si azzera quando il casuale si accende o si spegne.
        self._storia = []
        self._nella_storia = -1
        # Il posto della storia che Z, B o l'avanzamento stanno per suonare:
        # solo lui sposta l'indice, ogni altro brano che parte va in fondo.
        self._atteso_dalla_storia = None
        # Il video, tappa 7: la sua finestra, nata al primo video; se il
        # motore disegna gia' nei suoi pannelli; il rapporto dell'immagine
        # scelto con Maiuscolo+F6, come indice di RAPPORTI; la finestra che
        # aveva il fuoco prima del video, per riportarcelo; la sintesi dei
        # sottotitoli letti.
        # I MIDI, tappa 8: vero mentre si scarica FluidSynth, si cercano i
        # banchi o si scarica FluidR3.
        self._midi_in_preparazione = False
        self._video = None
        self._video_nel_motore = False
        # Il brano su cui la finestra del video e' stata nascosta a mano, con
        # Esc o chiudendola: per lui non si riapre.
        self._video_nascosto_per = None
        # La finestra del video rimandata perche' era aperto un dialogo, e il
        # brano ripreso all'avvio in pausa, che la apre con X (tappa 9).
        self._video_rimandato = False
        self._video_in_attesa = None
        self._rapporto = 0
        # La domanda il cui suono aspetta la fine dell'effetto prima, e il
        # brano seguente che aspetta la fine del suono di un errore.
        self._domanda_viva = None
        self._avanzamento_dopo_errore = None
        self._sintesi = sintesi.Sintesi()
        # La barra braille a blocchi (1.83.0): i testi letti in fila, con il
        # tempo minimo di lettura; le attese sono di wx, nel filo della finestra.
        self._braille = braille.Coda(self._mostra_in_braille, lambda secondi, funzione: wx.CallLater(max(1, round(secondi * 1000)), funzione))
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
        self._dove_si_cerca = OVUNQUE
        self.risultati = None
        # Quanti risultati della ricerca sono gia' passati nella plancia.
        self._risultati_letti = 0
        self.nodo_risultati = None
        self._albero_dei_risultati = None
        # I rinfreschi chiesti dallo schedario e dal contatore, accorpati.
        self._rinfreschi = set()
        self._rinfresco_pianificato = False
        self._prossimo_rinfresco = 0.0
        self.schedario = Schedario(os.path.join(cartella_dati, FILE_SCHEDARIO), avvisa=lambda: wx.CallAfter(self._rinfresco_chiesto, "schede"))
        self.schedario.carica()
        self.contatore = Contatore(self.schedario, avvisa=lambda: wx.CallAfter(self._rinfresco_chiesto, "conti"))
        # Il segnale che fa aspettare i fili del contatore e dello schedario
        # mentre la finestra rinfresca o apre la plancia (1.83.1).
        self._cedi = threading.Event()
        self.schedario.cedi = self.contatore.cedi = self._cedi
        # I totali delle cartelle, per le loro etichette: cartella -> [i file
        # del contatore, quanti hanno la durata, la somma, il numero
        # dell'ultima variazione dello schedario compresa] (1.83.1).
        self._totali = {}
        # I file con una scheda nuova, le cui etichette vanno rifatte.
        self._schede_nuove = set()
        # Durante l'apertura di tutta la plancia, o di un ramo intero, le
        # cartelle vuote e quelle che non si leggono non suonano una per
        # una: si contano, e la fine lo dice (1.83.1).
        self._taciuti = None
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
        # Quante righe in fondo non si tagliano mentre F2, F3, F11 o F12 scrivono.
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
        self.Bind(wx.EVT_ACTIVATE, self._all_attivazione)
        self.scrivi(f"MeTeOra {version.VERSION} del {version.DATE}. Pronto: F1 apre il manuale nel browser, F12 scrive nella console la guida rapida dei tasti, F7 apre il cruscotto con i tasti del punto in cui ti trovi.")
        fuori_dal_normale = self._riproduzione_fuori_dal_normale()
        if fuori_dal_normale:
            self.scrivi(fuori_dal_normale)
        if self.impostazioni.errore:
            nuovo = os.path.basename(self.impostazioni.percorso)
            if self.impostazioni.da_nuovo:
                testo = f"Il file delle impostazioni non si legge: {self.impostazioni.errore}. Riparto da quelle salvate in {nuovo}."
            else:
                testo = f"Il file delle impostazioni non si legge, e parto con quelle predefinite: {self.impostazioni.errore}. Le impostazioni nuove vanno in {nuovo}."
            self._avviso_all_avvio("errore", testo)
        if errore_archivio:
            self._avviso_all_avvio("errore", f"Il file delle playlist non si legge, e parto senza playlist: {errore_archivio}")
            # Il file illeggibile non va sovrascritto alla prima modifica.
            self.archivio.percorso += ".nuovo"
        if self.marcatori.errore:
            self._avviso_all_avvio("errore", f"Il file dei marker non si legge, e resta com'è: {self.marcatori.errore}. I marker nuovi vanno in {os.path.basename(self.marcatori.percorso)}.")
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
        self.albero.Bind(wx.EVT_CHAR, self._carattere_nell_albero)
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
        self.nodo_rete = self.albero.AppendItem(radice, "Questa rete", data={"tipo": "rete", "caricato": False})
        self.albero.SetItemHasChildren(self.nodo_rete, True)
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
        # Un riscontro e' l'esito di una domanda: quella rimandata non suona piu'.
        self._domanda_viva = None
        self._suono(evento)
        self.scrivi(testo, categoria)

    def _dopo_il_suono(self, funzione, *argomenti):
        """Chiama funzione quando finisce l'ultimo effetto partito: due suoni
        nello stesso istante si fondono in uno, e quello che informa non si
        riconosce piu' (tappa 9). Se non suona niente, subito."""
        if self._chiusa:
            return
        attesa = suoni.attesa()
        if attesa <= 0:
            funzione(*argomenti)
            return
        # Allo scadere si guarda di nuovo: intanto puo' essere partito un
        # altro suono, anche lui rimandato.
        wx.CallLater(round(attesa * 1000) + 30, self._dopo_il_suono, funzione, *argomenti)

    def _riscontro_dopo(self, evento, testo):
        """Il riscontro con la riga subito e il suono dopo l'ultimo effetto."""
        self._domanda_viva = None
        self.scrivi(testo)
        self._dopo_il_suono(self._suono, evento)

    def _domanda(self):
        """Il suono della domanda, prima di un campo o di una scelta: dopo
        l'ultimo effetto, per esempio quello dell'errore che riapre il campo.
        Se intanto il campo ha gia' un esito, come Esc, non suona piu'."""
        segno = self._domanda_viva = object()
        self._dopo_il_suono(self._suona_la_domanda, segno)

    def _suona_la_domanda(self, segno):
        if segno is self._domanda_viva:
            self._domanda_viva = None
            self._suono("domanda")

    def _annullato(self, testo):
        """Esc in un campo, o No a una domanda: l'operazione non si fa. Il
        suono aspetta l'effetto prima, per esempio l'errore che ha riaperto
        il campo."""
        self._riscontro_dopo("annullamento", testo)

    def _avviso_all_avvio(self, evento, testo):
        """Un avviso nato mentre la finestra si costruisce: la riga subito, il
        suono dopo quello dell'avvio, che parte con la finestra mostrata."""
        self.scrivi(testo)
        wx.CallAfter(self._dopo_il_suono, self._suono, evento)

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
            righe = ["Tasti per la console.", "Frecce, Pagina su e giù, Inizio e Fine per leggere; i messaggi nuovi arrivano in fondo, con l'ora. "
                "La barra rovesciata cerca nella console, anche con i jolly e le virgolette, e Invio passa all'occorrenza seguente."]
        elif len(self._voci_selezionate()) > 1:
            righe = [f"Tasti per {len(self._voci_selezionate())} voci selezionate: un ramo selezionato vale per tutto ciò che contiene.",
                "X suona la selezione come una playlist invisibile, che resta finché non premi V. Invio, Applicazioni o Spazio: menu della selezione, con Leggi i tag e Modifica i tag. "
                "Canc toglie i brani dalle playlist ed elimina le playlist e i marker, Maiuscolo con Canc manda i file nel cestino, F4 li mette nei Preferiti.",
                "Maiuscolo con le frecce allarga la selezione, Ctrl con le frecce muove il fuoco senza selezionare, Ctrl con Spazio accende e spegne la voce col fuoco."]
        else:
            # La voce su cui agiscono Canc, X, F4 e il menu, che puo' non
            # essere quella col fuoco (tappa 9).
            voce = self._voce_di_lavoro()
            dati = self._dati(voce) or {}
            tipo = "preferiti" if dati.get("tipo") == "playlist" and dati["playlist"] is self.archivio.preferiti else dati.get("tipo")
            nome, riga = TASTI_DEL_CONTESTO.get(tipo, ("la plancia", ""))
            righe = [f"Tasti per {nome}."] + ([riga] if riga else [])
            if tipo == "cartella" and dati.get("a_mano"):
                righe.append("Canc, o Togli il percorso nel menu, lo toglie da Questa rete; i file restano dove sono.")
            if voce != self._voce_corrente():
                righe.append("Il fuoco è su un'altra voce: le frecce, F9, F10, J, K e la barra verticale partono da lì; Canc, Maiuscolo con Canc, X, Maiuscolo con X, F4, F11, "
                    "Maiuscolo con F11, Maiuscolo con le cifre, la barra rovesciata e il menu agiscono sulla voce selezionata.")
        return righe + TASTI_COMUNI

    def _vai(self, controllo, evento):
        self._suono(evento)
        if not self.IsActive():
            self.Raise()
        if controllo is self.cruscotto and self.cruscotto.HasFocus():
            self._rinfresca_cruscotto()
        controllo.SetFocus()

    # I tasti.

    def _tasto(self, evento):
        """I tasti di tutta la finestra. Quando un comando ha finito il suo
        lavoro, dialoghi compresi, il beep dice se ha portato il fuoco della
        plancia a un altro livello."""
        prima = self._profondita(self._voce_corrente())
        if self._apertura_della_plancia is not None and evento.GetKeyCode() not in _SOLO_MODIFICATORI:
            # Un tasto qualsiasi ferma l'apertura di tutta la plancia, prima
            # di fare il suo lavoro: niente rami tolti sotto di lei.
            self._ferma_l_apertura()
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
            wx.WXK_F7: lambda: self._vai(self.cruscotto, "cruscotto"), wx.WXK_F4: self._f4, wx.WXK_F8: self._vai_al_brano, wx.WXK_F9: self._chiudi_tutto, wx.WXK_F10: self._apri_tutto, wx.WXK_F11: self._comando_leggi_i_tag, wx.WXK_F12: self._elenco_dei_tasti,
            wx.WXK_ESCAPE: self.Close,
        }
        if modificatori == wx.MOD_NONE and codice in tasti_funzione:
            tasti_funzione[codice]()
            return True
        if modificatori == wx.MOD_SHIFT and codice == wx.WXK_F8:
            self._aggancia()
            return True
        if modificatori == wx.MOD_SHIFT and codice == wx.WXK_F9:
            self._chiudi_la_plancia()
            return True
        if modificatori == wx.MOD_SHIFT and codice == wx.WXK_F10:
            # Non apre piu' il menu della voce, come in Windows: quello resta
            # a Invio, al tasto Applicazioni e alla barra spaziatrice (Gabriele, 1.79.0).
            self._apri_la_plancia()
            return True
        if modificatori == wx.MOD_SHIFT and codice == wx.WXK_F11:
            self._comando_modifica_i_tag()
            return True
        tasti_del_video = {wx.WXK_F1: self._comando_video, wx.WXK_F2: self._comando_sottotitoli, wx.WXK_F3: self._comando_traccia_audio,
            wx.WXK_F5: self._comando_schermo_intero, wx.WXK_F6: self._comando_rapporto}
        if modificatori == wx.MOD_SHIFT and codice in tasti_del_video:
            tasti_del_video[codice]()
            return True
        if modificatori == wx.MOD_CONTROL and (evento.GetUnicodeKey() in (ord("\\"), 0x1C) or codice == ord("\\")):
            # Ctrl con la barra rovesciata: la ricerca in tutto MeTeOra (1.71.0).
            self._ricerca_globale()
            return True
        # Il tastierino numerico resta a NVDA, e Ctrl e Alt ai comandi di Windows.
        if modificatori not in (wx.MOD_NONE, wx.MOD_SHIFT) or wx.WXK_NUMPAD0 <= codice <= wx.WXK_NUMPAD_DIVIDE:
            evento.Skip()
            return False
        unicode = evento.GetUnicodeKey()
        # Canc arriva con il codice 127, come Invio, Tab ed Esc con i loro:
        # non sono caratteri da scrivere, e vanno ai controlli.
        if unicode == wx.WXK_NONE or unicode <= 32 or not chr(unicode).isprintable():
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
        # Un tasto senza comando lo dice, e non arriva all'albero, che ne
        # farebbe la sua ricerca per iniziale spostando il fuoco (tappa 9).
        segno = chr(unicode)
        nome = NOMI_DEI_SEGNI.get(segno.lower(), segno.upper() if segno.isalpha() else segno)
        self._riscontro("non_disponibile", f"{'Maiuscolo+' if maiuscolo else 'Il tasto '}{nome} non ha un comando.")
        return True

    def _carattere_nell_albero(self, evento):
        """I caratteri che arrivano fino all'albero, per esempio con AltGr o
        dal tastierino, si fermano qui: la ricerca per iniziale del controllo
        sposterebbe il fuoco senza un comando (tappa 9)."""
        codice = evento.GetUnicodeKey()
        if codice > 32 and chr(codice).isprintable():
            return
        evento.Skip()

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

    def _nome_della_voce(self, voce):
        """Il nome di una voce per le frasi della console, senza i conti, le
        durate e gli stati che ha nell'etichetta (tappa 9)."""
        dati = self._dati(voce) or {}
        tipo = dati.get("tipo")
        if tipo == "playlist":
            return dati["playlist"].nome
        if tipo == "unita":
            return dati.get("etichetta") or self.albero.GetItemText(voce)
        if tipo == "cartella":
            return dati.get("nome") or os.path.basename(dati["percorso"].rstrip("\\")) or dati["percorso"]
        if tipo in ("brano", "file"):
            brano = dati["brano"]
            return f"{brano.nome_del_file}, sottobrano {brano.sottobrano}" if brano.sottobrano else brano.nome_del_file
        if tipo == "sottobrano":
            return f"sottobrano {dati['numero']} di {dati['brano'].nome_del_file}"
        if tipo == "marker":
            return f"il marker {dati['marker']['nome']}"
        if tipo == "risultati":
            return f"Risultati di {self._testo_della_ricerca}"
        if tipo == "gruppo_risultati":
            return dati["gruppo"].nome
        return self.albero.GetItemText(voce)

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
        self._riscontro("risali", f"Chiuso {self._nome_della_voce(ramo)}.", "risali")

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
        # Il nome soltanto, senza i conti dell'etichetta.
        nome = self._nome_della_voce(antenato)
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
        """Vero per un SID o un file delle console con piu' sottobrani, che
        nella plancia diventa un ramo."""
        if brano.sottobrano is not None or not formati.ha_sottobrani(brano.percorso):
            return False
        info = sottobrani.info(brano.percorso)
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
            titoli = (sottobrani.info(brano.percorso) or {}).get("titoli") or []
            titolo = f", {titoli[n - 1]}" if n <= len(titoli) and titoli[n - 1] else ""
            parti = [f"Sottobrano {n} di {dati['totale']}{titolo}, {tempo(durata_del_sottobrano(brano.percorso, n))}"]
            if quanti:
                parti.append(f"{quanti} marker")
            if suona and self.motore.sottobrano == n:
                parti.append("in riproduzione")
            return ", ".join(parti)
        parti = [brano.percorso if dati.get("completo") else brano.nome_del_file]
        if brano.sottobrano:
            info = sottobrani.info(brano.percorso)
            parti[0] += f", sottobrano {brano.sottobrano}" + (f" di {info['sottobrani']}" if info else "")
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
            totale = sottobrani.info(brano.percorso)["sottobrani"]
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

    def _aggiorna_etichette(self, solo=None):
        """Rinfresca le etichette di brani, file e sottobrani: saltato, loop,
        marker, in riproduzione; con solo, un insieme di percorsi, solo
        quelle dei loro file, come quando arrivano schede nuove (1.83.1)."""
        for voce in self._tutte_le_voci():
            dati = self._dati(voce)
            if not dati or dati["tipo"] not in ("brano", "file", "sottobrano"):
                continue
            if solo is not None and dati["brano"].percorso not in solo:
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
            self._domanda()
            with FinestraFiltro(self, f"Filtro di {pl.nome}", testo, ISTRUZIONI_DEL_FILTRO) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self._annullato("Filtro non cambiato.")
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
            self._ritrova_dentro(dati)
        else:
            self._popola_playlist(seleziona=pl if dentro else None)
        passano = sum(1 for b in pl.brani if self._ammesso(pl, b))
        if testo:
            self._riscontro("filtro_messo", f"Filtro di {pl.nome}: {testo}. {'Passa' if passano == 1 else 'Passano'} {brani_al_plurale(passano)} su {len(pl.brani)}.")
        else:
            totale = len(pl.brani)
            quanti = "la playlist è vuota" if not totale else "passa l'unico brano" if totale == 1 else f"passano tutti i {totale} brani"
            self._riscontro("filtro_tolto", f"Filtro di {pl.nome} svuotato: {quanti}.")

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

    def _etichetta_della_cartella(self, cartella, nome=None, vuota=None):
        """Il nome della cartella con quanti file suonabili ha, sottocartelle
        comprese, e quanto durano in tutto, appena il contatore e lo schedario
        lo sanno. nome, se c'e', e' quello da mostrare al posto del suo, come
        per i percorsi di rete. Contata senza niente da suonare, dice
        (vuota), o (niente da suonare) se ha file d'altro tipo: succede alle
        cartelle svuotate con il cestino, che non spariscono (1.77.0)."""
        nome = nome or os.path.basename(cartella.rstrip("\\")) or cartella
        files = self.contatore.files(cartella)
        if cartella in self.contatore.parziali:
            # Il conto ha saltato una parte che in rete non rispondeva.
            if not files:
                return f"{nome} (la rete non risponde)"
            return f"{nome}, almeno {len(files)} file: la rete non risponde del tutto"
        if files == []:
            if vuota is None:
                vuota = self._e_vuota(cartella)
            return f"{nome} (vuota)" if vuota else f"{nome} (niente da suonare)"
        if not files:
            return nome
        # Il totale si somma una volta; poi lo aggiornano le variazioni dello
        # schedario. Risommare a ogni rinfresco tutti i file di un disco, per
        # ogni cartella aperta, fermava la finestra (collaudo della 1.83.0).
        totale = self._totali.get(cartella)
        if totale is None or totale[0] is not files:
            totale = self._totali[cartella] = [files, *self.schedario.totale_delle_durate(files)]
        con_durata, somma = totale[1], totale[2]
        testo = f"{nome}, {len(files)} file"
        if con_durata:
            testo += f", {durata_lunga(max(0.0, somma))} in tutto"
            if con_durata < len(files):
                testo += f", {len(files) - con_durata} senza durata"
        return testo

    def _applica_le_variazioni(self):
        """Le durate arrivate allo schedario aggiornano i totali delle
        cartelle che contengono i loro file, risalendo il percorso: solo
        quelle variazioni che il totale non comprende gia'. I file restano
        in _schede_nuove, per le loro etichette."""
        for numero, percorso, vecchia, nuova in self.schedario.variazioni():
            self._schede_nuove.add(percorso)
            cartella = os.path.dirname(percorso)
            while True:
                totale = self._totali.get(cartella)
                if totale is not None and numero > totale[3]:
                    totale[1] += (nuova is not None) - (vecchia is not None)
                    totale[2] += (nuova or 0) - (vecchia or 0)
                sopra = os.path.dirname(cartella)
                if sopra == cartella:
                    break
                cartella = sopra

    def _e_vuota(self, cartella):
        """Vero se la cartella non ha file, a parte quelli di servizio; in
        rete, anche su un'unita' con la lettera, non si guarda, perche' un
        disco spento terrebbe ferma la finestra."""
        if in_rete(cartella):
            return False
        try:
            return questo_pc.cartella_vuota(cartella)
        except OSError:
            return False

    def _aggiorna_cartelle(self):
        """Rinfresca le etichette delle cartelle caricate nella plancia, e
        toglie quelle che il contatore ha trovato senza niente da suonare,
        sottocartelle comprese, anche se il fuoco ci sta sopra o dentro."""
        self._applica_le_variazioni()
        vuote = set()
        for voce, dati, mostra_file in list(self._cartelle_della_plancia()):
            if dati.get("radice_di_rete"):
                continue
            # Una cartella aperta che mostra dei file non e' vuota, qualunque
            # cosa dica un conto fatto su una lettura vecchia: mostra_file.
            # Una cartella toccata dal cestino resta, e dice (vuota).
            parziale = dati["percorso"] in self.contatore.parziali
            if self.contatore.files(dati["percorso"]) == [] and not mostra_file and not dati.get("toccata") and not parziale:
                # Le voci arrivano prima dei loro figli: basta togliere il
                # ramo piu' in alto.
                if not self._dentro_una_di(voce, vuote):
                    vuote.add(voce)
                continue
            if dati.get("toccata") and self.contatore.files(dati["percorso"]) == [] and "vuota" not in dati:
                # Si guarda una volta sola, non a ogni avviso del contatore.
                dati["vuota"] = self._e_vuota(dati["percorso"])
            nuova = self._etichetta_della_cartella(dati["percorso"], dati.get("nome"), dati.get("vuota"))
            if self.albero.GetItemText(voce) != nuova:
                self.albero.SetItemText(voce, nuova)
        if vuote and self._apertura_della_plancia is None:
            # Mentre si apre tutta la plancia i rami non si tolgono: la fine
            # dell'apertura li ricontrolla.
            self._togli_dalla_plancia(vuote)

    def _cartelle_della_plancia(self):
        """Le cartelle caricate in Questo PC e in Questa rete, ciascuna prima
        di quelle che contiene, come (voce, dati, se e' caricata e mostra dei
        file). Si scende nelle cartelle, nelle unita' e nei rami della rete,
        non nei brani, e ogni figlio si guarda una volta sola: con migliaia di
        voci aperte il giro su tutta la plancia fermava la finestra (1.83.1)."""
        pila = [self.nodo_rete, self.nodo_pc]
        while pila:
            voce = pila.pop()
            dati = self._dati(voce) or {}
            dentro, ha_file = [], False
            for figlio in self._figli(voce):
                tipo = (self._dati(figlio) or {}).get("tipo")
                if tipo == "file":
                    ha_file = True
                elif tipo not in ("brano", "sottobrano", "marker"):
                    dentro.append(figlio)
            if dati.get("tipo") == "cartella":
                yield voce, dati, bool(dati.get("caricato")) and ha_file
            pila.extend(reversed(dentro))

    def _ramo_di_rete_muto(self, voce, dati):
        """Un ramo di rete che non risponde resta chiuso, da riaprire."""
        dati["caricato"] = False
        self.albero.SetItemHasChildren(voce, True)
        wx.CallAfter(self.albero.Collapse, voce)
        self._riscontro("errore", f"{dati['percorso']} non risponde: il computer o il disco di rete sono spenti, la rete non c'è, "
            "o la condivisione si è fermata. Aggiorna, sul ramo o su Questa rete, la riprova.")

    def _riconta(self, *cartelle):
        """Dopo un file o una cartella mandati nel cestino (Gabriele, 4
        ottobre 2026, 1.77.0): le cartelle che li contenevano si rileggono, e
        i conti loro e di chi le contiene si rifanno, cosi' risalendo le
        etichette dicono il vero. Le loro voci nella plancia non spariscono
        piu', nemmeno senza niente da suonare: dicono (vuota)."""
        da_rifare = set()
        for cartella in cartelle:
            da_rifare.update(self.contatore.cambiata(cartella))
        cambiate = {os.path.normcase(c.rstrip("\\")) for c in cartelle}
        for voce in [*self._tutte_le_voci(self.nodo_pc), *self._tutte_le_voci(self.nodo_rete)]:
            dati = self._dati(voce) or {}
            if dati.get("tipo") != "cartella":
                continue
            percorso = os.path.normcase(dati["percorso"].rstrip("\\"))
            if any(c == percorso or c.startswith(percorso + "\\") for c in cambiate):
                dati["toccata"] = True
                dati.pop("vuota", None)
        self.contatore.chiedi(sorted(da_rifare))
        self._aggiorna_cartelle()

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

    def _rinfresco_chiesto(self, cosa):
        """Nel filo della finestra: lo schedario ("schede") o il contatore
        ("conti") hanno novita'. I rinfreschi si accorpano, e fra la fine di
        uno e l'inizio del seguente passa almeno PAUSA_FRA_I_RINFRESCHI volte
        la sua durata, cosi' la finestra risponde anche con migliaia di voci
        aperte (1.83.1)."""
        self._rinfreschi.add(cosa)
        if self._rinfresco_pianificato or self._chiusa:
            return
        self._rinfresco_pianificato = True
        attesa = max(0.0, self._prossimo_rinfresco - time.monotonic())
        wx.CallLater(max(1, round(attesa * 1000)), self._rinfresca)

    def _rinfresca(self):
        self._rinfresco_pianificato = False
        cose, self._rinfreschi = self._rinfreschi, set()
        if self._chiusa or not cose:
            return
        inizio = time.monotonic()
        self._cedi.set()
        try:
            # Le schede nuove rinfrescano anche le cartelle.
            if "schede" in cose:
                self._schede_arrivate()
            else:
                self._conti_arrivati()
        finally:
            self._cedi.clear()
        fine = time.monotonic()
        self._prossimo_rinfresco = fine + PAUSA_FRA_I_RINFRESCHI * (fine - inizio)

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
        # Solo le etichette dei file con una scheda nuova: rifarle tutte, con
        # migliaia di voci aperte, fermava la finestra (1.83.1).
        self._applica_le_variazioni()
        nuove, self._schede_nuove = self._schede_nuove, set()
        self._aggiorna_etichette(solo=nuove)
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
        # Un sottobrano o un marker col fuoco si ritrova dentro il suo brano,
        # che rinasce chiuso (tappa 9).
        interno = None
        if seleziona is None and dentro and (self._dati(voce_selezionata) or {}).get("tipo") in ("sottobrano", "marker"):
            interno = dict(self._dati(voce_selezionata))
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
            if interno is not None:
                self._ritrova_dentro(interno)
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
        if tipo == "rete":
            self._riempi_la_rete(voce)
            return
        if tipo in ("computer_della_rete", "computer"):
            self._cerca_nella_rete(voce, dati)
            return
        di_rete = tipo in ("cartella", "unita") and in_rete(dati["percorso"])
        if di_rete and (os.path.splitdrive(dati["percorso"])[0].lower() in self.contatore.mute or not questa_rete.raggiungibile(dati["percorso"])):
            # Una cartella di rete spenta farebbe aspettare Windows anche mezzo
            # minuto, e una condivisione che si e' gia' fermata non risponde
            # piu': si lascia perdere, e il ramo resta da riaprire.
            self._ramo_di_rete_muto(voce, dati)
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
            totale = sottobrani.info(brano.percorso)["sottobrani"]
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
            cartelle, files = leggi_in_rete(dati["percorso"], attesa=ATTESA_NELLA_PLANCIA) if di_rete else questo_pc.contenuto(dati["percorso"])
        except NonRisponde:
            self.contatore.mute.add(os.path.splitdrive(dati["percorso"])[0].lower())
            self._ramo_di_rete_muto(voce, dati)
            return
        except OSError as e:
            if self._taciuti is not None:
                self._taciuti["illeggibili"] += 1
            else:
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
            if self._taciuti is not None:
                self._taciuti["vuote"] += 1
            else:
                self._riscontro("niente_da_suonare", "Niente da suonare qui dentro.")

    # Questa rete, 1.64.0.

    def _voce_di_rete(self, genitore, nome, percorso, a_mano=False):
        """Una cartella condivisa sotto Questa rete o sotto un computer: si
        apre come le cartelle di Questo PC, ma prima si prova se risponde, e
        resta nella plancia anche senza niente da suonare."""
        dati = {"tipo": "cartella", "percorso": percorso, "nome": nome, "caricato": False, "rete": True, "radice_di_rete": True}
        if a_mano:
            dati["a_mano"] = True
        voce = self.albero.AppendItem(genitore, nome, data=dati)
        self.albero.SetItemHasChildren(voce, True)
        return voce

    def _riempi_la_rete(self, voce):
        """I figli di Questa rete: i percorsi salvati in Windows, quelli
        scritti a mano, i computer della rete e il comando per aggiungere."""
        for nome, percorso in questa_rete.percorsi_salvati():
            self._voce_di_rete(voce, nome, percorso)
        for percorso in self.impostazioni["percorsi_di_rete"]:
            self._voce_di_rete(voce, percorso, percorso, a_mano=True)
        computer = self.albero.AppendItem(voce, "Computer della rete", data={"tipo": "computer_della_rete", "caricato": False})
        self.albero.SetItemHasChildren(computer, True)
        self.albero.AppendItem(voce, "Aggiungi un percorso di rete", data={"tipo": "comando", "comando": "aggiungi_percorso_di_rete"})

    def _cerca_nella_rete(self, voce, dati):
        """I computer della rete, o le cartelle condivise di un computer: la
        ricerca va in disparte, e intanto il ramo mostra una voce d'attesa."""
        computer = dati["tipo"] == "computer_della_rete"
        self.albero.AppendItem(voce, "Cerco i computer della rete..." if computer else "Cerco le cartelle condivise...", data={"tipo": "attesa"})
        testo = "Cerco i computer della rete: può volerci qualche secondo." if computer else f"Cerco le cartelle condivise di {dati['nome']}."
        if self._freccia_nell_albero:
            # Il ramo aperto con la freccia suona dopo questo gestore: la
            # ricerca suona finito lui.
            self.scrivi(testo)
            wx.CallAfter(self._dopo_il_suono, self._suono, "ricerca_avviata")
        else:
            self._riscontro("ricerca_avviata", testo)
        lavoro = questa_rete.computer if computer else (lambda: questa_rete.condivisioni(dati["percorso"]))
        questa_rete.in_disparte(lavoro, lambda trovati: wx.CallAfter(self._trovati_nella_rete, dati, trovati))

    def _trovati_nella_rete(self, dati, trovati):
        """Il risultato di una ricerca nella rete, se il suo ramo c'e' ancora."""
        if self._chiusa:
            return
        voce = next((v for v in self._tutte_le_voci(self.nodo_rete) if self._dati(v) is dati), None)
        if voce is None:
            return
        self.albero.DeleteChildren(voce)
        computer = dati["tipo"] == "computer_della_rete"
        for nome, percorso in trovati:
            if computer:
                figlio = self.albero.AppendItem(voce, nome, data={"tipo": "computer", "nome": nome, "percorso": percorso, "caricato": False})
                self.albero.SetItemHasChildren(figlio, True)
            else:
                self._voce_di_rete(voce, nome, percorso)
        if not trovati:
            self.albero.SetItemHasChildren(voce, False)
            dati["caricato"] = False
            self._riscontro("non_disponibile", "Nella rete non ho trovato computer." if computer else f"{dati['nome']} non mostra cartelle condivise.")
            return
        quanti = len(trovati)
        if computer:
            testo = "Trovato 1 computer nella rete." if quanti == 1 else f"Trovati {quanti} computer nella rete."
        else:
            testo = f"{dati['nome']}: 1 cartella condivisa." if quanti == 1 else f"{dati['nome']}: {quanti} cartelle condivise."
        self._riscontro("ricerca_finita", testo)

    def _comando_aggiungi_percorso_di_rete(self):
        """Chiede un percorso di rete, lo ricorda e lo mette in Questa rete,
        anche se adesso non risponde."""
        self._domanda()
        with DialogoTesto(self, "Il percorso di rete da aggiungere a Questa rete, per esempio \\\\server\\cartella.", "Aggiungi un percorso di rete") as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Nessun percorso aggiunto.")
                return
            testo = dialogo.GetValue()
        percorso = testo.strip().replace("/", "\\").rstrip("\\")
        parti = percorso[2:].split("\\") if questa_rete.e_di_rete(percorso) else []
        if len(parti) < 2 or not all(parti):
            self._riscontro("errore", f"{testo.strip()} non è un percorso di rete: si scrive come \\\\server\\cartella.")
            return
        presenti = [p.casefold() for p in self.impostazioni["percorsi_di_rete"]] + [p.casefold() for _n, p in questa_rete.percorsi_salvati()]
        if percorso.casefold() in presenti:
            self._riscontro("non_disponibile", f"{percorso} è già in Questa rete.")
            return
        self.impostazioni["percorsi_di_rete"].append(percorso)
        self._salva_impostazioni()
        self._ricarica_la_rete(percorso)
        avviso = "" if questa_rete.raggiungibile(percorso) else " Adesso non risponde, ma lo tengo."
        self._riscontro("percorso_aggiunto", f"Aggiunto a Questa rete {percorso}.{avviso}")

    def _togli_percorso_di_rete(self, percorso):
        """Toglie un percorso scritto a mano: dalle impostazioni e dalla
        plancia. I file restano dove sono."""
        self.impostazioni["percorsi_di_rete"] = [p for p in self.impostazioni["percorsi_di_rete"] if p != percorso]
        self._salva_impostazioni()
        voce = next((v for v in self._figli(self.nodo_rete) if (self._dati(v) or {}).get("percorso") == percorso), None)
        if voce is not None:
            self._togli_dalla_plancia({voce})
        self._riscontro("percorso_tolto", f"Tolto da Questa rete {percorso}. I file restano dove sono.")

    def _ricarica_la_rete(self, da_selezionare=None):
        """Rifa' i figli di Questa rete se e' gia' stata aperta, e porta la
        selezione sul percorso dato."""
        dati = self._dati(self.nodo_rete)
        if not dati.get("caricato"):
            return
        aperta = self.albero.IsExpanded(self.nodo_rete)
        self.albero.DeleteChildren(self.nodo_rete)
        self._riempi_la_rete(self.nodo_rete)
        if aperta:
            self.albero.Expand(self.nodo_rete)
        voce = next((v for v in self._figli(self.nodo_rete) if (self._dati(v) or {}).get("percorso") == da_selezionare), None)
        if voce is not None and aperta:
            self._seleziona(voce)

    def _aggiorna_cartella(self, cartella):
        """Aggiorna dal menu: la voce si cerca quando la si sceglie, perche'
        mentre il menu e' aperto una cartella vuota puo' sparire."""
        radice = self.nodo_rete if questa_rete.e_di_rete(cartella) else self.nodo_pc
        voce = next((v for v in self._tutte_le_voci(radice) if (self._dati(v) or {}).get("percorso") == cartella), None)
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
        self._riscontro("ramo_aggiornato", f"Aggiornato {self._nome_della_voce(voce)}.")

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
            self._altri_risultati(dati)
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
        selezione = len(self._voci_selezionate()) > 1
        voci = self._voci_del_menu_della_selezione() if selezione else self._voci_del_menu(dati)
        if not voci:
            # Spazio, Applicazioni o Invio non restano muti (tappa 9).
            if selezione:
                testo = "La selezione non ha un menu."
            elif dati.get("tipo") == "comando":
                testo = f"{self.albero.GetItemText(voce)} non ha un menu: Invio lo esegue."
            elif dati.get("tipo") == "attesa":
                testo = "Ricerca in corso: la voce sparisce quando finisce."
            else:
                testo = f"{self.albero.GetItemText(voce)} non ha un menu."
            self._riscontro("non_disponibile", testo)
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
            if azione is None:
                # Si legge ma non si sceglie, come un tag che non e' testo.
                menu.Append(wx.ID_ANY, etichetta).Enable(False)
            elif isinstance(azione, list):
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
        # I dettagli della voce del menu, anche se intanto il fuoco si sposta.
        dettagli_della_voce = ("Leggi i dettagli", lambda: self._leggi_i_dettagli(dati))
        if tipo == "radice_playlist":
            return [("Nuova playlist", self._comando_nuova_playlist), dettagli_della_voce]
        if tipo == "risultati":
            return [("Riproduci", lambda: self._riproduci_playlist(self.risultati)), ("Salva come playlist", self._salva_risultati),
                ("Nuova ricerca", self._ricerca_globale), ("Ferma la ricerca", self._ferma_ricerca), dettagli_della_voce]
        if tipo == "altri":
            return [("Mostra altri risultati", lambda: self._altri_risultati(dati))]
        if tipo == "gruppo_risultati":
            gruppo = dati["gruppo"]
            return [("Salva come playlist", lambda: self._salva_risultati(gruppo)), dettagli_della_voce]
        if tipo == "playlist":
            pl = dati["playlist"]
            voci = [("Riproduci", lambda: self._riproduci_playlist(pl)), ("Filtro", lambda: self._modifica_filtro(pl))]
            if pl.filtro:
                voci.append(("Togli il filtro", lambda: self._imposta_filtro(pl, "")))
            if pl is not self.archivio.preferiti:
                voci += [("Rinomina", lambda: self._rinomina(pl)), ("Elimina", lambda: self._elimina_playlist(pl))]
            return [*voci, dettagli_della_voce]
        if tipo == "brano":
            pl, brano = dati["playlist"], dati["brano"]
            return [("Riproduci", lambda: self._riproduci(pl, brano)),
                ("Sposta su", lambda: self._sposta(pl, brano, "su")), ("Sposta giù", lambda: self._sposta(pl, brano, "giu")),
                ("Sposta in cima", lambda: self._sposta(pl, brano, "cima")), ("Sposta in fondo", lambda: self._sposta(pl, brano, "fondo")),
                ("Saltato", (lambda: self._salta(pl, brano), brano.saltato)), ("Togli dalla playlist", lambda: self._togli(pl, brano)),
                ("Aggiungi ai preferiti", lambda: self._ai_preferiti(brano)), ("Rinomina file", lambda: self._rinomina_file(brano)),
                *self._voci_dei_tag([brano.percorso]), ("Manda nel cestino", lambda: self._al_cestino(self._voce_di_lavoro()))]
        if tipo == "pc":
            return [("Aggiorna", lambda: self._aggiorna_ramo(self.nodo_pc)), dettagli_della_voce]
        if tipo == "rete":
            return [("Aggiungi un percorso di rete", self._comando_aggiungi_percorso_di_rete), ("Aggiorna", lambda: self._aggiorna_ramo(self.nodo_rete))]
        if tipo in ("computer_della_rete", "computer"):
            voce = self._voce_di_lavoro()
            return [("Cerca di nuovo" if tipo == "computer_della_rete" else "Aggiorna", lambda: self._aggiorna_ramo(voce))]
        if tipo in ("unita", "cartella"):
            cartella = dati["percorso"]
            nome = dati.get("etichetta", "").split("\\", 1)[-1] if tipo == "unita" else dati.get("nome") or os.path.basename(cartella)
            voci = [("Riproduci", lambda: self._riproduci_cartella(cartella)), ("Crea playlist da qui", lambda: self._crea_da_qui(cartella, nome)),
                ("Aggiungi alla playlist", self._menu_aggiungi(lambda: [Brano(p) for p in questo_pc.file_ricorsivi(cartella)])),
                ("Aggiorna", lambda: self._aggiorna_cartella(cartella))]
            if dati.get("a_mano"):
                voci.append(("Togli il percorso", lambda: self._togli_percorso_di_rete(cartella)))
            return [*voci, dettagli_della_voce]
        if tipo == "file":
            pl, brano = dati["playlist"], dati["brano"]
            return [("Riproduci", lambda: self._riproduci(pl, brano)), ("Aggiungi alla playlist", self._menu_aggiungi(lambda: [Brano(brano.percorso)])),
                ("Aggiungi ai preferiti", lambda: self._ai_preferiti(brano)), ("Rinomina file", lambda: self._rinomina_file(brano)),
                *self._voci_dei_tag([brano.percorso]), ("Manda nel cestino", lambda: self._al_cestino(self._voce_di_lavoro()))]
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
        """Una domanda con Si' e No, e No come risposta predefinita; Esc vale
        No. Da un dialogo, il genitore e' lui: chiudendosi, la domanda gli
        rende il fuoco."""
        self._domanda()
        with DialogoConferma(genitore or self, domanda, titolo) as dialogo:
            return dialogo.ShowModal() == wx.ID_YES

    def _rinomina_file(self, brano):
        """Rinomina file, dal menu di un brano o di un file: cambia il nome del
        file sul disco, e l'estensione resta. I file accanto con lo stesso
        nome, come i sottotitoli, cambiano con lui; playlist, Preferiti,
        cartelle aperte, marker e schedario seguono il nome nuovo. Un audio o
        un video che suona si ferma un istante e riparte dal suo punto
        (Gabriele, 3 ottobre 2026, 1.67.0)."""
        vecchio = brano.percorso
        if not os.path.isfile(vecchio):
            self._riscontro("errore", f"Non trovo {vecchio} sul disco.")
            return
        cartella, nome_del_file = os.path.split(vecchio)
        nome, estensione = os.path.splitext(nome_del_file)
        resta = f" L'estensione {estensione} resta." if estensione else ""
        self._domanda()
        with DialogoTesto(self, f"Nuovo nome del file {nome_del_file}.{resta}", "Rinomina file", nome) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Nome del file non cambiato.")
                return
            # Windows toglie da se' punti e spazi in fondo al nome.
            scritto = dialogo.GetValue().strip().rstrip(". ")
        if estensione and scritto.casefold().endswith(estensione.casefold()):
            # L'estensione scritta per abitudine non si raddoppia.
            scritto = scritto[:-len(estensione)].rstrip(". ")
        if not scritto or scritto == nome:
            self._annullato("Nome del file non cambiato.")
            return
        problema = questo_pc.nome_non_valido(scritto)
        if problema:
            self._riscontro("errore", f"{problema} Il nome resta {nome_del_file}.")
            return
        nuovo = os.path.join(cartella, scritto + estensione)
        compagni = [(p, os.path.join(cartella, scritto + coda)) for p, coda in questo_pc.file_compagni(vecchio, m3u=formati.e_chip(vecchio))]
        occupati = [os.path.basename(d) for o, d in ((vecchio, nuovo), *compagni) if os.path.exists(d) and os.path.normcase(d) != os.path.normcase(o)]
        if occupati:
            self._riscontro("errore", f"In {cartella} c'è già {', '.join(occupati)}: il nome resta {nome_del_file}.")
            return
        # Le durate con cui il file si riconosce per i marker, prima che cambi nome.
        if formati.ha_sottobrani(vecchio):
            durate = [d for d in (sottobrani.durate(vecchio) or []) if d]
        else:
            durate = [self._durata_dei_marker(vecchio)[0]]
        try:
            ripresa = self._rinomina_sul_disco(vecchio, nuovo)
        except OSError as e:
            self._riscontro("errore", f"Non riesco a rinominare {nome_del_file}: {e.strerror or e}.")
            return
        rinominati, falliti = [], []
        for o, d in compagni:
            try:
                os.rename(o, d)
                rinominati.append(os.path.basename(d))
            except OSError:
                falliti.append(os.path.basename(o))
        self._segui_la_rinomina(vecchio, nuovo, durate)
        if ripresa is not None:
            posizione, in_pausa, sottobrano = ripresa
            self.motore.suona(nuovo, sottobrano, inizio=posizione, in_pausa=in_pausa)
            self._aggiorna_etichette()
        testo = f"{nome_del_file} ora si chiama {scritto + estensione}."
        if rinominati:
            testo += f" Con lui anche {', '.join(rinominati)}."
        if falliti:
            testo += f" Non ho potuto rinominare {', '.join(falliti)}."
        self._riscontro("file_rinominato", testo)

    def _rinomina_sul_disco(self, vecchio, nuovo):
        """Cambia il nome del file. Se il motore lo tiene aperto, cioe' un
        audio o un video che suona o che e' pronto a entrare, prima lo
        lascia: torna allora (posizione, pausa, sottobrano) del brano
        fermato, da far ripartire con il nome nuovo, o None. Se non riesce
        solleva OSError, dopo aver fatto ripartire il brano con il nome di
        prima."""
        try:
            os.rename(vecchio, nuovo)
        except PermissionError:
            pass
        else:
            # Un SID, un MIDI o un brano delle console suonano dalla memoria.
            self.motore.rinomina_il_file(vecchio, nuovo)
            return None
        ripresa = self._lascia_il_file(vecchio)
        # mpv chiude il file nel suo filo: si riprova per qualche istante.
        fine = time.monotonic() + 3
        while True:
            try:
                os.rename(vecchio, nuovo)
                return ripresa
            except PermissionError:
                if time.monotonic() >= fine:
                    if ripresa is not None:
                        self.motore.suona(vecchio, ripresa[2], inizio=ripresa[0], in_pausa=ripresa[1])
                    raise
                time.sleep(0.05)

    def _lascia_il_file(self, percorso):
        """Il motore lascia il file, per rinominarlo o scriverci: il seguente
        preparato con quel file si scarta, il brano in corso si ferma. Torna
        (posizione, pausa, sottobrano) del brano fermato, da far ripartire,
        o None se il file non suonava."""
        stesso = os.path.normcase(percorso)
        ripresa = None
        if self.motore.in_corso and os.path.normcase(self.motore.in_corso) == stesso:
            ripresa = (self.motore.posizione or 0.0, self.motore.in_pausa, self.motore.sottobrano if self.motore.sottobrani else None)
            self._uscente = self._preparato = None
        elif self._preparato is not None and os.path.normcase(self._preparato[1].percorso) == stesso:
            self._preparato = None
        self.motore.lascia_il_file(percorso)
        return ripresa

    def _segui_la_rinomina(self, vecchio, nuovo, durate):
        """Dopo Rinomina file: playlist, Preferiti, Risultati, cartelle aperte
        nella plancia, schedario e marker passano al nome nuovo."""
        stesso = os.path.normcase(vecchio)
        liste = [*self.archivio.playlist, self.archivio.preferiti, self.risultati, self.coda.playlist]
        liste += [dati["playlist"] for dati in (self._dati(v) for v in self._tutte_le_voci()) if dati and dati.get("playlist") is not None]
        for pl in {id(p): p for p in liste if p is not None}.values():
            for brano in pl.brani:
                if os.path.normcase(brano.percorso) == stesso:
                    brano.percorso = nuovo
        self.schedario.rinomina(vecchio, nuovo)
        chiavi = self.marcatori.rinomina_file(vecchio, nuovo, durate)
        self._salva_archivio()
        if chiavi:
            self._salva_i_marker(*chiavi)
        self._popola_playlist()
        self._aggiorna_etichette()

    # I tag, tappa 10 (1.69.0): F11 li legge nella console; il sottomenu Tag
    # del menu, o Maiuscolo+F11, li modifica uno alla volta, anche su piu'
    # file insieme (Gabriele, 3 ottobre 2026).

    def _file_dei_tag(self):
        """I file dei brani selezionati, o della voce di lavoro, di cui MeTeOra
        sa scrivere i tag, senza doppioni: un ramo selezionato vale per i
        suoi brani."""
        if len(self._voci_selezionate()) > 1:
            percorsi = [brano.percorso for _pl, brano, _sottobrano in self._brani_della_selezione()]
        else:
            dati = self._dati(self._voce_di_lavoro()) or {}
            percorsi = [dati["brano"].percorso] if dati.get("tipo") in ("brano", "file") else []
        return list({os.path.normcase(p): p for p in percorsi if tag.modificabile(p)}.values())

    def _di_chi(self, percorsi):
        return os.path.basename(percorsi[0]) if len(percorsi) == 1 else f"{len(percorsi)} file"

    def _voci_dei_tag(self, percorsi):
        """Le voci Leggi i tag e Tag del menu, per i file di cui MeTeOra sa
        scrivere i tag; nessuna per gli altri."""
        percorsi = [p for p in percorsi if tag.modificabile(p)]
        if not percorsi:
            return []
        return [("Leggi i tag", lambda: self._leggi_i_tag(percorsi)), ("Tag", self._sottomenu_dei_tag(percorsi))]

    def _sottomenu_dei_tag(self, percorsi):
        """Il sottomenu Tag: una voce per tag, "Titolo: Love Song", che con
        Invio chiede il valore nuovo; i tag che non sono testo, come le
        copertine, si leggono ma non si scelgono."""
        with wx.BusyCursor():
            letti, errori = tag.leggi_insieme(percorsi)
        if not letti:
            return [((errori or ["I tag non si leggono."])[0].replace("&", "&&"), None)]
        voci = []
        for t in letti:
            valore = "valori diversi" if t.get("diversi") else t["valore"] or "vuoto"
            if len(valore) > 80:
                valore = valore[:80].rstrip() + "..."
            etichetta = f"{t['nome']}: {valore}".replace("&", "&&")
            voci.append((etichetta, (lambda t=t: self._cambia_tag(percorsi, t)) if t["testo"] else None))
        return voci

    def _comando_leggi_i_tag(self):
        """F11: i tag del brano selezionato, o dei file selezionati, nella
        console; su un contenitore, i suoi dettagli (1.77.0)."""
        if len(self._voci_selezionate()) <= 1:
            dati = self._dati(self._voce_di_lavoro()) or {}
            if dati.get("tipo") in TIPI_CON_I_DETTAGLI:
                self._leggi_i_dettagli(dati)
                return
        # I dettagli chiesti prima, se arrivano, non portano via il fuoco ai tag.
        self._dettagli_attesi = None
        with wx.BusyCursor():
            percorsi = self._file_dei_tag()
        if not percorsi:
            self._riscontro("non_disponibile", "F11 legge i tag di un brano o di un file audio o video, e i dettagli di una cartella, di un'unità o di una playlist: scegline uno nella plancia. "
                "I SID, i MIDI, i tracker e MKV non hanno tag che MeTeOra sappia leggere.")
            return
        if self._troppi_per_i_tag(percorsi):
            return
        self._leggi_i_tag(percorsi)

    # I dettagli dei contenitori (Gabriele, 4 ottobre 2026, 1.77.0).

    def _in_disparte(self, lavoro, al_termine):
        """lavoro() in un filo a parte, e al_termine(esito) nel filo della
        finestra; le prove lo sostituiscono per fare tutto subito. Un guasto
        del lavoro arriva ad al_termine come riga della console, e poi risale
        come problema interno, invece di lasciare chi aspetta nel silenzio."""

        def fai():
            try:
                esito = lavoro()
            except Exception as errore:
                wx.CallAfter(al_termine, [f"Non riesco a raccogliere i dettagli: {errore}"])
                raise
            wx.CallAfter(al_termine, esito)

        threading.Thread(target=fai, name="MeTeOra, dettagli", daemon=True).start()

    def _durata_del_percorso(self, percorso):
        return (self.schedario.scheda(percorso) or {}).get("durata")

    def _nome_del_contenitore(self, dati):
        """Il nome di un contenitore per le frasi della console, dai suoi dati."""
        tipo = dati.get("tipo")
        if tipo == "cartella":
            return dati.get("nome") or os.path.basename(dati["percorso"].rstrip("\\")) or dati["percorso"]
        if tipo == "unita":
            return dati.get("etichetta") or dati["percorso"]
        if tipo == "playlist":
            return "i Preferiti" if dati["playlist"] is self.archivio.preferiti else f"la playlist {dati['playlist'].nome}"
        if tipo == "risultati":
            return "i Risultati"
        if tipo == "gruppo_risultati":
            return dati["gruppo"].nome
        return "Questo PC" if tipo == "pc" else "le playlist"

    def _leggi_i_dettagli(self, dati):
        """F11 su un contenitore, o Leggi i dettagli nel suo menu: tutti i
        dati che MeTeOra sa dare, nella console. Si raccolgono in un filo a
        parte, perche' una cartella grande o un'unita' si percorrono tutte; se
        ci vuole tempo, la console lo dice. Un altro F11 interrompe il conto
        di prima. dati sono quelli della voce, presi quando si e' chiesto: il
        fuoco, intanto, puo' spostarsi."""
        tipo = (dati or {}).get("tipo")
        if tipo not in TIPI_CON_I_DETTAGLI:
            self._riscontro("non_disponibile", "I dettagli ci sono per le cartelle, le unità, Questo PC e le playlist.")
            return
        segno = self._dettagli_attesi = object()

        def fermo():
            return segno is not self._dettagli_attesi or self._chiusa

        if tipo in ("cartella", "unita"):
            lavoro = lambda: self._dettagli_della_cartella(dati["percorso"], tipo == "unita", fermo)  # noqa: E731
        elif tipo == "pc":
            lavoro = self._dettagli_di_questo_pc
        elif tipo == "radice_playlist":
            elenco = [(pl, list(pl.brani)) for pl in self.archivio.playlist]
            lavoro = lambda: self._dettagli_delle_playlist(elenco, fermo)  # noqa: E731
        else:
            titolo, brani, pl = self._contenuto_da_descrivere(dati)
            lavoro = lambda: self._dettagli_dei_brani(titolo, brani, pl, fermo)  # noqa: E731
        nome = self._nome_del_contenitore(dati)

        def se_tarda():
            if segno is self._dettagli_attesi and not self._chiusa:
                self.scrivi(f"Raccolgo i dettagli di {nome}: ci vuole qualche secondo.")

        wx.CallLater(800, se_tarda)
        self._in_disparte(lavoro, lambda righe: self._dettagli_pronti(segno, dati, righe))

    def _dettagli_pronti(self, segno, dati, righe):
        """Le righe arrivate: se chi le ha chieste e' ancora li', sulla stessa
        voce della plancia, il fuoco va sulla prima riga come per i tag;
        altrimenti le righe si scrivono senza portare via il fuoco."""
        if segno is not self._dettagli_attesi or self._chiusa:
            return
        self._dettagli_attesi = None
        sul_posto = wx.Window.FindFocus() is self.albero and self._dati(self._voce_di_lavoro()) is dati
        self._stampa("dettagli", righe, porta_il_fuoco=sul_posto)

    def _contenuto_da_descrivere(self, dati):
        """(titolo, brani, playlist o None) di una playlist, dei Preferiti, dei Risultati o di un loro ramo."""
        tipo = dati["tipo"]
        if tipo == "playlist":
            pl = dati["playlist"]
            return ("Preferiti" if pl is self.archivio.preferiti else f"Playlist {pl.nome}"), list(pl.brani), pl
        if tipo == "risultati":
            return f"Risultati di {self._testo_della_ricerca}", list(self.risultati.brani), None
        gruppo = dati["gruppo"]
        return f"Ramo {gruppo.nome} dei Risultati", self._brani_del_gruppo(gruppo), None

    def _dettagli_della_cartella(self, percorso, e_un_unita, fermo):
        righe = []
        if e_un_unita:
            unita = dettagli.dati_dell_unita(percorso)
            righe = dettagli.righe_dell_unita(unita)
            if not unita["pronta"]:
                return righe
        if in_rete(percorso) and not questa_rete.raggiungibile(percorso):
            return [*righe, f"{percorso} non risponde: la rete o il disco sono spenti, o lontani."]
        censimento = dettagli.censisci(percorso, fermo)
        sconosciuti = [p for p in censimento["suonabili"] if self._durata_del_percorso(p) is None]
        if sconosciuti:
            # Le durate che mancano si leggono in sottofondo, per il prossimo F11.
            self.schedario.chiedi(sconosciuti)
        cartella = dettagli.righe_della_cartella(percorso, censimento, self._durata_del_percorso, durata_lunga)
        if e_un_unita:
            # La riga col percorso, le date e gli attributi della radice, che
            # e' sempre nascosta e di sistema, per un'unita' non servono.
            cartella = [r for r in cartella[1:] if not r.startswith(("Creata il ", "Attributi: "))]
        return righe + cartella

    def _dettagli_di_questo_pc(self):
        """Lo spazio di ogni unita', e in tutto quello dei dischi del PC:
        senza le unita' di rete, e contando una volta sola un volume che ha
        due lettere."""
        righe = []
        totale = libero = 0
        visti = set()
        unita = questo_pc.unita()
        for radice, nome in unita:
            d = dettagli.dati_dell_unita(radice)
            if not d["pronta"]:
                righe.append(f"{nome}: {d['tipo']}, non risponde o non ha un disco.")
                continue
            if d["tipo"] != dettagli.TIPI_DI_UNITA[4] and d["volume"] not in visti:
                visti.add(d["volume"])
                totale, libero = totale + d["totale"], libero + d["libero"]
            righe.append(f"{nome}: {d['tipo']}, liberi {dettagli.dimensione(d['libero'])} di {dettagli.dimensione(d['totale'])}, {dettagli.percentuale(d['libero'], d['totale'])} del totale.")
        testa = [f"Questo PC: {len(unita)} unità."]
        if totale:
            testa.append(f"Dischi del PC, in tutto: liberi {dettagli.dimensione(libero)} di {dettagli.dimensione(totale)}, {dettagli.percentuale(libero, totale)} del totale.")
        return testa + righe

    def _nome_del_brano(self, brano):
        return f"{brano.nome_del_file}, sottobrano {brano.sottobrano}" if brano.sottobrano else brano.nome_del_file

    def _dettagli_dei_brani(self, titolo, brani, pl=None, fermo=None):
        """Le righe di una playlist, dei Preferiti, dei Risultati o di un loro ramo."""
        righe = [f"{titolo}: {al_plurale(len(brani), 'brano', 'brani')}."]
        if not brani:
            return righe
        censimento = dettagli.censisci_brani([b.percorso for b in brani], fermo)
        righe.append(f"Sul disco: {dettagli.dimensione(censimento['byte'])}.")
        self.schedario.chiedi([b.percorso for b in brani if self.schedario.durata(b) is None])
        righe += dettagli.righe_dei_brani(brani, self.schedario.durata, durata_lunga, nome_di=self._nome_del_brano, percorso_di=lambda b: b.percorso)
        saltati = sum(1 for b in brani if b.saltato)
        if saltati:
            righe.append(f"Saltati: {saltati}.")
        mancanti = censimento["mancanti"]
        if mancanti:
            righe.append(f"Mancanti sul disco: {len(mancanti)}; il primo è {mancanti[0]}.")
        if censimento["lontani"]:
            righe.append(f"In rete, senza risposta: {censimento['lontani']} file, che i conti non comprendono.")
        if censimento["interrotto"]:
            righe.append("Conto interrotto: i numeri valgono per la parte letta.")
        if pl is not None and pl.filtro:
            passano = sum(1 for b in brani if self._ammesso(pl, b))
            righe.append(f"Filtro: {pl.filtro}; lo {'passa' if passano == 1 else 'passano'} {al_plurale(passano, 'brano', 'brani')}.")
        return righe

    def _dettagli_delle_playlist(self, elenco, fermo=None):
        """Il ramo Playlist: quante, quanti brani in tutto, e una riga per playlist."""
        tutti = [b for _pl, brani in elenco for b in brani]
        righe = [f"Playlist: {len(elenco)}, con {al_plurale(len(tutti), 'brano', 'brani')} in tutto."]
        if tutti:
            censimento = dettagli.censisci_brani([b.percorso for b in tutti], fermo)
            righe.append(f"Sul disco: {dettagli.dimensione(censimento['byte'])}.")
        for pl, brani in elenco:
            durate = [self.schedario.durata(b) for b in brani]
            note = [d for d in durate if d is not None]
            durata = f", {durata_lunga(sum(note))}" if note else ""
            righe.append(f"{pl.nome}: {al_plurale(len(brani), 'brano', 'brani')}{durata}.")
        return righe

    def _troppi_per_i_tag(self, percorsi):
        if len(percorsi) <= MASSIMO_DI_FILE_PER_I_TAG:
            return False
        self._riscontro("non_disponibile", f"I tag si leggono e si modificano al massimo su {MASSIMO_DI_FILE_PER_I_TAG} file insieme: la selezione ne ha {len(percorsi)}.")
        return True

    def _leggi_i_tag(self, percorsi):
        with wx.BusyCursor():
            letti, errori = tag.leggi_insieme(percorsi)
        if not letti:
            self._riscontro("errore", " ".join(errori))
            return
        righe = [f"Tag di {self._di_chi(percorsi)}."]
        righe += [f"{t['nome']}: {'valori diversi' if t.get('diversi') else t['valore'] or 'vuoto'}." for t in letti]
        self._stampa("tag_letti", righe + errori)

    def _comando_modifica_i_tag(self):
        """Maiuscolo+F11: il sottomenu Tag del brano selezionato, o dei file
        selezionati, aperto subito."""
        with wx.BusyCursor():
            percorsi = self._file_dei_tag()
        if not percorsi:
            self._riscontro("non_disponibile", "Maiuscolo+F11 modifica i tag di un brano o di un file audio o video: scegline uno nella plancia.")
            return
        if self._troppi_per_i_tag(percorsi):
            return
        menu = wx.Menu()
        self._riempi_menu(menu, self._sottomenu_dei_tag(percorsi))
        self._suono("menu")
        voce = self._voce_di_lavoro()
        rettangolo = self.albero.GetBoundingRect(voce, textOnly=True) if voce.IsOk() else None
        self.albero.PopupMenu(menu, rettangolo.GetBottomLeft() if rettangolo else wx.DefaultPosition)
        menu.Destroy()

    def _cambia_tag(self, percorsi, t):
        """Chiede il valore nuovo del tag e lo scrive in tutti i file; un
        campo vuoto lo cancella. Un brano che suona si ferma un istante e
        riparte dal suo punto: mpv legge il file mentre mutagen lo riscrive."""
        nome, chi = t["nome"], self._di_chi(percorsi)
        diversi = " I file hanno valori diversi: quello che scrivi va in tutti." if t.get("diversi") else ""
        self._domanda()
        with DialogoTesto(self, f"{nome} di {chi}. Un campo vuoto cancella il tag.{diversi}", f"Tag {nome}", t["valore"]) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(f"Tag {nome} non cambiato.")
                return
            scritto = dialogo.GetValue()
        if not t.get("diversi") and tag.pulito(scritto) == t["valore"]:
            # Un valore lasciato com'era non si controlla: un anno con l'ora,
            # o una traccia come A1, restano dove sono.
            self._annullato(f"Tag {nome} non cambiato.")
            return
        try:
            valore = tag.controlla(t["chiave"], scritto)
        except tag.ErroreTag as e:
            self._riscontro("errore", f"{e} Il tag {nome} resta com'era.")
            return
        if not valore and t.get("diversi") and len(percorsi) > 1 and not self._conferma(
                f"Cancellare il tag {nome} da {len(percorsi)} file? Hanno valori diversi, che si perdono.", f"Tag {nome}"):
            # Il campo dei valori diversi parte vuoto: un Invio distratto non
            # deve cancellare il tag da tutti.
            self._annullato(f"Tag {nome} non cambiato.")
            return
        scritti, errori = 0, []
        for percorso in percorsi:
            ripresa = self._lascia_il_file(percorso)
            try:
                tag.scrivi(percorso, t["chiave"], valore)
                scritti += 1
            except tag.ErroreTag as e:
                errori.append(str(e))
            finally:
                if ripresa is not None:
                    posizione, in_pausa, sottobrano = ripresa
                    self.motore.suona(percorso, sottobrano, inizio=posizione, in_pausa=in_pausa)
            # Lo schedario rilegge i tag, per il filtro e la ricerca.
            self.schedario.leggi_subito(percorso)
        if not scritti:
            self._riscontro("errore", " ".join(errori))
            return
        chi = self._di_chi(percorsi) if scritti == len(percorsi) else f"{scritti} file su {len(percorsi)}"
        testo = f"{nome} di {chi}: {valore}." if valore else f"Tag {nome} cancellato da {chi}."
        self._riscontro("tag_cambiato" if valore else "tag_cancellato", " ".join([testo, *errori]))
        self._aggiorna_etichette()

    def _al_cestino(self, voce):
        """Maiuscolo+Canc: il file del brano va nel cestino di Windows, e il
        brano esce dalla playlist o dalla cartella in cui sta. Su una
        cartella vuota, la cartella (1.76.0)."""
        dati = self._dati(voce) or {}
        tipo = dati.get("tipo")
        if tipo == "cartella":
            self._cartella_al_cestino(voce, dati)
            return
        if tipo == "sottobrano":
            self._riscontro("non_disponibile", "Un sottobrano non si cestina da solo: Maiuscolo+Canc si usa sul file che lo contiene.")
            return
        if tipo not in ("brano", "file"):
            self._riscontro("non_disponibile", "Maiuscolo+Canc manda nel cestino un file, da una playlist o da una cartella, o una cartella vuota.")
            return
        pl, brano = dati["playlist"], dati["brano"]
        dove = "" if pl.temporanea else f" Si toglie anche dalla playlist {pl.nome}."
        cestino = questo_pc.ha_il_cestino(brano.percorso)
        domanda = f"Mandare nel cestino di Windows il file {brano.percorso}?" if cestino else f"Cancellare per sempre il file {brano.percorso}? Lì il cestino di Windows non c'è."
        if not self._conferma(domanda + dove, "Manda nel cestino" if cestino else "Cancella per sempre"):
            self._annullato("Il file resta dov'è.")
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
        self._riconta(os.path.dirname(brano.percorso))
        self._riscontro("cestino", f"{brano.nome_del_file} è nel cestino di Windows." if cestino else f"{brano.nome_del_file} è cancellato per sempre.")

    def _cartella_al_cestino(self, voce, dati):
        """Maiuscolo+Canc su una cartella (Gabriele, 4 ottobre 2026): va nel
        cestino solo se e' vuota, cioe' senza file nemmeno nelle
        sottocartelle, a parte quelli di servizio come desktop.ini; con dei
        file dentro, anche che MeTeOra non suona, resta. Le cartelle prime di
        Questa rete e di un computer sono condivisioni, e non si toccano."""
        percorso = dati["percorso"]
        nome = self._nome_della_voce(voce)
        genitore = self.albero.GetItemParent(voce)
        if dati.get("a_mano") or (self._dati(genitore) or {}).get("tipo") in ("rete", "computer"):
            self._riscontro("non_disponibile", f"{nome} è un percorso di rete, non una cartella da cestinare.")
            return
        try:
            vuota = questo_pc.cartella_vuota(percorso)
        except OSError as e:
            self._riscontro("errore", f"Non riesco a leggere {nome}: {e.strerror or e}.")
            return
        if not vuota:
            self._riscontro("non_disponibile", f"{nome} non è vuota: ci sono dei file, anche se MeTeOra magari non li suona. Maiuscolo+Canc manda nel cestino solo le cartelle vuote.")
            return
        cestino = questo_pc.ha_il_cestino(percorso)
        domanda = f"Mandare nel cestino di Windows la cartella vuota {percorso}?" if cestino else f"Cancellare per sempre la cartella vuota {percorso}? Lì il cestino di Windows non c'è."
        if not self._conferma(domanda, "Manda nel cestino" if cestino else "Cancella per sempre"):
            self._annullato("La cartella resta dov'è.")
            return
        if not questo_pc.nel_cestino(percorso):
            self._riscontro("errore", f"Non riesco a mandare nel cestino {percorso}.")
            return
        vicina = self.albero.GetNextSibling(voce)
        if not vicina.IsOk():
            vicina = self.albero.GetPrevSibling(voce)
        self._seleziona(vicina if vicina.IsOk() else genitore)
        self.albero.Delete(voce)
        self.contatore.dimentica(percorso, anche_sopra=False)
        self._riconta(os.path.dirname(percorso.rstrip("\\")))
        self._riscontro("cestino", f"La cartella {nome} è nel cestino di Windows." if cestino else f"La cartella {nome} è cancellata per sempre.")

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
        elif dati.get("a_mano"):
            self._togli_percorso_di_rete(dati["percorso"])
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
            ("Togli dalle playlist, ed elimina le playlist e i marker selezionati", self._cancella_selezione), ("Manda nel cestino", self._cestina_selezione),
            # I file e i loro tag si leggono solo alla scelta: aprire il menu
            # di una selezione con un'unita' intera non deve fermare tutto.
            ("Leggi i tag", self._comando_leggi_i_tag), ("Modifica i tag", self._comando_modifica_i_tag)]

    def _crea_dalla_selezione(self):
        brani = self._copie_della_selezione()
        if not brani:
            self._riscontro("niente_da_suonare", "Nella selezione non c'è niente da mettere in una playlist.")
            return
        self._domanda()
        with DialogoTesto(self, "Nome della nuova playlist:", "Crea playlist dalla selezione", "Selezione") as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Nessuna playlist creata.")
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
        altri = ("; 1 c'era già" if gia == 1 else f"; {gia} c'erano già") if gia else ""
        self._riscontro("preferito_aggiunto", f"{'Aggiunto' if len(nuovi) == 1 else 'Aggiunti'} ai Preferiti {brani_al_plurale(len(nuovi))}{altri}.")

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
            self._annullato("Eliminazione annullata.")
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
        evento = "brano_tolto" if da_togliere else "playlist_eliminata" if da_eliminare else "marker_eliminato"
        self._riscontro(evento, ", ".join(parti).capitalize() + ".")

    def _ricostruisci_dopo_la_cancellazione(self, approdo, voci_da_togliere=()):
        """Dopo una cancellazione: toglie dalla plancia le voci delle cartelle
        e dei Risultati, ricostruisce il ramo Playlist e rimette il fuoco
        sull'approdo, da solo nella selezione. Le voci delle playlist e dei
        Preferiti rinascono, e si ritrovano dal brano o dalla playlist che
        mostrano; le altre restano le stesse."""
        rinasce = approdo is not None and approdo not in (self.nodo_preferiti, self.nodo_playlist) and (
            self._sotto(approdo, self.nodo_preferiti) or self._sotto(approdo, self.nodo_playlist))
        oggetto = interno = None
        if rinasce:
            dati = self._dati(approdo) or {}
            oggetto = "nuova_playlist" if dati.get("comando") == "nuova_playlist" else (dati.get("brano") or dati.get("playlist"))
            interno = dict(dati)
        self.albero.UnselectAll()
        if approdo is not None and not rinasce:
            self._seleziona(approdo)
        for voce in voci_da_togliere:
            self.albero.Delete(voce)
        self._popola_playlist(seleziona=oggetto)
        self._ritrova_dentro(interno)
        if approdo is not None and not rinasce:
            self._seleziona(approdo)

    def _ritrova_dentro(self, interno):
        """Dopo una ricostruzione che ha ritrovato il brano: riporta il fuoco
        sul sottobrano o sul marker in cui stava; interno sono i dati di
        quella voce, e per le altre voci non si fa niente."""
        tipo = (interno or {}).get("tipo")
        if tipo == "sottobrano":
            self._al_sottobrano(interno["numero"])
            return
        if tipo != "marker":
            return
        voce = self._voce_corrente()
        dati = self._dati(voce) or {}
        if dati.get("tipo") == "brano" and dati["brano"].sottobrano is None and self._ha_sottobrani(dati["brano"]):
            # Il marker sta sotto un sottobrano del file.
            self._al_sottobrano(interno.get("numero"))
            voce = self._voce_corrente()
        if not voce.IsOk() or not self.albero.ItemHasChildren(voce):
            return
        self.albero.Expand(voce)
        tempo_del_marker = interno["marker"]["tempo"]
        figlio = next((v for v in self._figli(voce) if (self._dati(v) or {}).get("tipo") == "marker" and self._dati(v)["marker"]["tempo"] == tempo_del_marker), None)
        if figlio is not None:
            self._seleziona(figlio)

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
        senza_cestino = sum(1 for _v, _pl, brano in bersagli if not questo_pc.ha_il_cestino(brano.percorso))
        avviso = ""
        if senza_cestino:
            # In rete e sulle chiavette Windows cancella per sempre: lo si dice prima.
            avviso = f" {'1 sta' if senza_cestino == 1 else f'{senza_cestino} stanno'} dove il cestino non c'è, e si {'cancella' if senza_cestino == 1 else 'cancellano'} per sempre."
        if not self._conferma(f"Mandare nel cestino di Windows {len(bersagli)} file? I brani escono anche dalle loro playlist.{avviso}", "Manda nel cestino"):
            self._annullato("I file restano dove sono.")
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
        self._riconta(*{os.path.dirname(brano.percorso) for _v, _pl, brano in bersagli if not os.path.exists(brano.percorso)})
        if any(pl is self.risultati for _v, pl, _b in bersagli):
            self._aggiorna_risultati()
        testo = f"Nel cestino di Windows {riusciti} file." if not senza_cestino else f"Tolti {riusciti} file: quelli dove il cestino non c'è sono cancellati per sempre."
        if falliti:
            testo += " 1 non c'è andato." if falliti == 1 else f" {falliti} non ci sono andati."
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
        cosa = "Creata la playlist" if nuova else "Aggiunto alla playlist" if len(percorsi_da_aggiungere) == 1 else "Aggiunti alla playlist"
        self._riscontro("playlist_creata" if nuova else "brano_aggiunto", f"{cosa} {pl.nome}: {brani_al_plurale(len(percorsi_da_aggiungere))}, ora {brani_al_plurale(len(pl.brani))}.")

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
        altro punto nel ramo della plancia in cui si e' (Gabriele, 3 ottobre
        2026, 1.71.0). Ctrl con la barra rovesciata cerca in tutto MeTeOra."""
        if wx.Window.FindFocus() is self.console:
            self._comando_cerca_in_console()
            return
        ramo = self._ramo_della_ricerca()
        if ramo is None:
            self._riscontro("non_disponibile", "Qui non c'è niente in cui cercare: Ctrl con la barra rovesciata cerca in tutto MeTeOra.")
            return
        self._ricerca_globale(*ramo)

    def _ramo_della_ricerca(self):
        """Il ramo in cui cerca la barra rovesciata, dalla voce su cui si
        agisce: (dove, brani delle playlist, radici del disco), con dove come
        si legge nelle frasi, per esempio "in Amiga giochi". Una cartella o
        un'unita' con le sottocartelle, una playlist, i Preferiti, i Risultati
        o un loro ramo; Questo PC sono tutti i dischi, il ramo Playlist tutte
        le playlist, Questa rete i suoi percorsi. Un brano o un file valgono
        per la lista in cui stanno. Dalle voci di primo livello senza un
        contenuto, la ricerca in tutto MeTeOra. None se li' non c'e' niente."""
        voce = self._voce_di_lavoro()
        while voce.IsOk() and voce != self.albero.GetRootItem():
            dati = self._dati(voce) or {}
            tipo = dati.get("tipo")
            if tipo in ("cartella", "unita"):
                return f"in {self._nome_della_voce(voce)}", [], [dati["percorso"]]
            if tipo == "pc":
                return "in Questo PC", [], None
            if tipo == "radice_playlist":
                return "nelle playlist", [(b, f"Playlist {pl.nome}") for pl in self.archivio.playlist for b in pl.brani], []
            if tipo in ("risultati", "gruppo_risultati"):
                return "nei Risultati", [(b, None) for b in self._brani_del_gruppo(dati["gruppo"])], []
            if tipo == "rete":
                percorsi = self._percorsi_di_questa_rete()
                return ("in Questa rete", [], percorsi) if percorsi else None
            if tipo == "computer":
                percorsi = [d["percorso"] for d in (self._dati(v) for v in self._figli(voce)) if d.get("tipo") == "cartella"]
                return (f"in {dati['nome']}", [], percorsi) if percorsi else None
            if tipo in ("playlist", "brano", "file", "sottobrano", "marker"):
                pl = dati["playlist"]
                if pl is self.risultati:
                    voce = self.albero.GetItemParent(voce)
                    continue
                if pl is self.archivio.preferiti:
                    return "nei Preferiti", [(b, "Preferiti") for b in pl.brani], []
                if pl in self.archivio.playlist:
                    return f"nella playlist {pl.nome}", [(b, f"Playlist {pl.nome}") for b in pl.brani], []
                if pl.cartella:
                    # Il file di una cartella: la cartella, con le sue sottocartelle.
                    return f"in {os.path.basename(pl.cartella.rstrip(chr(92))) or pl.cartella}", [], [pl.cartella]
                return None
            voce = self.albero.GetItemParent(voce)
        return OVUNQUE, None, None

    def _percorsi_di_questa_rete(self, salvati=None):
        """I percorsi di Questa rete, anche a ramo chiuso: quelli salvati in
        Windows e quelli aggiunti a mano, senza doppioni e senza quelli che
        stanno dentro un altro."""
        if salvati is None:
            salvati = questa_rete.percorsi_salvati()
        return senza_annidati([p for _nome, p in salvati] + list(self.impostazioni["percorsi_di_rete"]))

    def _ricerca_globale(self, dove=OVUNQUE, brani=None, unita=None):
        """Il campo della ricerca, uguale a quello del filtro; con Invio parte
        la ricerca e i Risultati si riempiono mentre procede. Senza argomenti
        cerca in tutto MeTeOra; dove, brani e unita la limitano a un ramo."""
        testo = self._testo_della_ricerca
        titolo = "Ricerca in tutto MeTeOra" if dove == OVUNQUE else f"Ricerca {dove}"
        istruzioni = ISTRUZIONI_DELLA_RICERCA if dove == OVUNQUE else [f"Puoi usare questi comandi per comporre la ricerca, {dove}.", *_GRAMMATICA_DEL_FILTRO]
        while True:
            self._domanda()
            with FinestraFiltro(self, titolo, testo, istruzioni) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self._annullato("Ricerca annullata.")
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
        self._avvia_ricerca(testo, filtro, unita, brani, dove)

    def _avvia_ricerca(self, testo, filtro, unita=None, brani=None, dove=OVUNQUE):
        """brani sono le coppie (brano, nome della playlist) da guardare, di
        tutte le playlist e dei Preferiti se None; unita le radici del disco,
        di tutte le unita' se None, nessuna se vuota. La ricerca in tutto
        MeTeOra cerca per ultime le unita' di rete e i percorsi aggiunti a mano
        in Questa rete, non le condivisioni intere salvate in Windows: sul
        disco dell'Iliadbox, con decine di migliaia di cartelle di backup, il
        Samba si pianta dopo circa 17 mila (Gabriele, 4 ottobre 2026, 1.73.0)."""
        if self._ricerca is not None:
            self._ricerca.ferma()
        self._testo_della_ricerca = testo
        if brani is None:
            brani = [(b, "Preferiti") for b in self.archivio.preferiti.brani]
            brani += [(b, f"Playlist {pl.nome}") for pl in self.archivio.playlist for b in pl.brani]
        else:
            # I brani si prendono prima che i Risultati, se sono loro, si svuotino.
            brani = list(brani)
        self.risultati = Playlist("Risultati", cartella="")
        self._risultati_letti = 0
        self._dove_si_cerca = dove
        salvati = questa_rete.percorsi_salvati()
        ovunque = unita is None and dove == OVUNQUE
        # Le unita' di rete con la lettera le trova il filo della ricerca, perche' su un server fermo si fanno aspettare.
        self._ricerca = Ricerca(filtro, brani, self.schedario, avvisa=lambda: wx.CallAfter(self._risultati_arrivati), unita=unita,
            rete=list(self.impostazioni["percorsi_di_rete"]) if ovunque else (), lettere_di_rete=ovunque)
        # I rami dei risultati in rete prendono il nome che hanno in Questa rete.
        nomi = {percorso + "\\": nome for nome, percorso in salvati}
        self._albero_dei_risultati = AlberoDeiRisultati({**nomi, **dict(questo_pc.unita())})
        if self.nodo_risultati is None:
            self.nodo_risultati = self.albero.InsertItem(self.albero.GetRootItem(), self.nodo_preferiti, "Risultati")
        else:
            self.albero.Collapse(self.nodo_risultati)
            self.albero.DeleteChildren(self.nodo_risultati)
        self.albero.SetItemData(self.nodo_risultati, self._dati_del_gruppo("risultati", self._albero_dei_risultati.radice))
        self.albero.SetItemHasChildren(self.nodo_risultati, True)
        self._aggiorna_risultati()
        self._ricerca.avvia()
        self._riscontro("ricerca_avviata", f"Cerco {testo} {dove}. I Risultati si riempiono mentre cerco.")

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
        altri = figli[-1] if figli and (self._dati(figli[-1]) or {}).get("tipo") == "altri" else None
        da_mostrare = gruppo.brani[dati["brani"]:dati["pagina"]]
        if altri is not None and da_mostrare:
            # I brani nuovi vanno prima della voce, che torna in fondo. Succede
            # solo dopo Mostra altri risultati, che poi sceglie il primo.
            self.albero.Delete(altri)
            altri = None
        for sotto in gruppo.elenco_dei_gruppi[dati["rami"]:]:
            ramo = self.albero.InsertItem(voce, dati["rami"], self._etichetta_del_gruppo(sotto), data=self._dati_del_gruppo("gruppo_risultati", sotto))
            self.albero.SetItemHasChildren(ramo, True)
            dati["rami"] += 1
        for brano in da_mostrare:
            self._aggiungi_voce(voce, "file", self.risultati, brano)
            dati["brani"] += 1
        restano = len(gruppo.brani) - dati["brani"]
        if restano > 0:
            testo = "Mostra l'ultimo risultato" if restano == 1 else f"Mostra altri {min(restano, PAGINA_DEI_RISULTATI)} risultati, ne restano {restano}"
            if altri is None:
                self.albero.AppendItem(voce, testo, data={"tipo": "altri", "ramo": voce})
            elif self.albero.GetItemText(altri) != testo:
                # Mentre la ricerca va avanti la voce cambia il testo e resta
                # dov'e': cancellarla sposterebbe il fuoco di chi ci sta sopra
                # (tappa 9).
                self.albero.SetItemText(altri, testo)
        elif altri is not None:
            fuoco = altri == self._voce_corrente()
            self.albero.Delete(altri)
            figli = list(self._figli(voce))
            if fuoco and figli:
                self._seleziona(figli[-1])

    def _altri_risultati(self, altri=None):
        """La voce Mostra altri risultati; altri sono i suoi dati, quelli
        della voce su cui si agisce, o di quella di lavoro."""
        if altri is None:
            altri = self._dati(self._voce_di_lavoro()) or {}
        ramo = altri.get("ramo")
        if ramo is None:
            self._riscontro("non_disponibile", "Mostra altri risultati si usa sulla sua voce, in fondo a un ramo dei Risultati.")
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
            dove = "" if self._dove_si_cerca == OVUNQUE else f" {self._dove_si_cerca}"
            muti = self._ricerca.senza_risposta
            # Le radici di rete che non hanno risposto, con il nome di Questa rete se ce l'hanno.
            nomi = {os.path.normcase(p): n for n, p in questa_rete.percorsi_salvati()} if muti else {}
            silenzio = f" In rete non {'ha' if len(muti) == 1 else 'hanno'} risposto: {', '.join(nomi.get(os.path.normcase(p), p) for p in muti)}." if muti else ""
            saltate = len(self._ricerca.cartelle_mute)
            if saltate:
                silenzio += f" In rete {'una cartella non ha' if saltate == 1 else f'{saltate} cartelle non hanno'} risposto, e la ricerca è andata avanti senza."
            self._riscontro("ricerca_finita", f"Ricerca di {self._testo_della_ricerca}{dove} finita: {al_plurale(len(self.risultati.brani), 'risultato', 'risultati')}.{silenzio}")
            # Lo schedario legge senza tempo massimo: i file delle radici che
            # non hanno risposto lo terrebbero fermo.
            mute = tuple(os.path.normcase(p).rstrip("\\") + "\\" for p in muti)
            self.schedario.chiedi([b.percorso for b in self.risultati.brani if not os.path.normcase(b.percorso).startswith(mute)])

    def _ferma_ricerca(self):
        if self._ricerca is None or self._ricerca.finita or self._ricerca.fermata:
            self._riscontro("non_disponibile", "Non c'è una ricerca in corso.")
            return
        self._ricerca.ferma()
        self._aggiorna_risultati()
        self._riscontro("ricerca_fermata", f"Ricerca fermata: {al_plurale(len(self.risultati.brani), 'risultato', 'risultati')}.")

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
        self._domanda()
        with DialogoTesto(self, "Nome della nuova playlist:", "Salva i risultati", proposta) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Risultati non salvati.")
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
        self._riscontro("playlist_creata", f"Creata la playlist {pl.nome} con {brani_al_plurale(len(files))}.")

    def _rinomina(self, pl):
        self._domanda()
        with DialogoTesto(self, "Nuovo nome della playlist:", "Rinomina", pl.nome) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Nome della playlist non cambiato.")
                return
            nome = dialogo.GetValue().strip()
        if not nome or nome == pl.nome:
            self._annullato("Nome della playlist non cambiato.")
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
            self._annullato("Eliminazione annullata.")
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
        if formati.e_midi(brano.percorso) and not self._midi_pronti():
            self._prepara_i_midi(lambda: self._suona(pl, brano, evento, sottobrano, inizio, sfuma_lo_stesso))
            return
        self._uscente = self._preparato = self._avanzamento_dopo_errore = None
        self.coda.imposta(pl, brano)
        self._segna_nel_mazzo(pl, brano, sottobrano)
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
        self._video_nascosto_per = self._video_in_attesa = None
        self._aggiorna_il_video()

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
        """Apre in Questo PC, o in Questa rete per le cartelle di rete, i rami
        fino alla cartella e ne restituisce la voce; None se non la trova."""
        voce = self.nodo_rete if questa_rete.e_di_rete(cartella) else self.nodo_pc
        self.albero.Expand(voce)
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
        self._mazzo_finito = False
        if self.impostazioni["casuale"]:
            # Dopo Z si ripercorre la storia, prima di scegliere a caso.
            avanti = self._dalla_storia(1)
            if avanti is not None:
                self._atteso_dalla_storia = avanti
                return avanti
            seguente = self._seguente_casuale(voce, sottobrano)
            if seguente is FINE_DEL_MAZZO:
                self._mazzo_finito = True
                return None
            if seguente is not None:
                return seguente
        if voce is not None:
            return self._passo_in_plancia(voce, 1)
        seguente = self.coda.successivo()
        return (self.coda.playlist, seguente, None) if seguente else None

    def _candidati_in_plancia(self, voce):
        """Le voci suonabili che si vedono nella plancia, tranne voce."""
        return [v for v in self._tutte_le_voci() if v != voce and self._visibile(v) and self._suonabile_in_plancia(v)]

    def _seguente_casuale(self, voce, sottobrano):
        """Con la riproduzione casuale accesa (issue 17), il seguente a caso
        nel campo dell'avanzamento automatico, diverso da cio' che suona: fra
        le voci suonabili che si vedono nella plancia, se a decidere e' la
        plancia; altrimenti nella lista, nel loop o nella selezione. None se
        non c'e' altro, e allora decide l'avanzamento in ordine, che nel loop
        sullo stesso brano lo fa ripetere.
        La scelta resta la stessa finche' suona lo stesso brano: con la
        dissolvenza il seguente si chiede due volte, per prepararlo e per
        ricontrollarlo al passaggio, e una seconda estrazione farebbe
        suonare un altro brano al posto di quello preparato. Si rifa' se il
        brano scelto non e' piu' fra quelli possibili."""
        if voce is not None:
            candidati = [(d["playlist"], d["brano"], d.get("numero")) for d in map(self._dati, self._candidati_in_plancia(voce))]
        else:
            candidati = [(self.coda.playlist, brano, None) for brano in self.coda.altri()]
        if not candidati:
            return None
        suona = (self.coda.playlist, self.coda.corrente, self.motore.sottobrano if sottobrano is None else sottobrano)
        ricordato = self._casuale_ricordato
        if ricordato is not None and _stesso_posto(ricordato[0], suona):
            scelto = next((c for c in candidati if _stesso_posto(c, ricordato[1])), None)
            if scelto is not None:
                return scelto
        modello = self.impostazioni["modello_casuale"]
        if modello != "totale":
            # Il mazzo: solo i brani non ancora usciti. Finito il mazzo ci si
            # ferma, o si rimescola, e il brano che suona conta gia' nel giro
            # nuovo, cosi' non torna subito.
            nel_mazzo = [c for c in candidati if (id(c[0]), id(c[1]), c[2]) not in self._mazzo]
            if not nel_mazzo:
                if modello == "una_volta":
                    return FINE_DEL_MAZZO
                self._mazzo.clear()
                self._mazzo_tenuti.clear()
                self._segna_nel_mazzo(*suona)
                nel_mazzo = candidati
            candidati = nel_mazzo
        scelto = self._a_caso(candidati)
        self._casuale_ricordato = (suona, scelto)
        return scelto

    # La scelta a caso, che le prove sostituiscono.
    _a_caso = staticmethod(random.choice)

    def _segna_nel_mazzo(self, pl, brano, numero):
        """Con la riproduzione casuale accesa, il brano che parte esce dal
        mazzo, anche se l'ha scelto chi ascolta: fino al giro nuovo non
        torna. Esce anche come brano intero, senza sottobrano: e' la voce di
        un SID con i sottobrani chiusi."""
        if not self.impostazioni["casuale"] or pl is None or brano is None:
            return
        self._mazzo.update({(id(pl), id(brano), numero), (id(pl), id(brano), None)})
        self._mazzo_tenuti.append((pl, brano))
        self._segna_nella_storia((pl, brano, numero))

    def _segna_nella_storia(self, posto):
        """Il brano che parte, nella storia della riproduzione casuale: se
        e' il posto atteso, cioe' quello prima o dopo che B, Z o l'avanzamento
        hanno preso dalla storia, ci si sposta li'; se e' quello in cui si e',
        come X da capo, niente cambia; altrimenti, anche se e' il brano di
        prima scelto con X, la storia da qui in avanti si dimentica e lui va
        in fondo, come in un browser."""
        i = self._nella_storia
        atteso, self._atteso_dalla_storia = self._atteso_dalla_storia, None
        if atteso is not None and _stesso_posto(atteso, posto):
            for vicino in (i + 1, i - 1):
                if 0 <= vicino < len(self._storia) and _stesso_posto(self._storia[vicino], posto):
                    self._nella_storia = vicino
                    return
        if 0 <= i < len(self._storia) and _stesso_posto(self._storia[i], posto):
            return
        del self._storia[i + 1:]
        self._storia.append(posto)
        del self._storia[:-MASSIMO_DELLA_STORIA]
        self._nella_storia = len(self._storia) - 1

    def _dalla_storia(self, verso):
        """Il posto della storia della riproduzione casuale subito prima
        (verso -1) o subito dopo (verso 1) di dove si e', saltando e
        dimenticando quelli che non sono piu' nella loro playlist; None se non
        ce n'e'."""
        i = self._nella_storia + verso
        while 0 <= i < len(self._storia):
            pl, brano, _numero = self._storia[i]
            if any(b is brano for b in pl.brani):
                return self._storia[i]
            del self._storia[i]
            if verso < 0:
                self._nella_storia -= 1
                i -= 1
        return None

    def _azzera_la_storia(self):
        """La storia della riproduzione casuale ricomincia: con il casuale
        acceso, da cio' che suona."""
        self._storia = []
        self._nella_storia = -1
        self._atteso_dalla_storia = None
        if self.impostazioni["casuale"] and self.motore.in_corso and self.coda.corrente is not None:
            self._segna_nella_storia((self.coda.playlist, self.coda.corrente, self.motore.sottobrano if self.motore.sottobrani else None))

    def _ricomincia_il_mazzo(self):
        """Il mazzo torna intero, e la scelta ricordata si dimentica; con la
        riproduzione casuale accesa, cio' che suona ne e' gia' uscito."""
        self._mazzo.clear()
        self._mazzo_tenuti.clear()
        self._casuale_ricordato = None
        if self.motore.in_corso and self.coda.corrente is not None:
            self._segna_nel_mazzo(self.coda.playlist, self.coda.corrente, self.motore.sottobrano if self.motore.sottobrani else None)

    def _evento_del_seguente(self, nuova, brano):
        """Il suono del passaggio automatico al brano della playlist nuova:
        nel loop, dopo il punto B si torna al punto A, e ha un suono suo. Da
        chiedere prima di spostare la coda."""
        if self.impostazioni["casuale"] and brano is not self.coda.corrente:
            # A caso non si torna al punto A: si va da un'altra parte.
            return "brano_seguente_da_solo"
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
        self._aggiorna_il_video()
        if self._mazzo_finito:
            # Il mazzo si rifa': la prossima riproduzione comincia un giro nuovo.
            self._mazzo_finito = False
            self._ricomincia_il_mazzo()
            self._riscontro("fine_playlist", "Fine: ogni brano del mazzo ha suonato una volta.")
            return
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
        if formati.e_midi(brano.percorso) and not self._midi_pronti():
            # Senza banco il MIDI non si prepara: a fine brano lo chiede _suona.
            return
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
        self._testo_superato()
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
        self._segna_nel_mazzo(nuova, brano, numero)
        self._annuncia(nuova, brano, evento)

    def _brano_in_errore(self, percorso):
        if self._chiusa:
            return
        self._uscente = self._preparato = None
        self._riscontro("errore", f"Non riesco a suonare {os.path.basename(percorso or '')}.")
        segno = self._avanzamento_dopo_errore = object()
        self._dopo_il_suono(self._avanza_dopo_l_errore, segno)

    def _avanza_dopo_l_errore(self, segno):
        if segno is not self._avanzamento_dopo_errore or self.motore.in_corso:
            # Intanto e' partito altro, per esempio con X, o V ha fermato.
            return
        self._avanzamento_dopo_errore = None
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
            self._riscontro("ripresa", self._frase_della_ripresa())
            self._riprende_il_video()
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
            self._riscontro("loop_a_messo", f"Punto A del loop su {brano.nome_del_file}. Maiuscolo+X su un brano della stessa lista, anche questo, mette il punto B.")
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
            posizione = self.motore.posizione
            self._riscontro("pausa", f"Pausa a {tempo(posizione)}." if posizione is not None else "Pausa.")
        else:
            self._riscontro("ripresa", self._frase_della_ripresa())
            self._riprende_il_video()

    def _frase_della_ripresa(self):
        posizione = self.motore.posizione
        return f"Riprende da {tempo(posizione)}." if posizione is not None else "Riprende."

    def _comando_stop(self):
        if self._avanzamento_dopo_errore is not None and not self.motore.in_corso:
            # Il brano dopo uno che non si suona sta per partire: V lo ferma.
            self._avanzamento_dopo_errore = None
            self._riscontro("stop", "Stop: il brano seguente non parte.")
            return
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
            self._aggiorna_il_video()
            self._riscontro("stop", "Stop. La selezione suonata è chiusa: X suona di nuovo ciò che selezioni.")
            return
        self._aggiorna_etichette()
        self._aggiorna_il_video()
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
        if self.impostazioni["casuale"] and self.coda.playlist:
            self._successivo_a_caso()
            return
        self._vicino(1, "successivo", "È l'ultimo brano.")

    def _comando_precedente(self):
        if self.impostazioni["casuale"] and self.coda.playlist:
            # Z torna al brano suonato prima, non a quello che sta prima.
            indietro = self._dalla_storia(-1)
            if indietro is None:
                self._riscontro("nessun_altro_brano", "È il primo brano suonato a caso.")
                return
            self._atteso_dalla_storia = indietro
            pl, brano, numero = indietro
            self._suona(pl, brano, "precedente", numero)
            return
        self._vicino(-1, "precedente", "È il primo brano.")

    def _successivo_a_caso(self):
        """B con la riproduzione casuale accesa (Gabriele, 4 ottobre 2026):
        se Z e' tornata indietro, il brano dopo nella storia; altrimenti uno
        a caso, con lo stesso modello e lo stesso mazzo dell'avanzamento
        automatico, e lo stesso brano gia' scelto per la dissolvenza."""
        seguente = self._dalla_storia(1)
        if seguente is None:
            seguente = self._seguente_casuale(self._voce_da_seguire(), None)
        else:
            self._atteso_dalla_storia = seguente
        if seguente is FINE_DEL_MAZZO:
            self._ricomincia_il_mazzo()
            self._riscontro("nessun_altro_brano", "Ogni brano del mazzo ha suonato una volta: B ricomincia un giro nuovo.")
            return
        if seguente is None:
            self._riscontro("nessun_altro_brano", "Non c'è un altro brano da scegliere a caso.")
            return
        pl, brano, numero = seguente
        self._suona(pl, brano, "successivo", numero)

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
        candidati = self._candidati_in_plancia(voce)
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
        di = f" di {tempo(durata)}" if durata is not None else ""
        self._riscontro(evento, f"{'Avanti' if secondi > 0 else 'Indietro'} a {tempo(arrivo)}{di}.", "salto")
        self._avvisa_l_attesa_del_sid(arrivo)

    def _avvisa_l_attesa_del_sid(self, arrivo):
        """Dopo un salto: se il brano e' un SID, un MIDI o un brano delle
        console e il punto d'arrivo non e' ancora reso, la console dice
        quanto c'e' da aspettare, che altrimenti sarebbe silenzio senza
        spiegazioni (tappa 5, 1.62.0)."""
        attesa = self.motore.attesa_del_sid(arrivo)
        if attesa >= ATTESA_DA_DIRE:
            in_corso = self.motore.in_corso or ""
            che = "Il MIDI" if formati.e_midi(in_corso) else "Il brano della console" if formati.e_chip(in_corso) else "Il SID"
            self.scrivi(f"{che} si prepara fino a {tempo(arrivo)}: circa {max(2, round(attesa))} secondi.")

    def _comando_avanti(self):
        self._salto(self.impostazioni["passo_avanti"], "avanti")

    def _comando_indietro(self):
        self._salto(-self.impostazioni["passo_indietro"], "indietro")

    def _chiedi_secondi(self, chiave, verso):
        self._domanda()
        attuale = self.impostazioni[chiave]
        with DialogoTesto(self, f"Di quanti secondi salta {verso}? Anche con i decimali, per esempio 2.5.", "Passo di salto", secondi_da_leggere(attuale)) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(f"Il salto {verso} resta di {valori.scrivi_durata(attuale)}.")
                return
            testo = dialogo.GetValue()
        secondi = leggi_tempo(testo)
        if not secondi or secondi < 0.1:
            self._riscontro("errore", f"{testo} non è un numero di secondi valido; il passo resta {secondi_da_leggere(attuale)}.")
            return
        self.impostazioni[chiave] = round(secondi, 3)
        self._salva_impostazioni()
        self._riscontro("passo_di_salto", f"Il salto {verso} ora è di {valori.scrivi_durata(round(secondi, 3))}.", "passo_di_salto")

    def _comando_passo_indietro(self):
        self._chiedi_secondi("passo_indietro", "indietro")

    def _comando_passo_avanti(self):
        self._chiedi_secondi("passo_avanti", "avanti")

    def _comando_vai_a_tempo(self):
        if self._niente_in_corso():
            return
        self._domanda()
        durata = self.motore.durata
        dura = f"Il brano dura {tempo(durata)}." if durata is not None else "La durata del brano non si sa ancora."
        with DialogoTesto(self, f"A che tempo andare? Minuti e secondi, per esempio 1:30, o dalla fine con il meno, per esempio -12. {dura}",
                "Vai al tempo") as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Vai al tempo annullato.")
                return
            testo = dialogo.GetValue()
        secondi = leggi_tempo_nel_brano(testo, durata)
        if secondi is None:
            self._riscontro("errore", f"{testo} non è un tempo dentro il brano.")
            return
        self.motore.vai_a(secondi)
        di = f" di {tempo(durata)}" if durata is not None else ""
        self._riscontro("vai_a_tempo", f"Vado a {tempo(secondi)}{di}.")
        self._avvisa_l_attesa_del_sid(secondi)

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
        self._domanda()
        attuale = self.impostazioni["passo_volume"]
        with DialogoTesto(self, "Di quanto cambiano il volume più e meno? Da 1 a 50.", "Passo del volume", str(attuale)) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Passo del volume non cambiato.")
                return
            testo = dialogo.GetValue()
        # La lettura delle impostazioni: un numero fuori dai limiti va al
        # limite, e lo si dice (tappa 9).
        try:
            passo, correzioni = valori.leggi_passo_volume(testo)
        except ErroreValore as e:
            self._riscontro("errore", f"{e} Il passo resta {attuale}.")
            return
        self.impostazioni["passo_volume"] = passo
        self._salva_impostazioni()
        self._riscontro("passo_del_volume", " ".join([f"Più e meno ora cambiano il volume di {passo}.", *correzioni]), "passo_del_volume")

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
        self._applica_il_banco()
        self._applica_il_karaoke()

    def _applica_il_karaoke(self):
        """Il modo e l'anticipo del karaoke al motore (1.82.0)."""
        self.motore.imposta_il_karaoke(self.impostazioni["karaoke"], self.impostazioni["anticipo_karaoke"])

    def _applica_la_dissolvenza(self):
        dissolvenza = self.impostazioni["dissolvenza"]
        self.motore.dissolvenza = dissolvenza["secondi"] if dissolvenza["accesa"] else 0

    def _applica_il_banco(self):
        """Il banco dei MIDI al motore, se FluidSynth c'e' e il banco si trova."""
        self.motore.banco_midi = self.impostazioni["banco_midi"] if self._midi_pronti() else None

    def _midi_pronti(self):
        banco = self.impostazioni["banco_midi"]
        return bool(banco) and midi.fluidsynth_presente() and midi.e_un_banco(banco)

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
        """O e P: la banda scelta giu' o su di un dB; ai limiti lo dicono. Il
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

    def _comando_riproduzione_casuale(self):
        """Maiuscolo con N: accende e spegne la riproduzione casuale (issue
        17): a caso il brano che segue quando uno finisce da solo, e dalla
        1.74.0 anche B, mentre Z torna ai brani suonati prima."""
        accesa = not self.impostazioni["casuale"]
        self.impostazioni["casuale"] = accesa
        self._ricomincia_il_mazzo()
        self._azzera_la_storia()
        self._salva_impostazioni()
        self._riscontro("casuale_acceso" if accesa else "casuale_spento", _frase_della_casuale(accesa, self.impostazioni["modello_casuale"]))

    def _comando_durata_della_dissolvenza(self):
        """Maiuscolo con L: chiede la durata della dissolvenza in secondi. La
        dissolvenza resta accesa o spenta com'era."""
        self._domanda()
        dissolvenza = self.impostazioni["dissolvenza"]
        attuale = dissolvenza["secondi"]
        da_leggere = valori.scrivi_durata(attuale)
        # Nel campo e nella domanda i numeri soli, senza la parola secondi.
        minimo, massimo, numero = (valori.scrivi_durata(s).split()[0] for s in (valori.DISSOLVENZA_MINIMA, valori.DISSOLVENZA_MASSIMA, attuale))
        with DialogoTesto(self, f"Quanti secondi dura la dissolvenza? Da {minimo} a {massimo}, anche con i decimali, per esempio 2.5.",
                "Durata della dissolvenza", numero) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(f"La durata della dissolvenza resta di {da_leggere}.")
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
        self._domanda()
        with DialogoDiFile(self, "Apri file", wildcard=formati.filtro_dialogo(), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Nessun file aperto.")
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
            "passo_indietro": lambda: valori.scrivi_durata(imp["passo_indietro"]),
            "passo_avanti": lambda: valori.scrivi_durata(imp["passo_avanti"]),
            "velocita": lambda: valori.scrivi_velocita(imp["velocita"]),
            "tono": lambda: valori.scrivi_tono(imp["tono"]),
            "bande": self._bande_da_leggere,
            "dissolvenza": lambda: valori.scrivi_dissolvenza(imp["dissolvenza"]),
            "casuale": lambda: "sì" if imp["casuale"] else "no",
            "modello_casuale": lambda: valori.MODELLI_CASUALI[imp["modello_casuale"]],
            "video": lambda: "sì" if imp["video"] else "no",
            "sottotitoli": lambda: "sì" if imp["sottotitoli"] else "no",
            "sintesi": self._sintesi_da_leggere,
            "destinazione": lambda: sintesi.DESTINAZIONI[imp["destinazione"]],
            "karaoke": lambda: MODI_DEL_KARAOKE[imp["karaoke"]],
            "anticipo_karaoke": lambda: f"{imp['anticipo_karaoke']} ms",
            "celle_braille": lambda: str(imp["celle_braille"]) if imp["celle_braille"] else "0, il testo intero",
            "lettura_minima": lambda: f"{imp['lettura_minima']} ms",
            "banco_midi": self._banco_da_leggere,
            "insegui": lambda: "sì" if imp["insegui"] else "no",
            "caratteri": self._caratteri_da_leggere,
            "colori_testo": lambda: self._colori_da_leggere("colori_testo"),
            "colori_sfondo": lambda: self._colori_da_leggere("colori_sfondo"),
            "righe_della_console": lambda: str(imp["righe_della_console"]),
            "salva_console": lambda: "scrive la console in un file di testo",
            "marcatori": self._marcatori_da_leggere,
            "importa_marcatori": lambda: "da un file esportato da MeTeOra",
            "impressi": lambda: MODI_DEGLI_IMPRESSI[imp["impressi"]],
            "dona": lambda: "offri un caffè all'autore, con PayPal",
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
            "modello_casuale": self._scegli_il_modello_casuale,
            "sintesi": self._scegli_la_sintesi,
            "banco_midi": self._scegli_il_banco,
            "salva_console": lambda _genitore: self._salva_console(),
            "marcatori": self._finestra_dei_marcatori,
            "importa_marcatori": self._importa_i_marcatori,
            "dona": self._dona,
            "impressi": self._scegli_come_leggere_gli_impressi,
            "destinazione": self._scegli_la_destinazione,
            "karaoke": self._scegli_il_modo_del_karaoke,
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
            self._domanda()
            with FinestraFiltro(genitore, f"{errore} {etichetta}" if errore else etichetta, testo, istruzioni) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self._annullato(f"{etichetta} non {participio}.")
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
                f"Per esempio 10 o 2.5, oppure minuti e secondi come 1:30. Anche Maiuscolo+{tasto} lo cambia, dalla finestra principale.",
                f"Adesso è di {valori.scrivi_durata(imp[chiave])}.", REGOLA_DEL_DOLLARO], attuale
        if chiave == "velocita":
            minima, massima, passo = (valori.scrivi_velocita(v) for v in (valori.VELOCITA_MINIMA, valori.VELOCITA_MASSIMA, valori.PASSO_VELOCITA))
            return valori.leggi_velocita, [
                f"La velocità di riproduzione, da {minima} a {massima}: 1 è la normale, meno di 1 rallenta, più di 1 accelera. Il tono non cambia.",
                f"Va a passi di {passo}: un valore fra due passi va al più vicino. Per esempio 1.05 o 0.9.",
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
                "con più bande vicine alzate, o tutte, sale fino a circa 5.6 dB oltre, e dal volume 80 o 90 in su conviene abbassare il volume.",
                "Anche U e I scelgono la banda, O e P la abbassano e la alzano, È la azzera e Maiuscolo con È le azzera tutte, dalla finestra principale.",
                f"Adesso: {self._bande_da_leggere()}.", REGOLA_DEL_DOLLARO], valori.scrivi_bande(imp["bande"])
        if chiave == "dissolvenza":
            secondi = imp["dissolvenza"]["secondi"]
            minima, massima = (valori.scrivi_durata(s).split()[0] for s in (valori.DISSOLVENZA_MINIMA, valori.DISSOLVENZA_MASSIMA))
            return (lambda testo: valori.leggi_dissolvenza(testo, secondi)), [
                "La dissolvenza incrociata: il brano che finisce sfuma mentre il seguente entra. Vale a ogni cambio di brano, da solo o con i tasti.",
                f"Scrivi no per spegnerla, sì per accenderla, oppure i secondi, da {minima} a {massima}, anche con i decimali, per accenderla con quella durata. Per esempio 4 o 2.5.",
                "Anche L la accende e la spegne, e Maiuscolo con L ne cambia la durata, dalla finestra principale.",
                f"Adesso è {valori.scrivi_dissolvenza(imp['dissolvenza'])}.", REGOLA_DEL_DOLLARO], valori.scrivi_dissolvenza(imp["dissolvenza"])
        if chiave == "casuale":
            return (lambda testo: valori.leggi_si_no(testo, "Riproduzione casuale")), [
                "Con la riproduzione casuale accesa, quando un brano finisce da solo il seguente si sceglie a caso, fra quelli che l'avanzamento automatico "
                "potrebbe suonare: le voci che si vedono nella plancia, oppure la lista, il loop o la selezione da cui si suona. Z, B e gli altri tasti restano come sono.",
                "Scrivi sì per accenderla, no per spegnerla; valgono anche s, n, 1, 0, acceso e spento. Anche Maiuscolo con N la accende e la spegne.",
                f"Adesso è {'accesa' if imp['casuale'] else 'spenta'}.", REGOLA_DEL_DOLLARO], "sì" if imp["casuale"] else "no"
        if chiave == "video":
            return (lambda testo: valori.leggi_si_no(testo, "Video")), [
                "Con il video acceso, quando parte un brano con il video si apre la sua finestra, sopra MeTeOra; allo stop sparisce. Spento, dei video si sente solo l'audio.",
                "Scrivi sì per accenderlo, no per spegnerlo; valgono anche s, n, 1, 0, acceso e spento. Anche Maiuscolo con F1 lo accende e lo spegne.",
                f"Adesso è {'acceso' if imp['video'] else 'spento'}.", REGOLA_DEL_DOLLARO], "sì" if imp["video"] else "no"
        if chiave == "sottotitoli":
            return (lambda testo: valori.leggi_si_no(testo, "Sottotitoli letti")), [
                "Con i sottotitoli letti accesi, ogni sottotitolo dei video va alla sintesi scelta qui sotto e si scrive nella console, anche con il video spento.",
                "Scrivi sì per accenderli, no per spegnerli; valgono anche s, n, 1, 0, acceso e spento. Maiuscolo con F2 li accende e sceglie la traccia, a giro.",
                f"Adesso sono {'accesi' if imp['sottotitoli'] else 'spenti'}.", REGOLA_DEL_DOLLARO], "sì" if imp["sottotitoli"] else "no"
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
        if chiave == "anticipo_karaoke":
            return valori.leggi_anticipo_del_karaoke, [
                f"Quanti millesimi di secondo prima del canto arriva il testo del karaoke: da 0 a {valori.ANTICIPO_MASSIMO_DEL_KARAOKE}.",
                "Per esempio 500, mezzo secondo prima. Vale per i MIDI, i file LRC e i testi nei tag, non per i sottotitoli dei video.",
                f"Adesso: {imp['anticipo_karaoke']}.", REGOLA_DEL_DOLLARO], str(imp["anticipo_karaoke"])
        if chiave == "celle_braille":
            return valori.leggi_celle_braille, [
                f"Quante celle ha la tua barra braille, da 0 a {valori.CELLE_MASSIME}: sottotitoli e karaoke arrivano in blocchi lunghi al più così, spezzati fra le parole.",
                "Ogni carattere conta una cella, come nel braille informatico a otto punti: con le tabelle a sei punti, dove maiuscole e numeri prendono più celle, scrivi qualche cella in meno.",
                "Per esempio 40; 0 manda il testo intero, senza dividerlo.",
                f"Adesso: {imp['celle_braille']}.", REGOLA_DEL_DOLLARO], str(imp["celle_braille"])
        if chiave == "lettura_minima":
            return valori.leggi_lettura_minima, [
                f"Per quanti millesimi di secondo resta almeno ogni blocco sulla barra braille: da {valori.LETTURA_MINIMA} a {valori.LETTURA_MASSIMA}.",
                "Per esempio 2000, il valore di partenza. I testi che arrivano prima aspettano il loro turno.",
                f"Adesso: {imp['lettura_minima']}.", REGOLA_DEL_DOLLARO], str(imp["lettura_minima"])
        return valori.leggi_righe_della_console, [
            f"Quante righe tiene la console: da {valori.RIGHE_MINIME} in su. Le più vecchie si tolgono dalla cima.",
            "Per esempio 2000, il valore di partenza. Un testo lungo, come le novità di F2, resta comunque intero.",
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
            return f"Il salto {'indietro' if chiave == 'passo_indietro' else 'avanti'} ora è di {valori.scrivi_durata(valore)}."
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
        if chiave == "casuale":
            self._ricomincia_il_mazzo()
            self._azzera_la_storia()
            return _frase_della_casuale(valore, imp["modello_casuale"])
        if chiave == "video":
            if not valore:
                self._spegni_il_video()
            self._aggiorna_il_video()
            return _frase_del_video(valore)
        if chiave == "sottotitoli":
            if not valore:
                self._braille.svuota()
            if not valore and self.motore.in_corso:
                self.motore.scegli_traccia("sid", "no")
            self._aggiorna_il_video()
            return "Sottotitoli letti accesi." if valore else "Sottotitoli letti spenti."
        if chiave == "insegui":
            if not valore:
                return "Inseguimento sganciato: la selezione resta dove la lasci."
            if self.motore.in_corso:
                self._insegui()
            return "Inseguimento agganciato: la selezione della plancia segue il brano che suona."
        if chiave in ("celle_braille", "lettura_minima"):
            # I blocchi in fila erano fatti con i valori di prima.
            self._testo_superato()
        if chiave == "celle_braille":
            return f"Sottotitoli e karaoke ora arrivano al braille in blocchi di {valore} celle al più." if valore else "Sottotitoli e karaoke ora arrivano al braille interi."
        if chiave == "lettura_minima":
            return f"Ogni blocco ora resta sulla barra braille almeno {valore} millesimi."
        if chiave == "anticipo_karaoke":
            self._applica_il_karaoke()
            return f"Il testo del karaoke ora arriva {valore} millesimi prima del canto." if valore else "Il testo del karaoke ora arriva quando comincia il canto."
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
                self._avviso_all_avvio("errore", f"La scheda audio scelta, {scelta['dispositivo']}, non si apre, e non riesco a usare quella automatica: {errore}.")
            else:
                self._avviso_all_avvio("errore", f"La scheda audio scelta, {scelta['dispositivo']}, non si apre: uso quella automatica.")
        elif errore is not None:
            self._avviso_all_avvio("errore", f"Non riesco a usare la scheda audio scelta, {scelta.get('dispositivo', 'automatica')}: {errore}.")
        elif esito["mancante"]:
            dove = f", {self._nome_della_scheda(esito['dispositivo'], esito['interfaccia'])}" if esito["dispositivo"] else ""
            self._avviso_all_avvio("errore", f"La scheda audio scelta, {scelta['dispositivo']}, non c'è: uso quella automatica{dove}.")
        elif not esito["musica"]:
            self._avviso_all_avvio("errore", f"La musica non ritrova la scheda audio {esito['dispositivo']} e suona sulla scheda di Windows.")

    # Il video e i sottotitoli, tappa 7.

    def _aggiorna_il_video(self):
        """Il video del brano in corso: la finestra si apre, se il video e'
        acceso e il brano ne ha uno, e altrimenti si chiude; i sottotitoli si
        accendono o si spengono come dicono le impostazioni. Si chiama a ogni
        brano annunciato, quando il motore ha aperto un brano, allo stop e
        quando cambia un'impostazione: rifare i conti non costa niente."""
        if self._chiusa:
            return
        if not self.motore.in_corso:
            self._nascondi_il_video()
            self._aggiorna_la_lettura(None)
            return
        tracce = self.motore.tracce()
        if tracce is None:
            # Il brano si sta aprendo: decide l'avviso del caricamento, senza
            # chiudere e riaprire la finestra nel frattempo.
            return
        self._aggiorna_la_lettura(tracce, scelta=self._sottotitoli_del_brano(tracce))
        in_attesa = self.motore.in_pausa and self.motore.in_corso == self._video_in_attesa
        if self.impostazioni["video"] and tracce["video"] and self.motore.in_corso != self._video_nascosto_per and not in_attesa:
            self._mostra_il_video()
        else:
            self._nascondi_il_video()

    def _sottotitoli_del_brano(self, tracce):
        """Accesi, se il brano non ne ha gia' scelti si prende la prima traccia,
        o, con gli impressi scelti, il file della loro passata, se c'e', e
        altrimenti nessuna, perche' si leggono al volo; spenti, nessuna. Torna
        la traccia appena scelta, None se li ha spenti, _DALLE_TRACCE se non
        ha cambiato niente: la lettura dei sottotitoli fatti di immagini deve
        sapere la scelta prima che le tracce la dicano."""
        scelta = next((t for t in tracce["sub"] if t.get("selected")), None)
        if self.impostazioni["sottotitoli"] and scelta is None and tracce["sub"]:
            passata = _traccia_della_passata(tracce)
            # Gli impressi scelti contano solo sui video: su un brano senza,
            # come un kar, si prende la prima traccia, il suo testo.
            if self.impostazioni["impressi_scelti"] and tracce["video"]:
                if passata is None:
                    return _DALLE_TRACCE
                nuova = passata
            else:
                nuova = next((t for t in tracce["sub"] if t is not passata), passata)
            self.motore.scegli_traccia("sid", str(nuova["id"]))
            return nuova
        if not self.impostazioni["sottotitoli"] and scelta is not None:
            self.motore.scegli_traccia("sid", "no")
            return None
        return _DALLE_TRACCE

    def _mostra_il_video(self):
        if self._video is None:
            self._video = FinestraVideo(self, lambda: self.motore.posizione, lambda: self.motore.durata, self._salta_dalla_barra, self._nascondi_a_mano)
        if not self._video_nel_motore:
            self.motore.imposta_il_video(self._video.finestre())
            self._video_nel_motore = True
        self._video.mostra_il_lettore(self.motore.indice_attivo())
        titolo = f"{os.path.basename(self.motore.in_corso or '')}, video, MeTeOra"
        if self._video.IsShown():
            # Gia' aperta: si aggiorna, senza riprendere il fuoco a chi lo ha.
            self._video.SetTitle(titolo)
            return
        if not ctypes.windll.user32.IsWindowEnabled(self.GetHandle()):
            # Un dialogo e' aperto: la finestra del video gli ruberebbe il
            # fuoco, e le lettere scritte nel campo diventerebbero comandi. Si
            # apre quando MeTeOra torna attiva (tappa 9).
            self._video_rimandato = True
            return
        self._video.apri(titolo, self.GetScreenRect())

    def _nascondi_il_video(self):
        """La finestra del video sparisce. Se aveva il fuoco, MeTeOra torna
        davanti con il fuoco dove lo aveva lasciato; se no, il fuoco resta
        dov'e', per esempio in un dialogo o nella console (tappa 9)."""
        if self._video is None or not self._video.IsShown():
            return
        attiva = self._video.IsActive()
        self._video.chiudi()
        if not attiva:
            return
        # Tornando attiva, la finestra rimette da se' il fuoco sull'ultimo
        # controllo che lo aveva; la plancia solo se non lo trova.
        self.Raise()
        wx.CallAfter(self._fuoco_dopo_il_video)

    def _fuoco_dopo_il_video(self):
        if self._chiusa:
            return
        fuoco = wx.Window.FindFocus()
        if fuoco is None or fuoco.GetTopLevelParent() is not self:
            self.albero.SetFocus()

    def _nascondi_a_mano(self):
        """Esc nella finestra del video, o la sua chiusura: la finestra
        sparisce per il brano in corso, e il video resta acceso per i brani
        dopo."""
        self._video_nascosto_per = self.motore.in_corso
        self._nascondi_il_video()
        self._riscontro("video_nascosto", "Video nascosto per questo brano: il prossimo video si apre da sé.")

    def _salta_dalla_barra(self, secondi):
        """La barra del tempo della finestra del video, per chi vede: il
        salto ha il riscontro di W."""
        self.motore.vai_a(secondi)
        durata = self.motore.durata
        self._riscontro("vai_a_tempo", f"Vado a {tempo(secondi)}" + (f" di {tempo(durata)}." if durata is not None else "."))

    def _all_attivazione(self, evento):
        """Tornata attiva, per esempio alla chiusura di un dialogo, MeTeOra
        apre la finestra del video rimandata intanto."""
        evento.Skip()
        if evento.GetActive() and self._video_rimandato:
            self._video_rimandato = False
            wx.CallAfter(self._aggiorna_il_video)

    def _riprende_il_video(self):
        """X o C tolgono la pausa del brano ripreso all'avvio: se e' un
        video, adesso la sua finestra si apre."""
        if self._video_in_attesa is not None:
            self._video_in_attesa = None
            self._aggiorna_il_video()

    def _spegni_il_video(self):
        if self._video_nel_motore:
            self.motore.imposta_il_video(None)
            self._video_nel_motore = False

    def _sottotitolo(self, testo):
        """Un sottotitolo del brano in corso: alla sintesi scelta e nella
        console, se i sottotitoli letti sono accesi. Alla voce va subito,
        intero; al braille in fila, a blocchi lunghi quanto la barra, con il
        tempo che resta al sottotitolo diviso fra i blocchi e il tempo minimo
        di lettura (1.83.0)."""
        testo = " ".join(testo.split())
        if self._chiusa or not testo or not self.impostazioni["sottotitoli"]:
            return
        imp = self.impostazioni
        if imp["destinazione"] in ("entrambi", "sintesi"):
            self._sintesi.dici(testo, imp["sintesi"], "sintesi")
        if imp["destinazione"] in ("entrambi", "braille"):
            self._braille.aggiungi(testo, imp["celle_braille"], imp["lettura_minima"] / 1000, self.motore.resto_del_sottotitolo())
        self.scrivi(testo)

    def _testo_superato(self):
        """Un salto, uno stop, un brano nuovo o un'altra traccia: i blocchi in
        fila per il braille non valgono piu', e il testo dopo arriva subito
        (revisione della 1.83.0)."""
        coda = getattr(self, "_braille", None)
        if coda is not None:
            coda.svuota()

    def _mostra_in_braille(self, blocco):
        """Un blocco della coda del braille, sulla barra."""
        if not self._chiusa:
            self._sintesi.dici(blocco, self.impostazioni["sintesi"], "braille")

    def _comando_video(self):
        """Maiuscolo con F1: il video acceso o spento."""
        acceso = not self.impostazioni["video"]
        self.impostazioni["video"] = acceso
        self._video_nascosto_per = None
        self._salva_impostazioni()
        if not acceso:
            self._spegni_il_video()
        self._riscontro("video_acceso" if acceso else "video_spento", _frase_del_video(acceso))
        self._aggiorna_il_video()

    def _comando_sottotitoli(self):
        """Maiuscolo con F2: i sottotitoli letti a giro, spenti, la prima
        traccia, la seconda e cosi' via, e sui video in fondo i sottotitoli
        impressi (1.80.0): la traccia del file di una passata non e' un passo
        a se', e' quello degli impressi. Su un brano senza sottotitoli, e
        senza impressi da leggere, li accende o li spegne per i brani dopo."""
        tracce = self.motore.tracce() if self.motore.in_corso else None
        passata = _traccia_della_passata(tracce)
        sottotitoli = [t for t in (tracce["sub"] if tracce else []) if t is not passata]
        # Gli impressi ci sono se c'e' il file della passata, o se si possono leggere.
        con_gli_impressi = bool(tracce and tracce["video"] and (passata is not None or ocr.disponibile()))
        if not sottotitoli and not con_gli_impressi:
            acceso = not self.impostazioni["sottotitoli"]
            self.impostazioni["impressi_scelti"] = False
            frase = ("Sottotitoli letti accesi; questo brano non ne ha." if tracce else "Sottotitoli letti accesi.") if acceso else "Sottotitoli letti spenti."
        else:
            if (passata is not None and passata.get("selected")) or (self.impostazioni["impressi_scelti"] and self.impostazioni["sottotitoli"]
                    and tracce["video"] and not any(t.get("selected") for t in sottotitoli)):
                attuale = len(sottotitoli)
            else:
                attuale = next((i for i, t in enumerate(sottotitoli) if t.get("selected")), None)
            indice = 0 if attuale is None else attuale + 1
            if indice < len(sottotitoli):
                acceso, frase = True, self._scegli_i_sottotitoli(tracce, sottotitoli[indice], indice, len(sottotitoli))
            elif indice == len(sottotitoli) and con_gli_impressi:
                acceso, frase = True, self._scegli_gli_impressi(tracce, passata)
            else:
                acceso, frase = False, "Sottotitoli letti spenti."
                self.impostazioni["impressi_scelti"] = False
                self.motore.scegli_traccia("sid", "no")
        self.impostazioni["sottotitoli"] = acceso
        self._salva_impostazioni()
        self._riscontro("sottotitoli_accesi" if acceso else "sottotitoli_spenti", frase)
        if not acceso:
            self._braille.svuota()
            self._aggiorna_la_lettura(tracce, scelta=None)

    def _scegli_i_sottotitoli(self, tracce, traccia, indice, quante):
        """Una traccia di sottotitoli, scelta con Maiuscolo con F2; se e' fatta
        di immagini, la legge il riconoscimento dei caratteri."""
        self.impostazioni["impressi_scelti"] = False
        self.impostazioni["sottotitoli"] = True
        self._testo_superato()
        self.motore.scegli_traccia("sid", str(traccia["id"]))
        titolo = traccia.get("title") or ""
        if titolo.startswith(karaoke.TITOLO):
            # Il testo del karaoke dice da dove viene, non il formato (1.82.0).
            numero = f", traccia {indice + 1} di {quante}" if quante > 1 else ""
            frase = f"Testo del karaoke letto{numero}, {titolo[len(karaoke.TITOLO):].lstrip(', ')}."
            self._aggiorna_la_lettura(tracce, scelta=traccia)
            return frase
        frase = f"Sottotitoli letti, traccia {_descrivi_traccia(traccia, indice, quante)}."
        if traccia.get("codec") in sottotitoli_ocr.CODEC_A_IMMAGINI:
            if ocr.disponibile():
                frase += " È fatta di immagini: la legge il riconoscimento dei caratteri di Windows."
            else:
                frase += " È fatta di immagini, e il riconoscimento dei caratteri di Windows non c'è: non si può leggere."
        self._aggiorna_la_lettura(tracce, scelta=traccia)
        return frase

    def _scegli_gli_impressi(self, tracce, passata):
        """I sottotitoli impressi nel video, in fondo al giro di Maiuscolo
        con F2 (Gabriele, 4 ottobre 2026): il file della passata, se c'e',
        in ogni modo, perche' e' a tempo e senza ritardo; altrimenti letti al
        volo, e con la passata scelta nelle impostazioni la passata parte."""
        self.impostazioni["impressi_scelti"] = True
        self.impostazioni["sottotitoli"] = True
        self._testo_superato()
        if passata is not None:
            self.motore.scegli_traccia("sid", str(passata["id"]))
            self._aggiorna_la_lettura(tracce, scelta=passata)
            return "Sottotitoli impressi, dal file della passata fatta prima."
        self.motore.scegli_traccia("sid", "no")
        self._aggiorna_la_lettura(tracce, scelta=None)
        video = self.motore.in_corso
        if self.impostazioni["impressi"] != "passata":
            return "Sottotitoli impressi, letti al volo."
        if self._passata is not None and self._passata.video == video:
            return "Sottotitoli impressi, letti al volo: la passata è già in corso."
        if video in self._passate_vuote:
            return "Sottotitoli impressi, letti al volo: la passata di prima non ne ha trovati in questo video."
        self._avvia_la_passata(video)
        return "Sottotitoli impressi, letti al volo mentre la passata li prepara per le volte dopo."

    def _sottotitolo_a_immagini(self):
        """Dal filo del motore: comincia un sottotitolo. La lettura delle
        tracce a immagini, se c'e', lo fotografa e lo legge."""
        lettura = getattr(self, "_lettura", None)
        if lettura is not None and lettura.tipo == "immagini":
            lettura.nuovo_sottotitolo()

    def _aggiorna_la_lettura(self, tracce, scelta=_DALLE_TRACCE):
        """La lettura dei sottotitoli fatti di immagini che serve adesso: le
        tracce a immagini, se ne e' scelta una; quelli impressi, se li ha
        scelti Maiuscolo con F2 e non c'e' una traccia; nessuna altrimenti, o
        se il riconoscimento non c'e'. scelta e' la traccia appena scelta, o
        None per nessuna; senza, la si legge dalle tracce."""
        voluta = None
        if self.impostazioni["sottotitoli"] and tracce and tracce["video"] and not self._chiusa:
            if scelta is _DALLE_TRACCE:
                scelta = next((t for t in tracce["sub"] if t.get("selected")), None)
            if scelta is not None and scelta.get("codec") in sottotitoli_ocr.CODEC_A_IMMAGINI:
                voluta = ("immagini", ocr.lingua_per(scelta.get("lang")))
            elif scelta is None and self.impostazioni["impressi_scelti"]:
                voluta = ("impressi", ocr.lingua_per(None))
        if voluta is not None and (voluta[1] is None or not ocr.disponibile()):
            voluta = None
        attuale = (self._lettura.tipo, self._lettura.lingua) if self._lettura is not None else None
        if voluta == attuale:
            return
        if self._lettura is not None:
            self._lettura.ferma()
            self._lettura = None
        self.motore.leggi_il_video(voluta is not None, oscura=voluta is not None and voluta[0] == "immagini")
        if voluta is not None:
            classe = sottotitoli_ocr.LetturaDelleImmagini if voluta[0] == "immagini" else sottotitoli_ocr.LetturaDegliImpressi
            self._lettura = classe(self.motore, lambda testo: wx.CallAfter(self._sottotitolo, testo), voluta[1],
                guasto=lambda frase: wx.CallAfter(self._riscontro, "errore", frase)).avvia()

    def _avvia_la_passata(self, video):
        """La passata in anticipo dei sottotitoli impressi di un video, in
        sottofondo: la console dice a che punto e', ogni dieci per cento. Una
        passata su un altro video si ferma, e la console lo dice."""
        if self._passata is not None:
            self._passata.ferma()
            self.scrivi(f"La passata dei sottotitoli impressi di {os.path.basename(self._passata.video)} si ferma: ne parte una per {os.path.basename(video)}.")
        self._passata = sottotitoli_ocr.PassataDegliImpressi(video, ocr.lingua_per(None),
            lambda percentuale: wx.CallAfter(self._passata_avanza, video, percentuale),
            lambda esito: wx.CallAfter(self._passata_finita, video, esito)).avvia()
        durata = self.motore.durata or 0
        minuti = max(1, round(durata / sottotitoli_ocr.VELOCITA_DELLA_PASSATA / 60))
        quanto = f": ci vogliono circa {al_plurale(minuti, 'minuto', 'minuti')}" if durata else ""
        self._riscontro("passata_avviata", f"Comincia la passata dei sottotitoli impressi di {os.path.basename(video)}{quanto}; intanto li leggo al volo.")

    def _passata_avanza(self, video, percentuale):
        if self._chiusa or self._passata is None or self._passata.video != video or not 0 < percentuale < 100:
            return
        self.scrivi(f"Passata dei sottotitoli impressi di {os.path.basename(video)}: {percentuale}%.", categoria="passata")

    def _passata_finita(self, video, esito):
        """La passata e' finita. Il file scritto diventa una traccia del video,
        se suona ancora, e si sceglie solo se si aspettavano gli impressi: chi
        nel frattempo ha scelto un'altra traccia, o li ha spenti, la tiene."""
        if self._chiusa or self._passata is None or self._passata.video != video:
            return
        lingua = self._passata.lingua
        self._passata = None
        nome = os.path.basename(video)
        if esito is None:
            self._passate_vuote.add(video)
            self._riscontro("passata_finita", f"La passata non ha trovato sottotitoli impressi in {nome}.")
            return
        if not os.path.isfile(esito):
            self._riscontro("errore", esito)
            return
        sceglierla = self.motore.in_corso == video and self.impostazioni["sottotitoli"] and self.impostazioni["impressi_scelti"]
        if self.motore.in_corso == video:
            self.motore.aggiungi_sottotitoli(esito, TITOLO_DELLA_PASSATA, lingua.split("-")[0], scegli=sceglierla)
        if sceglierla:
            self._aggiorna_la_lettura(self.motore.tracce(), scelta={"codec": "subrip", "title": TITOLO_DELLA_PASSATA})
            self._riscontro("passata_finita", f"Sottotitoli impressi pronti nel file {os.path.basename(esito)}, accanto al video: da ora si leggono da lì.")
        else:
            self._riscontro("passata_finita", f"Sottotitoli impressi pronti nel file {os.path.basename(esito)}, accanto al video: Maiuscolo con F2 li sceglie, anche le volte dopo.")

    def _comando_traccia_audio(self):
        """Maiuscolo con F3: la traccia audio del brano, a giro."""
        if self._niente_in_corso():
            return
        tracce = self.motore.tracce()
        audio = tracce["audio"] if tracce else []
        if len(audio) < 2:
            self._riscontro("non_disponibile", "Questo brano ha una traccia audio sola." if audio else "Questo brano non ha tracce audio da scegliere.")
            return
        scelta = next((i for i, t in enumerate(audio) if t.get("selected")), -1)
        indice = (scelta + 1) % len(audio)
        self.motore.scegli_traccia("aid", str(audio[indice]["id"]))
        self._riscontro("traccia_audio", f"Traccia audio {_descrivi_traccia(audio[indice], indice, len(audio))}.")

    def _comando_schermo_intero(self):
        """Maiuscolo con F5: la finestra del video a schermo intero, o di nuovo in finestra."""
        if self._video is None or not self._video.IsShown():
            self._riscontro("non_disponibile", "La finestra del video non è aperta.")
            return
        if self._video.schermo_intero():
            self._riscontro("schermo_intero", "Video a schermo intero.")
        else:
            self._riscontro("schermo_in_finestra", "Video in finestra.")

    def _comando_rapporto(self):
        """Maiuscolo con F6: il rapporto dell'immagine, a giro."""
        self._rapporto = (self._rapporto + 1) % len(RAPPORTI)
        valore, nome = RAPPORTI[self._rapporto]
        self.motore.rapporto(valore)
        self._riscontro("rapporto", f"Rapporto dell'immagine: {nome}.")

    def _sintesi_da_leggere(self):
        scelta = self.impostazioni["sintesi"]
        if scelta != sintesi.AUTOMATICA:
            return sintesi.nome(scelta)
        effettiva = self._sintesi.scelta(sintesi.AUTOMATICA)
        return f"automatica, adesso {sintesi.nome(effettiva)}" if effettiva else "automatica, adesso nessuna"

    def _scegli_la_sintesi(self, genitore):
        """La sintesi dei sottotitoli, da una lista: l'automatica e le uscite
        che si possono usare adesso."""
        chiavi = [sintesi.AUTOMATICA, *sintesi.disponibili()]
        attuale = self.impostazioni["sintesi"]
        if attuale not in chiavi:
            # Una scelta di prima che ora non risponde resta in fondo, e lo dice.
            chiavi.append(attuale)
        righe = [self._riga_della_sintesi(chiave) for chiave in chiavi]
        self._domanda()
        nome = VOCI_DELLE_IMPOSTAZIONI["sintesi"][0]
        with FinestraScelta(genitore, nome, righe, chiavi.index(attuale)) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(f"{nome} non cambiata.")
                return
            indice = dialogo.GetSelection()
        self.impostazioni["sintesi"] = chiavi[indice]
        self._salva_impostazioni()
        genitore.aggiorna("sintesi", self._riga_dell_impostazione("sintesi"))
        self._riscontro("impostazione_cambiata", f"{nome}: {self._sintesi_da_leggere()}.")

    def _riga_della_sintesi(self, chiave):
        if chiave == sintesi.AUTOMATICA:
            return "Automatica: lo screen reader attivo, altrimenti la voce di Windows"
        if chiave in sintesi.USCITE and self._sintesi.scelta(chiave) is None:
            return f"{sintesi.nome(chiave)}, che adesso non risponde"
        return sintesi.nome(chiave)[0].upper() + sintesi.nome(chiave)[1:]

    # I MIDI, tappa 8: FluidSynth e il banco dei suoni.

    def _prepara_i_midi(self, dopo=None, genitore=None):
        """Al primo MIDI: dice cosa serve, scarica FluidSynth se manca, cerca
        nei dischi i banchi di suoni e li propone; se non ce ne sono propone
        FluidR3. Tutto in disparte; dopo() arriva quando i MIDI sono pronti.
        genitore e' il dialogo da cui si parte, se c'e', per le domande."""
        if self._midi_in_preparazione:
            self._riscontro("non_disponibile", "Sto preparando i MIDI: un momento.")
            return
        serve_fluidsynth = not midi.fluidsynth_presente()
        if serve_fluidsynth:
            domanda = ("Per suonare i MIDI MeTeOra usa FluidSynth, un programma libero di circa 3 MB, e un banco di suoni General MIDI. "
                "Scarico FluidSynth e cerco nei dischi i banchi che hai già? La ricerca può durare qualche minuto.")
        else:
            domanda = "Per suonare i MIDI serve un banco di suoni General MIDI. Cerco nei dischi quelli che hai già? La ricerca può durare qualche minuto."
        if not self._conferma(domanda, "MIDI", self._genitore_valido(genitore)):
            self._annullato(MIDI_DA_PREPARARE)
            return
        self._midi_in_preparazione = True

        def lavoro():
            if serve_fluidsynth:
                wx.CallAfter(self._riscontro, "scaricamento_avviato", "Scarico FluidSynth.")
                try:
                    midi.scarica_fluidsynth()
                except (OSError, ValueError) as e:
                    return ("errore", f"FluidSynth non si scarica: {e}")
                wx.CallAfter(self._riscontro, "scaricamento_finito", "FluidSynth pronto.")
            wx.CallAfter(self._riscontro_dopo, "ricerca_avviata", "Cerco i banchi di suoni nei dischi.")
            return ("trovati", midi.cerca_banchi(avvisa=lambda quante: wx.CallAfter(self.scrivi, f"Cerco i banchi: {quante} cartelle viste.", "banchi")))

        midi_in_disparte(lavoro, lambda esito: wx.CallAfter(self._banchi_cercati, esito, dopo, genitore))

    def _genitore_valido(self, genitore):
        """Il dialogo da cui si e' partiti, se e' ancora aperto, o la finestra
        principale: un dialogo chiuso nel frattempo non fa da genitore."""
        return genitore if genitore and genitore.IsShown() else self

    def _banchi_cercati(self, esito, dopo, genitore=None):
        self._midi_in_preparazione = False
        if self._chiusa:
            return
        tipo, valore = esito
        if tipo == "errore":
            self._riscontro("errore", valore)
            return
        trovati = valore
        genitore = self._genitore_valido(genitore)
        if not trovati:
            self._riscontro("ricerca_finita", "Nei dischi non ho trovato banchi di suoni General MIDI.")
            if self._conferma(f"Scarico FluidR3 GM, il banco storico di FluidSynth, circa {midi.FLUIDR3_DIMENSIONE // 1_000_000} MB?", "MIDI", genitore):
                self._scarica_fluidr3(dopo, genitore)
            else:
                self._annullato(MIDI_DA_PREPARARE)
            return
        self._riscontro("ricerca_finita", "Trovato un banco General MIDI." if len(trovati) == 1 else f"Trovati {len(trovati)} banchi General MIDI.")
        self._scegli_fra_i_banchi(trovati, genitore, dopo)

    def _scegli_fra_i_banchi(self, trovati, genitore, dopo=None):
        """La lista dei banchi trovati, con in fondo lo scaricamento di FluidR3."""
        righe = [f"{os.path.splitext(os.path.basename(p))[0]}, {midi.dimensione_da_leggere(d)}, in {os.path.dirname(p)}" for p, d in trovati]
        righe.append(f"Scarica FluidR3 GM, circa {midi.FLUIDR3_DIMENSIONE // 1_000_000} MB")
        self._domanda()
        with FinestraScelta(genitore, "Banco dei suoni MIDI", righe, 0) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Banco dei suoni MIDI non cambiato.")
                return
            indice = dialogo.GetSelection()
        if indice == len(trovati):
            self._scarica_fluidr3(dopo, genitore)
        else:
            self._usa_il_banco(trovati[indice][0], dopo, genitore)

    def _scarica_fluidr3(self, dopo=None, genitore=None):
        self._midi_in_preparazione = True
        self._riscontro("scaricamento_avviato", f"Scarico FluidR3 GM, circa {midi.FLUIDR3_DIMENSIONE // 1_000_000} MB.")
        decimi = [0]

        def avanza(scaricati, totale):
            if totale and scaricati * 10 // totale > decimi[0]:
                decimi[0] = scaricati * 10 // totale
                wx.CallAfter(self.scrivi, f"FluidR3 GM: {decimi[0] * 10} per cento.", "banchi")

        def lavoro():
            try:
                return ("banco", midi.scarica_fluidr3(avanza))
            except (OSError, ValueError) as e:
                return ("errore", f"FluidR3 GM non si scarica: {e}")

        midi_in_disparte(lavoro, lambda esito: wx.CallAfter(self._fluidr3_scaricato, esito, dopo, genitore))

    def _fluidr3_scaricato(self, esito, dopo, genitore):
        self._midi_in_preparazione = False
        if self._chiusa:
            return
        tipo, valore = esito
        if tipo == "errore":
            self._riscontro("errore", valore)
            return
        self._riscontro("scaricamento_finito", "FluidR3 GM scaricato.")
        # Il banco nuovo, e il MIDI in attesa, dopo il suono dello scaricamento.
        self._dopo_il_suono(self._usa_il_banco, valore, dopo, genitore)

    def _usa_il_banco(self, percorso, dopo=None, genitore=None):
        """Il banco scelto vale da subito, e si ricorda."""
        self.impostazioni["banco_midi"] = percorso
        self._salva_impostazioni()
        self._applica_il_banco()
        # Il dialogo da cui si e' partiti puo' essersi chiuso intanto.
        if genitore and genitore.IsShown() and hasattr(genitore, "aggiorna"):
            genitore.aggiorna("banco_midi", self._riga_dell_impostazione("banco_midi"))
        self._riscontro("impostazione_cambiata", f"I MIDI suonano con il banco {os.path.basename(percorso)}.")
        if dopo is not None and self._midi_pronti():
            self._dopo_il_suono(dopo)

    def _banco_da_leggere(self):
        banco = self.impostazioni["banco_midi"]
        if not banco:
            return "nessuno, si sceglie al primo MIDI"
        if not midi.e_un_banco(banco):
            return f"{banco}, che non si trova più"
        return os.path.basename(banco) + ("" if midi.fluidsynth_presente() else ", FluidSynth da scaricare")

    def _scegli_il_banco(self, genitore):
        """La voce Banco dei suoni MIDI: cerca nel PC, scrivi il percorso, o
        scarica FluidR3."""
        righe = ["Cerca i banchi nel PC", "Scrivi il percorso di un banco", f"Scarica FluidR3 GM, circa {midi.FLUIDR3_DIMENSIONE // 1_000_000} MB"]
        self._domanda()
        with FinestraScelta(genitore, "Banco dei suoni MIDI", righe, 0) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Banco dei suoni MIDI non cambiato.")
                return
            indice = dialogo.GetSelection()
        if indice == 0:
            self._prepara_i_midi(genitore=genitore)
        elif indice == 1:
            self._scrivi_il_banco(genitore)
        else:
            self._scarica_fluidr3(genitore=genitore)

    def _scrivi_il_banco(self, genitore):
        self._domanda()
        with DialogoTesto(genitore, "Il percorso del banco di suoni, un file sf2 o sf3.", "Banco dei suoni MIDI", self.impostazioni["banco_midi"]) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Banco dei suoni MIDI non cambiato.")
                return
            percorso = dialogo.GetValue().strip().strip('"')
        if not midi.e_un_banco(percorso):
            self._riscontro("errore", f"{percorso} non è un banco di suoni: serve un file sf2 o sf3.")
            return
        self._usa_il_banco(percorso, genitore=genitore)
        if not midi.general_midi(percorso):
            self.scrivi("Non è un banco General MIDI completo: alcuni strumenti dei MIDI potrebbero mancare o suonare con un altro timbro.")

    def _scegli_come_leggere_gli_impressi(self, genitore):
        """Come si leggono i sottotitoli impressi, da una lista: al volo o con
        la passata in anticipo (Gabriele, 4 ottobre 2026)."""
        chiavi = list(MODI_DEGLI_IMPRESSI)
        righe = [f"{MODI_DEGLI_IMPRESSI[c][0].upper()}{MODI_DEGLI_IMPRESSI[c][1:]}" for c in chiavi]
        self._domanda()
        with FinestraScelta(genitore, "Sottotitoli impressi", righe, chiavi.index(self.impostazioni["impressi"])) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Sottotitoli impressi non cambiati.")
                return
            indice = dialogo.GetSelection()
        self.impostazioni["impressi"] = chiavi[indice]
        self._salva_impostazioni()
        genitore.aggiorna("impressi", self._riga_dell_impostazione("impressi"))
        self._riscontro("impostazione_cambiata", f"I sottotitoli impressi ora sono {MODI_DEGLI_IMPRESSI[chiavi[indice]]}.")

    def _scegli_da_una_lista(self, genitore, chiave, scelte, frase):
        """Una voce delle impostazioni scelta da una lista: scelte va dalle
        chiavi alle righe, frase(chiave) dice la scelta fatta. Torna vero se
        e' cambiata."""
        nome = VOCI_DELLE_IMPOSTAZIONI[chiave][0]
        chiavi = list(scelte)
        righe = [f"{scelte[c][0].upper()}{scelte[c][1:]}" for c in chiavi]
        self._domanda()
        with FinestraScelta(genitore, nome, righe, chiavi.index(self.impostazioni[chiave])) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(f"{nome}: non cambiato.")
                return False
            indice = dialogo.GetSelection()
        self.impostazioni[chiave] = chiavi[indice]
        self._salva_impostazioni()
        genitore.aggiorna(chiave, self._riga_dell_impostazione(chiave))
        self._riscontro("impostazione_cambiata", frase(chiavi[indice]))
        return True

    def _scegli_la_destinazione(self, genitore):
        """Dove vanno sottotitoli e karaoke: alla sintesi, al braille o a
        tutti e due (Gabriele, 4 ottobre 2026)."""
        if self._scegli_da_una_lista(genitore, "destinazione", sintesi.DESTINAZIONI, self._frase_della_destinazione):
            self._testo_superato()

    def _frase_della_destinazione(self, chiave):
        """La destinazione scelta, e se il braille non arrivera', perche'
        l'uscita in uso non ce l'ha."""
        frase = f"Sottotitoli e karaoke ora vanno {sintesi.DESTINAZIONI[chiave]}."
        effettiva = self._sintesi.scelta(self.impostazioni["sintesi"])
        if chiave != "sintesi" and effettiva is not None and effettiva not in sintesi.CON_IL_BRAILLE:
            frase += f" Con {sintesi.nome(effettiva)}, il braille non arriva: ce l'hanno NVDA, JAWS e System Access."
        return frase

    def _scegli_il_modo_del_karaoke(self, genitore):
        """Il testo del karaoke per riga o per strofa (Gabriele, 4 ottobre
        2026): la traccia del brano in corso si rifa' subito."""
        if self._scegli_da_una_lista(genitore, "karaoke", MODI_DEL_KARAOKE,
                lambda chiave: f"Il testo del karaoke ora arriva {MODI_DEL_KARAOKE[chiave]}."):
            self._applica_il_karaoke()

    def _scegli_il_modello_casuale(self, genitore):
        """Il modello della riproduzione casuale, da una lista (Gabriele,
        collaudo della 1.60.1). Cambiandolo il mazzo si rifa'."""
        chiavi = list(valori.MODELLI_CASUALI)
        righe = [f"{valori.MODELLI_CASUALI[c][0].upper()}{valori.MODELLI_CASUALI[c][1:]}: {SPIEGAZIONI_DEI_MODELLI[c]}" for c in chiavi]
        self._domanda()
        with FinestraScelta(genitore, "Modello della riproduzione casuale", righe, chiavi.index(self.impostazioni["modello_casuale"])) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Modello della riproduzione casuale non cambiato.")
                return
            indice = dialogo.GetSelection()
        self.impostazioni["modello_casuale"] = chiavi[indice]
        self._ricomincia_il_mazzo()
        self._salva_impostazioni()
        genitore.aggiorna("modello_casuale", self._riga_dell_impostazione("modello_casuale"))
        self._riscontro("impostazione_cambiata", f"La riproduzione casuale ora va con il modello {valori.MODELLI_CASUALI[chiavi[indice]]}.")

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
        self._domanda()
        with FinestraScelta(genitore, "Scheda audio", righe, elenco.index(attuale) + 1 if attuale is not None else 0) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Scheda audio non cambiata.")
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

    # L'invito a offrire un caffe' (Gabriele, 4 ottobre 2026, 1.75.0).

    def _invito_alla_donazione(self, genitore, probabilita=20):
        """Il testo lo da' Donazione di GBUtils, o None se il sorteggio non
        passa: una volta su cinque, se non si chiede altro. La finestra e'
        come quella di Tornello, con il suo suono. Restituisce come si e'
        chiusa, wx.ID_YES se si e' aperto PayPal, o None se non si e' aperta."""
        from GBUtils import Donazione

        testo = Donazione(lang="it", probabilita=probabilita, stampa=False)
        if testo is None:
            return None
        self._suono("donazione")
        with DialogoDonazione(genitore, testo) as dialogo:
            return dialogo.ShowModal()

    def _dona(self, genitore):
        """La voce Dona per questo progetto delle impostazioni: l'invito
        compare sempre."""
        if self._invito_alla_donazione(genitore, probabilita=100) == wx.ID_YES:
            self.scrivi("PayPal si apre nel browser: grazie di cuore!")

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
            self._annullato("Eliminazione annullata.")
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
            self._annullato("I marcatori restano dove sono.")
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
        self._domanda()
        with DialogoDiFile(genitore, "Esporta marcatori", defaultDir=os.path.dirname(self.impostazioni.percorso), defaultFile=FILE_DELL_ESPORTAZIONE,
                wildcard=FILTRO_DEI_MARCATORI, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Esportazione annullata.")
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
        self._domanda()
        with DialogoDiFile(genitore, "Importa marcatori", defaultDir=os.path.dirname(self.impostazioni.percorso), wildcard=FILTRO_DEI_MARCATORI,
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Importazione annullata.")
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
        if formati.ha_sottobrani(percorso):
            info = sottobrani.info(percorso)
            numero = sottobrano or (info or {}).get("iniziale") or 1
            durate = sottobrani.durate(percorso)
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
        self._avvisa_l_attesa_del_sid(marker["tempo"])
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
            info = sottobrani.info(brano.percorso) or {}
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
            self._domanda()
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato("Nome del marker non cambiato.")
                return
            nome = " ".join(dialogo.GetValue().split())
        if not nome or nome == marker["nome"]:
            self._annullato("Nome del marker non cambiato.")
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
            ripartito = self.motore.in_pausa
            if ripartito:
                self.motore.vai_a(marker["tempo"])
                self.motore.pausa(False, sfumando=True)
            else:
                self._vai_nel_brano(marker["tempo"])
            self._riscontro("marker_avanti" if avanti else "marker_indietro", f"{marker['nome']}, {durata_lunga(marker['tempo'])}.")
            if ripartito:
                self._riprende_il_video()
            self._avvisa_l_attesa_del_sid(marker["tempo"])
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
        self._riscontro("vai_al_brano", f"Selezione su {self._nome_della_voce(voce)}.")
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
        self._riscontro("chiudi_tutto", f"Chiuso tutto dentro {self._nome_della_voce(voce)}.")

    def _chiudi_la_plancia(self):
        """Maiuscolo con F9 (Gabriele, 4 ottobre 2026): chiude tutti i rami
        della plancia, con tutto quello che hanno dentro; il fuoco va sulla
        voce di primo livello che conteneva quella su cui si era."""
        radice = self.albero.GetRootItem()
        primo = self._voce_corrente()
        while primo.IsOk() and primo != radice and self.albero.GetItemParent(primo) != radice:
            primo = self.albero.GetItemParent(primo)
        for voce in list(self._figli(radice)):
            self.albero.CollapseAllChildren(voce)
        if primo.IsOk() and primo != radice:
            self._seleziona(primo)
        self._riscontro("chiudi_la_plancia", "Chiusa tutta la plancia.")

    def _apri_la_plancia(self):
        """Maiuscolo con F10 (Gabriele, 4 ottobre 2026): apre i Preferiti, i
        Risultati e le playlist con tutto quello che hanno dentro. Questo PC e
        Questa rete restano chiusi: aprire i dischi interi caricava decine di
        migliaia di cartelle, contatore e schedario lavoravano per minuti, e
        la finestra si fermava, con una cacofonia di suoni (collaudo della
        1.83.0; Gabriele ci rinuncia)."""
        radice = self.albero.GetRootItem()
        rami = [v for v in self._figli(radice) if v not in (self.nodo_rete, self.nodo_pc) and self.albero.ItemHasChildren(v)]

        def avvio():
            self._riscontro("apri_la_plancia", "Apro tutta la plancia, tranne Questo PC e Questa rete: ci vuole un po', e un tasto qualsiasi mi ferma.")

        def finito(aperti, voci, fermato, taciuti):
            if fermato:
                return "plancia_aperta", f"Aperti {aperti} rami, {voci} voci; mi fermo qui, gli altri restano chiusi.{taciuti}"
            return "plancia_aperta", f"Aperta tutta la plancia, tranne Questo PC e Questa rete: {al_plurale(aperti, 'ramo', 'rami')}.{taciuti}"

        self._apri_in_blocco(rami, avvio, finito)

    def _apri_tutto(self):
        """F10: apre la voce col fuoco e tutti i rami che ha dentro, a fette
        come Maiuscolo con F10 (Gabriele, 1.83.2): sotto Questo PC ci sono
        dischi interi, e tutto d'un fiato la finestra si fermava."""
        voce = self._ramo_di_lavoro()
        if voce is None:
            self._riscontro("non_disponibile", "Qui non c'è niente da aprire.")
            return
        nome = self._nome_della_voce(voce)

        def avvio():
            self._riscontro("apri_la_plancia", f"Apro tutto dentro {nome}: ci vuole un po', e un tasto qualsiasi mi ferma.")

        def finito(aperti, voci, fermato, taciuti):
            if fermato:
                return "apri_tutto", f"Aperti {aperti} rami, {voci} voci dentro {nome}; mi fermo qui, gli altri restano chiusi.{taciuti}"
            return "apri_tutto", f"Aperto tutto dentro {nome}: {al_plurale(aperti, 'ramo', 'rami')}.{taciuti}"

        self._apri_in_blocco([voce], avvio, finito)

    def _apri_in_blocco(self, rami, avvio, finito):
        """Apre i rami e tutto quello che hanno dentro, fino a MASSIMO_DI_RAMI
        rami e MASSIMO_DI_VOCI voci, un decimo di secondo alla volta: la
        finestra risponde, e un tasto qualsiasi ferma l'apertura. Le
        cartelle vuote e quelle che non si leggono non suonano una per una:
        la fine le conta. avvio() dice l'inizio, con il suo suono, solo se
        il lavoro dura piu' di RITARDO_DELL_AVVIO secondi: quasi sempre
        l'apertura e' istantanea, e i suoni di inizio e di fine si sarebbero
        sovrapposti (Gabriele, 1.83.2); se e' suonato, quello di fine aspetta
        che finisca. finito(aperti, voci, fermato, taciuti) da' (evento,
        frase) della fine."""
        segno = self._apertura_della_plancia = object()
        da_aprire = list(rami)
        aperti, voci, avviato = [0], [0], [False]
        partenza = time.monotonic()
        self._taciuti = {"vuote": 0, "illeggibili": 0}

        def passo():
            if segno is not self._apertura_della_plancia or self._chiusa:
                return
            if not avviato[0] and time.monotonic() - partenza >= RITARDO_DELL_AVVIO:
                avviato[0] = True
                avvio()
            fine = time.monotonic() + 0.1
            self._cedi.set()
            try:
                while da_aprire and aperti[0] < MASSIMO_DI_RAMI and voci[0] < MASSIMO_DI_VOCI and time.monotonic() < fine:
                    ramo = da_aprire.pop(0)
                    if not self.albero.ItemHasChildren(ramo):
                        continue
                    self.albero.Expand(ramo)
                    aperti[0] += 1
                    figli = list(self._figli(ramo))
                    voci[0] += len(figli)
                    da_aprire.extend(figli)
            finally:
                self._cedi.clear()
            if da_aprire and aperti[0] < MASSIMO_DI_RAMI and voci[0] < MASSIMO_DI_VOCI:
                wx.CallLater(1, passo)
                return
            self._apertura_della_plancia = None
            evento, frase = finito(aperti[0], voci[0], bool(da_aprire), self._frase_dei_taciuti())
            # Le cartelle rimaste senza niente da suonare spariscono adesso.
            self._aggiorna_cartelle()
            if avviato[0]:
                self._riscontro_dopo(evento, frase)
            else:
                self._riscontro(evento, frase)

        # La prima fetta subito: un ramo piccolo finisce qui, con il suo solo
        # suono di fine.
        passo()

    def _ferma_l_apertura(self):
        self._apertura_della_plancia = None
        taciuti = self._frase_dei_taciuti()
        self._riscontro("annullamento", f"Apertura della plancia fermata: i rami aperti fin qui restano aperti.{taciuti}")
        self._aggiorna_cartelle()

    def _frase_dei_taciuti(self):
        """Quante cartelle vuote e illeggibili ha trovato un'apertura in
        blocco, che non hanno suonato una per una; e la fine del silenzio."""
        taciuti, self._taciuti = self._taciuti or {}, None
        parti = []
        if taciuti.get("vuote"):
            parti.append(f"{al_plurale(taciuti['vuote'], 'cartella', 'cartelle')} senza niente da suonare")
        if taciuti.get("illeggibili"):
            parti.append(f"{al_plurale(taciuti['illeggibili'], 'cartella', 'cartelle')} che non si leggono")
        return f" Trovate {' e '.join(parti)}." if parti else ""

    def _apri_ramo(self, voce, con_i_marker=True):
        """Apre la voce e tutti i rami che ha dentro, caricandoli, tutto
        d'un fiato, fino a MASSIMO_DI_RAMI rami e MASSIMO_DI_VOCI voci: serve
        a J e K, che aprono una playlist per suonarla. Torna (rami aperti,
        vero se si e' fermato prima). Senza con_i_marker restano chiusi i
        brani che dentro hanno solo marker."""
        aperti, voci = 0, 0
        da_aprire = [voce]
        with wx.BusyCursor():
            while da_aprire and aperti < MASSIMO_DI_RAMI and voci < MASSIMO_DI_VOCI:
                ramo = da_aprire.pop(0)
                if not self.albero.ItemHasChildren(ramo):
                    continue
                dati = self._dati(ramo) or {}
                if not con_i_marker and dati.get("tipo") in ("brano", "file", "sottobrano") and not (
                        dati["tipo"] != "sottobrano" and self._ha_sottobrani(dati["brano"])):
                    continue
                self.albero.Expand(ramo)
                aperti += 1
                figli = list(self._figli(ramo))
                voci += len(figli)
                da_aprire.extend(figli)
        return aperti, bool(da_aprire)

    # F1, F2, F3.

    def _stampa(self, evento, righe, porta_il_fuoco=True):
        """Scrive nella console un testo lungo, riga per riga, con l'ora solo
        in fondo, e ci porta il fuoco con il cursore sulla prima riga; con
        porta_il_fuoco falso il fuoco resta dov'e'."""
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
        inizio = len("".join(r + "\n" for r in self._righe[:-len(righe)]))
        if porta_il_fuoco:
            self._porta_il_cursore(inizio)
        else:
            # Il fuoco resta dov'e'; tornando nella console si arriva qui.
            self._posizione_della_console = self._nella_console(inizio)

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
        """Il testo di un file del programma, o None se non si legge: la
        console lo dice con il suono dell'errore (tappa 9)."""
        try:
            with open(percorsi.percorso_risorsa(nome), encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            self._riscontro("errore", f"Non riesco a leggere {nome}: {e.strerror or e}.")
            return None

    def _comando_cerca_in_console(self):
        """Il campo della ricerca nella console, con le sue istruzioni come
        commenti; se il testo non si capisce lo spiega e lo ripropone."""
        testo = self._cercato_in_console
        while True:
            self._domanda()
            with FinestraFiltro(self, "Cerca nella console", testo, ISTRUZIONI_DELLA_CONSOLE) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self._annullato("Ricerca nella console annullata.")
                    return
                # Andare a capo vale come uno spazio; gli spazi dentro il
                # testo contano, perche' si cerca cosi' com'e'.
                testo = " ".join(dialogo.testo.splitlines()).strip()
            if not testo:
                self._annullato("Ricerca nella console annullata: il testo è vuoto.")
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
        elif evento.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and evento.GetModifiers() == wx.MOD_NONE:
            self._riscontro("non_disponibile", "Nella console non c'è una ricerca: la barra rovesciata ne apre una.")
        else:
            evento.Skip()

    def _elenco_dei_tasti(self):
        """F12: scrive nella console la guida rapida del manuale, cioe' i
        tasti, i comandi della ricerca e del filtro e i colori, una riga per
        voce, cosi' la documentazione resta una sola; porta il fuoco nella
        console, con il cursore sulla prima riga (1.72.0)."""
        manuale = self._leggi_risorsa("manuale.html")
        if manuale is None:
            return
        righe = guida_rapida(manuale)
        if not righe:
            self._riscontro("errore", "Nel manuale non trovo la guida rapida.")
            return
        self._stampa("elenco_dei_tasti", righe)

    def _manuale(self):
        """F1: apre manuale.html nel browser predefinito, dove si naviga per
        titoli; la console lo dice (1.72.0, prima lo scriveva nella console).
        Se il file manca o non si apre, lo dice con il suono dell'errore."""
        nome = "manuale.html"
        percorso = percorsi.percorso_risorsa(nome)
        if not os.path.isfile(percorso):
            self._riscontro("errore", f"Non riesco ad aprire {nome}: il file non c'è.")
            return
        try:
            os.startfile(percorso)  # noqa: S606 - il manuale del programma, da un percorso fisso, nel browser predefinito
        except OSError as e:
            self._riscontro("errore", f"Non riesco ad aprire {nome}: {e.strerror or e}.")
            return
        self._riscontro("manuale", "Il manuale si apre nel browser.")

    def _changelog(self):
        novita = self._leggi_risorsa("CHANGELOG.md")
        if novita is not None:
            self._stampa("changelog", ["Novità di MeTeOra", *righe_del_changelog(novita)])

    def _crediti(self):
        righe = [
            "Crediti di MeTeOra",
            f"MeTeOra {version.VERSION} del {version.DATE}.",
            f"Autori: {version.AUTHOR}.",
            "MeTeOra è formato da tre parole italiane, una dedica di Gabriele alla sua ragazza Ginevra.",
            "Riproduzione: libmpv, dal progetto mpv, con FFmpeg e libopenmpt.",
            "SID del Commodore 64: libsidplayfp, con l'emulazione reSIDfp.",
            "Durate dei SID: il database Songlengths della High Voltage SID Collection.",
            "MIDI: FluidSynth, con il banco di suoni FluidR3 GM quando lo scarichi.",
            "Musica delle console: libgme, Game Music Emu.",
            "Sottotitoli letti: accessible_output2.",
            "Effetti sonori: Acusticator, della libreria GBUtils di Gabriele.",
            "Durate, lettura e scrittura dei tag dei file audio: mutagen.",
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
            self._riscontro_dopo("errore", f"Non trovo più {percorso}, che suonava l'ultima volta.")
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
        # Un video ripreso in pausa apre la sua finestra con X, non subito:
        # il fuoco resta nella plancia (tappa 9).
        self._video_in_attesa = percorso
        self.motore.suona(percorso, sottobrano, inizio=posizione, in_pausa=True)
        voce = self._trova_voce_che_suona()
        if voce is not None:
            self.albero.EnsureVisible(voce)
            self._seleziona(voce)
        self._aggiorna_etichette()
        # Dopo il suono dell'avvio, che parte un attimo prima.
        self._riscontro_dopo("ripresa_all_avvio", f"Riprendo da dove eri: {percorso}, in pausa a {tempo(posizione)}. X riparte.")

    # L'uscita.

    @staticmethod
    def _salva_all_uscita(salva, cosa, non_salvati):
        try:
            salva()
        except OSError as e:
            non_salvati.append(f"{cosa}: {e.strerror or e}")

    def _alla_chiusura(self, evento):
        if self._chiusa:
            evento.Skip()
            return
        self._chiusa = True
        self._braille.svuota()
        if self._ricerca is not None:
            self._ricerca.ferma()
        self.impostazioni["ripresa"] = self._stato_da_riprendere()
        non_salvati = []
        self._salva_all_uscita(self.archivio.salva, "le playlist", non_salvati)
        if self.marcatori.modificato:
            self._salva_all_uscita(self.marcatori.salva, "i marker", non_salvati)
        self.contatore.ferma()
        self.schedario.ferma()
        for lavoro in (self._lettura, self._passata):
            if lavoro is not None:
                lavoro.ferma()
        if self._video is not None:
            self._video.Destroy()
            self._video = None
        self._salva_all_uscita(self.schedario.salva, "lo schedario delle durate e dei tag", non_salvati)
        self._salva_all_uscita(self.impostazioni.salva, "le impostazioni", non_salvati)
        self.motore.chiudi()
        if non_salvati:
            # La console sta per sparire: lo dice una finestra, prima di
            # chiudere (tappa 9).
            suoni.suona("errore", self.impostazioni["volume_effetti"])
            wx.MessageBox(f"MeTeOra non è riuscito a salvare {'; '.join(non_salvati)}.", "MeTeOra, uscita", wx.OK | wx.ICON_ERROR, self)
        # L'invito a offrire un caffe', una volta su cinque, per ultimo:
        # tutto e' gia' salvato e la musica e' ferma. Un guasto dell'invito
        # non deve impedire l'uscita (1.75.0).
        try:
            self._invito_alla_donazione(self)
        except Exception:  # noqa: BLE001 - l'uscita viene prima dell'invito
            traceback.print_exc()
        # Il suono dell'uscita si ascolta intero prima che il processo finisca.
        suoni.suona("uscita", self.impostazioni["volume_effetti"], sync=True)
        evento.Skip()
