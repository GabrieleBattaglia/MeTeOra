# MeTeOra, le statistiche: ogni sorta di conti, raccolti mentre lo si usa, e la pagina che li racconta.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (UltraCode).
# 17/10/2026: nasce con la 1.103.0, chiesta da Gabriele: piu' dati ci sono, piu' e' contento. Nella 1.104.0 le righe che elencano voci tengono solo quelle diverse da zero, le percentuali uniformi, gli anni futuri dei tag ignorati, le date sempre con il giorno della settimana, e i brani dello storico tolti dalla pulizia all'avvio o rinominati, con i conti della pulizia nella salute. Nella 1.105.0 i nomi di Dove sono, il comando dell'apostrofo, e del suo suono. Nella 1.109.0 le playlist ordinate, invertite, mescolate e rimesse nell'ordine di prima. Nella 1.110.0 quelli della durata residua, Maiuscolo con l'apostrofo.

"""Le statistiche di MeTeOra (1.103.0).

Il file e' "MeTeOra - Statistiche.json", accanto agli altri dati, scritto
come loro: prima un file accanto, poi al posto del vero. Un file che non si
legge non si sovrascrive: errore dice perche', e i conti nuovi vanno accanto,
con .nuovo, come per le impostazioni. Le copie dei dati lo tengono.

I conti arrivano da quattro strade, tutte dalla finestra principale:
- gli eventi, uno per ogni effetto sonoro, cioe' per ogni azione: evento();
- i tasti premuti nella finestra, per nome: tasto();
- l'orologio, scatta(), che la finestra chiama ogni secondo e a ogni evento
  con lo stato di adesso: il tempo passato dall'ultima volta va allo stato
  di prima. Un intervallo piu' lungo di PASSO_MASSIMO vuol dire il PC
  sospeso o la finestra ferma, e conta al piu' PASSO_MASSIMO;
- i conti espliciti, dove serve una quantita': conta(), e la vita dei brani,
  brano_avviato(), brano_finito(), brano_fermato(), brano_in_errore().
Autori, album, generi, anni, cartelle e unita' non si salvano: le righe le
ricavano dai brani ascoltati e dai tag dello schedario.

Le righe della pagina le compone righe(), una informazione per riga, nella
forma "Etichetta: valore.", come i dettagli di F11; ogni sezione si apre con
"Sezione n di N", che si cerca con la barra rovesciata. I numeri non hanno il
separatore delle migliaia, perche' in MeTeOra il punto e' quello dei
decimali; le percentuali hanno il punto e niente articolo davanti; le durate
lunghe si dicono a parole; le date hanno sempre il giorno della settimana.
Le righe che elencano voci, come le ore o i mesi, tengono solo quelle
diverse da zero (1.104.0).

La pulizia all'avvio, che fa la finestra, toglie dallo storico dei brani i
file che non ci sono piu', con togli_i_brani(), e i suoi conti li scrive con
conta(); un file rinominato porta con se' la sua voce, con rinomina_brano().
I percorsi si confrontano normalizzati con normcase e abspath, come negli
altri moduli (1.104.0).
"""

import contextlib
import datetime
import itertools
import json
import ntpath
import os
import threading
import time
from collections import Counter

import formati
import valori

VERSIONE_DEL_FILE = 1
# Quanti brani ricorda lo storico dei brani: oltre, escono i meno ascoltati,
# un centesimo alla volta. I totali stanno a parte, e restano giusti.
MASSIMO_DEI_BRANI = 50000
# Il tempo piu' lungo che un passo dell'orologio puo' contare: di piu' vuol
# dire il PC sospeso, o la finestra ferma.
PASSO_MASSIMO = 5.0
# Sotto tanti secondi d'ascolto, un brano lasciato e' lasciato subito.
SUBITO = 10.0
# Una durata piu' lunga di una settimana non e' credibile: nello schedario ci
# sono file rovinati che dicono migliaia di anni.
DURATA_CREDIBILE = 7 * 86400
# Quanti posti hanno le classifiche (Gabriele, 17 ottobre 2026).
POSTI = 20
# Quanti sottobrani diversi si ricordano per ogni file.
MASSIMO_DEI_SOTTOBRANI = 256

MESI = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre")
GIORNI = ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica")

# Le famiglie dei formati, nell'ordine in cui si dicono a parita' di tempo.
FAMIGLIE = {
    "audio": "Audio, MP3, FLAC e gli altri",
    "sid": "SID del Commodore 64",
    "video": "Video",
    "midi": "MIDI",
    "tracker": "Moduli dei tracker",
    "console": "Musica delle console",
}
NOMI_BREVI_DELLE_FAMIGLIE = {"audio": "audio", "sid": "SID", "video": "video", "midi": "MIDI", "tracker": "tracker", "console": "console"}


def famiglia(percorso):
    """La famiglia del formato di un file, una chiave di FAMIGLIE."""
    if formati.e_sid(percorso):
        return "sid"
    if formati.e_midi(percorso):
        return "midi"
    if formati.e_chip(percorso):
        return "console"
    if formati.e_video(percorso):
        return "video"
    if formati.estensione(percorso) in formati.TRACKER:
        return "tracker"
    return "audio"


# Come e' partito un brano: l'evento del suo annuncio -> il gruppo da dire.
MODI = {
    "brano_seguente_da_solo": "da_soli",
    "ritorno_al_punto_a": "da_soli",
    "successivo": "b",
    "precedente": "z",
    "casuale": "n",
    "playlist_precedente": "playlist",
    "playlist_successiva": "playlist",
    "playlist_numero": "playlist",
    "ripresa_all_avvio": "ripresa",
}

# Le descrizioni dei comandi dei tasti a carattere, per la classifica dei tasti.
DESCRIZIONI_DEI_COMANDI = {
    "precedente": "brano precedente", "play": "suona", "playlist_precedente": "playlist precedente", "playlist_successiva": "playlist successiva",
    "loop": "loop A-B", "pausa": "pausa", "stop": "stop", "ripetizione": "ripetizione", "timer": "timer di spegnimento",
    "successivo": "brano successivo", "casuale": "brano a caso", "riproduzione_casuale": "riproduzione casuale", "muto": "muto",
    "indietro": "indietro nel brano", "avanti": "avanti nel brano", "passo_indietro": "secondi del salto indietro",
    "passo_avanti": "secondi del salto avanti", "vai_a_tempo": "vai a un tempo", "capitolo_precedente": "capitolo precedente",
    "capitolo_successivo": "capitolo successivo", "volume_su": "volume su", "volume_giu": "volume giù", "ricerca": "ricerca",
    "filtro": "filtro", "passo_volume": "passo del volume", "marker": "marker", "marker_precedente": "marker precedente",
    "marker_successivo": "marker successivo", "togli_i_marker": "toglie i marker", "togli_i_marker_prima": "toglie i marker prima",
    "togli_i_marker_dopo": "toglie i marker dopo", "velocita_giu": "più lento", "velocita_normale": "velocità normale",
    "velocita_su": "più veloce", "tono_giu": "tono giù", "tono_normale": "tono normale", "tono_su": "tono su",
    "banda_precedente": "banda precedente", "banda_successiva": "banda successiva", "banda_giu": "banda giù", "banda_su": "banda su",
    "azzera_la_banda": "azzera la banda", "azzera_le_bande": "azzera le bande", "dissolvenza": "dissolvenza",
    "durata_della_dissolvenza": "durata della dissolvenza", "dove_sono": "dove sono", "durata_residua": "durata residua",
}
# Le descrizioni degli altri tasti, per nome.
DESCRIZIONI_DEI_TASTI = {
    "F1": "il manuale", "F2": "le novità", "F3": "i crediti", "F4": "nei Preferiti", "F5": "alla plancia", "F6": "alla console",
    "F7": "al cruscotto", "F8": "al brano che suona", "F9": "chiude il ramo", "F10": "apre il ramo", "F11": "tag e dettagli",
    "F12": "la guida rapida", "Esc": "esce", "Maiuscolo con F1": "il video", "Maiuscolo con F2": "i sottotitoli",
    "Maiuscolo con F3": "la traccia audio", "Maiuscolo con F5": "lo schermo intero", "Maiuscolo con F6": "il rapporto dell'immagine",
    "Maiuscolo con F7": "le statistiche", "Maiuscolo con F8": "l'inseguimento", "Maiuscolo con F9": "chiude tutta la plancia",
    "Maiuscolo con F10": "apre tutta la plancia", "Maiuscolo con F11": "il menu dei tag", "Maiuscolo con F12": "i tasti rapidi",
    "Ctrl con barra rovesciata": "la ricerca in tutto MeTeOra", "Backspace": "risale", "Maiuscolo con Backspace": "risale all'antenato",
    "Barra spaziatrice": "il menu", "Invio": "il menu, o il comando", "Applicazioni": "il menu", "Canc": "toglie",
    "Maiuscolo con Canc": "nel cestino", "Ctrl con Barra spaziatrice": "seleziona",
}

# I nomi degli eventi, per la sezione di tutti gli eventi e per il suono piu'
# suonato. Un evento senza nome, per esempio uno nuovo, si dice com'e'.
NOMI_DEGLI_EVENTI = {
    "avvio": "avvio di MeTeOra", "uscita": "uscita da MeTeOra", "donazione": "invito a offrire un caffè",
    "dettagli": "dettagli di un contenitore, con F11", "chiudi_la_plancia": "tutta la plancia chiusa",
    "apri_la_plancia": "apertura di tutta la plancia", "plancia_aperta": "tutta la plancia aperta",
    "passata_avviata": "passata degli impressi avviata", "passata_finita": "passata degli impressi finita",
    "plancia": "alla plancia, con F5", "console": "alla console, con F6", "cruscotto": "al cruscotto, con F7",
    "manuale": "manuale, con F1", "changelog": "novità, con F2", "crediti": "crediti, con F3",
    "play": "riproduzione avviata", "pausa": "pausa", "ripresa": "ripresa dalla pausa", "stop": "stop", "da_capo": "da capo",
    "successivo": "brano successivo", "precedente": "brano precedente", "casuale": "brano a caso",
    "casuale_acceso": "riproduzione casuale accesa", "casuale_spento": "riproduzione casuale spenta",
    "video_acceso": "video acceso", "video_spento": "video spento", "sottotitoli_accesi": "sottotitoli accesi",
    "sottotitoli_spenti": "sottotitoli spenti", "traccia_audio": "traccia audio cambiata", "schermo_intero": "schermo intero",
    "schermo_in_finestra": "video in finestra", "rapporto": "rapporto dell'immagine cambiato", "video_nascosto": "video nascosto",
    "percorso_aggiunto": "percorso di rete aggiunto", "percorso_tolto": "percorso di rete tolto",
    "scaricamento_avviato": "scaricamento avviato", "scaricamento_finito": "scaricamento finito",
    "brano_seguente_da_solo": "brano seguente partito da solo", "fine_playlist": "fine della lista",
    "avanti": "salto avanti", "indietro": "salto indietro", "vai_a_tempo": "vai a un tempo",
    "passo_di_salto": "passo di salto cambiato", "passo_del_volume": "passo del volume cambiato",
    "volume_su": "volume su", "volume_giu": "volume giù", "volume_al_limite": "volume già al limite",
    "muto_acceso": "muto acceso", "muto_spento": "muto spento", "menu": "menu aperto",
    "nuova_playlist": "nuova playlist vuota", "playlist_creata": "playlist creata", "playlist_eliminata": "playlist eliminata",
    "playlist_rinominata": "playlist rinominata", "file_rinominato": "file rinominato", "tag_letti": "tag letti",
    "tag_cambiato": "tag cambiati", "tag_cancellato": "tag cancellati", "brano_aggiunto": "brani aggiunti a una playlist",
    "preferito_aggiunto": "brano messo nei Preferiti", "filtro_messo": "filtro messo", "ricerca_avviata": "ricerca avviata",
    "ricerca_finita": "ricerca finita", "ricerca_fermata": "ricerca fermata", "altri_risultati": "altri risultati mostrati",
    "filtro_tolto": "filtro tolto", "gia_nei_preferiti": "brano già nei Preferiti", "brano_tolto": "brani tolti da una playlist",
    "cestino": "nel cestino", "brano_spostato": "brano spostato", "playlist_ordinata": "playlist ordinata",
    "ordine_invertito": "ordine di una playlist invertito", "playlist_mescolata": "playlist mescolata",
    "ordine_ripristinato": "playlist rimessa nell'ordine di prima", "saltato_acceso": "brano segnato come saltato",
    "saltato_spento": "brano non più saltato", "ramo_aperto": "ramo aperto", "ramo_chiuso": "ramo chiuso",
    "file_aperto": "file aperto", "vai_al_brano": "al brano che suona, con F8", "playlist_precedente": "playlist precedente",
    "playlist_successiva": "playlist successiva", "playlist_numero": "playlist con una cifra",
    "ripresa_all_avvio": "ripresa all'avvio", "insegui_acceso": "inseguimento acceso", "insegui_spento": "inseguimento spento",
    "elenco_dei_tasti": "guida rapida, con F12", "trovato_in_console": "trovato nella console",
    "ripartito_in_console": "ricerca nella console ripartita dall'inizio", "non_trovato_in_console": "non trovato nella console",
    "chiudi_tutto": "ramo chiuso con F9", "marker_messo": "marker messo", "marker_rinominato": "marker rinominato",
    "marker_indietro": "al marker precedente", "marker_avanti": "al marker successivo",
    "marker_tolti_prima": "marker tolti prima del punto", "marker_tolti_dopo": "marker tolti dopo il punto",
    "marker_tolti_tutti": "tutti i marker del brano tolti", "marker_eliminato": "marker eliminati",
    "risali": "risalita con Backspace", "risali_all_antenato": "risalita all'antenato", "apri_tutto": "ramo aperto con F10",
    "impostazioni": "impostazioni aperte", "impostazione_cambiata": "impostazione cambiata", "console_salvata": "console salvata",
    "scheda_audio": "scheda audio cambiata", "marcatori": "finestra dei marcatori aperta",
    "marcatori_esportati": "marcatori esportati", "marcatori_importati": "marcatori importati",
    "marcatori_cancellati": "tutti i marcatori cancellati", "trovato_nei_marcatori": "trovato nei marcatori",
    "ripartito_nei_marcatori": "ricerca nei marcatori ripartita dall'inizio", "non_trovato_nei_marcatori": "non trovato nei marcatori",
    "domanda": "domanda", "aggiornamento": "aggiornamento proposto", "tasti_spenti": "tasti rapidi spenti",
    "tasti_accesi": "tasti rapidi accesi", "capitolo_precedente": "capitolo precedente", "capitolo_successivo": "capitolo successivo",
    "ripetizione_spenta": "ripetizione spenta", "ripetizione_brano": "ripetizione del brano", "ripetizione_lista": "ripetizione della lista",
    "timer_impostato": "timer impostato", "timer_tolto": "timer tolto", "timer_scaduto": "timer scaduto",
    "annullamento": "annullamento", "ramo_aggiornato": "ramo aggiornato", "non_disponibile": "comando che lì non vale",
    "errore": "errore", "problema": "problema interno", "niente_da_suonare": "niente da suonare",
    "loop_a_messo": "punto A del loop", "loop_b_messo": "punto B del loop", "loop_tolto": "loop tolto",
    "loop_non_qui": "loop che lì non si mette", "fuori_dal_loop": "brano fuori dal loop", "ritorno_al_punto_a": "ritorno al punto A",
    "nessun_altro_brano": "niente oltre", "velocita_su": "più veloce", "velocita_giu": "più lento",
    "velocita_normale": "velocità normale", "velocita_al_limite": "velocità al limite", "tono_su": "tono su", "tono_giu": "tono giù",
    "tono_normale": "tono normale", "tono_al_limite": "tono al limite", "banda_al_limite": "banda al limite",
    "guadagno_al_limite": "guadagno al limite", "banda_azzerata": "banda azzerata", "bande_azzerate": "equalizzatore azzerato",
    "dissolvenza_accesa": "dissolvenza accesa", "dissolvenza_spenta": "dissolvenza spenta",
    "dissolvenza_durata": "durata della dissolvenza cambiata", "statistiche": "statistiche aperte",
    "statistiche_azzerate": "statistiche azzerate", "trovato_nelle_statistiche": "trovato nelle statistiche",
    "ripartito_nelle_statistiche": "ricerca nelle statistiche ripartita dall'inizio",
    "non_trovato_nelle_statistiche": "non trovato nelle statistiche",
    # Nella 1.104.0, nell'ordine di suoni.EVENTI.
    "pulizia_avviata": "pulizia all'avvio cominciata", "pulizia_finita": "pulizia all'avvio finita",
    # Nella 1.105.0.
    "dove_sono": "dove sono, con l'apostrofo",
    # Nella 1.110.0.
    "durata_residua": "durata residua, con Maiuscolo e l'apostrofo",
}

