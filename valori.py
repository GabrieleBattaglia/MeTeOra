# MeTeOra, i valori scritti nei campi delle impostazioni: dal testo al valore, con le correzioni dette a chi scrive.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.51.0, per la finestra delle impostazioni (tappa 3, issue 14, piano 5.8); leggi_tempo e secondi_da_leggere arrivano da finestra.py. Nella 1.51.2 leggi_tempo accetta solo le cifre: prima passavano inf e 1e5.

"""I valori delle impostazioni, letti dal testo scritto nei campi.

Ogni voce della finestra delle impostazioni apre un campo come quello dei
filtri (piano 5.8): le righe che cominciano con il dollaro spiegano la voce,
e si scrive nell'ultima. Le funzioni leggi_* ricevono il testo gia' senza
quelle righe, con le righe rimaste unite da spazi, e restituiscono
(valore, correzioni): correzioni e' la lista delle frasi per chi scrive,
vuota se niente e' stato corretto. Correggere vuol dire portare al limite un
numero che lo supera, e dirlo; gli spazi in piu' e la virgola dei decimali
si normalizzano senza dirlo. Tutto il resto si rifiuta con ErroreValore, la
cui frase dice cosa non va e cosa ci si aspetta. Ogni frase comincia con il
nome dell'impostazione, perche' finisce nella console.

Qui stanno anche i limiti dei valori, che impostazioni.py usa per
controllare il file, e la lettura dei tempi che serve anche ai tasti della
finestra principale. Niente wx: sono funzioni pure.
"""

import math
import re

# Il volume della musica arriva fino a 300, come motore.VOLUME_MASSIMO: motore
# non si importa, perche' caricherebbe mpv e le sue librerie.
VOLUME_MASSIMO = 300
PASSO_VOLUME_MINIMO, PASSO_VOLUME_MASSIMO = 1, 50
# I salti di Q ed E, in secondi.
SECONDI_MINIMI = 0.1
RIGHE_MINIME = 100
# Le dimensioni dei caratteri, in punti.
CARATTERI_MINIMI, CARATTERI_MASSIMI = 6, 72
# I colori si scrivono in percentuali intere di rosso, verde e blu.
PERCENTUALE_MASSIMA = 100
COMPONENTI = ("rosso", "verde", "blu")
# Le tre aree della finestra, con la lettera che le indica nei campi.
AREE = {"p": "plancia", "c": "console", "t": "cruscotto"}
# Le risposte a una domanda si' o no, gia' in minuscolo.
SI = frozenset({"sì", "si", "sí", "si'", "s", "1", "acceso", "vero"})
NO = frozenset({"no", "n", "0", "spento", "falso"})

_CIFRE = re.compile(r"[0-9]+")
_INTERO = re.compile(r"[+-]?[0-9]+")
_DECIMALE = re.compile(r"[+-]?(?:[0-9]+[.,][0-9]*|[.,][0-9]+)")
# L'ultima parte di un tempo: i secondi, con i decimali dopo il punto.
_SECONDI = re.compile(r"[0-9]+(?:\.[0-9]*)?|\.[0-9]+")


class ErroreValore(ValueError):
    """Il testo scritto non si puo' usare; il messaggio, per chi scrive, dice
    cosa non va e cosa ci si aspetta."""


def _pulito(testo):
    """Il testo senza spazi in testa e in coda, con gli spazi di fila ridotti a uno."""
    return " ".join(testo.split())


def leggi_tempo(testo):
    """Da '90', '1.5', '1:30', '1:30,25' o '1:02:03' a secondi; None se non si
    capisce. I due punti separano ore, minuti e secondi; il punto o la
    virgola separano i decimali, solo nell'ultima parte. Valgono solo le
    cifre: segni, esponenti, inf e nan, che float() accetterebbe, no."""
    parti = [p.strip() for p in testo.strip().replace(",", ".").split(":")]
    if not 1 <= len(parti) <= 3 or not all(_CIFRE.fullmatch(p) for p in parti[:-1]) or not _SECONDI.fullmatch(parti[-1]):
        return None
    try:
        numeri = [int(p) for p in parti[:-1]] + [float(parti[-1])]
        if any(n >= 60 for n in numeri[1:]):
            return None
        totale = 0.0
        for n in numeri:
            totale = totale * 60 + n
    except (ValueError, OverflowError):
        # Numeri di centinaia di cifre: int() ne accetta al massimo 4300, e
        # un intero enorme non diventa float.
        return None
    return totale if math.isfinite(totale) else None


def secondi_da_leggere(secondi):
    """Un numero di secondi da leggere: 10, oppure 1.5."""
    return f"{secondi:.3f}".rstrip("0").rstrip(".")


def _nei_limiti(numero, minimo, massimo, nome, scritto=str):
    """Il numero portato fra minimo e massimo (massimo None: senza limite in
    alto), con la frase che lo dice se e' cambiato; scritto da' la forma da
    leggere dei numeri."""
    if numero < minimo:
        return minimo, [f"{nome}: {scritto(numero)} è sotto il minimo, ho messo {scritto(minimo)}."]
    if massimo is not None and numero > massimo:
        return massimo, [f"{nome}: {scritto(numero)} è oltre il massimo, ho messo {scritto(massimo)}."]
    return numero, []


