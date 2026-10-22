# MeTeOra, prototipi: il Chromecast e le due strade della tappa 15 b, da misurare a casa.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 22/10/2026: nasce con la tappa 15 b del piano, prima di toccare il programma.

"""Il prototipo del Chromecast: trova gli apparecchi, prova le due strade e
misura quanto tardano.

Le due strade, dal piano:
  A, mandare il brano: un piccolo server sul PC da' il file, il Chromecast lo
     scarica e lo suona da se', e il prototipo fa da telecomando. Un formato
     che il Chromecast non legge si converte prima in FLAC con libmpv, che
     lo fa in un attimo: provato in ufficio, 20 secondi in 0,09 secondi.
  B, trasmettere l'uscita: il brano, reso in memoria da libmpv come lo
     suonerebbe MeTeOra, va al Chromecast come un flusso WAV senza fine, al
     ritmo dell'orologio, come una radio; pausa e salti li fa il PC.
Le misure sono due. Quella dell'apparecchio, solo per la strada A: quanto
passa fra il comando e la risposta del Chromecast. Quella dell'orecchio, per
tutte e due: dopo ogni comando si preme Spazio appena se ne sente l'effetto,
e al tempo si tolgono i riflessi, misurati prima con cinque bip del PC.
Il dettaglio va in coda a prototipi/chromecast_misure.txt, con la data e la
macchina, anche le richieste che il Chromecast fa al server; a schermo solo
i riassunti.
Serve pychromecast: python -m pip install pychromecast. La prima volta che il
server parte Windows chiede il permesso del firewall: va dato per le reti
private, o il Chromecast non arriva al PC.
Uso: python prototipi/chromecast.py [--anticipo SECONDI] [--porta NUMERO]
L'anticipo e' quanto la strada B manda avanti rispetto all'orologio, mezzo
secondo di partenza: piu' e' grande, piu' tardano i comandi.
"""

import argparse
import datetime
import http.server
import os
import random
import socket
import statistics
import tempfile
import threading
import time
import urllib.parse

import ambiente  # noqa: F401

QUI = os.path.dirname(os.path.abspath(__file__))
FILE_DELLE_MISURE = os.path.join(QUI, "chromecast_misure.txt")
PORTA = 8765
FREQUENZA = 44100
CANALI = 2
BYTE_PER_CAMPIONE = 2
BYTE_PER_FRAME = CANALI * BYTE_PER_CAMPIONE
# I pezzi della strada B: 20 millesimi di secondo.
FRAME_PER_PEZZO = FREQUENZA // 50
ATTESA_DELLA_RICERCA = 8.0
SECONDI_DEL_SALTO = 10
PASSO_DEL_VOLUME = 0.05
# La strada B tiene il brano in memoria: cinque minuti sono 53 MB.
MASSIMO_DELLA_STRADA_B = 300
# La prova dei formati: quanto si aspetta che un file parta, e quanto lo si
# ascolta per dire che suona davvero.
ATTESA_DELLA_PARTENZA = 10.0
ASCOLTO_DELLA_PROVA = 3.0
# I tipi che il server dichiara. Quelli che il Chromecast dice di leggere
# sono MP3, AAC, FLAC, Ogg con Vorbis o Opus, WAV e WebM; gli altri si provano
# lo stesso, per saperlo dalla prova e non dalla documentazione.
TIPI = {
    ".mp3": "audio/mpeg", ".flac": "audio/flac", ".ogg": "audio/ogg", ".oga": "audio/ogg", ".opus": "audio/ogg",
    ".wav": "audio/wav", ".m4a": "audio/mp4", ".mp4": "audio/mp4", ".aac": "audio/aac", ".webm": "audio/webm",
    ".mka": "audio/x-matroska", ".wma": "audio/x-ms-wma", ".ape": "audio/x-ape", ".wv": "audio/x-wavpack",
    ".mpc": "audio/x-musepack", ".aiff": "audio/aiff", ".aif": "audio/aiff", ".dsf": "audio/x-dsf", ".tta": "audio/x-tta",
}
NOMI_DEI_TIPI = {"audio": "solo audio", "group": "gruppo", "cast": "audio e video"}


