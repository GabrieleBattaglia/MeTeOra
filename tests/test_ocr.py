# MeTeOra, le prove del riconoscimento dei caratteri e dei sottotitoli fatti di immagini (1.80.0).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import time

import pytest
from PIL import Image, ImageDraw, ImageFont

import ocr
import sottotitoli_ocr


def _scritta(testo, larghezza=640, altezza=360, in_basso=True):
    """Un fotogramma nero con una scritta bianca, in basso o in alto."""
    immagine = Image.new("RGB", (larghezza, altezza), "black")
    ImageDraw.Draw(immagine).text((40, altezza - 60 if in_basso else 20), testo, fill="white", font=ImageFont.truetype("arial.ttf", 32))
    return immagine


def test_la_differenza_isola_il_sottotitolo():
    senza = Image.new("RGB", (640, 360), (40, 60, 80))
    con = senza.copy()
    ImageDraw.Draw(con).text((100, 300), "Ciao a tutti", fill="white", font=ImageFont.truetype("arial.ttf", 32))
    ritaglio = ocr.scritte_della_differenza(con, senza)
    # Nero su bianco, ingrandito, solo la scritta.
    assert ritaglio is not None and ritaglio.width < 640 * 2 and ritaglio.height < 120
    grigi = ritaglio.convert("L").tobytes()
    assert sum(1 for g in grigi if g < 128) < sum(1 for g in grigi if g >= 128)
    assert ocr.scritte_della_differenza(senza, senza.copy()) is None


def test_la_fascia_in_basso_e_le_impronte():
    fascia = ocr.fascia_in_basso(_scritta("Ciao a tutti"))
    # Il trenta per cento in basso, ingrandito perche' il video e' piccolo.
    assert fascia.size == (640 * 2, int(360 * ocr.FASCIA + 0.5) * 2) or fascia.width == 640 * 2
    vuota = ocr.fascia_in_basso(Image.new("RGB", (640, 360), "black"))
    assert ocr.cambiata(ocr.impronta(vuota), ocr.impronta(fascia))
    assert not ocr.cambiata(ocr.impronta(fascia), ocr.impronta(ocr.fascia_in_basso(_scritta("Ciao a tutti"))))
    assert ocr.cambiata(None, ocr.impronta(fascia))


def test_parole_e_lingue(monkeypatch):
    assert ocr.parole(["Ciao a tutti", "- 12 :"]) == 2
    monkeypatch.setattr(ocr, "lingue", lambda: ["en-US", "it-IT"])
    assert ocr.lingua_per("eng") == "en-US" and ocr.lingua_per("ita") == "it-IT"
    assert ocr.lingua_per(None) == "it-IT" and ocr.lingua_per("fra") == "it-IT"
    # I codici di tre lettere: rum e' il rumeno, non il russo; est l'estone, non lo spagnolo.
    monkeypatch.setattr(ocr, "lingue", lambda: ["ru-RU", "ro-RO", "es-ES", "et-EE", "it-IT"])
    assert ocr.lingua_per("rum") == "ro-RO" and ocr.lingua_per("est") == "et-EE" and ocr.lingua_per("spa") == "es-ES"
    # Senza Pillow il riconoscimento non c'e', anche con le lingue.
    monkeypatch.setattr(ocr.importlib.util, "find_spec", lambda nome: None)
    assert not ocr.disponibile()
    monkeypatch.setattr(ocr, "lingue", lambda: [])
    assert ocr.lingua_per("ita") is None


@pytest.mark.skipif(not ocr.disponibile(), reason="il riconoscimento dei caratteri di Windows non c'e'")
def test_il_riconoscimento_vero_legge_una_scritta():
    immagine = Image.new("RGB", (900, 120), "black")
    ImageDraw.Draw(immagine).text((20, 30), "Perché Tito Pullo è tornato?", fill="white", font=ImageFont.truetype("arial.ttf", 44))
    assert ocr.leggi(immagine, ocr.lingua_per("ita")) == ["Perché Tito Pullo è tornato?"]


def test_i_file_della_passata(tmp_path):
    video = tmp_path / "Film.mkv"
    assert sottotitoli_ocr.file_della_passata(str(video), "it-IT") == str(tmp_path / "Film.impressi.it.srt")
    (tmp_path / "Film.impressi.it.srt").write_text("")
    (tmp_path / "Film.it.srt").write_text("")
    (tmp_path / "Altro.impressi.it.srt").write_text("")
    assert sottotitoli_ocr.passate_esistenti(str(video)) == [str(tmp_path / "Film.impressi.it.srt")]


