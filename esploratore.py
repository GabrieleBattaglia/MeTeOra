# MeTeOra, l'esploratore delle aperture di massa: legge in disparte i rami del disco e della rete da aprire.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/11/2026: nasce con la 2.7.0, tappa 17 del piano.

"""L'apertura di massa dei rami del disco e della rete (2.7.0).

Maiuscolo con F9 apre un ramo con tutto quello che ha dentro, Alt con F9
tutta la plancia. Fino alla 2.6 lo facevano a fette nel filo della finestra,
che leggeva ogni cartella e la mostrava prima di sapere se aveva qualcosa da
suonare: il disco C del gigante ha 259.808 cartelle e solo 914 con musica, e
la finestra si fermava. Per questo c'erano i limiti di 2000 rami e 10000
voci, e Questo PC e Questa rete restavano chiusi.

L'esploratore legge in un filo a parte, in ordine alfabetico come la
ricerca, e alla finestra annuncia solo le cartelle con qualcosa da suonare,
dentro di loro o piu' sotto: una cartella si annuncia quando vi si trova il
primo file, insieme alle cartelle che la contengono e che non si erano
ancora annunciate. Visitando in ordine, una cartella nuova arriva sempre dopo
le sorelle gia' annunciate. Gli avvisi, nell'ordine in cui si prendono:
("cartella", genitore, percorso), una cartella da mostrare dentro genitore;
("file", cartella, lettura), la lettura (cartelle, file) di una cartella
annunciata che ha dei file;
("finita", cartella), una cartella annunciata e letta tutta, con quello che
ha sotto.
Ogni lettura va anche al contatore, che cosi' non rilegge. Le intestazioni
dei SID e dei file delle console si leggono qui: la plancia, che ne ha
bisogno per farne dei rami, le trova pronte. In rete la lettura e' quella
protetta della ricerca: una cartella che tace si salta, e alla terza, o se
tace la radice, si salta tutta la radice. Chi aspetta viene avvisato al
massimo due volte al secondo e alla fine.
"""

import threading
import time

import formati
import questo_pc
import sottobrani
from ricerca import CARTELLE_MUTE, NonRisponde, errore_di_rete, in_rete, leggi_in_rete

INTERVALLO_DEGLI_AVVISI = 0.5
# Quanto aspetta il filo, a ogni giro, mentre deve cedere il passo alla finestra.
PAUSA_PER_CEDERE = 0.005


