# Changelog - MeTeOra

Tutti i cambiamenti e le novità introdotte nelle versioni di MeTeOra.

## [1.113.4] - 2026-10-21

- Correzione delle prove (issue 27): quella del filtro del tempo cadeva sempre lanciata da sola e passava nel file intero. Dopo l'apertura del brano e dopo ogni catena riscritta mpv manda l'evento AUDIO_RECONFIG, e se intanto il tono è cambiato al volo il motore riscrive la catena, come deve; al primo brano del processo la prima ricerca del karaoke tiene occupato il filo degli eventi per circa 30 ms, e quegli eventi arrivavano dopo il cambio di tono. Ora la prova aspetta che mpv abbia aperto l'uscita e che il motore abbia visto gli eventi già mandati, invece di contare sui tempi; il motore resta com'era. La stessa attesa sostituisce le pause fisse nella prova del tono cambiato al volo, che con il processo occupato cadeva per lo stesso motivo.

## [1.113.3] - 2026-10-20

- Correzione, nelle impostazioni la voce Barra dei comandi per il mouse, con una risposta che non è né sì né no, diceva nell'errore il nome dell'Inseguimento della plancia, per esempio Inseguimento della plancia: forse non è né sì né no; ora dice il suo, come Riproduzione casuale, Video e Sottotitoli letti (issue 26). Il difetto c'era dalla 1.87.0. Anche l'Inseguimento della plancia ora passa il suo nome, invece di avere quello giusto per caso. Una prova nuova scrive nella Barra dei comandi una risposta sbagliata e una vuota.

## [1.113.2] - 2026-10-20

- Correzione, issue 25: lo schedario legge i tag APEv2 dei TTA, come F11 dalla 1.69.0, e il titolo, l'autore, l'album, il genere e l'anno dei TTA arrivano nel filtro, nella ricerca e nelle statistiche, e insieme alla traccia e al disco anche in Ordina. Prima lo schedario apriva i TTA solo con mutagen, che ne vede l'ID3, di solito vuoto, e quei tag restavano vuoti. I tag che l'APEv2 non ha si prendono ancora dall'ID3, come in un TTA codificato da FFmpeg, che nell'APEv2 mette solo il nome del codificatore, e poi taggato in ID3. Le schede dei TTA si rileggono da sole, e solo quelle.

## [1.113.1] - 2026-10-20

- Correzione, nella plancia l'etichetta di un file delle console con più sottobrani, di cui qualcuno senza una durata nota, non cade più in errore (issue 24): ora, come per le cartelle, il totale somma le durate note e dice a parte quanti sottobrani ne restano senza, per esempio gioco.nsf, 5 sottobrani, 12:30 in tutto, 1 senza durata. Succede quando libgme non legge un brano, come con un .m3u che nomina brani che il file non ha; se non ne legge nessuno, l'etichetta dice solo il numero dei sottobrani, lo schedario fa lo stesso la scheda del file invece di fermarsi, e Ordina per durata lo mette in fondo con i brani senza durata, non in cima come se durasse zero. Il manuale lo dice nel capitolo Unità, cartelle e file; le prove nuove usano file finti.

## [1.113.0] - 2026-10-20

L'importazione delle playlist di altri programmi, il punto g della tappa 14 del piano, con le decisioni di Gabriele del 20 ottobre 2026. Per i due suoni nuovi serve GBUtils V212.

- Novità, Importa playlist: l'ultima voce del ramo Playlist, dopo Nuova playlist, e una voce del menu del ramo apre la finestra dei file di Windows, a selezione multipla, con i filtri Playlist e Tutti i file. Le playlist M3U, M3U8 e PLS scelte diventano playlist di MeTeOra, salvate nel suo file delle playlist, una alla volta, e la selezione va sulla prima, come con Nuova playlist. Il nome è quello del file: Rock anni 80.m3u diventa Rock anni 80, o Rock anni 80 2 se il nome c'è già. Nessun tasto rapido, come per gli altri comandi della plancia.
- Le playlist che arrivano da fuori si importano e suonano subito, come un file aperto da Windows: con un doppio clic, Apri con, il trascinamento sulla finestra, la riga di comando, una copia di MeTeOra già aperta, e Apri file, che ha un filtro Playlist e le comprende anche fra i file multimediali. Più playlist insieme si importano tutte, una alla volta, e suona la prima; insieme ad altri file suonano quelli, come prima, e le playlist si importano soltanto. La selezione della plancia non si sposta. Le playlist dentro una cartella trascinata non si guardano, e nelle cartelle di Questo PC e Questa rete i file M3U e PLS restano nascosti.
- Come si leggono: un M3U8 sempre in UTF-8, un M3U o un PLS in UTF-8 se lo è, altrimenti nella codifica di Windows, e con la BOM UTF-16 in UTF-16. Le righe degli M3U che cominciano con il cancelletto, come #EXTINF, e i titoli e le durate dei PLS si ignorano, perché li dà lo schedario; le voci dei PLS vanno nell'ordine del loro numero. I percorsi relativi valgono dalla cartella della playlist, quelli con la barra iniziale dalla sua unità, i file:/// diventano percorsi, anche scritti file://C:/ con due barre sole e con un cancelletto nel nome, e tutto si salva intero, con l'unità o la condivisione, la forma che la pulizia all'avvio controlla. I doppioni restano, nell'ordine del file.
- Si saltano, e la console lo dice, gli indirizzi in rete, come le radio in http, le cartelle, le playlist dentro la playlist, i file di un formato che MeTeOra non suona, i percorsi con caratteri che Windows non accetta e i file che non ci sono. Cartelle e formati si riconoscono dal nome, e sui dischi del computer guardando il disco: una cartella come Live.1986 resta una cartella. I file si controllano in un filo a parte, con le regole della pulizia all'avvio: si salta un file che manca su un'unità o una condivisione che risponde, e si tengono le voci di un disco staccato o di una lettera che non c'è. La console dice per esempio Importata la playlist Rock: 40 brani, da E:\Musica\Rock.m3u. Saltate 3 voci: 2 file che non ci sono, 1 indirizzo in rete; con le voci tenute, Tenute senza controllo 30 voci di F:, che non risponde. Poi una riga per ogni voce saltata, con il motivo, fino a venti, e quante altre. Se il controllo tarda, la console dice che sta controllando, ma solo finché il lavoro è davvero in corso, non mentre l'esito aspetta la fine di un dialogo. Il file della playlist su una condivisione si legge in un filo sorvegliato, come nella pulizia: muto per 15 secondi, la lettura si annulla e la console dice che la condivisione non risponde, così la coda va avanti. Una playlist che arriva mentre se ne importa un'altra aspetta il suo turno, e se l'attesa si allunga la console lo dice: Pop.m3u aspetta che finisca l'importazione di Rock.m3u. Una playlist senza niente da importare non nasce, e il file m3u accanto a un gioco delle console, che libgme usa già da solo come lista dei brani, non si importa.
- MeTeOra ricorda da quale file nasce ogni playlist importata, anche se poi la rinomini, e F11 sulla playlist lo dice: Importata da E:\Musica\Rock.m3u. Se lo stesso file arriva di nuovo ed è com'era, cioè con la stessa dimensione e la stessa data, a meno di due secondi, si usa la sua playlist; se è cambiato, la domanda Rock.m3u è cambiato dopo l'importazione. Rileggerlo, perdendo le modifiche fatte in MeTeOra? Con No o con Esc resta quella che c'è; con Sì la playlist tiene nome, posto, filtro e tasto cifra, e cambiano solo i brani: il loop A-B su di lei si toglie, e il brano che suona continua, poi B riparte dal primo. Se nel file cambiato non resta niente da importare, la console dice Niente da rileggere e la playlist resta com'è, come con No: arrivata da Windows suona, dal comando prende la selezione. Il file delle playlist resta alla versione 1, con il campo facoltativo origine; una versione di MeTeOra precedente lo perderebbe al primo salvataggio.
- Due suoni nuovi, fatti da ClaudIA per la collezione di GBUtils V212: meteora_playlist_gia_importata, di onda triangolare come i suoni delle playlist, due tocchi uguali di sol 5 e un re 5 più lungo, come chi riconosce qualcosa che c'è già; e meteora_playlist_riletta, di seno, una scivolata che scende, il file riletto da capo, e tre note che risalgono, mi 5, si 5 e mi 6. Una playlist importata la prima volta ha il suono della playlist creata, e gli errori e le playlist senza niente da importare i loro di sempre.
- Le associazioni dei formati comprendono le playlist M3U, M3U8 e PLS, con un tipo loro, Playlist per MeTeOra. Chi ha già associato MeTeOra deve rifare Associa, nelle impostazioni, perché compaia in Apri con anche per le playlist; la disinstallazione toglie anche questo tipo.
- Le statistiche, nella sezione Playlist e Preferiti, contano le playlist importate e i loro brani, quelle arrivate di nuovo e quelle rilette; le importate stanno anche nella riga delle playlist create. I due eventi nuovi hanno il loro nome in Tutti gli eventi, e contano fra quelli che MeTeOra conosce.

## [1.112.0] - 2026-10-20

La protezione dei dischi nella pulizia all'avvio, decisa da Gabriele il 20 ottobre 2026 al posto della pulizia regolabile del punto f della tappa 14, depennato perché la pulizia all'avvio basta: le voci che toglie devono essere di file davvero inutilizzabili. Con le sue risposte della sera dello stesso giorno, Riconosci questo disco, la Sentinella che guarda i dischi a MeTeOra aperto e i dischi di ogni computer tenuti a parte; con il terzo giro di risposte, la stessa sera, la conferma di Riconosci questo disco con il conto delle voci, la riga e il suono della Sentinella e il MachineGuid accanto al nome del computer. Per i suoni di Riconosci questo disco e della Sentinella serve la collezione di GBUtils che li comprende.

- Novità, la pulizia riconosce il disco di ogni lettera. Prima un'altra chiavetta, o un altro disco, nella lettera di uno che MeTeOra conosceva rispondeva, i file non c'erano, e la pulizia toglieva le voci del primo anche se i suoi file erano intatti, solo staccati. Ora le unità del PC, cioè dischi fissi e rimovibili, CD e dischi in memoria, si riconoscono dal numero di serie del volume, quello che dice il comando vol; le unità di rete con la lettera dalla condivisione a cui portano, perché in rete il numero di serie non è affidabile e chiederlo potrebbe restare appeso come una lettura; le cartelle di rete scritte per esteso, come \\server\condivisione, dal loro nome; le lettere fatte con subst dalla cartella a cui portano, con il numero di serie del volume se la cartella è sul PC, perché per Windows non sono connessioni di rete e hanno il numero di serie del volume su cui portano: spostata su un'altra cartella dello stesso volume, una subst sembrerebbe la stessa; se la cartella è su un'unità di rete con la lettera, invece, dalla condivisione, come quell'unità. Quello che la pulizia sa dei dischi sta nel file nuovo MeTeOra - Dischi.json, accanto agli altri dati.
- La prima volta che incontra una lettera, la pulizia ne fa suo il disco solo se ci trova almeno la metà dei file che conosce lì e ha potuto controllare: le voci dei file spariti si tolgono a ogni avvio, quindi sul disco giusto c'è quasi tutto, mentre un disco qualunque non ha i file di un altro. Se ne trova meno, la lettera è contesa. La soglia resta la metà, come ha confermato Gabriele.
- Una lettera è contesa anche quando le risponde un disco diverso dal suo, o quando cambia disco a metà pulizia. Una lettera contesa si salta senza leggerla, le sue voci restano, e la console lo dice in fondo alla riga della pulizia: Saltata F:, usata da dischi diversi: le sue 12 voci restano, se alla lettera hanno risposto almeno due dischi; Saltata G:, non riconosco il disco che risponde: le sue 10 voci restano, se ne ha visto uno solo, che non è mai stato il suo, come la prima volta di una chiavetta senza i file che MeTeOra conosce lì. Resta contesa anche quando torna il suo disco, la strada prudente scelta da Gabriele, perché lì le voci dei due dischi sono mescolate: tornata la prima chiavetta, la pulizia toglierebbe le voci della seconda, che è solo staccata. Si sblocca solo a mano, con Riconosci questo disco.
- Novità, Riconosci questo disco, nel menu dell'unità in Questo PC, che si apre con Invio, Applicazioni o Spazio, scelta di Gabriele: un comando esplicito, mai niente da solo. Compare solo dove serve, cioè sulle lettere contese, e nel menu sta subito dopo Aggiorna. Da quel momento la lettera appartiene al disco che risponde adesso, smette di essere contesa, e la pulizia del prossimo avvio la controlla, togliendo le voci dei file che su quel disco non ci sono. Prima chiede conferma, scelta di Gabriele, con la domanda Sì e No di MeTeOra, dove No è la risposta predefinita ed Esc vale No, e dice quante voci la pulizia toglierà, per esempio F: diventa del disco che risponde adesso; delle 120 voci di F:, 30 sono di file che qui non ci sono e la prossima pulizia le toglierà. Riconosco? Il conto si fa in disparte, senza fermare la finestra, e legge ogni cartella una volta sola, come la pulizia; se non si può fare, per esempio perché una cartella di rete resta ferma, la domanda lo dice senza numeri. Se mentre si conta la lettera cambia disco, la domanda parla di quello che risponde alla fine, senza numeri, e non di quello che se n'è andato; se smette di rispondere, lo dice senza domanda, come una lettera che non risponde. Se mentre la domanda aspetta la Sentinella vede un altro disco nella lettera, e lo dice, il Sì non riconosce niente, perché cancellerebbe il disco appena visto: la console dice Intanto a F: ha risposto un altro disco: il disco resta da riconoscere, e il comando va scelto di nuovo. No ed Esc annullano, con il suono dell'annullamento e la riga Il disco di F: resta da riconoscere: la pulizia all'avvio continua a saltarla. Serve per un disco che prende per sempre il posto di quello di prima, come un disco nuovo o formattato, che ha un altro numero di serie, e per una lettera che la prima volta aveva meno della metà dei suoi file, per esempio perché molti erano stati cancellati. Il comando ha un suono suo, nuovo, fatto da ClaudIA per la collezione di GBUtils V211, meteora_disco_riconosciuto: onda triangolare, una scivolata che sale e una che ricade sul sol, tenuto al centro, come un disco che prende giri e si ferma al suo posto. La console dice Disco di F: riconosciuto: è quello che risponde adesso, e che cosa farà la pulizia; se la lettera non risponde, o non dice quale disco c'è, lo dice senza domanda, e il disco resta da riconoscere. Chi risponde si chiede in disparte, così una lettera che non risponde non ferma la finestra.
- La riga della pulizia dice dove trovare il comando per le lettere usate da dischi diversi: Saltata F:, usata da dischi diversi: le sue 30 voci restano. Per riconoscere il disco di adesso, Riconosci questo disco nel menu di F: in Questo PC. Con più lettere le nomina tutte, come nel menu di F: e di G:. Per una lettera vista con un disco solo, che non è mai stato il suo, come la prima volta di una chiavetta con meno della metà dei file, dice soltanto che la salta, scelta di Gabriele; il menu offre comunque Riconosci questo disco. Il cruscotto di un'unità, che si apre con F7, nomina il comando e la sua conferma.
- Novità, la Sentinella, chiesta da Gabriele: MeTeOra guarda il disco di una lettera anche a sessione aperta, ogni volta che ne usa un file, cioè quando lo suona, lo aggiunge a una playlist o ai Preferiti, lo legge lo schedario o ne apre la cartella nella plancia. Se a una lettera risponde un disco diverso da quello ricordato, la lettera diventa contesa e si salva subito: una chiavetta infilata dopo l'avvio nella lettera di un'altra, usata e tolta prima di chiudere, non sfugge più. Per una lettera che la pulizia non conosce ancora la Sentinella ricorda il disco che ci ha visto, e un secondo disco la rende contesa: anche le voci di due chiavette usate nella stessa lettera prima della pulizia non si mescolano più. La regola della metà resta per le voci di dischi che MeTeOra non ha mai visto, come quelle scritte prima di questa versione. La Sentinella chiede a Windows chi risponde una volta per lettera e non per ogni file, e si fida della risposta per cinque secondi, perché MeTeOra non riceve l'avviso di Windows sui dischi che si collegano e si staccano; la domanda si fa in disparte, quindi non rallenta la riproduzione e non ferma la finestra, e una lettera che non risponde non si aspetta. Come la pulizia, guarda le unità del PC e quelle di rete con la lettera, e lascia stare le cartelle di rete scritte per esteso. Se una lettera diventa contesa mentre la pulizia lavora, per esempio con un'altra chiavetta infilata e usata prima che la pulizia finisca, restano anche le voci che la pulizia le aveva trovato mancanti; e così se intanto scegli Riconosci questo disco, perché la pulizia l'aveva letta forse con il disco di prima: le guarda il prossimo avvio, sul disco riconosciuto. Quando rende contesa una lettera lo dice subito, chiesto da Gabriele, con una riga nella console, per esempio: F: ha un disco diverso da quello che conosco: le sue voci restano, e la pulizia la salta finché non usi Riconosci questo disco nel menu di F: in Questo PC. Insieme alla riga, un suono suo, nuovo, fatto da ClaudIA per la collezione di GBUtils V211, meteora_disco_diverso: onda triangolare, due colpetti sul fa, a sinistra e a destra, come chi bussa a una porta che conosce, e un si più lungo al centro, che scende di tritono e resta sospeso. Lo dice una volta sola per lettera e per disco, non a ogni file: lo stesso disco visto di nuovo, o quello di prima che torna, tace, e un terzo disco si dice. Con la stessa riga e lo stesso suono, dopo la riga della pulizia, si dice anche una lettera che diventa contesa alla fine della pulizia, perché la pulizia ne impara il disco mentre la Sentinella ce ne aveva visto un altro, il primo e quindi senza riga.
- Se non si legge chi risponde a una lettera, la lettera si salta senza ricordare niente, le sue voci restano per il prossimo avvio, e la riga dice che non riconosce il disco che risponde.
- Se MeTeOra - Dischi.json c'è ma non si legge, per esempio dopo una modifica a mano sbagliata, non si sovrascrive, come gli altri dati: all'avvio la console lo dice, con il suono dell'errore e il motivo, e finché non si legge la pulizia salta tutte le unità con la lettera senza imparare niente, perché le lettere contese non si possono ricostruire da nessuna parte. Le cartelle di rete scritte per esteso si puliscono come sempre.
- In MeTeOra - Dischi.json i dischi stanno separati per nome del computer, quello che Windows dice in COMPUTERNAME, scelta di Gabriele: ogni computer impara i suoi come la prima volta, e i dischi degli altri computer restano nel file come sono. Così i numeri di serie dei dischi di un computer non fanno saltare le lettere di un altro. Accanto al nome si salva il MachineGuid di Windows, letto dal registro, scelta di Gabriele: il nome resta la chiave, ma un computer che ha cambiato nome, e nel file non c'è ancora, adotta i dischi del nome vecchio con il suo stesso MachineGuid, e il file li salva sotto il nome nuovo. Se il MachineGuid non si legge, o se lo hanno più nomi, come due computer clonati dalla stessa immagine di Windows, si va per nome; e se in una sessione non si legge, il file tiene quello salvato prima. Con i dati portati da un altro computer, con la versione portatile o copiando i file, una lettera che non ha almeno la metà dei file che MeTeOra conosce in quella lettera, come quelli rimasti sull'altro computer, si salta però come la prima volta di una chiavetta, con la riga Saltata, non riconosco il disco che risponde, e le sue voci restano. Su quella lettera Riconosci questo disco va scelto solo se quei file sono spariti davvero: playlist, Preferiti, marker e statistiche sono gli stessi sui due computer, e la pulizia dopo toglierebbe le voci dei file dell'altro computer, che tornandoci non ci sarebbero più. Una lettera in cui l'altro computer trova almeno la metà dei file, invece, diventa del suo disco, e la pulizia lì toglie le voci dei file che mancano, anche se sul primo computer ci sono, come dalla 1.104.0.
- La sezione La salute delle statistiche conta anche le unità saltate perché usate da dischi diversi e quelle saltate perché il disco che rispondeva non si riconosceva; in una riga sua, Dischi riconosciuti a mano, quante volte hai scelto Riconosci questo disco, e quante lettere la Sentinella ha reso contese a MeTeOra aperto. I due eventi hanno il loro nome anche nella sezione di tutti gli eventi. La pulizia non ha suoni nuovi: lo dice la sua riga.
- pulisci_i_dati.py cancella anche MeTeOra - Dischi.json, così la prima pulizia dopo pulisci_i_dati riconosce i dischi come la prima volta; e il file entra nelle copie dei dati, nella cartella copie, come playlist, marker e impostazioni.
- Il banco del collaudo, strumenti/banco.py, ha una sessione in più, dischi: con un altro numero di serie nel file dei dischi, la pulizia salta l'unità dei dati, lo dice con dove riconoscerla, lascia nei Preferiti e nello schedario il file cancellato e ricorda il disco vero fra gli altri; poi Riconosci questo disco, dal menu dell'unità, chiede conferma con il conto delle voci da togliere, Esc annulla e S la sblocca con il disco vero; la Sentinella, con un altro disco finto mentre un file suona, la rende di nuovo contesa e lo dice subito, con il suo suono.
- Correzione delle prove: quella della pulizia che toglie i file spariti non lascia più leggere allo schedario, in sottofondo, i file finti, che teneva aperti mentre la prova ne cancellava uno, e Windows lo trovava in uso.

