# MeTeOra, le prove degli indirizzi in rete: yt-dlp finto, niente rete.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 3.2.0, tappa 19 b del piano, issue 40.

import datetime
import hashlib
import io
import json
import os
import subprocess
import types
import zipfile

import pytest

import componenti
import filtro
import formati
import impostazioni
import indirizzi
import motore
import pulizia
import statistiche
from playlist import Archivio, Brano, Playlist
from schedario import Schedario

# La chiamata vera di yt-dlp, presa prima che il conftest la sostituisca.
_ESEGUI_VERO = indirizzi._esegui
YOUTUBE = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
GOOGLEVIDEO = "https://rr2.googlevideo.com/videoplayback?expire=9999999999&id=1"
INFO_YOUTUBE = {"title": "Me at the zoo", "duration": 19, "uploader": "jawed", "upload_date": "20050424", "url": GOOGLEVIDEO, "protocol": "https",
    "http_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64), di prova", "Accept": "text/html,*/*;q=0.8"},
    "chapters": [{"start_time": 0, "title": "Intro", "end_time": 5}, {"start_time": 5.5, "title": "The cool thing", "end_time": 17}]}
VIDEO = {"title": "Un video", "duration": 30, "requested_formats": [
    {"format_id": "395", "url": "https://video.example/v.mp4", "protocol": "https", "http_headers": {"Accept": "*/*"}},
    {"format_id": "251", "url": "https://video.example/a.webm", "protocol": "https"}]}
MIXCLOUD = {"title": "Cryptkeeper", "duration": 3723, "protocol": "http_dash_segments", "url": "https://aod.example/manifest.mpd",
    "manifest_url": "https://aod.example/manifest.mpd", "fragments": [{"url": "https://aod.example/init.mp4"}], "artist": "Vari", "release_year": 2017}
ALBUM = "https://blazo.bandcamp.com/album/jazz-format-mixtape-vol-1"
INFO_ALBUM = {"_type": "playlist", "title": "Jazz Format Mixtape vol.1", "entries": [
    {"_type": "url", "url": "https://blazo.bandcamp.com/track/intro", "title": "Intro"},
    {"_type": "url", "url": "https://blazo.bandcamp.com/track/due", "title": "Due", "duration": 120.5},
    {"_type": "playlist", "url": "https://blazo.bandcamp.com/annidata", "title": "Annidata"},
    {"_type": "url", "url": "senza-schema", "title": "Rotta"}]}
INFO_INTRO = {"title": "Intro", "duration": 60, "url": "https://t4.bcbits.com/stream/intro.mp3", "protocol": "https"}
INFO_DUE = {"title": "Due", "duration": 120.5, "url": "https://t4.bcbits.com/stream/due.mp3", "protocol": "https"}


def _risposte(monkeypatch, tabella, chiamate=None):
    """yt-dlp finto: risponde con l'info della tabella per l'indirizzo, che e'
    l'ultimo argomento, o con l'errore se la voce e' un testo."""
    def esegui(argomenti, attesa=indirizzi.ATTESA):
        if chiamate is not None:
            chiamate.append(list(argomenti))
        risposta = tabella[argomenti[-1]]
        if isinstance(risposta, str):
            raise indirizzi.ErroreIndirizzo(risposta)
        return json.loads(json.dumps(risposta))

    monkeypatch.setattr(indirizzi, "_esegui", esegui)


# Gli indirizzi, senza finestra.


def test_gli_indirizzi_non_hanno_l_estensione_di_un_formato():
    assert formati.e_indirizzo("https://x.it/a.mid") and formati.e_indirizzo("HTTP://x.it") and not formati.e_indirizzo(r"C:\a.mp3")
    assert not formati.e_indirizzo(None) and not formati.e_indirizzo("ftp://x.it/a.mp3")
    assert formati.estensione("https://x.it/a.mid") == "" and not formati.e_midi("https://x.it/a.mid") and not formati.supportato("https://x.it/a.mp3")
    assert formati.estensione(r"C:\a.MID") == ".mid"


def test_l_indirizzo_degli_appunti_e_quello_scritto():
    assert indirizzi.dagli_appunti("guarda qui: <https://www.raiplaysound.it/audio/x.html> bello") == "https://www.raiplaysound.it/audio/x.html"
    assert indirizzi.dagli_appunti("niente di utile") is None and indirizzi.dagli_appunti("") is None and indirizzi.dagli_appunti(None) is None
    assert indirizzi.dagli_appunti("https://") is None
    assert indirizzi.indirizzo_scritto("www.youtube.com/watch?v=1") == "https://www.youtube.com/watch?v=1"
    assert indirizzi.indirizzo_scritto("  http://radio.example:8000/flusso ") == "http://radio.example:8000/flusso"
    assert indirizzi.indirizzo_scritto("una frase con spazi") is None and indirizzi.indirizzo_scritto("parola") is None
    assert indirizzi.sito("https://www.youtube.com/watch?v=1") == "youtube.com" and indirizzi.sito("https://blazo.bandcamp.com/album/x") == "blazo.bandcamp.com"


