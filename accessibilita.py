# MeTeOra, lo stato della selezione per lo screen reader: la plancia dice a NVDA quali voci sono selezionate, con un wx.Accessible.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 20/10/2026: nasce con la 1.111.0, per la issue 21 (tappa 14, punto e).

"""Lo stato della selezione per lo screen reader (issue 21).

La plancia e' un albero di Windows a selezione singola: per Windows la voce
col fuoco e' sempre selezionata, e la selezione multipla la tiene MeTeOra
(1.98.0). NVDA legge l'albero con MSAA e chiede lo stato di ogni voce ad
accState: senza aiuto non dice mai "non selezionato", come invece fa in
Esplora risorse muovendosi con Ctrl e le frecce.
StatoDellaSelezione e' l'oggetto di accessibilita' della plancia. Risponde da
se' solo a GetState: lo stato standard di Windows, letto dall'oggetto che
crea CreateStdAccessibleObject, con "selezionata" secondo la selezione di
MeTeOra e "selezionabile" sempre; la plancia stessa, il figlio 0, si dichiara
a selezione multipla. Tutte le altre domande, nome, ruolo, valore, posto,
figli, fuoco, selezione, wx le inoltra all'oggetto standard, perche' i metodi
di wx.Accessible non ridefiniti rispondono ACC_NOT_IMPLEMENTED. Posizione e
livello NVDA li calcola da se', con i messaggi dell'albero.
Senza la selezione multipla vale lo stato di Windows: la voce col fuoco e'
selezionata, e NVDA tace come prima. Spenta la voce delle impostazioni, e a
finestra chiusa, anche GetState risponde ACC_NOT_IMPLEMENTED.

Le misure, prese il 20 ottobre 2026 sul desktop nascosto, dentro il processo
e da un processo a parte come NVDA (strumenti\\banco.py --plancia):
- senza l'oggetto la plancia non risponde a WM_GETOBJECT, e l'oggetto
  standard lo crea oleacc dentro il processo del lettore; con l'oggetto wx
  risponde anche a 64 bit, e da fuori ogni voce si legge uguale, nome, ruolo,
  stato, valore, descrizione, scorciatoia, azione e posto, tranne i due bit
  voluti;
- wx riconverte gli stati di MSAA uno per uno, ma non ha SIZEABLE, MOVEABLE,
  LINKED, TRAVERSED e HASPOPUP, e PROTECTED lo ha ma non lo riconverte:
  uno stato con uno di questi bit resta quello di Windows, intero;
- wx.Accessible.NotifyEvent in wxPython 4.3.1 non manda niente: il cambio di
  stato si annuncia con NotifyWinEvent;
- da fuori una lettura completa di una voce costa circa 0.7 ms invece di
  0.5, e nome, ruolo e stato per un evento, con l'oggetto chiesto ogni volta
  come fa NVDA, circa 1.7 ms invece di 0.25: il marshaling di COM costa piu'
  dei messaggi, ma resta di solito sotto i 4 ms, con una punta di 7.7 in
  cinque corse del banco; con il filo
  della finestra occupato aspettano tutte e due le strade, perche' anche
  l'oggetto standard parla con l'albero per messaggi;
- in cinque chiusure con il lettore che legge la plancia senza sosta,
  MeTeOra e' uscito pulito, senza crash.
Solo ctypes e oleacc, che sono di Windows: niente pacchetti nuovi.
"""

import ctypes
import sys
from ctypes import wintypes

import wx

import registro

# Gli stati di MSAA, STATE_SYSTEM_* di oleacc.h, per nome.
STATI = {"UNAVAILABLE": 0x1, "SELECTED": 0x2, "FOCUSED": 0x4, "PRESSED": 0x8, "CHECKED": 0x10, "MIXED": 0x20, "READONLY": 0x40,
    "HOTTRACKED": 0x80, "DEFAULT": 0x100, "EXPANDED": 0x200, "COLLAPSED": 0x400, "BUSY": 0x800, "FLOATING": 0x1000, "MARQUEED": 0x2000,
    "ANIMATED": 0x4000, "INVISIBLE": 0x8000, "OFFSCREEN": 0x10000, "SIZEABLE": 0x20000, "MOVEABLE": 0x40000, "SELFVOICING": 0x80000,
    "FOCUSABLE": 0x100000, "SELECTABLE": 0x200000, "LINKED": 0x400000, "TRAVERSED": 0x800000, "MULTISELECTABLE": 0x1000000,
    "EXTSELECTABLE": 0x2000000, "ALERT_LOW": 0x4000000, "ALERT_MEDIUM": 0x8000000, "ALERT_HIGH": 0x10000000, "PROTECTED": 0x20000000,
    "HASPOPUP": 0x40000000}
