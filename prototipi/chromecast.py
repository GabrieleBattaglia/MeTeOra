# MeTeOra, prototipi: il Chromecast e le strade della tappa 15 b, da misurare a casa.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 22/10/2026: nasce con la tappa 15 b del piano, prima di toccare il programma; poi ricerca, server e connessione passano a trasmissione.py, la parte comune.

"""Il prototipo del Chromecast: trova gli apparecchi, prova le strade e
misura quanto tardano.

Le strade, dal piano:
  A, mandare il brano: il server di trasmissione.py da' il file, il
     Chromecast lo scarica e lo suona da se', e il prototipo fa da
     telecomando.
  A convertita: come A, ma il brano si converte prima in FLAC con libmpv,
     che lo fa in un attimo: provato in ufficio, 20 secondi in 0,09 secondi.
     E' la strada per i formati che il Chromecast non legge.
  B, trasmettere l'uscita: il brano, reso in memoria da libmpv come lo
     suonerebbe MeTeOra, va al Chromecast come un flusso WAV senza fine, al
     ritmo dell'orologio, come una radio; pausa e salti li fa il PC.
Ricerca, server e connessione sono quelli di trasmissione.py, la parte
comune che MeTeOra usera': provando il prototipo si prova anche lei.
Le misure sono due. Quella dell'apparecchio, solo per la strada A: quanto
passa fra il comando e la risposta del Chromecast. Quella dell'orecchio, per
tutte: dopo ogni comando si preme Spazio appena se ne sente l'effetto, e al
tempo si tolgono i riflessi, misurati prima con cinque bip del PC.
Il dettaglio va in coda a prototipi/chromecast_misure.txt, con la data e la
macchina, anche le richieste che il Chromecast fa al server; a schermo solo
i riassunti.
Serve pychromecast, che sta in requirements.txt. La prima volta che il
server parte Windows chiede il permesso del firewall: va dato per le reti
private, o il Chromecast non arriva al PC.
Uso: python prototipi/chromecast.py [--anticipo SECONDI] [--porta NUMERO]
L'anticipo e' quanto la strada B manda avanti rispetto all'orologio, mezzo
secondo di partenza: piu' e' grande, piu' tardano i comandi.
"""

import argparse
import datetime
import os
import random
import socket
import statistics
import struct
import tempfile
import threading
import time

import ambiente  # noqa: F401

# isort: split
import trasmissione

QUI = os.path.dirname(os.path.abspath(__file__))
FILE_DELLE_MISURE = os.path.join(QUI, "chromecast_misure.txt")
PORTA = 8765
FREQUENZA = 44100
CANALI = 2
BYTE_PER_CAMPIONE = 2
BYTE_PER_FRAME = CANALI * BYTE_PER_CAMPIONE
# I pezzi della strada B: 20 millesimi di secondo.
FRAME_PER_PEZZO = FREQUENZA // 50
ATTESA_DELLA_RICERCA = 8.0
SECONDI_DEL_SALTO = 10
PASSO_DEL_VOLUME = 0.05
# La strada B tiene il brano in memoria: cinque minuti sono 53 MB.
MASSIMO_DELLA_STRADA_B = 300
# La prova dei formati: quanto si aspetta che un file parta, e quanto lo si
# ascolta per dire che suona davvero.
ATTESA_DELLA_PARTENZA = 10.0
ASCOLTO_DELLA_PROVA = 3.0
NOMI_DEI_TIPI = {trasmissione.TIPO_SOLO_AUDIO: "solo audio", trasmissione.TIPO_GRUPPO: "gruppo", trasmissione.TIPO_AUDIO_E_VIDEO: "audio e video"}


