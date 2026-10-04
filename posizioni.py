# MeTeOra, le posizioni dei file lunghi: audiolibri e film riprendono dal punto in cui li si e' lasciati.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.92.0, tappa 12 e del piano.

"""Le posizioni dei file lunghi (1.92.0).

Per ogni file piu' lungo del limite delle impostazioni, 10 minuti di
partenza, MeTeOra ricorda l'ultimo punto ascoltato, e la volta dopo il file
riparte da li'. Un punto troppo vicino all'inizio o alla fine, entro MARGINE
secondi, non si ricorda: il file e' appena cominciato, o e' finito. Si
tengono al piu' MASSIME posizioni, le piu' recenti. Il file e' "MeTeOra -
Posizioni.json", accanto ai dati, scritto come gli altri: prima un file
accanto, poi al posto del vero. Un file che non si legge vale come vuoto:
le posizioni sono comode, non preziose, e le copie dei dati le tengono.
"""

import contextlib
import datetime
import json
import os

MARGINE = 30.0
MASSIME = 1000


class Posizioni:
    def __init__(self, percorso):
        self.percorso = percorso
        self._punti = {}
        self.modificate = False
        with contextlib.suppress(OSError, ValueError):
            with open(percorso, encoding="utf-8") as f:
                dati = json.load(f)
            if isinstance(dati, dict):
                self._punti = {p: v for p, v in dati.items() if isinstance(v, dict) and isinstance(v.get("secondi"), int | float)}

    def ricorda(self, percorso, secondi, durata):
        """Il punto di adesso di un file lungo; vicino all'inizio o alla fine
        lo dimentica."""
        if secondi is None or durata is None:
            return
        if secondi < MARGINE or secondi > durata - MARGINE:
            self.dimentica(percorso)
            return
        vecchio = self._punti.get(percorso)
        if vecchio is not None and abs(vecchio["secondi"] - secondi) < 1:
            return
        self._punti[percorso] = {"secondi": round(float(secondi), 1), "quando": datetime.datetime.now().isoformat(timespec="seconds")}
        self.modificate = True

    def dove(self, percorso):
        """I secondi a cui riprendere il file, o None."""
        punto = self._punti.get(percorso)
        return punto["secondi"] if punto else None

    def dimentica(self, percorso):
        if self._punti.pop(percorso, None) is not None:
            self.modificate = True

    def salva(self):
        """Scrive il file, tenendo solo le MASSIME posizioni piu' recenti."""
        if len(self._punti) > MASSIME:
            recenti = sorted(self._punti.items(), key=lambda voce: voce[1].get("quando", ""), reverse=True)[:MASSIME]
            self._punti = dict(recenti)
        provvisorio = self.percorso + ".tmp"
        with open(provvisorio, "w", encoding="utf-8") as f:
            json.dump(self._punti, f, ensure_ascii=False, indent=1)
        os.replace(provvisorio, self.percorso)
        self.modificate = False
