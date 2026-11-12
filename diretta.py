# MeTeOra, le dirette lette da MeTeOra: le radio HTTP passate a libmpv senza la sua lettura di rete.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 12/11/2026: nasce con la 3.11.0, issue 46, con le correzioni della rilettura di un sottoagente.

"""Le dirette HTTP lette da MeTeOra (issue 46, 3.11.0).

Gabriele sentiva piccole distorsioni, a intervalli piu' o meno regolari, in
molte radio. La causa, misurata l'11 novembre 2026: la lettura di rete di
libmpv, cioe' di FFmpeg, consegnava al decodificatore fotogrammi MP3 rotti,
Header missing e overread, fino a 56 in 25 secondi; con Python che legge la
rete e passa i byte a libmpv, zero. La catena dei filtri e la riserva della
rete erano innocenti.

Cosi' una diretta HTTP o HTTPS, come le radio di Icecast e Shoutcast, la
legge Lettura: chiede i metadati ICY, li toglie dall'audio e ne dice lo
StreamTitle, il titolo in onda; accetta anche la riga di stato ICY 200 OK dei
vecchi Shoutcast; segue i rinvii; se il server chiude si ricollega, al piu'
RIPROVE volte in FINESTRA_DELLE_RIPROVE secondi. libmpv riceve solo l'audio,
con il protocollo diretta:// che il motore e le registrazioni registrano nei
loro lettori. Come libmpv, non verifica i certificati HTTPS, che molte radio
hanno scaduti o incompleti. Le dirette a pezzi, come le m3u8 della BBC, e un
indirizzo che porta a una lista restano a libmpv: Lettura non si apre, e il
motore riapre l'indirizzo vero con libmpv, ricordandolo con a_libmpv.
"""

import base64
import contextlib
import http.client
import re
import socket
import ssl
import threading
import time
import urllib.parse

import version

# Il protocollo dei lettori di libmpv, e il suo indirizzo: diretta://, poi
# l'indirizzo vero, codificato.
SCHEMA = "diretta"
# I secondi per collegarsi e avere le intestazioni, brevi perche' uno stop
# non aspetti troppo, e quelli di attesa di una lettura.
ATTESA_DELL_APERTURA = 5.0
ATTESA = 15.0
# Quante volte ci si ricollega a un server che chiude, in quanti secondi, e
# quanti rinvii si seguono.
RIPROVE = 3
FINESTRA_DELLE_RIPROVE = 60.0
# La pausa prima di ricollegarsi, che cresce a ogni riprova, fino a due secondi.
PAUSA_DELLE_RIPROVE = 0.5
RINVII = 6
# Le estensioni delle liste e delle dirette a pezzi, e i tipi delle liste,
# che restano a libmpv.
DA_LIBMPV = (".m3u8", ".m3u", ".pls", ".mpd", ".xspf", ".asx")
TIPI_DELLE_LISTE = ("mpegurl", "scpls", "dash+xml", "xspf", "text/html", "x-ms-asf", "text/xml")
_TITOLO = re.compile(r"StreamTitle='(.*?)';", re.DOTALL)
# Gli indirizzi che Lettura non ha aperto, perche' portano a una lista: da
# qui li apre libmpv.
_a_libmpv = set()


class NonDiretta(OSError):
    """L'indirizzo porta a una lista o a una pagina, non a una diretta."""


def da_leggere(indirizzo):
    """Vero per una diretta che MeTeOra puo' leggere da se': HTTP o HTTPS,
    non una lista o una diretta a pezzi, come le m3u8, e non un indirizzo
    gia' lasciato a libmpv."""
    indirizzo = str(indirizzo or "")
    parti = urllib.parse.urlsplit(indirizzo)
    return (parti.scheme in ("http", "https") and bool(parti.hostname) and not parti.path.lower().endswith(DA_LIBMPV)
        and indirizzo not in _a_libmpv)


def a_libmpv(indirizzo):
    """Da qui in poi l'indirizzo lo apre libmpv."""
    _a_libmpv.add(indirizzo)


def indirizzo_per_mpv(indirizzo):
    return f"{SCHEMA}://{urllib.parse.quote(indirizzo, safe='')}"


def indirizzo_vero(uri):
    return urllib.parse.unquote(uri[len(SCHEMA) + 3:])


