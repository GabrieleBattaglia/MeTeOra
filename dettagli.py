# MeTeOra, i dettagli dei contenitori: cartelle, unita', Questo PC e playlist, che F11 scrive nella console.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.77.0, chiesto da Gabriele: tutti i dati possibili del contenitore su cui si e'.

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
from ricerca import in_rete

MESI = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre")
_NASCOSTO_O_DI_SISTEMA = stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM
# Il nome dei tipi di unita' di GetDriveTypeW.
TIPI_DI_UNITA = {2: "unità rimovibile", 3: "disco locale", 4: "unità di rete", 5: "unità CD o DVD", 6: "disco in memoria"}


def quando(secondi):
    """Una data con l'ora, come la si dice: 4 ottobre 2026 alle 9:05. Una
    data che Windows non sa convertire, come quelle a zero del 1601 o oltre
    l'anno 3000, si dice data non valida."""
    try:
        t = time.localtime(secondi)
    except (OSError, OverflowError, ValueError):
        return "una data non valida"
    return f"{t.tm_mday} {MESI[t.tm_mon - 1]} {t.tm_year} alle {t.tm_hour}:{t.tm_min:02d}"


def dimensione(byte):
    """Una dimensione con l'unita' adatta, con un decimale: 1.5 GB."""
    from GBUtils import formatta_dimensione

    return formatta_dimensione(byte, decimali=1, unita=("byte", "KB", "MB", "GB", "TB", "PB"), byte_interi=True)


def per_tipo(percorsi):
    """Quanti file per estensione, dalla piu' frequente: mp3 120, flac 3."""
    conti = Counter(os.path.splitext(p)[1].lower().lstrip(".") or "senza estensione" for p in percorsi)
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
                raggiungibili[radice] = questa_rete.raggiungibile(radice)
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
    esito = {"radice": radice, "tipo": TIPI_DI_UNITA.get(tipo, "unità"), "pronta": False}
    with contextlib.suppress(OSError):
        uso = shutil.disk_usage(radice)
        esito.update(pronta=True, totale=uso.total, libero=uso.free, occupato=uso.used)
    # Il numero di serie dice se due lettere sono lo stesso volume.
    esito["nome"], esito["file_system"], esito["volume"] = _volume(radice)
    return esito


def percentuale(parte, tutto):
    """La percentuale con il punto, 58.4%, da dire senza articolo davanti:
    l'8%, il 58%, lo 0.5% vorrebbero articoli diversi."""
    return f"{100 * parte / tutto:.1f}%" if tutto else "0%"


def righe_dell_unita(dati):
    """Le righe dello spazio di un'unita'."""
    lettera = dati["radice"].rstrip("\\")
    nome = f", {dati['nome']}" if dati["nome"] else ""
    sistema = f", file system {dati['file_system']}" if dati["file_system"] else ""
    righe = [f"Unità {lettera}{nome}: {dati['tipo']}{sistema}."]
    if not dati["pronta"]:
        righe.append("Spazio: l'unità non risponde, o non ha un disco.")
        return righe
    righe.append(f"Capacità: {dimensione(dati['totale'])}.")
    righe.append(f"Spazio libero: {dimensione(dati['libero'])}, {percentuale(dati['libero'], dati['totale'])} del totale.")
    righe.append(f"Spazio occupato: {dimensione(dati['occupato'])}, {percentuale(dati['occupato'], dati['totale'])} del totale.")
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
    righe = [f"Tipi: {per_tipo([percorso_di(e) for e in elementi])}."]
    durate = [(e, durata_di(e)) for e in elementi]
    note = [(p, d) for p, d in durate if d is not None]
    ignote = len(durate) - len(note)
    if note:
        righe.append(f"Durata: {scrivi_durata(sum(d for _p, d in note))}" + (f", più {ignote} di cui la durata non si conosce." if ignote else "."))
        lungo = max(note, key=lambda c: c[1])
        corto = min(note, key=lambda c: c[1])
        righe.append(f"Il più lungo: {nome_di(lungo[0])}, {scrivi_durata(lungo[1])}.")
        if len(note) > 1:
            righe.append(f"Il più corto: {nome_di(corto[0])}, {scrivi_durata(corto[1])}.")
    else:
        righe.append("Durata: non ancora nota.")
    return righe


def attributi(percorso):
    """Gli attributi da dire di una cartella: nascosta, di sistema, sola lettura, compressa."""
    try:
        valore = os.stat(percorso).st_file_attributes
    except (OSError, AttributeError):
        return []
    nomi = ((stat.FILE_ATTRIBUTE_HIDDEN, "nascosta"), (stat.FILE_ATTRIBUTE_SYSTEM, "di sistema"),
        (stat.FILE_ATTRIBUTE_READONLY, "sola lettura"), (stat.FILE_ATTRIBUTE_COMPRESSED, "compressa"))
    return [nome for bit, nome in nomi if valore & bit]


def righe_della_cartella(percorso, censimento, durata_di, scrivi_durata):
    """Le righe dei dettagli di una cartella, dal suo censimento."""
    nome = os.path.basename(percorso.rstrip("\\")) or percorso
    righe = [f"Cartella {nome}: {percorso}."]
    if censimento["errore"]:
        return [*righe, f"Non riesco a leggerla: {censimento['errore']}."]
    suonabili = censimento["suonabili"]
    # Vuota solo se si e' letto tutto: una sottocartella illeggibile puo' avere file.
    if not censimento["file"] and not censimento["sottocartelle"] and not censimento["illeggibili"]:
        righe.append("È vuota: niente file e niente sottocartelle.")
    elif not censimento["file"] and not censimento["illeggibili"]:
        righe.append("È vuota: ha solo sottocartelle vuote.")
    if suonabili:
        righe.append(f"Da suonare: {len(suonabili)} file, sottocartelle comprese, {dimensione(censimento['byte_suonabili'])}.")
        righe += righe_dei_brani(suonabili, durata_di, scrivi_durata)
    elif censimento["file"]:
        righe.append("Da suonare: niente, in nessuna sottocartella.")
    if censimento["sottocartelle"]:
        righe.append(f"Sottocartelle: {censimento['dirette']} qui dentro, {censimento['sottocartelle']} in tutto.")
    if censimento["file"]:
        righe.append(f"Tutti i file: {censimento['file']}, {dimensione(censimento['byte'])}, nascosti e di ogni tipo compresi.")
    with contextlib.suppress(OSError):
        info = os.stat(percorso)
        nascita = getattr(info, "st_birthtime", info.st_ctime)
        righe.append(f"Creata il {quando(nascita)}; modificata il {quando(info.st_mtime)}.")
    if censimento["piu_recente"]:
        istante, recente = censimento["piu_recente"]
        righe.append(f"Il file cambiato per ultimo: {os.path.relpath(recente, percorso)}, il {quando(istante)}.")
    segni = attributi(percorso)
    if segni:
        righe.append(f"Attributi: {', '.join(segni)}.")
    if censimento["illeggibili"]:
        righe.append(f"Non si leggono: {censimento['illeggibili']} {'cartella' if censimento['illeggibili'] == 1 else 'cartelle'}, che i conti non comprendono.")
    if censimento["interrotto"]:
        righe.append("Conto interrotto: i numeri valgono per la parte letta.")
    return righe
