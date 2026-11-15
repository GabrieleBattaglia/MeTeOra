# MeTeOra, le prove delle registrazioni: libmpv vero su file locali, niente rete.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 10/11/2026: nasce con la 3.5.0, issue 42. Nella 3.13.0 la cartella delle registrazioni; nella 3.13.2 l'attesa al passaggio e le parti non unite. Nella 3.14.0 la voce che apre la cartella. Nella 3.15.0 i bit veri nei file e la voce a due passi.

import contextlib
import datetime
import itertools
import json
import os
import shutil
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
    # Il taglio cade a fotogrammi: il primo tenuto e' quello che comincia dal
    # secondo chiesto, senza il fotogramma in piu' di prima della revisione.
    fotogramma = 1152 / 44100
    tolti = -(-round(1.0 * 44100) // 1152) * fotogramma
    assert abs(reg.secondi - (2.0376 + 3.0 + 0.03 + 3.0 + 0.03 - tolti)) < 0.06
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
    minima rinomina il marker di prima; i doppioni delle connessioni nuove non
    contano; il richiamo dice numero, nome e secondi del marker sul file,
    senza il lucchetto. Dalla revisione del 15 novembre 2026 il marker si
    dice una volta sola, quando il suo nome e' fermo, con il titolo vero e
    non con il segnaposto; un titolo gia' andato in onda da poco non fa un
    marker nuovo, contro l'alternanza del nome della radio e del brano; e il
    titolo arrivato prima dell'audio di una ripresa va nel suo marker."""
    orologio = [1000.0]
    monkeypatch.setattr(registrazioni.time, "monotonic", lambda: orologio[0])
    detti, riprese = [], []
    reg = registrazioni.Registrazione(RADIO, "Rai Radio 3", indirizzi.Flusso(RADIO, dal_vivo=True), dove="non usata",
        al_marker=lambda r, numero, nome, secondi: detti.append((numero, nome, secondi)), alla_ripresa=lambda r, motivo: riprese.append(motivo))
    monkeypatch.setattr(reg, "_annota", lambda: None)
    parte = registrazioni.Parte("x.parziale1")
    parte.partita = orologio[0]
    reg._parte = parte
    reg._posizione(parte, 1.5)
    reg._titolo_nella_parte(parte, "Radio 3 Suite")
    orologio[0] += 5
    reg._posizione(parte, 6.0)
    reg._titolo_nella_parte(parte, "Lucio  Dalla - Caruso")
    # Il nome non e' ancora fermo: niente da dire. La prima parte ha l'audio.
    assert detti == [] and riprese == [None]
    orologio[0] += 60
    reg._posizione(parte, 66.0)
    assert detti == [(1, "Lucio Dalla - Caruso", 0.0)]
    reg._titolo_nella_parte(parte, "Lucio Dalla - Caruso")
    reg._titolo_nella_parte(parte, "Mina - Azzurro")
    reg._titolo_nella_parte(registrazioni.Parte("vecchia"), "Da una parte chiusa")
    assert parte.marker == [[0.0, "Lucio Dalla - Caruso", False, "Lucio Dalla - Caruso"], [66.0, "Mina - Azzurro", False, "Mina - Azzurro"]]
    # L'alternanza: il nome della radio e il brano di prima, gia' andati in
    # onda, non fanno marker, ne' righe; un brano nuovo si'.
    for passo, titolo in enumerate(["Radio 3 Suite", "Mina - Azzurro", "Radio 3 Suite", "Mina - Azzurro", "Radio 3 Suite", "Battiato - La cura"]):
        orologio[0] += 30
        reg._posizione(parte, 96.0 + 30 * passo)
        reg._titolo_nella_parte(parte, titolo)
    assert [voce[1] for voce in parte.marker] == ["Lucio Dalla - Caruso", "Mina - Azzurro", "Battiato - La cura"] and reg.numero_dei_marker == 3
    assert detti == [(1, "Lucio Dalla - Caruso", 0.0), (2, "Mina - Azzurro", 66.0)]
    orologio[0] += 20
    reg._posizione(parte, 266.0)
    assert detti[-1] == (3, "Battiato - La cura", 246.0)
    # La ripresa: un titolo arrivato con la riserva, prima dell'audio, va nel
    # suo marker, che si dice subito, sul tempo del file dopo la prima parte.
    parte.secondi, parte.finita = 266.0, orologio[0]
    reg._parti = [parte]
    nuova = registrazioni.Parte("x.parziale2")
    nuova.ripresa, nuova.partita = "sorgente", orologio[0]
    reg._parte = nuova
    reg._titolo_nella_parte(nuova, "Franco Battiato - Centro di gravità")
    assert nuova.marker == [] and reg.numero_dei_marker == 3
    reg._posizione(nuova, 0.5)
    assert nuova.marker[0][1].startswith("Ripresa alle ") and nuova.marker[0][1].endswith(": Franco Battiato - Centro di gravità") and reg.numero_dei_marker == 4
    assert detti[-1][0] == 4 and detti[-1][2] == 266.0 and riprese == [None, "sorgente"]
    # Un titolo subito dopo si aggiunge alla ripresa, senza un marker nuovo ne' una riga.
    reg._titolo_nella_parte(nuova, "Lucio Dalla - Futura")
    assert nuova.marker[0][1].endswith(": Lucio Dalla - Futura") and len(detti) == 4
    # Un ricollegamento non ha marker: dice solo che l'audio e' arrivato.
    rete = registrazioni.Parte("x.parziale3")
    rete.ripresa = "rete"
    reg._parte = rete
    reg._posizione(rete, 0.3)
    assert rete.marker == [] and riprese == [None, "sorgente", "rete"] and rete.viva and rete.ultimo_dato == orologio[0]


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


def test_una_connessione_rifiutata_si_dice_anche_subito(tmp_path):
    # Un server che rifiuta subito la connessione: la fine arrivava prima che
    # la registrazione fosse in corso, non contava, e la registrazione restava
    # viva senza flusso. Ora la caduta si dice, all'avvio e al ricollegamento.
    presa = socket.socket()
    presa.bind(("127.0.0.1", 0))
    porta = presa.getsockname()[1]
    presa.close()
    indirizzo = f"http://127.0.0.1:{porta}/stream"
    cadute = []
    caduta = threading.Event()
    reg = registrazioni.Registrazione(indirizzo, "Muta", indirizzi.Flusso(indirizzo, dal_vivo=True), "mp3", 64, 1, 44100, dove=str(tmp_path / "Registrazioni"),
        alla_caduta=lambda r, secondi: cadute.append(secondi) or caduta.set())
    for _volta in range(3):
        caduta.clear()
        if reg.stato == "pronta":
            reg.avvia()
        else:
            reg.pausa(False)
        assert caduta.wait(15) and (reg.stato, reg.motivo) == ("in_pausa", "rete")
    assert len(cadute) == 3 and not reg._parti
    assert reg.ferma() is None and not os.path.exists(reg.percorso + registrazioni.FILE_DELLE_PARTI)


def _server_icy(audio, metaint, titoli, pausa=0.5, riserva=2):
    """Un server ICY in locale: a ogni connessione manda l'audio diviso in
    blocchi da metaint, con un titolo dopo ognuno; i primi riserva blocchi
    subito, come la riserva di una radio vera, poi uno ogni pausa secondi,
    al passo dell'orologio: 4000 byte ogni mezzo secondo sono 64 kbps
    (revisione del 15 novembre 2026: prima un blocco ogni 0.15 secondi, tre
    volte piu' veloce dell'orologio, e senza riserva). Poi chiude. Torna la porta."""
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
                for numero, i in enumerate(range(0, len(audio), metaint)):
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
                    if numero >= riserva - 1:
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
    sorgente = _registrata(tmp_path, "da servire", 4.0)
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
    # Secondi e byte sono quelli di tutte le parti, con la loro riserva: prima i secondi erano zero.
    assert reg.secondi == pytest.approx(4.0) and reg.byte == sum(os.path.getsize(f) for f in file)


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
    assert all(os.path.exists(f) for f in reg.parti_separate) and not os.path.exists(uno) and not os.path.exists(due) and reg.secondi == pytest.approx(5.0)
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
    """Una registrazione finta: annota i comandi, e ferma dice il suo file.
    Come la vera, la ripresa e il ricollegamento si dicono quando la parte
    nuova riceve l'audio: lo fa arriva(), con alla_ripresa e, per una
    diretta, il marker della ripresa (revisione del 15 novembre 2026)."""

    create: typing.ClassVar[list] = []

    def __init__(self, sorgente, titolo, flusso, formato, kbps, canali, frequenza, al_termine=None, dove=None, bit=None, dal_vivo=None, al_marker=None,
            alla_caduta=None, capitoli=(), alla_ripresa=None, da_riconoscere=False):
        self.sorgente, self.titolo, self.flusso = sorgente, titolo, flusso
        self.formato, self.kbps, self.canali, self.frequenza, self.al_termine = formato, kbps, canali, frequenza, al_termine
        self.dal_vivo = getattr(flusso, "dal_vivo", True) if dal_vivo is None else dal_vivo
        self.al_marker, self.alla_caduta, self.alla_ripresa, self.capitoli = al_marker, alla_caduta, alla_ripresa, list(capitoli)
        self.da_riconoscere = da_riconoscere
        self.stato, self.secondi, self.byte, self.comandi = "pronta", 754.0, 11_534_336, []
        self.dove, self.bit = dove, registrazioni.bit_per(formato, bit or 16)
        self.percorso = os.path.join(dove or registrazioni.cartella(), f"{titolo}.mp3")
        self.motivo = self.avanzamento = self.salvataggio = self.ripresa = None
        self.marker_finali, self.parti_separate = [], []
        _Finta.create.append(self)

    @property
    def descrizione(self):
        return registrazioni.descrizione(self.formato, self.kbps, self.canali, self.frequenza, self.bit)

    @property
    def file_finali(self):
        return [self.percorso] if os.path.exists(self.percorso) else []

    def avvia(self):
        self.comandi.append("avvia")
        self.stato = "in_corso"

    def pausa(self, valore, motivo="mano", flusso=None):
        self.comandi.append(("pausa", valore))
        prima = self.motivo
        self.stato, self.motivo = ("in_pausa", motivo) if valore else ("in_corso", None)
        if not valore:
            self.ripresa = prima or "mano"

    def arriva(self):
        """La parte nuova della ripresa riceve l'audio."""
        motivo, self.ripresa = self.ripresa, None
        if motivo is None:
            return
        if self.dal_vivo and motivo != "rete":
            self.al_marker(self, 3, "Ripresa alle 16.05", 754.0)
        self.alla_ripresa(self, motivo)

    def metti_il_motivo(self, motivo):
        self.motivo = motivo

    def capitoli_passati(self):
        return getattr(self, "passati", 0)

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

    def cade(self, secondi=5.0):
        """La connessione della diretta cade, come fa Registrazione con
        alla_caduta: secondi zero per un tentativo che non ha ricevuto niente."""
        self.stato, self.motivo, self.ripresa = "in_pausa", "rete", None
        self.alla_caduta(self, secondi)


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
    # La ripresa si conta, e il suo marker si dice, quando la parte nuova riceve l'audio.
    assert finestra._statistiche.dati["conti"].get("riprese_automatiche", 0) == 0
    reg.arriva()
    assert finestra._righe[-1].startswith("Registro Rai Radio 3, marker 3: Ripresa alle 16.05, a 12:34.") and len(suoni_annotati) == suonati
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


def test_una_puntata_scarica_intera_e_un_altra_sorgente_la_chiude(finestra, con_registrazioni, suoni_annotati):
    """Le puntate le scarica il registratore: la pausa dell'ascolto non le
    tocca. Un'altra sorgente invece chiude il file, anche della puntata, con
    quello che ha scaricato, come chiede il compito (revisione del 15 novembre
    2026: prima la lasciava finire in disparte, e tornandoci se ne scaricava
    un'altra copia, in parallelo). Una puntata finita mentre suona ancora non
    si riscarica. La scheda con la durata dice che non e' una diretta."""
    from test_finestra import _premi

    video = Brano("https://www.youtube.com/watch?v=prova", titolo="Il video di prova")
    indirizzi.metti_il_diretto(video.percorso)
    finestra.schedario.metti_la_scheda(video.percorso, {"durata": 600.0})
    _premi(finestra, "r", alt=True)
    con_registrazioni.stato["in_corso"] = video.percorso
    finestra.coda.imposta(None, video)
    finestra._guarda_le_registrazioni()
    puntata = _Finta.create[-1]
    assert not puntata.dal_vivo and not puntata.da_riconoscere
    con_registrazioni.stato["in_pausa"] = True
    finestra._guarda_le_registrazioni()
    assert puntata.comandi == ["avvia"]
    # A, poi la radio B, poi di nuovo A: la prima copia di A e' chiusa, mai due in corso.
    _suona_la_radio(finestra, con_registrazioni)
    assert puntata.comandi == ["avvia", "ferma"] and puntata not in finestra._in_chiusura and _Finta.create[-1].titolo == "Rai Radio 3"
    con_registrazioni.stato.update(in_corso=video.percorso, in_pausa=False)
    finestra.coda.imposta(None, video)
    finestra._guarda_le_registrazioni()
    vive = [r for r in _Finta.create if r.sorgente == video.percorso and r.stato == "in_corso"]
    assert vive == [finestra._registrazione] and not finestra._in_chiusura
    seconda = finestra._registrazione
    seconda.stato = "completa"
    seconda.al_termine(seconda)
    assert "è arrivata alla fine" in finestra._righe[-1] and finestra._registrazione is None
    # Finita la puntata mentre suona ancora, l'attesa non la riscarica, e R lo dice.
    finestra._guarda_le_registrazioni()
    assert finestra._registrazione is None and len(_Finta.create) == 3
    assert _premi(finestra, "r") == "Attesa accesa: non registro di nuovo Il video di prova, finché non suona un'altra sorgente. Alt con R spegne l'attesa."


def test_la_ripresa_a_mano_con_la_sorgente_che_tace(finestra, con_registrazioni, suoni_annotati):
    # Con l'attesa accesa e la sorgente in pausa, Maiuscolo con R toglie la
    # pausa a mano e la rimette ad aspettare la sorgente, senza aprire niente.
    from test_finestra import _premi

    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    reg = _Finta.create[-1]
    _premi(finestra, "r", maiuscolo=True)
    con_registrazioni.stato["in_pausa"] = True
    finestra._guarda_le_registrazioni()
    assert reg.motivo == "mano"
    assert _premi(finestra, "r", maiuscolo=True) == "Registrazione ripresa: Rai Radio 3 riparte appena la sorgente torna a suonare."
    assert suoni_annotati[-1] == "registrazione_ripresa" and reg.motivo == "sorgente" and reg.comandi[-1] == ("pausa", True)
    con_registrazioni.stato["in_pausa"] = False
    finestra._guarda_le_registrazioni()
    assert reg.comandi[-1] == ("pausa", False) and reg.stato == "in_corso"


def test_i_capitoli_di_una_puntata_si_dicono_senza_inondare(finestra, con_registrazioni, suoni_annotati):
    # Una puntata scarica piu' veloce dell'ascolto: una riga dice l'ultimo
    # capitolo passato, al piu' ogni dieci secondi, e il primo non si dice.
    video = Brano("https://www.youtube.com/watch?v=capitoli", titolo="Puntata")
    indirizzi.metti_il_diretto(video.percorso)
    finestra.schedario.metti_la_scheda(video.percorso, {"durata": 600.0, "capitoli": [[0.0, "Sigla"], [60.0, "Intervista"], [120.0, ""], [300.0, "Saluti"]]})
    con_registrazioni.stato["in_corso"] = video.percorso
    finestra.coda.imposta(None, video)
    finestra._comando_registra()
    puntata = _Finta.create[-1]
    assert not puntata.dal_vivo and [c[1] for c in puntata.capitoli] == ["Sigla", "Intervista", "", "Saluti"]
    righe = len(finestra._righe)
    puntata.passati = 3
    finestra._guarda_le_registrazioni()
    assert finestra._righe[-1].startswith("Registro Puntata, marker 3: capitolo 3, a 2:00.") and len(finestra._righe) == righe + 1
    puntata.passati = 4
    con_registrazioni.orologio[0] += 5
    finestra._guarda_le_registrazioni()
    assert len(finestra._righe) == righe + 1
    con_registrazioni.orologio[0] += 5
    finestra._guarda_le_registrazioni()
    assert finestra._righe[-1].startswith("Registro Puntata, marker 4: Saluti, a 5:00.") and suoni_annotati[-1] == "registrazione_avviata"


def test_la_chiusura_aspetta_il_comando_in_volo(finestra, con_registrazioni, monkeypatch, suoni_annotati):
    # Esc mentre la pausa chiude un pezzo: la registrazione si chiude quando
    # il comando ha finito, e poi MeTeOra.
    import finestra as modulo

    lavori = []
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: lavori.append((lavoro, al_termine)))
    finestra._comando_registra()
    assert finestra._registrazione_occupata and len(lavori) == 1
    finestra.Close()
    assert not finestra._chiusa and finestra._registrazione is reg and finestra._da_chiudere == "chiusura"
    lavoro, al_termine = lavori.pop()
    al_termine(lavoro())
    assert finestra._registrazione is None and finestra._in_chiusura == [reg] and len(lavori) == 1
    lavoro, al_termine = lavori.pop()
    al_termine(lavoro())
    assert finestra._chiusa and reg.comandi[-2:] == [("pausa", True), "ferma"]