class Registro:
    """Le righe del file delle misure, e le misure raccolte per i riassunti."""

    def __init__(self):
        self.misure = {}
        self._blocco = threading.Lock()
        self.scrivi(f"Sessione del {datetime.datetime.now():%d/%m/%Y alle %H:%M} su {socket.gethostname()}.")

    def scrivi(self, testo):
        with self._blocco, open(FILE_DELLE_MISURE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now():%H:%M:%S} {testo}\n")

    def misura(self, nome, secondi):
        self.misure.setdefault(nome, []).append(secondi)
        self.scrivi(f"Misura, {nome}: {secondi:.3f} s.")

    def riassunto(self):
        """Una riga per misura: quante, la mediana, la piu' breve e la piu' lunga."""
        righe = []
        for nome, valori in self.misure.items():
            if len(valori) == 1:
                righe.append(f"{nome}: {valori[0]:.2f} s.")
            else:
                righe.append(f"{nome}: {len(valori)} misure, mediana {statistics.median(valori):.2f} s, da {min(valori):.2f} a {max(valori):.2f}.")
        return righe


def dice(testo):
    print(testo, flush=True)


def tasto(prompt, attesa=None):
    from GBUtils import key

    return key(prompt, attesa=attesa, alla_scadenza=None)


def svuota_la_tastiera():
    """I tasti premuti prima del tempo non devono valere come risposta."""
    while tasto("", attesa=0) is not None:
        pass


# Il server: i file della strada A e il flusso della strada B.

class Flusso:
    """La strada B: il brano in memoria, s16 stereo a 44100, mandato come un
    WAV senza fine al ritmo dell'orologio, con anticipo secondi di vantaggio.
    In pausa si manda silenzio, perche' un flusso che si ferma il Chromecast
    lo chiude. Una connessione nuova prende il posto della vecchia."""

    def __init__(self, pcm, anticipo):
        self.pcm = pcm
        self.frame = len(pcm) // BYTE_PER_FRAME
        self.anticipo = anticipo
        self.posizione = 0
        self.pausa = False
        self._blocco = threading.Lock()
        self._connessione = 0

    @staticmethod
    def intestazione():
        # Le dimensioni al massimo: per chi legge il WAV non finisce mai.
        import struct

        senza_fine = 0xFFFFFFFF
        return (b"RIFF" + struct.pack("<I", senza_fine) + b"WAVE" + b"fmt " + struct.pack("<IHHIIHH", 16, 1, CANALI, FREQUENZA,
                FREQUENZA * BYTE_PER_FRAME, BYTE_PER_FRAME, BYTE_PER_CAMPIONE * 8) + b"data" + struct.pack("<I", senza_fine))

    def servi(self, uscita):
        with self._blocco:
            self._connessione += 1
            mia = self._connessione
        uscita.write(self.intestazione())
        partenza = time.perf_counter()
        mandati = 0
        silenzio = bytes(FRAME_PER_PEZZO * BYTE_PER_FRAME)
        while True:
            dovuti = int((time.perf_counter() - partenza + self.anticipo) * FREQUENZA)
            pezzi = []
            with self._blocco:
                if mia != self._connessione:
                    return
                while mandati < dovuti:
                    quanti = min(FRAME_PER_PEZZO, dovuti - mandati)
                    if self.pausa or self.posizione >= self.frame:
                        pezzi.append(silenzio[:quanti * BYTE_PER_FRAME])
                    else:
                        presi = min(quanti, self.frame - self.posizione)
                        inizio = self.posizione * BYTE_PER_FRAME
                        pezzi.append(self.pcm[inizio:inizio + presi * BYTE_PER_FRAME] + silenzio[:(quanti - presi) * BYTE_PER_FRAME])
                        self.posizione += presi
                    mandati += quanti
            if pezzi:
                uscita.write(b"".join(pezzi))
            time.sleep(0.01)

    def pausa_o_ripresa(self):
        with self._blocco:
            self.pausa = not self.pausa
            return "pausa" if self.pausa else "ripresa"

    def salta(self, secondi):
        with self._blocco:
            self.posizione = max(0, min(self.frame, self.posizione + int(secondi * FREQUENZA)))