# Che cosa ha tolto la pulizia all'avvio: il conto, il singolare, il plurale
# e se e' femminile, per l'accordo di tolto (1.104.0). pulizia_schede sono i
# file spariti; pulizia_doppioni le schede doppie, che differiscono solo per
# le maiuscole, tolte quando c'e' quella scritta come sul disco.
TOLTI_DALLA_PULIZIA = (
    ("pulizia_schede", "file dallo schedario", "file dallo schedario", False),
    ("pulizia_doppioni", "scheda doppia dello schedario", "schede doppie dello schedario", True),
    ("pulizia_brani", "brano da playlist e Preferiti", "brani da playlist e Preferiti", False),
    ("pulizia_marker", "voce dei marker", "voci dei marker", True),
    ("pulizia_punti", "punto da riprendere", "punti da riprendere", False),
    ("pulizia_storico", "brano dallo storico", "brani dallo storico", False),
)


# Le parole.

def al_plurale(n, singolare, plurale):
    return f"{n} {singolare if n == 1 else plurale}"


def elenco(parti):
    """a; a e b; a, b e c."""
    parti = [p for p in parti if p]
    if len(parti) <= 1:
        return "".join(parti)
    return f"{', '.join(parti[:-1])} e {parti[-1]}"


def durata(secondi):
    """Una durata a parole: sotto l'ora minuti e secondi, come 3 minuti e 41
    secondi; dall'ora in su giorni, ore e minuti, come 2 giorni, 19 ore e 40
    minuti."""
    secondi = max(0.0, float(secondi or 0))
    if secondi == 0:
        return "0 secondi"
    if secondi < 1:
        return "meno di un secondo"
    if round(secondi) < 3600:
        minuti, resto = divmod(round(secondi), 60)
        return elenco([al_plurale(minuti, "minuto", "minuti") if minuti else "", al_plurale(resto, "secondo", "secondi") if resto else ""])
    giorni, resto = divmod(round(secondi / 60), 1440)
    ore, minuti = divmod(resto, 60)
    return elenco([al_plurale(giorni, "giorno", "giorni") if giorni else "", al_plurale(ore, "ora", "ore") if ore else "",
        al_plurale(minuti, "minuto", "minuti") if minuti else ""])


def anni_e_mesi(giorni):
    """Tanti giorni come anni e mesi: 9 anni e 7 mesi; sotto l'anno i mesi,
    sotto il mese i giorni."""
    mesi_in_tutto = round(giorni / 30.4375)
    if mesi_in_tutto < 1:
        return al_plurale(max(1, round(giorni)), "giorno", "giorni")
    anni, mesi = divmod(mesi_in_tutto, 12)
    return elenco([al_plurale(anni, "anno", "anni") if anni else "", al_plurale(mesi, "mese", "mesi") if mesi else ""])


def percentuale(parte, tutto):
    """Con il punto e un decimale, senza articolo davanti: 58.4%. Sotto lo
    0.1% due decimali, perche' una parte piccola non sembri niente. Il
    formato si sceglie sul valore arrotondato a due decimali, cosi' 0.0996
    da' 0.1% e non 0.10%; con il totale a zero, 0.0% come le altre (1.104.0)."""
    if not tutto:
        return "0.0%"
    valore = 100 * parte / tutto
    arrotondato = round(valore, 2)
    if valore > 0 and arrotondato < 0.01:
        return "meno di 0.01%"
    return f"{valore:.2f}%" if 0 < arrotondato < 0.1 else f"{valore:.1f}%"


def numero_decimale(valore):
    """1.75, 0.8, 1: il punto, e senza zeri in fondo."""
    return f"{valore:.2f}".rstrip("0").rstrip(".")


def _ora(quando):
    return f"{quando.hour}:{quando.minute:02d}"


def _alle(quando):
    """alle 10:12, all'1:16."""
    return f"all'{_ora(quando)}" if quando.hour == 1 else f"alle {_ora(quando)}"


def _con(preposizione, testo):
    """La preposizione davanti, se c'e', scritta com'e': da, a, di. Le date
    cominciano con il giorno della settimana, e non si elide mai (1.104.0)."""
    return f"{preposizione} {testo}" if preposizione else testo


def dalle(ora):
    """L'inizio di un'ora: da mezzanotte, dall'una, dalle 13."""
    return {0: "da mezzanotte", 1: "dall'una"}.get(ora, f"dalle {ora}")


def alle(ora):
    return {0: "a mezzanotte", 1: "all'una"}.get(ora, f"alle {ora}")


def _leggi_data(testo):
    """Una data del file, scritta con isoformat, o None."""
    try:
        return datetime.datetime.fromisoformat(testo)
    except (TypeError, ValueError):
        return None


def data(quando, preposizione=None):
    """Una data, sempre con il giorno della settimana, e la preposizione
    davanti se c'e': lunedi' 19 ottobre 2026, da lunedi' 19 ottobre 2026.
    Dalla 1.104.0 tutte le date sono cosi'."""
    return _con(preposizione, f"{GIORNI[quando.weekday()]} {quando.day} {MESI[quando.month - 1]} {quando.year}")


def data_e_ora(testo, preposizione=None):
    """Una data del file con l'ora: lunedi' 19 ottobre 2026 alle 18:03; "una
    data che non si legge" se non e' una data, con la preposizione anche
    davanti a questa."""
    quando = _leggi_data(testo)
    return f"{data(quando, preposizione)} {_alle(quando)}" if quando else _con(preposizione, "una data che non si legge")


def solo_la_data(testo, preposizione=None):
    quando = _leggi_data(testo)
    return data(quando, preposizione) if quando else _con(preposizione, "una data che non si legge")


def _decennio(anno):
    decennio = anno // 10 * 10
    return f"anni '{decennio % 100:02d}" if 1920 <= decennio < 2000 else f"anni {decennio}"


def _nome(percorso):
    # I percorsi sono di Windows: ntpath li tratta cosi' anche altrove.
    return ntpath.basename(percorso.rstrip("\\")) or percorso


def _norm(percorso):
    """Il percorso come si confronta: assoluto e, su Windows, con le
    maiuscole e le barre di sistema. E' la forma degli insiemi di percorsi
    mancanti che arrivano dalla pulizia (1.104.0)."""
    return os.path.normcase(os.path.abspath(percorso))


def unita_di(percorso):
    """L'unita' di un percorso: E:, oppure il server di rete, \\\\iliadbox_Server."""
    if percorso.startswith("\\\\"):
        return "\\\\" + percorso[2:].split("\\", 1)[0]
    lettera = ntpath.splitdrive(percorso)[0]
    return lettera.upper() if lettera else "senza unità"


def _numero(valore):
    """Vero per un numero del file, non booleano e finito."""
    return isinstance(valore, int | float) and not isinstance(valore, bool) and valore == valore and abs(valore) != float("inf")


def _piu(dizionario, chiave, quanto=1):
    """Aggiunge quanto alla chiave: gli interi restano interi, i secondi
    si tengono al millesimo, perche' il file non cresca di cifre inutili."""
    valore = dizionario.get(chiave, 0) + quanto
    dizionario[chiave] = round(valore, 3) if isinstance(valore, float) else valore


def _quando(testo):
    """La data di un'ultima volta, da confrontare: senza il fuso, che un
    file toccato a mano potrebbe avere."""
    quando = _leggi_data(testo)
    return quando.replace(tzinfo=None) if quando else None


def _unisci(prima, dopo):
    """Due voci dello storico dello stesso file, in una nuova: volte,
    secondi, finiti e marker si sommano; l'ultima volta e' la piu' recente;
    i sottobrani di prima, poi quelli di dopo che mancano, fino a
    MASSIMO_DEI_SOTTOBRANI. Il resto viene da prima, o da dopo se prima non
    ce l'ha (1.104.0)."""
    voce = {**dopo, **prima}
    for chiave in ("volte", "secondi", "finiti", "marker"):
        if chiave in prima or chiave in dopo:
            voce[chiave] = 0
            _piu(voce, chiave, prima.get(chiave, 0) + dopo.get(chiave, 0))
    ultime = [u for u in (prima.get("ultima"), dopo.get("ultima")) if _quando(u)]
    if ultime:
        voce["ultima"] = max(ultime, key=_quando)
    sotto, visti = [], set()
    for n in itertools.chain(prima.get("sotto", ()), dopo.get("sotto", ())):
        if n not in visti and len(sotto) < MASSIMO_DEI_SOTTOBRANI:
            visti.add(n)
            sotto.append(n)
    if sotto:
        voce["sotto"] = sotto
    return voce


def _vuote(adesso):
    """I conti di una raccolta nuova, che comincia adesso."""
    return {
        "versione": VERSIONE_DEL_FILE,
        # Restano anche all'azzeramento.
        "prima_raccolta": adesso,
        "azzeramenti": 0,
        "ultimo_azzeramento": None,
        # La raccolta di adesso.
        "dal": adesso,
        "salvato": None,
        "sessione_aperta": False,
        "conti": {},
        "eventi": {},
        "tasti": {},
        "senza_comando": {},
        "tempi": {},
        "formati": {},
        "modi": {},
        "sorgenti": {},
        "schede_audio": {},
        "impostazioni": {},
        "bande": [0] * len(valori.FREQUENZE_DELLE_BANDE),
        "giorni": {},
        "ore": [0.0] * 24,
        "settimana": [0.0] * 7,
        "versioni": {},
        "record": {},
        "brani": {},
    }


def _numeri(valore):
    """Un dizionario di numeri dal file, senza le voci sbagliate."""
    return {str(k): v for k, v in valore.items() if _numero(v)} if isinstance(valore, dict) else {}


def _lista_di_numeri(valore, lunghezza):
    if isinstance(valore, list) and len(valore) == lunghezza and all(map(_numero, valore)):
        return list(valore)
    return [0] * lunghezza


