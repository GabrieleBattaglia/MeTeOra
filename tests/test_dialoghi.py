# MeTeOra, le prove dei dialoghi: impostazioni, scelta da una lista e marcatori, costruiti veri e mai mostrati.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.51.0, per la finestra delle impostazioni (tappa 3, issue 14, piano 5.8).

"""I dialoghi veri, sul desktop nascosto e senza ShowModal: si leggono le
righe e i nomi, e i tasti arrivano come eventi di wx mandati direttamente
al gestore di EVT_CHAR_HOOK del dialogo, come li manderebbe Windows."""

import pytest
import wx

import dialoghi
import marcatori
import suoni
from marcatori import Marcatori

A = r"C:\Musica\a.mp3"
Z = r"C:\Musica\z.sid"
K_A = marcatori.chiave(A, 50.0)
K_Z = marcatori.chiave(Z, 90.0, 2)


@pytest.fixture
def genitore(app):
    """Una cornice mai mostrata, genitore dei dialoghi."""
    cornice = wx.Frame(None)
    yield cornice
    cornice.Destroy()


def _tasto(dialogo, oggetto, codice=wx.WXK_RETURN, carattere=None):
    """Un tasto premuto su un controllo del dialogo: arriva al suo EVT_CHAR_HOOK."""
    evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
    if carattere is not None:
        evento.SetUnicodeKey(ord(carattere))
        codice = ord(carattere)
    evento.SetKeyCode(codice)
    evento.SetEventObject(oggetto)
    dialogo._tasto(evento)
    return evento


def _etichette(dialogo):
    return [c.GetLabel() for c in dialogo.lista.GetParent().GetChildren() if isinstance(c, wx.StaticText)]


def _righe(dialogo):
    return [dialogo.lista.GetItemText(i) for i in range(dialogo.lista.GetItemCount())]


def _selezionate(dialogo):
    return list(dialogo._selezionate())


def test_finestra_delle_impostazioni(genitore):
    cambi = []
    voci = [("volume", "Volume della musica: 80"), ("passo_volume", "Passo del volume: 5"), ("marcatori", "Marcatori: nessuno")]
    dialogo = dialoghi.FinestraImpostazioni(genitore, voci, lambda chiave, d: cambi.append((chiave, d)))
    try:
        assert dialogo.GetTitle() == "Impostazioni"
        assert _etichette(dialogo) == ["Filtro delle voci:", "Impostazioni. Invio cambia la voce, Esc chiude, Maiuscolo con Tab va al filtro."]
        assert dialogo.lista.GetName() == "Impostazioni"
        assert not dialogo.lista.HasMultipleSelection()
        assert dialogo.lista.GetStrings() == [testo for _chiave, testo in voci]
        assert dialogo.lista.GetSelection() == 0
        # Il pulsante Chiudi e' quello di Esc.
        chiudi = wx.Window.FindWindowById(wx.ID_CANCEL, dialogo)
        assert chiudi is not None and chiudi.GetLabel() == "Chiudi"
        # Invio sulla lista cambia la voce selezionata, dando il dialogo come genitore.
        dialogo.lista.SetSelection(1)
        evento = _tasto(dialogo, dialogo.lista)
        assert cambi == [("passo_volume", dialogo)]
        assert not evento.GetSkipped()
        # Invio sul pulsante, e le lettere sulla lista, vanno per la loro strada.
        assert _tasto(dialogo, chiudi).GetSkipped()
        assert _tasto(dialogo, dialogo.lista, carattere="a").GetSkipped()
        assert len(cambi) == 1
        # La riga si riscrive senza spostare la selezione, anche quando non e' la sua.
        dialogo.aggiorna("passo_volume", "Passo del volume: 7")
        dialogo.aggiorna("volume", "Volume della musica: 120")
        dialogo.aggiorna("sconosciuta", "non c'è")
        assert dialogo.lista.GetStrings() == ["Volume della musica: 120", "Passo del volume: 7", "Marcatori: nessuno"]
        assert dialogo.lista.GetSelection() == 1
        # Il doppio clic fa come Invio.
        clic = wx.CommandEvent(wx.wxEVT_LISTBOX_DCLICK, dialogo.lista.GetId())
        clic.SetEventObject(dialogo.lista)
        dialogo.lista.GetEventHandler().ProcessEvent(clic)
        assert cambi[-1] == ("passo_volume", dialogo)
    finally:
        dialogo.Destroy()


