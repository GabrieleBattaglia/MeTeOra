# MeTeOra, prototipi: l'ascolto alla cieca dei filtri candidati per Voce chiara e Cuffia.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 13/11/2026: nasce per la issue 40, la tappa 19 d del piano, sul modello di ascolto_registrazioni.py.

"""L'ascolto alla cieca dei filtri per la cuffia e per la voce.

Uso, dalla cartella di MeTeOra, con il via di Gabriele:
  python prototipi\\ascolto_effetti.py cuffia [PAROLA]
  python prototipi\\ascolto_effetti.py voce [PAROLA]
La prova della cuffia suona sulla cuffia G325, quella della voce sugli
altoparlanti Realtek, con WASAPI, senza toccare l'uscita predefinita di
Windows; se l'uscita non c'e', su quella predefinita. Con una parola fa sentire
soltanto i gruppi il cui titolo la contiene.

Tre gruppi per prova, uno per brano. In ogni gruppo i candidati, piu' uno di
loro ripetuto, estratto a caso, si danno alle lettere a caso: chi ascolta
non sa quale sia quale, ne' quale sia ripetuto. Prima la rassegna, come vuole
Gabriele quando i candidati sono meno di otto: tutti di fila, una volta
ciascuno, dopo la loro lettera. Poi un candidato alla volta, la lettera e due
ascolti, e il voto da 1 a 5: r lo riascolta, Escape lo lascia senza voto. Il
gruppo si chiude con il menu comune dei collaudi: r riascolta la rassegna, c
commenta, Invio lo da' per superato.
I campioni li prepara prepara_ascolto_effetti.py, tutti alla stessa
sonorita' dentro il gruppo; il volume e' quello dell'uscita. Gli esiti, con le
lettere sciolte, vanno in prototipi\\ascolto_effetti_esiti.txt, con in fondo
il riepilogo dei voti per candidato e per gruppo, e i due voti del candidato
ripetuto; a schermo, durante l'ascolto, niente nomi ne' numeri.
"""

import json
import os
import random
import sys
import time
import wave

import collaudo_comune as comune
import numpy as np
from GBUtils import enter_escape, key

QUI = os.path.dirname(os.path.abspath(__file__))
CAMPIONI = r"E:\git\tmp\meteora-effetti\ascolto"
ESITI = os.path.join(QUI, "ascolto_effetti_esiti.txt")
INTESTAZIONE = "MeTeOra: ascolto alla cieca dei filtri per la cuffia e per la voce, issue 40.\n"
PROVE = {
    "cuffia": ("la cuffia", ("spenta", "bs2b", "bs2b_cmoy", "bs2b_jmeier", "sofalizer"), ("california", "robinson", "money")),
    "voce": ("la voce", ("spenta", "arnndn", "speechnorm", "arnndn_speechnorm"), ("story_time", "chess_cli", "nemo")),
}
# L'uscita di ogni prova, scelta da Gabriele il 13 novembre 2026 per non
# passare dal mixer: la cuffia G325 e gli altoparlanti Realtek, con WASAPI.
USCITE = {"cuffia": "G325", "voce": "Altoparlanti (Realtek"}
INTERFACCIA = "Windows WASAPI"
# L'uscita scelta, come numero di sounddevice, o None per la predefinita.
_uscita = None


def trova_l_uscita(nome):
    """Il numero e il nome dell'uscita WASAPI il cui nome contiene nome, o
    (None, None) se non c'e'."""
    import sounddevice

    for numero, info in enumerate(sounddevice.query_devices()):
        if info["max_output_channels"] >= 2 and nome in info["name"] and sounddevice.query_hostapis(info["hostapi"])["name"] == INTERFACCIA:
            return numero, info["name"]
    return None, None
LETTERE = "ABCDEFGH"
ASCOLTI = 2
VOTI = "12345"
SILENZIO_INIZIALE = 4.0
# Dopo la lettera, perche' la sintesi finisca di dirla prima del suono.
SILENZIO_LETTERA = 1.5
SILENZIO_RASSEGNA = 2.0
SILENZIO_CANDIDATO = 2.0
SILENZIO_FRA_ASCOLTI = 2.5


# Le porte verso il mondo, che la prova del banco sostituisce: suono, attesa e
# tastiera. Il menu di fine gruppo usa quelle di collaudo_comune.
def suona(file):
    import sounddevice

    with wave.open(file, "rb") as w:
        frequenza = w.getframerate()
        dati = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").reshape(-1, w.getnchannels())
    # Con WASAPI condiviso la frequenza e' quella della scheda: se e' un'altra,
    # come i 44.1 kHz degli altoparlanti Realtek, la converte Windows.
    extra = sounddevice.WasapiSettings(auto_convert=True) if _uscita is not None else None
    sounddevice.play(dati.astype(np.float32) / 32768, frequenza, device=_uscita, extra_settings=extra)
    sounddevice.wait()


