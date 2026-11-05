# MeTeOra, i dettagli dei contenitori: cartelle, unita', Questo PC e playlist, che F11 scrive nella console.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.77.0, chiesto da Gabriele: tutti i dati possibili del contenitore su cui si e'. Nella 1.104.1 lo 0.0% come le statistiche. Nella 3.0.0 i testi passano da lingua.py, per le traduzioni.

"""I dettagli di un contenitore, raccolti fuori dal filo della finestra.

censisci percorre una cartella con tutto cio' che ha sotto, una volta sola:
i file da suonare, con le stesse regole del contatore (niente file o
cartelle nascosti o di sistema), e tutti i file, nascosti compresi, con le
loro dimensioni. Le giunzioni e i collegamenti si seguono, come fa il
contatore, ma ogni cartella si percorre una volta sola, per non girare in
tondo.
dati_dell_unita chiede a Windows capacita', spazio libero, nome del volume e
file system. Le righe le compongono le funzioni righe_*, una informazione
per riga, nella forma "Etichetta: valore", cosi' si leggono e si cercano
una per una.
"""

import contextlib
import ctypes
import os
import shutil
import stat
import time
from collections import Counter
from ctypes import wintypes

import formati
import questa_rete
from lingua import _, ngettext
from ricerca import in_rete

# Traduttori: i nomi dei mesi, nelle date come «4 ottobre 2026 alle 9:05».
MESI = (_("gennaio"), _("febbraio"), _("marzo"), _("aprile"), _("maggio"), _("giugno"), _("luglio"), _("agosto"), _("settembre"), _("ottobre"),
    _("novembre"), _("dicembre"))
_NASCOSTO_O_DI_SISTEMA = stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM
# Il nome dei tipi di unita' di GetDriveTypeW.
TIPI_DI_UNITA = {2: _("unità rimovibile"), 3: _("disco locale"), 4: _("unità di rete"), 5: _("unità CD o DVD"), 6: _("disco in memoria")}


def quando(secondi):
    """Una data con l'ora, come la si dice: 4 ottobre 2026 alle 9:05. Una
    data che Windows non sa convertire, come quelle a zero del 1601 o oltre
    l'anno 3000, si dice data non valida."""
    try:
        t = time.localtime(secondi)
    except (OSError, OverflowError, ValueError):
        # Traduttori: quello che si dice al posto di una data che Windows non sa convertire.
        return _("una data non valida")
    # Traduttori: una data con l'ora, come «4 ottobre 2026 alle 9:05»; {mese} e' il nome del mese.
    return _("{giorno} {mese} {anno} alle {ora}:{minuti:02d}").format(giorno=t.tm_mday, mese=MESI[t.tm_mon - 1], anno=t.tm_year, ora=t.tm_hour,
        minuti=t.tm_min)


def dimensione(byte):
    """Una dimensione con l'unita' adatta, con un decimale: 1.5 GB."""
    from GBUtils import formatta_dimensione

    # Traduttori: le unita' delle dimensioni dei file, dal byte al petabyte, come in «1.5 GB».
    return formatta_dimensione(byte, decimali=1, unita=(_("byte"), _("KB"), _("MB"), _("GB"), _("TB"), _("PB")), byte_interi=True)


def per_tipo(percorsi):
    """Quanti file per estensione, dalla piu' frequente: mp3 120, flac 3."""
    # Traduttori: i file senza estensione, come in «Tipi: mp3 120, senza estensione 2».
    senza = _("senza estensione")
    conti = Counter(os.path.splitext(p)[1].lower().lstrip(".") or senza for p in percorsi)
    return ", ".join(f"{tipo} {n}" for tipo, n in sorted(conti.items(), key=lambda c: (-c[1], c[0])))


