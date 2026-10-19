# MeTeOra, le prove del registro degli errori e dei crash: i file, la misura massima, il crash della volta prima.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.89.0. Nella 1.104.0 il crash vero, distinto dalle eccezioni di Windows gestite, e sopravvissuto().

"""faulthandler e' finto nelle prove nel processo, per non spegnere quello di
pytest; il crash vero, le eccezioni di Windows gestite e la chiusura a forza
si provano in processi figli, con il dialogo di errore di Windows spento, che
sul desktop non mostra niente."""

import os
import subprocess
import sys
import textwrap

import pytest

import registro

_RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Il principio di ogni processo figlio: il registro avviato nella cartella
# della prova, il dialogo di errore di Windows spento, e due strumenti.
# solleva() lancia un'eccezione di Windows che ctypes prende e trasforma in
# un OSError, come fa chi la gestisce da se'; termina() chiude il processo
# con TerminateProcess, come il Task Manager, senza l'uscita pulita.
_PRINCIPIO = """
import ctypes, sys
from ctypes import wintypes
sys.path.insert(0, {radice!r})
import registro
kernel32 = ctypes.WinDLL("kernel32")
kernel32.SetErrorMode(0x8003)
kernel32.RaiseException.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
kernel32.RaiseException.restype = None
kernel32.GetCurrentProcess.restype = wintypes.HANDLE
kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
def solleva(codice):
    try:
        kernel32.RaiseException(codice, 0, 0, None)
    except OSError:
        pass
def termina():
    kernel32.TerminateProcess(kernel32.GetCurrentProcess(), 7)
registro.avvia({cartella!r})
"""


def _figlio(cartella, corpo):
    codice = _PRINCIPIO.format(radice=_RADICE, cartella=str(cartella)) + textwrap.dedent(corpo)
    return subprocess.run([sys.executable, "-B", "-c", codice], capture_output=True, timeout=60, check=False)  # noqa: S603 - il codice della prova


def _resoconto(intestazione):
    """Un resoconto come quelli che scrive faulthandler."""
    return f'{intestazione}\n\nCurrent thread 0x00001a2b (most recent call first):\n  File "C:\\MeTeOra\\finestra.py", line 10 in suona\n\n'


def _errori(cartella):
    """Il testo del registro degli errori, vuoto se non c'e'."""
    file = cartella / registro.FILE_DEGLI_ERRORI
    return file.read_text(encoding="utf-8") if file.exists() else ""


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


def _replace_guasto(sorgente, destinazione):
    raise PermissionError(13, "Accesso negato", str(destinazione))


def test_il_crash_della_volta_prima_se_non_si_puo_spostare(tmp_path, faulthandler_finto, monkeypatch):
    # os.replace non riesce, per esempio con il file del crash bloccato: il
    # resoconto si scrive nel file del crash precedente, e solo dopo il file
    # del crash si tronca.
    resoconto = _resoconto("Windows fatal exception: access violation").encode("utf-8")
    (tmp_path / registro.FILE_DEL_CRASH).write_bytes(resoconto)
    (tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE).write_text("il crash di un'altra volta\n", encoding="utf-8")
    with monkeypatch.context() as finto:
        finto.setattr(registro.os, "replace", _replace_guasto)
        precedente = registro.avvia(str(tmp_path))
    assert precedente == str(tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE)
    assert (tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE).read_bytes() == resoconto
    assert (tmp_path / registro.FILE_DEL_CRASH).stat().st_size == 0 and faulthandler_finto.acceso is not None
    registro.chiudi()
    assert "Non riesco a scrivere il resoconto" not in _errori(tmp_path)


