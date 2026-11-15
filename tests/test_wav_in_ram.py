# MeTeOra, le prove del WAV in RAM per gli speaker Cast (2.7.0).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con wav_in_ram.py, nella 2.7.0. Nella 3.12.0 il WAV senza fine delle dirette.

"""Le prove di wav_in_ram.py con un convertitore finto, che scrive nella pipe
con nome vera dei byte che si riconoscono: il byte n del PCM vale n % 251.
Niente libmpv: il passaggio vero lo prova tests/test_motore.py."""

import struct
import threading
import time

import pytest

import wav_in_ram
from wav_in_ram import INTESTAZIONE, SorgenteWav


def _atteso(inizio, quanti):
    return bytes((inizio + n) % 251 for n in range(quanti))


class _Convertitore:
    """avvia(secondi, uscita, alla_fine, frequenza, bit) come quello del motore:
    scrive nella pipe i byte da secondi in poi, fino a quanti ne ha, a pezzi;
    terminate() lo ferma. Annota le partenze."""

    def __init__(self, totale, scrive=None):
        self.totale = totale if scrive is None else scrive
        self.partenze = []

    def __call__(self, secondi, uscita, alla_fine, frequenza, bit):
        inizio = round(secondi * frequenza * wav_in_ram.quadro(bit))
        self.partenze.append(inizio)
        fermo = threading.Event()

        def scrivi():
            try:
                with open(uscita, "wb", buffering=0) as pipe:
                    posizione = inizio
                    while posizione < self.totale and not fermo.is_set():
                        quanti = min(8192, self.totale - posizione)
                        pipe.write(_atteso(posizione, quanti))
                        posizione += quanti
            except OSError:
                pass
            finally:
                alla_fine()

        threading.Thread(target=scrivi, daemon=True).start()
        return type("Lettore", (), {"terminate": lambda _self: fermo.set()})()


class _SoloDallInizio(_Convertitore):
    """Il convertitore di un flusso che dopo la prima volta non si apre piu',
    come una pagina di YouTube con il flusso scaduto: dall'inizio scrive, da
    un salto non apre nemmeno la pipe, e dice subito che ha finito."""

    def __call__(self, secondi, uscita, alla_fine, frequenza, bit):
        if secondi:
            self.partenze.append(round(secondi * frequenza * wav_in_ram.quadro(bit)))
            threading.Thread(target=alla_fine, daemon=True).start()
            return type("Lettore", (), {"terminate": lambda _self: None})()
        return super().__call__(secondi, uscita, alla_fine, frequenza, bit)