def pausa(secondi):
    time.sleep(secondi)


def tasto(prompt):
    return key(prompt)


def via(prompt):
    return enter_escape(prompt)


def campione(prova, gruppo, candidato):
    return os.path.join(CAMPIONI, prova, gruppo, f"{candidato}.wav")


def titoli(percorso=None):
    """I titoli dei gruppi, dal manifesto dei campioni."""
    with open(percorso or os.path.join(CAMPIONI, "campioni.json"), encoding="utf-8") as f:
        manifesto = json.load(f)
    return {(prova, gruppo): voce["titolo"] for prova, gruppi in manifesto.items() for gruppo, voce in gruppi.items()}


def scrivi(testo):
    with open(ESITI, "a", encoding="utf-8") as f:
        f.write(testo)


def lettere_a_caso(candidati, caso):
    """Le coppie (lettera, candidato), con i candidati e uno di loro ripetuto,
    tutti in ordine a caso."""
    voci = [*candidati, caso.choice(candidati)]
    caso.shuffle(voci)
    return list(zip(LETTERE, voci, strict=False))


def rassegna(prova, gruppo, scelte):
    """Tutti i candidati di fila, una volta ciascuno, dopo la loro lettera."""
    print("Rassegna.")
    pausa(SILENZIO_LETTERA)
    for numero, (lettera, candidato) in enumerate(scelte, 1):
        print(f"{lettera}.")
        pausa(SILENZIO_LETTERA)
        suona(campione(prova, gruppo, candidato))
        if numero < len(scelte):
            pausa(SILENZIO_RASSEGNA)
    print("Fine della rassegna.")


def ascolti(file):
    for volta in range(ASCOLTI):
        suona(file)
        if volta < ASCOLTI - 1:
            pausa(SILENZIO_FRA_ASCOLTI)


def voto(lettera, riproduci):
    """Il voto di un candidato, da 1 a 5, o None con Escape; r riascolta."""
    while True:
        scelta = tasto(f"\rVoto per {lettera} da 1 a 5, r ripete, Esc salta\r")
        print()
        if len(scelta) == 1 and scelta in VOTI:
            return int(scelta)
        if scelta in ("r", "R"):
            riproduci()
        elif scelta == "\x1b":
            return None
        else:
            print("Da 1 a 5, r o Escape.")


def ascolta_il_gruppo(numero, quanti, prova, gruppo, titolo, candidati, esiti, caso):
    """Un gruppo: annuncio, rassegna, ogni lettera con il suo voto, e il menu.
    Restituisce le coppie (lettera, candidato, voto), o None se si salta."""
    scelte = lettere_a_caso(candidati, caso)
    if not comune.gruppo(f"{numero} di {quanti}, {titolo}", len(scelte), "lettere"):
        return None
    pausa(SILENZIO_CANDIDATO)
    rassegna(prova, gruppo, scelte)
    voti = []
    for lettera, candidato in scelte:
        file = campione(prova, gruppo, candidato)
        print(f"Lettera {lettera}, {ASCOLTI} volte.")
        pausa(SILENZIO_CANDIDATO)
        ascolti(file)
        voti.append((lettera, candidato, voto(lettera, lambda file=file: ascolti(file))))
    misura = "; ".join(f"{lettera} {candidato}, {'senza voto' if v is None else f'voto {v}'}" for lettera, candidato, v in voti)
    esiti.esito(f"{numero} di {quanti}, {titolo}, gruppo {gruppo}", riproduci=lambda: rassegna(prova, gruppo, scelte), misura=misura)
    return voti


