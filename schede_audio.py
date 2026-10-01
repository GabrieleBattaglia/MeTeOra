# MeTeOra, le schede audio: su quale uscita suonano musica ed effetti.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 01/10/2026: nasce con la 1.51.0, tappa 3, piano 5.8.9: la scheda audio in uso fra le impostazioni.

"""La scheda audio, una voce sola per la musica e per gli effetti.

Gli effetti suonano con il mixer condiviso di GBUtils, che apre la scheda
con PortAudio; la musica suona con mpv, aperto con ao=wasapi. I due non si
conoscono: la scelta si fa sull'elenco di GBUtils, e mpv ritrova la stessa
scheda per nome nel suo.
Della scelta si salvano il nome del dispositivo e il nome intero della sua
interfaccia, per esempio "Windows WASAPI", mai l'indice: gli indici di
PortAudio cambiano fra un avvio e l'altro, e lo stesso nome compare in piu'
interfacce. Una scelta vuota vuol dire automatica: la stessa regola di
scegli_dispositivo_audio di GBUtils per gli effetti, e "auto" di mpv, che
segue la scheda predefinita di Windows, per la musica.
Nell'elenco WDM-KS non c'e': non si apre mai a scrittura, che e' il modo
del mixer degli effetti. ASIO c'e', ma prende la scheda in esclusiva e puo'
zittire NVDA, e la sua etichetta lo dice.
Un fatto verificato da ricordare: se si legge l'elenco delle uscite di mpv
prima che sounddevice sia importato per la prima volta, PortAudio perde le
uscite ASIO. Per questo l'elenco di GBUtils si chiede sempre prima di
quello di mpv.
Funzioni senza finestre e senza suono: chi le usa scrive in console.
"""

import re

# Le interfacce che l'elenco lascia fuori: WDM-KS non si apre mai a
# scrittura, e il mixer degli effetti scrive.
ESCLUSE = ("WDM-KS",)
# MeTeOra apre mpv con ao=wasapi: delle uscite di mpv contano solo queste.
PREFISSO_MPV = "wasapi/"
# L'uscita di mpv che segue la scheda predefinita di Windows.
AUTOMATICA_MPV = "auto"
# MME taglia i nomi dei dispositivi a 31 caratteri: solo un nome lungo
# esattamente cosi' puo' essere l'inizio di un nome di mpv.
LUNGHEZZA_DEI_NOMI_MME = 31

_A_CAPO = re.compile(r"[\r\n]+")


def _ripulito(nome):
    """Il nome su una riga sola: qualche driver ci mette un a capo, che
    romperebbe la riga di una lista o della console."""
    return _A_CAPO.sub(" ", nome or "").strip()


def _tutte():
    """Tutte le uscite di GBUtils, WDM-KS compreso, nell'ordine di GBUtils,
    senza aprire niente."""
    from GBUtils import elenco_dispositivi_audio

    return [{"indice": v["indice"], "dispositivo": _ripulito(v["dispositivo"]), "interfaccia": v["interfaccia"], "breve": v["breve"],
             "latenza": v["latenza"], "esclusiva": v["esclusiva"]} for v in elenco_dispositivi_audio(prova="nessuno")]


def uscite():
    """Le uscite fra cui scegliere, senza aprire niente: una lista di
    dizionari con indice, dispositivo, interfaccia (il nome intero, per
    esempio "Windows WASAPI"), breve ("WASAPI"), latenza in millesimi di
    secondo ed esclusiva.
    In ordine di latenza crescente; dentro la stessa latenza resta l'ordine
    di GBUtils: prima la scheda che Windows usa gia', poi per preferenza
    d'interfaccia e per indice."""
    # sorted e' stabile: basta la latenza, il resto lo porta l'ordine di
    # partenza.
    return sorted((u for u in _tutte() if u["breve"] not in ESCLUSE), key=lambda u: (u["latenza"] is None, u["latenza"] or 0.0))


