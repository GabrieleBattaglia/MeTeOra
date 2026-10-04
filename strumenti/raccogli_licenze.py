# MeTeOra, utilita': raccoglie nella cartella licenze i testi delle licenze dei componenti e i loro sorgenti esatti.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.85.0, per la prima release. Nella 1.85.2 i testi scaricati da scarica_licenze.py.

"""Prepara la cartella licenze, che il pacchetto porta accanto all'eseguibile.

MeTeOra e' GPL-3.0-or-later, e la libmpv che suona quasi tutto e' una build
GPL 3. Chi distribuisce il programma compilato deve dare, con lui, i testi
delle licenze dei componenti e l'accesso al loro codice sorgente esatto
(GPL 3, sezioni 4 e 6). La cartella si fa con questo script e si committa;
va rifatta quando cambia una libreria, prima di compilare.

I testi vengono da dove sono gia' sul disco: i dist-info dei pacchetti
Python, il LICENSE.txt di Python, le licenze dei pacchetti MSYS2 da cui
vengono le DLL di lib. Le versioni si leggono dai pacchetti installati, dal
database di pacman e da prepara_ambiente.py per libmpv; e lo script controlla
che le DLL di lib siano proprio quelle dei pacchetti MSYS2 che nomina.
MSYS2 si cerca come in prepara_ambiente.py, nella cartella di METEORA_MSYS2
o in strumenti/msys64, ma qui non si scarica. I testi che sul disco non ci
sono, quelli delle librerie dentro libmpv, dei pacchetti winrt e di FluidR3 GM,
li scarica prima scarica_licenze.py, con il loro elenco in
strumenti/licenze_scaricate.json: qui si leggono e si nominano.

Lo script scrive e sovrascrive, non cancella: alla fine elenca i file della
cartella che non ha scritto, da togliere a mano se non servono piu'.
Uso: python strumenti/raccogli_licenze.py
"""

import contextlib
import hashlib
import importlib.metadata as metadati
import json
import os
import shutil
import subprocess
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)
sys.path.insert(0, os.path.join(RADICE, "strumenti"))

import prepara_ambiente  # noqa: E402

import version  # noqa: E402

LICENZE = os.path.join(RADICE, "licenze")
SCARICATE = os.path.join(RADICE, "strumenti", "licenze_scaricate.json")
LIB = os.path.join(RADICE, "lib")
REPOSITORY = "https://github.com/GabrieleBattaglia/MeTeOra"
SEGNALAZIONI = f"{REPOSITORY}/issues"

# I pacchetti Python che PyInstaller mette nel pacchetto: nome della
# distribuzione, a che cosa serve, licenza SPDX. La licenza si scrive qui,
# perche' nei metadati di alcuni manca o e' tutto il testo.
PYTHON = [
    ("python-mpv", "il collegamento con libmpv", "GPL-2.0-or-later OR LGPL-2.1-or-later, usato come GPL"),
    ("mutagen", "le durate e i tag dei file audio", "GPL-2.0-or-later"),
    ("wxPython", "l'interfaccia, con le DLL di wxWidgets", "LGPL-2.0-or-later WITH WxWindows-exception-3.1"),
    ("accessible_output2", "la sintesi e il braille degli screen reader", "MIT"),
    ("libloader", "il caricamento delle DLL di accessible_output2", "MIT"),
    ("platform_utils", "le cartelle di sistema per accessible_output2", "MIT"),
    ("pywin32", "le cartelle di rete e la voce di Windows", "PSF-2.0"),
    ("numpy", "i calcoli degli effetti sonori", "BSD-3-Clause, con OpenBLAS e il runtime di GCC"),
    ("scipy", "la sintesi degli effetti sonori di Acusticator", "BSD-3-Clause, con OpenBLAS e il runtime di GCC"),
    ("pillow", "le immagini del riconoscimento dei caratteri", "MIT-CMU"),
    ("winrt-runtime", "il riconoscimento dei caratteri di Windows, con i moduli winrt", "MIT"),
    ("sounddevice", "il suono degli effetti, con PortAudio", "MIT"),
    ("cffi", "il collegamento di sounddevice con PortAudio", "MIT-0"),
    ("pycparser", "per cffi", "BSD-3-Clause"),
    ("requests", "gli scaricamenti e l'aggiornamento automatico", "Apache-2.0"),
    ("urllib3", "per requests", "MIT"),
    ("idna", "per requests", "BSD-3-Clause"),
    ("charset_normalizer", "per requests", "MIT"),
    ("certifi", "i certificati per requests", "MPL-2.0"),
    ("platformdirs", "le cartelle di sistema", "MIT"),
    ("typing_extensions", "per i pacchetti qui sopra", "PSF-2.0"),
    ("pyinstaller", "il pacchetto, con il suo avviatore", "GPL-2.0-or-later WITH Bootloader-exception"),
]
# I moduli winrt del riconoscimento dei caratteri, con winrt-runtime.
WINRT = ["winrt-Windows.Foundation", "winrt-Windows.Foundation.Collections", "winrt-Windows.Globalization", "winrt-Windows.Graphics.Imaging",
    "winrt-Windows.Media.Ocr", "winrt-Windows.Storage.Streams"]