def _pulite(dati, adesso):
    """I conti letti dal file, con i predefiniti al posto di cio' che manca
    o e' sbagliato: un file toccato a mano non ferma l'avvio."""
    pulite = _vuote(adesso)
    if not isinstance(dati, dict):
        return pulite
    for chiave in ("prima_raccolta", "dal", "salvato", "ultimo_azzeramento"):
        if isinstance(dati.get(chiave), str) and _leggi_data(dati[chiave]):
            pulite[chiave] = dati[chiave]
    if isinstance(dati.get("azzeramenti"), int) and not isinstance(dati["azzeramenti"], bool) and dati["azzeramenti"] >= 0:
        pulite["azzeramenti"] = dati["azzeramenti"]
    pulite["sessione_aperta"] = dati.get("sessione_aperta") is True
    for chiave in ("conti", "eventi", "tasti", "senza_comando", "tempi", "modi", "sorgenti", "schede_audio", "impostazioni"):
        pulite[chiave] = _numeri(dati.get(chiave))
    pulite["bande"] = _lista_di_numeri(dati.get("bande"), len(valori.FREQUENZE_DELLE_BANDE))
    pulite["ore"] = _lista_di_numeri(dati.get("ore"), 24)
    pulite["settimana"] = _lista_di_numeri(dati.get("settimana"), 7)
    for chiave in ("formati", "giorni"):
        if isinstance(dati.get(chiave), dict):
            pulite[chiave] = {str(k): _numeri(v) for k, v in dati[chiave].items() if isinstance(v, dict)}
    if isinstance(dati.get("versioni"), dict):
        pulite["versioni"] = {str(k): v for k, v in dati["versioni"].items() if isinstance(v, str)}
    if isinstance(dati.get("record"), dict):
        pulite["record"] = {str(k): v for k, v in dati["record"].items() if isinstance(v, dict) and _numero(v.get("valore", 0))}
    if isinstance(dati.get("brani"), dict):
        brani = {}
        for percorso, brano in dati["brani"].items():
            if not isinstance(brano, dict):
                continue
            pulito = _numeri(brano)
            if isinstance(brano.get("ultima"), str):
                pulito["ultima"] = brano["ultima"]
            if isinstance(brano.get("sotto"), list):
                pulito["sotto"] = [n for n in brano["sotto"] if isinstance(n, int) and not isinstance(n, bool)][:MASSIMO_DEI_SOTTOBRANI]
            brani[str(percorso)] = pulito
        pulite["brani"] = brani
    return pulite


