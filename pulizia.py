# MeTeOra, la pulizia all'avvio: quali dei file che MeTeOra conosce non ci sono piu' sul disco.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 19/10/2026: nasce con la 1.104.0, perche' schedario, playlist, Preferiti, marker, punti da riprendere e statistiche non si portino dietro per sempre i file spariti. Nella 1.112.0 la protezione dei dischi: la pulizia riconosce il disco di ogni lettera, anche di quelle fatte con subst, e salta una lettera usata da dischi diversi o con un disco che non riconosce, e tutte quando il file dei dischi non si legge; poi Riconosci questo disco, il controllo dei dischi quando MeTeOra usa un file, con la Sentinella, e i dischi di ogni computer tenuti a parte; infine il conto delle voci per la conferma di Riconosci questo disco, e il MachineGuid accanto al nome del computer.

"""La pulizia all'avvio, la parte senza wx.

controlla riceve i percorsi che MeTeOra conosce e dice quali mancano; la
finestra poi toglie le loro voci. Le regole, decise con Gabriele:
- I percorsi si confrontano nella forma di norm, la stessa in tutti i moduli
  che tolgono i mancanti.
- Si guardano solo i percorsi assoluti, con l'unita' o la condivisione: uno
  relativo, come brano.mp3 arrivato dalla riga di comando, si risolverebbe
  con la cartella di lavoro, che non e' detto sia la sua, e resta senza
  controllo.
- Si raggruppano per radice, un'unita' con la lettera o una condivisione di
  rete, e per cartella, senza doppioni. Ogni radice si prova una volta: una
  che non risponde si salta, e le sue voci restano per il prossimo avvio.
  Si guardano anche le unita' rimovibili, se rispondono.
- Di ogni cartella si legge un solo elenco, e i nomi si confrontano senza
  badare alle maiuscole. Un file manca se il suo nome non e' nell'elenco, o
  se la sua cartella non c'e' piu'. Una cartella si da' per sparita solo se
  lo conferma l'elenco della prima cartella sopra che si e' letta: se ha il
  suo nome, la cartella c'e' ma non si legge, come una giunzione o un disco
  montato in una cartella che portano a un disco staccato, o un percorso
  troppo lungo, e le sue voci restano senza controllo. Anche ogni altro
  errore lascia le voci come sono. Dagli elenchi delle cartelle sopra si
  leggono anche le maiuscole vere: nomi_veri serve alla finestra per
  togliere i doppioni dello schedario che differiscono solo per come sono
  scritti.
- In rete il giro di una radice si fa in un filo a parte, sorvegliato come
  ricerca.leggi_in_rete: il Samba dell'Iliadbox puo' lasciare appesa una
  lettura per venti minuti. Se per attesa secondi il giro non va avanti, la
  lettura si annulla e la radice si salta.
- Alla fine del giro la radice si riprova: se non risponde piu', i suoi
  mancanti si buttano, perche' una rete caduta a meta' non deve far
  togliere niente.
- I dischi (1.112.0, Gabriele): le voci tolte devono essere di file
  davvero inutilizzabili, e un'altra chiavetta nella stessa lettera non ha i
  file di quella di prima, che sono solo staccati. Per questo la pulizia
  riconosce chi risponde a ogni lettera, con _identita: per le unita' del PC,
  dischi fissi e rimovibili, CD e dischi in memoria, il numero di serie del
  volume; per le unita' di rete con la lettera, la condivisione a cui
  portano, perche' in rete il numero di serie non e' affidabile e chiederlo
  potrebbe restare appeso come una lettura. Una condivisione scritta per
  esteso, con il nome del server, si riconosce dal nome. Una lettera fatta
  con subst si riconosce dalla cartella a cui porta, con il numero di serie
  del volume se la cartella e' sul PC, o con la condivisione se e' su
  un'unita' di rete con la lettera: spostata su un'altra cartella dello
  stesso volume, avrebbe lo stesso numero. Ogni lettera ha il suo ricordo in
  Dischi: il suo disco, gli altri che ci hanno risposto e, finche' non ha un
  disco suo, quello visto mentre MeTeOra usava i suoi file. I ricordi sono
  di ogni computer per conto suo, perche' i dischi fissi di un altro hanno
  altri numeri di serie (Gabriele), sotto il suo nome, con accanto il
  MachineGuid di Windows: un computer che cambia nome ritrova i suoi.
  La prima volta che incontra una lettera, la pulizia ne fa suo il disco
  solo se ci trova almeno la meta' dei file che ha potuto controllare: le
  voci dei file spariti si tolgono a ogni avvio, e sul disco giusto c'e'
  quasi tutto, mentre un disco qualunque non ha i file di un altro. Se no
  quel disco non e' il suo, e la lettera e' contesa. Contesa diventa anche
  una lettera a cui risponde un disco diverso dal suo, o da quello visto
  prima, o che cambia disco a meta' giro. Una lettera contesa si salta
  prima di leggere le sue cartelle, e le sue voci restano, anche quando
  torna il suo disco: sono mescolate a quelle dell'altro, e nessuna si puo'
  dare per persa. Si sblocca solo a mano, con Riconosci questo disco nel
  menu dell'unita' in Questo PC (Gabriele): da li' la lettera e' del disco
  che risponde, e la pulizia dopo la controlla. Prima di farlo il comando
  chiede conferma, con il conto delle voci che la pulizia togliera':
  conta_le_voci lo fa in disparte, leggendo le cartelle come la pulizia. La
  riga della finestra dice usata da dischi diversi solo se alla lettera ne
  hanno risposto almeno due, fra il suo e gli altri, e solo per queste
  suggerisce Riconosci questo disco; con un disco solo, che non e' mai stato
  il suo, dice soltanto che non lo riconosce. Non riconosciuta e' anche una
  lettera di cui non si legge chi risponde, che si salta senza ricordare
  niente, e ogni lettera quando il file dei dischi non si legge: senza i
  ricordi una contesa sembrerebbe nuova, e la regola della prima volta
  toglierebbe le voci di uno dei suoi dischi.
  La pulizia vede chi risponde solo all'avvio; a MeTeOra aperto guarda la
  Sentinella, ogni volta che MeTeOra usa un file di una lettera: lo suona,
  lo aggiunge a una playlist o ai Preferiti, lo legge lo schedario o ne
  apre la cartella nella plancia (Gabriele). Un disco diverso da quello
  ricordato rende la lettera contesa, e una chiavetta infilata e tolta a
  sessione aperta non sfugge piu'; la finestra lo dice subito, una volta
  per lettera e per disco. Anche due chiavette usate nella stessa
  lettera prima che la pulizia la conosca la rendono contesa: la regola
  della meta' resta per le voci di dischi che MeTeOra non ha mai visto, come
  quelle scritte prima della 1.112.0. Una lettera che la Sentinella rende
  contesa mentre la pulizia lavora tiene anche le voci che la pulizia ci ha
  trovato mancanti: la finestra, che le toglie, guarda i dischi di quel
  momento. Le tiene anche una lettera riconosciuta a mano intanto, perche'
  la pulizia puo' averla letta con un altro disco.
- Prima di ogni cartella si cede il passo alla finestra, se lo chiede, e si
  smette se chi aspetta ha fermato la pulizia.
Pulizia fa il lavoro in un filo a parte e passa l'esito a finita, nel suo
filo: chi la usa lo riporta in quello della finestra.
"""

