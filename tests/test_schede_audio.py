# MeTeOra, le prove delle schede audio: elenco, etichette, ritrovamento in mpv, applicazione della scelta.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.51.0, piano 5.8.9.

"""Le prove di schede_audio, con GBUtils e mpv sostituiti.

Le funzioni audio di GBUtils aprono davvero i dispositivi per provarli e
cambiano il mixer condiviso: qui sono tutte sostituite da un finto che le
annota, e una chiamata non prevista fa fallire la prova invece di arrivare
alla scheda. L'elenco finto ricalca quello vero della macchina di Gabriele.
Il motore vero si prova su ao=null, che non suona.
"""

import GBUtils
import pytest

import schede_audio

INTERFACCE = {"ASIO": "ASIO", "WASAPI": "Windows WASAPI", "WDM-KS": "Windows WDM-KS", "DirectSound": "Windows DirectSound", "MME": "MME"}
ALTOPARLANTI = "Altoparlanti (Realtek(R) Audio)"
DIGITALE = "Realtek Digital Output (Realtek(R) Audio)"
STEAM = "Altoparlanti (Steam Streaming Speakers)"
MICROFONO = "Altoparlanti (Steam Streaming Microphone)"
LATENZA_ASIO = 23.219954648526077


def _voce(indice, dispositivo, breve, latenza, stessa=False):
    return {"indice": indice, "dispositivo": dispositivo, "interfaccia": INTERFACCE[breve], "breve": breve, "canali": 2, "frequenza": 48000.0,
            "latenza": latenza, "predefinito": indice == 4, "stessa_scheda": stessa, "esclusiva": breve in ("ASIO", "WDM-KS"), "apribile": None,
            "motivo": None}


# Nell'ordine di GBUtils: prima la stessa scheda del predefinito, poi per
# preferenza d'interfaccia (ASIO, WASAPI, WDM-KS, DirectSound, MME) e indice.
# MME taglia i nomi a 31 caratteri; un nome WDM-KS ha un a capo dentro.
ELENCO = [
    _voce(18, ALTOPARLANTI, "WASAPI", 3.0, stessa=True),
    _voce(12, ALTOPARLANTI, "DirectSound", 120.0, stessa=True),
    _voce(4, ALTOPARLANTI, "MME", 90.0, stessa=True),
    _voce(16, "Realtek ASIO", "ASIO", LATENZA_ASIO),
    _voce(17, "ReaRoute ASIO (x64)", "ASIO", LATENZA_ASIO),
    _voce(19, DIGITALE, "WASAPI", 3.0),
    _voce(20, STEAM, "WASAPI", 3.0),
    _voce(21, MICROFONO, "WASAPI", 3.0),
    _voce(24, "Speakers (Realtek HD Audio output)", "WDM-KS", 10.0),
    _voce(34, "Output (@System32\\drivers\\bthhfenum.sys,#4;%1 Hands-Free HF Audio%0\r\n;(iPhone))", "WDM-KS", 10.0),
    _voce(11, "Driver audio principale", "DirectSound", 120.0),
    _voce(13, DIGITALE, "DirectSound", 120.0),
    _voce(15, "Cuffie\r\n(Bluetooth)", "DirectSound", 120.0),
    _voce(3, "Microsoft Sound Mapper - Output", "MME", 90.0),
    _voce(5, DIGITALE[:31], "MME", 90.0),
    _voce(6, STEAM[:31], "MME", 90.0),
    _voce(7, MICROFONO[:31], "MME", 90.0),
]
# Come lo da' mpv anche con ao=wasapi: c'e' auto e ci sono altri driver.
ELENCO_MPV = [
    {"name": "auto", "description": "Autoselect device"},
    {"name": "wasapi/{a}", "description": ALTOPARLANTI},
    {"name": "wasapi/{b}", "description": DIGITALE},
    {"name": "wasapi/{c}", "description": STEAM},
    {"name": "wasapi/{d}", "description": MICROFONO},
    {"name": "openal", "description": "Default (OpenAL)"},
    {"name": "openal/Realtek ASIO", "description": "Realtek ASIO"},
]


