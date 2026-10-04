# MeTeOra, gli effetti sonori: un suono per ogni azione, con Acusticator.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.51.0 i suoni delle impostazioni, della console salvata, della finestra dei marcatori, della sua ricerca e della scheda audio. Nella 1.55.0 quelli di velocita', tono, equalizzatore e dissolvenza. Nella 1.58.0 i suoni al volo dell'equalizzatore, e il loop con i soffi rimasti liberi. Nella 1.59.0 l'acceso e lo spento della riproduzione casuale. Nella 1.63.0 i suoni del video. Nella 1.64.0 quelli di Questa rete. Nella 1.65.0 quelli dello scaricamento. Nella 1.66.36 l'annullamento, il ramo aggiornato e il video nascosto, e la playlist creata con dei brani ha un suono solo. Nella 1.67.0 il file rinominato. Nella 1.69.0 i suoni dei tag. Nella 1.75.0 il suono dell'invito a offrire un caffe'.

"""La mappa degli eventi di MeTeOra sui preset della collezione di GBUtils.

Ogni evento ha un preset suo: mai lo stesso suono per due eventi diversi.
Sono preset della collezione; quelli fatti apposta per MeTeOra hanno il
prefisso meteora_ e stanno anche loro nella collezione, dove ogni suono
originale va appena nasce.
"""

import time

