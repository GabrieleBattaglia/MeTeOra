# MeTeOra, la tastiera simulata dentro il processo, per pilotare una finestra wx su un desktop di Windows nascosto, dove SendInput non arriva.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 19/10/2026: nasce con la 1.104.0, per il banco del collaudo sul desktop nascosto (Gabriele).

"""Due modi d'uso, con le stesse regole.

premi() e scrivi() si chiamano da un filo pilota mentre il filo della
finestra fa girare app.MainLoop(): tornano quando il ciclo di wx ha finito il
tasto, anche se il tasto ha aperto un dialogo modale, e nel_filo() e
aspetta() leggono lo stato della finestra dal suo filo.
premi_qui() e scrivi_qui() si chiamano dal filo della finestra senza
MainLoop, come in una prova di pytest: svuotano la coda da se'. Un dialogo
modale aperto dal tasto qui blocca, finche' qualcuno non lo chiude.

Il perche' di tutto: in wxWidgets 3.3.3 EVT_CHAR_HOOK nasce in
wxKeyboardHook, un gancio WH_KEYBOARD del filo (src/msw/window.cpp), che
Windows chiama solo per i tasti veri, quelli della coda d'ingresso. Un
WM_KEYDOWN messo in coda con PostMessage arriva al controllo ma non al
gancio. Qui il gancio lo si rifa' in Python (_gancio_di_wx), come lo fa wx:
se lo tiene un gestore senza Skip, WM_KEYDOWN non parte; altrimenti parte con
PostMessage, e il ciclo di wx fa il resto come con un tasto vero:
tabulazione, Invio, Esc, mnemonici con Alt, TranslateMessage e il controllo.
I modificatori li mette giu' SetKeyboardState, che vale per il filo della
finestra: wx li legge con GetKeyState, Alt invece dal bit 29 di lParam.
"""

import ctypes
import threading
from ctypes import wintypes

import wx

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32.GetKeyboardState.restype = wintypes.BOOL
user32.GetKeyboardState.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
user32.SetKeyboardState.restype = wintypes.BOOL
user32.SetKeyboardState.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
user32.PostMessageW.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = wintypes.LPARAM
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.GetFocus.restype = wintypes.HWND
user32.GetActiveWindow.restype = wintypes.HWND
user32.GetCapture.restype = wintypes.HWND
user32.VkKeyScanW.restype = ctypes.c_short
user32.VkKeyScanW.argtypes = [wintypes.WCHAR]
user32.MapVirtualKeyW.restype = wintypes.UINT
user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.GetKeyState.restype = ctypes.c_short
user32.GetKeyState.argtypes = [ctypes.c_int]
kernel32.GetTickCount.restype = wintypes.DWORD

WM_KEYDOWN, WM_KEYUP, WM_CHAR, WM_SYSKEYDOWN, WM_SYSKEYUP = 0x0100, 0x0101, 0x0102, 0x0104, 0x0105
VK_SHIFT, VK_CONTROL, VK_MENU, VK_F10, VK_F24 = 0x10, 0x11, 0x12, 0x79, 0x87
VK_LSHIFT, VK_RSHIFT, VK_LCONTROL, VK_RCONTROL, VK_LMENU, VK_RMENU = 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5
# Nome del tasto: (codice virtuale, esteso). Frecce, Inizio, Fine, Pagina su
# e giu', Ins e Canc sono estesi: senza quel bit wx li prende per il
# tastierino (WXK_NUMPAD_UP e compagni), e Invio esteso e' WXK_NUMPAD_ENTER.
TASTI = {
    "invio": (0x0D, False), "tn_invio": (0x0D, True), "esc": (0x1B, False), "tab": (0x09, False),
    "spazio": (0x20, False), "indietro": (0x08, False), "canc": (0x2E, True), "ins": (0x2D, True),
    "inizio": (0x24, True), "fine": (0x23, True), "pagsu": (0x21, True), "paggiu": (0x22, True),
    "sinistra": (0x25, True), "su": (0x26, True), "destra": (0x27, True), "giu": (0x28, True),
    "applicazioni": (0x5D, True),
    **{f"f{numero}": (0x6F + numero, False) for numero in range(1, 13)},
    **{f"tn{numero}": (0x60 + numero, False) for numero in range(10)},
}
ATTESA_DEL_TASTO = 10.0
_MODELLO_RIPETUTO = {}


