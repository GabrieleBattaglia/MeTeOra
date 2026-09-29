"""SID in tempo reale dentro libmpv: flusso WAV virtuale servito dalla RAM, con seek."""
import os
import time

import ambiente  # noqa: F401
import sidmotore
import songlengths

# isort: split
import mpv
from sidmotore import FlussoSid

SID = r"E:\C64Music\MUSICIANS\T\Tel_Jeroen\Turbo_Outrun.sid"
tabella = songlengths.carica(songlengths.trova_database(SID))
durate = songlengths.durate(SID, tabella)
p = mpv.MPV(ao=os.environ.get("AO", "null"), vo="null", video="no", config=False, ytdl=False, cache="no", demuxer_lavf_format="wav", demuxer_readahead_secs=1)


@p.register_stream_protocol("sid")
def _apri(uri):
	# sid://<sottobrano>/<percorso>
	sottobrano, percorso = uri[len("sid://"):].split("/", 1)
	n = int(sottobrano)
	return FlussoSid(sidmotore.BranoSid(percorso, n, durate[n - 1]))


for n in (1, 2):
	t0 = time.perf_counter()
	p.play(f"sid://{n}/{SID}")
	p.wait_until_playing()
	print(f"sottobrano {n}: suona dopo {(time.perf_counter() - t0) * 1000:.0f} ms, durata dichiarata {p.duration:.1f} s")
	time.sleep(1)
	t0 = time.perf_counter()
	p.seek(90, "absolute", "exact")
	p.wait_for_property("time-pos", lambda v: v is not None and v >= 90.5)
	print(f"  seek a 90 s in {(time.perf_counter() - t0) * 1000:.0f} ms, pos {p.time_pos:.2f}")
	time.sleep(3)
	t0 = time.perf_counter()
	p.seek(10, "absolute", "exact")
	p.wait_for_property("time-pos", lambda v: v is not None and 10.5 <= v < 20)
	print(f"  seek indietro a 10 s in {(time.perf_counter() - t0) * 1000:.0f} ms, pos {p.time_pos:.2f}")
	time.sleep(float(os.environ.get("ASCOLTO", "0")))
p.terminate()
