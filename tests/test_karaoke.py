# MeTeOra, le prove dei testi del karaoke: MIDI e .kar costruiti qui, .lrc, SYLT, blocchi e traccia.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.82.0.

"""I MIDI si costruiscono byte per byte, i .lrc si scrivono in tmp_path, i
SYLT arrivano da tag ID3 veri di mutagen dentro un file finto."""

import struct
import types

import pytest

import karaoke
from karaoke import Riga


def _numero(n):
    pezzi = [n & 0x7F]
    n >>= 7
    while n:
        pezzi.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(pezzi))


def _meta(tipo, dati):
    return bytes([0xFF, tipo]) + _numero(len(dati)) + dati


def _traccia(*eventi):
    """Una traccia MTrk da (delta, evento)."""
    corpo = b"".join(_numero(delta) + evento for delta, evento in eventi) + _numero(0) + b"\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(corpo)) + corpo


def _midi(*tracce, divisione=480):
    return b"MThd" + struct.pack(">IHHH", 6, 1, len(tracce), divisione) + b"".join(tracce)


def _testi(tipo, *sillabe):
    """Eventi di testo da (delta, sillaba)."""
    return [(delta, _meta(tipo, sillaba.encode("cp1252"))) for delta, sillaba in sillabe]


def test_un_kar_con_i_cambi_di_tempo():
    # Tempo 120 fino al quarto battito, poi 240: 480 tick valgono mezzo
    # secondo, poi un quarto. Le note usano lo stato corrente.
    tempi = _traccia((0, _meta(0x51, (500000).to_bytes(3, "big"))), (1920, _meta(0x51, (250000).to_bytes(3, "big"))))
    note = _traccia((0, b"\x90\x40\x40"), (10, b"\x41\x40"), (10, b"\xc0\x05"), (0, b"\xf0\x02\x7e\xf7"), (10, b"\x80\x40\x00"))
    parole = _traccia(*_testi(0x01, (0, "@KMIDI KARAOKE FILE"), (0, "@TTitolo"), (480, "\\Pri"), (240, "ma "), (240, "ri"), (240, "ga"),
        (720, "/Se"), (120, "con"), (120, "da"), (240, "\\Ter"), (120, "za")))
    righe = karaoke.dal_midi(_midi(tempi, note, parole), kar=True)
    assert righe == [Riga(0.5, "Prima riga", True), Riga(2.0, "Seconda", False), Riga(2.25, "Terza", True)]
    # Un .mid con gli eventi di testo segnati dalle barre e' un karaoke
    # anche senza la chiocciola; con le intestazioni anche senza barre in
    # testa, se va a capo.
    barre = _traccia(*_testi(0x01, (480, "\\Pri"), (240, "ma"), (240, "/Se"), (240, "con"), (240, "/Ter")))
    assert [r.testo for r in karaoke.dal_midi(_midi(tempi, barre))] == ["Prima", "Secon", "Ter"]
    titolo = _traccia(*_testi(0x01, (0, "@TTitolo"), (480, "Uno\r"), (240, "Due\r"), (240, "Tre\r")))
    assert [r.testo for r in karaoke.dal_midi(_midi(tempi, titolo))] == ["Uno", "Due", "Tre"]
    # Senza intestazioni e senza barre gli eventi di testo sono commenti.
    commenti = _traccia(*_testi(0x01, (480, "Arrangiamento "), (240, "di "), (240, "Mario "), (240, "Rossi")))
    assert karaoke.dal_midi(_midi(tempi, commenti)) == []


def test_il_testo_cantato_con_gli_a_capo_gli_accordi_e_il_copyright():
    # Gli a capo arrivano anche da soli; gli accordi e l'istante zero si saltano.
    cantato = _traccia(*_testi(0x05, (0, "All rights reserved"), (480, "My "), (0, "%DO"), (240, "name"), (0, "\r"), (480, "I "), (240, "live"),
        (0, "\r"), (480, "<UP"), (240, "STAIRS"), (0, "\n"), (480, "from you")))
    righe = karaoke.dal_midi(_midi(cantato))
    assert righe == [Riga(0.5, "My name", True), Riga(1.25, "I live", False), Riga(2.0, "UPSTAIRS", False), Riga(2.75, "from you", True)]
    # Due righe sole sono un avviso, non un testo.
    poco = _traccia(*_testi(0x05, (480, "Copyright"), (0, "\r"), (480, "Tutti i diritti")))
    assert karaoke.dal_midi(_midi(poco)) == []


