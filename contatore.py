# MeTeOra, il contatore delle cartelle: quanti file suonabili ha una cartella, sottocartelle comprese.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la 1.22.0, dal collaudo della 1.20.0. Nella 1.34.6 le letture rinfrescate e Aggiorna su Questo PC. Nella 1.77.0 la cartella cambiata, dopo il cestino. Nella 1.77.1 la rete letta con la protezione della ricerca. Nella 1.83.1 il filo cede il passo alla finestra mentre rinfresca la plancia. Nella 1.85.5 la radice di rete lasciata solo alla terza cartella muta, e ritrovata viva dalla plancia.

"""Il conto dei file di una cartella, con tutto cio' che ha sotto.

Serve alle etichette delle cartelle di Questo PC, che dicono quanti file
suonabili contengono e quanto durano in tutto. Contare vuol dire leggere
ogni sottocartella: lo fa un filo a parte. Ogni cartella del disco si legge
una volta sola per sessione, e il conto di una cartella si ricava da quelli
delle sue sottocartelle. Chi aspetta viene avvisato al massimo una volta al
secondo e alla fine; lo schedario riceve i file contati, per le durate.
In rete ogni cartella si legge con la lettura protetta della ricerca: il
Samba dell'Iliadbox, percorso tutto, dopo circa 17 mila cartelle lascia
appesa una lettura, e il contatore restava fermo per il resto della
sessione, senza piu' contare nemmeno i dischi del PC. Una cartella che non
risponde si salta, e non si rilegge: lascerebbe appeso un altro filo; i
conti che la comprendono sono parziali (1.77.1).
Dalla 1.85.5 la radice intera, come \\\\server\\cartella, si lascia perdere solo
alla terza cartella muta, come fa la ricerca: il Samba dell'Iliadbox, quando
lascia appesa una lettura, risponde a tutte le altre. Prima bastava la
prima, e la radice restava muta per tutta la sessione: nel collaudo di
Gabriele una cartella dei backup ha spento cosi' tutta la condivisione,
Video compreso, mentre Esplora risorse la leggeva. Una radice lasciata
perdere torna viva quando la plancia vi legge una cartella: i conti
parziali di quella radice si rifanno.
"""

import os
import queue
import threading
import time

import questo_pc
from ricerca import CARTELLE_MUTE, NonRisponde, errore_di_rete, in_rete, leggi_in_rete

