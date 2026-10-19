# MeTeOra, la pulizia all'avvio: quali dei file che MeTeOra conosce non ci sono piu' sul disco.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 19/10/2026: nasce con la 1.104.0, perche' schedario, playlist, Preferiti, marker, punti da riprendere e statistiche non si portino dietro per sempre i file spariti.

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
- Prima di ogni cartella si cede il passo alla finestra, se lo chiede, e si
  smette se chi aspetta ha fermato la pulizia.
Pulizia fa il lavoro in un filo a parte e passa l'esito a finita, nel suo
filo: chi la usa lo riporta in quello della finestra.
"""

import contextlib
import ctypes
import ntpath
import os
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


def controlla(percorsi, fermo=None, cedi=None, risponde=None, attesa=ricerca.ATTESA_IN_RETE):
    r"""Quali percorsi mancano sul disco. Torna un dizionario con:
    - mancanti: l'insieme dei norm dei percorsi che non ci sono piu';
    - saltate: radice -> quante voci sue sono restate senza controllo, per
      le radici che non hanno risposto, prima o dopo il giro, o che in rete
      si sono fermate a meta'; la radice e' la lettera, come E:, o la
      condivisione, come \\server\condivisione;
    - nomi_veri: norm -> il percorso con le maiuscole che ha sul disco, solo
      per i percorsi dati scritti in un altro modo, per esempio con altre
      maiuscole;
    - controllati: quanti percorsi distinti si sono potuti guardare.
    fermo(), se c'e', si chiede prima di ogni cartella: vero, e si torna
    subito con quello che si sa, con le radici non finite fra le saltate.
    cedi, se c'e', e' un threading.Event: finche' e' alzato si aspetta.
    risponde(radice), per le prove, dice se una radice risponde; attesa e'
    quanto si aspetta, in rete, un giro che non va avanti."""
    fermo = fermo or _mai
    risponde = risponde or _risponde
    esito = {"mancanti": set(), "saltate": {}, "nomi_veri": {}, "controllati": 0}

    def salta(*radici):
        for radice in radici:
            esito["saltate"][radice.nome] = len(radice.voci)

    radici = _raggruppa(percorsi, cedi, fermo)
    for indice, radice in enumerate(radici):
        if fermo():
            salta(*radici[indice:])
            break
        if not risponde(radice.nome):
            salta(radice)
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
        mancanti, veri, controllati = _esito_della_radice(radice, elenchi)
        esito["mancanti"] |= mancanti
        esito["nomi_veri"].update(veri)
        esito["controllati"] += controllati
    return esito


class Pulizia:
    """La pulizia in un filo a parte, come i lavori di sottotitoli_ocr:
    finita(esito) si chiama alla fine, nel filo della pulizia, solo se nessuno
    l'ha fermata; esito e' quello di controlla, o {"errore": testo} se il
    lavoro si guasta. cedi e' l'evento con cui la finestra chiede il passo."""

    def __init__(self, percorsi, finita, cedi=None):
        # Una copia: chi la crea puo' cambiare i suoi elenchi mentre si lavora.
        self._percorsi = list(percorsi)
        self._finita = finita
        self._cedi = cedi
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
            esito = controlla(self._percorsi, fermo=self._fermo.is_set, cedi=self._cedi)
        except Exception as errore:  # noqa: BLE001 - torna a chi aspetta come frase
            traceback.print_exc()
            if isinstance(errore, OSError) and errore.strerror:
                motivo = errore.strerror
            else:
                motivo = f"{type(errore).__name__}: {errore}" if str(errore) else type(errore).__name__
            esito = {"errore": motivo.rstrip(". ") + "."}
        if not self._fermo.is_set():
            self._finita(esito)