def test_nei_kar_vince_il_testo_con_le_barre():
    cantato = _traccia(*_testi(0x05, (480, "Uno"), (480, "Due"), (480, "Tre")))
    parole = _traccia(*_testi(0x01, (0, "@KMIDI KARAOKE FILE"), (480, "\\Uno"), (480, "/Due"), (480, "/Tre")))
    righe = karaoke.dal_midi(_midi(cantato, parole))
    assert [riga.testo for riga in righe] == ["Uno", "Due", "Tre"]
    # Con una traccia sola di testo cantato vale quello.
    assert [riga.testo for riga in karaoke.dal_midi(_midi(cantato), kar=True)] == []


def test_un_kar_con_gli_accordi_negli_eventi_di_testo():
    # Revisione 1.82.0: tre .kar di Gabriele hanno negli eventi di testo solo
    # gli accordi, senza barre; il testo vero e' nel testo cantato.
    accordi = _traccia(*_testi(0x01, (480, "A             "), (480, "D             /F#"), (480, "E min"), (480, "A")))
    cantato = _traccia(*_testi(0x05, (480, "NON PARLI MAI\r"), (480, "PERCHE'\r"), (480, "SE C'E' UN MOTIVO\r")))
    assert [r.testo for r in karaoke.dal_midi(_midi(accordi, cantato), kar=True)] == ["NON PARLI MAI", "PERCHE'", "SE C'E' UN MOTIVO"]


def test_la_barra_dopo_lo_spazio_e_le_righe_vicine():
    # Pollon.kar: la barra rovesciata dopo uno spazio cambia strofa.
    righe = karaoke.righe_dalle_sillabe([(1.0, "Pol"), (1.2, "lon"), (2.0, " \\Pol"), (2.2, "lon "), (2.4, "com"), (2.6, "bi")])
    assert righe == [Riga(1.0, "Pollon", True), Riga(2.0, "Pollon combi", True)]
    # Due righe a meno di DURATA_MINIMA si uniscono: libmpv le sovrapporrebbe.
    vicine = [Riga(0.704, "MI FAI STARE BENE", True), Riga(0.725, "(Biagio Antonacci)", False), Riga(5.0, "Prima", False)]
    assert karaoke.blocchi(vicine) == [(0.704, 5.0, "MI FAI STARE BENE\n(Biagio Antonacci)"), (5.0, 15.0, "Prima")]
    # L'ultima strofa dura fino a DURATA_DELL_ULTIMA dopo la sua ultima riga.
    strofe = [Riga(1.0, "Uno", True), Riga(5.0, "Due", True), Riga(20.0, "Tre", False)]
    assert karaoke.blocchi(strofe, "strofa")[-1] == (5.0, 30.0, "Due\nTre")


def test_la_divisione_smpte_e_i_file_rovinati():
    divisione = ((256 - 25) << 8) | 40
    cantato = _traccia(*_testi(0x05, (1500, "Uno\r"), (1000, "Due\r"), (1000, "Tre\r")))
    assert [riga.inizio for riga in karaoke.dal_midi(_midi(cantato, divisione=divisione))] == [1.5, 2.5, 3.5]
    # Una traccia troncata tiene quello che ha letto; un file che non e' MIDI solleva.
    intero = _midi(_traccia(*_testi(0x05, (480, "Uno\r"), (480, "Due\r"), (480, "Tre\r"), (480, "Quattro\r"))))
    assert [riga.testo for riga in karaoke.dal_midi(intero[:-12])] == ["Uno", "Due", "Tre"]
    with pytest.raises(ValueError):
        karaoke.dal_midi(b"non sono un midi")


