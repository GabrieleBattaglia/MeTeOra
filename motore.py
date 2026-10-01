# MeTeOra, il motore di riproduzione: libmpv, e i SID in tempo reale.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1, dai prototipi della tappa 0. Nella 1.51.0 la scheda audio della musica, letta e scelta.

"""Un solo lettore per tutti i formati.

I file normali li apre libmpv. I SID passano dal protocollo sid://, che
libmpv chiede a questo modulo: il brano si emula in un filo che corre in
anticipo e libmpv lo legge come un WAV. Cosi' volume, seek e fine del brano
funzionano allo stesso modo per tutti.
Gli eventi di libmpv arrivano in un filo suo: chi li riceve (fine e errore)
deve riportarli nel filo della finestra, per esempio con wx.CallAfter.
La scheda audio su cui suona la musica e' quella di dispositivo, da
scegliere fra quelle di dispositivi(); la sceglie schede_audio.applica.
"""

import librerie  # noqa: F401

# isort: split
import mpv

import formati
import sid
import songlengths

# La durata di un SID che non sta in nessun database: tre minuti, come fanno
# i lettori di SID.
DURATA_SID_PREDEFINITA = 180.0
# Oltre il 100 il volume amplifica, per gli audio registrati troppo bassi.
VOLUME_MASSIMO = 300


def durata_del_sottobrano(percorso, sottobrano):
    """I secondi di un sottobrano di un SID: dal database, o la durata predefinita."""
    durate = songlengths.durate_del_file(percorso)
    return durate[sottobrano - 1] if durate and sottobrano <= len(durate) else DURATA_SID_PREDEFINITA


class Motore:
    def __init__(self, alla_fine=None, all_errore=None, ao="wasapi", volume=80):
        """alla_fine() quando un brano finisce da solo; all_errore(percorso)
        quando un brano non si puo' aprire o si interrompe per un errore."""
        self._alla_fine = alla_fine
        self._all_errore = all_errore
        # Gli script interni di mpv (interfaccia a schermo, console,
        # statistiche...) a MeTeOra non servono, e caricandoli LuaJIT solleva
        # all'avvio eccezioni di Windows che gestisce da se', ma che il
        # faulthandler di Python stampa come errori fatali.
        self._lettore = mpv.MPV(ao=ao, vo="null", video="no", config=False, ytdl=False, input_default_bindings=False,
            keep_open="no", volume=volume, volume_max=VOLUME_MASSIMO, osc=False, load_stats_overlay=False, load_console=False, load_auto_profiles=False,
            load_select=False, load_commands=False, load_positioning=False, load_context_menu=False)
        self._in_corso = None
        self.sottobrano = None
        self.sottobrani = None
        self._lettore.register_stream_protocol("sid", self._apri_sid)
        self._lettore.register_event_callback(self._evento)

    def _apri_sid(self, uri):
        # sid://<sottobrano>/<secondi>/<percorso>
        sottobrano, secondi, percorso = uri[len("sid://"):].split("/", 2)
        return sid.FlussoSid(sid.BranoSid(percorso, int(sottobrano), float(secondi)))

    def _evento(self, evento):
        if evento.event_id.value != mpv.MpvEventID.END_FILE:
            return
        motivo = evento.data.reason
        # Un brano sostituito da un altro finisce con il motivo STOP, e il
        # file in corso resta quello nuovo.
        if motivo not in (mpv.MpvEventEndFile.EOF, mpv.MpvEventEndFile.ERROR):
            return
        percorso, self._in_corso = self._in_corso, None
        if motivo == mpv.MpvEventEndFile.EOF and self._alla_fine:
            self._alla_fine()
        elif motivo == mpv.MpvEventEndFile.ERROR and self._all_errore:
            self._all_errore(percorso)

    def suona(self, percorso, sottobrano=None, inizio=None, in_pausa=False):
        """Avvia un file, dall'inizio o dai secondi inizio, e in pausa se
        chiesto. Per i SID suona il sottobrano chiesto, o quello iniziale,
        con la durata dal database della collezione."""
        self._in_corso = percorso
        self.sottobrano = self.sottobrani = None
        # La pausa si mette prima di caricare: il brano non deve suonare
        # nemmeno un istante.
        self._lettore.pause = in_pausa
        opzioni = {"start": f"{inizio:.3f}"} if inizio else {}
        info = songlengths.info_del_sid(percorso) if formati.e_sid(percorso) else None
        if info:
            self.sottobrani = max(1, info["sottobrani"])
            self.sottobrano = min(sottobrano or info["iniziale"] or 1, self.sottobrani)
            secondi = durata_del_sottobrano(percorso, self.sottobrano)
            self._lettore.loadfile(f"sid://{self.sottobrano}/{max(1.0, secondi)}/{percorso}", demuxer_lavf_format="wav", cache="no",
                demuxer_readahead_secs="1", **opzioni)
        else:
            self._lettore.loadfile(percorso, **opzioni)

    @property
    def in_corso(self):
        """Il file caricato, anche se in pausa; None dopo stop, a fine brano
        o dopo un errore."""
        return self._in_corso

    @property
    def in_pausa(self):
        return bool(self._lettore.pause)

    def pausa(self, valore=None):
        """Mette o toglie la pausa; senza valore la inverte. Torna il nuovo stato."""
        self._lettore.pause = (not self._lettore.pause) if valore is None else valore
        return self._lettore.pause

    def stop(self):
        self._lettore.command("stop")
        self._in_corso = None

    def salta(self, secondi):
        """Avanti (positivo) o indietro (negativo) nel brano."""
        self._lettore.seek(secondi, "relative", "exact")

    def vai_a(self, secondi):
        self._lettore.seek(secondi, "absolute", "exact")

    @property
    def posizione(self):
        return self._lettore.time_pos

    @property
    def durata(self):
        return self._lettore.duration

    @property
    def volume(self):
        return round(self._lettore.volume)

    @volume.setter
    def volume(self, valore):
        self._lettore.volume = max(0, min(VOLUME_MASSIMO, valore))

    @property
    def muto(self):
        return bool(self._lettore.mute)

    @muto.setter
    def muto(self, valore):
        self._lettore.mute = valore

    @property
    def dispositivo(self):
        """L'uscita audio della musica, col nome che le da' mpv: "auto",
        il valore di partenza, segue la scheda predefinita di Windows;
        "wasapi/{...}" e' una scheda precisa, presa da dispositivi().
        mpv accetta in scrittura anche un nome che non esiste, e se ne
        accorge solo quando apre il suono: chi scrive lo prende dall'elenco.
        Scritta durante la riproduzione, mpv riapre l'uscita sulla scheda
        nuova. Dice la scheda chiesta, non quella che suona davvero."""
        return self._lettore.audio_device or "auto"

    @dispositivo.setter
    def dispositivo(self, nome):
        self._lettore.audio_device = nome

    def dispositivi(self):
        """Le uscite audio che mpv conosce: una lista di dizionari con name,
        il nome da scrivere in dispositivo, e description, quello leggibile.
        Ci sono anche le uscite degli altri driver di mpv, per esempio
        openal, e la voce "auto".
        Attenzione, fatto verificato: se la si legge prima che sounddevice
        sia importato per la prima volta, PortAudio perde le uscite ASIO.
        Chi la legge chiede prima l'elenco di GBUtils, come fa
        schede_audio.applica."""
        return [dict(voce) for voce in self._lettore.audio_device_list or []]

    def chiudi(self):
        self._lettore.terminate()
