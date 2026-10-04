# MeTeOra, le prove delle posizioni dei file lunghi: il punto, i margini, il file.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.92.0.

import json

import posizioni


def test_il_punto_i_margini_e_il_file(tmp_path):
    file = tmp_path / "MeTeOra - Posizioni.json"
    p = posizioni.Posizioni(str(file))
    assert p.dove("libro.m4b") is None and not p.modificate
    p.ricorda("libro.m4b", 1500.04, 3600)
    assert p.dove("libro.m4b") == 1500.0 and p.modificate
    # Vicino all'inizio o alla fine il punto si dimentica.
    p.ricorda("libro.m4b", 10, 3600)
    assert p.dove("libro.m4b") is None
    p.ricorda("libro.m4b", 3590, 3600)
    assert p.dove("libro.m4b") is None
    p.ricorda("film.mkv", 600, 7200)
    p.salva()
    assert not p.modificate and json.loads(file.read_text(encoding="utf-8"))["film.mkv"]["secondi"] == 600
    assert posizioni.Posizioni(str(file)).dove("film.mkv") == 600
    # Un file che non si legge vale come vuoto.
    file.write_text("{rotto", encoding="utf-8")
    assert posizioni.Posizioni(str(file)).dove("film.mkv") is None


def test_si_tengono_le_piu_recenti(tmp_path, monkeypatch):
    monkeypatch.setattr(posizioni, "MASSIME", 3)
    p = posizioni.Posizioni(str(tmp_path / "p.json"))
    for numero in range(5):
        p.ricorda(f"f{numero}", 100, 1000)
        p._punti[f"f{numero}"]["quando"] = f"2026-10-0{numero + 1}T10:00:00"
    p.salva()
    assert sorted(p._punti) == ["f2", "f3", "f4"]
