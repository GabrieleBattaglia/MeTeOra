# MeTeOra, le prove delle registrazioni: libmpv vero su file locali, niente rete.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 10/11/2026: nasce con la 3.5.0, issue 42. Nella 3.13.0 la cartella delle registrazioni; nella 3.13.2 l'attesa al passaggio e le parti non unite.

import datetime
import os
import threading
import time
import types
import typing
import wave

import numpy as np
import pytest

import registrazioni  # per primo, perche' carica libmpv

# isort: split
import mpv

import indirizzi
import statistiche
from playlist import Brano

RADIO = "http://icestreaming.rai.it/3.mp3"


def _seno(percorso, secondi, frequenza=44100, canali=1):
    campioni = (0.25 * np.sin(2 * np.pi * 440 * np.arange(int(frequenza * secondi)) / frequenza) * 32767).astype("<i2")
    if canali == 2:
        campioni = np.repeat(campioni, 2)
    with wave.open(str(percorso), "wb") as f:
        f.setnchannels(canali)
        f.setsampwidth(2)
        f.setframerate(frequenza)
        f.writeframes(campioni.tobytes())
    return str(percorso)


def _durata(percorso):
    lettore = mpv.MPV(vo="null", ao="null", video="no", config=False)
    pronto = threading.Event()
    lettore.register_event_callback(lambda e: pronto.set() if e.event_id.value in (mpv.MpvEventID.FILE_LOADED, mpv.MpvEventID.END_FILE) else None)
    lettore.command("loadfile", str(percorso))
    pronto.wait(10)
    traccia = next((t for t in lettore.track_list or [] if t.get("type") == "audio"), {})
    durata = lettore.duration
    lettore.terminate()
    if str(percorso).endswith(".wav"):
        # Del WAV la durata vera la dice l'intestazione.
        with wave.open(str(percorso), "rb") as f:
            durata = f.getnframes() / f.getframerate()
    return durata, traccia.get("demux-channel-count"), traccia.get("demux-samplerate")


def _registrata(tmp_path, nome, secondi, formato="mp3", kbps=64, canali=1, frequenza=44100):
    """Una registrazione di un file locale, che finisce da se', completa."""
    sorgente = _seno(tmp_path / f"{nome}.wav", secondi)
    finita = threading.Event()
    reg = registrazioni.Registrazione(sorgente, nome, indirizzi.Flusso(sorgente), formato, kbps, canali, frequenza, dove=str(tmp_path / "Registrazioni"),
        al_termine=lambda _r: finita.set())
    reg.avvia()
    assert finita.wait(30)
    return reg


# Il modulo, senza finestra.


def test_il_nome_del_file(tmp_path):
    quando = datetime.datetime(2026, 11, 10, 16, 5, 12)
    percorso = registrazioni.nome_del_file('Rai Radio 3: "prova"/<due>', quando, ".mp3", str(tmp_path))
    assert os.path.basename(percorso) == "Rai Radio 3 prova due 2026-11-10 16.05.12.mp3"
    open(percorso, "wb").close()
    assert os.path.basename(registrazioni.nome_del_file("Rai Radio 3: prova/due", quando, ".mp3", str(tmp_path))).endswith("16.05.12 2.mp3")
    assert os.path.basename(registrazioni.nome_del_file("...", quando, ".wav", str(tmp_path))).startswith("Registrazione 2026")
    assert registrazioni.estensioni() == {".mp3", ".opus", ".aac", ".flac", ".wav"}


def test_la_qualita_si_adatta_alla_sorgente():
    assert registrazioni.parametri("mp3", 128) == (128, 2, 44100)
    # Mono con meta' dei kbps, mai piu' della sorgente, mai piu' campioni della sorgente.
    assert registrazioni.parametri("mp3", 128, sorgente_kbps=320, canali=1, frequenza=48000) == (64, 1, 44100)
    assert registrazioni.parametri("mp3", 128, sorgente_kbps=56, canali=2, frequenza=22050) == (48, 2, 22050)
    assert registrazioni.parametri("mp3", 32, sorgente_kbps=20, canali=1) == (32, 1, 44100)
    assert registrazioni.parametri("opus", 96, canali=2, frequenza=22050) == (96, 2, 48000)
    assert registrazioni.parametri("flac", 128, sorgente_kbps=64, canali=1, frequenza=96000) == (None, 1, 48000)
    assert registrazioni.parametri("wav", 320, frequenza=22050) == (None, 2, 22050)
    assert registrazioni.descrizione("mp3", 128, 2, 44100) == "MP3 a 128 kbps, stereo, 44.1 kHz"
    assert registrazioni.descrizione("flac", None, 1, 48000) == "FLAC, mono, 48 kHz"


