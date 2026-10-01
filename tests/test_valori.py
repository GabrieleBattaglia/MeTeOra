# MeTeOra, le prove dei valori scritti nei campi delle impostazioni e dei controlli sul file delle impostazioni.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.51.0, insieme a valori.py.

import json
import os
import re

import pytest

import valori
from impostazioni import CONTROLLI, PREDEFINITE, Impostazioni
from valori import (
    ErroreValore,
    colore_da_percentuali,
    leggi_caratteri,
    leggi_colori,
    leggi_intero,
    leggi_passo_volume,
    leggi_righe_della_console,
    leggi_secondi,
    leggi_si_no,
    leggi_tempo,
    leggi_volume_effetti,
    leggi_volume_musica,
    percentuali_da_colore,
    scrivi_colori,
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
    assert set(PREDEFINITE) - set(CONTROLLI) == {"insegui", "ripresa"}
    assert set(CONTROLLI) <= set(PREDEFINITE)
    for chiave, controllo in CONTROLLI.items():
        assert controllo(PREDEFINITE[chiave]), chiave


def test_carica_i_valori_buoni(tmp_path):
    buoni = {"volume": 300, "passo_volume": 50, "passo_indietro": 0.1, "passo_avanti": 0.23, "volume_effetti": 1, "insegui": True,
        "ripresa": {"percorso": "x"}, "righe_della_console": 100, "caratteri": {"p": 6, "t": 72}, "colori_testo": {"c": [0, 100, 50]},
        "colori_sfondo": {"p": [31, 31, 31], "c": [100, 100, 100], "t": [0, 0, 0]},
        "scheda_audio": {"dispositivo": "Altoparlanti (Realtek(R) Audio)", "interfaccia": "Windows WASAPI"}}
    imp = _caricate(tmp_path, buoni)
    assert dict(imp) == buoni
    assert isinstance(imp["volume_effetti"], float)
    assert _caricate(tmp_path, {"volume": 0, "passo_volume": 1, "volume_effetti": 0})["volume_effetti"] == 0.0


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


@pytest.mark.parametrize("contenuto", ["[]", "5", '"testo"', "null", "{troncato", ""])
def test_carica_un_file_che_non_e_un_dizionario(tmp_path, contenuto):
    assert dict(_caricate(tmp_path, contenuto)) == PREDEFINITE


def test_carica_un_file_troppo_annidato(tmp_path):
    assert dict(_caricate(tmp_path, "[" * 100000)) == PREDEFINITE


def test_i_predefiniti_non_si_toccano_dalle_istanze(tmp_path):
    imp = Impostazioni(str(tmp_path / "imp.json"))
    imp["caratteri"]["p"] = 12
    imp["ripresa"]["percorso"] = "x"
    assert PREDEFINITE["caratteri"] == {}
    assert PREDEFINITE["ripresa"] == {}
    assert Impostazioni(str(tmp_path / "altre.json"))["caratteri"] == {}


def test_salva_e_ricarica_le_chiavi_nuove(tmp_path):
    percorso = str(tmp_path / "imp.json")
    imp = Impostazioni(percorso)
    imp["caratteri"], _ = leggi_caratteri("10 12 14")
    imp["colori_testo"] = unisci_colori(imp["colori_testo"], leggi_colori("p31.31.31 c")[0])
    imp["colori_sfondo"] = unisci_colori(imp["colori_sfondo"], leggi_colori("t100.100.100")[0])
    imp["scheda_audio"] = {"dispositivo": "Altoparlanti (Realtek(R) Audio)", "interfaccia": "Windows WASAPI"}
    imp["volume_effetti"], _ = leggi_volume_effetti("35")
    imp["passo_indietro"], _ = leggi_secondi("0")
    imp.salva()
    assert not os.path.exists(percorso + ".tmp")
    rilette = Impostazioni(percorso)
    rilette.carica()
    assert dict(rilette) == dict(imp)
    assert rilette["colori_testo"] == {"p": [31, 31, 31]}
    assert rilette["passo_indietro"] == 0.1


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
    }
    for chiave, valori_letti in letti.items():
        for valore in valori_letti:
            assert CONTROLLI[chiave](valore), (chiave, valore)
