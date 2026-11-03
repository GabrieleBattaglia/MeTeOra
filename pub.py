# MeTeOra, le parole delle due voci del PUB, il gruppo di supporto: la mail che iscrive e quella che chiede aiuto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/11/2026: nasce con la 2.1.0, issue 30. Nella 2.4.0 i registri degli errori, ripuliti, da allegare alla richiesta d'aiuto.

"""Entra al PUB e Chiedi aiuto al PUB, le voci delle impostazioni accanto a
Dona per questo progetto (issue 30, richiesta di Gabriele del 21 ottobre
2026, per tutti i programmi del parco che hanno una finestra).

Gli indirizzi, le informazioni sul computer e la composizione della mail
vengono da GBUtils, la finestra che la prepara da GBwx, finestra_mail: qui
ci sono soltanto le parole di MeTeOra, perche' GBUtils non ne ha di sue. La
finestra si apre sempre, anche quando il programma di posta c'e', perche' il
nuovo Outlook di Windows 11 e' spesso associato a mailto anche per chi non lo
usa; senza posta accompagna l'utente un passo alla volta, copiando negli
appunti un campo per volta. MeTeOra non spedisce mai niente: spedisce
l'utente, se vuole, dopo aver letto e corretto.
Dalla 2.4.0 la richiesta d'aiuto ha la casella dei registri (Gabriele, 3
novembre 2026): spuntata, MeTeOra scrive accanto al programma un file con il
registro degli errori e i resoconti dei crash, ripuliti dal nome dell'utente
di Windows e del computer, e la mail dice di allegarlo; mailto gli allegati
non li porta, e il percorso del file va negli appunti, da incollare nella
finestra Allega del programma di posta.
"""

import glob
import os
import re
import time

PULSANTI = {"apri": "&Apri nel programma di posta", "passi": "&Passo per passo", "ok": "&OK", "chiudi": "&Chiudi", "annulla": "&Annulla"}
SENZA_POSTA = ("Non trovo un programma di posta, oppure non si è aperto: prepariamo la mail un pezzo alla volta, da incollare nella tua "
    "posta, per esempio nella webmail del browser.")
# Le informazioni del computer nella mail d'aiuto, nell'ordine in cui
# compaiono; quelle che non si leggono restano fuori. Se il programma e'
# compilato lo dice gia' la riga del programma.
ETICHETTE = {
    "windows": "Sistema operativo",
    "windows_versione": "Versione di Windows",
    "windows_build": "Build di Windows",
    "architettura": "Architettura",
    "processore": "Processore",
    "nuclei": "Nuclei logici",
    "memoria_totale": "Memoria",
    "memoria_libera": "Memoria libera",
    "lingua": "Lingua di sistema",
    "screen_reader": "Screen reader",
    "schermo": "Schermo",
    "scala": "Scala dello schermo",
    "python": "Python",
}
PAROLE = {True: "sì", False: "no"}
_ALTRA_STRADA = ("Se la mail non compare, torna qui e scegli Passo per passo: ti guido a scriverla nella tua posta, per esempio nella webmail "
    "del browser.")
_ISCRIVITI = "Se non sei ancora iscritto al PUB, puoi farlo con Entra al PUB, nelle impostazioni."
# La casella dei registri, e il file che si allega (2.4.0).
CASELLA_DEI_REGISTRI = "&Includi anche i registri degli errori"
FILE_DEI_REGISTRI = "MeTeOra - Registri per il PUB.txt"
# Quanto si tiene della fine di ogni registro, in caratteri: gli ultimi
# problemi bastano a chi risponde, e la mail resta leggera.
CODA_DEGLI_ERRORI = 200_000
CODA_DI_UN_CRASH = 100_000
# I registri da allegare, nell'ordine in cui entrano nel file: il registro
# degli errori con la sua copia a rotazione, la piu' vecchia prima, e i
# resoconti dei crash, anche quelli di riserva con la data.
_ERRORI = ("MeTeOra - Errori.log.1", "MeTeOra - Errori.log")
_CRASH = "MeTeOra - Crash precedente*.log"


def registri_presenti(cartella):
    """I percorsi dei registri che ci sono e non sono vuoti, nella cartella
    del programma: gli errori, poi i crash dal piu' vecchio."""
    errori = [os.path.join(cartella, nome) for nome in _ERRORI]
    crash = sorted(glob.glob(os.path.join(glob.escape(cartella), _CRASH)), key=lambda p: (os.path.getmtime(p), p))
    presenti = []
    for percorso in errori + crash:
        try:
            if os.path.getsize(percorso):
                presenti.append(percorso)
        except OSError:
            continue
    return presenti


