# MeTeOra, il WAV in RAM: la conversione per gli speaker Cast senza disco, servita a intervalli da una finestra di memoria.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 2.7.0, tappa 17 del piano, dal prototipo prototipi/wav_a_finestra.py provato su GabryBar.

"""Il WAV in RAM, per i brani che lo speaker Cast non legge da se'.

Fino alla 2.6 MeTeOra convertiva il brano intero in FLAC su disco prima di
mandarlo: lo speaker aspettava la conversione intera, circa sette secondi
per un sottobrano di un SID, e su GabryBar i FLAC restavano in caricamento
all'ultimo campione. Gabriele ha chiesto di non usare il disco, con una
parte sicura della RAM (4 novembre 2026).

Il FLAC dice la sua lunghezza solo alla fine; il WAV ha un flusso costante:
la dimensione si sa dalla durata, e ogni byte e' un istante. libmpv, in modo
codifica, scrive il PCM a 16 bit, stereo, in una pipe con nome; un filo lo
versa in una finestra di RAM, il 5% della RAM libera fra 32 e 512 MB; il
server di trasmissione.py dichiara un WAV della dimensione che la durata
dice, e serve ogni intervallo di byte dalla finestra, aspettando quelli che
il convertitore non ha ancora scritto. Il convertitore si ferma quando e'
troppo avanti rispetto a chi legge e riparte quando quello legge; un
quarto della finestra resta dietro, per i salti indietro brevi. Un
intervallo fuori dalla finestra fa ripartire la conversione da li'; per i
brani resi emulando, SID, musica delle console e MIDI, che ripartendo
emulano da capo, in avanti si aspetta la conversione in corsa. Se il
convertitore finisce prima della dimensione dichiarata il resto e'
silenzio, se va oltre si taglia: la fine arriva puntuale. Una conversione
che non scrive niente e' un brano che non si legge, e il server chiude.

Prove su GabryBar del 4 e 5 novembre 2026: un sottobrano di Outrun Europa
suona in 1,9 secondi, contro i circa 7 del FLAC; l'audio di Braveheart, 1,95
GB di PCM, con il convertitore fermo a finestra piena e i salti fuori dalla
finestra pronti subito; la fine sempre con FINISHED.
"""

import ctypes
import os
import struct
import threading
from ctypes import wintypes

FREQUENZA = 48000
# I brani tanto lunghi che il WAV a 48 kHz passerebbe i 4 GB che la sua
# intestazione sa dire, piu' di sei ore, vanno alla meta'.
FREQUENZA_DEI_LUNGHI = 24000
CANALI = 2
QUADRO = CANALI * 2
INTESTAZIONE = 44
MASSIMO_DEL_WAV = 2**32 - 1 - 36
# La finestra: una parte della RAM libera, fra un minimo e un massimo
# (Gabriele, 4 novembre 2026); dietro al punto letto se ne tiene un quarto.
PARTE_DELLA_RAM = 0.05
FINESTRA_MINIMA = 32 * 2**20
FINESTRA_MASSIMA = 512 * 2**20
PARTE_DIETRO = 0.25
# Fin dove, avanti, si aspetta il convertitore invece di farlo ripartire.
SECONDI_DA_ASPETTARE = 10
PEZZO = 65536
TIPO = "audio/wav"

_numeri = iter(range(1, 1 << 62))


def ram_libera():
    class Stato(ctypes.Structure):
        _fields_ = [("dwLength", wintypes.DWORD), ("dwMemoryLoad", wintypes.DWORD)] + [
            (nome, ctypes.c_ulonglong) for nome in ("ullTotalPhys", "ullAvailPhys", "ullTotalPageFile", "ullAvailPageFile", "ullTotalVirtual",
                "ullAvailVirtual", "ullAvailExtendedVirtual")]

    stato = Stato()
    stato.dwLength = ctypes.sizeof(stato)
    ctypes.WinDLL("kernel32").GlobalMemoryStatusEx(ctypes.byref(stato))
    return stato.ullAvailPhys


def dimensione_della_finestra(libera=None):
    """I byte della finestra: PARTE_DELLA_RAM della RAM libera, fra
    FINESTRA_MINIMA e FINESTRA_MASSIMA, a quadri interi."""
    byte = min(FINESTRA_MASSIMA, max(FINESTRA_MINIMA, int((ram_libera() if libera is None else libera) * PARTE_DELLA_RAM)))
    return byte - byte % QUADRO


def frequenza_per(durata):
    """La frequenza del WAV di un brano di durata secondi."""
    return FREQUENZA if durata * FREQUENZA * QUADRO <= MASSIMO_DEL_WAV else FREQUENZA_DEI_LUNGHI


def intestazione(totale_pcm, frequenza):
    """L'intestazione di un WAV PCM a 16 bit, stereo, con totale_pcm byte di campioni."""
    al_secondo = frequenza * QUADRO
    return (b"RIFF" + struct.pack("<I", 36 + totale_pcm) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, CANALI, frequenza, al_secondo, QUADRO, 16)
        + b"data" + struct.pack("<I", totale_pcm))


