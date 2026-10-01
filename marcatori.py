# MeTeOra, i marker: punti con un nome dentro un brano, salvati in un file JSON.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.39.0, tappa 3, issue 12 e 14. Nella 1.51.0 l'elenco di tutti i marker, Cancella tutto, l'esportazione e l'importazione.

"""I marker dei brani.

Un marker sta con il file, non con il percorso: due copie identiche dello
stesso file, in posti diversi, hanno gli stessi marker (decisione di Gabriele
del 1 ottobre 2026). Il file si riconosce dal nome e dalla durata al
millesimo, che per due copie identiche e' la stessa; per i SID conta anche il
sottobrano. Per i file di cui la durata non si conosce vale il percorso.
I nomi automatici sono M1, M2, M3 e cosi' via, per file. Due marker non stanno
mai piu' vicini della tolleranza: in quel caso sono lo stesso marker.

Dalla 1.51.0 la finestra dei marcatori li elenca tutti insieme, raggruppati
per provenienza (tutti), e li cancella tutti (cancella_tutto). I marker
scelti si esportano in un file JSON con il nome, la durata e il sottobrano
dei file ma senza percorsi; chi lo importa, anche su un altro computer, li
ritrova sulle sue copie degli stessi file, perche' la chiave e' fatta solo
di quelle tre cose. I marker dei file senza durata non si esportano: la
loro chiave e' il percorso, che altrove non vale.
"""

import json
import math
import os

# Entro questa distanza la posizione e' quella di un marker: il motore, in
# pausa, torna sul tempo chiesto entro pochi centomillesimi di secondo.
TOLLERANZA = 0.005
# Il file di esportazione si riconosce da questi due valori, in testa.
FORMATO_DELL_ESPORTAZIONE = "MeTeOra - Marcatori"
VERSIONE_DELL_ESPORTAZIONE = 1
# Dieci miliardi di secondi, oltre trecento anni: una durata o un tempo piu'
# lunghi non sono di nessun file, ma di un file di esportazione rovinato o
# ritoccato male. Un tempo come 1e306 passerebbe come numero finito, ma poi la
# finestra dei marcatori e la plancia non riuscirebbero piu' a scriverlo. Il
# tetto e' cosi' alto perche' i file veri dichiarano durate enormi: un WAV
# non chiuso, a 8000 Hz e 8 bit, ne dichiara 149 ore, e T ci mette i marker.
# Vale all'andata e al ritorno, perche' MeTeOra non rifiuti i file che scrive.
TETTO_DEI_SECONDI = 10_000_000_000


def chiave(percorso, durata, sottobrano=None):
    """La chiave dei marker di un file, o di un suo sottobrano."""
    base = f"{os.path.basename(percorso).casefold()}|{durata:.3f}" if durata else f"percorso|{os.path.normcase(os.path.abspath(percorso))}"
    return f"{base}|{sottobrano}" if sottobrano else base


def _numero(valore):
    """Il valore come float se e' un numero finito, altrimenti None: un
    booleano, un testo o un infinito non sono numeri."""
    if isinstance(valore, bool) or not isinstance(valore, (int, float)):
        return None
    try:
        numero = float(valore)
    except OverflowError:
        return None
    return numero if math.isfinite(numero) else None


def _durata_valida(durata):
    """La durata come float se puo' fare da chiave, cioe' se e' un numero
    maggiore di zero, altrimenti None."""
    numero = _numero(durata)
    return numero if numero is not None and numero > 0 else None


def _nome_del_file(k, voce):
    """Il nome del file di una voce. Una voce scritta a mano senza nome lo
    prende dal primo percorso o, senza percorsi, dalla chiave."""
    if voce.get("file"):
        return str(voce["file"])
    percorsi = voce.get("percorsi") or []
    if percorsi:
        return os.path.basename(str(percorsi[0]))
    parti = k.split("|")
    return os.path.basename(parti[1]) if parti[0] == "percorso" and len(parti) > 1 else parti[0]