# Le DLL di lib che vengono da MSYS2: pacchetto, DLL, a che cosa serve,
# licenza SPDX. Il pacchetto e' il nome dopo mingw-w64-ucrt-x86_64-.
MSYS2 = [
    ("libsidplayfp", "libsidplayfp-6.dll", "i SID del Commodore 64, con l'emulazione reSIDfp", "GPL-2.0-or-later"),
    ("libgcrypt", "libgcrypt-20.dll", "per libsidplayfp", "LGPL-2.1-or-later"),
    ("libgpg-error", "libgpg-error-0.dll", "per libgcrypt", "LGPL-2.1-or-later"),
    ("libusb", "libusb-1.0.dll", "per libsidplayfp", "LGPL-2.1-or-later"),
    ("libgme", "libgme.dll", "la musica delle console, Game Music Emu", "LGPL-2.1-or-later"),
    ("zlib", "zlib1.dll", "per libgme", "Zlib"),
    ("libgcc", "libgcc_s_seh-1.dll", "il runtime di GCC per sidshim e libsidplayfp", "GPL-3.0-or-later WITH GCC-exception-3.1"),
    ("libstdc++", "libstdc++-6.dll", "il runtime C++ di GCC per sidshim e libsidplayfp", "GPL-3.0-or-later WITH GCC-exception-3.1"),
    ("libwinpthread", "libwinpthread-1.dll", "i thread di mingw-w64", "MIT AND BSD-3-Clause-Clear"),
]

# Le parole che, nel percorso, fanno riconoscere un file di licenza fra
# quelli di un pacchetto Python installato.
FILE_DI_LICENZA = ("LICEN", "COPYING", "NOTICE", "AUTHORS")


def trova_msys2():
    for candidato in (os.environ.get("METEORA_MSYS2"), os.path.join(RADICE, "strumenti", "msys64")):
        if candidato and os.path.isdir(os.path.join(candidato, "ucrt64")):
            return candidato
    sys.exit("MSYS2 non trovato: indica la sua cartella nella variabile METEORA_MSYS2.")


def impronta(percorso):
    h = hashlib.sha256()
    with open(percorso, "rb") as f:
        for blocco in iter(lambda: f.read(1 << 20), b""):
            h.update(blocco)
    return h.hexdigest()


class Raccolta:
    def __init__(self):
        self.scritti = set()

    def copia(self, origine, destinazione):
        """Copia un file nella cartella licenze; destinazione e' relativa."""
        arrivo = os.path.join(LICENZE, destinazione)
        os.makedirs(os.path.dirname(arrivo), exist_ok=True)
        shutil.copyfile(origine, arrivo)
        self.scritti.add(os.path.normcase(os.path.abspath(arrivo)))

    def scrivi(self, destinazione, righe):
        arrivo = os.path.join(LICENZE, destinazione)
        os.makedirs(os.path.dirname(arrivo), exist_ok=True)
        with open(arrivo, "w", encoding="utf-8") as f:
            f.write("\n".join(righe) + "\n")
        self.scritti.add(os.path.normcase(os.path.abspath(arrivo)))

    def gia_scritto(self, destinazione):
        """Un file messo nella cartella da scarica_licenze.py, che deve esserci."""
        arrivo = os.path.join(LICENZE, destinazione)
        if not os.path.isfile(arrivo):
            sys.exit(f"Manca licenze\\{destinazione}: rifai scarica_licenze.py.")
        self.scritti.add(os.path.normcase(os.path.abspath(arrivo)))

    def superati(self):
        """I file della cartella che questa raccolta non ha scritto."""
        restano = []
        for radice, _cartelle, file in os.walk(LICENZE):
            for nome in file:
                percorso = os.path.normcase(os.path.abspath(os.path.join(radice, nome)))
                if percorso not in self.scritti:
                    restano.append(os.path.relpath(percorso, LICENZE))
        return sorted(restano)