class Registro:
    """Le righe del file delle misure, e le misure raccolte per i riassunti."""

    def __init__(self):
        self.misure = {}
        self._blocco = threading.Lock()
        self.scrivi(f"Sessione del {datetime.datetime.now():%d/%m/%Y alle %H:%M} su {socket.gethostname()}.")

    def scrivi(self, testo):
        with self._blocco, open(FILE_DELLE_MISURE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now():%H:%M:%S} {testo}\n")

    def misura(self, nome, secondi):
        self.misure.setdefault(nome, []).append(secondi)
        self.scrivi(f"Misura, {nome}: {secondi:.3f} s.")

    def riassunto(self):
        """Una riga per misura: quante, la mediana, la piu' breve e la piu' lunga."""
        righe = []
        for nome, valori in self.misure.items():
            if len(valori) == 1:
                righe.append(f"{nome}: {valori[0]:.2f} s.")
            else:
                righe.append(f"{nome}: {len(valori)} misure, mediana {statistics.median(valori):.2f} s, da {min(valori):.2f} a {max(valori):.2f}.")
        return righe


def dice(testo):
    print(testo, flush=True)


def tasto(prompt, attesa=None):
    from GBUtils import key

    return key(prompt, attesa=attesa, alla_scadenza=None)


def svuota_la_tastiera():
    """I tasti premuti prima del tempo non devono valere come risposta."""
    while tasto("", attesa=0) is not None:
        pass


# La strada B: il flusso.

class Flusso:
    """Il brano in memoria, s16 stereo a 44100, mandato come un WAV senza fine
    al ritmo dell'orologio, con anticipo secondi di vantaggio. In pausa si
    manda silenzio, perche' un flusso che si ferma il Chromecast lo chiude.
    Una connessione nuova prende il posto della vecchia."""

    def __init__(self, pcm, anticipo):
        self.pcm = pcm
        self.frame = len(pcm) // BYTE_PER_FRAME
        self.anticipo = anticipo
        self.posizione = 0
        self.pausa = False
        self._blocco = threading.Lock()
        self._connessione = 0

    @staticmethod
    def intestazione():
        # Le dimensioni al massimo: per chi legge, il WAV non finisce mai.
        senza_fine = 0xFFFFFFFF
        return (b"RIFF" + struct.pack("<I", senza_fine) + b"WAVE" + b"fmt " + struct.pack("<IHHIIHH", 16, 1, CANALI, FREQUENZA,
                FREQUENZA * BYTE_PER_FRAME, BYTE_PER_FRAME, BYTE_PER_CAMPIONE * 8) + b"data" + struct.pack("<I", senza_fine))

    def servi(self, uscita):
        with self._blocco:
            self._connessione += 1
            mia = self._connessione
        uscita.write(self.intestazione())
        partenza = time.perf_counter()
        mandati = 0
        silenzio = bytes(FRAME_PER_PEZZO * BYTE_PER_FRAME)
        while True:
            dovuti = int((time.perf_counter() - partenza + self.anticipo) * FREQUENZA)
            pezzi = []
            with self._blocco:
                if mia != self._connessione:
                    return
                while mandati < dovuti:
                    quanti = min(FRAME_PER_PEZZO, dovuti - mandati)
                    if self.pausa or self.posizione >= self.frame:
                        pezzi.append(silenzio[:quanti * BYTE_PER_FRAME])
                    else:
                        presi = min(quanti, self.frame - self.posizione)
                        inizio = self.posizione * BYTE_PER_FRAME
                        pezzi.append(self.pcm[inizio:inizio + presi * BYTE_PER_FRAME] + silenzio[:(quanti - presi) * BYTE_PER_FRAME])
                        self.posizione += presi
                    mandati += quanti
            if pezzi:
                uscita.write(b"".join(pezzi))
            time.sleep(0.01)

    def pausa_o_ripresa(self):
        with self._blocco:
            self.pausa = not self.pausa
            return "pausa" if self.pausa else "ripresa"

    def salta(self, secondi):
        with self._blocco:
            self.posizione = max(0, min(self.frame, self.posizione + int(secondi * FREQUENZA)))


# Gli apparecchi.

def nome_del_tipo(voce):
    """Il tipo da leggere; la ricerca a volte non lo sa ancora, e lo dice la
    connessione."""
    return NOMI_DEI_TIPI.get(voce["tipo"], voce["tipo"] or "tipo non ancora noto")


