# MeTeOra, le prove della ricerca in rete (1.73.0): letture a tempo, cartelle e radici saltate, ordine.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import os
import threading
import time

import pytest

import questo_pc
import ricerca
from filtro import Filtro


class _SchedarioVuoto:
    def scheda(self, _percorso):
        return None


RETE = "\\\\finto\\condivisione"


def _sotto(*nomi):
    return os.path.join(RETE, *nomi)


@pytest.fixture
def contenuto_finto(monkeypatch):
    """Sostituisce la lettura delle cartelle che cominciano con RETE con
    stato["lettura"](cartella, rilascio, al_passo), scelta dalla prova; le
    altre si leggono dal disco. Alla fine libera i fili rimasti in attesa."""
    vero = questo_pc.contenuto
    stato = {"lettura": None, "fili": []}
    rilascio = threading.Event()

    def contenuto(cartella, al_passo=None):
        if not cartella.startswith(RETE):
            return vero(cartella, al_passo=al_passo)
        stato["fili"].append(threading.current_thread())
        return stato["lettura"](cartella, rilascio, al_passo)

    monkeypatch.setattr(questo_pc, "contenuto", contenuto)
    yield stato
    rilascio.set()


def _tace(_cartella, rilascio, _al_passo):
    rilascio.wait(30)
    return [], []


def _cerca(tmp_path, monkeypatch, attesa=0.3):
    (tmp_path / "rock locale.mp3").write_bytes(b"")
    monkeypatch.setattr(ricerca, "ATTESA_IN_RETE", attesa)
    lavoro = ricerca.Ricerca(Filtro("rock"), [], _SchedarioVuoto(), unita=[str(tmp_path)], rete=[RETE])
    lavoro.avvia()
    return lavoro


def _nomi(lavoro):
    return [os.path.basename(b.percorso) for b in lavoro.risultati]


def test_la_rete_viene_dopo_i_dischi(tmp_path, contenuto_finto, monkeypatch):
    contenuto_finto["lettura"] = lambda cartella, _rilascio, _al_passo: ([], [os.path.join(cartella, "rock in rete.mp3")])
    lavoro = _cerca(tmp_path, monkeypatch)
    lavoro.aspetta(10)
    assert lavoro.finita and lavoro.senza_risposta == [] and lavoro.cartelle_mute == []
    assert _nomi(lavoro) == ["rock locale.mp3", "rock in rete.mp3"]


def test_la_radice_che_tace_si_salta(tmp_path, contenuto_finto, monkeypatch):
    contenuto_finto["lettura"] = _tace
    inizio = time.monotonic()
    lavoro = _cerca(tmp_path, monkeypatch)
    lavoro.aspetta(10)
    assert lavoro.finita and lavoro.senza_risposta == [RETE]
    assert _nomi(lavoro) == ["rock locale.mp3"]
    assert time.monotonic() - inizio < 5


def test_una_cartella_muta_non_ferma_la_radice(tmp_path, contenuto_finto, monkeypatch):
    # La cartella dei backup tace, quella dei video dopo di lei risponde: il
    # film si trova lo stesso, e la console dira' una cartella saltata.
    def lettura(cartella, rilascio, al_passo):
        if cartella == RETE:
            return [_sotto("Backup"), _sotto("Video")], []
        if cartella == _sotto("Backup"):
            return _tace(cartella, rilascio, al_passo)
        return [], [_sotto("Video", "rock film.mkv")]

    contenuto_finto["lettura"] = lettura
    lavoro = _cerca(tmp_path, monkeypatch)
    lavoro.aspetta(10)
    assert lavoro.finita and lavoro.senza_risposta == [] and lavoro.cartelle_mute == [_sotto("Backup")]
    assert _nomi(lavoro) == ["rock locale.mp3", "rock film.mkv"]


def test_tre_cartelle_mute_fermano_la_radice(tmp_path, contenuto_finto, monkeypatch):
    def lettura(cartella, rilascio, al_passo):
        if cartella == RETE:
            return [_sotto(n) for n in ("a", "b", "c", "d")], []
        return _tace(cartella, rilascio, al_passo)

    contenuto_finto["lettura"] = lettura
    lavoro = _cerca(tmp_path, monkeypatch)
    lavoro.aspetta(10)
    # La radice si dice da sola, senza le sue cartelle; la quarta non si legge.
    assert lavoro.finita and lavoro.senza_risposta == [RETE] and lavoro.cartelle_mute == []
    assert len(contenuto_finto["fili"]) == 4


def test_una_cartella_lenta_ma_viva_non_scade(tmp_path, contenuto_finto, monkeypatch):
    # Una voce ogni 0.1 secondi per un secondo, con l'attesa a 0.3: arriva
    # sempre qualcosa, quindi la cartella si legge tutta.
    def lettura(cartella, _rilascio, al_passo):
        for _ in range(10):
            time.sleep(0.1)
            al_passo()
        return [], [os.path.join(cartella, "rock lento.mp3")]

    contenuto_finto["lettura"] = lettura
    lavoro = _cerca(tmp_path, monkeypatch)
    lavoro.aspetta(10)
    assert lavoro.finita and lavoro.senza_risposta == [] and _nomi(lavoro) == ["rock locale.mp3", "rock lento.mp3"]


