# MeTeOra, il riconoscimento dei caratteri: i sottotitoli a immagini e quelli impressi nel video, letti con Windows.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.80.0, dalla tappa 10 (punti a e b), dopo il banco su Roma.

"""Il riconoscimento dei caratteri di Windows (Windows.Media.Ocr), dai pacchetti
winrt di PyPI: legge le scritte in un'immagine, nelle lingue installate in
Windows, italiano e inglese sul PC di Gabriele.

Le immagini sono quelle di Pillow, come le da' screenshot-raw di libmpv.
Due modi di preparare il testo, misurati sul banco del 4 ottobre 2026:
- un sottotitolo a immagini (VobSub dei DVD, PGS dei Blu-ray) si isola
  fotografando il fotogramma con e senza sottotitoli: la differenza sono le
  sue lettere, che in nero su bianco si leggono senza errori (20 su 20, 14 ms);
- un sottotitolo impresso nel video sta nella fascia in basso: si tengono i
  punti chiari, si capovolgono in nero su bianco, e si legge (21 esatti su 25,
  somiglianza media 0.99).
Il riconoscimento si chiama da un filo a parte, mai da quello della finestra.
Ogni filo ha i suoi motori: Windows rifiuta un secondo riconoscimento sullo
stesso motore mentre il primo lavora, e la lettura al volo e la passata
lavorano insieme (revisione della 1.80.0).
"""

import asyncio
import contextlib
import importlib.util
import re
import threading

# Fin dove arriva la fascia dei sottotitoli impressi, dal basso.
FASCIA = 0.30
# Sopra questa luminosita' un punto e' parte di una scritta chiara.
SOGLIA_DEL_CHIARO = 190
# Sopra questa differenza fra le due foto un punto e' parte del sottotitolo.
SOGLIA_DELLA_DIFFERENZA = 40
# La lingua quando la traccia non la dice.
LINGUA_PREDEFINITA = "it"
# I codici di tre lettere delle tracce, ISO 639-2 nelle due forme, B e T,
# verso quelli di due delle lingue di Windows. Le prime due lettere non
# bastano: rum e' il rumeno, non il russo; est l'estone, non lo spagnolo.
ISO_639_2 = {
    "ita": "it", "eng": "en", "fre": "fr", "fra": "fr", "ger": "de", "deu": "de", "spa": "es", "por": "pt", "rus": "ru",
    "rum": "ro", "ron": "ro", "pol": "pl", "cze": "cs", "ces": "cs", "slo": "sk", "slk": "sk", "slv": "sl", "gre": "el",
    "ell": "el", "swe": "sv", "dut": "nl", "nld": "nl", "chi": "zh", "zho": "zh", "jpn": "ja", "kor": "ko", "ara": "ar",
    "tur": "tr", "hun": "hu", "fin": "fi", "dan": "da", "nor": "nb", "nob": "nb", "est": "et", "lav": "lv", "lit": "lt",
    "hrv": "hr", "srp": "sr", "bul": "bg", "ukr": "uk", "heb": "he", "hin": "hi", "tha": "th", "vie": "vi", "cat": "ca",
    "glg": "gl", "baq": "eu", "eus": "eu", "ind": "id", "may": "ms", "msa": "ms", "per": "fa", "fas": "fa",
}

_locale = threading.local()


def _winrt():
    """I moduli di winrt, o None se non ci sono."""
    try:
        from winrt.windows.globalization import Language
        from winrt.windows.graphics.imaging import BitmapAlphaMode, BitmapPixelFormat, SoftwareBitmap
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.storage.streams import DataWriter
    except ImportError:
        return None
    return Language, BitmapAlphaMode, BitmapPixelFormat, SoftwareBitmap, OcrEngine, DataWriter


def lingue():
    """I codici delle lingue che Windows sa riconoscere, come it-IT; vuoto
    se il riconoscimento non c'e'."""
    moduli = _winrt()
    if moduli is None:
        return []
    with contextlib.suppress(Exception):
        return [l.language_tag for l in moduli[4].available_recognizer_languages]
    return []


def disponibile():
    """Vero se il riconoscimento c'e', con le sue lingue, e c'e' anche
    Pillow, che fa le immagini: senza, le foto non arriverebbero mai."""
    return importlib.util.find_spec("PIL") is not None and bool(lingue())


def lingua_per(etichetta):
    """La lingua del riconoscimento per una traccia: quella che dice, se
    Windows la sa leggere, altrimenti l'italiano, altrimenti la prima che c'e'.
    etichetta e' quella di mpv, come it, ita, en, eng."""
    installate = lingue()
    corti = {l.split("-")[0].lower(): l for l in installate}
    codice = (etichetta or "").lower().split("-")[0].split("_")[0]
    codice = ISO_639_2.get(codice, codice)
    if codice in corti:
        return corti[codice]
    if LINGUA_PREDEFINITA in corti:
        return corti[LINGUA_PREDEFINITA]
    return installate[0] if installate else None


