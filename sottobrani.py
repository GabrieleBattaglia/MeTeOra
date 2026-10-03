# MeTeOra, i file con piu' brani dentro: i SID e la musica delle console.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 8, dalle funzioni dei SID.

"""Un'interfaccia sola per i file con piu' sottobrani (tappa 8).

Fino alla 1.65.0 i sottobrani erano solo dei SID, e plancia, motore e
schedario chiedevano a songlengths. Dalla 1.66.0 chiedono qui: per i SID
risponde songlengths, con il database della collezione HVSC; per la musica
delle console risponde chip, con libgme. Le informazioni hanno la stessa
forma: sottobrani, iniziale, titolo, autore, copyright.
"""

import chip
import formati
import songlengths


def info(percorso):
    """Le informazioni di un file con sottobrani, o None."""
    if formati.e_sid(percorso):
        return songlengths.info_del_sid(percorso)
    if formati.e_chip(percorso):
        return chip.info(percorso)
    return None


def durate(percorso):
    """Le durate in secondi dei sottobrani, una per sottobrano (None dove
    non si sa), o None se il file non le ha."""
    if formati.e_sid(percorso):
        return songlengths.durate_del_file(percorso)
    if formati.e_chip(percorso):
        dati = chip.info(percorso)
        return dati["durate"] if dati else None
    return None
