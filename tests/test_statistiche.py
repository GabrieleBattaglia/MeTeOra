# MeTeOra, le prove delle statistiche: l'orologio, la vita dei brani, il file, l'azzeramento e la pagina.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (UltraCode).
# 17/10/2026: nasce con la 1.103.0. Nella 1.104.0 le prove delle righe-elenco senza le voci a zero, delle percentuali, degli anni futuri, delle date con il giorno della settimana, della pulizia all'avvio e dei brani rinominati. Nella 1.105.0 quella dei nomi di tutti gli eventi, con Dove sono. Nella 1.109.0 la riga delle playlist con Ordina e Mescola. Nella 1.110.0 la durata residua in fondo agli eventi.

import datetime
import json
import os

import pytest

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
    assert statistiche.percentuale(1, 3) == "33.3%" and statistiche.percentuale(1, 0) == "0.0%"
    assert statistiche.anni_e_mesi(3513) == "9 anni e 7 mesi" and statistiche.anni_e_mesi(10) == "10 giorni"
    assert statistiche.numero_decimale(1.75) == "1.75" and statistiche.numero_decimale(1.0) == "1"
    assert statistiche.unita_di("E:\\Musica\\a.mp3") == "E:" and statistiche.unita_di("\\\\iliadbox\\Video\\f.mkv") == "\\\\iliadbox"
    assert statistiche.famiglia("a.SID") == "sid" and statistiche.famiglia("a.xm") == "tracker" and statistiche.famiglia("a.kar") == "midi"
    assert statistiche.data(datetime.date(2026, 11, 8)) == "domenica 8 novembre 2026"
    assert statistiche.data(datetime.date(2026, 11, 1), "da") == "da domenica 1 novembre 2026"
    assert statistiche.data(datetime.date(2026, 11, 6), "a") == "a venerdì 6 novembre 2026"
    assert statistiche.data_e_ora("2026-11-11T01:16:00", "di") == "di mercoledì 11 novembre 2026 all'1:16"
    assert statistiche.data_e_ora("2026-10-19T18:03:00") == "lunedì 19 ottobre 2026 alle 18:03"
    assert statistiche.solo_la_data("2026-10-19T18:03:00", "da") == "da lunedì 19 ottobre 2026"
    assert statistiche.data_e_ora("rotta") == "una data che non si legge"
    assert statistiche.data_e_ora("rotta", "da") == "da una data che non si legge" and statistiche.solo_la_data(None) == "una data che non si legge"
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
    # Senza anno a zero non si dice (1.104.0).
    assert "Per decennio, dall'anno dei tag: anni '80 100.0%." in testo
    # Le date con il giorno della settimana, e solo le voci diverse da zero.
    assert righe[0] == "Statistiche di MeTeOra 1.103.0, raccolte da domenica 1 novembre 2026 alle 10:00: 1 giorno, oggi compreso."
    assert "Versioni usate: 1.103.0 da domenica 1 novembre 2026." in testo
    assert any(r.startswith("Questa è la sessione numero 1, aperta domenica 1 novembre 2026 alle 10:00: da ") for r in righe)
    assert "Per ora: ore 10: 100.0%." in testo and "Per giorno della settimana: domenica 100.0%." in testo
    assert "Per fascia: mattina, dalle 6: 100.0%." in testo and "Per mese: novembre 2026, 2 minuti." in testo
    assert not any(r.startswith(("Video:", "MIDI:", "Audio, MP3")) for r in righe)
    assert "Marker eliminati: 3." in testo and "Prima del punto, con Maiuscolo e R: 3, in 0 volte." in testo
    assert "1. Freccia giù: 1.\n2. X, suona: 1." in testo and "Frecce: 1; freccia giù 1." in testo
    assert "Tasti senza comando: 1; il più frequente: U accentata, 1 volta." in testo
    assert "la più usata: Volume degli effetti, 1 volta" in testo
    assert "La banda più ritoccata: banda 3, 400 Hz, 1 volta; in tutto 1 ritocco." in testo
    assert "Schedario: 2 file conosciuti." in testo
    assert "SID del Commodore 64: 2 minuti, 100.0% della riproduzione; 2 avvii." in testo
    assert f"Formati suonati: 1 dei {len(formati.TUTTI)} che MeTeOra conosce." in testo
    assert f"Formati mai suonati: {len(formati.TUTTI) - 1}." in righe


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
    # Solo le famiglie con dei file (1.104.0).
    assert "Per numero di file: audio 2, 50.0%; SID 1, 25.0%; video 1, 25.0%." in testo
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


