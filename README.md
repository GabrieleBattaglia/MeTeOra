# MeTeOra

Un lettore audio e video per Windows pensato per chi usa uno screen reader e un display braille. Motore di riproduzione solido, moltissimi formati, compresa la musica del Commodore 64 in formato SID, controllo completo da tastiera, e un riscontro scritto e sonoro per ogni azione. Niente streaming, skin o copertine.

MeTeOra è formato da tre parole italiane, una dedica alla mia ragazza Ginevra, e insieme sono una parola luminosa.

Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5).

## Stato

In sviluppo, nessuna versione utilizzabile. Il progetto è nella fase di studio: il piano è in `docs/piano.txt`, le prove di fattibilità e le loro misure in `docs/tappa0-risultati.txt`. Le novità di ogni versione stanno in `CHANGELOG.md`.

## Come è fatto

- Riproduzione con libmpv, tramite python-mpv.
- I SID sono emulati in tempo reale da libsidplayfp, con una piccola DLL scritta per MeTeOra (`sidshim/sidshim.cpp`): il brano si rende in memoria mentre suona, e libmpv lo riceve come un normale file WAV. Le durate e i sottobrani vengono dal database Songlengths della High Voltage SID Collection.
- Interfaccia in wxPython con un albero dei comandi, un'area dei messaggi e una barra di stato.

## Preparare l'ambiente di sviluppo

Le librerie native non stanno nel repository. Servono Python 3.14, 7-Zip installato e una connessione.

```
pip install -r requirements.txt
python strumenti/prepara_ambiente.py
```

Lo script scarica libmpv, scarica MSYS2 in versione portatile se non c'è, compila la DLL dei SID e mette tutto nella cartella `lib`. Se MSYS2 è già su disco, la variabile `METEORA_MSYS2` gli dice dove trovarlo.

I prototipi della cartella `prototipi` si avviano da lì dentro, per esempio `python prova_zapping.py E:\C64Music\MUSICIANS\H\Hubbard_Rob`.

## Licenza

GPL 3. libsidplayfp è distribuita sotto GPL, e MeTeOra la usa.