def test_le_righe_troppo_lunghe_si_spezzano():
    # Un file che non va mai a capo: si va a capo alle pause del canto.
    parole = ["Tutti", "mi", "dicevano", "vedrai", "e", "successo", "a", "tutti", "pero", "poi", "ti", "alzi", "un", "giorno", "e", "non", "ci", "pensi", "piu"]
    sillabe = [(i * 0.3 + (2.0 if i >= 9 else 0.0), parola + " ") for i, parola in enumerate(parole)]
    righe = karaoke.righe_dalle_sillabe(sillabe)
    assert [riga.testo for riga in righe] == ["Tutti mi dicevano vedrai e successo a tutti pero", "poi ti alzi un giorno e non ci pensi piu"]
    assert righe[1].inizio == pytest.approx(9 * 0.3 + 2.0) and righe[0].strofa and not righe[1].strofa
    # Una pausa su una sillaba tenuta, a meta' parola, aspetta la fine della parola.
    tenuta = [(i * 0.3, parola) for i, parola in enumerate(["Avrai ", "sorrisi ", "sul ", "tuo ", "viso ", "come ", "ad ", "agosto ", "grilli ",
        "e ", "stelle ", "storie ", "fotografate ", "dentro ", "un ", "album ", "rile", "ga"])] + [(8.0, "to "), (8.2, "in "), (8.4, "pelle ")]
    assert [r.testo for r in karaoke.righe_dalle_sillabe(tenuta)][-1] == "in pelle"
    assert all(not r.testo.endswith("rilega") for r in karaoke.righe_dalle_sillabe(tenuta))
    # Senza pause, fra due parole prima di superare la lunghezza massima.
    lunga = [(i * 0.3, f"parola{i} ") for i in range(30)]
    assert all(len(riga.testo) <= karaoke.LUNGHEZZA_MASSIMA for riga in karaoke.righe_dalle_sillabe(lunga))


def test_le_codifiche():
    assert karaoke.codifica("perché".encode()) == "utf-8"
    # La a accentata di DOS, che in Windows sarebbero i puntini.
    assert karaoke.codifica(b"pouvoir parler \x85 un ange, \x82t\x82") == "cp850"
    assert karaoke.codifica("perché là".encode("cp1252")) == "cp1252"
    # Gli apostrofi curvi di Windows non fanno pensare a DOS: Don Raffae'.
    assert karaoke.codifica(b"c\x92\xe8 l\x92anima, \x91oin\xe8\x92 e l\x92ore") == "cp1252"
    assert karaoke.codifica(b"I\x92m sure you don\x92t") == "cp1252"
    cantato = _traccia(*[(480, _meta(0x05, parola)) for parola in (b"parler \x85\r", b"l\x85\r", b"\x82t\x82\r")])
    assert [riga.testo for riga in karaoke.dal_midi(_midi(cantato))] == ["parler à", "là", "été"]


LRC = """[ar:Artista]
[offset:+500]
[00:01.00]Prima riga
[00:03.50][00:10.00]Ritornello
[00:05.00]<00:05.00>Pa<00:05.30>ro<00:05.60>le
[00:07.00]

[00:08.00]Seconda strofa
"""


def test_il_lrc():
    righe = karaoke.dal_lrc(LRC)
    assert righe == [Riga(0.5, "Prima riga", True), Riga(3.0, "Ritornello", False), Riga(4.5, "Parole", False), Riga(6.5, "", False),
        Riga(7.5, "Seconda strofa", True), Riga(9.5, "Ritornello", False)]
    # I centesimi e i millesimi, e i due punti al posto del punto.
    assert [r.inizio for r in karaoke.dal_lrc("[01:02.5]a\n[01:02:250]b\n[1:2]c")] == [62.0, 62.25, 62.5]


def test_i_blocchi_per_riga_e_per_strofa():
    righe = karaoke.dal_lrc(LRC)
    assert karaoke.blocchi(righe) == [(0.5, 3.0, "Prima riga"), (3.0, 4.5, "Ritornello"), (4.5, 6.5, "Parole"), (7.5, 9.5, "Seconda strofa"),
        (9.5, 19.5, "Ritornello")]
    # L'ultima strofa dura fino a dieci secondi dopo la sua ultima riga.
    assert karaoke.blocchi(righe, "strofa") == [(0.5, 6.5, "Prima riga\nRitornello\nParole"), (7.5, 19.5, "Seconda strofa\nRitornello")]
    # Una riga di soli segni e' una pausa: non si legge.
    segni = [Riga(1.0, "Uno", True), Riga(3.0, "=====", False), Riga(5.0, "* * *", False), Riga(7.0, "Due", False)]
    assert karaoke.blocchi(segni) == [(1.0, 3.0, "Uno"), (7.0, 17.0, "Due")]
    # Senza strofe segnate, per strofa vale per riga.
    senza = [Riga(1.0, "Uno", True), Riga(2.0, "Due", False)]
    assert karaoke.blocchi(senza, "strofa") == karaoke.blocchi(senza) == [(1.0, 2.0, "Uno"), (2.0, 12.0, "Due")]
    # L'anticipo sposta tutto prima; quelli che partono insieme diventano uno.
    assert karaoke.blocchi(righe, anticipo=1.0)[:2] == [(0.0, 2.0, "Prima riga"), (2.0, 3.5, "Ritornello")]
    primo = karaoke.blocchi(righe, anticipo=5.0)[0]
    assert primo[0] == 0.0 and primo[2] == "Prima riga\nRitornello\nParole"
    srt = karaoke.traccia(righe, "riga", 0.5)
    assert srt.startswith("1\n00:00:00,000 --> 00:00:02,500\nPrima riga\n\n2\n00:00:02,500 --> 00:00:04,000\nRitornello\n")


