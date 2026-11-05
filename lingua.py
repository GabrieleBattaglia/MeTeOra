# MeTeOra, la lingua: i testi per l'utente passano da qui, per tradurli con gettext.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 05/11/2026: nasce con la 3.0.0, la localizzazione.

"""La lingua di MeTeOra.

Ogni testo per l'utente passa da _ e, quando dipende da un numero, da
ngettext: l'italiano e' la lingua sorgente, e un catalogo in
locales/<lingua>/LC_MESSAGES/messages.mo lo traduce. I segnaposto sono fra
graffe, con un nome, e si riempiono con format dopo la traduzione: il
traduttore puo' spostarli nella frase, ma non cambiarne il nome.

La lingua la sceglie polipo di GBUtils, all'importazione di questo modulo,
prima che gli altri costruiscano le loro tabelle di testi: quella della voce
Lingua delle impostazioni, che polipo salva in selected_language.json accanto
ai dati; al primo avvio quella di Windows, se qualcuno l'ha tradotta;
altrimenti l'italiano. Una lingua scelta vale dal riavvio.
"""

import ctypes
import os

import percorsi

SORGENTE = "it"
DOMINIO = "messages"
CARTELLA = "locales"
# Il nome della lingua nella lingua stessa, per GetLocaleInfoEx: italiano, English.
LOCALE_SNATIVELANGUAGENAME = 0x04


def cartella_dei_cataloghi():
    return percorsi.percorso_risorsa(CARTELLA)


def _polipo(lingua=None):
    if not os.path.isdir(cartella_dei_cataloghi()):
        # Senza cataloghi, come nel pacchetto che non ne porta, c'e' solo
        # l'italiano: polipo lo direbbe con un avviso a schermo.
        return SORGENTE, lambda testo: testo, lambda singolare, plurale_, n: singolare if n == 1 else plurale_
    from GBUtils import polipo

    return polipo(domain=DOMINIO, localedir=cartella_dei_cataloghi(), source_language=SORGENTE, config_path=percorsi.cartella_programma(),
        interattivo=False, lingua=lingua, plurali=True)


CODICE, _gettext, _ngettext = _polipo()
# La lingua scelta nelle impostazioni durante questa sessione, che vale dal riavvio.
prossima = None


def _(testo):
    """Il testo nella lingua di MeTeOra."""
    return _gettext(testo)


def ngettext(singolare, plurale, n):
    """Il testo con il numero n, nella forma giusta della lingua: in italiano
    il singolare per 1 e il plurale per gli altri, ma il polacco, per
    esempio, ne ha tre."""
    return _ngettext(singolare, plurale, n)


def plurale(n, singolare, plurale_):
    """Il caso piu' comune di ngettext, il numero con la sua parola:
    plurale(3, "{n} brano", "{n} brani") fa "3 brani"."""
    return _ngettext(singolare, plurale_, n).format(n=n)


def lingue():
    """I codici delle lingue che MeTeOra sa parlare: l'italiano e quelle che
    hanno il catalogo compilato, in ordine."""
    cartella = cartella_dei_cataloghi()
    try:
        nomi = os.listdir(cartella)
    except OSError:
        nomi = []
    return sorted({SORGENTE} | {n for n in nomi if os.path.isfile(os.path.join(cartella, n, "LC_MESSAGES", f"{DOMINIO}.mo"))})


def nome(codice):
    """Il nome della lingua nella lingua stessa, come lo dice Windows:
    italiano, English, polski. Senza risposta, il codice."""
    testo = ctypes.create_unicode_buffer(85)
    try:
        if ctypes.WinDLL("kernel32").GetLocaleInfoEx(codice, LOCALE_SNATIVELANGUAGENAME, testo, len(testo)):
            return testo.value
    except (OSError, AttributeError):
        pass
    return codice


def scegli(codice):
    """La voce Lingua delle impostazioni: polipo salva la scelta, che vale dal
    riavvio."""
    global prossima
    _polipo(codice)
    prossima = None if codice == CODICE else codice
