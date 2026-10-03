# MeTeOra, i tag dei file: letti, scritti e cancellati con mutagen.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 10, punto d. Nella 1.70.0 il blocco INFO dei WAV.

"""I tag dei file audio e video, con mutagen (tappa 10, 1.69.0).

Ogni famiglia di formati chiama a modo suo gli stessi tag: ID3 per MP3,
WAV e AIFF; i commenti Vorbis per FLAC, OGG, Opus e Speex; gli atomi di
MP4 e M4A; APEv2 per Monkey's Audio, WavPack, Musepack e i TTA che lo
hanno; gli attributi ASF per WMA e WMV. MeTeOra mostra sempre i dieci tag
comuni, anche vuoti, cosi' si possono aggiungere, e poi gli altri che il
file ha gia'. MKV e WebM no: per scriverli servirebbe MKVToolNix.
Un tag e' un dizionario: chiave (quella comune, come "titolo", oppure
quella della famiglia con la tilde davanti, come
"~TXXX:REPLAYGAIN_TRACK_GAIN", cosi' le due non si confondono mai), nome da
leggere, valore (testo; vuoto se il tag non c'e') e testo (vero se si
modifica). Non si modificano, ma si leggono, i tag che non sono testo,
come le copertine, e quelli su piu' righe, come i testi delle canzoni: un
campo da una riga ne perderebbe l'impaginazione.
Un tag con piu' valori, come due artisti, si legge con i valori divisi da
punto e virgola, e si riscrive diviso allo stesso modo; un tag con un
valore solo resta di un valore solo.
I WAV hanno anche il blocco RIFF LIST/INFO, quello che legge e scrive
Esplora risorse, e che mutagen non conosce: MeTeOra lo legge, con i tag
comuni presi da li' quando ID3 non li ha, e scrive i tag comuni in tutti e
due i posti (1.70.0, Gabriele). Il testo va nella codifica di Windows, la
cp1252, o in UTF-8 se non ci sta. Un WAV con la struttura irregolare, come
una registrazione interrotta, non si tocca.
"""

import os
import re
import struct

# I dieci tag comuni, nell'ordine in cui si mostrano.
COMUNI = (("titolo", "Titolo"), ("artista", "Artista"), ("album", "Album"), ("artista_album", "Artista dell'album"), ("anno", "Anno"),
    ("genere", "Genere"), ("traccia", "Traccia"), ("disco", "Disco"), ("compositore", "Compositore"), ("commento", "Commento"))
NOMI_COMUNI = dict(COMUNI)
# La tilde davanti alle chiavi della famiglia.
ALTRO = "~"

CHIAVI = {
    "id3": {"titolo": "TIT2", "artista": "TPE1", "album": "TALB", "artista_album": "TPE2", "anno": "TDRC", "genere": "TCON",
        "traccia": "TRCK", "disco": "TPOS", "compositore": "TCOM", "commento": "COMM"},
    "vorbis": {"titolo": "title", "artista": "artist", "album": "album", "artista_album": "albumartist", "anno": "date", "genere": "genre",
        "traccia": "tracknumber", "disco": "discnumber", "compositore": "composer", "commento": "comment"},
    "mp4": {"titolo": "\xa9nam", "artista": "\xa9ART", "album": "\xa9alb", "artista_album": "aART", "anno": "\xa9day", "genere": "\xa9gen",
        "traccia": "trkn", "disco": "disk", "compositore": "\xa9wrt", "commento": "\xa9cmt"},
    "ape": {"titolo": "Title", "artista": "Artist", "album": "Album", "artista_album": "Album Artist", "anno": "Year", "genere": "Genre",
        "traccia": "Track", "disco": "Disc", "compositore": "Composer", "commento": "Comment"},
    "asf": {"titolo": "Title", "artista": "Author", "album": "WM/AlbumTitle", "artista_album": "WM/AlbumArtist", "anno": "WM/Year",
        "genere": "WM/Genre", "traccia": "WM/TrackNumber", "disco": "WM/PartOfSet", "compositore": "WM/Composer", "commento": "Description"},
}

# Le estensioni dei file di cui MeTeOra sa scrivere i tag.
ESTENSIONI = frozenset({".mp3", ".wav", ".aif", ".aiff", ".tta", ".flac", ".ogg", ".oga", ".opus", ".spx", ".m4a", ".m4b", ".mp4", ".m4v",
    ".alac", ".ape", ".wv", ".mpc", ".wma", ".wmv", ".asf"})