import contextlib
import copy
import ctypes
import json
import ntpath
import os
import platform
import threading
import time
import traceback
from collections import Counter
from ctypes import wintypes

import questa_rete
import ricerca

# I codici di Windows con cui una cartella dice di non esserci: il file e il
# percorso che non si trovano.
ERRORI_DI_MANCANZA = frozenset({2, 3})
# Quanto aspetta il filo, a ogni giro, mentre deve cedere il passo: come lo schedario.
PAUSA_PER_CEDERE = 0.005
# Ogni quanti percorsi, mentre si raggruppano, si guarda se cedere il passo.
GRUPPO_FRA_UNA_PAUSA_E_L_ALTRA = 500
# SEM_FAILCRITICALERRORS: un'unita' senza disco risponde con un errore,
# senza la finestra di Windows. Si imposta con SetThreadErrorMode, che vale
# solo per il filo che la chiama: SetErrorMode vale per tutto il processo, e
# la pulizia, che la imposta e la ripristina migliaia di volte, la
# cambierebbe anche sotto questo_pc._nome_del_volume, nel filo della finestra.
_SENZA_FINESTRE_DI_ERRORE = 0x0001
# I tipi di unita' di GetDriveTypeW che sono del PC, e che si riconoscono dal
# numero di serie del volume: rimovibili, dischi fissi, CD e dischi in
# memoria (1.112.0). Quelle di rete, il 4, si riconoscono dalla
# condivisione a cui portano.
UNITA_DEL_PC = frozenset({2, 3, 5, 6})
# Quanta parte dei file controllati deve esserci perche' la pulizia faccia
# suo il disco di una lettera che incontra la prima volta (1.112.0).
PARTE_PER_RICONOSCERE = 0.5
# Come comincia, per QueryDosDeviceW, il bersaglio di una lettera fatta con
# subst, come \??\E:\Musica; quello di un volume e' come
# \Device\HarddiskVolume3, e quello di un'unita' di rete porta il numero
# della sessione di Windows, che cambia (1.112.0).
PREFISSO_DI_SUBST = "\\??\\"
# Per quanti secondi la Sentinella si fida di chi ha appena visto rispondere
# a una lettera: una domanda a Windows per lettera, non per file. MeTeOra non
# riceve WM_DEVICECHANGE, e niente avvisa di un disco cambiato; ma cambiare
# chiavetta, fra toglierla, infilare l'altra e aspettare che Windows la
# monti, chiede piu' di cosi' (1.112.0).
MEMORIA_DELLA_SENTINELLA = 5.0


def norm(percorso):
    """La forma in cui i moduli della pulizia confrontano i percorsi:
    assoluta, in minuscolo e con le barre di Windows."""
    return os.path.normcase(os.path.abspath(percorso))


def _mai():
    return False


def _niente():
    pass


@contextlib.contextmanager
def _senza_finestre_di_errore():
    """Come in questo_pc: un'unita' vuota, per esempio un lettore di schede
    senza la scheda, non deve far comparire la finestra di errore di Windows.
    Vale solo per il filo che la usa."""
    kernel32 = ctypes.windll.kernel32
    vecchia = wintypes.DWORD()
    impostata = kernel32.SetThreadErrorMode(_SENZA_FINESTRE_DI_ERRORE, ctypes.byref(vecchia))
    try:
        yield
    finally:
        if impostata:
            kernel32.SetThreadErrorMode(vecchia.value, None)


def _cedi_il_passo(cedi, fermo, al_passo=_niente):
    """Finche' la finestra chiede il passo, si aspetta; al_passo dice a chi
    sorveglia che il filo non e' appeso. fermo() fa smettere di aspettare."""
    while cedi is not None and cedi.is_set() and not fermo():
        al_passo()
        time.sleep(PAUSA_PER_CEDERE)


def _risponde(radice):
    r"""Vero se la radice, come E: o \\server\condivisione, risponde: in rete
    con questa_rete.raggiungibile, che smette di aspettare da sola; le unita'
    del PC senza la finestra di errore di Windows."""
    if ricerca.in_rete(radice):
        return questa_rete.raggiungibile(radice + "\\", attesa=questa_rete.ATTESA_IN_SOTTOFONDO)
    with _senza_finestre_di_errore():
        return os.path.isdir(radice + "\\")


def _tipo_di_unita(radice):
    """Il tipo di unita' di GetDriveTypeW di una lettera, come E:."""
    return ctypes.windll.kernel32.GetDriveTypeW(wintypes.LPCWSTR(radice + "\\"))


def _numero_di_serie(radice):
    """Il numero di serie del volume di un'unita' del PC, come E:, scritto
    come lo dice il comando vol, 1A2B-3C4D; "" se non si legge. Senza la
    finestra di errore di Windows, come _risponde."""
    seriale = wintypes.DWORD()
    with _senza_finestre_di_errore():
        riuscito = ctypes.windll.kernel32.GetVolumeInformationW(wintypes.LPCWSTR(radice + "\\"), None, 0, ctypes.byref(seriale), None, None,
            None, 0)
    if not riuscito:
        return ""
    return f"{seriale.value >> 16:04X}-{seriale.value & 0xFFFF:04X}"


def _condivisione(radice):
    r"""La condivisione a cui porta un'unita' di rete con la lettera, come
    \\server\condivisione, in minuscolo come la da' norm; "" se Windows non
    la dice. WNetGetConnectionW la legge dalle connessioni di Windows, come
    ricerca.senza_annidati."""
    spazio = ctypes.create_unicode_buffer(1024)
    lunghezza = wintypes.DWORD(len(spazio))
    if ctypes.WinDLL("mpr").WNetGetConnectionW(radice, spazio, ctypes.byref(lunghezza)) != 0 or not spazio.value:
        return ""
    return os.path.normcase(spazio.value).rstrip("\\")