def test_il_filtro_delle_impostazioni(genitore, monkeypatch):
    cambi = []
    voci = [("volume", "Volume della musica: 80"), ("passo_volume", "Passo del volume: 5"), ("velocita", "Velocità: 1.0"),
        ("marcatori", "Marcatori: nessuno"), ("sintesi", "Sintesi dei sottotitoli: automatica, adesso NVDA")]
    dialogo = dialoghi.FinestraImpostazioni(genitore, voci, lambda chiave, d: cambi.append((chiave, d)))
    try:
        # Il filtro viene prima della lista, nell'ordine del Tab, e ha un
        # nome; subito prima della lista ci sono le istruzioni, che Windows le
        # da' come nome, e subito prima del filtro la sua etichetta.
        figli = list(dialogo.lista.GetParent().GetChildren())
        assert figli.index(dialogo.filtro) < figli.index(dialogo.lista)
        assert figli[figli.index(dialogo.lista) - 1].GetLabel().startswith("Impostazioni. Invio cambia la voce")
        assert figli[figli.index(dialogo.filtro) - 1].GetLabel() == "Filtro delle voci:"
        assert dialogo.filtro.GetName() == "Filtro delle voci" and dialogo.filtro.GetValue() == ""
        # Maiuscole e accenti non contano; la selezione resta sulla voce.
        _scegli(dialogo, 1)
        dialogo.filtro.SetValue("VOL")
        assert _righe_della_lista(dialogo) == ["Volume della musica: 80", "Passo del volume: 5"]
        assert dialogo.lista.GetSelection() == 1
        dialogo.filtro.SetValue("velocita")
        assert _righe_della_lista(dialogo) == ["Velocità: 1.0"] and dialogo.lista.GetSelection() == 0
        # Conta solo il nome, non il valore: NVDA sta nel valore della sintesi.
        dialogo.filtro.SetValue("nvda")
        assert _righe_della_lista(dialogo) == ["Nessuna voce contiene nvda."] and dialogo.lista.GetSelection() == 0
        _tasto(dialogo, dialogo.lista)
        assert cambi == []
        # Invio cambia la voce giusta anche con la lista filtrata.
        dialogo.filtro.SetValue("  del   volume ")
        assert _righe_della_lista(dialogo) == ["Passo del volume: 5"]
        _tasto(dialogo, dialogo.lista)
        assert cambi == [("passo_volume", dialogo)]
        # Una voce nascosta si aggiorna lo stesso, e ricompare col testo nuovo.
        dialogo.aggiorna("marcatori", "Marcatori: 3 in 1 file")
        dialogo.aggiorna("passo_volume", "Passo del volume: 7")
        assert _righe_della_lista(dialogo) == ["Passo del volume: 7"]
        dialogo.filtro.SetValue("")
        assert _righe_della_lista(dialogo) == ["Volume della musica: 80", "Passo del volume: 7", "Velocità: 1.0", "Marcatori: 3 in 1 file",
            "Sintesi dei sottotitoli: automatica, adesso NVDA"]
        assert dialogo.lista.GetSelection() == 1
        # Un errore di battitura non fa perdere il posto: la voce scelta torna
        # selezionata quando ricompare, anche dopo la riga senza voci.
        dialogo.filtro.SetValue("vol")
        _scegli(dialogo, 1)
        for scritto in ("volx", "vol", "volu", ""):
            dialogo.filtro.SetValue(scritto)
        assert dialogo.lista.GetStringSelection() == "Passo del volume: 7"
        dialogo.filtro.SetValue("marc")
        assert dialogo.lista.GetStringSelection() == "Marcatori: 3 in 1 file"
        dialogo.filtro.SetValue("")
        assert dialogo.lista.GetStringSelection() == "Passo del volume: 7"
        # Invio nel filtro torna alla lista, senza cambiare niente.
        fuoco = []
        monkeypatch.setattr(dialogo.lista, "SetFocus", lambda: fuoco.append(True))
        evento = _tasto(dialogo, dialogo.filtro)
        assert fuoco == [True] and not evento.GetSkipped() and len(cambi) == 1
        # Le lettere nel filtro vanno al campo.
        assert _tasto(dialogo, dialogo.filtro, carattere="a").GetSkipped()
    finally:
        dialogo.Destroy()


