# MeTeOra, le prove dei valori scritti nei campi delle impostazioni e dei controlli sul file delle impostazioni.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.51.0, insieme a valori.py. Nella 1.55.0 le prove di velocita', tono, bande dell'equalizzatore e dissolvenza.

import json
import os
import re

import pytest

import valori
from impostazioni import CONTROLLI, PREDEFINITE, Impostazioni
from valori import (
    DISSOLVENZA_MASSIMA,
    DISSOLVENZA_MINIMA,
    FREQUENZE_DELLE_BANDE,
    GUADAGNO_MASSIMO,
    PASSO_VELOCITA,
    TONO_MASSIMO,
    VELOCITA_MASSIMA,
    VELOCITA_MINIMA,
    ErroreValore,
    colore_da_percentuali,
    leggi_bande,
    leggi_caratteri,
    leggi_colori,
    leggi_dissolvenza,
    leggi_durata_della_dissolvenza,
    leggi_intero,
    leggi_passo_volume,
    leggi_righe_della_console,
    leggi_secondi,
    leggi_si_no,
    leggi_tempo,
    leggi_tempo_nel_brano,
    leggi_tono,
    leggi_velocita,
    leggi_volume_effetti,
    leggi_volume_musica,
    nome_della_banda,
    percentuali_da_colore,
    scrivi_bande,
    scrivi_colori,
    scrivi_dissolvenza,
    scrivi_durata,
    scrivi_guadagno,
    scrivi_tono,
    scrivi_velocita,
    secondi_da_leggere,
    unisci_colori,
)

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# I tempi, passati qui da finestra.py.

@pytest.mark.parametrize(("testo", "secondi"), [("90", 90), ("1.5", 1.5), ("2,5", 2.5), ("1:30", 90), ("1:30,25", 90.25), ("1:02:03", 3723),
    (" 1 : 30 ", 90), (".5", 0.5), ("5.", 5), ("0", 0), ("75:00", 4500)])
def test_leggi_tempo_capisce_le_forme_di_sempre(testo, secondi):
    assert leggi_tempo(testo) == secondi


@pytest.mark.parametrize("testo", ["", " ", "a", "-5", "+5", "1:75", "1:2:3:4", "1:30.5:00", "1 30", "inf", "nan", "1e5", "1_000", "١٢"])
def test_leggi_tempo_rifiuta_quello_che_non_e_un_tempo(testo):
    assert leggi_tempo(testo) is None


@pytest.mark.parametrize(("testo", "durata", "secondi"), [("4:00", 252.4, 240), ("-12", 252.4, 240.4), (" - 1:30 ", 252.4, 162.4),
    ("-0", 252.4, 252.4), ("4:12", 252.4, 252), ("90", None, 90)])
def test_leggi_tempo_nel_brano_anche_dalla_fine(testo, durata, secondi):
    assert leggi_tempo_nel_brano(testo, durata) == pytest.approx(secondi)


@pytest.mark.parametrize(("testo", "durata"), [("4:13", 252.4), ("-4:13", 252.4), ("-12", None), ("--12", 252.4), ("-", 252.4), ("-x", 252.4), ("", 252.4)])
def test_leggi_tempo_nel_brano_rifiuta_fuori_dal_brano(testo, durata):
    assert leggi_tempo_nel_brano(testo, durata) is None


def test_leggi_tempo_rifiuta_i_numeri_di_centinaia_di_cifre():
    # Fuori dal parametrize: pytest mette il nome della prova in una
    # variabile d'ambiente, e i testi lunghi la farebbero traboccare.
    for testo in ("9" * 400, "9" * 5000, "9" * 5000 + ":00", "9" * 400 + ":00"):
        assert leggi_tempo(testo) is None, len(testo)


def test_secondi_da_leggere():
    assert secondi_da_leggere(10.0) == "10"
    assert secondi_da_leggere(1.25) == "1.25"
    assert secondi_da_leggere(0.1) == "0.1"


# Gli interi.

def test_errore_valore_e_un_value_error():
    assert issubclass(ErroreValore, ValueError)


@pytest.mark.parametrize(("testo", "numero"), [("5", 5), ("  7 ", 7), ("+5", 5), ("007", 7), ("0", 0), ("10", 10)])
def test_leggi_intero_buono(testo, numero):
    assert leggi_intero(testo, 0, 10, "Prova") == (numero, [])


def test_leggi_intero_corregge_ai_limiti():
    assert leggi_intero("-3", 0, 10, "Prova") == (0, ["Prova: -3 è sotto il minimo, ho messo 0."])
    assert leggi_intero("300", 0, 100, "Prova") == (100, ["Prova: 300 è oltre il massimo, ho messo 100."])
    assert leggi_intero("99999999999999999999", 100, None, "Prova") == (99999999999999999999, [])
    assert leggi_intero("50", 100, None, "Prova") == (100, ["Prova: 50 è sotto il minimo, ho messo 100."])


@pytest.mark.parametrize(("testo", "frase"), [
    ("", "Prova: manca il numero; scrivi un numero intero da 1 a 50."),
    ("1.5", "Prova: 1.5 non è un numero intero; scrivi un numero intero da 1 a 50, senza decimali."),
    ("1,5", "Prova: 1,5 non è un numero intero; scrivi un numero intero da 1 a 50, senza decimali."),
    (",5", "Prova: ,5 non è un numero intero; scrivi un numero intero da 1 a 50, senza decimali."),
    ("abc", "Prova: abc non è un numero; scrivi un numero intero da 1 a 50."),
    ("1  000", "Prova: 1 000 non è un numero solo; scrivi un numero intero da 1 a 50."),
    ("5%", "Prova: 5% non è un numero; scrivi un numero intero da 1 a 50."),
    ("١٢", "Prova: ١٢ non è un numero; scrivi un numero intero da 1 a 50."),
])
def test_leggi_intero_rifiuta_e_dice_cosa_aspetta(testo, frase):
    with pytest.raises(ErroreValore) as errore:
        leggi_intero(testo, 1, 50, "Prova")
    assert str(errore.value) == frase


def test_leggi_intero_con_la_forma_da_leggere():
    def con_segno(numero):
        return f"{numero:+d}" if numero else "0"
    assert leggi_intero("+20", -12, 12, "Prova", con_segno) == (12, ["Prova: +20 è oltre il massimo, ho messo +12."])
    assert leggi_intero("-13", -12, 12, "Prova", con_segno) == (-12, ["Prova: -13 è sotto il minimo, ho messo -12."])
    with pytest.raises(ErroreValore, match=r"^Prova: manca il numero; scrivi un numero intero da -12 a \+12\.$"):
        leggi_intero("", -12, 12, "Prova", con_segno)