def _motore(lingua):
    """Il motore della lingua per il filo che chiama: ogni filo ha i suoi."""
    moduli = _winrt()
    if moduli is None or lingua is None:
        return None
    motori = getattr(_locale, "motori", None)
    if motori is None:
        motori = _locale.motori = {}
    if lingua not in motori:
        motori[lingua] = moduli[4].try_create_from_language(moduli[0](lingua))
    return motori[lingua]


def _bitmap(immagine):
    """Un'immagine di Pillow come la vuole Windows: BGRA, alfa premoltiplicato."""
    from PIL import Image

    moduli = _winrt()
    _language, alfa, formato, software_bitmap, _engine, scrittore = moduli
    r, g, b, a = immagine.convert("RGBA").split()
    dati = scrittore()
    dati.write_bytes(Image.merge("RGBA", (b, g, r, a)).tobytes())
    return software_bitmap.create_copy_with_alpha_from_buffer(dati.detach_buffer(), formato.BGRA8, immagine.width, immagine.height, alfa.PREMULTIPLIED)


def leggi(immagine, lingua):
    """Le righe di testo che Windows legge nell'immagine, in una lista; vuota
    se non legge niente o se il riconoscimento non c'e'. Da un filo a parte."""
    motore = _motore(lingua)
    if motore is None or immagine is None:
        return []

    async def riconosci():
        return await motore.recognize_async(_bitmap(immagine))

    esito = asyncio.run(riconosci())
    return [" ".join(riga.text.split()) for riga in esito.lines if riga.text.strip()]


def scritte_della_differenza(con, senza):
    """Il sottotitolo a immagini isolato: i punti dove le due foto, con e
    senza sottotitoli, differiscono, e che sono chiari, in nero su bianco e
    ingranditi. None se le foto sono uguali, cioe' non c'e' sottotitolo."""
    from PIL import ImageChops, ImageOps

    con, senza = con.convert("RGB"), senza.convert("RGB")
    maschera = ImageChops.difference(con, senza).convert("L").point(lambda v: 255 if v > SOGLIA_DELLA_DIFFERENZA else 0)
    riquadro = maschera.getbbox()
    if riquadro is None:
        return None
    x0, y0, x1, y1 = riquadro
    scatola = (max(0, x0 - 10), max(0, y0 - 10), min(con.width, x1 + 10), min(con.height, y1 + 10))
    chiari = con.crop(scatola).convert("L").point(lambda v: 255 if v > 150 else 0)
    solo = ImageChops.multiply(chiari, maschera.crop(scatola))
    larghezza, altezza = scatola[2] - scatola[0], scatola[3] - scatola[1]
    return ImageOps.invert(solo).resize((larghezza * 2, altezza * 2)).convert("RGB")


def scritte_sul_nero(foto):
    """Il sottotitolo a immagini su un fotogramma annerito dal filtro del
    motore: i punti chiari sono le sue lettere, in nero su bianco e
    ingrandite. None se non ce ne sono. Una foto sola: con due, una con e una
    senza sottotitoli, il fotogramma cambiava fra l'una e l'altra."""
    from PIL import ImageOps

    chiari = foto.convert("L").point(lambda v: 255 if v > 150 else 0)
    riquadro = chiari.getbbox()
    if riquadro is None:
        return None
    x0, y0, x1, y1 = riquadro
    ritaglio = ImageOps.invert(chiari.crop((max(0, x0 - 10), max(0, y0 - 10), min(foto.width, x1 + 10), min(foto.height, y1 + 10)))).convert("RGB")
    return ritaglio.resize((ritaglio.width * 2, ritaglio.height * 2))


def fascia_in_basso(quadro):
    """La fascia in basso del fotogramma dove stanno i sottotitoli impressi:
    i punti chiari in nero su bianco; ingrandita se il video e' piccolo."""
    from PIL import ImageOps

    grigio = quadro.convert("L")
    fascia = grigio.crop((0, int(grigio.height * (1 - FASCIA)), grigio.width, grigio.height))
    chiara = ImageOps.invert(fascia.point(lambda v: 255 if v > SOGLIA_DEL_CHIARO else 0)).convert("RGB")
    if chiara.width < 1000:
        chiara = chiara.resize((chiara.width * 2, chiara.height * 2))
    return chiara


def impronta(immagine):
    """Un riassunto di un'immagine, per sapere se e' cambiata: 128 per 16
    celle, ciascuna con la media dei suoi punti. Piu' piccola, le lettere
    sottili di un sottotitolo sparivano nella media (prova della 1.80.0)."""
    from PIL import Image

    return immagine.convert("L").resize((128, 16), Image.Resampling.BOX).tobytes()


def cambiata(prima, dopo, celle=3, soglia=24):
    """Vero se almeno celle celle delle due impronte differiscono piu' della
    soglia: un sottotitolo cambia poche celle, ma di molto."""
    if prima is None or dopo is None or len(prima) != len(dopo):
        return True
    return sum(1 for a, b in zip(prima, dopo, strict=True) if abs(a - b) > soglia) >= celle


def parole(righe):
    """Quante parole vere ci sono nelle righe: due lettere almeno."""
    return sum(len(re.findall(r"[^\W\d_]{2,}", riga)) for riga in righe)

