# Changelog - MeTeOra

Tutti i cambiamenti e le novità introdotte nelle versioni di MeTeOra.

## [0.1.0] - 2026-09-29

Nasce il repository, dopo la fase di studio. Non c'è ancora un programma da usare: ci sono il piano, le prove di fattibilità e i prototipi.

- Il piano in `docs/piano.txt`: obiettivi, requisiti di accessibilità nati dal confronto con foobar2000, interfaccia ad albero con area dei messaggi e barra di stato, tasti rapidi, funzioni, architettura, tappe e rischi.
- Le prove della tappa 0 in `docs/tappa0-risultati.txt`: libmpv legge moltissimi formati, fa seek, velocità ed equalizzatore al volo, e segnala la fine del brano; non legge i SID.
- Il motore SID in tempo reale: una DLL propria su libsidplayfp, un filo che emula in anticipo e tiene il brano in memoria, e un flusso WAV virtuale che lo passa a libmpv. Parte in meno di mezzo secondo e non scrive niente su disco. Approvato all'ascolto.
- La lettura delle durate e dei sottobrani dal database Songlengths della High Voltage SID Collection.
- Lo script `strumenti/prepara_ambiente.py`, che scarica libmpv e compila la DLL dei SID.
