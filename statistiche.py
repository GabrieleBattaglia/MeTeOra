# MeTeOra, le statistiche: ogni sorta di conti, raccolti mentre lo si usa, e la pagina che li racconta.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (UltraCode).
# 17/10/2026: nasce con la 1.103.0, chiesta da Gabriele: piu' dati ci sono, piu' e' contento. Nella 1.104.0 le righe che elencano voci tengono solo quelle diverse da zero, le percentuali uniformi, gli anni futuri dei tag ignorati, le date sempre con il giorno della settimana, e i brani dello storico tolti dalla pulizia all'avvio o rinominati, con i conti della pulizia nella salute. Nella 1.105.0 i nomi di Dove sono, il comando dell'apostrofo, e del suo suono. Nella 1.109.0 le playlist ordinate, invertite, mescolate e rimesse nell'ordine di prima. Nella 1.110.0 quelli della durata residua, Maiuscolo con l'apostrofo. Nella 1.112.0, nella salute, anche le unita' saltate dalla pulizia perche' usate da dischi diversi o perche' il disco che rispondeva non si riconosceva, i dischi riconosciuti a mano e le lettere rese contese dalla Sentinella. Nella 1.113.0 le playlist importate da un M3U o da un PLS, riaperte e rilette. Nella 1.113.5 il campo modificate, perche' la finestra scriva il file solo quando qualcosa e' cambiato davvero. Nella 1.116.0 i nomi delle schede audio che se ne vanno e tornano. Nella 1.119.0 le uscite: la scelta che va e torna, i brani ripresi, gli speaker Cast e l'assenza piu' lunga (issue 31). Nella 3.0.0 i testi passano da lingua.py, per le traduzioni. Nella 3.2.0 i brani dei siti fra i formati, e la riga degli indirizzi in rete. Nella 3.3.0 le radio fra i formati, la riga delle radio, e i componenti aggiuntivi e la lingua. Nella 3.5.0 la riga delle registrazioni, e i nomi dei loro eventi. Nella 3.7.0 le righe lette da sole e i nomi della famiglia di F10. Nella 3.8.0 i capitoli detti suonando. Nella 3.9.0 la riga della ricerca dei contenuti. Nella 3.9.2 la sezione Le registrazioni, con media, dirette e puntate, formati e primati. Nella 3.10.0 gli altri risultati e le altre radio chiesti. Nella 3.11.6 i punti rotti tolti alle radio ripetute a uno speaker.

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
import indirizzi
import valori
from lingua import _, ngettext, plurale

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

MESI = (_("gennaio"), _("febbraio"), _("marzo"), _("aprile"), _("maggio"), _("giugno"), _("luglio"), _("agosto"), _("settembre"), _("ottobre"),
    _("novembre"), _("dicembre"))
GIORNI = (_("lunedì"), _("martedì"), _("mercoledì"), _("giovedì"), _("venerdì"), _("sabato"), _("domenica"))

# Le famiglie dei formati, nell'ordine in cui si dicono a parita' di tempo.
# MIDI e SID sono nomi, e non si traducono.
FAMIGLIE = {
    "audio": _("Audio, MP3, FLAC e gli altri"),
    "sid": _("SID del Commodore 64"),
    "video": _("Video"),
    "midi": "MIDI",
    "tracker": _("Moduli dei tracker"),
    "console": _("Musica delle console"),
}
# Traduttori: le famiglie dei formati con un nome breve, nelle righe della libreria come «audio 2, 50.0%».
NOMI_BREVI_DELLE_FAMIGLIE = {"audio": _("audio"), "sid": "SID", "video": _("video"), "midi": "MIDI", "tracker": _("tracker"), "console": _("console")}


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
    # Traduttori: da qui, che cosa fa un tasto, nella classifica dei tasti premuti: «X, suona: 3.».
    "precedente": _("brano precedente"), "play": _("suona"), "playlist_precedente": _("playlist precedente"), "playlist_successiva": _("playlist successiva"),
    "loop": _("loop A-B"), "pausa": _("pausa"), "stop": _("stop"), "ripetizione": _("ripetizione"), "timer": _("timer di spegnimento"),
    "successivo": _("brano successivo"), "casuale": _("brano a caso"), "riproduzione_casuale": _("riproduzione casuale"), "muto": _("muto"),
    "indietro": _("indietro nel brano"), "avanti": _("avanti nel brano"), "passo_indietro": _("secondi del salto indietro"),
    "passo_avanti": _("secondi del salto avanti"), "vai_a_tempo": _("vai a un tempo"), "capitolo_precedente": _("capitolo precedente"),
    "capitolo_successivo": _("capitolo successivo"), "volume_su": _("volume su"), "volume_giu": _("volume giù"), "ricerca": _("ricerca"),
    "filtro": _("filtro"), "passo_volume": _("passo del volume"), "marker": _("marker"), "marker_precedente": _("marker precedente"),
    "marker_successivo": _("marker successivo"), "togli_i_marker": _("toglie i marker"), "togli_i_marker_prima": _("toglie i marker prima"),
    "togli_i_marker_dopo": _("toglie i marker dopo"), "velocita_giu": _("più lento"), "velocita_normale": _("velocità normale"),
    "velocita_su": _("più veloce"), "tono_giu": _("tono giù"), "tono_normale": _("tono normale"), "tono_su": _("tono su"),
    "banda_precedente": _("banda precedente"), "banda_successiva": _("banda successiva"), "banda_giu": _("banda giù"), "banda_su": _("banda su"),
    "azzera_la_banda": _("azzera la banda"), "azzera_le_bande": _("azzera le bande"), "dissolvenza": _("dissolvenza"),
    "durata_della_dissolvenza": _("durata della dissolvenza"), "dove_sono": _("dove sono"), "durata_residua": _("durata residua"),
    # I comandi della nuova mappa, issue 38 (2.0.0).
    "segnalibro": _("il segnalibro"), "vai_al_segnalibro": _("al segnalibro"), "togli_il_segnalibro": _("toglie il segnalibro"),
    "metti_il_segnalibro": _("mette il segnalibro"),
    # Il piu' e Ctrl e Maiuscolo con X (2.6.0).
    "impostazioni": _("le impostazioni"), "scheda_audio": _("la scheda audio"),
    "posizione": _("il punto del brano"), "verso_la_fine": _("gli ultimi secondi"), "all_inizio": _("l'inizio del brano"),
    "passi_dei_salti": _("i passi dei salti"), "passi_predefiniti": _("salti predefiniti"), "marker_attuale": _("il marker"),
    "ultimo_marker": _("ultimo marker"), "primo_marker": _("primo marker"), "conta_i_marker": _("quanti marker"), "velocita": _("la velocità"),
    "velocita_massima": _("velocità massima"), "velocita_minima": _("velocità minima"), "timer_attuale": _("il timer"), "togli_il_timer": _("toglie il timer"),
    "timer_a_fine_brano": _("timer a fine brano"), "sottotitoli": _("i sottotitoli"), "sottotitoli_precedenti": _("sottotitoli precedenti"),
    "sottotitoli_successivi": _("sottotitoli successivi"), "ultimi_sottotitoli": _("ultimi sottotitoli"), "sottotitoli_spenti": _("sottotitoli spenti"),
    "tono": _("il tono"), "tono_massimo": _("tono massimo"), "tono_minimo": _("tono minimo"), "traccia_audio": _("la traccia audio"),
    "traccia_audio_precedente": _("traccia audio precedente"), "traccia_audio_successiva": _("traccia audio successiva"),
    "ultima_traccia_audio": _("ultima traccia audio"), "prima_traccia_audio": _("prima traccia audio"), "rapporto": _("il rapporto dell'immagine"),
    "rapporto_precedente": _("rapporto precedente"), "rapporto_successivo": _("rapporto successivo"), "rapporto_del_video": _("rapporto del video"),
    "ultimo_rapporto": _("ultimo rapporto"), "primo_rapporto": _("primo rapporto"), "banda": _("la banda"), "ultima_banda": _("ultima banda"),
    "prima_banda": _("prima banda"), "guadagno": _("il guadagno"), "guadagno_massimo": _("guadagno massimo"), "guadagno_minimo": _("guadagno minimo"),
    "curva": _("tutte le bande"), "playlist": _("la playlist"), "ultima_playlist": _("ultima playlist"), "prima_playlist": _("prima playlist"),
    "dissolvenza_piu_breve": _("dissolvenza più breve"), "dissolvenza_piu_lunga": _("dissolvenza più lunga"), "durata_predefinita": _("dissolvenza predefinita"),
    "dissolvenza_massima": _("dissolvenza massima"), "dissolvenza_minima": _("dissolvenza minima"), "spegni_la_dissolvenza": _("spegne la dissolvenza"),
    "accendi_la_dissolvenza": _("accende la dissolvenza"), "spegni_la_casuale": _("spegne la casuale"), "accendi_la_casuale": _("accende la casuale"),
    "volume": _("il volume"), "volume_di_prima": _("volume di prima"), "volume_massimo": _("volume massimo"), "volume_minimo": _("volume a zero"),
    "capitolo": _("il capitolo"), "ultimo_capitolo": _("ultimo capitolo"), "primo_capitolo": _("primo capitolo"), "passo_volume_giu": _("passo del volume giù"),
    "passo_volume_su": _("passo del volume su"), "passo_volume_predefinito": _("passo del volume predefinito"), "passo_volume_massimo": _("passo del volume massimo"),
    "passo_volume_minimo": _("passo del volume minimo"),
}
# Le descrizioni degli altri tasti, per nome.
DESCRIZIONI_DEI_TASTI = {
    # Traduttori: da qui, che cosa fa un tasto, nella classifica dei tasti premuti: «F1, il manuale: 3.».
    "F1": _("il manuale"), "F2": _("le novità"), "F3": _("i crediti"), "F4": _("nei Preferiti"), "F5": _("alla plancia"), "F6": _("alla console"),
    "F7": _("al cruscotto"), "F8": _("al brano che suona"), "F9": _("lo stato del ramo"), "F10": _("la lettura della console, fino alla 3.6 nessun comando"), "F11": _("tag e dettagli"),
    "F12": _("la guida rapida"), "Esc": _("esce"), "Maiuscolo con F1": _("il video"), "Maiuscolo con F2": _("i sottotitoli"),
    "Maiuscolo con F3": _("la traccia audio"), "Maiuscolo con F5": _("lo schermo intero"), "Maiuscolo con F6": _("il rapporto dell'immagine"),
    "Maiuscolo con F7": _("le statistiche"), "Maiuscolo con F8": _("l'inseguimento"),
    "Ctrl con F1": _("spegne il video"), "Ctrl con F5": _("il video in finestra"), "Ctrl con F8": _("sgancia l'inseguimento"), "Ctrl con F12": _("spegne i tasti rapidi"), "Maiuscolo con F9": _("apre il ramo"),
    "Ctrl con F9": _("chiude il ramo"), "Alt con F9": _("apre tutta la plancia"), "Ctrl e Alt con F9": _("chiude tutta la plancia"),
    "Ctrl e Maiuscolo con F9": _("ferma l'apertura"), "Maiuscolo con F10": _("la lettura della console sale, fino alla 3.6 il menu della voce"),
    "Ctrl con F10": _("la lettura della console scende"), "Ctrl e Maiuscolo con F10": _("la console letta al braille e alla sintesi"),
    "Ctrl e Alt con F10": _("la lettura della console spenta"), "Maiuscolo con F11": _("il menu dei tag"), "Maiuscolo con F12": _("i tasti rapidi"),
    "Ctrl con barra rovesciata": _("la ricerca in tutto MeTeOra"), "Backspace": _("risale"), "Maiuscolo con Backspace": _("risale all'antenato"),
    "Barra spaziatrice": _("il menu"), "Invio": _("il menu, o il comando"), "Applicazioni": _("il menu"), "Canc": _("toglie"),
    "Maiuscolo con Canc": _("nel cestino"), "Ctrl con Barra spaziatrice": _("seleziona"),
}

