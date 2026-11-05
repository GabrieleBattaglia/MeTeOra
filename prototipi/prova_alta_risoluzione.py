# MeTeOra, prototipi: il WAV in RAM a 24 bit e 96 kHz su uno speaker Cast, con il percorso vero di MeTeOra.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 2.7.0, dalla domanda di Gabriele sulla qualita' del WAV in RAM.

"""La prova dell'alta risoluzione sullo speaker.

Uso, dalla cartella di MeTeOra, con MeTeOra chiuso e il via di Gabriele:
  python prototipi\\prova_alta_risoluzione.py BRANO SPEAKER [--secondi S]

Dai primi S secondi del brano, 20 se non si dice, fa un AIFF a 24 bit e
96 kHz nella cartella temporanea di Windows, e lo manda allo speaker per la
strada di MeTeOra: motore.sorgente_wav, che ne legge frequenza e bit, il
server di trasmissione.py e il telecomando dell'apparecchio. Dice che
formato ha il WAV in RAM, quanto tarda a suonare, se lo speaker legge la
durata, e come finisce; il dettaglio va in coda a
prototipi/wav_a_finestra_misure.txt.
"""

import argparse
import datetime
import os
import socket
import sys
import tempfile
import threading
import time

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)
MISURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wav_a_finestra_misure.txt")


def principale():
    parser = argparse.ArgumentParser(description="Il WAV in RAM a 24 bit e 96 kHz su uno speaker Cast.")
    parser.add_argument("brano")
    parser.add_argument("speaker")
    parser.add_argument("--secondi", type=float, default=20.0)
    argomenti = parser.parse_args()
    import librerie  # noqa: F401 - le DLL di libmpv, prima del motore
    import motore
    import trasmissione

    registro = open(MISURE, "a", encoding="utf-8")  # noqa: SIM115 - resta aperto per tutta la prova
    partenza = time.perf_counter()

    def scrivi(testo, a_schermo=True):
        registro.write(f"{time.perf_counter() - partenza:9.3f} {testo}\n")
        registro.flush()
        if a_schermo:
            print(testo, flush=True)

    scrivi(f"Prova dell'alta risoluzione del {datetime.datetime.now():%d/%m/%Y %H:%M}, su {socket.gethostname()}.", a_schermo=False)
    alto = os.path.join(tempfile.gettempdir(), "meteora_prova_24_96.aiff")
    fatto = threading.Event()
    codifica = motore.mpv.MPV(**{**motore.OPZIONI_DI_BASE, "o": alto, "of": "aiff", "oac": "pcm_s24be", "audio_samplerate": 96000,
        "audio_format": "s32", "audio_channels": "stereo", "length": str(argomenti.secondi)})
    codifica.register_event_callback(lambda e: fatto.set() if e.event_id.value == motore.mpv.MpvEventID.END_FILE else None)
    codifica.command("loadfile", os.path.abspath(argomenti.brano))
    fatto.wait(60)
    codifica.terminate()
    m = motore.Motore(ao="null")
    ricerca = trasmissione.Ricerca()
    ricerca.avvia()
    try:
        durata, frequenza, bit = m.formato_da_convertire(alto)
        scrivi(f"Sorgente: {os.path.basename(alto)}, {durata:.2f} secondi, WAV in RAM a {bit} bit e {frequenza} Hz.")
        voce = None
        scadenza = time.monotonic() + 15
        while voce is None and time.monotonic() < scadenza:
            voce = next((v for v in ricerca.apparecchi() if v["nome"].lower() == argomenti.speaker.lower()), None)
            time.sleep(0.2)
        if voce is None:
            scrivi(f"Non trovo {argomenti.speaker}.")
            return 1
        server = trasmissione.Server(trasmissione.indirizzo_verso(voce["indirizzo"]), 0, al_registro=lambda riga: scrivi(riga, a_schermo=False))
        stati = []
        apparecchio = ricerca.connetti(voce["uuid"], allo_stato=lambda s: (stati.append((time.perf_counter(), s)), scrivi(f"Stato: {s}.", a_schermo=False)))
        sorgente = m.sorgente_wav(alto)
        indirizzo = server.pubblica_sorgente(sorgente)
        comando = time.perf_counter()
        apparecchio.suona(indirizzo, sorgente.tipo, titolo="Prova a 24 bit e 96 kHz")
        suona = fine = None
        scadenza = time.perf_counter() + durata + 40
        while fine is None and time.perf_counter() < scadenza:
            for quando, stato in list(stati):
                if quando < comando:
                    continue
                if suona is None and stato["stato"] == trasmissione.IN_RIPRODUZIONE:
                    suona = (quando - comando, stato.get("durata"))
                    continue
                # La fine conta solo dopo la partenza: prima lo speaker dice
                # IDLE senza motivo, mentre carica.
                dopo = suona is not None and quando - comando > suona[0]
                if stato["stato"] == trasmissione.FERMO and (dopo or stato.get("motivo") == "ERROR"):
                    fine = (quando - comando, stato.get("motivo"), stato.get("codice"))
                    break
            time.sleep(0.05)
        if suona is not None:
            scrivi(f"Suona dopo {suona[0]:.2f} secondi; lo speaker dice che dura {suona[1]} secondi.")
        else:
            scrivi("Lo speaker non ha cominciato a suonare.")
        scrivi(f"Fine: {'nessuna' if fine is None else f'dopo {fine[0]:.2f} secondi, motivo {fine[1]}' + (f', codice {fine[2]}' if fine[2] else '')}.")
        apparecchio.chiudi()
        sorgente.chiudi()
        server.ferma()
    finally:
        ricerca.ferma()
        m.chiudi()
        registro.close()
        if os.path.exists(alto):
            os.remove(alto)
    return 0


if __name__ == "__main__":
    raise SystemExit(principale())
