# MeTeOra, una volta sola per macchina: cancella i dati di MeTeOra accanto ai sorgenti, perche' la 1.104.0 riparta da zero.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 20/10/2026: nasce con la 1.104.0, chiesto da Gabriele: si lancia prima di MeTeOra su ogni macchina, e poi si toglie dal progetto. Nella 1.112.0 anche i dischi della pulizia all'avvio.

"""Cancella per sempre, senza copie, i dati di MeTeOra nella cartella di questo
script, cioe' quella dei sorgenti: impostazioni, playlist e Preferiti,
schedario, marker, punti da riprendere, statistiche e dischi riconosciuti
dalla pulizia all'avvio, con i loro file .tmp e .nuovo, la cartella copie e
i registri degli errori e dei crash. Restano i file che si fanno a mano: i
marker esportati e le console salvate.
Uso, con MeTeOra chiuso: python pulisci_i_dati.py
"""

import ctypes
import glob
import os
import shutil
import sys
from ctypes import wintypes

from GBUtils import key

import copie
import istanza
import registro
from lingua import _

CARTELLA = os.path.dirname(os.path.abspath(__file__))
DATI = ("Impostazioni", "Playlist", "Schedario", "Marcatori", "Posizioni", "Statistiche", "Dischi")
SYNCHRONIZE = 0x00100000
# Il tasto che conferma la cancellazione: la s di sì vale sempre, e accanto
# quello della lingua di MeTeOra.
# Traduttori: il tasto da premere per rispondere sì alla domanda "Cancello tutto?", una lettera minuscola.
CONFERMA = frozenset({"s", _("s")})


def meteora_aperto():
    """Vero se MeTeOra tiene il suo mutex: all'uscita riscriverebbe i dati."""
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenMutexW.restype = wintypes.HANDLE
    kernel32.OpenMutexW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    maniglia = kernel32.OpenMutexW(SYNCHRONIZE, False, istanza.nome_del_mutex())
    if not maniglia:
        return False
    kernel32.CloseHandle(wintypes.HANDLE(maniglia))
    return True


def da_cancellare():
    """I file e le cartelle da togliere, che ci sono davvero."""
    trovati = []
    for nome in DATI:
        trovati += glob.glob(os.path.join(CARTELLA, glob.escape(f"MeTeOra - {nome}.json")) + "*")
    for nome in (registro.FILE_DEGLI_ERRORI, registro.FILE_DEL_CRASH, registro.FILE_DEL_CRASH_PRECEDENTE):
        trovati += glob.glob(os.path.join(CARTELLA, glob.escape(nome)) + "*")
    cartella_delle_copie = os.path.join(CARTELLA, copie.CARTELLA)
    if os.path.isdir(cartella_delle_copie):
        trovati.append(cartella_delle_copie)
    return sorted(set(trovati))


def main():
    print(_("Pulizia dei dati di MeTeOra."))
    print(_("Cartella: {cartella}").format(cartella=CARTELLA))
    if meteora_aperto():
        print(_("MeTeOra è aperto: chiudilo e rilancia."))
        return 1
    elenco = da_cancellare()
    if not elenco:
        # Traduttori: e' gia' pulita la cartella dei dati.
        print(_("Niente da cancellare: è già pulita."))
        return 0
    # Traduttori: n e' il numero dei file e delle cartelle da cancellare, che seguono uno per riga.
    print(_("Da cancellare per sempre, {n}:").format(n=len(elenco)))
    for percorso in elenco:
        nome = os.path.basename(percorso)
        # Traduttori: un elemento dell'elenco da cancellare che e' una cartella.
        print("  " + (_("{nome}, cartella").format(nome=nome) if os.path.isdir(percorso) else nome))
    # Traduttori: S e' il tasto che risponde sì: la stessa lettera della traduzione di "s", qui in maiuscolo.
    risposta = key("\r" + _("Cancello tutto? S sì, altro tasto no.") + "\r")
    print()
    if str(risposta).lower() not in CONFERMA:
        print(_("Niente cancellato."))
        return 0
    non_riusciti = []
    for percorso in elenco:
        try:
            if os.path.isdir(percorso):
                shutil.rmtree(percorso)
            else:
                os.remove(percorso)
        except OSError as e:
            non_riusciti.append(f"{os.path.basename(percorso)}: {e.strerror or e}")
    print(_("Cancellati: {n} su {totale}.").format(n=len(elenco) - len(non_riusciti), totale=len(elenco)))
    for riga in non_riusciti:
        # Traduttori: dettaglio e' il nome del file, due punti, e il motivo dato da Windows.
        print("  " + _("Non cancellato, {dettaglio}").format(dettaglio=riga))
    if non_riusciti:
        return 1
    print(_("Fatto: al prossimo avvio MeTeOra riparte da zero."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
