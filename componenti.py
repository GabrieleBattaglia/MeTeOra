# MeTeOra, i componenti aggiuntivi: cio' che MeTeOra scarica quando serve, ognuno con la sua licenza.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 3.1.0, tappa 19 a del piano, issue 40. Nella 3.2.0 yt-dlp e QuickJS, per gli indirizzi in rete.

"""I componenti aggiuntivi di MeTeOra (3.1.0, issue 40).

Sono i programmi e i dati che MeTeOra non porta nel pacchetto e scarica
quando servono: per ora FluidSynth e i banchi di suoni dei MIDI, e con le
versioni seguenti della tappa 19 gli altri. Ognuno ha un nome, a che cosa
serve, la licenza, il peso e una fonte fissa, controllata dopo lo
scaricamento: un file che non e' quello atteso non si installa. La voce
Componenti aggiuntivi delle impostazioni li elenca, e da li' si installano,
si aggiornano e si tolgono; FluidSynth e il banco si scaricano anche al
primo MIDI, come prima. FluidSynth resta nella cartella fluidsynth e i
banchi nella cartella banchi, accanto ai dati, dove gia' erano.
GeneralUser GS si scarica da una copia fra i file della release componenti
di MeTeOra su GitHub, come chiede il suo autore, che non vuole collegamenti
diretti ai suoi file (Gabriele, 5 novembre 2026). Gli altri banchi dalla loro
fonte, fissata a una versione, con l'impronta git che le API di GitHub
dicono senza scaricarli.
Dalla 3.2.0 yt-dlp, che apre gli indirizzi in rete, e QuickJS, che gli serve
per YouTube. yt-dlp non ha una versione fissa: si scarica l'ultima, con le
impronte della sua release, e si aggiorna da se' una volta al giorno, o a
mano da qui con Cerca un aggiornamento; QuickJS si', la 0.18.0.
"""

import contextlib
import os

import indirizzi
import midi
from lingua import _


class Componente:
    """Un componente: chiave, nome, a che cosa serve, licenza e peso in byte.
    midi dice se serve ai MIDI, banco se e' un banco di suoni."""

    banco = False
    midi = False
    # Vero per chi si aggiorna dalla rete, come yt-dlp: allora ha aggiorna().
    aggiornabile = False

    def __init__(self, chiave, nome, uso, licenza, peso):
        self.chiave, self.nome, self.uso, self.licenza, self.peso = chiave, nome, uso, licenza, peso

    def presente(self):
        raise NotImplementedError

    def versione(self):
        """La versione installata, da dire nella lista, o None."""

    def da_aggiornare(self):
        """Vero se c'e' ma non e' la versione di questo MeTeOra."""
        return False

    def installa(self, avanza=None):
        """Scarica e installa; avanza(scaricati, totale) a ogni pezzo. OSError o
        ValueError se non riesce."""
        raise NotImplementedError

    def togli(self):
        raise NotImplementedError


class FluidSynth(Componente):
    midi = True

    def presente(self):
        return midi.fluidsynth_presente()

    def installa(self, avanza=None):
        midi.scarica_fluidsynth(avanza)

    def togli(self):
        if midi.fluidsynth_caricato():
            raise OSError(_("FluidSynth è già in uso in questa sessione: si toglie dopo aver chiuso e riaperto MeTeOra"))
        cartella = midi.cartella_fluidsynth()
        for dll in midi.FLUIDSYNTH_DLL:
            with contextlib.suppress(FileNotFoundError):
                os.remove(os.path.join(cartella, dll))
        # La cartella se ne va solo se e' vuota.
        with contextlib.suppress(OSError):
            os.rmdir(cartella)


