# MeTeOra, le prove della trasmissione agli apparecchi Cast: formati, ricerca, connessione e server.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 22/10/2026: nasce con trasmissione.py, tappa 15 b del piano.

"""Le prove di trasmissione, senza apparecchi e senza rete.

La ricerca e la connessione usano dei finti al posto di CastBrowser, di
zeroconf e del Chromecast di pychromecast: nessuna prova manda niente sulla
rete di casa. Il server e' quello vero, su 127.0.0.1 e su una porta libera.
"""

import types
import urllib.error
import urllib.request
import uuid

import pytest

import trasmissione


def test_formati():
    assert trasmissione.tipo_di(r"C:\m\Brano.FLAC") == "audio/flac"
    assert trasmissione.tipo_di("brano.opus") == "audio/ogg"
    assert trasmissione.tipo_di("brano.sconosciuto") == trasmissione.TIPO_SCONOSCIUTO
    assert trasmissione.legge_da_se("a.mp3") and trasmissione.legge_da_se("a.M4A")
    assert not trasmissione.legge_da_se("a.ape") and not trasmissione.legge_da_se("a.sid")
    # Tutto cio' che si legge da se' ha un tipo da dichiarare.
    assert set(trasmissione.TIPI) >= trasmissione.LEGGE_DA_SE


def test_disponibile(monkeypatch):
    import importlib.util

    assert trasmissione.disponibile()
    monkeypatch.setattr(importlib.util, "find_spec", lambda nome: None)
    assert not trasmissione.disponibile()


def test_indirizzo_verso():
    assert trasmissione.indirizzo_verso("127.0.0.1") == "127.0.0.1"


def _info(nome, tipo=trasmissione.TIPO_SOLO_AUDIO, modello="Google Nest Mini"):
    return types.SimpleNamespace(uuid=uuid.uuid4(), friendly_name=nome, model_name=modello, manufacturer="Google Inc.", cast_type=tipo,
                                 host="192.168.1.30", port=8009)


class _BrowserFinto:
    """CastBrowser: tiene gli apparecchi e chiama l'ascolto come zeroconf."""

    ultimo = None

    def __init__(self, ascolto, zc):
        self.ascolto, self.zc = ascolto, zc
        self.devices = {}
        self.avviato = self.fermato = False
        _BrowserFinto.ultimo = self

    def start_discovery(self):
        self.avviato = True

    def stop_discovery(self):
        self.fermato = True

    def aggiungi(self, info):
        self.devices[info.uuid] = info
        self.ascolto.add_cast(info.uuid, "servizio")

    def togli(self, info):
        del self.devices[info.uuid]
        self.ascolto.remove_cast(info.uuid, "servizio", info)


@pytest.fixture
def browser_finto(monkeypatch):
    import pychromecast.discovery
    import zeroconf

    monkeypatch.setattr(pychromecast.discovery, "CastBrowser", _BrowserFinto)
    monkeypatch.setattr(zeroconf, "Zeroconf", lambda: "zeroconf finto")
    _BrowserFinto.ultimo = None
    return _BrowserFinto


def test_ricerca(browser_finto):
    avvisi = []
    ricerca = trasmissione.Ricerca(al_cambio=lambda: avvisi.append(True))
    assert not ricerca.attiva and ricerca.apparecchi() == []
    ricerca.avvia()
    browser = browser_finto.ultimo
    assert ricerca.attiva and browser.avviato and browser.zc == "zeroconf finto"
    # Una seconda partenza non crea un'altra ricerca.
    ricerca.avvia()
    assert browser_finto.ultimo is browser
    cucina, gruppo, ambeo = _info("cucina"), _info("Tutta la casa", trasmissione.TIPO_GRUPPO), _info("Ambeo", trasmissione.TIPO_AUDIO_E_VIDEO)
    for info in (gruppo, cucina, ambeo):
        browser.aggiungi(info)
    assert len(avvisi) == 3
    # Prima gli apparecchi, per nome senza badare alle maiuscole, poi i gruppi.
    elenco = ricerca.apparecchi()
    assert [v["nome"] for v in elenco] == ["Ambeo", "cucina", "Tutta la casa"]
    assert elenco[1] == {"uuid": cucina.uuid, "nome": "cucina", "modello": "Google Nest Mini", "produttore": "Google Inc.",
                         "tipo": trasmissione.TIPO_SOLO_AUDIO, "indirizzo": "192.168.1.30", "porta": 8009}
    browser.togli(cucina)
    assert len(avvisi) == 4 and [v["nome"] for v in ricerca.apparecchi()] == ["Ambeo", "Tutta la casa"]
    with pytest.raises(LookupError):
        ricerca.connetti(cucina.uuid)
    ricerca.ferma()
    assert browser.fermato and not ricerca.attiva and ricerca.apparecchi() == []
    # Fermata due volte non fa niente.
    ricerca.ferma()


