# MeTeOra, il banco del collaudo: MeTeOra vero su un desktop di Windows nascosto, con una copia dei dati, pilotato da una tastiera simulata.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 19/10/2026: nasce con la 1.104.0, dal banco con cui ClaudIA ha collaudato le statistiche della 1.103; sul desktop nascosto, come preferisce Gabriele. Nella 1.105.0 la sessione di Dove sono, l'opzione --solo, la sintesi finta e la pipe dell'istanza con il numero del processo. Nella 1.109.0 la sessione ordina, con --ordina. Nella 1.110.0 la sessione della durata residua, e al_normale in comune con Dove sono.

"""Il banco del collaudo.

Uso, dalla cartella di MeTeOra:
  python strumenti\\banco.py             tutte le sessioni, su una copia dei dati di questa cartella
  python strumenti\\banco.py --vuoti     tutte le sessioni, partendo senza dati
  python strumenti\\banco.py --video V   in piu' Maiuscolo con F7 con la finestra del video V davanti
  python strumenti\\banco.py --solo S    la sola sessione S, per quelle che non dipendono dalle altre,
                                        come dove_sono e durata_residua
  python strumenti\\banco.py --ordina    solo la sessione ordina, partendo senza dati

Con --video la finestra del video di MeTeOra si apre e prende i tasti, ma
libmpv, che disegna in un suo filo nato sul desktop di partenza, li' non puo'
creare la sua finestra e resta senza immagine: il banco prova la finestra di
MeTeOra, non il disegno del video.

Ogni sessione e' un processo a parte che apre MeTeOra come meteora.py, ma con
i dati in una cartella temporanea e su un desktop di Windows nascosto: lo
schermo non cambia, NVDA non legge, i suoni si annotano senza suonare, il
motore suona sull'uscita nulla e la sintesi dei sottotitoli annota soltanto,
senza mai arrivare a NVDA. Un filo pilota preme i tasti con
tastiera_simulata e guarda cosa succede dentro la finestra. Le sessioni:
- principale: la pulizia all'avvio, la voce Statistiche, Maiuscolo con F7 da
  plancia, console, cruscotto e dal video, la ricerca nelle statistiche, Invio,
  Esc e Chiudi, l'azzeramento, F12 e F1, tre brani suonati e i loro conti;
  alla fine prepara un file che il banco poi cancella, ed esce con Esc;
- riavvio: i conti dopo il riavvio, la copia delle statistiche, la pulizia
  del file cancellato; poi il banco la chiude a forza, come il Task Manager,
  nel primo minuto;
- dopo_il_crash: la chiusura non regolare contata, senza l'errore grave; resta
  aperta oltre il minuto, per il salvataggio e lo svuotamento del file del
  crash, ed esce con Esc;
- controllo: le chiusure regolari e gli avvii contati;
- dove_sono: l'apostrofo, il tasto vero della tastiera italiana, con niente
  in corso e con due file che suonano, dalla plancia e dalla console, in
  pausa e a velocita' cambiata, con Maiuscolo; il fuoco che resta dov'e' e la
  riga che va alla sintesi e al braille, dove si riscrive subito anche lei;
  ripetizione, casuale, velocita', tono e sintesi partono da quelli normali,
  qualunque cosa dica la copia dei dati;
- durata_residua: Maiuscolo con l'apostrofo, il tasto vero, anche come punto
  interrogativo, con niente in corso e con due playlist di file veri aperte
  nella plancia, con le durate lette dallo schedario: il conto che segue i
  rami aperti e chiusi, la pausa, la velocita', un brano senza durata che lo
  schedario rilegge, la lista che decide, le ripetizioni, il nome nelle
  statistiche, il tempo del conto con tremila voci aperte, e le voci sopra
  la lista che suona, che non contano.
La sessione ordina (tappa 14 c) gira solo con --ordina: Ordina, Inverti
l'ordine, Mescola e Ordine di prima su una playlist aperta di cinquemila
brani, con i tempi, e Mescola sulla playlist che suona con la dissolvenza
accesa, quando il brano seguente e' gia' preparato.
Alla fine un riassunto, una riga per ogni controllo non riuscito; l'uscita
vale 1 se ce n'e' almeno uno. La cartella di prova resta solo in quel caso.
"""

import argparse
import contextlib
import ctypes
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import wave
from ctypes import wintypes

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISTANZA = "meteora_banco"
FILE_DELLE_STATISTICHE = "MeTeOra - Statistiche.json"
SESSIONI = ("principale", "riavvio", "dopo_il_crash", "controllo", "dove_sono", "durata_residua")
# Le sessioni che girano solo quando si chiedono (tappa 14 c).
SESSIONI_A_PARTE = ("ordina",)
# Quanto puo' durare ogni sessione, in secondi: la pulizia sulla copia dei
# dati veri guarda anche la rete.
DURATE_MASSIME = {"principale": 1200, "riavvio": 900, "dopo_il_crash": 1200, "controllo": 900, "dove_sono": 900, "durata_residua": 900, "ordina": 600}
# I brani della playlist grande della sessione ordina, e quanto puo' durare al
# massimo ogni riordino, in secondi.
BRANI_DELLA_PLAYLIST_GRANDE = 5000
DURATA_DEL_RIORDINO = 5.0
# Quanto aspettare la fine della pulizia all'avvio, in secondi.
ATTESA_DELLA_PULIZIA = 900

S = None


# La sessione: annota suoni, righe della console e controlli.


class Sessione:
    def __init__(self, nome, dati, esito, video):
        self.nome, self.dati, self.esito, self.video = nome, dati, esito, video
        self.inizio = time.monotonic()
        self.risultati, self.suonati, self.console, self.aperti, self.aperture = [], [], [], [], []
        self.extra = {}
        self.finestra = None
        self.crash_precedente = None
        self.svuotamenti = []
        self._registro = open(esito + ".log", "w", encoding="utf-8", buffering=1)  # noqa: SIM115 - resta aperto per tutta la sessione

    def nota(self, *parti):
        riga = f"{time.monotonic() - self.inizio:8.2f} " + " ".join(str(p) for p in parti)
        self._registro.write(riga[:2000] + "\n")

    def verifica(self, voce, cosa, esito, dettaglio=""):
        self.risultati.append({"voce": str(voce), "cosa": cosa, "esito": bool(esito), "dettaglio": str(dettaglio)[:600]})
        self.nota("OK " if esito else "NO ", f"[{voce}]", cosa, "|", str(dettaglio)[:600])
        self.salva()
        return bool(esito)

    def salva(self):
        with open(self.esito + ".json", "w", encoding="utf-8") as f:
            json.dump({"sessione": self.nome, "risultati": self.risultati, "aperture": self.aperture, "extra": self.extra}, f, ensure_ascii=False, indent=1)

    def suoni_da(self, segno):
        return [e for t, e in self.suonati if t >= segno]

    def console_da(self, segno):
        return [testo for t, testo in self.console if t >= segno]


def _desktop_nascosto():
    """Come tests/conftest.py: il filo della finestra passa a un desktop
    nascosto prima che wx crei una finestra qualsiasi."""
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.CreateDesktopW.restype = wintypes.HANDLE
    user32.CreateDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
    user32.SetThreadDesktop.restype = wintypes.BOOL
    user32.SetThreadDesktop.argtypes = [wintypes.HANDLE]
    desktop = user32.CreateDesktopW(f"meteora_banco_{os.getpid()}", None, None, 0, 0x10000000, None)
    if not desktop or not user32.SetThreadDesktop(desktop):
        raise SystemExit(f"Il desktop nascosto non si crea: errore {ctypes.get_last_error()}.")
    return desktop


def _prepara_i_moduli():
    """Suoni annotati e muti; il browser e os.startfile annotati; niente
    controllo degli aggiornamenti."""
    import aggiornamento
    import suoni

    def annota(evento, volume=0.5, sync=False):
        S.suonati.append((time.monotonic(), evento))
        S.nota("suono", evento)
        return True

    suoni.suona = annota
    suoni.livello = lambda profondita, volume=0.5: True
    suoni.banda = lambda indice, volume=0.5: True
    suoni.guadagno = lambda db, volume=0.5: True
    os.startfile = lambda *argomenti, **opzioni: S.aperti.append(argomenti)
    import webbrowser

    webbrowser.open = lambda *argomenti, **opzioni: S.nota("browser", argomenti)
    aggiornamento.controlla = lambda *argomenti, **opzioni: None
    # La sintesi dei sottotitoli, e di Dove sono, annota soltanto: quella
    # vera parlerebbe con NVDA anche dal desktop nascosto. NVDA e' attivo,
    # cosi' l'automatica sceglie lui, come sul PC di Gabriele.
    import sintesi

    class SintesiFinta:
        def __init__(self, chiave):
            self.chiave = chiave

        def is_active(self):
            return self.chiave == "nvda"

        def speak(self, testo, interrupt=False):
            S.extra.setdefault("detti", []).append([self.chiave, testo])
            if interrupt:
                # Anche i testi che interrompono la voce, come Dove sono.
                S.extra.setdefault("interrotti", []).append([self.chiave, testo])
            S.nota("sintesi che interrompe" if interrupt else "sintesi", self.chiave, testo)

        def braille(self, testo):
            S.extra.setdefault("braille", []).append([self.chiave, testo])
            S.nota("braille", self.chiave, testo)

    sintesi._crea = SintesiFinta