_FAMIGLIE = {"MP3": "id3", "EasyMP3": "id3", "WAVE": "id3", "AIFF": "id3", "TrueAudio": "id3", "FLAC": "vorbis", "OggVorbis": "vorbis",
    "OggOpus": "vorbis", "OggSpeex": "vorbis", "OggFLAC": "vorbis", "MP4": "mp4", "MonkeysAudio": "ape", "WavPack": "ape",
    "Musepack": "ape", "OptimFROG": "ape", "ASF": "asf", "APEv2File": "ape"}

# I nomi da leggere di qualche tag non comune, per famiglia.
NOMI_NOTI = {
    "id3": {"TENC": "Codificato da", "TSSE": "Programma di codifica", "TCOP": "Copyright", "TBPM": "BPM", "TKEY": "Tonalità", "TLAN": "Lingua",
        "TPUB": "Editore", "TSRC": "ISRC", "TIT1": "Gruppo", "TIT3": "Sottotitolo", "TPE3": "Direttore", "TPE4": "Remix", "TEXT": "Paroliere",
        "TMOO": "Umore", "TOAL": "Album originale", "TOPE": "Artista originale", "TSOP": "Artista per l'ordine", "TSOA": "Album per l'ordine",
        "TSOT": "Titolo per l'ordine", "TSO2": "Artista dell'album per l'ordine", "TCMP": "Compilation", "USLT": "Testo", "APIC": "Copertina",
        "TDOR": "Data originale", "TDRL": "Data di pubblicazione", "TDEN": "Data di codifica", "TDTG": "Data dei tag"},
    "mp4": {"\xa9too": "Programma di codifica", "\xa9lyr": "Testo", "\xa9grp": "Gruppo", "cprt": "Copyright", "covr": "Copertina", "tmpo": "BPM",
        "cpil": "Compilation", "pgap": "Senza pause", "desc": "Descrizione", "soar": "Artista per l'ordine", "soal": "Album per l'ordine",
        "sonm": "Titolo per l'ordine"},
    "asf": {"WM/Picture": "Copertina", "WM/EncodedBy": "Codificato da", "WM/ToolName": "Programma di codifica", "WM/Lyrics": "Testo",
        "WM/Publisher": "Editore", "Copyright": "Copyright", "WM/BeatsPerMinute": "BPM"},
}
# I campi del blocco INFO dei WAV: quelli dei tag comuni, e i nomi da
# leggere degli altri piu' diffusi.
INFO_COMUNI = {"titolo": "INAM", "artista": "IART", "album": "IPRD", "anno": "ICRD", "genere": "IGNR", "commento": "ICMT", "traccia": "ITRK"}
NOMI_INFO = {"ICOP": "Copyright", "ISFT": "Programma", "IENG": "Tecnico del suono", "ITCH": "Tecnico della digitalizzazione", "ISRC": "Fonte",
    "IKEY": "Parole chiave", "ISBJ": "Soggetto", "IARL": "Archivio", "ICMS": "Commissionato da", "IMED": "Supporto", "ISRF": "Supporto originale",
    "IMUS": "Compositore", "IPRT": "Parte"}
INFO = "INFO:"
# Un nome di quattro caratteri stampabili, come quelli degli spezzoni RIFF.
_FOURCC = re.compile(rb"[\x20-\x7e]{4}")
# Quanti byte dopo la fine del RIFF si lasciano stare, come un ID3v1 in coda.
CODA_AMMESSA = 1024
# Il separatore fra piu' valori dello stesso tag.
SEPARATORE = "; "
# Una data come la scrivono i tag, dall'anno solo fino all'ora: 1999,
# 1999-05-21, 2012-03-26T07:00:00Z.
_DATA = re.compile(r"\d{4}(-\d{2}(-\d{2}([T ]\d{2}(:\d{2}(:\d{2})?)?Z?)?)?)?")
# I frame ID3 che update_to_v23 converte, invece di toglierli.
_CONVERTITI_IN_V23 = frozenset({"TDRC", "TDOR", "TIPL", "TMCL"})


class ErroreTag(Exception):
    """Un file di cui i tag non si leggono o non si scrivono, o un valore
    che non va: il messaggio si legge cosi' com'e'."""


def modificabile(percorso):
    """Vero se MeTeOra sa scrivere i tag di questo tipo di file."""
    return os.path.splitext(percorso)[1].casefold() in ESTENSIONI


def _motivo(errore):
    return getattr(errore, "strerror", None) or str(errore) or type(errore).__name__


