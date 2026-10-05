# MeTeOra, le prove dell'istanza unica e delle associazioni dei formati: pipe di prova e registro finto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.91.0.

"""La pipe ha un nome solo per la prova, mai quello del MeTeOra che magari e'
aperto; il registro di Windows e' finto, in memoria: niente di vero si tocca."""

import ctypes
import os
import threading
import uuid
from ctypes import wintypes

import associazioni
import formati
import installazione
import istanza


def _nome_di_prova():
    return rf"\\.\pipe\MeTeOra-prova-{uuid.uuid4().hex}"


def test_la_seconda_copia_passa_i_file_alla_prima(tmp_path):
    nome = _nome_di_prova()
    ricevuti, arrivati = [], threading.Event()

    def ricevi(percorsi):
        ricevuti.append(percorsi)
        arrivati.set()

    # Nessuna prima copia: manda dice di no.
    assert istanza.manda(["a.mp3"], nome) is False
    prima = istanza.Ascolto(ricevi, nome)
    try:
        assert prima.attiva
        # Una seconda copia che parte nello stesso istante non ascolta.
        assert istanza.Ascolto(ricevi, nome).attiva is False
        brano = tmp_path / "brano.mp3"
        assert istanza.manda([str(brano), "relativo.flac"], nome) is True
        assert arrivati.wait(10)
        assert ricevuti == [[str(brano), os.path.abspath("relativo.flac")]]
        # Anche senza file, per portare MeTeOra in primo piano.
        arrivati.clear()
        assert istanza.manda([], nome) is True
        assert arrivati.wait(10) and ricevuti[-1] == []
    finally:
        prima.ferma()
    assert istanza.manda(["dopo.mp3"], nome) is False


def test_il_nome_della_pipe(monkeypatch):
    monkeypatch.setenv("METEORA_ISTANZA", "banco")
    assert istanza.nome() == r"\\.\pipe\banco"
    monkeypatch.delenv("METEORA_ISTANZA")
    monkeypatch.setenv("USERNAME", "gabriele")
    assert istanza.nome() == r"\\.\pipe\MeTeOra-gabriele"


class _RegistroFinto:
    """Il poco di winreg che serve, con le chiavi in un dizionario."""

    HKEY_CURRENT_USER = "HKCU"
    KEY_WRITE, KEY_READ, REG_SZ = 1, 2, 1

    def __init__(self):
        self.chiavi = {}

    class _Chiave:
        def __init__(self, registro, percorso):
            self.registro, self.percorso = registro, percorso

        def __enter__(self):
            return self

        def __exit__(self, *_argomenti):
            return False

    def CreateKeyEx(self, _radice, percorso, _riservato=0, _accesso=0):
        parti = percorso.split("\\")
        for i in range(1, len(parti) + 1):
            self.chiavi.setdefault("\\".join(parti[:i]).lower(), {})
        return self._Chiave(self, percorso.lower())

    def OpenKey(self, _radice, percorso, _riservato=0, _accesso=0):
        if percorso.lower() not in self.chiavi:
            raise FileNotFoundError(percorso)
        return self._Chiave(self, percorso.lower())

    def SetValueEx(self, chiave, nome, _riservato, _tipo, valore):
        self.chiavi[chiave.percorso][nome] = valore

    def QueryValueEx(self, chiave, nome):
        if nome not in self.chiavi[chiave.percorso]:
            raise FileNotFoundError(nome)
        return self.chiavi[chiave.percorso][nome], self.REG_SZ

    def DeleteValue(self, chiave, nome):
        if nome not in self.chiavi[chiave.percorso]:
            raise FileNotFoundError(nome)
        del self.chiavi[chiave.percorso][nome]

    def EnumKey(self, chiave, indice):
        figlie = sorted({k[len(chiave.percorso) + 1:].split("\\")[0] for k in self.chiavi if k.startswith(chiave.percorso + "\\")})
        if indice >= len(figlie):
            raise OSError("niente altro")
        return figlie[indice]

    def DeleteKey(self, _radice, percorso):
        percorso = percorso.lower()
        if any(k.startswith(percorso + "\\") for k in self.chiavi):
            raise OSError("ha delle sottochiavi")
        self.chiavi.pop(percorso, None)


def test_le_associazioni_si_scrivono_e_si_tolgono(monkeypatch):
    monkeypatch.setattr(associazioni, "_avvisa_windows", lambda: None)
    reg = _RegistroFinto()
    # Un altro programma ha gia' i suoi valori per .mp3.
    reg.CreateKeyEx("HKCU", r"Software\Classes\.mp3\OpenWithProgids")
    reg.chiavi[r"software\classes\.mp3\openwithprogids"]["VLC.mp3"] = ""
    eseguibile = r"C:\Programmi\MeTeOra\MeTeOra.exe"
    quante = associazioni.registra(eseguibile, reg)
    assert quante == len(formati.TUTTI)
    comando = reg.chiavi[r"software\classes\applications\meteora.exe\shell\open\command"][""]
    assert comando == f'"{eseguibile}" "%1"'
    assert ".mp3" in reg.chiavi[r"software\classes\applications\meteora.exe\supportedtypes"]
    assert reg.chiavi[r"software\classes\.mp3\openwithprogids"] == {"VLC.mp3": "", "MeTeOra.Audio": ""}
    assert "MeTeOra.Video" in reg.chiavi[r"software\classes\.mkv\openwithprogids"]
    assert reg.chiavi[r"software\meteora\capabilities\fileassociations"][".flac"] == "MeTeOra.Audio"
    assert reg.chiavi[r"software\registeredapplications"]["MeTeOra"] == r"Software\MeTeOra\Capabilities"
    associazioni.togli(reg)
    # Resta solo cio' che non e' di MeTeOra.
    assert reg.chiavi[r"software\classes\.mp3\openwithprogids"] == {"VLC.mp3": ""}
    assert not any("meteora" in k for k in reg.chiavi)
    assert "MeTeOra" not in reg.chiavi.get(r"software\registeredapplications", {})
    # Togliere di nuovo non rompe niente.
    associazioni.togli(reg)


