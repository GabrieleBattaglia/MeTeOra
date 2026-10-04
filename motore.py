# MeTeOra, il motore di riproduzione: libmpv, e i SID in tempo reale.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1, dai prototipi della tappa 0. Nella 1.51.0 la scheda audio della musica, letta e scelta. Nella 1.55.0 due lettori, velocita', tono, equalizzatore e dissolvenza incrociata (tappa 4, issue 15); nella 1.55.1 i comandi ai lettori diventano asincroni, e a fine brano la finestra non aspetta piu' il mezzo secondo in cui mpv svuota l'uscita. Nella 1.58.0 stop, pausa, ripresa, X da capo e marker sfumano con la dissolvenza accesa; nella 1.58.4 le discese arrivano allo zero prima di fermarsi. Nella 1.61.1 i SID partono prima. Nella 1.62.0 attesa_del_sid. Nella 1.62.2 due lettori sullo stesso SID ne condividono la resa. Nella 1.62.4 OPZIONI_DI_BASE, anche per la sonda dello schedario. Nella 1.63.0 il video in una finestra, le tracce e i sottotitoli (tappa 7). Nella 1.65.0 i MIDI resi da FluidSynth (tappa 8). Nella 1.66.0 la musica delle console con libgme. Nella 1.67.0 il file lasciato o rinominato per Rinomina file. Nella 1.82.0 il testo del karaoke come traccia in memoria, senza i .lrc caricati da mpv, e due sottotitoli uguali di fila detti tutti e due. Nella 1.83.0 il tempo che resta al sottotitolo, per la barra braille a blocchi. Nella 1.83.3 la durata vera di Musepack e DSF, da mutagen. Nella 1.93.0 i capitoli che libmpv vede. Nella 1.95.0 l'attenuazione, per la sfumatura del timer di spegnimento. Nella 1.96.0 il volume uniforme con ReplayGain. Nella 1.96.11 suona con a_volume_pieno.

"""Due lettori libmpv per tutti i formati.

I file normali li apre libmpv. I SID passano dal protocollo sid://, che
libmpv chiede a questo modulo: il brano si emula in un filo che corre in
anticipo e libmpv lo legge come un WAV. Cosi' volume, seek e fine del brano
funzionano allo stesso modo per tutti.

I lettori sono due, per la dissolvenza incrociata: uno e' l'attivo, quello
del brano in corso; l'altro resta fermo, oppure suona il brano che esce
durante una sfumatura, oppure tiene in pausa il brano seguente preparato
in anticipo. Fuori dalla dissolvenza suona solo l'attivo, come quando il
lettore era uno.

Ogni comando arriva ai lettori in modo asincrono, in fila: a fine brano
mpv svuota l'uscita per circa 0,4 secondi, e in quel tempo ogni chiamata
sincrona a quel lettore resta ferma (misurato: da 426 a 495 ms). Le
chiamate asincrone tornano subito e restano nell'ordine in cui sono
partite; per questo volume, muto, pausa e scheda il motore li ricorda da
se', e non li rilegge da mpv. Si leggono da mpv solo posizione e durata,
e mai da un lettore che sta finendo.

Velocita', tono ed equalizzatore valgono per tutti e due i lettori e per
tutti i brani. La catena dei filtri e' fissa: l'equalizzatore a sette bande
e poi scaletempo2, che tiene fermo il tono quando cambia la velocita' e
non lascia buchi tornando al normale. Il guadagno di una banda cambiato al
volo (af-command) mpv lo perde a ogni seek, a ogni brano nuovo e al cambio
di scheda: per questo la catena si riscrive, con i guadagni di adesso,
prima di ognuno di questi passi. Lo perde anche quando riapre l'uscita da
se', per esempio quando Windows cambia la scheda predefinita: li' la catena
si riscrive dopo, all'evento AUDIO_RECONFIG del lettore.

Gli eventi di libmpv e il sorvegliante della dissolvenza lavorano in fili
loro: chi riceve gli avvisi (alla_fine, all_errore, chiedi_il_seguente,
al_passaggio) deve riportarli nel filo della finestra, per esempio con
wx.CallAfter.
La scheda audio su cui suona la musica e' quella di dispositivo, da
scegliere fra quelle di dispositivi(); la sceglie schede_audio.applica.
"""

import contextlib
import functools
import math
import os
import threading

import librerie  # noqa: F401

# isort: split
import mpv

import chip
import formati
import karaoke
import midi
import sid
import sottobrani
import valori

# La durata di un SID che non sta in nessun database: tre minuti, come fanno
# i lettori di SID.
DURATA_SID_PREDEFINITA = 180.0
# Oltre il 100 il volume amplifica, per gli audio registrati troppo bassi.
VOLUME_MASSIMO = 300
# La larghezza delle bande dell'equalizzatore, come Q: circa un'ottava e un
# quarto, la distanza fra una banda e l'altra. Misurato su rumore bianco:
# con tutte le bande a +6 la risposta fra 60 e 12000 Hz sta fra +6,3 e +8,5,
# con tutte a +12 fra +12,7 e +17,5; nessun buco fra una banda e l'altra.
Q_DELLE_BANDE = 1.07
# Quanto prima della fine del brano, oltre alla durata della dissolvenza, si
# chiede alla finestra il brano seguente: un SID impiega fino a mezzo secondo
# per partire. Secondi veri, non del brano: con la velocita' cambiano.
ANTICIPO_DEL_SEGUENTE = 1.5
# Quanto prima della fine si ferma chi esce: l'evento di fine arriva circa
# 0,4 secondi prima della fine che si sente, e da li' il lettore svuota
# l'uscita senza rispondere. Fermato prima, quell'attesa non c'e'.
MARGINE_DI_FINE = 0.5
# Ogni quanti secondi il sorvegliante guarda la dissolvenza.
PASSO_DEL_SORVEGLIANTE = 0.02
_FINE_NORMALE = mpv.MpvEventEndFile.EOF
_FINE_PER_ERRORE = mpv.MpvEventEndFile.ERROR
# Le opzioni di ogni istanza di libmpv di MeTeOra, anche della sonda dello
# schedario. Gli script interni di mpv (interfaccia a schermo, console,
# statistiche...) a MeTeOra non servono, e caricandoli LuaJIT solleva
# all'avvio eccezioni di Windows che gestisce da se', ma che il faulthandler
# di Python stampa come errori fatali.
OPZIONI_DI_BASE = {"vo": "null", "video": "no", "config": False, "ytdl": False, "input_default_bindings": False, "osc": False,
    "load_stats_overlay": False, "load_console": False, "load_auto_profiles": False, "load_select": False, "load_commands": False,
    "load_positioning": False, "load_context_menu": False, "input_vo_keyboard": False, "input_cursor": False}
# I formati di cui libmpv stima la durata, dai pacchetti o dalla dimensione
# del file: quella vera la sa mutagen. Prova del 4 ottobre 2026 sui campioni
# di FFmpeg: i Musepack SV8 piu' corti fino a un secondo e mezzo, che con la
# dissolvenza perdevano la fine; i DSF piu' lunghi quanto pesano i loro tag.
DURATA_DA_MUTAGEN = frozenset({".mpc", ".dsf"})
# Il filtro che annerisce il fotogramma per leggere le tracce a immagini a
# video spento: una foto con i sottotitoli ha solo le loro lettere (1.80.0).
FILTRO_DEL_NERO = "lavfi=[drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill]"
# Un sottotitolo di testo uguale al precedente si ridice solo se il
# precedente e' cominciato almeno tanti secondi prima: un ritornello o due No
# di un film si', i cartelli ASS animati fotogramma per fotogramma no
# (revisione della 1.82.0: uno di tre secondi si diceva 44 volte).
RIPETIZIONE_MINIMA = 0.5
# Il volume uniforme (1.96.0): la scelta delle impostazioni e l'opzione di
# mpv, che legge i tag ReplayGain dei file e vale subito, anche per il brano
# in corso.
REPLAYGAIN_DI_MPV = {"spento": "no", "brano": "track", "album": "album"}
_EVENTI_UTILI = frozenset({mpv.MpvEventID.START_FILE, mpv.MpvEventID.FILE_LOADED, mpv.MpvEventID.END_FILE, mpv.MpvEventID.AUDIO_RECONFIG})


def durata_del_sottobrano(percorso, sottobrano):
    """I secondi di un sottobrano: per i SID dal database della collezione,
    per le console da libgme; se non si sa, la durata predefinita."""
    durate = sottobrani.durate(percorso)
    durata = durate[sottobrano - 1] if durate and sottobrano <= len(durate) else None
    return durata if durata is not None else DURATA_SID_PREDEFINITA


def sottobrano_risolto(percorso, sottobrano=None):
    """Il sottobrano che il motore suona per un file e un sottobrano chiesto:
    per un SID o un file delle console quello chiesto, o l'iniziale, o il
    primo, entro i sottobrani; None per gli altri file e per quelli che non
    si leggono."""
    info = sottobrani.info(percorso)
    if not info:
        return None
    return min(sottobrano or info["iniziale"] or 1, max(1, info["sottobrani"]))


def catena_dei_filtri(bande):
    """La stringa af per mpv: le sette bande dell'equalizzatore con i guadagni
    dati, in dB, e poi scaletempo2. L'equalizzatore viene prima: con
    scaletempo2 davanti mpv segnala un errore al primo cambio di velocita'.
    Le bande hanno la larghezza in Q (t=q): con le ottave (t=o) l'uscita e'
    tutta NaN sui file a 8000, 16000 e 32000 Hz. precision=f64 evita la
    saturazione dentro il filtro sui file a 16 bit."""
    filtri = ",".join(f"equalizer@b{i}=f={f}:t=q:w={Q_DELLE_BANDE}:g={g:g}:precision=f64" for i, (f, g) in enumerate(zip(valori.FREQUENZE_DELLE_BANDE, bande, strict=True)))
    return f"@eq:lavfi=[{filtri}],scaletempo2"


