# MeTeOra, le prove delle parole del PUB e dei registri da allegare alla richiesta d'aiuto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
# 03/11/2026: nasce con la 2.4.0.

"""I registri stanno in una cartella di prova: niente di vero si legge o si
scrive accanto al programma."""

import os

import pub


def test_ripulisci_toglie_utente_e_computer():
    testo = "C:\\Users\\Utente\\Music e C:/Users/utente/Desktop, \\\\GABRYBAT\\musica, il computer gabrybat; l'utente resta, e Utentessa pure."
    assert pub.ripulisci(testo, "Utente", "GabryBat") == (
        "C:\\Users\\<utente>\\Music e C:/Users/<utente>/Desktop, \\\\<computer>\\musica, il computer <computer>; l'utente resta, e Utentessa pure.")
    # Un nome con lo spazio, e il nome che chiude il percorso.
    assert pub.ripulisci("C:\\Users\\Gabriele Battaglia", "Gabriele Battaglia", "") == "C:\\Users\\<utente>"
    # Senza nomi, il testo resta com'e'.
    assert pub.ripulisci("C:\\Users\\X", "", "") == "C:\\Users\\X"


def test_i_registri_presenti_e_il_file_da_allegare(tmp_path):
    assert pub.registri_presenti(str(tmp_path)) == []
    assert pub.scrivi_i_registri(str(tmp_path), "2.4.0", "Utente", "PC") is None
    (tmp_path / "MeTeOra - Errori.log.1").write_text("vecchio\n", encoding="utf-8")
    (tmp_path / "MeTeOra - Errori.log").write_text("x" * (pub.CODA_DEGLI_ERRORI + 10) + "\n", encoding="utf-8")
    (tmp_path / "MeTeOra - Crash.log").write_text("il file del crash in corso non si allega\n", encoding="utf-8")
    (tmp_path / "MeTeOra - Crash precedente.log").write_text("", encoding="utf-8")
    riserva = tmp_path / "MeTeOra - Crash precedente 2026-11-03 10.00.00.log"
    riserva.write_text("resoconto\n", encoding="utf-8")
    presenti = [os.path.basename(p) for p in pub.registri_presenti(str(tmp_path))]
    assert presenti == ["MeTeOra - Errori.log.1", "MeTeOra - Errori.log", riserva.name]
    percorso = pub.scrivi_i_registri(str(tmp_path), "2.4.0", "Utente", "PC")
    assert percorso == str(tmp_path / pub.FILE_DEI_REGISTRI)
    with open(percorso, encoding="utf-8") as f:
        righe = f.read().splitlines()
    # Del registro degli errori resta la parte finale, senza la copia vecchia.
    assert righe[1] == "Dal registro degli errori, la parte finale:" and righe[2] == "x" * (pub.CODA_DEGLI_ERRORI - 1)
    assert righe[3:] == [f"Dal resoconto del crash {riserva.name}, tutto:", "resoconto"]


def test_la_mail_d_aiuto_con_e_senza_registri():
    informazioni = [("windows", "Windows 11 Pro")]
    senza = pub.mail_d_aiuto("2.4.0", True, informazioni)
    assert len(senza["passi"]) == 4 and "appunti" not in senza and "casella" not in senza["spiegazione"]
    assert senza["passi"][-1][0].startswith("Passo 4 di 4. Spedisci la mail.")
    offerta = pub.mail_d_aiuto("2.4.0", True, informazioni, casella=True)
    assert "spunta la casella qui sotto" in offerta["spiegazione"] and offerta["corpo"] == senza["corpo"]
    con = pub.mail_d_aiuto("2.4.0", True, informazioni, casella=True, registri="D:\\MeTeOra\\MeTeOra - Registri per il PUB.txt")
    assert con["appunti"] == "D:\\MeTeOra\\MeTeOra - Registri per il PUB.txt"
    assert [n.split(".")[0] for n, _t in con["passi"]] == [f"Passo {i} di 5" for i in range(1, 6)]
    assert "nella cartella D:\\MeTeOra:" in con["spiegazione"] and "spunta la casella" not in con["spiegazione"]
