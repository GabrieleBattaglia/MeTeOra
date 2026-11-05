# MeTeOra, le prove dei componenti aggiuntivi: il modulo e la voce delle impostazioni.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 3.1.0, tappa 19 a, issue 40.

"""Le prove dei componenti aggiuntivi.

Niente rete: gli scaricamenti si sostituiscono con byte finti, e i banchi e
FluidSynth stanno in cartelle temporanee. Le prove della voce usano gli aiuti
delle prove della finestra.
"""

import os

import pytest
from test_finestra import _ListaFinta, _midi_finti, _senza_ora, _ultima
from test_midi import banco_di_prova

import componenti
import finestra as modulo
import midi


class _SceltaInFila:
    """Le scelte da una lista, che rispondono una dopo l'altra con gli indici
    dati, None per Annulla; annota titolo e righe di ogni apertura."""

    def __init__(self, *indici):
        self.indici = list(indici)
        self.aperture = []

    def __call__(self, genitore, titolo, voci, scelta, con_filtro=False):
        self.aperture.append((titolo, list(voci)))
        self._indice = self.indici.pop(0)
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def ShowModal(self):
        return modulo.wx.ID_CANCEL if self._indice is None else modulo.wx.ID_OK

    def GetSelection(self):
        return self._indice


@pytest.fixture
def banchi(tmp_path, monkeypatch):
    cartella = tmp_path / "banchi"
    monkeypatch.setattr(midi, "cartella_dei_banchi", lambda: str(cartella))
    return cartella