class Gestore(http.server.BaseHTTPRequestHandler):
    """/file/<numero><estensione> per la strada A, /flusso.wav per la B."""

    def log_message(self, formato, *argomenti):
        self.server.registro.scrivi(f"Server, {self.client_address[0]}: {formato % argomenti}")

    def do_HEAD(self):
        self._rispondi(solo_intestazioni=True)

    def do_GET(self):
        self._rispondi(solo_intestazioni=False)

    def _rispondi(self, solo_intestazioni):
        percorso = urllib.parse.urlparse(self.path).path
        intervallo = self.headers.get("Range")
        if intervallo:
            self.server.registro.scrivi(f"Server, chiesto {self.command} {percorso} con Range {intervallo}.")
        try:
            if percorso == "/flusso.wav" and self.server.flusso is not None:
                self._manda_il_flusso(solo_intestazioni)
                return
            if percorso.startswith("/file/"):
                numero = os.path.splitext(percorso[len("/file/"):])[0]
                if numero in self.server.file_serviti:
                    self._manda_il_file(self.server.file_serviti[numero], solo_intestazioni, intervallo)
                    return
            self.send_error(404)
        except (ConnectionError, OSError):
            # Il Chromecast chiude le connessioni quando ha letto quanto gli
            # serve, o quando cambia brano: e' normale.
            pass

    def _intestazioni_comuni(self, tipo):
        self.send_header("Content-Type", tipo)
        self.send_header("Access-Control-Allow-Origin", "*")

    def _manda_il_file(self, percorso, solo_intestazioni, intervallo):
        dimensione = os.path.getsize(percorso)
        inizio, fine, parziale = 0, dimensione - 1, False
        if intervallo and intervallo.startswith("bytes="):
            da, _, a = intervallo[len("bytes="):].split(",")[0].strip().partition("-")
            if da:
                inizio = int(da)
                fine = min(int(a), dimensione - 1) if a else dimensione - 1
            elif a:
                inizio = max(0, dimensione - int(a))
            parziale = True
            if inizio > fine:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{dimensione}")
                self.end_headers()
                return
        self.send_response(206 if parziale else 200)
        self._intestazioni_comuni(TIPI.get(os.path.splitext(percorso)[1].lower(), "application/octet-stream"))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(fine - inizio + 1))
        if parziale:
            self.send_header("Content-Range", f"bytes {inizio}-{fine}/{dimensione}")
        self.end_headers()
        if solo_intestazioni:
            return
        restano = fine - inizio + 1
        with open(percorso, "rb") as f:
            f.seek(inizio)
            while restano > 0:
                pezzo = f.read(min(65536, restano))
                if not pezzo:
                    break
                self.wfile.write(pezzo)
                restano -= len(pezzo)

    def _manda_il_flusso(self, solo_intestazioni):
        self.send_response(200)
        self._intestazioni_comuni("audio/wav")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if not solo_intestazioni:
            self.server.flusso.servi(self.wfile)


def avvia_il_server(indirizzo, porta, registro):
    server = http.server.ThreadingHTTPServer((indirizzo, porta), Gestore)
    server.registro = registro
    server.file_serviti = {}
    server.flusso = None
    threading.Thread(target=server.serve_forever, name="Server del Chromecast", daemon=True).start()
    return server


def indirizzo_verso(host):
    """L'indirizzo di questo PC sulla rete del Chromecast."""
    prova = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        prova.connect((host, 8009))
        return prova.getsockname()[0]
    finally:
        prova.close()


# Gli apparecchi.

def cerca(registro):
    """Gli apparecchi Cast della rete, in ATTESA_DELLA_RICERCA secondi, e il
    browser che li tiene aggiornati."""
    import pychromecast
    import zeroconf

    trovati = []
    partenza = time.perf_counter()

    def aggiunto(uuid, _servizio):
        trovati.append((uuid, time.perf_counter() - partenza))

    zc = zeroconf.Zeroconf()
    browser = pychromecast.discovery.CastBrowser(pychromecast.discovery.SimpleCastListener(aggiunto), zc)
    browser.start_discovery()
    dice(f"Cerco gli apparecchi Cast per {ATTESA_DELLA_RICERCA:.0f} secondi.")
    time.sleep(ATTESA_DELLA_RICERCA)
    apparecchi = []
    for uuid, quando in trovati:
        info = browser.devices.get(uuid)
        if info is None:
            continue
        apparecchi.append(info)
        registro.scrivi(f"Trovato dopo {quando:.2f} s: {info.friendly_name}, {info.model_name}, {info.manufacturer}, {nome_del_tipo(info)}, {info.host}:{info.port}.")
        registro.misura("ricerca, primo avviso di ogni apparecchio", quando)
    # Prima gli apparecchi, poi i gruppi di Google Home.
    apparecchi.sort(key=lambda i: (i.cast_type == "group", (i.friendly_name or "").lower()))
    return apparecchi, browser


