# MeTeOra, le prove di Questa rete.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la 1.64.0.

"""I percorsi salvati si leggono da una cartella temporanea con collegamenti
veri; la rete vera non si tocca."""

import time

import questa_rete


def _collegamento(percorso_lnk, bersaglio):
    import pythoncom
    from win32com.shell import shell

    link = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
    link.SetPath(bersaglio)
    link.QueryInterface(pythoncom.IID_IPersistFile).Save(str(percorso_lnk), 0)


def test_percorsi_salvati(tmp_path):
    (tmp_path / "zeta (server)").mkdir()
    _collegamento(tmp_path / "zeta (server)" / "target.lnk", r"\\server\zeta")
    (tmp_path / "Alfa (nas)").mkdir()
    _collegamento(tmp_path / "Alfa (nas)" / "target.lnk", "\\\\nas\\alfa\\")
    _collegamento(tmp_path / "beta.lnk", r"\\nas\beta")
    # Un collegamento a una cartella del PC, e un file qualsiasi, non contano.
    _collegamento(tmp_path / "locale.lnk", str(tmp_path))
    (tmp_path / "desktop.ini").write_text("[.ShellClassInfo]")
    assert questa_rete.percorsi_salvati(str(tmp_path)) == [("Alfa (nas)", r"\\nas\alfa"), ("beta", r"\\nas\beta"), ("zeta (server)", r"\\server\zeta")]
    assert questa_rete.percorsi_salvati(str(tmp_path / "non c'e'")) == []


def test_e_di_rete():
    assert questa_rete.e_di_rete(r"\\server\cartella") and not questa_rete.e_di_rete(r"C:\musica")


def test_raggiungibile_smette_di_aspettare(tmp_path):
    assert questa_rete.raggiungibile(str(tmp_path)) is True
    assert questa_rete.raggiungibile(str(tmp_path / "non c'e'")) is False
    inizio = time.perf_counter()
    questa_rete.raggiungibile(r"\\nessun-computer-di-prova-meteora\niente", attesa=0.5)
    assert time.perf_counter() - inizio < 2
