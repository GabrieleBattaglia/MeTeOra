# MeTeOra, il lettore multimediale accessibile: il programma da avviare.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.34.0 i problemi interni arrivano nella console. Nella 1.84.0 il controllo degli aggiornamenti. Nella 1.89.0 il registro degli errori e dei crash. Nella 1.90.0 le copie dei dati.

"""Avvia MeTeOra: controlla le librerie native e apre la finestra massimizzata."""

import wx


def main():
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
    from finestra import FILE_IMPOSTAZIONI, FILE_MARCATORI, FILE_PLAYLIST, Finestra

    # Le copie dei dati, prima di leggerli: una per sessione (1.90.0).
    mancate = copie.ruota(percorsi.cartella_programma(), [FILE_PLAYLIST, FILE_MARCATORI, FILE_IMPOSTAZIONI])
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
    # Solo dall'eseguibile compilato, in un filo: la finestra intanto risponde.
    import aggiornamento

    aggiornamento.controlla(finestra)
    app.MainLoop()
    # L'uscita pulita: il file del crash si toglie.
    registro.scrivi("MeTeOra si chiude.")
    registro.chiudi()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