def _bersaglio(radice):
    r"""Dove porta una lettera, come E:, per Windows, letto con
    QueryDosDeviceW: come \Device\HarddiskVolume3 per un volume, o come
    \??\E:\Musica per una lettera fatta con subst; "" se non si legge. Non
    tocca il disco ne' la rete."""
    spazio = ctypes.create_unicode_buffer(1024)
    if not ctypes.windll.kernel32.QueryDosDeviceW(wintypes.LPCWSTR(radice), spazio, len(spazio)):
        return ""
    return spazio.value


def _identita(radice):
    r"""Chi risponde alla radice, per riconoscerlo agli avvii dopo
    (1.112.0): per un'unita' del PC il numero di serie del volume, per
    una di rete con la lettera la condivisione a cui porta; "" se non si
    legge, o per un tipo di unita' che non si sa. None per una condivisione
    scritta per esteso, come \\server\condivisione, che si riconosce dal nome.
    Una lettera fatta con subst, che per Windows non e' una connessione di
    rete e ha il numero di serie del volume su cui porta, si riconosce dal
    suo bersaglio in minuscolo, come \??\e:\musica, seguito dal numero di
    serie se e' sul PC, o dalla condivisione se porta su un'unita' di rete
    con la lettera, come \??\z:\musica \\server\condivisione, perche' il
    numero di serie, in rete, non si chiede; o come
    \??\unc\server\condivisione se porta su una condivisione scritta per
    esteso."""
    if len(radice) != 2 or radice[1] != ":":
        return None
    bersaglio = _bersaglio(radice)
    if bersaglio.startswith(PREFISSO_DI_SUBST):
        bersaglio = os.path.normcase(bersaglio).rstrip("\\")
        destinazione = bersaglio[len(PREFISSO_DI_SUBST):len(PREFISSO_DI_SUBST) + 2].upper()
        if destinazione[1:] != ":":
            return bersaglio
        if _tipo_di_unita(destinazione) == ricerca.UNITA_DI_RETE:
            # Come l'unita' di rete su cui porta: dalla condivisione.
            condivisione = _condivisione(destinazione)
            return f"{bersaglio} {condivisione}" if condivisione else ""
        seriale = _numero_di_serie(radice)
        return f"{bersaglio} {seriale}" if seriale else ""
    tipo = _tipo_di_unita(radice)
    if tipo in UNITA_DEL_PC:
        return _numero_di_serie(radice)
    if tipo == ricerca.UNITA_DI_RETE:
        return _condivisione(radice)
    return ""


def _unisci(*ricordi):
    """Un ricordo solo dai ricordi della stessa lettera, presi in ordine,
    ognuno come {"disco": ..., "altri": [...], "visti": [...]} con le sole
    chiavi che servono, o None. Il disco e' il primo che c'e'; gli altri sono
    quelli di tutti, senza doppioni e senza il disco. I visti sono i dischi
    visti dalla Sentinella mentre MeTeOra usava i file di una lettera che non
    ha ancora un disco suo: restano visti solo se e' uno e la lettera non ha
    ne' un disco ne' altri; se no vanno fra gli altri, se diversi dal disco, e
    la lettera e' contesa. Torna un dizionario nuovo, senza le chiavi vuote:
    quelli dati non cambiano (1.112.0)."""
    ricordi = [ricordo or {} for ricordo in ricordi]
    disco = next((ricordo["disco"] for ricordo in ricordi if ricordo.get("disco")), None)
    contesa = any(ricordo.get("altri") for ricordo in ricordi)
    dischi = []
    for ricordo in ricordi:
        for chi in (*ricordo.get("altri", ()), *ricordo.get("visti", ())):
            if chi != disco and chi not in dischi:
                dischi.append(chi)
    if disco is None and not contesa and len(dischi) <= 1:
        return {"visti": dischi} if dischi else {}
    nuovo = {"disco": disco} if disco else {}
    if dischi:
        nuovo["altri"] = dischi
    return nuovo


def _contesa(ricordo, chi):
    """Il ricordo di una lettera dopo che ci ha risposto chi, che non e' il
    suo disco: chi va fra gli altri, con il disco visto prima, e la lettera
    e' contesa. ricordo e' quello di prima, come lo da' _unisci, o None.
    Torna un dizionario nuovo: quello di prima non cambia."""
    return _unisci(ricordo, {"altri": [chi]})


def _puo_essere_suo(ricordo, chi):
    """Vero se chi puo' essere il disco di una lettera con questo ricordo: la
    lettera non e' contesa, e chi e' il suo disco o, se non ne ha ancora
    uno, quello che la Sentinella ci ha visto (1.112.0)."""
    if ricordo.get("altri"):
        return False
    if ricordo.get("disco"):
        return ricordo["disco"] == chi
    return all(visto == chi for visto in ricordo.get("visti", ()))


def _manca(errore):
    """Vero se l'errore dice che la cartella non si trova, con uno dei codici
    di Windows di ERRORI_DI_MANCANZA. Un errore senza il codice, che potrebbe
    venire dalla rete, non vale, e nemmeno quelli della rete, che hanno altri
    codici. Se la cartella e' sparita davvero lo dice poi _sparita."""
    return isinstance(errore, (FileNotFoundError, NotADirectoryError)) and getattr(errore, "winerror", None) in ERRORI_DI_MANCANZA


def _elenco(cartella, cercati, al_passo, protetta=False):
    """I nomi cercati che ci sono nella cartella: {nome in minuscolo: nome
    com'e' scritto sul disco}; gli altri non si tengono. al_passo si chiama
    a ogni voce letta; protetta, per le unita' del PC, legge senza la
    finestra di errore di Windows. Solleva OSError se la cartella non si legge."""
    trovati = {}
    with _senza_finestre_di_errore() if protetta else contextlib.nullcontext(), os.scandir(cartella) as voci:
        for voce in voci:
            al_passo()
            nome = os.path.normcase(voce.name)
            if nome in cercati:
                trovati[nome] = voce.name
    return trovati