def _risolvi(tasto, maiuscolo, ctrl, alt):
    """Codice virtuale, bit esteso e modificatori del tasto. Un carattere si
    cerca sulla tastiera del filo della finestra con VkKeyScanW, e porta con
    se' i modificatori che gli servono: Maiuscolo per la A, AltGr, cioe' Ctrl
    con Alt, per la chiocciola della tastiera italiana."""
    if isinstance(tasto, str) and len(tasto) > 1:
        if tasto.lower() not in TASTI:
            raise ValueError(f"tasto sconosciuto: {tasto!r}")
        codice, esteso = TASTI[tasto.lower()]
        return codice, esteso, maiuscolo, ctrl, alt
    if isinstance(tasto, str) and len(tasto) == 1 and ord(tasto) <= 0xFFFF:
        risultato = user32.VkKeyScanW(tasto)
        if risultato == -1:
            raise ValueError(f"la tastiera in uso non ha il carattere {tasto!r}")
        bisogni = (risultato >> 8) & 0xFF
        return risultato & 0xFF, False, maiuscolo or bool(bisogni & 1), ctrl or bool(bisogni & 2), alt or bool(bisogni & 4)
    raise ValueError(f"tasto sconosciuto: {tasto!r}")


def _stato_della_tastiera():
    stato = (ctypes.c_ubyte * 256)()
    user32.GetKeyboardState(stato)
    return stato


def _con_i_modificatori(prima, maiuscolo, ctrl, alt):
    """Lo stato della tastiera con i soli modificatori chiesti giu'. Ctrl con
    Alt e' AltGr, che Windows da' come Ctrl sinistro e Alt destro."""
    stato = (ctypes.c_ubyte * 256)(*prima)
    altgr = ctrl and alt
    giu = {
        VK_SHIFT: maiuscolo, VK_LSHIFT: maiuscolo, VK_RSHIFT: False,
        VK_CONTROL: ctrl, VK_LCONTROL: ctrl, VK_RCONTROL: False,
        VK_MENU: alt, VK_LMENU: alt and not altgr, VK_RMENU: altgr,
    }
    for codice, premuto in giu.items():
        stato[codice] = 0x80 if premuto else 0
    return stato


def _lparam(codice, esteso, alt, giu, ripetuto):
    """lParam di WM_KEYDOWN e WM_KEYUP: una ripetizione, codice di scansione,
    bit esteso, bit 29 con Alt giu' (wx ne prende AltDown), bit 30 e 31 per
    il rilascio; il bit 30 alla pressione fa IsAutoRepeat."""
    valore = 1 | ((user32.MapVirtualKeyW(codice, 0) & 0xFF) << 16)
    if esteso:
        valore |= 1 << 24
    if alt:
        valore |= 1 << 29
    if not giu:
        valore |= (1 << 30) | (1 << 31)
    elif ripetuto:
        valore |= 1 << 30
    return valore


def _bersaglio():
    """Il controllo col fuoco, dove la tastiera vera manderebbe il tasto;
    senza fuoco la finestra attiva, e senza quella la prima di wx."""
    hwnd = user32.GetFocus() or user32.GetActiveWindow()
    if not hwnd:
        finestre = [f for f in wx.GetTopLevelWindows() if f.IsShown()] or list(wx.GetTopLevelWindows())
        hwnd = finestre[0].GetHandle() if finestre else None
    return hwnd


