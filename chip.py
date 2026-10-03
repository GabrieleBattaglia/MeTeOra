# MeTeOra, la musica delle console: libgme, resa in RAM come i SID.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 8.

"""La musica delle console con libgme, Game Music Emu (tappa 8).

NES (NSF, NSFE), Super Nintendo (SPC), Game Boy (GBS), Sega (VGM, VGZ,
GYM), ZX Spectrum (AY), PC Engine (HES), MSX (KSS) e Atari (SAP). Come i
SID, un file puo' avere piu' brani, che nella plancia diventano
sottobrani; un filo in disparte rende il brano in RAM e libmpv lo legge
come un WAV virtuale.
La durata: se il file dice che il brano finisce, come un VGM senza
ritornello, il brano finisce li'. Altrimenti il brano gira in tondo, e la
durata scritta nel file (SPC, NSFE, .m3u) e' il punto in cui comincia la
dissolvenza; se il file non la scrive, libgme propone due giri del
ritornello, o due minuti e mezzo. La dissolvenza e' quella scritta nel
file, o di otto secondi, come nel lettore d'esempio di libgme. Un brano
che tace per sei secondi si chiude da se'.
HES e KSS non dicono quanti brani hanno: libgme ne apre sempre 256, e un
file .m3u accanto, con lo stesso nome, li ordina, li nomina e ne dice le
durate; MeTeOra lo carica quando nomina proprio quel file.
"""

import ctypes
import os
import threading
import time

import numpy as np

import librerie
import sid

# La dissolvenza finale dei brani che girano in tondo, e la coda di quelli
# che finiscono da soli.
DISSOLVENZA = 8.0
CODA = 1.0
# libgme apre un file solo per leggerne le informazioni con questa frequenza.
_SOLO_INFORMAZIONI = -1


class _Info(ctypes.Structure):
    _fields_ = ([("length", ctypes.c_int), ("intro_length", ctypes.c_int), ("loop_length", ctypes.c_int), ("play_length", ctypes.c_int),
                 ("fade_length", ctypes.c_int)] + [(f"i{n}", ctypes.c_int) for n in range(5, 16)]
                + [(nome, ctypes.c_char_p) for nome in ("system", "game", "song", "author", "copyright", "comment", "dumper")]
                + [(f"s{n}", ctypes.c_char_p) for n in range(7, 16)])


_LIBRERIA = []
_LIBRERIA_BLOCCO = threading.Lock()


def presente():
    """Vero se libgme e' nella cartella delle librerie: la mette
    strumenti/prepara_ambiente.py."""
    return os.path.isfile(os.path.join(librerie.LIB, "libgme.dll"))


def _gme():
    with _LIBRERIA_BLOCCO:
        if _LIBRERIA:
            return _LIBRERIA[0]
        dll = ctypes.CDLL(os.path.join(librerie.LIB, "libgme.dll"))
        p = ctypes.c_void_p
        firme = {
            "gme_open_file": (ctypes.c_char_p, [ctypes.c_char_p, ctypes.POINTER(p), ctypes.c_int]),
            "gme_load_m3u": (ctypes.c_char_p, [p, ctypes.c_char_p]),
            "gme_track_count": (ctypes.c_int, [p]),
            "gme_track_info": (ctypes.c_char_p, [p, ctypes.POINTER(ctypes.POINTER(_Info)), ctypes.c_int]),
            "gme_free_info": (None, [ctypes.POINTER(_Info)]),
            "gme_start_track": (ctypes.c_char_p, [p, ctypes.c_int]),
            "gme_play": (ctypes.c_char_p, [p, ctypes.c_int, p]),
            "gme_track_ended": (ctypes.c_int, [p]),
            "gme_set_fade_msecs": (None, [p, ctypes.c_int, ctypes.c_int]),
            "gme_delete": (None, [p]),
        }
        for nome, (risultato, argomenti) in firme.items():
            funzione = getattr(dll, nome)
            funzione.restype, funzione.argtypes = risultato, argomenti
        _LIBRERIA.append(dll)
        return dll


def _testo(byte):
    return byte.decode("cp1252", "replace").strip() if byte else ""


def _apri(percorso, frequenza):
    """L'emulatore di libgme per il file, con il suo .m3u se c'e'. OSError
    se libgme non lo apre."""
    gme = _gme()
    emu = ctypes.c_void_p()
    errore = gme.gme_open_file(os.fsencode(percorso), ctypes.byref(emu), frequenza)
    if errore:
        raise OSError(f"libgme non apre {percorso}: {_testo(errore)}")
    m3u = _m3u_del_file(percorso)
    if m3u:
        # Un .m3u sbagliato non ferma niente: restano i brani del file.
        gme.gme_load_m3u(emu, os.fsencode(m3u))
    return emu


def _m3u_del_file(percorso):
    """Il .m3u accanto al file, con lo stesso nome, se le sue righe nominano
    quel file o il suo tipo: un gioco con un file per sistema, come
    gioco.nsf e gioco.spc, non deve prendere la lista dell'altro. None se
    non c'e'."""
    m3u = os.path.splitext(percorso)[0] + ".m3u"
    try:
        with open(m3u, encoding="cp1252", errors="replace") as f:
            righe = [riga.split("::", 1) for riga in f.read().splitlines() if "::" in riga]
    except OSError:
        return None
    nome = os.path.basename(percorso).casefold()
    tipo = os.path.splitext(percorso)[1][1:].casefold()
    for file, resto in righe:
        if file.strip().casefold() == nome or resto.split(",", 1)[0].strip().casefold() == tipo:
            return m3u
    return None


