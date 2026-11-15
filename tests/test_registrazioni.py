# MeTeOra, le prove delle registrazioni: libmpv vero su file locali, niente rete.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 10/11/2026: nasce con la 3.5.0, issue 42. Nella 3.13.0 la cartella delle registrazioni; nella 3.13.2 l'attesa al passaggio e le parti non unite. Nella 3.14.0 la voce che apre la cartella. Nella 3.15.0 i bit veri nei file e la voce a due passi.

import datetime
import json
import os
import socket
import struct
import threading
import time
import types
import typing
import wave

import numpy as np
import pytest

import registrazioni  # per primo, perche' carica libmpv

# isort: split
import mpv

import indirizzi
import motore
import statistiche
from playlist import Brano

RADIO = "http://icestreaming.rai.it/3.mp3"
RADIO_2 = "http://icestreaming.rai.it/2.mp3"


def _seno(percorso, secondi, frequenza=44100, canali=1, hz=440):
    campioni = (0.25 * np.sin(2 * np.pi * hz * np.arange(int(frequenza * secondi)) / frequenza) * 32767).astype("<i2")
    if canali == 2:
        campioni = np.repeat(campioni, 2)
    with wave.open(str(percorso), "wb") as f:
        f.setnchannels(canali)
        f.setsampwidth(2)
        f.setframerate(frequenza)
        f.writeframes(campioni.tobytes())
    return str(percorso)


def _durata(percorso):
    # Con le opzioni di MeTeOra, senza gli script Lua di libmpv: LuaJIT, avviato,
    # lancia eccezioni sue che faulthandler scrive come fatali, e non lo sono.
    lettore = mpv.MPV(**{**motore.OPZIONI_DI_BASE, "ao": "null"})
    pronto = threading.Event()
    lettore.register_event_callback(lambda e: pronto.set() if e.event_id.value in (mpv.MpvEventID.FILE_LOADED, mpv.MpvEventID.END_FILE) else None)
    lettore.command("loadfile", str(percorso))
    pronto.wait(10)
    traccia = next((t for t in lettore.track_list or [] if t.get("type") == "audio"), {})
    durata = lettore.duration
    lettore.terminate()
    if str(percorso).endswith(".wav"):
        # Del WAV la durata vera la dice l'intestazione.
        with wave.open(str(percorso), "rb") as f:
            durata = f.getnframes() / f.getframerate()
    return durata, traccia.get("demux-channel-count"), traccia.get("demux-samplerate")


def _salto(percorso, secondi):
    """Dove arriva libmpv saltando ai secondi dati del file, in pausa."""
    lettore = mpv.MPV(**{**motore.OPZIONI_DI_BASE, "ao": "null", "pause": True})
    pronto = threading.Event()
    lettore.register_event_callback(lambda e: pronto.set() if e.event_id.value in (mpv.MpvEventID.FILE_LOADED, mpv.MpvEventID.END_FILE) else None)
    lettore.command("loadfile", str(percorso))
    pronto.wait(10)
    lettore.command("seek", secondi, "absolute+exact")
    arrivo, fine = None, time.monotonic() + 5
    while time.monotonic() < fine:
        arrivo = lettore.time_pos
        if arrivo is not None and abs(arrivo - secondi) < 0.05:
            break
        time.sleep(0.02)
    lettore.terminate()
    return arrivo


def _registrata(tmp_path, nome, secondi, formato="mp3", kbps=64, canali=1, frequenza=44100, bit=16, hz=440):
    """Una registrazione di un file locale, che finisce da se', completa."""
    sorgente = _seno(tmp_path / f"{nome}.wav", secondi, hz=hz)
    finita = threading.Event()
    reg = registrazioni.Registrazione(sorgente, nome, indirizzi.Flusso(sorgente), formato, kbps, canali, frequenza, dove=str(tmp_path / "Registrazioni"),
        al_termine=lambda _r: finita.set(), bit=bit)
    reg.avvia()
    assert finita.wait(30)
    return reg


def _a_parti(tmp_path, formato, tagli, nome="unione"):
    """Una diretta finta fatta delle parti date, (secondi, taglio, marker),
    ognuna una registrazione vera di un seno, da unire."""
    reg = registrazioni.Registrazione(RADIO, f"{nome} {formato}", indirizzi.Flusso(RADIO, dal_vivo=True), formato, 64, 1, 44100, dove=str(tmp_path / "Registrazioni"))
    parti = []
    for numero, (secondi, taglio, marker) in enumerate(tagli):
        origine = _registrata(tmp_path, f"{nome} {formato} {numero}", secondi, formato, hz=440 * (numero + 1))
        parte = registrazioni.Parte(origine.percorso)
        parte.secondi, parte.taglio = secondi, taglio
        parte.marker = [[t, n, False, n] for t, n in marker]
        parti.append(parte)
    reg._parti = parti
    return reg


# Il modulo, senza finestra.


def test_il_nome_del_file(tmp_path):
    quando = datetime.datetime(2026, 11, 10, 16, 5, 12)
    percorso = registrazioni.nome_del_file('Rai Radio 3: "prova"/<due>', quando, ".mp3", str(tmp_path))
    assert os.path.basename(percorso) == "Rai Radio 3 prova due 2026-11-10 16.05.12.mp3"
    open(percorso, "wb").close()
    assert os.path.basename(registrazioni.nome_del_file("Rai Radio 3: prova/due", quando, ".mp3", str(tmp_path))).endswith("16.05.12 2.mp3")
    assert os.path.basename(registrazioni.nome_del_file("...", quando, ".wav", str(tmp_path))).startswith("Registrazione 2026")
    assert registrazioni.estensioni() == {".mp3", ".opus", ".aac", ".flac", ".wav"}


def test_il_nome_del_file_vede_le_parti_e_il_file_delle_parti(tmp_path):
    # Le parti sono .parziale1 e seguenti, e nome_del_file cercava .parziale:
    # due registrazioni dello stesso titolo nello stesso secondo avevano lo
    # stesso file finale (15 novembre 2026).
    quando = datetime.datetime(2026, 11, 15, 16, 5, 12)
    percorso = registrazioni.nome_del_file("Rai Radio 3", quando, ".mp3", str(tmp_path))
    open(percorso + ".parziale1", "wb").close()
    secondo = registrazioni.nome_del_file("Rai Radio 3", quando, ".mp3", str(tmp_path))
    assert secondo.endswith("16.05.12 2.mp3")
    open(secondo + registrazioni.FILE_DELLE_PARTI, "wb").close()
    assert registrazioni.nome_del_file("Rai Radio 3", quando, ".mp3", str(tmp_path)).endswith("16.05.12 3.mp3")


def test_il_nome_dei_marker():
    assert registrazioni.nome_del_marker("  Lucio   Dalla -\tCaruso ") == "Lucio Dalla - Caruso"
    assert registrazioni.nome_del_marker("x" * 100) == "x" * registrazioni.LUNGHEZZA_DEL_MARKER
    assert registrazioni.nome_del_marker("   ") == "" and registrazioni.nome_del_marker(None) == ""


def test_la_qualita_si_adatta_alla_sorgente():
    assert registrazioni.parametri("mp3", 128) == (128, 2, 44100)
    # Mono con meta' dei kbps, mai piu' della sorgente, mai piu' campioni della sorgente.
    assert registrazioni.parametri("mp3", 128, sorgente_kbps=320, canali=1, frequenza=48000) == (64, 1, 44100)
    assert registrazioni.parametri("mp3", 128, sorgente_kbps=56, canali=2, frequenza=22050) == (48, 2, 22050)
    assert registrazioni.parametri("mp3", 32, sorgente_kbps=20, canali=1) == (32, 1, 44100)
    assert registrazioni.parametri("opus", 96, canali=2, frequenza=22050) == (96, 2, 48000)
    # Senza perdita, dalla 3.15.0, la frequenza della sorgente fino a 96 kHz.
    assert registrazioni.parametri("flac", 128, sorgente_kbps=64, canali=1, frequenza=192000) == (None, 1, 96000)
    assert registrazioni.parametri("wav", 320, frequenza=22050) == (None, 2, 22050)
    assert registrazioni.descrizione("mp3", 128, 2, 44100) == "MP3 a 128 kbps, stereo, 44.1 kHz"
    assert registrazioni.descrizione("flac", None, 1, 48000) == "FLAC a 16 bit, mono, 48 kHz"
    # I parametri scelti (3.15.0): i canali vincono sulla sorgente, la frequenza fissa vale senza perdita.
    assert registrazioni.parametri("mp3", 128, canali=2, scelta_canali="mono") == (64, 1, 44100)
    assert registrazioni.parametri("mp3", 128, canali=1, scelta_canali="stereo") == (128, 2, 44100)
    assert registrazioni.parametri("wav", 128, canali=1, frequenza=22050, scelta_canali="stereo", scelta_frequenza=96000) == (None, 2, 96000)
    assert registrazioni.parametri("mp3", 128, frequenza=22050, scelta_frequenza=96000) == (128, 2, 22050)
    assert [registrazioni.bit_per(f, b) for f, b in (("mp3", 24), ("flac", 32), ("flac", 16), ("wav", 32), ("wav", 8))] == [None, 24, 16, 32, 16]
    assert registrazioni.descrizione("wav", None, 2, 96000, 32) == "WAV a 32 bit in virgola mobile, stereo, 96 kHz"