def test_la_rete_che_cade_si_ricollega(finestra, con_registrazioni, monkeypatch, suoni_annotati):
    """La connessione del registratore cade mentre il lettore suona: si
    ricollega da se', nello stesso file, e lo dice quando la parte nuova
    riceve l'audio. Con il lettore fermo e' una pausa automatica. Dopo cinque
    tentativi falliti la registrazione finisce, e l'attesa la riprova un
    minuto dopo, mentre la sorgente suona."""
    from test_finestra import _premi

    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    reg = _Finta.create[-1]
    reg.cade()
    assert reg.comandi[-1] == ("pausa", False) and reg.stato == "in_corso" and reg.riprove == 1
    assert finestra._righe[-1].startswith("La registrazione di Rai Radio 3 ha perso la connessione: mi ricollego.")
    assert finestra._statistiche.dati["conti"].get("ricollegamenti_delle_registrazioni", 0) == 0
    reg.arriva()
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
    assert finestra._righe[-1].rsplit(" ", 1)[0].endswith("L'attesa ci riprova ogni minuto mentre suona, o appena la fai ripartire.")
    assert finestra._statistiche.dati["conti"]["ricollegamenti_delle_registrazioni"] == 1
    # La sorgente che non risponde si riprova un minuto dopo, se suona ancora, con un file nuovo.
    finestra._guarda_le_registrazioni()
    assert finestra._registrazione is None and len(_Finta.create) == 1
    assert _premi(finestra, "r").startswith("Attesa accesa, ma la registrazione di Rai Radio 3 non è riuscita: ci riprovo ogni minuto mentre suona")
    con_registrazioni.orologio[0] += 60
    finestra._guarda_le_registrazioni()
    seconda = _Finta.create[-1]
    assert len(_Finta.create) == 2 and finestra._registrazione is seconda and finestra._statistiche.dati["conti"]["riprove_dell_attesa"] == 1

    def non_risponde(valore, motivo="mano", flusso=None):
        raise OSError("il server non risponde")

    # Il tentativo nuovo non riceve niente: fallisce in silenzio, senza file, e l'attesa riprova ancora.
    monkeypatch.setattr(seconda, "pausa", non_risponde)
    monkeypatch.setattr(seconda, "ferma", lambda: seconda.comandi.append("ferma"))
    righe = len(finestra._righe)
    seconda.cade(0.0)
    assert finestra._registrazione is None and len(finestra._righe) == righe and finestra._non_riuscita[2] == 2 and seconda.comandi[-1] == "ferma"
    # Quando l'audio arriva, la sorgente si registra di nuovo davvero.
    con_registrazioni.orologio[0] += 60
    finestra._guarda_le_registrazioni()
    terza = _Finta.create[-1]
    assert terza is not seconda and finestra._non_riuscita is not None
    terza.alla_ripresa(terza, None)
    assert finestra._non_riuscita is None


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


