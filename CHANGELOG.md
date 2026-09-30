# Changelog - MeTeOra

Tutti i cambiamenti e le novità introdotte nelle versioni di MeTeOra.

## [1.28.1] - 2026-10-01

- Una barra rovesciata sola per le due ricerche: con il fuoco nella console cerca nella console, da ogni altro punto cerca in tutte le playlist e le unità. La barra verticale torna libera.

## [1.28.0] - 2026-10-01

- La selezione multipla nella plancia, come in Esplora risorse: Maiuscolo con le frecce allarga la selezione, Ctrl con le frecce muove il fuoco senza selezionare, Ctrl con Spazio seleziona e deseleziona la voce col fuoco. Un ramo selezionato vale per tutto ciò che contiene, anche chiuso. Con più voci selezionate: X le suona come una playlist invisibile, che resta finché V non la chiude; Canc toglie i brani dalle playlist, elimina le playlist dopo una conferma e svuota i filtri; Maiuscolo con Canc manda i file nel cestino con una conferma sola; F4 li mette nei Preferiti; il menu ha anche Crea playlist dalla selezione e Aggiungi alla playlist. La selezione resta anche quando la plancia si ricostruisce. Il cruscotto spiega i tasti della selezione.
- X su ciò che sta suonando lo fa ripartire da capo, come in Winamp, con un suono suo; in pausa riprende dal punto.

## [1.26.0] - 2026-10-01

Chiude la tappa 2 del piano (issue 13).

- Alla riapertura MeTeOra ritrova ciò che suonava all'uscita: la stessa playlist, cartella o file, lo stesso brano e sottobrano, allo stesso punto, in pausa, con la selezione della plancia su di lui. X riparte.
- J e K portano il fuoco nella plancia sulla playlist precedente e successiva, la aprono tutta, sottobrani compresi, e suonano il suo primo elemento, se ne ha. Senza una playlist di partenza K va alla prima e J all'ultima.
- Le cifre da 1 a 9, e lo 0 per la decima, fanno lo stesso con le prime dieci playlist salvate.
- L'apostrofo e la ì sono riservati alla scelta della traccia audio, che arriverà.

## [1.23.0] - 2026-09-30

- I Risultati della ricerca sono un albero che ricrea la provenienza: sotto il nome della playlist, o sotto Preferiti, quelli trovati nelle playlist; lungo il percorso della cartella, unità per unità e cartella per cartella, quelli trovati sul disco. Ogni ramo dice quanti risultati contiene, e dal suo menu si salva da solo come playlist. Le pagine da mille restano come riserva, dentro ogni ramo. F8 apre i rami fino al brano che suona.

## [1.22.0] - 2026-09-30

- Le cartelle di Questo PC, dopo il nome, dicono quanti file suonabili contengono, sottocartelle comprese, e quanto durano in tutto; se una cartella non ha niente da suonare lo dice. Il conto si fa in sottofondo, ogni cartella del disco si legge una volta sola, e le durate arrivano mentre lo schedario le legge. Aggiorna rifà il conto.

## [1.21.2] - 2026-09-30

- Nei campi da riempire, come il passo del salto, il volume, il tempo di W, i nomi e i filtri, il testo di prima arriva selezionato: scrivendo lo si sostituisce, senza doverlo cancellare.
- L'esempio del passo del salto usa il punto decimale, 2.5, non più la virgola.

## [1.21.0] - 2026-09-30

- Il volume sale fino a 300: oltre il 100 amplifica gli audio registrati troppo bassi, e la console lo dice.

## [1.20.0] - 2026-09-30

- F1, F2 e F3 scrivono manuale, novità e crediti nella console, come F12, e ci portano il fuoco con il cursore sulla prima riga: niente più finestre a parte. Le novità arrivano senza i segni del Markdown, con le versioni scritte come frasi.
- Ogni scritta della console ha in fondo l'ora, ore e minuti; un testo lungo la ha solo in fondo all'ultima riga.
- La barra verticale, cioè Maiuscolo con la barra rovesciata, cerca un testo nella console e ci porta il fuoco sulla prima occorrenza; nella console Invio passa alla seguente e, arrivato in fondo, riparte dall'inizio con un suono suo.

