# MeTeOra, gli effetti sonori: un suono per ogni azione, con Acusticator.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1.

"""La mappa degli eventi di MeTeOra sui preset della collezione di GBUtils.

Ogni evento ha un preset suo: mai lo stesso suono per due eventi diversi.
Per ora sono preset gia' presenti nella collezione; quelli fatti apposta,
con il prefisso meteora_, arriveranno quando Gabriele li chiedera'.
"""

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
    "filtro_tolto": "processo_quartina_10",
    "gia_nei_preferiti": "doppio_tic_conferma",
    "brano_tolto": "espelli",
    "cestino": "morto",
    "brano_spostato": "scudisciata",
    "saltato_acceso": "salto_del_gioco_1",
    "saltato_spento": "salto_del_gioco_10",
    "cartella_aperta": "carta_pescata",
    "file_aperto": "carta_girata",
    "vai_al_brano": "grosse_biglie",
    "chiudi_tutto": "menu_tripletta_gi_7",
    "apri_tutto": "menu_tripletta_su_10",
    "domanda": "campanellino",
    "non_disponibile": "rifiuto",
    "errore": "errore_secco",
    "niente_da_suonare": "arpeggio_pensoso",
    "sottobrano_precedente": "menu_tripletta_in_basso_5",
    "sottobrano_successivo": "menu_triplicato_su_4",
    "loop_a_messo": "notifica_tramite_interfaccia_utente_2",
    "loop_b_messo": "notifica_tramite_interfaccia_utente_3",
    "loop_b_tolto": "colpo_d_impatto_1",
    "loop_tolto": "colpo_d_impatto_2",
    "loop_non_qui": "colpo_d_impatto_5",
    "fuori_dal_loop": "avviso_di_sistema",
    "ritorno_al_punto_a": "scintillio_di_ghiaccio",
    "nessun_altro_brano": "il_gioco_spunta_a_met",
}


def suona(evento, volume=0.5, sync=False):
    """Suona il preset dell'evento. Il volume va da 0 a 1; a zero tace.
    Con sync aspetta la fine del suono."""
    if volume <= 0:
        return False
    from GBUtils import Acusticator

    return Acusticator.play(EVENTI[evento], sync=sync, volume=volume)