def test_un_indirizzo_diretto_non_chiama_yt_dlp(monkeypatch):
    assert indirizzi.diretto("https://archive.org/download/x/Brano%201.mp3") and indirizzi.diretto("https://x.it/live/index.m3u8")
    assert not indirizzi.diretto(YOUTUBE) and not indirizzi.diretto("https://www.raiplaysound.it/audio/x.html")
    pagina = indirizzi.esplora("https://archive.org/download/x/Brano%201.mp3")
    assert not pagina.playlist and pagina.titolo == "Brano 1.mp3" and pagina.flusso.indirizzo == "https://archive.org/download/x/Brano%201.mp3"
    assert indirizzi.pronto("https://archive.org/download/x/Brano%201.mp3").indirizzo.endswith("Brano%201.mp3")


def test_il_motivo_di_yt_dlp():
    assert indirizzi._motivo("WARNING: qualcosa\nERROR: [IlPost] 1-avis: Unable to extract metadata; please report this issue on  https://github.com/x") == (
        "Unable to extract metadata")
    assert indirizzi._motivo("ERROR: Unsupported URL: https://example.com/") == "yt-dlp non conosce questo sito"
    assert indirizzi._motivo("ERROR: [youtube] abc: Video unavailable. This video is private.") == "Video unavailable. This video is private"
    assert indirizzi._motivo("") == "yt-dlp non ha detto perché"


def test_il_flusso_e_la_scheda_di_un_brano():
    flusso = indirizzi.flusso_dell_info(INFO_YOUTUBE)
    assert flusso.indirizzo == GOOGLEVIDEO and flusso.audio == ()
    # Le virgole delle intestazioni restano dentro la loro riga.
    assert flusso.intestazioni == ("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64), di prova", "Accept: text/html,*/*;q=0.8")
    scheda = indirizzi.scheda_dell_info(INFO_YOUTUBE)
    assert scheda["durata"] == 19.0 and scheda["tag"] == {"titolo": "Me at the zoo", "autore": "jawed", "anno": 2005} and scheda["indirizzo"]
    assert scheda["capitoli"] == [[0.0, "Intro"], [5.5, "The cool thing"]] and scheda["dim"] is None
    video = indirizzi.flusso_dell_info(VIDEO)
    assert video.indirizzo == "https://video.example/v.mp4" and video.audio == ("https://video.example/a.webm",) and video.intestazioni == ("Accept: */*",)
    mixcloud = indirizzi.flusso_dell_info(MIXCLOUD)
    assert mixcloud.indirizzo == "https://aod.example/manifest.mpd"
    assert indirizzi.scheda_dell_info(MIXCLOUD)["tag"] == {"titolo": "Cryptkeeper", "autore": "Vari", "anno": 2017} and "capitoli" not in indirizzi.scheda_dell_info(MIXCLOUD)
    with pytest.raises(indirizzi.ErroreIndirizzo):
        indirizzi.flusso_dell_info({"title": "senza flusso"})


def test_esplora_una_playlist_e_risolve_le_sue_voci(monkeypatch):
    chiamate = []
    _risposte(monkeypatch, {ALBUM: INFO_ALBUM, "https://blazo.bandcamp.com/track/intro": INFO_INTRO}, chiamate)
    pagina = indirizzi.esplora(ALBUM)
    assert pagina.playlist and pagina.titolo == "Jazz Format Mixtape vol.1"
    # Le sottoplaylist e le voci senza indirizzo restano fuori.
    assert pagina.voci == [("https://blazo.bandcamp.com/track/intro", "Intro", None), ("https://blazo.bandcamp.com/track/due", "Due", 120.5)]
    assert chiamate == [["--flat-playlist", "-f", indirizzi.FORMATO_AUDIO, ALBUM]]
    brano = indirizzi.risolvi("https://blazo.bandcamp.com/track/intro")
    assert brano.flusso.indirizzo == "https://t4.bcbits.com/stream/intro.mp3" and brano.scheda["durata"] == 60.0
    assert chiamate[-1] == ["--no-playlist", "-f", indirizzi.FORMATO_AUDIO, "https://blazo.bandcamp.com/track/intro"]
    # Il flusso trovato si tiene: la seconda volta yt-dlp non si chiama.
    di_nuovo = indirizzi.risolvi("https://blazo.bandcamp.com/track/intro")
    assert di_nuovo.flusso is brano.flusso and di_nuovo.scheda is None and len(chiamate) == 2
    with pytest.raises(indirizzi.ErroreIndirizzo, match="playlist"):
        indirizzi.risolvi(ALBUM)