def cerca(registro):
    """La ricerca di trasmissione.py, avviata, e gli apparecchi visti in
    ATTESA_DELLA_RICERCA secondi, con il tempo in cui si e' visto ciascuno."""
    partenza = time.perf_counter()
    visti = {}
    ricerca = None

    def al_cambio():
        for voce in ricerca.apparecchi():
            visti.setdefault(voce["uuid"], time.perf_counter() - partenza)

    ricerca = trasmissione.Ricerca(al_cambio=al_cambio)
    ricerca.avvia()
    dice(f"Cerco gli apparecchi Cast per {ATTESA_DELLA_RICERCA:.0f} secondi.")
    time.sleep(ATTESA_DELLA_RICERCA)
    apparecchi = ricerca.apparecchi()
    for voce in apparecchi:
        quando = visti.get(voce["uuid"])
        registro.scrivi(f"Trovato dopo {quando if quando is not None else '?'} s: {voce['nome']}, {voce['modello']}, {voce['produttore']}, "
                        f"{nome_del_tipo(voce)}, {voce['indirizzo']}:{voce['porta']}.")
        if quando is not None:
            registro.misura("ricerca, primo avviso di ogni apparecchio", quando)
    return apparecchi, ricerca


class Collegato:
    """L'apparecchio di trasmissione.py, con gli stati annotati e l'istante
    in cui arrivano, per misurare."""

    def __init__(self, ricerca, voce, registro):
        self.stati = []
        self.registro = registro
        partenza = time.perf_counter()
        self.apparecchio = ricerca.connetti(voce["uuid"], allo_stato=self._stato)
        registro.misura("connessione", time.perf_counter() - partenza)

    def _stato(self, stato):
        self.stati.append((time.perf_counter(), stato))
        self.registro.scrivi(f"Stato: {stato}.")

    def aspetta(self, da, voluti, limite):
        """I secondi da da al primo stato fra voluti, o None; si ferma prima
        se l'apparecchio si ferma per un errore."""
        fine = time.perf_counter() + limite
        while time.perf_counter() < fine:
            for quando, stato in list(self.stati):
                if quando < da:
                    continue
                if stato["stato"] in voluti:
                    return quando - da
                if stato["stato"] == trasmissione.FERMO and stato["motivo"] == "ERROR":
                    return None
            time.sleep(0.02)
        return None


# Le misure.

def misura_i_riflessi(registro):
    """La mediana di cinque risposte a un bip del PC, che poi si toglie dalle
    misure dell'orecchio. Comprende anche il ritardo della scheda del PC,
    qualche decina di millesimi."""
    import numpy
    from GBUtils import Acusticator

    dice("I riflessi: cinque bip dal PC, a intervalli casuali. Premi Spazio appena senti ciascun bip.")
    # Un attimo di silenzio apre la scheda: il primo bip non paga l'apertura.
    Acusticator.riproduci(numpy.zeros((441, 2), dtype=numpy.float32))
    tasto("\rPremi un tasto per cominciare.\r")
    tempi = []
    for _ in range(5):
        time.sleep(random.uniform(1.5, 3.5))  # noqa: S311 - l'intervallo fra due bip non e' un segreto
        svuota_la_tastiera()
        partenza = time.perf_counter()
        Acusticator(["a5", 0.08, 0, 0.5])
        if tasto("", attesa=5) == " ":
            tempi.append(time.perf_counter() - partenza)
    if not tempi:
        dice("Nessuna risposta: tengo un quarto di secondo.")
        return 0.25
    riflessi = statistics.median(tempi)
    registro.misura("riflessi", riflessi)
    dice(f"Riflessi: {riflessi:.2f} s, mediana di {len(tempi)} risposte.")
    return riflessi


def ascolta(registro, nome, partenza, riflessi):
    """Aspetta Spazio, al massimo trenta secondi, e misura dall'istante
    partenza; Esc o un altro tasto rinunciano."""
    risposta = tasto("\rSpazio appena senti; un altro tasto se non senti niente.\r", attesa=30)
    if risposta != " ":
        registro.scrivi(f"{nome}: nessuna risposta dell'orecchio ({risposta!r}).")
        dice(f"{nome}: non misurato.")
        return
    ritardo = time.perf_counter() - partenza - riflessi
    registro.misura(nome, ritardo)
    dice(f"{nome}: {ritardo:.2f} s.")