@pytest.mark.parametrize("formato", ["mp3", "opus", "aac", "flac", "wav"])
def test_una_registrazione_che_finisce_da_se(tmp_path, formato):
    reg = _registrata(tmp_path, f"breve {formato}", 3.0, formato)
    assert reg.stato == "completa" and os.path.exists(reg.percorso) and reg.percorso.endswith(registrazioni.FORMATI[formato][3])
    durata, canali, frequenza = _durata(reg.percorso)
    # Dell'AAC grezzo libmpv stima la durata dai kbps, e sbaglia; il WAV ha in
    # coda un terzo di secondo di silenzio, il riempimento dell'ultimo blocco
    # del codificatore PCM di libmpv (prova del 10 novembre 2026).
    tolleranza = 0.5 if formato == "wav" else 0.2
    assert (abs(durata - 3.0) < tolleranza or formato == "aac") and canali == 1 and frequenza == (48000 if formato == "opus" else 44100)
    assert (abs(reg.secondi - 3.0) < tolleranza or formato == "aac") and reg.byte == os.path.getsize(reg.percorso)
    assert not [f for f in os.listdir(os.path.dirname(reg.percorso)) if ".parziale" in f]


def test_le_parti_si_uniscono(tmp_path):
    """Le parti dopo una ripresa: senza tagli un MP3 si accoda; con la
    riserva da togliere, o in FLAC, si riscrive."""
    for formato, taglio in (("mp3", 0.0), ("mp3", 1.0), ("flac", 1.0)):
        uno = _registrata(tmp_path, f"uno {formato} {taglio}", 2.0, formato)
        due = _registrata(tmp_path, f"due {formato} {taglio}", 3.0, formato)
        reg = registrazioni.Registrazione(RADIO, f"unione {formato} {taglio}", indirizzi.Flusso(RADIO, dal_vivo=True), formato, 64, 1, 44100,
            dove=str(tmp_path / "Registrazioni"))
        parti = []
        for origine, secondi, tolto in ((uno, 2.0, 0.0), (due, 3.0, taglio)):
            parte = registrazioni.Parte(origine.percorso)
            parte.secondi, parte.taglio = secondi, tolto
            parti.append(parte)
        reg._parti = parti
        reg._unisci()
        durata, _canali, _frequenza = _durata(reg.percorso)
        assert abs(durata - (5.0 - taglio)) < 0.2, (formato, taglio, durata)
        assert abs(reg.secondi - (5.0 - taglio)) < 0.01 and not os.path.exists(uno.percorso) and not os.path.exists(due.percorso)


def test_eliminare_toglie_i_file(tmp_path):
    reg = _registrata(tmp_path, "da togliere", 1.0)
    assert os.path.exists(reg.percorso)
    reg.elimina()
    assert reg.stato == "eliminata" and not os.path.exists(reg.percorso)


def test_la_riserva_di_una_ripresa_si_misura_con_l_orologio(monkeypatch):
    """Dopo la prima parte, i secondi registrati in piu' dell'orologio sono la riserva della radio."""
    reg = registrazioni.Registrazione(RADIO, "x", indirizzi.Flusso(RADIO, dal_vivo=True), dove="non usata")
    parte = registrazioni.Parte("x.parziale2")
    parte.posizione = 30.0
    reg._parti = [registrazioni.Parte("x.parziale1")]
    reg._partita = 100.0
    monkeypatch.setattr(registrazioni.time, "monotonic", lambda: 106.0)
    assert reg._registrati(parte, types.SimpleNamespace(time_pos=None)) == (30.0, 24.0)
    puntata = registrazioni.Registrazione("x", "x", indirizzi.Flusso("https://x/p.mp3"), dove="non usata")
    puntata._parti = reg._parti
    assert puntata._registrati(parte, types.SimpleNamespace(time_pos=31.0)) == (31.0, 0.0)


# Le registrazioni nella finestra.


