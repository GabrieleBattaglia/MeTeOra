# MeTeOra, le dirette lette da MeTeOra: le radio HTTP passate a libmpv senza la sua lettura di rete.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 12/11/2026: nasce con la 3.11.0, issue 46, con le correzioni della rilettura di un sottoagente. Nella 3.11.1 il tipo, per lo speaker Cast. Nella 3.11.6 il filtro dei fotogrammi MP3 e AAC per lo speaker.

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


# Il filtro dei fotogrammi per lo speaker (3.11.6). I tipi delle dirette MP3
# e AAC, a cui si tolgono i byte rotti fra un fotogramma e l'altro.
TIPI_DA_FILTRARE = ("audio/mpeg", "audio/mp3", "audio/mpeg3", "audio/x-mpeg", "audio/aac", "audio/aacp", "audio/x-aac", "audio/x-aacp")
# Senza un aggancio entro tanti byte dall'inizio, o dopo una rottura, il
# flusso non e' quello che il tipo dice, e il filtro lo lascia passare com'e'.
AGGANCIO_ALL_INIZIO = 16384
AGGANCIO_DOPO_UNA_ROTTURA = 65536
# I byte che servono per leggere un'intestazione: 4 per l'MP3, 6 per l'AAC.
_TESTA = 6
_POCO = object()
# Le frequenze dell'MP3 per versione, 3 MPEG-1, 2 MPEG-2, 0 MPEG-2.5, e i
# kbps per versione e strato, 3 il primo, 2 il secondo, 1 il terzo.
_FREQUENZE_MP3 = {3: (44100, 48000, 32000), 2: (22050, 24000, 16000), 0: (11025, 12000, 8000)}
_KBPS_MPEG1 = {3: (0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448),
    2: (0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384),
    1: (0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320)}
_KBPS_MPEG2 = {3: (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256),
    2: (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160),
    1: (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160)}


def da_filtrare(tipo):
    """Vero per il tipo di una diretta MP3 o AAC, come audio/mpeg."""
    return str(tipo or "").split(";", 1)[0].strip().lower() in TIPI_DA_FILTRARE


