# MeTeOra, utilita': compila l'installatore con Inno Setup.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/10/2026: nasce con la 1.97.0, per la prima release.

"""Compila MeTeOra.iss con il compilatore di Inno Setup 6, passandogli la
versione di version.py, e scrive MeTeOra-Setup-<versione>.exe nella
cartella del progetto, accanto a MeTeOra.zip.

Si lancia dopo PyInstaller e zip_maker.py, dalla cartella del progetto:
l'installatore prende dist/MeTeOra com'e', quindi va ripulita prima, come per
l'archivio (prontuario, fase 7.0). Il compilatore si cerca nella variabile
METEORA_ISCC, poi sulla path, poi nelle cartelle dove Inno Setup si installa.
"""

import os
import shutil
import subprocess
import sys

import version


def compilatore():
    """Il percorso di ISCC.exe, o None."""
    candidati = [os.environ.get("METEORA_ISCC"), shutil.which("iscc")]
    if os.environ.get("LOCALAPPDATA"):
        candidati.append(os.path.join(os.environ["LOCALAPPDATA"], "Programs", "Inno Setup 6", "ISCC.exe"))
    for radice in (os.environ.get("PROGRAMFILES(X86)"), os.environ.get("PROGRAMFILES")):
        if radice:
            candidati.append(os.path.join(radice, "Inno Setup 6", "ISCC.exe"))
    return next((c for c in candidati if c and os.path.isfile(c)), None)


def main():
    iscc = compilatore()
    if iscc is None:
        print("Installatore non creato: non trovo ISCC.exe di Inno Setup 6. Indica il percorso con la variabile METEORA_ISCC.")
        return 1
    if not os.path.isfile(os.path.join("dist", "MeTeOra", "MeTeOra.exe")):
        print("Installatore non creato: manca dist\\MeTeOra\\MeTeOra.exe. Compila prima con PyInstaller.")
        return 1
    esito = subprocess.run([iscc, "/Q", f"/DVersione={version.VERSION}", "MeTeOra.iss"], check=False)  # noqa: S603 - il compilatore trovato qui sopra
    if esito.returncode:
        print(f"Installatore non creato: ISCC ha finito con il codice {esito.returncode}.")
        return esito.returncode
    print(f"Installatore creato: MeTeOra-Setup-{version.VERSION}.exe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
