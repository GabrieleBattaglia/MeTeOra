# MeTeOra, le prove della precedenza della finestra sui fili in disparte (2.7.1).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con precedenza.py, nella 2.7.1.

import time

from precedenza import Cedi


def test_si_usa_come_un_evento():
    cedi = Cedi()
    assert not cedi.is_set()
    cedi.set()
    assert cedi.is_set()
    cedi.clear()
    assert not cedi.is_set() and cedi.trattenuto() == 0.0


def test_trattenuto_per_un_tasto():
    # A ogni tasto il segnale resta alzato per un attimo, anche se la
    # finestra intanto lo abbassa alla fine di una fetta.
    cedi = Cedi()
    cedi.trattieni(0.2)
    cedi.set()
    cedi.clear()
    assert cedi.is_set() and 0.0 < cedi.trattenuto() <= 0.2
    # Un tasto dopo l'altro allunga, non accorcia.
    cedi.trattieni(0.05)
    assert cedi.trattenuto() > 0.1
    time.sleep(0.25)
    assert not cedi.is_set() and cedi.trattenuto() == 0.0
