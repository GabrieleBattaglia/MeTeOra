# MeTeOra, le prove delle radio in rete: radio-browser finto, niente rete.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 06/11/2026: nasce con la 3.3.0, tappa 19 c del piano, issue 40. Nella 3.8.2 il sottoramo Recenti. Nella 3.10.0 Mostra altre radio.

import datetime
import json
import os
import threading
import types

import pytest

import importazione
import indirizzi
import motore
import radio
import statistiche
from playlist import RADIO_RECENTI, Archivio, Brano, Playlist

# La domanda vera a radio-browser, presa prima che il conftest la sostituisca.
_CHIEDI_VERO = radio._chiedi
RAI3 = {"stationuuid": "uuid-rai3", "name": "Rai  Radio 3", "url": "http://x/3.pls", "url_resolved": "http://icestreaming.rai.it/3.mp3", "countrycode": "it",
    "codec": "MP3", "bitrate": 320, "tags": "classical, culture,public radio", "language": "italian", "hls": 0}
DEEJAY = {"stationuuid": "uuid-deejay", "name": "Radio Deejay", "url_resolved": "https://x.msvdn.net/radiodeejay/master.m3u8", "countrycode": "IT",
    "codec": "UNKNOWN", "bitrate": 0, "tags": "", "hls": 1}


def _radio_browser(monkeypatch, risposte, chieste=None):
    """radio-browser finto: risponde dalla tabella per il percorso, o con
    l'errore se la voce e' un testo."""
    def chiedi(percorso, **parametri):
        if chieste is not None:
            chieste.append((percorso, parametri))
        risposta = risposte[percorso]
        if isinstance(risposta, str):
            raise radio.ErroreRadio(risposta)
        return json.loads(json.dumps(risposta))

    monkeypatch.setattr(radio, "_chiedi", chiedi)


# Le radio, senza finestra.


def test_le_stazioni_di_radio_browser():
    rai3, deejay = radio._stazioni([RAI3, DEEJAY, {**RAI3, "name": "doppione"}, {"stationuuid": "senza"}, {"stationuuid": "x", "url": "ftp://x/y"}, "rotta"])
    assert (rai3.uuid, rai3.nome, rai3.indirizzo, rai3.paese, rai3.codec, rai3.bitrate) == ("uuid-rai3", "Rai Radio 3", "http://icestreaming.rai.it/3.mp3", "IT", "MP3", 320)
    assert rai3.generi == "classical, culture, public radio" and deejay.codec == "" and deejay.bitrate == 0
    brano = rai3.come_brano()
    assert brano.percorso == "http://icestreaming.rai.it/3.mp3" and brano.titolo == "Rai Radio 3"
    assert brano.radio == {"uuid": "uuid-rai3", "paese": "IT", "codec": "MP3", "bitrate": 320, "generi": "classical, culture, public radio"}
    assert deejay.come_brano().radio == {"uuid": "uuid-deejay", "paese": "IT"}


def test_i_server_e_la_domanda_che_passa_al_seguente(monkeypatch):
    letti = []

    def leggi(url):
        letti.append(url)
        if url == radio.ELENCO_DEI_SERVER:
            return [{"name": "uno.api.radio-browser.info"}, {"name": "due.api.radio-browser.info"}, {"name": "uno.api.radio-browser.info"}]
        if url.startswith("https://uno."):
            raise OSError("spento")
        return [RAI3]

    monkeypatch.setattr(radio, "_leggi", leggi)
    monkeypatch.setattr(radio, "_chiedi", _CHIEDI_VERO)
    assert radio.server() == ["uno.api.radio-browser.info", "due.api.radio-browser.info"]
    assert [s.uuid for s in radio.cerca("rai tre")] == ["uuid-rai3"]
    assert letti[-1].startswith("https://due.api.radio-browser.info/json/stations/search?") and "name=rai+tre" in letti[-1] and "hidebroken=true" in letti[-1]
    assert "order=clickcount" in letti[-1] and "reverse=true" in letti[-1] and f"limit={radio.RADIO_PER_GRUPPO}" in letti[-1]
    # Senza elenco dei server valgono quelli di riserva; se nessuno risponde, un errore da dire.
    monkeypatch.setattr(radio, "_server", [])
    monkeypatch.setattr(radio, "_leggi", lambda url: (_ for _ in ()).throw(OSError("rete assente")))
    assert radio.server() == list(radio.SERVER_DI_RISERVA)
    with pytest.raises(radio.ErroreRadio, match="radio-browser non risponde: rete assente"):
        radio.paesi()
    # Il clic non si lamenta mai.
    radio.clic("uuid-rai3")
    assert radio._intestazioni()["User-Agent"].startswith("MeTeOra/")