def leggi_intero(testo, minimo, massimo, nome):
    """Un numero intero da minimo a massimo; massimo None vuol dire senza
    limite in alto. Fuori dai limiti si porta al limite, e lo si dice; i
    decimali, con la virgola o con il punto, si rifiutano."""
    testo = _pulito(testo)
    attesa = f"un numero intero da {minimo} in su" if massimo is None else f"un numero intero da {minimo} a {massimo}"
    if not testo:
        raise ErroreValore(f"{nome}: manca il numero; scrivi {attesa}.")
    if " " in testo:
        raise ErroreValore(f"{nome}: {testo} non è un numero solo; scrivi {attesa}.")
    if _DECIMALE.fullmatch(testo):
        raise ErroreValore(f"{nome}: {testo} non è un numero intero; scrivi {attesa}, senza decimali.")
    non_numero = f"{nome}: {testo} non è un numero; scrivi {attesa}."
    if not _INTERO.fullmatch(testo):
        raise ErroreValore(non_numero)
    try:
        numero = int(testo)
    except ValueError:
        # Oltre le 4300 cifre int() non converte.
        raise ErroreValore(non_numero) from None
    return _nei_limiti(numero, minimo, massimo, nome)


def leggi_volume_musica(testo):
    """Il volume della musica, da 0 a 300: oltre il 100 mpv amplifica."""
    return leggi_intero(testo, 0, VOLUME_MASSIMO, "Volume della musica")


def leggi_passo_volume(testo):
    """Di quanto cambiano il volume i tasti piu' e meno, da 1 a 50."""
    return leggi_intero(testo, PASSO_VOLUME_MINIMO, PASSO_VOLUME_MASSIMO, "Passo del volume")


def leggi_volume_effetti(testo):
    """Il volume degli effetti sonori, scritto in percentuale da 0 a 100
    (anche con il segno di percento dopo) e restituito da 0 a 1: "35" da'
    0.35."""
    testo = _pulito(testo).removesuffix("%")
    percentuale, correzioni = leggi_intero(testo, 0, PERCENTUALE_MASSIMA, "Volume degli effetti")
    return percentuale / 100, correzioni


def leggi_secondi(testo, nome="Salto"):
    """Un salto in secondi, scritto come leggi_tempo lo capisce (90, 1.5,
    1,5, 1:30, 1:30,25, 1:02:03), arrotondato al millesimo e almeno di 0.1:
    sotto si porta a 0.1, e lo si dice. nome e' quello dell'impostazione,
    per esempio "Salto indietro di Q"."""
    testo = _pulito(testo)
    if not testo:
        raise ErroreValore(f"{nome}: mancano i secondi; scrivi per esempio 10 o 2.5, oppure minuti e secondi come 1:30.")
    secondi = leggi_tempo(testo)
    if secondi is None:
        raise ErroreValore(f"{nome}: {testo} non è un numero di secondi; scrivi per esempio 10 o 2.5, oppure minuti e secondi come 1:30.")
    return _nei_limiti(round(secondi, 3), SECONDI_MINIMI, None, nome, secondi_da_leggere)


def leggi_si_no(testo, nome="Inseguimento della plancia"):
    """Si' o no: sì, si, s, 1, acceso e vero valgono True; no, n, 0, spento e
    falso valgono False; le maiuscole non contano."""
    testo = _pulito(testo)
    risposta = testo.casefold()
    if risposta in SI:
        return True, []
    if risposta in NO:
        return False, []
    if not testo:
        raise ErroreValore(f"{nome}: manca la risposta; scrivi sì o no.")
    raise ErroreValore(f"{nome}: {testo} non è né sì né no; scrivi sì o no.")


def leggi_righe_della_console(testo):
    """Quante righe tiene la console: almeno 100, senza massimo."""
    return leggi_intero(testo, RIGHE_MINIME, None, "Righe della console")


def leggi_caratteri(testo):
    """Le dimensioni dei caratteri in punti, da 6 a 72: tre numeri, per
    plancia, console e cruscotto, oppure uno solo che vale per tutte e tre.
    Restituisce {"p": n, "c": n, "t": n}; il testo vuoto da' un dizionario
    vuoto, cioe' il carattere di Windows in tutte e tre le aree."""
    nome = "Dimensioni dei caratteri"
    parole = _pulito(testo).split()
    if not parole:
        return {}, []
    if len(parole) == 1:
        punti, correzioni = leggi_intero(parole[0], CARATTERI_MINIMI, CARATTERI_MASSIMI, nome)
        return dict.fromkeys(AREE, punti), correzioni
    if len(parole) != len(AREE):
        raise ErroreValore(f"{nome}: {' '.join(parole)} sono {len(parole)} valori; scrivi un numero solo, che vale per tutte e tre le aree, oppure tre numeri, per plancia, console e cruscotto, ciascuno da {CARATTERI_MINIMI} a {CARATTERI_MASSIMI}.")
    caratteri, correzioni = {}, []
    for area, parola in zip(AREE, parole, strict=True):
        caratteri[area], corrette = leggi_intero(parola, CARATTERI_MINIMI, CARATTERI_MASSIMI, f"{nome}, {AREE[area]}")
        correzioni += corrette
    return caratteri, correzioni


