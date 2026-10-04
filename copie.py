# MeTeOra, le copie dei dati: le ultime tre versioni di playlist, marker e impostazioni, una per sessione.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.90.0, tappa 12 c del piano.

"""Le copie dei dati (1.90.0).

Le playlist, i marker e le impostazioni sono un patrimonio: un file rovinato
si riconosce gia' all'avvio, e non si sovrascrive, ma una sessione andata
storta, per esempio una playlist svuotata per sbaglio, poi si salva. A ogni
avvio, prima che MeTeOra legga i dati, ruota() mette nella cartella "copie",
accanto ai dati, la versione di adesso di ogni file, se e' diversa dall'ultima
copia: "MeTeOra - Playlist.json.1" e' quella dell'avvio piu' recente, .2 e .3
quelle prima. Copie per sessione e non per salvataggio: le playlist si
salvano a ogni modifica, e tre copie a pochi secondi l'una dall'altra non
servirebbero. Lo schedario resta fuori: si rifa' da solo rileggendo i file, e
pesa. Per tornare a una copia, a MeTeOra chiuso, la si copia al posto del file
vero, togliendo il numero in fondo al nome.
"""

import contextlib
import os
import shutil

CARTELLA = "copie"
QUANTE = 3


def _uguali(primo, secondo):
    """Vero se i due file hanno lo stesso contenuto. Non filecmp, che ricorda
    gli esiti per misura e ora di modifica: due salvataggi nello stesso
    istante, della stessa misura, gli sembrerebbero uguali."""
    if os.path.getsize(primo) != os.path.getsize(secondo):
        return False
    with open(primo, "rb") as a, open(secondo, "rb") as b:
        return a.read() == b.read()


def ruota(cartella, nomi, quante=QUANTE):
    """Una copia di ogni file di nomi che c'e' nella cartella, se e' diverso
    dall'ultima: la piu' vecchia esce. Un errore del disco non ferma l'avvio:
    torna i nomi dei file che non e' riuscita a copiare."""
    copie = os.path.join(cartella, CARTELLA)
    mancate = []
    for nome in nomi:
        originale = os.path.join(cartella, nome)
        if not os.path.isfile(originale):
            continue
        try:
            os.makedirs(copie, exist_ok=True)
            ultima = os.path.join(copie, f"{nome}.1")
            if os.path.isfile(ultima) and _uguali(originale, ultima):
                continue
            for numero in range(quante - 1, 0, -1):
                vecchia = os.path.join(copie, f"{nome}.{numero}")
                if os.path.isfile(vecchia):
                    os.replace(vecchia, os.path.join(copie, f"{nome}.{numero + 1}"))
            shutil.copy2(originale, ultima)
        except OSError:
            mancate.append(nome)
            continue
        # Una copia oltre il numero voluto, per esempio dopo averlo cambiato, se ne va.
        with contextlib.suppress(OSError):
            os.remove(os.path.join(copie, f"{nome}.{quante + 1}"))
    return mancate