def censisci(cartella, fermo=None):
    """Tutto quello che si sa di una cartella dal disco, percorsa una volta.
    fermo, se c'e', si chiede fra una cartella e l'altra: vero interrompe,
    e il risultato lo dice con interrotto."""
    esito = {"file": 0, "byte": 0, "suonabili": [], "byte_suonabili": 0, "dirette": 0, "sottocartelle": 0,
        "piu_recente": None, "illeggibili": 0, "interrotto": False, "errore": None}
    # Le cartelle gia' percorse, per non girare in tondo seguendo le
    # giunzioni, che il contatore segue: (disco, indice) del file system.
    viste = set()
    pila = [(cartella, True)]
    while pila:
        if fermo is not None and fermo():
            esito["interrotto"] = True
            break
        attuale, visibile = pila.pop()
        try:
            with os.scandir(attuale) as voci:
                voci = list(voci)
        except OSError as errore:
            if attuale == cartella:
                esito["errore"] = errore.strerror or str(errore)
                break
            esito["illeggibili"] += 1
            continue
        for voce in voci:
            try:
                # Le giunzioni e i collegamenti si seguono, come fa il contatore.
                info = voce.stat()
            except OSError:
                continue
            nascosta = bool(getattr(info, "st_file_attributes", 0) & _NASCOSTO_O_DI_SISTEMA)
            if voce.is_dir():
                if (info.st_dev, info.st_ino) in viste and info.st_ino:
                    continue
                viste.add((info.st_dev, info.st_ino))
                esito["sottocartelle"] += 1
                if attuale == cartella:
                    esito["dirette"] += 1
                pila.append((voce.path, visibile and not nascosta))
                continue
            esito["file"] += 1
            esito["byte"] += info.st_size
            if not visibile or nascosta:
                continue
            # Il piu' recente fra i file visibili: quelli nascosti, come gli
            # oggetti di git, cambiano di continuo e non dicono niente.
            if esito["piu_recente"] is None or info.st_mtime > esito["piu_recente"][0]:
                esito["piu_recente"] = (info.st_mtime, voce.path)
            if formati.supportato(voce.name):
                esito["suonabili"].append(voce.path)
                esito["byte_suonabili"] += info.st_size
    return esito


def censisci_brani(percorsi, fermo=None):
    """Dimensione e assenze dei file di una playlist: byte, mancanti, i
    percorsi che sul disco non ci sono piu', e lontani, quanti file stanno
    in rete su un disco che non risponde: si prova una volta per radice,
    con il tempo massimo di Questa rete, invece di aspettare file per file.
    fermo, se c'e', si chiede ogni cento file."""
    esito = {"byte": 0, "mancanti": [], "lontani": 0, "interrotto": False}
    raggiungibili = {}
    for numero, percorso in enumerate(dict.fromkeys(percorsi)):
        if fermo is not None and numero % 100 == 0 and fermo():
            esito["interrotto"] = True
            break
        if in_rete(percorso):
            radice = os.path.splitdrive(percorso)[0] + "\\"
            if radice not in raggiungibili:
                raggiungibili[radice] = questa_rete.raggiungibile(radice, attesa=questa_rete.ATTESA_IN_SOTTOFONDO)
            if not raggiungibili[radice]:
                esito["lontani"] += 1
                continue
        try:
            esito["byte"] += os.stat(percorso).st_size
        except OSError:
            esito["mancanti"].append(percorso)
    return esito


def _volume(radice):
    """(nome del volume, file system, numero di serie) di un'unita', o
    stringhe vuote e il percorso al posto del numero."""
    nome = ctypes.create_unicode_buffer(261)
    sistema = ctypes.create_unicode_buffer(261)
    seriale, massima, opzioni = wintypes.DWORD(), wintypes.DWORD(), wintypes.DWORD()
    riuscito = ctypes.windll.kernel32.GetVolumeInformationW(
        wintypes.LPCWSTR(radice), nome, 261, ctypes.byref(seriale), ctypes.byref(massima), ctypes.byref(opzioni), sistema, 261)
    return (nome.value, sistema.value, seriale.value) if riuscito else ("", "", radice)


def dati_dell_unita(radice):
    """Capacita', spazio libero e occupato, nome del volume, file system e
    tipo di un'unita' come E:\\. pronta e' falso per un lettore senza disco
    o una rete che non risponde."""
    tipo = ctypes.windll.kernel32.GetDriveTypeW(wintypes.LPCWSTR(radice))
    # Traduttori: un'unita' di cui Windows non dice il tipo.
    esito = {"radice": radice, "tipo": TIPI_DI_UNITA.get(tipo, _("unità")), "pronta": False}
    with contextlib.suppress(OSError):
        uso = shutil.disk_usage(radice)
        esito.update(pronta=True, totale=uso.total, libero=uso.free, occupato=uso.used)
    # Il numero di serie dice se due lettere sono lo stesso volume.
    esito["nome"], esito["file_system"], esito["volume"] = _volume(radice)
    return esito