# I nomi degli eventi, per la sezione di tutti gli eventi e per il suono piu'
# suonato. Un evento senza nome, per esempio uno nuovo, si dice com'e'.
NOMI_DEGLI_EVENTI = {
    # Traduttori: da qui, i nomi degli eventi, cioè delle azioni che hanno un suono, nella sezione di tutti gli eventi: «Avvio di MeTeOra: 3.».
    "avvio": _("avvio di MeTeOra"), "uscita": _("uscita da MeTeOra"), "donazione": _("invito a offrire un caffè"),
    "pub_entra": _("Entra al PUB"), "pub_aiuto": _("Chiedi aiuto al PUB"),
    "segnalibro_messo": _("segnalibro messo"), "segnalibro_tolto": _("segnalibro tolto"), "al_segnalibro": _("brano ripreso dal segnalibro"),
    "dettagli": _("dettagli di un contenitore, con F11"), "chiudi_la_plancia": _("tutta la plancia chiusa"),
    "apri_la_plancia": _("apertura di tutta la plancia"), "plancia_aperta": _("tutta la plancia aperta"),
    "passata_avviata": _("passata degli impressi avviata"), "passata_finita": _("passata degli impressi finita"),
    "plancia": _("alla plancia, con F5"), "console": _("alla console, con F6"), "cruscotto": _("al cruscotto, con F7"),
    "manuale": _("manuale, con F1"), "changelog": _("novità, con F2"), "crediti": _("crediti, con F3"),
    "play": _("riproduzione avviata"), "pausa": _("pausa"), "ripresa": _("ripresa dalla pausa"), "stop": _("stop"), "da_capo": _("da capo"),
    "successivo": _("brano successivo"), "precedente": _("brano precedente"), "casuale": _("brano a caso"),
    "casuale_acceso": _("riproduzione casuale accesa"), "casuale_spento": _("riproduzione casuale spenta"),
    "video_acceso": _("video acceso"), "video_spento": _("video spento"), "sottotitoli_accesi": _("sottotitoli accesi"),
    "sottotitoli_spenti": _("sottotitoli spenti"), "traccia_audio": _("traccia audio cambiata"), "schermo_intero": _("schermo intero"),
    "schermo_in_finestra": _("video in finestra"), "rapporto": _("rapporto dell'immagine cambiato"), "video_nascosto": _("video nascosto"),
    "percorso_aggiunto": _("percorso di rete aggiunto"), "percorso_tolto": _("percorso di rete tolto"),
    "registrazione_avviata": _("registrazione avviata"), "registrazione_in_pausa": _("registrazione in pausa"),
    "registrazione_ripresa": _("registrazione ripresa"), "registrazione_fermata": _("registrazione fermata"),
    "registrazione_in_ascolto": _("in ascolto per registrare, con Alt e R"), "registrazione_eliminata": _("registrazione eliminata"),
    "alle_registrazioni": _("al ramo Registrazioni"), "cartella_delle_registrazioni": _("cartella delle registrazioni aperta"),
    "scheda_degli_effetti": _("scheda degli effetti cambiata"), "console_letta": _("lettura della console cambiata, con F10"),
    "console_letta_al_limite": _("lettura della console già al limite"),
    "sorgente_tenuta": _("indirizzo o radio tenuti dopo un minuto di ascolto"),
    "scaricamento_avviato": _("scaricamento avviato"), "scaricamento_finito": _("scaricamento finito"),
    "brano_seguente_da_solo": _("brano seguente partito da solo"), "fine_playlist": _("fine della lista"),
    "avanti": _("salto avanti"), "indietro": _("salto indietro"), "vai_a_tempo": _("vai a un tempo"),
    "passo_di_salto": _("passo di salto cambiato"), "passo_del_volume": _("passo del volume cambiato"),
    "volume_su": _("volume su"), "volume_giu": _("volume giù"), "volume_al_limite": _("volume già al limite"),
    "muto_acceso": _("muto acceso"), "muto_spento": _("muto spento"), "menu": _("menu aperto"),
    "nuova_playlist": _("nuova playlist vuota"), "playlist_creata": _("playlist creata"),
    # Nella 1.113.0, accanto alla playlist creata come in suoni.EVENTI.
    "playlist_gia_importata": _("playlist importata arrivata di nuovo"), "playlist_riletta": _("playlist riletta dal suo file"),
    "playlist_eliminata": _("playlist eliminata"),
    "playlist_rinominata": _("playlist rinominata"), "file_rinominato": _("file rinominato"), "tag_letti": _("tag letti"),
    "tag_cambiato": _("tag cambiati"), "tag_cancellato": _("tag cancellati"), "brano_aggiunto": _("brani aggiunti a una playlist"),
    "preferito_aggiunto": _("brano messo nei Preferiti"), "filtro_messo": _("filtro messo"), "ricerca_avviata": _("ricerca avviata"),
    "ricerca_finita": _("ricerca finita"), "ricerca_fermata": _("ricerca fermata"), "altri_risultati": _("altri risultati mostrati"),
    "filtro_tolto": _("filtro tolto"), "gia_nei_preferiti": _("brano già nei Preferiti"), "brano_tolto": _("brani tolti da una playlist"),
    "cestino": _("nel cestino"), "brano_spostato": _("brano spostato"), "playlist_ordinata": _("playlist ordinata"),
    "ordine_invertito": _("ordine di una playlist invertito"), "playlist_mescolata": _("playlist mescolata"),
    "ordine_ripristinato": _("playlist rimessa nell'ordine di prima"), "saltato_acceso": _("brano segnato come saltato"),
    "saltato_spento": _("brano non più saltato"), "ramo_aperto": _("ramo aperto"), "ramo_chiuso": _("ramo chiuso"),
    "file_aperto": _("file aperto"), "vai_al_brano": _("al brano che suona, con F8"), "playlist_precedente": _("playlist precedente"),
    "playlist_successiva": _("playlist successiva"), "playlist_numero": _("playlist con una cifra"),
    "ripresa_all_avvio": _("ripresa all'avvio"), "insegui_acceso": _("inseguimento acceso"), "insegui_spento": _("inseguimento spento"),
    "elenco_dei_tasti": _("guida rapida, con F12"), "trovato_in_console": _("trovato nella console"),
    "ripartito_in_console": _("ricerca nella console ripartita dall'inizio"), "non_trovato_in_console": _("non trovato nella console"),
    "chiudi_tutto": _("ramo chiuso con Ctrl e F9"), "marker_messo": _("marker messo"), "marker_rinominato": _("marker rinominato"),
    "marker_indietro": _("al marker precedente"), "marker_avanti": _("al marker successivo"),
    "marker_tolti_prima": _("marker tolti prima del punto"), "marker_tolti_dopo": _("marker tolti dopo il punto"),
    "marker_tolti_tutti": _("tutti i marker del brano tolti"), "marker_eliminato": _("marker eliminati"),
    "risali": _("risalita con Backspace"), "risali_all_antenato": _("risalita all'antenato"), "apri_tutto": _("ramo aperto con Maiuscolo e F9"),
    "impostazioni": _("impostazioni aperte"), "impostazione_cambiata": _("impostazione cambiata"), "console_salvata": _("console salvata"),
    "scheda_audio": _("scheda audio cambiata"), "scheda_sparita": _("scheda audio scelta sparita"), "scheda_tornata": _("scheda audio scelta tornata"),
    "scheda_di_windows": _("scheda audio di Windows cambiata"), "marcatori": _("finestra dei marcatori aperta"),
    "marcatori_esportati": _("marcatori esportati"), "marcatori_importati": _("marcatori importati"),
    "marcatori_cancellati": _("tutti i marcatori cancellati"), "trovato_nei_marcatori": _("trovato nei marcatori"),
    "ripartito_nei_marcatori": _("ricerca nei marcatori ripartita dall'inizio"), "non_trovato_nei_marcatori": _("non trovato nei marcatori"),
    "domanda": _("domanda"), "aggiornamento": _("aggiornamento proposto"), "tasti_spenti": _("tasti rapidi spenti"),
    "tasti_accesi": _("tasti rapidi accesi"), "capitolo_precedente": _("capitolo precedente"), "capitolo_successivo": _("capitolo successivo"),
    "ripetizione_spenta": _("ripetizione spenta"), "ripetizione_brano": _("ripetizione del brano"), "ripetizione_lista": _("ripetizione della lista"),
    "timer_impostato": _("timer impostato"), "timer_tolto": _("timer tolto"), "timer_scaduto": _("timer scaduto"),
    "annullamento": _("annullamento"), "ramo_aggiornato": _("ramo aggiornato"), "non_disponibile": _("comando che lì non vale"),
    "errore": _("errore"), "problema": _("problema interno"), "niente_da_suonare": _("niente da suonare"),
    "loop_a_messo": _("punto A del loop"), "loop_b_messo": _("punto B del loop"), "loop_tolto": _("loop tolto"),
    "loop_non_qui": _("loop che lì non si mette"), "fuori_dal_loop": _("brano fuori dal loop"), "ritorno_al_punto_a": _("ritorno al punto A"),
    "nessun_altro_brano": _("niente oltre"), "velocita_su": _("più veloce"), "velocita_giu": _("più lento"),
    "velocita_normale": _("velocità normale"), "velocita_al_limite": _("velocità al limite"), "tono_su": _("tono su"), "tono_giu": _("tono giù"),
    "tono_normale": _("tono normale"), "tono_al_limite": _("tono al limite"), "banda_al_limite": _("banda al limite"),
    "guadagno_al_limite": _("guadagno al limite"), "banda_azzerata": _("banda azzerata"), "bande_azzerate": _("equalizzatore azzerato"),
    "dissolvenza_accesa": _("dissolvenza accesa"), "dissolvenza_spenta": _("dissolvenza spenta"),
    "dissolvenza_durata": _("durata della dissolvenza cambiata"), "statistiche": _("statistiche aperte"),
    "statistiche_azzerate": _("statistiche azzerate"), "trovato_nelle_statistiche": _("trovato nelle statistiche"),
    "ripartito_nelle_statistiche": _("ricerca nelle statistiche ripartita dall'inizio"),
    "non_trovato_nelle_statistiche": _("non trovato nelle statistiche"),
    # Nella 1.104.0, nell'ordine di suoni.EVENTI.
    "pulizia_avviata": _("pulizia all'avvio cominciata"), "pulizia_finita": _("pulizia all'avvio finita"),
    # Nella 1.105.0.
    "dove_sono": _("dove sono, con l'apostrofo"),
    # Nella 1.110.0.
    "durata_residua": _("durata residua, con Maiuscolo e l'apostrofo"),
    # Nella 1.112.0, nell'ordine di suoni.EVENTI.
    "disco_riconosciuto": _("disco riconosciuto a mano"), "disco_diverso": _("lettera resa contesa dalla Sentinella"),
}

# Che cosa ha tolto la pulizia all'avvio: il conto; la frase della voce da
# sola, con tolto accordato; la voce in un elenco; e se e' femminile, per
# l'accordo di tolti quando le voci sono piu' d'una (1.104.0; dalla 3.0.0
# frasi intere, da tradurre). pulizia_schede sono i file spariti;
# pulizia_doppioni le schede doppie, che differiscono solo per le
# maiuscole, tolte quando c'e' quella scritta come sul disco.
TOLTI_DALLA_PULIZIA = (
    ("pulizia_schede", lambda n: ngettext("; tolto {n} file dallo schedario", "; tolti {n} file dallo schedario", n).format(n=n),
        lambda n: plurale(n, "{n} file dallo schedario", "{n} file dallo schedario"), False),
    ("pulizia_doppioni", lambda n: ngettext("; tolta {n} scheda doppia dello schedario", "; tolte {n} schede doppie dello schedario", n).format(n=n),
        lambda n: plurale(n, "{n} scheda doppia dello schedario", "{n} schede doppie dello schedario"), True),
    ("pulizia_brani", lambda n: ngettext("; tolto {n} brano da playlist e Preferiti", "; tolti {n} brani da playlist e Preferiti", n).format(n=n),
        lambda n: plurale(n, "{n} brano da playlist e Preferiti", "{n} brani da playlist e Preferiti"), False),
    ("pulizia_marker", lambda n: ngettext("; tolta {n} voce dei marker", "; tolte {n} voci dei marker", n).format(n=n),
        lambda n: plurale(n, "{n} voce dei marker", "{n} voci dei marker"), True),
    ("pulizia_punti", lambda n: ngettext("; tolto {n} punto da riprendere", "; tolti {n} punti da riprendere", n).format(n=n),
        lambda n: plurale(n, "{n} punto da riprendere", "{n} punti da riprendere"), False),
    ("pulizia_storico", lambda n: ngettext("; tolto {n} brano dallo storico", "; tolti {n} brani dallo storico", n).format(n=n),
        lambda n: plurale(n, "{n} brano dallo storico", "{n} brani dallo storico"), False),
)
# La chiave dei formati senza estensione, nel file e nei conti dello
# schedario: si traduce solo quando si dice, con estensione_da_dire() (3.0.0).
SENZA_ESTENSIONE = "senza estensione"
# I brani dei siti, aperti dagli indirizzi in rete, hanno una voce loro fra i
# formati (3.2.0): il formato vero lo sa solo il sito.
DAI_SITI = "dai siti"
# E dalla 3.3.0 le radio, che sono dirette.
DALLE_RADIO = "dalle radio"


# Le parole.

def _peso(byte):
    """Un peso da dire, come 11.5 MB (3.5.0)."""
    import midi

    return midi.dimensione_da_leggere(byte)


def _volte(n):
    return plurale(n, "{n} volta", "{n} volte")


def estensione_da_dire(estensione):
    """Un'estensione come si dice: senza il punto, e quella dei file senza
    estensione nella lingua di MeTeOra."""
    if estensione == DAI_SITI:
        return _("dai siti")
    if estensione == DALLE_RADIO:
        return _("dalle radio")
    return _("senza estensione") if estensione == SENZA_ESTENSIONE else estensione.lstrip(".")


def elenco(parti):
    """a; a e b; a, b e c."""
    parti = [p for p in parti if p]
    if len(parti) <= 1:
        return "".join(parti)
    if len(parti) == 2:
        # Traduttori: un elenco di due voci, come «1 minuto e 5 secondi».
        return _("{prima} e {seconda}").format(prima=parti[0], seconda=parti[1])
    # Traduttori: un elenco di tre voci o più: prime sono tutte le voci meno l'ultima, separate da virgole, come in «2 giorni, 19 ore e 40 minuti».
    return _("{prime} e {ultima}").format(prime=", ".join(parti[:-1]), ultima=parti[-1])


def durata(secondi):
    """Una durata a parole: sotto l'ora minuti e secondi, come 3 minuti e 41
    secondi; dall'ora in su giorni, ore e minuti, come 2 giorni, 19 ore e 40
    minuti."""
    secondi = max(0.0, float(secondi or 0))
    if secondi == 0:
        return plurale(0, "{n} secondo", "{n} secondi")
    if secondi < 1:
        return _("meno di un secondo")
    if round(secondi) < 3600:
        minuti, resto = divmod(round(secondi), 60)
        return elenco([plurale(minuti, "{n} minuto", "{n} minuti") if minuti else "", plurale(resto, "{n} secondo", "{n} secondi") if resto else ""])
    giorni, resto = divmod(round(secondi / 60), 1440)
    ore, minuti = divmod(resto, 60)
    return elenco([plurale(giorni, "{n} giorno", "{n} giorni") if giorni else "", plurale(ore, "{n} ora", "{n} ore") if ore else "",
        plurale(minuti, "{n} minuto", "{n} minuti") if minuti else ""])


