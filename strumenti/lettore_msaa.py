# MeTeOra, il lettore MSAA del banco: fa la parte di NVDA, da un processo a parte, sul desktop nascosto dove gira MeTeOra.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 20/10/2026: nasce con la 1.111.0, per misurare lo stato della selezione dato a NVDA dalla plancia (issue 21).

"""Il lettore MSAA del banco della plancia.

Uso, lo lancia strumenti\\banco.py --plancia:
  python strumenti\\lettore_msaa.py DESKTOP FINESTRA PROCESSO

DESKTOP e' il nome del desktop nascosto di MeTeOra, FINESTRA la maniglia
della plancia e PROCESSO il numero del processo di MeTeOra. Il lettore passa
a quel desktop prima di aprire COM, perche' i messaggi delle finestre non
attraversano i desktop, e poi fa cio' che fa NVDA con un albero di Windows:
- si aggancia da fuori, WINEVENT_OUTOFCONTEXT, agli eventi di fuoco, di
  selezione e di cambio di stato del processo di MeTeOra;
- per ogni evento, quando il suo ciclo arriva a guardarlo, chiede l'oggetto
  con AccessibleObjectFromEvent, cioe' con WM_GETOBJECT alla plancia, e ne
  legge nome, ruolo e stato attraverso il marshaling di COM;
- lo stesso fa con l'oggetto standard di Windows creato qui, con
  CreateStdAccessibleObject: e' quello che NVDA legge oggi, quando la
  plancia a WM_GETOBJECT non risponde.
I comandi arrivano da stdin, una riga JSON ciascuno, e le risposte vanno su
stdout, una riga JSON ciascuna:
- {"comando": "leggi", "figli": [...], "giri": n, "oggetti": [...]}: tutto
  cio' che un client legge delle voci date, e della plancia stessa, con i
  tempi in microsecondi, dall'oggetto della plancia, "plancia", e da quello
  standard, "standard": di partenza da tutti e due;
- {"comando": "eventi"}: gli eventi arrivati da allora, con le letture;
- {"comando": "martella", "figli": [...], "file": percorso}: da qui legge
  le voci date senza sosta, come NVDA che tiene il fuoco, mentre MeTeOra si
  chiude; finisce dopo 200 letture fallite di fila, o all'uscita, e scrive i
  conti nel file;
- {"comando": "esci"}, o stdin chiuso.
Solo ctypes e oleacc, come in MeTeOra: niente comtypes ne' pywin32.
"""

import contextlib
import ctypes
import json
import queue
import sys
import threading
import time
from ctypes import wintypes

oleacc = ctypes.WinDLL("oleacc")
ole32 = ctypes.WinDLL("ole32")
oleaut32 = ctypes.WinDLL("oleaut32")
user32 = ctypes.WinDLL("user32", use_last_error=True)


class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]


class _Valore(ctypes.Union):
    _fields_ = [("lVal", ctypes.c_long), ("puntatore", ctypes.c_void_p), ("record", ctypes.c_void_p * 2)]


class VARIANT(ctypes.Structure):
    """24 byte a 64 bit: per valore, ctypes lo passa per indirizzo come vuole Windows."""
    _fields_ = [("vt", ctypes.c_ushort), ("r1", ctypes.c_ushort), ("r2", ctypes.c_ushort), ("r3", ctypes.c_ushort), ("u", _Valore)]


def _guid(testo):
    g = GUID()
    ole32.CLSIDFromString(ctypes.c_wchar_p(testo), ctypes.byref(g))
    return g


IID_IACCESSIBLE = _guid("{618736E0-3C3D-11CF-810C-00AA00389B71}")
VT_EMPTY, VT_I4, VT_BSTR, VT_DISPATCH = 0, 3, 8, 9
OBJID_CLIENT = -4
WM_GETOBJECT = 0x003D
STATO_SELEZIONATO, STATO_CON_IL_FUOCO, STATO_SELEZIONABILE = 0x2, 0x4, 0x200000
EVENTI = {0x8005: "fuoco", 0x8006: "selezione", 0x8007: "aggiunta", 0x8008: "tolta", 0x8009: "dentro", 0x800A: "stato", 0x800C: "nome"}