def _apri(percorso):
    """(file di mutagen, famiglia), con i tag pronti. Un file rovinato puo'
    far sollevare a mutagen ogni sorta di eccezione: diventano tutte
    ErroreTag."""
    import mutagen
    from mutagen.apev2 import APEv2File

    nome = os.path.basename(percorso)
    try:
        file = mutagen.File(percorso)
        famiglia = _FAMIGLIE.get(type(file).__name__) if file is not None else None
        if type(file).__name__ == "TrueAudio":
            # I TTA portano di solito un APEv2, che mutagen.trueaudio non legge.
            ape = APEv2File(percorso)
            if ape.tags is not None:
                file, famiglia = ape, "ape"
        if famiglia is not None and file.tags is None:
            file.add_tags()
    except Exception as e:
        # mutagen su un file rovinato solleva di tutto.
        raise ErroreTag(f"Non riesco a leggere i tag di {nome}: {_motivo(e)}") from e
    if famiglia is None:
        raise ErroreTag(f"MeTeOra non sa scrivere i tag di {nome}.")
    return file, famiglia


def _pulito(testo):
    """Un valore su una riga, senza i caratteri di controllo."""
    return " ".join(str(testo).replace("\x00", SEPARATORE).split())


pulito = _pulito


def _voce(chiave, nome, valori, testo=True):
    """Un tag letto: valori sono i testi grezzi del file."""
    valori = [str(v) for v in valori]
    su_piu_righe = any("\n" in v or "\r" in v for v in valori)
    return {"chiave": chiave, "nome": nome, "valore": SEPARATORE.join(_pulito(v) for v in valori), "testo": testo and not su_piu_righe}


def _sola_lettura(chiave, nome, descrizione):
    return {"chiave": chiave, "nome": nome, "valore": descrizione, "testo": False}


def _dimensione(byte):
    return f"{max(1, round(byte / 1000))} KB" if byte >= 1000 else f"{byte} byte"


def leggi(percorso):
    """I tag del file: i dieci comuni, anche vuoti, e poi gli altri che ha,
    in ordine di nome. Solleva ErroreTag."""
    file, famiglia = _apri(percorso)
    try:
        comuni, altri = _LETTURE[famiglia](file.tags)
    except Exception as e:
        # Un frame rovinato non deve fermare chi legge.
        raise ErroreTag(f"Non riesco a leggere i tag di {os.path.basename(percorso)}: {_motivo(e)}") from e
    if _e_un_wav(file):
        _unisci_info(percorso, comuni, altri)
    risultato = [comuni.get(chiave) or _voce(chiave, nome, []) for chiave, nome in COMUNI]
    for voce, (chiave, nome) in zip(risultato, COMUNI, strict=True):
        voce["chiave"], voce["nome"] = chiave, nome
    return risultato + sorted(altri, key=lambda t: t["nome"].casefold())


def _e_un_wav(file):
    return type(file).__name__ == "WAVE"


def _unisci_info(percorso, comuni, altri):
    """I campi del blocco INFO: i comuni dove ID3 non li ha, gli altri a parte."""
    per_campo = {campo: chiave for chiave, campo in INFO_COMUNI.items()}
    for campo, valore in leggi_info(percorso).items():
        chiave = per_campo.get(campo)
        if chiave is not None:
            if not (comuni.get(chiave) or {}).get("valore"):
                comuni[chiave] = _voce(chiave, "", [valore])
        else:
            altri.append(_voce(ALTRO + INFO + campo, NOMI_INFO.get(campo, campo), [valore]))


def comuni_del_file(file):
    """I tag comuni di un file gia' aperto con mutagen, senza la modalita'
    easy: dizionario dalla chiave comune al valore, senza i vuoti. Vuoto se
    il file non e' di una famiglia che MeTeOra conosce o non si legge. Lo
    usa lo schedario, per il filtro e la ricerca, senza aprire il file due
    volte."""
    famiglia = _FAMIGLIE.get(type(file).__name__)
    if famiglia is None:
        return {}
    try:
        comuni = _LETTURE[famiglia](file.tags)[0] if file.tags is not None else {}
        if _e_un_wav(file):
            _unisci_info(file.filename, comuni, [])
        risultato = {chiave: voce["valore"] for chiave, voce in comuni.items() if voce["valore"]}
        if famiglia == "vorbis" and "anno" not in risultato and file.tags.get("year"):
            # Qualche programma scrive l'anno in YEAR invece che in DATE.
            risultato["anno"] = SEPARATORE.join(_pulito(v) for v in file.tags["year"])
    except Exception:  # noqa: BLE001 - un file rovinato non deve fermare lo schedario
        return {}
    return risultato


def _commento_id3(tags):
    """Il commento comune di un ID3: il primo COMM senza descrizione, in
    ordine di chiave; gli altri, in altre lingue, sono tag a parte."""
    from mutagen.id3 import COMM

    return next((k for k, f in sorted(tags.items()) if isinstance(f, COMM) and not f.desc), None)


