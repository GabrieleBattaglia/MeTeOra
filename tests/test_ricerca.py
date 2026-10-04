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
    # 1.77.1: una sottocartella che tace non ferma il contatore, e il conto e'
    # parziale. 1.85.5: la cartella muta non si rilegge, ma la radice resta
    # viva, e le altre cartelle si contano (collaudo della 1.85.2).
    import contatore as modulo_contatore

    monkeypatch.setattr(ricerca, "ATTESA_IN_RETE", 0.3)
    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith(RETE))

    def lettura(cartella, rilascio, al_passo):
        if cartella == RETE:
            return [_sotto("A"), _sotto("B")], []
        if cartella == _sotto("A"):
            return [], [_sotto("A", "uno.mp3")]
        if cartella == _sotto("C"):
            return [], [_sotto("C", "due.mp3")]
        return _tace(cartella, rilascio, al_passo)

    contenuto_finto["lettura"] = lettura
    conta = modulo_contatore.Contatore()
    inizio = time.monotonic()
    conta.chiedi([RETE])
    conta.aspetta(10)
    assert time.monotonic() - inizio < 5
    assert conta.files(RETE) == [_sotto("A", "uno.mp3")] and RETE in conta.parziali
    assert not conta.mute and conta.cartelle_mute == {_sotto("B").lower()}
    letture = len(contenuto_finto["fili"])
    conta.chiedi([_sotto("B"), _sotto("C")])
    conta.aspetta(10)
    # B non si rilegge, C si'.
    assert len(contenuto_finto["fili"]) == letture + 1 and conta.files(_sotto("B")) == [] and _sotto("B") in conta.parziali
    assert conta.files(_sotto("C")) == [_sotto("C", "due.mp3")] and _sotto("C") not in conta.parziali
    conta.dimentica_tutto()
    assert not conta.mute and not conta.parziali and not conta.cartelle_mute


def test_tre_cartelle_mute_lasciano_la_radice_finche_la_plancia_la_ritrova(contenuto_finto, monkeypatch):
    # 1.85.5: alla terza cartella muta il contatore lascia perdere la radice,
    # come la ricerca; una lettura riuscita della plancia la fa tornare viva, e
    # i conti parziali di quella radice si rifanno.
    import contatore as modulo_contatore

    monkeypatch.setattr(ricerca, "ATTESA_IN_RETE", 0.2)
    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith(RETE))
    vive = set()

    def lettura(cartella, rilascio, al_passo):
        if cartella == RETE:
            return [_sotto(n) for n in ("M1", "M2", "M3", "Video")], []
        if cartella in vive or cartella == _sotto("Video"):
            return [], [os.path.join(cartella, "film.mkv")]
        return _tace(cartella, rilascio, al_passo)

    contenuto_finto["lettura"] = lettura
    conta = modulo_contatore.Contatore()
    conta.chiedi([_sotto("M1"), _sotto("M2"), _sotto("M3")])
    conta.aspetta(10)
    radice = os.path.splitdrive(RETE)[0].lower()
    assert radice in conta.mute and len(conta.cartelle_mute) == 3
    # Con la radice lasciata perdere, nemmeno Video si legge: il conto e' parziale.
    letture = len(contenuto_finto["fili"])
    conta.chiedi([_sotto("Video")])
    conta.aspetta(10)
    assert len(contenuto_finto["fili"]) == letture and conta.files(_sotto("Video")) == [] and _sotto("Video") in conta.parziali
    # La plancia legge Video: la radice torna viva, e Video si riconta.
    da_rifare = conta.risponde(_sotto("Video"))
    assert radice not in conta.mute and _sotto("Video") in da_rifare and _sotto("Video") not in conta.parziali
    conta.chiedi(da_rifare)
    conta.aspetta(10)
    assert conta.files(_sotto("Video")) == [_sotto("Video", "film.mkv")] and _sotto("Video") not in conta.parziali
    # Le cartelle mute restano tali finche' non si leggono: M1, letta dalla
    # plancia, esce dalle mute, e si rifanno il suo conto e quello di chi la
    # contiene, che l'aveva saltata; le altre due restano mute.
    conta.conti[RETE] = [_sotto("Video", "film.mkv")]
    conta.parziali.add(RETE)
    vive.add(_sotto("M1"))
    da_rifare = conta.risponde(_sotto("M1"))
    assert da_rifare == sorted([RETE, _sotto("M1")]) and conta.cartelle_mute == {_sotto("M2").lower(), _sotto("M3").lower()}
    conta.chiedi(da_rifare)
    conta.aspetta(10)
    assert conta.files(_sotto("M1")) == [_sotto("M1", "film.mkv")] and _sotto("M1") not in conta.parziali
    assert RETE in conta.parziali and _sotto("M1", "film.mkv") in conta.files(RETE)
    # Una cartella che non era muta, in una radice viva, non rifa' niente.
    assert conta.risponde(_sotto("Video")) == []
    # Aggiorna su una di loro la fa riprovare; se la radice era stata lasciata
    # perdere di nuovo, torna viva, con le mute da contare da capo.
    for nome in ("N1", "N2", "N3"):
        conta.non_risponde(_sotto(nome))
    assert radice in conta.mute
    conta.dimentica(_sotto("M2"))
    assert _sotto("M2").lower() not in conta.cartelle_mute and _sotto("M3").lower() in conta.cartelle_mute
    assert radice not in conta.mute and radice not in conta._mute_per_radice
    conta.non_risponde(_sotto("N4"))
    assert radice not in conta.mute
    # Una cartella che torna viva non conta piu' fra le mute della radice.
    conta.risponde(_sotto("N4"))
    for nome in ("N5", "N6"):
        conta.non_risponde(_sotto(nome))
    assert radice not in conta.mute


