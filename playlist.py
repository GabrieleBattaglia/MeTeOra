# MeTeOra, le playlist: brani, playlist, archivio e coda di riproduzione.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.2.0 il sottobrano dei SID, nella 1.3.0 il loop A-B, nella 1.6.0 i Preferiti, nella 1.8.0 il filtro. Nella 1.59.0 Coda.altri, per la riproduzione casuale. Nella 1.104.0 si tolgono i brani dei file spariti, per la pulizia all'avvio. Nella 1.109.0 Ordina, Inverti l'ordine, Mescola e Ordine di prima. Nella 1.113.0 l'origine delle playlist importate da un M3U o da un PLS di altri programmi.

"""Il modello dei dati, senza finestre e senza suono.

Una Playlist e' una lista di Brano. Quelle dell'archivio si salvano nel file
JSON di MeTeOra; quelle temporanee nascono da una cartella di Questo PC, o
dal file aperto con Apri file, e si perdono alla chiusura. Una playlist
importata da un M3U o da un PLS ricorda il file da cui viene, la sua
origine, per riconoscerlo quando arriva di nuovo (1.113.0).
La Coda dice cosa sta suonando: la playlist di provenienza e il brano. Tiene
il brano e non la sua posizione, cosi' spostare o togliere altri brani
mentre suona non la confonde. Tiene anche il loop A-B: due brani di una
playlist fra i quali la riproduzione gira in tondo.
Ordina, Inverti l'ordine e Mescola cambiano l'ordine dei brani di una
playlist sul posto, con gli stessi oggetti Brano, e la playlist ricorda in
memoria l'ordine di prima, finche' MeTeOra resta aperto (tappa 14 c).
"""

import json
import os
import random
import re

import filtro
import formati

VERSIONE_DEL_FILE = 1

# I criteri di Ordina, nell'ordine del sottomenu (Gabriele, 20 ottobre 2026):
# la chiave, la voce del menu e il dato che puo' mancare, None per quelli che
# ogni brano ha. Ogni criterio va in un verso solo: dalla A alla Z, dal piu'
# vecchio, dal piu' corto. I brani senza il dato vanno in fondo.
CRITERI = {
    "nome": ("Per nome del file", None),
    "percorso": ("Per percorso", None),
    "titolo": ("Per titolo", "titolo"),
    "autore": ("Per autore", "autore"),
    "album": ("Per album", "album"),
    "anno": ("Per anno", "anno"),
    "durata": ("Per durata", "durata"),
}
_CIFRE = re.compile(r"(\d+)")
_BARRE = re.compile(r"[\\/]+")


def chiave_naturale(testo):
    """Un testo come si confronta per ordinare: senza maiuscole e senza
    accenti, come lo confronta il filtro, e con i numeri per il loro valore,
    cosi' Traccia 2 viene prima di Traccia 10. Nessuna regola sugli articoli:
    The Beatles va sotto la T. Fra due testi che cosi' sono uguali, come 2 e
    02, decide il testo senza maiuscole (tappa 14 c)."""
    normale = filtro.normale(testo)
    # Le cifre stanno sempre nei posti dispari: due chiavi si confrontano
    # numero con numero e testo con testo.
    return tuple(int(p) if i % 2 else p for i, p in enumerate(_CIFRE.split(normale))), normale


def chiave_del_percorso(brano):
    """Il posto del brano nell'ordine di Crea playlist da qui: unita' per
    unita' e cartella per cartella, con i file di una cartella prima delle
    sue sottocartelle e i numeri per valore. Un sottobrano messo in playlist
    come brano a se' va dopo il suo file, nell'ordine dei numeri."""
    unita, resto = os.path.splitdrive(brano.percorso)
    parti = [p for p in _BARRE.split(resto) if p]
    nome = parti.pop() if parti else ""
    # Una cartella vale 1 e il file 0: nella stessa cartella i file vengono
    # prima delle sottocartelle.
    return chiave_naturale(unita), (*((1, chiave_naturale(c)) for c in parti), (0, chiave_naturale(nome))), brano.sottobrano or 0