class Pipe:
    """Una pipe con nome di Windows, dalla parte di chi legge: libmpv la apre
    come un file e ci scrive."""

    def __init__(self, nome):
        k = self._k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.CreateNamedPipeW.restype = wintypes.HANDLE
        k.CreateNamedPipeW.argtypes = [wintypes.LPCWSTR] + [wintypes.DWORD] * 6 + [ctypes.c_void_p]
        k.ConnectNamedPipe.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
        k.ReadFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        k.CreateFileW.restype = wintypes.HANDLE
        k.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        self.percorso = rf"\\.\pipe\{nome}"
        # In entrata, a byte, bloccante, un'istanza sola.
        self._maniglia = k.CreateNamedPipeW(self.percorso, 1, 0, 1, 0, PEZZO, 0, None)
        if not self._maniglia or self._maniglia == ctypes.c_void_p(-1).value:
            raise OSError(ctypes.get_last_error(), f"CreateNamedPipe {self.percorso}")

    def aspetta_chi_scrive(self):
        # ERROR_PIPE_CONNECTED: chi scrive era gia' arrivato.
        if not self._k.ConnectNamedPipe(self._maniglia, None) and ctypes.get_last_error() != 535:
            raise OSError(ctypes.get_last_error(), "ConnectNamedPipe")

    def sblocca(self):
        """Apre la pipe da chi scrive e la richiude: chi aspetta in
        aspetta_chi_scrive torna, se libmpv non e' mai arrivato."""
        maniglia = self._k.CreateFileW(self.percorso, 0x40000000, 0, None, 3, 0, None)
        if maniglia and maniglia != ctypes.c_void_p(-1).value:
            self._k.CloseHandle(maniglia)

    def leggi(self, quanti=PEZZO):
        """I byte che arrivano, b"" quando chi scrive ha chiuso."""
        spazio = ctypes.create_string_buffer(quanti)
        letti = wintypes.DWORD()
        if not self._k.ReadFile(self._maniglia, spazio, quanti, ctypes.byref(letti), None):
            # ERROR_BROKEN_PIPE, ERROR_PIPE_NOT_CONNECTED: chi scrive ha chiuso.
            if ctypes.get_last_error() in (109, 233):
                return b""
            raise OSError(ctypes.get_last_error(), "ReadFile")
        return spazio.raw[:letti.value]

    def chiudi(self):
        if self._maniglia:
            self._k.CloseHandle(self._maniglia)
            self._maniglia = None


class _Passaggio:
    """Un passaggio del convertitore dai secondi dati: avvia(secondi, uscita,
    alla_fine) scrive nella pipe, e un filo versa i byte nella sorgente."""

    def __init__(self, sorgente, generazione, avvia, secondi, frequenza):
        self._sorgente, self._generazione = sorgente, generazione
        self.pipe = Pipe(f"meteora_wav_{os.getpid()}_{next(_numeri)}")
        self._filo = threading.Thread(target=self._versa, name="MeTeOra, WAV in RAM", daemon=True)
        self._filo.start()
        self._lettore = None
        try:
            self._lettore = avvia(secondi, self.pipe.percorso, self._finito, frequenza)
        except Exception:
            self.pipe.sblocca()
            raise

    def _finito(self):
        # Se il convertitore non ha mai aperto la pipe, chi aspetta torna.
        threading.Thread(target=self.pipe.sblocca, daemon=True).start()

    def _versa(self):
        scritti = 0
        try:
            self.pipe.aspetta_chi_scrive()
            while True:
                pezzo = self.pipe.leggi()
                if not pezzo or not self._sorgente._versa(self._generazione, pezzo):
                    break
                scritti += len(pezzo)
        except OSError:
            pass
        finally:
            self._sorgente._fine(self._generazione, scritti)

    def ferma(self):
        threading.Thread(target=self._chiudi, name="MeTeOra, fine del WAV in RAM", daemon=True).start()

    def _chiudi(self):
        try:
            if self._lettore is not None:
                self._lettore.terminate()
        finally:
            self.pipe.sblocca()
            self._filo.join(5)
            self.pipe.chiudi()