def _cancello(arrivata, via, al_passo):
    """Una lettura che si ferma finche' la prova non la lascia andare,
    tenendo viva l'attesa della lettura protetta."""
    arrivata.set()
    while not via.wait(0.05):
        if al_passo:
            al_passo()


def test_una_cartella_che_torna_viva_rifa_il_conto_in_corso(contenuto_finto, monkeypatch):
    # Revisione della 1.85.5: la plancia legge una cartella muta mentre il
    # conto di chi la contiene e' ancora in corso; quel conto si rifa', invece
    # di restare parziale fino ad Aggiorna.
    import contatore as modulo_contatore

    monkeypatch.setattr(ricerca, "ATTESA_IN_RETE", 0.2)
    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith(RETE))
    arrivata, via = threading.Event(), threading.Event()
    vive = set()

    def lettura(cartella, rilascio, al_passo):
        if cartella == _sotto("Video"):
            return [_sotto("Video", "Sub"), _sotto("Video", "Gate")], []
        if cartella == _sotto("Video", "Gate"):
            _cancello(arrivata, via, al_passo)
            return [], [_sotto("Video", "Gate", "g.mkv")]
        if cartella in vive:
            return [], [os.path.join(cartella, "s.mkv")]
        return _tace(cartella, rilascio, al_passo)

    contenuto_finto["lettura"] = lettura
    conta = modulo_contatore.Contatore()
    conta.chiedi([_sotto("Video")])
    assert arrivata.wait(10)
    assert _sotto("Video", "Sub").lower() in conta.cartelle_mute
    vive.add(_sotto("Video", "Sub"))
    assert conta.risponde(_sotto("Video", "Sub")) == []
    via.set()
    conta.aspetta(10)
    assert sorted(conta.files(_sotto("Video"))) == [_sotto("Video", "Gate", "g.mkv"), _sotto("Video", "Sub", "s.mkv")]
    assert _sotto("Video") not in conta.parziali


def test_una_radice_che_torna_viva_rifa_il_conto_in_corso(contenuto_finto, monkeypatch):
    # Revisione della 1.85.5: la radice viene lasciata perdere a meta' di un
    # conto, che salta Saltata; la plancia la ritrova viva prima che il conto
    # finisca: il conto si rifa', e Saltata si legge.
    import contatore as modulo_contatore

    monkeypatch.setattr(ricerca, "ATTESA_IN_RETE", 0.2)
    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith(RETE))
    arrivata, via = threading.Event(), threading.Event()
    figli = [_sotto("Video", n) for n in ("M1", "M2", "M3", "Saltata", "Gate")]

    def lettura(cartella, rilascio, al_passo):
        if cartella == _sotto("Video"):
            return figli, []
        if cartella in figli[3:]:
            return [], [os.path.join(cartella, "f.mkv")]
        return _tace(cartella, rilascio, al_passo)

    contenuto_finto["lettura"] = lettura
    conta = modulo_contatore.Contatore()
    vera = conta._lettura

    def lettura_con_cancello(cartella):
        if cartella == figli[4]:
            _cancello(arrivata, via, None)
        return vera(cartella)

    conta._lettura = lettura_con_cancello
    conta.chiedi([_sotto("Video")])
    assert arrivata.wait(10)
    radice = os.path.splitdrive(RETE)[0].lower()
    assert radice in conta.mute
    assert conta.risponde(_sotto("Video")) == []
    via.set()
    conta.aspetta(10)
    assert sorted(conta.files(_sotto("Video"))) == sorted([os.path.join(figli[3], "f.mkv"), os.path.join(figli[4], "f.mkv")])
    # M1, M2 e M3 restano mute: il conto resta parziale, ma senza buchi in piu'.
    assert _sotto("Video") in conta.parziali and radice not in conta.mute