def test_paesi_generi_e_lingue(monkeypatch):
    _radio_browser(monkeypatch, {
        "/json/countries": [{"name": "Germany", "iso_3166_1": "DE", "stationcount": 6309}, {"name": "Italy", "iso_3166_1": "IT", "stationcount": 1803},
            {"name": "Austria", "iso_3166_1": "AT", "stationcount": 500}, {"name": "Nessuna", "iso_3166_1": "XX", "stationcount": 0}, {"name": "?", "iso_3166_1": ""}],
        "/json/tags": [{"name": "pop", "stationcount": 6193}, {"name": "jazz", "stationcount": 1277}, {"name": "", "stationcount": 3}],
        "/json/languages": [{"name": "english", "iso_639": "en", "stationcount": 12686}, {"name": "klingon", "iso_639": None, "stationcount": 2}],
    })
    nomi = {"IT": "Italia", "DE": "Germania", "AT": "Austria"}
    monkeypatch.setattr(radio, "nome_del_paese", nomi.get)
    monkeypatch.setattr(radio, "paese_di_casa", lambda: "IT")
    # Il paese di Windows in cima, poi gli altri dalla A alla Z, con i nomi di Windows.
    assert radio.paesi() == [("IT", "Italia", 1803), ("AT", "Austria", 500), ("DE", "Germania", 6309)]
    assert radio.generi() == [("pop", 6193), ("jazz", 1277)]
    lingue = radio.lingue()
    assert lingue[0][0] == "english" and lingue[0][2] == 12686 and lingue[1] == ("klingon", "Klingon", 2)
    assert isinstance(radio.nome_del_paese("IT"), str) and radio.nome_del_paese("ZZ") is None


def test_i_brani_delle_radio_e_le_ascoltate(tmp_path):
    brano = Brano("http://icestreaming.rai.it/3.mp3", titolo="Rai Radio 3", radio={"uuid": "uuid-rai3", "paese": "IT", "bitrate": 320})
    dati = brano.come_dati()
    assert dati["radio"] == {"uuid": "uuid-rai3", "paese": "IT", "bitrate": 320} and "diretto" not in dati
    assert Brano.da_dati(dati).radio == brano.radio and Brano.da_dati({**dati, "radio": {"paese": "IT"}}).radio is None
    assert Brano.da_dati({**dati, "radio": {"uuid": "u", "bitrate": "tanti", "altro": 1}}).radio == {"uuid": "u"}
    copia = brano.copia()
    assert copia.radio == brano.radio and copia.radio is not brano.radio
    diretto = Brano("http://radio.example/flusso", titolo="Flusso", diretto=True)
    assert diretto.come_dati()["diretto"] is True and Brano.da_dati(diretto.come_dati()).diretto and diretto.copia().diretto
    archivio = Archivio(str(tmp_path / "Playlist.json"))
    archivio.carica()
    archivio.metti_la_radio(brano.copia())
    archivio.metti_la_radio(Brano("http://x/due", titolo="Due", radio={"uuid": "due"}))
    # La stessa radio con l'indirizzo nuovo sale in cima, una volta sola.
    tornata = archivio.metti_la_radio(Brano("http://nuovo.rai.it/3.mp3", titolo="Rai Radio 3", radio={"uuid": "uuid-rai3", "paese": "IT"}))
    assert [b.radio["uuid"] for b in archivio.radio.brani] == ["uuid-rai3", "due"] and tornata.percorso == "http://nuovo.rai.it/3.mp3"
    for n in range(RADIO_RECENTI + 5):
        archivio.metti_la_radio(Brano(f"http://x/{n}", titolo=str(n), radio={"uuid": str(n)}))
    assert len(archivio.radio.brani) == RADIO_RECENTI and archivio.radio.brani[0].titolo == str(RADIO_RECENTI + 4)
    archivio.salva()
    di_nuovo = Archivio(archivio.percorso)
    di_nuovo.carica()
    assert [b.come_dati() for b in di_nuovo.radio.brani] == [b.come_dati() for b in archivio.radio.brani]