## [1.111.0] - 2026-10-20

La issue 21, nata da una nota di Gabriele al collaudo della 1.98.0: il punto e della tappa 14 del piano, con le decisioni di Gabriele del 20 ottobre 2026.

- Novità, nella plancia NVDA dice non selezionato come in Esplora risorse. Quando Ctrl con le frecce porta il fuoco su una voce fuori dalla selezione multipla, NVDA lo dice dopo il nome, per esempio d.mp3 non selezionato; su una voce selezionata tace, come prima. Ctrl con la barra spaziatrice, e il clic con Ctrl sulla voce che ha il fuoco, gli fanno dire selezionato o non selezionato. Quando la selezione multipla si chiude e il fuoco resta su una voce che ne era fuori, per esempio con freccia giù sull'ultima voce, con F9 sul ramo che ha il fuoco o con un clic sulla voce stessa, NVDA dice selezionato, perché Windows da sé non manderebbe niente. Senza selezione multipla la plancia si legge come sempre, e la riga della console con il conto delle voci selezionate resta. Lo fa un oggetto di accessibilità di MeTeOra per la plancia, che a NVDA dà solo lo stato di ogni voce, secondo la selezione di MeTeOra, e lascia tutto il resto all'albero di Windows: nome, ruolo, valore, e la posizione e il livello, che NVDA calcola da sé. La plancia si dichiara anche a selezione multipla, che NVDA dice solo con la lettura della selezione multipla accesa nelle sue impostazioni. Se Windows ha già spostato il fuoco con freccia sinistra o destra o con la ricerca per iniziale, e la selezione multipla non è ancora chiusa, la voce d'arrivo vale già come selezionata, perché NVDA non senta un non selezionato sbagliato.
- Una voce nuova delle impostazioni, Stato della selezione per lo screen reader, accesa di partenza. Spenta, la plancia risponde subito a NVDA come un albero di Windows, e dalla riapertura l'oggetto di MeTeOra non si attacca più.
- Il banco del collaudo ha la sessione della plancia, strumenti\banco.py --plancia, con strumenti\lettore_msaa.py, che fa la parte di NVDA da un processo a parte sullo stesso desktop nascosto: confronta voce per voce ciò che la plancia espone via MSAA con l'oggetto standard di Windows, con e senza la selezione multipla e con la voce accesa e spenta; legge gli eventi dei tasti veri come li legge NVDA, anche sull'ultima voce, dove la freccia non muove il fuoco; misura i tempi, anche con una playlist di tremila brani aperta e con la finestra occupata; e chiude MeTeOra cinque volte mentre legge la plancia senza sosta. Le misure: senza l'oggetto la plancia non risponde a WM_GETOBJECT, con l'oggetto sì, e ogni voce si legge come dall'oggetto standard tranne selezionata; da fuori una lettura completa di una voce costa circa 0.7 millesimi di secondo invece di 0.5, e nome, ruolo e stato per un evento, come li chiede NVDA, circa 1.7 invece di 0.25, di solito sotto i 4, con una punta di 7.7 in cinque corse del banco; con la finestra occupata aspettano tutte e due le strade; nelle cinque chiusure MeTeOra è uscito pulito. wx non riconverte uno stato di MSAA, PROTECTED, e cinque non li ha: una voce che ne avesse uno resterebbe allo stato di Windows, intero.

## [1.110.0] - 2026-10-20

Il punto d della tappa 14 del piano, deciso da Gabriele il 20 ottobre 2026: la durata residua a richiesta, del punto 2.5 del piano. Per il suo suono serve GBUtils V209.

- Novità, la durata residua: Maiuscolo con l'apostrofo, cioè il punto interrogativo, scrive nella console, con un suono suo, quanto manca e quanto è passato di ciò che MeTeOra suonerà, con il totale, la percentuale ascoltata e l'ora di fine prevista, poi il brano e la lista come in Dove sono, per esempio Mancano 32:40 di 46:45, trascorsi 14:05, 30.1% ascoltato, finisce verso le 23:42, brano 3 di 12, playlist Rock. Il conto segue l'avanzamento vero: se il brano che suona si vede nella plancia, le voci suonabili che vi si vedono dalla prima della lista che suona in giù, anche nelle playlist, nelle cartelle e nei sottobrani dei rami aperti dopo, perché l'avanzamento va solo avanti, e con la riproduzione casuale, che pesca fra tutte, tutte quelle che si vedono; quando la plancia va oltre la lista la riga dice quanti brani sono in tutto, e un SID aperto conta i suoi sottobrani uno per uno, anche fra i saltati; altrimenti la lista, o il loop A-B. Il trascorso sono i brani prima più il punto del brano, il mancante il resto del brano più i brani dopo, e insieme fanno il totale. I saltati e i brani nascosti dal filtro non contano, e i saltati si dicono; i brani di cui la durata non si sa si contano a parte, per esempio 3 brani senza durata, e lo schedario intanto li legge, così ripremendo il tasto il conto si completa. Un SID o un file delle console conta con il sottobrano che suonerà, e senza durata con i tre minuti a cui il motore lo ferma. A una velocità diversa da 1 si aggiunge il tempo vero di ascolto, subito dopo il mancante, con il totale dopo, per esempio Mancano 45:00, alla velocità 1.5 sono 30:00, in tutto 1:10:00, senza togliere la dissolvenza; in pausa l'ora di fine non c'è; una fine che non è oggi dice il giorno, come verso le 02:48 di domani. Con la riproduzione casuale a mazzo contano i brani usciti e quelli che restano nel mazzo, per esempio Casuale: suonati 5 di 12, nel mazzo restano 32:40 di 46:45, dove dopo Z contano anche i brani che la storia farà risuonare; con la casualità totale il resto del brano, il totale e ordine casuale senza fine. Un brano solo dice quanto gli manca, Suona un brano solo: mancano 2:10. In fondo, cosa succede dopo: la lista o la plancia che ricominciano, il ritorno al punto A del loop, il mazzo che si rimescola, il brano che si ripete, il brano tolto dalla lista dopo cui si riparte dal primo, e il timer, se ferma la musica prima della fine, o sempre quando la musica non finisce da sola; con il mazzo che si ferma, anche nel loop A-B, la riga dice solo quando finisce. La riga si riscrive a ogni pressione e va anche alla sintesi e al braille scelti per sottotitoli e karaoke, come quella di Dove sono, e come lei interrompe la voce che sta parlando, così con la voce di Windows le pressioni ravvicinate non si accodano; il fuoco resta dov'è; il cruscotto e la riga In riproduzione non cambiano. Se non suona niente, la frase e il suono di F8, ma come in Dove sono la frase va anche alla sintesi, interrompendo la voce, e al braille, dove prende il posto della riga di prima. Con 10000 voci aperte nella plancia il conto dura circa 30 millesimi di secondo, sul PC gigante.
- Un suono nuovo nella collezione di GBUtils V209, fatto da ClaudIA su richiesta di Gabriele: meteora_durata_residua, onda triangolare, due tocchi brevi che scendono dal centro verso destra, come il tic tac di un orologio, poi una scivolata di un'ottava giù, come la sabbia di una clessidra. Non è a onda quadra e non suona uguale a nessun altro suono di MeTeOra.
- La guida rapida di F12, il cruscotto e il manuale parlano di Maiuscolo con l'apostrofo, con una sezione sua, La durata residua, dopo Dove sono, e un esempio. Le statistiche danno un nome al comando e al suo suono, e chiamano il tasto sempre Maiuscolo con apostrofo, anche quando Windows lo dà come punto interrogativo.
- Il banco del collaudo ha una sessione per la durata residua, con il tasto vero della tastiera italiana e i brani letti davvero dallo schedario, che controlla anche la voce interrotta, pure dalla frase di F8; nella sessione di Dove sono, Maiuscolo con l'apostrofo non è più un tasto senza comando.

## [1.109.0] - 2026-10-20

Ordina e Mescola nel menu della playlist e dei Preferiti, la tappa 14 c del piano, con le decisioni di Gabriele del 20 ottobre 2026: quattro novità. Per i quattro suoni nuovi serve GBUtils V210, con i loro preset nella collezione.

- Novità, Ordina: nel menu di una playlist, dopo Rinomina, e in quello dei Preferiti, un sottomenu, l'unico di quel menu, con sette criteri: per nome del file, per percorso, per titolo, per autore, per album, per anno e per durata, ognuno in un verso solo, dalla A alla Z, dal più vecchio, dal più corto. I testi si confrontano senza maiuscole e accenti, come nel filtro, e i numeri per valore, così Traccia 2 viene prima di Traccia 10; nessuna regola sugli articoli. Per percorso va come Crea playlist da qui, con i file di una cartella prima delle sue sottocartelle e i sottobrani dopo il loro file; per durata vale quella che mostra la plancia, per un SID con più sottobrani il totale. Dopo il criterio vengono, per titolo, l'autore; per autore, l'album; per anno, l'autore e l'album. Un album sta in una cartella, così due Greatest Hits di autori diversi restano due album, e dentro un album si va per disco e traccia, se tutti i suoi brani hanno il numero di traccia, con il disco che manca contato come il primo, altrimenti per nome del file. I brani senza il dato vanno in fondo, in ordine di percorso, e la console lo dice: Rock ordinata per autore: 340 brani, 12 senza autore in fondo. Il titolo o l'autore <?>, che nei SID della HVSC vuol dire sconosciuto, conta come un dato che manca, come nelle statistiche. In fondo vanno anche i brani che lo schedario non ha ancora letto, ma la console li conta a parte, per esempio 12 senza autore e 200 non ancora letti dallo schedario in fondo, e avverte che un nuovo Ordina, quando sono letti, li mette al loro posto; le loro schede si chiedono allo schedario senza aspettarle. Si ordina tutta la playlist, anche i brani che il filtro nasconde, e la riga dice quanti sono. Niente conferme e niente riproduzione: il fuoco resta sulla playlist, i rami aperti restano aperti e l'ordine si salva subito, come con Sposta. Una lista già in quell'ordine lo dice, con il suono di Sposta su un brano che è già lì, e non salva niente; con meno di due brani la console dice che non c'è niente da ordinare.
- Novità, Inverti l'ordine, in fondo al sottomenu Ordina: rovescia la lista così com'è, anche un ordine fatto a mano con Sposta.
- Novità, Mescola, dopo Ordina: un ordine a caso, con ogni ordine ugualmente probabile, senza distribuire gli autori. Cambia l'ordine salvato, mentre la riproduzione casuale sceglie soltanto cosa suonare.
- Novità, Ordine di prima: dopo un Ordina, un Inverti l'ordine o un Mescola compare nel sottomenu Ordina, subito prima di Inverti l'ordine, e senza conferme rimette l'ordine di prima, con gli stessi brani, finché MeTeOra resta aperto; i brani aggiunti dopo restano in fondo, quelli tolti non tornano, un nuovo riordino lo sostituisce e, usato, la voce sparisce.
- Con la playlist che suona o è in pausa il brano continua: con Ordina e Inverti l'ordine va al suo posto nell'ordine nuovo, con Mescola in cima e gli altri mescolati dopo di lui. La console dice il suo posto nuovo, contato con il filtro fra i brani che si vedono, e l'avanzamento riparte da lì, anche con il brano seguente già preparato dalla dissolvenza. Un loop A-B sulla playlist si toglie, e la console lo dice, perché fra A e B finirebbero altri brani; Ordine di prima non lo rimette. Restano il loop con il solo punto A e quello con A e B sullo stesso brano, che non coprono altri brani.
- Correzione: quando il ramo Playlist si ricostruisce, dopo Ordina, Mescola, Sposta o un'altra modifica di una playlist, i brani aperti dentro le playlist aperte e i Preferiti, come un SID con i suoi sottobrani o un brano con i marker, restano aperti. Prima si richiudevano, e con un sottobrano di un SID aperto che suonava, quando l'avanzamento lo decide la plancia, alla sua fine si passava al brano dopo il SID, saltando i sottobrani rimasti.
- Lo schedario tiene anche traccia e disco dei file che legge da qui in poi, fuori dai tag, così il filtro e la ricerca non trovano i numeri delle tracce; le schede già salvate restano come sono, senza rilettura.
- Quattro suoni originali, di onda triangolare sulle stesse quattro note: meteora_playlist_ordinata, sol, la, si e do che salgono da sinistra a destra, con il do più lungo; meteora_ordine_invertito, le stesse al contrario, da destra a sinistra; meteora_playlist_mescolata, le stesse in disordine, rimbalzando fra i due lati, con un la sospeso in fondo; meteora_ordine_di_prima, una scivolata che torna da destra a sinistra e due tocchi sul sol.
- Le statistiche contano le playlist ordinate, invertite, mescolate e rimesse nell'ordine di prima, nella riga delle playlist e fra gli eventi.
- Il cruscotto della playlist e dei Preferiti dice le voci nuove; il manuale ha il capitolo Ordina e Mescola, due esempi, e una riga nella riproduzione casuale su che cosa cambia Mescola.
- Il banco del collaudo, strumenti/banco.py, ha la sessione ordina, con --ordina: i tempi dei riordini su una playlist aperta di cinquemila brani, e Mescola sulla playlist che suona con il seguente già preparato dalla dissolvenza.