GUIDA_DEI_COMANDI = "P pausa e ripresa, A indietro e D avanti di 10 secondi, meno e piu' il volume, X basta."


def telecomando(registro, riflessi, strada, comandi):
    """I comandi di una strada, ciascuno misurato con l'orecchio, e per la
    strada A anche con la risposta dell'apparecchio. comandi e' un dizionario
    tasto -> funzione che restituisce il nome del comando."""
    dice(GUIDA_DEI_COMANDI)
    while True:
        scelta = tasto("\rComando: P, A, D, meno, piu', X.\r")
        if scelta in ("x", "X", "\x1b"):
            return
        funzione = comandi.get(scelta.lower() if isinstance(scelta, str) else scelta)
        if funzione is None:
            dice(GUIDA_DEI_COMANDI)
            continue
        svuota_la_tastiera()
        partenza = time.perf_counter()
        try:
            nome = funzione()
        except Exception as e:  # noqa: BLE001 - un comando che non va si dice e si annota, e il prototipo prosegue
            registro.scrivi(f"Strada {strada}, comando non riuscito: {e!r}.")
            dice(f"Comando non riuscito: {e}.")
            continue
        risposta = time.perf_counter() - partenza
        if strada.startswith("A"):
            registro.misura(f"strada {strada}, risposta dell'apparecchio, {nome}", risposta)
        ascolta(registro, f"strada {strada}, orecchio, {nome}", partenza, riflessi)


def volume_di(apparecchio, delta):
    apparecchio.volume = (apparecchio.volume or 0.0) + delta
    return f"volume {'su' if delta > 0 else 'giu'}"


def converti_in_flac(percorso, cartella, registro):
    """Il brano convertito in FLAC da libmpv, nella cartella temporanea: il
    percorso del file nuovo, o None se la conversione non va."""
    import mpv

    from motore import OPZIONI_DI_BASE

    uscita = os.path.join(cartella, f"conversione_{len(os.listdir(cartella)) + 1}.flac")
    partenza = time.perf_counter()
    try:
        lettore = mpv.MPV(**{**OPZIONI_DI_BASE, "o": uscita, "of": "flac", "oac": "flac"})
        try:
            lettore.play(percorso)
            lettore.wait_for_playback(timeout=300)
        finally:
            lettore.terminate()
    except Exception as e:  # noqa: BLE001 - libmpv fallisce in molti modi: per la prova vuol dire che non converte
        registro.scrivi(f"Conversione in FLAC non riuscita per {percorso}: {e!r}.")
        return None
    if not os.path.isfile(uscita) or not os.path.getsize(uscita):
        registro.scrivi(f"Conversione in FLAC vuota per {percorso}.")
        return None
    registro.misura("conversione in FLAC", time.perf_counter() - partenza)
    return uscita


