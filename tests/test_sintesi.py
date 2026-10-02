# MeTeOra, le prove della sintesi dei sottotitoli.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 7.

"""Le uscite sono finte, dal conftest: nessuna prova parla."""

import sintesi


def test_disponibili_e_automatica(sintesi_finta):
    assert sintesi.disponibili() == ["nvda", "sapi5"]
    voce = sintesi.Sintesi()
    assert voce.scelta(sintesi.AUTOMATICA) == "nvda"
    sintesi_finta.attive["jaws"] = True
    sintesi_finta.attive["nvda"] = False
    assert voce.scelta(sintesi.AUTOMATICA) == "jaws"
    sintesi_finta.attive["jaws"] = False
    assert voce.scelta(sintesi.AUTOMATICA) == "sapi5"
    sintesi_finta.presenti.discard("sapi5")
    assert sintesi.Sintesi().scelta(sintesi.AUTOMATICA) is None


def test_dici_con_la_scelta_e_senza_uscite(sintesi_finta):
    voce = sintesi.Sintesi()
    assert voce.dici("uno") is True and voce.dici("due", "sapi5") is True
    assert sintesi_finta.detti == [("nvda", "uno"), ("sapi5", "due")]
    # Una scelta che non risponde non dice niente, e non ricade su altre.
    assert voce.dici("tre", "jaws") is False and voce.dici("quattro", "festival") is False
    assert len(sintesi_finta.detti) == 2


def test_un_uscita_che_si_rompe_non_ferma_niente(sintesi_finta, monkeypatch):
    voce = sintesi.Sintesi()
    rotta = voce._uscita("nvda")

    def errore(_testo, interrupt=False):
        raise OSError("NVDA chiuso")

    monkeypatch.setattr(rotta, "output", errore)
    assert voce.dici("uno", "nvda") is False
    # L'uscita si riapre alla richiesta dopo.
    assert voce.dici("due", "nvda") is True and sintesi_finta.detti == [("nvda", "due")]


def test_i_nomi_da_leggere():
    assert sintesi.nome(sintesi.AUTOMATICA) == "automatica"
    assert sintesi.nome("nvda") == "NVDA" and sintesi.nome("sapi5") == "la voce di Windows, SAPI5"
