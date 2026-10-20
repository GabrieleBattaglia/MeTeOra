# MeTeOra, l'importazione delle playlist di altri programmi: M3U, M3U8 e PLS.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 20/10/2026: nasce con la 1.113.0, tappa 14 g del piano.

"""L'importazione delle playlist di altri programmi, la parte senza wx.

leggi apre un file M3U, M3U8 o PLS e lo passa ad analizza, che ne fa un
elenco di Voce: per ognuna il testo com'e' scritto, il percorso assoluto e,
se si salta, il motivo. Quali file mancano lo dice poi pulizia.controlla,
che la finestra chiama in un filo a parte, ed esito mette insieme le due
cose. Le regole, decise con Gabriele il 20 ottobre 2026:
- Le estensioni sono quelle di formati.PLAYLIST. Un M3U8 e' sempre in
  UTF-8; un M3U o un PLS in UTF-8 se il testo lo e', con o senza BOM,
  altrimenti nella codifica di Windows, cp1252. Una BOM UTF-16 vale per
  tutti e tre.
- Di un M3U si leggono le righe che non sono vuote e non cominciano con il
  cancelletto: #EXTM3U, #EXTINF e le altre si ignorano, perche' titoli e
  durate li da' lo schedario. Di un PLS si leggono File1, File2 e i
  seguenti, nell'ordine del numero e non delle righe; titoli, durate e
  NumberOfEntries si ignorano.
- Un percorso relativo vale dalla cartella della playlist, uno con la barra
  iniziale dalla sua unita'. Un file:/// diventa un percorso, con le lettere
  decodificate in UTF-8, e un file://server/condivisione un percorso di
  rete; file://C:/ con due barre sole vale come file:///C:/, e il
  cancelletto resta nel nome. Le barre diventano quelle di Windows. Tutto
  si salva in forma assoluta, l'unica che la pulizia controlla.
- Si saltano, con il motivo, gli indirizzi in rete (http, https e ogni altro
  schema), le cartelle, le playlist dentro la playlist, che non si aprono, i
  file di un formato che MeTeOra non suona e i percorsi con caratteri che
  Windows non vuole. Cartella o formato si decidono dal nome, e sui dischi
  del computer leggi li corregge guardando il disco. I doppioni restano,
  nell'ordine del file, come con Aggiungi alla playlist.
- In rete il file della playlist si legge in un filo sorvegliato, come
  nella pulizia: se tace oltre ricerca.ATTESA_IN_RETE la lettura si annulla,
  e la coda delle importazioni va avanti.
- Un M3U con le righe di libgme, quelle con i due punti doppi, e' la lista
  dei brani di un file delle console: non si importa, perche' chip.py la
  legge gia' da sola accanto al suo file.
- Le voci che mancano si trattano come nella pulizia all'avvio: si tolgono
  quelle di un'unita' o di una condivisione che risponde, e si tengono,
  senza controllo, quelle di una radice che non risponde.
"""

import ntpath
import os
import re
import threading
import time
from collections import Counter
from urllib.parse import unquote, urlsplit

import formati
import pulizia
import questa_rete
import ricerca

# Uno schema come http: o file:, di almeno due lettere: C: e' un'unita'.
_SCHEMA = re.compile(r"([A-Za-z][A-Za-z0-9+.\-]+):")
# La riga di libgme: il file, i due punti doppi e il tipo, come
# gioco.nsf::NSF,1,Titolo; il file si puo' anche omettere.
_RIGA_DI_LIBGME = re.compile(r"([^:]*)::\s*([A-Za-z0-9]+)\s*(,|$)")
# Un'estensione vera: un punto e poche lettere o cifre. Con lo spazio, come
# in Vol. 2, e' il nome di una cartella.
_ESTENSIONE = re.compile(r"\.[A-Za-z0-9]{1,10}")
# I caratteri che Windows non vuole in un percorso, dopo l'unita'.
_NON_VALIDI = frozenset('<>"|?*') | frozenset(chr(c) for c in range(32))
# La voce PLS di un file: File1, File2... senza badare alle maiuscole.
_VOCE_PLS = re.compile(r"file(\d+)", re.IGNORECASE)
# Una lettera d'unita' dove un indirizzo file: ha il server: file://C:/a.mp3.
_UNITA_AL_POSTO_DEL_SERVER = re.compile(r"[A-Za-z][:|]")
# Sotto quanti secondi la data del file non conta, se la dimensione e' la
# stessa: su FAT e su alcune condivisioni l'ora si scrive a passi di due secondi.
TOLLERANZA_DELLA_DATA = 2.0
# A blocchi di quanti byte si legge il file della playlist: ogni blocco e'
# un passo per chi sorveglia la lettura in rete.
BLOCCO_DI_LETTURA = 65536

