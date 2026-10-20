# MeTeOra, le prove dell'importazione delle playlist di altri programmi: codifiche, righe M3U e PLS, percorsi, motivi e origine.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 20/10/2026: nasce con la 1.113.0.

"""Quasi tutto si prova sul testo, senza dischi: analizza riceve i byte e il
percorso della playlist. Solo leggi apre un file vero, in una cartella
visibile accanto al progetto, perche' le temporanee di Windows stanno sotto
AppData, che e' nascosta."""

import os
import tempfile
import threading

import pytest

import importazione
import pulizia

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYLIST = r"E:\Musica\Rock\Rock.m3u"


@pytest.fixture
def cartella():
    with tempfile.TemporaryDirectory(dir=RADICE) as radice:
        yield radice


def _voci(testo, percorso=PLAYLIST, codifica="utf-8"):
    voci, libgme = importazione.analizza(testo.encode(codifica), percorso)
    assert libgme is None
    return [(v.percorso, v.motivo) for v in voci]


def test_le_codifiche():
    citta = "Città.mp3\n"
    # Un M3U in UTF-8, con o senza BOM, e nella codifica di Windows se non lo e'.
    assert importazione.decodifica(citta.encode("utf-8"), ".m3u") == citta
    assert importazione.decodifica(b"\xef\xbb\xbf" + citta.encode("utf-8"), ".m3u") == citta
    assert importazione.decodifica(citta.encode("cp1252"), ".m3u") == citta
    assert importazione.decodifica(citta.encode("cp1252"), ".pls") == citta
    # Un M3U8 e' sempre UTF-8: un byte che non lo e' diventa il segno di sostituzione.
    assert importazione.decodifica(citta.encode("cp1252"), ".m3u8") == "Citt\ufffd.mp3\n"
    # La BOM UTF-16 vale per tutti, nei due ordini dei byte.
    for codifica in ("utf-16-le", "utf-16-be"):
        bom = "\ufeff".encode(codifica)
        assert importazione.decodifica(bom + citta.encode(codifica), ".m3u8") == citta


def test_le_righe_m3u_saltano_commenti_e_righe_vuote():
    testo = "#EXTM3U\r\n\r\n#EXTINF:123,Autore - Titolo\r\n  uno.mp3  \r\n#EXTGRP:Rock\r\n#PLAYLIST:Bella\ndue.flac\r\n"
    assert importazione.righe_m3u(testo) == ["uno.mp3", "due.flac"]


def test_le_voci_pls_vanno_nell_ordine_del_numero():
    testo = "[playlist]\nNumberOfEntries=3\nFile3=tre.mp3\nTitle3=Tre\nfile1=uno.mp3\nLength1=60\nFILE2 = due.mp3\nFile2=doppio.mp3\nFile4=\nVersion=2\n"
    assert importazione.righe_pls(testo) == ["uno.mp3", "due.mp3", "tre.mp3"]


def test_i_percorsi_relativi_assoluti_e_con_le_barre():
    voci = _voci("a.mp3\nsotto/b.flac\n..\\Pop\\c.ogg\n\\Altro\\d.mp3\nF:/Dischi/e.wav\n\\\\nas\\musica\\f.mp3\n\"G:\\Con spazi\\g.mp3\"\nH:h.mp3\n./i.mp3\n")
    assert voci == [
        (r"E:\Musica\Rock\a.mp3", None), (r"E:\Musica\Rock\sotto\b.flac", None), (r"E:\Musica\Pop\c.ogg", None), (r"E:\Altro\d.mp3", None),
        (r"F:\Dischi\e.wav", None), (r"\\nas\musica\f.mp3", None), (r"G:\Con spazi\g.mp3", None), (r"H:\h.mp3", None), (r"E:\Musica\Rock\i.mp3", None),
    ]
    # Una playlist in rete: la barra iniziale porta alla sua condivisione.
    assert _voci("x.mp3\n\\y.mp3\n", r"\\nas\musica\liste\Rock.m3u") == [(r"\\nas\musica\liste\x.mp3", None), (r"\\nas\musica\y.mp3", None)]