## [1.105.1] - 2026-10-20

- Correzione, la riga In riproduzione, che la console scrive a ogni brano che parte, chiama la lista come Dove sono: Preferiti e Risultati, invece di playlist Preferiti e cartella Risultati, come ha deciso Gabriele il 20 ottobre 2026 con il punto b della tappa 14. Con lo stesso nome cambiano anche i file aperti da Windows, che erano cartella file aperti, e le unità, che erano per esempio cartella E:\ e ora sono unità E:. Le cartelle e le unità suonate con tutto ciò che hanno sotto, invece, non dicono con le sottocartelle, come fa Dove sono: nella riga di avvio Gabriele l'ha lasciato fuori, perché allungherebbe ogni riga. Il resto della riga resta com'era: il percorso intero del file, il posto nella lista, il nome soltanto con un brano solo, la selezione e il sottobrano.
- Le prove della riga di avvio: i Preferiti, i Risultati, anche quelli di una ricerca di prima, e le altre liste; quella delle cartelle suonate con le sottocartelle controlla la riga fino in fondo, che finisce con il nome della cartella, senza con le sottocartelle.

## [1.105.0] - 2026-10-20

Il punto b della tappa 14 del piano, deciso da Gabriele il 20 ottobre 2026: il tasto che dice a che punto si è, tolto da F9 nella 1.12.0, torna sull'apostrofo. Per il suo suono serve GBUtils V208.

- Novità, Dove sono: l'apostrofo scrive nella console, con un suono suo, una riga con il tempo, il brano e la lista di ciò che suona, in quest'ordine, per esempio 1:23 di 4:56, mancano 3:33, Caruso.mp3, 3 di 12, playlist Dalla, in pausa. Il tempo è il trascorso, la durata e il mancante; con la durata che non si sa, il trascorso e la durata non si sa; con il lettore non ancora pronto, il tempo non si sa ancora, con la durata se MeTeOra la conosce. Il brano è il nome del file. Il posto nella lista si conta come nella plancia: con un filtro fra i brani che lo passano, e la riga dice col filtro; senza, fra tutti i brani, saltati compresi; un brano che il filtro arrivato dopo lascia fuori dice fuori dal filtro, 15 di 120 in tutto. La lista ha il nome della plancia: playlist, Preferiti, Risultati, selezione, cartella o unità, con le sottocartelle quando suona tutta, o file aperto. In fondo, solo quando ci sono: in pausa; il sottobrano dei SID e delle console, o il capitolo, con il titolo; la ripetizione, la riproduzione casuale, il timer, il loop A-B e il muto; la velocità e il tono diversi dal normale, come velocità 1.25 e tono più 2 semitoni. La riga si riscrive a ogni pressione e va anche alla sintesi e al braille scelti per sottotitoli e karaoke, senza l'ora; anche sulla barra la riga nuova prende subito il posto di quella di prima ancora da leggere, mentre i sottotitoli in fila restano, e la voce lascia quello che sta dicendo per dire la riga nuova, così con la voce di Windows, che da sola non interrompe, più pressioni ravvicinate non si accodano; i sottotitoli e il karaoke invece non interrompono la voce. Il fuoco resta dov'è, anche nella finestra del video. Se non suona niente, la frase e il suono di F8, Non sta suonando niente, e la frase va anche alla sintesi e al braille, come la riga. Maiuscolo con l'apostrofo resta senza comando.
- Un suono nuovo nella collezione di GBUtils V208, fatto da ClaudIA su richiesta di Gabriele: meteora_dove_sono, sinusoide, una scivolata che scende dal la 5 al mi 5 da sinistra e una che risale fino al do diesis 6 verso il centro, come una voce che chiede dove sono, poi un'eco più piana a destra. Non è a onda quadra e non suona uguale a nessun altro suono di MeTeOra.
- La guida rapida di F12, il cruscotto e il manuale parlano dell'apostrofo, con un capitolo suo, Dove sono, nella riproduzione; gli esempi del tasto senza comando usano la o accentata. Le statistiche danno un nome al comando e al suo suono.
- Il banco del collaudo, strumenti/banco.py, ha una sessione per Dove sono, che preme l'apostrofo vero della tastiera italiana, e l'opzione --solo per lanciare una sessione da sola. La sintesi dei sottotitoli, nel banco, annota soltanto, anche i testi che interrompono la voce: quella vera, anche dal desktop nascosto, parlerebbe con NVDA. La pipe dell'istanza unica del banco ha il numero del processo, così due banchi lanciati insieme non si mandano i file l'uno all'altro. La sessione di Dove sono riporta al normale ripetizione, riproduzione casuale, velocità, tono e sintesi, così l'esito non dipende dai dati della macchina.

## [1.104.2] - 2026-10-20

- Correzione, la stessa cartella scritta con maiuscole diverse, come E:\git\mine ed E:\git\Mine, è una cartella sola, come per Windows. Prima MeTeOra ne faceva due liste: suonando una cartella da un percorso scritto in un modo e aprendola nella plancia, che usa le maiuscole vere del disco, F8 non ritrovava il brano che suonava e la plancia non lo diceva in riproduzione. L'ha trovato la suite delle prove sul PC gigante di Gabriele, dove la cartella dei progetti si chiama Mine.
- Correzione delle prove: quella di F8 sulle sottocartelle non conta più sulle maiuscole del percorso, e non lascia più leggere allo schedario i file finti, che la sonda di libmpv teneva aperti mentre la cartella si cancellava; una prova nuova suona una cartella scritta tutta in maiuscolo.

## [1.104.1] - 2026-10-20

Piccoli ritocchi decisi da Gabriele il 20 ottobre 2026, prima delle funzioni nuove della tappa 14 del piano.

- F11 dice 0.0% invece di 0% quando il totale è zero, come le statistiche.
- Il manuale dice che per ora MeTeOra parla solo italiano, e due limiti noti: un DSD256 con la velocità o il tono cambiati va a scatti, nel capitolo della velocità; un APE vecchio con un campo di testo che non è in UTF-8, per esempio con le lettere accentate nella codifica di Windows, perde tutti i tag, nel capitolo dei tag.
- strumenti/prepara_ambiente.py cerca 7-Zip prima di scaricare qualunque cosa e, se manca, dice come installarlo, invece di cadere con un FileNotFoundError dopo il download di libmpv (issue 23).
- strumenti/prepara_ambiente.py tiene libsidplayfp alla 2.16.1, quella che la cartella licenze nomina, installata dal suo pacchetto nell'archivio di MSYS2 anche al posto di una più nuova: una versione 3 non arriva più da sola. Se dopo l'installazione la versione è un'altra, sidshim non si compila.

## [1.104.0] - 2026-10-19

Dal collaudo delle statistiche fatto da ClaudIA sul PC di Gabriele il 19 ottobre 2026: una novità, la pulizia all'avvio, e le correzioni che il collaudo ha trovato, decise da Gabriele tutte insieme in questa versione. Per i due suoni della pulizia serve GBUtils V207.

- Novità, la pulizia all'avvio: a ogni avvio, dopo i suoni della partenza, MeTeOra controlla in un filo a parte che ci siano ancora i file che conosce, cioè quelli delle schede dello schedario, i brani di playlist e Preferiti, i marker, i punti da riprendere e lo storico delle statistiche, e toglie le voci dei file spariti. La console dice quante voci controlla, e alla fine quanti file sono spariti e da dove li ha tolti. Ogni cartella si legge una volta sola. Un'unità o una condivisione che non risponde, o che smette di rispondere a metà, si salta e le sue voci restano; una lettura di rete muta oltre 15 secondi si annulla, come nella ricerca. Il brano che suona non si tocca, e con un dialogo aperto le voci si tolgono quando si chiude. Una cartella che c'è ma non si legge, come una giunzione verso un disco staccato, resta senza controllo, e così un percorso scritto senza l'unità. Un file che durante la pulizia si rinomina con il nome di uno sparito, o si rimette in una playlist, non si tocca. I marker di un file sparito passano alla sua copia con lo stesso nome e la stessa durata, se lo schedario la conosce, come dopo aver spostato una cartella con Esplora risorse. Nello schedario di Gabriele mancavano 45564 file sui dischi e 2358 sull'Iliadbox, fra cui le cartelle di prova della 1.103.1, e c'erano 82 schede doppie di HVSC che differivano solo per le maiuscole: la prima pulizia le toglie, e la console le dice a parte, se nessuna playlist usa la scrittura sbagliata. Due suoni nuovi nella collezione di GBUtils V207: meteora_pulizia_avviata, due colpi di scopa di rumore azzurro verso destra, e meteora_pulizia_finita, tre note di seno che tornano al centro. La sezione La salute delle statistiche conta le pulizie e quello che hanno tolto.
- Rinomina file porta con sé anche il punto da riprendere e lo storico delle statistiche del file, che la pulizia altrimenti toglierebbe, e li scrive subito; e lo schedario trova la scheda del file anche quando le maiuscole sono scritte diverse.
- Un file aperto dalla riga di comando con il nome soltanto si ricorda con il percorso intero, come quelli che arrivano a un MeTeOra già aperto.
- Correzione, le statistiche si scrivono subito all'avvio, con la sessione aperta. Prima il primo salvataggio arrivava dopo un minuto, e una chiusura a forza nei primi sessanta secondi spariva, con il suo avvio e la chiusura non regolare: nel collaudo una sessione chiusa dopo 9 secondi non contava.
- Correzione, una chiusura dal Task Manager non è più un errore grave. faulthandler scrive nel file del crash anche le eccezioni di Windows che le librerie gestiscono da sé, come la 0x8001010d di COM e la 0xe24c4a02 di LuaJIT dentro libmpv, e alla riapertura MeTeOra chiedeva di mandare il resoconto a chi sviluppa. Ora è un crash solo un errore fatale vero, come una violazione di accesso o un Fatal Python error; e ogni minuto il file del crash si riassume nel registro degli errori e si svuota, così non cresce per tutta la sessione, tranne un errore fatale appena scritto, che aspetta il minuto dopo perché un crash in corso non si perda. Se il resoconto di un crash vero non si può spostare in Crash precedente.log, non si perde più.
- Correzione, lo schedario non tiene una durata troppo lunga per il peso di un file audio o video, cioè sotto 100 byte al secondo: nello schedario di Gabriele 17 file rovinati, da pochi KB, dicevano fino a 37 ore, sotto la soglia della settimana della 1.103.1, e gonfiavano la libreria di circa 143 ore. SID, MIDI, tracker e console, piccoli per natura, non si controllano così. La stessa regola vale per il record del brano più lungo ascoltato fino alla fine.
- Le statistiche si leggono meglio. Tutte le date dicono il giorno della settimana, come raccolte da lunedì 19 ottobre 2026. Le righe che elencano, come le ore, i giorni, le fasce, i mesi, le famiglie e i decenni, hanno solo le voci diverse da zero, e dei formati mai suonati resta il numero. Tasti premuti dice 254, cioè 855 per ogni ora, che prima sembrava un numero solo. Le percentuali sono tutte uguali, 0.0% anche con il totale a zero e 0.1% invece di 0.10%. Gli anni dei tag nel futuro, come il 2100 di un SID, non contano. L'istruzione della ricerca dice la riga che comincia con Le sezioni, invece della quarta, che lo era solo dopo un azzeramento.
- I file dei dati, MeTeOra - *.json, non stanno più nel repository: ogni macchina ha i suoi, e da qui parte da zero (Gabriele). pulisci_i_dati.py, accanto a meteora.py, si lancia una volta su ogni macchina prima di MeTeOra: chiede una S e cancella per sempre i dati vecchi, la cartella copie e i registri; poi si toglie dal progetto.
- Il banco del collaudo, strumenti/banco.py: MeTeOra vero su un desktop nascosto, con una copia dei dati, pilotato da una tastiera simulata dentro il processo, strumenti/tastiera_simulata.py, perché sul desktop nascosto SendInput non arriva.
- Correzione delle prove: quella del trascinamento non sapeva ancora che dalla 1.103.0 il trascinamento dice da dove arrivano i file; quella del crash vero usava ctypes.string_at(0), che ctypes trasforma in un OSError, e ora fa un crash vero.
- La cartella licenze dice la 1.104.0 e GBUtils V207, con il suo commit.

## [1.103.2] - 2026-10-17

- I cinque suoni delle statistiche ci sono, nella collezione di GBUtils V206, fatti da ClaudIA su richiesta di Gabriele: meteora_statistiche, cinque tocchi pentatonici che salgono come le colonne di un istogramma e un do più lungo, il totale; meteora_statistiche_azzerate, una scivolata che scende, i contatori che tornano indietro, un do grave, lo zero, e un sol breve, il conto che riparte; e la ricerca nel testo, meteora_statistiche_trovato, ripartito e non_trovato, di onda triangolare, cugina di quella dei marcatori, che è di seno. Nessuno suona uguale a un altro preset della collezione, e nessuno è a onda quadra. Per suonarli serve GBUtils aggiornato alla V206.
- La cartella licenze dice la 1.103.2 e GBUtils V206, con il suo commit.

## [1.103.1] - 2026-10-17

- Correzione, lo schedario non tiene più le durate da una settimana in su: nello schedario di Gabriele 1430 schede venivano da file di prova rovinati, in una cartella di backup sull'Iliadbox, e sette dicevano fino a 1.4 milioni di milioni di secondi, circa 44600 anni. Nella plancia quei file restano senza durata, e i totali delle cartelle e delle playlist non ne sono più gonfiati; le schede già salvate si rileggono quando servono. Era la pulizia a parte scelta da Gabriele con le statistiche, che già lasciano fuori quelle durate.

## [1.103.0] - 2026-10-17

Le statistiche, chieste da Gabriele: più dati ci sono, più è contento. La proposta, discussa il 17 ottobre 2026, ha fissato venti posti per le classifiche, lo storico di 50000 brani, le durate a parole e la ricerca con la barra rovesciata, come nella console.

- La voce Statistiche, nel primo livello della plancia prima di Impostazioni, e Maiuscolo con F7 da tutta la finestra aprono la finestra delle statistiche: un testo di sola lettura, con il fuoco sulla prima riga, e i pulsanti Azzera le statistiche e Chiudi, il predefinito. Esc e Chiudi chiudono sempre; Invio nel testo chiude finché non c'è una ricerca.
- Ventitré sezioni, un'informazione per riga: in breve, le sessioni, il tempo, il tempo per famiglia e per ognuno dei formati, come hai ascoltato, i brani, le classifiche di brani, autori, album, generi, decenni, cartelle e unità, il calendario con le serie di giorni e le 24 ore, i record, il movimento nel brano, i marker, playlist e Preferiti, la ricerca, file e tag, video e sottotitoli, plancia e tastiera con i tasti più premuti, console e aiuto, impostazioni, rete e MIDI, la salute, la libreria di adesso, le curiosità e tutti gli eventi, uno per riga.
- I conti arrivano da quattro strade: ogni effetto sonoro è un evento, contato anche con il volume degli effetti a zero; ogni tasto premuto nella finestra principale si conta per nome; un orologio di un secondo dà il tempo allo stato di prima, e un passo vale al più cinque secondi, così un PC sospeso non diventa ascolto; e i conti espliciti dove serve una quantità, come i marker tolti in blocco, i secondi saltati, i risultati della ricerca e i brani aggiunti.
- Un brano è finito quando arriva alla fine da solo, anche sfumando; lasciato quando lo cambi o lo fermi, e lasciato subito nei primi 10 secondi; un brano ancora in corso all'uscita ha una riga sua. X da capo non è un altro avvio.
- Autori, album, generi, anni, cartelle e unità non si salvano: si ricavano dallo storico dei brani e dai tag dello schedario. La libreria di adesso si conta a ogni apertura, in sottofondo, da una copia delle schede; le durate oltre una settimana restano fuori dai conti, e una riga dice quante sono: nello schedario di Gabriele ci sono file di prova rovinati che dicono migliaia di anni.
- Il file è MeTeOra - Statistiche.json, scritto ogni minuto in sottofondo e all'uscita, e copiato nella cartella copie come gli altri dati; un file che non si legge non si sovrascrive, e le statistiche nuove vanno nel .nuovo. Una sessione che non si è chiusa conta come chiusura non regolare.
- Azzera le statistiche chiede una conferma, con No predefinito; restano la data della prima raccolta e il numero degli azzeramenti.
- Cinque suoni nuovi, da creare nella collezione di GBUtils: meteora_statistiche, meteora_statistiche_azzerate, meteora_statistiche_trovato, meteora_statistiche_ripartito e meteora_statistiche_non_trovato.
- Il manuale ha il capitolo Le statistiche, e Maiuscolo con F7 nella guida rapida. Correzione del manuale: Maiuscolo con F9 e F12 non passano più a Windows da tempo; ora passa solo Maiuscolo con F4.

