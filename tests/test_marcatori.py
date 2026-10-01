# MeTeOra, le prove dei marcatori per la finestra dei marcatori: elenco, Cancella tutto, esportazione e importazione.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.51.0, piano 5.8.5 e 5.8.7; le prove piu' vecchie dei marcatori restano in test_moduli.py.

import json
import os

import pytest

import marcatori
from marcatori import Marcatori

FORMATO = marcatori.FORMATO_DELL_ESPORTAZIONE
K_A = marcatori.chiave(r"C:\Musica\a.mp3", 50.0)
K_B = marcatori.chiave(r"C:\Musica\B.mp3", 100.0)
K_Z1 = marcatori.chiave(r"C:\Musica\Z.sid", 90.0, 1)
K_Z2 = marcatori.chiave(r"C:\Musica\Z.sid", 120.0, 2)
K_ROCK = marcatori.chiave(r"C:\Musica\Rock\c.mp3", 20.0)
K_SPAZIO = marcatori.chiave(r"C:\Musica rock\d.mp3", 30.0)
K_SENZA_DURATA = marcatori.chiave(r"C:\Altro\e.mod", None)
K_IMPORTATO = marcatori.chiave("Importato.mp3", 60.0)


def _archivio(tmp_path, nome="marcatori.json"):
    archivio = Marcatori(str(tmp_path / nome))
    archivio.carica()
    return archivio


def _riempi(archivio):
    """Marker in tre cartelle (una con lo spazio, che non deve finire fra
    una cartella e la sua sottocartella), due nomi che differiscono per le
    maiuscole, un SID con due sottobrani aggiunti alla rovescia, un file
    senza durata e una voce importata, senza percorsi."""
    archivio.aggiungi(K_SPAZIO, 2.0, r"C:\Musica rock\d.mp3", 30.0)
    archivio.aggiungi(K_B, 30.0, r"C:\Musica\B.mp3", 100.0)
    archivio.aggiungi(K_B, 10.0, r"C:\Musica\B.mp3", 100.0)
    archivio.aggiungi(K_Z2, 7.0, r"C:\Musica\Z.sid", 120.0, 2)
    archivio.aggiungi(K_Z1, 8.0, r"C:\Musica\Z.sid", 90.0, 1)
    archivio.aggiungi(K_ROCK, 1.0, r"C:\Musica\Rock\c.mp3", 20.0)
    archivio.aggiungi(K_A, 5.0, r"C:\Musica\a.mp3", 50.0)
    archivio.aggiungi(K_SENZA_DURATA, 3.0, r"C:\Altro\e.mod")
    archivio.importa([{"file": "Importato.mp3", "durata": 60.0, "sottobrano": None, "marker": [{"tempo": 4.0, "nome": "Da fuori"}]}])


def _coppie(archivio, k):
    return [(m["tempo"], m["nome"]) for m in archivio.elenco(k)]


def test_tutti_raggruppa_per_provenienza(tmp_path):
    archivio = _archivio(tmp_path)
    assert archivio.tutti() == []
    _riempi(archivio)
    elenco = archivio.tutti()
    assert [(k, m["nome"]) for k, _voce, m in elenco] == [
        (K_SENZA_DURATA, "M1"),
        (K_A, "M1"),
        (K_B, "M2"),
        (K_B, "M1"),
        (K_Z1, "M1"),
        (K_Z2, "M1"),
        (K_ROCK, "M1"),
        (K_SPAZIO, "M1"),
        (K_IMPORTATO, "Da fuori"),
    ]
    # Voci e marker sono quelli dell'archivio: rinomina e togli li ritrovano.
    k, voce, marker = elenco[2]
    assert voce is archivio.voci[k] and any(m is marker for m in archivio.voci[k]["marker"])
    assert archivio.rinomina(k, marker, "Strofa") and archivio.elenco(K_B)[0]["nome"] == "Strofa"
    k, _voce, marker = elenco[-1]
    assert archivio.togli(k, marker) == 1 and K_IMPORTATO not in archivio.voci
    assert len(archivio.tutti()) == 8