def _vk_in_wx(codice, lparam):
    """Il codice wx e il carattere Unicode di un tasto, come li calcola
    wxMSWKeyboard::VKToWX di wxWidgets 3.3.3 (src/msw/window.cpp)."""
    speciali = {
        0x03: wx.WXK_CANCEL, 0x08: wx.WXK_BACK, 0x09: wx.WXK_TAB, 0x0C: wx.WXK_CLEAR, 0x10: wx.WXK_SHIFT,
        0x11: wx.WXK_CONTROL, 0x12: wx.WXK_ALT, 0x13: wx.WXK_PAUSE, 0x14: wx.WXK_CAPITAL, 0x20: wx.WXK_SPACE,
        0x1B: wx.WXK_ESCAPE, 0x29: wx.WXK_SELECT, 0x2A: wx.WXK_PRINT, 0x2B: wx.WXK_EXECUTE, 0x2C: wx.WXK_SNAPSHOT,
        0x2F: wx.WXK_HELP, 0x6A: wx.WXK_NUMPAD_MULTIPLY, 0x6B: wx.WXK_NUMPAD_ADD, 0x6D: wx.WXK_NUMPAD_SUBTRACT,
        0x6E: wx.WXK_NUMPAD_DECIMAL, 0x6F: wx.WXK_NUMPAD_DIVIDE, 0x90: wx.WXK_NUMLOCK, 0x91: wx.WXK_SCROLL,
        0x5B: wx.WXK_WINDOWS_LEFT, 0x5C: wx.WXK_WINDOWS_RIGHT, 0x5D: wx.WXK_WINDOWS_MENU,
        **{0x60 + numero: getattr(wx, f"WXK_NUMPAD{numero}") for numero in range(10)},
        **{0x6F + numero: getattr(wx, f"WXK_F{numero}") for numero in range(1, 25)},
    }
    if codice in speciali:
        wxk = speciali[codice]
        return wxk, (wxk if wxk < wx.WXK_START else wx.WXK_NONE)
    esteso = bool(lparam & (1 << 24))
    doppi = {0x21: (wx.WXK_NUMPAD_PAGEUP, wx.WXK_PAGEUP), 0x22: (wx.WXK_NUMPAD_PAGEDOWN, wx.WXK_PAGEDOWN),
        0x23: (wx.WXK_NUMPAD_END, wx.WXK_END), 0x24: (wx.WXK_NUMPAD_HOME, wx.WXK_HOME),
        0x25: (wx.WXK_NUMPAD_LEFT, wx.WXK_LEFT), 0x26: (wx.WXK_NUMPAD_UP, wx.WXK_UP),
        0x27: (wx.WXK_NUMPAD_RIGHT, wx.WXK_RIGHT), 0x28: (wx.WXK_NUMPAD_DOWN, wx.WXK_DOWN),
        0x2D: (wx.WXK_NUMPAD_INSERT, wx.WXK_INSERT), 0x2E: (wx.WXK_NUMPAD_DELETE, wx.WXK_DELETE)}
    if codice in doppi:
        return doppi[codice][esteso], (wx.WXK_DELETE if codice == 0x2E else wx.WXK_NONE)
    if codice == 0x0D:
        return (wx.WXK_NUMPAD_ENTER if esteso else wx.WXK_RETURN), wx.WXK_RETURN
    if codice in (0xBA, 0xBB, 0xBC, 0xBD, 0xBE, 0xBF, 0xC0, 0xDB, 0xDC, 0xDD, 0xDE, 0xDF, 0xE2):
        wxk = user32.MapVirtualKeyW(codice, 2)
        if wxk & 0x80000000:
            # Un tasto morto: wx non da' niente.
            wxk = wx.WXK_NONE
        carattere = wxk
        if wxk > 255:
            # Un segno fuori da Latin-1: wx da' il tasto della tastiera americana.
            americana = [wx.WXK_NONE, wx.WXK_ESCAPE, *map(ord, "1234567890-="), wx.WXK_BACK, wx.WXK_TAB,
                *map(ord, "QWERTYUIOP[]"), wx.WXK_RETURN, wx.WXK_CONTROL, *map(ord, "ASDFGHJKL;'`"), wx.WXK_SHIFT,
                *map(ord, "\\ZXCVBNM,./")]
            scansione = user32.MapVirtualKeyW(codice, 0)
            wxk = americana[scansione] if scansione < len(americana) else wx.WXK_NONE
        return wxk, carattere
    if 0x30 <= codice <= 0x39 or 0x41 <= codice <= 0x5A:
        return codice, codice
    return wx.WXK_NONE, codice