class _LettoreFinto:
    """Il media controller: annota i comandi e tiene l'ascolto degli stati."""

    def __init__(self):
        self.chiamate = []
        self.ascolto = None
        self.status = types.SimpleNamespace(adjusted_current_time=12.5)

    def register_status_listener(self, ascolto):
        self.ascolto = ascolto

    def play_media(self, indirizzo, tipo, **opzioni):
        self.chiamate.append(("play_media", indirizzo, tipo, opzioni))

    def pause(self):
        self.chiamate.append("pause")

    def play(self):
        self.chiamate.append("play")

    def stop(self):
        self.chiamate.append("stop")

    def seek(self, secondi):
        self.chiamate.append(("seek", secondi))

    def update_status(self):
        self.chiamate.append("update_status")


class _CastFinto:
    def __init__(self):
        self.media_controller = _LettoreFinto()
        self.status = types.SimpleNamespace(volume_level=0.4)
        self.chiamate = []

    def wait(self, timeout=None):
        self.chiamate.append(("wait", timeout))

    def set_volume(self, valore):
        self.chiamate.append(("volume", valore))

    def quit_app(self):
        self.chiamate.append("quit_app")

    def disconnect(self, timeout=None):
        self.chiamate.append("disconnect")


def test_apparecchio(browser_finto, monkeypatch):
    import pychromecast

    cast = _CastFinto()
    chieste = []
    monkeypatch.setattr(pychromecast, "get_chromecast_from_cast_info", lambda info, zc: chieste.append((info, zc)) or cast)
    ricerca = trasmissione.Ricerca()
    ricerca.avvia()
    ambeo = _info("Ambeo", trasmissione.TIPO_AUDIO_E_VIDEO, "AMBEO Soundbar Plus")
    browser_finto.ultimo.aggiungi(ambeo)
    stati = []
    apparecchio = ricerca.connetti(ambeo.uuid, allo_stato=stati.append, attesa=3)
    assert chieste == [(ambeo, "zeroconf finto")] and cast.chiamate == [("wait", 3)]
    assert (apparecchio.nome, apparecchio.modello, apparecchio.tipo) == ("Ambeo", "AMBEO Soundbar Plus", trasmissione.TIPO_AUDIO_E_VIDEO)
    lettore = cast.media_controller
    # I comandi arrivano al lettore dell'apparecchio.
    apparecchio.suona("http://pc/file/1.flac", "audio/flac", titolo="Brano")
    apparecchio.suona("http://pc/flusso/uscita.wav", "audio/wav", inizio=None, in_diretta=True)
    apparecchio.suona("http://pc/file/1.flac", "audio/flac", inizio=42.0)
    apparecchio.pausa()
    apparecchio.riprendi()
    apparecchio.vai_a(-5)
    apparecchio.vai_a("30")
    apparecchio.aggiorna()
    apparecchio.ferma()
    assert lettore.chiamate == [
        ("play_media", "http://pc/file/1.flac", "audio/flac", {"title": "Brano", "current_time": None, "stream_type": "BUFFERED"}),
        ("play_media", "http://pc/flusso/uscita.wav", "audio/wav", {"title": None, "current_time": None, "stream_type": "LIVE"}),
        ("play_media", "http://pc/file/1.flac", "audio/flac", {"title": None, "current_time": 42.0, "stream_type": "BUFFERED"}),
        "pause", "play", ("seek", 0.0), ("seek", 30.0), "update_status", "stop",
    ]
    assert apparecchio.posizione == 12.5
    # Il volume si legge e si scrive da 0 a 1.
    assert apparecchio.volume == 0.4
    apparecchio.volume = 1.7
    apparecchio.volume = -1
    assert cast.chiamate[-2:] == [("volume", 1.0), ("volume", 0.0)]
    # Gli stati del lettore arrivano come dizionari, anche il caricamento non riuscito.
    assert apparecchio.stato is None
    lettore.ascolto.new_media_status(types.SimpleNamespace(player_state="PLAYING", current_time=3.0, duration=180.0, idle_reason=None))
    lettore.ascolto.load_media_failed(1, 104)
    assert stati == [{"stato": "PLAYING", "posizione": 3.0, "durata": 180.0, "motivo": None},
                     {"stato": trasmissione.FERMO, "posizione": None, "durata": None, "motivo": "ERROR", "codice": 104}]
    assert apparecchio.stato == stati[-1]
    # La chiusura arriva in fondo anche con un apparecchio che non risponde piu'.
    lettore.stop = lambda: (_ for _ in ()).throw(OSError("sparito"))
    apparecchio.chiudi()
    assert cast.chiamate[-2:] == ["quit_app", "disconnect"]
    ricerca.ferma()


