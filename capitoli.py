# MeTeOra, i capitoli dei file: dai tag degli MP4 e degli MP3, per la plancia.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.93.0, tappa 12 e del piano.

"""I capitoli dei file (1.93.0).

Gli audiolibri M4B, molti M4A e MP4, e alcuni MP3 hanno i capitoli: dai_tag()
li legge dall'oggetto di mutagen che lo schedario ha gia' aperto, i capitoli
degli MP4 e i frame CHAP degli ID3, come (secondi, titolo) in ordine di
tempo. Un capitolo solo non e' una divisione: non conta. I capitoli che i
tag non dicono, come quelli degli MKV, li vede libmpv mentre il file suona.
"""

import contextlib


def dai_tag(audio):
    """[(secondi, titolo)] dall'oggetto di mutagen, o [] se non ne ha almeno due."""
    if audio is None:
        return []
    elenco = []
    with contextlib.suppress(Exception):
        for capitolo in getattr(audio, "chapters", None) or []:
            elenco.append((float(capitolo.start), str(capitolo.title or "").strip()))
    if not elenco:
        with contextlib.suppress(Exception):
            tags = audio.tags
            for frame in tags.getall("CHAP") if hasattr(tags, "getall") else []:
                titolo = ""
                sotto = getattr(frame, "sub_frames", None)
                if sotto is not None and "TIT2" in sotto:
                    titolo = str(sotto["TIT2"].text[0])
                elenco.append((frame.start_time / 1000.0, titolo.strip()))
    elenco.sort(key=lambda capitolo: capitolo[0])
    return [(round(secondi, 3), titolo) for secondi, titolo in elenco] if len(elenco) > 1 else []
