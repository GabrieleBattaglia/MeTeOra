# MeTeOra, il filtro delle playlist: dal testo scritto da chi ascolta a una funzione che dice si' o no a ogni brano.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la 1.8.0, issue 2. Nella 1.34.0 i commenti col dollaro e la grammatica della ricerca nella console.

"""Il filtro delle playlist.

La grammatica, decisa con Gabriele nella issue 2:
- i termini si separano con gli spazi, e devono valere tutti (AND); andare a
  capo vale come uno spazio;
- la barra verticale unisce alternative: hubbard|galway vuol dire l'uno o
  l'altro (OR); lega piu' dello spazio, quindi rob hubbard|galway e' rob e
  poi hubbard o galway;
- il meno davanti a un termine lo nega (NOT); dentro una parola e' un
  carattere come gli altri (AC-DC);
- * vale qualsiasi sequenza di caratteri, # una o piu' cifre;
- le virgolette cercano la sequenza esatta, spazi compresi, senza jolly;
- una lettera seguita da <, >, =, <= o >= e' un comando: t tempo, d
  dimensione, k tipo, a autore, n titolo, l album, g genere, y anno,
  p percorso, s saltato, r sottobrani dei SID.
Un termine senza comando cerca nel nome del file e nei tag. Maiuscole e
accenti non contano. L'ordine dei termini non conta.

Nei campi in cui si scrivono filtri e ricerche le righe che cominciano con il
dollaro sono commenti: MeTeOra ci mette le istruzioni, e non contano. Il
cancelletto no, perche' e' gia' il jolly delle cifre (dalla 1.34.0).

La ricerca nella console ha una grammatica sua, piu' semplice: il testo si
cerca cosi' com'e', spazi compresi e senza badare alle maiuscole; l'asterisco
vale qualsiasi testo nella stessa riga, il cancelletto una o piu' cifre, e
fra virgolette la sequenza e' esatta, maiuscole comprese.
"""

import os
import re
import unicodedata

import formati
from lingua import _

OPERATORI = ("<=", ">=", "<", ">", "=")
_TERMINE = re.compile(r'-?(?:"[^"]*"|[^\s"|]+)(?:\|(?:"[^"]*"|[^\s"|]+))*|\|')
_COMANDO = re.compile(r"^([a-z])(<=|>=|<|>|=)(.*)$", re.IGNORECASE)
FAMIGLIE = {
    "audio": formati.AUDIO | formati.SID | formati.MIDI | formati.CHIP,
    "video": formati.VIDEO,
    "sid": formati.SID,
    "tracker": formati.TRACKER,
    "midi": formati.MIDI,
    "chip": formati.CHIP,
}
NUMERICI = {"t", "d", "y", "r"}
# Le chiavi dei tag nella scheda dello schedario.
TESTUALI = {"a": "autore", "n": "titolo", "l": "album", "g": "genere"}
# I nomi dei comandi, per le frasi d'errore: le lettere restano quelle, i
# nomi si traducono (3.0.0).
NOMI_DEI_COMANDI = {
    # Traduttori: i nomi dei comandi del filtro, come in «I comandi sono: t tempo, d dimensione»; la lettera resta quella.
    "t": _("tempo"),
    "d": _("dimensione"),
    # Traduttori: il nome del comando k del filtro, il tipo di file, come mp3 o audio.
    "k": _("tipo"),
    "a": _("autore"),
    "n": _("titolo"),
    "l": _("album"),
    "g": _("genere"),
    "y": _("anno"),
    "p": _("percorso"),
    # Traduttori: il nome del comando s del filtro, i brani da saltare.
    "s": _("saltato"),
    # Traduttori: il nome del comando r del filtro, quanti sottobrani ha un file SID.
    "r": _("sottobrani"),
}


COMMENTO = "$"


class ErroreFiltro(ValueError):
    """Il testo del filtro non si capisce; il messaggio dice dove."""


def senza_commenti(testo):
    """Il testo scritto nel campo senza le righe di commento, quelle che
    cominciano con il dollaro, anche dopo qualche spazio."""
    return "\n".join(r for r in testo.splitlines() if not r.lstrip().startswith(COMMENTO))


