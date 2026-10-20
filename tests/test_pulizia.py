# MeTeOra, le prove della pulizia all'avvio: file presenti e spariti, cartelle che non si leggono, maiuscole vere, radici saltate, sorveglianza della rete, dischi riconosciuti.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 19/10/2026: nasce con la 1.104.0. Nella 1.112.0 le prove della protezione dei dischi: il disco di ogni lettera, imparato o diverso, anche con subst, le lettere contese o non riconosciute e il file dei dischi che non si legge; poi i dischi visti dalla Sentinella, Riconosci questo disco e i dischi di ogni computer; infine il conto delle voci di Riconosci questo disco e il MachineGuid del computer rinominato.

"""Sul disco si guardano file veri in una cartella temporanea, presa con le
maiuscole che ha davvero, e una giunzione vera verso una lettera che non
c'e'; la rete e' una condivisione finta, con le letture sostituite, e la
rete vera non si tocca. Chi risponde a una lettera lo dice la prova: senza,
per conftest.py, nessuna radice ha un disco da riconoscere, come prima della
1.112.0; la Sentinella si prova con le domande fatte dalla prova; la
protezione dei dischi si prova su una lettera finta, F:, con le letture
sostituite, e le funzioni che leggono il disco con un kernel32 finto."""

import ctypes
import json
import ntpath
import os
import string
import struct
import sys
import threading
import time
import types
from ctypes import wintypes
from pathlib import Path

import pytest

import pulizia
import ricerca

RETE = "\\\\finto\\condivisione"
# Chi risponde davvero alle lettere, prima che conftest.py lo sostituisca:
# i dischi veri non si toccano, e le prove di prima della 1.112.0 restano
# com'erano.
_identita_vera = pulizia._identita
# E il MachineGuid, che conftest.py non lascia leggere.
_guid_vero = pulizia.guid_del_computer


@pytest.fixture
def cartella(tmp_path):
    """La cartella temporanea scritta come sul disco, maiuscole comprese:
    se fosse scritta in un altro modo, ogni file finirebbe fra i nomi_veri."""
    return Path(os.path.realpath(tmp_path))


def _file(percorso):
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_bytes(b"")
    return percorso


def _radice(percorso):
    return ntpath.splitdrive(str(percorso))[0].upper()


def _in_rete(*nomi):
    return ntpath.join(RETE, *nomi)


def _aspetta(condizione, secondi=3):
    scadenza = time.monotonic() + secondi
    while not condizione() and time.monotonic() < scadenza:
        time.sleep(0.01)
    return condizione()


@pytest.fixture
def letture(monkeypatch):
    """Le cartelle lette, in ordine, con la lettura vera del disco."""
    vera = pulizia._elenco
    lette = []

    def elenco(cartella, *altro):
        lette.append(os.path.normcase(cartella))
        return vera(cartella, *altro)

    monkeypatch.setattr(pulizia, "_elenco", elenco)
    return lette


def test_norm():
    assert pulizia.norm("E:/Musica/Brano.MP3") == "e:\\musica\\brano.mp3"
    assert pulizia.norm("\\\\Server\\Condivisione\\Rock\\..\\Pop\\a.mp3") == "\\\\server\\condivisione\\pop\\a.mp3"
    assert pulizia.norm("brano.mp3") == os.path.normcase(os.path.join(os.getcwd(), "brano.mp3"))


def test_file_presenti_e_spariti(cartella):
    presente = _file(cartella / "Musica" / "Presente.mp3")
    sparito = cartella / "Musica" / "Sparito.mp3"
    esito = pulizia.controlla([str(presente), str(sparito)])
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 2, "contese": {},
        "non_riconosciute": {}, "dischi": {}}


def test_la_cartella_sparita(cartella):
    resta = _file(cartella / "resta.mp3")
    spariti = [cartella / "Vecchia" / "uno.mp3", cartella / "Vecchia" / "Sotto" / "due.mp3"]
    esito = pulizia.controlla([str(resta), *(str(p) for p in spariti)])
    assert esito["mancanti"] == {pulizia.norm(p) for p in spariti}
    assert esito["controllati"] == 3 and esito["saltate"] == {}


def test_una_cartella_diventata_file_lascia_le_voci(cartella):
    # scandir su un file da' NotADirectoryError con il codice 267, che non e'
    # fra quelli di una cartella che manca: la voce resta, senza controllo.
    _file(cartella / "era una cartella")
    esito = pulizia.controlla([str(cartella / "era una cartella" / "brano.mp3")])
    assert esito == {"mancanti": set(), "saltate": {}, "nomi_veri": {}, "controllati": 0, "contese": {}, "non_riconosciute": {},
        "dischi": {}}


def test_le_maiuscole_vere(cartella):
    giusto = str(_file(cartella / "Musica" / "Brano Uno.mp3"))
    altro = str(_file(cartella / "Musica" / "Brano Due.mp3"))
    storto = str(cartella / "MUSICA" / "brano uno.MP3")
    # La cartella scritta male, il file scritto bene: le maiuscole vere della
    # cartella vengono dall'elenco di quella sopra.
    cartella_storta = str(cartella / "musica" / "Brano Due.mp3")
    lettera_minuscola = altro[0].lower() + altro[1:]
    sparito = cartella / "musica" / "manca.mp3"
    esito = pulizia.controlla([storto, giusto, cartella_storta, lettera_minuscola, str(sparito)])
    assert esito["mancanti"] == {pulizia.norm(sparito)}
    assert esito["nomi_veri"] == {pulizia.norm(giusto): giusto, pulizia.norm(altro): altro}
    assert esito["controllati"] == 3


def test_i_doppioni_si_guardano_una_volta(cartella, letture):
    brano = _file(cartella / "Album" / "a.mp3")
    secondo = _file(cartella / "Album" / "b.mp3")
    sparito = cartella / "Album" / "c.mp3"
    percorsi = [str(brano), str(brano), str(sparito), str(sparito), str(secondo)]
    esito = pulizia.controlla(percorsi)
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 3, "contese": {},
        "non_riconosciute": {}, "dischi": {}}
    # Un elenco per cartella: Album e quelle sopra, fino alla radice.
    assert len(letture) == len(set(letture))
    assert os.path.normcase(str(cartella / "Album")) in letture
    assert os.path.normcase(_radice(cartella) + "\\") in letture


def test_le_barre_diritte_sono_un_doppione(cartella):
    brano = str(_file(cartella / "a.mp3"))
    esito = pulizia.controlla([brano, brano.replace("\\", "/")])
    assert esito["controllati"] == 1 and esito["mancanti"] == set()
    # La scrittura con le barre diritte si toglie dallo schedario come quella
    # con altre maiuscole, se c'e' anche quella giusta.
    assert esito["nomi_veri"] == {pulizia.norm(brano): brano}


def test_voci_che_non_sono_file():
    esito = pulizia.controlla([None, "", 12, "C:\\", "\\\\server\\condivisione", "nul\0lo"], risponde=lambda _r: pytest.fail("nessuna radice da provare"))
    assert esito == {"mancanti": set(), "saltate": {}, "nomi_veri": {}, "controllati": 0, "contese": {}, "non_riconosciute": {},
        "dischi": {}}


def test_la_radice_che_non_risponde(cartella):
    presente = _file(cartella / "presente.mp3")
    sparito = cartella / "sparito.mp3"
    lontani = ["Q:\\Musica\\uno.mp3", "q:\\musica\\due.mp3", "q:\\musica\\UNO.mp3"]
    provate = []

    def risponde(radice):
        provate.append(radice)
        return radice != "Q:"

    esito = pulizia.controlla([*lontani, str(presente), str(sparito)], risponde=risponde)
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {"Q:": 2}, "nomi_veri": {}, "controllati": 2, "contese": {},
        "non_riconosciute": {}, "dischi": {}}
    # Ogni radice si prova una volta, e quella che risponde anche alla fine del giro.
    assert provate == ["Q:", _radice(cartella), _radice(cartella)]


def test_la_radice_che_smette_di_rispondere(cartella):
    resta = _file(cartella / "resta.mp3")
    risposte = iter([True, False])
    esito = pulizia.controlla([str(resta), str(cartella / "sparito.mp3")], risponde=lambda _r: next(risposte))
    assert esito == {"mancanti": set(), "saltate": {_radice(cartella): 2}, "nomi_veri": {}, "controllati": 0, "contese": {},
        "non_riconosciute": {}, "dischi": {}}


def test_cede_il_passo(cartella, letture):
    resta = _file(cartella / "resta.mp3")
    sparito = cartella / "sparito.mp3"
    cedi = threading.Event()
    cedi.set()
    esiti = []
    filo = threading.Thread(target=lambda: esiti.append(pulizia.controlla([str(resta), str(sparito)], cedi=cedi)), daemon=True)
    filo.start()
    time.sleep(0.2)
    assert filo.is_alive() and letture == []
    cedi.clear()
    filo.join(10)
    assert esiti[0]["mancanti"] == {pulizia.norm(sparito)}


def test_fermo_smette_prima_della_cartella_dopo(cartella, letture):
    _file(cartella / "uno" / "a.mp3")
    percorsi = [str(cartella / "uno" / "a.mp3"), str(cartella / "due" / "b.mp3"), "Q:\\c.mp3"]
    esito = pulizia.controlla(percorsi, fermo=lambda: len(letture) >= 1, risponde=lambda _r: True)
    assert len(letture) == 1
    # La radice lasciata a meta' e quella dopo restano tutte per la prossima volta.
    assert esito == {"mancanti": set(), "saltate": {_radice(cartella): 2, "Q:": 1}, "nomi_veri": {}, "controllati": 0, "contese": {},
        "non_riconosciute": {}, "dischi": {}}


def test_fermo_vale_anche_mentre_si_cede(cartella):
    cedi = threading.Event()
    cedi.set()
    inizio = time.monotonic()
    esito = pulizia.controlla([str(cartella / "a.mp3")], fermo=lambda: time.monotonic() - inizio > 0.1, cedi=cedi)
    assert time.monotonic() - inizio < 2
    assert esito["saltate"] == {_radice(cartella): 1} and esito["mancanti"] == set()