def _leggi_id3(tags):
    from mutagen.id3 import APIC, COMM, TextFrame, UrlFrame

    comuni, altri = {}, []
    per_frame = {fid: chiave for chiave, fid in CHIAVI["id3"].items() if fid != "COMM"}
    commento = _commento_id3(tags)
    for chiave_id3, frame in sorted(tags.items()):
        fid = frame.FrameID
        if chiave_id3 == commento:
            comuni["commento"] = _voce("commento", "", frame.text)
        elif fid in per_frame:
            # Il genere puo' essere un numero fra parentesi, come (17): genres lo scioglie.
            comuni[per_frame[fid]] = _voce(per_frame[fid], "", frame.genres if fid == "TCON" else frame.text)
        elif isinstance(frame, COMM):
            altri.append(_voce(ALTRO + chiave_id3, frame.desc or f"Commento ({frame.lang})", frame.text))
        elif isinstance(frame, TextFrame):
            nome = frame.desc if fid == "TXXX" and frame.desc else NOMI_NOTI["id3"].get(fid, fid)
            altri.append(_voce(ALTRO + chiave_id3, nome, frame.text))
        elif isinstance(frame, UrlFrame):
            altri.append(_sola_lettura(ALTRO + chiave_id3, NOMI_NOTI["id3"].get(fid, fid), frame.url))
        elif isinstance(frame, APIC):
            altri.append(_sola_lettura(ALTRO + chiave_id3, "Copertina", f"immagine di {_dimensione(len(frame.data))}"))
        else:
            altri.append(_sola_lettura(ALTRO + chiave_id3, NOMI_NOTI["id3"].get(fid, fid), "dati non testuali"))
    return comuni, altri


def _leggi_vorbis(tags):
    comuni, altri = {}, []
    per_chiave = {k: chiave for chiave, k in CHIAVI["vorbis"].items()}
    # VComment e' una lista di coppie: iterandola si hanno le coppie, keys() da' i nomi.
    for k in sorted({k.casefold() for k in tags.keys()}):  # noqa: SIM118
        valori = tags.get(k) or []
        if k in per_chiave:
            comuni[per_chiave[k]] = _voce(per_chiave[k], "", valori)
        elif k == "metadata_block_picture":
            altri.append(_sola_lettura(ALTRO + k, "Copertina", "immagine"))
        else:
            altri.append(_voce(ALTRO + k, k.upper(), valori))
    return comuni, altri


def _leggi_mp4(tags):
    from mutagen.mp4 import AtomDataType

    comuni, altri = {}, []
    per_chiave = {k: chiave for chiave, k in CHIAVI["mp4"].items()}
    for k, valori in sorted(tags.items()):
        # I booleani, come cpil e pgap, mutagen li tiene da soli, non in una lista.
        valori = valori if isinstance(valori, list) else [valori]
        if k in ("trkn", "disk"):
            comuni[per_chiave[k]] = _voce(per_chiave[k], "", [f"{n}/{totale}" if totale else str(n) for n, totale in valori])
        elif k in per_chiave:
            comuni[per_chiave[k]] = _voce(per_chiave[k], "", valori)
        elif k.startswith("----:"):
            nome = k.rsplit(":", 1)[-1]
            if all(getattr(v, "dataformat", AtomDataType.UTF8) == AtomDataType.UTF8 for v in valori):
                altri.append(_voce(ALTRO + k, nome, [bytes(v).decode("utf-8", "replace") for v in valori]))
            else:
                altri.append(_sola_lettura(ALTRO + k, nome, "dati non testuali"))
        elif valori and all(isinstance(v, str) for v in valori):
            altri.append(_voce(ALTRO + k, NOMI_NOTI["mp4"].get(k, k), valori))
        elif k == "covr":
            altri.append(_sola_lettura(ALTRO + k, "Copertina", f"immagine di {_dimensione(sum(len(v) for v in valori))}"))
        else:
            altri.append(_sola_lettura(ALTRO + k, NOMI_NOTI["mp4"].get(k, k), _pulito(SEPARATORE.join(str(v) for v in valori))))
    return comuni, altri


def _leggi_ape(tags):
    from mutagen.apev2 import APETextValue

    comuni, altri = {}, []
    per_chiave = {k.casefold(): chiave for chiave, k in CHIAVI["ape"].items()}
    for k, valore in sorted(tags.items(), key=lambda kv: kv[0].casefold()):
        if isinstance(valore, APETextValue):
            if k.casefold() in per_chiave:
                comuni[per_chiave[k.casefold()]] = _voce(per_chiave[k.casefold()], "", list(valore))
            else:
                altri.append(_voce(ALTRO + k, k, list(valore)))
        elif k.casefold().startswith("cover art"):
            altri.append(_sola_lettura(ALTRO + k, "Copertina", f"immagine di {_dimensione(len(valore.value))}"))
        else:
            altri.append(_sola_lettura(ALTRO + k, k, "dati non testuali"))
    return comuni, altri