# La 1.104.0.


def _norm(percorso):
    """La normalizzazione concordata fra i moduli per i percorsi mancanti."""
    return os.path.normcase(os.path.abspath(percorso))


def _pagina(s, scheda=None, libreria=None, numeri=None):
    return statistiche.Pagina(s, "1.104.0", scheda or (lambda _p: None), libreria, numeri or {}, {}, {})


def test_le_percentuali_sono_uniformi():
    # Il totale a zero come le altre; il formato si sceglie sul valore
    # arrotondato a due decimali.
    assert statistiche.percentuale(0, 0) == "0.0%" and statistiche.percentuale(0, 5) == "0.0%"
    assert statistiche.percentuale(0.0996, 100) == "0.1%" and statistiche.percentuale(0.0951, 100) == "0.1%"
    assert statistiche.percentuale(0.0949, 100) == "0.09%" and statistiche.percentuale(0.05, 100) == "0.05%"
    assert statistiche.percentuale(0.004, 100) == "meno di 0.01%" and statistiche.percentuale(0.0096, 100) == "0.01%"
    assert statistiche.percentuale(58.44, 100) == "58.4%" and statistiche.percentuale(3, 3) == "100.0%"


def test_le_date_hanno_sempre_il_giorno_e_le_preposizioni_semplici(tmp_path):
    s, o = _nuove(tmp_path)
    s.avvio("1.103.2")
    o.avanti(86400)
    s.avvio("1.104.0", "1.103.2")
    s.dati["record"]["chiusura_non_regolare"] = {"valore": 0, "quando": "2026-10-19T18:03:00"}
    s.dati["conti"]["chiusure_non_regolari"] = 1
    for giorno in ("2026-11-01", "2026-11-02", "2026-11-03", "2026-11-05"):
        s.dati["giorni"][giorno] = {"aperto": 60, "play": 30, "marker": 1 if giorno == "2026-11-05" else 0}
    o.avanti(3 * 86400)
    testo = "\n".join(s.righe("1.104.0"))
    assert "Statistiche di MeTeOra 1.104.0, raccolte da domenica 1 novembre 2026 alle 10:00: 5 giorni, oggi compreso." in testo
    assert "Versioni usate: 1.103.2 da domenica 1 novembre 2026, 1.104.0 da lunedì 2 novembre 2026." in testo
    assert "; l'ultima dopo il salvataggio di lunedì 19 ottobre 2026 alle 18:03." in testo
    assert "Questa è la sessione numero 2, aperta lunedì 2 novembre 2026 alle 10:00: da 0 secondi." in testo
    assert "La serie più lunga di giorni di fila con ascolto: 3, da domenica 1 novembre 2026 a martedì 3 novembre 2026." in testo
    assert "Il giorno con più marker messi: giovedì 5 novembre 2026, 1." in testo
    # Nessuna data con le preposizioni di prima.
    assert not any(f" {p} {n} " in testo for p in ("dal", "al", "il", "del") for n in range(1, 32))
    assert not any(f"{p}{n} " in testo for p in ("dall'", "all'", "l'", "dell'") for n in (1, 8, 11))
    # Dopo l'azzeramento, l'ultimo senza preposizione.
    s.azzera()
    testo = "\n".join(s.righe("1.104.0"))
    assert "Azzerate 1 volta, l'ultima giovedì 5 novembre 2026 alle 10:00." in testo