def durata_mostrata(brano, scheda):
    """La durata come la mostra la plancia: per un sottobrano la sua, per un
    SID o un file delle console con piu' sottobrani il totale; None se non
    si sa."""
    if not scheda:
        return None
    durate = scheda.get("durate_sid")
    if brano.sottobrano:
        return durate[brano.sottobrano - 1] if durate and brano.sottobrano <= len(durate) else None
    if formati.ha_sottobrani(brano.percorso) and (scheda.get("sottobrani") or 0) > 1:
        return sum(d or 0 for d in durate) if durate else None
    return scheda.get("durata")


def _intero(valore):
    return valore if isinstance(valore, int) and not isinstance(valore, bool) and valore >= 0 else None


# Il segnaposto della HVSC per un titolo o un autore che non si conosce: per
# Ordina e' un dato che manca, come per le statistiche.
SCONOSCIUTO = "<?>"


def _testo_del_tag(valore):
    """Un tag di testo come lo usa Ordina: None se manca, se e' vuoto o se e'
    il segnaposto della HVSC."""
    testo = str(valore or "").strip()
    return testo if testo and testo != SCONOSCIUTO else None


def _dati_per_ordinare(brano, scheda):
    """I dati della scheda che servono a Ordina, None quelli che mancano;
    traccia e disco ci sono solo nelle schede lette dalla tappa 14 c."""
    tag = (scheda or {}).get("tag") or {}
    testi = {chiave: _testo_del_tag(tag.get(chiave)) for chiave in ("titolo", "autore", "album")}
    return {**testi, "anno": _intero(tag.get("anno")), "durata": durata_mostrata(brano, scheda),
        "traccia": _intero((scheda or {}).get("traccia")), "disco": _intero((scheda or {}).get("disco"))}


def _secondario(testo):
    """Un dato che ordina dopo il criterio: prima chi ce l'ha, in ordine, poi chi no."""
    return (0, chiave_naturale(testo)) if testo else (1,)


def ordinati(brani, criterio, scheda_di):
    """(i brani nell'ordine del criterio, una chiave di CRITERI, quanti sono
    andati in fondo perche' senza il dato). scheda_di(brano) da' la scheda
    dello schedario, o None se non c'e' ancora. L'ordine e' stabile.
    Le chiavi dopo il criterio (Gabriele e ClaudIA, 20 ottobre 2026): per
    titolo l'autore e il percorso; per autore l'album; per anno l'autore e
    l'album; per durata il percorso; per nome del file il percorso. Dentro
    un album, cioe' fra i brani con lo stesso album nella stessa cartella,
    si va per disco e traccia se tutti hanno la traccia, con il disco che
    manca contato come il primo, altrimenti per percorso: le schede di prima
    della tappa 14 c non li hanno, e non si rileggono. Un titolo, un autore
    o un album <?>, il segnaposto della HVSC, manca come uno vuoto."""
    percorsi = {id(b): chiave_del_percorso(b) for b in brani}
    if criterio == "percorso":
        return sorted(brani, key=lambda b: percorsi[id(b)]), 0
    if criterio == "nome":
        return sorted(brani, key=lambda b: (chiave_naturale(b.nome_del_file), percorsi[id(b)])), 0
    dato = CRITERI[criterio][1]
    dati = {id(b): _dati_per_ordinare(b, scheda_di(b)) for b in brani}
    con = [b for b in brani if dati[id(b)][dato] is not None]
    senza = sorted((b for b in brani if dati[id(b)][dato] is None), key=lambda b: percorsi[id(b)])

    def testa(b):
        """(il criterio con le chiavi che lo seguono, vero se il brano sta in
        un album). Dentro un album la testa finisce con la cartella: lo
        stesso album in due cartelle, come due Greatest Hits di autori
        diversi, sono due album."""
        d = dati[id(b)]
        if criterio == "titolo":
            return (chiave_naturale(d["titolo"]), _secondario(d["autore"])), False
        if criterio == "durata":
            return (d["durata"],), False
        if criterio == "autore":
            prima = (chiave_naturale(d["autore"]), _secondario(d["album"]))
        elif criterio == "album":
            prima = (chiave_naturale(d["album"]),)
        else:
            prima = (d["anno"], _secondario(d["autore"]), _secondario(d["album"]))
        if not d["album"]:
            return prima, False
        unita, cartelle, _sottobrano = percorsi[id(b)]
        return (*prima, (unita, cartelle[:-1])), True

    teste = {id(b): testa(b) for b in con}
    # Un album va per disco e traccia solo se tutti i suoi brani hanno la traccia.
    con_la_traccia = {}
    for b in con:
        album, in_un_album = teste[id(b)]
        if in_un_album:
            con_la_traccia[album] = con_la_traccia.get(album, True) and dati[id(b)]["traccia"] is not None

    def chiave(b):
        d, (prima, _in_un_album) = dati[id(b)], teste[id(b)]
        # Un disco che manca, in un album che ha le tracce, e' il primo.
        numeri = (d["disco"] if d["disco"] is not None else 1, d["traccia"]) if con_la_traccia.get(prima) else (0, 0)
        return (*prima, numeri, percorsi[id(b)])

    return sorted(con, key=chiave) + senza, len(senza)


