# MeTeOra, utilita': scarica i testi delle licenze che sul disco non ci sono: le librerie dentro libmpv, winrt, FluidR3 e PortAudio.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 04/10/2026: nasce con la 1.85.2, con il permesso di Gabriele per gli scaricamenti.

"""I testi delle licenze che raccogli_licenze.py non trova sul disco.

Sono di tre gruppi: le librerie chiuse dentro libmpv-2.dll, i pacchetti winrt
del riconoscimento dei caratteri, il cui wheel non porta la licenza, e il
banco di suoni FluidR3 GM, che MeTeOra scarica per i MIDI.

La build di shinchiro collega dentro libmpv-2.dll, in modo statico, FFmpeg e
decine di librerie, molte BSD o MIT, che chiedono di riportare la loro nota
di copyright con il programma compilato. Quali siano lo dicono gli script
della build, al commit fissato in prepara_ambiente.py (WINBUILD_COMMIT): la
cartella packages ha un file per libreria, con il repository e le
dipendenze. Questo script parte da mpv, segue le dipendenze, e di ogni
libreria scarica dal suo repository i file di licenza della radice
(LICENSE, COPYING, COPYRIGHT, NOTICE, PATENTS e simili), in
licenze/libmpv/<libreria>. Le dipendenze facoltative di FFmpeg, come x265,
contano solo se il loro nome compare nella DLL.

I testi vengono dal ramo principale di ogni progetto: molte librerie la build
le prende dal ramo principale del giorno, senza fissarne la versione, e il
testo di una licenza cambia di rado. winrt e FluidR3 finiscono in
licenze/winrt e licenze/fluidr3. L'elenco di tutto va in
strumenti/licenze_scaricate.json, che raccogli_licenze.py legge per LEGGIMI.txt
e SORGENTI.txt. Va rifatto quando cambia la build di libmpv, prima di
raccogli_licenze.py. Per l'API di GitHub usa, se c'e', il gettone di gh.
Uso: python strumenti/scarica_licenze.py
"""

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADICE, "strumenti"))

import prepara_ambiente  # noqa: E402

LICENZE = os.path.join(RADICE, "licenze")
ELENCO = os.path.join(RADICE, "strumenti", "licenze_scaricate.json")
DLL = os.path.join(RADICE, "lib", "libmpv-2.dll")
WINBUILD = "shinchiro/mpv-winbuild-cmake"
# I nomi dei file di licenza, nella radice di un repository.
NOMI = re.compile(r"^(licen[cs]e|copying|copyright|notice|patents|unlicense)([.\-_].*)?$", re.IGNORECASE)
# Gli stessi nomi, ma file di configurazione o di codice: si scartano.
SCARTATI = re.compile(r"\.(cfg|py|json|ya?ml|toml|in|sh|cmake|c|h)$", re.IGNORECASE)
# Le dipendenze di FFmpeg scritte come variabili negli script: il nome della
# libreria, che conta solo se compare dentro la DLL.
VARIABILI = {"${ffmpeg_x265}": "x265", "${ffmpeg_davs2}": "davs2", "${ffmpeg_uavs3d}": "uavs3d"}
# Le librerie che arrivano come archivio e non da un repository: la licenza
# si dice qui, con il testo che la cartella licenze ha gia'.
DA_ARCHIVIO = {
    "libiconv": "LGPL-2.1-or-later, testi\\LGPL-2.1.txt",
    "lzo": "GPL-2.0-or-later, testi\\GPL-2.0.txt",
    "opus-dnn": "i modelli di Opus, con la licenza di Opus (libmpv\\opus)",
}
# Le librerie che arrivano come archivio dal sito del progetto: i file di
# licenza si prendono dal suo repository ufficiale.
REPOSITORY_UFFICIALI = {"libopenmpt": "https://github.com/OpenMPT/openmpt"}
# Le librerie senza file di licenza nella radice: che cosa dire.
# Gli altri testi: cartella in licenze, repository, a che cosa serve.
ALTRI = [
    ("winrt", "https://github.com/pywinrt/pywinrt", "i pacchetti winrt del riconoscimento dei caratteri"),
    ("fluidr3", "https://github.com/pianobooster/fluid-soundfont", "il banco di suoni FluidR3 GM, scaricato per i MIDI"),
    # La DLL di PortAudio viaggia dentro sounddevice, che porta solo la sua
    # licenza (1.97.9, permesso di Gabriele del 5 ottobre 2026).
    ("portaudio", "https://github.com/PortAudio/portaudio", "PortAudio, la libreria del suono degli effetti, dentro sounddevice"),
]
SENZA_FILE = {
    "avisynth-headers": "solo le intestazioni di AviSynth+, per usarlo se è installato; la licenza è scritta in testa ai file",
    "nvcodec-headers": "solo le intestazioni delle schede NVIDIA, per usarle se ci sono; la licenza è scritta in testa ai file",
}