def test_le_righe_elenco_tengono_solo_le_voci_diverse_da_zero(tmp_path):
    s, o = _nuove(tmp_path)
    s.avvio("1.104.0")
    # Nulla di suonato: la sezione delle famiglie non ha niente da dire, e
    # le righe per ora, giorno, fascia e mese non ci sono.
    s.dati["giorni"]["2026-10-15"] = {"aperto": 30}
    righe = s.righe("1.104.0")
    i = righe.index("Sezione 4 di 23, il tempo per famiglia.")
    assert righe[i + 1] == "Ancora niente da dire."
    testo = "\n".join(righe)
    assert "Per mese:" not in testo and "Per ora:" not in testo and "Per fascia:" not in testo and "Per giorno della settimana:" not in testo
    assert f"Formati mai suonati: {len(formati.TUTTI)}." in righe
    # Un brano la domenica alle 10, e un mese con l'apertura ma senza ascolto.
    s.brano_avviato("E:\\musica\\a.mp3")
    _passi(s, o, _suona(), 30)
    s.brano_finito()
    s.dati["schede_audio"]["Altoparlanti"] = 0
    s.dati["sorgenti"]["Ricerca"] = 0
    s.dati["tasti"] = {"Freccia su": 3, "Freccia giù": 0}
    s.dati["eventi"]["muto_acceso"] = 0
    righe = s.righe("1.104.0")
    testo = "\n".join(righe)
    assert "Per mese: novembre 2026, 30 secondi." in testo
    assert "Per giorno della settimana: domenica 100.0%." in testo and "Per fascia: mattina, dalle 6: 100.0%." in testo
    assert "Per ora: ore 10: 100.0%." in testo
    i = righe.index("Sezione 4 di 23, il tempo per famiglia.")
    assert righe[i + 1] == "Audio, MP3, FLAC e gli altri: 30 secondi, 100.0% della riproduzione; 1 avvio." and righe[i + 2] == ""
    assert "Schede audio: Cuffie, 100.0%." in testo and "Da dove: Preferiti 100.0%." in testo
    assert "Frecce: 3; freccia su 3." in testo and "Muto acceso:" not in testo
    assert "Eventi diversi accaduti: 0 su" in testo


def test_classifiche_e_piu_frequenti_senza_le_voci_a_zero(tmp_path):
    s, o = _nuove(tmp_path)
    # Un file toccato a mano: tasti, tasti senza comando, eventi e voci
    # delle impostazioni a zero.
    s.dati["tasti"] = {"X": 2, "Freccia giù": 0, "Canc": 0}
    s.dati["senza_comando"] = {"U accentata": 0}
    s.dati["eventi"] = {"zeta": 0, "play": 0}
    s.dati["impostazioni"] = {"volume": 0}
    righe = _pagina(s).la_tastiera()
    assert "I 20 tasti più premuti:" in righe and "1. X: 2." in righe
    assert not any(r.startswith("2. ") for r in righe)
    assert "Tasti senza comando: 0." in righe
    assert "Effetti sonori, contati anche con il volume degli effetti a zero: 0." in _pagina(s).la_console()
    assert "Voci delle impostazioni aperte con Invio: 0." in _pagina(s).le_impostazioni()
    # Tutti i tasti a zero: niente classifica.
    s.dati["tasti"] = {"X": 0}
    assert not any(r.startswith(("I 20 tasti", "1. ")) for r in _pagina(s).la_tastiera())
    # Con una voce diversa da zero, il piu' frequente e' lei, anche se a
    # zero ce n'e' una che verrebbe dopo nell'ordine dei nomi.
    s.dati["senza_comando"] = {"A": 1, "Z": 0}
    s.dati["eventi"] = {"play": 3, "zeta": 0}
    s.dati["impostazioni"] = {"a": 1, "z": 0}
    assert "Tasti senza comando: 1; il più frequente: A, 1 volta." in _pagina(s).la_tastiera()
    assert ("Effetti sonori, contati anche con il volume degli effetti a zero: 3; il più suonato: riproduzione avviata, 3 volte."
        in _pagina(s).la_console())
    assert "Voci delle impostazioni aperte con Invio: 1; la più usata: a, 1 volta." in _pagina(s).le_impostazioni()
    # Un autore che ha solo una voce con i marker, senza secondi e senza
    # avvii, non entra in classifica.
    schede = {"E:\\a.mp3": {"tag": {"autore": "Uno"}}, "E:\\b.mp3": {"tag": {"autore": "Due"}}}
    s.brano_avviato("E:\\a.mp3")
    _passi(s, o, _suona("E:\\a.mp3"), 3)
    s.marker_messo("E:\\b.mp3")
    righe = _pagina(s, schede.get).le_classifiche()
    assert "1. Uno: 3 secondi, 100.0%; 1 avvio di 1 file." in righe
    assert not any(r.startswith("2. Due") for r in righe)
    s.dati["brani"] = {"E:\\b.mp3": {"marker": 1}}
    assert not any(r.startswith(("I 20 autori", "Senza autore")) for r in _pagina(s, schede.get).le_classifiche())