def test_il_seguito_dello_speaker():
    # Il karaoke con lo speaker Cast (Gabriele, 3.17.0): i blocchi detti
    # seguendo la posizione che lo speaker riferisce.
    s = karaoke.Seguito("lrc", karaoke.dal_lrc(LRC))
    s.scegli(True)
    assert s.avanza(None) == [] and s.avanza(0.0) == []
    assert s.avanza(0.4) == [] and s.avanza(0.6) == ["Prima riga"] and s.avanza(1.5) == []
    # Due blocchi cominciati in un passo arrivano tutti e due, in ordine.
    assert s.avanza(2.9) == [] and s.avanza(4.6) == ["Ritornello", "Parole"]
    # Fra due blocchi niente; il blocco dopo quando comincia, con il tempo che gli resta.
    assert s.avanza(7.0) == [] and s.avanza(7.6) == ["Seconda strofa"]
    assert s.resto(7.6) == pytest.approx(1.9) and s.resto(7.0) is None and s.resto(None) is None
    # Un piccolo passo indietro dello speaker non ridice niente; un salto
    # indietro, o in avanti, ridice il blocco in corso.
    assert s.avanza(7.0) == [] and s.avanza(7.7) == []
    assert s.avanza(3.5) == ["Ritornello"] and s.avanza(4.0) == []
    assert s.avanza(10.0) == ["Ritornello"]
    # Non scelto tace, e scelto di nuovo ridice subito il blocco in corso.
    s.scegli(False)
    assert s.avanza(10.5) == []
    s.scegli(True)
    assert s.avanza(10.6) == ["Ritornello"]
    # Il modo e l'anticipo nuovi non ridicono il blocco in corso; dopo
    # l'ultimo non c'e' piu' niente.
    s.imposta("strofa", 0.0)
    assert s.avanza(10.8) == [] and s.avanza(20.0) == []
    assert s.avanza(7.6) == ["Seconda strofa\nRitornello"]


def _sylt(*voci, tipo=1):
    from mutagen.id3 import ID3, SYLT

    tag = ID3()
    tag.add(SYLT(encoding=3, lang="ita", format=2, type=tipo, desc="", text=list(voci)))
    return types.SimpleNamespace(tags=tag)


def test_i_testi_dei_tag(monkeypatch, tmp_path):
    import mutagen

    brano = tmp_path / "canzone.mp3"
    brano.write_bytes(b"")
    monkeypatch.setattr(mutagen, "File", lambda _percorso: _sylt(("Prima riga", 1000), ("Seconda", 2500), ("", 4000)))
    assert karaoke.dai_tag(str(brano)) == [Riga(1.0, "Prima riga", True), Riga(2.5, "Seconda", False)]
    # Con gli a capo le voci sono sillabe; una riga vuota cambia strofa.
    monkeypatch.setattr(mutagen, "File", lambda _percorso: _sylt(("Pri", 1000), ("ma", 1200), ("\nSe", 2000), ("conda", 2200), ("\n\nTer", 3000), ("za", 3200)))
    assert karaoke.dai_tag(str(brano)) == [Riga(1.0, "Prima", True), Riga(2.0, "Seconda", False), Riga(3.0, "Terza", True)]
    assert karaoke.cerca(str(brano))[0] == "sylt"
    # Il .lrc accanto vince sui tag.
    (tmp_path / "canzone.lrc").write_text("[00:01.00]Dal file\n", encoding="utf-8")
    assert karaoke.cerca(str(brano)) == ("lrc", [Riga(1.0, "Dal file", True)])


