#!/usr/bin/env python3
# Partie 3, extension 1 : ajout d’un deuxième serveur.
# Coordonne la prise des commandes dans le bar.


import sys,time,re
import tempfile
from pathlib import Path
import asyncio

unite = 1

def usage():
    print(f"usage: {sys.argv[0]} fichier")
    exit(1)

class Clients:
    def __init__(self,fname):
        self.prise = asyncio.Lock()
        commandes = []

        start = time.time()
        fmt = re.compile(r"(\d+)\s+(.*)")
        with open(fname,"r",encoding="utf-8-sig") as f:
            for line in f:
                found = fmt.search(line)
                if found:
                    when = int(found.group(1)) * unite
                    what = found.group(2)
                    if any(not conso.strip() for conso in what.split(",")):
                        raise ValueError("Cocktail vide dans le fichier")
                    commandes.append((start+when,what.split(",")))
                    start += when
        self.commandes = commandes[::-1]

    async def commande(self):
        if len(self.commandes)>0:
            when,what = self.commandes.pop()
            await asyncio.sleep(max(0,when-time.time()))
            return what
        return None

class Logable:
    """
    Classe de base pour disposer d'une méthode log
    """

    def __init__(self,name,verbose):
        self.name = name
        self.verbose = verbose

    def log(self,msg):
        if self.verbose:
            print(f"[{self.name}] {msg}", file=logf, flush=True)

class Accessoire(asyncio.Queue,Logable):
    def __init__(self,name,verbose):
        asyncio.Queue.__init__(self)
        Logable.__init__(self,name,verbose)

class Pic(Accessoire):
    """
    Un pic contient les commandes à fabriquer.
    Il peut embrocher un post-it contenant une commande
    (une liste de consommations) par-dessus les post-it
    déjà présents et libérer le premier embroché.
    """

    async def embrocher(self,postit):
        await self.put(postit)
        self.log(f"post-it '{postit}' embroché, {self.qsize()} post-it(s) à traiter")

    async def liberer(self):
        postit = await self.get()
        if postit is not None:
            self.log(f"post-it '{postit}' libéré, {self.qsize()} post-it(s) à traiter")
        return postit

class Bar(Accessoire):
    """
    Un bar peut recevoir des commandes (composées de consommations),
    en attente d'être servies (évacuées).
    """

    async def recevoir(self,commande):
        await self.put(commande)
        self.log(f"'{commande}' posée, {self.qsize()} commande(s) à servir")

    async def evacuer(self):
        commande = await self.get()
        if commande is not None:
            self.log(f"'{commande}' évacuée, {self.qsize()} commande(s) à servir")
        return commande

class Employé(Logable):
    """
    Classe de base modélisant un employé
    """
    def __init__(self,pic,bar,clients,name,verbose):
        Logable.__init__(self,name, verbose)
        self.pic = pic
        self.bar = bar
        self.clients = clients
        self.verrou = asyncio.Lock()
        self.step = 0
        self.log('prêt pour le service')

class Serveur(Employé):
    async def prendre_commande(self):
        while True:
            async with self.clients.prise:
                commande = await self.clients.commande()
                if commande is None:
                    break
                async with self.verrou:
                    self.log("prêt pour prendre une nouvelle commande...")
                    self.log(f"j'ai la commande '{commande}'")
                    await asyncio.sleep(0.4 * unite)
                    self.log(f"j'écris sur le post-it '{commande}'")
                    await self.pic.embrocher(commande)

    async def servir(self):
        while True:
            commande = await self.bar.evacuer()
            if commande is None:
                break
            async with self.verrou:
                self.log(f"j'apporte la commande '{commande}'")
                for conso in commande:
                    await asyncio.sleep(0.4 * unite)
                    self.log(f"je sers '{conso}'")

class Barman(Employé):
    async def preparer(self):
        while True:
            commande = await self.pic.liberer()
            if commande is None:
                break
            self.log(f"je commence la fabrication de '{commande}'")
            for conso in commande:
                await asyncio.sleep(0.4 * unite)
                self.log(f"je prépare '{conso}'")
            await self.bar.recevoir(commande)
            self.log(f"la commande {commande} est prête")
            self.pic.task_done()

async def main():
    async def prendre():
        await asyncio.gather(alice.prendre_commande(),leo.prendre_commande())
        await le_pic.join()
        await le_pic.put(None)

    async def preparer():
        await bob.preparer()
        await le_bar.put(None)
        await le_bar.put(None)

    await asyncio.gather(prendre(),preparer(),alice.servir(),leo.servir())

if __name__=="__main__":
  if len(sys.argv)!=2:
    usage()
  fcommandes = sys.argv[1]

  logfile = Path(tempfile.gettempdir()) / "borabora.log"
  print(f"Journal : {logfile}")
  with open(logfile,"a",encoding="utf-8") as logf:
    print("\n---", file=logf, flush=True)
    les_clients = Clients(fcommandes)
    le_pic = Pic(name="le_pic", verbose=False)
    le_bar = Bar(name="le_bar", verbose=False)
    bob = Barman(le_pic,le_bar,les_clients,name="bob",verbose=True)
    alice = Serveur(le_pic,le_bar,les_clients,name="alice",verbose=True)
    leo = Serveur(le_pic,le_bar,les_clients,name="leo",verbose=True)
    asyncio.run(main())