class _GBUtilsFinto:
    """Le funzioni audio di GBUtils, annotate nell'ordine in cui arrivano."""

    def __init__(self):
        self.elenco = ELENCO
        self.scelta = (18, "Windows WASAPI")
        self.device = None
        self.chiamate = []

    def elenco_dispositivi_audio(self, prova="predefinito", modo="scrittura"):
        # Con prova diversa da nessuno GBUtils aprirebbe i dispositivi.
        assert prova == "nessuno" and modo == "scrittura"
        self.chiamate.append("elenco")
        return [dict(v) for v in self.elenco]

    def scegli_dispositivo_audio(self, api=None, riprova=False, modo="scrittura"):
        assert api is None and riprova is True and modo == "scrittura"
        self.chiamate.append("scegli")
        return self.scelta

    def setup(self, **valori):
        assert set(valori) == {"device"} and type(valori["device"]) is int
        self.chiamate.append(("setup", valori["device"]))
        return {"device": valori["device"]}

    def stato(self):
        return {"stream_aperto": False, "device": self.device, "interfaccia": None}


class _MotoreFinto:
    """Il motore come lo vede schede_audio: un dispositivo e l'elenco di mpv."""

    def __init__(self, gb, dispositivo="auto"):
        self._gb = gb
        self._dispositivo = dispositivo

    @property
    def dispositivo(self):
        return self._dispositivo

    @dispositivo.setter
    def dispositivo(self, nome):
        self._gb.chiamate.append(("mpv", nome))
        self._dispositivo = nome

    def dispositivi(self):
        self._gb.chiamate.append("elenco_mpv")
        return [dict(v) for v in ELENCO_MPV]


@pytest.fixture
def gb(monkeypatch):
    """GBUtils sostituito: nessuna prova arriva al mixer o ai dispositivi veri."""
    finto = _GBUtilsFinto()
    monkeypatch.setattr(GBUtils, "elenco_dispositivi_audio", finto.elenco_dispositivi_audio)
    monkeypatch.setattr(GBUtils, "scegli_dispositivo_audio", finto.scegli_dispositivo_audio)
    monkeypatch.setattr(GBUtils.Acusticator, "setup", finto.setup)
    monkeypatch.setattr(GBUtils.Acusticator, "stato", finto.stato)
    return finto


def _uscita(indice):
    return next(u for u in schede_audio.uscite() if u["indice"] == indice)


def test_uscite_senza_wdm_ks_in_ordine_di_latenza(gb):
    elenco = schede_audio.uscite()
    assert gb.chiamate == ["elenco"]
    # Dentro la stessa latenza resta l'ordine di GBUtils: la scheda gia' in
    # uso davanti, poi per indice.
    assert [u["indice"] for u in elenco] == [18, 19, 20, 21, 16, 17, 4, 3, 5, 6, 7, 12, 11, 13, 15]
    assert all(u["breve"] != "WDM-KS" for u in elenco)
    assert all(set(u) == {"indice", "dispositivo", "interfaccia", "breve", "latenza", "esclusiva"} for u in elenco)
    assert elenco[0] == {"indice": 18, "dispositivo": ALTOPARLANTI, "interfaccia": "Windows WASAPI", "breve": "WASAPI", "latenza": 3.0, "esclusiva": False}
    assert [u["esclusiva"] for u in elenco if u["breve"] == "ASIO"] == [True, True]
    # L'a capo nel nome diventa uno spazio.
    assert elenco[-1]["dispositivo"] == "Cuffie (Bluetooth)"
    assert not any("\r" in u["dispositivo"] or "\n" in u["dispositivo"] for u in elenco)