def test_ferma_non_si_appende():
    # 1.96.11: se fermando l'ascolto resta una pipe che nessuno serve, come
    # quando il filo dell'ascolto ne ha appena preparata una nuova, la sveglia
    # non ci resta appesa: Client vi aspettava la sfida per sempre.
    import _winapi
    from multiprocessing.connection import BUFSIZE, Listener

    nome = _nome_di_prova()
    ascolto = istanza.Ascolto.__new__(istanza.Ascolto)
    ascolto._nome = nome
    ascolto._fermo = False
    ascolto._mutex = None
    ascolto._ascoltatore = Listener(nome, family="AF_PIPE", authkey=istanza._chiave(nome))
    in_piu = _winapi.CreateNamedPipe(nome, _winapi.PIPE_ACCESS_DUPLEX | _winapi.FILE_FLAG_OVERLAPPED,
        _winapi.PIPE_TYPE_MESSAGE | _winapi.PIPE_READMODE_MESSAGE | _winapi.PIPE_WAIT, _winapi.PIPE_UNLIMITED_INSTANCES,
        BUFSIZE, BUFSIZE, _winapi.NMPWAIT_WAIT_FOREVER, _winapi.NULL)
    try:
        filo = threading.Thread(target=ascolto.ferma, daemon=True)
        filo.start()
        filo.join(5)
        assert not filo.is_alive()
    finally:
        _winapi.CloseHandle(in_piu)


def _mutex_aperto(nome_del_mutex):
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenMutexW.restype = wintypes.HANDLE
    kernel32.OpenMutexW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    maniglia = kernel32.OpenMutexW(0x00100000, False, nome_del_mutex)  # SYNCHRONIZE
    if maniglia:
        kernel32.CloseHandle(wintypes.HANDLE(maniglia))
    return bool(maniglia)


def test_il_mutex_per_l_installatore(monkeypatch):
    # 1.97.0: la prima copia tiene il mutex che AppMutex di MeTeOra.iss
    # cerca; con METEORA_ISTANZA, uno di prova, e mai quello vero.
    monkeypatch.setenv("METEORA_ISTANZA", f"prova-mutex-{uuid.uuid4().hex}")
    mutex = istanza.nome_del_mutex()
    assert mutex.startswith("MeTeOra-prova-mutex-")
    ascolto = istanza.Ascolto(lambda _percorsi: None)
    try:
        assert ascolto.attiva and _mutex_aperto(mutex)
    finally:
        ascolto.ferma()
    assert not _mutex_aperto(mutex)
    # Le prove che danno il nome della pipe non lo tengono.
    ascolto = istanza.Ascolto(lambda _percorsi: None, _nome_di_prova())
    try:
        assert ascolto._mutex is None
    finally:
        ascolto.ferma()
    monkeypatch.delenv("METEORA_ISTANZA")
    assert istanza.nome_del_mutex() == "MeTeOra"
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "MeTeOra.iss"), encoding="utf-8") as f:
        assert "AppMutex=MeTeOra\n" in f.read()


def test_la_versione_in_app_installate():
    # 1.97.0: dopo un aggiornamento automatico la voce del setup dice la
    # versione vera, ma solo se e' quella di questa cartella.
    reg = _RegistroFinto()
    cartella = r"C:\Users\prova\AppData\Local\Programs\MeTeOra"
    assert installazione.aggiorna_la_versione("1.97.0", cartella, reg) is False
    with reg.CreateKeyEx(reg.HKEY_CURRENT_USER, installazione.CHIAVE) as chiave:
        reg.SetValueEx(chiave, "InstallLocation", 0, reg.REG_SZ, cartella + "\\")
        reg.SetValueEx(chiave, "DisplayVersion", 0, reg.REG_SZ, "1.96.0")
    assert installazione.aggiorna_la_versione("1.97.0", r"D:\MeTeOra portatile", reg) is False
    assert installazione.aggiorna_la_versione("1.97.0", cartella.upper(), reg) is True
    assert reg.chiavi[installazione.CHIAVE.lower()]["DisplayVersion"] == "1.97.0"
    assert installazione.aggiorna_la_versione("1.97.0", cartella, reg) is False
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "MeTeOra.iss"), encoding="utf-8") as f:
        app_id = next(r for r in f.read().splitlines() if r.startswith("AppId="))
    assert installazione.CHIAVE.endswith("\\" + app_id[len("AppId={"):] + "_is1")
