# MeTeOra, le prove dei capitoli: la lettura dai tag e lo schedario.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.93.0.

import json
import types

from mutagen.id3 import CHAP, ID3, TIT2

import capitoli
import schedario


def test_i_capitoli_degli_mp4():
    audio = types.SimpleNamespace(chapters=[types.SimpleNamespace(start=600.0, title=" Due "), types.SimpleNamespace(start=0.0, title="Uno")])
    assert capitoli.dai_tag(audio) == [(0.0, "Uno"), (600.0, "Due")]
    # Un capitolo solo non conta.
    assert capitoli.dai_tag(types.SimpleNamespace(chapters=[types.SimpleNamespace(start=0.0, title="Tutto")])) == []
    assert capitoli.dai_tag(None) == []


def test_i_capitoli_degli_mp3():
    tags = ID3()
    tags.add(CHAP(element_id="c2", start_time=95500, end_time=200000, sub_frames=[TIT2(text=["Il secondo"])]))
    tags.add(CHAP(element_id="c1", start_time=0, end_time=95500, sub_frames=[TIT2(text=["Il primo"])]))
    assert capitoli.dai_tag(types.SimpleNamespace(chapters=None, tags=tags)) == [(0.0, "Il primo"), (95.5, "Il secondo")]


def test_lo_schedario_rilegge_solo_i_file_lunghi(tmp_path):
    vecchia = {"dim": 1, "mod": 0, "tag": {}, "sottobrani": None, "durate_sid": None, "tag_v": 2}
    schede = {
        r"C:\m\libro.m4b": {**vecchia, "durata": 3600.0},
        r"C:\m\canzone.mp3": {**vecchia, "durata": 200.0},
        r"C:\m\film.mkv": {**vecchia, "durata": 7200.0},
        r"C:\m\nuovo.m4b": {**vecchia, "durata": 3600.0, "tag_v": 3, "capitoli": [[0, "Uno"], [600, "Due"]]},
    }
    percorso = tmp_path / "MeTeOra - Schedario.json"
    percorso.write_text(json.dumps({"versione": schedario.VERSIONE_DEL_FILE, "schede": schede}), encoding="utf-8")
    s = schedario.Schedario(str(percorso))
    s.carica()
    assert sorted(s.schede) == sorted([r"C:\m\canzone.mp3", r"C:\m\film.mkv", r"C:\m\nuovo.m4b"])
    assert s.scheda(r"C:\m\nuovo.m4b")["capitoli"] == [[0, "Uno"], [600, "Due"]]
