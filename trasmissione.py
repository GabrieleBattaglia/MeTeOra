# MeTeOra, la trasmissione agli apparecchi Cast: la parte comune a tutte le strade del Chromecast.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 22/10/2026: nasce con la tappa 15 b del piano, prima che Gabriele scelga la strada: il programma ancora non lo usa.

"""Gli apparecchi Cast: Chromecast, speaker Google, soundbar e televisori con
Chromecast integrato, e i gruppi di altoparlanti di Google Home.

Qui c'e' cio' che serve a tutte e tre le strade del prototipo
(prototipi/chromecast.py): i formati che il Chromecast legge da se', la
ricerca degli apparecchi sulla rete, il server da cui prendono i file e i
flussi, e la connessione con il telecomando. Come suonare, mandando il
brano, convertendolo prima in FLAC o trasmettendo l'uscita, lo decide
Gabriele dopo le misure di casa, e da quella scelta dipende anche dove gli
apparecchi compaiono nell'interfaccia.
pychromecast si importa solo dentro le funzioni: se manca, disponibile() lo
dice e il resto di MeTeOra non se ne accorge.
Niente finestre e niente suoni: gli avvisi arrivano dai fili della ricerca,
del server e di pychromecast, e chi li riceve li porta nel filo della
finestra, come gli avvisi del motore.
"""

import contextlib
import http.server
import os
import socket
import threading
import urllib.parse

# I tipi che il server dichiara, per estensione.
TIPI = {
    ".mp3": "audio/mpeg", ".flac": "audio/flac", ".ogg": "audio/ogg", ".oga": "audio/ogg", ".opus": "audio/ogg",
    ".wav": "audio/wav", ".m4a": "audio/mp4", ".mp4": "audio/mp4", ".aac": "audio/aac", ".webm": "audio/webm",
    ".mka": "audio/x-matroska", ".wma": "audio/x-ms-wma", ".ape": "audio/x-ape", ".wv": "audio/x-wavpack",
    ".mpc": "audio/x-musepack", ".aiff": "audio/aiff", ".aif": "audio/aiff", ".dsf": "audio/x-dsf", ".tta": "audio/x-tta",
}
TIPO_SCONOSCIUTO = "application/octet-stream"
# I formati che il Chromecast legge da se', secondo la documentazione di
# Google: MP3, AAC, FLAC, Ogg con Vorbis o Opus, WAV e WebM. Gli altri vanno
# convertiti o trasmessi. Da confermare con la prova dei formati del
# prototipo, sugli apparecchi di Gabriele.
LEGGE_DA_SE = frozenset({".mp3", ".flac", ".ogg", ".oga", ".opus", ".wav", ".m4a", ".mp4", ".aac", ".webm"})
# I tipi di apparecchio come li chiama pychromecast.
TIPO_SOLO_AUDIO = "audio"
TIPO_AUDIO_E_VIDEO = "cast"
TIPO_GRUPPO = "group"
# Quanto si aspetta la connessione a un apparecchio, in secondi.
ATTESA_DELLA_CONNESSIONE = 20.0
# Gli stati del lettore dell'apparecchio, come li manda il Chromecast.
IN_RIPRODUZIONE = "PLAYING"
IN_PAUSA = "PAUSED"
IN_CARICAMENTO = "BUFFERING"
FERMO = "IDLE"
# La porta che l'apparecchio usa per i comandi, che serve anche a trovare la
# strada verso di lui.
PORTA_DEGLI_APPARECCHI = 8009


def disponibile():
    """Vero se pychromecast e' installato."""
    from importlib.util import find_spec

    return find_spec("pychromecast") is not None


def tipo_di(percorso):
    """Il tipo del file da dichiarare all'apparecchio, dall'estensione."""
    return TIPI.get(os.path.splitext(percorso)[1].lower(), TIPO_SCONOSCIUTO)


def legge_da_se(percorso):
    """Vero se il Chromecast legge il file cosi' com'e'."""
    return os.path.splitext(percorso)[1].lower() in LEGGE_DA_SE


def indirizzo_verso(host):
    """L'indirizzo di questo PC sulla strada verso host: con piu' schede di
    rete, o una VPN, e' quello che l'apparecchio puo' raggiungere. Non manda
    niente: chiede soltanto a Windows quale scheda userebbe."""
    prova = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        prova.connect((host, PORTA_DEGLI_APPARECCHI))
        return prova.getsockname()[0]
    finally:
        prova.close()