def ripulisci(testo, utente, computer):
    """Il testo senza il nome dell'utente di Windows e del computer, che
    diventano <utente> e <computer>, senza badare alle maiuscole. Il nome
    del computer si toglie dovunque sia una parola intera; quello
    dell'utente solo accanto a un separatore dei percorsi, come in
    C:\\Users\\Gabriele\\Music, perche' puo' essere anche una parola
    comune, per esempio Utente, che nelle frasi deve restare."""
    if computer:
        testo = re.sub(rf"(?i)(?<![\w-]){re.escape(computer)}(?![\w-])", "<computer>", testo)
    if utente:
        nome = re.escape(utente)
        testo = re.sub(rf"(?i)(?<=[\\/]){nome}(?![\w-])|(?<![\w-]){nome}(?=[\\/])", "<utente>", testo)
    return testo


def _coda(percorso, quanti):
    """Gli ultimi caratteri di un file di testo, e se e' stato tagliato."""
    with open(percorso, encoding="utf-8", errors="replace") as f:
        testo = f.read()
    return testo[-quanti:], len(testo) > quanti


def scrivi_i_registri(cartella, versione, utente, computer):
    """Scrive nella cartella il file dei registri da allegare, ripulito, e
    ne restituisce il percorso; None se non c'e' nessun registro. Solleva
    OSError se il file non si scrive."""
    presenti = registri_presenti(cartella)
    if not presenti:
        return None
    righe = [f"Registri di MeTeOra {versione}, preparati il {time.strftime('%d/%m/%Y alle %H:%M')} per il PUB, "
             "ripuliti dal nome dell'utente di Windows e del computer."]
    errori = [p for p in presenti if os.path.basename(p) in _ERRORI]
    if errori:
        testo = "".join(_coda(p, CODA_DEGLI_ERRORI)[0] for p in errori)
        tagliato = len(testo) > CODA_DEGLI_ERRORI
        righe.append(f"Dal registro degli errori, {'la parte finale' if tagliato else 'tutto'}:")
        righe.append(testo[-CODA_DEGLI_ERRORI:].rstrip("\n"))
    for percorso in presenti:
        if percorso in errori:
            continue
        testo, tagliato = _coda(percorso, CODA_DI_UN_CRASH)
        righe.append(f"Dal resoconto del crash {os.path.basename(percorso)}, {'la parte finale' if tagliato else 'tutto'}:")
        righe.append(testo.rstrip("\n"))
    destinazione = os.path.join(cartella, FILE_DEI_REGISTRI)
    with open(destinazione, "w", encoding="utf-8") as f:
        f.write(ripulisci("\n".join(righe), utente, computer) + "\n")
    return destinazione


def mail_d_iscrizione():
    """Entra al PUB: le parole della mail che iscrive al gruppo. All'indirizzo
    dell'iscrizione Google non legge oggetto e testo, e risponde con una mail
    di conferma: nei passi basta l'indirizzo."""
    from GBUtils import PUB_ISCRIZIONE

    return {
        "titolo": "Entra al PUB, il gruppo di supporto",
        "destinatario": PUB_ISCRIZIONE,
        "oggetto": "Iscrizione al PUB",
        "corpo": "Invia questo messaggio così com'è per iscriverti al PUB. Google ti scriverà per chiederti di confermare.",
        "spiegazione": "\n".join((
            "Il PUB è il gruppo di supporto dei programmi di Gabriele Battaglia, una lista di posta su Google Groups, dove si chiede aiuto, si "
            "segnalano i problemi e si propongono idee.",
            "Il pulsante Apri nel programma di posta prepara in {programma} la mail che ti iscrive: spediscila così com'è, perché MeTeOra non "
            "spedisce niente da solo. Poi Google ti scriverà per chiederti di confermare l'iscrizione: segui le sue istruzioni.",
            _ALTRA_STRADA,
        )),
        "passi": (
            ("Passo 1 di 2. Scrivi una mail nuova nella tua posta, per esempio nella webmail del browser, e incolla nel campo A l'indirizzo "
             "dell'iscrizione, che ho copiato negli appunti; poi torna qui e premi OK. L'indirizzo è questo:", PUB_ISCRIZIONE),
            ("Passo 2 di 2. Oggetto e testo possono restare vuoti, perché Google non li legge: spedisci la mail così com'è. Google ti scriverà "
             "per chiederti di confermare l'iscrizione: segui le sue istruzioni. OK chiude questa finestra.", None),
        ),
    }