oleacc.AccessibleObjectFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]
oleacc.AccessibleObjectFromWindow.restype = ctypes.c_long
oleacc.AccessibleObjectFromEvent.argtypes = [wintypes.HWND, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(VARIANT)]
oleacc.AccessibleObjectFromEvent.restype = ctypes.c_long
oleacc.CreateStdAccessibleObject.argtypes = [wintypes.HWND, wintypes.LONG, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]
oleacc.CreateStdAccessibleObject.restype = ctypes.c_long
oleaut32.SysStringLen.argtypes = [ctypes.c_void_p]
oleaut32.SysStringLen.restype = wintypes.UINT
oleaut32.SysFreeString.argtypes = [ctypes.c_void_p]
oleaut32.VariantClear.argtypes = [ctypes.POINTER(VARIANT)]
ole32.CoInitialize.argtypes = [ctypes.c_void_p]
user32.OpenDesktopW.restype = wintypes.HANDLE
user32.OpenDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
user32.SetThreadDesktop.argtypes = [wintypes.HANDLE]
user32.SendMessageTimeoutW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM, wintypes.UINT, wintypes.UINT,
    ctypes.POINTER(ctypes.c_size_t)]
user32.SendMessageTimeoutW.restype = ctypes.c_ssize_t
_RICHIAMO = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND, wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)
user32.SetWinEventHook.restype = wintypes.HANDLE
user32.SetWinEventHook.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.HMODULE, _RICHIAMO, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD]
user32.UnhookWinEvent.argtypes = [wintypes.HANDLE]
user32.MsgWaitForMultipleObjects.argtypes = [wintypes.DWORD, ctypes.c_void_p, wintypes.BOOL, wintypes.DWORD, wintypes.DWORD]
user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]

# Le chiamate di IAccessible per posto nella tabella dei metodi: IUnknown,
# poi IDispatch, poi IAccessible.
_PROTOTIPI = {}


