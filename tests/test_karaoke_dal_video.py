# MeTeOra, le prove del testo dei video karaoke, letto dall'immagine con l'archivio dei testi (3.28.0, issue 51).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import pytest
from PIL import Image

import karaoke_dal_video as kv
import ocr
import testi_dei_video

TESTO = """Is this the real life
Is this just fantasy
Caught in a landslide
No escape from reality

Let it be, let it be
Let it be, let it be
Whisper words of wisdom, let it be"""
CANDIDATO = {"artistName": "Queen", "trackName": "Bohemian Rhapsody", "plainLyrics": TESTO, "syncedLyrics": ""}
ALTRO = {"artistName": "Qualcuno", "trackName": "Altra canzone", "plainLyrics": "Tutt'altre parole\nche non c'entrano niente\ncon il video", "syncedLyrics": "[00:01.00]x"}
YOUTUBE = "https://www.youtube.com/watch?v=abcdefghijk"


def test_il_titolo_ripulito_e_i_karaoke():
    assert kv.pulisci_il_titolo("Natalie Imbruglia - Torn (Karaoke Version)") == "Natalie Imbruglia Torn"
    assert kv.pulisci_il_titolo("Whitney Houston - I Will Always Love You (Karaoke With Lyrics) @StingrayKaraoke") == "Whitney Houston I Will Always Love You"
    assert kv.pulisci_il_titolo("Queen - Don't Stop Me Now (Karaoke Version) with Lyrics On Screen") == "Queen Don't Stop Me Now"
    assert kv.pulisci_il_titolo("Laura Pausini - La solitudine (Versione Karaoke Academy Italia)") == "Laura Pausini La solitudine"
    assert kv.pulisci_il_titolo("Karaoké La solitudine - Laura Pausini *") == "La solitudine Laura Pausini"
    assert kv.e_un_karaoke("Karaoké La solitudine") and kv.e_un_karaoke("Torn (KARAOKE)") and not kv.e_un_karaoke("Il film") and not kv.e_un_karaoke(None)


def test_la_ricerca_toglie_le_parole_finche_trova():
    domande = []

    def chiedi(domanda, attesa):
        domande.append(domanda)
        return [CANDIDATO] * 12 if domanda == "Queen Bohemian" else []

    assert kv.cerca_nell_archivio("Queen - Bohemian Rhapsody (Karaoke) mp4", chiedi=chiedi) == [CANDIDATO] * kv.RISULTATI
    assert domande == ["Queen Bohemian Rhapsody mp4", "Queen Bohemian Rhapsody", "Queen Bohemian"]
    domande.clear()
    assert kv.cerca_nell_archivio("Niente da trovare qui", chiedi=chiedi) == [] and domande[-1] == "Niente da"


def test_l_abbinatore_dice_le_parole_dell_archivio():
    archivio = kv.Archivio(TESTO, "Queen - Bohemian Rhapsody")
    abbinatore = kv.Abbinatore(archivio, "Queen - Bohemian Rhapsody (Karaoke)")
    # L'OCR storpia, l'archivio da' le parole esatte; il cartello iniziale e i loghi no.
    assert abbinatore.abbina(5.0, "bohemian rhapsody", "BOHEMIAN RHAPSODY") is None
    assert abbinatore.abbina(6.0, "sing king", "SING KING") is None
    assert abbinatore.abbina(30.0, kv.norm("Is thls the reai life"), "Is thls the reai life") == "Is this the real life"
    assert abbinatore.abbina(30.0, kv.norm("Is this just fantasy"), "") == "Is this just fantasy"
    # Una riga gia' detta da poco non si ridice.
    assert abbinatore.abbina(33.0, kv.norm("Is this just fantasy"), "") is None
    # Una riga corta vuole di piu': "caught in a" e' esatta, "tube" non e' true.
    assert abbinatore.abbina(40.0, "caught in a", "") == "Caught in a"
    assert abbinatore.abbina(41.0, "tube", "") is None
    # Il ritornello che torna in una pagina nuova va alla sua ripetizione.
    assert abbinatore.abbina(60.0, "let it be let it be", "") == "Let it be, let it be"
    assert abbinatore.abbina(62.0, "let it be let it be", "") == "Let it be, let it be"
    # La riga che cresce dice solo le parole nuove.
    assert abbinatore.abbina(70.0, "whisper words", "") == "Whisper words"
    assert abbinatore.abbina(71.0, "whisper words of wisdom let it be", "") == "of wisdom, let it be"
    # Senza l'archivio, la riga come la legge l'OCR, e della riga cresciuta solo il resto.
    senza = kv.Abbinatore(None, "Video qualunque")
    assert senza.abbina(30.0, "may be", "MAY BE") == "MAY BE"
    assert senza.abbina(30.4, "may be parted", "MAY BE PARTED") == "PARTED"