def _leggi_asf(tags):
    from mutagen.asf import ASFUnicodeAttribute

    comuni, altri = {}, []
    per_chiave = {k: chiave for chiave, k in CHIAVI["asf"].items()}
    for k in sorted(tags.keys()):
        valori = tags[k]
        if k in per_chiave:
            comuni[per_chiave[k]] = _voce(per_chiave[k], "", [v.value for v in valori])
        elif valori and all(isinstance(v, ASFUnicodeAttribute) for v in valori):
            altri.append(_voce(ALTRO + k, NOMI_NOTI["asf"].get(k, k), [v.value for v in valori]))
        elif k == "WM/Picture":
            altri.append(_sola_lettura(ALTRO + k, "Copertina", "immagine"))
        else:
            altri.append(_sola_lettura(ALTRO + k, NOMI_NOTI["asf"].get(k, k), _pulito(SEPARATORE.join(str(v.value) for v in valori))))
    return comuni, altri


_LETTURE = {"id3": _leggi_id3, "vorbis": _leggi_vorbis, "mp4": _leggi_mp4, "ape": _leggi_ape, "asf": _leggi_asf}


def controlla(chiave, valore):
    """Il valore pulito per il tag, o ErroreTag con il perche'. L'anno si
    scrive con quattro cifre, o come data, anche con l'ora; traccia e disco
    come numero, o numero e totale divisi dalla barra."""
    valore = _pulito(valore)
    if not valore:
        return ""
    if chiave == "anno" and not _DATA.fullmatch(valore):
        raise ErroreTag(f"{valore} non è un anno: si scrive con quattro cifre, per esempio 1999, oppure come data, 1999-05-21.")
    if chiave in ("traccia", "disco") and not re.fullmatch(r"\d{1,4}(/\d{1,4})?", valore):
        raise ErroreTag(f"{valore} non è un numero di {NOMI_COMUNI[chiave].lower()}: si scrive per esempio 3, oppure 3/12 con il totale.")
    return valore


def _valori(valore, esistenti):
    """Il valore come lista: diviso al punto e virgola se il tag aveva gia'
    piu' valori, intero altrimenti."""
    if len(esistenti) > 1:
        return [v.strip() for v in valore.split(SEPARATORE.strip()) if v.strip()]
    return [valore]


def scrivi(percorso, chiave, valore):
    """Scrive il tag nel file; un valore vuoto lo cancella. chiave e' una
    dei comuni o una di quelle, con la tilde, che leggi ha dato per il
    file. Solleva ErroreTag."""
    valore = controlla(chiave, valore)
    if os.path.splitext(percorso)[1].casefold() == ".wav":
        # Prima di mutagen: un WAV irregolare non si tocca, e il riempimento
        # che manca si aggiunge, o mutagen non ritroverebbe il suo id3.
        prepara_il_wav(percorso)
    file, famiglia = _apri(percorso)
    comune = not chiave.startswith(ALTRO)
    k = CHIAVI[famiglia][chiave] if comune else chiave[len(ALTRO):]
    try:
        if _e_un_wav(file) and not comune and k.startswith(INFO):
            # Un campo del blocco INFO che ID3 non ha: solo li'.
            scrivi_info(percorso, {k[len(INFO):]: valore})
            return
        _SCRITTURE[famiglia](file.tags, k, valore, comune)
        _salva(file, famiglia)
    except ErroreTag:
        raise
    except Exception as e:
        # mutagen su un file rovinato solleva di tutto.
        raise ErroreTag(f"Non riesco a scrivere i tag di {os.path.basename(percorso)}: {_motivo(e)}") from e
    if _e_un_wav(file) and chiave in INFO_COMUNI:
        # I tag comuni dei WAV vanno anche nel blocco INFO, per Esplora risorse.
        try:
            scrivi_info(percorso, {INFO_COMUNI[chiave]: valore})
        except ErroreTag as e:
            raise ErroreTag(f"ID3 scritto, il blocco INFO no: {e}") from e
        except Exception as e:
            raise ErroreTag(f"ID3 scritto, il blocco INFO di {os.path.basename(percorso)} no: {_motivo(e)}") from e