def file_di_licenza(distribuzione):
    """I file di licenza di un pacchetto installato: (origine, nome relativo)."""
    trovati = []
    for voce in distribuzione.files or ():
        testo = str(voce).replace("\\", "/")
        if not any(chiave in testo.upper() for chiave in FILE_DI_LICENZA):
            continue
        # Nei dist-info si toglie la cartella; gli altri tengono il percorso.
        relativo = testo.split(".dist-info/", 1)[1].removeprefix("licenses/") if ".dist-info/" in testo else testo
        trovati.append((str(distribuzione.locate_file(voce)), relativo))
    return trovati


def pacchetto_msys2(msys2, nome):
    """Versione e pacchetto sorgente (%BASE%) dal database di pacman."""
    locale = os.path.join(msys2, "var", "lib", "pacman", "local")
    prefisso = f"mingw-w64-ucrt-x86_64-{nome}-"
    for cartella in os.listdir(locale):
        if not cartella.startswith(prefisso):
            continue
        campi, chiave = {}, None
        with open(os.path.join(locale, cartella, "desc"), encoding="utf-8") as f:
            for riga in f.read().splitlines():
                if riga.startswith("%") and riga.endswith("%"):
                    chiave = riga.strip("%")
                elif riga and chiave and chiave not in campi:
                    campi[chiave] = riga
        if campi.get("NAME") == f"mingw-w64-ucrt-x86_64-{nome}":
            return campi["VERSION"], campi["BASE"]
    sys.exit(f"Il pacchetto MSYS2 di {nome} non e' installato in {msys2}.")