def test_il_crash_della_volta_prima_in_un_file_di_riserva(tmp_path, faulthandler_finto, monkeypatch):
    # Anche il file del crash precedente non si puo' scrivere: qui e' una
    # cartella. Il resoconto va in un file di riserva accanto, ed e' quello
    # che avvia() indica.
    resoconto = _resoconto("Fatal Python error: Aborted").encode("utf-8")
    (tmp_path / registro.FILE_DEL_CRASH).write_bytes(resoconto)
    (tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE).mkdir()
    # Il nome di riserva vero ha la data e l'ora; qui e' fisso.
    assert registro._nome_di_riserva().startswith("MeTeOra - Crash precedente 20")
    with monkeypatch.context() as finto:
        finto.setattr(registro, "_nome_di_riserva", lambda: "MeTeOra - Crash precedente 2026-10-20 10.20.30.log")
        finto.setattr(registro.os, "replace", _replace_guasto)
        precedente = registro.avvia(str(tmp_path))
    riserva = tmp_path / "MeTeOra - Crash precedente 2026-10-20 10.20.30.log"
    assert precedente == str(riserva) and riserva.read_bytes() == resoconto
    assert (tmp_path / registro.FILE_DEL_CRASH).stat().st_size == 0
    registro.chiudi()
    assert f"Non riesco a scrivere il resoconto del crash della volta prima in {registro.FILE_DEL_CRASH_PRECEDENTE}: è in {riserva.name}." in _errori(tmp_path)


def test_il_crash_della_volta_prima_che_non_si_puo_scrivere_da_nessuna_parte(tmp_path, faulthandler_finto, monkeypatch):
    # Nessuna scrittura riesce: il resoconto resta in testa al file del
    # crash, che non si tronca, e avvia() indica quello.
    resoconto = _resoconto("Windows fatal exception: access violation").encode("utf-8")
    crash = tmp_path / registro.FILE_DEL_CRASH
    crash.write_bytes(resoconto)
    (tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE).mkdir()
    (tmp_path / "riserva bloccata.log").mkdir()
    with monkeypatch.context() as finto:
        finto.setattr(registro, "_nome_di_riserva", lambda: "riserva bloccata.log")
        finto.setattr(registro.os, "replace", _replace_guasto)
        precedente = registro.avvia(str(tmp_path))
    assert precedente == str(crash) and crash.read_bytes() == resoconto
    # Faulthandler scrive in aggiunta, dopo il resoconto della volta prima.
    descrittore = faulthandler_finto.acceso.fileno()
    gestita = _resoconto("Windows fatal exception: code 0x8001010d").encode("utf-8")
    os.write(descrittore, gestita)
    assert crash.read_bytes() == resoconto + gestita
    # sopravvissuto() riassume solo cio' che e' venuto dopo, e lo toglie
    # senza toccare il resoconto della volta prima, ne' lasciare buchi.
    assert registro.sopravvissuto() == 1 and crash.read_bytes() == resoconto
    assert "1 in tutto: code 0x8001010d 1 volta." in _errori(tmp_path).splitlines()[-1]
    assert registro.sopravvissuto() == 0
    os.write(descrittore, gestita)
    assert crash.read_bytes() == resoconto + gestita
    # L'uscita pulita lascia il file con il solo resoconto della volta prima.
    registro.chiudi()
    assert crash.read_bytes() == resoconto
    assert f"Non riesco a scrivere il resoconto del crash della volta prima in {registro.FILE_DEL_CRASH_PRECEDENTE}: è in {crash.name}." in _errori(tmp_path)
    # All'avvio dopo, sbloccato il file del crash precedente, il resoconto va
    # al suo posto.
    (tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE).rmdir()
    assert registro.avvia(str(tmp_path)) == str(tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE)
    assert (tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE).read_bytes() == resoconto
    assert crash.stat().st_size == 0


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


