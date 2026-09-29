
import ambiente  # noqa: F401

# isort: split
import mpv

p = mpv.MPV(ao="null", vo="null", config=False)
print(p.mpv_version)
print("ffmpeg", p.ffmpeg_version)
d = p.demuxer_lavf_list
print(len(d), "demuxer")
chiavi = ("mod", "sid", "gme", "xm", "mpt", "it", "sap", "nsf", "ay", "vgm", "spc", "mid", "hes", "gbs", "tta", "wv", "ape", "dsf", "dff", "mpc", "tak", "ac3", "dts")
print([x for x in d if any(k in x for k in chiavi)])
p.terminate()