class SorgenteWav:
    """Il WAV di un brano, servito a intervalli dalla finestra di RAM.
    avvia(secondi, uscita, alla_fine, frequenza) fa partire il convertitore,
    che scrive in uscita il PCM dai secondi dati e chiama alla_fine quando ha
    finito, e torna un oggetto con terminate(); durata sono i secondi da
    dichiarare; emulato dice se ripartendo il convertitore rende da capo.
    Per il server: dimensione, tipo, nuova_richiesta() e leggi(); chiudi()
    ferma tutto e libera la RAM."""

    def __init__(self, avvia, durata, emulato=False, finestra=None):
        self._avvia = avvia
        self.durata = float(durata)
        self.emulato = emulato
        self.frequenza = frequenza_per(self.durata)
        self.al_secondo = self.frequenza * QUADRO
        self.totale_pcm = min(int(self.durata * self.frequenza) * QUADRO, MASSIMO_DEL_WAV // QUADRO * QUADRO)
        self.dimensione = INTESTAZIONE + self.totale_pcm
        self.tipo = TIPO
        self.finestra = dimensione_della_finestra() if finestra is None else finestra
        self.dietro = int(self.finestra * PARTE_DIETRO) // QUADRO * QUADRO
        self._testa = intestazione(self.totale_pcm, self.frequenza)
        self._cond = threading.Condition()
        self._generazione = 0
        self._base, self._dati, self._finito, self._letto = 0, bytearray(), False, 0
        self._passaggio = None
        self._chiusa = False
        self._richiesta = 0
        # Vero se un passaggio partito dall'inizio non ha scritto niente: il
        # brano non si legge, e il server chiude.
        self.guasta = False
        self.ripartenze = 0
        self.convertiti = 0
        self._avvia_da(0)

    def _avvia_da(self, inizio):
        """Fa ripartire il convertitore dal byte di PCM inizio: i dati di prima
        non valgono piu'."""
        with self._cond:
            if self._chiusa:
                return
            self._generazione += 1
            generazione = self._generazione
            self._base, self._dati, self._finito, self._letto = inizio, bytearray(), False, inizio
            vecchio, self._passaggio = self._passaggio, None
            self._cond.notify_all()
        if vecchio is not None:
            vecchio.ferma()
            self.ripartenze += 1
        try:
            passaggio = _Passaggio(self, generazione, self._avvia, inizio / self.al_secondo, self.frequenza)
        except Exception:  # noqa: BLE001 - libmpv fallisce in molti modi: per la sorgente vuol dire che il brano non si legge
            self._fine(generazione, 0)
            return
        with self._cond:
            if generazione == self._generazione and not self._chiusa:
                self._passaggio = passaggio
                return
        passaggio.ferma()

    def _versa(self, generazione, pezzo):
        """Dal filo della pipe: aggiunge i byte, aspettando se la finestra
        davanti a chi legge e' piena. Falso se il passaggio non vale piu'."""
        with self._cond:
            while generazione == self._generazione and self._base + len(self._dati) - self._letto >= self.finestra - self.dietro:
                self._cond.wait(0.5)
            if generazione != self._generazione:
                return False
            self._dati += pezzo
            self.convertiti += len(pezzo)
            troppo = self._letto - self.dietro - self._base
            if troppo > 0:
                troppo = min(troppo, len(self._dati)) // QUADRO * QUADRO
                del self._dati[:troppo]
                self._base += troppo
            self._cond.notify_all()
            return True

    def _fine(self, generazione, scritti):
        with self._cond:
            if generazione != self._generazione:
                return
            self._finito = True
            if scritti == 0 and self._base == 0:
                self.guasta = True
            self._cond.notify_all()

    def nuova_richiesta(self):
        """Il numero di una richiesta nuova dell'apparecchio: le richieste di
        prima non leggono piu'."""
        with self._cond:
            self._richiesta += 1
            self._cond.notify_all()
            return self._richiesta

    def leggi(self, inizio, quanti, richiesta):
        """I byte del WAV da inizio, al piu' quanti, aspettando il
        convertitore: oltre la fine di quello che converte, silenzio fino alla
        dimensione dichiarata. None quando non c'e' piu' niente da dare: la
        sorgente chiusa o guasta, o una richiesta nuova arrivata intanto."""
        quanti = min(quanti, self.dimensione - inizio)
        if quanti <= 0:
            return None
        if inizio < INTESTAZIONE:
            return self._testa[inizio:inizio + min(quanti, INTESTAZIONE - inizio)]
        pcm = inizio - INTESTAZIONE
        with self._cond:
            fine_scritta = self._base + len(self._dati)
            avanti = not self.emulato and pcm > fine_scritta + SECONDI_DA_ASPETTARE * self.al_secondo
            fuori = pcm < self._base or avanti
        if fuori:
            self._avvia_da(pcm - pcm % QUADRO)
        with self._cond:
            self._letto = pcm
            self._cond.notify_all()
            while True:
                if self._chiusa or self.guasta or richiesta != self._richiesta:
                    return None
                fine_scritta = self._base + len(self._dati)
                if self._base <= pcm < fine_scritta:
                    da = pcm - self._base
                    pezzo = bytes(self._dati[da:da + quanti])
                    break
                if self._finito and pcm >= fine_scritta:
                    pezzo = bytes(quanti)
                    break
                if pcm < self._base:
                    # Un'altra richiesta ha fatto ripartire la finestra.
                    return None
                self._cond.wait(0.5)
            self._letto = pcm + len(pezzo)
            self._cond.notify_all()
        return pezzo

    def chiudi(self):
        with self._cond:
            self._chiusa = True
            self._generazione += 1
            vecchio, self._passaggio = self._passaggio, None
            self._dati = bytearray()
            self._cond.notify_all()
        if vecchio is not None:
            vecchio.ferma()