@pytest.mark.parametrize(("testo", "atteso"), [
    ("", False),
    # Le eccezioni che chi le solleva gestisce da se': COM, LuaJIT dentro
    # libmpv, un punto d'interruzione.
    (_resoconto("Windows fatal exception: code 0x8001010d"), False),
    (_resoconto("Windows fatal exception: code 0xe24c4a02"), False),
    (_resoconto("Windows fatal exception: code 0x8001010d") + _resoconto("Windows fatal exception: code 0xe24c4a02"), False),
    (_resoconto("Windows fatal exception: code 0x80000003"), False),
    # L'intestazione conta solo a inizio riga, non dentro una riga della pila.
    ('  File "C:\\prove\\Windows fatal exception: access violation.py", line 3 in <module>\n', False),
    ('  File "C:\\prove\\Fatal Python error.py", line 3 in <module>\n', False),
    (_resoconto("Windows fatal exception: access violation"), True),
    (_resoconto("Windows fatal exception: stack overflow"), True),
    (_resoconto("Windows fatal exception: int divide by zero"), True),
    # I codici NTSTATUS di errore: il mucchio rovinato e la pila sfondata.
    (_resoconto("Windows fatal exception: code 0xc0000374"), True),
    (_resoconto("Windows fatal exception: code 0xC0000409"), True),
    # Un'eccezione gestita, poi il crash: il crash conta.
    (_resoconto("Windows fatal exception: code 0x8001010d") + _resoconto("Windows fatal exception: access violation"), True),
    (_resoconto("Fatal Python error: Aborted"), True),
    (_resoconto("Fatal Python error from unexpected signum: 22"), True),
], ids=["vuoto", "com", "luajit", "com e luajit", "interruzione", "pila con l'eccezione", "pila con l'errore di python", "access violation",
    "stack overflow", "divisione per zero", "mucchio rovinato", "pila sfondata", "gestita e poi crash", "aborted", "segnale inatteso"])
def test_crash_vero(testo, atteso):
    assert registro.crash_vero(testo) is atteso


def test_resoconti_le_intestazioni_in_ordine():
    testo = _resoconto("Windows fatal exception: code 0x8001010d") + _resoconto("Windows fatal exception: access violation")
    assert registro.resoconti(testo) == [("Windows fatal exception: code 0x8001010d", False), ("Windows fatal exception: access violation", True)]
    # Anche con i ritorni a capo di Windows.
    assert registro.resoconti(testo.replace("\n", "\r\n")) == registro.resoconti(testo)


def test_le_sole_eccezioni_gestite_non_sono_un_crash(tmp_path, faulthandler_finto):
    # Una chiusura a forza dopo eccezioni gestite: nessun crash, il file del
    # crash non diventa quello precedente, e il registro le riassume.
    gestite = [_resoconto(f"Windows fatal exception: code {codice}") for codice in ("0x8001010d", "0xe24c4a02", "0x8001010d")]
    (tmp_path / registro.FILE_DEL_CRASH).write_text("".join(gestite), encoding="utf-8")
    assert registro.avvia(str(tmp_path)) is None
    assert not (tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE).exists()
    assert (tmp_path / registro.FILE_DEL_CRASH).stat().st_size == 0
    registro.chiudi()
    testo = (tmp_path / registro.FILE_DEGLI_ERRORI).read_text(encoding="utf-8")
    assert "Nessun crash la volta prima" in testo and "3 in tutto: code 0x8001010d 2 volte, code 0xe24c4a02 1 volta." in testo


def test_sopravvissuto_svuota_subito_le_sole_eccezioni_gestite(tmp_path, faulthandler_finto):
    # Senza avvia() non fa niente.
    assert registro.sopravvissuto() == 0
    registro.avvia(str(tmp_path))
    crash = tmp_path / registro.FILE_DEL_CRASH
    # Con il file vuoto non c'e' niente da dire.
    assert registro.sopravvissuto() == 0
    # Si scrive come faulthandler, nel descrittore del file che ha ricevuto.
    descrittore = faulthandler_finto.acceso.fileno()
    scritto = "".join(_resoconto(f"Windows fatal exception: code {codice}") for codice in ("0x8001010d", "0xe24c4a02", "0x8001010d"))
    os.write(descrittore, scritto.encode("utf-8"))
    # Al primo giro: niente di fatale, si riassume e si svuota subito.
    assert registro.sopravvissuto() == 3
    assert crash.stat().st_size == 0
    ultima = _errori(tmp_path).splitlines()[-1]
    assert "3 in tutto: code 0x8001010d 2 volte, code 0xe24c4a02 1 volta." in ultima and "sopravvissuto" not in ultima
    # Dopo lo svuotamento faulthandler riscrive dall'inizio, senza un buco
    # di zeri davanti.
    nuovo = "Windows fatal exception: code 0xe24c4a02\n"
    os.write(descrittore, nuovo.encode("utf-8"))
    assert crash.read_bytes() == nuovo.encode("utf-8")
    assert registro.sopravvissuto() == 1
    assert "1 in tutto: code 0xe24c4a02 1 volta." in _errori(tmp_path).splitlines()[-1]
    registro.chiudi()
    assert registro.sopravvissuto() == 0