def modello_della_console(testo):
    """L'espressione regolare che cerca il testo nella console: fuori dalle
    virgolette maiuscole e minuscole non contano, l'asterisco vale qualsiasi
    testo nella stessa riga e il cancelletto una o piu' cifre; fra le
    virgolette la sequenza e' esatta, maiuscole comprese, senza jolly."""
    if testo.count('"') % 2:
        raise ErroreFiltro(_("Le virgolette non sono chiuse."))
    # La ricerca non e' ancorata: un asterisco in testa non aggiunge niente,
    # e toglierlo fa cominciare l'occorrenza dove comincia cio' che si cerca,
    # senza rallentare la ricerca con tutte le righe lunghe.
    testo = testo.lstrip("*")
    if not testo.strip("* "):
        raise ErroreFiltro(_("Scrivi cosa cercare: l'asterisco da solo trova qualsiasi cosa."))
    parti = []
    for pezzo in re.split(r'("[^"]*")', testo):
        if pezzo.startswith('"'):
            if len(pezzo) == 2:
                raise ErroreFiltro(_("Fra le virgolette non c'è niente."))
            parti.append(re.escape(pezzo[1:-1]))
        elif pezzo:
            libero = "".join(r"[^\n]*" if c == "*" else r"\d+" if c == "#" else re.escape(c) for c in pezzo)
            parti.append(f"(?i:{libero})")
    if not parti:
        raise ErroreFiltro(_("Scrivi cosa cercare."))
    return re.compile("".join(parti))


def normale(testo):
    """Senza maiuscole e senza accenti."""
    scomposto = unicodedata.normalize("NFD", str(testo))
    return "".join(c for c in scomposto if not unicodedata.combining(c)).casefold()


def _modello(testo):
    """Un'espressione regolare da un termine con i jolly * e #."""
    parti = []
    for c in normale(testo):
        if c == "*":
            parti.append(".*")
        elif c == "#":
            parti.append(r"\d+")
        else:
            parti.append(re.escape(c))
    return re.compile("".join(parti))


def _tempo(testo):
    parti = testo.strip().replace(",", ".").split(":")
    try:
        numeri = [int(p) for p in parti[:-1]] + [float(parti[-1])]
    except ValueError:
        return None
    if not 1 <= len(numeri) <= 3 or any(n < 0 for n in numeri):
        return None
    totale = 0.0
    for n in numeri:
        totale = totale * 60 + n
    return totale


def _dimensione(testo):
    """Byte da un numero con k, m o g facoltativi: 700k, 5m, 1.5g."""
    testo = testo.strip().lower().replace(",", ".")
    moltiplicatore = 1
    if testo and testo[-1] in "kmg":
        moltiplicatore = {"k": 1024, "m": 1024 ** 2, "g": 1024 ** 3}[testo[-1]]
        testo = testo[:-1]
    try:
        return float(testo) * moltiplicatore
    except ValueError:
        return None


def _confronta(valore, operatore, soglia):
    if valore is None:
        return False
    return {"<": valore < soglia, ">": valore > soglia, "=": valore == soglia, "<=": valore <= soglia, ">=": valore >= soglia}[operatore]


def _alternativa(testo):
    """Una funzione (brano, scheda, testo_normale) -> bool per un pezzo di
    termine: una frase fra virgolette, un comando o una parola."""
    if testo.startswith('"'):
        frase = normale(testo.strip('"'))
        if not frase:
            raise ErroreFiltro(_("Fra le virgolette non c'è niente."))
        return lambda _b, _s, dove: frase in dove
    comando = _COMANDO.match(testo)
    if comando:
        return _comando(comando.group(1).lower(), comando.group(2), comando.group(3), testo)
    modello = _modello(testo)
    return lambda _b, _s, dove: modello.search(dove) is not None


