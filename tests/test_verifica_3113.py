# MeTeOra, le prove dei difetti trovati dalle due verifiche del 12 novembre 2026.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 12/11/2026: nasce con la 3.11.3. Nella 3.11.4 il brano sale subito in cima, e la coda ricorda l'ordine di prima.

import types

import finestra as modulo
from playlist import Brano, Coda


def _letti(finestra, monkeypatch):
    detti = []
    monkeypatch.setattr(finestra._sintesi, "dici", lambda testo, _scelta, dove, interrompi=False: detti.append((testo, dove)))
    monkeypatch.setattr(finestra._sintesi, "scelta", lambda _chiave: "nvda")
    return detti


def _minuto(finestra, monkeypatch, pl, brano, durata=None):
    """Un motore finto che suona brano da pl, e il conto dei secondi."""
    finto = types.SimpleNamespace(in_corso=brano.percorso, posizione=0.0, in_pausa=False, volume=100, durata=durata)
    orologio = [100.0]
    monkeypatch.setattr(finestra, "motore", finto)
    monkeypatch.setattr(finestra, "_scatto_delle_statistiche", lambda: None)
    coda = Coda()
    coda.imposta(pl, brano)
    monkeypatch.setattr(finestra, "coda", coda)
    monkeypatch.setattr(modulo.time, "monotonic", lambda: orologio[0])

    def secondi(n):
        for _i in range(n):
            orologio[0] += 1.0
            finto.posizione += 1.0
            finestra._guarda_l_indirizzo()

    return secondi


def test_la_lista_che_suona_non_rimbalza(finestra, monkeypatch):
    # Un brano degli Indirizzi ascoltato un minuto sale subito in cima, e la
    # coda continua nell'ordine di prima: il seguente non e' il primo, che
    # farebbe rimbalzare la fila fra due brani (3.11.4).
    brani = [Brano(f"https://x.it/{n}", titolo=n) for n in "ABCD"]
    finestra.archivio.indirizzi.brani = list(brani)
    secondi = _minuto(finestra, monkeypatch, finestra.archivio.indirizzi, brani[1])
    secondi(62)
    assert [b.titolo for b in finestra.archivio.indirizzi.brani] == ["B", "A", "C", "D"]
    assert finestra.coda.successivo() is brani[2] and finestra.coda.precedente() is brani[0]
    monkeypatch.undo()


def test_una_radio_delle_recenti_sale_subito_in_cima(finestra, monkeypatch):
    # Il collaudo della 3.8.2, fallito nella 3.11.3: la radio ascoltata dal
    # fondo delle Recenti e' in cima quando si riapre il ramo, anche se suona.
    radio = [Brano(f"http://x/{n}.mp3", titolo=n, radio={"uuid": n, "paese": "IT"}) for n in "ABC"]
    finestra.archivio.radio.brani = list(radio)
    secondi = _minuto(finestra, monkeypatch, finestra.archivio.radio, radio[2])
    secondi(59)
    assert [b.titolo for b in finestra.archivio.radio.brani] == ["A", "B", "C"]
    secondi(3)
    assert [b.titolo for b in finestra.archivio.radio.brani] == ["C", "A", "B"]
    assert finestra.coda.successivo() is None and finestra.coda.precedente() is radio[1]
    # Con la ripetizione della lista si riparte dal primo di prima, non da lei.
    assert finestra._da_capo(None) == (finestra.archivio.radio, radio[0], None)
    monkeypatch.undo()


def test_un_brano_breve_entra_se_ascoltato_fino_in_fondo(finestra, monkeypatch):
    pl = modulo.Playlist("Ricerca di x", [], cartella="")
    pl.contenuti = True
    brano = Brano("https://x.it/breve", titolo="Breve")
    pl.brani.append(brano)
    secondi = _minuto(finestra, monkeypatch, pl, brano, durata=40.0)
    secondi(38)
    assert not finestra.archivio.indirizzi.brani
    secondi(2)
    assert [b.percorso for b in finestra.archivio.indirizzi.brani] == ["https://x.it/breve"]
    monkeypatch.undo()


def test_un_salto_ricomincia_capitolo_e_minuto(finestra, monkeypatch):
    saltati = []
    monkeypatch.setattr(finestra.motore, "vai_a", saltati.append)
    finestra._capitolo_visto = ("x", 1, 10.0, 100.0)
    finestra._indirizzo_visto = ("x", 0.0, 10.0, 100.0, False)
    finestra._vai_a(42.0)
    assert saltati == [42.0] and finestra._capitolo_visto is None and finestra._indirizzo_visto is None


