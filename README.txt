BoraBora

Les commandes sont à exécuter dans PowerShell, depuis le dossier BoraBora qui contient les fichiers lundi, mardi.


Partie 1. Exécution séquentielle

Exécution et vérification

Étape 1. Saisie au clavier
py -3.13 .\partie_1_sequentielle\etape_1_clavier.py

Saisir une commande par ligne en séparant les cocktails par des virgules. Une ligne vide termine la saisie.

Étape 2. Lecture des commandes depuis un fichier
py -3.13 .\partie_1_sequentielle\etape_2_fichier.py .\lundi

Étape 3. Écriture dans le journal
py -3.13 .\partie_1_sequentielle\etape_3_journal.py .\mardi

Pour les deux premières étapes, les actions sont affichées dans le terminal. À partir de l’étape 3, elles sont enregistrées dans borabora.log. La commande suivante permet d’ouvrir ce fichier dans VS Code après chaque exécution.

code "$env:TEMP\borabora.log"

La dernière exécution se trouve à la fin du fichier.

Méthode utilisée

La classe Accessoire hérite de list. Elle sert de base aux classes Pic et Bar. Comme dans le code de départ, append() ajoute une commande et pop() retire la dernière commande déposée.

La classe Employé regroupe les attributs communs au serveur et au barman. Le premier appel à alice.run() permet de prendre les commandes. L’appel à bob.run() lance leur préparation. Le second appel à alice.run() lance le service. L’attribut step permet de distinguer les deux activités d’Alice.

À l’étape 2, la classe Clients lit les commandes dans le fichier indiqué au lancement. Chaque ligne contient un délai et les cocktails commandés. Les délais sont cumulés pour déterminer les instants d’arrivée.

À l’étape 3, la classe Logable permet aux employés et aux accessoires d’écrire dans le même journal. L’attribut name indique l’origine du message et verbose active ou désactive son écriture. Le fichier est ouvert en mode ajout pour conserver les exécutions précédentes.


Partie 2. Exécution asynchrone

Exécution et vérification

Étape 1. Passage aux coroutines
py -3.13 .\partie_2_asynchrone\etape_1_coroutines.py .\lundi

Étape 2. Utilisation des files FIFO
py -3.13 .\partie_2_asynchrone\etape_2_files_fifo.py .\lundi

Étape 3. Coopération entre les tâches
py -3.13 .\partie_2_asynchrone\etape_3_cooperation.py .\mardi

Étape 4. Utilisation d’un verrou
py -3.13 .\partie_2_asynchrone\etape_4_verrou.py .\mardi

La vérification se fait dans borabora.log. Pour comparer les étapes 3 et 4, il suffit de suivre les actions d’Alice entre le début et la fin du service d’un même plateau.

Méthode utilisée

À l’étape 1, la prise des commandes, la préparation et le service deviennent trois coroutines lancées avec asyncio.gather(). Les listes du programme séquentiel sont conservées. Une tâche peut donc trouver une liste vide et se terminer avant l’arrivée de la première commande.

À l’étape 2, le pic et le bar utilisent asyncio.Queue. La lecture avec await get() permet d’attendre une commande lorsque la file est vide. Les commandes sont retirées dans leur ordre de dépôt. La valeur None signale la fin du travail.

À l’étape 3, asyncio.sleep() simule le temps nécessaire pour prendre une commande, préparer un cocktail ou le servir. Pendant cette attente, une autre tâche peut avancer.

À l’étape 4, la prise de commande et le service utilisent le même verrou pour Alice. Le verrou est conservé jusqu’à la fin de l’action en cours. Alice termine ainsi son plateau avant de prendre une autre commande, tandis que Bob peut continuer ses préparations.


Partie 3. Extensions

Exécution et vérification

Extension 1. Ajout d’un second serveur
py -3.13 .\partie_3_extensions\extension_1_deux_serveurs.py .\mardi

Extension 2. Prise en compte du rythme de chaque employé
py -3.13 .\partie_3_extensions\extension_2_productivite.py .\mardi

Extension 3. Participation du barman au service
py -3.13 .\partie_3_extensions\extension_3_aide_bariste.py .\mardi

Les actions des trois employés sont enregistrées dans borabora.log. 

Méthode utilisée

La première extension ajoute une seconde instance de Serveur, nommée leo. Alice et Léo partagent les clients, le pic et le bar. Un verrou commun organise la prise des commandes. Chaque serveur possède aussi son propre verrou pour terminer le service d’un plateau avant de prendre une nouvelle commande.

La deuxième extension introduit l’attribut tempo. Sa valeur détermine la durée d’une action pour chaque employé et permet de faire travailler Alice, Bob et Léo à des rythmes différents.

Dans la troisième extension, Bob vérifie si le pic est vide après avoir préparé une commande. Si aucune autre commande n’attend, il sert lui-même le plateau. Sinon, il le dépose sur le bar et poursuit la préparation. La méthode apporter() est définie dans la classe Employé pour que les serveurs et le barman puissent l’utiliser.