# La revisione del 15 novembre 2026: le prove dei due revisori, portate nel ramo.


def _linea_del_tempo(percorso, secondi, frequenza=44100):
    """Un WAV in cui il secondo k e' un tono di 400 + 50 k Hz: nel file
    registrato si riconosce ogni secondo, e un buco o un doppione si vede."""
    t = np.arange(frequenza) / frequenza
    campioni = (np.concatenate([0.25 * np.sin(2 * np.pi * (400 + 50 * k) * t) for k in range(secondi)]) * 32767).astype("<i2")
    with wave.open(str(percorso), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(frequenza)
        f.writeframes(campioni.tobytes())
    return str(percorso)


def _secondi_presenti(percorso, frequenza=44100):
    """Per ogni mezzo secondo di un WAV registrato, il secondo della linea del tempo che vi suona."""
    with wave.open(percorso, "rb") as f:
        dati = np.frombuffer(f.readframes(f.getnframes()), dtype="<i2").astype(float) / 32768
    finestra = frequenza // 2
    trovati = []
    for inizio in range(0, len(dati) - finestra, finestra):
        spettro = np.abs(np.fft.rfft(dati[inizio:inizio + finestra] * np.hanning(finestra)))
        trovati.append(round((np.argmax(spettro) * frequenza / finestra - 400) / 50))
    return trovati


def _glissando(percorso, secondi, hz, frequenza=44100):
    """Un glissando da hz a quattro volte hz: nessun pezzo somiglia a un altro, e l'allineamento e' uno solo."""
    t = np.arange(int(frequenza * secondi)) / frequenza
    campioni = (0.25 * np.sin(2 * np.pi * (hz * t + 3 * hz * t * t / (2 * secondi))) * 32767).astype("<i2")
    with wave.open(str(percorso), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(frequenza)
        f.writeframes(campioni.tobytes())
    return str(percorso)


def _decodificato(percorso):
    """I campioni di un file decodificato da libmpv, da -1 a 1."""
    uscita = percorso + ".pcm.wav"
    finita = threading.Event()
    lettore = mpv.MPV(**{**motore.OPZIONI_DI_BASE, "o": uscita, "of": "wav", "oac": "pcm_s16le"})
    lettore.register_event_callback(lambda e: finita.set() if e.event_id.value == mpv.MpvEventID.END_FILE else None)
    lettore.command("loadfile", percorso)
    assert finita.wait(30)
    lettore.terminate()
    with wave.open(uscita, "rb") as f:
        return np.frombuffer(f.readframes(f.getnframes()), dtype="<i2").astype(float) / 32768


class _LibmpvFinto:
    """Il libmpv di una parte, finto: annota i comandi, e non apre niente."""

    def __init__(self, **opzioni):
        self.opzioni, self.comandi, self.time_pos = opzioni, [], None

    def __setitem__(self, chiave, valore):
        pass

    def register_event_callback(self, funzione):
        self.evento = funzione

    def observe_property(self, nome, funzione):
        pass

    def register_stream_protocol(self, schema, funzione):
        pass

    def command(self, *argomenti):
        self.comandi.append(argomenti)

    def terminate(self):
        pass


class _Rimando:
    """Un wx.CallLater finto, che parte quando la coda della prova lo raggiunge, se non e' fermato."""

    def __init__(self, funzione, argomenti):
        self.funzione, self.argomenti, self.fermo = funzione, argomenti, False

    def Stop(self):
        self.fermo = True

    def __call__(self):
        if not self.fermo:
            self.funzione(*self.argomenti)


def _come_il_vero(lavoro, al_termine):
    """registrazioni_in_disparte come la vera, ma nel filo della prova: l'errore del lavoro e' l'esito."""
    try:
        esito = lavoro()
    except Exception as e:  # noqa: BLE001 - come registrazioni_in_disparte
        esito = e
    al_termine(esito)


def test_le_opzioni_della_codifica_scrivono_ogni_pacchetto():
    # flush_packets: la parte in corso cresce sul disco a ogni pacchetto, e
    # dopo un crollo c'e' tutta; la riscrittura dell'unione non ne ha bisogno.
    assert registrazioni._codifica("mp3", 128, None)["ofopts"] == "flush_packets=1"
    assert registrazioni._codifica("wav", None, 24)["ofopts"] == "rf64=auto,flush_packets=1"
    assert registrazioni._codifica("opus", 96, None)["ofopts"] == "flush_packets=1,page_duration=200000"
    assert "ofopts" not in registrazioni._codifica("flac", None, 16, svuota=False)
    assert registrazioni._codifica("wav", None, 16, svuota=False)["ofopts"] == "rf64=auto"


def test_registrazioni_in_disparte_porta_anche_gli_errori():
    # Un'eccezione del lavoro arriva ad al_termine come esito: prima chiudeva
    # il filo senza dirlo, e la chiusura di MeTeOra aspettava per sempre.
    import finestra as modulo

    esiti, fatto = [], threading.Event()

    def rotto():
        raise RuntimeError("libmpv non riparte")

    modulo.registrazioni_in_disparte(rotto, lambda esito: esiti.append(esito) or fatto.set())
    assert fatto.wait(5) and isinstance(esiti[0], RuntimeError)


def test_il_buco_di_un_ricollegamento_parte_dall_ultimo_dato(tmp_path, monkeypatch):
    """La rete si pianta senza chiudere: libmpv dice la fine solo dopo
    l'attesa della lettura, quindici secondi dopo l'ultimo dato. Il buco si
    conta dall'ultimo dato, e della riserva della connessione nuova, che
    riporta quei secondi, si toglie solo il doppione; anche il taglio si
    ferma all'ultimo dato mentre non arriva niente (prima si perdevano fino a
    quindici secondi a ogni stallo)."""
    orologio = [100.0]
    monkeypatch.setattr(registrazioni.time, "monotonic", lambda: orologio[0])
    monkeypatch.setattr(registrazioni.mpv, "MPV", _LibmpvFinto)
    reg = registrazioni.Registrazione(RADIO, "x", indirizzi.Flusso(RADIO, dal_vivo=True), dove=str(tmp_path))
    caduta = registrazioni.Parte(str(tmp_path / "x.parziale1"))
    caduta.secondi, caduta.partita, caduta.ultimo_dato, caduta.finita = 6.0, 100.0, 106.0, 121.0
    reg._parti, reg.stato, reg.motivo = [caduta], "in_pausa", "rete"
    orologio[0] = 122.0
    reg.pausa(False)
    nuova = reg._parte
    assert nuova.buco == 16.0 and nuova.ripresa == "rete" and nuova.dati_contati and reg._lettore.comandi[-1][0] == "loadfile"
    # La riserva di 22 secondi, poi 8 al passo dell'orologio: se ne tolgono i
    # 6 doppi. L'ultimo dato lo annota la lettura della rete, non time-pos,
    # che cresce anche quando libmpv decodifica alla fine quello che teneva.
    orologio[0] = 130.0
    reg._posizione(nuova, 29.0)
    assert nuova.ultimo_dato == 0.0 and nuova.viva
    nuova.ultimo_dato = 130.0
    reg._posizione(nuova, 30.0)
    assert reg._taglio(nuova, 30.0) == 6.0 and reg.secondi == 30.0
    # La rete si pianta di nuovo: mentre non arriva niente il taglio resta.
    orologio[0] = 145.0
    assert reg._taglio(nuova, 30.0) == 6.0 and reg.secondi == 30.0
    # La lettura della parte annota l'orologio di ogni dato arrivato.
    lettura = registrazioni._LetturaDellaParte(types.SimpleNamespace(read=lambda quanti: b"x" * quanti, close=lambda: None, cancel=lambda: None), nuova)
    assert lettura.read(4) == b"xxxx" and nuova.ultimo_dato == 145.0 and not hasattr(lettura, "seek") and not hasattr(lettura, "size")


def test_la_rete_che_si_pianta_non_perde_i_secondi(tmp_path, monkeypatch):
    """Con libmpv vero e una radio in locale che si pianta senza chiudere,
    poi alla connessione nuova manda otto secondi di riserva: nel file
    registrato ci sono tutti i secondi della linea del tempo, senza buchi e
    senza doppioni (la prova dello stallo del revisore, accorciata: prima
    mancavano i secondi della caduta)."""
    monkeypatch.setattr(registrazioni.diretta, "ATTESA", 1.5)
    origine = _linea_del_tempo(tmp_path / "linea.wav", 16)
    finita = threading.Event()
    mp3 = registrazioni.Registrazione(origine, "linea", indirizzi.Flusso(origine), "mp3", 64, 1, 44100, dove=str(tmp_path / "L"), al_termine=lambda _r: finita.set())
    mp3.avvia()
    assert finita.wait(30)
    with open(mp3.percorso, "rb") as f:
        dati = f.read()
    i = registrazioni._lunghezza_id3(dati)
    # Solo i fotogrammi audio, senza ID3 ne' Info, come una radio: 8000 byte al secondo.
    audio = dati[i + registrazioni.diretta._testa(dati, i)[0]:]
    presa = socket.socket()
    presa.bind(("127.0.0.1", 0))
    presa.listen(4)
    stato = {}

    def una(conn, numero):
        with conn, contextlib.suppress(OSError):
            conn.recv(4096)
            conn.sendall(b"HTTP/1.0 200 OK\r\nContent-Type: audio/mpeg\r\n\r\n")
            if numero == 1:
                stato["partenza"] = time.monotonic()
                for passo in range(12):
                    conn.sendall(audio[passo * 2000:(passo + 1) * 2000])
                    time.sleep(0.25)
                time.sleep(5.0)
                return
            adesso = time.monotonic() - stato["partenza"]
            conn.sendall(audio[max(0, int((adesso - 8.0) * 8000)):int(adesso * 8000)])
            fatto = adesso
            while fatto < adesso + 6.0:
                time.sleep(0.25)
                conn.sendall(audio[int(fatto * 8000):int((fatto + 0.25) * 8000)])
                fatto += 0.25

    def servi():
        for numero in (1, 2):
            try:
                conn, _da = presa.accept()
            except OSError:
                return
            threading.Thread(target=una, args=(conn, numero), daemon=True).start()
        presa.close()

    threading.Thread(target=servi, daemon=True).start()
    indirizzo = f"http://127.0.0.1:{presa.getsockname()[1]}/radio"
    caduta = threading.Event()
    reg = registrazioni.Registrazione(indirizzo, "Piantata", indirizzi.Flusso(indirizzo, dal_vivo=True), "wav", None, 1, 44100, dove=str(tmp_path / "R"),
        alla_caduta=lambda r, s: caduta.set())
    reg.avvia()
    assert caduta.wait(20)
    reg.pausa(False)
    time.sleep(3.0)
    percorso = reg.ferma()
    presenti = _secondi_presenti(percorso)
    assert presenti and presenti[0] == 0 and max(presenti) >= 6 and all(0 <= b - a <= 1 for a, b in itertools.pairwise(presenti)), " ".join(map(str, presenti))


def test_la_registrazione_riconosce_da_se_una_diretta(tmp_path):
    """Una radio aperta con Ctrl con V, che il motore non ha ancora
    riconosciuto: la registrazione la riconosce dal suo libmpv, di rete, che
    non si salta e senza durata, e la sua fine e' una caduta della rete, non
    quella di una puntata. Un file del disco resta quello che e'."""
    sorgente = _registrata(tmp_path, "da riconoscere", 4.0)
    with open(sorgente.percorso, "rb") as f:
        dati = f.read()
    # Solo i fotogrammi audio, come una radio: con l'intestazione Info libmpv sa la durata.
    i = registrazioni._lunghezza_id3(dati)
    audio = dati[i + registrazioni.diretta._testa(dati, i)[0]:]
    porta = _server_icy(audio, 4000, [["Primo"]], riserva=4)
    indirizzo = f"http://127.0.0.1:{porta}/stream"
    cadute = threading.Event()
    reg = registrazioni.Registrazione(indirizzo, "Da riconoscere", indirizzi.Flusso(indirizzo), "mp3", 64, 1, 44100, dove=str(tmp_path / "Registrazioni"),
        alla_caduta=lambda r, s: cadute.set(), da_riconoscere=True)
    assert not reg.dal_vivo
    reg.avvia()
    fine = time.monotonic() + 10
    while not reg.dal_vivo and time.monotonic() < fine:
        time.sleep(0.05)
    assert reg.dal_vivo and reg.capitoli == []
    assert cadute.wait(20) and (reg.stato, reg.motivo) == ("in_pausa", "rete")
    reg.ferma()
    finita = threading.Event()
    locale = registrazioni.Registrazione(sorgente.percorso, "locale", indirizzi.Flusso(sorgente.percorso), "mp3", 64, 1, 44100, dove=str(tmp_path / "Locale"),
        al_termine=lambda _r: finita.set(), da_riconoscere=True)
    locale.avvia()
    assert finita.wait(30) and locale.stato == "completa" and not locale.dal_vivo


def test_la_finestra_chiede_di_riconoscere_solo_le_sorgenti_senza_durata(finestra, con_registrazioni):
    # Un indirizzo aperto con Ctrl con V, che il flusso non dice diretta e la
    # scheda non sa lungo: la registrazione deve riconoscerlo da se'.
    indirizzo = "http://127.0.0.1:9/stream"
    indirizzi.metti_il_diretto(indirizzo)
    con_registrazioni.stato["in_corso"] = indirizzo
    finestra.coda.imposta(None, Brano(indirizzo))
    finestra._comando_registra()
    assert _Finta.create[-1].da_riconoscere and not _Finta.create[-1].dal_vivo
    # La radio, che si sa diretta, no.
    finestra._comando_ferma_la_registrazione()
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    assert not _Finta.create[-1].da_riconoscere and _Finta.create[-1].dal_vivo


def test_il_recupero_toglie_la_parte_vuota_del_crollo(tmp_path):
    """Al crollo la parte appena aperta e' ancora vuota: si toglie, i suoi
    marker vanno in fondo alla parte prima, e il resto si unisce in un file
    solo, con l'intestazione rifatta; prima tutto diventava file separati,
    con un file vuoto. Una registrazione della sola parte vuota non lascia niente."""
    import mutagen

    reg = _a_parti(tmp_path, "mp3", [(2.0, 0.0, [(0.5, "Caruso")])], nome="vuota")
    base = reg.percorso
    os.replace(reg._parti[0].file, base + ".parziale1")
    reg._parti[0].file = base + ".parziale1"
    open(base + ".parziale2", "wb").close()
    in_corso = registrazioni.Parte(base + ".parziale2")
    in_corso.marker = [[1.0, "Azzurro", False, "Azzurro"]]
    reg._parte = in_corso
    reg._annota()
    reg._parte = None
    recuperata = registrazioni.Registrazione.da_recuperare(base)
    assert recuperata.recuperate == 1 and not os.path.exists(base + ".parziale2")
    percorso = recuperata.ferma()
    assert percorso == base and not recuperata.parti_separate and abs(mutagen.File(percorso).info.length - 2.0) < 0.1
    assert [n for _f, _t, n in recuperata.marker_finali] == ["Caruso", "Azzurro"] and abs(recuperata.marker_finali[1][1] - recuperata.secondi) < 0.1
    sola = str(tmp_path / "Registrazioni" / "Sola 2026-11-15 10.00.00.mp3")
    open(sola + ".parziale1", "wb").close()
    assert registrazioni.Registrazione.da_recuperare(sola) is None and not os.path.exists(sola + ".parziale1")
    # Un file delle parti rotto non ferma il recupero.
    rotta = _a_parti(tmp_path, "mp3", [(2.0, 0.0, [])], nome="rotta")
    os.replace(rotta._parti[0].file, rotta.percorso + ".parziale1")
    with open(rotta.percorso + registrazioni.FILE_DELLE_PARTI, "w", encoding="utf-8") as f:
        json.dump({"formato": "mp3", "kbps": "tanti", "frequenza": None, "parti": [{"file": os.path.basename(rotta.percorso) + ".parziale1", "inizio": "x",
            "secondi": [], "taglio": "?", "marker": [["a", "b"]]}], "capitoli": [["mai", "Sigla"]]}, f)
    recuperata = registrazioni.Registrazione.da_recuperare(rotta.percorso)
    assert recuperata.ferma() == rotta.percorso and abs(recuperata.secondi - 2.0) < 0.1


@pytest.mark.parametrize("formato", ["wav", "mp3"])
def test_il_recupero_di_una_parte_ancora_aperta(tmp_path, formato):
    """Un crollo vero, fatto copiando a meta' i file di una registrazione in
    corso da una radio in locale: con flush_packets la parte aperta cresce a
    ogni pacchetto, e il recupero le rifa' l'intestazione, anche da sola.
    Prima il WAV recuperato diceva 48695 secondi, l'MP3 zero, e una parte MP3
    piu' giovane di sedici secondi era vuota."""
    import mutagen

    sorgente = _registrata(tmp_path, f"servita {formato}", 8.0)
    with open(sorgente.percorso, "rb") as f:
        audio = f.read()
    porta = _server_icy(audio, 4000, [["Primo"]])
    indirizzo = f"http://127.0.0.1:{porta}/stream"
    reg = registrazioni.Registrazione(indirizzo, f"Crollo {formato}", indirizzi.Flusso(indirizzo, dal_vivo=True), formato, 64, 1, 44100,
        dove=str(tmp_path / "Registrazioni"), alla_caduta=lambda r, s: None)
    reg.avvia()
    time.sleep(3.0)
    copia = tmp_path / "copia"
    copia.mkdir()
    cartella = os.path.dirname(reg.percorso)
    for nome in os.listdir(cartella):
        if nome.startswith(os.path.basename(reg.percorso)):
            shutil.copy(os.path.join(cartella, nome), copia / nome)
    al_crollo = reg.secondi
    assert os.path.getsize(copia / (os.path.basename(reg.percorso) + ".parziale1")) > 0
    reg.ferma()
    recuperata = registrazioni.Registrazione.da_recuperare(str(copia / os.path.basename(reg.percorso)))
    percorso = recuperata.ferma()
    assert percorso is not None and not recuperata.parti_separate
    durata = mutagen.File(percorso).info.length
    assert abs(durata - recuperata.secondi) < 0.1 and abs(durata - al_crollo) < 1.0, (durata, recuperata.secondi, al_crollo)
    assert abs(_durata(percorso)[0] - durata) < 0.1 and [n for _f, _t, n in recuperata.marker_finali] == ["Primo"]


def test_il_taglio_della_parte_in_corso_si_stima_al_recupero(tmp_path):
    """La parte in corso al crollo non ha il suo taglio nel file delle parti:
    si stima dall'ora vera della partenza e da quella dell'ultima scrittura
    (prima teneva tutta la riserva, venti e piu' secondi doppi alla giunzione)."""
    reg = _a_parti(tmp_path, "wav", [(2.0, 0.0, []), (3.0, 0.0, [])], nome="stima")
    base = reg.percorso
    for numero, parte in enumerate(reg._parti, 1):
        os.replace(parte.file, f"{base}.parziale{numero}")
        parte.file = f"{base}.parziale{numero}"
    prima, seconda = reg._parti
    reg._parti = [prima]
    # La seconda era aperta: tre secondi di file, scritti un secondo dopo la sua partenza.
    seconda.secondi, seconda.partita_ora = 0.0, time.time() - 100.0
    os.utime(seconda.file, (seconda.partita_ora + 1.0, seconda.partita_ora + 1.0))
    reg._parte = seconda
    reg._annota()
    reg._parte = None
    recuperata = registrazioni.Registrazione.da_recuperare(base)
    presenti = registrazioni._audio_della_parte(seconda.file, "wav")
    assert presenti >= 3.0 and recuperata._parti[1].taglio == pytest.approx(presenti - 1.0, abs=0.01)
    recuperata.ferma()
    with wave.open(recuperata.percorso, "rb") as f:
        assert f.getnframes() / f.getframerate() == pytest.approx(3.0, abs=0.05)


def test_la_giunzione_dell_mp3_tagliato(tmp_path):
    """La giunzione dell'MP3 tagliato a fotogrammi, decodificata e confrontata
    con la parte decodificata da sola: sbaglia solo il primo granulo, per il
    serbatoio di bit, senza picchi sopra l'ampiezza. Il fotogramma in piu'
    saltato prima della revisione ne sbagliava tre, con un picco a 0.273."""

    def mp3(nome, origine):
        finita = threading.Event()
        reg = registrazioni.Registrazione(origine, nome, indirizzi.Flusso(origine), "mp3", 64, 1, 44100, dove=str(tmp_path / "R"), al_termine=lambda _r: finita.set())
        reg.avvia()
        assert finita.wait(30)
        return reg.percorso

    uno = mp3("silenzio", _seno(tmp_path / "silenzio.wav", 2.0, hz=0))
    due = mp3("glissando", _glissando(tmp_path / "glissando.wav", 3.0, 660))
    (tmp_path / "U").mkdir()
    unita = registrazioni.Registrazione(RADIO, "giunzione", indirizzi.Flusso(RADIO, dal_vivo=True), "mp3", 64, 1, 44100, dove=str(tmp_path / "U"))
    for file, secondi, taglio in ((uno, 2.0, 0.0), (due, 3.0, 1.0)):
        copia = str(tmp_path / f"parte {len(unita._parti)}.mp3")
        shutil.copy(file, copia)
        parte = registrazioni.Parte(copia)
        parte.secondi, parte.taglio = secondi, taglio
        unita._parti.append(parte)
    unita._unisci()
    onda, sola = _decodificato(unita.percorso), _decodificato(due)
    # La parte da sola allineata sul file unito, lontano dalla giunzione.
    m0, lunghezza = int(2.6 * 44100), 4096
    pezzo = onda[m0:m0 + lunghezza]
    candidati = np.argsort(np.correlate(sola, pezzo, mode="valid"))[-20:]
    migliore = int(min(candidati, key=lambda s: float(np.sum(np.abs(sola[s:s + lunghezza] - pezzo)))))
    scarto = migliore - m0
    assert float(np.sqrt(np.mean((sola[migliore:migliore + lunghezza] - pezzo) ** 2))) < 1e-4
    inizio = int(np.argmax(np.abs(onda[int(1.5 * 44100):]) > 0.02)) + int(1.5 * 44100)
    errori = [float(np.sqrt(np.mean((onda[a:a + 576] - sola[a + scarto:a + 576 + scarto]) ** 2))) for a in range(inizio, inizio + 8 * 576, 576)]
    picco = float(np.max(np.abs(onda[inizio:inizio + 3 * 576])))
    assert max(errori[1:]) < 0.02 and picco <= 0.26, (errori, picco)


def test_la_ripresa_vera_mette_il_marker_sulla_giunzione(tmp_path):
    """Pausa e ripresa di una Registrazione vera, da una radio in locale al
    passo dell'orologio: alla_ripresa arriva quando la parte nuova ha
    l'audio, e il marker della ripresa nasce allora, detto e messo dove
    comincia la seconda parte nel file finale."""
    import mutagen

    sorgente = _registrata(tmp_path, "ripresa vera", 12.0)
    with open(sorgente.percorso, "rb") as f:
        audio = f.read()
    porta = _server_icy(audio, 4000, [["Primo"], ["Primo"]])
    indirizzo = f"http://127.0.0.1:{porta}/stream"
    riprese, detti = [], []
    reg = registrazioni.Registrazione(indirizzo, "Ripresa", indirizzi.Flusso(indirizzo, dal_vivo=True), "mp3", 64, 1, 44100, dove=str(tmp_path / "Registrazioni"),
        alla_caduta=lambda r, s: None, alla_ripresa=lambda r, motivo: riprese.append(motivo), al_marker=lambda r, numero, nome, secondi: detti.append((nome, secondi)))
    reg.avvia()
    time.sleep(3.0)
    reg.pausa(True, motivo="sorgente")
    giunzione = reg.secondi
    reg.pausa(False)
    assert riprese == [None]
    fine = time.monotonic() + 10
    while len(riprese) < 2 and time.monotonic() < fine:
        time.sleep(0.05)
    time.sleep(1.0)
    percorso = reg.ferma()
    assert riprese == [None, "sorgente"]
    nomi = [n for _f, _t, n in reg.marker_finali]
    ripresa = [t for _f, t, n in reg.marker_finali if n.startswith("Ripresa alle ")]
    assert nomi[0] == "Primo" and len(ripresa) == 1 and abs(ripresa[0] - giunzione) < 0.3, (reg.marker_finali, giunzione)
    assert any(n.startswith("Ripresa alle ") and abs(s - giunzione) < 0.3 for n, s in detti)
    assert abs(mutagen.File(percorso).info.length - reg.secondi) < 0.1


def test_il_margine_contro_i_cambi_rapidi(finestra, con_registrazioni, monkeypatch):
    """Il margine di ATTESA_DELLA_SORGENTE, che il fixture mette a zero: una
    pausa di un secondo, e un'altra radio per un secondo, non toccano il file;
    la pausa vera arriva dopo il margine (prova del revisore)."""
    from test_finestra import _premi

    import finestra as modulo

    monkeypatch.setattr(modulo, "ATTESA_DELLA_SORGENTE", 2500)
    in_attesa = []
    monkeypatch.setattr(modulo.wx, "CallLater", lambda ms, funzione, *a: in_attesa.append((con_registrazioni.orologio[0] + ms / 1000, funzione, a)))

    def avanza(secondi, passo=0.5):
        orologio = con_registrazioni.orologio
        fine = orologio[0] + secondi
        while orologio[0] < fine - 1e-9:
            orologio[0] = min(fine, orologio[0] + passo)
            for voce in [v for v in in_attesa if v[0] <= orologio[0] + 1e-9]:
                in_attesa.remove(voce)
                voce[1](*voce[2])
            finestra._guarda_le_registrazioni()

    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    avanza(1.0)
    assert not _Finta.create
    avanza(2.0)
    assert len(_Finta.create) == 1
    reg = _Finta.create[-1]
    con_registrazioni.stato["in_pausa"] = True
    finestra._segui_la_sorgente()
    avanza(1.0)
    con_registrazioni.stato["in_pausa"] = False
    finestra._segui_la_sorgente()
    avanza(5.0)
    assert reg.comandi == ["avvia"]
    _suona_la_radio(finestra, con_registrazioni, Brano(RADIO_2, titolo="Rai Radio 2", radio={"uuid": "v"}))
    avanza(1.0)
    _suona_la_radio(finestra, con_registrazioni)
    avanza(5.0)
    assert reg.comandi == ["avvia"] and len(_Finta.create) == 1
    con_registrazioni.stato["in_pausa"] = True
    finestra._segui_la_sorgente()
    avanza(2.0)
    assert reg.comandi == ["avvia"]
    avanza(1.0)
    assert reg.comandi[-1] == ("pausa", True)


def test_i_ricollegamenti_falliti_non_si_dicono_riusciti(finestra, con_registrazioni, monkeypatch):
    """Come la Registrazione vera, pausa(False) da' solo il loadfile, e la
    connessione rifiutata arriva dopo, come una caduta di zero secondi: prima
    ogni tentativo si diceva ricollegato e si contava (prova D del revisore)."""
    import finestra as modulo

    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]

    def in_disparte(lavoro, al_termine):
        al_termine(lavoro())
        if reg.stato == "in_corso" and reg.ripresa == "rete":
            reg.cade(0.0)

    monkeypatch.setattr(modulo, "registrazioni_in_disparte", in_disparte)
    reg.cade()
    righe = [r for r in finestra._righe if "Rai Radio 3" in r]
    assert not any("ricollegata" in r for r in righe) and sum("ha perso la connessione" in r for r in righe) == 1
    assert finestra._statistiche.dati["conti"].get("ricollegamenti_delle_registrazioni", 0) == 0 and finestra._registrazione is None
    assert reg.comandi.count(("pausa", False)) == 5 and reg.comandi[-1] == "ferma"


def test_un_ricollegamento_vero_che_non_riceve_niente_non_si_dice_riuscito(finestra, monkeypatch, suoni_annotati):
    """Con la Registrazione vera e libmpv vero, nella finestra, una radio che
    accetta la connessione e la chiude senza mandare niente: i cinque
    tentativi falliscono, nessuno si dice riuscito, e la registrazione
    finisce senza file (prova E del revisore, con una porta chiusa, che su
    Windows rifiuta dopo due secondi: prima la console diceva cinque volte
    che si era ricollegata)."""
    import finestra as modulo

    servitore = socket.socket()
    servitore.bind(("127.0.0.1", 0))
    servitore.listen(8)

    def chiudi_subito():
        while True:
            try:
                conn, _da = servitore.accept()
            except OSError:
                return
            conn.close()

    threading.Thread(target=chiudi_subito, daemon=True).start()
    coda = []
    monkeypatch.setattr(modulo.wx, "CallAfter", lambda funzione, *argomenti, **chiavi: coda.append(lambda: funzione(*argomenti, **chiavi)))

    def piu_tardi(_ms, funzione, *argomenti):
        rimando = _Rimando(funzione, argomenti)
        coda.append(rimando)
        return rimando

    monkeypatch.setattr(modulo.wx, "CallLater", piu_tardi)
    monkeypatch.setattr(modulo, "_blocca_lo_spegnimento", lambda *_a: True)
    monkeypatch.setattr(modulo, "_sblocca_lo_spegnimento", lambda *_a: True)
    indirizzo = f"http://127.0.0.1:{servitore.getsockname()[1]}/stream"
    indirizzi.metti_il_diretto(indirizzo, dal_vivo=True)
    stato = {"in_corso": indirizzo, "in_pausa": False}
    monkeypatch.setattr(finestra.motore, "suona", lambda *a, **k: None)
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda self: stato["in_corso"]))
    monkeypatch.setattr(type(finestra.motore), "in_pausa", property(lambda self: stato["in_pausa"]))
    monkeypatch.setattr(type(finestra.motore), "caratteristiche", lambda self: (128, 2, 44100))
    finestra.coda.imposta(None, Brano(indirizzo, titolo="Radio muta"))
    finestra._comando_registra()
    assert isinstance(finestra._registrazione, registrazioni.Registrazione)
    fine = time.monotonic() + 60
    while time.monotonic() < fine and (finestra._registrazione is not None or finestra._in_chiusura):
        while coda:
            coda.pop(0)()
        time.sleep(0.05)
    servitore.close()
    righe = [r for r in finestra._righe if "Radio muta" in r]
    assert finestra._registrazione is None and not finestra._in_chiusura
    assert not any("ricollegata" in r for r in righe) and finestra._statistiche.dati["conti"].get("ricollegamenti_delle_registrazioni", 0) == 0
    assert sum("ha perso la connessione" in r for r in righe) == 1
    assert any(r.startswith("La registrazione di Radio muta si è interrotta: il flusso non risponde, e non era arrivato niente da scrivere.") for r in righe), righe