def test_i_flussi_tenuti_valgono_con_il_video_giusto_e_scadono(monkeypatch):
    _risposte(monkeypatch, {YOUTUBE: INFO_YOUTUBE})
    pagina = indirizzi.esplora(YOUTUBE)
    assert indirizzi.pronto(YOUTUBE) is pagina.flusso and indirizzi.pronto(YOUTUBE, False) is pagina.flusso
    # Chiesto senza video, non vale per il video acceso.
    assert indirizzi.pronto(YOUTUBE, True) is None
    indirizzi.dimentica(YOUTUBE)
    assert indirizzi.pronto(YOUTUBE) is None
    # La scadenza scritta nell'indirizzo, se viene prima, vince.
    adesso = 1000.0
    scade = indirizzi.Flusso(f"https://x.it/v?expire={int(indirizzi.time.time()) + 600}")
    assert adesso + 500 < indirizzi._scadenza(scade, adesso) < adesso + 600
    assert indirizzi._scadenza(indirizzi.Flusso("https://x.it/v"), adesso) == adesso + indirizzi.FLUSSO_VALIDO
    monkeypatch.setattr(indirizzi.time, "monotonic", lambda: 0.0)
    indirizzi._tieni(YOUTUBE, False, pagina.flusso)
    monkeypatch.setattr(indirizzi.time, "monotonic", lambda: indirizzi.FLUSSO_VALIDO + 1)
    assert indirizzi.pronto(YOUTUBE) is None


def test_la_chiamata_vera_di_yt_dlp(monkeypatch):
    """Il comando, il JSON, gli errori e il tempo scaduto, con un processo finto."""
    monkeypatch.setattr(indirizzi, "_esegui", _ESEGUI_VERO)
    with pytest.raises(indirizzi.SenzaYtDlp):
        indirizzi._esegui(["-x", YOUTUBE])
    os.makedirs(indirizzi.cartella_di_ytdlp())
    open(indirizzi.eseguibile_di_ytdlp(), "wb").close()
    lanciati = []

    class Processo:
        uscita, errore, codice, appeso = json.dumps(INFO_YOUTUBE).encode(), b"", 0, False

        def __init__(self, comando, **opzioni):
            lanciati.append((comando, opzioni))
            self.returncode = None
            self.uccisi = 0

        def communicate(self, timeout=None):
            if Processo.appeso and not self.uccisi:
                raise subprocess.TimeoutExpired("yt-dlp", timeout)
            self.returncode = Processo.codice
            return Processo.uscita, Processo.errore

        def kill(self):
            self.uccisi += 1

    monkeypatch.setattr(indirizzi.subprocess, "Popen", Processo)
    assert indirizzi._esegui(["--no-playlist", YOUTUBE])["title"] == "Me at the zoo"
    comando, opzioni = lanciati[-1]
    assert comando[:7] == [indirizzi.eseguibile_di_ytdlp(), "--ignore-config", "--no-warnings", "--no-progress", "--encoding", "utf-8", "-J"]
    assert comando[-2:] == ["--no-playlist", YOUTUBE] and "--js-runtimes" not in comando and opzioni["stdin"] == subprocess.DEVNULL
    # Con QuickJS installato, yt-dlp lo usa per YouTube.
    os.makedirs(indirizzi.cartella_di_quickjs())
    open(indirizzi.eseguibile_di_quickjs(), "wb").close()
    indirizzi._esegui([YOUTUBE])
    assert f"quickjs:{indirizzi.eseguibile_di_quickjs()}" in lanciati[-1][0]
    Processo.codice, Processo.errore = 1, b"ERROR: [youtube] x: Private video"
    with pytest.raises(indirizzi.ErroreIndirizzo, match="Private video"):
        indirizzi._esegui([YOUTUBE])
    Processo.codice, Processo.uscita = 0, b"non json"
    with pytest.raises(indirizzi.ErroreIndirizzo, match="non capisco"):
        indirizzi._esegui([YOUTUBE])
    Processo.appeso = True
    with pytest.raises(indirizzi.ErroreIndirizzo, match="60 secondi"):
        indirizzi._esegui([YOUTUBE])
    assert not indirizzi._processi


def _zip_di_ytdlp(versione):
    dati = io.BytesIO()
    with zipfile.ZipFile(dati, "w") as archivio:
        archivio.writestr("yt-dlp.exe", f"yt-dlp {versione}")
        archivio.writestr("_internal/base_library.zip", "librerie")
    return dati.getvalue()


def _github_finto(monkeypatch, versione, guasto=False):
    zip_ = _zip_di_ytdlp(versione)
    impronta = "0" * 64 if guasto else hashlib.sha256(zip_).hexdigest()
    file = {indirizzi.YTDLP_RELEASE.format(versione=versione) + indirizzi.YTDLP_IMPRONTE: f"{impronta}  {indirizzi.YTDLP_ZIP}\nabc  altro.zip\n".encode(),
        indirizzi.YTDLP_RELEASE.format(versione=versione) + indirizzi.YTDLP_ZIP: zip_}
    scaricati = []

    def scarica(url, avanza=None):
        scaricati.append(url)
        return file[url]

    monkeypatch.setattr(indirizzi, "_scarica", scarica)
    monkeypatch.setattr(indirizzi, "ultima_versione", lambda: versione)
    return scaricati