## [1.102.4] - 2026-10-06

- L'invito a offrire un caffè non compare più alla chiusura, dove usciva una volta su cinque: resta soltanto la voce Dona per questo progetto, nelle impostazioni, che lo apre sempre (Gabriele, 6 ottobre 2026, per tutti i suoi programmi con una finestra).

## [1.102.3] - 2026-10-06

- Correzione, con velocità o tono cambiati il passo ondeggiava (issue 20, segnalata da Andrea). Velocità e tono passavano per scaletempo2, l'algoritmo WSOLA di Chromium pensato per il parlato: tiene il seguito naturale del suono finché resta entro 20 ms dal punto giusto, poi salta, e a 1,05 la musica andava a velocità normale per circa 0,7 secondi e poi saltava di 35 ms; il tono, fatto da mpv con il ricampionamento e scaletempo2 alla velocità inversa, ondeggiava allo stesso modo. Due ascolti alla cieca di Gabriele, con le coppie di controllo sempre giudicate uguali: accorciare l'intervallo di ricerca di scaletempo2 suonava peggio, e contro filtri di natura diversa scaletempo2 non ha mai vinto, 0 a 3 contro rubberband e 0 a 2 contro atempo di FFmpeg, che però sotto il tempo 0,5, con velocità bassa e tono alto, sbaglia. Ora, quando velocità o tono sono cambiati, il filtro del tempo è rubberband con il motore R3, che fa anche il tono, senza il ricampionamento; a velocità e tono normali resta scaletempo2, che lì lascia l'audio identico all'originale. Lasciando il normale o tornandoci la catena dei filtri si riscrive, con un buco di qualche centesimo di secondo; fra due velocità o due toni diversi dal normale niente si riscrive, e il tono arriva a rubberband al volo. rubberband costa l'11-15% di un nucleo in stereo, solo mentre velocità o tono sono cambiati; aggiunge circa 40 ms di attacco morbido all'inizio di ogni brano e 50 di silenzio alla fine. Il timbro si sposta con il tono, come faceva il ricampionamento (formant=shifted): con le formanti conservate, come mpv lo avvia, un la puro alzato di un'ottava usciva quasi muto, e così la musica dei SID e dei chip.

## [1.102.2] - 2026-10-06

Dalla segnalazione di Andrea, che sentiva MeTeOra meno bello degli altri lettori (issue 22): tre novità e due correzioni, decise da Gabriele dopo le misure del 6 ottobre, tutte su file e senza suoni.

- Correzione, il ricampionamento: in WASAPI condiviso Windows accetta solo la frequenza del suo mixer, di solito 48 kHz, e mpv convertiva da sé la musica a 44,1 kHz con il suo convertitore predefinito, che toglieva gli acuti: -0,5 dB a 16 kHz, -2,9 a 18, -9 a 20, e da 48 a 44,1 ancora di più. Ora la conversione la fa soxr, già dentro libmpv, piatto fino a 21 kHz in tutte e due le direzioni, con distorsione e rumore a -148 dB e i ripiegamenti a -151, e un costo trascurabile. Chi ha la scheda alla frequenza dei file, come Gabriele a 44,1 kHz, non sentiva differenze, e non ne sente.
- Correzione, il volume di partenza è 100, il livello originale dei file, come gli altri lettori al cento per cento: 80, con la legge cubica di mpv, era -5,8 dB. Chi ha già un volume salvato lo tiene.
- Novità, il volume oltre 100 passa per un limitatore: prima amplificava e basta, e sui brani forti tosava i picchi, l'1,9% dei campioni in mediana a 127 e il 16% a 160, con la distorsione che ne viene. Ora mpv riceve al massimo 100, e il di più lo dà la catena dei filtri, seguito dal limitatore di FFmpeg a -1 dBFS; fino a 100 la catena resta identica all'originale. Su un brano già forte, a -9 LUFS, +12 dB di volume danno +2,5 dB veri e nessuna distorsione; un brano piano cresce di tutto il volume chiesto.
- Novità, le bande compensate: le bande dell'equalizzatore si sovrappongono, e tutte a +6 davano fino a +8,5 dB, tutte a +12 fino a +17,6. Ora i filtri si calcolano in modo che la curva intera, al centro di ogni banda, valga quanto la banda scritta: tutte a +6 danno +6, misurato con un impulso nella catena vera.
- Novità, il preamplificatore sul punto più alto della curva: prima il volume scendeva quanto la banda più alzata, e con più bande vicine alzate la curva lo superava fino a 5,6 dB. Ora il suono entra nell'equalizzatore abbassato quanto sale davvero la curva, calcolata con le formule di FFmpeg, che coincidono con la catena al centesimo di dB; e il preamplificatore sta nella catena, prima delle bande, invece che nel volume di mpv.
- Le misure hanno escluso altre cause: con le bande a 0 e la velocità a 1 l'audio esce identico campione per campione; a volume 100 la musica di Gabriele esce in mediana a -11,6 LUFS, più forte delle voci di Windows, a -19 e -20, e nessun filtro le toglie potenza.

## [1.99.0] - 2026-10-06

Pubblicata il 6 ottobre 2026, con l'installatore e lo zip: la seconda release, la prima che arriva agli utenti con l'aggiornamento automatico. VirusTotal ha analizzato l'installatore, scaricandolo dalla release: nessuno dei 68 antivirus lo segnala.

- vulkan-1.dll di scorta: libmpv la chiede per partire, e due dei primi tre utenti, con driver della scheda video che non la portano, si fermavano al messaggio dell'avvio. Ora MeTeOra ha con sé il caricatore ufficiale di Vulkan, dal runtime 1.4.363.0 di LunarG, e lo usa solo se Windows non ne ha uno suo: chi ha i driver giusti non cambia niente. Scelta di Gabriele, che il 4 ottobre aveva preferito il messaggio; licenza Apache 2.0 con parti MIT, nella cartella licenze.

## [1.98.1] - 2026-10-06

- Con il fuoco su un capitolo nella plancia, T, che mette un marker, faceva perdere il posto: rinfrescando i marker il ramo dei capitoli rinasceva e il fuoco finiva sul brano. Ora ritorna sul capitolo, come succede già per i marker. Lo ha trovato la revisione della 1.98.0; c'era dalla 1.93.0.

## [1.98.0] - 2026-10-06

- La plancia è un albero di Windows a selezione singola, come quello di Esplora risorse: con le frecce NVDA legge sempre la voce d'arrivo. Con la selezione multipla che wxWidgets simulava, ogni freccia mandava a NVDA anche un fuoco sulla voce di prima, e a volte NVDA leggeva quella; l'ha segnalato Andrea, il primo utente, e agganciando gli eventi di accessibilità succedeva in 8 pressioni su 9 (issue 19).
- La selezione multipla la tiene MeTeOra: Maiuscolo e Ctrl con le frecce, Ctrl con la barra spaziatrice e, per chi usa il mouse, il clic con Ctrl e con Maiuscolo. Le voci selezionate hanno lo sfondo del colore della selezione di Windows, più chiaro, e la console dice, in una riga che si riscrive, se la voce col fuoco è selezionata e quante lo sono, perché NVDA non lo dice da sé. Le frecce senza modificatori, il clic semplice e la ricerca per iniziale riportano la selezione alla sola voce col fuoco; il clic destro porta il fuoco sulla voce, come in Esplora risorse.
- Dalla revisione a più agenti, prima della pubblicazione: il clic destro, che nell'albero nativo non spostava più il fuoco e faceva agire il menu sulla voce sbagliata; l'ordine della selezione, calcolato a ogni lettura in una passata sola, anche su migliaia di voci; il rinfresco del ramo Playlist, che rimette la selezione intera; i colori leggibili a plancia senza fuoco; il nome della voce, senza conti e durate, nella riga della console.
- Una prova nuova si aggancia agli stessi eventi che riceve NVDA e controlla che le frecce, Maiuscolo e Ctrl con le frecce e gli spostamenti fatti da MeTeOra mandino il fuoco soltanto sulla voce d'arrivo.

## [1.97.10] - 2026-10-05

Pubblicata il 5 ottobre 2026: la prima release di MeTeOra, con l'installatore e lo zip. VirusTotal ha analizzato l'installatore, scaricandolo dalla release: nessun antivirus lo segnala.

La preparazione della prima release, dalla verifica a più agenti delle risorse del pacchetto e dei documenti: dieci correzioni.
- La cartella licenze dice la versione della release e GBUtils V198, con il commit esatto; si rifà prima di ogni release.
- La licenza di PortAudio, la libreria del suono degli effetti che sounddevice porta con sé, è nella cartella licenze, scaricata con il permesso di Gabriele.
- Il pacchetto non porta più due volte le librerie dei SID e della musica delle console: circa 5,6 MB in meno.
- Nel programma compilato, se mancano le librerie, il messaggio dice di reinstallare MeTeOra, e non di eseguire uno script che nel pacchetto non c'è.
- Un mpv-2.dll di un altro programma, nel PATH di Windows, non prende più il posto della libmpv di MeTeOra.
- Il manuale: la cartella _internal, con lib dentro, e dove sta il changelog nel programma compilato.
- Il manuale: X e Invio su un capitolo nella guida rapida, e le quattro eccezioni di Invio nella plancia.
- Il manuale: F2, nella guida rapida, scrive le novità delle versioni recenti.
- Il manuale: le lettere nella plancia e Maiuscolo con F12.
- Il README per chi scarica MeTeOra: installazione, requisiti, aggiornamenti e dati, il manuale online, e GBUtils per avviarlo dai sorgenti.

## [1.97.0] - 2026-10-05

- L'installatore, chiesto da Gabriele per la prima release: MeTeOra-Setup seguito dalla versione, fatto con Inno Setup 6 da setup_maker.py, accanto a MeTeOra.zip, che resta per l'aggiornamento automatico e come versione portatile. Installa per utente, senza amministratore, in AppData\Local\Programs\MeTeOra, perché MeTeOra scrive i dati accanto al programma e lì si aggiorna; mette MeTeOra nel menu Start, e sul desktop se lo chiedi.
- La disinstallazione toglie anche le associazioni dei formati di quell'installazione, e alla fine chiede se cancellare i dati: playlist, Preferiti, impostazioni, marker e copie, scelta di Gabriele; con No restano.
- MeTeOra aperto tiene un mutex che installazione e disinstallazione riconoscono, e chiedono di chiuderlo. Dopo un aggiornamento automatico MeTeOra corregge da sé la versione che App installate mostra.
- Il manuale ha il capitolo Installare MeTeOra, con i due file della release, l'avviso di SmartScreen al primo avvio, che cosa serve e come si disinstalla.

## [1.96.11] - 2026-10-05

Le correzioni della revisione a più agenti delle versioni da 1.94.0 a 1.96.0, chiesta da Gabriele, dieci in tutto, e una trovata dalla suite.
- All'uscita MeTeOra poteva restare appeso, di rado: l'ascolto delle altre copie, chiudendosi, si svegliava con una connessione che a volte aspettava per sempre una risposta. Ora apre e chiude la pipe e basta, e una prova ricrea apposta il caso.
- Fra file che non si suonano, per esempio su una cartella di rete staccata, MeTeOra si ferma quando nessuno dei brani che l'avanzamento può suonare è partito, e lo dice: vale con la ripetizione della lista e anche con la riproduzione casuale, dove prima il giro poteva non finire.
- Con la riproduzione casuale una volta per brano e la ripetizione della lista, il mazzo rimescolato non fa tornare subito l'ultimo brano suonato, come nel modello a giro.
- Se la ripetizione della lista si spegne negli ultimi secondi di un mazzo, quando la dissolvenza ha già preparato il giro nuovo, il giro nuovo si annulla.
- La sfumatura del timer non si chiude più fra un brano e l'altro: il brano seguente parte già attenuato, e quello che stava per partire quando il timer ferma tutto non parte.
- Un brano scelto mentre il timer sfuma, con la dissolvenza accesa: quello vecchio esce dal volume a cui era arrivato, senza tornare di colpo forte.
- Un numero sotto zero nella domanda del timer non toglie più il timer: è un errore, e il timer resta com'era.
- Mentre la domanda di Maiuscolo con S è aperta, la sfumatura e il tempo del timer aspettano, e Esc dice il timer di adesso.
- Il manuale e la console dicono che il ReplayGain fa salire un file registrato piano solo fin dove il suo picco lo permette.
- Il manuale: con vol, il filtro delle impostazioni mostra anche Volume uniforme (ReplayGain).
- Il changelog: la 1.95.0 e la 1.96.0 sono i punti f e g della tappa 12.

## [1.96.0] - 2026-10-04

- Il volume uniforme, tappa 12 g del piano: la voce Volume uniforme (ReplayGain) delle impostazioni, spenta di partenza come deciso da Gabriele, porta allo stesso volume i file con i tag ReplayGain, per brano o per album. La legge libmpv, e vale subito, anche per il brano in corso.

## [1.95.0] - 2026-10-04

- Il timer di spegnimento, tappa 12 f del piano: Maiuscolo con S, il tasto scelto da Gabriele, chiede fra quanti minuti fermare la riproduzione, da 1 a 600, oppure f per la fine del brano, o 0 per togliere il timer. Allo scadere la musica sfuma per venti secondi, sempre, anche con la dissolvenza spenta, e si ferma; alla fine del brano il seguente non parte. Tre suoni nuovi dalla collezione di GBUtils (V198).
- Mentre sfuma, V ferma subito, un brano scelto da chi ascolta torna al volume pieno, e Maiuscolo con S con 0 toglie la sfumatura. Il motore ha un'attenuazione sopra il volume e le dissolvenze, che non tocca il volume scelto.

## [1.94.0] - 2026-10-04

- La ripetizione, tappa 12 e del piano: Maiuscolo con V, il tasto scelto da Gabriele, la cambia a giro, del brano, della lista, spenta, ognuna con il suo suono dalla collezione di GBUtils (V198). Del brano, quello che finisce da solo ricomincia; della lista, dove non c'è altro si riparte dal primo, nella plancia dalla prima voce suonabile che si vede. Con la riproduzione casuale una volta per brano, la ripetizione della lista rimescola il mazzo finito. La ripetizione si ricorda alla riapertura ed è anche una voce delle impostazioni.
- Un brano che non si suona non si ripete, e fra file che non si suonano dal primo si riparte una volta sola: nessun giro senza fine.

## [1.93.0] - 2026-10-04

- I capitoli, tappa 12 e del piano: negli audiolibri e nei film che ne hanno, la virgola va al capitolo precedente e il punto al successivo, i tasti scelti da Gabriele, e la console dice quale, con il titolo e il tempo; la virgola, oltre i primi tre secondi di un capitolo, torna al suo inizio. Due suoni nuovi dalla collezione di GBUtils (V198).
- Nella plancia un file con i capitoli è un ramo, con dentro i capitoli e poi i marker: X, Invio o il menu su un capitolo suonano il file da lì. I capitoli si leggono dai tag di M4B, M4A, MP4 e MP3; quelli degli MKV li vede libmpv mentre il file suona. Lo schedario rilegge da sé le schede vecchie dei file lunghi di quei formati.

## [1.92.0] - 2026-10-04

- I file lunghi riprendono dal punto lasciato, tappa 12 e del piano: audiolibri, podcast e film più lunghi di dieci minuti, il limite scelto da Gabriele, ricordano dove li hai lasciati, e quando li suoni di nuovo riprendono da lì; la console lo dice, e X li fa ripartire da capo. Il limite è la voce Punto lasciato dei file lunghi delle impostazioni, e 0 spegne la ripresa. I punti stanno in MeTeOra - Posizioni.json, fino a mille, e entrano nelle copie dei dati.
- MeTeOra suona anche i file M4B, il formato degli audiolibri.

## [1.91.0] - 2026-10-04

- Aprire i file da Windows, tappa 12 d del piano: MeTeOra suona i file e le cartelle passati sulla riga di comando, aperti da Esplora risorse o trascinati sulla finestra; più file insieme suonano come una lista che non entra fra le playlist, una cartella sola con tutte le sue sottocartelle.
- MeTeOra resta uno solo: se è già aperto, la copia nuova gli passa i file, attraverso una pipe di Windows per l'utente, e si chiude; quello aperto torna in primo piano. I file aperti insieme da Esplora risorse arrivano tutti e fanno una lista sola.
- La voce Associazioni dei formati delle impostazioni, dal programma compilato: registra MeTeOra in Apri con per tutti i formati che suona e apre la pagina delle app predefinite di Windows, dove lo si sceglie come predefinito; oppure lo toglie, cancellando solo ciò che aveva scritto. Solo per l'utente, senza diritti di amministratore.

## [1.90.0] - 2026-10-04

