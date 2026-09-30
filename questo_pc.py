# MeTeOra, Questo PC: unita', cartelle e file supportati.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.4.0 il cestino.

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


def contenuto(cartella):
    """Sottocartelle e file supportati di una cartella, in ordine
    alfabetico: (cartelle, file), percorsi completi. Solleva OSError se la
    cartella non si puo' leggere."""
    cartelle, files = [], []
    with os.scandir(cartella) as voci:
        for voce in voci:
            if not _visibile(voce):
                continue
            if voce.is_dir(follow_symlinks=False):
                cartelle.append(voce.path)
            elif voce.is_file() and formati.supportato(voce.name):
                files.append(voce.path)
    return _in_ordine(cartelle), _in_ordine(files)


def file_ricorsivi(cartella):
    """Tutti i file supportati sotto una cartella, cartella per cartella in
    ordine alfabetico: i file di una cartella prima delle sue sottocartelle.
    Le cartelle che non si possono leggere si saltano."""
    try:
        cartelle, files = contenuto(cartella)
    except OSError:
        return []
    for sotto in cartelle:
        files.extend(file_ricorsivi(sotto))
    return files


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


def nel_cestino(percorso):
    """Manda un file nel cestino di Windows. Vero se ci e' andato."""
    operazione = _SHFILEOPSTRUCTW(
        hwnd=None, wFunc=_FO_DELETE, pFrom=os.path.abspath(percorso) + "\0", pTo=None,
        fFlags=_FOF_ALLOWUNDO | _FOF_NOCONFIRMATION | _FOF_SILENT | _FOF_NOERRORUI,
    )
    esito = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(operazione))
    return esito == 0 and not operazione.fAnyOperationsAborted and not os.path.exists(percorso)