def test_gli_indirizzi_file_e_quelli_in_rete():
    voci = _voci("file:///E:/Musica/Citt%C3%A0%20mia.mp3\nfile:///C|/vecchio.mp3\nfile://localhost/D:/a.mp3\nfile://nas/musica/b.flac\n"
        "file:////nas/musica/c.ogg\nhttp://radio.example/flusso\nhttps://example.com/a.mp3\nrtsp://example.com/x\nmms://example.com/y\n")
    assert voci == [
        (r"E:\Musica\Città mia.mp3", None), (r"C:\vecchio.mp3", None), (r"D:\a.mp3", None), (r"\\nas\musica\b.flac", None), (r"\\nas\musica\c.ogg", None),
        (None, "indirizzo"), (None, "indirizzo"), (None, "indirizzo"), (None, "indirizzo"),
    ]
    # Con due barre sole la lettera non e' un server, e il cancelletto resta nel nome.
    assert _voci("file://C:/Musica/a.mp3\nfile://D|/b.mp3\nfile:///E:/Musica/Best #1.mp3\n") == [
        (r"C:\Musica\a.mp3", None), (r"D:\b.mp3", None), (r"E:\Musica\Best #1.mp3", None)]


def test_cartelle_playlist_formati_e_percorsi_non_validi():
    voci = _voci("Album/\nAlbum\nVol. 2\naltra.m3u8\nlista.PLS\ncopertina.jpg\nnote.txt\nbrutto|nome.mp3\nSID.SID\n")
    assert voci == [
        (r"E:\Musica\Rock\Album", "cartella"), (r"E:\Musica\Rock\Album", "cartella"), (r"E:\Musica\Rock\Vol. 2", "cartella"),
        (r"E:\Musica\Rock\altra.m3u8", "playlist"), (r"E:\Musica\Rock\lista.PLS", "playlist"), (r"E:\Musica\Rock\copertina.jpg", "formato"),
        (r"E:\Musica\Rock\note.txt", "formato"), (None, "non_valido"), (r"E:\Musica\Rock\SID.SID", None),
    ]


def test_un_pls_si_legge_dalle_voci_file():
    voci, libgme = importazione.analizza(b"[playlist]\r\nFile2=b.mp3\r\nFile1=a.mp3\r\nFile3=http://radio/x\r\n", r"E:\Liste\Radio.pls")
    assert libgme is None and [(v.scritta, v.percorso, v.motivo) for v in voci] == [
        ("a.mp3", r"E:\Liste\a.mp3", None), ("b.mp3", r"E:\Liste\b.mp3", None), ("http://radio/x", None, "indirizzo")]
    assert voci[2].leggibile == "http://radio/x" and voci[0].leggibile == r"E:\Liste\a.mp3"


def test_la_lista_di_libgme_non_si_importa():
    voci, libgme = importazione.analizza(b"# Gioco\r\ngioco.nsf::NSF,1,Titolo,2:30,,10\r\ngioco.nsf::NSF,2,Altro,1:00\r\n", r"E:\Console\gioco.m3u")
    assert voci == [] and libgme == "gioco.nsf"
    # Senza il nome del file vale quello della lista, con il tipo.
    assert importazione.analizza(b"::KSS,3\r\n", r"E:\Console\Gioco.m3u") == ([], "Gioco.kss")
    # Un indirizzo con i due punti doppi, come IPv6, non e' una riga di libgme.
    voci, libgme = importazione.analizza(b"http://[::1]:8000/flusso\r\n", r"E:\Liste\Radio.m3u")
    assert libgme is None and [v.motivo for v in voci] == ["indirizzo"]


def test_leggi_apre_il_file_e_ne_ricorda_l_origine(cartella):
    percorso = os.path.join(cartella, "Rock anni 80.m3u")
    with open(percorso, "wb") as f:
        f.write("#EXTM3U\r\nCittà.mp3\r\n".encode("cp1252"))
    letta = importazione.leggi(percorso)
    assert letta["libgme"] is None and [v.percorso for v in letta["voci"]] == [os.path.join(cartella, "Città.mp3")]
    stato = os.stat(percorso)
    assert letta["origine"] == {"percorso": percorso, "data": stato.st_mtime, "dimensione": stato.st_size}
    assert "errore" in importazione.leggi(os.path.join(cartella, "non c'è.m3u"))