- Le copie dei dati, tappa 12 c del piano: a ogni avvio, prima di leggerli, MeTeOra mette nella cartella copie, accanto ai dati, la versione di adesso delle playlist, dei marker e delle impostazioni, se è cambiata; restano le ultime tre, e il manuale spiega come tornare a una di loro. Una per sessione e non per salvataggio: le playlist si salvano a ogni modifica, e tre copie a pochi secondi l'una dall'altra non servirebbero.

## [1.89.0] - 2026-10-04

- Il registro degli errori, tappa 12 b del piano: ogni problema interno lascia il resoconto completo, con il punto del codice, nel file MeTeOra - Errori.log accanto ai dati; il file gira con una copia e i due insieme non superano i 10 MB (Gabriele). Dal programma compilato ci finisce anche quello che prima si perdeva, perché lì non c'è un terminale.
- I crash che Python non vede, come quelli dentro le librerie di Windows, lasciano la pila di tutti i fili in MeTeOra - Crash.log, con faulthandler. All'avvio dopo un crash la console lo dice, e il file diventa MeTeOra - Crash precedente.log, da mandare a chi sviluppa; un'uscita normale non lascia niente.

## [1.88.1] - 2026-10-04

- F2 scrive solo le novità delle versioni più recenti, a versioni intere, una cinquantina di righe: tutte erano troppe da scorrere (Gabriele). In fondo una riga dice dove leggere il changelog intero: il file CHANGELOG.md nella cartella di MeTeOra, e la sua pagina su GitHub.

## [1.88.0] - 2026-10-04

- La barra dei comandi per il mouse anche sopra il video, in finestra e a schermo intero, chiesta da Gabriele, con in più la linea del tempo, larga quasi quanto il video: un clic salta in quel punto, trascinando si salta dove si lascia, e la console lo dice come per W. Sotto, con il puntatore sulla linea, la barra scrive il tempo a cui si salterebbe.
- Prende il posto del cursore del tempo di prima, un cursore di Windows: al clic avanzava a passi invece di saltare, toglieva spazio al video quando compariva, e prendeva il fuoco quando lo si cliccava.
- Le due barre non si incontrano mai: ciascuna compare solo quando la sua finestra è attiva. La voce Barra dei comandi per il mouse delle impostazioni le spegne tutte e due.
- Dalla revisione prima della pubblicazione: un doppio clic sulla linea salta una volta sola; se il brano cambia mentre si trascina, il salto non si fa; dopo il rilascio la barra scrive il punto lasciato; chiudere MeTeOra mentre si trascina non fa più cadere wx; la barra del video guarda il mouse solo a video aperto.

## [1.87.0] - 2026-10-04

- La barra dei comandi per il mouse, chiesta da Gabriele per chi vede: compare in basso al centro quando il mouse si muove sopra MeTeOra, come nei lettori più diffusi, e sparisce dopo tre secondi di mouse fermo o quando il puntatore esce. Ha i pulsanti della riproduzione, del volume, della velocità e del tono, con i simboli dei font di Windows, e sotto scrive il nome e il tasto del pulsante indicato; ogni pulsante fa quello che fa il suo tasto.
- Senza nessun costo per chi usa lo screen reader: la barra è una finestrella che Windows non attiva mai e che non prende il fuoco, nemmeno al clic, non si raggiunge con Tab, non usa i suggerimenti di Windows, e nascosta per Windows non c'è. La voce Barra dei comandi per il mouse delle impostazioni, accesa di partenza, la spegne del tutto.
- Dalla revisione prima della pubblicazione: la barra compare solo con un movimento vero del mouse e mai sotto il puntatore, e un pulsante risponde solo al puntatore arrivato muovendosi, così il mouse che NVDA porta sul cruscotto non la fa comparire e il clic di NVDA non finisce su Muto; al ritorno in MeTeOra, dopo Alt con Tab o un dialogo, il mouse fermo non la mostra; sparisce con un menu aperto e mentre la finestra si sposta, e segue la finestra ridimensionata; la barra del titolo di MeTeOra non resta disegnata attiva; per NVDA si chiama Barra dei comandi per il mouse.

## [1.86.0] - 2026-10-04

- Maiuscolo con F12 spegne e riaccende i tasti rapidi a carattere, chiesto da Gabriele: spenti, lettere, cifre e segni, anche con il Maiuscolo, vanno alla plancia, che come ogni albero di Windows salta alla voce che comincia con ciò che scrivi, utile in un ramo grande. Restano i tasti funzione, Esc, Ctrl con la barra rovesciata, e nella plancia Backspace, Spazio, Invio e Canc.
- Due suoni nuovi per MeTeOra, presi dalla collezione di GBUtils (V197): due note che scendono quando i tasti si spengono, tre che salgono quando si riaccendono; la console lo dice, e il cruscotto, F7, dice per primo quando sono spenti. A ogni avvio sono accesi.
- Dalla revisione prima della pubblicazione: dopo la ricerca per iniziale la selezione segue il fuoco, come con le frecce, così Invio, Canc, X e gli altri agiscono sulla voce trovata e non su quella di prima; fuori dalla plancia, nella console, nel cruscotto o nel video, un carattere non fa suonare l'avviso di Windows ma dice, sempre sulla stessa riga, che i tasti rapidi sono spenti.

## [1.85.5] - 2026-10-04

- Collaudo di Gabriele: ogni cartella dell'Iliadbox diceva la rete non risponde, e Roma non si apriva, mentre Esplora risorse la leggeva. Bastava una sola cartella che non rispondesse, per esempio fra i backup, dove il Samba del router lascia appesa una lettura per una ventina di minuti ma risponde a tutte le altre, e i conti abbandonavano la condivisione intera fino ad Aggiorna, Video compreso. Ora la cartella che non risponde si salta da sola, senza rileggerla, e la condivisione si lascia perdere solo alla terza, come fa già la ricerca.
- Aprire un ramo di rete prova sempre a leggerlo, aspettando fino a otto secondi fra una voce e l'altra. Prima, se i conti avevano lasciato perdere la condivisione, il ramo non si apriva più; e una prova di tre secondi lo dava per spento, mentre la prima lettura dell'Iliadbox, misurata, ne chiede quasi tre. Se il ramo risponde, la condivisione torna viva, e i conti che aveva lasciato a metà si rifanno da soli.
- Le etichette dei conti incompleti dicono che è una cartella di rete a non rispondere, non la rete: (conto incompleto: una cartella di rete non risponde), oppure almeno 1200 file: una cartella di rete non risponde. E il conto di una cartella che ne contiene uno incompleto ora si dice incompleto anche lui: prima sembrava esatto.
- Dalla revisione prima della pubblicazione: un conto ancora in corso quando una cartella, o la condivisione, torna viva si rifà, invece di restare incompleto fino ad Aggiorna; Aggiorna su Questa rete riprova davvero le cartelle di rete che non rispondevano, come diceva il manuale, e Aggiorna su un ramo, se fa tornare viva la condivisione, rifà anche i conti delle altre sue cartelle; una cartella di rete con il conto incompleto resta nella plancia, per poterla riaprire; un ramo di rete che sbaglia subito, per esempio con il router che si riavvia, resta da riaprire invece di perdere la freccia; e una cartella che torna a rispondere non conta più fra le tre che fanno lasciar perdere la condivisione.
- Dal secondo giro di revisione: anche i conti in sottofondo trattano un errore di rete immediato come una cartella che tace, invece di tenerla per vuota e nasconderla; gli errori che fanno riprovare sono solo quelli della rete, e la console dice il testo di Windows; una lettura riuscita della plancia vale anche per i conti, e vince su un'attesa del contatore che scade dopo; Aggiorna su un computer della rete fa tornare vive le sue condivisioni, Aggiorna su Questo PC rifà anche il conto in corso, e Aggiorna su Questa rete riconta le unità di rete aperte in Questo PC; il cestino rifà i conti che la condivisione tornata viva aveva lasciato a metà; F11 su una cartella di rete aspetta otto secondi, come la plancia.

## [1.85.2] - 2026-10-04

- La cartella licenze è completa: ci sono anche i file di licenza delle 87 librerie chiuse dentro libmpv-2.dll, da FFmpeg e x264 a FreeType e libjpeg, molte BSD o MIT, che chiedono di riportare la loro nota con il programma compilato; e i testi dei pacchetti winrt e del banco FluidR3 GM. LEGGIMI.txt ha una riga per ognuna, SORGENTI.txt il suo repository.
- Li scarica strumenti/scarica_licenze.py, con il permesso di Gabriele: segue le dipendenze di mpv negli script della build fissata di libmpv e prende i file di licenza dal repository ufficiale di ogni libreria. raccogli_licenze.py li legge, e si ferma se sono di un'altra build.

## [1.85.1] - 2026-10-04

- Se libmpv non si carica, MeTeOra non si ferma più su un errore di Python: la finestra MeTeOra non può partire dice il motivo. Il caso tipico è vulkan-1.dll, che libmpv chiede per il video e che installano i driver della scheda video: su una macchina virtuale o con driver vecchi può mancare, e la finestra dice di aggiornare i driver o di installare il Vulkan Runtime (Gabriele).

## [1.85.0] - 2026-10-04

- Licenze e crediti, per la prima release: MeTeOra è GPL-3.0-or-later, la GNU General Public License versione 3 o, a scelta, successiva, come la libmpv che porta con sé (Gabriele). F3 ora dice il copyright, la licenza, la garanzia assente e dove sono i testi delle licenze e i sorgenti, e nomina la licenza di ogni componente.
- La cartella licenze, accanto all'eseguibile insieme al file LICENSE: LEGGIMI.txt elenca ogni componente con la versione esatta e la licenza, SORGENTI.txt dice dove trovarne il codice sorgente esatto, e ci sono i testi delle licenze. La fa strumenti/raccogli_licenze.py, che controlla anche che le DLL di lib siano proprio quelle dei pacchetti che nomina.
- Fra le sintesi non ci sono più ZDSR, Dolphin, System Access e PC-Talker: le loro DLL sono proprietarie, senza un permesso di ridistribuirle, e restano fuori dal pacchetto; Dolphin e System Access, poi, le hanno solo a 32 bit, che MeTeOra non può caricare. Il braille arriva con NVDA e JAWS. Chi aveva scelto una di quelle sintesi torna all'automatica.
- Il pacchetto non porta più la DLL a 32 bit di NVDA, le varianti di PortAudio che MeTeOra non usa, né cinque pacchetti Python tirati dentro da import facoltativi o di prova: psutil, chardet, cryptography, setuptools e tomli.
- strumenti/prepara_ambiente.py scarica la build 20260928 di libmpv, controllando l'impronta dell'archivio, e non più l'ultima: gli avvisi delle licenze nominano i sorgenti esatti di quella build.
- Nuovo capitolo del manuale, Licenze e crediti.

## [1.84.0] - 2026-10-04

- L'aggiornamento automatico, condizione di Gabriele per il primo rilascio: a ogni avvio del programma compilato MeTeOra controlla in sottofondo su GitHub se c'è una versione nuova, con l'auto updater di GBUtils, come Dadillo, Tornello e Terminal Beast. Dai sorgenti non controlla.
- Se c'è, si apre la finestra Aggiornamento di MeTeOra, con il fuoco sul testo: la versione nuova, quella che hai e le novità di tutte le versioni dalla tua alla nuova, prese da questo changelog, così chi ne salta qualcuna le legge tutte; senza il changelog valgono le note della release.
- Aggiorna adesso scarica la versione nuova, con l'avanzamento nella console, poi chiude MeTeOra salvando tutto, senza l'invito a offrire un caffè, e lo riapre aggiornato. Non adesso, Esc, Invio nel testo o due minuti senza risposta lo rimandano al prossimo avvio.
- Al primo avvio dopo un aggiornamento la console dice da quale versione a quale, e che F2 scrive le novità.
- zip_maker.py prepara l'archivio della release che l'aggiornamento scarica, senza i file dei dati, le console salvate, FluidSynth e i banchi dei MIDI.

## [1.83.3] - 2026-10-04

- Prova con file veri, scaricati dall'archivio dei campioni di FFmpeg: APE, TAK, Musepack SV7 e SV8, Speex, DSF e DFF si suonano, saltano e arrivano in fondo senza errori.
- La durata dei Musepack SV8 e dei DSF ora viene da mutagen: libmpv la stimava, più corta fino a un secondo e mezzo nei Musepack, e con la dissolvenza la fine del brano si perdeva; più lunga nei DSF, quanto pesano i loro tag.
- I tag dei TAK si leggono e si scrivono anche dalla finestra dei tag, e quelli dei DSF e DFF, che nessuno leggeva, anche nello schedario, quindi nel filtro e nella ricerca. Dei Speex si legge l'autore che speexenc scrive in AUTHOR.
- La voce di Windows, il ripiego senza screen reader, non si apriva sul PC di Gabriele: accessible_output2 legge l'elenco delle voci all'apertura, e l'elenco falliva. Ora la apre MeTeOra.
- La ricetta di PyInstaller, MeTeOra.spec, per il pacchetto a cartella della tappa 11: compilato, parte, apre la finestra e si chiude pulito; da congelati funzionano libmpv, i SID, il riconoscimento dei caratteri, il karaoke e la sintesi.

## [1.83.2] - 2026-10-04

- F10 lavora a fette come Maiuscolo con F10, chiesto da Gabriele: su un ramo con decine di migliaia di cartelle la finestra risponde durante l'apertura, e un tasto qualsiasi la ferma.
- Il suono d'inizio delle due aperture suona solo se l'apertura dura più di quattro decimi di secondo, e quello della fine aspetta che finisca: quasi sempre l'apertura è istantanea, e i due suoni si sarebbero sovrapposti (Gabriele).

## [1.83.1] - 2026-10-04

- Collaudo di Gabriele: Maiuscolo con F10 faceva partire una cacofonia di suoni e fermava MeTeOra, che andava chiuso a forza. Riprodotto con una copia dei suoi dati: ogni cartella vuota o illeggibile aperta suonava il suo suono, decine in pochi secondi; e i dischi interi caricavano decine di migliaia di cartelle, mentre ogni rinfresco della plancia risommava le durate di tutti i file di un disco per ogni cartella aperta, e la finestra restava ferma oltre un minuto.
- Maiuscolo con F10 ora lascia chiuso Questo PC, come Questa rete: Gabriele ci rinuncia. Apre i Preferiti, i Risultati e le playlist, fino a duemila rami e diecimila voci.
- Le aperture in blocco, anche F10 su una cartella, non suonano piu' una per una le cartelle vuote e quelle che non si leggono: alla fine la console dice quante erano.
- La plancia molto aperta non ferma piu' la finestra: i totali delle cartelle si sommano una volta e poi li aggiornano solo le durate nuove; i rinfreschi chiesti dal contatore e dallo schedario si accorpano, e fra uno e l'altro passa tre volte la durata dell'ultimo; si rifanno solo le etichette dei file con una scheda nuova; e mentre la finestra rinfresca, il contatore e lo schedario aspettano, perche' con il lucchetto di Python conteso lo stesso lavoro andava venti volte piu' piano. Sul banco, con i dati di Gabriele, la pausa piu' lunga e' scesa da oltre sessanta secondi a meno di uno e mezzo.
- I messaggi load_mid e load_pat che si vedevano nel prompt vengono dalla sonda che legge con libmpv le durate dei MIDI che FluidSynth non misura: sono innocui.

## [1.83.0] - 2026-10-04

- La barra braille a blocchi, tappa 10 punto g, chiesta da Gabriele per chi ha una barra corta: la voce Celle della barra braille divide sottotitoli e karaoke in blocchi lunghi al più quanto la barra, spezzati fra le parole, e i blocchi si mostrano uno dopo l'altro. Ognuno resta per la sua parte del tempo che resta al testo, in proporzione alla lunghezza, e mai meno della voce Tempo minimo di lettura in braille, di partenza 2000 millesimi; i testi che arrivano prima aspettano in fila, che si smaltisce nei silenzi o in pausa. Alla sintesi il testo arriva subito e intero. Con 0 celle, il valore di partenza, il testo resta intero, ma il tempo minimo vale anche per lui.
- La revisione prima della pubblicazione ha trovato otto difetti, corretti: un testo nuovo aspettava anche la parte di tempo del blocco mostrato, e un cartello lungo sovrapposto ai dialoghi fermava la barra per mezzo minuto, ora aspetta solo il minimo e il tempo di un testo vale al più quindici secondi; la fila non si svuotava ai salti, allo stop, ai brani nuovi, al cambio di traccia e di impostazioni; le passate degli impressi di un video potevano finire sul video caricato dopo; le righe del karaoke fatte di soli segni, come =====, si leggevano; il manuale prometteva la riga ridetta cambiando l'anticipo, e consigliava male il timeout di NVDA; e ora dice che ogni carattere conta una cella, come nel braille a otto punti.

## [1.82.0] - 2026-10-04

