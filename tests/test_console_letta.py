# MeTeOra, le prove della console letta da sola, dei capitoli detti suonando e dei sottotitoli dei siti.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 11/11/2026: nasce con la 3.8.0, issue 44 e 45.

import types

import wx

import finestra as modulo
import indirizzi


def _letti(finestra, monkeypatch):
    """Quello che va alla sintesi e al braille: (testo, dove)."""
    detti = []
    monkeypatch.setattr(finestra._sintesi, "dici", lambda testo, _scelta, dove, interrompi=False: detti.append((testo, dove)))
    monkeypatch.setattr(finestra._sintesi, "scelta", lambda _chiave: "nvda")
    return detti


def test_la_console_letta_da_sola_senza_ripetere(finestra, monkeypatch):
    detti = _letti(finestra, monkeypatch)
    finestra.impostazioni["console_letta"] = "braille"
    finestra.scrivi("Prima riga")
    # Dove sono va gia' alla sintesi dei sottotitoli: la console non lo ripete.
    finestra.impostazioni["destinazione"] = "sintesi"
    finestra._ai_testi_letti("Gia' letta")
    finestra.scrivi("Gia' letta")
    finestra._leggi_le_righe()
    assert ("Prima riga", "braille") in detti
    assert [d for d in detti if d[0] == "Gia' letta"] == [("Gia' letta", "sintesi")]
    assert finestra._statistiche.dati["conti"]["righe_lette"] == 1
    # Spenta, niente.
    detti.clear()
    finestra.impostazioni["console_letta"] = "spenta"
    finestra.scrivi("Muta")
    finestra._leggi_le_righe()
    assert not detti


def test_la_famiglia_di_f10(finestra, monkeypatch, suoni_annotati):
    from test_finestra import _tasto, _ultima

    detti = _letti(finestra, monkeypatch)
    _tasto(finestra, codice=wx.WXK_F10, maiuscolo=True)
    assert finestra.impostazioni["console_letta"] == "braille" and suoni_annotati[-1] == "console_letta"
    assert _ultima(finestra) == "La console si legge da sola, solo al braille."
    _tasto(finestra, codice=wx.WXK_F10, ctrl=True, maiuscolo=True)
    assert finestra.impostazioni["console_letta"] == "entrambi"
    _tasto(finestra, codice=wx.WXK_F10, maiuscolo=True)
    assert suoni_annotati[-1] == "console_letta_al_limite" and _ultima(finestra) == "La console si legge già al braille e alla sintesi."
    _tasto(finestra, codice=wx.WXK_F10, ctrl=True)
    assert finestra.impostazioni["console_letta"] == "braille"
    detti.clear()
    _tasto(finestra, codice=wx.WXK_F10, ctrl=True, alt=True)
    # Spenta, l'ultima riga si dice ancora, dove andava prima.
    assert finestra.impostazioni["console_letta"] == "spenta" and ("La console non si legge da sola.", "braille") in detti
    _tasto(finestra, codice=wx.WXK_F10, ctrl=True)
    assert suoni_annotati[-1] == "console_letta_al_limite" and _ultima(finestra) == "La lettura della console è già spenta."


def test_il_capitolo_nuovo_si_dice_suonando_ma_non_dopo_un_salto(finestra, monkeypatch):
    detti = _letti(finestra, monkeypatch)
    finestra.impostazioni["sottotitoli"] = True
    finestra.impostazioni["destinazione"] = "sintesi"
    finto = types.SimpleNamespace(in_corso="libro.m4b", posizione=8.0)
    orologio = [100.0]
    monkeypatch.setattr(finestra, "motore", finto)
    monkeypatch.setattr(modulo.time, "monotonic", lambda: orologio[0])
    monkeypatch.setattr(finestra, "_capitoli_in_corso", lambda: [(0.0, "Uno"), (10.0, "Due"), (60.0, "Tre")])
    finestra._guarda_il_capitolo()
    righe = len(finestra._righe)
    # Un secondo dopo, due secondi piu' avanti: entrato in Due da se'.
    finto.posizione, orologio[0] = 10.2, 101.0
    finestra._guarda_il_capitolo()
    assert len(finestra._righe) == righe + 1 and finestra._righe[-1].startswith("Capitolo 2 di 3: Due, 0:10")
    assert any(testo.startswith("Capitolo 2 di 3") for testo, _dove in detti)
    # Un salto a Tre non si dice: lo dicono i comandi dei capitoli.
    finto.posizione, orologio[0] = 61.0, 102.0
    finestra._guarda_il_capitolo()
    assert len(finestra._righe) == righe + 1
    assert finestra._statistiche.dati["conti"]["capitoli_annunciati"] == 1
    monkeypatch.undo()


