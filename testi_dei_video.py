# MeTeOra, la cartella Testi: i testi del karaoke letti dai video, tenuti per la volta dopo.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 19/11/2026: nasce con la 3.28.0, con la lettura del testo dei video karaoke (issue 51), dalla proposta di Gabriele del 19 novembre 2026.

"""I testi del karaoke che karaoke_dal_video legge da un video, salvati.

Stanno nella cartella Testi, dentro quella delle registrazioni: un file .lrc
per testo e l'indice Testi.json, che lega ogni testo al suo video. Quando il
video torna, il testo diventa la traccia del karaoke, dal video, come un .lrc
accanto al brano, e il riconoscimento resta spento; se l'ascolto di prima si
era fermato o aveva saltato, l'indice sa quali tratti sono letti, e il
riconoscimento si accende solo dove manca qualcosa.
Il video si riconosce cosi':
- su YouTube dal suo identificativo, perche' lo stesso video arriva con
  indirizzi diversi, da una playlist o da una ricerca;
- negli altri siti dall'indirizzo intero;
- sul disco da percorso, dimensione e data: un file sostituito non si prende
  il testo vecchio.
Un testo non ascoltato da GIORNI giorni si toglie con pulisci, all'avvio,
perche' la cartella non cresca per sempre. Mai un errore verso chi chiama:
una cartella che non si scrive vuol dire un testo che non si salva.
"""

import contextlib
import datetime
import hashlib
import json
import os
import re
import threading

import formati
import percorsi

# Dove stanno i testi, dentro la cartella delle registrazioni.
CARTELLA = "Testi"
INDICE = "Testi.json"
# Dopo tanti giorni senza ascolti un testo si toglie (Gabriele).
GIORNI = 365
# Un testo e' completo quando i tratti letti coprono il video fino a tanto
# dalla durata: i primi e gli ultimi secondi di un karaoke non hanno testo.
MARGINE = 10.0
# I file dei testi, per riconoscerli fra gli altri della cartella.
_NOME_DEL_FILE = re.compile(r"^(?:youtube|sito|file)-[\w-]+\.lrc$")
_YOUTUBE = re.compile(r"(?:youtube\.com/(?:watch\?(?:[^#]*&)?v=|shorts/|embed/|live/)|youtu\.be/)([\w-]{11})")

_base = None
_blocco = threading.Lock()


def imposta_la_cartella(base):
    """La cartella delle registrazioni scelta nelle impostazioni, o None per
    quella predefinita: i testi stanno nella sua cartella Testi."""
    global _base
    _base = base or None


def cartella():
    return os.path.join(_base or percorsi.percorso_dati("Registrazioni"), CARTELLA)


def chiave(percorso):
    """Il nome con cui il video sta nella cartella, o None se non si puo' dire,
    come un file che non c'e' piu'."""
    if not percorso:
        return None
    if formati.e_indirizzo(percorso):
        youtube = _YOUTUBE.search(percorso)
        if youtube:
            return f"youtube-{youtube.group(1)}"
        return "sito-" + hashlib.sha1(percorso.split("#")[0].encode("utf-8"), usedforsecurity=False).hexdigest()[:20]
    try:
        stato = os.stat(percorso)
    except OSError:
        return None
    impronta = f"{os.path.normcase(os.path.abspath(percorso))}|{stato.st_size}|{stato.st_mtime_ns}"
    return "file-" + hashlib.sha1(impronta.encode("utf-8"), usedforsecurity=False).hexdigest()[:20]


def _oggi():
    return datetime.date.today().isoformat()


def _leggi_l_indice():
    try:
        with open(os.path.join(cartella(), INDICE), encoding="utf-8") as f:
            dati = json.load(f)
    except (OSError, ValueError):
        return {}
    testi = dati.get("testi") if isinstance(dati, dict) else None
    return testi if isinstance(testi, dict) else {}


