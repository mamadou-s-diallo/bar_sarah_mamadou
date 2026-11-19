import argparse
import asyncio
import math
import tempfile
from importlib import import_module
from pathlib import Path


def main(arguments=None):
    parser = argparse.ArgumentParser(description="Simulation du bar à cocktails")
    parser.add_argument("fichier", nargs="?", help="commandes des clients")
    parser.add_argument("--mode", choices=["clavier", "fichier", "journal", "async", "extension"],
                        default="async")
    parser.add_argument("--etape", choices=[1, 2, 3, 4], type=int, default=4,
                        help="étape de la partie asynchrone")
    parser.add_argument("--unite", type=float, default=1, help="secondes par unité")
    parser.add_argument("--logs", nargs="+", choices=["alice", "leo", "bob", "le_pic", "le_bar"])
    parser.add_argument("--journal", type=Path, default=Path(tempfile.gettempdir()) / "borabora.log")
    parser.add_argument("--extension", type=int, choices=[1, 2, 3], default=3)
    args = parser.parse_args(arguments)
    if not math.isfinite(args.unite) or args.unite < 0:
        parser.error("L'unité doit être un nombre positif ou nul.")
    if args.mode == "clavier" or (args.mode == "async" and not args.fichier):
        etape = import_module("partie_1_sequentielle.etape_1_clavier")
        le_pic = etape.Pic()
        le_bar = etape.Bar()
        etape.bob = etape.Barman(le_pic,le_bar)
        etape.alice = etape.Serveur(le_pic,le_bar)
        etape.main()
        return

    if not args.fichier:
        parser.error("Indiquer un fichier de commandes.")
    if args.mode in ("fichier", "journal"):
        dossier = "partie_1_sequentielle"
        numero = 2 if args.mode == "fichier" else 3
        prefixe = "etape"
    elif args.mode == "async":
        dossier, numero, prefixe = "partie_2_asynchrone", args.etape, "etape"
    else:
        dossier, numero, prefixe = "partie_3_extensions", args.extension, "extension"
    chemin = next((Path(__file__).parent / dossier).glob(f"{prefixe}_{numero}_*.py"))
    etape = import_module(f"{dossier}.{chemin.stem}")
    etape.unite = args.unite
    try:
        les_clients = etape.Clients(args.fichier)
    except (ValueError, OSError) as erreur:
        parser.error(str(erreur))
    if args.mode == "fichier":
        le_pic = etape.Pic()
        le_bar = etape.Bar()
        etape.bob = etape.Barman(le_pic,le_bar,les_clients)
        etape.alice = etape.Serveur(le_pic,le_bar,les_clients)
        etape.main()
        return

    noms = args.logs or ["alice","bob","leo"]
    with args.journal.open("a+", encoding="utf-8") as logf:
        etape.logf = logf
        print("\n---", file=logf)
        debut = logf.tell()
        etape.le_pic = etape.Pic("le_pic","le_pic" in noms)
        etape.le_bar = etape.Bar("le_bar","le_bar" in noms)
        materiel = (etape.le_pic,etape.le_bar,les_clients)
        etape.bob = etape.Barman(*materiel,"bob","bob" in noms)
        etape.alice = etape.Serveur(*materiel,"alice","alice" in noms)
        if args.mode == "extension":
            etape.leo = etape.Serveur(*materiel,"leo","leo" in noms)
            if numero >= 2:
                etape.alice.tempo, etape.bob.tempo, etape.leo.tempo = 0.25, 0.4, 0.5
        if args.mode == "journal":
            etape.main()
        else:
            asyncio.run(etape.main())
        logf.seek(debut)
        print(logf.read(), end="")
