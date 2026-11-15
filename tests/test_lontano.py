# MeTeOra, le prove del lettore lontano: uno speaker Cast al posto della scheda audio.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/11/2026: nasce con lontano.py, nella 1.117.0. Nella 3.11.1 la radio allo speaker dal ripetitore. Nella 3.11.6 i fotogrammi interi allo speaker. Nella 3.12.0 le TV convertite.

"""Le prove di lontano.py, con un apparecchio, un server e una sorgente del
WAV in RAM finti: niente rete e niente libmpv. Gli stati dell'apparecchio si mandano
a mano, come li manderebbe pychromecast dal suo filo."""

import os
import threading
import time

import pytest

import lontano
import trasmissione


class _ApparecchioFinto:
    nome = "Cucina"

    def __init__(self):
        self.chiamate = []
        self.posizione = None
        self.volume = 0.4
        self.muto = False
        self.guasto = None

    def _annota(self, *voce):
        if self.guasto is not None:
            raise self.guasto
        self.chiamate.append(voce)

    def suona(self, indirizzo, tipo, titolo=None, inizio=None, in_pausa=False, in_diretta=False):
        self.in_diretta = in_diretta
        self._annota("suona", indirizzo, tipo, titolo, inizio, in_pausa)

    def pausa(self):
        self._annota("pausa")

    def riprendi(self):
        self._annota("riprendi")

    def ferma(self):
        self._annota("ferma")

    def vai_a(self, secondi):
        self._annota("vai_a", secondi)

    def chiudi(self, lascia_l_app=False):
        self.chiamate.append(("chiudi", lascia_l_app))


class _SorgenteFinta:
    tipo = "audio/wav"

    def __init__(self, percorso, sottobrano):
        self.percorso, self.sottobrano = percorso, sottobrano
        self.chiusa = False

    def chiudi(self):
        self.chiusa = True


class _ServerFinto:
    def __init__(self):
        self.pubblicati = []
        self.sorgenti = []
        self.ritirate = []
        self.flussi = []
        self.fermato = False

    def pubblica_file(self, percorso):
        self.pubblicati.append(percorso)
        return f"http://pc/file/{len(self.pubblicati)}{os.path.splitext(percorso)[1].lower()}"

    def pubblica_sorgente(self, sorgente):
        self.sorgenti.append(sorgente)
        return f"http://pc/sorgente/{len(self.sorgenti)}.wav"

    def ritira_sorgente(self, sorgente):
        self.ritirate.append(sorgente)

    def pubblica_flusso(self, nome, scrivi, tipo):
        self.flussi.append((nome, scrivi, tipo))
        return f"http://pc/flusso/{nome}"

    def ferma(self):
        self.fermato = True


class _ApparecchioLento(_ApparecchioFinto):
    """Lo speaker che risponde a un salto solo quando la prova lo lascia
    andare, come pychromecast, che aspetta la sua risposta fino a 10 secondi;
    intanto dice ancora la posizione di prima. errore_del_salto, se c'e', e'
    quello che il salto solleva alla fine."""

    def __init__(self):
        super().__init__()
        self.via = threading.Event()
        self.errore_del_salto = None

    def vai_a(self, secondi):
        self._annota("vai_a", secondi)
        assert self.via.wait(5)
        if self.errore_del_salto is not None:
            raise self.errore_del_salto


def _aspetta(condizione, secondi=5):
    fine = time.monotonic() + secondi
    while time.monotonic() < fine:
        if condizione():
            return True
        time.sleep(0.01)
    return condizione()


class _Banco:
    """Il lettore lontano con i suoi finti, e gli avvisi in una lista."""

    def __init__(self, tmp_path, converti=None, apparecchio=None):
        self.apparecchio = apparecchio or _ApparecchioFinto()
        self.server = _ServerFinto()
        self.avvisi = []
        self.conversioni = []
        self.allo_stato = self.al_distacco = None

        def connetti(allo_stato, al_distacco):
            self.allo_stato, self.al_distacco = allo_stato, al_distacco
            return self.apparecchio

        def converti_finto(percorso, sottobrano):
            self.conversioni.append((percorso, sottobrano))
            return _SorgenteFinta(percorso, sottobrano)

        self.lettore = lontano.LettoreLontano(connetti, self.server, converti or converti_finto,
            alla_fine=lambda: self.avvisi.append("fine"), all_errore=lambda p: self.avvisi.append(("errore", p)),
            al_caricamento=lambda: self.avvisi.append("caricato"),
            all_interruzione=lambda: self.avvisi.append("interruzione"), al_guasto=lambda e: self.avvisi.append(("guasto", str(e))))

    def stato(self, stato, indirizzo=None, durata=None, motivo=None):
        self.allo_stato({"stato": stato, "posizione": None, "durata": durata, "motivo": motivo, "indirizzo": indirizzo})

    def aspetta_suona(self, quanti=1, secondi=5):
        fine = threading.Event()
        for _ in range(int(secondi / 0.01)):
            if sum(1 for c in self.apparecchio.chiamate if c[0] == "suona") >= quanti:
                return True
            fine.wait(0.01)
        return False