def test_sopravvissuto_un_resoconto_fatale_aspetta_il_giro_dopo(tmp_path, faulthandler_finto):
    # Un resoconto fatale scritto subito prima del giro: forse un crash in
    # corso in un altro filo, e il file resta com'e'.
    registro.avvia(str(tmp_path))
    crash = tmp_path / registro.FILE_DEL_CRASH
    descrittore = faulthandler_finto.acceso.fileno()
    scritto = (_resoconto("Windows fatal exception: code 0x8001010d") + _resoconto("Windows fatal exception: access violation")
        + _resoconto("Windows fatal exception: code 0x8001010d")).encode("utf-8")
    os.write(descrittore, scritto)
    assert registro.sopravvissuto() == 0
    assert crash.read_bytes() == scritto
    assert "Il file del crash" not in _errori(tmp_path)
    # Al giro dopo MeTeOra c'e' ancora: e' sopravvissuto, e il file si svuota.
    assert registro.sopravvissuto() == 3
    assert crash.stat().st_size == 0
    testo = _errori(tmp_path)
    assert "3 in tutto: code 0x8001010d 2 volte, access violation 1 volta." in testo
    assert "Fra queste access violation sarebbe fatale, ma chi l'ha sollevata l'ha gestita: MeTeOra è sopravvissuto." in testo
    # Faulthandler riscrive dall'inizio, e un nuovo resoconto fatale aspetta
    # di nuovo un giro.
    os.write(descrittore, _resoconto("Windows fatal exception: stack overflow").encode("utf-8"))
    assert registro.sopravvissuto() == 0 and crash.read_bytes().startswith(b"Windows fatal exception: stack overflow\n")
    assert registro.sopravvissuto() == 1 and crash.stat().st_size == 0


def test_sopravvissuto_un_altro_resoconto_fatale_fa_aspettare_ancora(tmp_path, faulthandler_finto):
    registro.avvia(str(tmp_path))
    crash = tmp_path / registro.FILE_DEL_CRASH
    descrittore = faulthandler_finto.acceso.fileno()
    os.write(descrittore, _resoconto("Windows fatal exception: access violation").encode("utf-8"))
    assert registro.sopravvissuto() == 0
    # Fra i due giri un altro resoconto fatale: il primo e' sopravvissuto,
    # ma il secondo si vede ora per la prima volta, e non si svuota niente.
    os.write(descrittore, _resoconto("Windows fatal exception: code 0xc0000374").encode("utf-8"))
    assert registro.sopravvissuto() == 0
    assert crash.read_text(encoding="utf-8").count("Windows fatal exception") == 2
    # Una gestita, dopo, non fa aspettare: tutti e tre insieme.
    os.write(descrittore, _resoconto("Windows fatal exception: code 0x8001010d").encode("utf-8"))
    assert registro.sopravvissuto() == 3 and crash.stat().st_size == 0
    assert "Fra queste access violation, code 0xc0000374 sarebbero fatali, ma chi le ha sollevate le ha gestite" in _errori(tmp_path)


def test_sopravvissuto_una_riga_a_meta_aspetta(tmp_path, faulthandler_finto):
    # Faulthandler scrive l'intestazione a pezzi: a meta' non si sa ancora
    # se e' fatale, e il file non si svuota.
    registro.avvia(str(tmp_path))
    crash = tmp_path / registro.FILE_DEL_CRASH
    descrittore = faulthandler_finto.acceso.fileno()
    os.write(descrittore, b"Windows fatal exception: acc")
    assert registro.sopravvissuto() == 0 and crash.read_bytes() == b"Windows fatal exception: acc"
    # Finita la riga e' un resoconto fatale visto per la prima volta.
    os.write(descrittore, b"ess violation\n\n")
    assert registro.sopravvissuto() == 0 and crash.stat().st_size > 0
    assert registro.sopravvissuto() == 1 and crash.stat().st_size == 0
    # Una riga a meta' che non cresce piu' da un giro non fa aspettare per
    # sempre.
    os.write(descrittore, b"qualcosa senza a capo")
    assert registro.sopravvissuto() == 0 and crash.stat().st_size > 0
    assert registro.sopravvissuto() == 0 and crash.stat().st_size == 0