def _durata_da_mutagen(percorso):
    """La durata letta da mutagen, o None se non la sa."""
    try:
        import mutagen

        info = getattr(mutagen.File(percorso), "info", None)
        return float(info.length) if info is not None and info.length else None
    except Exception:  # noqa: BLE001 - un file che mutagen non legge tiene la durata di libmpv
        return None


def _apri_sid(uri):
    # sid://<sottobrano>/<secondi>/<percorso>
    sottobrano, secondi, percorso = uri[len("sid://"):].split("/", 2)
    return sid.apri_flusso(percorso, int(sottobrano), float(secondi))


def _apri_chip(uri):
    # chip://<sottobrano>/<secondi>/<percorso>, la musica delle console.
    sottobrano, secondi, percorso = uri[len("chip://"):].split("/", 2)
    return chip.apri_flusso(percorso, int(sottobrano), float(secondi))


# Le opzioni di loadfile per i flussi WAV resi in RAM, SID e MIDI. Il formato
# e' gia' detto, e l'intestazione WAV dice tutto il resto: senza probe-info e
# con probesize al minimo lavf non legge in anticipo secondi di flusso, che
# andrebbero prima resi. La partenza scende da circa 230 a circa 80 ms
# (tappa 5, 1.61.1).
_OPZIONI_DEL_FLUSSO = {"demuxer-lavf-format": "wav", "demuxer-lavf-probe-info": "no", "demuxer-lavf-probesize": "32",
    "cache": "no", "demuxer-readahead-secs": "1"}
# La durata di un MIDI di cui la mappa dei tempi non si legge.
DURATA_DI_RISERVA_DEL_MIDI = 180.0


def _testo(valore):
    """Un valore come lo vuole il comando set di mpv."""
    if isinstance(valore, bool):
        return "yes" if valore else "no"
    return str(valore)


def _fra(valore, minimo, massimo):
    return max(minimo, min(massimo, valore))


class _Brano:
    """Dove sta un brano per libmpv: l'indirizzo, le opzioni di loadfile e,
    per i SID, il sottobrano scelto e quanti ce ne sono."""

    def __init__(self, percorso, sottobrano=None, inizio=None, banco_midi=None):
        self.percorso = percorso
        self.indirizzo = percorso
        self.opzioni = {"start": f"{inizio:.3f}"} if inizio else {}
        self.sottobrano = sottobrano_risolto(percorso, sottobrano)
        self.sottobrani = None
        if self.sottobrano is not None:
            self.sottobrani = max(1, sottobrani.info(percorso)["sottobrani"])
            secondi = durata_del_sottobrano(percorso, self.sottobrano)
            protocollo = "chip" if formati.e_chip(percorso) else "sid"
            self.indirizzo = f"{protocollo}://{self.sottobrano}/{max(1.0, secondi)}/{percorso}"
            self.opzioni.update(_OPZIONI_DEL_FLUSSO)
        elif banco_midi and formati.e_midi(percorso):
            # Un MIDI, con un banco di suoni: lo rende FluidSynth (tappa 8).
            # Senza banco lo legge libmpv da se', come prima della 1.65.0.
            secondi = (midi.durata(percorso) or DURATA_DI_RISERVA_DEL_MIDI) + midi.CODA
            self.indirizzo = f"midi://{secondi}/{percorso}"
            self.opzioni.update(_OPZIONI_DEL_FLUSSO)


class _Lettore:
    """Un'istanza di libmpv, con il suo protocollo sid, e il brano che vi e'
    caricato. I comandi partono tutti in modo asincrono, e restano in fila
    nell'ordine in cui sono partiti.

    Lo stato del brano lo tiene il Motore, sotto il suo lucchetto:
      percorso    il file caricato, None se non c'e' niente o e' finito;
      sottobrano  e sottobrani, per i SID;
      voce        il numero che mpv ha dato al brano caricato (la risposta
                  di loadfile), None finche' non arriva;
      pronto      vero quando il brano e' aperto (FILE_LOADED): solo allora
                  posizione e durata si leggono;
      finito      vero dopo la fine o l'errore del brano: il lettore sta
                  svuotando l'uscita, e non va interrogato.
    Ricorda anche l'ultima catena dei filtri scritta (af_scritto): se e'
    diversa da quella dei guadagni di adesso, il lettore ha avuto bande
    cambiate al volo, che mpv perde quando ricostruisce i filtri."""

    def __init__(self, motore, ao, volume, af, opzioni):
        self._motore = motore
        self.percorso = None
        self.sottobrano = self.sottobrani = None
        self.voce = None
        self.pronto = False
        self.finito = False
        self.volume_scritto = volume
        self.af_scritto = af
        self._avviata = None
        self._richieste = 0
        self.mpv = mpv.MPV(**{**OPZIONI_DI_BASE, "ao": ao, "keep_open": "no", "volume": volume, "volume_max": VOLUME_MASSIMO, "af": af, **opzioni})
        # Il flusso del SID caricato, per sapere quanto e' gia' reso: None
        # finche' mpv non lo apre, e a ogni brano nuovo.
        self.flusso = None
        self.mpv.register_stream_protocol("sid", self._apri_sid)
        self.mpv.register_stream_protocol("midi", self._apri_midi)
        self.mpv.register_stream_protocol("chip", self._apri_chip)
        self.mpv.register_event_callback(functools.partial(motore._evento, self))
        # I .lrc accanto ai brani li legge karaoke.py, con le strofe e senza i
        # tempi per parola: mpv non li carica da se' (1.82.0). Una libmpv
        # senza l'opzione li carica lei, e la traccia c'e' due volte.
        with contextlib.suppress(Exception):
            self.mpv["sub-auto-exts"] = [estensione for estensione in self.mpv["sub-auto-exts"] if estensione != "lrc"]
        # Il testo del karaoke del brano aperto, (fonte, righe), o None; il
        # formato imposto a libmpv per il brano, "wav" per quelli resi in RAM;
        # e se un'aggiunta della sua traccia e' in volo, e se va rifatta
        # quando torna: le aggiunte vanno una alla volta.
        self.karaoke = None
        self.formato_imposto = None
        # La durata vera, quando libmpv la stima male (DURATA_DA_MUTAGEN).
        self.durata_vera = None
        self.karaoke_in_volo = False
        self.karaoke_da_rifare = False
        # L'ultimo sottotitolo di testo visto, se e' arrivato dopo l'ultimo
        # inizio, e l'ultimo inizio: servono a ridire due sottotitoli uguali
        # di fila (1.82.0).
        self.testo_visto = None
        self.testo_nuovo = False
        self.inizio_visto = None

    def _apri_sid(self, uri):
        flusso = _apri_sid(uri)
        self.flusso = flusso
        return flusso

    def _apri_chip(self, uri):
        flusso = _apri_chip(uri)
        self.flusso = flusso
        return flusso

    def _apri_midi(self, uri):
        # midi://<secondi>/<percorso>: il banco e' quello del motore.
        secondi, percorso = uri[len("midi://"):].split("/", 1)
        flusso = midi.apri_flusso(percorso, self._motore.banco_midi, float(secondi))
        self.flusso = flusso
        return flusso

    def comando(self, *argomenti, risposta=None):
        """Un comando di mpv, asincrono. risposta(errore, esito) arriva nel
        filo degli eventi di questo lettore; senza, gli errori si ignorano."""
        if self._motore._chiuso:
            return
        self.mpv.command_async(*argomenti, callback=risposta or (lambda _errore, _esito: None))

    def imposta(self, nome, valore):
        """Una proprieta' di mpv, scritta in modo asincrono."""
        if nome == "volume":
            self.volume_scritto = valore
        elif nome == "af":
            self.af_scritto = valore
        self.comando("set", nome, _testo(valore))

    def carica(self, brano, in_pausa, volume, af):
        """Carica il brano al posto di quello che c'era. Pausa, volume e catena
        dei filtri si scrivono prima: il brano non deve suonare nemmeno un
        istante senza. Di quello che c'era non arrivera' piu' niente."""
        self.percorso = brano.percorso
        self.karaoke = None
        self.durata_vera = None
        self.formato_imposto = brano.opzioni.get("demuxer-lavf-format")
        self.karaoke_in_volo = self.karaoke_da_rifare = False
        self.testo_visto, self.testo_nuovo, self.inizio_visto = None, False, None
        self.sottobrano, self.sottobrani = brano.sottobrano, brano.sottobrani
        self.voce = None
        self.pronto = self.finito = False
        self.flusso = None
        self._richieste += 1
        numero = self._richieste
        self.imposta("pause", in_pausa)
        self.imposta("volume", volume)
        self.imposta("af", af)
        opzioni = ",".join(f"{chiave}={valore}" for chiave, valore in brano.opzioni.items())
        self.comando("loadfile", brano.indirizzo, "replace", "-1", opzioni, risposta=functools.partial(self._motore._caricato, self, numero))

    def aggiungi_testo(self, srt, scelta, titolo, risposta=None):
        """Una traccia di sottotitoli SubRip in memoria, con scelta "auto" o
        "select" (1.82.0); da chiamare con il lucchetto del motore. Un brano
        reso in RAM, SID, MIDI o console, si apre con il formato WAV imposto,
        che vale anche per le tracce aggiunte: libmpv leggerebbe il testo come
        un WAV, e lo rifiuterebbe (banco del 4 ottobre 2026, sui .kar di
        Gabriele). Il formato imposto diventa quello dei sottotitoli, e resta
        cosi' fino al brano dopo, che ha le sue opzioni: questo e' gia' aperto,
        e libmpv non lo riapre. Rimetterlo subito non si puo': sub-add apre il
        file in disparte, e il comando dopo arriverebbe prima. Il lucchetto
        tiene questi comandi prima di un loadfile chiesto intanto, cosi' il
        formato vale per il brano che finisce, non per quello nuovo."""
        if self.formato_imposto:
            self.comando("set", "file-local-options/demuxer-lavf-format", "srt")
        self.comando("sub-add", "memory://" + srt, scelta, titolo, risposta=risposta)

    def ferma(self):
        """Ferma il brano. Di quello che c'era non arrivera' piu' niente."""
        self.percorso = None
        self.sottobrano = self.sottobrani = None
        self.voce = None
        self.pronto = False
        # La musica gia' resa di un SID puo' pesare decine di megabyte: il
        # riferimento si lascia anche qui, non solo al brano dopo (1.62.1).
        self.flusso = None
        self._richieste += 1
        self.comando("stop")

    def leggi(self):
        """Posizione e durata, lette da mpv in modo sincrono: da chiamare
        senza il lucchetto del motore."""
        return self.mpv.time_pos, self.durata_vera or self.mpv.duration

    def chiudi(self):
        self.mpv.terminate()