def test_cerca_non_solleva_mai(tmp_path, monkeypatch):
    import mutagen

    rotto = tmp_path / "rotto.mid"
    rotto.write_bytes(b"MThd\x00\x00")
    assert karaoke.cerca(str(rotto)) == (None, [])
    assert karaoke.cerca(str(tmp_path / "manca.kar")) == (None, [])

    def guasto(_percorso):
        raise OSError("disco staccato")

    monkeypatch.setattr(mutagen, "File", guasto)
    assert karaoke.cerca(str(tmp_path / "canzone.flac")) == (None, [])
    buono = tmp_path / "Canzone.KAR"
    buono.write_bytes(_midi(_traccia(*_testi(0x01, (480, "\\Uno"), (480, "/Due"), (480, "/Tre")))))
    fonte, righe = karaoke.cerca(str(buono))
    assert fonte == "midi" and [r.testo for r in righe] == ["Uno", "Due", "Tre"]
    assert karaoke.titolo(fonte) == "Testo del karaoke, dal MIDI"


class _SpeakerFinto:
    """Lo speaker come lo vede la finestra: la posizione la sceglie la prova."""

    def __init__(self):
        self.percorso = self.sottobrano = self.sottobrani = None
        self.in_pausa, self.posizione, self.durata, self.volume, self.titolo_in_onda = False, 0.0, 60.0, 50, None

    def suona(self, percorso, sottobrano=None, sottobrani=None, inizio=None, in_pausa=False, midi_reso=False):
        self.percorso = percorso

    def stop(self):
        self.percorso = None

    def pausa(self, valore=None):
        return False

    def salta(self, secondi):
        pass

    def vai_a(self, secondi):
        pass

    def chiudi(self, attendi=True):
        pass

    @property
    def posizione_attesa(self):
        # Quella che il motore da' alla finestra (15 novembre 2026): qui la stessa.
        return self.posizione


