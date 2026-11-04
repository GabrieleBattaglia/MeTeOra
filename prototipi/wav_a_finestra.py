# MeTeOra, prototipi: il WAV a finestra in RAM per gli speaker Cast, da misurare prima di toccare il programma.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/11/2026: nasce con la tappa 17 del piano, dalla domanda di Gabriele sulle conversioni senza disco.

"""Il WAV a finestra: la conversione per lo speaker Cast senza il disco.

Uso, dalla cartella di MeTeOra:
  python prototipi\\wav_a_finestra.py BRANO [--sottobrano N] [--locale | --speaker NOME] [--salto SECONDI] [--per SECONDI]

Oggi MeTeOra converte in FLAC su disco, tutto, prima di mandare il brano:
il FLAC dice la sua lunghezza solo alla fine. Qui libmpv, in modo codifica,
scrive il brano come PCM a 16 bit, stereo, 48 kHz in una pipe con nome; un
filo la versa in una finestra di RAM, il 5% della RAM libera fra 32 e 512 MB;
il server dichiara un WAV della dimensione che la durata dice, e serve ogni
intervallo di byte dalla finestra, aspettando i byte che il convertitore non
ha ancora scritto. Il convertitore si ferma quando e' troppo avanti rispetto
a chi legge, e riparte quando quello legge. Un intervallo fuori dalla
finestra fa ripartire la conversione da quel punto. Se il convertitore
finisce prima della dimensione dichiarata il resto e' silenzio, se va oltre
si taglia: la fine arriva puntuale.

Con --locale fa la parte dello speaker un libmpv sull'uscita nulla, che
legge dal server come farebbe lui: si prova il prototipo senza suonare
niente. Con --speaker NOME suona sull'apparecchio Cast che si chiama cosi':
si fa solo con il via di Gabriele. --salto, dopo tanti secondi, salta a
meta' del brano e poi vicino alla fine; --per dice quanti secondi lasciarlo
suonare prima dei salti. Il dettaglio di ogni richiesta, delle attese e
degli stati va in coda a prototipi/wav_a_finestra_misure.txt; a schermo i
riassunti.
"""

import argparse
import ctypes
import datetime
import http.server
import os
import socket
import struct
import sys
import threading
import time
from ctypes import wintypes

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

FREQUENZA = 48000
CANALI = 2
QUADRO = CANALI * 2
BYTE_AL_SECONDO = FREQUENZA * QUADRO
INTESTAZIONE = 44
# La finestra: una parte della RAM libera, fra un minimo e un massimo
# (Gabriele, 4 novembre 2026); dietro al punto letto se ne tiene un quarto,
# per i salti indietro brevi.
PARTE_DELLA_RAM = 0.05
FINESTRA_MINIMA = 32 * 2**20
FINESTRA_MASSIMA = 512 * 2**20
PARTE_DIETRO = 0.25
# Fin dove, avanti, si aspetta il convertitore invece di farlo ripartire. I
# SID e la musica delle console si rendono emulando dall'inizio anche con
# start: per loro, in avanti, si aspetta sempre la conversione in corsa
# (prova del 4 novembre 2026: il secondo 92 di Outrun Europa, ripartendo,
# aspettava 5,9 secondi).
SALTO_DA_ASPETTARE = 10 * BYTE_AL_SECONDO
PEZZO = 65536
MISURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wav_a_finestra_misure.txt")


class Registro:
    """Le righe del dettaglio, con il tempo dalla partenza, in coda al file
    delle misure; a schermo solo quelle da dire."""

    def __init__(self):
        self.partenza = time.perf_counter()
        self._blocco = threading.Lock()
        self._file = open(MISURE, "a", encoding="utf-8")  # noqa: SIM115 - resta aperto per tutta la prova
        self.scrivi(f"Prova del {datetime.datetime.now():%d/%m/%Y %H:%M}, su {socket.gethostname()}.")

    def scrivi(self, testo, a_schermo=False):
        riga = f"{time.perf_counter() - self.partenza:9.3f} {testo}"
        with self._blocco:
            self._file.write(riga + "\n")
            self._file.flush()
        if a_schermo:
            print(testo, flush=True)

    def chiudi(self):
        self._file.close()


def ram_libera():
    class Stato(ctypes.Structure):
        _fields_ = [("dwLength", wintypes.DWORD), ("dwMemoryLoad", wintypes.DWORD)] + [
            (nome, ctypes.c_ulonglong) for nome in ("ullTotalPhys", "ullAvailPhys", "ullTotalPageFile", "ullAvailPageFile", "ullTotalVirtual",
                "ullAvailVirtual", "ullAvailExtendedVirtual")]

    stato = Stato()
    stato.dwLength = ctypes.sizeof(stato)
    ctypes.WinDLL("kernel32").GlobalMemoryStatusEx(ctypes.byref(stato))
    return stato.ullAvailPhys


