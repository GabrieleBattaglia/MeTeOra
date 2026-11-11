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
        "subtitles": {"de": [{"ext": "json3", "url": "https://s/de.json"}, {"ext": "vtt", "url": "https://s/de.vtt"}]},
        "automatic_captions": {"en": [{"ext": "vtt", "url": "https://a/en.vtt"}], "fr": [{"ext": "vtt", "url": "https://a/fr.vtt"}],
            "it": [{"ext": "vtt", "url": "https://a/it.vtt"}]}}
    # Prima l'italiano, la lingua di MeTeOra; dei sottotitoli automatici solo
    # quelli della lingua del video e dell'italiano.
    assert indirizzi.sottotitoli_dell_info(info) == ["https://a/it.vtt", "https://s/de.vtt", "https://a/en.vtt"]
    assert indirizzi.sottotitoli_dell_info({}) == []