def test_le_dirette_negli_indirizzi_e_nel_motore():
    indirizzi.metti_il_diretto("http://icestreaming.rai.it/3.mp3", dal_vivo=True)
    indirizzi.metti_il_diretto("http://radio.example/flusso")
    assert indirizzi.e_una_radio("http://icestreaming.rai.it/3.mp3") and not indirizzi.e_una_radio("http://radio.example/flusso")
    assert indirizzi.pronto("http://icestreaming.rai.it/3.mp3").dal_vivo and not indirizzi.pronto("http://radio.example/flusso").dal_vivo
    assert indirizzi.flusso_dell_info({"url": "https://x/live.m3u8", "is_live": True}).dal_vivo
    brano = motore._Brano("http://icestreaming.rai.it/3.mp3")
    assert brano.dal_vivo and brano.indirizzo == "http://icestreaming.rai.it/3.mp3"
    # La durata di una diretta non conta: libmpv la fa crescere con lei.
    finto = types.SimpleNamespace(dal_vivo=True, durata_vera=None, mpv=types.SimpleNamespace(time_pos=12.0, duration=15.0))
    assert motore._Lettore.leggi(finto) == (12.0, None)
    finto.dal_vivo = False
    assert motore._Lettore.leggi(finto) == (12.0, 15.0)
    assert statistiche.Statistiche._formato_di(types.SimpleNamespace(_formato=lambda chiave: chiave), "http://icestreaming.rai.it/3.mp3") == statistiche.DALLE_RADIO
    assert statistiche.estensione_da_dire(statistiche.DALLE_RADIO) == "dalle radio"


def test_il_titolo_in_onda_dai_metadati():
    arrivati = []
    lettore = types.SimpleNamespace(percorso="http://x/radio.mp3", titolo_in_onda=None)
    finto = types.SimpleNamespace(_blocco=threading.Lock(), _chiuso=False, _attivo=lettore, _al_titolo_in_onda=arrivati.append)
    motore.Motore._metadati(finto, lettore, "metadata", {"icy-name": "Radio", "icy-title": " Lucio Dalla - Caruso "})
    motore.Motore._metadati(finto, lettore, "metadata", {"icy-title": "Lucio Dalla - Caruso"})
    motore.Motore._metadati(finto, lettore, "metadata", {"ICY-TITLE": "Mina - Se telefonando"})
    motore.Motore._metadati(finto, lettore, "metadata", {"icy-title": ""})
    motore.Motore._metadati(finto, types.SimpleNamespace(percorso="x", titolo_in_onda=None), "metadata", {"icy-title": "di un altro lettore"})
    motore.Motore._metadati(finto, lettore, "metadata", None)
    assert arrivati == ["Lucio Dalla - Caruso", "Mina - Se telefonando"] and lettore.titolo_in_onda is None


def test_gli_indirizzi_dei_file_m3u_e_pls_si_tengono_con_il_titolo():
    m3u = b"#EXTM3U\n#EXTINF:-1,Rai Radio 3\nhttp://icestreaming.rai.it/3.mp3\n#EXTINF:-1,\nhttps://x/senza-titolo\nbrano.mp3\nrtsp://x/y\n"
    voci, _libgme = importazione.analizza(m3u, r"E:\Liste\Radio.m3u")
    assert [(v.percorso, v.motivo, v.titolo) for v in voci] == [("http://icestreaming.rai.it/3.mp3", None, "Rai Radio 3"), ("https://x/senza-titolo", None, None),
        (r"E:\Liste\brano.mp3", None, None), (None, "indirizzo", None)]
    pls = b"[playlist]\r\nFile2=http://b/2\r\nTitle1=Prima\r\nFile1=http://a/1\r\nTitle2=Seconda\r\nNumberOfEntries=2\r\n"
    voci, _libgme = importazione.analizza(pls, r"E:\Liste\Radio.pls")
    assert [(v.percorso, v.titolo) for v in voci] == [("http://a/1", "Prima"), ("http://b/2", "Seconda")]