def test_i_tasti_premuti_per_ora(tmp_path):
    s, _o = _nuove(tmp_path)
    s.dati["tasti"] = {"X": 254}
    s.dati["tempi"]["aperto"] = 254 / 855 * 3600
    assert _pagina(s).la_tastiera()[0] == "Tasti premuti: 254, cioè 855 per ogni ora di MeTeOra aperto."
    # Sotto i sei minuti aperti, il conto per ora non si fa.
    s.dati["tempi"]["aperto"] = 300
    assert _pagina(s).la_tastiera()[0] == "Tasti premuti: 254."
    # Nemmeno senza tasti premuti.
    s.dati["tasti"] = {}
    s.dati["tempi"]["aperto"] = 3600
    assert _pagina(s).la_tastiera()[0] == "Tasti premuti: 0."


def test_gli_anni_futuri_dei_tag_non_contano(tmp_path):
    s, o = _nuove(tmp_path)
    schede = {"E:\\a.mp3": {"tag": {"anno": 1985}}, "E:\\b.mp3": {"tag": {"anno": 2027}}, "E:\\c.mp3": {"tag": {"anno": 2026}}}
    for percorso, secondi in (("E:\\a.mp3", 20), ("E:\\b.mp3", 20), ("E:\\c.mp3", 10)):
        s.brano_avviato(percorso)
        _passi(s, o, _suona(percorso), secondi)
    righe = _pagina(s, schede.get).le_classifiche()
    # L'orologio dice 2026: il 2027 va con quelli senza anno.
    assert "Per decennio, dall'anno dei tag: anni '80 40.0%; anni 2020 20.0%; senza anno 40.0%." in righe
    assert "L'anno più ascoltato: 1985, 40.0%." in righe
    libreria = {"E:\\a.mp3": {"tag": {"anno": 1985}}, "E:\\b.mp3": {"tag": {"anno": 2031}}, "E:\\c.mp3": {"tag": {"anno": 9999}}}
    c = statistiche.censisci_la_libreria(libreria, anno_di_adesso=2030)
    assert c["anni"] == [1985] and dict(c["decenni"]) == {"anni '80": 1}
    assert "Dai tag: anni dal 1985 al 1985." in statistiche.righe_della_libreria(c, str)
    assert statistiche.censisci_la_libreria(libreria, anno_di_adesso=2031)["anni"] == [1985, 2031]
    # Senza anno_di_adesso vale quello di oggi.
    oggi = datetime.date.today().year
    assert statistiche.censisci_la_libreria(libreria)["anni"] == [a for a in (1985, 2031, 9999) if a <= oggi]