def _salva(file, famiglia):
    if famiglia == "id3":
        if file.tags.version[:2] == (2, 3):
            # Un tag 2.3 resta 2.3, quello che leggono Esplora risorse e i
            # lettori vecchi. mutagen lo carica in 2.4: update_to_v23 rimette
            # TYER e IPLS, ma toglie i frame che la 2.3 non ha, come TSOP, e
            # quelli tornano com'erano.
            prima = dict(file.tags.items())
            file.tags.update_to_v23()
            for k, frame in prima.items():
                if k not in file.tags and frame.FrameID not in _CONVERTITI_IN_V23:
                    file.tags.add(frame)
            file.save(v2_version=3)
        else:
            file.save(v2_version=4)
        return
    if famiglia == "ape":
        # APEv2 salvando taglia il file dall'inizio del suo tag, e con lui
        # l'ID3v1 che lo segue: si rimette in coda.
        with open(file.filename, "rb") as f:
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - 128))
            coda = f.read()
        file.save()
        if len(coda) == 128 and coda.startswith(b"TAG"):
            with open(file.filename, "rb+") as f:
                f.seek(-128, os.SEEK_END)
                if f.read(3) != b"TAG":
                    f.seek(0, os.SEEK_END)
                    f.write(coda)
        return
    file.save()


def _scrivi_id3(tags, k, valore, comune):
    from mutagen.id3 import COMM, TXXX, Frames, TimeStampTextFrame

    if comune and k == "COMM":
        # Il commento comune e' uno solo: gli altri COMM restano.
        chiave_id3 = _commento_id3(tags)
        vecchio = tags[chiave_id3] if chiave_id3 else None
        if vecchio is not None:
            del tags[chiave_id3]
        if valore:
            tags.add(COMM(encoding=3, lang=vecchio.lang if vecchio else "eng", desc="", text=_valori(valore, vecchio.text if vecchio else [])))
        return
    vecchio = tags.get(k)
    classe = Frames.get(k[:4])
    if classe is not None and issubclass(classe, TimeStampTextFrame) and valore and not _DATA.fullmatch(valore):
        raise ErroreTag(f"{valore} non è una data: si scrive per esempio 1999, oppure 1999-05-21.")
    if vecchio is not None:
        del tags[k]
    if not valore:
        return
    valori = _valori(valore, vecchio.text if vecchio is not None else [])
    if k.startswith("TXXX:"):
        tags.add(TXXX(encoding=3, desc=k[5:], text=valori))
    elif k.startswith("COMM:"):
        _comm, descrizione, lingua = [*k.split(":"), "", ""][:3]
        tags.add(COMM(encoding=3, lang=lingua or "eng", desc=descrizione, text=valori))
    elif classe is not None:
        tags.add(classe(encoding=3, text=valori))
    else:
        raise ErroreTag(f"Il tag {k} non si modifica.")


def _scrivi_vorbis(tags, k, valore, _comune):
    vecchi = tags.get(k) or []
    if k in tags:
        del tags[k]
    if valore:
        tags[k] = _valori(valore, vecchi)


def _scrivi_mp4(tags, k, valore, _comune):
    from mutagen.mp4 import MP4FreeForm

    vecchi = tags.get(k) or []
    vecchi = vecchi if isinstance(vecchi, list) else [vecchi]
    if k in tags:
        del tags[k]
    if not valore:
        return
    if k in ("trkn", "disk"):
        numero, _barra, totale = valore.partition("/")
        tags[k] = [(int(numero), int(totale or 0))]
    elif k.startswith("----:"):
        tags[k] = [MP4FreeForm(v.encode("utf-8")) for v in _valori(valore, vecchi)]
    else:
        tags[k] = _valori(valore, vecchi)


def _scrivi_ape(tags, k, valore, _comune):
    vecchio = tags.get(k)
    vecchi = list(vecchio) if vecchio is not None else []
    if k in tags:
        del tags[k]
    if valore:
        tags[k] = _valori(valore, vecchi)


def _scrivi_asf(tags, k, valore, _comune):
    vecchi = tags.get(k) or []
    if k in tags:
        del tags[k]
    if valore:
        tags[k] = _valori(valore, vecchi)


_SCRITTURE = {"id3": _scrivi_id3, "vorbis": _scrivi_vorbis, "mp4": _scrivi_mp4, "ape": _scrivi_ape, "asf": _scrivi_asf}