def nome_del_tipo(info):
    """Il tipo da leggere; la ricerca a volte non lo sa ancora, e lo dice la
    connessione."""
    return NOMI_DEI_TIPI.get(info.cast_type, info.cast_type or "tipo non ancora noto")


class Apparecchio:
    """La connessione a un apparecchio, con gli stati che manda."""

    def __init__(self, info, zc, registro):
        import pychromecast
        from pychromecast.controllers.media import MediaStatusListener

        self.info = info
        self.registro = registro
        self.stati = []
        self.errori = []
        partenza = time.perf_counter()
        self.cast = pychromecast.get_chromecast_from_cast_info(info, zc)
        self.cast.wait(timeout=20)
        registro.misura("connessione", time.perf_counter() - partenza)
        self.mc = self.cast.media_controller
        apparecchio = self

        class Ascolto(MediaStatusListener):
            def new_media_status(self, status):
                apparecchio.stati.append((time.perf_counter(), status.player_state, status.current_time, status.idle_reason))
                registro.scrivi(f"Stato: {status.player_state}, a {status.current_time}, motivo {status.idle_reason}.")

            def load_media_failed(self, queue_item_id, error_code):
                apparecchio.errori.append((time.perf_counter(), error_code))
                registro.scrivi(f"Caricamento non riuscito: elemento {queue_item_id}, errore {error_code}.")

        self.mc.register_status_listener(Ascolto())

    def volume(self):
        stato = self.cast.status
        return stato.volume_level if stato else None

    def aspetta(self, da, voluti, limite):
        """I secondi da da al primo stato fra voluti, o None. Si ferma prima
        se arriva un errore di caricamento o un IDLE per errore."""
        fine = time.perf_counter() + limite
        while time.perf_counter() < fine:
            for quando, stato, _tempo, motivo in list(self.stati):
                if quando >= da and stato in voluti:
                    return quando - da
                if quando >= da and stato == "IDLE" and motivo == "ERROR":
                    return None
            if any(quando >= da for quando, _codice in self.errori):
                return None
            time.sleep(0.02)
        return None

    def chiudi(self):
        try:
            self.cast.quit_app()
        except Exception as e:  # noqa: BLE001 - si sta chiudendo: lo si annota soltanto
            self.registro.scrivi(f"Chiusura dell'app del Chromecast non riuscita: {e}.")
        self.cast.disconnect(timeout=5)


# Le misure.

def misura_i_riflessi(registro):
    """La mediana di cinque risposte a un bip del PC, che poi si toglie dalle
    misure dell'orecchio. Comprende anche il ritardo della scheda del PC,
    qualche decina di millesimi."""
    import numpy
    from GBUtils import Acusticator

    dice("I riflessi: cinque bip dal PC, a intervalli casuali. Premi Spazio appena senti ciascun bip.")
    # Un attimo di silenzio apre la scheda: il primo bip non paga l'apertura.
    Acusticator.riproduci(numpy.zeros((441, 2), dtype=numpy.float32))
    tasto("\rPremi un tasto per cominciare.\r")
    tempi = []
    for _ in range(5):
        time.sleep(random.uniform(1.5, 3.5))  # noqa: S311 - l'intervallo fra due bip non e' un segreto
        svuota_la_tastiera()
        partenza = time.perf_counter()
        Acusticator(["a5", 0.08, 0, 0.5])
        if tasto("", attesa=5) == " ":
            tempi.append(time.perf_counter() - partenza)
    if not tempi:
        dice("Nessuna risposta: tengo un quarto di secondo.")
        return 0.25
    riflessi = statistics.median(tempi)
    registro.misura("riflessi", riflessi)
    dice(f"Riflessi: {riflessi:.2f} s, mediana di {len(tempi)} risposte.")
    return riflessi


