# MeTeOra, le prove dell'aggiornamento automatico: le novita' fra due versioni, il filo del controllo e la finestra.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.84.0.

"""GitHub e GBUtils sono finti: le prove non scaricano e non aggiornano niente."""

import sys

import wx

import aggiornamento
import dialoghi

CHANGELOG = """# Changelog - MeTeOra

Tutti i cambiamenti.

## [1.85.0] - 2026-10-06

- Terza novita'.

## [1.84.1] - 2026-10-05

- Seconda novita'.
- Ancora la seconda.

## [1.84.0] - 2026-10-04

- Prima novita'.

## [1.83.3] - 2026-10-04

- Vecchia.
"""


def test_le_novita_fra_due_versioni():
    testo = aggiornamento.novita_fra(CHANGELOG, "1.84.0", "1.85.0")
    assert testo == ("Versione 1.85.0 del 2026-10-06:\nTerza novita'.\nVersione 1.84.1 del 2026-10-05:\nSeconda novita'.\n"
        "Ancora la seconda.")
    assert aggiornamento.novita_fra(CHANGELOG, "1.83.3", "1.84.0") == "Versione 1.84.0 del 2026-10-04:\nPrima novita'."
    assert aggiornamento.novita_fra(CHANGELOG, "1.85.0", "1.85.0") == ""
    assert aggiornamento.numeri("v1.84.10") == (1, 84, 10) and aggiornamento.numeri("1.9") < aggiornamento.numeri("1.10")


def test_da_sorgente_non_si_controlla(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert aggiornamento.controlla(object()) is None


class _FinestraFinta:
    def __init__(self, accetta=True):
        self.chiusa, self.accetta, self.fatti = False, accetta, []

    def proponi_l_aggiornamento(self, attuale, nuova, novita, attesa=None):
        self.fatti.append(("proponi", attuale, nuova, novita, attesa))
        return self.accetta

    def avvisa_dell_aggiornamento(self, testo):
        self.fatti.append(("avvisa", testo))

    def avanzamento_dell_aggiornamento(self, presi, totale):
        self.fatti.append(("avanzamento", presi, totale))

    def chiudi_per_aggiornare(self):
        self.fatti.append(("chiudi",))


def _subito(funzione, *argomenti):
    """Il filo della finestra, finto: la funzione si fa subito."""
    funzione(*argomenti)


def test_il_filo_del_controllo(monkeypatch):
    import GBUtils

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(aggiornamento, "scarica_le_novita", lambda da, a: f"novita' dalla {da} alla {a}")
    chiamate = []

    def gestisci(app, versione, api, proponi, avvisa, avanzamento):
        chiamate.append((app, versione, api))
        if not proponi(versione, "9.0.0", "note della release", attesa=120):
            return False
        avanzamento(50, 100)
        avvisa("MeTeOra si chiude per aggiornarsi.")
        return True

    monkeypatch.setattr(GBUtils, "gestisci_aggiornamento", gestisci)
    finestra = _FinestraFinta()
    aggiornamento.controlla(finestra, chiama_dopo=_subito).join(5)
    versione = aggiornamento.version.VERSION
    assert chiamate == [("MeTeOra", versione, aggiornamento.API)]
    assert finestra.fatti == [("proponi", versione, "9.0.0", f"novita' dalla {versione} alla 9.0.0", 120), ("avanzamento", 50, 100),
        ("avvisa", "MeTeOra si chiude per aggiornarsi."), ("chiudi",)]
    # Senza le novita' dal changelog valgono le note; e chi rimanda non chiude.
    monkeypatch.setattr(aggiornamento, "scarica_le_novita", lambda da, a: None)
    finestra = _FinestraFinta(accetta=False)
    aggiornamento.controlla(finestra, chiama_dopo=_subito).join(5)
    assert finestra.fatti == [("proponi", versione, "9.0.0", "note della release", 120)]
    # Una finestra gia' chiusa non risponde: vale come no.
    finestra = _FinestraFinta()
    finestra.chiusa = True
    aggiornamento.controlla(finestra, chiama_dopo=_subito).join(5)
    assert finestra.fatti == []


def test_la_finestra_dell_aggiornamento(app):
    cornice = wx.Frame(None)
    try:
        dialogo = dialoghi.FinestraAggiornamento(cornice, "1.83.3", "1.84.0", "Versione 1.84.0 del 2026-10-04:\nPrima novita'.", attesa=120)
        try:
            testo = dialogo.testo.GetValue()
            assert testo.startswith("È disponibile MeTeOra 1.84.0; tu hai la 1.83.3.") and "entro 2 minuti" in testo
            assert testo.endswith("Le novità:\nVersione 1.84.0 del 2026-10-04:\nPrima novita'.")
            assert dialogo.GetEscapeId() == wx.ID_NO and dialogo.non_adesso.GetLabelText() == "Non adesso"
            assert dialogo.aggiorna.GetLabelText() == "Aggiorna adesso" and dialogo.testo.GetName() == "Aggiornamento di MeTeOra"
            # Invio nel testo vale Non adesso.
            chiusa = []
            dialogo.EndModal = chiusa.append
            evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
            evento.SetKeyCode(wx.WXK_RETURN)
            evento.SetEventObject(dialogo.testo)
            dialogo._tasto(evento)
            assert chiusa == [wx.ID_NO]
        finally:
            dialogo.Destroy()
        assert dialoghi.durata_dell_attesa(90) == "90 secondi" and dialoghi.durata_dell_attesa(60) == "1 minuto"
        assert dialoghi.durata_dell_attesa(120) == "2 minuti"
    finally:
        cornice.Destroy()