def test_yt_dlp_si_installa_e_si_aggiorna(monkeypatch):
    _github_finto(monkeypatch, "2026.10.26")
    assert indirizzi.installa_ytdlp() == "2026.10.26"
    assert indirizzi.ytdlp_presente() and indirizzi.versione_di_ytdlp() == "2026.10.26"
    assert os.path.isfile(os.path.join(indirizzi.cartella_di_ytdlp(), "_internal", "base_library.zip"))
    assert componenti.YT_DLP.presente() and componenti.YT_DLP.versione() == "2026.10.26"
    # La stessa versione non si riscarica.
    scaricati = _github_finto(monkeypatch, "2026.10.26")
    assert indirizzi.aggiorna_ytdlp() is None and not scaricati
    # Una versione nuova prende il posto della vecchia, senza avanzi.
    _github_finto(monkeypatch, "2026.11.03")
    assert componenti.YT_DLP.aggiorna() == "2026.11.03"
    with open(indirizzi.eseguibile_di_ytdlp(), encoding="utf-8") as f:
        assert f.read() == "yt-dlp 2026.11.03"
    assert not os.path.exists(indirizzi.cartella_di_ytdlp() + ".nuova") and not os.path.exists(indirizzi.cartella_di_ytdlp() + ".vecchia")
    # Uno zip che non e' quello della release non si installa, e il vecchio resta.
    _github_finto(monkeypatch, "2026.11.04", guasto=True)
    with pytest.raises(OSError, match="non è quello atteso"):
        indirizzi.aggiorna_ytdlp()
    assert indirizzi.versione_di_ytdlp() == "2026.11.03"
    componenti.YT_DLP.togli()
    assert not componenti.YT_DLP.presente() and componenti.YT_DLP.versione() is None


def test_quickjs_si_installa_con_la_sua_impronta(monkeypatch):
    monkeypatch.setattr(indirizzi, "_scarica", lambda url, avanza=None: b"qjs finto")
    with pytest.raises(OSError, match="non è quello atteso"):
        componenti.QUICKJS.installa()
    assert not componenti.QUICKJS.presente()
    monkeypatch.setattr(indirizzi, "QUICKJS_SHA256", hashlib.sha256(b"qjs finto").hexdigest())
    componenti.QUICKJS.installa()
    assert componenti.QUICKJS.presente() and os.path.basename(indirizzi.eseguibile_di_quickjs()) == "qjs.exe"
    componenti.QUICKJS.togli()
    assert not componenti.QUICKJS.presente() and not os.path.exists(indirizzi.cartella_di_quickjs())


def test_i_brani_e_l_archivio_degli_indirizzi(tmp_path):
    brano = Brano(YOUTUBE, titolo="Me at the zoo")
    assert brano.nome == brano.nome_del_file == "Me at the zoo" and Brano(YOUTUBE).nome_del_file == YOUTUBE
    assert brano.come_dati() == {"percorso": YOUTUBE, "saltato": False, "titolo": "Me at the zoo"}
    assert Brano.da_dati(brano.come_dati()).titolo == "Me at the zoo" and Brano(r"C:\a.mp3").come_dati() == {"percorso": r"C:\a.mp3", "saltato": False}
    copia = brano.copia()
    assert copia is not brano and copia.titolo == "Me at the zoo" and Brano(r"C:\a.sid", sottobrano=2).copia(3).sottobrano == 3
    archivio = Archivio(str(tmp_path / "Playlist.json"))
    archivio.carica()
    archivio.metti_l_indirizzo(brano)
    archivio.metti_l_indirizzo(Brano("https://x.it/due", titolo="Due"))
    # Lo stesso indirizzo riaperto sale in cima con il titolo nuovo, senza doppioni.
    tornato = archivio.metti_l_indirizzo(Brano(YOUTUBE, titolo="Allo zoo"))
    assert tornato is brano and [b.titolo for b in archivio.indirizzi.brani] == ["Allo zoo", "Due"]
    album = archivio.metti_la_playlist_in_rete(Playlist("Album", [Brano("https://x.it/t1", titolo="Uno")], indirizzo=ALBUM))
    archivio.metti_la_playlist_in_rete(Playlist("Altro", [], indirizzo="https://x.it/altro"))
    riletto = archivio.metti_la_playlist_in_rete(Playlist("Album nuovo", [Brano("https://x.it/t1", titolo="Uno")], indirizzo=ALBUM))
    assert [p.nome for p in archivio.in_rete] == ["Album nuovo", "Altro"] and archivio.in_rete_da(ALBUM) is riletto is not album
    archivio.salva()
    di_nuovo = Archivio(archivio.percorso)
    di_nuovo.carica()
    assert [b.come_dati() for b in di_nuovo.indirizzi.brani] == [b.come_dati() for b in archivio.indirizzi.brani]
    assert [(p.nome, p.indirizzo, [b.titolo for b in p.brani]) for p in di_nuovo.in_rete] == [("Album nuovo", ALBUM, ["Uno"]), ("Altro", "https://x.it/altro", [])]
    di_nuovo.elimina(di_nuovo.in_rete[0])
    assert [p.nome for p in di_nuovo.in_rete] == ["Altro"]
    # Senza indirizzi il file resta com'era prima della 3.2.0.
    vuoto = Archivio(str(tmp_path / "Vuoto.json"))
    vuoto.salva()
    with open(vuoto.percorso, encoding="utf-8") as f:
        assert "indirizzi" not in json.load(f)