def test_etichette(gb):
    assert schede_audio.etichetta(_uscita(18)) == "Altoparlanti (Realtek(R) Audio), WASAPI, 3 ms"
    assert schede_audio.etichetta(_uscita(16)) == "Realtek ASIO, ASIO, 23.2 ms, esclusiva: può zittire NVDA"
    assert schede_audio.etichetta(_uscita(5)) == "Realtek Digital Output (Realtek, MME, 90 ms"
    assert schede_audio.etichetta(_uscita(15)) == "Cuffie (Bluetooth), DirectSound, 120 ms"
    voce = {"indice": 1, "dispositivo": "Scheda", "interfaccia": "Windows WASAPI", "breve": "WASAPI", "latenza": 2.96, "esclusiva": False}
    assert schede_audio.etichetta(voce) == "Scheda, WASAPI, 3 ms"
    assert schede_audio.etichetta({**voce, "latenza": 0.54}) == "Scheda, WASAPI, 0.5 ms"
    # Senza latenza e senza nome breve: l'interfaccia senza Windows, e niente millesimi.
    assert schede_audio.etichetta({"indice": 1, "dispositivo": "Scheda", "interfaccia": "Windows WASAPI", "latenza": None}) == "Scheda, WASAPI"


def test_ritrova_e_da_salvare(gb):
    elenco = schede_audio.uscite()
    # Lo stesso nome in tre interfacce: conta la coppia.
    assert schede_audio.ritrova({"dispositivo": ALTOPARLANTI, "interfaccia": "MME"}, elenco)["indice"] == 4
    assert schede_audio.ritrova({"dispositivo": ALTOPARLANTI, "interfaccia": "Windows WASAPI"}, elenco)["indice"] == 18
    assert schede_audio.ritrova({"dispositivo": ALTOPARLANTI, "interfaccia": "ASIO"}, elenco) is None
    assert schede_audio.ritrova({"dispositivo": "Cuffie USB", "interfaccia": "Windows WASAPI"}, elenco) is None
    assert schede_audio.ritrova({}, elenco) is None
    assert schede_audio.ritrova(None, elenco) is None
    # Si salvano i nomi, non l'indice, e la scelta salvata si ritrova.
    for uscita in elenco:
        scelta = schede_audio.da_salvare(uscita)
        assert scelta == {"dispositivo": uscita["dispositivo"], "interfaccia": uscita["interfaccia"]}
        assert schede_audio.ritrova(scelta, elenco) is uscita
    assert schede_audio.da_salvare(None) == {}
    # Un nome scritto a mano con l'a capo si ritrova lo stesso.
    assert schede_audio.ritrova({"dispositivo": "Cuffie\r\n(Bluetooth)", "interfaccia": "Windows DirectSound"}, elenco)["indice"] == 15