STATO_SELEZIONATO = STATI["SELECTED"]
STATO_SELEZIONABILE = STATI["SELECTABLE"]
STATO_A_SELEZIONE_MULTIPLA = STATI["MULTISELECTABLE"]
# wx ha gli stessi stati con altri valori, wx.ACC_STATE_SYSTEM_*, e li
# riconverte a uno a uno: PROTECTED c'e' ma non torna (misurato col banco).
_NON_RICONVERTITI = {"PROTECTED"}
DA_MSAA_A_WX = {valore: getattr(wx, f"ACC_STATE_SYSTEM_{nome}") for nome, valore in STATI.items()
    if hasattr(wx, f"ACC_STATE_SYSTEM_{nome}") and nome not in _NON_RICONVERTITI}
RAPPRESENTABILI = sum(DA_MSAA_A_WX)
OBJID_CLIENT = -4
EVENT_OBJECT_STATECHANGE = 0x800A
# Dalla comctl32 6 l'identificativo MSAA di una voce non e' il suo HTREEITEM:
# questi due messaggi li traducono.
_TVM_MAPACCIDTOHTREEITEM = 0x1100 + 42
_TVM_MAPHTREEITEMTOACCID = 0x1100 + 43
_COME_WINDOWS = (wx.ACC_NOT_IMPLEMENTED, 0)


class _GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]


class _Valore(ctypes.Union):
    _fields_ = [("lVal", ctypes.c_long), ("puntatore", ctypes.c_void_p), ("record", ctypes.c_void_p * 2)]


class VARIANT(ctypes.Structure):
    """Il VARIANT di COM, 24 byte a 64 bit. Passato per valore, ctypes lo
    passa per indirizzo a una copia, come vuole Windows a 64 bit."""
    _fields_ = [("vt", ctypes.c_ushort), ("riservato1", ctypes.c_ushort), ("riservato2", ctypes.c_ushort), ("riservato3", ctypes.c_ushort),
        ("u", _Valore)]


VT_I4 = 3
IID_IACCESSIBLE = _GUID(0x618736E0, 0x3C3D, 0x11CF, (ctypes.c_ubyte * 8)(0x81, 0x0C, 0x00, 0xAA, 0x00, 0x38, 0x9B, 0x71))
_oleacc = ctypes.WinDLL("oleacc")
_oleacc.CreateStdAccessibleObject.argtypes = [wintypes.HWND, wintypes.LONG, ctypes.POINTER(_GUID), ctypes.POINTER(ctypes.c_void_p)]
_oleacc.CreateStdAccessibleObject.restype = ctypes.c_long
_oleaut32 = ctypes.WinDLL("oleaut32")
_oleaut32.VariantClear.argtypes = [ctypes.POINTER(VARIANT)]
_user32 = ctypes.WinDLL("user32")
_user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
_user32.SendMessageW.restype = ctypes.c_ssize_t
_user32.NotifyWinEvent.argtypes = [wintypes.DWORD, wintypes.HWND, wintypes.LONG, wintypes.LONG]
_user32.NotifyWinEvent.restype = None
_PROTOTIPI = {}