class _Finta:
    """Una registrazione finta: annota i comandi, e ferma dice il suo file."""

    create: typing.ClassVar[list] = []

    def __init__(self, sorgente, titolo, flusso, formato, kbps, canali, frequenza, al_termine=None, dove=None):
        self.sorgente, self.titolo, self.flusso = sorgente, titolo, flusso
        self.formato, self.kbps, self.canali, self.frequenza, self.al_termine = formato, kbps, canali, frequenza, al_termine
        self.dal_vivo = getattr(flusso, "dal_vivo", True)
        self.stato, self.secondi, self.byte, self.comandi = "pronta", 754.0, 11_534_336, []
        self.dove = dove
        self.percorso = os.path.join(dove or registrazioni.cartella(), f"{titolo}.mp3")
        _Finta.create.append(self)

    @property
    def descrizione(self):
        return registrazioni.descrizione(self.formato, self.kbps, self.canali, self.frequenza)

    def avvia(self):
        self.comandi.append("avvia")
        self.stato = "in_corso"

    def pausa(self, valore):
        self.comandi.append(("pausa", valore))
        self.stato = "in_pausa" if valore else "in_corso"

    def ferma(self):
        self.comandi.append("ferma")
        self.stato = "finita"
        os.makedirs(os.path.dirname(self.percorso), exist_ok=True)
        open(self.percorso, "wb").close()
        return self.percorso

    def elimina(self):
        self.comandi.append("elimina")
        self.stato = "eliminata"


@pytest.fixture
def con_registrazioni(finestra, monkeypatch):
    """Una radio che suona per finta, la registrazione finta, e il lavoro in disparte subito."""
    import finestra as modulo

    _Finta.create = []
    monkeypatch.setattr(modulo.registrazioni, "Registrazione", _Finta)
    for nome in ("registrazioni_in_disparte", "radio_in_disparte"):
        monkeypatch.setattr(modulo, nome, lambda lavoro, al_termine: al_termine(lavoro()))
    monkeypatch.setattr(modulo.wx, "CallAfter", lambda funzione, *argomenti, **chiavi: funzione(*argomenti, **chiavi))
    monkeypatch.setattr(modulo.wx, "CallLater", lambda _ms, funzione, *argomenti: funzione(*argomenti))
    monkeypatch.setattr(finestra.motore, "suona", lambda *argomenti, **chiavi: None)
    brano = Brano(RADIO, titolo="Rai Radio 3", radio={"uuid": "u", "paese": "IT", "bitrate": 320})
    stato = {"in_corso": None}
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda self: stato["in_corso"]))
    monkeypatch.setattr(type(finestra.motore), "caratteristiche", lambda self: (320, 2, 48000))
    return types.SimpleNamespace(brano=brano, stato=stato)


def _suona_la_radio(finestra, radio):
    # Il motore finto suona subito: l'attesa di Alt con R la trova gia' partita.
    radio.stato["in_corso"] = radio.brano.percorso
    finestra.archivio.metti_la_radio(radio.brano)
    finestra._suona(finestra.archivio.radio, radio.brano)