def test_l_impronta_git_e_quella_di_git():
    # Quella del file vuoto, che git scrive sempre uguale.
    assert midi.impronta_git(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"


def test_scarica_banco_controlla_dimensione_intestazione_e_impronta(banchi, monkeypatch):
    buono = b"RIFF" + b"\0" * 4 + b"sfbk" + b"dati"
    monkeypatch.setattr(midi, "_scarica", lambda url, avanza=None: buono if "buono" in url else b"RIFF\0\0\0\0sfbkALTRO")
    percorso = midi.scarica_banco("Prova", "prova.sf2", ("https://x/buono",), len(buono), midi.impronta_git(buono))
    assert percorso == str(banchi / "prova.sf2") and (banchi / "prova.sf2").read_bytes() == buono
    with pytest.raises(OSError, match="il file non è Prova"):
        midi.scarica_banco("Prova", "altro.sf2", ("https://x/cattivo",), len(buono))
    with pytest.raises(OSError, match="il file non è Prova"):
        midi.scarica_banco("Prova", "altro.sf2", ("https://x/buono",), len(buono), "0" * 40)
    assert not (banchi / "altro.sf2").exists()


def test_un_banco_c_e_si_aggiorna_e_si_toglie(banchi, monkeypatch):
    banco = componenti.Banco("prova", "Prova", "un banco.", "MIT", "Prova.sf2", ("https://x",), 0)
    assert not banco.presente() and not banco.da_aggiornare()
    banco_di_prova(banchi / "Prova.sf2")
    banco.dimensione = os.path.getsize(banco.percorso())
    assert banco.presente() and not banco.da_aggiornare()
    banco.dimensione += 1
    assert banco.da_aggiornare()
    svuotate = []
    monkeypatch.setattr(midi, "svuota_la_scorta", lambda tranne=None: svuotate.append(tranne))
    banco.togli()
    assert not banco.presente() and svuotate == [None]


def test_fluidsynth_non_si_toglie_mentre_e_in_uso(tmp_path, monkeypatch):
    cartella = tmp_path / "fluidsynth"
    cartella.mkdir()
    for dll in midi.FLUIDSYNTH_DLL:
        (cartella / dll).write_bytes(b"MZ")
    monkeypatch.setattr(midi, "cartella_fluidsynth", lambda: str(cartella))
    monkeypatch.setattr(midi, "fluidsynth_caricato", lambda: True)
    with pytest.raises(OSError, match="già in uso"):
        componenti.FLUIDSYNTH.togli()
    assert componenti.FLUIDSYNTH.presente()
    monkeypatch.setattr(midi, "fluidsynth_caricato", lambda: False)
    componenti.FLUIDSYNTH.togli()
    assert not componenti.FLUIDSYNTH.presente() and not cartella.exists()


def test_l_elenco_dei_componenti():
    assert [c.chiave for c in componenti.TUTTI] == ["fluidsynth", "fluidr3", "generaluser_gs", "ms_basic"]
    assert componenti.TUTTI[1:] == componenti.BANCHI and all(c.banco and c.midi for c in componenti.BANCHI)
    for banco in componenti.BANCHI:
        assert banco.fonti and all(f.startswith("https://") for f in banco.fonti) and banco.dimensione > 1_000_000
    # GeneralUser GS dalla copia di MeTeOra, come vuole il suo autore.
    assert componenti.GENERALUSER_GS.fonti[0].startswith("https://github.com/GabrieleBattaglia/MeTeOra/releases/download/componenti/")
    assert all(len(b.impronta) == 40 for b in (componenti.GENERALUSER_GS, componenti.MS_BASIC))


def test_la_voce_componenti_installa_un_banco_e_lo_usa(finestra, monkeypatch, suoni_annotati, tmp_path):
    _midi_finti(finestra, monkeypatch)
    lista = _ListaFinta()
    assert finestra._riga_dell_impostazione("componenti") == "Componenti aggiuntivi: 1 installato su 4"

    def installa(avanza=None):
        avanza(50, 100)
        return banco_di_prova(tmp_path / "scaricati" / "GeneralUser-GS.sf2")

    monkeypatch.setattr(componenti.GENERALUSER_GS, "installa", installa)
    scelta = _SceltaInFila(2, 0)
    monkeypatch.setattr(modulo, "FinestraScelta", scelta)
    finestra._cambia_impostazione("componenti", lista)
    titolo, righe = scelta.aperture[0]
    assert titolo == "Componenti aggiuntivi" and righe[0].startswith("FluidSynth, installato: il sintetizzatore che suona i MIDI")
    assert righe[2] == ("GeneralUser GS, da installare: un banco di suoni General MIDI leggero e curato, di S. Christian Collins. "
        "Licenza uso libero, anche nei programmi, circa 32 MB.")
    assert scelta.aperture[1] == ("GeneralUser GS", ["Installa, circa 32 MB"])
    testi = [_senza_ora(r) for r in finestra._righe]
    assert "Scarico GeneralUser GS, circa 32 MB." in testi and "GeneralUser GS: 50%." in testi and "GeneralUser GS scaricato." in testi
    banco = str(tmp_path / "scaricati" / "GeneralUser-GS.sf2")
    assert finestra.impostazioni["banco_midi"] == banco and _ultima(finestra) == "I MIDI suonano con il banco GeneralUser-GS.sf2."
    assert lista.righe["componenti"].startswith("Componenti aggiuntivi: ")
    for evento in ("scaricamento_avviato", "scaricamento_finito", "impostazione_cambiata"):
        assert evento in suoni_annotati
    assert finestra._componente_in_arrivo is None


def test_un_banco_in_uso_si_toglie_e_i_midi_restano_senza(finestra, monkeypatch, suoni_annotati):
    _midi_finti(finestra, monkeypatch)
    banco = banco_di_prova(__import__("pathlib").Path(midi.cartella_dei_banchi()) / "GeneralUser-GS.sf2")
    finestra.impostazioni["banco_midi"] = banco
    monkeypatch.setattr(midi, "svuota_la_scorta", lambda tranne=None: None)
    assert finestra._riga_del_componente(componenti.GENERALUSER_GS).startswith("GeneralUser GS, da aggiornare:")
    monkeypatch.setattr(componenti.GENERALUSER_GS, "dimensione", os.path.getsize(banco))
    assert finestra._riga_del_componente(componenti.GENERALUSER_GS).startswith("GeneralUser GS, installato e in uso per i MIDI:")
    domande = []
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo, genitore=None: domande.append(domanda) or True)
    scelta = _SceltaInFila(2, 0)
    monkeypatch.setattr(modulo, "FinestraScelta", scelta)
    lista = _ListaFinta()
    finestra._cambia_impostazione("componenti", lista)
    assert scelta.aperture[1] == ("GeneralUser GS", ["Togli"])
    assert domande == ["Tolgo GeneralUser GS? Si libera circa 32 MB, e si può installare di nuovo da qui."]
    assert not os.path.exists(banco) and finestra.impostazioni["banco_midi"] == ""
    assert _ultima(finestra) == "GeneralUser GS tolto. I MIDI non hanno più un banco: si sceglie al prossimo MIDI."
    assert lista.righe["banco_midi"] == "Banco dei suoni MIDI: nessuno, si sceglie al primo MIDI"