# I motivi per cui una voce si salta, con le parole al singolare e al plurale,
# nell'ordine in cui la console li dice a parita' di numero.
MOTIVI = {
    "mancante": ("file che non c'è", "file che non ci sono"),
    "indirizzo": ("indirizzo in rete", "indirizzi in rete"),
    "formato": ("file di un formato che MeTeOra non suona", "file di formati che MeTeOra non suona"),
    "cartella": ("cartella", "cartelle"),
    "playlist": ("playlist dentro la playlist", "playlist dentro la playlist"),
    "non_valido": ("percorso non valido", "percorsi non validi"),
}


class Voce:
    """Una voce della playlist: come e' scritta, il percorso assoluto a cui
    porta, o None per un indirizzo in rete, e il motivo per cui si salta,
    una chiave di MOTIVI, o None se e' un file da suonare."""

    __slots__ = ("motivo", "percorso", "scritta")

    def __init__(self, scritta, percorso, motivo):
        self.scritta = scritta
        self.percorso = percorso
        self.motivo = motivo

    @property
    def leggibile(self):
        """Come la console la nomina: il percorso a cui porta, se c'e'."""
        return self.percorso or self.scritta


def decodifica(byte, estensione):
    """Il testo della playlist: UTF-16 con la sua BOM, UTF-8 con la sua o
    per un M3U8, altrimenti UTF-8 se lo e' e cp1252 se non lo e'."""
    if byte.startswith((b"\xff\xfe", b"\xfe\xff")):
        return byte.decode("utf-16", errors="replace")
    if byte.startswith(b"\xef\xbb\xbf"):
        return byte[3:].decode("utf-8", errors="replace")
    if estensione == ".m3u8":
        return byte.decode("utf-8", errors="replace")
    try:
        return byte.decode("utf-8")
    except UnicodeDecodeError:
        return byte.decode("cp1252", errors="replace")


def righe_m3u(testo):
    """Le voci di un M3U: le righe non vuote che non cominciano con il cancelletto."""
    return [riga.strip() for riga in testo.splitlines() if riga.strip() and not riga.strip().startswith("#")]


def righe_pls(testo):
    """Le voci di un PLS: File1, File2 e seguenti, nell'ordine del numero;
    di un numero ripetuto vale la prima."""
    voci = {}
    for riga in testo.splitlines():
        chiave, uguale, valore = riga.strip().partition("=")
        numero = _VOCE_PLS.fullmatch(chiave.strip())
        if uguale and numero and valore.strip():
            voci.setdefault(int(numero.group(1)), valore.strip())
    return [voci[n] for n in sorted(voci)]


def lista_di_libgme(righe, percorso):
    """Il nome del file delle console di cui la playlist e' la lista dei
    brani, come gioco.nsf per gioco.m3u, se le sue righe sono quelle di
    libgme; altrimenti None. Gli indirizzi, come http://[::1]/, hanno anche
    loro i due punti doppi, e non contano."""
    for riga in righe:
        if "://" in riga:
            continue
        trovata = _RIGA_DI_LIBGME.match(riga)
        if trovata:
            nome = ntpath.basename(trovata.group(1).strip().replace("/", "\\"))
            return nome or f"{ntpath.splitext(ntpath.basename(percorso))[0]}.{trovata.group(2).lower()}"
    return None


def _da_indirizzo_file(testo):
    r"""Il percorso di un indirizzo file:, con le lettere decodificate in
    UTF-8: file:///C:/Musica/a.mp3 e' C:/Musica/a.mp3, file://server/x/a.mp3
    e' //server/x/a.mp3; vale anche C| dei programmi vecchi. Con due barre
    sole, come file://C:/Musica/a.mp3, la lettera non e' un server. Un
    cancelletto non codificato, come in Best #1.mp3, e' parte del nome: un
    file non ha frammenti."""
    parti = urlsplit(testo, allow_fragments=False)
    percorso = unquote(parti.path, encoding="utf-8", errors="replace")
    server = unquote(parti.netloc, encoding="utf-8", errors="replace")
    if _UNITA_AL_POSTO_DEL_SERVER.fullmatch(server):
        return f"{server[0]}:{percorso}"
    if server and server.lower() != "localhost":
        return "//" + server + percorso
    if re.match(r"/[A-Za-z][:|]", percorso):
        percorso = f"{percorso[1]}:{percorso[3:]}"
    return percorso


