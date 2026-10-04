# MeTeOra, i testi del karaoke: MIDI e .kar, .lrc accanto al brano, SYLT dei tag ID3, fatti traccia di sottotitoli.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.82.0, per la tappa 10, punto e.

"""I testi a tempo del karaoke (tappa 10, punto e).

Le fonti, nell'ordine: il testo cantato dentro un MIDI, negli eventi FF 05,
o negli eventi di testo FF 01 dei .kar; un file .lrc con lo stesso nome del
brano, anche nella forma estesa con i tempi per parola; i testi
sincronizzati SYLT dei tag ID3, in millisecondi. Ogni fonte da' una lista
di Riga: l'istante in secondi, il testo e se comincia una strofa; una Riga
senza testo e' una pausa, che chiude la riga prima.
MeTeOra ne fa una traccia di sottotitoli SubRip, per riga o per strofa e con
l'anticipo, che il motore aggiunge al brano: cosi' arriva alla sintesi e
nella console come i sottotitoli dei video, con Maiuscolo con F2, e dopo un
salto libmpv ridice la riga in corso.
I tempi dei MIDI si contano qui, dai tick e dai cambi di tempo: FluidSynth
rende il brano in RAM e non avvisa delle parole. Un file rovinato non
solleva niente: da' meno righe, o nessuna.
"""

import bisect
import collections
import os
import re
import struct
from typing import NamedTuple

import formati

# Il titolo delle tracce del karaoke, e da dove viene il testo.
TITOLO = "Testo del karaoke"
FONTI = {"midi": "dal MIDI", "lrc": "dal file LRC", "sylt": "dai tag del brano"}
MODI = ("riga", "strofa")
# L'ultima riga, o strofa, resta per tanto dopo il suo inizio.
DURATA_DELL_ULTIMA = 10.0
# La durata minima di un blocco della traccia, in secondi.
DURATA_MINIMA = 0.05
# Un MIDI o un .lrc piu' grande non si legge.
DIMENSIONE_MASSIMA = 16 << 20
# Un MIDI con meno righe non ha un testo da karaoke: e' l'avviso del
# copyright, o il titolo, messo fra le parole.
MINIMO_DI_RIGHE = 3
# Una riga piu' lunga, in caratteri, si spezza alle pause del canto lunghe
# almeno PAUSA_DI_FRASE secondi, o fra due parole: e' un file che non va mai
# a capo (banco del 4 ottobre 2026 sui .kar di Gabriele).
LUNGHEZZA_MASSIMA = 80
PAUSA_DI_FRASE = 0.7
# Il tempo di partenza dei MIDI: 120 battiti al minuto.
TEMPO_PREDEFINITO = 500000

_META = 0xFF
_FINE_DELLA_TRACCIA = 0x2F
_TESTO = 0x01
_TESTO_CANTATO = 0x05
_TEMPO = 0x51
# Quanti byte di dati seguono gli stati di sistema comune, che in un file
# MIDI non dovrebbero esserci.
_DATI_DI_SISTEMA = {0xF1: 1, 0xF2: 2, 0xF3: 1}

_TEMPO_LRC = re.compile(r"\s*\[(\d{1,3}):(\d{1,2})(?:[.:,](\d{1,3}))?\]")
_PAROLA_LRC = re.compile(r"<\d{1,3}:\d{1,2}(?:[.:,]\d{1,3})?>")
_OFFSET_LRC = re.compile(r"\[offset:\s*([+-]?\d+)\s*\]", re.IGNORECASE)
_A_CAPO = re.compile(r"(\r\n|\r|\n)")
# Le intestazioni dei .kar: il tipo di file, il titolo, la lingua, le
# informazioni, la versione, gli avvisi.
_INTESTAZIONI_KAR = (b"@K", b"@T", b"@L", b"@I", b"@V", b"@W")
# I byte di cp1252 che sono punteggiatura, apostrofi e virgolette curve e
# trattini: non dicono che il testo e' di DOS.
_PUNTEGGIATURA_DI_WINDOWS = frozenset({0x91, 0x92, 0x93, 0x94, 0x96, 0x97})


