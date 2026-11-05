# MeTeOra, la precedenza della finestra: il segnale che fa aspettare i fili in disparte, anche per mezzo secondo dopo ogni tasto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 2.7.1, dal collaudo della 2.7.0.

"""La precedenza della finestra sui fili in disparte.

Il contatore, lo schedario, l'esploratore e la pulizia all'avvio lavorano in
fili di Python, e Python esegue un filo alla volta: mentre lavorano, il filo
della finestra aspetta il suo turno, e con lui NVDA, perche' lo stato delle
voci della plancia glielo da' MeTeOra, in Python (issue 21). Dalla 1.83.1 la
finestra alza un segnale mentre rinfresca la plancia o la apre, e i fili lo
guardano tra una cartella e l'altra e aspettano.

Nel collaudo della 2.7.0 Gabriele ha trovato NVDA lento di secondi mentre
Questo PC si apriva tutto, e meno reattivo anche dopo, mentre lo schedario
leggeva i tag delle cartelle nuove. Dalla 2.7.1 il segnale si alza anche a
ogni tasto, per PRECEDENZA_AI_TASTI secondi: chi naviga trova la strada
libera, e il lavoro in disparte va avanti quando la tastiera si ferma.

Cedi si usa come il threading.Event di prima: set, clear e is_set. In piu'
trattieni(secondi) lo tiene alzato per un po', e trattenuto() dice se lo e'
ancora per un tasto, cosi' anche la finestra rimanda il lavoro suo.
"""

import time

PRECEDENZA_AI_TASTI = 0.5


class Cedi:
    def __init__(self):
        self._alzato = False
        self._fino = 0.0

    def set(self):
        self._alzato = True

    def clear(self):
        self._alzato = False

    def is_set(self):
        return self._alzato or time.monotonic() < self._fino

    def trattieni(self, secondi=PRECEDENZA_AI_TASTI):
        """Tiene alzato il segnale per secondi da adesso, oltre al resto."""
        self._fino = max(self._fino, time.monotonic() + secondi)

    def trattenuto(self):
        """I secondi che mancano alla fine della precedenza di un tasto, o 0."""
        return max(0.0, self._fino - time.monotonic())
