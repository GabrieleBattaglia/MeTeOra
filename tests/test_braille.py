# MeTeOra, le prove della barra braille a blocchi: la divisione nelle celle e la coda con il tempo minimo.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.83.0.

"""L'orologio e le attese sono finti: le prove non aspettano niente."""

import braille


def test_i_blocchi_fra_le_parole():
    assert braille.blocchi("  Ciao   a tutti ", 0) == ["Ciao a tutti"]
    assert braille.blocchi("", 40) == []
    assert braille.blocchi("Ciao a tutti", 40) == ["Ciao a tutti"]
    testo = "Partir effacer sur le Gange la douleur pouvoir parler à un ange"
    pezzi = braille.blocchi(testo, 20)
    assert pezzi == ["Partir effacer sur", "le Gange la douleur", "pouvoir parler à un", "ange"]
    assert all(len(p) <= 20 for p in pezzi) and " ".join(pezzi) == testo
    # Una parola piu' lunga della barra si spezza dove la barra finisce.
    assert braille.blocchi("Supercalifragilistichespiralidoso e basta", 12) == ["Supercalifra", "gilistichesp", "iralidoso e", "basta"]


class _Tempo:
    """L'orologio e le attese finte: avanza() fa passare il tempo e chiama
    le attese scadute, nell'ordine."""

    def __init__(self):
        self.ora = 100.0
        self.attese = []

    def __call__(self):
        return self.ora

    def pianifica(self, secondi, funzione):
        tempo = self

        class Attesa:
            def Stop(self):
                tempo.attese.remove(voce)

        voce = [self.ora + secondi, funzione]
        self.attese.append(voce)
        return Attesa()

    def avanza(self, secondi):
        fine = self.ora + secondi
        while True:
            pronte = sorted((a for a in self.attese if a[0] <= fine + 1e-9), key=lambda a: a[0])
            if not pronte:
                break
            voce = pronte[0]
            self.attese.remove(voce)
            self.ora = voce[0]
            voce[1]()
        self.ora = fine


def _coda():
    tempo, mostrati = _Tempo(), []
    coda = braille.Coda(lambda blocco: mostrati.append((round(tempo.ora - 100, 3), blocco)), tempo.pianifica, tempo)
    return coda, tempo, mostrati


def test_i_blocchi_si_dividono_il_tempo_del_testo():
    coda, tempo, mostrati = _coda()
    # Tre blocchi in nove secondi: ciascuno per la sua parte di lunghezza.
    coda.aggiungi("uno due tre quattro cinque sei", celle=10, minimo=1.0, durata=9.0)
    assert mostrati == [(0.0, "uno due")]
    tempo.avanza(9)
    assert [b for _t, b in mostrati] == ["uno due", "tre", "quattro", "cinque sei"]
    # 27 caratteri in nove secondi: un terzo di secondo per carattere.
    assert [t for t, _b in mostrati] == [0.0, 2.333, 3.333, 5.667]


def test_il_tempo_minimo_crea_la_coda_e_la_coda_aspetta():
    coda, tempo, mostrati = _coda()
    # Senza durata ogni blocco resta il minimo: due secondi.
    coda.aggiungi("Prima riga del sottotitolo", celle=12, minimo=2.0)
    coda.aggiungi("Seconda", celle=12, minimo=2.0)
    assert mostrati == [(0.0, "Prima riga")] and coda.in_fila == 3
    tempo.avanza(1.9)
    assert len(mostrati) == 1
    tempo.avanza(10)
    assert mostrati == [(0.0, "Prima riga"), (2.0, "del"), (4.0, "sottotitolo"), (6.0, "Seconda")]
    # L'ultimo blocco resta il suo minimo anche per il testo che arriva dopo.
    tempo.ora = 100 + 6.5
    coda.aggiungi("Terza", minimo=2.0)
    assert mostrati[-1] == (6.0, "Seconda")
    tempo.avanza(2)
    assert mostrati[-1] == (8.0, "Terza")
    # Passato il minimo, un testo nuovo si mostra subito.
    tempo.avanza(5)
    coda.aggiungi("Quarta", minimo=2.0)
    assert mostrati[-1] == (13.5, "Quarta")


def test_un_testo_nuovo_aspetta_solo_il_minimo():
    # Revisione 1.83.0: un cartello lungo sovrapposto faceva valere 29 secondi
    # alla prima battuta, e le altre aspettavano.
    coda, tempo, mostrati = _coda()
    coda.aggiungi("Cartello lungo", minimo=2.0, durata=29.0)
    tempo.avanza(2.5)
    coda.aggiungi("Battuta 1", minimo=2.0, durata=2.0)
    assert mostrati[-1] == (2.5, "Battuta 1")
    # La parte del tempo vale quando non aspetta nessuno, ma al piu' DURATA_MASSIMA.
    coda.aggiungi("uno due tre quattro", celle=8, minimo=1.0, durata=60.0)
    tempo.avanza(4.5)
    assert mostrati[-1] == (4.5, "uno due")
    tempo.avanza(braille.DURATA_MASSIMA)
    assert [b for _t, b in mostrati[-3:]] == ["uno due", "tre", "quattro"]
    assert mostrati[-2][0] < 4.5 + braille.DURATA_MASSIMA


def test_un_testo_in_ritardo_usa_solo_il_minimo_e_svuota():
    coda, tempo, mostrati = _coda()
    coda.aggiungi("aaaa bbbb cccc", celle=4, minimo=1.0, durata=1.5)
    tempo.avanza(5)
    # Il tempo del testo finisce prima dei blocchi: vale il minimo.
    assert [t for t, _b in mostrati] == [0.0, 1.0, 2.0]
    coda.aggiungi("dddd eeee", celle=4, minimo=3.0)
    coda.svuota()
    assert coda.in_fila == 0 and not tempo.attese
    coda.aggiungi("ffff", minimo=1.0)
    assert mostrati[-1][1] == "ffff"
