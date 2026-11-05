# MeTeOra, le prove della lingua: lingua.py e l'uso giusto di _, ngettext e plurale nei moduli.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 3.0.0, la localizzazione.

"""Le prove della lingua.

Le prove dei moduli leggono il codice, senza eseguirlo: un segnaposto
sbagliato in un testo tradotto si vedrebbe solo quando quel testo esce, e
con l'italiano, dove _ restituisce il testo com'e', molti non uscirebbero
mai nelle altre prove. Per ogni chiamata si controlla che pybabel possa
leggere il testo, cioe' che sia una stringa scritta per intero e non una
f-string o una variabile, e che i nomi fra graffe siano esattamente quelli
passati a format.
"""

import ast
import os
import string

import pytest

import lingua
import percorsi

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUORI_DAL_CATALOGO = {"setup_maker.py", "zip_maker.py"}
MODULI = sorted(n for n in os.listdir(RADICE) if n.endswith(".py") and n not in FUORI_DAL_CATALOGO)


def _segnaposto(testo):
    """I nomi fra graffe di un testo; ValueError se le graffe sono spaiate."""
    campi = set()
    for _testo, campo, spec, _conv in string.Formatter().parse(testo):
        if campo is None:
            continue
        if not campo.isidentifier():
            raise ValueError(f"il segnaposto {{{campo}}} non e' un nome semplice")
        if spec and "{" in spec:
            raise ValueError(f"il segnaposto {{{campo}}} ha una graffa nella forma")
        campi.add(campo)
    return campi


def _nome(chiamata):
    return chiamata.func.id if isinstance(chiamata, ast.Call) and isinstance(chiamata.func, ast.Name) else None


def _testo(nodo):
    return nodo.value if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str) else None


def _problemi(percorso):
    file = os.path.basename(percorso)
    with open(percorso, encoding="utf-8") as f:
        albero = ast.parse(f.read())
    problemi = []
    genitori = {figlio: padre for padre in ast.walk(albero) for figlio in ast.iter_child_nodes(padre)}
    usa = False
    for nodo in ast.walk(albero):
        nome = _nome(nodo)
        if nome not in ("_", "ngettext", "plurale"):
            continue
        usa = usa or nome in ("_", "ngettext", "plurale")
        dove = f"{file}:{nodo.lineno}"
        posizioni = {"_": (0,), "ngettext": (0, 1), "plurale": (1, 2)}[nome]
        if nodo.keywords or len(nodo.args) != {"_": 1, "ngettext": 3, "plurale": 3}[nome]:
            problemi.append(f"{dove}: {nome} con gli argomenti sbagliati")
            continue
        testi = [_testo(nodo.args[i]) for i in posizioni]
        if any(t is None for t in testi):
            problemi.append(f"{dove}: {nome} vuole il testo scritto per intero, non una f-string o una variabile")
            continue
        try:
            campi = set().union(*(_segnaposto(t) for t in testi))
        except ValueError as e:
            problemi.append(f"{dove}: {e}")
            continue
        if nome == "plurale":
            if not campi <= {"n"}:
                problemi.append(f"{dove}: plurale riempie solo {{n}}, non {sorted(campi - {'n'})}")
            continue
        padre = genitori.get(nodo)
        formato = genitori.get(padre) if isinstance(padre, ast.Attribute) and padre.attr == "format" and padre.value is nodo else None
        if not isinstance(formato, ast.Call) or formato.func is not padre:
            if campi or any("{" in t or "}" in t for t in testi):
                problemi.append(f"{dove}: {nome} con le graffe ma senza format")
            continue
        if formato.args or any(k.arg is None for k in formato.keywords):
            problemi.append(f"{dove}: format vuole solo nomi, come format(durata=...)")
            continue
        passati = {k.arg for k in formato.keywords}
        if passati != campi:
            problemi.append(f"{dove}: segnaposto {sorted(campi)}, ma format riceve {sorted(passati)}")
    vincoli = [n.lineno for n in ast.walk(albero) if (isinstance(n, ast.Name) and n.id == "_" and isinstance(n.ctx, ast.Store))
        or (isinstance(n, ast.arg) and n.arg == "_") or (isinstance(n, ast.ExceptHandler) and n.name == "_")]
    if usa and vincoli:
        problemi.append(f"{file}: il nome _ si usa anche per altro, righe {vincoli}: dentro quelle funzioni non traduce piu'")
    importati = {a.asname or a.name for n in ast.walk(albero) if isinstance(n, ast.ImportFrom) and n.module == "lingua" for a in n.names}
    definiti = {n.name for n in ast.walk(albero) if isinstance(n, ast.FunctionDef)}
    for funzione in ("_", "ngettext", "plurale"):
        chiamata = any(_nome(n) == funzione for n in ast.walk(albero))
        if chiamata and funzione not in importati and not (file == "lingua.py" and funzione in definiti):
            problemi.append(f"{file}: chiama {funzione} senza importarla da lingua")
    return problemi


