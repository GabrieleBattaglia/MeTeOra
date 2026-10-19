# MeTeOra, le prove delle posizioni dei file lunghi: il punto, i margini, il file.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.92.0. Nella 1.104.0 le prove della pulizia all'avvio e di Rinomina file.

import json
import os

import posizioni


def _norm(p):
    # La forma concordata degli insiemi di percorsi mancanti (1.104.0).
    return os.path.normcase(os.path.abspath(p))


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


def test_la_pulizia_all_avvio(tmp_path):
    file = tmp_path / "MeTeOra - Posizioni.json"
    p = posizioni.Posizioni(str(file))
    p.ricorda(r"C:\Libri\Uno.m4b", 600, 3600)
    p.ricorda(r"C:\Libri\due.m4b", 700, 3600)
    p.ricorda(r"D:\Film\tre.mkv", 800, 7200)
    p.salva()
    assert p.percorsi() == [r"C:\Libri\Uno.m4b", r"C:\Libri\due.m4b", r"D:\Film\tre.mkv"]
    # Il file mancante si riconosce anche scritto in un'altra forma.
    assert p.togli_i_mancanti({_norm("c:/libri/UNO.M4B"), _norm(r"C:\Libri\x.m4b")}) == 1 and p.modificate
    assert p.percorsi() == [r"C:\Libri\due.m4b", r"D:\Film\tre.mkv"] and p.quante() == 2
    p.salva()
    assert p.togli_i_mancanti({_norm(r"C:\Libri\x.m4b")}) == 0 and p.togli_i_mancanti(set()) == 0 and not p.modificate
    riletto = posizioni.Posizioni(str(file))
    assert riletto.percorsi() == [r"C:\Libri\due.m4b", r"D:\Film\tre.mkv"] and riletto.dove(r"C:\Libri\Uno.m4b") is None


def test_il_punto_segue_rinomina_file(tmp_path):
    file = tmp_path / "MeTeOra - Posizioni.json"
    p = posizioni.Posizioni(str(file))
    p.ricorda(r"C:\Libri\due.m4b", 700, 3600)
    p.ricorda(r"D:\Film\tre.mkv", 800, 7200)
    p.salva()
    # Il punto passa al nome nuovo, trovato anche con altre maiuscole.
    assert p.rinomina(r"c:\libri\DUE.m4b", r"C:\Libri\Due, il seguito.m4b") and p.modificate
    assert p.dove(r"C:\Libri\Due, il seguito.m4b") == 700 and p.dove(r"C:\Libri\due.m4b") is None
    p.salva()
    assert not p.rinomina(r"C:\Libri\nessuno.m4b", r"C:\Libri\altro.m4b") and not p.modificate
    # Cambiano solo le maiuscole: il punto resta, con il nome nuovo.
    assert p.rinomina(r"D:\Film\tre.mkv", r"D:\Film\Tre.mkv") and p.dove(r"D:\Film\Tre.mkv") == 800 and p.quante() == 2
    # Un punto che il nome nuovo aveva gia' e' di un file sparito, perche'
    # Rinomina file rifiuta un nome che esiste: resta quello del file
    # rinominato, anche se e' piu' vecchio.
    p._punti[r"D:\Film\Tre.mkv"]["quando"] = "2026-10-01T10:00:00"
    p._punti[r"D:\Film\quattro.mkv"] = {"secondi": 900.0, "quando": "2026-10-02T10:00:00"}
    assert p.rinomina(r"D:\Film\Tre.mkv", r"D:\Film\Quattro.mkv")
    assert p.percorsi() == [r"C:\Libri\Due, il seguito.m4b", r"D:\Film\Quattro.mkv"] and p.dove(r"D:\Film\Quattro.mkv") == 800
    # Anche se il punto del file rinominato non ha 'quando'.
    p._punti[r"D:\Film\cinque.mkv"] = {"secondi": 100.0}
    assert p.rinomina(r"D:\Film\cinque.mkv", r"D:\Film\quattro.mkv")
    assert p.percorsi() == [r"C:\Libri\Due, il seguito.m4b", r"D:\Film\quattro.mkv"] and p.dove(r"D:\Film\quattro.mkv") == 100
    p.salva()
    riletto = posizioni.Posizioni(str(file))
    assert riletto.dove(r"C:\Libri\Due, il seguito.m4b") == 700 and riletto.dove(r"D:\Film\quattro.mkv") == 100 and riletto.quante() == 2
    # Il file rinominato non ha un punto: quello sul nome nuovo, scritto in
    # un'altra forma, si toglie lo stesso.
    assert p.rinomina(r"D:\Film\sei.mkv", r"d:/film/QUATTRO.MKV") and p.modificate
    assert p.percorsi() == [r"C:\Libri\Due, il seguito.m4b"]


def test_rinomina_file_con_piu_grafie(tmp_path):
    # 1.104.0: fra le grafie del file rinominato resta il punto piu' recente.
    p = posizioni.Posizioni(str(tmp_path / "MeTeOra - Posizioni.json"))
    p._punti[r"C:\Libri\sette.m4b"] = {"secondi": 50.0, "quando": "2026-10-01T10:00:00"}
    p._punti[r"c:\libri\SETTE.m4b"] = {"secondi": 60.0, "quando": "2026-10-03T10:00:00"}
    p._punti["c:/libri/sette.M4B"] = {"secondi": 70.0, "quando": "2026-10-02T10:00:00"}
    p._punti[r"C:\Libri\Otto.m4b"] = {"secondi": 80.0, "quando": "2026-10-04T10:00:00"}
    assert p.rinomina(r"C:\Libri\sette.m4b", r"C:\Libri\otto.m4b") and p.percorsi() == [r"C:\Libri\otto.m4b"] and p.dove(r"C:\Libri\otto.m4b") == 60
    # Cambiano solo le maiuscole: le grafie sono tutte del file rinominato.
    p._punti[r"C:\Libri\OTTO.m4b"] = {"secondi": 90.0, "quando": "2026-10-05T10:00:00"}
    assert p.rinomina(r"C:\Libri\otto.m4b", r"C:\Libri\Otto.m4b") and p.percorsi() == [r"C:\Libri\Otto.m4b"] and p.dove(r"C:\Libri\Otto.m4b") == 90
    # Un nome che e' gia' quello scritto, o un file senza punti, non cambia niente.
    p.modificate = False
    assert not p.rinomina(r"c:\libri\otto.M4B", r"C:\Libri\Otto.m4b") and not p.modificate
    assert not p.rinomina(r"C:\Libri\nove.m4b", r"C:\Libri\dieci.m4b") and not p.modificate and p.quante() == 1