def test_leggi_intero_senza_massimo_lo_dice_e_regge_le_cifre_infinite():
    with pytest.raises(ErroreValore, match=r"^Prova: manca il numero; scrivi un numero intero da 100 in su\.$"):
        leggi_intero("", 100, None, "Prova")
    with pytest.raises(ErroreValore, match="non è un numero; scrivi un numero intero da 100 in su"):
        leggi_intero("9" * 5000, 100, None, "Prova")


# Volume, passo, effetti, righe.

def test_leggi_volume_musica():
    assert leggi_volume_musica("108") == (108, [])
    assert leggi_volume_musica("300") == (300, [])
    assert leggi_volume_musica("0") == (0, [])
    assert leggi_volume_musica("301") == (300, ["Volume della musica: 301 è oltre il massimo, ho messo 300."])
    assert leggi_volume_musica("-1") == (0, ["Volume della musica: -1 è sotto il minimo, ho messo 0."])
    with pytest.raises(ErroreValore, match=r"^Volume della musica: 80\.5 non è un numero intero; scrivi un numero intero da 0 a 300, senza decimali\.$"):
        leggi_volume_musica("80.5")


def test_il_volume_massimo_e_quello_del_motore():
    with open(os.path.join(RADICE, "motore.py"), encoding="utf-8") as f:
        trovato = re.search(r"^VOLUME_MASSIMO = (\d+)$", f.read(), re.MULTILINE)
    assert trovato and int(trovato.group(1)) == valori.VOLUME_MASSIMO


def test_leggi_passo_volume():
    assert leggi_passo_volume("2") == (2, [])
    assert leggi_passo_volume("50") == (50, [])
    assert leggi_passo_volume("0") == (1, ["Passo del volume: 0 è sotto il minimo, ho messo 1."])
    assert leggi_passo_volume("51") == (50, ["Passo del volume: 51 è oltre il massimo, ho messo 50."])
    with pytest.raises(ErroreValore, match=r"^Passo del volume: x non è un numero; scrivi un numero intero da 1 a 50\.$"):
        leggi_passo_volume("x")


@pytest.mark.parametrize(("testo", "volume"), [("35", 0.35), ("35%", 0.35), (" 35 % ", 0.35), ("0", 0.0), ("100", 1.0), ("50", 0.5), ("7", 0.07)])
def test_leggi_volume_effetti_da_percentuale(testo, volume):
    assert leggi_volume_effetti(testo) == (volume, [])


def test_leggi_volume_effetti_corregge_e_rifiuta():
    assert leggi_volume_effetti("150") == (1.0, ["Volume degli effetti: 150 è oltre il massimo, ho messo 100."])
    assert leggi_volume_effetti("-5") == (0.0, ["Volume degli effetti: -5 è sotto il minimo, ho messo 0."])
    with pytest.raises(ErroreValore, match=r"^Volume degli effetti: 0\.35 non è un numero intero; scrivi un numero intero da 0 a 100, senza decimali\.$"):
        leggi_volume_effetti("0.35")
    with pytest.raises(ErroreValore, match=r"^Volume degli effetti: manca il numero"):
        leggi_volume_effetti("%")


def test_leggi_righe_della_console():
    assert leggi_righe_della_console("5000") == (5000, [])
    assert leggi_righe_della_console("100") == (100, [])
    assert leggi_righe_della_console("1000000") == (1000000, [])
    assert leggi_righe_della_console("50") == (100, ["Righe della console: 50 è sotto il minimo, ho messo 100."])
    with pytest.raises(ErroreValore, match=r"^Righe della console: 1\.000 non è un numero intero; scrivi un numero intero da 100 in su, senza decimali\.$"):
        leggi_righe_della_console("1.000")


# I salti di Q ed E.

@pytest.mark.parametrize(("testo", "secondi"), [("90", 90.0), ("1,5", 1.5), ("1.5", 1.5), ("1:30", 90.0), ("1:30,25", 90.25), ("1:02:03", 3723.0),
    ("0.1", 0.1), ("2.12345", 2.123), ("0.0996", 0.1), ("  10  ", 10.0)])
def test_leggi_secondi_buoni_e_arrotondati(testo, secondi):
    assert leggi_secondi(testo) == (secondi, [])


def test_leggi_secondi_porta_al_minimo_con_il_nome():
    assert leggi_secondi("0,05", "Salto indietro di Q") == (0.1, ["Salto indietro di Q: 0.05 è sotto il minimo, ho messo 0.1."])
    assert leggi_secondi("0") == (0.1, ["Salto: 0 è sotto il minimo, ho messo 0.1."])
    assert leggi_secondi("0:00.0004", "Salto avanti di E") == (0.1, ["Salto avanti di E: 0 è sotto il minimo, ho messo 0.1."])


@pytest.mark.parametrize(("testo", "frase"), [
    ("", "Salto avanti di E: mancano i secondi; scrivi per esempio 10 o 2.5, oppure minuti e secondi come 1:30."),
    ("dieci", "Salto avanti di E: dieci non è un numero di secondi; scrivi per esempio 10 o 2.5, oppure minuti e secondi come 1:30."),
    ("1:75", "Salto avanti di E: 1:75 non è un numero di secondi; scrivi per esempio 10 o 2.5, oppure minuti e secondi come 1:30."),
    ("-5", "Salto avanti di E: -5 non è un numero di secondi; scrivi per esempio 10 o 2.5, oppure minuti e secondi come 1:30."),
    ("inf", "Salto avanti di E: inf non è un numero di secondi; scrivi per esempio 10 o 2.5, oppure minuti e secondi come 1:30."),
])
def test_leggi_secondi_rifiuta(testo, frase):
    with pytest.raises(ErroreValore) as errore:
        leggi_secondi(testo, "Salto avanti di E")
    assert str(errore.value) == frase


# Si' o no.

@pytest.mark.parametrize("testo", ["sì", "Sì", "SI", "si", "si'", "sí", "s", "S", "1", "acceso", "Acceso", "vero", "VERO", "  sì  "])
def test_leggi_si_no_dice_si(testo):
    assert leggi_si_no(testo) == (True, [])


@pytest.mark.parametrize("testo", ["no", "No", "NO", "n", "N", "0", "spento", "Spento", "falso", "FALSO", " no "])
def test_leggi_si_no_dice_no(testo):
    assert leggi_si_no(testo) == (False, [])


def test_leggi_si_no_rifiuta():
    with pytest.raises(ErroreValore, match=r"^Inseguimento della plancia: forse non è né sì né no; scrivi sì o no\.$"):
        leggi_si_no("forse")
    with pytest.raises(ErroreValore, match=r"^Inseguimento della plancia: manca la risposta; scrivi sì o no\.$"):
        leggi_si_no("  ")
    with pytest.raises(ErroreValore, match=r"^Altro: sì no non è né sì né no"):
        leggi_si_no("sì no", "Altro")