def titolo_dei_metadati(blocco):
    """Lo StreamTitle di un blocco di metadati ICY, o None."""
    testo = blocco.rstrip(b"\0")
    try:
        testo = testo.decode("utf-8")
    except UnicodeDecodeError:
        testo = testo.decode("latin-1")
    trovato = _TITOLO.search(testo)
    if trovato is None:
        return None
    return " ".join(trovato.group(1).split()) or None


def _contesto_tls():
    """Come libmpv, che di serie non verifica i certificati: molte radio li
    hanno scaduti, autofirmati o con la catena incompleta."""
    contesto = ssl.create_default_context()
    contesto.check_hostname = False
    contesto.verify_mode = ssl.CERT_NONE
    return contesto


class _RispostaIcy(http.client.HTTPResponse):
    """Una risposta HTTP che accetta anche ICY 200 OK, la riga di stato dei
    vecchi Shoutcast, che http.client rifiuterebbe."""

    def _read_status(self):
        riga = str(self.fp.readline(http.client._MAXLINE + 1), "iso-8859-1")
        if not riga:
            raise http.client.RemoteDisconnected("il server ha chiuso senza rispondere")
        if riga.startswith("ICY "):
            riga = "HTTP/1.0 " + riga[4:]
        parti = riga.split(None, 2)
        if len(parti) < 2 or not parti[0].startswith("HTTP/") or not parti[1].isdigit():
            raise http.client.BadStatusLine(riga)
        return parti[0], int(parti[1]), parti[2].strip() if len(parti) > 2 else ""


class _Connessione(http.client.HTTPConnection):
    response_class = _RispostaIcy


class _ConnessioneSicura(http.client.HTTPSConnection):
    response_class = _RispostaIcy


