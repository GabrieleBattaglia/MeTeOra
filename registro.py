# MeTeOra, il registro degli errori e dei crash: su file, accanto ai dati, a misura limitata.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.89.0, tappa 12 b del piano. Nella 1.104.0 il crash vero, distinto dalle eccezioni di Windows gestite da chi le solleva, e il file del crash riassunto e svuotato ogni minuto, un resoconto fatale solo al giro dopo.

"""Il registro degli errori e dei crash (1.89.0).

Due file accanto ai dati di MeTeOra:
- "MeTeOra - Errori.log": il resoconto completo di ogni problema interno, che
  nella console arriva in una riga sola, e, dal programma compilato, cio'
  che andrebbe su stderr, che li' non c'e'. Gira a rotazione con una copia,
  "MeTeOra - Errori.log.1", e i due insieme non superano MISURA_MASSIMA:
  10 MB, perche' non cresca all'infinito (Gabriele).
- "MeTeOra - Crash.log": quello che scrive faulthandler quando Python muore
  senza accorgersene, per esempio per un errore dentro una DLL di Windows,
  con la pila di tutti i fili. Si apre a ogni avvio e si toglie a ogni uscita
  pulita. Pero' faulthandler ci scrive anche le eccezioni di Windows che chi
  le solleva poi gestisce da se', come la 0x8001010d di COM o la 0xe24c4a02
  di LuaJIT dentro libmpv: dopo una chiusura a forza, dal Task Manager, il
  file resta e non e' vuoto anche senza nessun crash.
  Per questo, dalla 1.104.0, e' un crash vero solo se crash_vero() ci trova
  un resoconto fatale: una riga "Fatal Python error", o un'eccezione di
  Windows che e' un errore (access violation, stack overflow, o un codice
  NTSTATUS di errore, da 0xC0000000 a 0xDFFFFFFF). Allora all'avvio il file
  diventa "MeTeOra - Crash precedente.log", da mandare a chi sviluppa, e
  avvia() lo dice; se quel file e' bloccato, il resoconto va in uno di
  riserva accanto, o resta nel file del crash, ma non si perde. Le eccezioni
  gestite, invece, finiscono riassunte in una riga del registro degli
  errori. E perche' un'access violation presa da chi l'ha sollevata, per
  esempio da ctypes, che ne fa un OSError, non diventi un crash alla
  prossima chiusura a forza, la finestra chiama sopravvissuto() ogni
  minuto: riassume nel registro cio' che faulthandler ha scritto e svuota il
  file, con faulthandler sempre acceso. Un resoconto fatale, pero', lo
  svuota solo al giro dopo, quando MeTeOra e' davvero sopravvissuto.
Senza avvia(), per esempio nelle prove, le funzioni non fanno niente.
"""

import collections
import contextlib
import faulthandler
import logging
import logging.handlers
import os
import re
import sys
import time
import traceback

FILE_DEGLI_ERRORI = "MeTeOra - Errori.log"
FILE_DEL_CRASH = "MeTeOra - Crash.log"
FILE_DEL_CRASH_PRECEDENTE = "MeTeOra - Crash precedente.log"
MISURA_MASSIMA = 10 * 1024 * 1024
_NOME = "meteora.errori"
# "base": i byte in testa al file del crash che sono il resoconto della volta
# prima, rimasto li' perche' avvia() non l'ha potuto mettere da parte; "visto":
# quanti byte, dopo la base, sopravvissuto() ha letto al giro prima senza
# svuotare il file (1.104.0).
_stato = {"cartella": None, "crash": None, "registro": None, "stderr": None, "base": 0, "visto": 0}
# Le intestazioni dei resoconti di faulthandler, sempre a inizio riga.
_ERRORE_DI_PYTHON = "Fatal Python error"
_ECCEZIONE_DI_WINDOWS = "Windows fatal exception: "
# I nomi che faulthandler da' alle eccezioni di Windows piu' comuni, tutte
# errori; le altre le scrive col codice.
_NOMI_FATALI = frozenset({"access violation", "stack overflow", "int divide by zero", "float divide by zero", "float overflow",
    "integer overflow", "page error"})
_CODICE = re.compile(r"code 0x([0-9A-Fa-f]{1,8})")
# Nei codici NTSTATUS i due bit alti sono la gravita': 11 e' un errore, e il
# terzo, a zero, dice che il codice e' di Microsoft e non di un programma
# qualunque, come la 0xe24c4a02 di LuaJIT.
_MASCHERA_DELLA_GRAVITA = 0xE0000000
_GRAVITA_DI_ERRORE = 0xC0000000