class _Sfumatura:
    """Una dissolvenza in corso fra chi esce e chi entra. L'avanzamento si
    misura sulla posizione di chi entra, divisa per la velocita': la pausa
    la ferma, e un brano che tarda a partire non la fa cominciare. La durata
    si decide quando chi entra comincia a suonare."""

    def __init__(self, uscente, entrante, ampiezza=1.0):
        self.uscente = uscente
        self.entrante = entrante
        # L'ampiezza di chi esce quando la sfumatura comincia: 1, oppure meno
        # se usciva gia' da un'altra sfumatura.
        self.ampiezza = ampiezza
        self.durata = None
        self.trascorso = 0.0
        self.ultima = None
        # Vero quando un passo ha gia' scritto la voce a zero per chi esce:
        # vedi _passo.
        self.zittita = False

    def avanzamento(self):
        if self.durata is None:
            return 0.0
        return 1.0 if self.durata <= 0 else min(1.0, self.trascorso / self.durata)

    def ampiezze(self):
        """Le ampiezze di chi esce e di chi entra, a potenza costante."""
        angolo = self.avanzamento() * math.pi / 2
        return self.ampiezza * math.cos(angolo), math.sin(angolo)


class _Calo:
    """La voce di un lettore solo che scende fino al silenzio, o sale dal
    silenzio, con la dissolvenza accesa: per lo stop, la pausa e la ripresa
    (Gabriele, 2 ottobre 2026). Come la sfumatura, l'avanzamento si misura
    sulla posizione del brano divisa per la velocita', e la durata si decide
    alla prima lettura: la dissolvenza, ma non oltre cio' che resta al brano."""

    def __init__(self, lettore, sale, ampiezza):
        self.lettore = lettore
        self.sale = sale
        # L'ampiezza da cui parte: 1 a piena voce, 0 dalla pausa, o quella a
        # cui era arrivato un altro calo interrotto.
        self.ampiezza = ampiezza
        self.durata = None
        self.trascorso = 0.0
        self.ultima = None
        # Vero quando un passo ha gia' scritto la voce a zero: vedi
        # _passo_dei_cali.
        self.zittito = False

    def avanzamento(self):
        if self.durata is None:
            return 0.0
        return 1.0 if self.durata <= 0 else min(1.0, self.trascorso / self.durata)

    def ampiezza_ora(self):
        angolo = self.avanzamento() * math.pi / 2
        if self.sale:
            return self.ampiezza + (1.0 - self.ampiezza) * math.sin(angolo)
        return self.ampiezza * math.cos(angolo)