class _Riff:
    """La struttura di un WAV RIFF, letta senza toccarla: gli spezzoni
    (nome, inizio, dimensione dei dati, tipo della lista), la fine del RIFF
    con il suo byte di riempimento, i punti in cui manca il riempimento dopo
    uno spezzone dispari, come nei WAV scritti dal modulo wave di Python, e
    se la struttura e' abbastanza sana da modificarla. Non lo e' se uno
    spezzone sborda, se il giro non finisce sulla fine del RIFF, se dopo il
    RIFF c'e' piu' di un ID3v1 o poco piu', come nelle registrazioni
    interrotte, o se il file passa i 4 GB."""

    def __init__(self, f):
        self.spezzoni, self.pad_mancanti, self.sicuro, self.valido, self.fine = [], [], False, False, 0
        f.seek(0, os.SEEK_END)
        self.dimensione_del_file = f.tell()
        f.seek(0)
        testa = f.read(12)
        if len(testa) < 12 or testa[:4] != b"RIFF" or testa[8:12] != b"WAVE":
            return
        self.valido = True
        dichiarata = struct.unpack("<I", testa[4:8])[0]
        self.fine = min(8 + dichiarata + (dichiarata & 1), self.dimensione_del_file)
        sicuro = self.dimensione_del_file <= 0xFFFFFFFF + 8
        posizione = 12
        while posizione + 8 <= self.fine:
            f.seek(posizione)
            nome, dimensione = struct.unpack("<4sI", f.read(8))
            fine_dei_dati = posizione + 8 + dimensione
            if not _FOURCC.fullmatch(nome) or fine_dei_dati > self.fine:
                sicuro = False
                break
            tipo = f.read(4) if nome == b"LIST" and dimensione >= 4 else b""
            self.spezzoni.append((nome, posizione, dimensione, tipo))
            posizione = fine_dei_dati
            if dimensione & 1:
                f.seek(posizione)
                qui = f.read(5)
                if posizione >= self.fine or (_FOURCC.fullmatch(qui[:4]) and not _FOURCC.fullmatch(qui[1:5])):
                    # Il riempimento manca: il file finisce qui, o comincia subito un altro spezzone.
                    self.pad_mancanti.append(posizione)
                else:
                    posizione += 1
        if posizione != self.fine or self.dimensione_del_file - self.fine > CODA_AMMESSA:
            sicuro = False
        self.sicuro = sicuro


def _campi_info(dati):
    """I campi di un blocco INFO, in ordine: lista di [nome, byte]. Un
    campo dispari senza riempimento si riconosce dal nome che segue. None se
    il blocco e' incoerente."""
    campi, i = [], 0
    while i + 8 <= len(dati):
        nome, lunghezza = struct.unpack_from("<4sI", dati, i)
        if not _FOURCC.fullmatch(nome) or i + 8 + lunghezza > len(dati):
            return None
        campi.append([nome.decode("ascii"), dati[i + 8:i + 8 + lunghezza]])
        i += 8 + lunghezza
        if lunghezza & 1 and not (_FOURCC.fullmatch(dati[i:i + 4]) and not _FOURCC.fullmatch(dati[i + 1:i + 5])):
            i += 1
    return campi if len(dati) - i <= 1 else None


def _testo_info(byte):
    byte = byte.split(b"\x00", 1)[0]
    try:
        return byte.decode("utf-8")
    except UnicodeDecodeError:
        return byte.decode("cp1252", "replace")


def _codifica_info(testo):
    """Il testo per il blocco INFO: nella codifica di Windows se ci sta,
    altrimenti in UTF-8, che leggi_info prova per prima."""
    try:
        return testo.encode("cp1252") + b"\x00"
    except UnicodeEncodeError:
        return testo.encode("utf-8") + b"\x00"


def _blocchi_info(f, riff):
    """I blocchi INFO del RIFF: lista di (spezzone, campi o None se incoerente)."""
    blocchi = []
    for spezzone in riff.spezzoni:
        if spezzone[0] == b"LIST" and spezzone[3] == b"INFO":
            f.seek(spezzone[1] + 12)
            blocchi.append((spezzone, _campi_info(f.read(spezzone[2] - 4))))
    return blocchi


def leggi_info(percorso):
    """I campi non vuoti dei blocchi INFO di un WAV, dal nome al testo, con
    la precedenza al primo; vuoto se il file non li ha o non e' un WAV RIFF."""
    risultato = {}
    try:
        with open(percorso, "rb") as f:
            riff = _Riff(f)
            if not riff.valido:
                return {}
            for _spezzone, campi in _blocchi_info(f, riff):
                for nome, byte in campi or []:
                    testo = _testo_info(byte)
                    if nome not in risultato and testo.strip():
                        risultato[nome] = testo
    except (OSError, struct.error):
        return {}
    return risultato