def _nome_breve(intestazione):
    """Cio' che distingue un resoconto: per le eccezioni di Windows il nome o
    il codice, con le cifre minuscole, altrimenti l'intestazione intera."""
    if not intestazione.startswith(_ECCEZIONE_DI_WINDOWS):
        return intestazione
    resto = intestazione[len(_ECCEZIONE_DI_WINDOWS):].strip()
    codice = _CODICE.fullmatch(resto)
    return f"code 0x{int(codice.group(1), 16):08x}" if codice else resto


def _fatale(intestazione):
    if intestazione.startswith(_ERRORE_DI_PYTHON):
        return True
    resto = _nome_breve(intestazione)
    if resto in _NOMI_FATALI:
        return True
    codice = _CODICE.fullmatch(resto)
    return codice is not None and int(codice.group(1), 16) & _MASCHERA_DELLA_GRAVITA == _GRAVITA_DI_ERRORE


def resoconti(testo):
    """I resoconti che faulthandler ha scritto nel testo del file del crash,
    in ordine: per ognuno l'intestazione, la riga che lo apre, e se e' fatale.
    Fatali sono le righe "Fatal Python error..." e le eccezioni di Windows
    che sono errori: quelle con il nome (access violation, stack overflow e
    le altre di _NOMI_FATALI) e i codici NTSTATUS di errore."""
    elenco = []
    for riga in testo.splitlines():
        if riga.startswith((_ERRORE_DI_PYTHON, _ECCEZIONE_DI_WINDOWS)):
            intestazione = riga.rstrip()
            elenco.append((intestazione, _fatale(intestazione)))
    return elenco


def crash_vero(testo):
    """Se il testo del file del crash racconta un crash vero: almeno un
    resoconto fatale. Le eccezioni gestite da chi le solleva non contano."""
    return any(fatale for _, fatale in resoconti(testo))


def _fatale_nuovo(dati, visto):
    """Se nei byte letti dal file del crash c'e' un resoconto fatale la cui
    intestazione, a capo compreso, non stava gia' nei primi visto byte, letti
    al giro prima: un resoconto che si vede per la prima volta, forse di un
    crash ancora in corso (1.104.0)."""
    fine = 0
    for riga in dati.splitlines(keepends=True):
        fine += len(riga)
        if fine > visto and crash_vero(riga.decode("utf-8", errors="replace")):
            return True
    return False


def _nome_di_riserva():
    """Il file per il resoconto di un crash quando quello del crash precedente
    e' bloccato: con la data e l'ora, per non coprirne nessun altro."""
    return f"MeTeOra - Crash precedente {time.strftime('%Y-%m-%d %H.%M.%S')}.log"


def _metti_da_parte(cartella, crash, dati):
    """Il resoconto di un crash vero, dal file del crash a quello del crash
    precedente (1.104.0): con os.replace, o, se non si puo', per esempio
    perche' uno dei due file e' bloccato o in sola lettura, scrivendo i dati
    letti nel file del crash precedente, o in uno di riserva accanto se anche
    quello non si puo' scrivere. Torna il percorso dove il resoconto sta
    davvero, o None se non e' riuscito a scriverlo da nessuna parte."""
    precedente = os.path.join(cartella, FILE_DEL_CRASH_PRECEDENTE)
    with contextlib.suppress(OSError):
        os.replace(crash, precedente)
        return precedente
    # La riserva solo se non c'e' gia': non deve coprire niente.
    for percorso, modo in ((precedente, "wb"), (os.path.join(cartella, _nome_di_riserva()), "xb")):
        try:
            with open(percorso, modo) as file:
                file.write(dati)
        except OSError:
            continue
        return percorso
    return None


def _volte(numero):
    return f"{numero} volta" if numero == 1 else f"{numero} volte"


def _riassunto(elenco):
    """I resoconti in un pezzo di riga: quanti, e quali con quante volte,
    senza doppioni, nell'ordine in cui compaiono."""
    conta = collections.Counter(_nome_breve(intestazione) for intestazione, _ in elenco)
    return f"{len(elenco)} in tutto: {', '.join(f'{nome} {_volte(numero)}' for nome, numero in conta.items())}."