class _Radice:
    """Le voci di una radice, un'unita' o una condivisione di rete,
    raggruppate per cartella. Le cartelle sono in minuscolo, come le da' norm."""

    def __init__(self, chiave):
        # La cartella della radice, come E:\ o \\server\condivisione\.
        self.cima = chiave + "\\"
        self.nome = chiave
        self._scritture = Counter()
        # norm del file -> (cartella, nome in minuscolo, come e' stato scritto ogni volta).
        self.voci = {}
        # cartella -> i nomi da cercare nel suo elenco: quelli dei file e, per le
        # cartelle sopra, quelli delle cartelle che portano ai file.
        self.cercati = {}
        # cartella -> come si scrive, per leggerla.
        self.scritte = {}

    def aggiungi(self, percorso, assoluto, unita):
        """percorso com'e' stato dato, assoluto e' il suo abspath e unita la sua radice."""
        self._scritture[unita] += 1
        chiave = os.path.normcase(assoluto)
        voce = self.voci.get(chiave)
        if voce is not None:
            voce[2].add(percorso)
            return
        scritta, nome = ntpath.split(assoluto)
        cartella, cercato = os.path.normcase(scritta), os.path.normcase(nome)
        self.voci[chiave] = (cartella, cercato, {percorso})
        # La cartella e quelle sopra, fino alla radice: dai loro elenchi si
        # leggono le maiuscole vere di ogni pezzo del percorso. Una cartella
        # gia' vista ha gia' le sue cartelle sopra.
        while True:
            vista = cartella in self.cercati
            self.cercati.setdefault(cartella, set()).add(cercato)
            self.scritte.setdefault(cartella, scritta)
            sopra = ntpath.dirname(cartella)
            if vista or sopra == cartella:
                return
            cercato = ntpath.basename(cartella)
            cartella, scritta = sopra, ntpath.dirname(scritta)

    def scegli_il_nome(self):
        r"""Il nome della radice nei risultati: la lettera in maiuscolo, o per
        una condivisione, come \\server\condivisione, la scrittura che ricorre
        di piu', perche' le maiuscole di server e condivisione non si leggono
        da nessun elenco."""
        if len(self.cima) == 3 and self.cima[1:] == ":\\":
            self.nome = self.cima[:2].upper()
        else:
            self.nome = min(self._scritture, key=lambda s: (-self._scritture[s], s))


def _raggruppa(percorsi, cedi=None, fermo=_mai):
    """Le radici dei percorsi, nell'ordine in cui arrivano, con le loro voci
    senza doppioni. Si lasciano stare i percorsi che non sono testo o non si
    leggono, quelli non assoluti, che si risolverebbero con la cartella di
    lavoro, e le radici da sole, che non sono file. Ogni tanto si cede il
    passo: centomila percorsi da mettere in ordine si fanno sentire."""
    radici = {}
    for indice, percorso in enumerate(percorsi):
        if indice % GRUPPO_FRA_UNA_PAUSA_E_L_ALTRA == 0:
            _cedi_il_passo(cedi, fermo)
        try:
            scritto = os.fspath(percorso)
        except TypeError:
            continue
        # Un percorso con il carattere nullo non si puo' leggere: scandir
        # solleverebbe ValueError. Uno senza l'unita', come \brano.mp3, o
        # relativo, come brano.mp3 o C:brano.mp3, non si sa da dove venga.
        if not isinstance(scritto, str) or "\0" in scritto or not ntpath.isabs(scritto):
            continue
        try:
            assoluto = os.path.abspath(scritto)
        except ValueError:
            continue
        unita = ntpath.splitdrive(assoluto)[0]
        if not unita or not ntpath.basename(assoluto):
            continue
        chiave = os.path.normcase(unita)
        if chiave not in radici:
            radici[chiave] = _Radice(chiave)
        radici[chiave].aggiungi(scritto, assoluto, unita)
    for radice in radici.values():
        radice.scegli_il_nome()
    return list(radici.values())


def _giro(radice, fermo, cedi, al_passo, protetta):
    """Gli elenchi delle cartelle di una radice: cartella -> {nome in
    minuscolo: nome sul disco} dei soli nomi cercati, o None per una cartella
    che dice di non esserci: se e' sparita davvero lo dice poi _sparita. Una
    cartella che da' un altro errore non ha la sua chiave. al_passo si chiama a ogni cartella e a ogni voce, anche mentre si
    cede il passo. None se fermo() diventa vero prima della fine."""
    elenchi = {}
    for cartella in sorted(radice.cercati):
        _cedi_il_passo(cedi, fermo, al_passo)
        if fermo():
            return None
        al_passo()
        try:
            elenchi[cartella] = _elenco(radice.scritte[cartella], radice.cercati[cartella], al_passo, protetta)
        except OSError as errore:
            if _manca(errore):
                elenchi[cartella] = None
    return elenchi


def _giro_sorvegliato(radice, fermo, cedi, attesa):
    """Il giro di una radice di rete, fatto in un filo a parte e sorvegliato
    come ricerca.leggi_in_rete: se per attesa secondi non va avanti, la
    lettura in corso si annulla, in un altro filo perche' anche l'annullamento
    puo' restare fermo, e si solleva ricerca.NonRisponde; il filo lasciato
    smette prima della cartella dopo. fermo, se diventa vero mentre si
    aspetta, fa tornare subito con None."""
    esito = []
    passo = [time.monotonic()]
    lasciato = threading.Event()

    def al_passo():
        passo[0] = time.monotonic()

    def gira():
        try:
            esito.append(_giro(radice, lambda: lasciato.is_set() or fermo(), cedi, al_passo, protetta=False))
        except Exception as errore:  # noqa: BLE001 - torna a chi aspetta, che lo solleva
            esito.append(errore)

    filo = threading.Thread(target=gira, name="MeTeOra, pulizia in rete", daemon=True)
    filo.start()
    while filo.is_alive() and not fermo() and time.monotonic() - passo[0] < attesa:
        filo.join(0.1)
    if filo.is_alive():
        lasciato.set()
        threading.Thread(target=ricerca.annulla_la_lettura, args=(filo,), name="MeTeOra, annullamento in rete", daemon=True).start()
        if fermo():
            return None
        raise ricerca.NonRisponde(radice.nome)
    if not esito:
        raise OSError(f"Il giro di {radice.nome} si e' interrotto.")
    if isinstance(esito[0], Exception):
        raise esito[0]
    return esito[0]


def _vera(radice, elenchi, cartella, memoria):
    """La cartella con le maiuscole che ha sul disco, o None se un pezzo del
    percorso non si sa, perche' la cartella sopra non si e' letta."""
    if cartella in memoria:
        return memoria[cartella]
    sopra = ntpath.dirname(cartella)
    if cartella == radice.cima:
        vera = radice.nome + "\\"
    elif sopra == cartella:
        vera = None
    else:
        base = _vera(radice, elenchi, sopra, memoria)
        nome = (elenchi.get(sopra) or {}).get(ntpath.basename(cartella))
        vera = ntpath.join(base, nome) if base and nome else None
    memoria[cartella] = vera
    return vera


def _sparita(elenchi, cartella):
    r"""Vero se la cartella, che dice di non esserci, e' sparita davvero: lo
    conferma l'elenco della prima cartella sopra che si e' letta, se non ha
    il nome del pezzo che porta a lei. Se il nome c'e', la cartella c'e' ma
    non si legge, come una giunzione o un disco montato in una cartella che
    portano a un disco staccato, o un percorso troppo lungo. Falso anche per
    la radice, come E:\, che non ha cartelle sopra. Un'altra chiavetta
    infilata nella stessa lettera non ha le cartelle di quella di prima: li'
    il nome manca dall'elenco della radice."""
    while True:
        sopra = ntpath.dirname(cartella)
        if sopra == cartella:
            return False
        elenco = elenchi.get(sopra)
        if elenco is not None:
            return ntpath.basename(cartella) not in elenco
        cartella = sopra