def test_un_altro_errore_lascia_le_voci(cartella, monkeypatch):
    sparito = cartella / "aperta" / "sparito.mp3"
    (cartella / "aperta").mkdir()
    errori = {
        # L'accesso negato.
        "chiusa": OSError(0, "Accesso negato", None, 5),
        # Un file che manca senza il codice di Windows: potrebbe essere la rete.
        "senza codice": FileNotFoundError(2, "Non si trova"),
        # Il nome di rete che non si trova piu'.
        "di rete": OSError(0, "Nome di rete non trovato", None, 67),
    }
    assert isinstance(errori["chiusa"], PermissionError) and errori["chiusa"].winerror == 5
    vera = pulizia._elenco

    def elenco(percorso, *altro):
        nome = os.path.basename(percorso)
        if nome in errori:
            raise errori[nome]
        return vera(percorso, *altro)

    monkeypatch.setattr(pulizia, "_elenco", elenco)
    restano = [str(cartella / nome / "brano.mp3") for nome in errori]
    esito = pulizia.controlla([*restano, str(sparito)])
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 1, "contese": {},
        "non_riconosciute": {}, "dischi": {}}


def test_la_cartella_che_c_e_ma_non_si_legge(cartella, monkeypatch):
    # Un disco montato in una cartella e staccato, o un percorso oltre i 260
    # caratteri senza LongPathsEnabled: leggere la cartella da' l'errore 3,
    # ma il suo nome e' nell'elenco di quella sopra. Le voci restano, anche
    # quelle delle cartelle sotto; una cartella che manca dall'elenco di
    # sopra, invece, e' sparita davvero.
    montata = cartella / "Montata"
    (montata / "Sotto").mkdir(parents=True)
    vera = pulizia._elenco

    def elenco(percorso, *altro):
        if os.path.normcase(percorso) in {os.path.normcase(str(montata)), os.path.normcase(str(montata / "Sotto"))}:
            raise FileNotFoundError(0, "Percorso non trovato", percorso, 3)
        return vera(percorso, *altro)

    monkeypatch.setattr(pulizia, "_elenco", elenco)
    restano = [str(montata / "a.mp3"), str(montata / "Sotto" / "b.mp3")]
    spariti = [cartella / "Sparita" / "c.mp3", cartella / "Sparita" / "Sotto" / "d.mp3"]
    esito = pulizia.controlla([*restano, *(str(p) for p in spariti)])
    assert esito == {"mancanti": {pulizia.norm(p) for p in spariti}, "saltate": {}, "nomi_veri": {}, "controllati": 2, "contese": {},
        "non_riconosciute": {}, "dischi": {}}


def _lettera_libera():
    """Una lettera di unita' che non c'e', cercata dalla Z, o None."""
    maschera = ctypes.windll.kernel32.GetLogicalDrives()
    return next((lettera for indice, lettera in reversed(list(enumerate(string.ascii_uppercase))) if not maschera & (1 << indice)), None)


def _giunzione(giunzione, bersaglio):
    """Una giunzione, come mklink /J, verso bersaglio, che puo' anche non
    esserci: una cartella vuota diventa un punto di montaggio con
    FSCTL_SET_REPARSE_POINT. Vero se ci si e' riusciti. Un kernel32 tutto
    suo, perche' i tipi degli argomenti non cambino quelli degli altri."""
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
        wintypes.HANDLE]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.DeviceIoControl.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
    kernel32.DeviceIoControl.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    giunzione.mkdir()
    sostituto = ("\\??\\" + bersaglio).encode("utf-16-le")
    stampato = bersaglio.encode("utf-16-le")
    # MountPointReparseBuffer: dove stanno i due nomi, e i nomi con lo zero in fondo.
    dati = struct.pack("<HHHH", 0, len(sostituto), len(sostituto) + 2, len(stampato)) + sostituto + b"\0\0" + stampato + b"\0\0"
    # IO_REPARSE_TAG_MOUNT_POINT, la lunghezza dei dati e un campo riservato.
    richiesta = struct.pack("<LHH", 0xA0000003, len(dati), 0) + dati
    # GENERIC_WRITE, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS e FILE_FLAG_OPEN_REPARSE_POINT.
    maniglia = kernel32.CreateFileW(str(giunzione), 0x40000000, 0, None, 3, 0x02000000 | 0x00200000, None)
    if maniglia in (None, wintypes.HANDLE(-1).value):
        return False
    try:
        scritti = wintypes.DWORD()
        return bool(kernel32.DeviceIoControl(maniglia, 0x000900A4, richiesta, len(richiesta), None, 0, ctypes.byref(scritti), None))
    finally:
        kernel32.CloseHandle(maniglia)


@pytest.fixture
def giunzione_staccata(cartella):
    """Una giunzione in cartella verso una lettera che non c'e', come una
    giunzione verso un disco staccato. Alla fine si toglie la giunzione, e
    solo lei."""
    lettera = _lettera_libera()
    if lettera is None:
        pytest.skip("Nessuna lettera di unità libera per la giunzione.")
    giunzione = cartella / "Giunzione"
    if not _giunzione(giunzione, f"{lettera}:\\Musica"):
        giunzione.rmdir()
        pytest.skip("La giunzione non si crea su questo disco.")
    yield giunzione
    os.rmdir(giunzione)


def test_la_giunzione_verso_un_disco_staccato(cartella, giunzione_staccata):
    # Leggerla da' l'errore 3, come per una cartella sparita, ma il suo nome
    # e' nell'elenco della cartella sopra: le sue voci restano.
    with pytest.raises(FileNotFoundError) as errore:
        os.listdir(giunzione_staccata)
    assert errore.value.winerror == 3
    restano = [str(giunzione_staccata / "a.mp3"), str(giunzione_staccata / "Album" / "b.mp3")]
    presente = _file(cartella / "presente.mp3")
    sparito = cartella / "Sparita" / "c.mp3"
    esito = pulizia.controlla([*restano, str(presente), str(sparito)])
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 2, "contese": {},
        "non_riconosciute": {}, "dischi": {}}


def test_i_percorsi_non_assoluti_restano_senza_controllo(cartella, monkeypatch):
    # Con la cartella di lavoro dove i file non ci sono, i percorsi relativi
    # sembrerebbero spariti: restano senza controllo, ne' mancanti ne' saltati.
    monkeypatch.chdir(cartella)
    relativi = ["brano.mp3", "Musica\\brano.mp3", "..\\brano.mp3", "\\brano.mp3", "/brano.mp3", _radice(cartella) + "brano.mp3", Path("brano.mp3")]
    esito = pulizia.controlla(relativi, risponde=lambda _r: pytest.fail("nessuna radice da provare"))
    assert esito == {"mancanti": set(), "saltate": {}, "nomi_veri": {}, "controllati": 0, "contese": {}, "non_riconosciute": {},
        "dischi": {}}
    sparito = cartella / "sparito.mp3"
    esito = pulizia.controlla([*relativi, str(sparito)])
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 1, "contese": {},
        "non_riconosciute": {}, "dischi": {}}


def _modi_di_errore():
    """(quello del filo, quello del processo) di Windows."""
    kernel32 = ctypes.windll.kernel32
    return kernel32.GetThreadErrorMode(), kernel32.GetErrorMode()


def _in_un_altro_filo(funzione):
    esito = []
    filo = threading.Thread(target=lambda: esito.append(funzione()), daemon=True)
    filo.start()
    filo.join(5)
    return esito[0]


def test_senza_finestre_di_errore_vale_solo_nel_filo():
    filo, processo = _modi_di_errore()
    altro_filo = _in_un_altro_filo(_modi_di_errore)
    with pulizia._senza_finestre_di_errore():
        dentro = _modi_di_errore()
        # Il filo della finestra, intanto, non ne risente.
        assert _in_un_altro_filo(_modi_di_errore) == altro_filo
    assert dentro[0] & pulizia._SENZA_FINESTRE_DI_ERRORE and dentro[1] == processo
    assert _modi_di_errore() == (filo, processo)


def test_il_nome_del_volume_senza_finestre_di_errore_solo_nel_filo(cartella, monkeypatch):
    import questo_pc

    vero = ctypes.windll.kernel32
    letture = []

    class Kernel32:
        """Il kernel32 vero, che annota i modi di errore mentre si legge il
        volume e non lascia usare SetErrorMode, che vale per tutto il processo."""

        def __getattr__(self, nome):
            if nome == "SetErrorMode":
                pytest.fail("SetErrorMode vale per tutto il processo.")
            return getattr(vero, nome)

        def GetVolumeInformationW(self, *argomenti):
            letture.append(_modi_di_errore())
            return vero.GetVolumeInformationW(*argomenti)

    class Ctypes:
        windll = types.SimpleNamespace(kernel32=Kernel32())

        def __getattr__(self, nome):
            return getattr(ctypes, nome)

    filo, processo = _modi_di_errore()
    monkeypatch.setattr(questo_pc, "ctypes", Ctypes())
    assert questo_pc._nome_del_volume(_radice(cartella) + "\\")
    assert len(letture) == 1 and letture[0][0] & 0x0001 and letture[0][1] == processo
    assert _modi_di_errore() == (filo, processo)


@pytest.fixture
def rete_finta(monkeypatch):
    """La condivisione RETE con cartelle finte: stato["contenuti"] dice cosa
    c'e' in ogni cartella (norm -> nomi, o un'eccezione da sollevare),
    stato["lettura"], se c'e', sostituisce la lettura; l'annullamento annota
    il filo e libera la lettura appesa. Alla fine i fili rimasti si liberano."""
    rilascio = threading.Event()
    stato = {"contenuti": {}, "lettura": None, "annullati": [], "fili": [], "rilascio": rilascio}

    def elenco(cartella, cercati, al_passo, protetta=False):
        assert not protetta, "in rete si legge senza SetErrorMode"
        stato["fili"].append(threading.current_thread())
        if stato["lettura"] is not None:
            return stato["lettura"](cartella, cercati, al_passo)
        contenuto = stato["contenuti"][os.path.normcase(cartella)]
        if isinstance(contenuto, Exception):
            raise contenuto
        trovati = {}
        for nome in contenuto:
            al_passo()
            if os.path.normcase(nome) in cercati:
                trovati[os.path.normcase(nome)] = nome
        return trovati

    def annulla(filo, per_quanto=3.0):
        stato["annullati"].append(filo)
        rilascio.set()

    monkeypatch.setattr(pulizia, "_elenco", elenco)
    monkeypatch.setattr(ricerca, "annulla_la_lettura", annulla)
    yield stato
    rilascio.set()


def _appesa(rilascio):
    def legge(cartella, _cercati, _al_passo):
        rilascio.wait(10)
        # Come una lettura annullata da CancelSynchronousIo.
        raise OSError(0, "Operazione annullata", cartella, 995)

    return legge