def test_le_righe_nuove_sullo_schermo():
    righe = kv.Righe()
    assert righe.nuove(0.0, ["Hello world line"]) == []
    assert righe.nuove(0.4, ["Hello world line"]) == [(0.4, "hello world line", "Hello world line")]
    # Ferma sullo schermo, anche letta storta, non si ripropone.
    assert righe.nuove(0.8, ["Hello world line"]) == [] and righe.nuove(1.2, ["Hello wor1d line"]) == []
    # Sparita per piu' di ASSENZA e tornata, come un ritornello: di nuovo.
    for istante in (1.6, 2.0, 2.4, 2.8):
        assert righe.nuove(istante, []) == []
    assert righe.nuove(3.2, ["Hello world line"]) == []
    assert righe.nuove(3.6, ["Hello world line"]) == [(3.6, "hello world line", "Hello world line")]
    # Due righe uguali nella pagina sono due righe.
    pagina = kv.Righe()
    pagina.nuove(0.0, ["Look how they shine", "Look how they shine", "x"])
    assert len(pagina.nuove(0.4, ["Look how they shine", "Look how they shine", "x"])) == 2
    # La riga che cresce si ripropone intera, quando e' ferma.
    crescita = kv.Righe()
    crescita.nuove(0.0, ["MAY BE"])
    assert crescita.nuove(0.4, ["MAY BE"]) == [(0.4, "may be", "MAY BE")]
    assert crescita.nuove(0.8, ["MAY BE PARTED"]) == []
    assert crescita.nuove(1.2, ["MAY BE PARTED"]) == [(1.2, "may be parted", "MAY BE PARTED")]


def test_la_scelta_fra_i_testi_dell_archivio():
    lette = [kv.norm(r) for r in ("Is thls the reai life", "Caught in a landslide", "No escape frorn reality")]
    assert kv.scegli([ALTRO, CANDIDATO], lette) == (CANDIDATO, 3)
    assert kv.scegli([], lette) == (None, 0)
    assert kv.nome_del_candidato(CANDIDATO) == "Queen - Bohemian Rhapsody"
    # I nomi come arrivano a volte dall'archivio: il cantante ripetuto, una parentesi a meta'.
    sporco = {"artistName": "Natalie Imbruglia", "trackName": "Natalie Imbruglia - Torn    )"}
    assert kv.nome_del_candidato(sporco) == "Natalie Imbruglia - Torn"
    assert kv.nome_del_candidato({"artistName": "", "trackName": "Azzurro (Live)"}) == "Azzurro (Live)"


def test_il_fotogramma_in_grigio_ingrandito():
    piccolo = kv.prepara(Image.new("RGB", (640, 360), (200, 0, 0)))
    assert piccolo.size == (1280, 720) and len(set(piccolo.getpixel((5, 5)))) == 1
    assert kv.prepara(Image.new("RGB", (1280, 720))).size == (1280, 720)


class _MotoreFinto:
    """Un video che avanza di INTERVALLO a ogni posizione chiesta."""

    def __init__(self, percorso=YOUTUBE, durata=30.0):
        self.in_corso, self.in_pausa, self.durata, self._posizione = percorso, False, durata, -0.4

    @property
    def posizione(self):
        self._posizione = round(self._posizione + 0.4, 1)
        return self._posizione

    def foto(self, con_i_sottotitoli):
        return Image.new("RGB", (64, 36))


# Lo schermo del video finto: da quando a quando ogni pagina.
PAGINE = [(0.0, 4.0, ["SING KING"]), (4.0, 9.0, ["Is thls the reai life", "Is this just fantasy", "SING KING"]),
          (9.0, 14.0, ["Caught in a landslide", "No escape frorn reality", "SING KING"]), (14.0, 99.0, ["SING KING"])]


def _lettura(monkeypatch, motore, cerca, coperti=(), pagine=PAGINE):
    monkeypatch.setattr(kv, "INTERVALLO", 0.005)
    lette = []

    def leggi(immagine, lingua):
        istante = motore._posizione
        lette.append(istante)
        return next((righe for da, a, righe in pagine if da <= istante < a), [])

    monkeypatch.setattr(ocr, "leggi", leggi)
    detti, avvisi = [], []
    lettura = kv.LetturaDelKaraoke(motore, detti.append, "it-IT", motore.in_corso, "Queen - Bohemian Rhapsody (Karaoke Version)",
        lambda frase, con_l_archivio: avvisi.append((frase, con_l_archivio)), coperti=coperti, cerca=cerca)
    return lettura, detti, avvisi, lette


