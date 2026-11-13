# MeTeOra, prototipi: i campioni dell'ascolto alla cieca di Voce chiara e Cuffia.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 13/11/2026: nasce per la issue 40, la tappa 19 d del piano: la scelta dei filtri con l'ascolto di Gabriele.

"""I campioni dell'ascolto alla cieca degli effetti per la voce e la cuffia.

Uso, dalla cartella di MeTeOra:
  python prototipi\\prepara_ascolto_effetti.py
Rende, con la libmpv di MeTeOra in modo codifica, dodici secondi di ogni
brano dei gruppi con ogni filtro candidato, in WAV a 48 kHz, 16 bit e
stereo, in CAMPIONI, fuori dal repository. Ogni campione parte cinque
secondi prima e i primi cinque si tolgono, perche' i filtri che si adattano,
come speechnorm e arnndn, siano gia' a regime. Poi, gruppo per gruppo, tutti
i candidati si portano alla stessa sonorita' integrata, misurata come dice
la ITU-R BS.1770, cosi' nessuno vince perche' suona piu' forte; se un
candidato passerebbe il picco massimo, scende tutto il gruppo insieme. Il
manifesto, con i guadagni e le sonorita', va in CAMPIONI\\campioni.json.
I parlati partono dal punto del brano dove la voce e' piu' continua, cercato
intorno a quello indicato; la musica dal punto indicato.
"""

import json
import os
import sys
import threading
import wave

import numpy as np
from scipy.signal import lfilter

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, RADICE)
import motore  # noqa: E402

# libmpv la carica motore, che le prepara il percorso della DLL.
mpv = motore.mpv

CAMPIONI = r"E:\git\tmp\meteora-effetti\ascolto"
MODELLI = r"E:\git\tmp\meteora-effetti\scaricati"
FREQUENZA = 48000
DURATA = 12.0
RINCORSA = 5.0
SONORITA = -20.0
PICCO = 0.97
# Intorno al punto indicato, quanti secondi si guardano per trovare la voce piu' continua.
INTORNO = 60.0


def per_lavfi(percorso):
    """Un percorso di Windows come lo vuole un'opzione di un filtro dentro
    lavfi di mpv: barre in avanti e i due punti con due escape, uno per la
    descrizione del grafo e uno per l'opzione (prova del 13 novembre 2026)."""
    return percorso.replace("\\", "/").replace(":", "\\\\:")


RNN = per_lavfi(os.path.join(MODELLI, "sh.rnnn"))
SOFA = per_lavfi(os.path.join(MODELLI, "mit_kemar_normal_pinna.sofa"))
SPEECHNORM = "speechnorm=e=12.5:r=0.0001:l=1"
# Le due prove: i candidati, nome e catena, e i gruppi, nome, titolo, brano,
# secondo di partenza e se e' un parlato.
PROVE = {
    "cuffia": {
        "candidati": {
            "spenta": "",
            "bs2b": "bs2b=profile=default",
            "bs2b_cmoy": "bs2b=profile=cmoy",
            "bs2b_jmeier": "bs2b=profile=jmeier",
            "sofalizer": f"sofalizer=sofa={SOFA}:type=freq",
        },
        "gruppi": [
            ("california", "California Girls, dei Beach Boys", r"E:\Music\Beach Boys\Sounds of Summer Very Best Of\01 California Girls.m4a", 40.0, False),
            ("robinson", "Mrs. Robinson, di Simon & Garfunkel", r"E:\Music\Simon & Garfunkle\Unknown Album\Mrs. Robinson.m4a", 50.0, False),
            ("money", "Money, dei Pink Floyd", r"E:\Music\Pink Floyd\The Dark Side Of The Moon\05 Money.m4a", 60.0, False),
        ],
    },
    "voce": {
        "candidati": {
            "spenta": "",
            "arnndn": f"arnndn=m={RNN}",
            "speechnorm": SPEECHNORM,
            "arnndn_speechnorm": f"arnndn=m={RNN},{SPEECHNORM}",
        },
        "gruppi": [
            ("story_time", "un parlato alla radio, Story Time di CanaleItalia", r"E:\Audio\Miei interventi\CanaleItalia - Story Time 23 ottobre 2024.mp3", 270.0, True),
            ("chess_cli", "una presentazione registrata, quella di Chess-CLI", r"E:\Audio\Miei interventi\Chess-CLI - Presentazione 20240808.mp3", 900.0, True),
            ("nemo", "un film audiodescritto, Alla ricerca di Nemo", r"E:\Audio\AudioDescritti\Alla ricerca di Nemo.mp3", 1200.0, True),
        ],
    },
}


def rendi(brano, inizio, durata, catena, uscita):
    """durata secondi del brano dai secondi inizio, con la catena lavfi data,
    in un WAV a FREQUENZA, 16 bit, stereo. Torna gli errori di libmpv."""
    opzioni = {**motore.OPZIONI_DI_BASE, "o": uscita, "of": "wav", "oac": "pcm_s16le", "audio_samplerate": FREQUENZA,
        "audio_channels": "stereo", "start": f"{inizio:.3f}", "length": f"{durata:.3f}"}
    if catena:
        opzioni["af"] = f"lavfi=[{catena}]"
    errori = []
    lettore = mpv.MPV(log_handler=lambda livello, _prefisso, testo: errori.append(testo.strip()) if livello in ("error", "fatal") else None,
        loglevel="warn", **opzioni)
    finito = threading.Event()
    lettore.register_event_callback(lambda e: finito.set() if e.event_id.value == mpv.MpvEventID.END_FILE else None)
    try:
        lettore.command("loadfile", brano)
        finito.wait(120)
    finally:
        lettore.terminate()
    return errori