# La ricerca.

def _descrizione(info):
    return {"uuid": info.uuid, "nome": info.friendly_name or "", "modello": info.model_name or "", "produttore": info.manufacturer or "",
            "tipo": info.cast_type, "indirizzo": info.host, "porta": info.port}


class Ricerca:
    """La ricerca degli apparecchi sulla rete, con mDNS, come fa il telefono
    per il pulsante Trasmetti, finche' non la si ferma. al_cambio() avvisa
    dal filo di zeroconf quando un apparecchio arriva, se ne va o cambia.
    Va fermata solo alla fine, anche dopo le connessioni: una connessione
    caduta ritrova il suo apparecchio con la ricerca, e fermandola si chiude
    anche il suo zeroconf."""

    def __init__(self, al_cambio=None):
        self._al_cambio = al_cambio
        self._browser = None
        self._blocco = threading.Lock()

    @property
    def attiva(self):
        return self._browser is not None

    def avvia(self):
        """Comincia a cercare; se la ricerca e' gia' attiva non fa niente."""
        import zeroconf
        from pychromecast.discovery import CastBrowser, SimpleCastListener

        with self._blocco:
            if self._browser is not None:
                return
            ascolto = SimpleCastListener(self._cambio, self._tolto, self._cambio)
            self._browser = CastBrowser(ascolto, zeroconf.Zeroconf())
            self._browser.start_discovery()

    def ferma(self):
        with self._blocco:
            browser, self._browser = self._browser, None
        if browser is not None:
            browser.stop_discovery()

    def apparecchi(self):
        """Gli apparecchi visti adesso, come dizionari con uuid, nome,
        modello, produttore, tipo (TIPO_SOLO_AUDIO, TIPO_AUDIO_E_VIDEO,
        TIPO_GRUPPO, o None quando la ricerca non lo sa ancora), indirizzo e
        porta. Prima gli apparecchi e poi i gruppi, ciascuno per nome."""
        browser = self._browser
        if browser is None:
            return []
        # dict() copia in un passo solo, mentre zeroconf aggiunge e toglie.
        voci = [_descrizione(info) for info in dict(browser.devices).values()]
        voci.sort(key=lambda v: (v["tipo"] == TIPO_GRUPPO, v["nome"].lower(), str(v["uuid"])))
        return voci

    def connetti(self, uuid, allo_stato=None, attesa=ATTESA_DELLA_CONNESSIONE):
        """La connessione all'apparecchio uuid, gia' pronta, o LookupError se
        la ricerca non lo conosce piu'."""
        browser = self._browser
        info = browser.devices.get(uuid) if browser is not None else None
        if info is None:
            raise LookupError(f"apparecchio {uuid} non trovato")
        return Apparecchio(info, browser.zc, allo_stato, attesa)

    def _cambio(self, _uuid, _servizio):
        if self._al_cambio is not None:
            self._al_cambio()

    def _tolto(self, _uuid, _servizio, _info):
        if self._al_cambio is not None:
            self._al_cambio()


# La connessione.

