# POUR L'UTILISATEUR #

Cette application sert à générer, modifier, afficher des trajectoires.

Les trajectoires crées peuvent être sauvegardées dans un fichier, ou
affichées dans une fenêtre sur l'écran. Il y a deux formats le format
historique csv, et un format spécifique plus lisible. Cette même
application permet de traduire d'un format dans l'autre car elle
peut lire et écrire des fichiers des deux types.

D'autre applications de la suite permettent d'"exécuter" les trajectoires.

Une trajectoire est un ensemble de sections comme définies dans plasmaGui.
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
la zone d'entrée. Dans ce cas là un "ascenceur" apparaît qui permettent
d'ajuster la partie visible. Le nombre maximum de lignes est fixé dans le
source du programme, la valeur choisie est 200 (il y a des commentaires sur
ce point dans la section "sous le capot". Le nombre de lignes visibles
est implicitement fixé par la hauteur de la zone d'entrée. La taille des
fenêtres est fixe. 

Le bouton "*Add a line*" ajoute une ligne à la fin.

Le bouton "*Delete selected lines*" supprime les lignes sélectionnées (on peut
préferrer les déselectionner seulement qui permet de les remettre)

Le bouton "*Load*" permet de lire un fichier sur le disque, à l'un
deux formats possibles (le suffixe indique quel le format du fichier.

Le bouton "*Show/Save*" permet de visualiser la trajectoire avec, si
nécessaire, une image au nom non configurable "backgroundImage.jpg" 
comme fond. les coordonnées de la souris dans les unités physiques sont
montrées en permanence pour aider à remplir les paramètres des
sections.

Pour chaque ligne la dernière colonne permet de selectionner ou
déselectionner cette ligne. Les lignes non sélectionnées sont visibles
mais considérées comme absentes lorsque l'on dessine ou sauve la
trajectoire.

Pour chaque ligne l'avant dernière colonne permet d'éditer cette ligne.
"*Insert line above*" et "*Insert line below* " insère une ligne.
"*Copy line*" place la ligne dans le presse-papier. "*Paste line*"
remplace la ligne courrante par la ligne du presse-papier.
Quand un pop-up d'édition est activé les autres fenêtres sont
inactives, et il faut choisir une option du menu (par exemple *cancel*) pour
libérer l'interface graphique.

--------------------------------------------------------------
# POUR LES DEVELOPPEURS (SOUS LE CAPOT) #

Cette application nécessite python 3 et tkinter, différentes version
ont été testées avec succès. De plus le module PIL (testé avec version 10.2.0 et
10.3.0) est utile pour l'image de fond, mais n'est pas indispensable.

La classe trajMaker.trajMaker peut etre appelée sans parent ou avec un parent :
soit tk.Tk() soit un tk.Toplevel(). Si elle est appelée avec un
toplevel son layout DOIT etre pack(). Si elle appelée sans parent un
toplevel sera cree. Dans tous les cas myApp.parent sera accessible.

Au début du constructeur de la classe trajMaker.trajMaker il y a un
ensemble de paramètres que l'on peut modifier pour debugger plus
facilement ou pour changer l'aspect du GUI. Leurs noms sont explicites.

La classe trajMaker utilise des widgets ttk dès qu'ils existent:
ttk.Frame, ttk.Entry, ttk.Button, ttk.Combobox, ttk.Scrollbar,
ttk.Label, ttkCheckbutton (a travers jcCheckbutton))
et tk.Toplevel, tk.Canvas.

Il n'y a pas de redondance, c'est à dire que les paramètres sont
stockés directement dans les widget. C'est pourquoi j'ai introduit un
jcCheckButton, qui hérite de ttk.Checkbutton mais avec un membre de
plus qui est la valeur du bouton.

Flag utile pour debugger colorSpecialAsHelpToWork

La section *arc2* sens>0 clockwise sens<=0 anti-clockwise

Creation d'un nouveau type de troncon:
	rajouter une nouvelle entree dans Dico et Types, la nouvelle entrée sera proposée 
	dans "comboboxSelect()" rajouter le cas à traiter
	dans "processTraj()" traiter effectivement le cas
