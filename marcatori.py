# MeTeOra, i marker: punti con un nome dentro un brano, salvati in un file JSON.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.39.0, tappa 3, issue 12 e 14.

"""I marker dei brani.

Un marker sta con il file, non con il percorso: due copie identiche dello
stesso file, in posti diversi, hanno gli stessi marker (decisione di Gabriele
del 1 ottobre 2026). Il file si riconosce dal nome e dalla durata al
millesimo, che per due copie identiche e' la stessa; per i SID conta anche il
sottobrano. Per i file di cui la durata non si conosce vale il percorso.
I nomi automatici sono M1, M2, M3 e cosi' via, per file. Due marker non stanno
mai piu' vicini della tolleranza: in quel caso sono lo stesso marker.
"""

import json
import os

# Entro questa distanza la posizione e' quella di un marker: il motore, in
# pausa, torna sul tempo chiesto entro pochi centomillesimi di secondo.
TOLLERANZA = 0.005


def chiave(percorso, durata, sottobrano=None):
    """La chiave dei marker di un file, o di un suo sottobrano."""
    base = f"{os.path.basename(percorso).casefold()}|{durata:.3f}" if durata else f"percorso|{os.path.normcase(os.path.abspath(percorso))}"
    return f"{base}|{sottobrano}" if sottobrano else base


class Marcatori:
    def __init__(self, percorso):
        self.percorso = percorso
        # chiave -> {"file", "durata", "sottobrano", "percorsi", "marker": [{"tempo", "nome"}]}
        self.voci = {}
        self._nomi = set()
        # Vero se ci sono cambiamenti non ancora scritti nel file.
        self.modificato = False
        # Perche' il file non si e' letto, se non si e' letto.
        self.errore = None

    def carica(self):
        """Legge il file. Un file che non si legge non si sovrascrive: i
        marker nuovi vanno accanto, con .nuovo, e alla volta dopo, se il file
        e' ancora illeggibile, si riparte da quello."""
        try:
            self._leggi(self.percorso)
        except (OSError, ValueError, TypeError, AttributeError, KeyError) as e:
            self.errore = str(e) or type(e).__name__
            self.voci, self._nomi = {}, set()
            self.percorso += ".nuovo"
            try:
                self._leggi(self.percorso)
            except (OSError, ValueError, TypeError, AttributeError, KeyError):
                self.voci, self._nomi = {}, set()

    def _leggi(self, percorso):
        if not os.path.isfile(percorso):
            return
        with open(percorso, encoding="utf-8") as f:
            dati = json.load(f)
        for k, voce in dict(dati.get("marcatori") or {}).items():
            elenco = sorted(({"tempo": float(m["tempo"]), "nome": str(m["nome"])} for m in voce.get("marker", [])), key=lambda m: m["tempo"])
            if not elenco:
                continue
            voce["marker"] = elenco
            voce.setdefault("file", "")
            voce.setdefault("percorsi", [])
            self.voci[str(k)] = voce
            self._nomi.add(str(voce["file"]).casefold())

    def salva(self):
        provvisorio = self.percorso + ".tmp"
        with open(provvisorio, "w", encoding="utf-8") as f:
            json.dump({"versione": 1, "marcatori": self.voci}, f, ensure_ascii=False, indent=1)
        os.replace(provvisorio, self.percorso)
        self.modificato = False

    def forse(self, percorso):
        """Vero se qualche file con questo nome ha dei marker: un controllo
        veloce, prima di calcolare la chiave."""
        return os.path.basename(percorso).casefold() in self._nomi

    def elenco(self, k):
        """I marker della chiave, in ordine di tempo."""
        voce = self.voci.get(k)
        return list(voce["marker"]) if voce else []

    def trova(self, k, tempo):
        """Il marker che sta sul tempo, entro la tolleranza, o None."""
        return next((m for m in self.elenco(k) if abs(m["tempo"] - tempo) <= TOLLERANZA), None)

    def aggiungi(self, k, tempo, percorso, durata=None, sottobrano=None):
        """Un marker nuovo sul tempo, con il primo nome automatico libero dopo
        il piu' alto, e lo restituisce. Il tempo resta quello vero, senza
        arrotondarlo: arrotondato potrebbe finire dentro la tolleranza di
        un marker vicino."""
        voce = self.voci.setdefault(k, {"file": os.path.basename(percorso), "durata": durata, "sottobrano": sottobrano, "percorsi": [], "marker": []})
        if percorso not in voce["percorsi"]:
            voce["percorsi"].append(percorso)
        numeri = [int(m["nome"][1:]) for m in voce["marker"] if m["nome"][:1] == "M" and m["nome"][1:].isdigit()]
        marker = {"tempo": float(tempo), "nome": f"M{max(numeri, default=0) + 1}"}
        voce["marker"].append(marker)
        voce["marker"].sort(key=lambda m: m["tempo"])
        self._nomi.add(voce["file"].casefold())
        self.modificato = True
        return marker

    def rinomina(self, k, marker, nome):
        for m in self.voci.get(k, {}).get("marker", []):
            if m is marker or (m["tempo"] == marker["tempo"] and m["nome"] == marker["nome"]):
                m["nome"] = nome
                self.modificato = True
                return True
        return False

    def _tieni(self, k, condizione):
        """Tiene i marker per cui condizione e' vera e torna quanti ne ha tolti."""
        voce = self.voci.get(k)
        if not voce:
            return 0
        prima = len(voce["marker"])
        voce["marker"] = [m for m in voce["marker"] if condizione(m)]
        if not voce["marker"]:
            del self.voci[k]
        tolti = prima - len(voce["marker"])
        if tolti:
            self.modificato = True
        return tolti

    def togli(self, k, marker):
        return self._tieni(k, lambda m: not (m["tempo"] == marker["tempo"] and m["nome"] == marker["nome"]))

    def togli_prima(self, k, tempo):
        """Toglie i marker prima del tempo; quello che sta sul tempo resta
        (Gabriele, collaudo della 1.39.1)."""
        return self._tieni(k, lambda m: m["tempo"] >= tempo - TOLLERANZA)

    def togli_dopo(self, k, tempo):
        """Toglie i marker dopo il tempo; quello che sta sul tempo resta."""
        return self._tieni(k, lambda m: m["tempo"] <= tempo + TOLLERANZA)

    def togli_tutti(self, k):
        return self._tieni(k, lambda _m: False)

    def precedente(self, k, tempo, margine=TOLLERANZA):
        """L'ultimo marker prima del tempo meno il margine, o None. Mentre il
        brano suona il margine e' piu' largo: appena saltati su un marker si
        e' gia' un po' oltre, e il precedente e' quello prima."""
        prima = [m for m in self.elenco(k) if m["tempo"] < tempo - margine]
        return prima[-1] if prima else None

    def successivo(self, k, tempo):
        """Il primo marker dopo il tempo, o None."""
        return next((m for m in self.elenco(k) if m["tempo"] > tempo + TOLLERANZA), None)