class _VersoIlRegistro:
    """Uno stderr che scrive nel registro, riga per riga: per il programma
    compilato, che uno stderr non ce l'ha."""

    def __init__(self, registro):
        self._registro = registro
        self._resto = ""

    def write(self, testo):
        self._resto += str(testo)
        *righe, self._resto = self._resto.split("\n")
        for riga in righe:
            if riga.strip():
                self._registro.error(riga.rstrip())
        return len(testo)

    def flush(self):
        pass

    def isatty(self):
        return False


def avvia(cartella, misura=MISURA_MASSIMA):
    """All'avvio di MeTeOra: apre i due file nella cartella dei dati. Torna il
    percorso del file dove sta il resoconto del crash della volta prima, se
    e' stato un crash vero, altrimenti None; le eccezioni gestite rimaste nel
    file della volta prima finiscono riassunte in una riga del registro
    (1.104.0). Il resoconto di solito va nel file del crash precedente, ma
    se non lo si puo' scrivere ne' li' ne' in uno di riserva, resta in testa
    al file del crash, che non si tronca: faulthandler ci scrive dopo, in
    aggiunta, e l'uscita pulita lo riporta al solo resoconto invece di
    toglierlo. Cosi' non si perde, e il prossimo avvio riprova a metterlo da
    parte; un file diverso per faulthandler, invece, il prossimo avvio non
    lo guarderebbe, e lo si dovrebbe creare in una cartella dove poco prima
    non si e' riusciti a scrivere niente."""
    _stato["cartella"] = cartella
    _stato["base"] = _stato["visto"] = 0
    precedente = None
    gestite = []
    conserva = False
    crash = os.path.join(cartella, FILE_DEL_CRASH)
    dati = b""
    with contextlib.suppress(OSError), open(crash, "rb") as file:
        dati = file.read()
    testo = dati.decode("utf-8", errors="replace")
    if crash_vero(testo):
        precedente = _metti_da_parte(cartella, crash, dati)
        if precedente is None:
            precedente, conserva = crash, True
    else:
        gestite = resoconti(testo)
    registro = logging.getLogger(_NOME)
    registro.setLevel(logging.INFO)
    registro.propagate = False
    for vecchio in list(registro.handlers):
        registro.removeHandler(vecchio)
        vecchio.close()
    with contextlib.suppress(OSError):
        gestore = logging.handlers.RotatingFileHandler(os.path.join(cartella, FILE_DEGLI_ERRORI), maxBytes=misura // 2, backupCount=1,
            encoding="utf-8", delay=True)
        gestore.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        registro.addHandler(gestore)
    _stato["registro"] = registro
    with contextlib.suppress(OSError):
        # In aggiunta, il file si apre con O_APPEND: faulthandler scrive
        # sempre in fondo, dopo il resoconto della volta prima.
        _stato["crash"] = open(crash, "a" if conserva else "w", encoding="utf-8")  # noqa: SIM115 - resta aperto per faulthandler, fino a chiudi()
        if conserva:
            _stato["base"] = os.fstat(_stato["crash"].fileno()).st_size
        faulthandler.enable(_stato["crash"], all_threads=True)
    if sys.stderr is None:
        _stato["stderr"] = sys.stderr = _VersoIlRegistro(registro)
    if precedente is not None and os.path.basename(precedente) != FILE_DEL_CRASH_PRECEDENTE:
        scrivi(f"Non riesco a scrivere il resoconto del crash della volta prima in {FILE_DEL_CRASH_PRECEDENTE}: è in {os.path.basename(precedente)}.")
    if gestite:
        scrivi(f"Nessun crash la volta prima: il file del crash ha solo eccezioni di Windows gestite da chi le ha sollevate, {_riassunto(gestite)}")
    return precedente


