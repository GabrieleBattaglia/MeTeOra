# MeTeOra, le prove del motore: due lettori, velocita', tono, equalizzatore, dissolvenza e fine brano senza attese.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.55.0 (tappa 4, issue 15). Nella 1.113.4 le prove del filtro del tempo e del tono cambiato al volo aspettano che il motore abbia visto gli eventi di mpv, invece dei tempi (issue 27). Nella 1.116.0 alle_uscite e l'uscita che non si apre piu'. Nella 1.117.0 il lettore lontano e la conversione in FLAC. Nella 2.0.5 il calo, la sfumatura e la catena del volume oltre 100 aspettati per stato, non per tempo (issue 28). Nella 2.7.4 la sorgente a 24 bit che va allo speaker a 16. Nella 3.26.9 i flussi a pezzi con libmpv vera e un server in locale, il flusso rinnovato dopo la scadenza e il lettore lontano vero dentro il motore. Nella 3.26.14 i sottotitoli dei siti con lo speaker, anche a pezzi HLS, le tracce del PC una alla volta e il sottotitolo che sposta solo la riga vuota. Nella 3.26.24 i sottotitoli dopo il rinnovo, con il video, e l'uscita con lo speaker lasciato. Nella 3.26.25 la lettura interrotta, con un MP3 troncato.

"""Le prove del motore vero, senza suoni.

Il motore suona sull'uscita nulla (ao=null), che va in tempo reale come una
scheda vera, oppure su un file (ao=pcm), che rende il brano tutto d'un
fiato: li' si misura il suono uscito con numpy. I brani sono WAV brevi
generati in tmp_path: rumore bianco per l'equalizzatore, seni per tono e
volume, silenzio per la dissolvenza, dove contano i volumi dei due lettori
nel tempo. Le dissolvenze durano da 300 a 500 ms.
"""

import contextlib
import os
import threading
import time
import types
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


def _eventi_visti(lettore, secondi=60):
    """Aspetta che il motore abbia visto tutti gli eventi che mpv ha gia'
    mandato al lettore: la risposta a un comando che non cambia niente arriva
    nello stesso filo degli eventi, dietro di loro (issue 27). Di solito in
    pochi millesimi; ma al primo brano del processo la prima ricerca del
    karaoke tiene quel filo, e con altri fili Python occupati anche per
    decine di secondi: per questo il limite e' largo."""
    risposte = []
    lettore.mpv.command_async("expand-text", "", callback=lambda errore, _esito: risposte.append(errore))
    assert _aspetta(lambda: risposte, secondi), f"mpv non ha risposto all'expand-text entro {secondi} secondi"
    assert risposte == [None]


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
    # Con velocita' o tono cambiati, in fondo rubberband con il tono suo.
    assert modulo.catena_dei_filtri([0] * 7, tono=1).endswith("],@tempo:rubberband=formant=shifted:pitch-scale=1.05946309436")
    assert modulo.catena_dei_filtri([0] * 7, tono=0).endswith("],@tempo:rubberband=formant=shifted:pitch-scale=1")
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
    for lettore in m._lettori:
        assert _aspetta(lambda lettore=lettore: abs(lettore.mpv.speed - 1.25) < 1e-6)
    # Il tono lo fa rubberband, nella catena: la proprieta' pitch di mpv
    # resta 1 (1.102.3).
    assert all(lettore.mpv.pitch == 1 for lettore in m._lettori)
    assert m._catena().endswith(f"],@tempo:rubberband=formant=shifted:pitch-scale={2 ** (2 / 12):.12g}")
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
    # rubberband aggiunge circa 40 ms di attacco e 50 di silenzio in fondo.
    assert 2.0 <= len(x) / FREQUENZA < 2.15
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


def test_il_filtro_del_tempo_cambia_lasciando_il_normale(crea, tmp_path):
    rumore = _rumore(tmp_path / "rumore.wav", 3)
    m = crea()
    m.suona(rumore, in_pausa=True)
    lettore = m._attivo
    # L'apertura finisce dopo FILE_LOADED, quando mpv apre l'uscita e manda
    # l'ultimo AUDIO_RECONFIG.
    assert _aspetta(lambda: lettore.pronto and lettore.mpv.current_ao)
    assert "scaletempo2" in str(lettore.mpv.af) and "rubberband" not in str(lettore.mpv.af)
    m.velocita = 1.05
    assert _aspetta(lambda: "rubberband" in str(lettore.mpv.af) and "scaletempo2" not in str(lettore.mpv.af))
    # Fra due velocita' diverse dal normale la catena non si riscrive. Prima
    # il motore deve aver visto gli AUDIO_RECONFIG dell'apertura e della
    # riscrittura: arrivati dopo il tono cambiato al volo, la riscriverebbero,
    # come deve. Al primo brano del processo arrivavano tardi, perche' dopo
    # FILE_LOADED la prima ricerca del karaoke tiene il filo degli eventi per
    # circa 30 ms, e la prova da sola cadeva sempre (issue 27).
    _eventi_visti(lettore)
    scritta = lettore.af_scritto
    m.velocita = 1.1
    m.tono = 3
    # La risposta all'af-command del tono arriva al motore prima di quella di
    # _eventi_visti: se fosse un errore, la catena sarebbe gia' riscritta.
    _eventi_visti(lettore)
    assert lettore.af_scritto == scritta
    m.tono = 0
    m.velocita = 1.0
    assert _aspetta(lambda: "scaletempo2" in str(lettore.mpv.af) and "rubberband" not in str(lettore.mpv.af))
    m.tono = -2
    # mpv elenca i parametri di rubberband come dizionario, non come testo.
    assert _aspetta(lambda: f"{2 ** (-2 / 12):.12g}" in str(lettore.mpv.af))
    m.tono = 0
    assert _aspetta(lambda: "scaletempo2" in str(lettore.mpv.af) and "rubberband" not in str(lettore.mpv.af))


