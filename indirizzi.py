# MeTeOra, gli indirizzi in rete: le pagine dei siti, aperte con yt-dlp.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 3.2.0, tappa 19 b del piano, issue 40. Nella 3.3.0 le dirette, senza durata, e gli indirizzi diretti, che libmpv apre senza yt-dlp. Nella 3.3.1 la pagina che non c'e', il 404, e il 403 detti per chi ascolta. Nella 3.5.1 gli appunti con un indirizzo senza https://. Nella 3.8.0 i sottotitoli dei siti. Nella 3.9.0 la ricerca dei contenuti, issue 47.

"""Gli indirizzi in rete (3.2.0, issue 40).

Un indirizzo e' la pagina di un brano o di una playlist su un sito, come
RaiPlay Sound, YouTube, SoundCloud o Bandcamp: si incolla con Ctrl e V o si
scrive con Apri un indirizzo. Il flusso vero lo trova yt-dlp, un componente
aggiuntivo, e libmpv lo suona come un file: MeTeOra gli da' l'indirizzo
diretto, le intestazioni HTTP che il sito vuole e, per i video con l'audio a
parte, la traccia audio. La pagina resta il percorso del brano, e playlist,
Preferiti, statistiche, marker e punti da riprendere la conoscono cosi'. Un
indirizzo diretto a un file, come un .mp3, va a libmpv senza yt-dlp.

yt-dlp lo chiama MeTeOra, e non lo script di libmpv, che aprirebbe le
playlist dei siti nella playlist di libmpv: MeTeOra ha la sua. Una sola
chiamata per brano, con -J, da' insieme flusso, titolo, durata e capitoli.
Misure del 5 novembre 2026, con yt-dlp 2026.10.26 a cartella: mezzo secondo
per partire; un secondo per RaiPlay Sound, SoundCloud, Bandcamp e Mixcloud;
cinque per YouTube con QuickJS, il motore JavaScript che YouTube vuole per
le sue firme, e che e' l'altro componente. I flussi trovati si tengono per
FLUSSO_VALIDO secondi, o fino alla scadenza scritta nell'indirizzo se viene
prima: un brano rifatto, o ripreso dopo un cambio di uscita, riparte subito.
Un flusso che non si apre si dimentica, e la prova dopo richiama yt-dlp.

yt-dlp si aggiorna da se' una volta al giorno, al primo indirizzo (Gabriele,
5 novembre 2026): i siti cambiano spesso, e yt-dlp li rincorre. La versione
nuova si scarica da GitHub, si controlla con le impronte SHA-256 della sua
release e prende il posto della vecchia quando nessuna chiamata e' in corso.
"""

import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import threading
import time
import urllib.parse
import urllib.request
import zipfile

import formati
import percorsi
from lingua import _

# Che cosa si chiede a yt-dlp: l'audio migliore o, se il sito non ha l'audio
# da solo, il flusso migliore; con il video acceso, il video fino a 1080
# righe con l'audio migliore, o il flusso migliore che li ha tutti e due.
FORMATO_AUDIO = "ba/b"
FORMATO_VIDEO = "bv*[height<=?1080]+ba/b"
# Quanto si aspetta yt-dlp, al piu', prima di lasciarlo perdere.
ATTESA = 60.0
# Quanto vale un flusso trovato, e lo scarto prima della scadenza scritta
# nell'indirizzo, come l'expire di YouTube, che dura sei ore.
FLUSSO_VALIDO = 20 * 60.0
SCARTO_DELLA_SCADENZA = 60.0
# Le versioni di yt-dlp: la release ultima, il nome dello zip a cartella
# per Windows, piu' svelto a partire del file unico, e quello delle impronte.
YTDLP_ULTIMA = "https://github.com/yt-dlp/yt-dlp/releases/latest"
YTDLP_RELEASE = "https://github.com/yt-dlp/yt-dlp/releases/download/{versione}/"
YTDLP_ZIP = "yt-dlp_win.zip"
YTDLP_IMPRONTE = "SHA2-256SUMS"
YTDLP_PESO = 23_885_596
# QuickJS-NG 0.18.0, fissato con la sua impronta: yt-dlp lo vuole chiamato qjs.
QUICKJS_URL = "https://github.com/quickjs-ng/quickjs/releases/download/v0.18.0/qjs-windows-x86_64.exe"
QUICKJS_SHA256 = "ff03398d74ea6e6bd3a8e58058f7003225abcac229d7d57775b7aaae812a49c7"
QUICKJS_PESO = 1_873_152
_SENZA_FINESTRA = getattr(subprocess, "CREATE_NO_WINDOW", 0)
_SCADENZA = re.compile(r"[?&/]expire[=/](\d{9,11})")


