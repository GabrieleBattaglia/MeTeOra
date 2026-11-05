# MeTeOra, prototipi: quali formati del WAV uno speaker Cast suona bene, a spezzoni dello stesso passaggio.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 2.7.3, dal collaudo di Gabriele: su GabryBar il WAV in RAM a 24 bit e 96 kHz gracchiava.

"""La prova dei formati del WAV sullo speaker.

Uso, dalla cartella di MeTeOra, con MeTeOra chiuso e il via di Gabriele:
  python prototipi\\prova_formati_wav.py BRANO SPEAKER [--inizio S] [--secondi S] [--solo-prepara]

Dallo stesso passaggio del brano fa sei spezzoni, in WAV con
l'intestazione di MeTeOra o con quella estesa di Windows, e uno in FLAC, e
li manda allo speaker uno dopo l'altro, come file, con il server di
trasmissione.py. Chi ascolta conta gli spezzoni e dice quali gracchiano; i
formati li dice la prova solo alla fine, a schermo e in coda a
prototipi/wav_a_finestra_misure.txt.
"""

import argparse
import datetime
import os
import shutil
import socket
import struct
import sys
import tempfile
import threading
import time

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)
MISURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wav_a_finestra_misure.txt")
# Gli spezzoni, nell'ordine in cui suonano: (frequenza, bit, intestazione).
SPEZZONI = [(48000, 16, "pcm"), (96000, 24, "pcm"), (96000, 16, "pcm"), (48000, 24, "pcm"), (96000, 24, "estesa"), (96000, 24, "flac")]
# Il formato PCM dentro l'intestazione estesa, KSDATAFORMAT_SUBTYPE_PCM.
PCM_ESTESO = bytes.fromhex("0100000000001000800000aa00389b71")


def intestazione_estesa(totale, frequenza, bit, canali=2):
    """L'intestazione WAVE_FORMAT_EXTENSIBLE, quella che Windows vuole oltre i
    16 bit: 68 byte, con i bit validi e i canali davanti a sinistra e destra."""
    passo = canali * bit // 8
    formato = struct.pack("<HHIIHH", 0xFFFE, canali, frequenza, frequenza * passo, passo, bit) + struct.pack("<HHI", 22, bit, 3) + PCM_ESTESO
    return b"RIFF" + struct.pack("<I", 4 + 8 + len(formato) + 8 + totale) + b"WAVE" + b"fmt " + struct.pack("<I", len(formato)) + formato + b"data" + struct.pack("<I", totale)


def converti(mpv, opzioni_di_base, brano, uscita, inizio, secondi, frequenza, bit, formato):
    """Il passaggio del brano in uscita con libmpv in modo codifica: PCM
    grezzo, come il convertitore di MeTeOra, oppure FLAC."""
    a_24 = bit == 24
    if formato == "flac":
        opzioni = {"of": "flac", "oac": "flac"}
    else:
        opzioni = {"of": "s24le" if a_24 else "s16le", "oac": "pcm_s24le" if a_24 else "pcm_s16le"}
    fatto = threading.Event()
    codifica = mpv.MPV(**{**opzioni_di_base, **opzioni, "o": uscita, "audio_samplerate": frequenza, "audio_format": "s32" if a_24 else "s16",
        "audio_channels": "stereo", "start": str(inizio), "length": str(secondi)})
    codifica.register_event_callback(lambda e: fatto.set() if e.event_id.value == mpv.MpvEventID.END_FILE else None)
    codifica.command("loadfile", os.path.abspath(brano))
    fatto.wait(120)
    codifica.terminate()