def _comando(lettera, operatore, valore, testo):
    if lettera not in NOMI_DEI_COMANDI:
        # Traduttori: {testo} e' il termine del filtro, {lettera} la lettera che non e' un comando, {comandi} l'elenco, come «t tempo, d dimensione».
        raise ErroreFiltro(_("In {testo}, {lettera} non è un comando. I comandi sono: {comandi}.").format(testo=testo, lettera=lettera,
            comandi=", ".join(f"{k} {v}" for k, v in NOMI_DEI_COMANDI.items())))
    if not valore:
        # Traduttori: {operatore} e' il segno del confronto, come < o =.
        raise ErroreFiltro(_("In {testo} manca il valore dopo {operatore}.").format(testo=testo, operatore=operatore))
    nome = NOMI_DEI_COMANDI[lettera]
    if lettera not in NUMERICI and operatore != "=":
        # Traduttori: {lettera} e' la lettera del comando, {nome} il suo nome, come «a, autore».
        raise ErroreFiltro(_("In {testo}: il comando {lettera}, {nome}, accetta solo l'uguale.").format(testo=testo, lettera=lettera, nome=nome))
    if lettera == "t":
        soglia = _tempo(valore)
        if soglia is None:
            raise ErroreFiltro(_("In {testo}, {valore} non è un tempo: si scrive come 3:00, 1:02:03 o in secondi.").format(testo=testo, valore=valore))
        return lambda b, s, _d: _confronta(_durata(b, s), operatore, soglia)
    if lettera == "d":
        soglia = _dimensione(valore)
        if soglia is None:
            # Traduttori: le lettere k, m e g degli esempi restano come sono: sono quelle che il filtro capisce.
            raise ErroreFiltro(_("In {testo}, {valore} non è una dimensione: si scrive come 700k, 5m o 1.5g.").format(testo=testo, valore=valore))
        return lambda _b, s, _d: _confronta(s.get("dim") if s else None, operatore, soglia)
    if lettera in ("y", "r"):
        if not valore.isdigit():
            raise ErroreFiltro(_("In {testo}, {valore} non è un numero intero.").format(testo=testo, valore=valore))
        soglia = int(valore)
        chiave = "anno" if lettera == "y" else "sottobrani"
        if lettera == "y":
            return lambda _b, s, _d: _confronta((s or {}).get("tag", {}).get(chiave), operatore, soglia)
        return lambda _b, s, _d: _confronta((s or {}).get(chiave), operatore, soglia)
    if lettera == "k":
        valore = normale(valore).lstrip(".")
        estensioni = FAMIGLIE.get(valore, frozenset({"." + valore}))
        return lambda b, _s, _d: formati.estensione(b.percorso) in estensioni
    if lettera == "s":
        # 1, 0, si' e no valgono sempre; accanto, si' e no nella lingua di MeTeOra (3.0.0).
        si, no = {"1", "si", normale(_("sì"))}, {"0", "no", normale(_("no"))}
        if normale(valore) not in si | no:
            # Traduttori: la lettera s resta s; saltato e' il nome del comando, come nell'elenco dei comandi.
            raise ErroreFiltro(_("In {testo}: il comando s, saltato, vuole 1 o 0.").format(testo=testo))
        voluto = normale(valore) in si
        return lambda b, _s, _d: b.saltato == voluto
    if lettera == "p":
        modello = _modello(valore)
        return lambda b, _s, _d: modello.search(normale(os.path.dirname(b.percorso))) is not None
    modello = _modello(valore)
    chiave = TESTUALI[lettera]
    return lambda _b, s, _d: modello.search(normale((s or {}).get("tag", {}).get(chiave) or "")) is not None


def _durata(brano, scheda):
    if not scheda:
        return None
    if brano.sottobrano:
        durate = scheda.get("durate_sid")
        return durate[brano.sottobrano - 1] if durate and brano.sottobrano <= len(durate) else None
    return scheda.get("durata")


def dove_cercare(brano, scheda):
    """Il testo in cui cercano i termini senza comando: nome del file e tag."""
    parti = [os.path.basename(brano.percorso)]
    if scheda:
        parti.extend(str(v) for v in scheda.get("tag", {}).values() if v)
    return normale(" / ".join(parti))


class Filtro:
    def __init__(self, testo):
        self.testo = " ".join(testo.split())
        self._termini = []
        pezzi = _TERMINE.findall(self.testo)
        # Una barra staccata, come in hubbard | galway, unisce i due vicini.
        uniti = []
        for pezzo in pezzi:
            if uniti and (pezzo == "|" or uniti[-1].endswith("|")):
                uniti[-1] += pezzo
            else:
                uniti.append(pezzo)
        for termine in uniti:
            if termine.strip("|") != termine and "|" in (termine[0], termine[-1]):
                raise ErroreFiltro(_("In {termine} la barra verticale deve stare fra due alternative.").format(termine=termine))
            negato = termine.startswith("-") and len(termine) > 1
            corpo = termine[1:] if negato else termine
            alternative = [_alternativa(a) for a in re.findall(r'"[^"]*"|[^|]+', corpo)]
            if not alternative:
                raise ErroreFiltro(_("Il termine {termine} è vuoto.").format(termine=termine))
            self._termini.append((negato, alternative))
        if self.testo.count('"') % 2:
            raise ErroreFiltro(_("Le virgolette non sono chiuse."))

    @property
    def vuoto(self):
        return not self._termini

    def ammette(self, brano, scheda):
        """Vero se il brano, con la sua scheda (o None), passa il filtro."""
        if not self._termini:
            return True
        dove = dove_cercare(brano, scheda)
        return all(any(a(brano, scheda, dove) for a in alternative) != negato for negato, alternative in self._termini)
