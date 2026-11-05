# MeTeOra, il lettore di rete: le letture delle cartelle di rete in un processo a parte, che si puo' abbandonare se resta appeso.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 2.7.2, dal collaudo della 2.7.0.

"""Il lettore di rete, un processo a parte per le letture che possono restare appese.

Il Samba dell'Iliadbox, dopo qualche migliaio di cartelle, lascia appesa una
lettura per venti minuti e piu' (4 ottobre 2026). Fino alla 2.7.1 MeTeOra la
faceva in un filo suo, e se non rispondeva la lasciava perdere e provava ad
annullarla; ma con quel Samba l'annullamento non funziona, e un processo con
una lettura appesa dentro Windows non riesce a chiudersi: nel collaudo della
2.7.0, dopo Maiuscolo con F9 sulla condivisione dell'Iliadbox, MeTeOra chiuso
non tornava al prompt, e Gabriele ha dovuto forzarlo.

Dalla 2.7.2 le letture di rete le fa un processo lettore: lo stesso
eseguibile con ARGOMENTO, o dai sorgenti questo file. Riceve le richieste
su stdin, una riga JSON ciascuna, e risponde su stdout: l'elenco grezzo di
una cartella, con nome e quattro segni per voce (cartella, file, nascosta,
di sistema), o se un percorso e' una cartella. Mentre legge una cartella
grande manda un segno di vita ogni PASSO secondi. MeTeOra filtra l'elenco da
se', come faceva prima. Se il lettore non da' segni per il tempo d'attesa,
MeTeOra lo abbandona, lo chiude con TerminateProcess e per la lettura dopo
ne usa un altro: se e' appeso dentro Windows, resta appeso lui, e MeTeOra si
chiude subito. I lettori liberi si tengono, al piu' LIBERI_TENUTI, per non
pagare la partenza a ogni lettura. Se un lettore non parte, chi chiama torna
alla lettura in un filo, come prima: ATTIVO falso fa lo stesso, e lo usano le
prove, che fingono la rete nel loro processo.
"""

import contextlib
import itertools
import json
import os
import queue
import subprocess
import sys
import threading
import time

ARGOMENTO = "--lettore-di-rete"
# Quanti secondi fra un segno di vita e l'altro, mentre si legge una cartella grande.
PASSO = 0.5
LIBERI_TENUTI = 2
ATTIVO = True
# I segni di una voce nell'elenco.
CARTELLA, FILE, NASCOSTA, DI_SISTEMA = 1, 2, 4, 8
_NASCOSTO, _SISTEMA = 0x2, 0x4
# Senza finestre: nessuna console per il lettore.
_SENZA_FINESTRA = 0x08000000


class NonRisponde(OSError):
    """Una cartella di rete che non ha risposto in tempo. E' un OSError: chi
    tratta una cartella illeggibile la tratta gia' bene anche cosi'."""


class NonParte(OSError):
    """Il processo lettore non parte: chi chiama legge in un filo, come prima."""


# Il processo lettore.


def _flussi():
    """stdin e stdout come byte, anche nell'eseguibile senza console, dove
    sys.stdin e sys.stdout possono mancare: allora dalle maniglie di Windows."""
    if sys.stdin is not None and sys.stdout is not None:
        return sys.stdin.buffer, sys.stdout.buffer
    import ctypes
    import msvcrt

    kernel32 = ctypes.WinDLL("kernel32")
    kernel32.GetStdHandle.restype = ctypes.c_void_p
    entrata = os.fdopen(msvcrt.open_osfhandle(kernel32.GetStdHandle(-10), os.O_RDONLY), "rb", buffering=0)
    uscita = os.fdopen(msvcrt.open_osfhandle(kernel32.GetStdHandle(-11), 0), "wb", buffering=0)
    return entrata, uscita


def _segni(voce):
    segni = 0
    try:
        attributi = voce.stat(follow_symlinks=False).st_file_attributes
    except OSError:
        return NASCOSTA
    if attributi & _NASCOSTO:
        segni |= NASCOSTA
    if attributi & _SISTEMA:
        segni |= DI_SISTEMA
    try:
        if voce.is_dir(follow_symlinks=False):
            segni |= CARTELLA
        elif voce.is_file():
            segni |= FILE
    except OSError:
        pass
    return segni


def _elenca(percorso, vivo):
    voci = []
    ultimo = time.monotonic()
    with os.scandir(percorso) as elenco:
        for voce in elenco:
            voci.append([voce.name, _segni(voce)])
            if time.monotonic() - ultimo >= PASSO:
                ultimo = time.monotonic()
                vivo(len(voci))
    return voci


