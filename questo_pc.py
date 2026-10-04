# MeTeOra, Questo PC: unita', cartelle e file supportati.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.4.0 il cestino, nella 1.5.0 le cartelle ricorsive. Nella 1.67.0 i nomi validi e i file compagni, per Rinomina file.

"""Cosa mostra il ramo Questo PC della plancia.

Le unita' le chiede a Windows, con la lettera e il nome del volume; le
cartelle si leggono solo quando vengono espanse. Dei file restano solo
quelli che MeTeOra sa suonare; file e cartelle nascosti o di sistema non
compaiono.
"""

import ctypes
import os
import string
from ctypes import wintypes

import formati

# I caratteri che Windows non accetta nei nomi dei file, con il nome da
# leggere, e i nomi riservati (Rinomina file, 1.67.0).
CARATTERI_VIETATI = {"<": "minore", ">": "maggiore", ":": "due punti", '"': "virgolette", "/": "barra", "\\": "barra rovesciata",
    "|": "barra verticale", "?": "punto interrogativo", "*": "asterisco"}
NOMI_RISERVATI = frozenset({"con", "prn", "aux", "nul", *(f"com{n}" for n in range(1, 10)), *(f"lpt{n}" for n in range(1, 10))})
# I file che accompagnano un brano con il suo stesso nome, e che cambiano
# nome con lui: i sottotitoli e i testi sincronizzati.
ESTENSIONI_COMPAGNE = frozenset({".srt", ".ass", ".ssa", ".vtt", ".sub", ".idx", ".sup", ".lrc"})

_NASCOSTO = 0x2
_SISTEMA = 0x4
# I nomi dei tipi di unita' di GetDriveTypeW, usati quando il volume non ha nome.
_TIPI = {2: "Unità rimovibile", 3: "Disco locale", 4: "Unità di rete", 5: "Unità CD", 6: "Disco in memoria"}


def _nome_del_volume(radice):
    kernel32 = ctypes.windll.kernel32
    nome = ctypes.create_unicode_buffer(261)
    # Un'unita' vuota, per esempio un lettore CD senza disco, non deve far
    # comparire la finestra di errore di Windows.
    vecchia = kernel32.SetErrorMode(0x0001)
    try:
        riuscito = kernel32.GetVolumeInformationW(wintypes.LPCWSTR(radice), nome, len(nome), None, None, None, None, 0)
    finally:
        kernel32.SetErrorMode(vecchia)
    if riuscito and nome.value:
        return nome.value
    return _TIPI.get(kernel32.GetDriveTypeW(wintypes.LPCWSTR(radice)), "Unità")


def unita():
    """Le unita' logiche e virtuali collegate: lista di (radice, etichetta),
    per esempio ("E:\\", "E:\\Dati")."""
    maschera = ctypes.windll.kernel32.GetLogicalDrives()
    elenco = []
    for i, lettera in enumerate(string.ascii_uppercase):
        if maschera & (1 << i):
            radice = f"{lettera}:\\"
            elenco.append((radice, f"{lettera}:\\{_nome_del_volume(radice)}"))
    return elenco


def _visibile(voce):
    try:
        attributi = voce.stat(follow_symlinks=False).st_file_attributes
    except OSError:
        return False
    return not attributi & (_NASCOSTO | _SISTEMA)


def _in_ordine(nomi):
    return sorted(nomi, key=lambda n: os.path.basename(n).casefold())


def contenuto(cartella, al_passo=None):
    """Sottocartelle e file supportati di una cartella, in ordine
    alfabetico: (cartelle, file), percorsi completi. Solleva OSError se la
    cartella non si puo' leggere. al_passo, se c'e', si chiama a ogni voce
    letta: la ricerca in rete lo usa per sapere che la lettura va avanti."""
    cartelle, files = [], []
    with os.scandir(cartella) as voci:
        for voce in voci:
            if al_passo is not None:
                al_passo()
            if not _visibile(voce):
                continue
            if voce.is_dir(follow_symlinks=False):
                cartelle.append(voce.path)
            elif voce.is_file() and formati.supportato(voce.name):
                files.append(voce.path)
    return _in_ordine(cartelle), _in_ordine(files)


def contenuti_ricorsivi(cartella):
    """Le cartelle sotto una cartella, lei compresa, ciascuna con i suoi file
    supportati: lista di (cartella, file), in ordine alfabetico, con i file
    di una cartella prima delle sue sottocartelle. Le cartelle che non si
    possono leggere si saltano."""
    try:
        cartelle, files = contenuto(cartella)
    except OSError:
        return []
    elenco = [(cartella, files)]
    for sotto in cartelle:
        elenco.extend(contenuti_ricorsivi(sotto))
    return elenco