def test_dopo_una_caduta_l_attesa_registra_di_nuovo_la_stessa_radio(finestra, con_registrazioni, monkeypatch):
    """Attesa accesa, la rete cade e i cinque tentativi falliscono; l'avviso
    dei dieci minuti dice perche' non registra. Il lettore si ferma, e la
    stessa radio riparte con X: l'attesa la registra di nuovo, in un file
    nuovo (prova F del revisore: prima restava esclusa finche' non suonava
    un'altra sorgente, mentre R e l'avviso dicevano che si registrava)."""
    from test_finestra import _premi

    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    reg = _Finta.create[-1]

    def non_riapre(valore, motivo="mano", flusso=None):
        raise OSError("la rete non c'e'")

    monkeypatch.setattr(reg, "pausa", non_riapre)
    reg.cade()
    assert finestra._registrazione is None and finestra._non_riuscita[0] == RADIO
    finestra._ultimo_avviso -= 600
    finestra._guarda_le_registrazioni()
    assert finestra._righe[-1].startswith("Attesa accesa, ma la registrazione di Rai Radio 3 non è riuscita: ci riprovo ogni minuto mentre suona")
    con_registrazioni.stato["in_corso"] = None
    finestra._guarda_le_registrazioni()
    assert finestra._non_riuscita is None and len(_Finta.create) == 1
    _suona_la_radio(finestra, con_registrazioni)
    assert len(_Finta.create) == 2 and finestra._registrazione is _Finta.create[-1] and finestra._in_ascolto