def sopravvissuto():
    """Ogni minuto, dalla finestra (1.104.0): se faulthandler ha scritto
    qualcosa nel file del crash, ne mette il riassunto nel registro e lo
    svuota, mentre faulthandler resta acceso. Se fra i resoconti ce n'e' uno
    fatale, per esempio un'access violation che ctypes ha fatto diventare un
    OSError, chi l'ha sollevato l'ha gestito, e il riassunto dice che MeTeOra
    e' sopravvissuto: cosi' una chiusura a forza, dopo, non lo prende per un
    crash. Ma un resoconto fatale che vede per la prima volta lo lascia nel
    file: faulthandler lo scrive appena l'eccezione passa, e se e' un crash
    vero, per esempio in un filo nativo di libmpv, Windows sta chiudendo il
    processo mentre il filo di wx gira ancora, e svuotare il file lo
    perderebbe. Se al giro dopo MeTeOra c'e' ancora, e' sopravvissuto, e il
    resoconto si riassume. Allo stesso modo aspetta un giro se il file cresce
    mentre lo legge, o se l'ultima riga non e' finita: faulthandler sta
    scrivendo. Il resoconto della volta prima che avvia() ha lasciato in
    testa al file non lo tocca. Torna quanti resoconti ha riassunto, zero se
    aspetta; senza avvia() non fa niente."""
    crash = _stato["crash"]
    if crash is None:
        return 0
    base = _stato["base"]
    try:
        misura = os.fstat(crash.fileno()).st_size
        if misura <= base:
            _stato["visto"] = 0
            return 0
        # Fino alla misura letta: cio' che faulthandler aggiunge intanto
        # resta per il giro dopo.
        with open(crash.name, "rb") as file:
            file.seek(base)
            dati = file.read(misura - base)
        visto = _stato["visto"] if _stato["visto"] <= len(dati) else 0
        # Una riga non finita, se dal giro prima il file non e' cresciuto,
        # non la sta scrivendo nessuno, e non fa aspettare per sempre.
        if _fatale_nuovo(dati, visto) or (not dati.endswith((b"\n", b"\r")) and len(dati) != visto):
            _stato["visto"] = len(dati)
            return 0
        # Il controllo subito prima del taglio, per stringere la corsa con
        # faulthandler: se il file e' cresciuto dopo la lettura, non si taglia.
        if os.fstat(crash.fileno()).st_size != misura:
            _stato["visto"] = len(dati)
            return 0
        # Sullo stesso oggetto file: faulthandler scrive nel suo descrittore,
        # alla sua posizione, che cosi' torna alla base; altrimenti dopo il
        # taglio scriverebbe piu' avanti, lasciando un buco di zeri. Aperto
        # in aggiunta, scrive comunque in fondo.
        crash.seek(base)
        crash.truncate()
        _stato["visto"] = 0
    except (OSError, ValueError):
        return 0
    testo = dati.decode("utf-8", errors="replace")
    elenco = resoconti(testo)
    if elenco:
        riga = f"Il file del crash, ora svuotato, aveva eccezioni di Windows, {_riassunto(elenco)}"
        fatali = list(dict.fromkeys(_nome_breve(intestazione) for intestazione, fatale in elenco if fatale))
        if len(fatali) == 1:
            riga += f" Fra queste {fatali[0]} sarebbe fatale, ma chi l'ha sollevata l'ha gestita: MeTeOra è sopravvissuto."
        elif fatali:
            riga += f" Fra queste {', '.join(fatali)} sarebbero fatali, ma chi le ha sollevate le ha gestite: MeTeOra è sopravvissuto."
        scrivi(riga)
    return len(elenco)


def scrivi(testo):
    """Una riga nel registro, se e' avviato."""
    if _stato["registro"] is not None:
        with contextlib.suppress(Exception):
            _stato["registro"].info(testo)


def problema(tipo, valore, traccia):
    """Il resoconto completo di un problema interno, con la pila."""
    if _stato["registro"] is not None:
        with contextlib.suppress(Exception):
            _stato["registro"].error("".join(traceback.format_exception(tipo, valore, traccia)).rstrip())


def chiudi():
    """All'uscita pulita: faulthandler si spegne e il file del crash si toglie,
    perche' non c'e' stato nessun crash. Se in testa c'e' il resoconto della
    volta prima, che avvia() non ha potuto mettere da parte, il file torna a
    quello e resta, per il prossimo avvio (1.104.0)."""
    crash = _stato["crash"]
    if crash is not None:
        with contextlib.suppress(Exception):
            faulthandler.disable()
        base = _stato["base"]
        if base:
            with contextlib.suppress(OSError, ValueError):
                crash.truncate(base)
        with contextlib.suppress(OSError):
            crash.close()
            if not base:
                os.remove(crash.name)
        _stato["crash"] = None
    _stato["base"] = _stato["visto"] = 0
    if _stato["stderr"] is not None and sys.stderr is _stato["stderr"]:
        sys.stderr = None
    _stato["stderr"] = None
    registro = _stato["registro"]
    if registro is not None:
        for gestore in list(registro.handlers):
            registro.removeHandler(gestore)
            gestore.close()
    _stato["registro"] = None
