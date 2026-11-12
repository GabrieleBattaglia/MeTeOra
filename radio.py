# MeTeOra, le radio in rete: le stazioni di radio-browser.info.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 06/11/2026: nasce con la 3.3.0, tappa 19 c del piano, issue 40. Nella 3.10.0 le pagine, per Mostra altre radio. Nella 3.11.3 gli errori di http.client come ErroreRadio.

"""Le radio in rete (3.3.0, issue 40).

Le stazioni vengono da radio-browser.info, un elenco libero e senza chiave,
con i dati di pubblico dominio: piu' di sessantamila radio di tutto il
mondo, ciascuna con il suo indirizzo, gia' risolto dalle playlist PLS e M3U
dei siti, il paese, la lingua, i generi, il formato e la qualita'. Il ramo
Radio della plancia le mostra per paese, per genere e per lingua, dalle piu'
ascoltate, e le cerca per nome (Gabriele, 6 novembre 2026).
radio-browser chiede a chi lo usa un nome nell'User-Agent e di dire quando
una radio si ascolta, per tenere giusta la classifica delle piu' ascoltate:
lo fa clic. I server sono piu' d'uno, e l'elenco lo da' all.api: se uno non
risponde si prova il seguente. Misure del 6 novembre 2026: ogni domanda
torna in due o quattro decimi di secondo.
Una radio e' una diretta: libmpv ne apre l'indirizzo da se', senza yt-dlp,
e non ha durata. I nomi dei paesi e delle lingue vengono da Windows, nella
sua lingua, come Italia, Germania, Inglese.
"""

import contextlib
import ctypes
import http.client
import json
import threading
import urllib.parse
import urllib.request

import version
from lingua import _
from playlist import Brano

ELENCO_DEI_SERVER = "https://all.api.radio-browser.info/json/servers"
# I server noti, se l'elenco non arriva.
SERVER_DI_RISERVA = ("de1.api.radio-browser.info", "de2.api.radio-browser.info", "fi1.api.radio-browser.info")
ATTESA = 15.0
# Quante radio si chiedono per un paese, un genere, una lingua o una ricerca,
# dalle piu' ascoltate; e quanti generi e lingue, dai piu' numerosi.
RADIO_PER_GRUPPO = 300
GENERI = 100
LINGUE = 80
_GEO_FRIENDLYNAME = 8
_LOCALE_SLOCALIZEDLANGUAGENAME = 0x6F

_server = []
_server_blocco = threading.Lock()


class ErroreRadio(Exception):
    """radio-browser non risponde, o risponde male."""


def _intestazioni():
    return {"User-Agent": f"MeTeOra/{version.VERSION}"}


def _leggi(url):
    richiesta = urllib.request.Request(url, headers=_intestazioni())  # noqa: S310 - i server di radio-browser, in https
    with urllib.request.urlopen(richiesta, timeout=ATTESA) as risposta:  # noqa: S310 - i server di radio-browser, in https
        return json.loads(risposta.read().decode("utf-8", "replace"))


def server():
    """I nomi dei server di radio-browser, dall'elenco di all.api la prima
    volta, poi tenuti; quelli di riserva se l'elenco non arriva."""
    with _server_blocco:
        if _server:
            return list(_server)
    try:
        nomi = list(dict.fromkeys(s["name"] for s in _leggi(ELENCO_DEI_SERVER) if isinstance(s, dict) and isinstance(s.get("name"), str)))
    except (OSError, ValueError):
        nomi = []
    with _server_blocco:
        _server[:] = nomi or list(SERVER_DI_RISERVA)
        return list(_server)


def _chiedi(percorso, **parametri):
    """La risposta JSON di radio-browser: dal primo server che risponde.
    ErroreRadio se non risponde nessuno."""
    coda = "?" + urllib.parse.urlencode(parametri) if parametri else ""
    errori = []
    for nome in server():
        try:
            return _leggi(f"https://{nome}{percorso}{coda}")
        except (OSError, ValueError, http.client.HTTPException) as e:
            errori.append(str(getattr(e, "reason", None) or e))
    raise ErroreRadio(_("radio-browser non risponde: {errore}").format(errore=errori[-1] if errori else _("nessun server")))


def nome_del_paese(codice):
    """Il nome di un paese dal suo codice ISO, come lo dice Windows nella sua
    lingua: Italia. Senza risposta, None."""
    testo = ctypes.create_unicode_buffer(200)
    try:
        if ctypes.WinDLL("kernel32").GetGeoInfoEx(codice, _GEO_FRIENDLYNAME, testo, len(testo)):
            return testo.value
    except (OSError, AttributeError, TypeError, ctypes.ArgumentError):
        pass
    return None


def paese_di_casa():
    """Il paese di Windows, come IT, che va in cima a Per paese; None se non si sa."""
    testo = ctypes.create_unicode_buffer(10)
    try:
        if ctypes.WinDLL("kernel32").GetUserDefaultGeoName(testo, len(testo)):
            return testo.value.upper() or None
    except (OSError, AttributeError):
        pass
    return None