def _modello_ripetuto():
    """Un wx.KeyEvent nato da wx con IsAutoRepeat vero, da clonare: wxPython
    non ha come impostare IsAutoRepeat in un evento fatto in Python. Lo da'
    una cornice d'appoggio mai mostrata, con un F24 ripetuto mandato con
    SendMessage, che va dritto alla sua procedura di finestra e non tocca la
    coda. La cornice si distrugge subito; wx la toglie del tutto al primo
    momento libero del ciclo."""
    if "evento" not in _MODELLO_RIPETUTO:
        appoggio = wx.Frame(None)
        appoggio.Bind(wx.EVT_KEY_DOWN, lambda evento: _MODELLO_RIPETUTO.setdefault("evento", evento.Clone()))
        user32.SendMessageW(appoggio.GetHandle(), WM_KEYDOWN, VK_F24, _lparam(VK_F24, False, False, True, True))
        appoggio.Destroy()
    return _MODELLO_RIPETUTO.get("evento")


def _gancio_di_wx(codice, lparam):
    """Quello che fa wxKeyboardHook di wxWidgets 3.3.3 per una pressione
    vera: l'evento va al controllo col fuoco, o alla finestra attiva, e
    risale fino alla finestra di primo livello. Torna vero se il gancio ha
    tenuto il tasto: allora wx lo butta, e WM_KEYDOWN non parte."""
    wxk, carattere = _vk_in_wx(codice, lparam)
    if (wxk == wx.WXK_NONE and carattere == wx.WXK_NONE) or user32.GetCapture():
        return False
    fuoco = wx.Window.FindFocus() or wx.GetActiveWindow()
    modello = _modello_ripetuto() if lparam & (1 << 30) else None
    if modello is not None:
        evento = modello.Clone()
        evento.SetEventType(wx.wxEVT_CHAR_HOOK)
        evento.ResumePropagation(wx.EVENT_PROPAGATE_MAX)
        evento.Skip(False)
    else:
        evento = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
    evento.SetId(fuoco.GetId() if fuoco else wx.ID_ANY)
    evento.SetEventObject(fuoco)
    evento.SetShiftDown(user32.GetKeyState(VK_SHIFT) < 0)
    evento.SetControlDown(user32.GetKeyState(VK_CONTROL) < 0)
    evento.SetAltDown(bool(lparam & (1 << 29)))
    evento.SetMetaDown(False)
    evento.SetRawKeyCode(codice)
    evento.SetRawKeyFlags(lparam & 0xFFFFFFFF)
    evento.SetTimestamp(kernel32.GetTickCount() & 0x7FFFFFFF)
    evento.SetKeyCode(wxk)
    evento.SetUnicodeKey(carattere)
    gestore = fuoco.GetEventHandler() if fuoco else wx.GetApp()
    return bool(gestore and gestore.SafelyProcessEvent(evento)) and not evento.IsNextEventAllowed()


def _pressione(esito, tasto, maiuscolo, ctrl, alt, ripetuto, esteso, prima_del_gancio=None):
    """La pressione, nel filo della finestra: modificatori giu', il gancio, e
    WM_KEYDOWN se il gancio non ha tenuto il tasto. prima_del_gancio parte
    subito prima del gancio, che puo' aprire un dialogo modale e non tornare
    finche' il dialogo e' aperto."""
    codice, esteso_di_suo, maiuscolo, ctrl, alt = _risolvi(tasto, maiuscolo, ctrl, alt)
    if esteso is None:
        esteso = esteso_di_suo
    di_sistema = not ctrl and (alt or codice == VK_F10)
    giu, su = (WM_SYSKEYDOWN, WM_SYSKEYUP) if di_sistema else (WM_KEYDOWN, WM_KEYUP)
    esito["prima"] = _stato_della_tastiera()
    stato = _con_i_modificatori(esito["prima"], maiuscolo, ctrl, alt)
    stato[codice] = 0x80
    user32.SetKeyboardState(stato)
    esito["rilascio"] = (codice, esteso, alt, su)
    lparam = _lparam(codice, esteso, alt, True, ripetuto)
    if prima_del_gancio is not None:
        prima_del_gancio()
    esito["tenuto"] = _gancio_di_wx(codice, lparam)
    if esito["tenuto"] or esito.get("rilasciato"):
        # Tenuto dal gancio, o arrivato al rilascio dentro un dialogo modale
        # aperto dal gancio e gia' chiuso: la pressione non parte, come con wx.
        return
    hwnd = _bersaglio()
    if not hwnd:
        raise RuntimeError("nessuna finestra a cui mandare il tasto")
    esito["hwnd"] = hwnd
    user32.PostMessageW(hwnd, giu, codice, lparam)