def mail_d_aiuto(versione, compilato, informazioni, scheda_audio=None, casella=False, registri=None):
    """Chiedi aiuto al PUB: le parole della mail al gruppo. L'oggetto dice la
    versione; il testo ha una prima riga da sostituire con la domanda e sotto
    le informazioni: il programma, con la versione e se gira compilato o dai
    sorgenti, la scheda audio con la sua interfaccia, utile per un lettore
    multimediale, e il computer, da informazioni_di_sistema di GBUtils con le
    etichette italiane. casella dice che la finestra ha la casella dei
    registri; registri e' il percorso del file da allegare, quando la
    casella e' spuntata: allora la mail lo dice, i passi sono cinque, e
    appunti e' il percorso, che Apri copia negli appunti (2.4.0)."""
    from GBUtils import PUB_GRUPPO, righe_informazioni

    oggetto = f"Chiedo per MeTeOra {versione}"
    corpo = "\n".join((
        "Scrivi qui la tua domanda, al posto di questa riga.",
        "Informazioni su MeTeOra e sul computer di chi scrive:",
        f"Programma: MeTeOra {versione}, {'pacchetto compilato' if compilato else 'dai sorgenti'}",
        *([f"Scheda audio: {scheda_audio}"] if scheda_audio else []),
        *righe_informazioni(ETICHETTE, informazioni, PAROLE),
        *(["In allegato i registri degli errori di MeTeOra, ripuliti dal nome dell'utente e del computer."] if registri else []),
    ))
    if registri:
        allegati = (f"Allega alla mail anche il file {FILE_DEI_REGISTRI}, che sta nella cartella {os.path.dirname(registri)}: quando la bozza "
            "è pronta ne trovi il percorso negli appunti, da incollare nella finestra Allega del programma di posta. Il file è ripulito dal nome "
            "del tuo utente di Windows e del computer; i percorsi dei brani restano, perché aiutano a capire l'errore.")
    elif casella:
        allegati = "Se vuoi allegare anche i registri degli errori di MeTeOra, ripuliti dal nome del tuo utente e del computer, spunta la casella qui sotto."
    else:
        allegati = ""
    totale = 5 if registri else 4
    passi = [
        (f"Passo 1 di {totale}. Scrivi una mail nuova nella tua posta, per esempio nella webmail del browser, e incolla nel campo A "
         "l'indirizzo del PUB, che ho copiato negli appunti; poi torna qui e premi OK. L'indirizzo è questo:", PUB_GRUPPO),
        (f"Passo 2 di {totale}. Incolla nel campo Oggetto quello che ho copiato negli appunti, poi torna qui e premi OK. L'oggetto è questo:",
         oggetto),
        (f"Passo 3 di {totale}. Incolla nel testo della mail quello che ho copiato negli appunti, e scrivi la tua domanda al posto della prima "
         "riga; le informazioni su MeTeOra e sul computer, sotto, puoi cancellarle se preferisci. Poi torna qui e premi OK. Il testo è questo:",
         corpo),
    ]
    if registri:
        passi.append(("Passo 4 di 5. Allega alla mail il file dei registri: nella tua posta scegli Allega, o Aggiungi allegato, e nel campo del "
            "nome del file incolla il percorso che ho copiato negli appunti; poi torna qui e premi OK. Il percorso è questo:", registri))
    passi.append((f"Passo {totale} di {totale}. Spedisci la mail. {_ISCRIVITI} OK chiude questa finestra.", None))
    return {
        "titolo": "Chiedi aiuto al PUB",
        "destinatario": PUB_GRUPPO,
        "oggetto": oggetto,
        "corpo": corpo,
        "spiegazione": "\n".join((
            f"Il pulsante Apri nel programma di posta prepara in {{programma}} una mail al PUB, il gruppo di supporto dei programmi di "
            f"Gabriele Battaglia, con l'oggetto {oggetto}.",
            "Scrivi la tua domanda al posto della prima riga del testo; sotto ci sono le informazioni su MeTeOra e sul tuo computer, utili a "
            "chi ti risponde, che puoi cancellare se preferisci.",
            *([allegati] if allegati else []),
            f"Poi spediscila tu: MeTeOra non spedisce niente da solo. {_ISCRIVITI}",
            _ALTRA_STRADA,
        )),
        "passi": tuple(passi),
        **({"appunti": registri} if registri else {}),
    }