def test_una_puntata_in_pausa_a_mano_riprende_subito(finestra, con_registrazioni, suoni_annotati):
    """Una puntata in pausa a mano, con l'attesa accesa e il lettore in
    pausa: Maiuscolo con R la riprende subito, perche' il suo scaricamento non
    segue l'ascolto; prima si metteva ad aspettare la sorgente, e la ripresa
    diceva una riga rotta, marker 0 (prova B del revisore)."""
    from test_finestra import _premi

    video = Brano("https://www.youtube.com/watch?v=prova", titolo="Il video di prova")
    indirizzi.metti_il_diretto(video.percorso)
    finestra.schedario.metti_la_scheda(video.percorso, {"durata": 600.0})
    _premi(finestra, "r", alt=True)
    con_registrazioni.stato["in_corso"] = video.percorso
    finestra.coda.imposta(None, video)
    finestra._guarda_le_registrazioni()
    puntata = _Finta.create[-1]
    _premi(finestra, "r", maiuscolo=True)
    con_registrazioni.stato["in_pausa"] = True
    finestra._guarda_le_registrazioni()
    assert _premi(finestra, "r", maiuscolo=True).startswith("Registrazione ripresa: Il video di prova, 12:34")
    assert (puntata.stato, puntata.motivo) == ("in_corso", None)
    con_registrazioni.stato["in_pausa"] = False
    finestra._guarda_le_registrazioni()
    assert puntata.comandi == ["avvia", ("pausa", True), ("pausa", False)] and not any("marker 0" in r for r in finestra._righe)