def test_schedario_pulizia_filtro_e_statistiche_degli_indirizzi(tmp_path):
    schedario = Schedario(str(tmp_path / "Schedario.json"))
    assert schedario.chiedi([YOUTUBE]) == 0
    schedario.metti_la_scheda(YOUTUBE, indirizzi.scheda_dell_info(INFO_YOUTUBE))
    schedario.metti_la_scheda("https://x.it/senza", indirizzi.scheda_della_voce("Senza durata", None))
    assert schedario.durata(Brano(YOUTUBE)) == 19.0
    schedario.salva()
    di_nuovo = Schedario(schedario.percorso)
    di_nuovo.carica()
    # La scheda con la durata resta; quella senza si rifa' quando il brano si apre.
    assert di_nuovo.scheda(YOUTUBE)["tag"]["titolo"] == "Me at the zoo" and di_nuovo.scheda("https://x.it/senza") is None
    assert pulizia.norm(YOUTUBE) == YOUTUBE and pulizia.norm(r"C:\Musica\A.MP3") == os.path.normcase(r"C:\Musica\A.MP3")
    testo = filtro.dove_cercare(Brano(YOUTUBE, titolo="Me at the zoo"), None)
    assert "me at the zoo" in testo and "youtube" in testo
    dati = statistiche.Statistiche(str(tmp_path / "Statistiche.json"))
    assert dati._formato_di(YOUTUBE) is dati.dati["formati"][statistiche.DAI_SITI] and statistiche.estensione_da_dire(statistiche.DAI_SITI) == "dai siti"


def test_il_segnalibro_e_la_data_del_controllo_nelle_impostazioni(tmp_path):
    segno = {"percorso": YOUTUBE, "posizione": 5.0, "durata": 19.0, "sottobrano": None, "lista": "in_rete", "nome": ALBUM, "indice": 0,
        "titolo": "Me at the zoo", "titolo_della_lista": "Album"}
    assert impostazioni._segnalibro_valido(segno) and impostazioni._segnalibro_valido({**segno, "lista": "indirizzi", "nome": ""})
    assert not impostazioni._segnalibro_valido({**segno, "nome": ""}) and not impostazioni._segnalibro_valido({**segno, "titolo": 3})
    assert not impostazioni._segnalibro_valido({**segno, "altro": 1})
    controllo = impostazioni.CONTROLLI["ytdlp_controllato"]
    assert controllo("") and controllo("2026-11-05") and not controllo("5 novembre") and not controllo("2026-1105xx")


def test_il_motore_apre_il_flusso_con_le_sue_liste():
    indirizzi._tieni(YOUTUBE, False, indirizzi.flusso_dell_info(VIDEO))
    brano = motore._Brano(YOUTUBE, inizio=12.5)
    assert brano.indirizzo == "https://video.example/v.mp4" and brano.audio == ("https://video.example/a.webm",) and brano.intestazioni == ("Accept: */*",)
    assert brano.opzioni == {"start": "12.500"} and brano.sottobrano is None
    comandi = []
    finto = types.SimpleNamespace(liste_scritte={}, comando=lambda *argomenti: comandi.append(argomenti))
    motore._Lettore._metti_le_liste(finto, brano)
    assert comandi == [("change-list", "http-header-fields", "clr", ""), ("change-list", "http-header-fields", "append", "Accept: */*"),
        ("change-list", "audio-files", "clr", ""), ("change-list", "audio-files", "append", "https://video.example/a.webm")]
    # Il brano dopo, un file, svuota le liste; quello dopo ancora non tocca niente.
    comandi.clear()
    motore._Lettore._metti_le_liste(finto, motore._Brano(r"C:\a.mp3"))
    assert comandi == [("change-list", "http-header-fields", "clr", ""), ("change-list", "audio-files", "clr", "")]
    comandi.clear()
    motore._Lettore._metti_le_liste(finto, motore._Brano(r"C:\b.mp3"))
    assert comandi == []
    # Un indirizzo senza flusso tenuto va a libmpv com'e'.
    assert motore._Brano("https://x.it/pagina").indirizzo == "https://x.it/pagina"


# Gli indirizzi nella finestra.


@pytest.fixture
def con_ytdlp(finestra, monkeypatch):
    """yt-dlp installato per finta, il controllo di oggi gia' fatto, il lavoro
    in disparte e wx.CallAfter subito, e il motore che annota cosa suonerebbe."""
    import finestra as modulo

    os.makedirs(indirizzi.cartella_di_ytdlp())
    open(indirizzi.eseguibile_di_ytdlp(), "wb").close()
    finestra.impostazioni["ytdlp_controllato"] = datetime.date.today().isoformat()
    monkeypatch.setattr(modulo, "indirizzi_in_disparte", lambda lavoro, al_termine: al_termine(lavoro()))
    monkeypatch.setattr(modulo, "midi_in_disparte", lambda lavoro, al_termine: al_termine(lavoro()))
    monkeypatch.setattr(modulo.wx, "CallAfter", lambda funzione, *argomenti, **chiavi: funzione(*argomenti, **chiavi))
    monkeypatch.setattr(modulo.wx, "CallLater", lambda _ms, funzione, *argomenti: funzione(*argomenti))
    suonati = []
    monkeypatch.setattr(finestra.motore, "suona", lambda percorso, sottobrano=None, inizio=None, in_pausa=False, sfuma_lo_stesso=False, a_volume_pieno=False:
        suonati.append((percorso, inizio, in_pausa)))
    return suonati