def _ordine(k, voce):
    """Dove sta una voce nell'elenco di tutti i marker: prima quelle con un
    percorso conosciuto, per cartella del primo percorso (confrontata pezzo
    per pezzo, cosi' le sottocartelle vengono subito dopo la loro), poi per
    nome del file e per sottobrano. La chiave, in fondo, tiene separati i
    marker di due voci che resterebbero pari, come lo stesso file con due
    durate diverse."""
    percorsi = voce.get("percorsi") or []
    cartella = tuple(os.path.normcase(os.path.dirname(str(percorsi[0]))).casefold().split(os.sep)) if percorsi else ()
    sottobrano = voce.get("sottobrano")
    return (not percorsi, cartella, _nome_del_file(k, voce).casefold(), sottobrano if isinstance(sottobrano, int) else 0, k)


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

    # La finestra dei marcatori.

    def tutti(self):
        """Tutti i marker, come (chiave, voce, marker), raggruppati per
        provenienza: per cartella del primo percorso conosciuto (le voci
        senza percorso in fondo), poi per nome del file, sottobrano e tempo.
        Voci e marker sono quelli dell'archivio, non copie, cosi' rinomina e
        togli li ritrovano."""
        return [(k, voce, m) for k, voce in sorted(self.voci.items(), key=lambda kv: _ordine(*kv)) for m in sorted(voce["marker"], key=lambda m: m["tempo"])]

    def cancella_tutto(self):
        """Toglie tutti i marker di tutti i file e restituisce quanti erano."""
        tolti = sum(len(voce["marker"]) for voce in self.voci.values())
        self.voci.clear()
        # Qui l'insieme dei nomi si puo' svuotare: non resta nessun marker.
        self._nomi.clear()
        if tolti:
            self.modificato = True
        return tolti

    # L'esportazione e l'importazione.

    def esporta(self, scelti):
        """I marker scelti, una lista di (chiave, marker), pronti per il file
        di esportazione: restituisce (dati, saltati). I dati hanno una voce
        per chiave, con nome del file, durata e sottobrano ma senza
        percorsi, e i marker in ordine di tempo. saltati dice quanti marker
        scelti non si esportano perche' il loro file non ha una durata (la
        loro chiave e' il percorso), o perche' durata o tempo passano il
        tetto che leggi_esportazione rifiuterebbe. Un marker scelto due volte
        conta una volta; le chiavi che l'archivio non ha si ignorano."""
        uscite, visti, saltati = {}, set(), 0
        for k, marker in scelti:
            voce = self.voci.get(k)
            tempo, nome = float(marker["tempo"]), str(marker["nome"])
            if voce is None or (k, tempo, nome) in visti:
                continue
            visti.add((k, tempo, nome))
            durata = _durata_valida(voce.get("durata"))
            if durata is None or durata > TETTO_DEI_SECONDI or tempo > TETTO_DEI_SECONDI:
                saltati += 1
                continue
            uscita = uscite.setdefault(k, {"file": _nome_del_file(k, voce), "durata": durata, "sottobrano": voce.get("sottobrano") or None, "marker": []})
            uscita["marker"].append({"tempo": tempo, "nome": nome})
        for uscita in uscite.values():
            uscita["marker"].sort(key=lambda m: m["tempo"])
        dati = {"formato": FORMATO_DELL_ESPORTAZIONE, "versione": VERSIONE_DELL_ESPORTAZIONE, "marcatori": list(uscite.values())}
        return dati, saltati

    @staticmethod
    def scrivi_esportazione(dati, percorso):
        """Scrive i dati di esporta nel file, come salva: prima in .tmp, poi
        al suo posto. Un OSError lo intercetta chi chiama."""
        percorso = os.fspath(percorso)
        provvisorio = percorso + ".tmp"
        with open(provvisorio, "w", encoding="utf-8") as f:
            json.dump(dati, f, ensure_ascii=False, indent=1)
        os.replace(provvisorio, percorso)

    @staticmethod
    def leggi_esportazione(percorso):
        """Legge un file di esportazione e restituisce le sue voci, ognuna
        {"file", "durata", "sottobrano", "marker": [{"tempo", "nome"}]}, con
        il nome del file senza cartella e i nomi dei marker su una riga.
        Una durata che manca resta None: la voce la salta importa. Se il
        file non si legge, o non e' un'esportazione dei marcatori di
        MeTeOra, o e' rovinata, per esempio con una durata o un tempo oltre
        il tetto dei trecento anni, solleva ValueError con una frase per l'utente;
        nient'altro. Un marker oltre la durata della sua voce si accetta:
        la durata viene dall'intestazione del file, e un file unito o con
        l'intestazione sbagliata suona oltre, e T ci mette i marker."""
        percorso = os.fspath(percorso)
        nome = os.path.basename(percorso)
        try:
            # utf-8-sig: un file ritoccato a mano puo' avere il BOM in testa.
            with open(percorso, encoding="utf-8-sig") as f:
                dati = json.load(f)
        except OSError as e:
            raise ValueError(f"Non riesco a leggere {nome}: {e.strerror or e}.") from e
        except (ValueError, RecursionError) as e:
            # JSON rotto, o un testo che non e' UTF-8.
            raise ValueError(f"{nome} non è un'esportazione dei marcatori di MeTeOra: non è un file JSON.") from e
        if not isinstance(dati, dict) or dati.get("formato") != FORMATO_DELL_ESPORTAZIONE:
            raise ValueError(f"{nome} non è un'esportazione dei marcatori di MeTeOra.")
        versione = dati.get("versione")
        if isinstance(versione, bool) or versione != VERSIONE_DELL_ESPORTAZIONE:
            raise ValueError(f"{nome} è un'esportazione dei marcatori in un formato che questa versione di MeTeOra non sa leggere.")

        def rotta(perche):
            return ValueError(f"{nome} è un'esportazione dei marcatori di MeTeOra, ma è rovinata: {perche}.")

        elenco = dati.get("marcatori")
        if not isinstance(elenco, list):
            raise rotta("manca l'elenco dei marcatori")
        voci = []
        for i, voce in enumerate(elenco, 1):
            if not isinstance(voce, dict):
                raise rotta(f"la voce {i} non è una voce")
            file = voce.get("file")
            file = os.path.basename(file).strip() if isinstance(file, str) else ""
            if not file:
                raise rotta(f"la voce {i} non ha il nome del file")
            durata = voce.get("durata")
            if durata is not None and _numero(durata) is None:
                raise rotta(f"la voce {i}, {file}, non ha una durata che sia un numero")
            if durata is not None and _numero(durata) > TETTO_DEI_SECONDI:
                raise rotta(f"la voce {i}, {file}, ha una durata impossibile, di oltre trecento anni")
            sottobrano = voce.get("sottobrano")
            if sottobrano is not None and (isinstance(sottobrano, bool) or not isinstance(sottobrano, int) or sottobrano < 0):
                raise rotta(f"la voce {i}, {file}, ha un sottobrano che non è un numero")
            marker = voce.get("marker")
            if not isinstance(marker, list):
                raise rotta(f"la voce {i}, {file}, non ha l'elenco dei marker")
            letti = []
            for j, m in enumerate(marker, 1):
                tempo = _numero(m.get("tempo")) if isinstance(m, dict) else None
                if tempo is None or tempo < 0:
                    raise rotta(f"il marker {j} della voce {i}, {file}, non ha un tempo valido")
                if tempo > TETTO_DEI_SECONDI:
                    raise rotta(f"il marker {j} della voce {i}, {file}, ha un tempo impossibile, di oltre trecento anni")
                nome_del_marker = " ".join(m.get("nome").split()) if isinstance(m.get("nome"), str) else ""
                if not nome_del_marker:
                    raise rotta(f"il marker {j} della voce {i}, {file}, non ha un nome")
                letti.append({"tempo": tempo, "nome": nome_del_marker})
            letti.sort(key=lambda m: m["tempo"])
            voci.append({"file": file, "durata": None if durata is None else float(durata), "sottobrano": sottobrano or None, "marker": letti})
        return voci

    def importa(self, voci):
        """Aggiunge i marker delle voci lette con leggi_esportazione (vanno
        bene anche i dati["marcatori"] di esporta). Ogni voce va sulla
        chiave fatta di nome, durata e sottobrano, cosi' i marker compaiono
        su ogni copia del file; le voci senza una durata valida si saltano.
        Un marker che cade entro la tolleranza di uno che c'e' gia' non si
        aggiunge, e resta il nome di qui. Una voce che manca nasce senza
        percorsi: il primo arriva quando qui si mette un marker con T su
        quel file (aggiungi).
        Restituisce (aggiunti, gia_presenti, chiavi_toccate); le chiavi
        toccate, in ordine e senza doppioni, sono quelle che hanno ricevuto
        marker nuovi, da rinfrescare nella plancia."""
        aggiunti, gia_presenti, toccate = 0, 0, []
        for voce in voci:
            durata = _durata_valida(voce.get("durata"))
            file = os.path.basename(str(voce.get("file") or ""))
            if durata is None or not file:
                continue
            sottobrano = voce.get("sottobrano") or None
            k = chiave(file, durata, sottobrano)
            for m in voce.get("marker") or []:
                tempo = float(m["tempo"])
                if self.trova(k, tempo):
                    gia_presenti += 1
                    continue
                nuova = self.voci.setdefault(k, {"file": file, "durata": durata, "sottobrano": sottobrano, "percorsi": [], "marker": []})
                nuova["marker"].append({"tempo": tempo, "nome": str(m["nome"])})
                # forse() deve trovare il file anche prima del riavvio.
                self._nomi.add(file.casefold())
                aggiunti += 1
                if k not in toccate:
                    toccate.append(k)
        for k in toccate:
            self.voci[k]["marker"].sort(key=lambda m: m["tempo"])
        if aggiunti:
            self.modificato = True
        return aggiunti, gia_presenti, toccate