def test_leggi_corregge_cartelle_e_formati_guardando_il_disco(cartella):
    # Dal nome Live.1986 sembra un file e LEGGIMI una cartella: il disco dice il contrario.
    os.makedirs(os.path.join(cartella, "Live.1986"))
    with open(os.path.join(cartella, "LEGGIMI"), "wb"):
        pass
    percorso = os.path.join(cartella, "Strana.m3u")
    with open(percorso, "wb") as f:
        f.write(b"Live.1986\r\nLEGGIMI\r\nAlbum\r\nnote.txt\r\n")
    letta = importazione.leggi(percorso)
    # Quelli che non ci sono restano come dice il nome.
    assert [(os.path.basename(v.percorso), v.motivo) for v in letta["voci"]] == [
        ("Live.1986", "cartella"), ("LEGGIMI", "formato"), ("Album", "cartella"), ("note.txt", "formato")]
    # In rete il motivo resta quello del nome: ogni domanda puo' restare appesa.
    voci, _libgme = importazione.analizza(b"Live.1986\r\nLEGGIMI\r\n", percorso)
    importazione.rivedi_i_motivi(voci, in_rete=lambda _percorso: True)
    assert [v.motivo for v in voci] == ["formato", "cartella"]


def test_leggi_in_rete_lascia_perdere_un_file_che_tace(cartella, monkeypatch):
    # La condivisione risponde, ma la lettura del file resta appesa, come con
    # il Samba dell'Iliadbox: dopo l'attesa si annulla, e la coda va avanti.
    percorso = os.path.join(cartella, "Rock.m3u")
    with open(percorso, "wb") as f:
        f.write(b"a.mp3\r\n")
    monkeypatch.setattr(importazione.ricerca, "in_rete", lambda _percorso: True)
    monkeypatch.setattr(importazione.questa_rete, "raggiungibile", lambda _cartella, attesa=None: True)
    # Se risponde si legge come sul disco, a blocchi.
    monkeypatch.setattr(importazione, "BLOCCO_DI_LETTURA", 2)
    assert [v.percorso for v in importazione.leggi(percorso)["voci"]] == [os.path.join(cartella, "a.mp3")]
    sbloccata, annullate = threading.Event(), []

    def appesa(_percorso, al_passo=None):
        sbloccata.wait(10)
        raise OSError("lettura annullata")

    def annulla(filo):
        annullate.append(filo.name)
        sbloccata.set()

    monkeypatch.setattr(importazione, "_leggi_il_file", appesa)
    monkeypatch.setattr(importazione.ricerca, "annulla_la_lettura", annulla)
    assert importazione.leggi(percorso, attesa=0.2) == {"errore": f"{cartella} non risponde."}
    assert sbloccata.wait(5) and annullate == ["MeTeOra, lettura della playlist"]


def test_cambiata_guarda_la_dimensione_e_la_data():
    prima = {"percorso": "x.m3u", "data": 1000.0, "dimensione": 50}
    assert not importazione.cambiata(prima, dict(prima))
    # Su FAT la data va a passi di due secondi: sotto non conta.
    assert not importazione.cambiata(prima, {**prima, "data": 1001.5})
    assert importazione.cambiata(prima, {**prima, "data": 1002.0})
    assert importazione.cambiata(prima, {**prima, "dimensione": 51})
    assert importazione.cambiata({"percorso": "x.m3u"}, prima)


def test_l_esito_toglie_i_mancanti_e_conta_le_radici_che_non_rispondono():
    voci = [importazione.risolvi(r, r"E:\Musica") for r in ("a.mp3", "manca.mp3", "http://x/y", r"F:\lontano\b.mp3", "a.mp3", r"f:\lontano\c.mp3", "note.txt")]
    percorsi, scartate, tenute = importazione.esito(voci, {pulizia.norm(r"E:\Musica\manca.mp3")}, {"F:": 2})
    # I doppioni restano, nell'ordine del file.
    assert percorsi == [r"E:\Musica\a.mp3", r"F:\lontano\b.mp3", r"E:\Musica\a.mp3", r"f:\lontano\c.mp3"]
    assert [(v.leggibile, v.motivo) for v in scartate] == [(r"E:\Musica\manca.mp3", "mancante"), ("http://x/y", "indirizzo"), (r"E:\Musica\note.txt", "formato")]
    assert tenute == {"F:": 2}
    # Dal piu' frequente; a parita' nell'ordine dei motivi, i mancanti per primi.
    assert importazione.conta_i_motivi(scartate) == [("mancante", 1), ("indirizzo", 1), ("formato", 1)]
    assert importazione.conta_i_motivi([*scartate, scartate[1]]) == [("indirizzo", 2), ("mancante", 1), ("formato", 1)]
