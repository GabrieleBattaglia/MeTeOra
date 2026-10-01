# MeTeOra, il lettore multimediale accessibile: il programma da avviare.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 30/09/2026: nasce con la tappa 1. Nella 1.34.0 i problemi interni arrivano nella console.

"""Avvia MeTeOra: controlla le librerie native e apre la finestra massimizzata."""

import wx


def main():
    app = wx.App(False)
    try:
        import librerie  # noqa: F401
    except RuntimeError as e:
        wx.MessageBox(str(e), "MeTeOra non può partire", wx.OK | wx.ICON_ERROR)
        return 1
    import suoni
    from finestra import Finestra

    finestra = Finestra()
    finestra.ascolta_i_problemi()
    finestra.Maximize()
    finestra.Show()
    finestra.albero.SetFocus()
    suoni.suona("avvio", finestra.impostazioni["volume_effetti"])
    finestra.riprendi()
    app.MainLoop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