@pytest.mark.parametrize("formato", ["mp3", "opus", "aac", "flac", "wav"])
def test_una_registrazione_che_finisce_da_se(tmp_path, formato):
    reg = _registrata(tmp_path, f"breve {formato}", 3.0, formato)
    assert reg.stato == "completa" and os.path.exists(reg.percorso) and reg.percorso.endswith(registrazioni.FORMATI[formato][3])
    durata, canali, frequenza = _durata(reg.percorso)
    # Dell'AAC grezzo libmpv stima la durata dai kbps, e sbaglia; il WAV ha in
    # coda un terzo di secondo di silenzio, il riempimento dell'ultimo blocco
    # del codificatore PCM di libmpv (prova del 10 novembre 2026).
    tolleranza = 0.5 if formato == "wav" else 0.2
    assert (abs(durata - 3.0) < tolleranza or formato == "aac") and canali == 1 and frequenza == (48000 if formato == "opus" else 44100)
    assert (abs(reg.secondi - 3.0) < tolleranza or formato == "aac") and reg.byte == os.path.getsize(reg.percorso)
    # Niente parti e niente file delle parti, a registrazione chiusa.
    assert not [f for f in os.listdir(os.path.dirname(reg.percorso)) if ".parziale" in f or f.endswith(registrazioni.FILE_DELLE_PARTI)]


def test_le_parti_si_uniscono(tmp_path):
    """Le parti dopo una ripresa si uniscono senza ricodificare, e la durata
    giusta la dicono libmpv e mutagen, che legge lo schedario (15 novembre
    2026): prima l'MP3 accodato teneva l'intestazione Info della prima parte,
    e mutagen diceva i secondi della sola prima."""
    import mutagen

    for formato, taglio in (("mp3", 0.0), ("mp3", 1.0), ("flac", 1.0)):
        reg = _a_parti(tmp_path, formato, [(2.0, 0.0, []), (3.0, taglio, [])], nome=f"unione {taglio}")
        uno, due = (parte.file for parte in reg._parti)
        reg._unisci()
        durata, _canali, _frequenza = _durata(reg.percorso)
        # Il codificatore aggiunge in coda a ogni parte qualche centesimo; l'MP3
        # toglie un fotogramma in piu' dopo il taglio, per il serbatoio di bit.
        assert abs(durata - (5.0 - taglio)) < 0.2, (formato, taglio, durata)
        assert abs(mutagen.File(reg.percorso).info.length - durata) < 0.07, (formato, taglio)
        assert abs(reg.secondi - (5.0 - taglio)) < 0.15 and not os.path.exists(uno) and not os.path.exists(due)


def test_l_mp3_si_taglia_a_fotogrammi_e_tiene_un_info_solo(tmp_path):
    import mutagen.mp3

    reg = _a_parti(tmp_path, "mp3", [(2.0, 0.0, []), (3.0, 0.0, []), (3.0, 1.0, [])], nome="fotogrammi")
    reg._unisci()
    with open(reg.percorso, "rb") as f:
        dati = f.read()
    # Un'intestazione Info sola, quella della prima parte, con i conti del file intero.
    assert dati.count(b"Info") == 1 and dati[:3] == b"ID3"
    info = mutagen.mp3.MP3(reg.percorso).info
    assert abs(info.length - reg.secondi) < 0.06 and abs(info.length - 7.0) < 0.2
    # Il taglio cade a fotogrammi, uno in piu' del secondo chiesto.
    fotogramma = 1152 / 44100
    assert abs(reg.secondi - (2.0376 + 3.0 + 0.03 + 3.0 + 0.03 - 1.0 - fotogramma)) < 0.1
    # Si salta dove si vuole, anche nell'ultima parte.
    assert abs(_salto(reg.percorso, 6.5) - 6.5) < 0.05


def test_l_opus_diventa_un_ogg_solo(tmp_path):
    # Accodato a byte, l'Opus era un Ogg concatenato: libmpv non saltava oltre
    # la prima parte, e mutagen ne diceva la durata della sola prima.
    import mutagen.oggopus

    for taglio in (0.0, 1.0):
        reg = _a_parti(tmp_path, "opus", [(2.0, 0.0, []), (3.0, taglio, [])], nome=f"ogg {taglio}")
        reg._unisci()
        with open(reg.percorso, "rb") as f:
            dati = f.read()
        assert dati.count(b"OpusHead") == 1 and dati.count(b"OpusTags") == 1
        assert abs(mutagen.oggopus.OggOpus(reg.percorso).info.length - (5.0 - taglio)) < 0.05 and abs(reg.secondi - (5.0 - taglio)) < 0.05
        assert abs(_salto(reg.percorso, 4.5 - taglio) - (4.5 - taglio)) < 0.05


def test_il_wav_si_taglia_al_campione_senza_il_riempimento(tmp_path):
    # libmpv aggiunge in coda a ogni parte WAV fino a un terzo di secondo di
    # zeri: all'unione si toglie, e il taglio della riserva e' esatto.
    for taglio in (0.0, 1.0):
        reg = _a_parti(tmp_path, "wav", [(2.0, 0.0, []), (3.0, taglio, [])], nome=f"campioni {taglio}")
        reg._unisci()
        with wave.open(reg.percorso, "rb") as f:
            assert f.getnframes() == round((5.0 - taglio) * 44100) and f.getframerate() == 44100
        assert reg.secondi == pytest.approx(5.0 - taglio)


def test_l_aac_si_accoda_a_fotogrammi(tmp_path):
    import schedario

    reg = _a_parti(tmp_path, "aac", [(2.0, 0.0, []), (3.0, 1.0, [])], nome="adts")
    reg._unisci()
    # Lo schedario conta i fotogrammi dell'AAC grezzo: la durata e' quella giusta.
    assert abs(schedario.durata_adts(reg.percorso) - reg.secondi) < 0.001 and abs(reg.secondi - 4.0) < 0.15


def test_i_marker_vanno_sul_tempo_del_file_finale(tmp_path):
    """I marker delle parti, contati sul file finale: senza le pause e senza
    la riserva tagliata; uno caduto nella riserva va sulla giunzione."""
    reg = _a_parti(tmp_path, "wav", [(2.0, 0.0, [(0.0, "Inizio"), (1.5, "Caruso")]), (3.0, 1.0, [(0.0, "Ripresa alle 16.05"), (2.0, "Azzurro")])],
        nome="marker")
    reg._unisci()
    assert [(round(t, 3), n) for f, t, n in reg.marker_finali if f == reg.percorso] == [(0.0, "Inizio"), (1.5, "Caruso"), (2.0, "Ripresa alle 16.05"), (3.0, "Azzurro")]
    # Una puntata porta i capitoli della sorgente gia' registrati.
    puntata = _a_parti(tmp_path, "wav", [(2.0, 0.0, []), (2.0, 0.0, [])], nome="puntata")
    puntata.dal_vivo, puntata.capitoli = False, [(0.0, "Sigla"), (3.0, "  Intervista  "), (9.0, "Oltre la fine")]
    puntata._unisci()
    assert [(round(t, 3), n) for _f, t, n in puntata.marker_finali] == [(0.0, "Sigla"), (3.0, "Intervista")]


def test_eliminare_toglie_i_file(tmp_path):
    reg = _registrata(tmp_path, "da togliere", 1.0)
    assert os.path.exists(reg.percorso)
    reg.elimina()
    assert reg.stato == "eliminata" and not os.path.exists(reg.percorso)


def test_la_riserva_di_una_ripresa_si_misura_con_l_orologio(monkeypatch):
    """Dopo la prima parte, i secondi registrati in piu' dell'orologio sono la
    riserva della radio; dopo un ricollegamento se ne toglie solo il
    doppione, e il buco d'orologio della caduta resta (15 novembre 2026)."""
    reg = registrazioni.Registrazione(RADIO, "x", indirizzi.Flusso(RADIO, dal_vivo=True), dove="non usata")
    parte = registrazioni.Parte("x.parziale2")
    parte.posizione, parte.partita = 30.0, 100.0
    reg._parti = [registrazioni.Parte("x.parziale1")]
    monkeypatch.setattr(registrazioni.time, "monotonic", lambda: 106.0)
    assert reg._registrati(parte, types.SimpleNamespace(time_pos=None)) == (30.0, 24.0)
    # Caduta 4 secondi prima della parte nuova: della riserva di 24 se ne tolgono 20.
    parte.buco = 4.0
    assert reg._registrati(parte, types.SimpleNamespace(time_pos=None)) == (30.0, 20.0)
    parte.buco = 40.0
    assert reg._registrati(parte, types.SimpleNamespace(time_pos=None)) == (30.0, 0.0)
    puntata = registrazioni.Registrazione("x", "x", indirizzi.Flusso("https://x/p.mp3"), dove="non usata")
    puntata._parti = reg._parti
    assert puntata._registrati(parte, types.SimpleNamespace(time_pos=31.0)) == (31.0, 0.0)
    # Una diretta riconosciuta dal motore, con un flusso che non lo dice.
    assert registrazioni.Registrazione(RADIO, "x", indirizzi.Flusso(RADIO), dove="non usata", dal_vivo=True).dal_vivo


