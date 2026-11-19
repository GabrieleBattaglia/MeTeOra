# MeTeOra, le prove della cartella Testi: i testi del karaoke letti dai video, tenuti per la volta dopo (3.28.0, issue 51).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import datetime
import json
import os

import pytest

import karaoke
import testi_dei_video

URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL123"


def test_la_chiave_del_video():
    for indirizzo in (URL, "https://youtu.be/dQw4w9WgXcQ?t=3", "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
                      "https://www.youtube.com/shorts/dQw4w9WgXcQ", "https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ"):
        assert testi_dei_video.chiave(indirizzo) == "youtube-dQw4w9WgXcQ"
    altro = testi_dei_video.chiave("https://vimeo.com/123456")
    assert altro.startswith("sito-") and altro == testi_dei_video.chiave("https://vimeo.com/123456#inizio")
    assert testi_dei_video.chiave("") is None


def test_la_chiave_di_un_file_cambia_col_file(tmp_path):
    video = tmp_path / "Canzone (Karaoke).mp4"
    video.write_bytes(b"x" * 10)
    prima = testi_dei_video.chiave(str(video))
    assert prima.startswith("file-") and prima == testi_dei_video.chiave(str(video))
    video.write_bytes(b"x" * 20)
    assert testi_dei_video.chiave(str(video)) != prima
    assert testi_dei_video.chiave(str(tmp_path / "manca.mp4")) is None


def test_salva_unisce_e_diventa_karaoke():
    assert testi_dei_video.voce(URL) is None and karaoke.cerca(URL) == (None, [])
    esito = testi_dei_video.salva(URL, "Rick - Song (Karaoke)", 200.0, [(12.4, ["Riga uno", "Riga due"]), (20.0, ["Riga tre"])], [(10.0, 60.0)],
                                  "Rick - Song")
    assert esito == {"righe": 3, "nuovo": True, "completato": False}
    voce = testi_dei_video.voce(URL)
    assert voce == {"coperti": [(10.0, 60.0)], "durata": 200.0, "righe": 3, "archivio": "Rick - Song", "completo": False}
    fonte, righe = karaoke.cerca(URL)
    assert fonte == "video" and karaoke.titolo(fonte) == "Testo del karaoke, dal video"
    assert [(r.inizio, r.testo, r.strofa) for r in righe] == [(12.4, "Riga uno", True), (12.4, "Riga due", False), (20.0, "Riga tre", True)]
    # Le due righe comparse insieme sono un blocco solo della traccia.
    assert karaoke.blocchi(righe)[0] == (12.4, 20.0, "Riga uno\nRiga due")
    # Un altro ascolto: i tratti nuovi si uniscono, il gruppo gia' salvato non si ripete.
    assert testi_dei_video.salva(URL, "Rick - Song (Karaoke)", 0, [(12.5, ["Riga uno", "Riga due"]), (150.0, ["Riga quattro"])],
                                 [(0.0, 10.0), (60.0, 200.0)]) == {"righe": 4, "nuovo": False, "completato": True}
    # Gia' completo, un altro salvataggio non lo completa di nuovo.
    assert testi_dei_video.salva(URL, "Rick - Song (Karaoke)", 0, [(180.0, ["Riga cinque"])], [(0.0, 200.0)])["completato"] is False
    voce = testi_dei_video.voce(URL)
    assert voce["coperti"] == [(0.0, 200.0)] and voce["completo"] and voce["durata"] == 200.0 and voce["archivio"] == "Rick - Song"
    assert testi_dei_video.salva(URL, "x", 1, [], []) is None


def test_la_pulizia_dopo_un_anno(tmp_path):
    testi_dei_video.salva(URL, "Vecchio", 100.0, [(5.0, ["Riga"])], [(0.0, 100.0)])
    nuovo = "https://www.youtube.com/watch?v=abcdefghijk"
    testi_dei_video.salva(nuovo, "Nuovo", 100.0, [(5.0, ["Riga"])], [(0.0, 100.0)])
    cartella = testi_dei_video.cartella()
    indice = os.path.join(cartella, testi_dei_video.INDICE)
    with open(indice, encoding="utf-8") as f:
        dati = json.load(f)
    dati["testi"]["youtube-dQw4w9WgXcQ"]["ascoltato"] = "2025-11-01"
    with open(indice, "w", encoding="utf-8") as f:
        json.dump(dati, f)
    # Un file dei testi che l'indice non conosce si toglie; gli altri file restano.
    with open(os.path.join(cartella, "youtube-zzzzzzzzzzz.lrc"), "w", encoding="utf-8") as f:
        f.write("[00:01.00]x\n")
    with open(os.path.join(cartella, "nota.txt"), "w", encoding="utf-8") as f:
        f.write("mia")
    assert testi_dei_video.pulisci(datetime.date(2026, 11, 19)) == 2
    assert testi_dei_video.voce(URL) is None and testi_dei_video.voce(nuovo) is not None
    assert sorted(os.listdir(cartella)) == ["Testi.json", "nota.txt", "youtube-abcdefghijk.lrc"]


def test_ascoltato_rinfresca_la_data():
    testi_dei_video.salva(URL, "Titolo", 100.0, [(5.0, ["Riga"])], [(0.0, 50.0)])
    indice = os.path.join(testi_dei_video.cartella(), testi_dei_video.INDICE)
    with open(indice, encoding="utf-8") as f:
        dati = json.load(f)
    dati["testi"]["youtube-dQw4w9WgXcQ"]["ascoltato"] = "2020-01-01"
    with open(indice, "w", encoding="utf-8") as f:
        json.dump(dati, f)
    assert [r.testo for r in testi_dei_video.righe(URL)] == ["Riga"]
    with open(indice, encoding="utf-8") as f:
        assert json.load(f)["testi"]["youtube-dQw4w9WgXcQ"]["ascoltato"] == datetime.date.today().isoformat()


def test_una_cartella_che_non_si_scrive_non_solleva(monkeypatch, tmp_path):
    def rifiuta(*_dati, **_nomi):
        raise PermissionError("negato")

    monkeypatch.setattr(testi_dei_video.os, "makedirs", rifiuta)
    assert testi_dei_video.salva(URL, "Titolo", 100.0, [(5.0, ["Riga"])], [(0.0, 50.0)]) is None
    assert testi_dei_video.pulisci() == 0


@pytest.mark.parametrize(("tratti", "unione"), [([(5, 9), (0, 4.8)], [(0, 9)]), ([(0, 2), (3, 4)], [(0, 2), (3, 4)]), ([(1, 1)], [(1, 1)])])
def test_i_tratti_uniti(tratti, unione):
    assert testi_dei_video.unisci(tratti) == [tuple(map(float, t)) for t in unione]
    assert testi_dei_video.coperto(unione, 1) and not testi_dei_video.coperto(unione, 10)