def anni_e_mesi(giorni):
    """Tanti giorni come anni e mesi: 9 anni e 7 mesi; sotto l'anno i mesi,
    sotto il mese i giorni."""
    mesi_in_tutto = round(giorni / 30.4375)
    if mesi_in_tutto < 1:
        return plurale(max(1, round(giorni)), "{n} giorno", "{n} giorni")
    anni, mesi = divmod(mesi_in_tutto, 12)
    return elenco([plurale(anni, "{n} anno", "{n} anni") if anni else "", plurale(mesi, "{n} mese", "{n} mesi") if mesi else ""])


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
        # Traduttori: una percentuale piccolissima; percentuale è 0.01%, scritta sempre con il punto.
        return _("meno di {percentuale}").format(percentuale="0.01%")
    return f"{valore:.2f}%" if 0 < arrotondato < 0.1 else f"{valore:.1f}%"


def numero_decimale(valore):
    """1.75, 0.8, 1: il punto, e senza zeri in fondo."""
    return f"{valore:.2f}".rstrip("0").rstrip(".")


def _ora(quando):
    return f"{quando.hour}:{quando.minute:02d}"


def _alle(quando):
    """alle 10:12, all'1:16."""
    if quando.hour == 1:
        # Traduttori: il momento di un giorno, quando l'ora è l'una: all'1:16.
        return _("all'{orario}").format(orario=_ora(quando))
    # Traduttori: il momento di un giorno, con ore e minuti: alle 10:12.
    return _("alle {orario}").format(orario=_ora(quando))


def _con(preposizione, testo):
    """La preposizione davanti, se c'e': da, a o di, che qui sono codici. Le
    date cominciano con il giorno della settimana, e non si elide mai
    (1.104.0); dalla 3.0.0 preposizione e data sono una frase da tradurre."""
    if preposizione == "da":
        # Traduttori: l'inizio di un periodo; data è come «lunedì 19 ottobre 2026», a volte con l'ora, o «una data che non si legge».
        return _("da {data}").format(data=testo)
    if preposizione == "a":
        # Traduttori: la fine di un periodo che comincia con «da»: «da domenica 1 novembre 2026 a martedì 3 novembre 2026».
        return _("a {data}").format(data=testo)
    if preposizione == "di":
        # Traduttori: il momento di un salvataggio: «dopo il salvataggio di lunedì 19 ottobre 2026 alle 18:03».
        return _("di {data}").format(data=testo)
    return f"{preposizione} {testo}" if preposizione else testo


def dalle(ora):
    """L'inizio di un'ora: da mezzanotte, dall'una, dalle 13."""
    if ora == 0:
        # Traduttori: l'inizio di un'ora del giorno: «da mezzanotte all'una».
        return _("da mezzanotte")
    if ora == 1:
        # Traduttori: l'inizio di un'ora del giorno, quando è l'una: «dall'una alle 2».
        return _("dall'una")
    # Traduttori: l'inizio di un'ora del giorno, senza i minuti: «dalle 13 alle 14».
    return _("dalle {ora}").format(ora=ora)


def alle(ora):
    if ora == 0:
        # Traduttori: la fine di un'ora del giorno: «dalle 23 a mezzanotte».
        return _("a mezzanotte")
    if ora == 1:
        # Traduttori: la fine di un'ora del giorno, quando è l'una: «da mezzanotte all'una».
        return _("all'una")
    # Traduttori: la fine di un'ora del giorno, senza i minuti: «dalle 13 alle 14».
    return _("alle {ora}").format(ora=ora)


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
    # Traduttori: una data; giorno_della_settimana e mese sono nomi: «lunedì 19 ottobre 2026».
    testo = _("{giorno_della_settimana} {giorno} {mese} {anno}").format(giorno_della_settimana=GIORNI[quando.weekday()], giorno=quando.day,
        mese=MESI[quando.month - 1], anno=quando.year)
    return _con(preposizione, testo)


def data_e_ora(testo, preposizione=None):
    """Una data del file con l'ora: lunedi' 19 ottobre 2026 alle 18:03; "una
    data che non si legge" se non e' una data, con la preposizione anche
    davanti a questa."""
    quando = _leggi_data(testo)
    if not quando:
        return _con(preposizione, _("una data che non si legge"))
    # Traduttori: una data con l'ora: data è come «lunedì 19 ottobre 2026», alle_ore come «alle 18:03».
    return _con(preposizione, _("{data} {alle_ore}").format(data=data(quando), alle_ore=_alle(quando)))


def solo_la_data(testo, preposizione=None):
    quando = _leggi_data(testo)
    return data(quando, preposizione) if quando else _con(preposizione, _("una data che non si legge"))