def test_registrare_una_radio(finestra, con_registrazioni, suoni_annotati):
    from test_finestra import _premi

    assert _premi(finestra, "r").startswith("Nessuna registrazione. Maiuscolo con R registra")
    assert _premi(finestra, "r", maiuscolo=True).startswith("Non suona niente da registrare") and suoni_annotati[-1] == "non_disponibile"
    finestra.coda.imposta(None, Brano(r"C:\musica\a.mp3"))
    con_registrazioni.stato["in_corso"] = r"C:\musica\a.mp3"
    assert _premi(finestra, "r", maiuscolo=True) == "a.mp3 è un file, già sul disco: si registrano le radio e gli indirizzi in rete."
    _suona_la_radio(finestra, con_registrazioni)
    assert _premi(finestra, "r", maiuscolo=True) == "Registro Rai Radio 3, in MP3 a 128 kbps, stereo, 44.1 kHz. Ctrl con R la ferma."
    reg = _Finta.create[-1]
    assert suoni_annotati[-1] == "registrazione_avviata" and reg.flusso.dal_vivo and reg.comandi == ["avvia"]
    assert _premi(finestra, "r").startswith("Registro Rai Radio 3, 12:34, 12 MB, in MP3")
    assert _premi(finestra, "r", maiuscolo=True).startswith("Registrazione in pausa: Rai Radio 3, 12:34") and suoni_annotati[-1] == "registrazione_in_pausa"
    assert _premi(finestra, "r").startswith("Registrazione in pausa")
    assert _premi(finestra, "r", maiuscolo=True).startswith("Registrazione ripresa") and reg.comandi[-2:] == [("pausa", True), ("pausa", False)]
    assert _premi(finestra, "r", ctrl=True).startswith("Registrazione finita: Rai Radio 3, 12:34, 12 MB") and suoni_annotati[-1] == "registrazione_fermata"
    assert finestra._registrazione is None and reg.comandi[-1] == "ferma"
    conti = finestra._statistiche.dati["conti"]
    assert conti["registrazioni_avviate"] == 1 and conti["registrazioni_finite"] == 1 and conti["secondi_registrati"] == 754
    assert _premi(finestra, "r", ctrl=True) == "Non c'è una registrazione da fermare."
    # Il ramo Registrazioni ha il file, e Ctrl e Maiuscolo con R ci portano.
    assert _premi(finestra, "r", ctrl=True, maiuscolo=True) == "Registrazioni: 1 file."
    assert finestra._voce_corrente() == finestra.nodo_registrazioni and suoni_annotati[-1] == "alle_registrazioni"
    finestra.albero.Expand(finestra.nodo_registrazioni)
    assert [finestra.albero.GetItemText(v) for v in finestra._figli(finestra.nodo_registrazioni)] == ["Rai Radio 3.mp3"]
    # La sezione Le registrazioni delle statistiche (3.9.2).
    righe = statistiche.Pagina(finestra._statistiche, "", None, None, {}, {}, {}).le_registrazioni()
    assert righe[0] == "Registrazioni avviate: 1, di cui con l'attesa di Alt con R 0; file prodotti: 1, con 12 minuti e 34 secondi e 12 MB."
    assert "In media una registrazione dura 12 minuti e 34 secondi e pesa 12 MB." in righe
    assert "Dalle dirette, come le radio: 1; dalle puntate e dai video, che finiscono da soli: 0." in righe
    assert "Per formato: MP3 1." in righe and any(r.startswith("La registrazione più lunga: 12 minuti e 34 secondi, di Rai Radio 3") for r in righe)
    assert not any(r.startswith("Registrazioni avviate") for r in statistiche.Pagina(finestra._statistiche, "", None, None, {}, {}, {}).le_playlist())


def test_l_attesa_di_alt_con_r_e_l_eliminazione(finestra, con_registrazioni, monkeypatch, suoni_annotati):
    from test_finestra import _premi

    assert _premi(finestra, "r", alt=True).startswith("In ascolto: registro la prossima radio") and suoni_annotati[-1] == "registrazione_in_ascolto"
    assert _premi(finestra, "r").startswith("In ascolto")
    assert _premi(finestra, "r", alt=True, maiuscolo=True) == "Niente più attesa: la prossima radio non si registra."
    _premi(finestra, "r", alt=True)
    _suona_la_radio(finestra, con_registrazioni)
    # Il brano partito si registra da solo, dopo l'attesa della sorgente.
    reg = _Finta.create[-1]
    assert reg.titolo == "Rai Radio 3" and finestra._registrazione is reg and not finestra._in_ascolto
    assert _premi(finestra, "r", alt=True).startswith("Sto già registrando Rai Radio 3")
    risposta = [False]
    monkeypatch.setattr(finestra, "_conferma", lambda *argomenti: risposta[0])
    assert _premi(finestra, "r", alt=True, maiuscolo=True) == "La registrazione continua."
    risposta[0] = True
    assert _premi(finestra, "r", alt=True, maiuscolo=True) == "Registrazione di Rai Radio 3 eliminata." and reg.comandi[-1] == "elimina"
    assert finestra._registrazione is None and suoni_annotati[-1] == "registrazione_eliminata"
    # Ctrl e Alt con R aprono la cartella.
    aperte = []
    import finestra as modulo

    monkeypatch.setattr(modulo.os, "startfile", aperte.append, raising=False)
    assert _premi(finestra, "r", ctrl=True, alt=True).startswith("Apro la cartella delle registrazioni") and aperte == [registrazioni.cartella()]


