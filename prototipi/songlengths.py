"""Durate dei SID dal database Songlengths.md5 di HVSC.

Dal formato attuale (HVSC 68 in poi) la chiave e l'MD5 dell'intero file.
Ogni riga dati ha la forma md5=m:ss[.mmm] m:ss ... una durata per sottobrano.
"""
import hashlib
import os


def durata_in_secondi(testo):
	"""Converte 'm:ss' o 'm:ss.mmm' in secondi (float)."""
	minuti, secondi = testo.split(":")
	return int(minuti) * 60 + float(secondi)


def carica(percorso_md5):
	"""Legge Songlengths.md5 e restituisce {md5: [secondi, ...]}."""
	tabella = {}
	with open(percorso_md5, encoding="latin-1") as f:
		for riga in f:
			riga = riga.strip()
			if not riga or riga.startswith((";", "[")):
				continue
			chiave, _, valori = riga.partition("=")
			tabella[chiave.lower()] = [durata_in_secondi(v) for v in valori.split()]
	return tabella


def md5_file(percorso):
	with open(percorso, "rb") as f:
		return hashlib.md5(f.read(), usedforsecurity=False).hexdigest()


def leggi_intestazione(percorso):
	"""Titolo, autore, copyright, numero di sottobrani e sottobrano iniziale."""
	with open(percorso, "rb") as f:
		dati = f.read(0x76)

	def testo(inizio):
		return dati[inizio:inizio + 32].split(b"\0")[0].decode("latin-1")

	return {
		"titolo": testo(0x16),
		"autore": testo(0x36),
		"copyright": testo(0x56),
		"sottobrani": int.from_bytes(dati[0x0E:0x10], "big"),
		"iniziale": int.from_bytes(dati[0x10:0x12], "big"),
	}


def durate(percorso_sid, tabella):
	"""Lista delle durate per sottobrano, o None se il file non e nel database."""
	return tabella.get(md5_file(percorso_sid))


def trova_database(percorso_sid):
	"""Risale le cartelle fino a trovare DOCUMENTS\\Songlengths.md5."""
	cartella = os.path.dirname(os.path.abspath(percorso_sid))
	while True:
		candidato = os.path.join(cartella, "DOCUMENTS", "Songlengths.md5")
		if os.path.isfile(candidato):
			return candidato
		superiore = os.path.dirname(cartella)
		if superiore == cartella:
			return None
		cartella = superiore