def _esito_della_radice(radice, elenchi):
    """(mancanti, nomi veri, quanti controllati) di una radice, dagli elenchi
    delle sue cartelle. Le voci di una cartella che dice di non esserci sono
    mancanti solo se _sparita lo conferma; se no restano senza controllo."""
    mancanti, veri, controllati = set(), {}, 0
    memoria, sparite = {}, {}
    for chiave, (cartella, nome, scritture) in radice.voci.items():
        if cartella not in elenchi:
            continue
        elenco = elenchi[cartella]
        if elenco is None:
            if cartella not in sparite:
                sparite[cartella] = _sparita(elenchi, cartella)
            if sparite[cartella]:
                controllati += 1
                mancanti.add(chiave)
            continue
        controllati += 1
        if nome not in elenco:
            mancanti.add(chiave)
            continue
        sopra = _vera(radice, elenchi, cartella, memoria)
        if sopra is None:
            continue
        vero = ntpath.join(sopra, elenco[nome])
        if any(scritto != vero for scritto in scritture):
            veri[chiave] = vero
    return mancanti, veri, controllati


def controlla(percorsi, fermo=None, cedi=None, risponde=None, attesa=ricerca.ATTESA_IN_RETE, dischi=None, identita=None, dischi_ignoti=False):
    r"""Quali percorsi mancano sul disco. Torna un dizionario con:
    - mancanti: l'insieme dei norm dei percorsi che non ci sono piu';
    - saltate: radice -> quante voci sue sono restate senza controllo, per
      le radici che non hanno risposto, prima o dopo il giro, o che in rete
      si sono fermate a meta'; la radice e' la lettera, come E:, o la
      condivisione, come \\server\condivisione;
    - contese: radice -> quante voci sue sono restate senza controllo, per
      le lettere usate da dischi diversi, cioe' contese con almeno due
      dischi visti, fra il suo e gli altri (1.112.0);
    - non_riconosciute: radice -> quante voci sue sono restate senza
      controllo, per le lettere a cui risponde un disco che non si
      riconosce: contese con un disco solo visto, che non e' mai stato il
      suo, lettere di cui non si legge chi risponde e, con dischi_ignoti,
      tutte;
    - dischi: radice -> il ricordo nuovo, solo per le lettere il cui ricordo
      e' cambiato: il disco imparato, {"disco": identita'}, o gli altri
      dischi visti, {"disco": identita', "altri": [identita', ...]}, con il
      disco solo se si conosce; i dischi che la Sentinella aveva visto in una
      lettera senza un disco suo restano solo se e' diventato il suo, se no
      vanno fra gli altri;
    - nomi_veri: norm -> il percorso con le maiuscole che ha sul disco, solo
      per i percorsi dati scritti in un altro modo, per esempio con altre
      maiuscole;
    - controllati: quanti percorsi distinti si sono potuti guardare.
    fermo(), se c'e', si chiede prima di ogni cartella: vero, e si torna
    subito con quello che si sa, con le radici non finite fra le saltate.
    cedi, se c'e', e' un threading.Event: finche' e' alzato si aspetta.
    risponde(radice), per le prove, dice se una radice risponde; attesa e'
    quanto si aspetta, in rete, un giro che non va avanti. dischi sono i
    ricordi delle lettere, radice -> ricordo, come li tiene Dischi;
    identita(radice), per le prove, dice chi risponde a una radice, come
    _identita. dischi_ignoti, vero quando il file dei dischi non si e'
    potuto leggere, fa saltare ogni lettera senza impararne il disco: una
    lettera contesa sembrerebbe nuova."""
    fermo = fermo or _mai
    risponde = risponde or _risponde
    identita = identita or _identita
    dischi = dischi or {}
    esito = {"mancanti": set(), "saltate": {}, "contese": {}, "non_riconosciute": {}, "dischi": {}, "nomi_veri": {}, "controllati": 0}

    def salta(*radici):
        for radice in radici:
            esito["saltate"][radice.nome] = len(radice.voci)

    def non_riconosciuta(radice):
        esito["non_riconosciute"][radice.nome] = len(radice.voci)

    def contesa(radice, *chi):
        """La radice si salta, e la sua lettera ricorda chi le ha risposto:
        e' usata da dischi diversi se ne ha visti almeno due, fra il suo e
        gli altri; se no il disco che risponde non e' mai stato il suo, e
        non si riconosce."""
        prima = ricordo = dischi.get(radice.nome)
        for uno in chi:
            ricordo = _contesa(ricordo, uno)
        if ricordo != prima:
            esito["dischi"][radice.nome] = ricordo
        if "disco" in ricordo or len(ricordo.get("altri", ())) > 1:
            esito["contese"][radice.nome] = len(radice.voci)
        else:
            non_riconosciuta(radice)

    radici = _raggruppa(percorsi, cedi, fermo)
    for indice, radice in enumerate(radici):
        if fermo():
            salta(*radici[indice:])
            break
        if not risponde(radice.nome):
            salta(radice)
            continue
        # Chi risponde: se non si sa, o se i ricordi non si sono letti, la
        # lettera si salta senza ricordare niente. Una lettera contesa, o
        # con un disco diverso dal suo o da quello che la Sentinella ci ha
        # visto, si salta senza leggerla.
        chi = identita(radice.nome)
        if chi == "" or (chi is not None and dischi_ignoti):
            non_riconosciuta(radice)
            continue
        ricordo = dischi.get(radice.nome) if chi is not None else None
        if ricordo is not None and not _puo_essere_suo(ricordo, chi):
            contesa(radice, chi)
            continue
        try:
            if ricerca.in_rete(radice.nome):
                elenchi = _giro_sorvegliato(radice, fermo, cedi, attesa)
            else:
                elenchi = _giro(radice, fermo, cedi, _niente, protetta=True)
        except ricerca.NonRisponde:
            salta(radice)
            continue
        if elenchi is None:
            salta(*radici[indice:])
            break
        if not risponde(radice.nome):
            salta(radice)
            continue
        dopo = identita(radice.nome)
        if dopo != chi:
            # Un altro disco infilato a meta' giro: le cartelle lette dopo
            # erano sue.
            if dopo == "":
                non_riconosciuta(radice)
            else:
                contesa(radice, chi, dopo)
            continue
        mancanti, veri, controllati = _esito_della_radice(radice, elenchi)
        if chi is not None and not (ricordo or {}).get("disco") and controllati:
            # La prima volta: il disco si fa suo solo se ha i file che si
            # conoscono, anche se la Sentinella l'ha gia' visto all'uso.
            if controllati - len(mancanti) < controllati * PARTE_PER_RICONOSCERE:
                contesa(radice, chi)
                continue
            esito["dischi"][radice.nome] = {"disco": chi}
        esito["mancanti"] |= mancanti
        esito["nomi_veri"].update(veri)
        esito["controllati"] += controllati
    return esito