def test_una_radio_caduta_e_le_impostazioni_delle_registrazioni(finestra, con_registrazioni, suoni_annotati):
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    reg.stato = "interrotta"
    reg.al_termine(reg)
    assert finestra._righe[-1].startswith("La registrazione di Rai Radio 3 si è interrotta") and suoni_annotati[-1] == "errore"
    assert finestra._registrazione is None and finestra._statistiche.dati["conti"]["registrazioni_interrotte"] == 1
    assert finestra._riga_dell_impostazione("formato_registrazioni") == "Formato delle registrazioni: MP3, il più diffuso"
    assert finestra._riga_dell_impostazione("qualita_registrazioni") == "Qualità delle registrazioni: 128 kbps"
    finestra.impostazioni["formato_registrazioni"] = "flac"
    assert finestra._riga_dell_impostazione("qualita_registrazioni") == "Qualità delle registrazioni: 128 kbps, che non conta per FLAC"
    # Una puntata che finisce da se' e' completa.
    finestra.impostazioni["formato_registrazioni"] = "mp3"
    finestra._comando_registra()
    reg = _Finta.create[-1]
    reg.stato = "completa"
    reg.al_termine(reg)
    assert "è arrivata alla fine" in finestra._righe[-1] and suoni_annotati[-1] == "registrazione_fermata"


def test_le_registrazioni_si_chiudono_con_meteora(finestra, con_registrazioni):
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    finestra.Close(force=True)
    assert reg.comandi[-1] == "ferma"
    time.sleep(0)


class _DialogoDiCartella:
    """La finestra delle cartelle di Windows, finta: risponde con la cartella data, o annulla."""

    risposte: typing.ClassVar[list] = []
    aperti: typing.ClassVar[list] = []

    def __init__(self, _genitore, titolo, defaultPath="", style=0):
        _DialogoDiCartella.aperti.append((titolo, defaultPath))

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def ShowModal(self):
        import wx

        self.scelta = _DialogoDiCartella.risposte.pop(0)
        return wx.ID_CANCEL if self.scelta is None else wx.ID_OK

    def GetPath(self):
        return self.scelta


def test_la_cartella_delle_registrazioni(finestra, con_registrazioni, monkeypatch, tmp_path):
    # La voce delle impostazioni (Gabriele, 3.13.0): la finestra delle
    # cartelle di Windows, e le registrazioni nuove nella cartella scelta.
    import finestra as modulo

    monkeypatch.setattr(modulo, "DialogoDiCartella", _DialogoDiCartella)
    _DialogoDiCartella.aperti.clear()
    di_sempre = registrazioni.cartella()
    assert finestra._riga_dell_impostazione("cartella_registrazioni") == f"Cartella delle registrazioni: Registrazioni, accanto ai dati di MeTeOra: {di_sempre}"
    scelta = tmp_path / "Le mie registrazioni"
    _DialogoDiCartella.risposte[:] = [None, str(scelta)]
    finestra._cambia_impostazione("cartella_registrazioni", None)

    def riga():
        # L'ultima riga della console, senza l'ora in fondo.
        return finestra._righe[-1].rsplit(" ", 1)[0]

    assert finestra.impostazioni["cartella_registrazioni"] == "" and riga() == "Cartella delle registrazioni non cambiata."
    finestra._cambia_impostazione("cartella_registrazioni", None)
    assert finestra.impostazioni["cartella_registrazioni"] == str(scelta) and scelta.is_dir()
    assert riga() == f"Le registrazioni nuove vanno in {scelta}; quelle di prima restano dove sono."
    assert finestra._riga_dell_impostazione("cartella_registrazioni") == f"Cartella delle registrazioni: {scelta}"
    assert _DialogoDiCartella.aperti[0][0] == "Cartella delle registrazioni"
    # La registrazione nuova va li', e Ctrl e Alt con R aprono quella.
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    assert reg.dove == str(scelta) and os.path.dirname(reg.percorso) == str(scelta)
    aperte = []
    monkeypatch.setattr(modulo.os, "startfile", aperte.append, raising=False)
    finestra._comando_apri_la_cartella_delle_registrazioni()
    assert aperte == [str(scelta)]
    # Con la registrazione in corso, la scelta lo dice; e scegliere quella di
    # sempre la rimette come predefinita.
    _DialogoDiCartella.risposte[:] = [di_sempre]
    finestra._cambia_impostazione("cartella_registrazioni", None)
    assert finestra.impostazioni["cartella_registrazioni"] == "" and riga().endswith("La registrazione in corso finisce dov'è.")
    assert _DialogoDiCartella.aperti[-1][1] == str(scelta)
    finestra._comando_ferma_la_registrazione()
    assert os.path.exists(reg.percorso)
    # Una cartella che non c'e' piu' si dice.
    finestra.impostazioni["cartella_registrazioni"] = str(tmp_path / "staccata")
    assert finestra._riga_dell_impostazione("cartella_registrazioni").endswith("staccata, che non si trova")
    assert finestra._statistiche.dati["conti"]["cartelle_delle_registrazioni_cambiate"] == 2
    righe = statistiche.Pagina(finestra._statistiche, "", None, None, {}, {}, {}).le_registrazioni()
    assert "La cartella delle registrazioni cambiata nelle impostazioni: 2 volte." in righe


