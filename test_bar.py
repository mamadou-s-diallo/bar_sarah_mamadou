# Tests automatisés du projet BoraBora.
# Vérifie le fonctionnement des différents modes de simulation.

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from partie_1_sequentielle.etape_2_fichier import Clients
from unittest.mock import patch


DOSSIER = Path(__file__).resolve().parent


class TestBar(unittest.TestCase):
    def setUp(self):
        temporaire = tempfile.TemporaryDirectory()
        self.addCleanup(temporaire.cleanup)
        self.dossier = Path(temporaire.name)
        self.log = self.dossier / "service.log"

    def lancer(self, *options, saisie="", succes=True):
        resultat = subprocess.run(
            [sys.executable, "borabora", *options, "--unite", "0.015", "--journal", str(self.log)],
            cwd=DOSSIER, input=saisie, capture_output=True, text=True, timeout=8)
        self.assertEqual(resultat.returncode == 0, succes, resultat.stderr)
        return resultat.stdout

    def test_clavier(self):
        texte = self.lancer("--mode", "clavier", saisie="planteur,mojito\nmargarita\n\n")
        self.assertLess(texte.index("je prépare 'margarita'"), texte.index("je prépare 'planteur'"))
        self.assertLess(texte.index("je sers 'planteur'"), texte.index("je sers 'margarita'"))

    def test_fichier(self):
        texte = self.lancer("lundi", "--mode", "fichier")
        self.assertEqual(texte.count("je sers"), 4)
        self.assertLess(texte.index("je prépare 'daiquiri'"), texte.index("je prépare 'margarita'"))

    def test_journal(self):
        alice = self.lancer("lundi", "--mode", "journal", "--logs", "alice")
        bob = self.lancer("lundi", "--mode", "journal", "--logs", "bob")
        self.assertTrue(all(l.startswith("[alice]") for l in alice.splitlines()))
        self.assertTrue(all(l.startswith("[bob]") for l in bob.splitlines()))
        contenu = self.log.read_text(encoding="utf-8")
        self.assertIn(alice, contenu)
        self.assertIn(bob, contenu)

    def test_arrivees(self):
        with patch("time.time", return_value=0):
            self.assertEqual([t for t, c in reversed(Clients(DOSSIER / "mardi").commandes)], [0, 4, 6])

    def test_etape_incomplete(self):
        texte = self.lancer("lundi", "--etape", "1")
        self.assertEqual(texte.count("j'écris"), 2)
        self.assertNotIn("je sers", texte)

    def test_files_fifo(self):
        attendus = [nom for t, commande in reversed(Clients(DOSSIER / "mardi").commandes) for nom in commande]
        for etape in ("2", "3", "4"):
            with self.subTest(etape=etape):
                texte = self.lancer("mardi", "--etape", etape)
                for action in ("je prépare", "je sers"):
                    noms = [ligne.split("'")[1] for ligne in texte.splitlines() if action in ligne]
                    self.assertEqual(noms, attendus)

    def test_extensions_et_verrous(self):
        fichier = self.dossier / "affluence"
        fichier.write_text("".join(f"0 A{i},B{i},C{i}\n" for i in range(12)), encoding="utf-8")
        texte = self.lancer(str(fichier), "--mode", "extension")
        commandes = [c for t, c in Clients(fichier).commandes]
        self.assertIn("[bob] le pic est vide", texte)
        for nom in ("alice", "leo"):
            lignes = [l for l in texte.splitlines() if l.startswith(f"[{nom}]")]
            self.assertTrue(any("j'ai la commande" in l for l in lignes))
            self.assertTrue(any("j'apporte" in l for l in lignes))
            for i, ligne in enumerate(lignes):
                if "j'apporte" in ligne:
                    self.assertTrue(all("je sers" in l for l in lignes[i+1:i+4]))
        servis = [l.split("'")[1] for l in texte.splitlines() if "je sers '" in l]
        self.assertCountEqual(servis, [nom for c in commandes for nom in c])

    def test_vide_et_invalide(self):
        fichier = self.dossier / "essai"
        fichier.touch()
        for mode in ("async", "extension"):
            self.assertNotIn("je sers", self.lancer(str(fichier), "--mode", mode))
        fichier.write_text("0 mojito,\n", encoding="utf-8")
        self.lancer(str(fichier), succes=False)


if __name__ == "__main__":
    unittest.main()
