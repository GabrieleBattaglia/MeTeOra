# MeTeOra, l'aggiornamento automatico: il controllo all'avvio con l'auto updater di GBUtils, e le novita' dalla versione di chi aggiorna.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.84.0, condizione di Gabriele per il rilascio.

"""L'aggiornamento automatico di MeTeOra (1.84.0).

Come in Dadillo, Tornello e Terminal Beast lo conduce gestisci_aggiornamento
di GBUtils: controlla l'ultima release su GitHub, e se e' piu' nuova la
propone; se si accetta la scarica, chiude MeTeOra, sostituisce i file e lo
riapre. Solo dall'eseguibile compilato: da sorgente non si fa niente.
Il controllo gira in un filo, all'avvio; la proposta, che nasce li', si
porta nel filo della finestra, l'unico che possa aprirla, e il filo aspetta
la risposta. Le novita' non sono le sole note dell'ultima release: si
scarica il CHANGELOG.md da GitHub e se ne tengono le versioni dopo quella
di chi aggiorna, fino alla nuova, cosi' chi salta delle versioni le legge
tutte (Gabriele, 4 ottobre 2026). Se lo scaricamento non riesce, valgono le
note della release.
"""

import re
import sys
import threading

import version

APP = "MeTeOra"
API = "https://api.github.com/repos/GabrieleBattaglia/MeTeOra/releases/latest"
CHANGELOG = "https://raw.githubusercontent.com/GabrieleBattaglia/MeTeOra/main/CHANGELOG.md"
ATTESA_DEL_CHANGELOG = 10
# La testata di una versione nel CHANGELOG.md: ## [1.84.0] - 2026-10-04.
_TESTATA = re.compile(r"^## \[(\d+(?:\.\d+)*)\](?:\s*-\s*(.+))?$")


def numeri(versione):
    """I numeri di una versione, per confrontarle: (1, 84, 0)."""
    return tuple(int(n) for n in re.findall(r"\d+", versione or ""))


def novita_fra(changelog, da, a):
    """Il testo delle versioni del CHANGELOG.md dopo da e fino ad a compresa,
    nell'ordine del file, dalla piu' nuova. Ogni versione comincia con la
    riga "Versione x del data:", e i punti perdono il trattino, che NVDA
    leggerebbe. Vuoto se nessuna versione sta fra le due."""
    dopo, fino = numeri(da), numeri(a)
    righe, dentro = [], False
    for riga in changelog.splitlines():
        pulita = riga.strip()
        testata = _TESTATA.match(pulita)
        if testata:
            dentro = dopo < numeri(testata.group(1)) <= fino
            if dentro:
                data = f" del {testata.group(2).strip()}" if testata.group(2) else ""
                righe.append(f"Versione {testata.group(1)}{data}:")
            continue
        if pulita.startswith("#"):
            dentro = False
            continue
        if dentro and pulita:
            righe.append(pulita.removeprefix("- "))
    return "\n".join(righe)


def scarica_le_novita(da, a):
    """Le novita' fra le due versioni dal CHANGELOG.md su GitHub, o None se
    non si scarica o non ne ha."""
    try:
        import requests

        risposta = requests.get(CHANGELOG, timeout=ATTESA_DEL_CHANGELOG)
        risposta.raise_for_status()
    except Exception:  # noqa: BLE001 - senza rete valgono le note della release
        return None
    risposta.encoding = "utf-8"
    return novita_fra(risposta.text, da, a) or None


def controlla(finestra, chiama_dopo=None):
    """All'avvio, solo dall'eseguibile compilato: il controllo in un filo.
    finestra fa la proposta (proponi_l_aggiornamento), dice gli esiti
    (avvisa_dell_aggiornamento) e l'avanzamento dello scaricamento
    (avanzamento_dell_aggiornamento), e si chiude per farsi sostituire
    (chiudi_per_aggiornare). chiama_dopo porta una funzione nel filo della
    finestra: wx.CallAfter, se non si dice altro."""
    if not getattr(sys, "frozen", False):
        return None
    try:
        from GBUtils import gestisci_aggiornamento
    except ImportError:
        # Senza GBUtils MeTeOra parte lo stesso, senza controllo.
        return None
    if chiama_dopo is None:
        import wx

        chiama_dopo = wx.CallAfter

    def nella_finestra(funzione, *argomenti):
        """Esegue funzione nel filo della finestra e ne aspetta il valore;
        None se intanto la finestra si e' chiusa."""
        esito, fatto = [], threading.Event()

        def lavoro():
            try:
                if finestra and not finestra.chiusa:
                    esito.append(funzione(*argomenti))
            finally:
                fatto.set()

        chiama_dopo(lavoro)
        fatto.wait()
        return esito[0] if esito else None

    def proponi(versione_attuale, versione_nuova, note, attesa=None):
        novita = scarica_le_novita(versione_attuale, versione_nuova) or note
        return bool(nella_finestra(finestra.proponi_l_aggiornamento, versione_attuale, versione_nuova, novita, attesa))

    def avvisa(testo):
        nella_finestra(finestra.avvisa_dell_aggiornamento, testo)

    def avanzamento(presi, totale):
        chiama_dopo(finestra.avanzamento_dell_aggiornamento, presi, totale)

    def lavoro():
        if gestisci_aggiornamento(APP, version.VERSION, API, proponi=proponi, avvisa=avvisa, avanzamento=avanzamento):
            chiama_dopo(finestra.chiudi_per_aggiornare)

    filo = threading.Thread(target=lavoro, name="MeTeOra, aggiornamento", daemon=True)
    filo.start()
    return filo