def file_ricorsivi(cartella):
    """Tutti i file supportati sotto una cartella, nell'ordine di contenuti_ricorsivi."""
    return [f for _cartella, files in contenuti_ricorsivi(cartella) for f in files]


class _SHFILEOPSTRUCTW(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("wFunc", wintypes.UINT),
        ("pFrom", wintypes.LPCWSTR),
        ("pTo", wintypes.LPCWSTR),
        ("fFlags", ctypes.c_uint16),
        ("fAnyOperationsAborted", wintypes.BOOL),
        ("hNameMappings", ctypes.c_void_p),
        ("lpszProgressTitle", wintypes.LPCWSTR),
    ]


_FO_DELETE = 3
# Nel cestino, senza le domande e le finestre di Windows: la conferma la
# chiede MeTeOra, e un errore torna come esito.
_FOF_ALLOWUNDO = 0x40
_FOF_NOCONFIRMATION = 0x10
_FOF_SILENT = 0x4
_FOF_NOERRORUI = 0x400


# I file che Windows e gli altri sistemi lasciano da soli nelle cartelle:
# una cartella che ha solo loro conta come vuota (1.76.0).
FILE_DI_SERVIZIO = {"desktop.ini", "thumbs.db", ".ds_store"}


def cartella_vuota(cartella):
    """Vero se nella cartella e nelle sue sottocartelle non c'e' nessun file,
    a parte quelli di servizio, nascosti compresi: si ferma al primo.
    Solleva OSError se la cartella, o una sottocartella, non si legge."""

    def errore(eccezione):
        raise eccezione

    for _radice, _cartelle, files in os.walk(cartella, onerror=errore):
        if any(nome.lower() not in FILE_DI_SERVIZIO for nome in files):
            return False
    return True


def ha_il_cestino(percorso):
    """Falso dove Windows non ha il cestino e cancella per sempre: in rete,
    sulle unita' rimovibili come le chiavette e sui CD."""
    unita = os.path.splitdrive(os.path.abspath(percorso))[0]
    if not unita.endswith(":"):
        return False
    return ctypes.windll.kernel32.GetDriveTypeW(unita + "\\") not in (2, 4, 5)


def nel_cestino(percorso):
    """Manda un file, o una cartella, nel cestino di Windows; dove il
    cestino non c'e' (vedi ha_il_cestino) Windows lo cancella per sempre.
    Vero se non c'e' piu'."""
    operazione = _SHFILEOPSTRUCTW(
        hwnd=None, wFunc=_FO_DELETE, pFrom=os.path.abspath(percorso) + "\0", pTo=None,
        fFlags=_FOF_ALLOWUNDO | _FOF_NOCONFIRMATION | _FOF_SILENT | _FOF_NOERRORUI,
    )
    esito = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(operazione))
    return esito == 0 and not operazione.fAnyOperationsAborted and not os.path.exists(percorso)


def nome_non_valido(nome):
    """Perche' nome non va bene come nome di un file in Windows, o None."""
    vietati = [CARATTERI_VIETATI[c] for c in dict.fromkeys(nome) if c in CARATTERI_VIETATI]
    if vietati:
        return f"Nel nome di un file non possono stare: {', '.join(vietati)}."
    if any(ord(c) < 32 for c in nome):
        return "Nel nome di un file non possono stare caratteri di controllo."
    if nome.split(".")[0].strip().casefold() in NOMI_RISERVATI:
        return f"{nome} è un nome riservato di Windows."
    return None


def file_compagni(percorso, m3u=False):
    """I file accanto con lo stesso nome e un'estensione da compagno, come i
    sottotitoli, anche con la lingua in mezzo come film.it.srt; con m3u
    anche la lista della musica delle console. Lista di (percorso, coda del
    nome dopo quello del file, per esempio .it.srt)."""
    cartella, nome_del_file = os.path.split(percorso)
    base = os.path.splitext(nome_del_file)[0]
    estensioni = ESTENSIONI_COMPAGNE | ({".m3u"} if m3u else frozenset())
    try:
        nomi = sorted(os.listdir(cartella), key=str.casefold)
    except OSError:
        return []
    return [(os.path.join(cartella, nome), nome[len(base):]) for nome in nomi
        if nome.casefold() != nome_del_file.casefold() and nome.casefold().startswith(base.casefold() + ".")
        and os.path.splitext(nome)[1].casefold() in estensioni]