def _veloce(inizio, quanti):
    """_atteso, ma svelto: un giro di 251 byte ripetuto."""
    giro = bytes(range(251)) * (quanti // 251 + 2)
    return giro[inizio % 251:inizio % 251 + quanti]


class _Ostinato:
    """Un convertitore come libmpv: scrive piu' svelto di chi legge, a pezzi
    da 64 KB, e il suo terminate aspetta che abbia finito di scrivere. Fermo a
    scrivere in una pipe piena, che nessuno legge, terminate non tornerebbe
    mai: qui torna dopo ATTESA secondi, e si conta fra i bloccati.
    dal_vivo(uscita, alla_fine) e' quello delle dirette, senza fine."""

    ATTESA = 3.0

    def __init__(self, totale=None):
        self.totale = totale
        self.tornati = self.bloccati = 0
        self._blocco = threading.Lock()

    def __call__(self, secondi, uscita, alla_fine, frequenza, bit):
        return self._parti(round(secondi * frequenza * wav_in_ram.quadro(bit)), uscita, alla_fine)

    def dal_vivo(self, uscita, alla_fine):
        return self._parti(0, uscita, alla_fine)

    def _parti(self, inizio, uscita, alla_fine):
        fermo = threading.Event()

        def scrivi():
            try:
                with open(uscita, "wb", buffering=0) as pipe:
                    posizione = inizio
                    while not fermo.is_set() and (self.totale is None or posizione < self.totale):
                        pipe.write(_veloce(posizione, 65536))
                        posizione += 65536
            except OSError:
                pass
            finally:
                alla_fine()

        filo = threading.Thread(target=scrivi, name="convertitore ostinato", daemon=True)
        filo.start()
        ostinato = self

        class Lettore:
            def terminate(self):
                fermo.set()
                filo.join(ostinato.ATTESA)
                with ostinato._blocco:
                    if filo.is_alive():
                        ostinato.bloccati += 1
                    else:
                        ostinato.tornati += 1

        return Lettore()


def _vivi(nome):
    return sum(1 for f in threading.enumerate() if f.name.startswith(nome))


def _esatti(sorgente, inizio, quanti, richiesta):
    """quanti byte da inizio, chiesti finche' arrivano, come fa il server:
    leggi da' quelli gia' convertiti, anche meno di quanti."""
    letti = bytearray()
    while len(letti) < quanti:
        pezzo = sorgente.leggi(inizio + len(letti), quanti - len(letti), richiesta)
        if not pezzo:
            return bytes(letti) if letti else pezzo
        letti += pezzo
    return bytes(letti)


def _tutto(sorgente, inizio=0):
    """Legge tutta la sorgente da inizio, come il server, con una richiesta."""
    richiesta = sorgente.nuova_richiesta()
    letti = bytearray()
    while inizio + len(letti) < sorgente.dimensione:
        pezzo = sorgente.leggi(inizio + len(letti), 65536, richiesta)
        if not pezzo:
            break
        letti += pezzo
    return bytes(letti)


def test_misure_e_intestazione():
    assert wav_in_ram.dimensione_della_finestra(10 * 2**20) == wav_in_ram.FINESTRA_MINIMA // 12 * 12
    assert wav_in_ram.dimensione_della_finestra(40 * 2**30) == wav_in_ram.FINESTRA_MASSIMA // 12 * 12
    assert wav_in_ram.dimensione_della_finestra(2 * 2**30) == int(2 * 2**30 * 0.05) // 12 * 12
    testa = wav_in_ram.intestazione(1200, 96000, 24)
    assert len(testa) == INTESTAZIONE and testa[:4] == b"RIFF" and testa[8:16] == b"WAVEfmt "
    assert struct.unpack("<I", testa[40:44])[0] == 1200 and struct.unpack("<I", testa[24:28])[0] == 96000
    assert struct.unpack("<IHH", testa[28:36]) == (96000 * 6, 6, 24)


def test_la_frequenza_e_i_bit_della_sorgente():
    # 5 novembre 2026, domanda di Gabriele: la qualita' della sorgente, nei
    # limiti dello speaker; sopra i 96 kHz a 96, o a 88,2 per i multipli di
    # 44,1, come i DSD; sotto i 44,1 kHz al multiplo giusto.
    vale = wav_in_ram.frequenza_della_sorgente
    assert [vale(f) for f in (44100, 48000, 88200, 96000)] == [44100, 48000, 88200, 96000]
    assert vale(192000) == 96000 and vale(352800) == 88200 and vale(176400) == 88200
    assert vale(22050) == 44100 and vale(11025) == 44100 and vale(32000) == 96000 and vale(8000) == 48000
    assert vale(None) == 48000 and vale(64000) == 48000
    # Nei 4 GB del WAV: prima la frequenza alla meta', poi 16 bit, per
    # ultimo 24 kHz.
    formato = wav_in_ram.formato_per
    assert formato(3600, 96000, 24) == (96000, 24)
    assert formato(3 * 3600, 96000, 24) == (48000, 24)
    assert formato(5 * 3600, 96000, 24) == (48000, 16)
    assert formato(3 * 3600, 44100, 24) == (44100, 24) and formato(5 * 3600, 44100, 24) == (44100, 16)
    assert formato(5 * 3600) == (48000, 16) and formato(7 * 3600) == (24000, 16)


def test_a_24_bit_e_96_khz():
    durata = 0.5
    totale = int(durata * 96000) * 6
    sorgente = SorgenteWav(_Convertitore(totale), durata, finestra=4 * 2**20, frequenza=96000, bit=24)
    try:
        assert (sorgente.frequenza, sorgente.bit, sorgente.quadro) == (96000, 24, 6) and sorgente.dimensione == INTESTAZIONE + totale
        corpo = _tutto(sorgente)
        assert corpo[:INTESTAZIONE] == wav_in_ram.intestazione(totale, 96000, 24) and corpo[INTESTAZIONE:] == _atteso(0, totale)
    finally:
        sorgente.chiudi()


def test_la_sorgente_da_tutto_il_brano(monkeypatch):
    durata = 0.5
    totale = int(durata * 48000) * 4
    convertitore = _Convertitore(totale)
    sorgente = SorgenteWav(convertitore, durata, finestra=4 * 2**20)
    try:
        assert sorgente.dimensione == INTESTAZIONE + totale and sorgente.tipo == "audio/wav"
        corpo = _tutto(sorgente)
        assert corpo[:INTESTAZIONE] == wav_in_ram.intestazione(totale, 48000) and corpo[INTESTAZIONE:] == _atteso(0, totale)
        assert convertitore.partenze == [0]
    finally:
        sorgente.chiudi()


def test_il_resto_e_silenzio_e_la_fine_si_taglia():
    # Il convertitore che finisce prima: il resto e' silenzio; quello che va
    # oltre la durata dichiarata non si serve.
    totale = int(0.5 * 48000) * 4
    corto = SorgenteWav(_Convertitore(totale, scrive=totale - 4000), 0.5, finestra=4 * 2**20)
    lungo = SorgenteWav(_Convertitore(totale, scrive=totale + 8000), 0.5, finestra=4 * 2**20)
    try:
        corpo = _tutto(corto)[INTESTAZIONE:]
        assert len(corpo) == totale and corpo[:-4000] == _atteso(0, totale - 4000) and corpo[-4000:] == bytes(4000)
        assert _tutto(lungo)[INTESTAZIONE:] == _atteso(0, totale)
    finally:
        corto.chiudi()
        lungo.chiudi()


def test_il_convertitore_si_ferma_a_finestra_piena():
    durata = 10.0
    totale = int(durata * 48000) * 4
    sorgente = SorgenteWav(_Convertitore(totale), durata, finestra=256 * 1024)
    try:
        time.sleep(0.5)
        # Davanti a chi legge, al piu' la finestra meno la parte dietro.
        assert sorgente.convertiti <= sorgente.finestra - sorgente.dietro + 65536
        assert _tutto(sorgente)[INTESTAZIONE:] == _atteso(0, totale)
        assert sorgente.convertiti == totale
    finally:
        sorgente.chiudi()


def test_l_anello_tiene_la_parte_dietro_anche_a_cavallo():
    # 15 novembre 2026: la finestra sta in un anello allocato una volta, che
    # non si rialloca a ogni pezzo. Letto un mega di fila, cioe' l'anello
    # quasi tre volte, un salto indietro dentro la parte dietro e una lettura
    # a cavallo della fine dell'anello danno i byte giusti, senza ripartire.
    durata = 10.0
    totale = int(durata * 48000) * 4
    convertitore = _Convertitore(totale)
    sorgente = SorgenteWav(convertitore, durata, finestra=256 * 1024)
    try:
        assert sorgente._capacita == 256 * 1024 + 2 * wav_in_ram.PEZZO
        mega = 1024 * 1024
        assert _esatti(sorgente, INTESTAZIONE, mega, sorgente.nuova_richiesta()) == _atteso(0, mega)
        indietro = mega - 32 * 1024
        assert _esatti(sorgente, INTESTAZIONE + indietro, 16 * 1024, sorgente.nuova_richiesta()) == _atteso(indietro, 16 * 1024)
        a_cavallo = 3 * sorgente._capacita - 4096
        assert _esatti(sorgente, INTESTAZIONE + a_cavallo, 8192, sorgente.nuova_richiesta()) == _atteso(a_cavallo, 8192)
        assert convertitore.partenze == [0] and sorgente.ripartenze == 0
    finally:
        sorgente.chiudi()


def test_un_salto_fuori_dalla_finestra_riparte():
    durata = 60.0
    totale = int(durata * 48000) * 4
    convertitore = _Convertitore(totale)
    sorgente = SorgenteWav(convertitore, durata, finestra=256 * 1024)
    try:
        lontano = INTESTAZIONE + 40 * 48000 * 4
        richiesta = sorgente.nuova_richiesta()
        pezzo = _esatti(sorgente, lontano, 1000, richiesta)
        assert pezzo == _atteso(lontano - INTESTAZIONE, 1000)
        assert convertitore.partenze == [0, 40 * 48000 * 4] and sorgente.ripartenze == 1
        # Una richiesta nuova ferma quella di prima.
        sorgente.nuova_richiesta()
        assert sorgente.leggi(lontano + 1000, 1000, richiesta) is None
    finally:
        sorgente.chiudi()


def test_i_brani_emulati_in_avanti_aspettano():
    # I SID ripartendo emulano da capo: in avanti si aspetta la conversione in corsa.
    durata = 30.0
    totale = int(durata * 48000) * 4
    convertitore = _Convertitore(totale)
    sorgente = SorgenteWav(convertitore, durata, emulato=True, finestra=64 * 2**20)
    try:
        lontano = INTESTAZIONE + 25 * 48000 * 4
        assert _esatti(sorgente, lontano, 1000, sorgente.nuova_richiesta()) == _atteso(lontano - INTESTAZIONE, 1000)
        assert convertitore.partenze == [0]
    finally:
        sorgente.chiudi()


def test_un_brano_che_non_si_legge(monkeypatch):
    # Una conversione che non scrive niente: il server chiude, e lo speaker da' errore.
    sorgente = SorgenteWav(_Convertitore(0), 1.0, finestra=4 * 2**20)
    try:
        richiesta = sorgente.nuova_richiesta()
        assert sorgente.leggi(0, 44, richiesta)[:4] == b"RIFF"
        assert sorgente.leggi(INTESTAZIONE, 1000, richiesta) is None and sorgente.guasta
    finally:
        sorgente.chiudi()

    def rotto(secondi, uscita, alla_fine, frequenza, bit):
        raise RuntimeError("libmpv non parte")

    sorgente = SorgenteWav(rotto, 1.0, finestra=4 * 2**20)
    assert sorgente.leggi(INTESTAZIONE, 1000, sorgente.nuova_richiesta()) is None and sorgente.guasta


def test_una_ripartenza_che_non_scrive_niente_e_un_guasto():
    # Gabriele, 15 novembre 2026: un flusso di YouTube scaduto non si apriva
    # piu' alla ripartenza, e lo speaker restava nel silenzio fino alla fine
    # del brano, anche per ore. Una ripartenza vuota e' un guasto, e il
    # server chiude; negli ultimi SECONDI_VUOTI_IN_FONDO e' silenzio, come
    # prima, perche' li' la fine vera puo' venire prima di quella dichiarata.
    durata = 120.0
    totale = int(durata * 48000) * 4
    convertitore = _SoloDallInizio(totale)
    sorgente = SorgenteWav(convertitore, durata, finestra=2**20 // 12 * 12)
    try:
        assert _esatti(sorgente, INTESTAZIONE, 1000, sorgente.nuova_richiesta()) == _atteso(0, 1000)
        in_fondo = INTESTAZIONE + int((durata - wav_in_ram.SECONDI_VUOTI_IN_FONDO / 2) * 48000) * 4
        assert sorgente.leggi(in_fondo, 1000, sorgente.nuova_richiesta()) == bytes(1000) and not sorgente.guasta
        lontano = INTESTAZIONE + 60 * 48000 * 4
        assert sorgente.leggi(lontano, 1000, sorgente.nuova_richiesta()) is None and sorgente.guasta
        assert sorgente.ripartenze == 2 and len(convertitore.partenze) == 3
    finally:
        sorgente.chiudi()


def test_le_ripartenze_non_lasciano_convertitori_appesi():
    # 15 novembre 2026, dalla misura dell'esploratore: con una conversione
    # veloce, il flusso a pezzi di YouTube o un file del disco, il passaggio
    # sostituito lasciava libmpv ferma a scrivere in una pipe che nessuno
    # leggeva piu', e terminate la aspettava per sempre: a ogni ripartenza
    # restavano vivi un filo di fine e una libmpv. La pipe ora si vuota
    # finche' libmpv non si ferma.
    convertitore = _Ostinato(120 * 48000 * 4)
    sorgente = SorgenteWav(convertitore, 120.0, finestra=2**20 // 12 * 12)
    try:
        time.sleep(0.3)
        for secondi in (30, 60, 90, 20, 100, 45, 75, 5):
            inizio = secondi * sorgente.al_secondo
            assert _esatti(sorgente, INTESTAZIONE + inizio, 4096, sorgente.nuova_richiesta()) == _veloce(inizio, 4096)
            # Il convertitore riempie la finestra e resta fermo a scrivere.
            time.sleep(0.2)
        assert sorgente.ripartenze == 8
    finally:
        sorgente.chiudi()
    scadenza = time.monotonic() + 2 * _Ostinato.ATTESA
    while time.monotonic() < scadenza and (_vivi("MeTeOra, fine del WAV in RAM") or _vivi("convertitore ostinato")):
        time.sleep(0.05)
    assert convertitore.bloccati == 0 and convertitore.tornati == 9
    assert not _vivi("MeTeOra, fine del WAV in RAM") and not _vivi("convertitore ostinato")


def test_la_diretta_chiusa_senza_leggere_ferma_il_convertitore():
    # Lo stesso per l'audio delle TV convertito dal vivo (3.12.0): chiusa la
    # lettura, nessuno vuota piu' la pipe, e la si chiude prima di fermare
    # libmpv (15 novembre 2026).
    convertitore = _Ostinato()
    flusso = wav_in_ram.FlussoPcm(convertitore.dal_vivo)
    assert flusso.read(100).startswith(b"RIFF")
    dati = flusso.read(65536)
    assert dati and dati == _veloce(0, len(dati))
    time.sleep(0.3)
    inizio = time.monotonic()
    flusso.close()
    scadenza = time.monotonic() + 2 * _Ostinato.ATTESA
    while time.monotonic() < scadenza and not (convertitore.tornati or convertitore.bloccati):
        time.sleep(0.05)
    assert convertitore.tornati == 1 and convertitore.bloccati == 0 and time.monotonic() - inizio < _Ostinato.ATTESA
    assert flusso.read(10) == b""


def test_chiusa_non_da_piu_niente():
    sorgente = SorgenteWav(_Convertitore(5 * 48000 * 4), 5.0, finestra=4 * 2**20)
    richiesta = sorgente.nuova_richiesta()
    sorgente.chiudi()
    assert sorgente.leggi(INTESTAZIONE, 1000, richiesta) is None


@pytest.fixture(autouse=True)
def _nessuna_pipe_appesa():
    """I fili delle pipe sono demoni: una prova che li lascia appesi non
    ferma pytest, ma qui si controlla che finiscano."""
    prima = {f for f in threading.enumerate() if f.name.startswith("MeTeOra, WAV in RAM")}
    yield
    scadenza = time.monotonic() + 5
    while time.monotonic() < scadenza:
        rimasti = {f for f in threading.enumerate() if f.name.startswith("MeTeOra, WAV in RAM")} - prima
        if not rimasti:
            return
        time.sleep(0.05)
    raise AssertionError(f"fili della pipe rimasti: {len(rimasti)}")


# La diretta convertita dal vivo per lo speaker (3.12.0).

class _DalVivo:
    """avvia(uscita, alla_fine) come il convertitore dal vivo della finestra:
    scrive nella pipe quanti byte riconoscibili, poi, se aspetta, resta
    aperto finche' terminate() non lo ferma, come una TV che va avanti."""

    def __init__(self, quanti, aspetta=False):
        self.quanti, self.aspetta = quanti, aspetta
        self.fermo = threading.Event()
        self.finito = threading.Event()

    def __call__(self, uscita, alla_fine):
        def scrivi():
            try:
                with open(uscita, "wb", buffering=0) as pipe:
                    pipe.writelines(_atteso(inizio, min(4096, self.quanti - inizio)) for inizio in range(0, self.quanti, 4096))
                    if self.aspetta:
                        self.fermo.wait(10)
            except OSError:
                pass
            finally:
                self.finito.set()
                alla_fine()

        threading.Thread(target=scrivi, daemon=True).start()
        return type("Lettore", (), {"terminate": lambda _self: self.fermo.set()})()


def _letto(flusso):
    letti = bytearray()
    while True:
        pezzo = flusso.read(5000)
        if not pezzo:
            return bytes(letti)
        letti += pezzo


def test_la_diretta_dal_vivo_e_un_wav_senza_fine():
    flusso = wav_in_ram.FlussoPcm(_DalVivo(20000))
    dati = _letto(flusso)
    flusso.close()
    testa, pcm = dati[:INTESTAZIONE], dati[INTESTAZIONE:]
    # Un WAV lungo quanto il WAV sa dire, a 48 kHz, 16 bit e stereo.
    assert testa[:4] == b"RIFF" and testa[8:16] == b"WAVEfmt " and testa[36:40] == b"data"
    totale = struct.unpack("<I", testa[40:44])[0]
    assert totale % 4 == 0 and totale > 6 * 3600 * 48000 * 4 and struct.unpack("<I", testa[24:28])[0] == 48000
    assert pcm == _atteso(0, 20000) and flusso.scritti == 20000 and flusso.tipo == "audio/wav"


def test_close_ferma_la_diretta_dal_vivo_che_aspetta():
    convertitore = _DalVivo(4096, aspetta=True)
    flusso = wav_in_ram.FlussoPcm(convertitore)
    assert flusso.read(100).startswith(b"RIFF") and flusso.read(4096) == _atteso(0, 4096)
    letti = []
    filo = threading.Thread(target=lambda: letti.append(flusso.read(4096)))
    filo.start()
    time.sleep(0.2)
    inizio = time.monotonic()
    flusso.close()
    filo.join(5)
    assert not filo.is_alive() and letti == [b""] and time.monotonic() - inizio < 2
    assert convertitore.finito.wait(5) and flusso.read(10) == b""


def test_la_diretta_gia_scritta_e_chiusa_si_legge_lo_stesso():
    # Il convertitore ha scritto tutto e chiuso prima della prima lettura:
    # ConnectNamedPipe da' ERROR_NO_DATA, e i byte ci sono ancora (3.12.0).
    convertitore = _DalVivo(10000)
    flusso = wav_in_ram.FlussoPcm(convertitore)
    assert convertitore.finito.wait(5)
    time.sleep(0.1)
    assert _letto(flusso)[INTESTAZIONE:] == _atteso(0, 10000)
    flusso.close()