# Le radio nella finestra.


@pytest.fixture
def con_le_radio(finestra, monkeypatch):
    """Il lavoro in disparte e wx.CallAfter subito, e il motore che annota
    cosa suonerebbe; il controllo di yt-dlp di oggi gia' fatto."""
    import finestra as modulo

    finestra.impostazioni["ytdlp_controllato"] = datetime.date.today().isoformat()
    for nome in ("radio_in_disparte", "indirizzi_in_disparte", "midi_in_disparte"):
        monkeypatch.setattr(modulo, nome, lambda lavoro, al_termine: al_termine(lavoro()))
    monkeypatch.setattr(modulo.wx, "CallAfter", lambda funzione, *argomenti, **chiavi: funzione(*argomenti, **chiavi))
    monkeypatch.setattr(modulo.wx, "CallLater", lambda _ms, funzione, *argomenti: funzione(*argomenti))
    suonati = []
    monkeypatch.setattr(finestra.motore, "suona", lambda percorso, sottobrano=None, inizio=None, in_pausa=False, sfuma_lo_stesso=False, a_volume_pieno=False:
        suonati.append((percorso, inizio, in_pausa)))
    monkeypatch.setattr(radio, "nome_del_paese", {"IT": "Italia", "DE": "Germania"}.get)
    monkeypatch.setattr(radio, "paese_di_casa", lambda: "IT")
    return suonati


def _figlio(finestra, voce, inizio):
    return next(v for v in finestra._figli(voce) if finestra.albero.GetItemText(v).startswith(inizio))


def _etichette(finestra, voce):
    return [finestra.albero.GetItemText(v) for v in finestra._figli(voce)]


