# MeTeOra, la ricerca globale: cerca con il filtro in tutte le playlist e in tutte le unita'.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la 1.15.0, issue 10. Nella 1.23.0 l'albero della provenienza dei risultati; nella 1.34.6 i risultati cestinati escono dal ramo.
# Nella 1.73.0 la ricerca ovunque anche in rete, dopo i dischi, con le letture di rete a tempo.

"""La ricerca in tutto MeTeOra.

Usa la grammatica del filtro. Cerca prima nei Preferiti e nelle playlist,
poi nelle unita' di Questo PC, dischi e chiavette, e per ultime nelle radici
di rete che riceve, cioe' le unita' di rete e i percorsi aggiunti a mano in
Questa rete; salta i CD, che possono essere lentissimi o vuoti. In rete ogni
cartella si legge in un filo a parte, con un tempo massimo fra una voce e
l'altra: il Samba dell'Iliadbox, percorso tutto, dopo circa 17 mila cartelle
lascia appesa una lettura per venti minuti e piu' (banco del 4 ottobre 2026).
Allora si tenta di annullarla, in un filo usa e getta perche' anche
l'annullamento puo' restare fermo, e la cartella si salta; alla terza cartella
muta, o se tace la radice stessa, si salta tutta la radice, ricordandola in
senza_risposta, come una radice che risponde subito con un errore. I file sul disco li giudica con
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

import questa_rete
import questo_pc
from playlist import Brano

# I tipi di unita' in cui si cerca: rimovibili, dischi fissi, dischi in memoria.
UNITA_DA_CERCARE = (2, 3, 6)
UNITA_DI_RETE = 4
INTERVALLO_DEGLI_AVVISI = 0.5
# Quanti secondi aspetta, fra una voce e l'altra, la lettura di una cartella
# di rete prima di darla per persa: abbastanza per un disco del router che si
# risveglia (1.73.0).
ATTESA_IN_RETE = 15.0
# Dopo quante cartelle mute si lascia perdere tutta la radice: ognuna lascia
# un filo appeso, quindi non si insiste.
CARTELLE_MUTE = 3


def _tipo_di_unita(radice):
    import ctypes

    return ctypes.windll.kernel32.GetDriveTypeW(radice)


def in_rete(percorso):
    r"""Vero per un percorso di rete, come \\server\cartella, o su un'unita' di rete."""
    return questa_rete.e_di_rete(percorso) or _tipo_di_unita(os.path.splitdrive(percorso)[0] + "\\") == UNITA_DI_RETE


def _percorso_di_rete(radice):
    """Il percorso \\\\server\\cartella a cui porta un'unita' di rete con la
    lettera, o la radice com'e'."""
    import ctypes
    from ctypes import wintypes

    unita, resto = os.path.splitdrive(radice)
    if not unita.endswith(":"):
        return radice
    spazio = ctypes.create_unicode_buffer(1024)
    lunghezza = wintypes.DWORD(1024)
    if ctypes.WinDLL("mpr").WNetGetConnectionW(unita, spazio, ctypes.byref(lunghezza)) != 0:
        return radice
    return spazio.value + resto


def senza_annidati(radici):
    """Le radici senza i doppioni e senza quelle che stanno dentro un'altra:
    la stessa cartella si cerca una volta sola, anche se arriva da un'unita'
    di rete e da un percorso salvato."""
    chiavi = [os.path.normcase(_percorso_di_rete(r)).rstrip("\\") + "\\" for r in radici]
    tenute = []
    for i, radice in enumerate(radici):
        dentro = any(j != i and chiavi[i].startswith(chiavi[j]) and (chiavi[i] != chiavi[j] or j < i) for j in range(len(radici)))
        if not dentro:
            tenute.append(radice)
    return tenute


def lettere_di_rete():
    """Le radici delle unita' di rete con la lettera, come Z:\\, senza
    chiedere il nome del volume, che su un server fermo si fa aspettare."""
    import ctypes

    maschera = ctypes.windll.kernel32.GetLogicalDrives()
    radici = [f"{chr(65 + i)}:\\" for i in range(26) if maschera >> i & 1]
    return [r for r in radici if _tipo_di_unita(r) == UNITA_DI_RETE]


def radici_di_rete(percorsi):
    """Le radici di rete della ricerca ovunque: i percorsi dati, cioe' quelli
    aggiunti a mano in Questa rete, e le unita' di rete con la lettera, senza
    doppioni. Si chiama nel filo della ricerca."""
    return senza_annidati(list(percorsi) + lettere_di_rete())


def _annulla_la_lettura(filo, per_quanto=3.0):
    """Annulla la lettura su cui il filo e' fermo, con CancelSynchronousIo:
    senza, un filo bloccato su una condivisione che tace resta li' finche'
    Windows non si arrende. Se il server ignora l'annullamento, questa
    chiamata resta ferma anche lei: va fatta in un filo a parte. Si ripete
    finche' il filo e' vivo, per per_quanto secondi: un annullamento che arriva
    fra una lettura e l'altra non vale per quella dopo."""
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32")
    kernel32.OpenThread.restype = wintypes.HANDLE
    kernel32.OpenThread.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.CancelSynchronousIo.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    # 1 e' THREAD_TERMINATE, il permesso che CancelSynchronousIo chiede.
    maniglia = kernel32.OpenThread(1, False, filo.native_id or 0)
    if not maniglia:
        return
    try:
        scadenza = time.monotonic() + per_quanto
        while filo.is_alive() and time.monotonic() < scadenza:
            kernel32.CancelSynchronousIo(maniglia)
            filo.join(0.05)
    finally:
        kernel32.CloseHandle(maniglia)