@pytest.mark.parametrize("video_nell_elenco", [True, False], ids=["Video c'e' ma non si legge", "Video sparita"])
def test_in_rete_maiuscole_e_cartelle_sparite(rete_finta, video_nell_elenco):
    # Video, e la cartella sotto, danno l'errore 3 in tutti e due i casi: se
    # Video e' sparita davvero lo dice l'elenco della condivisione. Se ha il
    # suo nome, Video c'e' ma non si legge, come una giunzione verso un disco
    # staccato, e le sue voci restano senza controllo.
    non_si_trova = FileNotFoundError(0, "Percorso non trovato", None, 3)
    rete_finta["contenuti"] = {
        os.path.normcase(RETE + "\\"): ["Musica", "Spenta", *(["Video"] if video_nell_elenco else [])],
        os.path.normcase(_in_rete("Musica")): ["a.mp3", "b.mp3"],
        os.path.normcase(_in_rete("Video")): non_si_trova,
        os.path.normcase(_in_rete("Video", "Serie")): non_si_trova,
        os.path.normcase(_in_rete("Spenta")): OSError(0, "Rete non raggiungibile", None, 1231),
    }
    video = [_in_rete("Video", "film.mkv"), _in_rete("Video", "Serie", "puntata.mkv")]
    percorsi = [_in_rete("Musica", "a.mp3"), _in_rete("musica", "B.MP3"), _in_rete("Musica", "c.mp3"), *video, _in_rete("Spenta", "d.mp3")]
    esito = pulizia.controlla(percorsi, risponde=lambda _r: True, attesa=5)
    sparito = {pulizia.norm(_in_rete("Musica", "c.mp3"))}
    if video_nell_elenco:
        assert esito["mancanti"] == sparito and esito["controllati"] == 3
    else:
        assert esito["mancanti"] == sparito | {pulizia.norm(p) for p in video} and esito["controllati"] == 5
    assert esito["nomi_veri"] == {pulizia.norm(_in_rete("Musica", "b.mp3")): _in_rete("Musica", "b.mp3")}
    assert esito["saltate"] == {}
    # Il giro di rete si fa in un filo a parte, sorvegliato.
    assert {f.name for f in rete_finta["fili"]} == {"MeTeOra, pulizia in rete"}
    assert rete_finta["annullati"] == []


def test_la_radice_che_non_si_legge_non_toglie_niente(rete_finta):
    # Sopra la radice non c'e' un elenco che possa dire che una cartella e'
    # sparita: con l'errore 3 dappertutto, le voci restano senza controllo.
    non_si_trova = FileNotFoundError(0, "Percorso non trovato", None, 3)
    rete_finta["contenuti"] = {os.path.normcase(RETE + "\\"): non_si_trova, os.path.normcase(_in_rete("Musica")): non_si_trova}
    esito = pulizia.controlla([_in_rete("a.mp3"), _in_rete("Musica", "b.mp3")], risponde=lambda _r: True)
    assert esito == {"mancanti": set(), "saltate": {}, "nomi_veri": {}, "controllati": 0, "contese": {}, "non_riconosciute": {},
        "dischi": {}}


def test_la_condivisione_si_chiama_come_la_scrivono_di_piu(rete_finta):
    rete_finta["contenuti"] = {os.path.normcase(RETE + "\\"): ["a.mp3"]}
    altra = "\\\\FINTO\\Condivisione"
    percorsi = [_in_rete("a.mp3"), altra + "\\a.mp3", _in_rete("A.mp3")]
    esito = pulizia.controlla(percorsi, risponde=lambda _r: True)
    assert esito["nomi_veri"] == {pulizia.norm(_in_rete("a.mp3")): _in_rete("a.mp3")}


def test_la_rete_che_tace_si_salta(rete_finta):
    rete_finta["lettura"] = _appesa(rete_finta["rilascio"])
    inizio = time.monotonic()
    esito = pulizia.controlla([_in_rete("Musica", "a.mp3"), _in_rete("Musica", "b.mp3")], risponde=lambda _r: True, attesa=0.3)
    assert time.monotonic() - inizio < 3
    assert esito == {"mancanti": set(), "saltate": {RETE: 2}, "nomi_veri": {}, "controllati": 0, "contese": {}, "non_riconosciute": {},
        "dischi": {}}
    # La lettura appesa si annulla, e il filo lasciato smette invece di
    # andare avanti con la cartella dopo.
    assert _aspetta(lambda: rete_finta["annullati"])
    filo = rete_finta["annullati"][0]
    assert filo.name == "MeTeOra, pulizia in rete"
    filo.join(3)
    assert not filo.is_alive() and len(rete_finta["fili"]) == 1


def test_la_rete_lenta_che_va_avanti_non_scade(rete_finta):
    def lenta(_cartella, cercati, al_passo):
        # Otto voci, una ogni decimo di secondo: piu' dell'attesa in tutto,
        # ma mai senza progressi per tanto.
        trovati = {}
        for nome in ("a.mp3", "b.mp3", "c.mp3", "d.mp3", "e.mp3", "f.mp3", "g.mp3", "Musica"):
            time.sleep(0.1)
            al_passo()
            if os.path.normcase(nome) in cercati:
                trovati[os.path.normcase(nome)] = nome
        return trovati

    rete_finta["lettura"] = lenta
    esito = pulizia.controlla([_in_rete("Musica", "a.mp3"), _in_rete("Musica", "z.mp3")], risponde=lambda _r: True, attesa=0.5)
    assert esito["mancanti"] == {pulizia.norm(_in_rete("Musica", "z.mp3"))} and esito["saltate"] == {}
    assert rete_finta["annullati"] == []


def test_cedere_il_passo_non_fa_scadere_la_rete(rete_finta):
    cedi = threading.Event()

    def legge(cartella, cercati, _al_passo):
        if os.path.normcase(cartella) == os.path.normcase(RETE + "\\"):
            # Dopo la prima cartella la finestra chiede il passo, per piu'
            # dell'attesa: il filo della rete aspetta, ma non e' appeso.
            cedi.set()
            threading.Timer(0.6, cedi.clear).start()
            return {"musica": "Musica"}
        return {nome: nome for nome in cercati if nome == "a.mp3"}

    rete_finta["lettura"] = legge
    inizio = time.monotonic()
    esito = pulizia.controlla([_in_rete("Musica", "a.mp3"), _in_rete("Musica", "b.mp3")], cedi=cedi, risponde=lambda _r: True, attesa=0.2)
    assert time.monotonic() - inizio >= 0.5
    assert esito["mancanti"] == {pulizia.norm(_in_rete("Musica", "b.mp3"))} and esito["saltate"] == {}
    assert rete_finta["annullati"] == []


def test_fermo_mentre_la_rete_tace(rete_finta):
    rete_finta["lettura"] = _appesa(rete_finta["rilascio"])
    inizio = time.monotonic()
    esito = pulizia.controlla([_in_rete("a.mp3")], fermo=lambda: time.monotonic() - inizio > 0.2, risponde=lambda _r: True, attesa=30)
    assert time.monotonic() - inizio < 2
    assert esito["saltate"] == {RETE: 1} and esito["mancanti"] == set()
    assert _aspetta(lambda: rete_finta["annullati"])


def test_la_rete_caduta_a_meta_non_toglie_niente(rete_finta):
    rete_finta["contenuti"] = {os.path.normcase(RETE + "\\"): ["a.mp3"]}
    risposte = iter([True, False])
    esito = pulizia.controlla([_in_rete("a.mp3"), _in_rete("b.mp3")], risponde=lambda _r: next(risposte))
    assert esito == {"mancanti": set(), "saltate": {RETE: 2}, "nomi_veri": {}, "controllati": 0, "contese": {}, "non_riconosciute": {},
        "dischi": {}}


def test_pulizia_finita(cartella):
    resta = _file(cartella / "resta.mp3")
    sparito = cartella / "sparito.mp3"
    arrivati = []
    lavoro = pulizia.Pulizia(iter([str(resta), str(sparito)]), lambda esito: arrivati.append((threading.current_thread().name, esito)))
    assert lavoro.avvia() is lavoro
    lavoro.aspetta(10)
    assert arrivati == [("MeTeOra, pulizia", {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 2,
        "contese": {}, "non_riconosciute": {}, "dischi": {}})]


def test_pulizia_fermata_non_avvisa(cartella):
    cedi = threading.Event()
    cedi.set()
    arrivati = []
    lavoro = pulizia.Pulizia([str(cartella / "a.mp3")], arrivati.append, cedi=cedi).avvia()
    time.sleep(0.1)
    lavoro.ferma()
    lavoro.aspetta(5)
    assert not any(f.name == "MeTeOra, pulizia" for f in threading.enumerate())
    assert arrivati == []


def test_pulizia_guasta(monkeypatch, capsys):
    def guasta(*_altro, **_nominati):
        raise RuntimeError("guasto finto")

    monkeypatch.setattr(pulizia, "controlla", guasta)
    arrivati = []
    pulizia.Pulizia(["C:\\a.mp3"], arrivati.append).avvia().aspetta(5)
    assert arrivati == [{"errore": "RuntimeError: guasto finto."}]
    assert "RuntimeError: guasto finto" in capsys.readouterr().err


def test_pulizia_guasta_sul_disco(monkeypatch, capsys):
    def guasta(*_altro, **_nominati):
        raise PermissionError(13, "Accesso negato")

    monkeypatch.setattr(pulizia, "controlla", guasta)
    arrivati = []
    pulizia.Pulizia(["C:\\a.mp3"], arrivati.append).avvia().aspetta(5)
    assert arrivati == [{"errore": "Accesso negato."}]
    assert "PermissionError" in capsys.readouterr().err


# La protezione dei dischi (1.112.0).


DISCO = "F:"
# Due numeri di serie, come li scrive il comando vol.
PRIMO, SECONDO = "1A2B-3C4D", "5E6F-7A8B"
# Due MachineGuid, come li scrive Windows.
GUID, ALTRO_GUID = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0", "11111111-2222-3333-4444-555555555555"


@pytest.fixture
def disco_finto(monkeypatch):
    """La lettera F: con cartelle finte, come rete_finta: stato["contenuti"]
    dice cosa c'e' in ogni cartella, norm -> nomi o un'eccezione da
    sollevare, e stato["lette"] annota le cartelle lette. F: e' un'unita'
    del PC anche dove questa macchina ha un'unita' di rete con quella
    lettera: il disco vero non si tocca."""
    stato = {"contenuti": {}, "lette": []}

    def elenco(cartella, cercati, al_passo, protetta=False):
        assert protetta, "le unita' del PC si leggono senza la finestra di errore"
        stato["lette"].append(os.path.normcase(cartella))
        contenuto = stato["contenuti"].get(os.path.normcase(cartella), [])
        if isinstance(contenuto, Exception):
            raise contenuto
        return {os.path.normcase(nome): nome for nome in contenuto if os.path.normcase(nome) in cercati}

    monkeypatch.setattr(pulizia, "_elenco", elenco)
    monkeypatch.setattr(ricerca, "in_rete", lambda percorso: percorso.startswith("\\\\"))
    return stato


