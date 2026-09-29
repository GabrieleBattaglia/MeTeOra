"""Motore SID in tempo reale su sidshim.dll: rendering a blocchi in RAM, senza disco."""
import ctypes
import os
import struct
import threading

import ambiente
import numpy as np

_dll = ctypes.CDLL(os.path.join(ambiente.LIB, "sidshim.dll"))
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
        self._filo = threading.Thread(target=self._lavora, daemon=True)
        self._filo.start()

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