def test_il_ramo_radio_per_paese_e_una_radio_che_suona(finestra, con_le_radio, monkeypatch):
    chieste = []
    _radio_browser(monkeypatch, {"/json/countries": [{"iso_3166_1": "DE", "stationcount": 6309}, {"iso_3166_1": "IT", "stationcount": 1803}],
        "/json/stations/search": [RAI3, DEEJAY], "/json/url/uuid-rai3": {"ok": True}}, chieste)
    finestra.albero.Expand(finestra.nodo_radio)
    assert _etichette(finestra, finestra.nodo_radio) == ["Per paese", "Per genere", "Per lingua"]
    paesi = _figlio(finestra, finestra.nodo_radio, "Per paese")
    finestra.albero.Expand(paesi)
    assert _etichette(finestra, paesi) == ["Italia, 1803 radio", "Germania, 6309 radio"]
    italia = _figlio(finestra, paesi, "Italia")
    finestra.albero.Expand(italia)
    assert chieste[-1][0] == "/json/stations/search" and chieste[-1][1]["countrycode"] == "IT"
    assert _etichette(finestra, italia) == ["Rai Radio 3, Italia, MP3 a 320 kbps", "Radio Deejay, Italia"]
    voce = _figlio(finestra, italia, "Rai Radio 3")
    dati = finestra._dati(voce)
    finestra._riproduci(dati["playlist"], dati["brano"])
    # La radio si apre senza yt-dlp, che qui non c'e', come diretta; fra le
    # ascoltate va dopo un minuto di fila (3.10.2), qui chiamato a mano.
    assert con_le_radio == [("http://icestreaming.rai.it/3.mp3", None, False)] and indirizzi.e_una_radio("http://icestreaming.rai.it/3.mp3")
    assert any("In riproduzione: Rai Radio 3, Italia, MP3 a 320 kbps" in r for r in finestra._righe)
    assert not finestra.archivio.radio.brani and chieste[-1] == ("/json/url/uuid-rai3", {})
    finestra._radio_tenuta(dati["playlist"], dati["brano"])
    assert [b.titolo for b in finestra.archivio.radio.brani] == ["Rai Radio 3"]
    assert finestra._statistiche.dati["conti"]["radio_ascoltate"] == 1
    with open(finestra.archivio.percorso, encoding="utf-8") as f:
        assert json.load(f)["radio"]["brani"][0]["radio"]["uuid"] == "uuid-rai3"
    # Il menu, F4 e Canc su una radio di radio-browser.
    voci = [etichetta for etichetta, _azione in finestra._voci_del_menu(dati)]
    assert voci == ["Riproduci", "Aggiungi alla playlist", "Aggiungi ai preferiti", "Copia l'indirizzo", "Cerca una radio"]
    finestra._ai_preferiti(dati["brano"])
    assert finestra.archivio.preferiti_in_rete.brani[0].radio["uuid"] == "uuid-rai3"
    finestra._cancella(voce)
    assert "Le radio di radio-browser non si tolgono" in finestra._righe[-1]
    # Riaperto, il ramo Radio ha in cima Recenti, con le ascoltate (3.8.2).
    finestra.albero.Collapse(finestra.nodo_radio)
    finestra.albero.Expand(finestra.nodo_radio)
    assert _etichette(finestra, finestra.nodo_radio) == ["Recenti, 1 radio", "Per paese", "Per genere", "Per lingua"]
    recenti = _figlio(finestra, finestra.nodo_radio, "Recenti, 1 radio")
    finestra.albero.Expand(recenti)
    assert _etichette(finestra, recenti) == ["Rai Radio 3, Italia, MP3 a 320 kbps"]
    finestra._seleziona(recenti)
    assert [e for e, _a in finestra._voci_del_menu(finestra._dati(recenti))] == ["Riproduci", "Cerca una radio"]
    assert finestra.righe_del_cruscotto()[0].startswith("Tasti per le radio recenti")
    recente = next(iter(finestra._figli(recenti)))
    voci = [etichetta for etichetta, _azione in finestra._voci_del_menu(finestra._dati(recente))]
    assert "Togli dalle ascoltate" in voci


def test_la_ricerca_di_una_radio_con_la_barra_rovesciata(finestra, con_le_radio, monkeypatch):
    from test_finestra import _premi

    import finestra as modulo

    _radio_browser(monkeypatch, {"/json/stations/search": [DEEJAY, RAI3]})
    scritti = iter(["deejay", ""])

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
    finestra._seleziona(finestra.nodo_radio)
    _premi(finestra, "\\")
    assert finestra._righe[-1].startswith("Trovate 2 radio con deejay nel nome.") and finestra._statistiche.dati["conti"]["radio_cercate"] == 1
    voce = finestra._voce_corrente()
    assert finestra.albero.GetItemText(voce) == "Ricerca di deejay, 2 radio" and finestra.albero.GetItemParent(voce) == finestra.nodo_radio
    assert _etichette(finestra, voce) == ["Radio Deejay, Italia", "Rai Radio 3, Italia, MP3 a 320 kbps"]
    # Una ricerca vuota non fa niente.
    finestra._cerca_una_radio()
    assert "Nessuna radio cercata." in finestra._righe[-1]


def test_radio_browser_che_non_risponde(finestra, con_le_radio, monkeypatch, suoni_annotati):
    _radio_browser(monkeypatch, {"/json/tags": "radio-browser non risponde: rete assente"})
    finestra.albero.Expand(finestra.nodo_radio)
    generi = _figlio(finestra, finestra.nodo_radio, "Per genere")
    finestra.albero.Expand(generi)
    assert finestra._righe[-1].startswith("radio-browser non risponde: rete assente. Riaprendo il ramo si riprova.") and suoni_annotati[-1] == "errore"
    assert finestra.albero.ItemHasChildren(generi) and finestra._dati(generi)["caricato"] is False
    _radio_browser(monkeypatch, {"/json/tags": [{"name": "jazz", "stationcount": 1277}]})
    finestra.albero.Expand(generi)
    assert _etichette(finestra, generi) == ["jazz, 1277 radio"] and finestra._dati(next(iter(finestra._figli(generi))))["filtro"] == {"tag": "jazz", "tagExact": "true"}