def _metti(stato, *percorsi):
    """I file sul disco finto, con le cartelle che portano a loro."""
    for percorso in percorsi:
        cartella, nome = ntpath.split(percorso)
        while nome:
            nomi = stato["contenuti"].setdefault(os.path.normcase(cartella), [])
            if nome not in nomi:
                nomi.append(nome)
            cartella, nome = ntpath.split(cartella)


def _chi(*risposte):
    """Chi risponde alla lettera, per controlla: le risposte una dopo
    l'altra, e l'ultima per sempre."""
    rimaste = list(risposte)

    def identita(radice):
        assert radice == DISCO
        return rimaste.pop(0) if len(rimaste) > 1 else rimaste[0]

    return identita


def _sul_disco(*nomi):
    return [ntpath.join(DISCO + "\\", "Musica", nome) for nome in nomi]


def _controlla(percorsi, **opzioni):
    return pulizia.controlla(percorsi, risponde=lambda _r: True, **opzioni)


def test_il_suo_disco_si_pulisce_anche_se_manca_quasi_tutto(disco_finto):
    # Il numero di serie e' quello che si ricorda: e' il disco giusto, e i
    # file che non ha sono spariti davvero.
    presente, *spariti = _sul_disco("a.mp3", "b.mp3", "c.mp3", "d.mp3")
    _metti(disco_finto, presente)
    esito = _controlla([presente, *spariti], dischi={DISCO: {"disco": PRIMO}}, identita=_chi(PRIMO))
    assert esito == {"mancanti": {pulizia.norm(p) for p in spariti}, "saltate": {}, "contese": {}, "non_riconosciute": {}, "dischi": {},
        "nomi_veri": {}, "controllati": 4}


def test_un_altro_disco_nella_stessa_lettera_si_salta(disco_finto):
    # La chiavetta di prima e' staccata, e nella stessa lettera ce n'e'
    # un'altra: le voci restano, e la lettera diventa contesa, senza leggere
    # nemmeno una cartella.
    percorsi = _sul_disco("a.mp3", "b.mp3", "c.mp3")
    esito = _controlla(percorsi, dischi={DISCO: {"disco": PRIMO}}, identita=_chi(SECONDO))
    assert esito == {"mancanti": set(), "saltate": {}, "contese": {DISCO: 3}, "non_riconosciute": {}, "dischi": {DISCO: {"disco": PRIMO,
        "altri": [SECONDO]}},
        "nomi_veri": {}, "controllati": 0}
    assert disco_finto["lette"] == []


def test_la_lettera_contesa_resta_contesa_anche_con_il_suo_disco(disco_finto):
    # Tornata la chiavetta di prima, le voci della lettera sono mescolate a
    # quelle dell'altra, e nessuna si puo' dare per persa.
    presente, sparito = _sul_disco("a.mp3", "b.mp3")
    _metti(disco_finto, presente)
    contesa = {DISCO: {"disco": PRIMO, "altri": [SECONDO]}}
    esito = _controlla([presente, sparito], dischi=contesa, identita=_chi(PRIMO))
    assert esito == {"mancanti": set(), "saltate": {}, "contese": {DISCO: 2}, "non_riconosciute": {}, "dischi": {}, "nomi_veri": {},
        "controllati": 0}
    # Con l'altra il ricordo non cambia; con un terzo disco, si aggiunge.
    assert _controlla([presente], dischi=contesa, identita=_chi(SECONDO))["dischi"] == {}
    esito = _controlla([presente], dischi=contesa, identita=_chi("9F00-0001"))
    assert esito["dischi"] == {DISCO: {"disco": PRIMO, "altri": [SECONDO, "9F00-0001"]}}
    assert disco_finto["lette"] == []
    # Il ricordo dato non cambia.
    assert contesa == {DISCO: {"disco": PRIMO, "altri": [SECONDO]}}


def test_la_prima_volta_il_disco_con_i_suoi_file_si_impara(disco_finto):
    # La meta' dei file controllati c'e': e' il disco giusto, si impara e si pulisce.
    presente, sparito = _sul_disco("a.mp3", "b.mp3")
    _metti(disco_finto, presente)
    esito = _controlla([presente, sparito], identita=_chi(PRIMO))
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "contese": {}, "non_riconosciute": {},
        "dischi": {DISCO: {"disco": PRIMO}}, "nomi_veri": {}, "controllati": 2}


def test_la_prima_volta_con_le_voci_di_un_disco_mai_visto(disco_finto):
    # La regola della meta' resta per le voci di un disco che MeTeOra non ha
    # mai visto, come quelle scritte prima della 1.112.0: tre file della
    # chiavetta infilata e due di un'altra, staccata, che la Sentinella non
    # ha visto. La meta' c'e', la lettera diventa di quella infilata, e le
    # voci dell'altra si tolgono.
    suoi, dell_altra = _sul_disco("a.mp3", "b.mp3", "c.mp3"), _sul_disco("x.mp3", "y.mp3")
    _metti(disco_finto, *suoi)
    esito = _controlla([*suoi, *dell_altra], identita=_chi(PRIMO))
    assert esito["mancanti"] == {pulizia.norm(p) for p in dell_altra} and esito["dischi"] == {DISCO: {"disco": PRIMO}}
    assert esito["contese"] == {} and esito["non_riconosciute"] == {}


def test_la_prima_volta_con_il_disco_visto_dalla_sentinella(disco_finto):
    # Lo stesso disco che la Sentinella ha visto all'uso: si impara con la
    # regola della meta', e il disco visto diventa il suo.
    suoi, sparito = _sul_disco("a.mp3", "b.mp3"), _sul_disco("c.mp3")[0]
    _metti(disco_finto, *suoi)
    visto = {DISCO: {"visti": [PRIMO]}}
    esito = _controlla([*suoi, sparito], dischi=visto, identita=_chi(PRIMO))
    assert esito["mancanti"] == {pulizia.norm(sparito)} and esito["dischi"] == {DISCO: {"disco": PRIMO}}
    # Senza la meta' dei file non si impara, come la prima volta di sempre.
    esito = _controlla([suoi[0], sparito, *_sul_disco("d.mp3", "e.mp3")], dischi=visto, identita=_chi(PRIMO))
    assert esito["mancanti"] == set() and esito["non_riconosciute"] == {DISCO: 4} and esito["dischi"] == {DISCO: {"altri": [PRIMO]}}
    # Niente da controllare: il disco visto resta quello che era.
    disco_finto["contenuti"] = {"f:\\": ["Chiusa"], "f:\\chiusa": OSError(0, "Accesso negato", None, 5)}
    assert _controlla(["F:\\Chiusa\\a.mp3"], dischi=visto, identita=_chi(PRIMO))["dischi"] == {}


def test_due_chiavette_prima_che_la_pulizia_conosca_la_lettera(disco_finto):
    # La Sentinella ha visto una chiavetta, e all'avvio ne risponde un'altra:
    # le voci della lettera possono essere di tutte e due, e la lettera e'
    # usata da dischi diversi, senza leggere niente, anche se l'altra ha la
    # meta' dei file.
    suoi = _sul_disco("a.mp3", "b.mp3", "c.mp3")
    _metti(disco_finto, *suoi)
    esito = _controlla([*suoi, *_sul_disco("x.mp3")], dischi={DISCO: {"visti": [SECONDO]}}, identita=_chi(PRIMO))
    assert esito == {"mancanti": set(), "saltate": {}, "contese": {DISCO: 4}, "non_riconosciute": {},
        "dischi": {DISCO: {"altri": [SECONDO, PRIMO]}}, "nomi_veri": {}, "controllati": 0}
    assert disco_finto["lette"] == []
    # Cambiata a meta' giro, dopo la chiavetta vista: due dischi anche qui.
    esito = _controlla(suoi, dischi={DISCO: {"visti": [PRIMO]}}, identita=_chi(PRIMO, SECONDO))
    assert esito["contese"] == {DISCO: 3} and esito["dischi"] == {DISCO: {"altri": [PRIMO, SECONDO]}}


def test_i_ricordi_uniti():
    unisci = pulizia._unisci
    # Il disco visto resta visto finche' e' uno solo e la lettera non ha un disco.
    assert unisci(None, {"visti": [PRIMO]}) == {"visti": [PRIMO]} and unisci({"visti": [PRIMO]}, {"visti": [PRIMO]}) == {"visti": [PRIMO]}
    # Due dischi visti: la lettera e' contesa.
    assert unisci({"visti": [PRIMO]}, {"visti": [SECONDO]}) == {"altri": [PRIMO, SECONDO]}
    # Con un disco suo, il visto uguale sparisce e quello diverso va fra gli altri.
    assert unisci({"disco": PRIMO}, {"visti": [PRIMO]}) == {"disco": PRIMO}
    assert unisci({"disco": PRIMO}, {"visti": [SECONDO]}) == {"disco": PRIMO, "altri": [SECONDO]}
    assert unisci({"visti": [SECONDO]}, {"disco": PRIMO}) == {"disco": PRIMO, "altri": [SECONDO]}
    # Gli altri di tutti, in ordine e senza doppioni; il disco e' il primo che c'e'.
    assert unisci({"disco": PRIMO, "altri": [SECONDO]}, {"altri": ["9F00-0001", SECONDO]}) == {"disco": PRIMO, "altri": [SECONDO, "9F00-0001"]}
    assert unisci(None, {}) == {} and unisci({"altri": [PRIMO]}, None) == {"altri": [PRIMO]}
    # I ricordi dati non cambiano.
    ricordo = {"disco": PRIMO, "altri": [SECONDO]}
    unisci(ricordo, {"altri": ["9F00-0001"]})
    assert ricordo == {"disco": PRIMO, "altri": [SECONDO]}


