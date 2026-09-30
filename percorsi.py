# MeTeOra, i percorsi: dove stanno i file, da sorgente e da eseguibile.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1.

"""I percorsi di MeTeOra.

Le due regole stanno per esteso nelle docstring di cartella_applicazione e
percorso_risorsa di GBUtils. Cio' che il programma scrive, cioe' playlist e
impostazioni, sta accanto al programma: accanto all'eseguibile quando e'
compilato, accanto ai sorgenti altrimenti. Cio' che il programma legge
soltanto, cioe' manuale, changelog e librerie native, da compilato viaggia
dentro il pacchetto e li' va cercato per primo.
Sono funzioni e non costanti: una costante si calcolerebbe all'importazione
e non guarderebbe piu' se il programma e' compilato.
"""

import os

from GBUtils import cartella_applicazione
from GBUtils import percorso_risorsa as _percorso_risorsa


def cartella_programma():
    """La cartella dell'eseguibile compilato, oppure quella dei sorgenti."""
    return cartella_applicazione()


def percorso_dati(nome_file):
    """Un file che MeTeOra scrive: playlist, impostazioni."""
    return os.path.join(cartella_applicazione(), nome_file)


def percorso_risorsa(nome_file):
    """Un file che MeTeOra legge soltanto: manuale, changelog, crediti."""
    return _percorso_risorsa(nome_file)


def cartella_librerie():
    """La cartella lib con libmpv e la DLL dei SID."""
    return _percorso_risorsa("lib")
