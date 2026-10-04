# MeTeOra, i valori scritti nei campi delle impostazioni: dal testo al valore, con le correzioni dette a chi scrive.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.51.0, per la finestra delle impostazioni (tappa 3, issue 14, piano 5.8); leggi_tempo e secondi_da_leggere arrivano da finestra.py. Nella 1.51.2 leggi_tempo accetta solo le cifre: prima passavano inf e 1e5. Nella 1.55.0 velocita', tono, bande dell'equalizzatore e dissolvenza, con i loro limiti e le loro forme da leggere (tappa 4, issue 15). Nella 1.59.2 velocita' e dissolvenza si scrivono con il punto, come il resto di MeTeOra. Nella 1.60.0 leggi_tempo_nel_brano, per W, anche dalla fine. Nella 1.61.0 i modelli della riproduzione casuale. Nella 1.82.0 l'anticipo del karaoke. Nella 1.83.0 le celle della barra braille e il tempo minimo di lettura. Nella 1.88.0 tempo() arriva da finestra.py, per la linea del tempo della barra.

"""I valori delle impostazioni, letti dal testo scritto nei campi.

Ogni voce della finestra delle impostazioni apre un campo come quello dei
filtri (piano 5.8): le righe che cominciano con il dollaro spiegano la voce,
e si scrive nell'ultima. Le funzioni leggi_* ricevono il testo gia' senza
quelle righe, con le righe rimaste unite da spazi, e restituiscono
(valore, correzioni): correzioni e' la lista delle frasi per chi scrive,
vuota se niente e' stato corretto. Correggere vuol dire portare al limite un
numero che lo supera, o al passo una velocita' che non ci cade, e dirlo; gli
spazi in piu' e la virgola dei decimali si normalizzano senza dirlo. Tutto
il resto si rifiuta con ErroreValore, la cui frase dice cosa non va e cosa
ci si aspetta. Ogni frase comincia con il nome dell'impostazione, perche'
finisce nella console.

Le funzioni scrivi_* danno la forma da leggere di un valore, per le righe
della console e delle impostazioni; quella di scrivi_colori, scrivi_velocita,
scrivi_tono, scrivi_bande e scrivi_dissolvenza si rilegge con la sua leggi_*
e da' lo stesso valore, senza correzioni.

Qui stanno anche i limiti dei valori, che impostazioni.py usa per
controllare il file, e la lettura dei tempi che serve anche ai tasti della
finestra principale. Niente wx: sono funzioni pure.
"""

import math
import re
from decimal import ROUND_HALF_UP, Decimal

# Il volume della musica arriva fino a 300, come motore.VOLUME_MASSIMO: motore
# non si importa, perche' caricherebbe mpv e le sue librerie.
VOLUME_MASSIMO = 300
PASSO_VOLUME_MINIMO, PASSO_VOLUME_MASSIMO = 1, 50
# I salti di Q ed E, in secondi.
SECONDI_MINIMI = 0.1
RIGHE_MINIME = 100
# L'anticipo del testo del karaoke, in millesimi di secondo (1.82.0).
ANTICIPO_MASSIMO_DEL_KARAOKE = 10000
# La barra braille a blocchi (1.83.0): le celle della barra, 0 per il testo
# intero, e il tempo minimo di lettura di un blocco, in millesimi.
CELLE_MASSIME = 160
# Oltre quanti minuti un file riprende dal punto lasciato (1.92.0): 0 mai.
RIPRESA_MASSIMA = 600
# Il timer di spegnimento (1.95.0): al massimo dieci ore; e la scelta della
# fine del brano, scritta f o fine.
TIMER_MASSIMO = 600
FINE_DEL_BRANO = "fine"
LETTURA_MINIMA, LETTURA_MASSIMA = 100, 60000
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
# La velocita' di riproduzione (tappa 4): 1 e' la normale, i tasti A e D la
# cambiano di un passo.
VELOCITA_MINIMA, VELOCITA_MASSIMA = 0.5, 2.0
PASSO_VELOCITA = 0.05
# Il tono in semitoni e il guadagno di ogni banda dell'equalizzatore in dB
# vanno da meno a piu' il loro massimo, interi.
TONO_MASSIMO = 12
GUADAGNO_MASSIMO = 12
# Le frequenze centrali delle sette bande dell'equalizzatore, in Hz, dalla
# piu' bassa alla piu' alta: la banda 1 e' quella dei 60.
FREQUENZE_DELLE_BANDE = (60, 150, 400, 1000, 2400, 6000, 12000)
# La durata della dissolvenza incrociata, in secondi.
DISSOLVENZA_MINIMA, DISSOLVENZA_MASSIMA = 0.5, 15
# I modelli della riproduzione casuale (Gabriele, collaudo della 1.60.1): il
# nome salvato nelle impostazioni e la forma da leggere. Con i due modelli a
# mazzo ogni brano suona una volta; finito il mazzo, ci si ferma o si
# ricomincia.
MODELLI_CASUALI = {
    "totale": "casualità totale",
    "una_volta": "una volta per brano, poi si ferma",
    "a_giro": "una volta per brano, poi ricomincia",
}
# La ripetizione (1.94.0), a giro con Maiuscolo con V: il nome salvato nelle
# impostazioni e la forma da leggere.
RIPETIZIONI = {
    "spenta": "spenta",
    "brano": "del brano",
    "lista": "della lista",
}
# Il volume uniforme con ReplayGain (1.96.0): il nome salvato nelle
# impostazioni e la forma da leggere.
VOLUMI_UNIFORMI = {
    "spento": "spento",
    "brano": "per brano",
    "album": "per album",
}
# Le parole che accendono e spengono la dissolvenza: quelle del si' e del no,
# senza le cifre, che li' sono secondi, e anche al femminile.
_ACCESA = frozenset(parola for parola in SI if not parola.isdigit()) | {"accesa"}
_SPENTA = frozenset(parola for parola in NO if not parola.isdigit()) | {"spenta"}

