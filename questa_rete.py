# MeTeOra, Questa rete: i percorsi di rete salvati in Windows, i computer della rete e le loro cartelle condivise.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la 1.64.0, chiesto da Gabriele.

"""Cosa mostra il ramo Questa rete della plancia, accanto a Questo PC.

I percorsi di rete salvati in Windows sono quelli che Esplora risorse
mostra sotto Questo PC, per esempio una cartella condivisa da un disco di
rete: stanno nella cartella Network Shortcuts del profilo, ciascuno come un
collegamento. I computer della rete sono quelli della cartella Rete di
Esplora risorse, e le loro cartelle condivise si chiedono alla shell nello
stesso modo; su molti Windows di oggi la ricerca trova poco o niente, e puo'
durare secondi: si fa in un filo in disparte. Le unita' di rete con una
lettera restano in Questo PC.
Una cartella di rete che non risponde puo' far aspettare Windows anche
mezzo minuto: raggiungibile la prova in un filo a parte, e smette di
aspettare dopo pochi secondi.
"""

import contextlib
import os
import threading

# Quanto si aspetta una cartella di rete prima di dirla irraggiungibile.
ATTESA_DELLA_RETE = 3.0


def cartella_dei_percorsi():
    """La cartella dei percorsi di rete salvati, nel profilo di chi usa Windows."""
    return os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Network Shortcuts")


def e_di_rete(percorso):
    r"""Vero per un percorso di rete, come \\server\cartella."""
    return percorso.startswith("\\\\")


def _bersaglio(collegamento):
    """Il percorso a cui punta un file .lnk, o None."""
    import pythoncom
    from win32com.shell import shell

    link = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
    link.QueryInterface(pythoncom.IID_IPersistFile).Load(collegamento)
    percorso = link.GetPath(shell.SLGP_RAWPATH)[0]
    if not percorso:
        lista = link.GetIDList()
        percorso = shell.SHGetPathFromIDList(lista).decode("mbcs", "replace") if lista else ""
    return percorso or None


def percorsi_salvati(cartella=None):
    r"""I percorsi di rete salvati in Windows: lista di (nome, percorso), per
    esempio ("iliadbox (iliadbox_Server)", "\\iliadbox_Server\iliadbox"), in
    ordine di nome. Restano solo le cartelle di rete: i percorsi FTP o web
    non sono cartelle che MeTeOra sa leggere."""
    cartella = cartella or cartella_dei_percorsi()
    try:
        voci = sorted(os.scandir(cartella), key=lambda v: v.name.casefold())
    except OSError:
        return []
    trovati = []
    for voce in voci:
        if voce.is_dir():
            nome, collegamento = voce.name, os.path.join(voce.path, "target.lnk")
        elif voce.name.lower().endswith(".lnk"):
            nome, collegamento = voce.name[:-4], voce.path
        else:
            continue
        percorso = None
        with contextlib.suppress(Exception):
            percorso = _bersaglio(collegamento)
        if percorso and e_di_rete(percorso):
            trovati.append((nome, percorso.rstrip("\\")))
    return trovati


def _figli_nella_shell(percorso=None):
    r"""(nome, percorso) delle cartelle che la shell mostra dentro la cartella
    Rete (percorso None) o dentro \\computer: computer e cartelle condivise.
    Da chiamare in un filo a parte, che qui inizializza COM."""
    import pythoncom
    from win32com.shell import shell, shellcon

    pythoncom.CoInitialize()
    try:
        scrivania = shell.SHGetDesktopFolder()
        if percorso is None:
            lista = shell.SHGetSpecialFolderLocation(0, shellcon.CSIDL_NETWORK)
        else:
            lista = scrivania.ParseDisplayName(0, None, percorso)[1]
        cartella = scrivania.BindToObject(lista, None, shell.IID_IShellFolder)
        figli = []
        for figlio in cartella.EnumObjects(0, shellcon.SHCONTF_FOLDERS) or []:
            nome = cartella.GetDisplayNameOf(figlio, shellcon.SHGDN_NORMAL)
            completo = cartella.GetDisplayNameOf(figlio, shellcon.SHGDN_FORPARSING)
            if e_di_rete(completo):
                figli.append((nome, completo))
        return sorted(figli, key=lambda f: f[0].casefold())
    finally:
        pythoncom.CoUninitialize()


def computer():
    r"""I computer della cartella Rete: lista di (nome, \\nome). Puo' durare
    secondi, e su molti Windows e' vuota; un errore vale come nessuno."""
    try:
        return [(nome, percorso) for nome, percorso in _figli_nella_shell() if percorso.count("\\") == 2]
    except Exception:  # noqa: BLE001 - la shell e COM falliscono in molti modi: nessun computer
        return []


def condivisioni(server):
    r"""Le cartelle condivise di \\server: lista di (nome, percorso). Un
    computer che non risponde o non condivide niente da' la lista vuota."""
    try:
        return [(nome, percorso) for nome, percorso in _figli_nella_shell(server) if percorso.lower().startswith(server.lower() + "\\")]
    except Exception:  # noqa: BLE001 - come sopra
        return []


def raggiungibile(percorso, attesa=ATTESA_DELLA_RETE):
    """Vero se la cartella risponde entro attesa secondi. La prova continua
    da sola nel suo filo, se Windows la fa aspettare di piu'."""
    esito = []
    filo = threading.Thread(target=lambda: esito.append(os.path.isdir(percorso)), name="MeTeOra, prova della rete", daemon=True)
    filo.start()
    filo.join(attesa)
    return bool(esito and esito[0])


def in_disparte(lavoro, al_termine):
    """Fa lavoro() in un filo a parte e passa il risultato ad al_termine, che
    chi chiama riporta nel suo filo."""
    threading.Thread(target=lambda: al_termine(lavoro()), name="MeTeOra, ricerca nella rete", daemon=True).start()
