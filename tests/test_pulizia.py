# MeTeOra, le prove della pulizia all'avvio: file presenti e spariti, cartelle che non si leggono, maiuscole vere, radici saltate, sorveglianza della rete.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 19/10/2026: nasce con la 1.104.0.

"""Sul disco si guardano file veri in una cartella temporanea, presa con le
maiuscole che ha davvero, e una giunzione vera verso una lettera che non
c'e'; la rete e' una condivisione finta, con le letture sostituite, e la
rete vera non si tocca."""

import ctypes
import ntpath
import os
import string
import struct
import threading
import time
import types
from ctypes import wintypes
from pathlib import Path

import pytest

import pulizia
import ricerca

RETE = "\\\\finto\\condivisione"


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
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 2}


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
    assert esito == {"mancanti": set(), "saltate": {}, "nomi_veri": {}, "controllati": 0}


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
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 3}
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
    assert esito == {"mancanti": set(), "saltate": {}, "nomi_veri": {}, "controllati": 0}


def test_la_radice_che_non_risponde(cartella):
    presente = _file(cartella / "presente.mp3")
    sparito = cartella / "sparito.mp3"
    lontani = ["Q:\\Musica\\uno.mp3", "q:\\musica\\due.mp3", "q:\\musica\\UNO.mp3"]
    provate = []

    def risponde(radice):
        provate.append(radice)
        return radice != "Q:"

    esito = pulizia.controlla([*lontani, str(presente), str(sparito)], risponde=risponde)
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {"Q:": 2}, "nomi_veri": {}, "controllati": 2}
    # Ogni radice si prova una volta, e quella che risponde anche alla fine del giro.
    assert provate == ["Q:", _radice(cartella), _radice(cartella)]


def test_la_radice_che_smette_di_rispondere(cartella):
    resta = _file(cartella / "resta.mp3")
    risposte = iter([True, False])
    esito = pulizia.controlla([str(resta), str(cartella / "sparito.mp3")], risponde=lambda _r: next(risposte))
    assert esito == {"mancanti": set(), "saltate": {_radice(cartella): 2}, "nomi_veri": {}, "controllati": 0}


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
    assert esito == {"mancanti": set(), "saltate": {_radice(cartella): 2, "Q:": 1}, "nomi_veri": {}, "controllati": 0}


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
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 1}


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
    assert esito == {"mancanti": {pulizia.norm(p) for p in spariti}, "saltate": {}, "nomi_veri": {}, "controllati": 2}


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
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 2}


def test_i_percorsi_non_assoluti_restano_senza_controllo(cartella, monkeypatch):
    # Con la cartella di lavoro dove i file non ci sono, i percorsi relativi
    # sembrerebbero spariti: restano senza controllo, ne' mancanti ne' saltati.
    monkeypatch.chdir(cartella)
    relativi = ["brano.mp3", "Musica\\brano.mp3", "..\\brano.mp3", "\\brano.mp3", "/brano.mp3", _radice(cartella) + "brano.mp3", Path("brano.mp3")]
    esito = pulizia.controlla(relativi, risponde=lambda _r: pytest.fail("nessuna radice da provare"))
    assert esito == {"mancanti": set(), "saltate": {}, "nomi_veri": {}, "controllati": 0}
    sparito = cartella / "sparito.mp3"
    esito = pulizia.controlla([*relativi, str(sparito)])
    assert esito == {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 1}


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
    assert esito == {"mancanti": set(), "saltate": {}, "nomi_veri": {}, "controllati": 0}


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
    assert esito == {"mancanti": set(), "saltate": {RETE: 2}, "nomi_veri": {}, "controllati": 0}
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
    assert esito == {"mancanti": set(), "saltate": {RETE: 2}, "nomi_veri": {}, "controllati": 0}


def test_pulizia_finita(cartella):
    resta = _file(cartella / "resta.mp3")
    sparito = cartella / "sparito.mp3"
    arrivati = []
    lavoro = pulizia.Pulizia(iter([str(resta), str(sparito)]), lambda esito: arrivati.append((threading.current_thread().name, esito)))
    assert lavoro.avvia() is lavoro
    lavoro.aspetta(10)
    assert arrivati == [("MeTeOra, pulizia", {"mancanti": {pulizia.norm(sparito)}, "saltate": {}, "nomi_veri": {}, "controllati": 2})]


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
