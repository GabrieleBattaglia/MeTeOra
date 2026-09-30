# MeTeOra, la ricerca globale: cerca con il filtro in tutte le playlist e in tutte le unita'.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la 1.15.0, issue 10.

"""La ricerca in tutto MeTeOra.

Usa la grammatica del filtro. Cerca prima nei Preferiti e nelle playlist,
poi nelle unita' di Questo PC, dischi e chiavette; salta le unita' di rete e
i CD, che possono essere lentissimi o vuoti. I file sul disco li giudica con
la scheda dello schedario, se c'e': un file mai visto si conosce solo per il
nome e il percorso, quindi i comandi su durata e tag non lo trovano.
Il lavoro lo fa un filo a parte, che si puo' fermare; chi aspetta viene
avvisato al massimo due volte al secondo e alla fine.
"""

import os
import threading
import time

import questo_pc
from playlist import Brano

# I tipi di unita' in cui si cerca: rimovibili, dischi fissi, dischi in memoria.
UNITA_DA_CERCARE = (2, 3, 6)
INTERVALLO_DEGLI_AVVISI = 0.5


def _tipo_di_unita(radice):
    import ctypes

    return ctypes.windll.kernel32.GetDriveTypeW(radice)


class Ricerca:
    def __init__(self, filtro, brani_delle_playlist, schedario, avvisa=None, unita=None):
        """brani_delle_playlist: i brani dei Preferiti e delle playlist, da
        guardare per primi; unita: le radici da cercare, se si vogliono
        diverse da quelle di Questo PC, per esempio nelle prove."""
        self.filtro = filtro
        self._brani = list(brani_delle_playlist)
        self._schedario = schedario
        self._avvisa = avvisa
        self._unita = unita
        self.risultati = []
        self._visti = set()
        self.finita = False
        self.fermata = False
        self._lucchetto = threading.Lock()
        self._ultimo_avviso = 0.0
        self._filo = threading.Thread(target=self._lavora, name="ricerca", daemon=True)

    def avvia(self):
        self._filo.start()

    def ferma(self):
        self.fermata = True
        self._filo.join(timeout=2)

    def aspetta(self, secondi=60):
        """Per le prove."""
        self._filo.join(timeout=secondi)

    def quanti(self):
        with self._lucchetto:
            return len(self.risultati)

    def pezzo(self, inizio, fine):
        with self._lucchetto:
            return self.risultati[inizio:fine]

    def _trovato(self, brano):
        chiave = (os.path.normcase(brano.percorso), brano.sottobrano)
        if chiave in self._visti:
            return
        self._visti.add(chiave)
        with self._lucchetto:
            self.risultati.append(Brano(brano.percorso, sottobrano=brano.sottobrano))
        adesso = time.monotonic()
        if self._avvisa and adesso - self._ultimo_avviso >= INTERVALLO_DEGLI_AVVISI:
            self._ultimo_avviso = adesso
            self._avvisa()

    def _lavora(self):
        for brano in self._brani:
            if self.fermata:
                return
            if self.filtro.ammette(brano, self._schedario.scheda(brano.percorso)):
                self._trovato(brano)
        radici = self._unita if self._unita is not None else [r for r, _nome in questo_pc.unita() if _tipo_di_unita(r) in UNITA_DA_CERCARE]
        for radice in radici:
            self._cerca_in(radice)
            if self.fermata:
                return
        self.finita = True
        if self._avvisa:
            self._avvisa()

    def _cerca_in(self, cartella):
        pendenti = [cartella]
        while pendenti and not self.fermata:
            attuale = pendenti.pop()
            try:
                cartelle, files = questo_pc.contenuto(attuale)
            except OSError:
                continue
            for percorso in files:
                if self.fermata:
                    return
                brano = Brano(percorso)
                if self.filtro.ammette(brano, self._schedario.scheda(percorso)):
                    self._trovato(brano)
            # In ordine alfabetico: le cartelle si prendono dalla fine della pila.
            pendenti.extend(reversed(cartelle))