def test_dispositivo_di_mpv():
    trova = schede_audio.dispositivo_di_mpv
    assert trova(ALTOPARLANTI, ELENCO_MPV) == "wasapi/{a}"
    assert trova(DIGITALE, ELENCO_MPV) == "wasapi/{b}"
    # MME taglia a 31 caratteri: vale l'unica voce che comincia cosi'.
    assert trova(DIGITALE[:31], ELENCO_MPV) == "wasapi/{b}"
    assert trova(STEAM[:31], ELENCO_MPV) == "wasapi/{c}"
    assert trova(MICROFONO[:31], ELENCO_MPV) == "wasapi/{d}"
    # Piu' voci con lo stesso inizio di 31 caratteri: meglio la scheda di Windows.
    assert trova(STEAM[:31], [*ELENCO_MPV, {"name": "wasapi/{h}", "description": f"{STEAM} 2"}]) is None
    # Un nome piu' corto di 31 caratteri e' intero, non tagliato da MME:
    # anche se e' l'inizio di una voce sola, quella voce e' un'altra scheda.
    assert len(ALTOPARLANTI) == schede_audio.LUNGHEZZA_DEI_NOMI_MME
    assert trova(ALTOPARLANTI[:30], ELENCO_MPV) is None
    assert trova("Realtek Digital Output", ELENCO_MPV) is None
    assert trova("Altoparlanti", [{"name": "wasapi/{a}", "description": ALTOPARLANTI}]) is None
    assert trova("Altoparlanti (Steam", ELENCO_MPV) is None
    # ASIO ha nomi suoi; la voce openal con lo stesso nome non conta.
    assert trova("Realtek ASIO", ELENCO_MPV) is None
    assert trova("Microsoft Sound Mapper - Output", ELENCO_MPV) is None
    assert trova("Autoselect device", ELENCO_MPV) is None
    assert trova("", ELENCO_MPV) is None
    assert trova(None, ELENCO_MPV) is None
    assert trova(ALTOPARLANTI, None) is None
    # Il nome uguale vince su quello che comincia uguale.
    con_un_altro = [*ELENCO_MPV, {"name": "wasapi/{e}", "description": f"{ALTOPARLANTI} 2"}]
    assert trova(ALTOPARLANTI, con_un_altro) == "wasapi/{a}"
    # Due schede con lo stesso nome: non si tira a indovinare.
    assert trova(ALTOPARLANTI, [*ELENCO_MPV, {"name": "wasapi/{f}", "description": ALTOPARLANTI}]) is None
    # L'a capo si ripulisce anche dalla parte di mpv.
    assert trova("Cuffie (Bluetooth)", [{"name": "wasapi/{g}", "description": "Cuffie\r\n(Bluetooth)"}]) == "wasapi/{g}"


def test_automatica(gb):
    uscita = schede_audio.automatica()
    assert uscita["indice"] == 18 and uscita["dispositivo"] == ALTOPARLANTI and uscita["interfaccia"] == "Windows WASAPI"
    assert gb.chiamate == ["scegli", "elenco"]
    gb.scelta = (None, None)
    assert schede_audio.automatica() is None
    # Un indice che l'elenco non ha: resta buono per il mixer.
    gb.scelta = (99, "MME")
    assert schede_audio.automatica() == {"indice": 99, "dispositivo": "dispositivo 99", "interfaccia": "MME", "breve": "MME", "latenza": None, "esclusiva": False}


def test_in_uso(gb):
    # Il mixer non ha ancora scelto: sceglie alla prima apertura.
    assert schede_audio.in_uso() is None
    assert gb.chiamate == []
    gb.device = 19
    assert schede_audio.in_uso()["dispositivo"] == DIGITALE
    # Anche l'uscita che l'elenco della finestra non mostra.
    gb.device = 24
    assert schede_audio.in_uso()["breve"] == "WDM-KS"
    assert schede_audio.in_uso(schede_audio.uscite()) is None
    gb.device = 77
    assert schede_audio.in_uso() is None


def test_applica_la_scelta_ritrovata(gb):
    motore = _MotoreFinto(gb)
    esito = schede_audio.applica({"dispositivo": DIGITALE, "interfaccia": "Windows WASAPI"}, motore)
    # L'elenco di GBUtils prima di quello di mpv, o PortAudio perde ASIO.
    assert gb.chiamate == ["elenco", "elenco_mpv", ("setup", 19), ("mpv", "wasapi/{b}")]
    assert esito == {"uscita": _uscita(19), "dispositivo": DIGITALE, "interfaccia": "Windows WASAPI", "automatica": False, "mancante": False,
                     "musica": True, "mpv": "wasapi/{b}"}
    assert motore.dispositivo == "wasapi/{b}"
    # Un nome MME tagliato: la musica la ritrova sul prefisso.
    esito = schede_audio.applica({"dispositivo": STEAM[:31], "interfaccia": "MME"}, motore)
    assert esito["musica"] and esito["mpv"] == "wasapi/{c}" and esito["dispositivo"] == STEAM[:31]
    assert gb.chiamate[-2:] == [("setup", 6), ("mpv", "wasapi/{c}")]


