# MeTeOra, prototipi: rende visibili le librerie native della cartella lib.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5).
# 29/09/2026: nasce con il repository.

"""Da importare prima di mpv e di sidmotore.

Le DLL (libmpv-2.dll, sidshim.dll e le sue dipendenze) non stanno nel
repository: le mette in lib/ lo script strumenti/prepara_ambiente.py.
"""

import os

LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib")
if not os.path.isdir(LIB):
	raise SystemExit(f"Manca la cartella {LIB}: eseguire prima strumenti/prepara_ambiente.py")
os.environ["PATH"] = LIB + os.pathsep + os.environ["PATH"]
os.add_dll_directory(LIB)