class NonRisponde(OSError):
    """Una cartella di rete che non ha risposto in tempo. E' un OSError: chi
    tratta una cartella illeggibile la tratta gia' bene anche cosi'."""


_NonRisponde = NonRisponde

# Gli errori di Windows che vengono dalla rete, e non dalla cartella: il
# percorso o il nome di rete che non si trova, la connessione caduta, rifiutata
# o irraggiungibile, il server che non c'e'. Una cartella di rete che ne da' uno
# si tratta come una che tace: si riprova (revisione della 1.85.5).
ERRORI_DI_RETE = frozenset({51, 53, 54, 59, 64, 67, 121, 1222, 1231, 1232, 1236})


def errore_di_rete(errore):
    """Vero per un errore che dice che manca la rete, non la cartella: uno di
    ERRORI_DI_RETE, o una lettura interrotta senza un errore di Windows."""
    codice = getattr(errore, "winerror", None)
    return codice is None or codice in ERRORI_DI_RETE


def leggi_in_rete(cartella, fermo=None, attesa=None):
    """Il contenuto di una cartella di rete, come questo_pc.contenuto, letto
    in un filo a parte: se per attesa secondi, ATTESA_IN_RETE se non si dice,
    non arriva nemmeno una voce, la lettura si annulla, in un altro filo
    perche' anche l'annullamento puo' restare fermo, e si solleva
    NonRisponde; una cartella grande che risponde a blocchi non scade.
    fermo, se c'e', si chiede mentre si aspetta: vero, e si torna subito con
    ([], []). La usano la ricerca, il contatore e la plancia (1.77.1)."""
    attesa = ATTESA_IN_RETE if attesa is None else attesa
    esito = []
    passo = [time.monotonic()]

    def al_passo():
        passo[0] = time.monotonic()

    def leggi():
        try:
            esito.append(questo_pc.contenuto(cartella, al_passo=al_passo))
        except Exception as errore:  # noqa: BLE001 - torna a chi aspetta, che lo solleva
            esito.append(errore)

    filo = threading.Thread(target=leggi, name="MeTeOra, lettura in rete", daemon=True)
    filo.start()
    while filo.is_alive() and not (fermo is not None and fermo()) and time.monotonic() - passo[0] < attesa:
        filo.join(0.1)
    if filo.is_alive():
        threading.Thread(target=_annulla_la_lettura, args=(filo,), name="MeTeOra, annullamento in rete", daemon=True).start()
        if fermo is not None and fermo():
            return [], []
        raise NonRisponde(cartella)
    if not esito:
        raise OSError(f"La lettura di {cartella} si e' interrotta.")
    if isinstance(esito[0], Exception):
        raise esito[0]
    return esito[0]


class Ricerca:
    def __init__(self, filtro, brani_delle_playlist, schedario, avvisa=None, unita=None, rete=(), lettere_di_rete=False):
        """brani_delle_playlist: coppie (brano, nome della playlist) dei
        Preferiti e delle playlist, da guardare per primi; unita: le radici da
        cercare, se si vogliono diverse da quelle di Questo PC, per esempio
        nelle prove; rete: le radici di rete da cercare per ultime, a cui
        lettere_di_rete aggiunge le unita' di rete con la lettera."""
        self.filtro = filtro
        self._brani = list(brani_delle_playlist)
        self._schedario = schedario
        self._avvisa = avvisa
        self._unita = unita
        self._rete = list(rete)
        self._lettere_di_rete = lettere_di_rete
        # Le radici di rete saltate perche' non rispondevano, e le cartelle
        # mute saltate dentro radici che invece rispondevano.
        self.senza_risposta = []
        self.cartelle_mute = []
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
        rete = radici_di_rete(self._rete) if self._lettere_di_rete else self._rete
        for radice in [*radici, *rete]:
            self._cerca_in(radice)
            if self.fermata:
                return
        self.finita = True
        if self._avvisa:
            self._avvisa()

    def _cerca_in(self, cartella):
        di_rete = in_rete(cartella)
        mute = []
        pendenti = [cartella]
        while pendenti and not self.fermata:
            attuale = pendenti.pop()
            try:
                cartelle, files = self._leggi_in_rete(attuale) if di_rete else questo_pc.contenuto(attuale)
            except _NonRisponde:
                mute.append(attuale)
                if attuale == cartella or len(mute) >= CARTELLE_MUTE:
                    # La radice intera si dice da sola, senza le sue cartelle.
                    self.cartelle_mute = [m for m in self.cartelle_mute if m not in mute]
                    self.senza_risposta.append(cartella)
                    return
                self.cartelle_mute.append(attuale)
                continue
            except OSError:
                # Una radice di rete che risponde subito con un errore, come
                # un server spento, si dice come una che tace.
                if di_rete and attuale == cartella:
                    self.senza_risposta.append(cartella)
                continue
            for percorso in files:
                if self.fermata:
                    return
                brano = Brano(percorso)
                if self.filtro.ammette(brano, self._schedario.scheda(percorso)):
                    self._trovato(brano)
            # In ordine alfabetico: le cartelle si prendono dalla fine della pila.
            pendenti.extend(reversed(cartelle))

    def _leggi_in_rete(self, cartella):
        """La lettura protetta di una cartella di rete; ferma() vale subito."""
        return leggi_in_rete(cartella, fermo=lambda: self.fermata)


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

