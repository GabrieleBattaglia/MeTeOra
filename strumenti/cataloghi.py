# MeTeOra, sviluppo: il catalogo dei testi e le traduzioni (3.0.0).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 3.0.0, la localizzazione, sul modello degli strumenti di Orologic.

"""Il catalogo dei testi di MeTeOra e i cataloghi delle traduzioni.

Uso, dalla cartella di MeTeOra:
  python strumenti\\cataloghi.py estrai
      rifa locales\\messages.pot, il modello con tutti i testi, con pybabel;
  python strumenti\\cataloghi.py nuova CODICE
      comincia la traduzione in una lingua, per esempio en, in
      locales\\CODICE\\LC_MESSAGES\\messages.po;
  python strumenti\\cataloghi.py aggiorna
      porta i testi nuovi del modello in tutte le traduzioni;
  python strumenti\\cataloghi.py verifica
      controlla le traduzioni: segnaposto, plurali, spazi ai bordi, separatori;
  python strumenti\\cataloghi.py compila [--forza]
      verifica e compila le traduzioni nei messages.mo che MeTeOra legge;
  python strumenti\\cataloghi.py scoperti [--parole] [FILE...]
      elenca le stringhe dei moduli che sembrano testi per l'utente e non
      passano dalla traduzione, da rivedere a mano; con --parole anche quelle
      di una parola sola.
Le prime cinque vogliono babel e polib (requirements-dev.txt).
"""

import ast
import os
import re
import string
import subprocess
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGHI = os.path.join(RADICE, "locales")
MODELLO = os.path.join(CATALOGHI, "messages.pot")
DOMINIO = "messages"
# Le funzioni che pybabel legge: _ e ngettext ci sono gia', plurale e' quella
# di lingua.py, con singolare e plurale come secondo e terzo argomento.
PAROLE_CHIAVE = ["-k", "plurale:2,3"]
# I commenti che cominciano cosi', sopra un testo, vanno ai traduttori.
COMMENTO_PER_I_TRADUTTORI = "Traduttori:"
SEPARATORI = re.compile(r"[-=_]{4,}")
# Le chiamate i cui testi non si traducono: il registro degli errori resta in
# italiano, perche' lo legge l'autore.
CHIAMATE_SENZA_TRADUZIONE = {("registro", "scrivi")}
FUNZIONI_DI_TRADUZIONE = {"_", "ngettext", "plurale"}
FUORI_DAL_CATALOGO = {"setup_maker.py", "zip_maker.py"}


def _babel(*argomenti):
    return subprocess.run([sys.executable, "-m", "babel.messages.frontend", *argomenti], cwd=RADICE, check=False).returncode


def estrai():
    import version

    os.makedirs(CATALOGHI, exist_ok=True)
    return _babel("extract", "-F", "babel.cfg", *PAROLE_CHIAVE, "-c", COMMENTO_PER_I_TRADUTTORI, "--project", "MeTeOra", "--version", version.VERSION,
        "--copyright-holder", "Gabriele Battaglia", "--msgid-bugs-address", "https://github.com/GabrieleBattaglia/MeTeOra/issues", "-o", MODELLO, ".")


def nuova(codice):
    return _babel("init", "-i", MODELLO, "-d", CATALOGHI, "-D", DOMINIO, "-l", codice)


def aggiorna():
    return _babel("update", "-i", MODELLO, "-d", CATALOGHI, "-D", DOMINIO)


def _segnaposto(testo):
    return {campo for _testo, campo, _spec, _conv in string.Formatter().parse(testo) if campo is not None}


def _traduzioni():
    if not os.path.isdir(CATALOGHI):
        return []
    return sorted(os.path.join(CATALOGHI, c, "LC_MESSAGES", f"{DOMINIO}.po") for c in os.listdir(CATALOGHI)
        if os.path.isfile(os.path.join(CATALOGHI, c, "LC_MESSAGES", f"{DOMINIO}.po")))


def _bordi(testo):
    return testo[:len(testo) - len(testo.lstrip())], testo[len(testo.rstrip()):]


def problemi(percorso):
    """I problemi di una traduzione, come righe da leggere: segnaposto che non
    tornano, che farebbero cadere MeTeOra quando il testo esce, spazi ai bordi
    diversi dall'originale e separatori grafici."""
    import polib

    righe = []
    for voce in polib.pofile(percorso):
        if voce.obsolete or "fuzzy" in voce.flags:
            continue
        try:
            originali = _segnaposto(voce.msgid) | (_segnaposto(voce.msgid_plural) if voce.msgid_plural else set())
        except ValueError:
            continue
        tradotte = list(voce.msgstr_plural.values()) if voce.msgid_plural else [voce.msgstr]
        for tradotta in (t for t in tradotte if t):
            try:
                trovati = _segnaposto(tradotta)
            except ValueError:
                righe.append(f"riga {voce.linenum}: graffe spaiate in {tradotta!r}")
                continue
            if not trovati <= originali or (not voce.msgid_plural and trovati != originali):
                righe.append(f"riga {voce.linenum}: segnaposto {sorted(trovati)} invece di {sorted(originali)} in {tradotta!r}")
            if _bordi(tradotta) != _bordi(voce.msgid):
                righe.append(f"riga {voce.linenum}: spazi ai bordi diversi dall'originale in {tradotta!r}")
            if SEPARATORI.search(tradotta) and not SEPARATORI.search(voce.msgid):
                righe.append(f"riga {voce.linenum}: un separatore grafico in {tradotta!r}")
    return righe