def test_segmenti_scritte_fisse_e_srt():
    campioni = [(0.0, ("CANALE UNO",)), (0.5, ("Ciao a tutti", "CANALE UNO")), (1.0, ("Ciao a tuttl", "CANALE UNO")),
        (1.5, ("Ciao a tutti", "CANALE UNO")), (2.0, ("CANALE UNO",)), (2.5, ("Come stai oggi", "CANALE UNO")),
        (3.0, ("CANALE UNO",)), (20.0, ("CANALE UNO",)), (20.5, ())]
    # Il canale, fermo per venti secondi, non e' un sottotitolo.
    puliti = sottotitoli_ocr.senza_scritte_fisse(campioni)
    assert all("CANALE UNO" not in righe for _t, righe in puliti)
    sottotitoli = sottotitoli_ocr.segmenti(puliti, 21.0)
    # Le letture simili di fila sono un sottotitolo, con la lettura piu' frequente.
    assert sottotitoli == [(0.5, 2.0, "Ciao a tutti"), (2.5, 3.0, "Come stai oggi")]
    assert sottotitoli_ocr.testo_srt(sottotitoli) == "1\n00:00:00,500 --> 00:00:02,000\nCiao a tutti\n\n2\n00:00:02,500 --> 00:00:03,000\nCome stai oggi\n"


class _MotoreFinto:
    video_oscurato = False

    def __init__(self, foto=None, quadri=None):
        self.in_pausa, self.in_corso = False, "film.mkv"
        self._foto = foto or {}
        self._quadri = list(quadri or [])

    def foto(self, con_i_sottotitoli):
        if self._quadri:
            return self._quadri.pop(0) if len(self._quadri) > 1 else self._quadri[0]
        return self._foto.get(con_i_sottotitoli)


def _aspetta(condizione, secondi=3):
    fine = time.monotonic() + secondi
    while not condizione() and time.monotonic() < fine:
        time.sleep(0.01)
    return condizione()


def test_la_lettura_delle_immagini(monkeypatch):
    letti = []
    monkeypatch.setattr(ocr, "leggi", lambda immagine, lingua: ["Ciao a tutti"] if immagine is not None else [])
    senza = Image.new("RGB", (320, 180), "black")
    motore = _MotoreFinto(foto={True: _scritta("Ciao a tutti", 320, 180), False: senza})
    lettura = sottotitoli_ocr.LetturaDelleImmagini(motore, letti.append, "it-IT").avvia()
    lettura.nuovo_sottotitolo()
    assert _aspetta(lambda: letti == ["Ciao a tutti"])
    lettura.ferma()
    lettura.aspetta(2)


def test_la_lettura_degli_impressi_dice_solo_le_righe_nuove(monkeypatch):
    # Un logo fisso si sente una volta sola; un testo si dice quando due
    # letture di fila coincidono.
    letti = []
    monkeypatch.setattr(sottotitoli_ocr, "INTERVALLO_AL_VOLO", 0.005)
    monkeypatch.setattr(ocr, "fascia_in_basso", lambda quadro: quadro)
    monkeypatch.setattr(ocr, "impronta", lambda fascia: fascia["impronta"])
    monkeypatch.setattr(ocr, "cambiata", lambda prima, dopo: prima != dopo)
    monkeypatch.setattr(ocr, "leggi", lambda fascia, lingua: fascia["righe"])
    vuota = {"impronta": b"a", "righe": []}
    prima = {"impronta": b"b", "righe": ["Ciao a tutti", "CANALE UNO"]}
    dopo = {"impronta": b"c", "righe": ["Come stai oggi", "CANALE UNO"]}
    motore = _MotoreFinto(quadri=[vuota, vuota, prima, prima, prima, dopo, dopo, dopo])
    lettura = sottotitoli_ocr.LetturaDegliImpressi(motore, letti.append, "it-IT").avvia()
    assert _aspetta(lambda: len(letti) >= 2)
    lettura.ferma()
    lettura.aspetta(2)
    assert letti[:2] == ["Ciao a tutti CANALE UNO", "Come stai oggi"]


class _LettoreFinto:
    """Il libmpv della passata, finto: dieci secondi di video, mezzo secondo a ogni occhiata."""

    def __init__(self, sottotitoli):
        self.duration, self.pause, self.speed, self.idle_active = 10.0, True, 1, False
        self._istante, self._sottotitoli, self.terminato = 0.0, sottotitoli, False

    @property
    def time_pos(self):
        if self._istante > self.duration:
            self.idle_active = True
            return None
        istante = self._istante
        self._istante += 0.25
        return istante

    def screenshot_raw(self, includes="video"):
        istante = self._istante - 0.25
        return {"righe": next((r for (a, b), r in self._sottotitoli.items() if a <= istante < b), [])}

    def terminate(self):
        self.terminato = True


