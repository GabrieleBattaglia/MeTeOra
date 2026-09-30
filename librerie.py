# MeTeOra, le librerie native: rende visibili libmpv e la DLL dei SID.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1, da prototipi/ambiente.py.

"""Da importare prima di mpv e di sid.

Le DLL non stanno nel repository: le mette in lib lo script
strumenti/prepara_ambiente.py. Il percorso lo aggiunge sia a PATH, dove
python-mpv cerca libmpv-2.dll, sia alle cartelle delle DLL di Windows, dove
sidshim.dll trova le sue dipendenze.
"""

import os

import percorsi


class LibrerieMancanti(RuntimeError):
    """La cartella lib non c'e' o e' incompleta."""


def prepara():
    """Rende visibile la cartella lib e la restituisce."""
    cartella = percorsi.cartella_librerie()
    mancanti = [f for f in ("libmpv-2.dll", "sidshim.dll") if not os.path.isfile(os.path.join(cartella, f))]
    if mancanti:
        raise LibrerieMancanti(f"Nella cartella {cartella} mancano {', '.join(mancanti)}: eseguire strumenti/prepara_ambiente.py")
    if cartella not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] = cartella + os.pathsep + os.environ["PATH"]
        os.add_dll_directory(cartella)
    return cartella


LIB = prepara()