def test_il_titolo_in_onda_e_la_diretta_nella_finestra(finestra, con_le_radio, monkeypatch, sintesi_finta):
    import finestra as modulo

    # Le attese rimandate, come i blocchi del braille, restano da parte.
    monkeypatch.setattr(modulo.wx, "CallLater", lambda *argomenti: None)
    brano = Brano("http://icestreaming.rai.it/3.mp3", titolo="Rai Radio 3", radio={"uuid": "uuid-rai3", "paese": "IT"})
    finestra.archivio.metti_la_radio(brano)
    finestra._suona(finestra.archivio.radio, brano)
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda self: brano.percorso))
    monkeypatch.setattr(type(finestra.motore), "dal_vivo", property(lambda self: True))
    monkeypatch.setattr(type(finestra.motore), "titolo_in_onda", property(lambda self: "Lucio Dalla - Caruso"))
    monkeypatch.setattr(type(finestra.motore), "posizione", property(lambda self: 75.0))
    # Con D spento il titolo va solo nella console (issue 45, 3.8.0).
    finestra.impostazioni["sottotitoli"] = False
    finestra._titolo_in_onda("Lucio Dalla -  Caruso")
    assert finestra._righe[-1].startswith("In onda: Lucio Dalla - Caruso.") and ("nvda", "In onda: Lucio Dalla - Caruso.") not in sintesi_finta.detti
    finestra.impostazioni["sottotitoli"] = True
    finestra._titolo_in_onda("Lucio Dalla -  Caruso")
    assert finestra._righe[-1].startswith("In onda: Lucio Dalla - Caruso.") and ("nvda", "In onda: Lucio Dalla - Caruso.") in sintesi_finta.detti
    finestra._titolo_in_onda("Mina - Se telefonando")
    # La riga del titolo si riscrive, non se ne aggiunge un'altra.
    assert sum(1 for r in finestra._righe if r.startswith("In onda:")) == 1 and finestra._statistiche.dati["conti"]["titoli_in_onda"] == 3
    finestra._comando_avanti()
    assert "Rai Radio 3 è una diretta: non si salta." in finestra._righe[-1]
    finestra._comando_dove_sono()
    riga = next(r for r in reversed(finestra._righe) if "in diretta" in r)
    assert riga.startswith("1:15, in diretta") and "in onda Lucio Dalla - Caruso" in riga
    assert modulo.TASTI_DEL_CONTESTO["brano_radio"][0] == "una radio"


def test_una_playlist_m3u_di_radio_suona_senza_yt_dlp(finestra, con_le_radio, monkeypatch, tmp_path):
    from test_finestra import _file, _importazione_subito

    _importazione_subito(finestra, monkeypatch)
    m3u = _file(os.path.join(str(tmp_path), "Radio.m3u"), "#EXTM3U\n#EXTINF:-1,Rai Radio 3\nhttp://icestreaming.rai.it/3.mp3\n")
    finestra._importa_le_playlist([m3u])
    pl = finestra.archivio.playlist[-1]
    assert [(b.percorso, b.titolo, b.diretto) for b in pl.brani] == [("http://icestreaming.rai.it/3.mp3", "Rai Radio 3", True)]
    finestra._riproduci_playlist(pl)
    assert con_le_radio == [("http://icestreaming.rai.it/3.mp3", None, False)] and not indirizzi.ytdlp_presente()
    assert not indirizzi.e_una_radio("http://icestreaming.rai.it/3.mp3")


