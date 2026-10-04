# MeTeOra, le associazioni dei formati: Apri con MeTeOra e le app predefinite di Windows.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.91.0, tappa 12 d del piano.

"""Le associazioni dei formati (1.91.0).

Solo per l'utente di Windows, in HKEY_CURRENT_USER: niente diritti di
amministratore. registra() fa comparire MeTeOra in Apri con per tutti i
formati che suona, e fra le app predefinite delle impostazioni di Windows;
renderlo il programma predefinito, pero', Windows non lo lascia fare a un
programma da solo: lo sceglie chi usa il PC, nella pagina che apri_le_app_predefinite()
apre. togli() cancella soltanto le chiavi e i valori che registra() ha scritto.
Il modulo del registro e' un parametro, cosi' le prove non toccano quello vero.
"""

import contextlib
import os
import winreg

import formati

NOME = "MeTeOra"
PROGID_AUDIO = "MeTeOra.Audio"
PROGID_VIDEO = "MeTeOra.Video"
_CLASSI = r"Software\Classes"
_APPLICAZIONE = rf"{_CLASSI}\Applications\MeTeOra.exe"
_CAPACITA = r"Software\MeTeOra\Capabilities"
_REGISTRATE = r"Software\RegisteredApplications"
_SHCNE_ASSOCCHANGED = 0x08000000


def estensioni():
    """Le estensioni di MeTeOra, con il loro ProgID: video o audio."""
    return {estensione: (PROGID_VIDEO if estensione in formati.VIDEO else PROGID_AUDIO) for estensione in sorted(formati.TUTTI)}


def _scrivi(reg, percorso, valori):
    with reg.CreateKeyEx(reg.HKEY_CURRENT_USER, percorso, 0, reg.KEY_WRITE) as chiave:
        for nome, valore in valori.items():
            reg.SetValueEx(chiave, nome, 0, reg.REG_SZ, valore)


def registra(eseguibile, reg=winreg):
    """Scrive le chiavi: l'applicazione con i tipi che apre, i due ProgID,
    MeTeOra fra i programmi di Apri con di ogni estensione, e le capacita'
    per le app predefinite. Torna quante estensioni ha registrato."""
    comando = f'"{eseguibile}" "%1"'
    icona = f'"{eseguibile}",0'
    tipi = estensioni()
    _scrivi(reg, _APPLICAZIONE, {"FriendlyAppName": NOME})
    _scrivi(reg, rf"{_APPLICAZIONE}\shell\open\command", {"": comando})
    _scrivi(reg, rf"{_APPLICAZIONE}\SupportedTypes", dict.fromkeys(tipi, ""))
    for progid, descrizione in ((PROGID_AUDIO, "Audio per MeTeOra"), (PROGID_VIDEO, "Video per MeTeOra")):
        _scrivi(reg, rf"{_CLASSI}\{progid}", {"": descrizione})
        _scrivi(reg, rf"{_CLASSI}\{progid}\DefaultIcon", {"": icona})
        _scrivi(reg, rf"{_CLASSI}\{progid}\shell\open\command", {"": comando})
    for estensione, progid in tipi.items():
        _scrivi(reg, rf"{_CLASSI}\{estensione}\OpenWithProgids", {progid: ""})
    _scrivi(reg, _CAPACITA, {"ApplicationName": NOME, "ApplicationDescription": "Lettore audio e video accessibile"})
    _scrivi(reg, rf"{_CAPACITA}\FileAssociations", tipi)
    _scrivi(reg, _REGISTRATE, {NOME: _CAPACITA})
    _avvisa_windows()
    return len(tipi)


def _cancella_albero(reg, percorso):
    """Cancella una chiave con tutte le sue sottochiavi, se c'e'."""
    try:
        chiave = reg.OpenKey(reg.HKEY_CURRENT_USER, percorso, 0, reg.KEY_READ | reg.KEY_WRITE)
    except OSError:
        return
    with chiave:
        while True:
            try:
                figlia = reg.EnumKey(chiave, 0)
            except OSError:
                break
            _cancella_albero(reg, rf"{percorso}\{figlia}")
    with contextlib.suppress(OSError):
        reg.DeleteKey(reg.HKEY_CURRENT_USER, percorso)


def _cancella_valore(reg, percorso, nome):
    with contextlib.suppress(OSError), reg.OpenKey(reg.HKEY_CURRENT_USER, percorso, 0, reg.KEY_WRITE) as chiave:
        reg.DeleteValue(chiave, nome)


def togli(reg=winreg):
    """Cancella cio' che registra() ha scritto, e solo quello: le chiavi delle
    estensioni restano, perche' sono anche di altri programmi."""
    _cancella_albero(reg, _APPLICAZIONE)
    _cancella_albero(reg, rf"{_CLASSI}\{PROGID_AUDIO}")
    _cancella_albero(reg, rf"{_CLASSI}\{PROGID_VIDEO}")
    for estensione, progid in estensioni().items():
        _cancella_valore(reg, rf"{_CLASSI}\{estensione}\OpenWithProgids", progid)
    _cancella_albero(reg, r"Software\MeTeOra")
    _cancella_valore(reg, _REGISTRATE, NOME)
    _avvisa_windows()


def _avvisa_windows():
    """Esplora risorse rilegge le associazioni."""
    with contextlib.suppress(Exception):
        import ctypes

        ctypes.windll.shell32.SHChangeNotify(_SHCNE_ASSOCCHANGED, 0, None, None)


def apri_le_app_predefinite():
    """La pagina delle app predefinite di Windows, su MeTeOra se Windows la sa
    aprire, altrimenti l'elenco intero."""
    try:
        os.startfile(f"ms-settings:defaultapps?registeredAppUser={NOME}")  # noqa: S606 - una pagina delle impostazioni di Windows
    except OSError:
        os.startfile("ms-settings:defaultapps")  # noqa: S606, S607 - una pagina delle impostazioni di Windows