EVENTI = {
    "avvio": "partenza",
    "uscita": "terminata",
    # L'invito a offrire un caffe' (1.75.0): lo stesso di Tornello e Terminal
    # Beast, firmato anche da MeTeOra nella collezione (GBUtils V192).
    "donazione": "donazione",
    "plancia": "spostamento_f5",
    "console": "spostamento_f6",
    "cruscotto": "spostamento_f7",
    "manuale": "apertura",
    "changelog": "lista",
    "crediti": "mostra",
    "play": "Rapida_salita-sin_des",
    "pausa": "sys_tick_basso",
    "ripresa": "sys_tick_alto",
    "stop": "annullato",
    "da_capo": "timbratura",
    "successivo": "successivo",
    "precedente": "menu_triplicato_su_2",
    "casuale": "mazzo_mescolato",
    # Maiuscolo con N, la riproduzione casuale (1.59.0): due avvisi del loop
    # di prima, quello che sale per accenderla e quello che scende per
    # spegnerla (Gabriele, issue 17).
    "casuale_acceso": "notifica_tramite_interfaccia_utente_3",
    "casuale_spento": "notifica_tramite_interfaccia_utente_2",
    # Il video, tappa 7 (1.63.0): suoni originali, nella collezione di GBUtils V186.
    "video_acceso": "meteora_video_acceso",
    "video_spento": "meteora_video_spento",
    "sottotitoli_accesi": "meteora_sottotitoli_accesi",
    "sottotitoli_spenti": "meteora_sottotitoli_spenti",
    "traccia_audio": "meteora_traccia_audio",
    "schermo_intero": "meteora_schermo_intero",
    "schermo_in_finestra": "meteora_schermo_in_finestra",
    "rapporto": "meteora_rapporto",
    # Esc nella finestra del video la nasconde per il brano in corso (1.66.36).
    "video_nascosto": "meteora_video_nascosto",
    # Questa rete (1.64.0): la ricerca dei computer usa i suoni della ricerca.
    "percorso_aggiunto": "meteora_percorso_aggiunto",
    "percorso_tolto": "meteora_percorso_tolto",
    # I MIDI (1.65.0): la ricerca dei banchi usa i suoni della ricerca.
    "scaricamento_avviato": "meteora_scaricamento_avviato",
    "scaricamento_finito": "meteora_scaricamento_finito",
    "brano_seguente_da_solo": "carta_giocata",
    "fine_playlist": "carillon_dolce",
    "avanti": "laser_da_gioco_2",
    "indietro": "Laser_destra_sinistra",
    "vai_a_tempo": "salto",
    "passo_di_salto": "controllo_ok",
    "passo_del_volume": "convalida0",
    "volume_su": "salita_ideale",
    "volume_giu": "discesa_ideale",
    "volume_al_limite": "Coccodrillino",
    "muto_acceso": "colpo_d_impatto_3",
    "muto_spento": "colpo_d_impatto_7",
    "menu": "il_gioco_alto",
    "nuova_playlist": "moneta_raccolta",
    # Una playlist nata gia' con dei brani: da una cartella, dalla selezione,
    # dai Risultati o dal sottomenu Aggiungi alla playlist (1.66.36).
    "playlist_creata": "jingle_livello_superato",
    "playlist_eliminata": "cancellato",
    "playlist_rinominata": "written_ok",
    # Rinomina file, 1.67.0: il file cambia nome sul disco.
    "file_rinominato": "meteora_file_rinominato",
    # I tag, 1.69.0: letti con F11, scritti e cancellati dal sottomenu Tag.
    "tag_letti": "meteora_tag_letti",
    "tag_cambiato": "meteora_tag_cambiato",
    "tag_cancellato": "meteora_tag_cancellato",
    "brano_aggiunto": "aggiunta_giocatore",
    "preferito_aggiunto": "perfect_match",
    "filtro_messo": "processo_quartina_1",
    "ricerca_avviata": "caricamento_in_corso",
    "ricerca_finita": "jingle_scoperta",
    "ricerca_fermata": "passaggio_veloce",
    "altri_risultati": "Digitazione",
    "filtro_tolto": "processo_quartina_10",
    "gia_nei_preferiti": "doppio_tic_conferma",
    "brano_tolto": "espelli",
    "cestino": "morto",
    "brano_spostato": "scudisciata",
    "saltato_acceso": "salto_del_gioco_1",
    "saltato_spento": "salto_del_gioco_10",
    # I rami della plancia aperti e chiusi con le frecce.
    "ramo_aperto": "carta_pescata",
    "ramo_chiuso": "meteora_ramo_chiuso",
    "file_aperto": "carta_girata",
    "vai_al_brano": "grosse_biglie",
    "playlist_precedente": "menu_triplicato_su_6",
    "playlist_successiva": "menu_tripletta_in_basso_9",
    "playlist_numero": "notifica_tramite_interfaccia_utente_4",
    "ripresa_all_avvio": "notifica_tramite_interfaccia_utente_5",
    # Lo stesso laser: sale quando aggancia, scende quando sgancia.
    "insegui_acceso": "meteora_aggancio",
    "insegui_spento": "laser_da_gioco_3",
    "elenco_dei_tasti": "rimbalzo_stereo",
    "trovato_in_console": "conferma",
    "ripartito_in_console": "tripletta_su_giu_rapidissima",
    "non_trovato_in_console": "rifiutato",
    "chiudi_tutto": "menu_tripletta_gi_7",
    # I marker, con i suoni nati per loro nella collezione (GBUtils V175).
    "marker_messo": "meteora_marker_messo",
    "marker_rinominato": "meteora_marker_rinominato",
    "marker_indietro": "meteora_marker_indietro",
    "marker_avanti": "meteora_marker_avanti",
    "marker_tolti_prima": "meteora_marker_tolti_prima",
    "marker_tolti_dopo": "meteora_marker_tolti_dopo",
    "marker_tolti_tutti": "meteora_marker_tolti_tutti",
    "marker_eliminato": "meteora_marker_eliminato",
    # Backspace e Maiuscolo con Backspace nella plancia.
    "risali": "menu_triplicato_su_4",
    "risali_all_antenato": "meteora_risali_all_antenato",
    "apri_tutto": "meteora_apri_tutto",
    # La finestra delle impostazioni e quella dei marcatori (1.51.0), con i
    # suoni nati per loro nella collezione. Cancella tutto della finestra dei
    # marcatori svuota l'archivio intero: non e' marker_tolti_tutti, che
    # toglie i marker di un brano solo.
    "impostazioni": "meteora_impostazioni",
    "impostazione_cambiata": "meteora_impostazione_cambiata",
    "console_salvata": "meteora_console_salvata",
    "scheda_audio": "meteora_scheda_audio",
    "marcatori": "meteora_marcatori",
    "marcatori_esportati": "meteora_marcatori_esportati",
    "marcatori_importati": "meteora_marcatori_importati",
    "marcatori_cancellati": "meteora_marcatori_cancellati",
    # La barra rovesciata nella finestra dei marcatori: una famiglia di tre
    # esiti, diversa da quella della ricerca nella console. Trovato e non
    # trovato cominciano con la stessa scorsa di tre note; ripartito ha la
    # stessa chiusa di trovato, preceduta da una scivolata che torna in cima.
    "trovato_nei_marcatori": "meteora_marcatori_trovato",
    "ripartito_nei_marcatori": "meteora_marcatori_ripartito",
    "non_trovato_nei_marcatori": "meteora_marcatori_non_trovato",
    "domanda": "campanellino",
    # Esc in un campo, o No a una domanda (tappa 9, 1.66.36): l'operazione non
    # si fa. Non e' lo stop, che ha il preset annullato.
    "annullamento": "meteora_annullamento",
    "ramo_aggiornato": "meteora_ramo_aggiornato",
    "non_disponibile": "rifiuto",
    "errore": "errore_secco",
    # Un problema interno di MeTeOra, non un errore di chi lo usa.
    "problema": "notifica",
    "niente_da_suonare": "arpeggio_pensoso",
    # Maiuscolo con X, a giro (1.58.0): punto A, punto B, loop tolto. I suoni
    # sono i soffi che fino alla 1.55.2 servivano a U, I e O, P.
    "loop_a_messo": "meteora_loop_a_messo",
    "loop_b_messo": "meteora_loop_b_messo",
    "loop_tolto": "meteora_loop_tolto",
    "loop_non_qui": "colpo_d_impatto_5",
    "fuori_dal_loop": "avviso_di_sistema",
    "ritorno_al_punto_a": "scintillio_di_ghiaccio",
    "nessun_altro_brano": "il_gioco_spunta_a_met",
    # Velocita', tono, equalizzatore e dissolvenza (1.55.0), con i suoni nati
    # per loro nella collezione. Ogni famiglia ha la sua onda: tic di onda
    # triangolare per la velocita', note di seno per il tono, soffi di rumore
    # rosa per l'equalizzatore, dente di sega sfumato per la dissolvenza. Su e
    # giu' sono specchiati, il ritorno al normale fa incontrare le loro note in
    # mezzo, e ai limiti si bussa due volte, col secondo colpo piu' piano.
    "velocita_su": "meteora_velocita_su",
    "velocita_giu": "meteora_velocita_giu",
    "velocita_normale": "meteora_velocita_normale",
    "velocita_al_limite": "meteora_velocita_al_limite",
    "tono_su": "meteora_tono_su",
    "tono_giu": "meteora_tono_giu",
    "tono_normale": "meteora_tono_normale",
    "tono_al_limite": "meteora_tono_al_limite",
    # U e I scelgono la banda e O e P ne cambiano il guadagno con i suoni fatti
    # al volo (banda e guadagno, qui sotto); ai limiti, la E accentata che la
    # azzera e Maiuscolo con la E accentata che le azzera tutte hanno i preset.
    "banda_al_limite": "meteora_banda_al_limite",
    "guadagno_al_limite": "meteora_guadagno_al_limite",
    "banda_azzerata": "meteora_banda_azzerata",
    "bande_azzerate": "meteora_bande_azzerate",
    "dissolvenza_accesa": "meteora_dissolvenza_accesa",
    "dissolvenza_spenta": "meteora_dissolvenza_spenta",
    "dissolvenza_durata": "meteora_dissolvenza_durata",
}


