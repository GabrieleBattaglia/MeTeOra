# MeTeOra, le prove delle statistiche: l'orologio, la vita dei brani, il file, l'azzeramento e la pagina.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (UltraCode).
# 17/10/2026: nasce con la 1.103.0.

import datetime
import json

import formati
import statistiche
from statistiche import Statistiche


class Orologio:
    """L'orologio dei passi e il calendario, che le prove muovono a mano."""

    def __init__(self):
        self.secondi = 1000.0
        self.quando = datetime.datetime(2026, 11, 1, 10, 0, 0)

    def adesso(self):
        return self.secondi

    def ora(self):
        return self.quando

    def avanti(self, secondi):
        self.secondi += secondi
        self.quando += datetime.timedelta(seconds=secondi)


def _nuove(tmp_path, orologio=None):
    orologio = orologio or Orologio()
    s = Statistiche(str(tmp_path / "MeTeOra - Statistiche.json"), adesso=orologio.adesso, ora=orologio.ora)
    s.carica()
    return s, orologio


def _suona(percorso="E:\\musica\\a.mp3", **altro):
    return {"stato": "play", "percorso": percorso, "volume": 100, "velocita": 1.0, "scheda": "Cuffie", "sorgente": "Preferiti", **altro}


def _passi(s, orologio, stato, secondi):
    """Tanti passi da un secondo, come l'orologio della finestra."""
    for _ in range(int(secondi)):
        s.scatta(stato)
        orologio.avanti(1)
    s.scatta(stato)


def test_l_orologio_da_il_tempo_allo_stato_di_prima(tmp_path):
    s, o = _nuove(tmp_path)
    s.avvio("1.103.0")
    _passi(s, o, {"stato": "fermo"}, 10)
    _passi(s, o, _suona(), 30)
    _passi(s, o, {"stato": "pausa", "percorso": "E:\\musica\\a.mp3"}, 5)
    tempi = s.dati["tempi"]
    # Il primo passo di ogni stato nuovo va ancora a quello di prima.
    assert tempi["aperto"] == 45
    assert tempi["fermo"] == 10 and tempi["play"] == 30 and tempi["pausa"] == 5
    assert s.dati["formati"][".mp3"]["secondi"] == 30
    assert s.dati["schede_audio"] == {"Cuffie": 30} and s.dati["sorgenti"] == {"Preferiti": 30}
    assert s.dati["ore"][10] == 30 and s.dati["settimana"][6] == 30
    assert s.dati["giorni"]["2026-11-01"]["play"] == 30


def test_un_passo_lungo_vale_al_piu_cinque_secondi(tmp_path):
    s, o = _nuove(tmp_path)
    s.scatta(_suona())
    # Il PC sospeso per un'ora con il brano che suonava.
    o.avanti(3600)
    s.scatta(_suona())
    assert s.dati["tempi"]["play"] == statistiche.PASSO_MASSIMO


def test_video_volume_velocita_e_record(tmp_path):
    s, o = _nuove(tmp_path)
    _passi(s, o, _suona("film.mkv", video=True, immagine=True, schermo_intero=True, volume=150, velocita=1.5, tono=2, eq=True), 10)
    _passi(s, o, _suona("film.mkv", video=True, immagine=False, volume=50, muto=True), 10)
    t = s.dati["tempi"]
    assert t["play_video"] == 20 and t["video_immagine"] == 10 and t["video_senza_immagine"] == 10 and t["schermo_intero"] == 10
    assert t["oltre_100"] == 10 and t["muto"] == 10 and t["volume_pesato"] == 150 * 10 + 50 * 10
    assert t["velocita_cambiata"] == 10 and t["contenuto_a_velocita_cambiata"] == 15 and t["tono_cambiato"] == 10 and t["eq"] == 10
    r = s.dati["record"]
    assert r["volume_piu_alto"]["valore"] == 150 and r["velocita_piu_alta"]["valore"] == 1.5 and r["velocita_piu_bassa"]["valore"] == 1.0
    assert r["tono_piu_alto"]["valore"] == 2 and r["filata"]["valore"] == 20


