#!/usr/bin/env python3
# Partie 1, étape 2 : lecture des commandes dans un fichier.
# Prise en compte des délais indiqués pour chaque commande.


import sys,time,re

unite = 1

def usage():
    print(f"usage: {sys.argv[0]} fichier")
    exit(1)

class Clients:
    def __init__(self,fname):
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

    def commande(self):
            if len(self.commandes)>0:
              while True:
                if time.time()>self.commandes[-1][0]:
                    return self.commandes.pop()[1]
            else:
                return None

class Accessoire(list):
    pass

class Pic(Accessoire):
    """
    Un pic contient les commandes à fabriquer.
    Il peut embrocher un post-it contenant une commande
    (une liste de consommations) par-dessus les post-it
    déjà présents et libérer le dernier embroché.
    """

    def embrocher(self,postit):
        self.append(postit)

    def liberer(self):
        if len(self)>0:
            postit = self.pop()
            return postit
        else:
            return None

class Bar(Accessoire):
    """
    Un bar peut recevoir des commandes (composées de consommations),
    en attente d'être servies (évacuées).
    """

    def recevoir(self,commande):
        self.append(commande)

    def evacuer(self):
        if len(self)>0:
            commande = self.pop()
            return commande
        else:
            return None

class Employé:
    def __init__(self,pic,bar,clients):
        self.pic = pic
        self.bar = bar
        self.clients = clients
        self.step = 0
        print(f"{self.__class__.__name__}: prêt pour le service")

class Serveur(Employé):
    def __init__(self,pic,bar,clients):
        super().__init__(pic,bar,clients)

    def prendre_commande(self):
        while True:
            print(f"{self.__class__.__name__}: prêt pour prendre une nouvelle commande...")
            commande = self.clients.commande()
            if not commande:
                break
            print(f"{self.__class__.__name__}: j'ai la commande '{commande}'")
            print(f"{self.__class__.__name__}: j'écris sur le post-it '{commande}'")
            self.pic.embrocher(commande)

    def servir(self):
        while True:
                commande = self.bar.evacuer()
                if not commande:
                    break
                print(f"{self.__class__.__name__}: j'apporte la commande '{commande}'")

                for conso in commande:
                    print(f"{self.__class__.__name__}: je sers '{conso}'")

    def run(self):
        if self.step==0:
            self.step += 1
            self.prendre_commande()
        elif self.step==1:
            self.step += 1
            self.servir()

class Barman(Employé):
    def __init__(self,pic,bar,clients):
        super().__init__(pic,bar,clients)

    def preparer(self):
        while True:
            commande = self.pic.liberer()
            if not commande:
                break
            print(f"{self.__class__.__name__}: je commence la fabrication de '{commande}'")
            for conso in commande:
                print(f"{self.__class__.__name__}: je prépare '{conso}'")
            self.bar.recevoir(commande)
            print(f"{self.__class__.__name__}: la commande {commande} est prête")

    def run(self):
        self.preparer()

def main():
    alice.run()
    bob.run()
    alice.run()

if __name__=="__main__":
  if len(sys.argv)!=2:
    usage()
  fcommandes = sys.argv[1]

  le_pic = Pic()
  le_bar = Bar()
  les_clients = Clients(fcommandes)
  bob = Barman(le_pic,le_bar,les_clients)
  alice = Serveur(le_pic,le_bar,les_clients)
  main()