def test_la_libreria_senza_tag_e_senza_famiglie_vuote():
    c = statistiche.censisci_la_libreria({"E:\\a.mp3": {"dim": 10, "durata": 5.0}, "E:\\b.mp3": {"dim": 10, "durata": 5.0}})
    righe = statistiche.righe_della_libreria(c, lambda b: f"{b} byte")
    assert "Per numero di file: audio 2, 100.0%." in righe
    assert "Dai tag: nessun autore, album, genere o anno." in righe
    c = statistiche.censisci_la_libreria({"E:\\a.mp3": {"tag": {"autore": "A"}}}, anno_di_adesso=2026)
    assert "Dai tag: 1 autore." in statistiche.righe_della_libreria(c, str)


def test_la_pulizia_toglie_i_brani_mancanti_e_lascia_i_totali(tmp_path):
    s, o = _nuove(tmp_path)
    for percorso in ("E:\\Musica\\a.mp3", "E:\\Musica\\b.mp3", "E:\\Musica\\c.mp3", "E:\\Musica\\d.mp3", "E:\\Musica\\in corso.mp3"):
        s.brano_avviato(percorso)
        _passi(s, o, _suona(percorso), 3)
    assert s.percorsi_dei_brani() == ["E:\\Musica\\a.mp3", "E:\\Musica\\b.mp3", "E:\\Musica\\c.mp3", "E:\\Musica\\d.mp3", "E:\\Musica\\in corso.mp3"]
    # La lista e' nuova: cambiarla non tocca lo storico.
    s.percorsi_dei_brani().clear()
    assert len(s.dati["brani"]) == 5
    prima = json.loads(json.dumps({k: v for k, v in s.dati.items() if k != "brani"}))
    # I mancanti arrivano normalizzati: a e' scritto in un'altra forma; il
    # brano in corso e il file che suona restano anche se mancano.
    mancanti = {_norm("e:/musica/A.MP3"), _norm("E:\\Musica\\b.mp3"), _norm("E:\\Musica\\in corso.mp3"), _norm("E:\\Musica\\zeta.mp3")}
    assert s.togli_i_brani(mancanti, in_corso="E:\\Musica\\B.mp3") == 1
    assert list(s.dati["brani"]) == ["E:\\Musica\\b.mp3", "E:\\Musica\\c.mp3", "E:\\Musica\\d.mp3", "E:\\Musica\\in corso.mp3"]
    assert json.loads(json.dumps({k: v for k, v in s.dati.items() if k != "brani"})) == prima
    assert s.togli_i_brani(set()) == 0 and s.togli_i_brani({_norm("E:\\Musica\\c.mp3"), _norm("E:\\Musica\\d.mp3")}) == 2
    assert list(s.dati["brani"]) == ["E:\\Musica\\b.mp3", "E:\\Musica\\in corso.mp3"]