def _appunti(finestra, monkeypatch, testo):
    monkeypatch.setattr(type(finestra), "_testo_degli_appunti", staticmethod(lambda: testo))


def _ultime(finestra, n=3):
    return [r.rsplit(" ", 1)[0] for r in finestra._righe[-n:]]


def test_ctrl_con_v_apre_l_indirizzo_degli_appunti_e_lo_suona(finestra, con_ytdlp, monkeypatch, suoni_annotati):
    from test_finestra import _premi

    _risposte(monkeypatch, {YOUTUBE: INFO_YOUTUBE})
    _appunti(finestra, monkeypatch, f"guarda {YOUTUBE}")
    _premi(finestra, "v", ctrl=True)
    assert con_ytdlp == [(YOUTUBE, None, False)]
    brano = finestra.archivio.indirizzi.brani[0]
    assert brano.titolo == "Me at the zoo" and finestra.coda.corrente is brano and finestra.coda.playlist is finestra.archivio.indirizzi
    assert any("Apro un indirizzo di youtube.com" in r for r in finestra._righe)
    assert any("In riproduzione: Me at the zoo, da youtube.com" in r for r in finestra._righe)
    assert finestra.schedario.scheda(YOUTUBE)["durata"] == 19.0 and "play" in suoni_annotati
    # Il ramo Indirizzi ha il brano, con i capitoli del sito da aprire.
    voci = list(finestra._figli(finestra.nodo_indirizzi))
    assert len(voci) == 1 and finestra.albero.GetItemText(voci[0]).startswith("Me at the zoo")
    assert finestra.albero.ItemHasChildren(voci[0])
    with open(finestra.archivio.percorso, encoding="utf-8") as f:
        assert json.load(f)["indirizzi"]["brani"][0]["titolo"] == "Me at the zoo"
    assert finestra._statistiche.dati["conti"]["indirizzi_aperti"] == 1


def test_senza_indirizzo_negli_appunti_si_chiede(finestra, con_ytdlp, monkeypatch):
    import finestra as modulo

    _risposte(monkeypatch, {"https://www.raiplaysound.it/audio/x.html": {"title": "Il Ruggito", "duration": 5685, "url": "https://x.it/r.mp3",
        "protocol": "https"}})
    _appunti(finestra, monkeypatch, "niente")
    scritti = iter(["www.raiplaysound.it/audio/x.html", "parola", ""])

    class Campo:
        def __init__(self, *argomenti):
            self.valore = next(scritti)

        def __enter__(self):
            return self

        def __exit__(self, *argomenti):
            return False

        def ShowModal(self):
            return modulo.wx.ID_OK

        def GetValue(self):
            return self.valore

    monkeypatch.setattr(modulo, "DialogoTesto", Campo)
    finestra._comando_apri_un_indirizzo()
    assert con_ytdlp == [("https://www.raiplaysound.it/audio/x.html", None, False)]
    finestra._comando_apri_un_indirizzo()
    assert "parola non è un indirizzo" in finestra._righe[-1]
    finestra._comando_apri_un_indirizzo()
    assert "Nessun indirizzo aperto." in finestra._righe[-1]


def test_una_playlist_di_un_sito_diventa_un_ramo_degli_indirizzi(finestra, con_ytdlp, monkeypatch):
    chiamate = []
    _risposte(monkeypatch, {ALBUM: INFO_ALBUM, "https://blazo.bandcamp.com/track/intro": INFO_INTRO, "https://blazo.bandcamp.com/track/due": INFO_DUE},
        chiamate)
    finestra._apri_l_indirizzo(ALBUM)
    pl = finestra.archivio.in_rete_da(ALBUM)
    assert [b.titolo for b in pl.brani] == ["Intro", "Due"] and pl.nome == "Jazz Format Mixtape vol.1"
    # Suona dal primo, il cui flusso si chiede prima; e intanto si chiede quello del seguente.
    assert con_ytdlp == [("https://blazo.bandcamp.com/track/intro", None, False)]
    assert [c[-1] for c in chiamate] == [ALBUM, "https://blazo.bandcamp.com/track/intro", "https://blazo.bandcamp.com/track/due"]
    assert indirizzi.pronto("https://blazo.bandcamp.com/track/due") is not None
    assert any("Negli Indirizzi la playlist Jazz Format Mixtape vol.1, da blazo.bandcamp.com: 2 brani." in r for r in finestra._righe)
    # La durata della playlist del sito si sa prima di aprire il brano.
    assert finestra.schedario.durata(pl.brani[1]) == 120.5
    nodo = finestra._nodo_della_playlist(pl)
    assert nodo is not None and finestra.albero.GetItemParent(nodo) == finestra.nodo_indirizzi
    assert finestra.albero.GetItemText(finestra.nodo_indirizzi).startswith("Indirizzi, 1 playlist")
    # Il seguente parte senza chiedere niente a yt-dlp.
    finestra._suona(pl, pl.brani[1], "brano_seguente_da_solo")
    assert con_ytdlp[-1][0] == "https://blazo.bandcamp.com/track/due" and len(chiamate) == 3
    # Rileggi dal sito: la playlist prende il posto di quella di prima, e non suona.
    finestra._apri_l_indirizzo(ALBUM, suona=False)
    assert finestra.archivio.in_rete_da(ALBUM) is not pl and len(con_ytdlp) == 2 and "Riletta dal sito" in finestra._righe[-1]
    # Canc la toglie, dopo la conferma.
    monkeypatch.setattr(finestra, "_conferma", lambda *argomenti: True)
    finestra._cancella(finestra._nodo_della_playlist(finestra.archivio.in_rete_da(ALBUM)))
    assert finestra.archivio.in_rete == [] and "Tolta dagli Indirizzi" in finestra._righe[-1]