- Il testo del karaoke, tappa 10 punto e: i MIDI, con i kar, anche quelli che si chiamano mid, e il testo cantato, i file LRC accanto al brano o al video, anche con i tempi per parola, e i testi sincronizzati SYLT nei tag. Maiuscolo con F2 lo accende e lo spegne come i sottotitoli, e con i sottotitoli letti accesi arriva da solo; dopo un salto arriva subito la riga in corso.
- Tre voci nuove nelle impostazioni, con le decisioni di Gabriele: Testo del karaoke, per riga o per strofa dove il file le segna; Anticipo del karaoke, in millesimi, di partenza 0; Dove vanno sottotitoli e karaoke, alla sintesi e al braille, solo alla sintesi o solo al braille, che vale anche per i sottotitoli dei video. La voce Sintesi dei sottotitoli ora si chiama Sintesi di sottotitoli e karaoke.
- Sul banco dei 127 kar e dei 946 mid e midi di Gabriele: tutti i kar e 333 fra mid e midi hanno il testo, 26428 righe in tutto. Nei kar italiani vince il testo con le barre, perché il testo cantato degli stessi file spesso non va mai a capo o porta gli accordi; dove invece gli eventi di testo hanno solo gli accordi, vince il testo cantato. Il testo di 67 kar è nella codifica di Windows, di 59 senza accenti, e di uno, Sauver l'Amour di Balavoine, in quella di DOS, dove la a accentata diventava i puntini.
- Due sottotitoli uguali di fila, come un ritornello ripetuto o due No di seguito in un film, ora si dicono tutti e due: libmpv non li segnalava.
- Con NVDA, la sintesi dei sottotitoli buttava via l'uscita e la riapriva a ogni sottotitolo, perché accessible_output2 solleva un errore dopo aver detto il testo: ora voce e braille si chiamano uno per uno.
- libmpv non carica più da sé i file LRC accanto ai brani: li legge MeTeOra, con le strofe e senza i tempi per parola. Il testo arriva anche sui MIDI resi da FluidSynth, sui SID e sulla musica delle console, che libmpv apre come WAV: anche il testo veniva letto come WAV, e rifiutato.
- Il braille arriva con NVDA, JAWS e System Access; scegliendo il braille con un'altra sintesi, la console lo dice.
- La revisione prima della pubblicazione ha trovato 19 difetti, corretti. Fra gli altri: tre kar con gli accordi al posto del testo; dodici karaoke chiamati mid senza testo; gli apostrofi curvi che facevano scegliere la codifica di DOS; le righe lunghe tagliate a metà parola; la ripetizione dei sottotitoli uguali, che faceva dire 44 volte un cartello animato dei sottotitoli ASS, ora vale solo fra sottotitoli distanti almeno mezzo secondo; i LRC accanto ai video non più letti; le tracce del karaoke doppie ricaricando un brano o cambiando due volte un'impostazione; gli impressi scelti su un video che fermavano il karaoke.

## [1.81.0] - 2026-10-04

- Il filtro delle voci nella finestra delle impostazioni, chiesto da Gabriele: un campo da una riga subito prima della lista, che si raggiunge con Maiuscolo con Tab. Mentre si scrive restano solo le voci il cui nome contiene il testo, senza badare a maiuscole e accenti, come il filtro della plancia; Invio nel filtro torna alla lista, con la selezione sull'ultima voce scelta se è fra quelle mostrate, anche dopo un errore di battitura che l'aveva nascosta. Senza voci, una riga dice che nessuna contiene quel testo.
- La revisione prima della pubblicazione ha trovato tre difetti, corretti: il campo del filtro, creato fra le istruzioni e la lista, toglieva alla lista il nome che NVDA legge; un errore di battitura nel filtro faceva perdere la voce selezionata; l'intestazione del collaudo diceva ancora 1.80.0.

## [1.80.0] - 2026-10-04

- I sottotitoli fatti di immagini si leggono, con il riconoscimento dei caratteri di Windows, nella lingua della traccia o in italiano. Le tracce dei DVD e dei Blu-ray, VobSub e PGS, scelte con Maiuscolo con F2: a ogni sottotitolo nuovo MeTeOra lo fotografa e lo legge: a video spento il fotogramma si annerisce e basta una foto, a video acceso ne servono due, con e senza sottotitolo, e si legge la differenza; sul banco, 20 sottotitoli su 20 letti esatti, in 14 millesimi l'uno. Tappa 10, punto b.
- I sottotitoli impressi nel video, in fondo al giro di Maiuscolo con F2: letti al volo, guardando la fascia in basso un paio di volte al secondo, con circa mezzo secondo di ritardo; oppure, con la voce nuova Sottotitoli impressi delle impostazioni, letti prima con una passata a cinque volte la velocità normale, che salva accanto al video un file come Film.impressi.it.srt, usato come traccia le volte dopo, in tutti e due i modi. La scelta resta alla riapertura. Le scritte ferme, come i loghi, si scartano. Una passata che non trova niente non si rifà fino alla chiusura; se accanto al video non si può scrivere, non parte e lo dice; a passata finita, chi intanto ha scelto altro tiene la sua scelta. Sul banco, sottotitoli simulati letti esatti nove volte su dieci, gli altri con una lettera storta. Tappa 10, punto a, con le decisioni di Gabriele.
- Per leggere il fotogramma il video si decodifica anche spento, senza finestre, solo mentre serve.
- Due suoni originali per la passata, nella collezione di GBUtils V195. Servono i pacchetti winrt e Pillow, ora in requirements.txt; senza, la console dice che il riconoscimento non c'è.
- Prima della pubblicazione la revisione ha trovato e corretto 14 difetti. Fra gli altri: due letture insieme sullo stesso motore di Windows, che lo rifiuta, ora ogni filo ha il suo; il giro di Maiuscolo con F2 che si fermava sulla traccia della passata; la traccia a immagini scelta all'apertura che non si leggeva; le lingue di tre lettere come rum, il rumeno, prese per altre; un errore in una lettura, che ora si dice una volta sola e non la ferma.

## [1.79.0] - 2026-10-04

- Maiuscolo con F9 chiude tutta la plancia, e il fuoco va sulla voce di primo livello che conteneva quella su cui eri. Chiesto da Gabriele.
- Maiuscolo con F10 apre tutta la plancia, fino a duemila rami: i Preferiti, i Risultati, le playlist e Questo PC; Questa rete e le unità di rete restano chiuse. Lavora a pezzi, così la finestra risponde, con un suono all'inizio e uno alla fine, come la ricerca; un tasto qualsiasi la ferma. Maiuscolo con F10 non apre più il menu della voce, che si apre con Invio, il tasto Applicazioni e la barra spaziatrice. Chiesto da Gabriele.
- Tre suoni originali, nella collezione di GBUtils V194: la tripletta di F9 che continua a scendere, quella di F10 che continua a salire, e due note staccate per l'inizio dell'apertura.
- Il manuale spiega le differenze fra Backspace, Maiuscolo con Backspace, F9 e Maiuscolo con F9.

## [1.77.1] - 2026-10-04

- Il contatore delle cartelle legge la rete con la protezione della ricerca: quindici secondi al massimo senza che arrivi niente, poi la lettura si annulla in un filo a parte e il percorso si salta fino ad Aggiorna. Prima, aprendo la radice dell'Iliadbox in Questa rete, il contatore entrava nei backup, si piantava dopo circa 17 mila cartelle e restava fermo fino alla chiusura, e nessuna cartella, nemmeno dei dischi del PC, mostrava più i suoi conti. Un conto che ha saltato qualcosa lo dice l'etichetta, e la cartella non sparisce.
- Anche l'apertura di un ramo di rete legge con un tempo massimo, otto secondi, e un ramo di un percorso che si è già fermato dice subito che non risponde. Prima si controllava solo il primo livello di Questa rete, e una sottocartella poteva fermare la finestra.

## [1.77.0] - 2026-10-04

- F11 su un contenitore ne scrive i dettagli nella console, una informazione per riga, con un suono nuovo. Su una cartella: i file da suonare e quanto occupano, i tipi, la durata, il più lungo e il più corto, le sottocartelle dirette e in tutto, tutti i file con la dimensione, le date, il file cambiato per ultimo, gli attributi. Su un'unità prima lo spazio: capacità, libero e occupato con la percentuale, nome del volume, tipo e file system. Su Questo PC lo spazio di ogni unità e in tutto. Su una playlist, i Preferiti, i Risultati e i loro rami: brani, spazio sul disco, tipi, durata, saltati, mancanti sul disco, il filtro; sul ramo Playlist una riga per playlist. I conti si fanno in sottofondo, e un altro F11 interrompe quello di prima. Nei menu dei contenitori c'è anche la voce Leggi i dettagli. Chiesto da Gabriele.
- Dopo un file o una cartella mandati nel cestino, i conti delle cartelle che li contenevano, e di quelle che le contengono, si rifanno: risalendo, le etichette dicono il vero. Una cartella toccata così non sparisce più quando resta senza niente da suonare: dice (vuota), o (niente da suonare) se ha file d'altro tipo. Chiesto da Gabriele.
- Il suono dei dettagli è quello delle statistiche di meditimer, firmato anche da MeTeOra nella collezione di GBUtils V193.
- La revisione prima della pubblicazione ha trovato undici difetti, corretti: fra gli altri, la cartella cestinata faceva perdere i conti a quella che la conteneva; la voce del menu lavorava sulla voce col fuoco invece che su quella del menu; una cartella illeggibile si diceva vuota; i dettagli in ritardo portavano via il fuoco; un conto del contatore fatto mentre una cartella cambiava restava vecchio.

## [1.76.0] - 2026-10-04

- Maiuscolo con Canc su una cartella vuota la manda nel cestino, dopo la domanda con No predefinito. Vuota vuol dire senza file nemmeno nelle sottocartelle, a parte quelli di servizio come desktop.ini e Thumbs.db; una cartella con dei file, anche che MeTeOra non suona, resta, e la console lo dice. Le unità e i percorsi di Questa rete non si toccano. Chiesto da Gabriele.
- In rete e sulle chiavette Windows non ha il cestino, e Maiuscolo con Canc cancellava per sempre dicendo che il file era nel cestino: ora la domanda dice Cancellare per sempre, e la console che il file è cancellato per sempre, anche con più file selezionati.

## [1.75.0] - 2026-10-04

- All'uscita, una volta su cinque, per ultimo, l'invito a offrire un caffè, come in Tornello: il testo di Donazione di GBUtils, con il suo suono, e i pulsanti Dona con PayPal, che apre PayPal nel browser, e Chiudi, il predefinito; Invio nel testo ed Esc chiudono. Un guasto dell'invito non impedisce l'uscita. Chiesto da Gabriele.
- Nelle impostazioni, l'ultima voce Dona per questo progetto apre l'invito sempre; con Dona con PayPal la console ringrazia.
- Il suono dell'invito è quello di Tornello e Terminal Beast, e nella collezione di GBUtils V192 lo firma anche MeTeOra.

## [1.74.0] - 2026-10-04

- Con la riproduzione casuale accesa B sceglie a caso, con lo stesso modello e lo stesso mazzo del passaggio automatico, e Z torna ai brani suonati prima, uno alla volta, come in Winamp. Dopo Z, B e la fine di un brano ripercorrono in avanti la stessa strada prima di scegliere di nuovo a caso; un brano scelto con X, N, J, K o le cifre va in fondo alla strada. Al primo brano della strada Z lo dice, e con il mazzo finito B lo dice e ricomincia il giro. Chiesto da Gabriele, che prima aveva voluto il caso solo a fine brano.

## [1.73.0] - 2026-10-04

- Ctrl con la barra rovesciata cerca anche in rete, per ultima, dopo le playlist e i dischi del PC: nelle unità di rete con la lettera e nei percorsi aggiunti a mano in Questa rete, senza cercare due volte la stessa cartella. Le condivisioni intere salvate in Windows no: si cercano con la barra rovesciata sul loro ramo. Chiesto da Gabriele, che ha scelto così dopo il banco sul router.
- In rete una cartella ha quindici secondi per far arrivare qualcosa, anche con la barra rovesciata su un ramo di rete: una cartella grande che arriva a pezzi non scade. Una lettura rimasta appesa si annulla, con la funzione di Windows fatta apposta, e la cartella si salta; se tace il percorso stesso, o tacciono tre sue cartelle, o il server risponde subito con un errore, si salta tutto il percorso. Alla fine la console dice quali percorsi e quante cartelle non hanno risposto, e lo schedario non legge i file dei percorsi muti, che lo terrebbero fermo. Ferma la ricerca vale subito anche mentre la rete tace. Il banco sul disco dell'Iliadbox, percorso tutto in rete: mille cartelle al secondo, ma dopo circa 17 mila il Samba lascia appesa una lettura per una ventina di minuti, e l'annullamento stesso resta fermo, quindi parte in un filo a parte.
- Nei Risultati, una condivisione di rete salvata in Windows prende il nome che ha in Questa rete.
- La barra rovesciata su Questa rete non cerca due volte la stessa cartella, nemmeno scritta con maiuscole diverse o dentro un altro percorso. Le unità di rete con la lettera si trovano nel filo della ricerca, senza chiedere il nome del volume, che su un server fermo farebbe aspettare l'interfaccia.

## [1.72.0] - 2026-10-04

- Il manuale è in HTML, manuale.html, e si naviga per titoli: un capitolo per argomento, come la finestra, i Preferiti, le playlist, Questo PC, la rete, la ricerca e il filtro, la riproduzione, i marker, i tag, il video, il Commodore 64, l'Amiga, la musica delle console, i MIDI e le impostazioni, ognuno con il concetto, i tasti e degli esempi. Chiesto da Gabriele.
- Il primo capitolo è la guida rapida: tutti i tasti divisi per aree, una riga per tasto con una spiegazione breve; poi i comandi della ricerca e del filtro, con quelli della ricerca nella console e nei marcatori; poi i codici RGB dei colori delle impostazioni.
- F1 apre il manuale nel browser predefinito, e la console lo dice; se il file manca o non si apre, lo dice con il suono dell'errore. Prima lo scriveva nella console.
- F12 scrive nella console la guida rapida, una riga per titolo e per voce, e ci porta il fuoco sulla prima riga: un tasto che non ricordi si trova scorrendo. Prima scriveva solo la sezione I tasti.
- Il cruscotto segue i menu veri: l'unità e la cartella hanno anche Riproduci, Aggiungi alla playlist e Aggiorna; il brano Togli dalla playlist, Aggiungi ai preferiti e Manda nel cestino; il file Aggiungi ai preferiti e Manda nel cestino; il sottobrano Aggiungi ai preferiti; un ramo dei Risultati Salva come playlist; le playlist e i Preferiti Togli il filtro, quando c'è. Leggi i tag e Tag valgono solo per i formati che li hanno.
- Il cruscotto chiama i tasti come il manuale, Inizio invece di Home e Maiuscolo con M invece di Maiuscolo+M; dice che F8 porta anche il fuoco, che X fa ripartire da capo il brano che suona già, che la barra rovesciata da Apri file e Impostazioni cerca in tutto MeTeOra e Nuova ricerca dei Risultati pure; con il fuoco spostato da Ctrl elenca tutti i comandi che agiscono sulla voce selezionata e quelli che partono dalla voce col fuoco.
- Le prove automatiche non aprono mai il browser: il comando che apre i file è sostituito per tutte.

## [1.71.0] - 2026-10-03

- La barra rovesciata cerca nel ramo della plancia in cui sei, sottocartelle comprese: una cartella, un'unità, una playlist, i Preferiti o i Risultati; su Questo PC tutti i dischi, sul ramo Playlist tutte le playlist, su Questa rete i suoi percorsi. Così cercare in una cartella, per esempio nei giochi Amiga, è molto più veloce. Ctrl con la barra rovesciata cerca in tutto MeTeOra, come prima la barra da sola. Chiesto da Gabriele.

## [1.70.0] - 2026-10-03

- I tag dei WAV comprendono il blocco INFO, quello di Esplora risorse: MeTeOra lo legge, con i tag comuni presi da lì quando ID3 non li ha, e scrive titolo, artista, album, anno, genere, commento e traccia sia in ID3 sia nel blocco INFO; gli altri campi, come Copyright e Programma, si leggono e si modificano nel blocco INFO. Il filtro e la ricerca li trovano. Un WAV con la struttura irregolare, come una registrazione interrotta, non si tocca, e la console lo dice. Chiesto da Gabriele.

## [1.69.0] - 2026-10-03

- F11 scrive nella console i tag del brano o del file selezionato: i dieci comuni, anche vuoti, e gli altri che il file ha. C'è anche la voce Leggi i tag nel menu (tappa 10, chiesto da Gabriele).
- Il sottomenu Tag del menu, o Maiuscolo con F11, modifica i tag uno alla volta: Invio su un tag chiede il valore nuovo e lo scrive nel file, un campo vuoto lo cancella. Con più file selezionati il valore va in tutti, e dove sono diversi la voce lo dice; svuotare un tag con valori diversi chiede conferma. Un tag con più valori resta diviso; i testi su più righe e le copertine si leggono soltanto. Vale per MP3, WAV, AIFF, TTA, FLAC, OGG, Opus, M4A, MP4, WMA, WMV, APE, WavPack e Musepack.
- Il filtro e la ricerca trovano anche i tag dei file WAV, AIFF, WMA e TTA.