_CIFRE = re.compile(r"[0-9]+")
_INTERO = re.compile(r"[+-]?[0-9]+")
_DECIMALE = re.compile(r"[+-]?(?:[0-9]+[.,][0-9]*|[.,][0-9]+)")
# Un numero, intero o con i decimali dopo il punto o la virgola.
_NUMERO = re.compile(r"[+-]?(?:[0-9]+(?:[.,][0-9]*)?|[.,][0-9]+)")
# L'ultima parte di un tempo: i secondi, con i decimali dopo il punto.
_SECONDI = re.compile(r"[0-9]+(?:\.[0-9]*)?|\.[0-9]+")
# Il tono, con la parola semitoni (o semitono) dopo il numero.
_SEMITONI = re.compile(r"(.*?) ?semiton[oi]", re.IGNORECASE)
# La durata della dissolvenza: il numero, con o senza la parola secondi
# (secondo, sec, s) e il punto finale.
_DURATA = re.compile(rf"(?P<numero>{_NUMERO.pattern}) ?(?:secondi|secondo|sec|s)?\.?", re.IGNORECASE)


class ErroreValore(ValueError):
    """Il testo scritto non si puo' usare; il messaggio, per chi scrive, dice
    cosa non va e cosa ci si aspetta."""


def _pulito(testo):
    """Il testo senza spazi in testa e in coda, con gli spazi di fila ridotti a uno."""
    return " ".join(testo.split())


def leggi_tempo(testo):
    """Da '90', '1.5', '1:30', '1:30.25' o '1:02:03' a secondi; None se non si
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


def leggi_tempo_nel_brano(testo, durata):
    """Il tempo di W in secondi dall'inizio del brano: come leggi_tempo,
    oppure, con il meno davanti, contato dalla fine, -12 o -1:30, se la
    durata si sa (Gabriele, 2 ottobre 2026). None se non si capisce o se
    cade fuori dal brano."""
    testo = testo.strip()
    if testo.startswith("-"):
        indietro = leggi_tempo(testo[1:])
        secondi = None if indietro is None or durata is None else durata - indietro
    else:
        secondi = leggi_tempo(testo)
    if secondi is None or secondi < 0 or (durata is not None and secondi > durata):
        return None
    return secondi


def tempo(secondi):
    """m:ss, oppure h:mm:ss oltre l'ora; ? se non si sa."""
    if secondi is None:
        return "?"
    secondi = max(0, int(secondi))
    ore, resto = divmod(secondi, 3600)
    minuti, secondi = divmod(resto, 60)
    return f"{ore}:{minuti:02d}:{secondi:02d}" if ore else f"{minuti}:{secondi:02d}"


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


