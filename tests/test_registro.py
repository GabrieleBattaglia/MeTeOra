# MeTeOra, le prove del registro degli errori e dei crash: i file, la misura massima, il crash della volta prima.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.89.0.

"""faulthandler e' finto nelle prove nel processo, per non spegnere quello di
pytest; il crash vero si prova in un processo figlio, con il dialogo di
errore di Windows spento, che sul desktop non mostra niente."""

import os
import subprocess
import sys
import textwrap

import pytest

import registro


class _FaulthandlerFinto:
    def __init__(self):
        self.acceso = None

    def enable(self, file, all_threads=True):
        self.acceso = file

    def disable(self):
        self.acceso = None


@pytest.fixture
def faulthandler_finto(monkeypatch):
    finto = _FaulthandlerFinto()
    monkeypatch.setattr(registro, "faulthandler", finto)
    yield finto
    registro.chiudi()


def test_il_registro_scrive_i_problemi_e_si_chiude_pulito(tmp_path, faulthandler_finto):
    assert registro.avvia(str(tmp_path)) is None
    crash = tmp_path / registro.FILE_DEL_CRASH
    assert crash.exists() and faulthandler_finto.acceso is not None
    registro.scrivi("MeTeOra si avvia.")
    try:
        raise ValueError("una prova")
    except ValueError:
        registro.problema(*sys.exc_info())
    registro.chiudi()
    testo = (tmp_path / registro.FILE_DEGLI_ERRORI).read_text(encoding="utf-8")
    assert "MeTeOra si avvia." in testo and "ValueError: una prova" in testo and "Traceback" in testo
    # L'uscita pulita toglie il file del crash, e spegne faulthandler.
    assert not crash.exists() and faulthandler_finto.acceso is None
    # Senza avvia() non si scrive niente, e niente si rompe.
    registro.scrivi("dopo")
    registro.problema(ValueError, ValueError("dopo"), None)
    assert "dopo" not in (tmp_path / registro.FILE_DEGLI_ERRORI).read_text(encoding="utf-8")


def test_il_registro_non_supera_la_misura_massima(tmp_path, faulthandler_finto):
    registro.avvia(str(tmp_path), misura=4000)
    for numero in range(400):
        registro.scrivi(f"riga {numero} " + "x" * 50)
    registro.chiudi()
    file = [p for p in tmp_path.iterdir() if p.name.startswith(registro.FILE_DEGLI_ERRORI)]
    assert len(file) == 2 and sum(p.stat().st_size for p in file) <= 4000 + 200
    assert "riga 399" in (tmp_path / registro.FILE_DEGLI_ERRORI).read_text(encoding="utf-8")


def test_il_crash_della_volta_prima(tmp_path, faulthandler_finto):
    (tmp_path / registro.FILE_DEL_CRASH).write_text("Windows fatal exception: access violation\n", encoding="utf-8")
    precedente = registro.avvia(str(tmp_path))
    assert precedente == str(tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE)
    assert "access violation" in (tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE).read_text(encoding="utf-8")
    registro.chiudi()
    # Un file vuoto e' una chiusura forzata senza resoconto: niente da dire.
    (tmp_path / registro.FILE_DEL_CRASH).write_text("", encoding="utf-8")
    assert registro.avvia(str(tmp_path)) is None


def test_senza_stderr_le_righe_vanno_nel_registro(tmp_path, faulthandler_finto, monkeypatch):
    # Il programma compilato non ha uno stderr: traceback.print_exc e gli
    # avvisi finiscono nel registro.
    monkeypatch.setattr(sys, "stderr", None)
    registro.avvia(str(tmp_path))
    print("prima riga\nseconda riga", file=sys.stderr)
    registro.chiudi()
    assert sys.stderr is None
    testo = (tmp_path / registro.FILE_DEGLI_ERRORI).read_text(encoding="utf-8")
    assert "prima riga" in testo and "seconda riga" in testo


def test_un_crash_vero_lascia_il_resoconto(tmp_path):
    # Un processo figlio avvia il registro e muore per un accesso alla
    # memoria non valido; il dialogo di errore di Windows e' spento.
    codice = textwrap.dedent(f"""
        import ctypes, sys
        sys.path.insert(0, {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))!r})
        import registro
        ctypes.windll.kernel32.SetErrorMode(0x8003)
        registro.avvia({str(tmp_path)!r})
        ctypes.string_at(0)
    """)
    esito = subprocess.run([sys.executable, "-B", "-c", codice], capture_output=True, timeout=60, check=False)  # noqa: S603 - il codice della prova
    assert esito.returncode != 0
    testo = (tmp_path / registro.FILE_DEL_CRASH).read_text(encoding="utf-8", errors="replace")
    assert "access violation" in testo.lower() and "Current thread" in testo
