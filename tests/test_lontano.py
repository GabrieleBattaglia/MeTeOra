# MeTeOra, le prove del lettore lontano: uno speaker Cast al posto della scheda audio.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/11/2026: nasce con lontano.py, nella 1.117.0.

"""Le prove di lontano.py, con un apparecchio, un server e una conversione
finti: niente rete e niente libmpv. Gli stati dell'apparecchio si mandano
a mano, come li manderebbe pychromecast dal suo filo."""

import os
import threading

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

    def suona(self, indirizzo, tipo, titolo=None, inizio=None, in_pausa=False):
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


class _ServerFinto:
    def __init__(self):
        self.pubblicati = []
        self.fermato = False

    def pubblica_file(self, percorso):
        self.pubblicati.append(percorso)
        return f"http://pc/file/{len(self.pubblicati)}{os.path.splitext(percorso)[1].lower()}"

    def ferma(self):
        self.fermato = True


class _Banco:
    """Il lettore lontano con i suoi finti, e gli avvisi in una lista."""

    def __init__(self, tmp_path, converti=None):
        self.apparecchio = _ApparecchioFinto()
        self.server = _ServerFinto()
        self.avvisi = []
        self.conversioni = []
        self.allo_stato = self.al_distacco = None

        def connetti(allo_stato, al_distacco):
            self.allo_stato, self.al_distacco = allo_stato, al_distacco
            return self.apparecchio

        def converti_finto(percorso, sottobrano, uscita):
            self.conversioni.append((percorso, sottobrano))
            with open(uscita, "wb") as f:
                f.write(b"fLaC")
            return True

        self.lettore = lontano.LettoreLontano(connetti, self.server, str(tmp_path), converti or converti_finto,
            alla_fine=lambda: self.avvisi.append("fine"), all_errore=lambda p: self.avvisi.append(("errore", p)),
            al_caricamento=lambda: self.avvisi.append("caricato"), alla_conversione=lambda p: self.avvisi.append(("conversione", p)),
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
    indirizzo = banco.apparecchio.chiamate[-1][1]
    banco.stato(trasmissione.IN_RIPRODUZIONE, indirizzo, durata=200.0)
    banco.allo_stato({"stato": trasmissione.IN_CARICAMENTO, "posizione": 199.9, "durata": 200.0, "motivo": None, "indirizzo": indirizzo})
    banco.stato(trasmissione.FERMO, indirizzo, motivo="FINISHED")
    threading.Event().wait(0.2)
    assert banco.avvisi.count("fine") == 2
    # E se riparte, per esempio dopo un salto indietro, la fine attesa si toglie.
    lettore.suona("altro.mp3")
    indirizzo = banco.apparecchio.chiamate[-1][1]
    banco.stato(trasmissione.IN_RIPRODUZIONE, indirizzo, durata=200.0)
    banco.allo_stato({"stato": trasmissione.IN_CARICAMENTO, "posizione": 200.0, "durata": 200.0, "motivo": None, "indirizzo": indirizzo})
    banco.stato(trasmissione.IN_RIPRODUZIONE, indirizzo, durata=200.0)
    threading.Event().wait(0.2)
    assert banco.avvisi.count("fine") == 2 and lettore.percorso == "altro.mp3"


def test_i_comandi(banco):
    lettore, apparecchio = banco.lettore, banco.apparecchio
    lettore.suona("brano.flac", in_pausa=True)
    assert apparecchio.chiamate[-1][-1] is True and lettore.in_pausa
    banco.stato(trasmissione.IN_PAUSA, "http://pc/file/1.flac")
    assert banco.avvisi == ["caricato"] and lettore.in_pausa
    assert lettore.pausa() is False and apparecchio.chiamate[-1] == ("riprendi",)
    assert lettore.pausa(True) is True and apparecchio.chiamate[-1] == ("pausa",)
    apparecchio.posizione = 30.0
    lettore.salta(-40)
    lettore.vai_a(90)
    assert apparecchio.chiamate[-2:] == [("vai_a", 0.0), ("vai_a", 90.0)]
    # Il volume da 0 a 100, quello dello speaker; quello chiesto vale per un
    # attimo, finche' lo speaker non dice il suo.
    assert lettore.volume == 40
    lettore.volume = 150
    assert apparecchio.volume == 1.0 and lettore.volume == 100
    lettore.volume = 25
    assert apparecchio.volume == 0.25
    apparecchio.volume = 0.3
    assert lettore.volume == 25
    lettore._quando_chiesto -= lontano.MEMORIA_DEL_VOLUME
    assert lettore.volume == 30
    lettore.muto = True
    assert apparecchio.muto is True and lettore.muto
    lettore.stop()
    assert apparecchio.chiamate[-1] == ("ferma",) and lettore.percorso is None
    # Da fermi, stop, pausa e salti non mandano niente.
    quanti = len(apparecchio.chiamate)
    lettore.stop()
    lettore.vai_a(5)
    assert lettore.pausa() is False and len(apparecchio.chiamate) == quanti
    # Senza un brano di MeTeOra che suona, lo speaker si lascia com'e'.
    lettore.chiudi()
    assert apparecchio.chiamate[-1] == ("chiudi", True) and banco.server.fermato


def test_la_chiusura_spegne_solo_i_brani_di_meteora(banco):
    banco.lettore.suona("brano.mp3")
    banco.stato(trasmissione.IN_RIPRODUZIONE, "http://pc/file/1.mp3")
    banco.lettore.chiudi()
    assert banco.apparecchio.chiamate[-1] == ("chiudi", False)


def test_la_conversione(banco):
    lettore, apparecchio = banco.lettore, banco.apparecchio
    lettore.suona(r"C:\m\brano.ape")
    assert banco.aspetta_suona()
    assert banco.conversioni == [(r"C:\m\brano.ape", None)] and banco.avvisi == [("conversione", r"C:\m\brano.ape")]
    indirizzo, tipo, titolo = apparecchio.chiamate[-1][1:4]
    assert indirizzo.endswith(".flac") and tipo == "audio/flac" and titolo == "brano.ape"
    assert banco.server.pubblicati[-1].endswith(".flac") and os.path.isfile(banco.server.pubblicati[-1])
    # Lo stesso brano, di nuovo: la conversione c'e' gia'.
    lettore.suona(r"C:\m\brano.ape")
    assert banco.aspetta_suona(2) and len(banco.conversioni) == 1
    # Un sottobrano di un SID si converte a parte.
    lettore.suona(r"C:\m\musica.sid", sottobrano=2, sottobrani=12)
    assert banco.aspetta_suona(3) and banco.conversioni[-1] == (r"C:\m\musica.sid", 2)
    assert lettore.sottobrano == 2 and lettore.sottobrani == 12
    # A fine brano il sottobrano resta, come nel motore: la finestra ci trova
    # il seguente, e non riparte dal primo (2.6.4). Lo stop lo cancella.
    indirizzo = apparecchio.chiamate[-1][1]
    banco.stato(trasmissione.IN_RIPRODUZIONE, indirizzo, durata=97.0)
    banco.stato(trasmissione.FERMO, indirizzo, motivo="FINISHED")
    assert banco.avvisi[-1] == "fine" and lettore.percorso is None
    assert lettore.sottobrano == 2 and lettore.sottobrani == 12
    lettore.suona(r"C:\m\musica.sid", sottobrano=3, sottobrani=12)
    assert banco.aspetta_suona(4) and lettore.sottobrano == 3
    lettore.stop()
    assert lettore.sottobrano is None and lettore.sottobrani is None


def test_una_conversione_finita_tardi_non_suona(tmp_path):
    via = threading.Event()

    def lenta(percorso, sottobrano, uscita):
        via.wait(5)
        with open(uscita, "wb") as f:
            f.write(b"fLaC")
        return True

    banco = _Banco(tmp_path, converti=lenta)
    banco.lettore.suona("lento.ape")
    banco.lettore.suona("veloce.mp3")
    via.set()
    assert banco.aspetta_suona()
    threading.Event().wait(0.2)
    assert [c[1] for c in banco.apparecchio.chiamate if c[0] == "suona"] == ["http://pc/file/1.mp3"]


def test_gli_errori(tmp_path):
    banco = _Banco(tmp_path, converti=lambda percorso, sottobrano, uscita: False)
    # Una conversione che non riesce e' un errore del brano.
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
    assert banco.avvisi[-1] == ("guasto", "speaker spento")