def test_un_errore_nel_salvataggio_non_blocca_la_chiusura(finestra, con_registrazioni, monkeypatch):
    """ferma che solleva qualcosa che non e' OSError: le parti si salvano in
    fretta, e MeTeOra si chiude lo stesso (prova A del revisore: prima la
    registrazione restava fra quelle in chiusura, e Esc ridiceva per sempre il
    suono della chiusura che aspetta)."""
    import finestra as modulo

    lavori = []
    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: lavori.append((lavoro, al_termine)))
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]

    def rotta():
        raise RuntimeError("un errore che non e' OSError")

    reg.ferma = rotta
    monkeypatch.setattr(finestra, "_ferma", lambda sfumando: con_registrazioni.stato.update(in_corso=None))
    finestra.Close()
    assert not finestra._chiusa and len(lavori) == 1
    _come_il_vero(*lavori.pop())
    assert finestra._chiusa and reg.comandi[-1] == "in fretta" and not finestra._in_chiusura


def test_un_errore_nel_recupero_non_blocca_la_chiusura(finestra, monkeypatch):
    # da_recuperare che solleva: il recupero si scala comunque, e la console lo dice.
    import finestra as modulo

    monkeypatch.setattr(modulo, "registrazioni_in_disparte", _come_il_vero)
    monkeypatch.setattr(modulo.wx, "CallAfter", lambda funzione, *argomenti, **chiavi: funzione(*argomenti, **chiavi))
    cartella = registrazioni.cartella()
    os.makedirs(cartella, exist_ok=True)
    with open(os.path.join(cartella, "Rai Radio 3 2026-11-15 10.00.00.mp3.parziale1"), "wb") as f:
        f.write(b"\xff\xfb" + b"\0" * 400)

    def rotta(percorso):
        raise RuntimeError("libmpv non parte")

    monkeypatch.setattr(registrazioni.Registrazione, "da_recuperare", staticmethod(rotta))
    finestra._recupera_le_registrazioni()
    assert finestra._recuperi_in_corso == 0 and not finestra._da_salvare()
    assert finestra._righe[-1].startswith("La registrazione rimasta a metà Rai Radio 3 2026-11-15 10.00.00.mp3 non si recupera: libmpv non parte.")