def leggi(file):
    with wave.open(file, "rb") as w:
        if (w.getframerate(), w.getnchannels(), w.getsampwidth()) != (FREQUENZA, 2, 2):
            raise ValueError(f"{file}: non e' un WAV a {FREQUENZA} Hz, stereo, 16 bit")
        dati = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768
    return dati.reshape(-1, 2)


def scrivi(file, dati):
    pcm = np.clip(np.round(dati * 32767), -32768, 32767).astype("<i2")
    with wave.open(file, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(FREQUENZA)
        w.writeframes(pcm.tobytes())


def sonorita(dati):
    """La sonorita' integrata in LUFS della ITU-R BS.1770-4, a 48 kHz: il
    filtro K in due stadi, blocchi di 400 ms ogni 100 ms, il cancello
    assoluto a -70 e quello relativo a 10 LU sotto."""
    pesati = lfilter([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585], dati, axis=0)
    pesati = lfilter([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621], pesati, axis=0)
    blocco, passo = int(0.4 * FREQUENZA), int(0.1 * FREQUENZA)
    energie = np.array([np.sum(np.mean(pesati[i:i + blocco] ** 2, axis=0)) for i in range(0, len(pesati) - blocco + 1, passo)])
    livelli = -0.691 + 10 * np.log10(np.maximum(energie, 1e-12))
    sopra = energie[livelli > -70]
    if not len(sopra):
        return -70.0
    relativo = -0.691 + 10 * np.log10(np.mean(sopra)) - 10
    tenuti = energie[(livelli > -70) & (livelli > relativo)]
    return float(-0.691 + 10 * np.log10(np.mean(tenuti)))


def voce_piu_continua(brano, punto, cartella):
    """Il secondo di partenza, intorno a punto, della finestra di DURATA con
    meno pause: dei blocchi da 50 ms, quella con meno blocchi a 30 dB sotto
    la mediana."""
    prova = os.path.join(cartella, "_intorno.wav")
    inizio = max(0.0, punto - INTORNO)
    rendi(brano, inizio, 2 * INTORNO, "", prova)
    dati = leggi(prova).mean(axis=1)
    os.remove(prova)
    blocco = int(0.05 * FREQUENZA)
    rms = np.sqrt(np.array([np.mean(dati[i:i + blocco] ** 2) for i in range(0, len(dati) - blocco + 1, blocco)]) + 1e-12)
    silenzio = rms < np.median(rms) * 10 ** (-30 / 20)
    finestra = int(DURATA / 0.05)
    pause = np.convolve(silenzio.astype(int), np.ones(finestra, dtype=int), "valid")
    migliore = int(np.argmin(pause))
    return inizio + migliore * 0.05


def prepara():
    manifesto = {}
    for prova, dati_della_prova in PROVE.items():
        manifesto[prova] = {}
        for gruppo, titolo, brano, punto, parlato in dati_della_prova["gruppi"]:
            cartella = os.path.join(CAMPIONI, prova, gruppo)
            os.makedirs(cartella, exist_ok=True)
            partenza = voce_piu_continua(brano, punto, cartella) if parlato else punto
            grezzi = {}
            for candidato, catena in dati_della_prova["candidati"].items():
                file = os.path.join(cartella, f"{candidato}.wav")
                errori = rendi(brano, max(0.0, partenza - RINCORSA), DURATA + RINCORSA, catena, file)
                if errori:
                    raise RuntimeError(f"{prova} {gruppo} {candidato}: {errori[:3]}")
                dati = leggi(file)
                togli = int(min(RINCORSA, partenza) * FREQUENZA)
                grezzi[candidato] = dati[togli:togli + int(DURATA * FREQUENZA)]
            misure = {c: sonorita(d) for c, d in grezzi.items()}
            guadagni = {c: 10 ** ((SONORITA - misure[c]) / 20) for c in grezzi}
            picco = max(float(np.max(np.abs(grezzi[c]))) * guadagni[c] for c in grezzi)
            correzione = min(1.0, PICCO / picco)
            for candidato, dati in grezzi.items():
                scrivi(os.path.join(cartella, f"{candidato}.wav"), dati * guadagni[candidato] * correzione)
            dopo = {c: sonorita(leggi(os.path.join(cartella, f"{c}.wav"))) for c in grezzi}
            manifesto[prova][gruppo] = {"titolo": titolo, "brano": brano, "partenza": round(partenza, 2),
                "sonorita_di_partenza": {c: round(v, 2) for c, v in misure.items()},
                "guadagni_db": {c: round(20 * np.log10(guadagni[c] * correzione), 2) for c in grezzi},
                "sonorita_finali": {c: round(v, 2) for c, v in dopo.items()}}
            print(f"{prova}, {gruppo}: da {partenza:.1f} s; sonorita' finali {', '.join(f'{c} {v:.1f}' for c, v in dopo.items())}", flush=True)
    with open(os.path.join(CAMPIONI, "campioni.json"), "w", encoding="utf-8") as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=1)
    return manifesto


if __name__ == "__main__":
    prepara()