def _stesso_ordine(uno, altro):
    """Vero se le due liste hanno gli stessi oggetti, nello stesso ordine."""
    return len(uno) == len(altro) and all(a is b for a, b in zip(uno, altro, strict=True))


def mescolati(brani, mescola=random.shuffle, in_cima=None):
    """I brani in un ordine a caso, con ogni ordine ugualmente probabile:
    mescola e' random.shuffle, che le prove sostituiscono. Con in_cima, un
    brano della lista, quel brano va per primo e gli altri dopo di lui, a
    caso (Gabriele, 20 ottobre 2026)."""
    primo = [b for b in brani if b is in_cima][:1] if in_cima is not None else []
    altri = [b for b in brani if b is not in_cima] if primo else list(brani)
    mescola(altri)
    return primo + altri


def _norm(percorso):
    """Il percorso come si confronta: assoluto e, su Windows, con le
    maiuscole e le barre di sistema. E' la forma degli insiemi di percorsi
    spariti che arrivano dalla pulizia (1.104.0)."""
    return os.path.normcase(os.path.abspath(percorso))


def _origine(dati):
    """L'origine di una playlist importata, come la scrive il file dei dati:
    il percorso, la data e la dimensione del file M3U o PLS al momento
    dell'importazione (1.113.0). None se manca o non e' scritta bene."""
    if not isinstance(dati, dict):
        return None
    percorso, data, dimensione = dati.get("percorso"), dati.get("data"), dati.get("dimensione")
    if not isinstance(percorso, str) or not percorso or isinstance(data, bool) or not isinstance(data, (int, float)):
        return None
    if isinstance(dimensione, bool) or not isinstance(dimensione, int):
        return None
    return {"percorso": percorso, "data": float(data), "dimensione": dimensione}


class Brano:
    def __init__(self, percorso, saltato=False, sottobrano=None):
        self.percorso = percorso
        self.saltato = saltato
        # Per un SID, il sottobrano da suonare; None vuol dire quello iniziale.
        self.sottobrano = sottobrano

    @property
    def nome(self):
        """Il nome del file senza estensione."""
        return os.path.splitext(os.path.basename(self.percorso))[0]

    @property
    def nome_del_file(self):
        """Il nome del file con l'estensione, come compare nella plancia."""
        return os.path.basename(self.percorso)

    def come_dati(self):
        dati = {"percorso": self.percorso, "saltato": self.saltato}
        if self.sottobrano is not None:
            dati["sottobrano"] = self.sottobrano
        return dati

    @classmethod
    def da_dati(cls, dati):
        sottobrano = dati.get("sottobrano")
        return cls(dati["percorso"], bool(dati.get("saltato", False)), sottobrano if isinstance(sottobrano, int) and sottobrano > 0 else None)