def test_l_attesa_di_alt_con_r_e_il_brano_che_entra_con_il_passaggio(finestra, con_registrazioni):
    # Il seguente di una playlist di indirizzi, preparato, entra con il
    # passaggio senza essere suonato da capo: con l'attesa di Alt con R si
    # registra anche lui (3.13.2; prima no).
    import finestra as modulo

    file = Brano(r"C:\m\a.mp3")
    video = Brano("https://www.youtube.com/watch?v=prova", titolo="Il video di prova")
    indirizzi.metti_il_diretto(video.percorso)
    pl = modulo.Playlist("Video", [file, video], cartella="")
    finestra.coda.imposta(pl, file)
    finestra._in_ascolto = True
    finestra._uscente, finestra._preparato = (pl, file, None), (pl, video, None)
    con_registrazioni.stato["in_corso"] = video.percorso
    finestra._passaggio(video.percorso, None)
    assert finestra.coda.corrente is video and finestra._registrazione is _Finta.create[-1]
    assert _Finta.create[-1].sorgente == video.percorso and not finestra._in_ascolto


def test_le_parti_che_non_si_uniscono_restano_file(tmp_path, monkeypatch):
    # Un'unione che fallisce non perde niente: le parti diventano file da
    # ascoltare (3.13.2; prima restavano .parziale, nascoste).
    vera = registrazioni._riscrivi
    uno = _registrata(tmp_path, "uno", 2.0)
    due = _registrata(tmp_path, "due", 3.0)
    reg = registrazioni.Registrazione(RADIO, "radio lunga", indirizzi.Flusso(RADIO, dal_vivo=True), "mp3", 64, 1, 44100, dove=str(tmp_path / "Registrazioni"))
    parti = []
    for origine, secondi, taglio in ((uno, 2.0, 0.0), (due, 3.0, 1.0)):
        parte = registrazioni.Parte(origine.percorso)
        parte.secondi, parte.taglio = secondi, taglio
        parti.append(parte)
    reg._parti = parti
    base = os.path.splitext(reg.percorso)[0]

    def rotta(*_argomenti):
        raise OSError("le parti della registrazione non si uniscono")

    monkeypatch.setattr(registrazioni, "_riscrivi", rotta)
    percorso = reg.ferma()
    assert reg.parti_separate == [f"{base} parte 1.mp3", f"{base} parte 2.mp3"] and percorso == reg.parti_separate[0]
    assert all(os.path.exists(f) for f in reg.parti_separate) and not os.path.exists(uno.percorso) and not os.path.exists(due.percorso)
    # La riscrittura vera, con una parte che non c'e', fallisce e non lascia
    # un file a meta'.
    with pytest.raises(OSError):
        vera([registrazioni.Parte(str(tmp_path / "manca.mp3"))], str(tmp_path / "unione.mp3"), "mp3", 64, 1, 44100)
    assert not os.path.exists(tmp_path / "unione.mp3")


def test_la_console_dice_le_parti_che_non_si_sono_unite(finestra, con_registrazioni, suoni_annotati):
    _suona_la_radio(finestra, con_registrazioni)
    finestra._comando_registra()
    reg = _Finta.create[-1]
    reg.parti_separate = [os.path.join(registrazioni.cartella(), "Rai Radio 3 parte 1.mp3"), os.path.join(registrazioni.cartella(), "Rai Radio 3 parte 2.mp3")]
    finestra._registrazione_fermata(reg, reg.parti_separate[0])
    assert finestra._righe[-1].startswith("Le parti della registrazione di Rai Radio 3 non si sono unite: sono 2 file, nel ramo Registrazioni, come Rai Radio 3 parte 1.mp3.")
    assert suoni_annotati[-1] == "errore" and finestra._statistiche.dati["conti"]["registrazioni_a_parti_separate"] == 1