def _fino_a(lettura, motore, istante):
    lettura.avvia()
    for _volta in range(4000):
        if motore._posizione >= istante:
            break
        lettura._fermo.wait(0.005)
    lettura.ferma()
    lettura.aspetta(5)


def test_la_lettura_con_l_archivio_salva_il_testo(monkeypatch):
    motore = _MotoreFinto(durata=60.0)
    lettura, detti, avvisi, _lette = _lettura(monkeypatch, motore, lambda titolo: [ALTRO, CANDIDATO])
    _fino_a(lettura, motore, 20.0)
    assert detti == ["Is this the real life\nIs this just fantasy", "Caught in a landslide\nNo escape from reality"]
    assert avvisi == [("Testo del karaoke di Queen - Bohemian Rhapsody (Karaoke Version): è nell'archivio dei testi, Queen - Bohemian Rhapsody; "
                       "le righe lette si dicono con le sue parole.", True)]
    assert lettura.esito_dell_archivio == "trovato" and lettura.righe_dette == 4
    # Il testo e' nella cartella Testi, con i tratti letti.
    voce = testi_dei_video.voce(YOUTUBE)
    assert voce["righe"] == 4 and voce["archivio"] == "Queen - Bohemian Rhapsody" and voce["coperti"][0][0] == pytest.approx(0.0, abs=0.5)
    assert voce["coperti"][-1][1] >= 20.0 and not voce["completo"]
    righe = testi_dei_video.righe(YOUTUBE)
    assert [r.testo for r in righe] == ["Is this the real life", "Is this just fantasy", "Caught in a landslide", "No escape from reality"]
    assert [r.strofa for r in righe] == [True, False, True, False] and righe[0].inizio == pytest.approx(4.4, abs=0.01)


def test_senza_archivio_si_dice_l_ocr(monkeypatch):
    motore = _MotoreFinto()

    def guasto(titolo):
        raise OSError("niente rete")

    lettura, detti, avvisi, _lette = _lettura(monkeypatch, motore, guasto)
    _fino_a(lettura, motore, 16.0)
    # Il logo e' gia' sullo schermo dall'inizio: si dice una volta, come l'OCR lo legge.
    assert detti == ["SING KING", "Is thls the reai life\nIs this just fantasy", "Caught in a landslide\nNo escape frorn reality"]
    assert avvisi == [("L'archivio dei testi non risponde: il testo di Queen - Bohemian Rhapsody (Karaoke Version) si legge dal video così com'è, "
                       "con qualche errore possibile.", False)]
    # Un archivio che non ha la canzone del video: dieci righe lette, nessuna
    # riconosciuta; da li' si dice l'OCR, senza aver mai detto che c'era.
    versi = ["Sole cuore amore", "Volare oh oh", "Nel blu dipinto di blu", "Una lunga storia d'amore", "Ancora tu non mi sorprende",
             "Quanto tempo e ancora", "Se bruciasse la citta", "Gloria manchi tu nell'aria", "Ti amo un soldo", "Vado al massimo",
             "Bella senz'anima", "Fotoromanza di notte", "Margherita non lo sa", "Albachiara respiri piano", "Sapore di sale"]
    altre = [(da, da + 1.2, [verso]) for verso, da in zip(versi, range(0, 60, 2), strict=False)]
    motore = _MotoreFinto(durata=80.0)
    lettura, detti, avvisi, _lette = _lettura(monkeypatch, motore, lambda titolo: [ALTRO], pagine=altre)
    _fino_a(lettura, motore, 30.0)
    assert len(avvisi) == 1 and avvisi[0][1] is False and avvisi[0][0].startswith("I testi dell'archivio non sono quello di")
    assert "Sapore di sale" in detti and "Volare oh oh" not in detti


def test_i_tratti_gia_letti_non_si_rileggono(monkeypatch):
    motore = _MotoreFinto()
    lettura, detti, _avvisi, lette = _lettura(monkeypatch, motore, lambda titolo: [CANDIDATO], coperti=[(0.0, 10.0)])
    _fino_a(lettura, motore, 16.0)
    assert lette and min(lette) > 10.0
    assert detti == ["Caught in a landslide\nNo escape from reality"]