class Lettura:
    """Una diretta letta da MeTeOra, per il protocollo dei flussi di
    python-mpv: read da' l'audio, senza i metadati, e b'' alla fine; close e
    cancel chiudono la presa di rete, che sveglia anche una lettura che
    aspetta in un altro filo. al_titolo(titolo) arriva, dal filo di libmpv
    che legge, a ogni titolo in onda nuovo. riconnetti falso, come per le
    registrazioni, fa finire la lettura alla prima caduta. La connessione si
    apre subito: OSError o HTTPException se il server non risponde, NonDiretta
    se l'indirizzo porta a una lista."""

    def __init__(self, indirizzo, al_titolo=None, riconnetti=True):
        self.indirizzo, self.al_titolo, self.riconnetti = indirizzo, al_titolo, riconnetti
        self.riconnessioni = 0
        self._blocco = threading.Lock()
        self._fermo = threading.Event()
        self._connessione = self._risposta = self._presa = None
        self._titolo = None
        self._metaint = self._al_blocco = 0
        self._con_la_lunghezza = False
        self._finita = False
        self._riprove, self._prima_riprova = 0, 0.0
        self._apri()

    def _apri(self):
        """Si collega, seguendo i rinvii; un errore chiude sempre la
        connessione a meta'."""
        try:
            self._collegati()
        except BaseException:
            self._chiudi_la_connessione()
            raise

    def _collegati(self):
        indirizzo = self.indirizzo
        for _rinvio in range(RINVII):
            parti = urllib.parse.urlsplit(indirizzo)
            sicura = parti.scheme == "https"
            porta = parti.port or (443 if sicura else 80)
            if sicura:
                connessione = _ConnessioneSicura(parti.hostname, porta, timeout=ATTESA_DELL_APERTURA, context=_contesto_tls())
            else:
                connessione = _Connessione(parti.hostname, porta, timeout=ATTESA_DELL_APERTURA)
            with self._blocco:
                if self._fermo.is_set():
                    raise OSError("la diretta è chiusa")
                self._connessione = connessione
            connessione.connect()
            with self._blocco:
                self._presa = connessione.sock
            intestazioni = {"User-Agent": f"MeTeOra/{version.VERSION}", "Icy-MetaData": "1", "Accept": "*/*"}
            if parti.username:
                credenziali = f"{urllib.parse.unquote(parti.username)}:{urllib.parse.unquote(parti.password or '')}"
                intestazioni["Authorization"] = "Basic " + base64.b64encode(credenziali.encode("utf-8")).decode("ascii")
            percorso = (parti.path or "/") + (f"?{parti.query}" if parti.query else "")
            connessione.request("GET", percorso, headers=intestazioni)
            risposta = connessione.getresponse()
            dove = risposta.getheader("Location")
            if risposta.status in (301, 302, 303, 307, 308) and dove:
                indirizzo = urllib.parse.urljoin(indirizzo, dove)
                self._chiudi_la_connessione()
                continue
            if risposta.status != 200:
                self._chiudi_la_connessione()
                raise OSError(f"il server risponde {risposta.status} {risposta.reason}".strip())
            tipo = (risposta.getheader("Content-Type") or "").lower()
            if any(lista in tipo for lista in TIPI_DELLE_LISTE) or urllib.parse.urlsplit(indirizzo).path.lower().endswith(DA_LIBMPV):
                self._chiudi_la_connessione()
                raise NonDiretta(f"{indirizzo} porta a una lista, {tipo or 'senza tipo'}")
            try:
                metaint = max(0, int(risposta.getheader("icy-metaint") or 0))
            except ValueError:
                metaint = 0
            with self._blocco:
                presa = self._presa
                if self._fermo.is_set() or presa is None:
                    raise OSError("la diretta è chiusa")
                self._risposta, self._metaint, self._al_blocco = risposta, metaint, metaint
                self._con_la_lunghezza = risposta.length is not None and not risposta.chunked
            # Collegati, la lettura aspetta di piu'.
            with contextlib.suppress(OSError):
                presa.settimeout(ATTESA)
            return
        raise OSError("troppi rinvii")

    def _leggi(self, risposta, quanti):
        """Fino a quanti byte di audio, senza i metadati ICY; b'' alla fine."""
        if self._metaint and self._al_blocco <= 0:
            lunghezza = risposta.read(1)
            if not lunghezza:
                return b""
            if lunghezza[0]:
                blocco = risposta.read(lunghezza[0] * 16)
                titolo = titolo_dei_metadati(blocco)
                if titolo and titolo != self._titolo:
                    self._titolo = titolo
                    if self.al_titolo is not None:
                        self.al_titolo(titolo)
            self._al_blocco = self._metaint
        dati = risposta.read1(min(quanti, self._al_blocco) if self._metaint else quanti)
        if self._metaint:
            self._al_blocco -= len(dati)
        return dati

    def read(self, quanti):
        while True:
            with self._blocco:
                risposta = self._risposta
            if self._fermo.is_set() or self._finita:
                return b""
            if risposta is not None:
                try:
                    dati = self._leggi(risposta, quanti)
                except (OSError, http.client.HTTPException, ValueError, AttributeError):
                    dati = b""
                if dati:
                    return dati
                # Un file con la sua lunghezza e' finito: non si ricomincia.
                if self._con_la_lunghezza:
                    self._finita = True
                    return b""
            if not self._riprova():
                self._finita = True
                return b""

    def _riprova(self):
        """Dopo una caduta, o una riconnessione fallita: si ricollega, al piu'
        RIPROVE volte in FINESTRA_DELLE_RIPROVE secondi, con una pausa che
        cresce. Falso se non si riprova piu'."""
        self._chiudi_la_connessione()
        if not self.riconnetti or self._fermo.is_set():
            return False
        adesso = time.monotonic()
        if adesso - self._prima_riprova > FINESTRA_DELLE_RIPROVE:
            self._riprove, self._prima_riprova = 0, adesso
        if self._riprove >= RIPROVE:
            return False
        self._riprove += 1
        self.riconnessioni += 1
        if self._fermo.wait(min(2.0, PAUSA_DELLE_RIPROVE * self._riprove)):
            return False
        with contextlib.suppress(OSError, http.client.HTTPException, ValueError):
            self._apri()
        return True

    def _chiudi_la_connessione(self):
        with self._blocco:
            connessione, presa = self._connessione, self._presa
            self._connessione = self._risposta = self._presa = None
        if presa is not None:
            # Su Windows shutdown non sveglia una lettura che aspetta in un
            # altro filo: la sveglia la chiusura vera della presa, staccata
            # prima dall'oggetto di Python (rilettura del 12 novembre 2026).
            with contextlib.suppress(OSError):
                presa.shutdown(socket.SHUT_RDWR)
            with contextlib.suppress(OSError, ValueError):
                socket.close(presa.detach())
        if connessione is not None:
            with contextlib.suppress(Exception):
                connessione.close()

    def close(self):
        self._fermo.set()
        self._chiudi_la_connessione()

    def cancel(self):
        self.close()
