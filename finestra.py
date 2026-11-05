# MeTeOra, la finestra principale: plancia dei comandi, console e cruscotto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.2.0 i sottobrani dei SID, nella 1.3.0 il loop A-B, nella 1.4.0 il cestino, Nella 1.102.2 la voce del volume dice del livello originale e del limitatore. Nella 1.102.3 rubberband nei crediti. Nella 1.102.4 l'invito a offrire un caffe' non compare piu' alla chiusura: resta la voce delle impostazioni. Nella 1.103.0 le statistiche, con la loro voce nella plancia e Maiuscolo con F7. Nella 1.104.0 la pulizia all'avvio, le statistiche salvate subito, il file del crash svuotato ogni minuto e Rinomina file che porta con se' anche il punto da riprendere e lo storico. Nella 1.104.2 la stessa cartella con le maiuscole diverse e' una cartella sola. Nella 1.105.0 Dove sono, sull'apostrofo: tempo, brano e lista di cio' che suona, nella console e alla sintesi e al braille dei sottotitoli, dove la riga nuova prende il posto di quella di prima. Nella 1.105.1 la riga In riproduzione chiama la lista come Dove sono: Risultati e Preferiti, non piu' cartella Risultati e playlist Preferiti. Nella 1.109.0 Ordina e Mescola nel menu della playlist e dei Preferiti, e il ramo Playlist ricostruito tiene aperti anche i brani e i sottobrani che lo erano. Nella 1.110.0 la durata residua, su Maiuscolo con l'apostrofo: trascorso, mancante e totale di cio' che suonera' la plancia, con la percentuale ascoltata e l'ora di fine, nella console e alla sintesi e al braille dei sottotitoli. Nella 1.111.0 lo stato della selezione detto a NVDA nella plancia, con la sua voce delle impostazioni (issue 21). Nella 1.112.0 la pulizia all'avvio riconosce il disco di ogni lettera, e salta quelle usate da dischi diversi o con un disco che non riconosce, e tutte se il file dei dischi non si legge; Riconosci questo disco nel menu delle unita' contese, indicato dalla riga della pulizia, e il disco di una lettera guardato ogni volta che MeTeOra ne usa un file; le voci di una lettera diventata contesa, o riconosciuta a mano, mentre la pulizia lavorava restano; infine Riconosci questo disco chiede conferma con il conto delle voci, la Sentinella dice subito, con il suo suono, la lettera che rende contesa, e la riga della pulizia suggerisce Riconosci questo disco solo per le lettere usate da dischi diversi. Nella 1.113.0 l'importazione delle playlist M3U, M3U8 e PLS di altri programmi, con il comando Importa playlist, da Apri file e da Windows. Nella 1.113.1 l'etichetta di un file con piu' sottobrani somma solo le durate note e dice quanti sono senza durata, invece di cadere in errore (issue 24). Nella 1.113.3 la voce Barra dei comandi per il mouse dice il suo nome nell'errore, non quello dell'Inseguimento della plancia, e l'Inseguimento passa il suo (issue 26). Nella 1.113.5 le statistiche si scrivono solo se sono cambiate davvero, al piu' ogni mezz'ora, oltre che all'avvio e all'uscita. Nella 1.116.0 le schede audio che arrivano e se ne vanno, come le cuffie Bluetooth: PortAudio riletto, la scheda scelta lasciata e ritrovata, e il brano che riparte quando la sua uscita si perde. Nella 1.116.1 il tempo delle statistiche va alla scheda che suona davvero, non a quella scelta che manca.. Nella 1.116.2 il suono di piu' e meno fatto al volo, che dice il volume con la sua frequenza. Nella 1.116.3 i comandi che si muovono nel brano rispondono anche da fermi, ricaricandolo in pausa all'inizio (issue 39). Nella 1.119.0 gli speaker Cast fra le destinazioni, con la lista unica e il filtro, e le statistiche delle uscite (tappa 15 b, issue 31). Nella 2.0.6 il rinfresco dei Preferiti non porta piu' il fuoco su Playlist (issue 29). Nella 2.1.0 le voci Entra al PUB e Chiedi aiuto al PUB (issue 30). Nella 2.2.0 il segnalibro, su H (issue 37). Nella 2.4.0 i registri degli errori in Chiedi aiuto al PUB e i sostenitori nei crediti. Nella 2.7.0 le aperture in blocco in disparte, senza limiti e anche su Questo PC e Questa rete, con i comandi tutti su F9 (tappa 17). Nella 2.7.1 la precedenza ai tasti sul lavoro in disparte. Nella 2.7.2 i lettori di rete chiusi all'uscita. Nella 2.7.3 i tasti funzione nelle tabelle COMANDI_DEI_TASTI_FUNZIONE e INTERRUTTORI, lette dalla prova della guida rapida, e le righe del cruscotto nell'ordine della regola
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
# nella 1.55.0 velocita', tono, equalizzatore e dissolvenza incrociata, con i tasti, le voci delle impostazioni e il passaggio fra due brani (tappa 4, issue 15). Nella 1.58.0 la dissolvenza anche su stop, pausa, X da capo e marker, i suoni al volo dell'equalizzatore e il loop a giro su Maiuscolo+X; nella 1.58.1 F e H scambiati. Nella 1.59.0 la riproduzione casuale con Maiuscolo+N (issue 17). Nella 1.60.0 W anche dalla fine, con il meno. Nella 1.60.1 O abbassa e P alza. Nella 1.61.0 i modelli della riproduzione casuale, con il mazzo. Nella 1.62.0 l'attesa del SID dopo un salto. Nella 1.63.0 il video: Maiuscolo con F1, F2, F3, F5 e F6, la finestra del video e i sottotitoli letti (tappa 7). Nella 1.64.0 il ramo Questa rete. Nella 1.65.0 i MIDI con FluidSynth e il banco dei suoni (tappa 8). Nella 1.66.0 la musica delle console, con i sottobrani come i SID. Nella 1.66.36 le rifiniture della tappa 9: riscontro per ogni tasto e annullamento, domande con Esc, fuoco che non si sposta da solo. Nella 1.67.0 Rinomina file; nella 1.67.4 solo i banchi General MIDI. Nella 1.69.0 i tag: F11, Maiuscolo+F11 e il sottomenu Tag. Nella 1.71.0 la barra rovesciata cerca nel ramo, Ctrl con la barra rovesciata ovunque. Nella 1.72.0 F1 apre manuale.html nel browser e F12 scrive la sua guida rapida. Nella 1.73.0 Ctrl con la barra rovesciata cerca anche in rete, dopo i dischi. Nella 1.74.0, con la riproduzione casuale, B sceglie a caso e Z torna ai brani suonati prima. Nella 1.75.0 l'invito a offrire un caffe', alla chiusura e dalle impostazioni. Nella 1.76.0 Maiuscolo con Canc manda nel cestino una cartella vuota, e dove il cestino non c'e' lo dice. Nella 1.77.0 F11 scrive i dettagli dei contenitori, e i conti delle cartelle si rifanno dopo il cestino. Nella 1.77.1 il contatore e l'apertura dei rami di rete con la lettura protetta. Nella 1.79.0 Maiuscolo con F9 chiude tutta la plancia e Maiuscolo con F10 la apre tutta. Nella 1.80.0 i sottotitoli a immagini e quelli impressi, letti con il riconoscimento dei caratteri di Windows. Nella 1.82.0 il testo del karaoke, con Maiuscolo con F2, e le voci Dove vanno sottotitoli e karaoke, Testo del karaoke e Anticipo del karaoke. Nella 1.83.0 la barra braille a blocchi, con le celle e il tempo minimo di lettura. Nella 1.83.1 Maiuscolo con F10 lascia chiuso Questo PC, e la plancia molto aperta non ferma piu' la finestra. Nella 1.83.2 F10 a fette, e i suoni delle aperture che non si sovrappongono. Nella 1.84.0 la proposta dell'aggiornamento, il suo avanzamento e la chiusura per aggiornarsi. Nella 1.85.0 i crediti con la licenza e le licenze dei componenti. Nella 1.85.5 i rami di rete che si riprovano sempre. Nella 1.86.0 Maiuscolo con F12 spegne e riaccende i tasti rapidi a carattere. Nella 1.87.0 la barra dei comandi per il mouse. Nella 1.88.0 anche sopra il video, con la linea del tempo. Nella 1.88.1 F2 scrive solo le versioni recenti. Nella 1.89.0 i problemi interni anche nel registro degli errori. Nella 1.90.0 le copie dei dati che non riescono. Nella 1.91.0 i file aperti da Windows, il trascinamento e le associazioni dei formati. Nella 1.92.0 i file lunghi riprendono dal punto lasciato. Nella 1.93.0 i capitoli, con virgola e punto e nella plancia. Nella 1.94.0 la ripetizione del brano e della lista, con Maiuscolo con V. Nella 1.95.0 il timer di spegnimento, con Maiuscolo con S. Nella 1.96.0 il volume uniforme con ReplayGain. Nella 1.96.11 le correzioni della revisione: la catena degli errori, il mazzo della ripetizione, la sfumatura del timer fra due brani e durante la domanda. Nella 1.98.0 la plancia nativa a selezione singola, con la selezione multipla tenuta da MeTeOra: NVDA non legge piu' la voce di prima. Nella 1.98.1 il fuoco su un capitolo resta al rinfresco dei marker. Nella 1.99.0 il caricatore di Vulkan di scorta, nei crediti.

"""La finestra di MeTeOra.

Tre aree, nell'ordine di tabulazione: la plancia dei comandi (F5), un albero;
la console (F6), dove scorrono i riscontri di ogni azione; il cruscotto
(F7), che mostra i tasti del contesto da cui ci si e' arrivati.
I tasti a lettera valgono in tutta la finestra e li intercetta EVT_CHAR_HOOK,
prima dei controlli: per questo l'albero non ha la ricerca per iniziale. Un
carattere senza comando lo dice, con il suo suono, e all'albero non arriva.
Ctrl con F12 li spegne e Maiuscolo con F12 li riaccende (1.86.0, 2.0.2): spenti,
lettere, cifre e segni vanno ai controlli, e l'albero cerca la voce per iniziale.
Il brano in riproduzione e la voce selezionata sono due cose distinte: la
riproduzione non sposta mai la selezione; lo fa F8, su richiesta.
"""

import collections
import contextlib
import copy
import ctypes
import datetime
import math
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

import GBsintesi
import wx

import accessibilita
import associazioni
import dettagli
import formati
import importazione
import karaoke
import lettore_di_rete
import lingua
import lontano
import marcatori
import midi
import ocr
import percorsi
import posizioni
import pub
import pulizia
import questa_rete
import questo_pc
import registro
import schede_audio
import sintesi
import sottobrani
import sottotitoli_ocr
import statistiche
import suoni
import tag
import trasmissione
import valori
import version
from barra import BarraDeiComandi
from contatore import Contatore
from dialoghi import (
    DialogoConferma,
    DialogoDonazione,
    DialogoTesto,
    FinestraAggiornamento,
    FinestraImpostazioni,
    FinestraMarcatori,
    FinestraScelta,
    FinestraStatistiche,
)
from esploratore import Esploratore
from filtro import COMMENTO, ErroreFiltro, Filtro, modello_della_console
from impostazioni import PREDEFINITE, Impostazioni
from lingua import _, ngettext, plurale
from marcatori import Marcatori
from motore import DURATA_SID_PREDEFINITA, VOLUME_MASSIMO, durata_del_sottobrano, sottobrano_risolto
from playlist import CRITERI, Archivio, Brano, Coda, Playlist
from precedenza import PRECEDENZA_AI_TASTI, Cedi
from ricerca import (
    UNITA_CD,
    UNITA_DI_RETE,
    AlberoDeiRisultati,
    NonRisponde,
    Ricerca,
    errore_di_rete,
    in_rete,
    leggi_in_rete,
    senza_annidati,
    tipo_di_unita,
)
from schedario import Schedario, credibile
from valori import AREE, ErroreValore, leggi_tempo, leggi_tempo_nel_brano, secondi_da_leggere, tempo
from video import FinestraVideo

FILE_PLAYLIST = "MeTeOra - Playlist.json"
FILE_IMPOSTAZIONI = "MeTeOra - Impostazioni.json"
FILE_SCHEDARIO = "MeTeOra - Schedario.json"
FILE_MARCATORI = "MeTeOra - Marcatori.json"
FILE_POSIZIONI = "MeTeOra - Posizioni.json"
FILE_STATISTICHE = "MeTeOra - Statistiche.json"
# I dischi che la pulizia all'avvio riconosce (1.112.0).
FILE_DISCHI = "MeTeOra - Dischi.json"
# I file dei dati con le copie nella cartella copie, una per sessione (1.90.0):
# lo schedario no, perche' si rifa' da solo rileggendo i file; dalla
# 1.112.0 anche i dischi.
FILE_CON_LE_COPIE = (FILE_PLAYLIST, FILE_MARCATORI, FILE_IMPOSTAZIONI, FILE_POSIZIONI, FILE_STATISTICHE, FILE_DISCHI)
# Ogni quanti millisecondi scatta l'orologio delle statistiche, e quanti scatti
# fanno il giro del minuto (1.103.0). Dalla 1.113.5 il loro file si scrive
# all'avvio, a fine pulizia, alla rinomina, all'azzeramento e all'uscita, e in
# mezzo solo se sono cambiate davvero e al piu' ogni tanti minuti: meno
# scritture sul disco, e un crollo perde al piu' quei minuti (Gabriele).
GIRO_DELLE_STATISTICHE = 1000
GIRI_IN_UN_MINUTO = 60
MINUTI_FRA_I_SALVATAGGI_DELLE_STATISTICHE = 30
# Ogni quanti millisecondi si guarda il punto del file lungo che suona, e
# ogni quanti giri si scrive il file delle posizioni (1.92.0).
GIRO_DELLE_POSIZIONI = 5000
GIRI_PER_SALVARE = 12
# Il nome proposto per l'esportazione dei marcatori, e il filtro dei dialoghi
# che la scrivono e la leggono.
FILE_DELL_ESPORTAZIONE = "MeTeOra - Marcatori esportati.json"
FILTRO_DEI_MARCATORI = _("Marcatori di MeTeOra (*.json)") + "|*.json"
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
# Quanti rami al massimo apre J, che apre una playlist tutta d'un fiato per
# suonarla. Fino alla 2.6 valeva anche per F10, che dalla 2.7.0 e' Maiuscolo
# con F9 e non ha limiti: legge il disco in disparte.
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
# Da quante etichette cambiate in un rinfresco in su si scrivono a pezzi, e
# quanto dura al massimo un pezzo: con 12.600 cartelle aperte SetItemText una
# per una chiede 1,4 secondi, e con Freeze il Thaw della plancia con 140 mila
# voci teneva ferma la finestra fino a quattro secondi (banco della 2.7.0).
ETICHETTE_A_PEZZI = 50
PEZZO_DELLE_ETICHETTE = 0.03
# Le aperture in blocco, Maiuscolo e Alt con F9, dicono il loro inizio, con il
# suono, solo se durano piu' di tanti secondi (1.83.2).
RITARDO_DELL_AVVIO = 0.4
# Quanti risultati della ricerca si mostrano alla volta.
PAGINA_DEI_RISULTATI = 1000

# I modificatori dei tasti a carattere, issue 38 (2.0.0): da solo il tasto
# riporta il valore del suo controllo, con i limiti; con Ctrl va indietro,
# abbassa o spegne; con Maiuscolo va avanti, alza o accende; con Ctrl e
# Maiuscolo torna al valore predefinito; con Alt va al massimo e con Ctrl e
# Alt al minimo. Gli interruttori dei tasti funzione seguono la stessa
# regola, Ctrl spegne e Maiuscolo accende, mentre il tasto da solo resta al
# suo comando (Gabriele, collaudo della 2.0.0).
SOLO = wx.MOD_NONE
CTRL = wx.MOD_CONTROL
MAIUSCOLO = wx.MOD_SHIFT
CTRL_MAIUSCOLO = wx.MOD_CONTROL | wx.MOD_SHIFT
ALT = wx.MOD_ALT
CTRL_ALT = wx.MOD_CONTROL | wx.MOD_ALT
# I tasti funzione ed Esc, con i modificatori: (tasto, modificatori) -> il
# metodo del comando. La prova della guida rapida li legge da qui, cosi' una
# combinazione nuova senza la sua riga non passa (2.7.3). Maiuscolo con F7
# apre le statistiche da tutta la finestra (Gabriele, 1.103.0). F9 con i
# modificatori (2.7.0): Maiuscolo apre il ramo con tutto dentro, Ctrl lo
# chiude, Alt apre tutta la plancia, Ctrl e Alt la chiude, Ctrl e Maiuscolo
# fermano l'apertura in corso; Maiuscolo con F10 resta a Windows, che apre il
# menu della voce.
COMANDI_DEI_TASTI_FUNZIONE = {
    (wx.WXK_F1, SOLO): "_manuale", (wx.WXK_F2, SOLO): "_changelog", (wx.WXK_F3, SOLO): "_crediti", (wx.WXK_F4, SOLO): "_f4",
    (wx.WXK_F5, SOLO): "_vai_alla_plancia", (wx.WXK_F6, SOLO): "_vai_alla_console", (wx.WXK_F7, SOLO): "_vai_al_cruscotto",
    (wx.WXK_F7, MAIUSCOLO): "_comando_statistiche", (wx.WXK_F8, SOLO): "_vai_al_brano",
    (wx.WXK_F9, SOLO): "_comando_stato_del_ramo", (wx.WXK_F9, CTRL): "_chiudi_tutto", (wx.WXK_F9, MAIUSCOLO): "_apri_tutto",
    (wx.WXK_F9, CTRL_MAIUSCOLO): "_ferma_l_apertura", (wx.WXK_F9, ALT): "_apri_la_plancia", (wx.WXK_F9, CTRL_ALT): "_chiudi_la_plancia",
    (wx.WXK_F10, SOLO): "_f10", (wx.WXK_F11, SOLO): "_comando_leggi_i_tag", (wx.WXK_F11, MAIUSCOLO): "_comando_modifica_i_tag",
    (wx.WXK_F12, SOLO): "_elenco_dei_tasti", (wx.WXK_ESCAPE, SOLO): "Close",
}
# Gli interruttori, con la regola della issue 38: Ctrl spegne, Maiuscolo
# accende, e il tasto da solo resta al suo comando (Gabriele, collaudo della
# 2.0.0). Sottotitoli, traccia audio e rapporto dell'immagine sono passati a
# D, G e I.
INTERRUTTORI = {wx.WXK_F1: "_metti_il_video", wx.WXK_F5: "_metti_lo_schermo_intero", wx.WXK_F8: "_metti_l_inseguimento",
    wx.WXK_F12: "_metti_i_tasti_rapidi"}
# I tasti a carattere: (carattere, modificatori) -> comando, una famiglia per
# tasto dove la regola si applica. Ctrl con Alt e' anche AltGr: resta libero
# sui tasti che con AltGr scrivono un segno, come E per l'euro, e su N, che
# con Ctrl e Alt avvia NVDA (Gabriele, 3 novembre 2026). Le combinazioni con
# Ctrl e Alt che non sono qui vanno a Windows, come Ctrl con C per copiare.
TASTI = {
    # Il cuore del lettore resta com'era, anche con i modificatori: Z, X, C,
    # V e B (Gabriele, 3 novembre 2026).
    ("z", SOLO): "precedente",
    ("x", SOLO): "play",
    ("x", MAIUSCOLO): "loop",
    # Ctrl e Maiuscolo con X: la lista della voce Scheda audio, da tutta la
    # finestra, con le schede del PC, le cuffie Bluetooth e gli speaker Cast
    # (Gabriele, 2.6.0).
    ("x", CTRL_MAIUSCOLO): "scheda_audio",
    ("c", SOLO): "pausa",
    ("v", SOLO): "stop",
    # La ripetizione a giro (Gabriele, 1.94.0).
    ("v", MAIUSCOLO): "ripetizione",
    ("b", SOLO): "successivo",
    ("w", SOLO): "vai_a_tempo",
    # Dove sono: tempo, brano e lista di cio' che suona (Gabriele, tappa 14 b).
    ("'", SOLO): "dove_sono",
    # La durata residua, Maiuscolo con l'apostrofo: il punto interrogativo
    # della tastiera italiana (Gabriele, tappa 14 d).
    ("'", MAIUSCOLO): "durata_residua",
    ("\\", SOLO): "ricerca",
    # La barra verticale: Maiuscolo con la barra rovesciata.
    ("\\", MAIUSCOLO): "filtro",
    # T mette un marker o lo rinomina, Maiuscolo con T li toglie tutti (issue 12).
    ("t", SOLO): "marker",
    ("t", MAIUSCOLO): "togli_i_marker",
    # H, il segnalibro, uno per tutto MeTeOra (Gabriele, issue 37, 2.2.0): da
    # solo lo dice, con Maiuscolo ci va e suona, con Ctrl lo toglie, con Ctrl
    # e Maiuscolo lo mette dove si e', riscrivendo quello di prima.
    ("h", SOLO): "segnalibro",
    ("h", MAIUSCOLO): "vai_al_segnalibro",
    ("h", CTRL): "togli_il_segnalibro",
    ("h", CTRL_MAIUSCOLO): "metti_il_segnalibro",
    # Q, il punto del brano: un salto indietro e avanti, gli ultimi secondi e l'inizio.
    ("q", SOLO): "posizione",
    ("q", CTRL): "indietro",
    ("q", MAIUSCOLO): "avanti",
    ("q", ALT): "verso_la_fine",
    ("q", CTRL_ALT): "all_inizio",
    # E, accanto a Q: i passi dei suoi salti.
    ("e", SOLO): "passi_dei_salti",
    ("e", CTRL): "passo_indietro",
    ("e", MAIUSCOLO): "passo_avanti",
    ("e", CTRL_MAIUSCOLO): "passi_predefiniti",
    # R, accanto a T: quanti marker, e toglierli prima e dopo il punto.
    ("r", SOLO): "conta_i_marker",
    ("r", CTRL): "togli_i_marker_prima",
    ("r", MAIUSCOLO): "togli_i_marker_dopo",
    # Y, i marker del brano: con Alt l'ultimo, come Gabriele propone nella issue.
    ("y", SOLO): "marker_attuale",
    ("y", CTRL): "marker_precedente",
    ("y", MAIUSCOLO): "marker_successivo",
    ("y", ALT): "ultimo_marker",
    ("y", CTRL_ALT): "primo_marker",
    # A, la velocita'.
    ("a", SOLO): "velocita",
    ("a", CTRL): "velocita_giu",
    ("a", MAIUSCOLO): "velocita_su",
    ("a", CTRL_MAIUSCOLO): "velocita_normale",
    ("a", ALT): "velocita_massima",
    ("a", CTRL_ALT): "velocita_minima",
    # S, il timer di spegnimento (Gabriele, 1.95.0).
    ("s", SOLO): "timer_attuale",
    ("s", CTRL): "togli_il_timer",
    ("s", MAIUSCOLO): "timer",
    ("s", ALT): "timer_a_fine_brano",
    # D, G e I, il video: sottotitoli letti, traccia audio e rapporto
    # dell'immagine, senza i giri di Maiuscolo con F2, F3 e F6.
    ("d", SOLO): "sottotitoli",
    ("d", CTRL): "sottotitoli_precedenti",
    ("d", MAIUSCOLO): "sottotitoli_successivi",
    ("d", ALT): "ultimi_sottotitoli",
    ("d", CTRL_ALT): "sottotitoli_spenti",
    # F, il tono, di un semitono.
    ("f", SOLO): "tono",
    ("f", CTRL): "tono_giu",
    ("f", MAIUSCOLO): "tono_su",
    ("f", CTRL_MAIUSCOLO): "tono_normale",
    ("f", ALT): "tono_massimo",
    ("f", CTRL_ALT): "tono_minimo",
    ("g", SOLO): "traccia_audio",
    ("g", CTRL): "traccia_audio_precedente",
    ("g", MAIUSCOLO): "traccia_audio_successiva",
    ("g", ALT): "ultima_traccia_audio",
    ("g", CTRL_ALT): "prima_traccia_audio",
    ("i", SOLO): "rapporto",
    ("i", CTRL): "rapporto_precedente",
    ("i", MAIUSCOLO): "rapporto_successivo",
    ("i", CTRL_MAIUSCOLO): "rapporto_del_video",
    ("i", ALT): "ultimo_rapporto",
    ("i", CTRL_ALT): "primo_rapporto",
    # U, la banda scelta dell'equalizzatore; O, accanto, il suo guadagno; P,
    # accanto ancora, tutte le bande.
    ("u", SOLO): "banda",
    ("u", CTRL): "banda_precedente",
    ("u", MAIUSCOLO): "banda_successiva",
    ("u", ALT): "ultima_banda",
    ("u", CTRL_ALT): "prima_banda",
    ("o", SOLO): "guadagno",
    ("o", CTRL): "banda_giu",
    ("o", MAIUSCOLO): "banda_su",
    ("o", CTRL_MAIUSCOLO): "azzera_la_banda",
    ("o", ALT): "guadagno_massimo",
    ("o", CTRL_ALT): "guadagno_minimo",
    ("p", SOLO): "curva",
    ("p", CTRL_MAIUSCOLO): "azzera_le_bande",
    # J, le playlist, che si aprono e suonano.
    ("j", SOLO): "playlist",
    ("j", CTRL): "playlist_precedente",
    ("j", MAIUSCOLO): "playlist_successiva",
    ("j", ALT): "ultima_playlist",
    ("j", CTRL_ALT): "prima_playlist",
    # K, accanto a L: la durata della dissolvenza.
    ("k", SOLO): "durata_della_dissolvenza",
    ("k", CTRL): "dissolvenza_piu_breve",
    ("k", MAIUSCOLO): "dissolvenza_piu_lunga",
    ("k", CTRL_MAIUSCOLO): "durata_predefinita",
    ("k", ALT): "dissolvenza_massima",
    ("k", CTRL_ALT): "dissolvenza_minima",
    ("l", SOLO): "dissolvenza",
    ("l", CTRL): "spegni_la_dissolvenza",
    ("l", MAIUSCOLO): "accendi_la_dissolvenza",
    # N, la riproduzione casuale; Alt con N suona subito un brano a caso.
    ("n", SOLO): "riproduzione_casuale",
    ("n", CTRL): "spegni_la_casuale",
    ("n", MAIUSCOLO): "accendi_la_casuale",
    ("n", ALT): "casuale",
    # M, il volume: con Ctrl e Alt a zero, che fa da muto, e con Ctrl e
    # Maiuscolo quello di prima del massimo o dello zero (Gabriele, 3 novembre 2026).
    ("m", SOLO): "volume",
    ("m", CTRL): "volume_giu",
    ("m", MAIUSCOLO): "volume_su",
    ("m", CTRL_MAIUSCOLO): "volume_di_prima",
    ("m", ALT): "volume_massimo",
    ("m", CTRL_ALT): "volume_minimo",
    # La virgola, accanto a M: i capitoli degli audiolibri e dei film (1.93.0).
    (",", SOLO): "capitolo",
    (",", CTRL): "capitolo_precedente",
    (",", MAIUSCOLO): "capitolo_successivo",
    (",", ALT): "ultimo_capitolo",
    (",", CTRL_ALT): "primo_capitolo",
    # Il punto: il passo del volume.
    (".", SOLO): "passo_volume",
    (".", CTRL): "passo_volume_giu",
    (".", MAIUSCOLO): "passo_volume_su",
    (".", CTRL_MAIUSCOLO): "passo_volume_predefinito",
    (".", ALT): "passo_volume_massimo",
    (".", CTRL_ALT): "passo_volume_minimo",
    # Il piu', da solo: la finestra delle impostazioni (Gabriele, 2.6.0). Ctrl
    # con la virgola, il tasto di tanti programmi, e' il capitolo precedente.
    ("+", SOLO): "impostazioni",
}
# I segni che la tastiera italiana scrive con il Maiuscolo, e che Windows puo'
# dare al posto del loro tasto: valgono come il tasto con il Maiuscolo.
SEGNI_COL_MAIUSCOLO = {"?": "'", "|": "\\", ":": ".", ";": ","}
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

# I nomi dei tasti senza carattere, nelle statistiche (1.103.0).
NOMI_DEI_TASTI = {
    wx.WXK_UP: "Freccia su", wx.WXK_DOWN: "Freccia giù", wx.WXK_LEFT: "Freccia sinistra", wx.WXK_RIGHT: "Freccia destra",
    wx.WXK_PAGEUP: "Pagina su", wx.WXK_PAGEDOWN: "Pagina giù", wx.WXK_HOME: "Inizio", wx.WXK_END: "Fine",
    wx.WXK_RETURN: "Invio", wx.WXK_NUMPAD_ENTER: "Invio", wx.WXK_ESCAPE: "Esc", wx.WXK_TAB: "Tab", wx.WXK_BACK: "Backspace",
    wx.WXK_DELETE: "Canc", wx.WXK_INSERT: "Ins", wx.WXK_SPACE: "Barra spaziatrice", wx.WXK_WINDOWS_MENU: "Applicazioni",
    **{getattr(wx, f"WXK_F{n}"): f"F{n}" for n in range(1, 13)},
}
# I segni che nelle statistiche hanno un nome loro, prima di quelli dei
# tasti senza comando.
SEGNI_DELLE_STATISTICHE = {"\\": "barra rovesciata", "|": "barra verticale", "-": "meno"}


def nome_del_carattere(carattere, modificatori=SOLO):
    """Il nome di un tasto a carattere nelle statistiche: X, Maiuscolo con N,
    Ctrl e Maiuscolo con A, più."""
    if carattere.isalpha() and carattere not in NOMI_DEI_SEGNI:
        nome = carattere.upper()
    else:
        nome = SEGNI_DELLE_STATISTICHE.get(carattere) or NOMI_DEI_SEGNI.get(carattere, carattere)
    prefisso = [n for bit, n in ((wx.MOD_CONTROL, "Ctrl"), (wx.MOD_ALT, "Alt"), (wx.MOD_SHIFT, "Maiuscolo")) if modificatori & bit]
    return f"{' e '.join(prefisso)} con {nome}" if prefisso else nome


def carattere_del_tasto(evento):
    """(carattere, modificatori) di un tasto che scrive un carattere, con il
    carattere minuscolo, anche con Ctrl e Alt; None per gli altri tasti. Le
    lettere vengono dal codice del tasto, che con Ctrl non cambia; la barra
    rovesciata con Ctrl puo' arrivare come 0x1C; i segni del Maiuscolo, come
    il punto interrogativo, valgono come il loro tasto con il Maiuscolo."""
    modificatori = evento.GetModifiers()
    codice = evento.GetKeyCode()
    if ord("A") <= codice <= ord("Z"):
        return chr(codice).lower(), modificatori
    unicode = evento.GetUnicodeKey()
    if unicode == 0x1C:
        return "\\", modificatori
    if unicode == wx.WXK_NONE or unicode <= 32 or not chr(unicode).isprintable():
        return None
    carattere = chr(unicode).lower()
    if carattere in SEGNI_COL_MAIUSCOLO:
        return SEGNI_COL_MAIUSCOLO[carattere], modificatori | wx.MOD_SHIFT
    return carattere, modificatori


TASTI_COMUNI = [
    _("La regola dei tasti a lettera: il tasto da solo dice il valore del suo controllo, con i limiti, nella console e alla sintesi e al braille dei sottotitoli; "
    "con Ctrl va indietro, abbassa o spegne; con Maiuscolo va avanti, alza o accende; con Ctrl e Maiuscolo torna al valore predefinito; con Alt va al massimo, con Ctrl e Alt al minimo."),
    _("X suona la voce selezionata, riprende dalla pausa o fa ripartire da capo il brano che suona già; C pausa, V stop, Z e B brano precedente e successivo. "
    "Maiuscolo con V la ripetizione, a giro: del brano, della lista, spenta. Maiuscolo con X, a giro: punto A del loop sul brano selezionato, poi punto B, poi toglie il loop."),
    _("N la riproduzione casuale: Ctrl la spegne, Maiuscolo la accende, e con lei B sceglie a caso e Z torna ai brani suonati prima; Alt con N suona subito un brano a caso. "
    "S il timer di spegnimento: Ctrl lo toglie, Maiuscolo lo chiede in minuti, Alt lo mette alla fine del brano."),
    _("L'apostrofo dice dove sei: il tempo del brano che suona, il suo nome, il posto nella lista e quello che c'è di particolare, come la pausa; "
    "lo scrive nella console e lo manda alla sintesi e al braille dei sottotitoli, senza spostare il fuoco."),
    _("Maiuscolo con l'apostrofo dice la durata residua: quanto manca e quanto è passato di ciò che suonerà, anche nei rami aperti dopo nella plancia, "
    "la percentuale ascoltata e l'ora in cui finisce; anche lei va nella console, alla sintesi e al braille dei sottotitoli."),
    _("H il segnalibro, uno per tutto MeTeOra, che resta anche chiudendo: Ctrl con H lo toglie, Maiuscolo con H ci torna, aprendo la plancia fino al brano "
    "e suonandolo da lì, Ctrl e Maiuscolo con H lo mettono sul brano che suona, al punto in cui è."),
    _("Q il punto del brano: Ctrl e Maiuscolo indietro e avanti di un salto, Alt agli ultimi secondi, Ctrl e Alt all'inizio. "
    "E i passi dei salti: Ctrl e Maiuscolo chiedono quello indietro e quello avanti, Ctrl e Maiuscolo insieme li riportano ai predefiniti. W va a un tempo."),
    _("M il volume: Ctrl e Maiuscolo lo abbassano e lo alzano di un passo, Ctrl e Maiuscolo insieme lo riportano a quello di prima del massimo o dello zero, "
    "Alt lo porta al massimo, Ctrl e Alt a zero, che fa da muto. Il punto: il passo del volume."),
    _("La virgola, i capitoli degli audiolibri e dei film: Ctrl e Maiuscolo il precedente e il successivo, Alt l'ultimo, Ctrl e Alt il primo; "
    "Ctrl con la virgola, oltre i primi secondi di un capitolo, torna al suo inizio."),
    _("A la velocità, F il tono, di un semitono: Ctrl abbassa, Maiuscolo alza, Ctrl e Maiuscolo insieme tornano al normale, Alt al massimo, Ctrl e Alt al minimo."),
    _("U la banda dell'equalizzatore: Ctrl e Maiuscolo la precedente e la seguente, Alt l'ultima, Ctrl e Alt la prima. "
    "O il suo guadagno, di un dB, e Ctrl e Maiuscolo insieme la azzerano; P tutte le bande, e Ctrl e Maiuscolo insieme le azzerano."),
    _("L la dissolvenza incrociata, con cui sfumano i cambi di brano, lo stop, la pausa, X da capo e i marker: Ctrl la spegne, Maiuscolo la accende. "
    "K la sua durata, di mezzo secondo alla volta."),
    _("Il video: Ctrl con F1 lo spegne, Maiuscolo con F1 lo accende; Ctrl con F5 lo rimette in finestra, Maiuscolo con F5 a schermo intero. D i sottotitoli letti, G la traccia audio, I il rapporto dell'immagine: "
    "Ctrl e Maiuscolo il precedente e il seguente, Alt l'ultimo, Ctrl e Alt il primo, che per i sottotitoli è spenti."),
    _("J la playlist: Ctrl e Maiuscolo aprono e suonano la precedente e la successiva, Alt l'ultima, Ctrl e Alt la prima; le cifre da 1 a 0 le prime dieci playlist."),
    _("Nella plancia Backspace chiude il ramo in cui sei e risale di un livello, Maiuscolo con Backspace risale di colpo all'unità o alla playlist, Preferiti compresi, e chiude i rami al suo interno."),
    _("T mette un marker dove sei, o rinomina quello su cui sei; Maiuscolo con T li toglie tutti. Y il marker su cui sei o quello prima: Ctrl e Maiuscolo il precedente e il successivo, "
    "Alt l'ultimo, Ctrl e Alt il primo. R quanti marker ha il brano: Ctrl e Maiuscolo tolgono quelli prima e quelli dopo. Maiuscolo con le cifre da 1 a 0 va ai primi dieci marker del brano della plancia."),
    _("F4 mette nei Preferiti il brano selezionato. F5 plancia, F6 console, F7 cruscotto, Maiuscolo con F7 le statistiche, F8 porta la selezione e il fuoco della plancia sul brano in riproduzione, Ctrl con F8 la sgancia e Maiuscolo con F8 ce la tiene agganciata, "
    "F9 dice se il ramo col fuoco è aperto, e quante voci ha aperte dentro: Ctrl con F9 lo chiude e Maiuscolo con F9 lo apre con tutto quello che ha dentro, "
    "Ctrl e Maiuscolo con F9 fermano un'apertura, Alt con F9 apre tutta la plancia e Ctrl e Alt con F9 la chiude; mentre si apre puoi navigare; "
    "F11 legge i tag del brano selezionato, o i dettagli di una cartella, di un'unità o di una playlist, e Maiuscolo con F11 apre il menu dei tag."),
    _("Barra rovesciata: nella console cerca nella console, altrove nel ramo della plancia in cui sei, e da Apri file, Statistiche o Impostazioni in tutto MeTeOra; Ctrl con la barra rovesciata cerca in tutto MeTeOra, anche dalla console. "
    "Barra verticale: il filtro della playlist o dei Preferiti in cui sta la plancia, anche dalla console."),
    _("F1 apre il manuale nel browser; F12 scrive nella console la guida rapida dei tasti, F2 le novità e F3 i crediti, sempre nella console. Esc esce salvando tutto. "
    "Il più apre le impostazioni, Ctrl e Maiuscolo con X la lista della scheda audio, con le cuffie Bluetooth e gli speaker Cast."),
    _("Ctrl con F12 spegne i tasti rapidi a carattere e Maiuscolo con F12 li riaccende: spenti, lettere, cifre e segni vanno alla plancia, che salta alla voce che comincia con ciò che scrivi; "
    "i tasti funzione, Esc e le combinazioni con Ctrl e con Alt restano. Gli interruttori dei tasti funzione seguono la regola: Ctrl spegne, Maiuscolo accende, il tasto da solo fa il suo lavoro."),
]
# Chi sostiene MeTeOra con una donazione, nei crediti di F3, nell'ordine in
# cui arriva: i nomi li dice Gabriele, via via (2.4.0).
SOSTENITORI = ("Massimo Diana",)
# Le righe del cruscotto proprie di ogni tipo di voce della plancia.
TASTI_DEL_CONTESTO = {
    # Traduttori: per ogni tipo di voce della plancia, il nome che completa la riga Tasti per..., come i Risultati della ricerca, e la riga dei suoi tasti.
    "risultati": (_("i Risultati della ricerca"), _("Invio, Applicazioni o Spazio: menu con Riproduci, Salva come playlist, Nuova ricerca, che cerca in tutto MeTeOra, e Ferma la ricerca.")),
    "altri": (_("la voce che mostra altri risultati"), _("Invio mostra i risultati seguenti.")),
    "gruppo_risultati": (_("un ramo dei Risultati"), _("Freccia destra lo apre: i risultati stanno come stavano, sotto la loro playlist o lungo il percorso della loro cartella. Invio, Applicazioni o Spazio: menu con Salva come playlist.")),
    "preferiti": (_("i Preferiti"), _("Invio, Applicazioni o Spazio: menu con Riproduci, Filtro e, se c'è un filtro, Togli il filtro; Ordina, un sottomenu con i criteri, poi, dopo un riordino, Ordine di prima, e in fondo Inverti l'ordine; e Mescola. "
        "Barra verticale: il filtro. Canc su un loro brano lo toglie dai Preferiti.")),
    "radice_playlist": (_("il ramo Playlist"), _("Invio, Applicazioni o Spazio: menu con Nuova playlist e Importa playlist, che importa le playlist M3U, M3U8 e PLS di altri programmi.")),
    "playlist": (_("una playlist"), _("Invio, Applicazioni o Spazio: menu con Riproduci, Filtro, Togli il filtro se c'è un filtro, Rinomina, Ordina, Mescola ed Elimina. "
        "Ordina è un sottomenu con i criteri, poi, dopo un riordino, Ordine di prima, e in fondo Inverti l'ordine. Barra verticale: il filtro. Canc elimina la playlist, dopo una conferma.")),
    "brano": (_("un brano di una playlist"), _("Invio, Applicazioni o Spazio: menu con Riproduci, Sposta su, giù, in cima e in fondo, Saltato, Togli dalla playlist, Aggiungi ai preferiti, Rinomina file, Leggi i tag e Tag per i formati che li hanno, e Manda nel cestino. "
        "Canc toglie il brano dalla playlist, Maiuscolo con Canc manda il file nel cestino. Un SID o un file delle console con più sottobrani, o un brano con dei marker, si apre con freccia destra.")),
    "pc": (_("Questo PC"), _("Freccia destra mostra le unità. Invio, Applicazioni o Spazio: menu con Aggiorna.")),
    "rete": (_("Questa rete"), _("Freccia destra mostra i percorsi di rete, i computer della rete e il comando per aggiungere un percorso. Invio, Applicazioni o Spazio: menu con Aggiungi un percorso di rete e Aggiorna.")),
    "computer_della_rete": (_("i computer della rete"), _("Freccia destra li cerca, in disparte: può volerci qualche secondo. Invio, Applicazioni o Spazio: menu con Cerca di nuovo.")),
    "computer": (_("un computer della rete"), _("Freccia destra mostra le sue cartelle condivise. Invio, Applicazioni o Spazio: menu con Aggiorna.")),
    "attesa": (_("una ricerca in corso"), _("Aspetta: la voce sparisce quando la ricerca finisce.")),
    "unita": (_("un'unità"), _("Freccia destra mostra il contenuto. Invio, Applicazioni o Spazio: menu con Riproduci, Crea playlist da qui, Aggiungi alla playlist, Aggiorna e, "
        "se la pulizia all'avvio la salta per il disco che risponde, Riconosci questo disco, che prima chiede conferma dicendo quante voci la pulizia toglierà.")),
    "cartella": (_("una cartella"), _("Freccia destra mostra il contenuto. Invio, Applicazioni o Spazio: menu con Riproduci, Crea playlist da qui, Aggiungi alla playlist e Aggiorna. "
        "Maiuscolo con Canc la manda nel cestino, se è vuota.")),
    "file": (_("un file"), _("Invio, Applicazioni o Spazio: menu con Riproduci, Aggiungi alla playlist, Aggiungi ai preferiti, Rinomina file, Leggi i tag e Tag per i formati che li hanno, e Manda nel cestino. "
        "Maiuscolo con Canc manda il file nel cestino. Un SID o un file delle console con più sottobrani, o un file con dei marker, si apre con freccia destra.")),
    "sottobrano": (_("un sottobrano di un SID o di un file delle console"), _("Invio, Applicazioni o Spazio: menu con Riproduci, Aggiungi alla playlist e Aggiungi ai preferiti. Se ha dei marker, freccia destra li mostra.")),
    "capitolo": (_("un capitolo"), _("X, Invio, Applicazioni o Spazio suonano il file da questo capitolo. Ctrl e Maiuscolo con la virgola, mentre suona, vanno al capitolo precedente e successivo.")),
    "marker": (_("un marker"), _("Invio rinomina il marker, Canc lo elimina, X fa come sul suo brano. Applicazioni o Spazio: menu con Vai al marker, che suona il brano da lì, Rinomina ed Elimina.")),
    "comando": (_("un comando"), _("Invio esegue il comando.")),
}
# Le voci della finestra delle impostazioni, in ordine: chiave -> (etichetta,
# participio per dire che non e' cambiata; None per le voci che fanno
# un'azione invece di cambiare un valore).
def _stesso_posto(a, b):
    """Vero se due (playlist, brano, sottobrano) sono lo stesso posto: la
    stessa playlist e lo stesso brano, non due uguali, e lo stesso numero."""
    return a[0] is b[0] and a[1] is b[1] and a[2] == b[2]


def _minuti(numero):
    return plurale(numero, "{n} minuto", "{n} minuti")


def _frase_della_ripetizione(ripetizione):
    """Il riscontro della ripetizione, una chiave di valori.RIPETIZIONI (1.94.0)."""
    return FRASI_DELLA_RIPETIZIONE[ripetizione]


def _frase_della_casuale(accesa, modello):
    if accesa:
        return _("Riproduzione casuale accesa: {modello}.").format(modello=valori.MODELLI_CASUALI[modello])
    return _("Riproduzione casuale spenta: a fine brano si va avanti in ordine.")


# Le righe della lista dei modelli della riproduzione casuale.
# Il timer di spegnimento (1.95.0): i minuti proposti la prima volta, e la
# sfumatura quando scade, in secondi, a passi in millesimi.
TIMER_PROPOSTO = 30
# Il passo di Ctrl e Maiuscolo con K, la durata della dissolvenza (issue 38).
PASSO_DELLA_DISSOLVENZA = 0.5
# Le famiglie dei tasti che con uno speaker Cast non valgono: velocita',
# tono, equalizzatore e dissolvenza. Il tasto da solo, dopo il valore, lo
# ricorda (Gabriele, collaudo della 2.6.0).
SOLO_SUL_PC = ("velocita", "tono", "banda", "dissolvenza")
SFUMATURA_DEL_TIMER = 20.0
PASSO_DELLA_SFUMATURA = 100
FRASI_DEL_VOLUME_UNIFORME = {
    "spento": _("Volume uniforme spento: ogni file suona con il volume con cui è registrato."),
    "brano": _("Volume uniforme per brano: i file con i tag ReplayGain si avvicinano allo stesso volume; quelli forti scendono, e quelli piani salgono fin dove i loro picchi lo permettono."),
    "album": _("Volume uniforme per album: ogni disco con i tag ReplayGain suona allo stesso volume, e dentro il disco restano le differenze volute."),
}
FRASI_DELLA_RIPETIZIONE = {
    "spenta": _("Ripetizione spenta."),
    "brano": _("Ripetizione del brano: quando finisce, ricomincia."),
    "lista": _("Ripetizione della lista: dopo l'ultimo brano, si riparte dal primo."),
}
SPIEGAZIONI_DEI_MODELLI = {
    "totale": _("ogni volta un brano qualsiasi, mai lo stesso due volte di fila"),
    "una_volta": _("ogni brano suona una volta, poi la riproduzione finisce"),
    "a_giro": _("ogni brano suona una volta, poi si rimescola e si ricomincia"),
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
MIDI_DA_PREPARARE = _("I MIDI restano da preparare: si può fare anche dalle impostazioni, con Banco dei suoni MIDI.")
# Da quanti secondi d'attesa in su la console dice che il SID, il MIDI o il
# brano della console si prepara.
ATTESA_DA_DIRE = 1.5
# Quanto si aspetta, al piu', che il motore riapra in pausa il brano fermo per
# un comando che si muove nel brano (issue 39, 1.116.3).
ATTESA_DEL_RISVEGLIO = 3.0
# All'avvio, quanto si aspetta lo speaker Cast scelto prima di dire che non
# c'e', in millesimi: di solito la ricerca lo trova in meno di un secondo.
ATTESA_DELLO_SPEAKER = 4000


def riga_dello_speaker(voce):
    """La riga di uno speaker Cast nella lista delle destinazioni, da una
    voce di trasmissione.Ricerca.apparecchi: "Cucina, speaker Cast, Google
    Home Speaker"; un gruppo di Google Home "ovunque, gruppo Cast"."""
    if voce["tipo"] == trasmissione.TIPO_GRUPPO:
        return _("{nome}, gruppo Cast").format(nome=voce["nome"])
    if voce["modello"]:
        return _("{nome}, speaker Cast, {modello}").format(nome=voce["nome"], modello=voce["modello"])
    return _("{nome}, speaker Cast").format(nome=voce["nome"])


# I rapporti dell'immagine di I, dal primo all'ultimo (issue 38): il valore per mpv e
# il nome da leggere. -1 e' quello del file.
# Traduttori: il rapporto dell'immagine che ha il video stesso, come in Rapporto dell'immagine: quello del video, 1 di 4.
RAPPORTI = (("-1", _("quello del video")), ("16:9", "16:9"), ("4:3", "4:3"), ("2.33:1", "21:9"))
# I nomi delle lingue piu' comuni nelle tracce, dai codici di tre lettere.
# Traduttori: i nomi delle lingue delle tracce audio e dei sottotitoli, come in 2 di 3, italiano, ac3.
LINGUE = {"ita": _("italiano"), "eng": _("inglese"), "fre": _("francese"), "fra": _("francese"), "ger": _("tedesco"), "deu": _("tedesco"), "spa": _("spagnolo"),
    "por": _("portoghese"), "jpn": _("giapponese"), "chi": _("cinese"), "zho": _("cinese"), "rus": _("russo"), "dut": _("olandese"), "nld": _("olandese"),
    "swe": _("svedese"), "pol": _("polacco"), "kor": _("coreano"), "ara": _("arabo"), "und": None}


def _descrivi_traccia(traccia, indice, totale):
    """Una traccia audio o di sottotitoli da leggere: "2 di 3, italiano,
    Commento del regista, ac3"."""
    lingua = traccia.get("lang")
    # Traduttori: il numero della traccia e quante sono, come in Traccia audio 2 di 3, italiano, ac3.
    parti = [_("{numero} di {totale}").format(numero=indice + 1, totale=totale), LINGUE.get(lingua, lingua), traccia.get("title"), traccia.get("codec")]
    return ", ".join(str(parte) for parte in parti if parte)


def midi_in_disparte(lavoro, al_termine):
    """Fa lavoro() in un filo a parte e passa il risultato ad al_termine:
    gli scaricamenti e la ricerca dei banchi non fermano la finestra."""
    threading.Thread(target=lambda: al_termine(lavoro()), name="MeTeOra, preparazione dei MIDI", daemon=True).start()


def _frase_del_video(acceso):
    if acceso:
        return _("Video acceso: i video si vedono in una finestra sopra MeTeOra.")
    return _("Video spento: dei video si sente solo l'audio.")


VOCI_DELLE_IMPOSTAZIONI = {
    # Traduttori: il nome della voce, e il participio che chiude la frase di Esc nel suo campo: Volume della musica non cambiato.
    "volume": (_("Volume della musica"), _("cambiato")),
    "passo_volume": (_("Passo del volume"), _("cambiato")),
    "volume_effetti": (_("Volume degli effetti"), _("cambiato")),
    "replaygain": (_("Volume uniforme (ReplayGain)"), _("cambiato")),
    "scheda_audio": (_("Scheda audio"), _("cambiata")),
    "passo_indietro": (_("Salto indietro di Ctrl+Q"), _("cambiato")),
    "passo_avanti": (_("Salto avanti di Maiuscolo+Q"), _("cambiato")),
    "velocita": (_("Velocità"), _("cambiata")),
    "tono": (_("Tono"), _("cambiato")),
    "bande": (_("Equalizzatore"), _("cambiato")),
    "dissolvenza": (_("Dissolvenza"), _("cambiata")),
    "casuale": (_("Riproduzione casuale (Ctrl+N, Maiuscolo+N)"), _("cambiata")),
    "modello_casuale": (_("Modello della riproduzione casuale"), _("cambiato")),
    "ripetizione": (_("Ripetizione (Maiuscolo+V)"), _("cambiata")),
    "video": (_("Video (Ctrl+F1, Maiuscolo+F1)"), _("cambiato")),
    "sottotitoli": (_("Sottotitoli letti (D)"), _("cambiati")),
    "sintesi": (_("Sintesi di sottotitoli e karaoke"), _("cambiata")),
    "destinazione": (_("Dove vanno sottotitoli e karaoke"), _("cambiato")),
    "karaoke": (_("Testo del karaoke"), _("cambiato")),
    "anticipo_karaoke": (_("Anticipo del karaoke"), _("cambiato")),
    "celle_braille": (_("Celle della barra braille"), _("cambiate")),
    "lettura_minima": (_("Tempo minimo di lettura in braille"), _("cambiato")),
    "banco_midi": (_("Banco dei suoni MIDI"), _("cambiato")),
    "insegui": (_("Inseguimento della plancia (Ctrl+F8, Maiuscolo+F8)"), _("cambiato")),
    "ripresa_oltre": (_("Punto lasciato dei file lunghi"), _("cambiato")),
    # La lingua di MeTeOra, fra quelle con un catalogo (3.0.0).
    "lingua": (_("Lingua"), _("cambiata")),
    "caratteri": (_("Dimensioni dei caratteri"), _("cambiate")),
    "colori_testo": (_("Colori dei caratteri"), _("cambiati")),
    "colori_sfondo": (_("Colori dello sfondo"), _("cambiati")),
    "barra_dei_comandi": (_("Barra dei comandi per il mouse"), _("cambiata")),
    "stato_della_selezione": (_("Stato della selezione per lo screen reader"), _("cambiato")),
    "righe_della_console": (_("Righe della console"), _("cambiate")),
    "salva_console": (_("Salva console"), None),
    "marcatori": (_("Marcatori"), None),
    "importa_marcatori": (_("Importa marcatori"), None),
    "associazioni": (_("Associazioni dei formati"), None),
    "impressi": (_("Sottotitoli impressi"), _("cambiati")),
    "dona": (_("Dona per questo progetto"), None),
    # Il PUB, il gruppo di supporto, accanto al dono (issue 30, 2.1.0).
    "entra_al_pub": (_("Entra al PUB (gruppo di supporto)"), None),
    "chiedi_aiuto_al_pub": (_("Chiedi aiuto al PUB"), None),
}
# Come si leggono i sottotitoli impressi nel video, 1.80.0: le righe della scelta.
MODI_DEGLI_IMPRESSI = {
    # Traduttori: completano la frase I sottotitoli impressi ora sono letti al volo, ...
    "al_volo": _("letti al volo, mentre il video suona, con circa mezzo secondo di ritardo"),
    "passata": _("letti prima, con una passata che salva accanto al video un file usato le volte dopo"),
}
# Il testo del karaoke, 1.82.0: le righe della scelta.
MODI_DEL_KARAOKE = {
    # Traduttori: come si mostra il testo del karaoke, una riga alla volta.
    "riga": _("per riga"),
    "strofa": _("per strofa, dove il file le segna; altrimenti per riga"),
}
# Il titolo della traccia che fa un file scritto dalla passata.
TITOLO_DELLA_PASSATA = _("Sottotitoli impressi")
# Per _aggiorna_la_lettura: la traccia scelta la dicono le tracce.
_DALLE_TRACCE = object()


def _traccia_della_passata(tracce):
    """La traccia del file di una passata dei sottotitoli impressi, o None."""
    return next((t for t in tracce["sub"] if t.get("title") == TITOLO_DELLA_PASSATA), None) if tracce else None
# L'ultima riga delle istruzioni di ogni campo.
REGOLA_DEL_DOLLARO = _("Le righe che cominciano con il dollaro non contano: scrivi nell'ultima riga.")
# La prova della scheda audio degli effetti: un centesimo di secondo di
# silenzio alla frequenza del mixer, 44100, che la apre senza suonare niente,
# anche con il volume degli effetti a zero.
SILENZIO_DI_PROVA = 441
# Perche' la scheda audio scelta non e' quella in uso, come lo dice la riga
# della finestra delle impostazioni: si usa l'automatica, e la scelta resta.
# Traduttori: la scheda audio scelta, come in Scheda audio: Cuffie USB, non c'è: uso quella automatica.
SCHEDA_MANCANTE = _("non c'è")
# Traduttori: la scheda audio scelta, come in Scheda audio: Cuffie USB, non si apre: uso quella automatica.
SCHEDA_CHE_NON_SI_APRE = _("non si apre")
# Quanto si aspetta dopo l'ultimo cambio delle uscite audio, prima di
# rileggerle (1.116.0), in millesimi: connettendo delle cuffie Bluetooth
# Windows aggiunge l'uscita e poi ne fa la predefinita, e gli avvisi
# arrivano a grappoli.
ATTESA_DELLE_USCITE = 2000


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


# Per quanti millisecondi si raccolgono i file aperti da Windows prima di
# suonarli: Esplora risorse apre piu' file selezionati lanciando una copia per
# file, e insieme fanno una lista sola (1.91.0).
ATTESA_DEI_FILE_DA_WINDOWS = 400


class _Trascinamento(wx.FileDropTarget):
    """I file e le cartelle trascinati sulla finestra (1.91.0)."""

    def __init__(self, finestra):
        super().__init__()
        self._finestra = finestra

    def OnDropFiles(self, _x, _y, nomi):
        wx.CallAfter(self._finestra.apri_dall_esterno, list(nomi), "trascinamento")
        return True


# Quante righe del changelog scrive F2, a versioni intere (Gabriele, 1.88.1).
RIGHE_DEL_CHANGELOG = 50
CHANGELOG_SU_GITHUB = "https://github.com/GabrieleBattaglia/MeTeOra/blob/main/CHANGELOG.md"


# Oltre quanti secondi di un capitolo la virgola torna al suo inizio, invece
# che al capitolo prima, come nei lettori (1.93.0).
RITORNO_AL_CAPITOLO = 3.0


def frase_del_capitolo(numero, totale, titolo, secondi, dal=False):
    """Capitolo 3 di 12: Il titolo, 23:10. Con dal, per il file fatto
    partire da li': Dal capitolo 3 di 12: Il titolo, 23:10."""
    if dal and titolo:
        return _("Dal capitolo {numero} di {totale}: {titolo}, {tempo}").format(numero=numero, totale=totale, titolo=titolo, tempo=tempo(secondi))
    if dal:
        return _("Dal capitolo {numero} di {totale}, {tempo}").format(numero=numero, totale=totale, tempo=tempo(secondi))
    if titolo:
        return _("Capitolo {numero} di {totale}: {titolo}, {tempo}").format(numero=numero, totale=totale, titolo=titolo, tempo=tempo(secondi))
    return _("Capitolo {numero} di {totale}, {tempo}").format(numero=numero, totale=totale, tempo=tempo(secondi))


def capitolo_attuale(elenco, posizione):
    """L'indice del capitolo in cui cade posizione, in secondi: il mezzo
    secondo in piu' tiene dentro un capitolo appena raggiunto con un salto,
    che il lettore puo' dare un attimo prima del suo inizio."""
    return max((i for i, (secondi, _titolo) in enumerate(elenco) if secondi <= posizione + 0.5), default=0)


def novita_recenti(righe, massimo=RIGHE_DEL_CHANGELOG):
    """Le righe del changelog delle versioni piu' recenti, a versioni intere,
    finche' non superano massimo righe; almeno la versione piu' recente. Torna
    (righe, tagliato), tagliato vero se ne sono rimaste fuori."""
    versioni, prima = [], []
    for riga in righe:
        if riga.startswith("Versione "):
            versioni.append([riga])
        elif versioni:
            versioni[-1].append(riga)
        else:
            prima.append(riga)
    tenute = list(prima)
    for numero, versione in enumerate(versioni):
        if numero and len(tenute) + len(versione) > massimo:
            return tenute, True
        tenute += versione
    return tenute, False


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
    return plurale(n, "{n} brano", "{n} brani")


# Quante voci saltate la console elenca una per una, dopo l'importazione di
# una playlist M3U o PLS; le altre si contano soltanto (Gabriele, 1.113.0).
MASSIMO_DELLE_VOCI_SALTATE = 20


def frase_delle_saltate(scartate):
    """Le voci saltate di una playlist importata, contate per motivo:
    Saltate 3 voci: 2 file che non ci sono, 1 indirizzo in rete. Con un
    motivo solo il numero non si ripete: Saltate 2 voci: file che non ci sono."""
    if not scartate:
        return ""
    motivi = importazione.conta_i_motivi(scartate)
    if len(motivi) == 1:
        motivo, quante = motivi[0]
        elenco = importazione.motivo(motivo, quante)
    else:
        elenco = ", ".join(importazione.motivo(motivo, quante, numero=True) for motivo, quante in motivi)
    # Traduttori: motivi e' l'elenco dei motivi per cui le voci della playlist si saltano, come 2 indirizzi in rete, 1 cartella.
    return ngettext("Saltata {n} voce: {motivi}.", "Saltate {n} voci: {motivi}.", len(scartate)).format(n=len(scartate), motivi=elenco)


def righe_delle_saltate(scartate, massimo=MASSIMO_DELLE_VOCI_SALTATE):
    """Una riga per ogni voce saltata, con il motivo, fino a massimo; poi
    quante altre ce ne sono."""
    righe = [_("Saltata {voce}: {motivo}.").format(voce=voce.leggibile, motivo=importazione.motivo(voce.motivo)) for voce in scartate[:massimo]]
    altre = len(scartate) - massimo
    if altre == 1:
        righe.append(_("E un'altra voce saltata."))
    elif altre > 1:
        # Traduttori: sempre piu' di una voce; una sola ha la sua frase, E un'altra voce saltata.
        righe.append(plurale(altre, "E altre {n} voci saltate.", "E altre {n} voci saltate."))
    return righe


def frase_delle_tenute(tenute):
    """Le voci delle radici che non hanno risposto, tenute senza controllo
    come nella pulizia all'avvio: Tenute senza controllo 30 voci di F:, che
    non risponde."""
    if not tenute:
        return ""
    quante, radici = sum(tenute.values()), sorted(tenute)
    # Traduttori: l'ultima unita' di un elenco, come in F:, G: e H:.
    elenco = radici[0] if len(radici) == 1 else _("{prime} e {ultima}").format(prime=", ".join(radici[:-1]), ultima=radici[-1])
    voci = ngettext("Tenuta senza controllo {n} voce", "Tenute senza controllo {n} voci", quante).format(n=quante)
    # Traduttori: voci e' Tenute senza controllo 30 voci, radici le unita' che non rispondono, come F: e G:.
    return ngettext("{voci} di {radici}, che non risponde.", "{voci} di {radici}, che non rispondono.", len(radici)).format(voci=voci, radici=elenco)


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
    riga = _("Problema interno nel motore: {messaggio}").format(messaggio=_breve(testo.splitlines()[0] if testo else ""))
    passi = [p for p in _PASSO_NEL_TESTO.finditer(testo) if _passo_nostro(p.group(1))]
    if passi:
        # Traduttori: dove e' successo un problema interno: il file del codice, il numero della riga e la funzione.
        riga += _(", in {file} alla riga {numero}, {funzione}").format(file=os.path.basename(passi[-1].group(1)), numero=passi[-1].group(2), funzione=passi[-1].group(3))
    return riga + "."


def riga_del_problema(tipo, valore, traccia):
    """Una riga sola per un problema interno: che cosa e' successo e dove,
    nel codice di MeTeOra se ci e' passato, altrimenti nell'ultimo punto."""
    passi = traceback.extract_tb(traccia) if traccia else []
    nostri = [p for p in passi if _passo_nostro(p.filename)]
    passo = (nostri or passi or [None])[-1]
    testo = _("Problema interno: {tipo}").format(tipo=tipo.__name__)
    # Anche un messaggio che non si lascia scrivere non deve fermare la riga.
    messaggio = ""
    with contextlib.suppress(Exception):
        messaggio = _breve(str(valore))
    if messaggio:
        testo += f", {messaggio}"
    if passo is not None:
        # Traduttori: dove e' successo un problema interno: il file del codice, il numero della riga e la funzione.
        testo += _(", in {file} alla riga {numero}, {funzione}").format(file=os.path.basename(passo.filename), numero=passo.lineno, funzione=passo.name)
    return testo + "."


# Le istruzioni in cima ai campi dei filtri e delle ricerche, scritte come
# righe di commento, che cominciano con il dollaro e non contano.
_GRAMMATICA_DEL_FILTRO = [
    _("Spazio: tutti i termini insieme, come rob hubbard. Andare a capo vale come uno spazio."),
    _("Barra verticale: l'uno o l'altro, come hubbard|galway."),
    _("Meno davanti a un termine: escluso, come -remix."),
    _("Asterisco: qualsiasi testo, come comm*do. Cancelletto: una o più cifre, come vol#."),
    _('Virgolette: la sequenza esatta, spazi compresi, come "last ninja".'),
    _("Maiuscole e accenti non contano. Un termine senza comando cerca nel nome del file e nei tag."),
    _("I comandi sono una lettera, un segno fra < > = <= >= e un valore:"),
    # Traduttori: le lettere, i segni e i valori dopo l'uguale sono i comandi del filtro, e restano come sono.
    _("t tempo, come t<=3:00 o t>90."),
    _("d dimensione, come d>5m o d<700k."),
    _("y anno, come y<1990."),
    _("r sottobrani dei SID e della musica delle console, come r>1."),
    _("Questi solo con l'uguale:"),
    # Traduttori: le lettere, i segni e i valori dopo l'uguale sono i comandi del filtro, e restano come sono.
    _("k tipo: k=sid, k=audio, k=video, k=tracker, k=midi, k=chip, o un'estensione come k=flac."),
    _("a autore, come a=hubbard."),
    _("n titolo, come n=commando."),
    _("l album."),
    _("g genere."),
    _("p percorso della cartella, come p=c64music."),
    _("s saltato: s=1 i brani saltati, s=0 gli altri."),
    REGOLA_DEL_DOLLARO,
]
ISTRUZIONI_DEL_FILTRO = [_("Puoi usare questi comandi per comporre il filtro."), *_GRAMMATICA_DEL_FILTRO]
ISTRUZIONI_DELLA_RICERCA = [_("Puoi usare questi comandi per comporre la ricerca, in tutte le playlist, in tutte le unità e nei percorsi di rete aggiunti a mano."), *_GRAMMATICA_DEL_FILTRO]
# Dove cerca Ctrl con la barra rovesciata, la ricerca in tutto MeTeOra.
OVUNQUE = "nelle playlist, nei dischi e in rete"
ISTRUZIONI_DELLA_CONSOLE = [
    _("Puoi usare questi segni per comporre la ricerca nella console."),
    _("Il testo si cerca così com'è, spazi compresi; maiuscole e minuscole non contano. Andare a capo vale come uno spazio."),
    _("Asterisco: qualsiasi testo nella stessa riga, come non*suonare."),
    _("Cancelletto: una o più cifre, come volume #."),
    _('Virgolette: la sequenza esatta, maiuscole comprese, come "SID".'),
    _("I messaggi finiscono con l'ora: 07:13 trova ciò che è accaduto alle 7 e 13, e 07:# tutta l'ora delle 7; trovano anche i tempi dei brani che contengono quelle cifre, come 1:07:13."),
    _("Invio, dalla console, passa all'occorrenza seguente."),
    REGOLA_DEL_DOLLARO,
]
ISTRUZIONI_DELLE_STATISTICHE = [
    _("Puoi usare questi segni per comporre la ricerca nelle statistiche."),
    _("Il testo si cerca così com'è, spazi compresi; maiuscole e minuscole non contano. Andare a capo vale come uno spazio."),
    _("Asterisco: qualsiasi testo nella stessa riga, come brani*fine."),
    _("Cancelletto: una o più cifre, come sezione # di."),
    _('Virgolette: la sequenza esatta, maiuscole comprese, come "SID".'),
    _("Sezione 12 porta all'inizio della dodicesima sezione; le sezioni le elenca la riga che comincia con Le sezioni."),
    _("Invio, dal testo delle statistiche, passa all'occorrenza seguente."),
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
        etichetta = wx.StaticText(pannello, label=_("{titolo}. Invio conferma, Ctrl+Invio va a capo, Esc annulla.").format(titolo=titolo))
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
        pulsanti.AddButton(wx.Button(pannello, wx.ID_OK, _("Conferma")))
        pulsanti.AddButton(wx.Button(pannello, wx.ID_CANCEL, _("Annulla")))
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


class _Apertura:
    """Un'apertura in blocco in corso, Maiuscolo o Alt con F9 (2.7.0): i rami
    da aprire, gli avvisi dell'esploratore, e le voci della plancia che
    l'apertura tiene. Ogni voce tenuta si segna con il suo numero di Windows,
    e una voce tolta dalla plancia, per esempio con il cestino mentre si
    naviga, esce anche da qui: il numero di una voce tolta non si usa piu'."""

    def __init__(self, titolo, inizio, fine, evento, tutta):
        self.titolo, self.inizio, self.fine, self.evento, self.tutta = titolo, inizio, fine, evento, tutta
        self.radici = []
        self.esploratore = None
        self.eventi = collections.deque()
        self.da_aprire = collections.deque()
        # Le cartelle della plancia per percorso, e le voci tenute, per numero,
        # con il percorso o None.
        self.mappa = {}
        self._tenute = {}
        # I rami caricati a mano di cui si sono gia' guardate le cartelle, e
        # per ramo l'ultima cartella inserita dall'esploratore.
        self.guardati = set()
        self.ultime = {}
        # Le cartelle che l'esploratore riempie e non ha ancora finito, e i
        # rami chiusi da chi naviga mentre si apre, per numero: restano chiusi.
        self.incomplete = set()
        self.chiusi_a_mano = set()
        self.rami = 0
        self.voci = 0
        self.avviato = False
        self.pianificato = False

    def tieni(self, voce, percorso=None):
        chiave = pulizia.norm(percorso) if percorso is not None else None
        numero = int(voce.GetID())
        if chiave is not None or numero not in self._tenute:
            self._tenute[numero] = chiave
        if chiave is not None:
            self.mappa[chiave] = voce
        return voce

    def viva(self, voce):
        return voce is not None and int(voce.GetID()) in self._tenute

    def voce(self, percorso):
        voce = self.mappa.get(pulizia.norm(percorso))
        return voce if self.viva(voce) else None

    def tolta(self, numero):
        chiave = self._tenute.pop(numero, None)
        if chiave is not None and chiave in self.mappa and int(self.mappa[chiave].GetID()) == numero:
            del self.mappa[chiave]
        self.guardati.discard(numero)
        self.ultime.pop(numero, None)
        self.chiusi_a_mano.discard(numero)


class Finestra(wx.Frame):
    def __init__(self, ao="wasapi", cartella_dati=None):
        super().__init__(None, title=f"MeTeOra {version.VERSION}")
        cartella_dati = cartella_dati or percorsi.cartella_programma()
        self.impostazioni = Impostazioni(os.path.join(cartella_dati, FILE_IMPOSTAZIONI))
        self.impostazioni.carica()
        # Le statistiche (1.103.0): prima di ogni suono e di ogni riga della
        # console, che contano. L'avvio si conta con la versione di prima,
        # che le impostazioni ricordano ancora.
        self._statistiche = statistiche.Statistiche(os.path.join(cartella_dati, FILE_STATISTICHE))
        self._statistiche.carica()
        self._statistiche.avvio(version.VERSION, self.impostazioni["versione"])
        # Vero quando la finestra ha tutto cio' che l'orologio guarda.
        self._orologio_pronto = False
        self.archivio = Archivio(os.path.join(cartella_dati, FILE_PLAYLIST))
        errore_archivio = None
        try:
            self.archivio.carica()
        except (OSError, ValueError, KeyError) as e:
            errore_archivio = e
        from motore import Motore

        # Le uscite audio che cambiano (1.116.0): l'attesa prima di
        # rileggerle, se un brano si e' fermato perche' la sua uscita non si
        # apriva piu', e il punto da cui farlo ripartire, che l'orologio
        # delle statistiche annota ogni secondo.
        self._attesa_delle_uscite = None
        self._uscita_persa = False
        self._punto_di_ripresa = None
        # Gli speaker Cast (1.119.0): la ricerca, accesa solo se c'e'
        # pychromecast; lo speaker scelto che si aspetta, all'avvio o dopo
        # che e' sparito, e quello che si sta collegando, per uuid; da quando
        # la scelta e' assente, per il primato delle statistiche; la cartella
        # delle conversioni in FLAC, che sparisce all'uscita.
        self._ricerca_cast = None
        self._speaker_atteso = None
        self._speaker_in_collegamento = None
        self._assenza_dal = None
        # Gli avvisi del motore arrivano dai suoi fili: wx.CallAfter li porta
        # nel filo della finestra.
        self.motore = Motore(alla_fine=lambda: wx.CallAfter(self._brano_finito),
            all_errore=lambda p: wx.CallAfter(self._brano_in_errore, p), ao=ao, volume=self.impostazioni["volume"],
            chiedi_il_seguente=lambda: wx.CallAfter(self._prepara_il_seguente),
            al_passaggio=lambda percorso, sottobrano: wx.CallAfter(self._passaggio, percorso, sottobrano),
            al_caricamento=lambda: wx.CallAfter(self._aggiorna_il_video),
            ai_sottotitoli=lambda testo: wx.CallAfter(self._sottotitolo, testo), ai_sottotitoli_a_immagini=self._sottotitolo_a_immagini,
            al_salto=self._testo_superato, alle_uscite=lambda: wx.CallAfter(self._uscite_cambiate),
            all_uscita_persa=lambda percorso, sottobrano: wx.CallAfter(self._uscita_persa_dal_motore, percorso, sottobrano))
        # Velocita', tono, equalizzatore e dissolvenza salvati valgono per tutti
        # i brani, dal primo.
        self._applica_la_riproduzione()
        # Il brano che esce quando il motore ha chiesto il seguente, come
        # (playlist, brano, sottobrano), e il seguente preparato, come
        # (playlist, brano, sottobrano chiesto): servono al passaggio, per
        # ricontrollare. None fuori da un passaggio preparato.
        self._uscente = None
        self._preparato = None
        # Il brano fermo ricaricato in pausa da un comando (issue 39): conta
        # come avviato quando X lo fa ripartire.
        self._risvegliato = None
        # La scelta della riproduzione casuale, come (cio' che suona, il
        # seguente scelto): vedi _seguente_casuale.
        self._casuale_ricordato = None
        # Il mazzo com'era prima del giro nuovo che la ripetizione della lista
        # ha aperto preparando la dissolvenza, con il posto che suonava: se al
        # passaggio la ripetizione e' spenta, torna finito (1.96.11).
        self._mazzo_prima_del_giro = None
        # Il segno dei dettagli che F11 sta raccogliendo: un altro F11 lo cambia (1.77.0).
        self._dettagli_attesi = None
        # La lettura dei sottotitoli fatti di immagini in corso, una di
        # sottotitoli_ocr, o None; la passata in anticipo in corso, o None
        # (1.80.0). La scelta degli impressi sta nelle impostazioni.
        self._lettura = None
        self._passata = None
        # La pulizia all'avvio in corso, nel suo filo (1.104.0); i percorsi che
        # aveva da guardare, cosi' come erano scritti, e quelli, normalizzati,
        # che intanto sono tornati in uso, come il nome nuovo di una rinomina.
        self._pulizia = None
        self._guardati_in_pulizia = set()
        self._toccati_in_pulizia = set()
        # Il disco di ogni lettera e gli altri che ci hanno risposto: la
        # pulizia salta una lettera usata da dischi diversi (1.112.0).
        self.dischi = pulizia.Dischi(os.path.join(cartella_dati, FILE_DISCHI))
        # La Sentinella guarda il disco di una lettera ogni volta che MeTeOra
        # ne usa un file: uno diverso da quello ricordato rende la lettera
        # contesa. Chi risponde arriva dal suo filo (1.112.0).
        self._sentinella = pulizia.Sentinella(lambda lettera, chi: wx.CallAfter(self._disco_visto, lettera, chi))
        # Le lettere di cui Riconosci questo disco sta contando le voci, in
        # disparte, e l'evento che ferma i conti all'uscita (1.112.0).
        self._lettere_in_conto = set()
        self._conti_fermati = threading.Event()
        # I video su cui la passata non ha trovato niente: in questa sessione
        # non si rifa'.
        self._passate_vuote = set()
        # L'apertura in blocco in corso, Maiuscolo o Alt con F9: dalla 2.7.0
        # i tasti non la fermano, e si naviga mentre la plancia si riempie.
        self._apertura = None
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
        # I brani che di fila non si sono potuti suonare, per identita': quando
        # ci sono tutti quelli che l'avanzamento puo' suonare, un altro giro
        # non servirebbe, con la ripetizione della lista o con la casuale
        # (1.96.11). Li dimenticano la fine vera di un brano e i brani fatti
        # partire da chi ascolta; non il caricamento, perche' un file rovinato
        # puo' caricarsi e poi non suonare.
        self._errori_di_fila = {}
        # Vero dopo che il timer ha fermato tutto, fino al brano seguente: una
        # fine di brano gia' in coda non fa partire altro (1.96.11).
        self._fermo_del_timer = False
        # Il timer di spegnimento (1.95.0): la sveglia dei minuti e quando
        # suona, in secondi di _adesso, oppure la fine del brano; scaduto, la
        # sfumatura, con il suo inizio. I minuti si ripropongono la volta dopo.
        self._sveglia_del_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._scade_il_timer, self._sveglia_del_timer)
        self._timer_scade = None
        self._timer_a_fine_brano = False
        self._minuti_del_timer = TIMER_PROPOSTO
        self._orologio_della_sfumatura = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._passo_della_sfumatura, self._orologio_della_sfumatura)
        self._inizio_della_sfumatura = None
        self._sintesi = GBsintesi.Sintesi()
        # La barra braille a blocchi (1.83.0): i testi letti in fila, con il
        # tempo minimo di lettura; le attese sono di wx, nel filo della finestra.
        self._braille = GBsintesi.Coda(self._mostra_in_braille, lambda secondi, funzione: wx.CallLater(max(1, round(secondi * 1000)), funzione))
        # Il numero dell'ultima riga di Dove sono nella coda del braille: la
        # riga dopo ne prende il posto, come nella console (tappa 14 b).
        # Il rapporto dei tasti da soli e di Dove sono sulla barra braille: il
        # nuovo prende il posto di quello di prima (issue 38).
        self._rapporto_in_braille = None
        # Il volume dello speaker Cast a cui Ctrl e Maiuscolo con M riportano.
        self._volume_di_prima_dello_speaker = None
        # Lo stesso per la riga della durata residua (tappa 14 d).
        self._durata_residua_in_braille = None
        # La banda dell'equalizzatore scelta con U, contata da zero: si
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
        self.schedario = Schedario(os.path.join(cartella_dati, FILE_SCHEDARIO), avvisa=lambda: wx.CallAfter(self._rinfresco_chiesto, "schede"),
            letto=self._sentinella.guarda)
        self.schedario.carica()
        self.contatore = Contatore(self.schedario, avvisa=lambda: wx.CallAfter(self._rinfresco_chiesto, "conti"))
        # Il segnale che fa aspettare i fili del contatore e dello schedario
        # mentre la finestra rinfresca o apre la plancia (1.83.1); dalla 2.7.1
        # anche per mezzo secondo dopo ogni tasto, perche' NVDA non aspetti.
        self._cedi = Cedi()
        self._precedenza_ai_tasti = PRECEDENZA_AI_TASTI
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
        self.marcatori = Marcatori(os.path.join(cartella_dati, FILE_MARCATORI))
        # I punti dei file lunghi (1.92.0).
        self.posizioni = posizioni.Posizioni(os.path.join(cartella_dati, FILE_POSIZIONI))
        self._giri_delle_posizioni = 0
        self._posizioni_non_salvate = False
        self._orologio_delle_posizioni = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._giro_delle_posizioni, self._orologio_delle_posizioni)
        self._orologio_delle_posizioni.Start(GIRO_DELLE_POSIZIONI)
        self.marcatori.carica()
        # L'orologio delle statistiche (1.103.0): ogni secondo da' lo stato
        # di adesso; ogni minuto guarda se e' ora di scrivere il file, in
        # disparte (1.113.5). La scheda audio automatica si chiede a Windows
        # una volta al minuto.
        self._giri_delle_statistiche = 0
        self._minuti_dal_salvataggio_delle_statistiche = 0
        self._statistiche_non_salvate = False
        self._scheda_per_le_statistiche = None
        self._inizio_della_ricerca = None
        self._ricerca_contata = True
        # Vero mentre la libreria si conta per la finestra delle statistiche.
        self._statistiche_in_arrivo = False
        self._orologio_delle_statistiche = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._giro_delle_statistiche, self._orologio_delle_statistiche)
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
        # La selezione multipla della plancia (1.98.0): None quando la
        # selezionata e' solo la voce col fuoco, come dopo una freccia;
        # altrimenti le voci scelte con Maiuscolo, Ctrl o i clic, per numero
        # di voce.
        self._selezione = None
        # Le voci dei brani, dei file e dei sottobrani per percorso, come
        # {percorso: {numero della voce: voce}}, e il percorso del brano che le
        # etichette dicono in riproduzione: le schede nuove e il cambio di
        # brano rinfrescano solo le loro voci. Con Questo PC aperto tutto, 140
        # mila voci, rifarle tutte fermava la finestra (2.7.0). La chiave sta
        # anche nei dati della voce: una rinomina non lascia voci tolte qui.
        self._voci_dei_file = {}
        self._annunciato = None
        # Le etichette che aspettano di essere scritte a pezzi, per numero di
        # voce, come (voce, testo); una voce tolta ne esce.
        self._etichette_in_attesa = {}
        self._etichette_pianificate = False
        # Lo stato della selezione per lo screen reader (issue 21): l'oggetto
        # di accessibilita' della plancia, se attaccato, e la voce col fuoco
        # di prima di una freccia o di un'iniziale che Windows muove, finche'
        # la selezione multipla non e' chiusa dopo di loro.
        self._accessibile = None
        self._fuoco_prima_della_freccia = None
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
        # I file aperti da Windows, raccolti per un attimo (1.91.0), e
        # l'ascolto delle altre copie di MeTeOra, che meteora.py collega.
        self._da_aprire = []
        self._apertura_esterna_pianificata = False
        self.ascolto_delle_copie = None
        # Le playlist M3U e PLS da importare, una per una, come coppie
        # (percorso, gruppo), e quella che si sta importando (1.113.0).
        self._da_importare = []
        self._importazione = None
        for controllo in (self.albero, self.console, self.cruscotto):
            controllo.SetDropTarget(_Trascinamento(self))
        # La barra dei comandi per il mouse, per chi vede (Gabriele, 1.87.0):
        # non prende mai il fuoco e non e' nell'ordine di tabulazione.
        self.barra = BarraDeiComandi(self, acceso=self.impostazioni["barra_dei_comandi"])
        self.scrivi(_("MeTeOra {versione} del {data}. Pronto: F1 apre il manuale nel browser, F12 scrive nella console la guida rapida dei tasti, "
            "F7 apre il cruscotto con i tasti del punto in cui ti trovi.").format(versione=version.VERSION, data=version.DATE))
        # Dopo un aggiornamento la versione e' cambiata: lo si dice (1.84.0).
        prima = self.impostazioni["versione"]
        if prima and prima != version.VERSION:
            self.scrivi(_("MeTeOra è stato aggiornato dalla {prima} alla {versione}: F2 scrive nella console le novità.").format(prima=prima, versione=version.VERSION))
        if prima != version.VERSION:
            self.impostazioni["versione"] = version.VERSION
            self._salva_impostazioni()
        # I tasti rapidi a carattere, che Ctrl con F12 spegne e Maiuscolo con F12 riaccende:
        # a ogni avvio sono accesi (Gabriele, 1.86.0).
        self._tasti_rapidi = True
        fuori_dal_normale = self._riproduzione_fuori_dal_normale()
        if fuori_dal_normale:
            self.scrivi(fuori_dal_normale)
        if self.impostazioni.errore:
            nuovo = os.path.basename(self.impostazioni.percorso)
            if self.impostazioni.da_nuovo:
                testo = _("Il file delle impostazioni non si legge: {errore}. Riparto da quelle salvate in {nuovo}.").format(errore=self.impostazioni.errore, nuovo=nuovo)
            else:
                testo = _("Il file delle impostazioni non si legge, e parto con quelle predefinite: {errore}. Le impostazioni nuove vanno in {nuovo}.").format(
                    errore=self.impostazioni.errore, nuovo=nuovo)
            self._avviso_all_avvio("errore", testo)
        if errore_archivio:
            self._avviso_all_avvio("errore", _("Il file delle playlist non si legge, e parto senza playlist: {errore}").format(errore=errore_archivio))
            # Il file illeggibile non va sovrascritto alla prima modifica.
            self.archivio.percorso += ".nuovo"
        if self.marcatori.errore:
            self._avviso_all_avvio("errore", _("Il file dei marker non si legge, e resta com'è: {errore}. I marker nuovi vanno in {nuovo}.").format(
                errore=self.marcatori.errore, nuovo=os.path.basename(self.marcatori.percorso)))
        if self._statistiche.errore:
            nuovo = os.path.basename(self._statistiche.percorso)
            if self._statistiche.da_nuovo:
                testo = _("Il file delle statistiche non si legge: {errore}. Riparto da quelle salvate in {nuovo}.").format(errore=self._statistiche.errore, nuovo=nuovo)
            else:
                testo = _("Il file delle statistiche non si legge, e resta com'è: {errore}. Le statistiche nuove vanno in {nuovo}.").format(
                    errore=self._statistiche.errore, nuovo=nuovo)
            self._avviso_all_avvio("errore", testo)
        if self.dischi.errore:
            # Le lettere contese non si rileggono da nessuna parte: niente .nuovo, la pulizia non impara niente (1.112.0).
            self._avviso_all_avvio("errore", _("Il file dei dischi della pulizia non si legge, e resta com'è: {errore}. "
                "Finché non si legge, la pulizia all'avvio salta tutte le unità con la lettera.").format(errore=self.dischi.errore))
        self._scrivi_la_scheda_all_avvio(esito_della_scheda, errore_della_scheda)
        self._chiedi_schede(*self.archivio.playlist, self.archivio.preferiti)
        self._orologio_pronto = True
        self._orologio_delle_statistiche.Start(GIRO_DELLE_STATISTICHE)

    # La costruzione.

    def _costruisci(self):
        pannello = wx.Panel(self)
        sopra = wx.BoxSizer(wx.HORIZONTAL)
        colonna_sinistra = wx.BoxSizer(wx.VERTICAL)
        colonna_sinistra.Add(wx.StaticText(pannello, label=_("Plancia dei comandi")), 0, wx.ALL, 2)
        # A selezione singola, nativa, come l'albero di Esplora risorse. Con
        # wx.TR_MULTIPLE wx simula la selezione multipla, e a ogni freccia
        # manda a NVDA anche fuochi sulla voce di prima, che NVDA a volte
        # legge (Andrea, 5 ottobre 2026; 1.98.0). La selezione multipla la
        # tiene MeTeOra: Maiuscolo con le frecce la allarga, Ctrl con le
        # frecce muove il fuoco senza selezionare, Ctrl+Spazio accende e
        # spegne la voce col fuoco, e i clic con Ctrl e Maiuscolo fanno lo
        # stesso con il mouse.
        self.albero = wx.TreeCtrl(pannello, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        self.albero.SetName(_("Plancia dei comandi"))
        # Lo stato della selezione per lo screen reader (issue 21): l'oggetto
        # si attacca solo con la voce delle impostazioni accesa all'avvio, o
        # quando la si accende; spenta, risponde come Windows, e non si stacca
        # mai a finestra aperta.
        if self.impostazioni["stato_della_selezione"]:
            self._attacca_lo_stato_della_selezione()
        colonna_sinistra.Add(self.albero, 1, wx.EXPAND)
        colonna_destra = wx.BoxSizer(wx.VERTICAL)
        colonna_destra.Add(wx.StaticText(pannello, label=_("Console")), 0, wx.ALL, 2)
        self.console = wx.TextCtrl(pannello, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.console.SetName(_("Console"))
        colonna_destra.Add(self.console, 1, wx.EXPAND)
        sopra.Add(colonna_sinistra, 1, wx.EXPAND | wx.ALL, 4)
        sopra.Add(colonna_destra, 1, wx.EXPAND | wx.ALL, 4)
        tutto = wx.BoxSizer(wx.VERTICAL)
        tutto.Add(sopra, 1, wx.EXPAND)
        # Traduttori: il nome dell'area in basso della finestra, che mostra i tasti del punto in cui si e'.
        tutto.Add(wx.StaticText(pannello, label=_("Cruscotto")), 0, wx.LEFT | wx.RIGHT, 6)
        self.cruscotto = wx.TextCtrl(pannello, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.cruscotto.SetName(_("Cruscotto"))
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
        self.albero.Bind(wx.EVT_LEFT_DOWN, self._clic_nell_albero)
        self.albero.Bind(wx.EVT_TREE_DELETE_ITEM, self._voce_tolta)
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
        self.nodo_preferiti = self.albero.AppendItem(radice, _("Preferiti"), data={"tipo": "playlist", "playlist": self.archivio.preferiti, "caricato": False})
        self.nodo_playlist = self.albero.AppendItem(radice, _("Playlist"), data={"tipo": "radice_playlist"})
        self.nodo_pc = self.albero.AppendItem(radice, _("Questo PC"), data={"tipo": "pc", "caricato": False})
        self.albero.SetItemHasChildren(self.nodo_pc, True)
        self.nodo_rete = self.albero.AppendItem(radice, _("Questa rete"), data={"tipo": "rete", "caricato": False})
        self.albero.SetItemHasChildren(self.nodo_rete, True)
        self.albero.AppendItem(radice, _("Apri file"), data={"tipo": "comando", "comando": "apri_file"})
        # Le statistiche, prima delle impostazioni (Gabriele, 1.103.0).
        self.albero.AppendItem(radice, _("Statistiche"), data={"tipo": "comando", "comando": "statistiche"})
        self.albero.AppendItem(radice, _("Impostazioni"), data={"tipo": "comando", "comando": "impostazioni"})
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
            self._statistiche.conta("righe_riscritte")
            return
        self._statistiche.conta("righe_della_console")
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
        volume degli effetti e' a zero. Le statistiche lo contano anche a
        volume zero, e l'orologio fa un passo: l'evento puo' aver cambiato
        lo stato (1.103.0)."""
        self._conta_l_evento(evento)
        return suoni.suona(evento, self.impostazioni["volume_effetti"])

    def _conta_l_evento(self, evento):
        """L'evento nelle statistiche, e un passo dell'orologio; anche per gli
        eventi che suonano al volo, come il volume (1.116.2)."""
        self._statistiche.evento(evento)
        self._scatto_delle_statistiche()

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
            # Il resoconto intero, con la pila, nel registro degli errori (1.89.0).
            registro.problema(tipo, valore, traccia)
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
                registro.scrivi(f"Avviso di python-mpv: {messaggio}")
                with contextlib.suppress(Exception):
                    wx.CallAfter(self._scrivi_il_problema, riga_dell_avviso(messaggio))

        sys.excepthook = nel_filo_della_finestra
        threading.excepthook = negli_altri_fili
        warnings.showwarning = negli_avvisi

    def apri_dall_esterno(self, percorsi, da=None):
        """I file e le cartelle che arrivano da Windows (1.91.0): dalla riga di
        comando, da un'altra copia di MeTeOra o trascinati sulla finestra.
        Quelli che arrivano insieme, come quando si aprono piu' file da Esplora
        risorse, si raccolgono per un attimo e suonano come una lista sola.
        MeTeOra torna in primo piano. da dice alle statistiche da dove
        arrivano: avvio, copia o trascinamento."""
        if not self or self._chiusa:
            return
        if da in ("avvio", "copia", "trascinamento"):
            self._statistiche.conta({"avvio": "aperti_all_avvio", "copia": "aperti_da_un_altra_copia", "trascinamento": "aperti_col_trascinamento"}[da])
        self._da_aprire.extend(percorsi)
        if self.IsIconized():
            self.Iconize(False)
        self.Raise()
        if not self._apertura_esterna_pianificata:
            self._apertura_esterna_pianificata = True
            wx.CallLater(ATTESA_DEI_FILE_DA_WINDOWS, self._apri_i_percorsi)

    def _apri_i_percorsi(self):
        self._apertura_esterna_pianificata = False
        percorsi, self._da_aprire = list(dict.fromkeys(self._da_aprire)), []
        if self._chiusa or not percorsi:
            return
        # Le playlist M3U e PLS di altri programmi si importano, una per una,
        # e la prima suona se non arriva altro da suonare (1.113.0). Quelle
        # dentro una cartella non si guardano.
        liste = [p for p in percorsi if formati.e_playlist(p) and os.path.isfile(p)]
        if liste:
            percorsi = [p for p in percorsi if p not in set(liste)]
        cartelle = [p for p in percorsi if os.path.isdir(p)]
        if len(cartelle) == len(percorsi) == 1:
            # Una cartella sola suona come X su di lei nella plancia.
            self._importa_le_playlist(liste)
            self._riproduci_cartella(cartelle[0])
            return
        brani, scartati = [], []
        for percorso in percorsi:
            if os.path.isdir(percorso):
                brani += [Brano(f) for _sotto, files in questo_pc.contenuti_ricorsivi(percorso) for f in files]
            elif os.path.isfile(percorso) and formati.supportato(percorso):
                brani.append(Brano(percorso))
            else:
                scartati.append(os.path.basename(percorso.rstrip("\\")) or percorso)
        if scartati:
            self.scrivi(_("MeTeOra non suona {file}: non è un formato che conosce, o non c'è.").format(file=", ".join(scartati)))
        self._importa_le_playlist(liste, None if brani else "suona")
        if not brani:
            if not liste:
                self._riscontro("niente_da_suonare", _("Niente da suonare in quello che arriva da Windows."))
            return
        # Come Apri file: la lista non entra fra le playlist, e la sua
        # cartella vuota la tiene fuori da Questo PC.
        # Traduttori: il nome della lista, che non entra fra le playlist, dei file aperti da Windows.
        pl = Playlist(_("file aperti") if len(brani) > 1 else _("file aperto"), brani, cartella="")
        self._suona(pl, pl.brani[0], "file_aperto")

    # I punti dei file lunghi (Gabriele, 4 ottobre 2026, 1.92.0).

    def _ricorda_la_posizione(self):
        """Il punto del file che suona, se e' piu' lungo del limite delle
        impostazioni; non per i file con piu' sottobrani, che sono canzoni."""
        limite = self.impostazioni["ripresa_oltre"] * 60
        percorso = self.motore.in_corso
        if not limite or not percorso or self.motore.sottobrani:
            return
        durata = self.motore.durata
        if durata is not None and durata >= limite:
            self.posizioni.ricorda(percorso, self.motore.posizione, durata)

    def _giro_delle_posizioni(self, _evento):
        """Ogni GIRO_DELLE_POSIZIONI il punto; ogni GIRI_PER_SALVARE il file.
        Un salvataggio che non riesce lo si dice una volta sola."""
        if self._chiusa:
            return
        self._ricorda_la_posizione()
        self._giri_delle_posizioni += 1
        if self._giri_delle_posizioni % GIRI_PER_SALVARE or not self.posizioni.modificate:
            return
        try:
            self.posizioni.salva()
        except OSError as e:
            self._statistiche.conta("salvataggi_non_riusciti")
            if not self._posizioni_non_salvate:
                self._posizioni_non_salvate = True
                self._riscontro("errore", _("Non riesco a salvare le posizioni dei file lunghi: {errore}.").format(errore=e.strerror or e))

    # I capitoli (Gabriele, 4 ottobre 2026, 1.93.0).

    def _capitoli_della_voce(self, dati):
        """I capitoli di un brano o di un file della plancia, dalla sua scheda:
        [(secondi, titolo)]. Non per i sottobrani e i file che ne hanno."""
        if dati.get("tipo") not in ("brano", "file") or dati["brano"].sottobrano or self._ha_sottobrani(dati["brano"]):
            return []
        scheda = self.schedario.scheda(dati["brano"].percorso) or {}
        return [tuple(capitolo) for capitolo in scheda.get("capitoli") or []]

    def _capitoli_in_corso(self):
        """I capitoli del brano che suona: quelli di libmpv, che li vede tutti,
        altrimenti quelli dei tag nello schedario."""
        elenco = self.motore.capitoli()
        if not elenco and self.motore.in_corso:
            scheda = self.schedario.scheda(self.motore.in_corso) or {}
            elenco = [tuple(capitolo) for capitolo in scheda.get("capitoli") or []]
        return elenco

    def _comando_capitolo(self):
        """La virgola (issue 38): il capitolo in cui si e', fra quanti."""
        if self._niente_in_corso(risveglia=True):
            return
        elenco = self._capitoli_in_corso()
        if not elenco:
            self._riporta(_("{file} non ha capitoli.").format(file=os.path.basename(self.motore.in_corso)), "capitolo")
            return
        indice = capitolo_attuale(elenco, self.motore.posizione or 0.0)
        secondi, titolo = elenco[indice]
        self._riporta(f"{frase_del_capitolo(indice + 1, len(elenco), titolo, secondi)}.", "capitolo")

    def _comando_primo_capitolo(self):
        self._al_capitolo_estremo(ultimo=False)

    def _comando_ultimo_capitolo(self):
        self._al_capitolo_estremo(ultimo=True)

    def _al_capitolo_estremo(self, ultimo):
        """Alt con la virgola l'ultimo capitolo, Ctrl e Alt con la virgola il
        primo, o l'inizio del primo, come Ctrl con la virgola."""
        if self._niente_in_corso(risveglia=True):
            return
        elenco = self._capitoli_in_corso()
        if not elenco:
            self._riscontro("non_disponibile", _("{file} non ha capitoli.").format(file=os.path.basename(self.motore.in_corso)))
            return
        posizione = self.motore.posizione or 0.0
        attuale = capitolo_attuale(elenco, posizione)
        indice = len(elenco) - 1 if ultimo else 0
        if attuale == indice and (ultimo or posizione - elenco[0][0] <= RITORNO_AL_CAPITOLO):
            self._riscontro("nessun_altro_brano", _("Sei già nell'ultimo capitolo.") if ultimo else _("È il primo capitolo."))
            return
        secondi, titolo = elenco[indice]
        self.motore.vai_a(secondi)
        self._riscontro("capitolo_successivo" if ultimo else "capitolo_precedente", f"{frase_del_capitolo(indice + 1, len(elenco), titolo, secondi)}.")

    def _comando_capitolo_precedente(self):
        self._vai_al_capitolo(-1)

    def _comando_capitolo_successivo(self):
        self._vai_al_capitolo(1)

    def _vai_al_capitolo(self, passo):
        """Ctrl e Maiuscolo con la virgola: il capitolo prima o dopo. Ctrl con la virgola, oltre i primi
        RITORNO_AL_CAPITOLO secondi del capitolo, torna al suo inizio."""
        if self._niente_in_corso(risveglia=True):
            return
        elenco = self._capitoli_in_corso()
        if not elenco:
            self._riscontro("non_disponibile", _("{file} non ha capitoli.").format(file=os.path.basename(self.motore.in_corso)))
            return
        posizione = self.motore.posizione or 0.0
        attuale = capitolo_attuale(elenco, posizione)
        if passo < 0:
            indice = attuale if posizione - elenco[attuale][0] > RITORNO_AL_CAPITOLO else attuale - 1
            if indice < 0:
                self._riscontro("nessun_altro_brano", _("È il primo capitolo."))
                return
        else:
            indice = attuale + 1
            if indice >= len(elenco):
                self._riscontro("nessun_altro_brano", _("È l'ultimo capitolo."))
                return
        secondi, titolo = elenco[indice]
        self.motore.vai_a(secondi)
        self._riscontro("capitolo_precedente" if passo < 0 else "capitolo_successivo", f"{frase_del_capitolo(indice + 1, len(elenco), titolo, secondi)}.")

    def _suona_il_capitolo(self, dati):
        """X, Invio o il menu su un capitolo della plancia: il file da li'; se
        suona gia', un salto."""
        frase = f"{frase_del_capitolo(dati['numero'], dati['totale'], dati['titolo'], dati['secondi'])}."
        if self.motore.in_corso and dati["brano"] is self.coda.corrente:
            self.motore.vai_a(dati["secondi"])
            self._riscontro("capitolo_successivo", frase)
            return
        self._suona(dati["playlist"], dati["brano"], inizio=dati["secondi"])
        self.scrivi(f"{frase_del_capitolo(dati['numero'], dati['totale'], dati['titolo'], dati['secondi'], dal=True)}.")

    def copie_mancate(self, nomi):
        """All'avvio, se una copia dei dati non e' riuscita (1.90.0)."""
        self._riscontro("errore", _("Non riesco a fare la copia di {file} nella cartella copie: forse il disco è pieno o protetto.").format(file=", ".join(nomi)))

    def crash_precedente(self, percorso):
        """All'avvio dopo un crash (1.89.0): la console dice dove sta il
        resoconto, da mandare a chi sviluppa."""
        self._statistiche.conta("crash")
        # Traduttori: MeTeOra - Errori.log e' il nome di un file, e resta com'e'.
        self._riscontro("problema", _("L'ultima volta MeTeOra si è chiuso per un errore grave. Il resoconto è nel file {file}, "
            "nella cartella {cartella}: mandalo a chi sviluppa, insieme a MeTeOra - Errori.log.").format(file=os.path.basename(percorso), cartella=os.path.dirname(percorso)))

    def _problema(self, tipo, valore, traccia):
        self._scrivi_il_problema(riga_del_problema(tipo, valore, traccia))

    def _scrivi_il_problema(self, riga):
        """Scrive il problema nella console. Lo stesso problema ripetuto di
        seguito riscrive la sua riga con il conto delle volte, senza suono:
        un errore che torna a ogni istante non deve riempire la console."""
        if not self or self._chiusa:
            return
        self._statistiche.conta("problemi_interni")
        categoria = ("problema", riga)
        if self._categoria == categoria:
            self._ripetizioni += 1
            # Traduttori: riga e' la riga di un problema interno, senza il punto finale; n quante volte e' arrivato di seguito.
            self.scrivi(ngettext("{riga}, {n} volta.", "{riga}, {n} volte.", self._ripetizioni).format(riga=riga[:-1], n=self._ripetizioni), categoria)
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
            righe = [_("Tasti per la console."), _("Frecce, Pagina su e giù, Inizio e Fine per leggere; i messaggi nuovi arrivano in fondo, con l'ora. "
                "La barra rovesciata cerca nella console, anche con i jolly e le virgolette, e Invio passa all'occorrenza seguente.")]
        elif len(self._voci_selezionate()) > 1:
            quante = len(self._voci_selezionate())
            righe = [ngettext("Tasti per {n} voce selezionata: un ramo selezionato vale per tutto ciò che contiene.",
                    "Tasti per {n} voci selezionate: un ramo selezionato vale per tutto ciò che contiene.", quante).format(n=quante),
                _("X suona la selezione come una playlist invisibile, che resta finché non premi V. Invio, Applicazioni o Spazio: menu della selezione, con Leggi i tag e Modifica i tag. "
                "Canc toglie i brani dalle playlist ed elimina le playlist e i marker, Maiuscolo con Canc manda i file nel cestino, F4 li mette nei Preferiti."),
                _("Maiuscolo con le frecce allarga la selezione, Ctrl con le frecce muove il fuoco senza selezionare, Ctrl con Spazio accende e spegne la voce col fuoco.")]
        else:
            # La voce su cui agiscono Canc, X, F4 e il menu, che puo' non
            # essere quella col fuoco (tappa 9).
            voce = self._voce_di_lavoro()
            dati = self._dati(voce) or {}
            tipo = "preferiti" if dati.get("tipo") == "playlist" and dati["playlist"] is self.archivio.preferiti else dati.get("tipo")
            nome, riga = TASTI_DEL_CONTESTO.get(tipo, (_("la plancia"), ""))
            # Traduttori: nome e' il tipo di voce della plancia, con l'articolo, come i Preferiti o una cartella.
            righe = [_("Tasti per {nome}.").format(nome=nome)] + ([riga] if riga else [])
            if tipo == "cartella" and dati.get("a_mano"):
                righe.append(_("Canc, o Togli il percorso nel menu, lo toglie da Questa rete; i file restano dove sono."))
            if voce != self._voce_corrente():
                righe.append(_("Il fuoco è su un'altra voce: le frecce, F9 con i suoi comandi, J, K e la barra verticale partono da lì; Canc, Maiuscolo con Canc, X, Maiuscolo con X, F4, F11, "
                    "Maiuscolo con F11, Maiuscolo con le cifre, la barra rovesciata e il menu agiscono sulla voce selezionata."))
        if not self._tasti_rapidi:
            righe = [_("Tasti rapidi spenti: lettere, cifre e segni vanno alla plancia, che cerca per iniziale; Maiuscolo con F12 li riaccende."), *righe]
        return righe + TASTI_COMUNI

    def _vai(self, controllo, evento):
        self._suono(evento)
        if not self.IsActive():
            self.Raise()
        if controllo is self.cruscotto and self.cruscotto.HasFocus():
            self._rinfresca_cruscotto()
        controllo.SetFocus()

    def _vai_alla_plancia(self):
        self._vai(self.albero, "plancia")

    def _vai_alla_console(self):
        self._vai(self.console, "console")

    def _vai_al_cruscotto(self):
        self._vai(self.cruscotto, "cruscotto")

    # I tasti.

    def _tasto(self, evento):
        """I tasti di tutta la finestra. Quando un comando ha finito il suo
        lavoro, dialoghi compresi, il beep dice se ha portato il fuoco della
        plancia a un altro livello. Ogni tasto ha la precedenza sul lavoro in
        disparte per un attimo (2.7.1): NVDA, che chiede lo stato delle voci
        a MeTeOra, trova la strada libera."""
        if self._precedenza_ai_tasti and evento.GetKeyCode() not in _SOLO_MODIFICATORI:
            self._cedi.trattieni(self._precedenza_ai_tasti)
        prima = self._profondita(self._voce_corrente())
        nome = self._nome_del_tasto(evento)
        if nome:
            self._statistiche.tasto(nome)
        if self._esegui_il_tasto(evento):
            self._controlla_il_livello(prima)

    def _esegui_il_tasto(self, evento):
        """Esegue il tasto, se e' un comando, e torna vero; altrimenti lo
        lascia passare e torna falso."""
        codice = evento.GetKeyCode()
        modificatori = evento.GetModifiers()
        comando = COMANDI_DEI_TASTI_FUNZIONE.get((codice, modificatori))
        if comando:
            getattr(self, comando)()
            return True
        if modificatori in (CTRL, MAIUSCOLO) and codice in INTERRUTTORI:
            getattr(self, INTERRUTTORI[codice])(modificatori == MAIUSCOLO)
            return True
        if modificatori == wx.MOD_CONTROL and (evento.GetUnicodeKey() in (ord("\\"), 0x1C) or codice == ord("\\")):
            # Ctrl con la barra rovesciata: la ricerca in tutto MeTeOra (1.71.0).
            self._ricerca_globale()
            return True
        # Il tastierino numerico resta a NVDA.
        if wx.WXK_NUMPAD0 <= codice <= wx.WXK_NUMPAD_DIVIDE:
            evento.Skip()
            return False
        tasto = carattere_del_tasto(evento)
        # Canc arriva con il codice 127, come Invio, Tab ed Esc con i loro:
        # non sono caratteri da scrivere, e vanno ai controlli.
        if tasto is None:
            evento.Skip()
            return False
        carattere, modificatori = tasto
        if modificatori not in (SOLO, MAIUSCOLO):
            # Ctrl e Alt (issue 38): le famiglie dei tasti a lettera, anche
            # con i tasti rapidi spenti, perche' non scrivono; le altre
            # combinazioni restano a Windows.
            comando = TASTI.get((carattere, modificatori))
            if comando is None:
                evento.Skip()
                return False
            getattr(self, f"_comando_{comando}")()
            return True
        if not self._tasti_rapidi:
            # Tasti rapidi spenti (1.86.0): nella plancia il carattere va
            # all'albero, che cerca la voce per iniziale. Altrove, nella
            # console, nel cruscotto o nel video, un controllo in sola lettura
            # suonerebbe l'avviso di Windows: lo si dice invece, sempre sulla
            # stessa riga (revisione della 1.86.0).
            if self._fuoco_nella_plancia():
                evento.Skip()
                return False
            self._riscontro("non_disponibile", _("Tasti rapidi spenti: le lettere cercano solo nella plancia, F5. Maiuscolo con F12 li riaccende."),
                "tasti_spenti")
            return True
        maiuscolo = modificatori == MAIUSCOLO
        if carattere.isdigit() and not maiuscolo:
            self._playlist_numero(int(carattere) or 10)
            return True
        # Maiuscolo con le cifre: i primi dieci marker. Windows puo' dare la
        # cifra con il Maiuscolo o il segno che la tastiera italiana ci mette sopra.
        if maiuscolo and (carattere.isdigit() or carattere in CIFRE_COL_MAIUSCOLO):
            self._marker_numero((int(carattere) or 10) if carattere.isdigit() else CIFRE_COL_MAIUSCOLO[carattere])
            return True
        comando = TASTI.get((carattere, modificatori))
        if comando:
            getattr(self, f"_comando_{comando}")()
            return True
        # Un tasto senza comando lo dice, e non arriva all'albero, che ne
        # farebbe la sua ricerca per iniziale spostando il fuoco (tappa 9).
        nome = NOMI_DEI_SEGNI.get(carattere, carattere.upper() if carattere.isalpha() else carattere)
        self._statistiche.senza_comando(f"{'Maiuscolo con ' if maiuscolo else ''}{nome}")
        if maiuscolo:
            self._riscontro("non_disponibile", _("Maiuscolo+{tasto} non ha un comando.").format(tasto=nome))
        else:
            self._riscontro("non_disponibile", _("Il tasto {tasto} non ha un comando.").format(tasto=nome))
        return True

    def _metti_i_tasti_rapidi(self, accesi):
        """Ctrl con F12 spegne i tasti rapidi a carattere, lettere, cifre e
        segni, anche con il Maiuscolo, e Maiuscolo con F12 li riaccende
        (Gabriele, 1.86.0; dalla 2.0.2 non piu' a giro). Spenti, vanno ai
        controlli: nella plancia l'albero di Windows salta alla voce che
        comincia con cio' che si scrive, utile in un ramo grande. I tasti
        funzione, Esc e Ctrl con la barra rovesciata restano; a ogni avvio i
        tasti rapidi sono accesi."""
        evento = "tasti_accesi" if accesi else "tasti_spenti"
        frase = _("Tasti rapidi accesi.") if accesi else _("Tasti rapidi spenti: le lettere cercano nella plancia per iniziale. Maiuscolo con F12 li riaccende.")
        if self._tasti_rapidi == accesi:
            # Traduttori: frase e' lo stato che il comando chiedeva, ed era gia' quello.
            self._riscontro(evento, _("Già così. {frase}").format(frase=frase))
            return
        self._tasti_rapidi = accesi
        self._riscontro(evento, frase)
        # Il cruscotto in cui si e' gia' dice subito lo stato nuovo.
        if self.cruscotto.HasFocus():
            self._rinfresca_cruscotto()

    def _fuoco_nella_plancia(self):
        return wx.Window.FindFocus() is self.albero

    def _dopo_l_iniziale(self, prima):
        """La ricerca per iniziale di Windows sposta la voce col fuoco, come
        una freccia: la selezione multipla, se c'era, finisce (1.98.0). La
        voce di prima si scorda solo dopo, come in _dopo_la_freccia."""
        if not self._chiusa:
            voce = self.albero.GetFocusedItem()
            if voce.IsOk() and voce != prima:
                self._azzera_la_selezione()
        self._fuoco_prima_della_freccia = None

    def _carattere_nell_albero(self, evento):
        """I caratteri che arrivano fino all'albero, per esempio con AltGr o
        dal tastierino, si fermano qui: la ricerca per iniziale del controllo
        sposterebbe il fuoco senza un comando (tappa 9). Con i tasti rapidi
        spenti passano, e la ricerca per iniziale e' proprio quella voluta."""
        codice = evento.GetUnicodeKey()
        if codice > 32 and chr(codice).isprintable():
            if self._tasti_rapidi:
                return
            self._aspetta_la_fine_della_selezione(self.albero.GetFocusedItem())
            wx.CallAfter(self._dopo_l_iniziale, self.albero.GetFocusedItem())
        evento.Skip()

    def _tasto_nell_albero(self, evento):
        codice = evento.GetKeyCode()
        voce = self._voce_corrente()
        prima = self._profondita(voce)
        if self._esegui_nell_albero(evento):
            self._controlla_il_livello(prima)
        elif codice not in _SOLO_MODIFICATORI:
            # Le frecce e gli altri tasti del controllo spostano il fuoco dopo
            # questo gestore: si guarda quando hanno finito.
            wx.CallAfter(self._controlla_il_livello, prima)
            if codice in (wx.WXK_LEFT, wx.WXK_RIGHT) and evento.GetModifiers() == wx.MOD_NONE:
                # Sinistra e destra aprono e chiudono i rami, oppure spostano
                # il fuoco: solo se lo spostano la selezione multipla finisce.
                self._aspetta_la_fine_della_selezione(voce)
                wx.CallAfter(self._dopo_la_freccia, voce)

    def _esegui_nell_albero(self, evento):
        """I tasti propri della plancia: torna vero se ne ha eseguito uno,
        falso se lo lascia al controllo."""
        codice = evento.GetKeyCode()
        modificatori = evento.GetModifiers()
        spostamento = codice in (wx.WXK_UP, wx.WXK_DOWN, wx.WXK_HOME, wx.WXK_END, wx.WXK_PAGEUP, wx.WXK_PAGEDOWN)
        con_ancora = spostamento and modificatori in (wx.MOD_SHIFT, wx.MOD_CONTROL)
        if spostamento and modificatori == wx.MOD_NONE:
            # Le frecce senza modificatori le muove Windows, che manda a NVDA
            # solo il fuoco sulla voce d'arrivo; la selezione multipla, come
            # in Esplora risorse, finisce (1.98.0).
            self._azzera_la_selezione()
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
        elif codice == wx.WXK_SPACE and modificatori == wx.MOD_CONTROL:
            self._alterna_nella_selezione(self._voce_corrente())
            # Il fuoco non si muove: lo stato nuovo NVDA lo sente solo se
            # glielo si annuncia (issue 21).
            self._annuncia_lo_stato(self._voce_corrente())
            self._di_la_selezione()
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
            return self._nome_del_brano(dati["brano"])
        if tipo == "sottobrano":
            # Traduttori: il nome di un sottobrano nelle frasi della console, come in Chiuso sottobrano 3 di gioco.sid.
            return _("sottobrano {numero} di {file}").format(numero=dati["numero"], file=dati["brano"].nome_del_file)
        if tipo == "marker":
            return _("il marker {nome}").format(nome=dati["marker"]["nome"])
        if tipo == "capitolo":
            return _("il capitolo {numero} di {file}").format(numero=dati["numero"], file=dati["brano"].nome_del_file)
        if tipo == "risultati":
            return _("Risultati di {ricerca}").format(ricerca=self._testo_della_ricerca)
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
        if len(selezionate) == 1 and voce.IsOk() and not self._e_selezionata(voce):
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
            for _volta in range(self._voci_visibili_per_pagina() if codice in (wx.WXK_PAGEUP, wx.WXK_PAGEDOWN) else 1):
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
        # restano le selezioni di prima, anche la sola voce col fuoco.
        nuova = self._intervallo(self._ancora, arrivo) if allarga else self._voci_selezionate()
        self._sposta_il_cursore(arrivo)
        self._fuoco_atteso = arrivo
        self._imposta_la_selezione(nuova)
        self._di_la_selezione()

    def _risali(self):
        """Backspace: chiude il ramo in cui sta la voce col fuoco e ci porta il
        fuoco; premuto ancora risale di un livello, chiudendo anche quello."""
        voce = self._voce_corrente()
        ramo = self.albero.GetItemParent(voce) if voce.IsOk() else None
        if ramo is None or not ramo.IsOk() or ramo == self.albero.GetRootItem():
            self._riscontro("nessun_altro_brano", _("Sei già al primo livello della plancia."))
            return
        self.albero.Collapse(ramo)
        self._seleziona(ramo)
        # Traduttori: nome e' il ramo della plancia appena chiuso, come una playlist, una cartella o il marker X.
        self._riscontro("risali", _("Chiuso {nome}.").format(nome=self._nome_della_voce(ramo)), "risali")

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
            self._riscontro("nessun_altro_brano", _("Sei già al primo livello della plancia."))
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
                self._chiudi_con_tutto(figlio)
        self.albero.EnsureVisible(antenato)
        # Il nome soltanto, senza i conti dell'etichetta.
        nome = self._nome_della_voce(antenato)
        if antenato == voce:
            # Gia' sull'antenato: non si sale, si chiudono solo i rami dentro.
            if chiusi:
                self._riscontro("nessun_altro_brano", _("Sei già su {nome}, non si risale oltre. Chiusi i rami aperti al suo interno.").format(nome=nome))
            else:
                self._riscontro("nessun_altro_brano", _("Sei già su {nome}, non si risale oltre.").format(nome=nome))
            return
        self._riscontro("risali_all_antenato", _("Risalito a {nome}.").format(nome=nome), "risali")

    def _seleziona(self, voce):
        """Seleziona soltanto questa voce e le da' il fuoco, come una freccia:
        nell'albero nativo, a NVDA arriva solo il fuoco sulla voce."""
        self._azzera_la_selezione()
        self.albero.SelectItem(voce)

    # La selezione multipla, tenuta da MeTeOra (1.98.0).

    def _voci_selezionate(self):
        """Le voci selezionate, nell'ordine della plancia: quelle della
        selezione multipla, oppure la voce col fuoco, che senza selezione
        multipla e' la selezionata."""
        if self._selezione is None:
            voce = self._voce_corrente()
            return [voce] if voce.IsOk() else []
        return self._in_ordine([voce for voce in self._selezione.values() if voce.IsOk()])

    def _e_selezionata(self, voce):
        if self._selezione is None:
            return voce.IsOk() and voce == self._voce_corrente()
        return voce.IsOk() and int(voce.GetID()) in self._selezione

    def _in_ordine(self, voci):
        """Le voci nell'ordine della plancia. L'ordine si calcola a ogni
        lettura, perche' intanto la plancia puo' inserire o togliere voci, con
        una passata sola sui figli di ogni ramo che ne contiene: anche migliaia
        di voci selezionate costano una passata."""
        if len(voci) < 2:
            return voci
        radice = self.albero.GetRootItem()
        indici = {}
        posti = {}

        def posto(voce):
            numero = int(voce.GetID())
            if numero not in posti:
                ramo = self.albero.GetItemParent(voce)
                chiave = int(ramo.GetID())
                if chiave not in indici:
                    indici[chiave] = {int(figlio.GetID()): i for i, figlio in enumerate(self._figli(ramo))}
                sopra = posto(ramo) if ramo.IsOk() and ramo != radice else ()
                posti[numero] = (*sopra, indici[chiave].get(numero, 0))
            return posti[numero]

        return sorted(voci, key=posto)

    def _colore_della_selezione(self):
        """Lo sfondo delle voci della selezione multipla: il colore della
        selezione di Windows schiarito verso lo sfondo della plancia, cosi'
        il testo resta leggibile con il suo colore."""
        selezione = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        sfondo = self.albero.GetBackgroundColour()
        return wx.Colour(*(round(0.35 * a + 0.65 * b) for a, b in zip(selezione.Get(False), sfondo.Get(False), strict=True)))

    def _colora(self, voce, selezionata):
        """Chi vede riconosce le voci della selezione multipla dal loro
        sfondo. Solo lo sfondo: la voce col fuoco Windows la disegna sempre
        evidenziata, e un colore del testo suo diventerebbe illeggibile a
        plancia senza fuoco. Cambiare lo sfondo non manda eventi a NVDA."""
        self.albero.SetItemBackgroundColour(voce, self._colore_della_selezione() if selezionata else wx.NullColour)

    def _imposta_la_selezione(self, voci):
        """La selezione multipla diventa queste voci."""
        vecchia = self._selezione or {}
        nuova = {int(voce.GetID()): voce for voce in voci if voce.IsOk()}
        for numero, voce in vecchia.items():
            if numero not in nuova and voce.IsOk():
                self._colora(voce, False)
        for numero, voce in nuova.items():
            if numero not in vecchia:
                self._colora(voce, True)
        self._selezione = nuova

    def _azzera_la_selezione(self):
        """Resta selezionata la sola voce col fuoco, come dopo una freccia."""
        if self._selezione is None:
            return
        # La voce col fuoco, se per NVDA era non selezionata, adesso lo e':
        # se il fuoco resta li', glielo si annuncia (issue 21).
        fuoco = self.albero.GetFocusedItem()
        if self._accessibile is not None and fuoco.IsOk() and self._selezionata_per_lo_screen_reader(int(fuoco.GetID())) is False:
            wx.CallAfter(self._annuncia_a_fuoco_fermo, fuoco)
        for voce in self._selezione.values():
            if voce.IsOk():
                self._colora(voce, False)
        self._selezione = None

    def _aggiungi_alla_selezione(self, voce):
        """Aggiunge la voce alla selezione; senza selezione multipla ci entra
        anche la voce col fuoco, come con Ctrl e un clic."""
        attuali = self._voci_selezionate()
        if voce.IsOk() and voce not in attuali:
            self._imposta_la_selezione([*attuali, voce])

    def _alterna_nella_selezione(self, voce):
        """Ctrl+Spazio e Ctrl con il clic: la voce entra nella selezione, o
        ne esce."""
        attuali = self._voci_selezionate()
        if voce in attuali:
            self._imposta_la_selezione([v for v in attuali if v != voce])
        else:
            self._aggiungi_alla_selezione(voce)

    def _intervallo(self, da, a):
        """Le voci fra da e a, estremi compresi, nell'ordine della plancia."""
        voci = self._cammino(da, a) or [a]
        if len(voci) > 1 and self._dopo(voci[0]) != voci[1]:
            voci.reverse()
        return voci

    def _di_la_selezione(self):
        """La riga della console, riscritta a ogni tasto: se la voce col
        fuoco e' selezionata e quante voci lo sono. Senza lo stato della
        selezione per lo screen reader NVDA non lo dice da se', perche' la
        selezione multipla e' di MeTeOra; con lo stato dice solo non
        selezionato, e il conto resta qui (issue 21)."""
        voce = self._voce_corrente()
        if not voce.IsOk():
            return
        quante = len(self._voci_selezionate())
        self._statistiche.massimo("selezione", quante)
        totale = _("Nessuna voce selezionata") if quante == 0 else plurale(quante, "{n} voce selezionata", "{n} voci selezionate")
        if self._e_selezionata(voce):
            # Traduttori: nome e' la voce col fuoco, totale quante voci sono selezionate, come 3 voci selezionate.
            testo = _("Selezionata: {nome}. {totale}.").format(nome=self._nome_della_voce(voce), totale=totale)
        else:
            testo = _("Non selezionata: {nome}. {totale}.").format(nome=self._nome_della_voce(voce), totale=totale)
        self.scrivi(testo, "selezione")

    def _dopo_la_freccia(self, prima):
        """Sinistra o destra hanno spostato il fuoco: come le altre frecce,
        la selezione multipla finisce. La voce di prima si scorda solo dopo:
        la voce d'arrivo NVDA l'ha gia' sentita selezionata, come per
        Windows, e chiudendo la selezione non c'e' niente da annunciargli."""
        if not self._chiusa:
            voce = self._voce_corrente()
            if voce.IsOk() and voce != prima:
                self._azzera_la_selezione()
        self._fuoco_prima_della_freccia = None

    def _clic_nell_albero(self, evento):
        """Il clic del mouse nella plancia, per chi vede: con Ctrl la voce
        entra o esce dalla selezione, con Maiuscolo la selezione va
        dall'ancora fino a lei; senza, come le frecce, la selezione multipla
        finisce e il clic lo gestisce Windows."""
        voce, dove = self.albero.HitTest(evento.GetPosition())
        sulla_voce = voce.IsOk() and dove & (wx.TREE_HITTEST_ONITEMLABEL | wx.TREE_HITTEST_ONITEMICON)
        if not sulla_voce or not (evento.ControlDown() or evento.ShiftDown()):
            if sulla_voce:
                self._azzera_la_selezione()
            evento.Skip()
            return
        corrente = self._voce_corrente()
        if evento.ControlDown():
            self._alterna_nella_selezione(voce)
            self._ancora = voce
        else:
            if self._ancora is None or self._fuoco_atteso != corrente or self._cammino(corrente, self._ancora) is None:
                self._ancora = corrente if corrente.IsOk() else voce
            self._imposta_la_selezione(self._intervallo(self._ancora, voce))
        self.albero.SetFocus()
        self._sposta_il_cursore(voce)
        self._fuoco_atteso = voce
        if voce == corrente:
            # Sulla voce col fuoco Windows non manda un fuoco nuovo: lo stato
            # cambiato si annuncia, come con Ctrl+Spazio (issue 21).
            self._annuncia_lo_stato(voce)
        self._di_la_selezione()

    def _voce_tolta(self, evento):
        """Una voce tolta dalla plancia esce anche dalla selezione: il suo
        numero Windows puo' darlo a una voce nuova."""
        if self._selezione:
            self._selezione.pop(int(evento.GetItem().GetID()), None)
        if self._apertura is not None:
            self._apertura.tolta(int(evento.GetItem().GetID()))
        self._etichette_in_attesa.pop(int(evento.GetItem().GetID()), None)
        # A finestra chiusa le voci si tolgono con l'albero, che non risponde piu'.
        chiave = None if self._chiusa else (self._dati(evento.GetItem()) or {}).get("chiave_dell_indice")
        if chiave is not None:
            voci = self._voci_dei_file.get(chiave)
            if voci is not None:
                voci.pop(int(evento.GetItem().GetID()), None)
                if not voci:
                    del self._voci_dei_file[chiave]
        evento.Skip()

    # Lo stato della selezione per lo screen reader (issue 21).

    def _attacca_lo_stato_della_selezione(self):
        """L'oggetto di accessibilita' della plancia, che a NVDA da' lo stato
        di ogni voce secondo la selezione di MeTeOra; il resto lo da'
        Windows. Si attacca una volta sola."""
        if self._accessibile is None:
            self._accessibile = accessibilita.StatoDellaSelezione(self.albero, self._stato_della_selezione_acceso,
                self._selezionata_per_lo_screen_reader)
            self.albero.SetAccessible(self._accessibile)

    def _stato_della_selezione_acceso(self):
        return not self._chiusa and self.impostazioni["stato_della_selezione"]

    def _selezionata_per_lo_screen_reader(self, numero):
        """Se la voce con questo numero, un HTREEITEM, e' selezionata per
        MeTeOra; None quando vale cio' che dice Windows, cioe' senza la
        selezione multipla, quando la selezionata e' la sola voce col fuoco.
        Lo chiede NVDA, anche a ogni voce: niente _voci_selezionate, che
        ordina. Una freccia sinistra o destra o un'iniziale che Windows ha gia'
        mosso chiudono la selezione multipla solo dopo, con un CallAfter: se
        intanto NVDA chiede, la voce d'arrivo e' gia' selezionata come per
        Windows, e non sente un non selezionato sbagliato."""
        if self._selezione is None:
            return None
        prima = self._fuoco_prima_della_freccia
        if prima is not None and int(self.albero.GetFocusedItem().GetID()) != prima:
            return None
        return numero in self._selezione

    def _aspetta_la_fine_della_selezione(self, voce):
        """Una freccia o un'iniziale che muove Windows sta per partire dalla
        voce col fuoco: fino al suo CallAfter, se il fuoco si muove, per lo
        screen reader vale la selezione di Windows."""
        self._fuoco_prima_della_freccia = int(voce.GetID()) if voce.IsOk() else None

    def _annuncia_lo_stato(self, voce):
        """Lo stato della voce col fuoco e' cambiato senza che il fuoco si
        muova, con Ctrl+Spazio, con un clic sulla voce stessa o con la
        selezione multipla chiusa a fuoco fermo: NVDA lo dice selezionato o
        non selezionato se glielo si annuncia."""
        if self._accessibile is not None and voce.IsOk():
            self._accessibile.annuncia(int(voce.GetID()))

    def _annuncia_a_fuoco_fermo(self, voce):
        """La selezione multipla si e' chiusa mentre la voce col fuoco ne era
        fuori, e per NVDA era non selezionata: adesso e' selezionata.
        Se il fuoco e' rimasto li', come con freccia giu' sull'ultima voce,
        con Ctrl e F9 sul ramo che ha il fuoco o con un clic sulla voce stessa,
        Windows non manda niente, e lo stato si annuncia; se si e' mosso,
        basta il suo evento di fuoco, che porta gia' lo stato nuovo. Si
        guarda dopo, perche' le frecce il fuoco lo muovono dopo il gestore
        del tasto: annunciato subito, NVDA direbbe selezionato sulla voce di
        partenza prima di ogni freccia."""
        if not self._chiusa and self._voce_corrente() == voce:
            self._annuncia_lo_stato(voce)

    def _dati(self, voce):
        return self.albero.GetItemData(voce) if voce and voce.IsOk() else None

    def _figli(self, voce):
        figlio, cookie = self.albero.GetFirstChild(voce)
        while figlio.IsOk():
            yield figlio
            figlio, cookie = self.albero.GetNextChild(voce, cookie)

    def _tutte_le_voci(self, voce=None):
        """Tutte le voci dentro voce, o dentro la plancia, nell'ordine della
        freccia giu' con tutto aperto. Con una pila: i generatori annidati,
        uno per livello, con 140 mila voci costavano a ogni rinfresco
        (banco della 2.7.0)."""
        pila = list(self._figli(voce or self.albero.GetRootItem()))[::-1]
        while pila:
            attuale = pila.pop()
            yield attuale
            pila.extend(list(self._figli(attuale))[::-1])

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
        if dati["tipo"] == "capitolo":
            return frase_del_capitolo(dati["numero"], dati["totale"], dati["titolo"], dati["secondi"])
        suona = bool(self.motore.in_corso) and brano is self.coda.corrente
        quanti = len(self._marker_della_voce(dati))
        if dati["tipo"] == "sottobrano":
            n = dati["numero"]
            titoli = (sottobrani.info(brano.percorso) or {}).get("titoli") or []
            durata = tempo(durata_del_sottobrano(brano.percorso, n))
            if n <= len(titoli) and titoli[n - 1]:
                parti = [_("Sottobrano {numero} di {totale}, {titolo}, {durata}").format(numero=n, totale=dati["totale"], titolo=titoli[n - 1], durata=durata)]
            else:
                parti = [_("Sottobrano {numero} di {totale}, {durata}").format(numero=n, totale=dati["totale"], durata=durata)]
            if quanti:
                parti.append(plurale(quanti, "{n} marker", "{n} marker"))
            if suona and self.motore.sottobrano == n:
                parti.append(_("in riproduzione"))
            return ", ".join(parti)
        nome = brano.percorso if dati.get("completo") else brano.nome_del_file
        if brano.sottobrano:
            info = sottobrani.info(brano.percorso)
            if info:
                nome = _("{nome}, sottobrano {numero} di {totale}").format(nome=nome, numero=brano.sottobrano, totale=info["sottobrani"])
            else:
                nome = _("{nome}, sottobrano {numero}").format(nome=nome, numero=brano.sottobrano)
        parti = [nome, *self._durata_nella_plancia(brano)]
        if quanti:
            parti.append(plurale(quanti, "{n} marker", "{n} marker"))
        if brano.saltato:
            # Traduttori: nell'etichetta di un brano segnato come saltato, che l'avanzamento non suona.
            parti.append(_("saltato"))
        if self.coda.loop_playlist is dati["playlist"]:
            if brano is self.coda.punto_a:
                parti.append(_("punto A del loop"))
            if brano is self.coda.punto_b:
                parti.append(_("punto B del loop"))
        if suona:
            parti.append(_("in riproduzione"))
        return ", ".join(parti)

    def _durata_nella_plancia(self, brano):
        """La durata da mostrare accanto al brano, se si sa: per un SID o un
        file delle console con piu' sottobrani, quanti sono e quanto durano in
        tutto. Come per le cartelle, il totale somma le durate note e dice a
        parte i sottobrani senza durata, che le console possono avere; senza
        nessuna durata nota resta solo il numero (issue 24)."""
        if self._ha_sottobrani(brano):
            totale = sottobrani.info(brano.percorso)["sottobrani"]
            durate = (self.schedario.scheda(brano.percorso) or {}).get("durate_sid") or []
            note = [d for d in durate if d is not None]
            if not note:
                return [plurale(totale, "{n} sottobrano", "{n} sottobrani")]
            if len(note) < totale:
                return [ngettext("{n} sottobrano, {durata} in tutto, {senza} senza durata", "{n} sottobrani, {durata} in tutto, {senza} senza durata", totale).format(
                    n=totale, durata=durata_lunga(sum(note)), senza=totale - len(note))]
            return [ngettext("{n} sottobrano, {durata} in tutto", "{n} sottobrani, {durata} in tutto", totale).format(n=totale, durata=durata_lunga(sum(note)))]
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
        self._segna_la_voce_del_file(voce, dati)
        if self._ha_sottobrani(brano) or self._marker_della_voce(dati) or self._capitoli_della_voce(dati):
            dati["caricato"] = False
            self.albero.SetItemHasChildren(voce, True)
        return voce

    def _segna_la_voce_del_file(self, voce, dati):
        chiave = dati["chiave_dell_indice"] = dati["brano"].percorso
        self._voci_dei_file.setdefault(chiave, {})[int(voce.GetID())] = voce

    def _aggiorna_etichette(self, solo=None):
        """Rinfresca le etichette di brani, file e sottobrani: saltato, loop,
        marker, in riproduzione; con solo, un insieme di percorsi, solo
        quelle dei loro file, come quando arrivano schede nuove (1.83.1). Le
        etichette cambiate si scrivono insieme, alla fine (2.7.0)."""
        cambiate = []
        if solo is None:
            voci = self._tutte_le_voci()
        else:
            voci = [v for percorso in solo for v in list(self._voci_dei_file.get(percorso, {}).values())]
        for voce in voci:
            dati = self._dati(voce)
            if not dati or dati["tipo"] not in ("brano", "file", "sottobrano"):
                continue
            if solo is not None and dati["brano"].percorso not in solo:
                continue
            nuova = self._etichetta(dati)
            if self.albero.GetItemText(voce) != nuova:
                cambiate.append((voce, nuova))
                if not self.albero.ItemHasChildren(voce) and (self._marker_della_voce(dati) or self._capitoli_della_voce(dati)):
                    dati["caricato"] = False
                    self.albero.SetItemHasChildren(voce, True)
        self._scrivi_le_etichette(cambiate)

    def _scrivi_le_etichette(self, cambiate):
        """Scrive le etichette nuove, coppie (voce, testo): poche subito, da
        ETICHETTE_A_PEZZI in su a pezzi, fra un giro e l'altro della finestra,
        che intanto risponde. Il fuoco e la selezione non si muovono."""
        if len(cambiate) < ETICHETTE_A_PEZZI and not self._etichette_in_attesa:
            for voce, nuova in cambiate:
                self.albero.SetItemText(voce, nuova)
            return
        for voce, nuova in cambiate:
            self._etichette_in_attesa[int(voce.GetID())] = (voce, nuova)
        if not self._etichette_pianificate:
            self._etichette_pianificate = True
            wx.CallLater(1, self._scrivi_un_pezzo_di_etichette)

    def _scrivi_un_pezzo_di_etichette(self):
        self._etichette_pianificate = False
        if self._chiusa:
            return
        attesa = self._cedi.trattenuto()
        if attesa:
            # Chi naviga ha la precedenza (2.7.1).
            self._etichette_pianificate = True
            wx.CallLater(max(1, round(attesa * 1000)), self._scrivi_un_pezzo_di_etichette)
            return
        fine = time.monotonic() + PEZZO_DELLE_ETICHETTE
        while self._etichette_in_attesa and time.monotonic() < fine:
            numero = next(iter(self._etichette_in_attesa))
            voce, nuova = self._etichette_in_attesa.pop(numero)
            self.albero.SetItemText(voce, nuova)
        if self._etichette_in_attesa:
            self._etichette_pianificate = True
            wx.CallLater(1, self._scrivi_un_pezzo_di_etichette)

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
        self._riscontro("non_disponibile", _("Il filtro c'è nelle playlist e nei Preferiti: porta la plancia su una playlist o su un suo brano."))

    def _modifica_filtro(self, pl):
        """Il campo del filtro; se il testo non si capisce lo spiega e lo ripropone."""
        testo = pl.filtro
        while True:
            self._domanda()
            with FinestraFiltro(self, _("Filtro di {nome}").format(nome=pl.nome), testo, ISTRUZIONI_DEL_FILTRO) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self._annullato(_("Filtro non cambiato."))
                    return
                testo = " ".join(dialogo.testo.split())
            try:
                Filtro(testo)
            except ErroreFiltro as e:
                self._riscontro("errore", _("Nel filtro non capisco: {errore}").format(errore=e))
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
            self._riscontro("filtro_messo", ngettext("Filtro di {nome}: {filtro}. Passa {n} brano su {totale}.", "Filtro di {nome}: {filtro}. Passano {n} brani su {totale}.", passano).format(
                nome=pl.nome, filtro=testo, n=passano, totale=len(pl.brani)))
        else:
            totale = len(pl.brani)
            if not totale:
                frase = _("Filtro di {nome} svuotato: la playlist è vuota.").format(nome=pl.nome)
            elif totale == 1:
                frase = _("Filtro di {nome} svuotato: passa l'unico brano.").format(nome=pl.nome)
            else:
                # Traduttori: sempre almeno due brani; uno solo ha la sua frase, passa l'unico brano.
                frase = ngettext("Filtro di {nome} svuotato: passano tutti i {n} brani.", "Filtro di {nome} svuotato: passano tutti i {n} brani.", totale).format(nome=pl.nome, n=totale)
            self._riscontro("filtro_tolto", frase)

    def _conto(self, brani):
        """'numero (durata)' di una lista di brani; i brani di cui la durata
        non si sa ancora, o non si sapra', sono detti a parte."""
        if not brani:
            return "0"
        durate = [self.schedario.durata(b) for b in brani]
        note = [d for d in durate if d is not None]
        if not note:
            # Traduttori: n e' quanti brani ha la playlist, nella sua etichetta: Rock, brani: 12 (senza durata), totali: ...
            return _("{n} (senza durata)").format(n=len(brani))
        ignote = len(durate) - len(note)
        if ignote:
            # Traduttori: n brani, che durano in tutto durata, e di ignote brani la durata non si sa.
            return _("{n} ({durata}, {ignote} senza durata)").format(n=len(brani), durata=durata_lunga(sum(note)), ignote=ignote)
        return f"{len(brani)} ({durata_lunga(sum(note))})"

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
            # Il conto ha saltato una cartella di rete che non rispondeva: non
            # e' la rete intera a tacere (collaudo della 1.85.2).
            if not files:
                return _("{nome} (conto incompleto: una cartella di rete non risponde)").format(nome=nome)
            return ngettext("{nome}, almeno {n} file: una cartella di rete non risponde", "{nome}, almeno {n} file: una cartella di rete non risponde", len(files)).format(
                nome=nome, n=len(files))
        if files == []:
            if vuota is None:
                vuota = self._e_vuota(cartella)
            return _("{nome} (vuota)").format(nome=nome) if vuota else _("{nome} (niente da suonare)").format(nome=nome)
        if not files:
            return nome
        # Il totale si somma una volta; poi lo aggiornano le variazioni dello
        # schedario. Risommare a ogni rinfresco tutti i file di un disco, per
        # ogni cartella aperta, fermava la finestra (collaudo della 1.83.0).
        totale = self._totali.get(cartella)
        if totale is None or totale[0] is not files:
            totale = self._totali[cartella] = [files, *self.schedario.totale_delle_durate(files)]
        con_durata, somma = totale[1], totale[2]
        quanti = len(files)
        if not con_durata:
            return ngettext("{nome}, {n} file", "{nome}, {n} file", quanti).format(nome=nome, n=quanti)
        if con_durata < quanti:
            return ngettext("{nome}, {n} file, {durata} in tutto, {senza} senza durata", "{nome}, {n} file, {durata} in tutto, {senza} senza durata", quanti).format(
                nome=nome, n=quanti, durata=durata_lunga(max(0.0, somma)), senza=quanti - con_durata)
        return ngettext("{nome}, {n} file, {durata} in tutto", "{nome}, {n} file, {durata} in tutto", quanti).format(nome=nome, n=quanti, durata=durata_lunga(max(0.0, somma)))

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
        cambiate = []
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
                cambiate.append((voce, nuova))
        self._scrivi_le_etichette(cambiate)
        if vuote and self._apertura is None:
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
                    # In una cartella le sottocartelle vengono prima dei file:
                    # dopo il primo file non ce ne sono altre. Guardarli tutti,
                    # con Questo PC aperto, voleva dire 126 mila voci (2.7.0).
                    ha_file = True
                    break
                if tipo not in ("brano", "sottobrano", "marker", "capitolo"):
                    dentro.append(figlio)
            if dati.get("tipo") == "cartella":
                yield voce, dati, bool(dati.get("caricato")) and ha_file
            pila.extend(reversed(dentro))

    def _ramo_di_rete_muto(self, voce, dati, errore=None):
        """Un ramo di rete che non risponde resta chiuso, da riaprire. Con un
        errore di Windows si dice il suo testo."""
        dati["caricato"] = False
        self.albero.SetItemHasChildren(voce, True)
        wx.CallAfter(self.albero.Collapse, voce)
        if errore is not None:
            motivo = f"{str(errore.strerror or errore).rstrip('.')}."
        else:
            motivo = _("il computer o il disco di rete sono spenti, la rete non c'è, o la condivisione si è fermata.")
        self._statistiche.conta("rete_muta")
        # Traduttori: motivo e' il perche', una frase con il suo punto: il testo dell'errore di Windows o quello di MeTeOra.
        self._riscontro("errore", _("{percorso} non risponde: {motivo} Riaprendo il ramo si riprova.").format(percorso=dati["percorso"], motivo=motivo))

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
        attesa = self._cedi.trattenuto()
        if attesa and self._rinfreschi and not self._chiusa:
            # Chi naviga ha la precedenza (2.7.1): il rinfresco aspetta.
            self._rinfresco_pianificato = True
            wx.CallLater(max(1, round(attesa * 1000)), self._rinfresca)
            return
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
        if pl.filtro:
            # Traduttori: i brani che passano il filtro e quelli della playlist, ciascuno come 12 (40:00).
            return _("{nome}, brani: {filtrati}, totali: {totali}, filtro: {filtro}").format(nome=pl.nome, filtrati=self._conto(filtrati), totali=self._conto(pl.brani),
                filtro=pl.filtro)
        return _("{nome}, brani: {filtrati}, totali: {totali}").format(nome=pl.nome, filtrati=self._conto(filtrati), totali=self._conto(pl.brani))

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
                self._riscontro("errore", _("Non riesco a salvare lo schedario: {errore}").format(errore=e))

    def _sotto(self, voce, radice):
        """Vero se la voce sta dentro il ramo radice."""
        while voce.IsOk():
            if voce == radice:
                return True
            voce = self.albero.GetItemParent(voce)
        return False

    def _popola_playlist(self, seleziona=None):
        """Ricostruisce il ramo Playlist dall'archivio. Tiene aperte le
        playlist che lo erano e, dalla 1.109.0, i brani e i sottobrani
        aperti dentro di loro e nei Preferiti; e se la selezione stava nel
        ramo la rimette sulla stessa voce, o su seleziona quando e' dato (una
        playlist o un brano). I brani di una playlist si caricano quando la
        si apre."""
        aperte = set()
        brani_aperti = self._brani_aperti()
        selezionato = None
        voce_selezionata = self._voce_corrente()
        dentro = False
        # Le altre voci selezionate delle playlist e dei Preferiti, per
        # riselezionarle dopo, e quelle di fuori, che restano: una selezione
        # multipla non va persa, e la voce col fuoco ci rientra solo se c'era.
        esplicita = self._selezione is not None
        fuoco_selezionato = esplicita and self._e_selezionata(voce_selezionata)
        altre_selezionate = set()
        fuori = []
        for voce in self._voci_selezionate() if esplicita else ():
            if voce == voce_selezionata:
                continue
            if self._sotto(voce, self.nodo_playlist) or self._sotto(voce, self.nodo_preferiti):
                dati = self._dati(voce) or {}
                oggetto = dati.get("brano") if dati.get("tipo") == "brano" else dati.get("playlist") if dati.get("tipo") == "playlist" else None
                if oggetto is not None:
                    altre_selezionate.add(id(oggetto))
            else:
                fuori.append(voce)
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
            selezionato = dati.get("comando") or dati.get("brano") or dati.get("playlist")
        # Un sottobrano o un marker col fuoco si ritrova dentro il suo brano
        # (tappa 9), che dalla 1.109.0 rinasce aperto, come gli altri.
        interno = None
        if seleziona is None and dentro and (self._dati(voce_selezionata) or {}).get("tipo") in ("sottobrano", "marker"):
            interno = dict(self._dati(voce_selezionata))
        if seleziona is not None:
            selezionato, dentro = seleziona, True
        if dentro and voce_selezionata != self.nodo_preferiti:
            # La selezione passa sul ramo mentre i figli spariscono, senza
            # rimbalzi su voci che stanno per essere cancellate: dai Preferiti
            # sulla loro voce, che resta, e non su Playlist. Sulla voce dei
            # Preferiti la selezione resta dov'e': spariscono solo i suoi
            # figli, e NVDA non deve sentire un fuoco su Playlist, come a fine
            # pulizia all'avvio (issue 29).
            self._seleziona(self.nodo_preferiti if self._sotto(voce_selezionata, self.nodo_preferiti) else self.nodo_playlist)
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
            self._riapri_i_brani(self.nodo_preferiti, brani_aperti)
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
                self._riapri_i_brani(nodo, brani_aperti)
                if isinstance(selezionato, Brano):
                    da_selezionare = next((v for v in self._figli(nodo) if self._dati(v).get("brano") is selezionato), da_selezionare)
        # In fondo i comandi del ramo: Nuova playlist e, dalla 1.113.0,
        # Importa playlist. Uno dei due col fuoco lo ritrova dal suo nome.
        for etichetta, nome in ((_("Nuova playlist"), "nuova_playlist"), (_("Importa playlist"), "importa_playlist")):
            comando = self.albero.AppendItem(self.nodo_playlist, etichetta, data={"tipo": "comando", "comando": nome})
            if selezionato == nome:
                da_selezionare = comando
        if dentro:
            if da_selezionare is None or self._sotto(da_selezionare, self.nodo_playlist):
                self.albero.Expand(self.nodo_playlist)
            self._seleziona(da_selezionare or self.nodo_playlist)
            if interno is not None:
                self._ritrova_dentro(interno)
        if esplicita:
            ritrovate = []
            if altre_selezionate:
                for radice in (self.nodo_preferiti, self.nodo_playlist):
                    for voce in self._tutte_le_voci(radice):
                        dati = self._dati(voce) or {}
                        oggetto = dati.get("brano") if dati.get("tipo") == "brano" else dati.get("playlist") if dati.get("tipo") == "playlist" else None
                        if oggetto is not None and id(oggetto) in altre_selezionate:
                            ritrovate.append(voce)
            corrente = self._voce_corrente()
            fuoco = [corrente] if fuoco_selezionato and corrente.IsOk() else []
            # In una volta sola: anche migliaia di voci costano una passata.
            self._imposta_la_selezione([*fuori, *ritrovate, *fuoco])

    def _brani_aperti(self):
        """Prima di ricostruire il ramo Playlist: gli id dei brani aperti
        nelle playlist aperte e nei Preferiti, e le coppie (id del brano,
        numero) dei loro sottobrani aperti, quelli con i marker. Un SID aperto
        che rinascesse chiuso farebbe saltare all'avanzamento della plancia i
        sottobrani rimasti, per esempio dopo un Ordina (1.109.0)."""
        aperti = set()
        for radice in (self.nodo_preferiti, *self._figli(self.nodo_playlist)):
            if not self.albero.IsExpanded(radice):
                continue
            for voce in self._figli(radice):
                dati = self._dati(voce) or {}
                if dati.get("tipo") != "brano" or not self.albero.IsExpanded(voce):
                    continue
                aperti.add(id(dati["brano"]))
                for figlio in self._figli(voce):
                    sotto = self._dati(figlio) or {}
                    if sotto.get("tipo") == "sottobrano" and self.albero.IsExpanded(figlio):
                        aperti.add((id(dati["brano"]), sotto["numero"]))
        return aperti

    def _riapri_i_brani(self, nodo, aperti):
        """Dopo la ricostruzione, nella playlist nodo appena riaperta, riapre i
        brani e i sottobrani che erano aperti; aperti viene da _brani_aperti."""
        if not aperti:
            return
        for voce in self._figli(nodo):
            dati = self._dati(voce) or {}
            if dati.get("tipo") != "brano" or id(dati["brano"]) not in aperti or not self.albero.ItemHasChildren(voce):
                continue
            self.albero.Expand(voce)
            for figlio in self._figli(voce):
                sotto = self._dati(figlio) or {}
                if sotto.get("tipo") == "sottobrano" and (id(dati["brano"]), sotto["numero"]) in aperti and self.albero.ItemHasChildren(figlio):
                    self.albero.Expand(figlio)

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
        freccia sinistra, ha il suo suono. Un ramo chiuso mentre si apre tutto
        lo ha chiuso chi naviga: l'apertura non lo riapre (2.7.0)."""
        evento.Skip()
        dati = self._dati(evento.GetItem()) or {}
        if dati.get("tipo") == "playlist":
            dati["caricato"] = False
        if self._apertura is not None:
            self._apertura.chiusi_a_mano.add(int(evento.GetItem().GetID()))
        if self._freccia_nell_albero:
            self._suono("ramo_chiuso")

    def _aperta_una_voce(self, evento):
        """Un ramo aperto con la freccia destra ha il suo suono, ogni volta e
        per ogni ramo. I rami che aprono i comandi, come Maiuscolo con F9 e J, no:
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
        # Un ramo di rete si legge sempre, anche se il contatore ha lasciato
        # perdere la sua radice: aprirlo e' una richiesta di chi ascolta, e la
        # lettura protetta non aspetta piu' di ATTESA_NELLA_PLANCIA fra una voce
        # e l'altra. Prima un ramo di una radice muta non si apriva per tutta
        # la sessione, e una prova di tre secondi lo dava per spento: la prima
        # lettura dell'Iliadbox ne chiede quasi tre (collaudo della 1.85.2).
        di_rete = tipo in ("cartella", "unita") and in_rete(dati["percorso"])
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
                self._segna_la_voce_del_file(sotto, figlio)
                if self._marker_della_voce(figlio):
                    figlio["caricato"] = False
                    self.albero.SetItemHasChildren(sotto, True)
            return
        if tipo in ("brano", "file", "sottobrano"):
            # Prima i capitoli, nell'ordine del file; poi i marker (1.93.0).
            elenco = self._capitoli_della_voce(dati)
            for numero, (secondi, titolo) in enumerate(elenco, 1):
                figlio = {"tipo": "capitolo", "playlist": dati["playlist"], "brano": dati["brano"], "numero": numero, "totale": len(elenco),
                    "secondi": secondi, "titolo": titolo}
                self.albero.AppendItem(voce, self._etichetta(figlio), data=figlio)
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
            self.contatore.non_risponde(dati["percorso"])
            self._ramo_di_rete_muto(voce, dati)
            return
        except OSError as e:
            if di_rete and errore_di_rete(e):
                # La rete che manca del tutto, come il router che si riavvia o
                # un nome che non si trova, risponde subito con un errore: il
                # ramo resta da riaprire, come uno che tace (revisione della
                # 1.85.5; prima ci pensava la prova dei tre secondi).
                self._ramo_di_rete_muto(voce, dati, e)
                return
            self._riscontro("errore", _("Non riesco a leggere {percorso}: {errore}").format(percorso=dati["percorso"], errore=e.strerror or e))
            self.albero.SetItemHasChildren(voce, False)
            return
        # La cartella aperta: il disco della sua lettera (1.112.0).
        self._sentinella.guarda(dati["percorso"])
        # Una cartella di rete letta: la sua radice risponde, e i conti che
        # aveva lasciato a meta' si rifanno.
        if di_rete:
            self.contatore.chiedi(self.contatore.risponde(dati["percorso"]))
        # La lettura appena fatta vale piu' di quella che il contatore tiene
        # per la sessione: se sono diverse, i conti di questa cartella e di
        # chi la contiene si rifanno.
        self.contatore.chiedi(self.contatore.rinfresca(dati["percorso"], (cartelle, files)))
        # Le cartelle che il contatore sa gia' senza niente da suonare, nemmeno
        # sotto, non si mostrano; le altre spariscono quando arriva il conto.
        # Restano quelle con un conto parziale, come fa _aggiorna_cartelle: una
        # cartella di rete muta si deve poter riaprire, per riprovarla
        # (revisione della 1.85.5).
        cartelle = [c for c in cartelle if self.contatore.files(c) != [] or c in self.contatore.parziali]
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
            self._riscontro("niente_da_suonare", _("Niente da suonare qui dentro."))

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
        computer = self.albero.AppendItem(voce, _("Computer della rete"), data={"tipo": "computer_della_rete", "caricato": False})
        self.albero.SetItemHasChildren(computer, True)
        self.albero.AppendItem(voce, _("Aggiungi un percorso di rete"), data={"tipo": "comando", "comando": "aggiungi_percorso_di_rete"})

    def _cerca_nella_rete(self, voce, dati):
        """I computer della rete, o le cartelle condivise di un computer: la
        ricerca va in disparte, e intanto il ramo mostra una voce d'attesa."""
        computer = dati["tipo"] == "computer_della_rete"
        self._statistiche.conta("ricerche_della_rete")
        self.albero.AppendItem(voce, _("Cerco i computer della rete...") if computer else _("Cerco le cartelle condivise..."), data={"tipo": "attesa"})
        testo = _("Cerco i computer della rete: può volerci qualche secondo.") if computer else _("Cerco le cartelle condivise di {nome}.").format(nome=dati["nome"])
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
            self._riscontro("non_disponibile", _("Nella rete non ho trovato computer.") if computer else _("{nome} non mostra cartelle condivise.").format(nome=dati["nome"]))
            return
        quanti = len(trovati)
        if computer:
            testo = ngettext("Trovato {n} computer nella rete.", "Trovati {n} computer nella rete.", quanti).format(n=quanti)
        else:
            testo = ngettext("{nome}: {n} cartella condivisa.", "{nome}: {n} cartelle condivise.", quanti).format(nome=dati["nome"], n=quanti)
        self._riscontro("ricerca_finita", testo)

    def _comando_aggiungi_percorso_di_rete(self):
        """Chiede un percorso di rete, lo ricorda e lo mette in Questa rete,
        anche se adesso non risponde."""
        self._domanda()
        with DialogoTesto(self, _("Il percorso di rete da aggiungere a Questa rete, per esempio \\\\server\\cartella."), _("Aggiungi un percorso di rete")) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Nessun percorso aggiunto."))
                return
            testo = dialogo.GetValue()
        percorso = testo.strip().replace("/", "\\").rstrip("\\")
        parti = percorso[2:].split("\\") if questa_rete.e_di_rete(percorso) else []
        if len(parti) < 2 or not all(parti):
            self._riscontro("errore", _("{testo} non è un percorso di rete: si scrive come \\\\server\\cartella.").format(testo=testo.strip()))
            return
        presenti = [p.casefold() for p in self.impostazioni["percorsi_di_rete"]] + [p.casefold() for _n, p in questa_rete.percorsi_salvati()]
        if percorso.casefold() in presenti:
            self._riscontro("non_disponibile", _("{percorso} è già in Questa rete.").format(percorso=percorso))
            return
        self.impostazioni["percorsi_di_rete"].append(percorso)
        self._salva_impostazioni()
        self._ricarica_la_rete(percorso)
        if questa_rete.raggiungibile(percorso):
            self._riscontro("percorso_aggiunto", _("Aggiunto a Questa rete {percorso}.").format(percorso=percorso))
        else:
            self._riscontro("percorso_aggiunto", _("Aggiunto a Questa rete {percorso}. Adesso non risponde, ma lo tengo.").format(percorso=percorso))

    def _togli_percorso_di_rete(self, percorso):
        """Toglie un percorso scritto a mano: dalle impostazioni e dalla
        plancia. I file restano dove sono."""
        self.impostazioni["percorsi_di_rete"] = [p for p in self.impostazioni["percorsi_di_rete"] if p != percorso]
        self._salva_impostazioni()
        voce = next((v for v in self._figli(self.nodo_rete) if (self._dati(v) or {}).get("percorso") == percorso), None)
        if voce is not None:
            self._togli_dalla_plancia({voce})
        self._riscontro("percorso_tolto", _("Tolto da Questa rete {percorso}. I file restano dove sono.").format(percorso=percorso))

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
            self._riscontro("non_disponibile", _("{cartella} non è più nella plancia: dentro non c'è niente da suonare.").format(cartella=cartella))
            return
        self._aggiorna_ramo(voce)

    def _aggiorna_ramo(self, voce):
        dati = self._dati(voce)
        if dati.get("tipo") == "pc":
            self.contatore.dimentica_tutto()
        elif dati.get("tipo") == "rete":
            # Aggiorna su Questa rete riprova davvero le cartelle di rete che
            # non rispondevano (revisione della 1.85.5); le cartelle di rete
            # mostrate altrove, come le unita' di rete in Questo PC, si
            # ricontano, perche' nessun'altra le richiede.
            dimenticate = set(self.contatore.dimentica_la_rete())
            if dimenticate:
                self.contatore.chiedi([d["percorso"] for _v, d, _m in self._cartelle_della_plancia() if d.get("percorso") in dimenticate])
        elif dati.get("percorso"):
            # Se la radice di rete torna viva, si rifanno anche i conti delle
            # altre sue cartelle.
            self.contatore.chiedi(self.contatore.dimentica(dati["percorso"]))
        aperto = self.albero.IsExpanded(voce)
        self.albero.Collapse(voce)
        self.albero.DeleteChildren(voce)
        dati["caricato"] = False
        self.albero.SetItemHasChildren(voce, True)
        if aperto:
            self.albero.Expand(voce)
        # Traduttori: nome e' il ramo della plancia appena riletto, come Questo PC o una cartella.
        self._riscontro("ramo_aggiornato", _("Aggiornato {nome}.").format(nome=self._nome_della_voce(voce)))

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
        elif dati and dati["tipo"] == "capitolo":
            self._suona_il_capitolo(dati)
        else:
            self._menu(voce)

    def _menu_da_evento(self, evento):
        # Dalla tastiera la voce dell'evento e' quella col fuoco; col mouse e'
        # quella su cui si e' cliccato. Il clic destro, come in Esplora
        # risorse, porta il fuoco sulla voce: se non e' selezionata diventa la
        # sola selezionata, se lo e' la selezione resta (1.98.0: prima lo
        # faceva wx, con TR_MULTIPLE).
        prima = self._profondita(self._voce_corrente())
        voce = evento.GetItem()
        if voce.IsOk() and voce != self._voce_corrente():
            if self._e_selezionata(voce):
                self._sposta_il_cursore(voce)
            else:
                self._seleziona(voce)
        self._menu(self._voce_di_lavoro())
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
                testo = _("La selezione non ha un menu.")
            elif dati.get("tipo") == "comando":
                testo = _("{voce} non ha un menu: Invio lo esegue.").format(voce=self.albero.GetItemText(voce))
            elif dati.get("tipo") == "attesa":
                testo = _("Ricerca in corso: la voce sparisce quando finisce.")
            else:
                testo = _("{voce} non ha un menu.").format(voce=self.albero.GetItemText(voce))
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
        voci.append((_("Nuova playlist"), lambda: self._aggiungi(None, brani_da_aggiungere())))
        return voci

    def _voci_del_menu(self, dati):
        tipo = dati["tipo"]
        # I dettagli della voce del menu, anche se intanto il fuoco si sposta.
        dettagli_della_voce = (_("Leggi i dettagli"), lambda: self._leggi_i_dettagli(dati))
        if tipo == "radice_playlist":
            return [(_("Nuova playlist"), self._comando_nuova_playlist), (_("Importa playlist"), self._comando_importa_playlist), dettagli_della_voce]
        if tipo == "risultati":
            return [(_("Riproduci"), lambda: self._riproduci_playlist(self.risultati)), (_("Salva come playlist"), self._salva_risultati),
                (_("Nuova ricerca"), self._ricerca_globale), (_("Ferma la ricerca"), self._ferma_ricerca), dettagli_della_voce]
        if tipo == "altri":
            return [(_("Mostra altri risultati"), lambda: self._altri_risultati(dati))]
        if tipo == "gruppo_risultati":
            gruppo = dati["gruppo"]
            return [(_("Salva come playlist"), lambda: self._salva_risultati(gruppo)), dettagli_della_voce]
        if tipo == "playlist":
            pl = dati["playlist"]
            voci = [(_("Riproduci"), lambda: self._riproduci_playlist(pl)), (_("Filtro"), lambda: self._modifica_filtro(pl))]
            if pl.filtro:
                voci.append((_("Togli il filtro"), lambda: self._imposta_filtro(pl, "")))
            # Il posto di Ordina e Mescola e' quello del punto 3.10 del piano;
            # i Preferiti non si rinominano e non si eliminano (tappa 14 c).
            preferiti = pl is self.archivio.preferiti
            if not preferiti:
                voci.append((_("Rinomina"), lambda: self._rinomina(pl)))
            voci += [(_("Ordina"), self._voci_dell_ordine(pl)), (_("Mescola"), lambda: self._mescola(pl))]
            if not preferiti:
                voci.append((_("Elimina"), lambda: self._elimina_playlist(pl)))
            return [*voci, dettagli_della_voce]
        if tipo == "brano":
            pl, brano = dati["playlist"], dati["brano"]
            return [(_("Riproduci"), lambda: self._riproduci(pl, brano)),
                (_("Sposta su"), lambda: self._sposta(pl, brano, "su")), (_("Sposta giù"), lambda: self._sposta(pl, brano, "giu")),
                (_("Sposta in cima"), lambda: self._sposta(pl, brano, "cima")), (_("Sposta in fondo"), lambda: self._sposta(pl, brano, "fondo")),
                (_("Saltato"), (lambda: self._salta(pl, brano), brano.saltato)), (_("Togli dalla playlist"), lambda: self._togli(pl, brano)),
                (_("Aggiungi ai preferiti"), lambda: self._ai_preferiti(brano)), (_("Rinomina file"), lambda: self._rinomina_file(brano)),
                *self._voci_dei_tag([brano.percorso]), (_("Manda nel cestino"), lambda: self._al_cestino(self._voce_di_lavoro()))]
        if tipo == "pc":
            return [(_("Aggiorna"), lambda: self._aggiorna_ramo(self.nodo_pc)), dettagli_della_voce]
        if tipo == "rete":
            return [(_("Aggiungi un percorso di rete"), self._comando_aggiungi_percorso_di_rete), (_("Aggiorna"), lambda: self._aggiorna_ramo(self.nodo_rete))]
        if tipo in ("computer_della_rete", "computer"):
            voce = self._voce_di_lavoro()
            return [(_("Cerca di nuovo") if tipo == "computer_della_rete" else _("Aggiorna"), lambda: self._aggiorna_ramo(voce))]
        if tipo in ("unita", "cartella"):
            cartella = dati["percorso"]
            nome = dati.get("etichetta", "").split("\\", 1)[-1] if tipo == "unita" else dati.get("nome") or os.path.basename(cartella)
            voci = [(_("Riproduci"), lambda: self._riproduci_cartella(cartella)), (_("Crea playlist da qui"), lambda: self._crea_da_qui(cartella, nome)),
                (_("Aggiungi alla playlist"), self._menu_aggiungi(lambda: [Brano(p) for p in questo_pc.file_ricorsivi(cartella)])),
                (_("Aggiorna"), lambda: self._aggiorna_cartella(cartella))]
            if dati.get("a_mano"):
                voci.append((_("Togli il percorso"), lambda: self._togli_percorso_di_rete(cartella)))
            if tipo == "unita" and self.dischi.contesa(pulizia.lettera_di(cartella)):
                # Solo dove serve: sulle lettere contese, che la pulizia salta (1.112.0, Gabriele).
                voci.append((_("Riconosci questo disco"), lambda: self._riconosci_il_disco(cartella)))
            return [*voci, dettagli_della_voce]
        if tipo == "file":
            pl, brano = dati["playlist"], dati["brano"]
            return [(_("Riproduci"), lambda: self._riproduci(pl, brano)), (_("Aggiungi alla playlist"), self._menu_aggiungi(lambda: [Brano(brano.percorso)])),
                (_("Aggiungi ai preferiti"), lambda: self._ai_preferiti(brano)), (_("Rinomina file"), lambda: self._rinomina_file(brano)),
                *self._voci_dei_tag([brano.percorso]), (_("Manda nel cestino"), lambda: self._al_cestino(self._voce_di_lavoro()))]
        if tipo == "capitolo":
            return [(_("Suona da questo capitolo"), lambda: self._suona_il_capitolo(dati))]
        if tipo == "marker":
            return [(_("Vai al marker"), lambda: self._vai_al_marker(dati)), (_("Rinomina"), lambda: self._rinomina_il_marker(dati["chiave"], dati["marker"])),
                (_("Elimina"), lambda: self._elimina_il_marker(dati["chiave"], dati["marker"], self._voce_di_lavoro()))]
        if tipo == "sottobrano":
            pl, brano, n = dati["playlist"], dati["brano"], dati["numero"]
            return [(_("Riproduci"), lambda: self._riproduci(pl, brano, n)),
                (_("Aggiungi alla playlist"), self._menu_aggiungi(lambda: [Brano(brano.percorso, sottobrano=n)])),
                (_("Aggiungi ai preferiti"), lambda: self._ai_preferiti(Brano(brano.percorso, sottobrano=n)))]
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
            self._riscontro("errore", _("Non trovo {percorso} sul disco.").format(percorso=vecchio))
            return
        cartella, nome_del_file = os.path.split(vecchio)
        nome, estensione = os.path.splitext(nome_del_file)
        if estensione:
            domanda = _("Nuovo nome del file {file}. L'estensione {estensione} resta.").format(file=nome_del_file, estensione=estensione)
        else:
            domanda = _("Nuovo nome del file {file}.").format(file=nome_del_file)
        self._domanda()
        with DialogoTesto(self, domanda, _("Rinomina file"), nome) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Nome del file non cambiato."))
                return
            # Windows toglie da se' punti e spazi in fondo al nome.
            scritto = dialogo.GetValue().strip().rstrip(". ")
        if estensione and scritto.casefold().endswith(estensione.casefold()):
            # L'estensione scritta per abitudine non si raddoppia.
            scritto = scritto[:-len(estensione)].rstrip(". ")
        if not scritto or scritto == nome:
            self._annullato(_("Nome del file non cambiato."))
            return
        problema = questo_pc.nome_non_valido(scritto)
        if problema:
            # Traduttori: problema e' la frase, con il suo punto, che dice perche' Windows non vuole il nome scritto.
            self._riscontro("errore", _("{problema} Il nome resta {file}.").format(problema=problema, file=nome_del_file))
            return
        nuovo = os.path.join(cartella, scritto + estensione)
        compagni = [(p, os.path.join(cartella, scritto + coda)) for p, coda in questo_pc.file_compagni(vecchio, m3u=formati.e_chip(vecchio))]
        occupati = [os.path.basename(d) for o, d in ((vecchio, nuovo), *compagni) if os.path.exists(d) and os.path.normcase(d) != os.path.normcase(o)]
        if occupati:
            self._riscontro("errore", _("In {cartella} c'è già {occupati}: il nome resta {file}.").format(cartella=cartella, occupati=", ".join(occupati), file=nome_del_file))
            return
        # Le durate con cui il file si riconosce per i marker, prima che cambi nome.
        if formati.ha_sottobrani(vecchio):
            durate = [d for d in (sottobrani.durate(vecchio) or []) if d]
        else:
            durate = [self._durata_dei_marker(vecchio)[0]]
        try:
            ripresa = self._rinomina_sul_disco(vecchio, nuovo)
        except OSError as e:
            self._riscontro("errore", _("Non riesco a rinominare {file}: {errore}.").format(file=nome_del_file, errore=e.strerror or e))
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
        testo = _("{vecchio} ora si chiama {nuovo}.").format(vecchio=nome_del_file, nuovo=scritto + estensione)
        if rinominati:
            # Traduttori: i file accanto con lo stesso nome, come i sottotitoli, rinominati insieme al file.
            testo += " " + _("Con lui anche {file}.").format(file=", ".join(rinominati))
        if falliti:
            testo += " " + _("Non ho potuto rinominare {file}.").format(file=", ".join(falliti))
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
        nella plancia, schedario e marker passano al nome nuovo; dalla
        1.104.0 anche il punto da riprendere e lo storico delle statistiche,
        che altrimenti la pulizia all'avvio toglierebbe (Gabriele)."""
        stesso = os.path.normcase(vecchio)
        liste = [*self.archivio.playlist, self.archivio.preferiti, self.risultati, self.coda.playlist]
        liste += [dati["playlist"] for dati in (self._dati(v) for v in self._tutte_le_voci()) if dati and dati.get("playlist") is not None]
        for pl in {id(p): p for p in liste if p is not None}.values():
            for brano in pl.brani:
                if os.path.normcase(brano.percorso) == stesso:
                    brano.percorso = nuovo
        self.schedario.rinomina(vecchio, nuovo)
        # Il punto e lo storico si scrivono subito, come playlist e marker: con
        # una chiusura a forza nel minuto, la pulizia dopo toglierebbe il nome
        # vecchio con tutta la sua storia.
        if self.posizioni.rinomina(vecchio, nuovo):
            try:
                self.posizioni.salva()
            except OSError:
                self._statistiche.conta("salvataggi_non_riusciti")
        if self._statistiche.rinomina_brano(vecchio, nuovo):
            self._salva_le_statistiche_in_disparte()
        segno = self.impostazioni["segnalibro"]
        if segno and os.path.normcase(segno["percorso"]) == stesso:
            # Anche il segnalibro passa al nome nuovo (issue 37).
            segno["percorso"] = nuovo
            self._salva_impostazioni()
        if self._pulizia is not None:
            # Il nome nuovo puo' essere uno che la pulizia ha visto mancare.
            self._toccati_in_pulizia.add(pulizia.norm(nuovo))
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
        return os.path.basename(percorsi[0]) if len(percorsi) == 1 else plurale(len(percorsi), "{n} file", "{n} file")

    def _voci_dei_tag(self, percorsi):
        """Le voci Leggi i tag e Tag del menu, per i file di cui MeTeOra sa
        scrivere i tag; nessuna per gli altri."""
        percorsi = [p for p in percorsi if tag.modificabile(p)]
        if not percorsi:
            return []
        return [(_("Leggi i tag"), lambda: self._leggi_i_tag(percorsi)), (_("Tag"), self._sottomenu_dei_tag(percorsi))]

    def _sottomenu_dei_tag(self, percorsi):
        """Il sottomenu Tag: una voce per tag, "Titolo: Love Song", che con
        Invio chiede il valore nuovo; i tag che non sono testo, come le
        copertine, si leggono ma non si scelgono."""
        with wx.BusyCursor():
            letti, errori = tag.leggi_insieme(percorsi)
        if not letti:
            return [((errori or [_("I tag non si leggono.")])[0].replace("&", "&&"), None)]
        voci = []
        for t in letti:
            # Traduttori: il valore di un tag su piu' file che non ce l'hanno uguale, o di un tag vuoto, come in Titolo: vuoto.
            valore = _("valori diversi") if t.get("diversi") else t["valore"] or _("vuoto")
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
            self._riscontro("non_disponibile", _("F11 legge i tag di un brano o di un file audio o video, e i dettagli di una cartella, di un'unità o di una playlist: scegline uno nella plancia. "
                "I SID, i MIDI, i tracker e MKV non hanno tag che MeTeOra sappia leggere."))
            return
        if self._troppi_per_i_tag(percorsi):
            return
        self._leggi_i_tag(percorsi)

    # I dettagli dei contenitori (Gabriele, 4 ottobre 2026, 1.77.0).

    def _in_disparte(self, lavoro, al_termine, nome="MeTeOra, dettagli", guasto=None):
        """lavoro() in un filo a parte, e al_termine(esito) nel filo della
        finestra; le prove lo sostituiscono per fare tutto subito. Un guasto
        del lavoro arriva ad al_termine come riga della console, o come
        guasto(errore) se c'e', e poi risale come problema interno, invece di
        lasciare chi aspetta nel silenzio. nome e' quello del filo: dalla
        1.113.0 lavora qui anche l'importazione delle playlist."""

        def fai():
            try:
                esito = lavoro()
            except Exception as errore:
                wx.CallAfter(al_termine, guasto(errore) if guasto else [_("Non riesco a raccogliere i dettagli: {errore}").format(errore=errore)])
                raise
            wx.CallAfter(al_termine, esito)

        threading.Thread(target=fai, name=nome, daemon=True).start()

    def _durata_del_percorso(self, percorso):
        return (self.schedario.scheda(percorso) or {}).get("durata")

    def _nome_del_contenitore(self, dati):
        """Il nome di un contenitore per le frasi della console, dai suoi dati."""
        tipo = dati.get("tipo")
        if tipo == "cartella":
            return dati.get("nome") or os.path.basename(dati["percorso"].rstrip("\\")) or dati["percorso"]
        if tipo == "unita":
            return dati.get("etichetta") or dati["percorso"]
        # Traduttori: i nomi dei contenitori, con l'articolo, come in Raccolgo i dettagli di la playlist Rock: ci vuole qualche secondo.
        if tipo == "playlist":
            return _("i Preferiti") if dati["playlist"] is self.archivio.preferiti else _("la playlist {nome}").format(nome=dati["playlist"].nome)
        if tipo == "risultati":
            return _("i Risultati")
        if tipo == "gruppo_risultati":
            return dati["gruppo"].nome
        return _("Questo PC") if tipo == "pc" else _("le playlist")

    def _leggi_i_dettagli(self, dati):
        """F11 su un contenitore, o Leggi i dettagli nel suo menu: tutti i
        dati che MeTeOra sa dare, nella console. Si raccolgono in un filo a
        parte, perche' una cartella grande o un'unita' si percorrono tutte; se
        ci vuole tempo, la console lo dice. Un altro F11 interrompe il conto
        di prima. dati sono quelli della voce, presi quando si e' chiesto: il
        fuoco, intanto, puo' spostarsi."""
        tipo = (dati or {}).get("tipo")
        if tipo not in TIPI_CON_I_DETTAGLI:
            self._riscontro("non_disponibile", _("I dettagli ci sono per le cartelle, le unità, Questo PC e le playlist."))
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
                # Traduttori: nome e' il contenitore, con l'articolo, come la playlist Rock o una cartella.
                self.scrivi(_("Raccolgo i dettagli di {nome}: ci vuole qualche secondo.").format(nome=nome))

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
            return (_("Preferiti") if pl is self.archivio.preferiti else _("Playlist {nome}").format(nome=pl.nome)), list(pl.brani), pl
        if tipo == "risultati":
            return _("Risultati di {ricerca}").format(ricerca=self._testo_della_ricerca), list(self.risultati.brani), None
        gruppo = dati["gruppo"]
        return _("Ramo {nome} dei Risultati").format(nome=gruppo.nome), self._brani_del_gruppo(gruppo), None

    def _dettagli_della_cartella(self, percorso, e_un_unita, fermo):
        righe = []
        if e_un_unita:
            unita = dettagli.dati_dell_unita(percorso)
            righe = dettagli.righe_dell_unita(unita)
            if not unita["pronta"]:
                return righe
        if in_rete(percorso) and not questa_rete.raggiungibile(percorso, attesa=questa_rete.ATTESA_IN_SOTTOFONDO):
            return [*righe, _("{percorso} non risponde: la rete o il disco sono spenti, o lontani.").format(percorso=percorso)]
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
                # Traduttori: nome e' l'unita', con la lettera; tipo il suo tipo, come disco locale o unita' di rete.
                righe.append(_("{nome}: {tipo}, non risponde o non ha un disco.").format(nome=nome, tipo=d["tipo"]))
                continue
            if d["tipo"] != dettagli.TIPI_DI_UNITA[4] and d["volume"] not in visti:
                visti.add(d["volume"])
                totale, libero = totale + d["totale"], libero + d["libero"]
            # Traduttori: lo spazio libero dell'unita', come in C:, disco locale, liberi 120 GB di 500 GB, 24.0% del totale.
            righe.append(_("{nome}: {tipo}, liberi {libero} di {totale}, {percentuale} del totale.").format(nome=nome, tipo=d["tipo"], libero=dettagli.dimensione(d["libero"]),
                totale=dettagli.dimensione(d["totale"]), percentuale=dettagli.percentuale(d["libero"], d["totale"])))
        testa = [plurale(len(unita), "Questo PC: {n} unità.", "Questo PC: {n} unità.")]
        if totale:
            testa.append(_("Dischi del PC, in tutto: liberi {libero} di {totale}, {percentuale} del totale.").format(libero=dettagli.dimensione(libero),
                totale=dettagli.dimensione(totale), percentuale=dettagli.percentuale(libero, totale)))
        return testa + righe

    def _nome_del_brano(self, brano):
        if brano.sottobrano:
            return _("{nome}, sottobrano {numero}").format(nome=brano.nome_del_file, numero=brano.sottobrano)
        return brano.nome_del_file

    def _dettagli_dei_brani(self, titolo, brani, pl=None, fermo=None):
        """Le righe di una playlist, dei Preferiti, dei Risultati o di un loro ramo."""
        # Traduttori: nome e' il contenitore, come Preferiti o Playlist Rock.
        righe = [ngettext("{nome}: {n} brano.", "{nome}: {n} brani.", len(brani)).format(nome=titolo, n=len(brani))]
        if pl is not None and pl.origine:
            righe.append(_("Importata da {percorso}.").format(percorso=pl.origine["percorso"]))
        if not brani:
            return righe
        censimento = dettagli.censisci_brani([b.percorso for b in brani], fermo)
        righe.append(_("Sul disco: {dimensione}.").format(dimensione=dettagli.dimensione(censimento["byte"])))
        self.schedario.chiedi([b.percorso for b in brani if self.schedario.durata(b) is None])
        righe += dettagli.righe_dei_brani(brani, self.schedario.durata, durata_lunga, nome_di=self._nome_del_brano, percorso_di=lambda b: b.percorso)
        saltati = sum(1 for b in brani if b.saltato)
        if saltati:
            # Traduttori: quanti brani sono segnati come saltati.
            righe.append(plurale(saltati, "Saltati: {n}.", "Saltati: {n}."))
        mancanti = censimento["mancanti"]
        if mancanti:
            righe.append(ngettext("Mancanti sul disco: {n}; il primo è {primo}.", "Mancanti sul disco: {n}; il primo è {primo}.", len(mancanti)).format(n=len(mancanti), primo=mancanti[0]))
        if censimento["lontani"]:
            righe.append(plurale(censimento["lontani"], "In rete, senza risposta: {n} file, che i conti non comprendono.", "In rete, senza risposta: {n} file, che i conti non comprendono."))
        if censimento["interrotto"]:
            righe.append(_("Conto interrotto: i numeri valgono per la parte letta."))
        if pl is not None and pl.filtro:
            passano = sum(1 for b in brani if self._ammesso(pl, b))
            righe.append(ngettext("Filtro: {filtro}; lo passa {n} brano.", "Filtro: {filtro}; lo passano {n} brani.", passano).format(filtro=pl.filtro, n=passano))
        return righe

    def _dettagli_delle_playlist(self, elenco, fermo=None):
        """Il ramo Playlist: quante, quanti brani in tutto, e una riga per playlist."""
        tutti = [b for _pl, brani in elenco for b in brani]
        # Traduttori: quante playlist ci sono, e quanti brani hanno in tutto, come 3 brani.
        righe = [_("Playlist: {quante}, con {brani} in tutto.").format(quante=len(elenco), brani=plurale(len(tutti), "{n} brano", "{n} brani"))]
        if tutti:
            censimento = dettagli.censisci_brani([b.percorso for b in tutti], fermo)
            righe.append(_("Sul disco: {dimensione}.").format(dimensione=dettagli.dimensione(censimento["byte"])))
        for pl, brani in elenco:
            durate = [self.schedario.durata(b) for b in brani]
            note = [d for d in durate if d is not None]
            if note:
                righe.append(ngettext("{nome}: {n} brano, {durata}.", "{nome}: {n} brani, {durata}.", len(brani)).format(nome=pl.nome, n=len(brani), durata=durata_lunga(sum(note))))
            else:
                righe.append(ngettext("{nome}: {n} brano.", "{nome}: {n} brani.", len(brani)).format(nome=pl.nome, n=len(brani)))
        return righe

    def _troppi_per_i_tag(self, percorsi):
        if len(percorsi) <= MASSIMO_DI_FILE_PER_I_TAG:
            return False
        self._riscontro("non_disponibile", ngettext("I tag si leggono e si modificano al massimo su {massimo} file insieme: la selezione ne ha {n}.",
            "I tag si leggono e si modificano al massimo su {massimo} file insieme: la selezione ne ha {n}.", len(percorsi)).format(massimo=MASSIMO_DI_FILE_PER_I_TAG, n=len(percorsi)))
        return True

    def _leggi_i_tag(self, percorsi):
        with wx.BusyCursor():
            letti, errori = tag.leggi_insieme(percorsi)
        if not letti:
            self._riscontro("errore", " ".join(errori))
            return
        # Traduttori: chi e' il nome del file, o quanti file, come 3 file.
        righe = [_("Tag di {chi}.").format(chi=self._di_chi(percorsi))]
        for t in letti:
            valore = _("valori diversi") if t.get("diversi") else t["valore"] or _("vuoto")
            righe.append(f"{t['nome']}: {valore}.")
        self._stampa("tag_letti", righe + errori)

    def _comando_modifica_i_tag(self):
        """Maiuscolo+F11: il sottomenu Tag del brano selezionato, o dei file
        selezionati, aperto subito."""
        with wx.BusyCursor():
            percorsi = self._file_dei_tag()
        if not percorsi:
            self._riscontro("non_disponibile", _("Maiuscolo+F11 modifica i tag di un brano o di un file audio o video: scegline uno nella plancia."))
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
        # Traduttori: nome e' il nome del tag, come Titolo; chi dice di quali file, come il nome di un file o 3 file.
        domanda = _("{nome} di {chi}. Un campo vuoto cancella il tag.").format(nome=nome, chi=chi)
        if t.get("diversi"):
            domanda += " " + _("I file hanno valori diversi: quello che scrivi va in tutti.")
        self._domanda()
        # Traduttori: il titolo del campo, con il nome del tag, come Titolo.
        with DialogoTesto(self, domanda, _("Tag {nome}").format(nome=nome), t["valore"]) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Tag {nome} non cambiato.").format(nome=nome))
                return
            scritto = dialogo.GetValue()
        if not t.get("diversi") and tag.pulito(scritto) == t["valore"]:
            # Un valore lasciato com'era non si controlla: un anno con l'ora,
            # o una traccia come A1, restano dove sono.
            self._annullato(_("Tag {nome} non cambiato.").format(nome=nome))
            return
        try:
            valore = tag.controlla(t["chiave"], scritto)
        except tag.ErroreTag as e:
            self._riscontro("errore", _("{errore} Il tag {nome} resta com'era.").format(errore=e, nome=nome))
            return
        if not valore and t.get("diversi") and len(percorsi) > 1 and not self._conferma(
                ngettext("Cancellare il tag {nome} da {n} file? Hanno valori diversi, che si perdono.",
                    "Cancellare il tag {nome} da {n} file? Hanno valori diversi, che si perdono.", len(percorsi)).format(nome=nome, n=len(percorsi)),
                _("Tag {nome}").format(nome=nome)):
            # Il campo dei valori diversi parte vuoto: un Invio distratto non
            # deve cancellare il tag da tutti.
            self._annullato(_("Tag {nome} non cambiato.").format(nome=nome))
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
        chi = self._di_chi(percorsi) if scritti == len(percorsi) else ngettext("{n} file su {totale}", "{n} file su {totale}", scritti).format(n=scritti, totale=len(percorsi))
        self._statistiche.conta("file_dei_tag_cambiati", scritti)
        testo = _("{nome} di {chi}: {valore}.").format(nome=nome, chi=chi, valore=valore) if valore else _("Tag {nome} cancellato da {chi}.").format(nome=nome, chi=chi)
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
            self._riscontro("non_disponibile", _("Un sottobrano non si cestina da solo: Maiuscolo+Canc si usa sul file che lo contiene."))
            return
        if tipo not in ("brano", "file"):
            self._riscontro("non_disponibile", _("Maiuscolo+Canc manda nel cestino un file, da una playlist o da una cartella, o una cartella vuota."))
            return
        pl, brano = dati["playlist"], dati["brano"]
        dove = "" if pl.temporanea else " " + _("Si toglie anche dalla playlist {nome}.").format(nome=pl.nome)
        cestino = questo_pc.ha_il_cestino(brano.percorso)
        domanda = _("Mandare nel cestino di Windows il file {percorso}?").format(percorso=brano.percorso) if cestino else _(
            "Cancellare per sempre il file {percorso}? Lì il cestino di Windows non c'è.").format(percorso=brano.percorso)
        if not self._conferma(domanda + dove, _("Manda nel cestino") if cestino else _("Cancella per sempre")):
            self._annullato(_("Il file resta dov'è."))
            return
        if self.motore.in_corso == brano.percorso:
            self.motore.stop()
        if not questo_pc.nel_cestino(brano.percorso):
            self._riscontro("errore", _("Non riesco a mandare nel cestino {percorso}.").format(percorso=brano.percorso))
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
        self._statistiche.conta("file_nel_cestino")
        self._riscontro("cestino", _("{nome} è nel cestino di Windows.").format(nome=brano.nome_del_file) if cestino else _(
            "{nome} è cancellato per sempre.").format(nome=brano.nome_del_file))

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
            self._riscontro("non_disponibile", _("{nome} è un percorso di rete, non una cartella da cestinare.").format(nome=nome))
            return
        try:
            vuota = questo_pc.cartella_vuota(percorso)
        except OSError as e:
            self._riscontro("errore", _("Non riesco a leggere {nome}: {errore}.").format(nome=nome, errore=e.strerror or e))
            return
        if not vuota:
            self._riscontro("non_disponibile", _("{nome} non è vuota: ci sono dei file, anche se MeTeOra magari non li suona. "
                "Maiuscolo+Canc manda nel cestino solo le cartelle vuote.").format(nome=nome))
            return
        cestino = questo_pc.ha_il_cestino(percorso)
        domanda = _("Mandare nel cestino di Windows la cartella vuota {percorso}?").format(percorso=percorso) if cestino else _(
            "Cancellare per sempre la cartella vuota {percorso}? Lì il cestino di Windows non c'è.").format(percorso=percorso)
        if not self._conferma(domanda, _("Manda nel cestino") if cestino else _("Cancella per sempre")):
            self._annullato(_("La cartella resta dov'è."))
            return
        if not questo_pc.nel_cestino(percorso):
            self._riscontro("errore", _("Non riesco a mandare nel cestino {percorso}.").format(percorso=percorso))
            return
        vicina = self.albero.GetNextSibling(voce)
        if not vicina.IsOk():
            vicina = self.albero.GetPrevSibling(voce)
        self._seleziona(vicina if vicina.IsOk() else genitore)
        self.albero.Delete(voce)
        # Se la radice di rete torna viva, si rifanno i conti delle altre sue
        # cartelle (revisione della 1.85.5).
        self.contatore.chiedi(self.contatore.dimentica(percorso, anche_sopra=False))
        self._riconta(os.path.dirname(percorso.rstrip("\\")))
        self._statistiche.conta("cartelle_nel_cestino")
        self._riscontro("cestino", _("La cartella {nome} è nel cestino di Windows.").format(nome=nome) if cestino else _(
            "La cartella {nome} è cancellata per sempre.").format(nome=nome))

    def _cancella(self, voce):
        dati = self._dati(voce) or {}
        if dati.get("tipo") == "playlist" and dati["playlist"] is self.archivio.preferiti:
            self._riscontro("non_disponibile", _("I Preferiti non si eliminano; Canc su un loro brano lo toglie."))
        elif dati.get("tipo") == "playlist":
            self._elimina_playlist(dati["playlist"])
        elif dati.get("tipo") == "brano":
            self._togli(dati["playlist"], dati["brano"])
        elif dati.get("tipo") == "marker":
            self._elimina_il_marker(dati["chiave"], dati["marker"], voce)
        elif dati.get("a_mano"):
            self._togli_percorso_di_rete(dati["percorso"])
        else:
            self._riscontro("non_disponibile", _("Qui Canc non cancella niente."))

    # La selezione multipla.

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
        # Traduttori: il nome della lista che fanno le voci selezionate.
        pl = Playlist(_("Selezione"), brani, cartella="")
        pl.selezione = True
        primo = self.coda.primo(pl)
        if primo is None:
            self._riscontro("niente_da_suonare", _("Nella selezione non c'è niente da suonare."))
            return
        self._suona(pl, primo)

    def _voci_del_menu_della_selezione(self):
        n = len(self._voci_selezionate())
        return [(ngettext("Riproduci {n} voce selezionata", "Riproduci le {n} voci selezionate", n).format(n=n), self._suona_selezione),
            (_("Crea playlist dalla selezione"), self._crea_dalla_selezione),
            (_("Aggiungi alla playlist"), self._menu_aggiungi(self._copie_della_selezione)), (_("Aggiungi ai preferiti"), self._selezione_ai_preferiti),
            (_("Togli dalle playlist, ed elimina le playlist e i marker selezionati"), self._cancella_selezione), (_("Manda nel cestino"), self._cestina_selezione),
            # I file e i loro tag si leggono solo alla scelta: aprire il menu
            # di una selezione con un'unita' intera non deve fermare tutto.
            (_("Leggi i tag"), self._comando_leggi_i_tag), (_("Modifica i tag"), self._comando_modifica_i_tag)]

    def _crea_dalla_selezione(self):
        brani = self._copie_della_selezione()
        if not brani:
            self._riscontro("niente_da_suonare", _("Nella selezione non c'è niente da mettere in una playlist."))
            return
        self._domanda()
        with DialogoTesto(self, _("Nome della nuova playlist:"), _("Crea playlist dalla selezione"), _("Selezione")) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Nessuna playlist creata."))
                return
            nome = dialogo.GetValue().strip() or _("Selezione")
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
            self._riscontro("gia_nei_preferiti", _("I brani selezionati sono già tutti nei Preferiti."))
            return
        self.archivio.preferiti.brani.extend(nuovi)
        self._sentinella.guarda(*(b.percorso for b in nuovi))
        self._chiedi_schede(self.archivio.preferiti)
        self._salva_archivio()
        self._popola_playlist()
        frase = ngettext("Aggiunto ai Preferiti {n} brano", "Aggiunti ai Preferiti {n} brani", len(nuovi)).format(n=len(nuovi))
        if gia:
            # Traduttori: segue la frase dei brani aggiunti ai Preferiti; n sono quelli che c'erano gia'.
            frase += ngettext("; {n} c'era già", "; {n} c'erano già", gia).format(n=gia)
        self._riscontro("preferito_aggiunto", frase + ".")

    def _cancella_selezione(self):
        """Canc su piu' voci: toglie i brani dalle loro playlist ed elimina le
        playlist selezionate, dopo una conferma. Il fuoco resta li' dove si
        lavorava, sulla prima voce vicina che resta."""
        voci = [(v, self._dati(v) or {}) for v in self._voci_selezionate()]
        da_eliminare = [d["playlist"] for _v, d in voci if d.get("tipo") == "playlist" and d["playlist"] in self.archivio.playlist]
        da_togliere = [(v, d["playlist"], d["brano"]) for v, d in voci if d.get("tipo") == "brano" and d["playlist"] not in da_eliminare]
        marker = [(v, d["chiave"], d["marker"]) for v, d in voci if d.get("tipo") == "marker"]
        if not (da_eliminare or da_togliere or marker):
            self._riscontro("non_disponibile", _("Nella selezione non c'è niente che Canc possa togliere: brani di playlist, playlist o marker."))
            return
        if da_eliminare and not self._conferma(ngettext("Eliminare {n} playlist? I file restano sul disco.", "Eliminare {n} playlist? I file restano sul disco.",
                len(da_eliminare)).format(n=len(da_eliminare)), _("Elimina playlist")):
            self._annullato(_("Eliminazione annullata."))
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
            self._seleziona(approdo)
        if marker:
            self._salva_i_marker(*{k for _v, k, _m in marker})
        self._statistiche.conta("brani_tolti", len(da_togliere))
        self._statistiche.conta("marker_tolti_selezione", tolti_marker)
        # I pezzi della frase, uniti dalle virgole, con la maiuscola al primo.
        parti = []
        if da_togliere:
            parti.append(ngettext("tolto {n} brano", "tolti {n} brani", len(da_togliere)).format(n=len(da_togliere)))
        if da_eliminare:
            parti.append(ngettext("eliminata {n} playlist", "eliminate {n} playlist", len(da_eliminare)).format(n=len(da_eliminare)))
        if tolti_marker:
            parti.append(ngettext("eliminato {n} marker", "eliminati {n} marker", tolti_marker).format(n=tolti_marker))
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
            oggetto = dati.get("comando") or dati.get("brano") or dati.get("playlist")
            interno = dict(dati)
        self._azzera_la_selezione()
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
            self._riscontro("non_disponibile", _("Maiuscolo+Canc manda nel cestino i file: seleziona brani o file."))
            return
        senza_cestino = sum(1 for _v, _pl, brano in bersagli if not questo_pc.ha_il_cestino(brano.percorso))
        avviso = ""
        if senza_cestino:
            # In rete e sulle chiavette Windows cancella per sempre: lo si dice prima.
            avviso = " " + ngettext("{n} sta dove il cestino non c'è, e si cancella per sempre.", "{n} stanno dove il cestino non c'è, e si cancellano per sempre.",
                senza_cestino).format(n=senza_cestino)
        domanda = ngettext("Mandare nel cestino di Windows {n} file? I brani escono anche dalle loro playlist.",
            "Mandare nel cestino di Windows {n} file? I brani escono anche dalle loro playlist.", len(bersagli)).format(n=len(bersagli))
        if not self._conferma(domanda + avviso, _("Manda nel cestino")):
            self._annullato(_("I file restano dove sono."))
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
        if not senza_cestino:
            testo = ngettext("Nel cestino di Windows {n} file.", "Nel cestino di Windows {n} file.", riusciti).format(n=riusciti)
        else:
            testo = ngettext("Tolti {n} file: quelli dove il cestino non c'è sono cancellati per sempre.",
                "Tolti {n} file: quelli dove il cestino non c'è sono cancellati per sempre.", riusciti).format(n=riusciti)
        if falliti:
            testo += " " + ngettext("{n} non c'è andato.", "{n} non ci sono andati.", falliti).format(n=falliti)
        self._statistiche.conta("file_nel_cestino", riusciti)
        self._riscontro("cestino", testo)

    # Le playlist.

    def _salva_archivio(self):
        try:
            self.archivio.salva()
        except OSError as e:
            self._statistiche.conta("salvataggi_non_riusciti")
            self._riscontro("errore", _("Non riesco a salvare le playlist: {errore}").format(errore=e))

    def _salva_impostazioni(self):
        try:
            self.impostazioni.salva()
        except OSError as e:
            self._statistiche.conta("salvataggi_non_riusciti")
            self._riscontro("errore", _("Non riesco a salvare le impostazioni: {errore}").format(errore=e))

    def _comando_nuova_playlist(self):
        pl = self.archivio.nuova()
        self._salva_archivio()
        self._popola_playlist(seleziona=pl)
        self._riscontro("nuova_playlist", _("Creata la playlist {nome}, vuota. Si riempie da Questo PC, con Aggiungi alla playlist.").format(nome=pl.nome))

    # L'importazione delle playlist di altri programmi (Gabriele, 20 ottobre 2026, 1.113.0).

    def _comando_importa_playlist(self):
        """Importa playlist, nel ramo Playlist e nel suo menu: la finestra dei
        file di Windows, a selezione multipla. Le playlist scelte si importano
        una per una e si salvano soltanto; la selezione va sulla prima, come
        con Nuova playlist."""
        self._domanda()
        stile = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
        with DialogoDiFile(self, _("Importa playlist"), wildcard=formati.filtro_delle_playlist(), style=stile) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Nessuna playlist importata."))
                return
            percorsi = list(dialogo.GetPaths())
        liste = [p for p in percorsi if formati.e_playlist(p)]
        altri = [os.path.basename(p) for p in percorsi if not formati.e_playlist(p)]
        if altri:
            # Traduttori: nomi sono i nomi dei file scelti, separati da virgole.
            self._riscontro("non_disponibile", ngettext("{nomi}: non è una playlist. MeTeOra importa i file m3u, m3u8 e pls.",
                "{nomi}: non sono playlist. MeTeOra importa i file m3u, m3u8 e pls.", len(altri)).format(nomi=", ".join(altri)))
        self._importa_le_playlist(liste, "seleziona")

    def _importa_le_playlist(self, percorsi, dopo=None):
        """Mette in coda le playlist M3U, M3U8 e PLS da importare, che si
        importano una per una. dopo dice cosa fare della prima del gruppo che
        si importa, o che c'era gia': "suona" per quelle che arrivano da fuori,
        da Windows o da Apri file; "seleziona" per il comando Importa
        playlist; None quando insieme arrivano altri file, che suonano loro.
        Se un'altra importazione le tiene in coda, _avvisa_se_aspetta."""
        if not percorsi:
            return
        gruppo = {"dopo": dopo}
        coda = [(percorso, gruppo) for percorso in percorsi]
        self._da_importare.extend(coda)
        self._prossima_importazione()
        if any(voce is coda[0] for voce in self._da_importare):
            self._avvisa_se_aspetta(coda)

    def _avvisa_se_aspetta(self, coda):
        """Le playlist appena arrivate aspettano un'altra importazione, per
        esempio da una condivisione lenta: se dopo un attimo la prima non e'
        ancora partita, la console lo dice una volta, perche' chi le ha
        mandate non resti nel silenzio."""

        def se_aspetta():
            lavoro = self._importazione
            in_attesa = [voce for voce in coda if any(voce is altra for altra in self._da_importare)]
            if self._chiusa or lavoro is None or not in_attesa or in_attesa[0] is not coda[0]:
                return
            nome, altre = os.path.basename(coda[0][0]), len(in_attesa) - 1
            if altre == 0:
                # Traduttori: nome e in_corso sono nomi di file di playlist; in_corso e' quella che si sta importando.
                frase = _("{nome} aspetta che finisca l'importazione di {in_corso}.").format(nome=nome, in_corso=lavoro["nome"])
            else:
                # Traduttori: nome e in_corso sono nomi di file di playlist; in_corso e' quella che si sta importando.
                frase = ngettext("{nome} e un'altra playlist aspettano che finisca l'importazione di {in_corso}.",
                    "{nome} e altre {n} playlist aspettano che finisca l'importazione di {in_corso}.", altre).format(nome=nome, n=altre, in_corso=lavoro["nome"])
            self.scrivi(frase)

        wx.CallLater(800, se_aspetta)

    def _prossima_importazione(self):
        """La prossima playlist della coda, se nessuna si sta importando:
        la lettura del file in un filo a parte, poi _playlist_letta."""
        if self._chiusa or self._importazione is not None or not self._da_importare:
            return
        percorso, gruppo = self._da_importare.pop(0)
        lavoro = self._importazione = {"percorso": percorso, "nome": os.path.basename(percorso), "gruppo": gruppo}
        self._avvisa_se_tarda(lavoro, _("Leggo {nome}: ci vuole qualche secondo.").format(nome=lavoro["nome"]))
        self._in_disparte(lambda: importazione.leggi(percorso), lambda letta: self._esito_dell_importazione(self._playlist_letta, lavoro, letta),
            "MeTeOra, importazione", guasto=self._guasto_dell_importazione)

    @staticmethod
    def _guasto_dell_importazione(errore):
        return {"errore": f"{type(errore).__name__}: {errore}" if str(errore) else type(errore).__name__}

    def _avvisa_se_tarda(self, lavoro, testo):
        """Se la lettura o il controllo dei file tardano, come su una
        condivisione lenta, la console lo dice una volta."""
        segno = lavoro["attesa"] = object()

        def se_tarda():
            if not self._chiusa and self._importazione is lavoro and lavoro.get("attesa") is segno:
                self.scrivi(testo)

        wx.CallLater(800, se_tarda)

    def _esito_dell_importazione(self, funzione, lavoro, *argomenti):
        """L'esito del filo dell'importazione e' arrivato: l'avviso di chi
        tarda non serve piu', anche se funzione aspetta la fine di un dialogo."""
        lavoro["attesa"] = None
        self._quando_libera(funzione, lavoro, *argomenti)

    def _quando_libera(self, funzione, *argomenti):
        """funzione quando la finestra non ha un dialogo aperto, come per la
        pulizia all'avvio: una domanda o la plancia che cambia non arrivano
        sotto le mani di un'altra finestra, come le impostazioni."""
        if self._chiusa:
            return
        if not ctypes.windll.user32.IsWindowEnabled(self.GetHandle()):
            wx.CallLater(500, self._quando_libera, funzione, *argomenti)
            return
        funzione(*argomenti)

    def _importazione_finita(self, lavoro):
        if self._importazione is lavoro:
            self._importazione = None
        self._prossima_importazione()

    def _scrivi_l_importazione(self, evento, righe):
        """Il resoconto: una riga sola come ogni riscontro, piu' righe con
        l'ora solo in fondo, senza spostare il fuoco."""
        self._domanda_viva = None
        if len(righe) == 1:
            self._riscontro(evento, righe[0])
        else:
            self._stampa(evento, righe, porta_il_fuoco=False)

    def _playlist_letta(self, lavoro, letta):
        """Il file della playlist e' letto. Se una playlist viene gia' da lui
        e il file non e' cambiato, si usa quella; se e' cambiato, si chiede se
        rileggerlo, e No o Esc tengono quella che c'e'. Altrimenti i file
        delle voci si controllano in un filo a parte, come nella pulizia."""
        if self._chiusa or self._importazione is not lavoro:
            return
        percorso, nome = lavoro["percorso"], lavoro["nome"]
        if "errore" in letta:
            self._riscontro("errore", _("Non riesco a leggere {nome}: {errore}").format(nome=nome, errore=letta["errore"]))
            self._importazione_finita(lavoro)
            return
        if letta["libgme"]:
            # Traduttori: nome e' il file della playlist, musica il file di musica delle console a cui appartiene.
            self._riscontro("niente_da_suonare", _("Niente da importare da {nome}: è la lista dei brani di {musica}, che MeTeOra usa già da sola "
                "quando suona {musica}.").format(nome=nome, musica=letta["libgme"]))
            self._importazione_finita(lavoro)
            return
        esistente = self.archivio.dall_origine(percorso)
        if esistente is not None:
            if not importazione.cambiata(esistente.origine, letta["origine"]):
                self._riscontro("playlist_gia_importata", _("La playlist {nome} viene già da {percorso}.").format(nome=esistente.nome, percorso=percorso))
                self._dopo_l_importazione(lavoro, esistente)
                return
            if not self._conferma(_("{nome} è cambiato dopo l'importazione. Rileggerlo, perdendo le modifiche fatte in MeTeOra?").format(nome=nome), _("Importa playlist")):
                self._annullato(_("La playlist {nome} resta com'è.").format(nome=esistente.nome))
                self._dopo_l_importazione(lavoro, esistente)
                return
        voci = letta["voci"]
        if not voci:
            if esistente is not None:
                # Si' alla rilettura di un file svuotato: resta quella che
                # c'e', e va avanti come con No.
                # Traduttori: nome e' il file letto, playlist la playlist di MeTeOra che ne viene.
                self._riscontro("niente_da_suonare", _("Niente da rileggere da {nome}: non ha nessuna voce, e la playlist {playlist} resta com'è.").format(
                    nome=nome, playlist=esistente.nome))
                self._dopo_l_importazione(lavoro, esistente)
                return
            self._riscontro("niente_da_suonare", _("Niente da importare da {nome}: non ha nessuna voce.").format(nome=nome))
            self._importazione_finita(lavoro)
            return
        candidati = [voce.percorso for voce in voci if voce.motivo is None]
        if not candidati:
            self._playlist_controllata(lavoro, letta, esistente, {"mancanti": set(), "saltate": {}})
            return
        self._avvisa_se_tarda(lavoro, _("Controllo i file di {nome}: ci vuole qualche secondo.").format(nome=nome))
        self._in_disparte(lambda: pulizia.controlla(candidati, fermo=lambda: self._chiusa, cedi=self._cedi),
            lambda esito: self._esito_dell_importazione(self._playlist_controllata, lavoro, letta, esistente, esito), "MeTeOra, importazione",
            guasto=self._guasto_dell_importazione)

    def _playlist_controllata(self, lavoro, letta, esistente, esito):
        """I file delle voci sono controllati: si tolgono quelli che mancano
        su una radice che risponde, e si tengono quelli delle radici che non
        rispondono. Nasce la playlist nuova, con il nome del file, o quella
        che c'era prende i brani nuovi; la console dice cosa e' arrivato e
        cosa si e' saltato."""
        if self._chiusa or self._importazione is not lavoro:
            return
        percorso, nome = lavoro["percorso"], lavoro["nome"]
        if "errore" in esito:
            self._riscontro("errore", _("Non riesco a controllare i file di {nome}: {errore}").format(nome=nome, errore=esito["errore"]))
            self._importazione_finita(lavoro)
            return
        if esistente is not None and esistente not in self.archivio.playlist:
            # Eliminata mentre si controllavano i file: si importa da capo.
            esistente = None
        percorsi, scartate, tenute = importazione.esito(letta["voci"], esito["mancanti"], esito.get("saltate"))
        saltate = [frase_delle_saltate(scartate), frase_delle_tenute(tenute)]
        if not percorsi:
            if esistente is not None:
                testa = _("Niente da rileggere da {nome}: la playlist {playlist} resta com'è.").format(nome=nome, playlist=esistente.nome)
            else:
                testa = _("Niente da importare da {nome}.").format(nome=nome)
            self._scrivi_l_importazione("niente_da_suonare", [" ".join(t for t in (testa, *saltate) if t), *righe_delle_saltate(scartate)])
            if esistente is not None:
                # Resta quella che c'e', e va avanti come con No.
                self._dopo_l_importazione(lavoro, esistente)
            else:
                self._importazione_finita(lavoro)
            return
        brani = [Brano(p) for p in percorsi]
        seleziona = lavoro["gruppo"]["dopo"] == "seleziona"
        if esistente is not None:
            # Nome, posto, filtro e tasto cifra restano; cambiano i brani. Il
            # brano che suona continua, e poi si riparte dal primo, come
            # quando si toglie il brano corrente; il loop su di lei si toglie.
            # Il fuoco su uno dei suoi brani di prima va sulla playlist.
            pl = esistente
            dati = self._dati(self._voce_corrente()) or {}
            seleziona = seleziona or (dati.get("playlist") is pl and dati.get("tipo") != "playlist")
            pl.brani[:] = brani
            pl.origine = letta["origine"]
            if self.coda.loop_playlist is pl:
                self.coda.togli_loop()
            evento, testa = "playlist_riletta", ngettext("Riletta la playlist {nome}: {n} brano, da {percorso}.", "Riletta la playlist {nome}: {n} brani, da {percorso}.",
                len(brani)).format(nome=pl.nome, n=len(brani), percorso=percorso)
        else:
            # Traduttori: il nome di una playlist importata da un file senza nome.
            pl = self.archivio.nuova(os.path.splitext(nome)[0].strip() or _("Playlist"), percorsi)
            pl.origine = letta["origine"]
            self._statistiche.conta("playlist_importate")
            self._statistiche.conta("brani_importati", len(brani))
            evento, testa = "playlist_creata", ngettext("Importata la playlist {nome}: {n} brano, da {percorso}.", "Importata la playlist {nome}: {n} brani, da {percorso}.",
                len(brani)).format(nome=pl.nome, n=len(brani), percorso=percorso)
        self._chiedi_schede(pl)
        self._salva_archivio()
        self._popola_playlist(seleziona=pl if seleziona else None)
        if lavoro["gruppo"]["dopo"] == "seleziona":
            lavoro["gruppo"]["dopo"] = None
        self._scrivi_l_importazione(evento, [" ".join(t for t in (testa, *saltate) if t), *righe_delle_saltate(scartate)])
        self._dopo_l_importazione(lavoro, pl)

    def _dopo_l_importazione(self, lavoro, pl):
        """La playlist importata, o quella che c'era gia': la prima del gruppo
        suona, se arriva da fuori, dopo il suono del resoconto; dal comando
        Importa playlist la selezione va su di lei. Poi la prossima della coda."""
        gruppo = lavoro["gruppo"]
        if gruppo["dopo"] == "suona":
            gruppo["dopo"] = None
            self._dopo_il_suono(self._suona_l_importata, pl)
        elif gruppo["dopo"] == "seleziona":
            gruppo["dopo"] = None
            self._popola_playlist(seleziona=pl)
        self._importazione_finita(lavoro)

    def _suona_l_importata(self, pl):
        """Come un file aperto da Windows: suona subito, dal primo brano che si puo' suonare."""
        if self._chiusa or pl not in self.archivio.playlist:
            return
        brano = self.coda.primo(pl)
        if brano is None:
            self._riscontro("niente_da_suonare", _("La playlist {nome} non ha brani da suonare.").format(nome=pl.nome))
            return
        self._suona(pl, brano, "file_aperto")

    def _aggiungi(self, pl, percorsi_da_aggiungere, nome=None):
        if not percorsi_da_aggiungere:
            self._riscontro("niente_da_suonare", _("Non c'è niente da aggiungere: nessun file supportato."))
            return
        nuova = pl is None
        if nuova:
            pl = self.archivio.nuova(nome)
        pl.brani.extend(b if isinstance(b, Brano) else Brano(b) for b in percorsi_da_aggiungere)
        # Il disco delle lettere dei brani aggiunti (1.112.0).
        self._sentinella.guarda(*(b.percorso for b in pl.brani[-len(percorsi_da_aggiungere):]))
        self._statistiche.conta("brani_aggiunti", len(percorsi_da_aggiungere))
        self._statistiche.conta("aggiunte")
        self._chiedi_schede(pl)
        self._salva_archivio()
        self._popola_playlist()
        n = len(percorsi_da_aggiungere)
        ora = plurale(len(pl.brani), "{n} brano", "{n} brani")
        if nuova:
            # Traduttori: ora sono i brani che la playlist ha adesso, come 12 brani.
            frase = ngettext("Creata la playlist {nome}: {n} brano, ora {ora}.", "Creata la playlist {nome}: {n} brani, ora {ora}.", n).format(nome=pl.nome, n=n, ora=ora)
        else:
            # Traduttori: ora sono i brani che la playlist ha adesso, come 12 brani.
            frase = ngettext("Aggiunto alla playlist {nome}: {n} brano, ora {ora}.", "Aggiunti alla playlist {nome}: {n} brani, ora {ora}.", n).format(
                nome=pl.nome, n=n, ora=ora)
        self._riscontro("playlist_creata" if nuova else "brano_aggiunto", frase)

    def _ai_preferiti(self, brano):
        """Mette nei Preferiti una copia del brano: stesso file e sottobrano."""
        if brano is None:
            self._riscontro("non_disponibile", _("F4 mette nei Preferiti il brano selezionato: scegline uno in una playlist o in una cartella."))
            return
        if self.archivio.nei_preferiti(brano):
            self._riscontro("gia_nei_preferiti", _("{nome} è già nei Preferiti.").format(nome=brano.nome_del_file))
            return
        self.archivio.preferiti.brani.append(Brano(brano.percorso, sottobrano=brano.sottobrano))
        self._sentinella.guarda(brano.percorso)
        self._chiedi_schede(self.archivio.preferiti)
        self._salva_archivio()
        self._popola_playlist()
        n = len(self.archivio.preferiti.brani)
        self._riscontro("preferito_aggiunto", ngettext("{nome} è nei Preferiti, che ora hanno {n} brano.", "{nome} è nei Preferiti, che ora hanno {n} brani.", n).format(
            nome=brano.nome_del_file, n=n))

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
            self._riscontro("non_disponibile", _("Qui non c'è niente in cui cercare: Ctrl con la barra rovesciata cerca in tutto MeTeOra."))
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
            # I posti in cui si cerca entrano nelle frasi della ricerca, come
            # Ricerca in Musica o Cerco rock nei Preferiti.
            if tipo in ("cartella", "unita"):
                # Traduttori: dove si cerca, come in Ricerca in Musica; nome e' una cartella o un'unita'.
                return _("in {nome}").format(nome=self._nome_della_voce(voce)), [], [dati["percorso"]]
            if tipo == "pc":
                # Traduttori: dove si cerca, come in Ricerca in Questo PC.
                return _("in Questo PC"), [], None
            if tipo == "radice_playlist":
                # Traduttori: dove si cerca, come in Ricerca nelle playlist.
                return _("nelle playlist"), [(b, _("Playlist {nome}").format(nome=pl.nome)) for pl in self.archivio.playlist for b in pl.brani], []
            if tipo in ("risultati", "gruppo_risultati"):
                # Traduttori: dove si cerca, come in Ricerca nei Risultati.
                return _("nei Risultati"), [(b, None) for b in self._brani_del_gruppo(dati["gruppo"])], []
            if tipo == "rete":
                percorsi = self._percorsi_di_questa_rete()
                # Traduttori: dove si cerca, come in Ricerca in Questa rete.
                return (_("in Questa rete"), [], percorsi) if percorsi else None
            if tipo == "computer":
                percorsi = [d["percorso"] for d in (self._dati(v) for v in self._figli(voce)) if d.get("tipo") == "cartella"]
                return (_("in {nome}").format(nome=dati["nome"]), [], percorsi) if percorsi else None
            if tipo in ("playlist", "brano", "file", "sottobrano", "marker"):
                pl = dati["playlist"]
                if pl is self.risultati:
                    voce = self.albero.GetItemParent(voce)
                    continue
                if pl is self.archivio.preferiti:
                    # Traduttori: dove si cerca, come in Ricerca nei Preferiti.
                    return _("nei Preferiti"), [(b, _("Preferiti")) for b in pl.brani], []
                if pl in self.archivio.playlist:
                    # Traduttori: dove si cerca, come in Ricerca nella playlist Rock.
                    return _("nella playlist {nome}").format(nome=pl.nome), [(b, _("Playlist {nome}").format(nome=pl.nome)) for b in pl.brani], []
                if pl.cartella:
                    # Il file di una cartella: la cartella, con le sue sottocartelle.
                    return _("in {nome}").format(nome=os.path.basename(pl.cartella.rstrip(chr(92))) or pl.cartella), [], [pl.cartella]
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
        # Traduttori: dove e' il posto in cui si cerca, come in Musica o nei Preferiti.
        titolo = _("Ricerca in tutto MeTeOra") if dove == OVUNQUE else _("Ricerca {dove}").format(dove=dove)
        # Traduttori: dove e' il posto in cui si cerca, come in Musica o nei Preferiti.
        istruzioni = ISTRUZIONI_DELLA_RICERCA if dove == OVUNQUE else [_("Puoi usare questi comandi per comporre la ricerca, {dove}.").format(dove=dove), *_GRAMMATICA_DEL_FILTRO]
        while True:
            self._domanda()
            with FinestraFiltro(self, titolo, testo, istruzioni) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self._annullato(_("Ricerca annullata."))
                    return
                testo = " ".join(dialogo.testo.split())
            if not testo:
                self._riscontro("errore", _("Scrivi cosa cercare."))
                continue
            try:
                filtro = Filtro(testo)
            except ErroreFiltro as e:
                self._riscontro("errore", _("Nella ricerca non capisco: {errore}").format(errore=e))
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
            brani = [(b, _("Preferiti")) for b in self.archivio.preferiti.brani]
            brani += [(b, _("Playlist {nome}").format(nome=pl.nome)) for pl in self.archivio.playlist for b in pl.brani]
        else:
            # I brani si prendono prima che i Risultati, se sono loro, si svuotino.
            brani = list(brani)
        self.risultati = Playlist(_("Risultati"), cartella="")
        # Dove sono riconosce i Risultati anche dopo una ricerca nuova, se il
        # brano che suona viene da quelli di prima (tappa 14 b).
        self.risultati.risultati = True
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
            self.nodo_risultati = self.albero.InsertItem(self.albero.GetRootItem(), self.nodo_preferiti, _("Risultati"))
        else:
            self.albero.Collapse(self.nodo_risultati)
            self.albero.DeleteChildren(self.nodo_risultati)
        self.albero.SetItemData(self.nodo_risultati, self._dati_del_gruppo("risultati", self._albero_dei_risultati.radice))
        self.albero.SetItemHasChildren(self.nodo_risultati, True)
        self._aggiorna_risultati()
        self._ricerca.avvia()
        self._statistiche.conta("ricerche_ovunque" if dove == OVUNQUE else "ricerche_nel_ramo")
        self._inizio_della_ricerca = time.monotonic()
        self._ricerca_contata = False
        # Traduttori: testo e' cio' che si cerca, dove il posto in cui si cerca, come nei Preferiti.
        self._riscontro("ricerca_avviata", _("Cerco {testo} {dove}. I Risultati si riempiono mentre cerco.").format(testo=testo, dove=dove))

    def _etichetta_dei_risultati(self):
        trovati = self._ricerca.quanti() if self._ricerca else 0
        testo = self._testo_della_ricerca
        if self._ricerca is None or self._ricerca.finita:
            return ngettext("Risultati di {testo}: {n} trovato", "Risultati di {testo}: {n} trovati", trovati).format(testo=testo, n=trovati)
        if self._ricerca.fermata:
            return ngettext("Risultati di {testo}: {n} trovato, ricerca fermata", "Risultati di {testo}: {n} trovati, ricerca fermata", trovati).format(testo=testo, n=trovati)
        return ngettext("Risultati di {testo}: {n} trovato, ricerca in corso", "Risultati di {testo}: {n} trovati, ricerca in corso", trovati).format(testo=testo, n=trovati)

    def _dati_del_gruppo(self, tipo, gruppo):
        """I dati di un ramo dei Risultati: quanti suoi rami e brani sono gia'
        nella plancia, e fin dove arriva la sua pagina."""
        return {"tipo": tipo, "playlist": self.risultati, "gruppo": gruppo, "caricato": False, "rami": 0, "brani": 0,
            "pagina": PAGINA_DEI_RISULTATI}

    def _etichetta_del_gruppo(self, gruppo):
        return ngettext("{nome}, {n} risultato", "{nome}, {n} risultati", gruppo.totale).format(nome=gruppo.nome, n=gruppo.totale)

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
            mostrati = min(restano, PAGINA_DEI_RISULTATI)
            testo = _("Mostra l'ultimo risultato") if restano == 1 else ngettext("Mostra {n} altro risultato, ne restano {restano}",
                "Mostra altri {n} risultati, ne restano {restano}", mostrati).format(n=mostrati, restano=restano)
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
            self._riscontro("non_disponibile", _("Mostra altri risultati si usa sulla sua voce, in fondo a un ramo dei Risultati."))
            return
        dati = self._dati(ramo)
        prima = dati["rami"] + dati["brani"]
        dati["pagina"] += PAGINA_DEI_RISULTATI
        self._riempi_gruppo(ramo)
        # La selezione va sul primo dei risultati appena mostrati.
        figli = list(self._figli(ramo))
        if len(figli) > prima:
            self._seleziona(figli[prima])
        self._riscontro("altri_risultati", ngettext("Mostrati {n} risultati su {totale} in {nome}.", "Mostrati {n} risultati su {totale} in {nome}.", dati["brani"]).format(
            n=dati["brani"], totale=len(dati["gruppo"].brani), nome=dati["gruppo"].nome))

    def _risultati_arrivati(self):
        if self._chiusa or self._ricerca is None:
            return
        self._aggiorna_risultati()
        if self._ricerca.finita:
            dove = "" if self._dove_si_cerca == OVUNQUE else f" {self._dove_si_cerca}"
            muti = self._ricerca.senza_risposta
            # Le radici di rete che non hanno risposto, con il nome di Questa rete se ce l'hanno.
            nomi = {os.path.normcase(p): n for n, p in questa_rete.percorsi_salvati()} if muti else {}
            silenzio = ""
            if muti:
                silenzio = " " + ngettext("In rete non ha risposto: {nomi}.", "In rete non hanno risposto: {nomi}.", len(muti)).format(
                    nomi=", ".join(nomi.get(os.path.normcase(p), p) for p in muti))
            saltate = len(self._ricerca.cartelle_mute)
            if saltate:
                silenzio += " " + ngettext("In rete una cartella non ha risposto, e la ricerca è andata avanti senza.",
                    "In rete {n} cartelle non hanno risposto, e la ricerca è andata avanti senza.", saltate).format(n=saltate)
            self._conta_la_ricerca(dove)
            n = len(self.risultati.brani)
            if self._dove_si_cerca == OVUNQUE:
                finita = ngettext("Ricerca di {testo} finita: {n} risultato.", "Ricerca di {testo} finita: {n} risultati.", n).format(testo=self._testo_della_ricerca, n=n)
            else:
                # Traduttori: testo e' cio' che si cerca, dove il posto in cui si cerca, come nei Preferiti.
                finita = ngettext("Ricerca di {testo} {dove} finita: {n} risultato.", "Ricerca di {testo} {dove} finita: {n} risultati.", n).format(
                    testo=self._testo_della_ricerca, dove=self._dove_si_cerca, n=n)
            self._riscontro("ricerca_finita", finita + silenzio)
            # Lo schedario legge senza tempo massimo: i file delle radici che
            # non hanno risposto lo terrebbero fermo.
            mute = tuple(os.path.normcase(p).rstrip("\\") + "\\" for p in muti)
            self.schedario.chiedi([b.percorso for b in self.risultati.brani if not os.path.normcase(b.percorso).startswith(mute)])

    def _ferma_ricerca(self):
        if self._ricerca is None or self._ricerca.finita or self._ricerca.fermata:
            self._riscontro("non_disponibile", _("Non c'è una ricerca in corso."))
            return
        self._ricerca.ferma()
        self._aggiorna_risultati()
        self._riscontro("ricerca_fermata", ngettext("Ricerca fermata: {n} risultato.", "Ricerca fermata: {n} risultati.", len(self.risultati.brani)).format(
            n=len(self.risultati.brani)))

    def _brani_del_gruppo(self, gruppo):
        """I risultati di un ramo e di tutti quelli che contiene, in ordine."""
        brani = list(gruppo.brani)
        for sotto in gruppo.elenco_dei_gruppi:
            brani.extend(self._brani_del_gruppo(sotto))
        return brani

    def _salva_risultati(self, gruppo=None):
        """Salva come playlist tutti i Risultati, o soltanto un loro ramo."""
        if not self.risultati or not self.risultati.brani:
            self._riscontro("niente_da_suonare", _("Non ci sono risultati da salvare."))
            return
        # Traduttori: il nome proposto per la playlist dei risultati; testo e' cio' che si e' cercato.
        proposta = _("Ricerca {testo}").format(testo=self._testo_della_ricerca) if gruppo is None else f"{gruppo.nome} {self._testo_della_ricerca}"
        self._domanda()
        with DialogoTesto(self, _("Nome della nuova playlist:"), _("Salva i risultati"), proposta) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Risultati non salvati."))
                return
            # Traduttori: il nome della playlist dei risultati, se il campo resta vuoto.
            nome = dialogo.GetValue().strip() or _("Ricerca")
        self._aggiorna_risultati()
        brani = self.risultati.brani if gruppo is None else self._brani_del_gruppo(gruppo)
        self._statistiche.conta("playlist_dalla_ricerca")
        self._aggiungi(None, [Brano(b.percorso, sottobrano=b.sottobrano) for b in brani], nome=nome)

    def _crea_da_qui(self, cartella, nome):
        with wx.BusyCursor():
            files = questo_pc.file_ricorsivi(cartella)
        if not files:
            self._riscontro("niente_da_suonare", _("In {cartella} non c'è niente da suonare.").format(cartella=cartella))
            return
        pl = self.archivio.nuova(nome or _("Playlist"), files)
        self._sentinella.guarda(*files)
        self._statistiche.conta("playlist_da_una_cartella")
        self._chiedi_schede(pl)
        self._salva_archivio()
        self._popola_playlist()
        self._riscontro("playlist_creata", ngettext("Creata la playlist {nome} con {n} brano.", "Creata la playlist {nome} con {n} brani.", len(files)).format(
            nome=pl.nome, n=len(files)))

    def _rinomina(self, pl):
        self._domanda()
        with DialogoTesto(self, _("Nuovo nome della playlist:"), _("Rinomina"), pl.nome) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Nome della playlist non cambiato."))
                return
            nome = dialogo.GetValue().strip()
        if not nome or nome == pl.nome:
            self._annullato(_("Nome della playlist non cambiato."))
            return
        if any(p is not pl and p.nome.casefold() == nome.casefold() for p in self.archivio.playlist):
            self._riscontro("errore", _("C'è già una playlist che si chiama {nome}.").format(nome=nome))
            return
        vecchio, pl.nome = pl.nome, nome
        self._salva_archivio()
        segno = self.impostazioni["segnalibro"]
        if segno and segno["lista"] == "playlist" and segno["nome"] == vecchio:
            # Il segnalibro segue la sua playlist (issue 37).
            segno["nome"] = nome
            self._salva_impostazioni()
        self._popola_playlist(seleziona=pl)
        self._riscontro("playlist_rinominata", _("La playlist {vecchio} ora si chiama {nome}.").format(vecchio=vecchio, nome=nome))

    def _elimina_playlist(self, pl):
        domanda = ngettext("Eliminare la playlist {nome}, con {n} brano? I file restano sul disco.", "Eliminare la playlist {nome}, con {n} brani? I file restano sul disco.",
            len(pl.brani)).format(nome=pl.nome, n=len(pl.brani))
        if not self._conferma(domanda, _("Elimina playlist")):
            self._annullato(_("Eliminazione annullata."))
            return
        indice = self.archivio.playlist.index(pl)
        self.archivio.elimina(pl)
        self._salva_archivio()
        vicina = self.archivio.playlist[min(indice, len(self.archivio.playlist) - 1)] if self.archivio.playlist else "nuova_playlist"
        self._popola_playlist(seleziona=vicina)
        self._riscontro("playlist_eliminata", _("Eliminata la playlist {nome}.").format(nome=pl.nome))

    def _sposta(self, pl, brano, dove):
        if not pl.sposta(brano, dove):
            self._riscontro("nessun_altro_brano", _("Il brano è già lì."))
            return
        self._salva_archivio()
        self._popola_playlist(seleziona=brano)
        i = pl.indice(brano)
        # Traduttori: posto e' il numero del brano nella playlist, totale quanti ne ha.
        self._riscontro("brano_spostato", _("{nome} ora è il {posto} di {totale}.").format(nome=brano.nome, posto=i + 1, totale=len(pl.brani)))

    # Ordina e Mescola, nel menu della playlist e dei Preferiti (tappa 14 c,
    # decisa da Gabriele il 20 ottobre 2026). Si riordina tutta la playlist,
    # anche i brani che il filtro nasconde; niente riproduzione, niente
    # conferme, il fuoco resta sulla playlist e si salva subito, come Sposta.

    def _voci_dell_ordine(self, pl):
        """Il sottomenu Ordina: i sette criteri; Ordine di prima, solo dopo
        un Ordina, un Inverti l'ordine o un Mescola; e in fondo Inverti
        l'ordine."""
        voci = [(etichetta, lambda c=criterio: self._ordina(pl, c)) for criterio, (etichetta, _dato) in CRITERI.items()]
        if pl.ordine_di_prima is not None:
            voci.append((_("Ordine di prima"), lambda: self._ordine_di_prima(pl)))
        voci.append((_("Inverti l'ordine"), lambda: self._inverti(pl)))
        return voci

    # Le righe di Ordina e Mescola sono frasi intere, una per i Preferiti e
    # una per le playlist: Rock e' una playlist, i Preferiti sono loro (3.0.0).

    def _troppo_pochi(self, pl, niente):
        """Con meno di due brani non c'e' niente da riordinare: lo dice, e
        torna vero. niente e' la fine della frase, come niente da ordinare."""
        if len(pl.brani) >= 2:
            return False
        preferiti = pl is self.archivio.preferiti
        if not pl.brani:
            quanti = _("Nei Preferiti non ci sono brani") if preferiti else _("In {nome} non ci sono brani").format(nome=pl.nome)
        else:
            quanti = _("Nei Preferiti c'è un brano solo") if preferiti else _("In {nome} c'è un brano solo").format(nome=pl.nome)
        # Traduttori: quanti dice che la playlist e' vuota o ha un brano solo, niente e' come niente da ordinare.
        self._riscontro("non_disponibile", _("{quanti}: {niente}.").format(quanti=quanti, niente=niente))
        return True

    def _che_suona_in(self, pl):
        """Il brano di pl che suona o e' in pausa, o None."""
        corrente = self.coda.corrente
        if self.motore.in_corso and self.coda.playlist is pl and corrente is not None and pl.indice(corrente) is not None:
            return corrente
        return None

    def _posto_come_la_plancia(self, pl, brano):
        """Il posto del brano, come il 57 di 340: con un filtro, se il brano
        lo passa, fra i brani che la plancia mostra, e lo dice."""
        if pl.filtro and self._ammesso(pl, brano):
            visibili = [b for b in pl.brani if self._ammesso(pl, b)]
            # Traduttori: il posto del brano fra quelli che il filtro lascia vedere, come il 57 di 340 col filtro.
            return _("il {posto} di {totale} col filtro").format(posto=next(i for i, b in enumerate(visibili) if b is brano) + 1, totale=len(visibili))
        # Traduttori: il posto del brano nella playlist, come il 57 di 340.
        return _("il {posto} di {totale}").format(posto=pl.indice(brano) + 1, totale=len(pl.brani))

    def _ordina(self, pl, criterio):
        """Una voce di Ordina: i brani senza il dato vanno in fondo, in ordine
        di percorso, e la console dice quanti sono, con a parte quelli che lo
        schedario non ha ancora letto; le loro schede si chiedono allo
        schedario, senza aspettarle, e un nuovo Ordina li sistema."""
        etichetta, dato = CRITERI[criterio]
        come = etichetta[0].lower() + etichetta[1:]
        if self._troppo_pochi(pl, _("niente da ordinare")):
            return
        preferiti = pl is self.archivio.preferiti
        # Le schede che mancano si annotano mentre si ordina: lo schedario le
        # aggiunge da un altro filo, e il conto deve essere quello dell'ordine.
        non_letti = []

        def scheda_di(brano):
            scheda = self.schedario.scheda(brano.percorso)
            if scheda is None:
                non_letti.append(brano.percorso)
            return scheda

        cambiata, senza = pl.ordina(criterio, scheda_di)
        if non_letti:
            self.schedario.chiedi(non_letti)
        in_fondo, avviso = self._in_fondo(dato, senza, len(non_letti), len(pl.brani))
        if not cambiata:
            # Come Sposta con il brano gia' li': non si salva niente, e
            # l'ordine di prima resta quello che era.
            # Traduttori: come e' il criterio, come per autore; in_fondo dice dei brani senza il dato, come , 3 senza album in fondo.
            frase = _("I Preferiti sono già ordinati {come}{in_fondo}.").format(come=come, in_fondo=in_fondo) if preferiti else _(
                "{nome} è già ordinata {come}{in_fondo}.").format(nome=pl.nome, come=come, in_fondo=in_fondo)
            self._riscontro("nessun_altro_brano", frase + avviso)
            return
        # Traduttori: come e' il criterio, come per autore.
        testa = _("Preferiti ordinati {come}").format(come=come) if preferiti else _("{nome} ordinata {come}").format(nome=pl.nome, come=come)
        self._dopo_il_riordino(pl, "playlist_ordinata", testa, in_fondo, avviso=avviso)

    @staticmethod
    def _in_fondo(dato, senza, non_letti, totale):
        """(il pezzo della riga di Ordina sui brani andati in fondo, l'avviso
        da mettere dopo). I brani che lo schedario non ha ancora letto stanno
        in fondo con quelli senza il dato, ma si contano a parte: il dato forse
        ce l'hanno, e un nuovo Ordina, quando sono letti, li mette a posto.
        Il pezzo segue la frase dell'ordine, come Rock ordinata per album."""
        if not senza:
            return "", ""
        mancanti = senza - non_letti
        if not non_letti:
            if senza == totale:
                # Come Per album su una raccolta di SID, che l'album non l'hanno.
                # Traduttori: segue la frase dell'ordine, come Rock ordinata per album: 5 brani; dato e' cio' che manca ai brani, come album.
                return _(", tutti senza {dato}, in ordine di percorso").format(dato=dato), ""
            # Traduttori: segue la frase dell'ordine, come Rock ordinata per album: 5 brani; dato e' cio' che manca ai brani, come album.
            return ngettext(", {n} senza {dato} in fondo", ", {n} senza {dato} in fondo", mancanti).format(n=mancanti, dato=dato), ""
        avviso = " " + ngettext("Quando lo schedario l'ha letto, un nuovo Ordina lo mette al suo posto.",
            "Quando lo schedario li ha letti, un nuovo Ordina li mette al loro posto.", non_letti)
        if non_letti == totale:
            # Traduttori: segue la frase dell'ordine, come Rock ordinata per album: 5 brani.
            return _(", tutti non ancora letti dallo schedario, in ordine di percorso"), avviso
        if not mancanti:
            # Traduttori: segue la frase dell'ordine, come Rock ordinata per album: 5 brani.
            return ngettext(", {n} non ancora letto dallo schedario in fondo", ", {n} non ancora letti dallo schedario in fondo", non_letti).format(n=non_letti), avviso
        if senza == totale:
            # Traduttori: segue la frase dell'ordine, come Rock ordinata per album: 5 brani; senza sono i brani senza il dato, come album, n quelli non ancora letti.
            return ngettext(", {senza} senza {dato} e {n} non ancora letto dallo schedario, tutti in ordine di percorso",
                ", {senza} senza {dato} e {n} non ancora letti dallo schedario, tutti in ordine di percorso", non_letti).format(senza=mancanti, dato=dato, n=non_letti), avviso
        # Traduttori: segue la frase dell'ordine, come Rock ordinata per album: 5 brani; senza sono i brani senza il dato, come album, n quelli non ancora letti.
        return ngettext(", {senza} senza {dato} e {n} non ancora letto dallo schedario in fondo",
            ", {senza} senza {dato} e {n} non ancora letti dallo schedario in fondo", non_letti).format(senza=mancanti, dato=dato, n=non_letti), avviso

    def _inverti(self, pl):
        """Inverti l'ordine: la lista rovesciata com'e', anche un ordine fatto
        a mano; i brani senza il dato, che stavano in fondo, vanno in cima."""
        if self._troppo_pochi(pl, _("niente da invertire")):
            return
        preferiti = pl is self.archivio.preferiti
        if not pl.inverti():
            self._riscontro("nessun_altro_brano", _("I Preferiti sono uguale anche al contrario.") if preferiti else _(
                "{nome} è uguale anche al contrario.").format(nome=pl.nome))
            return
        self._dopo_il_riordino(pl, "ordine_invertito", _("Preferiti in ordine inverso") if preferiti else _("{nome} in ordine inverso").format(nome=pl.nome))

    def _mescola(self, pl):
        """Mescola: ogni ordine ugualmente probabile, con random.shuffle, senza
        distribuire gli autori. Se la playlist suona, o e' in pausa, il brano in
        riproduzione va in cima e gli altri dopo di lui (Gabriele). Cambia
        l'ordine salvato, non la riproduzione casuale, che ha il suo mazzo."""
        if self._troppo_pochi(pl, _("niente da mescolare")):
            return
        preferiti = pl is self.archivio.preferiti
        suona = self._che_suona_in(pl)
        if not pl.mescola(self._mescola_a_caso, in_cima=suona):
            self._riscontro("nessun_altro_brano", _("Mescolando, l'ordine dei Preferiti è venuto uguale a prima: niente cambia.") if preferiti else _(
                "Mescolando, l'ordine di {nome} è venuto uguale a prima: niente cambia.").format(nome=pl.nome))
            return
        self._dopo_il_riordino(pl, "playlist_mescolata", _("Preferiti mescolati") if preferiti else _("{nome} mescolata").format(nome=pl.nome), in_cima=suona is not None)

    # Il mescolamento di Mescola, che le prove sostituiscono, come _a_caso.
    _mescola_a_caso = staticmethod(random.shuffle)

    def _ordine_di_prima(self, pl):
        """Ordine di prima: l'ordine di prima dell'ultimo Ordina, Inverti
        l'ordine o Mescola, con gli stessi brani; quelli aggiunti dopo restano
        in fondo. Poi la voce sparisce, fino al prossimo riordino."""
        preferiti = pl is self.archivio.preferiti
        if not pl.rimetti_l_ordine_di_prima():
            self._riscontro("nessun_altro_brano", _("I Preferiti sono già nell'ordine di prima.") if preferiti else _(
                "{nome} è già nell'ordine di prima.").format(nome=pl.nome))
            return
        self._dopo_il_riordino(pl, "ordine_ripristinato", _("Preferiti di nuovo nell'ordine di prima") if preferiti else _(
            "{nome} di nuovo nell'ordine di prima").format(nome=pl.nome))

    def _dopo_il_riordino(self, pl, evento, testa, dettaglio="", in_cima=False, avviso=""):
        """Dopo un riordino che ha cambiato l'ordine: salva; toglie il loop
        A-B della playlist, perche' fra A e B finirebbero altri brani (un loop
        con il solo punto A, o con A e B sullo stesso brano, resta); ricostruisce
        il ramo, con il fuoco che resta sulla playlist; e lo dice, con i brani
        nascosti dal filtro e il posto nuovo del brano che suona, e poi
        l'avviso, se c'e'. Il brano che suona continua, e l'avanzamento
        riparte dal suo posto nuovo."""
        self._salva_archivio()
        coda = self.coda
        senza_loop = coda.loop_playlist is pl and coda.punto_b is not None and coda.punto_b is not coda.punto_a
        if senza_loop:
            coda.togli_loop()
        self._popola_playlist(seleziona=pl)
        # Traduttori: testa e' la frase del riordino, come Rock ordinata per autore.
        testo = ngettext("{testa}: {n} brano", "{testa}: {n} brani", len(pl.brani)).format(testa=testa, n=len(pl.brani))
        nascosti = sum(1 for b in pl.brani if not self._ammesso(pl, b)) if pl.filtro else 0
        if nascosti:
            testo += ngettext(", anche quello nascosto dal filtro", ", anche i {n} nascosti dal filtro", nascosti).format(n=nascosti)
        testo += dettaglio
        suona = self._che_suona_in(pl)
        if suona is not None:
            # Traduttori: posto e' come il 3 di 40.
            testo += _("; quello in riproduzione ora è in cima") if in_cima else _("; quello in riproduzione ora è {posto}").format(posto=self._posto_come_la_plancia(pl, suona))
        testo += "." + avviso
        if senza_loop:
            testo += " " + _("Il loop A-B è tolto: fra A e B sarebbero finiti altri brani.")
        self._riscontro(evento, testo)

    def _salta(self, pl, brano):
        brano.saltato = not brano.saltato
        self._salva_archivio()
        self._aggiorna_etichette()
        if brano.saltato:
            self._riscontro("saltato_acceso", _("{nome} resta nella playlist ma non verrà suonato.").format(nome=brano.nome))
        else:
            self._riscontro("saltato_spento", _("{nome} torna a essere suonato.").format(nome=brano.nome))

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
            self._statistiche.conta("brani_tolti")
            # Traduttori: file e' il nome del file tolto, nome quello della playlist.
            self._riscontro("brano_tolto", ngettext("Tolto {file}; nella playlist {nome} restano {n} brano.", "Tolto {file}; nella playlist {nome} restano {n} brani.",
                len(pl.brani)).format(file=brano.nome_del_file, nome=pl.nome, n=len(pl.brani)))

    # La riproduzione.

    def _temporanea(self, cartella, files=None):
        """La playlist temporanea di una cartella: i suoi file supportati.
        Se i file sono gli stessi resta la stessa playlist, con gli stessi
        brani: cosi' il brano che suona, e il loop, non si perdono quando la
        cartella si riapre o si aggiorna.
        Cartelle e file si confrontano senza badare alle maiuscole, come fa
        Windows (1.104.2): E:\\git\\mine e E:\\git\\Mine sono la stessa cartella,
        e il brano che suona da una resta lo stesso aprendo l'altra."""
        chiave = pulizia.norm(cartella)
        pl = self._temporanee.get(chiave)
        if files is None:
            if pl is not None:
                return pl
            try:
                files = questo_pc.contenuto(cartella)[1]
            except OSError:
                files = []
        if pl is None or [pulizia.norm(b.percorso) for b in pl.brani] != [pulizia.norm(f) for f in files]:
            nome = os.path.basename(cartella.rstrip("\\")) or cartella
            pl = self._temporanee[chiave] = Playlist.da_percorsi(nome, files, cartella)
        return pl

    def _suona(self, pl, brano, evento="play", sottobrano=None, inizio=None, sfuma_lo_stesso=False):
        """Suona il brano e lo dice. Con la dissolvenza accesa il motore lo fa
        entrare sfumando, se qualcosa si sente; un seguente preparato non
        conta piu'. Con sfuma_lo_stesso sfuma anche ripartendo con il brano
        in corso, come X da capo."""
        self._risvegliato = None
        if formati.e_midi(brano.percorso) and not self._midi_pronti():
            self._prepara_i_midi(lambda: self._suona(pl, brano, evento, sottobrano, inizio, sfuma_lo_stesso))
            return
        self._uscente = self._preparato = self._avanzamento_dopo_errore = None
        self._fermo_del_timer = False
        sveglio = False
        if evento not in ("brano_seguente_da_solo", "ritorno_al_punto_a"):
            # Un brano scelto da chi ascolta chiude la catena degli errori, e
            # dice che e' sveglio: la sfumatura del timer scaduto si ferma, e
            # il motore porta il brano nuovo a volume pieno.
            self._errori_di_fila.clear()
            sveglio = self._inizio_della_sfumatura is not None
            self._ferma_la_sfumatura(riporta=False)
        # Il punto del file lungo che si lascia, e quello a cui riprendere il
        # nuovo, se nessuno ne chiede un altro (1.92.0).
        self._ricorda_la_posizione()
        ripresa = None
        if inizio is None and not (sottobrano or brano.sottobrano) and evento != "da_capo" and self.impostazioni["ripresa_oltre"]:
            ripresa = inizio = self.posizioni.dove(brano.percorso)
        self.coda.imposta(pl, brano)
        self._segna_nel_mazzo(pl, brano, sottobrano)
        self._sentinella.guarda(brano.percorso)
        self.motore.suona(brano.percorso, sottobrano or brano.sottobrano, inizio=inizio, sfuma_lo_stesso=sfuma_lo_stesso, a_volume_pieno=sveglio)
        self._annuncia(pl, brano, evento)
        if ripresa:
            self._statistiche.conta("ripresi_dal_punto")
            self.scrivi(_("Riprendo da {tempo}, dove l'avevi lasciato: X lo fa ripartire da capo.").format(tempo=tempo(ripresa)))

    def _annuncia(self, pl, brano, evento):
        """Il riscontro del brano appena partito, con la sua posizione nella
        lista e il sottobrano, le etichette della plancia e l'inseguimento."""
        numero, totale = self.coda.posizione()
        if evento != "da_capo":
            # Da capo e' lo stesso brano che riparte, non un avvio (1.103.0).
            a_caso = evento == "casuale" or (self.impostazioni["casuale"] and evento in ("brano_seguente_da_solo", "successivo"))
            self._statistiche.brano_avviato(brano.percorso, self.motore.sottobrano if self.motore.sottobrani else None, evento, a_caso)
        if getattr(pl, "selezione", False):
            dove = _("{numero} di {totale} della selezione").format(numero=numero, totale=totale)
        else:
            # La lista con il nome della plancia, come in Dove sono: Preferiti e
            # Risultati, non playlist Preferiti e cartella Risultati (1.105.1).
            # Senza con le sottocartelle, che allungherebbe ogni riga di avvio:
            # resta solo in Dove sono (Gabriele).
            # Traduttori: il posto del brano nella lista, come 3 di 12, playlist Rock.
            dove = _("{numero} di {totale}, {lista}").format(numero=numero, totale=totale, lista=self._nome_della_lista(pl, sottocartelle=False)) if totale > 1 else pl.nome
        # Traduttori: dove e' il posto del brano nella lista, come 3 di 12, playlist Rock.
        testo = _("In riproduzione: {percorso}, {dove}.").format(percorso=brano.percorso, dove=dove)
        if self.motore.sottobrani:
            testo += " " + _("Sottobrano {numero} di {totale}.").format(numero=self.motore.sottobrano, totale=self.motore.sottobrani)
        self._riscontro(evento, testo)
        # In riproduzione lo dicono solo le voci del brano di prima e di questo.
        solo = {brano.percorso} if self._annunciato is None else {brano.percorso, self._annunciato}
        self._annunciato = brano.percorso
        self._aggiorna_etichette(solo=solo)
        self._insegui()
        self._video_nascosto_per = self._video_in_attesa = None
        self._aggiorna_il_video()

    def _riproduci(self, pl, brano, sottobrano=None):
        """Suona un brano scelto nella plancia, se il loop lo permette."""
        if not self.coda.nel_loop(pl, brano):
            self._riscontro("fuori_dal_loop", _("{nome} è fuori dal loop: si suona solo fra il punto A e il punto B.").format(nome=brano.nome_del_file))
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
            self._riscontro("errore", _("{nome} non c'è più.").format(nome=os.path.basename(percorso)))
            return
        self._riproduci(pl, brano)

    def _riproduci_playlist(self, pl):
        brano = self.coda.primo(pl)
        if brano is None and pl is self.archivio.preferiti:
            self._riscontro("niente_da_suonare", _("I Preferiti sono vuoti: F4 ci mette il brano selezionato."))
            return
        if brano is None:
            self._riscontro("niente_da_suonare", _("La playlist {nome} non ha brani da suonare.").format(nome=pl.nome))
            return
        self._suona(pl, brano)

    def _riproduci_cartella(self, cartella):
        """Suona una cartella con tutto l'albero che le sta sotto: i suoi file,
        poi quelli delle sottocartelle. Z, B e N girano su tutti. I brani sono
        quelli delle playlist temporanee di ciascuna cartella, cosi' nella
        plancia il brano che suona si riconosce anche dentro le sottocartelle."""
        pl = self._playlist_ricorsiva(cartella)
        if pl is None:
            return
        brano = self.coda.primo(pl)
        if brano is None:
            self._riscontro("niente_da_suonare", _("Né in questa cartella né nelle sue sottocartelle ci sono file da suonare."))
            return
        self._suona(pl, brano)

    def _playlist_ricorsiva(self, cartella):
        """La playlist temporanea di una cartella con tutto l'albero che le sta
        sotto, o None, detto nella console, se la cartella non si legge. La
        usano X su una cartella e il segnalibro (issue 37)."""
        with wx.BusyCursor():
            contenuti = questo_pc.contenuti_ricorsivi(cartella)
        if not contenuti:
            self._riscontro("errore", _("Non riesco a leggere {cartella}.").format(cartella=cartella))
            return None
        brani = [b for sotto, files in contenuti for b in self._temporanea(sotto, files).brani]
        nome = os.path.basename(cartella.rstrip("\\")) or cartella
        pl = Playlist(nome, brani, cartella=cartella)
        pl.ricorsiva = True
        return pl

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

    def _voce_che_suona(self, sottobrano=None, brano=None):
        """La voce visibile della plancia che corrisponde a cio' che suona, o
        None se non si vede: il sottobrano, se il SID e' aperto, altrimenti il
        brano o il file. Il sottobrano e' quello del motore, se non lo si da':
        al passaggio della dissolvenza il motore ha gia' quello che entra,
        mentre la coda e' ancora sul brano che esce. brano, se c'e', prende il
        posto di quello della coda, per la durata residua (tappa 14 d)."""
        corrente = self.coda.corrente if brano is None else brano
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

    def _seguente_automatico(self, sottobrano=None, dopo_errore=False):
        """Cosa suonare quando un brano finisce da solo: (playlist, brano,
        sottobrano) o None. Se cio' che suona si vede nella plancia, decide la
        plancia: la voce suonabile che viene dopo, dentro i rami aperti,
        sottobrani compresi, anche in un'altra cartella o playlist. Se non si
        vede, per esempio una cartella suonata chiusa o un file aperto con
        Apri file, decide la lista. Con il loop A-B decide il loop.
        sottobrano e' quello del brano che finisce, se non e' quello del
        motore, come al passaggio della dissolvenza.
        La ripetizione (1.94.0): del brano, si risuona lo stesso, con lo
        stesso sottobrano; della lista, dove non c'e' altro si riparte dal
        primo. Dopo un errore, dopo_errore, il brano che non si suona non si
        ripete, e dal primo si riparte una volta sola."""
        if self._timer_a_fine_brano:
            # Il timer alla fine del brano (1.95.0): non segue niente.
            self._mazzo_finito = False
            return None
        ripetizione = self.impostazioni["ripetizione"]
        pl, corrente = self.coda.playlist, self.coda.corrente
        if not dopo_errore and corrente is not None and self._il_brano_si_ripete(pl, corrente):
            # Un brano saltato, tolto dalla lista o nascosto dal filtro non si
            # ripete: si va avanti come sempre.
            self._mazzo_finito = False
            return pl, corrente, self.motore.sottobrano if sottobrano is None else sottobrano
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
            seguente = self._passo_in_plancia(voce, 1)
        else:
            dopo = self.coda.successivo()
            seguente = (self.coda.playlist, dopo, None) if dopo else None
        if seguente is None and ripetizione == "lista":
            seguente = self._da_capo(voce)
        return seguente

    def _da_capo(self, voce):
        """Con la ripetizione della lista, il primo di cio' che l'avanzamento
        suonerebbe: se decide la plancia, la prima voce suonabile che vi si
        vede; altrimenti il primo della lista, del loop o della selezione.
        None se non c'e'."""
        if voce is not None:
            prima, _cookie = self.albero.GetFirstChild(self.albero.GetRootItem())
            prima = prima if prima.IsOk() else None
            while prima is not None and not self._suonabile_in_plancia(prima):
                prima = self._dopo(prima)
            if prima is None:
                return None
            dati = self._dati(prima)
            return dati["playlist"], dati["brano"], dati.get("numero")
        pl = self.coda.playlist
        primo = self.coda.primo(pl) if pl is not None else None
        return (pl, primo, None) if primo is not None else None

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
                    if self.impostazioni["ripetizione"] != "lista":
                        return FINE_DEL_MAZZO
                    # Con la ripetizione della lista il mazzo finito si
                    # rimescola, come nel modello a giro (1.94.0); se la
                    # ripetizione si spegne prima del passaggio della
                    # dissolvenza, il giro nuovo si annulla (1.96.11).
                    self._mazzo_prima_del_giro = (suona, set(self._mazzo), list(self._mazzo_tenuti))
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

    def _storia_in_avanti(self):
        """I posti della storia della riproduzione casuale dopo quello in cui
        si e', che dopo Z l'avanzamento ripercorre prima di pescare dal mazzo:
        quelli ancora nella loro playlist, come in _dalla_storia, ma senza
        dimenticare gli altri, per la durata residua (tappa 14 d)."""
        return [posto for posto in self._storia[self._nella_storia + 1:] if any(b is posto[1] for b in posto[0].brani)]

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
        self._mazzo_prima_del_giro = None
        if self.motore.in_corso and self.coda.corrente is not None:
            self._segna_nel_mazzo(self.coda.playlist, self.coda.corrente, self.motore.sottobrano if self.motore.sottobrani else None)

    def _evento_del_seguente(self, nuova, brano):
        """Il suono del passaggio automatico al brano della playlist nuova:
        nel loop, dopo il punto B si torna al punto A, e ha un suono suo. Da
        chiedere prima di spostare la coda."""
        if self.impostazioni["casuale"] and brano is not self.coda.corrente:
            # A caso non si torna al punto A: si va da un'altra parte.
            return "brano_seguente_da_solo"
        if self.impostazioni["ripetizione"] == "brano" and brano is self.coda.corrente and nuova is self.coda.playlist:
            # Il brano che si ripete non torna al punto A del loop.
            return "brano_seguente_da_solo"
        pl = self.coda.playlist
        prima = pl.indice(self.coda.corrente) if pl else None
        dopo = nuova.indice(brano)
        ritorno = self.coda.intervallo() and nuova is pl and prima is not None and dopo is not None and dopo <= prima
        return "ritorno_al_punto_a" if ritorno else "brano_seguente_da_solo"

    def _brano_finito(self):
        """Il brano e' finito da solo, senza un seguente preparato che
        entrasse con la dissolvenza: si suona il seguente, se c'e'."""
        if self._chiusa or self._fermo_del_timer:
            # Il timer ha fermato tutto mentre questa fine era gia' in coda.
            return
        self._statistiche.brano_finito()
        # Il file lungo arrivato alla fine non ha piu' un punto da riprendere.
        if self.coda.corrente is not None:
            self.posizioni.dimentica(self.coda.corrente.percorso)
        self._uscente = self._preparato = None
        self._errori_di_fila.clear()
        seguente = self._seguente_automatico()
        if seguente:
            nuova, brano, sottobrano = seguente
            self._suona(nuova, brano, self._evento_del_seguente(nuova, brano), sottobrano)
        else:
            self._fine_della_lista()

    def _fine_della_lista(self):
        self._aggiorna_etichette()
        self._aggiorna_il_video()
        if self._timer_a_fine_brano:
            self._timer_a_fine_brano = False
            self._riscontro("timer_scaduto", _("Timer scaduto: il brano è finito, e la riproduzione si ferma."))
            return
        if self._mazzo_finito:
            # Il mazzo si rifa': la prossima riproduzione comincia un giro nuovo.
            self._mazzo_finito = False
            self._ricomincia_il_mazzo()
            self._riscontro("fine_playlist", _("Fine: ogni brano del mazzo ha suonato una volta."))
            return
        self._riscontro("fine_playlist", _("Fine: davanti non c'è altro da suonare."))

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
        self._sentinella.guarda(brano.percorso)
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
        # Il brano che esce e' arrivato alla sua fine, sfumando.
        self._statistiche.brano_finito()
        self._statistiche.conta("passaggi_sfumati")
        self._errori_di_fila.clear()
        prima, self._mazzo_prima_del_giro = self._mazzo_prima_del_giro, None
        if prima is not None and self.impostazioni["ripetizione"] != "lista" and _stesso_posto(prima[0], uscente):
            # Il giro nuovo era della ripetizione della lista, che intanto si
            # e' spenta: il mazzo torna finito.
            self._mazzo, self._mazzo_tenuti = prima[1], prima[2]
            self._casuale_ricordato = None
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
        self._statistiche.brano_in_errore(percorso)
        if self.coda.corrente is not None:
            self._errori_di_fila[id(self.coda.corrente)] = self.coda.corrente
        self._riscontro("errore", _("Non riesco a suonare {nome}.").format(nome=os.path.basename(percorso or "")))
        segno = self._avanzamento_dopo_errore = object()
        self._dopo_il_suono(self._avanza_dopo_l_errore, segno)

    def _avanza_dopo_l_errore(self, segno):
        if segno is not self._avanzamento_dopo_errore or self.motore.in_corso:
            # Intanto e' partito altro, per esempio con X, o V ha fermato.
            return
        self._avanzamento_dopo_errore = None
        seguente = self._seguente_automatico(dopo_errore=True)
        if seguente and len(self._errori_di_fila) >= self._brani_da_suonare():
            # Nessuno dei brani che l'avanzamento puo' suonare si e' suonato:
            # un altro giro non servirebbe (1.96.11).
            self._errori_di_fila.clear()
            self._aggiorna_etichette()
            self._riscontro("fine_playlist", _("Fine: nessun brano si riesce a suonare."))
            return
        if seguente:
            nuova, brano, sottobrano = seguente
            self._suona(nuova, brano, "brano_seguente_da_solo", sottobrano)
        elif self._timer_a_fine_brano:
            self._fine_della_lista()
        else:
            self._aggiorna_etichette()

    def _brani_da_suonare(self):
        """Quanti brani diversi l'avanzamento automatico puo' suonare: le
        voci suonabili che si vedono nella plancia, se decide lei; altrimenti
        quelli della lista, o del loop."""
        voce = self._voce_da_seguire()
        if voce is not None:
            return len({id(self._dati(v)["brano"]) for v in self._candidati_in_plancia(None)})
        pl = self.coda.playlist
        if pl is None:
            return 0
        brani = pl.brani
        limiti = self.coda.intervallo()
        if limiti is not None:
            brani = brani[limiti[0]:limiti[1] + 1]
        return sum(1 for b in brani if not b.saltato and self.coda.ammesso(pl, b))

    def _niente_in_corso(self, risveglia=False):
        """Vero, con il riscontro, se non c'e' un brano caricato. Con risveglia
        il brano fermo si ricarica in pausa, con _risveglia_il_fermo."""
        if self.motore.in_corso or (risveglia and self._risveglia_il_fermo()):
            return False
        self._riscontro("niente_da_suonare", _("Non sta suonando niente."))
        return True

    def _risveglia_il_fermo(self):
        """Issue 39 (1.116.3): da fermi, con un brano corrente, i comandi che si
        muovono nel brano o che lo raccontano, come Q, E, R, Y e Dove sono, lo
        ricaricano in pausa dove sta la testina, che dopo lo stop e'
        l'inizio, come X lo farebbe ripartire; poi rispondono come in pausa.
        Aspetta che il motore lo apra, al piu' ATTESA_DEL_RISVEGLIO secondi,
        senza far girare gli eventi della finestra. Il brano conta come
        avviato quando X lo fa ripartire, non qui. Vero se ora c'e' un brano
        caricato."""
        if self.motore.in_corso:
            return True
        corrente = self.coda.corrente
        # Un MIDI senza il banco dei suoni pronto andrebbe in errore, e
        # l'errore fa partire il brano dopo.
        if corrente is None or (formati.e_midi(corrente.percorso) and not self._midi_pronti()):
            return False
        self._sentinella.guarda(corrente.percorso)
        # Un video ricaricato in pausa apre la sua finestra con X, come alla
        # ripresa dell'avvio.
        self._video_in_attesa = corrente.percorso
        self.motore.suona(corrente.percorso, inizio=0.0, in_pausa=True)
        self._risvegliato = corrente.percorso
        fine = time.monotonic() + ATTESA_DEL_RISVEGLIO
        while self.motore.posizione is None and self.motore.in_corso and time.monotonic() < fine:
            time.sleep(0.01)
        self._aggiorna_etichette()
        return bool(self.motore.in_corso)

    def _comando_play(self):
        if len(self._voci_selezionate()) > 1:
            self._suona_selezione()
            return
        dati = self._dati(self._voce_di_lavoro()) or {}
        tipo = dati.get("tipo")
        corrente = self.coda.corrente
        if tipo == "capitolo":
            self._suona_il_capitolo(dati)
            return
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
            self._conta_la_ripartenza()
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
            self._riscontro("niente_da_suonare", _("Niente da riprodurre: scegli un brano, una playlist o una cartella nella plancia."))

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
            self._riscontro("niente_da_suonare", _("La playlist {nome} non ha niente da suonare.").format(nome=pl.nome))
            return
        dati = self._dati(voce)
        self._suona(dati["playlist"], dati["brano"], evento, dati.get("numero"))

    def _playlist_vicina(self, passo):
        playlist = self.archivio.playlist
        if not playlist:
            self._riscontro("niente_da_suonare", _("Non ci sono playlist salvate."))
            return
        attuale = self._playlist_selezionata()
        # Senza una playlist di partenza, K parte dalla prima e J dall'ultima.
        partenza = playlist.index(attuale) if attuale is not None else (-1 if passo > 0 else len(playlist))
        indice = partenza + passo
        if not 0 <= indice < len(playlist):
            self._riscontro("nessun_altro_brano", _("È la prima playlist.") if passo < 0 else _("È l'ultima playlist."))
            return
        self._apri_e_suona(playlist[indice], "playlist_precedente" if passo < 0 else "playlist_successiva")

    def _comando_playlist_precedente(self):
        self._playlist_vicina(-1)

    def _comando_playlist_successiva(self):
        self._playlist_vicina(1)

    def _comando_playlist(self):
        """J (issue 38): la playlist della plancia, o quella che suona, e il
        suo posto fra le playlist salvate."""
        playlist = self.archivio.playlist
        attuale = self._playlist_selezionata()
        if not playlist:
            testo = _("Non ci sono playlist salvate.")
        elif attuale is None:
            testo = ngettext("La plancia non è in una playlist; ne hai {n}.", "La plancia non è in una playlist; ne hai {n}.", len(playlist)).format(n=len(playlist))
        else:
            testo = _("Playlist {numero} di {totale}, {nome}.").format(numero=playlist.index(attuale) + 1, totale=len(playlist), nome=attuale.nome)
        self._riporta(testo, "playlist")

    def _comando_prima_playlist(self):
        if not self.archivio.playlist:
            self._riscontro("niente_da_suonare", _("Non ci sono playlist salvate."))
            return
        self._playlist_numero(1)

    def _comando_ultima_playlist(self):
        if not self.archivio.playlist:
            self._riscontro("niente_da_suonare", _("Non ci sono playlist salvate."))
            return
        self._playlist_numero(len(self.archivio.playlist))

    def _playlist_numero(self, numero):
        if numero > len(self.archivio.playlist):
            self._riscontro("nessun_altro_brano", ngettext("Non c'è la playlist numero {numero}: ne hai {n}.", "Non c'è la playlist numero {numero}: ne hai {n}.",
                len(self.archivio.playlist)).format(numero=numero, n=len(self.archivio.playlist)))
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
            self._riscontro("loop_tolto", _("Loop tolto: si suona di nuovo tutta la lista."))
            return
        dati = self._dati(self._voce_di_lavoro()) or {}
        if dati.get("tipo") not in ("brano", "file", "sottobrano"):
            self._riscontro("loop_non_qui", _("Il loop si mette su un brano: scegline uno in una playlist o in una cartella."))
            return
        pl, brano = dati["playlist"], dati["brano"]
        if coda.loop_playlist is None:
            coda.loop_playlist, coda.punto_a, coda.punto_b = pl, brano, None
            self._riscontro("loop_a_messo", _("Punto A del loop su {nome}. Maiuscolo+X su un brano della stessa lista, anche questo, mette il punto B.").format(
                nome=brano.nome_del_file))
        elif coda.loop_playlist is not pl:
            self._riscontro("loop_non_qui", _("Il punto A sta in {lista}: il punto B va su un brano della stessa lista.").format(lista=coda.loop_playlist.nome))
            return
        else:
            coda.punto_b = brano
            primo, ultimo = coda.intervallo(pl)
            # Traduttori: a e b sono i nomi dei file dei punti A e B del loop.
            self._riscontro("loop_b_messo", ngettext("Loop fra {a} e {b}: {n} brano. Maiuscolo+X lo toglie.", "Loop fra {a} e {b}: {n} brani. Maiuscolo+X lo toglie.",
                ultimo - primo + 1).format(a=coda.punto_a.nome_del_file, b=brano.nome_del_file, n=ultimo - primo + 1))
        self._aggiorna_etichette()

    def _comando_pausa(self):
        if self._niente_in_corso():
            return
        if self.motore.pausa(sfumando=True):
            posizione = self.motore.posizione
            self._riscontro("pausa", _("Pausa a {tempo}.").format(tempo=tempo(posizione)) if posizione is not None else _("Pausa."))
        else:
            self._conta_la_ripartenza()
            self._riscontro("ripresa", self._frase_della_ripresa())
            self._riprende_il_video()

    def _conta_la_ripartenza(self):
        """Un brano ricaricato da fermo per un comando (issue 39), che X o C
        fanno ripartire: per le statistiche parte adesso, come avrebbe fatto
        X dopo lo stop."""
        if self._risvegliato is not None and self._risvegliato == self.motore.in_corso:
            self._statistiche.brano_avviato(self.motore.in_corso, self.motore.sottobrano if self.motore.sottobrani else None)
        self._risvegliato = None

    def _frase_della_ripresa(self):
        posizione = self.motore.posizione
        return _("Riprende da {tempo}.").format(tempo=tempo(posizione)) if posizione is not None else _("Riprende.")

    def _comando_stop(self):
        if self._avanzamento_dopo_errore is not None and not self.motore.in_corso:
            # Il brano dopo uno che non si suona sta per partire: V lo ferma.
            self._avanzamento_dopo_errore = None
            self._riscontro("stop", _("Stop: il brano seguente non parte."))
            return
        if self._niente_in_corso():
            return
        # Con la dissolvenza accesa il brano si spegne piano, e il motore e'
        # subito libero (Gabriele, 2 ottobre 2026); non se sta gia' sfumando
        # per il timer.
        if self._ferma(sfumando=self._inizio_della_sfumatura is None):
            self._riscontro("stop", _("Stop. La selezione suonata è chiusa: X suona di nuovo ciò che selezioni."))
            return
        self._riscontro("stop", _("Stop. X riparte dall'inizio del brano."))

    def _ferma(self, sfumando):
        """Lo stop, per V e per il timer: il punto del file lungo, il motore e
        la selezione suonata, che si chiude; torna vero se c'era. La
        sfumatura del timer finisce qui, e il volume torna pieno a motore
        fermo."""
        self._ricorda_la_posizione()
        self.motore.stop(sfumando=sfumando)
        self._statistiche.brano_fermato()
        self._ferma_la_sfumatura()
        self._uscente = self._preparato = None
        self._risvegliato = None
        selezione = getattr(self.coda.playlist, "selezione", False)
        if selezione:
            # La playlist invisibile della selezione vive fino allo stop.
            self.coda.imposta(None, None)
        self._aggiorna_etichette()
        self._aggiorna_il_video()
        return selezione

    # Il timer di spegnimento (1.95.0).

    # L'orologio del timer, che le prove sostituiscono.
    _adesso = staticmethod(time.monotonic)

    def _comando_timer(self):
        """Maiuscolo con S (Gabriele, 1.95.0): il timer di spegnimento, fra
        tanti minuti o alla fine del brano. Scaduto, la musica sfuma e si
        ferma. Un timer nuovo prende il posto di quello che c'era."""
        self._domanda()
        # Mentre la domanda e' aperta, la sfumatura e la sveglia aspettano: lo
        # 0 deve arrivare in tempo (1.96.11).
        self._sveglia_del_timer.Stop()
        self._orologio_della_sfumatura.Stop()
        sfumato = None if self._inizio_della_sfumatura is None else self._adesso() - self._inizio_della_sfumatura
        proposta = valori.FINE_DEL_BRANO if self._timer_a_fine_brano else str(self._minuti_del_timer)
        # Traduttori: f e' la lettera che il campo accetta per la fine del brano; adesso e' la frase del timer di adesso.
        with DialogoTesto(self, _("Fra quanti minuti si ferma la riproduzione? Da 1 a {massimo}; "
                "f la ferma alla fine del brano, 0 toglie il timer. {adesso}").format(massimo=valori.TIMER_MASSIMO, adesso=self._frase_del_timer()),
                _("Timer di spegnimento"), proposta) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._riprendi_il_timer(sfumato)
                # Traduttori: adesso e' la frase del timer di adesso, come Adesso non c'e' un timer.
                self._annullato(_("Timer non cambiato. {adesso}").format(adesso=self._frase_del_timer()))
                return
            testo = dialogo.GetValue()
        try:
            scelta, correzioni = valori.leggi_timer(testo)
        except ErroreValore as e:
            self._riprendi_il_timer(sfumato)
            self._riscontro("errore", _("{errore} Timer non cambiato.").format(errore=e))
            return
        c_era = self._timer_scade is not None or self._timer_a_fine_brano or self._inizio_della_sfumatura is not None
        self._togli_il_timer()
        if scelta == 0:
            self._riscontro("timer_tolto", _("Timer tolto.") if c_era else _("Non c'era un timer da togliere."))
            return
        if scelta == valori.FINE_DEL_BRANO:
            self._timer_a_fine_brano = True
            self._statistiche.conta("timer_a_fine_brano")
            frase = _("Timer impostato: la riproduzione si ferma alla fine del brano.")
        else:
            self._minuti_del_timer = scelta
            self._timer_scade = self._adesso() + scelta * 60
            self._sveglia_del_timer.StartOnce(scelta * 60 * 1000)
            # Traduttori: minuti e' come 30 minuti, ora come 21:45.
            frase = _("Timer impostato: la riproduzione si ferma fra {minuti}, alle {ora}.").format(minuti=_minuti(scelta), ora=self._ora_del_timer())
        self._riscontro("timer_impostato", " ".join([frase, *correzioni]))

    def _comando_timer_attuale(self):
        """S (issue 38): il timer di spegnimento, con i suoi limiti."""
        self._riporta(self._frase_del_timer() + " " + ngettext("Il timer va da 1 a {massimo} minuti, o alla fine del brano.",
            "Il timer va da 1 a {massimo} minuti, o alla fine del brano.", valori.TIMER_MASSIMO).format(massimo=valori.TIMER_MASSIMO), "timer")

    def _comando_togli_il_timer(self):
        """Ctrl con S: toglie il timer, anche mentre la musica sfuma."""
        c_era = self._timer_scade is not None or self._timer_a_fine_brano or self._inizio_della_sfumatura is not None
        self._togli_il_timer()
        self._riscontro("timer_tolto", _("Timer tolto.") if c_era else _("Non c'era un timer da togliere."))

    def _comando_timer_a_fine_brano(self):
        """Alt con S: il timer alla fine del brano, al posto di quello che c'era."""
        self._togli_il_timer()
        self._timer_a_fine_brano = True
        self._statistiche.conta("timer_a_fine_brano")
        self._riscontro("timer_impostato", _("Timer impostato: la riproduzione si ferma alla fine del brano."))

    def _riprendi_il_timer(self, sfumato):
        """Dopo la domanda lasciata com'era: la sfumatura riprende dal punto
        in cui era, sfumato secondi, e la sveglia dalla sua scadenza, anche
        subito se e' passata."""
        if sfumato is not None:
            self._inizio_della_sfumatura = self._adesso() - sfumato
            self._orologio_della_sfumatura.Start(PASSO_DELLA_SFUMATURA)
        elif self._timer_scade is not None:
            resto = self._timer_scade - self._adesso()
            if resto <= 0:
                self._scade_il_timer()
            else:
                self._sveglia_del_timer.StartOnce(max(1, round(resto * 1000)))

    def _ora_del_timer(self):
        return self._ora_fra(max(0.0, self._timer_scade - self._adesso()))

    def _frase_del_timer(self):
        """Il timer di adesso, per la domanda di Maiuscolo con S."""
        if self._inizio_della_sfumatura is not None:
            return _("Adesso il timer è scaduto, e la musica sta sfumando.")
        if self._timer_a_fine_brano:
            return _("Adesso la ferma alla fine del brano.")
        if self._timer_scade is not None:
            minuti = max(1, math.ceil((self._timer_scade - self._adesso()) / 60))
            # Traduttori: minuti e' come 30 minuti, ora come 21:45.
            return _("Adesso scade fra {minuti}, alle {ora}.").format(minuti=_minuti(minuti), ora=self._ora_del_timer())
        return _("Adesso non c'è un timer.")

    def _togli_il_timer(self):
        self._sveglia_del_timer.Stop()
        self._timer_scade = None
        self._timer_a_fine_brano = False
        self._ferma_la_sfumatura()

    def _scade_il_timer(self, _evento=None):
        """I minuti sono passati: se qualcosa si sente, sfuma e poi si ferma;
        altrimenti si ferma subito."""
        self._timer_scade = None
        if self._chiusa:
            return
        if not self.motore.in_corso or self.motore.in_pausa:
            self._fermato_dal_timer()
            return
        self.scrivi(_("Timer scaduto: la musica sfuma."))
        self._inizio_della_sfumatura = self._adesso()
        self._orologio_della_sfumatura.Start(PASSO_DELLA_SFUMATURA)

    def _passo_della_sfumatura(self, _evento=None):
        """La voce scende come nelle dissolvenze, con il coseno, e in fondo
        ci si ferma. Il motore fermo fra un brano e l'altro non vuol dire
        musica finita: il seguente parte gia' attenuato (1.96.11)."""
        if self._chiusa or self._inizio_della_sfumatura is None:
            return
        avanzamento = min(1.0, (self._adesso() - self._inizio_della_sfumatura) / SFUMATURA_DEL_TIMER)
        self.motore.attenuazione = math.cos(avanzamento * math.pi / 2)
        if avanzamento >= 1.0:
            self._fermato_dal_timer()

    def _fermato_dal_timer(self):
        """Lo stop del timer: anche il brano che sta per partire, dopo un
        errore o alla fine di quello di prima gia' in coda, non parte."""
        fermato = bool(self.motore.in_corso) or self._avanzamento_dopo_errore is not None
        self._avanzamento_dopo_errore = None
        self._ferma(sfumando=False)
        self._fermo_del_timer = True
        self._riscontro("timer_scaduto", _("Timer scaduto: riproduzione fermata.") if fermato else _("Timer scaduto."))

    def _ferma_la_sfumatura(self, riporta=True):
        """La sfumatura del timer, se c'e', finisce, e il volume torna pieno;
        senza riporta lo fa il motore, con il brano nuovo."""
        if self._inizio_della_sfumatura is None:
            return
        self._orologio_della_sfumatura.Stop()
        self._inizio_della_sfumatura = None
        if riporta:
            self.motore.attenuazione = 1.0

    def _vicino(self, verso, evento, limite):
        """Z e B: il brano prima o dopo, dalla plancia se cio' che suona si
        vede, altrimenti dalla lista."""
        if not self.coda.playlist:
            self._riscontro("niente_da_suonare", _("Non c'è una playlist in riproduzione."))
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
        self._vicino(1, "successivo", _("È l'ultimo brano."))

    def _comando_precedente(self):
        if self.impostazioni["casuale"] and self.coda.playlist:
            # Z torna al brano suonato prima, non a quello che sta prima.
            indietro = self._dalla_storia(-1)
            if indietro is None:
                self._riscontro("nessun_altro_brano", _("È il primo brano suonato a caso."))
                return
            self._atteso_dalla_storia = indietro
            pl, brano, numero = indietro
            self._suona(pl, brano, "precedente", numero)
            return
        self._vicino(-1, "precedente", _("È il primo brano."))

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
            self._riscontro("nessun_altro_brano", _("Ogni brano del mazzo ha suonato una volta: B ricomincia un giro nuovo."))
            return
        if seguente is None:
            self._riscontro("nessun_altro_brano", _("Non c'è un altro brano da scegliere a caso."))
            return
        pl, brano, numero = seguente
        self._suona(pl, brano, "successivo", numero)

    def _comando_casuale(self, scelta=random.choice):
        """Alt con N: a caso fra le voci suonabili che si vedono nella plancia, se cio'
        che suona si vede; altrimenti a caso nella sua lista."""
        if not self.coda.playlist:
            self._riscontro("niente_da_suonare", _("Non c'è una playlist in riproduzione."))
            return
        voce = self._voce_da_seguire()
        if voce is None:
            brano = self.coda.casuale(scelta)
            if brano is None:
                self._riscontro("nessun_altro_brano", _("Non ci sono brani da scegliere."))
                return
            self._suona(self.coda.playlist, brano, "casuale")
            return
        candidati = self._candidati_in_plancia(voce)
        if not candidati:
            self._riscontro("nessun_altro_brano", _("Nella plancia non si vede nient'altro da suonare."))
            return
        dati = self._dati(scelta(candidati))
        self._suona(dati["playlist"], dati["brano"], "casuale", dati.get("numero"))

    def _salto(self, secondi, evento):
        if self._niente_in_corso(risveglia=True):
            return
        prima = self.motore.posizione or 0
        durata = self.motore.durata
        arrivo = max(0, prima + secondi)
        if durata is not None:
            arrivo = min(arrivo, durata)
        self.motore.salta(secondi)
        self._statistiche.conta("secondi_avanti" if secondi > 0 else "secondi_indietro", round(abs(arrivo - prima), 3))
        if secondi > 0:
            # Traduttori: tempo e' il punto d'arrivo nel brano, durata quella del brano, come 1:20 di 3:45.
            testo = _("Avanti a {tempo} di {durata}.").format(tempo=tempo(arrivo), durata=tempo(durata)) if durata is not None else _("Avanti a {tempo}.").format(
                tempo=tempo(arrivo))
        else:
            # Traduttori: tempo e' il punto d'arrivo nel brano, durata quella del brano, come 1:20 di 3:45.
            testo = _("Indietro a {tempo} di {durata}.").format(tempo=tempo(arrivo), durata=tempo(durata)) if durata is not None else _("Indietro a {tempo}.").format(
                tempo=tempo(arrivo))
        self._riscontro(evento, testo, "salto")
        self._avvisa_l_attesa_del_sid(arrivo)

    def _avvisa_l_attesa_del_sid(self, arrivo):
        """Dopo un salto: se il brano e' un SID, un MIDI o un brano delle
        console e il punto d'arrivo non e' ancora reso, la console dice
        quanto c'e' da aspettare, che altrimenti sarebbe silenzio senza
        spiegazioni (tappa 5, 1.62.0)."""
        attesa = self.motore.attesa_del_sid(arrivo)
        if attesa >= ATTESA_DA_DIRE:
            self._statistiche.conta("attese_lunghe")
            in_corso = self.motore.in_corso or ""
            secondi = max(2, round(attesa))
            # Traduttori: tempo e' il punto del brano a cui si e' saltati, come 1:20.
            if formati.e_midi(in_corso):
                frase = ngettext("Il MIDI si prepara fino a {tempo}: circa {n} secondo.", "Il MIDI si prepara fino a {tempo}: circa {n} secondi.", secondi).format(
                    tempo=tempo(arrivo), n=secondi)
            elif formati.e_chip(in_corso):
                frase = ngettext("Il brano della console si prepara fino a {tempo}: circa {n} secondo.", "Il brano della console si prepara fino a {tempo}: circa {n} secondi.",
                    secondi).format(tempo=tempo(arrivo), n=secondi)
            else:
                frase = ngettext("Il SID si prepara fino a {tempo}: circa {n} secondo.", "Il SID si prepara fino a {tempo}: circa {n} secondi.", secondi).format(
                    tempo=tempo(arrivo), n=secondi)
            self.scrivi(frase)

    def _comando_avanti(self):
        self._salto(self.impostazioni["passo_avanti"], "avanti")

    def _comando_indietro(self):
        self._salto(-self.impostazioni["passo_indietro"], "indietro")

    def _chiedi_secondi(self, chiave, verso):
        """Ctrl e Maiuscolo con E: il passo del salto indietro o avanti; verso
        e' indietro o avanti, e sceglie le frasi."""
        self._domanda()
        attuale = self.impostazioni[chiave]
        avanti = verso == "avanti"
        domanda = _("Di quanti secondi salta avanti? Anche con i decimali, per esempio 2.5.") if avanti else _(
            "Di quanti secondi salta indietro? Anche con i decimali, per esempio 2.5.")
        with DialogoTesto(self, domanda, _("Passo di salto"), secondi_da_leggere(attuale)) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Il salto avanti resta di {durata}.").format(durata=valori.scrivi_durata(attuale)) if avanti else _(
                    "Il salto indietro resta di {durata}.").format(durata=valori.scrivi_durata(attuale)))
                return
            testo = dialogo.GetValue()
        secondi = leggi_tempo(testo)
        if not secondi or secondi < 0.1:
            # Traduttori: testo e' quello scritto nel campo, passo il passo di adesso in secondi.
            self._riscontro("errore", _("{testo} non è un numero di secondi valido; il passo resta {passo}.").format(testo=testo, passo=secondi_da_leggere(attuale)))
            return
        self.impostazioni[chiave] = round(secondi, 3)
        self._salva_impostazioni()
        durata = valori.scrivi_durata(round(secondi, 3))
        self._riscontro("passo_di_salto", _("Il salto avanti ora è di {durata}.").format(durata=durata) if avanti else _(
            "Il salto indietro ora è di {durata}.").format(durata=durata), "passo_di_salto")

    def _comando_passo_indietro(self):
        self._chiedi_secondi("passo_indietro", "indietro")

    def _comando_passo_avanti(self):
        self._chiedi_secondi("passo_avanti", "avanti")

    def _comando_posizione(self):
        """Q (issue 38): il punto del brano, 1:23 di 4:56, mancano 3:33."""
        if self._niente_in_corso(risveglia=True):
            return
        posizione, durata = self.motore.posizione, self.motore.durata
        if self.coda.corrente is not None:
            testo = self._tempo_di_dove_sono(self.coda.corrente)
        elif posizione is not None and durata is not None:
            # Traduttori: il punto del brano e la sua durata, come 1:23 di 4:56.
            testo = _("{tempo} di {durata}").format(tempo=tempo(posizione), durata=tempo(durata))
        else:
            testo = _("il tempo non si sa ancora")
        self._riporta(f"{testo[0].upper()}{testo[1:]}.", "salto")

    def _comando_verso_la_fine(self):
        """Alt con Q: un salto avanti prima della fine, per sentirne gli
        ultimi secondi."""
        if self._niente_in_corso(risveglia=True):
            return
        durata = self.motore.durata
        if durata is None:
            self._riscontro("non_disponibile", _("La durata del brano non si sa ancora: Alt con Q non sa dove sia la fine."))
            return
        self._salto(max(0, durata - self.impostazioni["passo_avanti"]) - (self.motore.posizione or 0), "avanti")

    def _comando_all_inizio(self):
        """Ctrl e Alt con Q: l'inizio del brano, senza farlo ripartire."""
        if self._niente_in_corso(risveglia=True):
            return
        self._salto(-(self.motore.posizione or 0), "indietro")

    def _comando_passi_dei_salti(self):
        """E (issue 38): i passi dei salti di Ctrl e Maiuscolo con Q."""
        imp = self.impostazioni
        self._riporta(_("Salto indietro di {indietro}, avanti di {avanti}; da {minimo} in su, e il predefinito è di {predefinito}.").format(
            indietro=valori.scrivi_durata(imp["passo_indietro"]), avanti=valori.scrivi_durata(imp["passo_avanti"]), minimo=valori.scrivi_durata(valori.SECONDI_MINIMI),
            predefinito=valori.scrivi_durata(PREDEFINITE["passo_avanti"])), "passo_di_salto")

    def _comando_passi_predefiniti(self):
        """Ctrl e Maiuscolo con E: i due passi dei salti tornano ai predefiniti."""
        for chiave in ("passo_indietro", "passo_avanti"):
            self.impostazioni[chiave] = PREDEFINITE[chiave]
        self._salva_impostazioni()
        self._riscontro("passo_di_salto", _("I salti indietro e avanti sono di nuovo di {durata}.").format(durata=valori.scrivi_durata(PREDEFINITE["passo_avanti"])),
            "passo_di_salto")

    def _comando_vai_a_tempo(self):
        if self._niente_in_corso(risveglia=True):
            return
        self._domanda()
        durata = self.motore.durata
        dura = _("Il brano dura {durata}.").format(durata=tempo(durata)) if durata is not None else _("La durata del brano non si sa ancora.")
        # Traduttori: dura e' la frase sulla durata del brano, come Il brano dura 3:45.
        with DialogoTesto(self, _("A che tempo andare? Minuti e secondi, per esempio 1:30, o dalla fine con il meno, per esempio -12. {dura}").format(dura=dura),
                _("Vai al tempo")) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Vai al tempo annullato."))
                return
            testo = dialogo.GetValue()
        secondi = leggi_tempo_nel_brano(testo, durata)
        if secondi is None:
            self._riscontro("errore", _("{testo} non è un tempo dentro il brano.").format(testo=testo))
            return
        self.motore.vai_a(secondi)
        # Traduttori: tempo e' il punto d'arrivo nel brano, durata quella del brano, come 1:20 di 3:45.
        self._riscontro("vai_a_tempo", _("Vado a {tempo} di {durata}.").format(tempo=tempo(secondi), durata=tempo(durata)) if durata is not None else _(
            "Vado a {tempo}.").format(tempo=tempo(secondi)))
        self._avvisa_l_attesa_del_sid(secondi)

    def _volume(self, passo):
        """Ctrl e Maiuscolo con M: il volume giu' o su di un passo."""
        attuale = self._volume_attuale()
        if attuale is None:
            self._riscontro("errore", _("Il volume di {nome} non si legge.").format(nome=self.motore.lontano.nome))
            return
        self._porta_il_volume(attuale + passo, passo)

    def _volume_attuale(self):
        """Il volume di adesso: quello dello speaker Cast, se la musica e'
        sua, che puo' non leggersi, altrimenti quello del motore."""
        lettore = self.motore.lontano
        return lettore.volume if lettore is not None else self.motore.volume

    def _porta_il_volume(self, nuovo, verso):
        """Porta il volume a nuovo, nei limiti: sul PC da 0 a 300, su uno
        speaker Cast da 0 a 100, senza amplificazione (1.119.0). verso, piu'
        o meno di zero, dice quale limite e' gia' raggiunto. Il suono, fatto
        al volo, dice il volume nuovo con la sua frequenza, dopo il
        riferimento del volume 100 (1.116.2)."""
        lettore = self.motore.lontano
        massimo = VOLUME_MASSIMO if lettore is None else 100
        attuale = self._volume_attuale()
        if attuale is None:
            self._riscontro("errore", _("Il volume non si legge.") if lettore is None else _("Il volume di {nome} non si legge.").format(nome=lettore.nome))
            return
        nuovo = max(0, min(massimo, nuovo))
        if nuovo == attuale:
            # Il volume di uno speaker Cast porta il suo nome, come Volume di Cucina.
            if nuovo == massimo and verso > 0:
                frase = _("Volume già al massimo, {volume}.").format(volume=attuale) if lettore is None else _(
                    "Volume di {nome} già al massimo, {volume}.").format(nome=lettore.nome, volume=attuale)
            elif nuovo == 0 and verso < 0:
                frase = _("Volume già al minimo, {volume}.").format(volume=attuale) if lettore is None else _(
                    "Volume di {nome} già al minimo, {volume}.").format(nome=lettore.nome, volume=attuale)
            else:
                frase = _("Volume già a {volume}.").format(volume=attuale) if lettore is None else _(
                    "Volume di {nome} già a {volume}.").format(nome=lettore.nome, volume=attuale)
            # Sullo speaker il 100 e' il suo massimo: lo si dice, perche' sul
            # PC si va fino a 300 (Gabriele, collaudo della 2.6.0).
            if lettore is not None and nuovo == massimo and verso > 0:
                frase += " " + _("Oltre il 100 si amplifica solo sulle schede del PC.")
            self._riscontro("volume_al_limite", frase, "volume")
            return
        if lettore is not None:
            lettore.volume = nuovo
        else:
            self.motore.volume = nuovo
            self.impostazioni["volume"] = nuovo
        self._domanda_viva = None
        self._conta_l_evento("volume_su" if nuovo > attuale else "volume_giu")
        suoni.volume_della_musica(nuovo, self.impostazioni["volume_effetti"])
        # Sullo speaker il volume arriva al piu' a 100: amplificato vale solo sul PC.
        if lettore is not None:
            frase = _("Volume di {nome} {volume}.").format(nome=lettore.nome, volume=nuovo)
        elif nuovo > 100:
            frase = _("Volume {volume}, amplificato oltre il 100.").format(volume=nuovo)
        else:
            frase = _("Volume {volume}.").format(volume=nuovo)
        self.scrivi(frase, "volume")

    def _comando_volume(self):
        """M (issue 38): il volume, con i suoi limiti, e quello a cui Ctrl e
        Maiuscolo con M lo riportano, se c'e'."""
        lettore = self.motore.lontano
        massimo = VOLUME_MASSIMO if lettore is None else 100
        volume = self._volume_attuale()
        if volume is None:
            self._riporta(_("Il volume non si legge.") if lettore is None else _("Il volume di {nome} non si legge.").format(nome=lettore.nome), "volume")
            return
        if lettore is None:
            frase = _("Volume {volume}, amplificato oltre il 100, da 0 a {massimo}.").format(volume=volume, massimo=massimo) if volume > 100 else _(
                "Volume {volume}, da 0 a {massimo}.").format(volume=volume, massimo=massimo)
        else:
            frase = _("Volume di {nome} {volume}, amplificato oltre il 100, da 0 a {massimo}.").format(nome=lettore.nome, volume=volume, massimo=massimo) if volume > 100 else _(
                "Volume di {nome} {volume}, da 0 a {massimo}.").format(nome=lettore.nome, volume=volume, massimo=massimo)
        prima = self._volume_di_prima()
        if prima is not None:
            frase += " " + _("Ctrl e Maiuscolo con M lo riportano a {volume}.").format(volume=prima)
        self._riporta(frase, "volume")

    def _comando_volume_su(self):
        self._volume(self.impostazioni["passo_volume"])

    def _comando_volume_giu(self):
        self._volume(-self.impostazioni["passo_volume"])

    def _comando_volume_massimo(self):
        """Alt con M: il volume al massimo, 300 sul PC e 100 sullo speaker."""
        self._volume_estremo(VOLUME_MASSIMO if self.motore.lontano is None else 100, 1)

    def _comando_volume_minimo(self):
        """Ctrl e Alt con M: il volume a zero, che fa da muto (Gabriele, 3
        novembre 2026)."""
        self._volume_estremo(0, -1)

    def _volume_estremo(self, nuovo, verso):
        """Al massimo o a zero: il volume di prima si ricorda, per Ctrl e
        Maiuscolo con M, se non era gia' al massimo o a zero; cosi' dallo
        zero al massimo resta quello da cui si era partiti."""
        attuale = self._volume_attuale()
        massimo = VOLUME_MASSIMO if self.motore.lontano is None else 100
        if attuale is not None and 0 < attuale < massimo and attuale != nuovo:
            self._ricorda_il_volume(attuale)
        self._porta_il_volume(nuovo, verso)

    def _comando_volume_di_prima(self):
        """Ctrl e Maiuscolo con M (Gabriele, 3 novembre 2026): il volume di
        prima che Alt o Ctrl e Alt con M lo portassero al massimo o a zero;
        dallo zero, toglie il muto."""
        prima = self._volume_di_prima()
        attuale = self._volume_attuale()
        if prima is None:
            self._riscontro("volume_al_limite", _("Il volume non è stato portato al massimo o a zero: resta {volume}.").format(volume=attuale), "volume")
            return
        self._ricorda_il_volume(None)
        self._porta_il_volume(prima, 1 if attuale is None or prima >= attuale else -1)

    def _volume_di_prima(self):
        """Il volume a cui Ctrl e Maiuscolo con M riportano, o None. Quello
        del PC sta nelle impostazioni, perche' lo zero dura anche dopo una
        chiusura; quello dello speaker vale finche' MeTeOra resta aperto."""
        if self.motore.lontano is not None:
            return self._volume_di_prima_dello_speaker
        prima = self.impostazioni["volume_di_prima"]
        return None if prima < 0 else prima

    def _ricorda_il_volume(self, volume):
        if self.motore.lontano is not None:
            self._volume_di_prima_dello_speaker = volume
        else:
            self.impostazioni["volume_di_prima"] = -1 if volume is None else volume

    def _comando_muto(self):
        """Il pulsante Muto della barra delle applicazioni: il volume a zero,
        come Ctrl e Alt con M, e dallo zero quello di prima, come Ctrl e
        Maiuscolo con M."""
        if self._volume_attuale() == 0 and self._volume_di_prima() is not None:
            self._comando_volume_di_prima()
        else:
            self._comando_volume_minimo()

    def _comando_passo_volume(self):
        """Il punto (issue 38): il passo di Ctrl e Maiuscolo con M."""
        self._riporta(_("Passo del volume {passo}, da {minimo} a {massimo}; il predefinito è {predefinito}.").format(passo=self.impostazioni["passo_volume"],
            minimo=valori.PASSO_VOLUME_MINIMO, massimo=valori.PASSO_VOLUME_MASSIMO, predefinito=PREDEFINITE["passo_volume"]), "passo_del_volume")

    def _porta_il_passo_del_volume(self, nuovo, verso):
        attuale = self.impostazioni["passo_volume"]
        nuovo = max(valori.PASSO_VOLUME_MINIMO, min(valori.PASSO_VOLUME_MASSIMO, nuovo))
        if nuovo == attuale:
            if nuovo == valori.PASSO_VOLUME_MASSIMO and verso > 0:
                frase = _("Passo del volume già al massimo, {passo}.").format(passo=attuale)
            elif nuovo == valori.PASSO_VOLUME_MINIMO and verso < 0:
                frase = _("Passo del volume già al minimo, {passo}.").format(passo=attuale)
            else:
                frase = _("Passo del volume già {passo}.").format(passo=attuale)
            self._riscontro("volume_al_limite", frase, "passo_del_volume")
            return
        self.impostazioni["passo_volume"] = nuovo
        self._salva_impostazioni()
        self._riscontro("passo_del_volume", _("Passo del volume {passo}: Ctrl e Maiuscolo con M cambiano il volume di {passo}.").format(passo=nuovo), "passo_del_volume")

    def _comando_passo_volume_giu(self):
        self._porta_il_passo_del_volume(self.impostazioni["passo_volume"] - 1, -1)

    def _comando_passo_volume_su(self):
        self._porta_il_passo_del_volume(self.impostazioni["passo_volume"] + 1, 1)

    def _comando_passo_volume_predefinito(self):
        self._porta_il_passo_del_volume(PREDEFINITE["passo_volume"], 0)

    def _comando_passo_volume_massimo(self):
        self._porta_il_passo_del_volume(valori.PASSO_VOLUME_MASSIMO, 1)

    def _comando_passo_volume_minimo(self):
        self._porta_il_passo_del_volume(valori.PASSO_VOLUME_MINIMO, -1)

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
        self.motore.replaygain = imp["replaygain"]
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
            return _("Velocità {velocita} e tono {tono}: Ctrl e Maiuscolo con A e con F li riportano al normale.").format(velocita=valori.scrivi_velocita(velocita),
                tono=valori.scrivi_tono(tono))
        if velocita != 1:
            return _("Velocità {velocita}: Ctrl e Maiuscolo con A la riportano al normale.").format(velocita=valori.scrivi_velocita(velocita))
        if tono:
            return _("Tono {tono}: Ctrl e Maiuscolo con F lo riportano al normale.").format(tono=valori.scrivi_tono(tono))
        return ""

    @staticmethod
    def _riga_della_velocita(velocita):
        if velocita == 1:
            return _("Velocità {velocita}, la normale.").format(velocita=valori.scrivi_velocita(velocita))
        return _("Velocità {velocita}.").format(velocita=valori.scrivi_velocita(velocita))

    @staticmethod
    def _riga_del_tono(tono):
        if tono == 0:
            return _("Tono {tono}, il normale.").format(tono=valori.scrivi_tono(tono))
        return _("Tono {tono}.").format(tono=valori.scrivi_tono(tono))

    def _velocita(self, nuova, evento):
        """Porta la velocita' a nuova, nei limiti; ai limiti lo dice con il
        suono suo."""
        # Traduttori: il soggetto di frasi come La velocità su Cucina non vale: vale sulle schede del PC.
        if self._vale_solo_sul_pc(_("La velocità")):
            return
        attuale = self.impostazioni["velocita"]
        nuova = max(valori.VELOCITA_MINIMA, min(valori.VELOCITA_MASSIMA, round(nuova, 2)))
        if nuova == attuale and evento != "velocita_normale":
            if nuova >= valori.VELOCITA_MASSIMA:
                frase = _("Velocità già al massimo, {velocita}.").format(velocita=valori.scrivi_velocita(attuale))
            else:
                frase = _("Velocità già al minimo, {velocita}.").format(velocita=valori.scrivi_velocita(attuale))
            self._riscontro("velocita_al_limite", frase, "velocita")
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

    def _comando_velocita_massima(self):
        self._velocita(valori.VELOCITA_MASSIMA, "velocita_su")

    def _comando_velocita_minima(self):
        self._velocita(valori.VELOCITA_MINIMA, "velocita_giu")

    def _comando_velocita(self):
        """A (issue 38): la velocita', con i suoi limiti."""
        velocita = self.impostazioni["velocita"]
        minima, massima = valori.scrivi_velocita(valori.VELOCITA_MINIMA), valori.scrivi_velocita(valori.VELOCITA_MASSIMA)
        if velocita == 1:
            frase = _("Velocità {velocita}, la normale, da {minima} a {massima}.").format(velocita=valori.scrivi_velocita(velocita), minima=minima, massima=massima)
        else:
            frase = _("Velocità {velocita}, da {minima} a {massima}.").format(velocita=valori.scrivi_velocita(velocita), minima=minima, massima=massima)
        self._riporta(frase, "velocita")

    def _tono(self, nuovo, evento):
        """Porta il tono a nuovo semitoni, nei limiti; ai limiti lo dice con il
        suono suo."""
        # Traduttori: il soggetto di frasi come La velocità su Cucina non vale: vale sulle schede del PC.
        if self._vale_solo_sul_pc(_("Il tono")):
            return
        attuale = self.impostazioni["tono"]
        nuovo = max(-valori.TONO_MASSIMO, min(valori.TONO_MASSIMO, nuovo))
        if nuovo == attuale and evento != "tono_normale":
            if nuovo > 0:
                frase = _("Tono già al massimo, {tono}.").format(tono=valori.scrivi_tono(attuale))
            else:
                frase = _("Tono già al minimo, {tono}.").format(tono=valori.scrivi_tono(attuale))
            self._riscontro("tono_al_limite", frase, "tono")
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

    def _comando_tono_massimo(self):
        self._tono(valori.TONO_MASSIMO, "tono_su")

    def _comando_tono_minimo(self):
        self._tono(-valori.TONO_MASSIMO, "tono_giu")

    def _comando_tono(self):
        """F (issue 38): il tono, con i suoi limiti."""
        tono = self.impostazioni["tono"]
        minimo, massimo = valori.scrivi_tono(-valori.TONO_MASSIMO), valori.scrivi_tono(valori.TONO_MASSIMO)
        if tono == 0:
            frase = _("Tono {tono}, il normale, da {minimo} a {massimo}.").format(tono=valori.scrivi_tono(tono), minimo=minimo, massimo=massimo)
        else:
            frase = _("Tono {tono}, da {minimo} a {massimo}.").format(tono=valori.scrivi_tono(tono), minimo=minimo, massimo=massimo)
        self._riporta(frase, "tono")

    def _banda_e_guadagno(self):
        """La banda scelta e il suo guadagno, per le sue righe: Banda 3, 400
        Hz e +2 dB. La maiuscola non viene da capitalize, che scriverebbe hz."""
        nome = valori.nome_della_banda(self._banda)
        return f"{nome[0].upper()}{nome[1:]}", valori.scrivi_guadagno(self.impostazioni["bande"][self._banda])

    def _riga_della_banda(self):
        """La riga della banda scelta: Banda 3, 400 Hz: +2 dB. Le righe con
        un'aggiunta, come il massimo, sono frasi intere (3.0.0)."""
        banda, guadagno = self._banda_e_guadagno()
        return f"{banda}: {guadagno}."

    def _scegli_la_banda(self, passo):
        """Ctrl e Maiuscolo con U: la banda prima o dopo."""
        self._alla_banda(self._banda + passo, passo)

    def _alla_banda(self, nuova, verso):
        """La banda nuova, contata da zero; si ferma alla prima e all'ultima,
        e lo dice. Il suono, fatto al volo, dice la banda con una nota della
        scala."""
        # Traduttori: il soggetto di frasi come La velocità su Cucina non vale: vale sulle schede del PC.
        if self._vale_solo_sul_pc(_("L'equalizzatore")):
            return
        nuova = max(0, min(len(valori.FREQUENZE_DELLE_BANDE) - 1, nuova))
        if nuova == self._banda:
            banda, guadagno = self._banda_e_guadagno()
            # Traduttori: banda e' come Banda 3, 400 Hz, guadagno come +2 dB.
            frase = _("{banda}: {guadagno}. È la prima.").format(banda=banda, guadagno=guadagno) if verso < 0 else _(
                "{banda}: {guadagno}. È l'ultima.").format(banda=banda, guadagno=guadagno)
            self._riscontro("banda_al_limite", frase, "banda")
            return
        self._banda = nuova
        suoni.banda(nuova, self.impostazioni["volume_effetti"])
        self.scrivi(self._riga_della_banda(), "banda")

    def _comando_prima_banda(self):
        self._alla_banda(0, -1)

    def _comando_ultima_banda(self):
        self._alla_banda(len(valori.FREQUENZE_DELLE_BANDE) - 1, 1)

    def _comando_banda(self):
        """U (issue 38): la banda scelta, fra quante, e il suo guadagno."""
        frequenza = valori.FREQUENZE_DELLE_BANDE[self._banda]
        guadagno = valori.scrivi_guadagno(self.impostazioni["bande"][self._banda])
        self._riporta(_("Banda {numero} di {totale}, {frequenza} Hz: {guadagno}.").format(numero=self._banda + 1, totale=len(valori.FREQUENZE_DELLE_BANDE),
            frequenza=frequenza, guadagno=guadagno), "banda")

    def _comando_guadagno(self):
        """O (issue 38): il guadagno della banda scelta, con i suoi limiti."""
        banda, guadagno = self._banda_e_guadagno()
        # Traduttori: banda e' come Banda 3, 400 Hz, guadagno come +2 dB; minimo e massimo i guadagni ai limiti.
        self._riporta(_("{banda}: {guadagno}, da {minimo} a {massimo}.").format(banda=banda, guadagno=guadagno,
            minimo=valori.scrivi_guadagno(-valori.GUADAGNO_MASSIMO), massimo=valori.scrivi_guadagno(valori.GUADAGNO_MASSIMO)), "banda")

    def _comando_curva(self):
        """P (issue 38): i guadagni di tutte le bande, dalla piu' bassa."""
        bande = self.impostazioni["bande"]
        if not any(bande):
            self._riporta(ngettext("Equalizzatore piatto: tutte le {n} bande a 0 dB.", "Equalizzatore piatto: tutte le {n} bande a 0 dB.", len(bande)).format(n=len(bande)), "banda")
            return
        curva = ", ".join(f"{frequenza} Hz {valori.scrivi_guadagno(guadagno)}" for frequenza, guadagno in zip(valori.FREQUENZE_DELLE_BANDE, bande, strict=True))
        # Traduttori: curva sono i guadagni di tutte le bande, come 60 Hz +2 dB, 150 Hz 0 dB.
        self._riporta(_("Equalizzatore: {curva}.").format(curva=curva), "banda")

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
        """Ctrl e Maiuscolo con O: la banda scelta giu' o su di un dB."""
        self._porta_il_guadagno(self.impostazioni["bande"][self._banda] + passo, passo)

    def _porta_il_guadagno(self, nuovo, verso):
        """Il guadagno della banda scelta a nuovo, nei limiti, che dice. Il
        suono, fatto al volo, dice il guadagno con l'altezza della nota."""
        # Traduttori: il soggetto di frasi come La velocità su Cucina non vale: vale sulle schede del PC.
        if self._vale_solo_sul_pc(_("L'equalizzatore")):
            return
        bande = list(self.impostazioni["bande"])
        nuovo = max(-valori.GUADAGNO_MASSIMO, min(valori.GUADAGNO_MASSIMO, nuovo))
        if nuovo == bande[self._banda]:
            banda, guadagno = self._banda_e_guadagno()
            # Traduttori: banda e' come Banda 3, 400 Hz, guadagno come +2 dB.
            frase = _("{banda}: {guadagno}, il massimo.").format(banda=banda, guadagno=guadagno) if verso > 0 else _(
                "{banda}: {guadagno}, il minimo.").format(banda=banda, guadagno=guadagno)
            self._riscontro("guadagno_al_limite", frase, "banda")
            return
        bande[self._banda] = nuovo
        self._metti_le_bande(bande)
        self._statistiche.banda(self._banda)
        suoni.guadagno(nuovo, self.impostazioni["volume_effetti"])
        self.scrivi(self._riga_della_banda(), "banda")

    def _comando_guadagno_massimo(self):
        self._porta_il_guadagno(valori.GUADAGNO_MASSIMO, 1)

    def _comando_guadagno_minimo(self):
        self._porta_il_guadagno(-valori.GUADAGNO_MASSIMO, -1)

    def _comando_banda_su(self):
        self._guadagno(1)

    def _comando_banda_giu(self):
        self._guadagno(-1)

    def _comando_azzera_la_banda(self):
        # Traduttori: il soggetto di frasi come La velocità su Cucina non vale: vale sulle schede del PC.
        if self._vale_solo_sul_pc(_("L'equalizzatore")):
            return
        bande = list(self.impostazioni["bande"])
        bande[self._banda] = 0
        self._metti_le_bande(bande)
        banda, guadagno = self._banda_e_guadagno()
        # Traduttori: banda e' come Banda 3, 400 Hz, guadagno come 0 dB; azzerata si riferisce alla banda.
        self._riscontro("banda_azzerata", _("{banda}: {guadagno}, azzerata.").format(banda=banda, guadagno=guadagno), "banda")

    def _comando_azzera_le_bande(self):
        # Traduttori: il soggetto di frasi come La velocità su Cucina non vale: vale sulle schede del PC.
        if self._vale_solo_sul_pc(_("L'equalizzatore")):
            return
        self._metti_le_bande([0] * len(valori.FREQUENZE_DELLE_BANDE))
        self._riscontro("bande_azzerate", _("Equalizzatore azzerato, tutte a 0 dB."), "banda")

    def _comando_dissolvenza(self):
        """L (issue 38): la dissolvenza, accesa o spenta, e la sua durata."""
        # Traduttori: dissolvenza e' come accesa, 4 secondi, oppure spenta.
        self._riporta(_("Dissolvenza {dissolvenza}.").format(dissolvenza=valori.scrivi_dissolvenza(self.impostazioni["dissolvenza"])), "dissolvenza")

    def _metti_la_dissolvenza(self, accesa):
        """Ctrl con L la spegne, Maiuscolo con L la accende; la durata resta."""
        # Traduttori: il soggetto di frasi come La velocità su Cucina non vale: vale sulle schede del PC.
        if self._vale_solo_sul_pc(_("La dissolvenza")):
            return
        dissolvenza = self.impostazioni["dissolvenza"]
        evento = "dissolvenza_accesa" if accesa else "dissolvenza_spenta"
        if dissolvenza["accesa"] == accesa:
            # Traduttori: dissolvenza e' come accesa, 4 secondi, oppure spenta.
            self._riscontro(evento, _("La dissolvenza è già {dissolvenza}.").format(dissolvenza=valori.scrivi_dissolvenza(dissolvenza)), "dissolvenza")
            return
        dissolvenza["accesa"] = accesa
        self._applica_la_dissolvenza()
        self._salva_impostazioni()
        # Traduttori: dissolvenza e' come accesa, 4 secondi, oppure spenta.
        self._riscontro(evento, _("Dissolvenza {dissolvenza}.").format(dissolvenza=valori.scrivi_dissolvenza(dissolvenza)), "dissolvenza")

    def _comando_spegni_la_dissolvenza(self):
        self._metti_la_dissolvenza(False)

    def _comando_accendi_la_dissolvenza(self):
        self._metti_la_dissolvenza(True)

    def _comando_riproduzione_casuale(self):
        """N (issue 38): la riproduzione casuale, accesa o spenta, e il suo modello."""
        self._riporta(_frase_della_casuale(self.impostazioni["casuale"], self.impostazioni["modello_casuale"]), "casuale")

    def _metti_la_casuale(self, accesa):
        """Ctrl con N spegne la riproduzione casuale, Maiuscolo con N la
        accende (issue 17): a caso il brano che segue quando uno finisce da
        solo, e dalla 1.74.0 anche B, mentre Z torna ai brani suonati prima."""
        evento = "casuale_acceso" if accesa else "casuale_spento"
        frase = _frase_della_casuale(accesa, self.impostazioni["modello_casuale"])
        if self.impostazioni["casuale"] == accesa:
            # Traduttori: frase dice la riproduzione casuale di adesso, come Riproduzione casuale spenta.
            self._riscontro(evento, _("Già così. {frase}").format(frase=frase))
            return
        self.impostazioni["casuale"] = accesa
        self._ricomincia_il_mazzo()
        self._azzera_la_storia()
        self._salva_impostazioni()
        self._riscontro(evento, frase)

    def _comando_spegni_la_casuale(self):
        self._metti_la_casuale(False)

    def _comando_accendi_la_casuale(self):
        self._metti_la_casuale(True)

    def _comando_ripetizione(self):
        """Maiuscolo con V (Gabriele, 1.94.0): la ripetizione a giro, del
        brano, della lista, spenta. Il seguente gia' preparato per la
        dissolvenza si ricontrolla al passaggio, come sempre."""
        chiavi = list(valori.RIPETIZIONI)
        ripetizione = chiavi[(chiavi.index(self.impostazioni["ripetizione"]) + 1) % len(chiavi)]
        self.impostazioni["ripetizione"] = ripetizione
        self._salva_impostazioni()
        self._riscontro(f"ripetizione_{ripetizione}", _frase_della_ripetizione(ripetizione))

    def _comando_durata_della_dissolvenza(self):
        """K (issue 38): la durata della dissolvenza, con i suoi limiti."""
        dissolvenza = self.impostazioni["dissolvenza"]
        durata, minima, massima = (valori.scrivi_durata(s) for s in (dissolvenza["secondi"], valori.DISSOLVENZA_MINIMA, valori.DISSOLVENZA_MASSIMA))
        if dissolvenza["accesa"]:
            frase = _("Durata della dissolvenza {durata}, da {minima} a {massima}; la dissolvenza è accesa.").format(durata=durata, minima=minima, massima=massima)
        else:
            frase = _("Durata della dissolvenza {durata}, da {minima} a {massima}; la dissolvenza è spenta.").format(durata=durata, minima=minima, massima=massima)
        self._riporta(frase, "dissolvenza")

    def _porta_la_dissolvenza(self, secondi, verso):
        """La durata della dissolvenza a secondi, nei limiti, che dice. La
        dissolvenza resta accesa o spenta com'era."""
        # Traduttori: il soggetto di frasi come La velocità su Cucina non vale: vale sulle schede del PC.
        if self._vale_solo_sul_pc(_("La dissolvenza")):
            return
        dissolvenza = self.impostazioni["dissolvenza"]
        secondi = max(valori.DISSOLVENZA_MINIMA, min(valori.DISSOLVENZA_MASSIMA, round(secondi, 3)))
        if secondi == dissolvenza["secondi"]:
            durata = valori.scrivi_durata(secondi)
            if secondi == valori.DISSOLVENZA_MASSIMA and verso > 0:
                frase = _("Durata della dissolvenza già al massimo, {durata}.").format(durata=durata)
            elif secondi == valori.DISSOLVENZA_MINIMA and verso < 0:
                frase = _("Durata della dissolvenza già al minimo, {durata}.").format(durata=durata)
            else:
                frase = _("Durata della dissolvenza già {durata}.").format(durata=durata)
            self._riscontro("nessun_altro_brano", frase, "dissolvenza")
            return
        dissolvenza["secondi"] = secondi
        self._applica_la_dissolvenza()
        self._salva_impostazioni()
        # Traduttori: dissolvenza e' come accesa, 4 secondi, oppure spenta.
        self._riscontro("dissolvenza_durata", _("Dissolvenza {dissolvenza}.").format(dissolvenza=valori.scrivi_dissolvenza(dissolvenza)), "dissolvenza")

    def _comando_dissolvenza_piu_breve(self):
        self._porta_la_dissolvenza(self.impostazioni["dissolvenza"]["secondi"] - PASSO_DELLA_DISSOLVENZA, -1)

    def _comando_dissolvenza_piu_lunga(self):
        self._porta_la_dissolvenza(self.impostazioni["dissolvenza"]["secondi"] + PASSO_DELLA_DISSOLVENZA, 1)

    def _comando_durata_predefinita(self):
        self._porta_la_dissolvenza(PREDEFINITE["dissolvenza"]["secondi"], 0)

    def _comando_dissolvenza_massima(self):
        self._porta_la_dissolvenza(valori.DISSOLVENZA_MASSIMA, 1)

    def _comando_dissolvenza_minima(self):
        self._porta_la_dissolvenza(valori.DISSOLVENZA_MINIMA, -1)

    def _comando_apri_file(self):
        self._domanda()
        with DialogoDiFile(self, _("Apri file"), wildcard=formati.filtro_dialogo(), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Nessun file aperto."))
                return
            percorso = dialogo.GetPath()
        if formati.e_playlist(percorso):
            # Una playlist di altri programmi si importa, e poi suona (1.113.0).
            self._importa_le_playlist([percorso], "suona")
            return
        # Il file aperto non entra in nessuna playlist: resta finche' non si
        # suona altro. La sua cartella vuota lo tiene fuori da Questo PC.
        # Traduttori: il nome della lista di un file aperto da solo, come in In riproduzione: C:\musica\a.mp3, file aperto.
        pl = Playlist(_("file aperto"), [Brano(percorso)], cartella="")
        self._suona(pl, pl.brani[0], "file_aperto")

    # Le statistiche (Gabriele, 17 ottobre 2026, 1.103.0).

    def _stato_per_le_statistiche(self):
        """Lo stato di adesso, per l'orologio delle statistiche: cosa suona,
        come e da dove. La durata e' una funzione, perche' la si chiede a mpv
        solo quando serve."""
        motore, imp = self.motore, self.impostazioni
        percorso = motore.in_corso
        if not percorso:
            return {"stato": "fermo"}
        immagine = self._video is not None and self._video.IsShown()
        return {
            "stato": "pausa" if motore.in_pausa else "play", "percorso": percorso, "video": formati.e_video(percorso),
            "immagine": immagine, "schermo_intero": immagine and self._video.IsFullScreen(),
            "volume": motore.volume, "muto": motore.muto, "velocita": motore.velocita, "tono": motore.tono, "eq": any(imp["bande"]),
            "dissolvenza": imp["dissolvenza"]["accesa"], "casuale": imp["casuale"], "ripetizione": imp["ripetizione"],
            "replaygain": imp["replaygain"], "scheda": self._scheda_per_le_statistiche, "sorgente": self._sorgente_per_le_statistiche(),
            # Con le regole dello schedario: un file rovinato che dice 37 ore in
            # pochi KB non diventa il record del brano piu' lungo (1.104.0).
            "durata": lambda: credibile(self.motore.durata, percorso, (self.schedario.scheda(percorso) or {}).get("dim")),
        }

    def _sorgente_per_le_statistiche(self):
        """Da dove suona il brano in corso, come lo dicono le statistiche."""
        pl = self.coda.playlist
        if pl is None:
            return "altro"
        if pl is self.archivio.preferiti:
            return "Preferiti"
        if pl in self.archivio.playlist:
            return f"playlist {pl.nome}"
        if pl is self.risultati:
            return "Risultati della ricerca"
        if getattr(pl, "selezione", False):
            return "selezioni della plancia"
        return "cartelle di Questo PC e Questa rete" if pl.cartella else "file aperti da soli"

    def _scatto_delle_statistiche(self):
        """Un passo dell'orologio delle statistiche, appena la finestra ha
        tutto cio' che guarda."""
        if self._orologio_pronto and not self._chiusa:
            self._statistiche.scatta(self._stato_per_le_statistiche())

    def _giro_delle_statistiche(self, _evento):
        """Ogni GIRO_DELLE_STATISTICHE un passo; a ogni giro del minuto la
        scheda audio di adesso, e il file del crash che si svuota: le
        eccezioni che le librerie gestiscono da se' passano nel registro degli
        errori, e alla riapertura dopo una chiusura a forza non sembrano un
        crash (1.104.0). Il file delle statistiche, scritto in disparte, solo
        se sono cambiate davvero e se dall'ultimo salvataggio sono passati
        MINUTI_FRA_I_SALVATAGGI_DELLE_STATISTICHE minuti: con MeTeOra fermo
        non si scrive niente (1.113.5). Un salvataggio che non riesce lo si
        dice una volta sola."""
        if self._chiusa:
            return
        self._scatto_delle_statistiche()
        self._annota_il_punto_di_ripresa()
        self._giri_delle_statistiche += 1
        if self._giri_delle_statistiche % GIRI_IN_UN_MINUTO == 1:
            self._aggiorna_la_scheda_delle_statistiche()
        if self._giri_delle_statistiche % GIRI_IN_UN_MINUTO == 0:
            self._minuti_dal_salvataggio_delle_statistiche += 1
            if self._statistiche.modificate and self._minuti_dal_salvataggio_delle_statistiche >= MINUTI_FRA_I_SALVATAGGI_DELLE_STATISTICHE:
                self._salva_le_statistiche_in_disparte()
            registro.sopravvissuto()

    def _annota_il_punto_di_ripresa(self):
        """Il brano in corso e il suo punto, ogni secondo: se la sua uscita
        audio si perde, riparte da qui (1.116.0)."""
        percorso = self.motore.in_corso
        self._punto_di_ripresa = (percorso, self.motore.sottobrano, self.motore.posizione) if percorso else None

    def _salva_le_statistiche_in_disparte(self):
        self._minuti_dal_salvataggio_delle_statistiche = 0
        self._statistiche.salva_in_disparte(lambda e: wx.CallAfter(self._statistiche_non_salvate_in_disparte, e))

    def _statistiche_non_salvate_in_disparte(self, errore):
        self._statistiche.conta("salvataggi_non_riusciti")
        if self._chiusa or self._statistiche_non_salvate:
            return
        self._statistiche_non_salvate = True
        self._riscontro("errore", _("Non riesco a salvare le statistiche: {errore}.").format(errore=errore.strerror or errore))

    def _aggiorna_la_scheda_delle_statistiche(self):
        """Il nome della scheda audio su cui suona la musica, per le
        statistiche: quella scelta, o quella che Windows usa con la scelta
        automatica, chiesta senza aprire niente. Una scheda scelta che
        manca, o che non si apre, non conta: intanto si suona
        sull'automatica, ed e' lei che prende il tempo (1.116.1)."""
        if self.motore.lontano is not None:
            self._scheda_per_le_statistiche = f"Speaker {self.motore.lontano.nome}"
            return
        scelta = self._scelta_del_pc()
        if scelta and not self._scheda_in_disparte:
            self._scheda_per_le_statistiche = self._nome_della_scheda(scelta["dispositivo"], scelta["interfaccia"])
            return
        uscita = None
        with contextlib.suppress(Exception):
            uscita = schede_audio.in_uso()
        self._scheda_per_le_statistiche = f"Automatica ({self._nome_della_scheda(uscita['dispositivo'], uscita['interfaccia'])})" if uscita else "Automatica"

    def conta_un_clic(self):
        """Un comando dalla barra dei comandi per il mouse."""
        self._statistiche.conta("clic_sulla_barra")

    def _nome_del_tasto(self, evento):
        """Il nome di un tasto premuto nella finestra, per le statistiche;
        None per i modificatori premuti da soli e per la ripetizione di un
        tasto tenuto giu'."""
        codice = evento.GetKeyCode()
        if codice in _SOLO_MODIFICATORI or evento.IsAutoRepeat():
            return None
        modificatori = evento.GetModifiers()
        if codice in NOMI_DEI_TASTI:
            nome = NOMI_DEI_TASTI[codice]
        elif (tasto := carattere_del_tasto(evento)) is not None:
            # Il punto interrogativo e' Maiuscolo con l'apostrofo, comunque
            # arrivi: la durata residua ha un nome solo (tappa 14 d).
            carattere, modificatori = tasto
            if modificatori == MAIUSCOLO and carattere in CIFRE_COL_MAIUSCOLO:
                carattere = str(CIFRE_COL_MAIUSCOLO[carattere] % 10)
            return nome_del_carattere(carattere, modificatori)
        else:
            nome = "Altro tasto"
        prefisso = [n for bit, n in ((wx.MOD_CONTROL, "Ctrl"), (wx.MOD_ALT, "Alt"), (wx.MOD_SHIFT, "Maiuscolo")) if modificatori & bit]
        return f"{' e '.join(prefisso)} con {nome}" if prefisso else nome

    def _comandi_dei_tasti(self):
        """Il comando di ogni tasto a carattere, per il nome che ha nelle statistiche."""
        return {nome_del_carattere(carattere, modificatori): comando for (carattere, modificatori), comando in TASTI.items()}

    def _conta_la_ricerca(self, dove):
        """La ricerca finita, una volta sola: i risultati, e i record."""
        if self._ricerca_contata:
            return
        self._ricerca_contata = True
        risultati = len(self.risultati.brani)
        self._statistiche.conta("risultati", risultati)
        if not risultati:
            self._statistiche.conta("ricerche_senza_risultati")
        # Traduttori: il record della ricerca nelle statistiche; testo e' cio' che si e' cercato.
        cosa = f"{self._testo_della_ricerca}{dove}" if dove else _("{testo} in tutto MeTeOra").format(testo=self._testo_della_ricerca)
        self._statistiche.massimo("risultati", risultati, cosa)
        if self._inizio_della_ricerca is not None:
            self._statistiche.massimo("ricerca_piu_lunga", round(time.monotonic() - self._inizio_della_ricerca, 1), cosa)

    def _comando_statistiche(self):
        """La voce Statistiche della plancia, e Maiuscolo con F7: la libreria
        di adesso si conta in disparte, dalla copia delle schede, e poi si
        apre la finestra. Mentre la libreria si conta, un'altra richiesta non
        apre una seconda finestra."""
        if self._statistiche_in_arrivo:
            return
        self._statistiche_in_arrivo = True
        self._scatto_delle_statistiche()
        schede = self.schedario.istantanea()
        self._in_disparte(lambda: statistiche.censisci_la_libreria(schede), self._apri_le_statistiche)

    def _apri_le_statistiche(self, censimento):
        """La finestra delle statistiche, con la libreria contata. Un
        conteggio non riuscito arriva come righe, e le dice la sua sezione."""
        self._statistiche_in_arrivo = False
        if self._chiusa:
            return
        if isinstance(censimento, dict):
            libreria = self._righe_del_patrimonio() + statistiche.righe_della_libreria(censimento, dettagli.dimensione)
            numeri = statistiche.numeri_della_libreria(censimento)
        else:
            libreria, numeri = self._righe_del_patrimonio() + list(censimento), {}
        self._suono("statistiche")
        azioni = {"azzera": lambda genitore: self._azzera_le_statistiche(genitore, libreria, numeri), "cerca": self._cerca_nelle_statistiche,
            "suono": self._suono, "riscontro": self._riscontro}
        with FinestraStatistiche(self, self._testo_delle_statistiche(libreria, numeri), azioni) as dialogo:
            dialogo.ShowModal()

    def _testo_delle_statistiche(self, libreria, numeri):
        self._scatto_delle_statistiche()
        nomi = {chiave: etichetta for chiave, (etichetta, _participio) in VOCI_DELLE_IMPOSTAZIONI.items()}
        return "\n".join(self._statistiche.righe(version.VERSION, scheda=self.schedario.scheda, libreria=libreria, numeri_della_libreria=numeri,
            comandi_dei_tasti=self._comandi_dei_tasti(), nomi_delle_impostazioni=nomi))

    def _righe_del_patrimonio(self):
        """Le righe della libreria di adesso che non vengono dallo
        schedario: playlist, Preferiti, marker, punti da riprendere e
        percorsi di rete."""
        playlist = self.archivio.playlist
        brani = [b for pl in playlist for b in pl.brani]
        # Traduttori: brani e' come 12 brani, 45 minuti.
        righe = [_("Playlist: {n}, con {brani}.").format(n=len(playlist), brani=self._brani_e_durata(brani)) if playlist else _("Playlist: nessuna, oltre ai Preferiti."),
            # Traduttori: brani e' come 12 brani, 45 minuti.
            _("Preferiti: {brani}.").format(brani=self._brani_e_durata(self.archivio.preferiti.brani))]
        if playlist:
            lunga = max(playlist, key=lambda pl: len(pl.brani))
            righe.append(ngettext("La playlist più lunga: {nome}, {n} brano.", "La playlist più lunga: {nome}, {n} brani.", len(lunga.brani)).format(
                nome=lunga.nome, n=len(lunga.brani)))
        voci = self.marcatori.voci
        quanti = sum(len(voce["marker"]) for voce in voci.values())
        # Traduttori: marker e' quanti marker ci sono in tutto, n su quanti brani.
        righe.append(ngettext("Marker di adesso: {marker}, su {n} brano.", "Marker di adesso: {marker}, su {n} brani.", len(voci)).format(marker=quanti, n=len(voci)))
        if voci:
            voce = max(voci.values(), key=lambda v: len(v["marker"]))
            nome = os.path.basename((voce.get("percorsi") or [voce.get("file") or ""])[0])
            # Traduttori: n e' quanti marker ha il brano.
            righe.append(_("Il brano con più marker adesso: {nome}, {n}.").format(nome=nome, n=len(voce["marker"])))
        righe.append(_("File lunghi con un punto da riprendere: {n}.").format(n=self.posizioni.quante()))
        righe.append(_("Percorsi di rete scritti a mano: {n}.").format(n=len(self.impostazioni["percorsi_di_rete"])))
        return righe

    def _brani_e_durata(self, brani):
        """Quanti brani e quanto durano, a parole, per le statistiche."""
        durate = [self.schedario.durata(b) for b in brani]
        note = [d for d in durate if d is not None]
        testo = plurale(len(brani), "{n} brano", "{n} brani")
        if note:
            testo += f", {statistiche.durata(sum(note))}"
        if len(note) < len(durate):
            # Traduttori: segue come 12 brani, 45 minuti; n sono i brani di cui la durata non si sa.
            testo += ngettext(", più {n} di cui la durata non si sa", ", più {n} di cui la durata non si sa", len(durate) - len(note)).format(n=len(durate) - len(note))
        return testo

    def _azzera_le_statistiche(self, genitore, libreria, numeri):
        """Azzera le statistiche nella loro finestra, dopo una conferma con No
        come risposta predefinita: da' il testo nuovo, o None se restano."""
        if not self._conferma(_("Azzero tutte le statistiche? I conti ripartono da zero, e non si torna indietro; restano la data della prima raccolta "
                "e quante volte le hai azzerate. La copia dell'ultimo avvio resta nella cartella copie."), _("Azzera le statistiche"), genitore):
            self._annullato(_("Le statistiche restano come sono."))
            return None
        self._statistiche.azzera()
        self._salva_le_statistiche()
        self._riscontro("statistiche_azzerate", _("Statistiche azzerate: i conti ripartono da adesso."))
        return self._testo_delle_statistiche(libreria, numeri)

    def _salva_le_statistiche(self):
        try:
            self._statistiche.salva()
        except OSError as e:
            self._statistiche.conta("salvataggi_non_riusciti")
            self._riscontro("errore", _("Non riesco a salvare le statistiche: {errore}.").format(errore=e.strerror or e))

    def _cerca_nelle_statistiche(self, genitore, testo):
        """La barra rovesciata nelle statistiche, come nella console: il
        campo con le istruzioni, e se il testo non si capisce lo spiega e lo
        ripropone. Da' (testo, espressione), o None se la ricerca e' annullata."""
        while True:
            self._domanda()
            with FinestraFiltro(genitore, _("Cerca nelle statistiche"), testo, ISTRUZIONI_DELLE_STATISTICHE) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self._annullato(_("Ricerca nelle statistiche annullata."))
                    return None
                testo = " ".join(dialogo.testo.splitlines()).strip()
            if not testo:
                self._annullato(_("Ricerca nelle statistiche annullata: il testo è vuoto."))
                return None
            try:
                return testo, modello_della_console(testo)
            except ErroreFiltro as e:
                self._riscontro("errore", _("Nella ricerca non capisco: {errore}").format(errore=e))

    # Le impostazioni, piano 5.8.

    def _comando_impostazioni(self):
        """La finestra delle impostazioni: una lista piatta, una riga per voce;
        Invio su una voce la cambia, o fa la sua azione. La apre la voce
        Impostazioni della plancia, e dalla 2.6.0 il piu' da tutta la finestra."""
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
            "replaygain": lambda: valori.VOLUMI_UNIFORMI[imp["replaygain"]],
            "scheda_audio": self._scheda_da_leggere,
            "passo_indietro": lambda: valori.scrivi_durata(imp["passo_indietro"]),
            "passo_avanti": lambda: valori.scrivi_durata(imp["passo_avanti"]),
            "velocita": lambda: valori.scrivi_velocita(imp["velocita"]),
            "tono": lambda: valori.scrivi_tono(imp["tono"]),
            "bande": self._bande_da_leggere,
            "dissolvenza": lambda: valori.scrivi_dissolvenza(imp["dissolvenza"]),
            # Traduttori: il valore di una voce delle impostazioni, come Video: sì; e' anche una delle risposte che il suo campo accetta.
            "casuale": lambda: _("sì") if imp["casuale"] else _("no"),
            "modello_casuale": lambda: valori.MODELLI_CASUALI[imp["modello_casuale"]],
            "ripetizione": lambda: valori.RIPETIZIONI[imp["ripetizione"]],
            "video": lambda: _("sì") if imp["video"] else _("no"),
            "sottotitoli": lambda: _("sì") if imp["sottotitoli"] else _("no"),
            "sintesi": self._sintesi_da_leggere,
            "destinazione": lambda: sintesi.DESTINAZIONI[imp["destinazione"]],
            "karaoke": lambda: MODI_DEL_KARAOKE[imp["karaoke"]],
            "anticipo_karaoke": lambda: f"{imp['anticipo_karaoke']} ms",
            # Traduttori: le celle della barra braille a 0, come Celle della barra braille: 0, il testo intero.
            "celle_braille": lambda: str(imp["celle_braille"]) if imp["celle_braille"] else _("0, il testo intero"),
            "lettura_minima": lambda: f"{imp['lettura_minima']} ms",
            "banco_midi": self._banco_da_leggere,
            "insegui": lambda: _("sì") if imp["insegui"] else _("no"),
            # Traduttori: la voce Punto lasciato dei file lunghi, come Punto lasciato dei file lunghi: oltre 30 minuti, oppure mai.
            "ripresa_oltre": lambda: ngettext("oltre {n} minuti", "oltre {n} minuti", imp["ripresa_oltre"]).format(n=imp["ripresa_oltre"]) if imp["ripresa_oltre"] else _("mai"),
            "lingua": self._lingua_da_leggere,
            "caratteri": self._caratteri_da_leggere,
            "colori_testo": lambda: self._colori_da_leggere("colori_testo"),
            "colori_sfondo": lambda: self._colori_da_leggere("colori_sfondo"),
            "barra_dei_comandi": lambda: _("sì") if imp["barra_dei_comandi"] else _("no"),
            "stato_della_selezione": lambda: _("sì") if imp["stato_della_selezione"] else _("no"),
            "righe_della_console": lambda: str(imp["righe_della_console"]),
            "salva_console": lambda: _("scrive la console in un file di testo"),
            "marcatori": self._marcatori_da_leggere,
            "importa_marcatori": lambda: _("da un file esportato da MeTeOra"),
            "associazioni": lambda: _("Apri con MeTeOra e app predefinite di Windows") if getattr(sys, "frozen", False) else _("solo dal programma compilato"),
            "impressi": lambda: MODI_DEGLI_IMPRESSI[imp["impressi"]],
            "dona": lambda: _("offri un caffè all'autore, con PayPal"),
            "entra_al_pub": lambda: _("prepara la mail che ti iscrive alla lista di supporto"),
            "chiedi_aiuto_al_pub": lambda: _("prepara una mail alla lista, con la tua domanda e le informazioni del computer"),
        }[chiave]()
        return f"{VOCI_DELLE_IMPOSTAZIONI[chiave][0]}: {valore}"

    def _bande_da_leggere(self):
        """I guadagni dell'equalizzatore come li scrive il campo, in dB, o
        piatto se sono tutti a zero."""
        bande = self.impostazioni["bande"]
        # Traduttori: la voce Equalizzatore, come Equalizzatore: piatto, tutte le bande a 0 dB.
        return f"{valori.scrivi_bande(bande)} dB" if any(bande) else _("piatto, tutte le bande a 0 dB")

    def _caratteri_da_leggere(self):
        caratteri = self.impostazioni["caratteri"]
        if not caratteri:
            # Traduttori: la voce Dimensioni dei caratteri, come Dimensioni dei caratteri: quelle di Windows.
            return _("quelle di Windows")
        # Traduttori: area e' una delle tre aree della finestra, come plancia.
        return ", ".join(f"{nome} {caratteri[area]}" if area in caratteri else _("{area} di Windows").format(area=nome) for area, nome in AREE.items())

    def _colori_da_leggere(self, chiave):
        colori = self.impostazioni[chiave]
        if not colori:
            # Traduttori: la voce Colori dei caratteri o Colori dello sfondo, come Colori dello sfondo: quelli di Windows.
            return _("quelli di Windows")
        testo = ", ".join(f"{nome} {'.'.join(str(p) for p in colori[area])}" for area, nome in AREE.items() if area in colori)
        # Traduttori: segue i colori delle aree scelte, come plancia 31.31.31; le altre sono le aree della finestra.
        return testo + (_("; le altre aree di Windows") if len(colori) < len(AREE) else "")

    def _marcatori_da_leggere(self):
        voci = self.marcatori.voci
        quanti = sum(len(voce["marker"]) for voce in voci.values())
        # Traduttori: la voce Marcatori, come Marcatori: 12 in 3 file, oppure nessuno; marker sono i marker, n i file.
        return ngettext("{marker} in {n} file", "{marker} in {n} file", len(voci)).format(marker=quanti, n=len(voci)) if quanti else _("nessuno")

    def _lingua_da_leggere(self):
        """La lingua di adesso e, se nelle impostazioni se n'e' scelta
        un'altra, quella che vale dal riavvio (3.0.0)."""
        if lingua.prossima:
            return _("{adesso}; dal riavvio {prossima}").format(adesso=lingua.nome(lingua.CODICE), prossima=lingua.nome(lingua.prossima))
        return lingua.nome(lingua.CODICE)

    def _scegli_la_lingua(self, genitore):
        """La voce Lingua (3.0.0): una lista delle lingue che hanno un
        catalogo. polipo salva la scelta, che vale dal riavvio: le tabelle
        dei testi si traducono quando i moduli si caricano."""
        codici = lingua.lingue()
        if len(codici) < 2:
            self._riscontro("non_disponibile", _("Per ora MeTeOra parla solo {lingua}: le altre lingue arrivano con le traduzioni, "
                "come spiega il manuale.").format(lingua=lingua.nome(lingua.CODICE)))
            return
        attuale = lingua.prossima or lingua.CODICE
        righe = [_("{nome}, codice {codice}").format(nome=lingua.nome(c), codice=c) for c in codici]
        self._domanda()
        with FinestraScelta(genitore, _("Lingua"), righe, codici.index(attuale) if attuale in codici else 0) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Lingua: non cambiata."))
                return
            scelta = codici[dialogo.GetSelection()]
        lingua.scegli(scelta)
        genitore.aggiorna("lingua", self._riga_dell_impostazione("lingua"))
        if scelta == lingua.CODICE:
            self._riscontro("impostazione_cambiata", _("La lingua resta {lingua}.").format(lingua=lingua.nome(scelta)))
        else:
            self._riscontro("impostazione_cambiata", _("La lingua sarà {lingua} dal prossimo avvio di MeTeOra.").format(lingua=lingua.nome(scelta)))

    def _cambia_impostazione(self, chiave, genitore):
        """Invio su una voce della finestra delle impostazioni, genitore: le
        voci di valore aprono il loro campo, le altre fanno la loro azione."""
        azioni = {
            "scheda_audio": self._scegli_la_scheda_audio,
            "modello_casuale": self._scegli_il_modello_casuale,
            "ripetizione": lambda genitore: self._scegli_da_una_lista(genitore, "ripetizione", valori.RIPETIZIONI, _frase_della_ripetizione),
            "replaygain": self._scegli_il_volume_uniforme,
            "sintesi": self._scegli_la_sintesi,
            "banco_midi": self._scegli_il_banco,
            "salva_console": lambda _genitore: self._salva_console(),
            "marcatori": self._finestra_dei_marcatori,
            "importa_marcatori": self._importa_i_marcatori,
            "dona": self._dona,
            "entra_al_pub": self._entra_al_pub,
            "chiedi_aiuto_al_pub": self._chiedi_aiuto_al_pub,
            "associazioni": self._associa_i_formati,
            "impressi": self._scegli_come_leggere_gli_impressi,
            "destinazione": self._scegli_la_destinazione,
            "karaoke": self._scegli_il_modo_del_karaoke,
            "lingua": self._scegli_la_lingua,
        }
        self._statistiche.impostazione(chiave)
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
                    # Traduttori: etichetta e' la voce delle impostazioni, come Volume della musica, participio come cambiato.
                    self._annullato(_("{etichetta} non {participio}.").format(etichetta=etichetta, participio=participio))
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
        # Le righe col dollaro dei campi: "Adesso" dice il valore di adesso.
        if chiave == "volume":
            return valori.leggi_volume_musica, [
                _("Il volume della musica, da 0 a 300: 100 è il livello originale del file; oltre il 100 amplifica, con un limitatore contro la distorsione, "
                    "per gli audio registrati troppo bassi."),
                _("Per esempio 80 o 150. Anche Ctrl e Maiuscolo con M lo cambiano, dalla finestra principale."),
                # Traduttori: valore e' il valore di adesso della voce, come 80.
                _("Adesso è {valore}.").format(valore=imp["volume"]), REGOLA_DEL_DOLLARO], str(imp["volume"])
        if chiave == "passo_volume":
            return valori.leggi_passo_volume, [
                _("Di quanto cambiano il volume Ctrl e Maiuscolo con M: un numero intero da 1 a 50."),
                _("Per esempio 5. Anche Ctrl e Maiuscolo con il punto lo cambiano, dalla finestra principale."),
                _("Adesso è {valore}.").format(valore=imp["passo_volume"]), REGOLA_DEL_DOLLARO], str(imp["passo_volume"])
        if chiave == "volume_effetti":
            percentuale = round(imp["volume_effetti"] * 100)
            return valori.leggi_volume_effetti, [
                _("Quanto forte suonano gli effetti sonori, in percentuale, da 0 a 100: 0 li zittisce. Il volume della musica non cambia."),
                _("Per esempio 50, oppure 35%."),
                _("Adesso è {percentuale}%.").format(percentuale=percentuale), REGOLA_DEL_DOLLARO], str(percentuale)
        if chiave in ("passo_indietro", "passo_avanti"):
            nome = VOCI_DELLE_IMPOSTAZIONI[chiave][0]
            if chiave == "passo_indietro":
                spiegazione = [_("Di quanti secondi salta indietro Ctrl con Q: almeno 0.1, anche con i decimali."),
                    _("Per esempio 10 o 2.5, oppure minuti e secondi come 1:30. Anche Ctrl con E lo cambia, dalla finestra principale.")]
            else:
                spiegazione = [_("Di quanti secondi salta avanti Maiuscolo con Q: almeno 0.1, anche con i decimali."),
                    _("Per esempio 10 o 2.5, oppure minuti e secondi come 1:30. Anche Maiuscolo con E lo cambia, dalla finestra principale.")]
            attuale = secondi_da_leggere(imp[chiave])
            return (lambda testo: valori.leggi_secondi(testo, nome)), [
                # Traduttori: durata e' come 5 secondi.
                *spiegazione, _("Adesso è di {durata}.").format(durata=valori.scrivi_durata(imp[chiave])), REGOLA_DEL_DOLLARO], attuale
        if chiave == "velocita":
            minima, massima, passo = (valori.scrivi_velocita(v) for v in (valori.VELOCITA_MINIMA, valori.VELOCITA_MASSIMA, valori.PASSO_VELOCITA))
            return valori.leggi_velocita, [
                _("La velocità di riproduzione, da {minima} a {massima}: 1 è la normale, meno di 1 rallenta, più di 1 accelera. Il tono non cambia.").format(
                    minima=minima, massima=massima),
                _("Va a passi di {passo}: un valore fra due passi va al più vicino. Per esempio 1.05 o 0.9.").format(passo=passo),
                _("Anche Ctrl e Maiuscolo con A la cambiano, e premuti insieme la riportano a 1, dalla finestra principale."),
                _("Adesso è {valore}.").format(valore=valori.scrivi_velocita(imp["velocita"])), REGOLA_DEL_DOLLARO], valori.scrivi_velocita(imp["velocita"])
        if chiave == "tono":
            return valori.leggi_tono, [
                _("Il tono in semitoni, da -{massimo} a +{massimo}: 0 è il normale. La velocità non cambia, e l'equalizzatore segue il tono.").format(massimo=valori.TONO_MASSIMO),
                _("Per esempio +2 per alzarlo di due semitoni, -3 per abbassarlo di tre."),
                _("Anche Ctrl e Maiuscolo con F lo cambiano, e premuti insieme lo riportano a 0, dalla finestra principale."),
                # Traduttori: tono e' come +2 semitoni.
                _("Adesso è di {tono}.").format(tono=valori.scrivi_tono(imp["tono"])), REGOLA_DEL_DOLLARO], valori.scrivi_tono(imp["tono"]).split()[0]
        if chiave == "bande":
            frequenze = ", ".join(str(f) for f in valori.FREQUENZE_DELLE_BANDE[:-1])
            return valori.leggi_bande, [
                # Traduttori: frequenze sono quelle delle bande prima dell'ultima, come 60, 150, 400; ultima e' quella dell'ultima banda.
                ngettext("I guadagni della {n} banda dell'equalizzatore, in dB interi da -{massimo} a +{massimo}, "
                    "separati da spazi, dalla banda più bassa alla più alta: {frequenze} e {ultima} Hz.",
                    "I guadagni delle {n} bande dell'equalizzatore, in dB interi da -{massimo} a +{massimo}, "
                    "separati da spazi, dalla banda più bassa alla più alta: {frequenze} e {ultima} Hz.", len(valori.FREQUENZE_DELLE_BANDE)).format(
                    n=len(valori.FREQUENZE_DELLE_BANDE), massimo=valori.GUADAGNO_MASSIMO, frequenze=frequenze, ultima=valori.FREQUENZE_DELLE_BANDE[-1]),
                _("Un numero solo vale per tutte le bande, e il campo vuoto le riporta tutte a 0. Per esempio 0 0 +2 0 0 0 -3, oppure 3."),
                _("Contro la saturazione il volume scende da solo quanto la banda più alzata: con una banda sola il suono non satura, "
                    "con più bande vicine alzate, o tutte, sale fino a circa 5.6 dB oltre, e dal volume 80 o 90 in su conviene abbassare il volume."),
                _("Anche Ctrl e Maiuscolo con U scelgono la banda, Ctrl e Maiuscolo con O la abbassano e la alzano, e premuti insieme la azzerano; "
                    "Ctrl e Maiuscolo con P le azzerano tutte, dalla finestra principale."),
                # Traduttori: valore e' il valore di adesso della voce, come piatto, tutte le bande a 0 dB.
                _("Adesso: {valore}.").format(valore=self._bande_da_leggere()), REGOLA_DEL_DOLLARO], valori.scrivi_bande(imp["bande"])
        if chiave == "dissolvenza":
            secondi = imp["dissolvenza"]["secondi"]
            minima, massima = (valori.scrivi_durata(s).split()[0] for s in (valori.DISSOLVENZA_MINIMA, valori.DISSOLVENZA_MASSIMA))
            return (lambda testo: valori.leggi_dissolvenza(testo, secondi)), [
                _("La dissolvenza incrociata: il brano che finisce sfuma mentre il seguente entra. Vale a ogni cambio di brano, da solo o con i tasti."),
                # Traduttori: no e sì sono le risposte che il campo accetta, come nelle altre voci.
                _("Scrivi no per spegnerla, sì per accenderla, oppure i secondi, da {minima} a {massima}, anche con i decimali, per accenderla con quella durata. "
                    "Per esempio 4 o 2.5.").format(minima=minima, massima=massima),
                _("Anche Maiuscolo con L la accende e Ctrl con L la spegne, e Ctrl e Maiuscolo con K ne cambiano la durata, dalla finestra principale."),
                # Traduttori: valore e' come accesa, 4 secondi, oppure spenta.
                _("Adesso è {valore}.").format(valore=valori.scrivi_dissolvenza(imp["dissolvenza"])), REGOLA_DEL_DOLLARO], valori.scrivi_dissolvenza(imp["dissolvenza"])
        # Le voci sì o no: il campo parte dalla risposta di adesso, una di
        # quelle che valori.leggi_si_no accetta.
        if chiave == "casuale":
            # Traduttori: il nome della voce nei messaggi d'errore del campo, come Riproduzione casuale: manca la risposta.
            return (lambda testo: valori.leggi_si_no(testo, _("Riproduzione casuale"))), [
                _("Con la riproduzione casuale accesa, quando un brano finisce da solo il seguente si sceglie a caso, fra quelli che l'avanzamento automatico "
                    "potrebbe suonare: le voci che si vedono nella plancia, oppure la lista, il loop o la selezione da cui si suona. Z, B e gli altri tasti restano come sono."),
                # Traduttori: sì, no, s, n, 1, 0, acceso e spento sono le risposte che il campo accetta.
                _("Scrivi sì per accenderla, no per spegnerla; valgono anche s, n, 1, 0, acceso e spento. Anche Maiuscolo con N la accende, e Ctrl con N la spegne."),
                _("Adesso è accesa.") if imp["casuale"] else _("Adesso è spenta."), REGOLA_DEL_DOLLARO], _("sì") if imp["casuale"] else _("no")
        if chiave == "video":
            # Traduttori: il nome della voce nei messaggi d'errore del campo, come Video: manca la risposta.
            return (lambda testo: valori.leggi_si_no(testo, _("Video"))), [
                _("Con il video acceso, quando parte un brano con il video si apre la sua finestra, sopra MeTeOra; allo stop sparisce. Spento, dei video si sente solo l'audio."),
                # Traduttori: sì, no, s, n, 1, 0, acceso e spento sono le risposte che il campo accetta.
                _("Scrivi sì per accenderlo, no per spegnerlo; valgono anche s, n, 1, 0, acceso e spento. Anche Maiuscolo con F1 lo accende, e Ctrl con F1 lo spegne."),
                _("Adesso è acceso.") if imp["video"] else _("Adesso è spento."), REGOLA_DEL_DOLLARO], _("sì") if imp["video"] else _("no")
        if chiave == "sottotitoli":
            # Traduttori: il nome della voce nei messaggi d'errore del campo, come Sottotitoli letti: manca la risposta.
            return (lambda testo: valori.leggi_si_no(testo, _("Sottotitoli letti"))), [
                _("Con i sottotitoli letti accesi, ogni sottotitolo dei video va alla sintesi scelta qui sotto e si scrive nella console, anche con il video spento."),
                # Traduttori: sì, no, s, n, 1, 0, acceso e spento sono le risposte che il campo accetta.
                _("Scrivi sì per accenderli, no per spegnerli; valgono anche s, n, 1, 0, acceso e spento. Maiuscolo con D li accende e sceglie la traccia seguente, "
                    "Ctrl con D la precedente."),
                _("Adesso sono accesi.") if imp["sottotitoli"] else _("Adesso sono spenti."), REGOLA_DEL_DOLLARO], _("sì") if imp["sottotitoli"] else _("no")
        if chiave == "barra_dei_comandi":
            # Traduttori: il nome della voce nei messaggi d'errore del campo, come Barra dei comandi per il mouse: manca la risposta.
            return (lambda testo: valori.leggi_si_no(testo, _("Barra dei comandi per il mouse"))), [
                _("Per chi vede: con la barra accesa, quando il mouse si muove sopra MeTeOra compare in basso una barra con i comandi della riproduzione, "
                    "del volume, della velocità e del tono; sparisce dopo qualche secondo di mouse fermo."),
                _("Non prende mai il fuoco e non si raggiunge con Tab: con la tastiera e lo screen reader non cambia niente."),
                # Traduttori: sì, no, s, n, 1, 0, acceso e spento sono le risposte che il campo accetta.
                _("Scrivi sì per accenderla, no per spegnerla; valgono anche s, n, 1, 0, acceso e spento."),
                _("Adesso è accesa.") if imp["barra_dei_comandi"] else _("Adesso è spenta."), REGOLA_DEL_DOLLARO], _("sì") if imp["barra_dei_comandi"] else _("no")
        if chiave == "stato_della_selezione":
            # Traduttori: il nome della voce nei messaggi d'errore del campo, come Stato della selezione per lo screen reader: manca la risposta.
            return (lambda testo: valori.leggi_si_no(testo, _("Stato della selezione per lo screen reader"))), [
                _("Con lo stato acceso, nella plancia NVDA dice non selezionato sulle voci che non sono nella selezione multipla, come in Esplora risorse, "
                    "per esempio quando Ctrl con le frecce porta il fuoco fuori dalla selezione; con Ctrl e la barra spaziatrice dice selezionato o non selezionato."),
                _("Spento, la plancia risponde a NVDA come un albero di Windows, e se una voce è selezionata lo dice solo la console."),
                # Traduttori: sì, no, s, n, 1, 0, acceso e spento sono le risposte che il campo accetta.
                _("Scrivi sì per accenderlo, no per spegnerlo; valgono anche s, n, 1, 0, acceso e spento."),
                _("Adesso è acceso.") if imp["stato_della_selezione"] else _("Adesso è spento."), REGOLA_DEL_DOLLARO], _("sì") if imp["stato_della_selezione"] else _("no")
        if chiave == "insegui":
            # Traduttori: il nome della voce nei messaggi d'errore del campo, come Inseguimento della plancia: manca la risposta.
            return (lambda testo: valori.leggi_si_no(testo, _("Inseguimento della plancia"))), [
                _("Con l'inseguimento agganciato, a ogni cambio di brano la selezione della plancia va da sola su ciò che suona, senza spostare il fuoco."),
                # Traduttori: sì, no, s, n, 1, 0, acceso e spento sono le risposte che il campo accetta.
                _("Scrivi sì per agganciarlo, no per sganciarlo; valgono anche s, n, 1, 0, acceso e spento. Anche Maiuscolo con F8 lo aggancia, e Ctrl con F8 lo sgancia."),
                _("Adesso è agganciato.") if imp["insegui"] else _("Adesso è sganciato."), REGOLA_DEL_DOLLARO], _("sì") if imp["insegui"] else _("no")
        if chiave == "caratteri":
            caratteri = imp["caratteri"]
            di_sistema = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).GetPointSize()
            attuale = " ".join(str(caratteri.get(area, di_sistema)) for area in AREE) if caratteri else ""
            return valori.leggi_caratteri, [
                _("La dimensione dei caratteri in punti, da {minima} a {massima}: tre numeri separati da spazi, per plancia, console e cruscotto.").format(
                    minima=valori.CARATTERI_MINIMI, massima=valori.CARATTERI_MASSIMI),
                ngettext("Un numero solo vale per tutte e tre le aree. Per esempio 12, oppure 12 14 12. Il carattere di Windows è di {n} punto.",
                    "Un numero solo vale per tutte e tre le aree. Per esempio 12, oppure 12 14 12. Il carattere di Windows è di {n} punti.", di_sistema).format(n=di_sistema),
                _("Il campo vuoto torna al carattere di Windows in tutte e tre le aree."),
                # Traduttori: valore e' il valore di adesso della voce, come plancia 12, console di Windows.
                _("Adesso: {valore}.").format(valore=self._caratteri_da_leggere()), REGOLA_DEL_DOLLARO], attuale
        if chiave in ("colori_testo", "colori_sfondo"):
            nome = VOCI_DELLE_IMPOSTAZIONI[chiave][0]
            if chiave == "colori_testo":
                # Traduttori: p, c e t sono le lettere delle aree che il campo accetta.
                spiegazione = [_("Il colore dei caratteri di ogni area: la lettera dell'area, p plancia, c console, t cruscotto, e tre percentuali da 0 a 100 "
                    "di rosso, verde e blu, separate dal punto."), _("Più aree si separano con lo spazio. Per esempio p31.31.31 è un grigio scuro, c100.100.100 il bianco.")]
            else:
                # Traduttori: p, c e t sono le lettere delle aree che il campo accetta.
                spiegazione = [_("Il colore dello sfondo di ogni area: la lettera dell'area, p plancia, c console, t cruscotto, e tre percentuali da 0 a 100 "
                    "di rosso, verde e blu, separate dal punto."), _("Più aree si separano con lo spazio. Per esempio t0.0.0 è il nero, c100.100.80 un giallo chiaro.")]
            return (lambda testo: valori.leggi_colori(testo, nome)), [
                *spiegazione,
                _("La lettera da sola torna ai colori di Windows; le aree che non scrivi restano come sono."),
                # Traduttori: valore e' il valore di adesso della voce, come plancia 31.31.31.
                _("Adesso: {valore}.").format(valore=self._colori_da_leggere(chiave)), REGOLA_DEL_DOLLARO], valori.scrivi_colori(imp[chiave])
        if chiave == "ripresa_oltre":
            return valori.leggi_ripresa_oltre, [
                _("I file più lunghi di tanti minuti, da 0 a {massimo}, riprendono dal punto in cui li hai lasciati: audiolibri, podcast, film.").format(
                    massimo=valori.RIPRESA_MASSIMA),
                _("I file più corti, come le canzoni, ripartono da capo. 0 vuol dire mai. Su un file ripreso, X lo fa ripartire da capo."),
                _("Adesso: {valore}.").format(valore=imp["ripresa_oltre"]), REGOLA_DEL_DOLLARO], str(imp["ripresa_oltre"])
        if chiave == "anticipo_karaoke":
            return valori.leggi_anticipo_del_karaoke, [
                _("Quanti millesimi di secondo prima del canto arriva il testo del karaoke: da 0 a {massimo}.").format(massimo=valori.ANTICIPO_MASSIMO_DEL_KARAOKE),
                _("Per esempio 500, mezzo secondo prima. Vale per i MIDI, i file LRC e i testi nei tag, non per i sottotitoli dei video."),
                _("Adesso: {valore}.").format(valore=imp["anticipo_karaoke"]), REGOLA_DEL_DOLLARO], str(imp["anticipo_karaoke"])
        if chiave == "celle_braille":
            return valori.leggi_celle_braille, [
                _("Quante celle ha la tua barra braille, da 0 a {massimo}: sottotitoli e karaoke arrivano in blocchi lunghi al più così, spezzati fra le parole.").format(
                    massimo=valori.CELLE_MASSIME),
                _("Ogni carattere conta una cella, come nel braille informatico a otto punti: con le tabelle a sei punti, dove maiuscole e numeri prendono più celle, "
                    "scrivi qualche cella in meno."),
                _("Per esempio 40; 0 manda il testo intero, senza dividerlo."),
                _("Adesso: {valore}.").format(valore=imp["celle_braille"]), REGOLA_DEL_DOLLARO], str(imp["celle_braille"])
        if chiave == "lettura_minima":
            return valori.leggi_lettura_minima, [
                _("Per quanti millesimi di secondo resta almeno ogni blocco sulla barra braille: da {minima} a {massima}.").format(
                    minima=valori.LETTURA_MINIMA, massima=valori.LETTURA_MASSIMA),
                _("Per esempio 2000, il valore di partenza. I testi che arrivano prima aspettano il loro turno."),
                _("Adesso: {valore}.").format(valore=imp["lettura_minima"]), REGOLA_DEL_DOLLARO], str(imp["lettura_minima"])
        return valori.leggi_righe_della_console, [
            _("Quante righe tiene la console: da {minimo} in su. Le più vecchie si tolgono dalla cima.").format(minimo=valori.RIGHE_MINIME),
            _("Per esempio 2000, il valore di partenza. Un testo lungo, come le novità di F2, resta comunque intero."),
            ngettext("Adesso ne tiene {n}.", "Adesso ne tiene {n}.", imp["righe_della_console"]).format(n=imp["righe_della_console"]), REGOLA_DEL_DOLLARO], str(imp["righe_della_console"])

    def _applica_l_impostazione(self, chiave, valore):
        """Applica il valore letto dal campo e restituisce la frase che lo dice."""
        imp = self.impostazioni
        if chiave in ("colori_testo", "colori_sfondo"):
            # Dal campo dei colori arrivano i cambi, da unire a quelli di adesso.
            valore = valori.unisci_colori(imp[chiave], valore)
        imp[chiave] = valore
        if chiave == "volume":
            self.motore.volume = valore
            if valore > 100:
                return _("Il volume della musica ora è {volume}, amplificato oltre il 100.").format(volume=valore)
            return _("Il volume della musica ora è {volume}.").format(volume=valore)
        if chiave == "passo_volume":
            return _("Ctrl e Maiuscolo con M ora cambiano il volume di {passo}.").format(passo=valore)
        if chiave == "volume_effetti":
            return _("Gli effetti sonori ora suonano al {percentuale}%.").format(percentuale=round(valore * 100)) if valore else _("Gli effetti sonori ora tacciono.")
        if chiave in ("passo_indietro", "passo_avanti"):
            if chiave == "passo_indietro":
                return _("Il salto indietro ora è di {durata}.").format(durata=valori.scrivi_durata(valore))
            return _("Il salto avanti ora è di {durata}.").format(durata=valori.scrivi_durata(valore))
        if chiave == "velocita":
            self.motore.velocita = valore
            if valore == 1:
                return _("La velocità ora è {velocita}, la normale.").format(velocita=valori.scrivi_velocita(valore))
            return _("La velocità ora è {velocita}.").format(velocita=valori.scrivi_velocita(valore))
        if chiave == "tono":
            self.motore.tono = valore
            if valore == 0:
                return _("Il tono ora è di {tono}, il normale.").format(tono=valori.scrivi_tono(valore))
            return _("Il tono ora è di {tono}.").format(tono=valori.scrivi_tono(valore))
        if chiave == "bande":
            self.motore.bande = valore
            return _("L'equalizzatore ora è {bande}.").format(bande=self._bande_da_leggere())
        if chiave == "dissolvenza":
            self._applica_la_dissolvenza()
            return _("La dissolvenza ora è {dissolvenza}.").format(dissolvenza=valori.scrivi_dissolvenza(valore))
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
            return _("Sottotitoli letti accesi.") if valore else _("Sottotitoli letti spenti.")
        if chiave == "barra_dei_comandi":
            self.barra.accendi(valore)
            # Quella del video guarda il mouse solo a video aperto.
            if self._video is not None and (not valore or self._video.IsShown()):
                self._video.barra.accendi(valore)
            if valore:
                return _("Barra dei comandi per il mouse accesa: compare quando il mouse si muove sopra MeTeOra.")
            return _("Barra dei comandi per il mouse spenta.")
        if chiave == "stato_della_selezione":
            if valore:
                self._attacca_lo_stato_della_selezione()
                return _("Stato della selezione per lo screen reader acceso: nella plancia NVDA dice non selezionato sulle voci fuori dalla selezione.")
            return _("Stato della selezione per lo screen reader spento: la plancia risponde a NVDA come un albero di Windows.")
        if chiave == "insegui":
            if not valore:
                return _("Inseguimento sganciato: la selezione resta dove la lasci.")
            if self.motore.in_corso:
                self._insegui()
            return _("Inseguimento agganciato: la selezione della plancia segue il brano che suona.")
        if chiave in ("celle_braille", "lettura_minima"):
            # I blocchi in fila erano fatti con i valori di prima.
            self._testo_superato()
        if chiave == "celle_braille":
            if valore:
                return plurale(valore, "Sottotitoli e karaoke ora arrivano al braille in blocchi di {n} celle al più.",
                    "Sottotitoli e karaoke ora arrivano al braille in blocchi di {n} celle al più.")
            return _("Sottotitoli e karaoke ora arrivano al braille interi.")
        if chiave == "lettura_minima":
            return plurale(valore, "Ogni blocco ora resta sulla barra braille almeno {n} millesimo.", "Ogni blocco ora resta sulla barra braille almeno {n} millesimi.")
        if chiave == "ripresa_oltre":
            if valore:
                return plurale(valore, "I file più lunghi di {n} minuti ora riprendono dal punto lasciato.", "I file più lunghi di {n} minuti ora riprendono dal punto lasciato.")
            return _("I file ora ripartono sempre da capo.")
        if chiave == "anticipo_karaoke":
            self._applica_il_karaoke()
            if valore:
                return plurale(valore, "Il testo del karaoke ora arriva {n} millesimi prima del canto.", "Il testo del karaoke ora arriva {n} millesimi prima del canto.")
            return _("Il testo del karaoke ora arriva quando comincia il canto.")
        if chiave == "righe_della_console":
            # Il taglio e' subito, senza il margine che scrivi lascia.
            posizione = self.console.GetInsertionPoint()
            self.console.SetInsertionPoint(max(0, posizione - self._taglia_la_console(valore)))
            return plurale(valore, "La console ora tiene {n} riga.", "La console ora tiene {n} righe.")
        self._applica_aspetto()
        if chiave == "caratteri":
            return _("Dimensioni dei caratteri: {caratteri}.").format(caratteri=self._caratteri_da_leggere())
        # Traduttori: voce e' il nome dell'impostazione, come Colori del testo; colori quelli di ogni area.
        return _("{voce}: {colori}.").format(voce=VOCI_DELLE_IMPOSTAZIONI[chiave][0], colori=self._colori_da_leggere(chiave))

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
        scelta = self._scelta_del_pc()
        speaker = self._speaker_scelto()
        if speaker is not None:
            # Si suona sul PC finche' lo speaker non compare (1.119.0).
            self._speaker_atteso = speaker["cast"]
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
        # Traduttori: la scheda audio scelta da sola; fra parentesi il suo nome.
        return _("Automatica ({scheda})").format(scheda=nome) if nome else _("Automatica")

    def _scheda_da_leggere(self):
        speaker = self._speaker_scelto()
        if speaker is not None:
            lettore = self.motore.lontano
            if lettore is not None:
                return _("{nome}, speaker Cast").format(nome=lettore.nome)
            return _("{nome}, speaker Cast, non c'è: uso il PC").format(nome=speaker["nome"])
        scelta = self.impostazioni["scheda_audio"]
        if scelta:
            nome = self._nome_della_scheda(scelta["dispositivo"], scelta["interfaccia"])
            # Traduttori: motivo e' perche' la scheda scelta non si usa: non c'è, oppure non si apre.
            return _("{scheda}, {motivo}: uso quella automatica").format(scheda=nome, motivo=self._scheda_in_disparte) if self._scheda_in_disparte else nome
        # Con la scelta automatica, la scheda che il mixer usa gia', senza
        # aprire niente per provarla.
        uscita = None
        with contextlib.suppress(Exception):
            uscita = schede_audio.in_uso()
        if uscita:
            # Traduttori: la scheda audio scelta da sola; fra parentesi il suo nome.
            return _("Automatica ({scheda})").format(scheda=self._nome_della_scheda(uscita["dispositivo"], uscita["interfaccia"]))
        return _("Automatica")

    def _scrivi_la_scheda_all_avvio(self, esito, errore):
        scelta = self._scelta_del_pc()
        if self._scheda_in_disparte == SCHEDA_CHE_NON_SI_APRE:
            # Con il suono dell'errore: senza, gli effetti tacerebbero per
            # tutta la sessione senza dire perche'.
            if errore is not None:
                self._avviso_all_avvio("errore", _("La scheda audio scelta, {scheda}, non si apre, e non riesco a usare quella automatica: {errore}.").format(
                    scheda=scelta["dispositivo"], errore=errore))
            else:
                self._avviso_all_avvio("errore", _("La scheda audio scelta, {scheda}, non si apre: uso quella automatica.").format(scheda=scelta["dispositivo"]))
        elif errore is not None:
            # Traduttori: scheda e' il nome della scheda audio scelta, oppure la parola automatica.
            self._avviso_all_avvio("errore", _("Non riesco a usare la scheda audio scelta, {scheda}: {errore}.").format(
                scheda=scelta.get("dispositivo", _("automatica")), errore=errore))
        elif esito["mancante"]:
            # Traduttori: dove e' vuoto, oppure una virgola e il nome della scheda automatica.
            self._avviso_all_avvio("errore", _("La scheda audio scelta, {scheda}, non c'è: uso quella automatica{dove}.").format(
                scheda=scelta["dispositivo"], dove=self._dove_suona(esito)))
        elif not esito["musica"]:
            self._avviso_all_avvio("errore", _("La musica non ritrova la scheda audio {scheda} e suona sulla scheda di Windows.").format(scheda=esito["dispositivo"]))

    # Le schede che arrivano e se ne vanno (1.116.0): cuffie Bluetooth
    # connesse, spente o uscite di portata, schede USB inserite e tolte.

    def _uscite_cambiate(self):
        """mpv dice che le sue uscite audio sono cambiate: si rileggono dopo
        ATTESA_DELLE_USCITE dall'ultimo avviso."""
        if self._chiusa:
            return
        if self._attesa_delle_uscite is not None:
            self._attesa_delle_uscite.Stop()
        self._attesa_delle_uscite = wx.CallLater(ATTESA_DELLE_USCITE, self._rileggi_le_uscite)

    def _uscita_persa_dal_motore(self, percorso, sottobrano):
        """Il brano si e' fermato perche' mpv non apre piu' la sua uscita: di
        solito la scheda scelta se n'e' andata, come delle cuffie Bluetooth
        spente, e mpv, provato, chiude il brano e non lo riprende neanche con
        un'uscita buona. La musica passa subito alla scheda di Windows e il
        brano riparte dal punto annotato, al piu' un secondo prima, anche in
        pausa se era in pausa; poi le schede si rileggono come a ogni cambio,
        e la console lo dice. Se gia' suonava sulla scheda di Windows, e'
        un errore come gli altri."""
        if self._chiusa:
            return
        if self.motore.dispositivo == schede_audio.AUTOMATICA_MPV:
            self._brano_in_errore(percorso)
            return
        self._uscente = self._preparato = None
        self._uscita_persa = True
        self._statistiche.conta("brani_ripresi_dopo_l_uscita_persa")
        self.motore.dispositivo = schede_audio.AUTOMATICA_MPV
        punto = self._punto_di_ripresa
        inizio = punto[2] if punto and punto[:2] == (percorso, sottobrano) else None
        self.motore.suona(percorso, sottobrano, inizio=inizio, in_pausa=self.motore.in_pausa)
        self._uscite_cambiate()

    def _rileggi_le_uscite(self):
        """Le uscite audio sono cambiate. PortAudio si rilegge, perche' da
        solo non vede le schede arrivate dopo l'avvio, e la scelta si applica
        di nuovo. Una scheda scelta che se ne va lascia il posto
        all'automatica, come all'avvio, e la scelta salvata resta: quando
        torna, musica ed effetti ci rientrano da soli. Una scheda che c'e' ma
        non si apre, per gli effetti o per la musica, resta da parte fino al
        prossimo cambio, cosi' non si riprova senza fine. Con l'automatica gli
        effetti seguono la scheda di Windows, come la musica gia' fa da se'.
        La console parla solo quando cambia la scheda su cui si suona."""
        self._attesa_delle_uscite = None
        if self._chiusa:
            return
        scelta = self._scelta_del_pc()
        uscita_persa, self._uscita_persa = self._uscita_persa, False
        prima = None
        with contextlib.suppress(Exception):
            prima = schede_audio.in_uso()
        try:
            schede_audio.rileggi()
        except Exception as e:  # noqa: BLE001 - PortAudio fallisce in molti modi, e lo dice la console
            self._avviso_delle_uscite("errore", _("Le schede audio sono cambiate, ma non riesco a rileggerle: {errore}.").format(errore=e))
            return
        in_disparte = self._scheda_in_disparte
        esito, errore = self._applica_la_scheda(scelta)
        evento = testo = None
        if errore is None and scelta and not esito["mancante"] and (uscita_persa or not self._effetti_si_aprono()):
            self._scheda_in_disparte = SCHEDA_CHE_NON_SI_APRE
            esito, errore = self._applica_la_scheda({})
            if in_disparte != SCHEDA_CHE_NON_SI_APRE:
                # Traduttori: dove e' vuoto, oppure una virgola e il nome della scheda automatica.
                evento, testo = "errore", _("La scheda audio scelta, {scheda}, non si apre: uso quella automatica{dove}.").format(
                    scheda=scelta["dispositivo"], dove=self._dove_suona(esito))
        elif errore is None and scelta and esito["mancante"]:
            self._scheda_in_disparte = SCHEDA_MANCANTE
            if in_disparte != SCHEDA_MANCANTE:
                # Traduttori: dove e' vuoto, oppure una virgola e il nome della scheda automatica.
                evento, testo = "scheda_sparita", _("La scheda audio scelta, {scheda}, non c'è più: uso quella automatica{dove}.").format(
                    scheda=scelta["dispositivo"], dove=self._dove_suona(esito))
        elif errore is None and scelta:
            self._scheda_in_disparte = None
            if in_disparte is not None:
                evento = "scheda_tornata"
                if esito["musica"]:
                    testo = _("La scheda audio scelta, {scheda}, è tornata: musica ed effetti suonano di nuovo lì.").format(scheda=scelta["dispositivo"])
                else:
                    testo = _("La scheda audio scelta, {scheda}, è tornata per gli effetti; la musica non la ritrova e resta sulla scheda di Windows.").format(
                        scheda=scelta["dispositivo"])
        if errore is not None:
            # Traduttori: scheda e' il nome della scheda audio scelta, oppure la parola automatica.
            self._avviso_delle_uscite("errore", _("Le schede audio sono cambiate, e non riesco a usare la scheda {scheda}: {errore}.").format(
                scheda=scelta.get("dispositivo", _("automatica")), errore=errore))
            return
        automatica = not scelta or self._scheda_in_disparte is not None
        cambiata = prima is not None and esito["dispositivo"] and (prima["dispositivo"], prima["interfaccia"]) != (esito["dispositivo"], esito["interfaccia"])
        if testo is None and automatica and cambiata:
            evento, testo = "scheda_di_windows", _("La scheda audio di Windows ora è {scheda}: musica ed effetti suonano lì.").format(
                scheda=self._nome_della_scheda(esito["dispositivo"], esito["interfaccia"]))
        self._aggiorna_la_scheda_delle_statistiche()
        if evento == "scheda_sparita":
            self._comincia_l_assenza()
        elif evento == "scheda_tornata":
            self._finisce_l_assenza()
        if testo:
            self._avviso_delle_uscite(evento, testo)

    def _comincia_l_assenza(self):
        """La scelta, scheda o speaker, se n'e' andata: per il primato delle
        statistiche, da quando (issue 31)."""
        if self._assenza_dal is None:
            self._assenza_dal = (time.monotonic(), datetime.datetime.now().isoformat(timespec="seconds"))

    def _finisce_l_assenza(self):
        """La scelta e' tornata: l'assenza conta per il primato."""
        if self._assenza_dal is not None:
            inizio, quando = self._assenza_dal
            self._assenza_dal = None
            self._statistiche.assenza_della_scelta(time.monotonic() - inizio, quando)

    def _dove_suona(self, esito):
        """La coda ", scheda, interfaccia" con l'automatica scelta da applica,
        o niente se non si sa."""
        return f", {self._nome_della_scheda(esito['dispositivo'], esito['interfaccia'])}" if esito and esito["dispositivo"] else ""

    def _avviso_delle_uscite(self, evento, testo):
        """La riga subito, il suono dopo l'ultimo effetto, senza toccare la
        domanda in corso: il cambio arriva da fuori, anche mentre si scrive in
        un campo."""
        self.scrivi(testo)
        self._dopo_il_suono(self._suono, evento)

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
        # Traduttori: il titolo della finestra del video; nome e' quello del file.
        titolo = _("{nome}, video, MeTeOra").format(nome=os.path.basename(self.motore.in_corso or ""))
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
        self._riscontro("video_nascosto", _("Video nascosto per questo brano: il prossimo video si apre da sé."))

    def _salta_dalla_barra(self, secondi):
        """La linea del tempo della barra sopra il video, per chi vede: il
        salto ha il riscontro di W."""
        self.motore.vai_a(secondi)
        durata = self.motore.durata
        if durata is not None:
            self._riscontro("vai_a_tempo", _("Vado a {tempo} di {durata}.").format(tempo=tempo(secondi), durata=tempo(durata)))
        else:
            self._riscontro("vai_a_tempo", _("Vado a {tempo}.").format(tempo=tempo(secondi)))

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
        self._statistiche.conta("righe_dei_sottotitoli")
        if self._lettura is not None:
            self._statistiche.conta("righe_riconosciute")
        elif formati.e_midi(self.motore.in_corso or ""):
            self._statistiche.conta("righe_del_karaoke")
        self._ai_testi_letti(testo, self.motore.resto_del_sottotitolo)
        self.scrivi(testo)

    def _ai_testi_letti(self, testo, resto=None, interrompi=False):
        """Il testo alla sintesi e al braille scelti per sottotitoli e karaoke,
        come dice la voce Dove vanno sottotitoli e karaoke: alla voce intero,
        al braille in fila, a blocchi lunghi quanto la barra. resto, se c'e',
        da' i secondi che restano al testo, da dividere fra i blocchi; senza,
        ogni blocco resta il tempo minimo di lettura. interrompi fa lasciare
        alla voce quello che sta dicendo: lo vuole Dove sono, non i
        sottotitoli e il karaoke, che si dicono uno dopo l'altro. Lo usano i
        sottotitoli e Dove sono (tappa 14 b). Torna il numero del testo nella
        coda del braille, o None se al braille non va."""
        imp = self.impostazioni
        if imp["destinazione"] in ("entrambi", "sintesi"):
            self._sintesi.dici(testo, imp["sintesi"], "sintesi", interrompi=interrompi)
        if imp["destinazione"] in ("entrambi", "braille"):
            return self._braille.aggiungi(testo, imp["celle_braille"], imp["lettura_minima"] / 1000, resto() if resto else None)
        return None

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

    def _metti_il_video(self, acceso):
        """Ctrl con F1 spegne il video, Maiuscolo con F1 lo accende (2.0.2,
        prima a giro); a video acceso, Maiuscolo con F1 riapre la finestra
        nascosta con Esc per il brano in corso."""
        evento = "video_acceso" if acceso else "video_spento"
        nascosto = acceso and self._video_nascosto_per is not None and self._video_nascosto_per == self.motore.in_corso
        if self.impostazioni["video"] == acceso and not nascosto:
            self._riscontro(evento, _("Già così. {frase}").format(frase=_frase_del_video(acceso)))
            return
        self.impostazioni["video"] = acceso
        self._video_nascosto_per = None
        self._salva_impostazioni()
        if not acceso:
            self._spegni_il_video()
        self._riscontro(evento, _frase_del_video(acceso))
        self._aggiorna_il_video()

    def _posti_dei_sottotitoli(self):
        """Le scelte fra cui si muove D (issue 38, al posto del giro di
        Maiuscolo con F2): spenti, poi le tracce dei sottotitoli, poi sui
        video i sottotitoli impressi (1.80.0), se c'e' il file della passata
        o si possono leggere; la traccia del file di una passata non e' una
        scelta a se', e' quella degli impressi. Su un brano senza
        sottotitoli, e senza impressi, o da fermi: spenti e accesi per i
        brani dopo. Torna (tracce, passata, sottotitoli, con_gli_impressi,
        attuale, quante), con attuale contato da zero."""
        tracce = self.motore.tracce() if self.motore.in_corso else None
        passata = _traccia_della_passata(tracce)
        sottotitoli = [t for t in (tracce["sub"] if tracce else []) if t is not passata]
        con_gli_impressi = bool(tracce and tracce["video"] and (passata is not None or ocr.disponibile()))
        if not sottotitoli and not con_gli_impressi:
            return tracce, passata, sottotitoli, False, 1 if self.impostazioni["sottotitoli"] else 0, 2
        quante = 1 + len(sottotitoli) + con_gli_impressi
        if con_gli_impressi and ((passata is not None and passata.get("selected")) or (self.impostazioni["impressi_scelti"]
                and self.impostazioni["sottotitoli"] and not any(t.get("selected") for t in sottotitoli))):
            attuale = quante - 1
        else:
            scelta = next((i for i, t in enumerate(sottotitoli) if t.get("selected")), None)
            attuale = 0 if scelta is None or not self.impostazioni["sottotitoli"] else scelta + 1
        return tracce, passata, sottotitoli, con_gli_impressi, attuale, quante

    def _frase_dei_sottotitoli(self, tracce, sottotitoli, con_gli_impressi, attuale, quante):
        """La scelta dei sottotitoli, fra quante, da dire."""
        if not sottotitoli and not con_gli_impressi:
            if attuale:
                return _("Sottotitoli letti accesi; questo brano non ne ha.") if tracce else _("Sottotitoli letti accesi; valgono per i brani che ne hanno.")
            return _("Sottotitoli letti spenti; questo brano non ne ha.") if tracce else _("Sottotitoli letti spenti; valgono per i brani che ne hanno.")
        if attuale == 0:
            stato = _("Sottotitoli letti spenti")
        elif attuale <= len(sottotitoli):
            stato = _("Sottotitoli letti, traccia {traccia}").format(traccia=_descrivi_traccia(sottotitoli[attuale - 1], attuale - 1, len(sottotitoli)))
        else:
            stato = _("Sottotitoli impressi")
        if sottotitoli and con_gli_impressi:
            # Traduttori: tracce e' il numero delle tracce dei sottotitoli, come 2 tracce.
            offerta = _("{tracce} e gli impressi").format(tracce=plurale(len(sottotitoli), "{n} traccia", "{n} tracce"))
        elif sottotitoli:
            offerta = plurale(len(sottotitoli), "{n} traccia", "{n} tracce")
        else:
            offerta = _("gli impressi")
        # Traduttori: stato e' la scelta di adesso, come Sottotitoli impressi; offerta quelle oltre a spenti, come 2 tracce e gli impressi.
        return _("{stato}; scelta {numero} di {quante}: spenti, {offerta}.").format(stato=stato, numero=attuale + 1, quante=quante, offerta=offerta)

    def _comando_sottotitoli(self):
        """D (issue 38): i sottotitoli letti, la scelta fra quante."""
        tracce, _passata, sottotitoli, con_gli_impressi, attuale, quante = self._posti_dei_sottotitoli()
        self._riporta(self._frase_dei_sottotitoli(tracce, sottotitoli, con_gli_impressi, attuale, quante), "sottotitoli")

    def _comando_sottotitoli_precedenti(self):
        self._vai_ai_sottotitoli(lambda attuale, _quante: attuale - 1, -1)

    def _comando_sottotitoli_successivi(self):
        self._vai_ai_sottotitoli(lambda attuale, _quante: attuale + 1, 1)

    def _comando_ultimi_sottotitoli(self):
        self._vai_ai_sottotitoli(lambda _attuale, quante: quante - 1, 1)

    def _comando_sottotitoli_spenti(self):
        self._vai_ai_sottotitoli(lambda _attuale, _quante: 0, -1)

    def _vai_ai_sottotitoli(self, scelta, verso):
        """Ctrl e Maiuscolo con D la scelta prima e dopo, Alt con D l'ultima,
        Ctrl e Alt con D spenti: scelta(attuale, quante) da' la nuova, che si
        ferma alla prima e all'ultima. Su un brano senza sottotitoli, e
        senza impressi da leggere, li accende o li spegne per i brani dopo."""
        tracce, passata, sottotitoli, con_gli_impressi, attuale, quante = self._posti_dei_sottotitoli()
        indice = max(0, min(quante - 1, scelta(attuale, quante)))
        if indice == attuale:
            frase = self._frase_dei_sottotitoli(tracce, sottotitoli, con_gli_impressi, attuale, quante)
            if indice == 0:
                frase = _("È già la prima scelta. {frase}").format(frase=frase)
            elif indice == quante - 1:
                frase = _("È già l'ultima scelta. {frase}").format(frase=frase)
            else:
                frase = _("È già questa scelta. {frase}").format(frase=frase)
            self._riscontro("nessun_altro_brano", frase, "sottotitoli")
            return
        if not sottotitoli and not con_gli_impressi:
            acceso = indice == 1
            self.impostazioni["impressi_scelti"] = False
            frase = (_("Sottotitoli letti accesi; questo brano non ne ha.") if tracce else _("Sottotitoli letti accesi.")) if acceso else _("Sottotitoli letti spenti.")
        elif indice == 0:
            acceso, frase = False, _("Sottotitoli letti spenti.")
            self.impostazioni["impressi_scelti"] = False
            self.motore.scegli_traccia("sid", "no")
        elif indice <= len(sottotitoli):
            acceso, frase = True, self._scegli_i_sottotitoli(tracce, sottotitoli[indice - 1], indice - 1, len(sottotitoli))
        else:
            acceso, frase = True, self._scegli_gli_impressi(tracce, passata)
        self.impostazioni["sottotitoli"] = acceso
        self._salva_impostazioni()
        self._riscontro("sottotitoli_accesi" if acceso else "sottotitoli_spenti", frase, "sottotitoli")
        if not acceso:
            self._braille.svuota()
            self._aggiorna_la_lettura(tracce, scelta=None)

    def _scegli_i_sottotitoli(self, tracce, traccia, indice, quante):
        """Una traccia di sottotitoli, scelta con D; se e' fatta
        di immagini, la legge il riconoscimento dei caratteri."""
        self.impostazioni["impressi_scelti"] = False
        self.impostazioni["sottotitoli"] = True
        self._testo_superato()
        self.motore.scegli_traccia("sid", str(traccia["id"]))
        titolo = traccia.get("title") or ""
        if titolo.startswith(karaoke.TITOLO):
            # Il testo del karaoke dice da dove viene, non il formato (1.82.0).
            origine = titolo[len(karaoke.TITOLO):].lstrip(", ")
            if quante > 1:
                # Traduttori: origine e' da dove viene il testo, come dal MIDI o dal file LRC.
                frase = _("Testo del karaoke letto, traccia {numero} di {quante}, {origine}.").format(numero=indice + 1, quante=quante, origine=origine)
            else:
                # Traduttori: origine e' da dove viene il testo, come dal MIDI o dal file LRC.
                frase = _("Testo del karaoke letto, {origine}.").format(origine=origine)
            self._aggiorna_la_lettura(tracce, scelta=traccia)
            return frase
        frase = _("Sottotitoli letti, traccia {traccia}.").format(traccia=_descrivi_traccia(traccia, indice, quante))
        if traccia.get("codec") in sottotitoli_ocr.CODEC_A_IMMAGINI:
            if ocr.disponibile():
                frase += " " + _("È fatta di immagini: la legge il riconoscimento dei caratteri di Windows.")
            else:
                frase += " " + _("È fatta di immagini, e il riconoscimento dei caratteri di Windows non c'è: non si può leggere.")
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
            return _("Sottotitoli impressi, dal file della passata fatta prima.")
        self.motore.scegli_traccia("sid", "no")
        self._aggiorna_la_lettura(tracce, scelta=None)
        video = self.motore.in_corso
        if self.impostazioni["impressi"] != "passata":
            return _("Sottotitoli impressi, letti al volo.")
        if self._passata is not None and self._passata.video == video:
            return _("Sottotitoli impressi, letti al volo: la passata è già in corso.")
        if video in self._passate_vuote:
            return _("Sottotitoli impressi, letti al volo: la passata di prima non ne ha trovati in questo video.")
        self._avvia_la_passata(video)
        return _("Sottotitoli impressi, letti al volo mentre la passata li prepara per le volte dopo.")

    def _sottotitolo_a_immagini(self):
        """Dal filo del motore: comincia un sottotitolo. La lettura delle
        tracce a immagini, se c'e', lo fotografa e lo legge."""
        lettura = getattr(self, "_lettura", None)
        if lettura is not None and lettura.tipo == "immagini":
            lettura.nuovo_sottotitolo()

    def _aggiorna_la_lettura(self, tracce, scelta=_DALLE_TRACCE):
        """La lettura dei sottotitoli fatti di immagini che serve adesso: le
        tracce a immagini, se ne e' scelta una; quelli impressi, se li ha
        scelti con D e non c'e' una traccia; nessuna altrimenti, o
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
            self.scrivi(_("La passata dei sottotitoli impressi di {prima} si ferma: ne parte una per {video}.").format(
                prima=os.path.basename(self._passata.video), video=os.path.basename(video)))
        self._passata = sottotitoli_ocr.PassataDegliImpressi(video, ocr.lingua_per(None),
            lambda percentuale: wx.CallAfter(self._passata_avanza, video, percentuale),
            lambda esito: wx.CallAfter(self._passata_finita, video, esito)).avvia()
        durata = self.motore.durata or 0
        minuti = max(1, round(durata / sottotitoli_ocr.VELOCITA_DELLA_PASSATA / 60))
        nome = os.path.basename(video)
        if durata:
            frase = ngettext("Comincia la passata dei sottotitoli impressi di {nome}: ci vogliono circa {n} minuto; intanto li leggo al volo.",
                "Comincia la passata dei sottotitoli impressi di {nome}: ci vogliono circa {n} minuti; intanto li leggo al volo.", minuti).format(nome=nome, n=minuti)
        else:
            frase = _("Comincia la passata dei sottotitoli impressi di {nome}; intanto li leggo al volo.").format(nome=nome)
        self._riscontro("passata_avviata", frase)

    def _passata_avanza(self, video, percentuale):
        if self._chiusa or self._passata is None or self._passata.video != video or not 0 < percentuale < 100:
            return
        self.scrivi(_("Passata dei sottotitoli impressi di {nome}: {percentuale}%.").format(nome=os.path.basename(video), percentuale=percentuale), categoria="passata")

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
            self._riscontro("passata_finita", _("La passata non ha trovato sottotitoli impressi in {nome}.").format(nome=nome))
            return
        if not os.path.isfile(esito):
            self._riscontro("errore", esito)
            return
        sceglierla = self.motore.in_corso == video and self.impostazioni["sottotitoli"] and self.impostazioni["impressi_scelti"]
        if self.motore.in_corso == video:
            self.motore.aggiungi_sottotitoli(esito, TITOLO_DELLA_PASSATA, lingua.split("-")[0], scegli=sceglierla)
        if sceglierla:
            self._aggiorna_la_lettura(self.motore.tracce(), scelta={"codec": "subrip", "title": TITOLO_DELLA_PASSATA})
            self._riscontro("passata_finita", _("Sottotitoli impressi pronti nel file {file}, accanto al video: da ora si leggono da lì.").format(file=os.path.basename(esito)))
        else:
            self._riscontro("passata_finita", _("Sottotitoli impressi pronti nel file {file}, accanto al video: Alt con D li sceglie, anche le volte dopo.").format(
                file=os.path.basename(esito)))

    def _comando_traccia_audio(self):
        """G (issue 38): la traccia audio del brano, fra quante."""
        if self._niente_in_corso(risveglia=True):
            return
        tracce = self.motore.tracce()
        audio = tracce["audio"] if tracce else []
        if not audio:
            self._riporta(_("Questo brano non ha tracce audio da scegliere."), "traccia_audio")
            return
        scelta = next((i for i, t in enumerate(audio) if t.get("selected")), 0)
        self._riporta(_("Traccia audio {traccia}.").format(traccia=_descrivi_traccia(audio[scelta], scelta, len(audio))), "traccia_audio")

    def _comando_traccia_audio_precedente(self):
        self._scegli_la_traccia_audio(lambda attuale, _quante: attuale - 1, -1)

    def _comando_traccia_audio_successiva(self):
        self._scegli_la_traccia_audio(lambda attuale, _quante: attuale + 1, 1)

    def _comando_ultima_traccia_audio(self):
        self._scegli_la_traccia_audio(lambda _attuale, quante: quante - 1, 1)

    def _comando_prima_traccia_audio(self):
        self._scegli_la_traccia_audio(lambda _attuale, _quante: 0, -1)

    def _scegli_la_traccia_audio(self, scelta, verso):
        """Ctrl e Maiuscolo con G la traccia audio prima e dopo, Alt con G
        l'ultima, Ctrl e Alt con G la prima, senza giro (issue 38): scelta(attuale,
        quante) da' la nuova, che si ferma alla prima e all'ultima."""
        if self._niente_in_corso(risveglia=True):
            return
        tracce = self.motore.tracce()
        audio = tracce["audio"] if tracce else []
        if len(audio) < 2:
            self._riscontro("non_disponibile", _("Questo brano ha una traccia audio sola.") if audio else _("Questo brano non ha tracce audio da scegliere."))
            return
        attuale = next((i for i, t in enumerate(audio) if t.get("selected")), 0)
        indice = max(0, min(len(audio) - 1, scelta(attuale, len(audio))))
        if indice == attuale:
            traccia = _descrivi_traccia(audio[indice], indice, len(audio))
            if verso < 0:
                frase = _("È già la prima traccia audio: {traccia}.").format(traccia=traccia)
            else:
                frase = _("È già l'ultima traccia audio: {traccia}.").format(traccia=traccia)
            self._riscontro("nessun_altro_brano", frase, "traccia_audio")
            return
        self.motore.scegli_traccia("aid", str(audio[indice]["id"]))
        self._riscontro("traccia_audio", _("Traccia audio {traccia}.").format(traccia=_descrivi_traccia(audio[indice], indice, len(audio))), "traccia_audio")

    def _metti_lo_schermo_intero(self, intero):
        """Maiuscolo con F5 mette la finestra del video a schermo intero, Ctrl
        con F5 la riporta in finestra, come Esc (2.0.2, prima a giro)."""
        if self._video is None or not self._video.IsShown():
            self._riscontro("non_disponibile", _("La finestra del video non è aperta."))
            return
        evento, frase = ("schermo_intero", _("Video a schermo intero.")) if intero else ("schermo_in_finestra", _("Video in finestra."))
        if self._video.IsFullScreen() == intero:
            self._riscontro(evento, _("Già così. {frase}").format(frase=frase))
            return
        self._video.schermo_intero(intero)
        self._riscontro(evento, frase)

    def _comando_rapporto(self):
        """I (issue 38): il rapporto dell'immagine, fra quanti."""
        self._riporta(self._frase_del_rapporto(), "rapporto")

    def _frase_del_rapporto(self):
        # Traduttori: rapporto e' il nome del rapporto, come 16:9 o quello del video.
        return _("Rapporto dell'immagine: {rapporto}, {numero} di {quanti}.").format(rapporto=RAPPORTI[self._rapporto][1], numero=self._rapporto + 1,
            quanti=len(RAPPORTI))

    def _comando_rapporto_precedente(self):
        self._scegli_il_rapporto(self._rapporto - 1, -1)

    def _comando_rapporto_successivo(self):
        self._scegli_il_rapporto(self._rapporto + 1, 1)

    def _comando_rapporto_del_video(self):
        self._scegli_il_rapporto(0, 0)

    def _comando_ultimo_rapporto(self):
        self._scegli_il_rapporto(len(RAPPORTI) - 1, 1)

    def _comando_primo_rapporto(self):
        self._scegli_il_rapporto(0, -1)

    def _scegli_il_rapporto(self, indice, verso):
        """Il rapporto dell'immagine, senza giro (issue 38): si ferma al primo,
        quello del video, e all'ultimo."""
        indice = max(0, min(len(RAPPORTI) - 1, indice))
        if indice == self._rapporto:
            if verso < 0:
                frase = _("È già il primo. {frase}").format(frase=self._frase_del_rapporto())
            elif verso > 0:
                frase = _("È già l'ultimo. {frase}").format(frase=self._frase_del_rapporto())
            else:
                frase = _("È già questo. {frase}").format(frase=self._frase_del_rapporto())
            self._riscontro("nessun_altro_brano", frase, "rapporto")
            return
        self._rapporto = indice
        self.motore.rapporto(RAPPORTI[indice][0])
        self._riscontro("rapporto", self._frase_del_rapporto(), "rapporto")

    def _sintesi_da_leggere(self):
        scelta = self.impostazioni["sintesi"]
        if scelta != GBsintesi.AUTOMATICA:
            return sintesi.nome(scelta)
        effettiva = self._sintesi.scelta(GBsintesi.AUTOMATICA)
        # Traduttori: la sintesi scelta da sola; sintesi e' quella che parla adesso, come NVDA.
        return _("automatica, adesso {sintesi}").format(sintesi=sintesi.nome(effettiva)) if effettiva else _("automatica, adesso nessuna")

    def _scegli_la_sintesi(self, genitore):
        """La sintesi dei sottotitoli, da una lista: l'automatica e le uscite
        che si possono usare adesso."""
        chiavi = [GBsintesi.AUTOMATICA, *GBsintesi.disponibili()]
        attuale = self.impostazioni["sintesi"]
        if attuale not in chiavi:
            # Una scelta di prima che ora non risponde resta in fondo, e lo dice.
            chiavi.append(attuale)
        righe = [self._riga_della_sintesi(chiave) for chiave in chiavi]
        self._domanda()
        nome = VOCI_DELLE_IMPOSTAZIONI["sintesi"][0]
        with FinestraScelta(genitore, nome, righe, chiavi.index(attuale)) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                # Traduttori: voce e' il nome dell'impostazione, Sintesi di sottotitoli e karaoke.
                self._annullato(_("{voce} non cambiata.").format(voce=nome))
                return
            indice = dialogo.GetSelection()
        self.impostazioni["sintesi"] = chiavi[indice]
        self._salva_impostazioni()
        genitore.aggiorna("sintesi", self._riga_dell_impostazione("sintesi"))
        # Traduttori: voce e' il nome dell'impostazione, Sintesi di sottotitoli e karaoke; sintesi quella scelta.
        self._riscontro("impostazione_cambiata", _("{voce}: {sintesi}.").format(voce=nome, sintesi=self._sintesi_da_leggere()))

    def _riga_della_sintesi(self, chiave):
        if chiave == GBsintesi.AUTOMATICA:
            return _("Automatica: lo screen reader attivo, altrimenti la voce di Windows")
        if chiave in GBsintesi.USCITE and self._sintesi.scelta(chiave) is None:
            return _("{sintesi}, che adesso non risponde").format(sintesi=sintesi.nome(chiave))
        return sintesi.nome(chiave)[0].upper() + sintesi.nome(chiave)[1:]

    # I MIDI, tappa 8: FluidSynth e il banco dei suoni.

    def _prepara_i_midi(self, dopo=None, genitore=None):
        """Al primo MIDI: dice cosa serve, scarica FluidSynth se manca, cerca
        nei dischi i banchi di suoni e li propone; se non ce ne sono propone
        FluidR3. Tutto in disparte; dopo() arriva quando i MIDI sono pronti.
        genitore e' il dialogo da cui si parte, se c'e', per le domande."""
        if self._midi_in_preparazione:
            self._riscontro("non_disponibile", _("Sto preparando i MIDI: un momento."))
            return
        serve_fluidsynth = not midi.fluidsynth_presente()
        if serve_fluidsynth:
            domanda = _("Per suonare i MIDI MeTeOra usa FluidSynth, un programma libero di circa 3 MB, e un banco di suoni General MIDI. "
                "Scarico FluidSynth e cerco nei dischi i banchi che hai già? La ricerca può durare qualche minuto.")
        else:
            domanda = _("Per suonare i MIDI serve un banco di suoni General MIDI. Cerco nei dischi quelli che hai già? La ricerca può durare qualche minuto.")
        if not self._conferma(domanda, "MIDI", self._genitore_valido(genitore)):
            self._annullato(MIDI_DA_PREPARARE)
            return
        self._midi_in_preparazione = True

        def lavoro():
            if serve_fluidsynth:
                wx.CallAfter(self._riscontro, "scaricamento_avviato", _("Scarico FluidSynth."))
                try:
                    midi.scarica_fluidsynth()
                except (OSError, ValueError) as e:
                    return ("errore", _("FluidSynth non si scarica: {errore}").format(errore=e))
                wx.CallAfter(self._riscontro, "scaricamento_finito", _("FluidSynth pronto."))
            wx.CallAfter(self._riscontro_dopo, "ricerca_avviata", _("Cerco i banchi di suoni nei dischi."))
            return ("trovati", midi.cerca_banchi(avvisa=lambda quante: wx.CallAfter(self.scrivi, plurale(quante, "Cerco i banchi: {n} cartella vista.",
                "Cerco i banchi: {n} cartelle viste."), "banchi")))

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
            self._riscontro("ricerca_finita", _("Nei dischi non ho trovato banchi di suoni General MIDI."))
            if self._conferma(_("Scarico FluidR3 GM, il banco storico di FluidSynth, circa {mega} MB?").format(mega=midi.FLUIDR3_DIMENSIONE // 1_000_000), "MIDI", genitore):
                self._scarica_fluidr3(dopo, genitore)
            else:
                self._annullato(MIDI_DA_PREPARARE)
            return
        self._riscontro("ricerca_finita", ngettext("Trovato un banco General MIDI.", "Trovati {n} banchi General MIDI.", len(trovati)).format(n=len(trovati)))
        self._scegli_fra_i_banchi(trovati, genitore, dopo)

    def _scegli_fra_i_banchi(self, trovati, genitore, dopo=None):
        """La lista dei banchi trovati, con in fondo lo scaricamento di FluidR3."""
        # Traduttori: un banco di suoni trovato: nome, dimensione e cartella.
        righe = [_("{nome}, {dimensione}, in {cartella}").format(nome=os.path.splitext(os.path.basename(p))[0], dimensione=midi.dimensione_da_leggere(d),
            cartella=os.path.dirname(p)) for p, d in trovati]
        righe.append(_("Scarica FluidR3 GM, circa {mega} MB").format(mega=midi.FLUIDR3_DIMENSIONE // 1_000_000))
        self._domanda()
        with FinestraScelta(genitore, _("Banco dei suoni MIDI"), righe, 0) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Banco dei suoni MIDI non cambiato."))
                return
            indice = dialogo.GetSelection()
        if indice == len(trovati):
            self._scarica_fluidr3(dopo, genitore)
        else:
            self._usa_il_banco(trovati[indice][0], dopo, genitore)

    def _scarica_fluidr3(self, dopo=None, genitore=None):
        self._midi_in_preparazione = True
        self._riscontro("scaricamento_avviato", _("Scarico FluidR3 GM, circa {mega} MB.").format(mega=midi.FLUIDR3_DIMENSIONE // 1_000_000))
        decimi = [0]

        def avanza(scaricati, totale):
            if totale and scaricati * 10 // totale > decimi[0]:
                decimi[0] = scaricati * 10 // totale
                wx.CallAfter(self.scrivi, _("FluidR3 GM: {percentuale} per cento.").format(percentuale=decimi[0] * 10), "banchi")

        def lavoro():
            try:
                return ("banco", midi.scarica_fluidr3(avanza))
            except (OSError, ValueError) as e:
                return ("errore", _("FluidR3 GM non si scarica: {errore}").format(errore=e))

        midi_in_disparte(lavoro, lambda esito: wx.CallAfter(self._fluidr3_scaricato, esito, dopo, genitore))

    def _fluidr3_scaricato(self, esito, dopo, genitore):
        self._midi_in_preparazione = False
        if self._chiusa:
            return
        tipo, valore = esito
        if tipo == "errore":
            self._riscontro("errore", valore)
            return
        self._riscontro("scaricamento_finito", _("FluidR3 GM scaricato."))
        # Il banco nuovo, e il MIDI in attesa, dopo il suono dello scaricamento.
        self._dopo_il_suono(self._usa_il_banco, valore, dopo, genitore)

    def _usa_il_banco(self, percorso, dopo=None, genitore=None):
        """Il banco scelto vale da subito, e si ricorda."""
        self._statistiche.conta("banchi_scelti")
        self.impostazioni["banco_midi"] = percorso
        self._salva_impostazioni()
        self._applica_il_banco()
        # Il dialogo da cui si e' partiti puo' essersi chiuso intanto.
        if genitore and genitore.IsShown() and hasattr(genitore, "aggiorna"):
            genitore.aggiorna("banco_midi", self._riga_dell_impostazione("banco_midi"))
        self._riscontro("impostazione_cambiata", _("I MIDI suonano con il banco {banco}.").format(banco=os.path.basename(percorso)))
        if dopo is not None and self._midi_pronti():
            self._dopo_il_suono(dopo)

    def _banco_da_leggere(self):
        banco = self.impostazioni["banco_midi"]
        if not banco:
            return _("nessuno, si sceglie al primo MIDI")
        if not midi.e_un_banco(banco):
            return _("{banco}, che non si trova più").format(banco=banco)
        if midi.fluidsynth_presente():
            return os.path.basename(banco)
        return _("{banco}, FluidSynth da scaricare").format(banco=os.path.basename(banco))

    def _scegli_il_banco(self, genitore):
        """La voce Banco dei suoni MIDI: cerca nel PC, scrivi il percorso, o
        scarica FluidR3."""
        righe = [_("Cerca i banchi nel PC"), _("Scrivi il percorso di un banco"), _("Scarica FluidR3 GM, circa {mega} MB").format(mega=midi.FLUIDR3_DIMENSIONE // 1_000_000)]
        self._domanda()
        with FinestraScelta(genitore, _("Banco dei suoni MIDI"), righe, 0) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Banco dei suoni MIDI non cambiato."))
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
        with DialogoTesto(genitore, _("Il percorso del banco di suoni, un file sf2 o sf3."), _("Banco dei suoni MIDI"), self.impostazioni["banco_midi"]) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Banco dei suoni MIDI non cambiato."))
                return
            percorso = dialogo.GetValue().strip().strip('"')
        if not midi.e_un_banco(percorso):
            self._riscontro("errore", _("{percorso} non è un banco di suoni: serve un file sf2 o sf3.").format(percorso=percorso))
            return
        self._usa_il_banco(percorso, genitore=genitore)
        if not midi.general_midi(percorso):
            self.scrivi(_("Non è un banco General MIDI completo: alcuni strumenti dei MIDI potrebbero mancare o suonare con un altro timbro."))

    def _scegli_come_leggere_gli_impressi(self, genitore):
        """Come si leggono i sottotitoli impressi, da una lista: al volo o con
        la passata in anticipo (Gabriele, 4 ottobre 2026)."""
        chiavi = list(MODI_DEGLI_IMPRESSI)
        righe = [f"{MODI_DEGLI_IMPRESSI[c][0].upper()}{MODI_DEGLI_IMPRESSI[c][1:]}" for c in chiavi]
        self._domanda()
        with FinestraScelta(genitore, _("Sottotitoli impressi"), righe, chiavi.index(self.impostazioni["impressi"])) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Sottotitoli impressi non cambiati."))
                return
            indice = dialogo.GetSelection()
        self.impostazioni["impressi"] = chiavi[indice]
        self._salva_impostazioni()
        genitore.aggiorna("impressi", self._riga_dell_impostazione("impressi"))
        # Traduttori: modo e' come si leggono, come letti al volo, mentre il video suona.
        self._riscontro("impostazione_cambiata", _("I sottotitoli impressi ora sono {modo}.").format(modo=MODI_DEGLI_IMPRESSI[chiavi[indice]]))

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
                # Traduttori: voce e' il nome dell'impostazione, come Ripetizione o Volume uniforme.
                self._annullato(_("{voce}: non cambiato.").format(voce=nome))
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
        # Traduttori: destinazione e' dove vanno, come alla sintesi e al braille.
        frase = _("Sottotitoli e karaoke ora vanno {destinazione}.").format(destinazione=sintesi.DESTINAZIONI[chiave])
        effettiva = self._sintesi.scelta(self.impostazioni["sintesi"])
        if chiave != "sintesi" and effettiva is not None and effettiva not in GBsintesi.CON_IL_BRAILLE:
            frase += " " + _("Con {sintesi}, il braille non arriva: ce l'hanno NVDA e JAWS.").format(sintesi=sintesi.nome(effettiva))
        return frase

    def _scegli_il_volume_uniforme(self, genitore):
        """Il volume uniforme con ReplayGain (1.96.0): vale subito, anche per
        il brano in corso."""
        if self._scegli_da_una_lista(genitore, "replaygain", valori.VOLUMI_UNIFORMI, FRASI_DEL_VOLUME_UNIFORME.get):
            self.motore.replaygain = self.impostazioni["replaygain"]

    def _scegli_il_modo_del_karaoke(self, genitore):
        """Il testo del karaoke per riga o per strofa (Gabriele, 4 ottobre
        2026): la traccia del brano in corso si rifa' subito."""
        if self._scegli_da_una_lista(genitore, "karaoke", MODI_DEL_KARAOKE,
                # Traduttori: modo e' come arriva il testo, come per riga.
                lambda chiave: _("Il testo del karaoke ora arriva {modo}.").format(modo=MODI_DEL_KARAOKE[chiave])):
            self._applica_il_karaoke()

    def _scegli_il_modello_casuale(self, genitore):
        """Il modello della riproduzione casuale, da una lista (Gabriele,
        collaudo della 1.60.1). Cambiandolo il mazzo si rifa'."""
        chiavi = list(valori.MODELLI_CASUALI)
        righe = [f"{valori.MODELLI_CASUALI[c][0].upper()}{valori.MODELLI_CASUALI[c][1:]}: {SPIEGAZIONI_DEI_MODELLI[c]}" for c in chiavi]
        self._domanda()
        with FinestraScelta(genitore, _("Modello della riproduzione casuale"), righe, chiavi.index(self.impostazioni["modello_casuale"])) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Modello della riproduzione casuale non cambiato."))
                return
            indice = dialogo.GetSelection()
        self.impostazioni["modello_casuale"] = chiavi[indice]
        self._ricomincia_il_mazzo()
        self._salva_impostazioni()
        genitore.aggiorna("modello_casuale", self._riga_dell_impostazione("modello_casuale"))
        self._riscontro("impostazione_cambiata", _("La riproduzione casuale ora va con il modello {modello}.").format(modello=valori.MODELLI_CASUALI[chiavi[indice]]))

    def _comando_scheda_audio(self):
        """Ctrl e Maiuscolo con X: la lista della voce Scheda audio, senza
        passare dalle impostazioni (Gabriele, 2.6.0)."""
        self._scegli_la_scheda_audio(None)

    def _scegli_la_scheda_audio(self, genitore):
        """La scelta della destinazione, una lista sola con il filtro: in cima
        la scelta automatica, poi le schede del PC in ordine di latenza, che
        valgono per musica ed effetti, poi gli speaker e i gruppi Cast che la
        ricerca vede, che valgono per la musica (1.119.0). genitore e' la
        finestra delle impostazioni, o None con Ctrl e Maiuscolo con X: la
        lista si apre allora sulla finestra principale (2.6.0)."""
        scelta = self._scelta_del_pc()
        try:
            # Una scheda arrivata dopo l'avvio, se l'avviso di mpv non e' ancora
            # arrivato o e' andato perso (1.116.0).
            schede_audio.rileggi_se_serve(self.motore)
            elenco = schede_audio.uscite()
            # La scelta automatica: con l'automatica in uso e' la scheda del
            # mixer, senza aprire niente; altrimenti la si rifa' per provarla.
            automatica = (None if scelta else schede_audio.in_uso(elenco)) or schede_audio.automatica()
        except Exception as e:  # noqa: BLE001 - PortAudio fallisce in molti modi, e lo dice la console
            self._riscontro("errore", _("Non riesco a leggere le schede audio: {errore}.").format(errore=e))
            return
        apparecchi = self._ricerca_cast.apparecchi() if self._ricerca_cast is not None else []
        # Traduttori: la scheda audio scelta da sola, nella lista delle schede; dopo i due punti quella che sarebbe adesso.
        righe = [_("Automatica: {scheda}").format(scheda=schede_audio.etichetta(automatica)) if automatica else _("Automatica"), *(schede_audio.etichetta(u) for u in elenco),
                 *(riga_dello_speaker(voce) for voce in apparecchi)]
        attuale = schede_audio.ritrova(scelta, elenco)
        indice = elenco.index(attuale) + 1 if attuale is not None else 0
        speaker = self._speaker_scelto()
        if speaker is not None:
            indice = next((len(elenco) + 1 + i for i, voce in enumerate(apparecchi) if str(voce["uuid"]) == speaker["cast"]), indice)
        self._domanda()
        with FinestraScelta(genitore or self, _("Scheda audio"), righe, indice, con_filtro=True) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK or dialogo.GetSelection() < 0:
                self._annullato(_("Scheda audio non cambiata."))
                return
            indice = dialogo.GetSelection()
        if indice > len(elenco):
            self._collega_lo_speaker(apparecchi[indice - len(elenco) - 1], salva=True, genitore=genitore)
            return
        self._usa_la_scheda(schede_audio.da_salvare(elenco[indice - 1]) if indice > 0 else {}, genitore)

    def _usa_la_scheda(self, nuova, genitore):
        """Applica la scheda scelta e la salva; il suono della scheda arriva
        gia' da quella nuova. Se gli effetti non riescono ad aprirla si torna
        all'automatica, e la console lo dice. La prova d'apertura vale anche
        con il volume degli effetti a zero. Con uno speaker Cast in uso, la
        musica torna sul PC da dove era (1.119.0)."""
        self._speaker_atteso = None
        if self.motore.lontano is not None:
            self._passa_a(None)
        esito, errore = self._applica_la_scheda(nuova)
        aperta = errore is None and self._effetti_si_aprono()
        evento = None
        if aperta:
            self._suono("scheda_audio")
            testo = _("Scheda audio: {scheda}.").format(scheda=self._scheda_dell_esito(esito))
            if not esito["musica"]:
                testo += " " + _("La musica non la ritrova, e suona sulla scheda di Windows.")
        else:
            evento = "errore"
            if nuova:
                nome = self._nome_della_scheda(nuova["dispositivo"], nuova["interfaccia"])
                if errore is not None:
                    testo = _("La scheda audio {scheda} non si apre: {errore}.").format(scheda=nome, errore=errore)
                else:
                    testo = _("La scheda audio {scheda} non si apre.").format(scheda=nome)
                nuova = {}
                esito, errore = self._applica_la_scheda(nuova)
                if errore is not None:
                    testo += " " + _("Torno alla scelta automatica, ma neanche lei va: {errore}.").format(errore=errore)
                elif esito["dispositivo"]:
                    testo += " " + _("Torno alla scelta automatica, {scheda}.").format(scheda=self._nome_della_scheda(esito["dispositivo"], esito["interfaccia"]))
                else:
                    testo += " " + _("Torno alla scelta automatica.")
            elif errore is not None:
                testo = _("La scheda audio automatica non si apre: {errore}.").format(errore=errore)
            else:
                testo = _("La scheda audio automatica non si apre.")
        self.impostazioni["scheda_audio"] = nuova
        self._scheda_in_disparte = None
        self._salva_impostazioni()
        self._aggiorna_la_scheda_delle_statistiche()
        if genitore:
            genitore.aggiorna("scheda_audio", self._riga_dell_impostazione("scheda_audio"))
        if evento:
            self._riscontro(evento, testo)
        else:
            self.scrivi(testo)

    # Gli speaker Cast (tappa 15 b, 1.119.0): la strada A con conversione,
    # con lontano.py e trasmissione.py; dalla 2.7.0 i brani da convertire vanno
    # come WAV in RAM, con wav_in_ram.py, senza disco.

    def _scelta_del_pc(self):
        """La scheda del PC della scelta salvata: per uno speaker Cast quella
        che la scelta tiene con se', per gli effetti e per quando lo speaker
        manca; altrimenti la scelta stessa."""
        scelta = self.impostazioni["scheda_audio"]
        return scelta.get("pc", {}) if "cast" in scelta else scelta

    def _speaker_scelto(self):
        """La scelta salvata se e' uno speaker Cast, {"cast", "nome", "pc"},
        o None."""
        scelta = self.impostazioni["scheda_audio"]
        return scelta if "cast" in scelta else None

    def _avvia_la_ricerca_cast(self):
        """La ricerca degli speaker, accesa all'avvio se c'e' pychromecast. Se
        lo speaker scelto non arriva entro ATTESA_DELLO_SPEAKER, la console
        lo dice."""
        speaker = self._speaker_scelto()
        if not trasmissione.disponibile():
            if speaker is not None:
                self._avviso_delle_uscite("errore", _("Lo speaker scelto, {nome}, non si può usare: manca pychromecast. Suono sul PC.").format(nome=speaker["nome"]))
            return
        self._ricerca_cast = trasmissione.Ricerca(al_cambio=lambda: wx.CallAfter(self._apparecchi_cambiati))
        self._ricerca_cast.avvia()
        if speaker is not None:
            wx.CallLater(ATTESA_DELLO_SPEAKER, self._speaker_non_ancora_arrivato)

    def _speaker_non_ancora_arrivato(self):
        speaker = self._speaker_scelto()
        if self._chiusa or speaker is None or self.motore.lontano is not None or self._speaker_atteso is None:
            return
        self._comincia_l_assenza()
        self._avviso_delle_uscite("scheda_sparita", _("Lo speaker scelto, {nome}, non c'è: suono sul PC finché non compare.").format(nome=speaker["nome"]))

    def _apparecchi_cambiati(self):
        """La ricerca ha visto arrivare, andare o cambiare un apparecchio: se
        e' lo speaker che si aspetta, ci si collega."""
        if self._chiusa or self._ricerca_cast is None or self._speaker_atteso is None or self._speaker_in_collegamento is not None:
            return
        voce = next((v for v in self._ricerca_cast.apparecchi() if str(v["uuid"]) == self._speaker_atteso), None)
        if voce is not None:
            self._collega_lo_speaker(voce)

    def _collega_lo_speaker(self, voce, salva=False, genitore=None):
        """Si collega allo speaker in disparte, perche' puo' volerci un po';
        la scelta si salva, con salva, quando il collegamento riesce."""
        if self._speaker_in_collegamento is not None or self._ricerca_cast is None:
            return
        self._speaker_in_collegamento = voce["uuid"]
        if salva:
            self.scrivi(_("Mi collego a {nome}.").format(nome=voce["nome"]), "scheda_audio")
        ricerca, converti = self._ricerca_cast, self.motore.sorgente_wav
        avvisi = {
            "alla_fine": lambda: wx.CallAfter(self._brano_finito),
            "all_errore": lambda percorso: wx.CallAfter(self._brano_in_errore, percorso),
            "al_caricamento": lambda: wx.CallAfter(self._aggiorna_il_video),
            "all_interruzione": lambda: wx.CallAfter(self._speaker_interrotto),
            "al_guasto": lambda errore: wx.CallAfter(self._speaker_perso, errore),
        }

        def collega():
            try:
                server = trasmissione.Server(trasmissione.indirizzo_verso(voce["indirizzo"]), 0)
                try:
                    lettore = lontano.LettoreLontano(lambda allo_stato, al_distacco: ricerca.connetti(voce["uuid"], allo_stato, al_distacco=al_distacco),
                                                     server, converti, **avvisi)
                except Exception:
                    server.ferma()
                    raise
            except Exception as errore:  # noqa: BLE001 - la rete e lo speaker falliscono in molti modi, e lo dice la console
                wx.CallAfter(self._speaker_non_collegato, voce, errore, salva)
                return
            wx.CallAfter(self._speaker_collegato, voce, lettore, salva, genitore)

        threading.Thread(target=collega, name="MeTeOra, collegamento allo speaker", daemon=True).start()

    def _speaker_collegato(self, voce, lettore, salva, genitore):
        """Il collegamento e' riuscito: la musica passa allo speaker da dove
        era, gli effetti restano sul PC."""
        self._speaker_in_collegamento = None
        if self._chiusa:
            lettore.chiudi(attendi=False)
            return
        tornato = self._speaker_atteso is not None and not salva and self._assenza_dal is not None
        self._speaker_atteso = None
        self._passa_a(lettore)
        if salva:
            self.impostazioni["scheda_audio"] = {"cast": str(voce["uuid"]), "nome": voce["nome"], "pc": self._scelta_del_pc()}
            self._salva_impostazioni()
            self._statistiche.conta("speaker_scelti")
            if genitore:
                genitore.aggiorna("scheda_audio", self._riga_dell_impostazione("scheda_audio"))
        self._aggiorna_la_scheda_delle_statistiche()
        if tornato:
            self._finisce_l_assenza()
            self._avviso_delle_uscite("scheda_tornata", _("Lo speaker {nome} è tornato: la musica suona di nuovo lì.").format(nome=voce["nome"]))
            return
        # Traduttori: tipo e' la riga dello speaker senza il nome, come speaker Cast, Google Home Speaker.
        testo = _("Suono su {nome}, {tipo}. Gli effetti restano sul PC; "
                  "dissolvenza, equalizzatore, velocità e tono sullo speaker non valgono.").format(nome=voce["nome"], tipo=riga_dello_speaker(voce).split(", ", 1)[-1])
        if salva:
            self._riscontro("scheda_audio", testo)
        else:
            self._finisce_l_assenza()
            self._avviso_delle_uscite("scheda_audio", testo)

    def _speaker_non_collegato(self, voce, errore, salva):
        self._speaker_in_collegamento = None
        if self._chiusa:
            return
        if salva:
            self._riscontro("errore", _("Non riesco a collegarmi a {nome}: {errore}.").format(nome=voce["nome"], errore=errore))
        # Uno speaker atteso che non risponde si riprova al prossimo cambio
        # della ricerca.

    def _passa_a(self, lettore):
        """La musica passa al lettore lontano dato, o con None al PC, dal
        punto in cui era e in pausa se lo era."""
        percorso = self.motore.in_corso
        posizione = self.motore.posizione
        punto = self._punto_di_ripresa
        if posizione is None and punto and punto[0] == percorso:
            posizione = punto[2]
        in_pausa = self.motore.in_pausa
        sottobrano = self.motore.sottobrano if self.motore.sottobrani else None
        self._uscente = self._preparato = None
        self.motore.usa_il_lontano(lettore)
        if percorso:
            self.motore.suona(percorso, sottobrano, inizio=posizione, in_pausa=in_pausa)
        self._aggiorna_la_scheda_delle_statistiche()

    def _speaker_perso(self, errore):
        """Lo speaker non risponde piu': la musica torna sul PC da dove era, e
        quando lo speaker ricompare la ricerca lo riprende."""
        lettore = self.motore.lontano
        if self._chiusa or lettore is None:
            return
        nome = lettore.nome
        speaker = self._speaker_scelto()
        self._passa_a(None)
        self._speaker_atteso = speaker["cast"] if speaker is not None else None
        self._comincia_l_assenza()
        self._avviso_delle_uscite("scheda_sparita", _("Lo speaker {nome} non risponde più: suono sul PC, da dove eri.").format(nome=nome))
        registro.scrivi(f"Lo speaker {nome} non risponde: {errore!r}")

    def _speaker_interrotto(self):
        """Sullo speaker e' partito altro, per esempio dal telefono: MeTeOra
        si ferma, e la playlist non va avanti."""
        lettore = self.motore.lontano
        if self._chiusa or lettore is None:
            return
        self._uscente = self._preparato = None
        self._aggiorna_etichette()
        self._riscontro("stop", _("Su {nome} suona altro, mandato da fuori: MeTeOra si ferma. X riparte da qui.").format(nome=lettore.nome))

    def _vale_solo_sul_pc(self, cosa):
        """Vero, e lo dice, se suona uno speaker Cast: dissolvenza,
        equalizzatore, velocita' e tono sullo speaker non valgono, e tornano
        con una scheda del PC (decisione di Gabriele del 29 ottobre 2026).
        Dalla 2.6.2 il rifiuto va anche alla sintesi e al braille dei
        sottotitoli, oltre al suono e alla console: nella console, da sola,
        si perdeva (Gabriele, collaudo della 2.6.0)."""
        lettore = self.motore.lontano
        if lettore is None:
            return False
        self._suono("non_disponibile")
        # Traduttori: cosa e' quello che sullo speaker non vale, come La velocità o L'equalizzatore; nome quello dello speaker.
        self._riporta(_("{cosa} su {nome} non vale: vale sulle schede del PC.").format(cosa=cosa, nome=lettore.nome), None)
        return True

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
            self._riscontro("errore", _("Non riesco a salvare la console: {errore}.").format(errore=e.strerror or e))
            return
        quante = len(self._righe)
        self._riscontro("console_salvata", ngettext("Console salvata in {nome}, nella cartella del programma: {n} riga.",
            "Console salvata in {nome}, nella cartella del programma: {n} righe.", quante).format(nome=nome, n=quante))

    # L'aggiornamento automatico (Gabriele, 4 ottobre 2026, 1.84.0): lo
    # conduce aggiornamento.py, dal suo filo; qui la finestra e le frasi.

    @property
    def chiusa(self):
        return self._chiusa

    def proponi_l_aggiornamento(self, attuale, nuova, novita, attesa=None):
        """La proposta, con le novita': vero se si sceglie di aggiornare."""
        self._domanda()
        self.scrivi(_("È disponibile MeTeOra {versione}: la finestra dell'aggiornamento dice le novità.").format(versione=nuova))
        with FinestraAggiornamento(self, attuale, nuova, novita, attesa) as dialogo:
            scelta = dialogo.ShowModal()
        if scelta == wx.ID_YES:
            self._riscontro("aggiornamento", _("Scarico MeTeOra {versione}: la console dice a che punto sono.").format(versione=nuova))
            return True
        self._annullato(_("Aggiornamento rimandato: te lo ripropongo al prossimo avvio."))
        return False

    def avanzamento_dell_aggiornamento(self, presi, totale):
        """A che punto e' lo scaricamento, in una riga che si riscrive."""
        if self._chiusa:
            return
        if totale:
            testo = _("Aggiornamento: {percentuale}%.").format(percentuale=presi * 100 // totale)
        else:
            testo = _("Aggiornamento: {mega} MB.").format(mega=presi // 1048576)
        self.scrivi(testo, "aggiornamento")

    def avvisa_dell_aggiornamento(self, testo):
        """Un esito dell'aggiornamento: nella console e in una finestra, che
        aspetta l'OK."""
        self.scrivi(testo)
        wx.MessageBox(testo, _("Aggiornamento di MeTeOra"), wx.OK | wx.ICON_INFORMATION, self)

    def chiudi_per_aggiornare(self):
        """GBUtils sta per sostituire MeTeOra: si chiude salvando tutto."""
        self.Close(force=True)

    # L'invito a offrire un caffe' (Gabriele, 4 ottobre 2026, 1.75.0): dalla
    # 1.102.4 solo dalla voce delle impostazioni, non piu' alla chiusura
    # (Gabriele, 6 ottobre 2026).

    def _invito_alla_donazione(self, genitore):
        """Il testo lo da' Donazione di GBUtils, che con la probabilita' piena
        lo da' sempre; None resta per un testo che non arriva. La finestra e'
        come quella di Tornello, con il suo suono. Restituisce come si e'
        chiusa, wx.ID_YES se si e' aperto PayPal, o None se non si e' aperta."""
        from GBUtils import Donazione

        testo = Donazione(lang="it", probabilita=100, stampa=False)
        if testo is None:
            return None
        self._suono("donazione")
        with DialogoDonazione(genitore, testo) as dialogo:
            return dialogo.ShowModal()

    def _associa_i_formati(self, genitore):
        """La voce Associazioni dei formati (1.91.0): MeTeOra in Apri con per
        tutti i suoi formati e fra le app predefinite di Windows, dove chi usa
        il PC lo puo' scegliere come predefinito; oppure lo toglie. Solo dal
        programma compilato: da sorgente Windows aprirebbe Python."""
        if not getattr(sys, "frozen", False):
            self._riscontro("non_disponibile", _("Le associazioni dei formati si fanno solo dal programma compilato: da sorgente, Windows aprirebbe Python."))
            return
        scelte = [_("Associa: MeTeOra in Apri con per tutti i suoi formati, poi la pagina delle app predefinite di Windows"),
            _("Togli MeTeOra dalle associazioni")]
        self._domanda()
        with FinestraScelta(genitore, _("Associazioni dei formati"), scelte, 0) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Associazioni dei formati: niente di cambiato."))
                return
            indice = dialogo.GetSelection()
        try:
            if indice == 0:
                quante = associazioni.registra(sys.executable)
            else:
                associazioni.togli()
        except OSError as e:
            self._riscontro("errore", _("Non riesco a cambiare le associazioni dei formati: {errore}.").format(errore=e.strerror or e))
            return
        if indice:
            self._riscontro("impostazione_cambiata", _("MeTeOra non è più nelle associazioni dei formati."))
            return
        # Traduttori: Apri con e' il menu di Esplora file.
        self._riscontro("impostazione_cambiata", ngettext("MeTeOra ora compare in Apri con per {n} formato. Si apre la pagina delle app predefinite "
            "di Windows: lì, se vuoi, lo scegli come predefinito.", "MeTeOra ora compare in Apri con per {n} formati. Si apre la pagina delle app predefinite "
            "di Windows: lì, se vuoi, lo scegli come predefinito.", quante).format(n=quante))
        with contextlib.suppress(OSError):
            associazioni.apri_le_app_predefinite()

    def _dona(self, genitore):
        """La voce Dona per questo progetto delle impostazioni, l'unica strada
        per l'invito: compare sempre."""
        if self._invito_alla_donazione(genitore) == wx.ID_YES:
            self.scrivi(_("PayPal si apre nel browser: grazie di cuore!"))

    # Il PUB, il gruppo di supporto (issue 30, 2.1.0): indirizzi, informazioni
    # sul computer e mail da GBUtils, la finestra della mail da GBwx, le parole
    # da pub.py. La finestra si apre sempre, anche quando il programma di posta
    # c'e', e senza posta guida un passo alla volta.

    def _entra_al_pub(self, genitore):
        """Entra al PUB: la mail che iscrive al gruppo di supporto."""
        self._suono("pub_entra")
        self._mail_al_pub(genitore, pub.mail_d_iscrizione(), _("La mail d'iscrizione al PUB è pronta: spediscila tu."),
            _("Entra al PUB: niente di preparato."))

    def _chiedi_aiuto_al_pub(self, genitore):
        """Chiedi aiuto al PUB: la mail al gruppo, con l'oggetto che dice la
        versione, la riga da sostituire con la domanda e le informazioni su
        MeTeOra, sulla scheda audio e sul computer, che l'utente vede e puo'
        cancellare prima di spedire. Se ci sono registri degli errori o dei
        crash, la casella li allega, ripuliti (2.4.0, Gabriele)."""
        from GBUtils import informazioni_di_sistema

        self._suono("pub_aiuto")
        scheda = None
        with contextlib.suppress(Exception):
            scheda = self._scheda_da_leggere()
        argomenti = (version.VERSION, bool(getattr(sys, "frozen", False)), informazioni_di_sistema(), scheda)
        cartella = percorsi.cartella_programma()
        presenti = pub.registri_presenti(cartella)
        mail = pub.mail_d_aiuto(*argomenti, casella=bool(presenti))
        spuntata = [False]

        def cambi(con_i_registri):
            # Il file si scrive quando la casella si spunta, ripulito dal
            # nome dell'utente e del computer.
            spuntata[0] = con_i_registri
            if not con_i_registri:
                return {}
            try:
                registri = pub.scrivi_i_registri(cartella, version.VERSION, os.environ.get("USERNAME", ""), os.environ.get("COMPUTERNAME", ""))
            except OSError as errore:
                return {"spiegazione": mail["spiegazione"] + "\n" + _("Non riesco a scrivere il file dei registri: {errore}.").format(errore=errore.strerror or errore)}
            return pub.mail_d_aiuto(*argomenti, casella=True, registri=registri) if registri else {}

        casella = (pub.CASELLA_DEI_REGISTRI, cambi) if presenti else None
        if self._mail_al_pub(genitore, mail, _("La mail d'aiuto al PUB è pronta: scrivi la domanda e spediscila tu."),
                _("Chiedi aiuto al PUB: niente di preparato."), casella) and spuntata[0]:
            self._statistiche.conta("registri_al_pub")

    def _mail_al_pub(self, genitore, mail, pronta, annullata, casella=None):
        """La finestra di GBwx che prepara la mail, con la casella se c'e'. La
        console dice se la mail e' pronta, cioe' aperta nel programma di
        posta o scritta passo per passo, o se la finestra si e' chiusa prima,
        con il suono dell'annullamento. Torna vero se e' pronta."""
        from GBwx import finestra_mail

        riuscita = finestra_mail(genitore, mail["titolo"], mail["destinatario"], mail["oggetto"], mail["corpo"], mail["spiegazione"],
            mail["passi"], pub.PULSANTI, pub.SENZA_POSTA, casella=casella)
        if riuscita:
            self._statistiche.conta("mail_al_pub_pronte")
            self.scrivi(pronta)
        else:
            self._annullato(annullata)
        return riuscita

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
        if not self._conferma(plurale(len(unici), "Eliminare {n} marker?", "Eliminare {n} marker?"), _("Elimina marcatori"), genitore):
            self._annullato(_("Eliminazione annullata."))
            return
        tolti = sum(self.marcatori.togli(k, m) for k, m in unici)
        self._salva_i_marker(*dict.fromkeys(k for k, _m in unici))
        self._statistiche.conta("marker_tolti_finestra", tolti)
        self._riscontro("marker_eliminato", plurale(tolti, "Eliminati {n} marker.", "Eliminati {n} marker."))

    def _cancella_tutti_i_marcatori(self, genitore):
        """Cancella tutto nella finestra dei marcatori, dopo una conferma con
        No come risposta predefinita."""
        voci = self.marcatori.voci
        quanti, file = sum(len(voce["marker"]) for voce in voci.values()), len(voci)
        if not quanti:
            self._riscontro("non_disponibile", _("Non ci sono marcatori da cancellare."))
            return
        # Traduttori: marker e' come 3 marker, file come 2 file.
        if not self._conferma(_("Cancellare tutti i marcatori, {marker} in {file}? Non si possono recuperare.").format(
                marker=plurale(quanti, "{n} marker", "{n} marker"), file=plurale(file, "{n} file", "{n} file")), _("Cancella tutto"), genitore):
            self._annullato(_("I marcatori restano dove sono."))
            return
        # Le chiavi da rinfrescare nella plancia si prendono prima di cancellare.
        chiavi = list(voci)
        tolti = self.marcatori.cancella_tutto()
        self._salva_i_marker(*chiavi)
        self._statistiche.conta("marker_tolti_finestra", tolti)
        # Traduttori: marker e' come 3 marker, file come 2 file.
        self._riscontro("marcatori_cancellati", _("Cancellati tutti i marcatori: {marker} in {file}.").format(
            marker=plurale(tolti, "{n} marker", "{n} marker"), file=plurale(file, "{n} file", "{n} file")))

    def _esporta_i_marcatori(self, scelti, genitore):
        """Esporta selezionati: i marker scelti in un file JSON senza
        percorsi, che un'altra copia di MeTeOra puo' importare."""
        dati, saltati = self.marcatori.esporta(scelti)
        esportati = sum(len(voce["marker"]) for voce in dati["marcatori"])
        if not esportati:
            self._riscontro("non_disponibile", _("I marker scelti non si esportano: MeTeOra non conosce una durata valida dei loro file, e senza la durata un altro computer non li ritroverebbe."))
            return
        self._domanda()
        with DialogoDiFile(genitore, _("Esporta marcatori"), defaultDir=os.path.dirname(self.impostazioni.percorso), defaultFile=FILE_DELL_ESPORTAZIONE,
                wildcard=FILTRO_DEI_MARCATORI, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Esportazione annullata."))
                return
            percorso = dialogo.GetPath()
        if not os.path.splitext(percorso)[1]:
            percorso += ".json"
        try:
            Marcatori.scrivi_esportazione(dati, percorso)
        except OSError as e:
            self._riscontro("errore", _("Non riesco a esportare i marcatori: {errore}.").format(errore=e.strerror or e))
            return
        file = len(dati["marcatori"])
        # Traduttori: file e' come 2 file, nome quello del file scritto.
        testo = ngettext("Esportato {n} marker di {file} in {nome}.", "Esportati {n} marker di {file} in {nome}.", esportati).format(n=esportati,
            file=plurale(file, "{n} file", "{n} file"), nome=os.path.basename(percorso))
        if saltati:
            testo += " " + ngettext("{n} non esportato: MeTeOra non conosce una durata valida dei loro file.",
                "{n} non esportati: MeTeOra non conosce una durata valida dei loro file.", saltati).format(n=saltati)
        self._riscontro("marcatori_esportati", testo)

    def _importa_i_marcatori(self, genitore):
        """Importa marcatori: i marker di un file esportato vanno sui file con
        lo stesso nome e la stessa durata, copie comprese; quelli che ci
        sono gia' restano come sono."""
        self._domanda()
        with DialogoDiFile(genitore, _("Importa marcatori"), defaultDir=os.path.dirname(self.impostazioni.percorso), wildcard=FILTRO_DEI_MARCATORI,
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialogo:
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Importazione annullata."))
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
        presenti = ngettext("{n} c'era già", "{n} c'erano già", gia_presenti).format(n=gia_presenti) if gia_presenti else _("nessuno c'era già")
        # Traduttori: presenti e' quanti marcatori c'erano già, come nessuno c'era già o 2 c'erano già.
        self._riscontro("marcatori_importati", ngettext("Importato {n} marcatore, {presenti}.", "Importati {n} marcatori, {presenti}.", aggiunti).format(
            n=aggiunti, presenti=presenti))
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

    def _contesto_dei_marker(self, senza_brano, risveglia=False):
        """(chiave, percorso, durata, sottobrano) di cio' che suona, o None
        con il riscontro senza_brano se non suona niente. Con risveglia il
        brano fermo si ricarica in pausa (issue 39)."""
        if risveglia:
            self._risveglia_il_fermo()
        percorso = self.motore.in_corso
        if not percorso:
            # Traduttori: spiegazione e' una frase su cosa fa il comando, come i marker si mettono nel brano che suona.
            self._riscontro("niente_da_suonare", _("Non sta suonando niente: {spiegazione}").format(spiegazione=senza_brano))
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
            self._statistiche.conta("salvataggi_non_riusciti")
            self._riscontro("errore", _("Non riesco a salvare i marker, riprovo all'uscita: {errore}").format(errore=e))
        for k in chiavi:
            self._rinfresca_i_marker(k)

    def _comando_marker(self):
        """T: un marker nuovo dove si e'; se li' c'e' gia' un marker, lo rinomina."""
        contesto = self._contesto_dei_marker(_("i marker si mettono nel brano che suona."))
        if contesto is None:
            return
        k, percorso, durata, numero = contesto
        posizione = self.motore.posizione or 0.0
        esistente = self.marcatori.trova(k, posizione)
        if esistente is not None:
            self._rinomina_il_marker(k, esistente)
            return
        marker = self.marcatori.aggiungi(k, posizione, percorso, durata, numero)
        self._statistiche.marker_messo(percorso)
        self._salva_i_marker(k)
        self._riscontro("marker_messo", _("Marker {nome} a {tempo}.").format(nome=marker["nome"], tempo=durata_lunga(marker["tempo"])))

    def _salta_al_marker(self, verso):
        contesto = self._contesto_dei_marker(_("Ctrl e Maiuscolo con Y saltano fra i marker del brano che suona."), risveglia=True)
        if contesto is None:
            return
        k = contesto[0]
        if not self.marcatori.elenco(k):
            self._riscontro("non_disponibile", _("Questo brano non ha marker: T ne mette uno dove sei."))
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
                testo = _("È l'ultimo marker.") if sopra else _("Dopo di qui non ci sono marker.")
            else:
                testo = _("È il primo marker.") if sopra else _("Prima di qui non ci sono marker.")
            self._riscontro("nessun_altro_brano", testo)
            return
        self._al_marker(k, marker, verso)

    def _al_marker(self, k, marker, verso):
        """Il salto a un marker del brano in corso, con il riscontro."""
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

    def _comando_marker_attuale(self):
        """Y (issue 38): il marker su cui si e', o l'ultimo prima, fra quanti."""
        contesto = self._contesto_dei_marker(_("Y dice i marker del brano che suona."), risveglia=True)
        if contesto is None:
            return
        elenco = self.marcatori.elenco(contesto[0])
        if not elenco:
            self._riporta(_("Questo brano non ha marker: T ne mette uno dove sei."), "marker")
            return
        posizione = self.motore.posizione or 0.0
        prima = [m for m in elenco if m["tempo"] <= posizione + marcatori.TOLLERANZA]
        if not prima:
            primo = elenco[0]
            self._riporta(ngettext("Prima di qui non ci sono marker; il brano ne ha {n}, il primo è {nome}, {tempo}.",
                "Prima di qui non ci sono marker; il brano ne ha {n}, il primo è {nome}, {tempo}.", len(elenco)).format(n=len(elenco), nome=primo["nome"],
                tempo=durata_lunga(primo["tempo"])), "marker")
            return
        marker = prima[-1]
        nome, tempo_del_marker = marker["nome"], durata_lunga(marker["tempo"])
        if abs(marker["tempo"] - posizione) <= marcatori.TOLLERANZA:
            testo = _("Marker {numero} di {quanti}, {nome}, {tempo}: ci sei sopra.").format(numero=len(prima), quanti=len(elenco), nome=nome, tempo=tempo_del_marker)
        else:
            testo = _("Marker {numero} di {quanti}, {nome}, {tempo}: il più vicino prima di qui.").format(numero=len(prima), quanti=len(elenco), nome=nome,
                tempo=tempo_del_marker)
        self._riporta(testo, "marker")

    def _comando_primo_marker(self):
        self._marker_estremo(ultimo=False)

    def _comando_ultimo_marker(self):
        self._marker_estremo(ultimo=True)

    def _marker_estremo(self, ultimo):
        """Alt con Y l'ultimo marker del brano, Ctrl e Alt con Y il primo."""
        contesto = self._contesto_dei_marker(_("Alt con Y e Ctrl e Alt con Y vanno all'ultimo e al primo marker del brano che suona."), risveglia=True)
        if contesto is None:
            return
        k = contesto[0]
        elenco = self.marcatori.elenco(k)
        if not elenco:
            self._riscontro("non_disponibile", _("Questo brano non ha marker: T ne mette uno dove sei."))
            return
        self._al_marker(k, elenco[-1] if ultimo else elenco[0], 1 if ultimo else -1)

    def _comando_conta_i_marker(self):
        """R (issue 38): quanti marker ha il brano, prima e dopo il punto."""
        contesto = self._contesto_dei_marker(_("R conta i marker del brano che suona."), risveglia=True)
        if contesto is None:
            return
        elenco = self.marcatori.elenco(contesto[0])
        if not elenco:
            self._riporta(_("Questo brano non ha marker: T ne mette uno dove sei."), "marker")
            return
        posizione = self.motore.posizione or 0.0
        prima = sum(1 for m in elenco if m["tempo"] < posizione - marcatori.TOLLERANZA)
        dopo = sum(1 for m in elenco if m["tempo"] > posizione + marcatori.TOLLERANZA)
        quanti = len(elenco)
        if quanti - prima - dopo:
            testo = ngettext("Il brano ha {n} marker: {prima} prima di qui e {dopo} dopo, e sei su uno.",
                "Il brano ha {n} marker: {prima} prima di qui e {dopo} dopo, e sei su uno.", quanti).format(n=quanti, prima=prima, dopo=dopo)
        else:
            testo = ngettext("Il brano ha {n} marker: {prima} prima di qui e {dopo} dopo.", "Il brano ha {n} marker: {prima} prima di qui e {dopo} dopo.",
                quanti).format(n=quanti, prima=prima, dopo=dopo)
        self._riporta(testo, "marker")

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
            self._riscontro("non_disponibile", _("Maiuscolo con le cifre va ai marker del brano su cui sta la plancia: porta il fuoco su un brano."))
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
            file = brano.nome_del_file
            if multiplo and sottobrano:
                if not elenco:
                    testo = _("Il sottobrano {sottobrano} di {file} non ha marker.").format(sottobrano=sottobrano, file=file)
                else:
                    testo = ngettext("Non c'è il marker {numero}: il sottobrano {sottobrano} di {file} ne ha {n}.",
                        "Non c'è il marker {numero}: il sottobrano {sottobrano} di {file} ne ha {n}.", len(elenco)).format(numero=numero, sottobrano=sottobrano,
                        file=file, n=len(elenco))
            elif not elenco:
                # Traduttori: file e' il nome del file, con l'iniziale maiuscola.
                testo = _("{file} non ha marker.").format(file=f"{file[:1].upper()}{file[1:]}")
            else:
                testo = ngettext("Non c'è il marker {numero}: {file} ne ha {n}.", "Non c'è il marker {numero}: {file} ne ha {n}.", len(elenco)).format(
                    numero=numero, file=file, n=len(elenco))
            self._riscontro("nessun_altro_brano", testo)
            return
        self._statistiche.conta("marker_con_le_cifre")
        self._vai_al_marker({"playlist": dati["playlist"], "brano": brano, "numero": sottobrano, "marker": elenco[numero - 1]})

    def _togli_i_marker(self, quali):
        contesto = self._contesto_dei_marker(_("Ctrl e Maiuscolo con R, e Maiuscolo con T, tolgono i marker del brano che suona; "
            "quelli di un altro brano si tolgono con Canc sulla loro voce nella plancia."))
        if contesto is None:
            return
        k = contesto[0]
        posizione = self.motore.posizione or 0.0
        if quali == "prima":
            tolti, evento = self.marcatori.togli_prima(k, posizione), "marker_tolti_prima"
        elif quali == "dopo":
            tolti, evento = self.marcatori.togli_dopo(k, posizione), "marker_tolti_dopo"
        else:
            tolti, evento = self.marcatori.togli_tutti(k), "marker_tolti_tutti"
        if not tolti:
            if quali == "prima":
                testo = _("Non ci sono marker da togliere prima di {tempo}.").format(tempo=durata_lunga(posizione))
            elif quali == "dopo":
                testo = _("Non ci sono marker da togliere dopo {tempo}.").format(tempo=durata_lunga(posizione))
            else:
                testo = _("Non ci sono marker da togliere in tutto il brano.")
            self._riscontro("non_disponibile", testo)
            return
        self._statistiche.conta(f"marker_tolti_{quali}", tolti)
        self._salva_i_marker(k)
        if quali == "prima":
            testo = ngettext("Tolto {n} marker prima di {tempo}.", "Tolti {n} marker prima di {tempo}.", tolti).format(n=tolti, tempo=durata_lunga(posizione))
        elif quali == "dopo":
            testo = ngettext("Tolto {n} marker dopo {tempo}.", "Tolti {n} marker dopo {tempo}.", tolti).format(n=tolti, tempo=durata_lunga(posizione))
        else:
            testo = ngettext("Tolto {n} marker in tutto il brano.", "Tolti {n} marker in tutto il brano.", tolti).format(n=tolti)
        self._riscontro(evento, testo)

    def _comando_togli_i_marker_prima(self):
        self._togli_i_marker("prima")

    def _comando_togli_i_marker_dopo(self):
        self._togli_i_marker("dopo")

    def _comando_togli_i_marker(self):
        self._togli_i_marker("tutti")

    def _rinomina_il_marker(self, k, marker, genitore=None):
        with DialogoTesto(genitore or self, _("Nome del marker a {tempo}:").format(tempo=durata_lunga(marker["tempo"])), _("Rinomina il marker"), marker["nome"]) as dialogo:
            self._domanda()
            if dialogo.ShowModal() != wx.ID_OK:
                self._annullato(_("Nome del marker non cambiato."))
                return
            nome = " ".join(dialogo.GetValue().split())
        if not nome or nome == marker["nome"]:
            self._annullato(_("Nome del marker non cambiato."))
            return
        vecchio = marker["nome"]
        self.marcatori.rinomina(k, marker, nome)
        self._salva_i_marker(k)
        self._riscontro("marker_rinominato", _("Il marker {vecchio}, a {tempo}, ora si chiama {nome}.").format(vecchio=vecchio, tempo=durata_lunga(marker["tempo"]),
            nome=nome))

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
        self._statistiche.conta("marker_tolti_uno")
        self._salva_i_marker(k)
        self._riscontro("marker_eliminato", _("Eliminato il marker {nome}, a {tempo}.").format(nome=marker["nome"], tempo=durata_lunga(marker["tempo"])))

    def _vai_al_marker(self, dati):
        """Vai al marker, e Maiuscolo con le cifre: suona il brano dal marker, rispettando il loop
        A-B. Se il brano e' quello caricato ci salta, e riparte se era in
        pausa; il suono dice se il salto va avanti o indietro. Vero se ha
        suonato."""
        brano, numero, marker = dati["brano"], dati.get("numero"), dati["marker"]
        self._statistiche.conta("vai_al_marker")
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
            self._riscontro("fuori_dal_loop", _("{file} è fuori dal loop: si suona solo fra il punto A e il punto B.").format(file=brano.nome_del_file))
            return False
        self._suona(dati["playlist"], brano, sottobrano=numero, inizio=marker["tempo"])
        self.scrivi(_("Dal marker {nome}, {tempo}.").format(nome=marker["nome"], tempo=durata_lunga(marker["tempo"])))
        return True

    def _rinfresca_i_marker(self, k):
        """Dopo un cambio ai marker di una chiave, rinfresca nella plancia
        tutte le voci di quel file, in ogni playlist e cartella: etichetta,
        ramo e marker che mostra. Il fuoco su un marker rinato si ritrova
        dal suo tempo, quello su un capitolo dal suo numero (1.98.1). Prima
        si raccolgono le voci, poi si rifanno: rifacendo una voce i suoi
        marker spariscono, e non vanno piu' toccati."""
        corrente = self._voce_corrente()
        dati_correnti = self._dati(corrente) or {}
        tempo_corrente = dati_correnti["marker"]["tempo"] if dati_correnti.get("tipo") == "marker" else None
        capitolo_corrente = dati_correnti.get("numero") if dati_correnti.get("tipo") == "capitolo" else None
        rinasce = tempo_corrente is not None or capitolo_corrente is not None
        genitore_del_fuoco = self.albero.GetItemParent(corrente) if rinasce else None
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
            # Il ramo resta anche per i capitoli (1.93.0).
            ha_figli = ha_marker or bool(self._capitoli_della_voce(dati))
            self.albero.SetItemText(voce, self._etichetta(dati))
            fuoco_dentro = genitore_del_fuoco is not None and genitore_del_fuoco == voce
            if fuoco_dentro:
                # Il marker o il capitolo col fuoco sta per rinascere: il
                # fuoco passa un attimo sul brano, e poi lo ritrova.
                self._seleziona(voce)
            aperta = self.albero.IsExpanded(voce)
            self.albero.DeleteChildren(voce)
            dati["caricato"] = False
            self.albero.SetItemHasChildren(voce, ha_figli)
            if not (aperta and ha_figli):
                continue
            self._carica(voce, dati)
            self.albero.Expand(voce)
            if fuoco_dentro:
                if capitolo_corrente is not None:
                    figlio = next((v for v in self._figli(voce) if (self._dati(v) or {}).get("tipo") == "capitolo"
                        and self._dati(v).get("numero") == capitolo_corrente), None)
                else:
                    figlio = next((v for v in self._figli(voce)
                        if abs((self._dati(v) or {}).get("marker", {}).get("tempo", float("inf")) - tempo_corrente) < 1e-6), None)
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
        """Y: il fuoco della plancia va sul marker raggiunto, aprendo i
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

    def _trova_voce_che_suona(self, fino_al_sottobrano=False):
        """La voce della plancia di cio' che suona, caricando la playlist o
        aprendo le cartelle se serve; None se non c'e', per esempio per un
        file aperto con Apri file. Con fino_al_sottobrano apre anche i
        sottobrani di un SID chiuso, come vuole F8 (2.6.6); senza, come per
        l'inseguimento e la ripresa all'avvio, resta sul SID: aprirli da soli
        cambierebbe il giro, che segue i rami aperti."""
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
        if fino_al_sottobrano:
            return self._apri_fino_al_sottobrano(voce, self.motore.sottobrano)
        # Se i sottobrani del SID sono aperti, la voce e' quella del sottobrano che suona.
        if voce is not None and self.albero.IsExpanded(voce):
            voce = next((v for v in self._figli(voce) if self._dati(v).get("tipo") == "sottobrano" and self._dati(v).get("numero") == self.motore.sottobrano), voce)
        return voce

    def _apri_fino_al_sottobrano(self, voce, numero):
        """La voce del sottobrano numero, sotto quella del suo SID o file
        delle console, aprendone i sottobrani se sono chiusi; la voce data se
        non ne ha, se numero e' None o se non lo trova. Fino alla 2.6.5 F8 e
        Maiuscolo con H, con i sottobrani chiusi, si fermavano sul file
        (Gabriele)."""
        dati = (self._dati(voce) or {}) if voce is not None else {}
        if numero is None or dati.get("tipo") not in ("brano", "file") or not self._ha_sottobrani(dati["brano"]):
            return voce
        self.albero.Expand(voce)
        return next((v for v in self._figli(voce) if (self._dati(v) or {}).get("tipo") == "sottobrano" and self._dati(v).get("numero") == numero), voce)

    def _vai_al_brano(self):
        corrente = self.coda.corrente
        # Anche da fermi, il brano corrente (issue 39).
        if not corrente:
            self._riscontro("niente_da_suonare", _("Non sta suonando niente."))
            return
        voce = self._trova_voce_che_suona(fino_al_sottobrano=True)
        if voce is None:
            self._riscontro("niente_da_suonare", _("{file} non è nella plancia: è stato aperto con Apri file.").format(file=corrente.nome_del_file))
            return
        self.albero.EnsureVisible(voce)
        self._seleziona(voce)
        self._riscontro("vai_al_brano", _("Selezione su {voce}.").format(voce=self._nome_della_voce(voce)))
        self.albero.SetFocus()

    # Il segnalibro, H (Gabriele, 28 ottobre 2026, issue 37, 2.2.0): uno per
    # tutto MeTeOra, diverso dal punto da riprendere dei file lunghi, che e'
    # l'ultimo ascoltato. Per esempio si segna un audiolibro, si ascolta
    # altro, si chiude, e il giorno dopo il segnalibro riporta al libro. Sta
    # nelle impostazioni: il file, il punto, la durata se si sa, il sottobrano
    # e la lista da cui suonava, perche' si torni a suonare nello stesso giro.

    def _frase_del_segnalibro(self, segno):
        """Canzone.mp3, a 12:34 di 45:00, nella playlist Libri."""
        # Traduttori: i pezzi della frase del segnalibro, come Canzone.mp3, a 12:34 di 45:00, nella playlist Libri.
        punto = _("a {tempo} di {durata}").format(tempo=tempo(segno["posizione"]), durata=tempo(segno["durata"])) if segno["durata"] else _("a {tempo}").format(
            tempo=tempo(segno["posizione"]))
        parti = [os.path.basename(segno["percorso"]), punto]
        if segno["sottobrano"] is not None:
            parti.append(_("sottobrano {numero}").format(numero=segno["sottobrano"]))
        if segno["lista"] == "preferiti":
            parti.append(_("nei Preferiti"))
        elif segno["lista"] == "playlist":
            parti.append(_("nella playlist {nome}").format(nome=segno["nome"]))
        elif segno["lista"] == "cartella":
            parti.append(_("nella cartella {nome} con le sottocartelle").format(nome=os.path.basename(segno["nome"].rstrip(chr(92))) or segno["nome"]))
        else:
            cartella = os.path.dirname(segno["percorso"])
            parti.append(_("nella cartella {nome}").format(nome=os.path.basename(cartella.rstrip(chr(92))) or cartella))
        return ", ".join(parti)

    def _comando_segnalibro(self):
        """H (issue 37): dov'e' il segnalibro, alla sintesi e al braille dei
        sottotitoli e nella console, come gli altri tasti da soli."""
        segno = self.impostazioni["segnalibro"]
        if not segno:
            self._riporta(_("Nessun segnalibro: Ctrl e Maiuscolo con H lo mettono sul brano che suona."), "segnalibro")
            return
        self._riporta(_("Segnalibro su {segnalibro}. Maiuscolo con H ci torna.").format(segnalibro=self._frase_del_segnalibro(segno)), "segnalibro")

    def _comando_metti_il_segnalibro(self):
        """Ctrl e Maiuscolo con H: il segnalibro sul brano corrente, al punto
        in cui e', con la lista da cui suona; quello di prima si riscrive. Da
        fermi, dall'inizio, dove sta la testina dopo lo stop (issue 39)."""
        brano, pl = self.coda.corrente, self.coda.playlist
        if brano is None:
            self._riscontro("non_disponibile", _("Niente da segnare: il segnalibro si mette sul brano che suona."))
            return
        in_corso = bool(self.motore.in_corso) and os.path.normcase(self.motore.in_corso) == os.path.normcase(brano.percorso)
        durata = self.motore.durata if in_corso else None
        if durata is None:
            durata = self._durata_senza_il_lettore(brano)
        segno = {
            "percorso": brano.percorso,
            "posizione": round(float(self.motore.posizione or 0.0), 2) if in_corso else 0.0,
            "durata": round(float(durata), 2) if durata else None,
            "sottobrano": (self.motore.sottobrano if in_corso and self.motore.sottobrani else brano.sottobrano),
            "lista": "disco", "nome": "", "indice": -1,
        }
        if pl is self.archivio.preferiti or (pl is not None and not pl.temporanea and pl in self.archivio.playlist):
            indice = pl.indice(brano)
            segno.update(lista="preferiti" if pl is self.archivio.preferiti else "playlist", nome="" if pl is self.archivio.preferiti else pl.nome,
                indice=-1 if indice is None else indice)
        elif pl is not None and pl.temporanea and pl.cartella and getattr(pl, "ricorsiva", False):
            segno.update(lista="cartella", nome=pl.cartella)
        prima = self.impostazioni["segnalibro"]
        self.impostazioni["segnalibro"] = segno
        self._salva_impostazioni()
        frase = self._frase_del_segnalibro(segno)
        if prima:
            self._riscontro("segnalibro_messo", _("Segnalibro riscritto su {segnalibro}.").format(segnalibro=frase))
        else:
            self._riscontro("segnalibro_messo", _("Segnalibro su {segnalibro}. Maiuscolo con H ci torna.").format(segnalibro=frase))

    def _comando_togli_il_segnalibro(self):
        """Ctrl con H: il segnalibro non c'e' piu'."""
        segno = self.impostazioni["segnalibro"]
        if not segno:
            self._riscontro("non_disponibile", _("Nessun segnalibro da togliere."))
            return
        self.impostazioni["segnalibro"] = {}
        self._salva_impostazioni()
        self._riscontro("segnalibro_tolto", _("Segnalibro tolto: era su {segnalibro}.").format(segnalibro=self._frase_del_segnalibro(segno)))

    def _comando_vai_al_segnalibro(self):
        """Maiuscolo con H: il fuoco della plancia sul brano del segnalibro,
        aprendo tutti i suoi contenitori, fino al sottobrano di un SID (2.6.6),
        e il brano suona dal punto segnato,
        nella lista da cui suonava; se quella non c'e' piu', dalla cartella
        del file."""
        segno = self.impostazioni["segnalibro"]
        if not segno:
            self._riscontro("non_disponibile", _("Nessun segnalibro: Ctrl e Maiuscolo con H lo mettono sul brano che suona."))
            return
        if not os.path.isfile(segno["percorso"]):
            self._riscontro("errore", _("Il file del segnalibro non c'è più: {percorso}.").format(percorso=segno["percorso"]))
            return
        pl, brano, voce = self._dove_sta_il_segnalibro(segno)
        if brano is None:
            self._riscontro("errore", _("Non ritrovo {file} nella sua cartella.").format(file=os.path.basename(segno["percorso"])))
            return
        voce = self._apri_fino_al_sottobrano(voce, segno["sottobrano"])
        if voce is not None:
            self.albero.EnsureVisible(voce)
            self._seleziona(voce)
            self.albero.SetFocus()
        if not self.coda.nel_loop(pl, brano):
            self._riscontro("fuori_dal_loop", _("{file} è fuori dal loop: si suona solo fra il punto A e il punto B.").format(file=brano.nome_del_file))
            return
        self._suona(pl, brano, "al_segnalibro", sottobrano=segno["sottobrano"], inizio=segno["posizione"])
        if segno["posizione"]:
            self.scrivi(_("Dal segnalibro, a {tempo}.").format(tempo=tempo(segno["posizione"])))

    def _dove_sta_il_segnalibro(self, segno):
        """(playlist, brano, voce della plancia) del segnalibro: nella sua
        playlist o nei Preferiti, se ci sono ancora e lo contengono; altrimenti
        dalla cartella del file, aperta nella plancia, e con le sottocartelle
        se suonava cosi'. La voce e' None se la plancia non lo mostra."""
        chiave = pulizia.norm(segno["percorso"])
        if segno["lista"] in ("preferiti", "playlist"):
            pl = self.archivio.preferiti if segno["lista"] == "preferiti" else next((p for p in self.archivio.playlist if p.nome == segno["nome"]), None)
            brano = None
            if pl is not None:
                indice = segno["indice"]
                if 0 <= indice < len(pl.brani) and pulizia.norm(pl.brani[indice].percorso) == chiave:
                    brano = pl.brani[indice]
                else:
                    brano = next((b for b in pl.brani if pulizia.norm(b.percorso) == chiave), None)
            if brano is not None:
                nodo = self.nodo_preferiti if pl is self.archivio.preferiti else self._nodo_della_playlist(pl)
                voce = None
                if nodo is not None:
                    self.albero.Expand(self.nodo_playlist)
                    if self._dati(nodo).get("caricato") is False:
                        self._carica(nodo, self._dati(nodo))
                    self.albero.Expand(nodo)
                    voce = next((v for v in self._figli(nodo) if (self._dati(v) or {}).get("brano") is brano), None)
                return pl, brano, voce
        cartella = os.path.dirname(segno["percorso"])
        nodo = self._apri_fino_a(cartella)
        voce = None
        if nodo is not None:
            voce = next((v for v in self._figli(nodo) if (dati := self._dati(v) or {}).get("brano") is not None
                and pulizia.norm(dati["brano"].percorso) == chiave), None)
        if segno["lista"] == "cartella":
            pl = self._playlist_ricorsiva(segno["nome"])
            brano = next((b for b in pl.brani if pulizia.norm(b.percorso) == chiave), None) if pl is not None else None
            if brano is not None:
                return pl, brano, voce
        if voce is not None:
            dati = self._dati(voce)
            return dati["playlist"], dati["brano"], voce
        pl = self._temporanea(cartella)
        return pl, next((b for b in pl.brani if pulizia.norm(b.percorso) == chiave), None), None

    # Dove sono, l'apostrofo (Gabriele, 20 ottobre 2026, tappa 14 b).

    def _comando_dove_sono(self):
        """L'apostrofo: il tempo, il brano e la lista di cio' che suona, in
        quest'ordine, e in fondo solo quello che c'e', per esempio la pausa,
        il capitolo o la velocita' cambiata. La riga si riscrive a ogni
        pressione e va anche alla sintesi e al braille scelti per sottotitoli
        e karaoke, senza l'ora; il fuoco resta dov'e', anche nel video. Se non
        suona niente, come F8, ma la frase va anche alla sintesi e al braille,
        come la riga. Durante una dissolvenza parla del brano che entra,
        quello della coda."""
        brano = self.coda.corrente
        if brano is not None:
            self._risveglia_il_fermo()
        if not brano or not self.motore.in_corso:
            testo = _("Non sta suonando niente.")
            self._riscontro("niente_da_suonare", testo)
        else:
            parti = [self._tempo_di_dove_sono(brano), brano.nome_del_file, *self._lista_di_dove_sono(self.coda.playlist, brano)]
            if brano.saltato:
                # Traduttori: il brano di Dove sono, che l'avanzamento salta.
                parti.append(_("saltato"))
            testo = f"{', '.join(parti + self._aggiunte_di_dove_sono())}."
            self._riscontro("dove_sono", testo, "dove_sono")
        # Anche sulla barra la riga nuova prende il posto di quella di prima,
        # se e' ancora in fila o sulla barra: i dati vecchi non si leggono
        # dopo i nuovi, e i sottotitoli in fila restano. E anche a voce: la
        # voce di Windows, che da sola non interrompe, accodava le pressioni
        # ravvicinate (ritocco della 1.105.0).
        self._a_voce_e_in_braille(testo)

    def _a_voce_e_in_braille(self, testo):
        """Il testo alla sintesi e al braille scelti per sottotitoli e karaoke,
        al posto del rapporto di prima, se e' ancora in fila o sulla barra."""
        self._braille.togli(self._rapporto_in_braille)
        self._rapporto_in_braille = self._ai_testi_letti(testo, interrompi=True)

    def _riporta(self, testo, categoria):
        """Il tasto da solo, issue 38 (2.0.0): il valore del suo controllo,
        con i limiti, nella console, dove riscrive la riga della sua famiglia,
        e alla sintesi e al braille dei sottotitoli, come Dove sono; senza
        suono, perche' parla, e senza spostare il fuoco. Con uno speaker Cast
        le famiglie di SOLO_SUL_PC dicono anche che li' non valgono (2.6.2)."""
        self._domanda_viva = None
        lettore = self.motore.lontano
        if categoria in SOLO_SUL_PC and lettore is not None:
            testo += " " + _("Su {nome} non vale: vale sulle schede del PC.").format(nome=lettore.nome)
        self.scrivi(testo, categoria)
        self._a_voce_e_in_braille(testo)

    def _tempo_di_dove_sono(self, brano):
        """1:23 di 4:56, mancano 3:33. Il mancante si conta dai secondi interi
        che la riga dice, cosi' torna con la sottrazione di chi ascolta."""
        posizione, durata = self.motore.posizione, self.motore.durata
        if durata is None:
            durata = self._durata_senza_il_lettore(brano)
        if posizione is None:
            # Subito dopo l'avvio, o nell'attesa del SID dopo un salto, il
            # lettore non dice ancora il punto.
            return _("il tempo non si sa ancora, dura {durata}").format(durata=tempo(durata)) if durata else _("il tempo non si sa ancora")
        if durata is None:
            return _("{posizione}, la durata non si sa").format(posizione=tempo(posizione))
        return _("{posizione} di {durata}, mancano {mancano}").format(posizione=tempo(posizione), durata=tempo(durata),
            mancano=tempo(max(0, int(durata) - int(posizione))))

    def _durata_senza_il_lettore(self, brano):
        """La durata di cio' che suona quando il lettore non la dice: quella
        del sottobrano, se il database dei SID o delle console la sa, e
        altrimenti quella dello schedario, come nella plancia."""
        numero, quanti = self.motore.sottobrano, self.motore.sottobrani
        if quanti and numero:
            durate = sottobrani.durate(brano.percorso) or []
            return durate[numero - 1] if numero <= len(durate) else None
        return self.schedario.durata(brano)

    def _lista_di_dove_sono(self, pl, brano):
        """Il posto del brano nella lista, contato come la plancia: con un
        filtro fra i brani che lo passano, e senza fra tutti, saltati
        compresi. Con un brano solo, solo il nome della lista; una selezione
        suonata con X dice 3 di 12 della selezione."""
        nome = self._nome_della_lista(pl)
        indice = pl.indice(brano)
        if indice is None:
            # Tolto dalla lista mentre suona: il nome viene da
            # _nome_della_lista, e si confronta con i suoi testi.
            if nome == _("Preferiti"):
                return [_("non è più nei Preferiti")]
            if nome == _("Risultati"):
                return [_("non è più nei Risultati")]
            # Traduttori: lista e' come playlist Libri, selezione o cartella Musica.
            return [_("non è più nella {lista}").format(lista=nome)]
        if getattr(pl, "selezione", False):
            return [_("{numero} di {quanti} della selezione").format(numero=indice + 1, quanti=len(pl.brani)) if len(pl.brani) > 1 else nome]
        if self._filtro_di(pl) is not None:
            passano = [b for b in pl.brani if self._ammesso(pl, b)]
            numero = next((n for n, b in enumerate(passano) if b is brano), None)
            if numero is None:
                # Il filtro e' arrivato dopo che il brano e' partito.
                return [_("fuori dal filtro, {numero} di {quanti} in tutto").format(numero=indice + 1, quanti=len(pl.brani)), nome]
            return [_("{numero} di {quanti} col filtro").format(numero=numero + 1, quanti=len(passano)), nome]
        # Traduttori: il posto del brano nella lista, come 3 di 12.
        return [_("{numero} di {quanti}").format(numero=indice + 1, quanti=len(pl.brani)), nome] if len(pl.brani) > 1 else [nome]

    def _nome_della_lista(self, pl, sottocartelle=True):
        """La lista da cui suona un brano, detta con il nome che ha nella
        plancia: Preferiti, playlist X, Risultati, selezione, cartella X o
        unita' E:, con le sottocartelle se suona tutta, o file aperto (tappa
        14 b). La usa anche la riga In riproduzione (1.105.1), con
        sottocartelle falso: con le sottocartelle lo dice solo Dove sono."""
        if pl is self.archivio.preferiti:
            return _("Preferiti")
        if not pl.temporanea:
            # Anche una playlist eliminata mentre suonava.
            return _("playlist {nome}").format(nome=pl.nome)
        if pl is self.risultati or getattr(pl, "risultati", False):
            return _("Risultati")
        if getattr(pl, "selezione", False):
            # Traduttori: la lista dei brani scelti nella plancia e suonati con X.
            return _("selezione")
        if pl.cartella:
            con_le_sottocartelle = sottocartelle and getattr(pl, "ricorsiva", False)
            # Un'unita' suonata con X ha per nome la radice, E:\.
            if re.fullmatch(r"[A-Za-z]:\\?", pl.cartella):
                unita = pl.cartella[:2].upper()
                return _("unità {unita} con le sottocartelle").format(unita=unita) if con_le_sottocartelle else _("unità {unita}").format(unita=unita)
            return _("cartella {nome} con le sottocartelle").format(nome=pl.nome) if con_le_sottocartelle else _("cartella {nome}").format(nome=pl.nome)
        return pl.nome

    def _aggiunte_di_dove_sono(self):
        """In fondo alla riga, solo quando ci sono: la pausa; il sottobrano o
        il capitolo; ripetizione, riproduzione casuale, timer, loop A-B e
        muto; velocita' e tono diversi dal normale, con i decimali col punto."""
        motore, imp = self.motore, self.impostazioni
        parti = [_("in pausa")] if motore.in_pausa else []
        if motore.sottobrani and motore.sottobrani > 1:
            parti.append(_("sottobrano {numero} di {quanti}").format(numero=motore.sottobrano, quanti=motore.sottobrani))
        elif (capitolo := self._capitolo_di_dove_sono()) is not None:
            parti.append(capitolo)
        if imp["ripetizione"] != "spenta":
            # Traduttori: ripetizione e' quale, come del brano o della lista.
            parti.append(_("ripetizione {ripetizione}").format(ripetizione=valori.RIPETIZIONI[imp["ripetizione"]]))
        if imp["casuale"]:
            parti.append(_("riproduzione casuale"))
        if (timer := self._timer_di_dove_sono()) is not None:
            parti.append(timer)
        if self.coda.intervallo() is not None:
            parti.append(_("loop A-B"))
        if motore.muto:
            # Traduttori: il volume tolto, in fondo alla riga di Dove sono.
            parti.append(_("muto"))
        if motore.velocita != 1:
            parti.append(_("velocità {velocita}").format(velocita=valori.scrivi_velocita(motore.velocita)))
        if motore.tono:
            # Il segno in parole, come l'ha scritto Gabriele: tono piu' 2 semitoni.
            semitoni = abs(motore.tono)
            if motore.tono > 0:
                parti.append(plurale(semitoni, "tono più {n} semitono", "tono più {n} semitoni"))
            else:
                parti.append(plurale(semitoni, "tono meno {n} semitono", "tono meno {n} semitoni"))
        return parti

    def _capitolo_di_dove_sono(self):
        """Capitolo 3 di 12: il titolo, per gli audiolibri e i film che ne
        hanno; None senza capitoli, o finche' il lettore non dice il punto."""
        posizione = self.motore.posizione
        elenco = self._capitoli_in_corso() if posizione is not None else []
        if not elenco:
            return None
        attuale = capitolo_attuale(elenco, posizione)
        titolo = elenco[attuale][1]
        if titolo:
            return _("capitolo {numero} di {quanti}: {titolo}").format(numero=attuale + 1, quanti=len(elenco), titolo=titolo)
        return _("capitolo {numero} di {quanti}").format(numero=attuale + 1, quanti=len(elenco))

    def _timer_di_dove_sono(self):
        """Il timer di spegnimento, se c'e': fra quanti minuti, alla fine del
        brano, o scaduto mentre la musica sfuma."""
        if self._inizio_della_sfumatura is not None:
            return _("timer scaduto, la musica sfuma")
        if self._timer_a_fine_brano:
            return _("timer alla fine del brano")
        if self._timer_scade is not None:
            # Traduttori: minuti e' come 5 minuti.
            return _("timer fra {minuti}").format(minuti=_minuti(max(1, math.ceil((self._timer_scade - self._adesso()) / 60))))
        return None

    # La durata residua, Maiuscolo con l'apostrofo (Gabriele, 20 ottobre 2026, tappa 14 d).

    def _comando_durata_residua(self):
        """Maiuscolo con l'apostrofo: quanto manca e quanto e' passato di cio'
        che l'avanzamento suonera', con il totale, la percentuale ascoltata e
        l'ora di fine prevista, poi il brano e la lista come in Dove sono. Il
        campo e' quello di _seguente_automatico: se decide la plancia, le sue
        voci suonabili che si vedono dalla prima della lista che suona in
        giu', anche nelle playlist, nelle cartelle e nei sottobrani aperti
        dopo, o con la casuale tutte; altrimenti la lista o il loop. Come Dove
        sono, la riga si riscrive a ogni pressione e va alla sintesi e al
        braille dei sottotitoli, e il fuoco resta dov'e'. Se non suona niente,
        come F8, ma la frase va anche alla sintesi e al braille, come in Dove
        sono."""
        pl, brano = self._brano_che_suona()
        if brano is not None and pl is not None:
            self._risveglia_il_fermo()
        if brano is None or pl is None or not self.motore.in_corso:
            testo = _("Non sta suonando niente.")
            self._riscontro("niente_da_suonare", testo)
        else:
            testo = self._frase_della_durata_residua(pl, brano)
            self._riscontro("durata_residua", testo, "durata_residua")
        # Anche sulla barra la riga nuova prende il posto di quella di prima,
        # e a voce, come Dove sono: la voce di Windows accodava le pressioni.
        # Anche la frase di F8, come in Dove sono (ritocco della 1.110.0).
        self._braille.togli(self._durata_residua_in_braille)
        self._durata_residua_in_braille = self._ai_testi_letti(testo, interrompi=True)

    def _brano_che_suona(self):
        """(playlist, brano) di cio' che suona: quelli della coda, o al
        passaggio della dissolvenza quelli del brano preparato, che il motore
        ha gia' fatto entrare mentre la coda e' ancora su quello che esce,
        finche' _passaggio non la sposta."""
        pl, brano = self.coda.playlist, self.coda.corrente
        preparato, in_corso = self._preparato, self.motore.in_corso
        if preparato is not None and brano is not None and in_corso == preparato[1].percorso and in_corso != brano.percorso:
            return preparato[0], preparato[1]
        return pl, brano

    def _voci_in_vista(self, voce=None):
        """Le voci che si vedono nella plancia, nell'ordine della freccia giu':
        come _tutte_le_voci con _visibile, ma senza entrare nei rami chiusi,
        che dopo Alt con F9 possono avere centinaia di migliaia di voci."""
        for figlio in self._figli(voce or self.albero.GetRootItem()):
            yield figlio
            if self.albero.IsExpanded(figlio):
                yield from self._voci_in_vista(figlio)

    def _campo_della_durata_residua(self, pl, brano):
        """Cio' che l'avanzamento suonera' prima e dopo il brano che suona,
        come lo sceglie _seguente_automatico: (prima, dopo, esclusi, plancia,
        fuori). prima e dopo sono posti suonabili (playlist, brano,
        sottobrano), senza il brano che suona; esclusi i saltati lasciati
        fuori; plancia e' vero se decide la plancia; fuori e' vero se il brano
        non e' piu' nella lista o sta fuori dal loop, e allora tutta la lista,
        o il loop, viene dopo, perche' la Coda riparte dal suo primo brano. I
        brani nascosti dal filtro non contano, come nell'etichetta della
        playlist. Se decide la plancia, senza la riproduzione casuale prima
        comincia dalla prima voce della lista che suona: l'avanzamento va
        solo avanti, e le voci aperte sopra, come i Preferiti in cima, non
        le ha suonate e non le suonera'; con la ripetizione della lista
        tornano nel giro dopo. La casuale invece pesca fra tutte le voci che
        si vedono, e le conta tutte."""
        loop = self.coda.intervallo(pl)
        voce = None if loop is not None or getattr(pl, "selezione", False) else self._voce_che_suona(brano=brano)
        prima, dopo, esclusi = [], [], 0
        if voce is not None:
            dentro = prima if self.impostazioni["casuale"] else None
            for v in self._voci_in_vista():
                if v == voce:
                    dentro = dopo
                    continue
                dati = self._dati(v) or {}
                if dentro is None:
                    # Sopra la lista che suona: non conta, nemmeno fra i saltati.
                    if dati.get("playlist") is not pl or dati.get("tipo") not in ("brano", "file", "sottobrano"):
                        continue
                    dentro = prima
                if self._suonabile_in_plancia(v):
                    dentro.append((dati["playlist"], dati["brano"], dati.get("numero")))
                elif dati.get("tipo") in ("brano", "file", "sottobrano") and dati["brano"].saltato:
                    # Un SID saltato e aperto conta con i suoi sottobrani, non da solo.
                    esclusi += not (dati["tipo"] != "sottobrano" and self.albero.IsExpanded(v) and self._ha_sottobrani(dati["brano"]))
            return prima, dopo, esclusi, True, False
        primo, ultimo = loop or (0, len(pl.brani) - 1)
        indice = pl.indice(brano)
        fuori = indice is None or not primo <= indice <= ultimo
        for i in range(primo, ultimo + 1):
            altro = pl.brani[i]
            if altro is brano or not self.coda.ammesso(pl, altro):
                continue
            if altro.saltato:
                esclusi += 1
            else:
                (dopo if fuori or i > indice else prima).append((pl, altro, None))
        return prima, dopo, esclusi, False, fuori

    def _durata_nel_conto(self, brano, numero=None):
        """La durata di un posto della durata residua, dalla scheda; None se
        non si sa. Per un SID o un file delle console conta il sottobrano che
        il motore suonera', numero, quello del brano o l'iniziale, di cui la
        scheda tiene la durata come durata del file; se il database non la
        sa, i secondi a cui il motore lo ferma. Cosi' i None di durate_sid
        non arrivano mai a una somma."""
        scheda = self.schedario.scheda(brano.percorso)
        if scheda is None:
            return None
        if scheda.get("sottobrani") and formati.ha_sottobrani(brano.percorso):
            numero = numero or brano.sottobrano
            if numero is None:
                durata = scheda.get("durata")
            else:
                durate = scheda.get("durate_sid") or []
                durata = durate[numero - 1] if numero <= len(durate) else None
            return DURATA_SID_PREDEFINITA if durata is None else durata
        return scheda.get("durata")

    def _durata_di_cio_che_suona(self, brano):
        """La durata del brano che suona: per un SID o un file delle console
        quella del sottobrano del motore, come la usa il motore; altrimenti
        quella dello schedario, perche' per l'AAC grezzo il motore ha solo la
        stima di libmpv, e se lo schedario non la sa quella del motore, se e'
        credibile, come nelle statistiche."""
        if self.motore.sottobrani and self.motore.sottobrano:
            return durata_del_sottobrano(brano.percorso, self.motore.sottobrano)
        durata = self._durata_nel_conto(brano)
        if durata is None:
            durata = credibile(self.motore.durata, brano.percorso, (self.schedario.scheda(brano.percorso) or {}).get("dim"))
        return durata

    def _il_brano_si_ripete(self, pl, brano):
        """Vero se con la ripetizione del brano il brano che suona si ripete:
        non se e' saltato, tolto dalla lista o nascosto dal filtro, che vanno
        avanti come sempre."""
        return (self.impostazioni["ripetizione"] == "brano" and not brano.saltato and self.coda.ammesso(pl, brano)
            and any(b is brano for b in pl.brani))

    def _ora_fra(self, secondi):
        """L'ora, in ore e minuti, fra tanti secondi da adesso."""
        return (datetime.datetime.now() + datetime.timedelta(seconds=secondi)).strftime("%H:%M")

    def _ora_di_fine(self, secondi):
        """L'ora di fine della durata residua, fra tanti secondi: se non e'
        oggi, con di domani o con la data, perche' una lista lunga finisce
        anche fra qualche giorno."""
        adesso = datetime.datetime.now()
        quando = adesso + datetime.timedelta(seconds=secondi)
        giorni = (quando.date() - adesso.date()).days
        ora = quando.strftime("%H:%M")
        if giorni <= 0:
            return ora
        return _("{ora} di domani").format(ora=ora) if giorni == 1 else _("{ora} di {data}").format(ora=ora, data=statistiche.data(quando))

    def _frase_della_durata_residua(self, pl, brano):
        """La riga della durata residua: prima i numeri, poi l'ora di fine
        prevista o la pausa, poi il brano e la lista come in Dove sono, e in
        fondo, quando ci sono, i rami aperti della plancia, i saltati
        esclusi, i brani senza durata, cosa succede dopo e il timer. Il
        mancante e' il totale meno il trascorso, in secondi interi, cosi' i
        conti di chi ascolta tornano; a velocita' diversa da 1 si aggiunge il
        tempo vero di ascolto, subito dopo il mancante, come nell'esempio di
        Gabriele, e il totale va dopo, con in tutto; la dissolvenza non si
        toglie. Con la riproduzione casuale a mazzo il trascorso sono i
        brani gia' usciti e il mancante quelli che ci restano, piu' quelli
        che dopo Z la storia fara' risuonare; con la casualita' totale, che
        non finisce mai, il resto del brano e il totale."""
        motore, imp = self.motore, self.impostazioni
        prima, dopo, esclusi, plancia, fuori = self._campo_della_durata_residua(pl, brano)
        altri = prima + dopo
        durate = [self._durata_nel_conto(b, numero) for _pl, b, numero in altri]
        durata = self._durata_di_cio_che_suona(brano)
        posizione = max(0.0, motore.posizione or 0.0)
        if durata is not None:
            posizione = min(posizione, durata)
        resto = None if durata is None else durata - posizione
        modello = imp["modello_casuale"] if imp["casuale"] and altri else None
        aggiunti = []
        if modello not in (None, "totale"):
            # Dopo Z l'avanzamento ripercorre prima la storia in avanti, e solo
            # poi pesca dal mazzo: quei brani suoneranno di nuovo, anche se ne
            # sono gia' usciti, e contano fra quelli che restano. Un posto
            # della storia che non e' fra gli altri, come il brano che suona in
            # un giro nuovo, si aggiunge.
            avanti = self._storia_in_avanti()
            # Le chiavi sono quelle del mazzo, anche senza sottobrano, che e'
            # la voce di un SID chiuso: insiemi, perche' la storia tiene fino a
            # mille posti e la plancia aperta migliaia di voci.
            di_avanti = {(id(p), id(b), n) for p, b, n in avanti} | {(id(p), id(b), None) for p, b, _n in avanti}
            chiavi = [(id(p), id(b), numero) for p, b, numero in altri]
            usciti = [chiave in self._mazzo and chiave not in di_avanti for chiave in chiavi]
            degli_altri = set(chiavi)
            aggiunti = [(p, b, n) for p, b, n in avanti if (id(p), id(b), None) not in degli_altri and (id(p), id(b), n) not in degli_altri]
            passati = [d for d, uscito in zip(durate, usciti, strict=True) if uscito]
            futuri = [d for d, uscito in zip(durate, usciti, strict=True) if not uscito]
            futuri += [self._durata_nel_conto(b, numero) for _pl, b, numero in aggiunti]
        else:
            passati, futuri = durate[:len(prima)], durate[len(prima):]
        mai_letti = {b.percorso for b in [brano, *(b for _pl, b, _numero in altri + aggiunti)] if self.schedario.scheda(b.percorso) is None}
        if mai_letti:
            # Lo schedario le legge in disparte: ripremendo il tasto il conto si completa.
            self.schedario.chiedi(mai_letti)
        trascorso = sum(d for d in passati if d is not None) + posizione
        totale = trascorso + sum(d for d in futuri if d is not None) + (resto or 0.0)
        mancano = max(0, int(totale) - int(trascorso))
        senza = sum(d is None for d in passati + futuri) + (durata is None)
        nessuna = senza == len(passati) + len(futuri) + 1
        velocita = motore.velocita

        def alla_velocita(secondi):
            # Solo a velocita' diversa da 1.
            return _("alla velocità {velocita} sono {tempo}").format(velocita=valori.scrivi_velocita(velocita), tempo=tempo(secondi / velocita))

        solo = not altri
        # Il tempo vero di ascolto subito dopo il mancante, perche' non lo si
        # prenda per quello del totale, che va dopo, con in tutto.
        if velocita == 1:
            # Traduttori: quanto manca, di quanto dura tutto: come 3:00 di 10:00.
            numeri = _("{mancano} di {totale}").format(mancano=tempo(mancano), totale=tempo(totale))
        else:
            # Traduttori: alla_velocita e' come alla velocità 1.5 sono 2:00.
            numeri = _("{mancano}, {alla_velocita}, in tutto {totale}").format(mancano=tempo(mancano), alla_velocita=alla_velocita(mancano), totale=tempo(totale))
        # Traduttori: percentuale e' come 70%.
        numeri += ", " + _("trascorsi {trascorso}, {percentuale} ascoltato").format(trascorso=tempo(trascorso), percentuale=dettagli.percentuale(trascorso, totale))
        if nessuna:
            testa = _("Suona un brano solo, e la sua durata non si sa") if solo else _("Nessuna durata è nota")
        elif solo:
            if velocita == 1:
                testa = _("Suona un brano solo: mancano {mancano}").format(mancano=tempo(mancano))
            else:
                testa = _("Suona un brano solo: mancano {mancano}, {alla_velocita}").format(mancano=tempo(mancano), alla_velocita=alla_velocita(mancano))
        elif modello == "totale":
            if resto is None:
                del_brano = _("Del brano la durata non si sa")
            elif velocita == 1:
                del_brano = _("Del brano mancano {resto}").format(resto=tempo(resto))
            else:
                del_brano = _("Del brano mancano {resto}, {alla_velocita}").format(resto=tempo(resto), alla_velocita=alla_velocita(resto))
            # Traduttori: del_brano e' come Del brano mancano 2:00.
            testa = _("{del_brano}, in tutto {totale}, ordine casuale senza fine").format(del_brano=del_brano, totale=tempo(totale))
        elif modello is not None:
            # Traduttori: numeri e' come 3:00 di 10:00, trascorsi 7:00, 70% ascoltato.
            testa = _("Casuale: suonati {suonati} di {quanti}, nel mazzo restano {numeri}").format(suonati=sum(usciti) + 1, quanti=len(altri) + 1, numeri=numeri)
        else:
            # Traduttori: numeri e' come 3:00 di 10:00, trascorsi 7:00, 70% ascoltato.
            testa = _("Mancano {numeri}").format(numeri=numeri)
        # Cosa succede dopo: niente fine con il brano che si ripete o con la
        # casualita' totale; un giro che ricomincia con il loop, il mazzo
        # rimescolato e la ripetizione della lista. Il mazzo decide anche nel
        # loop: finito, si rimescola o la musica si ferma, e non si torna al
        # punto A.
        loop = self.coda.intervallo(pl)
        senza_fine = dopo_la_fine = None
        if self._il_brano_si_ripete(pl, brano) or (loop is not None and loop[0] == loop[1] and not fuori):
            senza_fine = _("il brano si ripete") if solo else _("il brano si ripete: la lista non va avanti finché la ripetizione resta accesa")
        elif modello == "totale":
            senza_fine = ""
        elif modello is not None:
            if modello == "a_giro" or imp["ripetizione"] == "lista":
                dopo_la_fine = _("poi il mazzo si rimescola")
        elif loop is not None:
            dopo_la_fine = _("il brano è fuori dal loop: poi si va al punto A") if fuori else _("poi si torna al punto A")
        elif imp["ripetizione"] == "lista":
            dopo_la_fine = _("poi si riparte dalla prima voce della plancia") if plancia else _("poi la lista ricomincia")
        if solo and dopo_la_fine:
            # Da solo, il giro nuovo e' lo stesso brano.
            senza_fine, dopo_la_fine = _("il brano si ripete"), None
        # Il timer scaduto, o alla fine di questo brano, ferma tutto prima.
        fermo = None
        if self._inizio_della_sfumatura is not None:
            fermo = _("il timer è scaduto, e la musica sta sfumando")
        elif self._timer_a_fine_brano:
            if motore.in_pausa or resto is None:
                fermo = _("il timer ferma la musica alla fine di questo brano")
            else:
                # Traduttori: ora e' come 14:30, o 14:30 di domani.
                fermo = _("il timer ferma la musica alla fine di questo brano, verso le {ora}").format(ora=self._ora_di_fine(resto / velocita))
        fine = not motore.in_pausa and not nessuna and fermo is None and senza_fine is None
        frasi = [testa]
        if motore.in_pausa:
            frasi.append(_("in pausa"))
        elif fine:
            if dopo_la_fine:
                # Traduttori: ora e' come 14:30, o 14:30 di domani.
                frasi.append(_("il giro finisce verso le {ora}").format(ora=self._ora_di_fine(mancano / velocita)))
            else:
                # Traduttori: ora e' come 14:30, o 14:30 di domani.
                frasi.append(_("finisce verso le {ora}").format(ora=self._ora_di_fine(mancano / velocita)))
        lista = self._lista_di_dove_sono(pl, brano)
        if lista[0][:1].isdigit():
            # Traduttori: posto e' il posto del brano nella lista, come 3 di 12.
            lista[0] = _("brano {posto}").format(posto=lista[0])
        frasi += lista
        if plancia and any(p is not pl for p, _b, _numero in altri):
            frasi.append(plurale(len(altri) + 1, "con i rami aperti della plancia, {n} brano in tutto", "con i rami aperti della plancia, {n} brani in tutto"))
        if fuori and altri and loop is None and modello is None and fermo is None:
            frasi.append(_("dopo si riparte dal primo brano"))
        if esclusi:
            frasi.append(plurale(esclusi, "{n} saltato escluso", "{n} saltati esclusi"))
        if senza and not nessuna:
            frasi.append(plurale(senza, "{n} brano senza durata", "{n} brani senza durata"))
        if fermo is None and (senza_fine or dopo_la_fine):
            frasi.append(senza_fine or dopo_la_fine)
        if fermo is None and self._timer_scade is not None:
            # Senza una fine, anche con un giro che ricomincia, a fermare la
            # musica sara' il timer; con la fine, solo se scade prima, e
            # allora con il ma.
            entro = self._timer_scade - self._adesso() < mancano / velocita
            if not fine or dopo_la_fine or entro:
                if fine and entro:
                    fermo = _("ma il timer ferma la musica alle {ora}").format(ora=self._ora_del_timer())
                else:
                    fermo = _("il timer ferma la musica alle {ora}").format(ora=self._ora_del_timer())
        if fermo is not None:
            frasi.append(fermo)
        return f"{', '.join(frasi)}."

    def _insegui(self):
        """Con l'inseguimento agganciato porta la selezione su cio' che suona,
        senza spostare il fuoco e senza suoni: il suono del brano nuovo c'e' gia'."""
        if not self.impostazioni["insegui"] or not self.coda.corrente:
            return
        voce = self._trova_voce_che_suona()
        if voce is not None and voce != self._voce_corrente():
            self.albero.EnsureVisible(voce)
            self._seleziona(voce)

    def _metti_l_inseguimento(self, agganciato):
        """Maiuscolo con F8 aggancia la selezione della plancia al brano che
        suona, Ctrl con F8 la sgancia (2.0.2, prima a giro)."""
        if agganciato:
            evento, frase = "insegui_acceso", _("Inseguimento agganciato: la selezione della plancia segue il brano che suona.")
        else:
            evento, frase = "insegui_spento", _("Inseguimento sganciato: la selezione resta dove la lasci.")
        if self.impostazioni["insegui"] == agganciato:
            self._riscontro(evento, _("Già così. {frase}").format(frase=frase))
            return
        self.impostazioni["insegui"] = agganciato
        self._salva_impostazioni()
        self._riscontro(evento, frase)
        if agganciato and self.motore.in_corso:
            self._insegui()

    # F9, le aperture e le chiusure (2.7.0, tappa 17): tutto su un tasto, con la
    # regola della issue 38. F9 da solo dice lo stato del ramo col fuoco;
    # Maiuscolo con F9 lo apre con tutto quello che ha dentro e Ctrl con F9 lo
    # chiude; Alt con F9 apre tutta la plancia e Ctrl e Alt con F9 la chiude;
    # Ctrl e Maiuscolo con F9 fermano un'apertura. F10 resta libero.

    def _ramo_di_lavoro(self):
        """Il ramo su cui lavora F9: la voce selezionata, o quella che la
        contiene se non ha niente dentro."""
        voce = self._voce_corrente()
        if voce.IsOk() and not self.albero.ItemHasChildren(voce):
            voce = self.albero.GetItemParent(voce)
        return voce if voce.IsOk() and voce != self.albero.GetRootItem() else None

    def _comando_stato_del_ramo(self):
        """F9 da solo: il ramo col fuoco, aperto o chiuso, con quante voci e
        quanti rami aperti ha dentro, e l'apertura in corso, se c'e'."""
        voce = self._ramo_di_lavoro()
        in_corso = self._frase_dell_apertura_in_corso()
        if voce is None:
            self._riporta(_("Qui non c'è un ramo.") + in_corso, "ramo")
            return
        nome = self._nome_della_voce(voce)
        if not self.albero.IsExpanded(voce):
            # Traduttori: il ramo della plancia, che non e' aperto.
            self._riporta(_("{nome}: chiuso.").format(nome=nome) + in_corso, "ramo")
            return
        rami, voci = self._aperti_dentro(voce)
        # Traduttori: voci e' come 12 voci, rami come 2 rami aperti.
        self._riporta(_("{nome}: aperto, con {voci} e {rami} dentro.").format(nome=nome, voci=plurale(voci, "{n} voce", "{n} voci"),
            rami=plurale(rami, "{n} ramo aperto", "{n} rami aperti")) + in_corso, "ramo")

    def _aperti_dentro(self, voce):
        """Quante voci si vedono dentro un ramo, e quanti dei rami che ha dentro
        sono aperti: si scende solo nei rami aperti. Intanto i fili del
        contatore, dello schedario e dell'esploratore cedono il passo: con
        Questo PC aperto il giro e' di 140 mila voci, e con loro a pieno
        lavoro durava tre secondi (banco della 2.7.0)."""
        rami, voci = 0, 0
        pila = [voce]
        gia_ceduto = self._cedi.is_set()
        self._cedi.set()
        try:
            while pila:
                for figlio in self._figli(pila.pop()):
                    voci += 1
                    if self.albero.IsExpanded(figlio):
                        rami += 1
                        pila.append(figlio)
        finally:
            if not gia_ceduto:
                self._cedi.clear()
        return rami, voci

    def _frase_dell_apertura_in_corso(self):
        apertura = self._apertura
        if apertura is None:
            return ""
        # Traduttori: titolo e' come Apertura di tutta la plancia; rami come 3 rami, voci come 120 voci.
        frase = " " + _("{titolo} in corso: finora {rami} e {voci}").format(titolo=apertura.titolo, rami=plurale(apertura.rami, "{n} ramo", "{n} rami"),
            voci=plurale(apertura.voci, "{n} voce", "{n} voci"))
        esploratore = apertura.esploratore
        if esploratore is not None and not esploratore.finita:
            frase += ", " + plurale(esploratore.lette, "{n} cartella letta", "{n} cartelle lette")
            if esploratore.in_lettura:
                frase += ", " + _("sto leggendo {cartella}").format(cartella=esploratore.in_lettura)
        return frase + "."

    def _chiudi_tutto(self):
        """Ctrl con F9: chiude il ramo col fuoco con tutto quello che ha dentro.
        Un'apertura in corso che lo tocca si ferma: riaprirebbe i rami appena
        chiusi."""
        voce = self._ramo_di_lavoro()
        if voce is None:
            self._riscontro("non_disponibile", _("Qui non c'è niente da chiudere."))
            return
        fermata = self._apertura is not None and self._l_apertura_tocca(voce)
        if fermata:
            self._chiudi_l_apertura()
        self._chiudi_con_tutto(voce)
        self._seleziona(voce)
        self._riscontro("chiudi_tutto", _("Chiuso tutto dentro {nome}.").format(nome=self._nome_della_voce(voce)) + (" " + _("Apertura fermata.") if fermata else ""))

    def _l_apertura_tocca(self, voce):
        """Vero se il ramo sta dentro una delle radici dell'apertura in corso,
        o la contiene."""
        apertura = self._apertura
        return any(apertura.viva(radice) and (self._sotto(voce, radice) or self._sotto(radice, voce)) for radice in apertura.radici)

    def _chiudi_con_tutto(self, voce):
        """Chiude il ramo e tutti i rami che ha dentro, che riaprendolo si
        trovano chiusi. Prima il ramo, poi quelli dentro, che intanto non si
        vedono piu': CollapseAllChildren di wx li chiude dal basso, mentre si
        vedono ancora, e con 138 mila voci aperte su Questo PC la finestra
        restava ferma 22 secondi (banco della 2.7.0)."""
        if self.albero.IsExpanded(voce):
            self.albero.Collapse(voce)
        pila = [voce]
        while pila:
            for figlio in self._figli(pila.pop()):
                if self.albero.ItemHasChildren(figlio):
                    if self.albero.IsExpanded(figlio):
                        self.albero.Collapse(figlio)
                    pila.append(figlio)

    def _chiudi_la_plancia(self):
        """Ctrl e Alt con F9, il minimo (Gabriele, 4 ottobre 2026, e 2.7.0):
        chiude tutti i rami della plancia, con tutto quello che hanno dentro;
        il fuoco va sulla voce di primo livello che conteneva quella su cui si
        era. Un'apertura in corso si ferma."""
        fermata = self._chiudi_l_apertura() is not None
        radice = self.albero.GetRootItem()
        primo = self._voce_corrente()
        while primo.IsOk() and primo != radice and self.albero.GetItemParent(primo) != radice:
            primo = self.albero.GetItemParent(primo)
        for voce in list(self._figli(radice)):
            self._chiudi_con_tutto(voce)
        if primo.IsOk() and primo != radice:
            self._seleziona(primo)
        self._riscontro("chiudi_la_plancia", _("Chiusa tutta la plancia.") + (" " + _("Apertura fermata.") if fermata else ""))

    def _apri_la_plancia(self):
        """Alt con F9, il massimo (Gabriele, 4 ottobre 2026, e 2.7.0): apre
        tutta la plancia con tutto quello che ha dentro, anche Questo PC e
        Questa rete, tranne i CD, Computer della rete, che ripete le stesse
        cartelle condivise sotto il nome dei computer, e le condivisioni
        salvate in Windows, come fa la ricerca."""
        radice = self.albero.GetRootItem()
        rami = [v for v in self._figli(radice) if self.albero.ItemHasChildren(v)]
        self._apri_in_blocco(rami, _("Apertura di tutta la plancia"), _("Apro tutta la plancia, tranne i CD, Computer della rete e le condivisioni salvate in Windows"),
            _("Aperta tutta la plancia"), "plancia_aperta", tutta=True)

    def _apri_tutto(self):
        """Maiuscolo con F9: apre la voce col fuoco e tutto quello che ha
        dentro, anche un disco intero o una cartella di rete."""
        voce = self._ramo_di_lavoro()
        if voce is None:
            self._riscontro("non_disponibile", _("Qui non c'è niente da aprire."))
            return
        nome = self._nome_della_voce(voce)
        self._apri_in_blocco([voce], _("Apertura dentro {nome}").format(nome=nome), _("Apro tutto dentro {nome}").format(nome=nome),
            _("Aperto tutto dentro {nome}").format(nome=nome), "apri_tutto")

    def _f10(self):
        """F10 da solo non ha piu' un comando (2.7.0): lo dice, invece di
        lasciarlo a Windows, che porterebbe il fuoco al menu di sistema."""
        self._statistiche.senza_comando("F10")
        self._riscontro("non_disponibile", _("Il tasto F10 non ha un comando."))

    def _ferma_l_apertura(self):
        """Ctrl e Maiuscolo con F9: ferma l'apertura in corso, e lascia aperto
        quello che ha aperto fin qui (scelta di ClaudIA, 2.7.0)."""
        apertura = self._chiudi_l_apertura()
        if apertura is None:
            self._riscontro("non_disponibile", _("Non c'è un'apertura in corso."))
            return
        # Traduttori: titolo e' come Apertura di tutta la plancia, o Apertura dentro Musica.
        self._riscontro("annullamento", _("{titolo} fermata: i rami aperti fin qui restano aperti.").format(titolo=apertura.titolo))

    def _apri_in_blocco(self, rami, titolo, inizio, fine, evento, tutta=False):
        """Apre i rami con tutto quello che hanno dentro, senza limiti (2.7.0).
        I rami del disco e della rete li legge l'esploratore, in disparte, e
        nella plancia entrano solo le cartelle con qualcosa da suonare: prima i
        dischi, poi le unita' di rete, poi Questa rete. Gli altri rami, come
        le playlist, si aprono a fette di un decimo di secondo nel filo della
        finestra. Intanto la finestra risponde, e si naviga anche dentro i
        rami che si stanno riempiendo: i tasti non fermano l'apertura, la
        fermano Ctrl e Maiuscolo con F9 o una chiusura. L'inizio si dice, con
        il suo suono, solo se il lavoro dura piu' di RITARDO_DELL_AVVIO
        secondi, e allora quello di fine aspetta che finisca (1.83.2)."""
        if self._apertura is not None:
            # Una nuova apertura prende il posto di quella in corso.
            self._chiudi_l_apertura()
        # Traduttori: inizio e' come Apro tutto dentro Musica.
        apertura = self._apertura = _Apertura(titolo, _("{inizio}: ci vuole un po', e intanto puoi navigare. Ctrl e Maiuscolo con F9 mi fermano.").format(
            inizio=inizio), fine, evento, tutta)
        dischi, rete = [], []
        freccia, self._freccia_nell_albero = self._freccia_nell_albero, False
        try:
            for ramo in rami:
                apertura.radici.append(apertura.tieni(ramo))
                self._smista(apertura, ramo, dischi, rete)
        finally:
            self._freccia_nell_albero = freccia
        radici = [percorso for percorso, _voce in dischi + rete]
        for percorso, voce in dischi + rete:
            self._radice_dell_apertura(apertura, voce, percorso)
        if radici:
            self._sentinella.guarda(*radici)
            apertura.esploratore = Esploratore(radici, self.contatore, lambda: wx.CallAfter(self._avviso_dell_apertura, apertura),
                self._cedi).avvia()
        # La prima fetta subito: un ramo piccolo finisce qui, con il suo solo
        # suono di fine.
        self._passo_dell_apertura(apertura)
        if apertura is self._apertura:
            wx.CallLater(max(1, round(RITARDO_DELL_AVVIO * 1000)), self._inizio_dell_apertura, apertura)

    def _smista(self, apertura, voce, dischi, rete):
        """Mette un ramo dove va: le cartelle e le unita' all'esploratore, come
        (percorso, voce), prima i dischi e poi la rete; Questo PC e Questa rete
        si aprono qui, e passano all'esploratore le loro voci; gli altri rami
        vanno a fette. Computer della rete e i computer, che cercano in
        disparte, si aprono come con la freccia, e basta."""
        dati = self._dati(voce) or {}
        tipo = dati.get("tipo")
        if tipo in ("pc", "rete", "computer_della_rete", "computer"):
            self._apri_se_chiuso(apertura, voce, anche_vuoto=True)
        if tipo == "pc":
            for unita in self._figli(voce):
                percorso = (self._dati(unita) or {}).get("percorso")
                if not percorso:
                    continue
                genere = tipo_di_unita(os.path.splitdrive(percorso)[0] + "\\")
                if genere == UNITA_CD:
                    continue
                (rete if genere == UNITA_DI_RETE else dischi).append((percorso, unita))
        elif tipo == "rete":
            # Come la ricerca (1.73.0): i percorsi scritti a mano, non le
            # condivisioni intere salvate in Windows. Il Samba dell'Iliadbox,
            # con decine di migliaia di cartelle di backup, lascia appesa una
            # lettura, e MeTeOra non riusciva a chiudersi finche' non scadeva
            # (collaudo della 2.7.0). Una condivisione salvata si apre tutta
            # con Maiuscolo con F9 sul suo ramo.
            for figlio in self._figli(voce):
                dati_figlio = self._dati(figlio) or {}
                if dati_figlio.get("radice_di_rete") and dati_figlio.get("a_mano"):
                    rete.append((dati_figlio["percorso"], figlio))
        elif tipo in ("cartella", "unita"):
            (rete if in_rete(dati["percorso"]) else dischi).append((dati["percorso"], voce))
        elif tipo not in ("computer_della_rete", "computer"):
            apertura.da_aprire.append(voce)

    def _radice_dell_apertura(self, apertura, voce, percorso):
        """Una cartella da cui parte l'esploratore. Se non e' ancora caricata
        la riempie l'esploratore; se lo e', le cartelle che trova si cercano
        fra quelle che ha gia'."""
        dati = self._dati(voce)
        apertura.tieni(voce, percorso)
        if dati.get("caricato") is False:
            self.albero.DeleteChildren(voce)
            dati["caricato"] = True
            dati["esplorata"] = True
            apertura.incomplete.add(pulizia.norm(percorso))

    def _inizio_dell_apertura(self, apertura):
        if apertura is self._apertura and not apertura.avviato and not self._chiusa:
            apertura.avviato = True
            self._riscontro("apri_la_plancia", apertura.inizio)

    def _avviso_dell_apertura(self, apertura):
        """L'esploratore ha degli avvisi: se non c'e' gia' una fetta in arrivo,
        se ne fa una."""
        if apertura is self._apertura and not apertura.pianificato and not self._chiusa:
            self._passo_dell_apertura(apertura)

    def _passo_dell_apertura(self, apertura):
        """Una fetta dell'apertura: gli avvisi dell'esploratore e i rami da
        aprire, per un decimo di secondo, con i fili del contatore, dello
        schedario e dell'esploratore che cedono il passo. I rami aperti qui
        non suonano: lo fa la fine."""
        apertura.pianificato = False
        if apertura is not self._apertura or self._chiusa:
            return
        attesa = self._cedi.trattenuto()
        if attesa:
            # Chi naviga ha la precedenza (2.7.1): la fetta aspetta.
            apertura.pianificato = True
            wx.CallLater(max(1, round(attesa * 1000)), self._passo_dell_apertura, apertura)
            return
        if not any(apertura.viva(radice) for radice in apertura.radici):
            # Le radici non ci sono piu', per esempio dopo Aggiorna.
            self._chiudi_l_apertura()
            return
        if apertura.esploratore is not None:
            apertura.eventi.extend(apertura.esploratore.prendi())
        fine = time.monotonic() + 0.1
        freccia, self._freccia_nell_albero = self._freccia_nell_albero, False
        self._cedi.set()
        try:
            while time.monotonic() < fine:
                if apertura.eventi:
                    self._avviso_dell_esploratore(apertura, apertura.eventi.popleft())
                elif apertura.da_aprire:
                    self._apri_un_ramo(apertura, apertura.da_aprire.popleft())
                else:
                    break
        finally:
            self._cedi.clear()
            self._freccia_nell_albero = freccia
        if not apertura.eventi and not apertura.da_aprire and apertura.esploratore is not None:
            if not apertura.esploratore.finita:
                # Si aspetta il prossimo avviso.
                return
            apertura.eventi.extend(apertura.esploratore.prendi())
        if apertura.eventi or apertura.da_aprire:
            apertura.pianificato = True
            wx.CallLater(1, self._passo_dell_apertura, apertura)
            return
        # Anche la fine, con il rinfresco delle cartelle e il conto, mentre i
        # fili cedono il passo.
        self._cedi.set()
        try:
            self._fine_dell_apertura(apertura)
        finally:
            self._cedi.clear()

    def _apri_un_ramo(self, apertura, voce):
        """Un ramo fuori dal disco e dalla rete, come una playlist o un SID: si
        apre, e i rami che ha dentro vanno in fila."""
        if not apertura.viva(voce) or not self.albero.ItemHasChildren(voce):
            return
        if (self._dati(voce) or {}).get("tipo") in ("cartella", "unita", "pc", "rete", "computer_della_rete", "computer"):
            return
        self._apri_se_chiuso(apertura, voce, anche_vuoto=True)
        figli = list(self._figli(voce))
        apertura.voci += len(figli)
        for figlio in figli:
            if self.albero.ItemHasChildren(figlio):
                apertura.da_aprire.append(apertura.tieni(figlio))

    def _apri_se_chiuso(self, apertura, voce, anche_vuoto=False):
        """Apre un ramo chiuso, se ha gia' qualcosa dentro: le cartelle
        dell'esploratore si aprono quando arriva la prima voce. Con
        anche_vuoto si apre comunque, e si carica, come con la freccia. Un
        ramo chiuso a mano durante l'apertura resta chiuso."""
        if self.albero.IsExpanded(voce) or not (anche_vuoto or self.albero.GetChildrenCount(voce, False)):
            return
        if int(voce.GetID()) in apertura.chiusi_a_mano:
            return
        self.albero.Expand(voce)
        apertura.rami += 1

    def _avviso_dell_esploratore(self, apertura, avviso):
        """Un avviso dell'esploratore: una cartella da mostrare, i file di una
        cartella, o una cartella finita. Se la cartella che lo riguarda non
        c'e' piu' nella plancia, l'avviso si lascia cadere."""
        if avviso[0] == "cartella":
            _avviso, genitore, percorso = avviso
            padre = apertura.voce(genitore)
            if padre is not None:
                self._cartella_dell_apertura(apertura, padre, percorso)
                self._apri_se_chiuso(apertura, padre)
            return
        if avviso[0] == "file":
            _avviso, cartella, (_cartelle, files) = avviso
            voce = apertura.voce(cartella)
            if voce is None:
                return
            if (self._dati(voce) or {}).get("esplorata"):
                pl = self._temporanea(cartella, files)
                self._chiedi_schede(pl)
                for brano in pl.brani:
                    figlio = self._aggiungi_voce(voce, "file", pl, brano)
                    apertura.voci += 1
                    if self.albero.ItemHasChildren(figlio):
                        apertura.da_aprire.append(apertura.tieni(figlio))
            else:
                # Una cartella caricata a mano ha gia' i suoi file: si aprono
                # quelli che hanno qualcosa dentro, come i SID.
                for figlio in self._figli(voce):
                    if (self._dati(figlio) or {}).get("tipo") == "file" and self.albero.ItemHasChildren(figlio):
                        apertura.da_aprire.append(apertura.tieni(figlio))
            self._apri_se_chiuso(apertura, voce)
            return
        cartella = avviso[1]
        apertura.incomplete.discard(pulizia.norm(cartella))
        voce = apertura.voce(cartella)
        if voce is not None and (self._dati(voce) or {}).get("esplorata") and not self.albero.GetChildrenCount(voce, False):
            self.albero.SetItemHasChildren(voce, False)

    def _cartella_dell_apertura(self, apertura, padre, percorso):
        """La voce di una cartella annunciata dall'esploratore: quella che c'e'
        gia', o una nuova, al suo posto in ordine alfabetico fra le cartelle,
        che vengono prima dei file. Una cartella che c'era ma non era
        caricata la riempie l'esploratore."""
        voce = apertura.voce(percorso)
        if voce is None and not (self._dati(padre) or {}).get("esplorata"):
            # Un ramo caricato a mano: le sue cartelle si guardano una volta.
            numero = int(padre.GetID())
            if numero not in apertura.guardati:
                apertura.guardati.add(numero)
                for figlio in self._figli(padre):
                    dati_figlio = self._dati(figlio) or {}
                    if dati_figlio.get("tipo") == "cartella":
                        apertura.tieni(figlio, dati_figlio["percorso"])
                voce = apertura.voce(percorso)
        chiave = pulizia.norm(percorso)
        if voce is None:
            dati = {"tipo": "cartella", "percorso": percorso, "caricato": True, "esplorata": True}
            voce = self._inserisci_la_cartella(apertura, padre, percorso, dati)
            self.albero.SetItemHasChildren(voce, True)
            apertura.tieni(voce, percorso)
            apertura.incomplete.add(chiave)
            apertura.voci += 1
            self.contatore.chiedi([percorso])
            return voce
        dati = self._dati(voce)
        if dati.get("caricato") is False:
            self.albero.DeleteChildren(voce)
            dati["caricato"] = True
            dati["esplorata"] = True
            apertura.incomplete.add(chiave)
        return voce

    def _inserisci_la_cartella(self, apertura, padre, percorso, dati):
        """Inserisce la cartella dopo l'ultima che l'esploratore ha messo nello
        stesso ramo: arrivano in ordine. Se non c'e', si cerca il posto fra le
        cartelle che il ramo ha."""
        testo = self._etichetta_della_cartella(percorso)
        numero = int(padre.GetID())
        precedente = apertura.ultime.get(numero)
        if not apertura.viva(precedente):
            precedente = None
            nome = os.path.basename(percorso.rstrip("\\")).casefold()
            for figlio in self._figli(padre):
                dati_figlio = self._dati(figlio) or {}
                if dati_figlio.get("tipo") != "cartella" or os.path.basename(dati_figlio["percorso"].rstrip("\\")).casefold() > nome:
                    break
                precedente = figlio
        if precedente is None:
            voce = self.albero.PrependItem(padre, testo, data=dati)
        else:
            voce = self.albero.InsertItem(padre, precedente, testo, data=dati)
        apertura.ultime[numero] = voce
        return voce

    def _fine_dell_apertura(self, apertura):
        """La fine: quanti rami e quante voci si vedono, quante cartelle si
        sono lette, e quelle che non si leggono o non rispondono."""
        self._apertura = None
        self._lascia_le_incomplete(apertura)
        # Le cartelle rimaste senza niente da suonare spariscono adesso.
        self._aggiorna_cartelle()
        esploratore = apertura.esploratore
        radici = [r for r in apertura.radici if apertura.viva(r)]
        if not radici:
            return
        evento = apertura.evento
        if not apertura.tutta and len(radici) == 1 and not self.albero.ItemHasChildren(radici[0]):
            evento, frase = "niente_da_suonare", _("Niente da suonare dentro {nome}.").format(nome=self._nome_della_voce(radici[0]))
        else:
            rami, voci = self._aperti_dentro(self.albero.GetRootItem() if apertura.tutta else radici[0])
            # Traduttori: fine e' come Aperta tutta la plancia; voci come 120 voci, rami come 3 rami aperti.
            frase = _("{fine}: {voci} e {rami}").format(fine=apertura.fine, voci=plurale(voci, "{n} voce", "{n} voci"),
                rami=plurale(rami, "{n} ramo aperto", "{n} rami aperti"))
            if esploratore is not None:
                frase += ", " + plurale(esploratore.lette, "da {n} cartella letta", "da {n} cartelle lette")
            frase += "."
        frase += self._frase_dei_silenzi(esploratore)
        if apertura.avviato:
            self._riscontro_dopo(evento, frase)
        else:
            self._riscontro(evento, frase)

    def _frase_dei_silenzi(self, esploratore):
        """Le cartelle che l'esploratore non ha letto: quelle che non si
        leggono, e in rete quelle e le radici che non hanno risposto."""
        if esploratore is None:
            return ""
        parti = []
        if esploratore.illeggibili:
            parti.append(" " + plurale(esploratore.illeggibili, "{n} cartella non si legge.", "{n} cartelle non si leggono."))
        if esploratore.senza_risposta:
            nomi = {pulizia.norm(p): n for n, p in questa_rete.percorsi_salvati()}
            elenco = ", ".join(nomi.get(pulizia.norm(p), p) for p in esploratore.senza_risposta)
            # Traduttori: elenco e' quello dei percorsi di rete, divisi dalle virgole.
            parti.append(" " + ngettext("In rete non ha risposto: {elenco}.", "In rete non hanno risposto: {elenco}.", len(esploratore.senza_risposta)).format(
                elenco=elenco))
        if esploratore.cartelle_mute:
            mute = len(esploratore.cartelle_mute)
            parti.append(" " + ngettext("In rete una cartella non ha risposto, e l'apertura è andata avanti senza.",
                "In rete {n} cartelle non hanno risposto, e l'apertura è andata avanti senza.", mute).format(n=mute))
        return "".join(parti)

    def _lascia_le_incomplete(self, apertura):
        """Le cartelle che l'esploratore non ha finito di leggere, perche' si
        e' fermato o la rete taceva, si ricaricano quando si riaprono."""
        for chiave in apertura.incomplete:
            voce = apertura.mappa.get(chiave)
            if not apertura.viva(voce):
                continue
            dati = self._dati(voce)
            dati["caricato"] = False
            if not self.albero.GetChildrenCount(voce, False):
                self.albero.SetItemHasChildren(voce, True)

    def _chiudi_l_apertura(self):
        """Ferma l'apertura in corso, in silenzio: chi la ferma lo dice. Torna
        l'apertura fermata, o None."""
        apertura, self._apertura = self._apertura, None
        if apertura is None:
            return None
        if apertura.esploratore is not None:
            apertura.esploratore.ferma()
        self._lascia_le_incomplete(apertura)
        self._aggiorna_cartelle()
        return apertura

    def _apri_ramo(self, voce, con_i_marker=True):
        """Apre la voce e tutti i rami che ha dentro, caricandoli, tutto
        d'un fiato, fino a MASSIMO_DI_RAMI rami e MASSIMO_DI_VOCI voci: serve
        a J, che apre una playlist per suonarla. Torna (rami aperti,
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
            self._riscontro("errore", _("Non riesco a leggere {nome}: {errore}.").format(nome=nome, errore=e.strerror or e))
            return None

    def _comando_cerca_in_console(self):
        """Il campo della ricerca nella console, con le sue istruzioni come
        commenti; se il testo non si capisce lo spiega e lo ripropone."""
        testo = self._cercato_in_console
        while True:
            self._domanda()
            with FinestraFiltro(self, _("Cerca nella console"), testo, ISTRUZIONI_DELLA_CONSOLE) as dialogo:
                if dialogo.ShowModal() != wx.ID_OK:
                    self._annullato(_("Ricerca nella console annullata."))
                    return
                # Andare a capo vale come uno spazio; gli spazi dentro il
                # testo contano, perche' si cerca cosi' com'e'.
                testo = " ".join(dialogo.testo.splitlines()).strip()
            if not testo:
                self._annullato(_("Ricerca nella console annullata: il testo è vuoto."))
                return
            try:
                modello = modello_della_console(testo)
            except ErroreFiltro as e:
                self._riscontro("errore", _("Nella ricerca non capisco: {errore}").format(errore=e))
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
            self._riscontro("non_trovato_in_console", _("Nella console non c'è {testo}.").format(testo=self._cercato_in_console), "non_trovato_in_console")
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
            self._riscontro("non_disponibile", _("Nella console non c'è una ricerca: la barra rovesciata ne apre una."))
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
            self._riscontro("errore", _("Nel manuale non trovo la guida rapida."))
            return
        self._stampa("elenco_dei_tasti", righe)

    def _manuale(self):
        """F1: apre manuale.html nel browser predefinito, dove si naviga per
        titoli; la console lo dice (1.72.0, prima lo scriveva nella console).
        Se il file manca o non si apre, lo dice con il suono dell'errore."""
        nome = "manuale.html"
        percorso = percorsi.percorso_risorsa(nome)
        if not os.path.isfile(percorso):
            self._riscontro("errore", _("Non riesco ad aprire {nome}: il file non c'è.").format(nome=nome))
            return
        try:
            os.startfile(percorso)  # noqa: S606 - il manuale del programma, da un percorso fisso, nel browser predefinito
        except OSError as e:
            self._riscontro("errore", _("Non riesco ad aprire {nome}: {errore}.").format(nome=nome, errore=e.strerror or e))
            return
        self._riscontro("manuale", _("Il manuale si apre nel browser."))

    def _changelog(self):
        """F2: le novita' delle versioni piu' recenti, una cinquantina di righe;
        tutte erano troppe da scorrere (Gabriele, 1.88.1). In fondo, dove
        leggere il changelog intero."""
        novita = self._leggi_risorsa("CHANGELOG.md")
        if novita is None:
            return
        righe, tagliato = novita_recenti(righe_del_changelog(novita))
        if tagliato:
            cartella = os.path.dirname(percorsi.percorso_risorsa("CHANGELOG.md"))
            righe.append(_("Le versioni precedenti sono nel changelog intero: il file CHANGELOG.md, nella cartella {cartella}, "
                "e su GitHub, all'indirizzo {indirizzo}").format(cartella=cartella, indirizzo=CHANGELOG_SU_GITHUB))
        self._stampa("changelog", [_("Novità di MeTeOra"), *righe])

    def _crediti(self):
        righe = [
            _("Crediti di MeTeOra"),
            _("MeTeOra {versione} del {data}.").format(versione=version.VERSION, data=version.DATE),
            _("Autori: {autori}.").format(autori=version.AUTHOR),
            # I sostenitori, subito dopo gli autori (Gabriele, 3 novembre 2026).
            _("Grazie a chi sostiene MeTeOra con una donazione: {sostenitori}.").format(sostenitori=statistiche.elenco(SOSTENITORI)),
            # La nota di copyright, la licenza, la garanzia assente e dove
            # sono i testi: la GPL 3 li chiede nell'interfaccia (1.85.0).
            "Copyright (C) 2026 Gabriele Battaglia (IZ4APU).",
            _("MeTeOra è software libero: puoi ridistribuirlo e modificarlo secondo la GNU General Public License, versione 3 o, a tua scelta, "
              "qualunque versione successiva. È distribuito senza alcuna garanzia."),
            _("Il testo della licenza è nel file LICENSE accanto al programma; le licenze dei componenti sono nella cartella licenze, e il file "
              "licenze\\SORGENTI.txt dice dove trovarne il codice sorgente. Quello di MeTeOra è su https://github.com/GabrieleBattaglia/MeTeOra."),
            _("MeTeOra è formato da tre parole italiane, una dedica di Gabriele alla sua ragazza Ginevra."),
            _("Riproduzione: libmpv, del progetto mpv, con FFmpeg, libopenmpt, rubberband e le altre librerie della build di shinchiro, GPL 3 o successiva."),
            _("SID del Commodore 64: libsidplayfp, con l'emulazione reSIDfp, GPL 2 o successiva."),
            _("Durate dei SID: il database Songlengths della High Voltage SID Collection."),
            _("MIDI: FluidSynth e libsndfile, LGPL 2.1 o successiva, scaricati al primo MIDI; il banco di suoni FluidR3 GM di Frank Wen, "
              "licenza MIT, quando lo scarichi."),
            _("Musica delle console: libgme, Game Music Emu, LGPL 2.1 o successiva."),
            _("Interfaccia: wxPython e wxWidgets, wxWindows Library Licence."),
            _("Sintesi e braille: accessible_output2, licenza MIT, con il client di controllo di NVDA, LGPL 2.1."),
            _("Riconoscimento dei caratteri: il motore di Windows con i pacchetti winrt, licenza MIT, e Pillow."),
            _("Durate, lettura e scrittura dei tag dei file audio: mutagen, GPL 2 o successiva. Collegamento con libmpv: python-mpv, "
              "GPL 2 o successiva."),
            _("Effetti sonori: Acusticator, della libreria GBUtils di Gabriele, GPL 3, con numpy, scipy e sounddevice su PortAudio."),
            _("Il caricatore di Vulkan, di Khronos Group, LunarG e Valve: la copia di scorta di vulkan-1.dll. Apache 2.0, con parti MIT."),
            _("Python, della Python Software Foundation; pacchetto creato con PyInstaller, programma di installazione con Inno Setup."),
            _("Questo software si basa in parte sul lavoro dell'Independent JPEG Group."),
            _("Parti di questo software sono copyright The FreeType Project (www.freetype.org). Tutti i diritti riservati."),
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
            self._riscontro_dopo("errore", _("Non trovo più {percorso}, che suonava l'ultima volta.").format(percorso=percorso))
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
            # Traduttori: il nome della lista di un file aperto da solo.
            pl = Playlist(_("file aperto"), [Brano(percorso)], cartella="")
            brano = pl.brani[0]
        posizione = stato.get("posizione") or 0
        self.coda.imposta(pl, brano)
        sottobrano = stato.get("sottobrano") if isinstance(stato.get("sottobrano"), int) else None
        # Un video ripreso in pausa apre la sua finestra con X, non subito:
        # il fuoco resta nella plancia (tappa 9).
        self._video_in_attesa = percorso
        self._sentinella.guarda(percorso)
        self.motore.suona(percorso, sottobrano, inizio=posizione, in_pausa=True)
        self._statistiche.brano_avviato(percorso, sottobrano, "ripresa_all_avvio")
        voce = self._trova_voce_che_suona()
        if voce is not None:
            self.albero.EnsureVisible(voce)
            self._seleziona(voce)
        self._aggiorna_etichette()
        # Dopo il suono dell'avvio, che parte un attimo prima.
        self._riscontro_dopo("ripresa_all_avvio", _("Riprendo da dove eri: {percorso}, in pausa a {tempo}. X riparte.").format(percorso=percorso, tempo=tempo(posizione)))

    def dopo_l_avvio(self):
        """Da meteora.py, con la finestra mostrata, la ripresa fatta e i file
        di Windows arrivati (1.104.0). Le statistiche si scrivono subito, con
        la sessione aperta: anche una chiusura a forza nel primo minuto conta
        come non regolare. Poi, dopo i suoni dell'avvio, la pulizia."""
        self._salva_le_statistiche_in_disparte()
        self._avvia_la_ricerca_cast()
        self._dopo_il_suono(self._comincia_la_pulizia)

    # La pulizia all'avvio (Gabriele, 19 ottobre 2026, 1.104.0).

    def _comincia_la_pulizia(self):
        """Nel filo della finestra le copie di cio' che MeTeOra conosce:
        schede dello schedario, brani di playlist e Preferiti, marker, punti
        da riprendere e storico delle statistiche. Un filo a parte guarda se
        i file ci sono ancora, e le voci di quelli spariti le toglie
        _pulizia_finita, di nuovo nel filo della finestra. Senza niente da
        guardare, come al primo avvio, non parte."""
        if self._chiusa or self._pulizia is not None:
            return
        viste = self.schedario.istantanea()
        in_uso = self._percorsi_in_uso()
        da_guardare = set(viste) | in_uso
        if not da_guardare:
            return
        self._guardati_in_pulizia, self._toccati_in_pulizia = set(da_guardare), set()

        def finita(esito):
            # Nel filo della pulizia, sulle copie: le schede da togliere e le
            # copie vive dei file con i marker, perche' scorrere centomila
            # percorsi fermerebbe la finestra per un attimo.
            if "errore" not in esito:
                esito["schede"], esito["doppioni"] = self._schede_della_pulizia(viste, esito, in_uso)
                esito["altre_copie"] = marcatori.indice_delle_copie(viste, esito["mancanti"], pulizia.norm)
            wx.CallAfter(self._pulizia_finita, esito)

        self._riscontro("pulizia_avviata", plurale(len(da_guardare), "Pulizia all'avvio: controllo {n} voce.", "Pulizia all'avvio: controllo {n} voci."))
        # Con il file dei dischi che non si legge, ogni lettera si salta (1.112.0).
        self._pulizia = pulizia.Pulizia(da_guardare, finita, cedi=self._cedi, dischi=self.dischi.per_la_pulizia(),
            dischi_ignoti=bool(self.dischi.errore)).avvia()

    def _percorsi_in_uso(self):
        """I percorsi, cosi' come sono scritti, di playlist e Preferiti, dei
        marker, dei punti da riprendere e dello storico delle statistiche."""
        return (self.archivio.percorsi() | self.marcatori.percorsi_noti() | set(self.posizioni.percorsi())
            | set(self._statistiche.percorsi_dei_brani()))

    @staticmethod
    def _schede_della_pulizia(viste, esito, in_uso):
        """Le schede viste da togliere, percorso -> scheda, e quali di loro
        sono doppioni: quelle dei file spariti, e quelle scritte con
        maiuscole diverse dal disco quando c'e' anche la scheda con il nome
        vero e nessuno usa la scrittura sbagliata, che altrimenti si
        rileggerebbe e tornerebbe a ogni avvio."""
        mancanti, nomi_veri = esito["mancanti"], esito.get("nomi_veri") or {}
        schede, doppioni = {}, set()
        for percorso, scheda in viste.items():
            chiave = pulizia.norm(percorso)
            if chiave in mancanti:
                schede[percorso] = scheda
                continue
            vero = nomi_veri.get(chiave)
            if vero is not None and vero != percorso and vero in viste and percorso not in in_uso:
                schede[percorso] = scheda
                doppioni.add(percorso)
        return schede, doppioni

    def _pulizia_finita(self, esito):
        """La pulizia ha guardato tutto: nel filo della finestra si tolgono
        le voci dei file spariti, tranne quello che suona e quelle delle
        lettere diventate contese o riconosciute a mano intanto, e la console
        dice cosa e' cambiato, anche delle lettere diventate contese adesso.
        Con un dialogo aperto si aspetta che si chiuda: la plancia non cambia
        sotto le sue mani."""
        if self._chiusa or self._pulizia is None:
            return
        if not ctypes.windll.user32.IsWindowEnabled(self.GetHandle()):
            wx.CallLater(500, self._pulizia_finita, esito)
            return
        self._pulizia = None
        toccati, guardati = self._toccati_in_pulizia, self._guardati_in_pulizia
        self._toccati_in_pulizia, self._guardati_in_pulizia = set(), set()
        if "errore" in esito:
            self._statistiche.conta("pulizie_non_riuscite")
            self._riscontro_dopo("errore", _("La pulizia all'avvio non è riuscita: {errore}").format(errore=esito["errore"]))
            return
        self._statistiche.conta("pulizie")
        # I dischi imparati e le lettere diventate contese si ricordano anche
        # se intanto non si toglie niente (1.112.0).
        nuovi_dischi = esito.get("dischi") or {}
        contese_prima = {radice for radice in nuovi_dischi if self.dischi.contesa(radice)}
        if self.dischi.aggiorna(nuovi_dischi):
            try:
                self.dischi.salva()
            except OSError:
                # Restano da salvare: ci riprova l'uscita.
                self._statistiche.conta("salvataggi_non_riusciti")
        # Tornati in uso mentre la pulizia guardava, e quindi da non toccare:
        # il brano che suona, il nome nuovo di una rinomina, e i percorsi che
        # playlist, marker, punti e storico hanno preso dopo la copia, come un
        # file rimesso al suo posto e riaggiunto. Il prossimo avvio li guarda.
        in_corso = self.motore.in_corso
        tornati = set(toccati) | {pulizia.norm(p) for p in self._percorsi_in_uso() - guardati}
        if in_corso:
            tornati.add(pulizia.norm(in_corso))
        # Anche le voci delle lettere contese adesso, dopo i dischi della
        # pulizia: la Sentinella puo' averne resa contesa una dopo che la
        # pulizia l'ha guardata, con un altro disco infilato e usato, i cui
        # file sono fra i mancanti solo perche' allora era staccato. Una
        # lettera contesa tiene le sue voci, e cosi' una riconosciuta a mano
        # intanto, magari proprio con quel disco: la pulizia l'aveva letta con
        # quello di prima (1.112.0).
        riconosciute = self.dischi.riconosciute_dopo_la_copia()
        tornati |= {m for m in esito["mancanti"] if (lettera := pulizia.lettera_di(m)) in riconosciute or self.dischi.contesa(lettera)}
        mancanti = set(esito["mancanti"]) - tornati
        da_togliere = esito["schede"]
        if tornati:
            da_togliere = {p: s for p, s in da_togliere.items() if pulizia.norm(p) not in tornati}
        schede = self.schedario.togli(da_togliere)
        if schede:
            self._rinfresco_chiesto("schede")
        doppioni = len(set(schede) & (esito.get("doppioni") or set()))
        brani = self._togli_i_brani_spariti(mancanti)
        voci_tolte, marker_tolti, chiavi = self.marcatori.togli_i_mancanti(mancanti, altre_copie=esito.get("altre_copie"))
        if voci_tolte or chiavi:
            self._salva_i_marker(*chiavi)
        punti = self.posizioni.togli_i_mancanti(mancanti)
        if punti:
            try:
                self.posizioni.salva()
            except OSError:
                # Restano da salvare: ci riprova l'orologio delle posizioni, o l'uscita.
                self._statistiche.conta("salvataggi_non_riusciti")
        storico = self._statistiche.togli_i_brani(mancanti, in_corso=in_corso)
        saltate, contese = esito.get("saltate") or {}, esito.get("contese") or {}
        non_riconosciute = esito.get("non_riconosciute") or {}
        # La riga suggerisce Riconosci questo disco solo per le lettere usate
        # da dischi diversi; per una vista con un disco solo, che non e' mai
        # stato il suo, dice soltanto che la salta, anche se il menu lo offre
        # (1.112.0, Gabriele).
        da_riconoscere = [radice for radice in contese if self.dischi.contesa(radice)]
        for nome, quanti in (("pulizia_schede", len(schede) - doppioni), ("pulizia_doppioni", doppioni), ("pulizia_brani", brani),
                ("pulizia_marker", voci_tolte), ("pulizia_punti", punti), ("pulizia_storico", storico), ("pulizia_radici_saltate", len(saltate)),
                ("pulizia_dischi_diversi", len(contese)), ("pulizia_dischi_non_riconosciuti", len(non_riconosciute))):
            if quanti:
                self._statistiche.conta(nome, quanti)
        self._salva_le_statistiche_in_disparte()
        self._riscontro_dopo("pulizia_finita", self._frase_della_pulizia(len(mancanti), len(schede) - doppioni, doppioni, brani, voci_tolte, marker_tolti,
            punti, storico, saltate, contese, non_riconosciute, da_riconoscere))
        # Una lettera che la pulizia ha letto, e che diventa contesa solo
        # adesso, unendo il disco imparato a quello che la Sentinella ci aveva
        # visto intanto, il primo e quindi senza riga: la riga della pulizia
        # non la nomina, e lo si dice come la Sentinella.
        for radice in sorted(nuovi_dischi):
            if radice not in contese_prima and radice not in contese and radice not in non_riconosciute and self.dischi.contesa(radice):
                self._di_la_lettera_contesa(radice)

    def _togli_i_brani_spariti(self, mancanti):
        """Toglie da playlist e Preferiti i brani dei file spariti, anche i
        doppioni; il loop perde i suoi punti come con Canc. Se il fuoco era
        su uno di loro, va dove andrebbe dopo una cancellazione. Torna
        quanti brani ha tolto."""
        nella_plancia = [v for nodo in (self.nodo_preferiti, self.nodo_playlist) for v in self._tutte_le_voci(nodo)
            if (dati := self._dati(v)) and dati.get("tipo") == "brano" and pulizia.norm(dati["brano"].percorso) in mancanti]
        fuoco = self._voce_corrente()
        approdo = self._approdo(nella_plancia) if nella_plancia and self._dentro_una_di(fuoco, set(nella_plancia)) else None
        tolti = self.archivio.togli_i_percorsi(mancanti)
        if not tolti:
            return 0
        for pl, brano in tolti:
            if self.coda.loop_playlist is pl and brano is self.coda.punto_a:
                self.coda.togli_loop()
            elif self.coda.loop_playlist is pl and brano is self.coda.punto_b:
                self.coda.punto_b = None
        self._salva_archivio()
        if approdo is not None:
            self._ricostruisci_dopo_la_cancellazione(approdo)
        else:
            self._popola_playlist()
        return len(tolti)

    @staticmethod
    def _frase_della_pulizia(spariti, schede, doppioni, brani, voci, marker, punti, storico, saltate, contese=None, non_riconosciute=None,
            da_riconoscere=None):
        """La riga della console alla fine della pulizia: nei primi quaranta
        caratteri quanti file sono spariti, poi da dove sono stati tolti, le
        schede doppie dello schedario, le unita' che non hanno risposto, le
        lettere usate da dischi diversi e quelle a cui risponde un disco che
        la pulizia non riconosce (1.112.0); in fondo, per le lettere da
        riconoscere, cioe' quelle usate da dischi diversi, dove si trova
        Riconosci questo disco."""
        if spariti or schede:
            parti = [plurale(spariti, "Pulizia finita, {n} file sparito.", "Pulizia finita, {n} file spariti.")]
            # Traduttori: i pezzi di Tolti, divisi dai punti e virgola: dove e quanti, come da playlist e Preferiti 3 brani.
            tolti = [plurale(schede, "dallo schedario {n}", "dallo schedario {n}") if schede else "",
                _("da playlist e Preferiti {brani}").format(brani=plurale(brani, "{n} brano", "{n} brani")) if brani else "",
                _("dai marker {voci} con {marker}").format(voci=plurale(voci, "{n} voce", "{n} voci"), marker=plurale(marker, "{n} marker", "{n} marker")) if voci else "",
                plurale(punti, "punti da riprendere {n}", "punti da riprendere {n}") if punti else "",
                _("dallo storico delle statistiche {brani}").format(brani=plurale(storico, "{n} brano", "{n} brani")) if storico else ""]
            tolti = [t for t in tolti if t]
            if tolti:
                # Traduttori: tolti e' l'elenco di dove e quanti, diviso dai punti e virgola.
                parti.append(_("Tolti {tolti}.").format(tolti="; ".join(tolti)))
        else:
            parti = [_("Pulizia finita: c'è ancora tutto.")]
        if doppioni:
            parti.append(ngettext("Tolta dallo schedario {n} scheda doppia, scritta con le maiuscole diverse dal disco.",
                "Tolte dallo schedario {n} schede doppie, scritte con le maiuscole diverse dal disco.", doppioni).format(n=doppioni))
        if saltate:
            radici = sorted(saltate)
            restano = plurale(sum(saltate.values()), "{n} voce resta", "{n} voci restano")
            # Traduttori: radici e' l'elenco delle unità, come E:\, F:\; restano come 3 voci restano.
            parti.append(ngettext("Non risponde {radici}, e {restano} per il prossimo avvio.", "Non rispondono {radici}, e {restano} per il prossimo avvio.",
                len(radici)).format(radici=", ".join(radici), restano=restano))
        if contese:
            radici, quante = sorted(contese), sum(contese.values())
            if len(radici) > 1:
                # Traduttori: radici e' l'elenco delle unità, come E:\, F:\.
                parti.append(ngettext("Saltate {radici}, usate da dischi diversi: le loro {n} voci restano.",
                    "Saltate {radici}, usate da dischi diversi: le loro {n} voci restano.", quante).format(radici=", ".join(radici), n=quante))
            else:
                # Traduttori: radice e' un'unità, come E:\.
                parti.append(ngettext("Saltata {radice}, usata da dischi diversi: la sua voce resta.",
                    "Saltata {radice}, usata da dischi diversi: le sue {n} voci restano.", quante).format(radice=radici[0], n=quante))
        if non_riconosciute:
            radici, quante = sorted(non_riconosciute), sum(non_riconosciute.values())
            if len(radici) > 1:
                # Traduttori: radici e' l'elenco delle unità, come E:\, F:\.
                parti.append(ngettext("Saltate {radici}, non riconosco i dischi che rispondono: le loro {n} voci restano.",
                    "Saltate {radici}, non riconosco i dischi che rispondono: le loro {n} voci restano.", quante).format(radici=", ".join(radici), n=quante))
            else:
                # Traduttori: radice e' un'unità, come E:\.
                parti.append(ngettext("Saltata {radice}, non riconosco il disco che risponde: la sua voce resta.",
                    "Saltata {radice}, non riconosco il disco che risponde: le sue {n} voci restano.", quante).format(radice=radici[0], n=quante))
        if da_riconoscere:
            radici = sorted(da_riconoscere)
            if len(radici) == 1:
                # Traduttori: Riconosci questo disco e Questo PC sono una voce di menu e un ramo della plancia; radice un'unità, come E:\.
                parti.append(_("Per riconoscere il disco di adesso, Riconosci questo disco nel menu di {radice} in Questo PC.").format(radice=radici[0]))
            else:
                # Traduttori: menu e' l'elenco delle unità, come di E:\, di F:\ e di G:\.
                menu = _("{elenco} e di {ultima}").format(elenco=", ".join(_("di {radice}").format(radice=radice) for radice in radici[:-1]), ultima=radici[-1])
                # Traduttori: Riconosci questo disco e Questo PC sono una voce di menu e un ramo della plancia; menu come di E:\ e di F:\.
                parti.append(_("Per riconoscere i dischi di adesso, Riconosci questo disco nel menu {menu} in Questo PC.").format(menu=menu))
        return " ".join(parti)

    # I dischi a MeTeOra aperto: la Sentinella e Riconosci questo disco (1.112.0, Gabriele).

    def _disco_visto(self, lettera, chi):
        """La Sentinella ha visto chi rispondere alla lettera mentre MeTeOra
        ne usava un file: se non e' il suo disco, la lettera diventa contesa,
        e si salva subito, perche' una chiusura a forza non lo perda. Se cosi'
        la lettera e' contesa, lo si dice subito, con la riga e il suono suo
        (Gabriele): una volta sola per lettera e per disco, perche' un disco
        gia' visto non cambia il ricordo. La riga va subito, il suono dopo
        l'ultimo effetto, come quello del brano che parte; la domanda di un
        campo che si sta aprendo suona lo stesso."""
        if self._chiusa or not self.dischi.visto(lettera, chi):
            return
        try:
            self.dischi.salva()
        except OSError:
            # Restano da salvare: ci riprova l'uscita.
            self._statistiche.conta("salvataggi_non_riusciti")
        if self.dischi.contesa(lettera):
            self._di_la_lettera_contesa(lettera)

    def _di_la_lettera_contesa(self, lettera):
        """La riga della Sentinella per una lettera appena diventata contesa a
        MeTeOra aperto, e dopo l'ultimo effetto il suo suono (Gabriele)."""
        # Traduttori: lettera e' un'unità, come E:\; Riconosci questo disco e Questo PC sono una voce di menu e un ramo della plancia.
        self.scrivi(_("{lettera} ha un disco diverso da quello che conosco: le sue voci restano, e la pulizia la salta finché non usi "
            "Riconosci questo disco nel menu di {lettera} in Questo PC.").format(lettera=lettera))
        self._dopo_il_suono(self._suono, "disco_diverso")

    def _riconosci_il_disco(self, radice):
        """Riconosci questo disco, dal menu di un'unita' contesa in Questo PC:
        da adesso la lettera e' del disco che risponde, non e' piu' contesa, e
        la pulizia del prossimo avvio la controlla, togliendo le voci dei file
        che su quel disco non ci sono. Prima chiede conferma, dicendo quante
        sono (Gabriele): chi risponde e il conto si chiedono in disparte, su
        una copia dei percorsi che la pulizia guarderebbe, e una lettera che
        non risponde non ferma la finestra."""
        lettera = pulizia.lettera_di(radice)
        if self.dischi.errore:
            self._riscontro("errore", _("Il file dei dischi della pulizia non si legge: {errore}. Finché non si legge, {lettera} non si può riconoscere.").format(
                errore=self.dischi.errore, lettera=lettera))
            return
        if lettera in self._lettere_in_conto:
            self._riscontro("non_disponibile", _("Sto ancora contando le voci di {lettera}, e la domanda arriva appena ho finito.").format(lettera=lettera))
            return
        self._lettere_in_conto.add(lettera)
        percorsi = set(self.schedario.istantanea()) | self._percorsi_in_uso()
        pulizia.chiedi_il_conto(lettera, percorsi, lambda chi, conto: wx.CallAfter(self._disco_da_riconoscere, lettera, chi, conto),
            fermo=self._conti_fermati.is_set, cedi=self._cedi)

    def _disco_da_riconoscere(self, lettera, chi, conto):
        """Chi risponde alla lettera e il conto delle sue voci, arrivati dal
        loro filo: la domanda con Si' e No, con No predefinito ed Esc che vale
        No; con Si' chi risponde diventa il suo disco, si salva subito e lo si
        dice. Si riconosce il disco che rispondeva alla fine del conto: se
        dopo ne arriva un altro, la pulizia e la Sentinella rendono di nuovo
        contesa la lettera, e niente si toglie. Se pero' la Sentinella lo vede
        mentre la domanda aspetta, e lo dice, il Si' non riconosce niente:
        cancellerebbe il disco appena visto, che magari e' quello di adesso.
        Con un dialogo aperto si aspetta che si chiuda, come la fine della
        pulizia."""
        if self._chiusa:
            return
        if not ctypes.windll.user32.IsWindowEnabled(self.GetHandle()):
            wx.CallLater(500, self._disco_da_riconoscere, lettera, chi, conto)
            return
        self._lettere_in_conto.discard(lettera)
        if not chi:
            self._riscontro("errore", _("{lettera} non risponde, o non dice quale disco c'è: il disco resta da riconoscere.").format(lettera=lettera))
            return
        gia = _("Il disco di {lettera} è già quello riconosciuto: la pulizia all'avvio la controlla.").format(lettera=lettera)
        ricordo = self.dischi.conosciuti().get(lettera)
        if ricordo == {"disco": chi}:
            self._riscontro("non_disponibile", gia)
            return
        if not self._conferma(self._domanda_del_riconoscimento(lettera, conto), _("Riconosci questo disco")):
            self._annullato(_("Il disco di {lettera} resta da riconoscere: la pulizia all'avvio continua a saltarla.").format(lettera=lettera))
            return
        if self.dischi.conosciuti().get(lettera) != ricordo:
            self._riscontro("non_disponibile", _("Intanto a {lettera} ha risposto un altro disco: il disco resta da riconoscere. "
                "Per riconoscere quello di adesso, scegli di nuovo Riconosci questo disco.").format(lettera=lettera))
            return
        if not self.dischi.riconosci(lettera, chi):
            self._riscontro("non_disponibile", gia)
            return
        try:
            self.dischi.salva()
        except OSError:
            # Resta da salvare: ci riprova l'uscita.
            self._statistiche.conta("salvataggi_non_riusciti")
        self._riscontro("disco_riconosciuto", _("Disco di {lettera} riconosciuto: è quello che risponde adesso. Dal prossimo avvio la pulizia controlla {lettera}, "
            "e toglie le voci dei file che su questo disco non ci sono.").format(lettera=lettera))

    @staticmethod
    def _domanda_del_riconoscimento(lettera, conto):
        """La domanda di Riconosci questo disco, con quante voci della lettera
        la prossima pulizia togliera' (Gabriele). conto e' (voci, mancanti),
        come lo da' pulizia.conta_le_voci, o None se non si e' potuto fare:
        allora la domanda lo dice, senza numeri."""
        if conto is None:
            quante = _("le sue voci non si sono potute contare, e la prossima pulizia toglierà quelle dei file che qui non ci sono.")
        else:
            voci, mancanti = conto
            if not voci:
                quante = _("di {lettera} non conosco nessuna voce, e la prossima pulizia non avrà niente da togliere.").format(lettera=lettera)
            elif voci == 1:
                quante = (_("l'unica voce di {lettera} è di un file che qui non c'è, e la prossima pulizia la toglierà.").format(lettera=lettera) if mancanti
                    else _("l'unica voce di {lettera} è di un file che c'è, e la prossima pulizia non toglierà niente.").format(lettera=lettera))
            elif not mancanti:
                # Qui le voci sono almeno due.
                quante = ngettext("le {n} voci di {lettera} sono tutte di file che ci sono, e la prossima pulizia non toglierà niente.",
                    "le {n} voci di {lettera} sono tutte di file che ci sono, e la prossima pulizia non toglierà niente.", voci).format(n=voci, lettera=lettera)
            elif mancanti == voci:
                quante = ngettext("le {n} voci di {lettera} sono tutte di file che qui non ci sono, e la prossima pulizia le toglierà.",
                    "le {n} voci di {lettera} sono tutte di file che qui non ci sono, e la prossima pulizia le toglierà.", voci).format(n=voci, lettera=lettera)
            else:
                # Traduttori: voci e' quante voci ha l'unità, n quante di loro sono di file che non ci sono.
                quante = ngettext("delle {voci} voci di {lettera}, {n} è di un file che qui non c'è e la prossima pulizia la toglierà.",
                    "delle {voci} voci di {lettera}, {n} sono di file che qui non ci sono e la prossima pulizia le toglierà.", mancanti).format(voci=voci,
                    lettera=lettera, n=mancanti)
        # Traduttori: lettera e' un'unità, come E:\; quante e' una frase su quante voci la pulizia toglierà.
        return _("{lettera} diventa del disco che risponde adesso; {quante} Riconosco?").format(lettera=lettera, quante=quante)

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
        # Da qui la plancia risponde a NVDA come Windows (issue 21): NVDA puo'
        # chiedere anche mentre la finestra si chiude.
        if self._accessibile is not None:
            self._accessibile.chiudi()
        if self.ascolto_delle_copie is not None:
            self.ascolto_delle_copie.ferma()
        self.barra.ferma()
        self._braille.svuota()
        if self._ricerca is not None:
            self._ricerca.ferma()
        if self._apertura is not None and self._apertura.esploratore is not None:
            self._apertura.esploratore.ferma()
        # I lettori di rete liberi si chiudono; uno appeso e' gia' abbandonato (2.7.2).
        lettore_di_rete.lettori.chiudi()
        if self._ricerca_cast is not None:
            # La ricerca chiude il suo zeroconf: in disparte, come lo speaker,
            # che il motore chiude con se'.
            threading.Thread(target=self._ricerca_cast.ferma, daemon=True).start()
        self.impostazioni["ripresa"] = self._stato_da_riprendere()
        self._orologio_delle_posizioni.Stop()
        self._orologio_delle_statistiche.Stop()
        self._sveglia_del_timer.Stop()
        self._orologio_della_sfumatura.Stop()
        self._ricorda_la_posizione()
        non_salvati = []
        self._salva_all_uscita(self.archivio.salva, _("le playlist"), non_salvati)
        if self.posizioni.modificate:
            self._salva_all_uscita(self.posizioni.salva, _("le posizioni dei file lunghi"), non_salvati)
        if self.marcatori.modificato:
            self._salva_all_uscita(self.marcatori.salva, _("i marker"), non_salvati)
        if self.dischi.modificati:
            self._salva_all_uscita(self.dischi.salva, _("i dischi della pulizia all'avvio"), non_salvati)
        self.contatore.ferma()
        self.schedario.ferma()
        # La pulizia ferma non porta piu' niente: quello che non ha finito di
        # guardare resta per il prossimo avvio.
        for lavoro in (self._lettura, self._passata, self._pulizia):
            if lavoro is not None:
                lavoro.ferma()
        # Anche i conti di Riconosci questo disco: la loro domanda non arriva piu'.
        self._conti_fermati.set()
        if self._video is not None:
            # Prima la barra: un trascinamento in corso tiene il mouse, e una
            # finestra distrutta con il mouse preso fa cadere wx (revisione
            # della 1.88.0).
            self._video.barra.ferma()
            self._video.Destroy()
            self._video = None
        self._salva_all_uscita(self.schedario.salva, _("lo schedario delle durate e dei tag"), non_salvati)
        self._salva_all_uscita(self.impostazioni.salva, _("le impostazioni"), non_salvati)
        # Le statistiche per ultime: contano anche i salvataggi non riusciti.
        # L'ultimo passo dell'orologio guarda il motore, che e' ancora aperto.
        self._statistiche.scatta(self._stato_per_le_statistiche())
        self._statistiche.chiusura()
        self._statistiche.conta("salvataggi_non_riusciti", len(non_salvati))
        self._salva_all_uscita(self._statistiche.salva, _("le statistiche"), non_salvati)
        self.motore.chiudi()
        if non_salvati:
            # La console sta per sparire: lo dice una finestra, prima di
            # chiudere (tappa 9).
            suoni.suona("errore", self.impostazioni["volume_effetti"])
            # Traduttori: cosa e' l'elenco di cosa non si e' salvato, con il perche', diviso dai punti e virgola.
            wx.MessageBox(_("MeTeOra non è riuscito a salvare {cosa}.").format(cosa="; ".join(non_salvati)), _("MeTeOra, uscita"), wx.OK | wx.ICON_ERROR, self)
        # Il suono dell'uscita si ascolta intero prima che il processo finisca.
        suoni.suona("uscita", self.impostazioni["volume_effetti"], sync=True)
        evento.Skip()
