# MeTeOra, i SID: emulazione in tempo reale su sidshim.dll, resa in RAM, senza disco.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: passa dai prototipi al programma con la tappa 1. Nella 1.61.1 il riscaldamento, per il primo SID. Nella 1.62.0 l'attesa di un punto non ancora reso.

"""Motore SID in tempo reale su sidshim.dll: rendering a blocchi in RAM, senza disco."""
import ctypes
import os
import struct
import threading
import time

import numpy as np

import librerie

_dll = ctypes.CDLL(os.path.join(librerie.LIB, "sidshim.dll"))
_dll.sid_apri.restype = ctypes.c_void_p
_dll.sid_apri.argtypes = [ctypes.c_char_p, ctypes.c_uint, ctypes.c_int]
_dll.sid_errore.restype = ctypes.c_char_p
_dll.sid_errore.argtypes = [ctypes.c_void_p]
_dll.sid_info.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
_dll.sid_scegli.argtypes = [ctypes.c_void_p, ctypes.c_int]
_dll.sid_rendi.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_short), ctypes.c_int]
_dll.sid_chiudi.argtypes = [ctypes.c_void_p]
FREQUENZA = 48000
CANALI = 2
BLOCCO = FREQUENZA // 50 * CANALI  # 20 ms di campioni interlacciati
# Quante volte il tempo reale corre la resa, finche' non la si misura: le
# misure del 2 ottobre 2026 stanno fra 16 e 25 volte.
VELOCITA_STIMATA = 15.0
# Quanto deve aver lavorato la resa perche' la sua velocita' si misuri.
MISURA_MINIMA = 0.3
# La stima dell'attesa resta prudente: l'inizio di un brano si rende spesso
# piu' in fretta del resto, e la velocita' misurata si prende al massimo
# cosi'; al salto stesso, a mpv, servono ancora circa mezzo secondo.
VELOCITA_MASSIMA_STIMATA = 20.0
RITARDO_DEL_SALTO = 0.5
_RISCALDATA = threading.Event()
_RISCALDAMENTO = threading.Lock()


def riscalda():
    """La prima apertura di un SID nel processo costa circa 150 ms in piu':
    libsidplayfp prepara le tabelle dei filtri. Qui la si fa una volta sola,
    in un filo in disparte, cosi' il primo SID suonato parte come gli altri
    (tappa 5, 1.61.1). Un percorso vuoto basta: i chip si creano prima di
    leggere il brano."""
    with _RISCALDAMENTO:
        if _RISCALDATA.is_set():
            return
        _RISCALDATA.set()

    def lavora():
        h = _dll.sid_apri(b"", FREQUENZA, 1)
        if h:
            _dll.sid_chiudi(h)

    threading.Thread(target=lavora, name="MeTeOra, riscaldamento dei SID", daemon=True).start()


class BranoSid:
    """Un sottobrano reso in memoria da un filo di esecuzione che corre in anticipo."""

    def __init__(self, percorso, sottobrano, secondi):
        self._h = _dll.sid_apri(os.fsencode(percorso), FREQUENZA, 1)
        errore = _dll.sid_errore(self._h)
        if errore:
            _dll.sid_chiudi(self._h)
            raise OSError(errore.decode("latin-1"))
        if _dll.sid_scegli(self._h, sottobrano):
            raise OSError(_dll.sid_errore(self._h).decode("latin-1"))
        self.totale = int(secondi * FREQUENZA) * CANALI
        self.dati = np.zeros(self.totale, dtype=np.int16)
        self.pronti = 0
        self._fermo = False
        self._condizione = threading.Condition()
        self._partenza = time.perf_counter()
        self._filo = threading.Thread(target=self._lavora, daemon=True)
        self._filo.start()

    def secondi_pronti(self):
        return self.pronti / (FREQUENZA * CANALI)

    def attesa(self, secondi):
        """Quanti secondi mancano, circa, perche' il punto dato sia reso: zero
        se lo e' gia', o se la resa e' finita (tappa 5, 1.62.0)."""
        pronti = self.secondi_pronti()
        if secondi <= pronti or self.pronti >= self.totale:
            return 0.0
        trascorso = time.perf_counter() - self._partenza
        velocita = min(pronti / trascorso, VELOCITA_MASSIMA_STIMATA) if trascorso >= MISURA_MINIMA and pronti > 0 else VELOCITA_STIMATA
        return (min(secondi, self.totale / (FREQUENZA * CANALI)) - pronti) / velocita + RITARDO_DEL_SALTO

    def _lavora(self):
        while self.pronti < self.totale and not self._fermo:
            n = min(BLOCCO, self.totale - self.pronti)
            vista = self.dati[self.pronti:self.pronti + n]
            fatti = _dll.sid_rendi(self._h, vista.ctypes.data_as(ctypes.POINTER(ctypes.c_short)), n)
            with self._condizione:
                self.pronti += fatti if fatti > 0 else n
                self._condizione.notify_all()
        _dll.sid_chiudi(self._h)
        self._h = None

    def aspetta(self, fino_a, attesa=None):
        """Blocca finche i campioni fino a 'fino_a' sono pronti."""
        with self._condizione:
            return self._condizione.wait_for(lambda: self.pronti >= min(fino_a, self.totale) or self._fermo, attesa)

    def ferma(self):
        self._fermo = True
        self._filo.join()


def intestazione_wav(byte_dati):
    f, c = FREQUENZA, CANALI
    return b"RIFF" + struct.pack("<I", 36 + byte_dati) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, c, f, f * c * 2, c * 2, 16) + b"data" + struct.pack("<I", byte_dati)


class FlussoSid:
    """Flusso WAV virtuale per register_stream_protocol di python-mpv, servito dalla RAM."""

    def __init__(self, brano):
        self.brano = brano
        self.testa = intestazione_wav(brano.totale * 2)
        self.size = len(self.testa) + brano.totale * 2
        self.pos = 0

    def read(self, quanti):
        if self.pos >= self.size:
            return b""
        if self.pos < len(self.testa):
            pezzo = self.testa[self.pos:self.pos + quanti]
        else:
            inizio = (self.pos - len(self.testa)) // 2
            fine = min(inizio + max(1, quanti // 2), self.brano.totale)
            self.brano.aspetta(fine)
            pezzo = self.brano.dati[inizio:fine].tobytes()
        self.pos += len(pezzo)
        return pezzo

    def seek(self, pos):
        self.pos = pos
        return pos

    def close(self):
        self.brano.ferma()