def ascolta(registro, nome, partenza, riflessi):
    """Aspetta Spazio, al massimo trenta secondi, e misura dall'istante
    partenza; Esc o un altro tasto rinunciano."""
    risposta = tasto("\rSpazio appena senti; un altro tasto se non senti niente.\r", attesa=30)
    if risposta != " ":
        registro.scrivi(f"{nome}: nessuna risposta dell'orecchio ({risposta!r}).")
        dice(f"{nome}: non misurato.")
        return
    ritardo = time.perf_counter() - partenza - riflessi
    registro.misura(nome, ritardo)
    dice(f"{nome}: {ritardo:.2f} s.")


GUIDA_DEI_COMANDI = "P pausa e ripresa, A indietro e D avanti di 10 secondi, meno e piu' il volume, X basta."


def telecomando(apparecchio, registro, riflessi, strada, comandi):
    """I comandi di una strada, ciascuno misurato con l'orecchio, e per la
    strada A anche con la risposta dell'apparecchio. comandi e' un dizionario
    tasto -> funzione che restituisce il nome del comando."""
    dice(GUIDA_DEI_COMANDI)
    while True:
        scelta = tasto("\rComando: P, A, D, meno, piu', X.\r")
        if scelta in ("x", "X", "\x1b"):
            return
        funzione = comandi.get(scelta.lower() if isinstance(scelta, str) else scelta)
        if funzione is None:
            dice(GUIDA_DEI_COMANDI)
            continue
        svuota_la_tastiera()
        partenza = time.perf_counter()
        try:
            nome = funzione()
        except Exception as e:  # noqa: BLE001 - un comando che non va si dice e si annota, e il prototipo prosegue
            registro.scrivi(f"Strada {strada}, comando non riuscito: {e!r}.")
            dice(f"Comando non riuscito: {e}.")
            continue
        risposta = time.perf_counter() - partenza
        if strada.startswith("A"):
            registro.misura(f"strada {strada}, risposta dell'apparecchio, {nome}", risposta)
        ascolta(registro, f"strada {strada}, orecchio, {nome}", partenza, riflessi)


def volume_di(apparecchio, delta):
    attuale = apparecchio.volume() or 0.0
    nuovo = max(0.0, min(1.0, attuale + delta))
    apparecchio.cast.set_volume(nuovo)
    return f"volume {'su' if delta > 0 else 'giu'}"


def converti_in_flac(percorso, cartella, registro):
    """Il brano convertito in FLAC da libmpv, nella cartella temporanea: il
    percorso del file nuovo, o None se la conversione non va."""
    import mpv

    from motore import OPZIONI_DI_BASE

    uscita = os.path.join(cartella, f"conversione_{len(os.listdir(cartella)) + 1}.flac")
    partenza = time.perf_counter()
    try:
        lettore = mpv.MPV(**{**OPZIONI_DI_BASE, "o": uscita, "of": "flac", "oac": "flac"})
        try:
            lettore.play(percorso)
            lettore.wait_for_playback(timeout=300)
        finally:
            lettore.terminate()
    except Exception as e:  # noqa: BLE001 - libmpv fallisce in molti modi: per la prova vuol dire che non converte
        registro.scrivi(f"Conversione in FLAC non riuscita per {percorso}: {e!r}.")
        return None
    if not os.path.isfile(uscita) or not os.path.getsize(uscita):
        registro.scrivi(f"Conversione in FLAC vuota per {percorso}.")
        return None
    registro.misura("conversione in FLAC", time.perf_counter() - partenza)
    return uscita