def test_la_vita_dei_brani(tmp_path):
    s, o = _nuove(tmp_path)
    s.brano_avviato("a.mp3", modo="play")
    _passi(s, o, _suona("a.mp3", durata=lambda: 200.0), 30)
    s.brano_finito()
    s.brano_avviato("b.sid", 3, modo="brano_seguente_da_solo", a_caso=True)
    _passi(s, o, _suona("b.sid"), 4)
    # Lasciato nei primi dieci secondi.
    s.brano_avviato("c.ogg", modo="successivo")
    s.brano_in_errore("c.ogg")
    s.brano_avviato("d.flac", modo="precedente")
    s.brano_fermato()
    c = s.dati["conti"]
    assert sum(s.dati["modi"].values()) == 4
    assert c["finiti"] == 1 and c["lasciati"] == 2 and c["lasciati_subito"] == 2 and c["errori_di_riproduzione"] == 1 and c["a_caso"] == 1
    assert s.dati["formati"][".ogg"]["errori"] == 1 and s.dati["formati"][".mp3"]["finiti"] == 1
    assert s.dati["brani"]["b.sid"]["sotto"] == [3]
    assert s.dati["record"]["finito_piu_lungo"] == {"valore": 200.0, "quando": s.dati["record"]["finito_piu_lungo"]["quando"], "cosa": "a.mp3"}
    assert s.dati["giorni"]["2026-11-01"]["avvii"] == 4
    # Un brano in corso alla chiusura non e' lasciato.
    s.brano_avviato("e.mp3")
    s.chiusura()
    assert c["lasciati"] == 2 and c["in_corso_alla_chiusura"] == 1 and c["chiusure_regolari"] == 1


def test_il_file_si_salva_si_rilegge_e_non_si_sovrascrive_se_rotto(tmp_path):
    s, o = _nuove(tmp_path)
    s.avvio("1.103.0", "1.102.4")
    s.evento("play")
    s.tasto("X")
    s.salva()
    dati = json.loads((tmp_path / "MeTeOra - Statistiche.json").read_text(encoding="utf-8"))
    assert dati["conti"] == {"avvii": 1, "aggiornamenti": 1} and dati["eventi"] == {"play": 1} and dati["sessione_aperta"]
    # Il file con la sessione aperta: all'avvio dopo, e' una chiusura non regolare.
    s2, _o = _nuove(tmp_path, o)
    s2.avvio("1.103.0", "1.103.0")
    assert s2.dati["conti"]["chiusure_non_regolari"] == 1 and s2.dati["conti"]["avvii"] == 2 and "aggiornamenti" in s2.dati["conti"]
    assert s2.sessione["numero"] == 2
    # Un file rotto resta com'e': i conti nuovi vanno accanto.
    (tmp_path / "MeTeOra - Statistiche.json").write_text("{rotto", encoding="utf-8")
    s3, _o = _nuove(tmp_path, o)
    assert s3.errore and s3.percorso.endswith(".nuovo") and not s3.da_nuovo
    s3.salva()
    assert (tmp_path / "MeTeOra - Statistiche.json").read_text(encoding="utf-8") == "{rotto"
    s4, _o = _nuove(tmp_path, o)
    assert s4.da_nuovo


def test_i_valori_sbagliati_del_file_si_scartano(tmp_path):
    file = tmp_path / "MeTeOra - Statistiche.json"
    file.write_text(json.dumps({"conti": {"avvii": 3, "rotto": "tre", "vero": True}, "ore": [1, 2], "brani": {"a.mp3": {"volte": 2, "sotto": [1, "x"]}, "b": 4},
        "azzeramenti": -1, "record": {"r": {"valore": "x"}}}), encoding="utf-8")
    s, _o = _nuove(tmp_path)
    assert s.errore is None
    assert s.dati["conti"] == {"avvii": 3} and s.dati["ore"] == [0] * 24 and s.dati["azzeramenti"] == 0 and s.dati["record"] == {}
    assert s.dati["brani"] == {"a.mp3": {"volte": 2, "sotto": [1]}}


