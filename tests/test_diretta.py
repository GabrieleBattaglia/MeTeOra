# MeTeOra, le prove delle dirette lette da MeTeOra: un server ICY finto in locale, niente rete.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 12/11/2026: nasce con la 3.11.0, issue 46. Nella 3.11.6 il filtro dei fotogrammi.

import socket
import threading

import pytest

import diretta


def _server(risposte):
    """Un server TCP in locale: a ogni connessione manda la risposta dopo,
    byte per byte com'e', poi chiude. Torna (porta, richieste ricevute)."""
    presa = socket.socket()
    presa.bind(("127.0.0.1", 0))
    presa.listen(8)
    richieste = []

    def servi():
        for risposta in risposte:
            try:
                conn, _da = presa.accept()
            except OSError:
                return
            with conn:
                richieste.append(conn.recv(4096).decode("latin-1"))
                conn.sendall(risposta(presa.getsockname()[1]) if callable(risposta) else risposta)
        presa.close()

    threading.Thread(target=servi, daemon=True).start()
    return presa.getsockname()[1], richieste


def _icy(audio, metaint, titoli, stato=b"HTTP/1.0 200 OK"):
    """Una risposta con l'audio diviso in blocchi da metaint e, dopo ognuno, i
    metadati: un titolo, o il byte zero."""
    corpo = b""
    for i in range(0, len(audio), metaint):
        corpo += audio[i:i + metaint]
        # I metadati vengono solo dopo un blocco intero, come nei server veri.
        if len(audio[i:i + metaint]) < metaint:
            break
        titolo = titoli.pop(0) if titoli else None
        if titolo is None:
            corpo += b"\x00"
        else:
            meta = f"StreamTitle='{titolo}';StreamUrl='';".encode()
            meta += b"\x00" * (-len(meta) % 16)
            corpo += bytes([len(meta) // 16]) + meta
    return stato + b"\r\nContent-Type: audio/mpeg\r\nicy-metaint: " + str(metaint).encode() + b"\r\n\r\n" + corpo


def _tutto(lettura):
    dati = b""
    while True:
        pezzo = lettura.read(7)
        if not pezzo:
            return dati
        dati += pezzo


def test_da_leggere_e_indirizzi():
    assert diretta.da_leggere("http://cast.az-streamingserver.com:8590/stream")
    assert diretta.da_leggere("https://x.it/radio.mp3?token=1")
    assert not diretta.da_leggere("https://x.it/live/main.m3u8") and not diretta.da_leggere("http://x.it/3.pls")
    assert not diretta.da_leggere("rtsp://x.it/a") and not diretta.da_leggere("") and not diretta.da_leggere(None)
    url = "https://d131.rndfnk.com/star/rne5/mp3/128/stream.mp3?aggregator=tunein&cid=01G"
    assert diretta.indirizzo_per_mpv(url).startswith("diretta://") and "/" not in diretta.indirizzo_per_mpv(url)[len("diretta://"):]
    assert diretta.indirizzo_vero(diretta.indirizzo_per_mpv(url)) == url


def test_titolo_dei_metadati():
    assert diretta.titolo_dei_metadati(b"StreamTitle='Lucio Dalla - Caruso';StreamUrl='';\x00\x00") == "Lucio Dalla - Caruso"
    assert diretta.titolo_dei_metadati("StreamTitle='Caffè   corretto';".encode("latin-1")) == "Caffè corretto"
    assert diretta.titolo_dei_metadati(b"StreamTitle='';") is None and diretta.titolo_dei_metadati(b"\x00" * 16) is None


@pytest.mark.parametrize("stato", [b"HTTP/1.0 200 OK", b"ICY 200 OK"])
def test_la_lettura_toglie_i_metadati_e_dice_i_titoli(stato, monkeypatch):
    # L'audio arriva intero e senza metadati, letto a pezzi piccoli che
    # cadono anche a cavallo dei blocchi; un titolo ripetuto si dice una volta.
    # Finito l'audio il server non c'e' piu': le riconnessioni falliscono.
    monkeypatch.setattr(diretta, "PAUSA_DELLE_RIPROVE", 0.0)
    audio = bytes(range(256)) * 4
    porta, richieste = _server([_icy(audio, 100, [None, "Primo", None, "Primo", "Secondo"], stato)])
    titoli = []
    lettura = diretta.Lettura(f"http://127.0.0.1:{porta}/stream", al_titolo=titoli.append, riconnetti=False)
    assert _tutto(lettura) == audio
    assert titoli == ["Primo", "Secondo"]
    assert "Icy-MetaData: 1" in richieste[0] and "User-Agent: MeTeOra/" in richieste[0]


def test_i_rinvii_e_il_server_senza_metadati(monkeypatch):
    monkeypatch.setattr(diretta, "PAUSA_DELLE_RIPROVE", 0.0)
    audio = b"x" * 3000
    porta_vera, _r = _server([b"HTTP/1.1 200 OK\r\nContent-Type: audio/aac\r\nConnection: close\r\n\r\n" + audio])
    porta, _richieste = _server([f"HTTP/1.1 302 Found\r\nLocation: http://127.0.0.1:{porta_vera}/vera\r\nContent-Length: 0\r\n\r\n".encode()])
    lettura = diretta.Lettura(f"http://127.0.0.1:{porta}/radio", riconnetti=False)
    assert _tutto(lettura) == audio


def test_un_server_che_chiude_si_riprova_poi_basta(monkeypatch):
    monkeypatch.setattr(diretta, "PAUSA_DELLE_RIPROVE", 0.0)
    pezzo = b"HTTP/1.0 200 OK\r\nContent-Type: audio/mpeg\r\n\r\n" + b"a" * 50
    porta, richieste = _server([pezzo] * (1 + diretta.RIPROVE))
    lettura = diretta.Lettura(f"http://127.0.0.1:{porta}/stream")
    assert _tutto(lettura) == b"a" * 50 * (1 + diretta.RIPROVE)
    # Tre volte si ricollega, alla quarta caduta smette.
    assert lettura.riconnessioni == diretta.RIPROVE and len(richieste) == 1 + diretta.RIPROVE


def test_un_errore_http_non_apre_la_diretta():
    porta, _richieste = _server([b"HTTP/1.0 404 Not Found\r\nContent-Length: 0\r\n\r\n"])
    with pytest.raises(OSError, match="404"):
        diretta.Lettura(f"http://127.0.0.1:{porta}/niente")


def test_chiusa_non_legge_piu():
    porta, _richieste = _server([b"HTTP/1.0 200 OK\r\n\r\n" + b"b" * 10])
    lettura = diretta.Lettura(f"http://127.0.0.1:{porta}/stream")
    lettura.cancel()
    assert lettura.read(100) == b""


def test_il_motore_apre_le_radio_con_il_protocollo(monkeypatch):
    import indirizzi
    import motore

    indirizzi.metti_il_diretto("http://icestreaming.rai.it/3.mp3", dal_vivo=True)
    indirizzi.metti_il_diretto("https://x.it/live/main.m3u8", dal_vivo=True)
    assert motore._Brano("http://icestreaming.rai.it/3.mp3").indirizzo == diretta.indirizzo_per_mpv("http://icestreaming.rai.it/3.mp3")
    assert motore._Brano("https://x.it/live/main.m3u8").indirizzo == "https://x.it/live/main.m3u8"
    # Un lettore di passaggio, come quello dello speaker, apre l'indirizzo vero.
    brano = motore._Brano("http://icestreaming.rai.it/3.mp3")
    assert motore._indirizzo_nel_lettore({}, brano) == "http://icestreaming.rai.it/3.mp3"


# I casi della rilettura del 12 novembre 2026.


def test_close_sveglia_una_lettura_ferma():
    # Un server che manda le intestazioni e poi tace: close, da un altro
    # filo, sveglia la lettura subito, non dopo ATTESA.
    import time

    presa = socket.socket()
    presa.bind(("127.0.0.1", 0))
    presa.listen(1)
    fine = threading.Event()

    def servi():
        conn, _da = presa.accept()
        conn.recv(4096)
        conn.sendall(b"HTTP/1.0 200 OK\r\nicy-metaint: 8000\r\n\r\n" + b"a" * 10)
        fine.wait(30)
        conn.close()
        presa.close()

    threading.Thread(target=servi, daemon=True).start()
    lettura = diretta.Lettura(f"http://127.0.0.1:{presa.getsockname()[1]}/stream")
    assert lettura.read(100) == b"a" * 10
    arrivato = []
    filo = threading.Thread(target=lambda: arrivato.append(lettura.read(100)))
    filo.start()
    time.sleep(0.3)
    inizio = time.monotonic()
    lettura.close()
    filo.join(5)
    fine.set()
    assert arrivato == [b""] and time.monotonic() - inizio < 2


def test_una_riconnessione_fallita_si_riprova(monkeypatch):
    pezzo = b"HTTP/1.0 200 OK\r\nContent-Type: audio/mpeg\r\n\r\n" + b"a" * 40
    porta, richieste = _server([pezzo, b"HTTP/1.0 503 Service Unavailable\r\n\r\n", pezzo])
    monkeypatch.setattr(diretta, "PAUSA_DELLE_RIPROVE", 0.0)
    lettura = diretta.Lettura(f"http://127.0.0.1:{porta}/stream")
    # Il 503 non ferma la radio: la riprova dopo trova il server.
    assert _tutto(lettura)[:80] == b"a" * 80 and len(richieste) == 3


def test_la_registrazione_non_si_ricollega():
    pezzo = b"HTTP/1.0 200 OK\r\n\r\n" + b"r" * 30
    porta, richieste = _server([pezzo, pezzo])
    lettura = diretta.Lettura(f"http://127.0.0.1:{porta}/stream", riconnetti=False)
    assert _tutto(lettura) == b"r" * 30 and lettura.riconnessioni == 0 and len(richieste) == 1


def test_un_file_con_la_lunghezza_non_ricomincia():
    porta, richieste = _server([b"HTTP/1.1 200 OK\r\nContent-Length: 20\r\nConnection: close\r\n\r\n" + b"f" * 20] * 2)
    lettura = diretta.Lettura(f"http://127.0.0.1:{porta}/brano.mp3")
    assert _tutto(lettura) == b"f" * 20 and len(richieste) == 1


def test_una_risposta_a_pezzi():
    corpo = b"".join(f"{len(p):x}".encode() + b"\r\n" + p + b"\r\n" for p in (b"uno", b"duetre", b"quattro")) + b"0\r\n\r\n"
    porta, _richieste = _server([b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n" + corpo])
    lettura = diretta.Lettura(f"http://127.0.0.1:{porta}/stream", riconnetti=False)
    assert _tutto(lettura) == b"unoduetrequattro"


def test_un_indirizzo_che_porta_a_una_lista_resta_a_libmpv():
    porta, _richieste = _server([b"HTTP/1.0 200 OK\r\nContent-Type: application/vnd.apple.mpegurl\r\n\r\n#EXTM3U\n"])
    with pytest.raises(diretta.NonDiretta):
        diretta.Lettura(f"http://127.0.0.1:{porta}/radio")
    diretta.a_libmpv("http://esempio.it/radio")
    assert not diretta.da_leggere("http://esempio.it/radio")


def test_il_motore_ripiega_su_libmpv_se_l_indirizzo_porta_a_una_lista(finestra):
    # La lista arriva due volte, a diretta.py e poi a libmpv; dentro c'e' un
    # WAV di un secondo, che libmpv apre da se'.
    import io
    import time
    import wave

    import indirizzi

    suono = io.BytesIO()
    with wave.open(suono, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\x00\x10" * 8000)
    porta_del_wav, _r = _server([b"HTTP/1.0 200 OK\r\nContent-Type: audio/wav\r\n\r\n" + suono.getvalue()] * 3)
    lista = f"HTTP/1.0 200 OK\r\nContent-Type: audio/x-mpegurl\r\n\r\nhttp://127.0.0.1:{porta_del_wav}/uno.wav\n".encode()
    porta, richieste = _server([lista] * 3)
    indirizzo = f"http://127.0.0.1:{porta}/radio"
    indirizzi.metti_il_diretto(indirizzo, dal_vivo=True)
    finestra.motore.suona(indirizzo)
    fine = time.monotonic() + 10
    while time.monotonic() < fine and not diretta._a_libmpv.issuperset({indirizzo}):
        time.sleep(0.05)
    assert indirizzo in diretta._a_libmpv and not diretta.da_leggere(indirizzo)
    while time.monotonic() < fine and len(richieste) < 2:
        time.sleep(0.05)
    assert len(richieste) >= 2
    finestra.motore.stop()


# Il filtro dei fotogrammi per lo speaker (3.11.6).

def _mp3(n, frequenza=24000):
    """n fotogrammi MP3 layer III senza CRC, mono: MPEG-2 a 56 kbps e 24 kHz,
    168 byte come quelli della BBC, o MPEG-1 a 192 kbps e 48 kHz, 576 byte.
    Il contenuto non ha 0xFF, che sembrerebbe un'intestazione."""
    if frequenza == 24000:
        testa, lunghezza = b"\xff\xf3\x74\xc0", 168
    else:
        testa, lunghezza = b"\xff\xfb\xb4\xc0", 576
    return [testa + bytes([0x11 + (k % 100)]) * (lunghezza - 4) for k in range(n)]


def _adts(n, contenuto=200):
    """n fotogrammi AAC LC in ADTS, 44,1 kHz, stereo, senza CRC."""
    lunghezza = 7 + contenuto
    testa = bytes([0xFF, 0xF1, 0x50, 0x80 | (lunghezza >> 11), (lunghezza >> 3) & 0xFF, ((lunghezza & 7) << 5) | 0x1F, 0xFC])
    return [testa + bytes([0x22 + (k % 100)]) * contenuto for k in range(n)]


def _a_pezzi(filtro, dati, passo=7):
    uscita = b""
    for i in range(0, len(dati), passo):
        uscita += filtro.passa(dati[i:i + passo])
    return uscita


def test_il_filtro_toglie_i_byte_rotti_e_i_fotogrammi_troncati():
    fotogrammi = _mp3(20)
    rotti = b"\x8d\x01\x02\x7f" * 8
    troncato = fotogrammi[0][:50]
    flusso = b"".join(fotogrammi[:6]) + rotti + b"".join(fotogrammi[6:12]) + troncato + b"".join(fotogrammi[12:])
    for passo in (1, 7, 100, 4096):
        filtro = diretta.Fotogrammi()
        uscita = _a_pezzi(filtro, flusso, passo)
        # L'ultimo aspetta il seguente, e a flusso finito passa se e' intero.
        assert uscita == b"".join(fotogrammi[:19]) and filtro.fine() == fotogrammi[19]
        assert filtro.rotture == 2 and filtro.scartati == len(rotti) + len(troncato) and not filtro.arreso


def test_il_filtro_tiene_l_aac_e_i_cambi_di_formato_confermati():
    fotogrammi = _adts(10)
    filtro = diretta.Fotogrammi()
    assert _a_pezzi(filtro, b"\x00\x01" + b"".join(fotogrammi[:5]) + b"\x13" * 40 + b"".join(fotogrammi[5:])) == b"".join(fotogrammi[:9])
    assert filtro.rotture == 1 and filtro.scartati == 42
    # Da 24 a 48 kHz, come la BBC il 12 novembre 2026: il formato nuovo passa.
    prima, dopo = _mp3(5), _mp3(5, frequenza=48000)
    filtro = diretta.Fotogrammi()
    assert _a_pezzi(filtro, b"".join(prima + dopo)) == b"".join(prima + dopo[:4]) and filtro.rotture == 0


def test_cio_che_non_e_mp3_passa_com_e():
    # Un flusso che si dice MP3 ma non lo e', o pochi byte: passa tutto.
    filtro = diretta.Fotogrammi()
    altro = bytes(range(100)) * 200
    assert _a_pezzi(filtro, altro, 1000) == altro and filtro.arreso
    filtro = diretta.Fotogrammi()
    assert filtro.passa(b"a" * 10) == b"" and filtro.fine() == b"a" * 10
    assert diretta.da_filtrare("audio/mpeg") and diretta.da_filtrare("audio/aacp; charset=x") and not diretta.da_filtrare("audio/ogg")