def strada_a(apparecchio, server, base, registro, riflessi, cartella=None):
    """Manda un brano scelto e lo comanda; con cartella, prima lo converte in
    FLAC li' dentro."""
    percorso = input("Percorso del brano da mandare: ").strip().strip('"')
    if not os.path.isfile(percorso):
        dice("Il file non c'e'.")
        return
    strada = "A"
    if cartella is not None:
        dice("Converto il brano in FLAC.")
        convertito = converti_in_flac(percorso, cartella, registro)
        if convertito is None:
            dice("La conversione non e' riuscita: il file forse non si apre.")
            return
        dice(f"Convertito in {registro.misure['conversione in FLAC'][-1]:.1f} s.")
        percorso, strada = convertito, "A convertita"
    numero = str(len(server.file_serviti) + 1)
    estensione = os.path.splitext(percorso)[1].lower()
    server.file_serviti[numero] = percorso
    indirizzo = f"{base}/file/{numero}{estensione}"
    registro.scrivi(f"Strada {strada}: {percorso}, servito come {indirizzo}, tipo {TIPI.get(estensione, 'application/octet-stream')}.")
    svuota_la_tastiera()
    partenza = time.perf_counter()
    apparecchio.mc.play_media(indirizzo, TIPI.get(estensione, "application/octet-stream"), title=os.path.basename(percorso), stream_type="BUFFERED")
    dice("Mandato: premi Spazio appena senti la musica.")
    ascolta(registro, f"strada {strada}, orecchio, avvio", partenza, riflessi)
    avvio = apparecchio.aspetta(partenza, ("PLAYING",), ATTESA_DELLA_PARTENZA)
    if avvio is None:
        dice("Il Chromecast non dice di suonare: il file forse non lo legge. Guarda il file delle misure.")
        return
    registro.misura(f"strada {strada}, avvio riferito dall'apparecchio", avvio)

    def pausa_o_ripresa():
        if apparecchio.mc.status.player_state == "PAUSED":
            apparecchio.mc.play()
            return "ripresa"
        apparecchio.mc.pause()
        return "pausa"

    def salto(secondi):
        apparecchio.mc.update_status()
        posizione = apparecchio.mc.status.adjusted_current_time or 0.0
        apparecchio.mc.seek(max(0.0, posizione + secondi))
        return "avanti" if secondi > 0 else "indietro"

    telecomando(apparecchio, registro, riflessi, strada, {
        "p": pausa_o_ripresa, "a": lambda: salto(-SECONDI_DEL_SALTO), "d": lambda: salto(SECONDI_DEL_SALTO),
        "-": lambda: volume_di(apparecchio, -PASSO_DEL_VOLUME), "+": lambda: volume_di(apparecchio, PASSO_DEL_VOLUME),
    })
    apparecchio.mc.stop()


def file_per_estensione(cartella, limite=20000):
    """Un file per ogni estensione di TIPI, il primo che si trova, guardando
    al piu' limite file."""
    scelti, visti = {}, 0
    for radice, _cartelle, nomi in os.walk(cartella):
        for nome in sorted(nomi):
            estensione = os.path.splitext(nome)[1].lower()
            if estensione in TIPI and estensione not in scelti:
                scelti[estensione] = os.path.join(radice, nome)
            visti += 1
            if visti >= limite or len(scelti) == len(TIPI):
                return scelti
    return scelti


def suona_per_prova(apparecchio, server, base, percorso):
    """Manda un file, aspetta che suoni e lo ascolta qualche secondo: vero e
    i secondi della partenza se la posizione e' andata avanti, falso e il
    motivo se no."""
    numero = str(len(server.file_serviti) + 1)
    estensione = os.path.splitext(percorso)[1].lower()
    server.file_serviti[numero] = percorso
    partenza = time.perf_counter()
    apparecchio.mc.play_media(f"{base}/file/{numero}{estensione}", TIPI[estensione], title=os.path.basename(percorso), stream_type="BUFFERED")
    avvio = apparecchio.aspetta(partenza, ("PLAYING",), ATTESA_DELLA_PARTENZA)
    if avvio is None:
        esito = (False, "non suona")
    else:
        time.sleep(ASCOLTO_DELLA_PROVA)
        apparecchio.mc.update_status()
        time.sleep(0.5)
        stato = apparecchio.mc.status
        va = stato.player_state == "PLAYING" and (stato.current_time or 0) > 1
        esito = (True, f"partito in {avvio:.2f} s") if va else (False, f"parte ma si ferma ({stato.player_state})")
    apparecchio.mc.stop()
    apparecchio.aspetta(time.perf_counter(), ("IDLE",), 5)
    return esito