@pytest.fixture
def banco(tmp_path):
    return _Banco(tmp_path)


def test_da_convertire():
    assert not lontano.da_convertire("brano.mp3") and not lontano.da_convertire("brano.flac")
    assert lontano.da_convertire("brano.ape") and lontano.da_convertire("brano.wv")
    # I video vanno solo con l'audio, convertito; e i brani che MeTeOra rende da se'.
    assert lontano.da_convertire("film.mp4") and lontano.da_convertire("film.mkv")
    assert lontano.da_convertire("musica.sid", sottobrano=3) and lontano.da_convertire("musica.nsf", sottobrano=1)
    assert lontano.da_convertire("canzone.mid", midi_reso=True)


def test_un_brano_che_lo_speaker_legge(banco):
    lettore, apparecchio = banco.lettore, banco.apparecchio
    lettore.suona(r"C:\m\Brano.MP3", inizio=12.5)
    # Dal 15 novembre 2026 i comandi vanno allo speaker dal loro filo.
    assert lettore.aspetta_i_comandi()
    assert apparecchio.chiamate == [("suona", "http://pc/file/1.mp3", "audio/mpeg", "Brano.MP3", 12.5, False)]
    assert lettore.percorso == r"C:\m\Brano.MP3" and lettore.posizione is None and lettore.durata is None
    # Finche' lo speaker non lo ha, gli stati del brano di prima non contano.
    banco.stato(trasmissione.FERMO, motivo="INTERRUPTED")
    assert banco.avvisi == [] and lettore.percorso is not None
    banco.stato(trasmissione.IN_CARICAMENTO, "http://pc/file/1.mp3")
    banco.stato(trasmissione.IN_RIPRODUZIONE, "http://pc/file/1.mp3", durata=200.0)
    assert banco.avvisi == ["caricato"]
    apparecchio.posizione = 13.0
    assert lettore.posizione == 13.0 and lettore.durata == 200.0 and not lettore.in_pausa
    # A fine brano, alla_fine, e il lettore e' libero.
    banco.stato(trasmissione.FERMO, "http://pc/file/1.mp3", motivo="FINISHED")
    assert banco.avvisi == ["caricato", "fine"] and lettore.percorso is None


def test_la_fine_che_lo_speaker_non_dice(banco, monkeypatch):
    # GabryBar, alla fine dei FLAC convertiti, resta in caricamento
    # all'ultimo campione per 23 secondi, poi da' errore: dopo
    # ATTESA_DELLA_FINE il brano e' finito, sottobrano compreso (2.6.5).
    monkeypatch.setattr(lontano, "ATTESA_DELLA_FINE", 0.05)
    lettore = banco.lettore
    lettore.suona(r"C:\m\musica.sid", sottobrano=4, sottobrani=27)
    assert banco.aspetta_suona()
    indirizzo = banco.apparecchio.chiamate[-1][1]
    banco.stato(trasmissione.IN_RIPRODUZIONE, indirizzo, durata=97.056)
    # Un caricamento a meta' brano e' un caricamento vero: niente fine.
    banco.allo_stato({"stato": trasmissione.IN_CARICAMENTO, "posizione": 40.0, "durata": 97.056, "motivo": None, "indirizzo": indirizzo})
    threading.Event().wait(0.2)
    assert "fine" not in banco.avvisi and lettore.percorso is not None
    # All'ultimo campione, e lo speaker non dice altro.
    banco.allo_stato({"stato": trasmissione.IN_CARICAMENTO, "posizione": 97.056, "durata": 97.056, "motivo": None, "indirizzo": indirizzo})
    for _ in range(200):
        if "fine" in banco.avvisi:
            break
        threading.Event().wait(0.01)
    assert banco.avvisi.count("fine") == 1 and lettore.percorso is None and lettore.sottobrano == 4
    # L'errore che lo speaker manda 23 secondi dopo non conta piu'.
    banco.stato(trasmissione.FERMO, indirizzo, motivo="ERROR")
    assert not any(isinstance(a, tuple) and a[0] == "errore" for a in banco.avvisi)
    # Se lo speaker dice la fine da se', entro l'attesa, la fine e' una sola.
    lettore.suona("brano.mp3")
    assert lettore.aspetta_i_comandi()
    indirizzo = banco.apparecchio.chiamate[-1][1]
    banco.stato(trasmissione.IN_RIPRODUZIONE, indirizzo, durata=200.0)
    banco.allo_stato({"stato": trasmissione.IN_CARICAMENTO, "posizione": 199.9, "durata": 200.0, "motivo": None, "indirizzo": indirizzo})
    banco.stato(trasmissione.FERMO, indirizzo, motivo="FINISHED")
    threading.Event().wait(0.2)
    assert banco.avvisi.count("fine") == 2
    # E se riparte, per esempio dopo un salto indietro, la fine attesa si toglie.
    lettore.suona("altro.mp3")
    assert lettore.aspetta_i_comandi()
    indirizzo = banco.apparecchio.chiamate[-1][1]
    banco.stato(trasmissione.IN_RIPRODUZIONE, indirizzo, durata=200.0)
    banco.allo_stato({"stato": trasmissione.IN_CARICAMENTO, "posizione": 200.0, "durata": 200.0, "motivo": None, "indirizzo": indirizzo})
    banco.stato(trasmissione.IN_RIPRODUZIONE, indirizzo, durata=200.0)
    threading.Event().wait(0.2)
    assert banco.avvisi.count("fine") == 2 and lettore.percorso == "altro.mp3"