# I caratteri.

def test_leggi_caratteri_uno_o_tre():
    assert leggi_caratteri("12") == ({"p": 12, "c": 12, "t": 12}, [])
    assert leggi_caratteri("10 12 14") == ({"p": 10, "c": 12, "t": 14}, [])
    assert leggi_caratteri("  10   12 14 ") == ({"p": 10, "c": 12, "t": 14}, [])
    assert leggi_caratteri("6 72 9") == ({"p": 6, "c": 72, "t": 9}, [])


def test_leggi_caratteri_vuoto_torna_al_carattere_di_windows():
    assert leggi_caratteri("") == ({}, [])
    assert leggi_caratteri("   ") == ({}, [])


def test_leggi_caratteri_corregge_area_per_area():
    assert leggi_caratteri("4") == ({"p": 6, "c": 6, "t": 6}, ["Dimensioni dei caratteri: 4 è sotto il minimo, ho messo 6."])
    assert leggi_caratteri("4 80 12") == ({"p": 6, "c": 72, "t": 12}, [
        "Dimensioni dei caratteri, plancia: 4 è sotto il minimo, ho messo 6.",
        "Dimensioni dei caratteri, console: 80 è oltre il massimo, ho messo 72.",
    ])


def test_leggi_caratteri_rifiuta():
    with pytest.raises(ErroreValore, match=r"^Dimensioni dei caratteri: 10 12 sono 2 valori; scrivi un numero solo, che vale per tutte e tre le aree, oppure tre numeri, per plancia, console e cruscotto, ciascuno da 6 a 72\.$"):
        leggi_caratteri("10 12")
    with pytest.raises(ErroreValore, match=r"^Dimensioni dei caratteri: 1 2 3 4 sono 4 valori"):
        leggi_caratteri("1 2 3 4")
    with pytest.raises(ErroreValore, match=r"^Dimensioni dei caratteri, cruscotto: a non è un numero; scrivi un numero intero da 6 a 72\.$"):
        leggi_caratteri("12 14 a")
    with pytest.raises(ErroreValore, match=r"^Dimensioni dei caratteri: 12,5 non è un numero intero"):
        leggi_caratteri("12,5")


# I colori.

def test_leggi_colori_buoni():
    assert leggi_colori("") == ({}, [])
    assert leggi_colori("p31.31.31") == ({"p": [31, 31, 31]}, [])
    assert leggi_colori("P31.31.31 c100.100.100 T") == ({"p": [31, 31, 31], "c": [100, 100, 100], "t": None}, [])
    assert leggi_colori("c0.0.0 p") == ({"c": [0, 0, 0], "p": None}, [])
    assert leggi_colori("p007.0.5") == ({"p": [7, 0, 5]}, [])


def test_leggi_colori_riattacca_la_lettera_staccata():
    assert leggi_colori("p 31.31.31  c  100.0.0 t") == ({"p": [31, 31, 31], "c": [100, 0, 0], "t": None}, [])


def test_leggi_colori_corregge_oltre_100_e_le_aree_ripetute():
    colori, correzioni = leggi_colori("p150.0.200", "Colori dei caratteri")
    assert colori == {"p": [100, 0, 100]}
    assert correzioni == ["Colori dei caratteri, plancia, rosso: 150 è oltre il massimo, ho messo 100.",
        "Colori dei caratteri, plancia, blu: 200 è oltre il massimo, ho messo 100."]
    colori, correzioni = leggi_colori("p1.1.1 c2.2.2 p300.3.3", "Colori dello sfondo")
    assert list(colori.items()) == [("c", [2, 2, 2]), ("p", [100, 3, 3])]
    assert correzioni == ["Colori dello sfondo, plancia: due valori, vale l'ultimo.",
        "Colori dello sfondo, plancia, rosso: 300 è oltre il massimo, ho messo 100."]
    assert leggi_colori("t5.5.5 t") == ({"t": None}, ["Colori, cruscotto: due valori, vale l'ultimo."])


@pytest.mark.parametrize(("testo", "inizio"), [
    ("x31.31.31", "Colori dello sfondo: in x31.31.31, x non è un'area; le aree sono p plancia, c console e t cruscotto"),
    ("31.31.31", "Colori dello sfondo: davanti a 31.31.31 manca la lettera dell'area"),
    ("p31.31", "Colori dello sfondo: in p31.31 servono tre percentuali intere da 0 a 100, per rosso, verde e blu, separate dal punto, per esempio p31.31.31;"),
    ("C31.31.31.31", "Colori dello sfondo: in C31.31.31.31 servono tre percentuali"),
    ("p31,31,31", "Colori dello sfondo: in p31,31,31 servono tre percentuali"),
    ("p-1.0.0", "Colori dello sfondo: in p-1.0.0 servono tre percentuali"),
    ("p31..31", "Colori dello sfondo: in p31..31 servono tre percentuali"),
    ("p1.5.2.3", "Colori dello sfondo: in p1.5.2.3 servono tre percentuali"),
    ("pc", "Colori dello sfondo: in pc servono tre percentuali"),
    ("p31.31.31 5", "Colori dello sfondo: davanti a 5 manca la lettera dell'area"),
])
def test_leggi_colori_rifiuta(testo, inizio):
    with pytest.raises(ErroreValore) as errore:
        leggi_colori(testo, "Colori dello sfondo")
    assert str(errore.value).startswith(inizio)


def test_leggi_colori_le_cifre_infinite():
    with pytest.raises(ErroreValore, match=r"^Colori: in p999"):
        leggi_colori("p" + "9" * 5000 + ".0.0")
    assert leggi_colori("p" + "9" * 400 + ".0.0")[0] == {"p": [100, 0, 0]}


def test_unisci_colori():
    attuali = {"c": [1, 2, 3], "p": [4, 5, 6]}
    assert unisci_colori(attuali, {"p": None, "t": [7, 8, 9]}) == {"c": [1, 2, 3], "t": [7, 8, 9]}
    assert attuali == {"c": [1, 2, 3], "p": [4, 5, 6]}
    uguali = unisci_colori(attuali, {})
    assert list(uguali.items()) == [("p", [4, 5, 6]), ("c", [1, 2, 3])]
    assert uguali["p"] is not attuali["p"]
    assert unisci_colori({}, {"c": None}) == {}


def test_scrivi_colori_e_il_ritorno():
    assert scrivi_colori({}) == ""
    assert scrivi_colori({"c": [100, 100, 100], "p": [31, 31, 31]}) == "p31.31.31 c100.100.100"
    assert scrivi_colori({"t": None, "p": [0, 5, 10]}) == "p0.5.10 t"
    for colori in ({}, {"p": [31, 31, 31]}, {"p": [0, 0, 0], "c": [100, 50, 0], "t": [1, 2, 3]}, {"c": None}):
        assert leggi_colori(scrivi_colori(colori)) == (colori, [])