def test_un_indirizzo_che_non_si_apre(finestra, con_ytdlp, monkeypatch, suoni_annotati):
    _risposte(monkeypatch, {YOUTUBE: "Video unavailable"})
    finestra._apri_l_indirizzo(YOUTUBE)
    assert finestra._righe[-1].startswith("L'indirizzo di youtube.com non si apre: Video unavailable.") and suoni_annotati[-1] == "errore"
    assert con_ytdlp == [] and finestra.archivio.indirizzi.brani == []
    # Un brano gia' negli Indirizzi che non si apre piu' lo dice, e non suona.
    brano = finestra.archivio.metti_l_indirizzo(Brano(YOUTUBE, titolo="Me at the zoo"))
    finestra._suona(finestra.archivio.indirizzi, brano)
    assert finestra._righe[-1].startswith("Me at the zoo non si apre: Video unavailable.") and con_ytdlp == []


def test_l_errore_del_motore_richiede_il_flusso_una_volta(finestra, con_ytdlp, monkeypatch):
    chiamate = []
    _risposte(monkeypatch, {YOUTUBE: INFO_YOUTUBE}, chiamate)
    brano = finestra.archivio.metti_l_indirizzo(Brano(YOUTUBE, titolo="Me at the zoo"))
    finestra._suona(finestra.archivio.indirizzi, brano)
    assert len(chiamate) == 1 and len(con_ytdlp) == 1
    # Il flusso tenuto non si apre: si richiede al sito e si riprova.
    finestra._brano_in_errore(YOUTUBE)
    assert len(chiamate) == 2 and len(con_ytdlp) == 2
    # La seconda volta e' un errore vero.
    finestra._brano_in_errore(YOUTUBE)
    assert "Non riesco a suonare Me at the zoo." in "".join(finestra._righe[-3:]) and len(con_ytdlp) == 2


def test_lo_stop_ferma_l_attesa_del_flusso(finestra, con_ytdlp, monkeypatch):
    import finestra as modulo

    _risposte(monkeypatch, {YOUTUBE: INFO_YOUTUBE})
    in_attesa = []
    monkeypatch.setattr(modulo, "indirizzi_in_disparte", lambda lavoro, al_termine: in_attesa.append((lavoro, al_termine)))
    brano = finestra.archivio.metti_l_indirizzo(Brano(YOUTUBE, titolo="Me at the zoo"))
    finestra._suona(finestra.archivio.indirizzi, brano)
    finestra._comando_stop()
    assert "Stop: l'indirizzo non suona." in finestra._righe[-1]
    lavoro, al_termine = in_attesa[0]
    al_termine(lavoro())
    assert con_ytdlp == []


def test_senza_yt_dlp_si_propone_di_scaricarlo(finestra, monkeypatch):
    import finestra as modulo

    monkeypatch.setattr(modulo, "indirizzi_in_disparte", lambda lavoro, al_termine: al_termine(lavoro()))
    monkeypatch.setattr(modulo, "midi_in_disparte", lambda lavoro, al_termine: al_termine(lavoro()))
    monkeypatch.setattr(modulo.wx, "CallAfter", lambda funzione, *argomenti, **chiavi: funzione(*argomenti, **chiavi))
    monkeypatch.setattr(modulo.wx, "CallLater", lambda _ms, funzione, *argomenti: funzione(*argomenti))
    domande = []
    risposta = [False]
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, *argomenti: domande.append(domanda) or risposta[0])
    finestra._apri_l_indirizzo(YOUTUBE)
    assert "serve yt-dlp, e per YouTube anche QuickJS" in domande[-1] and "Senza yt-dlp gli indirizzi" in finestra._righe[-1]
    # Con il si' si scaricano tutti e due, e poi l'indirizzo si apre.
    installati = []
    monkeypatch.setattr(componenti.YT_DLP, "installa", lambda avanza=None: installati.append("yt-dlp") or os.makedirs(indirizzi.cartella_di_ytdlp())
        or open(indirizzi.eseguibile_di_ytdlp(), "wb").close())
    monkeypatch.setattr(componenti.QUICKJS, "installa", lambda avanza=None: installati.append("quickjs"))
    _risposte(monkeypatch, {YOUTUBE: INFO_YOUTUBE})
    suonati = []
    monkeypatch.setattr(finestra.motore, "suona", lambda percorso, *argomenti, **chiavi: suonati.append(percorso))
    risposta[0] = True
    finestra.impostazioni["ytdlp_controllato"] = datetime.date.today().isoformat()
    finestra._apri_l_indirizzo(YOUTUBE)
    assert installati == ["yt-dlp", "quickjs"] and suonati == [YOUTUBE]