class Playlist:
    def __init__(self, nome, brani=None, cartella=None, filtro="", origine=None):
        self.nome = nome
        self.brani = list(brani or [])
        # Il testo del filtro; vuoto vuol dire tutti i brani.
        self.filtro = filtro
        # La cartella di Questo PC da cui nasce una playlist temporanea.
        self.cartella = cartella
        # L'ordine di prima dell'ultimo Ordina, Inverti l'ordine o Mescola,
        # con gli stessi oggetti Brano; solo in memoria, non si salva.
        self.ordine_di_prima = None
        # Il file M3U o PLS da cui e' stata importata, con la sua data e la
        # sua dimensione di allora, o None (1.113.0).
        self.origine = origine

    @property
    def temporanea(self):
        return self.cartella is not None

    @classmethod
    def da_percorsi(cls, nome, percorsi, cartella=None):
        return cls(nome, [Brano(p) for p in percorsi], cartella)

    def indice(self, brano):
        """La posizione del brano, per identita'; None se non c'e' piu'."""
        for i, b in enumerate(self.brani):
            if b is brano:
                return i
        return None

    def sposta(self, brano, dove):
        """Sposta un brano: dove e' 'su', 'giu', 'cima' o 'fondo'. Vero se
        si e' mosso."""
        i = self.indice(brano)
        if i is None:
            return False
        nuovo = {"su": i - 1, "giu": i + 1, "cima": 0, "fondo": len(self.brani) - 1}[dove]
        if nuovo == i or not 0 <= nuovo < len(self.brani):
            return False
        self.brani.insert(nuovo, self.brani.pop(i))
        return True

    def riordina(self, nuovi):
        """Mette i brani nell'ordine nuovo, sul posto, e ricorda quello di
        prima per Ordine di prima. Falso, e niente cambia, se l'ordine e'
        lo stesso: allora anche l'ordine di prima resta com'era."""
        if _stesso_ordine(nuovi, self.brani):
            return False
        self.ordine_di_prima = list(self.brani)
        self.brani[:] = nuovi
        return True

    def ordina(self, criterio, scheda_di):
        """Ordina, con un criterio di CRITERI: (vero se l'ordine e'
        cambiato, quanti brani sono andati in fondo perche' senza il dato)."""
        nuovi, senza = ordinati(self.brani, criterio, scheda_di)
        return self.riordina(nuovi), senza

    def inverti(self):
        """Inverti l'ordine: la lista com'e', rovesciata, anche se l'ordine
        l'ha fatto chi ascolta. Vero se e' cambiata."""
        return self.riordina(self.brani[::-1])

    def mescola(self, mescola=random.shuffle, in_cima=None):
        """Mescola, come mescolati. Vero se l'ordine e' cambiato."""
        return self.riordina(mescolati(self.brani, mescola, in_cima))

    def rimetti_l_ordine_di_prima(self):
        """Ordine di prima: rimette l'ordine di prima dell'ultimo Ordina,
        Inverti o Mescola, con gli stessi oggetti Brano, cosi' la coda, il
        mazzo e la storia della riproduzione casuale li ritrovano. I brani
        aggiunti dopo restano in fondo, quelli tolti non tornano. L'ordine di
        prima poi si dimentica. Vero se l'ordine e' cambiato."""
        prima, self.ordine_di_prima = self.ordine_di_prima, None
        if prima is None:
            return False
        ci_sono = {id(b) for b in self.brani}
        tornano = [b for b in prima if id(b) in ci_sono]
        rimessi = {id(b) for b in tornano}
        nuovi = tornano + [b for b in self.brani if id(b) not in rimessi]
        if _stesso_ordine(nuovi, self.brani):
            return False
        self.brani[:] = nuovi
        return True

    def togli(self, brano):
        i = self.indice(brano)
        if i is not None:
            del self.brani[i]
        return i

    def togli_i_percorsi(self, spariti):
        """Toglie tutti i brani dei file spariti, un insieme di percorsi gia'
        normalizzati con normcase e abspath: anche i doppioni e gli altri
        sottobrani dello stesso file, scritti in qualunque forma. Lavora sul
        posto, cosi' chi tiene la lista la vede cambiare, e restituisce i
        brani tolti, nel loro ordine (1.104.0)."""
        if not spariti:
            return []
        tolti, restano = [], []
        for b in self.brani:
            (tolti if _norm(b.percorso) in spariti else restano).append(b)
        if tolti:
            self.brani[:] = restano
        return tolti

    def come_dati(self):
        dati = {"nome": self.nome, "brani": [b.come_dati() for b in self.brani]}
        if self.filtro:
            dati["filtro"] = self.filtro
        if self.origine:
            dati["origine"] = dict(self.origine)
        return dati

    @classmethod
    def da_dati(cls, dati):
        filtro = dati.get("filtro")
        return cls(dati["nome"], [Brano.da_dati(b) for b in dati.get("brani", [])], filtro=filtro if isinstance(filtro, str) else "",
            origine=_origine(dati.get("origine")))