def _chiama(oggetto, indice, *argomenti, tipi):
    if (indice, tipi) not in _PROTOTIPI:
        _PROTOTIPI[indice, tipi] = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *tipi)
    tabella = ctypes.cast(oggetto, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return _PROTOTIPI[indice, tipi](tabella[indice])(oggetto, *argomenti)


def rilascia(oggetto):
    if oggetto:
        _chiama(oggetto, 2, tipi=())


def _figlio(numero):
    v = VARIANT()
    v.vt = VT_I4
    v.u.lVal = numero
    return v


def _bstr(puntatore):
    if not puntatore:
        return None
    testo = ctypes.wstring_at(puntatore, oleaut32.SysStringLen(puntatore))
    oleaut32.SysFreeString(puntatore)
    return testo


def _testo(oggetto, indice, numero):
    uscita = ctypes.c_void_p()
    esito = _chiama(oggetto, indice, _figlio(numero), ctypes.byref(uscita), tipi=(VARIANT, ctypes.POINTER(ctypes.c_void_p)))
    return [esito, _bstr(uscita.value)]


def _variante(oggetto, indice, numero):
    uscita = VARIANT()
    esito = _chiama(oggetto, indice, _figlio(numero), ctypes.byref(uscita), tipi=(VARIANT, ctypes.POINTER(VARIANT)))
    if uscita.vt == VT_I4:
        valore = uscita.u.lVal & 0xFFFFFFFF
    elif uscita.vt == VT_BSTR:
        valore = ctypes.wstring_at(uscita.u.puntatore, oleaut32.SysStringLen(uscita.u.puntatore)) if uscita.u.puntatore else None
    else:
        valore = f"vt {uscita.vt}"
    oleaut32.VariantClear(ctypes.byref(uscita))
    return [esito, valore]


def nome(oggetto, numero): return _testo(oggetto, 10, numero)
def valore(oggetto, numero): return _testo(oggetto, 11, numero)
def descrizione(oggetto, numero): return _testo(oggetto, 12, numero)
def ruolo(oggetto, numero): return _variante(oggetto, 13, numero)
def stato(oggetto, numero): return _variante(oggetto, 14, numero)
def aiuto(oggetto, numero): return _testo(oggetto, 15, numero)
def scorciatoia(oggetto, numero): return _testo(oggetto, 17, numero)
def azione(oggetto, numero): return _testo(oggetto, 20, numero)


def quanti_figli(oggetto):
    uscita = ctypes.c_long()
    esito = _chiama(oggetto, 8, ctypes.byref(uscita), tipi=(ctypes.POINTER(ctypes.c_long),))
    return [esito, uscita.value]


def figlio_oggetto(oggetto, numero):
    uscita = ctypes.c_void_p()
    esito = _chiama(oggetto, 9, _figlio(numero), ctypes.byref(uscita), tipi=(VARIANT, ctypes.POINTER(ctypes.c_void_p)))
    rilascia(uscita.value)
    return [esito, bool(uscita.value)]


def posto(oggetto, numero):
    misure = [ctypes.c_long() for _ in range(4)]
    esito = _chiama(oggetto, 22, *(ctypes.byref(m) for m in misure), _figlio(numero), tipi=(ctypes.POINTER(ctypes.c_long),) * 4 + (VARIANT,))
    return [esito, [m.value for m in misure]]


def selezione(oggetto):
    uscita = VARIANT()
    esito = _chiama(oggetto, 19, ctypes.byref(uscita), tipi=(ctypes.POINTER(VARIANT),))
    valore = uscita.u.lVal if uscita.vt == VT_I4 else f"vt {uscita.vt}"
    oleaut32.VariantClear(ctypes.byref(uscita))
    return [esito, valore]


def tutto(oggetto, numero):
    """Tutto cio' che un client puo' leggere di una voce, o della plancia con 0."""
    letto = {"nome": nome(oggetto, numero), "ruolo": ruolo(oggetto, numero), "stato": stato(oggetto, numero), "valore": valore(oggetto, numero),
        "descrizione": descrizione(oggetto, numero), "aiuto": aiuto(oggetto, numero), "scorciatoia": scorciatoia(oggetto, numero),
        "azione": azione(oggetto, numero), "posto": posto(oggetto, numero)}
    if numero:
        letto["figlio"] = figlio_oggetto(oggetto, numero)
    else:
        letto["figli"] = quanti_figli(oggetto)
        letto["selezione"] = selezione(oggetto)
    return letto


def come_nvda(oggetto, numero):
    """Le tre letture di NVDA per un evento: nome, ruolo e stato."""
    return {"nome": nome(oggetto, numero), "ruolo": ruolo(oggetto, numero), "stato": stato(oggetto, numero)}


class Lettore:
    def __init__(self, desktop, finestra, processo):
        self.finestra, self.processo = finestra, processo
        maniglia = user32.OpenDesktopW(desktop, 0, False, 0x10000000)
        if not maniglia or not user32.SetThreadDesktop(maniglia):
            raise SystemExit(f"Il desktop {desktop} non si apre: errore {ctypes.get_last_error()}.")
        ole32.CoInitialize(None)
        uscita = ctypes.c_void_p()
        oleacc.CreateStdAccessibleObject(finestra, OBJID_CLIENT, ctypes.byref(IID_IACCESSIBLE), ctypes.byref(uscita))
        self.standard = uscita.value
        self.in_coda, self.letti, self.comandi = [], [], queue.Queue()
        self.richiamo = _RICHIAMO(self._evento)
        # Come NVDA: da fuori, e senza gli eventi del lettore stesso.
        self.aggancio = user32.SetWinEventHook(0x8005, 0x800C, None, self.richiamo, processo, 0, 0x0002)
        self.finito = False
        self.martellata = None

    def _evento(self, _aggancio, evento, finestra, oggetto, figlio, _filo, _tempo):
        # Come NVDA, l'evento si annota e si guarda dopo, fuori dal richiamo.
        if finestra == self.finestra and evento in EVENTI:
            self.in_coda.append((time.perf_counter(), EVENTI[evento], oggetto, figlio))

    def _guarda(self, arrivo, tipo, oggetto, figlio):
        accessibile, numero = ctypes.c_void_p(), VARIANT()
        inizio = time.perf_counter()
        esito = oleacc.AccessibleObjectFromEvent(self.finestra, oggetto & 0xFFFFFFFF, figlio & 0xFFFFFFFF, ctypes.byref(accessibile), ctypes.byref(numero))
        letto = {"evento": tipo, "oggetto": oggetto, "figlio": figlio, "esito": esito, "attesa_ms": round((inizio - arrivo) * 1000, 1)}
        if esito == 0 and accessibile.value:
            n = numero.u.lVal if numero.vt == VT_I4 else 0
            letto.update(come_nvda(accessibile.value, n))
            letto["microsecondi"] = round((time.perf_counter() - inizio) * 1e6)
            rilascia(accessibile.value)
            # La strada di oggi, senza l'oggetto della plancia: oleacc crea
            # l'oggetto standard qui, nel processo del lettore, e legge.
            inizio = time.perf_counter()
            uscita = ctypes.c_void_p()
            oleacc.CreateStdAccessibleObject(self.finestra, OBJID_CLIENT, ctypes.byref(IID_IACCESSIBLE), ctypes.byref(uscita))
            if uscita.value:
                letto["stato_standard"] = come_nvda(uscita.value, n)["stato"]
                rilascia(uscita.value)
            letto["microsecondi_standard"] = round((time.perf_counter() - inizio) * 1e6)
        self.letti.append(letto)

    def _dalla_finestra(self):
        accessibile = ctypes.c_void_p()
        esito = oleacc.AccessibleObjectFromWindow(self.finestra, OBJID_CLIENT & 0xFFFFFFFF, ctypes.byref(IID_IACCESSIBLE), ctypes.byref(accessibile))
        return esito, accessibile.value

    def _leggi(self, figli, giri, oggetti):
        inizio = time.perf_counter()
        esito, accessibile = self._dalla_finestra()
        apertura = round((time.perf_counter() - inizio) * 1e6)
        risposta = ctypes.c_size_t()
        user32.SendMessageTimeoutW(self.finestra, WM_GETOBJECT, 0, OBJID_CLIENT & 0xFFFFFFFF, 0x0002, 5000, ctypes.byref(risposta))
        uscita = {"esito": esito, "apertura_us": apertura, "wm_getobject": risposta.value, "voci": {}, "tempi_us": {}, "totale_us": {}}
        if esito != 0 or not accessibile:
            return uscita
        for chiave, oggetto in (("plancia", accessibile), ("standard", self.standard)):
            if chiave not in oggetti:
                continue
            inizio = time.perf_counter()
            for _ in range(giri):
                letture = {n: tutto(oggetto, n) for n in [0, *figli]}
            totale = (time.perf_counter() - inizio) * 1e6
            uscita["totale_us"][chiave] = round(totale)
            uscita["tempi_us"][chiave] = round(totale / (giri * (len(figli) + 1)))
            uscita["voci"][chiave] = letture
        rilascia(accessibile)
        return uscita

    def _martella(self):
        """Un giro di letture mentre MeTeOra si chiude: dall'oggetto tenuto
        dall'inizio, come NVDA che tiene il fuoco, e ogni dieci giri da uno
        nuovo, come per un evento nuovo."""
        m = self.martellata
        m["giri"] += 1
        if m["giri"] % 10 == 0:
            esito, nuovo = self._dalla_finestra()
            if esito == 0 and nuovo:
                m["nuovi"] += 1
                stato(nuovo, 0)
                rilascia(nuovo)
            else:
                m["nuovi_rifiutati"] += 1
        for n in m["figli"]:
            letto = come_nvda(m["oggetto"], n) if m["oggetto"] else {"stato": [-1, None]}
            if letto["stato"][0] == 0:
                m["riuscite"] += 1
                m["di_fila"] = 0
            else:
                m["fallite"] += 1
                m["di_fila"] += 1
        if m["di_fila"] >= 200:
            self._fine_della_martellata()

    def _fine_della_martellata(self):
        m, self.martellata = self.martellata, None
        oggetto, m["oggetto"] = m.pop("oggetto"), None
        rilascia(oggetto)
        with open(m.pop("file"), "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False)

    def _esegui(self, comando):
        if comando["comando"] == "leggi":
            return self._leggi(comando.get("figli", []), comando.get("giri", 1), comando.get("oggetti", ("plancia", "standard")))
        if comando["comando"] == "eventi":
            letti, self.letti = self.letti, []
            return {"eventi": letti, "in_coda": len(self.in_coda)}
        if comando["comando"] == "martella":
            esito, oggetto = self._dalla_finestra()
            self.martellata = {"figli": comando["figli"], "file": comando["file"], "oggetto": oggetto if esito == 0 else None, "giri": 0,
                "riuscite": 0, "fallite": 0, "di_fila": 0, "nuovi": 0, "nuovi_rifiutati": 0}
            return {"martella": esito == 0}
        self.finito = True
        return {"esci": True}

    def ciclo(self):
        messaggio = wintypes.MSG()
        while not self.finito:
            user32.MsgWaitForMultipleObjects(0, None, False, 0 if self.martellata else 10, 0x04FF)
            while user32.PeekMessageW(ctypes.byref(messaggio), None, 0, 0, 1):
                user32.TranslateMessage(ctypes.byref(messaggio))
                user32.DispatchMessageW(ctypes.byref(messaggio))
            while self.in_coda:
                self._guarda(*self.in_coda.pop(0))
            if self.martellata:
                self._martella()
            with contextlib.suppress(queue.Empty):
                comando = self.comandi.get_nowait()
                try:
                    risposta = self._esegui(comando)
                except Exception as e:  # noqa: BLE001 - l'errore torna al banco come risposta
                    risposta = {"errore": repr(e)}
                # Il banco puo' essere gia' uscito, durante una martellata.
                with contextlib.suppress(OSError, ValueError):
                    print(json.dumps(risposta, ensure_ascii=False), flush=True)
        if self.martellata:
            self._fine_della_martellata()
        user32.UnhookWinEvent(self.aggancio)
        rilascia(self.standard)


def _ascolta(lettore):
    for riga in sys.stdin:
        if riga.strip():
            lettore.comandi.put(json.loads(riga))
    lettore.comandi.put({"comando": "esci"})


def main():
    desktop, finestra, processo = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    lettore = Lettore(desktop, finestra, processo)
    threading.Thread(target=_ascolta, args=(lettore,), name="lettore, comandi", daemon=True).start()
    print(json.dumps({"pronto": True}), flush=True)
    lettore.ciclo()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
