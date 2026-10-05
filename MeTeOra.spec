# MeTeOra, la ricetta di PyInstaller: il pacchetto a cartella (prontuario, premessa).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la prova del pacchetto, prima della tappa 11. Nella 1.85.0 le DLL e i pacchetti lasciati fuori, e la licenza e la cartella licenze accanto all'eseguibile. Nella 1.97.9 senza i doppioni delle DLL di lib.
#
# Si compila dalla cartella del progetto con: python -m PyInstaller --noconfirm MeTeOra.spec
# Dentro il pacchetto vanno le sole cose che MeTeOra legge: il manuale, le
# novita', la licenza, la collezione dei suoni di GBUtils, che Acusticator cerca
# accanto a GBUtils.py e il codice non nomina mai (prontuario 2.2), le librerie
# native della cartella lib e quelle di accessible_output2. FluidSynth e i banchi
# dei MIDI no: MeTeOra li scarica al primo MIDI accanto ai suoi dati.
# La licenza e la cartella licenze, che fa strumenti/raccogli_licenze.py, vanno
# accanto all'eseguibile, dove chi riceve il pacchetto le trova.

import os
import shutil

import GBUtils
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = [
    ("manuale.html", "."),
    ("CHANGELOG.md", "."),
    (os.path.join(os.path.dirname(GBUtils.__file__), "Acu_Collection.json"), "."),
    ("lib", "lib"),
]
# Le DLL dei lettori di schermo, che accessible_output2 cerca nella sua cartella lib.
datas += collect_data_files("accessible_output2", include_py_files=False)

# Fuori dal pacchetto (1.85.0): le DLL proprietarie di accessible_output2, di
# PC-Talker, ZDSR, Dolphin e System Access, che non danno il permesso di
# ridistribuirle, e quella a 32 bit di NVDA; le varianti di PortAudio che
# sounddevice non carica mai su Windows a 64 bit, con ASIO, a 32 bit, per ARM e
# per macOS.
FUORI = {
    "pctkusr.dll", "pctkusr64.dll", "zdsrapi.dll", "zdsrapi_x64.dll", "dolapi.dll", "saapi32.dll", "nvdacontrollerclient32.dll",
    "libportaudio.dylib", "libportaudio32bit.dll", "libportaudio32bit-asio.dll", "libportaudio64bit-asio.dll", "libportaudioarm64.dll",
    "libportaudioarm64-asio.dll",
}


def _dentro(voce):
    return os.path.basename(voce[0]).lower() not in FUORI


datas = [voce for voce in datas if _dentro(voce)]

# Le uscite della sintesi si aprono per nome (sintesi.py, importlib), e i
# moduli di winrt del riconoscimento dei caratteri si importano dentro le
# funzioni di ocr.py.
hiddenimports = collect_submodules("accessible_output2.outputs") + [
    "winrt.windows.foundation",
    "winrt.windows.foundation.collections",
    "winrt.windows.globalization",
    "winrt.windows.graphics.imaging",
    "winrt.windows.media.ocr",
    "winrt.windows.storage.streams",
]

a = Analysis(
    ["meteora.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # psutil, chardet, cryptography, setuptools e tomli li tirano dentro solo
    # import facoltativi o di prova di numpy, scipy, requests e cffi (1.85.0).
    excludes=["tkinter", "matplotlib", "pandas", "PyQt5", "PyQt6", "PySide2", "PySide6", "IPython", "jedi", "notebook", "pytest",
        "psutil", "chardet", "cryptography", "setuptools", "tomli"],
    noarchive=False,
    optimize=0,
)
a.binaries = [voce for voce in a.binaries if _dentro(voce)]
# Le DLL di lib viaggiano gia' nella loro cartella, con i datas; PyInstaller ne
# raccoglie le dipendenze anche alla radice di _internal, doppie, per circa
# 5,6 MB. sidshim.dll e libgme.dll si caricano con il percorso intero, e
# Windows cerca le loro dipendenze nella loro cartella (1.97.9).
_LIB = os.path.normcase(os.path.abspath("lib"))
a.binaries = [voce for voce in a.binaries
    if not (os.path.dirname(voce[0]) == "" and os.path.normcase(os.path.dirname(os.path.abspath(voce[1]))) == _LIB)]
a.datas = [voce for voce in a.datas if _dentro(voce)]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MeTeOra",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="MeTeOra",
)

# Accanto all'eseguibile, dove chi riceve il pacchetto li trova.
_pacchetto = os.path.join(DISTPATH, "MeTeOra")  # noqa: F821 - lo definisce PyInstaller
shutil.copyfile("LICENSE", os.path.join(_pacchetto, "LICENSE"))
shutil.copytree("licenze", os.path.join(_pacchetto, "licenze"), dirs_exist_ok=True)