def test_voci_senza_percorso_in_fondo_per_nome(tmp_path):
    archivio = _archivio(tmp_path)
    archivio.importa([
        {"file": "b.mp3", "durata": 2.0, "sottobrano": None, "marker": [{"tempo": 1.0, "nome": "B"}]},
        {"file": "A.mp3", "durata": 3.0, "sottobrano": None, "marker": [{"tempo": 2.0, "nome": "Due"}, {"tempo": 1.0, "nome": "Uno"}]},
    ])
    archivio.aggiungi(marcatori.chiave(r"D:\z.mp3", 9.0), 1.0, r"D:\z.mp3", 9.0)
    assert [m["nome"] for _k, _voce, m in archivio.tutti()] == ["M1", "Uno", "Due", "B"]


def test_cancella_tutto(tmp_path):
    archivio = _archivio(tmp_path)
    _riempi(archivio)
    archivio.salva()
    assert not archivio.modificato
    assert archivio.cancella_tutto() == 9
    assert archivio.voci == {} and archivio.tutti() == [] and archivio.modificato
    assert not archivio.forse(r"C:\Musica\B.mp3")
    archivio.salva()
    di_nuovo = _archivio(tmp_path)
    assert di_nuovo.voci == {} and not di_nuovo.errore
    # Senza marker non c'e' niente da togliere, e niente da salvare.
    assert archivio.cancella_tutto() == 0 and not archivio.modificato


def test_esportazione_senza_percorsi_e_con_saltati(tmp_path):
    archivio = _archivio(tmp_path)
    _riempi(archivio)
    scelti = [(k, m) for k, _voce, m in archivio.tutti()]
    # Alla rovescia e con un doppione: i marker escono in ordine di tempo, una volta sola.
    dati, saltati = archivio.esporta([*reversed(scelti), scelti[2]])
    assert saltati == 1
    assert dati["formato"] == "MeTeOra - Marcatori" and dati["versione"] == 1
    assert all(set(voce) == {"file", "durata", "sottobrano", "marker"} for voce in dati["marcatori"])
    testo = json.dumps(dati, ensure_ascii=False)
    assert "Musica" not in testo and "Altro" not in testo and "e.mod" not in testo
    per_file = {(voce["file"], voce["sottobrano"]): voce for voce in dati["marcatori"]}
    assert len(dati["marcatori"]) == len(per_file) == 7
    assert per_file["B.mp3", None] == {"file": "B.mp3", "durata": 100.0, "sottobrano": None, "marker": [{"tempo": 10.0, "nome": "M2"}, {"tempo": 30.0, "nome": "M1"}]}
    assert per_file["Z.sid", 2]["durata"] == 120.0 and per_file["Z.sid", 1]["durata"] == 90.0
    # I dati sono copie: cambiarli non tocca l'archivio.
    per_file["B.mp3", None]["marker"][0]["nome"] = "Altro nome"
    assert archivio.elenco(K_B)[0]["nome"] == "M2"
    # Una scelta parziale; solo marker senza durata; chiavi che l'archivio non ha.
    solo_b = [(k, m) for k, m in scelti if k == K_B]
    assert [voce["file"] for voce in archivio.esporta(solo_b)[0]["marcatori"]] == ["B.mp3"]
    dati, saltati = archivio.esporta([(K_SENZA_DURATA, archivio.elenco(K_SENZA_DURATA)[0])])
    assert dati["marcatori"] == [] and saltati == 1
    assert archivio.esporta([("nessuno.mp3|1.000", {"tempo": 1.0, "nome": "X"})]) == ({"formato": FORMATO, "versione": 1, "marcatori": []}, 0)