def test_i_comandi(banco):
    # Dal 15 novembre 2026 i comandi vanno allo speaker dal loro filo, in
    # fila: aspetta_i_comandi aspetta che siano arrivati.
    lettore, apparecchio = banco.lettore, banco.apparecchio
    lettore.suona("brano.flac", in_pausa=True)
    assert lettore.in_pausa and lettore.aspetta_i_comandi()
    assert apparecchio.chiamate[-1][-1] is True
    banco.stato(trasmissione.IN_PAUSA, "http://pc/file/1.flac")
    assert banco.avvisi == ["caricato"] and lettore.in_pausa
    assert lettore.pausa() is False and lettore.aspetta_i_comandi() and apparecchio.chiamate[-1] == ("riprendi",)
    assert lettore.pausa(True) is True and lettore.aspetta_i_comandi() and apparecchio.chiamate[-1] == ("pausa",)
    apparecchio.posizione = 30.0
    lettore.salta(-40)
    assert lettore.aspetta_i_comandi()
    lettore.vai_a(90)
    assert lettore.aspetta_i_comandi()
    assert apparecchio.chiamate[-2:] == [("vai_a", 0.0), ("vai_a", 90.0)]
    # Il volume da 0 a 100, quello dello speaker; quello chiesto vale per un
    # attimo, finche' lo speaker non dice il suo.
    assert lettore.volume == 40
    lettore.volume = 150
    assert lettore.volume == 100 and lettore.aspetta_i_comandi()
    assert apparecchio.volume == 1.0 and lettore.volume == 100
    lettore.volume = 25
    assert lettore.aspetta_i_comandi() and apparecchio.volume == 0.25
    apparecchio.volume = 0.3
    assert lettore.volume == 25
    lettore._quando_chiesto -= lontano.MEMORIA_DEL_VOLUME
    assert lettore.volume == 30
    lettore.muto = True
    assert lettore.aspetta_i_comandi() and apparecchio.muto is True and lettore.muto
    lettore.stop()
    assert lettore.percorso is None and lettore.aspetta_i_comandi() and apparecchio.chiamate[-1] == ("ferma",)
    # Da fermi, stop, pausa e salti non mandano niente.
    quanti = len(apparecchio.chiamate)
    lettore.stop()
    lettore.vai_a(5)
    assert lettore.pausa() is False and lettore.aspetta_i_comandi() and len(apparecchio.chiamate) == quanti
    # Senza un brano di MeTeOra che suona, lo speaker si lascia com'e'.
    lettore.chiudi()
    assert apparecchio.chiamate[-1] == ("chiudi", True) and banco.server.fermato


