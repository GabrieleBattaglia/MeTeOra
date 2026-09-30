"""Zapping di SID in tempo reale: python prova_zapping.py <cartella o file .sid>"""
import msvcrt
import os
import sys

import ambiente  # noqa: F401

import sid as sidmotore
import songlengths

# isort: split
import mpv

from sid import FlussoSid

origine = sys.argv[1] if len(sys.argv) > 1 else r"E:\C64Music\MUSICIANS\T\Tel_Jeroen"
files = sorted(os.path.join(origine, f) for f in os.listdir(origine) if f.lower().endswith(".sid")) if os.path.isdir(origine) else [origine]
tabella = songlengths.carica(songlengths.trova_database(files[0]))
p = mpv.MPV(ao="wasapi", vo="null", video="no", config=False, ytdl=False, cache="no", demuxer_lavf_format="wav", demuxer_readahead_secs=1)
stato = {"file": 0, "sotto": 1, "durate": [], "info": {}}


@p.register_stream_protocol("sid")
def _apri(uri):
    n, percorso = uri[len("sid://"):].split("/", 1)
    n = int(n)
    durate = stato["durate"]
    secondi = durate[n - 1] if durate and n <= len(durate) else 180
    return FlussoSid(sidmotore.BranoSid(percorso, n, max(1.0, secondi)))


def mmss(s):
    return f"{int(s // 60)}:{int(s % 60):02d}"


def suona(indice_file, sottobrano=None):
    stato["file"] = indice_file % len(files)
    percorso = files[stato["file"]]
    stato["info"] = songlengths.leggi_intestazione(percorso)
    stato["durate"] = songlengths.durate(percorso, tabella) or []
    stato["sotto"] = sottobrano or stato["info"]["iniziale"] or 1
    p.play(f"sid://{stato['sotto']}/{percorso}")
    i = stato["info"]
    durata = stato["durate"][stato["sotto"] - 1] if stato["durate"] else 180
    print(f"{stato['file'] + 1}/{len(files)} {i['titolo']}, {i['autore']}, {i['copyright']}. Sottobrano {stato['sotto']} di {i['sottobrani']}, {mmss(durata)}", flush=True)


def cambia_sotto(passo):
    totale = stato["info"]["sottobrani"]
    suona(stato["file"], (stato["sotto"] - 1 + passo) % totale + 1)


print("Tasti: j e k brano successivo e precedente, n e p sottobrano, frecce destra e sinistra 10 secondi, t tempo, spazio pausa, q esci.")
suona(0)
while True:
    c = msvcrt.getwch()
    if c in ("\x00", "\xe0"):
        c = {"M": "destra", "K": "sinistra"}.get(msvcrt.getwch(), "")
    if c == "q":
        break
    if c == "j":
        suona(stato["file"] + 1)
    elif c == "k":
        suona(stato["file"] - 1)
    elif c == "n":
        cambia_sotto(1)
    elif c == "p":
        cambia_sotto(-1)
    elif c in ("destra", "sinistra"):
        p.seek(10 if c == "destra" else -10, "relative", "exact")
        print(f"Salto a {mmss(max(0, (p.time_pos or 0) + (10 if c == 'destra' else -10)))}", flush=True)
    elif c == "t":
        print(f"{mmss(p.time_pos or 0)} di {mmss(p.duration or 0)}", flush=True)
    elif c == " ":
        p.pause = not p.pause
        print("Pausa" if p.pause else "Riprende", flush=True)
p.terminate()
