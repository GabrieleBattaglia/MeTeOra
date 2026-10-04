# MeTeOra, la barra braille a blocchi: i testi letti divisi nelle celle della barra, in fila con il tempo minimo di lettura.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.83.0, per la tappa 10, punto g.

"""La barra braille a blocchi (tappa 10, punto g; Gabriele, 4 ottobre 2026).

Chi ha una barra di poche celle legge male un sottotitolo lungo: deve
spostarsi lungo la riga. Qui il testo si divide in blocchi lunghi al piu'
quante celle ha la barra, spezzati fra le parole, e i blocchi si mostrano
uno dopo l'altro, perche' un messaggio braille sostituisce quello di prima.
Ogni blocco resta per la sua parte del tempo che rimane al testo, in
proporzione alla lunghezza, e mai meno del tempo minimo di lettura, che
ognuno sceglie secondo la sua velocita'; ma un testo nuovo aspetta solo il
tempo minimo del blocco mostrato, non la sua parte. Se il tempo minimo crea una coda, i
testi in arrivo aspettano il loro turno: la coda si smaltisce nei silenzi, o
mettendo in pausa, perche' il tempo e' quello dell'orologio, non del brano.
Ogni carattere occupa una cella: il braille informatico a otto punti.
"""

import collections
import time

# Il tempo di un testo, per dividerlo fra i blocchi, al piu' tanti secondi:
# libmpv da' la fine dell'ultimo dei sottotitoli mostrati insieme, e un
# cartello che dura tutto il film non deve fermare la barra (revisione della
# 1.83.0).
DURATA_MASSIMA = 15.0


def blocchi(testo, celle):
    """Il testo in blocchi lunghi al piu' celle caratteri, spezzati fra le
    parole; una parola piu' lunga della barra si spezza dove finisce la
    barra. Con celle 0 il testo resta intero."""
    testo = " ".join(testo.split())
    if not testo:
        return []
    if not celle or len(testo) <= celle:
        return [testo]
    risultato, corrente = [], ""
    for parola in testo.split(" "):
        while len(parola) > celle:
            if corrente:
                risultato.append(corrente)
                corrente = ""
            risultato.append(parola[:celle])
            parola = parola[celle:]
        if not parola:
            continue
        if not corrente:
            corrente = parola
        elif len(corrente) + 1 + len(parola) <= celle:
            corrente += " " + parola
        else:
            risultato.append(corrente)
            corrente = parola
    if corrente:
        risultato.append(corrente)
    return risultato


class Coda:
    """I blocchi in fila per la barra. mostra(blocco) li manda al braille;
    pianifica(secondi, funzione) chiama funzione piu' tardi, nello stesso
    filo, e restituisce un oggetto con Stop(), come wx.CallLater; orologio
    da' i secondi, come time.monotonic."""

    def __init__(self, mostra, pianifica, orologio=time.monotonic):
        self._mostra = mostra
        self._pianifica = pianifica
        self._orologio = orologio
        # (blocco, fine del testo o None, caratteri dal blocco alla fine del
        # testo, minimo in secondi, numero del testo)
        self._fila = collections.deque()
        self._testi = 0
        # Fin quando il blocco mostrato deve restare: con la sua parte del
        # tempo del testo, e con il solo minimo; e l'attesa pianificata.
        self._libera = float("-inf")
        self._minimo_fino = float("-inf")
        self._attesa = None

    def aggiungi(self, testo, celle=0, minimo=2.0, durata=None):
        """Un testo nuovo, in coda: celle quante ne ha la barra, 0 per il
        testo intero; minimo il tempo minimo di lettura di ogni blocco, in
        secondi; durata quanti secondi d'orologio resta il testo, se si sa,
        per dividerla fra i blocchi."""
        pezzi = blocchi(testo, celle)
        if not pezzi:
            return
        self._testi += 1
        fine = self._orologio() + min(durata, DURATA_MASSIMA) if durata else None
        for numero, pezzo in enumerate(pezzi):
            self._fila.append((pezzo, fine, sum(len(p) for p in pezzi[numero:]), minimo, self._testi))
        # Il blocco mostrato trattiene il testo nuovo solo per il suo minimo.
        if self._libera > self._minimo_fino:
            self._libera = self._minimo_fino
            if self._attesa is not None:
                self._attesa.Stop()
                self._attesa = None
        if self._attesa is None:
            self._prossimo()

    def svuota(self):
        """Toglie dalla fila i testi non ancora mostrati, e il tempo minimo
        del blocco mostrato: il testo che arriva dopo si mostra subito."""
        self._fila.clear()
        self._libera = self._minimo_fino = float("-inf")
        if self._attesa is not None:
            self._attesa.Stop()
            self._attesa = None

    @property
    def in_fila(self):
        return len(self._fila)

    def _prossimo(self):
        self._attesa = None
        if not self._fila:
            return
        ora = self._orologio()
        if ora < self._libera:
            self._attesa = self._pianifica(self._libera - ora, self._prossimo)
            return
        pezzo, fine, rimasti, minimo, numero = self._fila.popleft()
        self._mostra(pezzo)
        # La parte del tempo del testo vale finche' non aspetta un altro testo.
        altro = any(voce[4] != numero for voce in self._fila)
        quota = (fine - ora) * len(pezzo) / rimasti if fine is not None and fine > ora and not altro else 0.0
        self._minimo_fino = ora + minimo
        self._libera = ora + max(minimo, quota)
        if self._fila:
            self._attesa = self._pianifica(self._libera - ora, self._prossimo)