def chiama(oggetto, indice, *argomenti, tipi):
    """Un metodo di un'interfaccia COM per posto nella sua tabella: per
    IAccessible 0, 1 e 2 sono di IUnknown, da 3 a 6 di IDispatch, poi
    get_accParent e' il 7, get_accName il 10, get_accState il 14. Torna
    l'HRESULT."""
    if (indice, tipi) not in _PROTOTIPI:
        _PROTOTIPI[indice, tipi] = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *tipi)
    tabella = ctypes.cast(oggetto, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return _PROTOTIPI[indice, tipi](tabella[indice])(oggetto, *argomenti)


def figlio(numero):
    """Il VARIANT di un figlio di MSAA: 0 e' l'oggetto stesso."""
    v = VARIANT()
    v.vt = VT_I4
    v.u.lVal = numero
    return v


def rilascia(oggetto):
    if oggetto:
        chiama(oggetto, 2, tipi=())


def oggetto_standard(finestra):
    """L'oggetto standard di Windows per l'area client di una finestra, o
    None: quello che oleacc crea quando la finestra non risponde a
    WM_GETOBJECT. Va rilasciato."""
    uscita = ctypes.c_void_p()
    esito = _oleacc.CreateStdAccessibleObject(finestra, OBJID_CLIENT, ctypes.byref(IID_IACCESSIBLE), ctypes.byref(uscita))
    return uscita.value if esito == 0 and uscita.value else None


def stato_di(oggetto, numero):
    """accState di un figlio, come intero, o None se non risponde."""
    uscita = VARIANT()
    esito = chiama(oggetto, 14, figlio(numero), ctypes.byref(uscita), tipi=(VARIANT, ctypes.POINTER(VARIANT)))
    stato = uscita.u.lVal & 0xFFFFFFFF if esito == 0 and uscita.vt == VT_I4 else None
    _oleaut32.VariantClear(ctypes.byref(uscita))
    return stato


def in_wx(stato):
    """Uno stato di MSAA nei valori di wx, o None se ha un bit che wx
    perderebbe nel riconvertirlo."""
    if stato & ~RAPPRESENTABILI:
        return None
    return sum(valore for bit, valore in DA_MSAA_A_WX.items() if stato & bit)


def numero_della_voce(albero, voce):
    """L'identificativo MSAA di una voce dell'albero, dal suo HTREEITEM
    come intero; 0 se l'albero non la conosce."""
    return _user32.SendMessageW(albero, _TVM_MAPHTREEITEMTOACCID, voce, 0)


class StatoDellaSelezione(wx.Accessible):
    """L'oggetto di accessibilita' della plancia. acceso() dice se la voce
    delle impostazioni e' accesa e la finestra aperta; selezionata(voce),
    con l'HTREEITEM come intero, dice se la voce e' selezionata per MeTeOra,
    o None quando vale cio' che dice Windows."""

    def __init__(self, albero, acceso, selezionata):
        super().__init__(albero)
        self._finestra = albero.GetHandle()
        self._acceso, self._selezionata = acceso, selezionata
        self._standard = None
        self._chiuso = False
        self._errore_scritto = False

    def GetState(self, childId):
        # Un'eccezione qui wx la renderebbe un errore per NVDA: risponde
        # invece Windows, e la pila va nel registro degli errori una volta.
        try:
            return self._stato(childId)
        except Exception:  # noqa: BLE001 - a NVDA non arriva mai un errore
            if not self._errore_scritto:
                self._errore_scritto = True
                registro.problema(*sys.exc_info())
            return _COME_WINDOWS

    def _stato(self, numero):
        if self._chiuso or numero < 0 or not self._acceso():
            return _COME_WINDOWS
        if self._standard is None:
            self._standard = oggetto_standard(self._finestra)
        stato = stato_di(self._standard, numero) if self._standard else None
        if stato is None:
            return _COME_WINDOWS
        if numero == 0:
            stato |= STATO_A_SELEZIONE_MULTIPLA
        else:
            voce = _user32.SendMessageW(self._finestra, _TVM_MAPACCIDTOHTREEITEM, numero, 0)
            if not voce:
                return _COME_WINDOWS
            stato |= STATO_SELEZIONABILE
            selezionata = self._selezionata(voce)
            if selezionata is not None:
                stato = stato | STATO_SELEZIONATO if selezionata else stato & ~STATO_SELEZIONATO
        convertito = in_wx(stato)
        return _COME_WINDOWS if convertito is None else (wx.ACC_OK, convertito)

    def annuncia(self, voce):
        """EVENT_OBJECT_STATECHANGE sulla voce, un HTREEITEM come intero, per
        uno stato cambiato senza che il fuoco si muova: NVDA allora rilegge
        lo stato e dice selezionato o non selezionato."""
        if self._chiuso or not self._acceso():
            return
        numero = numero_della_voce(self._finestra, voce)
        if numero:
            _user32.NotifyWinEvent(EVENT_OBJECT_STATECHANGE, self._finestra, OBJID_CLIENT, numero)

    def chiudi(self):
        """Alla chiusura della finestra: da qui risponde Windows, e l'oggetto
        standard si rilascia."""
        self._chiuso = True
        standard, self._standard = self._standard, None
        rilascia(standard)