class Apparecchio:
    """La connessione a un apparecchio, con il telecomando del suo lettore.
    allo_stato(stato) arriva dal filo di pychromecast a ogni stato nuovo: un
    dizionario con stato (IN_RIPRODUZIONE, IN_PAUSA, IN_CARICAMENTO, FERMO),
    posizione e durata in secondi, o None, e motivo, per esempio FINISHED o
    ERROR quando e' fermo; con un caricamento non riuscito lo stato e' FERMO,
    il motivo ERROR e in piu' c'e' codice."""

    def __init__(self, info, zeroconf, allo_stato=None, attesa=ATTESA_DELLA_CONNESSIONE):
        import pychromecast
        from pychromecast.controllers.media import MediaStatusListener

        self.nome = info.friendly_name or ""
        self.modello = info.model_name or ""
        self.tipo = info.cast_type
        self._allo_stato = allo_stato
        self._ultimo = None
        self._cast = pychromecast.get_chromecast_from_cast_info(info, zeroconf)
        self._cast.wait(timeout=attesa)
        self._mc = self._cast.media_controller
        apparecchio = self

        class _Ascolto(MediaStatusListener):
            def new_media_status(self, status):
                apparecchio._nuovo_stato({"stato": status.player_state, "posizione": status.current_time, "durata": status.duration,
                                          "motivo": status.idle_reason})

            def load_media_failed(self, queue_item_id, error_code):
                apparecchio._nuovo_stato({"stato": FERMO, "posizione": None, "durata": None, "motivo": "ERROR", "codice": error_code})

        self._mc.register_status_listener(_Ascolto())

    def _nuovo_stato(self, stato):
        self._ultimo = stato
        if self._allo_stato is not None:
            self._allo_stato(dict(stato))

    @property
    def stato(self):
        """L'ultimo stato arrivato, come quelli di allo_stato, o None."""
        return dict(self._ultimo) if self._ultimo else None

    def aggiorna(self):
        """Chiede all'apparecchio lo stato di adesso, che arriva poi con
        allo_stato: senza, lo stato e' l'ultimo che l'apparecchio ha mandato
        da se'."""
        self._mc.update_status()

    @property
    def posizione(self):
        """I secondi del brano adesso, contando il tempo passato dall'ultimo
        stato se suona; None se non si sa."""
        stato = self._mc.status
        return stato.adjusted_current_time if stato is not None else None

    def suona(self, indirizzo, tipo, titolo=None, inizio=None, in_diretta=False):
        """Fa suonare all'apparecchio cio' che sta a indirizzo, dai secondi
        inizio se dati. in_diretta per un flusso senza fine, come una radio:
        l'apparecchio non ci salta dentro."""
        self._mc.play_media(indirizzo, tipo, title=titolo, current_time=inizio, stream_type="LIVE" if in_diretta else "BUFFERED")

    def pausa(self):
        self._mc.pause()

    def riprendi(self):
        self._mc.play()

    def ferma(self):
        self._mc.stop()

    def vai_a(self, secondi):
        self._mc.seek(max(0.0, float(secondi)))

    @property
    def volume(self):
        """Il volume dell'apparecchio, da 0 a 1, o None se non si sa."""
        stato = self._cast.status
        return stato.volume_level if stato is not None else None

    @volume.setter
    def volume(self, valore):
        self._cast.set_volume(max(0.0, min(1.0, float(valore))))

    def chiudi(self):
        """Ferma il lettore e chiude l'app dell'apparecchio, che torna libero
        per gli altri, poi chiude la connessione. Un apparecchio che non
        risponde piu' non ferma la chiusura."""
        for passo in (self._mc.stop, self._cast.quit_app):
            # Si sta chiudendo: un apparecchio sparito non ha piu' niente da dire.
            with contextlib.suppress(Exception):
                passo()
        self._cast.disconnect(timeout=5)


# Il server.

class _Gestore(http.server.BaseHTTPRequestHandler):
    """/file/<numero><estensione> e /flusso/<nome>; il resto e' 404."""

    def log_message(self, formato, *argomenti):
        self.server.proprietario.annota(f"{self.client_address[0]}: {formato % argomenti}")

    def do_HEAD(self):
        self._rispondi(solo_intestazioni=True)

    def do_GET(self):
        self._rispondi(solo_intestazioni=False)

    def _rispondi(self, solo_intestazioni):
        percorso = urllib.parse.urlparse(self.path).path
        proprietario = self.server.proprietario
        try:
            if percorso.startswith("/flusso/"):
                flusso = proprietario.flusso(percorso[len("/flusso/"):])
                if flusso is not None:
                    self._manda_il_flusso(*flusso, solo_intestazioni)
                    return
            elif percorso.startswith("/file/"):
                file = proprietario.file(os.path.splitext(percorso[len("/file/"):])[0])
                if file is not None:
                    self._manda_il_file(file, solo_intestazioni)
                    return
            self.send_error(404)
        except OSError:
            # L'apparecchio chiude la connessione quando ha letto quanto gli
            # serve, o quando cambia brano: e' normale.
            pass

    def _manda_il_file(self, percorso, solo_intestazioni):
        dimensione = os.path.getsize(percorso)
        intervallo = _intervallo(self.headers.get("Range"), dimensione)
        if intervallo == "fuori":
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{dimensione}")
            self.end_headers()
            return
        inizio, fine = intervallo or (0, dimensione - 1)
        self.send_response(206 if intervallo else 200)
        self.send_header("Content-Type", tipo_di(percorso))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(fine - inizio + 1))
        if intervallo:
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

    def _manda_il_flusso(self, scrivi, tipo, solo_intestazioni):
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if not solo_intestazioni:
            scrivi(self.wfile)


