# MeTeOra, le playlist: brani, playlist, archivio e coda di riproduzione.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.2.0 il sottobrano dei SID, nella 1.3.0 il loop A-B, nella 1.6.0 i Preferiti.

"""Il modello dei dati, senza finestre e senza suono.

Una Playlist e' una lista di Brano. Quelle dell'archivio si salvano nel file
JSON di MeTeOra; quelle temporanee nascono da una cartella di Questo PC, o
dal file aperto con Apri file, e si perdono alla chiusura.
La Coda dice cosa sta suonando: la playlist di provenienza e il brano. Tiene
il brano e non la sua posizione, cosi' spostare o togliere altri brani
mentre suona non la confonde. Tiene anche il loop A-B: due brani di una
playlist fra i quali la riproduzione gira in tondo.
"""

import json
import os
import random

VERSIONE_DEL_FILE = 1


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
        return [b for b in self.playlist.brani[primo:ultimo + 1] if not b.saltato]

    def primo(self, playlist):
        """Il primo brano non saltato della playlist, o del suo loop; None se non ce n'e'."""
        primo, ultimo = self._campo(playlist)
        return next((b for b in playlist.brani[primo:ultimo + 1] if not b.saltato), None)

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
                if not candidato.saltato:
                    return candidato
            return None
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