def test_mostra_altre_radio_in_fondo_alla_ricerca(finestra, con_le_radio, monkeypatch, suoni_annotati):
    # Mostra altre radio (3.10.0): la pagina seguente di radio-browser, in fondo al ramo.
    import types

    chieste = []

    def stazioni(limite=radio.RADIO_PER_GRUPPO, inizio=0, **filtro):
        chieste.append((inizio, filtro))
        pagina = radio.Pagina([radio.Stazione({"stationuuid": f"u{inizio + n}", "name": f"Radio {inizio + n}", "url": f"http://x/{inizio + n}.mp3"})
            for n in range(2 if inizio < 600 else 1)])
        pagina.piena = inizio < 600
        return pagina

    monkeypatch.setattr(radio, "stazioni", stazioni)
    monkeypatch.setattr(radio, "cerca", lambda testo, limite=radio.RADIO_PER_GRUPPO, inizio=0: stazioni(limite, inizio, name=testo))
    finestra._radio_trovate_per_nome("deejay", radio.cerca("deejay"))
    voce = next(v for v in finestra._figli(finestra.nodo_radio) if finestra.albero.GetItemText(v).startswith("Ricerca di deejay"))
    finestra.albero.Expand(voce)
    figli = list(finestra._figli(voce))
    assert [finestra.albero.GetItemText(v).split(",")[0] for v in figli] == ["Radio 0", "Radio 1", "Mostra altre radio"]
    finestra._seleziona(figli[-1])
    finestra._invio(types.SimpleNamespace(GetItem=finestra._voce_corrente))
    assert chieste[-1] == (300, {"name": "deejay"})
    figli = list(finestra._figli(voce))
    assert [finestra.albero.GetItemText(v).split(",")[0] for v in figli] == ["Radio 0", "Radio 1", "Radio 300", "Radio 301", "Mostra altre radio"]
    assert finestra._voce_corrente() == figli[2] and "Altre 2 radio in deejay: ora sono 4." in finestra._righe[-1]
    # La pagina da 600 non e' piena: la voce sparisce, e sull'ultima radio non chiede piu' niente.
    finestra._altre_radio(finestra._dati(figli[-1]))
    assert chieste[-1][0] == 600 and "Mostra altre radio" not in [finestra.albero.GetItemText(v) for v in finestra._figli(voce)]
    finestra._altre_radio(finestra._dati(list(finestra._figli(voce))[-1]))
    assert len(chieste) == 3 and "si usa sulla sua voce" in finestra._righe[-1]
    assert finestra._statistiche.dati["conti"]["radio_altre"] == 2


def test_una_radio_entra_fra_le_recenti_dopo_un_minuto(finestra, con_le_radio, monkeypatch, suoni_annotati):
    # Il minuto di ascolto di fila anche per le radio (3.10.2).
    import types

    import finestra as modulo

    brano = Brano("http://icestreaming.rai.it/3.mp3", titolo="Rai Radio 3", radio={"uuid": "uuid-rai3", "paese": "IT"})
    gruppo = Playlist("Radio, Italia", [brano], cartella="")
    gruppo.radio_gruppo = True
    finestra._suona(gruppo, brano)
    assert not finestra.archivio.radio.brani
    finto = types.SimpleNamespace(in_corso=brano.percorso, posizione=0.0, in_pausa=False, volume=100)
    orologio = [100.0]
    monkeypatch.setattr(finestra, "motore", finto)
    # Lo scatto delle statistiche leggerebbe il motore vero.
    monkeypatch.setattr(finestra, "_scatto_delle_statistiche", lambda: None)
    monkeypatch.setattr(finestra, "coda", types.SimpleNamespace(playlist=gruppo, corrente=brano))
    monkeypatch.setattr(modulo.time, "monotonic", lambda: orologio[0])
    for _n in range(60):
        orologio[0] += 1.0
        finto.posizione += 1.0
        finestra._guarda_l_indirizzo()
    assert not finestra.archivio.radio.brani
    orologio[0] += 1.0
    finto.posizione += 1.0
    finestra._guarda_l_indirizzo()
    assert [b.radio["uuid"] for b in finestra.archivio.radio.brani] == ["uuid-rai3"]
    assert finestra._righe[-1].startswith("Rai Radio 3: un minuto di ascolto di fila, ora è fra le Recenti.") and suoni_annotati[-1] == "sorgente_tenuta"
    assert finestra._statistiche.dati["conti"]["radio_tenute"] == 1 and not finestra.archivio.indirizzi.brani
    monkeypatch.undo()