def test_la_prima_volta_un_disco_senza_i_suoi_file_non_si_impara(disco_finto):
    # Meno della meta': un'altra chiavetta, o un disco che non ha piu' i file
    # che si conoscono. La lettera e' contesa e non si toglie niente,
    # nemmeno le schede scritte con le maiuscole sbagliate. Ha visto un
    # disco solo, che non e' il suo: non lo riconosce, e non e' usata da
    # dischi diversi.
    presente, *spariti = _sul_disco("a.mp3", "b.mp3", "c.mp3")
    _metti(disco_finto, presente)
    esito = _controlla([presente.upper(), *spariti], identita=_chi(PRIMO))
    assert esito == {"mancanti": set(), "saltate": {}, "contese": {}, "non_riconosciute": {DISCO: 3}, "dischi": {DISCO: {"altri": [PRIMO]}},
        "nomi_veri": {}, "controllati": 0}
    # Anche con un file solo, sparito: le voci restano.
    esito = _controlla([spariti[0]], identita=_chi(PRIMO))
    assert esito["mancanti"] == set() and esito["non_riconosciute"] == {DISCO: 1} and esito["dischi"] == {DISCO: {"altri": [PRIMO]}}
    # Agli avvii dopo, con lo stesso disco, la lettera resta non riconosciuta
    # e si salta senza leggerla; con un secondo disco e' usata da dischi diversi.
    disco_finto["lette"].clear()
    ricordo = {DISCO: {"altri": [PRIMO]}}
    esito = _controlla([presente, *spariti], dischi=ricordo, identita=_chi(PRIMO))
    assert esito["non_riconosciute"] == {DISCO: 3} and esito["contese"] == {} and esito["dischi"] == {}
    esito = _controlla([presente, *spariti], dischi=ricordo, identita=_chi(SECONDO))
    assert esito["contese"] == {DISCO: 3} and esito["non_riconosciute"] == {} and esito["dischi"] == {DISCO: {"altri": [PRIMO, SECONDO]}}
    assert disco_finto["lette"] == []


def test_la_prima_volta_senza_file_controllati_non_si_impara(disco_finto):
    # Tutto in una cartella che c'e' ma non si legge: niente da togliere, e
    # niente da cui riconoscere il disco.
    disco_finto["contenuti"] = {"f:\\": ["Chiusa"], "f:\\chiusa": OSError(0, "Accesso negato", None, 5)}
    esito = _controlla(["F:\\Chiusa\\a.mp3"], identita=_chi(PRIMO))
    assert esito == {"mancanti": set(), "saltate": {}, "contese": {}, "non_riconosciute": {}, "dischi": {}, "nomi_veri": {},
        "controllati": 0}


def test_un_disco_cambiato_a_meta_giro(disco_finto):
    # Le cartelle lette dopo il cambio erano dell'altro disco.
    presente, sparito = _sul_disco("a.mp3", "b.mp3")
    _metti(disco_finto, presente)
    esito = _controlla([presente, sparito], dischi={DISCO: {"disco": PRIMO}}, identita=_chi(PRIMO, SECONDO))
    assert esito == {"mancanti": set(), "saltate": {}, "contese": {DISCO: 2}, "non_riconosciute": {},
        "dischi": {DISCO: {"disco": PRIMO, "altri": [SECONDO]}}, "nomi_veri": {}, "controllati": 0}
    # La prima volta, nessuno dei due e' il suo disco: due dischi, e la
    # lettera e' usata da dischi diversi.
    esito = _controlla([presente, sparito], identita=_chi(PRIMO, SECONDO))
    assert esito["contese"] == {DISCO: 2} and esito["dischi"] == {DISCO: {"altri": [PRIMO, SECONDO]}}


def test_chi_risponde_non_si_legge(disco_finto):
    # Il disco che risponde non si riconosce: la lettera si salta senza
    # ricordare niente, e le voci restano per il prossimo avvio.
    presente, sparito = _sul_disco("a.mp3", "b.mp3")
    esito = _controlla([presente], dischi={DISCO: {"disco": PRIMO}}, identita=_chi(""))
    assert esito == {"mancanti": set(), "saltate": {}, "contese": {}, "non_riconosciute": {DISCO: 1}, "dischi": {}, "nomi_veri": {},
        "controllati": 0}
    assert disco_finto["lette"] == []
    # Anche se smette di leggersi alla fine del giro.
    _metti(disco_finto, presente)
    esito = _controlla([presente, sparito], dischi={DISCO: {"disco": PRIMO}}, identita=_chi(PRIMO, ""))
    assert esito == {"mancanti": set(), "saltate": {}, "contese": {}, "non_riconosciute": {DISCO: 2}, "dischi": {}, "nomi_veri": {},
        "controllati": 0}


def test_con_i_dischi_ignoti_ogni_lettera_si_salta(rete_finta):
    # Il file dei dischi non si legge: una lettera contesa sembrerebbe
    # nuova, quindi nessuna lettera si legge, si impara o si pulisce, anche
    # con il suo disco. Una condivisione scritta per esteso si pulisce come
    # sempre. Le cartelle di F: non sono fra quelle finte: leggerle
    # solleverebbe KeyError.
    rete_finta["contenuti"] = {os.path.normcase(RETE + "\\"): ["a.mp3"]}

    def identita(radice):
        return None if radice == RETE else PRIMO

    esito = _controlla([*_sul_disco("a.mp3", "b.mp3"), _in_rete("a.mp3"), _in_rete("b.mp3")], identita=identita, dischi_ignoti=True)
    assert esito["non_riconosciute"] == {DISCO: 2} and esito["dischi"] == {} and esito["contese"] == {} and esito["saltate"] == {}
    assert esito["mancanti"] == {pulizia.norm(_in_rete("b.mp3"))}


def test_la_condivisione_si_riconosce_dal_nome(rete_finta):
    # Per una condivisione scritta per esteso chi risponde non si chiede:
    # niente da imparare, e si pulisce come prima.
    rete_finta["contenuti"] = {os.path.normcase(RETE + "\\"): ["a.mp3"]}
    chieste = []
    esito = pulizia.controlla([_in_rete("a.mp3"), _in_rete("b.mp3")], risponde=lambda _r: True, identita=lambda r: chieste.append(r),
        dischi={RETE: {"disco": PRIMO}})
    assert esito["mancanti"] == {pulizia.norm(_in_rete("b.mp3"))} and esito["dischi"] == {} and esito["contese"] == {}
    assert chieste == [RETE, RETE]


def test_chi_risponde_a_ogni_tipo_di_unita(monkeypatch):
    tipi = {"E:": 2, "C:": 3, "D:": 5, "R:": 6, "Z:": 4, "Q:": 1, "X:": 0}
    # Nessuna lettera fatta con subst: le lettere di questa macchina non contano.
    monkeypatch.setattr(pulizia, "_bersaglio", lambda radice: "\\Device\\HarddiskVolume3")
    monkeypatch.setattr(pulizia, "_tipo_di_unita", lambda radice: tipi[radice])
    monkeypatch.setattr(pulizia, "_numero_di_serie", lambda radice: f"numero di {radice}")
    monkeypatch.setattr(pulizia, "_condivisione", lambda radice: f"condivisione di {radice}")
    # Le unita' del PC dal numero di serie: rimovibili, fisse, CD e dischi in memoria.
    assert [_identita_vera(r) for r in ("E:", "C:", "D:", "R:")] == ["numero di E:", "numero di C:", "numero di D:", "numero di R:"]
    # Quelle di rete con la lettera dalla condivisione; un tipo che non si sa, da niente.
    assert _identita_vera("Z:") == "condivisione di Z:"
    assert _identita_vera("Q:") == "" and _identita_vera("X:") == ""
    # Una condivisione scritta per esteso non si chiede.
    assert _identita_vera(RETE) is None


def test_una_lettera_fatta_con_subst(monkeypatch):
    # Per Windows non e' una connessione di rete, e ha il numero di serie del
    # volume su cui porta: si riconosce dal suo bersaglio, con il numero di
    # serie se e' sul PC. Il tipo si chiede solo per la lettera su cui porta.
    bersagli = {"X:": "\\??\\E:\\Musica\\", "Y:": "\\??\\E:\\Video", "W:": "\\??\\UNC\\Server\\Musica", "V:": "\\??\\E:\\",
        "M:": "\\??\\Z:\\Musica"}
    numeri = {"X:": PRIMO, "Y:": PRIMO, "V:": PRIMO}
    tipi, condivisioni, chiesti = {"E:": 3, "Z:": 4}, {"Z:": "\\\\iliadbox\\disco"}, []
    monkeypatch.setattr(pulizia, "_bersaglio", lambda radice: bersagli[radice])
    monkeypatch.setattr(pulizia, "_tipo_di_unita", lambda radice: chiesti.append(radice) or tipi[radice])
    monkeypatch.setattr(pulizia, "_numero_di_serie", lambda radice: numeri.get(radice, "") if radice != "M:" else pytest.fail("in rete non si chiede"))
    monkeypatch.setattr(pulizia, "_condivisione", lambda radice: condivisioni.get(radice, "") if radice == "Z:" else pytest.fail(
        "una subst non e' una connessione di rete"))
    # Spostata su un'altra cartella dello stesso volume, non e' piu' lei.
    assert _identita_vera("X:") == f"\\??\\e:\\musica {PRIMO}" and _identita_vera("Y:") == f"\\??\\e:\\video {PRIMO}"
    assert _identita_vera("V:") == f"\\??\\e: {PRIMO}"
    assert chiesti == ["E:", "E:", "E:"]
    # Su una condivisione, senza chiedere niente alla rete.
    assert _identita_vera("W:") == "\\??\\unc\\server\\musica" and chiesti == ["E:", "E:", "E:"]
    # Su un'unita' di rete con la lettera, come lei, dalla condivisione: il
    # numero di serie, in rete, non si chiede; se la condivisione non si
    # legge, non si sa.
    assert _identita_vera("M:") == "\\??\\z:\\musica \\\\iliadbox\\disco"
    condivisioni.clear()
    assert _identita_vera("M:") == ""
    # Sul PC, se il numero di serie non si legge, non si sa.
    numeri.pop("X:")
    assert _identita_vera("X:") == ""


def test_il_bersaglio_di_una_lettera(monkeypatch):
    class Kernel32:
        def __init__(self, risposta):
            self.risposta, self.chieste = risposta, []

        def QueryDosDeviceW(self, nome, spazio, misura):
            self.chieste.append((nome.value, misura))
            if self.risposta is None:
                return 0
            spazio.value = self.risposta
            return len(self.risposta) + 2

    kernel32 = Kernel32("\\??\\E:\\Musica")
    monkeypatch.setattr(pulizia, "ctypes", _ctypes_finto(kernel32))
    assert pulizia._bersaglio("X:") == "\\??\\E:\\Musica" and kernel32.chieste == [("X:", 1024)]
    kernel32.risposta = None
    assert pulizia._bersaglio("X:") == ""