def test_i_salti_ravvicinati_partono_dal_punto_chiesto(tmp_path):
    # Gabriele, 15 novembre 2026: con lo speaker, Maiuscolo con Q due volte di
    # fila partiva dal punto vecchio, che lo speaker dice ancora, e la
    # finestra aspettava la sua risposta. Il salto va in fila al filo dei
    # comandi, la posizione e' subito il punto chiesto, e i salti in fila
    # diventano uno, al punto chiesto per ultimo.
    apparecchio = _ApparecchioLento()
    banco = _Banco(tmp_path, apparecchio=apparecchio)
    lettore, conti = banco.lettore, []
    lettore._al_conto = lambda nome, quanto: conti.append((nome, quanto))
    lettore.suona("brano.mp3")
    assert lettore.aspetta_i_comandi()
    banco.stato(trasmissione.IN_RIPRODUZIONE, "http://pc/file/1.mp3", durata=300.0)
    apparecchio.posizione = 30.0
    assert lettore.posizione == 30.0
    lettore.salta(10)
    # Il primo salto e' in volo, e lo speaker non risponde: la posizione e' il punto chiesto.
    assert _aspetta(lambda: ("vai_a", 40.0) in apparecchio.chiamate) and lettore.posizione == 40.0
    inizio = time.monotonic()
    lettore.salta(10)
    lettore.salta(10)
    assert time.monotonic() - inizio < 0.5 and lettore.posizione == 60.0
    assert conti == [("salti_uniti_allo_speaker", 1)]
    # Oltre la fine, la fine.
    lettore.vai_a(1000)
    assert lettore.posizione == 300.0 and conti == [("salti_uniti_allo_speaker", 1)] * 2
    lettore.vai_a(60)
    apparecchio.via.set()
    assert lettore.aspetta_i_comandi()
    assert [c for c in apparecchio.chiamate if c[0] == "vai_a"] == [("vai_a", 40.0), ("vai_a", 60.0)]
    # Arrivato il salto, il punto chiesto vale ancora per un attimo, poi vale quello dello speaker.
    assert lettore.posizione == 60.0
    assert _aspetta(lambda: lettore.posizione == 30.0, lontano.MEMORIA_DEL_PUNTO + 3)
    # Un salto chiesto e poi un brano nuovo: il punto non vale per lui.
    lettore.vai_a(90)
    lettore.suona("altro.mp3")
    assert lettore.posizione is None and lettore.aspetta_i_comandi()


def test_un_salto_senza_risposta_non_perde_lo_speaker(tmp_path):
    # pychromecast aspetta la risposta di un salto fino a 10 secondi, poi
    # solleva RequestTimeout: prima andava ad al_guasto, e la musica tornava
    # sul PC. Uno speaker che carica il punto nuovo puo' rispondere tardi;
    # la connessione che cade la dice al_distacco (15 novembre 2026).
    from pychromecast.error import RequestFailed, RequestTimeout

    apparecchio = _ApparecchioLento()
    apparecchio.via.set()
    banco = _Banco(tmp_path, apparecchio=apparecchio)
    lettore, conti = banco.lettore, []
    lettore._al_conto = lambda nome, quanto: conti.append((nome, quanto))
    lettore.suona("brano.mp3")
    banco.stato(trasmissione.IN_RIPRODUZIONE, "http://pc/file/1.mp3", durata=300.0)
    apparecchio.errore_del_salto = RequestTimeout("seek 40.0", 10.0)
    lettore.vai_a(40)
    assert lettore.aspetta_i_comandi()
    apparecchio.errore_del_salto = RequestFailed("seek 50.0")
    lettore.vai_a(50)
    assert lettore.aspetta_i_comandi()
    assert banco.avvisi == ["caricato"] and conti == [("salti_senza_risposta_dallo_speaker", 1)] * 2
    # Un altro errore, come la rete che non c'e', resta un guasto; e cosi'
    # una pausa senza risposta, come prima.
    apparecchio.errore_del_salto = OSError("rete assente")
    lettore.vai_a(60)
    assert lettore.aspetta_i_comandi() and banco.avvisi[-1] == ("guasto", "rete assente")
    apparecchio.guasto = RequestTimeout("pause", 10.0)
    lettore.pausa()
    assert lettore.aspetta_i_comandi() and banco.avvisi[-1][0] == "guasto" and "pause" in banco.avvisi[-1][1]


def test_un_salto_prima_che_lo_speaker_abbia_il_brano_lo_aspetta(banco):
    # Un salto chiesto prima che lo speaker abbia il brano andrebbe al brano
    # di prima, o a nessuno: aspetta il brano, e parte dal punto da cui il
    # brano e' partito, non dall'inizio (15 novembre 2026).
    lettore, apparecchio = banco.lettore, banco.apparecchio
    lettore.suona("brano.mp3", inizio=100.0)
    assert lettore.aspetta_i_comandi() and lettore.posizione is None
    lettore.salta(10)
    assert lettore.posizione == 110.0
    time.sleep(0.2)
    assert not [c for c in apparecchio.chiamate if c[0] == "vai_a"]
    banco.stato(trasmissione.IN_RIPRODUZIONE, "http://pc/file/1.mp3", durata=300.0)
    assert lettore.aspetta_i_comandi() and apparecchio.chiamate[-1] == ("vai_a", 110.0)