INTERVALLO_DEGLI_AVVISI = 1.0
# Quanto aspetta il filo, a ogni giro, mentre deve cedere il passo.
PAUSA_PER_CEDERE = 0.005


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
        # Le cartelle di rete che non hanno risposto, minuscole e senza la
        # barra in fondo: non si rileggono, perche' ognuna lascia un filo
        # appeso, finche' la plancia non le legge o fino ad Aggiorna. Le radici,
        # come \\server\cartella o Z:, lasciate perdere alla CARTELLE_MUTE-esima
        # cartella muta, con il loro conto; non si leggono finche' la plancia
        # non le ritrova vive (1.85.5): per radice, le cartelle mute contate
        # dall'ultima volta che e' tornata viva. Le radici tornate vive, una
        # voce per ritorno: un conto parziale fatto in una di loro mentre
        # tornava viva si rifa'. E le cartelle il cui conto ne ha saltato una
        # parte.
        self.cartelle_mute = set()
        self.mute = set()
        self._mute_per_radice = {}
        self._rinate = []
        self.parziali = set()
        # Gli Aggiorna che dimenticano tutto ("tutto") o la rete ("rete"): un
        # conto in corso in quel momento si rifa' (revisione della 1.85.5).
        self._azzeramenti = []
        self._parziale = False
        # Quando e' alzato, il filo aspetta prima della cartella seguente: la
        # finestra lo alza mentre rinfresca la plancia, che altrimenti, con il
        # lucchetto di Python conteso, andava venti volte piu' piano (1.83.1).
        self.cedi = threading.Event()

    def _cedi_il_passo(self):
        while self.cedi.is_set() and not self._fermo:
            time.sleep(PAUSA_PER_CEDERE)

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
            # Una copia delle chiavi: il filo del contatore puo' aggiungere
            # letture intanto.
            for mappa in (self.conti, self._letture):
                for c in [c for c in list(mappa) if legate(c)]:
                    mappa.pop(c, None)
            self.parziali = {c for c in self.parziali if not legate(c)}
            # Aggiorna su una cartella di rete la riprova, con le mute che ha
            # sotto; se la sua radice era stata lasciata perdere, torna viva, e
            # si rifanno anche i conti delle altre cartelle che l'avevano
            # saltata (revisione della 1.85.5).
            self.cartelle_mute = {c for c in self.cartelle_mute if not legate(c)}
            for contate in self._mute_per_radice.values():
                contate.difference_update([c for c in contate if legate(c)])
            # Le radici legate al percorso: la sua, o quelle che contiene, come
            # le condivisioni di un computer della rete con Aggiorna su di lui.
            radice = _radice(cartella)
            da_rifare = []
            for r in [r for r in self.mute if r == radice or legate(r)]:
                da_rifare += self._ravviva(r)
            return da_rifare

    def cambiata(self, cartella):
        """La cartella ha perso qualcosa, per esempio un file mandato nel
        cestino: si rilegge lei sola, e si dimenticano i conti suoi e di chi
        la contiene; quelli delle sue sottocartelle restano buoni, e il conto
        nuovo li riusa. Torna le cartelle che avevano un conto, da rifare."""
        chiave = cartella.rstrip("\\").lower()
        with self._lucchetto:
            self._cambiate.append(chiave)
            for c in [c for c in list(self._letture) if c.rstrip("\\").lower() == chiave]:
                self._letture.pop(c, None)
            vecchi = [c for c in list(self.conti) if c.rstrip("\\").lower() == chiave or chiave.startswith(c.rstrip("\\").lower() + "\\")]
            for c in vecchi:
                del self.conti[c]
        return vecchi

    def dimentica_tutto(self):
        """Dimentica tutti i conti e tutte le letture: Aggiorna su Questo PC."""
        with self._lucchetto:
            self.conti.clear()
            self._letture.clear()
            self.cartelle_mute.clear()
            self.mute.clear()
            self._mute_per_radice.clear()
            self.parziali.clear()
            self._azzeramenti.append("tutto")

    def dimentica_la_rete(self):
        """Aggiorna su Questa rete: dimentica i conti e le letture delle
        cartelle di rete, le cartelle mute e le radici lasciate perdere; i
        conti dei dischi del PC restano. Torna le cartelle di cui ha
        dimenticato il conto (revisione della 1.85.5)."""
        with self._lucchetto:
            radici = {}

            def di_rete(c):
                radice = _radice(c)
                if radice not in radici:
                    radici[radice] = in_rete(c)
                return radici[radice]

            dimenticate = sorted(c for c in list(self.conti) if di_rete(c))
            for c in dimenticate:
                self.conti.pop(c, None)
            for c in [c for c in list(self._letture) if di_rete(c)]:
                self._letture.pop(c, None)
            self.parziali = {c for c in self.parziali if not di_rete(c)}
            self.cartelle_mute.clear()
            self.mute.clear()
            self._mute_per_radice.clear()
            self._azzeramenti.append("rete")
        return dimenticate

    def _ravviva(self, radice):
        """Con il lucchetto preso: la radice lasciata perdere torna viva, con
        le mute da contare da capo. Si dimenticano i conti parziali delle sue
        cartelle, che l'avevano saltata, e un conto parziale ancora in corso
        in lei si rifara'. Torna le cartelle da ricontare."""
        self.mute.discard(radice)
        self._mute_per_radice.pop(radice, None)
        self._rinate.append(radice)
        da_rifare = [c for c in self.parziali if _radice(c) == radice]
        for c in da_rifare:
            self.conti.pop(c, None)
            self.parziali.discard(c)
            self._cambiate.append(_chiave(c))
        return da_rifare

    def non_risponde(self, cartella):
        """Una cartella di rete che non ha risposto, nel conto o nella plancia:
        non si rilegge, e alla CARTELLE_MUTE-esima della stessa radice si
        lascia perdere la radice (1.85.5)."""
        radice = _radice(cartella)
        with self._lucchetto:
            chiave = _chiave(cartella)
            if chiave in self.cartelle_mute:
                return
            self.cartelle_mute.add(chiave)
            contate = self._mute_per_radice.setdefault(radice, set())
            contate.add(chiave)
            if len(contate) >= CARTELLE_MUTE:
                self.mute.add(radice)

    def risponde(self, cartella):
        """La plancia ha appena letto una cartella di rete: lei e la sua radice
        rispondono. Se la cartella era muta, esce dalle mute e da quelle che
        contano per la radice, e si rifanno i conti suoi e di chi la contiene,
        che l'avevano saltata, anche quelli ancora in corso; se la radice era
        stata lasciata perdere, torna viva, con le mute da contare da capo, e
        si rifanno i conti parziali di tutte le sue cartelle. Torna le
        cartelle da ricontare (1.85.5)."""
        radice = _radice(cartella)
        chiave = _chiave(cartella)
        with self._lucchetto:
            da_rifare = set(self._ravviva(radice)) if radice in self.mute else set()
            if chiave in self.cartelle_mute:
                self.cartelle_mute.discard(chiave)
                self._mute_per_radice.get(radice, set()).discard(chiave)
                # Un conto in corso che la contiene se ne accorge, e si rifa'.
                self._cambiate.append(chiave)
                for c in [c for c in self.parziali if _chiave(c) == chiave or chiave.startswith(_chiave(c) + "\\")]:
                    self.conti.pop(c, None)
                    self.parziali.discard(c)
                    self._cambiate.append(_chiave(c))
                    da_rifare.add(c)
        return sorted(da_rifare)

    def rinfresca(self, cartella, lettura):
        """La cartella e' stata appena letta da chi la mostra: se la lettura
        tenuta qui per la sessione e' diversa, la sostituisce e dimentica i
        conti della cartella e di chi la contiene, che vanno rifatti. Torna
        le cartelle da ricontare."""
        with self._lucchetto:
            if cartella not in self._letture:
                # La lettura della plancia vale anche qui: il contatore non
                # rilegge una cartella appena letta, e in rete una lettura in
                # meno puo' restare appesa (revisione della 1.85.5).
                self._letture[cartella] = lettura
                return []
            if self._letture[cartella] == lettura:
                return []
            self._letture[cartella] = lettura
            chiave = cartella.rstrip("\\").lower()
            self._cambiate.append(chiave)
            vecchi = [c for c in list(self.conti) if c.rstrip("\\").lower() == chiave or chiave.startswith(c.rstrip("\\").lower() + "\\")]
            for c in vecchi:
                self.conti.pop(c, None)
        return vecchi

    def _lettura(self, cartella):
        lettura = self._letture.get(cartella)
        if lettura is not None:
            return lettura
        rete = in_rete(cartella)
        try:
            if rete:
                if _radice(cartella) in self.mute or _chiave(cartella) in self.cartelle_mute:
                    # Gia' muta: non si riprova, il conto e' parziale.
                    self._parziale = True
                    return [], []
                lettura = leggi_in_rete(cartella, fermo=lambda: self._fermo)
            else:
                lettura = questo_pc.contenuto(cartella)
        except NonRisponde:
            # Se intanto l'ha letta la plancia, vale la sua lettura.
            with self._lucchetto:
                letta = self._letture.get(cartella)
            if letta is not None:
                return letta
            # Non si tiene: la plancia, o Aggiorna, la riprova.
            self.non_risponde(cartella)
            self._parziale = True
            return [], []
        except OSError as errore:
            if rete and errore_di_rete(errore):
                # La rete che manca subito, come il router che si riavvia: come
                # una cartella che tace, e non si tiene come vuota (revisione
                # della 1.85.5).
                self.non_risponde(cartella)
                self._parziale = True
                return [], []
            lettura = ([], [])
        # Sotto il lucchetto: chi dimentica scorre le letture da un altro filo.
        with self._lucchetto:
            self._letture[cartella] = lettura
        return lettura

    def _conta(self, cartella):
        """Il conto di una cartella, con una pila e non con la ricorsione:
        gli alberi delle collezioni possono essere molto profondi."""
        if cartella in self.conti:
            return self.conti[cartella]
        files = []
        pila = [cartella]
        while pila and not self._fermo:
            self._cedi_il_passo()
            attuale = pila.pop()
            # Un conto gia' fatto si riusa; .get, perche' un'altra mano puo'
            # dimenticarlo nel frattempo.
            fatto = self.conti.get(attuale) if attuale != cartella else None
            if fatto is not None:
                files.extend(fatto)
                # Chi riusa un conto parziale e' parziale anche lui (1.85.5).
                if attuale in self.parziali:
                    self._parziale = True
                continue
            sottocartelle, propri = self._lettura(attuale)
            files.extend(propri)
            pila.extend(reversed(sottocartelle))
        return files

    def _lavora(self):
        ultimo = time.monotonic()
        while not self._fermo:
            self._cedi_il_passo()
            try:
                cartella = self._coda.get(timeout=0.5)
            except queue.Empty:
                break
            with self._lucchetto:
                visti = len(self._cambiate)
                rinate = len(self._rinate)
                azzerati = len(self._azzeramenti)
            self._parziale = False
            files = self._conta(cartella)
            if self._fermo:
                break
            rete = in_rete(cartella)
            with self._lucchetto:
                chiave = cartella.rstrip("\\").lower()
                cambiata = any(c == chiave or c.startswith(chiave + "\\") for c in self._cambiate[visti:])
                # Un Aggiorna che ha dimenticato tutto, o la rete, mentre si
                # contava: il conto e' di prima, e si rifa'.
                cambiata = cambiata or any(a == "tutto" or (a == "rete" and rete) for a in self._azzeramenti[azzerati:])
                # Un conto parziale fatto mentre la sua radice tornava viva ha
                # saltato cartelle che adesso si leggono (revisione della 1.85.5).
                rinata = self._parziale and _radice(cartella) in self._rinate[rinate:]
                if cambiata or rinata:
                    # Intanto qualcosa li' dentro e' cambiato: il conto si rifa'.
                    self._coda.put(cartella)
                    continue
                self.conti[cartella] = files
                if self._parziale:
                    self.parziali.add(cartella)
                else:
                    self.parziali.discard(cartella)
                self._in_coda.discard(cartella)
                if self._coda.empty():
                    self._cambiate.clear()
                    self._rinate.clear()
                    self._azzeramenti.clear()
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


def _radice(cartella):
    """La radice di un percorso, come \\\\server\\cartella o E:, minuscola."""
    return os.path.splitdrive(cartella)[0].lower()


def _chiave(cartella):
    """Una cartella come chiave: minuscola, senza la barra in fondo."""
    return cartella.rstrip("\\").lower()