def prova_dei_formati(apparecchio, server, base, registro, cartella_temporanea):
    """Un file per estensione: si manda e si ascolta qualche secondo; se non
    suona, si riprova convertito in FLAC."""
    cartella = input("Cartella della musica da cui prendere un file per formato: ").strip().strip('"')
    if not os.path.isdir(cartella):
        dice("La cartella non c'e'.")
        return
    scelti = file_per_estensione(cartella)
    dice(f"Formati trovati: {len(scelti)}. Ognuno suona qualche secondo.")
    esiti = []
    for estensione, percorso in sorted(scelti.items()):
        va, come = suona_per_prova(apparecchio, server, base, percorso)
        esito = f"suona, {come}" if va else come
        if not va:
            convertito = converti_in_flac(percorso, cartella_temporanea, registro)
            if convertito is None:
                esito += ", e non si converte"
            else:
                va, come = suona_per_prova(apparecchio, server, base, convertito)
                esito += f"; convertito in FLAC in {registro.misure['conversione in FLAC'][-1]:.1f} s suona, {come}" if va else f"; convertito in FLAC {come}"
        riga = f"{estensione[1:].upper()}: {esito}, {os.path.basename(percorso)}."
        esiti.append(riga)
        registro.scrivi(f"Formato, {riga}")
        dice(riga)
    registro.scrivi(f"Formati: {'; '.join(esiti)}")


def rendi_in_memoria(percorso, massimo):
    """Il brano reso da libmpv come s16 stereo a 44100, al piu' massimo
    secondi: l'uscita su file di mpv rende tutto d'un fiato."""
    import mpv

    from motore import OPZIONI_DI_BASE

    with tempfile.TemporaryDirectory() as cartella:
        uscita = os.path.join(cartella, "resa.raw")
        lettore = mpv.MPV(**{**OPZIONI_DI_BASE, "ao": "pcm", "vo": "null", "video": "no", "ao_pcm_file": uscita, "ao_pcm_waveheader": False,
                             "audio_format": "s16", "audio_samplerate": FREQUENZA, "audio_channels": "stereo", "end": str(massimo)})
        try:
            lettore.play(percorso)
            lettore.wait_for_playback(timeout=120)
        finally:
            lettore.terminate()
        with open(uscita, "rb") as f:
            return f.read()


def strada_b(apparecchio, server, base, registro, riflessi, anticipo):
    """Rende un brano in memoria e lo trasmette come flusso continuo."""
    percorso = input("Percorso del brano da trasmettere: ").strip().strip('"')
    if not os.path.isfile(percorso):
        dice("Il file non c'e'.")
        return
    dice("Rendo il brano in memoria.")
    partenza = time.perf_counter()
    pcm = rendi_in_memoria(percorso, MASSIMO_DELLA_STRADA_B)
    secondi = len(pcm) / (FREQUENZA * BYTE_PER_FRAME)
    if not secondi:
        dice("libmpv non ha reso niente: il file forse non si apre.")
        return
    registro.scrivi(f"Strada B: {percorso}, {secondi:.1f} s resi in {time.perf_counter() - partenza:.1f} s, anticipo {anticipo} s.")
    server.flusso = Flusso(pcm, anticipo)
    svuota_la_tastiera()
    partenza = time.perf_counter()
    apparecchio.mc.play_media(f"{base}/flusso.wav", "audio/wav", title=f"MeTeOra, {os.path.basename(percorso)}", stream_type="LIVE")
    dice("Trasmesso: premi Spazio appena senti la musica.")
    ascolta(registro, "strada B, orecchio, avvio", partenza, riflessi)
    avvio = apparecchio.aspetta(partenza, ("PLAYING",), ATTESA_DELLA_PARTENZA)
    if avvio is None:
        dice("Il Chromecast non dice di suonare il flusso. Guarda il file delle misure.")
    else:
        registro.misura("strada B, avvio riferito dall'apparecchio", avvio)

    def salto(secondi):
        server.flusso.salta(secondi)
        return "avanti" if secondi > 0 else "indietro"

    telecomando(apparecchio, registro, riflessi, "B", {
        "p": server.flusso.pausa_o_ripresa, "a": lambda: salto(-SECONDI_DEL_SALTO), "d": lambda: salto(SECONDI_DEL_SALTO),
        "-": lambda: volume_di(apparecchio, -PASSO_DEL_VOLUME), "+": lambda: volume_di(apparecchio, PASSO_DEL_VOLUME),
    })
    apparecchio.mc.stop()
    server.flusso = None