# Il beep dei livelli della plancia: sinusoide di 150 ms, attacco e rilascio
# di 25 ms, dal do 4 al primo livello e tre semitoni piu' su per ogni livello.
DO_4 = 261.6255653005986
DURATA_DEL_LIVELLO = 0.15
MORBIDEZZA_DEL_LIVELLO = 0.025


# Oltre questo livello l'altezza resta quella del do 8: piu' su il beep
# diventerebbe inudibile, e oltre i 22 kHz tornerebbe a scendere.
LIVELLO_MASSIMO = 17


def frequenza_del_livello(profondita):
    return DO_4 * 2 ** (3 * (min(profondita, LIVELLO_MASSIMO) - 1) / 12)


def livello(profondita, volume=0.5):
    """Suona il beep del livello profondita' della plancia, 1 per le voci
    principali. Non e' un preset della collezione: l'altezza cambia con il
    livello, e il suono si crea ogni volta con Acusticator."""
    if volume <= 0:
        return False
    from GBUtils import Acusticator

    morbido = MORBIDEZZA_DEL_LIVELLO / DURATA_DEL_LIVELLO * 100
    Acusticator([frequenza_del_livello(profondita), DURATA_DEL_LIVELLO, 0.0, volume], kind=1, adsr=[morbido, 0.0, 100.0, morbido])
    return True