def test_il_karaoke_nella_finestra_con_lo_speaker(finestra, tmp_path, sintesi_finta):
    # Gabriele, 3.17.0: con lo speaker il testo si sceglie da solo, con i
    # sottotitoli accesi, e le righe vanno alla sintesi e nella console.
    import time
    import wave

    import wx

    def aspetta(condizione):
        fine = time.time() + 5
        while time.time() < fine and not condizione():
            wx.Yield()
            time.sleep(0.02)
        return condizione()

    brano = tmp_path / "canzone.wav"
    with wave.open(str(brano), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\0\0" * 8000)
    (tmp_path / "canzone.lrc").write_text("[00:01.00]Prima riga\n[00:03.00]Seconda riga\n", encoding="utf-8")
    speaker = _SpeakerFinto()
    finestra.motore.usa_il_lontano(speaker)
    finestra.impostazioni["sottotitoli"] = True
    try:
        finestra._suona_file(str(brano), str(tmp_path))
        assert aspetta(lambda: [t["selected"] for t in (finestra.motore.tracce() or {}).get("sub", [])] == [True])
        speaker.posizione = 1.2
        assert aspetta(lambda: [n for n, t in sintesi_finta.detti if t == "Prima riga"])
        speaker.posizione = 3.1
        assert aspetta(lambda: [n for n, t in sintesi_finta.detti if t == "Seconda riga"])
        # Nella console senza l'ora, che e' dei messaggi di MeTeOra (3.17.2).
        assert finestra._righe[-2:] == ["Prima riga", "Seconda riga"]
        conti = finestra._statistiche.dati["conti"]
        assert conti["righe_dei_sottotitoli"] == 2 and conti["righe_allo_speaker"] == 2
    finally:
        finestra.motore.usa_il_lontano(None)


def test_le_righe_e_i_colori_della_vista():
    # La vista del karaoke a tutto schermo (Gabriele, 3.18.0).
    import vista_karaoke

    blocchi = karaoke.blocchi(karaoke.dal_lrc(LRC))
    # Prima del canto sono tutte prossime; poi in alto quella cominciata, anche fra due righe.
    # Le prossime sono al piu' tre (Gabriele).
    assert vista_karaoke.righe_da_mostrare(blocchi, 0.1) == (None, ["Prima riga", "Ritornello", "Parole"])
    assert vista_karaoke.righe_da_mostrare(blocchi, 3.2) == ("Ritornello", ["Parole", "Seconda strofa", "Ritornello"])
    assert vista_karaoke.righe_da_mostrare(blocchi, 1.0) == ("Prima riga", ["Ritornello", "Parole", "Seconda strofa"])
    assert vista_karaoke.righe_da_mostrare(blocchi, 7.0) == ("Parole", ["Seconda strofa", "Ritornello"])
    assert vista_karaoke.righe_da_mostrare(blocchi, 30.0) == ("Ritornello", [])
    assert vista_karaoke.righe_da_mostrare([], 3.0) == (None, []) and vista_karaoke.righe_da_mostrare(blocchi, None)[0] is None
    # Il colore della riga da cantare risalta piu' del testo: sul nero il
    # giallo, o il bianco se il testo e' gia' giallo; sul bianco il blu scuro.
    ciano, nero, bianco = (0, 204, 214), (0, 0, 0), (255, 255, 255)
    assert vista_karaoke.colore_in_evidenza(ciano, nero) == (255, 255, 0)
    assert vista_karaoke.colore_in_evidenza((255, 255, 0), nero) == bianco
    assert vista_karaoke.colore_in_evidenza((60, 60, 60), bianco) == (0, 0, 140)
    assert vista_karaoke.contrasto(bianco, nero) == pytest.approx(21.0)
    assert vista_karaoke.contrasto((255, 255, 0), nero) > vista_karaoke.contrasto(ciano, nero)
    # A capo fra le parole, con gli a capo delle strofe; una parola troppo larga resta intera.
    assert vista_karaoke.a_capo("uno due tre quattro", 9, len) == ["uno due", "tre", "quattro"]
    assert vista_karaoke.a_capo("prima\nseconda riga", 20, len) == ["prima", "seconda riga"]
    assert vista_karaoke.a_capo("lunghissimaparola", 5, len) == ["lunghissimaparola"]


def test_la_vista_del_karaoke_nella_finestra(finestra, tmp_path, suoni_annotati):
    # Gabriele, 3.18.0: con il video acceso, un brano da cantare senza video
    # apre la vista a tutto schermo; Esc la nasconde per il brano, Ctrl con F1 la spegne.
    import time
    import wave

    import wx

    def aspetta(condizione, secondi=8):
        fine = time.time() + secondi
        while time.time() < fine and not condizione():
            wx.Yield()
            time.sleep(0.02)
        return condizione()

    brano = tmp_path / "canzone.wav"
    with wave.open(str(brano), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\0\0" * 8000 * 20)
    (tmp_path / "canzone.lrc").write_text("[00:00.50]Prima riga\n[00:03.00]Seconda riga\n[00:06.00]Terza riga\n", encoding="utf-8")
    finestra.impostazioni["video"] = True
    finestra.impostazioni["colori_testo"] = {"c": [0, 80, 84]}
    finestra.impostazioni["colori_sfondo"] = {"c": [0, 0, 0]}
    finestra._suona_file(str(brano), str(tmp_path))
    assert aspetta(lambda: finestra._vista_del_karaoke is not None and finestra._vista_del_karaoke.IsShown())
    vista = finestra._vista_del_karaoke
    assert vista.IsFullScreen() and vista.GetTitle().endswith(", karaoke, MeTeOra")
    assert vista._colori == ((0, 204, 214), (0, 0, 0), (255, 255, 0))
    assert aspetta(lambda: vista.mostrate()[0] == "Prima riga")
    assert vista.mostrate()[1] == ["Seconda riga", "Terza riga"]
    assert finestra._statistiche.dati["conti"]["viste_del_karaoke"] == 1
    # Esc la nasconde per questo brano, e la console lo dice; Maiuscolo con F1 la riapre.
    evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
    evento.SetKeyCode(wx.WXK_ESCAPE)
    vista._tasto(evento)
    assert not vista.IsShown() and "Karaoke nascosto per questo brano" in finestra._righe[-1]
    finestra._aggiorna_il_video()
    assert not vista.IsShown()
    finestra._metti_il_video(True)
    assert vista.IsShown()
    # La dimensione e il colore scelti valgono subito, anche a vista aperta (3.20.0).
    finestra.impostazioni["altezza_karaoke"] = 20
    finestra.impostazioni["colore_karaoke"] = [100, 0, 0]
    finestra._aspetto_del_karaoke()
    assert vista._altezza == 0.2 and vista._colori[2] == (255, 0, 0)
    # Ctrl con F1 spegne il video e la vista.
    finestra._metti_il_video(False)
    assert not vista.IsShown() and "il karaoke non si vede" in finestra._righe[-1]
    finestra.motore.stop()