def test_i_titoli_diventano_marker_con_la_distanza_minima(monkeypatch):
    """Il primo titolo va all'inizio; un titolo che arriva entro la distanza
    minima rinomina il marker di prima; su una ripresa si aggiunge; i
    doppioni delle connessioni nuove non contano; il richiamo dice numero,
    nome e secondi, senza il lucchetto."""
    orologio = [1000.0]
    monkeypatch.setattr(registrazioni.time, "monotonic", lambda: orologio[0])
    detti = []
    reg = registrazioni.Registrazione(RADIO, "Rai Radio 3", indirizzi.Flusso(RADIO, dal_vivo=True), dove="non usata",
        al_marker=lambda r, numero, nome, secondi: detti.append((numero, nome)))
    monkeypatch.setattr(reg, "_annota", lambda: None)
    parte = registrazioni.Parte("x.parziale1")
    parte.partita = orologio[0]
    reg._parte = parte
    parte.posizione = 1.5
    reg._titolo_nella_parte(parte, "Radio 3 Suite")
    orologio[0] += 5
    parte.posizione = 6.0
    reg._titolo_nella_parte(parte, "Lucio  Dalla - Caruso")
    orologio[0] += 60
    parte.posizione = 66.0
    reg._titolo_nella_parte(parte, "Lucio Dalla - Caruso")
    reg._titolo_nella_parte(parte, "Mina - Azzurro")
    reg._titolo_nella_parte(registrazioni.Parte("vecchia"), "Da una parte chiusa")
    assert parte.marker == [[0.0, "Lucio Dalla - Caruso", False, "Lucio Dalla - Caruso"], [66.0, "Mina - Azzurro", False, "Mina - Azzurro"]]
    assert detti == [(1, "Radio 3 Suite"), (1, "Lucio Dalla - Caruso"), (2, "Mina - Azzurro")] and reg.numero_dei_marker == 2
    # La ripresa ha il suo marker, e un titolo subito dopo le si aggiunge.
    nuova = registrazioni.Parte("x.parziale2")
    reg._parte = nuova
    reg._marker_di_ripresa()
    reg._titolo_nella_parte(nuova, "Battiato - La cura")
    assert nuova.marker[0][1].startswith("Ripresa alle ") and nuova.marker[0][1].endswith(": Battiato - La cura") and reg.numero_dei_marker == 3


def test_la_caduta_di_una_diretta_e_una_pausa_per_la_rete(tmp_path, monkeypatch):
    # Con alla_caduta la diretta che cade non finisce: va in pausa per la
    # rete, con la parte chiusa, e chi la riceve la ricollega.
    cadute = []
    reg = registrazioni.Registrazione(RADIO, "x", indirizzi.Flusso(RADIO, dal_vivo=True), dove=str(tmp_path), alla_caduta=lambda r, secondi: cadute.append(secondi))
    lettore = object()
    parte = registrazioni.Parte(str(tmp_path / "x.parziale1"))
    with open(parte.file, "wb") as f:
        f.write(b"x" * 10)
    parte.secondi = 5.0
    finita = threading.Event()
    finita.set()
    reg._parte, reg._lettore, reg._finita, reg.stato = parte, lettore, finita, "in_corso"
    monkeypatch.setattr(reg, "_registrati", lambda _p, _l: (5.0, 0.0))
    reg._finito_da_se(lettore, False)
    assert (reg.stato, reg.motivo) == ("in_pausa", "rete") and len(cadute) == 1 and reg._parti == [parte]


