# Changelog - MeTeOra

Tutti i cambiamenti e le novità introdotte nelle versioni di MeTeOra.

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