def leggi_intero(testo, minimo, massimo, nome, scritto=str):
    """Un numero intero da minimo a massimo; massimo None vuol dire senza
    limite in alto. Fuori dai limiti si porta al limite, e lo si dice; i
    decimali, con la virgola o con il punto, si rifiutano. scritto da' la
    forma da leggere dei numeri nelle frasi, per esempio con il segno."""
    testo = _pulito(testo)
    attesa = f"un numero intero da {scritto(minimo)} in su" if massimo is None else f"un numero intero da {scritto(minimo)} a {scritto(massimo)}"
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
    return _nei_limiti(numero, minimo, massimo, nome, scritto)


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
    1.5, 1:30, 1:30.25, 1:02:03), arrotondato al millesimo e almeno di 0.1:
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


def leggi_anticipo_del_karaoke(testo):
    """Quanti millesimi prima del canto arriva il testo del karaoke."""
    return leggi_intero(testo, 0, ANTICIPO_MASSIMO_DEL_KARAOKE, "Anticipo del karaoke")


def leggi_ripresa_oltre(testo):
    """Oltre quanti minuti un file riprende dal punto lasciato: 0 mai."""
    return leggi_intero(testo, 0, RIPRESA_MASSIMA, "Punto lasciato dei file lunghi")


def leggi_timer(testo):
    """Il timer di spegnimento (1.95.0): (minuti, correzioni), con 0 per
    toglierlo, oppure (FINE_DEL_BRANO, []) per la fine del brano."""
    if _pulito(testo).lower() in ("f", "fine"):
        return FINE_DEL_BRANO, []
    try:
        return leggi_intero(testo, 0, TIMER_MASSIMO, "Timer di spegnimento")
    except ErroreValore as e:
        raise ErroreValore(f"{e} Oppure f, per fermarla alla fine del brano.") from None


def leggi_celle_braille(testo):
    """Quante celle ha la barra braille: 0 per il testo intero."""
    return leggi_intero(testo, 0, CELLE_MASSIME, "Celle della barra braille")


def leggi_lettura_minima(testo):
    """Il tempo minimo di lettura di un blocco sulla barra, in millesimi."""
    return leggi_intero(testo, LETTURA_MINIMA, LETTURA_MASSIMA, "Tempo minimo di lettura in braille")


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


# Velocita', tono, equalizzatore e dissolvenza, tappa 4 (issue 15).

def _con_il_punto(numero, decimali):
    """Un numero da leggere, float o Decimal, con al piu' decimali cifre dopo
    il punto e senza gli zeri che non servono: 1.05, 0.5, 2. Dalla 1.59.2 il
    punto, come in tutta MeTeOra: prima qui c'era la virgola."""
    return f"{numero:.{decimali}f}".rstrip("0").rstrip(".")


def _con_segno(numero):
    """Un intero da leggere con il segno davanti, se non e' zero: +2, -3, 0."""
    return f"{numero:+d}" if numero else "0"


def _decimale(testo):
    """Il numero scritto, con i decimali dopo il punto o la virgola, come
    Decimal esatto; None se non e' un numero. Valgono solo le cifre, con il
    segno davanti: niente esponenti, inf o nan, che Decimal accetterebbe.
    Un Decimal regge anche migliaia di cifre, senza i limiti di int e float."""
    return Decimal(testo.replace(",", ".")) if _NUMERO.fullmatch(testo) else None


def _decimale_nei_limiti(numero, scritto, minimo, massimo, nome, da_leggere):
    """Come _nei_limiti, per un numero letto con _decimale: numero e' il
    Decimal, scritto la forma in cui l'ha scritto chi scrive, e il limite
    torna come Decimal; da_leggere da' la forma da leggere dei limiti."""
    minimo, massimo = Decimal(str(minimo)), Decimal(str(massimo))
    if numero < minimo:
        return minimo, [f"{nome}: {scritto} è sotto il minimo, ho messo {da_leggere(minimo)}."]
    if numero > massimo:
        return massimo, [f"{nome}: {scritto} è oltre il massimo, ho messo {da_leggere(massimo)}."]
    return numero, []


def scrivi_velocita(velocita):
    """La velocita' da leggere, con il punto e al centesimo: 1.05, 0.5, 1."""
    return _con_il_punto(velocita, 2)