def dimensione_della_finestra():
    byte = min(FINESTRA_MASSIMA, max(FINESTRA_MINIMA, int(ram_libera() * PARTE_DELLA_RAM)))
    return byte - byte % QUADRO


def intestazione(totale_pcm):
    """L'intestazione di un WAV PCM a 16 bit con totale_pcm byte di campioni."""
    return (b"RIFF" + struct.pack("<I", 36 + totale_pcm) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, CANALI, FREQUENZA, BYTE_AL_SECONDO, QUADRO, 16)
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
            errore = ctypes.get_last_error()
            # ERROR_BROKEN_PIPE, ERROR_PIPE_NOT_CONNECTED: chi scrive ha chiuso.
            if errore in (109, 233):
                return b""
            raise OSError(errore, "ReadFile")
        return spazio.raw[:letti.value]

    def chiudi(self):
        if self._maniglia:
            self._k.CloseHandle(self._maniglia)
            self._maniglia = None


class Conversione:
    """Un passaggio di libmpv dai secondi dati in poi: scrive nella pipe, e un
    filo la versa nella finestra. ferma() lo interrompe."""

    def __init__(self, finestra, generazione, percorso, sottobrano, secondi):
        import motore

        self._finestra, self._generazione = finestra, generazione
        self.pipe = Pipe(f"meteora_wav_{os.getpid()}_{generazione}")
        self._finito = threading.Event()
        self._filo = threading.Thread(target=self._versa, name="prototipo, pipe", daemon=True)
        self._filo.start()
        brano = motore._Brano(percorso, sottobrano, secondi or None)
        opzioni = {**motore.OPZIONI_DI_BASE, "o": self.pipe.percorso, "of": "s16le", "oac": "pcm_s16le",
            "audio_channels": "stereo", "audio_samplerate": FREQUENZA, "audio_format": "s16"}
        self._mpv = motore.mpv.MPV(**opzioni)
        self._mpv.register_stream_protocol("sid", motore._apri_sid)
        self._mpv.register_stream_protocol("chip", motore._apri_chip)
        self._mpv.register_event_callback(self._evento)
        testo = ",".join(f"{chiave}={valore}" for chiave, valore in brano.opzioni.items())
        self._mpv.command("loadfile", brano.indirizzo, "replace", "-1", testo)

    def _evento(self, evento):
        if evento.event_id.value == self._finestra.mpv.MpvEventID.END_FILE:
            self._finito.set()
            # Se libmpv non ha mai aperto la pipe, chi aspetta torna.
            threading.Thread(target=self.pipe.sblocca, daemon=True).start()

    def _versa(self):
        try:
            self.pipe.aspetta_chi_scrive()
            while True:
                pezzo = self.pipe.leggi()
                if not pezzo or not self._finestra.versa(self._generazione, pezzo):
                    break
        except OSError as errore:
            self._finestra.registro.scrivi(f"Pipe {self._generazione}: {errore}")
        finally:
            self._finestra.fine(self._generazione)

    def ferma(self):
        threading.Thread(target=self._chiudi, daemon=True).start()

    def _chiudi(self):
        try:
            self._mpv.terminate()
        finally:
            self.pipe.sblocca()
            self._filo.join(5)
            self.pipe.chiudi()