def test_il_tono_lo_fa_rubberband(crea, tmp_path):
    # Un'ottava su: il seno a 440 esce a 880, lungo uguale, e la proprieta'
    # pitch di mpv resta 1.
    seno = _seno(tmp_path / "la.wav", 2)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", opzioni_mpv=opzioni)
    m.tono = 12
    m.suona(seno)
    x = _uscito_alla_fine(m, uscita)
    assert abs(_frequenza_dominante(x[FREQUENZA // 2:-FREQUENZA // 2]) - 880) < 3
    assert abs(len(x) / FREQUENZA - 2) < 0.2


def test_velocita_bassa_e_tono_alto(crea, tmp_path):
    # Meta' velocita' e un'ottava su: tempo 0,25 per chi fa il tono con il
    # ricampionamento; rubberband li tiene separati. Due secondi ne durano
    # quattro, e il la suona a 880.
    seno = _seno(tmp_path / "la.wav", 2)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", opzioni_mpv=opzioni)
    m.velocita = 0.5
    m.tono = 12
    m.suona(seno)
    x = _uscito_alla_fine(m, uscita)
    assert abs(len(x) / FREQUENZA - 4) < 0.3
    assert abs(_frequenza_dominante(x[FREQUENZA // 2:-FREQUENZA // 2]) - 880) < 3


def test_il_tono_cambia_al_volo(crea, tmp_path):
    # Da +1 a +12 il tono arriva a rubberband con af-command, senza
    # riscrivere la catena: il la esce a 880. Il suono gia' filtrato in pausa
    # resta a +1: su ao=pcm circa un secondo e mezzo, sulla scheda il buffer
    # d'uscita; si guardano gli ultimi due secondi.
    seno = _seno(tmp_path / "la.wav", 6)
    uscita, opzioni = _su_file(tmp_path)
    m = crea(ao="pcm", opzioni_mpv=opzioni)
    m.tono = 1
    m.suona(seno, in_pausa=True)
    lettore = m._attivo
    # Appena aperto il brano mpv riapre l'uscita ancora un paio di volte, e a
    # ogni riapertura il motore riscrive la catena se e' cambiata al volo:
    # prima del tono nuovo il motore deve aver visto quegli AUDIO_RECONFIG,
    # che con il processo occupato arrivavano dopo i 300 ms che la prova
    # aspettava (issue 27). Anche sul file, a uscita aperta, mpv li ha gia'
    # mandati tutti.
    assert _aspetta(lambda: lettore.pronto and "rubberband" in str(lettore.mpv.af) and lettore.mpv.current_ao)
    _eventi_visti(lettore)
    scritta = lettore.af_scritto
    m.tono = 12
    # La risposta all'af-command arriva prima di quella di _eventi_visti.
    _eventi_visti(lettore)
    assert lettore.af_scritto == scritta
    m.pausa(False)
    x = _uscito_alla_fine(m, uscita)
    assert abs(_frequenza_dominante(x[-3 * FREQUENZA:-FREQUENZA // 2]) - 880) < 3


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
    # Dopo gli eventi che mpv ha gia' mandato, non dopo un tempo fisso (issue 28).
    _eventi_visti(lettore)
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


def test_alle_uscite_solo_quando_l_elenco_cambia(crea, avvisi):
    m = crea(alle_uscite=avvisi("alle_uscite"))
    # La prima lettura di mpv arriva appena ci si iscrive, e non e' un cambio.
    assert _aspetta(lambda: m._uscite_viste is not None)
    assert "alle_uscite" not in avvisi.nomi()
    vere = m.dispositivi()
    m._uscite_cambiate("audio-device-list", vere)
    assert "alle_uscite" not in avvisi.nomi()
    m._uscite_cambiate("audio-device-list", [*vere, {"name": "wasapi/{cuffie}", "description": "Cuffie (WH-1000XM4)"}])
    assert avvisi.nomi().count("alle_uscite") == 1
    m._uscite_cambiate("audio-device-list", vere)
    assert avvisi.nomi().count("alle_uscite") == 2
    # Senza alle_uscite il motore non si iscrive.
    assert crea()._uscite_viste is None


@pytest.mark.parametrize("persa", [True, False])
def test_l_uscita_che_non_si_apre(crea, avvisi, tmp_path, persa):
    # Un'uscita WASAPI che non esiste: mpv non apre niente, quindi non si
    # sente niente, e chiude il brano con l'errore dell'uscita, come quando
    # si spengono le cuffie scelte per nome.
    altri = {"all_uscita_persa": avvisi("all_uscita_persa")} if persa else {}
    m = crea(ao="wasapi", **altri)
    m.dispositivo = "wasapi/{00000000-0000-0000-0000-000000000000}"
    brano = _silenzio(tmp_path / "brano.wav", 3)
    m.suona(brano)
    # Senza all_uscita_persa e' un errore come gli altri.
    atteso = "all_uscita_persa" if persa else "all_errore"
    assert _aspetta(lambda: avvisi.nomi() == [atteso])
    assert avvisi.righe[0][2] == ((brano, None) if persa else (brano,))
    assert m.in_corso is None


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
    # La sfumatura si toglie un attimo prima che la voce torni piena: si
    # aspettano tutte e due le cose (issue 28).
    assert _aspetta(lambda: m._sfumatura is None and lettore.mpv.volume == 80)


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
        self.data = type("Fine", (), {"reason": motivo, "error": 0, "playlist_entry_id": voce})()


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
    # Fermo in pausa, la voce torna piena: la ripresa la fara' risalire. Il
    # calo si chiude anche un passo dopo che la voce e' tornata a 80: si
    # aspettano tutte e due le cose (issue 28).
    assert _aspetta(lambda: lettore.mpv.volume == 80 and m._calo is None, 1)
    assert m.pausa(sfumando=True) is False and not m.in_pausa
    assert _aspetta(lambda: not lettore.mpv.pause, 1)
    assert lettore.mpv.volume < 40
    assert _aspetta(lambda: lettore.mpv.volume == 80 and m._calo is None, 2)
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
        # L'avviso del caricamento puo' arrivare un attimo dopo le tracce.
        assert _aspetta(lambda: m.tracce() is not None and caricati)
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


def test_il_sottotitolo_che_sposta_solo_la_riga_vuota_non_si_ridice(avvisi):
    # Gabriele, 15 novembre 2026: il cue di 10 millesimi di YouTube dopo una
    # pausa ha le stesse righe di quello prima, con la riga vuota spostata:
    # libmpv lo coglie qualche volta, e la finestra lo ridiceva come un
    # ritornello. Sono i testi veri di libmpv sul video di Superquark.
    detti = []
    m = Motore(ao="null", ai_sottotitoli=detti.append)
    try:
        lettore = m._attivo
        m._sottotitolo(lettore, "sub-text", " \nassai Ma tanto tanto bene")
        m._sottotitolo_a_immagini(lettore, "sub-start", 131.08)
        m._sottotitolo(lettore, "sub-text", "assai Ma tanto tanto bene\n")
        m._sottotitolo_a_immagini(lettore, "sub-start", 136.93)
        m._sottotitolo(lettore, "sub-text", "assai Ma tanto tanto bene\n[Musica]")
        m._sottotitolo_a_immagini(lettore, "sub-start", 136.94)
        assert detti == [" \nassai Ma tanto tanto bene", "assai Ma tanto tanto bene\n[Musica]"]
        # Il cue che lascia solo la riga di sotto e' un sottotitolo che scorre: arriva, e lo filtra la finestra.
        m._sottotitolo(lettore, "sub-text", "[Musica]\n")
        assert detti[-1] == "[Musica]\n"
        # Dopo un salto il sottotitolo si dice anche con le righe di prima.
        m._sottotitolo(lettore, "sub-text", "Caruso\n")
        m.vai_a(18.0)
        m._sottotitolo(lettore, "sub-text", " \nCaruso")
        assert detti[-1] == " \nCaruso"
        # Lo stesso nel lettore ombra dello speaker.
        ombra = types.SimpleNamespace(_testo=None, _nuovo=False, numero=1, _al_testo=lambda _numero, testo: detti.append(testo))
        detti.clear()
        for testo in (" \nfeci ma veramente", "feci ma veramente\n", "feci ma veramente\ncosì e poi"):
            modulo._Ombra._sottotitolo(ombra, "sub-text", testo)
        assert detti == [" \nfeci ma veramente", "feci ma veramente\ncosì e poi"]
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


class _LontanoFinto:
    """Il lettore lontano come lo vede il motore: annota i comandi."""

    def __init__(self):
        self.chiamate = []
        self.percorso = self.sottobrano = self.sottobrani = None
        self.in_pausa = False
        self.posizione = 42.0
        self.durata = 180.0

    def suona(self, percorso, sottobrano=None, sottobrani=None, inizio=None, in_pausa=False, midi_reso=False):
        self.chiamate.append(("suona", percorso, sottobrano, inizio, in_pausa, midi_reso))
        self.percorso, self.sottobrano, self.sottobrani, self.in_pausa = percorso, sottobrano, sottobrani, in_pausa

    def pausa(self, valore=None):
        self.in_pausa = (not self.in_pausa) if valore is None else valore
        self.chiamate.append(("pausa", valore))
        return self.in_pausa

    def stop(self):
        self.chiamate.append(("stop",))
        self.percorso = None

    def salta(self, secondi):
        self.chiamate.append(("salta", secondi))

    def vai_a(self, secondi):
        self.chiamate.append(("vai_a", secondi))

    def chiudi(self, attendi=True):
        self.chiamate.append(("chiudi", attendi))

    @property
    def posizione_attesa(self):
        # Quella che il motore da' alla finestra (15 novembre 2026): qui la stessa.
        return self.posizione

    def aspetta_i_comandi(self, attesa=5.0):
        return True


def test_il_lettore_lontano(crea, avvisi, tmp_path):
    m = crea(al_salto=avvisi("al_salto"))
    lontano = _LontanoFinto()
    m.usa_il_lontano(lontano)
    assert m.lontano is lontano and m.in_corso is None
    brano = _silenzio(tmp_path / "brano.wav", 2)
    m.suona(brano, inizio=10.0, in_pausa=True)
    # Il brano va al lettore lontano, e i lettori del PC restano fermi.
    assert lontano.chiamate == [("suona", brano, None, 10.0, True, False)]
    assert m.in_corso == brano and m.in_pausa and m.posizione == 42.0 and m.durata == 180.0
    assert m._lettori[0].percorso is None and m._lettori[1].percorso is None
    assert m.pausa() is False and lontano.chiamate[-1] == ("pausa", None)
    m.salta(-10)
    m.vai_a(30)
    assert lontano.chiamate[-2:] == [("salta", -10), ("vai_a", 30)]
    # Niente dissolvenza, tracce, capitoli e attese dei SID con lo speaker.
    assert m.prepara(brano) is False and m.capitoli() == [] and m.attesa_del_sid(60) == 0.0
    assert m.tracce() == {"video": False, "audio": [], "sub": []}
    m.stop()
    assert lontano.chiamate[-1] == ("stop",) and m.in_corso is None and m.tracce() is None
    # Lo stop di usa_il_lontano, suona, i due salti e lo stop.
    assert avvisi.nomi().count("al_salto") == 5
    # Tornando al PC il lettore lontano si chiude.
    m.usa_il_lontano(None)
    assert lontano.chiamate[-1] == ("chiudi", False) and m.lontano is None


def test_il_karaoke_con_lo_speaker(crea, avvisi, tmp_path):
    # Gabriele, 3.17.0: con lo speaker il brano non suona in libmpv, e il
    # testo del karaoke si dice seguendo la posizione che lo speaker riferisce.
    brano = _silenzio(tmp_path / "canzone.wav", 1)
    (tmp_path / "canzone.lrc").write_text("[00:01.00]Prima riga\n[00:03.00]Seconda riga\n[00:05.00]Terza riga\n", encoding="utf-8")
    detti = []
    m = crea(ai_sottotitoli=detti.append, al_caricamento=avvisi("al_caricamento"))
    lontano = _LontanoFinto()
    lontano.posizione = 0.0
    m.usa_il_lontano(lontano)
    m.imposta_il_karaoke("riga", 0)
    m.suona(brano)
    # Il testo arriva in disparte come una traccia da scegliere, e la finestra rilegge le tracce.
    assert _aspetta(lambda: m.tracce()["sub"])
    assert m.tracce()["sub"] == [{"id": 1, "type": "sub", "title": "Testo del karaoke, dal file LRC", "selected": False, "external": True, "image": False,
        "codec": "subrip"}]
    assert _aspetta(lambda: "al_caricamento" in avvisi.nomi())
    # Non scelto tace.
    lontano.posizione = 1.5
    time.sleep(0.3)
    assert detti == [] and m.resto_del_sottotitolo() is None
    # Scelto, dice subito la riga in corso, poi le seguenti quando cominciano.
    m.scegli_traccia("sid", "1")
    assert _aspetta(lambda: detti == ["Prima riga"]) and m.tracce()["sub"][0]["selected"]
    assert m.resto_del_sottotitolo() == pytest.approx(1.5)
    lontano.posizione = 3.2
    assert _aspetta(lambda: detti == ["Prima riga", "Seconda riga"])
    # Un salto indietro ridice la riga in corso.
    lontano.posizione = 1.2
    assert _aspetta(lambda: detti == ["Prima riga", "Seconda riga", "Prima riga"])
    # Spento tace; l'anticipo nuovo vale subito.
    m.scegli_traccia("sid", "no")
    lontano.posizione = 5.5
    time.sleep(0.3)
    assert len(detti) == 3
    m.scegli_traccia("sid", "1")
    m.imposta_il_karaoke("riga", 1000)
    assert _aspetta(lambda: detti[-1] == "Terza riga") and m.resto_del_sottotitolo() == pytest.approx(8.5)
    # Lo stop ferma il filo, e un brano senza testo non ha tracce.
    m.stop()
    assert m.tracce() is None
    m.suona(_silenzio(tmp_path / "senza.wav", 1))
    time.sleep(0.3)
    assert m.tracce() == {"video": False, "audio": [], "sub": []}
    m.usa_il_lontano(None)


def test_i_sottotitoli_dei_video_con_lo_speaker(crea, avvisi, tmp_path):
    # Gabriele, 3.19.0: con lo speaker il video suona solo lassu'; il lettore
    # ombra, muto, apre lo stesso video, ne segue il punto e legge i sottotitoli.
    # Il video e' un WAV con il nome di un MKV: libmpv lo apre dal contenuto.
    film = _silenzio(tmp_path / "film.mkv", 12)
    (tmp_path / "film.srt").write_text("1\n00:00:01,000 --> 00:00:02,500\nPrima\n\n2\n00:00:05,000 --> 00:00:06,500\nSeconda\n", encoding="utf-8")
    detti = []
    m = crea(ai_sottotitoli=detti.append, al_caricamento=avvisi("al_caricamento"))
    lontano = _LontanoFinto()
    lontano.posizione = 0.0
    m.usa_il_lontano(lontano)
    m.suona(film)
    # Le tracce sono quelle dell'ombra, e la finestra rilegge le tracce quando l'ombra ha aperto il video.
    assert _aspetta(lambda: (m.tracce() or {}).get("sub"))
    assert _aspetta(lambda: "al_caricamento" in avvisi.nomi())
    sub = m.tracce()["sub"]
    assert len(sub) == 1 and sub[0].get("external")
    m.scegli_traccia("sid", str(sub[0]["id"]))
    # Lo speaker al secondo 1.2: l'ombra salta li', e il sottotitolo arriva.
    lontano.posizione = 1.2
    assert _aspetta(lambda: "Prima" in detti)
    lontano.posizione = 5.2
    assert _aspetta(lambda: "Seconda" in detti)
    assert m.resto_del_sottotitolo() is not None
    # Spenti, tacciono anche tornando al primo.
    m.scegli_traccia("sid", "no")
    quanti = len(detti)
    lontano.posizione = 1.2
    time.sleep(1.0)
    assert len(detti) == quanti
    # Lo stop ferma l'ombra; un brano che non e' un video non la usa.
    m.stop()
    assert m.tracce() is None and _aspetta(lambda: m._ombra.numero is None)
    m.usa_il_lontano(None)


# Un WebVTT che scorre come quelli automatici di YouTube, con il cue di 10
# millesimi fra due sottotitoli e una pausa.
WEBVTT_CHE_SCORRE = ("WEBVTT\n\n00:00:01.000 --> 00:00:02.990\n \nPrima riga\n\n00:00:02.990 --> 00:00:03.000\nPrima riga\n \n\n"
    "00:00:03.000 --> 00:00:05.000\nPrima riga\nSeconda riga\n\n00:00:08.000 --> 00:00:09.000\nDopo la pausa\n")


def test_i_sottotitoli_dei_siti_con_lo_speaker(crea, avvisi, monkeypatch):
    # Gabriele, 15 novembre 2026: con lo speaker i sottotitoli di un video di
    # YouTube si scaricano una volta e si seguono come il karaoke, senza il
    # lettore ombra, che riscaricava tutto l'audio.
    import indirizzi

    scaricati = []

    def scarica(traccia, intestazioni=(), attesa=None, serve=None):
        scaricati.append((traccia.lingua, tuple(intestazioni)))
        if traccia.lingua == "de":
            raise OSError("HTTP Error 403")
        return WEBVTT_CHE_SCORRE if traccia.lingua == "it" else "WEBVTT\n\n00:00:00.500 --> 00:00:09.000\nEnglish line\n"

    monkeypatch.setattr(indirizzi, "scarica_i_sottotitoli", scarica)
    pagina = "https://www.youtube.com/watch?v=prova"
    tracce = [indirizzi.Sottotitoli("https://a/it.vtt", "it", "Italian (Original)", True), indirizzi.Sottotitoli("https://a/de.vtt", "de", "Deutsch"),
        indirizzi.Sottotitoli("https://a/en.vtt", "en", "English")]
    indirizzi._tieni(pagina, False, indirizzi.Flusso("https://a/audio.webm", ["User-Agent: di prova"], sottotitoli=tracce))
    detti = []
    m = crea(ai_sottotitoli=detti.append, al_caricamento=avvisi("al_caricamento"))
    lontano = _LontanoFinto()
    lontano.posizione = 0.0
    m.usa_il_lontano(lontano)
    m.suona(pagina)
    # Le tracce arrivano una alla volta: si aspetta l'ultima.
    assert _aspetta(lambda: len((m.tracce() or {}).get("sub") or ()) == 2)
    # Una traccia che non si scarica resta fuori; le altre hanno la lingua e il titolo.
    assert m.tracce()["sub"] == [
        {"id": 1, "type": "sub", "title": "automatici", "lang": "it", "selected": False, "external": True, "image": False, "codec": "webvtt"},
        {"id": 2, "type": "sub", "title": "English", "lang": "en", "selected": False, "external": True, "image": False, "codec": "webvtt"}]
    # Ognuna si scarica una volta, con le intestazioni del flusso; l'ombra non nasce.
    assert scaricati == [("it", ("User-Agent: di prova",)), ("de", ("User-Agent: di prova",)), ("en", ("User-Agent: di prova",))] and m._ombra is None
    assert _aspetta(lambda: "al_caricamento" in avvisi.nomi())
    # Non scelta tace; scelta, dice il blocco in corso e poi quelli che
    # cominciano, senza il cue di 10 millesimi.
    lontano.posizione = 1.5
    time.sleep(0.3)
    assert detti == [] and m.resto_del_sottotitolo() is None
    m.scegli_traccia("sid", "1")
    assert _aspetta(lambda: detti == ["Prima riga"]) and m.resto_del_sottotitolo() == pytest.approx(1.49)
    lontano.posizione = 3.2
    assert _aspetta(lambda: detti == ["Prima riga", "Prima riga\nSeconda riga"])
    # Fra due sottotitoli non c'e' niente da dire.
    lontano.posizione = 6.0
    time.sleep(0.3)
    assert len(detti) == 2 and m.resto_del_sottotitolo() is None
    # L'altra traccia dice subito il suo blocco in corso, e la prima tace.
    m.scegli_traccia("sid", "2")
    assert _aspetta(lambda: detti[-1] == "English line") and [t["selected"] for t in m.tracce()["sub"]] == [False, True]
    # Spenti tacciono; il karaoke non c'e', ne' la sua vista.
    m.scegli_traccia("sid", "no")
    lontano.posizione = 8.5
    time.sleep(0.3)
    assert len(detti) == 3 and m.blocchi_del_karaoke() is None
    # Lo stop ferma il filo.
    m.stop()
    assert m.tracce() is None and m._sottotitoli_lontani is None
    m.usa_il_lontano(None)


def test_il_testo_salvato_dei_video_karaoke_con_lo_speaker(crea, avvisi, monkeypatch):
    # 3.28.3, dal collaudo di Gabriele: un video karaoke di un sito, gia'
    # letto, allo speaker non aveva il suo testo. Ora, senza sottotitoli del
    # sito, il testo salvato nella cartella Testi si segue come il karaoke;
    # e anche dopo il rinnovo del flusso, se quello nuovo non ne ha.
    import indirizzi
    import testi_dei_video

    pagina = "https://www.youtube.com/watch?v=karaoke0001"
    testi_dei_video.salva(pagina, "Torn (Karaoke)", 100.0, [(1.0, ["Prima riga", "Seconda riga"]), (5.0, ["Terza riga"])], [(0.0, 100.0)])
    indirizzi._tieni(pagina, False, indirizzi.Flusso("https://a/audio.webm"))
    detti = []
    m = crea(ai_sottotitoli=detti.append, al_caricamento=avvisi("al_caricamento"))
    lontano = _LontanoFinto()
    lontano.posizione = 0.0
    m.usa_il_lontano(lontano)
    m.suona(pagina)
    assert _aspetta(lambda: (m.tracce() or {}).get("sub"))
    assert m.tracce()["sub"][0]["title"] == "Testo del karaoke, dal video" and m._ombra is None
    m.scegli_traccia("sid", "1")
    lontano.posizione = 1.5
    assert _aspetta(lambda: detti == ["Prima riga\nSeconda riga"])
    lontano.posizione = 5.2
    assert _aspetta(lambda: detti[-1] == "Terza riga")
    m.stop()
    # Il flusso scaduto, rinnovato dal convertitore senza sottotitoli: il testo salvato arriva lo stesso.
    with indirizzi._flussi_blocco:
        flusso, _scadenza, video = indirizzi._flussi[pagina]
        indirizzi._flussi[pagina] = (flusso, time.monotonic() - 1.0, video)

    def risolvi(indirizzo, video=False):
        flusso = indirizzi.Flusso("https://a/nuovo.webm")
        indirizzi._tieni(indirizzo, video, flusso)
        return indirizzi.Pagina(indirizzo, None, flusso=flusso)

    monkeypatch.setattr(indirizzi, "risolvi", risolvi)
    m.suona(pagina)
    convertitore = threading.Thread(target=modulo._flusso_per_il_convertitore, args=(pagina,))
    convertitore.start()
    assert _aspetta(lambda: ((m.tracce() or {}).get("sub") or [{}])[0].get("title") == "Testo del karaoke, dal video")
    convertitore.join(5)
    m.stop()
    m.usa_il_lontano(None)


def test_i_sottotitoli_dei_siti_con_lo_speaker_arrivano_una_traccia_alla_volta(crea, avvisi, monkeypatch):
    # Revisione del 15 novembre 2026: la prima traccia, nella lingua di
    # MeTeOra, quella che la finestra sceglie, non aspetta le altre, che
    # possono metterci fino a 15 secondi l'una; la finestra lo sa dopo la
    # prima e di nuovo dopo l'ultima, come sul PC.
    import indirizzi

    sblocca = threading.Event()
    servono = []

    def scarica(traccia, intestazioni=(), attesa=None, serve=None):
        servono.append(serve)
        if traccia.lingua == "de":
            assert sblocca.wait(10)
        return f"WEBVTT\n\n00:00:00.500 --> 00:00:09.000\nRiga {traccia.lingua}\n"

    monkeypatch.setattr(indirizzi, "scarica_i_sottotitoli", scarica)
    pagina = "https://www.youtube.com/watch?v=lenta"
    indirizzi._tieni(pagina, False, indirizzi.Flusso("https://a/audio.webm", sottotitoli=[indirizzi.Sottotitoli("https://a/it.vtt", "it", "Italiano"),
        indirizzi.Sottotitoli("https://a/de.vtt", "de", "Deutsch")]))
    detti = []
    m = crea(ai_sottotitoli=detti.append, al_caricamento=avvisi("al_caricamento"))
    lontano = _LontanoFinto()
    lontano.posizione = 1.0
    m.usa_il_lontano(lontano)
    m.suona(pagina)
    # La prima c'e', la finestra lo sa e si legge gia', mentre la seconda si scarica ancora.
    assert _aspetta(lambda: [t["lang"] for t in (m.tracce() or {}).get("sub", [])] == ["it"])
    assert _aspetta(lambda: avvisi.nomi().count("al_caricamento") == 1)
    m.scegli_traccia("sid", "1")
    assert _aspetta(lambda: detti == ["Riga it"])
    # La seconda arriva in coda, la finestra lo risa, e la scelta resta.
    sblocca.set()
    assert _aspetta(lambda: [t["lang"] for t in m.tracce()["sub"]] == ["it", "de"])
    assert _aspetta(lambda: avvisi.nomi().count("al_caricamento") == 2)
    assert [t["selected"] for t in m.tracce()["sub"]] == [True, False] and detti == ["Riga it"]
    # serve dice se le tracce servono ancora: dopo lo stop no.
    assert len(servono) == 2 and servono[0]()
    m.stop()
    assert not servono[0]()
    # Una traccia che arriva a brano cambiato resta fuori.
    sblocca.clear()
    m.suona(pagina)
    assert _aspetta(lambda: [t["lang"] for t in (m.tracce() or {}).get("sub", [])] == ["it"])
    m.stop()
    sblocca.set()
    time.sleep(0.3)
    assert m._sottotitoli_lontani is None
    m.usa_il_lontano(None)


def test_i_sottotitoli_a_pezzi_dei_siti_con_lo_speaker(crea, avvisi, monkeypatch):
    # Revisione del 15 novembre 2026: una traccia che il sito da' come
    # playlist HLS di pezzi WebVTT, come quelle che yt-dlp chiama
    # m3u8_native, con lo speaker spariva senza avviso; ora si scarica a
    # pezzi, come fa libmpv sul PC, e si legge seguendo lo speaker.
    import io

    import indirizzi

    pagine = {"https://s.example/it/prog.m3u8": "#EXTM3U\n#EXT-X-TARGETDURATION:6\n#EXTINF:6.0,\nseg0.webvtt\n#EXTINF:6.0,\nseg1.webvtt\n#EXT-X-ENDLIST\n",
        "https://s.example/it/seg0.webvtt": ("WEBVTT\nX-TIMESTAMP-MAP=MPEGTS:900000,LOCAL:00:00:00.000\n\n00:00:01.000 --> 00:00:02.500\nBip!\n\n"
            "00:00:05.000 --> 00:00:07.000\nA cavallo\n"),
        "https://s.example/it/seg1.webvtt": ("WEBVTT\nX-TIMESTAMP-MAP=MPEGTS:900000,LOCAL:00:00:00.000\n\n00:00:05.000 --> 00:00:07.000\nA cavallo\n\n"
            "00:00:08.000 --> 00:00:09.000\nBop!\n")}

    class Risposta(io.BytesIO):
        def __init__(self, indirizzo):
            super().__init__(pagine[indirizzo].encode("utf-8"))
            self.indirizzo = indirizzo

        def geturl(self):
            return self.indirizzo

        def __enter__(self):
            return self

        def __exit__(self, *_eccezione):
            self.close()

    monkeypatch.setattr(indirizzi.urllib.request, "urlopen", lambda richiesta, timeout=None: Risposta(richiesta.full_url))
    pagina = "https://www.example.com/video/a-pezzi"
    indirizzi._tieni(pagina, False, indirizzi.Flusso("https://s.example/audio.m4a", sottotitoli=[indirizzi.Sottotitoli("https://s.example/it/prog.m3u8", "it", "Italiano")]))
    detti = []
    m = crea(ai_sottotitoli=detti.append, al_caricamento=avvisi("al_caricamento"))
    lontano = _LontanoFinto()
    lontano.posizione = 0.0
    m.usa_il_lontano(lontano)
    m.suona(pagina)
    assert _aspetta(lambda: [(t["title"], t["lang"]) for t in (m.tracce() or {}).get("sub", [])] == [("Italiano", "it")])
    m.scegli_traccia("sid", "1")
    for posizione, testo in ((1.5, "Bip!"), (5.5, "A cavallo"), (8.5, "Bop!")):
        lontano.posizione = posizione
        assert _aspetta(lambda testo=testo: detti[-1:] == [testo])
    # Il cue a cavallo dei due pezzi si dice una volta, come sul PC.
    assert detti == ["Bip!", "A cavallo", "Bop!"]
    m.stop()
    m.usa_il_lontano(None)


def test_le_tracce_dei_siti_sul_pc_si_aggiungono_una_alla_volta():
    # Revisione del 15 novembre 2026: sub-add apre ogni traccia in disparte,
    # e le aggiunte vanno una alla volta, dalla risposta di quella prima,
    # perche' insieme finirebbero in un ordine qualunque. La prima, nella
    # lingua di MeTeOra, si aggiunge scelta, come la sceglieva sub-files
    # (3.8.0): con i sottotitoli spenti la toglie la finestra.
    import indirizzi

    class LettoreFinto:
        """Il lettore come lo vede il motore: annota i comandi, e risponde solo quando la prova lo chiede."""

        def __init__(self):
            self._richieste = 1
            self.sottotitoli_del_sito = (indirizzi.Sottotitoli("https://a/it.vtt", "it", "Italian (Original)", True), indirizzi.Sottotitoli("https://a/de.vtt", "de", "Deutsch"),
                indirizzi.Sottotitoli("https://a/en.vtt", "en", "English"))
            self.comandi, self.risposte = [], []

        def comando(self, *argomenti, risposta=None):
            self.comandi.append(argomenti)
            self.risposte.append(risposta)

    m = Motore(ao="null")
    try:
        finto = LettoreFinto()
        avvisati = []
        m._aggiungi_i_sottotitoli_del_sito(finto, 1, lambda: avvisati.append(len(finto.comandi)))
        assert finto.comandi == [("sub-add", "https://a/it.vtt", "select", "automatici", "it")] and avvisati == []
        # La seconda parte solo dalla risposta della prima, e la finestra rilegge le tracce.
        finto.risposte[0](None, None)
        assert finto.comandi[1:] == [("sub-add", "https://a/de.vtt", "auto", "Deutsch", "de")] and avvisati == [2]
        # Una traccia che il sito non da' non ferma le altre.
        finto.risposte[1](RuntimeError("HTTP Error 404"), None)
        assert finto.comandi[2:] == [("sub-add", "https://a/en.vtt", "auto", "English", "en")] and avvisati == [2]
        # Dopo l'ultima, la finestra le rilegge tutte.
        finto.risposte[2](None, None)
        assert len(finto.comandi) == 3 and avvisati == [2, 3]
        # La risposta di un caricamento vecchio non aggiunge niente.
        finto.comandi.clear()
        finto.risposte.clear()
        m._aggiungi_i_sottotitoli_del_sito(finto, 1)
        finto._richieste = 2
        finto.risposte[0](None, None)
        assert len(finto.comandi) == 1
    finally:
        m.chiudi()


def test_i_sottotitoli_dei_siti_sul_pc_hanno_titolo_e_lingua(avvisi, tmp_path):
    # Gabriele, 15 novembre 2026: con sub-files libmpv chiamava la traccia
    # con la coda del suo indirizzo firmato, e D la leggeva tutta; sub-add le
    # da' il titolo e la lingua, nell'ordine dato, e sceglie la prima, come
    # sub-files (revisione del 15 novembre 2026). I sottotitoli sono file sul
    # disco, che sub-add apre come gli indirizzi.
    import indirizzi

    brano = _silenzio(tmp_path / "audio.wav", 6)
    (tmp_path / "it.vtt").write_text("WEBVTT\n\n00:00:00.500 --> 00:00:04.000\nCiao a tutti\n", encoding="utf-8")
    (tmp_path / "de.vtt").write_text("WEBVTT\n\n00:00:00.500 --> 00:00:04.000\nHallo\n", encoding="utf-8")
    pagina = "https://www.youtube.com/watch?v=prova"
    tracce = [indirizzi.Sottotitoli(str(tmp_path / "it.vtt"), "it", "Italian (Original)", True), indirizzi.Sottotitoli(str(tmp_path / "de.vtt"), "de", "Deutsch")]
    indirizzi._tieni(pagina, False, indirizzi.Flusso(brano, sottotitoli=tracce))
    detti, caricati = [], []
    m = Motore(ao="null", ai_sottotitoli=detti.append, al_caricamento=lambda: caricati.append(True))
    try:
        m.suona(pagina)
        # L'avviso arriva dopo la prima traccia, e di nuovo dopo l'ultima.
        assert _aspetta(lambda: len((m.tracce() or {"sub": []})["sub"]) == 2 and len(caricati) == 2, 10)
        sub = m.tracce()["sub"]
        assert [(t.get("title"), t.get("lang"), t.get("selected"), t.get("codec")) for t in sub] == [("automatici", "it", True, "webvtt"), ("Deutsch", "de", False, "webvtt")]
        # La prima, scelta da libmpv, si legge senza che la finestra la scelga.
        assert _aspetta(lambda: detti == ["Ciao a tutti"], 5)
        m.scegli_traccia("sid", str(sub[1]["id"]))
        assert _aspetta(lambda: detti == ["Ciao a tutti", "Hallo"], 5)
        # Il brano dopo, un file, non ha le tracce del sito.
        m.suona(_silenzio(tmp_path / "file.wav", 2))
        assert _aspetta(lambda: m.tracce() is not None and m._attivo.percorso.endswith("file.wav"), 5)
        assert _aspetta(lambda: m.tracce()["sub"] == [], 2)
    finally:
        m.chiudi()


def _sul_pc(blocchi):
    """Che cosa dice il motore sul PC di una fila di sottotitoli di testo,
    [(inizio, fine, testo)]: sub-text quando il testo cambia, anche vuoto fra
    due staccati, e sub-start a ogni cue, come li manda libmpv."""
    detti = []
    m = Motore(ao="null", ai_sottotitoli=detti.append)
    try:
        lettore, fine_di_prima, testo_di_prima = m._attivo, None, None
        for inizio, fine, testo in blocchi:
            if fine_di_prima is not None and inizio > fine_di_prima + 0.001:
                m._sottotitolo(lettore, "sub-text", "")
                m._sottotitolo_a_immagini(lettore, "sub-start", None)
                testo_di_prima = ""
            if testo != testo_di_prima:
                m._sottotitolo(lettore, "sub-text", testo)
            m._sottotitolo_a_immagini(lettore, "sub-start", inizio)
            fine_di_prima, testo_di_prima = fine, testo
    finally:
        m.chiudi()
    return detti


def test_i_blocchi_uguali_e_attaccati_dei_siti_si_dicono_come_sul_pc():
    # Revisione del 15 novembre 2026: con lo speaker un cartello animato, lo
    # stesso testo cue dopo cue, come quello della 1.82.0, si ridiceva ogni
    # mezzo secondo, perche' il cue si confrontava con l'inizio del blocco
    # gia' unito; sul PC si dice una volta. Il confronto e' con il cue prima.
    import karaoke

    cartello = [(20 + i / 24, 20 + (i + 1) / 24, "Stazione di Tokyo") for i in range(72)]
    uniti = modulo._senza_ripetizioni(cartello)
    assert len(uniti) == 1 and uniti[0][0] == 20 and uniti[0][1] == pytest.approx(23.0) and uniti[0][2] == "Stazione di Tokyo"
    # Due uguali e attaccati restano due se il secondo comincia mezzo secondo
    # o piu' dopo il primo, come un ritornello; prima diventano uno. Due
    # staccati restano due.
    no, si, ah = [(1.0, 1.6, "No"), (1.6, 2.2, "No")], [(1.0, 1.4, "Sì"), (1.4, 1.8, "Sì")], [(1.0, 1.2, "Ah"), (1.3, 1.5, "Ah")]
    assert modulo._senza_ripetizioni(no) == no and modulo._senza_ripetizioni(si) == [(1.0, 1.8, "Sì")] and modulo._senza_ripetizioni(ah) == ah
    # Con lo speaker si dicono come sul PC.
    attesi = {"Stazione di Tokyo": ["Stazione di Tokyo"], "No": ["No", "No"], "Sì": ["Sì"], "Ah": ["Ah", "Ah"]}
    for blocchi in (cartello, no, si, ah):
        seguito = karaoke.Seguito("sito", [], pronti=modulo._senza_ripetizioni(blocchi))
        seguito.scegli(True)
        detti = [testo for passo in range(300) for testo in seguito.avanza(round(blocchi[0][0] - 1.0 + passo * 0.1, 3))]
        assert detti == _sul_pc(blocchi) == attesi[blocchi[0][2]]


def test_dopo_un_salto_l_ombra_ridice_il_sottotitolo():
    # Revisione del 15 novembre 2026: quando l'ombra salta al punto dello
    # speaker, il sottotitolo di adesso si dice anche se ha le righe di
    # quello visto prima, con la sola riga vuota spostata, come nei lettori.
    detti = []
    comandi = []
    mpv_finto = types.SimpleNamespace(pause=False, seeking=False, time_pos=12.1, command_async=lambda *argomenti: comandi.append(argomenti))
    ombra = types.SimpleNamespace(pronto=True, mpv=mpv_finto, _testo="Caruso\n", _nuovo=False, numero=1, _al_testo=lambda _numero, testo: detti.append(testo))
    # Vicina allo speaker non salta, e la riga spostata non si ridice.
    modulo._Ombra.segui(ombra, 12.0, False)
    modulo._Ombra._sottotitolo(ombra, "sub-text", " \nCaruso")
    assert comandi == [] and detti == []
    # Scostata piu' di SCARTO_DELL_OMBRA salta, e la riga si dice.
    mpv_finto.time_pos = 12.0 + modulo.SCARTO_DELL_OMBRA + 1.0
    modulo._Ombra.segui(ombra, 12.0, False)
    assert comandi == [("seek", "12.000", "absolute+exact")] and ombra._testo is None
    modulo._Ombra._sottotitolo(ombra, "sub-text", "Caruso\n")
    assert detti == ["Caruso\n"]


def test_la_sorgente_wav(crea, tmp_path):
    # 2.7.0: il WAV in RAM per gli speaker, al posto del FLAC su disco, con
    # libmpv vero che scrive nella pipe con nome: tre secondi di seno a 16 bit
    # e 44,1 kHz restano a 16 bit e 44,1 kHz, in stereo, con la durata letta da
    # libmpv.
    import wav_in_ram

    m = crea()
    brano = _seno(tmp_path / "brano.wav", 3)
    assert m.formato_da_convertire(brano) == (pytest.approx(3.0, abs=0.05), 44100, 16)
    sorgente = m.sorgente_wav(brano)
    try:
        assert not sorgente.emulato and (sorgente.frequenza, sorgente.bit) == (44100, 16)
        assert sorgente.dimensione == wav_in_ram.INTESTAZIONE + int(sorgente.durata * 44100) * 4
        richiesta = sorgente.nuova_richiesta()
        letti = bytearray()
        while len(letti) < sorgente.dimensione:
            pezzo = sorgente.leggi(len(letti), 65536, richiesta)
            assert pezzo
            letti += pezzo
        assert letti[:4] == b"RIFF" and letti[8:12] == b"WAVE"
        # Il seno c'e': il PCM non e' silenzio.
        assert max(letti[wav_in_ram.INTESTAZIONE:wav_in_ram.INTESTAZIONE + 48000]) > 0 and not sorgente.guasta
    finally:
        sorgente.chiudi()
    # Un 24 bit a 96 kHz resta a 96 kHz, ma a 16 bit: i WAV a 24 bit lo
    # speaker li suona gracchianti (prova di Gabriele del 5 novembre 2026).
    alto = tmp_path / "alto.wav"
    with wave.open(str(alto), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(3)
        f.setframerate(96000)
        campioni = np.round(0.25 * 8388607 * np.sin(2 * np.pi * 440 * np.arange(96000 * 2) / 96000)).astype("<i4")
        f.writeframes(b"".join(int(c).to_bytes(4, "little", signed=True)[:3] for c in campioni))
    assert m.formato_da_convertire(str(alto)) == (pytest.approx(2.0, abs=0.05), 96000, 16)
    sorgente = m.sorgente_wav(str(alto))
    try:
        assert (sorgente.frequenza, sorgente.bit) == (96000, 16) and sorgente.dimensione == wav_in_ram.INTESTAZIONE + int(sorgente.durata * 96000) * 4
        richiesta = sorgente.nuova_richiesta()
        letti = bytearray()
        while len(letti) < sorgente.dimensione:
            pezzo = sorgente.leggi(len(letti), 65536, richiesta)
            assert pezzo
            letti += pezzo
        assert letti[34:36] == (16).to_bytes(2, "little") and max(letti[wav_in_ram.INTESTAZIONE:wav_in_ram.INTESTAZIONE + 96000]) > 0
    finally:
        sorgente.chiudi()
    # Un file che non c'e' non ha durata, e la sorgente non si fa.
    assert m.durata_da_convertire(str(tmp_path / "non_ce.wav")) is None
    with pytest.raises(ValueError):
        m.sorgente_wav(str(tmp_path / "non_ce.wav"))


# Il ramo velocita (Gabriele, 15 novembre 2026): i salti con YouTube erano
# diventati lenti.


def _server_a_intervalli(dati):
    """Un server HTTP come quello dei flussi di YouTube, che serve dati a
    intervalli di byte e annota l'intestazione Range di ogni richiesta."""
    import http.server

    chiesti = []

    class Gestore(http.server.BaseHTTPRequestHandler):
        def log_message(self, *_argomenti):
            pass

        def do_GET(self):
            intervallo = self.headers.get("Range")
            chiesti.append(intervallo)
            inizio, fine = 0, len(dati) - 1
            if intervallo and intervallo.startswith("bytes="):
                da, _trattino, a = intervallo[len("bytes="):].partition("-")
                inizio, fine = int(da or 0), min(int(a), len(dati) - 1) if a else len(dati) - 1
                self.send_response(206)
                self.send_header("Content-Range", f"bytes {inizio}-{fine}/{len(dati)}")
            else:
                self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(fine - inizio + 1))
            self.end_headers()
            # libmpv chiude la connessione quando ha letto quanto gli serve.
            with contextlib.suppress(OSError):
                self.wfile.write(dati[inizio:fine + 1])

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Gestore)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, chiesti


def _chiudi_il_server(server):
    server.shutdown()
    server.server_close()


def test_il_flusso_a_pezzi_arriva_a_libmpv_a_pezzi(crea, tmp_path):
    # YouTube da' circa 26 KB/s a una richiesta aperta, Range: bytes=0-, e da
    # 4 a 11 MB/s a pezzi da 10 MB (misura dell'esploratore): il pezzo che
    # yt-dlp dice arriva a libmpv come curl-max-request-size, per i lettori,
    # per la sonda dello speaker e per il suo convertitore. Qui un server
    # vero, in locale, con pezzi da 64 KB.
    import indirizzi
    import wav_in_ram

    brano = _seno(tmp_path / "brano.wav", 20, frequenza=8000)
    with open(brano, "rb") as f:
        dati = f.read()
    server, chiesti = _server_a_intervalli(dati)
    try:
        vero = f"http://127.0.0.1:{server.server_address[1]}/brano.wav"
        pagina = "https://www.youtube.com/watch?v=a_pezzi"
        indirizzi._tieni(pagina, False, indirizzi.Flusso(vero, pezzo=65536))
        assert modulo._Brano(pagina, inizio=3.0).opzioni == {"start": "3.000", "curl-max-request-size": "65536"}
        m = crea()
        # La sonda dello speaker.
        assert m.formato_da_convertire(pagina) == (pytest.approx(20.0, abs=0.1), 48000, 16)
        assert chiesti and all(r and r.startswith("bytes=") and not r.endswith("-") for r in chiesti), chiesti
        # Il convertitore dello speaker, fino in fondo.
        chiesti.clear()
        sorgente = m.sorgente_wav(pagina)
        try:
            richiesta = sorgente.nuova_richiesta()
            letti = bytearray()
            while len(letti) < sorgente.dimensione:
                pezzo = sorgente.leggi(len(letti), 65536, richiesta)
                assert pezzo
                letti += pezzo
            assert max(letti[wav_in_ram.INTESTAZIONE:]) > 0 and not sorgente.guasta
        finally:
            sorgente.chiudi()
        assert len(chiesti) >= len(dati) // 65536 and all(r and not r.endswith("-") for r in chiesti), chiesti
        # Il lettore del PC.
        chiesti.clear()
        m.suona(pagina)
        assert _aspetta(lambda: m._attivo.pronto and m.posizione is not None)
        assert chiesti and all(r and not r.endswith("-") for r in chiesti), chiesti
        m.stop()
        # Un flusso senza pezzo, come quelli degli altri siti, resta com'era.
        indirizzi._tieni(pagina, False, indirizzi.Flusso(vero))
        assert modulo._Brano(pagina).opzioni == {}
        indirizzi.metti_il_diretto("http://radio.example/flusso", dal_vivo=True)
        assert modulo._Brano("http://radio.example/flusso").opzioni == {} and modulo._Brano(brano).opzioni == {}
    finally:
        _chiudi_il_server(server)


def test_la_ripartenza_dopo_la_scadenza_rinnova_il_flusso(crea, tmp_path, monkeypatch):
    # Un flusso vale venti minuti (indirizzi.FLUSSO_VALIDO): dopo, una
    # ripartenza del WAV in RAM per un salto lontano apriva la pagina, che
    # libmpv senza ytdl non apre, e lo speaker restava nel silenzio fino alla
    # fine (15 novembre 2026). Il convertitore rinnova il flusso da se', con
    # yt-dlp, senza il video.
    import indirizzi
    import wav_in_ram

    monkeypatch.setattr(wav_in_ram, "dimensione_della_finestra", lambda libera=None: 2**20 // 12 * 12)
    brano = _seno(tmp_path / "lungo.wav", 120, frequenza=8000)
    with open(brano, "rb") as f:
        server, _chiesti = _server_a_intervalli(f.read())
    vero = f"http://127.0.0.1:{server.server_address[1]}/lungo.wav"
    pagina = "https://www.youtube.com/watch?v=scaduto"
    rinnovi = []

    def risolvi(indirizzo, video=False):
        rinnovi.append((indirizzo, video))
        flusso = indirizzi.Flusso(vero, pezzo=1 << 20)
        indirizzi._tieni(indirizzo, video, flusso)
        return indirizzi.Pagina(indirizzo, None, flusso=flusso)

    monkeypatch.setattr(indirizzi, "risolvi", risolvi)
    m = crea()
    try:
        # Senza il flusso, la sonda lo chiede; con il flusso, la sorgente parte senza.
        sorgente = m.sorgente_wav(pagina)
        assert rinnovi == [(pagina, False)]
        try:
            assert max(sorgente.leggi(wav_in_ram.INTESTAZIONE, 65536, sorgente.nuova_richiesta())) > 0
            assert rinnovi == [(pagina, False)]
            # Il flusso scade; il salto lontano lo rinnova, e il brano suona.
            indirizzi.dimentica(pagina)
            lontano = wav_in_ram.INTESTAZIONE + 60 * sorgente.al_secondo
            pezzo = sorgente.leggi(lontano, 65536, sorgente.nuova_richiesta())
            assert pezzo and max(pezzo) > 0 and not sorgente.guasta and sorgente.ripartenze == 1
            assert rinnovi == [(pagina, False)] * 2
        finally:
            sorgente.chiudi()
        # Se yt-dlp non trova il flusso, la ripartenza e' un guasto, non silenzio.
        sorgente = m.sorgente_wav(pagina)
        try:
            monkeypatch.setattr(indirizzi, "risolvi", lambda indirizzo, video=False: (_ for _ in ()).throw(indirizzi.ErroreIndirizzo("niente")))
            indirizzi.dimentica(pagina)
            assert sorgente.leggi(lontano, 65536, sorgente.nuova_richiesta()) is None and sorgente.guasta
        finally:
            sorgente.chiudi()
    finally:
        _chiudi_il_server(server)


def test_le_ripartenze_del_wav_in_ram_non_lasciano_libmpv_vive(crea, tmp_path, monkeypatch):
    # Con una conversione veloce, come un file del disco o il flusso a pezzi
    # di YouTube, il passaggio sostituito lasciava libmpv ferma a scrivere in
    # una pipe che nessuno leggeva piu', e terminate la aspettava per sempre:
    # a ogni ripartenza una libmpv e un filo in piu' (misura dell'esploratore
    # del 15 novembre 2026). Con libmpv vera, dopo otto ripartenze e la
    # chiusura non resta niente.
    import wav_in_ram

    def vivi(nome):
        return sum(1 for f in threading.enumerate() if f.name.startswith(nome))

    monkeypatch.setattr(wav_in_ram, "dimensione_della_finestra", lambda libera=None: 2**20 // 12 * 12)
    brano = _seno(tmp_path / "lungo.wav", 120, frequenza=8000)
    m = crea()
    libmpv = vivi("MPVEventHandlerThread")
    sorgente = m.sorgente_wav(brano)
    try:
        for secondi in (30, 60, 90, 15, 105, 45, 75, 5):
            pezzo = sorgente.leggi(wav_in_ram.INTESTAZIONE + secondi * sorgente.al_secondo, 4096, sorgente.nuova_richiesta())
            assert pezzo and max(pezzo) > 0
            # Il convertitore riempie la finestra, e resta fermo a scrivere;
            # quello di prima si chiude in disparte, e con lui al piu' uno
            # ancora piu' vecchio, su una macchina carica.
            time.sleep(0.2)
            assert vivi("MPVEventHandlerThread") <= libmpv + 3
        assert sorgente.ripartenze == 8 and not sorgente.guasta
    finally:
        sorgente.chiudi()
    assert _aspetta(lambda: not vivi("MeTeOra, fine del WAV in RAM") and not vivi("MeTeOra, WAV in RAM") and vivi("MPVEventHandlerThread") == libmpv, 20)


# La revisione del ramo velocita (15 novembre 2026): il lettore lontano vero
# dentro il motore, non _LontanoFinto, con lo speaker finto di
# tests/test_lontano.py che suona in tempo reale e risponde ai salti in
# ritardo, e libmpv vera.


def _speaker_vero(ritardo=None):
    """Un lontano.LettoreLontano vero, con lo speaker che suona in tempo
    reale, il server finto e una sorgente finta per i brani da convertire:
    (lettore, apparecchio, stati), e stati["allo_stato"] manda gli stati
    dello speaker, come pychromecast."""
    from test_lontano import _ApparecchioCheSuona, _ServerFinto, _SorgenteFinta

    import lontano

    apparecchio = _ApparecchioCheSuona(ritardo)
    stati = {}

    def connetti(allo_stato, al_distacco):
        stati["allo_stato"] = allo_stato
        return apparecchio

    return lontano.LettoreLontano(connetti, _ServerFinto(), _SorgenteFinta), apparecchio, stati


def _suona_allo_speaker(stati, apparecchio, durata=300.0):
    """Lo speaker dice che suona il brano che ha ricevuto per ultimo."""
    import trasmissione

    indirizzo = next(c[1] for c in reversed(apparecchio.chiamate) if c[0] == "suona")
    stati["allo_stato"]({"stato": trasmissione.IN_RIPRODUZIONE, "posizione": 0.0, "durata": durata, "motivo": None, "indirizzo": indirizzo})


def test_lo_speaker_lasciato_si_ferma(crea, tmp_path):
    # Scegliendo un altro speaker, o una scheda del PC, usa_il_lontano fa lo
    # stop e chiude lo speaker di prima: il suo comando ferma, legato al
    # brano, cadeva con lo stop che chiudi rifa', e lo speaker di prima
    # continuava a suonare. _LontanoFinto non lo vedeva.
    brano = str(tmp_path / "brano.mp3")
    with open(brano, "wb") as f:
        f.write(bytes(1024))
    m = crea()
    primo, apparecchio, stati = _speaker_vero()
    apparecchio.via.set()
    m.usa_il_lontano(primo)
    m.suona(brano)
    assert primo.aspetta_i_comandi()
    _suona_allo_speaker(stati, apparecchio)
    secondo, altro, _stati = _speaker_vero()
    altro.via.set()
    m.usa_il_lontano(secondo)
    m.suona(brano)
    assert primo.aspetta_i_comandi() and secondo.aspetta_i_comandi()
    assert [c[0] for c in apparecchio.chiamate] == ["suona", "ferma", "chiudi"] and apparecchio.chiamate[-1] == ("chiudi", True)
    assert [c[0] for c in altro.chiamate] == ["suona"]
    # Tornando al PC, si ferma anche il secondo.
    m.usa_il_lontano(None)
    assert secondo.aspetta_i_comandi() and [c[0] for c in altro.chiamate] == ["suona", "ferma", "chiudi"] and m.lontano is None


def test_una_lettura_interrotta_riprende_dal_punto(crea, avvisi, tmp_path):
    # Un file che finisce molto prima della sua durata, come un video in una
    # cartella di rete la cui lettura si interrompe, non e' finito: l'avviso
    # dice da dove riprendere, al piu' due volte di fila nello stesso punto,
    # e la terza e' un errore. Un file che finisce davvero da' la fine
    # (collaudo di Gabriele, 18 novembre 2026). Qui un MP3 a 64 kbps la cui
    # intestazione Info dichiara 40 secondi, come la durata di un MP4, e che
    # ne ha 3: libmpv crede all'intestazione. Il WAV no, conta i suoi byte.
    from test_registrazioni import _registrata

    interrotto = _registrata(tmp_path, "interrotto", 40).percorso
    with open(interrotto, "r+b") as f:
        f.truncate(1000 + 8000 * 3)
    m = crea(alla_fine_anticipata=avvisi("alla_fine_anticipata"))

    def finali():
        return [(nome, argomenti) for _istante, nome, argomenti in avvisi.righe if nome in ("alla_fine_anticipata", "all_errore", "alla_fine")]

    m.suona(interrotto)
    assert _aspetta(lambda: len(finali()) == 1, 15)
    nome, (percorso, sottobrano, secondi, riprende) = finali()[-1]
    assert (nome, percorso, sottobrano, riprende) == ("alla_fine_anticipata", interrotto, None, True) and 2.5 < secondi <= 3.05
    # Ripreso, si ferma di nuovo nello stesso punto: e' la sua fine, detta, e poi la fine come sempre.
    m.suona(interrotto, inizio=secondi - 1.0)
    assert _aspetta(lambda: len(finali()) == 3, 15)
    assert [nome for nome, _argomenti in finali()[1:]] == ["alla_fine_anticipata", "alla_fine"] and finali()[1][1][3] is False
    # Un file intero finisce come sempre, e poi un altro interrotto si riprende di nuovo.
    m.suona(_seno(tmp_path / "intero.wav", 2))
    assert _aspetta(lambda: len(finali()) == 4, 15) and finali()[-1][0] == "alla_fine"
    m.suona(interrotto)
    assert _aspetta(lambda: len(finali()) == 5, 15) and finali()[-1][1][3] is True


def test_la_chiusura_del_motore_aspetta_lo_stop_dello_speaker(crea, tmp_path):
    # All'uscita di MeTeOra lo stop allo speaker va in fila, dietro un salto
    # che lo speaker conferma tardi, in un filo demone, e il processo finiva
    # prima: lo speaker continuava a suonare. La chiusura del motore aspetta
    # i comandi, al piu' ATTESA_DELLO_SPEAKER_ALL_USCITA.
    brano = str(tmp_path / "brano.mp3")
    with open(brano, "wb") as f:
        f.write(bytes(1024))
    m = crea()
    lettore, apparecchio, stati = _speaker_vero(ritardo=0.5)
    m.usa_il_lontano(lettore)
    m.suona(brano)
    assert lettore.aspetta_i_comandi()
    _suona_allo_speaker(stati, apparecchio)
    m.salta(30)
    assert _aspetta(lambda: any(c[0] == "vai_a" for c in apparecchio.chiamate))
    inizio = time.monotonic()
    m.chiudi()
    durata = time.monotonic() - inizio
    assert [c[0] for c in apparecchio.chiamate] == ["suona", "vai_a", "ferma", "chiudi"] and apparecchio.chiamate[-1] == ("chiudi", False)
    assert durata < modulo.ATTESA_DELLO_SPEAKER_ALL_USCITA + 1


def test_l_uscita_aspetta_anche_lo_speaker_lasciato(crea, tmp_path):
    # Passando al PC, o a un altro speaker, e uscendo subito: lo stop allo
    # speaker lasciato e' in fila dietro un salto che conferma tardi, e
    # l'uscita aspettava solo lo speaker in uso. Il lasciato continuava a
    # suonare (revisione dell'unione, 15 novembre 2026).
    brano = str(tmp_path / "brano.mp3")
    with open(brano, "wb") as f:
        f.write(bytes(1024))
    m = crea()
    lettore, apparecchio, stati = _speaker_vero(ritardo=0.6)
    m.usa_il_lontano(lettore)
    m.suona(brano)
    assert lettore.aspetta_i_comandi()
    _suona_allo_speaker(stati, apparecchio)
    m.salta(30)
    assert _aspetta(lambda: any(c[0] == "vai_a" for c in apparecchio.chiamate))
    m.usa_il_lontano(None)
    inizio = time.monotonic()
    m.chiudi()
    durata = time.monotonic() - inizio
    assert [c[0] for c in apparecchio.chiamate] == ["suona", "vai_a", "ferma", "chiudi"]
    assert durata < modulo.ATTESA_DELLO_SPEAKER_ALL_USCITA + 1


def test_i_sottotitoli_dei_siti_con_lo_speaker_dopo_il_rinnovo(crea, avvisi, monkeypatch):
    # Il brano di un sito riparte allo speaker con il flusso tenuto scaduto,
    # come passando allo speaker dopo venti minuti, o con Y e la dissolvenza:
    # il convertitore lo rinnova, e i sottotitoli arrivano dal flusso nuovo,
    # con una sola chiamata a yt-dlp. Prima il brano restava senza tracce
    # finche' non si rifaceva con X. Il flusso nuovo si chiede con il video,
    # come quello scaduto: solo audio, tornando al PC il video non c'era piu'
    # (revisione dell'unione, 15 novembre 2026).
    import indirizzi

    monkeypatch.setattr(indirizzi, "scarica_i_sottotitoli", lambda traccia, intestazioni=(), attesa=None, serve=None: WEBVTT_CHE_SCORRE)
    pagina = "https://www.youtube.com/watch?v=rinnovo"
    tracce = [indirizzi.Sottotitoli("https://a/it.vtt", "it", "Italian (Original)", True)]
    chiesti = []

    def risolvi(indirizzo, video=False):
        chiesti.append((indirizzo, video))
        time.sleep(0.3)
        flusso = indirizzi.Flusso("https://a/nuovo.webm", ["User-Agent: di prova"], sottotitoli=tracce)
        indirizzi._tieni(indirizzo, video, flusso)
        return indirizzi.Pagina(indirizzo, None, flusso=flusso)

    monkeypatch.setattr(indirizzi, "risolvi", risolvi)
    indirizzi._tieni(pagina, True, indirizzi.Flusso("https://a/vecchio.webm", sottotitoli=tracce))
    with indirizzi._flussi_blocco:
        flusso, _scadenza, video = indirizzi._flussi[pagina]
        indirizzi._flussi[pagina] = (flusso, time.monotonic() - 1.0, video)
    assert indirizzi.pronto(pagina) is None and indirizzi.video_tenuto(pagina)
    detti = []
    m = crea(ai_sottotitoli=detti.append, al_caricamento=avvisi("al_caricamento"))
    lontano = _LontanoFinto()
    lontano.posizione = 0.0
    m.usa_il_lontano(lontano)
    m.suona(pagina, inizio=12.0)
    # Il convertitore dello speaker rinnova anche lui, nello stesso momento.
    convertitore = threading.Thread(target=modulo._flusso_per_il_convertitore, args=(pagina,))
    convertitore.start()
    assert _aspetta(lambda: len((m.tracce() or {}).get("sub") or ()) == 1)
    convertitore.join(5)
    assert chiesti == [(pagina, True)] and indirizzi.pronto(pagina, video=True) is not None
    m.scegli_traccia("sid", "1")
    lontano.posizione = 1.5
    assert _aspetta(lambda: detti == ["Prima riga"])
    m.stop()
    m.usa_il_lontano(None)


def test_un_salto_con_lo_speaker_dice_il_sottotitolo_una_volta(crea, avvisi, tmp_path):
    # Dopo un salto il lettore lontano dava come posizione il punto chiesto,
    # fermo, finche' lo speaker non rispondeva e per un secondo dopo; l'ombra,
    # che corre, se ne scostava e risaltava allo stesso punto ogni mezzo
    # secondo, e il sottotitolo in corso si ridiceva tre o quattro volte.
    # L'ombra segue il suono dello speaker: un salto, un sottotitolo. Lo
    # speaker risponde al salto dopo 0.3 secondi.
    film = _silenzio(tmp_path / "film.mkv", 30)
    (tmp_path / "film.srt").write_text("1\n00:00:01,000 --> 00:00:02,500\nPrima\n\n2\n00:00:12,000 --> 00:00:17,000\nSeconda\n\n"
                                       "3\n00:00:25,000 --> 00:00:26,000\nTerza\n", encoding="utf-8")
    detti = []
    m = crea(ai_sottotitoli=detti.append, al_caricamento=avvisi("al_caricamento"))
    lettore, apparecchio, stati = _speaker_vero(ritardo=0.3)
    m.usa_il_lontano(lettore)
    m.suona(film)
    assert _aspetta(lambda: any(c[0] == "suona" for c in apparecchio.chiamate))
    _suona_allo_speaker(stati, apparecchio, 30.0)
    assert _aspetta(lambda: (m.tracce() or {}).get("sub"), 10)
    m.scegli_traccia("sid", str(m.tracce()["sub"][0]["id"]))
    # Fra Prima e Seconda, il salto dentro Seconda, che dura cinque secondi.
    assert _aspetta(lambda: lettore.posizione > 3.0)
    detti.clear()
    m.vai_a(12.0)
    # La finestra ha subito il punto chiesto; l'ombra il suono, che arriva dopo.
    assert m.posizione == pytest.approx(12.0, abs=0.1) and lettore.posizione < 5.0
    time.sleep(2.5)
    assert detti == ["Seconda"] and lettore.posizione == pytest.approx(14.2, abs=0.3)
    m.usa_il_lontano(None)


def test_la_diretta_convertita_chiusa_non_lascia_libmpv_vive(crea, tmp_path):
    # L'audio delle TV per lo speaker, wav_in_ram.FlussoPcm, chiuso senza piu'
    # leggere: con la pipe chiusa prima di terminate libmpv restava fermo a
    # scrivere nella meta' dei casi, con un filo e una libmpv vivi per ogni
    # TV fermata, e la prova con il convertitore finto non lo vedeva. La
    # pipe si vuota mentre libmpv si ferma: sei chiusure, e non resta niente.
    import wav_in_ram

    def vivi(nome):
        return sum(1 for f in threading.enumerate() if f.name.startswith(nome))

    m = crea()
    brano = _seno(tmp_path / "tv.wav", 60, frequenza=8000)
    libmpv = vivi("MPVEventHandlerThread")
    for _ in range(6):
        flusso = wav_in_ram.FlussoPcm(lambda uscita, alla_fine: m.passaggio_in_pcm(brano, None, None, uscita, alla_fine))
        assert flusso.read(100).startswith(b"RIFF") and flusso.read(65536)
        # libmpv riempie la pipe e resta fermo a scrivere.
        time.sleep(0.3)
        flusso.close()
    assert _aspetta(lambda: not vivi("MeTeOra, fine della diretta convertita") and not vivi("MeTeOra, pipe della diretta convertita")
                    and vivi("MPVEventHandlerThread") == libmpv, 20)


def test_un_rinnovo_lento_non_fa_aspettare_gli_altri_brani(monkeypatch):
    # Il lucchetto dei rinnovi era uno per tutti, preso anche solo per
    # guardare se il flusso era pronto: il rinnovo di un video, fino a 60
    # secondi con yt-dlp, faceva aspettare la sonda e il convertitore degli
    # altri brani, gia' pronti, e delle TV. Ora aspetta solo chi chiede lo
    # stesso indirizzo, e yt-dlp si chiama una volta sola.
    import indirizzi

    scaduto = "https://www.youtube.com/watch?v=rinnovo_lento"
    pronto = "https://www.youtube.com/watch?v=gia_pronto"
    tv = "https://tv.example/diretta_del_rinnovo.m3u8"
    indirizzi._tieni(pronto, False, indirizzi.Flusso("https://googlevideo.example/pronto", pezzo=10485760))
    indirizzi.metti_il_diretto(tv, dal_vivo=True)
    via, chiamate = threading.Event(), []

    def risolvi_lento(indirizzo, video=False):
        chiamate.append(indirizzo)
        assert via.wait(10)
        flusso = indirizzi.Flusso("https://googlevideo.example/nuovo", pezzo=10485760)
        indirizzi._tieni(indirizzo, video, flusso)
        return indirizzi.Pagina(indirizzo, None, flusso=flusso)

    monkeypatch.setattr(indirizzi, "risolvi", risolvi_lento)
    fili = [threading.Thread(target=modulo._flusso_per_il_convertitore, args=(scaduto,), daemon=True) for _ in range(2)]
    try:
        for filo in fili:
            filo.start()
        assert _aspetta(lambda: chiamate)
        for indirizzo in (pronto, tv):
            inizio = time.monotonic()
            modulo._flusso_per_il_convertitore(indirizzo)
            assert time.monotonic() - inizio < 0.5, indirizzo
    finally:
        via.set()
        for filo in fili:
            filo.join(5)
    assert not any(filo.is_alive() for filo in fili)
    assert chiamate == [scaduto] and indirizzi.pronto(scaduto) is not None and scaduto not in modulo._rinnovi
    for indirizzo in (scaduto, pronto):
        indirizzi.dimentica(indirizzo)