class Archivio:
    """Le playlist salvate, nell'ordine in cui compaiono nella plancia, e i
    Preferiti, una playlist speciale che non si rinomina e non si elimina."""

    def __init__(self, percorso):
        self.percorso = percorso
        self.playlist = []
        self.preferiti = Playlist("Preferiti")

    def carica(self):
        """Legge il file; se non c'e' l'archivio resta vuoto."""
        self.preferiti = Playlist("Preferiti")
        if not os.path.isfile(self.percorso):
            self.playlist = []
            return
        with open(self.percorso, encoding="utf-8") as f:
            dati = json.load(f)
        self.playlist = [Playlist.da_dati(p) for p in dati.get("playlist", [])]
        if isinstance(dati.get("preferiti"), dict):
            self.preferiti = Playlist.da_dati(dati["preferiti"])
            self.preferiti.nome = "Preferiti"

    def nei_preferiti(self, brano):
        """Il brano dei Preferiti con lo stesso file e sottobrano, o None."""
        return next((b for b in self.preferiti.brani if b.percorso == brano.percorso and b.sottobrano == brano.sottobrano), None)

    def salva(self):
        """Scrive su un file accanto e poi lo sostituisce, cosi' un'uscita a
        meta' scrittura non lascia un archivio troncato."""
        dati = {"versione": VERSIONE_DEL_FILE, "playlist": [p.come_dati() for p in self.playlist], "preferiti": self.preferiti.come_dati()}
        provvisorio = self.percorso + ".tmp"
        with open(provvisorio, "w", encoding="utf-8") as f:
            json.dump(dati, f, ensure_ascii=False, indent=1)
        os.replace(provvisorio, self.percorso)

    def nome_libero(self, base="Playlist"):
        """Un nome non ancora usato: base, poi base 2, base 3..."""
        nomi = {p.nome.casefold() for p in self.playlist}
        if base.casefold() not in nomi:
            return base
        n = 2
        while f"{base} {n}".casefold() in nomi:
            n += 1
        return f"{base} {n}"

    def nuova(self, nome=None, percorsi=()):
        pl = Playlist.da_percorsi(self.nome_libero(nome or "Playlist"), percorsi)
        self.playlist.append(pl)
        return pl

    def elimina(self, pl):
        self.playlist = [p for p in self.playlist if p is not pl]

    def dall_origine(self, percorso):
        """La playlist importata dal file M3U o PLS percorso, anche se poi e'
        stata rinominata, o None (1.113.0)."""
        chiave = _norm(percorso)
        return next((p for p in self.playlist if p.origine and _norm(p.origine["percorso"]) == chiave), None)

    def percorsi(self):
        """I percorsi dei brani di tutte le playlist e dei Preferiti, cosi'
        come sono scritti, per la pulizia all'avvio (1.104.0)."""
        return {b.percorso for pl in (*self.playlist, self.preferiti) for b in pl.brani}

    def togli_i_percorsi(self, spariti):
        """Toglie i brani dei file spariti da tutte le playlist e dai
        Preferiti, come Playlist.togli_i_percorsi, e restituisce le coppie
        (playlist, brano) dei tolti. Una playlist rimasta vuota resta: la
        si elimina a mano (1.104.0). Non salva: salva chi chiama."""
        return [(pl, b) for pl in (*self.playlist, self.preferiti) for b in pl.togli_i_percorsi(spariti)]


