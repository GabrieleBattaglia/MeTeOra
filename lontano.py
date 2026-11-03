# MeTeOra, il lettore lontano: uno speaker Cast al posto della scheda audio, con la strada A e la conversione in FLAC.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/11/2026: nasce con la 1.117.0, tappa 15 b del piano.

"""Il lettore che suona su un apparecchio Cast, per il motore.

E' la strada A con conversione, scelta da Gabriele il 29 ottobre 2026:
l'apparecchio scarica il file dal server di trasmissione.py e lo suona da
se', e il lettore lontano fa da telecomando. I file che il Chromecast legge
da se' vanno cosi' come sono; gli altri, i video, di cui va solo l'audio, e
i brani che MeTeOra rende da se', SID, MIDI e musica delle console, si
convertono prima in FLAC, in disparte, con la funzione converti del motore,
che usa i suoi protocolli. Le conversioni restano nella cartella data finche'
il lettore non si chiude, cosi' un brano risentito non si converte due
volte.
Quando l'apparecchio e' scelto il motore gli passa i comandi: suona, pausa,
stop, i salti e il volume; posizione, durata e pausa le dice lui. Gli avvisi
arrivano dai fili di pychromecast e delle conversioni, come quelli del
motore: alla_fine() a fine brano, all_errore(percorso) se l'apparecchio non
lo suona, al_caricamento() quando comincia a suonarlo o e' pronto in pausa,
alla_conversione(percorso) quando una conversione comincia,
all_interruzione() quando sull'apparecchio parte altro, per esempio dal
telefono, e al_guasto(errore) quando un comando non arriva, per esempio
perche' l'apparecchio si e' spento.
"""

import os
import threading
import time

import formati
import trasmissione

# Per quanti secondi il volume chiesto vale piu' di quello che l'apparecchio
# dice: tanto basta perche' arrivi il suo stato nuovo.
MEMORIA_DEL_VOLUME = 1.0
# Gli stati che dicono che l'apparecchio ha in mano il brano.
_SUONA_O_ASPETTA = (trasmissione.IN_RIPRODUZIONE, trasmissione.IN_PAUSA, trasmissione.IN_CARICAMENTO)


def da_convertire(percorso, sottobrano=None, midi_reso=False):
    """Vero se il brano va convertito in FLAC prima di mandarlo: un formato
    che il Chromecast non legge, un video, un sottobrano di un SID o della
    musica delle console, o un MIDI che MeTeOra rende con FluidSynth."""
    return sottobrano is not None or midi_reso or formati.e_video(percorso) or not trasmissione.legge_da_se(percorso)


