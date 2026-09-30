# MeTeOra, le impostazioni: i valori che il programma ricorda fra un avvio e l'altro.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1.

"""Le impostazioni, in un file JSON accanto al programma.

La finestra delle impostazioni arriva con la tappa 3: per ora i valori si
cambiano con i tasti (volume, passo di salto) e si salvano all'uscita.
Un valore mancante o sbagliato nel file prende il predefinito.
"""

import json
import os

PREDEFINITE = {
    "volume": 80,
    "passo_volume": 5,
    "passo_indietro": 10,
    "passo_avanti": 10,
    "volume_effetti": 0.5,
}


class Impostazioni(dict):
    def __init__(self, percorso):
        super().__init__(PREDEFINITE)
        self.percorso = percorso

    def carica(self):
        if not os.path.isfile(self.percorso):
            return
        try:
            with open(self.percorso, encoding="utf-8") as f:
                dati = json.load(f)
        except (OSError, ValueError):
            return
        for chiave, predefinito in PREDEFINITE.items():
            valore = dati.get(chiave)
            if isinstance(valore, bool):
                continue
            if isinstance(predefinito, float) and isinstance(valore, int | float):
                self[chiave] = float(valore)
            elif isinstance(valore, type(predefinito)):
                self[chiave] = valore

    def salva(self):
        provvisorio = self.percorso + ".tmp"
        with open(provvisorio, "w", encoding="utf-8") as f:
            json.dump(dict(self), f, ensure_ascii=False, indent=1)
        os.replace(provvisorio, self.percorso)
