"""Velocita del motore e differenza fra sottobrani."""
import time

import ambiente  # noqa: F401
import numpy as np

# isort: split
import sid as sidmotore

SID = r"E:\C64Music\MUSICIANS\T\Tel_Jeroen\Turbo_Outrun.sid"
impronte = []
for n, secondi in ((1, 60), (2, 60), (3, 30)):
    t0 = time.perf_counter()
    b = sidmotore.BranoSid(SID, n, secondi)
    b.aspetta(sidmotore.FREQUENZA // 10 * 2)
    partenza = time.perf_counter() - t0
    b.aspetta(b.totale)
    durata = time.perf_counter() - t0
    stereo = b.dati.reshape(-1, 2)
    impronte.append(stereo[: sidmotore.FREQUENZA * 20, 0].astype(float))
    print(f"sottobrano {n}: {secondi} s resi in {durata:.2f} s ({secondi / durata:.0f} volte il tempo reale), primi 100 ms pronti in {partenza * 1000:.0f} ms, rms {stereo.std():.0f}, L uguale a R: {np.array_equal(stereo[:, 0], stereo[:, 1])}")
    b.ferma()
print("1 e 2 diversi:", not np.array_equal(impronte[0], impronte[1]), "| 1 e 3 diversi:", not np.array_equal(impronte[0], impronte[2]))