def test_l_azzeramento_tiene_la_prima_raccolta(tmp_path):
    s, o = _nuove(tmp_path)
    prima = s.dati["prima_raccolta"]
    s.avvio("1.103.0")
    _passi(s, o, _suona(), 20)
    o.avanti(3600)
    s.azzera()
    assert s.dati["prima_raccolta"] == prima and s.dati["azzeramenti"] == 1 and s.dati["ultimo_azzeramento"] != prima
    assert s.dati["tempi"] == {} and s.dati["brani"] == {} and s.dati["conti"] == {"avvii": 1} and s.dati["sessione_aperta"]
    assert s.dati["versioni"] == {"1.103.0": s.dati["dal"]}
    righe = s.righe("1.103.0")
    assert any(r.startswith("Prima raccolta:") and "Azzerate 1 volta" in r for r in righe)


def test_lo_storico_dei_brani_ha_un_tetto(tmp_path, monkeypatch):
    monkeypatch.setattr(statistiche, "MASSIMO_DEI_BRANI", 200)
    s, _o = _nuove(tmp_path)
    for n in range(200):
        s.brano_avviato(f"{n}.mp3")
        s.dati["brani"][f"{n}.mp3"]["secondi"] = n
    s.brano_avviato("nuovo.mp3")
    # Escono i due meno ascoltati, un centesimo, e i totali restano.
    assert len(s.dati["brani"]) == 199 and "0.mp3" not in s.dati["brani"] and "1.mp3" not in s.dati["brani"] and "nuovo.mp3" in s.dati["brani"]
    assert s.dati["formati"][".mp3"]["avvii"] == 201


def test_le_parole():
    assert statistiche.durata(0) == "0 secondi"
    assert statistiche.durata(0.4) == "meno di un secondo"
    assert statistiche.durata(61) == "1 minuto e 1 secondo"
    assert statistiche.durata(221) == "3 minuti e 41 secondi"
    assert statistiche.durata(3600) == "1 ora"
    assert statistiche.durata(243600) == "2 giorni, 19 ore e 40 minuti"
    assert statistiche.durata(86400 + 60) == "1 giorno e 1 minuto"
    assert statistiche.percentuale(1, 3) == "33.3%" and statistiche.percentuale(1, 0) == "0%"
    assert statistiche.anni_e_mesi(3513) == "9 anni e 7 mesi" and statistiche.anni_e_mesi(10) == "10 giorni"
    assert statistiche.numero_decimale(1.75) == "1.75" and statistiche.numero_decimale(1.0) == "1"
    assert statistiche.unita_di("E:\\Musica\\a.mp3") == "E:" and statistiche.unita_di("\\\\iliadbox\\Video\\f.mkv") == "\\\\iliadbox"
    assert statistiche.famiglia("a.SID") == "sid" and statistiche.famiglia("a.xm") == "tracker" and statistiche.famiglia("a.kar") == "midi"
    assert statistiche.data(datetime.date(2026, 11, 8), preposizione="il") == "l'8 novembre 2026"
    assert statistiche.data(datetime.date(2026, 11, 1), preposizione="dal") == "dall'1 novembre 2026"
    assert statistiche.data(datetime.date(2026, 11, 6), preposizione="al") == "al 6 novembre 2026"
    assert statistiche.data(datetime.date(2026, 11, 1), True, "il") == "domenica 1 novembre 2026"
    assert statistiche.data_e_ora("2026-11-11T01:16:00", preposizione="il") == "l'11 novembre 2026 all'1:16"
    assert statistiche.data_e_ora("rotta") == "una data che non si legge"
    assert (statistiche.dalle(0), statistiche.dalle(1), statistiche.dalle(13)) == ("da mezzanotte", "dall'una", "dalle 13")
    assert (statistiche.alle(0), statistiche.alle(1), statistiche.alle(14)) == ("a mezzanotte", "all'una", "alle 14")
    assert statistiche.famiglia("a.nsf") == "console" and statistiche.famiglia("a.mkv") == "video" and statistiche.famiglia("a.flac") == "audio"