def _rilascio(esito):
    """Il rilascio, nel filo della finestra: il tasto su, e WM_KEYUP al
    fuoco di adesso, come la tastiera vera dopo un dialogo appena aperto."""
    esito["rilasciato"] = True
    codice, esteso, alt, su = esito["rilascio"]
    stato = _stato_della_tastiera()
    stato[codice] = 0
    user32.SetKeyboardState(stato)
    hwnd = _bersaglio()
    if hwnd:
        user32.PostMessageW(hwnd, su, codice, _lparam(codice, esteso, alt, False, False))


def _rimetti(esito):
    if "prima" in esito:
        user32.SetKeyboardState(esito["prima"])


# Il modo col filo pilota.

def nel_filo(funzione, *argomenti, attesa=ATTESA_DEL_TASTO):
    """Esegue funzione nel filo della finestra e ne rende il risultato, o ne
    rilancia l'eccezione. Gira anche mentre e' aperto un dialogo modale."""
    if wx.IsMainThread():
        return funzione(*argomenti)
    fatto = threading.Event()
    esito = {}

    def esegui():
        try:
            esito["valore"] = funzione(*argomenti)
        except BaseException as errore:  # noqa: BLE001 - la rilancia il filo pilota
            esito["errore"] = errore
        finally:
            fatto.set()

    wx.CallAfter(esegui)
    if not fatto.wait(attesa):
        raise TimeoutError(f"nel_filo: {funzione!r} non ha risposto in {attesa} secondi")
    if "errore" in esito:
        raise esito["errore"]
    return esito.get("valore")


def aspetta(condizione, attesa=5.0, passo=0.02):
    """Aspetta che condizione, chiesta nel filo della finestra, diventi vera."""
    import time

    scadenza = time.monotonic() + attesa
    while time.monotonic() < scadenza:
        if nel_filo(condizione):
            return True
        time.sleep(passo)
    return False


def premi(tasto, maiuscolo=False, ctrl=False, alt=False, ripetuto=False, esteso=None, attesa=ATTESA_DEL_TASTO):
    """Preme e rilascia un tasto come la tastiera vera, nel controllo col
    fuoco: tasto e' un nome di TASTI o un carattere. Si chiama dal filo
    pilota mentre il filo della finestra fa girare MainLoop. Torna quando il
    ciclo di wx ha elaborato la pressione, il WM_CHAR che ne fa
    TranslateMessage e il rilascio, anche se il tasto ha aperto un dialogo
    modale. La barriera e' un timer di wx: Windows da' WM_TIMER solo a coda
    vuota. Il primo timer parte prima del gancio, cosi' scatta anche dentro
    il ciclo di un dialogo modale aperto dal gancio. Rende il controllo a cui
    e' andata la pressione, o None se il gancio l'ha tenuta."""
    if wx.IsMainThread():
        raise RuntimeError("premi va chiamata dal filo pilota; dal filo della finestra c'e' premi_qui")
    fatto = threading.Event()
    esito = {}

    def fine():
        try:
            _rimetti(esito)
        finally:
            fatto.set()

    def rilascio():
        if "errore" in esito:
            # La pressione e' fallita e fine() e' gia' passata: un rimetti in
            # ritardo toccherebbe lo stato del tasto dopo.
            return
        try:
            _rilascio(esito)
            wx.CallLater(1, fine)
        except BaseException as errore:  # noqa: BLE001 - la rilancia il filo pilota
            esito["errore"] = errore
            fine()

    def pressione():
        try:
            _pressione(esito, tasto, maiuscolo, ctrl, alt, ripetuto, esteso, prima_del_gancio=lambda: wx.CallLater(1, rilascio))
        except BaseException as errore:  # noqa: BLE001 - la rilancia il filo pilota
            esito["errore"] = errore
            fine()

    wx.CallAfter(pressione)
    if not fatto.wait(attesa):
        raise TimeoutError(f"premi({tasto!r}): il ciclo di wx non ha risposto in {attesa} secondi")
    if "errore" in esito:
        raise esito["errore"]
    return esito.get("hwnd")