## [1.67.4] - 2026-10-03

- Nel menu dei brani e dei file c'è Rinomina file: cambia il nome del file sul disco, e l'estensione resta. I sottotitoli accanto con lo stesso nome lo seguono, come la lista m3u della musica delle console; playlist, Preferiti, marker e durate passano al nome nuovo. Un brano che suona continua a suonare. Chiesto da Gabriele.
- La ricerca dei banchi dei MIDI propone solo i banchi General MIDI, con tutti i 128 strumenti e la batteria: i banchi di uno strumento solo, come i pianoforti o gli esempi di Csound, suonerebbero un MIDI con strumenti sbagliati o mancanti. Un banco scritto a mano che non è General MIDI si può usare lo stesso, e la console lo dice.
- La ricerca dei banchi salta la cartella dei file temporanei di Windows, dove c'erano i banchi finti delle prove automatiche di MeTeOra.
- Le dimensioni dei banchi sotto i 10 MB si scrivono con un decimale: prima un banco piccolo diceva 0 MB.
- Le prove automatiche cancellano le loro cartelle temporanee quando riescono.

## [1.66.36] - 2026-10-03

Le rifiniture di accessibilità della tappa 9, dopo una verifica dei requisiti del piano.

- Un tasto senza comando, come Maiuscolo+A o l'apostrofo, lo dice con un suono, e nella plancia il fuoco non salta più sulla voce che comincia con quella lettera.
- Esc in un campo, o No a una domanda, scrive cosa non è cambiato, con un suono nuovo dell'annullamento: prima molti comandi, come Rinomina, W, Maiuscolo con M, Q, E ed L, Apri file e la ricerca nella console, uscivano muti, e altri scrivevano senza suono.
- Le domande con Sì e No si chiudono con Esc, che vale No; le lettere S e N rispondono subito.
- Spazio e Applicazioni su un comando, come Nuova playlist, dicono che non ha un menu; Invio nella console senza una ricerca lo dice.
- La finestra del video non ruba più il fuoco a un campo o a una finestra aperta: aspetta che si chiudano. Alla riapertura di MeTeOra un video ripreso in pausa apre la sua finestra con X, e la plancia tiene il fuoco. Chiudendo il video, il fuoco torna dov'era solo se il video lo aveva.
- Esc nella finestra del video ha un suono e una riga; a schermo intero ha quelli di Maiuscolo con F5; il salto con la barra del tempo ha quelli di W.
- Il fuoco su un sottobrano o su un marker resta lì quando la plancia si rifà, per esempio dopo F4; durante una ricerca la voce Mostra altri risultati non sparisce più da sotto il fuoco.
- Un file delle impostazioni che non si legge non si sovrascrive più con i valori predefiniti: MeTeOra lo dice e salva accanto, con .nuovo. Se all'uscita qualcosa non si salva, lo dice una finestra prima di chiudere. Gli errori all'avvio hanno il loro suono.
- Due suoni non partono più nello stesso istante, per esempio l'avvio e la ripresa, o l'errore e la domanda che riapre il campo: il secondo aspetta il primo, e la domanda non suona più se intanto hai già chiuso il campo. Dopo un brano che non si suona, il seguente parte finito il suono dell'errore, e V intanto lo ferma.
- Suoni giusti: eliminare playlist con Canc, creare una playlist con dei brani, Aggiorna, F8, la fine dello scaricamento di FluidR3, la domanda prima di Rinomina, Apri file, Esporta e Importa marcatori.
- Frasi più chiare: niente punto interrogativo quando la durata non si sa, il singolare con un solo brano, secondo o risultato, il nome della voce senza conti in Backspace, F9, F10 e Aggiorna, "più e meno volume" nel cruscotto, la sintesi dei sottotitoli, il punto B del loop anche sullo stesso brano.
- Maiuscolo con M legge il passo come le impostazioni: fuori dai limiti va al limite, e lo dice.
- Il cruscotto dice quando il fuoco è su una voce diversa da quella su cui agiscono Canc, X, F4 e il menu, e su un percorso di rete aggiunto a mano dice come toglierlo; parla anche dei file delle console con più brani.
- F12 trova nella sezione dei tasti anche Canc sui percorsi di rete, X sui marker ed Esc nella finestra del video. F3 nomina FluidSynth, libgme e accessible_output2. Se il manuale o le novità non si leggono, F1, F2 e F12 lo dicono con il suono dell'errore.

## [1.66.0] - 2026-10-03

- MeTeOra suona la musica delle console con libgme: NES, Super Nintendo, Game Boy, Sega, ZX Spectrum, PC Engine, MSX e Atari. Come i SID, i brani di un file diventano sottobrani nella plancia, con il loro titolo quando il file lo dice; il filtro ha la famiglia k=chip, e r conta anche i loro sottobrani (tappa 8).
- Un brano delle console che gira in tondo sfuma alla durata scritta nel file, o dopo due giri del ritornello; un file m3u accanto, con lo stesso nome, ordina i brani, li nomina e ne dice le durate.

## [1.65.0] - 2026-10-03

- I MIDI suonano con FluidSynth e un banco di suoni General MIDI: ogni strumento ha il suo suono, invece di uno solo per tutti. La prima volta MeTeOra chiede se procedere, scarica FluidSynth, cerca nei dischi i banchi che hai già e te li propone; se non ce ne sono, propone di scaricare FluidR3 GM. Il banco si cambia nelle impostazioni, con la voce nuova Banco dei suoni MIDI. Chiesto da Gabriele (issue 16, tappa 8).
- I MIDI hanno nella plancia la durata giusta, letta dalla loro mappa dei tempi.
- MeTeOra riconosce tutti i moduli dei tracker che libopenmpt sa suonare, compresi i formati dell'Amiga come OKT, MED, SFX, STK, DIGI e Future Composer; anche il filtro k=tracker li conta tutti.

## [1.64.0] - 2026-10-03

- Questa rete, un ramo nuovo della plancia accanto a Questo PC: i percorsi di rete salvati in Windows, come il disco della iliadbox, ciascuno con il suo nome; i percorsi che aggiungi con il comando Aggiungi un percorso di rete, ricordati e da togliere con Canc; e il ramo Computer della rete, che cerca in disparte i computer della rete e le loro cartelle condivise. Le cartelle di rete si aprono e si suonano come quelle di Questo PC, e una cartella che non risponde non blocca più MeTeOra: dopo pochi secondi la console lo dice. Chiesto da Gabriele.

## [1.63.0] - 2026-10-03

- Il video, tappa 7. Maiuscolo con F1 accende e spegne il video: acceso, quando parte un brano con il video si apre la sua finestra, sopra MeTeOra e grande come lei, che chi guarda può spostare, ridimensionare e mettere a schermo intero; allo stop sparisce e MeTeOra torna davanti. Spento, dei video si sente solo l'audio, come finora. Nella finestra del video tutti i tasti di MeTeOra funzionano, ed Esc toglie lo schermo intero o nasconde la finestra per il brano in corso; per chi vede c'è una barra del tempo che compare con il mouse sul bordo inferiore.
- Maiuscolo con F2: i sottotitoli letti, a giro, spenti e poi le tracce. Vanno alla sintesi scelta nelle impostazioni, uno screen reader o la voce di Windows, e nella console, anche con il video spento; MeTeOra prende anche il file dei sottotitoli accanto al video.
- Maiuscolo con F3 sceglie a giro la traccia audio, Maiuscolo con F5 mette il video a schermo intero, Maiuscolo con F6 cambia a giro il rapporto dell'immagine. Apostrofo e ì, tenuti finora per la traccia audio, sono liberi.
- Tre voci nuove nelle impostazioni: Video, Sottotitoli letti e Sintesi dei sottotitoli. Video e sottotitoli si ricordano alla riapertura.
- I suoni del video sono originali, nella collezione di GBUtils V186. Deciso con Gabriele nel discorso sulla GUI del 3 ottobre 2026.

## [1.62.4] - 2026-10-02

- I brani Matroska audio (mka), AU e CAF, e i moduli dei tracker, nella plancia non avevano la durata: la libreria che legge le durate non li conosce. Ora la chiede a libmpv, muta, in disparte. Le schede già salvate senza durata si rileggono.
- Gli AAC grezzi, i file .aac senza contenitore, avevano una durata sbagliata, anche di molto: il formato non la scrive, e la si stimava dal bitrate. Ora la si conta, fotogramma per fotogramma, ed è esatta. Durante l'ascolto però mpv usa ancora la sua stima: la durata detta da W e il momento della dissolvenza su questi file possono sbagliare.
- Le due correzioni vengono dal collaudo sistematico dei formati della tappa 6: 19 estensioni, con i file di prova fatti al momento, ciascuna aperta, misurata, attraversata con un salto e portata alla fine.

## [1.62.2] - 2026-10-02

- Con la dissolvenza accesa, X da capo e i marker su un SID non lo rigenerano più dall'inizio: il SID che entra usa la musica già generata per quello che esce. Prima, un marker lontano dall'inizio faceva sfumare il brano verso qualche secondo di silenzio.

## [1.62.1] - 2026-10-02

- Fermato un SID, la musica già generata restava in memoria finché quel lettore non apriva un altro brano: per un SID lungo, decine di megabyte. Ora si libera anche allo stop. Il difetto era nato nella 1.62.0.

## [1.62.0] - 2026-10-02

- Dopo un salto in avanti in un SID appena partito, con E, W o i marker, la console dice quanto c'è da aspettare, per esempio Il SID si prepara fino a 2:48: circa 9 secondi. Un SID si genera dall'inizio, più in fretta del tempo reale ma non subito, e fino al punto d'arrivo prima c'era solo silenzio. La riga compare da un secondo e mezzo d'attesa in su; dopo una decina di secondi d'ascolto, di solito, tutto il brano è già pronto e i salti sono immediati.

## [1.61.1] - 2026-10-02

- I SID partono prima: dal tasto alla musica passavano circa 230 millesimi di secondo, quasi 400 per il primo SID dopo l'avvio; ora circa 80. MeTeOra non fa più analizzare a mpv i primi secondi del brano, che andavano generati prima di partire, e prepara il motore dei SID appena si apre. È il primo passo della tappa 5.

## [1.61.0] - 2026-10-02

- La riproduzione casuale ha tre modelli, da scegliere fra le impostazioni con la voce Modello della riproduzione casuale: casualità totale, come finora, con un brano qualsiasi ogni volta; una volta per brano, poi si ferma; una volta per brano, poi ricomincia, che è il modello di partenza. Con il mazzo ogni brano suona una volta prima che si ricominci, anche quello scelto da te; finito il mazzo, la riproduzione si ferma e la console lo dice, oppure si rimescola e si continua senza ripetere subito l'ultimo brano. Maiuscolo con N, accendendo, dice il modello. Chiesto da Gabriele al collaudo.

## [1.60.1] - 2026-10-02

- O abbassa la banda dell'equalizzatore e P la alza, come A e D per la velocità e F e H per il tono: a sinistra si scende, a destra si sale. Il suono segue, perché dice il guadagno. Dal collaudo di Gabriele.

## [1.60.0] - 2026-10-02

- W accetta anche un tempo contato dalla fine, con il meno davanti: -12 va a dodici secondi dalla fine, -1:30 a un minuto e mezzo dalla fine. Comodo per sentire la dissolvenza senza fare il conto. Chiesto da Gabriele al collaudo.

## [1.59.2] - 2026-10-02

- I decimali si scrivono con il punto in tutta MeTeOra, come avevamo deciso: la velocità, per esempio 1.05, la durata della dissolvenza, per esempio 2.5 secondi, le latenze delle schede audio, gli esempi dei campi e delle frasi d'errore, l'esempio delle dimensioni nel filtro e il manuale. Dalla tappa 4 alcuni usavano la virgola. Scrivendo, la virgola si accetta ancora. Dal collaudo di Gabriele.
- Il manuale, fra le voci delle impostazioni, ha anche la Riproduzione casuale.

## [1.59.0] - 2026-10-02

- Maiuscolo con N accende e spegne la riproduzione casuale. Accesa, quando un brano finisce da solo il seguente si sceglie a caso fra quelli che l'avanzamento automatico potrebbe suonare: le voci che si vedono nella plancia, oppure la lista, il loop o la selezione da cui si suona. Con la dissolvenza il brano scelto è quello che entra sfumando. Z, B e gli altri tasti restano come sono, e MeTeOra ricorda la scelta alla riapertura; c'è anche nelle impostazioni. I suoni sono due avvisi del loop di prima, nella collezione di GBUtils V185. Chiesto da Gabriele nella issue 17.

## [1.58.4] - 2026-10-02

- Con la dissolvenza accesa, la pausa, lo stop e il brano che esce da una dissolvenza fra due brani finivano con un piccolo taglio: la voce non arrivava a zero, ma si fermava a circa un settimo, l'ultimo gradino della discesa. Adesso scende fino al silenzio, e il brano si ferma un istante dopo. Trovato da una prova che falliva ogni tanto.
- O e P suonano un'ottava più su: il fa di riferimento è il fa 4, e la nota del guadagno sta fra un'ottava e mezza sotto e un'ottava e mezza sopra. A -12 dB scendeva sotto i 62 Hz e si sentiva appena. Dal collaudo di Gabriele.
- Le note di O e P cominciano e finiscono senza schiocchi: hanno un attacco e un rilascio di pochi millesimi di secondo, dove prima l'onda triangolare partiva di colpo dal suo picco. Dal collaudo di Gabriele.

## [1.58.1] - 2026-10-02

- F abbassa il tono e H lo alza, come A e D per la velocità: a sinistra si scende, a destra si sale. Anche i suoni seguono. Dal collaudo di Gabriele.

## [1.58.0] - 2026-10-02

- Con la dissolvenza accesa sfumano anche lo stop, la pausa e la ripresa, X da capo e i salti ai marker con R, Y e Maiuscolo con le cifre. Lo stop fa spegnere il brano piano mentre MeTeOra è già pronta a suonarne un altro; la pausa arriva quando la voce è scesa, e la ripresa riparte dal silenzio e risale; X da capo e i marker fanno incrociare il punto di partenza e quello d'arrivo dello stesso brano. Chiesto da Gabriele al collaudo.
- I suoni di U, I, O e P si fanno al volo e dicono a orecchio quello che stai facendo: U e I suonano un fa di riferimento e poi una nota della scala, da do a si, una per banda; O e P lo stesso fa e poi una nota tanto più su o più giù quanto più la banda è alzata o abbassata, su tre ottave. Chiesto da Gabriele.
- Il loop si fa tutto con Maiuscolo con X, a giro: senza loop mette il punto A, con il punto A mette il punto B, anche sullo stesso brano, che allora si ripete da solo, e con A e B toglie il loop. Maiuscolo con C resta libero. I suoni del loop sono i soffi che prima avevano U, I, O e P, nella collezione di GBUtils V184. Chiesto da Gabriele.

## [1.55.2] - 2026-10-02

- Un brano finito proprio nell'istante in cui ne partiva un altro poteva far saltare il brano appena partito: la fine del vecchio veniva presa per quella del nuovo, e MeTeOra passava al seguente. Era una coincidenza rara, vista nel codice e mai sentita.

## [1.55.1] - 2026-10-02

- A ogni passaggio automatico da un brano all'altro la finestra si fermava per circa mezzo secondo, il tempo in cui il brano vecchio finiva di uscire dalla scheda audio, e i tasti premuti in quel momento aspettavano. Ora i comandi al motore partono senza aspettare, e la finestra resta pronta.

## [1.55.0] - 2026-10-02

- Velocità: A rallenta e D accelera la riproduzione a passi di 0,05, da 0,5 a 2; S torna alla velocità normale. Il tono non cambia, anche sui SID.
- Tono: F lo alza e H lo abbassa di un semitono, fino a dodici sopra o sotto; G lo riporta al normale. La velocità non cambia.
- Equalizzatore a sette bande, da 60 a 12000 Hz: U e I scelgono la banda, O e P la alzano e la abbassano di un dB, da -12 a +12, È la azzera e Maiuscolo con È le azzera tutte. Le bande seguono il tono, e contro la saturazione il volume scende da solo quanto la banda più alzata: con una sola banda alzata il suono non satura, mentre con più bande vicine alzate, o tutte, la risposta sale fino a circa 5,6 dB oltre, e dal volume 80 o 90 in su conviene abbassare il volume. I guadagni restano dopo i salti nel brano, da un brano all'altro e quando Windows cambia la scheda audio predefinita.
- Dissolvenza incrociata: L la accende e la spegne, Maiuscolo con L ne chiede la durata, da mezzo secondo a 15 secondi, 4 se non la cambi. Il brano che finisce sfuma mentre il seguente entra, a potenza costante, a ogni cambio di brano, da solo o con i tasti, compreso il ritorno al punto A del loop; con un brano corto la dissolvenza si accorcia. Il seguente si prepara poco prima, e se intanto la plancia cambia, quando la dissolvenza comincia MeTeOra ricontrolla e suona quello giusto; se davanti non c'è più niente, il brano in corso arriva in fondo. In pausa la dissolvenza aspetta la ripresa.
- Velocità, tono, equalizzatore e dissolvenza si ricordano fra un avvio e l'altro e valgono per tutti i brani; all'avvio la console dice velocità e tono se non sono quelli normali. Le impostazioni hanno quattro voci nuove, dopo Salto avanti di E: Velocità, Tono, Equalizzatore e Dissolvenza. Le righe della console di questi tasti sono brevi e si riscrivono a ogni pressione, come quella del volume.
- Ogni tasto nuovo ha il suo suono, anche ai limiti: diciannove suoni nuovi, nella collezione di GBUtils V183. Issue 15, tappa 4.