class Esploratore:
    def __init__(self, radici, contatore=None, avvisa=None, cedi=None):
        """radici: le cartelle da aprire, nell'ordine; contatore riceve le
        letture; avvisa() si chiama dal filo quando ci sono avvisi da
        prendere; cedi, un threading.Event, quando e' alzato fa aspettare il
        filo, perche' la finestra sta lavorando."""
        self._radici = list(radici)
        self._contatore = contatore
        self._avvisa = avvisa
        self._cedi = cedi
        self._eventi = []
        self._lucchetto = threading.Lock()
        self._ultimo_avviso = 0.0
        # I conti, per chi chiede a che punto si e'.
        self.lette = 0
        self.annunciate = 0
        self.file = 0
        self.illeggibili = 0
        # Le cartelle di rete saltate perche' tacevano, e le radici di rete
        # lasciate perdere.
        self.cartelle_mute = []
        self.senza_risposta = []
        # La cartella che si sta leggendo adesso.
        self.in_lettura = None
        self.finita = False
        self.fermata = False
        self._filo = threading.Thread(target=self._lavora, name="MeTeOra, esploratore", daemon=True)

    def avvia(self):
        self._filo.start()
        return self

    def ferma(self):
        self.fermata = True
        if self._filo.is_alive():
            self._filo.join(timeout=2)

    def aspetta(self, secondi=60):
        """Per le prove."""
        self._filo.join(timeout=secondi)

    def prendi(self):
        """Gli avvisi arrivati dall'ultima volta, in ordine."""
        with self._lucchetto:
            eventi, self._eventi = self._eventi, []
        return eventi

    # Dietro le quinte.

    def _lavora(self):
        try:
            for radice in self._radici:
                if self.fermata:
                    break
                self._esplora(radice)
        finally:
            self.in_lettura = None
            self.finita = True
            if self._avvisa is not None and not self.fermata:
                self._avvisa()

    def _cedi_il_passo(self):
        while self._cedi is not None and self._cedi.is_set() and not self.fermata:
            time.sleep(PAUSA_PER_CEDERE)

    def _metti(self, evento):
        with self._lucchetto:
            self._eventi.append(evento)

    def _forse_avvisa(self):
        """Avvisa se ci sono avvisi da prendere e l'ultimo avviso e' abbastanza
        lontano: si chiama a ogni cartella, anche dove non si annuncia niente,
        cosi' un avviso rimasto indietro non aspetta la fine."""
        if self._avvisa is None or time.monotonic() - self._ultimo_avviso < INTERVALLO_DEGLI_AVVISI:
            return
        with self._lucchetto:
            vuoti = not self._eventi
        if not vuoti:
            self._ultimo_avviso = time.monotonic()
            self._avvisa()

    def _leggi(self, cartella, di_rete):
        self.in_lettura = cartella
        if di_rete:
            return leggi_in_rete(cartella, fermo=lambda: self.fermata)
        return questo_pc.contenuto(cartella)

    def _esplora(self, radice):
        """Una radice, in profondita' e in ordine alfabetico, con una pila e non
        con la ricorsione: gli alberi delle collezioni sono profondi. Nella
        pila ogni cartella entra due volte: per leggerla e, dopo tutto quello
        che ha sotto, per dirla finita."""
        di_rete = in_rete(radice)
        mute = []
        annunciate = {radice}
        genitori = {radice: None}
        pila = [(True, radice)]
        while pila and not self.fermata:
            self._cedi_il_passo()
            self._forse_avvisa()
            entra, cartella = pila.pop()
            if not entra:
                genitori.pop(cartella, None)
                if cartella in annunciate:
                    annunciate.discard(cartella)
                    self._metti(("finita", cartella))
                continue
            try:
                lettura = self._leggi(cartella, di_rete)
            except OSError as errore:
                genitori.pop(cartella, None)
                if di_rete and (isinstance(errore, NonRisponde) or errore_di_rete(errore)):
                    mute.append(cartella)
                    if self._contatore is not None:
                        self._contatore.non_risponde(cartella)
                    if cartella == radice or len(mute) >= CARTELLE_MUTE:
                        # La radice intera si dice da sola, senza le sue cartelle.
                        self.cartelle_mute = [m for m in self.cartelle_mute if m not in mute]
                        self.senza_risposta.append(radice)
                        return
                    self.cartelle_mute.append(cartella)
                    continue
                self.illeggibili += 1
                if cartella == radice:
                    return
                continue
            if self.fermata:
                return
            self.lette += 1
            sottocartelle, files = lettura
            if self._contatore is not None:
                if di_rete and cartella == radice:
                    # La radice ha risposto: i conti che l'avevano saltata si rifanno.
                    self._contatore.chiedi(self._contatore.risponde(radice))
                self._contatore.chiedi(self._contatore.rinfresca(cartella, lettura))
            for percorso in files:
                if self.fermata:
                    return
                if formati.ha_sottobrani(percorso):
                    sottobrani.info(percorso)
            if files:
                catena = []
                attuale = cartella
                while attuale not in annunciate:
                    catena.append(attuale)
                    attuale = genitori[attuale]
                for annunciata in reversed(catena):
                    self._metti(("cartella", genitori[annunciata], annunciata))
                    annunciate.add(annunciata)
                    self.annunciate += 1
                self._metti(("file", cartella, lettura))
                self.file += len(files)
            pila.append((False, cartella))
            # In ordine alfabetico: le cartelle si prendono dalla fine della pila.
            for sotto in reversed(sottocartelle):
                genitori[sotto] = cartella
                pila.append((True, sotto))
