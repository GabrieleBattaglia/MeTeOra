# MeTeOra

Un lettore audio e video per Windows pensato per chi usa uno screen reader e un display braille. Motore di riproduzione solido, moltissimi formati, compresa la musica del Commodore 64 in formato SID, controllo completo da tastiera, e un riscontro scritto e sonoro per ogni azione. Niente skin o copertine.

MeTeOra è formato da tre parole italiane, una dedica alla mia ragazza Ginevra, e insieme sono una parola luminosa.

Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).

## Scaricare e installare

MeTeOra si scarica dalla pagina delle release, https://github.com/GabrieleBattaglia/MeTeOra/releases/latest. Ci sono due file:

- MeTeOra-Setup seguito dal numero della versione: il programma di installazione, che va bene quasi per tutti. Non chiede i diritti di amministratore, installa MeTeOra per il tuo utente, nella cartella AppData\Local\Programs\MeTeOra, e lo mette nel menu Start. Si disinstalla da Impostazioni di Windows, App installate; alla fine la disinstallazione chiede se cancellare anche playlist, impostazioni e marker.
- MeTeOra.zip: la versione portatile, senza installazione. Si estrae in una cartella dove puoi scrivere, per esempio dentro Documenti o su una chiavetta, e si avvia MeTeOra.exe. Non metterla in C:\Programmi: MeTeOra tiene i suoi dati accanto al programma e lì si aggiorna, e in quella cartella senza i diritti di amministratore non si può scrivere.

Il browser può dire che il file non viene scaricato spesso: in quel caso scegli di mantenerlo.

MeTeOra non è firmato digitalmente, come molti programmi liberi scritti da una persona sola. Per questo, la prima volta, Windows può mostrare la finestra Windows ha protetto il PC. Non vuol dire che il programma sia pericoloso, ma solo che Windows non lo conosce ancora: attiva il collegamento Ulteriori informazioni e poi il pulsante Esegui comunque. Le volte dopo l'avviso non torna.

## Che cosa serve

- Windows 10 o 11 a 64 bit.
- La libreria di Vulkan, vulkan-1.dll, che la riproduzione chiede già per partire, anche senza video. La installano i driver della scheda video, quindi di solito c'è. Se manca, per esempio su una macchina virtuale, MeTeOra lo dice all'avvio: si aggiornano i driver, oppure si installa il Vulkan Runtime da https://vulkan.lunarg.com.
- Per guardare i video, una scheda video con i suoi driver. Con il video spento, dei video si sente solo l'audio.
- Uno screen reader, NVDA o JAWS, che ricevono anche i sottotitoli e il karaoke, in voce e in braille. Senza screen reader, li legge la voce di Windows.
- La rete serve solo per l'aggiornamento automatico, e la prima volta che suoni un MIDI, per scaricare FluidSynth e, se lo chiedi, il banco di suoni FluidR3 GM, di circa 148 MB.

## Aggiornamenti e dati

A ogni avvio MeTeOra controlla su GitHub se c'è una versione nuova. Se c'è, una finestra mostra le novità e chiede se aggiornare. Con Aggiorna adesso, MeTeOra scarica la versione nuova, si chiude, sostituisce i suoi file e si riapre da solo. Playlist, impostazioni e marker restano come sono.

Tutti i dati stanno nella cartella di MeTeOra, accanto a MeTeOra.exe. Sono i file il cui nome comincia per MeTeOra, come MeTeOra - Playlist.json e MeTeOra - Impostazioni.json, più la cartella copie, con le ultime tre versioni di playlist, marker, impostazioni e punti lasciati. Per salvarli, o portarli su un altro computer, basta copiare quei file.

## Il manuale

Il manuale si legge online, https://gabrielebattaglia.github.io/MeTeOra/manuale.html, e da MeTeOra lo apre F1; F12 scrive nella console la guida rapida, con tutti i tasti. Le novità di ogni versione sono in `CHANGELOG.md`. Per ora MeTeOra parla solo italiano. Problemi e proposte si segnalano nella pagina Issues del repository.

## Come è fatto

- Riproduzione con libmpv, tramite python-mpv.
- I SID sono emulati in tempo reale da libsidplayfp, con una piccola DLL scritta per MeTeOra (`sidshim/sidshim.cpp`): il brano si rende in memoria mentre suona, e libmpv lo riceve come un normale file WAV. Le durate e i sottobrani vengono dal database Songlengths della High Voltage SID Collection.
- I MIDI li rende FluidSynth, scaricato al primo MIDI, con un banco di suoni General MIDI; la musica delle console la rende libgme. Anche loro si rendono in memoria e arrivano a libmpv come file WAV.
- Interfaccia in wxPython con un albero dei comandi, la console e il cruscotto.

Il piano di sviluppo è in `docs/piano.txt`, le prove di fattibilità in `docs/tappa0-risultati.txt`.

## Preparare l'ambiente di sviluppo

Le librerie native non stanno nel repository. Servono Python 3.14, 7-Zip installato e una connessione.

```
pip install -r requirements.txt
python strumenti/prepara_ambiente.py
```

Lo script scarica libmpv, scarica MSYS2 in versione portatile se non c'è, compila la DLL dei SID, installa libgme con pacman e mette tutto nella cartella `lib`. Se MSYS2 è già su disco, la variabile `METEORA_MSYS2` gli dice dove trovarlo.

Serve anche GBUtils, la libreria comune di Gabriele, che non è un pacchetto di pip: si clona https://github.com/GabrieleBattaglia/GBUtils e si aggiunge la sua cartella a PYTHONPATH. Le sue dipendenze che MeTeOra usa, sounddevice, scipy e requests, si installano con pip.

Poi MeTeOra si avvia con `python meteora.py`, e le prove con `python -m pytest`: le finestre delle prove nascono su un desktop di Windows nascosto e gli effetti sonori tacciono.

Il pacchetto si compila con `python -m PyInstaller --noconfirm MeTeOra.spec`; poi `python zip_maker.py` fa l'archivio per l'aggiornamento automatico, e `python setup_maker.py` il programma di installazione, con Inno Setup 6.

I prototipi della cartella `prototipi` si avviano da lì dentro, per esempio `python prova_zapping.py E:\C64Music\MUSICIANS\H\Hubbard_Rob`.

## Licenza

MeTeOra è software libero sotto la GNU General Public License, versione 3 o, a tua scelta, qualunque versione successiva (GPL-3.0-or-later): il testo è in `LICENSE`. La libmpv che porta con sé è una build GPL 3; libsidplayfp e mutagen sono GPL 2 o successiva, libgme e FluidSynth LGPL 2.1 o successiva. Le licenze di tutti i componenti, e dove trovarne il codice sorgente esatto, sono nella cartella `licenze`. La cartella si rifà prima di ogni release, perché LEGGIMI.txt e SORGENTI.txt portano il numero della versione e il commit di GBUtils, e ogni volta che cambia una libreria: con `python strumenti/scarica_licenze.py`, che scarica i testi che sul disco non ci sono, come quelli delle librerie dentro libmpv, e poi con `python strumenti/raccogli_licenze.py`.