def _righe_della_lista(dialogo):
    return list(dialogo.lista.GetStrings())


def _scegli(dialogo, indice):
    """La selezione mossa da chi usa la lista: su Windows SetSelection non
    manda EVT_LISTBOX, le frecce si'."""
    dialogo.lista.SetSelection(indice)
    evento = wx.CommandEvent(wx.wxEVT_LISTBOX, dialogo.lista.GetId())
    evento.SetEventObject(dialogo.lista)
    evento.SetInt(indice)
    dialogo.lista.GetEventHandler().ProcessEvent(evento)


def test_la_domanda_con_si_e_no(genitore, monkeypatch):
    dialogo = dialoghi.DialogoConferma(genitore, "Eliminare la playlist Rock?", "Elimina playlist")
    try:
        assert dialogo.GetTitle() == "Elimina playlist" and dialogo.domanda.GetLabel() == "Eliminare la playlist Rock?"
        assert (dialogo.si.GetLabelText(), dialogo.no.GetLabelText()) == ("Sì", "No")
        # No e' la risposta predefinita, ed Esc vale No.
        assert dialogo.GetDefaultItem() is dialogo.no and dialogo.GetEscapeId() == wx.ID_NO
        finiti = []
        monkeypatch.setattr(dialogo, "EndModal", finiti.append)
        _tasto(dialogo, dialogo.no, carattere="s")
        _tasto(dialogo, dialogo.no, carattere="N")
        assert finiti == [wx.ID_YES, wx.ID_NO]
        assert _tasto(dialogo, dialogo.no, codice=wx.WXK_ESCAPE).GetSkipped()
        clic = wx.CommandEvent(wx.wxEVT_BUTTON, wx.ID_YES)
        clic.SetEventObject(dialogo.si)
        dialogo.si.GetEventHandler().ProcessEvent(clic)
        assert finiti[-1] == wx.ID_YES
    finally:
        dialogo.Destroy()
    # Una & nella domanda resta com'e'.
    dialogo = dialoghi.DialogoConferma(genitore, "Eliminare la playlist Simon & Garfunkel?", "Elimina playlist")
    try:
        assert dialogo.domanda.GetLabelText() == "Eliminare la playlist Simon & Garfunkel?"
    finally:
        dialogo.Destroy()


def test_finestra_della_scelta(genitore, monkeypatch):
    voci = ["Automatica: Altoparlanti, WASAPI, 3 ms", "Altoparlanti, WASAPI, 3 ms", "Realtek ASIO, ASIO, 23,2 ms, esclusiva: può zittire NVDA"]
    dialogo = dialoghi.FinestraScelta(genitore, "Scheda audio", voci, 2)
    try:
        assert dialogo.GetTitle() == "Scheda audio"
        assert _etichette(dialogo) == ["Scheda audio. Invio conferma, Esc annulla."]
        assert dialogo.lista.GetName() == "Scheda audio"
        assert dialogo.lista.GetStrings() == voci
        assert dialogo.GetSelection() == 2
        assert wx.Window.FindWindowById(wx.ID_OK, dialogo).GetLabel() == "Conferma"
        assert wx.Window.FindWindowById(wx.ID_CANCEL, dialogo).GetLabel() == "Annulla"
        finiti = []
        monkeypatch.setattr(dialogo, "EndModal", finiti.append)
        dialogo.lista.SetSelection(1)
        _tasto(dialogo, dialogo.lista)
        assert finiti == [wx.ID_OK]
        assert dialogo.GetSelection() == 1
    finally:
        dialogo.Destroy()
    # Una scelta fuori dalla lista si porta all'ultima riga.
    dialogo = dialoghi.FinestraScelta(genitore, "Prova", ["uno", "due"], 9)
    try:
        assert dialogo.GetSelection() == 1
    finally:
        dialogo.Destroy()


def _archivio(tmp_path):
    """Due marker su un file, uno sul sottobrano 2 di un SID e uno importato,
    senza percorso."""
    archivio = Marcatori(str(tmp_path / "marcatori.json"))
    archivio.carica()
    archivio.aggiungi(K_A, 3.25, A, 50.0)
    archivio.aggiungi(K_A, 1.0, A, 50.0)
    archivio.aggiungi(K_Z, 61.5, Z, 90.0, 2)
    archivio.importa([{"file": "Importato.mp3", "durata": 60.0, "sottobrano": None, "marker": [{"tempo": 5.0, "nome": "Inizio"}]}])
    return archivio