def scegli(apparecchi):
    for numero, info in enumerate(apparecchi, 1):
        dice(f"{numero}. {info.friendly_name}, {info.model_name}, {nome_del_tipo(info)}, {info.host}.")
    risposta = input("Numero dell'apparecchio, Invio per nessuno: ").strip()
    if risposta.isdigit() and 1 <= int(risposta) <= len(apparecchi):
        return apparecchi[int(risposta) - 1]
    return None


def principale():
    parametri = argparse.ArgumentParser(description="Il prototipo del Chromecast di MeTeOra.")
    parametri.add_argument("--anticipo", type=float, default=0.5, help="i secondi di vantaggio del flusso della strada B")
    parametri.add_argument("--porta", type=int, default=PORTA, help="la porta del server sul PC")
    argomenti = parametri.parse_args()
    from importlib.util import find_spec

    if find_spec("pychromecast") is None:
        dice("Manca pychromecast: installalo con python -m pip install pychromecast e rilancia il prototipo.")
        return
    registro = Registro()
    from importlib.metadata import version

    registro.scrivi(f"pychromecast {version('pychromecast')}, anticipo {argomenti.anticipo} s, porta {argomenti.porta}.")
    apparecchi, browser = cerca(registro)
    if not apparecchi:
        dice("Nessun apparecchio Cast sulla rete. Controlla che il PC e gli speaker siano sulla stessa rete, non quella degli ospiti.")
        browser.stop_discovery()
        return
    dice(f"Apparecchi trovati: {len(apparecchi)}.")
    apparecchio = server = None
    riflessi = 0.25
    # I file convertiti in FLAC, che spariscono all'uscita.
    # Un file ancora aperto dal server non deve fermare l'uscita.
    conversioni = tempfile.TemporaryDirectory(prefix="meteora_chromecast_", ignore_cleanup_errors=True)
    try:
        info = scegli(apparecchi)
        if info is None:
            return
        dice(f"Mi collego a {info.friendly_name}.")
        apparecchio = Apparecchio(info, browser.zc, registro)
        indirizzo = indirizzo_verso(info.host)
        server = avvia_il_server(indirizzo, argomenti.porta, registro)
        base = f"http://{indirizzo}:{argomenti.porta}"
        registro.scrivi(f"Apparecchio: {info.friendly_name}, {info.model_name}; server su {base}; volume {apparecchio.volume()}.")
        volume = apparecchio.volume()
        dice(f"Collegata a {info.friendly_name}, volume {round(volume * 100) if volume is not None else '?'}. Il server e' su {base}.")
        while True:
            scelta = tasto("\rR riflessi, A manda il brano, C manda convertito in FLAC, F formati, B trasmetti l'uscita, Q esci.\r")
            scelta = scelta.lower() if isinstance(scelta, str) else scelta
            if scelta in ("q", "\x1b"):
                break
            try:
                if scelta == "r":
                    riflessi = misura_i_riflessi(registro)
                elif scelta == "a":
                    strada_a(apparecchio, server, base, registro, riflessi)
                elif scelta == "c":
                    strada_a(apparecchio, server, base, registro, riflessi, cartella=conversioni.name)
                elif scelta == "f":
                    prova_dei_formati(apparecchio, server, base, registro, conversioni.name)
                elif scelta == "b":
                    strada_b(apparecchio, server, base, registro, riflessi, argomenti.anticipo)
            except Exception as e:  # noqa: BLE001 - nel collaudo un guasto si annota e si va avanti, invece di perdere la sessione
                registro.scrivi(f"Guasto nella scelta {scelta!r}: {e!r}.")
                dice(f"Non riuscito: {e}. Il dettaglio e' nel file delle misure.")
    finally:
        if apparecchio is not None:
            apparecchio.chiudi()
        if server is not None:
            server.shutdown()
        browser.stop_discovery()
        conversioni.cleanup()
        righe = registro.riassunto()
        for riga in righe:
            registro.scrivi(f"Riassunto, {riga}")
        dice("Riassunto:" if righe else "Nessuna misura.")
        for riga in righe:
            dice(riga)
        dice(f"Il dettaglio e' in {FILE_DELLE_MISURE}.")


if __name__ == "__main__":
    principale()
