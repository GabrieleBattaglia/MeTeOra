# MeTeOra, il lettore lontano: uno speaker Cast al posto della scheda audio, con la strada A e il WAV in RAM.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/11/2026: nasce con la 1.117.0, tappa 15 b del piano. Nella 2.6.4 il sottobrano resta a fine brano, come nel motore. Nella 3.11.1 le radio, con MeTeOra che fa da ripetitore senza conversione.
# Nella 2.6.5 la fine che lo speaker non dice, fermo in caricamento all'ultimo campione. Nella 2.7.0 il WAV in RAM al posto del FLAC su disco.

"""Il lettore che suona su un apparecchio Cast, per il motore.

E' la strada A con conversione, scelta da Gabriele il 29 ottobre 2026:
l'apparecchio scarica il file dal server di trasmissione.py e lo suona da
se', e il lettore lontano fa da telecomando. I file che il Chromecast legge
da se' vanno cosi' come sono; gli altri, i video, di cui va solo l'audio, e
i brani che MeTeOra rende da se', SID, MIDI e musica delle console, vanno
come WAV in RAM (2.7.0, wav_in_ram.py): la funzione converti del motore da'
la sorgente, che il server serve a intervalli mentre il convertitore la
riempie, e il brano parte subito, senza disco. Fino alla 2.6 si convertiva
prima tutto in FLAC su disco, e lo speaker aspettava. La sorgente si lascia
a fine brano, allo stop e al brano nuovo; un brano risentito si riconverte.
Quando l'apparecchio e' scelto il motore gli passa i comandi: suona, pausa,
stop, i salti e il volume; posizione, durata e pausa le dice lui. Gli avvisi
arrivano dai fili di pychromecast e delle conversioni, come quelli del
motore: alla_fine() a fine brano, all_errore(percorso) se l'apparecchio non
lo suona, al_caricamento() quando comincia a suonarlo o e' pronto in pausa,
all_interruzione() quando sull'apparecchio parte altro, per esempio dal
telefono, e al_guasto(errore) quando un comando non arriva, per esempio
perche' l'apparecchio si e' spento.
"""

import os
import threading
import time

import diretta
import formati
import indirizzi
import trasmissione

# Per quanti secondi il volume chiesto vale piu' di quello che l'apparecchio
# dice: tanto basta perche' arrivi il suo stato nuovo.
MEMORIA_DEL_VOLUME = 1.0
# Gli stati che dicono che l'apparecchio ha in mano il brano.
_SUONA_O_ASPETTA = (trasmissione.IN_RIPRODUZIONE, trasmissione.IN_PAUSA, trasmissione.IN_CARICAMENTO)
# La fine che lo speaker non dice (2.6.5). Dalla 2.7.0 i brani convertiti
# vanno come WAV, che su GabryBar finisce puntuale: resta per sicurezza.
# Misurato su GabryBar, una Ambeo Soundbar Plus, il 3 novembre 2026: con i
# FLAC che MeTeOra convertiva arriva
# all'ultimo campione, passa in caricamento con la posizione uguale alla
# durata, resta cosi' 23 secondi e poi chiude il brano con un errore; un MP3
# e un WAV finiscono da soli, entro mezzo secondo. Se dopo ATTESA_DELLA_FINE
# secondi lo speaker e' ancora li', il brano e' finito. Vale come fine un
# caricamento entro MARGINE_DELLA_FINE secondi dalla durata.
ATTESA_DELLA_FINE = 1.0
MARGINE_DELLA_FINE = 0.25


def da_convertire(percorso, sottobrano=None, midi_reso=False):
    """Vero se il brano va mandato come WAV in RAM: un formato
    che il Chromecast non legge, un video, un sottobrano di un SID o della
    musica delle console, o un MIDI che MeTeOra rende con FluidSynth."""
    return sottobrano is not None or midi_reso or formati.e_video(percorso) or not trasmissione.legge_da_se(percorso)