def principale():
    """Il ciclo del processo lettore: una richiesta alla volta, finche'
    stdin non si chiude. Senza le finestre di errore di Windows."""
    import ctypes

    # SEM_FAILCRITICALERRORS e SEM_NOOPENFILEERRORBOX.
    ctypes.WinDLL("kernel32").SetErrorMode(0x0001 | 0x8000)
    entrata, uscita = _flussi()

    def scrivi(oggetto):
        uscita.write((json.dumps(oggetto, ensure_ascii=False) + "\n").encode("utf-8"))
        uscita.flush()

    prova = os.environ.get("METEORA_LETTORE_DI_PROVA") == "1"
    for riga in entrata:
        richiesta = json.loads(riga)
        numero, percorso = richiesta.get("n"), richiesta.get("percorso", "")
        if richiesta.get("cosa") == "esci":
            break
        try:
            if prova and "<appesa>" in percorso:
                # Solo nelle prove: una lettura che non torna mai.
                threading.Event().wait()
            if richiesta.get("cosa") == "elenca":
                scrivi({"n": numero, "voci": _elenca(percorso, lambda quante, numero=numero: scrivi({"n": numero, "passo": quante}))})
            elif richiesta.get("cosa") == "cartella":
                scrivi({"n": numero, "vero": os.path.isdir(percorso)})
        except OSError as errore:
            scrivi({"n": numero, "errore": [errore.errno, getattr(errore, "winerror", None), errore.strerror or str(errore)]})
    return 0


# Dalla parte di MeTeOra.


def _comando():
    if getattr(sys, "frozen", False):
        return [sys.executable, ARGOMENTO]
    return [sys.executable, "-B", os.path.abspath(__file__)]


class _Processo:
    """Un processo lettore, con un filo che mette le sue risposte in coda."""

    def __init__(self):
        try:
            self.processo = subprocess.Popen(_comando(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,  # noqa: S603 - il nostro eseguibile
                creationflags=_SENZA_FINESTRA)
        except OSError as errore:
            raise NonParte(errore.errno, f"il lettore di rete non parte: {errore}") from errore
        self.coda = queue.Queue()
        threading.Thread(target=self._ascolta, name="MeTeOra, ascolto del lettore di rete", daemon=True).start()

    def _ascolta(self):
        try:
            for riga in self.processo.stdout:
                self.coda.put(json.loads(riga))
        except (OSError, ValueError):
            pass
        self.coda.put(None)

    def manda(self, richiesta):
        self.processo.stdin.write((json.dumps(richiesta, ensure_ascii=False) + "\n").encode("utf-8"))
        self.processo.stdin.flush()

    def abbandona(self):
        """Lo chiude subito, senza aspettarlo: se e' appeso dentro Windows,
        resta appeso lui."""
        with contextlib.suppress(OSError):
            self.processo.kill()

    def chiudi(self):
        """Un lettore libero: stdin chiuso, e il suo ciclo finisce."""
        try:
            self.processo.stdin.close()
        except OSError:
            self.abbandona()


class Lettori:
    """I processi lettori di MeTeOra. elenca e e_una_cartella si chiamano
    da qualsiasi filo; chiudi() alla chiusura di MeTeOra."""

    def __init__(self):
        self._blocco = threading.Lock()
        self._liberi = []
        self._numeri = itertools.count(1)
        self.abbandonati = 0

    def _prendi(self):
        with self._blocco:
            if self._liberi:
                return self._liberi.pop()
        return _Processo()

    def _rendi(self, processo):
        with self._blocco:
            if len(self._liberi) < LIBERI_TENUTI:
                self._liberi.append(processo)
                return
        processo.chiudi()

    def _abbandona(self, processo):
        self.abbandonati += 1
        processo.abbandona()

    def _chiedi(self, cosa, percorso, fermo, attesa):
        """La risposta del lettore, o None se fermo() diventa vero. Solleva
        NonRisponde se per attesa secondi non arriva niente, NonParte se il
        lettore non parte, OSError con l'errore della lettura."""
        processo = self._prendi()
        numero = next(self._numeri)
        try:
            processo.manda({"n": numero, "cosa": cosa, "percorso": percorso})
        except OSError as errore:
            self._abbandona(processo)
            raise NonParte(errore.errno, f"il lettore di rete non risponde: {errore}") from errore
        ultimo = time.monotonic()
        while True:
            if fermo is not None and fermo():
                self._abbandona(processo)
                return None
            try:
                risposta = processo.coda.get(timeout=0.1)
            except queue.Empty:
                if time.monotonic() - ultimo >= attesa:
                    self._abbandona(processo)
                    raise NonRisponde(percorso) from None
                continue
            if risposta is None:
                self._abbandona(processo)
                raise NonParte(None, "il lettore di rete si e' chiuso")
            if risposta.get("n") != numero:
                continue
            if "passo" in risposta:
                ultimo = time.monotonic()
                continue
            self._rendi(processo)
            if "errore" in risposta:
                numero_errore, errore_di_windows, testo = risposta["errore"]
                raise OSError(numero_errore, testo, percorso, errore_di_windows)
            return risposta

    def elenca(self, cartella, fermo=None, attesa=15.0):
        """L'elenco grezzo della cartella: [nome, segni] per voce; None se
        fermo() diventa vero."""
        risposta = self._chiedi("elenca", cartella, fermo, attesa)
        return None if risposta is None else risposta["voci"]

    def e_una_cartella(self, percorso, attesa=3.0):
        """Vero se il percorso e' una cartella e risponde entro attesa secondi."""
        try:
            risposta = self._chiedi("cartella", percorso, None, attesa)
        except NonRisponde:
            return False
        return bool(risposta and risposta.get("vero"))

    def chiudi(self):
        with self._blocco:
            liberi, self._liberi = self._liberi, []
        for processo in liberi:
            processo.chiudi()


lettori = Lettori()


if __name__ == "__main__":
    raise SystemExit(principale())
