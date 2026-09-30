# MeTeOra, il contatore delle cartelle: quanti file suonabili ha una cartella, sottocartelle comprese.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la 1.22.0, dal collaudo della 1.20.0.

"""Il conto dei file di una cartella, con tutto cio' che ha sotto.

Serve alle etichette delle cartelle di Questo PC, che dicono quanti file
suonabili contengono e quanto durano in tutto. Contare vuol dire leggere
ogni sottocartella: lo fa un filo a parte. Ogni cartella del disco si legge
una volta sola per sessione, e il conto di una cartella si ricava da quelli
delle sue sottocartelle. Chi aspetta viene avvisato al massimo una volta al
secondo e alla fine; lo schedario riceve i file contati, per le durate.
"""

import queue
import threading
import time

import questo_pc

INTERVALLO_DEGLI_AVVISI = 1.0


class Contatore:
    def __init__(self, schedario=None, avvisa=None):
        self._schedario = schedario
        self._avvisa = avvisa
        # Per cartella: i file suonabili, sottocartelle comprese.
        self.conti = {}
        self._letture = {}
        self._coda = queue.Queue()
        self._in_coda = set()
        self._lucchetto = threading.Lock()
        self._fermo = False
        self._filo = None

    def files(self, cartella):
        """I file suonabili della cartella e delle sue sottocartelle, o None
        se il conto non e' ancora pronto."""
        return self.conti.get(cartella)

    def chiedi(self, cartelle):
        with self._lucchetto:
            for cartella in cartelle:
                if cartella not in self.conti and cartella not in self._in_coda:
                    self._in_coda.add(cartella)
                    self._coda.put(cartella)
        if self._in_coda and (self._filo is None or not self._filo.is_alive()):
            self._filo = threading.Thread(target=self._lavora, name="contatore", daemon=True)
            self._filo.start()

    def dimentica(self, cartella):
        """Dimentica i conti e le letture della cartella e di cio' che ha
        sotto, e di chi la contiene: servono quando la cartella cambia."""
        chiave = cartella.rstrip("\\").lower()

        def legate(c):
            c = c.rstrip("\\").lower()
            return c == chiave or c.startswith(chiave + "\\") or chiave.startswith(c + "\\")

        with self._lucchetto:
            for mappa in (self.conti, self._letture):
                for c in [c for c in mappa if legate(c)]:
                    del mappa[c]

    def _lettura(self, cartella):
        if cartella not in self._letture:
            try:
                self._letture[cartella] = questo_pc.contenuto(cartella)
            except OSError:
                self._letture[cartella] = ([], [])
        return self._letture[cartella]

    def _conta(self, cartella):
        """Il conto di una cartella, con una pila e non con la ricorsione:
        gli alberi delle collezioni possono essere molto profondi."""
        if cartella in self.conti:
            return self.conti[cartella]
        files = []
        pila = [cartella]
        while pila and not self._fermo:
            attuale = pila.pop()
            if attuale != cartella and attuale in self.conti:
                files.extend(self.conti[attuale])
                continue
            sottocartelle, propri = self._lettura(attuale)
            files.extend(propri)
            pila.extend(reversed(sottocartelle))
        return files

    def _lavora(self):
        ultimo = time.monotonic()
        while not self._fermo:
            try:
                cartella = self._coda.get(timeout=0.5)
            except queue.Empty:
                break
            files = self._conta(cartella)
            if self._fermo:
                break
            with self._lucchetto:
                self.conti[cartella] = files
                self._in_coda.discard(cartella)
            if self._schedario is not None:
                self._schedario.chiedi(files)
            if self._avvisa and time.monotonic() - ultimo >= INTERVALLO_DEGLI_AVVISI:
                ultimo = time.monotonic()
                self._avvisa()
        if self._avvisa and not self._fermo:
            self._avvisa()

    def ferma(self):
        self._fermo = True
        if self._filo is not None:
            self._filo.join(timeout=2)

    def aspetta(self, secondi=30):
        """Per le prove."""
        if self._filo is not None:
            self._filo.join(timeout=secondi)