class ErroreIndirizzo(Exception):
    """Un indirizzo che non si apre, con il motivo da dire."""


class SenzaYtDlp(ErroreIndirizzo):
    """yt-dlp non e' installato."""


def e_indirizzo(percorso):
    return formati.e_indirizzo(percorso)


def dagli_appunti(testo):
    """Il primo indirizzo http o https di un testo, come quello degli appunti;
    se non ce n'e', il primo copiato senza https://, come
    www.raiplaysound.it/radio2, con https:// davanti (3.5.1, dal collaudo di
    Gabriele); None se non c'e' nessuno dei due. Le virgolette e le parentesi
    attorno si tolgono."""
    parole = [parola.strip("<>\"'()[]") for parola in (testo or "").split()]
    for parola in parole:
        if formati.e_indirizzo(parola) and urllib.parse.urlsplit(parola).hostname:
            return parola
    for parola in parole:
        indirizzo = _senza_https(parola)
        if indirizzo is not None:
            return indirizzo
    return None


def _senza_https(parola):
    """Un indirizzo copiato senza https://, con https:// davanti, o None. Negli
    appunti puo' esserci di tutto, come il nome di un file, brano.mp3: vale
    solo un sito che finisce con un dominio di lettere, come .it o .com, e
    comincia con www. o ha una barra dopo di se', come raiplaysound.it/radio2."""
    sito_scritto, barra, _resto = parola.partition("/")
    if not re.fullmatch(r"[\w-]+(\.[\w-]+)+(:\d+)?", sito_scritto):
        return None
    nome = sito_scritto.split(":", 1)[0]
    dominio = nome.rsplit(".", 1)[-1]
    if not (dominio.isalpha() and len(dominio) >= 2) or not (barra or nome.lower().startswith("www.")):
        return None
    indirizzo = "https://" + parola
    return indirizzo if urllib.parse.urlsplit(indirizzo).hostname else None


def indirizzo_scritto(testo):
    """L'indirizzo scritto nel campo di Apri un indirizzo: anche senza
    https://, come www.raiplaysound.it/audio/..., che lo prende davanti.
    None se il testo non e' un indirizzo."""
    testo = (testo or "").strip()
    trovato = dagli_appunti(testo)
    if trovato is not None or not testo or " " in testo:
        return trovato
    sito_scritto = testo.split("/", 1)[0]
    if "." in sito_scritto.strip(".") and re.fullmatch(r"[\w.-]+(:\d+)?", sito_scritto):
        return dagli_appunti("https://" + testo)
    return None


def sito(indirizzo):
    """Il nome del sito di un indirizzo, senza www: youtube.com."""
    nome = urllib.parse.urlsplit(indirizzo).hostname or indirizzo
    return nome.removeprefix("www.")


def diretto(indirizzo):
    """Vero per un indirizzo che porta a un file che libmpv sa suonare da se',
    come un .mp3 o un .ogg: non serve yt-dlp."""
    nome = urllib.parse.urlsplit(indirizzo).path
    return formati.supportato(nome) or formati.estensione(nome) == ".m3u8"


# I componenti.


def cartella_di_ytdlp():
    """Dove MeTeOra tiene yt-dlp: accanto ai suoi dati."""
    return percorsi.percorso_dati("yt-dlp")


def eseguibile_di_ytdlp():
    return os.path.join(cartella_di_ytdlp(), "yt-dlp.exe")


def ytdlp_presente():
    return os.path.isfile(eseguibile_di_ytdlp())