def test_percentuali_e_livelli_andata_e_ritorno():
    for p in range(101):
        assert percentuali_da_colore(*colore_da_percentuali([p, p, p])) == [p, p, p]
    assert colore_da_percentuali([31, 31, 31]) == (79, 79, 79)
    assert colore_da_percentuali([100, 0, 50]) == (255, 0, 128)
    assert percentuali_da_colore(255, 0, 128) == [100, 0, 50]


# I limiti della tappa 4.

def test_limiti_della_tappa_4():
    assert (VELOCITA_MINIMA, VELOCITA_MASSIMA, PASSO_VELOCITA) == (0.5, 2, 0.05)
    assert (TONO_MASSIMO, GUADAGNO_MASSIMO) == (12, 12)
    assert (DISSOLVENZA_MINIMA, DISSOLVENZA_MASSIMA) == (0.5, 15)
    assert FREQUENZE_DELLE_BANDE == (60, 150, 400, 1000, 2400, 6000, 12000)
    # I limiti della velocita' cadono sul passo: arrotondare un valore dentro
    # i limiti non lo porta mai fuori.
    for limite in (VELOCITA_MINIMA, VELOCITA_MASSIMA):
        assert abs(limite / PASSO_VELOCITA - round(limite / PASSO_VELOCITA)) < 1e-9


# La velocita'.

@pytest.mark.parametrize(("testo", "velocita"), [("1", 1.0), ("1,05", 1.05), ("1.05", 1.05), ("  0,5 ", 0.5), ("2", 2.0), ("0.75", 0.75),
    ("1,050", 1.05), (",9", 0.9), ("1.", 1.0), ("+1,1", 1.1), ("2,00", 2.0), ("01,95", 1.95)])
def test_leggi_velocita_buona(testo, velocita):
    letta, correzioni = leggi_velocita(testo)
    assert (letta, correzioni) == (velocita, [])
    assert isinstance(letta, float)


@pytest.mark.parametrize(("testo", "velocita", "frase"), [
    ("1,07", 1.05, "Velocità: 1.07 va a passi di 0.05, ho messo 1.05."),
    ("1.08", 1.1, "Velocità: 1.08 va a passi di 0.05, ho messo 1.1."),
    ("1,025", 1.05, "Velocità: 1.025 va a passi di 0.05, ho messo 1.05."),
    ("1,0249", 1.0, "Velocità: 1.0249 va a passi di 0.05, ho messo 1."),
    ("0,52", 0.5, "Velocità: 0.52 va a passi di 0.05, ho messo 0.5."),
    ("1,975", 2.0, "Velocità: 1.975 va a passi di 0.05, ho messo 2."),
    ("0,3", 0.5, "Velocità: 0.3 è sotto il minimo, ho messo 0.5."),
    ("0", 0.5, "Velocità: 0 è sotto il minimo, ho messo 0.5."),
    ("-1", 0.5, "Velocità: -1 è sotto il minimo, ho messo 0.5."),
    ("3", 2.0, "Velocità: 3 è oltre il massimo, ho messo 2."),
    ("2.03", 2.0, "Velocità: 2.03 è oltre il massimo, ho messo 2."),
])
def test_leggi_velocita_corregge_e_lo_dice(testo, velocita, frase):
    """Prima i limiti, poi il passo, la meta' in su: una correzione sola."""
    assert leggi_velocita(testo) == (velocita, [frase])


def test_leggi_velocita_le_cifre_infinite():
    assert leggi_velocita("9" * 5000) == (2.0, [f"Velocità: {'9' * 5000} è oltre il massimo, ho messo 2."])
    assert leggi_velocita("0," + "0" * 5000 + "1") == (0.5, [f"Velocità: 0.{'0' * 5000}1 è sotto il minimo, ho messo 0.5."])


@pytest.mark.parametrize(("testo", "frase"), [
    ("", "Velocità: manca il numero; scrivi un numero da 0.5 a 2, per esempio 1.05 o 0.9; 1 è la velocità normale."),
    ("  ", "Velocità: manca il numero; scrivi un numero da 0.5 a 2, per esempio 1.05 o 0.9; 1 è la velocità normale."),
    ("veloce", "Velocità: veloce non è un numero; scrivi un numero da 0.5 a 2, per esempio 1.05 o 0.9; 1 è la velocità normale."),
    ("1 05", "Velocità: 1 05 non è un numero; scrivi un numero da 0.5 a 2, per esempio 1.05 o 0.9; 1 è la velocità normale."),
])
def test_leggi_velocita_rifiuta_e_dice_cosa_aspetta(testo, frase):
    with pytest.raises(ErroreValore) as errore:
        leggi_velocita(testo)
    assert str(errore.value) == frase


@pytest.mark.parametrize("testo", ["1,0,5", "1e5", "1E0", "inf", "nan", "١٢", "1/2", "1,05x", "x1", "--1", ".", ",", "+"])
def test_leggi_velocita_vuole_solo_le_cifre(testo):
    with pytest.raises(ErroreValore, match=f"^Velocità: {re.escape(testo)} non è un numero;"):
        leggi_velocita(testo)


def test_leggi_velocita_sta_sempre_sul_passo_e_nei_limiti():
    for millesimi in range(-100, 2600, 7):
        velocita, _ = leggi_velocita(f"{millesimi / 1000:.3f}")
        assert VELOCITA_MINIMA <= velocita <= VELOCITA_MASSIMA, millesimi
        assert velocita == round(round(velocita / PASSO_VELOCITA) * PASSO_VELOCITA, 2), millesimi


def test_scrivi_velocita_e_il_ritorno():
    assert scrivi_velocita(1.0) == "1"
    assert scrivi_velocita(1.05) == "1.05"
    assert scrivi_velocita(0.5) == "0.5"
    assert scrivi_velocita(2.0) == "2"
    # Il float di 1 + 0.05 + 0.05 si legge comunque al centesimo.
    assert scrivi_velocita(1.0 + 0.05 + 0.05) == "1.1"
    for passi in range(10, 41):
        velocita = round(passi * PASSO_VELOCITA, 2)
        assert leggi_velocita(scrivi_velocita(velocita)) == (velocita, []), velocita


# Il tono.

@pytest.mark.parametrize(("testo", "semitoni"), [("+2", 2), ("2", 2), ("-3", -3), ("0", 0), ("+0", 0), (" +12 ", 12), ("-12", -12),
    ("+2 semitoni", 2), ("-1 semitono", -1), ("3 Semitoni", 3), ("-4semitoni", -4), ("007", 7)])
def test_leggi_tono_buono(testo, semitoni):
    letto, correzioni = leggi_tono(testo)
    assert (letto, correzioni) == (semitoni, [])
    assert type(letto) is int


