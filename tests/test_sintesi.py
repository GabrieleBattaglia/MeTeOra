# MeTeOra, le prove della sintesi dei sottotitoli.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 7.

"""Le uscite sono finte, dal conftest: nessuna prova parla."""

import sintesi

# La _crea vera: il conftest la sostituisce in ogni prova.
_CREA_VERA = sintesi._crea


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

    monkeypatch.setattr(rotta, "speak", errore)
    assert voce.dici("uno", "nvda") is False
    # L'uscita si riapre alla richiesta dopo.
    assert voce.dici("due", "nvda") is True and sintesi_finta.detti == [("nvda", "due")]


def test_i_nomi_da_leggere():
    assert sintesi.nome(sintesi.AUTOMATICA) == "automatica"
    assert sintesi.nome("nvda") == "NVDA" and sintesi.nome("sapi5") == "la voce di Windows, SAPI5"


def test_dove_vanno_i_testi(sintesi_finta):
    # 1.82.0: voce e braille, uno per uno; la voce di Windows il braille non ce l'ha.
    voce = sintesi.Sintesi()
    assert voce.dici("uno") and voce.dici("due", dove="sintesi") and voce.dici("tre", dove="braille")
    assert sintesi_finta.detti == [("nvda", "uno"), ("nvda", "due")] and sintesi_finta.braille == [("nvda", "uno"), ("nvda", "tre")]
    assert voce.dici("quattro", "sapi5", "braille") and sintesi_finta.braille[-1] == ("nvda", "tre")
    assert set(sintesi.DESTINAZIONI) == {"entrambi", "sintesi", "braille"}


def test_la_voce_di_windows_si_apre_anche_senza_l_elenco_delle_voci(monkeypatch):
    # 1.83.3: accessible_output2 legge l'elenco delle voci all'apertura, e sul
    # PC di Gabriele l'elenco fallisce: la voce di Windows la apre MeTeOra.
    import win32com.client

    detti = []

    class Voce:
        def Speak(self, testo, segni):
            detti.append((testo, segni))

    def rotto(_nome):
        raise RuntimeError("elenco delle voci non letto")

    monkeypatch.setattr(sintesi.importlib, "import_module", rotto)
    monkeypatch.setattr(win32com.client, "Dispatch", lambda nome: Voce() if nome == "SAPI.SpVoice" else None)
    voce = _CREA_VERA("sapi5")
    assert type(voce).__name__ == "_VoceDiWindows" and voce.is_active() and voce.braille("x") is False
    voce.speak("ciao")
    voce.speak("basta", interrupt=True)
    assert detti == [("ciao", 1), ("basta", 3)]
    # Le altre uscite, se non si aprono, restano chiuse.
    assert _CREA_VERA("nvda") is None
    monkeypatch.setattr(win32com.client, "Dispatch", lambda nome: (_ for _ in ()).throw(OSError("niente SAPI")))
    assert _CREA_VERA("sapi5") is None