def risolvi(scritta, cartella):
    """La Voce di una riga della playlist, che sta in cartella."""
    testo = scritta.strip()
    if len(testo) >= 2 and testo[0] == testo[-1] == '"':
        testo = testo[1:-1].strip()
    schema = _SCHEMA.match(testo)
    if schema:
        if schema.group(1).lower() != "file":
            return Voce(scritta, None, "indirizzo")
        testo = _da_indirizzo_file(testo)
    testo = testo.replace("/", "\\")
    unita, resto = ntpath.splitdrive(testo)
    if not (unita or resto.strip("\\")) or any(c in _NON_VALIDI for c in resto):
        return Voce(scritta, None, "non_valido")
    if unita and resto.startswith("\\"):
        assoluto = testo
    elif unita:
        # C:brano.mp3 non dice da quale cartella di C: parte: dalla radice.
        assoluto = f"{unita}\\{resto}"
    elif resto.startswith("\\"):
        assoluto = ntpath.splitdrive(cartella)[0] + resto
    else:
        assoluto = ntpath.join(cartella, resto)
    finisce_con_la_barra = assoluto.endswith("\\")
    assoluto = ntpath.normpath(assoluto)
    estensione = ntpath.splitext(assoluto)[1]
    if finisce_con_la_barra or not _ESTENSIONE.fullmatch(estensione):
        return Voce(scritta, assoluto, "cartella")
    if estensione.lower() in formati.PLAYLIST:
        return Voce(scritta, assoluto, "playlist")
    if not formati.supportato(assoluto):
        return Voce(scritta, assoluto, "formato")
    return Voce(scritta, assoluto, None)


def analizza(byte, percorso):
    """(voci, libgme) del contenuto di una playlist che sta in percorso:
    le Voce nell'ordine del file, e il nome del file delle console se e' una
    lista di libgme, che non si importa; allora le voci sono vuote."""
    estensione = formati.estensione(percorso)
    testo = decodifica(byte, estensione)
    if estensione == ".pls":
        righe = righe_pls(testo)
    else:
        righe = righe_m3u(testo)
        libgme = lista_di_libgme(righe, percorso)
        if libgme:
            return [], libgme
    cartella = ntpath.dirname(percorso)
    return [risolvi(riga, cartella) for riga in righe], None


def rivedi_i_motivi(voci, in_rete=None):
    r"""Le voci saltate come cartella o come formato, decise dal nome,
    corrette guardando il disco: E:\Musica\Live.1986 puo' essere una
    cartella, e E:\Musica\LEGGIMI un file senza estensione. Solo sui dischi
    del computer: in rete ogni domanda puo' restare appesa, e il motivo
    resta quello del nome. Un percorso che non c'e' resta com'e'. in_rete,
    per le prove, dice quali percorsi sono in rete."""
    in_rete = in_rete or ricerca.in_rete
    for voce in voci:
        if voce.motivo not in ("cartella", "formato") or in_rete(voce.percorso):
            continue
        if os.path.isdir(voce.percorso):
            voce.motivo = "cartella"
        elif os.path.isfile(voce.percorso):
            voce.motivo = "formato"


def _leggi_il_file(percorso, al_passo=None):
    """(stato, byte) del file, letto a blocchi: al_passo, se c'e', si chiama
    dopo ognuno, per chi sorveglia la lettura."""
    stato = os.stat(percorso)
    blocchi = []
    with open(percorso, "rb") as f:
        while blocco := f.read(BLOCCO_DI_LETTURA):
            blocchi.append(blocco)
            if al_passo is not None:
                al_passo()
    return stato, b"".join(blocchi)