class Finestra:
    """La finestra di RAM sul brano convertito: base e' il primo byte di PCM
    che tiene, dati quelli che seguono. Chi legge dice dove legge; il
    convertitore non va oltre la finestra davanti a lui, e quello che resta
    troppo indietro si toglie."""

    def __init__(self, percorso, sottobrano, durata, registro):
        import motore

        self.mpv = motore.mpv
        self.percorso, self.sottobrano, self.registro = percorso, sottobrano, registro
        self.emulato = motore.sottobrano_risolto(percorso, sottobrano) is not None
        self.totale_pcm = int(durata * FREQUENZA) * QUADRO
        self.dimensione = dimensione_della_finestra()
        self.dietro = int(self.dimensione * PARTE_DIETRO) // QUADRO * QUADRO
        self._cond = threading.Condition()
        self.generazione = 0
        self.base, self.dati, self.finito, self.letto = 0, bytearray(), False, 0
        self.conversione = None
        self.richiesta = 0
        self.ripartenze, self.convertiti, self.attese = 0, 0, []
        registro.scrivi(f"Finestra di {self.dimensione / 2**20:.0f} MB, {self.dimensione / BYTE_AL_SECONDO:.0f} secondi, "
                        f"con {self.dietro / BYTE_AL_SECONDO:.0f} dietro; brano di {durata:.1f} secondi, {self.totale_pcm / 2**20:.1f} MB di PCM.", True)
        self.avvia(0)

    def avvia(self, inizio):
        with self._cond:
            self.generazione += 1
            generazione = self.generazione
            self.base, self.dati, self.finito, self.letto = inizio, bytearray(), False, inizio
            vecchia, self.conversione = self.conversione, None
            self._cond.notify_all()
        if vecchia is not None:
            vecchia.ferma()
            self.ripartenze += 1
        self.registro.scrivi(f"Conversione {generazione} da {inizio / BYTE_AL_SECONDO:.2f} s.")
        conversione = Conversione(self, generazione, self.percorso, self.sottobrano, inizio / BYTE_AL_SECONDO)
        with self._cond:
            if generazione == self.generazione:
                self.conversione = conversione
            else:
                conversione.ferma()

    def versa(self, generazione, pezzo):
        """Dal filo della pipe: aggiunge i byte, aspettando se la finestra
        davanti a chi legge e' piena. Falso se la conversione non vale piu'."""
        with self._cond:
            while generazione == self.generazione and self.base + len(self.dati) - self.letto >= self.dimensione - self.dietro:
                self._cond.wait(0.5)
            if generazione != self.generazione:
                return False
            self.dati += pezzo
            self.convertiti += len(pezzo)
            troppo = self.letto - self.dietro - self.base
            if troppo > 0:
                troppo = min(troppo, len(self.dati)) // QUADRO * QUADRO
                del self.dati[:troppo]
                self.base += troppo
            self._cond.notify_all()
            return True

    def fine(self, generazione):
        with self._cond:
            if generazione == self.generazione:
                self.finito = True
                self.registro.scrivi(f"Conversione {generazione} finita a {(self.base + len(self.dati)) / BYTE_AL_SECONDO:.2f} s.")
                self._cond.notify_all()

    def leggi(self, inizio, quanti):
        """I byte di PCM da inizio, al piu' quanti, aspettando il convertitore;
        oltre la fine di quello che converte, silenzio fino al totale."""
        quanti = min(quanti, self.totale_pcm - inizio)
        with self._cond:
            avanti = not self.emulato and inizio > self.base + len(self.dati) + SALTO_DA_ASPETTARE
            fuori = inizio < self.base or avanti
        if fuori:
            self.registro.scrivi(f"Fuori dalla finestra a {inizio / BYTE_AL_SECONDO:.2f} s: si riparte.")
            self.avvia(inizio - inizio % QUADRO)
        partenza = time.perf_counter()
        with self._cond:
            self.letto = inizio
            self._cond.notify_all()
            while True:
                fine_scritta = self.base + len(self.dati)
                if self.base <= inizio < fine_scritta:
                    da = inizio - self.base
                    pezzo = bytes(self.dati[da:da + quanti])
                    break
                if self.finito and inizio >= fine_scritta:
                    pezzo = bytes(quanti)
                    break
                if inizio < self.base:
                    # Un'altra richiesta ha fatto ripartire la finestra.
                    return None
                self._cond.wait(0.5)
            self.letto = inizio + len(pezzo)
            self._cond.notify_all()
        attesa = time.perf_counter() - partenza
        if attesa > 0.05:
            self.attese.append(attesa)
        return pezzo

    def nuova_richiesta(self):
        with self._cond:
            self.richiesta += 1
            return self.richiesta

    def chiudi(self):
        with self._cond:
            self.generazione += 1
            vecchia, self.conversione = self.conversione, None
            self._cond.notify_all()
        if vecchia is not None:
            vecchia.ferma()