def _millisecondi(latenza):
    """3 ms, 23,2 ms: il decimale solo se serve, con la virgola."""
    decimi = round(latenza, 1)
    numero = f"{decimi:.0f}" if decimi == int(decimi) else f"{decimi:.1f}".replace(".", ",")
    return f"{numero} ms"


def etichetta(uscita):
    """La riga che si legge nella lista: "Altoparlanti (Realtek(R) Audio),
    WASAPI, 3 ms"; per le interfacce esclusive, come ASIO, in coda
    l'avviso che possono zittire NVDA."""
    parti = [uscita["dispositivo"], uscita.get("breve") or (uscita.get("interfaccia") or "").replace("Windows ", "")]
    if uscita.get("latenza") is not None:
        parti.append(_millisecondi(uscita["latenza"]))
    testo = ", ".join(parti)
    return f"{testo}, esclusiva: può zittire NVDA" if uscita.get("esclusiva") else testo


def da_salvare(uscita):
    """La scelta da scrivere nelle impostazioni: dispositivo e interfaccia
    dell'uscita, o il dizionario vuoto per l'automatica (uscita None)."""
    return {"dispositivo": uscita["dispositivo"], "interfaccia": uscita["interfaccia"]} if uscita else {}


def ritrova(scelta, elenco):
    """L'uscita dell'elenco con lo stesso dispositivo e la stessa
    interfaccia della scelta salvata, o None: la scheda non c'e' piu', o la
    scelta e' vuota."""
    if not scelta:
        return None
    dispositivo, interfaccia = _ripulito(scelta.get("dispositivo")), scelta.get("interfaccia")
    for uscita in elenco:
        if uscita["dispositivo"] == dispositivo and uscita["interfaccia"] == interfaccia:
            return uscita
    return None


def automatica():
    """La scelta automatica, la stessa che il mixer degli effetti fa da se'
    alla prima apertura: fra le interfacce che portano alla scheda
    predefinita di Windows, la piu' pronta che si lascia davvero aprire.
    Restituisce l'uscita, un dizionario come quelli di uscite(), o None se
    non c'e' niente da scegliere.
    Rifa' la scelta da capo e prova davvero ad aprire i dispositivi, da 3 a
    16 millesimi l'uno: serve quando si torna all'automatica o quando la
    scheda salvata non c'e' piu', non all'avvio. Nelle prove si sostituisce
    scegli_dispositivo_audio."""
    from GBUtils import scegli_dispositivo_audio

    indice, interfaccia = scegli_dispositivo_audio(riprova=True)
    if indice is None:
        return None
    for uscita in _tutte():
        if uscita["indice"] == indice:
            return uscita
    # Un indice che l'elenco non ha non dovrebbe capitare: la scelta resta
    # buona per il mixer, e del nome si sa solo l'interfaccia.
    return {"indice": indice, "dispositivo": f"dispositivo {indice}", "interfaccia": interfaccia, "breve": (interfaccia or "").replace("Windows ", ""),
            "latenza": None, "esclusiva": False}


def in_uso(elenco=None):
    """L'uscita su cui il mixer degli effetti suona adesso, da
    Acusticator.stato(), senza aprire niente: un dizionario come quelli di
    uscite(), o None se il mixer non ha ancora scelto (sceglie alla prima
    apertura) o se il suo indice non e' nell'elenco. Senza elenco lo chiede
    a GBUtils, WDM-KS compreso."""
    from GBUtils import Acusticator

    indice = Acusticator.stato()["device"]
    if indice is None:
        return None
    for uscita in _tutte() if elenco is None else elenco:
        if uscita["indice"] == indice:
            return uscita
    return None


