# MeTeOra, le impostazioni: i valori che il programma ricorda fra un avvio e l'altro.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.34.0 le righe della console. Nella 1.51.0 caratteri, colori e scheda audio, e i limiti controllati alla lettura del file. Nella 1.51.2 un file con un JSON che non e' un dizionario non ferma l'avvio.

"""Le impostazioni, in un file JSON accanto al programma.

Dalla 1.51.0 si cambiano dalla finestra delle impostazioni, la voce
Impostazioni della plancia, che le applica e le salva subito; alcune anche
con i tasti (il volume, il suo passo, i salti di Q ed E, l'inseguimento).
Il testo scritto nei campi lo legge valori.py, che tiene anche i limiti.
Un valore mancante o sbagliato nel file prende il predefinito: sbagliato vuol
dire di un altro tipo, o fuori dai limiti che controlla CONTROLLI. Le chiavi
che il programma non conosce si perdono al primo salvataggio.
"""

import copy
import json
import math
import os

from valori import (
    AREE,
    CARATTERI_MASSIMI,
    CARATTERI_MINIMI,
    COMPONENTI,
    PASSO_VOLUME_MASSIMO,
    PASSO_VOLUME_MINIMO,
    PERCENTUALE_MASSIMA,
    RIGHE_MINIME,
    SECONDI_MINIMI,
    VOLUME_MASSIMO,
)

PREDEFINITE = {
    "volume": 80,
    "passo_volume": 5,
    "passo_indietro": 10.0,
    "passo_avanti": 10.0,
    "volume_effetti": 0.5,
    # Maiuscolo+F8: la selezione della plancia segue il brano che suona.
    "insegui": False,
    # Cosa suonava all'uscita, per riprendere da li' in pausa.
    "ripresa": {},
    # Quante righe tiene la console.
    "righe_della_console": 2000,
    # La dimensione dei caratteri in punti, area per area (p plancia, c
    # console, t cruscotto); un'area assente ha il carattere di Windows.
    "caratteri": {},
    # I colori dei caratteri e dello sfondo, area per area, come [r, g, b] in
    # percentuali intere da 0 a 100; un'area assente ha i colori di Windows.
    "colori_testo": {},
    "colori_sfondo": {},
    # La scheda audio di musica ed effetti: {"dispositivo": nome, "interfaccia":
    # nome intero di PortAudio, per esempio "Windows WASAPI"}. Si salvano i
    # nomi e non l'indice, che cambia fra un avvio e l'altro; il dizionario
    # vuoto e' la scelta automatica.
    "scheda_audio": {},
}


def _intero_fra(minimo, massimo=None):
    """Il controllo di un intero, non booleano, da minimo a massimo; massimo
    None vuol dire senza limite in alto."""
    return lambda valore: isinstance(valore, int) and not isinstance(valore, bool) and minimo <= valore and (massimo is None or valore <= massimo)


def _numero_fra(minimo, massimo=None):
    """Il controllo di un numero finito, intero o con i decimali, da minimo a
    massimo; massimo None vuol dire senza limite in alto."""
    return lambda valore: (isinstance(valore, int | float) and not isinstance(valore, bool) and math.isfinite(valore)
        and minimo <= valore and (massimo is None or valore <= massimo))


def _caratteri_validi(valore):
    """Un dizionario dalle lettere delle aree ai punti, da 6 a 72."""
    punti_validi = _intero_fra(CARATTERI_MINIMI, CARATTERI_MASSIMI)
    return isinstance(valore, dict) and all(area in AREE and punti_validi(punti) for area, punti in valore.items())


def _colori_validi(valore):
    """Un dizionario dalle lettere delle aree a liste di tre percentuali intere."""
    percentuale_valida = _intero_fra(0, PERCENTUALE_MASSIMA)
    return isinstance(valore, dict) and all(
        area in AREE and isinstance(rgb, list) and len(rgb) == len(COMPONENTI) and all(map(percentuale_valida, rgb))
        for area, rgb in valore.items())


def _scheda_valida(valore):
    """Il dizionario vuoto, oppure i due nomi, non vuoti, del dispositivo e
    dell'interfaccia."""
    if not isinstance(valore, dict):
        return False
    return not valore or (set(valore) == {"dispositivo", "interfaccia"} and all(isinstance(nome, str) and nome for nome in valore.values()))


# Per ogni chiave, la funzione che dice se un valore letto dal file, gia' del
# tipo giusto, e' accettabile; un valore che non passa prende il predefinito.
# I limiti sono quelli di valori.py, gli stessi dei campi della finestra.
CONTROLLI = {
    "volume": _intero_fra(0, VOLUME_MASSIMO),
    "passo_volume": _intero_fra(PASSO_VOLUME_MINIMO, PASSO_VOLUME_MASSIMO),
    "passo_indietro": _numero_fra(SECONDI_MINIMI),
    "passo_avanti": _numero_fra(SECONDI_MINIMI),
    "volume_effetti": _numero_fra(0, 1),
    "righe_della_console": _intero_fra(RIGHE_MINIME),
    "caratteri": _caratteri_validi,
    "colori_testo": _colori_validi,
    "colori_sfondo": _colori_validi,
    "scheda_audio": _scheda_valida,
}


class Impostazioni(dict):
    def __init__(self, percorso):
        # Una copia profonda: i dizionari dei predefiniti non devono cambiare
        # quando la finestra cambia quelli di un'istanza.
        super().__init__(copy.deepcopy(PREDEFINITE))
        self.percorso = percorso

    def carica(self):
        if not os.path.isfile(self.percorso):
            return
        try:
            with open(self.percorso, encoding="utf-8") as f:
                dati = json.load(f)
        except (OSError, ValueError, RecursionError):
            return
        # Un file che non contiene un dizionario, per esempio una lista, vale
        # come un file illeggibile: tutto resta predefinito.
        if not isinstance(dati, dict):
            return
        for chiave, predefinito in PREDEFINITE.items():
            if chiave not in dati:
                continue
            valore = dati[chiave]
            if isinstance(valore, bool) != isinstance(predefinito, bool):
                continue
            if isinstance(predefinito, float) and isinstance(valore, int | float):
                try:
                    valore = float(valore)
                except OverflowError:
                    # Un intero di centinaia di cifre non diventa float.
                    continue
            if not isinstance(valore, type(predefinito)):
                continue
            if chiave in CONTROLLI and not CONTROLLI[chiave](valore):
                continue
            self[chiave] = valore

    def salva(self):
        provvisorio = self.percorso + ".tmp"
        with open(provvisorio, "w", encoding="utf-8") as f:
            json.dump(dict(self), f, ensure_ascii=False, indent=1)
        os.replace(provvisorio, self.percorso)
