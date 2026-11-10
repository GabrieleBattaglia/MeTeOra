# MeTeOra, prototipi: l'ascolto alla cieca dei suoni candidati delle registrazioni.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 10/11/2026: nasce con la 3.5.1, per scegliere i suoni della issue 42, che nella 3.5.0 suonano segnaposto.

"""L'ascolto alla cieca dei suoni delle registrazioni.

Uso, dalla cartella di MeTeOra, con il via di Gabriele:
  python prototipi\\ascolto_registrazioni.py [PAROLA]
Con una parola fa sentire soltanto i gruppi il cui titolo la contiene, per
esempio pausa.

Otto gruppi, uno per evento delle registrazioni, nell'ordine in cui
capitano, con tre candidati ciascuno, in tre stili: nastro, triangolo che
scivola; spia, seno che lampeggia; soffio, rumore filtrato. Le lettere A, B e
C si danno a caso a ogni gruppo: chi ascolta non sa quale sia quale. Il
gruppo si annuncia, con il tasto che fa suonare l'evento, e si puo' saltare.
Prima la rassegna, come vuole Gabriele quando i candidati sono meno di otto:
i tre di fila, una volta ciascuno, dopo la loro lettera, senza domande. Poi
un candidato alla volta, la lettera e tre ascolti, e il voto da 1 a 5: r lo
riascolta, Escape lo lascia senza voto. Il gruppo si chiude con il menu
comune dei collaudi: r riascolta la rassegna, c commenta, Invio lo da' per
superato.
I candidati stanno in prototipi\\ascolto_registrazioni.json, una collezione
nel formato di quella di GBUtils, che l'ascolto legge senza toccare quella
condivisa. Il volume e' quello degli effetti di MeTeOra. Gli esiti, con le
lettere sciolte, vanno in prototipi\\ascolto_registrazioni_esiti.txt, con in
fondo il riepilogo dei voti per evento e per stile; a schermo, durante
l'ascolto, niente nomi ne' numeri.
"""

import json
import os
import random
import sys
import time

import collaudo_comune as comune
from GBUtils import Acusticator, enter_escape, key

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
CANDIDATI = os.path.join(QUI, "ascolto_registrazioni.json")
ESITI = os.path.join(QUI, "ascolto_registrazioni_esiti.txt")
IMPOSTAZIONI = os.path.join(RADICE, "MeTeOra - Impostazioni.json")
INTESTAZIONE = "MeTeOra: ascolto alla cieca dei suoni delle registrazioni, issue 42.\n"
# Gli eventi nell'ordine in cui capitano, con il titolo del gruppo.
GRUPPI = (
    ("registrazione_avviata", "la registrazione comincia, con Maiuscolo e R"),
    ("registrazione_in_pausa", "la registrazione va in pausa, con Maiuscolo e R"),
    ("registrazione_ripresa", "la registrazione riprende dalla pausa, con Maiuscolo e R"),
    ("registrazione_fermata", "la registrazione si ferma e il file si chiude, con Ctrl e R"),
    ("registrazione_in_ascolto", "in ascolto per registrare la prossima radio che parte, con Alt e R"),
    ("registrazione_eliminata", "la registrazione in corso si elimina, con Alt, Maiuscolo e R"),
    ("alle_registrazioni", "la plancia va al ramo Registrazioni, con Ctrl, Maiuscolo e R"),
    ("cartella_delle_registrazioni", "si apre la cartella delle registrazioni, con Ctrl, Alt e R"),
)
STILI = ("nastro", "spia", "soffio")
LETTERE = "ABC"
ASCOLTI = 3
VOTI = "12345"
SILENZIO_INIZIALE = 4.0
# Dopo la lettera, perche' la sintesi finisca di dirla prima del suono.
SILENZIO_LETTERA = 1.5
SILENZIO_RASSEGNA = 2.0
SILENZIO_CANDIDATO = 2.0
SILENZIO_FRA_ASCOLTI = 2.5


# Le porte verso il mondo, che la prova del banco sostituisce: suono, attesa e
# tastiera. Il menu di fine gruppo usa quelle di collaudo_comune.
def suona(nome, volume):
    Acusticator.play(nome, sync=True, volume=volume)


def pausa(secondi):
    time.sleep(secondi)


def tasto(prompt):
    return key(prompt)


def via(prompt):
    return enter_escape(prompt)


def scalda():
    """Apre il flusso audio con una pausa muta, cosi' il primo suono vero non
    paga il tempo d'apertura."""
    Acusticator(["p", 0.05, 0, 0], sync=True)


def preset(evento, stile):
    return f"candidato_{evento}_{stile}"


def volume_di_meteora(percorso=IMPOSTAZIONI):
    """Il volume degli effetti delle impostazioni di MeTeOra, da 0 a 1; 0.5
    se il file manca, non si legge, o gli effetti sono muti."""
    try:
        with open(percorso, encoding="utf-8") as f:
            volume = float(json.load(f).get("volume_effetti", 0.5))
    except (OSError, ValueError, AttributeError, TypeError):
        volume = 0.5
    return volume if 0 < volume <= 1 else 0.5


def scrivi(testo):
    with open(ESITI, "a", encoding="utf-8") as f:
        f.write(testo)


