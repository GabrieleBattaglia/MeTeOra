# MeTeOra, il lettore multimediale accessibile: il programma da avviare.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.34.0 i problemi interni arrivano nella console. Nella 1.84.0 il controllo degli aggiornamenti. Nella 1.89.0 il registro degli errori e dei crash. Nella 1.90.0 le copie dei dati. Nella 1.91.0 i file passati da Windows e l'istanza unica. Nella 1.97.0 la versione giusta in App installate. Nella 1.103.0 le copie delle statistiche, e da dove arrivano i file aperti. Nella 1.104.0 le statistiche salvate subito e la pulizia all'avvio. Nella 1.112.0 le copie dei dischi della pulizia.

"""Avvia MeTeOra: controlla le librerie native e apre la finestra massimizzata.

Gli argomenti sono file e cartelle da suonare, come li passa Windows aprendo
un file da Esplora risorse (1.91.0). Se un MeTeOra e' gia' aperto, li riceve
lui, e questa copia si chiude subito.
"""

import os
import sys

import wx


def main():
    import istanza

    # Assoluti, come li passa istanza.manda: un nome relativo della riga di
    # comando, salvato cosi', all'avvio dopo non si ritroverebbe (1.104.0).
    da_aprire = [os.path.abspath(p) for p in sys.argv[1:]]
    # Prima di tutto, anche del registro: un MeTeOra gia' aperto riceve i
    # file e viene in primo piano, e questa copia non tocca niente (1.91.0).
    if istanza.manda(da_aprire):
        return 0
    app = wx.App(False)
    # Il registro degli errori e dei crash, per primo: anche un problema delle
    # librerie native ci finisce (1.89.0).
    import percorsi
    import registro
    import version

    crash_precedente = registro.avvia(percorsi.cartella_programma())
    registro.scrivi(f"MeTeOra {version.VERSION} si avvia.")
    try:
        import librerie  # noqa: F401
    except RuntimeError as e:
        registro.scrivi(f"MeTeOra non può partire: {e}")
        wx.MessageBox(str(e), "MeTeOra non può partire", wx.OK | wx.ICON_ERROR)
        registro.chiudi()
        return 1
    import copie
    import suoni
    from finestra import FILE_CON_LE_COPIE, Finestra

    # Le copie dei dati, prima di leggerli: una per sessione (1.90.0); dalla
    # 1.112.0 anche i dischi della pulizia, con l'elenco in finestra.
    mancate = copie.ruota(percorsi.cartella_programma(), FILE_CON_LE_COPIE)
    finestra = Finestra()
    finestra.ascolta_i_problemi()
    if mancate:
        registro.scrivi(f"Copie dei dati non riuscite: {', '.join(mancate)}.")
        finestra.copie_mancate(mancate)
    if crash_precedente:
        finestra.crash_precedente(crash_precedente)
    finestra.Maximize()
    finestra.Show()
    finestra.albero.SetFocus()
    suoni.suona("avvio", finestra.impostazioni["volume_effetti"])
    finestra.riprendi()
    # Le copie di MeTeOra aperte dopo passano qui i loro file.
    finestra.ascolto_delle_copie = istanza.Ascolto(lambda percorsi: wx.CallAfter(finestra.apri_dall_esterno, percorsi, "copia"))
    if da_aprire:
        finestra.apri_dall_esterno(da_aprire, "avvio")
    # Le statistiche subito sul disco, e la pulizia dei file spariti (1.104.0).
    finestra.dopo_l_avvio()
    # Solo dall'eseguibile compilato, in un filo: la finestra intanto risponde.
    import aggiornamento

    aggiornamento.controlla(finestra)
    if getattr(sys, "frozen", False):
        # Installato con il setup e poi aggiornato da se': App installate
        # deve dire la versione vera (1.97.0).
        import installazione
        installazione.aggiorna_la_versione(version.VERSION, percorsi.cartella_programma())
    app.MainLoop()
    # L'uscita pulita: il file del crash si toglie.
    registro.scrivi("MeTeOra si chiude.")
    registro.chiudi()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