class Motore:
    def __init__(self, alla_fine=None, all_errore=None, ao="wasapi", volume=80, chiedi_il_seguente=None, al_passaggio=None, opzioni_mpv=None,
            al_caricamento=None, ai_sottotitoli=None, ai_sottotitoli_a_immagini=None, al_salto=None):
        """alla_fine() quando un brano finisce da solo e non c'e' un seguente
        preparato, o quando arriva in fondo in pausa, con un salto oltre la
        fine, e allora il preparato si scarta; all_errore(percorso) quando un brano non si puo' aprire o
        si interrompe per un errore; con la dissolvenza accesa,
        chiedi_il_seguente() quando mancano la durata della dissolvenza piu'
        ANTICIPO_DEL_SEGUENTE secondi alla fine del brano (chi lo riceve
        risponde con prepara, o non risponde se non c'e' altro da suonare),
        e al_passaggio(percorso, sottobrano) quando il brano preparato entra,
        con la sfumatura o, se e' stato pronto troppo tardi, alla fine di
        quello di prima. Gli avvisi arrivano dai fili del motore.
        opzioni_mpv: altre opzioni di mpv, uguali per i due lettori; servono
        alle prove (ao_pcm_file e simili).
        Dalla tappa 7: al_caricamento() quando un lettore ha aperto il suo
        brano, e se ne possono leggere le tracce; ai_sottotitoli(testo) a
        ogni sottotitolo nuovo del brano in corso. Dalla 1.80.0
        ai_sottotitoli_a_immagini() quando comincia un sottotitolo del brano in
        corso, anche di una traccia a immagini, che testo non ne ha. Dalla
        1.83.0 al_salto() a ogni suona, stop e salto, nel filo di chi li
        chiede: i testi in fila per il braille non valgono piu'."""
        self._alla_fine = alla_fine
        self._all_errore = all_errore
        self._chiedi_il_seguente = chiedi_il_seguente
        self._al_passaggio = al_passaggio
        self._al_caricamento = al_caricamento
        self._ai_sottotitoli = ai_sottotitoli
        self._ai_sottotitoli_a_immagini = ai_sottotitoli_a_immagini
        self._al_salto = al_salto
        # Le finestre del video, o None a video spento; e se il video va
        # decodificato anche spento, perche' si leggono i suoi sottotitoli
        # fatti di immagini (1.80.0).
        self._finestre = None
        self._video_da_leggere = False
        self._oscura = False
        self._blocco = threading.RLock()
        self._sveglia = threading.Condition(self._blocco)
        self._riposo = threading.Event()
        self._chiuso = False
        self._volume = _fra(volume, 0, VOLUME_MASSIMO)
        self._muto = False
        self._pausa = False
        self._dispositivo = "auto"
        self._velocita = 1.0
        self._tono = 0
        self._bande = [0] * len(valori.FREQUENZE_DELLE_BANDE)
        self._dissolvenza = 0.0
        # L'attenuazione (1.95.0), un'ampiezza da 1 a 0 sopra il volume e le
        # sfumature, per tutti i lettori: la usa il timer di spegnimento.
        self._attenuazione = 1.0
        self._replaygain = "spento"
        # Il banco di suoni dei MIDI, None finche' la finestra non lo sceglie.
        self._banco_midi = None
        # Il testo del karaoke: per riga o per strofa, e l'anticipo in secondi.
        self._karaoke = ("riga", 0.0)
        self._uscente = None
        self._preparato = None
        self._sfumatura = None
        # Il calo dell'attivo verso la pausa, o la sua salita dopo la ripresa;
        # e la coda di un brano fermato con lo stop, che si spegne sull'altro
        # lettore mentre l'attivo e' gia' libero.
        self._calo = None
        self._coda = None
        self._chiesto = False
        # Cresce a ogni cambio di stato: il sorvegliante, che legge mpv senza
        # il lucchetto, scarta le letture fatte nel frattempo.
        self._generazione = 0
        lettori = []
        try:
            for _ in range(2):
                lettori.append(_Lettore(self, ao, self._volume, catena_dei_filtri(self._bande), opzioni_mpv or {}))
        except Exception:
            # Un lettore con il protocollo registrato e mai chiuso manda
            # Python in crash all'uscita.
            for lettore in lettori:
                lettore.chiudi()
            raise
        self._lettori = tuple(lettori)
        self._attivo = self._lettori[0]
        for lettore in self._lettori:
            lettore.mpv.observe_property("sub-text", functools.partial(self._sottotitolo, lettore))
            lettore.mpv.observe_property("sub-start", functools.partial(self._sottotitolo_a_immagini, lettore))
        self._sorvegliante = threading.Thread(target=self._sorveglia, name="MeTeOra, dissolvenza", daemon=True)
        self._sorvegliante.start()
        sid.riscalda()

    # Gli eventi dei lettori, nei loro fili.

    def _caricato(self, lettore, numero, errore, esito):
        """La risposta di loadfile: il numero del brano per mpv."""
        avviso = None
        with self._blocco:
            if self._chiuso or numero != lettore._richieste:
                return
            if errore is None and isinstance(esito, dict):
                lettore.voce = esito.get("playlist_entry_id")
                return
            avviso = self._fine_del_brano(lettore, _FINE_PER_ERRORE)
        if avviso:
            avviso()

    def _evento(self, lettore, evento):
        identita = evento.event_id.value
        if identita not in _EVENTI_UTILI:
            return
        avviso = None
        with self._blocco:
            if self._chiuso:
                return
            if identita == mpv.MpvEventID.START_FILE:
                lettore._avviata = evento.data.playlist_entry_id
            elif identita == mpv.MpvEventID.FILE_LOADED:
                if lettore.voce is not None and lettore._avviata == lettore.voce:
                    lettore.pronto = True
                    self._cambiato()
                    # Le tracce aggiunte da MeTeOra, i file delle passate dei
                    # video e il testo del karaoke, prima dell'avviso, che
                    # legge le tracce; e fuori dal blocco, perche' leggere in
                    # una cartella di rete puo' far aspettare.
                    avviso = functools.partial(self._aggiungi_le_tracce, lettore, lettore.percorso, lettore._richieste, self._al_caricamento)
            elif identita == mpv.MpvEventID.END_FILE:
                # Un brano sostituito o fermato finisce con il motivo STOP; e la
                # fine di un brano gia' sostituito da un altro non conta.
                motivo = evento.data.reason
                if motivo in (_FINE_NORMALE, _FINE_PER_ERRORE) and lettore.voce is not None and evento.data.playlist_entry_id == lettore.voce:
                    avviso = self._fine_del_brano(lettore, motivo)
            elif identita == mpv.MpvEventID.AUDIO_RECONFIG:
                # mpv ha riaperto l'uscita o rifatto i filtri, anche da se':
                # quando Windows cambia la scheda predefinita, o la scheda
                # cambia formato o sparisce. I filtri ripartono dalla catena
                # scritta, e le bande cambiate al volo dopo l'ultima scrittura
                # si perdono: se ce ne sono, la catena si riscrive con i
                # guadagni di adesso, sempre in modo asincrono. La
                # riscrittura manda un altro AUDIO_RECONFIG, che trova la
                # catena gia' uguale: nessun giro senza fine.
                catena = self._catena()
                if lettore.percorso is not None and lettore.af_scritto != catena:
                    lettore.imposta("af", catena)
        if avviso:
            avviso()

    def _fine_del_brano(self, lettore, motivo):
        """Un brano finito da solo o per un errore: restituisce l'avviso da dare
        fuori dal lucchetto, o None."""
        percorso = lettore.percorso
        lettore.percorso = None
        lettore.voce = None
        lettore.pronto = False
        lettore.finito = True
        self._cambiato()
        if self._coda is not None and lettore is self._coda.lettore:
            # La coda di uno stop, arrivata in fondo prima di spegnersi.
            self._coda = None
            return None
        if self._calo is not None and lettore is self._calo.lettore:
            self._calo = None
        if lettore is self._preparato:
            # Il preparato in errore si scarta: il passaggio avverra' senza
            # dissolvenza, e il brano dara' l'errore quando la finestra lo
            # chiedera' di nuovo.
            self._preparato = None
            return None
        if lettore is not self._attivo:
            # Chi esce, finito prima del previsto: la sfumatura continua.
            return None
        if self._sfumatura is not None:
            # Chi entra non c'e' piu': si ferma anche chi usciva.
            self._chiudi_la_sfumatura()
        if motivo == _FINE_PER_ERRORE:
            return functools.partial(self._all_errore, percorso) if self._all_errore else None
        if self._preparato is not None and self._pausa:
            # In pausa il brano arriva in fondo solo con un salto oltre la
            # fine: come senza la dissolvenza, il preparato si scarta e si
            # dice la fine, e il seguente lo sceglie chi riceve alla_fine.
            self._scarta_il_preparato()
        if self._preparato is not None:
            return self._passa_al_preparato(sfumando=False)
        return self._alla_fine

    # Il brano in corso.

    @property
    def in_corso(self):
        """Il file caricato, anche se in pausa; None dopo stop, a fine brano
        o dopo un errore."""
        return self._attivo.percorso

    @property
    def _in_corso(self):
        # Le prove della finestra, con il loro motore finto, scrivono qui il
        # file in corso.
        return self._attivo.percorso

    @_in_corso.setter
    def _in_corso(self, valore):
        self._attivo.percorso = valore

    @property
    def sottobrano(self):
        """Il sottobrano che suona, per i SID e le console; None per gli altri file."""
        return self._attivo.sottobrano

    @sottobrano.setter
    def sottobrano(self, valore):
        self._attivo.sottobrano = valore

    @property
    def sottobrani(self):
        """Quanti sottobrani ha il SID che suona; None per gli altri file."""
        return self._attivo.sottobrani

    @sottobrani.setter
    def sottobrani(self, valore):
        self._attivo.sottobrani = valore

    def suona(self, percorso, sottobrano=None, inizio=None, in_pausa=False, sfuma_lo_stesso=False, a_volume_pieno=False):
        """Avvia un file, dall'inizio o dai secondi inizio, e in pausa se
        chiesto. Per i SID suona il sottobrano chiesto, o quello iniziale,
        con la durata dal database della collezione.
        Con la dissolvenza accesa, se qualcosa si sente, il brano nuovo parte
        sull'altro lettore a volume zero e sale mentre il vecchio scende. Se
        due brani si sentono gia', perche' una sfumatura e' in corso, il piu'
        debole si ferma subito e il piu' forte esce dal punto in cui e'.
        Ripartire con il brano in corso, stesso file e stesso sottobrano, non
        sfuma, a meno di sfuma_lo_stesso: senza, e' un salto dentro il
        brano. Vale anche durante una sfumatura, per il brano che entra,
        appena entrato o quasi alla fine: chi esce si ferma, come a un salto,
        e il brano riparte a piena voce, su un lettore solo. Con
        sfuma_lo_stesso, per X da capo e per i marker con la dissolvenza
        accesa (Gabriele, 2 ottobre 2026), lo stesso brano riparte dal punto
        chiesto sull'altro lettore e i due punti si incrociano.
        Con a_volume_pieno l'attenuazione torna a 1 per il brano nuovo, e chi
        esce sfumando parte dal punto in cui lei lo aveva portato: un brano
        scelto mentre il timer sfumava (1.96.11)."""
        if self._al_salto is not None:
            self._al_salto()
        brano = _Brano(percorso, sottobrano, inizio, self._banco_midi)
        with self._blocco:
            if self._chiuso:
                return
            attivo = self._attivo
            stesso = attivo.percorso == percorso and attivo.sottobrano == brano.sottobrano and not sfuma_lo_stesso
            si_sente = self._sfumatura is not None or (attivo.percorso is not None and attivo.pronto and not attivo.finito)
            sfuma = self._dissolvenza > 0 and not in_pausa and not self._pausa and si_sente and not stesso
            self._pausa = bool(in_pausa)
            self._chiesto = False
            self._scarta_il_preparato()
            attenuazione = 1.0
            if a_volume_pieno:
                attenuazione, self._attenuazione = self._attenuazione, 1.0
            if not sfuma:
                self._calo = None
                self._chiudi_la_sfumatura()
                attivo.carica(brano, self._pausa, self._volume_attenuato(), self._catena())
            else:
                uscente, ampiezza = self._chi_esce()
                ampiezza *= attenuazione
                entrante = self._altro(uscente)
                self._lascia_la_coda(entrante)
                if entrante.percorso is not None:
                    entrante.ferma()
                entrante.carica(brano, False, 0, self._catena())
                self._attivo = entrante
                self._uscente = uscente
                self._sfumatura = _Sfumatura(uscente, entrante, ampiezza)
            self._cambiato()

    def _chi_esce(self):
        """Chi esce dalla sfumatura che comincia, e con quale ampiezza: l'attivo
        a piena voce, o, se una sfumatura e' gia' in corso, quello dei due che
        si sente di piu', dal punto in cui e'."""
        s = self._sfumatura
        if s is None:
            # Un calo in corso, verso la pausa o in salita dalla ripresa: chi
            # esce parte dal punto in cui era arrivato.
            ampiezza = self._calo.ampiezza_ora() if self._calo is not None else 1.0
            self._calo = None
            return self._attivo, ampiezza
        self._sfumatura = None
        self._uscente = None
        ampiezza_uscente, ampiezza_entrante = s.ampiezze()
        if ampiezza_entrante > ampiezza_uscente or s.uscente.finito or s.uscente.percorso is None:
            s.uscente.ferma()
            return s.entrante, ampiezza_entrante
        s.entrante.ferma()
        return s.uscente, ampiezza_uscente

    def prepara(self, percorso, sottobrano=None):
        """Il brano seguente, per il passaggio con la dissolvenza: si carica
        sull'altro lettore, in pausa e a volume zero, ed entrera' da solo
        quando manca la durata della dissolvenza alla fine di quello in
        corso. Vale solo con la dissolvenza accesa, un brano in corso e
        nessuna sfumatura in corso; torna vero se il brano e' stato preso."""
        brano = _Brano(percorso, sottobrano, banco_midi=self._banco_midi)
        with self._blocco:
            attivo = self._attivo
            if self._chiuso or not self._dissolvenza or self._sfumatura is not None or attivo.percorso is None or attivo.finito:
                return False
            if self._preparato is not None:
                if self._preparato.percorso == percorso and self._preparato.sottobrano == brano.sottobrano:
                    return True
                self._scarta_il_preparato()
            self._preparato = self._altro(attivo)
            self._lascia_la_coda(self._preparato)
            self._preparato.carica(brano, True, 0, self._catena())
            self._chiesto = True
            self._cambiato()
            return True

    @property
    def in_pausa(self):
        return self._pausa

    def pausa(self, valore=None, sfumando=False):
        """Mette o toglie la pausa; senza valore la inverte. Torna il nuovo
        stato. Durante una sfumatura vale per tutti e due i brani.
        Con sfumando e la dissolvenza accesa, fuori da una sfumatura e con un
        brano che si sente, la pausa arriva dopo che la voce e' scesa fino al
        silenzio, e la ripresa riparte dal silenzio e risale; in_pausa dice
        subito il nuovo stato. Una ripresa durante la discesa risale dal
        punto in cui era arrivata."""
        with self._blocco:
            nuova = (not self._pausa) if valore is None else bool(valore)
            attivo = self._attivo
            si_sente = attivo.percorso is not None and attivo.pronto and not attivo.finito
            if sfumando and self._dissolvenza > 0 and self._sfumatura is None and si_sente and nuova != self._pausa:
                self._pausa = nuova
                if nuova:
                    self._calo = _Calo(attivo, False, self._calo.ampiezza_ora() if self._calo is not None else 1.0)
                else:
                    if self._calo is not None:
                        partenza = self._calo.ampiezza_ora()
                    else:
                        # Dalla pausa vera: si riparte muti.
                        partenza = 0.0
                        self._scrivi_il_volume(attivo, 0)
                        attivo.imposta("pause", False)
                    self._calo = _Calo(attivo, True, partenza)
                self._applica_i_volumi()
                self._cambiato()
                return self._pausa
            self._pausa = nuova
            self._calo = None
            self._applica_i_volumi()
            for lettore in self._suonanti():
                lettore.imposta("pause", self._pausa)
            self._cambiato()
            return self._pausa

    def stop(self, sfumando=False):
        """Ferma tutto: il brano, chi esce e il preparato.
        Con sfumando e la dissolvenza accesa, fuori da una sfumatura e con un
        brano che si sente, il brano si spegne piano sull'altro lettore,
        come coda, e il motore e' subito libero: in_corso vale None, e un
        brano avviato intanto parte senza aspettare la coda."""
        if self._al_salto is not None:
            self._al_salto()
        with self._blocco:
            attivo = self._attivo
            si_sente = attivo.percorso is not None and attivo.pronto and not attivo.finito and not self._pausa
            if sfumando and self._dissolvenza > 0 and self._sfumatura is None and si_sente:
                ampiezza = self._calo.ampiezza_ora() if self._calo is not None else 1.0
                self._calo = None
                self._scarta_il_preparato()
                altro = self._altro(attivo)
                self._lascia_la_coda(altro)
                if altro.percorso is not None:
                    altro.ferma()
                self._coda = _Calo(attivo, False, ampiezza)
                self._attivo = altro
                self._chiesto = False
                self._cambiato()
                return
            self._calo = None
            self._chiudi_la_coda()
            self._chiudi_la_sfumatura()
            self._scarta_il_preparato()
            self._attivo.ferma()
            self._chiesto = False
            self._applica_i_volumi()
            self._cambiato()

    def lascia_il_file(self, percorso):
        """Lascia il file, che sta per cambiare nome: un seguente preparato
        con quel file si scarta, e si richiedera'; se lo tengono il brano in
        corso, chi esce o la coda di uno stop, si ferma tutto. mpv chiude il
        file poco dopo, nel suo filo (Rinomina file, 1.67.0)."""
        def suo(lettore):
            return lettore is not None and lettore.percorso and os.path.normcase(lettore.percorso) == os.path.normcase(percorso)

        with self._blocco:
            if self._preparato is not None and suo(self._preparato):
                self._scarta_il_preparato()
                self._chiesto = False
            fermare = suo(self._attivo)
            if not fermare:
                # Chi esce da una dissolvenza, o la coda di uno stop sfumato,
                # si chiude da solo: il brano che entra continua.
                if self._sfumatura is not None and suo(self._uscente):
                    self._chiudi_la_sfumatura()
                if self._coda is not None and suo(self._coda.lettore):
                    self._chiudi_la_coda()
        if fermare:
            self.stop()

    def rinomina_il_file(self, vecchio, nuovo):
        """Un file che suona dalla memoria, come un SID, un MIDI o un brano
        delle console, ha cambiato nome mentre suonava: i lettori che lo
        hanno lo chiamano con il nome nuovo."""
        with self._blocco:
            for lettore in self._lettori:
                if lettore.percorso and os.path.normcase(lettore.percorso) == os.path.normcase(vecchio):
                    lettore.percorso = nuovo

    def annulla_il_passaggio(self):
        """Rinuncia al passaggio appena cominciato, per chi al ricontrollo non
        trova piu' un seguente: chi entra si ferma, e chi esce torna il brano
        in corso, a piena voce, e finisce da solo, con il suo alla_fine. Il
        seguente non si chiede di nuovo. Se chi esce e' gia' finito, o fermo,
        o il passaggio e' avvenuto senza sfumatura, si ferma tutto come con
        stop. Torna vero se chi esce continua."""
        with self._blocco:
            if self._chiuso:
                return False
            s = self._sfumatura
            if s is None or s.entrante is not self._attivo or s.uscente.finito or s.uscente.percorso is None:
                self.stop()
                return False
            s.entrante.ferma()
            self._attivo = s.uscente
            self._uscente = self._sfumatura = None
            self._applica_i_volumi()
            self._attivo.imposta("pause", self._pausa)
            self._chiesto = True
            self._cambiato()
            return True

    def salta(self, secondi):
        """Avanti (positivo) o indietro (negativo) nel brano."""
        self._seek(secondi, "relative")

    def vai_a(self, secondi):
        self._seek(secondi, "absolute")

    def _seek(self, secondi, riferimento):
        if self._al_salto is not None:
            self._al_salto()
        # Un salto chiude la sfumatura: chi esce si ferma, chi entra torna a
        # piena voce. La catena si riscrive prima: il seek perde i guadagni
        # dati al volo.
        with self._blocco:
            self._chiudi_la_sfumatura()
            self._chiudi_il_calo()
            if self._preparato is None:
                self._chiesto = False
            self._attivo.imposta("af", self._catena())
            self._attivo.comando("seek", str(secondi), riferimento, "exact")
            self._cambiato()

    # Il video e i sottotitoli, tappa 7.

    def _sottotitolo(self, lettore, _nome, testo):
        """sub-text di un lettore, nel suo filo: conta solo quello del brano
        in corso, e non vuoto."""
        with self._blocco:
            if self._chiuso or lettore is not self._attivo:
                return
            lettore.testo_visto, lettore.testo_nuovo = testo, True
        if testo and self._ai_sottotitoli is not None:
            self._ai_sottotitoli(testo)

    def _sottotitolo_a_immagini(self, lettore, _nome, inizio):
        """sub-start di un lettore: un sottotitolo comincia. Conta solo per il
        brano in corso; serve alle tracce a immagini, che sub-text non hanno.
        E ridice un sottotitolo di testo uguale a quello di prima, come un
        ritornello ripetuto, perche' sub-text, che non cambia, non lo dice
        (1.82.0), se quello di prima e' cominciato almeno RIPETIZIONE_MINIMA
        secondi prima. sub-text si osserva prima di sub-start, e mpv avvisa
        dei cambi nell'ordine delle osservazioni: un testo nuovo arriva sempre
        prima del suo inizio (banco del 4 ottobre 2026)."""
        with self._blocco:
            if self._chiuso or lettore is not self._attivo:
                return
            ripeti = None
            if inizio is not None:
                if not lettore.testo_nuovo and lettore.inizio_visto is not None and inizio - lettore.inizio_visto >= RIPETIZIONE_MINIMA:
                    ripeti = lettore.testo_visto
                lettore.inizio_visto = inizio
            lettore.testo_nuovo = False
        if inizio is not None and self._ai_sottotitoli_a_immagini is not None:
            self._ai_sottotitoli_a_immagini()
        if ripeti and self._ai_sottotitoli is not None:
            self._ai_sottotitoli(ripeti)

    def resto_del_sottotitolo(self):
        """I secondi d'orologio che restano al sottotitolo mostrato adesso dal
        brano in corso, contando la velocita', o None se non si sa: servono
        alla barra braille a blocchi, per dividerli fra i blocchi (1.83.0)."""
        with self._blocco:
            lettore = self._attivo
            if self._chiuso or lettore.percorso is None or not lettore.pronto:
                return None
            velocita = self._velocita
        # Le proprieta' si leggono come attributi: le parentesi quadre di
        # python-mpv leggono le opzioni.
        try:
            fine, ora = lettore.mpv.sub_end, lettore.mpv.time_pos
        except Exception:  # noqa: BLE001 - un lettore che si chiude, o niente sottotitolo
            return None
        if fine is None or ora is None or fine <= ora:
            return None
        return (fine - ora) / max(velocita, 0.01)

    def _aggiungi_le_passate(self, lettore, video, numero, poi=None):
        """Un video appena aperto, il caricamento numero del lettore: i file
        .srt delle passate dei sottotitoli impressi fatte prima, accanto a
        lui, diventano tracce, senza sceglierle; poi(), se c'e', arriva quando
        mpv le ha aggiunte, cosi' chi legge le tracce le trova. Nel filo degli
        eventi del lettore, fuori dal blocco; un video ricaricato intanto non
        prende le passate di questo caricamento (revisione della 1.83.0)."""
        import sottotitoli_ocr

        passate = sottotitoli_ocr.passate_esistenti(video) if formati.e_video(video or "") else []
        with self._blocco:
            if passate and lettore._richieste == numero and not self._chiuso:
                for posto, percorso in enumerate(passate, 1):
                    lingua = os.path.splitext(percorso)[0].rsplit(".", 1)[-1]
                    risposta = (lambda _errore, _esito: poi()) if poi is not None and posto == len(passate) else None
                    lettore.comando("sub-add", percorso, "auto", "Sottotitoli impressi", lingua, risposta=risposta)
                return
        if poi is not None:
            poi()

    def _aggiungi_le_tracce(self, lettore, percorso, numero, poi=None):
        """Un brano appena aperto, il caricamento numero del lettore: ai video
        i file delle passate, e poi a tutti il testo del karaoke, anche a un
        video musicale o a un audio .webm con il suo .lrc accanto, che mpv non
        carica piu' da se'; poi(), se c'e', quando mpv li ha aggiunti. Prima
        la durata vera dei formati che libmpv stima male, cosi' chi legge la
        durata dopo l'avviso la trova gia' giusta."""
        if os.path.splitext(percorso or "")[1].lower() in DURATA_DA_MUTAGEN:
            durata = _durata_da_mutagen(percorso)
            with self._blocco:
                if lettore._richieste == numero:
                    lettore.durata_vera = durata
        if formati.e_video(percorso or ""):
            self._aggiungi_le_passate(lettore, percorso, numero, functools.partial(self._aggiungi_il_karaoke, lettore, percorso, numero, poi))
        else:
            self._aggiungi_il_karaoke(lettore, percorso, numero, poi)

    def _aggiungi_il_karaoke(self, lettore, percorso, numero, poi=None):
        """Il testo a tempo di un brano appena aperto, se c'e', diventa la
        traccia del karaoke, senza sceglierla: la sceglie la finestra, come
        i sottotitoli (1.82.0). poi(), se c'e', arriva quando mpv l'ha
        aggiunta. Nel filo degli eventi del lettore, fuori dal blocco: la
        ricerca puo' aspettare una cartella di rete."""
        fonte, righe = karaoke.cerca(percorso) if percorso else (None, [])
        with self._blocco:
            # Un brano ricaricato intanto, anche lo stesso, non prende il
            # testo di questo caricamento: lo mette il suo.
            if fonte is not None and lettore._richieste == numero and not self._chiuso:
                lettore.karaoke = (fonte, righe)
                self._manda_il_karaoke(lettore, numero, poi)
                return
        if poi is not None:
            poi()

    def _manda_il_karaoke(self, lettore, numero, poi=None):
        """Con il lucchetto: aggiunge la traccia del karaoke del lettore, con
        il modo e l'anticipo di adesso, senza sceglierla. Le aggiunte vanno
        una alla volta: sub-add apre il testo in disparte, e due aggiunte
        insieme lascerebbero due tracce, una con l'anticipo vecchio."""
        fonte, righe = lettore.karaoke
        lettore.karaoke_in_volo = True
        lettore.aggiungi_testo(karaoke.traccia(righe, *self._karaoke), "auto", karaoke.titolo(fonte),
            risposta=functools.partial(self._karaoke_aggiunto, lettore, numero, poi))

    def _karaoke_aggiunto(self, lettore, numero, poi, _errore, _esito):
        """La risposta di sub-add della traccia del karaoke, nel filo degli
        eventi del lettore. Resta solo l'ultima traccia del karaoke, quella
        appena aggiunta, perche' le aggiunte vanno una alla volta e mpv da'
        numeri crescenti; se una vecchia era scelta, la scelta passa alla
        nuova. Se intanto un'impostazione e' cambiata, la traccia si rifa'."""
        with self._blocco:
            stesso = lettore._richieste == numero and not self._chiuso
            if stesso:
                lettore.karaoke_in_volo = False
        if stesso:
            try:
                tracce = lettore.mpv.track_list or []
            except (mpv.ShutdownError, SystemError, RuntimeError, ValueError, TypeError, AttributeError):
                tracce = []
            mie = [t for t in tracce if t.get("type") == "sub" and (t.get("title") or "").startswith(karaoke.TITOLO)]
            with self._blocco:
                if lettore._richieste == numero and not self._chiuso:
                    if len(mie) > 1:
                        ultima = max(mie, key=lambda traccia: traccia["id"])
                        vecchie = [t for t in mie if t is not ultima]
                        for vecchia in vecchie:
                            lettore.comando("sub-remove", str(vecchia["id"]))
                        if any(t.get("selected") for t in vecchie):
                            lettore.comando("set", "sid", str(ultima["id"]))
                    if lettore.karaoke_da_rifare and lettore.karaoke is not None:
                        lettore.karaoke_da_rifare = False
                        self._manda_il_karaoke(lettore, numero)
        if poi is not None:
            poi()

    def imposta_il_karaoke(self, modo, anticipo):
        """Il testo del karaoke per riga o per strofa, una chiave di
        karaoke.MODI, e quanti millesimi prima del canto (1.82.0). Le tracce
        del karaoke dei brani aperti si rifanno, e quella scelta resta
        scelta: la riga dopo arriva gia' con il modo e l'anticipo nuovi. Una
        traccia ancora in arrivo si rifa' quando arriva."""
        with self._blocco:
            nuovo = (modo, anticipo / 1000)
            if nuovo == self._karaoke:
                return
            self._karaoke = nuovo
            for lettore in self._lettori:
                if lettore.karaoke is None or not lettore.pronto:
                    continue
                if lettore.karaoke_in_volo:
                    lettore.karaoke_da_rifare = True
                else:
                    self._manda_il_karaoke(lettore, lettore._richieste)

    def aggiungi_sottotitoli(self, percorso, titolo, lingua, scegli=True):
        """Un file di sottotitoli aggiunto al brano in corso come traccia, e
        scelto se scegli: e' il file appena scritto dalla passata."""
        with self._blocco:
            self._attivo.comando("sub-add", percorso, "select" if scegli else "auto", titolo, lingua)

    def imposta_il_video(self, finestre):
        """finestre: le maniglie delle due finestre, una per lettore, in cui
        libmpv disegna; None spegne il video, e dei brani si sente solo
        l'audio. Le uscite si scelgono qui, a brano anche gia' partito:
        finche' il video resta spento libmpv non apre niente."""
        with self._blocco:
            self._finestre = finestre
            self._applica_il_video()

    def leggi_il_video(self, serve, oscura=False):
        """Vero quando si leggono i sottotitoli fatti di immagini: allora il
        video si decodifica anche spento, senza finestra, per le foto
        (1.80.0). Con oscura, per le tracce a immagini, il fotogramma a video
        spento diventa nero, e una foto con i sottotitoli ha solo le loro
        lettere: due foto, con e senza, non erano mai dello stesso fotogramma."""
        with self._blocco:
            self._video_da_leggere = serve
            self._oscura = serve and oscura
            self._applica_il_video()

    @property
    def video_oscurato(self):
        with self._blocco:
            return self._finestre is None and self._video_da_leggere and self._oscura

    def _applica_il_video(self):
        for indice, lettore in enumerate(self._lettori):
            if self._finestre is not None:
                # La finestra prima dell'uscita: con l'uscita prima, mpv ne
                # aprirebbe una sua.
                lettore.imposta("vf", "")
                lettore.imposta("wid", str(self._finestre[indice]))
                lettore.imposta("vo", "gpu")
                lettore.imposta("vid", "auto")
            elif self._video_da_leggere:
                lettore.imposta("vf", FILTRO_DEL_NERO if self._oscura else "")
                lettore.imposta("vo", "null")
                lettore.imposta("vid", "auto")
            else:
                lettore.imposta("vf", "")
                lettore.imposta("vid", "no")

    def foto(self, con_i_sottotitoli):
        """Il fotogramma del brano in corso come immagine di Pillow, con i
        sottotitoli disegnati o senza; None se non c'e'. Da un filo a parte."""
        with self._blocco:
            lettore = self._attivo
            if self._chiuso or lettore.percorso is None or not lettore.pronto:
                return None
        try:
            return lettore.mpv.screenshot_raw(includes="subtitles" if con_i_sottotitoli else "video")
        except Exception:  # noqa: BLE001 - un video che non ha ancora un fotogramma, o un lettore che si chiude
            return None

    def indice_attivo(self):
        """0 o 1: il lettore del brano in corso, quello da mostrare."""
        with self._blocco:
            return self._lettori.index(self._attivo)

    def tracce(self):
        """Le tracce del brano in corso: {"video": vero se ne ha una,
        "audio": [...], "sub": [...]}, ciascuna come la da' track-list di
        mpv (id, selected, title, lang, codec...). None se non c'e' un brano
        aperto."""
        with self._blocco:
            lettore = self._attivo
            if lettore.percorso is None or not lettore.pronto:
                return None
        try:
            elenco = lettore.mpv.track_list or []
        except (mpv.ShutdownError, SystemError, RuntimeError, ValueError, TypeError, AttributeError):
            return None
        tracce = {"video": False, "audio": [], "sub": []}
        for traccia in elenco:
            tipo = traccia.get("type")
            if tipo == "video" and not traccia.get("albumart"):
                tracce["video"] = True
            elif tipo in ("audio", "sub"):
                tracce[tipo].append(traccia)
        return tracce

    def scegli_traccia(self, tipo, numero):
        """tipo "aid" o "sid": la traccia audio o dei sottotitoli del brano in
        corso, per numero, o "no" per nessuna."""
        with self._blocco:
            self._attivo.imposta(tipo, numero)

    def rapporto(self, valore):
        """Il rapporto dell'immagine, per i due lettori: "-1" quello del file,
        altrimenti per esempio "16:9"."""
        with self._blocco:
            for lettore in self._lettori:
                lettore.imposta("video-aspect-override", valore)

    def attesa_del_sid(self, secondi):
        """Se il brano in corso e' un SID, quanti secondi mancano, circa,
        perche' il punto dato sia reso; zero per gli altri brani. Un SID
        appena caricato, che mpv non ha ancora aperto, si stima dall'inizio
        (tappa 5, 1.62.0)."""
        with self._blocco:
            lettore = self._attivo
            reso = lettore.sottobrano is not None or (self._banco_midi and formati.e_midi(lettore.percorso or ""))
            if lettore.percorso is None or not reso:
                return 0.0
            flusso = lettore.flusso
        if flusso is None:
            stimata = sid.VELOCITA_STIMATA if lettore.sottobrano is not None else midi.VELOCITA_STIMATA
            return secondi / stimata
        return flusso.brano.attesa(secondi)

    @property
    def banco_midi(self):
        """Il banco di suoni con cui FluidSynth rende i MIDI; None, e i MIDI
        li legge libmpv da se'. Vale dal brano dopo."""
        return self._banco_midi

    @banco_midi.setter
    def banco_midi(self, banco):
        with self._blocco:
            self._banco_midi = banco or None
        if midi.fluidsynth_presente():
            midi.svuota_la_scorta(tranne=banco)

    @property
    def posizione(self):
        """I secondi del brano in corso, o None se non c'e' o non e' ancora aperto."""
        lettore = self._attivo
        if not lettore.pronto or lettore.finito:
            return None
        return lettore.mpv.time_pos

    @property
    def durata(self):
        """La durata del brano in corso, o None se non c'e' o non si sa ancora."""
        lettore = self._attivo
        if not lettore.pronto or lettore.finito:
            return None
        return lettore.durata_vera or lettore.mpv.duration

    def capitoli(self):
        """I capitoli del brano in corso come li vede libmpv: [(secondi,
        titolo)], vuota se non ne ha (1.93.0)."""
        lettore = self._attivo
        if not lettore.pronto or lettore.finito:
            return []
        try:
            elenco = lettore.mpv.chapter_list or []
        except Exception:  # noqa: BLE001 - un lettore che si chiude intanto non ha capitoli
            return []
        return [(float(c.get("time") or 0.0), str(c.get("title") or "").strip()) for c in elenco if isinstance(c, dict)]

    # Volume, muto e scheda: li ricorda il motore.

    @property
    def volume(self):
        return round(self._volume)

    @volume.setter
    def volume(self, valore):
        with self._blocco:
            self._volume = _fra(valore, 0, VOLUME_MASSIMO)
            self._applica_i_volumi()

    @property
    def attenuazione(self):
        """L'ampiezza da 1, piena, a 0, il silenzio, che abbassa tutto senza
        toccare il volume: la sfumatura del timer di spegnimento (1.95.0)."""
        return self._attenuazione

    @attenuazione.setter
    def attenuazione(self, valore):
        with self._blocco:
            self._attenuazione = _fra(float(valore), 0.0, 1.0)
            self._applica_i_volumi()

    def _volume_attenuato(self):
        # La legge del volume di mpv e' cubica: vedi _applica_i_volumi.
        return self._volume * self._attenuazione ** (1 / 3)

    @property
    def replaygain(self):
        """Il volume uniforme, una chiave di REPLAYGAIN_DI_MPV: spento, per
        brano o per album, dai tag ReplayGain; i file senza restano come sono."""
        return self._replaygain

    @replaygain.setter
    def replaygain(self, valore):
        with self._blocco:
            self._replaygain = valore if valore in REPLAYGAIN_DI_MPV else "spento"
            for lettore in self._lettori:
                lettore.imposta("replaygain", REPLAYGAIN_DI_MPV[self._replaygain])

    @property
    def muto(self):
        return self._muto

    @muto.setter
    def muto(self, valore):
        with self._blocco:
            self._muto = bool(valore)
            for lettore in self._lettori:
                lettore.imposta("mute", self._muto)

    @property
    def dispositivo(self):
        """L'uscita audio della musica, col nome che le da' mpv: "auto",
        il valore di partenza, segue la scheda predefinita di Windows;
        "wasapi/{...}" e' una scheda precisa, presa da dispositivi().
        mpv accetta in scrittura anche un nome che non esiste, e se ne
        accorge solo quando apre il suono: chi scrive lo prende dall'elenco.
        Scritta durante la riproduzione, mpv riapre l'uscita sulla scheda
        nuova, su tutti e due i lettori. Dice la scheda chiesta, non quella
        che suona davvero."""
        return self._dispositivo

    @dispositivo.setter
    def dispositivo(self, nome):
        with self._blocco:
            self._dispositivo = nome or "auto"
            for lettore in self._lettori:
                # Riaprendo l'uscita mpv riparte dalla catena scritta: i
                # guadagni dati al volo si perderebbero.
                lettore.imposta("af", self._catena())
                lettore.imposta("audio-device", self._dispositivo)

    def dispositivi(self):
        """Le uscite audio che mpv conosce: una lista di dizionari con name,
        il nome da scrivere in dispositivo, e description, quello leggibile.
        Ci sono anche le uscite degli altri driver di mpv, per esempio
        openal, e la voce "auto".
        Attenzione, fatto verificato: se la si legge prima che sounddevice
        sia importato per la prima volta, PortAudio perde le uscite ASIO.
        Chi la legge chiede prima l'elenco di GBUtils, come fa
        schede_audio.applica."""
        # L'elenco e' lo stesso per i due lettori: lo si chiede a uno che non
        # stia svuotando l'uscita.
        lettore = next((lettore for lettore in self._lettori if not lettore.finito), self._attivo)
        return [dict(voce) for voce in lettore.mpv.audio_device_list or []]

    # Velocita', tono, equalizzatore e dissolvenza: per tutti i brani.

    @property
    def velocita(self):
        """La velocita' di riproduzione, da 0,5 a 2 (i limiti di valori.py);
        1 e' la normale. Il tono non cambia."""
        return self._velocita

    @velocita.setter
    def velocita(self, valore):
        with self._blocco:
            self._velocita = float(_fra(valore, valori.VELOCITA_MINIMA, valori.VELOCITA_MASSIMA))
            for lettore in self._lettori:
                lettore.imposta("speed", self._velocita)

    @property
    def tono(self):
        """Il tono in semitoni, intero, da -12 a +12 (valori.TONO_MASSIMO); 0 e'
        il normale. La velocita' non cambia, e le bande dell'equalizzatore
        seguono il tono."""
        return self._tono

    @tono.setter
    def tono(self, valore):
        with self._blocco:
            self._tono = int(_fra(round(valore), -valori.TONO_MASSIMO, valori.TONO_MASSIMO))
            for lettore in self._lettori:
                lettore.imposta("pitch", 2 ** (self._tono / 12))

    @property
    def bande(self):
        """I guadagni delle sette bande dell'equalizzatore, in dB, da -12 a +12
        (valori.GUADAGNO_MASSIMO), nell'ordine di valori.FREQUENZE_DELLE_BANDE.
        Si legge una copia; si scrive tutta la lista."""
        return list(self._bande)

    @bande.setter
    def bande(self, guadagni):
        guadagni = list(guadagni)
        if len(guadagni) != len(valori.FREQUENZE_DELLE_BANDE):
            raise ValueError(f"servono {len(valori.FREQUENZE_DELLE_BANDE)} bande, non {len(guadagni)}")
        with self._blocco:
            for indice, valore in enumerate(guadagni):
                self._metti_la_banda(indice, valore)
            self._applica_il_guadagno()

    def imposta_banda(self, indice, db):
        """Il guadagno di una banda, da 0 (60 Hz) a 6 (12000 Hz), in dB."""
        if not 0 <= indice < len(valori.FREQUENZE_DELLE_BANDE):
            raise IndexError(f"la banda {indice} non c'e'")
        with self._blocco:
            self._metti_la_banda(indice, db)
            self._applica_il_guadagno()

    def _metti_la_banda(self, indice, db):
        db = _fra(db, -valori.GUADAGNO_MASSIMO, valori.GUADAGNO_MASSIMO)
        if db == self._bande[indice]:
            return
        self._bande[indice] = db
        for lettore in self._lettori:
            if lettore.percorso is None:
                # Nessun brano: la catena si scrive prima del prossimo.
                continue
            if lettore.pronto and lettore is not self._preparato:
                # Al volo, senza scatti. Se il filtro non c'e' ancora, mpv
                # risponde con un errore, e allora si riscrive la catena.
                lettore.comando("af-command", "eq", "g", f"{db:g}", f"equalizer@b{indice}", risposta=functools.partial(self._comando_fallito, lettore))
            else:
                # Un brano che si sta aprendo, o il preparato in pausa con il
                # suono gia' filtrato in anticipo: la catena intera.
                lettore.imposta("af", self._catena())

    def _comando_fallito(self, lettore, errore, _esito):
        if errore is None:
            return
        with self._blocco:
            if not self._chiuso and lettore.percorso is not None:
                lettore.imposta("af", self._catena())

    def _applica_il_guadagno(self):
        # Contro la saturazione: il volume scende quanto la banda piu' alzata.
        # Con una banda sola alzata il suono non satura; le bande pero' si
        # sovrappongono, e con piu' bande vicine alzate, o tutte, la risposta
        # sale fino a circa 5,6 dB oltre: dal volume 80 o 90 in su conviene
        # abbassare il volume (decisione di Gabriele, 1 ottobre 2026: il
        # calcolo resta questo).
        guadagno = -max(0, *self._bande)
        for lettore in self._lettori:
            lettore.imposta("volume-gain", guadagno)

    @property
    def dissolvenza(self):
        """La durata della dissolvenza incrociata in secondi, da 0,5 a 15 (i
        limiti di valori.py); 0 la spegne."""
        return self._dissolvenza

    @dissolvenza.setter
    def dissolvenza(self, secondi):
        with self._blocco:
            prima = self._dissolvenza
            self._dissolvenza = float(_fra(secondi, valori.DISSOLVENZA_MINIMA, valori.DISSOLVENZA_MASSIMA)) if secondi and secondi > 0 else 0.0
            if not self._dissolvenza:
                self._scarta_il_preparato()
                self._chiudi_il_calo()
                self._chiudi_la_coda()
            if not prima:
                self._chiesto = False
            self._cambiato()

    def chiudi(self):
        """Ferma il sorvegliante e chiude tutti e due i lettori, sempre."""
        with self._blocco:
            if self._chiuso:
                return
            self._chiuso = True
            self._riposo.set()
            self._sveglia.notify_all()
        try:
            if threading.current_thread() is not self._sorvegliante:
                self._sorvegliante.join()
        finally:
            try:
                self._lettori[0].chiudi()
            finally:
                self._lettori[1].chiudi()

    # Le parti interne, da chiamare con il lucchetto.

    def _catena(self):
        return catena_dei_filtri(self._bande)

    def _altro(self, lettore):
        return self._lettori[1] if lettore is self._lettori[0] else self._lettori[0]

    def _suonanti(self):
        return [self._attivo] + ([self._uscente] if self._uscente is not None else [])

    def _cambiato(self):
        self._generazione += 1
        self._sveglia.notify_all()

    def _scarta_il_preparato(self):
        if self._preparato is not None:
            self._preparato.ferma()
            self._preparato = None

    def _chiudi_la_sfumatura(self):
        """Chi esce si ferma subito, chi entra va a piena voce."""
        if self._sfumatura is None:
            return
        self._uscente.ferma()
        self._uscente = None
        self._sfumatura = None
        self._applica_i_volumi()

    def _chiudi_il_calo(self):
        """Il calo dell'attivo finisce subito: se scendeva verso la pausa, la
        pausa arriva adesso; in ogni caso la voce torna piena."""
        c = self._calo
        if c is None:
            return
        self._calo = None
        if not c.sale:
            c.lettore.imposta("pause", True)
        self._applica_i_volumi()

    def _chiudi_la_coda(self):
        """La coda di uno stop si ferma subito."""
        if self._coda is None:
            return
        lettore = self._coda.lettore
        self._coda = None
        lettore.ferma()

    def _lascia_la_coda(self, lettore):
        """Il lettore serve a un altro brano: se teneva la coda di uno stop,
        la coda si lascia, e chi lo usa lo ferma o lo ricarica."""
        if self._coda is not None and self._coda.lettore is lettore:
            self._coda = None

    def _scrivi_il_volume(self, lettore, volume):
        if volume != lettore.volume_scritto:
            lettore.imposta("volume", volume)

    def _applica_i_volumi(self):
        # La legge del volume di mpv e' cubica: l'ampiezza e' (volume/100)
        # al cubo, quindi al volume va la radice cubica dell'ampiezza.
        s = self._sfumatura
        if s is None:
            ampiezza = self._calo.ampiezza_ora() if self._calo is not None else 1.0
            self._scrivi_il_volume(self._attivo, self._volume_attenuato() * max(0.0, ampiezza) ** (1 / 3))
        else:
            uscente, entrante = s.ampiezze()
            self._scrivi_il_volume(s.uscente, self._volume_attenuato() * max(0.0, uscente) ** (1 / 3))
            self._scrivi_il_volume(s.entrante, self._volume_attenuato() * max(0.0, entrante) ** (1 / 3))
        if self._coda is not None:
            self._scrivi_il_volume(self._coda.lettore, self._volume_attenuato() * max(0.0, self._coda.ampiezza_ora()) ** (1 / 3))

    def _passa_al_preparato(self, sfumando):
        """Il preparato diventa l'attivo: con la sfumatura, o a piena voce se
        quello di prima e' gia' finito. Restituisce l'avviso al_passaggio."""
        entrante = self._preparato
        self._preparato = None
        self._chiesto = False
        # Un calo in corso, per esempio la salita dopo una ripresa: chi esce
        # parte dal punto in cui era arrivato.
        ampiezza = self._calo.ampiezza_ora() if self._calo is not None else 1.0
        self._calo = None
        if sfumando:
            self._uscente = self._attivo
            self._sfumatura = _Sfumatura(self._uscente, entrante, ampiezza)
        else:
            self._scrivi_il_volume(entrante, self._volume_attenuato())
        self._attivo = entrante
        entrante.imposta("pause", self._pausa)
        self._cambiato()
        if self._al_passaggio is None:
            return None
        return functools.partial(self._al_passaggio, entrante.percorso, entrante.sottobrano)

    # Il sorvegliante della dissolvenza.

    def _da_sorvegliare(self):
        attivo = self._attivo
        if self._sfumatura is not None or self._calo is not None or self._coda is not None:
            return True
        return self._dissolvenza > 0 and attivo.percorso is not None and not attivo.finito

    def _da_leggere(self):
        """I lettori da interrogare in questo passo."""
        s = self._sfumatura
        if s is not None:
            lettori = [s.entrante] if s.entrante.pronto and not s.entrante.finito else []
            if s.durata is None and s.uscente.pronto and not s.uscente.finito:
                lettori.append(s.uscente)
        else:
            lettori = [self._attivo] if self._attivo.pronto and not self._attivo.finito else []
            if self._preparato is not None and self._preparato.pronto:
                lettori.append(self._preparato)
        coda = self._coda.lettore if self._coda is not None else None
        if coda is not None and coda.pronto and not coda.finito and coda not in lettori:
            lettori.append(coda)
        return lettori

    def _sorveglia(self):
        while True:
            with self._blocco:
                while not self._chiuso and not self._da_sorvegliare():
                    self._sveglia.wait()
                if self._chiuso:
                    return
                da_leggere = self._da_leggere()
                generazione = self._generazione
            # Le letture sono sincrone: fuori dal lucchetto, cosi' la finestra
            # non aspetta mai il sorvegliante.
            letture = {}
            for lettore in da_leggere:
                try:
                    letture[lettore] = lettore.leggi()
                except (mpv.ShutdownError, SystemError, RuntimeError, ValueError, TypeError, AttributeError):
                    letture[lettore] = (None, None)
            avvisi = []
            with self._blocco:
                if self._chiuso:
                    return
                if generazione == self._generazione:
                    avvisi = self._passo(letture)
            for avviso in avvisi:
                avviso()
            self._riposo.wait(PASSO_DEL_SORVEGLIANTE)

    def _passo_dei_cali(self, letture):
        """Fa avanzare il calo dell'attivo e la coda dello stop. Alla fine il
        calo verso la pausa mette la pausa e riporta la voce piena (la
        ripresa ripartira' dal silenzio), quello in salita si toglie, e la
        coda si ferma."""
        cambiati = False
        for c in (self._calo, self._coda):
            if c is None or c.lettore not in letture:
                continue
            posizione, durata = letture[c.lettore]
            if posizione is None:
                continue
            if c.durata is None:
                resto = (durata - posizione) / self._velocita - MARGINE_DI_FINE if durata else self._dissolvenza
                c.durata = max(0.0, min(self._dissolvenza, resto))
            else:
                c.trascorso += max(0.0, posizione - c.ultima) / self._velocita
            c.ultima = posizione
            cambiati = True
            if c.avanzamento() < 1:
                continue
            # Chi scende si ferma al passo dopo quello che ha scritto lo zero.
            # Fino alla 1.58.1 si fermava subito, e l'ultimo volume scritto
            # era quello del gradino di prima: con passi di una trentina di
            # millesimi, a una dissolvenza di mezzo secondo, circa un
            # settimo della voce, che la pausa o lo stop troncavano di
            # colpo. Il passo in piu' da' al dispositivo il tempo di
            # suonare il silenzio.
            if not c.sale and not c.zittito:
                c.zittito = True
                continue
            if c is self._coda:
                self._chiudi_la_coda()
            else:
                self._chiudi_il_calo()
        if cambiati:
            self._applica_i_volumi()

    def _lunghezza(self, posizione, durata):
        """I secondi veri della sfumatura per chi entra, alla sua posizione: la
        dissolvenza, ma non oltre meta' del brano, e non oltre il punto in cui
        arriverebbe la sua fine (conta solo per i brani sotto il secondo)."""
        lunghezza = self._dissolvenza
        if durata:
            lunghezza = min(lunghezza, durata / 2 / self._velocita, (durata - (posizione or 0.0)) / self._velocita - MARGINE_DI_FINE)
        return lunghezza

    def _passo(self, letture):
        """Un passo del sorvegliante, con il lucchetto: restituisce gli avvisi
        da dare fuori."""
        velocita = self._velocita
        self._passo_dei_cali(letture)
        s = self._sfumatura
        if s is not None:
            posizione, durata = letture.get(s.entrante, (None, None))
            if posizione is None:
                return []
            if s.durata is None:
                # Chi entra comincia ora: la sfumatura dura quanto la
                # dissolvenza, ma non oltre meta' di chi entra ne' oltre cio'
                # che resta a chi esce.
                lunghezza = self._lunghezza(posizione, durata)
                if s.uscente.finito or s.uscente.percorso is None:
                    lunghezza = 0.0
                elif s.uscente in letture:
                    posizione_uscente, durata_uscente = letture[s.uscente]
                    if posizione_uscente is not None and durata_uscente:
                        lunghezza = min(lunghezza, (durata_uscente - posizione_uscente) / velocita - MARGINE_DI_FINE)
                s.durata = max(0.0, lunghezza)
            else:
                s.trascorso += max(0.0, posizione - s.ultima) / velocita
            s.ultima = posizione
            if s.avanzamento() >= 1 and s.zittita:
                self._chiudi_la_sfumatura()
            else:
                # All'ultimo gradino chi esce va a zero, e si ferma al passo
                # dopo, come i cali.
                s.zittita = s.avanzamento() >= 1
                self._applica_i_volumi()
            return []
        if not self._dissolvenza or self._attivo not in letture:
            return []
        posizione, durata = letture[self._attivo]
        if posizione is None or not durata:
            return []
        resto = (durata - posizione) / velocita
        if self._preparato is None:
            if not self._chiesto and resto <= self._dissolvenza + ANTICIPO_DEL_SEGUENTE:
                self._chiesto = True
                if self._chiedi_il_seguente is not None:
                    return [self._chiedi_il_seguente]
            return []
        if self._preparato not in letture:
            return []
        if resto > self._lunghezza(*letture[self._preparato]) + MARGINE_DI_FINE:
            return []
        if self._pausa:
            # In pausa non suona niente, e il passaggio aspetta la ripresa:
            # una ripresa all'avvio o un salto in pausa vicino alla fine non
            # cambiano brano, e un salto indietro resta nello stesso brano.
            # Alla ripresa la sfumatura dura al massimo quanto resta a chi
            # esce.
            return []
        avviso = self._passa_al_preparato(sfumando=True)
        return [avviso] if avviso else []
