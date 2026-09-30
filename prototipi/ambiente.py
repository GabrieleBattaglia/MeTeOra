# MeTeOra, prototipi: rende visibili le librerie native della cartella lib.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 29/09/2026: nasce con il repository.

"""Da importare prima di mpv e di sid.

Le DLL (libmpv-2.dll, sidshim.dll e le sue dipendenze) non stanno nel
repository: le mette in lib/ lo script strumenti/prepara_ambiente.py.
"""

import os
import sys

# I moduli del programma stanno nella cartella superiore.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import librerie

LIB = librerie.LIB