def test_un_brano_rinominato_porta_la_sua_voce(tmp_path, monkeypatch):
    s, o = _nuove(tmp_path)
    s.brano_avviato("E:\\C64\\vecchio.sid", 1)
    _passi(s, o, _suona("E:\\C64\\vecchio.sid"), 4)
    s.marker_messo("E:\\C64\\vecchio.sid")
    voce = dict(s.dati["brani"]["E:\\C64\\vecchio.sid"])
    # Un po' di tempo dopo l'ultimo passo: va allo stato di prima, che
    # deve seguire il file anche lui.
    o.avanti(0.6)
    # Il nome nuovo non ha voci: la voce passa com'e', e il brano in corso la segue.
    assert s.rinomina_brano("e:/c64/VECCHIO.sid", "E:\\C64\\nuovo.sid")
    assert s.dati["brani"] == {"E:\\C64\\nuovo.sid": voce} and s._brano["percorso"] == "E:\\C64\\nuovo.sid"
    assert s._stato["percorso"] == "E:\\C64\\nuovo.sid"
    _passi(s, o, _suona("E:\\C64\\nuovo.sid"), 2)
    # Lo storico ha solo il nome nuovo, con anche i secondi di quel passo.
    assert list(s.dati["brani"]) == ["E:\\C64\\nuovo.sid"]
    assert s._brano["ascoltato"] == pytest.approx(6.6)
    assert s.dati["brani"]["E:\\C64\\nuovo.sid"]["secondi"] == pytest.approx(6.6)
    s.brano_finito()
    assert s.dati["brani"]["E:\\C64\\nuovo.sid"]["finiti"] == 1
    # Un file che lo storico non conosce.
    assert not s.rinomina_brano("E:\\C64\\altro.sid", "E:\\C64\\altro2.sid")
    # Il nome nuovo ha gia' una voce: si uniscono.
    monkeypatch.setattr(statistiche, "MASSIMO_DEI_SOTTOBRANI", 3)
    s.dati["brani"]["E:\\C64\\nuovo.sid"].update({"volte": 2, "secondi": 1.5, "sotto": [1, 2], "ultima": "2026-11-01T09:00:00"})
    s.dati["brani"]["E:\\C64\\uno.sid"] = {"volte": 3, "secondi": 10.25, "finiti": 2, "marker": 4, "sotto": [2, 3, 4], "ultima": "2026-11-01T12:00:00"}
    assert s.rinomina_brano("E:\\C64\\nuovo.sid", "E:\\c64\\UNO.sid")
    assert s.dati["brani"] == {"E:\\c64\\UNO.sid": {"volte": 5, "secondi": 11.75, "finiti": 3, "marker": 5, "sotto": [1, 2, 3], "ultima": "2026-11-01T12:00:00"}}
    # Solo le maiuscole cambiate: la stessa voce, con il nome nuovo.
    assert s.rinomina_brano("E:\\c64\\UNO.sid", "E:\\C64\\Uno.sid") and list(s.dati["brani"]) == ["E:\\C64\\Uno.sid"]
    assert s.dati["brani"]["E:\\C64\\Uno.sid"]["volte"] == 5