class Pulizia:
    """La pulizia in un filo a parte, come i lavori di sottotitoli_ocr:
    finita(esito) si chiama alla fine, nel filo della pulizia, solo se nessuno
    l'ha fermata; esito e' quello di controlla, o {"errore": testo} se il
    lavoro si guasta. cedi e' l'evento con cui la finestra chiede il passo;
    dischi sono i ricordi delle lettere, come li da' Dischi.per_la_pulizia, e
    dischi_ignoti e' vero quando il loro file non si legge, come per
    controlla."""

    def __init__(self, percorsi, finita, cedi=None, dischi=None, dischi_ignoti=False):
        # Una copia: chi la crea puo' cambiare i suoi elenchi mentre si lavora.
        self._percorsi = list(percorsi)
        self._finita = finita
        self._cedi = cedi
        self._dischi = dict(dischi or {})
        self._dischi_ignoti = dischi_ignoti
        self._fermo = threading.Event()
        self._filo = threading.Thread(target=self._lavora, name="MeTeOra, pulizia", daemon=True)

    def avvia(self):
        self._filo.start()
        return self

    def ferma(self):
        self._fermo.set()

    def aspetta(self, secondi=10):
        """Per le prove."""
        self._filo.join(secondi)

    def _lavora(self):
        try:
            esito = controlla(self._percorsi, fermo=self._fermo.is_set, cedi=self._cedi, dischi=self._dischi, dischi_ignoti=self._dischi_ignoti)
        except Exception as errore:  # noqa: BLE001 - torna a chi aspetta come frase
            traceback.print_exc()
            if isinstance(errore, OSError) and errore.strerror:
                motivo = errore.strerror
            else:
                motivo = f"{type(errore).__name__}: {errore}" if str(errore) else type(errore).__name__
            esito = {"errore": motivo.rstrip(". ") + "."}
        if not self._fermo.is_set():
            self._finita(esito)


def _in_disparte(lavoro, nome):
    """lavoro() in un filo a parte, che non tiene aperto MeTeOra."""
    threading.Thread(target=lavoro, name=nome, daemon=True).start()


def conta_le_voci(radice, percorsi, fermo=None, cedi=None, risponde=None, identita=None, attesa=ricerca.ATTESA_IN_RETE):
    """Per la conferma di Riconosci questo disco (1.112.0, Gabriele): chi
    risponde adesso a una lettera, come E:, e quante delle sue voci la
    prossima pulizia toglierebbe. Torna (chi, conto). chi e' come per
    _identita, ma "" anche quando la lettera non risponde, come un lettore di
    schede vuoto o una condivisione spenta, e allora il conto non si fa.
    conto e' (voci, mancanti): voci sono i percorsi della lettera fra quelli
    dati, senza doppioni, come li conta la riga della pulizia, e mancanti
    quelli che sul disco di adesso non ci sono. Le cartelle si leggono come
    nella pulizia, una volta sola, in rete con il giro sorvegliato, e cedi fa
    cedere il passo alla finestra. conto e' None se non si e' potuto fare:
    una cartella di rete ferma, un errore o fermo() vero. Alla fine si
    chiede di nuovo chi risponde, perche' le cartelle lette siano tutte
    dello stesso disco: se e' cambiato mentre si contava, chi e' quello
    nuovo, che risponde davvero, e conto e' None; se la lettera non risponde
    piu', chi e' "". risponde, identita e attesa servono alle prove, come per
    controlla. Puo' aspettare: si chiama in disparte, con chiedi_il_conto."""
    fermo = fermo or _mai
    risponde = risponde or _risponde
    identita = identita or _identita

    def chi_risponde():
        try:
            return (identita(radice) or "") if risponde(radice) else ""
        except OSError:
            return ""

    chi = chi_risponde()
    if not chi:
        return "", None
    radici = _raggruppa([percorso for percorso in percorsi if lettera_di(percorso) == radice], cedi, fermo)
    if not radici:
        return chi, (0, 0)
    gruppo = radici[0]
    try:
        if ricerca.in_rete(radice):
            elenchi = _giro_sorvegliato(gruppo, fermo, cedi, attesa)
        else:
            elenchi = _giro(gruppo, fermo, cedi, _niente, protetta=True)
    except OSError:
        elenchi = None
    if fermo():
        return chi, None
    # Un disco cambiato a meta' conto: la domanda parla di quello che
    # risponde adesso, senza numeri, e non di quello che se n'e' andato.
    dopo = chi_risponde()
    if dopo != chi or elenchi is None:
        return dopo, None
    mancanti, _veri, _controllati = _esito_della_radice(gruppo, elenchi)
    return chi, (len(gruppo.voci), len(mancanti))


def chiedi_il_conto(radice, percorsi, fatto, fermo=None, cedi=None):
    """conta_le_voci in un filo a parte: fatto(chi, conto) si chiama li', e
    chi lo usa lo riporta nel suo filo. Si chiama anche se il conto si
    guasta, con chi "", e il guasto va dove vanno quelli degli altri fili.
    La finestra non si ferma mai su una lettera che non risponde
    (1.112.0)."""

    def conta():
        esito = ("", None)
        try:
            esito = conta_le_voci(radice, percorsi, fermo=fermo, cedi=cedi)
        finally:
            fatto(*esito)

    _in_disparte(conta, f"MeTeOra, conto delle voci di {radice}")


def lettera_di(percorso):
    r"""La lettera dell'unita' di un percorso assoluto, come E:, in
    maiuscolo; None per una condivisione scritta per esteso, come
    \\server\condivisione, che si riconosce dal nome, per un percorso
    relativo, come brano.mp3 o C:brano.mp3, e per cio' che non e' un testo.
    Senza os.path: la Sentinella la chiede per ogni file di una playlist,
    anche diecimila, nel filo della finestra (1.112.0)."""
    if not isinstance(percorso, str) or len(percorso) < 3 or percorso[1] != ":" or percorso[2] not in "\\/":
        return None
    iniziale = percorso[0]
    return f"{iniziale.upper()}:" if iniziale.isascii() and iniziale.isalpha() else None