class Gestore(http.server.BaseHTTPRequestHandler):
    """/brano.wav, con gli intervalli di byte; il resto e' 404."""

    def log_message(self, formato, *argomenti):
        self.server.finestra.registro.scrivi(f"{self.client_address[0]}: {formato % argomenti}")

    def do_HEAD(self):
        self._rispondi(solo_intestazioni=True)

    def do_GET(self):
        self._rispondi(solo_intestazioni=False)

    def _rispondi(self, solo_intestazioni):
        import trasmissione

        finestra = self.server.finestra
        if self.path.split("?")[0] != "/brano.wav":
            self.send_error(404)
            return
        dimensione = INTESTAZIONE + finestra.totale_pcm
        richiesta = self.headers.get("Range")
        intervallo = trasmissione._intervallo(richiesta, dimensione)
        if intervallo == "fuori":
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{dimensione}")
            self.end_headers()
            return
        inizio, fine = intervallo or (0, dimensione - 1)
        numero = finestra.nuova_richiesta()
        finestra.registro.scrivi(f"Richiesta {numero}: {self.command} {richiesta or 'tutto'}, da {max(0, inizio - INTESTAZIONE) / BYTE_AL_SECONDO:.2f} s.")
        self.send_response(206 if intervallo else 200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(fine - inizio + 1))
        if intervallo:
            self.send_header("Content-Range", f"bytes {inizio}-{fine}/{dimensione}")
        self.end_headers()
        if solo_intestazioni:
            return
        testa = intestazione(finestra.totale_pcm)
        posizione, partenza, motivo = inizio, time.perf_counter(), "fine"
        try:
            while posizione <= fine:
                if finestra.richiesta != numero:
                    motivo = "superata da una richiesta nuova"
                    break
                if posizione < INTESTAZIONE:
                    pezzo = testa[posizione:min(INTESTAZIONE, fine + 1)]
                else:
                    pezzo = finestra.leggi(posizione - INTESTAZIONE, min(PEZZO, fine + 1 - posizione))
                    if pezzo is None:
                        motivo = "finestra ripartita"
                        break
                self.wfile.write(pezzo)
                posizione += len(pezzo)
        except OSError:
            motivo = "chiusa dall'apparecchio"
        servite = posizione - inizio
        durata = time.perf_counter() - partenza
        finestra.registro.scrivi(f"Richiesta {numero}: {servite / 2**20:.2f} MB in {durata:.2f} s, fino a "
                                 f"{max(0, posizione - INTESTAZIONE) / BYTE_AL_SECONDO:.2f} s; {motivo}.")


def durata_di(percorso, sottobrano):
    """I secondi del brano: dei sottobrani dal database, degli altri da libmpv."""
    import motore

    if motore.sottobrano_risolto(percorso, sottobrano) is not None:
        return motore.durata_del_sottobrano(percorso, motore.sottobrano_risolto(percorso, sottobrano))
    lettore = motore.mpv.MPV(**{**motore.OPZIONI_DI_BASE, "ao": "null", "pause": True})
    try:
        lettore.loadfile(percorso)
        fine = time.monotonic() + 15
        while time.monotonic() < fine:
            if lettore.duration:
                return float(lettore.duration)
            time.sleep(0.05)
    finally:
        lettore.terminate()
    raise RuntimeError(f"Non so quanto dura {percorso}.")


def prova_locale(indirizzo, durata, registro, per, salto):
    """Un libmpv sull'uscita nulla legge dal server come lo speaker: la
    partenza, i salti e la fine."""
    import motore

    eventi = []
    lettore = motore.mpv.MPV(**{**motore.OPZIONI_DI_BASE, "ao": "null"})
    lettore.register_event_callback(lambda e: eventi.append((time.perf_counter(), e.event_id.value)))

    def aspetta(evento, da, limite=60):
        fine = time.perf_counter() + limite
        while time.perf_counter() < fine:
            if any(quando >= da and numero == evento for quando, numero in list(eventi)):
                return next(quando for quando, numero in eventi if quando >= da and numero == evento) - da
            time.sleep(0.01)
        return None

    try:
        partenza = time.perf_counter()
        lettore.loadfile(indirizzo)
        tempo = aspetta(motore.mpv.MpvEventID.PLAYBACK_RESTART, partenza)
        registro.scrivi(f"Locale: parte dopo {tempo if tempo is None else round(tempo, 3)} s; durata letta {lettore.duration}.", True)
        time.sleep(per)
        for verso in (durata / 2, max(0.0, durata - salto)):
            da = time.perf_counter()
            lettore.seek(verso, "absolute")
            tempo = aspetta(motore.mpv.MpvEventID.PLAYBACK_RESTART, da)
            registro.scrivi(f"Locale: salto a {verso:.1f} s in {tempo if tempo is None else round(tempo, 3)} s.", True)
            time.sleep(min(per, 3))
        da = time.perf_counter()
        tempo = aspetta(motore.mpv.MpvEventID.END_FILE, da, limite=salto + 30)
        registro.scrivi(f"Locale: fine dopo {tempo if tempo is None else round(tempo, 2)} s dall'ultimo salto, a {salto} s dalla fine.", True)
    finally:
        lettore.terminate()