def prepara(cartella, brano, inizio, secondi):
    import librerie  # noqa: F401 - le DLL di libmpv, prima del motore
    import motore
    import wav_in_ram

    spezzoni = []
    for numero, (frequenza, bit, formato) in enumerate(SPEZZONI, 1):
        grezzo = os.path.join(cartella, f"grezzo_{numero}.pcm")
        if formato == "flac":
            percorso = os.path.join(cartella, f"spezzone_{numero}.flac")
            converti(motore.mpv, motore.OPZIONI_DI_BASE, brano, percorso, inizio, secondi, frequenza, bit, formato)
        else:
            converti(motore.mpv, motore.OPZIONI_DI_BASE, brano, grezzo, inizio, secondi, frequenza, bit, formato)
            with open(grezzo, "rb") as f:
                pcm = f.read()
            os.remove(grezzo)
            pcm = pcm[:len(pcm) // (bit // 4) * (bit // 4)]
            testa = wav_in_ram.intestazione(len(pcm), frequenza, bit) if formato == "pcm" else intestazione_estesa(len(pcm), frequenza, bit)
            percorso = os.path.join(cartella, f"spezzone_{numero}.wav")
            with open(percorso, "wb") as f:
                f.write(testa + pcm)
        spezzoni.append((percorso, frequenza, bit, formato, os.path.getsize(percorso)))
    return spezzoni


def principale():
    parser = argparse.ArgumentParser(description="Quali formati del WAV uno speaker Cast suona bene.")
    parser.add_argument("brano")
    parser.add_argument("speaker")
    parser.add_argument("--inizio", type=float, default=70.0)
    parser.add_argument("--secondi", type=float, default=12.0)
    parser.add_argument("--solo-prepara", action="store_true", help="fa gli spezzoni e li descrive, senza suonarli")
    argomenti = parser.parse_args()
    cartella = tempfile.mkdtemp(prefix="meteora_formati_")
    registro = open(MISURE, "a", encoding="utf-8")  # noqa: SIM115 - resta aperto per tutta la prova
    partenza = time.perf_counter()

    def scrivi(testo, a_schermo=True):
        registro.write(f"{time.perf_counter() - partenza:9.3f} {testo}\n")
        registro.flush()
        if a_schermo:
            print(testo, flush=True)

    try:
        scrivi(f"Prova dei formati del WAV del {datetime.datetime.now():%d/%m/%Y %H:%M}, su {socket.gethostname()}: "
            f"{os.path.basename(argomenti.brano)}, da {argomenti.inizio:g} secondi per {argomenti.secondi:g}.", a_schermo=False)
        spezzoni = prepara(cartella, argomenti.brano, argomenti.inizio, argomenti.secondi)
        if argomenti.solo_prepara:
            for numero, (percorso, frequenza, bit, formato, dimensione) in enumerate(spezzoni, 1):
                with open(percorso, "rb") as f:
                    testa = f.read(80)
                print(f"{numero}: {os.path.basename(percorso)}, {frequenza} Hz, {bit} bit, {formato}, {dimensione} byte, testa {testa[:44].hex()}")
            return 0
        risultati = _suona(spezzoni, argomenti, scrivi)
        for numero, ((_p, frequenza, bit, formato, _d), esito) in enumerate(zip(spezzoni, risultati, strict=True), 1):
            scrivi(f"Spezzone {numero}: {frequenza} Hz, {bit} bit, {formato}; {esito}.")
    finally:
        registro.close()
        shutil.rmtree(cartella, ignore_errors=True)
    return 0


def _suona(spezzoni, argomenti, scrivi):
    import trasmissione

    ricerca = trasmissione.Ricerca()
    ricerca.avvia()
    risultati = []
    try:
        voce = None
        scadenza = time.monotonic() + 15
        while voce is None and time.monotonic() < scadenza:
            voce = next((v for v in ricerca.apparecchi() if v["nome"].lower() == argomenti.speaker.lower()), None)
            time.sleep(0.2)
        if voce is None:
            scrivi(f"Non trovo {argomenti.speaker}.")
            return ["non suonato"] * len(spezzoni)
        server = trasmissione.Server(trasmissione.indirizzo_verso(voce["indirizzo"]), 0, al_registro=lambda riga: scrivi(riga, a_schermo=False))
        stati = []
        apparecchio = ricerca.connetti(voce["uuid"], allo_stato=lambda s: (stati.append((time.perf_counter(), s)), scrivi(f"Stato: {s}.", a_schermo=False)))
        for numero, (percorso, _frequenza, _bit, formato, _dimensione) in enumerate(spezzoni, 1):
            print(f"Spezzone {numero}.", flush=True)
            comando = time.perf_counter()
            tipo = "audio/flac" if formato == "flac" else "audio/wav"
            apparecchio.suona(server.pubblica_file(percorso), tipo, titolo=f"Spezzone {numero}")
            suona = fine = None
            scadenza = comando + argomenti.secondi + 25
            while fine is None and time.perf_counter() < scadenza:
                for quando, stato in list(stati):
                    if quando < comando:
                        continue
                    if suona is None and stato["stato"] == trasmissione.IN_RIPRODUZIONE:
                        suona = quando - comando
                        continue
                    # La fine conta solo dopo la partenza: prima lo speaker
                    # dice IDLE senza motivo, mentre carica.
                    if stato["stato"] == trasmissione.FERMO and ((suona is not None and quando - comando > suona) or stato.get("motivo") == "ERROR"):
                        fine = (quando - comando, stato.get("motivo"))
                        break
                time.sleep(0.05)
            esito = "non e' partito" if suona is None else f"partito dopo {suona:.2f} secondi"
            esito += ", nessuna fine" if fine is None else f", finito dopo {fine[0]:.2f} secondi, motivo {fine[1]}"
            risultati.append(esito)
            time.sleep(3)
        apparecchio.chiudi()
        server.ferma()
    finally:
        ricerca.ferma()
    return risultati


if __name__ == "__main__":
    raise SystemExit(principale())
