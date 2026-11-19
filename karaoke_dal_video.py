# MeTeOra, il testo dei video karaoke: letto dall'immagine, con le parole esatte dell'archivio dei testi.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 19/11/2026: nasce con la 3.28.0 (issue 51), dalla seconda prova del 19 novembre 2026 in tmp\ocr_karaoke\prova_2, approvata da Gabriele.

"""Il testo dei video karaoke, come quelli di Sing King, che non hanno
sottotitoli: le parole sono disegnate nell'immagine.

Tre tecniche insieme, misurate sulla seconda prova, 24 video di otto canali:
- il riconoscimento dei caratteri di Windows legge il fotogramma intero in
  grigio ogni INTERVALLO secondi, e da' il momento in cui compare ogni riga;
- l'archivio dei testi di LRCLIB da' le parole esatte: una riga letta si
  cerca nel testo, parola per parola, vicino all'ultima trovata, e si dice il
  pezzo dell'archivio; le righe che non somigliano a niente, loghi e scritte
  del canale, si scartano;
- il testo giusto si sceglie dal titolo del video, ripulito dalle parole dei
  canali, e fra i risultati dell'archivio vince quello che somiglia di piu'
  alle righe gia' lette.
Una riga si propone quando compare in due letture di fila e non e' gia'
sullo schermo; tre righe uguali nella pagina, come un ritornello, sono tre
righe. Nella prova il video mostrava 968 righe su 996, e se ne diceva il 91%,
0,4 secondi dopo la loro comparsa. La stabilita' sui fotogrammi, il colore e
l'unione di due modi non facevano meglio del grigio.
Senza il testo nell'archivio si dice l'OCR da solo, come legge (Gabriele).
I testi letti vanno nella cartella Testi, con testi_dei_video, per la volta
dopo. Il riconoscimento vuole un ciclo per filo (issue 50): ocr.leggi lo ha.
"""

import difflib
import json
import re
import threading
import time
import urllib.parse
import urllib.request

import ocr
import testi_dei_video
import version
from lingua import _
from sottotitoli_ocr import _Lettura

# Ogni quanto si legge il fotogramma, come la lettura degli impressi.
INTERVALLO = 0.4
# Una riga sparita da meno di cosi' e' ancora sullo schermo: la lettura che
# la perde una volta non la fa ridire.
ASSENZA = 1.2
# Due letture di fila che somigliano almeno tanto sono la stessa riga ferma.
STABILE = 0.85
# Una riga letta che somiglia almeno tanto a una sullo schermo e' quella.
STESSA = 0.75
# La somiglianza che serve per prendere un pezzo dell'archivio; una riga
# corta, di due parole o di meno di 12 lettere, vuole di piu': da sola
# somiglia a troppe cose (seconda prova: tube diventava true).
SOGLIA = 0.7
SOGLIA_BREVE = 0.85
LETTERE_BREVI = 12
# Un pezzo detto da meno di tanti secondi non si ridice; se va oltre, si
# dicono solo le parole nuove, come nei video che scrivono una parola alla volta.
RECENTE = 8.0
# Nei primi secondi una riga contenuta nel titolo del video e' il cartello
# iniziale, con cantante e canzone: non si dice come testo.
CARTELLO = 25.0
# Quanto si aspetta l'archivio prima di dire le righe come le legge l'OCR.
ATTESA_DELL_ARCHIVIO = 4.0
# Per quante righe lette si puo' cambiare il testo scelto fra i risultati
# dell'archivio; se l'archivio risponde tardi, per altrettante da li'.
SCELTA_RIGHE = 15
# Con almeno tante righe lette, se il testo scelto ne riconosce meno di
# questa parte, non e' la canzone del video: si dice l'OCR da solo.
CONTROLLO_RIGHE = 10
CONTROLLO_PARTE = 0.3
# Quante righe lette deve riconoscere il testo scelto perche' la console
# dica che c'e': il primo si sceglie prima di leggere, e puo' non essere lui.
CONFERMA = 2
# Ogni quante righe dette il testo si salva, oltre che alla fine.
SALVA_OGNI = 20
# Un passo della posizione piu' lungo di cosi' e' un salto: il tratto letto
# si chiude e ne comincia un altro.
SALTO = 2.0
ARCHIVIO = "https://lrclib.net/api/search"
RISULTATI = 10
# Le parole che i canali karaoke aggiungono al titolo della canzone.
_RUMORE = re.compile(
    r"\((?:[^)]*(?:karaok|lyrics|testo|version|instrumental|base)[^)]*)\)|\[[^\]]*\]|"
    r"\S*karaok\S*|\b(?:version[ei]?|with lyrics|lyrics on screen|on screen|lyrics|instrumental|testo|base|"
    r"sing king|karafun|stingray|zoom|academy|italia|official|hd|hq)\b|[|@*()]",
    re.IGNORECASE)