def test_andata_e_ritorno_su_un_altro_archivio(tmp_path):
    archivio = _archivio(tmp_path)
    _riempi(archivio)
    archivio.rinomina(K_B, archivio.elenco(K_B)[0], "Ritornello è qui")
    dati, saltati = archivio.esporta([(k, m) for k, _voce, m in archivio.tutti()])
    assert saltati == 1
    percorso = tmp_path / "MeTeOra - Marcatori esportati.json"
    Marcatori.scrivi_esportazione(dati, percorso)
    testo = percorso.read_text(encoding="utf-8")
    # UTF-8 con le lettere vere, un rientro di uno come l'archivio, nessun file provvisorio rimasto.
    assert "Ritornello è qui" in testo and testo.startswith('{\n "formato": "MeTeOra - Marcatori",\n "versione": 1,')
    assert not os.path.exists(str(percorso) + ".tmp")
    voci = Marcatori.leggi_esportazione(str(percorso))
    assert voci == dati["marcatori"]
    altro = _archivio(tmp_path, "altro.json")
    assert not altro.forse(r"D:\Copie\b.MP3")
    aggiunti, gia_presenti, toccate = altro.importa(voci)
    assert (aggiunti, gia_presenti) == (8, 0)
    assert toccate == [K_A, K_B, K_Z1, K_Z2, K_ROCK, K_SPAZIO, K_IMPORTATO]
    for k in toccate:
        assert _coppie(altro, k) == _coppie(archivio, k)
    assert K_SENZA_DURATA not in altro.voci
    voce = altro.voci[K_Z2]
    assert (voce["file"], voce["durata"], voce["sottobrano"], voce["percorsi"]) == ("Z.sid", 120.0, 2, [])
    # forse() trova subito le copie dei file, ovunque stiano, e la chiave e' la stessa.
    assert altro.forse(r"D:\Copie\b.MP3") and marcatori.chiave(r"D:\Copie\b.MP3", 100.0) in altro.voci
    assert altro.modificato
    altro.salva()
    riletto = _archivio(tmp_path, "altro.json")
    assert riletto.voci == altro.voci and riletto.forse(r"E:\z.SID")
    # Senza percorsi l'elenco va per nome del file, poi per sottobrano.
    assert [k for k, _voce, _m in riletto.tutti()] == [K_A, K_B, K_B, K_ROCK, K_SPAZIO, K_IMPORTATO, K_Z1, K_Z2]


def test_doppioni_entro_la_tolleranza(tmp_path):
    origine = _archivio(tmp_path, "origine.json")
    for tempo in (10.0, 20.0):
        origine.aggiungi(K_B, tempo, r"C:\Musica\B.mp3", 100.0)
    origine.rinomina(K_B, origine.elenco(K_B)[0], "Strofa")
    origine.rinomina(K_B, origine.elenco(K_B)[1], "Ponte")
    locale = _archivio(tmp_path)
    locale.rinomina(K_B, locale.aggiungi(K_B, 10.003, r"E:\Mie\b.mp3", 100.0), "Locale")
    locale.salva()
    dati, _saltati = origine.esporta([(K_B, m) for m in origine.elenco(K_B)])
    # Il marker entro la tolleranza resta quello di qui, con il suo nome.
    assert locale.importa(dati["marcatori"]) == (1, 1, [K_B])
    assert _coppie(locale, K_B) == [(10.003, "Locale"), (20.0, "Ponte")]
    assert locale.voci[K_B]["percorsi"] == [r"E:\Mie\b.mp3"] and locale.modificato
    locale.salva()
    # La seconda volta non c'e' niente di nuovo, e niente da salvare.
    assert locale.importa(dati["marcatori"]) == (0, 2, []) and not locale.modificato
    # Appena fuori dalla tolleranza e' un marker nuovo; due vicini nella stessa importazione contano una volta.
    vicini = [{"file": "B.MP3", "durata": 100.0, "sottobrano": None, "marker": [{"tempo": 10.009, "nome": "Vicino"}, {"tempo": 50.0, "nome": "A"}, {"tempo": 50.004, "nome": "B"}]}]
    assert locale.importa(vicini) == (2, 1, [K_B])
    assert _coppie(locale, K_B) == [(10.003, "Locale"), (10.009, "Vicino"), (20.0, "Ponte"), (50.0, "A")]