def test_la_ricerca_delle_registrazioni_rimaste_e_in_disparte(finestra, monkeypatch):
    """All'avvio la ricerca nelle cartelle non gira nel filo della finestra:
    una cartella su un disco di rete che non risponde la fermava. Mentre
    cerca conta fra i recuperi in corso, e la chiusura la aspetta."""
    import finestra as modulo

    lavori, guardate = [], []
    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: lavori.append((lavoro, al_termine)))
    monkeypatch.setattr(modulo.wx, "CallAfter", lambda funzione, *argomenti, **chiavi: funzione(*argomenti, **chiavi))
    monkeypatch.setattr(modulo.registrazioni, "rimaste", lambda cartella: guardate.append(cartella) or [])
    os.makedirs(registrazioni.cartella(), exist_ok=True)
    finestra._recupera_le_registrazioni()
    assert guardate == [] and finestra._recuperi_in_corso == 1 and finestra._da_salvare() and len(lavori) == 1
    lavoro, al_termine = lavori.pop()
    al_termine(lavoro())
    assert guardate == [registrazioni.cartella()] and finestra._recuperi_in_corso == 0 and not finestra._da_salvare()


def test_la_chiusura_rimandata_ricorda_il_punto_da_riprendere(finestra, con_registrazioni, monkeypatch):
    # Il punto da riprendere all'avvio si prende prima di fermare il lettore:
    # prima un file del disco ripartiva da zero.
    import finestra as modulo

    lavori = []
    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: lavori.append((lavoro, al_termine)))
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    stati = iter([{"percorso": r"C:\musica\a.mp3", "posizione": 150.0, "tipo": "file"}, {"percorso": r"C:\musica\a.mp3", "posizione": 0, "tipo": "file"}])
    monkeypatch.setattr(finestra, "_stato_da_riprendere", lambda: next(stati))
    monkeypatch.setattr(finestra, "_ferma", lambda sfumando: con_registrazioni.stato.update(in_corso=None))
    finestra.Close()
    lavoro, al_termine = lavori.pop()
    al_termine(lavoro())
    assert finestra._chiusa and finestra.impostazioni["ripresa"]["posizione"] == 150.0


