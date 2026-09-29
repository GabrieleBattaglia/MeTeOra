"""Tappa 0: quali formati apre libmpv, e con quale durata."""
import os
import sys
import time

import ambiente  # noqa: F401

# isort: split
import mpv


def prova(percorso):
    p = mpv.MPV(ao="null", vo="null", video="no", ytdl=False, input_default_bindings=False,
                config=False, log_handler=None)
    esito = "?"
    try:
        p.play(percorso)
        t0 = time.time()
        while time.time() - t0 < 6:
            try:
                d = p.duration
                if d is not None:
                    esito = f"ok durata={d:.1f}s codec={p.audio_codec_name} demux={p.current_demuxer}"
                    break
            except Exception:
                pass
            time.sleep(0.1)
        else:
            esito = "nessuna durata in 6 s"
    except Exception as e:
        esito = f"errore {e}"
    finally:
        p.terminate()
    return esito


for f in sys.argv[1:]:
    print(os.path.basename(f), "->", prova(f), flush=True)