def test_importa_salta_le_voci_senza_durata(tmp_path):
    archivio = _archivio(tmp_path)
    voci = [{"file": "x.mp3", "durata": durata, "sottobrano": None, "marker": [{"tempo": 1.0, "nome": "M1"}]} for durata in (None, 0, -3.0, True)]
    voci.append({"file": "", "durata": 5.0, "sottobrano": None, "marker": [{"tempo": 1.0, "nome": "M1"}]})
    assert archivio.importa(voci) == (0, 0, []) and archivio.voci == {} and not archivio.modificato
    assert not archivio.forse(r"C:\x.mp3")


def _esportazione(**cambi):
    """Il testo di un'esportazione con una voce, cambiata da cambi."""
    voce = {"file": "a.mp3", "durata": 10.0, "sottobrano": None, "marker": [{"tempo": 1.0, "nome": "M1"}]}
    voce.update(cambi)
    return json.dumps({"formato": FORMATO, "versione": 1, "marcatori": [voce]})


ROTTI = [
    ("{troncato", "prova.json non è un'esportazione dei marcatori di MeTeOra: non è un file JSON."),
    ("[]", "prova.json non è un'esportazione dei marcatori di MeTeOra."),
    (json.dumps({"versione": 1, "marcatori": []}), "prova.json non è un'esportazione dei marcatori di MeTeOra."),
    (json.dumps({"versione": 1, "marcatori": {"a.mp3|10.000": {"marker": []}}}), "prova.json non è un'esportazione dei marcatori di MeTeOra."),
    (json.dumps({"formato": "MeTeOra - Playlist", "versione": 1, "marcatori": []}), "prova.json non è un'esportazione dei marcatori di MeTeOra."),
    (json.dumps({"formato": FORMATO, "versione": 2, "marcatori": []}), "non sa leggere."),
    (json.dumps({"formato": FORMATO, "versione": True, "marcatori": []}), "non sa leggere."),
    (json.dumps({"formato": FORMATO, "marcatori": []}), "non sa leggere."),
    (json.dumps({"formato": FORMATO, "versione": 1, "marcatori": {}}), "ma è rovinata: manca l'elenco dei marcatori."),
    (json.dumps({"formato": FORMATO, "versione": 1, "marcatori": ["a.mp3"]}), "ma è rovinata: la voce 1 non è una voce."),
    (_esportazione(file=""), "la voce 1 non ha il nome del file."),
    (_esportazione(file=7), "la voce 1 non ha il nome del file."),
    (_esportazione(durata="tre minuti"), "la voce 1, a.mp3, non ha una durata che sia un numero."),
    (_esportazione(durata=True), "la voce 1, a.mp3, non ha una durata che sia un numero."),
    (_esportazione(durata=float("nan")), "la voce 1, a.mp3, non ha una durata che sia un numero."),
    (_esportazione(durata=10**400), "la voce 1, a.mp3, non ha una durata che sia un numero."),
    (_esportazione(sottobrano="2"), "la voce 1, a.mp3, ha un sottobrano che non è un numero."),
    (_esportazione(sottobrano=-1), "la voce 1, a.mp3, ha un sottobrano che non è un numero."),
    (_esportazione(marker={"tempo": 1.0, "nome": "M1"}), "la voce 1, a.mp3, non ha l'elenco dei marker."),
    (_esportazione(marker=[{"tempo": "1:30", "nome": "M1"}]), "il marker 1 della voce 1, a.mp3, non ha un tempo valido."),
    (_esportazione(marker=[{"tempo": 1.0, "nome": "M1"}, {"tempo": -1, "nome": "M2"}]), "il marker 2 della voce 1, a.mp3, non ha un tempo valido."),
    (_esportazione(marker=["M1"]), "il marker 1 della voce 1, a.mp3, non ha un tempo valido."),
    (_esportazione(marker=[{"tempo": 1.0, "nome": " \n "}]), "il marker 1 della voce 1, a.mp3, non ha un nome."),
    (_esportazione(marker=[{"tempo": 1.0}]), "il marker 1 della voce 1, a.mp3, non ha un nome."),
    # Numeri finiti ma impossibili: 1e306 secondi rompevano la finestra dei
    # marcatori e la plancia, che non riuscivano piu' a scrivere il tempo.
    (_esportazione(durata=100, marker=[{"tempo": 1e306, "nome": "x"}]), "il marker 1 della voce 1, a.mp3, ha un tempo impossibile, di oltre trecento anni."),
    (_esportazione(durata=None, marker=[{"tempo": 1e306, "nome": "x"}]), "il marker 1 della voce 1, a.mp3, ha un tempo impossibile, di oltre trecento anni."),
    (_esportazione(durata=1e306, marker=[{"tempo": 1e306, "nome": "x"}]), "la voce 1, a.mp3, ha una durata impossibile, di oltre trecento anni."),
    (_esportazione(durata=marcatori.TETTO_DEI_SECONDI + 0.5), "la voce 1, a.mp3, ha una durata impossibile, di oltre trecento anni."),
    (_esportazione(durata=None, marker=[{"tempo": marcatori.TETTO_DEI_SECONDI + 0.5, "nome": "x"}]), "il marker 1 della voce 1, a.mp3, ha un tempo impossibile, di oltre trecento anni."),
]