def _server_icy(audio, metaint, titoli, pausa=0.15):
    """Un server ICY in locale: a ogni connessione manda l'audio diviso in
    blocchi da metaint, con un titolo dopo ognuno, un blocco ogni pausa
    secondi come una radio vera, che va al passo dell'orologio, poi chiude.
    Torna la porta."""
    presa = socket.socket()
    presa.bind(("127.0.0.1", 0))
    presa.listen(4)

    def servi():
        for elenco in titoli:
            try:
                conn, _da = presa.accept()
            except OSError:
                return
            with conn:
                conn.recv(4096)
                conn.sendall(b"HTTP/1.0 200 OK\r\nContent-Type: audio/mpeg\r\nicy-metaint: " + str(metaint).encode() + b"\r\n\r\n")
                rimasti = list(elenco)
                for i in range(0, len(audio), metaint):
                    blocco = audio[i:i + metaint]
                    if len(blocco) == metaint:
                        titolo = rimasti.pop(0) if rimasti else None
                        meta = f"StreamTitle='{titolo}';".encode() if titolo else b""
                        meta += b"\0" * (-len(meta) % 16)
                        blocco += bytes([len(meta) // 16]) + meta
                    try:
                        conn.sendall(blocco)
                    except OSError:
                        break
                    time.sleep(pausa)
        presa.close()

    threading.Thread(target=servi, daemon=True).start()
    return presa.getsockname()[1]


def test_una_diretta_vera_con_i_titoli_e_il_ricollegamento(tmp_path, monkeypatch):
    """Dall'inizio alla fine, con un server ICY in locale e libmpv vero: i
    titoli della connessione della registrazione diventano marker, la
    caduta e' una pausa per la rete, il ricollegamento apre una parte nuova
    e l'unione porta i marker sul file finale, letto da mutagen."""
    import mutagen

    monkeypatch.setattr(registrazioni, "DISTANZA_DEI_MARKER", 0.0)
    sorgente = _registrata(tmp_path, "da servire", 6.0)
    with open(sorgente.percorso, "rb") as f:
        audio = f.read()
    # libmpv comincia a decodificare dopo un secondo e mezzo di flusso, che
    # sonda (misura del 15 novembre 2026): un titolo arrivato prima sta a zero.
    porta = _server_icy(audio, 4000, [["Primo", None, None, None, None, "Secondo"], ["Secondo", None, "Terzo"]])
    indirizzo = f"http://127.0.0.1:{porta}/stream"
    cadute, marker = threading.Event(), []
    reg = registrazioni.Registrazione(indirizzo, "Locale", indirizzi.Flusso(indirizzo, dal_vivo=True), "mp3", 64, 1, 44100, dove=str(tmp_path / "Registrazioni"),
        al_marker=lambda r, numero, nome, secondi: marker.append(nome), alla_caduta=lambda r, secondi: cadute.set())
    reg.avvia()
    assert cadute.wait(20) and (reg.stato, reg.motivo) == ("in_pausa", "rete")
    with open(reg.percorso + registrazioni.FILE_DELLE_PARTI, encoding="utf-8") as f:
        annotate = json.load(f)
    assert annotate["dal_vivo"] and [m[1] for m in annotate["parti"][0]["marker"]] == ["Primo", "Secondo"]
    cadute.clear()
    reg.pausa(False)
    assert cadute.wait(20) and len(reg._parti) == 2 and reg._parti[1].buco > 0
    percorso = reg.ferma()
    # Il doppione Secondo della connessione nuova non conta; Terzo cade nella riserva, sulla giunzione.
    assert marker == ["Primo", "Secondo", "Terzo"]
    assert [n for _f, _t, n in reg.marker_finali] == ["Primo", "Secondo", "Terzo"] and reg.marker_finali[0][1] == 0.0
    assert all(0.0 <= t <= reg.secondi for _f, t, _n in reg.marker_finali)
    assert abs(mutagen.File(percorso).info.length - reg.secondi) < 0.1
    assert not os.path.exists(reg.percorso + registrazioni.FILE_DELLE_PARTI)


def test_secondi_e_byte_non_aspettano_l_unione(tmp_path, monkeypatch):
    """R durante un'unione lunga fermava la finestra: secondi e byte
    prendevano il lucchetto che ferma tiene per tutta l'unione. Ora si
    leggono subito, e l'avanzamento dice a che punto e'."""
    reg = _a_parti(tmp_path, "mp3", [(2.0, 0.0, []), (2.0, 1.0, [])], nome="lenta")
    vera, via, dentro = registrazioni._accoda, threading.Event(), threading.Event()

    def lenta(parti, uscita, formato, avanza, fermata):
        avanza(0.4)
        dentro.set()
        via.wait(10)
        return vera(parti, uscita, formato, avanza, fermata)

    monkeypatch.setattr(registrazioni, "_accoda", lenta)
    filo = threading.Thread(target=reg.ferma, daemon=True)
    filo.start()
    assert dentro.wait(10)
    inizio = time.monotonic()
    assert reg.secondi > 2.5 and reg.byte > 0 and reg.in_salvataggio and reg.avanzamento == 0.4
    assert time.monotonic() - inizio < 0.5
    via.set()
    filo.join(10)
    assert not reg.in_salvataggio and reg.avanzamento is None and reg.salvataggio > 0 and os.path.exists(reg.percorso)


def test_in_fretta_le_parti_diventano_file(tmp_path):
    # Allo spegnimento di Windows non si unisce: le parti diventano subito
    # file separati, con i loro marker, e niente si perde.
    reg = _a_parti(tmp_path, "mp3", [(2.0, 0.0, [(1.0, "Caruso")]), (2.0, 1.0, [])], nome="fretta")
    reg.stato = "in_pausa"
    file = reg.salva_in_fretta()
    base = os.path.splitext(reg.parti_separate[0])[0][:-len(" parte 1")]
    assert file == [f"{base} parte 1.mp3", f"{base} parte 2.mp3"] and all(os.path.exists(f) for f in file) and reg.stato == "finita"
    assert reg.marker_finali == [(file[0], 1.0, "Caruso")]


def test_le_parti_rimaste_si_recuperano(tmp_path):
    """Dopo un crollo restano le parti e il file delle parti: all'avvio si
    uniscono, con i tagli e i marker; senza il file delle parti diventano
    file separati. I .unione a meta' si tolgono."""
    reg = _a_parti(tmp_path, "mp3", [(2.0, 0.0, [(0.5, "Caruso")]), (3.0, 1.0, [(1.5, "Azzurro")])], nome="crollo")
    cartella = os.path.dirname(reg.percorso)
    for numero, parte in enumerate(reg._parti, 1):
        os.replace(parte.file, f"{reg.percorso}.parziale{numero}")
        parte.file = f"{reg.percorso}.parziale{numero}"
    reg._annota()
    open(reg.percorso + ".unione", "wb").close()
    senza = os.path.join(cartella, "Senza 2026-11-15 10.00.00.mp3")
    os.replace(_registrata(tmp_path, "senza", 1.0).percorso, senza + ".parziale1")
    assert registrazioni.rimaste(cartella) == sorted([reg.percorso, senza]) and not os.path.exists(reg.percorso + ".unione")
    recuperata = registrazioni.Registrazione.da_recuperare(reg.percorso)
    assert recuperata.titolo == "crollo mp3" and recuperata.dal_vivo and recuperata.recuperate == 2
    percorso = recuperata.ferma()
    assert percorso == reg.percorso and abs(recuperata.secondi - 4.0) < 0.15
    assert [n for _f, _t, n in recuperata.marker_finali] == ["Caruso", "Azzurro"] and recuperata.marker_finali[0][1] == 0.5
    altra = registrazioni.Registrazione.da_recuperare(senza)
    altra.ferma()
    assert altra.parti_separate == [os.path.join(cartella, "Senza 2026-11-15 10.00.00 parte 1.mp3")]
    assert registrazioni.rimaste(cartella) == []


def test_le_parti_che_non_si_uniscono_restano_file(tmp_path, monkeypatch):
    # Un'unione che fallisce non perde niente: le parti diventano file da
    # ascoltare (3.13.2; prima restavano .parziale, nascoste).
    vera = registrazioni._riscrivi
    reg = _a_parti(tmp_path, "mp3", [(2.0, 0.0, []), (3.0, 1.0, [])], nome="radio lunga")
    uno, due = (parte.file for parte in reg._parti)
    base = os.path.splitext(reg.percorso)[0]

    def rotta(*_argomenti):
        raise OSError("le parti della registrazione non si uniscono")

    monkeypatch.setattr(registrazioni, "_accoda", rotta)
    percorso = reg.ferma()
    assert reg.parti_separate == [f"{base} parte 1.mp3", f"{base} parte 2.mp3"] and percorso == reg.parti_separate[0]
    assert all(os.path.exists(f) for f in reg.parti_separate) and not os.path.exists(uno) and not os.path.exists(due)
    # La riscrittura vera, con una parte che non c'e', fallisce e non lascia
    # un file a meta'.
    with pytest.raises(OSError):
        vera([registrazioni.Parte(str(tmp_path / "manca.mp3"))], str(tmp_path / "unione.mp3"), "mp3", 64, 1, 44100)
    assert not os.path.exists(tmp_path / "unione.mp3")


def _intestazione_del_wav(percorso):
    """(formato, bit, frequenza, canali) dall'intestazione di un WAV: 1 PCM, 3 virgola mobile."""
    with open(percorso, "rb") as f:
        dati = f.read(200)
    i = dati.find(b"fmt ")
    tag, canali, frequenza, _byte, _blocco, bit = struct.unpack("<HHIIHH", dati[i + 8:i + 24])
    if tag == 0xFFFE:
        tag = struct.unpack("<H", dati[i + 32:i + 34])[0]
    return tag, bit, frequenza, canali


def test_le_registrazioni_senza_perdita_hanno_i_loro_bit(tmp_path):
    # I bit scelti finiscono davvero nei file (3.15.0): WAV a 24 e a 32 in
    # virgola mobile, FLAC a 24, anche a 96 kHz e in stereo da una sorgente mono.
    import mutagen.flac

    reg = _registrata(tmp_path, "wav 24", 2.0, "wav", canali=2, frequenza=96000, bit=24)
    assert _intestazione_del_wav(reg.percorso) == (1, 24, 96000, 2) and reg.descrizione == "WAV a 24 bit, stereo, 96 kHz"
    reg = _registrata(tmp_path, "wav 32", 2.0, "wav", canali=1, frequenza=48000, bit=32)
    assert _intestazione_del_wav(reg.percorso) == (3, 32, 48000, 1)
    reg = _registrata(tmp_path, "flac 24", 2.0, "flac", canali=2, frequenza=48000, bit=24)
    info = mutagen.flac.FLAC(reg.percorso).info
    assert (info.bits_per_sample, info.sample_rate, info.channels) == (24, 48000, 2) and abs(info.length - 2.0) < 0.2
    # Il FLAC non ha i 32 bit: diventano 24.
    assert registrazioni.Registrazione("x", "y", indirizzi.Flusso("x"), "flac", None, 2, 48000, bit=32).bit == 24


def test_due_wav_a_24_bit_si_uniscono_con_la_loro_intestazione(tmp_path):
    # L'intestazione della prima parte, anche estesa, vale per il file unito.
    regs = [_registrata(tmp_path, f"wav24 {n}", 1.0, "wav", canali=2, frequenza=48000, bit=24) for n in range(2)]
    reg = registrazioni.Registrazione(RADIO, "unione 24", indirizzi.Flusso(RADIO, dal_vivo=True), "wav", None, 2, 48000, dove=str(tmp_path / "Registrazioni"), bit=24)
    for origine in regs:
        parte = registrazioni.Parte(origine.percorso)
        parte.secondi = 1.0
        reg._parti.append(parte)
    reg._unisci()
    assert _intestazione_del_wav(reg.percorso) == (1, 24, 48000, 2) and reg.secondi == pytest.approx(2.0)


# Le registrazioni nella finestra.


class _Finta:
    """Una registrazione finta: annota i comandi, e ferma dice il suo file."""

    create: typing.ClassVar[list] = []

    def __init__(self, sorgente, titolo, flusso, formato, kbps, canali, frequenza, al_termine=None, dove=None, bit=None, dal_vivo=None, al_marker=None,
            alla_caduta=None, capitoli=()):
        self.sorgente, self.titolo, self.flusso = sorgente, titolo, flusso
        self.formato, self.kbps, self.canali, self.frequenza, self.al_termine = formato, kbps, canali, frequenza, al_termine
        self.dal_vivo = getattr(flusso, "dal_vivo", True) if dal_vivo is None else dal_vivo
        self.al_marker, self.alla_caduta, self.capitoli = al_marker, alla_caduta, list(capitoli)
        self.stato, self.secondi, self.byte, self.comandi = "pronta", 754.0, 11_534_336, []
        self.dove, self.bit = dove, registrazioni.bit_per(formato, bit or 16)
        self.percorso = os.path.join(dove or registrazioni.cartella(), f"{titolo}.mp3")
        self.motivo = self.avanzamento = self.ultimo_marker = self.salvataggio = None
        self.marker_finali, self.parti_separate = [], []
        _Finta.create.append(self)

    @property
    def descrizione(self):
        return registrazioni.descrizione(self.formato, self.kbps, self.canali, self.frequenza, self.bit)

    def avvia(self):
        self.comandi.append("avvia")
        self.stato = "in_corso"

    def pausa(self, valore, motivo="mano", flusso=None):
        self.comandi.append(("pausa", valore))
        self.stato, self.motivo = ("in_pausa", motivo) if valore else ("in_corso", None)
        if not valore and self.dal_vivo:
            self.ultimo_marker = (3, "Ripresa alle 16.05")

    def metti_il_motivo(self, motivo):
        self.motivo = motivo

    def capitoli_passati(self):
        return 0

    def ferma(self):
        self.comandi.append("ferma")
        self.stato = "finita"
        os.makedirs(os.path.dirname(self.percorso), exist_ok=True)
        open(self.percorso, "wb").close()
        return self.percorso

    def salva_in_fretta(self):
        self.comandi.append("in fretta")
        self.stato = "finita"
        return [self.percorso]

    def elimina(self):
        self.comandi.append("elimina")
        self.stato = "eliminata"

    def cade(self):
        """La connessione della diretta cade, come fa Registrazione con alla_caduta."""
        self.stato, self.motivo = "in_pausa", "rete"
        self.alla_caduta(self, 5.0)


@pytest.fixture
def con_registrazioni(finestra, monkeypatch):
    """Una radio che suona per finta, la registrazione finta, il lavoro in
    disparte subito e l'attesa della sorgente senza margine."""
    import finestra as modulo

    _Finta.create = []
    monkeypatch.setattr(modulo.registrazioni, "Registrazione", _Finta)
    for nome in ("registrazioni_in_disparte", "radio_in_disparte"):
        monkeypatch.setattr(modulo, nome, lambda lavoro, al_termine: al_termine(lavoro()))
    monkeypatch.setattr(modulo.wx, "CallAfter", lambda funzione, *argomenti, **chiavi: funzione(*argomenti, **chiavi))
    monkeypatch.setattr(modulo.wx, "CallLater", lambda _ms, funzione, *argomenti: funzione(*argomenti))
    monkeypatch.setattr(modulo, "ATTESA_DELLA_SORGENTE", 0)
    bloccati = []
    monkeypatch.setattr(modulo, "_blocca_lo_spegnimento", lambda _finestra, testo: bloccati.append(testo) or True)
    monkeypatch.setattr(modulo, "_sblocca_lo_spegnimento", lambda _finestra: bloccati.append(None) or True)
    monkeypatch.setattr(finestra.motore, "suona", lambda *argomenti, **chiavi: None)
    brano = Brano(RADIO, titolo="Rai Radio 3", radio={"uuid": "u", "paese": "IT", "bitrate": 320})
    stato = {"in_corso": None, "in_pausa": False}
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda self: stato["in_corso"]))
    monkeypatch.setattr(type(finestra.motore), "in_pausa", property(lambda self: stato["in_pausa"]))
    monkeypatch.setattr(type(finestra.motore), "caratteristiche", lambda self: (320, 2, 48000))
    orologio = [1000.0]
    finestra._orologio_delle_registrazioni = lambda: orologio[0]
    return types.SimpleNamespace(brano=brano, stato=stato, orologio=orologio, bloccati=bloccati)


