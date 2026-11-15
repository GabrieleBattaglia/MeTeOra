# MeTeOra, il lettore lontano: uno speaker Cast al posto della scheda audio, con la strada A e il WAV in RAM.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/11/2026: nasce con la 1.117.0, tappa 15 b del piano. Nella 2.6.4 il sottobrano resta a fine brano, come nel motore. Nella 3.11.1 le radio, con MeTeOra che fa da ripetitore senza conversione. Nella 3.11.3 le letture chiuse allo stop e all'errore, i titoli vecchi scartati e le liste dirette allo speaker. Nella 3.11.6 allo speaker solo fotogrammi interi, e i conti per le statistiche. Nella 3.12.0 le TV con l'audio convertito dal vivo, e le liste rifiutate ricordate.
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

I comandi all'apparecchio vanno in fila a un filo loro (Gabriele, 15
novembre 2026: i salti con YouTube erano diventati lenti): pychromecast
aspetta la risposta di quasi ogni comando, fino a 10 secondi, e la finestra
aspettava con lui, con il suono e la riga dopo la risposta. Partono uno alla
volta, nell'ordine in cui sono chiesti, e la finestra torna subito; i salti
in fila diventano uno solo, al punto chiesto per ultimo, e cosi' i volumi.
Il punto chiesto con un salto vale come posizione finche' il salto non e'
arrivato, e un attimo dopo: due salti ravvicinati partono dal punto chiesto,
non da quello vecchio che l'apparecchio dice ancora. Un salto senza risposta
in tempo non e' uno speaker perso.
"""

import collections
import contextlib
import os
import threading
import time

import diretta
import formati
import indirizzi
import trasmissione
import wav_in_ram

# Per quanti secondi il volume chiesto vale piu' di quello che l'apparecchio
# dice: tanto basta perche' arrivi il suo stato nuovo. Dal 15 novembre 2026
# vale anche finche' il comando aspetta in fila, e i secondi contano da
# quando e' arrivato.
MEMORIA_DEL_VOLUME = 1.0
# Lo stesso per il punto chiesto con un salto (Gabriele, 15 novembre 2026):
# vale finche' il salto non e' arrivato all'apparecchio, e per tanti secondi
# dopo. Due pressioni ravvicinate di Maiuscolo con Q, o della virgola per i
# capitoli, partivano dal punto vecchio, che l'apparecchio dice ancora.
MEMORIA_DEL_PUNTO = 1.0
# Quanto chiudi, con attendi, aspetta al piu' che i comandi in fila arrivino.
ATTESA_DELLA_CHIUSURA = 60.0
# Le voci della fila dei comandi che, in fila una dopo l'altra, diventano una.
_DA_UNIRE = ("salto", "volume")
# Le voci che aspettano che l'apparecchio abbia il brano: pychromecast le
# manderebbe al brano di prima, o a nessuno, e senza brano solleva
# RequestFailed, che vale uno speaker perso.
_COL_BRANO = ("salto", "pausa")
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
# Le liste che uno speaker ha rifiutato, mandate com'erano: da li' in poi
# vanno con l'audio convertito dal vivo (3.12.0).
_liste_da_convertire = set()


def _unisci(fila, voce):
    """Mette la voce in fondo alla fila dei comandi; un salto o un volume
    subito dopo un altro dello stesso brano ne prende il posto, perche' quello
    di prima non serve piu'. Vero se si e' unita (15 novembre 2026)."""
    ultima = fila[-1] if fila else None
    if ultima is not None and voce[0] in _DA_UNIRE and ultima[0] == voce[0] and ultima[1] == voce[1]:
        fila[-1] = voce
        return True
    fila.append(voce)
    return False


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
    legge. I comandi non sollevano mai: un errore va ad al_guasto.
    al_conto(nome, quanto) riceve i conti per le statistiche, come i punti
    rotti tolti alle radio. converti_dal_vivo(percorso, uscita, alla_fine)
    fa partire il convertitore dell'audio di una TV, che scrive il PCM in
    uscita, e torna un oggetto con terminate()."""

    def __init__(self, connetti, server, converti, alla_fine=None, all_errore=None, al_caricamento=None, all_interruzione=None, al_guasto=None,
            al_titolo=None, al_conto=None, converti_dal_vivo=None):
        self._blocco = threading.RLock()
        # Chi tiene i conti delle statistiche, al_conto(nome, quanto), dai
        # fili del lettore (3.11.6).
        self._al_conto = al_conto
        # Chi converte dal vivo l'audio di una TV per lo speaker,
        # converti_dal_vivo(percorso, uscita, alla_fine), e la lista mandata
        # allo speaker com'era, per ricordarla se la rifiuta (3.12.0).
        self._converti_dal_vivo = converti_dal_vivo
        self._lista_diretta = None
        # La radio ripetuta allo speaker (3.11.1): il titolo in onda, chi lo
        # vuole sapere, e la lettura aperta che aspetta la prima richiesta.
        self.titolo_in_onda = None
        self._al_titolo = al_titolo
        self._lettura_in_attesa = None
        # Le letture che stanno passando una radio allo speaker (3.11.3).
        self._letture = set()
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
        # pressioni ravvicinate del volume non si perdono; e se il suo
        # comando e' ancora in fila (15 novembre 2026).
        self._volume_chiesto = None
        self._quando_chiesto = 0.0
        self._volume_in_fila = False
        # La fila dei comandi per l'apparecchio (Gabriele, 15 novembre 2026),
        # con il filo che la esegue, vero mentre lavora. Una voce e' (tipo,
        # generazione, cosa, numero): la generazione del brano a cui il
        # comando serve, o None per quelli di tutto l'apparecchio, come il
        # volume, e una voce di un brano di prima non parte piu'; cosa e' la
        # funzione da chiamare, o il punto di un salto e il volume; numero
        # quello del salto.
        self._comandi = collections.deque()
        self._esecutore = False
        self._fila_vuota = threading.Condition(self._blocco)
        # I salti e le pause chiesti prima che l'apparecchio abbia il brano:
        # tornano in testa alla fila quando lo ha, e un brano nuovo o lo stop
        # li lasciano cadere. Intanto il resto della fila va avanti, e il
        # brano stesso, che arriva dopo, non li aspetta.
        self._rinviati = []
        # Vero dopo chiudi: niente piu' comandi, e niente piu' avvisi di guasto.
        self._chiuso = False
        # Il punto chiesto con l'ultimo salto: (secondi, generazione, numero
        # del salto, scadenza in monotonic, None finche' il salto non e'
        # arrivato), e quanti salti sono stati chiesti, per numerarli. E il
        # punto da cui il brano e' partito, per un salto chiesto prima che
        # l'apparecchio dica la sua posizione.
        self._punto_chiesto = None
        self._salti = 0
        self._inizio = None
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
        """I secondi del brano adesso, o None se l'apparecchio non l'ha ancora.
        Dopo un salto, per un attimo, il punto chiesto (MEMORIA_DEL_PUNTO)."""
        punto = self._punto_valido()
        if punto is not None:
            return punto
        if not self._pronto:
            return None
        try:
            return self.apparecchio.posizione
        except Exception:  # noqa: BLE001 - un apparecchio sparito non sa la posizione
            return None

    def _punto_valido(self):
        """Il punto chiesto con l'ultimo salto, se vale ancora per il brano di
        adesso: finche' il salto non e' arrivato all'apparecchio, e per
        MEMORIA_DEL_PUNTO secondi dopo; altrimenti None."""
        with self._blocco:
            chiesto = self._punto_chiesto
            if chiesto is None or chiesto[1] != self._generazione or self.percorso is None:
                return None
            if chiesto[3] is not None and time.monotonic() >= chiesto[3]:
                return None
            return chiesto[0]

    @property
    def durata(self):
        return self._durata if self._pronto else None

    @property
    def volume(self):
        """Il volume dell'apparecchio, da 0 a 100, o None se non si sa."""
        with self._blocco:
            chiesto = self._volume_chiesto
            vale = chiesto is not None and (self._volume_in_fila or time.monotonic() - self._quando_chiesto < MEMORIA_DEL_VOLUME)
        if vale:
            return chiesto
        valore = self.apparecchio.volume
        return round(valore * 100) if valore is not None else None

    @volume.setter
    def volume(self, valore):
        valore = max(0, min(100, round(valore)))
        with self._blocco:
            if self._chiuso:
                return
            self._volume_chiesto, self._quando_chiesto, self._volume_in_fila = valore, time.monotonic(), True
            self._in_fila(("volume", None, valore, None))

    @property
    def muto(self):
        return bool(self.apparecchio.muto)

    @muto.setter
    def muto(self, valore):
        self._comanda("muto", lambda: setattr(self.apparecchio, "muto", bool(valore)))

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
            self._lista_diretta = None
            self._punto_chiesto = None
            self._inizio = inizio
            self._rinviati.clear()
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
        OK e i certificati scaduti, che lo speaker potrebbe non aprire. Alle
        MP3 e alle AAC si tolgono i byte rotti fra i fotogrammi, che fermano
        GabryBar (3.11.6, diretta.Fotogrammi). Le dirette a pezzi, come le
        m3u8, vanno a _manda_la_lista."""
        if not diretta.da_leggere(percorso):
            self._manda_la_lista(generazione, percorso)
            return
        def al_titolo(titolo):
            self._titolo(generazione, titolo)

        try:
            lettura = diretta.Lettura(percorso, al_titolo=al_titolo)
        except diretta.NonDiretta:
            # Porta a una lista, come una HLS senza .m3u8.
            diretta.a_libmpv(percorso)
            self._manda_la_lista(generazione, percorso)
            return
        except Exception:  # noqa: BLE001 - la rete fallisce in molti modi: per il lettore la radio non si suona
            self._errore(generazione)
            return
        with self._blocco:
            if generazione != self._generazione:
                lettura.close()
                return
            self._lettura_in_attesa = lettura
        tipo = lettura.tipo if lettura.tipo.startswith("audio/") else "audio/mpeg"
        filtrare = diretta.da_filtrare(lettura.tipo)

        def apri():
            with self._blocco:
                prima, self._lettura_in_attesa = self._lettura_in_attesa, None
            return prima or diretta.Lettura(percorso, al_titolo=al_titolo)

        def scrivi(uscita):
            self._passa(generazione, apri, uscita, filtrare)

        # L'estensione del tipo, che il Chromecast guarda.
        estensione = next((e for e, t in trasmissione.TIPI.items() if t == tipo), ".mp3")
        indirizzo = self._server.pubblica_flusso(f"radio{generazione}{estensione}", scrivi, tipo)
        self._manda(generazione, None, None, diretto=(indirizzo, tipo))

    def _manda_la_lista(self, generazione, percorso):
        """Una diretta a pezzi, come le m3u8, o un indirizzo che porta a una
        lista: lo speaker la apre da se'. Le TV, che radio-browser mette fra
        le radio, sono flussi video, e lo speaker, solo audio, le rifiuta
        senza mai partire (prova su GabryBar del 12 novembre 2026): una lista
        con varianti video, o che lo speaker ha gia' rifiutato, va con
        l'audio convertito dal vivo da libmpv, come WAV senza fine
        (Gabriele, 3.12.0). Un convertitore per richiesta."""
        if self._converti_dal_vivo is None or not (percorso in _liste_da_convertire or diretta.lista_con_video(percorso)):
            with self._blocco:
                if generazione == self._generazione:
                    self._lista_diretta = percorso
            self._manda(generazione, None, None, diretto=(percorso, "application/x-mpegURL"))
            return

        def avvia(uscita, alla_fine):
            return self._converti_dal_vivo(percorso, uscita, alla_fine)

        def scrivi(uscita):
            self._passa(generazione, lambda: wav_in_ram.FlussoPcm(avvia), uscita, False)

        self._conta("dirette_convertite_per_lo_speaker", 1)
        indirizzo = self._server.pubblica_flusso(f"radio{generazione}.wav", scrivi, wav_in_ram.TIPO)
        self._manda(generazione, None, None, diretto=(indirizzo, wav_in_ram.TIPO))

    def _passa(self, generazione, apri, uscita, filtrare):
        """Passa allo speaker, in uscita, quello che legge il lettore che apri()
        da', una diretta.Lettura o un wav_in_ram.FlussoPcm, finche' la radio
        e' la stessa e il lettore ha dati; a una radio nuova, o allo stop, lo
        chiude _lascia_la_lettura, che sveglia anche una lettura che aspetta.
        Con filtrare, solo fotogrammi interi (3.11.6): un filtro per
        richiesta, perche' una richiesta nuova riparte da un punto nuovo."""
        with self._blocco:
            if generazione != self._generazione:
                return
        corrente = apri()
        filtro = diretta.Fotogrammi() if filtrare else None
        with self._blocco:
            self._letture.add(corrente)
            viva = generazione == self._generazione
        try:
            while viva and generazione == self._generazione:
                dati = corrente.read(16384)
                if not dati:
                    resto = filtro.fine() if filtro is not None else b""
                    if resto:
                        uscita.write(resto)
                    return
                if filtro is not None:
                    rotture, scartati = filtro.rotture, filtro.scartati
                    dati = filtro.passa(dati)
                    self._conta("rotture_tolte_allo_speaker", filtro.rotture - rotture)
                    self._conta("byte_rotti_tolti_allo_speaker", filtro.scartati - scartati)
                    if not dati:
                        continue
                uscita.write(dati)
        finally:
            with self._blocco:
                self._letture.discard(corrente)
            corrente.close()

    def _titolo(self, generazione, titolo):
        """Il titolo in onda della radio ripetuta, dal filo che la legge; quello
        di una radio di prima si scarta."""
        if generazione != self._generazione:
            return
        self.titolo_in_onda = titolo
        if self._al_titolo is not None:
            self._al_titolo(titolo)

    def _lascia_la_lettura(self):
        """Le letture della radio di prima: quella che lo speaker non ha mai
        chiesto e quelle che gli passano la radio, che close sveglia anche se
        aspettano la rete (verifica della 3.11.3)."""
        with self._blocco:
            letture = [self._lettura_in_attesa, *self._letture]
            self._lettura_in_attesa = None
            self._letture.clear()
        for lettura in letture:
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
            self._comanda("suona", lambda: self.apparecchio.suona(indirizzo, tipo, titolo=titolo, in_diretta=True, in_pausa=in_pausa), generazione)
            return
        self._comanda("suona", lambda: self.apparecchio.suona(indirizzo, tipo, titolo=titolo, inizio=inizio or None, in_pausa=in_pausa), generazione)

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
            generazione = self._generazione
        self._comanda("pausa", self.apparecchio.pausa if pausa else self.apparecchio.riprendi, generazione)
        return pausa

    def stop(self, sfumando=False):
        with self._blocco:
            c_era = self.percorso is not None
            self._generazione += 1
            generazione = self._generazione
            self.percorso = self.sottobrano = self.sottobrani = None
            self._indirizzo = None
            self._pronto = False
            self._fine_attesa = None
            self._pausa = False
            self.titolo_in_onda = None
            self._lista_diretta = None
            self._punto_chiesto = None
            self._rinviati.clear()
        self._lascia_se_finito()
        self._lascia_la_lettura()
        if c_era:
            self._comanda("ferma", self.apparecchio.ferma, generazione)

    def vai_a(self, secondi):
        """Il salto ai secondi dati, nei limiti del brano, in fila per
        l'apparecchio: il punto vale subito come posizione (15 novembre
        2026), e un salto ancora in fila prende quello nuovo."""
        with self._blocco:
            if self.percorso is None:
                return
            punto = max(0.0, float(secondi))
            if self._durata:
                punto = min(punto, float(self._durata))
            self._salti += 1
            self._punto_chiesto = (punto, self._generazione, self._salti, None)
            unito = self._in_fila(("salto", self._generazione, punto, self._salti))
        if unito:
            self._conta("salti_uniti_allo_speaker", 1)

    def salta(self, secondi):
        """Un salto dal punto di adesso: dopo un altro salto, dal punto
        chiesto, anche se l'apparecchio non ci e' ancora arrivato (Gabriele,
        15 novembre 2026); prima che dica dove e', dal punto da cui il brano
        e' partito."""
        posizione = self.posizione
        if posizione is None:
            posizione = self._inizio or 0.0
        self.vai_a(posizione + secondi)

    def chiudi(self, attendi=True):
        """Ferma, chiude la connessione e il server; i FLAC convertiti restano
        nella cartella, che e' di chi l'ha data. La chiusura va in fondo alla
        fila dei comandi, dopo quelli chiesti prima; con attendi la si
        aspetta, al piu' ATTESA_DELLA_CHIUSURA secondi, senza la fa il filo
        dei comandi in disparte: uno speaker che non risponde puo' far
        aspettare secondi. L'app dello speaker si chiude solo se suona ancora
        un brano di MeTeOra: se intanto e' partito altro, per esempio dal
        telefono, non si spegne. Da qui i comandi che non arrivano non si
        dicono piu' ad al_guasto: lo speaker non e' piu' quello in uso, e la
        finestra lo prenderebbe per quello nuovo."""
        with self._blocco:
            nostro = self.percorso is not None
        self.stop()
        with self._blocco:
            if self._chiuso:
                return
            self._in_fila(("chiudi", None, lambda: self._chiudi(nostro), None))
            self._chiuso = True
        if attendi:
            self.aspetta_i_comandi(ATTESA_DELLA_CHIUSURA)

    def _chiudi(self, nostro):
        try:
            self.apparecchio.chiudi(lascia_l_app=not nostro)
        finally:
            self._server.ferma()

    # Dietro le quinte.

    def _conta(self, nome, quanto):
        """Un conto delle statistiche, dal filo che lo vede, se e' piu' di zero."""
        if quanto > 0 and self._al_conto is not None:
            self._al_conto(nome, quanto)

    # La fila dei comandi (Gabriele, 15 novembre 2026).

    def _comanda(self, tipo, comando, generazione=None):
        """Un comando per l'apparecchio, in fila al filo dei comandi. tipo e'
        suona, pausa, ferma o muto; con generazione vale solo per quel brano:
        un brano nuovo, o lo stop, lo lasciano cadere se non e' ancora
        partito, e una pausa anche a brano finito."""
        with self._blocco:
            self._in_fila((tipo, generazione, comando, None))

    def _in_fila(self, voce):
        """Con il lucchetto: la voce va in fondo alla fila dei comandi, e il
        filo dei comandi parte se non c'e'. Un salto o un volume subito dopo
        un altro dello stesso brano ne prende il posto, perche' quello di
        prima non serve piu': torna vero se si e' unito."""
        if self._chiuso:
            return False
        unito = _unisci(self._comandi, voce)
        self._avvia_l_esecutore()
        return unito

    def _avvia_l_esecutore(self):
        """Con il lucchetto: il filo dei comandi parte, se non c'e'."""
        if not self._esecutore:
            self._esecutore = True
            threading.Thread(target=self._esegui_i_comandi, name="MeTeOra, comandi dello speaker", daemon=True).start()

    def _riprendi_i_rinviati(self):
        """Con il lucchetto, quando l'apparecchio ha il brano: i salti e le
        pause rinviati tornano in testa alla fila, nel loro ordine."""
        rinviati = [voce for voce in self._rinviati if voce[1] == self._generazione]
        self._rinviati.clear()
        if rinviati and not self._chiuso:
            self._comandi.extendleft(reversed(rinviati))
            self._avvia_l_esecutore()

    def _esegui_i_comandi(self):
        """Il filo dei comandi: uno alla volta, nell'ordine in cui sono
        arrivati, fuori dal lucchetto, perche' pychromecast aspetta le
        risposte. Finisce a fila vuota, e il comando dopo lo fa ripartire.
        Un salto o una pausa prima che l'apparecchio abbia il brano si
        rinvia: il resto della fila, e il brano stesso, non lo aspettano."""
        while True:
            with self._blocco:
                if not self._comandi:
                    self._esecutore = False
                    self._fila_vuota.notify_all()
                    return
                voce = self._comandi.popleft()
                tipo, generazione, cosa, numero = voce
                vecchia = generazione is not None and (generazione != self._generazione or (tipo in _COL_BRANO and self.percorso is None))
                rinviata = not vecchia and tipo in _COL_BRANO and not self._pronto
                unito = rinviata and _unisci(self._rinviati, voce)
            if unito:
                self._conta("salti_uniti_allo_speaker", 1)
            if vecchia or rinviata:
                continue
            # Un avviso che non va, per esempio con la finestra che si
            # chiude, non ferma la fila.
            with contextlib.suppress(Exception):
                self._esegui(tipo, cosa, numero)

    def _esegui(self, tipo, cosa, numero):
        """Nel filo dei comandi: una voce della fila."""
        if tipo == "salto":
            self._manda_il_salto(cosa, numero)
        elif tipo == "volume":
            self._manda_il_volume(cosa)
        elif tipo == "chiudi":
            # Si sta chiudendo: un apparecchio sparito non ha piu' niente da dire.
            with contextlib.suppress(Exception):
                cosa()
        else:
            try:
                cosa()
            except Exception as errore:  # noqa: BLE001 - pychromecast e la rete falliscono in molti modi: lo dice al_guasto
                self._guasto(errore)

    def _manda_il_salto(self, punto, numero):
        """Nel filo dei comandi: il salto all'apparecchio, che ha il brano.
        Un salto senza risposta non e' uno speaker perso (Gabriele, 15
        novembre 2026): pychromecast aspetta la risposta fino a 10 secondi, e
        uno speaker che carica il punto nuovo puo' rispondere tardi; la
        connessione che cade la dice al_distacco. Si contano, come i salti
        uniti."""
        try:
            self.apparecchio.vai_a(punto)
        except Exception as errore:  # noqa: BLE001 - pychromecast e la rete falliscono in molti modi
            if trasmissione.senza_risposta(errore):
                self._conta("salti_senza_risposta_dallo_speaker", 1)
            else:
                self._guasto(errore)
        finally:
            with self._blocco:
                chiesto = self._punto_chiesto
                if chiesto is not None and chiesto[2] == numero:
                    # Arrivato: il punto chiesto vale ancora per un attimo.
                    self._punto_chiesto = (*chiesto[:3], time.monotonic() + MEMORIA_DEL_PUNTO)

    def _manda_il_volume(self, valore):
        """Nel filo dei comandi: il volume all'apparecchio. Arrivato l'ultimo
        chiesto, il volume chiesto vale ancora per MEMORIA_DEL_VOLUME."""
        try:
            self.apparecchio.volume = valore / 100
        except Exception as errore:  # noqa: BLE001 - pychromecast e la rete falliscono in molti modi: lo dice al_guasto
            self._guasto(errore)
        finally:
            with self._blocco:
                if not any(voce[0] == "volume" for voce in self._comandi):
                    self._volume_in_fila = False
                    self._quando_chiesto = time.monotonic()

    def aspetta_i_comandi(self, attesa=5.0):
        """Aspetta, al piu' attesa secondi, che la fila dei comandi sia vuota
        e l'ultimo arrivato all'apparecchio: vero se lo e'. Per chiudi e per
        le prove; non dal filo dei comandi, che aspetterebbe se stesso."""
        fine = time.monotonic() + attesa
        with self._blocco:
            while self._comandi or self._esecutore:
                resto = fine - time.monotonic()
                if resto <= 0:
                    return False
                self._fila_vuota.wait(resto)
            return True

    def _guasto(self, errore):
        """Un comando che non arriva, o la connessione che cade: lo dice
        al_guasto, se il lettore non e' chiuso."""
        if self._al_guasto is not None and not self._chiuso:
            self._al_guasto(errore)

    def _distacco(self, stato):
        """La connessione all'apparecchio e' caduta, nel filo di pychromecast."""
        self._guasto(ConnectionError(f"connessione {stato}"))

    def _errore(self, generazione):
        with self._blocco:
            if generazione != self._generazione or self.percorso is None:
                return
        # Le letture della radio in errore si chiudono (verifica della 3.11.3).
        self._lascia_la_lettura()
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
                self._riprendi_i_rinviati()
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
        if motivo == "ERROR" and self._lista_diretta is not None and self._lista_diretta == percorso:
            # La lista mandata com'era e' rifiutata: la riprova della finestra
            # la manda con l'audio convertito dal vivo (3.12.0).
            _liste_da_convertire.add(percorso)
            self._lista_diretta = None
            if self._al_conto is not None:
                self._al_conto("liste_rifiutate_dallo_speaker", 1)
        if motivo == "ERROR":
            return (lambda: self._all_errore(percorso)) if self._all_errore is not None else None
        if motivo in ("INTERRUPTED", "CANCELLED"):
            return self._all_interruzione
        return self._alla_fine
