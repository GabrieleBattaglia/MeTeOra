# MeTeOra, le prove: desktop nascosto, suoni muti, cartelle temporanee.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1, sul modello di tests/conftest.py di Tornello.
# 03/10/2026, 1.72.0: os.startfile vietato, perche' F1 apre il manuale nel browser.
# 04/10/2026, 1.75.0: il browser vietato e Donazione muta, per l'invito a offrire un caffe'.

"""Le regole comuni delle prove.

Le finestre nascono su un desktop di Windows nascosto, creato prima che wx
ne crei una qualunque: Windows da' il primo piano anche a una finestra mai
mostrata quando riceve il fuoco, e senza questo passaggio le prove
ruberebbero il fuoco allo schermo di chi le lancia, con NVDA che ne legge i
titoli. Se il passaggio non riesce, la suite non parte.
Gli effetti sonori sono sostituiti da una funzione che li annota soltanto,
e il motore suona sull'uscita nulla: le prove non fanno rumore.
"""

import ctypes
import os
import sys
from ctypes import wintypes

import pytest

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

NOME_DEL_DESKTOP = f"meteora_prove_{os.getpid()}"
GENERIC_ALL = 0x10000000
_DESKTOP = {}


def _user32():
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.CreateDesktopW.restype = wintypes.HANDLE
    user32.CreateDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
    user32.SetThreadDesktop.restype = wintypes.BOOL
    user32.SetThreadDesktop.argtypes = [wintypes.HANDLE]
    return user32


def pytest_configure(config):
    """Il passaggio al desktop nascosto, prima che le prove creino wx.App."""
    if sys.platform != "win32" or _DESKTOP:
        return
    user32 = _user32()
    desktop = user32.CreateDesktopW(NOME_DEL_DESKTOP, None, None, 0, GENERIC_ALL, None)
    if not desktop:
        raise pytest.UsageError(f"Le prove non partono: il desktop nascosto non si crea (errore {ctypes.get_last_error()}).")
    if not user32.SetThreadDesktop(desktop):
        raise pytest.UsageError(f"Le prove non partono: il passaggio al desktop nascosto non riesce (errore {ctypes.get_last_error()}).")
    _DESKTOP["maniglia"] = desktop


@pytest.fixture(autouse=True)
def suoni_annotati(monkeypatch):
    """Ogni effetto sonoro finisce in una lista invece che negli altoparlanti."""
    import suoni

    suonati = []

    def annota(evento, volume=0.5, sync=False):
        assert evento in suoni.EVENTI, f"evento sconosciuto: {evento}"
        suonati.append(evento)
        return True

    monkeypatch.setattr(suoni, "suona", annota)
    return suonati


@pytest.fixture(autouse=True)
def startfile_vietato(monkeypatch):
    """os.startfile non apre mai niente durante le prove: un browser, come
    quello del manuale di F1, comparirebbe davanti a chi le lancia e NVDA ne
    leggerebbe il titolo. Una prova che lo chiama senza sostituirlo fallisce."""

    def vietato(*argomenti, **opzioni):
        raise AssertionError(f"os.startfile chiamato da una prova senza sostituirlo: {argomenti}")

    monkeypatch.setattr(os, "startfile", vietato, raising=False)


@pytest.fixture(autouse=True)
def browser_vietato(monkeypatch):
    """webbrowser.open non apre mai niente durante le prove, come os.startfile:
    il pulsante Dona con PayPal lo chiama."""
    import webbrowser

    def vietato(*argomenti, **opzioni):
        raise AssertionError(f"webbrowser.open chiamato da una prova senza sostituirlo: {argomenti}")

    monkeypatch.setattr(webbrowser, "open", vietato)


@pytest.fixture(autouse=True)
def donazione_muta(monkeypatch):
    """Donazione di GBUtils non da' mai il testo: l'invito aprirebbe una
    finestra modale che fermerebbe la suite. Dalla 1.102.4 lo apre solo la
    voce delle impostazioni; le prove dell'invito la sostituiscono a loro
    volta."""
    import GBUtils

    monkeypatch.setattr(GBUtils, "Donazione", lambda *argomenti, **opzioni: None)


@pytest.fixture(autouse=True)
def livelli_annotati(monkeypatch):
    """I beep dei livelli della plancia, che Acusticator crea al momento,
    finiscono in una lista loro: le profondita' suonate."""
    import suoni

    livelli = []
    monkeypatch.setattr(suoni, "livello", lambda profondita, volume=0.5: livelli.append(profondita) or True)
    return livelli


@pytest.fixture(autouse=True)
def equalizzatore_annotato(monkeypatch):
    """I suoni dell'equalizzatore fatti al volo, U e I per la banda e O e P
    per il guadagno, finiscono in una lista: ("banda", indice) o
    ("guadagno", dB)."""
    import suoni

    suonati = []
    monkeypatch.setattr(suoni, "banda", lambda indice, volume=0.5: suonati.append(("banda", indice)) or True)
    monkeypatch.setattr(suoni, "guadagno", lambda db, volume=0.5: suonati.append(("guadagno", db)) or True)
    return suonati


@pytest.fixture(autouse=True)
def sintesi_finta(monkeypatch):
    """La sintesi dei sottotitoli non parla mai: le uscite sono finte. Si
    aprono quelle in presenti, sono attive quelle vere in attive (la voce di
    Windows, aperta, lo e' sempre), e i testi detti finiscono in detti, come
    (chiave, testo), quelli mandati al braille in braille. Le prove cambiano
    presenti e attive a piacere."""
    import types

    import sintesi

    stato = types.SimpleNamespace(detti=[], braille=[], presenti={"nvda", "jaws", "sapi5"}, attive={"nvda": True, "jaws": False})

    class Finta:
        def __init__(self, chiave):
            self.chiave = chiave

        def is_active(self):
            return stato.attive.get(self.chiave, False)

        def speak(self, testo, interrupt=False):
            stato.detti.append((self.chiave, testo))

        def braille(self, testo):
            # Come in accessible_output2: la voce di Windows il braille non ce l'ha.
            if self.chiave != "sapi5":
                stato.braille.append((self.chiave, testo))

    monkeypatch.setattr(sintesi, "_crea", lambda chiave: Finta(chiave) if chiave in stato.presenti else None)
    return stato


@pytest.fixture(scope="session")
def app():
    import wx

    applicazione = wx.App(False)
    yield applicazione


@pytest.fixture
def finestra(app, tmp_path):
    """Una finestra vera, mai mostrata, con i dati in una cartella temporanea
    e il motore sull'uscita nulla."""
    from finestra import Finestra

    f = Finestra(ao="null", cartella_dati=str(tmp_path))
    yield f
    if not f._chiusa:
        f.Close(force=True)
    f.Destroy()