class Banco(Componente):
    """Un banco di suoni General MIDI, un file solo nella cartella dei banchi.
    scarica, se c'e', prende il posto dello scaricamento comune."""

    banco = True
    midi = True

    def __init__(self, chiave, nome, uso, licenza, nome_file, fonti, dimensione, impronta=None, scarica=None):
        super().__init__(chiave, nome, uso, licenza, dimensione)
        self.nome_file, self.fonti, self.dimensione, self.impronta, self._scarica = nome_file, fonti, dimensione, impronta, scarica

    def percorso(self):
        return os.path.join(midi.cartella_dei_banchi(), self.nome_file)

    def presente(self):
        return midi.e_un_banco(self.percorso())

    def da_aggiornare(self):
        try:
            return self.presente() and os.path.getsize(self.percorso()) != self.dimensione
        except OSError:
            return False

    def installa(self, avanza=None):
        """Il percorso del banco installato."""
        if self._scarica is not None:
            return self._scarica(avanza)
        return midi.scarica_banco(self.nome, self.nome_file, self.fonti, self.dimensione, self.impronta, avanza)

    def togli(self):
        # I synth tenuti da parte potrebbero avere il banco caricato.
        midi.svuota_la_scorta()
        os.remove(self.percorso())


FLUIDSYNTH = FluidSynth("fluidsynth", "FluidSynth", _("il sintetizzatore che suona i MIDI con un banco di suoni."), _("LGPL 2.1 o successive"), 2_727_529)
FLUIDR3 = Banco("fluidr3", "FluidR3 GM", _("il banco di suoni General MIDI storico di FluidSynth, il più grande."), "MIT", midi.FLUIDR3_NOME,
    midi.FLUIDR3_URL, midi.FLUIDR3_DIMENSIONE, scarica=lambda avanza=None: midi.scarica_fluidr3(avanza))
# GeneralUser GS 2.0.3, del 22 febbraio 2026, dalla copia di MeTeOra.
GENERALUSER_GS = Banco("generaluser_gs", "GeneralUser GS", _("un banco di suoni General MIDI leggero e curato, di S. Christian Collins."),
    _("uso libero, anche nei programmi"), "GeneralUser-GS.sf2",
    ("https://github.com/GabrieleBattaglia/MeTeOra/releases/download/componenti/GeneralUser-GS.sf2",), 32_319_396,
    "298b552d2e9d1307e03e5c5c99d2c046aaed9ec3")
# MS Basic, il banco di MuseScore 4, nel formato sf3 con i campioni compressi:
# FluidSynth lo decomprime quando lo carica, in circa dieci secondi sul gigante.
MS_BASIC = Banco("ms_basic", "MS Basic", _("il banco di suoni General MIDI di MuseScore 4: compresso, al primo MIDI si carica in una decina di secondi."),
    "MIT", "MS Basic.sf3", ("https://raw.githubusercontent.com/musescore/MuseScore/37128c5ac8f9af804b63650610952414421828b8/share/sound/MS%20Basic.sf3",),
    51_278_610, "5be56b2fafa5eee347256cbe0d2fbfacd01702b6")


class YtDlp(Componente):
    aggiornabile = True

    def presente(self):
        return indirizzi.ytdlp_presente()

    def versione(self):
        return indirizzi.versione_di_ytdlp() if self.presente() else None

    def installa(self, avanza=None):
        return indirizzi.installa_ytdlp(avanza=avanza)

    def aggiorna(self, avanza=None):
        """La versione nuova installata, o None se c'era gia' l'ultima."""
        return indirizzi.aggiorna_ytdlp(avanza)

    def togli(self):
        indirizzi.togli_ytdlp()


class QuickJS(Componente):
    def presente(self):
        return indirizzi.quickjs_presente()

    def installa(self, avanza=None):
        indirizzi.installa_quickjs(avanza)

    def togli(self):
        indirizzi.togli_quickjs()


BANCHI = (FLUIDR3, GENERALUSER_GS, MS_BASIC)
YT_DLP = YtDlp("yt_dlp", "yt-dlp", _("apre gli indirizzi dei siti, come RaiPlay Sound, YouTube, SoundCloud e Bandcamp, e si aggiorna da sé ogni giorno."),
    _("Unlicense, l'eseguibile GPL 3"), indirizzi.YTDLP_PESO)
QUICKJS = QuickJS("quickjs", "QuickJS", _("il motore JavaScript che serve a yt-dlp per YouTube."), "MIT", indirizzi.QUICKJS_PESO)
INDIRIZZI = (YT_DLP, QUICKJS)
TUTTI = (FLUIDSYNTH, *BANCHI, *INDIRIZZI)