def commit_di_gbutils():
    import GBUtils

    cartella = os.path.dirname(os.path.abspath(GBUtils.__file__))
    git = shutil.which("git")
    commit = ""
    if git:
        with contextlib.suppress(OSError, subprocess.CalledProcessError):
            # Un comando fisso, con il solo percorso di GBUtils come argomento.
            commit = subprocess.run([git, "-C", cartella, "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()  # noqa: S603
    return GBUtils.VERSION, commit


def main():
    msys2 = trova_msys2()
    raccolta = Raccolta()
    with open(SCARICATE, encoding="utf-8") as f:
        scaricate = json.load(f)
    if scaricate["build"] != prepara_ambiente.MPV_BUILD:
        sys.exit(f"I testi scaricati sono della build {scaricate['build']} di libmpv, non della {prepara_ambiente.MPV_BUILD}: rifai scarica_licenze.py.")
    altri = {voce["nome"]: voce for voce in scaricate["altri"]}
    for voce in scaricate["altri"]:
        for file in voce["file"]:
            raccolta.gia_scritto(os.path.join(voce["nome"], file))
    leggimi = [
        f"Le licenze dei componenti di MeTeOra {version.VERSION}.",
        "MeTeOra è copyright 2026 di Gabriele Battaglia (IZ4APU), software libero sotto la GNU General Public License, versione 3 o, a tua "
        "scelta, qualunque versione successiva (GPL-3.0-or-later), senza alcuna garanzia. Il testo è nel file LICENSE accanto al "
        "programma, e una copia in testi\\GPL-3.0.txt.",
        "Qui sotto, un componente per riga: a che cosa serve, la versione, la licenza e dove sono i suoi testi in questa cartella. "
        "Il file SORGENTI.txt dice dove trovare il codice sorgente esatto di ognuno.",
    ]
    sorgenti = [
        f"Il codice sorgente dei componenti di MeTeOra {version.VERSION}.",
        "Il codice sorgente corrispondente di ogni componente incluso nel pacchetto si trova agli indirizzi qui sotto, alla versione "
        f"esatta. Se uno non fosse più raggiungibile, chiedilo con una segnalazione su {SEGNALAZIONI} e lo riceverai.",
    ]
    # I testi comuni, che le righe dei componenti nominano.
    raccolta.copia(os.path.join(RADICE, "LICENSE"), os.path.join("testi", "GPL-3.0.txt"))
    raccolta.copia(metadati.distribution("mutagen").locate_file("mutagen-{}.dist-info/licenses/COPYING".format(metadati.version("mutagen"))),
        os.path.join("testi", "GPL-2.0.txt"))
    mpv_python = metadati.distribution("python-mpv")
    raccolta.copia(mpv_python.locate_file(f"python_mpv-{mpv_python.version}.dist-info/licenses/LICENSE.LGPL"), os.path.join("testi", "LGPL-2.1.txt"))
    raccolta.copia(os.path.join(msys2, "ucrt64", "share", "licenses", "gcc", "COPYING.RUNTIME"), os.path.join("testi", "GCC-exception-3.1.txt"))

    # MeTeOra, sidshim e GBUtils.
    leggimi.append(f"MeTeOra {version.VERSION}, con sidshim.dll, il suo ponte verso libsidplayfp: GPL-3.0-or-later, testi\\GPL-3.0.txt.")
    sorgenti.append(f"MeTeOra {version.VERSION}, con sidshim.dll e lo script che prepara le librerie (strumenti\\prepara_ambiente.py): "
        f"{REPOSITORY}, alla release della versione {version.VERSION}.")
    versione_gbutils, commit = commit_di_gbutils()
    leggimi.append(f"GBUtils V{versione_gbutils}, la libreria di Gabriele, con gli effetti sonori di Acusticator: GPL-3.0, testi\\GPL-3.0.txt.")
    sorgenti.append(f"GBUtils V{versione_gbutils}: https://github.com/GabrieleBattaglia/GBUtils" + (f"/tree/{commit}" if commit else "") + ".")

    # libmpv, dalla build fissata in prepara_ambiente.py.
    dll_mpv = os.path.join(LIB, "libmpv-2.dll")
    leggimi.append(f"libmpv-2.dll, la riproduzione: mpv {prepara_ambiente.MPV_COMMIT} con FFmpeg {prepara_ambiente.FFMPEG_COMMIT}, libopenmpt "
        f"e le altre librerie della build {prepara_ambiente.MPV_BUILD} di shinchiro/mpv-winbuild-cmake: GPL-3.0-or-later nel suo insieme, "
        "testi\\GPL-3.0.txt; mpv è GPL-2.0-or-later con parti LGPL-2.1-or-later, testi\\GPL-2.0.txt e testi\\LGPL-2.1.txt. Le librerie che "
        "contiene sono nelle righe seguenti, ciascuna con i file di licenza del suo progetto, nella cartella libmpv.")
    for voce in scaricate["libmpv"]:
        testi = []
        for file in voce["file"]:
            raccolta.gia_scritto(os.path.join("libmpv", voce["nome"], file))
            testi.append(f"libmpv\\{voce['nome']}\\{file}")
        dove = " e ".join(testi)
        if voce.get("licenza"):
            dove = f"{voce['licenza']}" + (f", {dove}" if dove else "")
        leggimi.append(f"{voce['nome']}, dentro libmpv-2.dll: {dove}.")
    sorgenti.append(f"libmpv-2.dll, build {prepara_ambiente.MPV_BUILD} di shinchiro, impronta SHA-256 {impronta(dll_mpv)}:")
    sorgenti.append(f"mpv: https://github.com/mpv-player/mpv/tree/{prepara_ambiente.MPV_COMMIT}")
    sorgenti.append(f"FFmpeg: https://github.com/FFmpeg/FFmpeg/tree/{prepara_ambiente.FFMPEG_COMMIT}")
    sorgenti.append(f"Gli script della build, con l'elenco e la provenienza di ogni libreria inclusa (cartella packages): "
        f"https://github.com/shinchiro/mpv-winbuild-cmake/tree/{prepara_ambiente.WINBUILD_COMMIT}")
    sorgenti.append(f"La build: https://github.com/shinchiro/mpv-winbuild-cmake/releases/tag/{prepara_ambiente.MPV_BUILD}")
    sorgenti.append(f"Le librerie dentro libmpv-2.dll, dai loro repository; la build {prepara_ambiente.MPV_BUILD} ha preso quelle senza una "
        "versione fissata negli script dal ramo principale del giorno della build:")
    for voce in scaricate["libmpv"]:
        if voce["nome"] not in ("mpv", "ffmpeg"):
            sorgenti.append(f"{voce['nome']}: {voce['repository']}")

    # Le DLL di MSYS2, controllate una per una.
    for nome, dll, ruolo, licenza in MSYS2:
        versione, base = pacchetto_msys2(msys2, nome)
        nostra, sua = os.path.join(LIB, dll), os.path.join(msys2, "ucrt64", "bin", dll)
        if impronta(nostra) != impronta(sua):
            sys.exit(f"lib\\{dll} non è quella del pacchetto MSYS2 {nome} {versione}: rifai lib con prepara_ambiente.py.")
        cartella = os.path.join(msys2, "ucrt64", "share", "licenses", nome)
        testi = []
        for file in sorted(os.listdir(cartella)):
            raccolta.copia(os.path.join(cartella, file), os.path.join(nome, file))
            testi.append(f"{nome}\\{file}")
        leggimi.append(f"{dll}, {ruolo}: {nome} {versione}, {licenza}, " + " e ".join(testi) + ".")
        sorgenti.append(f"{nome} {versione}: https://repo.msys2.org/mingw/sources/{base}-{versione}.src.tar.zst")

    # Le DLL di accessible_output2 che restano nel pacchetto: il client di NVDA.
    import accessible_output2

    client = os.path.join(os.path.dirname(accessible_output2.__file__), "lib", "nvdaControllerClient64.dll")
    leggimi.append("nvdaControllerClient64.dll, il collegamento con NVDA, dentro accessible_output2: LGPL-2.1, testi\\LGPL-2.1.txt.")
    sorgenti.append(f"nvdaControllerClient64.dll, impronta SHA-256 {impronta(client)}: https://github.com/nvaccess/nvda/tree/master/extras/controllerClient")

    # Python e i pacchetti.
    versione_python = ".".join(map(str, sys.version_info[:3]))
    raccolta.copia(os.path.join(sys.base_prefix, "LICENSE.txt"), os.path.join("python", "LICENSE.txt"))
    leggimi.append(f"Python {versione_python}, della Python Software Foundation, con OpenSSL, libffi e le altre parti che contiene: PSF-2.0, "
        "python\\LICENSE.txt, che elenca anche le licenze delle parti.")
    sorgenti.append(f"Python {versione_python}: https://www.python.org/downloads/release/python-{versione_python.replace('.', '')}/")
    for nome, ruolo, licenza in PYTHON:
        distribuzione = metadati.distribution(nome)
        versione = distribuzione.version
        cartella = f"{nome}-{versione}"
        testi = []
        for origine, relativo in file_di_licenza(distribuzione):
            raccolta.copia(origine, os.path.join("python", cartella, relativo))
            testi.append(relativo)
        dove = f"python\\{cartella}" if testi else "winrt\\" + " e winrt\\".join(altri["winrt"]["file"])
        extra = ""
        if nome == "winrt-runtime":
            moduli = ", ".join(f"{m} {metadati.version(m)}" for m in WINRT)
            extra = f", con {moduli}"
        leggimi.append(f"{nome} {versione}{extra}, {ruolo}: {licenza}, {dove}.")
        sorgenti.append(f"{nome} {versione}: https://pypi.org/project/{nome}/{versione}/#files")
        if nome == "winrt-runtime":
            sorgenti.append(f"I moduli winrt: {altri['winrt']['repository']}")

    # I componenti che MeTeOra non porta con se'.
    leggimi.append("Non sono nel pacchetto, e MeTeOra li scarica solo quando servono: FluidSynth 2.6.1 con libsndfile, per i MIDI, "
        "LGPL-2.1-or-later, dal sito di FluidSynth; il banco di suoni FluidR3 GM di Frank Wen, licenza MIT, se lo chiedi, con il testo in "
        + " e ".join(f"fluidr3\\{file}" for file in altri["fluidr3"]["file"]) + ". "
        "Le durate dei SID vengono dal database Songlengths della High Voltage SID Collection, che MeTeOra legge dalla tua copia.")
    sorgenti.append("FluidSynth: https://github.com/FluidSynth/fluidsynth; FluidR3 GM: https://github.com/pianobooster/fluid-soundfont")

    raccolta.scrivi("LEGGIMI.txt", leggimi)
    raccolta.scrivi("SORGENTI.txt", sorgenti)
    print(f"Cartella licenze pronta: {len(raccolta.scritti)} file.")
    restano = raccolta.superati()
    if restano:
        print("File che questa raccolta non ha scritto, da togliere se non servono più:")
        for nome in restano:
            print(nome)
    return 0


if __name__ == "__main__":
    sys.exit(main())
