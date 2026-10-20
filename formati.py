# MeTeOra, i formati: quali file il programma sa suonare.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.65.0 i MIDI e i tracker a parte, nella 1.66.0 la musica delle console. Nella 1.82.0 testo_srt, da sottotitoli_ocr.py, per la passata e il karaoke. Nella 1.104.0 i formati campionati, per le durate credibili dello schedario. Nella 1.113.0 le playlist di altri programmi, a parte.

"""Le estensioni dei file supportati.

I SID li suona la DLL di libsidplayfp; tutto il resto libmpv, che dietro ha
FFmpeg e libopenmpt. L'elenco e' quello dei formati che la tappa 0 ha visto
fra i demuxer di libmpv. Dalla tappa 6 tests/test_formati.py collauda uno per
uno quelli che FFmpeg sa anche scrivere, DTS compreso; APE, TAK, Musepack, DSD
e Speex restano da provare con file veri.
"""

import os

SID = frozenset({".sid"})
# I MIDI li rende FluidSynth, dalla 1.65.0 (tappa 8, issue 16).
MIDI = frozenset({".mid", ".midi", ".kar"})
# La musica delle console la rende libgme, dalla 1.66.0 (tappa 8).
CHIP = frozenset({".ay", ".gbs", ".gym", ".hes", ".kss", ".nsf", ".nsfe", ".sap", ".spc", ".vgm", ".vgz"})
# I moduli dei tracker, che libmpv legge con libopenmpt: dalla 1.65.0 tutte
# le estensioni di libopenmpt, compresi i formati Amiga classici (OKT, MED,
# SFX, STK, DIGI, Future Composer...), tranne quelle che hanno anche altri
# usi, come .ppm e .mus (tappa 8, Gabriele). Il filtro le usa per k=tracker.
TRACKER = frozenset({
    ".mod", ".xm", ".it", ".s3m", ".mptm", ".669", ".med", ".mtm", ".stm", ".umx",
    ".amf", ".ams", ".c67", ".dbm", ".digi", ".dmf", ".dsm", ".dsym", ".dtm", ".far", ".fc", ".fc13", ".fc14", ".gdm", ".gmc",
    ".ice", ".imf", ".j2b", ".m15", ".mdl", ".mms", ".mo3", ".mt2", ".nst", ".okt", ".plm", ".psm", ".pt36", ".ptm", ".puma",
    ".rtm", ".sfx", ".sfx2", ".smod", ".st26", ".stk", ".stp", ".stx", ".symmod", ".ult", ".wow",
})
AUDIO = frozenset({
    ".mp3", ".mp2", ".wav", ".flac", ".ogg", ".oga", ".opus", ".m4a", ".m4b", ".aac", ".wma", ".ape", ".wv", ".tak", ".tta",
    ".mpc", ".dsf", ".dff", ".aiff", ".aif", ".alac", ".ac3", ".dts", ".mka", ".au", ".caf", ".spx",
}) | TRACKER
VIDEO = frozenset({".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv", ".m4v", ".mpg", ".mpeg", ".ts", ".m2ts", ".3gp", ".vob", ".ogv"})
TUTTI = SID | MIDI | CHIP | AUDIO | VIDEO
# I formati campionati, audio e video, che tengono il suono campione per
# campione: piu' durano, piu' pesano, e lo schedario ne scarta le durate
# troppo lunghe per il peso del file (1.104.0). AUDIO comprende anche i
# tracker, che come i SID, i MIDI e le console sono partiture.
CAMPIONATI = (AUDIO - TRACKER) | VIDEO
# Le playlist di altri programmi, che MeTeOra importa (1.113.0). Stanno
# fuori da TUTTI: non si suonano, la plancia non le mostra nelle cartelle, e
# le statistiche non le contano fra i formati.
PLAYLIST = frozenset({".m3u", ".m3u8", ".pls"})


def estensione(percorso):
    return os.path.splitext(percorso)[1].lower()


def supportato(percorso):
    return estensione(percorso) in TUTTI


def e_playlist(percorso):
    return estensione(percorso) in PLAYLIST


def e_sid(percorso):
    return estensione(percorso) in SID


def e_midi(percorso):
    return estensione(percorso) in MIDI


def e_chip(percorso):
    return estensione(percorso) in CHIP


def e_campionato(percorso):
    return estensione(percorso) in CAMPIONATI


def _tempo_srt(secondi):
    millesimi = round(secondi * 1000)
    ore, millesimi = divmod(millesimi, 3600000)
    minuti, millesimi = divmod(millesimi, 60000)
    secondi, millesimi = divmod(millesimi, 1000)
    return f"{ore:02d}:{minuti:02d}:{secondi:02d},{millesimi:03d}"


def testo_srt(sottotitoli):
    """Il contenuto di un file .srt da [(inizio, fine, testo)], in secondi:
    lo scrivono la passata degli impressi (1.80.0) e il karaoke (1.82.0)."""
    blocchi = [f"{numero}\n{_tempo_srt(inizio)} --> {_tempo_srt(fine)}\n{testo}\n" for numero, (inizio, fine, testo) in enumerate(sottotitoli, 1)]
    return "\n".join(blocchi)


def e_video(percorso):
    return estensione(percorso) in VIDEO


def ha_sottobrani(percorso):
    """Vero per i file che possono avere piu' brani dentro: SID e console."""
    return estensione(percorso) in SID | CHIP


def _modelli(estensioni):
    return ";".join(f"*{e}" for e in sorted(estensioni))


def filtro_dialogo():
    """Il filtro dei file per la finestra Apri file: dalla 1.113.0 i file
    multimediali comprendono le playlist, che hanno anche un filtro loro."""
    tutti, playlist = _modelli(TUTTI | PLAYLIST), _modelli(PLAYLIST)
    return f"File multimediali ({tutti})|{tutti}|Playlist ({playlist})|{playlist}|Tutti i file (*.*)|*.*"


def filtro_delle_playlist():
    """Il filtro dei file per il comando Importa playlist (1.113.0)."""
    playlist = _modelli(PLAYLIST)
    return f"Playlist ({playlist})|{playlist}|Tutti i file (*.*)|*.*"