def test_la_radice_che_risponde_con_un_errore_si_dice(tmp_path, contenuto_finto, monkeypatch):
    def lettura(_cartella, _rilascio, _al_passo):
        raise OSError(53, "Impossibile trovare il percorso di rete")

    contenuto_finto["lettura"] = lettura
    lavoro = _cerca(tmp_path, monkeypatch)
    lavoro.aspetta(10)
    assert lavoro.finita and lavoro.senza_risposta == [RETE]


def test_la_lettura_appesa_si_annulla_davvero(tmp_path, contenuto_finto, monkeypatch):
    # Una lettura vera e bloccata, su una pipe senza scrittore: CancelSynchronousIo
    # la interrompe, e il filo che la faceva finisce invece di restare appeso.
    lettura, scrittura = os.pipe()

    def legge(_cartella, _rilascio, _al_passo):
        os.read(lettura, 1)
        return [], []

    contenuto_finto["lettura"] = legge
    try:
        lavoro = _cerca(tmp_path, monkeypatch)
        lavoro.aspetta(10)
        assert lavoro.senza_risposta == [RETE]
        filo = contenuto_finto["fili"][0]
        filo.join(3)
        assert not filo.is_alive()
    finally:
        os.close(scrittura)
        os.close(lettura)


def test_ferma_vale_subito_e_annulla_la_lettura(tmp_path, contenuto_finto, monkeypatch):
    lettura, scrittura = os.pipe()

    def legge(_cartella, _rilascio, _al_passo):
        os.read(lettura, 1)
        return [], []

    contenuto_finto["lettura"] = legge
    try:
        lavoro = _cerca(tmp_path, monkeypatch, attesa=30)
        for _ in range(100):
            if contenuto_finto["fili"]:
                break
            time.sleep(0.02)
        inizio = time.monotonic()
        lavoro.ferma()
        assert lavoro.fermata and time.monotonic() - inizio < 2
        assert not lavoro.finita and lavoro.senza_risposta == []
        filo = contenuto_finto["fili"][0]
        filo.join(3)
        assert not filo.is_alive()
    finally:
        os.close(scrittura)
        os.close(lettura)


def test_senza_annidati():
    radici = ["\\\\s\\a", "\\\\S\\A\\", "\\\\s\\a\\dentro", "\\\\s\\ab", "\\\\altro\\x"]
    assert ricerca.senza_annidati(radici) == ["\\\\s\\a", "\\\\s\\ab", "\\\\altro\\x"]


def test_radici_di_rete_con_le_lettere(monkeypatch):
    # Z: porta alla condivisione \\s\a: il percorso aggiunto a mano dentro di
    # lei si cerca una volta sola, con la lettera; gli altri restano.
    monkeypatch.setattr(ricerca, "lettere_di_rete", lambda: ["Z:\\"])
    vero = ricerca._percorso_di_rete
    monkeypatch.setattr(ricerca, "_percorso_di_rete", lambda r: "\\\\s\\a\\" if r == "Z:\\" else vero(r))
    assert ricerca.radici_di_rete(["\\\\s\\a\\Video", "\\\\t\\x"]) == ["\\\\t\\x", "Z:\\"]


def test_il_contatore_in_rete_non_si_pianta(contenuto_finto, monkeypatch):
    # 1.77.1: una sottocartella che tace non ferma il contatore; la radice
    # finisce fra le mute, il conto e' parziale, e le letture dopo nella
    # stessa radice non si tentano piu' fino ad Aggiorna.
    import contatore as modulo_contatore

    monkeypatch.setattr(ricerca, "ATTESA_IN_RETE", 0.3)
    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith(RETE))

    def lettura(cartella, rilascio, al_passo):
        if cartella == RETE:
            return [_sotto("A"), _sotto("B")], []
        if cartella == _sotto("A"):
            return [], [_sotto("A", "uno.mp3")]
        return _tace(cartella, rilascio, al_passo)

    contenuto_finto["lettura"] = lettura
    conta = modulo_contatore.Contatore()
    inizio = time.monotonic()
    conta.chiedi([RETE])
    conta.aspetta(10)
    assert time.monotonic() - inizio < 5
    assert conta.files(RETE) == [_sotto("A", "uno.mp3")] and RETE in conta.parziali
    assert os.path.splitdrive(RETE)[0].lower() in conta.mute
    letture = len(contenuto_finto["fili"])
    conta.chiedi([_sotto("B")])
    conta.aspetta(10)
    assert len(contenuto_finto["fili"]) == letture and conta.files(_sotto("B")) == [] and _sotto("B") in conta.parziali
    conta.dimentica_tutto()
    assert not conta.mute and not conta.parziali
