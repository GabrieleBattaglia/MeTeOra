# MeTeOra, la sintesi dei sottotitoli: gli screen reader e la voce di Windows, con accessible_output2.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 7, per i sottotitoli letti.

"""Le uscite a cui MeTeOra manda i sottotitoli letti (tappa 7).

accessible_output2 parla con gli screen reader e con la voce di Windows:
voce e display braille, dove lo screen reader li ha. Le impostazioni
scelgono un'uscita, oppure l'automatica: il primo screen reader attivo,
nell'ordine di USCITE, e se non ce n'e' nessuno la voce di Windows.
Un'uscita che non si apre, o che sparisce, non ferma niente: dici
restituisce falso, e i sottotitoli restano nella console.
"""

import contextlib
import importlib

AUTOMATICA = "automatica"
# Le uscite, nell'ordine della scelta automatica: chiave salvata nelle
# impostazioni, (modulo di accessible_output2, classe, nome da leggere).
USCITE = {
    "nvda": ("nvda", "NVDA", "NVDA"),
    "jaws": ("jaws", "Jaws", "JAWS"),
    "zdsr": ("zdsr", "ZDSR", "ZDSR"),
    "dolphin": ("dolphin", "Dolphin", "Dolphin"),
    "system_access": ("system_access", "SystemAccess", "System Access"),
    "pc_talker": ("pc_talker", "PCTalker", "PC-Talker"),
    "sapi5": ("sapi5", "SAPI5", "la voce di Windows, SAPI5"),
}
VOCE_DI_SISTEMA = "sapi5"


def _crea(chiave):
    """L'uscita, o None se non si apre: accessible_output2 solleva errori
    suoi e di COM, e una libreria che manca non deve fermare MeTeOra."""
    modulo, classe, _nome = USCITE[chiave]
    try:
        return getattr(importlib.import_module(f"accessible_output2.outputs.{modulo}"), classe)()
    except Exception:  # noqa: BLE001 - qualunque errore vuol dire che quell'uscita non c'e'
        return None


def _attiva(chiave, uscita):
    """Vero se l'uscita si puo' usare adesso: uno screen reader in funzione,
    o la voce di Windows che si e' aperta."""
    if uscita is None:
        return False
    if chiave == VOCE_DI_SISTEMA:
        return True
    with contextlib.suppress(Exception):
        return bool(uscita.is_active())
    return False


def nome(chiave):
    """Il nome da leggere di una scelta delle impostazioni."""
    return "automatica" if chiave == AUTOMATICA else USCITE[chiave][2]


def disponibili():
    """Le chiavi delle uscite che si possono usare adesso, nell'ordine di USCITE."""
    return [chiave for chiave in USCITE if _attiva(chiave, _crea(chiave))]


class Sintesi:
    """Manda i testi all'uscita scelta, aprendola alla prima richiesta e
    tenendola aperta. Da usare sempre dallo stesso filo: la voce di Windows
    passa da COM."""

    def __init__(self):
        self._aperte = {}

    def _uscita(self, chiave):
        if chiave not in self._aperte:
            self._aperte[chiave] = _crea(chiave)
        return self._aperte[chiave]

    def scelta(self, chiave):
        """La chiave dell'uscita che si userebbe adesso per la scelta data, o
        None se non ce n'e': per l'automatica, il primo screen reader attivo
        e poi la voce di Windows."""
        if chiave != AUTOMATICA:
            return chiave if chiave in USCITE and _attiva(chiave, self._uscita(chiave)) else None
        return next((c for c in USCITE if _attiva(c, self._uscita(c))), None)

    def dici(self, testo, chiave=AUTOMATICA):
        """Dice il testo con l'uscita scelta, senza interrompere quello che
        sta dicendo. Falso se nessuna uscita risponde."""
        effettiva = self.scelta(chiave)
        if effettiva is None:
            return False
        try:
            self._uscita(effettiva).output(testo, interrupt=False)
        except Exception:  # noqa: BLE001 - uno screen reader chiuso nel frattempo
            self._aperte.pop(effettiva, None)
            return False
        return True