def rassegna(evento, candidati, volume):
    """I tre candidati di fila, una volta ciascuno, dopo la loro lettera."""
    print("Rassegna.")
    pausa(SILENZIO_LETTERA)
    for numero, (lettera, stile) in enumerate(candidati, 1):
        print(f"{lettera}.")
        pausa(SILENZIO_LETTERA)
        suona(preset(evento, stile), volume)
        if numero < len(candidati):
            pausa(SILENZIO_RASSEGNA)
    print("Fine della rassegna.")


def tre_ascolti(nome, volume):
    for volta in range(ASCOLTI):
        suona(nome, volume)
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


def ascolta_il_gruppo(numero, quanti, evento, titolo, volume, esiti, caso):
    """Un gruppo: annuncio, rassegna, i tre candidati con il loro voto, e il
    menu. Restituisce i voti per stile, o None se il gruppo si salta."""
    stili = list(STILI)
    caso.shuffle(stili)
    candidati = list(zip(LETTERE, stili, strict=True))
    if not comune.gruppo(f"{numero} di {quanti}, {titolo}", len(candidati), "candidati"):
        return None
    pausa(SILENZIO_CANDIDATO)
    rassegna(evento, candidati, volume)
    voti = {}
    for lettera, stile in candidati:
        nome = preset(evento, stile)
        print(f"Candidato {lettera}, tre volte.")
        pausa(SILENZIO_CANDIDATO)
        tre_ascolti(nome, volume)
        voti[stile] = voto(lettera, lambda nome=nome: tre_ascolti(nome, volume))
    misura = "; ".join(f"{lettera} {stile}, {'senza voto' if voti[stile] is None else f'voto {voti[stile]}'}" for lettera, stile in candidati)
    esiti.esito(f"{numero} di {quanti}, {titolo}, evento {evento}", riproduci=lambda: rassegna(evento, candidati, volume), misura=misura)
    return voti


def riepilogo(tutti):
    """Le righe del riepilogo: per evento i voti degli stili, dal migliore,
    poi la somma di ogni stile. tutti e' {evento: {stile: voto}}."""
    righe = []
    somme = dict.fromkeys(STILI, 0)
    for evento, voti in tutti.items():
        ordinati = sorted(STILI, key=lambda s: -(voti[s] or 0))
        righe.append(f"{evento}: " + ", ".join(f"{s} {'senza voto' if voti[s] is None else voti[s]}" for s in ordinati) + ".")
        for stile in STILI:
            somme[stile] += voti[stile] or 0
    righe.append("Somme: " + ", ".join(f"{s} {somme[s]}" for s in STILI) + ".")
    return righe


def main(argomenti=None):
    parola = " ".join(sys.argv[1:] if argomenti is None else argomenti).strip().casefold()
    gruppi = [(evento, titolo) for evento, titolo in GRUPPI if parola in titolo.casefold()]
    if not gruppi:
        print(f"Nessun gruppo contiene {parola}.")
        return 1
    if not Acusticator.collezione(CANDIDATI):
        print(f"Mancano i candidati, {CANDIDATI}.")
        return 1
    volume = volume_di_meteora()
    print(f"Ascolto alla cieca dei suoni delle registrazioni: {len(gruppi)} gruppi, uno per evento, con 3 candidati ciascuno.")
    print("Le lettere A, B e C cambiano a caso a ogni gruppo. Ogni gruppo si annuncia, e Escape lo salta.")
    print(f"Prima la rassegna: i tre candidati di fila, ognuno dopo la sua lettera e {SILENZIO_LETTERA:g} secondi di silenzio, con {SILENZIO_RASSEGNA:g} secondi dopo ogni suono.")
    print(f"Poi un candidato alla volta: la lettera, {SILENZIO_CANDIDATO:g} secondi, e tre ascolti con {SILENZIO_FRA_ASCOLTI:g} secondi fra l'uno e l'altro; poi il voto da 1 a 5.")
    print("Al voto r riascolta il candidato, Escape lo lascia senza voto. A fine gruppo r riascolta la rassegna, c commenta, Invio lo da' per superato.")
    print(f"Volume degli effetti di MeTeOra: {round(volume * 100)}%.")
    if not via("\rInvio per cominciare, Escape per uscire\r"):
        return 0
    scalda()
    pausa(SILENZIO_INIZIALE)
    inizio = time.strftime("%Y-%m-%d %H:%M")
    if not os.path.exists(ESITI):
        scrivi(INTESTAZIONE)
    scrivi(f"\nSessione del {inizio}, volume {round(volume * 100)}%\n")
    esiti = comune.Esiti(ESITI)
    caso = random.Random()  # noqa: S311 - lettere a caso per l'ascolto, non crittografia
    tutti = {}
    try:
        for numero, (evento, titolo) in enumerate(gruppi, 1):
            voti = ascolta_il_gruppo(numero, len(gruppi), evento, titolo, volume, esiti, caso)
            if voti is not None:
                tutti[evento] = voti
    except KeyboardInterrupt:
        print()
        print("Interrotto.")
    if tutti:
        scrivi(f"\nRIEPILOGO DEI VOTI, sessione del {inizio}\n" + "".join(f"{riga}\n" for riga in riepilogo(tutti)))
    print(f"Fine dell'ascolto. Gli esiti sono in {os.path.basename(ESITI)}, nella cartella prototipi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
