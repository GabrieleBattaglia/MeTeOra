# MeTeOra

Un lettore audio e video per Windows pensato per chi usa uno screen reader e un display braille. Motore di riproduzione solido, moltissimi formati, compresa la musica del Commodore 64 in formato SID, controllo completo da tastiera, e un riscontro scritto e sonoro per ogni azione. Niente skin o copertine.

MeTeOra è formato da tre parole italiane, una dedica alla mia ragazza Ginevra, e insieme sono una parola luminosa.

Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

## Stato

In sviluppo, senza ancora una release. La versione 1.0.0 chiude la tappa 1: la finestra con la plancia dei comandi, le playlist, Questo PC e la riproduzione, SID compresi. Il piano è in `docs/piano.txt`, le prove di fattibilità in `docs/tappa0-risultati.txt`, il manuale in `manuale.txt`, le novità di ogni versione in `CHANGELOG.md`.

## Come è fatto

- Riproduzione con libmpv, tramite python-mpv.
- I SID sono emulati in tempo reale da libsidplayfp, con una piccola DLL scritta per MeTeOra (`sidshim/sidshim.cpp`): il brano si rende in memoria mentre suona, e libmpv lo riceve come un normale file WAV. Le durate e i sottobrani vengono dal database Songlengths della High Voltage SID Collection.
- I MIDI li rende FluidSynth, scaricato al primo MIDI, con un banco di suoni General MIDI; la musica delle console la rende libgme. Anche loro si rendono in memoria e arrivano a libmpv come file WAV.
- Interfaccia in wxPython con un albero dei comandi, la console e il cruscotto.

## Preparare l'ambiente di sviluppo

Le librerie native non stanno nel repository. Servono Python 3.14, 7-Zip installato e una connessione.

```
pip install -r requirements.txt
python strumenti/prepara_ambiente.py
```

Lo script scarica libmpv, scarica MSYS2 in versione portatile se non c'è, compila la DLL dei SID, installa libgme con pacman e mette tutto nella cartella `lib`. Se MSYS2 è già su disco, la variabile `METEORA_MSYS2` gli dice dove trovarlo.

Poi MeTeOra si avvia con `python meteora.py`, e le prove con `python -m pytest`: le finestre delle prove nascono su un desktop di Windows nascosto e gli effetti sonori tacciono.

I prototipi della cartella `prototipi` si avviano da lì dentro, per esempio `python prova_zapping.py E:\C64Music\MUSICIANS\H\Hubbard_Rob`.

## Licenza

GPL 3. libsidplayfp è distribuita sotto GPL, e MeTeOra la usa; FluidSynth e libgme sono sotto LGPL 2.1.