## [1.17.4] - 2026-09-30

- F12, dopo aver scritto l'elenco dei tasti, porta il fuoco nella console con il cursore sulla prima riga dell'elenco: non serve più F6.

## [1.17.3] - 2026-09-30

- Il manuale diceva che Esc chiude il manuale, le novità e i crediti: in realtà esce da MeTeOra salvando tutto, ed è giusto così. Corretta la dicitura.

## [1.17.2] - 2026-09-30

- I suoni di Maiuscolo con F8 sono lo stesso laser: sale quando aggancia l'inseguimento e scende quando lo sgancia. Il suono che sale, meteora_aggancio, è nuovo ed è entrato nella collezione di GBUtils.

## [1.17.1] - 2026-09-30

- Tolti Maiuscolo con Z e Maiuscolo con B: con Z e B che seguono la plancia, i sottobrani si scorrono aprendo il ramo del SID.

## [1.17.0] - 2026-09-30

- Z, B e N seguono la plancia, come l'avanzamento automatico: se ciò che suona si vede, Z e B vanno alla voce suonabile prima o dopo, sottobrani compresi, anche in un'altra cartella o playlist aperta; N ne sceglie una a caso fra quelle che si vedono. Se ciò che suona non si vede, decide la sua lista; con il loop decide il loop.
- F12 scrive nella console l'elenco di tutti i tasti, preso dalla sezione I tasti del manuale, riscritta perché li raccolga tutti, una riga per tasto; poi F6 porta il cursore al suo inizio. Il cruscotto lo ricorda.

## [1.15.0] - 2026-09-30

- La ricerca globale (issue 10). La barra rovesciata apre un campo uguale a quello del filtro, con la stessa grammatica. Con Invio la ricerca parte in sottofondo, prima nei Preferiti e nelle playlist, poi in tutte le unità (dischi e chiavette; niente unità di rete e CD), e raccoglie ciò che trova nel ramo Risultati, fra i Preferiti e le playlist, che si riempie mentre cerca. Mille risultati alla volta, con la voce Mostra altri risultati in fondo; il menu ha Riproduci, Salva come playlist, Nuova ricerca e Ferma la ricerca. I Risultati sono temporanei: la ricerca seguente li sostituisce.

## [1.14.0] - 2026-09-30

- Maiuscolo con F8 aggancia e sgancia l'inseguimento (issue 9): agganciato, a ogni cambio di brano la selezione della plancia va su ciò che suona, senza spostare il fuoco. Due suoni nuovi per agganciare e sganciare; la scelta resta alla riapertura.

## [1.13.0] - 2026-09-30

- Quando un brano finisce da solo, il successivo lo decide la plancia (issue 11). Se ciò che suona si vede, si passa alla voce suonabile che viene dopo scendendo nella plancia: dentro i rami aperti tutto ciò che contengono, sottobrani compresi, anche in un'altra cartella o playlist aperta più avanti. Un SID chiuso lascia il posto al file dopo. Se davanti non c'è niente di aperto, la riproduzione si ferma. Se ciò che suona non si vede, si segue la sua lista come prima; con il loop decide il loop.

## [1.12.2] - 2026-09-30

Correzioni dal collaudo della 1.8.0.

- Il cruscotto ricorda davvero il cursore: il controllo, ricevendo il fuoco, lo rimetteva in cima, e ora lo si riporta dove era.
- I secondi si scrivono con il punto decimale, come sei abituato: 1.2, non più 1,2. La virgola si accetta ancora.

## [1.12.0] - 2026-09-30

Novità dal collaudo della 1.8.0.