@pytest.mark.parametrize("file", MODULI)
def test_i_testi_si_possono_tradurre(file):
    assert _problemi(os.path.join(RADICE, file)) == []


def test_il_controllo_trova_gli_errori(tmp_path):
    """Il controllo stesso, su un modulo finto con un errore di ogni tipo."""
    (tmp_path / "finto.py").write_text(
        "from lingua import _, ngettext, plurale\n"
        "a = _(f'Volume {v}')\n"
        "b = _('Volume {volume}').format(livello=3)\n"
        "c = _('Volume {volume}')\n"
        "d = ngettext('{n} brano', '{n} brani', n)\n"
        "e = plurale(n, '{n} brano', '{m} brani')\n"
        "f = _('Volume {volume}').format(volume=3)\n"
        "for _ in range(3): pass\n", encoding="utf-8")
    problemi = _problemi(str(tmp_path / "finto.py"))
    assert len(problemi) == 6
    assert any("non una f-string" in p for p in problemi)
    assert any("format riceve ['livello']" in p for p in problemi)
    assert any("senza format" in p for p in problemi)
    assert any("plurale riempie solo" in p for p in problemi)
    assert any("il nome _ si usa anche per altro" in p for p in problemi)


def test_plurale_e_ngettext_in_italiano():
    assert lingua.plurale(1, "{n} brano", "{n} brani") == "1 brano"
    assert lingua.plurale(0, "{n} brano", "{n} brani") == "0 brani"
    assert lingua.ngettext("Passa {n} brano", "Passano {n} brani", 2).format(n=2) == "Passano 2 brani"
    assert lingua._("Volume") == "Volume"


def test_i_testi_passano_dalla_traduzione(monkeypatch):
    """_ e plurale chiedono alla traduzione di adesso, non a quella
    dell'importazione: e' quello che le prove sostituiscono."""
    monkeypatch.setattr(lingua, "_gettext", lambda testo: f"<{testo}>")
    monkeypatch.setattr(lingua, "_ngettext", lambda s, p, n: f"<{s if n == 1 else p}>")
    assert lingua._("Volume") == "<Volume>"
    assert lingua.plurale(3, "{n} brano", "{n} brani") == "<3 brani>"


def test_le_lingue_sono_quelle_con_il_catalogo(tmp_path, monkeypatch):
    for codice, con_il_mo in (("en", True), ("pl", True), ("fr", False)):
        cartella = tmp_path / "locales" / codice / "LC_MESSAGES"
        cartella.mkdir(parents=True)
        (cartella / ("messages.mo" if con_il_mo else "messages.po")).write_bytes(b"")
    monkeypatch.setattr(percorsi, "percorso_risorsa", lambda nome: str(tmp_path / nome))
    assert lingua.lingue() == ["en", "it", "pl"]
    monkeypatch.setattr(percorsi, "percorso_risorsa", lambda nome: str(tmp_path / "manca" / nome))
    assert lingua.lingue() == ["it"]


def test_il_nome_della_lingua_lo_dice_windows():
    assert lingua.nome("it") == "italiano"
    assert lingua.nome("en") == "English"
    assert lingua.nome("zz-nessuna") == "zz-nessuna"


def test_la_lingua_scelta_vale_dal_riavvio(monkeypatch):
    chiamate = []
    monkeypatch.setattr(lingua, "_polipo", lambda codice=None: chiamate.append(codice))
    monkeypatch.setattr(lingua, "prossima", None)
    lingua.scegli("en")
    assert chiamate == ["en"] and lingua.prossima == "en"
    lingua.scegli(lingua.CODICE)
    assert lingua.prossima is None