class Sentinella:
    """Il controllo dei dischi a MeTeOra aperto (1.112.0, Gabriele): la
    pulizia vede chi risponde a una lettera solo all'avvio, e una chiavetta
    infilata dopo e tolta prima di chiudere le sfuggirebbe. guarda(percorsi)
    si chiama quando MeTeOra usa dei file, da qualunque filo, e torna
    subito: chi risponde a ogni lettera si chiede in un filo a parte, con
    _identita, una volta per lettera ogni MEMORIA_DELLA_SENTINELLA secondi.
    Una lettera che non risponde non si aspetta, e finche' la sua domanda non
    torna non se ne fa un'altra. visto(lettera, chi) si chiama nel filo
    della domanda, solo quando chi risponde si sa: chi la passa la riporta
    nel suo filo, per Dischi.visto. Come la pulizia guarda solo le lettere:
    le unita' del PC dal numero di serie, quelle di rete dalla condivisione.
    identita, avvia e adesso, per le prove, sostituiscono _identita, il filo
    a parte e l'orologio."""

    def __init__(self, visto, identita=None, avvia=None, adesso=time.monotonic, memoria=MEMORIA_DELLA_SENTINELLA):
        self._visto = visto
        self._identita = identita
        self._avvia = avvia or _in_disparte
        self._adesso = adesso
        self._memoria = memoria
        self._lucchetto = threading.Lock()
        # Lettera -> quando e' tornata la sua ultima domanda.
        self._viste = {}
        self._in_corso = set()

    def guarda(self, *percorsi):
        """Le lettere dei percorsi usati: per ognuna che non si e' chiesta di
        recente, e non si sta chiedendo, una domanda in disparte."""
        lettere = {lettera_di(percorso) for percorso in percorsi}
        lettere.discard(None)
        for lettera in sorted(lettere):
            with self._lucchetto:
                vista = self._viste.get(lettera)
                if lettera in self._in_corso or (vista is not None and self._adesso() - vista < self._memoria):
                    continue
                self._in_corso.add(lettera)
            self._avvia(lambda lettera=lettera: self._chiedi(lettera), f"MeTeOra, sentinella di {lettera}")

    def _chiedi(self, lettera):
        # _identita si cerca adesso, non alla nascita: le prove la sostituiscono.
        chi = ""
        try:
            chi = (self._identita or _identita)(lettera)
        except OSError:
            pass
        finally:
            with self._lucchetto:
                self._in_corso.discard(lettera)
                self._viste[lettera] = self._adesso()
        if chi:
            self._visto(lettera, chi)


def nome_del_computer():
    """Il nome di questo computer, in maiuscolo, come lo dice Windows in
    COMPUTERNAME: ogni computer ha i suoi dischi (1.112.0, Gabriele)."""
    return (os.environ.get("COMPUTERNAME") or platform.node() or "questo computer").upper()


def guid_del_computer():
    r"""Il MachineGuid di Windows, in minuscolo, letto da
    HKLM\SOFTWARE\Microsoft\Cryptography: resta lo stesso quando il computer
    cambia nome, e Dischi lo tiene accanto al nome (1.112.0, Gabriele).
    Si legge dalla vista a 64 bit del registro, l'unica che lo ha, anche da
    un Python a 32 bit; "" se non si legge, o fuori da Windows."""
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as chiave:
            valore, _tipo = winreg.QueryValueEx(chiave, "MachineGuid")
    except (ImportError, OSError):
        return ""
    return valore.strip().lower() if isinstance(valore, str) else ""


def _ricordi_letti(dati, computer):
    """I ricordi delle lettere di un computer letti dal file, con solo cio'
    che serve: il disco, gli altri e quello visto, uniti da _unisci, senza le
    chiavi in piu' e senza i ricordi vuoti. Solleva ValueError se qualcosa
    non si capisce, come un disco che non e' un testo o che sta anche fra gli
    altri: un ricordo lasciato da parte, o letto a meta', farebbe sembrare
    nuova la sua lettera, anche se era contesa."""

    def testi(valore):
        return isinstance(valore, list) and all(isinstance(chi, str) and chi for chi in valore)

    if not isinstance(dati, dict):
        raise ValueError(f"i dischi di {computer} non si capiscono")
    ricordi = {}
    for radice, ricordo in dati.items():
        if not isinstance(ricordo, dict):
            raise ValueError(f"il ricordo di {radice} su {computer} non si capisce")
        disco, altri, visti = ricordo.get("disco"), ricordo.get("altri", []), ricordo.get("visti", [])
        # Il disco, se c'e', e ognuno degli altri e dei visti sono testi non
        # vuoti; il disco non e' anche fra gli altri.
        if (disco is not None and not (isinstance(disco, str) and disco)) or not testi(altri) or not testi(visti) or disco in altri:
            raise ValueError(f"il ricordo di {radice} su {computer} non si capisce")
        valido = _unisci({"disco": disco, "altri": altri, "visti": visti})
        if valido:
            ricordi[radice] = valido
    return ricordi


def _computer_letti(dati):
    """I ricordi di tutti i computer letti dal file: nome del computer ->
    {"lettere": lettera -> ricordo, "guid": MachineGuid in minuscolo}, con
    guid solo se c'e'. Solleva ValueError come _ricordi_letti, anche per un
    computer senza le sue lettere o con un MachineGuid che non e' un testo:
    un computer letto senza lettere farebbe sembrare nuove le sue contese."""
    if not isinstance(dati, dict):
        raise ValueError("non contiene i dischi dei computer")
    letti = {}
    for computer, suoi in dati.items():
        if not isinstance(suoi, dict) or not isinstance(suoi.get("lettere"), dict) or not isinstance(suoi.get("guid", ""), str):
            raise ValueError(f"i dischi di {computer} non si capiscono")
        letti[computer] = {"lettere": _ricordi_letti(suoi["lettere"], computer)}
        if suoi.get("guid"):
            letti[computer]["guid"] = suoi["guid"].lower()
    return letti