- La durata accanto a ogni brano, nelle playlist e nei file di Questo PC, appena lo schedario la conosce. Un SID con più sottobrani dice quanti sono e quanto durano in tutto.
- Nella console le informazioni che si ripetono, volume, muto, salti nel brano e passi, riscrivono la loro riga invece di aggiungerne sempre un'altra.
- F9 chiude e F10 apre tutto il ramo selezionato, con due suoni nuovi (issue 11). F10 carica cartelle, playlist e sottobrani, e sotto Questo PC si ferma dopo duemila rami. F9 non dice più cosa suona: lo dice già la console.
- Maiuscolo con C toglie il loop A-B da qualsiasi punto.

## [1.8.0] - 2026-09-30

- Il filtro delle playlist e dei Preferiti (issue 2). È la prima voce di ogni playlist: Filtro (Tutto), o il testo del filtro. Invio o freccia destra aprono il campo, dove Invio conferma, Ctrl più Invio va a capo ed Esc annulla; Canc sulla voce lo svuota. Decide cosa si vede, cosa si conta e cosa si suona. Spazio per tutti i termini, barra verticale per le alternative, meno per escludere, asterisco e cancelletto come jolly, virgolette per le sequenze esatte, e i comandi t tempo, d dimensione, k tipo, a autore, n titolo, l album, g genere, y anno, p percorso, s saltato, r sottobrani. Un filtro che non si capisce viene spiegato e riproposto. Si salva con la playlist.

## [1.7.0] - 2026-09-30

- Conti e durate delle playlist e dei Preferiti (issue 4): dopo il nome, brani: numero (durata), totali: numero (durata), con la durata in ore, minuti, secondi e millesimi, le ore solo se ci sono e i millesimi solo se non sono zero. I brani senza una durata nota sono contati a parte. Il primo conto diventerà quello dei brani filtrati con la issue 2.
- Lo schedario dei file: durata, dimensione e tag di ogni brano si leggono in sottofondo, senza fermare la finestra, e si ricordano nel file MeTeOra - Schedario.json; un file si rilegge solo se cambia. Per i file audio li legge la libreria mutagen, per i SID l'intestazione e il database di HVSC.

## [1.6.0] - 2026-09-30

- I Preferiti (issue 3): la prima voce della plancia, una playlist speciale in cui F4, o la voce Aggiungi ai preferiti del menu, manda il brano, il file o il sottobrano selezionato, da qualsiasi playlist o cartella. Un brano che c'è già non si doppia. Canc su un brano dei Preferiti lo toglie; i Preferiti non si rinominano e non si eliminano. Il filtro arriverà con la issue 2.

## [1.5.0] - 2026-09-30

- X su una cartella o su un'unità la suona con tutto l'albero che le sta sotto (issue 5): prima i suoi file, poi quelli delle sottocartelle, in ordine alfabetico, e Z, B e N girano su tutti. F8 ritrova il brano anche in una sottocartella mai aperta, aprendo i rami fino a lui.

## [1.4.0] - 2026-09-30

- Maiuscolo con Canc, o la voce Manda nel cestino del menu, manda nel cestino di Windows il file di un brano o di un file di una cartella (issue 6). Chiede conferma, con No come risposta predefinita; il brano esce dalla playlist, o il file dalla cartella nella plancia. Se il file sta suonando, prima si ferma.

## [1.3.0] - 2026-09-30

- Il loop A-B fra brani (issue 8). Maiuscolo con X sul brano selezionato mette il punto A, su un altro brano della stessa lista il punto B; da quel momento la riproduzione gira in tondo fra i due, e X, Z, B e N lavorano solo lì dentro. Maiuscolo con X sul punto B lo toglie, sul punto A toglie il loop. I due brani lo dicono nella plancia, F9 lo ricorda, e il ritorno da B ad A ha un suono suo.

## [1.2.0] - 2026-09-30

- I sottobrani dei SID (issue 7). Un SID con più sottobrani è un ramo della plancia, in Questo PC e nelle playlist: dentro ci sono i sottobrani con la loro durata, da suonare o da aggiungere a una playlist come brani a sé. Maiuscolo con Z e Maiuscolo con B passano al sottobrano precedente e successivo di quello che suona.
- I brani di una playlist si caricano nella plancia quando la si apre: le playlist molto lunghe non rallentano più l'avvio.

## [1.1.0] - 2026-09-30

