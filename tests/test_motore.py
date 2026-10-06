# MeTeOra, le prove del motore: due lettori, velocita', tono, equalizzatore, dissolvenza e fine brano senza attese.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.55.0 (tappa 4, issue 15).

"""Le prove del motore vero, senza suoni.

Il motore suona sull'uscita nulla (ao=null), che va in tempo reale come una
scheda vera, oppure su un file (ao=pcm), che rende il brano tutto d'un
fiato: li' si misura il suono uscito con numpy. I brani sono WAV brevi
generati in tmp_path: rumore bianco per l'equalizzatore, seni per tono e
volume, silenzio per la dissolvenza, dove contano i volumi dei due lettori
nel tempo. Le dissolvenze durano da 300 a 500 ms.
"""

import os
import threading
import time
import wave

import numpy as np
import pytest

import motore as modulo
from motore import Motore

FREQUENZA = 44100


def _scrivi_wav(percorso, campioni, frequenza=FREQUENZA):
    with wave.open(str(percorso), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(frequenza)
        f.writeframes(np.clip(np.round(campioni * 32767), -32768, 32767).astype("<i2").tobytes())
    return str(percorso)


def _seno(percorso, secondi, hz=440, ampiezza=0.25, frequenza=FREQUENZA):
    t = np.arange(int(frequenza * secondi)) / frequenza
    return _scrivi_wav(percorso, ampiezza * np.sin(2 * np.pi * hz * t), frequenza)


def _rumore(percorso, secondi, seme=7):
    return _scrivi_wav(percorso, np.random.default_rng(seme).normal(0, 0.03, int(FREQUENZA * secondi)))


def _silenzio(percorso, secondi):
    return _scrivi_wav(percorso, np.zeros(int(FREQUENZA * secondi)))


def _aspetta(condizione, secondi=5):
    fine = time.perf_counter() + secondi
    while time.perf_counter() < fine:
        if condizione():
            return True
        time.sleep(0.005)
    return condizione()


class _Avvisi:
    """Gli avvisi del motore, con l'istante in cui arrivano, nel filo che li
    manda: come li vedrebbe la finestra, ma senza wx.CallAfter."""

    def __init__(self):
        self.righe = []
        self.fine = threading.Event()
        self.seguente = None

    def __call__(self, nome):
        def annota(*argomenti):
            self.righe.append((time.perf_counter(), nome, argomenti))
            if nome == "alla_fine":
                self.fine.set()
        return annota

    def nomi(self):
        return [nome for _, nome, _ in self.righe]

    def quando(self, nome):
        return next(t for t, n, _ in self.righe if n == nome)


@pytest.fixture
def avvisi():
    return _Avvisi()


@pytest.fixture
def crea(avvisi):
    """Crea motori che si chiudono da soli a fine prova. Con seguente, la
    risposta a chiedi_il_seguente e' prepara(seguente), data subito."""
    creati = []

    def nuovo(ao="null", seguente=None, **altri):
        m = None

        def chiedi():
            avvisi("chiedi_il_seguente")()
            if seguente:
                m.prepara(seguente)

        m = Motore(alla_fine=avvisi("alla_fine"), all_errore=avvisi("all_errore"), ao=ao, chiedi_il_seguente=chiedi,
            al_passaggio=avvisi("al_passaggio"), **altri)
        creati.append(m)
        return m

    yield nuovo
    for m in creati:
        m.chiudi()


def _su_file(tmp_path, nome="uscita.raw"):
    """Le opzioni per far rendere il motore su un file: float, mono, 44,1 kHz."""
    uscita = tmp_path / nome
    return uscita, {"ao_pcm_file": str(uscita), "ao_pcm_waveheader": False, "audio_format": "float", "audio_samplerate": FREQUENZA,
                    "audio_channels": "mono"}


def _uscito_alla_fine(m, uscita):
    """Il suono uscito sul file, a brano finito: il motore si chiude prima,
    perche' il file sia scritto tutto."""
    assert _aspetta(lambda: m.in_corso is None)
    m.chiudi()
    return np.fromfile(str(uscita), "<f4").astype(float)


def _livello(x, centro, ottave=1 / 3):
    """Il livello in dB di una fascia di frequenze attorno al centro."""
    potenza = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    frequenze = np.fft.rfftfreq(len(x), 1 / FREQUENZA)
    fascia = (frequenze >= centro * 2 ** (-ottave / 2)) & (frequenze <= centro * 2 ** (ottave / 2))
    return 10 * np.log10(potenza[fascia].mean())


def _rilievo(x):
    """Quanto la banda dei 1000 Hz sta sopra quella dei 150, in dB: zero sul
    rumore bianco con l'equalizzatore piatto."""
    return _livello(x, 1000) - _livello(x, 150)


def _frequenza_dominante(x):
    potenza = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    return np.fft.rfftfreq(len(x), 1 / FREQUENZA)[np.argmax(potenza)]


def _lettore_di(m, percorso):
    return next(lettore for lettore in m._lettori if lettore.percorso == percorso)


def _volumi(m):
    """I volumi che mpv ha davvero, letti dai due lettori."""
    return tuple(lettore.mpv.volume for lettore in m._lettori)


def _campiona(m, secondi):
    """Ogni 10 ms, per i secondi dati: l'istante, i volumi dei due lettori e
    se ciascuno ha un brano."""
    righe = []
    fine = time.perf_counter() + secondi
    while time.perf_counter() < fine:
        righe.append((time.perf_counter(), *_volumi(m), *(lettore.percorso is not None for lettore in m._lettori)))
        time.sleep(0.01)
    return righe


# La catena dei filtri e i limiti.

def test_catena_dei_filtri():
    # A zero: il preamplificatore a 0 dB e le bande a 0, niente limitatore.
    piatta = modulo.catena_dei_filtri([0] * 7)
    filtri = piatta[len("@eq:lavfi=["):-len("],scaletempo2")].split(",")
    assert filtri[0] == "volume@pre=volume=0dB:precision=double"
    assert filtri[1] == f"equalizer@b0=f=60:t=q:w={modulo.Q_DELLE_BANDE}:g=0:precision=f64"
    assert filtri[7] == f"equalizer@b6=f=12000:t=q:w={modulo.Q_DELLE_BANDE}:g=0:precision=f64"
    assert len(filtri) == 8 and "alimiter" not in piatta and "t=o" not in piatta
    catena = modulo.catena_dei_filtri([0, 1, -2, 3, 0, 12, -12])
    assert catena.startswith("@eq:lavfi=[") and catena.endswith("],scaletempo2")
    filtri = catena[len("@eq:lavfi=["):-len("],scaletempo2")].split(",")
    assert [f.split("=")[0] for f in filtri] == ["volume@pre"] + [f"equalizer@b{i}" for i in range(7)]
    # I guadagni dei filtri sono quelli compensati, e il preamplificatore
    # porta a 0 dB il punto piu' alto della curva.
    guadagni = modulo.guadagni_compensati([0, 1, -2, 3, 0, 12, -12])
    assert all(f"g={g:g}:" in filtri[i + 1] for i, g in enumerate(guadagni))
    assert filtri[0] == f"volume@pre=volume={modulo.preamplificazione(guadagni):g}dB:precision=double"
    # Oltre il volume 100: il guadagno in piu' e il limitatore, in fondo.
    oltre = modulo.catena_dei_filtri([0] * 7, 6.229)
    assert oltre.endswith(f",volume@oltre=volume=6.229dB:precision=double,{modulo.LIMITATORE}],scaletempo2")
    with pytest.raises(ValueError):
        modulo.catena_dei_filtri([0] * 6)


def test_bande_compensate_e_preamplificatore():
    centri = modulo.valori.FREQUENZE_DELLE_BANDE
    assert modulo.guadagni_compensati([0] * 7) == [0.0] * 7
    assert modulo.preamplificazione([0.0] * 7) == 0.0
    # Senza compenso tutte a +6 davano fino a +8,5 dB: compensate, ogni
    # centro vale quanto la banda scritta.
    assert modulo._curva(1000, [6] * 7) > 8.4
    for bande in ([6] * 7, [12] * 7, [12, -12, 12, -12, 12, -12, 12], [8, 4, 0, -3, 0, 4, 8], [0, 0, 0, 12, 0, 0, 0]):
        guadagni = modulo.guadagni_compensati(bande)
        assert all(abs(modulo._curva(c, guadagni) - b) < 0.01 for c, b in zip(centri, bande, strict=True)), bande
        # Il preamplificatore e' il punto piu' alto della curva, non la
        # banda piu' alzata: fra un centro e l'altro la curva sale appena.
        assert -max(bande) - 0.1 < modulo.preamplificazione(guadagni) <= -max(bande) + 0.01
    assert modulo.preamplificazione(modulo.guadagni_compensati([-6] * 7)) == 0.0


def test_guadagno_oltre_il_pieno():
    assert modulo.guadagno_oltre_il_pieno(0) == modulo.guadagno_oltre_il_pieno(100) == 0.0
    # La legge cubica di mpv: 127 e' 1,27 al cubo, +6,2 dB; 200 e' +18,1.
    assert abs(modulo.guadagno_oltre_il_pieno(127) - 6.228) < 0.001
    assert abs(modulo.guadagno_oltre_il_pieno(200) - 18.062) < 0.001


def test_valori_nei_limiti_e_su_tutti_e_due_i_lettori(crea):
    m = crea()
    assert (m.velocita, m.tono, m.bande, m.dissolvenza) == (1.0, 0, [0] * 7, 0.0)
    m.velocita = 3
    assert m.velocita == 2.0
    m.velocita = 0.1
    assert m.velocita == 0.5
    m.velocita = 1.25
    m.tono = 20
    assert m.tono == 12
    m.tono = -20
    assert m.tono == -12
    m.tono = 2
    m.imposta_banda(0, 50)
    m.imposta_banda(6, -50)
    m.imposta_banda(3, 4)
    assert m.bande == [12, 0, 0, 4, 0, 0, -12]
    with pytest.raises(IndexError):
        m.imposta_banda(7, 1)
    with pytest.raises(ValueError):
        m.bande = [1, 2]
    m.dissolvenza = 100
    assert m.dissolvenza == 15.0
    m.dissolvenza = 0.1
    assert m.dissolvenza == 0.5
    m.dissolvenza = 0
    assert m.dissolvenza == 0.0
    # Le proprieta' arrivano a mpv in modo asincrono, su tutti e due i lettori.
    attese = {"speed": 1.25, "pitch": 2 ** (2 / 12)}
    for lettore in m._lettori:
        assert _aspetta(lambda lettore=lettore: all(abs(getattr(lettore.mpv, nome) - valore) < 1e-6 for nome, valore in attese.items()))
    # Il preamplificatore sta nella catena, prima delle bande: il volume di
    # mpv non si tocca (1.102.2).
    assert m._catena().startswith(f"@eq:lavfi=[volume@pre=volume={modulo.preamplificazione(modulo.guadagni_compensati([12, 0, 0, 4, 0, 0, -12])):g}dB")
    assert all(lettore.mpv.volume_gain == 0 for lettore in m._lettori)
    m.bande = [0, 0, 0, -3, 0, 0, 0]
    assert m.bande == [0, 0, 0, -3, 0, 0, 0]
    # Una banda solo abbassata: compensata, le vicine salgono appena, e la
    # curva supera lo 0 di poco piu' di un decimo di dB fra un centro e
    # l'altro; il preamplificatore lo toglie.
    assert -0.2 < modulo.preamplificazione(modulo.guadagni_compensati(m.bande)) < 0


def test_volume_muto_e_scheda_li_ricorda_il_motore(crea):
    m = crea(volume=500)
    assert m.volume == 300
    m.volume = -4
    assert m.volume == 0
    m.volume = 95
    assert m.volume == 95
    assert not m.muto and not m.in_pausa
    m.muto = True
    assert m.muto
    assert _aspetta(lambda: all(lettore.mpv.mute for lettore in m._lettori))
    assert m.dispositivo == "auto"
    m.dispositivo = "wasapi/{prova}"
    assert m.dispositivo == "wasapi/{prova}"
    assert _aspetta(lambda: all(lettore.mpv.audio_device == "wasapi/{prova}" for lettore in m._lettori))
    assert any(voce["name"] == "auto" for voce in m.dispositivi())


# Velocita', tono, equalizzatore: il suono uscito, misurato.

def test_velocita_cambia_la_durata_e_non_il_tono(crea, tmp_path):
    seno = _seno(tmp_path / "seno.wav", 3)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", opzioni_mpv=opzioni)
    m.velocita = 1.5
    m.suona(seno)
    x = _uscito_alla_fine(m, uscita)
    assert abs(len(x) / FREQUENZA - 2.0) < 0.05
    assert abs(_frequenza_dominante(x) - 440) < 3


def test_tono_cambia_la_frequenza_e_non_la_durata(crea, tmp_path):
    seno = _seno(tmp_path / "seno.wav", 3)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", opzioni_mpv=opzioni)
    m.tono = 12
    m.suona(seno)
    x = _uscito_alla_fine(m, uscita)
    assert abs(len(x) / FREQUENZA - 3.0) < 0.05
    assert abs(_frequenza_dominante(x) - 880) < 5


def test_equalizzatore_piatto_non_cambia_il_rumore(crea, tmp_path):
    rumore = _rumore(tmp_path / "rumore.wav", 3)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", opzioni_mpv=opzioni)
    m.suona(rumore)
    x = _uscito_alla_fine(m, uscita)
    assert abs(_rilievo(x)) < 1.5
    assert not np.isnan(x).any()


def test_la_banda_alzata_resta_dopo_un_seek(crea, tmp_path):
    rumore = _rumore(tmp_path / "rumore.wav", 3)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", opzioni_mpv=opzioni)
    m.suona(rumore, in_pausa=True)
    assert _aspetta(lambda: m.durata is not None)
    # La banda alzata al volo, con af-command: il seek la perderebbe, se il
    # motore non riscrivesse la catena prima.
    m.imposta_banda(3, 12)
    m.vai_a(0.5)
    m.pausa(False)
    x = _uscito_alla_fine(m, uscita)
    # Si misurano gli ultimi due secondi, tutti dopo il seek: su ao=pcm a
    # volte esce anche il suono preparato prima del seek, che qui non conta.
    # Senza la catena riscritta prima del seek il rilievo sarebbe zero
    # (provato togliendo la riscrittura).
    assert len(x) >= 2.5 * FREQUENZA - 100
    assert _rilievo(x[-2 * FREQUENZA:]) > 8


def test_la_banda_alzata_resta_nel_brano_nuovo(crea, tmp_path):
    primo = _rumore(tmp_path / "primo.wav", 3, seme=1)
    secondo = _rumore(tmp_path / "secondo.wav", 3, seme=2)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", opzioni_mpv=opzioni)
    m.suona(primo, in_pausa=True)
    assert _aspetta(lambda: m.durata is not None)
    m.imposta_banda(3, 12)
    m.suona(secondo)
    x = _uscito_alla_fine(m, uscita)
    assert _rilievo(x[-2 * FREQUENZA:]) > 8


def test_la_banda_alzata_resta_quando_mpv_riapre_l_uscita(crea, tmp_path):
    # Cinque secondi: su ao=pcm la ricarica dell'uscita in pausa butta da se'
    # circa un secondo e mezzo dall'inizio del brano, con o senza il motore.
    rumore = _rumore(tmp_path / "rumore.wav", 5)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", opzioni_mpv=opzioni)
    m.suona(rumore, in_pausa=True)
    assert _aspetta(lambda: m.durata is not None)
    lettore = m._attivo
    # La banda alzata al volo, con af-command: la catena scritta non la ha.
    m.imposta_banda(3, 12)
    assert "g=12" not in lettore.af_scritto
    # mpv riapre l'uscita da se', come quando Windows cambia la scheda
    # predefinita: i filtri ripartono dalla catena scritta, e senza la
    # riscrittura all'evento AUDIO_RECONFIG il rilievo sarebbe zero (provato
    # togliendola), con il volume ancora abbassato di 12 dB.
    lettore.comando("ao-reload")
    # Su ao=pcm il brano esce tutto d'un fiato: prima di farlo suonare si
    # aspetta che mpv abbia la catena riscritta.
    _aspetta(lambda: "g=12" in str(lettore.mpv.af), 2)
    m.pausa(False)
    x = _uscito_alla_fine(m, uscita)
    assert m.bande[3] == 12
    assert len(x) >= 3 * FREQUENZA
    assert _rilievo(x[-2 * FREQUENZA:]) > 8


def test_il_volume_scende_quanto_la_banda_piu_alzata(crea, tmp_path):
    seno = _seno(tmp_path / "mille.wav", 2, hz=1000, ampiezza=0.5)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", volume=100, opzioni_mpv=opzioni)
    m.imposta_banda(3, 12)
    m.imposta_banda(0, -6)
    m.suona(seno)
    x = _uscito_alla_fine(m, uscita)
    # Senza preamplificatore il picco sarebbe 2: 0,5 alzato di 12 dB.
    assert abs(np.abs(x[FREQUENZA // 2:]).max() - 0.5) < 0.05


def test_tutte_le_bande_a_piu_sei_alzano_di_sei(crea, tmp_path):
    # Compensate, tutte a +6 danno +6 anche a 1000 Hz, dove senza compenso
    # erano +8,5; il preamplificatore toglie il punto piu' alto della curva,
    # 6,04 dB: il seno esce quasi uguale, invece che 2,4 dB piu' forte.
    seno = _seno(tmp_path / "mille.wav", 2, hz=1000, ampiezza=0.25)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", volume=100, opzioni_mpv=opzioni)
    m.bande = [6] * 7
    m.suona(seno)
    x = _uscito_alla_fine(m, uscita)
    attesa = 0.25 * 10 ** ((6 + modulo.preamplificazione(modulo.guadagni_compensati([6] * 7))) / 20)
    assert abs(np.abs(x[FREQUENZA // 2:]).max() - attesa) < 0.005


def test_il_ricampionamento_non_toglie_gli_acuti(crea, tmp_path):
    # Un seno a 19 kHz da 44,1 a 48 kHz: con il ricampionatore predefinito di
    # mpv usciva a -5,4 dB; con soxr resta pieno (1.102.2, issue 22).
    seno = _seno(tmp_path / "acuto.wav", 2, hz=19000, ampiezza=0.25)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", volume=100, opzioni_mpv={**opzioni, "audio_samplerate": 48000})
    m.suona(seno)
    x = _uscito_alla_fine(m, uscita)
    picco = np.abs(x[48000 // 2:-48000 // 4]).max()
    assert 20 * np.log10(picco / 0.25) > -0.5


def test_oltre_cento_amplifica_con_il_limitatore(crea, tmp_path):
    # Un seno piano oltre 100 cresce di tutto il guadagno: 160 e' 1,6 al cubo.
    piano = _seno(tmp_path / "piano.wav", 2, hz=1000, ampiezza=0.05)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", volume=160, opzioni_mpv=opzioni)
    m.suona(piano)
    x = _uscito_alla_fine(m, uscita)
    assert abs(np.abs(x[FREQUENZA // 2:]).max() - 0.05 * 1.6 ** 3) < 0.005
    # Uno forte non satura: il limitatore lo tiene sotto -1 dBFS, dove prima
    # sarebbe stato tosato a 1. A mpv va al massimo 100.
    forte = _seno(tmp_path / "forte.wav", 2, hz=1000, ampiezza=0.9)
    uscita, opzioni = _su_file(tmp_path, "forte.raw")
    m = crea(ao="pcm", volume=160, opzioni_mpv=opzioni)
    assert all(lettore.mpv.volume == 100 for lettore in m._lettori)
    m.suona(forte)
    assert _aspetta(lambda: "alimiter" in str(m._attivo.mpv.af))
    x = _uscito_alla_fine(m, uscita)
    assert np.abs(x[FREQUENZA // 2:]).max() < 0.9


def test_il_limitatore_entra_e_esce_passando_il_cento(crea, tmp_path):
    rumore = _rumore(tmp_path / "rumore.wav", 3)
    m = crea(volume=100)
    m.suona(rumore, in_pausa=True)
    assert _aspetta(lambda: m.durata is not None)
    lettore = m._attivo
    assert _aspetta(lambda: lettore.pronto)
    assert "alimiter" not in str(lettore.mpv.af)
    m.volume = 130
    oltre = f"volume@oltre=volume={modulo.guadagno_oltre_il_pieno(130):g}dB"
    assert _aspetta(lambda: "alimiter" in str(lettore.mpv.af) and oltre in str(lettore.mpv.af))
    assert _aspetta(lambda: lettore.mpv.volume == 100)
    # Oltre 100 al volo: la catena scritta resta, il comando va al filtro.
    m.volume = 150
    assert oltre in lettore.af_scritto
    assert m._catena().endswith(f"volume@oltre=volume={modulo.guadagno_oltre_il_pieno(150):g}dB:precision=double,{modulo.LIMITATORE}],scaletempo2")
    m.volume = 90
    assert _aspetta(lambda: "alimiter" not in str(lettore.mpv.af) and abs(lettore.mpv.volume - 90) < 1e-6)


def test_oltre_cento_il_volume_cambia_al_volo(crea, tmp_path):
    # Da 130 a 160 il guadagno in piu' arriva al filtro con af-command, senza
    # riscrivere la catena: il seno piano esce con il livello di 160.
    piano = _seno(tmp_path / "piano.wav", 2, hz=1000, ampiezza=0.05)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", volume=130, opzioni_mpv=opzioni)
    m.suona(piano, in_pausa=True)
    lettore = m._attivo
    assert _aspetta(lambda: lettore.pronto and "alimiter" in str(lettore.mpv.af))
    scritta = lettore.af_scritto
    risposte = []
    lettore.mpv.command_async("af-command", "eq", "volume", f"{modulo.guadagno_oltre_il_pieno(160):g}dB", "volume@oltre",
                              callback=lambda errore, _esito: risposte.append(errore))
    assert _aspetta(lambda: risposte) and risposte == [None]
    m.volume = 160
    time.sleep(0.2)
    assert lettore.af_scritto == scritta
    m.pausa(False)
    x = _uscito_alla_fine(m, uscita)
    assert abs(np.abs(x[FREQUENZA // 2:]).max() - 0.05 * 1.6 ** 3) < 0.005


# La fine del brano: niente attese.

def test_suona_dopo_la_fine_non_aspetta(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 1)
    secondo = _silenzio(tmp_path / "secondo.wav", 1)
    m = crea()
    m.suona(primo)
    assert avvisi.fine.wait(5)
    inizio = time.perf_counter()
    # Quello che la finestra fa a fine brano: il seguente, e le domande.
    m.suona(secondo)
    _ = (m.in_corso, m.in_pausa, m.posizione, m.durata, m.sottobrano)
    m.volume = 70
    assert time.perf_counter() - inizio < 0.03
    assert m.in_corso == secondo and not m.in_pausa
    assert _aspetta(lambda: (m.posizione or 0) > 0.1)
    assert avvisi.nomi() == ["alla_fine"]


def test_errore_e_fine_del_brano(crea, avvisi, tmp_path):
    m = crea()
    mancante = str(tmp_path / "non_ce.wav")
    m.suona(mancante)
    assert _aspetta(lambda: avvisi.nomi() == ["all_errore"])
    assert avvisi.righe[0][2] == (mancante,)
    assert m.in_corso is None
    breve = _silenzio(tmp_path / "breve.wav", 0.5)
    m.suona(breve)
    assert m.in_corso == breve and m.sottobrano is None and m.sottobrani is None
    assert _aspetta(lambda: m.durata is not None)
    assert abs(m.durata - 0.5) < 0.01
    assert avvisi.fine.wait(5)
    assert m.in_corso is None and m.posizione is None


def test_pausa_stop_e_seek(crea, tmp_path):
    brano = _silenzio(tmp_path / "brano.wav", 6)
    m = crea()
    m.suona(brano, inizio=2.0, in_pausa=True)
    assert m.in_pausa
    assert _aspetta(lambda: m.posizione is not None)
    assert abs(m.posizione - 2.0) < 0.01
    assert m.pausa() is False
    assert _aspetta(lambda: m.posizione > 2.2)
    m.vai_a(4.0)
    assert _aspetta(lambda: abs(m.posizione - 4.0) < 0.1)
    m.salta(-2)
    assert _aspetta(lambda: m.posizione < 3)
    assert m.pausa(True) is True
    m.stop()
    assert m.in_corso is None and m.posizione is None


# La dissolvenza.

def test_passaggio_automatico_con_la_sfumatura(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 2)
    secondo = _silenzio(tmp_path / "secondo.wav", 4)
    m = crea(seguente=secondo)
    m.dissolvenza = 0.4
    inizio = time.perf_counter()
    m.suona(primo)
    # Il seguente si chiede quando mancano 0,4 + 1,5 secondi: subito.
    assert _aspetta(lambda: "chiedi_il_seguente" in avvisi.nomi(), 1)
    assert _aspetta(lambda: "al_passaggio" in avvisi.nomi(), 3)
    righe = _campiona(m, 1.0)
    # Il passaggio comincia quando mancano 0,4 + 0,5 secondi alla fine.
    assert abs(avvisi.quando("al_passaggio") - inizio - 1.1) < 0.2
    assert next(argomenti for _, nome, argomenti in avvisi.righe if nome == "al_passaggio") == (secondo, None)
    assert m.in_corso == secondo
    primo_lettore = next(lettore for lettore in m._lettori if lettore.percorso != secondo)
    primo_lettore_indice = m._lettori.index(primo_lettore)
    # Durante la sfumatura chi esce ha ancora il suo brano.
    sfumatura = [r for r in righe if r[3 + primo_lettore_indice] and (1 < r[1] < 79 or 1 < r[2] < 79)]
    assert sfumatura, "nessun volume intermedio"
    durata = sfumatura[-1][0] - sfumatura[0][0]
    assert 0.25 < durata < 0.55
    for _, *volumi, _, _ in sfumatura:
        uscente = volumi[primo_lettore_indice] / 80
        entrante = volumi[1 - primo_lettore_indice] / 80
        # A potenza costante: le ampiezze (il cubo del volume) vanno come
        # coseno e seno. Le due letture non sono simultanee: margine largo.
        assert 0.75 < (uscente ** 3) ** 2 + (entrante ** 3) ** 2 < 1.25
    # Chi esce scende, chi entra sale.
    uscenti = [r[1 + primo_lettore_indice] for r in sfumatura]
    assert uscenti == sorted(uscenti, reverse=True)
    # Alla fine chi e' uscito e' fermo, prima del suo evento di fine.
    assert _volumi(m)[1 - primo_lettore_indice] == 80 and primo_lettore.percorso is None
    assert "alla_fine" not in avvisi.nomi() and "all_errore" not in avvisi.nomi()
    assert _aspetta(lambda: primo_lettore.mpv.idle_active)


def test_la_velocita_anticipa_il_passaggio(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 4)
    secondo = _silenzio(tmp_path / "secondo.wav", 4)
    m = crea(seguente=secondo)
    m.dissolvenza = 0.4
    m.velocita = 2
    inizio = time.perf_counter()
    m.suona(primo)
    assert _aspetta(lambda: "al_passaggio" in avvisi.nomi(), 4)
    # Quattro secondi a velocita' 2 sono due veri: il passaggio a 0,9 dalla fine.
    assert abs(avvisi.quando("al_passaggio") - inizio - 1.1) < 0.2


def test_cambio_coi_tasti_con_la_sfumatura_e_pausa(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 6)
    secondo = _silenzio(tmp_path / "secondo.wav", 6)
    m = crea()
    m.dissolvenza = 0.5
    m.suona(primo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    m.suona(secondo)
    assert m.in_corso == secondo
    vecchio, nuovo = _lettore_di(m, primo), _lettore_di(m, secondo)
    assert _aspetta(lambda: 20 < nuovo.mpv.volume < 70)
    m.pausa(True)
    assert _aspetta(lambda: vecchio.mpv.pause and nuovo.mpv.pause)
    time.sleep(0.1)
    fermi = _volumi(m)
    time.sleep(0.3)
    # In pausa la sfumatura non avanza.
    assert _volumi(m) == fermi
    m.pausa(False)
    assert _aspetta(lambda: vecchio.percorso is None, 2)
    assert _aspetta(lambda: nuovo.mpv.volume == 80)
    assert not nuovo.mpv.pause
    assert avvisi.nomi() == []


def test_stop_durante_la_sfumatura_ferma_tutto(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 6)
    secondo = _silenzio(tmp_path / "secondo.wav", 6)
    m = crea()
    m.dissolvenza = 0.5
    m.suona(primo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    m.suona(secondo)
    assert _aspetta(lambda: m._sfumatura is not None and m._sfumatura.durata is not None)
    m.stop()
    assert m.in_corso is None and m._sfumatura is None
    assert all(lettore.percorso is None for lettore in m._lettori)
    assert _aspetta(lambda: all(lettore.mpv.idle_active for lettore in m._lettori))
    time.sleep(0.2)
    assert avvisi.nomi() == []


def test_un_altro_cambio_ferma_il_piu_debole(crea, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 8)
    secondo = _silenzio(tmp_path / "secondo.wav", 8)
    terzo = _silenzio(tmp_path / "terzo.wav", 8)
    quarto = _silenzio(tmp_path / "quarto.wav", 8)
    m = crea()
    m.dissolvenza = 0.5
    m.suona(primo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    # Subito dopo l'inizio della sfumatura chi entra si sente appena: si
    # ferma lui, e il primo continua a scendere verso il terzo.
    m.suona(secondo)
    lettore_primo = _lettore_di(m, primo)
    assert _aspetta(lambda: m._sfumatura.durata is not None)
    m.suona(terzo)
    assert m.in_corso == terzo
    assert lettore_primo.percorso == primo and _lettore_di(m, terzo) is not lettore_primo
    assert _aspetta(lambda: lettore_primo.percorso is None, 2)
    # Oltre la meta' si sente di piu' chi entra: si ferma chi esce.
    lettore_terzo = _lettore_di(m, terzo)
    m.suona(quarto)
    assert _aspetta(lambda: m._sfumatura is not None and m._sfumatura.avanzamento() > 0.6)
    lettore_quarto = _lettore_di(m, quarto)
    m.suona(primo)
    assert _lettore_di(m, primo) is lettore_terzo and lettore_quarto.percorso == quarto
    assert m._sfumatura.ampiezza > 0.7
    assert _aspetta(lambda: lettore_quarto.percorso is None, 2)
    assert m.in_corso == primo


def test_brano_corto_dimezza_la_sfumatura(crea, avvisi, tmp_path):
    lungo = _silenzio(tmp_path / "lungo.wav", 6)
    corto = _silenzio(tmp_path / "corto.wav", 1.2)
    cortissimo = _silenzio(tmp_path / "cortissimo.wav", 0.7)
    m = crea()
    m.dissolvenza = 0.8
    m.suona(lungo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    m.suona(corto)
    sfumatura = m._sfumatura
    assert _aspetta(lambda: sfumatura.durata is not None)
    # Meta' del brano che entra: 0,6 secondi invece di 0,8.
    assert abs(sfumatura.durata - 0.6) < 0.01
    assert avvisi.fine.wait(3)
    # Finita la sfumatura il corto e' gia' vicino alla fine: il seguente si
    # chiede, ma qui nessuno risponde.
    assert avvisi.nomi() == ["chiedi_il_seguente", "alla_fine"]
    # Sotto il secondo conta anche la fine di chi entra, che mpv annuncia
    # mezzo secondo prima: 0,7 - 0,5 = 0,2 secondi, e la sfumatura finisce
    # prima di quell'annuncio.
    m.suona(lungo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    m.suona(cortissimo)
    sfumatura, lettore = m._sfumatura, _lettore_di(m, cortissimo)
    assert _aspetta(lambda: sfumatura.durata is not None)
    assert abs(sfumatura.durata - 0.2) < 0.03
    assert _aspetta(lambda: m._sfumatura is None)
    assert lettore.mpv.volume == 80


def test_ripartire_da_capo_non_sfuma(crea, tmp_path):
    brano = _silenzio(tmp_path / "brano.wav", 6)
    m = crea()
    m.dissolvenza = 0.5
    m.suona(brano)
    assert _aspetta(lambda: (m.posizione or 0) > 0.5)
    m.suona(brano)
    assert m._sfumatura is None and m._lettori[1].percorso is None
    assert _aspetta(lambda: m.posizione is not None and m.posizione < 0.3)


def test_da_capo_sul_brano_che_entra_non_lo_raddoppia(crea, avvisi, tmp_path):
    """X da capo sul brano che entra durante una sfumatura e' sempre un salto
    dentro il brano: chi esce si ferma e il brano riparte da capo a piena
    voce, su un lettore solo. Prima ripartiva sull'altro lettore e si
    sentiva due volte, sfasato; poi, finche' chi entra si sentiva meno di
    chi esce, continuava a sfumare."""
    primo = _silenzio(tmp_path / "primo.wav", 8)
    secondo = _silenzio(tmp_path / "secondo.wav", 8)
    m = crea()
    m.dissolvenza = 0.5

    def ripartito_da_solo(brano, lettore, fermo):
        assert m._sfumatura is None and m._uscente is None and m.in_corso == brano
        assert m._attivo is lettore and fermo.percorso is None
        assert [uno.percorso for uno in m._lettori].count(brano) == 1
        assert _aspetta(lambda: lettore.mpv.volume == 80)
        assert _aspetta(lambda: m.posizione is not None and m.posizione < 0.3)

    m.suona(primo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    # Oltre la meta', quando chi entra si sente gia' di piu'.
    m.suona(secondo)
    lettore_primo, lettore_secondo = _lettore_di(m, primo), _lettore_di(m, secondo)
    assert _aspetta(lambda: m._sfumatura is not None and m._sfumatura.avanzamento() > 0.6)
    m.suona(secondo)
    ripartito_da_solo(secondo, lettore_secondo, lettore_primo)
    # Appena entrato, quando chi entra si sente appena: e' un salto lo stesso.
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    m.suona(primo)
    lettore_primo = _lettore_di(m, primo)
    assert m._sfumatura is not None and m._sfumatura.avanzamento() < 0.5
    m.suona(primo)
    ripartito_da_solo(primo, lettore_primo, lettore_secondo)
    time.sleep(0.3)
    assert m._sfumatura is None and lettore_secondo.percorso is None
    assert avvisi.nomi() == []


def test_in_pausa_il_passaggio_aspetta_la_ripresa(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 4)
    secondo = _silenzio(tmp_path / "secondo.wav", 4)
    m = crea(seguente=secondo)
    m.dissolvenza = 1.0
    # Come la ripresa all'avvio: in pausa a 1,2 secondi dalla fine, gia'
    # dentro la soglia del passaggio (1 + 0,5). Il seguente si prepara, ma
    # finche' niente suona il brano non cambia.
    m.suona(primo, inizio=2.8, in_pausa=True)
    assert _aspetta(lambda: m._preparato is not None and m._preparato.pronto, 3)
    time.sleep(0.3)
    assert avvisi.nomi() == ["chiedi_il_seguente"]
    assert m.in_corso == primo and m._sfumatura is None and m.in_pausa
    # Alla ripresa il passaggio parte, con la sfumatura limitata a quanto
    # resta a chi esce: 1,2 - 0,5 secondi invece di uno.
    m.pausa(False)
    assert _aspetta(lambda: "al_passaggio" in avvisi.nomi(), 1)
    sfumatura = m._sfumatura
    assert sfumatura is not None and m.in_corso == secondo
    assert _aspetta(lambda: sfumatura.durata is not None, 1)
    assert 0.4 < sfumatura.durata < 0.75
    assert _aspetta(lambda: m._sfumatura is None, 2)
    assert _aspetta(lambda: _lettore_di(m, secondo).mpv.volume == 80 and not _lettore_di(m, secondo).mpv.pause)
    assert avvisi.nomi() == ["chiedi_il_seguente", "al_passaggio"]


def test_i_salti_in_pausa_vicino_alla_fine_restano_nel_brano(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 6)
    secondo = _silenzio(tmp_path / "secondo.wav", 6)
    m = crea(seguente=secondo)
    m.dissolvenza = 1.0
    m.suona(primo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.2)
    m.pausa(True)
    # In pausa, a 2 secondi dalla fine: il seguente si prepara.
    m.vai_a(4.0)
    assert _aspetta(lambda: m._preparato is not None and m._preparato.pronto, 3)
    # A 1 secondo dalla fine, dentro la soglia del passaggio: niente cambia.
    # (Su ao=null, in pausa, la posizione dopo un salto si legge prima
    # esatta e poi circa due decimi indietro: basta che stia oltre i 4,5.)
    m.vai_a(5.0)
    assert _aspetta(lambda: m.posizione is not None and m.posizione > 4.6)
    time.sleep(0.3)
    assert avvisi.nomi() == ["chiedi_il_seguente"]
    assert m.in_corso == primo and m._sfumatura is None
    # Il salto indietro resta nel brano su cui ci si muoveva, lontano dalla
    # fine, e il preparato resta pronto per quando ci si arrivera'.
    m.salta(-3)
    assert _aspetta(lambda: m.posizione is not None and m.posizione < 3.0)
    assert m.in_corso == primo and m._preparato is not None and m._preparato.percorso == secondo
    assert avvisi.nomi() == ["chiedi_il_seguente"]


def test_salto_oltre_la_fine_in_pausa_scarta_il_preparato(crea, avvisi, tmp_path):
    """Un salto oltre la fine fatto in pausa finisce il brano come senza la
    dissolvenza: arriva alla_fine, e la finestra sceglie il seguente da se'.
    Prima entrava il preparato, fermo in pausa, con al_passaggio."""
    primo = _silenzio(tmp_path / "primo.wav", 6)
    secondo = _silenzio(tmp_path / "secondo.wav", 6)
    m = crea(seguente=secondo)
    m.dissolvenza = 1.0
    m.suona(primo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.2)
    m.pausa(True)
    # In pausa, a 2 secondi dalla fine: il seguente si prepara.
    m.vai_a(4.0)
    assert _aspetta(lambda: m._preparato is not None and m._preparato.pronto, 3)
    preparato = m._preparato
    m.salta(10)
    assert avvisi.fine.wait(3)
    time.sleep(0.2)
    assert avvisi.nomi() == ["chiedi_il_seguente", "alla_fine"]
    assert m._preparato is None and preparato.percorso is None and m.in_corso is None
    assert all(lettore.percorso is None for lettore in m._lettori)
    assert _aspetta(lambda: preparato.mpv.idle_active)


def test_preparato_in_errore_passa_senza_sfumatura(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 2)
    mancante = str(tmp_path / "non_ce.wav")
    m = crea(seguente=mancante)
    m.dissolvenza = 0.4
    m.suona(primo)
    # L'errore del preparato non si dice: il brano finisce come senza la
    # dissolvenza, e l'errore arriva quando la finestra lo chiede di nuovo.
    assert avvisi.fine.wait(4)
    assert avvisi.nomi() == ["chiedi_il_seguente", "alla_fine"]
    m.suona(mancante)
    assert _aspetta(lambda: avvisi.nomi()[-1] == "all_errore")


def test_preparato_pronto_tardi_entra_alla_fine(crea, avvisi, tmp_path, monkeypatch):
    primo = _silenzio(tmp_path / "primo.wav", 1)
    secondo = _silenzio(tmp_path / "secondo.wav", 3)
    m = crea()
    m.dissolvenza = 0.4
    # Un preparato che il sorvegliante non vede mai pronto, come un SID che
    # tarda: alla fine del primo entra a piena voce, senza sfumatura.
    monkeypatch.setattr(m, "_da_leggere", lambda: [])
    m.suona(primo)
    assert _aspetta(lambda: m.posizione is not None)
    assert m.prepara(secondo) is True
    assert _aspetta(lambda: "al_passaggio" in avvisi.nomi(), 3)
    assert avvisi.nomi() == ["al_passaggio"]
    assert m.in_corso == secondo and m._sfumatura is None
    assert _aspetta(lambda: _lettore_di(m, secondo).mpv.volume == 80 and not _lettore_di(m, secondo).mpv.pause)
    assert _aspetta(lambda: (m.posizione or 0) > 0.2)


def test_prepara_solo_quando_serve(crea, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 4)
    secondo = _silenzio(tmp_path / "secondo.wav", 4)
    m = crea()
    assert m.prepara(secondo) is False
    m.suona(primo)
    assert _aspetta(lambda: m.posizione is not None)
    # Senza dissolvenza non si prepara niente.
    assert m.prepara(secondo) is False
    m.dissolvenza = 0.5
    assert m.prepara(secondo) is True
    altro = m._preparato
    assert altro is not m._lettori[0] and altro.percorso == secondo
    assert _aspetta(lambda: altro.pronto)
    assert altro.mpv.pause and altro.mpv.volume == 0
    # Lo stesso brano non si ricarica.
    assert m.prepara(secondo) is True and m._preparato is altro and altro.pronto


def test_spegnere_la_dissolvenza_scarta_il_preparato(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 3)
    secondo = _silenzio(tmp_path / "secondo.wav", 3)
    m = crea(seguente=secondo)
    m.dissolvenza = 0.5
    m.suona(primo)
    assert _aspetta(lambda: m._preparato is not None)
    m.dissolvenza = 0
    assert m._preparato is None and all(lettore.percorso != secondo for lettore in m._lettori)
    assert avvisi.fine.wait(4)
    assert "al_passaggio" not in avvisi.nomi()


def test_ricontrollo_al_passaggio_passa_al_giusto(avvisi, tmp_path):
    # Brani e dissolvenza lunghi, e lo stato fotografato nell'istante in cui
    # il giusto entra: sotto il carico della suite intera, con una
    # dissolvenza di mezzo secondo, il controllo arrivava a sfumatura finita.
    primo = _silenzio(tmp_path / "primo.wav", 4)
    preparato = _silenzio(tmp_path / "preparato.wav", 6)
    giusto = _silenzio(tmp_path / "giusto.wav", 6)
    m = None

    def al_passaggio(percorso, sottobrano):
        # Come la finestra quando la plancia e' cambiata dopo la preparazione:
        # il seguente ora e' un altro, e lo chiede subito.
        avvisi("al_passaggio")(percorso, sottobrano)
        m.suona(giusto)

    m = Motore(alla_fine=avvisi("alla_fine"), ao="null", chiedi_il_seguente=lambda: m.prepara(preparato), al_passaggio=al_passaggio)
    try:
        m.dissolvenza = 1.0
        m.suona(primo)
        visto = {}

        def entrato():
            sfumatura = m._sfumatura
            if m.in_corso != giusto or sfumatura is None:
                return False
            visto.update(uscente=sfumatura.uscente, ampiezza=sfumatura.ampiezza, percorsi=[lettore.percorso for lettore in m._lettori])
            return True

        assert _aspetta(entrato, 6)
        lettore_primo = _lettore_di(m, primo)
        # Il preparato, appena entrato e quasi muto, si ferma; il primo continua
        # a scendere, ora verso il giusto, e si ferma prima della sua fine.
        assert preparato not in visto["percorsi"]
        assert visto["uscente"] is lettore_primo and visto["ampiezza"] > 0.9
        assert _aspetta(lambda: lettore_primo.percorso is None, 3)
        assert _aspetta(lambda: _lettore_di(m, giusto).mpv.volume == 80)
        assert avvisi.nomi() == ["al_passaggio"]
    finally:
        m.chiudi()


def test_annullare_il_passaggio_lascia_finire_chi_esce(avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 3)
    preparato = _silenzio(tmp_path / "preparato.wav", 4)
    m = None
    esiti = []

    def al_passaggio(percorso, sottobrano):
        # Come la finestra quando, al ricontrollo, davanti non c'e' piu' niente.
        avvisi("al_passaggio")(percorso, sottobrano)
        esiti.append(m.annulla_il_passaggio())

    m = Motore(alla_fine=avvisi("alla_fine"), ao="null", chiedi_il_seguente=lambda: m.prepara(preparato), al_passaggio=al_passaggio)
    try:
        m.dissolvenza = 1.0
        inizio = time.perf_counter()
        m.suona(primo)
        # Il passaggio comincia a 1,5 secondi dalla fine; annullato, il primo
        # torna il brano in corso e arriva in fondo, e la fine si dice.
        posizioni = []
        while not avvisi.fine.is_set() and time.perf_counter() - inizio < 6:
            if m.in_corso == primo:
                posizioni.append(m.posizione or 0)
            time.sleep(0.01)
        assert avvisi.nomi() == ["al_passaggio", "alla_fine"] and esiti == [True]
        assert avvisi.quando("alla_fine") - avvisi.quando("al_passaggio") > 0.7
        assert max(posizioni) > 2.4
        assert m.in_corso is None and all(lettore.percorso is None for lettore in m._lettori)
        # Il seguente non si e' chiesto di nuovo (gli avvisi qui sopra), e il
        # preparato non c'e' piu'.
        assert m._sfumatura is None and m._preparato is None
        # Senza una sfumatura in corso si ferma tutto, e il motore lo dice.
        m.suona(primo)
        assert m.annulla_il_passaggio() is False
        assert m.in_corso is None and all(lettore.percorso is None for lettore in m._lettori)
    finally:
        m.chiudi()


class _Evento:
    """Un evento di fine brano finto, come lo manda python-mpv."""

    def __init__(self, voce, motivo=0):
        self.event_id = type("Id", (), {"value": modulo.mpv.MpvEventID.END_FILE})()
        self.data = type("Fine", (), {"reason": motivo, "playlist_entry_id": voce})()


def test_conta_solo_la_fine_del_brano_attivo(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 6)
    secondo = _silenzio(tmp_path / "secondo.wav", 6)
    m = crea()
    m.dissolvenza = 0.5
    m.suona(primo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    vecchio = m._attivo
    voce_vecchia = vecchio.voce
    m.suona(secondo)
    nuovo = m._attivo
    assert _aspetta(lambda: nuovo.voce is not None and m._sfumatura.durata is not None)
    # La fine di un brano gia' sostituito: non conta.
    m._evento(nuovo, _Evento(nuovo.voce - 1))
    # La fine di chi esce, arrivata prima del previsto: la sfumatura continua.
    m._evento(vecchio, _Evento(voce_vecchia))
    assert vecchio.finito and vecchio.percorso is None
    assert m._sfumatura is not None and m.in_corso == secondo
    assert _aspetta(lambda: m._sfumatura is None, 2)
    assert avvisi.nomi() == []
    # La fine del brano attivo, invece, si dice.
    m._evento(nuovo, _Evento(nuovo.voce))
    assert avvisi.nomi() == ["alla_fine"] and m.in_corso is None


def test_chiudi_chiude_tutti_e_due_i_lettori(avvisi, tmp_path):
    m = Motore(ao="null")
    brano = _silenzio(tmp_path / "brano.wav", 3)
    m.dissolvenza = 0.5
    m.suona(brano)
    assert _aspetta(lambda: m.posizione is not None)
    m.chiudi()
    assert all(lettore.mpv.handle is None for lettore in m._lettori)
    assert not m._sorvegliante.is_alive()
    m.chiudi()


# Stop, pausa, ripresa, X da capo e marker con la dissolvenza (1.58.0).


def test_pausa_e_ripresa_sfumando(crea, avvisi, tmp_path):
    brano = _silenzio(tmp_path / "brano.wav", 8)
    m = crea()
    m.dissolvenza = 0.4
    m.suona(brano)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    lettore = m._attivo
    # La pausa arriva dopo che la voce e' scesa; in_pausa lo dice subito.
    assert m.pausa(sfumando=True) is True and m.in_pausa
    assert not lettore.mpv.pause
    assert _aspetta(lambda: lettore.mpv.volume < 40, 1)
    assert _aspetta(lambda: lettore.mpv.pause, 2)
    # Fermo in pausa, la voce torna piena: la ripresa la fara' risalire.
    assert _aspetta(lambda: lettore.mpv.volume == 80, 1) and m._calo is None
    assert m.pausa(sfumando=True) is False and not m.in_pausa
    assert _aspetta(lambda: not lettore.mpv.pause, 1)
    assert lettore.mpv.volume < 40
    assert _aspetta(lambda: lettore.mpv.volume == 80, 2) and m._calo is None
    # Una ripresa durante la discesa risale dal punto in cui era arrivata.
    m.pausa(sfumando=True)
    assert _aspetta(lambda: 20 < lettore.mpv.volume < 70, 1)
    m.pausa(sfumando=True)
    assert _aspetta(lambda: lettore.mpv.volume == 80, 2)
    assert not lettore.mpv.pause and m.in_corso == brano
    assert avvisi.nomi() == []


def test_stop_sfumando_libera_subito_il_motore(crea, avvisi, tmp_path):
    primo = _silenzio(tmp_path / "primo.wav", 8)
    secondo = _silenzio(tmp_path / "secondo.wav", 8)
    m = crea()
    m.dissolvenza = 0.5
    m.suona(primo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    vecchio = m._attivo
    m.stop(sfumando=True)
    # Il motore e' libero subito, e il brano si spegne piano sull'altro lettore.
    assert m.in_corso is None and vecchio.percorso == primo
    assert _aspetta(lambda: vecchio.mpv.volume < 70, 1)
    # Un brano avviato intanto parte senza aspettare la coda.
    m.suona(secondo)
    assert m.in_corso == secondo and m._attivo is not vecchio and vecchio.percorso == primo
    assert _aspetta(lambda: vecchio.percorso is None, 2)
    assert _aspetta(lambda: m._attivo.mpv.volume == 80, 1) and m.in_corso == secondo
    assert avvisi.nomi() == []


def test_le_discese_arrivano_allo_zero_prima_di_fermarsi(crea, avvisi, tmp_path, monkeypatch):
    # Fino alla 1.58.1 la pausa, la coda dello stop e chi esce da una
    # sfumatura si fermavano con il volume dell'ultimo gradino, circa un
    # settimo della voce, e la fine era un taglio.
    primo = _silenzio(tmp_path / "primo.wav", 8)
    secondo = _silenzio(tmp_path / "secondo.wav", 8)
    fermati = []
    originali = modulo._Lettore.ferma, modulo._Lettore.imposta

    def ferma(self):
        if self.percorso is not None:
            fermati.append(("stop", self.volume_scritto))
        originali[0](self)

    def imposta(self, nome, valore):
        if nome == "pause" and valore is True:
            fermati.append(("pausa", self.volume_scritto))
        originali[1](self, nome, valore)

    monkeypatch.setattr(modulo._Lettore, "ferma", ferma)
    monkeypatch.setattr(modulo._Lettore, "imposta", imposta)
    m = crea()
    m.dissolvenza = 0.4
    m.suona(primo)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    m.pausa(sfumando=True)
    assert _aspetta(lambda: m._calo is None, 2)
    m.pausa(sfumando=True)
    assert _aspetta(lambda: m._calo is None, 2)
    m.suona(secondo)
    assert _aspetta(lambda: m._sfumatura is None and m.in_corso == secondo, 2)
    m.stop(sfumando=True)
    assert _aspetta(lambda: m._coda is None, 2)
    assert [nome for nome, _ in fermati] == ["pausa", "stop", "stop"]
    assert all(volume < 1 for _, volume in fermati), fermati
    assert avvisi.nomi() == []


def test_da_capo_e_marker_sfumano_con_lo_stesso_brano(crea, avvisi, tmp_path):
    brano = _silenzio(tmp_path / "brano.wav", 8)
    m = crea()
    m.dissolvenza = 0.4
    m.suona(brano)
    assert _aspetta(lambda: (m.posizione or 0) > 1.0)
    # X da capo, o un marker, con la dissolvenza: lo stesso brano su tutti e
    # due i lettori, dal punto di prima e dal punto chiesto, che si incrociano.
    m.suona(brano, inizio=3.0, sfuma_lo_stesso=True)
    assert m._sfumatura is not None
    assert [lettore.percorso for lettore in m._lettori] == [brano, brano]
    assert _aspetta(lambda: m._sfumatura is None, 2)
    assert [lettore.percorso for lettore in m._lettori].count(brano) == 1
    assert 3.0 <= m.posizione < 4.5 and m._attivo.mpv.volume == 80
    # Senza sfuma_lo_stesso resta un salto netto, su un lettore solo.
    m.suona(brano, sfuma_lo_stesso=False)
    assert m._sfumatura is None
    assert avvisi.nomi() == []


def test_senza_dissolvenza_stop_e_pausa_sono_netti(crea, tmp_path):
    brano = _silenzio(tmp_path / "brano.wav", 6)
    m = crea()
    m.suona(brano)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    lettore = m._attivo
    assert m.pausa(sfumando=True) and _aspetta(lambda: lettore.mpv.pause, 1)
    assert m._calo is None and lettore.mpv.volume == 80
    m.pausa(sfumando=True)
    m.stop(sfumando=True)
    assert m.in_corso is None and m._coda is None and lettore.percorso is None


def test_un_salto_durante_la_discesa_mette_subito_la_pausa(crea, tmp_path):
    brano = _silenzio(tmp_path / "brano.wav", 8)
    m = crea()
    m.dissolvenza = 0.5
    m.suona(brano)
    assert _aspetta(lambda: (m.posizione or 0) > 0.3)
    lettore = m._attivo
    m.pausa(sfumando=True)
    assert _aspetta(lambda: lettore.mpv.volume < 70, 1)
    m.vai_a(2.0)
    assert m._calo is None and m.in_pausa
    assert _aspetta(lambda: lettore.mpv.pause and lettore.mpv.volume == 80, 1)


TURBO_OUTRUN = r"E:\C64Music\MUSICIANS\T\Tel_Jeroen\Turbo_Outrun.sid"


@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_attesa_del_sid(crea, tmp_path):
    import shutil

    copia = tmp_path / "Turbo_Outrun.sid"
    shutil.copy(TURBO_OUTRUN, copia)
    m = crea()
    # Appena caricato, prima che mpv apra il flusso, l'attesa si stima.
    m.suona(str(copia), 1)
    assert m.attesa_del_sid(150) > 2
    assert _aspetta(lambda: (m.posizione or 0) > 0, 10)
    # Appena partito, la fine del brano non e' ancora resa; l'inizio si'.
    assert m.attesa_del_sid(170) > 2
    assert m.attesa_del_sid(0.5) == 0
    # Gli altri brani non aspettano mai.
    m.suona(_silenzio(tmp_path / "brano.wav", 8))
    assert _aspetta(lambda: (m.posizione or 0) > 0)
    assert m.attesa_del_sid(7) == 0

@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_due_flussi_sullo_stesso_sid_condividono_la_resa(tmp_path):
    import shutil

    copia = tmp_path / "Turbo_Outrun.sid"
    shutil.copy(TURBO_OUTRUN, copia)
    primo = modulo.sid.apri_flusso(str(copia), 1, 30.0)
    secondo = modulo.sid.apri_flusso(str(copia), 1, 30.0)
    altro = modulo.sid.apri_flusso(str(copia), 2, 30.0)
    try:
        assert primo.brano is secondo.brano and altro.brano is not primo.brano
        # La resa si ferma solo con l'ultimo flusso, e chiudere due volte non conta.
        primo.close()
        primo.close()
        assert not secondo.brano._fermo
        secondo.close()
        assert secondo.brano._fermo
    finally:
        altro.close()


@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_marker_sfumato_su_un_sid_senza_silenzio(crea, tmp_path):
    import shutil

    copia = tmp_path / "Turbo_Outrun.sid"
    shutil.copy(TURBO_OUTRUN, copia)
    m = crea()
    m.dissolvenza = 0.5
    m.suona(str(copia), 1)
    assert _aspetta(lambda: m._attivo.flusso is not None and m._attivo.flusso.brano.secondi_pronti() > 70, 15)
    # Lo stesso SID entra sull'altro lettore dal secondo 60: la resa c'e' gia'.
    m.suona(str(copia), 1, inizio=60, sfuma_lo_stesso=True)
    assert _aspetta(lambda: (m.posizione or 0) > 60, 1.5)


def _video_con_sottotitoli(cartella):
    """Un video di sei secondi con l'audio, fatto con la codifica di libmpv, e
    accanto il suo file di sottotitoli con due righe."""
    video = cartella / "film.mp4"
    finito = threading.Event()
    codifica = modulo.mpv.MPV(o=str(video), ovc="mpeg4", oac="aac", ao="null", vo="null", config=False)
    try:
        codifica.register_event_callback(lambda evento: finito.set() if evento.event_id.value == modulo.mpv.MpvEventID.END_FILE else None)
        codifica.play("av://lavfi:testsrc=duration=6:size=160x120:rate=25[out0];sine=frequency=440:duration=6[out1]")
        assert finito.wait(30)
    finally:
        codifica.terminate()
    (cartella / "film.srt").write_text("1\n00:00:01,000 --> 00:00:02,000\nPrima riga\n\n2\n00:00:02,500 --> 00:00:03,500\nSeconda riga\n\n", encoding="utf-8")
    return video


def test_tracce_e_sottotitoli_con_il_video_spento(avvisi, tmp_path):
    video = _video_con_sottotitoli(tmp_path)
    sottotitoli, caricati = [], []
    m = Motore(ao="null", ai_sottotitoli=sottotitoli.append, al_caricamento=lambda: caricati.append(True))
    try:
        assert m.tracce() is None
        m.suona(str(video))
        assert _aspetta(lambda: m.tracce() is not None) and caricati
        tracce = m.tracce()
        assert tracce["video"] is True and len(tracce["audio"]) == 1 and len(tracce["sub"]) == 1
        assert tracce["sub"][0].get("external") and m.indice_attivo() == 0
        # Il video e' spento, e i sottotitoli arrivano lo stesso, puntuali.
        assert _aspetta(lambda: sottotitoli == ["Prima riga"], 3)
        m.scegli_traccia("sid", "no")
        assert _aspetta(lambda: not any(t.get("selected") for t in m.tracce()["sub"]), 2)
        time.sleep(2)
        assert sottotitoli == ["Prima riga"]
        m.rapporto("4:3")
        # mpv lo rilegge come numero.
        assert _aspetta(lambda: abs(float(m._attivo.mpv.video_aspect_override) - 4 / 3) < 0.01, 2)
        m.imposta_il_video(None)
        assert _aspetta(lambda: m._attivo.mpv.vid is False, 2)
    finally:
        m.chiudi()


def test_due_sottotitoli_uguali_di_fila_si_dicono_due_volte(avvisi):
    # 1.82.0: sub-text non cambia, sub-start si'; dopo un salto niente doppioni.
    detti, immagini = [], []
    m = Motore(ao="null", ai_sottotitoli=detti.append, ai_sottotitoli_a_immagini=lambda: immagini.append(True))
    try:
        lettore = m._attivo
        m._sottotitolo(lettore, "sub-text", "Ritornello")
        m._sottotitolo_a_immagini(lettore, "sub-start", 3.0)
        m._sottotitolo_a_immagini(lettore, "sub-start", 5.0)
        assert detti == ["Ritornello", "Ritornello"] and len(immagini) == 2
        m._sottotitolo(lettore, "sub-text", None)
        m._sottotitolo_a_immagini(lettore, "sub-start", None)
        m._sottotitolo(lettore, "sub-text", "Ritornello")
        m._sottotitolo_a_immagini(lettore, "sub-start", 5.0)
        assert detti == ["Ritornello"] * 3
        # Un inizio senza testo, come nelle tracce a immagini, non dice niente.
        m._sottotitolo(lettore, "sub-text", "")
        m._sottotitolo_a_immagini(lettore, "sub-start", 9.0)
        m._sottotitolo_a_immagini(lettore, "sub-start", 11.0)
        assert len(detti) == 3
        # Un cartello ASS animato, un evento per fotogramma con lo stesso
        # testo, si dice una volta sola.
        m._sottotitolo(lettore, "sub-text", "Stazione di Tokyo")
        for fotogramma in range(72):
            m._sottotitolo_a_immagini(lettore, "sub-start", 20.0 + fotogramma / 24)
        assert detti.count("Stazione di Tokyo") == 1
        # Il lettore che non e' attivo non conta.
        m._sottotitolo(m._lettori[1], "sub-text", "Altro")
        assert "Altro" not in detti
    finally:
        m.chiudi()


def test_il_karaoke_di_un_lrc_accanto_al_brano(avvisi, tmp_path):
    import wave

    brano = tmp_path / "canzone.wav"
    with wave.open(str(brano), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\0\0" * 8000 * 6)
    (tmp_path / "canzone.lrc").write_text("[00:01.00]Prima riga\n[00:02.00]Ritornello\n[00:03.00]Ritornello\n", encoding="utf-8")
    detti, caricati = [], []
    m = Motore(ao="null", ai_sottotitoli=detti.append, al_caricamento=lambda: caricati.append(True))
    try:
        m.suona(str(brano))
        assert _aspetta(lambda: caricati, 5)
        # La traccia c'e', una volta sola: mpv non carica piu' il .lrc da se'.
        sottotitoli = m.tracce()["sub"]
        assert [t.get("title") for t in sottotitoli] == ["Testo del karaoke, dal file LRC"]
        m.scegli_traccia("sid", str(sottotitoli[0]["id"]))
        assert _aspetta(lambda: detti, 4)
        # Il tempo che resta alla riga, per la barra braille a blocchi.
        resto = m.resto_del_sottotitolo()
        assert resto is not None and 0 < resto <= 1.05
        assert _aspetta(lambda: detti == ["Prima riga", "Ritornello", "Ritornello"], 6)
        # L'anticipo rifa' la traccia, che resta scelta e sola, anche con due
        # cambi di fila.
        m.imposta_il_karaoke("strofa", 500)
        m.imposta_il_karaoke("riga", 300)
        assert _aspetta(lambda: [t.get("selected") for t in (m.tracce() or {"sub": []})["sub"]] == [True], 3)
        time.sleep(0.5)
        assert len(m.tracce()["sub"]) == 1
    finally:
        m.chiudi()


@pytest.mark.skipif(not os.path.isfile(TURBO_OUTRUN), reason="serve la collezione HVSC")
def test_il_karaoke_di_un_brano_reso_in_ram(avvisi, tmp_path):
    # Un SID si apre con il formato WAV imposto, che rifiutava la traccia del
    # testo: il banco del 4 ottobre 2026 sui .kar, resi da FluidSynth allo
    # stesso modo, l'ha trovato.
    import shutil

    copia = tmp_path / "Turbo_Outrun.sid"
    shutil.copy(TURBO_OUTRUN, copia)
    (tmp_path / "Turbo_Outrun.lrc").write_text("[00:00.50]Prima riga\n[00:01.50]Seconda riga\n", encoding="utf-8")
    detti, caricati = [], []
    m = Motore(ao="null", ai_sottotitoli=detti.append, al_caricamento=lambda: caricati.append(True))
    try:
        m.suona(str(copia), 1)
        assert _aspetta(lambda: caricati, 10)
        sottotitoli = m.tracce()["sub"]
        assert [t.get("title") for t in sottotitoli] == ["Testo del karaoke, dal file LRC"]
        m.scegli_traccia("sid", str(sottotitoli[0]["id"]))
        assert _aspetta(lambda: detti[:2] == ["Prima riga", "Seconda riga"], 6)
        assert (m.posizione or 0) > 1.4
    finally:
        m.chiudi()


def test_l_attenuazione_abbassa_senza_toccare_il_volume(crea, tmp_path):
    # 1.95.0: la sfumatura del timer di spegnimento. L'ampiezza 0.125 e' il
    # volume a meta', per la legge cubica di mpv; vale anche per un brano nuovo.
    primo = _seno(tmp_path / "primo.wav", 5)
    secondo = _seno(tmp_path / "secondo.wav", 5)
    m = crea(volume=80)
    m.suona(primo)
    m.attenuazione = 0.125
    assert m.volume == 80 and m.attenuazione == 0.125
    assert _aspetta(lambda: abs(m._attivo.mpv.volume - 40) < 0.5)
    m.volume = 60
    assert _aspetta(lambda: abs(m._attivo.mpv.volume - 30) < 0.5)
    m.suona(secondo)
    assert _aspetta(lambda: m._attivo.percorso == secondo and abs(m._attivo.mpv.volume - 30) < 0.5)
    m.attenuazione = 2
    assert m.attenuazione == 1.0
    assert _aspetta(lambda: abs(m._attivo.mpv.volume - 60) < 0.5)


def _con_il_replaygain(percorso):
    """I tag ReplayGain in un WAV, come ID3: -12 dB il brano, -6 l'album."""
    from mutagen.id3 import TXXX
    from mutagen.wave import WAVE

    wav = WAVE(str(percorso))
    wav.add_tags()
    wav.tags.add(TXXX(encoding=3, desc="REPLAYGAIN_TRACK_GAIN", text=["-12.00 dB"]))
    wav.tags.add(TXXX(encoding=3, desc="REPLAYGAIN_ALBUM_GAIN", text=["-6.00 dB"]))
    wav.save()
    return percorso


@pytest.mark.parametrize(("scelta", "picco"), [("spento", 0.25), ("brano", 0.25 * 10 ** (-12 / 20)), ("album", 0.25 * 10 ** (-6 / 20)), ("tutto", 0.25)])
def test_il_volume_uniforme_legge_i_tag(crea, tmp_path, scelta, picco):
    # 1.96.0: il ReplayGain dei tag, per brano o per album; una scelta che
    # non c'e' vale spento.
    seno = _con_il_replaygain(_seno(tmp_path / "seno.wav", 1))
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", volume=100, opzioni_mpv=opzioni)
    m.replaygain = scelta
    assert m.replaygain == (scelta if scelta in modulo.REPLAYGAIN_DI_MPV else "spento")
    m.suona(seno)
    x = _uscito_alla_fine(m, uscita)
    assert abs(np.abs(x).max() - picco) < 0.01


def test_a_volume_pieno_toglie_l_attenuazione(crea, tmp_path):
    # 1.96.11: il brano scelto mentre il timer sfuma entra pieno; con la
    # dissolvenza, chi esce parte dal punto in cui l'attenuazione l'aveva portato.
    primo = _seno(tmp_path / "primo.wav", 5)
    secondo = _seno(tmp_path / "secondo.wav", 5)
    m = crea(volume=80)
    m.suona(primo)
    m.attenuazione = 0.125
    m.suona(secondo, a_volume_pieno=True)
    assert m.attenuazione == 1.0
    assert _aspetta(lambda: m._attivo.percorso == secondo and abs(m._attivo.mpv.volume - 80) < 0.5)
    m.dissolvenza = 2
    assert _aspetta(lambda: m._attivo.pronto)
    m.attenuazione = 0.125
    m.suona(primo, a_volume_pieno=True)
    assert m.attenuazione == 1.0 and m._sfumatura is not None and m._sfumatura.ampiezza == pytest.approx(0.125)