# I suoni dell'equalizzatore, fatti al volo come il beep dei livelli (Gabriele,
# 2 ottobre 2026): un fa di riferimento, una pausa, e una seconda nota che
# dice a orecchio la banda scelta con U e I, dente di sega, sulla scala da do 3
# a si 3 dopo il fa 3, o il guadagno dato con O e P, onda triangolare, su tre
# ottave attorno al fa 4: un semitono e mezzo per ogni dB, da -12 a +12.
# Nella 1.58.4 O e P salgono di un'ottava, dal fa 3 al fa 4: a -12 dB la nota
# scendeva sotto i 62 Hz e si sentiva appena. E prendono un attacco e un
# rilascio del 5 per cento della nota, 2,5 e 4,5 ms: con l'inviluppo quasi
# nullo di U e I la triangolare di Acusticator comincia sul suo picco, e
# l'inizio e la fine delle note schioccavano (collaudo di Gabriele).
NOTE_DELLE_BANDE = ("c3", "d3", "e3", "f3", "g3", "a3", "b3")
FA_4 = 349.2282314330039
ADSR_DELL_EQUALIZZATORE = [0.002, 0.0, 100.0, 0.002]
ADSR_DEL_GUADAGNO = [5.0, 0.0, 100.0, 5.0]


def frequenza_del_guadagno(db):
    return FA_4 * 2 ** (1.5 * db / 12)


def banda(indice, volume=0.5):
    """Il suono della banda indice, da 0 (60 Hz) a 6 (12000 Hz)."""
    return _al_volo(["f3", 0.04, 0.0, volume, "p", 0.04, 0.0, 0.0, NOTE_DELLE_BANDE[indice], 0.08, 0.0, volume], 4, volume, ADSR_DELL_EQUALIZZATORE)


def guadagno(db, volume=0.5):
    """Il suono del guadagno di una banda, in dB."""
    return _al_volo(["f4", 0.05, 0.0, volume, "p", 0.04, 0.0, 0.0, frequenza_del_guadagno(db), 0.09, 0.0, volume], 3, volume, ADSR_DEL_GUADAGNO)


def _al_volo(score, kind, volume, adsr):
    if volume <= 0:
        return False
    from GBUtils import Acusticator

    _FINE_DELL_ULTIMO[0] = time.monotonic() + sum(score[1::4])
    Acusticator(score, kind=kind, adsr=adsr)
    return True


# Quando finisce l'ultimo effetto partito, e quanto dura ogni preset.
_FINE_DELL_ULTIMO = [0.0]
_DURATE = {}


def _durata(preset):
    if preset not in _DURATE:
        from GBUtils import Acusticator

        score, _kind, _adsr = Acusticator.preset(preset)
        _DURATE[preset] = sum(score[1::4]) if score else 0.0
    return _DURATE[preset]


def attesa():
    """Quanti secondi mancano alla fine dell'ultimo effetto partito: il beep
    dei livelli aspetta, per non sovrapporsi."""
    return max(0.0, _FINE_DELL_ULTIMO[0] - time.monotonic())


def suona(evento, volume=0.5, sync=False):
    """Suona il preset dell'evento. Il volume va da 0 a 1; a zero tace.
    Con sync aspetta la fine del suono."""
    if volume <= 0:
        return False
    from GBUtils import Acusticator

    _FINE_DELL_ULTIMO[0] = time.monotonic() + _durata(EVENTI[evento])
    return Acusticator.play(EVENTI[evento], sync=sync, volume=volume)