def _intervallo(richiesta, dimensione):
    """L'intervallo di byte di un'intestazione Range, come (inizio, fine)
    compresi; None senza Range, o con un Range che non si capisce, che vale
    il file intero; "fuori" se comincia oltre la fine. Del primo intervallo
    soltanto: gli apparecchi non ne chiedono di piu'."""
    if not richiesta or not richiesta.startswith("bytes="):
        return None
    da, trattino, a = richiesta[len("bytes="):].split(",")[0].strip().partition("-")
    if not trattino or not (da.isdigit() or a.isdigit()) or (da and not da.isdigit()) or (a and not a.isdigit()):
        return None
    if da:
        inizio = int(da)
        fine = min(int(a), dimensione - 1) if a else dimensione - 1
    else:
        inizio, fine = max(0, dimensione - int(a)), dimensione - 1
    return "fuori" if inizio >= dimensione or inizio > fine else (inizio, fine)


class Server:
    """Il piccolo server HTTP da cui gli apparecchi prendono file e flussi.
    Ascolta sull'indirizzo dato, quello della rete di casa che dice
    indirizzo_verso, sulla porta data o, con 0, su una libera. Ogni file e
    ogni flusso ha un indirizzo suo, e cio' che non e' stato pubblicato
    risponde 404: dal PC esce solo cio' che si e' mandato.
    La prima volta Windows chiede il permesso del firewall, che va dato per
    le reti private, o l'apparecchio non arriva al PC.
    al_registro(testo), se c'e', riceve dal filo del server una riga per
    ogni richiesta, per capire che cosa chiede l'apparecchio."""

    def __init__(self, indirizzo, porta=0, al_registro=None):
        self._al_registro = al_registro
        self._blocco = threading.Lock()
        self._file = {}
        self._numeri = {}
        self._flussi = {}
        self._server = http.server.ThreadingHTTPServer((indirizzo, porta), _Gestore)
        self._server.proprietario = self
        self._filo = threading.Thread(target=self._server.serve_forever, name="MeTeOra, server degli apparecchi Cast", daemon=True)
        self._filo.start()

    @property
    def base(self):
        indirizzo, porta = self._server.server_address[:2]
        return f"http://{indirizzo}:{porta}"

    def pubblica_file(self, percorso):
        """L'indirizzo da cui l'apparecchio prende il file; lo stesso file ha
        sempre lo stesso indirizzo. L'estensione resta in fondo, perche' il
        Chromecast la guarda."""
        percorso = os.path.abspath(percorso)
        with self._blocco:
            numero = self._numeri.get(percorso)
            if numero is None:
                numero = self._numeri[percorso] = str(len(self._numeri) + 1)
                self._file[numero] = percorso
        return f"{self.base}/file/{numero}{os.path.splitext(percorso)[1].lower()}"

    def pubblica_flusso(self, nome, scrivi, tipo):
        """L'indirizzo di un flusso: a ogni richiesta il server chiama
        scrivi(uscita) nel filo della connessione, e scrivi scrive finche'
        vuole; un OSError vuol dire che l'apparecchio ha chiuso. nome con
        l'estensione, per esempio uscita.wav."""
        with self._blocco:
            self._flussi[nome] = (scrivi, tipo)
        return f"{self.base}/flusso/{urllib.parse.quote(nome)}"

    def ritira(self):
        """Toglie tutto cio' che e' stato pubblicato: da qui in poi 404."""
        with self._blocco:
            self._file.clear()
            self._numeri.clear()
            self._flussi.clear()

    def file(self, numero):
        with self._blocco:
            return self._file.get(numero)

    def flusso(self, nome):
        with self._blocco:
            return self._flussi.get(urllib.parse.unquote(nome))

    def annota(self, testo):
        if self._al_registro is not None:
            self._al_registro(testo)

    def ferma(self):
        self._server.shutdown()
        self._server.server_close()
