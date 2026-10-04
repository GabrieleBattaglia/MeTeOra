# MeTeOra, i sottotitoli fatti di immagini: le tracce dei DVD e dei Blu-ray, e quelli impressi nel video.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.80.0, dalla tappa 10 (punti a e b), con le decisioni di Gabriele del 4 ottobre 2026.

"""La lettura dei sottotitoli che non sono testo, con il riconoscimento di ocr.

Tre lavori, ciascuno nel suo filo, mai in quello della finestra:
- LetturaDelleImmagini: una traccia a immagini, VobSub o PGS. libmpv avvisa
  quando un sottotitolo comincia (sub-start); allora si fotografa il
  fotogramma con e senza sottotitoli, e la differenza si legge.
- LetturaDegliImpressi: i sottotitoli impressi nel video, letti al volo. Un
  paio di volte al secondo si guarda la fascia in basso; quando cambia si
  legge, e il testo si dice quando due letture di fila danno lo stesso:
  uno sfondo chiaro in movimento cambia la fascia sempre, ma non il testo.
  Si dicono solo le righe nuove: un logo fisso si sente una volta sola.
- PassataDegliImpressi: la passata in anticipo. Un libmpv tutto suo, senza
  audio, percorre il video a cinque volte il tempo reale; ogni mezzo secondo si legge la
  fascia, e alla fine un file .srt accanto al video raccoglie i sottotitoli,
  senza le scritte che restano ferme piu' di DURATA_MASSIMA secondi.
Chi parla, cioe' la sintesi e la console, sta fuori: dici(testo).
"""

import os
import threading
import time
import traceback

# Prima di mpv: rende visibili le DLL di libmpv.
import librerie  # noqa: F401
import ocr
from formati import testo_srt

# Le tracce di sottotitoli fatte di immagini, come le chiama mpv.
CODEC_A_IMMAGINI = frozenset({"dvd_subtitle", "hdmv_pgs_subtitle", "dvb_subtitle", "xsub", "dvb_teletext"})
# Ogni quanto la lettura al volo guarda la fascia in basso.
INTERVALLO_AL_VOLO = 0.4
# Ogni quanti secondi del video la passata legge la fascia.
PASSO_DELLA_PASSATA = 0.5
# Quante volte il tempo reale corre la passata. Senza freno, sul banco, un
# episodio di 55 minuti passava in due, ma con un campione ogni 2.3 secondi
# di video invece che ogni mezzo: i sottotitoli brevi si perdevano. A cinque
# volte una lettura, foto e riconoscimento, sta comoda in un passo.
VELOCITA_DELLA_PASSATA = 5
# Una scritta ferma piu' di cosi' non e' un sottotitolo: un logo, un titolo.
DURATA_MASSIMA = 15.0
# Quante parole servono perche' una lettura sia un sottotitolo: una, perche'
# le battute brevi come Si', No! o Madre? sono sottotitoli veri; contro i
# disturbi c'e' la conferma di due letture uguali (banco della 1.80.0).
PAROLE_MINIME = 1
# Come finisce il nome del file della passata, prima della lingua.
SEGNO_DEL_FILE = ".impressi"


def file_della_passata(video, lingua):
    """Il file .srt che la passata scrive accanto al video:
    film.impressi.it.srt, riconoscibile e diverso dagli altri sottotitoli."""
    return f"{os.path.splitext(video)[0]}{SEGNO_DEL_FILE}.{(lingua or ocr.LINGUA_PREDEFINITA).split('-')[0].lower()}.srt"


def passate_esistenti(video):
    """I file .srt di una passata gia' fatta per il video, in qualsiasi lingua."""
    base = os.path.basename(os.path.splitext(video)[0]) + SEGNO_DEL_FILE + "."
    cartella = os.path.dirname(video) or "."
    try:
        return sorted(os.path.join(cartella, n) for n in os.listdir(cartella) if n.startswith(base) and n.lower().endswith(".srt"))
    except OSError:
        return []


class _Lavoro:
    """Un filo che lavora finche' non lo si ferma."""

    def __init__(self, nome):
        self._fermo = threading.Event()
        self._filo = threading.Thread(target=self._lavora, name=f"MeTeOra, {nome}", daemon=True)

    def avvia(self):
        self._filo.start()
        return self

    def ferma(self):
        self._fermo.set()

    def aspetta(self, secondi=10):
        """Per le prove."""
        self._filo.join(secondi)

    def _lavora(self):
        raise NotImplementedError