def test_un_salto_durante_la_conversione_non_ferma_il_brano(tmp_path):
    # Un salto o una pausa chiesti mentre la sorgente del WAV in RAM si
    # prepara, prima che il brano vada allo speaker, si rinviano: il brano
    # parte appena la sorgente c'e', e loro arrivano quando lo speaker lo ha.
    via = threading.Event()

    def lenta(percorso, sottobrano):
        via.wait(5)
        return _SorgenteFinta(percorso, sottobrano)

    banco = _Banco(tmp_path, converti=lenta)
    lettore, apparecchio, conti = banco.lettore, banco.apparecchio, []
    lettore._al_conto = lambda nome, quanto: conti.append((nome, quanto))
    lettore.suona("video.mkv")
    lettore.salta(30)
    lettore.salta(30)
    lettore.pausa()
    assert lettore.posizione == 60.0 and lettore.aspetta_i_comandi() and apparecchio.chiamate == []
    assert conti == [("salti_uniti_allo_speaker", 1)]
    inizio = time.monotonic()
    via.set()
    assert banco.aspetta_suona() and time.monotonic() - inizio < 1
    assert lettore.aspetta_i_comandi() and [c[0] for c in apparecchio.chiamate] == ["suona"] and apparecchio.chiamate[0][-1] is True
    banco.stato(trasmissione.IN_PAUSA, "http://pc/sorgente/1.wav", durata=600.0)
    assert lettore.aspetta_i_comandi() and apparecchio.chiamate[1:] == [("vai_a", 60.0), ("pausa",)]


def test_i_comandi_del_brano_di_prima_non_partono(tmp_path):
    # Dietro un salto lento, una pausa del brano di prima e un salto non
    # arrivano al brano nuovo; il volume, che e' dello speaker, si'.
    apparecchio = _ApparecchioLento()
    banco = _Banco(tmp_path, apparecchio=apparecchio)
    lettore = banco.lettore
    lettore.suona("brano.mp3")
    banco.stato(trasmissione.IN_RIPRODUZIONE, "http://pc/file/1.mp3", durata=300.0)
    lettore.vai_a(40)
    assert _aspetta(lambda: ("vai_a", 40.0) in apparecchio.chiamate)
    lettore.pausa()
    lettore.vai_a(80)
    lettore.volume = 55
    lettore.suona("altro.mp3")
    apparecchio.via.set()
    assert lettore.aspetta_i_comandi()
    dopo = apparecchio.chiamate[apparecchio.chiamate.index(("vai_a", 40.0)) + 1:]
    assert dopo == [("suona", "http://pc/file/2.mp3", "audio/mpeg", "altro.mp3", None, False)] and apparecchio.volume == 0.55


def test_la_chiusura_arriva_dopo_i_comandi_e_non_dice_guasti(tmp_path):
    # La chiusura va in fondo alla fila; senza attendi la finestra non la
    # aspetta. Da li' un comando che non arriva, o la connessione che cade,
    # non sono piu' un guasto: lo speaker non e' piu' quello in uso.
    apparecchio = _ApparecchioLento()
    banco = _Banco(tmp_path, apparecchio=apparecchio)
    lettore = banco.lettore
    lettore.suona("brano.mp3")
    banco.stato(trasmissione.IN_RIPRODUZIONE, "http://pc/file/1.mp3", durata=300.0)
    lettore.vai_a(40)
    assert _aspetta(lambda: ("vai_a", 40.0) in apparecchio.chiamate)
    inizio = time.monotonic()
    lettore.chiudi(attendi=False)
    assert time.monotonic() - inizio < 0.5 and not banco.server.fermato
    apparecchio.guasto = OSError("spento")
    lettore.volume = 10
    apparecchio.via.set()
    assert lettore.aspetta_i_comandi() and banco.server.fermato
    banco.al_distacco("LOST")
    assert banco.avvisi == ["caricato"] and apparecchio.chiamate[-1] == ("chiudi", False) and apparecchio.volume == 0.4


def test_la_chiusura_spegne_solo_i_brani_di_meteora(banco):
    banco.lettore.suona("brano.mp3")
    banco.stato(trasmissione.IN_RIPRODUZIONE, "http://pc/file/1.mp3")
    banco.lettore.chiudi()
    assert banco.apparecchio.chiamate[-1] == ("chiudi", False)