- Maiuscolo con M chiede di quanto cambiano il volume più e meno, da 1 a 50. Il valore resta anche alla riapertura.

## [1.0.5] - 2026-09-30

Le correzioni del collaudo della tappa 1.

- L'area dei messaggi ora si chiama console, e la barra di stato cruscotto: nella finestra, nel manuale e nel codice.
- Il cruscotto ricorda il cursore: tornando con F7 dallo stesso punto non si riparte dalla prima riga.
- Il messaggio del brano in riproduzione, e quello di F9, danno il percorso completo del file.
- Nelle playlist i brani si vedono con l'estensione.
- I secondi del salto e il tempo di W accettano i decimali, con il punto o con la virgola: 1.2 vuol dire un secondo e due decimi, non più un minuto e due secondi.

## [1.0.0] - 2026-09-30

Nasce il programma: MeTeOra si apre, suona e si comanda da tastiera. È la tappa 1 del piano, lo scheletro su cui cresceranno le altre.

- La finestra, massimizzata, con tre aree nell'ordine di tabulazione: la plancia dei comandi (F5), l'area dei messaggi (F6) e la barra di stato (F7), che elenca i tasti del punto da cui ci si arriva. L'area dei messaggi ricorda dove avevi lasciato il cursore e tiene le ultime duemila righe.
- La plancia dei comandi, un albero con Playlist, Questo PC, Apri file e Impostazioni. Invio, il tasto Applicazioni e la barra spaziatrice aprono il menu di ogni voce; Canc elimina una playlist, dopo una conferma, o toglie un brano.
- Le playlist: nuova, rinomina, elimina, riproduci; brani da spostare su, giù, in cima e in fondo, da saltare o da togliere. Si salvano da sole a ogni modifica.
- Questo PC: le unità con lettera e nome del volume, le cartelle e i file supportati, letti quando si apre il ramo. Una cartella si suona come playlist temporanea, oppure diventa una playlist vera con Crea playlist da qui, sottocartelle comprese. Aggiungi alla playlist porta file e cartelle in una playlist esistente o nuova.
- Apri file suona un file senza metterlo in una playlist.
- La riproduzione con libmpv e i SID in tempo reale, con la durata dal database di HVSC. Il brano in riproduzione non sposta mai la selezione; nella plancia porta l'indicazione "in riproduzione", F8 ci porta la selezione e F9 dice cosa suona e a che punto è.
- I tasti: X riproduce o riprende, C pausa, V stop, Z e B brano precedente e successivo, N a caso, Q ed E indietro e avanti, Maiuscolo con Q ed E il passo del salto, W vai a un tempo, più e meno il volume, M muto, Esc esce salvando. Gli altri tasti a lettera, già assegnati alle tappe successive, dicono che arriveranno.
- Un effetto sonoro per ogni azione, con Acusticator, diverso per ogni evento.
- Il manuale (F1), le novità (F2) e i crediti (F3).

## [0.1.0] - 2026-09-29

Nasce il repository, dopo la fase di studio. Non c'è ancora un programma da usare: ci sono il piano, le prove di fattibilità e i prototipi.

- Il piano in `docs/piano.txt`: obiettivi, requisiti di accessibilità nati dal confronto con foobar2000, interfaccia ad albero con area dei messaggi e barra di stato, tasti rapidi, funzioni, architettura, tappe e rischi.
- Le prove della tappa 0 in `docs/tappa0-risultati.txt`: libmpv legge moltissimi formati, fa seek, velocità ed equalizzatore al volo, e segnala la fine del brano; non legge i SID.
- Il motore SID in tempo reale: una DLL propria su libsidplayfp, un filo che emula in anticipo e tiene il brano in memoria, e un flusso WAV virtuale che lo passa a libmpv. Parte in meno di mezzo secondo e non scrive niente su disco. Approvato all'ascolto.
- La lettura delle durate e dei sottobrani dal database Songlengths della High Voltage SID Collection.
- Lo script `strumenti/prepara_ambiente.py`, che scarica libmpv e compila la DLL dei SID.
