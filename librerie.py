# MeTeOra, le librerie native: rende visibili libmpv e la DLL dei SID.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1, da prototipi/ambiente.py. Nella 1.85.1 libmpv caricata qui, per dire perche' non si carica.

"""Da importare prima di mpv e di sid.

Le DLL non stanno nel repository: le mette in lib lo script
strumenti/prepara_ambiente.py. Il percorso lo aggiunge sia a PATH, dove
python-mpv cerca libmpv-2.dll, sia alle cartelle delle DLL di Windows, dove
sidshim.dll trova le sue dipendenze.
Dalla 1.85.1 libmpv si carica qui, per la prima volta: se non si carica,
l'avvio lo dice con il motivo, invece di fermarsi su un errore di Python.
Il motivo tipico e' vulkan-1.dll, la libreria di Vulkan che libmpv chiede
per il video: la installano i driver della scheda video, e puo' mancare su
macchine virtuali o con driver vecchi (decisione di Gabriele, 4 ottobre 2026:
un messaggio chiaro, senza portarla nel pacchetto).
"""

import ctypes
import os

import percorsi

VULKAN = "vulkan-1.dll"


class LibrerieMancanti(RuntimeError):
    """La cartella lib non c'e', e' incompleta, o libmpv non si carica."""


def _carica(percorso):
    ctypes.CDLL(percorso)


def _vulkan_presente():
    """Vero se Windows trova vulkan-1.dll. Si chiede solo quando libmpv non
    si carica: caricarla non fa niente di suo."""
    try:
        ctypes.WinDLL(VULKAN)
    except OSError:
        return False
    return True


def prepara():
    """Rende visibile la cartella lib e la restituisce."""
    cartella = percorsi.cartella_librerie()
    mancanti = [f for f in ("libmpv-2.dll", "sidshim.dll") if not os.path.isfile(os.path.join(cartella, f))]
    if mancanti:
        raise LibrerieMancanti(f"Nella cartella {cartella} mancano {', '.join(mancanti)}: eseguire strumenti/prepara_ambiente.py")
    if cartella not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] = cartella + os.pathsep + os.environ["PATH"]
        os.add_dll_directory(cartella)
    try:
        _carica(os.path.join(cartella, "libmpv-2.dll"))
    except OSError as errore:
        if not _vulkan_presente():
            raise LibrerieMancanti(f"Manca {VULKAN}, la libreria di Vulkan che libmpv usa per il video, e senza di lei MeTeOra non suona. "
                "Di solito la installano i driver della scheda video: aggiornali dal sito di chi ha fatto la scheda, oppure installa "
                "il Vulkan Runtime da https://vulkan.lunarg.com.") from errore
        raise LibrerieMancanti(f"libmpv-2.dll, nella cartella {cartella}, non si carica: {errore}") from errore
    return cartella


LIB = prepara()