def test_la_conversione(banco):
    # 2.7.0: i brani che lo speaker non legge vanno come WAV in RAM, una
    # sorgente che il server serve a intervalli; a ogni brano la sua.
    lettore, apparecchio, server = banco.lettore, banco.apparecchio, banco.server
    lettore.suona(r"C:\m\brano.ape")
    assert banco.aspetta_suona()
    assert banco.conversioni == [(r"C:\m\brano.ape", None)]
    indirizzo, tipo, titolo = apparecchio.chiamate[-1][1:4]
    assert indirizzo == "http://pc/sorgente/1.wav" and tipo == "audio/wav" and titolo == "brano.ape"
    prima = server.sorgenti[-1]
    # Lo stesso brano, di nuovo: si riconverte, e la sorgente di prima se ne va.
    lettore.suona(r"C:\m\brano.ape")
    assert banco.aspetta_suona(2) and len(banco.conversioni) == 2
    assert prima.chiusa and prima in server.ritirate
    # Un sottobrano di un SID ha la sua sorgente.
    lettore.suona(r"C:\m\musica.sid", sottobrano=2, sottobrani=12)
    assert banco.aspetta_suona(3) and banco.conversioni[-1] == (r"C:\m\musica.sid", 2)
    assert lettore.sottobrano == 2 and lettore.sottobrani == 12
    # A fine brano il sottobrano resta, come nel motore: la finestra ci trova
    # il seguente, e non riparte dal primo (2.6.4). La sorgente se ne va.
    indirizzo = apparecchio.chiamate[-1][1]
    banco.stato(trasmissione.IN_RIPRODUZIONE, indirizzo, durata=97.0)
    banco.stato(trasmissione.FERMO, indirizzo, motivo="FINISHED")
    assert banco.avvisi[-1] == "fine" and lettore.percorso is None
    assert lettore.sottobrano == 2 and lettore.sottobrani == 12
    assert server.sorgenti[-1].chiusa
    lettore.suona(r"C:\m\musica.sid", sottobrano=3, sottobrani=12)
    assert banco.aspetta_suona(4) and lettore.sottobrano == 3
    # Lo stop cancella il sottobrano, e anche la sua sorgente se ne va.
    lettore.stop()
    assert lettore.sottobrano is None and lettore.sottobrani is None and server.sorgenti[-1].chiusa
    # Un file che lo speaker legge da se' va com'e', senza sorgente.
    lettore.suona(r"C:\m\brano.mp3")
    assert banco.aspetta_suona(5) and apparecchio.chiamate[-1][1:3] == ("http://pc/file/1.mp3", "audio/mpeg") and len(server.sorgenti) == 4


def test_una_sorgente_pronta_tardi_non_suona(tmp_path):
    via = threading.Event()
    preparate = []

    def lenta(percorso, sottobrano):
        via.wait(5)
        preparate.append(_SorgenteFinta(percorso, sottobrano))
        return preparate[-1]

    banco = _Banco(tmp_path, converti=lenta)
    banco.lettore.suona("lento.ape")
    banco.lettore.suona("veloce.mp3")
    via.set()
    assert banco.aspetta_suona()
    threading.Event().wait(0.2)
    assert [c[1] for c in banco.apparecchio.chiamate if c[0] == "suona"] == ["http://pc/file/1.mp3"]
    # La sorgente arrivata tardi non serve, e si chiude.
    assert preparate and preparate[0].chiusa


def test_gli_errori(tmp_path):
    def rotta(percorso, sottobrano):
        raise ValueError(f"la durata di {percorso} non si sa")

    banco = _Banco(tmp_path, converti=rotta)
    # Una sorgente che non si prepara e' un errore del brano.
    banco.lettore.suona("rovinato.ape")
    for _ in range(500):
        if ("errore", "rovinato.ape") in banco.avvisi:
            break
        threading.Event().wait(0.01)
    assert ("errore", "rovinato.ape") in banco.avvisi and banco.lettore.percorso is None
    # Anche dopo un errore il sottobrano resta, per il seguente.
    banco.lettore.suona("rovinato.sid", sottobrano=4, sottobrani=27)
    for _ in range(500):
        if ("errore", "rovinato.sid") in banco.avvisi:
            break
        threading.Event().wait(0.01)
    assert ("errore", "rovinato.sid") in banco.avvisi and banco.lettore.percorso is None and banco.lettore.sottobrano == 4
    # Lo speaker che non carica il brano: errore anche prima di averlo.
    banco.lettore.suona("brano.mp3")
    banco.allo_stato({"stato": trasmissione.FERMO, "posizione": None, "durata": None, "motivo": "ERROR", "codice": 104})
    assert banco.avvisi[-1] == ("errore", "brano.mp3")
    # Dal telefono parte altro sullo speaker: il lettore se ne accorge.
    banco.lettore.suona("brano.mp3")
    banco.stato(trasmissione.IN_RIPRODUZIONE, "http://pc/file/2.mp3")
    banco.stato(trasmissione.IN_RIPRODUZIONE, "https://youtube/altro")
    assert banco.avvisi[-1] == "interruzione" and banco.lettore.percorso is None
    banco.lettore.suona("brano.mp3")
    banco.stato(trasmissione.IN_RIPRODUZIONE, "http://pc/file/3.mp3")
    banco.stato(trasmissione.FERMO, "http://pc/file/3.mp3", motivo="INTERRUPTED")
    assert banco.avvisi[-1] == "interruzione"
    # La connessione che cade va ad al_guasto.
    banco.al_distacco("LOST")
    assert banco.avvisi[-1] == ("guasto", "connessione LOST")
    # Un comando che non arriva va ad al_guasto, e non solleva.
    banco.lettore.suona("brano.mp3")
    banco.apparecchio.guasto = OSError("speaker spento")
    banco.lettore.pausa()
    assert banco.lettore.aspetta_i_comandi() and banco.avvisi[-1] == ("guasto", "speaker spento")