def riepilogo(candidati, tutti):
    """Le righe del riepilogo. tutti e' {gruppo: [(lettera, candidato, voto)]}:
    per gruppo i voti dal migliore; poi la somma e la media di ogni
    candidato, contando il ripetuto una volta sola, con il primo voto; poi i
    due voti del ripetuto di ogni gruppo, che dicono quanto i voti tengono."""
    righe, somme, conti, ripetuti = [], dict.fromkeys(candidati, 0), dict.fromkeys(candidati, 0), []
    for gruppo, voti in tutti.items():
        ordinati = sorted(voti, key=lambda v: -(v[2] or 0))
        righe.append(f"{gruppo}: " + ", ".join(f"{c} ({lettera}) {'senza voto' if v is None else v}" for lettera, c, v in ordinati) + ".")
        visti = {}
        for lettera, candidato, v in voti:
            if candidato in visti:
                ripetuti.append(f"{gruppo}, {candidato}: {visti[candidato][0]} {visti[candidato][1]} e {lettera} {v}")
                continue
            visti[candidato] = (lettera, v)
            if v is not None:
                somme[candidato] += v
                conti[candidato] += 1
    ordine = sorted(candidati, key=lambda c: -somme[c])
    righe.append("Somme: " + ", ".join(f"{c} {somme[c]}" + (f", media {somme[c] / conti[c]:.1f}" if conti[c] else "") for c in ordine) + ".")
    righe.append("Il candidato ripetuto, per gruppo: " + ("; ".join(ripetuti) or "nessuno") + ".")
    return righe


def main(argomenti=None):
    argomenti = list(sys.argv[1:] if argomenti is None else argomenti)
    if not argomenti or argomenti[0] not in PROVE:
        print("Uso: python prototipi\\ascolto_effetti.py cuffia|voce [parola]")
        return 1
    prova, parola = argomenti[0], " ".join(argomenti[1:]).strip().casefold()
    nome, candidati, gruppi_della_prova = PROVE[prova]
    try:
        nomi = titoli()
    except (OSError, ValueError):
        print(f"Mancano i campioni in {CAMPIONI}: prima prepara_ascolto_effetti.py.")
        return 1
    gruppi = [(g, nomi[(prova, g)]) for g in gruppi_della_prova if parola in nomi[(prova, g)].casefold()]
    if not gruppi:
        print(f"Nessun gruppo contiene {parola}.")
        return 1
    mancanti = [campione(prova, g, c) for g, _t in gruppi for c in candidati if not os.path.exists(campione(prova, g, c))]
    if mancanti:
        print(f"Mancano {len(mancanti)} campioni, come {mancanti[0]}.")
        return 1
    global _uscita
    _uscita, nome_dell_uscita = trova_l_uscita(USCITE[prova])
    if _uscita is None:
        print(f"Non trovo l'uscita {USCITE[prova]}: suono su quella predefinita di Windows.")
    quante = len(candidati) + 1
    print(f"Ascolto alla cieca dei filtri per {nome}: {len(gruppi)} gruppi, uno per brano, con {quante} lettere ciascuno, di dodici secondi.")
    if _uscita is not None:
        print(f"Suona su {nome_dell_uscita}.")
    print("Le lettere cambiano a caso a ogni gruppo. Ogni gruppo si annuncia, e Escape lo salta.")
    print(f"Prima la rassegna: le {quante} lettere di fila, ognuna dopo {SILENZIO_LETTERA:g} secondi di silenzio, con {SILENZIO_RASSEGNA:g} secondi dopo ogni suono. "
          "Durante la prima rassegna puoi regolare il volume.")
    print(f"Poi una lettera alla volta: la lettera, {SILENZIO_CANDIDATO:g} secondi, e {ASCOLTI} ascolti con {SILENZIO_FRA_ASCOLTI:g} secondi fra l'uno e l'altro; "
          "poi il voto da 1 a 5, dove 3 vuol dire che va bene ma non ti colpisce.")
    print("Al voto r riascolta la lettera, Escape la lascia senza voto. A fine gruppo r riascolta la rassegna, c commenta, Invio lo da' per superato.")
    if not via("\rInvio per cominciare, Escape per uscire\r"):
        return 0
    pausa(SILENZIO_INIZIALE)
    inizio = time.strftime("%Y-%m-%d %H:%M")
    if not os.path.exists(ESITI):
        scrivi(INTESTAZIONE)
    scrivi(f"\nProva di {nome}, sessione del {inizio}\n")
    esiti = comune.Esiti(ESITI)
    caso = random.Random()  # noqa: S311 - lettere a caso per l'ascolto, non crittografia
    tutti = {}
    try:
        for numero, (gruppo, titolo) in enumerate(gruppi, 1):
            voti = ascolta_il_gruppo(numero, len(gruppi), prova, gruppo, titolo, candidati, esiti, caso)
            if voti is not None:
                tutti[gruppo] = voti
    except KeyboardInterrupt:
        print()
        print("Interrotto.")
    if tutti:
        scrivi(f"\nRIEPILOGO DEI VOTI, prova di {nome}, sessione del {inizio}\n" + "".join(f"{riga}\n" for riga in riepilogo(candidati, tutti)))
    print(f"Fine dell'ascolto. Gli esiti sono in {os.path.basename(ESITI)}, nella cartella prototipi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