def _richiesta(url, intestazioni=None):
    if not url.startswith("https://"):
        raise ValueError(f"indirizzo non https: {url}")
    richiesta = urllib.request.Request(url, headers={"User-Agent": "MeTeOra", **(intestazioni or {})})  # noqa: S310
    with urllib.request.urlopen(richiesta, timeout=30) as risposta:  # noqa: S310
        return risposta.read()


def _gettone_di_github():
    gh = shutil.which("gh")
    if not gh:
        return None
    try:
        # Un comando fisso, senza argomenti che vengano da fuori.
        uscita = subprocess.run([gh, "auth", "token"], check=True, capture_output=True, text=True)  # noqa: S603
    except (OSError, subprocess.CalledProcessError):
        return None
    return uscita.stdout.strip() or None


GETTONE = _gettone_di_github()


def _github_api(percorso):
    intestazioni = {"Accept": "application/vnd.github+json"}
    if GETTONE:
        intestazioni["Authorization"] = f"Bearer {GETTONE}"
    return json.loads(_richiesta(f"https://api.github.com/{percorso}", intestazioni))


def script_della_build():
    """Il testo di ogni script di packages, al commit fissato: {nome: testo}."""
    commit = prepara_ambiente.WINBUILD_COMMIT
    script = {}
    for voce in _github_api(f"repos/{WINBUILD}/contents/packages?ref={commit}"):
        if voce["name"].endswith(".cmake"):
            url = f"https://raw.githubusercontent.com/{WINBUILD}/{commit}/packages/{voce['name']}"
            script[voce["name"][:-6]] = _richiesta(url).decode("utf-8")
    return script


def leggi_script(testo):
    """Repository e dipendenze dell'ExternalProject_Add di uno script."""
    repository = re.search(r"\bGIT_REPOSITORY\s+(\S+)", testo) or re.search(r"\bURL\s+(\S+)", testo)
    dipendenze = []
    blocco = re.search(r"\bDEPENDS\b(.*?)(?=\n\s*[A-Z_]{3,}\b)", testo, re.DOTALL)
    if blocco:
        dipendenze = [t for t in blocco.group(1).split() if not t.startswith("#")]
    return (repository.group(1) if repository else ""), dipendenze


def librerie_di_mpv(script, nella_dll):
    """Le librerie di libmpv: mpv e le sue dipendenze, seguite fino in fondo."""
    viste, da_fare = set(), ["mpv"]
    while da_fare:
        nome = da_fare.pop()
        nome = VARIABILI.get(nome, nome)
        if nome in viste or nome not in script:
            continue
        if nome in VARIABILI.values() and nome.encode() not in nella_dll:
            continue
        viste.add(nome)
        da_fare.extend(leggi_script(script[nome])[1])
    return sorted(viste)


def _di_licenza(nome):
    return bool(NOMI.match(nome)) and not SCARTATI.search(nome)


def _file_github(proprietario, nome):
    radice = _github_api(f"repos/{proprietario}/{nome}/contents")
    return [(v["name"], v["download_url"]) for v in radice if v["type"] == "file" and _di_licenza(v["name"])]