class _Azioni(dict):
    """Le azioni della finestra principale, che annotano e fanno il minimo."""

    def __init__(self, archivio):
        self.fatte = []
        super().__init__(
            rinomina=lambda k, m, genitore: self.fatte.append(("rinomina", k, m["nome"], genitore)) or archivio.rinomina(k, m, "Nuovo"),
            elimina=lambda scelti, genitore: self.fatte.append(("elimina", [(k, m["nome"]) for k, m in scelti])) or [archivio.togli(k, m) for k, m in scelti],
            cancella_tutto=lambda genitore: self.fatte.append(("cancella_tutto",)) or archivio.cancella_tutto(),
            esporta=lambda scelti, genitore: self.fatte.append(("esporta", [(k, m["nome"]) for k, m in scelti])),
            suono=lambda evento: self._annota(("suono", evento)),
            riscontro=lambda evento, testo: self._annota(("riscontro", evento, testo)),
        )

    def _annota(self, fatta):
        # Come i suoni della finestra principale: solo eventi che esistono.
        assert fatta[1] in suoni.EVENTI, f"evento sconosciuto: {fatta[1]}"
        self.fatte.append(fatta)


class _CampoFinto:
    """Il campo della ricerca, che risponde da solo."""

    def __init__(self, risposta):
        self.risposta = risposta

    def __call__(self, *_a, **_k):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def ShowModal(self):
        return wx.ID_OK

    def GetValue(self):
        return self.risposta