class Statistiche:
    """I conti e il loro file. adesso e' l'orologio dei passi, in secondi;
    ora da' la data e l'ora di adesso: le prove li sostituiscono."""

    def __init__(self, percorso, adesso=time.monotonic, ora=datetime.datetime.now):
        self.percorso = percorso
        self._adesso = adesso
        self._ora = ora
        self.errore = None
        self.da_nuovo = False
        self.dati = _vuote(self._iso())
        # La sessione di adesso, che non si salva: il suo inizio, il tempo
        # aperto, i brani avviati e i tasti premuti.
        self.sessione = {"numero": 0, "inizio": self._iso(), "aperto": 0.0, "brani": 0, "tasti": 0}
        # L'orologio: quando e' scattato l'ultima volta, e lo stato di allora.
        self._ultimo_scatto = None
        self._stato = None
        # Il brano in corso: percorso, secondi ascoltati e durata, finche' non
        # finisce, non lo si lascia o non da' errore.
        self._brano = None
        # La riproduzione di fila: da quando, quanti secondi, quanti brani; e
        # da quanto si e' fermi, perche' il passaggio fra due brani non la rompa.
        self._filata = 0.0
        self._inizio_della_filata = None
        self._brani_di_fila = 0
        self._fermo_di_fila = 0.0
        # Da quanto dura la pausa di adesso.
        self._pausa = 0.0
        # La versione di MeTeOra di questa sessione, che l'azzeramento tiene.
        self._versione = None
        # La scrittura in disparte, e il lucchetto che ne fa una alla volta.
        self._scrittura = None
        self._lucchetto = threading.Lock()

    def _iso(self):
        return self._ora().isoformat(timespec="seconds")

    # Il file.

    def carica(self):
        """Legge il file. Un file che non si legge non si sovrascrive: errore
        dice perche', e i conti ripartono accanto, con .nuovo; alla volta dopo,
        se il file e' ancora illeggibile, si riparte da quello."""
        if not os.path.isfile(self.percorso):
            return
        try:
            dati = self._leggi(self.percorso)
        except (OSError, ValueError, RecursionError) as e:
            self.errore = str(e) or type(e).__name__
            self.percorso += ".nuovo"
            dati = None
            with contextlib.suppress(OSError, ValueError, RecursionError):
                dati = self._leggi(self.percorso) if os.path.isfile(self.percorso) else None
            self.da_nuovo = dati is not None
        if dati is not None:
            self.dati = _pulite(dati, self._iso())

    @staticmethod
    def _leggi(percorso):
        with open(percorso, encoding="utf-8") as f:
            dati = json.load(f)
        if not isinstance(dati, dict):
            raise ValueError("il file non contiene le statistiche")
        return dati

    def _testo(self):
        self.dati["salvato"] = self._iso()
        return json.dumps(self.dati, ensure_ascii=False, separators=(",", ":"))

    def _scrivi(self, testo):
        with self._lucchetto:
            provvisorio = self.percorso + ".tmp"
            with open(provvisorio, "w", encoding="utf-8") as f:
                f.write(testo)
            os.replace(provvisorio, self.percorso)

    def salva(self):
        """Scrive il file adesso, aspettando la scrittura in disparte, se c'e'."""
        if self._scrittura is not None:
            self._scrittura.join()
            self._scrittura = None
        self._scrivi(self._testo())

    def salva_in_disparte(self, al_guasto=None):
        """Il testo si prepara qui, la scrittura la fa un filo a parte: con
        tanti brani il file pesa qualche MB, e la finestra non deve fermarsi.
        Se la scrittura di prima non ha finito, questa si salta. al_guasto(e)
        arriva dal filo, con l'errore del disco."""
        if self._scrittura is not None and self._scrittura.is_alive():
            return
        testo = self._testo()

        def scrivi():
            try:
                self._scrivi(testo)
            except OSError as e:
                if al_guasto is not None:
                    al_guasto(e)

        self._scrittura = threading.Thread(target=scrivi, name="MeTeOra, statistiche", daemon=True)
        self._scrittura.start()

    # La sessione.

    def avvio(self, versione, versione_di_prima=None):
        """Un avvio di MeTeOra. Se la sessione di prima non si e' chiusa, e'
        una chiusura non regolare, all'ora dell'ultimo salvataggio."""
        d = self.dati
        if d["sessione_aperta"]:
            self.conta("chiusure_non_regolari")
            d["record"]["chiusura_non_regolare"] = {"valore": 0, "quando": d["salvato"] or self._iso()}
        d["sessione_aperta"] = True
        self.conta("avvii")
        self._versione = versione
        d["versioni"].setdefault(versione, self._iso())
        if versione_di_prima and versione_di_prima != versione:
            self.conta("aggiornamenti")
        self.sessione = {"numero": d["conti"]["avvii"], "inizio": self._iso(), "aperto": 0.0, "brani": 0, "tasti": 0}

    def chiusura(self):
        """L'uscita regolare: l'ultimo passo dell'orologio, il brano in corso,
        la sessione piu' breve."""
        if self._stato is not None:
            self.scatta(self._stato)
        self._chiudi_il_brano("chiusura")
        self._minimo("sessione_piu_breve", self.sessione["aperto"], quando=self.sessione["inizio"])
        self.conta("chiusure_regolari")
        self.dati["sessione_aperta"] = False

    def azzera(self):
        """Tutto da capo, da adesso: restano la data della prima raccolta e il
        numero degli azzeramenti. La sessione di adesso conta come la prima."""
        vecchie = self.dati
        self.dati = _vuote(self._iso())
        self.dati["prima_raccolta"] = vecchie["prima_raccolta"]
        self.dati["azzeramenti"] = vecchie["azzeramenti"] + 1
        self.dati["ultimo_azzeramento"] = self._iso()
        self.dati["sessione_aperta"] = True
        self.dati["conti"]["avvii"] = 1
        if self._versione:
            self.dati["versioni"] = {self._versione: self._iso()}
        self.sessione = {"numero": 1, "inizio": self._iso(), "aperto": 0.0, "brani": 0, "tasti": 0}
        self._brano = None
        self._chiudi_la_filata()
        self._pausa = 0.0

    # I conti.

    def conta(self, nome, quanto=1):
        _piu(self.dati["conti"], nome, quanto)

    def evento(self, nome):
        _piu(self.dati["eventi"], nome)

    def tasto(self, nome):
        _piu(self.dati["tasti"], nome)
        self.sessione["tasti"] += 1
        self._massimo("tasti_in_una_sessione", self.sessione["tasti"], quando=self.sessione["inizio"])

    def senza_comando(self, nome):
        _piu(self.dati["senza_comando"], nome)

    def impostazione(self, chiave):
        """Invio su una voce della finestra delle impostazioni."""
        _piu(self.dati["impostazioni"], chiave)

    def banda(self, indice):
        if 0 <= indice < len(self.dati["bande"]):
            self.dati["bande"][indice] += 1

    def massimo(self, nome, valore, cosa=None):
        """Un record da tenere se e' il piu' alto, con cio' di cui parla."""
        self._massimo(nome, valore, **({"cosa": cosa} if cosa else {}))

    def _massimo(self, nome, valore, quando=None, **altro):
        # Un record che cresce, come la sessione di adesso, si riscrive con
        # lo stesso quando a ogni passo.
        attuale = self.dati["record"].get(nome)
        if attuale is None or valore > attuale.get("valore", 0):
            self.dati["record"][nome] = {"valore": valore, "quando": quando or self._iso(), **altro}

    def _minimo(self, nome, valore, quando=None, **altro):
        attuale = self.dati["record"].get(nome)
        if attuale is None or valore < attuale.get("valore", 0):
            self.dati["record"][nome] = {"valore": valore, "quando": quando or self._iso(), **altro}

    def _giorno(self, quando):
        return self.dati["giorni"].setdefault(quando.date().isoformat(), {})

    def _formato(self, estensione):
        return self.dati["formati"].setdefault(estensione or "senza estensione", {})

    def _del_brano(self, percorso):
        """La voce del brano nello storico; oltre il massimo escono i meno
        ascoltati, un centesimo alla volta."""
        brani = self.dati["brani"]
        voce = brani.get(percorso)
        if voce is None:
            if len(brani) >= MASSIMO_DEI_BRANI:
                via = sorted(brani, key=lambda p: (brani[p].get("secondi", 0), brani[p].get("volte", 0)))[:max(1, MASSIMO_DEI_BRANI // 100)]
                for p in via:
                    del brani[p]
            voce = brani[percorso] = {}
        return voce

    # L'orologio.

    def scatta(self, stato):
        """Un passo dell'orologio. stato e' un dizionario: "stato" vale play,
        pausa o fermo; poi percorso, video, immagine, schermo_intero, volume,
        muto, velocita, tono, eq, dissolvenza, casuale, ripetizione,
        replaygain, scheda, sorgente, e durata, una funzione chiamata solo
        se la durata del brano serve. Il tempo dall'ultimo passo va allo
        stato di allora."""
        adesso = self._adesso()
        prima, self._stato = self._stato, stato
        if self._ultimo_scatto is None:
            self._ultimo_scatto = adesso
            return
        passo = min(max(0.0, adesso - self._ultimo_scatto), PASSO_MASSIMO)
        self._ultimo_scatto = adesso
        if passo > 0 and prima is not None:
            self._accumula(prima, passo)

    def _accumula(self, s, dt):
        quando = self._ora()
        tempi = self.dati["tempi"]
        giorno = self._giorno(quando)
        _piu(tempi, "aperto", dt)
        _piu(giorno, "aperto", dt)
        self.sessione["aperto"] += dt
        self._massimo("sessione_piu_lunga", round(self.sessione["aperto"], 3), quando=self.sessione["inizio"])
        stato = s.get("stato")
        if stato != "pausa":
            self._pausa = 0.0
        if stato == "fermo":
            _piu(tempi, "fermo", dt)
            self._fermo_di_fila += dt
            if self._fermo_di_fila > PASSO_MASSIMO:
                self._chiudi_la_filata()
            return
        if stato == "pausa":
            _piu(tempi, "pausa", dt)
            if not self._pausa:
                # Una pausa nuova, anche quella del brano ripreso all'avvio.
                self.conta("pause")
            self._pausa += dt
            self._massimo("pausa_piu_lunga", round(self._pausa, 3))
            self._chiudi_la_filata()
            return
        self._fermo_di_fila = 0.0
        _piu(tempi, "play", dt)
        _piu(giorno, "play", dt)
        self.dati["ore"][quando.hour] = round(self.dati["ore"][quando.hour] + dt, 3)
        self.dati["settimana"][quando.weekday()] = round(self.dati["settimana"][quando.weekday()] + dt, 3)
        percorso = s.get("percorso") or ""
        _piu(self._formato(formati.estensione(percorso)), "secondi", dt)
        if s.get("video"):
            _piu(tempi, "play_video", dt)
            _piu(tempi, "video_immagine" if s.get("immagine") else "video_senza_immagine", dt)
            if s.get("schermo_intero"):
                _piu(tempi, "schermo_intero", dt)
        else:
            _piu(tempi, "play_audio", dt)
        volume = s.get("volume") or 0
        _piu(tempi, "volume_pesato", volume * dt)
        if volume > 100:
            _piu(tempi, "oltre_100", dt)
        if s.get("muto"):
            _piu(tempi, "muto", dt)
        velocita = s.get("velocita") or 1.0
        if abs(velocita - 1) > 1e-6:
            _piu(tempi, "velocita_cambiata", dt)
            _piu(tempi, "contenuto_a_velocita_cambiata", velocita * dt)
        if s.get("tono"):
            _piu(tempi, "tono_cambiato", dt)
        for chiave in ("eq", "dissolvenza", "casuale"):
            if s.get(chiave):
                _piu(tempi, chiave, dt)
        if s.get("ripetizione") in ("brano", "lista"):
            _piu(tempi, f"ripetizione_{s['ripetizione']}", dt)
        if s.get("replaygain") in ("brano", "album"):
            _piu(tempi, f"replaygain_{s['replaygain']}", dt)
        _piu(self.dati["schede_audio"], s.get("scheda") or "Automatica", dt)
        _piu(self.dati["sorgenti"], s.get("sorgente") or "altro", dt)
        if percorso:
            _piu(self._del_brano(percorso), "secondi", dt)
        brano = self._brano
        if brano is not None and brano["percorso"] == percorso:
            brano["ascoltato"] += dt
            if brano["durata"] is None and callable(s.get("durata")):
                brano["durata"] = s["durata"]()
        if self._inizio_della_filata is None:
            self._inizio_della_filata = self._iso()
            self._brani_di_fila = 1
            self._filata = 0.0
        self._filata += dt
        self._massimo("filata", round(self._filata, 3), quando=self._inizio_della_filata, brani=self._brani_di_fila)
        self._massimo("volume_piu_alto", volume)
        self._massimo("velocita_piu_alta", velocita)
        self._minimo("velocita_piu_bassa", velocita)
        tono = s.get("tono") or 0
        self._massimo("tono_piu_alto", tono)
        self._minimo("tono_piu_basso", tono)

    def _chiudi_la_filata(self):
        self._inizio_della_filata = None
        self._filata = 0.0
        self._brani_di_fila = 0
        self._fermo_di_fila = 0.0

    # La vita dei brani.

    def brano_avviato(self, percorso, sottobrano=None, modo="play", a_caso=False):
        """Un brano e' partito: modo e' l'evento del suo annuncio. Il brano di
        prima, se non e' finito, e' lasciato."""
        self._chiudi_il_brano("lasciato")
        quando = self._ora()
        _piu(self._formato(formati.estensione(percorso)), "avvii")
        _piu(self.dati["modi"], modo)
        if a_caso:
            self.conta("a_caso")
        _piu(self._giorno(quando), "avvii")
        self.sessione["brani"] += 1
        self._massimo("brani_in_una_sessione", self.sessione["brani"], quando=self.sessione["inizio"])
        if self._inizio_della_filata is not None:
            self._brani_di_fila += 1
        voce = self._del_brano(percorso)
        _piu(voce, "volte")
        voce["ultima"] = self._iso()
        if sottobrano:
            sotto = voce.setdefault("sotto", [])
            if sottobrano not in sotto and len(sotto) < MASSIMO_DEI_SOTTOBRANI:
                sotto.append(sottobrano)
        self._brano = {"percorso": percorso, "ascoltato": 0.0, "durata": None}

    def brano_finito(self):
        """Il brano in corso e' arrivato alla fine da solo."""
        brano = self._brano
        if brano is None:
            return
        self._brano = None
        _piu(self._formato(formati.estensione(brano["percorso"])), "finiti")
        _piu(self._del_brano(brano["percorso"]), "finiti")
        self.conta("finiti")
        d = brano["durata"]
        if _numero(d) and 0 < d < DURATA_CREDIBILE:
            self._massimo("finito_piu_lungo", round(d, 3), cosa=brano["percorso"])
            self._minimo("finito_piu_breve", round(d, 3), cosa=brano["percorso"])

    def brano_fermato(self):
        """Lo stop, con V o con il timer: il brano in corso e' lasciato."""
        self._chiudi_il_brano("lasciato")

    def brano_in_errore(self, percorso):
        """Un brano che non si suona."""
        percorso = percorso or (self._brano or {}).get("percorso") or ""
        _piu(self._formato(formati.estensione(percorso)), "errori")
        self.conta("errori_di_riproduzione")
        if self._brano is not None and self._brano["percorso"] == percorso:
            self._brano = None

    def _chiudi_il_brano(self, come):
        brano = self._brano
        if brano is None:
            return
        self._brano = None
        if come == "chiusura":
            self.conta("in_corso_alla_chiusura")
            return
        self.conta("lasciati")
        self.conta("secondi_dei_lasciati", round(brano["ascoltato"], 3))
        if brano["ascoltato"] < SUBITO:
            self.conta("lasciati_subito")

    def marker_messo(self, percorso):
        _piu(self._del_brano(percorso), "marker")
        _piu(self._giorno(self._ora()), "marker")

    # Lo storico dei brani: la pulizia all'avvio e i file rinominati (1.104.0).

    def percorsi_dei_brani(self):
        """I percorsi dello storico dei brani, cosi' come sono scritti, da
        controllare nella pulizia all'avvio: una lista nuova, che si puo'
        passare a un filo."""
        return list(self.dati["brani"])

    def togli_i_brani(self, mancanti, in_corso=None):
        """La pulizia all'avvio: le voci dei file mancanti, un insieme di
        percorsi gia' normalizzati con normcase e abspath, escono dallo
        storico. Restano il brano in corso e in_corso, il file che suona
        adesso, anche se mancano. I totali non cambiano, come quando lo
        storico supera il tetto: conti, tempi, formati, giorni, ore,
        settimana, modi e record dicono anche dei file che non ci sono
        piu'. Calano invece i conti che la pagina ricava dallo storico: i
        file diversi ascoltati, quelli ascoltati una volta sola o piu' di 10
        volte, i sottobrani diversi, la durata media dei brani avviati e le
        classifiche, dei brani, degli autori, degli album, dei generi, degli
        anni, delle cartelle e delle unita', e il brano con piu' marker.
        Restituisce quante voci ha tolto."""
        if not mancanti:
            return 0
        salvi = {_norm(p) for p in (in_corso, (self._brano or {}).get("percorso")) if p}
        brani = self.dati["brani"]
        tolti = 0
        for percorso in list(brani):
            normalizzato = _norm(percorso)
            if normalizzato in mancanti and normalizzato not in salvi:
                del brani[percorso]
                tolti += 1
        return tolti

    def rinomina_brano(self, vecchio, nuovo):
        """Un file rinominato sul disco: la sua voce dello storico passa al
        nome nuovo, trovata con il percorso normalizzato. Se il nome nuovo
        ha gia' una voce, si uniscono, e cosi' le voci dello stesso file
        scritte in due forme. Anche il brano in corso segue il file, se e'
        lui, e cosi' lo stato del passo di prima dell'orologio, perche' il
        tempo del passo dopo vada al nome nuovo e non ricrei la voce del
        vecchio. I totali non cambiano. Restituisce vero se una voce e'
        passata al nome nuovo."""
        da, a = _norm(vecchio), _norm(nuovo)
        if self._brano is not None and _norm(self._brano["percorso"]) == da:
            self._brano["percorso"] = nuovo
        stato = self._stato
        if isinstance(stato, dict) and isinstance(stato.get("percorso"), str) and stato["percorso"] and _norm(stato["percorso"]) == da:
            # Una copia: il dizionario e' della finestra, che puo' tenerlo.
            self._stato = {**stato, "percorso": nuovo}
        brani = self.dati["brani"]
        vecchie, nuove = [], []
        for percorso in brani:
            normalizzato = _norm(percorso)
            if normalizzato == da:
                vecchie.append(percorso)
            elif normalizzato == a:
                nuove.append(percorso)
        if not vecchie:
            return False
        voce = {}
        # Prima le voci del nome vecchio, che e' il file sul disco: i suoi
        # sottobrani vengono per primi.
        for percorso in vecchie + nuove:
            voce = _unisci(voce, brani.pop(percorso))
        brani[nuovo] = voce
        return True

    # La pagina.

    def righe(self, versione, scheda=lambda _percorso: None, libreria=None, numeri_della_libreria=None, comandi_dei_tasti=None,
            nomi_delle_impostazioni=None):
        """Le righe della pagina. scheda(percorso) da' la scheda dello
        schedario, per i tag e le durate; libreria sono le righe della
        sezione della libreria di adesso, e numeri_della_libreria i suoi
        numeri che servono altrove, da numeri_della_libreria();
        comandi_dei_tasti dice il comando di ogni tasto a carattere, per
        nome; nomi_delle_impostazioni il nome di ogni voce delle impostazioni."""
        return Pagina(self, versione, scheda, libreria, numeri_della_libreria or {}, comandi_dei_tasti or {}, nomi_delle_impostazioni or {}).righe()


class Pagina:
    """Le righe della pagina delle statistiche, sezione per sezione."""

    def __init__(self, statistiche, versione, scheda, libreria, numeri_della_libreria, comandi_dei_tasti, nomi_delle_impostazioni):
        self.s = statistiche
        self.d = statistiche.dati
        self.versione = versione
        self.scheda = scheda
        self.libreria = libreria
        self.numeri_della_libreria = numeri_della_libreria
        self.file_nella_libreria = numeri_della_libreria.get("file")
        self.comandi_dei_tasti = comandi_dei_tasti
        self.nomi_delle_impostazioni = nomi_delle_impostazioni
        self.oggi = statistiche._ora()
        self.conti = self.d["conti"]
        self.eventi = self.d["eventi"]
        self.tempi = self.d["tempi"]
        self.play = self.tempi.get("play", 0)
        self._tag = {}

    def c(self, nome):
        return int(self.conti.get(nome, 0))

    def e(self, nome):
        return int(self.eventi.get(nome, 0))

    def t(self, nome):
        return self.tempi.get(nome, 0)

    def tag(self, percorso):
        """I tag di un brano dallo schedario, ricordati per questa pagina."""
        if percorso not in self._tag:
            scheda = self.scheda(percorso) or {}
            self._tag[percorso] = (scheda.get("tag") or {}, scheda.get("durata"))
        return self._tag[percorso]

    def avviati(self):
        return int(sum(self.d["modi"].values()))

    def marker_eliminati(self):
        return sum(self.c(f"marker_tolti_{come}") for come in ("uno", "prima", "dopo", "tutti", "selezione", "finestra"))

    def sezioni(self):
        return [
            ("In breve", self.in_breve),
            ("Le sessioni", self.le_sessioni),
            ("Il tempo", self.il_tempo),
            ("Il tempo per famiglia", self.per_famiglia),
            ("Il tempo per formato", self.per_formato),
            ("Come hai ascoltato", self.come_hai_ascoltato),
            ("I brani", self.i_brani),
            ("Le classifiche", self.le_classifiche),
            ("Il calendario", self.il_calendario),
            ("I record", self.i_record),
            ("Muoversi nel brano", self.muoversi),
            ("I marker", self.i_marker),
            ("Playlist e Preferiti", self.le_playlist),
            ("Ricerca e filtri", self.la_ricerca),
            ("File e tag", self.file_e_tag),
            ("Video, sottotitoli e karaoke", self.il_video),
            ("Plancia e tastiera", self.la_tastiera),
            ("Console e aiuto", self.la_console),
            ("Impostazioni, rete e MIDI", self.le_impostazioni),
            ("La salute", self.la_salute),
            ("La libreria di adesso", self.la_libreria),
            ("Curiosità", self.curiosita),
            ("Tutti gli eventi", self.tutti_gli_eventi),
        ]

    def righe(self):
        sezioni = self.sezioni()
        dal = _leggi_data(self.d["dal"]) or self.oggi
        giorni = max(1, (self.oggi.date() - dal.date()).days + 1)
        righe = [f"Statistiche di MeTeOra {self.versione}, raccolte {data_e_ora(self.d['dal'], 'da')}: {al_plurale(giorni, 'giorno', 'giorni')}, oggi compreso."]
        if self.d["azzeramenti"]:
            righe.append(f"Prima raccolta: {data_e_ora(self.d['prima_raccolta'])}. Azzerate {al_plurale(self.d['azzeramenti'], 'volta', 'volte')}, "
                f"l'ultima {data_e_ora(self.d['ultimo_azzeramento'])}.")
        righe.append("La barra rovesciata cerca nel testo, e Invio passa all'occorrenza seguente; senza una ricerca, Invio ed Esc chiudono. "
            "Azzera le statistiche le riporta a zero.")
        righe.append("Le sezioni: " + "; ".join(f"{n} {titolo}" for n, (titolo, _f) in enumerate(sezioni, 1)) + ".")
        for n, (titolo, funzione) in enumerate(sezioni, 1):
            righe.append("")
            righe.append(f"Sezione {n} di {len(sezioni)}, {titolo[0].lower()}{titolo[1:]}.")
            try:
                contenuto = [r for r in funzione() if r]
            except Exception as e:  # noqa: BLE001 - una sezione che non si compone non deve togliere le altre
                contenuto = [f"Questa sezione non si è potuta comporre: {type(e).__name__}, {e}."]
            righe.extend(contenuto or ["Ancora niente da dire."])
        return righe

    # 1.

    def in_breve(self):
        avviati, finiti = self.avviati(), self.c("finiti")
        righe = [
            f"Avvii di MeTeOra: {self.c('avvii')}.",
            f"MeTeOra aperto: {durata(self.t('aperto'))}.",
            f"In riproduzione: {durata(self.play)}, {percentuale(self.play, self.t('aperto'))} del tempo aperto.",
            f"Brani avviati: {avviati}; ascoltati fino alla fine: {finiti}, {percentuale(finiti, avviati)}.",
            self.riga_dei_file_diversi(),
        ]
        formato = self.formati_in_ordine()
        if formato:
            estensione, voce = formato[0]
            righe.append(f"Il formato più ascoltato: {estensione.lstrip('.')}, {durata(voce.get('secondi', 0))}, {percentuale(voce.get('secondi', 0), self.play)} della riproduzione.")
        primo = self.brani_per_volte()[:1]
        if primo:
            percorso, voce = primo[0]
            righe.append(f"Il brano più ascoltato: {_nome(percorso)}, {al_plurale(int(voce.get('volte', 0)), 'volta', 'volte')}.")
        righe.append(f"Marker messi: {self.e('marker_messo')}; eliminati: {self.marker_eliminati()}.")
        return righe

    def riga_dei_file_diversi(self):
        diversi = sum(1 for voce in self.d["brani"].values() if voce.get("volte"))
        if self.file_nella_libreria:
            return f"File diversi ascoltati: {diversi}, {percentuale(diversi, self.file_nella_libreria)} dei {self.file_nella_libreria} file dello schedario."
        return f"File diversi ascoltati: {diversi}."

    # 2.

    def le_sessioni(self):
        s = self.s.sessione
        record = self.d["record"]
        avvii = self.c("avvii")
        righe = [f"Questa è la sessione numero {s['numero']}, aperta {data_e_ora(s['inizio'])}: da {durata(s['aperto'])}."]
        if avvii:
            righe.append(f"Durata media di una sessione: {durata(self.t('aperto') / avvii)}.")
        if "sessione_piu_lunga" in record:
            righe.append(f"La sessione più lunga: {durata(record['sessione_piu_lunga']['valore'])}, cominciata {data_e_ora(record['sessione_piu_lunga']['quando'])}.")
        if "sessione_piu_breve" in record:
            righe.append(f"La sessione più breve: {durata(record['sessione_piu_breve']['valore'])}, cominciata {data_e_ora(record['sessione_piu_breve']['quando'])}.")
        if "brani_in_una_sessione" in record:
            righe.append(f"Più brani in una sessione: {record['brani_in_una_sessione']['valore']}, nella sessione cominciata {data_e_ora(record['brani_in_una_sessione']['quando'])}.")
        righe.append(f"Chiusure regolari: {self.c('chiusure_regolari')}.")
        non_regolari = self.c("chiusure_non_regolari")
        riga = f"Chiusure non regolari, con MeTeOra caduto, chiuso a forza o il PC spento: {non_regolari}"
        if non_regolari and "chiusura_non_regolare" in record:
            riga += f"; l'ultima dopo il salvataggio {data_e_ora(record['chiusura_non_regolare']['quando'], 'di')}"
        righe.append(riga + ".")
        righe.append(f"Avvii con un file aperto da Windows: {self.c('aperti_all_avvio')}.")
        righe.append(f"File e cartelle passati a MeTeOra già aperto, da Windows o da un'altra copia: {self.c('aperti_da_un_altra_copia')}.")
        righe.append(f"File e cartelle trascinati sulla finestra: {self.c('aperti_col_trascinamento')}.")
        righe.append(f"Avvii con la ripresa del brano lasciato: {self.e('ripresa_all_avvio')}.")
        righe.append(f"Aggiornamenti di MeTeOra: {self.c('aggiornamenti')}.")
        versioni = sorted(self.d["versioni"].items(), key=lambda v: v[1])
        if versioni:
            righe.append("Versioni usate: " + ", ".join(f"{v} {solo_la_data(quando, 'da')}" for v, quando in versioni) + ".")
        return righe

    # 3.

    def il_tempo(self):
        aperto = self.t("aperto")
        video = self.t("play_video")
        righe = [
            f"MeTeOra aperto: {durata(aperto)}.",
            f"In riproduzione: {durata(self.play)}, {percentuale(self.play, aperto)} del tempo aperto.",
            f"In pausa: {durata(self.t('pausa'))}, {percentuale(self.t('pausa'), aperto)}.",
            f"Fermo, senza niente che suona: {durata(self.t('fermo'))}, {percentuale(self.t('fermo'), aperto)}.",
            f"Riproduzione di audio: {durata(self.t('play_audio'))}, {percentuale(self.t('play_audio'), self.play)} della riproduzione.",
            f"Riproduzione di video: {durata(video)}, {percentuale(video, self.play)}.",
        ]
        if video:
            righe.append(f"Video con l'immagine: {durata(self.t('video_immagine'))}, {percentuale(self.t('video_immagine'), video)} del tempo dei video.")
            righe.append(f"Video con l'immagine spenta, solo l'audio: {durata(self.t('video_senza_immagine'))}, {percentuale(self.t('video_senza_immagine'), video)}.")
            righe.append(f"Video a schermo intero: {durata(self.t('schermo_intero'))}.")
        pause = self.c("pause")
        riga = f"Pause: {pause}"
        if pause:
            riga += f", lunghe in media {durata(self.t('pausa') / pause)}"
        if "pausa_piu_lunga" in self.d["record"]:
            riga += f"; la più lunga: {durata(self.d['record']['pausa_piu_lunga']['valore'])}"
        righe.append(riga + ".")
        filata = self.d["record"].get("filata")
        if filata:
            righe.append(f"La riproduzione più lunga senza fermarsi: {durata(filata['valore'])}, {al_plurale(int(filata.get('brani', 1)), 'brano', 'brani di fila')}, "
                f"cominciata {data_e_ora(filata['quando'])}.")
        return righe

    # 4 e 5.

    def formati_in_ordine(self):
        voci = [(e, v) for e, v in self.d["formati"].items() if v.get("secondi") or v.get("avvii")]
        return sorted(voci, key=lambda ev: (-ev[1].get("secondi", 0), -ev[1].get("avvii", 0), ev[0]))

    def per_famiglia(self):
        famiglie = {f: {"secondi": 0, "avvii": 0} for f in FAMIGLIE}
        for estensione, voce in self.d["formati"].items():
            f = famiglie[famiglia(f"x{estensione}")]
            f["secondi"] += voce.get("secondi", 0)
            f["avvii"] += voce.get("avvii", 0)
        ordine = list(FAMIGLIE)
        righe = []
        # Solo le famiglie suonate: senza nessuna, la sezione dice che non
        # c'e' ancora niente da dire (1.104.0).
        suonate = [f for f in famiglie if famiglie[f]["secondi"] or famiglie[f]["avvii"]]
        for chiave in sorted(suonate, key=lambda f: (-famiglie[f]["secondi"], -famiglie[f]["avvii"], ordine.index(f))):
            f = famiglie[chiave]
            righe.append(f"{FAMIGLIE[chiave]}: {durata(f['secondi'])}, {percentuale(f['secondi'], self.play)} della riproduzione; "
                f"{al_plurale(int(f['avvii']), 'avvio', 'avvii')}.")
        return righe

    def per_formato(self):
        voci = self.formati_in_ordine()
        suonati = {e for e, _v in voci}
        righe = [f"Formati suonati: {len(voci)} dei {len(formati.TUTTI)} che MeTeOra conosce."]
        for estensione, voce in voci:
            avvii = int(voce.get("avvii", 0))
            riga = f"{estensione.lstrip('.')}: {durata(voce.get('secondi', 0))}, {percentuale(voce.get('secondi', 0), self.play)}; {al_plurale(avvii, 'avvio', 'avvii')}"
            if avvii:
                riga += f", {percentuale(voce.get('finiti', 0), avvii)} fino alla fine"
            righe.append(riga + ".")
        # Solo quanti sono, senza l'elenco dei nomi (1.104.0).
        mai = len(formati.TUTTI - suonati)
        if mai:
            righe.append(f"Formati mai suonati: {mai}.")
        return righe

    # 6.

    def come_hai_ascoltato(self):
        record = self.d["record"]
        righe = []
        if self.play:
            riga = f"Volume medio, pesato sul tempo: {round(self.t('volume_pesato') / self.play)}"
            if "volume_piu_alto" in record:
                riga += f"; il più alto raggiunto: {record['volume_piu_alto']['valore']}"
            righe.append(riga + ".")
        righe.append(f"Volume oltre 100, con il limitatore: {durata(self.t('oltre_100'))}, {percentuale(self.t('oltre_100'), self.play)} della riproduzione.")
        righe.append(f"In muto mentre suonava: {durata(self.t('muto'))}.")
        cambiata = self.t("velocita_cambiata")
        riga = f"Velocità diversa dal normale: {durata(cambiata)}, {percentuale(cambiata, self.play)}"
        if cambiata and "velocita_piu_alta" in record:
            riga += f"; la più alta {numero_decimale(record['velocita_piu_alta']['valore'])}, la più bassa {numero_decimale(record.get('velocita_piu_bassa', {}).get('valore', 1))}"
        righe.append(riga + ".")
        if cambiata:
            contenuto = self.t("contenuto_a_velocita_cambiata")
            guadagno = contenuto - cambiata
            if guadagno >= 0:
                righe.append(f"Tempo guadagnato con la velocità: {durata(guadagno)}; brani che duravano {durata(contenuto)} ascoltati in {durata(cambiata)}.")
            else:
                righe.append(f"Tempo in più con la velocità: {durata(-guadagno)}; brani che duravano {durata(contenuto)} ascoltati in {durata(cambiata)}.")
        riga = f"Tono cambiato: {durata(self.t('tono_cambiato'))}"
        if self.t("tono_cambiato") and "tono_piu_alto" in record:
            alto, basso = int(record["tono_piu_alto"]["valore"]), int(record.get("tono_piu_basso", {}).get("valore", 0))
            riga += f"; il più alto {alto:+d} {'semitono' if abs(alto) == 1 else 'semitoni'}, il più basso {basso:+d}"
        righe.append(riga + ".")
        righe.append(f"Equalizzatore con almeno una banda fuori dallo zero: {durata(self.t('eq'))}, {percentuale(self.t('eq'), self.play)}.")
        bande = self.d["bande"]
        if any(bande):
            indice = max(range(len(bande)), key=lambda i: bande[i])
            righe.append(f"La banda più ritoccata: {valori.nome_della_banda(indice)}, {al_plurale(int(bande[indice]), 'volta', 'volte')}; "
                f"in tutto {al_plurale(int(sum(bande)), 'ritocco', 'ritocchi')}.")
        righe.append(f"Dissolvenza incrociata accesa: {durata(self.t('dissolvenza'))}, {percentuale(self.t('dissolvenza'), self.play)}; passaggi sfumati: {self.c('passaggi_sfumati')}.")
        righe.append(f"Riproduzione casuale accesa: {durata(self.t('casuale'))}, {percentuale(self.t('casuale'), self.play)}; brani scelti a caso: {self.c('a_caso')}.")
        righe.append(f"Ripetizione del brano: {durata(self.t('ripetizione_brano'))}; ripetizione della lista: {durata(self.t('ripetizione_lista'))}.")
        righe.append(f"Volume uniforme con ReplayGain: per brano {durata(self.t('replaygain_brano'))}, per album {durata(self.t('replaygain_album'))}.")
        schede = sorted(((nome, secondi) for nome, secondi in self.d["schede_audio"].items() if secondi), key=lambda s: -s[1])
        if schede:
            righe.append("Schede audio: " + "; ".join(f"{nome}, {percentuale(secondi, self.play)}" for nome, secondi in schede) + ".")
        return righe

    # 7.

    def i_brani(self):
        modi = Counter()
        for modo, quanti in self.d["modi"].items():
            modi[MODI.get(modo, "scelti")] += int(quanti)
        avviati = self.avviati()
        finiti, lasciati, errori = self.c("finiti"), self.c("lasciati"), self.c("errori_di_riproduzione")
        righe = [
            f"Brani avviati: {avviati}.",
            f"Scelti da te, con X, Invio, il menu, un marker o un capitolo: {modi['scelti']}.",
            f"Partiti da soli, alla fine del brano prima: {modi['da_soli']}; di questi, tornando al punto A del loop: {int(self.d['modi'].get('ritorno_al_punto_a', 0))}.",
            f"Con B: {modi['b']}; con Z: {modi['z']}; con N, a caso: {modi['n']}.",
            f"Aprendo una playlist con J, K o le cifre: {modi['playlist']}.",
            f"Ripresi all'avvio: {modi['ripresa']}.",
            f"Ascoltati fino alla fine: {finiti}, {percentuale(finiti, avviati)}.",
            f"Lasciati prima della fine: {lasciati}, {percentuale(lasciati, avviati)}; di questi, nei primi {int(SUBITO)} secondi: {self.c('lasciati_subito')}.",
            f"Non suonati per un errore: {errori}, {percentuale(errori, avviati)}.",
            f"Ancora in corso quando hai chiuso MeTeOra: {self.c('in_corso_alla_chiusura')}.",
            f"Ripartiti da capo con X, non contati come avvii: {self.e('da_capo')}.",
            self.riga_dei_file_diversi(),
        ]
        brani = self.d["brani"].values()
        righe.append(f"Ascoltati una volta sola: {sum(1 for v in brani if v.get('volte') == 1)}; più di 10 volte: {sum(1 for v in brani if v.get('volte', 0) > 10)}.")
        righe.append(f"Sottobrani diversi dei SID e delle console: {sum(len(v.get('sotto', [])) for v in brani)}.")
        durate = [(v.get("volte", 0), self.tag(p)[1]) for p, v in self.d["brani"].items() if v.get("volte")]
        note = [(volte, d) for volte, d in durate if _numero(d) and 0 < d < DURATA_CREDIBILE]
        if note:
            righe.append(f"Durata media dei brani avviati, dallo schedario: {durata(sum(v * d for v, d in note) / sum(v for v, _d in note))}.")
        if lasciati:
            righe.append(f"Ascolto medio prima di lasciare un brano: {durata(self.c('secondi_dei_lasciati') / lasciati)}.")
        righe.append(f"File lunghi ripresi dal punto lasciato: {self.c('ripresi_dal_punto')}.")
        return righe

    # 8.

    def brani_per_volte(self):
        voci = [(p, v) for p, v in self.d["brani"].items() if v.get("volte")]
        return sorted(voci, key=lambda pv: (-pv[1].get("volte", 0), -pv[1].get("secondi", 0), pv[0]))

    def di_chi(self, percorso):
        autore = self.tag(percorso)[0].get("autore")
        return f", di {autore}" if autore and autore != "<?>" else ""

    def classifica(self, titolo, conti, scrivi, posti=POSTI):
        """Le righe di una classifica: il titolo e i primi posti, gia' in ordine."""
        voci = list(conti)[:posti]
        if not voci:
            return []
        return [f"{titolo}:"] + [f"{n}. {scrivi(*voce) if isinstance(voce, tuple) else scrivi(voce)}" for n, voce in enumerate(voci, 1)]

    def le_classifiche(self):
        righe = []
        righe += self.classifica(f"I {POSTI} brani ascoltati più volte", self.brani_per_volte(),
            lambda p, v: f"{_nome(p)}{self.di_chi(p)}: {al_plurale(int(v.get('volte', 0)), 'volta', 'volte')}, {durata(v.get('secondi', 0))}.")
        per_tempo = sorted(((p, v) for p, v in self.d["brani"].items() if v.get("secondi")), key=lambda pv: (-pv[1]["secondi"], pv[0]))
        righe += self.classifica(f"I {POSTI} brani ascoltati più a lungo", per_tempo,
            lambda p, v: f"{_nome(p)}{self.di_chi(p)}: {durata(v['secondi'])}, in {al_plurale(int(v.get('volte', 0)), 'volta', 'volte')}.")
        tempo_dei_brani = sum(v.get("secondi", 0) for v in self.d["brani"].values())
        for chiave, titolo, senza in (("autore", "autori", "Senza autore nei tag"), ("album", "album", "Senza album nei tag"), ("genere", "generi", "Senza genere nei tag")):
            secondi, avvii, file = Counter(), Counter(), Counter()
            senza_tag = 0
            for p, v in self.d["brani"].items():
                valore = self.tag(p)[0].get(chiave)
                if not valore or valore == "<?>":
                    senza_tag += v.get("secondi", 0)
                    continue
                valore = str(valore)
                secondi[valore] += v.get("secondi", 0)
                avvii[valore] += v.get("volte", 0)
                file[valore] += 1
            # Una voce senza secondi e senza avvii, per esempio di un brano con
            # solo i marker, non entra in classifica (1.104.0).
            ordine = sorted((k for k in secondi if secondi[k] or avvii[k]), key=lambda k: (-secondi[k], k))
            if not ordine:
                continue
            righe += self.classifica(f"I {POSTI} {titolo} più ascoltati, dai tag", ordine,
                lambda k, secondi=secondi, avvii=avvii, file=file: f"{k}: {durata(secondi[k])}, {percentuale(secondi[k], tempo_dei_brani)}; "
                    f"{al_plurale(int(avvii[k]), 'avvio', 'avvii')} di {al_plurale(file[k], 'file', 'file')}.")
            righe.append(f"{senza}: {durata(senza_tag)}, {percentuale(senza_tag, tempo_dei_brani)}.")
        decenni, anni = Counter(), Counter()
        senza_anno = 0
        for p, v in self.d["brani"].items():
            anno = self.tag(p)[0].get("anno")
            # Un anno oltre quello di adesso e' un tag sbagliato: il suo tempo
            # va con quelli senza anno (1.104.0).
            if isinstance(anno, int) and not isinstance(anno, bool) and 0 < anno <= self.oggi.year:
                decenni[_decennio(anno)] += v.get("secondi", 0)
                anni[anno] += v.get("secondi", 0)
            else:
                senza_anno += v.get("secondi", 0)
        # Solo i decenni e gli anni con un po' d'ascolto, e senza anno se c'e'.
        decenni = {k: s for k, s in decenni.items() if s}
        anni = {a: s for a, s in anni.items() if s}
        if decenni:
            parti = [f"{k} {percentuale(s, tempo_dei_brani)}" for k, s in sorted(decenni.items(), key=lambda ks: -ks[1])]
            if senza_anno:
                parti.append(f"senza anno {percentuale(senza_anno, tempo_dei_brani)}")
            righe.append(f"Per decennio, dall'anno dei tag: {'; '.join(parti)}.")
            anno = max(anni, key=lambda a: (anni[a], -a))
            righe.append(f"L'anno più ascoltato: {anno}, {percentuale(anni[anno], tempo_dei_brani)}.")
        cartelle, unita = Counter(), Counter()
        for p, v in self.d["brani"].items():
            cartelle[ntpath.dirname(p) or p] += v.get("secondi", 0)
            unita[unita_di(p)] += v.get("secondi", 0)
        righe += self.classifica(f"Le {POSTI} cartelle più ascoltate", sorted(((k, s) for k, s in cartelle.items() if s), key=lambda ks: -ks[1]),
            lambda k, s: f"{k}: {durata(s)}, {percentuale(s, tempo_dei_brani)}.")
        if any(unita.values()):
            righe.append("Per unità: " + "; ".join(f"{k} {percentuale(s, tempo_dei_brani)}" for k, s in sorted(unita.items(), key=lambda ks: -ks[1]) if s) + ".")
        sorgenti = sorted(((nome, secondi) for nome, secondi in self.d["sorgenti"].items() if secondi), key=lambda s: -s[1])
        if sorgenti:
            righe.append("Da dove: " + "; ".join(f"{nome} {percentuale(secondi, self.play)}" for nome, secondi in sorgenti) + ".")
        return righe

    # 9.

    def il_calendario(self):
        giorni = {}
        for chiave, voce in self.d["giorni"].items():
            with contextlib.suppress(ValueError):
                giorni[datetime.date.fromisoformat(chiave)] = voce
        if not giorni:
            return []
        dal = (_leggi_data(self.d["dal"]) or self.oggi).date()
        di_calendario = max(1, (self.oggi.date() - dal).days + 1)
        aperti = [g for g, v in giorni.items() if v.get("aperto")]
        con_ascolto = sorted(g for g, v in giorni.items() if v.get("play"))
        righe = [f"Giorni con MeTeOra aperto: {len(aperti)} su {di_calendario}; con almeno un brano ascoltato: {len(con_ascolto)}."]
        if con_ascolto:
            totale = sum(giorni[g]["play"] for g in con_ascolto)
            righe.append(f"Ascolto medio nei giorni con ascolto: {durata(totale / len(con_ascolto))}.")
            record = max(con_ascolto, key=lambda g: giorni[g]["play"])
            righe.append(f"Il giorno con più ascolto: {data(record)}, {durata(giorni[record]['play'])}.")
            serie, inizio, migliore = 1, con_ascolto[0], (1, con_ascolto[0], con_ascolto[0])
            for prima, dopo in itertools.pairwise(con_ascolto):
                if (dopo - prima).days == 1:
                    serie += 1
                else:
                    serie, inizio = 1, dopo
                if serie > migliore[0]:
                    migliore = (serie, inizio, dopo)
            if migliore[0] > 1:
                righe.append(f"La serie più lunga di giorni di fila con ascolto: {migliore[0]}, {data(migliore[1], 'da')} {data(migliore[2], 'a')}.")
            else:
                righe.append("La serie più lunga di giorni di fila con ascolto: 1.")
            fine = self.oggi.date() if self.oggi.date() in giorni and giorni[self.oggi.date()].get("play") else self.oggi.date() - datetime.timedelta(days=1)
            di_adesso = 0
            presenti = set(con_ascolto)
            while fine - datetime.timedelta(days=di_adesso) in presenti:
                di_adesso += 1
            righe.append(f"La serie di adesso: {al_plurale(di_adesso, 'giorno', 'giorni')}.")
        # Negli elenchi per mese, per giorno, per fascia e per ora solo le voci
        # con un po' d'ascolto: senza nessun mese d'ascolto la riga dei mesi
        # non si scrive, perche' la prima riga gia' dice zero giorni (1.104.0).
        mesi = Counter()
        for g, v in giorni.items():
            mesi[(g.year, g.month)] += v.get("play", 0)
        mesi = sorted((am, s) for am, s in mesi.items() if s)
        if mesi:
            righe.append("Per mese: " + "; ".join(f"{MESI[m - 1]} {a}, {durata(s)}" for (a, m), s in mesi) + ".")
        settimana = self.d["settimana"]
        totale = sum(settimana)
        if totale:
            ordine = sorted((i for i in range(7) if settimana[i]), key=lambda i: -settimana[i])
            righe.append("Per giorno della settimana: " + "; ".join(f"{GIORNI[i]} {percentuale(settimana[i], totale)}" for i in ordine) + ".")
        ore = self.d["ore"]
        totale = sum(ore)
        if totale:
            fasce = [("sera, dalle 18", range(18, 24)), ("pomeriggio, dalle 12", range(12, 18)), ("mattina, dalle 6", range(6, 12)), ("notte, da mezzanotte alle 6", range(0, 6))]
            fasce = [(nome, sum(ore[h] for h in fascia)) for nome, fascia in fasce]
            fasce = sorted((f for f in fasce if f[1]), key=lambda f: -f[1])
            righe.append("Per fascia: " + "; ".join(f"{nome}: {percentuale(secondi, totale)}" for nome, secondi in fasce) + ".")
            ora = max(range(24), key=lambda h: ore[h])
            righe.append(f"L'ora con più ascolto: {dalle(ora)} {alle((ora + 1) % 24)}, {percentuale(ore[ora], totale)}, {durata(ore[ora])}.")
            righe.append("Per ora: " + "; ".join(f"ore {h}: {percentuale(ore[h], totale)}" for h in range(24) if ore[h]) + ".")
        con_marker = [g for g, v in giorni.items() if v.get("marker")]
        if con_marker:
            g = max(con_marker, key=lambda g: giorni[g]["marker"])
            righe.append(f"Il giorno con più marker messi: {data(g)}, {int(giorni[g]['marker'])}.")
        return righe

    # 10.

    def i_record(self):
        r = self.d["record"]
        righe = []
        if "sessione_piu_lunga" in r:
            righe.append(f"La sessione più lunga: {durata(r['sessione_piu_lunga']['valore'])}, cominciata {data_e_ora(r['sessione_piu_lunga']['quando'])}.")
        if "filata" in r:
            righe.append(f"La riproduzione più lunga senza fermarsi: {durata(r['filata']['valore'])}, {al_plurale(int(r['filata'].get('brani', 1)), 'brano', 'brani di fila')}.")
        if "pausa_piu_lunga" in r:
            righe.append(f"La pausa più lunga: {durata(r['pausa_piu_lunga']['valore'])}, {data_e_ora(r['pausa_piu_lunga']['quando'])}.")
        if "finito_piu_lungo" in r:
            righe.append(f"Il brano più lungo ascoltato fino alla fine: {_nome(r['finito_piu_lungo'].get('cosa', ''))}, {durata(r['finito_piu_lungo']['valore'])}.")
        if "finito_piu_breve" in r:
            righe.append(f"Il brano più breve ascoltato fino alla fine: {_nome(r['finito_piu_breve'].get('cosa', ''))}, {durata(r['finito_piu_breve']['valore'])}.")
        if "volume_piu_alto" in r:
            righe.append(f"Il volume più alto: {r['volume_piu_alto']['valore']}, {data_e_ora(r['volume_piu_alto']['quando'])}.")
        alta, bassa = r.get("velocita_piu_alta", {}).get("valore", 1), r.get("velocita_piu_bassa", {}).get("valore", 1)
        if alta != 1 or bassa != 1:
            righe.append(f"La velocità più alta: {numero_decimale(alta)}; la più bassa: {numero_decimale(bassa)}.")
        if "risultati" in r:
            righe.append(f"La ricerca con più risultati: {r['risultati'].get('cosa', '')}, {r['risultati']['valore']}.")
        if "ricerca_piu_lunga" in r:
            righe.append(f"La ricerca più lunga: {durata(r['ricerca_piu_lunga']['valore'])}, {r['ricerca_piu_lunga'].get('cosa', '')}.")
        if "selezione" in r:
            righe.append(f"La selezione più grande della plancia: {al_plurale(int(r['selezione']['valore']), 'voce', 'voci')}.")
        if "tasti_in_una_sessione" in r:
            righe.append(f"Più tasti in una sessione: {r['tasti_in_una_sessione']['valore']}.")
        if "brani_in_una_sessione" in r:
            righe.append(f"Più brani in una sessione: {r['brani_in_una_sessione']['valore']}.")
        return righe

    # 11.

    def muoversi(self):
        return [
            f"Salti in avanti con E: {self.e('avanti')}, per {durata(self.c('secondi_avanti'))} in tutto.",
            f"Salti indietro con Q: {self.e('indietro')}, per {durata(self.c('secondi_indietro'))} in tutto.",
            f"Secondi dei salti cambiati, con Maiuscolo e Q o E: {self.e('passo_di_salto')}.",
            f"Vai a un tempo, con W o con la linea del tempo: {self.e('vai_a_tempo')}.",
            f"Capitoli: avanti con il punto {self.e('capitolo_successivo')}, indietro con la virgola {self.e('capitolo_precedente')}.",
            f"Loop A-B: punti A {self.e('loop_a_messo')}, punti B {self.e('loop_b_messo')}, tolti {self.e('loop_tolto')}; ritorni al punto A {self.e('ritorno_al_punto_a')}.",
            f"Timer di spegnimento: {self.e('timer_impostato')} impostati, di cui a fine brano {self.c('timer_a_fine_brano')}; "
                f"{self.e('timer_scaduto')} scaduti, {self.e('timer_tolto')} tolti.",
        ]

    # 12.

    def i_marker(self):
        righe = [
            f"Marker messi, con T: {self.e('marker_messo')}.",
            f"Marker rinominati: {self.e('marker_rinominato')}.",
            f"Marker eliminati: {self.marker_eliminati()}.",
            f"Uno per uno, con Canc o dal menu: {self.c('marker_tolti_uno')}.",
            f"Prima del punto, con Maiuscolo e R: {self.c('marker_tolti_prima')}, in {al_plurale(self.e('marker_tolti_prima'), 'volta', 'volte')}.",
            f"Dopo il punto, con Maiuscolo e Y: {self.c('marker_tolti_dopo')}, in {al_plurale(self.e('marker_tolti_dopo'), 'volta', 'volte')}.",
            f"Tutti quelli del brano, con Maiuscolo e T: {self.c('marker_tolti_tutti')}, in {al_plurale(self.e('marker_tolti_tutti'), 'volta', 'volte')}.",
            f"Con la selezione multipla della plancia: {self.c('marker_tolti_selezione')}.",
            f"Dalla finestra dei marcatori: {self.c('marker_tolti_finestra')}.",
            f"Salti ai marker: con R e Y {self.e('marker_indietro') + self.e('marker_avanti')}; con Maiuscolo e le cifre {self.c('marker_con_le_cifre')}; "
                f"dalla plancia, con Vai al marker o X {max(0, self.c('vai_al_marker') - self.c('marker_con_le_cifre'))}.",
            f"Finestra dei marcatori aperta: {al_plurale(self.e('marcatori'), 'volta', 'volte')}; esportazioni {self.e('marcatori_esportati')}; "
                f"importazioni {self.e('marcatori_importati')}; cancellazioni di tutto {self.e('marcatori_cancellati')}.",
        ]
        con_marker = sorted(((p, v) for p, v in self.d["brani"].items() if v.get("marker")), key=lambda pv: (-pv[1]["marker"], pv[0]))
        if con_marker:
            p, v = con_marker[0]
            righe.append(f"Il brano con più marker messi: {_nome(p)}, {int(v['marker'])}.")
        return righe

    # 13.

    def le_playlist(self):
        create = self.e("playlist_creata") + self.e("nuova_playlist")
        dalla_ricerca, da_cartella = self.c("playlist_dalla_ricerca"), self.c("playlist_da_una_cartella")
        altre = max(0, self.e("playlist_creata") - dalla_ricerca - da_cartella)
        return [
            f"Playlist create: {create}; da una cartella {da_cartella}, dai risultati della ricerca {dalla_ricerca}, da una selezione o dal menu {altre}, vuote {self.e('nuova_playlist')}.",
            f"Playlist rinominate: {self.e('playlist_rinominata')}; eliminate: {self.e('playlist_eliminata')}; ordinate: {self.e('playlist_ordinata')}; "
            f"invertite: {self.e('ordine_invertito')}; mescolate: {self.e('playlist_mescolata')}; rimesse nell'ordine di prima: {self.e('ordine_ripristinato')}.",
            f"Brani aggiunti alle playlist: {self.c('brani_aggiunti')}, in {al_plurale(self.c('aggiunte'), 'volta', 'volte')}.",
            f"Brani tolti: {self.c('brani_tolti')}; spostati: {self.e('brano_spostato')}; segnati come saltati: {self.e('saltato_acceso')}, e tornati: {self.e('saltato_spento')}.",
            f"Brani messi nei Preferiti: {self.e('preferito_aggiunto')}; c'erano già: {self.e('gia_nei_preferiti')}.",
            f"Filtri messi: {self.e('filtro_messo')}; tolti: {self.e('filtro_tolto')}.",
        ]

    # 14.

    def la_ricerca(self):
        ricerche = self.c("ricerche_nel_ramo") + self.c("ricerche_ovunque")
        risultati = self.c("risultati")
        finite = self.e("ricerca_finita")
        righe = [f"Ricerche: {ricerche}; nel ramo {self.c('ricerche_nel_ramo')}, in tutto MeTeOra {self.c('ricerche_ovunque')}."]
        riga = f"Risultati trovati dalle ricerche finite: {risultati}"
        if finite:
            riga += f", in media {round(risultati / finite)} per ricerca"
        righe.append(riga + ".")
        righe.append(f"Ricerche senza risultati: {self.c('ricerche_senza_risultati')}; fermate prima della fine: {self.e('ricerca_fermata')}.")
        righe.append(f"Altri risultati mostrati: {self.e('altri_risultati')}; risultati salvati come playlist: {self.c('playlist_dalla_ricerca')}.")
        for dove, chiave in (("nella console", "in_console"), ("nella finestra dei marcatori", "nei_marcatori"), ("nelle statistiche", "nelle_statistiche")):
            righe.append(f"Ricerche {dove}, contando anche Invio: trovate {self.e('trovato_' + chiave)}, ripartite dall'inizio {self.e('ripartito_' + chiave)}, "
                f"non trovate {self.e('non_trovato_' + chiave)}.")
        return righe

    # 15.

    def file_e_tag(self):
        return [
            f"File rinominati: {self.e('file_rinominato')}.",
            f"Mandati nel cestino: {al_plurale(self.c('file_nel_cestino'), 'file', 'file')} e {al_plurale(self.c('cartelle_nel_cestino'), 'cartella', 'cartelle')}.",
            f"Tag letti con F11: {self.e('tag_letti')}; dettagli di cartelle, unità e playlist: {self.e('dettagli')}.",
            f"Tag cambiati: {al_plurale(self.e('tag_cambiato'), 'volta', 'volte')}, su {al_plurale(self.c('file_dei_tag_cambiati'), 'file', 'file')}; "
                f"tag cancellati: {self.e('tag_cancellato')}.",
        ]

    # 16.

    def il_video(self):
        video = sum(int(v.get("avvii", 0)) for e, v in self.d["formati"].items() if famiglia(f"x{e}") == "video")
        return [
            f"Video avviati: {video}.",
            f"Immagine accesa e spenta, con Maiuscolo e F1: accesa {self.e('video_acceso')}, spenta {self.e('video_spento')}.",
            f"Schermo intero: {al_plurale(self.e('schermo_intero'), 'volta', 'volte')}, per {durata(self.t('schermo_intero'))}.",
            f"Finestra del video nascosta: {self.e('video_nascosto')}.",
            f"Tracce audio cambiate: {self.e('traccia_audio')}; rapporto dell'immagine cambiato: {self.e('rapporto')}.",
            f"Sottotitoli accesi: {self.e('sottotitoli_accesi')}; spenti: {self.e('sottotitoli_spenti')}.",
            f"Righe di sottotitoli e karaoke lette: {self.c('righe_dei_sottotitoli')}.",
            f"Di queste, lette dalle immagini con il riconoscimento dei caratteri: {self.c('righe_riconosciute')}.",
            f"Di queste, del karaoke: {self.c('righe_del_karaoke')}.",
            f"Passate in anticipo degli impressi: avviate {self.e('passata_avviata')}, finite {self.e('passata_finita')}.",
        ]

    # 17.

    def descrizione_del_tasto(self, nome):
        comando = self.comandi_dei_tasti.get(nome)
        if comando in DESCRIZIONI_DEI_COMANDI:
            return DESCRIZIONI_DEI_COMANDI[comando]
        if nome in DESCRIZIONI_DEI_TASTI:
            return DESCRIZIONI_DEI_TASTI[nome]
        if nome.isdigit():
            return "una delle prime dieci playlist"
        if nome.startswith("Maiuscolo con ") and nome.removeprefix("Maiuscolo con ").isdigit():
            return "uno dei primi dieci marker"
        return ""

    def la_tastiera(self):
        tasti = self.d["tasti"]
        totale = int(sum(tasti.values()))
        ore = self.t("aperto") / 3600
        riga = f"Tasti premuti: {totale}"
        # Senza tasti premuti, il conto per ora non si dice (1.104.0).
        if ore >= 0.1 and totale:
            riga += f", cioè {round(totale / ore)} per ogni ora di MeTeOra aperto"
        righe = [riga + "."]
        frecce = {k: v for k, v in tasti.items() if k.startswith("Freccia ") and v}
        if frecce:
            righe.append(f"Frecce: {int(sum(frecce.values()))}; " + "; ".join(f"{k[0].lower()}{k[1:]} {int(v)}" for k, v in sorted(frecce.items(), key=lambda kv: -kv[1])) + ".")

        def scrivi(nome, quanti):
            descrizione = self.descrizione_del_tasto(nome)
            return f"{nome}{', ' + descrizione if descrizione else ''}: {int(quanti)}."

        # Nella classifica e nei piu' frequenti solo le voci diverse da zero,
        # che un file toccato a mano puo' avere (1.104.0).
        premuti = [(k, v) for k, v in tasti.items() if v]
        righe += self.classifica(f"I {POSTI} tasti più premuti", sorted(premuti, key=lambda kv: (-kv[1], kv[0])), scrivi)
        senza = {k: v for k, v in self.d["senza_comando"].items() if v}
        riga = f"Tasti senza comando: {int(sum(senza.values()))}"
        if senza:
            nome, quanti = max(senza.items(), key=lambda kv: (kv[1], kv[0]))
            riga += f"; il più frequente: {nome}, {al_plurale(int(quanti), 'volta', 'volte')}"
        righe.append(riga + ".")
        righe += [
            f"Rami aperti: {self.e('ramo_aperto')}; chiusi: {self.e('ramo_chiuso')}.",
            f"F8, al brano che suona: {self.e('vai_al_brano')}; inseguimento acceso con Maiuscolo e F8: {self.e('insegui_acceso')}.",
            f"F9 e F10 sul ramo: {self.e('chiudi_tutto')} e {self.e('apri_tutto')}; Maiuscolo con F9 e F10 su tutta la plancia: {self.e('chiudi_la_plancia')} e {self.e('apri_la_plancia')}.",
            f"Backspace, risali: {self.e('risali')}; Maiuscolo con Backspace, all'antenato: {self.e('risali_all_antenato')}.",
            f"Menu aperti: {self.e('menu')}.",
            f"Tasti rapidi spenti con Maiuscolo e F12: {self.e('tasti_spenti')}.",
            f"Clic sulla barra dei comandi: {self.c('clic_sulla_barra')}.",
        ]
        return righe

    # 18.

    def la_console(self):
        righe = [
            f"Righe scritte nella console: {self.c('righe_della_console')}; riscritte al loro posto, come quelle del volume: {self.c('righe_riscritte')}.",
            f"Alla plancia con F5: {self.e('plancia')}; alla console con F6: {self.e('console')}; al cruscotto con F7: {self.e('cruscotto')}.",
            f"Manuale con F1: {self.e('manuale')}; novità con F2: {self.e('changelog')}; crediti con F3: {self.e('crediti')}; guida rapida con F12: {self.e('elenco_dei_tasti')}.",
            f"Console salvata: {self.e('console_salvata')}.",
            f"Statistiche aperte: {self.e('statistiche')}.",
        ]
        totale = int(sum(self.eventi.values()))
        riga = f"Effetti sonori, contati anche con il volume degli effetti a zero: {totale}"
        # Il piu' suonato solo fra gli eventi accaduti (1.104.0).
        accaduti = {k: v for k, v in self.eventi.items() if v}
        if accaduti:
            evento, quanti = max(accaduti.items(), key=lambda kv: (kv[1], kv[0]))
            riga += f"; il più suonato: {NOMI_DEGLI_EVENTI.get(evento, evento.replace('_', ' '))}, {al_plurale(int(quanti), 'volta', 'volte')}"
        righe.append(riga + ".")
        righe.append(f"Domande, con il loro suono: {self.e('domanda')}; annullate: {self.e('annullamento')}.")
        return righe

    # 19.

    def le_impostazioni(self):
        # La piu' usata solo fra le voci aperte almeno una volta (1.104.0).
        voci = {k: v for k, v in self.d["impostazioni"].items() if v}
        riga = f"Voci delle impostazioni aperte con Invio: {int(sum(voci.values()))}"
        if voci:
            chiave, quante = max(voci.items(), key=lambda kv: (kv[1], kv[0]))
            riga += f"; la più usata: {self.nomi_delle_impostazioni.get(chiave, chiave)}, {al_plurale(int(quante), 'volta', 'volte')}"
        return [
            f"Finestra delle impostazioni aperta: {al_plurale(self.e('impostazioni'), 'volta', 'volte')}; impostazioni cambiate: {self.e('impostazione_cambiata')}.",
            riga + ".",
            f"Scheda audio cambiata: {al_plurale(self.e('scheda_audio'), 'volta', 'volte')}.",
            f"Percorsi di rete aggiunti: {self.e('percorso_aggiunto')}; tolti: {self.e('percorso_tolto')}; ricerche dei computer della rete: {self.c('ricerche_della_rete')}.",
            f"Banco dei suoni MIDI scelto: {al_plurale(self.c('banchi_scelti'), 'volta', 'volte')}; scaricamenti avviati: {self.e('scaricamento_avviato')}, finiti: {self.e('scaricamento_finito')}.",
            f"Aggiornamenti proposti: {self.e('aggiornamento')}.",
            f"Dona per questo progetto aperto: {al_plurale(self.e('donazione'), 'volta', 'volte')}.",
        ]

    # 20.

    def la_salute(self):
        errori = sorted(((e, int(v.get("errori", 0))) for e, v in self.d["formati"].items() if v.get("errori")), key=lambda ev: (-ev[1], ev[0]))
        riga = f"Brani non suonati per un errore: {self.c('errori_di_riproduzione')}"
        if errori:
            riga += "; per formato: " + ", ".join(f"{e.lstrip('.')} {n}" for e, n in errori)
        righe = [riga + "."]
        righe += [
            f"Messaggi d'errore nella console: {self.e('errore')}.",
            f"Problemi interni scritti nella console: {self.c('problemi_interni')}.",
            f"Avvii dopo un errore grave, con il resoconto da mandare: {self.c('crash')}.",
            f"Chiusure non regolari: {self.c('chiusure_non_regolari')}.",
            f"Salvataggi non riusciti: {self.c('salvataggi_non_riusciti')}.",
            f"Cartelle di rete che non hanno risposto nella plancia: {self.c('rete_muta')}.",
            self.riga_delle_pulizie(),
            f"Attese dei SID, dei MIDI e delle console oltre un secondo e mezzo, dopo un salto: {self.c('attese_lunghe')}.",
            f"Comandi che lì non valgono: {self.e('non_disponibile')}; niente da suonare: {self.e('niente_da_suonare')}.",
        ]
        return righe

    def riga_delle_pulizie(self):
        """Le pulizie all'avvio, quante in tutto e quante non riuscite, e
        cio' che hanno tolto, solo le voci diverse da zero, con tolto
        accordato a cio' che segue (1.104.0). pulizie conta quelle riuscite,
        pulizie_non_riuscite quelle finite con un errore."""
        riuscite, non_riuscite = self.c("pulizie"), self.c("pulizie_non_riuscite")
        totale = riuscite + non_riuscite
        if not totale:
            return "Pulizie all'avvio: nessuna."
        riga = f"Pulizie all'avvio: {totale}"
        if non_riuscite == totale:
            riga += ", non riuscita per un errore" if totale == 1 else ", tutte non riuscite per un errore"
        elif non_riuscite:
            riga += f", di cui {al_plurale(non_riuscite, 'non riuscita', 'non riuscite')} per un errore"
        tolti = [(self.c(conto), singolare, plurale, femminile) for conto, singolare, plurale, femminile in TOLTI_DALLA_PULIZIA if self.c(conto)]
        if tolti:
            primo, _singolare, _plurale, femminile = tolti[0]
            if len(tolti) > 1:
                # Femminile solo se lo sono tutte le voci.
                participio = "tolte" if all(f for *_resto, f in tolti) else "tolti"
            elif femminile:
                participio = "tolta" if primo == 1 else "tolte"
            else:
                participio = "tolto" if primo == 1 else "tolti"
            riga += f"; {participio} " + ", ".join(al_plurale(n, singolare, plurale) for n, singolare, plurale, _f in tolti)
        elif riuscite:
            riga += "; niente da togliere"
        saltate = self.c("pulizia_radici_saltate")
        if saltate:
            riga += f"; unità saltate perché non rispondevano: {saltate}"
        return riga + "."

    # 21.

    def la_libreria(self):
        return list(self.libreria) if self.libreria else ["La libreria di adesso non si è potuta contare."]

    # 22.

    def curiosita(self):
        righe = []
        dal = (_leggi_data(self.d["dal"]) or self.oggi).date()
        giorni = max(1, (self.oggi.date() - dal).days + 1)
        durata_della_libreria = self.numeri_della_libreria.get("durata")
        if self.play and durata_della_libreria:
            al_giorno = self.play / giorni
            ritmo = "di oggi" if giorni == 1 else f"di questi {giorni} giorni"
            righe.append(f"Al ritmo {ritmo}, per ascoltare tutta la libreria servirebbero {anni_e_mesi(durata_della_libreria / al_giorno)}.")
        if self.play >= 74 * 60:
            righe.append(f"La riproduzione equivale a {round(self.play / (74 * 60))} CD da 74 minuti, o {round(self.play / (90 * 60))} cassette da 90.")
        if self.t("pausa") and self.play:
            righe.append(f"Per ogni ora in pausa, {numero_decimale(self.play / self.t('pausa'))} ore in riproduzione.")
        avviati = self.avviati()
        if avviati >= 10:
            righe.append(f"Ogni 100 brani avviati, {round(100 * self.c('lasciati') / avviati)} lasciati prima della fine, {round(100 * self.c('lasciati_subito') / avviati)} nei primi {int(SUBITO)} secondi.")
        if self.c("secondi_avanti"):
            righe.append(f"Se i salti in avanti con E fossero un brano, durerebbe {durata(self.c('secondi_avanti'))}.")
        sid = sum(v.get("secondi", 0) for e, v in self.d["formati"].items() if e == ".sid")
        sid_della_libreria = self.numeri_della_libreria.get("sid")
        if sid and sid_della_libreria:
            righe.append(f"I SID ascoltati sono {percentuale(sid, sid_della_libreria)} dei {durata(sid_della_libreria)} di SID della libreria.")
        return righe

    # 23.

    def tutti_gli_eventi(self):
        # Un evento a zero, da un file toccato a mano, non e' accaduto (1.104.0).
        eventi = sorted(((evento, quante) for evento, quante in self.eventi.items() if quante), key=lambda kv: (-kv[1], kv[0]))
        righe = [f"Eventi diversi accaduti: {len(eventi)} su {len(NOMI_DEGLI_EVENTI)} che MeTeOra conosce."]
        for evento, quante in eventi:
            nome = NOMI_DEGLI_EVENTI.get(evento, evento.replace("_", " "))
            righe.append(f"{nome[0].upper()}{nome[1:]}: {int(quante)}.")
        return righe


# La libreria di adesso, dallo schedario.

def censisci_la_libreria(schede, anno_di_adesso=None):
    """I conti dello schedario, da fare in disparte: schede e' una copia del
    suo dizionario, percorso -> scheda. Gli anni dei tag oltre anno_di_adesso,
    predefinito quello di oggi, sono sbagliati e non contano (1.104.0)."""
    if anno_di_adesso is None:
        anno_di_adesso = datetime.date.today().year
    c = {"file": 0, "byte": 0, "durata": 0.0, "senza_durata": 0, "non_credibili": 0, "sottobrani_sid": 0, "file_sid": 0,
        "famiglie": {f: {"file": 0, "durata": 0.0, "byte": 0} for f in FAMIGLIE}, "estensioni": Counter(), "unita": Counter(),
        "lungo": None, "corto": None, "autori": Counter(), "album": set(), "generi": set(), "anni": [], "decenni": Counter()}
    for percorso, scheda in schede.items():
        if not isinstance(scheda, dict):
            continue
        c["file"] += 1
        f = c["famiglie"][famiglia(percorso)]
        f["file"] += 1
        dimensione = scheda.get("dim")
        if _numero(dimensione) and dimensione > 0:
            c["byte"] += dimensione
            f["byte"] += dimensione
        c["estensioni"][formati.estensione(percorso) or "senza estensione"] += 1
        c["unita"][unita_di(percorso)] += 1
        d = scheda.get("durata")
        if not _numero(d) or d < 0:
            c["senza_durata"] += 1
        elif d >= DURATA_CREDIBILE:
            c["non_credibili"] += 1
        else:
            c["durata"] += d
            f["durata"] += d
            if c["lungo"] is None or d > c["lungo"][0]:
                c["lungo"] = (d, percorso)
            if d > 0 and (c["corto"] is None or d < c["corto"][0]):
                c["corto"] = (d, percorso)
        if formati.e_sid(percorso):
            c["file_sid"] += 1
            if isinstance(scheda.get("sottobrani"), int):
                c["sottobrani_sid"] += scheda["sottobrani"]
        tag = scheda.get("tag") if isinstance(scheda.get("tag"), dict) else {}
        if tag.get("autore") and tag["autore"] != "<?>":
            c["autori"][str(tag["autore"])] += 1
        if tag.get("album"):
            c["album"].add(str(tag["album"]))
        if tag.get("genere"):
            c["generi"].add(str(tag["genere"]))
        anno = tag.get("anno")
        if isinstance(anno, int) and not isinstance(anno, bool) and 0 < anno <= anno_di_adesso:
            c["anni"].append(anno)
            c["decenni"][_decennio(anno)] += 1
    return c


def numeri_della_libreria(c):
    """I numeri della libreria che servono fuori dalla sua sezione: quanti
    file, quanto durano tutti e quanto i SID."""
    return {"file": c["file"], "durata": c["durata"], "sid": c["famiglie"]["sid"]["durata"]}


def righe_della_libreria(c, dimensione):
    """Le righe dello schedario nella sezione della libreria di adesso;
    dimensione(byte) scrive una dimensione, come i dettagli di F11."""
    righe = []
    totale = c["file"]
    if not totale:
        righe.append("Schedario: ancora vuoto.")
        return righe
    righe.append(f"Schedario: {al_plurale(totale, 'file conosciuto', 'file conosciuti')}, {dimensione(c['byte'])}.")
    righe.append(f"Durata di tutta la libreria: {durata(c['durata'])}.")
    ordine = list(FAMIGLIE)
    # Solo le famiglie che hanno dei file: con lo schedario non vuoto, almeno
    # una c'e' (1.104.0).
    famiglie = sorted((kv for kv in c["famiglie"].items() if kv[1]["file"]), key=lambda kv: (-kv[1]["file"], ordine.index(kv[0])))
    righe.append("Per numero di file: " + "; ".join(f"{NOMI_BREVI_DELLE_FAMIGLIE[k]} {v['file']}, {percentuale(v['file'], totale)}" for k, v in famiglie) + ".")
    con_durata = sorted((kv for kv in c["famiglie"].items() if kv[1]["durata"]), key=lambda kv: -kv[1]["durata"])
    if con_durata:
        righe.append("Per durata: " + "; ".join(f"{NOMI_BREVI_DELLE_FAMIGLIE[k]} {durata(v['durata'])}, {percentuale(v['durata'], c['durata'])}" for k, v in con_durata) + ".")
    con_spazio = sorted((kv for kv in c["famiglie"].items() if kv[1]["byte"]), key=lambda kv: -kv[1]["byte"])
    if con_spazio:
        righe.append("Per spazio: " + "; ".join(f"{NOMI_BREVI_DELLE_FAMIGLIE[k]} {dimensione(v['byte'])}" for k, v in con_spazio) + ".")
    if c["file_sid"]:
        righe.append(f"Sottobrani dei SID: {c['sottobrani_sid']}, in {al_plurale(c['file_sid'], 'file', 'file')}.")
    presenti = [e for e in c["estensioni"] if e in formati.TUTTI]
    piu = ", ".join(f"{e.lstrip('.')} {n}" for e, n in c["estensioni"].most_common(5))
    righe.append(f"Formati presenti: {len(presenti)} dei {len(formati.TUTTI)}; i più numerosi: {piu}.")
    righe.append("Per unità: " + "; ".join(f"{k} {al_plurale(n, 'file', 'file')}, {percentuale(n, totale)}" for k, n in c["unita"].most_common()) + ".")
    if c["lungo"]:
        righe.append(f"Il file più lungo: {_nome(c['lungo'][1])}, {durata(c['lungo'][0])}.")
    if c["corto"]:
        righe.append(f"Il file più corto: {_nome(c['corto'][1])}, {durata(c['corto'][0])}.")
    # Dai tag, solo cio' che c'e'; senza niente, una frase che lo dice (1.104.0).
    parti = []
    if c["autori"]:
        parti.append(al_plurale(len(c["autori"]), "autore", "autori"))
    if c["album"]:
        parti.append(f"{len(c['album'])} album")
    if c["generi"]:
        parti.append(al_plurale(len(c["generi"]), "genere", "generi"))
    testo = ", ".join(parti)
    if c["anni"]:
        anni = f"anni dal {min(c['anni'])} al {max(c['anni'])}"
        testo = f"{testo}; {anni}" if testo else anni
    righe.append(f"Dai tag: {testo or 'nessun autore, album, genere o anno'}.")
    if c["autori"]:
        autore, quanti = max(c["autori"].items(), key=lambda kv: (kv[1], kv[0]))
        righe.append(f"L'autore con più file: {autore}, {quanti}.")
    if c["decenni"]:
        decennio, quanti = max(c["decenni"].items(), key=lambda kv: (kv[1], kv[0]))
        righe.append(f"Il decennio con più file: gli {decennio}, {quanti}.")
    righe.append(f"File di cui la durata non si sa: {c['senza_durata']}.")
    if c["non_credibili"]:
        righe.append(f"Durate non credibili, oltre una settimana, lasciate fuori dai conti: {al_plurale(c['non_credibili'], 'file', 'file')}.")
    return righe