class _Lettura(_Lavoro):
    """Una lettura in diretta: un giro che si guasta non ferma la lettura,
    e il primo guasto si dice con guasto(frase), una volta sola."""

    def __init__(self, nome, motore, dici, lingua, guasto=None):
        super().__init__(nome)
        self.lingua = lingua
        self._motore = motore
        self._dici = dici
        self._guasto = guasto
        self._guasti = 0

    def _giro_guasto(self, errore):
        self._guasti += 1
        if self._guasti == 1 and self._guasto is not None:
            self._guasto(f"La lettura dei sottotitoli fatti di immagini ha avuto un problema e prova ad andare avanti: {errore}")


class LetturaDelleImmagini(_Lettura):
    """Una traccia di sottotitoli a immagini letta in diretta: a ogni
    nuovo_sottotitolo, che arriva da libmpv, si fotografa e si legge. Con il
    fotogramma annerito dal motore, a video spento, basta una foto; a video
    acceso servono due foto, con e senza sottotitoli, e la loro differenza."""

    tipo = "immagini"

    def __init__(self, motore, dici, lingua, guasto=None):
        super().__init__("sottotitoli a immagini", motore, dici, lingua, guasto)
        self._nuovo = threading.Event()

    def nuovo_sottotitolo(self):
        self._nuovo.set()

    def ferma(self):
        super().ferma()
        self._nuovo.set()

    def _lavora(self):
        while not self._fermo.is_set():
            self._nuovo.wait()
            self._nuovo.clear()
            if self._fermo.is_set():
                break
            # Il tempo che il sottotitolo nuovo arrivi nel fotogramma.
            time.sleep(0.05)
            try:
                righe = self._leggi()
            except Exception as errore:  # noqa: BLE001 - un giro guasto non ferma la lettura
                self._giro_guasto(errore)
                continue
            if righe and not self._fermo.is_set():
                self._dici(" ".join(righe))

    def _leggi(self):
        if self._motore.video_oscurato:
            foto = self._motore.foto(True)
            return ocr.leggi(ocr.scritte_sul_nero(foto), self.lingua) if foto is not None else []
        con, senza = self._motore.foto(True), self._motore.foto(False)
        if con is None or senza is None:
            return []
        return ocr.leggi(ocr.scritte_della_differenza(con, senza), self.lingua)


class LetturaDegliImpressi(_Lettura):
    """I sottotitoli impressi letti al volo: la fascia in basso, guardata
    ogni INTERVALLO_AL_VOLO secondi mentre il video suona; quando cambia si
    legge, e quando due letture di fila coincidono si dicono le righe nuove."""

    tipo = "impressi"

    def __init__(self, motore, dici, lingua, guasto=None):
        super().__init__("sottotitoli impressi", motore, dici, lingua, guasto)

    def _lavora(self):
        ultima, candidato, da_confermare, dette = None, None, False, []
        while not self._fermo.wait(INTERVALLO_AL_VOLO):
            if self._motore.in_pausa or not self._motore.in_corso:
                continue
            try:
                quadro = self._motore.foto(False)
                if quadro is None:
                    continue
                fascia = ocr.fascia_in_basso(quadro)
                impronta = ocr.impronta(fascia)
                if not ocr.cambiata(ultima, impronta) and not da_confermare:
                    continue
                ultima = impronta
                righe = ocr.leggi(fascia, self.lingua)
            except Exception as errore:  # noqa: BLE001 - un giro guasto non ferma la lettura
                self._giro_guasto(errore)
                continue
            if righe != candidato:
                # Una lettura nuova: si conferma alla prossima occhiata.
                candidato, da_confermare = righe, True
                continue
            da_confermare = False
            nuove = [r for r in righe if r not in dette]
            dette = righe
            if ocr.parole(nuove) >= PAROLE_MINIME and not self._fermo.is_set():
                self._dici(" ".join(nuove))


def senza_scritte_fisse(campioni, durata_massima=DURATA_MASSIMA):
    """I campioni (secondi, righe) senza le righe rimaste ferme, di fila, per
    piu' di durata_massima secondi: loghi, titoli, nomi di canali."""
    fisse = set()
    inizio = {}
    for istante, righe in campioni:
        for riga in righe:
            inizio.setdefault(riga, istante)
        for riga in list(inizio):
            if riga not in righe:
                del inizio[riga]
            elif istante - inizio[riga] > durata_massima:
                fisse.add(riga)
    return [(istante, tuple(r for r in righe if r not in fisse)) for istante, righe in campioni]


