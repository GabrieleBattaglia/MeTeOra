# MeTeOra, le prove del lettore di rete in un processo a parte (2.7.2).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con lettore_di_rete.py, nella 2.7.2.

"""Le prove di lettore_di_rete.py con processi lettori veri, su cartelle del
disco: la rete vera non serve, perche' il lettore legge qualsiasi cartella.
Una lettura appesa si finge con METEORA_LETTORE_DI_PROVA, che il lettore
eredita: un percorso con <appesa> non torna mai."""

import ctypes
import time

import pytest

import lettore_di_rete
import questo_pc
import ricerca
from lettore_di_rete import CARTELLA, DI_SISTEMA, FILE, NASCOSTA, Lettori


@pytest.fixture
def lettori(monkeypatch):
    monkeypatch.setattr(lettore_di_rete, "ATTIVO", True)
    monkeypatch.setenv("METEORA_LETTORE_DI_PROVA", "1")
    insieme = Lettori()
    # Anche ricerca.leggi_in_rete usa questi, che si chiudono alla fine.
    monkeypatch.setattr(lettore_di_rete, "lettori", insieme)
    yield insieme
    insieme.chiudi()


def _albero(base):
    (base / "Sotto").mkdir()
    (base / "brano.mp3").write_bytes(b"")
    (base / "nota.txt").write_bytes(b"")
    nascosto = base / "nascosto.mp3"
    nascosto.write_bytes(b"")
    ctypes.windll.kernel32.SetFileAttributesW(str(nascosto), 0x2)


def test_l_elenco_grezzo_e_il_contenuto(lettori, tmp_path):
    _albero(tmp_path)
    voci = dict(lettori.elenca(str(tmp_path), attesa=10))
    assert voci["Sotto"] & CARTELLA and voci["brano.mp3"] & FILE and voci["nota.txt"] & FILE
    assert voci["nascosto.mp3"] & NASCOSTA and not voci["brano.mp3"] & (NASCOSTA | DI_SISTEMA)
    # Filtrato come questo_pc.contenuto: cartelle visibili e file suonabili.
    assert questo_pc.contenuto_dalle_voci(str(tmp_path), list(voci.items())) == questo_pc.contenuto(str(tmp_path))
    # ricerca.leggi_in_rete passa dal lettore, e il lettore libero resta pronto.
    assert ricerca.leggi_in_rete(str(tmp_path)) == questo_pc.contenuto(str(tmp_path))


def test_gli_errori_arrivano_come_quelli_di_windows(lettori, tmp_path):
    with pytest.raises(OSError) as errore:
        lettori.elenca(str(tmp_path / "non c'e'"), attesa=10)
    assert errore.value.winerror == 3 and not isinstance(errore.value, lettore_di_rete.NonRisponde)
    assert lettori.e_una_cartella(str(tmp_path), attesa=10) and not lettori.e_una_cartella(str(tmp_path / "manca"), attesa=10)


def test_una_lettura_appesa_si_abbandona(lettori, tmp_path):
    # Il lettore appeso si lascia, e la lettura dopo la fa un altro.
    inizio = time.monotonic()
    with pytest.raises(lettore_di_rete.NonRisponde):
        lettori.elenca(str(tmp_path / "<appesa>"), attesa=1.5)
    assert time.monotonic() - inizio < 6 and lettori.abbandonati == 1
    assert lettori.elenca(str(tmp_path), attesa=10) == []
    # La prova se una cartella risponde: un lettore appeso vale come no.
    assert not lettori.e_una_cartella(str(tmp_path / "<appesa>"), attesa=1.5) and lettori.abbandonati == 2


def test_fermo_vale_subito(lettori, tmp_path):
    chiamate = []

    def fermo():
        chiamate.append(1)
        return len(chiamate) > 3

    inizio = time.monotonic()
    assert lettori.elenca(str(tmp_path / "<appesa>"), fermo=fermo, attesa=30) is None
    assert time.monotonic() - inizio < 3 and lettori.abbandonati == 1


def test_i_lettori_liberi_si_tengono_e_si_chiudono(lettori, tmp_path):
    for _ in range(3):
        lettori.elenca(str(tmp_path), attesa=10)
    assert len(lettori._liberi) == 1
    processo = lettori._liberi[0].processo
    lettori.chiudi()
    assert processo.wait(10) == 0


def test_senza_lettore_si_legge_in_un_filo(monkeypatch, tmp_path):
    # Se il lettore non parte, come quando manca l'eseguibile, ricerca torna
    # alla lettura in un filo.
    monkeypatch.setattr(lettore_di_rete, "ATTIVO", True)

    def non_parte():
        raise lettore_di_rete.NonParte(2, "manca")

    monkeypatch.setattr(lettore_di_rete, "_Processo", non_parte)
    monkeypatch.setattr(lettore_di_rete, "lettori", Lettori())
    _albero(tmp_path)
    assert ricerca.leggi_in_rete(str(tmp_path)) == questo_pc.contenuto(str(tmp_path))
    # E cosi' la prova se una cartella risponde.
    import questa_rete

    assert questa_rete.raggiungibile(str(tmp_path)) and not questa_rete.raggiungibile(str(tmp_path / "manca"))