def _testa(dati, i):
    """L'intestazione di un fotogramma MP3, di qualunque versione e strato,
    o AAC ADTS, a dati[i]: (lunghezza del fotogramma, chiave), dove la
    chiave dice il formato, che i fotogrammi di fila hanno uguale; None se li'
    non c'e' un'intestazione; _POCO se i byte non bastano per dirlo. Le due
    intestazioni non si confondono: l'ADTS ha lo strato 0, che l'MP3 non ha."""
    if i + _TESTA > len(dati):
        return _POCO
    b0, b1, b2, b3 = dati[i], dati[i + 1], dati[i + 2], dati[i + 3]
    if b0 != 0xFF:
        return None
    if b1 & 0xF6 == 0xF0:
        frequenza = (b2 >> 2) & 0x0F
        lunghezza = ((b3 & 3) << 11) | (dati[i + 4] << 3) | (dati[i + 5] >> 5)
        if frequenza > 12 or lunghezza < (7 if b1 & 1 else 9):
            return None
        return lunghezza, ("aac", b1 & 0x08, b2 >> 6, frequenza, ((b2 & 1) << 2) | (b3 >> 6))
    if b1 & 0xE0 != 0xE0:
        return None
    versione, strato = (b1 >> 3) & 3, (b1 >> 1) & 3
    indice, frequenza, riempimento = b2 >> 4, (b2 >> 2) & 3, (b2 >> 1) & 1
    # Il formato libero, indice 0, non dice la lunghezza: non si filtra.
    if versione == 1 or strato == 0 or indice in (0, 15) or frequenza == 3:
        return None
    hz = _FREQUENZE_MP3[versione][frequenza]
    kbps = (_KBPS_MPEG1 if versione == 3 else _KBPS_MPEG2)[strato][indice]
    if strato == 3:
        lunghezza = (12 * kbps * 1000 // hz + riempimento) * 4
    elif strato == 1 and versione != 3:
        lunghezza = 72 * kbps * 1000 // hz + riempimento
    else:
        lunghezza = 144 * kbps * 1000 // hz + riempimento
    return lunghezza, ("mp3", versione, strato, frequenza)


class Fotogrammi:
    """Il filtro dei fotogrammi di una diretta MP3 o AAC per lo speaker
    (3.11.6). BBC World Service manda, circa ogni 15 secondi, da 3 a 166 byte
    rotti fra un fotogramma e l'altro, gia' dal server (misura del 12
    novembre 2026): libmpv li salta, GabryBar si ferma con un errore.
    passa(dati) torna i fotogrammi interi arrivati, senza niente in mezzo, e
    tiene da parte quelli che non si possono ancora giudicare. Ci si aggancia
    a un fotogramma quando il seguente, dove deve stare, ha lo stesso
    formato. Agganciati, un fotogramma passa quando il seguente comincia
    dove deve; un cambio di formato vale se lo conferma il fotogramma dopo.
    Altrimenti c'e' una rottura, e si cerca l'aggancio dopo l'inizio del
    fotogramma: se e' oltre la sua fine il fotogramma era intero e passa, se
    e' prima era troncato e si scarta. Se l'aggancio non arriva entro
    AGGANCIO_ALL_INIZIO byte all'inizio, o AGGANCIO_DOPO_UNA_ROTTURA dopo una
    rottura, il flusso non e' MP3 ne' AAC, e da li' passa tutto com'e'.
    rotture conta i punti rotti, scartati i byte tolti."""

    def __init__(self):
        self._dati = bytearray()
        self._chiave = None
        self._in_rottura = False
        self.rotture = 0
        self.scartati = 0
        self.arreso = False

    def passa(self, dati):
        if self.arreso:
            return bytes(dati)
        self._dati += dati
        pezzi, i = [], 0
        while True:
            if self._chiave is None:
                k = self._aggancio(i, None, AGGANCIO_ALL_INIZIO)
                if k is _POCO:
                    break
                if k is None:
                    self.arreso = True
                    pezzi.append(self._dati[i:])
                    i = len(self._dati)
                    break
                self.scartati += k - i
                i, self._chiave = k, _testa(self._dati, k)[1]
                continue
            testa = _testa(self._dati, i)
            if testa is _POCO:
                break
            buono = False
            if testa is not None:
                lunghezza, chiave = testa
                seguente = _testa(self._dati, i + lunghezza)
                if seguente is _POCO:
                    break
                if seguente is not None and seguente[1][0] == chiave[0]:
                    buono = seguente[1] == chiave
                    if not buono:
                        # Un formato nuovo vale se lo conferma il fotogramma dopo.
                        terzo = _testa(self._dati, i + lunghezza + seguente[0])
                        if terzo is _POCO:
                            break
                        buono = terzo is not None and terzo[1] == seguente[1]
            if buono:
                pezzi.append(self._dati[i:i + lunghezza])
                i += lunghezza
                self._chiave, self._in_rottura = chiave, False
                continue
            if not self._in_rottura:
                self._in_rottura = True
                self.rotture += 1
            k = self._aggancio(i + 1, self._chiave[0], AGGANCIO_DOPO_UNA_ROTTURA)
            if k is _POCO:
                break
            if k is None:
                self.arreso = True
                pezzi.append(self._dati[i:])
                i = len(self._dati)
                break
            if testa is not None and k >= i + lunghezza:
                # Il fotogramma era intero: i byte rotti sono dopo.
                pezzi.append(self._dati[i:i + lunghezza])
                self.scartati += k - i - lunghezza
            else:
                self.scartati += k - i
            i, self._in_rottura = k, False
            self._chiave = _testa(self._dati, k)[1]
        del self._dati[:i]
        return b"".join(pezzi)

    def fine(self):
        """A flusso finito, cio' che resta da parte: tutto, se non ci si e'
        mai agganciati, perche' non era MP3 ne' AAC; altrimenti il
        fotogramma che aspettava il seguente, se e' intero."""
        if self._chiave is None:
            resto = bytes(self._dati)
        else:
            testa = _testa(self._dati, 0)
            intero = testa is not None and testa is not _POCO and testa[0] <= len(self._dati)
            resto = bytes(self._dati[:testa[0]]) if intero else b""
        self._dati.clear()
        return resto

    def _aggancio(self, da, genere, limite):
        """Il primo punto da da in poi dove comincia un fotogramma, del genere
        dato, mp3 o aac, o di uno qualunque con None, seguito da uno dello
        stesso formato; _POCO se i byte non bastano ancora per dirlo; None se
        non c'e' entro limite byte."""
        j = da
        while j - da <= limite:
            testa = _testa(self._dati, j)
            if testa is _POCO:
                return _POCO
            if testa is not None and (genere is None or testa[1][0] == genere):
                seguente = _testa(self._dati, j + testa[0])
                if seguente is _POCO:
                    return _POCO
                if seguente is not None and seguente[1] == testa[1]:
                    return j
            j += 1
        return None


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
        # Il tipo che il server dice, come audio/mpeg, per lo speaker (3.11.1).
        self.tipo = ""
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
            self.tipo = tipo.split(";", 1)[0].strip()
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