def _suona_la_radio(finestra, radio, brano=None):
    # Il motore finto suona subito: l'attesa di Alt con R la trova gia' partita.
    brano = brano or radio.brano
    radio.stato["in_corso"], radio.stato["in_pausa"] = brano.percorso, False
    finestra.archivio.metti_la_radio(brano)
    finestra._suona(finestra.archivio.radio, brano)


def test_registrare_una_radio(finestra, con_registrazioni, suoni_annotati):
    from test_finestra import _premi

    assert _premi(finestra, "r").startswith("Nessuna registrazione. Maiuscolo con R registra")
    assert _premi(finestra, "r", maiuscolo=True).startswith("Non suona niente da registrare") and suoni_annotati[-1] == "non_disponibile"
    finestra.coda.imposta(None, Brano(r"C:\musica\a.mp3"))
    con_registrazioni.stato["in_corso"] = r"C:\musica\a.mp3"
    assert _premi(finestra, "r", maiuscolo=True) == "a.mp3 è un file, già sul disco: si registrano le radio e gli indirizzi in rete."
    _suona_la_radio(finestra, con_registrazioni)
    assert _premi(finestra, "r", maiuscolo=True) == "Registro Rai Radio 3, in MP3 a 128 kbps, stereo, 44.1 kHz. Ctrl con R la ferma."
    reg = _Finta.create[-1]
    assert suoni_annotati[-1] == "registrazione_avviata" and reg.flusso.dal_vivo and reg.dal_vivo and reg.comandi == ["avvia"]
    assert _premi(finestra, "r").startswith("Registro Rai Radio 3, 12:34, 12 MB, in MP3")
    assert _premi(finestra, "r", maiuscolo=True).startswith("Registrazione in pausa: Rai Radio 3, 12:34") and suoni_annotati[-1] == "registrazione_in_pausa"
    assert reg.motivo == "mano"
    assert _premi(finestra, "r").startswith("Registrazione in pausa")
    assert _premi(finestra, "r", maiuscolo=True).startswith("Registrazione ripresa") and reg.comandi[-2:] == [("pausa", True), ("pausa", False)]
    assert _premi(finestra, "r", ctrl=True).startswith("Registrazione finita: Rai Radio 3, 12:34, 12 MB") and suoni_annotati[-1] == "registrazione_fermata"
    assert finestra._registrazione is None and reg.comandi[-1] == "ferma" and not finestra._in_chiusura
    conti = finestra._statistiche.dati["conti"]
    assert conti["registrazioni_avviate"] == 1 and conti["registrazioni_finite"] == 1 and conti["secondi_registrati"] == 754
    assert _premi(finestra, "r", ctrl=True) == "Non c'è una registrazione da fermare."
    # Il ramo Registrazioni ha il file, e Ctrl e Maiuscolo con R ci portano.
    assert _premi(finestra, "r", ctrl=True, maiuscolo=True) == "Registrazioni: 1 file."
    assert finestra._voce_corrente() == finestra.nodo_registrazioni and suoni_annotati[-1] == "alle_registrazioni"
    finestra.albero.Expand(finestra.nodo_registrazioni)
    assert [finestra.albero.GetItemText(v) for v in finestra._figli(finestra.nodo_registrazioni)] == ["Rai Radio 3.mp3"]
    # La sezione Le registrazioni delle statistiche (3.9.2).
    righe = statistiche.Pagina(finestra._statistiche, "", None, None, {}, {}, {}).le_registrazioni()
    assert righe[0] == "Registrazioni avviate: 1, di cui partite dall'attesa di Alt con R 0; file prodotti: 1, con 12 minuti e 34 secondi e 12 MB."
    assert "In media una registrazione dura 12 minuti e 34 secondi e pesa 12 MB." in righe
    assert "Dalle dirette, come le radio: 1; dalle puntate e dai video, che finiscono da soli: 0." in righe
    assert "Per formato: MP3 1." in righe and any(r.startswith("La registrazione più lunga: 12 minuti e 34 secondi, di Rai Radio 3") for r in righe)
    assert not any(r.startswith("Registrazioni avviate") for r in statistiche.Pagina(finestra._statistiche, "", None, None, {}, {}, {}).le_playlist())


def test_alt_con_r_e_un_interruttore(finestra, con_registrazioni, monkeypatch, suoni_annotati):
    # Alt con R accende e spegne l'attesa, ognuna con il suo suono; Alt e
    # Maiuscolo con R serve solo a eliminare (Gabriele, 15 novembre 2026).
    from test_finestra import _premi

    assert _premi(finestra, "r", alt=True).startswith("Attesa accesa: registro le radio e gli indirizzi in rete che suonano") and suoni_annotati[-1] == "registrazione_in_ascolto"
    assert _premi(finestra, "r").startswith("Attesa accesa")
    assert _premi(finestra, "r", alt=True, maiuscolo=True) == "Non c'è una registrazione in corso da eliminare." and suoni_annotati[-1] == "non_disponibile"
    assert finestra._in_ascolto
    assert _premi(finestra, "r", alt=True).startswith("Attesa spenta") and suoni_annotati[-1] == "registrazione_attesa_spenta" and not finestra._in_ascolto
    # Accesa con una radio che suona gia', la registra subito, e resta accesa.
    _suona_la_radio(finestra, con_registrazioni)
    assert finestra._registrazione is None
    _premi(finestra, "r", alt=True)
    reg = _Finta.create[-1]
    assert reg.titolo == "Rai Radio 3" and finestra._registrazione is reg and finestra._in_ascolto and suoni_annotati[-1] == "registrazione_avviata"
    assert _premi(finestra, "r").endswith("Ctrl con R la ferma. L'attesa è accesa.")
    risposta = [False]
    monkeypatch.setattr(finestra, "_conferma", lambda *argomenti: risposta[0])
    assert _premi(finestra, "r", alt=True, maiuscolo=True) == "La registrazione continua."
    risposta[0] = True
    assert _premi(finestra, "r", alt=True, maiuscolo=True) == "Registrazione di Rai Radio 3 eliminata." and reg.comandi[-1] == "elimina"
    assert finestra._registrazione is None and suoni_annotati[-1] == "registrazione_eliminata" and finestra._in_ascolto
    # L'attesa non ricomincia la sorgente eliminata finche' non ne suona un'altra.
    finestra._guarda_le_registrazioni()
    assert len(_Finta.create) == 1
    # Spenta con una registrazione in corso, la chiude e la salva.
    _suona_la_radio(finestra, con_registrazioni, Brano(RADIO_2, titolo="Rai Radio 2", radio={"uuid": "v"}))
    seconda = _Finta.create[-1]
    assert seconda.titolo == "Rai Radio 2"
    _premi(finestra, "r", alt=True)
    assert seconda.comandi[-1] == "ferma" and "registrazione_attesa_spenta" in suoni_annotati[-3:] and suoni_annotati[-1] == "registrazione_fermata"
    conti = finestra._statistiche.dati["conti"]
    assert conti["registrazioni_in_ascolto"] == 2 and conti["attese_spente"] == 2 and conti["registrazioni_dall_attesa"] == 2
    righe = statistiche.Pagina(finestra._statistiche, "", None, None, {}, {}, {}).le_registrazioni()
    assert "L'attesa di Alt con R: accesa 2 volte, spenta 2 volte." in righe
    # Ctrl e Alt con R aprono la cartella.
    aperte = []
    import finestra as modulo

    monkeypatch.setattr(modulo.os, "startfile", aperte.append, raising=False)
    assert _premi(finestra, "r", ctrl=True, alt=True).startswith("Apro la cartella delle registrazioni") and aperte == [registrazioni.cartella()]