def verifica():
    tutti = 0
    for percorso in _traduzioni():
        righe = problemi(percorso)
        tutti += len(righe)
        print(f"{os.path.relpath(percorso, RADICE)}: {len(righe) or 'nessun'} problem{'a' if len(righe) == 1 else 'i'}.")
        for riga in righe:
            print(f"  {riga}")
    if not _traduzioni():
        print("Nessuna traduzione in locales.")
    return 1 if tutti else 0


def compila(forza=False):
    if verifica() and not forza:
        print("Compilazione non eseguita: prima vanno sistemate le traduzioni.")
        return 1
    return _babel("compile", "-d", CATALOGHI, "-D", DOMINIO, "--statistics")


def _dentro(nodo, genitori, condizione):
    while nodo in genitori:
        nodo = genitori[nodo]
        if condizione(nodo):
            return True
    return False


def _chiamata(nodo):
    """Il nome della funzione chiamata: _ per _(...), ("registro", "scrivi") per registro.scrivi(...)."""
    if isinstance(nodo.func, ast.Name):
        return nodo.func.id
    if isinstance(nodo.func, ast.Attribute) and isinstance(nodo.func.value, ast.Name):
        return nodo.func.value.id, nodo.func.attr
    return None


def scoperti(file, parole=False):
    """Le stringhe di un modulo che sembrano testi per l'utente e non passano
    da _, ngettext o plurale: (riga, testo). Fuori le docstring, le chiavi dei
    dizionari, i confronti, gli indici e i testi del registro."""
    with open(file, encoding="utf-8") as f:
        albero = ast.parse(f.read())
    genitori = {figlio: padre for padre in ast.walk(albero) for figlio in ast.iter_child_nodes(padre)}
    docstring = set()
    for nodo in ast.walk(albero):
        if isinstance(nodo, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and nodo.body:
            primo = nodo.body[0]
            if isinstance(primo, ast.Expr) and isinstance(primo.value, ast.Constant) and isinstance(primo.value.value, str):
                docstring.add(primo.value)
    trovati = []
    for nodo in ast.walk(albero):
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str):
            if nodo in docstring or isinstance(genitori.get(nodo), (ast.JoinedStr, ast.FormattedValue)):
                continue
            testo = nodo.value
        elif isinstance(nodo, ast.JoinedStr):
            if isinstance(genitori.get(nodo), ast.FormattedValue):
                continue
            testo = "".join(p.value if isinstance(p, ast.Constant) else "{}" for p in nodo.values)
        else:
            continue
        lettere = re.sub(r"\{\}", "", testo)
        if not any(c.isalpha() for c in lettere):
            continue
        if " " not in lettere.strip() and not (parole and re.fullmatch(r"[^\W\d_]{2,}", lettere.strip())):
            continue
        padre = genitori.get(nodo)
        if isinstance(padre, ast.Dict) and nodo in padre.keys:
            continue
        if isinstance(padre, (ast.Compare, ast.Subscript, ast.MatchValue)):
            continue
        if _dentro(nodo, genitori, lambda n: isinstance(n, ast.Call) and _chiamata(n) in FUNZIONI_DI_TRADUZIONE | CHIAMATE_SENZA_TRADUZIONE):
            continue
        trovati.append((nodo.lineno, testo))
    return sorted(trovati)


def elenca_scoperti(file, parole=False):
    if not file:
        file = sorted(os.path.join(RADICE, n) for n in os.listdir(RADICE) if n.endswith(".py") and n not in FUORI_DAL_CATALOGO)
    tutti = 0
    for percorso in file:
        voci = scoperti(percorso, parole)
        tutti += len(voci)
        for riga, testo in voci:
            print(f"{os.path.basename(percorso)}:{riga}: {testo[:110]}")
    print(f"Stringhe da rivedere: {tutti}.")
    return 0


def principale(argomenti):
    for flusso in (sys.stdout, sys.stderr):
        if hasattr(flusso, "reconfigure"):
            flusso.reconfigure(errors="replace")
    sys.path.insert(0, RADICE)
    comando = argomenti[0] if argomenti else ""
    if comando == "estrai":
        return estrai()
    if comando == "nuova" and len(argomenti) == 2:
        return nuova(argomenti[1])
    if comando == "aggiorna":
        return aggiorna()
    if comando == "verifica":
        return verifica()
    if comando == "compila":
        return compila("--forza" in argomenti)
    if comando == "scoperti":
        return elenca_scoperti([a for a in argomenti[1:] if a != "--parole"], "--parole" in argomenti)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(principale(sys.argv[1:]))