def nome_della_lingua(codice, nome):
    """Il nome di una lingua nella lingua di Windows, dal codice ISO 639: Inglese.
    Senza codice o senza risposta, il nome di radio-browser, con l'iniziale grande."""
    if codice:
        testo = ctypes.create_unicode_buffer(85)
        try:
            if ctypes.WinDLL("kernel32").GetLocaleInfoEx(codice.split(",")[0], _LOCALE_SLOCALIZEDLANGUAGENAME, testo, len(testo)):
                return testo.value
        except (OSError, AttributeError, TypeError, ctypes.ArgumentError):
            pass
    return nome[:1].upper() + nome[1:]


def _numero(valore):
    return valore if isinstance(valore, int) and not isinstance(valore, bool) and valore > 0 else 0


class Stazione:
    """Una radio di radio-browser: uuid, nome, indirizzo da aprire, paese,
    codec, bitrate in kbps, generi e lingua."""

    def __init__(self, dati):
        self.uuid = str(dati.get("stationuuid") or "")
        self.nome = " ".join(str(dati.get("name") or "").split()) or self.uuid
        self.indirizzo = str(dati.get("url_resolved") or dati.get("url") or "").strip()
        self.paese = str(dati.get("countrycode") or "").upper()
        codec = str(dati.get("codec") or "").strip()
        self.codec = "" if codec.upper() == "UNKNOWN" else codec
        self.bitrate = _numero(dati.get("bitrate"))
        self.generi = ", ".join(g.strip() for g in str(dati.get("tags") or "").split(",") if g.strip())[:200]
        self.lingua = str(dati.get("language") or "")

    def come_brano(self):
        radio = {"uuid": self.uuid, "paese": self.paese, "codec": self.codec, "bitrate": self.bitrate, "generi": self.generi}
        return Brano(self.indirizzo, titolo=self.nome, radio={k: v for k, v in radio.items() if v or k == "uuid"})


def _stazioni(risposta):
    """Le radio di una risposta, senza quelle senza indirizzo o senza uuid, e
    senza doppioni dello stesso uuid."""
    viste, stazioni = set(), []
    for dati in risposta if isinstance(risposta, list) else []:
        if not isinstance(dati, dict):
            continue
        stazione = Stazione(dati)
        if stazione.uuid and stazione.uuid not in viste and stazione.indirizzo.lower().startswith(("http://", "https://")):
            viste.add(stazione.uuid)
            stazioni.append(stazione)
    return stazioni


class Pagina(list):
    """Una pagina di radio (3.10.0): piena se radio-browser ne ha date quante
    se ne chiedevano, e allora ce ne possono essere altre."""

    piena = False


def stazioni(limite=RADIO_PER_GRUPPO, inizio=0, **filtro):
    """Le radio che funzionano, dalle piu' ascoltate, con il filtro di
    radio-browser: countrycode, tag con tagExact, language con languageExact,
    name. inizio salta le prime, per Mostra altre radio (3.10.0)."""
    risposta = _chiedi("/json/stations/search", hidebroken="true", order="clickcount", reverse="true", limit=limite,
        **({"offset": inizio} if inizio else {}), **filtro)
    pagina = Pagina(_stazioni(risposta))
    pagina.piena = len(risposta) >= limite
    return pagina


def cerca(testo, limite=RADIO_PER_GRUPPO, inizio=0):
    """Le radio che hanno testo nel nome, dalle piu' ascoltate."""
    return stazioni(limite, inizio, name=testo)


def paesi():
    """I paesi con delle radio: (codice, nome, quante); quello di Windows in
    cima, poi gli altri in ordine alfabetico, con i nomi di Windows."""
    casa = paese_di_casa()
    elenco = []
    for dati in _chiedi("/json/countries", hidebroken="true"):
        codice, quante = str(dati.get("iso_3166_1") or "").upper(), _numero(dati.get("stationcount"))
        if len(codice) == 2 and quante:
            elenco.append((codice, nome_del_paese(codice) or str(dati.get("name") or codice), quante))
    elenco.sort(key=lambda p: (p[0] != casa, p[1].casefold()))
    return elenco


def generi(limite=GENERI):
    """I generi con piu' radio: (nome, quante), dal piu' numeroso."""
    return [(str(d["name"]), _numero(d.get("stationcount"))) for d in _chiedi("/json/tags", hidebroken="true", order="stationcount", reverse="true", limit=limite)
        if isinstance(d, dict) and d.get("name") and _numero(d.get("stationcount"))]


def lingue(limite=LINGUE):
    """Le lingue con piu' radio: (nome di radio-browser, nome di Windows, quante), dalla piu' numerosa."""
    return [(str(d["name"]), nome_della_lingua(d.get("iso_639"), str(d["name"])), _numero(d.get("stationcount")))
        for d in _chiedi("/json/languages", hidebroken="true", order="stationcount", reverse="true", limit=limite)
        if isinstance(d, dict) and d.get("name") and _numero(d.get("stationcount"))]


def clic(uuid):
    """Dice a radio-browser che la radio si ascolta: lo chiede a chi la suona,
    per la classifica. Da fare in disparte; un errore non conta."""
    with contextlib.suppress(ErroreRadio):
        _chiedi(f"/json/url/{urllib.parse.quote(uuid)}")