def prepara_il_wav(percorso):
    """Prima di scrivere i tag di un WAV: ErroreTag se la struttura non e'
    sana, e il riempimento che manca dopo uno spezzone dispari aggiunto,
    perche' ne' mutagen ne' il blocco INFO ritroverebbero gli spezzoni dopo."""
    from mutagen._util import insert_bytes

    nome = os.path.basename(percorso)
    try:
        with open(percorso, "rb+") as f:
            riff = _Riff(f)
            if not riff.valido or not riff.sicuro:
                raise ErroreTag(f"La struttura di {nome} non è regolare, per esempio una registrazione interrotta: i suoi tag restano com'erano.")
            if not riff.pad_mancanti:
                return
            for posizione in reversed(riff.pad_mancanti):
                insert_bytes(f, 1, posizione)
                f.seek(posizione)
                f.write(b"\x00")
            f.seek(4)
            f.write(struct.pack("<I", riff.fine + len(riff.pad_mancanti) - 8))
    except OSError as e:
        raise ErroreTag(f"Non riesco a preparare {nome}: {_motivo(e)}") from e


def scrivi_info(percorso, cambi):
    """Cambia i campi del blocco INFO di un WAV: cambi va dal nome del campo
    al testo nuovo, vuoto per toglierlo. Si cambia il primo campo con quel
    nome; togliendolo si tolgono tutti. Piu' blocchi INFO diventano uno
    solo; senza, il blocco nasce in fondo al RIFF. La modifica e' in posto,
    come quella di mutagen per ID3, e solo se qualcosa cambia davvero."""
    from mutagen._util import resize_bytes

    nome_del_file = os.path.basename(percorso)
    with open(percorso, "rb+") as f:
        riff = _Riff(f)
        if not riff.valido or not riff.sicuro or riff.pad_mancanti:
            raise ErroreTag(f"La struttura di {nome_del_file} non è regolare: il blocco INFO resta com'era.")
        blocchi = _blocchi_info(f, riff)
        if any(campi is None for _spezzone, campi in blocchi):
            raise ErroreTag(f"Il blocco INFO di {nome_del_file} è rovinato: resta com'era.")
        campi = [campo for _spezzone, uno in blocchi for campo in uno]
        nuovi = [list(campo) for campo in campi]
        for nome, testo in cambi.items():
            if testo:
                byte = _codifica_info(testo)
                primo = next((campo for campo in nuovi if campo[0] == nome), None)
                if primo is None:
                    nuovi.append([nome, byte])
                else:
                    primo[1] = byte
            else:
                nuovi = [campo for campo in nuovi if campo[0] != nome]
        if nuovi == campi and len(blocchi) <= 1:
            return
        corpo = b"".join(nome.encode("ascii") + struct.pack("<I", len(byte)) + byte + (b"\x00" if len(byte) & 1 else b"") for nome, byte in nuovi)
        nuovo = b"LIST" + struct.pack("<I", 4 + len(corpo)) + b"INFO" + corpo if corpo else b""
        differenza = 0
        # I blocchi in piu' si tolgono partendo dall'ultimo: gli inizi di prima restano buoni.
        for spezzone, _uno in reversed(blocchi[1:]):
            vecchia = 8 + spezzone[2] + (spezzone[2] & 1)
            resize_bytes(f, vecchia, 0, spezzone[1])
            differenza -= vecchia
        if blocchi:
            spezzone = blocchi[0][0]
            inizio, vecchia = spezzone[1], 8 + spezzone[2] + (spezzone[2] & 1)
        else:
            inizio, vecchia = riff.fine, 0
        resize_bytes(f, vecchia, len(nuovo), inizio)
        f.seek(inizio)
        f.write(nuovo)
        differenza += len(nuovo) - vecchia
        f.seek(4)
        f.write(struct.pack("<I", riff.fine + differenza - 8))


def leggi_insieme(percorsi):
    """I tag di piu' file insieme: i comuni, e gli altri che hanno tutti.
    Dove i valori sono diversi, diversi e' vero e il valore e' vuoto.
    Torna (tag, errori), con errori i messaggi dei file che non si leggono."""
    letti, errori = [], []
    for percorso in percorsi:
        try:
            letti.append(leggi(percorso))
        except ErroreTag as e:
            errori.append(str(e))
        except Exception as e:  # noqa: BLE001 - un file che non si legge non ferma gli altri
            errori.append(f"Non riesco a leggere i tag di {os.path.basename(percorso)}: {_motivo(e)}")
    if not letti:
        return [], errori
    per_file = [{t["chiave"]: t for t in tag} for tag in letti]
    in_tutti = set.intersection(*(set(d) for d in per_file))
    risultato = []
    for t in letti[0]:
        if t["chiave"] not in in_tutti:
            continue
        valori = {d[t["chiave"]]["valore"] for d in per_file}
        diversi = len(valori) > 1
        risultato.append({**t, "valore": "" if diversi else t["valore"], "testo": all(d[t["chiave"]]["testo"] for d in per_file), "diversi": diversi})
    return risultato, errori