class LettoreLontano:
    """Il lettore di un apparecchio Cast. connetti(allo_stato, al_distacco)
    da' la connessione, un trasmissione.Apparecchio, e il distacco va ad
    al_guasto, come un comando che non arriva; server e' il server da cui
    l'apparecchio prende i file e le sorgenti; converti(percorso, sottobrano)
    da' la sorgente del WAV in RAM, con chiudi(), o solleva se il brano non si
    legge. I comandi non sollevano mai: un errore va ad al_guasto."""

    def __init__(self, connetti, server, converti, alla_fine=None, all_errore=None, al_caricamento=None, all_interruzione=None, al_guasto=None,
            al_titolo=None):
        self._blocco = threading.RLock()
        # La radio ripetuta allo speaker (3.11.1): il titolo in onda, chi lo
        # vuole sapere, e la lettura aperta che aspetta la prima richiesta.
        self.titolo_in_onda = None
        self._al_titolo = al_titolo
        self._lettura_in_attesa = None
        self._server = server
        self._converti = converti
        self._alla_fine = alla_fine
        self._all_errore = all_errore
        self._al_caricamento = al_caricamento
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
        # Cresce a ogni brano e a ogni stop: una sorgente pronta tardi non
        # manda un brano che non serve piu'. E la sorgente del brano, se va
        # come WAV in RAM.
        self._generazione = 0
        self._sorgente = None
        # La fine attesa, con lo speaker in caricamento all'ultimo campione:
        # un segno che ogni stato nuovo, ogni brano e lo stop tolgono.
        self._fine_attesa = None
        # Il volume chiesto per ultimo, e quando: per un attimo vale lui,
        # finche' l'apparecchio non manda il suo stato nuovo, cosi' le
        # pressioni ravvicinate del volume non si perdono.
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
        se chiesto. Se va come WAV in RAM, la sorgente si prepara in disparte,
        perche' chiede la durata del brano, e il brano parte appena c'e'."""
        with self._blocco:
            self._generazione += 1
            generazione = self._generazione
            self.percorso, self.sottobrano, self.sottobrani = percorso, sottobrano, sottobrani
            self._indirizzo = None
            self._pronto = False
            self._fine_attesa = None
            self._pausa = bool(in_pausa)
            self._durata = None
            vecchia, self._sorgente = self._sorgente, None
            self.titolo_in_onda = None
        if vecchia is not None:
            self._lascia(vecchia)
        self._lascia_la_lettura()
        if formati.e_indirizzo(percorso) and indirizzi.e_una_radio(percorso):
            threading.Thread(target=self._ripeti_la_radio, args=(generazione, percorso), name="MeTeOra, radio per lo speaker", daemon=True).start()
            return
        if not da_convertire(percorso, sottobrano, midi_reso):
            self._manda(generazione, percorso, inizio)
        else:
            threading.Thread(target=self._converti_e_manda, args=(generazione, percorso, sottobrano, inizio),
                             name="MeTeOra, WAV per lo speaker", daemon=True).start()

    def _converti_e_manda(self, generazione, percorso, sottobrano, inizio):
        try:
            sorgente = self._converti(percorso, sottobrano)
        except Exception:  # noqa: BLE001 - libmpv e la pipe falliscono in molti modi: per il lettore vuol dire che il brano non si suona
            sorgente = None
        with self._blocco:
            corrente = generazione == self._generazione
            if corrente and sorgente is not None:
                self._sorgente = sorgente
        if not corrente:
            if sorgente is not None:
                self._lascia(sorgente)
            return
        if sorgente is None:
            self._errore(generazione)
            return
        self._manda(generazione, None, inizio, sorgente)

    def _ripeti_la_radio(self, generazione, percorso):
        """Una radio per lo speaker (Gabriele, 3.11.1): MeTeOra la legge con
        diretta.py, che toglie i metadati e da' il titolo in onda, e ne passa
        i byte cosi' come sono dal suo server, da ripetitore, senza
        convertirla: lo speaker la decodifica. Va anche con i server ICY 200
        OK e i certificati scaduti, che lo speaker potrebbe non aprire. Le
        dirette a pezzi, come le m3u8, lo speaker le apre da se'."""
        if not diretta.da_leggere(percorso):
            self._manda(generazione, None, None, diretto=(percorso, "application/x-mpegURL"))
            return
        try:
            lettura = diretta.Lettura(percorso, al_titolo=self._titolo)
        except Exception:  # noqa: BLE001 - la rete fallisce in molti modi: per il lettore la radio non si suona
            self._errore(generazione)
            return
        with self._blocco:
            if generazione != self._generazione:
                lettura.close()
                return
            self._lettura_in_attesa = lettura
        tipo = lettura.tipo if lettura.tipo.startswith("audio/") else "audio/mpeg"

        def scrivi(uscita):
            with self._blocco:
                prima, self._lettura_in_attesa = self._lettura_in_attesa, None
            corrente = prima or diretta.Lettura(percorso, al_titolo=self._titolo)
            try:
                while generazione == self._generazione:
                    dati = corrente.read(16384)
                    if not dati:
                        return
                    uscita.write(dati)
            finally:
                corrente.close()

        # L'estensione del tipo, che il Chromecast guarda.
        estensione = next((e for e, t in trasmissione.TIPI.items() if t == tipo), ".mp3")
        indirizzo = self._server.pubblica_flusso(f"radio{generazione}{estensione}", scrivi, tipo)
        self._manda(generazione, None, None, diretto=(indirizzo, tipo))

    def _titolo(self, titolo):
        """Il titolo in onda della radio ripetuta, dal filo che la legge."""
        self.titolo_in_onda = titolo
        if self._al_titolo is not None:
            self._al_titolo(titolo)

    def _lascia_la_lettura(self):
        """La lettura della radio di prima, se lo speaker non l'ha mai chiesta."""
        with self._blocco:
            lettura, self._lettura_in_attesa = self._lettura_in_attesa, None
        if lettura is not None:
            lettura.close()

    def _manda(self, generazione, file, inizio, sorgente=None, diretto=None):
        with self._blocco:
            if generazione != self._generazione:
                return
            if diretto is not None:
                # Una radio: il suo flusso ripetuto, o una m3u8, senza fine (3.11.1).
                indirizzo, tipo = diretto
                self._indirizzo = indirizzo
            elif sorgente is not None:
                indirizzo = self._indirizzo = self._server.pubblica_sorgente(sorgente)
                tipo = sorgente.tipo
            else:
                indirizzo = self._indirizzo = self._server.pubblica_file(file)
                tipo = trasmissione.tipo_di(file)
            in_pausa = self._pausa
            titolo = os.path.basename(self.percorso or file)
        if diretto is not None:
            self._comanda(lambda: self.apparecchio.suona(indirizzo, tipo, titolo=titolo, in_diretta=True, in_pausa=in_pausa))
            return
        self._comanda(lambda: self.apparecchio.suona(indirizzo, tipo, titolo=titolo, inizio=inizio or None, in_pausa=in_pausa))

    def _lascia(self, sorgente):
        """Il server non la serve piu', e il convertitore si ferma."""
        self._server.ritira_sorgente(sorgente)
        sorgente.chiudi()

    def _lascia_se_finito(self):
        """A brano finito, fermo o in errore, la sorgente se ne va: la RAM torna libera."""
        with self._blocco:
            if self.percorso is not None or self._sorgente is None:
                return
            sorgente, self._sorgente = self._sorgente, None
        self._lascia(sorgente)

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
            self._fine_attesa = None
            self._pausa = False
            self.titolo_in_onda = None
        self._lascia_se_finito()
        self._lascia_la_lettura()
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
            # Il sottobrano resta, come a fine brano.
            self.percorso = None
            self._indirizzo = None
            self._pronto = False
        self._lascia_se_finito()
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
        self._lascia_se_finito()
        if avviso is not None:
            avviso()

    def _all_ultimo_campione(self, posizione):
        return posizione is not None and bool(self._durata) and posizione >= self._durata - MARGINE_DELLA_FINE

    def _aspetta_la_fine(self):
        """Lo speaker e' in caricamento all'ultimo campione: se non cambia
        stato entro ATTESA_DELLA_FINE, il brano e' finito. Sotto il lucchetto."""
        segno = self._fine_attesa = object()
        filo = threading.Timer(ATTESA_DELLA_FINE, self._fine_non_detta, args=(segno,))
        filo.daemon = True
        filo.start()

    def _fine_non_detta(self, segno):
        """Lo speaker e' ancora fermo all'ultimo campione: per il lettore il
        brano e' finito, come con lo stato FINISHED, sottobrano compreso. Se
        poi lo speaker dice la fine o l'errore, quegli stati non contano
        piu', perche' il brano non c'e'."""
        with self._blocco:
            if self._fine_attesa is not segno or self.percorso is None:
                return
            self._fine_attesa = None
            self.percorso = None
            self._indirizzo = None
            self._pronto = False
        self._lascia_se_finito()
        if self._alla_fine is not None:
            self._alla_fine()

    def _stato_del_brano(self, stato):
        """Lo stato del brano pubblicato, sotto il lucchetto: l'avviso da dare
        fuori, o None."""
        if stato.get("durata"):
            self._durata = stato["durata"]
        self._fine_attesa = None
        if stato["stato"] in _SUONA_O_ASPETTA:
            if stato["stato"] != trasmissione.IN_CARICAMENTO:
                self._pausa = stato["stato"] == trasmissione.IN_PAUSA
            if not self._pronto:
                self._pronto = True
                return self._al_caricamento
            if stato["stato"] == trasmissione.IN_CARICAMENTO and self._all_ultimo_campione(stato.get("posizione")):
                self._aspetta_la_fine()
            return None
        motivo = stato.get("motivo")
        # Un FERMO prima che l'apparecchio abbia il brano e' quello del brano
        # di prima; un errore conta sempre.
        if stato["stato"] != trasmissione.FERMO or (not self._pronto and motivo != "ERROR"):
            return None
        percorso = self.percorso
        # Il sottobrano resta, come nel motore sul PC: la finestra ci trova il
        # seguente, il 5 dopo il 4. Cancellato, la plancia ripartiva dal primo
        # sottobrano del SID (Gabriele, con GabryBar, 2.6.4).
        self.percorso = None
        self._indirizzo = None
        self._pronto = False
        if motivo == "ERROR":
            return (lambda: self._all_errore(percorso)) if self._all_errore is not None else None
        if motivo in ("INTERRUPTED", "CANCELLED"):
            return self._all_interruzione
        return self._alla_fine