def test_la_pagina_ha_tutte_le_sezioni_e_i_tag(tmp_path):
    s, o = _nuove(tmp_path)
    s.avvio("1.103.0")
    schede = {"E:\\C64\\Hubbard\\Commando.sid": {"durata": 120.0, "tag": {"autore": "Rob Hubbard", "anno": 1985}},
        "E:\\C64\\Tel\\Afterburner.sid": {"durata": 180.0, "tag": {"autore": "Jeroen Tel", "anno": 1988, "album": "Giochi"}}}
    for percorso in schede:
        s.brano_avviato(percorso)
        _passi(s, o, _suona(percorso, durata=lambda percorso=percorso: schede[percorso]["durata"]), 60)
        s.brano_finito()
    s.evento("marker_messo")
    s.conta("marker_tolti_prima", 3)
    s.tasto("X")
    s.tasto("Freccia giù")
    s.senza_comando("U accentata")
    s.impostazione("volume_effetti")
    s.banda(2)
    righe = s.righe("1.103.0", scheda=schede.get, libreria=["Schedario: 2 file conosciuti."], numeri_della_libreria={"file": 2, "durata": 300.0, "sid": 300.0},
        comandi_dei_tasti={"X": "play"}, nomi_delle_impostazioni={"volume_effetti": "Volume degli effetti"})
    testo = "\n".join(righe)
    titoli = [r for r in righe if r.startswith("Sezione ")]
    assert len(titoli) == len(statistiche.Pagina(s, "", None, None, {}, {}, {}).sezioni()) == 23
    assert titoli[0] == "Sezione 1 di 23, in breve." and titoli[-1] == "Sezione 23 di 23, tutti gli eventi."
    assert "Brani avviati: 2; ascoltati fino alla fine: 2, 100.0%." in testo
    assert "File diversi ascoltati: 2, 100.0% dei 2 file dello schedario." in testo
    assert "1. Afterburner.sid, di Jeroen Tel: 1 volta, 1 minuto." in testo or "1. Commando.sid, di Rob Hubbard: 1 volta, 1 minuto." in testo
    assert "Per decennio, dall'anno dei tag: anni '80 100.0%; senza anno 0.0%." in testo
    assert "Marker eliminati: 3." in testo and "Prima del punto, con Maiuscolo e R: 3, in 0 volte." in testo
    assert "1. Freccia giù: 1.\n2. X, suona: 1." in testo and "Frecce: 1; freccia giù 1." in testo
    assert "Tasti senza comando: 1; il più frequente: U accentata, 1 volta." in testo
    assert "la più usata: Volume degli effetti, 1 volta" in testo
    assert "La banda più ritoccata: banda 3, 400 Hz, 1 volta; in tutto 1 ritocco." in testo
    assert "Schedario: 2 file conosciuti." in testo
    assert "SID del Commodore 64: 2 minuti, 100.0% della riproduzione; 2 avvii." in testo
    assert f"Formati suonati: 1 dei {len(formati.TUTTI)} che MeTeOra conosce." in testo


def test_la_libreria_lascia_fuori_le_durate_non_credibili():
    schede = {
        "E:\\a.mp3": {"dim": 1000, "durata": 100.0, "tag": {"autore": "A", "anno": 1991, "genere": "Pop", "album": "X"}},
        "E:\\b.sid": {"dim": 10, "durata": 50.0, "sottobrani": 3, "tag": {"autore": "<?>", "anno": 1985}},
        "\\\\nas\\v\\c.mkv": {"dim": 5000, "durata": 1.4e12},
        "E:\\d.wav": {"dim": 1, "durata": None},
    }
    c = statistiche.censisci_la_libreria(schede)
    assert c["file"] == 4 and c["durata"] == 150.0 and c["non_credibili"] == 1 and c["senza_durata"] == 1 and c["sottobrani_sid"] == 3
    assert statistiche.numeri_della_libreria(c) == {"file": 4, "durata": 150.0, "sid": 50.0}
    righe = statistiche.righe_della_libreria(c, lambda byte: f"{byte} byte")
    testo = "\n".join(righe)
    assert "Schedario: 4 file conosciuti, 6011 byte." in testo
    assert "Durata di tutta la libreria: 2 minuti e 30 secondi." in testo
    assert "Il file più lungo: a.mp3, 1 minuto e 40 secondi." in testo
    assert "Dai tag: 1 autore, 1 album, 1 genere; anni dal 1985 al 1991." in testo
    assert "Per unità: E: 3 file, 75.0%; \\\\nas 1 file, 25.0%." in testo
    assert "Durate non credibili, oltre una settimana, lasciate fuori dai conti: 1 file." in testo


