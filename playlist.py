# MeTeOra, le playlist: brani, playlist, archivio e coda di riproduzione.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1.

"""Il modello dei dati, senza finestre e senza suono.

Una Playlist e' una lista di Brano. Quelle dell'archivio si salvano nel file
JSON di MeTeOra; quelle temporanee nascono da una cartella di Questo PC, o
dal file aperto con Apri file, e si perdono alla chiusura.
La Coda dice cosa sta suonando: la playlist di provenienza e il brano. Tiene
il brano e non la sua posizione, cosi' spostare o togliere altri brani
mentre suona non la confonde.
"""

import json
import os
import random

VERSIONE_DEL_FILE = 1


class Brano:
    def __init__(self, percorso, saltato=False):
        self.percorso = percorso
        self.saltato = saltato

    @property
    def nome(self):
        """Il nome del file senza estensione."""
        return os.path.splitext(os.path.basename(self.percorso))[0]

    @property
    def nome_del_file(self):
        """Il nome del file con l'estensione, come compare nella plancia."""
        return os.path.basename(self.percorso)

    def come_dati(self):
        return {"percorso": self.percorso, "saltato": self.saltato}

    @classmethod
    def da_dati(cls, dati):
        return cls(dati["percorso"], bool(dati.get("saltato", False)))


class Playlist:
    def __init__(self, nome, brani=None, cartella=None):
        self.nome = nome
        self.brani = list(brani or [])
        # La cartella di Questo PC da cui nasce una playlist temporanea.
        self.cartella = cartella

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

    def togli(self, brano):
        i = self.indice(brano)
        if i is not None:
            del self.brani[i]
        return i

    def come_dati(self):
        return {"nome": self.nome, "brani": [b.come_dati() for b in self.brani]}

    @classmethod
    def da_dati(cls, dati):
        return cls(dati["nome"], [Brano.da_dati(b) for b in dati.get("brani", [])])


class Archivio:
    """Le playlist salvate, nell'ordine in cui compaiono nella plancia."""

    def __init__(self, percorso):
        self.percorso = percorso
        self.playlist = []

    def carica(self):
        """Legge il file; se non c'e' l'archivio resta vuoto."""
        if not os.path.isfile(self.percorso):
            self.playlist = []
            return
        with open(self.percorso, encoding="utf-8") as f:
            dati = json.load(f)
        self.playlist = [Playlist.da_dati(p) for p in dati.get("playlist", [])]

    def salva(self):
        """Scrive su un file accanto e poi lo sostituisce, cosi' un'uscita a
        meta' scrittura non lascia un archivio troncato."""
        dati = {"versione": VERSIONE_DEL_FILE, "playlist": [p.come_dati() for p in self.playlist]}
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


class Coda:
    """Cosa suona: una playlist e il suo brano corrente."""

    def __init__(self):
        self.playlist = None
        self.corrente = None

    def imposta(self, playlist, brano):
        self.playlist = playlist
        self.corrente = brano

    def _suonabili(self):
        return [b for b in self.playlist.brani if not b.saltato] if self.playlist else []

    def primo(self, playlist):
        """Il primo brano non saltato della playlist, o None."""
        return next((b for b in playlist.brani if not b.saltato), None)

    def _vicino(self, passo):
        if not self.playlist:
            return None
        brani = self.playlist.brani
        i = self.playlist.indice(self.corrente)
        if i is None:
            # Il brano corrente e' stato tolto: si riparte dal primo.
            return self.primo(self.playlist) if passo > 0 else None
        i += passo
        while 0 <= i < len(brani):
            if not brani[i].saltato:
                return brani[i]
            i += passo
        return None

    def successivo(self):
        return self._vicino(1)

    def precedente(self):
        return self._vicino(-1)

    def casuale(self, scelta=random.choice):
        """Un brano a caso fra quelli non saltati, diverso dal corrente
        quando ce n'e' piu' di uno."""
        candidati = [b for b in self._suonabili() if b is not self.corrente] or self._suonabili()
        return scelta(candidati) if candidati else None

    def posizione(self):
        """(numero del brano, totale), contando anche i saltati."""
        if not self.playlist:
            return None
        i = self.playlist.indice(self.corrente)
        return (i + 1 if i is not None else None, len(self.playlist.brani))