def test_finestra_dei_marcatori(genitore, tmp_path, monkeypatch):
    archivio = _archivio(tmp_path)
    azioni = _Azioni(archivio)
    dialogo = dialoghi.FinestraMarcatori(genitore, archivio, azioni)
    try:
        assert dialogo.GetTitle() == "Marcatori"
        assert _etichette(dialogo) == ["Marcatori. Barra rovesciata cerca, Invio rinomina, Canc elimina le righe selezionate, Esc chiude."]
        assert dialogo.lista.GetName() == "Marcatori"
        assert dialogo.lista.GetColumnCount() == 1 and dialogo.lista.HasFlag(wx.LC_NO_HEADER) and not dialogo.lista.HasFlag(wx.LC_SINGLE_SEL)
        assert wx.Window.FindWindowById(wx.ID_CANCEL, dialogo).GetLabel() == "Chiudi"
        assert {c.GetLabel() for c in dialogo.lista.GetParent().GetChildren() if isinstance(c, wx.Button)} == {"Cancella tutto", "Esporta selezionati", "Chiudi"}
        # Raggruppati per provenienza, in ordine di tempo; il sottobrano e il
        # marker senza percorso si leggono come dice il piano.
        assert _righe(dialogo) == [r"C:\Musica\a.mp3\M2, 0:01", r"C:\Musica\a.mp3\M1, 0:03.250", r"C:\Musica\z.sid, sottobrano 2\M1, 1:01.500",
            r"Importato.mp3\Inizio, 0:05"]
        assert dialogo.lista.GetFocusedItem() == 0 and _selezionate(dialogo) == [0]
        # Invio rinomina la riga col fuoco: il fuoco resta sul marker rinominato.
        dialogo.lista.Select(0, False)
        dialogo.lista.Select(1)
        dialogo.lista.Focus(1)
        assert not _tasto(dialogo, dialogo.lista).GetSkipped()
        assert azioni.fatte == [("rinomina", K_A, "M1", dialogo)]
        assert _righe(dialogo)[1] == r"C:\Musica\a.mp3\Nuovo, 0:03.250"
        assert dialogo.lista.GetFocusedItem() == 1 and _selezionate(dialogo) == [1]
        # Canc elimina le righe selezionate; il fuoco va sulla riga che prende il posto della sua.
        dialogo.lista.Select(2)
        dialogo.lista.Focus(2)
        _tasto(dialogo, dialogo.lista, wx.WXK_DELETE)
        assert azioni.fatte[-1] == ("elimina", [(K_A, "Nuovo"), (K_Z, "M1")])
        assert _righe(dialogo) == [r"C:\Musica\a.mp3\M2, 0:01", r"Importato.mp3\Inizio, 0:05"]
        assert dialogo.lista.GetFocusedItem() == 1 and _selezionate(dialogo) == [1]
        # La barra rovesciata cerca, maiuscole indifferenti, e riparte dalla cima.
        monkeypatch.setattr(dialoghi, "DialogoTesto", _CampoFinto("A.MP3"))
        _tasto(dialogo, dialogo.lista, carattere="\\")
        assert dialogo.lista.GetFocusedItem() == 0 and _selezionate(dialogo) == [0]
        assert azioni.fatte[-2:] == [("suono", "domanda"), ("suono", "ripartito_nei_marcatori")]
        _tasto(dialogo, dialogo.lista, carattere="\\")
        assert azioni.fatte[-1] == ("suono", "ripartito_nei_marcatori")
        monkeypatch.setattr(dialoghi, "DialogoTesto", _CampoFinto("inizio"))
        _tasto(dialogo, dialogo.lista, carattere="\\")
        assert dialogo.lista.GetFocusedItem() == 1 and azioni.fatte[-1] == ("suono", "trovato_nei_marcatori")
        monkeypatch.setattr(dialoghi, "DialogoTesto", _CampoFinto("ritornello"))
        _tasto(dialogo, dialogo.lista, carattere="\\")
        assert azioni.fatte[-1] == ("riscontro", "non_trovato_nei_marcatori", "Nei marcatori non c'è ritornello.")
        assert dialogo.lista.GetFocusedItem() == 1
        # Esporta selezionati passa le righe selezionate.
        dialogo.lista.Select(0)
        dialogo._esporta()
        assert azioni.fatte[-1] == ("esporta", [(K_A, "M2"), (archivio.tutti()[1][0], "Inizio")])
        # Senza righe selezionate non si esporta e non si elimina: lo si dice.
        for i in _selezionate(dialogo):
            dialogo.lista.Select(i, False)
        fatte = len(azioni.fatte)
        dialogo._esporta()
        _tasto(dialogo, dialogo.lista, wx.WXK_DELETE)
        assert [f[:2] for f in azioni.fatte[fatte:]] == [("riscontro", "non_disponibile")] * 2
        # Cancella tutto, e la lista vuota ha una riga che lo dice.
        dialogo._cancella_tutto()
        assert azioni.fatte[-1] == ("cancella_tutto",)
        assert _righe(dialogo) == [dialoghi.NESSUN_MARCATORE]
        fatte = len(azioni.fatte)
        _tasto(dialogo, dialogo.lista)
        _tasto(dialogo, dialogo.lista, wx.WXK_DELETE)
        _tasto(dialogo, dialogo.lista, carattere="\\")
        dialogo._esporta()
        dialogo._cancella_tutto()
        assert azioni.fatte[fatte:] == [("riscontro", "non_disponibile", "Non ci sono marcatori.")] * 5
        # Le altre lettere restano alla lista, per la ricerca per iniziale di Windows.
        assert _tasto(dialogo, dialogo.lista, carattere="m").GetSkipped()
    finally:
        dialogo.Destroy()


def _dieci_marker(tmp_path):
    """Dieci marker, M1 a M10, sullo stesso file, uno al secondo."""
    archivio = Marcatori(str(tmp_path / "dieci.json"))
    archivio.carica()
    for secondo in range(1, 11):
        archivio.aggiungi(K_A, float(secondo), A, 50.0)
    return archivio


def _nome_col_fuoco(dialogo):
    return dialogo._righe[dialogo.lista.GetFocusedItem()][2]["nome"]