def leggi_velocita(testo):
    """La velocita' di riproduzione, da 0.5 a 2, 1 la normale, con i decimali
    dopo il punto o la virgola: 1.05 o 1,05. Fuori dai limiti si porta al
    limite; dentro si arrotonda al passo di 0.05, la meta' in su, cosi' i
    tasti A e D ripartono da un valore del passo. L'una e l'altra correzione
    si dicono. Restituisce un float."""
    nome = "Velocità"
    testo = _pulito(testo)
    attesa = f"scrivi un numero da {scrivi_velocita(VELOCITA_MINIMA)} a {scrivi_velocita(VELOCITA_MASSIMA)}, per esempio 1.05 o 0.9; 1 è la velocità normale"
    if not testo:
        raise ErroreValore(f"{nome}: manca il numero; {attesa}.")
    numero = _decimale(testo)
    if numero is None:
        raise ErroreValore(f"{nome}: {testo} non è un numero; {attesa}.")
    scritto = testo.replace(",", ".")
    numero, correzioni = _decimale_nei_limiti(numero, scritto, VELOCITA_MINIMA, VELOCITA_MASSIMA, nome, scrivi_velocita)
    # Il calcolo in Decimal e' esatto: in float 1.025 / 0.05 fa 20.4999...
    # e la meta' andrebbe in giu'.
    passo = Decimal(str(PASSO_VELOCITA))
    al_passo = (numero / passo).to_integral_value(rounding=ROUND_HALF_UP) * passo
    velocita = float(al_passo)
    if al_passo != numero:
        correzioni.append(f"{nome}: {scritto} va a passi di {scrivi_velocita(PASSO_VELOCITA)}, ho messo {scrivi_velocita(velocita)}.")
    return velocita, correzioni


def scrivi_tono(semitoni):
    """Il tono da leggere: +2 semitoni, -1 semitono, 0 semitoni."""
    return f"{_con_segno(semitoni)} {'semitono' if abs(semitoni) == 1 else 'semitoni'}"


def leggi_tono(testo):
    """Il tono in semitoni, un intero da -12 a +12, 0 il normale: +2, 2, -3.
    La parola semitoni (o semitono) dopo il numero si accetta, cosi' si
    rilegge anche la forma di scrivi_tono. Fuori dai limiti si porta al
    limite, e lo si dice."""
    testo = _pulito(testo)
    con_la_parola = _SEMITONI.fullmatch(testo)
    if con_la_parola:
        testo = con_la_parola.group(1)
    return leggi_intero(testo, -TONO_MASSIMO, TONO_MASSIMO, "Tono", _con_segno)


def nome_della_banda(indice):
    """Il nome di una banda dell'equalizzatore, con l'indice contato da zero:
    "banda 3, 400 Hz" per l'indice 2."""
    return f"banda {indice + 1}, {FREQUENZE_DELLE_BANDE[indice]} Hz"


def scrivi_guadagno(guadagno):
    """Il guadagno di una banda da leggere: +2 dB, 0 dB, -3 dB."""
    return f"{_con_segno(guadagno)} dB"


def scrivi_bande(bande):
    """I guadagni delle bande separati da spazi, nella forma che rilegge
    leggi_bande: "0 0 +2 0 0 0 -3"."""
    return " ".join(map(_con_segno, bande))


def leggi_bande(testo):
    """I guadagni delle sette bande dell'equalizzatore, in dB interi da -12 a
    +12: sette numeri separati da spazi, dalla banda piu' bassa alla piu'
    alta, oppure uno solo, che vale per tutte; il testo vuoto le azzera
    tutte. Fuori dai limiti si porta al limite, banda per banda, e lo si
    dice. Restituisce una lista nuova di sette interi."""
    nome = "Equalizzatore"
    quante = len(FREQUENZE_DELLE_BANDE)
    parole = _pulito(testo).split()
    if not parole:
        return [0] * quante, []
    if len(parole) == 1:
        guadagno, correzioni = leggi_intero(parole[0], -GUADAGNO_MASSIMO, GUADAGNO_MASSIMO, nome, _con_segno)
        return [guadagno] * quante, correzioni
    if len(parole) != quante:
        raise ErroreValore(f"{nome}: {' '.join(parole)} sono {len(parole)} valori; scrivi un numero solo, che vale per tutte le bande, oppure sette numeri, uno per banda dalla più bassa alla più alta, ciascuno da {_con_segno(-GUADAGNO_MASSIMO)} a {_con_segno(GUADAGNO_MASSIMO)}; il campo vuoto le azzera tutte.")
    guadagni, correzioni = [], []
    for indice, parola in enumerate(parole):
        guadagno, corrette = leggi_intero(parola, -GUADAGNO_MASSIMO, GUADAGNO_MASSIMO, f"{nome}, {nome_della_banda(indice)}", _con_segno)
        guadagni.append(guadagno)
        correzioni += corrette
    return guadagni, correzioni