def _carattere_postato(carattere):
    """Un carattere che la tastiera in uso non ha: solo WM_CHAR, in UTF-16,
    al controllo col fuoco. Non passa da EVT_CHAR_HOOK ne' da EVT_KEY_DOWN."""
    hwnd = _bersaglio()
    dati = carattere.encode("utf-16-le")
    for posto in range(0, len(dati), 2):
        user32.PostMessageW(hwnd, WM_CHAR, int.from_bytes(dati[posto:posto + 2], "little"), 1)


def _sceglie(carattere):
    """Come scrivere un carattere: un nome di TASTI, il carattere stesso,
    o None se la tastiera in uso non lo ha."""
    if carattere == "\n":
        return "invio"
    if carattere == "\t":
        return "tab"
    if ord(carattere) <= 0xFFFF and user32.VkKeyScanW(carattere) != -1:
        return carattere
    return None


def scrivi(testo, attesa=ATTESA_DEL_TASTO):
    """Scrive testo nel controllo col fuoco, un tasto per carattere, con i
    tasti che lo danno sulla tastiera in uso: passano da EVT_CHAR_HOOK come
    quelli veri, e un gancio che non fa Skip li ferma, come davvero. A capo
    e' Invio, la tabulazione e' Tab. Un carattere che la tastiera non ha
    arriva come solo WM_CHAR. Rende i caratteri mandati cosi'."""
    soli = []
    for carattere in testo:
        tasto = nel_filo(_sceglie, carattere, attesa=attesa)
        if tasto is not None:
            premi(tasto, attesa=attesa)
            continue
        fatto = threading.Event()
        esito = {}

        def manda(carattere=carattere, fatto=fatto, esito=esito):
            try:
                _carattere_postato(carattere)
                wx.CallLater(1, fatto.set)
            except BaseException as errore:  # noqa: BLE001 - la rilancia il filo pilota
                esito["errore"] = errore
                fatto.set()

        wx.CallAfter(manda)
        if not fatto.wait(attesa):
            raise TimeoutError(f"scrivi({carattere!r}): il ciclo di wx non ha risposto in {attesa} secondi")
        if "errore" in esito:
            raise esito["errore"]
        soli.append(carattere)
    return soli


# Il modo senza MainLoop, dal filo della finestra.

def _svuota_la_coda(giri=500):
    """Elabora con il ciclo di wx, che fa anche tabulazione, mnemonici e
    TranslateMessage, i messaggi in coda e gli eventi rimandati con
    CallAfter, finche' non resta niente. Senza un ciclo attivo, come in
    pytest, ne attiva uno per l'occasione."""
    ciclo = wx.EventLoopBase.GetActive()
    attivatore = None
    if ciclo is None:
        ciclo = wx.GUIEventLoop()
        attivatore = wx.EventLoopActivator(ciclo)
    applicazione = wx.GetApp()
    try:
        for _ in range(giri):
            if ciclo.Pending():
                ciclo.Dispatch()
            elif applicazione.HasPendingEvents():
                applicazione.ProcessPendingEvents()
            else:
                break
    finally:
        del attivatore


def premi_qui(tasto, maiuscolo=False, ctrl=False, alt=False, ripetuto=False, esteso=None):
    """Come premi, ma dal filo della finestra e senza MainLoop: svuota la
    coda da se' dopo la pressione e dopo il rilascio. Un tasto che apre un
    dialogo modale qui non torna finche' il dialogo e' aperto."""
    esito = {}
    try:
        _pressione(esito, tasto, maiuscolo, ctrl, alt, ripetuto, esteso)
        _svuota_la_coda()
        _rilascio(esito)
        _svuota_la_coda()
    finally:
        _rimetti(esito)
    return esito.get("hwnd")


def scrivi_qui(testo):
    """Come scrivi, ma dal filo della finestra e senza MainLoop."""
    soli = []
    for carattere in testo:
        tasto = _sceglie(carattere)
        if tasto is not None:
            premi_qui(tasto)
            continue
        _carattere_postato(carattere)
        _svuota_la_coda()
        soli.append(carattere)
    return soli