def test_leggi_tono_corregge_ai_limiti():
    assert leggi_tono("15") == (12, ["Tono: +15 è oltre il massimo, ho messo +12."])
    assert leggi_tono("+13 semitoni") == (12, ["Tono: +13 è oltre il massimo, ho messo +12."])
    assert leggi_tono("-20") == (-12, ["Tono: -20 è sotto il minimo, ho messo -12."])


@pytest.mark.parametrize(("testo", "frase"), [
    ("", "Tono: manca il numero; scrivi un numero intero da -12 a +12."),
    ("semitoni", "Tono: manca il numero; scrivi un numero intero da -12 a +12."),
    ("1,5", "Tono: 1,5 non è un numero intero; scrivi un numero intero da -12 a +12, senza decimali."),
    ("+0.5 semitoni", "Tono: +0.5 non è un numero intero; scrivi un numero intero da -12 a +12, senza decimali."),
    ("alto", "Tono: alto non è un numero; scrivi un numero intero da -12 a +12."),
    ("2 3", "Tono: 2 3 non è un numero solo; scrivi un numero intero da -12 a +12."),
    ("2 ottave", "Tono: 2 ottave non è un numero solo; scrivi un numero intero da -12 a +12."),
])
def test_leggi_tono_rifiuta_e_dice_cosa_aspetta(testo, frase):
    with pytest.raises(ErroreValore) as errore:
        leggi_tono(testo)
    assert str(errore.value) == frase


def test_scrivi_tono_e_il_ritorno():
    assert scrivi_tono(2) == "+2 semitoni"
    assert scrivi_tono(1) == "+1 semitono"
    assert scrivi_tono(-1) == "-1 semitono"
    assert scrivi_tono(0) == "0 semitoni"
    assert scrivi_tono(-12) == "-12 semitoni"
    for semitoni in range(-TONO_MASSIMO, TONO_MASSIMO + 1):
        assert leggi_tono(scrivi_tono(semitoni)) == (semitoni, [])


# L'equalizzatore.

def test_nomi_e_guadagni_delle_bande():
    assert nome_della_banda(0) == "banda 1, 60 Hz"
    assert nome_della_banda(2) == "banda 3, 400 Hz"
    assert nome_della_banda(6) == "banda 7, 12000 Hz"
    assert scrivi_guadagno(2) == "+2 dB"
    assert scrivi_guadagno(0) == "0 dB"
    assert scrivi_guadagno(-12) == "-12 dB"


@pytest.mark.parametrize(("testo", "bande"), [
    ("", [0] * 7), ("   ", [0] * 7), ("3", [3] * 7), ("+2", [2] * 7), ("-12", [-12] * 7), ("0", [0] * 7),
    ("0 0 +2 0 0 0 -3", [0, 0, 2, 0, 0, 0, -3]), ("  -12 12   0 1 -1 5 -5 ", [-12, 12, 0, 1, -1, 5, -5]),
])
def test_leggi_bande_vuoto_uno_o_sette(testo, bande):
    assert leggi_bande(testo) == (bande, [])


def test_leggi_bande_da_una_lista_nuova_ogni_volta():
    prima, _ = leggi_bande("")
    prima[0] = 5
    assert leggi_bande("")[0] == [0] * 7


def test_leggi_bande_corregge_banda_per_banda():
    assert leggi_bande("15") == ([12] * 7, ["Equalizzatore: +15 è oltre il massimo, ho messo +12."])
    assert leggi_bande("0 20 0 0 0 0 -13") == ([0, 12, 0, 0, 0, 0, -12], [
        "Equalizzatore, banda 2, 150 Hz: +20 è oltre il massimo, ho messo +12.",
        "Equalizzatore, banda 7, 12000 Hz: -13 è sotto il minimo, ho messo -12.",
    ])


@pytest.mark.parametrize(("testo", "frase"), [
    ("1 2", "Equalizzatore: 1 2 sono 2 valori; scrivi un numero solo, che vale per tutte le bande, oppure sette numeri, uno per banda dalla più bassa alla più alta, ciascuno da -12 a +12; il campo vuoto le azzera tutte."),
    ("1 2 3 4 5 6 7 8", "Equalizzatore: 1 2 3 4 5 6 7 8 sono 8 valori; scrivi un numero solo"),
    ("0 0 0 0 0 0", "Equalizzatore: 0 0 0 0 0 0 sono 6 valori;"),
    ("0 0 a 0 0 0 0", "Equalizzatore, banda 3, 400 Hz: a non è un numero; scrivi un numero intero da -12 a +12."),
    ("0 0 0 0 0 0 1,5", "Equalizzatore, banda 7, 12000 Hz: 1,5 non è un numero intero; scrivi un numero intero da -12 a +12, senza decimali."),
    ("1,5", "Equalizzatore: 1,5 non è un numero intero; scrivi un numero intero da -12 a +12, senza decimali."),
    ("forte", "Equalizzatore: forte non è un numero; scrivi un numero intero da -12 a +12."),
])
def test_leggi_bande_rifiuta(testo, frase):
    with pytest.raises(ErroreValore) as errore:
        leggi_bande(testo)
    assert str(errore.value).startswith(frase)


def test_scrivi_bande_e_il_ritorno():
    assert scrivi_bande([0] * 7) == "0 0 0 0 0 0 0"
    assert scrivi_bande([0, 0, 2, 0, 0, 0, -3]) == "0 0 +2 0 0 0 -3"
    for bande in ([0] * 7, [12] * 7, [-12, -1, 0, 1, 2, 11, 12], [3, 0, 0, -2, 0, 0, 12]):
        assert leggi_bande(scrivi_bande(bande)) == (bande, [])


# La dissolvenza.

@pytest.mark.parametrize(("testo", "secondi"), [("4", 4.0), ("2,5", 2.5), ("2.5", 2.5), ("0,5", 0.5), ("15", 15.0), ("4 secondi", 4.0),
    ("1 secondo", 1.0), ("3 s", 3.0), ("3s", 3.0), ("3 sec", 3.0), ("4 Secondi.", 4.0), ("4.", 4.0), ("2,3456", 2.346), ("2,0005", 2.001),
    (",75", 0.75)])
def test_leggi_durata_della_dissolvenza_buona(testo, secondi):
    letti, correzioni = leggi_durata_della_dissolvenza(testo)
    assert (letti, correzioni) == (secondi, [])
    assert isinstance(letti, float)