def test_una_radio_va_allo_speaker_dal_ripetitore(banco, monkeypatch):
    # La radio la legge MeTeOra e la passa cosi' com'e', senza metadati e
    # senza conversione, come flusso senza fine (3.11.1).
    import io

    from test_diretta import _icy, _server

    import diretta
    import indirizzi

    monkeypatch.setattr(diretta, "RIPROVE", 0)
    audio = bytes(range(200)) + b"y" * 100
    porta, _richieste = _server([_icy(audio, 100, [None, "Lucio Dalla - Caruso"])])
    url = f"http://127.0.0.1:{porta}/stream"
    indirizzi.metti_il_diretto(url, dal_vivo=True)
    titoli = []
    banco.lettore._al_titolo = titoli.append
    banco.lettore.suona(url)
    assert banco.aspetta_suona()
    chiamata = next(c for c in banco.apparecchio.chiamate if c[0] == "suona")
    assert chiamata[1].startswith("http://pc/flusso/radio") and chiamata[1].endswith(".mp3") and chiamata[2] == "audio/mpeg"
    assert banco.apparecchio.in_diretta and not banco.conversioni and not banco.server.pubblicati
    uscita = io.BytesIO()
    banco.server.flussi[-1][1](uscita)
    assert uscita.getvalue() == audio and titoli == ["Lucio Dalla - Caruso"] and banco.lettore.titolo_in_onda == "Lucio Dalla - Caruso"
    banco.lettore.stop()
    assert banco.lettore.titolo_in_onda is None


def test_allo_speaker_arrivano_solo_fotogrammi_interi(banco, monkeypatch):
    # Come la BBC: byte rotti fra i fotogrammi, che fermavano GabryBar (3.11.6).
    import io

    from test_diretta import _icy, _mp3, _server

    import diretta
    import indirizzi

    monkeypatch.setattr(diretta, "RIPROVE", 0)
    fotogrammi = _mp3(30)
    rotti = b"\x8d\x01\x02" * 11
    audio = b"".join(fotogrammi[:10]) + rotti + b"".join(fotogrammi[10:])
    porta, _richieste = _server([_icy(audio, 1000, [])])
    url = f"http://127.0.0.1:{porta}/bbc"
    indirizzi.metti_il_diretto(url, dal_vivo=True)
    conti = []
    banco.lettore._al_conto = lambda nome, quanto: conti.append((nome, quanto))
    banco.lettore.suona(url)
    assert banco.aspetta_suona()
    uscita = io.BytesIO()
    banco.server.flussi[-1][1](uscita)
    assert uscita.getvalue() == b"".join(fotogrammi)
    assert conti == [("rotture_tolte_allo_speaker", 1), ("byte_rotti_tolti_allo_speaker", len(rotti))]
    banco.lettore.stop()


def test_lo_stop_chiude_la_radio_che_tace(banco):
    # Una radio che manda le intestazioni e poi tace: lo stop chiude la sua
    # lettura subito, senza aspettare la rete (verifica della 3.11.3).
    import io
    import socket
    import time

    import indirizzi

    presa = socket.socket()
    presa.bind(("127.0.0.1", 0))
    presa.listen(2)
    fine = threading.Event()

    def servi():
        conn, _da = presa.accept()
        conn.recv(4096)
        conn.sendall(b"HTTP/1.0 200 OK\r\nContent-Type: audio/mpeg\r\n\r\n" + b"a" * 10)
        fine.wait(30)
        conn.close()
        presa.close()

    threading.Thread(target=servi, daemon=True).start()
    url = f"http://127.0.0.1:{presa.getsockname()[1]}/stream"
    indirizzi.metti_il_diretto(url, dal_vivo=True)
    banco.lettore.suona(url)
    assert banco.aspetta_suona()
    uscita = io.BytesIO()
    filo = threading.Thread(target=banco.server.flussi[-1][1], args=(uscita,))
    filo.start()
    time.sleep(0.3)
    inizio = time.monotonic()
    banco.lettore.stop()
    filo.join(5)
    fine.set()
    assert not filo.is_alive() and time.monotonic() - inizio < 2 and uscita.getvalue() == b"a" * 10