## [1.51.3] - 2026-10-01

- X ha il suo suono: era muto, perché il volume del suo preset, Rapida_salita-sin_des, era scritto come testo, che Acusticator legge come volume assoluto zero mentre Acu_Maker lo legge come scarto dalla base, e così lo sentivi solo lì. Corretto nella collezione di GBUtils V182; la differenza fra le due letture resta da decidere nella issue 47 di GBUtils.

## [1.51.2] - 2026-10-01

- Maiuscolo con Q ed E, e W, accettano solo cifre, punto, virgola e due punti: prima passavano anche scritture come inf o 1e5, e con inf il salto diventava infinito.
- Un file delle impostazioni che contiene un JSON ma non delle impostazioni, per esempio una lista, non ferma più l'avvio.

## [1.51.0] - 2026-10-01

- La finestra delle impostazioni, dalla voce Impostazioni della plancia: una lista con una riga per voce, il nome e il valore di adesso. Invio su una voce apre un campo come quello del filtro, con le spiegazioni, i limiti e qualche esempio nelle righe col dollaro e il valore di adesso già selezionato nell'ultima riga. Un numero oltre i limiti si porta al limite, e la console lo dice; un testo che non si capisce riapre il campo con la spiegazione in testa. Ogni valore vale subito e si salva subito. Ci sono il volume della musica, il passo del volume, il volume degli effetti in percentuale, i salti di Q ed E, l'inseguimento della plancia e le righe della console, che si tolgono subito se il numero scende. Anche nel file delle impostazioni i valori fuori dai limiti, come un passo del volume a zero o un salto negativo scritti a mano, prendono il valore di partenza invece di arrivare al programma. La finestra, i suoi campi e le sue azioni hanno undici suoni nuovi, nella collezione di GBUtils. Issue 14, tappa 3.
- Dimensioni dei caratteri: plancia, console e cruscotto hanno ciascuna il suo carattere, da 6 a 72 punti, o tutte e tre lo stesso con un numero solo; il cruscotto cambia altezza con il suo carattere, per tenere cinque righe, ma di solito non occupa più di un terzo della finestra, così con caratteri molto grandi plancia e console restano visibili e il cruscotto scorre; due righe le tiene sempre, anche oltre il terzo in una finestra bassa. Il campo vuoto torna al carattere di Windows.
- Colori dei caratteri: per ogni area la sua lettera e tre percentuali di rosso, verde e blu, come p31.31.31, un bel grigio scuro; la lettera da sola torna ai colori di Windows.
- Colori dello sfondo, scritti come quelli dei caratteri.
- La finestra dei marcatori, dalla voce Marcatori: tutti i marker in una lista, uno per riga, con cartella, file, nome e tempo, raggruppati per cartella e per file, con la selezione multipla di Esplora risorse. La barra rovesciata cerca, con tre suoni suoi per il testo trovato, trovato ripartendo dalla cima e non trovato; Invio rinomina, Canc elimina, Cancella tutto li toglie tutti dopo una conferma. Esporta selezionati scrive i marker scelti in un file, con i nomi e le durate dei file ma senza i percorsi, perché altrove gli stessi file stanno in altre cartelle.
- Importa marcatori: i marker esportati da un'altra copia di MeTeOra arrivano su ogni copia degli stessi file, riconosciuti dal nome e dalla durata; quelli che ci sono già restano come sono, e la console dice quanti ne sono arrivati. Un file rovinato, per esempio con un tempo impossibile, di oltre trecento anni, non si importa, e la console dice perché.
- Salva console: tutta la console in un file di testo nella cartella del programma, con la versione, la data e l'ora nel nome, per esempio MeTeOra-V1_51_3-2026_10_01-15_42.txt.
- Scheda audio: una sola per la musica e per gli effetti, scelta da una lista in ordine di latenza, con in cima la scelta automatica, la più pronta fra quelle che portano alla scheda che Windows usa già. ASIO c'è, con l'avviso che può zittire NVDA. Se gli effetti non aprono la scheda scelta si torna all'automatica, e se la musica non la ritrova, per esempio con ASIO, suona sulla scheda di Windows: la console dice l'una e l'altra cosa. La prova dell'apertura vale anche con gli effetti a volume zero. Se all'avvio la scheda scelta non c'è, o c'è ma gli effetti non la aprono, per esempio perché un altro programma la tiene tutta per sé, suona l'automatica, e la scelta resta per quando la scheda torna; se non si apre, suona anche l'errore.

## [1.43.2] - 2026-10-01

- X su un marker fa come sul suo brano: lo suona dall'inizio, o se è il brano in corso lo riprende dalla pausa o lo fa ripartire da capo. Prima ripartiva dal marker, e dopo R o Y, che portano il fuoco sul marker, X non tornava più all'inizio del brano. Per suonare da un marker restano R, Y, Maiuscolo con le cifre e Vai al marker nel menu. Dal collaudo di Gabriele.
- Il beep dei livelli aspetta che finisca il suono del comando, invece di sovrapporsi, come accadeva con Backspace; se intanto un altro tasto cambia di nuovo livello, suona solo il beep dell'ultimo, e se il fuoco lascia la plancia, per esempio per un dialogo, tace. Dal collaudo di Gabriele.
- Ogni suono che MeTeOra prende dalla collezione di GBUtils porta la sua firma: se non ha meteora nel nome, la descrizione finisce con Usato da e il nome di MeTeOra, così Gabriele lo ritrova in Acu_Maker. Una prova automatica lo controlla. Le firme, per tutte le app, sono nella collezione di GBUtils V179.

## [1.43.0] - 2026-10-01

- Maiuscolo con Backspace risale di colpo al ramo antenato della plancia, cioè all'unità in Questo PC o alla playlist nel ramo Playlist, o ai Preferiti per i loro brani, e chiude i rami aperti dentro di lui: l'antenato resta aperto, così si scende subito in un ramo fratello. Ha un suono nuovo, meteora_risali_all_antenato, un salto d'ottava di onda triangolare, nella collezione di GBUtils V179. Prima scendeva fino all'ultimo ramo aperto, ma a Gabriele serviva la risalita: Backspace sale di un livello alla volta, e da otto livelli sotto servivano otto pressioni. Già sull'antenato, o al primo livello, il fuoco resta dov'è e la console lo dice.

## [1.42.2] - 2026-10-01

- Maiuscolo con le cifre suona il brano dal marker ma lascia il fuoco della plancia dov'è: prima lo portava sul marker, e X dopo ripartiva dal marker invece che dall'inizio del brano. Dal collaudo di Gabriele.
- F10 aveva lo stesso suono di J: ora ha meteora_apri_tutto, nuovo nella collezione di GBUtils V178, lo specchio di F9, le stesse tre note a dente di sega che salgono invece di scendere.

## [1.42.0] - 2026-10-01

- Il beep dei livelli: quando un tasto della plancia porta il fuoco a un livello diverso dell'albero, un beep breve, una sinusoide di 150 millisecondi con attacco e rilascio morbidi, ne dice la profondità: do al primo livello e tre semitoni più su per ogni livello, fino al do 8 del diciassettesimo livello. Vale per le frecce e per ogni comando, anche dopo un dialogo di conferma, ma non mentre si lavora nella console o nel cruscotto. Il suono si crea al momento con Acusticator, perché la sua altezza dipende dal livello. Chiesto da Gabriele.

## [1.41.0] - 2026-10-01

- Nella plancia, ogni ramo che apri con freccia destra ha il suo suono, carta_pescata, e ogni ramo che chiudi con freccia sinistra ne ha uno nuovo, meteora_ramo_chiuso: lo stesso fruscio, ma di rumore marrone, più scuro, che scende. Prima suonava solo la prima volta che si apriva una cartella. I rami che aprono e chiudono i comandi, come F9, F10, J, K e Backspace, restano con i loro suoni. Chiesto da Gabriele al collaudo; il suono nuovo è nella collezione di GBUtils V177.

## [1.40.2] - 2026-10-01

- Maiuscolo con R e Maiuscolo con Y tolgono i marker prima e dopo il punto in cui sei, ma non quello su cui sei: prima toglievano anche lui. Maiuscolo con T continua a toglierli tutti. Dal collaudo di Gabriele.

## [1.40.1] - 2026-10-01

- Il suono di Maiuscolo con Backspace era a onda quadra, che Gabriele trova aggressiva, e quasi uguale a quello di K: ora è meteora_scendi, nuovo nella collezione di GBUtils V176, lo specchio del suono di Backspace, le stesse tre note di seno che scendono da destra a sinistra.

## [1.40.0] - 2026-10-01

- Maiuscolo con le cifre da 1 a 0, cioè i tasti del punto esclamativo, delle virgolette e così via fino all'uguale nella tastiera italiana, va ai primi dieci marker del brano su cui sta la plancia: lo suona da lì e porta il fuoco della plancia sul marker. Se il brano ha meno marker, la console dice quanti ne ha; su un SID con più sottobrani chiuso vale il sottobrano che suona, o l'iniziale. Il fuoco resta sotto la voce su cui eri anche se lo stesso file suona da un'altra playlist, e se il brano era fermo la console dice anche da quale marker parte.

## [1.39.1] - 2026-10-01

- Le righe della console accordano il singolare: tolto 1 brano, eliminata 1 playlist, tolto ed eliminato 1 marker, invece di tolti ed eliminate.

## [1.39.0] - 2026-10-01

- I marker, issue 12: T mette un marker nel punto del brano in cui sei, con un nome automatico, M1, M2 e così via; fermo su un marker, a meno di cinque millesimi di secondo, ne chiede invece il nuovo nome.
- R e Y vanno al marker precedente e al successivo, anche in pausa, e portano il fuoco della plancia sul marker; R si ferma al primo, Y all'ultimo. Maiuscolo con R toglie i marker dall'inizio fino a dove sei, Maiuscolo con Y da dove sei alla fine, Maiuscolo con T tutti.
- Nella plancia un brano con dei marker dice quanti sono e si apre con freccia destra: dentro ci sono i marker, con nome e tempo. Invio ne cambia il nome, X suona il brano da lì, Canc lo elimina, e il menu ha Vai al marker, Rinomina ed Elimina. Un marker sta con il file: le copie identiche dello stesso file, in altre playlist o cartelle, hanno gli stessi marker. I marker si salvano in MeTeOra - Marcatori.json, e ogni azione ha il suo suono nuovo, breve, nella collezione di GBUtils.
- Mentre il brano suona, R salta il marker superato da meno di un secondo e mezzo, così premuto subito dopo un salto va a quello prima. X su un marker riparte anche dalla pausa e rispetta il loop A-B. J, K e le cifre aprono le playlist senza aprire gli elenchi dei marker. Una copia aperta prima che MeTeOra ne leggesse la durata si apre sui suoi marker appena la durata arriva. I SID fuori da una collezione HVSC usano il percorso, perché la loro durata non si sa. Un file dei marker che non si legge resta com'è, la console lo dice e i marker nuovi vanno accanto, nel file .nuovo, che si rilegge le volte dopo; un salvataggio fallito si ritenta all'uscita.

## [1.36.2] - 2026-10-01

- Dopo Ctrl con le frecce, che muove il fuoco senza selezionare, Canc, Maiuscolo con Canc, X, Maiuscolo con X, F4 e il menu agiscono sulla voce selezionata, se è una sola, e non su quella che ha solo il fuoco, come in Esplora risorse. Prima Canc toglieva dalla playlist, senza conferma, la voce col fuoco.

## [1.36.1] - 2026-10-01

- Backspace nella plancia chiude il ramo in cui sei e ci porta il fuoco; premuto ancora risale di un livello, chiudendo anche quello. Prima saliva soltanto, come freccia sinistra.
- Maiuscolo con Backspace scende dentro la voce su cui sei, lungo i rami aperti, fino all'ultimo ramo aperto, e ci porta il fuoco. Se la voce è chiusa ma dentro ha rami rimasti aperti, la riapre: per esempio dopo Backspace su una playlist aperta.
- Con Maiuscolo o Ctrl e le frecce, Inizio, Fine, Pagina su e Pagina giù, NVDA non ripete più il nome della plancia prima di ogni voce. wxWidgets, per spostare il fuoco da una voce selezionata, toglieva per un istante la selezione a tutto l'albero, e il fuoco cadeva sull'albero stesso: ora il fuoco si sposta con il messaggio di Windows, e le selezioni si rimettono dopo. La selezione con Maiuscolo parte sempre dalla stessa ancora, anche lasciando e ripremendo Maiuscolo, dopo Ctrl con le frecce e quando una voce in mezzo sparisce.

## [1.34.6] - 2026-10-01

Correzioni trovate da una revisione a più agenti della 1.34.1, prima del collaudo.

- Una cartella vista vuota quando la si contava, e riempita dopo, non sparisce più mentre la tieni aperta: una cartella aperta che mostra dei file resta sempre, la sua lettura fresca corregge i conti, e Aggiorna su Questo PC rifà tutti i conti, come già Aggiorna su una cartella.
- Una playlist si ricarica ogni volta che la richiudi e la riapri, come il manuale prometteva: l'elenco dei brani che passano il filtro segue le durate e i tag arrivati nel frattempo, e una playlist che il filtro svuotava non resta più chiusa per sempre.
- Mandando nel cestino dei Risultati, la ricerca non riaggiunge più gli ultimi risultati doppi: i file cestinati escono anche dal loro ramo e dai conti.
- Nella console le posizioni contano le emoji come le conta Windows: con un'emoji in una riga, la ricerca, le righe che si riscrivono e il taglio delle righe vecchie non cadono più un carattere prima.
- Nella ricerca nella console Invio passa all'occorrenza seguente anche con un jolly in testa, invece di ritrovare un pezzo della stessa; l'asterisco in testa si ignora e quello da solo si spiega; la riga che dice che il testo non c'è non viene più ritrovata dalla ricerca dopo.

## [1.34.1] - 2026-10-01

- Il filtro esce dalla plancia: non è più la prima voce della playlist, così NVDA conta solo i brani, e il primo è 1 di quanti sono. Il suo testo sta nell'etichetta della playlist, dopo i conti; si apre dal menu della playlist, e dei Preferiti, con le voci Filtro e Togli il filtro, oppure con la barra verticale, da qualsiasi area, sulla playlist in cui sta la plancia. Una playlist che il filtro svuota non si apre.
- I campi del filtro e delle ricerche hanno in cima le istruzioni, tutti i comandi con un esempio, come righe che cominciano con il dollaro e non contano; si scrive nell'ultima riga, dove il testo di prima arriva selezionato. Il campo della ricerca e quello del filtro dicono cose loro.
- La ricerca nella console usa lo stesso campo, con istruzioni sue: il testo si cerca così com'è, senza badare alle maiuscole; l'asterisco vale qualsiasi testo nella stessa riga, il cancelletto una o più cifre, e fra virgolette la sequenza è esatta, maiuscole comprese. Si trovano anche gli orari in fondo alle righe.
- In Questo PC le cartelle senza niente da suonare, nemmeno nelle sottocartelle, spariscono appena il contatore le ha contate; se il fuoco era su di loro passa alla cartella vicina. Riaprendo, quelle già contate non compaiono nemmeno.
- I problemi interni, gli errori che MeTeOra non si aspettava, arrivano nella console con una riga breve che dice cosa e dove, e un suono loro; lo stesso problema ripetuto di seguito riscrive la sua riga con il conto delle volte.
- Le righe della console sono un'impostazione, righe_della_console, 2000 se non la si cambia: per ora si cambia nel file delle impostazioni, poi nella finestra della tappa 3.
- Dopo Canc su più voci il fuoco resta nella playlist in cui si lavorava, sulla voce vicina che rimane, invece di tornare sul ramo Playlist; lo stesso dopo Maiuscolo con Canc. Anche Canc su un brano solo, con un filtro, sceglie il brano vicino fra quelli che si vedono. Il fuoco su un sottobrano resta sul sottobrano.
- Nei campi dei filtri le istruzioni restano righe intere, senza a capo automatici, e un Backspace di troppo che attacca la riga in cui si scrive all'ultima istruzione non fa più perdere il testo. I problemi interni del motore, che python-mpv trasformava in semplici avvisi, arrivano anche loro nella console, e nel pacchetto compilato la riga dice il punto giusto del codice.

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
