# MeTeOra, le prove del filtro delle playlist.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

import pytest

from filtro import ErroreFiltro, Filtro, modello_della_console, senza_commenti
from playlist import Brano

SCHEDE = {
    r"C:\sid\Hubbard_Rob\Commando.sid": {"dim": 5000, "durata": 250.0, "tag": {"titolo": "Commando", "autore": "Rob Hubbard", "anno": 1985},
        "sottobrani": 3, "durate_sid": [250.0, 20.0, 5.0]},
    r"C:\sid\Galway_Martin\Wizball.sid": {"dim": 6000, "durata": 170.0, "tag": {"titolo": "Wizball", "autore": "Martin Galway", "anno": 1987},
        "sottobrani": 1, "durate_sid": [170.0]},
    r"C:\musica\AC-DC - Thunderstruck (live).mp3": {"dim": 8 * 1024 ** 2, "durata": 292.5, "tag": {"autore": "AC/DC", "genere": "Rock", "anno": 1990}},
    r"C:\musica\Città vuota 07.flac": {"dim": 30 * 1024 ** 2, "durata": 180.0, "tag": {"autore": "Mina", "album": "Studio Uno"}},
    r"C:\musica\senza scheda.xm": None,
}


def _passano(testo, brani=None):
    f = Filtro(testo)
    brani = brani or [Brano(p) for p in SCHEDE]
    return [b.nome_del_file for b in brani if f.ammette(b, SCHEDE[b.percorso])]


def test_vuoto_passa_tutto():
    assert len(_passano("")) == 5
    assert Filtro("  \n ").vuoto


def test_parole_in_and_senza_maiuscole_e_accenti():
    assert _passano("rob commando") == ["Commando.sid"]
    assert _passano("CITTA") == ["Città vuota 07.flac"]
    assert _passano("hubbard\ncommando") == ["Commando.sid"]


def test_or_con_la_barra_anche_staccata():
    assert _passano("hubbard|galway") == ["Commando.sid", "Wizball.sid"]
    assert _passano("hubbard | galway") == ["Commando.sid", "Wizball.sid"]
    assert _passano("rob hubbard|galway") == ["Commando.sid"]


def test_not_solo_all_inizio():
    assert _passano("-k=sid") == ["AC-DC - Thunderstruck (live).mp3", "Città vuota 07.flac", "senza scheda.xm"]
    assert _passano("ac-dc") == ["AC-DC - Thunderstruck (live).mp3"]
    assert _passano("-hubbard|galway") == ["AC-DC - Thunderstruck (live).mp3", "Città vuota 07.flac", "senza scheda.xm"]


def test_jolly_e_virgolette():
    assert _passano("w*ball") == ["Wizball.sid"]
    assert _passano("vuota #") == ["Città vuota 07.flac"]
    assert _passano('"thunderstruck (live)"') == ["AC-DC - Thunderstruck (live).mp3"]
    assert _passano('"w*ball"') == []


def test_comandi_numerici():
    assert _passano("t<=3:00") == ["Wizball.sid", "Città vuota 07.flac"]
    assert _passano("t>4:50,5") == ["AC-DC - Thunderstruck (live).mp3"]
    assert _passano("d>10m") == ["Città vuota 07.flac"]
    assert _passano("y<1988 y>=1985") == ["Commando.sid", "Wizball.sid"]
    assert _passano("r>1") == ["Commando.sid"]


def test_tempo_di_un_sottobrano():
    brani = [Brano(r"C:\sid\Hubbard_Rob\Commando.sid", sottobrano=2)]
    assert _passano("t<0:30", brani) == ["Commando.sid"]


def test_comandi_di_testo():
    assert _passano("a=galway") == ["Wizball.sid"]
    assert _passano("g=rock") == ["AC-DC - Thunderstruck (live).mp3"]
    assert _passano("l=studio*") == ["Città vuota 07.flac"]
    assert _passano("k=tracker") == ["senza scheda.xm"]
    assert _passano("k=flac|mp3") == ["AC-DC - Thunderstruck (live).mp3", "Città vuota 07.flac"]
    assert _passano("p=hubbard") == ["Commando.sid"]


def test_saltati():
    brani = [Brano(p, saltato=i == 0) for i, p in enumerate(SCHEDE)]
    assert _passano("s=1", brani) == ["Commando.sid"]
    assert len(_passano("s=0", brani)) == 4


def test_senza_scheda_i_comandi_non_passano():
    brani = [Brano(r"C:\musica\senza scheda.xm")]
    assert _passano("t<10:00", brani) == []
    assert _passano("-t<10:00", brani) == ["senza scheda.xm"]
    assert _passano("scheda", brani) == ["senza scheda.xm"]


@pytest.mark.parametrize("testo", ['"aperte', "hubbard|", "|galway", "x<3", "t<tre", "d>tanto", "y>novanta", "a<rob", "s=forse", "t="])
def test_errori_spiegati(testo):
    with pytest.raises(ErroreFiltro):
        Filtro(testo)


def test_righe_di_commento_col_dollaro():
    assert senza_commenti("$ istruzioni\nrock\n   $ altro commento\n-live") == "rock\n-live"
    # Il cancelletto resta il jolly delle cifre, anche in testa alla riga.
    assert senza_commenti("#1 traccia") == "#1 traccia"
    assert senza_commenti("$ solo commenti\n$ e basta") == ""


def test_modello_della_console():
    testo = "Volume 60. 07:13\nStop. 07:14\nIn riproduzione: SID di Rob Hubbard, 3:00. 08:02"
    assert modello_della_console("volume").search(testo).start() == 0
    # Fra virgolette le maiuscole contano, fuori no.
    assert modello_della_console('"SID"').search(testo) is not None
    assert modello_della_console('"sid"').search(testo) is None
    assert modello_della_console('rob "Hubbard"').search(testo) is not None
    # L'asterisco resta nella stessa riga, il cancelletto vale le cifre.
    assert modello_della_console("volume*stop").search(testo) is None
    assert modello_della_console("in*hubbard").search(testo) is not None
    assert modello_della_console("07:#").search(testo).group() == "07:13"
    # Gli spazi si cercano cosi' come sono.
    assert modello_della_console("volume  60").search(testo) is None
    for sbagliato in ('"aperte', '""', ""):
        with pytest.raises(ErroreFiltro):
            modello_della_console(sbagliato)
