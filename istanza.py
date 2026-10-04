# MeTeOra, l'istanza unica: la seconda copia passa i file alla prima e si chiude.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.91.0, tappa 12 d del piano.

"""L'istanza unica di MeTeOra (1.91.0).

Aprire un file da Esplora risorse lancia MeTeOra con il percorso del file.
Se MeTeOra e' gia' aperto, la copia nuova non deve aprire una seconda
finestra: con manda() passa i percorsi alla prima, attraverso una pipe con
nome di Windows, le permette di venire in primo piano e si chiude. La prima
copia, con Ascolto, riceve i percorsi in un filo suo e li consegna a chi
ascolta, che li porta nel filo della finestra.
La pipe e' per utente, e chiede una chiave: un altro programma non ci parla.
Sul filo passano solo byte JSON, non oggetti di Python: niente pickle, che
eseguirebbe codice di chi scrive. La variabile d'ambiente METEORA_ISTANZA
cambia il nome della pipe, per le prove e i banchi: cosi' non parlano con
il MeTeOra che magari e' aperto.
"""

import contextlib
import ctypes
import hashlib
import json
import os
import threading
from multiprocessing.connection import Client, Listener

# AllowSetForegroundWindow: qualunque processo, cioe' la prima copia.
_ASFW_ANY = -1


def nome():
    """Il nome della pipe, per utente."""
    proprio = os.environ.get("METEORA_ISTANZA")
    if proprio:
        return rf"\\.\pipe\{proprio}"
    utente = os.environ.get("USERNAME", "utente")
    return rf"\\.\pipe\MeTeOra-{utente}"


def _chiave(nome_della_pipe):
    return hashlib.sha256(f"MeTeOra {nome_della_pipe}".encode()).digest()


def manda(percorsi, nome_della_pipe=None):
    """Se un MeTeOra e' gia' aperto, gli passa i percorsi, anche nessuno, che
    lo porta solo in primo piano, e torna vero; falso se non ce n'e' uno."""
    nome_della_pipe = nome_della_pipe or nome()
    try:
        connessione = Client(nome_della_pipe, family="AF_PIPE", authkey=_chiave(nome_della_pipe))
    except (OSError, EOFError):
        return False
    with contextlib.suppress(Exception):
        ctypes.windll.user32.AllowSetForegroundWindow(_ASFW_ANY)
    try:
        with connessione:
            connessione.send_bytes(json.dumps({"apri": [os.path.abspath(p) for p in percorsi]}).encode("utf-8"))
    except (OSError, EOFError):
        return False
    return True


class Ascolto:
    """La prima copia ascolta le altre: ricevi(percorsi) e' chiamata nel filo
    dell'ascolto, per ogni copia che si apre. Se la pipe c'e' gia', perche'
    un'altra copia e' partita nello stesso istante, attiva e' falso."""

    def __init__(self, ricevi, nome_della_pipe=None):
        self._ricevi = ricevi
        self._nome = nome_della_pipe or nome()
        self._fermo = False
        try:
            self._ascoltatore = Listener(self._nome, family="AF_PIPE", authkey=_chiave(self._nome))
        except OSError:
            self._ascoltatore = None
        self.attiva = self._ascoltatore is not None
        if self.attiva:
            threading.Thread(target=self._ascolta, name="MeTeOra, istanza unica", daemon=True).start()

    def _ascolta(self):
        while not self._fermo:
            try:
                connessione = self._ascoltatore.accept()
            except Exception:  # noqa: BLE001 - una copia che si presenta male, o la chiave sbagliata
                if self._fermo:
                    return
                continue
            with connessione, contextlib.suppress(Exception):
                messaggio = json.loads(connessione.recv_bytes(1 << 20).decode("utf-8"))
                percorsi = messaggio.get("apri", [])
                if isinstance(percorsi, list) and all(isinstance(p, str) for p in percorsi):
                    self._ricevi(percorsi)

    def ferma(self):
        """All'uscita: l'ascolto finisce."""
        self._fermo = True
        if self._ascoltatore is not None:
            with contextlib.suppress(Exception):
                self._ascoltatore.close()
            # Sblocca accept con una connessione a vuoto.
            with contextlib.suppress(Exception):
                Client(self._nome, family="AF_PIPE", authkey=_chiave(self._nome)).close()