def test_un_altra_sorgente_chiude_il_file_senza_il_suono_della_fermata(finestra, con_registrazioni, monkeypatch, suoni_annotati):
    """Quando l'attesa passa a un'altra sorgente, la registrazione nuova
    parte, con il suo suono, prima che quella di prima sia salvata: la riga
    di quella finita arriva dopo, senza il suono della fermata, che prima era
    l'ultimo suono mentre si registrava."""
    from test_finestra import _premi

    import finestra as modulo

    lavori = []
    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: lavori.append((lavoro, al_termine)))
    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    _suona_la_radio(finestra, con_registrazioni, Brano(RADIO_2, titolo="Rai Radio 2", radio={"uuid": "v"}))
    assert suoni_annotati[-1] == "registrazione_avviata" and finestra._registrazione.titolo == "Rai Radio 2"
    lavoro, al_termine = lavori.pop(0)
    al_termine(lavoro())
    assert suoni_annotati[-1] == "registrazione_avviata" and "registrazione_fermata" not in suoni_annotati
    assert finestra._righe[-1].startswith("Registrazione finita: Rai Radio 3")


def test_r_e_gli_avvisi_dicono_il_ricollegamento_e_la_pausa_a_mano(finestra, con_registrazioni, monkeypatch):
    """Durante un ricollegamento R e l'avviso dei dieci minuti dicono che si
    ricollega, non che aspetta la sorgente; con l'attesa accesa e la pausa a
    mano l'avviso dice la pausa, non che registra la prossima radio."""
    from test_finestra import _premi

    import finestra as modulo

    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    reg = _Finta.create[-1]
    monkeypatch.setattr(modulo.wx, "CallLater", lambda _ms, funzione, *argomenti: None)
    reg.cade()
    assert _premi(finestra, "r").startswith("La registrazione di Rai Radio 3, 12:34, 12 MB si sta ricollegando alla sorgente.")
    con_registrazioni.orologio[0] += 600
    finestra._guarda_le_registrazioni()
    assert finestra._righe[-1].startswith("La registrazione di Rai Radio 3, 12:34, 12 MB si sta ricollegando alla sorgente.")
    assert _premi(finestra, "r", maiuscolo=True).startswith("Registrazione in pausa: Rai Radio 3") and reg.motivo == "mano"
    con_registrazioni.orologio[0] += 600
    finestra._guarda_le_registrazioni()
    assert finestra._righe[-1].startswith("Registrazione in pausa: Rai Radio 3, 12:34, 12 MB. Maiuscolo con R riprende.")


def test_l_aggiornamento_aspetta_le_registrazioni(finestra, con_registrazioni, monkeypatch, suoni_annotati):
    """Con una registrazione aperta l'aggiornamento non si propone, e si
    ripropone al prossimo avvio; e una chiusura per l'aggiornamento che
    aspetta piu' dello script di GBUtils lascia MeTeOra aperto, perche'
    chiudersi lo lascerebbe chiuso senza aggiornarlo."""
    from test_finestra import _premi

    import finestra as modulo

    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    assert finestra.proponi_l_aggiornamento("3.20.0", "3.21.0", "novità", 120) is False and "domanda" not in suoni_annotati
    assert finestra._righe[-1].startswith("È disponibile MeTeOra 3.21.0: te lo propongo al prossimo avvio, perché ci sono registrazioni da salvare.")
    lavori, chiuse = [], []
    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: lavori.append((lavoro, al_termine)))
    monkeypatch.setattr(finestra, "_ferma", lambda sfumando: con_registrazioni.stato.update(in_corso=None))
    finestra.chiudi_per_aggiornare()
    assert finestra._chiusura_chiesta == "forzata"
    con_registrazioni.orologio[0] += modulo.ATTESA_DELL_AGGIORNAMENTO + 1
    monkeypatch.setattr(finestra, "Close", lambda force=False: chiuse.append(force))
    lavoro, al_termine = lavori.pop()
    al_termine(lavoro())
    assert chiuse == [] and finestra._chiusura_chiesta is None and not finestra._chiusa
    assert finestra._righe[-1].startswith("Registrazioni salvate. L'aggiornamento non ha potuto aspettare tanto: MeTeOra resta aperto")
    assert finestra._statistiche.dati["conti"]["aggiornamenti_rimandati_per_le_registrazioni"] == 2
    righe = statistiche.Pagina(finestra._statistiche, "", None, None, {}, {}, {}).le_registrazioni()
    assert "Aggiornamenti di MeTeOra rimandati al prossimo avvio per non interrompere le registrazioni: 2." in righe
    # MeTeOra resta usabile: si registra di nuovo.
    _suona_la_radio(finestra, con_registrazioni)
    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: al_termine(lavoro()))
    assert _premi(finestra, "r", maiuscolo=True).startswith("Registro Rai Radio 3")


def test_lo_spegnimento_arriva_dall_applicazione(finestra, con_registrazioni, monkeypatch):
    """EVT_QUERY_END_SESSION mandato all'applicazione arriva alla finestra, e
    si rifiuta; EVT_END_SESSION salva subito le parti (prova del revisore)."""
    import wx

    import finestra as modulo

    lavori = []
    monkeypatch.setattr(modulo, "registrazioni_in_disparte", lambda lavoro, al_termine: lavori.append((lavoro, al_termine)))
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    evento = wx.CloseEvent(wx.wxEVT_QUERY_END_SESSION)
    evento.SetCanVeto(True)
    wx.GetApp().ProcessEvent(evento)
    assert evento.GetVeto() and finestra._chiusura_chiesta == "normale" and not finestra._chiusa
    fine = wx.CloseEvent(wx.wxEVT_END_SESSION)
    fine.SetCanVeto(False)
    finestra._spegnimento(fine)
    assert reg.comandi[-1] == "in fretta" and not finestra._da_salvare()


def test_le_parti_recuperate_al_singolare(finestra):
    # Il plurale e' quello delle parti: prima si diceva con 1 parti.
    finestra._statistiche.conta("registrazioni_recuperate_all_avvio")
    finestra._statistiche.conta("parti_recuperate_all_avvio")
    righe = statistiche.Pagina(finestra._statistiche, "", None, None, {}, {}, {}).le_registrazioni()
    assert "Registrazioni recuperate all'avvio, rimaste a metà da una chiusura improvvisa: 1, con 1 parte." in righe