def dispositivo_di_mpv(nome, elenco_mpv):
    """Il nome mpv ("wasapi/{...}") della scheda che GBUtils chiama nome,
    cercato nell'elenco di mpv [{"name", "description"}]: la voce la cui
    description e' uguale al nome o, se nessuna e il nome e' lungo
    esattamente 31 caratteri, l'unica che comincia con il nome, perche'
    MME taglia i nomi a 31 caratteri. Un nome piu' corto e' intero: che
    sia l'inizio di un altro nome, come Altoparlanti per Altoparlanti
    (Realtek(R) Audio), non vuol dire niente. None se non ce n'e' nessuna o
    se sono piu' d'una: meglio la scheda di Windows che una tirata a
    indovinare. Le voci che non cominciano con "wasapi/" non contano:
    MeTeOra apre mpv con ao=wasapi."""
    nome = _ripulito(nome)
    if not nome:
        return None
    wasapi = [(voce["name"], _ripulito(voce.get("description"))) for voce in elenco_mpv or [] if str(voce.get("name", "")).startswith(PREFISSO_MPV)]
    candidate = [[n for n, d in wasapi if d == nome]]
    if len(nome) == LUNGHEZZA_DEI_NOMI_MME:
        candidate.append([n for n, d in wasapi if d.startswith(nome)])
    for trovate in candidate:
        if trovate:
            return trovate[0] if len(trovate) == 1 else None
    return None


def applica(scelta, motore, avvio=False):
    """Applica la scelta salvata, {"dispositivo", "interfaccia"}, o vuota
    per l'automatica: gli effetti con Acusticator.setup(device=indice), la
    musica scrivendo in motore.dispositivo il nome mpv della stessa scheda,
    o "auto" se mpv non la ritrova. Con l'automatica gli effetti vanno
    sull'uscita di automatica() e la musica su "auto". Se la scheda salvata
    non c'e' piu' si usa l'automatica.
    Con avvio vero e la scelta vuota non si tocca niente, e niente si apre
    per prova: il mixer sceglie da se' alla prima apertura con la stessa
    regola, e mpv parte gia' su "auto".
    Se l'automatica non trova niente, il mixer resta sull'uscita di prima:
    GBUtils non ha un modo pubblico per tornare a nessuna scelta.
    Non scrive in console: restituisce un esito, un dizionario con
      uscita       l'uscita degli effetti, come quelle di uscite(), o None
                   se non si sa (avvio con l'automatica, o niente da
                   scegliere);
      dispositivo  e interfaccia: i suoi nomi, o None;
      automatica   vero se gli effetti vanno sulla scelta automatica;
      mancante     vero se la scelta salvata non c'era piu';
      musica       vero se la musica suona sulla stessa scheda: con
                   l'automatica sempre, perche' "auto" segue Windows come
                   la scelta automatica; falso se mpv non l'ha ritrovata
                   (ASIO, nomi diversi) ed e' rimasta sulla scheda di Windows;
      mpv          il nome scritto in motore.dispositivo."""
    if not scelta and avvio:
        return {"uscita": None, "dispositivo": None, "interfaccia": None, "automatica": True, "mancante": False, "musica": True, "mpv": AUTOMATICA_MPV}
    from GBUtils import Acusticator

    # L'elenco di GBUtils va chiesto prima di quello di mpv: al contrario
    # PortAudio perderebbe le uscite ASIO.
    uscita = ritrova(scelta, uscite()) if scelta else None
    mancante = bool(scelta) and uscita is None
    automatico = uscita is None
    nome_mpv = None
    if automatico:
        uscita = automatica()
    else:
        nome_mpv = dispositivo_di_mpv(uscita["dispositivo"], motore.dispositivi())
    if uscita is not None:
        # int(): GBUtils riconosce l'indice solo come intero di Python.
        Acusticator.setup(device=int(uscita["indice"]))
    nome_mpv = nome_mpv or AUTOMATICA_MPV
    motore.dispositivo = nome_mpv
    return {"uscita": uscita, "dispositivo": uscita["dispositivo"] if uscita else None, "interfaccia": uscita["interfaccia"] if uscita else None,
            "automatica": automatico, "mancante": mancante, "musica": automatico or nome_mpv != AUTOMATICA_MPV, "mpv": nome_mpv}
