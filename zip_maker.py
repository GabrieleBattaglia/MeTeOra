# MeTeOra, utilita': prepara l'archivio della release per l'auto updater.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.84.0, dal modello di Dadillo.

"""Comprime la cartella prodotta da PyInstaller, dist/MeTeOra, nell'archivio
MeTeOra.zip, con i file alla radice e il manifesto di _internal.

Tutto il mestiere sta in crea_archivio_release di GBUtils, cosi' la regola
sulle esclusioni e' una sola per tutti i progetti (prontuario, fase 7). Qui
restano i nomi di MeTeOra: i file dei dati che nascono accanto
all'eseguibile provandolo, le console salvate, FluidSynth e i banchi di suoni
scaricati al primo MIDI.
"""

import sys

from GBUtils import crea_archivio_release

FUORI = [
    "MeTeOra - *.json",
    "MeTeOra-V*.txt",
    "fluidsynth/",
    "banchi/",
]


def main():
    try:
        crea_archivio_release("MeTeOra", escludi=FUORI)
    except (FileNotFoundError, OSError) as e:
        print(f"Archivio non creato: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