class Riga(NamedTuple):
    inizio: float
    testo: str
    strofa: bool


# Il MIDI.

def _numero_variabile(dati, pos):
    """Un numero a lunghezza variabile dei MIDI: (valore, posizione dopo)."""
    valore = 0
    for _ in range(4):
        byte = dati[pos]
        pos += 1
        valore = (valore << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return valore, pos
    raise ValueError("numero a lunghezza variabile troppo lungo")


def _leggi_la_traccia(dati, pos, fine, numero, eventi):
    """I meta eventi di testo, testo cantato e tempo di una traccia MTrk, in
    coda a eventi come (tick, traccia, tipo, contenuto). Una traccia
    rovinata tiene quello che si e' letto fino al guasto. Lo stato corrente
    sopravvive ai meta eventi e ai sysex: e' contro le regole, ma alcuni
    file lo fanno, e FluidSynth li suona."""
    tick = 0
    stato = None
    try:
        while pos < fine:
            delta, pos = _numero_variabile(dati, pos)
            tick += delta
            byte = dati[pos]
            if byte == _META:
                tipo = dati[pos + 1]
                lunghezza, pos = _numero_variabile(dati, pos + 2)
                contenuto = bytes(dati[pos:pos + lunghezza])
                pos += lunghezza
                if tipo == _FINE_DELLA_TRACCIA:
                    return
                if tipo in (_TESTO, _TESTO_CANTATO, _TEMPO):
                    eventi.append((tick, numero, tipo, contenuto))
            elif byte in (0xF0, 0xF7):
                lunghezza, pos = _numero_variabile(dati, pos + 1)
                pos += lunghezza
            elif byte >= 0xF1:
                pos += 1 + _DATI_DI_SISTEMA.get(byte, 0)
            else:
                if byte & 0x80:
                    stato = byte
                    pos += 1
                elif stato is None:
                    return
                pos += 1 if 0xC0 <= stato < 0xE0 else 2
    except (IndexError, ValueError):
        return


def _eventi_del_midi(dati):
    """(divisione, eventi) di un file MIDI, anche dentro un RIFF RMID."""
    inizio = dati.find(b"MThd")
    if inizio < 0 or len(dati) < inizio + 14:
        raise ValueError("non e' un file MIDI")
    lunghezza, _formato, tracce, divisione = struct.unpack(">IHHH", dati[inizio + 4:inizio + 14])
    pos = inizio + 8 + lunghezza
    eventi = []
    numero = 0
    while pos + 8 <= len(dati) and numero < tracce:
        tipo, lunghezza = struct.unpack(">4sI", dati[pos:pos + 8])
        pos += 8
        fine = min(pos + lunghezza, len(dati))
        if tipo == b"MTrk":
            _leggi_la_traccia(dati, pos, fine, numero, eventi)
            numero += 1
        pos = fine
    return divisione, eventi


def _da_tick_a_secondi(divisione, tempi):
    """La funzione che porta i tick in secondi, con la mappa dei tempi:
    tempi e' [(tick, microsecondi per semiminima)]. Con la divisione SMPTE
    i tick sono parti di fotogramma, e i tempi non contano."""
    if divisione & 0x8000:
        fotogrammi = 256 - (divisione >> 8)
        per_fotogramma = divisione & 0xFF
        if not fotogrammi or not per_fotogramma:
            raise ValueError("divisione SMPTE sbagliata")
        al_secondo = (29.97 if fotogrammi == 29 else fotogrammi) * per_fotogramma
        return lambda tick: tick / al_secondo
    if not divisione:
        raise ValueError("divisione zero")
    punti = [(0, 0.0, TEMPO_PREDEFINITO)]
    for tick, tempo in sorted(tempi):
        tick0, secondi0, tempo0 = punti[-1]
        secondi = secondi0 + (tick - tick0) * tempo0 / (divisione * 1e6)
        if tick == tick0:
            punti[-1] = (tick0, secondi0, tempo)
        else:
            punti.append((tick, secondi, tempo))
    ticks = [p[0] for p in punti]

    def converti(tick):
        tick0, secondi0, tempo0 = punti[bisect.bisect_right(ticks, tick) - 1]
        return secondi0 + (tick - tick0) * tempo0 / (divisione * 1e6)

    return converti


def _ha_parole(contenuto):
    """Vero per un evento con delle parole: non solo spazi e segni di a
    capo, e non un accordo, che i .kar italiani con gli accordi scrivono
    come %DO o %LA-7."""
    return bool(contenuto.strip(b" \r\n\t\x00/\\<")) and not contenuto.startswith(b"%")


def _della_traccia_piu_ricca(eventi):
    """Gli eventi della traccia che ha piu' parole, compresi quelli che
    vanno solo a capo: i duetti, con due tracce di testo, mescolati
    darebbero sillabe alternate. Senza gli accordi, e senza gli eventi
    all'istante zero, che sono intestazioni e avvisi del copyright."""
    conti = collections.Counter(numero for _tick, numero, contenuto in eventi if _ha_parole(contenuto))
    if not conti:
        return []
    scelta = max(conti, key=lambda numero: (conti[numero], -numero))
    return [(tick, contenuto) for tick, numero, contenuto in eventi if numero == scelta and tick > 0 and not contenuto.startswith(b"%")]


def codifica(dati):
    """La codifica di un testo senza dichiarazione: UTF-8 se lo e';
    altrimenti quella occidentale di DOS, cp850, se i byte alti stanno piu'
    fra 0x80 e 0x9F, dove DOS mette le lettere accentate e Windows quasi
    niente, come nei .kar francesi di Gabriele, dove la a accentata
    diventava i puntini; se no quella di Windows, cp1252, come quasi tutti
    i .kar. Gli apostrofi e le virgolette curve di Windows, in quella zona,
    non contano per DOS: un testo di De Andre' con piu' apostrofi che
    accenti diventava illeggibile (revisione della 1.82.0)."""
    try:
        dati.decode("utf-8")
    except UnicodeDecodeError:
        dos = sum(1 for byte in dati if 0x80 <= byte <= 0x9F and byte not in _PUNTEGGIATURA_DI_WINDOWS)
        windows = sum(1 for byte in dati if byte >= 0xC0)
        return "cp850" if dos > windows else "cp1252"
    return "utf-8"


def _decodifica(pezzi):
    """I testi di un file, tutti con la stessa codifica."""
    scelta = codifica(b"".join(pezzi))
    return [pezzo.decode(scelta, "replace") for pezzo in pezzi]


def _con_la_barra(scelti):
    """Quante sillabe cominciano con la barra o la barra rovesciata, anche
    dopo uno spazio."""
    return sum(1 for _tick, contenuto in scelti if contenuto.lstrip(b" ")[:1] in (b"/", b"\\"))


def _a_capo(scelti):
    """Quante sillabe vanno a capo: con la barra o con un a capo."""
    return _con_la_barra(scelti) + sum(1 for _tick, contenuto in scelti if b"\r" in contenuto or b"\n" in contenuto)


def dal_midi(dati, kar=False):
    """Le righe del testo cantato di un MIDI. Prima gli eventi di testo FF
    01, senza le intestazioni con la chiocciola, se il file e' un karaoke:
    un .kar, un file con le intestazioni dei .kar, o con almeno
    MINIMO_DI_RIGHE sillabe che cominciano con le barre, anche se si chiama
    .mid; e solo se le sue sillabe vanno a capo almeno MINIMO_DI_RIGHE
    volte, perche' certi .kar hanno negli eventi di testo solo gli accordi.
    Gli eventi di testo hanno le sillabe a tempo e le barre di riga e di
    strofa, mentre il testo cantato degli stessi file, quando c'e', spesso
    non va mai a capo, o porta gli accordi e la riga intera in anticipo,
    dopo il segno di minore. Poi gli eventi FF 05. Vale il primo che da'
    almeno MINIMO_DI_RIGHE righe (revisione della 1.82.0, sui MIDI di
    Gabriele)."""
    divisione, eventi = _eventi_del_midi(dati)
    tempi = [(tick, int.from_bytes(contenuto, "big")) for tick, _n, tipo, contenuto in eventi
        if tipo == _TEMPO and len(contenuto) == 3 and int.from_bytes(contenuto, "big") > 0]
    secondi = _da_tick_a_secondi(divisione, tempi)
    testi = [(tick, numero, contenuto) for tick, numero, tipo, contenuto in eventi if tipo == _TESTO]
    parole_di_testo = _della_traccia_piu_ricca([(t, n, c) for t, n, c in testi if not c.startswith(b"@")])
    karaoke = kar or any(c.startswith(_INTESTAZIONI_KAR) for _t, _n, c in testi) or _con_la_barra(parole_di_testo) >= MINIMO_DI_RIGHE
    candidati = []
    if karaoke and _a_capo(parole_di_testo) >= MINIMO_DI_RIGHE:
        candidati.append(parole_di_testo)
    candidati.append(_della_traccia_piu_ricca([(tick, numero, contenuto) for tick, numero, tipo, contenuto in eventi if tipo == _TESTO_CANTATO]))
    for scelti in candidati:
        # Il segno di minore in testa, nei .kar con gli accordi, comincia la riga.
        parole = [("/" + parola[1:]) if parola.startswith("<") else parola for parola in _decodifica([c for _t, c in scelti])]
        righe = righe_dalle_sillabe([(secondi(tick), parola) for (tick, _c), parola in zip(scelti, parole, strict=True)])
        if sum(1 for riga in righe if riga.testo) >= MINIMO_DI_RIGHE:
            return righe
    return []


# Le sillabe in righe, per i MIDI e i SYLT.

def righe_dalle_sillabe(sillabe, doppio_a_capo=False):
    """Le righe da sillabe a tempo, [(secondi, testo)]: le sillabe si
    attaccano, con gli spazi che hanno. Come nei .kar, la barra in testa a
    una sillaba va a capo e la barra rovesciata cambia strofa; come dice la
    RP-026 per i MIDI, il ritorno carrello chiude la riga e l'a capo la
    strofa. Con doppio_a_capo, per i SYLT, ogni a capo chiude la riga, e una
    riga vuota cambia strofa. Una riga comincia con la sua prima sillaba non
    vuota."""
    righe = []
    pezzi, strofa, vuote = [], True, 0

    def chiudi(cambia_strofa):
        nonlocal pezzi, strofa, vuote
        if "".join(testo for _i, testo in pezzi).strip():
            for numero, parte in enumerate(_spezza(pezzi)):
                righe.append(Riga(parte[0], parte[1], strofa and numero == 0))
            strofa, vuote = False, 0
        elif doppio_a_capo:
            vuote += 1
        pezzi = []
        if cambia_strofa or (doppio_a_capo and vuote >= 1 and righe):
            strofa = True

    for istante, sillaba in sillabe:
        sillaba = sillaba.replace("\x00", "")
        # La barra conta anche dopo uno spazio, come in Pollon.kar.
        while sillaba.lstrip(" ")[:1] in ("/", "\\"):
            sillaba = sillaba.lstrip(" ")
            chiudi(sillaba[0] == "\\")
            sillaba = sillaba[1:]
        for pezzo in _A_CAPO.split(sillaba):
            if pezzo in ("\r\n", "\r", "\n"):
                chiudi(not doppio_a_capo and pezzo == "\n")
            elif pezzo:
                pezzi.append((istante, pezzo))
    chiudi(False)
    return righe


def _spezza(pezzi):
    """Le righe, [(inizio, testo)], di una riga fatta di pezzi a tempo: una
    sola, se non supera LUNGHEZZA_MASSIMA; altrimenti si va a capo dopo le
    pause del canto, e prima di superarla, sempre fra due parole: una pausa
    su una sillaba tenuta, a meta' parola, aspetta la fine della parola.
    Una riga comincia con il suo primo pezzo non vuoto."""
    testo = "".join(parte for _i, parte in pezzi)
    if len(" ".join(testo.split())) <= LUNGHEZZA_MASSIMA:
        return [(next(i for i, parte in pezzi if parte.strip()), " ".join(testo.split()))]
    gruppi, gruppo, ultimo, pausa = [], [], None, False
    for istante, parte in pezzi:
        scritto = "".join(p for _i, p in gruppo)
        if gruppo and parte.strip() and scritto.strip():
            pausa = pausa or (ultimo is not None and istante - ultimo >= PAUSA_DI_FRASE)
            fra_parole = parte[0].isspace() or scritto[-1].isspace()
            if fra_parole and (pausa or len(scritto.strip()) + len(parte.rstrip()) > LUNGHEZZA_MASSIMA):
                gruppi.append(gruppo)
                gruppo, pausa = [], False
        gruppo.append((istante, parte))
        if parte.strip():
            ultimo = istante
    gruppi.append(gruppo)
    return [(next(i for i, parte in g if parte.strip()), " ".join("".join(p for _i, p in g).split())) for g in gruppi if "".join(p for _i, p in g).strip()]


# Il .lrc.

def dal_lrc(testo):
    """Le righe di un .lrc: [mm:ss.cc] davanti al testo, anche piu' d'uno
    per riga, e i tempi per parola <mm:ss.cc> della forma estesa, che si
    tolgono. Una riga vuota nel file, o una riga a tempo senza testo, chiude
    la strofa; quella a tempo e' anche una pausa. [offset:n] in millesimi
    anticipa il testo, se positivo."""
    anticipo = 0.0
    voci = []
    strofa = True
    for riga in testo.splitlines():
        offset = _OFFSET_LRC.fullmatch(riga.strip())
        if offset:
            anticipo = int(offset.group(1)) / 1000
            continue
        tempi, pos = [], 0
        while (tempo := _TEMPO_LRC.match(riga, pos)) is not None:
            minuti, secondi, frazione = tempo.groups()
            tempi.append(int(minuti) * 60 + int(secondi) + (float(f"0.{frazione}") if frazione else 0.0))
            pos = tempo.end()
        if not tempi:
            if not riga.strip():
                strofa = True
            continue
        parole = " ".join(_PAROLA_LRC.sub("", riga[pos:]).split())
        if not parole:
            voci.extend((istante, "", False) for istante in tempi)
            strofa = True
            continue
        voci.extend((istante, parole, strofa) for istante in tempi)
        strofa = False
    voci.sort(key=lambda voce: voce[0])
    return [Riga(max(0.0, istante - anticipo), parole, nuova) for istante, parole, nuova in voci]


def _testo_del_file(dati):
    if dati.startswith(b"\xef\xbb\xbf"):
        return dati[3:].decode("utf-8", "replace")
    if dati[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return dati.decode("utf-16", "replace")
    return dati.decode(codifica(dati), "replace")


# I tag.

def dai_tag(percorso):
    """Le righe del primo testo sincronizzato SYLT dei tag ID3, preferendo
    quello di tipo testo cantato, con i tempi in millesimi. Se nessuna voce
    va a capo, ogni voce e' una riga; altrimenti sono sillabe."""
    import mutagen

    try:
        tag = getattr(mutagen.File(percorso), "tags", None)
    except Exception:  # noqa: BLE001 - un file che mutagen non legge non ha testi
        return []
    if tag is None or not hasattr(tag, "getall"):
        return []
    testi = [s for s in tag.getall("SYLT") if s.format == 2 and s.text]
    if not testi:
        return []
    scelto = next((s for s in testi if s.type == 1), testi[0])
    sillabe = [(millesimi / 1000, testo) for testo, millesimi in scelto.text]
    if not any(_A_CAPO.search(testo) for _i, testo in sillabe):
        voci = [(istante, " ".join(testo.split())) for istante, testo in sillabe]
        return [Riga(istante, testo, numero == 0) for numero, (istante, testo) in enumerate(v for v in voci if v[1])]
    return righe_dalle_sillabe(sillabe, doppio_a_capo=True)


# Le fonti, e la traccia.

def file_lrc(percorso):
    """Il .lrc con lo stesso nome del brano, accanto a lui, o None."""
    lrc = os.path.splitext(percorso)[0] + ".lrc"
    return lrc if os.path.isfile(lrc) else None


def _leggi(percorso):
    with open(percorso, "rb") as f:
        return f.read(DIMENSIONE_MASSIMA)


def cerca(percorso):
    """(fonte, righe) del testo a tempo del brano, con fonte una chiave di
    FONTI; (None, []) se non ce n'e'. Mai un errore."""
    estensione = os.path.splitext(percorso)[1].lower()

    def dal_file_lrc():
        lrc = file_lrc(percorso)
        return dal_lrc(_testo_del_file(_leggi(lrc))) if lrc else []

    tentativi = []
    if estensione in formati.MIDI:
        tentativi.append(("midi", lambda: dal_midi(_leggi(percorso), kar=estensione == ".kar")))
    tentativi.append(("lrc", dal_file_lrc))
    if estensione not in formati.MIDI:
        tentativi.append(("sylt", lambda: dai_tag(percorso)))
    for fonte, leggi in tentativi:
        try:
            righe = leggi()
        except Exception:  # noqa: BLE001 - un file rovinato non ha testi
            righe = []
        if any(riga.testo for riga in righe):
            return fonte, righe
    return None, []


def blocchi(righe, modo="riga", anticipo=0.0):
    """I blocchi della traccia, [(inizio, fine, testo)]: uno per riga, o per
    strofa se il modo e' strofa e il file le segna, altrimenti per riga
    (Gabriele, 4 ottobre 2026). Un blocco dura fino al seguente, o alla
    pausa; l'ultimo fino a DURATA_DELL_ULTIMA dopo la sua ultima riga.
    L'anticipo, in secondi, sposta tutto prima; i blocchi che cosi'
    cominciano insieme, o a meno di DURATA_MINIMA uno dall'altro, diventano
    uno: libmpv li mostrerebbe sovrapposti, e il testo si direbbe tre volte."""
    per_strofa = modo == "strofa" and any(riga.strofa for riga in [r for r in righe if r.testo][1:])
    risultato = []
    aperto = None

    def chiudi(fine):
        nonlocal aperto
        if aperto is not None:
            risultato.append([aperto[0], fine, aperto[1]])
            aperto = None

    for riga in righe:
        if not riga.testo:
            chiudi(riga.inizio)
        elif aperto is None or not per_strofa or riga.strofa:
            chiudi(riga.inizio)
            aperto = [riga.inizio, [riga.testo], riga.inizio]
        else:
            aperto[1].append(riga.testo)
            aperto[2] = riga.inizio
    if aperto is not None:
        chiudi(aperto[2] + DURATA_DELL_ULTIMA)
    uniti = []
    for inizio, fine, testi in risultato:
        inizio, fine = max(0.0, inizio - anticipo), max(0.0, fine - anticipo)
        if uniti and inizio - uniti[-1][0] < DURATA_MINIMA:
            uniti[-1][1] = max(uniti[-1][1], fine)
            uniti[-1][2] = uniti[-1][2] + testi
            continue
        if uniti:
            uniti[-1][1] = min(uniti[-1][1], inizio)
        uniti.append([inizio, fine, list(testi)])
    return [(inizio, max(fine, inizio + DURATA_MINIMA), "\n".join(testi)) for inizio, fine, testi in uniti]


def titolo(fonte):
    """Il titolo della traccia del karaoke, con la fonte: Testo del karaoke, dal MIDI."""
    return f"{TITOLO}, {FONTI[fonte]}"


def traccia(righe, modo="riga", anticipo=0.0):
    """Il testo SubRip della traccia del karaoke."""
    return formati.testo_srt(blocchi(righe, modo, anticipo))