@pytest.mark.parametrize(("selezione", "fuoco", "dopo", "atteso"), [
    # Un blocco in mezzo, M4 M5 M6, col fuoco sull'ultima riga del blocco:
    # il fuoco va su M7, che seguiva il blocco, non su M9.
    ([3, 4, 5], 5, ["M1", "M2", "M3", "M7", "M8", "M9", "M10"], "M7"),
    # Una selezione non contigua fatta con Ctrl+Spazio, M2 e M5, col fuoco su
    # M5: il fuoco va su M6, non su M7.
    ([1, 4], 4, ["M1", "M3", "M4", "M6", "M7", "M8", "M9", "M10"], "M6"),
    # Col fuoco sulla prima riga del blocco, o col blocco in fondo, come prima.
    ([3, 4, 5], 3, ["M1", "M2", "M3", "M7", "M8", "M9", "M10"], "M7"),
    ([7, 8, 9], 9, ["M1", "M2", "M3", "M4", "M5", "M6", "M7"], "M7"),
])
def test_canc_porta_il_fuoco_sulla_prima_riga_rimasta(genitore, tmp_path, selezione, fuoco, dopo, atteso):
    archivio = _dieci_marker(tmp_path)
    azioni = _Azioni(archivio)
    dialogo = dialoghi.FinestraMarcatori(genitore, archivio, azioni)
    try:
        for i in _selezionate(dialogo):
            dialogo.lista.Select(i, False)
        for i in selezione:
            dialogo.lista.Select(i)
        dialogo.lista.Focus(fuoco)
        _tasto(dialogo, dialogo.lista, wx.WXK_DELETE)
        assert [m["nome"] for _k, _v, m in dialogo._righe] == dopo
        assert _nome_col_fuoco(dialogo) == atteso
        # Dei marker selezionati non ne resta nessuno: e' selezionata la riga col fuoco.
        assert _selezionate(dialogo) == [dialogo.lista.GetFocusedItem()]
    finally:
        dialogo.Destroy()


def test_finestra_dei_marcatori_vuota(genitore, tmp_path):
    archivio = Marcatori(str(tmp_path / "vuoto.json"))
    archivio.carica()
    dialogo = dialoghi.FinestraMarcatori(genitore, archivio, _Azioni(archivio))
    try:
        assert _righe(dialogo) == ["Nessun marcatore."]
        assert dialogo.scelti() == []
    finally:
        dialogo.Destroy()


def test_dialogo_testo_e_riga_del_marcatore(genitore):
    dialogo = dialoghi.DialogoTesto(genitore, "Nome:", "Rinomina", "M1")
    try:
        assert dialogo.GetValue() == "M1"
    finally:
        dialogo.Destroy()
    voce = {"file": "z.sid", "sottobrano": 3, "percorsi": []}
    assert dialoghi.riga_del_marcatore(voce, {"tempo": 3723.5, "nome": "Assolo"}) == r"z.sid, sottobrano 3\Assolo, 1:02:03.500"


def test_l_invito_a_offrire_un_caffe(genitore, monkeypatch):
    # 1.75.0: come in Tornello. Il fuoco nel testo, Chiudi predefinito, Esc e
    # Invio nel testo chiudono; Dona con PayPal apre il browser.
    import webbrowser

    dialogo = dialoghi.DialogoDonazione(genitore, "Offrimi un caffè su PayPal.")
    try:
        assert dialogo.GetTitle() == "Offri un caffè" and dialogo.testo.GetValue() == "Offrimi un caffè su PayPal."
        assert (dialogo.dona.GetLabelText(), dialogo.chiudi.GetLabelText()) == ("Dona con PayPal", "Chiudi")
        assert dialogo.GetDefaultItem() is dialogo.chiudi and dialogo.GetEscapeId() == wx.ID_NO
        finiti = []
        monkeypatch.setattr(dialogo, "EndModal", finiti.append)
        _tasto(dialogo, dialogo.testo)
        assert finiti == [wx.ID_NO]
        # Sui pulsanti Invio resta loro.
        assert _tasto(dialogo, dialogo.dona).GetSkipped()
        aperti = []
        monkeypatch.setattr(webbrowser, "open", aperti.append)
        clic = wx.CommandEvent(wx.wxEVT_BUTTON, wx.ID_YES)
        clic.SetEventObject(dialogo.dona)
        dialogo.dona.GetEventHandler().ProcessEvent(clic)
        assert aperti == [dialoghi.INDIRIZZO_PAYPAL] and finiti[-1] == wx.ID_YES
        # Un browser che non parte non tiene aperto l'invito.
        monkeypatch.setattr(webbrowser, "open", lambda _indirizzo: 1 / 0)
        dialogo.dona.GetEventHandler().ProcessEvent(clic)
        assert finiti[-1] == wx.ID_YES
    finally:
        dialogo.Destroy()
