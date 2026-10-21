# MeTeOra, i nomi della sintesi dei sottotitoli: le uscite e le destinazioni, come si leggono all'utente.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/10/2026: nasce con la tappa 7, per i sottotitoli letti. Nella 1.82.0 dove vanno i testi, alla voce, al braille o a tutti e due, chiamati uno per uno. Nella 1.83.3 la voce di Windows aperta da MeTeOra quando accessible_output2 non ci riesce. Nella 1.85.0 fuori ZDSR, Dolphin, System Access e PC-Talker. Nella 1.105.0 dici puo' interrompere la voce che sta parlando, per Dove sono. Nella 1.113.6 le uscite, la voce di Windows e la barra braille a blocchi passano in GBsintesi di GBUtils V213, che serve anche a MESS: qui restano le parole da leggere.

"""I nomi delle uscite e delle destinazioni della sintesi dei sottotitoli.

Le uscite, la scelta automatica, la voce di Windows di ripiego e la barra
braille a blocchi stanno in GBsintesi di GBUtils, che non scrive frasi: le
parole che l'utente legge le da' MeTeOra, qui.
"""

from GBsintesi import AUTOMATICA

# Le uscite di GBsintesi.USCITE, con il nome da leggere.
NOMI = {
    "nvda": "NVDA",
    "jaws": "JAWS",
    "sapi5": "la voce di Windows, SAPI5",
}
# Dove vanno i testi letti, sottotitoli e karaoke (1.82.0): le chiavi di
# GBsintesi.DESTINAZIONI, salvate nelle impostazioni, e le loro righe.
DESTINAZIONI = {"entrambi": "alla sintesi e al braille", "sintesi": "solo alla sintesi", "braille": "solo al braille"}


def nome(chiave):
    """Il nome da leggere di una scelta delle impostazioni."""
    return "automatica" if chiave == AUTOMATICA else NOMI[chiave]