def _scrivi(nome, testo):
    """Un file della cartella scritto per intero o per niente."""
    os.makedirs(cartella(), exist_ok=True)
    percorso = os.path.join(cartella(), nome)
    provvisorio = percorso + ".nuovo"
    with open(provvisorio, "w", encoding="utf-8", newline="\n") as f:
        f.write(testo)
    os.replace(provvisorio, percorso)


def _scrivi_l_indice(testi):
    _scrivi(INDICE, json.dumps({"versione": 1, "testi": testi}, ensure_ascii=False, indent=1))


def unisci(tratti):
    """I tratti (inizio, fine) uniti dove si toccano, in ordine."""
    uniti = []
    for inizio, fine in sorted((float(a), float(b)) for a, b in tratti if b >= a):
        if uniti and inizio <= uniti[-1][1] + 0.5:
            uniti[-1][1] = max(uniti[-1][1], fine)
        else:
            uniti.append([inizio, fine])
    return [tuple(t) for t in uniti]


def coperto(tratti, istante):
    """Vero se l'istante sta in uno dei tratti gia' letti."""
    return any(inizio <= istante <= fine for inizio, fine in tratti)


def voce(percorso):
    """Quello che l'indice sa del video: un dizionario con coperti, durata,
    righe, archivio e completo; None se il video non ha un testo salvato."""
    nome = chiave(percorso)
    if nome is None:
        return None
    with _blocco:
        dati = _leggi_l_indice().get(nome)
    if not isinstance(dati, dict) or not os.path.isfile(os.path.join(cartella(), nome + ".lrc")):
        return None
    tratti = unisci(dati.get("coperti") or [])
    durata = float(dati.get("durata") or 0)
    return {"coperti": tratti, "durata": durata, "righe": int(dati.get("righe") or 0), "archivio": dati.get("archivio") or "",
            "completo": _completo(tratti, durata)}


def _completo(tratti, durata):
    """Vero se i tratti letti coprono il video fino a MARGINE dalla durata."""
    return durata > 0 and sum(fine - inizio for inizio, fine in unisci(tratti)) >= durata - MARGINE


def righe(percorso):
    """Le righe del testo salvato del video, come karaoke.dal_lrc, o []; e il
    video conta come ascoltato oggi, per la pulizia."""
    import karaoke

    nome = chiave(percorso)
    if nome is None:
        return []
    file_del_testo = os.path.join(cartella(), nome + ".lrc")
    try:
        with open(file_del_testo, encoding="utf-8") as f:
            testo = f.read()
    except OSError:
        return []
    ascoltato(percorso)
    return karaoke.dal_lrc(testo)


def ascoltato(percorso):
    """Il video conta come ascoltato oggi: la pulizia lo lascia stare."""
    nome = chiave(percorso)
    if nome is None:
        return
    with _blocco:
        testi = _leggi_l_indice()
        if nome in testi and testi[nome].get("ascoltato") != _oggi():
            testi[nome]["ascoltato"] = _oggi()
            with contextlib.suppress(OSError):
                _scrivi_l_indice(testi)


def _gruppi_del_file(testo):
    """I gruppi (istante, [righe]) di un .lrc scritto da qui: le righe con lo
    stesso istante, comparse insieme sullo schermo, stanno insieme."""
    gruppi = {}
    for riga in testo.splitlines():
        trovato = re.match(r"\[(\d{1,3}):(\d{2})\.(\d{2})\](.*)", riga)
        if trovato and trovato.group(4).strip():
            istante = int(trovato.group(1)) * 60 + int(trovato.group(2)) + int(trovato.group(3)) / 100
            gruppi.setdefault(round(istante, 2), []).append(trovato.group(4).strip())
    return sorted(gruppi.items())


def _orario(istante):
    centesimi = round(istante * 100)
    return f"[{centesimi // 6000:02d}:{centesimi // 100 % 60:02d}.{centesimi % 100:02d}]"