def _durata_di(info):
    """(secondi totali, millisecondi a cui comincia la dissolvenza, o -1 se
    il brano finisce da se', millisecondi della dissolvenza)."""
    if info.length > 0 and info.loop_length == 0:
        # Il file dice che il brano finisce, senza ritornello.
        return info.length / 1000 + CODA, -1, 0
    dissolvenza = info.fade_length if info.fade_length > 0 else round(DISSOLVENZA * 1000)
    return (info.play_length + dissolvenza) / 1000, info.play_length, dissolvenza


_INFORMAZIONI = {}
_INFORMAZIONI_BLOCCO = threading.Lock()


def info(percorso):
    """Le informazioni di un file, lette una volta sola, nella forma di
    songlengths.info_del_sid: sottobrani, iniziale, titolo, autore,
    copyright, piu' sistema e durate, una per brano. None se libgme manca o
    non legge il file."""
    with _INFORMAZIONI_BLOCCO:
        if percorso in _INFORMAZIONI:
            return _INFORMAZIONI[percorso]
    risultato = None
    if presente():
        gme = _gme()
        try:
            emu = _apri(percorso, _SOLO_INFORMAZIONI)
        except OSError:
            emu = None
        if emu is not None:
            try:
                durate, titoli, generali = [], [], {}
                for traccia in range(gme.gme_track_count(emu)):
                    puntatore = ctypes.POINTER(_Info)()
                    if gme.gme_track_info(emu, ctypes.byref(puntatore), traccia):
                        durate.append(None)
                        titoli.append("")
                        continue
                    dati = puntatore.contents
                    durate.append(_durata_di(dati)[0])
                    titoli.append(_testo(dati.song))
                    if not generali:
                        generali = {"titolo": _testo(dati.game), "autore": _testo(dati.author), "copyright": _testo(dati.copyright), "sistema": _testo(dati.system)}
                    gme.gme_free_info(puntatore)
                if durate:
                    risultato = {"sottobrani": len(durate), "iniziale": 1, "durate": durate, "titoli": titoli, **generali}
            finally:
                gme.gme_delete(emu)
    with _INFORMAZIONI_BLOCCO:
        _INFORMAZIONI[percorso] = risultato
    return risultato


class BranoChip(sid.BranoSid):
    """Un brano di un file delle console, reso in memoria con libgme da un
    filo che corre in anticipo: come un sottobrano dei SID. traccia conta
    da 1; secondi e' la durata, dissolvenza compresa."""

    VELOCITA_STIMATA = 30.0
    VELOCITA_MASSIMA_STIMATA = 100.0

    def __init__(self, percorso, traccia, secondi):
        gme = _gme()
        self._emu = _apri(percorso, sid.FREQUENZA)
        errore = gme.gme_start_track(self._emu, traccia - 1)
        puntatore = ctypes.POINTER(_Info)()
        if errore or gme.gme_track_info(self._emu, ctypes.byref(puntatore), traccia - 1):
            gme.gme_delete(self._emu)
            raise OSError(f"libgme non suona il brano {traccia} di {percorso}: {_testo(errore)}")
        _secondi, inizio_della_dissolvenza, dissolvenza = _durata_di(puntatore.contents)
        gme.gme_free_info(puntatore)
        if inizio_della_dissolvenza >= 0:
            # Senza questa chiamata libgme non sfuma: un -1 farebbe sfumare
            # il brano dal primo istante.
            gme.gme_set_fade_msecs(self._emu, inizio_della_dissolvenza, dissolvenza)
        self.totale = int(secondi * sid.FREQUENZA) * sid.CANALI
        self.dati = np.zeros(self.totale, dtype=np.int16)
        self.pronti = 0
        self._fermo = False
        self._condizione = threading.Condition()
        self._partenza = time.perf_counter()
        self._filo = threading.Thread(target=self._lavora, name="MeTeOra, resa della console", daemon=True)
        self._filo.start()

    def _lavora(self):
        gme = _gme()
        try:
            while self.pronti < self.totale and not self._fermo and not gme.gme_track_ended(self._emu):
                n = min(sid.BLOCCO, self.totale - self.pronti)
                if gme.gme_play(self._emu, n, self.dati[self.pronti:].ctypes.data):
                    break
                with self._condizione:
                    self.pronti += n
                    self._condizione.notify_all()
        finally:
            # Finito prima: il resto e' silenzio, gia' zero.
            with self._condizione:
                self.pronti = self.totale
                self._condizione.notify_all()
            gme.gme_delete(self._emu)


_CONDIVISI = {}
_CONDIVISI_BLOCCO = threading.Lock()


def apri_flusso(percorso, traccia, secondi):
    """Un flusso WAV sul brano; i flussi aperti insieme sullo stesso brano
    condividono la resa, come i SID."""
    chiave = (os.path.normcase(os.path.abspath(percorso)), traccia, secondi)
    with _CONDIVISI_BLOCCO:
        voce = _CONDIVISI.get(chiave)
        if voce is None:
            voce = [BranoChip(percorso, traccia, secondi), 0]
            _CONDIVISI[chiave] = voce
        voce[1] += 1
    return sid.FlussoSid(voce[0], lambda: _lascia(chiave))


def _lascia(chiave):
    with _CONDIVISI_BLOCCO:
        voce = _CONDIVISI[chiave]
        voce[1] -= 1
        if voce[1]:
            return
        del _CONDIVISI[chiave]
    voce[0].ferma()