def strada_a(collegato, server, registro, riflessi, cartella=None):
    """Manda un brano scelto e lo comanda; con cartella, prima lo converte in
    FLAC li' dentro."""
    apparecchio = collegato.apparecchio
    percorso = input("Percorso del brano da mandare: ").strip().strip('"')
    if not os.path.isfile(percorso):
        dice("Il file non c'e'.")
        return
    strada = "A"
    if cartella is not None:
        dice("Converto il brano in FLAC.")
        convertito = converti_in_flac(percorso, cartella, registro)
        if convertito is None:
            dice("La conversione non e' riuscita: il file forse non si apre.")
            return
        dice(f"Convertito in {registro.misure['conversione in FLAC'][-1]:.1f} s.")
        percorso, strada = convertito, "A convertita"
    indirizzo = server.pubblica_file(percorso)
    registro.scrivi(f"Strada {strada}: {percorso}, servito come {indirizzo}, tipo {trasmissione.tipo_di(percorso)}.")
    svuota_la_tastiera()
    partenza = time.perf_counter()
    apparecchio.suona(indirizzo, trasmissione.tipo_di(percorso), titolo=os.path.basename(percorso))
    dice("Mandato: premi Spazio appena senti la musica.")
    ascolta(registro, f"strada {strada}, orecchio, avvio", partenza, riflessi)
    avvio = collegato.aspetta(partenza, (trasmissione.IN_RIPRODUZIONE,), ATTESA_DELLA_PARTENZA)
    if avvio is None:
        dice("Il Chromecast non dice di suonare: il file forse non lo legge. Guarda il file delle misure.")
        return
    registro.misura(f"strada {strada}, avvio riferito dall'apparecchio", avvio)

    def pausa_o_ripresa():
        stato = apparecchio.stato
        if stato and stato["stato"] == trasmissione.IN_PAUSA:
            apparecchio.riprendi()
            return "ripresa"
        apparecchio.pausa()
        return "pausa"

    def salto(secondi):
        apparecchio.vai_a((apparecchio.posizione or 0.0) + secondi)
        return "avanti" if secondi > 0 else "indietro"

    telecomando(registro, riflessi, strada, {
        "p": pausa_o_ripresa, "a": lambda: salto(-SECONDI_DEL_SALTO), "d": lambda: salto(SECONDI_DEL_SALTO),
        "-": lambda: volume_di(apparecchio, -PASSO_DEL_VOLUME), "+": lambda: volume_di(apparecchio, PASSO_DEL_VOLUME),
    })
    apparecchio.ferma()


def file_per_estensione(cartella, limite=20000):
    """Un file per ogni estensione di trasmissione.TIPI, il primo che si
    trova, guardando al piu' limite file."""
    scelti, visti = {}, 0
    for radice, _cartelle, nomi in os.walk(cartella):
        for nome in sorted(nomi):
            estensione = os.path.splitext(nome)[1].lower()
            if estensione in trasmissione.TIPI and estensione not in scelti:
                scelti[estensione] = os.path.join(radice, nome)
            visti += 1
            if visti >= limite or len(scelti) == len(trasmissione.TIPI):
                return scelti
    return scelti


def suona_per_prova(collegato, server, percorso):
    """Manda un file, aspetta che suoni e lo ascolta qualche secondo: vero e
    i secondi della partenza se la posizione e' andata avanti, falso e il
    motivo se no."""
    apparecchio = collegato.apparecchio
    partenza = time.perf_counter()
    apparecchio.suona(server.pubblica_file(percorso), trasmissione.tipo_di(percorso), titolo=os.path.basename(percorso))
    avvio = collegato.aspetta(partenza, (trasmissione.IN_RIPRODUZIONE,), ATTESA_DELLA_PARTENZA)
    if avvio is None:
        esito = (False, "non suona")
    else:
        time.sleep(ASCOLTO_DELLA_PROVA)
        richiesta = time.perf_counter()
        apparecchio.aggiorna()
        collegato.aspetta(richiesta, (trasmissione.IN_RIPRODUZIONE, trasmissione.IN_PAUSA, trasmissione.IN_CARICAMENTO, trasmissione.FERMO), 2)
        stato = apparecchio.stato or {}
        va = stato.get("stato") == trasmissione.IN_RIPRODUZIONE and (stato.get("posizione") or 0) > 1
        esito = (True, f"partito in {avvio:.2f} s") if va else (False, f"parte ma si ferma ({stato.get('stato')})")
    fermo = time.perf_counter()
    apparecchio.ferma()
    collegato.aspetta(fermo, (trasmissione.FERMO,), 5)
    return esito