def test_con_d_spento_la_console_letta_non_dice_titoli_e_capitoli(finestra, monkeypatch):
    detti = _letti(finestra, monkeypatch)
    finestra.impostazioni["console_letta"] = "entrambi"
    finestra.impostazioni["sottotitoli"] = False
    monkeypatch.setattr(type(finestra.motore), "in_corso", property(lambda self: "http://x/radio.mp3"))
    finestra._titolo_in_onda("Lucio Dalla - Caruso")
    finestra._leggi_le_righe()
    assert finestra._righe[-1].startswith("In onda: Lucio Dalla - Caruso.") and not detti
    # Con D acceso lo leggono la sintesi e il braille dei sottotitoli, e la
    # console letta non lo ripete.
    finestra.impostazioni["sottotitoli"] = True
    finestra.impostazioni["destinazione"] = "entrambi"
    finestra._titolo_in_onda("Mina - Se telefonando")
    finestra._leggi_le_righe()
    assert ("In onda: Mina - Se telefonando.", "sintesi") in detti and ("In onda: Mina - Se telefonando.", "entrambi") not in detti


def test_la_guida_si_legge_solo_nella_prima_riga(finestra, monkeypatch):
    detti = _letti(finestra, monkeypatch)
    finestra.impostazioni["console_letta"] = "braille"
    finestra._stampa("manuale", ["Prima riga", "Seconda", "Terza"], porta_il_fuoco=False)
    finestra._leggi_le_righe()
    assert [t for t, _d in detti] == ["Prima riga"]


def test_canc_sulle_recenti_aggiorna_il_ramo(finestra, monkeypatch):
    uno = Brano("http://x/1.mp3", titolo="Uno", radio={"uuid": "u1", "paese": "IT"})
    due = Brano("http://x/2.mp3", titolo="Due", radio={"uuid": "u2", "paese": "IT"})
    finestra.archivio.metti_la_radio(due)
    finestra.archivio.metti_la_radio(uno)
    finestra.albero.Expand(finestra.nodo_radio)
    recenti = next(v for v in finestra._figli(finestra.nodo_radio) if finestra.albero.GetItemText(v).startswith("Recenti"))
    finestra.albero.Expand(recenti)
    finestra._seleziona(next(iter(finestra._figli(recenti))))
    finestra._togli(finestra.archivio.radio, finestra.archivio.radio.brani[0])
    assert finestra.albero.GetItemText(recenti) == "Recenti, 1 radio"
    figli = list(finestra._figli(recenti))
    assert len(figli) == 1 and finestra._voce_corrente() == figli[0] and finestra._dati(figli[0])["brano"].titolo == "Due"


def test_i_doppioni_non_contano_fra_i_risultati_nuovi(finestra):
    pl = modulo.Playlist("Ricerca di x", [], cartella="")
    pl.contenuti = True
    finestra._contenuti_trovati = {"playlist": pl, "testo": "x", "in_corso": True, "pagina": 1, "altri": False, "nuovi": 0}
    finestra._numero_della_ricerca = 7
    pl.brani.append(Brano("https://x.it/a", titolo="A"))
    for indirizzo in ("https://x.it/a", "https://x.it/b", "https://x.it/a"):
        finestra._contenuto_trovato(7, (indirizzo, indirizzo[-1], None, None))
    finestra._contenuti_finiti(7, 3)
    assert "Un altro risultato per x: ora sono 2." in finestra._righe[-1] and finestra._contenuti_trovati["altri"]
    # Una pagina che fallisce lascia la voce, per riprovare.
    finestra._contenuti_trovati.update(in_corso=True, pagina=2, nuovi=0)
    finestra._contenuti_finiti(7, modulo.indirizzi.ErroreIndirizzo("rete assente"))
    assert finestra._contenuti_trovati["altri"] and finestra._contenuti_trovati["pagina"] == 1


def test_una_registrazione_vuota_non_e_un_file_prodotto(finestra):
    reg = types.SimpleNamespace(titolo="Rai Radio 3", secondi=0.0, byte=0, formato="mp3", dal_vivo=True)
    finestra._registrazione_fermata(reg, None)
    assert finestra._statistiche.dati["conti"].get("registrazioni_finite", 0) == 0


def test_con_gli_effetti_a_parte_la_scheda_della_musica_resta_la_sua(finestra):
    musica = {"dispositivo": "Altoparlanti", "interfaccia": "Windows WASAPI", "indice": 3}
    finestra._uscita_della_musica = musica
    finestra.impostazioni["scheda_effetti"] = {}
    assert finestra._scheda_della_musica_in_uso() is not musica or musica is None
    finestra.impostazioni["scheda_effetti"] = {"dispositivo": "Cuffie", "interfaccia": "Windows WASAPI"}
    assert finestra._scheda_della_musica_in_uso() is musica