class Coda:
    """Cosa suona: una playlist e il suo brano corrente, e il loop A-B."""

    def __init__(self):
        self.playlist = None
        self.corrente = None
        # Il loop: la playlist e i due brani, A e B; B e' None finche' non
        # viene scelto, e fino ad allora il loop non limita niente.
        self.loop_playlist = None
        self.punto_a = None
        self.punto_b = None
        # Chi usa la coda puo' sostituirla con il filtro delle playlist: un
        # brano che non passa si comporta come un brano saltato.
        self.ammesso = lambda _playlist, _brano: True

    def _suonabile(self, playlist, brano):
        return not brano.saltato and self.ammesso(playlist, brano)

    def imposta(self, playlist, brano):
        self.playlist = playlist
        self.corrente = brano

    def togli_loop(self):
        self.loop_playlist = self.punto_a = self.punto_b = None

    def intervallo(self, playlist=None):
        """(primo, ultimo) indice del loop completo sulla playlist, o None se
        su quella playlist non c'e' un loop con tutti e due i punti."""
        playlist = playlist or self.playlist
        if playlist is None or self.loop_playlist is not playlist or self.punto_b is None:
            return None
        a, b = playlist.indice(self.punto_a), playlist.indice(self.punto_b)
        if a is None or b is None:
            return None
        return (min(a, b), max(a, b))

    def nel_loop(self, playlist, brano):
        """Vero se il brano si puo' suonare con il loop attuale: sempre, se
        su quella playlist non c'e' un loop completo."""
        limiti = self.intervallo(playlist)
        if limiti is None:
            return True
        i = playlist.indice(brano)
        return i is not None and limiti[0] <= i <= limiti[1]

    def _campo(self, playlist):
        """Gli indici fra cui si suona: tutta la playlist, o il loop."""
        return self.intervallo(playlist) or (0, len(playlist.brani) - 1)

    def _suonabili(self):
        if not self.playlist:
            return []
        primo, ultimo = self._campo(self.playlist)
        return [b for b in self.playlist.brani[primo:ultimo + 1] if self._suonabile(self.playlist, b)]

    def primo(self, playlist):
        """Il primo brano non saltato della playlist, o del suo loop; None se non ce n'e'."""
        primo, ultimo = self._campo(playlist)
        return next((b for b in playlist.brani[primo:ultimo + 1] if self._suonabile(playlist, b)), None)

    def _vicino(self, passo):
        if not self.playlist:
            return None
        brani = self.playlist.brani
        limiti = self.intervallo()
        i = self.playlist.indice(self.corrente)
        if limiti is not None:
            # Nel loop si gira in tondo: dopo B si torna ad A, e prima di A si va a B.
            primo, ultimo = limiti
            if i is None or not primo <= i <= ultimo:
                return self.primo(self.playlist)
            larghezza = ultimo - primo + 1
            for passi in range(1, larghezza + 1):
                candidato = brani[primo + (i - primo + passo * passi) % larghezza]
                if self._suonabile(self.playlist, candidato):
                    return candidato
            return None
        if i is None:
            # Il brano corrente e' stato tolto: si riparte dal primo.
            return self.primo(self.playlist) if passo > 0 else None
        i += passo
        while 0 <= i < len(brani):
            if self._suonabile(self.playlist, brani[i]):
                return brani[i]
            i += passo
        return None

    def successivo(self):
        return self._vicino(1)

    def precedente(self):
        return self._vicino(-1)

    def altri(self):
        """I brani non saltati della playlist, o del suo loop, tranne il
        corrente."""
        return [b for b in self._suonabili() if b is not self.corrente]

    def casuale(self, scelta=random.choice):
        """Un brano a caso fra quelli non saltati, diverso dal corrente
        quando ce n'e' piu' di uno."""
        candidati = self.altri() or self._suonabili()
        return scelta(candidati) if candidati else None

    def posizione(self):
        """(numero del brano, totale), contando anche i saltati."""
        if not self.playlist:
            return None
        i = self.playlist.indice(self.corrente)
        return (i + 1 if i is not None else None, len(self.playlist.brani))