class LettoreLontano:
    """Il lettore di un apparecchio Cast. connetti(allo_stato, al_distacco)
    da' la connessione, un trasmissione.Apparecchio, e il distacco va ad
    al_guasto, come un comando che non arriva; server e' il server da cui
    l'apparecchio prende i file; cartella quella delle conversioni;
    converti(percorso, sottobrano, uscita) scrive il FLAC e torna vero se ci
    e' riuscito. I comandi non sollevano mai: un errore va ad al_guasto."""

    def __init__(self, connetti, server, cartella, converti, alla_fine=None, all_errore=None, al_caricamento=None, alla_conversione=None,
                 all_interruzione=None, al_guasto=None):
        self._blocco = threading.RLock()
        self._server = server
        self._cartella = cartella
        self._converti = converti
        self._alla_fine = alla_fine
        self._all_errore = all_errore
        self._al_caricamento = al_caricamento
        self._alla_conversione = alla_conversione
        self._all_interruzione = all_interruzione
        self._al_guasto = al_guasto
        # Il brano: il file, il sottobrano e quanti ce ne sono, come nel
        # motore; l'indirizzo pubblicato, che riconosce gli stati che lo
        # riguardano; se l'apparecchio l'ha in mano; la pausa chiesta.
        self.percorso = None
        self.sottobrano = self.sottobrani = None
        self._indirizzo = None
        self._pronto = False
        self._pausa = False
        self._durata = None
        # Cresce a ogni brano e a ogni stop: una conversione finita tardi non
        # manda un brano che non serve piu'.
        self._generazione = 0
        self._convertiti = {}
        # Il volume chiesto per ultimo, e quando: per un attimo vale lui,
        # finche' l'apparecchio non manda il suo stato nuovo, cosi' le
        # pressioni ravvicinate di piu' e meno non si perdono.
        self._volume_chiesto = None
        self._quando_chiesto = 0.0
        self.apparecchio = connetti(self._stato, self._distacco)

    # Lo stato, come lo chiede il motore.

    @property
    def nome(self):
        return self.apparecchio.nome

    @property
    def in_pausa(self):
        return self._pausa

    @property
    def posizione(self):
        """I secondi del brano adesso, o None se l'apparecchio non l'ha ancora."""
        if not self._pronto:
            return None
        try:
            return self.apparecchio.posizione
        except Exception:  # noqa: BLE001 - un apparecchio sparito non sa la posizione
            return None

    @property
    def durata(self):
        return self._durata if self._pronto else None

    @property
    def volume(self):
        """Il volume dell'apparecchio, da 0 a 100, o None se non si sa."""
        if self._volume_chiesto is not None and time.monotonic() - self._quando_chiesto < MEMORIA_DEL_VOLUME:
            return self._volume_chiesto
        valore = self.apparecchio.volume
        return round(valore * 100) if valore is not None else None

    @volume.setter
    def volume(self, valore):
        valore = max(0, min(100, round(valore)))
        self._volume_chiesto, self._quando_chiesto = valore, time.monotonic()
        self._comanda(lambda: setattr(self.apparecchio, "volume", valore / 100))

    @property
    def muto(self):
        return bool(self.apparecchio.muto)

    @muto.setter
    def muto(self, valore):
        self._comanda(lambda: setattr(self.apparecchio, "muto", bool(valore)))

    # I comandi.

    def suona(self, percorso, sottobrano=None, sottobrani=None, inizio=None, in_pausa=False, midi_reso=False):
        """Fa suonare il brano all'apparecchio, dai secondi inizio, in pausa
        se chiesto. Se va convertito, la conversione si fa in disparte e il
        brano parte quando e' pronta."""
        with self._blocco:
            self._generazione += 1
            generazione = self._generazione
            self.percorso, self.sottobrano, self.sottobrani = percorso, sottobrano, sottobrani
            self._indirizzo = None
            self._pronto = False
            self._pausa = bool(in_pausa)
            self._durata = None
            chiave = (os.path.normcase(percorso), sottobrano, midi_reso)
            convertito = self._convertiti.get(chiave)
        if not da_convertire(percorso, sottobrano, midi_reso):
            self._manda(generazione, percorso, inizio)
        elif convertito is not None and os.path.isfile(convertito):
            self._manda(generazione, convertito, inizio)
        else:
            threading.Thread(target=self._converti_e_manda, args=(generazione, chiave, percorso, sottobrano, inizio),
                             name="MeTeOra, conversione per lo speaker", daemon=True).start()

    def _converti_e_manda(self, generazione, chiave, percorso, sottobrano, inizio):
        if self._alla_conversione is not None:
            self._alla_conversione(percorso)
        uscita = os.path.join(self._cartella, f"brano_{len(self._convertiti) + 1}_{generazione}.flac")
        try:
            riuscita = self._converti(percorso, sottobrano, uscita)
        except Exception:  # noqa: BLE001 - libmpv fallisce in molti modi: per il lettore vuol dire che il brano non si suona
            riuscita = False
        with self._blocco:
            corrente = generazione == self._generazione
            if riuscita:
                self._convertiti[chiave] = uscita
        if not corrente:
            return
        if not riuscita or not os.path.isfile(uscita):
            self._errore(generazione)
            return
        self._manda(generazione, uscita, inizio)

    def _manda(self, generazione, file, inizio):
        with self._blocco:
            if generazione != self._generazione:
                return
            indirizzo = self._indirizzo = self._server.pubblica_file(file)
            in_pausa = self._pausa
            titolo = os.path.basename(self.percorso or file)
        self._comanda(lambda: self.apparecchio.suona(indirizzo, trasmissione.tipo_di(file), titolo=titolo, inizio=inizio or None, in_pausa=in_pausa))

    def pausa(self, valore=None, sfumando=False):
        """Mette o toglie la pausa; senza valore la inverte. Torna il nuovo
        stato. Lo speaker non sfuma: sfumando c'e' per il motore."""
        with self._blocco:
            if self.percorso is None:
                return self._pausa
            self._pausa = (not self._pausa) if valore is None else bool(valore)
            pausa = self._pausa
        self._comanda(self.apparecchio.pausa if pausa else self.apparecchio.riprendi)
        return pausa

    def stop(self, sfumando=False):
        with self._blocco:
            c_era = self.percorso is not None
            self._generazione += 1
            self.percorso = self.sottobrano = self.sottobrani = None
            self._indirizzo = None
            self._pronto = False
            self._pausa = False
        if c_era:
            self._comanda(self.apparecchio.ferma)

    def vai_a(self, secondi):
        if self.percorso is not None:
            self._comanda(lambda: self.apparecchio.vai_a(max(0.0, float(secondi))))

    def salta(self, secondi):
        self.vai_a((self.posizione or 0.0) + secondi)

    def chiudi(self, attendi=True):
        """Ferma, chiude la connessione e il server; i FLAC convertiti restano
        nella cartella, che e' di chi l'ha data. Senza attendi lo fa in
        disparte: uno speaker che non risponde puo' far aspettare secondi.
        L'app dello speaker si chiude solo se suona ancora un brano di
        MeTeOra: se intanto e' partito altro, per esempio dal telefono, non si
        spegne."""
        with self._blocco:
            nostro = self.percorso is not None
        self.stop()
        if not attendi:
            threading.Thread(target=self._chiudi, args=(nostro,), name="MeTeOra, chiusura dello speaker", daemon=True).start()
            return
        self._chiudi(nostro)

    def _chiudi(self, nostro):
        try:
            self.apparecchio.chiudi(lascia_l_app=not nostro)
        finally:
            self._server.ferma()

    # Dietro le quinte.

    def _comanda(self, comando):
        try:
            comando()
        except Exception as errore:  # noqa: BLE001 - pychromecast e la rete falliscono in molti modi: lo dice al_guasto
            if self._al_guasto is not None:
                self._al_guasto(errore)

    def _distacco(self, stato):
        """La connessione all'apparecchio e' caduta, nel filo di pychromecast."""
        if self._al_guasto is not None:
            self._al_guasto(ConnectionError(f"connessione {stato}"))

    def _errore(self, generazione):
        with self._blocco:
            if generazione != self._generazione or self.percorso is None:
                return
            percorso = self.percorso
            self.percorso = self.sottobrano = self.sottobrani = None
            self._indirizzo = None
            self._pronto = False
        if self._all_errore is not None:
            self._all_errore(percorso)

    def _stato(self, stato):
        """Uno stato nuovo dall'apparecchio, nel filo di pychromecast. Conta
        solo quello del brano pubblicato per ultimo."""
        avviso = None
        with self._blocco:
            if self.percorso is None or self._indirizzo is None:
                return
            if stato.get("indirizzo") not in (None, self._indirizzo):
                # Sull'apparecchio suona un'altra cosa, mandata da fuori; gli
                # stati del brano di prima, che finisce, non contano.
                if stato.get("stato") in _SUONA_O_ASPETTA and self._pronto:
                    self.percorso = self.sottobrano = self.sottobrani = None
                    self._indirizzo = None
                    self._pronto = False
                    avviso = self._all_interruzione
            else:
                avviso = self._stato_del_brano(stato)
        if avviso is not None:
            avviso()

    def _stato_del_brano(self, stato):
        """Lo stato del brano pubblicato, sotto il lucchetto: l'avviso da dare
        fuori, o None."""
        if stato.get("durata"):
            self._durata = stato["durata"]
        if stato["stato"] in _SUONA_O_ASPETTA:
            if stato["stato"] != trasmissione.IN_CARICAMENTO:
                self._pausa = stato["stato"] == trasmissione.IN_PAUSA
            if not self._pronto:
                self._pronto = True
                return self._al_caricamento
            return None
        motivo = stato.get("motivo")
        # Un FERMO prima che l'apparecchio abbia il brano e' quello del brano
        # di prima; un errore conta sempre.
        if stato["stato"] != trasmissione.FERMO or (not self._pronto and motivo != "ERROR"):
            return None
        percorso = self.percorso
        self.percorso = self.sottobrano = self.sottobrani = None
        self._indirizzo = None
        self._pronto = False
        if motivo == "ERROR":
            return (lambda: self._all_errore(percorso)) if self._all_errore is not None else None
        if motivo in ("INTERRUPTED", "CANCELLED"):
            return self._all_interruzione
        return self._alla_fine
