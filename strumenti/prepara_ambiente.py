# MeTeOra, preparazione dell'ambiente di sviluppo: scarica e compila le librerie native.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 29/09/2026: nasce con il repository. Nella 1.66.0 anche libgme, per la musica delle console.

"""Mette in lib/ le DLL che il repository non contiene.

1. libmpv-2.dll: l'ultima build di shinchiro/mpv-winbuild-cmake da GitHub.
2. sidshim.dll: compilata da sidshim/sidshim.cpp con MSYS2 (UCRT64), insieme
   a libsidplayfp e alle altre DLL di cui ha bisogno.
3. libgme.dll, per la musica delle console (tappa 8): dal pacchetto MSYS2
   di libgme, con le DLL di cui ha bisogno.

MSYS2 si cerca nella cartella indicata dalla variabile METEORA_MSYS2, poi in
strumenti/msys64; se non c'e' si scarica la versione portatile in
strumenti/msys64, che git ignora. Serve 7-Zip installato.
Uso: python strumenti/prepara_ambiente.py [--solo-mpv | --solo-sid | --solo-gme]
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(RADICE, "lib")
SETTEZIP = r"C:\Program Files\7-Zip\7z.exe"
MSYS2_URL = "https://github.com/msys2/msys2-installer/releases/download/nightly-x86_64/msys2-base-x86_64-latest.sfx.exe"
PACCHETTI = ["mingw-w64-ucrt-x86_64-gcc", "mingw-w64-ucrt-x86_64-libsidplayfp", "mingw-w64-ucrt-x86_64-pkgconf"]
PACCHETTO_GME = "mingw-w64-ucrt-x86_64-libgme"


def scarica(url, destinazione):
    print(f"Scarico {url}", flush=True)
    richiesta = urllib.request.Request(url, headers={"User-Agent": "MeTeOra"})  # noqa: S310
    with urllib.request.urlopen(richiesta) as risposta, open(destinazione, "wb") as f:  # noqa: S310
        shutil.copyfileobj(risposta, f)


def prepara_mpv():
    richiesta = urllib.request.Request("https://api.github.com/repos/shinchiro/mpv-winbuild-cmake/releases/latest", headers={"User-Agent": "MeTeOra"})
    with urllib.request.urlopen(richiesta) as risposta:  # noqa: S310
        rilascio = json.load(risposta)
    asset = next(a for a in rilascio["assets"] if re.fullmatch(r"mpv-dev-x86_64-\d{8}-git-\w+\.7z", a["name"]))
    with tempfile.TemporaryDirectory() as cartella:
        archivio = os.path.join(cartella, asset["name"])
        scarica(asset["browser_download_url"], archivio)
        subprocess.run([SETTEZIP, "e", "-y", f"-o{LIB}", archivio, "libmpv-2.dll"], check=True, stdout=subprocess.DEVNULL)
    print(f"libmpv-2.dll pronta, build {rilascio['tag_name']}", flush=True)


def trova_msys2():
    for candidato in (os.environ.get("METEORA_MSYS2"), os.path.join(RADICE, "strumenti", "msys64")):
        if candidato and os.path.isfile(os.path.join(candidato, "usr", "bin", "bash.exe")):
            return candidato
    destinazione = os.path.join(RADICE, "strumenti")
    with tempfile.TemporaryDirectory() as cartella:
        sfx = os.path.join(cartella, "msys2.sfx.exe")
        scarica(MSYS2_URL, sfx)
        subprocess.run([sfx, "-y", f"-o{destinazione}"], check=True, stdout=subprocess.DEVNULL)
    return os.path.join(destinazione, "msys64")


def bash(msys2, comando):
    ambiente = dict(os.environ, MSYSTEM="UCRT64", CHERE_INVOKING="1")
    return subprocess.run([os.path.join(msys2, "usr", "bin", "bash.exe"), "-lc", comando], env=ambiente, cwd=os.path.join(RADICE, "sidshim"),
        check=True, capture_output=True, text=True).stdout


def prepara_sid():
    msys2 = trova_msys2()
    print(f"MSYS2 in {msys2}", flush=True)
    bash(msys2, "pacman -S --noconfirm --needed " + " ".join(PACCHETTI))
    uscita = os.path.join(LIB, "sidshim.dll").replace("\\", "/")
    bash(msys2, f"g++ -O2 -shared -o '{uscita}' sidshim.cpp $(pkg-config --cflags --libs libsidplayfp) -static-libgcc -static-libstdc++")
    # Le dipendenze che non sono di Windows arrivano da /ucrt64/bin.
    dipendenze = re.findall(r"=> /ucrt64/bin/(\S+\.dll)", bash(msys2, f"ldd '{uscita}'"))
    for nome in dipendenze:
        shutil.copy2(os.path.join(msys2, "ucrt64", "bin", nome), LIB)
    versione = bash(msys2, "pkg-config --modversion libsidplayfp").strip()
    print(f"sidshim.dll pronta con libsidplayfp {versione}, dipendenze copiate: {', '.join(dipendenze)}", flush=True)


def prepara_gme():
    msys2 = trova_msys2()
    print(f"MSYS2 in {msys2}", flush=True)
    bash(msys2, f"pacman -S --noconfirm --needed {PACCHETTO_GME}")
    shutil.copy2(os.path.join(msys2, "ucrt64", "bin", "libgme.dll"), LIB)
    dipendenze = re.findall(r"=> /ucrt64/bin/(\S+\.dll)", bash(msys2, "ldd /ucrt64/bin/libgme.dll"))
    for nome in dipendenze:
        shutil.copy2(os.path.join(msys2, "ucrt64", "bin", nome), LIB)
    versione = bash(msys2, f"pacman -Q {PACCHETTO_GME}").split()[-1]
    print(f"libgme.dll pronta, versione {versione}, dipendenze copiate: {', '.join(dipendenze)}", flush=True)


if __name__ == "__main__":
    os.makedirs(LIB, exist_ok=True)
    solo = next((a for a in sys.argv[1:] if a.startswith("--solo-")), None)
    if solo in (None, "--solo-mpv"):
        prepara_mpv()
    if solo in (None, "--solo-sid"):
        prepara_sid()
    if solo in (None, "--solo-gme"):
        prepara_gme()