def _decennio(anno):
    decennio = anno // 10 * 10
    if 1920 <= decennio < 2000:
        # Traduttori: un decennio del Novecento, con le ultime due cifre: «anni '80».
        return _("anni '{decennio:02d}").format(decennio=decennio % 100)
    # Traduttori: un decennio con tutte le cifre: «anni 2020».
    return _("anni {decennio}").format(decennio=decennio)


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
    return lettera.upper() if lettera else _("senza unità")


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
        # Vero se da quando il file si e' scritto e' cambiato qualcosa di vero:
        # un ascolto, un brano, un tasto, un evento, un conto o un record. Il
        # tempo che passa con MeTeOra fermo o in pausa non conta: la finestra
        # scrive il file solo se e' vero (1.113.5).
        self.modificate = False
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
            # Il messaggio finisce nell'avviso all'avvio (3.0.0).
            raise ValueError(_("il file non contiene le statistiche"))
        return dati

    def _testo(self):
        self.modificate = False
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
        self.modificate = True
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
        self.modificate = True
        if self._stato is not None:
            self.scatta(self._stato)
        self._chiudi_il_brano("chiusura")
        self._minimo("sessione_piu_breve", self.sessione["aperto"], quando=self.sessione["inizio"])
        self.conta("chiusure_regolari")
        self.dati["sessione_aperta"] = False

    def azzera(self):
        """Tutto da capo, da adesso: restano la data della prima raccolta e il
        numero degli azzeramenti. La sessione di adesso conta come la prima."""
        self.modificate = True
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
        self.modificate = True
        _piu(self.dati["conti"], nome, quanto)

    def evento(self, nome):
        self.modificate = True
        _piu(self.dati["eventi"], nome)

    def tasto(self, nome):
        self.modificate = True
        _piu(self.dati["tasti"], nome)
        self.sessione["tasti"] += 1
        self._massimo("tasti_in_una_sessione", self.sessione["tasti"], quando=self.sessione["inizio"])

    def senza_comando(self, nome):
        self.modificate = True
        _piu(self.dati["senza_comando"], nome)

    def impostazione(self, chiave):
        """Invio su una voce della finestra delle impostazioni."""
        self.modificate = True
        _piu(self.dati["impostazioni"], chiave)

    def banda(self, indice):
        self.modificate = True
        if 0 <= indice < len(self.dati["bande"]):
            self.dati["bande"][indice] += 1

    def assenza_della_scelta(self, secondi, quando):
        """La scheda o lo speaker scelti sono tornati dopo secondi di assenza,
        cominciata a quando: il primato della piu' lunga (issue 31)."""
        self.modificate = True
        self._massimo("assenza_della_scelta", round(secondi, 3), quando=quando)

    def massimo(self, nome, valore, cosa=None):
        """Un record da tenere se e' il piu' alto, con cio' di cui parla."""
        self.modificate = True
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
        return self.dati["formati"].setdefault(estensione or SENZA_ESTENSIONE, {})

    def _formato_di(self, percorso):
        """La voce del formato di un brano; per un indirizzo in rete, quella dei siti (3.2.0)."""
        if indirizzi.e_una_radio(percorso):
            return self._formato(DALLE_RADIO)
        return self._formato(DAI_SITI if formati.e_indirizzo(percorso) else formati.estensione(percorso))

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
        self.modificate = True
        _piu(tempi, "play", dt)
        _piu(giorno, "play", dt)
        self.dati["ore"][quando.hour] = round(self.dati["ore"][quando.hour] + dt, 3)
        self.dati["settimana"][quando.weekday()] = round(self.dati["settimana"][quando.weekday()] + dt, 3)
        percorso = s.get("percorso") or ""
        _piu(self._formato_di(percorso), "secondi", dt)
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
        self.modificate = True
        self._chiudi_il_brano("lasciato")
        quando = self._ora()
        _piu(self._formato_di(percorso), "avvii")
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
        self.modificate = True
        _piu(self._formato_di(brano["percorso"]), "finiti")
        _piu(self._del_brano(brano["percorso"]), "finiti")
        self.conta("finiti")
        d = brano["durata"]
        if _numero(d) and 0 < d < DURATA_CREDIBILE:
            self._massimo("finito_piu_lungo", round(d, 3), cosa=brano["percorso"])
            self._minimo("finito_piu_breve", round(d, 3), cosa=brano["percorso"])

    def brano_fermato(self):
        """Lo stop, con V o con il timer: il brano in corso e' lasciato."""
        self.modificate = True
        self._chiudi_il_brano("lasciato")

    def brano_in_errore(self, percorso):
        """Un brano che non si suona."""
        self.modificate = True
        percorso = percorso or (self._brano or {}).get("percorso") or ""
        _piu(self._formato_di(percorso), "errori")
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
        self.modificate = True
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
        if tolti:
            self.modificate = True
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
        self.modificate = True
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
        """I titoli delle sezioni e le loro funzioni. I titoli hanno
        l'iniziale minuscola, come nella riga che apre la sezione; l'elenco
        delle sezioni la fa maiuscola (3.0.0: minuscola non si puo' fare in
        tutte le lingue, maiuscola si')."""
        return [
            # Traduttori: da qui, i titoli delle sezioni delle statistiche, con l'iniziale minuscola: «Sezione 1 di 23, in breve.».
            (_("in breve"), self.in_breve),
            (_("le sessioni"), self.le_sessioni),
            (_("il tempo"), self.il_tempo),
            (_("il tempo per famiglia"), self.per_famiglia),
            (_("il tempo per formato"), self.per_formato),
            (_("come hai ascoltato"), self.come_hai_ascoltato),
            (_("i brani"), self.i_brani),
            (_("le classifiche"), self.le_classifiche),
            (_("il calendario"), self.il_calendario),
            (_("i record"), self.i_record),
            (_("muoversi nel brano"), self.muoversi),
            (_("i marker"), self.i_marker),
            (_("playlist e Preferiti"), self.le_playlist),
            (_("le registrazioni"), self.le_registrazioni),
            (_("ricerca e filtri"), self.la_ricerca),
            (_("file e tag"), self.file_e_tag),
            (_("video, sottotitoli e karaoke"), self.il_video),
            (_("plancia e tastiera"), self.la_tastiera),
            (_("console e aiuto"), self.la_console),
            (_("impostazioni, rete e MIDI"), self.le_impostazioni),
            (_("la salute"), self.la_salute),
            (_("la libreria di adesso"), self.la_libreria),
            (_("curiosità"), self.curiosita),
            (_("tutti gli eventi"), self.tutti_gli_eventi),
        ]

    def righe(self):
        sezioni = self.sezioni()
        dal = _leggi_data(self.d["dal"]) or self.oggi
        giorni = max(1, (self.oggi.date() - dal.date()).days + 1)
        # Traduttori: da_quando è la data con la preposizione, come «da domenica 1 novembre 2026 alle 10:00»; giorni come «5 giorni».
        righe = [_("Statistiche di MeTeOra {versione}, raccolte {da_quando}: {giorni}, oggi compreso.").format(versione=self.versione,
            da_quando=data_e_ora(self.d["dal"], "da"), giorni=plurale(giorni, "{n} giorno", "{n} giorni"))]
        if self.d["azzeramenti"]:
            # Traduttori: Azzerate sono le statistiche; prima e ultima sono date con l'ora; volte come «2 volte».
            righe.append(_("Prima raccolta: {prima}. Azzerate {volte}, l'ultima {ultima}.").format(prima=data_e_ora(self.d["prima_raccolta"]),
                volte=_volte(self.d["azzeramenti"]), ultima=data_e_ora(self.d["ultimo_azzeramento"])))
        righe.append(_("La barra rovesciata cerca nel testo, e Invio passa all'occorrenza seguente; senza una ricerca, Invio ed Esc chiudono. "
            "Azzera le statistiche le riporta a zero."))
        elenco_delle_sezioni = "; ".join(f"{n} {titolo[0].upper()}{titolo[1:]}" for n, (titolo, _f) in enumerate(sezioni, 1))
        righe.append(_("Le sezioni: {sezioni}.").format(sezioni=elenco_delle_sezioni))
        for n, (titolo, funzione) in enumerate(sezioni, 1):
            righe.append("")
            righe.append(_("Sezione {n} di {totale}, {titolo}.").format(n=n, totale=len(sezioni), titolo=titolo))
            try:
                contenuto = [r for r in funzione() if r]
            except Exception as e:  # noqa: BLE001 - una sezione che non si compone non deve togliere le altre
                # Traduttori: tipo è il nome dell'errore, come ZeroDivisionError; errore il suo messaggio.
                contenuto = [_("Questa sezione non si è potuta comporre: {tipo}, {errore}.").format(tipo=type(e).__name__, errore=e)]
            righe.extend(contenuto or [_("Ancora niente da dire.")])
        return righe

    # 1.

    def in_breve(self):
        avviati, finiti = self.avviati(), self.c("finiti")
        righe = [
            _("Avvii di MeTeOra: {n}.").format(n=self.c("avvii")),
            _("MeTeOra aperto: {durata}.").format(durata=durata(self.t("aperto"))),
            _("In riproduzione: {durata}, {percentuale} del tempo aperto.").format(durata=durata(self.play), percentuale=percentuale(self.play, self.t("aperto"))),
            _("Brani avviati: {avviati}; ascoltati fino alla fine: {finiti}, {percentuale}.").format(avviati=avviati, finiti=finiti,
                percentuale=percentuale(finiti, avviati)),
            self.riga_dei_file_diversi(),
        ]
        formato = self.formati_in_ordine()
        if formato:
            estensione, voce = formato[0]
            # Traduttori: formato è un'estensione, come mp3.
            righe.append(_("Il formato più ascoltato: {formato}, {durata}, {percentuale} della riproduzione.").format(formato=estensione_da_dire(estensione),
                durata=durata(voce.get("secondi", 0)), percentuale=percentuale(voce.get("secondi", 0), self.play)))
        primo = self.brani_per_volte()[:1]
        if primo:
            percorso, voce = primo[0]
            righe.append(_("Il brano più ascoltato: {nome}, {volte}.").format(nome=_nome(percorso), volte=_volte(int(voce.get("volte", 0)))))
        righe.append(_("Marker messi: {messi}; eliminati: {eliminati}.").format(messi=self.e("marker_messo"), eliminati=self.marker_eliminati()))
        return righe

    def riga_dei_file_diversi(self):
        diversi = sum(1 for voce in self.d["brani"].values() if voce.get("volte"))
        if self.file_nella_libreria:
            return ngettext("File diversi ascoltati: {diversi}, {percentuale} dei {file} file dello schedario.",
                "File diversi ascoltati: {diversi}, {percentuale} dei {file} file dello schedario.", self.file_nella_libreria).format(diversi=diversi,
                percentuale=percentuale(diversi, self.file_nella_libreria), file=self.file_nella_libreria)
        return _("File diversi ascoltati: {n}.").format(n=diversi)

    # 2.

    def le_sessioni(self):
        s = self.s.sessione
        record = self.d["record"]
        avvii = self.c("avvii")
        righe = [_("Questa è la sessione numero {numero}, aperta {quando}: da {durata}.").format(numero=s["numero"], quando=data_e_ora(s["inizio"]),
            durata=durata(s["aperto"]))]
        if avvii:
            righe.append(_("Durata media di una sessione: {durata}.").format(durata=durata(self.t("aperto") / avvii)))
        if "sessione_piu_lunga" in record:
            righe.append(_("La sessione più lunga: {durata}, cominciata {quando}.").format(durata=durata(record["sessione_piu_lunga"]["valore"]),
                quando=data_e_ora(record["sessione_piu_lunga"]["quando"])))
        if "sessione_piu_breve" in record:
            righe.append(_("La sessione più breve: {durata}, cominciata {quando}.").format(durata=durata(record["sessione_piu_breve"]["valore"]),
                quando=data_e_ora(record["sessione_piu_breve"]["quando"])))
        if "brani_in_una_sessione" in record:
            righe.append(_("Più brani in una sessione: {n}, nella sessione cominciata {quando}.").format(n=record["brani_in_una_sessione"]["valore"],
                quando=data_e_ora(record["brani_in_una_sessione"]["quando"])))
        righe.append(_("Chiusure regolari: {n}.").format(n=self.c("chiusure_regolari")))
        non_regolari = self.c("chiusure_non_regolari")
        riga = _("Chiusure non regolari, con MeTeOra caduto, chiuso a forza o il PC spento: {n}").format(n=non_regolari)
        if non_regolari and "chiusura_non_regolare" in record:
            # Traduttori: di_quando è la data con la preposizione, come «di lunedì 19 ottobre 2026 alle 18:03».
            riga += _("; l'ultima dopo il salvataggio {di_quando}").format(di_quando=data_e_ora(record["chiusura_non_regolare"]["quando"], "di"))
        righe.append(riga + ".")
        righe.append(_("Avvii con un file aperto da Windows: {n}.").format(n=self.c("aperti_all_avvio")))
        righe.append(_("File e cartelle passati a MeTeOra già aperto, da Windows o da un'altra copia: {n}.").format(n=self.c("aperti_da_un_altra_copia")))
        righe.append(_("File e cartelle trascinati sulla finestra: {n}.").format(n=self.c("aperti_col_trascinamento")))
        righe.append(_("Avvii con la ripresa del brano lasciato: {n}.").format(n=self.e("ripresa_all_avvio")))
        righe.append(_("Aggiornamenti di MeTeOra: {n}.").format(n=self.c("aggiornamenti")))
        versioni = sorted(self.d["versioni"].items(), key=lambda v: v[1])
        if versioni:
            # Traduttori: le versioni con la data del primo avvio, come «1.103.0 da domenica 1 novembre 2026, 1.104.0 da lunedì 2 novembre 2026».
            righe.append(_("Versioni usate: {versioni}.").format(versioni=", ".join(f"{v} {solo_la_data(quando, 'da')}" for v, quando in versioni)))
        return righe

    # 3.

    def il_tempo(self):
        aperto = self.t("aperto")
        video = self.t("play_video")
        righe = [
            _("MeTeOra aperto: {durata}.").format(durata=durata(aperto)),
            _("In riproduzione: {durata}, {percentuale} del tempo aperto.").format(durata=durata(self.play), percentuale=percentuale(self.play, aperto)),
            _("In pausa: {durata}, {percentuale}.").format(durata=durata(self.t("pausa")), percentuale=percentuale(self.t("pausa"), aperto)),
            _("Fermo, senza niente che suona: {durata}, {percentuale}.").format(durata=durata(self.t("fermo")), percentuale=percentuale(self.t("fermo"), aperto)),
            _("Riproduzione di audio: {durata}, {percentuale} della riproduzione.").format(durata=durata(self.t("play_audio")),
                percentuale=percentuale(self.t("play_audio"), self.play)),
            _("Riproduzione di video: {durata}, {percentuale}.").format(durata=durata(video), percentuale=percentuale(video, self.play)),
        ]
        if video:
            righe.append(_("Video con l'immagine: {durata}, {percentuale} del tempo dei video.").format(durata=durata(self.t("video_immagine")),
                percentuale=percentuale(self.t("video_immagine"), video)))
            righe.append(_("Video con l'immagine spenta, solo l'audio: {durata}, {percentuale}.").format(durata=durata(self.t("video_senza_immagine")),
                percentuale=percentuale(self.t("video_senza_immagine"), video)))
            righe.append(_("Video a schermo intero: {durata}.").format(durata=durata(self.t("schermo_intero"))))
        pause = self.c("pause")
        riga = _("Pause: {n}").format(n=pause)
        if pause:
            riga += _(", lunghe in media {durata}").format(durata=durata(self.t("pausa") / pause))
        if "pausa_piu_lunga" in self.d["record"]:
            riga += _("; la più lunga: {durata}").format(durata=durata(self.d["record"]["pausa_piu_lunga"]["valore"]))
        righe.append(riga + ".")
        filata = self.d["record"].get("filata")
        if filata:
            righe.append(_("La riproduzione più lunga senza fermarsi: {durata}, {brani}, cominciata {quando}.").format(durata=durata(filata["valore"]),
                brani=plurale(int(filata.get("brani", 1)), "{n} brano", "{n} brani di fila"), quando=data_e_ora(filata["quando"])))
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
            righe.append(_("{famiglia}: {durata}, {percentuale} della riproduzione; {avvii}.").format(famiglia=FAMIGLIE[chiave], durata=durata(f["secondi"]),
                percentuale=percentuale(f["secondi"], self.play), avvii=plurale(int(f["avvii"]), "{n} avvio", "{n} avvii")))
        return righe

    def per_formato(self):
        voci = self.formati_in_ordine()
        suonati = {e for e, _v in voci}
        righe = [_("Formati suonati: {n} dei {totale} che MeTeOra conosce.").format(n=len([e for e, _v in voci if e not in (DAI_SITI, DALLE_RADIO)]), totale=len(formati.TUTTI))]
        for estensione, voce in voci:
            avvii = int(voce.get("avvii", 0))
            quanti = plurale(avvii, "{n} avvio", "{n} avvii")
            riga = f"{estensione_da_dire(estensione)}: {durata(voce.get('secondi', 0))}, {percentuale(voce.get('secondi', 0), self.play)}; {quanti}"
            if avvii:
                riga += _(", {percentuale} fino alla fine").format(percentuale=percentuale(voce.get("finiti", 0), avvii))
            righe.append(riga + ".")
        # Solo quanti sono, senza l'elenco dei nomi (1.104.0).
        mai = len(formati.TUTTI - suonati)
        if mai:
            righe.append(_("Formati mai suonati: {n}.").format(n=mai))
        return righe

    # 6.

    def come_hai_ascoltato(self):
        record = self.d["record"]
        righe = []
        if self.play:
            riga = _("Volume medio, pesato sul tempo: {volume}").format(volume=round(self.t("volume_pesato") / self.play))
            if "volume_piu_alto" in record:
                riga += _("; il più alto raggiunto: {volume}").format(volume=record["volume_piu_alto"]["valore"])
            righe.append(riga + ".")
        righe.append(_("Volume oltre 100, con il limitatore: {durata}, {percentuale} della riproduzione.").format(durata=durata(self.t("oltre_100")),
            percentuale=percentuale(self.t("oltre_100"), self.play)))
        righe.append(_("In muto mentre suonava: {durata}.").format(durata=durata(self.t("muto"))))
        cambiata = self.t("velocita_cambiata")
        riga = _("Velocità diversa dal normale: {durata}, {percentuale}").format(durata=durata(cambiata), percentuale=percentuale(cambiata, self.play))
        if cambiata and "velocita_piu_alta" in record:
            riga += _("; la più alta {alta}, la più bassa {bassa}").format(alta=numero_decimale(record["velocita_piu_alta"]["valore"]),
                bassa=numero_decimale(record.get("velocita_piu_bassa", {}).get("valore", 1)))
        righe.append(riga + ".")
        if cambiata:
            contenuto = self.t("contenuto_a_velocita_cambiata")
            guadagno = contenuto - cambiata
            if guadagno >= 0:
                righe.append(_("Tempo guadagnato con la velocità: {durata}; brani che duravano {contenuto} ascoltati in {ascolto}.").format(durata=durata(guadagno),
                    contenuto=durata(contenuto), ascolto=durata(cambiata)))
            else:
                righe.append(_("Tempo in più con la velocità: {durata}; brani che duravano {contenuto} ascoltati in {ascolto}.").format(durata=durata(-guadagno),
                    contenuto=durata(contenuto), ascolto=durata(cambiata)))
        riga = _("Tono cambiato: {durata}").format(durata=durata(self.t("tono_cambiato")))
        if self.t("tono_cambiato") and "tono_piu_alto" in record:
            alto, basso = int(record["tono_piu_alto"]["valore"]), int(record.get("tono_piu_basso", {}).get("valore", 0))
            # Traduttori: alto e basso sono semitoni con il segno, come +3 e -2; la forma la sceglie alto.
            riga += ngettext("; il più alto {alto:+d} semitono, il più basso {basso:+d}", "; il più alto {alto:+d} semitoni, il più basso {basso:+d}",
                abs(alto)).format(alto=alto, basso=basso)
        righe.append(riga + ".")
        righe.append(_("Equalizzatore con almeno una banda fuori dallo zero: {durata}, {percentuale}.").format(durata=durata(self.t("eq")),
            percentuale=percentuale(self.t("eq"), self.play)))
        bande = self.d["bande"]
        if any(bande):
            indice = max(range(len(bande)), key=lambda i: bande[i])
            righe.append(_("La banda più ritoccata: {banda}, {volte}; in tutto {ritocchi}.").format(banda=valori.nome_della_banda(indice),
                volte=_volte(int(bande[indice])), ritocchi=plurale(int(sum(bande)), "{n} ritocco", "{n} ritocchi")))
        righe.append(_("Dissolvenza incrociata accesa: {durata}, {percentuale}; passaggi sfumati: {n}.").format(durata=durata(self.t("dissolvenza")),
            percentuale=percentuale(self.t("dissolvenza"), self.play), n=self.c("passaggi_sfumati")))
        righe.append(_("Riproduzione casuale accesa: {durata}, {percentuale}; brani scelti a caso: {n}.").format(durata=durata(self.t("casuale")),
            percentuale=percentuale(self.t("casuale"), self.play), n=self.c("a_caso")))
        righe.append(_("Ripetizione del brano: {brano}; ripetizione della lista: {lista}.").format(brano=durata(self.t("ripetizione_brano")),
            lista=durata(self.t("ripetizione_lista"))))
        righe.append(_("Volume uniforme con ReplayGain: per brano {brano}, per album {album}.").format(brano=durata(self.t("replaygain_brano")),
            album=durata(self.t("replaygain_album"))))
        schede = sorted(((nome, secondi) for nome, secondi in self.d["schede_audio"].items() if secondi), key=lambda s: -s[1])
        if schede:
            righe.append(_("Schede audio: {schede}.").format(schede="; ".join(f"{nome}, {percentuale(secondi, self.play)}" for nome, secondi in schede)))
        return righe

    def _riga_delle_uscite(self):
        """Le schede e gli speaker che vanno e tornano (issue 31, 1.119.0)."""
        # Traduttori: la scelta è la scheda audio o lo speaker scelti; sparita, tornata e cambiata come «2 volte».
        riga = _("Uscite: la scelta sparita {sparita} e tornata {tornata}; la scheda di Windows cambiata da sola {cambiata}; "
            "brani ripresi dopo un'uscita persa: {ripresi}; speaker Cast scelti: {speaker}").format(sparita=_volte(self.e("scheda_sparita")),
            tornata=_volte(self.e("scheda_tornata")), cambiata=_volte(self.e("scheda_di_windows")), ripresi=self.c("brani_ripresi_dopo_l_uscita_persa"),
            speaker=self.c("speaker_scelti"))
        assenza = self.d["record"].get("assenza_della_scelta")
        if assenza:
            riga += _("; l'assenza più lunga della scelta: {durata}, cominciata {quando}").format(durata=durata(assenza["valore"]), quando=data_e_ora(assenza["quando"]))
        return riga + "."

    # 7.

    def i_brani(self):
        modi = Counter()
        for modo, quanti in self.d["modi"].items():
            modi[MODI.get(modo, "scelti")] += int(quanti)
        avviati = self.avviati()
        finiti, lasciati, errori = self.c("finiti"), self.c("lasciati"), self.c("errori_di_riproduzione")
        righe = [
            _("Brani avviati: {n}.").format(n=avviati),
            _("Scelti da te, con X, Invio, il menu, un marker o un capitolo: {n}.").format(n=modi["scelti"]),
            _("Partiti da soli, alla fine del brano prima: {da_soli}; di questi, tornando al punto A del loop: {al_punto_a}.").format(da_soli=modi["da_soli"],
                al_punto_a=int(self.d["modi"].get("ritorno_al_punto_a", 0))),
            _("Con B: {b}; con Z: {z}; con N, a caso: {n}.").format(b=modi["b"], z=modi["z"], n=modi["n"]),
            _("Aprendo una playlist con J, K o le cifre: {n}.").format(n=modi["playlist"]),
            _("Ripresi all'avvio: {n}.").format(n=modi["ripresa"]),
            _("Ascoltati fino alla fine: {n}, {percentuale}.").format(n=finiti, percentuale=percentuale(finiti, avviati)),
            _("Lasciati prima della fine: {n}, {percentuale}; di questi, nei primi {secondi} secondi: {subito}.").format(n=lasciati,
                percentuale=percentuale(lasciati, avviati), secondi=int(SUBITO), subito=self.c("lasciati_subito")),
            _("Non suonati per un errore: {n}, {percentuale}.").format(n=errori, percentuale=percentuale(errori, avviati)),
            _("Ancora in corso quando hai chiuso MeTeOra: {n}.").format(n=self.c("in_corso_alla_chiusura")),
            _("Ripartiti da capo con X, non contati come avvii: {n}.").format(n=self.e("da_capo")),
            self.riga_dei_file_diversi(),
        ]
        brani = self.d["brani"].values()
        righe.append(_("Ascoltati una volta sola: {una}; più di 10 volte: {piu_di_10}.").format(una=sum(1 for v in brani if v.get("volte") == 1),
            piu_di_10=sum(1 for v in brani if v.get("volte", 0) > 10)))
        righe.append(_("Sottobrani diversi dei SID e delle console: {n}.").format(n=sum(len(v.get("sotto", [])) for v in brani)))
        durate = [(v.get("volte", 0), self.tag(p)[1]) for p, v in self.d["brani"].items() if v.get("volte")]
        note = [(volte, d) for volte, d in durate if _numero(d) and 0 < d < DURATA_CREDIBILE]
        if note:
            righe.append(_("Durata media dei brani avviati, dallo schedario: {durata}.").format(durata=durata(sum(v * d for v, d in note) / sum(v for v, _d in note))))
        if lasciati:
            righe.append(_("Ascolto medio prima di lasciare un brano: {durata}.").format(durata=durata(self.c("secondi_dei_lasciati") / lasciati)))
        righe.append(_("File lunghi ripresi dal punto lasciato: {n}.").format(n=self.c("ripresi_dal_punto")))
        return righe

    # 8.

    def brani_per_volte(self):
        voci = [(p, v) for p, v in self.d["brani"].items() if v.get("volte")]
        return sorted(voci, key=lambda pv: (-pv[1].get("volte", 0), -pv[1].get("secondi", 0), pv[0]))

    def di_chi(self, percorso):
        autore = self.tag(percorso)[0].get("autore")
        # Traduttori: l'autore di un brano, dopo il suo nome: «Commando.sid, di Rob Hubbard».
        return _(", di {autore}").format(autore=autore) if autore and autore != "<?>" else ""

    def classifica(self, titolo, conti, scrivi, posti=POSTI):
        """Le righe di una classifica: il titolo e i primi posti, gia' in ordine."""
        voci = list(conti)[:posti]
        if not voci:
            return []
        return [f"{titolo}:"] + [f"{n}. {scrivi(*voce) if isinstance(voce, tuple) else scrivi(voce)}" for n, voce in enumerate(voci, 1)]

    def le_classifiche(self):
        righe = []
        righe += self.classifica(_("I {posti} brani ascoltati più volte").format(posti=POSTI), self.brani_per_volte(),
            lambda p, v: f"{_nome(p)}{self.di_chi(p)}: {_volte(int(v.get('volte', 0)))}, {durata(v.get('secondi', 0))}.")
        per_tempo = sorted(((p, v) for p, v in self.d["brani"].items() if v.get("secondi")), key=lambda pv: (-pv[1]["secondi"], pv[0]))
        righe += self.classifica(_("I {posti} brani ascoltati più a lungo").format(posti=POSTI), per_tempo,
            # Traduttori: nome è il nome di un file; di_chi è vuoto o l'autore, come «, di Rob Hubbard»; volte come «3 volte».
            lambda p, v: _("{nome}{di_chi}: {durata}, in {volte}.").format(nome=_nome(p), di_chi=self.di_chi(p), durata=durata(v["secondi"]),
                volte=_volte(int(v.get("volte", 0)))))
        tempo_dei_brani = sum(v.get("secondi", 0) for v in self.d["brani"].values())
        for chiave, titolo, senza in (("autore", _("I {posti} autori più ascoltati, dai tag").format(posti=POSTI), _("Senza autore nei tag")),
                ("album", _("I {posti} album più ascoltati, dai tag").format(posti=POSTI), _("Senza album nei tag")),
                ("genere", _("I {posti} generi più ascoltati, dai tag").format(posti=POSTI), _("Senza genere nei tag"))):
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
            righe += self.classifica(titolo, ordine,
                # Traduttori: nome è un autore, un album o un genere; avvii e file come «3 avvii» e «2 file».
                lambda k, secondi=secondi, avvii=avvii, file=file: _("{nome}: {durata}, {percentuale}; {avvii} di {file}.").format(nome=k,
                    durata=durata(secondi[k]), percentuale=percentuale(secondi[k], tempo_dei_brani), avvii=plurale(int(avvii[k]), "{n} avvio", "{n} avvii"),
                    file=plurale(file[k], "{n} file", "{n} file")))
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
                parti.append(_("senza anno {percentuale}").format(percentuale=percentuale(senza_anno, tempo_dei_brani)))
            righe.append(_("Per decennio, dall'anno dei tag: {decenni}.").format(decenni="; ".join(parti)))
            anno = max(anni, key=lambda a: (anni[a], -a))
            righe.append(_("L'anno più ascoltato: {anno}, {percentuale}.").format(anno=anno, percentuale=percentuale(anni[anno], tempo_dei_brani)))
        cartelle, unita = Counter(), Counter()
        for p, v in self.d["brani"].items():
            cartelle[ntpath.dirname(p) or p] += v.get("secondi", 0)
            unita[unita_di(p)] += v.get("secondi", 0)
        righe += self.classifica(_("Le {posti} cartelle più ascoltate").format(posti=POSTI), sorted(((k, s) for k, s in cartelle.items() if s), key=lambda ks: -ks[1]),
            lambda k, s: f"{k}: {durata(s)}, {percentuale(s, tempo_dei_brani)}.")
        if any(unita.values()):
            righe.append(_("Per unità: {unita}.").format(unita="; ".join(f"{k} {percentuale(s, tempo_dei_brani)}" for k, s in sorted(unita.items(), key=lambda ks: -ks[1]) if s)))
        sorgenti = sorted(((nome, secondi) for nome, secondi in self.d["sorgenti"].items() if secondi), key=lambda s: -s[1])
        if sorgenti:
            righe.append(_("Da dove: {sorgenti}.").format(sorgenti="; ".join(f"{nome} {percentuale(secondi, self.play)}" for nome, secondi in sorgenti)))
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
        # Traduttori: aperti è quanti giorni MeTeOra è stato aperto, su tutti quelli della raccolta.
        righe = [_("Giorni con MeTeOra aperto: {aperti} su {di_calendario}; con almeno un brano ascoltato: {con_ascolto}.").format(aperti=len(aperti),
            di_calendario=di_calendario, con_ascolto=len(con_ascolto))]
        if con_ascolto:
            totale = sum(giorni[g]["play"] for g in con_ascolto)
            righe.append(_("Ascolto medio nei giorni con ascolto: {durata}.").format(durata=durata(totale / len(con_ascolto))))
            record = max(con_ascolto, key=lambda g: giorni[g]["play"])
            righe.append(_("Il giorno con più ascolto: {data}, {durata}.").format(data=data(record), durata=durata(giorni[record]["play"])))
            serie, inizio, migliore = 1, con_ascolto[0], (1, con_ascolto[0], con_ascolto[0])
            for prima, dopo in itertools.pairwise(con_ascolto):
                if (dopo - prima).days == 1:
                    serie += 1
                else:
                    serie, inizio = 1, dopo
                if serie > migliore[0]:
                    migliore = (serie, inizio, dopo)
            if migliore[0] > 1:
                # Traduttori: da_quando e a_quando sono date con la preposizione, come «da domenica 1 novembre 2026» e «a martedì 3 novembre 2026».
                righe.append(_("La serie più lunga di giorni di fila con ascolto: {n}, {da_quando} {a_quando}.").format(n=migliore[0],
                    da_quando=data(migliore[1], "da"), a_quando=data(migliore[2], "a")))
            else:
                righe.append(_("La serie più lunga di giorni di fila con ascolto: 1."))
            fine = self.oggi.date() if self.oggi.date() in giorni and giorni[self.oggi.date()].get("play") else self.oggi.date() - datetime.timedelta(days=1)
            di_adesso = 0
            presenti = set(con_ascolto)
            while fine - datetime.timedelta(days=di_adesso) in presenti:
                di_adesso += 1
            righe.append(_("La serie di adesso: {giorni}.").format(giorni=plurale(di_adesso, "{n} giorno", "{n} giorni")))
        # Negli elenchi per mese, per giorno, per fascia e per ora solo le voci
        # con un po' d'ascolto: senza nessun mese d'ascolto la riga dei mesi
        # non si scrive, perche' la prima riga gia' dice zero giorni (1.104.0).
        mesi = Counter()
        for g, v in giorni.items():
            mesi[(g.year, g.month)] += v.get("play", 0)
        mesi = sorted((am, s) for am, s in mesi.items() if s)
        if mesi:
            righe.append(_("Per mese: {mesi}.").format(mesi="; ".join(f"{MESI[m - 1]} {a}, {durata(s)}" for (a, m), s in mesi)))
        settimana = self.d["settimana"]
        totale = sum(settimana)
        if totale:
            ordine = sorted((i for i in range(7) if settimana[i]), key=lambda i: -settimana[i])
            righe.append(_("Per giorno della settimana: {giorni}.").format(giorni="; ".join(f"{GIORNI[i]} {percentuale(settimana[i], totale)}" for i in ordine)))
        ore = self.d["ore"]
        totale = sum(ore)
        if totale:
            # Traduttori: le fasce del giorno, con l'ora in cui cominciano, nella riga «Per fascia: sera, dalle 18: 60.0%; mattina, dalle 6: 40.0%.».
            fasce = [(_("sera, dalle 18"), range(18, 24)), (_("pomeriggio, dalle 12"), range(12, 18)), (_("mattina, dalle 6"), range(6, 12)),
                (_("notte, da mezzanotte alle 6"), range(0, 6))]
            fasce = [(nome, sum(ore[h] for h in fascia)) for nome, fascia in fasce]
            fasce = sorted((f for f in fasce if f[1]), key=lambda f: -f[1])
            righe.append(_("Per fascia: {fasce}.").format(fasce="; ".join(f"{nome}: {percentuale(secondi, totale)}" for nome, secondi in fasce)))
            ora = max(range(24), key=lambda h: ore[h])
            # Traduttori: dalle e alle sono l'inizio e la fine dell'ora, come «dalle 13» e «alle 14»; durata come «2 minuti».
            righe.append(_("L'ora con più ascolto: {dalle} {alle}, {percentuale}, {durata}.").format(dalle=dalle(ora), alle=alle((ora + 1) % 24),
                percentuale=percentuale(ore[ora], totale), durata=durata(ore[ora])))
            # Traduttori: un'ora del giorno con la sua parte d'ascolto: «ore 10: 60.0%» dice dalle 10 alle 11.
            per_ora = "; ".join(_("ore {ora}: {percentuale}").format(ora=h, percentuale=percentuale(ore[h], totale)) for h in range(24) if ore[h])
            righe.append(_("Per ora: {ore}.").format(ore=per_ora))
        con_marker = [g for g, v in giorni.items() if v.get("marker")]
        if con_marker:
            g = max(con_marker, key=lambda g: giorni[g]["marker"])
            righe.append(_("Il giorno con più marker messi: {data}, {n}.").format(data=data(g), n=int(giorni[g]["marker"])))
        return righe

    # 10.

    def i_record(self):
        r = self.d["record"]
        righe = []
        if "sessione_piu_lunga" in r:
            righe.append(_("La sessione più lunga: {durata}, cominciata {quando}.").format(durata=durata(r["sessione_piu_lunga"]["valore"]),
                quando=data_e_ora(r["sessione_piu_lunga"]["quando"])))
        if "filata" in r:
            righe.append(_("La riproduzione più lunga senza fermarsi: {durata}, {brani}.").format(durata=durata(r["filata"]["valore"]),
                brani=plurale(int(r["filata"].get("brani", 1)), "{n} brano", "{n} brani di fila")))
        if "pausa_piu_lunga" in r:
            righe.append(_("La pausa più lunga: {durata}, {quando}.").format(durata=durata(r["pausa_piu_lunga"]["valore"]),
                quando=data_e_ora(r["pausa_piu_lunga"]["quando"])))
        if "finito_piu_lungo" in r:
            righe.append(_("Il brano più lungo ascoltato fino alla fine: {nome}, {durata}.").format(nome=_nome(r["finito_piu_lungo"].get("cosa", "")),
                durata=durata(r["finito_piu_lungo"]["valore"])))
        if "finito_piu_breve" in r:
            righe.append(_("Il brano più breve ascoltato fino alla fine: {nome}, {durata}.").format(nome=_nome(r["finito_piu_breve"].get("cosa", "")),
                durata=durata(r["finito_piu_breve"]["valore"])))
        if "volume_piu_alto" in r:
            righe.append(_("Il volume più alto: {volume}, {quando}.").format(volume=r["volume_piu_alto"]["valore"], quando=data_e_ora(r["volume_piu_alto"]["quando"])))
        alta, bassa = r.get("velocita_piu_alta", {}).get("valore", 1), r.get("velocita_piu_bassa", {}).get("valore", 1)
        if alta != 1 or bassa != 1:
            righe.append(_("La velocità più alta: {alta}; la più bassa: {bassa}.").format(alta=numero_decimale(alta), bassa=numero_decimale(bassa)))
        if "risultati" in r:
            # Traduttori: ricerca è quello che si è cercato, e dove, come «hubbard in tutto MeTeOra»; n quanti risultati.
            righe.append(_("La ricerca con più risultati: {ricerca}, {n}.").format(ricerca=r["risultati"].get("cosa", ""), n=r["risultati"]["valore"]))
        if "ricerca_piu_lunga" in r:
            # Traduttori: ricerca è quello che si è cercato, e dove, come «hubbard in tutto MeTeOra».
            righe.append(_("La ricerca più lunga: {durata}, {ricerca}.").format(durata=durata(r["ricerca_piu_lunga"]["valore"]),
                ricerca=r["ricerca_piu_lunga"].get("cosa", "")))
        if "selezione" in r:
            righe.append(_("La selezione più grande della plancia: {voci}.").format(voci=plurale(int(r["selezione"]["valore"]), "{n} voce", "{n} voci")))
        if "tasti_in_una_sessione" in r:
            righe.append(_("Più tasti in una sessione: {n}.").format(n=r["tasti_in_una_sessione"]["valore"]))
        if "brani_in_una_sessione" in r:
            righe.append(_("Più brani in una sessione: {n}.").format(n=r["brani_in_una_sessione"]["valore"]))
        return righe

    # 11.

    def muoversi(self):
        return [
            _("Salti in avanti con E: {n}, per {durata} in tutto.").format(n=self.e("avanti"), durata=durata(self.c("secondi_avanti"))),
            _("Salti indietro con Q: {n}, per {durata} in tutto.").format(n=self.e("indietro"), durata=durata(self.c("secondi_indietro"))),
            _("Secondi dei salti cambiati, con Maiuscolo e Q o E: {n}.").format(n=self.e("passo_di_salto")),
            _("Vai a un tempo, con W o con la linea del tempo: {n}.").format(n=self.e("vai_a_tempo")),
            _("Capitoli: avanti con il punto {avanti}, indietro con la virgola {indietro}.").format(avanti=self.e("capitolo_successivo"),
                indietro=self.e("capitolo_precedente")),
            _("Loop A-B: punti A {a}, punti B {b}, tolti {tolti}; ritorni al punto A {ritorni}.").format(a=self.e("loop_a_messo"), b=self.e("loop_b_messo"),
                tolti=self.e("loop_tolto"), ritorni=self.e("ritorno_al_punto_a")),
            # Traduttori: i numeri dei timer; a_fine_brano è quanti di quelli impostati erano a fine brano.
            _("Timer di spegnimento: {impostati} impostati, di cui a fine brano {a_fine_brano}; {scaduti} scaduti, {tolti} tolti.").format(
                impostati=self.e("timer_impostato"), a_fine_brano=self.c("timer_a_fine_brano"), scaduti=self.e("timer_scaduto"), tolti=self.e("timer_tolto")),
        ]

    # 12.

    def i_marker(self):
        righe = [
            _("Marker messi, con T: {n}.").format(n=self.e("marker_messo")),
            _("Marker rinominati: {n}.").format(n=self.e("marker_rinominato")),
            _("Marker eliminati: {n}.").format(n=self.marker_eliminati()),
            _("Uno per uno, con Canc o dal menu: {n}.").format(n=self.c("marker_tolti_uno")),
            # Traduttori: n è quanti marker sono stati tolti; volte come «2 volte».
            _("Prima del punto, con Ctrl e R: {n}, in {volte}.").format(n=self.c("marker_tolti_prima"), volte=_volte(self.e("marker_tolti_prima"))),
            _("Dopo il punto, con Maiuscolo e R: {n}, in {volte}.").format(n=self.c("marker_tolti_dopo"), volte=_volte(self.e("marker_tolti_dopo"))),
            _("Tutti quelli del brano, con Maiuscolo e T: {n}, in {volte}.").format(n=self.c("marker_tolti_tutti"), volte=_volte(self.e("marker_tolti_tutti"))),
            _("Con la selezione multipla della plancia: {n}.").format(n=self.c("marker_tolti_selezione")),
            _("Dalla finestra dei marcatori: {n}.").format(n=self.c("marker_tolti_finestra")),
            _("Salti ai marker: con Y {con_y}; con Maiuscolo e le cifre {con_le_cifre}; dalla plancia, con Vai al marker o X {dalla_plancia}.").format(
                con_y=self.e("marker_indietro") + self.e("marker_avanti"), con_le_cifre=self.c("marker_con_le_cifre"),
                dalla_plancia=max(0, self.c("vai_al_marker") - self.c("marker_con_le_cifre"))),
            _("Finestra dei marcatori aperta: {volte}; esportazioni {esportazioni}; importazioni {importazioni}; cancellazioni di tutto {cancellazioni}.").format(
                volte=_volte(self.e("marcatori")), esportazioni=self.e("marcatori_esportati"), importazioni=self.e("marcatori_importati"),
                cancellazioni=self.e("marcatori_cancellati")),
            _("Segnalibro messo, con Ctrl e Maiuscolo e H: {messo}; ripreso, con Maiuscolo e H: {ripreso}; tolto, con Ctrl e H: {tolto}.").format(
                messo=_volte(self.e("segnalibro_messo")), ripreso=_volte(self.e("al_segnalibro")), tolto=_volte(self.e("segnalibro_tolto"))),
        ]
        con_marker = sorted(((p, v) for p, v in self.d["brani"].items() if v.get("marker")), key=lambda pv: (-pv[1]["marker"], pv[0]))
        if con_marker:
            p, v = con_marker[0]
            righe.append(_("Il brano con più marker messi: {nome}, {n}.").format(nome=_nome(p), n=int(v["marker"])))
        return righe

    # 13.

    def le_playlist(self):
        create = self.e("playlist_creata") + self.e("nuova_playlist")
        dalla_ricerca, da_cartella = self.c("playlist_dalla_ricerca"), self.c("playlist_da_una_cartella")
        # Le importate da un M3U o da un PLS suonano anche loro playlist_creata (1.113.0).
        importate = self.c("playlist_importate")
        # Anche le playlist dei siti, negli Indirizzi, suonano playlist_creata
        # e, rilette, playlist_riletta (3.2.0).
        dai_siti, rilette_dai_siti = self.c("playlist_dai_siti"), self.c("playlist_rilette_dai_siti")
        altre = max(0, self.e("playlist_creata") - dalla_ricerca - da_cartella - importate - dai_siti)
        return [
            _("Playlist create: {create}; da una cartella {da_cartella}, dai risultati della ricerca {dalla_ricerca}, "
                "importate {importate}, da una selezione o dal menu {altre}, vuote {vuote}.").format(create=create, da_cartella=da_cartella,
                dalla_ricerca=dalla_ricerca, importate=importate, altre=altre, vuote=self.e("nuova_playlist")),
            _("Playlist importate da un M3U o da un PLS: {importate}, con {brani}; "
                "arrivate di nuovo con il loro file com'era: {di_nuovo}; rilette dal loro file cambiato: {rilette}.").format(importate=importate,
                brani=plurale(self.c("brani_importati"), "{n} brano", "{n} brani"), di_nuovo=self.e("playlist_gia_importata"),
                rilette=max(0, self.e("playlist_riletta") - rilette_dai_siti)),
            # La ricerca dei contenuti (issue 47, 3.9.0).
            _("Ricerche dei contenuti: {cercati}, con {trovati} risultati e altri risultati chiesti {altri}; entrati negli Indirizzi dopo un minuto di ascolto: {tenuti}.").format(
                cercati=self.c("contenuti_cercati"), trovati=self.c("contenuti_trovati"), altri=_volte(self.c("contenuti_altri")), tenuti=self.c("indirizzi_tenuti")),
            _("Indirizzi in rete aperti: {aperti}; playlist dei siti: {playlist}, con {brani}, e rilette dal sito {rilette}; "
                "flussi chiesti a yt-dlp: {flussi}; yt-dlp aggiornato {aggiornato}.").format(aperti=self.c("indirizzi_aperti"), playlist=dai_siti,
                brani=plurale(self.c("brani_dai_siti"), "{n} brano", "{n} brani"), rilette=rilette_dai_siti, flussi=self.c("flussi_chiesti"),
                aggiornato=_volte(self.c("ytdlp_aggiornato"))),
            _("Radio ascoltate: {ascoltate}, entrate fra le Recenti dopo un minuto di ascolto {tenute}; cercate per nome: {cercate}; altre radio chieste: {altre}; "
                "titoli in onda arrivati: {titoli}.").format(ascoltate=self.c("radio_ascoltate"), tenute=self.c("radio_tenute"), cercate=_volte(self.c("radio_cercate")),
                altre=_volte(self.c("radio_altre")), titoli=self.c("titoli_in_onda")),
            # Il filtro dei fotogrammi del ripetitore (3.11.6).
            _("Radio MP3 e AAC ripetute a uno speaker: punti rotti tolti {rotture}, per {peso}.").format(rotture=self.c("rotture_tolte_allo_speaker"),
                peso=_peso(self.c("byte_rotti_tolti_allo_speaker"))),
            _("Playlist rinominate: {rinominate}; eliminate: {eliminate}; ordinate: {ordinate}; "
                "invertite: {invertite}; mescolate: {mescolate}; rimesse nell'ordine di prima: {rimesse}.").format(rinominate=self.e("playlist_rinominata"),
                eliminate=self.e("playlist_eliminata"), ordinate=self.e("playlist_ordinata"), invertite=self.e("ordine_invertito"),
                mescolate=self.e("playlist_mescolata"), rimesse=self.e("ordine_ripristinato")),
            _("Brani aggiunti alle playlist: {n}, in {volte}.").format(n=self.c("brani_aggiunti"), volte=_volte(self.c("aggiunte"))),
            _("Brani tolti: {tolti}; spostati: {spostati}; segnati come saltati: {saltati}, e tornati: {tornati}.").format(tolti=self.c("brani_tolti"),
                spostati=self.e("brano_spostato"), saltati=self.e("saltato_acceso"), tornati=self.e("saltato_spento")),
            _("Brani messi nei Preferiti: {messi}; c'erano già: {gia}.").format(messi=self.e("preferito_aggiunto"), gia=self.e("gia_nei_preferiti")),
            _("Filtri messi: {messi}; tolti: {tolti}.").format(messi=self.e("filtro_messo"), tolti=self.e("filtro_tolto")),
        ]

    # 14.

    def le_registrazioni(self):
        """Le registrazioni delle radio e degli indirizzi in rete (issue 42,
        3.5.0): dalla 3.9.2 una sezione loro, come le altre raccolte, con la
        media, le dirette e le puntate, i formati e i primati."""
        r = self.d["record"]
        finite, secondi, byte = self.c("registrazioni_finite"), self.c("secondi_registrati"), self.c("byte_registrati")
        righe = [_("Registrazioni avviate: {avviate}, di cui con l'attesa di Alt con R {attese}; file prodotti: {finite}, con {durata} e {peso}.").format(
            avviate=self.c("registrazioni_avviate"), attese=self.c("registrazioni_in_ascolto"), finite=finite, durata=durata(secondi), peso=_peso(byte))]
        if finite:
            righe.append(_("In media una registrazione dura {durata} e pesa {peso}.").format(durata=durata(secondi / finite), peso=_peso(byte / finite)))
        dirette, puntate = self.c("registrazioni_di_dirette"), self.c("registrazioni_di_puntate")
        if dirette or puntate:
            righe.append(_("Dalle dirette, come le radio: {dirette}; dalle puntate e dai video, che finiscono da soli: {puntate}.").format(dirette=dirette, puntate=puntate))
        formati = sorted(((nome, self.c(f"registrazioni_in_{chiave}")) for chiave, nome in (("mp3", "MP3"), ("opus", "Opus"), ("aac", "AAC"), ("flac", "FLAC"), ("wav", "WAV"))),
            key=lambda voce: -voce[1])
        if any(quante for _nome, quante in formati):
            # Traduttori: formati e' un elenco come MP3 12, Opus 3.
            righe.append(_("Per formato: {formati}.").format(formati=", ".join(f"{nome} {quante}" for nome, quante in formati if quante)))
        if "registrazione_piu_lunga" in r:
            righe.append(_("La registrazione più lunga: {durata}, di {cosa}, {quando}.").format(durata=durata(r["registrazione_piu_lunga"]["valore"]),
                cosa=r["registrazione_piu_lunga"].get("cosa", ""), quando=data_e_ora(r["registrazione_piu_lunga"]["quando"])))
        if "registrazione_piu_pesante" in r:
            righe.append(_("La registrazione più pesante: {peso}, di {cosa}, {quando}.").format(peso=_peso(r["registrazione_piu_pesante"]["valore"]),
                cosa=r["registrazione_piu_pesante"].get("cosa", ""), quando=data_e_ora(r["registrazione_piu_pesante"]["quando"])))
        righe.append(_("In pausa: {pause}; interrotte dal flusso: {interrotte}; eliminate: {eliminate}.").format(pause=_volte(self.c("registrazioni_in_pausa")),
            interrotte=self.c("registrazioni_interrotte"), eliminate=self.c("registrazioni_eliminate")))
        return righe

    def la_ricerca(self):
        ricerche = self.c("ricerche_nel_ramo") + self.c("ricerche_ovunque")
        risultati = self.c("risultati")
        finite = self.e("ricerca_finita")
        righe = [_("Ricerche: {n}; nel ramo {nel_ramo}, in tutto MeTeOra {ovunque}.").format(n=ricerche, nel_ramo=self.c("ricerche_nel_ramo"),
            ovunque=self.c("ricerche_ovunque"))]
        riga = _("Risultati trovati dalle ricerche finite: {n}").format(n=risultati)
        if finite:
            riga += _(", in media {n} per ricerca").format(n=round(risultati / finite))
        righe.append(riga + ".")
        righe.append(_("Ricerche senza risultati: {senza}; fermate prima della fine: {fermate}.").format(senza=self.c("ricerche_senza_risultati"),
            fermate=self.e("ricerca_fermata")))
        righe.append(_("Altri risultati mostrati: {altri}; risultati salvati come playlist: {salvati}.").format(altri=self.e("altri_risultati"),
            salvati=self.c("playlist_dalla_ricerca")))
        # Traduttori: dove si cerca, nella riga «Ricerche nella console, contando anche Invio: ...».
        for dove, chiave in ((_("nella console"), "in_console"), (_("nella finestra dei marcatori"), "nei_marcatori"), (_("nelle statistiche"), "nelle_statistiche")):
            # Traduttori: dove è «nella console», «nella finestra dei marcatori» o «nelle statistiche»; gli altri sono numeri di ricerche.
            righe.append(_("Ricerche {dove}, contando anche Invio: trovate {trovate}, ripartite dall'inizio {ripartite}, non trovate {non_trovate}.").format(
                dove=dove, trovate=self.e("trovato_" + chiave), ripartite=self.e("ripartito_" + chiave), non_trovate=self.e("non_trovato_" + chiave)))
        return righe

    # 15.

    def file_e_tag(self):
        return [
            _("File rinominati: {n}.").format(n=self.e("file_rinominato")),
            _("Mandati nel cestino: {file} e {cartelle}.").format(file=plurale(self.c("file_nel_cestino"), "{n} file", "{n} file"),
                cartelle=plurale(self.c("cartelle_nel_cestino"), "{n} cartella", "{n} cartelle")),
            _("Tag letti con F11: {letti}; dettagli di cartelle, unità e playlist: {dettagli}.").format(letti=self.e("tag_letti"), dettagli=self.e("dettagli")),
            _("Tag cambiati: {volte}, su {file}; tag cancellati: {cancellati}.").format(volte=_volte(self.e("tag_cambiato")),
                file=plurale(self.c("file_dei_tag_cambiati"), "{n} file", "{n} file"), cancellati=self.e("tag_cancellato")),
        ]

    # 16.

    def il_video(self):
        video = sum(int(v.get("avvii", 0)) for e, v in self.d["formati"].items() if famiglia(f"x{e}") == "video")
        return [
            _("Video avviati: {n}.").format(n=video),
            _("Immagine accesa con Maiuscolo e F1 e spenta con Ctrl e F1: accesa {accesa}, spenta {spenta}.").format(accesa=self.e("video_acceso"),
                spenta=self.e("video_spento")),
            _("Schermo intero: {volte}, per {durata}.").format(volte=_volte(self.e("schermo_intero")), durata=durata(self.t("schermo_intero"))),
            _("Finestra del video nascosta: {n}.").format(n=self.e("video_nascosto")),
            _("Tracce audio cambiate: {tracce}; rapporto dell'immagine cambiato: {rapporto}.").format(tracce=self.e("traccia_audio"), rapporto=self.e("rapporto")),
            _("Sottotitoli accesi: {accesi}; spenti: {spenti}.").format(accesi=self.e("sottotitoli_accesi"), spenti=self.e("sottotitoli_spenti")),
            _("Righe di sottotitoli e karaoke lette: {n}.").format(n=self.c("righe_dei_sottotitoli")),
            # La console letta da sola (3.7.0) e i capitoli detti suonando (3.8.0).
            _("Righe della console lette da sole: {righe}; capitoli nuovi detti suonando: {capitoli}.").format(righe=self.c("righe_lette"),
                capitoli=self.c("capitoli_annunciati")),
            _("Di queste, lette dalle immagini con il riconoscimento dei caratteri: {n}.").format(n=self.c("righe_riconosciute")),
            _("Di queste, del karaoke: {n}.").format(n=self.c("righe_del_karaoke")),
            _("Passate in anticipo degli impressi: avviate {avviate}, finite {finite}.").format(avviate=self.e("passata_avviata"), finite=self.e("passata_finita")),
        ]

    # 17.

    def descrizione_del_tasto(self, nome):
        comando = self.comandi_dei_tasti.get(nome)
        if comando in DESCRIZIONI_DEI_COMANDI:
            return DESCRIZIONI_DEI_COMANDI[comando]
        if nome in DESCRIZIONI_DEI_TASTI:
            return DESCRIZIONI_DEI_TASTI[nome]
        if nome.isdigit():
            return _("una delle prime dieci playlist")
        # I nomi dei tasti sono chiavi del file, in italiano.
        if nome.startswith("Maiuscolo con ") and nome.removeprefix("Maiuscolo con ").isdigit():
            return _("uno dei primi dieci marker")
        return ""

    def la_tastiera(self):
        tasti = self.d["tasti"]
        totale = int(sum(tasti.values()))
        ore = self.t("aperto") / 3600
        riga = _("Tasti premuti: {n}").format(n=totale)
        # Senza tasti premuti, il conto per ora non si dice (1.104.0).
        if ore >= 0.1 and totale:
            riga += _(", cioè {n} per ogni ora di MeTeOra aperto").format(n=round(totale / ore))
        righe = [riga + "."]
        frecce = {k: v for k, v in tasti.items() if k.startswith("Freccia ") and v}
        if frecce:
            per_freccia = "; ".join(f"{k[0].lower()}{k[1:]} {int(v)}" for k, v in sorted(frecce.items(), key=lambda kv: -kv[1]))
            # Traduttori: n è quante frecce in tutto; frecce le frecce una per una, come «freccia giù 3; freccia su 1».
            righe.append(_("Frecce: {n}; {frecce}.").format(n=int(sum(frecce.values())), frecce=per_freccia))

        def scrivi(nome, quanti):
            descrizione = self.descrizione_del_tasto(nome)
            return f"{nome}{', ' + descrizione if descrizione else ''}: {int(quanti)}."

        # Nella classifica e nei piu' frequenti solo le voci diverse da zero,
        # che un file toccato a mano puo' avere (1.104.0).
        premuti = [(k, v) for k, v in tasti.items() if v]
        righe += self.classifica(_("I {posti} tasti più premuti").format(posti=POSTI), sorted(premuti, key=lambda kv: (-kv[1], kv[0])), scrivi)
        senza = {k: v for k, v in self.d["senza_comando"].items() if v}
        riga = _("Tasti senza comando: {n}").format(n=int(sum(senza.values())))
        if senza:
            nome, quanti = max(senza.items(), key=lambda kv: (kv[1], kv[0]))
            # Traduttori: nome è il nome di un tasto, come «U accentata»; volte come «3 volte».
            riga += _("; il più frequente: {nome}, {volte}").format(nome=nome, volte=_volte(int(quanti)))
        righe.append(riga + ".")
        righe += [
            _("Rami aperti: {aperti}; chiusi: {chiusi}.").format(aperti=self.e("ramo_aperto"), chiusi=self.e("ramo_chiuso")),
            _("F8, al brano che suona: {f8}; inseguimento acceso con Maiuscolo e F8: {acceso}, spento con Ctrl e F8: {spento}.").format(f8=self.e("vai_al_brano"),
                acceso=self.e("insegui_acceso"), spento=self.e("insegui_spento")),
            # Traduttori: ramo_aperto e ramo_chiuso vanno con Maiuscolo e Ctrl, plancia_aperta e plancia_chiusa con Alt e Ctrl e Alt.
            _("Maiuscolo e Ctrl con F9 sul ramo, aperto e chiuso: {ramo_aperto} e {ramo_chiuso}; "
                "Alt e Ctrl e Alt con F9 su tutta la plancia: {plancia_aperta} e {plancia_chiusa}.").format(ramo_aperto=self.e("apri_tutto"),
                ramo_chiuso=self.e("chiudi_tutto"), plancia_aperta=self.e("plancia_aperta"), plancia_chiusa=self.e("chiudi_la_plancia")),
            _("Backspace, risali: {risali}; Maiuscolo con Backspace, all'antenato: {antenato}.").format(risali=self.e("risali"), antenato=self.e("risali_all_antenato")),
            _("Menu aperti: {n}.").format(n=self.e("menu")),
            _("Tasti rapidi spenti con Ctrl e F12: {n}.").format(n=self.e("tasti_spenti")),
            _("Clic sulla barra dei comandi: {n}.").format(n=self.c("clic_sulla_barra")),
        ]
        return righe

    # 18.

    def la_console(self):
        righe = [
            _("Righe scritte nella console: {scritte}; riscritte al loro posto, come quelle del volume: {riscritte}.").format(scritte=self.c("righe_della_console"),
                riscritte=self.c("righe_riscritte")),
            _("Alla plancia con F5: {plancia}; alla console con F6: {console}; al cruscotto con F7: {cruscotto}.").format(plancia=self.e("plancia"),
                console=self.e("console"), cruscotto=self.e("cruscotto")),
            _("Manuale con F1: {manuale}; novità con F2: {novita}; crediti con F3: {crediti}; guida rapida con F12: {guida}.").format(manuale=self.e("manuale"),
                novita=self.e("changelog"), crediti=self.e("crediti"), guida=self.e("elenco_dei_tasti")),
            _("Console salvata: {n}.").format(n=self.e("console_salvata")),
            _("Statistiche aperte: {n}.").format(n=self.e("statistiche")),
        ]
        totale = int(sum(self.eventi.values()))
        riga = _("Effetti sonori, contati anche con il volume degli effetti a zero: {n}").format(n=totale)
        # Il piu' suonato solo fra gli eventi accaduti (1.104.0).
        accaduti = {k: v for k, v in self.eventi.items() if v}
        if accaduti:
            evento, quanti = max(accaduti.items(), key=lambda kv: (kv[1], kv[0]))
            riga += _("; il più suonato: {evento}, {volte}").format(evento=NOMI_DEGLI_EVENTI.get(evento, evento.replace("_", " ")), volte=_volte(int(quanti)))
        righe.append(riga + ".")
        righe.append(_("Domande, con il loro suono: {domande}; annullate: {annullate}.").format(domande=self.e("domanda"), annullate=self.e("annullamento")))
        return righe

    # 19.

    def le_impostazioni(self):
        # La piu' usata solo fra le voci aperte almeno una volta (1.104.0).
        voci = {k: v for k, v in self.d["impostazioni"].items() if v}
        riga = _("Voci delle impostazioni aperte con Invio: {n}").format(n=int(sum(voci.values())))
        if voci:
            chiave, quante = max(voci.items(), key=lambda kv: (kv[1], kv[0]))
            # Traduttori: voce è il nome di una voce delle impostazioni, come «Volume degli effetti»; volte come «3 volte».
            riga += _("; la più usata: {voce}, {volte}").format(voce=self.nomi_delle_impostazioni.get(chiave, chiave), volte=_volte(int(quante)))
        return [
            _("Finestra delle impostazioni aperta: {volte}; impostazioni cambiate: {cambiate}.").format(volte=_volte(self.e("impostazioni")),
                cambiate=self.e("impostazione_cambiata")),
            riga + ".",
            _("Scheda audio cambiata: {volte}.").format(volte=_volte(self.e("scheda_audio"))),
            self._riga_delle_uscite(),
            _("Percorsi di rete aggiunti: {aggiunti}; tolti: {tolti}; ricerche dei computer della rete: {ricerche}.").format(aggiunti=self.e("percorso_aggiunto"),
                tolti=self.e("percorso_tolto"), ricerche=self.c("ricerche_della_rete")),
            _("Banco dei suoni MIDI scelto: {volte}; scaricamenti avviati: {avviati}, finiti: {finiti}.").format(volte=_volte(self.c("banchi_scelti")),
                avviati=self.e("scaricamento_avviato"), finiti=self.e("scaricamento_finito")),
            _("Aggiornamenti proposti: {n}.").format(n=self.e("aggiornamento")),
            # I componenti aggiuntivi (3.1.0) e la lingua (3.0.0), contati dalla 3.3.0.
            _("Componenti aggiuntivi installati: {installati}; tolti: {tolti}. Lingua cambiata: {lingua}.").format(installati=self.c("componenti_installati"),
                tolti=self.c("componenti_tolti"), lingua=_volte(self.c("lingua_cambiata"))),
            # Traduttori: Dona per questo progetto è il nome di una voce del menu; volte come «2 volte».
            _("Dona per questo progetto aperto: {volte}.").format(volte=_volte(self.e("donazione"))),
            # Traduttori: Entra al PUB e Chiedi aiuto al PUB sono voci del menu; entra e aiuto come «2 volte»; pronte e registri sono numeri.
            _("Entra al PUB aperto: {entra}; Chiedi aiuto al PUB: {aiuto}; mail pronte: {pronte}, con i registri allegati: {registri}.").format(
                entra=_volte(self.e("pub_entra")), aiuto=_volte(self.e("pub_aiuto")), pronte=self.c("mail_al_pub_pronte"), registri=self.c("registri_al_pub")),
        ]

    # 20.

    def la_salute(self):
        errori = sorted(((e, int(v.get("errori", 0))) for e, v in self.d["formati"].items() if v.get("errori")), key=lambda ev: (-ev[1], ev[0]))
        riga = _("Brani non suonati per un errore: {n}").format(n=self.c("errori_di_riproduzione"))
        if errori:
            riga += _("; per formato: {formati}").format(formati=", ".join(f"{estensione_da_dire(e)} {n}" for e, n in errori))
        righe = [riga + "."]
        righe += [
            _("Messaggi d'errore nella console: {n}.").format(n=self.e("errore")),
            _("Problemi interni scritti nella console: {n}.").format(n=self.c("problemi_interni")),
            _("Avvii dopo un errore grave, con il resoconto da mandare: {n}.").format(n=self.c("crash")),
            _("Chiusure non regolari: {n}.").format(n=self.c("chiusure_non_regolari")),
            _("Salvataggi non riusciti: {n}.").format(n=self.c("salvataggi_non_riusciti")),
            _("Cartelle di rete che non hanno risposto nella plancia: {n}.").format(n=self.c("rete_muta")),
            self.riga_delle_pulizie(),
            # Dalla 1.112.0: Riconosci questo disco e la Sentinella che rende contesa una lettera, contati dai loro eventi.
            _("Dischi riconosciuti a mano: {riconosciuti}; lettere rese contese dalla Sentinella, a MeTeOra aperto: {contese}.").format(
                riconosciuti=self.e("disco_riconosciuto"), contese=self.e("disco_diverso")),
            _("Attese dei SID, dei MIDI e delle console oltre un secondo e mezzo, dopo un salto: {n}.").format(n=self.c("attese_lunghe")),
            _("Comandi che lì non valgono: {non_validi}; niente da suonare: {niente}.").format(non_validi=self.e("non_disponibile"), niente=self.e("niente_da_suonare")),
        ]
        return righe

    def riga_delle_pulizie(self):
        """Le pulizie all'avvio, quante in tutto e quante non riuscite, e
        cio' che hanno tolto, solo le voci diverse da zero, con tolto
        accordato a cio' che segue (1.104.0). pulizie conta quelle riuscite,
        pulizie_non_riuscite quelle finite con un errore. In fondo le unita'
        saltate perche' non rispondevano e, dalla 1.112.0, perche' usate da
        dischi diversi o perche' il disco che rispondeva non si riconosceva."""
        riuscite, non_riuscite = self.c("pulizie"), self.c("pulizie_non_riuscite")
        totale = riuscite + non_riuscite
        if not totale:
            return _("Pulizie all'avvio: nessuna.")
        riga = _("Pulizie all'avvio: {n}").format(n=totale)
        if non_riuscite == totale:
            # Traduttori: dopo «Pulizie all'avvio: 1», la sola pulizia che c'è stata.
            riga += _(", non riuscita per un errore") if totale == 1 else _(", tutte non riuscite per un errore")
        elif non_riuscite:
            # Traduttori: dopo «Pulizie all'avvio: 4», quante di quelle pulizie non sono riuscite.
            riga += ngettext(", di cui {n} non riuscita per un errore", ", di cui {n} non riuscite per un errore", non_riuscite).format(n=non_riuscite)
        tolti = [(self.c(conto), da_sola, in_elenco, femminile) for conto, da_sola, in_elenco, femminile in TOLTI_DALLA_PULIZIA if self.c(conto)]
        if len(tolti) == 1:
            n, da_sola, _in_elenco, _femminile = tolti[0]
            riga += da_sola(n)
        elif tolti:
            voci = ", ".join(in_elenco(n) for n, _da_sola, in_elenco, _f in tolti)
            # Femminile solo se lo sono tutte le voci.
            if all(f for *_resto, f in tolti):
                # Traduttori: voci sono due o più voci femminili, come «3 schede doppie dello schedario, 2 voci dei marker».
                riga += _("; tolte {voci}").format(voci=voci)
            else:
                # Traduttori: voci sono due o più voci, come «4 file dallo schedario, 2 voci dei marker».
                riga += _("; tolti {voci}").format(voci=voci)
        elif riuscite:
            riga += _("; niente da togliere")
        perche = []
        if self.c("pulizia_radici_saltate"):
            # Traduttori: da qui, i motivi per cui la pulizia ha saltato delle unità, con quante: «unità saltate perché non rispondevano: 2».
            perche.append(_("non rispondevano: {n}").format(n=self.c("pulizia_radici_saltate")))
        if self.c("pulizia_dischi_diversi"):
            perche.append(_("usate da dischi diversi: {n}").format(n=self.c("pulizia_dischi_diversi")))
        if self.c("pulizia_dischi_non_riconosciuti"):
            perche.append(_("il disco che rispondeva non si riconosceva: {n}").format(n=self.c("pulizia_dischi_non_riconosciuti")))
        if perche:
            # Traduttori: motivo è come «non rispondevano: 2»; gli altri motivi seguono con «; perché».
            riga += _("; unità saltate perché {motivo}").format(motivo=perche[0]) + "".join(_("; perché {motivo}").format(motivo=m) for m in perche[1:])
        return riga + "."

    # 21.

    def la_libreria(self):
        return list(self.libreria) if self.libreria else [_("La libreria di adesso non si è potuta contare.")]

    # 22.

    def curiosita(self):
        righe = []
        dal = (_leggi_data(self.d["dal"]) or self.oggi).date()
        giorni = max(1, (self.oggi.date() - dal).days + 1)
        durata_della_libreria = self.numeri_della_libreria.get("durata")
        if self.play and durata_della_libreria:
            al_giorno = self.play / giorni
            tempo = anni_e_mesi(durata_della_libreria / al_giorno)
            if giorni == 1:
                righe.append(_("Al ritmo di oggi, per ascoltare tutta la libreria servirebbero {tempo}.").format(tempo=tempo))
            else:
                # Traduttori: giorni è sempre almeno 2, perché con un giorno solo la frase è quella di oggi; tempo è come «9 anni e 7 mesi».
                righe.append(ngettext("Al ritmo di questi {giorni} giorni, per ascoltare tutta la libreria servirebbero {tempo}.",
                    "Al ritmo di questi {giorni} giorni, per ascoltare tutta la libreria servirebbero {tempo}.", giorni).format(giorni=giorni, tempo=tempo))
        if self.play >= 74 * 60:
            cassette = round(self.play / (90 * 60))
            # Traduttori: cd e cassette sono numeri interi; la forma la sceglie il numero delle cassette.
            righe.append(ngettext("La riproduzione equivale a {cd} CD da 74 minuti, o {cassette} cassetta da 90.",
                "La riproduzione equivale a {cd} CD da 74 minuti, o {cassette} cassette da 90.", cassette).format(cd=round(self.play / (74 * 60)), cassette=cassette))
        if self.t("pausa") and self.play:
            # Traduttori: ore è un numero con i decimali, come 1.5.
            righe.append(_("Per ogni ora in pausa, {ore} ore in riproduzione.").format(ore=numero_decimale(self.play / self.t("pausa"))))
        avviati = self.avviati()
        if avviati >= 10:
            righe.append(_("Ogni 100 brani avviati, {lasciati} lasciati prima della fine, {subito} nei primi {secondi} secondi.").format(
                lasciati=round(100 * self.c("lasciati") / avviati), subito=round(100 * self.c("lasciati_subito") / avviati), secondi=int(SUBITO)))
        if self.c("secondi_avanti"):
            righe.append(_("Se i salti in avanti con E fossero un brano, durerebbe {durata}.").format(durata=durata(self.c("secondi_avanti"))))
        sid = sum(v.get("secondi", 0) for e, v in self.d["formati"].items() if e == ".sid")
        sid_della_libreria = self.numeri_della_libreria.get("sid")
        if sid and sid_della_libreria:
            righe.append(_("I SID ascoltati sono {percentuale} dei {durata} di SID della libreria.").format(percentuale=percentuale(sid, sid_della_libreria),
                durata=durata(sid_della_libreria)))
        return righe

    # 23.

    def tutti_gli_eventi(self):
        # Un evento a zero, da un file toccato a mano, non e' accaduto (1.104.0).
        eventi = sorted(((evento, quante) for evento, quante in self.eventi.items() if quante), key=lambda kv: (-kv[1], kv[0]))
        righe = [_("Eventi diversi accaduti: {n} su {totale} che MeTeOra conosce.").format(n=len(eventi), totale=len(NOMI_DEGLI_EVENTI))]
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
        c["estensioni"][formati.estensione(percorso) or SENZA_ESTENSIONE] += 1
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
        righe.append(_("Schedario: ancora vuoto."))
        return righe
    righe.append(_("Schedario: {file}, {dimensione}.").format(file=plurale(totale, "{n} file conosciuto", "{n} file conosciuti"), dimensione=dimensione(c["byte"])))
    righe.append(_("Durata di tutta la libreria: {durata}.").format(durata=durata(c["durata"])))
    ordine = list(FAMIGLIE)
    # Solo le famiglie che hanno dei file: con lo schedario non vuoto, almeno
    # una c'e' (1.104.0).
    famiglie = sorted((kv for kv in c["famiglie"].items() if kv[1]["file"]), key=lambda kv: (-kv[1]["file"], ordine.index(kv[0])))
    per_numero = "; ".join(f"{NOMI_BREVI_DELLE_FAMIGLIE[k]} {v['file']}, {percentuale(v['file'], totale)}" for k, v in famiglie)
    righe.append(_("Per numero di file: {famiglie}.").format(famiglie=per_numero))
    con_durata = sorted((kv for kv in c["famiglie"].items() if kv[1]["durata"]), key=lambda kv: -kv[1]["durata"])
    if con_durata:
        per_durata = "; ".join(f"{NOMI_BREVI_DELLE_FAMIGLIE[k]} {durata(v['durata'])}, {percentuale(v['durata'], c['durata'])}" for k, v in con_durata)
        righe.append(_("Per durata: {famiglie}.").format(famiglie=per_durata))
    con_spazio = sorted((kv for kv in c["famiglie"].items() if kv[1]["byte"]), key=lambda kv: -kv[1]["byte"])
    if con_spazio:
        per_spazio = "; ".join(f"{NOMI_BREVI_DELLE_FAMIGLIE[k]} {dimensione(v['byte'])}" for k, v in con_spazio)
        righe.append(_("Per spazio: {famiglie}.").format(famiglie=per_spazio))
    if c["file_sid"]:
        righe.append(_("Sottobrani dei SID: {n}, in {file}.").format(n=c["sottobrani_sid"], file=plurale(c["file_sid"], "{n} file", "{n} file")))
    presenti = [e for e in c["estensioni"] if e in formati.TUTTI]
    piu = ", ".join(f"{estensione_da_dire(e)} {n}" for e, n in c["estensioni"].most_common(5))
    righe.append(_("Formati presenti: {n} dei {totale}; i più numerosi: {numerosi}.").format(n=len(presenti), totale=len(formati.TUTTI), numerosi=piu))
    per_unita = []
    for unita, n in c["unita"].most_common():
        quanti = plurale(n, "{n} file", "{n} file")
        per_unita.append(f"{unita} {quanti}, {percentuale(n, totale)}")
    righe.append(_("Per unità: {unita}.").format(unita="; ".join(per_unita)))
    if c["lungo"]:
        righe.append(_("Il file più lungo: {nome}, {durata}.").format(nome=_nome(c["lungo"][1]), durata=durata(c["lungo"][0])))
    if c["corto"]:
        righe.append(_("Il file più corto: {nome}, {durata}.").format(nome=_nome(c["corto"][1]), durata=durata(c["corto"][0])))
    # Dai tag, solo cio' che c'e'; senza niente, una frase che lo dice (1.104.0).
    parti = []
    if c["autori"]:
        parti.append(plurale(len(c["autori"]), "{n} autore", "{n} autori"))
    if c["album"]:
        parti.append(plurale(len(c["album"]), "{n} album", "{n} album"))
    if c["generi"]:
        parti.append(plurale(len(c["generi"]), "{n} genere", "{n} generi"))
    testo = ", ".join(parti)
    if c["anni"]:
        anni = _("anni dal {primo} al {ultimo}").format(primo=min(c["anni"]), ultimo=max(c["anni"]))
        testo = f"{testo}; {anni}" if testo else anni
    if testo:
        # Traduttori: tag è come «1 autore, 1 album, 1 genere; anni dal 1985 al 1991».
        righe.append(_("Dai tag: {tag}.").format(tag=testo))
    else:
        righe.append(_("Dai tag: nessun autore, album, genere o anno."))
    if c["autori"]:
        autore, quanti = max(c["autori"].items(), key=lambda kv: (kv[1], kv[0]))
        righe.append(_("L'autore con più file: {autore}, {n}.").format(autore=autore, n=quanti))
    if c["decenni"]:
        decennio, quanti = max(c["decenni"].items(), key=lambda kv: (kv[1], kv[0]))
        # Traduttori: decennio è come «anni '80» o «anni 2020»; n è quanti file.
        righe.append(_("Il decennio con più file: gli {decennio}, {n}.").format(decennio=decennio, n=quanti))
    righe.append(_("File di cui la durata non si sa: {n}.").format(n=c["senza_durata"]))
    if c["non_credibili"]:
        righe.append(_("Durate non credibili, oltre una settimana, lasciate fuori dai conti: {file}.").format(file=plurale(c["non_credibili"], "{n} file", "{n} file")))
    return righe