def test_leggi_durata_della_dissolvenza_corregge_e_rifiuta():
    assert leggi_durata_della_dissolvenza("20") == (15.0, ["Dissolvenza: 20 è oltre il massimo, ho messo 15."])
    assert leggi_durata_della_dissolvenza("0,2 secondi") == (0.5, ["Dissolvenza: 0.2 è sotto il minimo, ho messo 0.5."])
    assert leggi_durata_della_dissolvenza("0", "Durata della dissolvenza") == (0.5, ["Durata della dissolvenza: 0 è sotto il minimo, ho messo 0.5."])
    assert leggi_durata_della_dissolvenza("9" * 5000)[0] == 15.0
    with pytest.raises(ErroreValore, match=r"^Dissolvenza: mancano i secondi; scrivi i secondi, da 0.5 a 15, anche con i decimali, per esempio 4 o 2.5\.$"):
        leggi_durata_della_dissolvenza(" ")
    for testo in ("no", "sì", "1:30", "4 minuti", "inf", "1e1", "4 4"):
        with pytest.raises(ErroreValore, match=f"^Dissolvenza: {re.escape(testo)} non è un numero di secondi; scrivi i secondi, da 0.5 a 15,"):
            leggi_durata_della_dissolvenza(testo)


@pytest.mark.parametrize("testo", ["no", "No", "NO", "n", "spenta", "Spenta", "spento", "falso", "no.", "0", "0,0", "0 secondi", "-0", "spenta, 0 secondi"])
def test_leggi_dissolvenza_spegne_e_tiene_i_secondi(testo):
    assert leggi_dissolvenza(testo) == ({"accesa": False, "secondi": None}, [])
    assert leggi_dissolvenza(testo, 6.5) == ({"accesa": False, "secondi": 6.5}, [])


@pytest.mark.parametrize("testo", ["sì", "Sì", "si", "si'", "s", "accesa", "Accesa", "acceso", "vero", "sì."])
def test_leggi_dissolvenza_accende_con_i_secondi_di_adesso(testo):
    assert leggi_dissolvenza(testo) == ({"accesa": True, "secondi": None}, [])
    assert leggi_dissolvenza(testo, 6.5) == ({"accesa": True, "secondi": 6.5}, [])


@pytest.mark.parametrize(("testo", "dissolvenza"), [
    ("4", {"accesa": True, "secondi": 4.0}), ("2,5", {"accesa": True, "secondi": 2.5}), ("1", {"accesa": True, "secondi": 1.0}),
    ("4 secondi", {"accesa": True, "secondi": 4.0}), ("2,3456", {"accesa": True, "secondi": 2.346}),
    ("accesa, 4 secondi", {"accesa": True, "secondi": 4.0}), ("Accesa: 4", {"accesa": True, "secondi": 4.0}), ("sì 3", {"accesa": True, "secondi": 3.0}),
    ("spenta, 2,5 secondi", {"accesa": False, "secondi": 2.5}), ("no 7", {"accesa": False, "secondi": 7.0}),
])
def test_leggi_dissolvenza_con_i_secondi(testo, dissolvenza):
    """Con il numero i secondi sono quelli scritti, anche se la finestra
    passa quelli di adesso."""
    assert leggi_dissolvenza(testo) == (dissolvenza, [])
    assert leggi_dissolvenza(testo, 9.0) == (dissolvenza, [])


def test_leggi_dissolvenza_corregge_ai_limiti():
    assert leggi_dissolvenza("20") == ({"accesa": True, "secondi": 15.0}, ["Dissolvenza: 20 è oltre il massimo, ho messo 15."])
    assert leggi_dissolvenza("0,2") == ({"accesa": True, "secondi": 0.5}, ["Dissolvenza: 0.2 è sotto il minimo, ho messo 0.5."])
    assert leggi_dissolvenza("-3", 4.0) == ({"accesa": True, "secondi": 0.5}, ["Dissolvenza: -3 è sotto il minimo, ho messo 0.5."])
    assert leggi_dissolvenza("spenta, 30 secondi") == ({"accesa": False, "secondi": 15.0}, ["Dissolvenza: 30 è oltre il massimo, ho messo 15."])
    # Accesa a zero secondi non e' spenta: zero si porta al minimo.
    assert leggi_dissolvenza("accesa, 0") == ({"accesa": True, "secondi": 0.5}, ["Dissolvenza: 0 è sotto il minimo, ho messo 0.5."])


@pytest.mark.parametrize(("testo", "frase"), [
    ("", "Dissolvenza: manca il valore; scrivi no per spegnerla, sì per accenderla, oppure i secondi, da 0.5 a 15, per accenderla con quella durata, per esempio 4 o 2.5."),
    ("forse", "Dissolvenza: forse non è né no né un numero di secondi; scrivi no per spegnerla, sì per accenderla, oppure i secondi, da 0.5 a 15, per accenderla con quella durata, per esempio 4 o 2.5."),
    ("accesa forse", "Dissolvenza: accesa forse non è né no né un numero di secondi;"),
    ("4 minuti", "Dissolvenza: 4 minuti non è né no né un numero di secondi;"),
    ("1:30", "Dissolvenza: 1:30 non è né no né un numero di secondi;"),
    ("inf", "Dissolvenza: inf non è né no né un numero di secondi;"),
    ("4 4", "Dissolvenza: 4 4 non è né no né un numero di secondi;"),
    ("sì no", "Dissolvenza: sì no non è né no né un numero di secondi;"),
])
def test_leggi_dissolvenza_rifiuta(testo, frase):
    with pytest.raises(ErroreValore) as errore:
        leggi_dissolvenza(testo, 4.0)
    assert str(errore.value).startswith(frase)


def test_scrivi_durata_e_dissolvenza_e_il_ritorno():
    assert scrivi_durata(4.0) == "4 secondi"
    assert scrivi_durata(1.0) == "1 secondo"
    assert scrivi_durata(2.5) == "2.5 secondi"
    assert scrivi_durata(0.5) == "0.5 secondi"
    assert scrivi_durata(2.346) == "2.346 secondi"
    assert scrivi_durata(15) == "15 secondi"
    assert scrivi_dissolvenza({"accesa": True, "secondi": 4.0}) == "accesa, 4 secondi"
    assert scrivi_dissolvenza({"accesa": False, "secondi": 1.0}) == "spenta, 1 secondo"
    for dissolvenza in ({"accesa": True, "secondi": 4.0}, {"accesa": False, "secondi": 4.0}, {"accesa": True, "secondi": 1.0},
            {"accesa": False, "secondi": 2.5}, {"accesa": True, "secondi": 0.5}, {"accesa": False, "secondi": 15.0}, {"accesa": True, "secondi": 2.346}):
        assert leggi_dissolvenza(scrivi_dissolvenza(dissolvenza)) == (dissolvenza, [])
        assert leggi_durata_della_dissolvenza(scrivi_durata(dissolvenza["secondi"])) == (dissolvenza["secondi"], [])


# Il file delle impostazioni.