def test_l_eliminazione_ricontrolla_dopo_la_domanda(finestra, con_registrazioni, monkeypatch, suoni_annotati):
    # Mentre la domanda e' aperta la registrazione finisce da se': il Si' non
    # cancella un file gia' salvato e contato.
    from test_finestra import _premi

    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]

    def finisce_intanto(*_argomenti):
        reg.stato = "completa"
        reg.al_termine(reg)
        return True

    monkeypatch.setattr(finestra, "_conferma", finisce_intanto)
    assert _premi(finestra, "r", alt=True, maiuscolo=True) == "La registrazione di Rai Radio 3 intanto non è più in corso: non la elimino."
    assert "elimina" not in reg.comandi and finestra._statistiche.dati["conti"]["registrazioni_finite"] == 1


def test_ctrl_con_r_spegne_anche_l_attesa(finestra, con_registrazioni, suoni_annotati):
    from test_finestra import _premi

    _premi(finestra, "r", alt=True)
    assert _premi(finestra, "r", ctrl=True) == "Attesa spenta: non c'era una registrazione da fermare." and suoni_annotati[-1] == "registrazione_attesa_spenta"
    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    reg = _Finta.create[-1]
    assert _premi(finestra, "r", ctrl=True).startswith("Registrazione finita: Rai Radio 3") and not finestra._in_ascolto and reg.comandi[-1] == "ferma"
    assert "Chiudo la registrazione di Rai Radio 3, e l'attesa si spegne." in [r.rsplit(" ", 1)[0] for r in finestra._righe]


def test_l_attesa_segue_la_sorgente_senza_i_silenzi(finestra, con_registrazioni, suoni_annotati):
    """Il lettore in pausa, fermo o su un file: la registrazione della diretta
    va in pausa da se', senza suono; la stessa sorgente la riprende nello
    stesso file, con il marker della ripresa; un'altra sorgente chiude il file
    e ne comincia uno suo. La pausa a mano vince su quella automatica."""
    from test_finestra import _premi

    stato = con_registrazioni.stato
    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    reg = _Finta.create[-1]
    assert reg.comandi == ["avvia"]
    stato["in_pausa"] = True
    suonati = len(suoni_annotati)
    finestra._guarda_le_registrazioni()
    assert reg.comandi[-1] == ("pausa", True) and reg.motivo == "sorgente" and len(suoni_annotati) == suonati
    assert finestra._righe[-1].startswith("La registrazione di Rai Radio 3, 12:34, 12 MB aspetta che la sorgente torni a suonare.")
    assert _premi(finestra, "r").startswith("La registrazione di Rai Radio 3, 12:34, 12 MB aspetta che la sorgente torni a suonare.")
    finestra._guarda_le_registrazioni()
    assert reg.comandi[-1] == ("pausa", True)
    stato["in_pausa"] = False
    finestra._guarda_le_registrazioni()
    assert reg.comandi[-1] == ("pausa", False) and reg.motivo is None and len(suoni_annotati) == suonati
    assert finestra._righe[-1].startswith("Registro Rai Radio 3, marker 3: Ripresa alle 16.05, a 12:34.")
    # Fermo e poi su un file: sempre in pausa, mai un file nuovo.
    stato["in_corso"] = None
    finestra._guarda_le_registrazioni()
    finestra.coda.imposta(None, Brano(r"C:\musica\a.mp3"))
    stato["in_corso"] = r"C:\musica\a.mp3"
    finestra._guarda_le_registrazioni()
    assert reg.comandi[-1] == ("pausa", True) and len(_Finta.create) == 1
    # La pausa a mano vince: la sorgente che torna non la riprende.
    assert _premi(finestra, "r", maiuscolo=True).startswith("Registrazione in pausa: Rai Radio 3") and reg.motivo == "mano"
    _suona_la_radio(finestra, con_registrazioni)
    finestra._guarda_le_registrazioni()
    assert reg.stato == "in_pausa" and reg.motivo == "mano"
    assert _premi(finestra, "r", maiuscolo=True).startswith("Registrazione ripresa") and reg.stato == "in_corso"
    # Un'altra sorgente: il file di prima si chiude, e ne comincia uno suo.
    _suona_la_radio(finestra, con_registrazioni, Brano(RADIO_2, titolo="Rai Radio 2", radio={"uuid": "v"}))
    assert reg.comandi[-1] == "ferma" and _Finta.create[-1].titolo == "Rai Radio 2" and finestra._registrazione is _Finta.create[-1]
    conti = finestra._statistiche.dati["conti"]
    assert conti["pause_automatiche"] == 2 and conti["riprese_automatiche"] == 1 and conti["registrazioni_dall_attesa"] == 2


def test_una_puntata_scarica_intera_in_disparte(finestra, con_registrazioni, suoni_annotati):
    # Le puntate le scarica il registratore: la pausa dell'ascolto non le
    # tocca, e un'altra sorgente le lascia finire di scaricare in disparte.
    from test_finestra import _premi

    video = Brano("https://www.youtube.com/watch?v=prova", titolo="Il video di prova")
    indirizzi.metti_il_diretto(video.percorso)
    _premi(finestra, "r", alt=True)
    con_registrazioni.stato["in_corso"] = video.percorso
    finestra.coda.imposta(None, video)
    finestra._guarda_le_registrazioni()
    puntata = _Finta.create[-1]
    assert not puntata.dal_vivo
    con_registrazioni.stato["in_pausa"] = True
    finestra._guarda_le_registrazioni()
    assert puntata.comandi == ["avvia"]
    _suona_la_radio(finestra, con_registrazioni)
    assert puntata in finestra._in_chiusura and puntata.comandi == ["avvia"] and _Finta.create[-1].titolo == "Rai Radio 3"
    assert "Salvo in disparte: Il video di prova, che scarica ancora." in _premi(finestra, "r")
    puntata.stato = "completa"
    puntata.al_termine(puntata)
    assert puntata not in finestra._in_chiusura and "è arrivata alla fine" in finestra._righe[-1]
    # Finita la puntata mentre suona ancora, l'attesa non la riscarica.
    finestra.coda.imposta(None, video)
    con_registrazioni.stato.update(in_corso=video.percorso, in_pausa=False)
    finestra._registrazione = None
    finestra._da_non_registrare = video.percorso
    finestra._guarda_le_registrazioni()
    assert finestra._registrazione is None


def test_la_rete_che_cade_si_ricollega(finestra, con_registrazioni, monkeypatch, suoni_annotati):
    """La connessione del registratore cade mentre il lettore suona: si
    ricollega da se', nello stesso file. Con il lettore fermo e' una pausa
    automatica. Dopo cinque tentativi falliti la registrazione finisce."""
    from test_finestra import _premi

    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    reg = _Finta.create[-1]
    reg.cade()
    assert reg.comandi[-1] == ("pausa", False) and reg.stato == "in_corso" and reg.riprove == 1
    assert finestra._righe[-1].startswith("La registrazione di Rai Radio 3 si è ricollegata")
    assert finestra._statistiche.dati["conti"]["ricollegamenti_delle_registrazioni"] == 1
    con_registrazioni.stato["in_pausa"] = True
    reg.cade()
    assert reg.motivo == "sorgente" and reg.stato == "in_pausa"
    con_registrazioni.stato["in_pausa"] = False
    finestra._guarda_le_registrazioni()
    assert reg.stato == "in_corso"
    # I ricollegamenti che falliscono: 1, 2, 5, 10 e 30 secondi, poi basta.
    attese = []
    import finestra as modulo

    monkeypatch.setattr(modulo.wx, "CallLater", lambda ms, funzione, *argomenti: attese.append(ms) or funzione(*argomenti))

    def non_riapre(valore, motivo="mano", flusso=None):
        reg.comandi.append(("pausa", valore))
        raise OSError("il server non risponde")

    monkeypatch.setattr(reg, "pausa", non_riapre)
    reg.riprove = 0
    reg.cade()
    assert attese == [1000, 2000, 5000, 10000, 30000] and reg.comandi[-1] == "ferma" and finestra._registrazione is None
    assert finestra._righe[-1].startswith("La registrazione di Rai Radio 3 si è interrotta: il flusso non risponde più") and suoni_annotati[-1] == "errore"
    # La sorgente che non risponde non si riprova finche' non ne suona un'altra.
    finestra._guarda_le_registrazioni()
    assert finestra._registrazione is None


def test_i_marker_e_gli_avvisi_senza_suono(finestra, con_registrazioni, suoni_annotati):
    from test_finestra import _premi

    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    reg = _Finta.create[-1]
    suonati = len(suoni_annotati)
    reg.al_marker(reg, 4, "Lucio Dalla - Caruso", 3735.0)
    assert finestra._righe[-1].startswith("Registro Rai Radio 3, marker 4: Lucio Dalla - Caruso, a 1:02:15.")
    # Ogni dieci minuti, anche in pausa automatica e con la sola attesa.
    con_registrazioni.orologio[0] += 599
    finestra._guarda_le_registrazioni()
    assert finestra._righe[-1].startswith("Registro Rai Radio 3, marker 4")
    con_registrazioni.orologio[0] += 1
    finestra._guarda_le_registrazioni()
    assert finestra._righe[-1].startswith("Registro Rai Radio 3: 12:34, 12 MB.")
    con_registrazioni.orologio[0] += 600
    finestra._guarda_le_registrazioni()
    assert finestra._righe[-1].startswith("Registro Rai Radio 3: 12:34, 12 MB.") and finestra._righe[-2].startswith("Registro Rai Radio 3, marker 4")
    # Ctrl con R chiude e spegne l'attesa; riaccesa con niente che suona, avvisa lei.
    _premi(finestra, "r", ctrl=True)
    con_registrazioni.stato["in_corso"] = None
    _premi(finestra, "r", alt=True)
    finestra._guarda_le_registrazioni()
    suonati = len(suoni_annotati)
    con_registrazioni.orologio[0] += 600
    finestra._guarda_le_registrazioni()
    assert finestra._righe[-1].startswith("Attesa accesa: registro la prossima radio") and len(suoni_annotati) == suonati
    assert finestra._statistiche.dati["conti"]["avvisi_delle_registrazioni"] == 4


