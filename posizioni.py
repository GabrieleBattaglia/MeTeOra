# MeTeOra, le posizioni dei file lunghi: audiolibri e film riprendono dal punto in cui li si e' lasciati.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.92.0, tappa 12 e del piano. Nella 1.103.0 quante sono, per le statistiche. Nella 1.104.0 i punti dei file spariti si tolgono, e seguono Rinomina file.

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


def _norm(percorso):
    """Il percorso come si confronta: assoluto e, su Windows, con le
    maiuscole e le barre di sistema (1.104.0)."""
    return os.path.normcase(os.path.abspath(percorso))


def _quando(punto):
    """Il momento di un punto, per scegliere il piu' recente: un punto
    scritto a mano senza 'quando' vale come il piu' vecchio."""
    return str(punto.get("quando") or "")


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

    def quante(self):
        """Quanti file hanno un punto da riprendere, per le statistiche."""
        return len(self._punti)

    def dimentica(self, percorso):
        if self._punti.pop(percorso, None) is not None:
            self.modificate = True

    def percorsi(self):
        """I file che hanno un punto da riprendere, cosi' come sono scritti,
        per la pulizia all'avvio (1.104.0)."""
        return list(self._punti)

    def togli_i_mancanti(self, mancanti):
        """Toglie i punti dei file mancanti, un insieme di percorsi gia'
        normalizzati con normcase e abspath, e restituisce quanti ne ha
        tolti (1.104.0). Non salva: salva chi chiama."""
        via = [p for p in self._punti if _norm(p) in mancanti] if mancanti else []
        for p in via:
            del self._punti[p]
        if via:
            self.modificate = True
        return len(via)

    def rinomina(self, vecchio, nuovo):
        """Rinomina file: il punto da riprendere passa al nome nuovo, anche
        se era scritto in un'altra forma; fra piu' grafie del file resta il
        punto piu' recente. Se il nome cambia non solo nelle maiuscole, un
        punto gia' scritto sul nome nuovo e' di un file che non c'e' piu',
        perche' Rinomina file rifiuta un nome che esiste: si toglie sempre,
        anche se il file rinominato non ha un punto. Vero se qualcosa e'
        cambiato (Gabriele, 19 ottobre 2026, 1.104.0)."""
        stesso, arrivo = _norm(vecchio), _norm(nuovo)
        suoi = [p for p in self._punti if _norm(p) == stesso]
        superati = [p for p in self._punti if _norm(p) == arrivo] if arrivo != stesso else []
        if not superati and suoi in ([], [nuovo]):
            return False
        for p in superati:
            del self._punti[p]
        if suoi:
            # max tiene il primo dei pari, nell'ordine in cui le grafie sono scritte.
            self._punti[nuovo] = max((self._punti.pop(p) for p in suoi), key=_quando)
        self.modificate = True
        return True

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