def test_una_radio_che_porta_a_una_lista_va_diretta_allo_speaker(banco):
    from test_diretta import _server

    import indirizzi

    porta, _richieste = _server([b"HTTP/1.0 200 OK\r\nContent-Type: application/vnd.apple.mpegurl\r\n\r\n#EXTM3U\n"])
    url = f"http://127.0.0.1:{porta}/live"
    indirizzi.metti_il_diretto(url, dal_vivo=True)
    banco.lettore.suona(url)
    assert banco.aspetta_suona()
    chiamata = next(c for c in banco.apparecchio.chiamate if c[0] == "suona")
    assert chiamata[1] == url and chiamata[2] == "application/x-mpegURL" and not banco.server.flussi


# Le TV sullo speaker, con l'audio convertito dal vivo (3.12.0).

_LISTA = b"HTTP/1.0 200 OK\r\nContent-Type: application/vnd.apple.mpegurl\r\n\r\n#EXTM3U\n"


def test_una_tv_va_allo_speaker_con_l_audio_convertito(banco):
    import io

    from test_diretta import _server
    from test_wav_in_ram import _atteso, _DalVivo

    import indirizzi

    tv = _LISTA + b'#EXT-X-STREAM-INF:BANDWIDTH=2262829,CODECS="avc1.77.41,mp4a.40.2",RESOLUTION=1920x1080\nchunklist.m3u8\n'
    porta, _richieste = _server([tv])
    url = f"http://127.0.0.1:{porta}/bbstv/playlist.m3u8"
    indirizzi.metti_il_diretto(url, dal_vivo=True)
    chiesti, conti = [], []

    def converti_dal_vivo(percorso, uscita, alla_fine):
        chiesti.append(percorso)
        return _DalVivo(10000)(uscita, alla_fine)

    banco.lettore._converti_dal_vivo = converti_dal_vivo
    banco.lettore._al_conto = lambda nome, quanto: conti.append((nome, quanto))
    banco.lettore.suona(url)
    assert banco.aspetta_suona()
    chiamata = next(c for c in banco.apparecchio.chiamate if c[0] == "suona")
    assert chiamata[1].startswith("http://pc/flusso/radio") and chiamata[1].endswith(".wav") and chiamata[2] == "audio/wav"
    assert banco.apparecchio.in_diretta and conti == [("dirette_convertite_per_lo_speaker", 1)]
    uscita = io.BytesIO()
    banco.server.flussi[-1][1](uscita)
    assert chiesti == [url] and uscita.getvalue().startswith(b"RIFF") and uscita.getvalue()[44:] == _atteso(0, 10000)
    banco.lettore.stop()


def test_una_lista_rifiutata_dallo_speaker_poi_va_convertita(banco, monkeypatch):
    from test_diretta import _server
    from test_wav_in_ram import _DalVivo

    import indirizzi

    monkeypatch.setattr(lontano, "_liste_da_convertire", set())
    # Una lista di pezzi non dice se ha il video: va allo speaker com'e'.
    porta, _richieste = _server([_LISTA + b"#EXTINF:6.0,\nseg1.ts\n"])
    url = f"http://127.0.0.1:{porta}/tv.m3u8"
    indirizzi.metti_il_diretto(url, dal_vivo=True)
    conti = []
    banco.lettore._converti_dal_vivo = lambda percorso, uscita, alla_fine: _DalVivo(100)(uscita, alla_fine)
    banco.lettore._al_conto = lambda nome, quanto: conti.append((nome, quanto))
    banco.lettore.suona(url)
    assert banco.aspetta_suona()
    assert banco.apparecchio.chiamate[-1][1:3] == (url, "application/x-mpegURL")
    # Lo speaker la rifiuta: la riprova della finestra la manda convertita.
    banco.stato(trasmissione.FERMO, motivo="ERROR")
    assert banco.avvisi[-1] == ("errore", url) and url in lontano._liste_da_convertire
    assert conti == [("liste_rifiutate_dallo_speaker", 1)]
    banco.lettore.suona(url)
    assert banco.aspetta_suona(2)
    assert banco.apparecchio.chiamate[-1][2] == "audio/wav" and conti[-1] == ("dirette_convertite_per_lo_speaker", 1)
    banco.lettore.stop()