def test_la_riga_delle_pulizie(tmp_path):
    s, _o = _nuove(tmp_path)
    assert "Pulizie all'avvio: nessuna." in _pagina(s).la_salute()
    s.conta("pulizie")
    assert "Pulizie all'avvio: 1; niente da togliere." in _pagina(s).la_salute()
    s.conta("pulizia_marker")
    assert "Pulizie all'avvio: 1; tolta 1 voce dei marker." in _pagina(s).la_salute()
    s.conta("pulizia_marker")
    assert "Pulizie all'avvio: 1; tolte 2 voci dei marker." in _pagina(s).la_salute()
    s.dati["conti"] = {"pulizie": 3, "pulizia_punti": 1}
    assert "Pulizie all'avvio: 3; tolto 1 punto da riprendere." in _pagina(s).la_salute()
    s.dati["conti"] = {"pulizie": 2, "pulizia_schede": 45578, "pulizia_brani": 5, "pulizia_marker": 2, "pulizia_punti": 1, "pulizia_storico": 3,
        "pulizia_radici_saltate": 2}
    assert ("Pulizie all'avvio: 2; tolti 45578 file dallo schedario, 5 brani da playlist e Preferiti, 2 voci dei marker, 1 punto da riprendere, "
        "3 brani dallo storico; unità saltate perché non rispondevano: 2.") in _pagina(s).la_salute()
    s.dati["conti"] = {"pulizie": 1, "pulizia_radici_saltate": 1}
    assert "Pulizie all'avvio: 1; niente da togliere; unità saltate perché non rispondevano: 1." in _pagina(s).la_salute()
    # Le schede doppie dello schedario, a parte dai file spariti, con
    # l'accordo di tolto.
    s.dati["conti"] = {"pulizie": 1, "pulizia_doppioni": 82}
    assert "Pulizie all'avvio: 1; tolte 82 schede doppie dello schedario." in _pagina(s).la_salute()
    s.dati["conti"] = {"pulizie": 1, "pulizia_doppioni": 1}
    assert "Pulizie all'avvio: 1; tolta 1 scheda doppia dello schedario." in _pagina(s).la_salute()
    s.dati["conti"] = {"pulizie": 1, "pulizia_doppioni": 3, "pulizia_marker": 2}
    assert "Pulizie all'avvio: 1; tolte 3 schede doppie dello schedario, 2 voci dei marker." in _pagina(s).la_salute()
    s.dati["conti"] = {"pulizie": 1, "pulizia_schede": 4, "pulizia_doppioni": 82}
    assert "Pulizie all'avvio: 1; tolti 4 file dallo schedario, 82 schede doppie dello schedario." in _pagina(s).la_salute()
    # Le pulizie non riuscite: in tutto, e di cui.
    s.dati["conti"] = {"pulizie_non_riuscite": 1}
    assert "Pulizie all'avvio: 1, non riuscita per un errore." in _pagina(s).la_salute()
    s.dati["conti"] = {"pulizie_non_riuscite": 2}
    assert "Pulizie all'avvio: 2, tutte non riuscite per un errore." in _pagina(s).la_salute()
    s.dati["conti"] = {"pulizie": 3, "pulizie_non_riuscite": 1}
    assert "Pulizie all'avvio: 4, di cui 1 non riuscita per un errore; niente da togliere." in _pagina(s).la_salute()
    s.dati["conti"] = {"pulizie": 1, "pulizie_non_riuscite": 2, "pulizia_storico": 1}
    assert "Pulizie all'avvio: 3, di cui 2 non riuscite per un errore; tolto 1 brano dallo storico." in _pagina(s).la_salute()
    assert [conto for conto, *_resto in statistiche.TOLTI_DALLA_PULIZIA] == ["pulizia_schede", "pulizia_doppioni", "pulizia_brani", "pulizia_marker",
        "pulizia_punti", "pulizia_storico"]


def test_gli_eventi_della_pulizia_sono_in_fondo():
    # In fondo, nell'ordine di suoni.EVENTI; dalla 1.105.0 li segue Dove
    # sono, e dalla 1.110.0 la durata residua.
    assert list(statistiche.NOMI_DEGLI_EVENTI)[-4:] == ["pulizia_avviata", "pulizia_finita", "dove_sono", "durata_residua"]
    assert statistiche.NOMI_DEGLI_EVENTI["pulizia_avviata"] == "pulizia all'avvio cominciata"
    assert statistiche.NOMI_DEGLI_EVENTI["pulizia_finita"] == "pulizia all'avvio finita"


def test_ogni_evento_ha_il_suo_nome():
    """Ogni suono di MeTeOra ha un nome nelle statistiche, e ogni nome un suono."""
    import suoni

    assert set(statistiche.NOMI_DEGLI_EVENTI) == set(suoni.EVENTI)


def test_la_riga_delle_playlist_dice_ordinate_invertite_mescolate_e_rimesse(tmp_path):
    # Tappa 14 c: i quattro eventi nuovi hanno un nome e stanno nella riga delle playlist.
    s, _o = _nuove(tmp_path)
    for evento, volte in (("playlist_ordinata", 3), ("ordine_invertito", 1), ("playlist_mescolata", 2), ("ordine_ripristinato", 1)):
        assert evento in statistiche.NOMI_DEGLI_EVENTI
        for _ in range(volte):
            s.evento(evento)
    assert ("Playlist rinominate: 0; eliminate: 0; ordinate: 3; invertite: 1; mescolate: 2; rimesse nell'ordine di prima: 1."
        in _pagina(s).le_playlist())