def prova_sullo_speaker(ricerca, voce, indirizzo, durata, registro, per, salto):
    """Lo speaker Cast vero, con il via di Gabriele: la partenza, i salti e la fine."""
    import trasmissione

    stati = []
    try:
        apparecchio = ricerca.connetti(voce["uuid"], allo_stato=lambda s: (stati.append((time.perf_counter(), s)), registro.scrivi(f"Stato: {s}.")))

        def aspetta(voluto, da, limite=60):
            scadenza = time.perf_counter() + limite
            while time.perf_counter() < scadenza:
                for quando, stato in list(stati):
                    if quando >= da and stato["stato"] == voluto:
                        return quando - da
                time.sleep(0.02)
            return None

        partenza = time.perf_counter()
        apparecchio.suona(indirizzo, "audio/wav", titolo="Prova del WAV a finestra")
        tempo = aspetta(trasmissione.IN_RIPRODUZIONE, partenza)
        registro.scrivi(f"Speaker: suona dopo {tempo if tempo is None else round(tempo, 3)} s.", True)
        time.sleep(per)
        for verso in (durata / 2, max(0.0, durata - salto)):
            da = time.perf_counter()
            apparecchio.vai_a(verso)
            time.sleep(0.3)
            tempo = aspetta(trasmissione.IN_RIPRODUZIONE, da)
            registro.scrivi(f"Speaker: salto a {verso:.1f} s, di nuovo in riproduzione dopo {tempo if tempo is None else round(tempo, 3)} s.", True)
            time.sleep(min(per, 3))
        da = time.perf_counter()
        tempo = aspetta(trasmissione.FERMO, da, limite=salto + 60)
        motivo = next((s.get("motivo") for q, s in reversed(stati) if s["stato"] == trasmissione.FERMO), None)
        registro.scrivi(f"Speaker: fermo dopo {tempo if tempo is None else round(tempo, 2)} s dall'ultimo salto, a {salto} s dalla fine; motivo {motivo}.", True)
        apparecchio.chiudi()
    finally:
        ricerca.ferma()


def principale():
    parser = argparse.ArgumentParser(description="Il WAV a finestra in RAM per gli speaker Cast: il prototipo della tappa 17.")
    parser.add_argument("brano")
    parser.add_argument("--sottobrano", type=int)
    parser.add_argument("--locale", action="store_true", help="un libmpv sull'uscita nulla fa la parte dello speaker")
    parser.add_argument("--speaker", help="il nome dell'apparecchio Cast, solo con il via di Gabriele")
    parser.add_argument("--per", type=float, default=8.0, help="i secondi da suonare prima dei salti")
    parser.add_argument("--salto", type=float, default=10.0, help="l'ultimo salto, a tanti secondi dalla fine")
    argomenti = parser.parse_args()
    import librerie  # noqa: F401 - le DLL di libmpv e dei chip, prima del motore
    import trasmissione

    registro = Registro()
    percorso = os.path.abspath(argomenti.brano)
    durata = durata_di(percorso, argomenti.sottobrano)
    finestra = Finestra(percorso, argomenti.sottobrano, durata, registro)
    ricerca = voce = None
    indirizzo_locale = "127.0.0.1"
    if argomenti.speaker:
        ricerca = trasmissione.Ricerca()
        ricerca.avvia()
        scadenza = time.monotonic() + 15
        while voce is None and time.monotonic() < scadenza:
            voce = next((v for v in ricerca.apparecchi() if v["nome"].lower() == argomenti.speaker.lower()), None)
            time.sleep(0.2)
        if voce is None:
            ricerca.ferma()
            raise SystemExit(f"Non trovo {argomenti.speaker}.")
        indirizzo_locale = trasmissione.indirizzo_verso(voce["indirizzo"])
    server = http.server.ThreadingHTTPServer((indirizzo_locale, 0), Gestore)
    server.daemon_threads = True
    server.finestra = finestra
    threading.Thread(target=server.serve_forever, name="prototipo, server", daemon=True).start()
    indirizzo = f"http://{server.server_address[0]}:{server.server_address[1]}/brano.wav"
    registro.scrivi(f"Server su {indirizzo}.", True)
    try:
        if argomenti.speaker:
            prova_sullo_speaker(ricerca, voce, indirizzo, durata, registro, argomenti.per, argomenti.salto)
        else:
            prova_locale(indirizzo, durata, registro, argomenti.per, argomenti.salto)
    finally:
        attese = sorted(finestra.attese)
        registro.scrivi(f"Riassunto: {finestra.convertiti / 2**20:.1f} MB convertiti, {finestra.ripartenze} ripartenze, "
                        f"{len(attese)} attese dei byte oltre 50 ms, la piu' lunga {attese[-1] if attese else 0:.2f} s.", True)
        server.shutdown()
        finestra.chiudi()
        registro.chiudi()
    return 0


if __name__ == "__main__":
    raise SystemExit(principale())