class _Kernel32:
    """Il kernel32 vero, con GetVolumeInformationW finto: scrive numero nel
    numero di serie, o fallisce se numero e' None, e annota la radice e i
    modi di errore del momento."""

    def __init__(self, numero):
        self.numero, self.chiamate = numero, []

    def __getattr__(self, nome):
        return getattr(ctypes.windll.kernel32, nome)

    def GetVolumeInformationW(self, radice, _nome, _misura, seriale, *_altro):
        self.chiamate.append((radice.value, _modi_di_errore()))
        if self.numero is None:
            return 0
        seriale._obj.value = self.numero
        return 1


def _ctypes_finto(kernel32=None, mpr=None):
    class Ctypes:
        windll = types.SimpleNamespace(kernel32=kernel32 or ctypes.windll.kernel32)

        def WinDLL(self, nome):
            assert nome == "mpr"
            return mpr

        def __getattr__(self, nome):
            return getattr(ctypes, nome)

    return Ctypes()


def test_il_numero_di_serie_come_lo_dice_vol(monkeypatch):
    filo, processo = _modi_di_errore()
    kernel32 = _Kernel32(0x0A2B3C4D)
    monkeypatch.setattr(pulizia, "ctypes", _ctypes_finto(kernel32))
    assert pulizia._numero_di_serie("F:") == "0A2B-3C4D"
    # Sulla radice, senza la finestra di errore di Windows, solo in questo filo.
    radice, (nel_filo, nel_processo) = kernel32.chiamate[0]
    assert radice == "F:\\" and nel_filo & pulizia._SENZA_FINESTRE_DI_ERRORE and nel_processo == processo
    assert _modi_di_errore() == (filo, processo)
    kernel32.numero = None
    assert pulizia._numero_di_serie("F:") == ""


def test_la_condivisione_di_un_unita_di_rete(monkeypatch):
    class Mpr:
        risposta = (0, "\\\\IliadBox\\Disco")

        def WNetGetConnectionW(self, unita, spazio, lunghezza):
            assert unita == "Z:" and lunghezza._obj.value == len(spazio)
            codice, spazio.value = self.risposta
            return codice

    mpr = Mpr()
    monkeypatch.setattr(pulizia, "ctypes", _ctypes_finto(mpr=mpr))
    assert pulizia._condivisione("Z:") == "\\\\iliadbox\\disco"
    # ERROR_NOT_CONNECTED: la lettera non porta a una condivisione.
    mpr.risposta = (2250, "")
    assert pulizia._condivisione("Z:") == ""


def test_i_dischi_nel_loro_file(tmp_path):
    percorso = tmp_path / "MeTeOra - Dischi.json"
    dischi = pulizia.Dischi(str(percorso), computer="GIGANTE")
    assert dischi.conosciuti() == {} and not dischi.modificati and dischi.computer == "GIGANTE"
    assert dischi.aggiorna({"F:": {"disco": PRIMO}, "G:": {"altri": [SECONDO]}}) and dischi.modificati
    assert not dischi.aggiorna({"F:": {"disco": PRIMO}})
    # Le copie non toccano i ricordi.
    copia = dischi.conosciuti()
    copia["G:"]["altri"].append(PRIMO)
    assert dischi.conosciuti()["G:"] == {"altri": [SECONDO]}
    dischi.salva()
    assert not dischi.modificati and not (tmp_path / "MeTeOra - Dischi.json.tmp").exists()
    # Sotto il nome del computer, senza il MachineGuid, che qui non si legge.
    assert json.loads(percorso.read_text(encoding="utf-8")) == {"GIGANTE": {"lettere": {"F:": {"disco": PRIMO}, "G:": {"altri": [SECONDO]}}}}
    assert pulizia.Dischi(str(percorso), computer="GIGANTE").conosciuti() == {"F:": {"disco": PRIMO}, "G:": {"altri": [SECONDO]}}
    # Un file che manca e' il primo avvio, non un errore.
    assert pulizia.Dischi(str(tmp_path / "manca.json")).errore is None


def test_ogni_computer_ha_i_suoi_dischi(tmp_path, monkeypatch):
    # I dati portati su un altro computer, con la versione portatile o
    # copiando i file: le sue lettere non diventano contese, e i dischi del
    # primo restano com'erano.
    percorso = tmp_path / "MeTeOra - Dischi.json"
    gigante = {"guid": GUID, "lettere": {"C:": {"disco": PRIMO}, "F:": {"disco": PRIMO, "altri": [SECONDO]}}}
    percorso.write_text(json.dumps({"GIGANTE": gigante}), encoding="utf-8")
    mini = pulizia.Dischi(str(percorso), computer="MINI", guid=ALTRO_GUID)
    assert mini.conosciuti() == {} and not mini.contesa("F:") and not mini.modificati
    assert mini.aggiorna({"C:": {"disco": SECONDO}})
    mini.salva()
    assert json.loads(percorso.read_text(encoding="utf-8")) == {"GIGANTE": gigante, "MINI": {"guid": ALTRO_GUID, "lettere": {"C:": {"disco": SECONDO}}}}
    assert pulizia.Dischi(str(percorso), computer="GIGANTE").conosciuti() == {"C:": {"disco": PRIMO}, "F:": {"disco": PRIMO, "altri": [SECONDO]}}
    # Un computer senza ricordi non scrive la sua parte.
    vuoto = tmp_path / "vuoto.json"
    pulizia.Dischi(str(vuoto), computer="MINI").salva()
    assert json.loads(vuoto.read_text(encoding="utf-8")) == {}
    # Il nome del computer e' quello di Windows, in maiuscolo.
    monkeypatch.setenv("COMPUTERNAME", "GabryBat")
    assert pulizia.nome_del_computer() == "GABRYBAT" and pulizia.Dischi(str(percorso)).computer == "GABRYBAT"


def test_il_computer_rinominato_ritrova_i_suoi_dischi(tmp_path):
    # Il nome resta la chiave, e accanto c'e' il MachineGuid: con un nome
    # nuovo e lo stesso MachineGuid i ricordi del nome vecchio sono suoi, e
    # al salvataggio la chiave si rinomina.
    percorso = tmp_path / "MeTeOra - Dischi.json"
    vecchi = {"F:": {"disco": PRIMO, "altri": [SECONDO]}}
    mini = {"guid": ALTRO_GUID, "lettere": {"C:": {"disco": SECONDO}}}
    percorso.write_text(json.dumps({"GIGANTE": {"guid": GUID, "lettere": vecchi}, "MINI": mini}), encoding="utf-8")
    dischi = pulizia.Dischi(str(percorso), computer="GABRYBAT", guid=GUID)
    assert dischi.conosciuti() == vecchi and dischi.contesa("F:") and dischi.modificati
    dischi.salva()
    assert json.loads(percorso.read_text(encoding="utf-8")) == {"GABRYBAT": {"guid": GUID, "lettere": vecchi}, "MINI": mini}
    # Il nome c'e' gia': vale lui, anche con un altro MachineGuid, come
    # dopo aver reinstallato Windows, e quello nuovo prende il posto del vecchio.
    dischi = pulizia.Dischi(str(percorso), computer="MINI", guid=GUID)
    assert dischi.conosciuti() == {"C:": {"disco": SECONDO}} and not dischi.modificati
    dischi.aggiorna({"D:": {"disco": PRIMO}})
    dischi.salva()
    assert json.loads(percorso.read_text(encoding="utf-8"))["MINI"] == {"guid": GUID, "lettere": {"C:": {"disco": SECONDO}, "D:": {"disco": PRIMO}}}
    # Due nomi con lo stesso MachineGuid, come due computer clonati: non si
    # sa quale sia, e si va per nome; e senza MachineGuid, sempre per nome.
    assert pulizia.Dischi(str(percorso), computer="NUOVO", guid=GUID).conosciuti() == {}
    assert pulizia.Dischi(str(percorso), computer="NUOVO", guid="").conosciuti() == {}
    nuovo = pulizia.Dischi(str(percorso), computer="NUOVO", guid=ALTRO_GUID)
    assert nuovo.conosciuti() == {} and not nuovo.modificati


def test_il_machine_guid_che_non_si_legge_resta_nel_file(tmp_path):
    # Una sessione in cui il MachineGuid non si legge riscrive quello che il
    # file aveva per il suo nome: un nome nuovo, dopo, ritrova i ricordi.
    percorso = tmp_path / "MeTeOra - Dischi.json"
    percorso.write_text(json.dumps({"GIGANTE": {"guid": GUID, "lettere": {"F:": {"disco": PRIMO}}}}), encoding="utf-8")
    dischi = pulizia.Dischi(str(percorso), computer="GIGANTE", guid="")
    assert dischi.aggiorna({"G:": {"disco": SECONDO}})
    dischi.salva()
    lettere = {"F:": {"disco": PRIMO}, "G:": {"disco": SECONDO}}
    assert json.loads(percorso.read_text(encoding="utf-8")) == {"GIGANTE": {"guid": GUID, "lettere": lettere}}
    assert pulizia.Dischi(str(percorso), computer="GABRYBAT", guid=GUID).conosciuti() == lettere
    # Quello letto adesso, se c'e', vale piu' di quello del file.
    dischi = pulizia.Dischi(str(percorso), computer="GIGANTE", guid=ALTRO_GUID)
    dischi.aggiorna({"H:": {"disco": PRIMO}})
    dischi.salva()
    assert json.loads(percorso.read_text(encoding="utf-8"))["GIGANTE"]["guid"] == ALTRO_GUID


def test_il_machine_guid_dal_registro(monkeypatch):
    # Dalla vista a 64 bit del registro; "" se non si legge.
    aperte = []

    class Chiave:
        def __enter__(self):
            return self

        def __exit__(self, *_eccezione):
            return False

    def apri(radice, percorso, riservato, accesso):
        aperte.append((radice, percorso, accesso))
        return Chiave()

    finto = types.SimpleNamespace(HKEY_LOCAL_MACHINE="HKLM", KEY_READ=0x20019, KEY_WOW64_64KEY=0x100, OpenKey=apri,
        QueryValueEx=lambda chiave, nome: (" " + GUID.upper() + " ", 1) if nome == "MachineGuid" else None)
    monkeypatch.setitem(sys.modules, "winreg", finto)
    assert _guid_vero() == GUID
    assert aperte == [("HKLM", r"SOFTWARE\Microsoft\Cryptography", 0x20019 | 0x100)]

    def negato(*_argomenti):
        raise PermissionError(5, "Accesso negato")

    finto.OpenKey = negato
    assert _guid_vero() == ""


