# MeTeOra, l'installazione fatta con il setup: la versione in App installate.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/10/2026: nasce con la 1.97.0, con l'installatore di Inno Setup.

"""La versione di MeTeOra in App installate (1.97.0).

L'installatore di Inno Setup (MeTeOra.iss) scrive la voce della
disinstallazione in HKCU, con la versione installata. L'aggiornamento
automatico pero' sostituisce i file senza passare dall'installatore, e la
voce resterebbe ferma alla versione di partenza. All'avvio, dal programma
compilato, aggiorna_la_versione() la corregge, ma solo se la voce e' quella
di questa cartella: una copia portatile, da zip, accanto a una installata non
la tocca.
"""

import os
import winreg

# AppId di MeTeOra.iss, con il suffisso che Inno Setup aggiunge.
CHIAVE = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{64985198-5673-4D67-A490-35A62886C1F2}_is1"


def _stessa_cartella(una, altra):
    return os.path.normcase(os.path.normpath(una)) == os.path.normcase(os.path.normpath(altra))


def aggiorna_la_versione(versione, cartella, reg=winreg):
    """Scrive versione nella voce di App installate, se MeTeOra e' installato
    in cartella e la voce dice un'altra versione. Torna vero se l'ha scritta.
    Ogni problema del registro si tace: e' solo un'etichetta."""
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, CHIAVE, 0, reg.KEY_READ | reg.KEY_WRITE) as chiave:
            luogo, _tipo = reg.QueryValueEx(chiave, "InstallLocation")
            if not _stessa_cartella(luogo, cartella):
                return False
            try:
                attuale, _tipo = reg.QueryValueEx(chiave, "DisplayVersion")
            except OSError:
                attuale = None
            if attuale == versione:
                return False
            reg.SetValueEx(chiave, "DisplayVersion", 0, reg.REG_SZ, versione)
            return True
    except OSError:
        return False