def test_il_controllo_di_yt_dlp_una_volta_al_giorno(finestra, con_ytdlp, monkeypatch, suoni_annotati):
    controlli = []
    monkeypatch.setattr(indirizzi, "aggiorna_ytdlp", lambda avanza=None: controlli.append(True) or "2026.11.03")
    finestra.impostazioni["ytdlp_controllato"] = "2026-11-04"
    finestra._controlla_ytdlp()
    assert controlli == [True] and finestra._righe[-1].startswith("yt-dlp aggiornato alla versione 2026.11.03.")
    assert finestra.impostazioni["ytdlp_controllato"] == datetime.date.today().isoformat() and suoni_annotati[-1] == "scaricamento_finito"
    finestra._controlla_ytdlp()
    assert controlli == [True]
    # Un errore si dice nella console, senza fermare niente.
    finestra.impostazioni["ytdlp_controllato"] = ""
    monkeypatch.setattr(indirizzi, "aggiorna_ytdlp", lambda avanza=None: (_ for _ in ()).throw(OSError("rete assente")))
    finestra._controlla_ytdlp()
    assert finestra._righe[-1].startswith("yt-dlp non si aggiorna: rete assente")


def test_i_menu_e_le_copie_degli_indirizzi(finestra, con_ytdlp, monkeypatch):
    _risposte(monkeypatch, {YOUTUBE: INFO_YOUTUBE})
    finestra._apri_l_indirizzo(YOUTUBE)
    brano = finestra.archivio.indirizzi.brani[0]
    voci = [etichetta for etichetta, _azione in finestra._voci_del_menu({"tipo": "brano", "playlist": finestra.archivio.indirizzi, "brano": brano})]
    assert voci == ["Riproduci", "Sposta su", "Sposta giù", "Sposta in cima", "Sposta in fondo", "Saltato", "Togli dalla playlist", "Aggiungi alla playlist",
        "Aggiungi ai preferiti", "Copia l'indirizzo", "Apri un indirizzo"]
    voci = [etichetta for etichetta, _azione in finestra._voci_del_menu({"tipo": "playlist", "playlist": finestra.archivio.indirizzi})]
    assert voci[:2] == ["Riproduci", "Apri un indirizzo"] and "Rinomina" not in voci and "Elimina" not in voci
    finestra.archivio.in_rete.append(Playlist("Album", indirizzo=ALBUM))
    voci = [etichetta for etichetta, _azione in finestra._voci_del_menu({"tipo": "playlist", "playlist": finestra.archivio.in_rete[0]})]
    assert voci[:3] == ["Riproduci", "Rileggi dal sito", "Copia l'indirizzo"] and "Elimina" in voci
    # F4 e Aggiungi alla playlist tengono il titolo.
    finestra._ai_preferiti(brano)
    assert finestra.archivio.preferiti.brani[0].titolo == "Me at the zoo" and finestra.archivio.preferiti.brani[0] is not brano
    finestra._aggiungi(None, [brano.copia()], nome="Dal sito")
    assert finestra.archivio.playlist[-1].brani[0].titolo == "Me at the zoo"
    # La ricerca trova il titolo negli Indirizzi.
    assert (brano, "Indirizzi") in finestra._brani_degli_indirizzi()


def test_il_segnalibro_e_la_ripresa_di_un_indirizzo(finestra, con_ytdlp, monkeypatch):
    _risposte(monkeypatch, {YOUTUBE: INFO_YOUTUBE})
    finestra._apri_l_indirizzo(YOUTUBE)
    brano = finestra.archivio.indirizzi.brani[0]
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda self: YOUTUBE))
    monkeypatch.setattr(type(finestra.motore), "posizione", property(lambda self: 7.0))
    finestra._comando_metti_il_segnalibro()
    segno = finestra.impostazioni["segnalibro"]
    assert segno["lista"] == "indirizzi" and segno["titolo"] == "Me at the zoo" and "Me at the zoo, a 0:07" in finestra._righe[-1]
    assert finestra._dove_sta_il_segnalibro(segno)[:2] == (finestra.archivio.indirizzi, brano)
    stato = finestra._stato_da_riprendere()
    assert stato["tipo"] == "indirizzi" and stato["percorso"] == YOUTUBE
    # Alla riapertura il flusso si richiede, e il brano va in pausa al suo punto.
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda self: None))
    indirizzi.dimentica(YOUTUBE)
    finestra.impostazioni["ripresa"] = {**stato, "posizione": 7.0}
    finestra.riprendi()
    assert con_ytdlp[-1] == (YOUTUBE, 7.0, True) and finestra.coda.corrente is brano