def prova_dei_formati(collegato, server, registro, cartella_temporanea):
    """Un file per estensione: si manda e si ascolta qualche secondo; se non
    suona, si riprova convertito in FLAC."""
    cartella = input("Cartella della musica da cui prendere un file per formato: ").strip().strip('"')
    if not os.path.isdir(cartella):
        dice("La cartella non c'e'.")
        return
    scelti = file_per_estensione(cartella)
    dice(f"Formati trovati: {len(scelti)}. Ognuno suona qualche secondo.")
    esiti = []
    for estensione, percorso in sorted(scelti.items()):
        va, come = suona_per_prova(collegato, server, percorso)
        esito = f"suona, {come}" if va else come
        if not va:
            convertito = converti_in_flac(percorso, cartella_temporanea, registro)
            if convertito is None:
                esito += ", e non si converte"
            else:
                va, come = suona_per_prova(collegato, server, convertito)
                esito += f"; convertito in FLAC in {registro.misure['conversione in FLAC'][-1]:.1f} s suona, {come}" if va else f"; convertito in FLAC {come}"
        atteso = "lo legge da se'" if trasmissione.legge_da_se(percorso) else "da convertire"
        riga = f"{estensione[1:].upper()}, per Google {atteso}: {esito}, {os.path.basename(percorso)}."
        esiti.append(riga)
        registro.scrivi(f"Formato, {riga}")
        dice(riga)
    registro.scrivi(f"Formati: {'; '.join(esiti)}")


def rendi_in_memoria(percorso, massimo):
    """Il brano reso da libmpv come s16 stereo a 44100, al piu' massimo
    secondi: l'uscita su file di mpv rende tutto d'un fiato."""
    import mpv

    from motore import OPZIONI_DI_BASE

    with tempfile.TemporaryDirectory() as cartella:
        uscita = os.path.join(cartella, "resa.raw")
        lettore = mpv.MPV(**{**OPZIONI_DI_BASE, "ao": "pcm", "ao_pcm_file": uscita, "ao_pcm_waveheader": False, "audio_format": "s16",
                             "audio_samplerate": FREQUENZA, "audio_channels": "stereo", "end": str(massimo)})
        try:
            lettore.play(percorso)
            lettore.wait_for_playback(timeout=120)
        finally:
            lettore.terminate()
        with open(uscita, "rb") as f:
            return f.read()


def strada_b(collegato, server, registro, riflessi, anticipo):
    """Rende un brano in memoria e lo trasmette come flusso continuo."""
    apparecchio = collegato.apparecchio
    percorso = input("Percorso del brano da trasmettere: ").strip().strip('"')
    if not os.path.isfile(percorso):
        dice("Il file non c'e'.")
        return
    dice("Rendo il brano in memoria.")
    partenza = time.perf_counter()
    pcm = rendi_in_memoria(percorso, MASSIMO_DELLA_STRADA_B)
    secondi = len(pcm) / (FREQUENZA * BYTE_PER_FRAME)
    if not secondi:
        dice("libmpv non ha reso niente: il file forse non si apre.")
        return
    registro.scrivi(f"Strada B: {percorso}, {secondi:.1f} s resi in {time.perf_counter() - partenza:.1f} s, anticipo {anticipo} s.")
    flusso = Flusso(pcm, anticipo)
    indirizzo = server.pubblica_flusso("uscita.wav", flusso.servi, "audio/wav")
    svuota_la_tastiera()
    partenza = time.perf_counter()
    apparecchio.suona(indirizzo, "audio/wav", titolo=f"MeTeOra, {os.path.basename(percorso)}", in_diretta=True)
    dice("Trasmesso: premi Spazio appena senti la musica.")
    ascolta(registro, "strada B, orecchio, avvio", partenza, riflessi)
    avvio = collegato.aspetta(partenza, (trasmissione.IN_RIPRODUZIONE,), ATTESA_DELLA_PARTENZA)
    if avvio is None:
        dice("Il Chromecast non dice di suonare il flusso. Guarda il file delle misure.")
    else:
        registro.misura("strada B, avvio riferito dall'apparecchio", avvio)

    def salto(secondi):
        flusso.salta(secondi)
        return "avanti" if secondi > 0 else "indietro"

    telecomando(registro, riflessi, "B", {
        "p": flusso.pausa_o_ripresa, "a": lambda: salto(-SECONDI_DEL_SALTO), "d": lambda: salto(SECONDI_DEL_SALTO),
        "-": lambda: volume_di(apparecchio, -PASSO_DEL_VOLUME), "+": lambda: volume_di(apparecchio, PASSO_DEL_VOLUME),
    })
    apparecchio.ferma()