def test_applica_una_scheda_che_mpv_non_ritrova(gb):
    motore = _MotoreFinto(gb, "wasapi/{a}")
    esito = schede_audio.applica({"dispositivo": "Realtek ASIO", "interfaccia": "ASIO"}, motore)
    # Gli effetti vanno su ASIO, la musica torna sulla scheda di Windows.
    assert gb.chiamate == ["elenco", "elenco_mpv", ("setup", 16), ("mpv", "auto")]
    assert esito["dispositivo"] == "Realtek ASIO" and esito["interfaccia"] == "ASIO"
    assert not esito["musica"] and not esito["automatica"] and not esito["mancante"] and esito["mpv"] == "auto"
    assert motore.dispositivo == "auto"


@pytest.mark.parametrize("avvio", [False, True])
def test_applica_una_scelta_che_non_c_e_piu(gb, avvio):
    motore = _MotoreFinto(gb, "wasapi/{b}")
    esito = schede_audio.applica({"dispositivo": "Cuffie USB", "interfaccia": "Windows WASAPI"}, motore, avvio=avvio)
    # Anche all'avvio: la scelta salvata manca, si passa all'automatica.
    assert gb.chiamate == ["elenco", "scegli", "elenco", ("setup", 18), ("mpv", "auto")]
    assert esito["mancante"] and esito["automatica"] and esito["musica"]
    assert esito["uscita"]["indice"] == 18 and esito["dispositivo"] == ALTOPARLANTI and esito["mpv"] == "auto"


def test_applica_l_automatica_durante_la_sessione(gb):
    motore = _MotoreFinto(gb, "wasapi/{b}")
    esito = schede_audio.applica({}, motore)
    assert gb.chiamate == ["scegli", "elenco", ("setup", 18), ("mpv", "auto")]
    assert esito == {"uscita": _uscita(18), "dispositivo": ALTOPARLANTI, "interfaccia": "Windows WASAPI", "automatica": True, "mancante": False,
                     "musica": True, "mpv": "auto"}
    # Se l'automatica non trova niente, il mixer non si tocca.
    gb.chiamate.clear()
    gb.scelta = (None, None)
    esito = schede_audio.applica(None, motore)
    assert gb.chiamate == ["scegli", ("mpv", "auto")]
    assert esito["uscita"] is None and esito["dispositivo"] is None and esito["automatica"] and esito["mpv"] == "auto"


def test_applica_l_automatica_all_avvio_non_tocca_niente(gb):
    motore = _MotoreFinto(gb)
    esito = schede_audio.applica({}, motore, avvio=True)
    # Niente prove di apertura all'avvio: il mixer sceglie da se'.
    assert gb.chiamate == []
    assert esito == {"uscita": None, "dispositivo": None, "interfaccia": None, "automatica": True, "mancante": False, "musica": True, "mpv": "auto"}


def test_motore_vero_dispositivo_e_dispositivi(gb):
    from motore import Motore

    # Con ao=null mpv non suona: il dispositivo si legge e si scrive senza
    # aprire nessuna scheda, e mpv accetta anche un nome che non esiste.
    motore = Motore(ao="null")
    try:
        assert motore.dispositivo == "auto"
        elenco = motore.dispositivi()
        assert elenco and all(isinstance(v, dict) and {"name", "description"} <= set(v) for v in elenco)
        assert "auto" in [v["name"] for v in elenco]
        motore.dispositivo = "wasapi/{prova}"
        assert motore.dispositivo == "wasapi/{prova}"
        # Tornando all'automatica la musica torna su auto.
        esito = schede_audio.applica({}, motore)
        assert esito["mpv"] == "auto" and motore.dispositivo == "auto"
    finally:
        motore.chiudi()
