# MeTeOra, i formati: quali file il programma sa suonare.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1.

"""Le estensioni dei file supportati.

I SID li suona la DLL di libsidplayfp; tutto il resto libmpv, che dietro ha
FFmpeg e libopenmpt. L'elenco e' quello dei formati che la tappa 0 ha visto
fra i demuxer di libmpv: la tappa 6 lo collaudera' uno per uno.
"""

import os

SID = frozenset({".sid"})
AUDIO = frozenset({
    ".mp3", ".mp2", ".wav", ".flac", ".ogg", ".oga", ".opus", ".m4a", ".aac", ".wma", ".ape", ".wv", ".tak", ".tta",
    ".mpc", ".dsf", ".dff", ".aiff", ".aif", ".alac", ".ac3", ".dts", ".mka", ".au", ".caf", ".spx",
    ".mid", ".midi", ".kar",
    ".mod", ".xm", ".it", ".s3m", ".mptm", ".669", ".med", ".mtm", ".stm", ".umx",
})
VIDEO = frozenset({".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv", ".m4v", ".mpg", ".mpeg", ".ts", ".m2ts", ".3gp", ".vob", ".ogv"})
TUTTI = SID | AUDIO | VIDEO


def estensione(percorso):
    return os.path.splitext(percorso)[1].lower()


def supportato(percorso):
    return estensione(percorso) in TUTTI


def e_sid(percorso):
    return estensione(percorso) in SID


def filtro_dialogo():
    """Il filtro dei file per la finestra Apri file."""
    tutti = ";".join(f"*{e}" for e in sorted(TUTTI))
    return f"File multimediali ({tutti})|{tutti}|Tutti i file (*.*)|*.*"