def scegli(apparecchi):
    for numero, voce in enumerate(apparecchi, 1):
        dice(f"{numero}. {voce['nome']}, {voce['modello']}, {nome_del_tipo(voce)}, {voce['indirizzo']}.")
    risposta = input("Numero dell'apparecchio, Invio per nessuno: ").strip()
    if risposta.isdigit() and 1 <= int(risposta) <= len(apparecchi):
        return apparecchi[int(risposta) - 1]
    return None


def principale():
    parametri = argparse.ArgumentParser(description="Il prototipo del Chromecast di MeTeOra.")
    parametri.add_argument("--anticipo", type=float, default=0.5, help="i secondi di vantaggio del flusso della strada B")
    parametri.add_argument("--porta", type=int, default=PORTA, help="la porta del server sul PC")
    argomenti = parametri.parse_args()
    if not trasmissione.disponibile():
        dice("Manca pychromecast: installalo con python -m pip install -r requirements.txt e rilancia il prototipo.")
        return
    from importlib.metadata import version

    registro = Registro()
    registro.scrivi(f"pychromecast {version('pychromecast')}, anticipo {argomenti.anticipo} s, porta {argomenti.porta}.")
    apparecchi, ricerca = cerca(registro)
    if not apparecchi:
        dice("Nessun apparecchio Cast sulla rete. Controlla che il PC e gli speaker siano sulla stessa rete, non quella degli ospiti.")
        ricerca.ferma()
        return
    dice(f"Apparecchi trovati: {len(apparecchi)}.")
    collegato = server = None
    riflessi = 0.25
    # I file convertiti in FLAC, che spariscono all'uscita; un file ancora
    # aperto dal server non deve fermare l'uscita.
    conversioni = tempfile.TemporaryDirectory(prefix="meteora_chromecast_", ignore_cleanup_errors=True)
    try:
        voce = scegli(apparecchi)
        if voce is None:
            return
        dice(f"Mi collego a {voce['nome']}.")
        collegato = Collegato(ricerca, voce, registro)
        server = trasmissione.Server(trasmissione.indirizzo_verso(voce["indirizzo"]), argomenti.porta, al_registro=lambda t: registro.scrivi(f"Server, {t}"))
        volume = collegato.apparecchio.volume
        registro.scrivi(f"Apparecchio: {voce['nome']}, {voce['modello']}, tipo {collegato.apparecchio.tipo}; server su {server.base}; volume {volume}.")
        dice(f"Collegata a {voce['nome']}, volume {round(volume * 100) if volume is not None else '?'}. Il server e' su {server.base}.")
        while True:
            scelta = tasto("\rR riflessi, A manda il brano, C manda convertito in FLAC, F formati, B trasmetti l'uscita, Q esci.\r")
            scelta = scelta.lower() if isinstance(scelta, str) else scelta
            if scelta in ("q", "\x1b"):
                break
            try:
                if scelta == "r":
                    riflessi = misura_i_riflessi(registro)
                elif scelta == "a":
                    strada_a(collegato, server, registro, riflessi)
                elif scelta == "c":
                    strada_a(collegato, server, registro, riflessi, cartella=conversioni.name)
                elif scelta == "f":
                    prova_dei_formati(collegato, server, registro, conversioni.name)
                elif scelta == "b":
                    strada_b(collegato, server, registro, riflessi, argomenti.anticipo)
            except Exception as e:  # noqa: BLE001 - nel collaudo un guasto si annota e si va avanti, invece di perdere la sessione
                registro.scrivi(f"Guasto nella scelta {scelta!r}: {e!r}.")
                dice(f"Non riuscito: {e}. Il dettaglio e' nel file delle misure.")
    finally:
        if collegato is not None:
            collegato.apparecchio.chiudi()
        if server is not None:
            server.ferma()
        ricerca.ferma()
        conversioni.cleanup()
        righe = registro.riassunto()
        for riga in righe:
            registro.scrivi(f"Riassunto, {riga}")
        dice("Riassunto:" if righe else "Nessuna misura.")
        for riga in righe:
            dice(riga)
        dice(f"Il dettaglio e' in {FILE_DELLE_MISURE}.")


if __name__ == "__main__":
    principale()