def versione_di_ytdlp():
    """La versione installata, scritta all'installazione; None se non si sa."""
    try:
        with open(os.path.join(cartella_di_ytdlp(), "versione.txt"), encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def cartella_di_quickjs():
    return percorsi.percorso_dati("quickjs")


def eseguibile_di_quickjs():
    return os.path.join(cartella_di_quickjs(), "qjs.exe")


def quickjs_presente():
    return os.path.isfile(eseguibile_di_quickjs())


# Le chiamate a yt-dlp: quelle in corso, perche' l'aggiornamento aspetti che
# finiscano e la chiusura di MeTeOra le fermi.
_stato = threading.Condition()
_processi = set()
_aggiornamento_in_corso = False


def _comando(argomenti):
    comando = [eseguibile_di_ytdlp(), "--ignore-config", "--no-warnings", "--no-progress", "--encoding", "utf-8", "-J"]
    if quickjs_presente():
        comando += ["--js-runtimes", f"quickjs:{eseguibile_di_quickjs()}"]
    return comando + list(argomenti)


def _motivo(errore):
    """Il motivo detto da yt-dlp, dalla sua ultima riga ERROR, senza il nome
    dell'estrattore e senza l'invito a segnalare il difetto."""
    righe = [r.strip() for r in errore.splitlines() if r.strip()]
    riga = next((r for r in reversed(righe) if r.startswith("ERROR:")), righe[-1] if righe else "")
    riga = riga.removeprefix("ERROR:").strip()
    riga = re.sub(r"^\[[^\]]+\]\s*(\S+:\s*)?", "", riga)
    riga = riga.split("; please report this issue", 1)[0].strip()
    if riga.startswith("Unsupported URL"):
        return _("yt-dlp non conosce questo sito")
    # Una pagina che non c'e', come un indirizzo scritto a meta' o tolto dal
    # sito (collaudo della 3.2.0): il 404 di HTTP, detto per chi ascolta.
    if "HTTP Error 404" in riga:
        return _("la pagina non c'è: l'indirizzo è sbagliato, o il sito l'ha tolta")
    if "HTTP Error 403" in riga:
        return _("il sito non lascia aprire la pagina")
    return riga.rstrip(".") or _("yt-dlp non ha detto perché")


def _esegui(argomenti, attesa=ATTESA):
    """La risposta di yt-dlp, letta dal JSON di -J. SenzaYtDlp se non c'e',
    ErroreIndirizzo se non risponde o dice di no."""
    if not ytdlp_presente():
        raise SenzaYtDlp(_("yt-dlp non è installato"))
    with _stato:
        while _aggiornamento_in_corso:
            _stato.wait()
        try:
            processo = subprocess.Popen(_comando(argomenti), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,  # noqa: S603 - yt-dlp installato da MeTeOra
                creationflags=_SENZA_FINESTRA)
        except OSError as e:
            raise ErroreIndirizzo(_("yt-dlp non parte: {errore}").format(errore=e.strerror or e)) from e
        _processi.add(processo)
    try:
        uscita, errore = processo.communicate(timeout=attesa)
    except subprocess.TimeoutExpired:
        processo.kill()
        processo.communicate()
        raise ErroreIndirizzo(_("il sito non ha risposto in {secondi} secondi").format(secondi=round(attesa))) from None
    finally:
        with _stato:
            _processi.discard(processo)
            _stato.notify_all()
    if processo.returncode:
        raise ErroreIndirizzo(_motivo(errore.decode("utf-8", "replace")))
    try:
        return json.loads(uscita.decode("utf-8", "replace"))
    except ValueError:
        raise ErroreIndirizzo(_("yt-dlp ha risposto in un modo che non capisco")) from None


# La ricerca dei contenuti (Gabriele, issue 47, 3.9.0): i motori di yt-dlp,
# nell'ordine in cui si cercano, con quanti risultati chiedere a ognuno.
MOTORI_DELLA_RICERCA = (("ytsearch", 20), ("scsearch", 10))


def cerca(testo, trovato, fermo=None, attesa=ATTESA):
    """Cerca testo su YouTube e poi su SoundCloud con yt-dlp, e da' a trovato
    ogni risultato appena arriva, come (indirizzo, titolo, durata, autore):
    yt-dlp con -j ne scrive uno per riga. fermo(), vero, la interrompe.
    Torna quanti ne ha trovati. SenzaYtDlp se yt-dlp non c'e',
    ErroreIndirizzo se non parte, o se dice di no senza trovare niente."""
    if not ytdlp_presente():
        raise SenzaYtDlp(_("yt-dlp non è installato"))
    comando = _comando(["--flat-playlist", "--ignore-errors", *(f"{motore}{quanti}:{testo}" for motore, quanti in MOTORI_DELLA_RICERCA)])
    comando[comando.index("-J")] = "-j"
    with _stato:
        while _aggiornamento_in_corso:
            _stato.wait()
        try:
            processo = subprocess.Popen(comando, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,  # noqa: S603 - yt-dlp installato da MeTeOra
                creationflags=_SENZA_FINESTRA)
        except OSError as e:
            raise ErroreIndirizzo(_("yt-dlp non parte: {errore}").format(errore=e.strerror or e)) from e
        _processi.add(processo)
    sveglia = threading.Timer(attesa, processo.kill)
    sveglia.start()
    quanti = 0
    try:
        for riga in processo.stdout:
            if fermo is not None and fermo():
                processo.kill()
                break
            try:
                voce = json.loads(riga.decode("utf-8", "replace"))
            except ValueError:
                continue
            if not isinstance(voce, dict) or not voce.get("url"):
                continue
            quanti += 1
            trovato((voce["url"], str(voce.get("title") or voce["url"]), _durata(voce.get("duration")), voce.get("uploader") or voce.get("channel")))
        errore = processo.stderr.read().decode("utf-8", "replace")
        processo.wait()
    finally:
        sveglia.cancel()
        with _stato:
            _processi.discard(processo)
            _stato.notify_all()
    if processo.returncode and not quanti and not (fermo is not None and fermo()):
        raise ErroreIndirizzo(_motivo(errore))
    return quanti


def chiudi():
    """Alla chiusura di MeTeOra: le chiamate in corso si fermano."""
    with _stato:
        for processo in list(_processi):
            with contextlib.suppress(OSError):
                processo.kill()


# Le risposte.


class Flusso:
    """Che cosa dare a libmpv: l'indirizzo diretto, le intestazioni HTTP come
    righe Nome: valore, gli indirizzi delle tracce audio a parte, e se e' una
    diretta, che non ha durata ne' fine (3.3.0)."""

    def __init__(self, indirizzo, intestazioni=(), audio=(), dal_vivo=False, sottotitoli=()):
        self.indirizzo, self.intestazioni, self.audio, self.dal_vivo = indirizzo, tuple(intestazioni), tuple(audio), dal_vivo
        # Gli indirizzi dei sottotitoli in WebVTT (issue 45, 3.8.0).
        self.sottotitoli = tuple(sottotitoli)

    def __repr__(self):
        return f"Flusso({self.indirizzo!r})"


class Pagina:
    """Che cosa c'e' a un indirizzo: titolo, durata e scheda per lo schedario
    di un brano, con il suo flusso; per una playlist, le sue voci, ognuna
    (indirizzo, titolo, durata)."""

    def __init__(self, indirizzo, titolo, durata=None, scheda=None, flusso=None, voci=None):
        self.indirizzo, self.titolo, self.durata, self.scheda, self.flusso, self.voci = indirizzo, titolo, durata, scheda, flusso, voci

    @property
    def playlist(self):
        return self.voci is not None


def _durata(valore):
    return float(valore) if isinstance(valore, (int, float)) and not isinstance(valore, bool) and valore > 0 else None


def _diretto_del_formato(formato):
    """L'indirizzo che libmpv apre per un formato: il manifesto per il DASH a
    pezzi, che libmpv legge da se', come quello di Mixcloud."""
    if str(formato.get("protocol", "")).startswith("http_dash_segments") and formato.get("manifest_url"):
        return formato["manifest_url"]
    return formato.get("url")


# Quante tracce di sottotitoli, al piu', per un brano di un sito (3.8.0).
SOTTOTITOLI_MASSIMI = 6


def flusso_dell_info(info):
    """Il Flusso della risposta di yt-dlp per un brano."""
    formati_scelti = info.get("requested_formats") or [info]
    principale = _diretto_del_formato(formati_scelti[0])
    if not principale:
        raise ErroreIndirizzo(_("il sito non dà un flusso da suonare"))
    intestazioni = formati_scelti[0].get("http_headers") or info.get("http_headers") or {}
    audio = [a for a in (_diretto_del_formato(f) for f in formati_scelti[1:]) if a]
    return Flusso(principale, [f"{nome}: {valore}" for nome, valore in intestazioni.items()], audio, dal_vivo=bool(info.get("is_live")),
        sottotitoli=sottotitoli_dell_info(info))


def sottotitoli_dell_info(info):
    """Gli indirizzi dei sottotitoli di un brano di un sito, in WebVTT, che
    libmpv legge (Gabriele, issue 45, 3.8.0): quelli scritti, in tutte le
    lingue, e quelli automatici, come quelli di YouTube, solo nella lingua del
    brano e in quella di MeTeOra, che altrimenti sarebbero cento traduzioni.
    Prima la lingua di MeTeOra, che libmpv sceglie per prima."""
    import lingua

    originale = str(info.get("language") or "").split("-")[0].lower()
    tracce = []
    for gruppo, automatici in ((info.get("subtitles"), False), (info.get("automatic_captions"), True)):
        for codice, formati_della_lingua in (gruppo or {}).items():
            base = str(codice).split("-")[0].lower()
            if automatici and base not in (originale, lingua.CODICE):
                continue
            indirizzo = next((f.get("url") for f in formati_della_lingua or [] if f.get("ext") == "vtt" and f.get("url")), None)
            if indirizzo and indirizzo not in (t[1] for t in tracce):
                tracce.append((base != lingua.CODICE, indirizzo))
    return [indirizzo for _altra, indirizzo in sorted(tracce, key=lambda t: t[0])][:SOTTOTITOLI_MASSIMI]


def _titolo(info):
    """Il titolo di un brano; di una diretta senza la data e l'ora che yt-dlp
    gli aggiunge, come Rai Radio 2 invece di Rai Radio 2 2026-11-10 15:38 (3.3.1)."""
    if info.get("is_live") and info.get("fulltitle"):
        return info["fulltitle"]
    return info.get("title")


def scheda_dell_info(info):
    """La scheda di un brano di un sito per lo schedario, come quelle dei
    file: durata, tag e capitoli, senza dimensione e data."""
    anno = info.get("release_year") or str(info.get("upload_date") or "")[:4]
    tag = {"titolo": info.get("track") or _titolo(info), "autore": info.get("artist") or info.get("creator") or info.get("uploader") or info.get("channel"),
        "album": info.get("album"), "genere": info.get("genre"), "anno": int(anno) if str(anno).isdigit() else None}
    scheda = {"dim": None, "mod": None, "durata": _durata(info.get("duration")), "tag": {k: str(v) if k != "anno" else v for k, v in tag.items() if v},
        "sottobrani": None, "durate_sid": None, "indirizzo": True}
    capitoli = [[float(c["start_time"]), str(c.get("title") or "")] for c in info.get("chapters") or [] if isinstance(c.get("start_time"), (int, float))]
    if capitoli:
        scheda["capitoli"] = capitoli
    return scheda


def scheda_della_voce(titolo, durata):
    """La scheda di un brano di una playlist di un sito prima di aprirlo:
    il titolo e la durata che la playlist dice, quando li dice."""
    return {"dim": None, "mod": None, "durata": _durata(durata), "tag": {"titolo": titolo} if titolo else {}, "sottobrani": None, "durate_sid": None,
        "indirizzo": True}


def _voci(info):
    """Le voci di una playlist: (indirizzo, titolo, durata), senza le
    sottoplaylist, come le schede di un canale."""
    voci = []
    for voce in info.get("entries") or []:
        if not isinstance(voce, dict) or voce.get("_type") == "playlist":
            continue
        indirizzo = voce.get("webpage_url") or voce.get("url")
        if not formati.e_indirizzo(indirizzo or ""):
            continue
        voci.append((indirizzo, voce.get("title") or indirizzo, _durata(voce.get("duration"))))
    return voci


def _pagina(indirizzo, info):
    if info.get("_type") == "playlist":
        return Pagina(indirizzo, info.get("title") or sito(indirizzo), voci=_voci(info))
    return Pagina(indirizzo, _titolo(info) or sito(indirizzo), _durata(info.get("duration")), scheda_dell_info(info), flusso_dell_info(info))


# I flussi trovati: indirizzo -> (Flusso, scadenza in monotonic, con il video).
_flussi = {}
_flussi_blocco = threading.Lock()


def _scadenza(flusso, adesso):
    scadenza = adesso + FLUSSO_VALIDO
    trovata = _SCADENZA.search(flusso.indirizzo)
    if trovata:
        scadenza = min(scadenza, adesso + int(trovata.group(1)) - time.time() - SCARTO_DELLA_SCADENZA)
    return scadenza


def _tieni(indirizzo, video, flusso):
    adesso = time.monotonic()
    with _flussi_blocco:
        _flussi[indirizzo] = (flusso, _scadenza(flusso, adesso), video)


# Gli indirizzi che libmpv apre da se', senza yt-dlp, anche senza l'estensione
# di un formato: le radio di radio-browser, che sono dirette, e gli indirizzi
# dei file M3U e PLS importati (3.3.0). indirizzo -> dal vivo. Li mette chi
# li suona, prima di chiederne il flusso.
_diretti = {}


def metti_il_diretto(indirizzo, dal_vivo=False):
    _diretti[indirizzo] = dal_vivo


def e_una_radio(indirizzo):
    """Vero per un indirizzo messo come diretta, cioe' per una radio."""
    return _diretti.get(indirizzo, False)


def pronto(indirizzo, video=None):
    """Il Flusso dell'indirizzo se c'e' e vale ancora, chiesto con il video o
    senza come dice video, o in un modo qualunque con None, come lo chiede il
    motore; None se va chiesto a yt-dlp. Un indirizzo diretto e' sempre pronto."""
    if indirizzo in _diretti:
        return Flusso(indirizzo, dal_vivo=_diretti[indirizzo])
    if diretto(indirizzo):
        return Flusso(indirizzo)
    with _flussi_blocco:
        tenuto = _flussi.get(indirizzo)
    if tenuto is None or tenuto[1] <= time.monotonic() or (video is not None and tenuto[2] != video):
        return None
    return tenuto[0]


def dimentica(indirizzo):
    """Il flusso dell'indirizzo non si apre: la prossima volta si richiede."""
    with _flussi_blocco:
        _flussi.pop(indirizzo, None)


def esplora(indirizzo, video=False):
    """Che cosa c'e' a un indirizzo, la prima volta che si apre: un brano, con
    il flusso pronto, o una playlist con le sue voci. ErroreIndirizzo se non
    si apre. Da chiamare fuori dal filo della finestra."""
    if diretto(indirizzo):
        nome = os.path.basename(urllib.parse.unquote(urllib.parse.urlsplit(indirizzo).path)) or sito(indirizzo)
        return Pagina(indirizzo, nome, flusso=Flusso(indirizzo))
    pagina = _pagina(indirizzo, _esegui(["--flat-playlist", "-f", FORMATO_VIDEO if video else FORMATO_AUDIO, indirizzo]))
    if pagina.flusso is not None:
        _tieni(indirizzo, video, pagina.flusso)
    return pagina


def risolvi(indirizzo, video=False):
    """La Pagina di un brano, con il flusso: quello tenuto, se vale ancora,
    altrimenti chiesto a yt-dlp. Senza la scheda se il flusso era tenuto.
    ErroreIndirizzo se non si apre o se e' una playlist."""
    flusso = pronto(indirizzo, video)
    if flusso is not None:
        return Pagina(indirizzo, None, flusso=flusso)
    pagina = _pagina(indirizzo, _esegui(["--no-playlist", "-f", FORMATO_VIDEO if video else FORMATO_AUDIO, indirizzo]))
    if pagina.flusso is None:
        raise ErroreIndirizzo(_("è una playlist, non un brano"))
    _tieni(indirizzo, video, pagina.flusso)
    return pagina


# L'installazione e l'aggiornamento.


def _scarica(url, avanza=None):
    import midi

    return midi._scarica(url, avanza)


def ultima_versione():
    """Il nome dell'ultima versione di yt-dlp, dall'indirizzo a cui porta la
    sua release ultima: senza le API di GitHub, che hanno un limite."""
    richiesta = urllib.request.Request(YTDLP_ULTIMA, method="HEAD", headers={"User-Agent": "MeTeOra"})
    with urllib.request.urlopen(richiesta, timeout=30) as risposta:  # noqa: S310 - indirizzo https fisso
        versione = risposta.geturl().rstrip("/").rsplit("/", 1)[-1]
    if not re.fullmatch(r"[0-9][0-9.]*", versione):
        raise OSError(_("GitHub non dice l'ultima versione di yt-dlp"))
    return versione


def _impronte(testo):
    """nome -> impronta, dal file SHA2-256SUMS."""
    impronte = {}
    for riga in testo.splitlines():
        parti = riga.split()
        if len(parti) == 2:
            impronte[parti[1].lstrip("*")] = parti[0].lower()
    return impronte


def installa_ytdlp(versione=None, avanza=None):
    """Scarica yt-dlp, l'ultima versione o quella data, ne controlla
    l'impronta e lo mette nella sua cartella al posto di quello di prima,
    quando nessuna chiamata e' in corso. Torna la versione; OSError se non
    riesce."""
    global _aggiornamento_in_corso
    versione = versione or ultima_versione()
    base = YTDLP_RELEASE.format(versione=versione)
    attesa = _impronte(_scarica(base + YTDLP_IMPRONTE).decode("utf-8", "replace")).get(YTDLP_ZIP)
    if not attesa:
        raise OSError(_("la release {versione} di yt-dlp non ha l'impronta di {nome}").format(versione=versione, nome=YTDLP_ZIP))
    dati = _scarica(base + YTDLP_ZIP, avanza)
    if hashlib.sha256(dati).hexdigest() != attesa:
        raise OSError(_("lo zip di yt-dlp scaricato non è quello atteso"))
    cartella = cartella_di_ytdlp()
    nuova, vecchia = cartella + ".nuova", cartella + ".vecchia"
    shutil.rmtree(nuova, ignore_errors=True)
    with zipfile.ZipFile(io.BytesIO(dati)) as archivio:
        archivio.extractall(nuova)
    if not os.path.isfile(os.path.join(nuova, "yt-dlp.exe")):
        shutil.rmtree(nuova, ignore_errors=True)
        raise OSError(_("nello zip di yt-dlp manca yt-dlp.exe"))
    with open(os.path.join(nuova, "versione.txt"), "w", encoding="utf-8") as f:
        f.write(versione)
    with _stato:
        _aggiornamento_in_corso = True
        try:
            fine = time.monotonic() + ATTESA
            while _processi and time.monotonic() < fine:
                _stato.wait(fine - time.monotonic())
            shutil.rmtree(vecchia, ignore_errors=True)
            if os.path.isdir(cartella):
                os.replace(cartella, vecchia)
            os.replace(nuova, cartella)
        finally:
            _aggiornamento_in_corso = False
            _stato.notify_all()
    shutil.rmtree(vecchia, ignore_errors=True)
    return versione


def togli_ytdlp():
    with _stato:
        if _processi or _aggiornamento_in_corso:
            raise OSError(_("yt-dlp è al lavoro: si toglie fra poco"))
        shutil.rmtree(cartella_di_ytdlp())


def aggiorna_ytdlp(avanza=None):
    """L'aggiornamento di ogni giorno: la versione nuova installata, o None
    se quella che c'e' e' gia' l'ultima. OSError se non riesce."""
    versione = ultima_versione()
    if versione == versione_di_ytdlp():
        return None
    return installa_ytdlp(versione, avanza)


def installa_quickjs(avanza=None):
    dati = _scarica(QUICKJS_URL, avanza)
    if hashlib.sha256(dati).hexdigest() != QUICKJS_SHA256:
        raise OSError(_("QuickJS scaricato non è quello atteso"))
    os.makedirs(cartella_di_quickjs(), exist_ok=True)
    parziale = eseguibile_di_quickjs() + ".parziale"
    with open(parziale, "wb") as f:
        f.write(dati)
    os.replace(parziale, eseguibile_di_quickjs())


def togli_quickjs():
    with _stato:
        if _processi:
            raise OSError(_("yt-dlp lo sta usando: si toglie fra poco"))
        os.remove(eseguibile_di_quickjs())
    with contextlib.suppress(OSError):
        os.rmdir(cartella_di_quickjs())