def test_un_banco_non_in_uso_si_usa_per_i_midi(finestra, monkeypatch, suoni_annotati):
    _midi_finti(finestra, monkeypatch)
    banco = banco_di_prova(__import__("pathlib").Path(midi.cartella_dei_banchi()) / "MS Basic.sf3")
    monkeypatch.setattr(componenti.MS_BASIC, "dimensione", os.path.getsize(banco))
    monkeypatch.setattr(modulo, "FinestraScelta", scelta := _SceltaInFila(3, 0))
    finestra._cambia_impostazione("componenti", _ListaFinta())
    assert scelta.aperture[1] == ("MS Basic", ["Usa per i MIDI", "Togli"])
    assert finestra.impostazioni["banco_midi"] == banco and _ultima(finestra) == "I MIDI suonano con il banco MS Basic.sf3."


def test_fluidsynth_in_uso_non_si_toglie_e_lo_dice(finestra, monkeypatch, suoni_annotati):
    _midi_finti(finestra, monkeypatch)
    monkeypatch.setattr(midi, "fluidsynth_caricato", lambda: True)
    monkeypatch.setattr(finestra, "_conferma", lambda domanda, titolo, genitore=None: True)
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaInFila(0, 0))
    finestra._cambia_impostazione("componenti", _ListaFinta())
    assert suoni_annotati[-1] == "errore"
    assert _ultima(finestra) == "FluidSynth non si toglie: FluidSynth è già in uso in questa sessione: si toglie dopo aver chiuso e riaperto MeTeOra"


def test_uno_scaricamento_alla_volta_e_annulla(finestra, monkeypatch, suoni_annotati):
    _midi_finti(finestra, monkeypatch)
    finestra._componente_in_arrivo = componenti.FLUIDR3
    finestra._installa_il_componente(componenti.MS_BASIC)
    assert _ultima(finestra) == "Sto già scaricando FluidR3 GM: un momento." and suoni_annotati[-1] == "non_disponibile"
    finestra._componente_in_arrivo = None
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaInFila(None))
    finestra._cambia_impostazione("componenti", _ListaFinta())
    assert _ultima(finestra) == "Componenti aggiuntivi: niente di cambiato."
    monkeypatch.setattr(modulo, "FinestraScelta", _SceltaInFila(1, None))
    finestra._cambia_impostazione("componenti", _ListaFinta())
    assert _ultima(finestra) == "FluidR3 GM: niente di cambiato."


def test_uno_scaricamento_che_non_riesce(finestra, monkeypatch, suoni_annotati):
    _midi_finti(finestra, monkeypatch)

    def guasto(avanza=None):
        raise OSError("la rete non risponde")

    monkeypatch.setattr(componenti.MS_BASIC, "installa", guasto)
    finestra._installa_il_componente(componenti.MS_BASIC)
    assert _ultima(finestra) == "MS Basic non si scarica: la rete non risponde" and suoni_annotati[-1] == "errore"
    assert finestra._componente_in_arrivo is None and not finestra._midi_in_preparazione
