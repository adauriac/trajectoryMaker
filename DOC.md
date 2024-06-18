POUR L'UILISATEUR
Cette application sert à générer, modifier, afficher des trajectoires.

Les trajectoires crées peuvent être sauvegardées dans un fichier, ou
affichées dans une fenêtre sur l'écran. Il y a deux formats le format
historique csv, et un format spécifique plus lisible. Cette même
application permet de traduire d'un format dans l'autre car elle
peut lire et écrire des fichiers des deux types.

D'autre applications de la suite permettent d'"exécuter" les trajectoires.

Une trajectoires est un ensemble de sections comme définies dans plasmaGui.
Ce sont line, ezsqx, ezsqy, arc1 arc2, circ1 et circ2.
Il y a aussi des commandes de contrôle permettant de répéter des séquences.
Ce sont start, end, w.

Lorsqu'on démarre l'application apparait un écran divisé en deux parties.
En haut les boutons de controle, en bas la zone d'entrée des sections.
Chaque section correspond à une ligne, qui contient le type de la section,
les paramètres associés à cette section, un bouton à cocher pour indiquer
de parcourir cette section avec le plasma actif ou non, un aute bouton à
cocher pour déselectioner la ligne (une ligne déselectionnée est considérée
comme absente), et un numéro de ligne permettant aussi d'insérer une ligne
avant ou après. Il peut y avoir plus de sections que lignes possibles dans
la zone d'entrée. Dans ce cas la une "ascenceur" apparaît qui permettent
d'ajuster la partie visible. Le nombre maximum de lignes est fixé dans le
source du programme, la valeur choisie est 200 (il y a des commentaires sur
ce point dans la section "sous le capot". Le nombre de lignes visibles
est implicitement fixé par la hauteur de la zone d'entrée. La taille des
fenêtres est fixe. 

Le bouton addline ajoute une ligne à la fin.
Le bouton delselected supprime les lignes sélectionnées (on peut
préferrer les déselectionner seulemt qui permet de les remettre)

1) copie: On édite la ligne choisie en cliquant sur son numéro : un
pop-up apparait, choisir "copy"

2) colle: On édite la ligne que l'on veut remplacer en cliquant sur son numéro : un
pop-up apparait, choisir "paste"

Remarque on peut insérer une ligne vierge avant ou après une ligne en
éditant celle-ci et choisissant "insert below" ou "insert after" 

Quand un pop-up d'édition est activé les autres fenêtres sont
inactives. Il faut choisir une option du menu (par ex cancel)

---------------------------------------------------------------------------
SOUS LE CAPOT

La classe trajMaker peut etre appelée sans parent ou avec un parent : soit tk.Tk() soit un tk.Toplevel() 
Si elle est appelée avec un toplevel son layout DOIT etre pack()
Si elle appelée sans parent un toplevel sera cree.
Dans tous les cas myApp.parent sera accessible.

La classe trajMaker utilise des widgets ttk dès qu'ils existent:
ttk.Frame, ttk.Entry, ttk.Button, ttk.Combobox, ttk.Scrollbar,
ttk.Label, ttkCheckbutton (a travers jcCheckbutton))
et tk.Toplevel, tk.Canvas.

Il n'y a pas de redondance, c'est à dire que les paramètres sont dans
le widget. C'est pourquoi j'ai introduit un jcCheckButton, qui hérite
de ttk.Checkbutton

Flag utile pour debugger colorSpecialAsHelpToWork

Le copie/colle : on peut copier une ligne unique mise dans un
presse-papier invisible et coller cette ligne du presse-papier **à la
place** d'une ligne choisie

La section *arc2* sens>0 clockwise sens<=0 anti-clockwise

Creation d'un nouveau type de troncon:
	rajouter une nouvelle entree dans Dico et Types, la nouvelle entrée sera proposée 
	dans "comboboxSelect()" rajouter le cas à traiter
	dans "processTraj()" traiter effectivement le cas
---------------------------------------------------------------------------
AMéLIORATIONS POSSIBLES

	ne pas mettre de widget dans les cellules ne correspondant a aucun parametre 