def test_i_dischi_visti_dalla_sentinella(tmp_path):
    dischi = pulizia.Dischi(str(tmp_path / "MeTeOra - Dischi.json"), computer="GIGANTE")
    # Una lettera che non ha ancora un disco suo: il primo disco visto si ricorda.
    assert dischi.visto("F:", PRIMO) and dischi.conosciuti() == {"F:": {"visti": [PRIMO]}} and dischi.modificati
    assert not dischi.visto("F:", PRIMO) and not dischi.contesa("F:")
    # Un altro disco nella stessa lettera: la lettera e' contesa.
    assert dischi.visto("F:", SECONDO) and dischi.conosciuti()["F:"] == {"altri": [PRIMO, SECONDO]} and dischi.contesa("F:")
    # Il suo disco non cambia niente; un altro rende contesa la lettera.
    dischi.aggiorna({"E:": {"disco": PRIMO}})
    assert not dischi.visto("E:", PRIMO) and not dischi.contesa("E:")
    assert dischi.visto("E:", SECONDO) and dischi.conosciuti()["E:"] == {"disco": PRIMO, "altri": [SECONDO]} and dischi.contesa("E:")
    # Una contesa impara anche i dischi nuovi, e non quelli gia' visti.
    assert not dischi.visto("E:", SECONDO) and dischi.visto("E:", "9F00-0001")
    assert dischi.conosciuti()["E:"] == {"disco": PRIMO, "altri": [SECONDO, "9F00-0001"]}


def test_riconosci_questo_disco(tmp_path):
    percorso = tmp_path / "MeTeOra - Dischi.json"
    dischi = pulizia.Dischi(str(percorso), computer="GIGANTE")
    dischi.aggiorna({"F:": {"disco": PRIMO, "altri": [SECONDO]}, "G:": {"altri": [PRIMO]}})
    copia = dischi.per_la_pulizia()
    # La lettera e' del disco che risponde adesso, e non e' piu' contesa.
    assert dischi.riconosci("F:", SECONDO) and dischi.conosciuti()["F:"] == {"disco": SECONDO} and not dischi.contesa("F:")
    assert dischi.riconosci("G:", PRIMO) and dischi.conosciuti()["G:"] == {"disco": PRIMO}
    assert not dischi.riconosci("G:", PRIMO)
    # La finestra ne tiene i mancanti che la pulizia trovera' sulla copia,
    # forse letta con un altro disco.
    assert dischi.riconosciute_dopo_la_copia() == {"F:", "G:"}
    # La pulizia, che aveva la copia di prima, non la rende di nuovo contesa;
    # le altre lettere si uniscono come sempre.
    assert copia["F:"] == {"disco": PRIMO, "altri": [SECONDO]}
    assert dischi.aggiorna({"F:": {"disco": PRIMO, "altri": [SECONDO]}, "H:": {"disco": PRIMO}})
    assert dischi.conosciuti() == {"F:": {"disco": SECONDO}, "G:": {"disco": PRIMO}, "H:": {"disco": PRIMO}}
    # Con la copia nuova per la pulizia, quello che dice conta di nuovo.
    dischi.per_la_pulizia()
    assert dischi.riconosciute_dopo_la_copia() == set()
    assert dischi.aggiorna({"F:": {"disco": SECONDO, "altri": [PRIMO]}}) and dischi.contesa("F:")
    # La Sentinella vede ancora chi risponde alla lettera riconosciuta.
    assert not dischi.visto("G:", PRIMO) and dischi.visto("G:", SECONDO) and dischi.contesa("G:")


def test_la_pulizia_non_cancella_quello_che_la_sentinella_ha_visto(tmp_path):
    # Mentre la pulizia lavora sulla sua copia, la Sentinella rende contesa
    # una lettera e ne vede un'altra: i ricordi della pulizia si uniscono a
    # quelli di adesso, e niente si perde.
    dischi = pulizia.Dischi(str(tmp_path / "MeTeOra - Dischi.json"), computer="GIGANTE")
    dischi.aggiorna({"E:": {"disco": PRIMO}})
    dischi.per_la_pulizia()
    dischi.visto("E:", SECONDO)
    dischi.visto("F:", SECONDO)
    assert dischi.aggiorna({"F:": {"disco": PRIMO}, "G:": {"altri": [PRIMO]}})
    assert dischi.conosciuti() == {"E:": {"disco": PRIMO, "altri": [SECONDO]}, "F:": {"disco": PRIMO, "altri": [SECONDO]},
        "G:": {"altri": [PRIMO]}}
    # Il disco imparato dalla pulizia e quello visto sono lo stesso: niente contesa.
    dischi.visto("H:", PRIMO)
    dischi.aggiorna({"H:": {"disco": PRIMO}})
    assert dischi.conosciuti()["H:"] == {"disco": PRIMO}


def _lettere(**computer):
    """Il file dei dischi con le lettere di ogni computer, senza MachineGuid."""
    return json.dumps({nome: {"lettere": lettere} for nome, lettere in computer.items()})


@pytest.mark.parametrize("contenuto, motivo", [
    ("non e' JSON", "Expecting value"),
    ("[1, 2]", "non contiene i dischi dei computer"),
    ("null", "non contiene i dischi dei computer"),
    (json.dumps({"GIGANTE": [1, 2]}), "i dischi di GIGANTE non si capiscono"),
    (json.dumps({"GIGANTE": {"F:": {"disco": PRIMO}}}), "i dischi di GIGANTE non si capiscono"),
    (json.dumps({"GIGANTE": {"guid": GUID, "lettere": [1, 2]}}), "i dischi di GIGANTE non si capiscono"),
    (json.dumps({"GIGANTE": {"guid": 5, "lettere": {}}}), "i dischi di GIGANTE non si capiscono"),
    (_lettere(GIGANTE={"F:": {"disco": PRIMO, "altri": [SECONDO]}, "G:": PRIMO}), "il ricordo di G: su GIGANTE non si capisce"),
    (_lettere(GIGANTE={"F:": {"disco": 5}}), "il ricordo di F: su GIGANTE non si capisce"),
    (_lettere(GIGANTE={"F:": {"disco": PRIMO, "altri": SECONDO}}), "il ricordo di F: su GIGANTE non si capisce"),
    (_lettere(GIGANTE={"F:": {"disco": PRIMO, "altri": [SECONDO, ""]}}), "il ricordo di F: su GIGANTE non si capisce"),
    (_lettere(GIGANTE={"F:": {"disco": PRIMO, "altri": [PRIMO]}}), "il ricordo di F: su GIGANTE non si capisce"),
    (_lettere(GIGANTE={"F:": {"visti": PRIMO}}), "il ricordo di F: su GIGANTE non si capisce"),
    (_lettere(GIGANTE={}, MINI={"F:": {"disco": 5}}), "il ricordo di F: su MINI non si capisce"),
], ids=["rovinato", "una lista", "null", "un computer che non e' un dizionario", "un computer senza le sue lettere", "lettere che non sono un dizionario",
    "un MachineGuid che non e' un testo", "un ricordo che non e' un dizionario", "un disco che non e' un testo", "altri che non sono una lista",
    "un altro vuoto", "il disco anche fra gli altri", "visti che non sono una lista", "un altro computer rovinato"])
def test_un_file_dei_dischi_che_non_si_legge_resta_com_e(tmp_path, contenuto, motivo):
    # Le lettere contese non si rileggono da nessuna parte: il file non si
    # sovrascrive, e non si impara niente, nemmeno le lettere che si capiscono,
    # nemmeno se il ricordo rovinato e' di un altro computer.
    percorso = tmp_path / "MeTeOra - Dischi.json"
    percorso.write_text(contenuto, encoding="utf-8")
    dischi = pulizia.Dischi(str(percorso), computer="GIGANTE")
    assert dischi.conosciuti() == {} and motivo in dischi.errore
    assert not dischi.aggiorna({"H:": {"disco": PRIMO}}) and not dischi.modificati
    assert not dischi.visto("H:", PRIMO) and not dischi.riconosci("H:", PRIMO) and not dischi.modificati
    dischi.salva()
    assert percorso.read_text(encoding="utf-8") == contenuto and not (tmp_path / "MeTeOra - Dischi.json.tmp").exists()


def test_un_file_dei_dischi_bloccato(tmp_path, monkeypatch):
    # Per esempio da un antivirus: vale come illeggibile, non come vuoto.
    def bloccato(*_argomenti, **_opzioni):
        raise PermissionError(13, "Accesso negato")

    monkeypatch.setattr(pulizia, "open", bloccato, raising=False)
    dischi = pulizia.Dischi(str(tmp_path / "MeTeOra - Dischi.json"))
    assert dischi.errore and "Accesso negato" in dischi.errore


def test_dal_file_dei_dischi_si_tiene_solo_cio_che_serve(tmp_path):
    # Le chiavi in piu', come una nota scritta a mano, e i ricordi vuoti; due
    # dischi visti fanno la lettera contesa, e un disco visto con un disco suo
    # diverso va fra gli altri.
    percorso = tmp_path / "MeTeOra - Dischi.json"
    percorso.write_text(json.dumps({"GIGANTE": {"nota": "a mano", "lettere": {"F:": {"disco": PRIMO, "altri": [SECONDO], "nota": "a mano"},
        "G:": {"altri": [PRIMO]}, "J:": {}, "K:": {"visti": [PRIMO]}, "L:": {"visti": [PRIMO, SECONDO]}, "M:": {"disco": PRIMO, "visti": [SECONDO]}}}}),
        encoding="utf-8")
    dischi = pulizia.Dischi(str(percorso), computer="GIGANTE")
    assert dischi.conosciuti() == {"F:": {"disco": PRIMO, "altri": [SECONDO]}, "G:": {"altri": [PRIMO]}, "K:": {"visti": [PRIMO]},
        "L:": {"altri": [PRIMO, SECONDO]}, "M:": {"disco": PRIMO, "altri": [SECONDO]}} and dischi.errore is None


# La Sentinella: il disco di una lettera guardato quando MeTeOra ne usa un file (1.112.0).


def test_la_lettera_di_un_percorso():
    assert [pulizia.lettera_di(p) for p in ("e:\\Musica\\a.mp3", "F:/a.mp3", "E:\\")] == ["E:", "F:", "E:"]
    # Le condivisioni scritte per esteso, i percorsi relativi e cio' che non e' un testo non hanno lettera.
    assert [pulizia.lettera_di(p) for p in (_in_rete("a.mp3"), "brano.mp3", "C:brano.mp3", "\\brano.mp3", "E:", "1:\\a.mp3", "è:\\a.mp3", None, 5)] == [None] * 9


