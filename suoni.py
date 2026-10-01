# MeTeOra, gli effetti sonori: un suono per ogni azione, con Acusticator.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.51.0 i suoni delle impostazioni, della console salvata, della finestra dei marcatori, della sua ricerca e della scheda audio.

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
    "playlist_da_cartella": "jingle_livello_superato",
    "playlist_eliminata": "cancellato",
    "playlist_rinominata": "written_ok",
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
    "non_disponibile": "rifiuto",
    "errore": "errore_secco",
    # Un problema interno di MeTeOra, non un errore di chi lo usa.
    "problema": "notifica",
    "niente_da_suonare": "arpeggio_pensoso",
    "loop_a_messo": "notifica_tramite_interfaccia_utente_2",
    "loop_b_messo": "notifica_tramite_interfaccia_utente_3",
    "loop_b_tolto": "colpo_d_impatto_1",
    "loop_tolto": "colpo_d_impatto_2",
    "loop_non_qui": "colpo_d_impatto_5",
    "fuori_dal_loop": "avviso_di_sistema",
    "ritorno_al_punto_a": "scintillio_di_ghiaccio",
    "nessun_altro_brano": "il_gioco_spunta_a_met",
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