def test_i_sottotitoli_di_un_sito():
    info = {"language": "en",
        "subtitles": {"de": [{"ext": "json3", "url": "https://s/de.json"}, {"ext": "vtt", "url": "https://s/de.vtt", "name": "Deutsch", "http_headers": {"Referer": "https://s/"}}]},
        "automatic_captions": {"en-orig": [{"ext": "vtt", "url": "https://a/en.vtt", "name": "English (Original)"}], "en": [{"ext": "vtt", "url": "https://a/en.vtt"}],
            "fr": [{"ext": "vtt", "url": "https://a/fr.vtt"}], "it": [{"ext": "vtt", "url": "https://a/en.vtt?tlang=it", "name": "Italian"}]}}
    # Prima l'italiano, la lingua di MeTeOra; dei sottotitoli automatici solo
    # quelli della lingua del video e dell'italiano, e un indirizzo una volta sola.
    tracce = indirizzi.sottotitoli_dell_info(info)
    assert [t.indirizzo for t in tracce] == ["https://a/en.vtt?tlang=it", "https://s/de.vtt", "https://a/en.vtt"]
    assert indirizzi.sottotitoli_dell_info({}) == []
    # Ognuna con la lingua, il nome e le intestazioni di yt-dlp (Gabriele, 15
    # novembre 2026): il titolo dice se sono automatici, e tradotti dal sito.
    italiano, tedesco, inglese = tracce
    assert (italiano.lingua, italiano.automatici, italiano.tradotti, italiano.titolo) == ("it", True, True, "automatici, tradotti")
    assert (tedesco.lingua, tedesco.nome, tedesco.automatici, tedesco.titolo, tedesco.intestazioni) == ("de", "Deutsch", False, "Deutsch", ("Referer: https://s/",))
    assert (inglese.lingua, inglese.nome, inglese.tradotti, inglese.titolo) == ("en", "English (Original)", False, "automatici")
    assert indirizzi.Sottotitoli("https://s/x.vtt").titolo == "del sito"
    # Il flusso li porta tutti, come Sottotitoli.
    flusso = indirizzi.flusso_dell_info({**info, "url": "https://a/audio.webm", "protocol": "https"})
    assert flusso.sottotitoli == tuple(tracce)
    # D dice la lingua anche dal codice di due lettere.
    assert modulo._descrivi_traccia({"lang": "it", "title": "automatici", "codec": "webvtt"}, 0, 2) == "1 di 2, italiano, automatici, webvtt"
    assert modulo._descrivi_traccia({"lang": "en", "title": "English", "codec": "webvtt"}, 1, 2) == "2 di 2, inglese, English, webvtt"


# L'inizio dei sottotitoli automatici veri di un video di Superquark su
# YouTube, che scorrono, con i cue di 10 millesimi (3.19.1).
WEBVTT_DI_SUPERQUARK = ("WEBVTT\nKind: captions\nLanguage: it\n\n"
    "00:00:00.000 --> 00:00:01.790 align:start position:0%\n \nLeen<00:00:00.560><c> per</c><00:00:00.719><c> la</c><00:00:00.840><c> canzone</c>\n\n"
    "00:00:01.790 --> 00:00:01.800 align:start position:0%\nLeen per la canzone\n \n\n"
    "00:00:01.800 --> 00:00:04.230 align:start position:0%\nLeen per la canzone\nCaruso<00:00:02.800><c> che</c><00:00:02.919><c> ha</c><00:00:03.120><c> avuto</c>\n\n"
    "00:00:04.230 --> 00:00:04.240 align:start position:0%\nCaruso che ha avuto\n \n\n"
    "00:00:04.240 --> 00:00:06.470 align:start position:0%\nCaruso che ha avuto\nsappiamo<00:00:04.600><c> si</c><00:00:04.800><c> è</c><00:00:05.000><c> trovato</c>\n\n")


def test_i_sottotitoli_dei_siti_nella_finestra_con_lo_speaker(finestra, monkeypatch, sintesi_finta):
    # Gabriele, 15 novembre 2026: con lo speaker i sottotitoli di YouTube si
    # leggono dal loro file. Con i sottotitoli accesi la prima traccia si
    # sceglie da sola, D la dice con la lingua e il titolo, e le righe che
    # scorrono si dicono una volta sola, come sul PC.
    import time

    from test_finestra import _premi
    from test_karaoke import _SpeakerFinto

    def aspetta(condizione):
        fine = time.time() + 5
        while time.time() < fine and not condizione():
            wx.Yield()
            time.sleep(0.02)
        return condizione()

    monkeypatch.setattr(indirizzi, "scarica_i_sottotitoli", lambda _traccia, _intestazioni=(), _attesa=None, serve=None: WEBVTT_DI_SUPERQUARK)
    pagina = "https://www.youtube.com/watch?v=yXWQ_voCgwU"
    indirizzi._tieni(pagina, False, indirizzi.Flusso("https://a/audio.webm", sottotitoli=[indirizzi.Sottotitoli("https://a/it.vtt", "it", "Italian (Original)", True)]))
    speaker = _SpeakerFinto()
    finestra.motore.usa_il_lontano(speaker)
    finestra.impostazioni["sottotitoli"] = True
    finestra.impostazioni["destinazione"] = "sintesi"
    try:
        finestra.motore.suona(pagina)
        assert aspetta(lambda: [t["selected"] for t in (finestra.motore.tracce() or {}).get("sub", [])] == [True])
        assert _premi(finestra, "d") == "Sottotitoli letti, traccia 1 di 1, italiano, automatici, webvtt; scelta 2 di 2: spenti, 1 traccia."
        for posizione in (0.5, 1.2, 2.0, 3.5, 4.5, 5.5):
            speaker.posizione = posizione
            time.sleep(0.15)
            wx.Yield()
        assert aspetta(lambda: [t for _n, t in sintesi_finta.detti if not t.startswith("Sottotitoli")] == ["Leen per la canzone", "Caruso che ha avuto",
            "sappiamo si è trovato"])
        conti = finestra._statistiche.dati["conti"]
        assert conti["righe_dei_sottotitoli"] == conti["righe_allo_speaker"] == conti["righe_dei_siti_allo_speaker"] == 3
    finally:
        finestra.motore.usa_il_lontano(None)