def test_la_passata_scrive_il_file(monkeypatch, tmp_path):
    monkeypatch.setattr(ocr, "fascia_in_basso", lambda quadro: quadro)
    monkeypatch.setattr(ocr, "leggi", lambda fascia, lingua: fascia["righe"])
    lettore = _LettoreFinto({(1.0, 3.0): ["Ciao a tutti"], (5.0, 7.0): ["Come stai oggi"]})
    esiti, avanzamenti = [], []
    video = str(tmp_path / "Film.mkv")
    passata = sottotitoli_ocr.PassataDegliImpressi(video, "it-IT", avanzamenti.append, esiti.append, crea_lettore=lambda _v: lettore).avvia()
    passata.aspetta(5)
    assert esiti == [str(tmp_path / "Film.impressi.it.srt")] and lettore.terminato and lettore.speed == sottotitoli_ocr.VELOCITA_DELLA_PASSATA
    assert avanzamenti[0] == 0 and avanzamenti[-1] >= 90
    testo = (tmp_path / "Film.impressi.it.srt").read_text(encoding="utf-8")
    assert testo == "1\n00:00:01,000 --> 00:00:03,000\nCiao a tutti\n\n2\n00:00:05,000 --> 00:00:07,000\nCome stai oggi\n"


def test_la_passata_che_non_trova_niente_o_si_guasta(monkeypatch, tmp_path):
    monkeypatch.setattr(ocr, "fascia_in_basso", lambda quadro: quadro)
    monkeypatch.setattr(ocr, "leggi", lambda fascia, lingua: fascia["righe"])
    esiti = []
    video = str(tmp_path / "Film.mkv")
    sottotitoli_ocr.PassataDegliImpressi(video, "it-IT", lambda p: None, esiti.append, crea_lettore=lambda _v: _LettoreFinto({})).avvia().aspetta(5)
    assert esiti == [None] and not (tmp_path / "Film.impressi.it.srt").exists()

    def guasto(_video):
        raise RuntimeError("niente libmpv")

    sottotitoli_ocr.PassataDegliImpressi(video, "it-IT", lambda p: None, esiti.append, crea_lettore=guasto).avvia().aspetta(5)
    assert esiti[-1] == "La passata dei sottotitoli impressi di Film.mkv si è fermata per un errore."


def test_le_scritte_sul_nero_e_la_lettura_oscurata(monkeypatch):
    # Revisione 1.80.0: a video spento il fotogramma e' nero, e basta una foto.
    foto = _scritta("Ciao a tutti", 320, 180)
    ritaglio = ocr.scritte_sul_nero(foto)
    assert ritaglio is not None and ritaglio.width < 320 * 2
    assert ocr.scritte_sul_nero(Image.new("RGB", (320, 180), "black")) is None
    letti, viste = [], []
    monkeypatch.setattr(ocr, "leggi", lambda immagine, lingua: viste.append(immagine) or ["Ciao a tutti"])
    motore = _MotoreFinto(foto={True: foto})
    motore.video_oscurato = True
    lettura = sottotitoli_ocr.LetturaDelleImmagini(motore, letti.append, "it-IT").avvia()
    lettura.nuovo_sottotitolo()
    assert _aspetta(lambda: letti == ["Ciao a tutti"]) and viste[0].size == ritaglio.size
    lettura.ferma()


def test_un_giro_guasto_non_ferma_la_lettura(monkeypatch):
    # Revisione 1.80.0: un errore si dice una volta, e la lettura continua.
    letti, guasti, chiamate = [], [], []

    def leggi(immagine, lingua):
        chiamate.append(1)
        if len(chiamate) == 1:
            raise OSError("Another RecognizeAsync operation is already running!")
        return ["Ciao a tutti"]

    monkeypatch.setattr(ocr, "leggi", leggi)
    motore = _MotoreFinto(foto={True: _scritta("Ciao", 320, 180), False: Image.new("RGB", (320, 180), "black")})
    lettura = sottotitoli_ocr.LetturaDelleImmagini(motore, letti.append, "it-IT", guasto=guasti.append).avvia()
    lettura.nuovo_sottotitolo()
    assert _aspetta(lambda: len(chiamate) >= 1)
    time.sleep(0.1)
    lettura.nuovo_sottotitolo()
    assert _aspetta(lambda: letti == ["Ciao a tutti"]) and len(guasti) == 1
    lettura.ferma()


def test_la_passata_che_non_puo_scrivere_non_parte(monkeypatch, tmp_path):
    esiti, creati = [], []
    video = str(tmp_path / "manca" / "Film.mkv")
    sottotitoli_ocr.PassataDegliImpressi(video, "it-IT", lambda p: None, esiti.append, crea_lettore=lambda v: creati.append(v)).avvia().aspetta(5)
    assert not creati and esiti[0].startswith("La passata dei sottotitoli impressi non parte: nella cartella di Film.mkv non posso scrivere")
