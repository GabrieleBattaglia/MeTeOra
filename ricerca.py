# MeTeOra, la ricerca globale: cerca con il filtro in tutte le playlist e in tutte le unita'.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la 1.15.0, issue 10. Nella 1.23.0 l'albero della provenienza dei risultati; nella 1.34.6 i risultati cestinati escono dal ramo.

"""La ricerca in tutto MeTeOra.

Usa la grammatica del filtro. Cerca prima nei Preferiti e nelle playlist,
poi nelle unita' di Questo PC, dischi e chiavette; salta le unita' di rete e
i CD, che possono essere lentissimi o vuoti. I file sul disco li giudica con
la scheda dello schedario, se c'e': un file mai visto si conosce solo per il
nome e il percorso, quindi i comandi su durata e tag non lo trovano.
Il lavoro lo fa un filo a parte, che si puo' fermare; chi aspetta viene
avvisato al massimo due volte al secondo e alla fine.
Ogni risultato ricorda la sua provenienza: il nome della playlist in cui
l'ha trovato, o None se viene dal disco. AlberoDeiRisultati li ordina come
stanno: sotto la loro playlist, o lungo il percorso della loro cartella,
unita' per unita' e cartella per cartella.
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
        """brani_delle_playlist: coppie (brano, nome della playlist) dei
        Preferiti e delle playlist, da guardare per primi; unita: le radici da
        cercare, se si vogliono diverse da quelle di Questo PC, per esempio
        nelle prove."""
        self.filtro = filtro
        self._brani = list(brani_delle_playlist)
        self._schedario = schedario
        self._avvisa = avvisa
        self._unita = unita
        self.risultati = []
        self.origini = []
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
        """I risultati da inizio a fine, come coppie (brano, provenienza)."""
        with self._lucchetto:
            return list(zip(self.risultati[inizio:fine], self.origini[inizio:fine], strict=True))

    def _trovato(self, brano, origine=None):
        chiave = (os.path.normcase(brano.percorso), brano.sottobrano)
        if chiave in self._visti:
            return
        self._visti.add(chiave)
        with self._lucchetto:
            self.risultati.append(Brano(brano.percorso, sottobrano=brano.sottobrano))
            self.origini.append(origine)
        adesso = time.monotonic()
        if self._avvisa and adesso - self._ultimo_avviso >= INTERVALLO_DEGLI_AVVISI:
            self._ultimo_avviso = adesso
            self._avvisa()

    def _lavora(self):
        for brano, playlist in self._brani:
            if self.fermata:
                return
            if self.filtro.ammette(brano, self._schedario.scheda(brano.percorso)):
                self._trovato(brano, playlist)
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


class Gruppo:
    """Un ramo dell'albero dei risultati: una playlist, un'unita' o una
    cartella, con i rami che contiene e i suoi risultati."""

    def __init__(self, nome, genitore=None):
        self.nome = nome
        self.genitore = genitore
        self.gruppi = {}
        self.brani = []
        # I risultati di questo ramo e di tutti quelli che contiene.
        self.totale = 0

    def gruppo(self, nome):
        if nome not in self.gruppi:
            self.gruppi[nome] = Gruppo(nome, self)
        return self.gruppi[nome]

    @property
    def elenco_dei_gruppi(self):
        return list(self.gruppi.values())


class AlberoDeiRisultati:
    """I risultati ordinati per provenienza. nomi_delle_unita traduce la
    radice di un'unita', come E:\\, nel nome che ha in Questo PC."""

    def __init__(self, nomi_delle_unita=None):
        self.radice = Gruppo("Risultati")
        self._nomi = {os.path.normcase(k): v for k, v in (nomi_delle_unita or {}).items()}
        self.gruppo_del_brano = {}

    def aggiungi(self, brano, playlist=None):
        """Mette il brano nel suo ramo e lo restituisce."""
        if playlist is not None:
            # Il nome del ramo lo decide chi cerca: Preferiti, Playlist Rock...
            gruppi = [playlist]
        else:
            cartella = os.path.dirname(brano.percorso)
            unita, resto = os.path.splitdrive(cartella)
            radice = unita + "\\"
            gruppi = [self._nomi.get(os.path.normcase(radice), radice)] + [p for p in resto.split("\\") if p]
        gruppo = self.radice
        gruppo.totale += 1
        for nome in gruppi:
            gruppo = gruppo.gruppo(nome)
            gruppo.totale += 1
        gruppo.brani.append(brano)
        self.gruppo_del_brano[id(brano)] = gruppo
        return gruppo

    def togli(self, brano):
        """Toglie il brano dal suo ramo, per esempio perche' il suo file e'
        andato nel cestino, e lo sconta dai totali. Torna (ramo, posizione
        che aveva), o None se non c'era."""
        gruppo = self.gruppo_del_brano.pop(id(brano), None)
        if gruppo is None:
            return None
        indice = next((i for i, b in enumerate(gruppo.brani) if b is brano), None)
        if indice is None:
            return None
        del gruppo.brani[indice]
        ramo = gruppo
        while ramo is not None:
            ramo.totale -= 1
            ramo = ramo.genitore
        return gruppo, indice

    def catena(self, gruppo):
        """I rami dalla radice esclusa fino al gruppo compreso."""
        catena = []
        while gruppo is not None and gruppo is not self.radice:
            catena.append(gruppo)
            gruppo = gruppo.genitore
        return list(reversed(catena))