def _caricate(tmp_path, contenuto):
    percorso = tmp_path / "imp.json"
    percorso.write_text(contenuto if isinstance(contenuto, str) else json.dumps(contenuto), encoding="utf-8")
    imp = Impostazioni(str(percorso))
    imp.carica()
    return imp


def test_predefinite_nuove_e_controllate():
    for chiave in ("caratteri", "colori_testo", "colori_sfondo", "scheda_audio"):
        assert PREDEFINITE[chiave] == {}
    assert set(PREDEFINITE) - set(CONTROLLI) == {"insegui", "casuale", "ripresa", "video", "sottotitoli"}
    assert set(CONTROLLI) <= set(PREDEFINITE)
    for chiave, controllo in CONTROLLI.items():
        assert controllo(PREDEFINITE[chiave]), chiave


def test_predefinite_della_tappa_4():
    """Velocita' e tono normali, equalizzatore piatto, dissolvenza spenta di
    4 secondi; i tipi sono quelli che carica pretende dal file."""
    assert PREDEFINITE["velocita"] == 1.0 and isinstance(PREDEFINITE["velocita"], float)
    assert PREDEFINITE["tono"] == 0 and type(PREDEFINITE["tono"]) is int
    assert PREDEFINITE["bande"] == [0, 0, 0, 0, 0, 0, 0]
    assert PREDEFINITE["dissolvenza"] == {"accesa": False, "secondi": 4.0}


def test_carica_i_valori_buoni(tmp_path):
    buoni = {"volume": 300, "passo_volume": 50, "passo_indietro": 0.1, "passo_avanti": 0.23, "volume_effetti": 1, "insegui": True, "casuale": True, "modello_casuale": "totale", "video": True, "sottotitoli": True, "sintesi": "nvda",
        "ripresa": {"percorso": "x"}, "righe_della_console": 100, "caratteri": {"p": 6, "t": 72}, "colori_testo": {"c": [0, 100, 50]},
        "colori_sfondo": {"p": [31, 31, 31], "c": [100, 100, 100], "t": [0, 0, 0]},
        "scheda_audio": {"dispositivo": "Altoparlanti (Realtek(R) Audio)", "interfaccia": "Windows WASAPI"},
        "velocita": 1.05, "tono": -3, "bande": [0, 2, -12, 12, 0, 0, 1], "dissolvenza": {"accesa": True, "secondi": 2.5}}
    imp = _caricate(tmp_path, buoni)
    assert dict(imp) == buoni
    assert isinstance(imp["volume_effetti"], float)
    assert _caricate(tmp_path, {"volume": 0, "passo_volume": 1, "volume_effetti": 0})["volume_effetti"] == 0.0


def test_carica_i_limiti_della_tappa_4(tmp_path):
    """I limiti stessi passano; la velocita' scritta intera diventa float."""
    limiti = {"velocita": 0.5, "tono": 12, "bande": [-12, 12, -12, 12, -12, 12, -12], "dissolvenza": {"accesa": False, "secondi": 15}}
    imp = _caricate(tmp_path, limiti)
    assert {chiave: imp[chiave] for chiave in limiti} == limiti
    imp = _caricate(tmp_path, {"velocita": 2, "tono": -12, "dissolvenza": {"secondi": 0.5, "accesa": True}})
    assert imp["velocita"] == 2.0 and isinstance(imp["velocita"], float)
    assert imp["tono"] == -12
    assert imp["dissolvenza"] == {"accesa": True, "secondi": 0.5}


@pytest.mark.parametrize(("chiave", "valore"), [
    ("volume", 301), ("volume", -1), ("volume", 80.5), ("volume", True), ("volume", "80"),
    ("passo_volume", 0), ("passo_volume", 51),
    ("passo_indietro", 0.05), ("passo_indietro", -1), ("passo_indietro", 0), ("passo_indietro", "10"), ("passo_avanti", 0.0999),
    ("volume_effetti", 1.5), ("volume_effetti", -0.1), ("volume_effetti", False),
    ("righe_della_console", 99), ("righe_della_console", 5000.0),
    ("caratteri", {"p": 5}), ("caratteri", {"p": 73}), ("caratteri", {"x": 12}), ("caratteri", {"p": 12.0}), ("caratteri", {"p": True}),
    ("caratteri", {"p": "12"}), ("caratteri", []), ("caratteri", "12"),
    ("colori_testo", {"p": [101, 0, 0]}), ("colori_testo", {"p": [1, 2]}), ("colori_testo", {"p": [1, 2, 3, 4]}), ("colori_testo", {"p": "1.2.3"}),
    ("colori_testo", {"q": [1, 2, 3]}), ("colori_testo", {"p": [1.0, 2, 3]}), ("colori_testo", {"p": [-1, 2, 3]}), ("colori_testo", {"p": None}),
    ("colori_testo", {"p": [True, 2, 3]}), ("colori_sfondo", {"t": [0, 0, 500]}), ("colori_sfondo", [[0, 0, 0]]),
    ("scheda_audio", {"dispositivo": "x"}), ("scheda_audio", {"dispositivo": "x", "interfaccia": 3}),
    ("scheda_audio", {"dispositivo": "", "interfaccia": "Windows WASAPI"}), ("scheda_audio", {"dispositivo": "x", "interfaccia": "y", "altro": 1}),
    ("scheda_audio", []), ("scheda_audio", "auto"), ("scheda_audio", None),
    ("velocita", 0.45), ("velocita", 2.05), ("velocita", 0), ("velocita", -1.0), ("velocita", True), ("velocita", "1.05"), ("velocita", None),
    ("tono", 13), ("tono", -13), ("tono", 2.0), ("tono", True), ("tono", "+2"),
    ("bande", [0] * 6), ("bande", [0] * 8), ("bande", []), ("bande", [13, 0, 0, 0, 0, 0, 0]), ("bande", [0, 0, 0, 0, 0, 0, -13]),
    ("bande", [0.0] * 7), ("bande", [True, 0, 0, 0, 0, 0, 0]), ("bande", ["0"] * 7), ("bande", [None] * 7), ("bande", {}), ("bande", "0 0 0 0 0 0 0"),
    ("bande", 0),
    ("dissolvenza", {"accesa": True}), ("dissolvenza", {"secondi": 4.0}), ("dissolvenza", {}), ("dissolvenza", {"accesa": 1, "secondi": 4.0}),
    ("dissolvenza", {"accesa": "sì", "secondi": 4.0}), ("dissolvenza", {"accesa": True, "secondi": 0.4}), ("dissolvenza", {"accesa": True, "secondi": 16}),
    ("dissolvenza", {"accesa": True, "secondi": 0}), ("dissolvenza", {"accesa": True, "secondi": "4"}), ("dissolvenza", {"accesa": True, "secondi": True}),
    ("dissolvenza", {"accesa": True, "secondi": None}), ("dissolvenza", {"accesa": True, "secondi": 4.0, "altro": 1}), ("dissolvenza", True),
    ("dissolvenza", 4), ("dissolvenza", [True, 4.0]),
    ("casuale", 1), ("casuale", "sì"), ("casuale", None),
    ("modello_casuale", "mazzo"), ("modello_casuale", 1), ("modello_casuale", None), ("modello_casuale", ""),
    ("video", 1), ("sottotitoli", "sì"), ("sintesi", "festival"), ("sintesi", 3), ("sintesi", ""),
])
def test_carica_scarta_i_valori_fuori_intervallo(tmp_path, chiave, valore):
    imp = _caricate(tmp_path, {chiave: valore, "insegui": True})
    assert imp[chiave] == PREDEFINITE[chiave]
    assert imp["insegui"] is True