def segmenti(campioni, fine, somiglianza=0.75):
    """I sottotitoli (inizio, fine, testo) dai campioni (secondi, righe) in
    ordine di tempo: un sottotitolo per ogni tratto di campioni di fila con
    un testo simile, perche' lo stesso sottotitolo letto in due fotogrammi
    puo' differire di una lettera; il testo e' la lettura piu' frequente del
    tratto. Finisce al campione dopo l'ultimo del tratto, o a fine."""
    import difflib
    from collections import Counter

    tratti = []
    for indice, (istante, righe) in enumerate(campioni):
        dopo = campioni[indice + 1][0] if indice + 1 < len(campioni) else fine
        testo = "\n".join(righe)
        if not righe or ocr.parole(righe) < PAROLE_MINIME:
            continue
        ultimo = tratti[-1] if tratti else None
        if ultimo and ultimo["fine"] == istante and difflib.SequenceMatcher(None, ultimo["letture"][-1], testo).ratio() >= somiglianza:
            ultimo["fine"] = dopo
            ultimo["letture"].append(testo)
            continue
        tratti.append({"inizio": istante, "fine": dopo, "letture": [testo]})
    return [(t["inizio"], t["fine"], Counter(t["letture"]).most_common(1)[0][0]) for t in tratti]


class PassataDegliImpressi(_Lavoro):
    """La passata in anticipo su un video: avanza(percentuale) ogni tanto,
    finita(percorso del file scritto, o None se non c'e' niente da scrivere,
    o un errore come testo) alla fine; dal filo della passata."""

    tipo = "passata"

    def __init__(self, video, lingua, avanza, finita, crea_lettore=None):
        super().__init__("passata dei sottotitoli impressi")
        self.velocita = VELOCITA_DELLA_PASSATA
        self.video = video
        self.lingua = lingua
        self._avanza = avanza
        self._finita = finita
        self._crea_lettore = crea_lettore or _lettore_della_passata
        # I campioni (secondi, righe) letti fin qui: le prove li guardano; e
        # quanti non si sono potuti leggere.
        self.campioni = []
        self.campioni_persi = 0

    def _lavora(self):
        try:
            esito = self._passa()
        except Exception as errore:  # noqa: BLE001 - torna a chi aspetta come frase
            traceback.print_exc()
            motivo = f": {errore.strerror}" if isinstance(errore, OSError) and errore.strerror else ""
            esito = f"La passata dei sottotitoli impressi di {os.path.basename(self.video)} si è fermata per un errore{motivo}."
        if not self._fermo.is_set():
            self._finita(esito)

    def _passa(self):
        percorso = file_della_passata(self.video, self.lingua)
        # Si prova a scrivere prima di cominciare: scoprirlo dopo undici
        # minuti di passata farebbe buttare via tutto.
        try:
            with open(percorso + ".prova", "w", encoding="utf-8"):
                pass
            os.remove(percorso + ".prova")
        except OSError:
            return f"La passata dei sottotitoli impressi non parte: nella cartella di {os.path.basename(self.video)} non posso scrivere il file."
        lettore = self._crea_lettore(self.video)
        try:
            inizio = time.monotonic()
            while lettore.duration is None and time.monotonic() - inizio < 30 and not self._fermo.is_set():
                time.sleep(0.1)
            durata = lettore.duration
            if not durata:
                return f"La passata dei sottotitoli impressi non apre {os.path.basename(self.video)}."
            lettore.speed = self.velocita
            lettore.pause = False
            campioni, prossimo, ultimo_avviso = self.campioni, 0.0, -1
            while not self._fermo.is_set():
                istante = lettore.time_pos
                if istante is None:
                    if lettore.idle_active:
                        break
                    time.sleep(0.02)
                    continue
                if istante < prossimo:
                    time.sleep(0.01)
                    continue
                prossimo = istante + PASSO_DELLA_PASSATA
                try:
                    righe = ocr.leggi(ocr.fascia_in_basso(lettore.screenshot_raw(includes="video")), self.lingua)
                except Exception:  # noqa: BLE001 - un campione che non si legge si salta, contato
                    self.campioni_persi += 1
                    continue
                campioni.append((istante, tuple(righe)))
                percentuale = int(100 * istante / durata) // 10 * 10
                if percentuale > ultimo_avviso:
                    ultimo_avviso = percentuale
                    self._avanza(percentuale)
        finally:
            lettore.terminate()
        if self._fermo.is_set():
            return None
        sottotitoli = segmenti(senza_scritte_fisse(campioni), durata)
        if not sottotitoli:
            return None
        with open(percorso, "w", encoding="utf-8") as f:
            f.write(testo_srt(sottotitoli))
        return percorso


def _lettore_della_passata(video):
    """Un libmpv tutto per la passata: niente audio, niente sottotitoli di
    traccia, niente finestre; corre a VELOCITA_DELLA_PASSATA. Le opzioni di
    base sono quelle dei lettori del motore, senza gli script di mpv."""
    import mpv

    from motore import OPZIONI_DI_BASE

    lettore = mpv.MPV(**{**OPZIONI_DI_BASE, "video": "auto", "ao": "null", "aid": "no", "sid": "no", "pause": True})
    lettore.play(video)
    return lettore
