# MeTeOra, le parole delle due voci del PUB, il gruppo di supporto: la mail che iscrive e quella che chiede aiuto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/11/2026: nasce con la 2.1.0, issue 30. Nella 2.4.0 i registri degli errori, ripuliti, da allegare alla richiesta d'aiuto. Nella 3.0.0 i testi passano da lingua.py, per le traduzioni.

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

from lingua import _

PULSANTI = {"apri": _("&Apri nel programma di posta"), "passi": _("&Passo per passo"), "ok": _("&OK"), "chiudi": _("&Chiudi"), "annulla": _("&Annulla")}
SENZA_POSTA = _("Non trovo un programma di posta, oppure non si è aperto: prepariamo la mail un pezzo alla volta, da incollare nella tua "
    "posta, per esempio nella webmail del browser.")
# Le informazioni del computer nella mail d'aiuto, nell'ordine in cui
# compaiono; quelle che non si leggono restano fuori. Se il programma e'
# compilato lo dice gia' la riga del programma.
ETICHETTE = {
    # Traduttori: le etichette delle informazioni sul computer, nella mail di Chiedi aiuto al PUB.
    "windows": _("Sistema operativo"),
    "windows_versione": _("Versione di Windows"),
    # Traduttori: il numero di build di Windows, come 26100.
    "windows_build": _("Build di Windows"),
    # Traduttori: l'architettura del processore, come AMD64.
    "architettura": _("Architettura"),
    "processore": _("Processore"),
    # Traduttori: quanti processori logici ha il computer.
    "nuclei": _("Nuclei logici"),
    # Traduttori: la memoria RAM del computer.
    "memoria_totale": _("Memoria"),
    "memoria_libera": _("Memoria libera"),
    "lingua": _("Lingua di sistema"),
    "screen_reader": _("Screen reader"),
    # Traduttori: lo schermo del computer, con la sua risoluzione.
    "schermo": _("Schermo"),
    # Traduttori: il ridimensionamento di Windows, come 150%.
    "scala": _("Scala dello schermo"),
    "python": "Python",
}
# Traduttori: le risposte sì e no nelle informazioni sul computer della mail di Chiedi aiuto al PUB.
PAROLE = {True: _("sì"), False: _("no")}
_ALTRA_STRADA = _("Se la mail non compare, torna qui e scegli Passo per passo: ti guido a scriverla nella tua posta, per esempio nella webmail "
    "del browser.")