def test_sopravvissuto_non_taglia_se_il_file_cresce_dopo_la_lettura(tmp_path, faulthandler_finto, monkeypatch):
    registro.avvia(str(tmp_path))
    crash = tmp_path / registro.FILE_DEL_CRASH
    descrittore = faulthandler_finto.acceso.fileno()
    prima = _resoconto("Windows fatal exception: code 0x8001010d").encode("utf-8")
    dopo = _resoconto("Windows fatal exception: code 0xe24c4a02").encode("utf-8")
    os.write(descrittore, prima)
    vero = os.fstat
    chiamate = []

    def fstat(numero):
        # La seconda misura, dopo la lettura: faulthandler ha scritto ancora.
        if numero == descrittore:
            chiamate.append(numero)
            if len(chiamate) == 2:
                os.write(descrittore, dopo)
        return vero(numero)

    with monkeypatch.context() as finto:
        finto.setattr(registro.os, "fstat", fstat)
        assert registro.sopravvissuto() == 0
    assert len(chiamate) == 2 and crash.read_bytes() == prima + dopo
    assert registro.sopravvissuto() == 2 and crash.stat().st_size == 0


def test_un_crash_vero_lascia_il_resoconto(tmp_path):
    # Un processo figlio avvia il registro e muore per un accesso alla
    # memoria non valido. ctypes.string_at(0) non andrebbe: ctypes prende
    # l'eccezione e ne fa un OSError, e il processo sopravvive.
    esito = _figlio(tmp_path, """
        import faulthandler
        faulthandler._read_null()
    """)
    assert esito.returncode & 0xFFFFFFFF == 0xC0000005
    testo = (tmp_path / registro.FILE_DEL_CRASH).read_text(encoding="utf-8", errors="replace")
    assert "access violation" in testo.lower() and "Current thread" in testo
    assert registro.crash_vero(testo)


def test_eccezioni_gestite_e_chiusura_dal_task_manager_non_sono_un_crash(tmp_path, faulthandler_finto):
    # Le eccezioni di COM e di LuaJIT, gestite, poi la chiusura a forza:
    # faulthandler le ha scritte, ma non c'e' stato nessun crash.
    esito = _figlio(tmp_path, """
        solleva(0x8001010D)
        solleva(0xE24C4A02)
        termina()
    """)
    # Il codice di TerminateProcess: le due eccezioni non l'hanno ucciso.
    assert esito.returncode == 7
    testo = (tmp_path / registro.FILE_DEL_CRASH).read_text(encoding="utf-8", errors="replace")
    assert "code 0x8001010d" in testo and "code 0xe24c4a02" in testo
    assert not registro.crash_vero(testo)
    # All'avvio dopo, niente crash della volta prima.
    assert registro.avvia(str(tmp_path)) is None
    assert not (tmp_path / registro.FILE_DEL_CRASH_PRECEDENTE).exists()


def test_sopravvissuto_con_faulthandler_vero(tmp_path):
    # Un'access violation presa da ctypes: al primo giro resta nel file, al
    # secondo e' riassunta e tolta; poi un'eccezione gestita e la chiusura a
    # forza: il file non e' un crash.
    esito = _figlio(tmp_path, """
        try:
            ctypes.string_at(0)
        except OSError:
            pass
        print(registro.sopravvissuto(), flush=True)
        print(registro.sopravvissuto(), flush=True)
        solleva(0x8001010D)
        termina()
    """)
    assert esito.returncode == 7 and esito.stdout.split() == [b"0", b"1"]
    testo = (tmp_path / registro.FILE_DEL_CRASH).read_text(encoding="utf-8", errors="replace")
    assert testo.startswith("Windows fatal exception: code 0x8001010d") and "access violation" not in testo
    assert not registro.crash_vero(testo)
    errori = (tmp_path / registro.FILE_DEGLI_ERRORI).read_text(encoding="utf-8")
    assert "access violation 1 volta" in errori and "MeTeOra è sopravvissuto" in errori