def test_i_marker_finiscono_sul_file_registrato(finestra, con_registrazioni, monkeypatch, tmp_path):
    """Chiusa la registrazione, i suoi marker diventano marker di MeTeOra sul
    file finale, con la chiave della durata dello schedario e il nome del
    titolo; un nome vuoto e' M e il numero."""
    from test_finestra import _premi

    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    reg.percorso = os.path.join(registrazioni.cartella(), "Rai Radio 3.wav")
    vera = reg.ferma

    def ferma():
        vera()
        _seno(reg.percorso, 3.0)
        reg.marker_finali = [(reg.percorso, 0.0, "Radio 3 Suite"), (reg.percorso, 1.5, ""), (reg.percorso, 2.0, "Mina - Azzurro")]
        return reg.percorso

    reg.ferma = ferma
    assert _premi(finestra, "r", ctrl=True).startswith("Registrazione finita: Rai Radio 3, 12:34, 12 MB, con 3 marker.")
    k = finestra._chiave_dei_marker(reg.percorso, leggi=True)
    assert k.endswith("|3.000") and [(m["tempo"], m["nome"]) for m in finestra.marcatori.elenco(k)] == [(0.0, "Radio 3 Suite"), (1.5, "M1"), (2.0, "Mina - Azzurro")]
    assert finestra._statistiche.dati["conti"]["marker_delle_registrazioni"] == 3


def test_la_chiusura_aspetta_il_salvataggio(finestra, con_registrazioni, monkeypatch, suoni_annotati):
    """Chiudere MeTeOra con una registrazione aperta: la chiusura si rifiuta,
    il lettore si ferma, l'attesa si spegne e la registrazione si salva in
    disparte; un altro Esc ridice il suono e a che punto e'; finito il
    salvataggio, MeTeOra si chiude da se'."""
    from test_finestra import _premi, _ultima

    import finestra as modulo

    lavori = []
    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: lavori.append((lavoro, al_termine)))
    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    reg = _Finta.create[-1]
    fermati = []
    monkeypatch.setattr(finestra, "_ferma", lambda sfumando: fermati.append(sfumando) or con_registrazioni.stato.update(in_corso=None))
    finestra.Close()
    assert not finestra._chiusa and suoni_annotati[-1] == "chiusura_in_attesa" and fermati == [False] and not finestra._in_ascolto
    assert finestra._registrazione is None and finestra._in_chiusura == [reg] and len(lavori) == 1
    assert finestra._righe[-1].startswith("MeTeOra si chiude appena le registrazioni sono salvate. Salvo in disparte: Rai Radio 3.")
    assert con_registrazioni.bloccati == ["MeTeOra sta salvando le registrazioni, e si chiude da sé appena ha finito."]
    reg.avanzamento = 0.45
    finestra.Close()
    assert not finestra._chiusa and suoni_annotati[-2:] == ["chiusura_in_attesa", "chiusura_in_attesa"] and _ultima(finestra).endswith("Salvo in disparte: Rai Radio 3, 45%.")
    # Shift con R non comincia niente mentre si chiude.
    assert _premi(finestra, "r", maiuscolo=True).startswith("MeTeOra si sta chiudendo")
    reg.avanzamento = None
    lavoro, al_termine = lavori.pop()
    al_termine(lavoro())
    assert finestra._chiusa and reg.comandi[-1] == "ferma" and con_registrazioni.bloccati[-1] is None
    conti = finestra._statistiche.dati["conti"]
    assert conti["chiusure_rimandate"] == 1 and conti["registrazioni_salvate_alla_chiusura"] == 1


def test_l_aggiornamento_e_lo_spegnimento_aspettano(finestra, con_registrazioni, monkeypatch):
    import wx

    import finestra as modulo

    lavori = []
    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: lavori.append((lavoro, al_termine)))
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    # Windows chiede di spegnersi: no, finche' si salva.
    evento = wx.CloseEvent(wx.wxEVT_QUERY_END_SESSION)
    evento.SetCanVeto(True)
    finestra._spegnimento_chiesto(evento)
    assert evento.GetVeto() and not finestra._chiusa and finestra._chiusura_chiesta == "normale"
    # L'aggiornamento chiude a forza: si rimanda anche lui, e poi chiude a forza.
    finestra.chiudi_per_aggiornare()
    assert not finestra._chiusa and finestra._chiusura_chiesta == "forzata"
    chiuse = []
    monkeypatch.setattr(finestra, "Close", lambda force=False: chiuse.append(force))
    lavoro, al_termine = lavori.pop()
    al_termine(lavoro())
    assert chiuse == [True] and reg.comandi[-1] == "ferma"


def test_lo_spegnimento_che_non_aspetta_salva_le_parti(finestra, con_registrazioni):
    # EVT_END_SESSION, o una chiusura forzata: le parti si salvano subito.
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    finestra.Close(force=True)
    assert reg.comandi[-1] == "in fretta" and finestra._chiusa
    assert finestra._statistiche.dati["conti"]["registrazioni_salvate_alla_chiusura"] == 1


def test_una_radio_caduta_e_le_impostazioni_delle_registrazioni(finestra, con_registrazioni, suoni_annotati):
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    reg.stato = "interrotta"
    reg.al_termine(reg)
    assert finestra._righe[-1].startswith("La registrazione di Rai Radio 3 si è interrotta") and suoni_annotati[-1] == "errore"
    assert finestra._registrazione is None and finestra._statistiche.dati["conti"]["registrazioni_interrotte"] == 1
    assert finestra._riga_dell_impostazione("formato_registrazioni") == "Formato e qualità delle registrazioni: MP3 a 128 kbps, canali della sorgente"
    finestra.impostazioni["formato_registrazioni"] = "flac"
    assert finestra._riga_dell_impostazione("formato_registrazioni") == "Formato e qualità delle registrazioni: FLAC a 16 bit, frequenza della sorgente, canali della sorgente"
    # Una puntata che finisce da se' e' completa.
    finestra.impostazioni["formato_registrazioni"] = "mp3"
    finestra._comando_registra()
    reg = _Finta.create[-1]
    reg.stato = "completa"
    reg.al_termine(reg)
    assert "è arrivata alla fine" in finestra._righe[-1] and suoni_annotati[-1] == "registrazione_fermata"


def test_il_recupero_all_avvio_lo_dice_la_console(finestra, monkeypatch, tmp_path):
    import finestra as modulo

    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: al_termine(lavoro()))
    monkeypatch.setattr(modulo.wx, "CallAfter", lambda funzione, *argomenti, **chiavi: funzione(*argomenti, **chiavi))
    reg = _a_parti(tmp_path, "mp3", [(2.0, 0.0, [(0.5, "Caruso")]), (2.0, 1.0, [])], nome="crollo")
    for numero, parte in enumerate(reg._parti, 1):
        os.replace(parte.file, f"{reg.percorso}.parziale{numero}")
        parte.file = f"{reg.percorso}.parziale{numero}"
    reg._annota()
    finestra._recupera_le_registrazioni()
    assert finestra._righe[-1].startswith(f"Ho recuperato la registrazione di crollo mp3, rimasta a metà da una chiusura improvvisa: 2 parti unite, nel ramo Registrazioni, come "
        f"{os.path.basename(reg.percorso)}.")
    conti = finestra._statistiche.dati["conti"]
    assert conti["registrazioni_recuperate_all_avvio"] == 1 and conti["parti_recuperate_all_avvio"] == 2 and conti["marker_delle_registrazioni"] == 1
    assert not finestra._da_salvare() and not [f for f in os.listdir(os.path.dirname(reg.percorso)) if ".parziale" in f]
    righe = statistiche.Pagina(finestra._statistiche, "", None, None, {}, {}, {}).le_registrazioni()
    assert "Registrazioni recuperate all'avvio, rimaste a metà da una chiusura improvvisa: 1, con 2 parti." in righe


class _DialogoDiCartella:
    """La finestra delle cartelle di Windows, finta: risponde con la cartella data, o annulla."""

    risposte: typing.ClassVar[list] = []
    aperti: typing.ClassVar[list] = []

    def __init__(self, _genitore, titolo, defaultPath="", style=0):
        _DialogoDiCartella.aperti.append((titolo, defaultPath))

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def ShowModal(self):
        import wx

        self.scelta = _DialogoDiCartella.risposte.pop(0)
        return wx.ID_CANCEL if self.scelta is None else wx.ID_OK

    def GetPath(self):
        return self.scelta