_ISCRIVITI = _("Se non sei ancora iscritto al PUB, puoi farlo con Entra al PUB, nelle impostazioni.")
# La casella dei registri, e il file che si allega (2.4.0).
CASELLA_DEI_REGISTRI = _("&Includi anche i registri degli errori")
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
    # Traduttori: {data} e' come 03/11/2026, {ora} come 10:30.
    righe = [_("Registri di MeTeOra {versione}, preparati il {data} alle {ora} per il PUB, "
             "ripuliti dal nome dell'utente di Windows e del computer.").format(versione=versione, data=time.strftime("%d/%m/%Y"), ora=time.strftime("%H:%M"))]
    errori = [p for p in presenti if os.path.basename(p) in _ERRORI]
    if errori:
        testo = "".join(_coda(p, CODA_DEGLI_ERRORI)[0] for p in errori)
        tagliato = len(testo) > CODA_DEGLI_ERRORI
        righe.append(_("Dal registro degli errori, la parte finale:") if tagliato else _("Dal registro degli errori, tutto:"))
        righe.append(testo[-CODA_DEGLI_ERRORI:].rstrip("\n"))
    for percorso in presenti:
        if percorso in errori:
            continue
        testo, tagliato = _coda(percorso, CODA_DI_UN_CRASH)
        if tagliato:
            righe.append(_("Dal resoconto del crash {nome}, la parte finale:").format(nome=os.path.basename(percorso)))
        else:
            righe.append(_("Dal resoconto del crash {nome}, tutto:").format(nome=os.path.basename(percorso)))
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
        "titolo": _("Entra al PUB, il gruppo di supporto"),
        "destinatario": PUB_ISCRIZIONE,
        # Traduttori: l'oggetto della mail che iscrive al PUB; Google non lo legge.
        "oggetto": _("Iscrizione al PUB"),
        "corpo": _("Invia questo messaggio così com'è per iscriverti al PUB. Google ti scriverà per chiederti di confermare."),
        "spiegazione": "\n".join((
            _("Il PUB è il gruppo di supporto dei programmi di Gabriele Battaglia, una lista di posta su Google Groups, dove si chiede aiuto, si "
                "segnalano i problemi e si propongono idee."),
            # {programma} lo riempie finestra_mail di GBwx con il nome del
            # programma di posta: qui il segnaposto resta com'e' (3.0.0).
            # Traduttori: {programma} e' il programma di posta, come Outlook o Thunderbird.
            _("Il pulsante Apri nel programma di posta prepara in {programma} la mail che ti iscrive: spediscila così com'è, perché MeTeOra non "
                "spedisce niente da solo. Poi Google ti scriverà per chiederti di confermare l'iscrizione: segui le sue istruzioni.").format(
                programma="{programma}"),
            _ALTRA_STRADA,
        )),
        "passi": (
            # Traduttori: il campo A e' quello del destinatario della mail.
            (_("Passo 1 di 2. Scrivi una mail nuova nella tua posta, per esempio nella webmail del browser, e incolla nel campo A l'indirizzo "
               "dell'iscrizione, che ho copiato negli appunti; poi torna qui e premi OK. L'indirizzo è questo:"), PUB_ISCRIZIONE),
            (_("Passo 2 di 2. Oggetto e testo possono restare vuoti, perché Google non li legge: spedisci la mail così com'è. Google ti scriverà "
               "per chiederti di confermare l'iscrizione: segui le sue istruzioni. OK chiude questa finestra."), None),
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

    # Traduttori: l'oggetto della mail che chiede aiuto al PUB; {versione} e' come 3.0.0.
    oggetto = _("Chiedo per MeTeOra {versione}").format(versione=versione)
    if compilato:
        programma = _("Programma: MeTeOra {versione}, pacchetto compilato").format(versione=versione)
    else:
        programma = _("Programma: MeTeOra {versione}, dai sorgenti").format(versione=versione)
    corpo = "\n".join((
        _("Scrivi qui la tua domanda, al posto di questa riga."),
        _("Informazioni su MeTeOra e sul computer di chi scrive:"),
        programma,
        *([_("Scheda audio: {scheda}").format(scheda=scheda_audio)] if scheda_audio else []),
        *righe_informazioni(ETICHETTE, informazioni, PAROLE),
        *([_("In allegato i registri degli errori di MeTeOra, ripuliti dal nome dell'utente e del computer.")] if registri else []),
    ))
    if registri:
        # Traduttori: {file} e' il nome del file dei registri, {cartella} la cartella in cui sta.
        allegati = _("Allega alla mail anche il file {file}, che sta nella cartella {cartella}: quando la bozza "
            "è pronta ne trovi il percorso negli appunti, da incollare nella finestra Allega del programma di posta. Il file è ripulito dal nome "
            "del tuo utente di Windows e del computer; i percorsi dei brani restano, perché aiutano a capire l'errore.").format(
            file=FILE_DEI_REGISTRI, cartella=os.path.dirname(registri))
    elif casella:
        allegati = _("Se vuoi allegare anche i registri degli errori di MeTeOra, ripuliti dal nome del tuo utente e del computer, spunta la casella qui sotto.")
    else:
        allegati = ""
    totale = 5 if registri else 4
    passi = [
        # Traduttori: {totale} e' il numero dei passi, 4 o 5; il campo A e' quello del destinatario della mail.
        (_("Passo 1 di {totale}. Scrivi una mail nuova nella tua posta, per esempio nella webmail del browser, e incolla nel campo A "
           "l'indirizzo del PUB, che ho copiato negli appunti; poi torna qui e premi OK. L'indirizzo è questo:").format(totale=totale), PUB_GRUPPO),
        (_("Passo 2 di {totale}. Incolla nel campo Oggetto quello che ho copiato negli appunti, poi torna qui e premi OK. L'oggetto è questo:").format(
            totale=totale), oggetto),
        (_("Passo 3 di {totale}. Incolla nel testo della mail quello che ho copiato negli appunti, e scrivi la tua domanda al posto della prima "
           "riga; le informazioni su MeTeOra e sul computer, sotto, puoi cancellarle se preferisci. Poi torna qui e premi OK. Il testo è questo:").format(
            totale=totale), corpo),
    ]
    if registri:
        passi.append((_("Passo 4 di 5. Allega alla mail il file dei registri: nella tua posta scegli Allega, o Aggiungi allegato, e nel campo del "
            "nome del file incolla il percorso che ho copiato negli appunti; poi torna qui e premi OK. Il percorso è questo:"), registri))
    # Traduttori: {passo} e {totale} sono lo stesso numero, l'ultimo passo; {iscriviti} e' la frase che invita a iscriversi al PUB.
    passi.append((_("Passo {passo} di {totale}. Spedisci la mail. {iscriviti} OK chiude questa finestra.").format(passo=totale, totale=totale,
        iscriviti=_ISCRIVITI), None))
    return {
        "titolo": _("Chiedi aiuto al PUB"),
        "destinatario": PUB_GRUPPO,
        "oggetto": oggetto,
        "corpo": corpo,
        "spiegazione": "\n".join((
            # {programma} resta com'e', per finestra_mail, come nella mail d'iscrizione.
            # Traduttori: {programma} e' il programma di posta, come Outlook o Thunderbird; {oggetto} l'oggetto della mail.
            _("Il pulsante Apri nel programma di posta prepara in {programma} una mail al PUB, il gruppo di supporto dei programmi di "
                "Gabriele Battaglia, con l'oggetto {oggetto}.").format(programma="{programma}", oggetto=oggetto),
            _("Scrivi la tua domanda al posto della prima riga del testo; sotto ci sono le informazioni su MeTeOra e sul tuo computer, utili a "
                "chi ti risponde, che puoi cancellare se preferisci."),
            *([allegati] if allegati else []),
            # Traduttori: {iscriviti} e' la frase che invita a iscriversi al PUB.
            _("Poi spediscila tu: MeTeOra non spedisce niente da solo. {iscriviti}").format(iscriviti=_ISCRIVITI),
            _ALTRA_STRADA,
        )),
        "passi": tuple(passi),
        **({"appunti": registri} if registri else {}),
    }