def test_un_errore_di_rete_immediato_non_vale_come_cartella_vuota(contenuto_finto, monkeypatch):
    # Revisione della 1.85.5: la rete che manca subito, come il router che si
    # riavvia (errore 53), non si tiene come cartella vuota: il conto e'
    # parziale, la cartella e' muta, e quando la plancia la rilegge si riconta.
    import contatore as modulo_contatore

    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith(RETE))
    spenta = [True]

    def lettura(cartella, rilascio, al_passo):
        if cartella == _sotto("Video") and spenta[0]:
            raise OSError(None, "Impossibile trovare il percorso di rete", None, 53)
        return [], [os.path.join(cartella, "film.mkv")]

    contenuto_finto["lettura"] = lettura
    conta = modulo_contatore.Contatore()
    conta.chiedi([_sotto("Video")])
    conta.aspetta(10)
    assert conta.files(_sotto("Video")) == [] and _sotto("Video") in conta.parziali
    assert _sotto("Video").lower() in conta.cartelle_mute and _sotto("Video") not in conta._letture
    spenta[0] = False
    da_rifare = conta.risponde(_sotto("Video"))
    assert da_rifare == [_sotto("Video")]
    conta.chiedi(da_rifare)
    conta.aspetta(10)
    assert conta.files(_sotto("Video")) == [_sotto("Video", "film.mkv")] and _sotto("Video") not in conta.parziali
    # Un errore della cartella, come l'accesso negato (5), resta una cartella vuota.
    def negata(cartella, rilascio, al_passo):
        raise OSError(None, "Accesso negato", None, 5)

    contenuto_finto["lettura"] = negata
    conta.chiedi([_sotto("Chiusa")])
    conta.aspetta(10)
    assert conta.files(_sotto("Chiusa")) == [] and _sotto("Chiusa") not in conta.parziali
    assert ricerca.errore_di_rete(OSError(None, "x", None, 1231)) and not ricerca.errore_di_rete(OSError(None, "x", None, 1117))


def test_la_lettura_della_plancia_vince_sull_attesa_del_contatore(contenuto_finto, monkeypatch):
    # Revisione della 1.85.5: mentre il contatore aspetta una cartella, la
    # plancia la legge; quando l'attesa scade, vale la lettura della plancia, e
    # la cartella non diventa muta.
    import contatore as modulo_contatore

    monkeypatch.setattr(ricerca, "ATTESA_IN_RETE", 0.5)
    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith(RETE))
    partita = threading.Event()

    def lettura(cartella, rilascio, al_passo):
        partita.set()
        return _tace(cartella, rilascio, al_passo)

    contenuto_finto["lettura"] = lettura
    conta = modulo_contatore.Contatore()
    conta.chiedi([_sotto("Lenta")])
    assert partita.wait(10)
    assert conta.rinfresca(_sotto("Lenta"), ([], [_sotto("Lenta", "a.mp3")])) == []
    conta.aspetta(10)
    assert conta.files(_sotto("Lenta")) == [_sotto("Lenta", "a.mp3")] and _sotto("Lenta") not in conta.parziali
    assert not conta.cartelle_mute


def test_aggiorna_su_un_computer_della_rete_ravviva_le_sue_condivisioni(monkeypatch):
    # Revisione della 1.85.5: Aggiorna su \\\\finto, il computer, toglie le
    # mute delle sue condivisioni, con la radice lasciata perdere.
    import contatore as modulo_contatore

    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith(RETE))
    conta = modulo_contatore.Contatore()
    for nome in ("M1", "M2", "M3"):
        conta.non_risponde(_sotto(nome))
    radice = os.path.splitdrive(RETE)[0].lower()
    conta.conti[_sotto("Video")] = []
    conta.parziali.add(_sotto("Video"))
    assert radice in conta.mute
    # I conti di tutto cio' che il computer contiene si dimenticano gia'.
    assert conta.dimentica("\\\\finto") == [] and _sotto("Video") not in conta.conti and not conta.parziali
    assert radice not in conta.mute and not conta.cartelle_mute and not conta._mute_per_radice.get(radice)
    conta.non_risponde(_sotto("M4"))
    assert radice not in conta.mute


def test_aggiorna_su_questo_pc_rifa_il_conto_in_corso(contenuto_finto, monkeypatch):
    # Revisione della 1.85.5: un conto in corso quando Aggiorna dimentica
    # tutto si rifa', invece di salvare quello di prima.
    import contatore as modulo_contatore

    monkeypatch.setattr(ricerca, "ATTESA_IN_RETE", 0.2)
    monkeypatch.setattr(modulo_contatore, "in_rete", lambda percorso: percorso.startswith(RETE))
    arrivata, via = threading.Event(), threading.Event()
    vive = set()

    def lettura(cartella, rilascio, al_passo):
        if cartella == _sotto("Video"):
            return [_sotto("Video", "Sub"), _sotto("Video", "Gate")], []
        if cartella == _sotto("Video", "Gate"):
            _cancello(arrivata, via, al_passo)
            return [], [_sotto("Video", "Gate", "g.mkv")]
        if cartella in vive:
            return [], [os.path.join(cartella, "s.mkv")]
        return _tace(cartella, rilascio, al_passo)

    contenuto_finto["lettura"] = lettura
    conta = modulo_contatore.Contatore()
    conta.chiedi([_sotto("Video")])
    assert arrivata.wait(10)
    vive.add(_sotto("Video", "Sub"))
    conta.dimentica_tutto()
    via.set()
    conta.aspetta(10)
    assert sorted(conta.files(_sotto("Video"))) == [_sotto("Video", "Gate", "g.mkv"), _sotto("Video", "Sub", "s.mkv")]
    assert _sotto("Video") not in conta.parziali