def norm(testo):
    """Il testo da confrontare: minuscolo, senza punteggiatura, l'apostrofo
    curvo diritto."""
    return " ".join(re.sub(r"[^\w']+|_", " ", testo.lower().replace(chr(0x2019), "'")).split())


def simile(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def utile(riga):
    """Una riga con almeno una parola di due lettere."""
    return bool(riga) and re.search(r"[^\W\d_]{2,}", riga) is not None


def e_un_karaoke(titolo):
    """Vero se il titolo del video, o il nome del file, dice karaoke."""
    return "karaok" in (titolo or "").lower()


def pulisci_il_titolo(titolo):
    """Il titolo senza le parole del karaoke: Natalie Imbruglia Torn."""
    return " ".join(_RUMORE.sub(" ", titolo or "").replace(" - ", " ").replace("-", " ").split())


def prepara(quadro):
    """Il fotogramma intero in grigio, ingrandito se il video e' piccolo:
    il modo migliore della seconda prova."""
    grigio = quadro.convert("L").convert("RGB")
    return grigio.resize((grigio.width * 2, grigio.height * 2)) if grigio.width < 1000 else grigio


def _chiedi(domanda, attesa):
    indirizzo = ARCHIVIO + "?" + urllib.parse.urlencode({"q": domanda})
    richiesta = urllib.request.Request(indirizzo, headers={"User-Agent": f"MeTeOra/{version.VERSION}"})  # noqa: S310 - indirizzo fisso
    with urllib.request.urlopen(richiesta, timeout=attesa) as risposta:  # noqa: S310 - indirizzo fisso
        voci = json.loads(risposta.read().decode("utf-8"))
    return [v for v in voci if isinstance(v, dict) and v.get("plainLyrics")] if isinstance(voci, list) else []


def cerca_nell_archivio(titolo, attesa=10.0, chiedi=None):
    """I testi dell'archivio per il titolo del video, al piu' RISULTATI: si
    cerca il titolo ripulito, e se non trova niente si toglie l'ultima parola,
    fino a due parole. Solleva OSError se l'archivio non risponde. chiedi e'
    per le prove; senza, si chiede all'archivio vero."""
    chiedi = chiedi or _chiedi
    parole = pulisci_il_titolo(titolo).split()
    while len(parole) >= 2:
        candidati = chiedi(" ".join(parole), attesa)
        if candidati:
            return candidati[:RISULTATI]
        parole = parole[:-1]
    return []


class Archivio:
    """Un testo dell'archivio come sequenza di parole, ognuna con il pezzo
    originale da dire e la riga da cui viene."""

    def __init__(self, testo, nome=""):
        self.nome = nome
        self.pezzi, self.parole = [], []
        for indice, riga in enumerate(r for r in testo.splitlines() if norm(r)):
            for pezzo in riga.split():
                self.pezzi.append((pezzo, indice))
                self.parole.extend((p, len(self.pezzi) - 1) for p in norm(pezzo).split())
        self.normali = [p for p, _pezzo in self.parole]
        self.righe = [norm(r) for r in testo.splitlines() if norm(r)]

    def testo(self, inizio, fine):
        return " ".join(p for p, _riga in self.pezzi[self.parole[inizio][1]:self.parole[fine - 1][1] + 1])

    def abbina(self, riga, puntatore, soglia):
        """(somiglianza, inizio, fine) del pezzo piu' simile alla riga: fra
        quelli quasi migliori, il piu' vicino al puntatore. Prima intorno al
        puntatore, poi in tutto il testo; None se niente arriva alla soglia."""
        quante, totale = len(riga.split()), len(self.normali)
        confronto = difflib.SequenceMatcher(None)
        confronto.set_seq2(riga)
        minimo = soglia - 0.03

        def cerca(da, a):
            esiti = []
            for inizio in range(max(0, da), min(totale, a)):
                for lunghezza in range(max(1, quante - 2), quante + 3):
                    fine = inizio + lunghezza
                    if fine > totale:
                        break
                    confronto.set_seq1(" ".join(self.normali[inizio:fine]))
                    if confronto.real_quick_ratio() < minimo or confronto.quick_ratio() < minimo:
                        continue
                    somiglianza = confronto.ratio()
                    if somiglianza >= minimo:
                        esiti.append((somiglianza, inizio, fine))
            return esiti

        esiti = cerca(puntatore - 30, puntatore + 80)
        if not esiti or max(esiti)[0] < soglia:
            esiti = cerca(0, totale)
        if not esiti or max(esiti)[0] < soglia:
            return None
        migliore = max(esiti)[0]
        return min((e for e in esiti if e[0] >= migliore - 0.03), key=lambda e: (abs(e[1] - puntatore), -e[0]))

    def riconosce(self, riga):
        """Vero se la riga letta somiglia a una riga del testo."""
        confronto = difflib.SequenceMatcher(None)
        confronto.set_seq2(riga)
        for vera in self.righe:
            confronto.set_seq1(vera)
            if confronto.quick_ratio() >= SOGLIA and confronto.ratio() >= SOGLIA:
                return True
        return False


def scegli(candidati, lette):
    """Il candidato dell'archivio che riconosce piu' righe lette, a pari
    merito quello col testo sincronizzato e poi il primo; e quante ne
    riconosce. (None, 0) senza candidati."""
    lunghe = [r for r in lette if len(r) >= 8]
    migliore, punti = None, -1
    for candidato in candidati:
        archivio = Archivio(candidato.get("plainLyrics") or "")
        conto = sum(1 for r in lunghe if archivio.riconosce(r))
        if conto > punti or (conto == punti and candidato.get("syncedLyrics") and not (migliore or {}).get("syncedLyrics")):
            migliore, punti = candidato, conto
    return migliore, max(0, punti)


def _pulito(testo):
    """Un nome dell'archivio senza spazi doppi e senza le parentesi rimaste a
    meta', come Torn    ), che l'archivio a volte ha."""
    testo = " ".join((testo or "").split())
    if testo.count("(") != testo.count(")"):
        testo = " ".join(testo.replace("(", " ").replace(")", " ").split())
    return testo.strip(" -")


def nome_del_candidato(candidato):
    """Cantante e canzone di un testo dell'archivio, da dire nella console;
    il cantante una volta sola, anche quando l'archivio lo ripete nel titolo."""
    artista, canzone = _pulito(candidato.get("artistName")), _pulito(candidato.get("trackName"))
    if artista and norm(artista) in norm(canzone):
        return canzone
    return f"{artista} - {canzone}".strip(" -")


class Righe:
    """Le righe nuove sullo schermo, lettura dopo lettura: una riga si propone
    quando compare in due letture di fila e non e' gia' sullo schermo. Sullo
    schermo c'e' cio' che somiglia a una riga vista da meno di ASSENZA
    secondi, una copia per riga letta: un ritornello che torna dopo una
    pagina nuova si propone di nuovo. Una riga che cresce, nei video che
    scrivono una parola alla volta, si ripropone intera."""

    def __init__(self):
        self._prima = []
        self._schermo = []

    def nuove(self, istante, lette):
        """Le proposte (istante, riga normale, riga come letta) della lettura."""
        self._schermo = [v for v in self._schermo if istante - v[1] <= ASSENZA]
        righe = [(n, r) for n, r in ((norm(r), r) for r in lette) if utile(n)]
        proposte, usate = [], []
        for normale, letta in righe:
            stabile = sum(1 for p in self._prima if simile(normale, p) >= STABILE) > sum(1 for u in usate if simile(normale, u[0]) >= STABILE)
            gia = next((v for v in self._schermo if all(v is not u for u in usate)
                        and (simile(normale, v[0]) >= STESSA or normale in v[0] or v[0] in normale)), None)
            if gia is not None:
                usate.append(gia)
                gia[1] = istante
                if stabile and gia[0] in normale and len(normale.split()) > len(gia[0].split()):
                    gia[0] = normale
                    proposte.append((istante, normale, letta))
                continue
            if stabile:
                nuova = [normale, istante]
                self._schermo.append(nuova)
                usate.append(nuova)
                proposte.append((istante, normale, letta))
        self._prima = [n for n, _r in righe]
        return proposte


class Abbinatore:
    """Le proposte di Righe fatte testo da dire: con l'archivio, il pezzo
    esatto; senza, la riga come l'ha letta l'OCR. Nei primi CARTELLO secondi
    una riga contenuta nel titolo del video e' il cartello iniziale."""

    def __init__(self, archivio, titolo):
        self.archivio = archivio
        self._titolo = norm(titolo)
        self._puntatore = 0
        self._dette = []
        self._ultima = {}

    def abbina(self, istante, normale, letta):
        """Il testo da dire per la proposta, o None se si scarta."""
        if istante <= CARTELLO and normale in self._titolo:
            return None
        if self.archivio is None:
            return self._senza_archivio(istante, normale, letta)
        breve = len(normale) < LETTERE_BREVI or len(normale.split()) <= 2
        esito = self.archivio.abbina(normale, self._puntatore, max(SOGLIA, SOGLIA_BREVE) if breve else SOGLIA)
        if esito is None:
            return None
        _somiglianza, inizio, fine = esito
        self._puntatore = fine
        sopra = [f for tempo, i, f in self._dette if istante - tempo <= RECENTE and min(fine, f) > max(inizio, i)]
        if sopra:
            if fine <= max(sopra):
                return None
            inizio = max(inizio, max(sopra))
        self._dette.append((istante, inizio, fine))
        return self.archivio.testo(inizio, fine)

    def _senza_archivio(self, istante, normale, letta):
        """La riga come letta; se cresce da una appena detta, solo le parole nuove."""
        cresciuta = next((n for n, tempo in self._ultima.items() if istante - tempo <= RECENTE and normale.startswith(n + " ")), None)
        self._ultima[normale] = istante
        if cresciuta is None:
            return letta
        nuove = len(normale.split()) - len(cresciuta.split())
        return " ".join(letta.split()[-nuove:]) if nuove > 0 else None


class LetturaDelKaraoke(_Lettura):
    """Il testo di un video karaoke letto al volo, finche' lo si ferma.
    dici(testo) riceve le righe nuove, a capo fra l'una e l'altra;
    avvisa(frase, con_l_archivio) dice alla console cosa e' successo con
    l'archivio, e se le righe ora vengono da li'. coperti sono i tratti
    gia' letti un'altra volta: li' il riconoscimento resta spento. Alla fine,
    e ogni SALVA_OGNI righe, il testo va nella cartella Testi."""

    tipo = "karaoke"

    def __init__(self, motore, dici, lingua, percorso, titolo, avvisa, guasto=None, coperti=(), cerca=None, salva=None):
        super().__init__("testo del karaoke dal video", motore, dici, lingua, guasto)
        self.percorso = percorso
        self.titolo = titolo
        self._avvisa = avvisa
        # Le prove danno i loro; senza, quelli veri, cercati al momento.
        self._cerca = cerca or (lambda titolo: cerca_nell_archivio(titolo))
        self._salva = salva or (lambda *dati: testi_dei_video.salva(*dati))
        self._coperti_prima = [tuple(t) for t in coperti]
        # Per le prove e per le statistiche: i tratti letti [inizio, fine], i
        # gruppi detti (istante, [testi]), com'e' andata con l'archivio.
        self.tratti = []
        self.gruppi = []
        self.righe_dette = 0
        self.esito_dell_archivio = None
        self.archivio_usato = ""
        self._candidati = None
        self._risposta = threading.Event()
        self._annunciato = None

    def _chiedi_all_archivio(self):
        try:
            self._candidati = self._cerca(self.titolo)
            self.esito_dell_archivio = "trovato" if self._candidati else "assente"
        except Exception:  # noqa: BLE001 - un archivio che non risponde, in qualsiasi modo, vuol dire l'OCR da solo
            self._candidati = []
            self.esito_dell_archivio = "errore"
        self._risposta.set()

    def _scegli_l_archivio(self, lette):
        """(testo dell'archivio, righe lette che riconosce) per le righe lette
        fin qui; (None, 0) senza risposta, senza risultati, o se il migliore
        riconosce troppo poco."""
        if not self._risposta.is_set() or not self._candidati:
            return None, 0
        candidato, punti = scegli(self._candidati, lette)
        lunghe = sum(1 for r in lette if len(r) >= 8)
        if candidato is None or (lunghe >= CONTROLLO_RIGHE and punti < CONTROLLO_PARTE * lunghe):
            return None, 0
        return Archivio(candidato["plainLyrics"], nome_del_candidato(candidato)), punti

    def _annuncia(self, archivio, punti, finale):
        """La console dice com'e' andata con l'archivio, quando e' sicuro: un
        testo quando riconosce CONFERMA righe lette, o alla fine della scelta,
        perche' il primo, scelto senza righe, puo' non essere quello giusto;
        l'OCR da solo quando l'archivio ha risposto. Ogni cambio, una volta."""
        nome = archivio.nome if archivio is not None else ""
        if nome == self._annunciato:
            return
        if (archivio is not None and (punti >= CONFERMA or finale)) or (archivio is None and self._risposta.is_set()):
            self._annunciato = nome
            self._avvisa_l_esito(archivio)

    def _avvisa_l_esito(self, archivio):
        nome = self.titolo
        if archivio is not None:
            # Traduttori: titolo e' quello del video; canzone e' quella trovata nell'archivio dei testi, come Adele - Hello.
            frase = _("Testo del karaoke di {titolo}: è nell'archivio dei testi, {canzone}; le righe lette si dicono con le sue parole.").format(
                titolo=nome, canzone=archivio.nome)
        elif self.esito_dell_archivio == "errore":
            frase = _("L'archivio dei testi non risponde: il testo di {titolo} si legge dal video così com'è, con qualche errore possibile.").format(titolo=nome)
        elif self._candidati:
            frase = _("I testi dell'archivio non sono quello di {titolo}: si legge dal video così com'è, con qualche errore possibile.").format(titolo=nome)
        else:
            frase = _("Il testo di {titolo} non è nell'archivio dei testi: si legge dal video così com'è, con qualche errore possibile.").format(titolo=nome)
        self._avvisa(frase, archivio is not None)

    def _tratto(self, tratto, posizione):
        """Il tratto letto si allunga fino alla posizione, o se c'e' stato un
        salto ne comincia un altro."""
        if tratto is not None and tratto[1] - 0.5 <= posizione <= tratto[1] + SALTO:
            tratto[1] = posizione
            return tratto
        nuovo = [posizione, posizione]
        self.tratti.append(nuovo)
        return nuovo

    def salva_ora(self):
        """Il testo letto fin qui nella cartella Testi; mai un errore. Senza
        righe dette non si salva niente, nemmeno i tratti: chi passa dalla
        scelta con D per arrivare agli impressi non lascia segni."""
        tratti = [(a, b + INTERVALLO) for a, b in self.tratti if b > a]
        if not self.gruppi:
            return
        try:
            self._salva(self.percorso, self.titolo, self._motore.durata or 0, list(self.gruppi), tratti, self.archivio_usato)
        except Exception as errore:  # noqa: BLE001 - un testo che non si salva non ferma la lettura
            self._giro_guasto(errore)

    def _dici_le_proposte(self, abbinatore, proposte):
        dire = []
        for istante, normale, letta in proposte:
            testo = abbinatore.abbina(istante, normale, letta)
            if not testo:
                continue
            dire.append(testo)
            if self.gruppi and abs(self.gruppi[-1][0] - istante) < 0.01:
                self.gruppi[-1][1].append(testo)
            else:
                self.gruppi.append((istante, [testo]))
        if dire and not self._fermo.is_set():
            self.righe_dette += len(dire)
            self._dici("\n".join(dire))

    def _lavora(self):
        threading.Thread(target=self._chiedi_all_archivio, name="MeTeOra, archivio dei testi", daemon=True).start()
        righe = Righe()
        abbinatore, in_attesa, lette, partenza = None, [], [], time.monotonic()
        # La scelta fra i testi dell'archivio resta aperta per SCELTA_RIGHE
        # righe lette, e si riapre se l'archivio risponde tardi.
        fine_della_scelta, risposta_vista, salvate, tratto = SCELTA_RIGHE, False, 0, None
        while not self._fermo.wait(INTERVALLO):
            motore = self._motore
            if motore.in_pausa or motore.in_corso != self.percorso:
                continue
            posizione = motore.posizione
            if posizione is None:
                continue
            if testi_dei_video.coperto(self._coperti_prima, posizione):
                tratto = None
                continue
            tratto = self._tratto(tratto, posizione)
            try:
                quadro = motore.foto(False)
                if quadro is None:
                    continue
                proposte = righe.nuove(posizione, ocr.leggi(prepara(quadro), self.lingua))
            except Exception as errore:  # noqa: BLE001 - un giro guasto non ferma la lettura
                self._giro_guasto(errore)
                continue
            in_attesa.extend(proposte)
            lette.extend(normale for _istante, normale, _letta in proposte)
            if abbinatore is None and not self._risposta.is_set() and time.monotonic() - partenza < ATTESA_DELL_ARCHIVIO:
                continue
            if self._risposta.is_set() and not risposta_vista:
                risposta_vista = True
                fine_della_scelta = len(lette) + SCELTA_RIGHE
            if abbinatore is None or (len(lette) <= fine_della_scelta and proposte):
                archivio, punti = self._scegli_l_archivio(lette)
                attuale = abbinatore.archivio.nome if abbinatore is not None and abbinatore.archivio is not None else None
                if abbinatore is None or (archivio.nome if archivio is not None else None) != attuale:
                    abbinatore = Abbinatore(archivio, self.titolo)
                    self.archivio_usato = archivio.nome if archivio is not None else ""
                self._annuncia(archivio, punti, finale=len(lette) >= fine_della_scelta)
            self._dici_le_proposte(abbinatore, in_attesa)
            in_attesa.clear()
            if self.righe_dette - salvate >= SALVA_OGNI:
                salvate = self.righe_dette
                self.salva_ora()
        self.salva_ora()