@pytest.fixture
def server(tmp_path):
    righe = []
    s = trasmissione.Server("127.0.0.1", 0, al_registro=righe.append)
    s.righe = righe
    yield s
    s.ferma()


def _leggi(indirizzo, metodo="GET", intervallo=None):
    # Solo gli indirizzi http del server di prova, su 127.0.0.1.
    richiesta = urllib.request.Request(indirizzo, method=metodo, headers={"Range": intervallo} if intervallo else {})  # noqa: S310
    with urllib.request.urlopen(richiesta, timeout=5) as risposta:  # noqa: S310
        return risposta.status, dict(risposta.headers), risposta.read()


def test_server_dei_file(server, tmp_path):
    contenuto = bytes(range(256)) * 10
    brano = tmp_path / "Brano.FLAC"
    brano.write_bytes(contenuto)
    indirizzo = server.pubblica_file(str(brano))
    assert indirizzo.startswith(server.base + "/file/") and indirizzo.endswith(".flac")
    # Lo stesso file ha sempre lo stesso indirizzo.
    assert server.pubblica_file(str(brano)) == indirizzo
    stato, intestazioni, corpo = _leggi(indirizzo, "HEAD")
    assert stato == 200 and corpo == b"" and intestazioni["Content-Length"] == str(len(contenuto))
    assert intestazioni["Content-Type"] == "audio/flac" and intestazioni["Accept-Ranges"] == "bytes"
    assert _leggi(indirizzo)[2] == contenuto
    # I pezzi che il Chromecast chiede per saltare.
    stato, intestazioni, corpo = _leggi(indirizzo, intervallo="bytes=100-199")
    assert stato == 206 and corpo == contenuto[100:200] and intestazioni["Content-Range"] == f"bytes 100-199/{len(contenuto)}"
    assert _leggi(indirizzo, intervallo="bytes=2500-")[2] == contenuto[2500:]
    assert _leggi(indirizzo, intervallo="bytes=-60")[2] == contenuto[-60:]
    assert _leggi(indirizzo, intervallo="bytes=2000-999999")[2] == contenuto[2000:]
    # Un Range che non si capisce vale il file intero.
    assert _leggi(indirizzo, intervallo="bytes=a-b")[:1] == (200,)
    with pytest.raises(urllib.error.HTTPError) as fuori:
        _leggi(indirizzo, intervallo=f"bytes={len(contenuto)}-")
    assert fuori.value.code == 416
    assert any("GET /file/" in riga for riga in server.righe)


def test_server_risponde_solo_a_cio_che_e_pubblicato(server, tmp_path):
    brano = tmp_path / "brano.mp3"
    brano.write_bytes(b"mp3")
    indirizzo = server.pubblica_file(str(brano))
    for altro in (server.base + "/file/99.mp3", server.base + "/", server.base + "/flusso/niente.wav", server.base + "/../brano.mp3"):
        with pytest.raises(urllib.error.HTTPError) as errore:
            _leggi(altro)
        assert errore.value.code == 404
    server.ritira()
    with pytest.raises(urllib.error.HTTPError) as errore:
        _leggi(indirizzo)
    assert errore.value.code == 404


def test_server_dei_flussi(server):
    def scrivi(uscita):
        for pezzo in (b"RIFF", b"dati", b"fine"):
            uscita.write(pezzo)

    indirizzo = server.pubblica_flusso("uscita di MeTeOra.wav", scrivi, "audio/wav")
    assert indirizzo == server.base + "/flusso/uscita%20di%20MeTeOra.wav"
    stato, intestazioni, corpo = _leggi(indirizzo)
    assert stato == 200 and corpo == b"RIFFdatifine"
    assert intestazioni["Content-Type"] == "audio/wav" and intestazioni["Cache-Control"] == "no-cache" and "Content-Length" not in intestazioni
    assert _leggi(indirizzo, "HEAD")[2] == b""


def test_intervallo():
    assert trasmissione._intervallo(None, 100) is None
    assert trasmissione._intervallo("bytes=10-19", 100) == (10, 19)
    assert trasmissione._intervallo("bytes=10-19, 30-39", 100) == (10, 19)
    assert trasmissione._intervallo("bytes=90-", 100) == (90, 99)
    assert trasmissione._intervallo("bytes=-10", 100) == (90, 99)
    assert trasmissione._intervallo("bytes=-500", 100) == (0, 99)
    assert trasmissione._intervallo("bytes=100-", 100) == "fuori"
    assert trasmissione._intervallo("bytes=50-10", 100) == "fuori"
    assert trasmissione._intervallo("bytes=-", 100) is None
    assert trasmissione._intervallo("righe=1-2", 100) is None
    assert trasmissione._intervallo("bytes=0-", 0) == "fuori"