def _apri_meteora():
    """Quello che fa meteora.main, con i dati nella cartella di prova."""
    import wx

    _prepara_i_moduli()
    import copie
    import istanza
    import registro
    import suoni
    import version

    app = wx.App(False)
    S.crash_precedente = registro.avvia(S.dati)
    registro.scrivi(f"MeTeOra {version.VERSION} si avvia (banco).")
    sopravvissuto = registro.sopravvissuto

    def svuota():
        quante = sopravvissuto()
        S.svuotamenti.append((time.monotonic(), quante))
        return quante

    registro.sopravvissuto = svuota
    import librerie  # noqa: F401
    from finestra import FILE_IMPOSTAZIONI, FILE_MARCATORI, FILE_PLAYLIST, FILE_POSIZIONI, FILE_STATISTICHE, Finestra

    scrivi_di_prima = Finestra.scrivi

    def scrivi(self, testo, *argomenti, **opzioni):
        S.console.append((time.monotonic(), testo))
        S.nota("console:", testo)
        return scrivi_di_prima(self, testo, *argomenti, **opzioni)

    Finestra.scrivi = scrivi
    # Il tempo dentro MeTeOra, dal comando delle statistiche alla finestra
    # aperta: senza l'attesa della tastiera simulata.
    from dialoghi import FinestraStatistiche

    comando_di_prima, mostra_di_prima = Finestra._comando_statistiche, FinestraStatistiche.ShowModal

    def comando(self):
        S.extra.setdefault("comandi", []).append(time.monotonic())
        return comando_di_prima(self)

    def mostra(self):
        S.extra.setdefault("mostrate", []).append(time.monotonic())
        return mostra_di_prima(self)

    Finestra._comando_statistiche = comando
    FinestraStatistiche.ShowModal = mostra
    mancate = copie.ruota(S.dati, [FILE_PLAYLIST, FILE_MARCATORI, FILE_IMPOSTAZIONI, FILE_POSIZIONI, FILE_STATISTICHE])
    f = S.finestra = Finestra(ao="null", cartella_dati=S.dati)
    f.ascolta_i_problemi()
    if mancate:
        f.copie_mancate(mancate)
    if S.crash_precedente:
        f.crash_precedente(S.crash_precedente)
    f.Maximize()
    f.Show()
    f.Layout()
    f.albero.SetFocus()
    suoni.suona("avvio", f.impostazioni["volume_effetti"])
    f.riprendi()
    f.ascolto_delle_copie = istanza.Ascolto(lambda percorsi: wx.CallAfter(f.apri_dall_esterno, percorsi, "copia"))
    f.dopo_l_avvio()
    # Il salvataggio subito, prima di ogni altro: quello della fine della
    # pulizia e quello del minuto passano dal ciclo di wx, che non gira ancora.
    if f._statistiche._scrittura is not None:
        f._statistiche._scrittura.join(10)
    with contextlib.suppress(OSError, ValueError), open(os.path.join(S.dati, FILE_STATISTICHE), encoding="utf-8") as fl:
        su_disco = json.load(fl)
        S.extra["subito"] = {"sessione_aperta": su_disco.get("sessione_aperta"), "avvii": su_disco.get("conti", {}).get("avvii")}
    return app, registro


def sessione(nome, dati, esito, video, vuoti=False):
    global S
    _desktop_nascosto()
    # La pipe dell'istanza unica ha il numero del processo: due banchi
    # insieme, per esempio da due copie di lavoro, con lo stesso nome se la
    # contenderebbero, e i file di uno arriverebbero all'altro.
    os.environ["METEORA_ISTANZA"] = f"{ISTANZA}_{os.getpid()}"
    sys.path.insert(0, RADICE)
    os.chdir(RADICE)
    S = Sessione(nome, dati, esito, video)
    S.extra["vuoti"] = vuoti
    app, registro = _apri_meteora()
    S.nota("MeTeOra aperto sul desktop nascosto, pid", os.getpid())
    threading.Thread(target=_pilota, args=(SCENARI[nome],), name="banco, pilota", daemon=True).start()
    app.MainLoop()
    registro.scrivi("MeTeOra si chiude (banco).")
    registro.chiudi()
    S.nota("MeTeOra chiuso")
    S.salva()


def _pilota(scenario):
    import wx

    try:
        scenario()
    except BaseException as e:  # noqa: BLE001 - lo scenario interrotto e' un controllo non riuscito
        S.nota("SCENARIO INTERROTTO:", traceback.format_exc())
        S.verifica("banco", "Lo scenario arriva in fondo", False, repr(e))
        with contextlib.suppress(Exception):
            wx.CallAfter(lambda: S.finestra.Close(force=True))
    finally:
        S.salva()


# Gli aiuti del pilota.


def _tastiera():
    import tastiera_simulata

    return tastiera_simulata


def premi(tasto, **opzioni):
    S.nota("premo", tasto, opzioni or "")
    _tastiera().premi(tasto, **opzioni)


def scrivi(testo):
    S.nota("scrivo", repr(testo))
    _tastiera().scrivi(testo)


def nel_filo(funzione, *argomenti, attesa=30.0):
    return _tastiera().nel_filo(funzione, *argomenti, attesa=attesa)


def aspetta(condizione, attesa=10.0, passo=0.05):
    return _tastiera().aspetta(condizione, attesa=attesa, passo=passo)


def _aperte(nome_della_classe):
    import wx

    return [w for w in wx.GetTopLevelWindows() if type(w).__name__ == nome_della_classe and w.IsShown()]


def statistiche():
    return _aperte("FinestraStatistiche")


def campi():
    return _aperte("FinestraFiltro")


def domande():
    return _aperte("DialogoConferma")


def fuoco():
    import wx

    w = wx.Window.FindFocus()
    if w is None:
        return "nessuno"
    alto = w.GetTopLevelParent()
    etichetta = w.GetLabel() if isinstance(w, wx.Button) else ""
    return f"{type(w).__name__} '{w.GetName()}' '{etichetta}' in '{alto.GetTitle() if alto else ''}'"


def riga_del_cursore():
    """Il numero e il testo della riga del cursore, nelle statistiche."""
    d = statistiche()[0]
    indice = d._dal_controllo(d.testo.GetInsertionPoint())
    numero = d.valore.count("\n", 0, indice)
    return numero, d.valore.split("\n")[numero]


def conti():
    """Una copia dei dati delle statistiche, presa nel filo della finestra:
    l'orologio li cambia ogni secondo."""
    import copy

    return nel_filo(lambda: copy.deepcopy(S.finestra._statistiche.dati))


def apri_le_statistiche(voce, da, tasto=("f7", {"maiuscolo": True}), salva_come=None):
    """Preme il tasto, misura quanto ci vuole e quanto la finestra resta ferma
    nel frattempo. Torna il segno del tempo di prima del tasto."""
    segno = time.monotonic()
    premi(tasto[0], **tasto[1])
    inizio = time.monotonic()
    piu_lenta, aperta = 0.0, False
    while time.monotonic() - inizio < 120:
        t = time.monotonic()
        aperta = nel_filo(lambda: bool(statistiche()))
        piu_lenta = max(piu_lenta, time.monotonic() - t)
        if aperta:
            break
        time.sleep(0.02)
    # Dal tasto: premi torna quando il ciclo di wx l'ha finito, e la finestra
    # puo' essere gia' aperta.
    durata = time.monotonic() - segno
    comandi = [t for t in S.extra.get("comandi", []) if t >= segno]
    mostrate = [t for t in S.extra.get("mostrate", []) if t >= segno]
    dentro = round(mostrate[0] - comandi[0], 2) if comandi and mostrate else None
    S.aperture.append({"voce": voce, "da": da, "secondi": round(durata, 2), "dentro": dentro, "risposta_piu_lenta": round(piu_lenta, 3)})
    S.verifica(voce, f"Statistiche aperte, {da}", aperta, f"in {durata:.2f} s dal tasto, {dentro} s dentro MeTeOra; la finestra ha risposto al piu' in "
        f"{piu_lenta * 1000:.0f} ms")
    if aperta and salva_come:
        with open(f"{S.esito}_{salva_come}.txt", "w", encoding="utf-8") as f:
            f.write(nel_filo(lambda: statistiche()[0].valore))
    return segno


def chiudi_le_statistiche(voce, come="Esc"):
    if come == "Esc":
        premi("esc")
    chiusa = aspetta(lambda: not statistiche(), attesa=5)
    S.verifica(voce, f"Statistiche chiuse con {come}", chiusa)


def riga_della_pagina(testo, comincia):
    return next((r for r in testo.split("\n") if r.startswith(comincia)), "")


def aspetta_la_pulizia():
    """La fine della pulizia all'avvio, se e' partita: torna le righe della
    console che la riguardano."""
    f = S.finestra
    aspetta(lambda: f.IsShown(), attesa=30)
    partita = aspetta(lambda: any(t.startswith("Pulizia all'avvio") for _t, t in S.console), attesa=10)
    finita = aspetta(lambda: f._pulizia is None and any(t.startswith(("Pulizia finita", "La pulizia all'avvio non")) for _t, t in S.console),
        attesa=ATTESA_DELLA_PULIZIA, passo=0.5) if partita else True
    righe = [t for _t, t in S.console if t.startswith(("Pulizia", "La pulizia"))]
    if partita:
        S.verifica("pulizia", "La pulizia all'avvio finisce, con i suoi due suoni", finita and S.suoni_da(0).count("pulizia_avviata") == 1
            and S.suoni_da(0).count("pulizia_finita") == 1 and S.suoni_da(0).index("pulizia_avviata") < S.suoni_da(0).index("pulizia_finita"), righe)
    return righe


