# MeTeOra, le prove dell'esploratore delle aperture di massa (2.7.0).
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/11/2026: nasce con la 2.7.0, tappa 17 del piano.

import os

import esploratore
from esploratore import Esploratore
from ricerca import NonRisponde


def _albero(base, nomi):
    """Crea cartelle e file vuoti: i nomi che finiscono con la barra sono cartelle."""
    for nome in nomi:
        percorso = base / nome
        if nome.endswith("/"):
            percorso.mkdir(parents=True, exist_ok=True)
        else:
            percorso.parent.mkdir(parents=True, exist_ok=True)
            percorso.write_bytes(b"")


class _ContatoreFinto:
    def __init__(self):
        self.letture, self.chieste, self.mute, self.rispondono = {}, [], [], []

    def rinfresca(self, cartella, lettura):
        self.letture[cartella] = lettura
        return []

    def chiedi(self, cartelle):
        self.chieste.extend(cartelle)

    def non_risponde(self, cartella):
        self.mute.append(cartella)

    def risponde(self, cartella):
        self.rispondono.append(cartella)
        return []


def test_annuncia_solo_le_cartelle_con_qualcosa_da_suonare(tmp_path):
    # Le cartelle senza niente da suonare, nemmeno sotto, non si annunciano;
    # quelle che hanno musica solo piu' sotto si annunciano con la prima
    # cartella che ne ha, e ogni annunciata si dice finita dopo il suo ramo.
    _albero(tmp_path, ["c.mp3", "A/a.mp3", "A/Vuota/", "B/Sotto/b.mp3", "C/", "C/nota.txt"])
    radice = str(tmp_path)
    a, b, c = (os.path.join(radice, n) for n in "ABC")
    sotto, vuota = os.path.join(b, "Sotto"), os.path.join(a, "Vuota")
    contatore = _ContatoreFinto()
    esp = Esploratore([radice], contatore).avvia()
    esp.aspetta()
    eventi = esp.prendi()
    assert eventi == [
        ("file", radice, ([a, b, c], [os.path.join(radice, "c.mp3")])),
        ("cartella", radice, a), ("file", a, ([vuota], [os.path.join(a, "a.mp3")])), ("finita", a),
        ("cartella", radice, b), ("cartella", b, sotto), ("file", sotto, ([], [os.path.join(sotto, "b.mp3")])), ("finita", sotto), ("finita", b),
        ("finita", radice),
    ]
    assert esp.finita and esp.lette == 6 and esp.annunciate == 3 and esp.file == 3 and esp.prendi() == []
    # Ogni lettura va al contatore, anche delle cartelle vuote.
    assert set(contatore.letture) == {radice, a, vuota, b, sotto, c}
    assert contatore.letture[c] == ([], [])


def test_l_ordine_alfabetico_e_gli_avvisi(tmp_path):
    # In ordine alfabetico, senza badare alle maiuscole, come la plancia; chi
    # aspetta viene avvisato alla fine anche senza avvisi intermedi.
    _albero(tmp_path, ["beta/b.mp3", "Alfa/a.mp3", "gamma/g.mp3"])
    avvisi = []
    esp = Esploratore([str(tmp_path)], avvisa=lambda: avvisi.append(1)).avvia()
    esp.aspetta()
    cartelle = [os.path.basename(e[2]) for e in esp.prendi() if e[0] == "cartella"]
    assert cartelle == ["Alfa", "beta", "gamma"] and avvisi


def test_le_intestazioni_dei_sid_si_leggono_qui(tmp_path, monkeypatch):
    # La plancia le trova pronte: per i SID e i file delle console, non per gli altri.
    _albero(tmp_path, ["uno.sid", "due.nsf", "tre.mp3"])
    lette = []
    monkeypatch.setattr(esploratore.sottobrani, "info", lambda percorso: lette.append(os.path.basename(percorso)))
    esp = Esploratore([str(tmp_path)]).avvia()
    esp.aspetta()
    assert sorted(lette) == ["due.nsf", "uno.sid"]


def test_le_cartelle_che_non_si_leggono_si_contano(tmp_path, monkeypatch):
    _albero(tmp_path, ["A/a.mp3", "B/"])
    vera = esploratore.questo_pc.contenuto

    def contenuto(cartella, al_passo=None):
        if os.path.basename(cartella) == "B":
            raise PermissionError(5, "Accesso negato")
        return vera(cartella)

    monkeypatch.setattr(esploratore.questo_pc, "contenuto", contenuto)
    esp = Esploratore([str(tmp_path)]).avvia()
    esp.aspetta()
    assert esp.illeggibili == 1 and ("cartella", str(tmp_path), str(tmp_path / "A")) in esp.prendi()


def test_in_rete_le_cartelle_mute_si_saltano(tmp_path, monkeypatch):
    # Come nella ricerca: una cartella che tace si salta, alla terza si lascia
    # la radice; e una radice che tace si dice da sola.
    _albero(tmp_path, ["A/a.mp3", "M1/", "M2/", "M3/", "Z/z.mp3"])
    vera = esploratore.questo_pc.contenuto

    def leggi(cartella, fermo=None, attesa=None):
        if os.path.basename(cartella).startswith("M"):
            raise NonRisponde(cartella)
        return vera(cartella)

    monkeypatch.setattr(esploratore, "in_rete", lambda percorso: True)
    monkeypatch.setattr(esploratore, "leggi_in_rete", leggi)
    contatore = _ContatoreFinto()
    esp = Esploratore([str(tmp_path)], contatore).avvia()
    esp.aspetta()
    eventi = esp.prendi()
    # A si e' annunciata, Z no: la radice e' stata lasciata alla terza muta.
    assert ("cartella", str(tmp_path), str(tmp_path / "A")) in eventi
    assert not any(e[0] == "cartella" and e[2].endswith("Z") for e in eventi)
    assert esp.senza_risposta == [str(tmp_path)] and esp.cartelle_mute == []
    assert len(contatore.mute) == 3 and contatore.rispondono == [str(tmp_path)]
    # Una radice che tace subito.
    monkeypatch.setattr(esploratore, "leggi_in_rete", lambda cartella, fermo=None, attesa=None: (_ for _ in ()).throw(NonRisponde(cartella)))
    esp = Esploratore([str(tmp_path)]).avvia()
    esp.aspetta()
    assert esp.senza_risposta == [str(tmp_path)] and esp.prendi() == []


def test_si_ferma(tmp_path, monkeypatch):
    _albero(tmp_path, [f"C{n:02d}/a.mp3" for n in range(30)])
    vera = esploratore.questo_pc.contenuto
    lette = []

    def lenta(cartella, al_passo=None):
        lette.append(cartella)
        if len(lette) == 3:
            esp.fermata = True
        return vera(cartella)

    monkeypatch.setattr(esploratore.questo_pc, "contenuto", lenta)
    esp = Esploratore([str(tmp_path)])
    esp.avvia()
    esp.aspetta()
    assert esp.finita and len(lette) == 3
