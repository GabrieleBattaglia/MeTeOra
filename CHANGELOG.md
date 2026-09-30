# Changelog - MeTeOra

Tutti i cambiamenti e le novità introdotte nelle versioni di MeTeOra.

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
