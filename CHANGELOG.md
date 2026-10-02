# Changelog - MeTeOra

Tutti i cambiamenti e le novità introdotte nelle versioni di MeTeOra.

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