def percentuale(parte, tutto):
    """La percentuale con il punto, 58.4%, da dire senza articolo davanti:
    l'8%, il 58%, lo 0.5% vorrebbero articoli diversi. Con il totale a zero,
    0.0% come le statistiche (1.104.1)."""
    return f"{100 * parte / tutto:.1f}%" if tutto else "0.0%"


def righe_dell_unita(dati):
    """Le righe dello spazio di un'unita'."""
    lettera = dati["radice"].rstrip("\\")
    unita = f"{lettera}, {dati['nome']}" if dati["nome"] else lettera
    if dati["file_system"]:
        # Traduttori: {unita} e' la lettera dell'unita', con il nome del volume se c'e', come «E:, Musica»; {tipo} come disco locale; {sistema} come NTFS.
        righe = [_("Unità {unita}: {tipo}, file system {sistema}.").format(unita=unita, tipo=dati["tipo"], sistema=dati["file_system"])]
    else:
        righe = [_("Unità {unita}: {tipo}.").format(unita=unita, tipo=dati["tipo"])]
    if not dati["pronta"]:
        righe.append(_("Spazio: l'unità non risponde, o non ha un disco."))
        return righe
    righe.append(_("Capacità: {dimensione}.").format(dimensione=dimensione(dati["totale"])))
    # Traduttori: {percentuale} e' come 58.4%.
    righe.append(_("Spazio libero: {dimensione}, {percentuale} del totale.").format(dimensione=dimensione(dati["libero"]),
        percentuale=percentuale(dati["libero"], dati["totale"])))
    righe.append(_("Spazio occupato: {dimensione}, {percentuale} del totale.").format(dimensione=dimensione(dati["occupato"]),
        percentuale=percentuale(dati["occupato"], dati["totale"])))
    return righe


def righe_dei_brani(elementi, durata_di, scrivi_durata, nome_di=None, percorso_di=None):
    """Le righe comuni a cartelle e playlist sui file da suonare: di che
    tipo sono, quanto durano, il piu' lungo e il piu' corto. elementi sono
    percorsi, o brani con percorso_di che ne da' il percorso; durata_di da'
    i secondi di un elemento, o None se non si conoscono ancora; nome_di il
    nome da dire, per predefinito quello del file."""
    if not elementi:
        return []
    percorso_di = percorso_di or (lambda e: e)
    nome_di = nome_di or (lambda e: os.path.basename(percorso_di(e)))
    # Traduttori: quanti file per estensione, come «Tipi: mp3 120, flac 3.».
    righe = [_("Tipi: {tipi}.").format(tipi=per_tipo([percorso_di(e) for e in elementi]))]
    durate = [(e, durata_di(e)) for e in elementi]
    note = [(p, d) for p, d in durate if d is not None]
    ignote = len(durate) - len(note)
    if note:
        totale = scrivi_durata(sum(d for _p, d in note))
        if ignote:
            # Traduttori: {n} e' quanti file non hanno ancora una durata conosciuta.
            righe.append(ngettext("Durata: {durata}, più {n} di cui la durata non si conosce.", "Durata: {durata}, più {n} di cui la durata non si conosce.",
                ignote).format(durata=totale, n=ignote))
        else:
            righe.append(_("Durata: {durata}.").format(durata=totale))
        lungo = max(note, key=lambda c: c[1])
        corto = min(note, key=lambda c: c[1])
        # Traduttori: il brano piu' lungo, con il suo nome e la sua durata.
        righe.append(_("Il più lungo: {nome}, {durata}.").format(nome=nome_di(lungo[0]), durata=scrivi_durata(lungo[1])))
        if len(note) > 1:
            righe.append(_("Il più corto: {nome}, {durata}.").format(nome=nome_di(corto[0]), durata=scrivi_durata(corto[1])))
    else:
        righe.append(_("Durata: non ancora nota."))
    return righe