class Dischi:
    """I dischi che la pulizia riconosce (1.112.0): per ogni lettera, come
    E:, il suo disco, gli altri che ci hanno risposto e quello visto dalla
    Sentinella prima che la lettera ne avesse uno, come li unisce _unisci.
    Ogni computer ha i suoi, sotto il nome che da' nome_del_computer
    (Gabriele): con i dati portati su un altro computer, con la versione
    portatile o copiando i file, i dischi del primo non rendono contese le
    lettere dell'altro, che impara i suoi come la prima volta, con la regola
    della meta': una lettera con i file del primo, che li' non ci sono, resta
    da riconoscere. I ricordi degli altri computer si riscrivono come sono.
    Accanto al nome si salva il MachineGuid di guid_del_computer, e il nome
    resta la chiave: un computer che ha cambiato nome, che nel file non c'e'
    ancora, adotta i ricordi del solo nome con il suo stesso MachineGuid, e
    al salvataggio la chiave prende il nome nuovo (Gabriele). Se il
    MachineGuid non si legge, o se lo hanno piu' nomi, come due computer
    clonati dalla stessa immagine di Windows, si va per nome; se non si
    legge, quello che il file ha gia' per questo nome si riscrive com'e'.
    Il file e' "MeTeOra - Dischi.json", accanto agli altri dati, scritto come
    loro: prima un file accanto, poi al posto del vero. Un file che manca
    vale come vuoto, come al primo avvio. Uno che c'e' ma non si legge, o che
    ha un ricordo che non si capisce, anche di un altro computer, non si
    sovrascrive, come gli altri dati: errore dice perche', i ricordi restano
    vuoti e niente si impara. Le lettere contese non si possono rileggere da
    nessuna parte, e senza di loro una contesa sembrerebbe nuova: chi lo usa
    fa saltare alla pulizia ogni lettera, con dischi_ignoti, finche' il file
    non si legge. Si usa nel filo della finestra: la pulizia lavora su una
    copia, e i dischi visti dalla Sentinella ci arrivano con wx.CallAfter."""

    def __init__(self, percorso, computer=None, guid=None):
        self.percorso = percorso
        self.computer = computer or nome_del_computer()
        # Il MachineGuid di questo computer, "" se non si legge.
        self.guid = guid_del_computer() if guid is None else guid
        # Quello che il file ha per questo computer: se in una sessione il
        # MachineGuid non si legge, si riscrive questo, e un nome nuovo dopo
        # ritrova i ricordi lo stesso.
        self._guid_del_file = ""
        self._dischi = {}
        # I ricordi degli altri computer, che si riscrivono come sono.
        self._altri_computer = {}
        # Le lettere riconosciute a mano dopo la copia per la pulizia: quello
        # che la pulizia ne dira' e' superato.
        self._riconosciute = set()
        self.modificati = False
        # Perche' il file non si e' letto, se c'e' e non si e' letto.
        self.errore = None
        try:
            with open(percorso, encoding="utf-8") as f:
                letti = _computer_letti(json.load(f))
        except FileNotFoundError:
            pass
        except (OSError, ValueError) as e:
            self.errore = str(e) or type(e).__name__
        else:
            self._adotta(letti)
            suoi = letti.pop(self.computer, {})
            self._dischi, self._guid_del_file = suoi.get("lettere", {}), suoi.get("guid", "")
            self._altri_computer = letti

    def _adotta(self, letti):
        """Il computer ha cambiato nome: se il suo nome non c'e', e un solo
        altro nome ha il suo MachineGuid, i ricordi di quel nome passano al
        suo, e si salvano sotto il nome nuovo."""
        if self.computer in letti or not self.guid:
            return
        stessi = [nome for nome, suoi in letti.items() if suoi.get("guid") == self.guid]
        if len(stessi) == 1:
            letti[self.computer] = letti.pop(stessi[0])
            self.modificati = True

    def conosciuti(self):
        """Una copia dei ricordi di questo computer."""
        return copy.deepcopy(self._dischi)

    def per_la_pulizia(self):
        """La copia dei ricordi per il filo della pulizia: da qui le lettere
        riconosciute a mano contano di nuovo, perche' la pulizia le vede gia'
        riconosciute."""
        self._riconosciute.clear()
        return self.conosciuti()

    def riconosciute_dopo_la_copia(self):
        """Le lettere riconosciute a mano dopo la copia per la pulizia: i loro
        mancanti si tengono, perche' la pulizia puo' averle lette con un altro
        disco, e i file che ci mancavano sono magari proprio su quello
        riconosciuto. Li guarda il prossimo avvio."""
        return set(self._riconosciute)

    def contesa(self, radice):
        """Vero se la lettera, come E:, e' contesa: la pulizia la salta, e
        Riconosci questo disco la sblocca."""
        return bool(self._dischi.get(radice, {}).get("altri"))

    def _cambia(self, radice, ricordo):
        """Il ricordo nuovo di una lettera, {} per nessuno; vero se e' cambiato."""
        if self._dischi.get(radice, {}) == ricordo:
            return False
        if ricordo:
            self._dischi[radice] = copy.deepcopy(ricordo)
        else:
            self._dischi.pop(radice, None)
        self.modificati = True
        return True

    def aggiorna(self, nuovi):
        """I ricordi nuovi delle lettere, come li torna controlla, uniti a
        quelli di adesso: mentre la pulizia lavorava la Sentinella puo' aver
        visto altri dischi, e restano. Una lettera riconosciuta a mano intanto
        resta com'e'. Vero se qualcosa e' cambiato. Non salva: salva chi
        chiama. Con il file che non si legge non impara niente."""
        if self.errore:
            return False
        cambiati = False
        for radice, ricordo in nuovi.items():
            if radice not in self._riconosciute and self._cambia(radice, _unisci(self._dischi.get(radice), ricordo)):
                cambiati = True
        return cambiati

    def visto(self, radice, chi):
        """chi ha risposto alla lettera mentre MeTeOra ne usava un file, come
        lo dice la Sentinella: se non e' il suo disco, la lettera diventa
        contesa; se non ne ha ancora uno, chi e' il disco visto, e un altro
        disco visto dopo la rende contesa. Vero se il ricordo e' cambiato.
        Non salva."""
        if self.errore:
            return False
        return self._cambia(radice, _unisci(self._dischi.get(radice), {"visti": [chi]}))

    def riconosci(self, radice, chi):
        """Riconosci questo disco (Gabriele): la lettera e' del disco chi, non
        e' piu' contesa, e la pulizia del prossimo avvio la controlla. Vero se
        il ricordo e' cambiato. Non salva."""
        if self.errore:
            return False
        self._riconosciute.add(radice)
        return self._cambia(radice, {"disco": chi})

    def salva(self):
        """Scrive i ricordi di questo computer, con il suo MachineGuid se si
        legge, o se no con quello che aveva nel file, accanto a quelli degli
        altri; un file che non si legge resta com'e'."""
        if self.errore:
            return
        tutti = dict(self._altri_computer)
        if self._dischi:
            suoi = {"lettere": self._dischi}
            if self.guid or self._guid_del_file:
                suoi["guid"] = self.guid or self._guid_del_file
            tutti[self.computer] = suoi
        provvisorio = self.percorso + ".tmp"
        with open(provvisorio, "w", encoding="utf-8") as f:
            json.dump(tutti, f, ensure_ascii=False, indent=1, sort_keys=True)
        os.replace(provvisorio, self.percorso)
        self.modificati = False