class _Orologio:
    def __init__(self):
        self.adesso = 100.0

    def __call__(self):
        return self.adesso


def _sentinella(chi):
    """Una Sentinella che annota le domande senza farle: le fa la prova, con
    lavori.pop(0)(). chi e' un dizionario lettera -> chi risponde."""
    lavori, visti, chieste, orologio = [], [], [], _Orologio()

    def identita(lettera):
        chieste.append(lettera)
        risposta = chi[lettera]
        if isinstance(risposta, Exception):
            raise risposta
        return risposta

    sentinella = pulizia.Sentinella(lambda lettera, uno: visti.append((lettera, uno)), identita=identita,
        avvia=lambda lavoro, _nome: lavori.append(lavoro), adesso=orologio)
    return types.SimpleNamespace(sentinella=sentinella, lavori=lavori, visti=visti, chieste=chieste, orologio=orologio)


def test_la_sentinella_chiede_una_volta_per_lettera():
    s = _sentinella({"E:": PRIMO, "F:": SECONDO})
    # Tanti file, due lettere: due domande; la condivisione e il percorso relativo non contano.
    s.sentinella.guarda("E:\\a.mp3", "e:\\b.mp3", "F:\\c.mp3", _in_rete("d.mp3"), "brano.mp3")
    assert len(s.lavori) == 2
    # Finche' la domanda non torna, un'altra non parte.
    s.sentinella.guarda("E:\\c.mp3")
    assert len(s.lavori) == 2
    while s.lavori:
        s.lavori.pop(0)()
    assert s.chieste == ["E:", "F:"] and s.visti == [("E:", PRIMO), ("F:", SECONDO)]
    # Per qualche secondo ci si fida della risposta; dopo, si richiede.
    s.orologio.adesso += pulizia.MEMORIA_DELLA_SENTINELLA - 0.1
    s.sentinella.guarda("E:\\a.mp3")
    assert s.lavori == []
    s.orologio.adesso += 0.2
    s.sentinella.guarda("E:\\a.mp3")
    s.lavori.pop(0)()
    assert s.chieste == ["E:", "F:", "E:"] and s.visti[-1] == ("E:", PRIMO)


def test_la_sentinella_e_una_lettera_che_non_si_legge():
    # Chi risponde non si sa: niente da dire; un errore di Windows vale lo
    # stesso, e la lettera si puo' richiedere dopo la memoria.
    s = _sentinella({"G:": "", "H:": OSError(21, "Il dispositivo non e' pronto")})
    s.sentinella.guarda("G:\\a.mp3", "H:\\a.mp3")
    while s.lavori:
        s.lavori.pop(0)()
    assert s.visti == [] and s.chieste == ["G:", "H:"]
    s.orologio.adesso += pulizia.MEMORIA_DELLA_SENTINELLA
    s.sentinella.guarda("H:\\a.mp3")
    assert len(s.lavori) == 1


def test_la_sentinella_non_aspetta_una_lettera_che_non_risponde():
    # Un lettore che resta appeso: guarda torna subito, la domanda resta nel
    # suo filo, e la risposta arriva da li' quando c'e'.
    sblocca, arrivati = threading.Event(), []
    finito = threading.Event()

    def identita(lettera):
        sblocca.wait(5)
        return PRIMO

    def visto(lettera, chi):
        arrivati.append((lettera, chi, threading.current_thread() is threading.main_thread()))
        finito.set()

    sentinella = pulizia.Sentinella(visto, identita=identita)
    inizio = time.monotonic()
    sentinella.guarda("E:\\a.mp3")
    sentinella.guarda("E:\\b.mp3")
    assert time.monotonic() - inizio < 1 and arrivati == []
    sblocca.set()
    assert finito.wait(5) and arrivati == [("E:", PRIMO, False)]


# Il conto delle voci per la conferma di Riconosci questo disco (1.112.0).


def test_il_conto_delle_voci_di_una_lettera(disco_finto):
    # Le voci della lettera senza doppioni, come le conta la riga della
    # pulizia, e quante sul disco di adesso non ci sono; le altre lettere, le
    # condivisioni e i percorsi relativi non contano, e ogni cartella si
    # legge una volta.
    presente, *spariti = _sul_disco("a.mp3", "b.mp3", "c.mp3")
    _metti(disco_finto, presente)
    percorsi = [presente, presente.upper(), *spariti, "G:\\Musica\\d.mp3", _in_rete("e.mp3"), "brano.mp3", "F:brano.mp3"]
    assert pulizia.conta_le_voci(DISCO, percorsi, risponde=lambda _r: True, identita=_chi(PRIMO)) == (PRIMO, (3, 2))
    assert sorted(disco_finto["lette"]) == sorted(set(disco_finto["lette"])) and len(disco_finto["lette"]) == 2
    # Una lettera di cui non si conosce nessuna voce: niente da leggere.
    disco_finto["lette"].clear()
    assert pulizia.conta_le_voci(DISCO, ["G:\\a.mp3"], risponde=lambda _r: True, identita=_chi(PRIMO)) == (PRIMO, (0, 0))
    assert disco_finto["lette"] == []


def test_il_conto_di_una_lettera_che_non_risponde(disco_finto):
    # La lettera non risponde, o non dice chi c'e': niente conto, e niente da riconoscere.
    percorsi = _sul_disco("a.mp3")
    assert pulizia.conta_le_voci(DISCO, percorsi, risponde=lambda _r: False, identita=_chi(PRIMO)) == ("", None)
    assert pulizia.conta_le_voci(DISCO, percorsi, risponde=lambda _r: True, identita=_chi("")) == ("", None)

    def guasta(_radice):
        raise OSError(21, "Il dispositivo non e' pronto")

    assert pulizia.conta_le_voci(DISCO, percorsi, risponde=lambda _r: True, identita=guasta) == ("", None)
    assert disco_finto["lette"] == []


def test_il_conto_che_non_si_puo_fare(disco_finto, monkeypatch):
    # Chi risponde si sa, ma il conto no: la domanda lo dira' senza numeri.
    percorsi = _sul_disco("a.mp3", "b.mp3")
    # Il disco cambia mentre si conta: la domanda parla di quello che
    # risponde alla fine, e non di quello che se n'e' andato.
    assert pulizia.conta_le_voci(DISCO, percorsi, risponde=lambda _r: True, identita=_chi(PRIMO, SECONDO)) == (SECONDO, None)
    assert pulizia.conta_le_voci(DISCO, percorsi, risponde=lambda _r: True, identita=_chi(PRIMO, "")) == ("", None)
    # La lettera smette di rispondere: niente da riconoscere, come se non
    # avesse mai risposto.
    risposte = [True, False]
    assert pulizia.conta_le_voci(DISCO, percorsi, risponde=lambda _r: risposte.pop(0), identita=_chi(PRIMO)) == ("", None)
    # Chi aspetta ha fermato il conto: niente si legge.
    disco_finto["lette"].clear()
    assert pulizia.conta_le_voci(DISCO, percorsi, fermo=lambda: True, risponde=lambda _r: True, identita=_chi(PRIMO)) == (PRIMO, None)
    assert disco_finto["lette"] == []
    # In rete, con il giro sorvegliato: una condivisione ferma non si conta.
    monkeypatch.setattr(ricerca, "in_rete", lambda _percorso: True)

    def ferma(radice, *_altro):
        raise ricerca.NonRisponde(radice.nome)

    monkeypatch.setattr(pulizia, "_giro_sorvegliato", ferma)
    assert pulizia.conta_le_voci(DISCO, percorsi, risponde=lambda _r: True, identita=_chi("\\\\iliadbox\\disco")) == ("\\\\iliadbox\\disco", None)
    # Ferma, e intanto la lettera porta a un'altra condivisione, o la rete e' caduta.
    assert pulizia.conta_le_voci(DISCO, percorsi, risponde=lambda _r: True, identita=_chi("\\\\iliadbox\\disco", "\\\\nas\\musica")) == (
        "\\\\nas\\musica", None)
    risposte = [True, False]
    assert pulizia.conta_le_voci(DISCO, percorsi, risponde=lambda _r: risposte.pop(0), identita=_chi("\\\\iliadbox\\disco")) == ("", None)


def test_il_conto_si_chiede_in_disparte(monkeypatch):
    # La risposta arriva nel filo del conto, con la lettera e le copie date.
    chiesti = []

    def conta(radice, percorsi, **opzioni):
        chiesti.append((radice, percorsi, opzioni["fermo"](), opzioni["cedi"]))
        return SECONDO, (5, 1)

    monkeypatch.setattr(pulizia, "conta_le_voci", conta)
    arrivati, finito, cedi = [], threading.Event(), threading.Event()
    pulizia.chiedi_il_conto("E:", {"E:\\a.mp3"}, lambda chi, conto: (arrivati.append((chi, conto, threading.current_thread() is threading.main_thread())),
        finito.set()), fermo=lambda: False, cedi=cedi)
    assert finito.wait(5) and arrivati == [(SECONDO, (5, 1), False)] and chiesti == [("E:", {"E:\\a.mp3"}, False, cedi)]

    # Un conto guasto risponde lo stesso, come una lettera che non risponde,
    # e il guasto va avanti, dove vanno quelli degli altri fili.
    def guasto(*_altro, **_opzioni):
        raise RuntimeError("guasto finto")

    monkeypatch.setattr(pulizia, "conta_le_voci", guasto)
    monkeypatch.setattr(pulizia, "_in_disparte", lambda lavoro, _nome: lavoro())
    arrivati.clear()
    with pytest.raises(RuntimeError, match="guasto finto"):
        pulizia.chiedi_il_conto("E:", set(), lambda chi, conto: arrivati.append((chi, conto)))
    assert arrivati == [("", None)]


def test_la_pulizia_porta_i_dischi_a_controlla(monkeypatch):
    dati = []

    def controlla(percorsi, **opzioni):
        dati.append((opzioni["dischi"], opzioni["dischi_ignoti"]))
        return {"mancanti": set(), "saltate": {}, "contese": {}, "non_riconosciute": {}, "dischi": {}, "nomi_veri": {}, "controllati": 0}

    monkeypatch.setattr(pulizia, "controlla", controlla)
    dischi = {DISCO: {"disco": PRIMO}}
    pulizia.Pulizia(["F:\\a.mp3"], lambda _esito: None, dischi=dischi).avvia().aspetta(5)
    pulizia.Pulizia(["F:\\a.mp3"], lambda _esito: None, dischi_ignoti=True).avvia().aspetta(5)
    assert dati == [(dischi, False), ({}, True)]
