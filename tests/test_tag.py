# MeTeOra, le prove dei tag: le cinque famiglie, su file veri fatti da libmpv.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la 1.69.0, tappa 10, punto d.

"""I file delle prove li codifica libmpv, a uscita nulla, da un secondo di
silenzio: nessun suono. Ogni prova lavora su una copia."""

import os
import shutil
import wave

import numpy as np
import pytest
from test_formati import FORMATI, _codifica

import schedario
import tag

FORMATI_DEI_TAG = ("mp3", "ogg", "opus", "flac", "m4a", "wma", "aiff", "wav", "wv", "tta")
VALORI = (("titolo", "Ballata & co"), ("artista", "Gabriele"), ("album", "Prove"), ("artista_album", "Vari"), ("anno", "1999"),
    ("genere", "Rock"), ("traccia", "3/12"), ("disco", "1/2"), ("compositore", "ClaudIA"), ("commento", "Un commento"))


@pytest.fixture(scope="module")
def file_muti(tmp_path_factory):
    cartella = tmp_path_factory.mktemp("tag")
    sorgente = cartella / "sorgente.wav"
    with wave.open(str(sorgente), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(np.zeros(48000 * 2, dtype=np.int16).tobytes())  # un secondo, due canali
    file = {}
    for estensione in FORMATI_DEI_TAG:
        file[estensione] = cartella / f"prova.{estensione}"
        _codifica(sorgente, file[estensione], *FORMATI[estensione])
    return file


def _copia(file_muti, estensione, cartella, nome="prova"):
    copia = cartella / f"{nome}.{estensione}"
    shutil.copy(file_muti[estensione], copia)
    return str(copia)


@pytest.mark.parametrize("estensione", FORMATI_DEI_TAG)
def test_scrivere_rileggere_e_cancellare(file_muti, tmp_path, estensione):
    percorso = _copia(file_muti, estensione, tmp_path)
    assert tag.modificabile(percorso)
    letti = tag.leggi(percorso)
    assert [t["chiave"] for t in letti[:10]] == [chiave for chiave, _nome in tag.COMUNI] and not any(t["valore"] for t in letti[:10])
    for chiave, valore in VALORI:
        tag.scrivi(percorso, chiave, valore)
    dopo = {t["chiave"]: t["valore"] for t in tag.leggi(percorso)}
    assert {chiave: dopo[chiave] for chiave, _v in VALORI} == dict(VALORI), estensione
    tag.scrivi(percorso, "titolo", "")
    assert {t["chiave"]: t["valore"] for t in tag.leggi(percorso)}["titolo"] == ""
    # Il file resta un audio che si legge, con la sua durata.
    assert schedario.leggi_scheda(percorso)["durata"] == pytest.approx(1.0, abs=0.1)


def test_valori_che_non_vanno_e_file_che_non_si_leggono(tmp_path):
    for chiave, valore in (("anno", "99"), ("traccia", "tre"), ("disco", "1/due")):
        with pytest.raises(tag.ErroreTag):
            tag.controlla(chiave, valore)
    assert tag.controlla("anno", " 1999-05-21 ") == "1999-05-21" and tag.controlla("titolo", "a\nb") == "a b"
    (tmp_path / "rotto.mp3").write_bytes(b"niente di buono")
    with pytest.raises(tag.ErroreTag):
        tag.leggi(str(tmp_path / "rotto.mp3"))
    assert not tag.modificabile(r"C:\m\canzone.mid") and not tag.modificabile(r"C:\m\film.mkv")


def test_i_tag_non_comuni_e_la_versione_di_id3(file_muti, tmp_path):
    from mutagen.id3 import APIC, ID3, TXXX

    percorso = _copia(file_muti, "mp3", tmp_path)
    id3 = ID3(percorso)
    id3.add(TXXX(encoding=3, desc="REPLAYGAIN_TRACK_GAIN", text=["-6.5 dB"]))
    id3.add(APIC(encoding=3, mime="image/png", type=3, desc="", data=b"\x89PNG\r\n\x1a\n" + bytes(range(256)) * 20))
    id3.save(v2_version=3)
    altri = {t["nome"]: t for t in tag.leggi(percorso)[10:]}
    assert altri["REPLAYGAIN_TRACK_GAIN"]["valore"] == "-6.5 dB" and altri["REPLAYGAIN_TRACK_GAIN"]["testo"]
    assert altri["Copertina"] == {"chiave": "~APIC:", "nome": "Copertina", "valore": "immagine di 5 KB", "testo": False}
    tag.scrivi(percorso, altri["REPLAYGAIN_TRACK_GAIN"]["chiave"], "-3 dB")
    tag.scrivi(percorso, "titolo", "Sempre la 2.3")
    assert ID3(percorso).version[:2] == (2, 3)
    altri = {t["nome"]: t for t in tag.leggi(percorso)[10:]}
    assert altri["REPLAYGAIN_TRACK_GAIN"]["valore"] == "-3 dB" and "Copertina" in altri


def test_piu_file_insieme(file_muti, tmp_path):
    uno, due = _copia(file_muti, "flac", tmp_path, "uno"), _copia(file_muti, "mp3", tmp_path, "due")
    tag.scrivi(uno, "album", "Primo")
    tag.scrivi(due, "album", "Secondo")
    tag.scrivi(uno, "artista", "Lo stesso")
    tag.scrivi(due, "artista", "Lo stesso")
    insieme, errori = tag.leggi_insieme([uno, due, str(tmp_path / "manca.mp3")])
    per_chiave = {t["chiave"]: t for t in insieme}
    assert per_chiave["album"]["diversi"] and per_chiave["album"]["valore"] == ""
    assert not per_chiave["artista"]["diversi"] and per_chiave["artista"]["valore"] == "Lo stesso"
    # I tag non comuni stanno solo se li hanno tutti: le famiglie sono diverse.
    assert len(insieme) == 10 and len(errori) == 1

def _tag(percorso):
    return {t["chiave"]: t for t in tag.leggi(percorso)}


def test_i_booleani_di_itunes_negli_m4a(file_muti, tmp_path):
    # Revisione della 1.69.0: cpil e pgap mutagen li tiene da soli, non in una lista.
    import mutagen
    from mutagen.mp4 import MP4

    percorso = _copia(file_muti, "m4a", tmp_path)
    m4a = MP4(percorso)
    m4a["cpil"], m4a["pgap"], m4a["\xa9nam"] = False, True, ["Brano"]
    m4a.save()
    letti = _tag(percorso)
    assert letti["titolo"]["valore"] == "Brano" and letti["~pgap"]["valore"] == "True" and not letti["~pgap"]["testo"]
    assert tag.comuni_del_file(mutagen.File(percorso)) == {"titolo": "Brano"}
    assert schedario.leggi_scheda(percorso)["tag"]["titolo"] == "Brano"


def test_la_versione_2_3_resta_con_i_suoi_frame(file_muti, tmp_path):
    from mutagen.id3 import ID3, IPLS, TIT2, TSOP, TYER

    percorso = _copia(file_muti, "mp3", tmp_path)
    id3 = ID3()
    id3.add(TIT2(encoding=1, text=["Vecchio"]))
    id3.add(TYER(encoding=1, text=["1999"]))
    id3.add(TSOP(encoding=1, text=["Artista, L'"]))
    id3.add(IPLS(encoding=1, people=[["chitarra", "Gabriele"]]))
    id3.save(percorso, v2_version=3)
    assert _tag(percorso)["anno"]["valore"] == "1999"
    tag.scrivi(percorso, "titolo", "Nuovo")
    frame = ID3(percorso, translate=False)
    assert frame.version[:2] == (2, 3) and {"TIT2", "TYER", "TSOP", "IPLS"} <= {k[:4] for k in frame} and "TDRC" not in frame
    tag.scrivi(percorso, "anno", "2001")
    assert str(ID3(percorso, translate=False)["TYER"]) == "2001"


def test_un_file_rovinato_da_errori_di_mutagen_diventa_errore_tag(file_muti, tmp_path, monkeypatch):
    import mutagen

    percorso = _copia(file_muti, "ogg", tmp_path)

    def rotto(_percorso):
        raise IndexError("pagina rovinata")

    monkeypatch.setattr(mutagen, "File", rotto)
    with pytest.raises(tag.ErroreTag, match="pagina rovinata"):
        tag.leggi(percorso)
    with pytest.raises(tag.ErroreTag):
        tag.scrivi(percorso, "titolo", "x")
    assert tag.leggi_insieme([percorso]) == ([], ["Non riesco a leggere i tag di prova.ogg: pagina rovinata"])


def test_i_tag_con_piu_valori_restano_divisi(file_muti, tmp_path):
    from mutagen.flac import FLAC

    percorso = _copia(file_muti, "flac", tmp_path)
    flac = FLAC(percorso)
    flac["artist"] = ["Uno", "Due"]
    flac["title"] = ["Rock; e altro"]
    flac.save()
    letti = _tag(percorso)
    assert letti["artista"]["valore"] == "Uno; Due" and letti["titolo"]["valore"] == "Rock; e altro"
    tag.scrivi(percorso, "artista", "Uno; Due; Tre")
    tag.scrivi(percorso, "titolo", "Rock; e altro ancora")
    flac = FLAC(percorso)
    assert flac["artist"] == ["Uno", "Due", "Tre"] and flac["title"] == ["Rock; e altro ancora"]


def test_i_commenti_in_altre_lingue_restano(file_muti, tmp_path):
    from mutagen.id3 import COMM, ID3

    percorso = _copia(file_muti, "mp3", tmp_path)
    id3 = ID3(percorso)
    id3.add(COMM(encoding=3, lang="eng", desc="", text=["English comment"]))
    id3.add(COMM(encoding=3, lang="ita", desc="", text=["Commento italiano"]))
    id3.save()
    letti = _tag(percorso)
    assert letti["commento"]["valore"] == "English comment" and letti["~COMM::ita"]["nome"] == "Commento (ita)"
    tag.scrivi(percorso, "commento", "Nuovo")
    commenti = {f.lang: f.text[0] for f in ID3(percorso).getall("COMM")}
    assert commenti == {"eng": "Nuovo", "ita": "Commento italiano"}


def test_il_tta_con_l_ape_e_l_ape_con_l_id3v1(file_muti, tmp_path):
    from mutagen.apev2 import APEv2

    percorso = _copia(file_muti, "tta", tmp_path)
    ape = APEv2()
    ape["Title"] = "Titolo APE"
    ape.save(percorso)
    assert _tag(percorso)["titolo"]["valore"] == "Titolo APE"
    tag.scrivi(percorso, "titolo", "Nuovo")
    assert APEv2(percorso)["Title"] == "Nuovo" and _tag(percorso)["titolo"]["valore"] == "Nuovo"
    # Un WavPack con l'APEv2 e l'ID3v1 in coda: l'ID3v1 resta.
    wv = _copia(file_muti, "wv", tmp_path)
    tag.scrivi(wv, "titolo", "Con APE")
    v1 = b"TAG" + b"Titolo v1".ljust(30, b"\0") + bytes(95)
    with open(wv, "ab") as f:
        f.write(v1)
    tag.scrivi(wv, "titolo", "Cambiato")
    with open(wv, "rb") as f:
        assert f.read()[-128:] == v1
    assert _tag(wv)["titolo"]["valore"] == "Cambiato"


def test_righe_multiple_date_dati_binari_e_chiavi_personali(file_muti, tmp_path):
    from mutagen.flac import FLAC
    from mutagen.id3 import ID3, TDOR
    from mutagen.mp4 import MP4, AtomDataType, MP4FreeForm

    # Un tag su piu' righe si legge ma non si modifica.
    flac_p = _copia(file_muti, "flac", tmp_path)
    flac = FLAC(flac_p)
    flac["comment"] = ["riga uno\nriga due"]
    flac["titolo"] = ["Campo personale"]
    flac["year"] = ["1987"]
    flac.save()
    letti = _tag(flac_p)
    assert letti["commento"]["valore"] == "riga uno riga due" and not letti["commento"]["testo"]
    # Una chiave personale che si chiama come un tag comune resta sua.
    tag.scrivi(flac_p, "~titolo", "Cambiato")
    flac = FLAC(flac_p)
    assert flac["titolo"] == ["Cambiato"] and "title" not in flac
    # Lo schedario trova l'anno anche in YEAR.
    assert schedario.leggi_scheda(flac_p)["tag"]["anno"] == 1987
    # Le date di ID3 si controllano.
    mp3 = _copia(file_muti, "mp3", tmp_path)
    id3 = ID3(mp3)
    id3.add(TDOR(encoding=3, text=["1970"]))
    id3.save()
    with pytest.raises(tag.ErroreTag):
        tag.scrivi(mp3, "~TDOR", "primavera")
    tag.scrivi(mp3, "~TDOR", "1971-05-21")
    assert _tag(mp3)["~TDOR"]["valore"] == "1971-05-21"
    assert tag.controlla("anno", "2012-03-26T07:00:00Z") == "2012-03-26T07:00:00Z"
    # Un atomo freeform binario si legge ma non si modifica.
    m4a = _copia(file_muti, "m4a", tmp_path)
    mp4 = MP4(m4a)
    mp4["----:com.apple.iTunes:Encoding Params"] = [MP4FreeForm(b"vers\x00\x01", dataformat=AtomDataType.IMPLICIT)]
    mp4["----:com.apple.iTunes:MOOD"] = [MP4FreeForm(b"Allegro")]
    mp4.save()
    letti = _tag(m4a)
    assert not letti["~----:com.apple.iTunes:Encoding Params"]["testo"] and letti["~----:com.apple.iTunes:MOOD"]["valore"] == "Allegro"

def test_lo_schedario_rilegge_i_formati_senza_tag(tmp_path):
    import json

    file = tmp_path / "schedario.json"
    vecchia = {"dim": 1, "mod": 1.0, "durata": 3.0, "tag": {}, "sottobrani": None, "durate_sid": None}
    file.write_text(json.dumps({"versione": schedario.VERSIONE_DEL_FILE, "schede": {
        r"C:\m\a.wav": vecchia, r"C:\m\b.wma": vecchia, r"C:\m\c.mp3": vecchia, r"C:\m\d.wav": {**vecchia, "tag_v": 1},
        r"C:\m\e.wav": {**vecchia, "tag_v": 2}, r"C:\m\f.wma": {**vecchia, "tag_v": 1}}}), encoding="utf-8")
    s = schedario.Schedario(str(file))
    s.carica()
    # I WAV si rileggono anche se schedati dalla 1.69.0, che non leggeva il blocco INFO.
    assert sorted(s.schede) == [r"C:\m\c.mp3", r"C:\m\e.wav", r"C:\m\f.wma"]


def _wav_con_info(percorso, campi=None):
    """Un WAV fatto a mano: fmt, il blocco INFO se ci sono campi, e mezzo
    secondo di dati, di valori diversi per riconoscerli dopo."""
    import struct

    fmt = struct.pack("<HHIIHH", 1, 2, 48000, 48000 * 4, 4, 16)
    dati = bytes(range(256)) * 375
    spezzoni = b"fmt " + struct.pack("<I", len(fmt)) + fmt
    if campi:
        corpo = b""
        for nome, testo in campi.items():
            byte = testo.encode("cp1252") + b"\x00"
            corpo += nome.encode() + struct.pack("<I", len(byte)) + byte + (b"\x00" if len(byte) & 1 else b"")
        spezzoni += b"LIST" + struct.pack("<I", 4 + len(corpo)) + b"INFO" + corpo
    spezzoni += b"data" + struct.pack("<I", len(dati)) + dati
    percorso.write_bytes(b"RIFF" + struct.pack("<I", 4 + len(spezzoni)) + b"WAVE" + spezzoni)
    return str(percorso), dati


def _controlla_il_wav(percorso, dati):
    """Il RIFF ha la dimensione giusta, e l'audio e' quello di prima."""
    import struct

    with open(percorso, "rb") as f:
        byte = f.read()
    assert struct.unpack("<I", byte[4:8])[0] == len(byte) - 8
    with wave.open(percorso) as f:
        assert f.readframes(f.getnframes()) == dati


def test_il_blocco_info_dei_wav(tmp_path):
    from mutagen.wave import WAVE

    percorso, dati = _wav_con_info(tmp_path / "con_info.wav", {"INAM": "Vecchio titolo", "ICOP": "(c) 2001 Gabriele", "ISFT": "Registratore"})
    letti = _tag(percorso)
    assert letti["titolo"]["valore"] == "Vecchio titolo"
    assert letti["~INFO:ICOP"]["nome"] == "Copyright" and letti["~INFO:ICOP"]["valore"] == "(c) 2001 Gabriele"
    assert schedario.leggi_scheda(percorso)["tag"]["titolo"] == "Vecchio titolo"
    # Un tag comune va in ID3 e nel blocco INFO; gli altri campi restano.
    tag.scrivi(percorso, "titolo", "Nuovo è")
    assert str(WAVE(percorso).tags["TIT2"]) == "Nuovo è"
    assert tag.leggi_info(percorso) == {"INAM": "Nuovo è", "ICOP": "(c) 2001 Gabriele", "ISFT": "Registratore"}
    _controlla_il_wav(percorso, dati)
    # Un campo che ID3 non ha si scrive e si toglie solo nel blocco INFO.
    tag.scrivi(percorso, "~INFO:ICOP", "")
    tag.scrivi(percorso, "~INFO:ISFT", "MeTeOra")
    assert tag.leggi_info(percorso) == {"INAM": "Nuovo è", "ISFT": "MeTeOra"}
    _controlla_il_wav(percorso, dati)


def test_il_blocco_info_nasce_e_i_falsi_wav(tmp_path):
    percorso, dati = _wav_con_info(tmp_path / "senza_info.wav")
    tag.scrivi(percorso, "artista", "Gabriele")
    assert tag.leggi_info(percorso) == {"IART": "Gabriele"} and _tag(percorso)["artista"]["valore"] == "Gabriele"
    _controlla_il_wav(percorso, dati)
    # Il blocco svuotato sparisce.
    tag.scrivi(percorso, "artista", "")
    assert tag.leggi_info(percorso) == {}
    _controlla_il_wav(percorso, dati)
    finto = tmp_path / "finto.wav"
    finto.write_bytes(b"niente di buono")
    assert tag.leggi_info(str(finto)) == {}
    with pytest.raises(tag.ErroreTag):
        tag.scrivi_info(str(finto), {"INAM": "x"})


def _spezzoni_del_file(percorso):
    with open(percorso, "rb") as f:
        return [s[0] for s in tag._Riff(f).spezzoni]


def test_i_wav_senza_riempimento_del_modulo_wave(tmp_path):
    # Il modulo wave di Python non scrive il riempimento dopo dati dispari.
    percorso = str(tmp_path / "dispari.wav")
    with wave.open(percorso, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(1)
        f.setframerate(8000)
        f.writeframes(bytes(range(256)) * 10 + b"\x01")
    with wave.open(percorso) as f:
        dati = f.readframes(f.getnframes())
    for titolo in ("Uno", "Due", "Tre"):
        tag.scrivi(percorso, "titolo", titolo)
    assert _spezzoni_del_file(percorso).count(b"LIST") == 1 and _spezzoni_del_file(percorso).count(b"id3 ") == 1
    assert tag.leggi_info(percorso) == {"INAM": "Tre"} and _tag(percorso)["titolo"]["valore"] == "Tre"
    _controlla_il_wav(percorso, dati)


def test_un_wav_irregolare_non_si_tocca(tmp_path):
    import struct

    # Una registrazione interrotta: RIFF e data mai finiti, l'audio dopo.
    fmt = struct.pack("<HHIIHH", 1, 2, 48000, 48000 * 4, 4, 16)
    interrotta = tmp_path / "interrotta.wav"
    interrotta.write_bytes(b"RIFF" + struct.pack("<I", 36) + b"WAVEfmt " + struct.pack("<I", 16) + fmt + b"data" + struct.pack("<I", 0) + bytes(range(250)) * 16)
    prima = interrotta.read_bytes()
    with pytest.raises(tag.ErroreTag, match="non è regolare"):
        tag.scrivi(str(interrotta), "titolo", "x")
    assert interrotta.read_bytes() == prima
    # Un RIFF dispari che non conta il riempimento si scrive bene.
    dati = bytes(range(101))
    dispari = tmp_path / "riff_dispari.wav"
    fmt8 = struct.pack("<HHIIHH", 1, 1, 8000, 8000, 1, 8)
    dispari.write_bytes(b"RIFF" + struct.pack("<I", 4 + 24 + 8 + 101) + b"WAVEfmt " + struct.pack("<I", 16) + fmt8 + b"data" + struct.pack("<I", 101) + dati + b"\x00")
    tag.scrivi(str(dispari), "titolo", "Uno")
    tag.scrivi(str(dispari), "titolo", "Due")
    assert tag.leggi_info(str(dispari)) == {"INAM": "Due"} and _spezzoni_del_file(str(dispari)).count(b"LIST") == 1
    _controlla_il_wav(str(dispari), dati)


def test_due_blocchi_info_e_caratteri_fuori_dalla_cp1252(tmp_path):
    import struct

    percorso, dati = _wav_con_info(tmp_path / "doppio.wav", {"INAM": "Primo", "ICOP": "Vecchio"})
    # Un secondo blocco INFO in coda, con un ICOP diverso.
    secondo = b"ICOP" + struct.pack("<I", 8) + b"Secondo\x00"
    with open(percorso, "ab") as f:
        f.write(b"LIST" + struct.pack("<I", 4 + len(secondo)) + b"INFO" + secondo)
    with open(percorso, "rb+") as f:
        f.seek(0, os.SEEK_END)
        totale = f.tell()
        f.seek(4)
        f.write(struct.pack("<I", totale - 8))
    assert tag.leggi_info(percorso) == {"INAM": "Primo", "ICOP": "Vecchio"}
    # Togliere un campo lo toglie da tutti i blocchi, che diventano uno.
    tag.scrivi(percorso, "~INFO:ICOP", "")
    assert tag.leggi_info(percorso) == {"INAM": "Primo"} and _spezzoni_del_file(percorso).count(b"LIST") == 1
    _controlla_il_wav(percorso, dati)
    # Un testo che la cp1252 non sa scrivere va in UTF-8, e si rilegge uguale.
    tag.scrivi(percorso, "~INFO:ISBJ", "音楽 è")
    assert tag.leggi_info(percorso)["ISBJ"] == "音楽 è"
    # Una scrittura che non cambia niente lascia il file com'era.
    with open(percorso, "rb") as f:
        prima = f.read()
    tag.scrivi_info(percorso, {"INAM": "Primo"})
    with open(percorso, "rb") as f:
        assert f.read() == prima
