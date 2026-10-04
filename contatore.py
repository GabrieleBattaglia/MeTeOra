# MeTeOra, il contatore delle cartelle: quanti file suonabili ha una cartella, sottocartelle comprese.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la 1.22.0, dal collaudo della 1.20.0. Nella 1.34.6 le letture rinfrescate e Aggiorna su Questo PC. Nella 1.77.0 la cartella cambiata, dopo il cestino.

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
        # Le cartelle cambiate, dimenticate o rinfrescate: un conto fatto
        # mentre una di loro cambiava si rifa', invece di salvare quello
        # vecchio (1.77.0).
        self._cambiate = []

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

    def dimentica(self, cartella, anche_sopra=True):
        """Dimentica i conti e le letture della cartella e di cio' che ha
        sotto, e di chi la contiene: servono quando la cartella cambia. Con
        anche_sopra falso, chi la contiene resta, come per una cartella
        mandata nel cestino, dove i conti di sopra li rifa' cambiata."""
        chiave = cartella.rstrip("\\").lower()

        def legate(c):
            c = c.rstrip("\\").lower()
            return c == chiave or c.startswith(chiave + "\\") or (anche_sopra and chiave.startswith(c + "\\"))

        with self._lucchetto:
            self._cambiate.append(chiave)
            for mappa in (self.conti, self._letture):
                for c in [c for c in mappa if legate(c)]:
                    del mappa[c]

    def cambiata(self, cartella):
        """La cartella ha perso qualcosa, per esempio un file mandato nel
        cestino: si rilegge lei sola, e si dimenticano i conti suoi e di chi
        la contiene; quelli delle sue sottocartelle restano buoni, e il conto
        nuovo li riusa. Torna le cartelle che avevano un conto, da rifare."""
        chiave = cartella.rstrip("\\").lower()
        with self._lucchetto:
            self._cambiate.append(chiave)
            for c in [c for c in self._letture if c.rstrip("\\").lower() == chiave]:
                del self._letture[c]
            vecchi = [c for c in self.conti if c.rstrip("\\").lower() == chiave or chiave.startswith(c.rstrip("\\").lower() + "\\")]
            for c in vecchi:
                del self.conti[c]
        return vecchi

    def dimentica_tutto(self):
        """Dimentica tutti i conti e tutte le letture: Aggiorna su Questo PC."""
        with self._lucchetto:
            self.conti.clear()
            self._letture.clear()

    def rinfresca(self, cartella, lettura):
        """La cartella e' stata appena letta da chi la mostra: se la lettura
        tenuta qui per la sessione e' diversa, la sostituisce e dimentica i
        conti della cartella e di chi la contiene, che vanno rifatti. Torna
        le cartelle da ricontare."""
        with self._lucchetto:
            if cartella not in self._letture or self._letture[cartella] == lettura:
                return []
            self._letture[cartella] = lettura
            chiave = cartella.rstrip("\\").lower()
            self._cambiate.append(chiave)
            vecchi = [c for c in self.conti if c.rstrip("\\").lower() == chiave or chiave.startswith(c.rstrip("\\").lower() + "\\")]
            for c in vecchi:
                del self.conti[c]
        return vecchi

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
            # Un conto gia' fatto si riusa; .get, perche' un'altra mano puo'
            # dimenticarlo nel frattempo.
            fatto = self.conti.get(attuale) if attuale != cartella else None
            if fatto is not None:
                files.extend(fatto)
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
            with self._lucchetto:
                visti = len(self._cambiate)
            files = self._conta(cartella)
            if self._fermo:
                break
            with self._lucchetto:
                chiave = cartella.rstrip("\\").lower()
                if any(c == chiave or c.startswith(chiave + "\\") for c in self._cambiate[visti:]):
                    # Intanto qualcosa li' dentro e' cambiato: il conto si rifa'.
                    self._coda.put(cartella)
                    continue
                self.conti[cartella] = files
                self._in_coda.discard(cartella)
                if self._coda.empty():
                    self._cambiate.clear()
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