def test_la_cartella_delle_registrazioni(finestra, con_registrazioni, monkeypatch, tmp_path):
    # La voce delle impostazioni (Gabriele, 3.13.0): la finestra delle
    # cartelle di Windows, e le registrazioni nuove nella cartella scelta.
    import finestra as modulo

    monkeypatch.setattr(modulo, "DialogoDiCartella", _DialogoDiCartella)
    _DialogoDiCartella.aperti.clear()
    di_sempre = registrazioni.cartella()
    assert finestra._riga_dell_impostazione("cartella_registrazioni") == f"Cartella delle registrazioni: Registrazioni, accanto ai dati di MeTeOra: {di_sempre}"
    scelta = tmp_path / "Le mie registrazioni"
    _DialogoDiCartella.risposte[:] = [None, str(scelta)]
    finestra._cambia_impostazione("cartella_registrazioni", None)

    def riga():
        # L'ultima riga della console, senza l'ora in fondo.
        return finestra._righe[-1].rsplit(" ", 1)[0]

    assert finestra.impostazioni["cartella_registrazioni"] == "" and riga() == "Cartella delle registrazioni non cambiata."
    finestra._cambia_impostazione("cartella_registrazioni", None)
    assert finestra.impostazioni["cartella_registrazioni"] == str(scelta) and scelta.is_dir()
    assert riga() == f"Le registrazioni nuove vanno in {scelta}; quelle di prima restano dove sono."
    assert finestra._riga_dell_impostazione("cartella_registrazioni") == f"Cartella delle registrazioni: {scelta}"
    assert _DialogoDiCartella.aperti[0][0] == "Cartella delle registrazioni"
    # La registrazione nuova va li', e Ctrl e Alt con R aprono quella.
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    assert reg.dove == str(scelta) and os.path.dirname(reg.percorso) == str(scelta)
    aperte = []
    monkeypatch.setattr(modulo.os, "startfile", aperte.append, raising=False)
    finestra._comando_apri_la_cartella_delle_registrazioni()
    assert aperte == [str(scelta)]
    # Con la registrazione in corso, la scelta lo dice; e scegliere quella di
    # sempre la rimette come predefinita.
    _DialogoDiCartella.risposte[:] = [di_sempre]
    finestra._cambia_impostazione("cartella_registrazioni", None)
    assert finestra.impostazioni["cartella_registrazioni"] == "" and riga().endswith("La registrazione in corso finisce dov'è.")
    assert _DialogoDiCartella.aperti[-1][1] == str(scelta)
    finestra._comando_ferma_la_registrazione()
    assert os.path.exists(reg.percorso)
    # Una cartella che non c'e' piu' si dice.
    finestra.impostazioni["cartella_registrazioni"] = str(tmp_path / "staccata")
    assert finestra._riga_dell_impostazione("cartella_registrazioni").endswith("staccata, che non si trova")
    assert finestra._statistiche.dati["conti"]["cartelle_delle_registrazioni_cambiate"] == 2
    righe = statistiche.Pagina(finestra._statistiche, "", None, None, {}, {}, {}).le_registrazioni()
    assert "La cartella delle registrazioni aperta in Esplora risorse: 1 volta; cambiata nelle impostazioni: 2 volte." in righe
    # Vai alla cartella delle registrazioni, nelle impostazioni (3.14.0): come Ctrl e Alt con R.
    assert finestra._riga_dell_impostazione("apri_cartella_registrazioni") == "Vai alla cartella delle registrazioni: la apre in Esplora risorse, come Ctrl e Alt con R"
    finestra.impostazioni["cartella_registrazioni"] = str(scelta)
    finestra._cambia_impostazione("apri_cartella_registrazioni", None)
    assert aperte == [str(scelta), str(scelta)] and finestra._statistiche.dati["conti"]["cartelle_delle_registrazioni_aperte"] == 2


def test_l_attesa_di_alt_con_r_e_il_brano_che_entra_con_il_passaggio(finestra, con_registrazioni):
    # Il seguente di una playlist di indirizzi, preparato, entra con il
    # passaggio senza essere suonato da capo: con l'attesa di Alt con R si
    # registra anche lui (3.13.2; prima no), e l'attesa resta accesa.
    import finestra as modulo

    file = Brano(r"C:\m\a.mp3")
    video = Brano("https://www.youtube.com/watch?v=prova", titolo="Il video di prova")
    indirizzi.metti_il_diretto(video.percorso)
    pl = modulo.Playlist("Video", [file, video], cartella="")
    finestra.coda.imposta(pl, file)
    finestra._in_ascolto = True
    finestra._uscente, finestra._preparato = (pl, file, None), (pl, video, None)
    con_registrazioni.stato["in_corso"] = video.percorso
    finestra._passaggio(video.percorso, None)
    assert finestra.coda.corrente is video and finestra._registrazione is _Finta.create[-1]
    assert _Finta.create[-1].sorgente == video.percorso and finestra._in_ascolto


def test_la_console_dice_le_parti_che_non_si_sono_unite(finestra, con_registrazioni, suoni_annotati):
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    reg.parti_separate = [os.path.join(registrazioni.cartella(), "Rai Radio 3 parte 1.mp3"), os.path.join(registrazioni.cartella(), "Rai Radio 3 parte 2.mp3")]
    finestra._registrazione_fermata(reg, reg.parti_separate[0])
    assert finestra._righe[-1].startswith("Le parti della registrazione di Rai Radio 3 non si sono unite: sono 2 file, nel ramo Registrazioni, come Rai Radio 3 parte 1.mp3.")
    assert suoni_annotati[-1] == "errore" and finestra._statistiche.dati["conti"]["registrazioni_a_parti_separate"] == 1


class _ListeInFila:
    """Le liste delle impostazioni, finte: rispondono una dopo l'altra con le
    righe date, None per Escape, e annotano titolo, righe e riga di partenza."""

    def __init__(self, *risposte):
        self.risposte, self.aperte = list(risposte), []

    def __call__(self, _genitore, titolo, righe, scelta, con_filtro=False):
        self.aperte.append((titolo, list(righe), scelta))
        self._risposta = self.risposte.pop(0)
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def ShowModal(self):
        import wx

        return wx.ID_CANCEL if self._risposta is None else wx.ID_OK

    def GetSelection(self):
        return self.aperte[-1][1].index(self._risposta)


def test_formato_e_qualita_a_due_passi(finestra, con_registrazioni, monkeypatch):
    # La voce unica (Gabriele, 3.15.0): il formato, poi i suoi parametri.
    import finestra as modulo

    imp = finestra.impostazioni
    # WAV: bit, frequenza e canali, ognuno sulla scelta di adesso.
    liste = _ListeInFila("WAV, senza perdita e senza compressione", "32 bit in virgola mobile, che non satura mai: solo WAV", "48 kHz", "Sempre stereo")
    monkeypatch.setattr(modulo, "FinestraScelta", liste)
    finestra._cambia_impostazione("formato_registrazioni", None)
    assert [a[0] for a in liste.aperte] == ["Formato e qualità delle registrazioni", "Bit delle registrazioni in WAV", "Frequenza delle registrazioni in WAV",
        "Canali delle registrazioni in WAV"]
    assert [a[2] for a in liste.aperte] == [0, 0, 0, 0] and len(liste.aperte[1][1]) == 3
    assert (imp["formato_registrazioni"], imp["bit_registrazioni"], imp["frequenza_registrazioni"], imp["canali_registrazioni"]) == ("wav", 32, 48000, "stereo")
    assert finestra._righe[-1].startswith("Le registrazioni ora sono in WAV a 32 bit in virgola mobile, 48 kHz, stereo.")
    # FLAC non ha i 32 bit, e parte dai 24; Escape a meta' lascia tutto com'era.
    liste = _ListeInFila("FLAC, senza perdita e compresso", "24 bit, per la post-produzione", None)
    monkeypatch.setattr(modulo, "FinestraScelta", liste)
    finestra._cambia_impostazione("formato_registrazioni", None)
    assert len(liste.aperte[1][1]) == 2 and liste.aperte[1][2] == 1 and liste.aperte[2][2] == 2
    assert imp["formato_registrazioni"] == "wav" and finestra._righe[-1].startswith("Formato e qualità delle registrazioni non cambiati.")
    # MP3: kbps e canali.
    liste = _ListeInFila("MP3, il più diffuso", "192 kbps", "Sempre mono")
    monkeypatch.setattr(modulo, "FinestraScelta", liste)
    finestra._cambia_impostazione("formato_registrazioni", None)
    assert [a[0] for a in liste.aperte][1:] == ["Kbps delle registrazioni in MP3", "Canali delle registrazioni in MP3"]
    assert (imp["formato_registrazioni"], imp["qualita_registrazioni"], imp["canali_registrazioni"]) == ("mp3", 192, "mono")
    assert finestra._riga_dell_impostazione("formato_registrazioni") == "Formato e qualità delle registrazioni: MP3 a 192 kbps, mono"
    assert finestra._statistiche.dati["conti"]["formati_delle_registrazioni_scelti"] == 2
    # La registrazione riceve i parametri: mono da una sorgente stereo, con meta' dei kbps.
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    assert (reg.formato, reg.kbps, reg.canali) == ("mp3", 96, 1)