def _leggi_sorvegliato(percorso, attesa):
    """_leggi_il_file in un filo a parte, sorvegliato come
    pulizia._giro_sorvegliato: se per attesa secondi non arriva nemmeno un
    blocco, la lettura si annulla, in un altro filo perche' anche
    l'annullamento puo' restare fermo, e si solleva ricerca.NonRisponde.
    Con il Samba dell'Iliadbox una lettura puo' restare appesa per venti
    minuti, e con lei tutta la coda delle importazioni."""
    esito = []
    passo = [time.monotonic()]

    def al_passo():
        passo[0] = time.monotonic()

    def leggi_qui():
        try:
            esito.append(_leggi_il_file(percorso, al_passo))
        except Exception as errore:  # noqa: BLE001 - torna a chi aspetta, che lo solleva
            esito.append(errore)

    filo = threading.Thread(target=leggi_qui, name="MeTeOra, lettura della playlist", daemon=True)
    filo.start()
    while filo.is_alive() and time.monotonic() - passo[0] < attesa:
        filo.join(0.1)
    if filo.is_alive():
        threading.Thread(target=ricerca.annulla_la_lettura, args=(filo,), name="MeTeOra, annullamento in rete", daemon=True).start()
        raise ricerca.NonRisponde(ntpath.dirname(percorso))
    if not esito:
        raise OSError(f"La lettura di {percorso} si e' interrotta.")
    if isinstance(esito[0], Exception):
        raise esito[0]
    return esito[0]


def leggi(percorso, attesa=ricerca.ATTESA_IN_RETE):
    """La playlist sul disco: un dizionario con voci e libgme, come da
    analizza, e origine, cioe' percorso, data e dimensione del file, con cui
    riconoscerlo poi; oppure {"errore": motivo} se il file non si legge. In
    rete si prova prima se la cartella risponde, come per i dettagli di F11,
    e poi si legge con _leggi_sorvegliato, che dopo attesa secondi muti
    lascia perdere. Le voci saltate come cartella o formato si correggono
    con rivedi_i_motivi."""
    cartella = ntpath.dirname(percorso)
    try:
        if ricerca.in_rete(percorso):
            if not questa_rete.raggiungibile(cartella, attesa=questa_rete.ATTESA_IN_SOTTOFONDO):
                return {"errore": f"{cartella} non risponde."}
            stato, byte = _leggi_sorvegliato(percorso, attesa)
        else:
            stato, byte = _leggi_il_file(percorso)
    except ricerca.NonRisponde:
        return {"errore": f"{cartella} non risponde."}
    except OSError as e:
        return {"errore": f"{(e.strerror or str(e)).rstrip('. ')}."}
    voci, libgme = analizza(byte, percorso)
    rivedi_i_motivi(voci)
    return {"voci": voci, "libgme": libgme, "origine": {"percorso": percorso, "data": stato.st_mtime, "dimensione": stato.st_size}}


def cambiata(vecchia, nuova):
    """Vero se il file della playlist e' cambiato dall'importazione: un'altra
    dimensione, o una data diversa oltre TOLLERANZA_DELLA_DATA."""
    try:
        return vecchia["dimensione"] != nuova["dimensione"] or abs(vecchia["data"] - nuova["data"]) >= TOLLERANZA_DELLA_DATA
    except (KeyError, TypeError):
        return True


def esito(voci, mancanti=frozenset(), saltate=None):
    """Le voci messe insieme all'esito di pulizia.controlla: (percorsi da
    importare, voci saltate, tenute). Le saltate sono le Voce con un motivo,
    piu' quelle dei file che mancano, con il motivo mancante, nell'ordine del
    file; tenute dice, per ogni radice che non ha risposto, quante voci sono
    restate senza controllo, doppioni compresi."""
    radici = {os.path.normcase(radice): radice for radice in saltate or {}}
    percorsi, scartate, tenute = [], [], Counter()
    for voce in voci:
        if voce.motivo is None and pulizia.norm(voce.percorso) in mancanti:
            voce = Voce(voce.scritta, voce.percorso, "mancante")
        if voce.motivo is not None:
            scartate.append(voce)
            continue
        percorsi.append(voce.percorso)
        radice = radici.get(os.path.normcase(ntpath.splitdrive(voce.percorso)[0]))
        if radice is not None:
            tenute[radice] += 1
    return percorsi, scartate, dict(tenute)


def conta_i_motivi(scartate):
    """[(motivo, quante)] delle voci saltate, dal motivo piu' frequente; a
    parita', nell'ordine di MOTIVI."""
    conti = Counter(voce.motivo for voce in scartate)
    ordine = list(MOTIVI)
    return sorted(conti.items(), key=lambda coppia: (-coppia[1], ordine.index(coppia[0])))