def testo_lrc(titolo, gruppi):
    """Il .lrc dei gruppi (istante, [righe]): una riga vuota fra un gruppo e
    l'altro, che karaoke.dal_lrc legge come l'inizio di una strofa."""
    pezzi = [f"[ti:{' '.join(titolo.split())}]", "[re:MeTeOra]"]
    for istante, testi in gruppi:
        pezzi.append("")
        pezzi.extend(_orario(istante) + " ".join(t.split()) for t in testi if t.strip())
    return "\n".join(pezzi) + "\n"


def salva(percorso, titolo, durata, gruppi, tratti, archivio=""):
    """Aggiunge al testo del video i gruppi (istante, [righe]) letti e i tratti
    (inizio, fine) coperti, a quello che c'era. archivio e' il testo
    dell'archivio usato, come Adele - Hello, o vuoto. Torna, per le
    statistiche, {"righe": quante ne ha ora il testo, "nuovo": vero se prima
    non c'era, "completato": vero se e' diventato completo adesso}; None se
    non si e' potuto salvare."""
    nome = chiave(percorso)
    if nome is None or not (gruppi or tratti):
        return None
    file_del_testo = os.path.join(cartella(), nome + ".lrc")
    with _blocco:
        testi = _leggi_l_indice()
        prima = testi.get(nome) if isinstance(testi.get(nome), dict) else {}
        try:
            with open(file_del_testo, encoding="utf-8") as f:
                vecchi = _gruppi_del_file(f.read())
        except OSError:
            vecchi, prima = [], {}
        tutti = {istante: list(righe_del_gruppo) for istante, righe_del_gruppo in vecchi}
        for istante, righe_del_gruppo in gruppi:
            istante = round(float(istante), 2)
            # Lo stesso gruppo gia' salvato, a un passo di distanza, non si ripete.
            if any(abs(istante - altro) < 0.5 and tutti[altro] == list(righe_del_gruppo) for altro in tutti):
                continue
            tutti.setdefault(istante, []).extend(righe_del_gruppo)
        ordinati = sorted(tutti.items())
        quante = sum(len(r) for _istante, r in ordinati)
        durata_vera = round(float(durata or prima.get("durata") or 0), 1)
        coperti_prima = prima.get("coperti") or []
        coperti = unisci([*coperti_prima, *tratti])
        testi[nome] = {"origine": percorso, "titolo": titolo, "durata": durata_vera, "coperti": [[round(a, 1), round(b, 1)] for a, b in coperti],
            "archivio": archivio or prima.get("archivio") or "", "creato": prima.get("creato") or _oggi(), "ascoltato": _oggi(), "righe": quante}
        try:
            _scrivi(nome + ".lrc", testo_lrc(titolo, ordinati))
            _scrivi_l_indice(testi)
        except OSError:
            return None
    return {"righe": quante, "nuovo": not prima, "completato": _completo(coperti, durata_vera) and not _completo(coperti_prima, durata_vera)}


def pulisci(oggi=None):
    """Toglie i testi non ascoltati da GIORNI giorni, e i file della cartella
    che l'indice non conosce piu'. Torna quanti testi ha tolto."""
    oggi = oggi or datetime.date.today()
    limite = (oggi - datetime.timedelta(days=GIORNI)).isoformat()
    tolti = 0
    with _blocco:
        testi = _leggi_l_indice()
        vecchi = [nome for nome, dati in testi.items() if not isinstance(dati, dict) or (dati.get("ascoltato") or "") < limite]
        for nome in vecchi:
            del testi[nome]
        try:
            presenti = os.listdir(cartella())
        except OSError:
            return 0
        for file_del_testo in presenti:
            if _NOME_DEL_FILE.match(file_del_testo) and file_del_testo[:-4] not in testi:
                try:
                    os.remove(os.path.join(cartella(), file_del_testo))
                    tolti += 1
                except OSError:
                    pass
        if vecchi:
            with contextlib.suppress(OSError):
                _scrivi_l_indice(testi)
    return tolti