def test_carica_scarta_i_numeri_infiniti(tmp_path):
    imp = _caricate(tmp_path, '{"volume_effetti": NaN, "passo_avanti": Infinity, "passo_indietro": 1e400, "volume": ' + "9" * 400 + "}")
    for chiave in ("volume_effetti", "passo_avanti", "passo_indietro", "volume"):
        assert imp[chiave] == PREDEFINITE[chiave]
    imp = _caricate(tmp_path, '{"passo_indietro": 1' + "0" * 400 + "}")
    assert imp["passo_indietro"] == PREDEFINITE["passo_indietro"]
    imp = _caricate(tmp_path, '{"velocita": NaN, "tono": ' + "9" * 400 + ', "bande": [0, 0, 0, ' + "9" * 400 + ', 0, 0, 0], '
        '"dissolvenza": {"accesa": true, "secondi": NaN}}')
    for chiave in ("velocita", "tono", "bande", "dissolvenza"):
        assert imp[chiave] == PREDEFINITE[chiave], chiave
    assert _caricate(tmp_path, '{"dissolvenza": {"accesa": true, "secondi": Infinity}}')["dissolvenza"] == PREDEFINITE["dissolvenza"]


@pytest.mark.parametrize("contenuto", ["[]", "5", '"testo"', "null", "{troncato", ""])
def test_carica_un_file_che_non_e_un_dizionario(tmp_path, contenuto):
    assert dict(_caricate(tmp_path, contenuto)) == PREDEFINITE


def test_carica_un_file_troppo_annidato(tmp_path):
    assert dict(_caricate(tmp_path, "[" * 100000)) == PREDEFINITE


def test_i_predefiniti_non_si_toccano_dalle_istanze(tmp_path):
    imp = Impostazioni(str(tmp_path / "imp.json"))
    imp["caratteri"]["p"] = 12
    imp["ripresa"]["percorso"] = "x"
    imp["bande"][2] = 5
    imp["dissolvenza"]["accesa"] = True
    assert PREDEFINITE["caratteri"] == {}
    assert PREDEFINITE["ripresa"] == {}
    assert PREDEFINITE["bande"] == [0] * 7
    assert PREDEFINITE["dissolvenza"] == {"accesa": False, "secondi": 4.0}
    altre = Impostazioni(str(tmp_path / "altre.json"))
    assert altre["caratteri"] == {}
    assert altre["bande"] == [0] * 7
    assert altre["dissolvenza"]["accesa"] is False


def test_salva_e_ricarica_le_chiavi_nuove(tmp_path):
    percorso = str(tmp_path / "imp.json")
    imp = Impostazioni(percorso)
    imp["caratteri"], _ = leggi_caratteri("10 12 14")
    imp["colori_testo"] = unisci_colori(imp["colori_testo"], leggi_colori("p31.31.31 c")[0])
    imp["colori_sfondo"] = unisci_colori(imp["colori_sfondo"], leggi_colori("t100.100.100")[0])
    imp["scheda_audio"] = {"dispositivo": "Altoparlanti (Realtek(R) Audio)", "interfaccia": "Windows WASAPI"}
    imp["volume_effetti"], _ = leggi_volume_effetti("35")
    imp["passo_indietro"], _ = leggi_secondi("0")
    imp["velocita"], _ = leggi_velocita("1,15")
    imp["tono"], _ = leggi_tono("-5 semitoni")
    imp["bande"], _ = leggi_bande("+3 0 0 -2 0 0 +12")
    imp["dissolvenza"], _ = leggi_dissolvenza("2,5")
    imp.salva()
    assert not os.path.exists(percorso + ".tmp")
    rilette = Impostazioni(percorso)
    rilette.carica()
    assert dict(rilette) == dict(imp)
    assert rilette["colori_testo"] == {"p": [31, 31, 31]}
    assert rilette["passo_indietro"] == 0.1
    assert (rilette["velocita"], rilette["tono"], rilette["bande"]) == (1.15, -5, [3, 0, 0, -2, 0, 0, 12])
    assert rilette["dissolvenza"] == {"accesa": True, "secondi": 2.5}


def test_i_valori_letti_passano_i_controlli():
    """Quello che i campi accettano, anche corretto ai limiti, il file lo
    rilegge: valori.py e CONTROLLI hanno gli stessi limiti."""
    letti = {
        "volume": [leggi_volume_musica(t)[0] for t in ("-5", "0", "300", "999")],
        "passo_volume": [leggi_passo_volume(t)[0] for t in ("0", "1", "50", "99")],
        "passo_indietro": [leggi_secondi(t)[0] for t in ("0", "0.0996", "1:30")],
        "volume_effetti": [leggi_volume_effetti(t)[0] for t in ("-1", "0", "35", "100", "200")],
        "righe_della_console": [leggi_righe_della_console(t)[0] for t in ("1", "100", "123456")],
        "caratteri": [leggi_caratteri(t)[0] for t in ("", "1", "100", "5 50 500")],
        "colori_testo": [unisci_colori({}, leggi_colori(t)[0]) for t in ("", "p", "p999.0.100 c0.0.0 t1.2.3")],
        "velocita": [leggi_velocita(t)[0] for t in ("-1", "0,1", "0,5", "0,52", "1", "1,07", "1,975", "2", "2,5", "9" * 400)],
        "tono": [leggi_tono(t)[0] for t in ("-99", "-12", "0", "+5 semitoni", "12", "99")],
        "bande": [leggi_bande(t)[0] for t in ("", "99", "-99", "0 0 +2 0 0 0 -3", "-50 50 0 1 -1 13 -13")],
        "dissolvenza": [leggi_dissolvenza(t, 4.0)[0] for t in ("no", "0", "sì", "0,1", "0,5", "2,3456", "15", "99", "spenta, 30 secondi", "accesa, 0")],
    }
    for chiave, valori_letti in letti.items():
        for valore in valori_letti:
            assert CONTROLLI[chiave](valore), (chiave, valore)