def scrivi_durata(secondi):
    """La durata della dissolvenza da leggere, con il punto e al
    millesimo: 4 secondi, 2.5 secondi, 1 secondo."""
    scritto = _con_il_punto(secondi, 3)
    return f"{scritto} {'secondo' if scritto == '1' else 'secondi'}"


def scrivi_dissolvenza(dissolvenza):
    """La dissolvenza da leggere, come la dice la riga delle impostazioni:
    "accesa, 4 secondi" o "spenta, 4 secondi"; leggi_dissolvenza la rilegge."""
    return f"{'accesa' if dissolvenza['accesa'] else 'spenta'}, {scrivi_durata(dissolvenza['secondi'])}"


def _attesa_della_durata():
    """Cosa si aspetta il campo della durata, per le frasi d'errore."""
    return f"scrivi i secondi, da {_con_il_punto(DISSOLVENZA_MINIMA, 3)} a {_con_il_punto(DISSOLVENZA_MASSIMA, 3)}, anche con i decimali, per esempio 4 o 2.5"


def _durata(scritto, nome):
    """I secondi della dissolvenza dal numero scritto, gia' riconosciuto da
    _DURATA: portati fra 0.5 e 15, e lo si dice, poi arrotondati al
    millesimo senza dirlo, come i salti di Q ed E."""
    numero, correzioni = _decimale_nei_limiti(_decimale(scritto), scritto.replace(",", "."), DISSOLVENZA_MINIMA, DISSOLVENZA_MASSIMA, nome,
        lambda limite: _con_il_punto(limite, 3))
    return float(numero.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)), correzioni


def leggi_durata_della_dissolvenza(testo, nome="Dissolvenza"):
    """La durata della dissolvenza in secondi, da 0.5 a 15, con i decimali
    dopo il punto o la virgola, arrotondata al millesimo; dopo il numero si
    accetta la parola secondi (o secondo, sec, s). Fuori dai limiti si porta
    al limite, e lo si dice. Restituisce un float. E' la lettura del campo
    di Maiuscolo+L, che chiede solo la durata; nome comincia le frasi."""
    testo = _pulito(testo)
    if not testo:
        raise ErroreValore(f"{nome}: mancano i secondi; {_attesa_della_durata()}.")
    trovato = _DURATA.fullmatch(testo)
    if not trovato:
        raise ErroreValore(f"{nome}: {testo} non è un numero di secondi; {_attesa_della_durata()}.")
    return _durata(trovato["numero"], nome)


def leggi_dissolvenza(testo, secondi_attuali=None):
    """La dissolvenza incrociata, come {"accesa": vero o falso, "secondi":
    durata}. No (o spenta, spento, n, falso) la spegne, e cosi' lo zero; un
    numero di secondi, letto come in leggi_durata_della_dissolvenza, la
    accende con quella durata; si' (o accesa, acceso, s, vero) la accende
    senza cambiare durata. La parola e il numero possono stare insieme, come
    li scrive scrivi_dissolvenza: "accesa, 4 secondi" o "spenta, 2.5
    secondi", e spenta la durata resta per quando si riaccende.
    Senza numero i secondi sono secondi_attuali, quelli di adesso, che la
    finestra conserva: None se non li passa, e allora li mette lei."""
    nome = "Dissolvenza"
    testo = _pulito(testo)
    attesa = (f"scrivi no per spegnerla, sì per accenderla, oppure i secondi, da {_con_il_punto(DISSOLVENZA_MINIMA, 3)} a "
        f"{_con_il_punto(DISSOLVENZA_MASSIMA, 3)}, per accenderla con quella durata, per esempio 4 o 2.5")
    if not testo:
        raise ErroreValore(f"{nome}: manca il valore; {attesa}.")
    prima, _, resto = testo.partition(" ")
    parola = prima.rstrip(",:;.").casefold()
    if parola in _ACCESA or parola in _SPENTA:
        accesa = parola in _ACCESA
    else:
        accesa, resto = None, testo
    if not resto:
        return {"accesa": accesa, "secondi": secondi_attuali}, []
    trovato = _DURATA.fullmatch(resto)
    if not trovato:
        raise ErroreValore(f"{nome}: {testo} non è né no né un numero di secondi; {attesa}.")
    if accesa is not True and _decimale(trovato["numero"]) == 0:
        # Zero secondi spengono, come la dissolvenza 0 del motore.
        return {"accesa": False, "secondi": secondi_attuali}, []
    secondi, correzioni = _durata(trovato["numero"], nome)
    return {"accesa": accesa is not False, "secondi": secondi}, correzioni