def attributi(percorso):
    """Gli attributi da dire di una cartella: nascosta, di sistema, sola lettura, compressa."""
    try:
        valore = os.stat(percorso).st_file_attributes
    except (OSError, AttributeError):
        return []
    # Traduttori: gli attributi di una cartella, come in «Attributi: nascosta, di sistema.».
    nomi = ((stat.FILE_ATTRIBUTE_HIDDEN, _("nascosta")), (stat.FILE_ATTRIBUTE_SYSTEM, _("di sistema")),
        (stat.FILE_ATTRIBUTE_READONLY, _("sola lettura")), (stat.FILE_ATTRIBUTE_COMPRESSED, _("compressa")))
    return [nome for bit, nome in nomi if valore & bit]


def righe_della_cartella(percorso, censimento, durata_di, scrivi_durata, radice=False):
    """Le righe dei dettagli di una cartella, dal suo censimento. Con radice,
    la cartella e' la radice di un'unita': la riga col percorso, le date e gli
    attributi, che per la radice, sempre nascosta e di sistema, non servono,
    restano fuori (3.0.0: prima le toglieva la finestra, riconoscendole
    dall'italiano)."""
    nome = os.path.basename(percorso.rstrip("\\")) or percorso
    righe = [] if radice else [_("Cartella {nome}: {percorso}.").format(nome=nome, percorso=percorso)]
    if censimento["errore"]:
        # Traduttori: {errore} e' il perche' che dice Windows.
        return [*righe, _("Non riesco a leggerla: {errore}.").format(errore=censimento["errore"])]
    suonabili = censimento["suonabili"]
    # Vuota solo se si e' letto tutto: una sottocartella illeggibile puo' avere file.
    if not censimento["file"] and not censimento["sottocartelle"] and not censimento["illeggibili"]:
        righe.append(_("È vuota: niente file e niente sottocartelle."))
    elif not censimento["file"] and not censimento["illeggibili"]:
        righe.append(_("È vuota: ha solo sottocartelle vuote."))
    if suonabili:
        righe.append(ngettext("Da suonare: {n} file, sottocartelle comprese, {dimensione}.", "Da suonare: {n} file, sottocartelle comprese, {dimensione}.",
            len(suonabili)).format(n=len(suonabili), dimensione=dimensione(censimento["byte_suonabili"])))
        righe += righe_dei_brani(suonabili, durata_di, scrivi_durata)
    elif censimento["file"]:
        righe.append(_("Da suonare: niente, in nessuna sottocartella."))
    if censimento["sottocartelle"]:
        # Traduttori: {dirette} sono le sottocartelle subito dentro la cartella, {tutte} quelle a ogni livello.
        righe.append(_("Sottocartelle: {dirette} qui dentro, {tutte} in tutto.").format(dirette=censimento["dirette"], tutte=censimento["sottocartelle"]))
    if censimento["file"]:
        # Traduttori: {n} e' il numero di tutti i file della cartella, {dimensione} quanto occupano.
        righe.append(_("Tutti i file: {n}, {dimensione}, nascosti e di ogni tipo compresi.").format(n=censimento["file"], dimensione=dimensione(censimento["byte"])))
    if not radice:
        with contextlib.suppress(OSError):
            info = os.stat(percorso)
            nascita = getattr(info, "st_birthtime", info.st_ctime)
            # Traduttori: {creata} e {modificata} sono date con l'ora, come «4 ottobre 2026 alle 9:05».
            righe.append(_("Creata il {creata}; modificata il {modificata}.").format(creata=quando(nascita), modificata=quando(info.st_mtime)))
    if censimento["piu_recente"]:
        istante, recente = censimento["piu_recente"]
        righe.append(_("Il file cambiato per ultimo: {percorso}, il {quando}.").format(percorso=os.path.relpath(recente, percorso), quando=quando(istante)))
    segni = [] if radice else attributi(percorso)
    if segni:
        righe.append(_("Attributi: {attributi}.").format(attributi=", ".join(segni)))
    if censimento["illeggibili"]:
        righe.append(ngettext("Non si leggono: {n} cartella, che i conti non comprendono.", "Non si leggono: {n} cartelle, che i conti non comprendono.",
            censimento["illeggibili"]).format(n=censimento["illeggibili"]))
    if censimento["interrotto"]:
        righe.append(_("Conto interrotto: i numeri valgono per la parte letta."))
    return righe