def _file_gitlab(host, percorso):
    progetto = urllib.parse.quote(percorso, safe="")
    radice = json.loads(_richiesta(f"https://{host}/api/v4/projects/{progetto}/repository/tree?per_page=100"))
    return [(v["name"], f"https://{host}/{percorso}/-/raw/HEAD/{v['name']}") for v in radice if v["type"] == "blob" and _di_licenza(v["name"])]


def _file_codeberg(percorso):
    radice = json.loads(_richiesta(f"https://codeberg.org/api/v1/repos/{percorso}/contents"))
    return [(v["name"], v["download_url"]) for v in radice if v["type"] == "file" and _di_licenza(v["name"])]


def _file_googlesource(url):
    ramo = "+/refs/heads/main"
    testo = _richiesta(f"{url}/{ramo}/?format=JSON").decode("utf-8")
    radice = json.loads(testo.split("\n", 1)[1])
    return [(v["name"], f"{url}/{ramo}/{v['name']}?format=TEXT") for v in radice["entries"] if v["type"] == "blob" and _di_licenza(v["name"])]


def file_di_licenza(repository):
    """I file di licenza della radice di un repository: [(nome, url)]."""
    indirizzo = urllib.parse.urlparse(repository.removesuffix(".git"))
    percorso = indirizzo.path.strip("/")
    if indirizzo.netloc == "github.com":
        return _file_github(*percorso.split("/")[:2])
    if indirizzo.netloc in ("gitlab.com", "code.videolan.org", "gitlab.freedesktop.org"):
        return _file_gitlab(indirizzo.netloc, percorso)
    if indirizzo.netloc == "codeberg.org":
        return _file_codeberg(percorso)
    if indirizzo.netloc.endswith("googlesource.com"):
        return _file_googlesource(repository.removesuffix(".git"))
    raise ValueError(f"non so leggere i file di {repository}")


def scarica(nome, repository, cartella):
    """Scarica i file di licenza di un repository in licenze/cartella/nome:
    i loro nomi."""
    scritti = []
    for file, url in file_di_licenza(repository):
        contenuto = _richiesta(url)
        if url.endswith("?format=TEXT"):
            contenuto = base64.b64decode(contenuto)
        arrivo = os.path.join(LICENZE, cartella, nome, file)
        os.makedirs(os.path.dirname(arrivo), exist_ok=True)
        with open(arrivo, "wb") as f:
            f.write(contenuto)
        scritti.append(file)
    return scritti


def main():
    with open(DLL, "rb") as f:
        nella_dll = f.read().lower()
    script = script_della_build()
    componenti = []
    for nome in librerie_di_mpv(script, nella_dll):
        repository = REPOSITORY_UFFICIALI.get(nome) or leggi_script(script[nome])[0]
        voce = {"nome": nome, "repository": repository.removesuffix(".git"), "file": []}
        if nome in DA_ARCHIVIO:
            voce["licenza"] = DA_ARCHIVIO[nome]
            componenti.append(voce)
            continue
        voce["file"] = scarica(nome, repository, "libmpv")
        if nome in SENZA_FILE:
            voce["licenza"] = SENZA_FILE[nome]
        elif not voce["file"]:
            sys.exit(f"{nome}: nessun file di licenza nella radice di {repository}; va detto in SENZA_FILE.")
        componenti.append(voce)
        print(f"{nome}: {', '.join(voce['file']) or 'niente'}", flush=True)
    altri = []
    for nome, repository, ruolo in ALTRI:
        file = scarica("", repository, nome)
        if not file:
            sys.exit(f"{nome}: nessun file di licenza nella radice di {repository}.")
        altri.append({"nome": nome, "repository": repository, "ruolo": ruolo, "file": file})
        print(f"{nome}: {', '.join(file)}", flush=True)
    with open(ELENCO, "w", encoding="utf-8") as f:
        json.dump({"build": prepara_ambiente.MPV_BUILD, "commit_degli_script": prepara_ambiente.WINBUILD_COMMIT, "libmpv": componenti,
            "altri": altri}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(componenti)} librerie di libmpv e {len(altri)} altri testi, elenco in {ELENCO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