def _colore(parola, nome):
    """Una parola del campo dei colori: (area, [r, g, b]) oppure (area, None)
    per la lettera da sola."""
    if not parola[0].isalpha():
        raise ErroreValore(f"{nome}: davanti a {parola} manca la lettera dell'area, p plancia, c console o t cruscotto; per esempio p31.31.31.")
    area, resto = parola[0].casefold(), parola[1:]
    if area not in AREE:
        raise ErroreValore(f"{nome}: in {parola}, {parola[0]} non è un'area; le aree sono p plancia, c console e t cruscotto, per esempio p31.31.31.")
    if not resto:
        return area, None
    parti = resto.split(".")
    errore = f"{nome}: in {parola} servono tre percentuali intere da 0 a {PERCENTUALE_MASSIMA}, per rosso, verde e blu, separate dal punto, per esempio {area}31.31.31; la lettera da sola torna ai colori di Windows."
    if len(parti) != len(COMPONENTI) or not all(_CIFRE.fullmatch(p) for p in parti):
        raise ErroreValore(errore)
    try:
        return area, [int(p) for p in parti]
    except ValueError:
        raise ErroreValore(errore) from None


def leggi_colori(testo, nome="Colori"):
    """I colori delle aree: zero o piu' parole separate da spazi, ciascuna con
    la lettera dell'area (p plancia, c console, t cruscotto, maiuscole
    indifferenti) seguita da tre percentuali intere di rosso, verde e blu
    separate dal punto (p31.31.31), oppure da niente: la lettera da sola
    riporta quell'area ai colori di Windows. Oltre 100 si porta a 100; la
    stessa area scritta due volte prende l'ultima. Una lettera staccata dalle
    sue percentuali (p 31.31.31) si riattacca.
    Restituisce i cambi: area -> [r, g, b], oppure area -> None per tornare
    ai colori di Windows; le aree non scritte non cambiano, e il testo vuoto
    da' un dizionario vuoto. Li applica unisci_colori. nome e' quello
    dell'impostazione, per esempio "Colori dello sfondo"."""
    parole = []
    for parola in _pulito(testo).split():
        if parole and len(parole[-1]) == 1 and parole[-1].isalpha() and parola[0].isdigit():
            parole[-1] += parola
        else:
            parole.append(parola)
    colori, correzioni = {}, []
    for parola in parole:
        area, percentuali = _colore(parola, nome)
        if area in colori:
            # Tolta e rimessa, cosi' l'ordine e' quello dell'ultima volta.
            del colori[area]
            correzioni.append(f"{nome}, {AREE[area]}: due valori, vale l'ultimo.")
        colori[area] = percentuali
    for area, percentuali in colori.items():
        if percentuali is None:
            continue
        for i, componente in enumerate(COMPONENTI):
            percentuali[i], corrette = _nei_limiti(percentuali[i], 0, PERCENTUALE_MASSIMA, f"{nome}, {AREE[area]}, {componente}")
            correzioni += corrette
    return colori, correzioni


def unisci_colori(attuali, cambi):
    """I colori salvati dopo i cambi di leggi_colori: un'area con None torna ai
    colori di Windows, cioe' sparisce; le aree non toccate restano. Un
    dizionario nuovo, con le aree nell'ordine plancia, console, cruscotto."""
    nuovi = {area: list(rgb) for area, rgb in attuali.items()}
    for area, rgb in cambi.items():
        if rgb is None:
            nuovi.pop(area, None)
        else:
            nuovi[area] = list(rgb)
    return {area: nuovi[area] for area in AREE if area in nuovi}


def scrivi_colori(colori):
    """La forma scritta dei colori, come la legge leggi_colori: "p31.31.31
    c100.100.100", nell'ordine plancia, console, cruscotto; un'area con None
    e' la sua lettera da sola, il dizionario vuoto il testo vuoto."""
    return " ".join(area + ("" if colori[area] is None else ".".join(str(p) for p in colori[area])) for area in AREE if area in colori)


def percentuali_da_colore(r, g, b):
    """Da tre livelli da 0 a 255 alle tre percentuali intere da 0 a 100."""
    return [round(v * 100 / 255) for v in (r, g, b)]


def colore_da_percentuali(percentuali):
    """Da tre percentuali da 0 a 100 ai tre livelli da 0 a 255, per wx.Colour:
    con percentuali_da_colore l'andata e ritorno e' esatta per ogni
    percentuale intera."""
    return tuple(round(p * 255 / 100) for p in percentuali)
