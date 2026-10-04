# MeTeOra, il registro degli errori e dei crash: su file, accanto ai dati, a misura limitata.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.89.0, tappa 12 b del piano.

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
  pulita: se all'avvio c'e' ancora e non e' vuoto, l'ultima chiusura e' stata
  un crash. Allora diventa "MeTeOra - Crash precedente.log", da mandare a chi
  sviluppa, e avvia() lo dice. Le eccezioni di Windows che i programmi
  gestiscono da se' possono finire anch'esse nel file: l'uscita pulita lo
  toglie comunque, quindi non ingannano.
Senza avvia(), per esempio nelle prove, le funzioni non fanno niente.
"""

import contextlib
import faulthandler
import logging
import logging.handlers
import os
import sys
import traceback

FILE_DEGLI_ERRORI = "MeTeOra - Errori.log"
FILE_DEL_CRASH = "MeTeOra - Crash.log"
FILE_DEL_CRASH_PRECEDENTE = "MeTeOra - Crash precedente.log"
MISURA_MASSIMA = 10 * 1024 * 1024
_NOME = "meteora.errori"
_stato = {"cartella": None, "crash": None, "registro": None, "stderr": None}


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
    percorso del crash della volta prima, se c'e' stato, altrimenti None."""
    _stato["cartella"] = cartella
    precedente = None
    crash = os.path.join(cartella, FILE_DEL_CRASH)
    with contextlib.suppress(OSError):
        if os.path.getsize(crash) > 0:
            precedente = os.path.join(cartella, FILE_DEL_CRASH_PRECEDENTE)
            os.replace(crash, precedente)
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
        _stato["crash"] = open(crash, "w", encoding="utf-8")  # noqa: SIM115 - resta aperto per faulthandler, fino a chiudi()
        faulthandler.enable(_stato["crash"], all_threads=True)
    if sys.stderr is None:
        _stato["stderr"] = sys.stderr = _VersoIlRegistro(registro)
    return precedente


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
    perche' non c'e' stato nessun crash."""
    crash = _stato["crash"]
    if crash is not None:
        with contextlib.suppress(Exception):
            faulthandler.disable()
        with contextlib.suppress(OSError):
            crash.close()
            os.remove(crash.name)
        _stato["crash"] = None
    if _stato["stderr"] is not None and sys.stderr is _stato["stderr"]:
        sys.stderr = None
    _stato["stderr"] = None
    registro = _stato["registro"]
    if registro is not None:
        for gestore in list(registro.handlers):
            registro.removeHandler(gestore)
            gestore.close()
    _stato["registro"] = None