def test_una_sezione_rotta_non_ferma_la_pagina(tmp_path, monkeypatch):
    s, _o = _nuove(tmp_path)
    monkeypatch.setattr(statistiche.Pagina, "il_tempo", lambda _self: 1 / 0)
    righe = s.righe("1.103.0")
    i = righe.index("Sezione 3 di 23, il tempo.")
    assert righe[i + 1].startswith("Questa sezione non si è potuta comporre: ZeroDivisionError")
    assert "Sezione 4 di 23, il tempo per famiglia." in righe


def test_ogni_sezione_si_compone_con_tanti_dati(tmp_path):
    s, o = _nuove(tmp_path)
    s.avvio("1.103.0", "1.102.4")
    schede = {}
    for n in range(40):
        percorso = f"E:\\Musica\\{n % 5}\\brano {n}.{('mp3', 'sid', 'mkv', 'mid', 'xm', 'nsf')[n % 6]}"
        schede[percorso] = {"durata": 60.0 + n, "dim": 1000 * n, "tag": {"autore": f"Autore {n % 3}", "anno": 1980 + n, "album": "A", "genere": "G"}}
        s.brano_avviato(percorso, n % 3 or None, ("play", "brano_seguente_da_solo", "successivo", "precedente", "casuale", "playlist_numero")[n % 6], n % 2 == 0)
        _passi(s, o, _suona(percorso, video=percorso.endswith(".mkv"), immagine=n % 2 == 0, volume=80 + n, velocita=1.0 + (n % 3) / 4, tono=n % 3 - 1,
            eq=n % 2 == 0, dissolvenza=True, casuale=n % 2 == 1, ripetizione=("spenta", "brano", "lista")[n % 3], replaygain="album",
            durata=lambda d=60.0 + n: d), 5 + n)
        if n % 3:
            s.brano_finito()
        _passi(s, o, {"stato": "pausa", "percorso": percorso}, n % 4)
        o.avanti(3600 * (n % 7))
    for nome in statistiche.NOMI_DEGLI_EVENTI:
        s.evento(nome)
    for nome in ("Freccia giù", "X", "Maiuscolo con F7", "1", "Maiuscolo con 3", "Ctrl con barra rovesciata"):
        s.tasto(nome)
    s.senza_comando("U accentata")
    s.impostazione("volume")
    s.banda(0)
    s.marker_messo("E:\\Musica\\0\\brano 0.mp3")
    s.massimo("risultati", 12, "hubbard in tutto MeTeOra")
    s.massimo("ricerca_piu_lunga", 3.5, "hubbard in tutto MeTeOra")
    s.massimo("selezione", 40)
    for nome in ("secondi_avanti", "secondi_indietro", "risultati", "righe_della_console", "file_nel_cestino", "marker_tolti_tutti"):
        s.conta(nome, 7)
    s.chiusura()
    c = statistiche.censisci_la_libreria(schede)
    righe = s.righe("1.103.0", scheda=schede.get, libreria=statistiche.righe_della_libreria(c, lambda b: f"{b} byte"),
        numeri_della_libreria=statistiche.numeri_della_libreria(c), comandi_dei_tasti={"X": "play"}, nomi_delle_impostazioni={"volume": "Volume della musica"})
    testo = "\n".join(righe)
    assert "non si è potuta comporre" not in testo and "Ancora niente da dire." not in testo
    assert "Sezione 22 di 23, curiosità." in righe
    # Nessun numero con il separatore delle migliaia all'italiana.
    import re

    assert not re.search(r"\d\.\d{3}\b", testo.replace("1.103.0", "").replace("1.102.4", ""))
