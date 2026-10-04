# MeTeOra, preparazione dell'ambiente di sviluppo: scarica e compila le librerie native.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 29/09/2026: nasce con il repository. Nella 1.66.0 anche libgme, per la musica delle console. Nella 1.85.0 la build di libmpv fissata.

"""Mette in lib/ le DLL che il repository non contiene.

1. libmpv-2.dll: la build MPV_BUILD di shinchiro/mpv-winbuild-cmake da
   GitHub, con l'impronta dell'archivio controllata. E' fissata perche' gli
   avvisi della cartella licenze nominano i sorgenti esatti di quella build
   (1.85.0): per cambiarla si aggiornano qui la build, l'archivio, la sua
   impronta e i tre commit, poi si rifa' la cartella licenze con
   raccogli_licenze.py. shinchiro toglie le build vecchie: se questa sparisce,
   va scelta la nuova.
2. sidshim.dll: compilata da sidshim/sidshim.cpp con MSYS2 (UCRT64), insieme
   a libsidplayfp e alle altre DLL di cui ha bisogno.
3. libgme.dll, per la musica delle console (tappa 8): dal pacchetto MSYS2
   di libgme, con le DLL di cui ha bisogno.

MSYS2 si cerca nella cartella indicata dalla variabile METEORA_MSYS2, poi in
strumenti/msys64; se non c'e' si scarica la versione portatile in
strumenti/msys64, che git ignora. Serve 7-Zip installato.
Uso: python strumenti/prepara_ambiente.py [--solo-mpv | --solo-sid | --solo-gme]
"""

import hashlib
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
# La build di libmpv (1.85.0): il tag della release di shinchiro, l'archivio
# e la sua impronta, come li da' GitHub; i commit di mpv e FFmpeg dentro la
# DLL (mpv-version e ffmpeg-version), e quello degli script della build, dal
# lavoro di GitHub che l'ha prodotta.
MPV_BUILD = "20260928"
MPV_ARCHIVIO = "mpv-dev-x86_64-20260928-git-e470f8986e.7z"
MPV_IMPRONTA = "81795d759e01016f1550fd71651a1a5d59ab5c28ef31c0b6793224e9cff39459"
MPV_COMMIT = "e470f8986e"
FFMPEG_COMMIT = "939c2c733"
WINBUILD_COMMIT = "05a60b3cfd04e3e3b89918f4a27f3dde2935dff2"


def scarica(url, destinazione):
    print(f"Scarico {url}", flush=True)
    richiesta = urllib.request.Request(url, headers={"User-Agent": "MeTeOra"})  # noqa: S310
    with urllib.request.urlopen(richiesta) as risposta, open(destinazione, "wb") as f:  # noqa: S310
        shutil.copyfileobj(risposta, f)


def prepara_mpv():
    url = f"https://api.github.com/repos/shinchiro/mpv-winbuild-cmake/releases/tags/{MPV_BUILD}"
    richiesta = urllib.request.Request(url, headers={"User-Agent": "MeTeOra"})
    with urllib.request.urlopen(richiesta) as risposta:  # noqa: S310
        rilascio = json.load(risposta)
    asset = next((a for a in rilascio["assets"] if a["name"] == MPV_ARCHIVIO), None)
    if asset is None:
        sys.exit(f"La build {MPV_BUILD} di libmpv non ha piu' l'archivio {MPV_ARCHIVIO}: va scelta una build nuova.")
    with tempfile.TemporaryDirectory() as cartella:
        archivio = os.path.join(cartella, asset["name"])
        scarica(asset["browser_download_url"], archivio)
        with open(archivio, "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != MPV_IMPRONTA:
                sys.exit(f"L'archivio {MPV_ARCHIVIO} non ha l'impronta attesa: non lo uso.")
        subprocess.run([SETTEZIP, "e", "-y", f"-o{LIB}", archivio, "libmpv-2.dll"], check=True, stdout=subprocess.DEVNULL)
    print(f"libmpv-2.dll pronta, build {MPV_BUILD}", flush=True)


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