@pytest.mark.parametrize(("contenuto", "frase"), ROTTI)
def test_file_non_validi(tmp_path, contenuto, frase):
    percorso = tmp_path / "prova.json"
    percorso.write_text(contenuto, encoding="utf-8")
    with pytest.raises(ValueError, match=r"^prova\.json ") as errore:
        Marcatori.leggi_esportazione(str(percorso))
    messaggio = str(errore.value)
    # Una frase per l'utente, su una riga sola.
    assert messaggio.endswith(frase) and "\n" not in messaggio


def test_tempi_e_durate_ai_limiti(tmp_path):
    # Il tetto dei trecento anni si raggiunge, non si supera; un marker oltre
    # la durata della sua voce passa, perche' la durata e' quella
    # dell'intestazione e un file unito suona oltre; con una durata che non
    # vale come chiave la voce la salta importa.
    tetto = marcatori.TETTO_DEI_SECONDI
    voci = [
        {"file": "lungo.mp3", "durata": tetto, "marker": [{"tempo": tetto, "nome": "Fine"}]},
        {"file": "a.mp3", "durata": 10.0, "marker": [{"tempo": 37.5, "nome": "Oltre la durata"}]},
        {"file": "senza.mp3", "durata": None, "marker": [{"tempo": tetto - 1, "nome": "Tardi"}]},
        {"file": "zero.mp3", "durata": 0, "marker": [{"tempo": 50.0, "nome": "Oltre"}]},
    ]
    percorso = tmp_path / "limiti.json"
    percorso.write_text(json.dumps({"formato": FORMATO, "versione": 1, "marcatori": voci}), encoding="utf-8")
    letti = Marcatori.leggi_esportazione(percorso)
    assert [(v["file"], v["durata"], v["marker"][0]["tempo"]) for v in letti] == [
        ("lungo.mp3", float(tetto), float(tetto)), ("a.mp3", 10.0, 37.5), ("senza.mp3", None, float(tetto - 1)), ("zero.mp3", 0.0, 50.0)]
    archivio = _archivio(tmp_path)
    assert archivio.importa(letti)[:2] == (2, 0)