def fai_un_wav(percorso, secondi):
    if not os.path.isfile(percorso):
        with wave.open(percorso, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(22050)
            w.writeframes(bytes(2 * 22050 * secondi))
    return percorso


def _cartella_dei_brani():
    cartella = os.path.join(S.dati, "brani di prova")
    os.makedirs(cartella, exist_ok=True)
    return cartella


def _da_un_altra_sessione(nome):
    percorso = os.path.join(os.path.dirname(S.esito), f"{nome}.json")
    with open(percorso, encoding="utf-8") as f:
        return json.load(f)


def al_normale():
    """Nel filo della finestra. La copia dei dati di questa cartella puo'
    avere la ripetizione, la riproduzione casuale, la velocita', il tono, la
    sintesi o la barra dei sottotitoli cambiati: allungherebbero le righe di
    Dove sono e della durata residua, o le toglierebbero alla sintesi e al
    braille, mentre i controlli aspettano quelli di partenza, come con
    --vuoti."""
    f = S.finestra
    f.impostazioni.update(ripetizione="spenta", casuale=False, velocita=1.0, tono=0, sintesi="automatica", destinazione="entrambi", celle_braille=0)
    f._applica_la_riproduzione()
    f.motore.muto = False


# Gli scenari.


def scenario_principale():
    import istanza
    from finestra import ISTRUZIONI_DELLE_STATISTICHE

    f = S.finestra
    righe = aspetta_la_pulizia()
    S.extra["pulizia"] = righe
    albero = f.albero

    # La voce nella plancia, Invio e il fuoco.
    def radice():
        voce, biscotto = albero.GetFirstChild(albero.GetRootItem())
        nomi = []
        while voce.IsOk():
            nomi.append(albero.GetItemText(voce))
            voce, biscotto = albero.GetNextChild(albero.GetRootItem(), biscotto)
        return nomi

    nomi = nel_filo(radice)
    i = nomi.index("Statistiche") if "Statistiche" in nomi else -1
    S.verifica(2, "Statistiche fra Apri file e Impostazioni, al primo livello", 0 < i < len(nomi) - 1 and nomi[i - 1] == "Apri file" and nomi[i + 1] == "Impostazioni", nomi)
    premi("f5")
    premi("fine")
    premi("su")
    voce = nel_filo(lambda: albero.GetItemText(albero.GetFocusedItem()))
    S.verifica(2, "Fine e freccia su portano a Statistiche", voce == "Statistiche", voce)
    segno = apri_le_statistiche(2, "con Invio sulla voce della plancia, con lo schedario intero", tasto=("invio", {}), salva_come="testo")
    S.verifica(2, "Il suono dell'apertura", "statistiche" in S.suoni_da(segno), S.suoni_da(segno))
    dove, (numero, riga) = nel_filo(fuoco), nel_filo(riga_del_cursore)
    S.verifica(2, "Il fuoco nel testo, alla prima riga", "TextCtrl 'Statistiche'" in dove and numero == 0, f"{dove}; riga {numero}: {riga}")
    titolo = nel_filo(lambda: statistiche()[0].GetTitle())
    S.verifica(2, "Il titolo della finestra", titolo == "Statistiche di MeTeOra", titolo)
    premi("invio")
    S.verifica(9, "Senza una ricerca Invio chiude", aspetta(lambda: not statistiche(), attesa=5))
    S.verifica(9, "Il fuoco torna alla plancia", "Plancia dei comandi" in nel_filo(fuoco), nel_filo(fuoco))

    # Maiuscolo con F7 da plancia, console e cruscotto, e due volte di fila.
    for tasto, area in (("f5", "dalla plancia"), ("f6", "dalla console"), ("f7", "dal cruscotto")):
        premi(tasto)
        apri_le_statistiche(3, f"con Maiuscolo e F7 {area}")
        S.verifica(3, f"Una finestra sola, {area}", nel_filo(lambda: len(statistiche())) == 1)
        chiudi_le_statistiche(3)
    premi("f5")
    segno = time.monotonic()
    premi("f7", maiuscolo=True)
    premi("f7", maiuscolo=True)
    aspetta(lambda: bool(statistiche()), attesa=60)
    time.sleep(2)
    S.verifica(3, "Maiuscolo e F7 due volte di fila: una finestra sola", nel_filo(lambda: len(statistiche())) == 1)
    chiudi_le_statistiche(3)
    time.sleep(2)
    S.verifica(3, "Chiusa quella, non se ne apre un'altra", nel_filo(lambda: len(statistiche())) == 0)
    S.verifica(3, "Il suono dell'apertura una volta sola", S.suoni_da(segno).count("statistiche") == 1, S.suoni_da(segno))

    # La ricerca.
    apri_le_statistiche(7, "per la ricerca")
    segno = time.monotonic()
    premi("\\")
    S.verifica(7, "La barra rovesciata apre il campo Cerca", aspetta(lambda: bool(campi()), attesa=5))
    titolo, valore = nel_filo(lambda: (campi()[0].GetTitle(), campi()[0].campo.GetValue()))
    S.verifica(7, "Il campo e le sue istruzioni", titolo == "Cerca nelle statistiche" and all(r in valore for r in ISTRUZIONI_DELLE_STATISTICHE), titolo)
    S.verifica(7, "Il fuoco nel campo, con il suono della domanda", "Cerca nelle statistiche" in nel_filo(fuoco) and "domanda" in S.suoni_da(segno), nel_filo(fuoco))
    segno = time.monotonic()
    scrivi("Sezione 8")
    premi("invio")
    aspetta(lambda: not campi(), attesa=5)
    numero, riga = nel_filo(riga_del_cursore)
    S.verifica(7, "Il cursore sulla riga della sezione 8, con il suono del trovato", riga.startswith("Sezione 8 di") and S.suoni_da(segno) == ["trovato_nelle_statistiche"],
        f"riga {numero}: {riga}; {S.suoni_da(segno)}")
    S.verifica(7, "Il fuoco torna nel testo", "TextCtrl 'Statistiche'" in nel_filo(fuoco), nel_filo(fuoco))
    premi("\\")
    aspetta(lambda: bool(campi()), attesa=5)
    S.verifica(8, "Il campo ripropone la ricerca di prima", nel_filo(lambda: campi()[0].testo).strip() == "Sezione 8")
    scrivi("Sezione")
    premi("invio")
    aspetta(lambda: not campi(), attesa=5)

    def occorrenze():
        d = statistiche()[0]
        return [m.start() for m in d._modello.finditer(d.valore)]

    def dove_sta():
        d = statistiche()[0]
        return d._dal_controllo(d.testo.GetInsertionPoint())

    attese, viste, suoni_visti = nel_filo(occorrenze), [nel_filo(dove_sta)], []
    for _ in attese:
        segno = time.monotonic()
        premi("invio")
        viste.append(nel_filo(dove_sta))
        suoni_visti.append(S.suoni_da(segno))
    S.verifica(8, f"Invio passa alle {len(attese)} occorrenze in ordine, e in fondo riparte dalla prima", viste == attese + attese[:1], viste[-3:])
    S.verifica(8, "Trovato a ogni passo, ripartito alla fine", all(s == ["trovato_nelle_statistiche"] for s in suoni_visti[:-1])
        and suoni_visti[-1] == ["ripartito_nelle_statistiche"], suoni_visti[-2:])
    S.verifica(9, "Dopo una ricerca Invio non chiude", nel_filo(lambda: bool(statistiche())))
    segno = time.monotonic()
    premi("\\")
    aspetta(lambda: bool(campi()), attesa=5)
    scrivi("parola che non c'e")
    premi("invio")
    aspetta(lambda: not campi(), attesa=5)
    S.verifica(8, "Il testo che non c'e' lo dice la console, con il suo suono", "Nelle statistiche non c'è parola che non c'e." in S.console_da(segno)
        and "non_trovato_nelle_statistiche" in S.suoni_da(segno), S.console_da(segno))
    segno = time.monotonic()
    premi("\\")
    aspetta(lambda: bool(campi()), attesa=5)
    premi("esc")
    S.verifica(8, "Esc nel campo annulla la ricerca", aspetta(lambda: not campi(), attesa=5) and "Ricerca nelle statistiche annullata." in S.console_da(segno))
    chiudi_le_statistiche(9, "Esc")
    for come, tasti in (("il pulsante Chiudi", (("tab", {}), ("tab", {}), ("invio", {}))), ("Alt e C", (("c", {"alt": True}),))):
        apri_le_statistiche(9, f"per chiudere con {come}")
        premi("\\")
        aspetta(lambda: bool(campi()), attesa=5)
        scrivi("Sezione 3")
        premi("invio")
        aspetta(lambda: not campi(), attesa=5)
        for tasto, opzioni in tasti[:-1]:
            premi(tasto, **opzioni)
        if come == "il pulsante Chiudi":
            S.verifica(9, "Con due Tab il fuoco va su Chiudi", "Chiudi" in nel_filo(fuoco), nel_filo(fuoco))
        premi(tasti[-1][0], **tasti[-1][1])
        chiudi_le_statistiche(9, come)

    # L'azzeramento.
    apri_le_statistiche(10, "per l'azzeramento")
    prima = conti()
    for risposta in ("n", "esc"):
        segno = time.monotonic()
        premi("a", alt=True)
        if not S.verifica(10, "Alt e A apre la domanda", aspetta(lambda: bool(domande()), attesa=5)):
            continue
        predefinito = nel_filo(lambda: domande()[0].GetDefaultItem().GetLabel())
        S.verifica(10, "No predefinito, con il fuoco", "No" in predefinito and "No" in nel_filo(fuoco), f"{predefinito}; {nel_filo(fuoco)}")
        premi(risposta)
        aspetta(lambda: not domande(), attesa=5)
        dopo = conti()
        S.verifica(10, f"Con {risposta} non cambia niente, e la console lo dice", dopo["azzeramenti"] == prima["azzeramenti"]
            and dopo["conti"].get("avvii") == prima["conti"].get("avvii") and "Le statistiche restano come sono." in S.console_da(segno), S.console_da(segno))
    premi("fine", ctrl=True)
    valore_prima = nel_filo(lambda: statistiche()[0].valore)
    segno = time.monotonic()
    premi("a", alt=True)
    aspetta(lambda: bool(domande()), attesa=5)
    premi("s")
    aspetta(lambda: not domande(), attesa=5)
    dopo = conti()
    valore, posizione = nel_filo(lambda: (statistiche()[0].valore, statistiche()[0].testo.GetInsertionPoint()))
    S.verifica(10, "Con S si azzera, e la prima raccolta resta", dopo["azzeramenti"] == prima["azzeramenti"] + 1 and dopo["prima_raccolta"] == prima["prima_raccolta"])
    S.verifica(10, "Il testo si riscrive, con il cursore in cima e il fuoco nel testo", valore != valore_prima and posizione == 0 and "TextCtrl" in nel_filo(fuoco))
    S.verifica(10, "Il testo dice la prima raccolta e l'azzeramento", "Azzerate 1 volta" in riga_della_pagina(valore, "Prima raccolta")
        or any("Azzerate" in r for r in valore.split("\n")[:3]), valore.split("\n")[:3])
    S.verifica(10, "La console e il suono dell'azzeramento", "Statistiche azzerate: i conti ripartono da adesso." in S.console_da(segno)
        and "statistiche_azzerate" in S.suoni_da(segno))
    chiudi_le_statistiche(10)

    # F12 e F1.
    premi("f5")
    segno = time.monotonic()
    premi("f12")
    S.verifica(14, "F12: la guida rapida ha Maiuscolo con F7", any(r.startswith("Maiuscolo con F7:") for r in S.console_da(segno)))
    premi("f1")
    manuale = S.aperti[-1][0] if S.aperti else ""
    S.verifica(14, "F1 apre il manuale", str(manuale).lower().endswith("manuale.html"), manuale)

    # Tre brani: uno lasciato dopo una pausa, uno fino alla fine, uno fermato.
    cartella = _cartella_dei_brani()
    uno, due, tre = (fai_un_wav(os.path.join(cartella, nome), secondi) for nome, secondi in (("uno.wav", 40), ("due.wav", 12), ("tre.wav", 40)))
    # Il brano ripreso in pausa all'avvio si ferma prima dei conti: sarebbe
    # un lasciato in piu'.
    premi("v")
    prima = conti()

    def suona(nome):
        corrente = f.coda.corrente
        return f.motore.in_corso and corrente is not None and os.path.basename(corrente.percorso) == nome

    istanza.manda([uno, due, tre])
    S.verifica(11, "I brani arrivano da un'altra copia e parte uno.wav", aspetta(lambda: suona("uno.wav"), attesa=15))
    t_inizio = time.monotonic()
    time.sleep(4)
    premi("c")
    t_pausa = time.monotonic()
    time.sleep(3)
    premi("c")
    t_ripresa = time.monotonic()
    time.sleep(3)
    premi("b")
    aspetta(lambda: suona("due.wav"), attesa=10)
    S.verifica(11, "due.wav arriva in fondo e parte tre.wav da solo", aspetta(lambda: suona("tre.wav"), attesa=30))
    time.sleep(4)
    premi("v")
    t_fine = time.monotonic()
    dopo = conti()

    def piu(sezione, chiave):
        return round((dopo[sezione].get(chiave) or 0) - (prima[sezione].get(chiave) or 0), 2)

    wav = (dopo["formati"].get(".wav", {}).get("avvii") or 0) - (prima["formati"].get(".wav", {}).get("avvii") or 0)
    atteso = (t_fine - t_inizio) - (t_ripresa - t_pausa)
    S.verifica(11, "Tre avvii, un finito, due lasciati nei primi 10 secondi, una pausa", (wav, piu("conti", "finiti"), piu("conti", "lasciati"), piu("conti", "lasciati_subito"),
        piu("conti", "pause")) == (3, 1, 2, 2, 1), (wav, piu("conti", "finiti"), piu("conti", "lasciati"), piu("conti", "lasciati_subito"), piu("conti", "pause")))
    S.verifica(11, "Il tempo della pausa e quello in riproduzione", abs(piu("tempi", "pausa") - (t_ripresa - t_pausa)) < 1.5 and abs(piu("tempi", "play") - atteso) < 2.5,
        f"pausa {piu('tempi', 'pausa')} s su {t_ripresa - t_pausa:.1f}; riproduzione {piu('tempi', 'play')} s su {atteso:.1f}")
    S.verifica(11, "Aperti da un'altra copia", piu("conti", "aperti_da_un_altra_copia") == 1)

    # Con la finestra del video davanti.
    if S.video and os.path.isfile(S.video):
        istanza.manda([S.video])
        davanti = aspetta(lambda: f._video is not None and f._video.IsShown() and f._video.IsActive(), attesa=30)
        S.verifica(3, "La finestra del video si apre davanti", davanti)
        if davanti:
            apri_le_statistiche(3, "con Maiuscolo e F7 dalla finestra del video")
            chiudi_le_statistiche(3)
        premi("v")
        if nel_filo(lambda: f._video is not None and f._video.IsShown()):
            premi("esc")

    # Per la sessione dopo: due file nei Preferiti, con le schede e un
    # marker; uno lo cancella il banco, e la pulizia lo deve togliere.
    from playlist import Brano

    def prepara():
        for p in (uno, due):
            f.archivio.preferiti.brani.append(Brano(p))
            f.schedario.leggi_subito(p)
        f._salva_archivio()
        f._popola_playlist()
        k = f._chiave_dei_marker(uno, leggi=True)
        f.marcatori.aggiungi(k, 1.0, uno, f._durata_dei_marker(uno)[0])
        f._salva_i_marker(k)

    nel_filo(prepara)
    S.extra.update({"da_cancellare": uno, "da_tenere": due})
    apri_le_statistiche(12, "prima di chiudere", salva_come="testo_alla_chiusura")
    testo = nel_filo(lambda: statistiche()[0].valore)
    S.extra["pagina"] = {"avvii": riga_della_pagina(testo, "Avvii di MeTeOra"), "regolari": riga_della_pagina(testo, "Chiusure regolari")}
    chiudi_le_statistiche(12)
    S.extra["conti"] = conti()["conti"]
    S.salva()
    premi("f5")
    S.nota("chiudo MeTeOra con Esc")
    premi("esc")


def scenario_riavvio():
    f = S.finestra
    prima = _da_un_altra_sessione("principale")["extra"]
    # Letto prima del ciclo di wx, quando c'era solo il salvataggio subito.
    subito = S.extra.get("subito") or {}
    S.verifica(13, "Subito dopo l'avvio, prima di ogni altro salvataggio, il file dice la sessione aperta",
        subito.get("sessione_aperta") is True and subito.get("avvii") == prima["conti"].get("avvii", 0) + 1, subito)
    righe = aspetta_la_pulizia()
    via, resta = prima["da_cancellare"], prima["da_tenere"]
    # Senza --vuoti un'unita' saltata nella sessione di prima aggiunge i suoi
    # file spariti: il numero esatto vale solo partendo vuoti.
    attesa = "Pulizia finita, 1 file sparito." if S.extra.get("vuoti") else "Pulizia finita,"
    S.verifica("pulizia", "La pulizia trova il file cancellato", any(r.startswith(attesa) for r in righe), righe)

    def guarda():
        preferiti = [b.percorso for b in f.archivio.preferiti.brani]
        return (via not in preferiti and resta in preferiti, f.schedario.scheda(via) is None and f.schedario.scheda(resta) is not None,
            via not in f.marcatori.percorsi_noti(), via not in f._statistiche.percorsi_dei_brani())

    S.verifica("pulizia", "Via dai Preferiti, dallo schedario, dai marker e dallo storico; l'altro resta", nel_filo(guarda) == (True, True, True, True), nel_filo(guarda))
    apri_le_statistiche(12, "dopo il riavvio", salva_come="testo_dopo_il_riavvio")
    testo = nel_filo(lambda: statistiche()[0].valore)
    chiudi_le_statistiche(12)
    numero = lambda riga: int("".join(c for c in riga.split(":")[1] if c.isdigit()) or 0)  # noqa: E731
    avvii, regolari = riga_della_pagina(testo, "Avvii di MeTeOra"), riga_della_pagina(testo, "Chiusure regolari")
    S.verifica(12, "Avvii di MeTeOra cresce di uno, e Chiusure regolari pure", numero(avvii) == numero(prima["pagina"]["avvii"]) + 1
        and numero(regolari) == numero(prima["pagina"]["regolari"]) + 1, f"{prima['pagina']} -> {avvii}; {regolari}")
    copia = os.path.join(S.dati, "copie", f"{FILE_DELLE_STATISTICHE}.1")
    alla_chiusura = os.path.join(os.path.dirname(S.esito), "statistiche_alla_chiusura.json")
    uguali = os.path.isfile(copia) and _impronta(copia) == _impronta(alla_chiusura)
    S.verifica(12, "Nella cartella copie c'e' Statistiche.json.1, uguale al file della chiusura", uguali, copia)
    # Un'eccezione di Windows che chi la solleva gestisce, come quelle di COM:
    # faulthandler la scrive nel file del crash, e dopo la chiusura a forza non
    # deve sembrare un crash.
    import ctypes as c

    def solleva():
        with contextlib.suppress(OSError):
            c.windll.kernel32.RaiseException(0x8001010D, 0, 0, None)

    nel_filo(solleva)
    crash = os.path.join(S.dati, "MeTeOra - Crash.log")
    with open(crash, encoding="utf-8", errors="replace") as fl:
        S.verifica(13, "L'eccezione gestita e' nel file del crash", "0x8001010d" in fl.read().lower())
    S.extra.update({"conti": conti()["conti"], "secondi_dall_avvio": round(time.monotonic() - S.inizio, 1)})
    S.verifica(13, "La chiusura a forza arriva nel primo minuto", S.extra["secondi_dall_avvio"] < 60 or not S.extra.get("vuoti"), S.extra["secondi_dall_avvio"])
    S.salva()
    with open(S.esito + ".pronto", "w", encoding="utf-8") as fl:
        fl.write(str(os.getpid()))
    S.nota("pronto: il banco mi chiude a forza")
    while True:
        time.sleep(1)


def scenario_dopo_il_crash():
    prima = _da_un_altra_sessione("riavvio")["extra"]
    # L'ora sul disco al momento della chiusura a forza, letta dal banco dopo.
    with open(os.path.join(os.path.dirname(S.esito), "salvato_alla_chiusura_a_forza.txt"), encoding="utf-8") as fl:
        salvato = fl.read().strip()
    aspetta_la_pulizia()
    adesso = conti()
    S.verifica(13, "Chiusure non regolari cresce di uno, anche se la sessione e' durata pochi secondi",
        adesso["conti"].get("chiusure_non_regolari", 0) == prima["conti"].get("chiusure_non_regolari", 0) + 1,
        f"{prima['conti'].get('chiusure_non_regolari', 0)} -> {adesso['conti'].get('chiusure_non_regolari', 0)}, dopo {prima['secondi_dall_avvio']} s")
    record = adesso["record"].get("chiusura_non_regolare") or {}
    S.verifica(13, "Con l'ora dell'ultimo salvataggio", record.get("quando") == salvato, f"{record} su {salvato}")
    grave = [t for _t, t in S.console if "errore grave" in t]
    S.verifica(13, "Una chiusura a forza, con un'eccezione gestita nel file del crash, non e' un errore grave", S.crash_precedente is None and not grave
        and adesso["conti"].get("crash", 0) == prima["conti"].get("crash", 0), grave or S.crash_precedente)
    with open(os.path.join(S.dati, "MeTeOra - Errori.log"), encoding="utf-8", errors="replace") as fl:
        S.verifica(13, "Il registro degli errori riassume l'eccezione gestita", "0x8001010d" in fl.read().lower())
    apri_le_statistiche(13, "dopo la chiusura a forza", salva_come="testo_dopo_il_crash")
    testo = nel_filo(lambda: statistiche()[0].valore)
    chiudi_le_statistiche(13)
    riga = riga_della_pagina(testo, "Chiusure non regolari, con MeTeOra caduto")
    S.verifica(13, "La pagina dice l'ultima chiusura non regolare", "l'ultima dopo il salvataggio di " in riga, riga)
    # Oltre il minuto: lo svuotamento del file del crash, con un'altra
    # eccezione gestita da riassumere.
    import ctypes as c

    def solleva():
        with contextlib.suppress(OSError):
            c.windll.kernel32.RaiseException(0xE24C4A02, 0, 0, None)

    # Con i dati veri la pulizia puo' durare piu' di un minuto: conta il primo
    # svuotamento dopo l'eccezione, non quelli di prima.
    gia = len(S.svuotamenti)
    nel_filo(solleva)
    S.nota("aspetto il giro del minuto")
    svuotato = aspetta(lambda: len(S.svuotamenti) > gia, attesa=90, passo=1)
    crash = os.path.join(S.dati, "MeTeOra - Crash.log")
    S.verifica("crash", "Al minuto il file del crash si riassume e si svuota", svuotato and S.svuotamenti[gia][1] > 0 and os.path.getsize(crash) < 4096,
        f"{S.svuotamenti}; {os.path.getsize(crash)} byte")
    S.extra["conti"] = conti()["conti"]
    S.salva()
    premi("f5")
    premi("esc")


def scenario_controllo():
    prima = _da_un_altra_sessione("dopo_il_crash")["extra"]
    aspetta_la_pulizia()
    adesso = conti()["conti"]
    S.verifica(12, "La chiusura con Esc e' regolare", adesso.get("chiusure_regolari", 0) == prima["conti"].get("chiusure_regolari", 0) + 1,
        f"{prima['conti'].get('chiusure_regolari', 0)} -> {adesso.get('chiusure_regolari', 0)}")
    S.verifica(12, "Gli avvii contati tutti", adesso.get("avvii", 0) == prima["conti"].get("avvii", 0) + 1)
    premi("f5")
    premi("esc")


def scenario_dove_sono():
    """Dove sono, l'apostrofo (tappa 14 b): il tasto vero della tastiera
    italiana, premuto con la tastiera simulata, e la riga che ne esce con il
    motore vero sull'uscita nulla."""
    import re

    import istanza

    f = S.finestra
    voce = "dove sono"
    aspetta_la_pulizia()
    premi("f5")
    # Il brano ripreso in pausa all'avvio, se c'e', si ferma.
    premi("v")
    nel_filo(al_normale)

    def premi_l_apostrofo(**opzioni):
        """Preme l'apostrofo e torna l'ultima riga scritta e i suoni da li'."""
        segno = time.monotonic()
        premi("'", **opzioni)
        righe = S.console_da(segno)
        return (righe[-1] if righe else ""), S.suoni_da(segno)

    def righe():
        return nel_filo(lambda: len(f._righe))

    def suona(nome):
        corrente = f.coda.corrente
        return bool(f.motore.in_corso) and corrente is not None and os.path.basename(corrente.percorso) == nome and f.motore.posizione is not None

    riga, suonati = premi_l_apostrofo()
    S.verifica(voce, "Senza niente in corso, la frase e il suono di F8", riga == "Non sta suonando niente." and suonati == ["niente_da_suonare"], (riga, suonati))
    S.verifica(voce, "La frase va anche alla sintesi, interrompendo la voce, e al braille", S.extra.get("interrotti", [])[-1:] == [["nvda", riga]]
        and S.extra.get("braille", [])[-1:] == [["nvda", riga]], (S.extra.get("interrotti", [])[-1:], S.extra.get("braille", [])[-1:]))
    cartella = _cartella_dei_brani()
    # Nomi loro: la cartella e' quella della sessione principale, che ha gia'
    # un due.wav di 12 secondi.
    uno, due = fai_un_wav(os.path.join(cartella, "dove uno.wav"), 40), fai_un_wav(os.path.join(cartella, "dove due.wav"), 30)
    mandati = istanza.manda([uno, due])
    S.verifica(voce, "I due file arrivano da un'altra copia e dove uno.wav suona", mandati and aspetta(lambda: suona("dove uno.wav"), attesa=20), f"mandati: {mandati}")
    modello = re.compile(r"^0:\d\d di 0:40, mancano 0:\d\d, dove uno\.wav, 1 di 2, file aperti")
    # Dalla plancia, dopo qualche secondo: il tempo corre, e il mancante con lui.
    premi("f5")
    time.sleep(3)
    prima, quante = nel_filo(fuoco), righe()
    riga, suonati = premi_l_apostrofo()
    tempi = re.match(r"^0:(\d\d) di 0:40, mancano 0:(\d\d), ", riga)
    S.verifica(voce, "Dalla plancia: tempo, brano e lista, con il suo suono", bool(modello.match(riga)) and riga.endswith("file aperti.")
        and suonati == ["dove_sono"] and tempi is not None and int(tempi[1]) >= 2 and int(tempi[1]) + int(tempi[2]) == 40, (riga, suonati))
    S.verifica(voce, "Il fuoco resta dov'era", nel_filo(fuoco) == prima, f"{prima} -> {nel_filo(fuoco)}")
    S.verifica(voce, "La riga va alla sintesi e al braille, senza l'ora", S.extra.get("detti", [])[-1:] == [["nvda", riga]]
        and S.extra.get("braille", [])[-1:] == [["nvda", riga]], (S.extra.get("detti", [])[-1:], S.extra.get("braille", [])[-1:]))
    S.verifica(voce, "La riga interrompe la voce che sta parlando", S.extra.get("interrotti", [])[-1:] == [["nvda", riga]], S.extra.get("interrotti", [])[-1:])
    S.verifica(voce, "Una riga nuova nella console", righe() == quante + 1, f"{quante} -> {righe()}")
    # Dalla console la riga si riscrive, e il fuoco resta li'.
    premi("f6")
    quante = righe()
    riga, suonati = premi_l_apostrofo()
    S.verifica(voce, "Dalla console la riga si riscrive", bool(modello.match(riga)) and righe() == quante and suonati == ["dove_sono"], (riga, quante, righe()))
    S.verifica(voce, "Il fuoco resta nella console", "Console" in nel_filo(fuoco), nel_filo(fuoco))
    # Anche sulla barra la riga nuova prende subito il posto di quella di
    # prima, senza aspettarne il tempo minimo di lettura.
    S.verifica(voce, "La riga riscritta arriva subito anche al braille", S.extra.get("braille", [])[-1:] == [["nvda", riga]], S.extra.get("braille", [])[-1:])
    # In pausa, e a velocita' cambiata.
    premi("c")
    riga, _suonati = premi_l_apostrofo()
    S.verifica(voce, "In pausa, in fondo alla riga", bool(modello.match(riga)) and riga.endswith(", file aperti, in pausa."), riga)
    premi("c")
    premi("d")
    riga, _suonati = premi_l_apostrofo()
    S.verifica(voce, "La velocita' cambiata, con il punto", riga.endswith(", file aperti, velocità 1.05."), riga)
    premi("s")
    # Il secondo file.
    premi("b")
    S.verifica(voce, "B passa a dove due.wav", aspetta(lambda: suona("dove due.wav"), attesa=15))
    riga, _suonati = premi_l_apostrofo()
    S.verifica(voce, "Il secondo file, 2 di 2", bool(re.match(r"^0:\d\d di 0:30, mancano 0:\d\d, dove due\.wav, 2 di 2, file aperti\.$", riga)), riga)
    riga, suonati = premi_l_apostrofo(maiuscolo=True)
    # Dalla 1.110.0 Maiuscolo con l'apostrofo e' la durata residua, che ha una sessione sua.
    S.verifica(voce, "Maiuscolo con l'apostrofo dice la durata residua", suonati == ["durata_residua"]
        and bool(re.match(r"^Mancano \d:\d\d di \d:\d\d, trascorsi \d:\d\d, [\d.]+% ascoltato, finisce verso le \d\d:\d\d, brano 2 di 2, file aperti", riga)),
        (riga, suonati))
    premi("v")
    riga, _suonati = premi_l_apostrofo()
    S.verifica(voce, "Dopo lo stop, come F8", riga == "Non sta suonando niente.", riga)
    premi("f5")
    S.nota("chiudo MeTeOra con Esc")
    premi("esc")


def scenario_ordina():
    """Ordina e Mescola (tappa 14 c): i tempi su una playlist grande e aperta,
    e Mescola sulla playlist che suona con il seguente gia' preparato dalla
    dissolvenza. Le voci del menu si chiamano dal filo della finestra, come
    le sceglierebbe il menu."""
    import random

    f = S.finestra
    aspetta_la_pulizia()
    # I brani della playlist grande non ci sono: conta il rinfresco della
    # plancia, non il disco.
    grande = os.path.join(S.dati, "playlist grande")
    percorsi = [os.path.join(grande, f"cartella {i % 50}", f"brano {i}.mp3") for i in range(BRANI_DELLA_PLAYLIST_GRANDE)]

    def prepara():
        f._aggiungi(None, percorsi, nome="Grande")
        pl = f.archivio.playlist[-1]
        f.albero.Expand(f.nodo_playlist)
        f.albero.Expand(f._nodo_della_playlist(pl))
        f._seleziona(f._nodo_della_playlist(pl))
        return pl

    pl = nel_filo(prepara, attesa=300)
    # Un mescolamento sempre uguale, per tempi confrontabili fra due corse.
    f._mescola_a_caso = random.Random(14).shuffle  # noqa: S311 - non e' crittografia
    tempi = {}
    for nome, azione in (("Per percorso", lambda: f._ordina(pl, "percorso")), ("Per nome del file", lambda: f._ordina(pl, "nome")),
            ("Per autore", lambda: f._ordina(pl, "autore")), ("Inverti l'ordine", lambda: f._inverti(pl)), ("Mescola", lambda: f._mescola(pl)),
            ("Ordine di prima", lambda: f._ordine_di_prima(pl))):
        def misura(azione=azione):
            inizio = time.perf_counter()
            azione()
            return time.perf_counter() - inizio

        tempi[nome] = round(nel_filo(misura, attesa=300), 3)
    S.extra["tempi"] = tempi
    S.verifica("ordina", f"Ogni riordino di {BRANI_DELLA_PLAYLIST_GRANDE} brani, con la playlist aperta, sotto {DURATA_DEL_RIORDINO} secondi",
        all(t < DURATA_DEL_RIORDINO for t in tempi.values()), tempi)

    def stato_della_plancia():
        nodo = f._nodo_della_playlist(pl)
        figli = [f.albero.GetItemText(v).split(",")[0] for v in f._figli(nodo)]
        return f.albero.IsExpanded(nodo), figli[:3], [b.nome_del_file for b in pl.brani[:3]], f.albero.GetItemText(f._voce_corrente())

    aperta, nella_plancia, nella_lista, fuoco = nel_filo(stato_della_plancia)
    S.verifica("ordina", "La playlist resta aperta, nella plancia nell'ordine nuovo, e il fuoco resta su di lei", aperta and nella_plancia == nella_lista
        and fuoco.startswith("Grande"), f"{nella_plancia} {nella_lista} {fuoco}")
    righe = [r for r in S.console if r[1].startswith("Grande")]
    S.verifica("ordina", "Una riga per ogni riordino", len(righe) == len(tempi), [r[1] for r in righe])

    # La dissolvenza: il seguente preparato prima di Mescola non deve suonare.
    cartella = _cartella_dei_brani()
    wav = [fai_un_wav(os.path.join(cartella, f"{nome}.wav"), 12) for nome in ("a", "b", "c", "d")]

    def suona_con_la_dissolvenza():
        f.impostazioni["dissolvenza"].update(accesa=True, secondi=2.0)
        f._applica_la_dissolvenza()
        f._aggiungi(None, wav, nome="Dissolvenza")
        dissolvenza = f.archivio.playlist[-1]
        f._suona(dissolvenza, dissolvenza.brani[0])
        return dissolvenza

    dissolvenza = nel_filo(suona_con_la_dissolvenza)
    preparato = aspetta(lambda: f._preparato is not None, attesa=20, passo=0.05)
    nome_preparato = nel_filo(lambda: os.path.basename(f._preparato[1].percorso) if f._preparato else None)
    S.verifica("ordina", "La dissolvenza prepara il seguente, b.wav", preparato and nome_preparato == "b.wav", nome_preparato)
    f._mescola_a_caso = lambda brani: brani.reverse()
    segno = time.monotonic()
    nel_filo(lambda: f._mescola(dissolvenza))
    ordine = nel_filo(lambda: [b.nome_del_file for b in dissolvenza.brani])
    S.verifica("ordina", "Mescola mette in cima il brano che suona", ordine == ["a.wav", "d.wav", "c.wav", "b.wav"]
        and S.console_da(segno)[-1:] == ["Dissolvenza mescolata: 4 brani; quello in riproduzione ora è in cima."], f"{ordine} {S.console_da(segno)}")
    entrato = aspetta(lambda: f.coda.corrente is not None and f.coda.corrente.nome_del_file != "a.wav", attesa=20, passo=0.05)
    aspetta(lambda: os.path.basename(f.motore.in_corso or "") == f.coda.corrente.nome_del_file, attesa=3, passo=0.05)
    dopo = nel_filo(lambda: (f.coda.corrente.nome_del_file, os.path.basename(f.motore.in_corso or "")))
    S.extra["dissolvenza"] = {"preparato": nome_preparato, "ordine": ordine, "dopo": dopo}
    S.verifica("ordina", "Al passaggio entra il seguente dell'ordine nuovo, d.wav, non quello preparato prima", entrato and dopo == ("d.wav", "d.wav"), dopo)
    premi("v")
    premi("esc")


def scenario_durata_residua():
    """La durata residua, Maiuscolo con l'apostrofo (tappa 14 d): il tasto
    vero della tastiera italiana, premuto con la tastiera simulata, su due
    playlist di file veri aperte nella plancia, con le durate lette davvero
    dallo schedario e il motore vero sull'uscita nulla; alla fine il costo
    del conto con tremila voci aperte, e la seconda playlist che suona con
    la prima aperta sopra, che non conta."""
    import datetime
    import re

    f = S.finestra
    voce = "durata residua"
    aspetta_la_pulizia()
    premi("f5")
    # Il brano ripreso in pausa all'avvio, se c'e', si ferma.
    premi("v")
    nel_filo(al_normale)

    def premi_il_tasto(tasto="'"):
        """Preme Maiuscolo con l'apostrofo, o il punto interrogativo, e torna
        l'ultima riga scritta e i suoni da li'."""
        segno = time.monotonic()
        premi(tasto, maiuscolo=True)
        righe = S.console_da(segno)
        return (righe[-1] if righe else ""), S.suoni_da(segno)

    def righe():
        return nel_filo(lambda: len(f._righe))

    def suona(nome):
        corrente = f.coda.corrente
        return bool(f.motore.in_corso) and corrente is not None and os.path.basename(corrente.percorso) == nome and f.motore.posizione is not None

    def numeri(riga, totale):
        """Mancante e trascorso della riga, in secondi, se tornano con il
        totale e con la percentuale; None altrimenti. A un'altra velocita' il
        tempo vero viene subito dopo il mancante, e il totale dopo, con in
        tutto."""
        m = re.match(rf"^Mancano (\d+):(\d\d)(?: di {totale}|, alla velocità [\d.]+ sono \d+:\d\d, in tutto {totale}), trascorsi (\d+):(\d\d), ([\d.]+)% ascoltato, ",
            riga)
        if not m:
            return None
        mancano, trascorsi = int(m[1]) * 60 + int(m[2]), int(m[3]) * 60 + int(m[4])
        minuti, secondi = totale.split(":")
        tutto = int(minuti) * 60 + int(secondi)
        return (mancano, trascorsi) if mancano + trascorsi == tutto and abs(float(m[5]) - 100 * trascorsi / tutto) < 1 else None

    def ore_possibili(secondi):
        adesso = datetime.datetime.now()
        return {(adesso + datetime.timedelta(seconds=secondi + scarto)).strftime("%H:%M") for scarto in (-60, 0, 60)}

    riga, suonati = premi_il_tasto()
    S.verifica(voce, "Senza niente in corso, la frase e il suono di F8", riga == "Non sta suonando niente." and suonati == ["niente_da_suonare"], (riga, suonati))
    S.verifica(voce, "La frase va anche alla sintesi, interrompendo la voce, e al braille", S.extra.get("interrotti", [])[-1:] == [["nvda", riga]]
        and S.extra.get("braille", [])[-1:] == [["nvda", riga]], (S.extra.get("interrotti", [])[-1:], S.extra.get("braille", [])[-1:]))
    cartella = _cartella_dei_brani()
    secondi = {"uno": 40, "due": 30, "tre": 20, "quattro": 25, "cinque": 15}
    percorsi = {nome: fai_un_wav(os.path.join(cartella, f"residua {nome}.wav"), durata) for nome, durata in secondi.items()}

    def apri(*aperte, chiuse=()):
        """Apre nella plancia il ramo Playlist e le playlist date, e chiude le altre date."""
        f.albero.Expand(f.nodo_playlist)
        for pl in aperte:
            f.albero.Expand(f._nodo_della_playlist(pl))
        for pl in chiuse:
            f.albero.Collapse(f._nodo_della_playlist(pl))

    def prepara():
        """Due playlist nuove, aperte nella plancia, e tutto il resto chiuso;
        la selezione sul primo brano della prima."""
        f._chiudi_la_plancia()
        f._aggiungi(None, [percorsi[n] for n in ("uno", "due", "tre")], nome="Residua")
        prima = f.archivio.playlist[-1]
        f._aggiungi(None, [percorsi[n] for n in ("quattro", "cinque")], nome="Residua dopo")
        seconda = f.archivio.playlist[-1]
        apri(prima, seconda)
        f._seleziona(next(f._figli(f._nodo_della_playlist(prima))))
        return prima, seconda

    prima, seconda = nel_filo(prepara)
    tutti = prima.brani + seconda.brani
    letti = aspetta(lambda: all(f.schedario.durata(b) is not None for b in tutti), attesa=30)
    S.verifica(voce, "Lo schedario legge le durate dei cinque file", letti, nel_filo(lambda: [f.schedario.durata(b) for b in tutti]))
    premi("x")
    S.verifica(voce, "X suona residua uno.wav dalla plancia", aspetta(lambda: suona("residua uno.wav"), attesa=20))
    time.sleep(3)
    # Decide la plancia: le due playlist aperte, cinque brani, 2:10 in tutto.
    prima_del_tasto, quante = nel_filo(fuoco), righe()
    riga, suonati = premi_il_tasto()
    conto = numeri(riga, "2:10")
    m = re.search(r", finisce verso le (\d\d:\d\d), brano 1 di 3, playlist (.+), con i rami aperti della plancia, 5 brani in tutto\.$", riga)
    S.verifica(voce, "Dalla plancia: mancante, totale, trascorso, percentuale, ora di fine e lista, con il suo suono", conto is not None and conto[1] >= 2
        and m is not None and m[1] in ore_possibili(conto[0]) and m[2] == prima.nome and suonati == ["durata_residua"], (riga, suonati))
    S.verifica(voce, "Il fuoco resta dov'era", nel_filo(fuoco) == prima_del_tasto, f"{prima_del_tasto} -> {nel_filo(fuoco)}")
    S.verifica(voce, "La riga va alla sintesi e al braille, senza l'ora", S.extra.get("detti", [])[-1:] == [["nvda", riga]]
        and S.extra.get("braille", [])[-1:] == [["nvda", riga]], (S.extra.get("detti", [])[-1:], S.extra.get("braille", [])[-1:]))
    S.verifica(voce, "La riga interrompe la voce che sta parlando", S.extra.get("interrotti", [])[-1:] == [["nvda", riga]], S.extra.get("interrotti", [])[-1:])
    S.verifica(voce, "Una riga nuova nella console", righe() == quante + 1, f"{quante} -> {righe()}")
    # Dalla console, con il punto interrogativo: la riga si riscrive.
    premi("f6")
    quante = righe()
    riga, suonati = premi_il_tasto("?")
    S.verifica(voce, "Dalla console, con il punto interrogativo, la riga si riscrive", numeri(riga, "2:10") is not None and righe() == quante
        and suonati == ["durata_residua"] and S.extra.get("braille", [])[-1:] == [["nvda", riga]], (riga, quante, righe()))
    S.verifica(voce, "Il fuoco resta nella console", "Console" in nel_filo(fuoco), nel_filo(fuoco))
    # Chiusa la seconda playlist, restano i tre brani della prima.
    nel_filo(lambda: apri(prima, chiuse=[seconda]))
    riga, _suonati = premi_il_tasto()
    S.verifica(voce, "Chiusa la seconda playlist, il conto si accorcia", numeri(riga, "1:30") is not None
        and riga.endswith(f", brano 1 di 3, playlist {prima.nome}."), riga)
    # In pausa niente ora di fine; a un'altra velocita' il tempo vero.
    premi("c")
    riga, _suonati = premi_il_tasto()
    S.verifica(voce, "In pausa, senza l'ora di fine", numeri(riga, "1:30") is not None and ", in pausa, brano 1 di 3, " in riga and "finisce" not in riga, riga)
    premi("c")
    premi("d")
    riga, _suonati = premi_il_tasto()
    S.verifica(voce, "La velocita' cambiata, con il tempo vero di ascolto", numeri(riga, "1:30") is not None and ", alla velocità 1.05 sono " in riga, riga)
    premi("s")
    # Un brano mai letto: si conta a parte, lo schedario lo rilegge, e
    # ripremendo il tasto il conto si completa.
    tre = prima.brani[2]

    def dimentica():
        f.schedario.schede.pop(tre.percorso, None)
        f.schedario._verificati.discard(tre.percorso)

    nel_filo(dimentica)
    riga, _suonati = premi_il_tasto()
    S.verifica(voce, "Il brano senza durata si conta a parte", numeri(riga, "1:10") is not None and riga.endswith(", 1 brano senza durata."), riga)
    riletto = aspetta(lambda: f.schedario.durata(tre) is not None, attesa=20)
    riga, _suonati = premi_il_tasto()
    S.verifica(voce, "Ripremendo il tasto, il conto si completa", riletto and numeri(riga, "1:30") is not None and "senza durata" not in riga, riga)
    # Chiusa anche la prima, decide la lista: stessi numeri; e le ripetizioni, con Maiuscolo con V.
    nel_filo(lambda: apri(chiuse=[prima]))
    riga, _suonati = premi_il_tasto()
    S.verifica(voce, "Con la playlist chiusa decide la lista", numeri(riga, "1:30") is not None and riga.endswith(f", brano 1 di 3, playlist {prima.nome}."), riga)
    premi("v", maiuscolo=True)
    riga, _suonati = premi_il_tasto()
    S.verifica(voce, "Con la ripetizione del brano niente ora di fine", numeri(riga, "1:30") is not None and "finisce" not in riga
        and riga.endswith(", il brano si ripete: la lista non va avanti finché la ripetizione resta accesa."), riga)
    premi("v", maiuscolo=True)
    riga, _suonati = premi_il_tasto()
    S.verifica(voce, "Con la ripetizione della lista il giro e il suo ricominciare", ", il giro finisce verso le " in riga and riga.endswith(", poi la lista ricomincia."), riga)
    premi("v", maiuscolo=True)
    nomi = conti()["tasti"]
    S.verifica(voce, "Nelle statistiche il tasto ha un nome solo", nomi.get("Maiuscolo con apostrofo", 0) >= 11 and "Maiuscolo con punto interrogativo" not in nomi,
        {n: v for n, v in nomi.items() if "postrofo" in n or "interrogativo" in n})

    def molte_voci():
        """Tremila voci in piu' aperte nella plancia, gli stessi cinque file
        seicento volte, e il tempo del conto."""
        f._aggiungi(None, [percorsi[n] for n in secondi] * 600, nome="Residua grande")
        grande = f.archivio.playlist[-1]
        apri(prima, grande, chiuse=[seconda])
        inizio = time.perf_counter()
        f._frase_della_durata_residua(f.coda.playlist, f.coda.corrente)
        return time.perf_counter() - inizio, sum(1 for _ in f._voci_in_vista())

    durata, in_vista = nel_filo(molte_voci, attesa=120)
    S.extra["conto_con_tremila_voci"] = {"secondi": round(durata, 3), "voci_in_vista": in_vista}
    riga, _suonati = premi_il_tasto()
    S.verifica(voce, "Con tremila voci aperte il conto resta rapido", durata < 1.0 and riga.endswith(", con i rami aperti della plancia, 3003 brani in tutto."),
        f"{durata * 1000:.0f} ms con {in_vista} voci in vista; {riga}")

    def suona_la_seconda():
        """Apre anche la seconda playlist, fra la prima e la grande, e
        seleziona il suo primo brano."""
        apri(prima, seconda)
        f._seleziona(next(f._figli(f._nodo_della_playlist(seconda))))

    # Suona la seconda, con la prima aperta sopra: l'avanzamento va solo
    # avanti, e le voci sopra la lista che suona non contano.
    nel_filo(suona_la_seconda)
    premi("x")
    S.verifica(voce, "X suona residua quattro.wav, sotto la prima playlist aperta", aspetta(lambda: suona("residua quattro.wav"), attesa=20))
    riga, _suonati = premi_il_tasto()
    m = re.match(r"^Mancano \S+ di \S+, trascorsi (\d+):(\d\d), ", riga)
    S.verifica(voce, "Le voci sopra la lista che suona non contano", m is not None and int(m[1]) * 60 + int(m[2]) < 25
        and riga.endswith(f", brano 1 di 2, playlist {seconda.nome}, con i rami aperti della plancia, 3002 brani in tutto."), riga)
    premi("v")
    riga, _suonati = premi_il_tasto()
    S.verifica(voce, "Dopo lo stop, come F8", riga == "Non sta suonando niente.", riga)
    premi("f5")
    S.nota("chiudo MeTeOra con Esc")
    premi("esc")


SCENARI = {"principale": scenario_principale, "riavvio": scenario_riavvio, "dopo_il_crash": scenario_dopo_il_crash, "controllo": scenario_controllo,
    "dove_sono": scenario_dove_sono, "durata_residua": scenario_durata_residua, "ordina": scenario_ordina}


# Il banco intero: le sessioni una dopo l'altra, ognuna nel suo processo.


def _impronta(percorso):
    with open(percorso, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _lancia(nome, dati, esiti, video, vuoti):
    esito = os.path.join(esiti, nome)
    comando = [sys.executable, os.path.abspath(__file__), "--sessione", nome, "--dati", dati, "--esito", esito]
    if video:
        comando += ["--video", video]
    if vuoti:
        comando.append("--vuoti")
    print(f"Sessione {nome}, {time.strftime('%H:%M:%S')}", flush=True)
    return subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=open(esito + ".stderr.txt", "w", encoding="utf-8"))


def _aspetta_il_processo(processo, nome):
    try:
        processo.wait(DURATE_MASSIME[nome])
    except subprocess.TimeoutExpired:
        print(f"  la sessione {nome} non finisce: la chiudo a forza", flush=True)
        processo.kill()
        processo.wait()


def banco(vuoti, video, solo=None):
    """Le sessioni una dopo l'altra, o la sola sessione solo."""
    sessioni = (solo,) if solo else SESSIONI
    base = tempfile.mkdtemp(prefix="meteora_banco_")
    dati, esiti = os.path.join(base, "dati"), os.path.join(base, "esiti")
    os.makedirs(dati)
    os.makedirs(esiti)
    if not vuoti:
        for percorso in glob.glob(os.path.join(RADICE, "MeTeOra - *.json")):
            shutil.copy2(percorso, dati)
    print(f"Banco del collaudo: dati di prova in {dati}", flush=True)
    for nome in sessioni:
        processo = _lancia(nome, dati, esiti, video, vuoti)
        if nome == "riavvio":
            pronto = os.path.join(esiti, "riavvio.pronto")
            fine = time.monotonic() + DURATE_MASSIME[nome]
            while not os.path.exists(pronto) and time.monotonic() < fine and processo.poll() is None:
                time.sleep(0.5)
            if os.path.exists(pronto):
                # Come il Task Manager: TerminateProcess.
                print(f"  la chiudo a forza, {time.strftime('%H:%M:%S')}", flush=True)
                processo.kill()
        _aspetta_il_processo(processo, nome)
        if nome == "riavvio":
            # L'ora dell'ultimo salvataggio, letta a processo morto: nessun
            # salvataggio la puo' cambiare dopo.
            with contextlib.suppress(OSError, ValueError), open(os.path.join(dati, FILE_DELLE_STATISTICHE), encoding="utf-8") as f:
                salvato = json.load(f).get("salvato") or ""
                with open(os.path.join(esiti, "salvato_alla_chiusura_a_forza.txt"), "w", encoding="utf-8") as g:
                    g.write(salvato)
        if nome == "principale":
            statistiche_alla_chiusura = os.path.join(dati, FILE_DELLE_STATISTICHE)
            if os.path.isfile(statistiche_alla_chiusura):
                shutil.copy2(statistiche_alla_chiusura, os.path.join(esiti, "statistiche_alla_chiusura.json"))
            with contextlib.suppress(OSError, ValueError, KeyError), open(os.path.join(esiti, "principale.json"), encoding="utf-8") as f:
                os.remove(json.load(f)["extra"]["da_cancellare"])
    return base, esiti, _riassunto(esiti, sessioni)


def banco_a_parte(nome):
    """Una sessione a parte, come ordina, partendo senza dati."""
    base = tempfile.mkdtemp(prefix="meteora_banco_")
    dati, esiti = os.path.join(base, "dati"), os.path.join(base, "esiti")
    os.makedirs(dati)
    os.makedirs(esiti)
    print(f"Banco del collaudo, sessione {nome}: dati di prova in {dati}", flush=True)
    _aspetta_il_processo(_lancia(nome, dati, esiti, None, True), nome)
    return base, esiti, _riassunto(esiti, (nome,))


def _riassunto(esiti, sessioni=SESSIONI):
    """Il riassunto per la console e il display braille: una riga per
    sessione, una per ogni controllo non riuscito, una per ogni apertura."""
    falliti = 0
    for nome in sessioni:
        percorso = os.path.join(esiti, f"{nome}.json")
        if not os.path.isfile(percorso):
            print(f"Sessione {nome}: nessun esito.")
            falliti += 1
            continue
        with open(percorso, encoding="utf-8") as f:
            esito = json.load(f)
        risultati = esito["risultati"]
        no = [r for r in risultati if not r["esito"]]
        print(f"Sessione {nome}: {len(risultati) - len(no)} controlli superati su {len(risultati)}.")
        for r in no:
            print(f"  NO, voce {r['voce']}: {r['cosa']}. {r['dettaglio']}")
        for a in esito["aperture"]:
            print(f"  Statistiche {a['da']}: {a['secondi']} s dal tasto, {a.get('dentro')} s dentro MeTeOra, "
                f"finestra ferma al massimo {round(a['risposta_piu_lenta'] * 1000)} ms.")
        tempi = esito["extra"].get("tempi")
        if tempi:
            print("  Tempi: " + "; ".join(f"{voce} {secondi} s" for voce, secondi in tempi.items()) + ".")
        conto = esito.get("extra", {}).get("conto_con_tremila_voci")
        if conto:
            print(f"  Durata residua con {conto['voci_in_vista']} voci in vista nella plancia: {round(conto['secondi'] * 1000)} ms.")
        falliti += len(no)
    return falliti


def main():
    parser = argparse.ArgumentParser(description="Il banco del collaudo di MeTeOra, sul desktop nascosto.")
    parser.add_argument("--vuoti", action="store_true", help="parte senza i dati di questa cartella")
    parser.add_argument("--video", help="un video per Maiuscolo con F7 con la sua finestra davanti")
    parser.add_argument("--solo", choices=SESSIONI, help="la sola sessione data, per quelle che non dipendono dalle altre, come dove_sono e durata_residua")
    parser.add_argument("--ordina", action="store_true", help="solo la sessione di Ordina e Mescola, partendo senza dati")
    parser.add_argument("--sessione", choices=SESSIONI + SESSIONI_A_PARTE, help=argparse.SUPPRESS)
    parser.add_argument("--dati", help=argparse.SUPPRESS)
    parser.add_argument("--esito", help=argparse.SUPPRESS)
    argomenti = parser.parse_args()
    if argomenti.sessione:
        sessione(argomenti.sessione, argomenti.dati, argomenti.esito, argomenti.video, argomenti.vuoti)
        return 0
    if argomenti.ordina:
        base, _esiti, falliti = banco_a_parte("ordina")
    else:
        base, _esiti, falliti = banco(argomenti.vuoti, argomenti.video, argomenti.solo)
    if falliti:
        print(f"Controlli non riusciti: {falliti}. I dati e i registri restano in {base}.")
        return 1
    shutil.rmtree(base, ignore_errors=True)
    print("Tutti i controlli superati.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
