# MeTeOra, la ricetta di PyInstaller: il pacchetto a cartella (prontuario, premessa).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la prova del pacchetto, prima della tappa 11.
#
# Si compila dalla cartella del progetto con: python -m PyInstaller --noconfirm MeTeOra.spec
# Dentro il pacchetto vanno le sole cose che MeTeOra legge: il manuale, le
# novita', la licenza, la collezione dei suoni di GBUtils, che Acusticator cerca
# accanto a GBUtils.py e il codice non nomina mai (prontuario 2.2), le librerie
# native della cartella lib e quelle di accessible_output2. FluidSynth e i banchi
# dei MIDI no: MeTeOra li scarica al primo MIDI accanto ai suoi dati.

import os

import GBUtils
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = [
    ("manuale.html", "."),
    ("CHANGELOG.md", "."),
    ("LICENSE", "."),
    (os.path.join(os.path.dirname(GBUtils.__file__), "Acu_Collection.json"), "."),
    ("lib", "lib"),
]
# Le DLL dei lettori di schermo, che accessible_output2 cerca nella sua cartella lib.
datas += collect_data_files("accessible_output2", include_py_files=False)

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
    excludes=["tkinter", "matplotlib", "pandas", "PyQt5", "PyQt6", "PySide2", "PySide6", "IPython", "jedi", "notebook", "pytest"],
    noarchive=False,
    optimize=0,
)
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