def test_marker_oltre_la_durata_va_e_torna(tmp_path):
    # Un MP3 unito con copy /b dichiara 1 secondo e ne suona 4: T ci mette un
    # marker a 3,95. MeTeOra lo esporta, e un'altra copia lo deve accettare.
    archivio = _archivio(tmp_path)
    k = marcatori.chiave(r"C:\m\puntata.mp3", 1.045)
    archivio.aggiungi(k, 3.95, r"C:\m\puntata.mp3", 1.045)
    dati, saltati = archivio.esporta([(k, m) for m in archivio.elenco(k)])
    assert saltati == 0
    percorso = tmp_path / "esportati.json"
    archivio.scrivi_esportazione(dati, str(percorso))
    altro = Marcatori(str(tmp_path / "altro.json"))
    assert altro.importa(Marcatori.leggi_esportazione(str(percorso)))[:2] == (1, 0)
    assert [m["tempo"] for m in altro.elenco(k)] == [3.95]

def test_durate_enormi_vanno_e_tornano(tmp_path):
    # Un WAV non chiuso, a 8000 Hz e 8 bit, dichiara 149 ore: MeTeOra lo
    # esporta e un'altra copia lo importa. Oltre il tetto, invece, il marker
    # non si esporta e si conta fra i saltati, invece di rendere rovinato
    # tutto il file.
    archivio = _archivio(tmp_path)
    radio = marcatori.chiave(r"C:\r\radio.wav", 536870.9)
    archivio.aggiungi(radio, 0.5, r"C:\r\radio.wav", 536870.9)
    oltre = marcatori.chiave(r"C:\r\strano.wav", marcatori.TETTO_DEI_SECONDI * 2)
    archivio.aggiungi(oltre, 1.0, r"C:\r\strano.wav", marcatori.TETTO_DEI_SECONDI * 2)
    scelti = [(k, m) for k in (radio, oltre) for m in archivio.elenco(k)]
    dati, saltati = archivio.esporta(scelti)
    assert saltati == 1 and [v["file"] for v in dati["marcatori"]] == ["radio.wav"]
    percorso = tmp_path / "esportati.json"
    archivio.scrivi_esportazione(dati, str(percorso))
    altro = Marcatori(str(tmp_path / "altro.json"))
    assert altro.importa(Marcatori.leggi_esportazione(str(percorso)))[:2] == (1, 0)

def test_file_che_non_si_leggono(tmp_path):
    # L'archivio dei marcatori di MeTeOra non e' un'esportazione.
    archivio = _archivio(tmp_path)
    _riempi(archivio)
    archivio.salva()
    with pytest.raises(ValueError, match=r"^marcatori\.json non è un'esportazione dei marcatori di MeTeOra\.$"):
        Marcatori.leggi_esportazione(archivio.percorso)
    # Un testo che non e' UTF-8, e un file che non c'e'.
    (tmp_path / "latino.json").write_bytes('{"file": "è"}'.encode("latin-1"))
    with pytest.raises(ValueError, match="non è un file JSON"):
        Marcatori.leggi_esportazione(str(tmp_path / "latino.json"))
    with pytest.raises(ValueError, match=r"^Non riesco a leggere manca\.json: .+\.$"):
        Marcatori.leggi_esportazione(str(tmp_path / "manca.json"))


def test_lettura_tollerante_di_un_file_ritoccato(tmp_path):
    percorso = tmp_path / "ritoccato.json"
    voci = [
        {"file": r"C:\Musica\Canzone.mp3", "durata": 200, "marker": [{"tempo": 9, "nome": "Due\nrighe"}, {"tempo": 1.5, "nome": " Primo "}]},
        {"file": "Senza durata.mp3", "durata": None, "sottobrano": 0, "marker": []},
    ]
    # Il BOM di un editor di testo non disturba.
    percorso.write_text("\ufeff" + json.dumps({"formato": FORMATO, "versione": 1, "marcatori": voci}), encoding="utf-8")
    assert Marcatori.leggi_esportazione(percorso) == [
        {"file": "Canzone.mp3", "durata": 200.0, "sottobrano": None, "marker": [{"tempo": 1.5, "nome": "Primo"}, {"tempo": 9.0, "nome": "Due righe"}]},
        {"file": "Senza durata.mp3", "durata": None, "sottobrano": None, "marker": []},
    ]
