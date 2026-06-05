# Projet E-Santé
### Auteurs : DURAND Cem, LEROY Simon, ROY Jules
---

Ce projet est basé sur PyQt6 et suit l'architecture MVC (Modèle-Vue-Contrôleur). Il est nécessaire d'avoir Python **3.9 ou plus** (**3.12** recommandé) pour faire fonctionner PyQt6.

Extensions recommandées pour le développement :
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) : pour le support de Python dans Visual Studio Code.
- [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) : pour l'autocomplétion.
- [Qt for Python](https://marketplace.visualstudio.com/items?itemName=seanwu.vscode-qt-for-python) : pour le support de PyQt dans Visual Studio Code.

## 1. Utilisation de venv :

NB : se placer à chaque fois dans le dossier du projet avant de lancer les commandes suivantes.

**Windows** :  
1. Créer l'environnement et installer les dépendances :
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

2. L'activer (à chaque fois qu'on veut travailler sur le projet) :
```bash
.\venv\Scripts\activate
```

**MacOS/Linux** :
1. Créer l'environnement et installer les dépendances :
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

2. L'activer (à chaque fois qu'on veut travailler sur le projet) :
```bash
source venv/bin/activate
```

## 2. Lancement de l'application :

Windows :
```bash
python main.py
```

MacOS/Linux :
```bash
python3 main.py
```

## 3. Structure du projet :

On suit une architecture MVC, ce qui signifie que le projet est organisé en trois parties principales : le modèle (Model), la vue (View) et le contrôleur (Controller).
- `Model` : gère les données et la logique métier de l'application.
- `View` : gère l'interface utilisateur et l'affichage des données.
- `Controller` : fait le lien entre le modèle et la vue, en répondant aux actions de l'utilisateur et en mettant à jour le modèle et la vue en conséquence.

Voici la structure des fichiers du projet :
- `requirements.txt` : liste des dépendances nécessaires pour faire fonctionner l'application.
- `pyproject.toml` : fichier de configuration pour la gestion des dépendances et des scripts.
- `main.py` : point d'entrée de l'application, où on initialise le modèle, la vue et le contrôleur, et où on lance la boucle d'exécution de l'application.
- `models/` : contient les classes des modèles, qui gèrent les données de l'application (dans notre cas, un simple compteur).
- `views/` : contient les classes des vues, qui gèrent l'interface utilisateur (les boutons, les labels, etc.).
- `controllers/` : contient les classes des contrôleurs, qui font le lien entre le modèle et la vue, en répondant aux actions de l'utilisateur (clics sur les boutons) et en mettant à jour le modèle et la vue en conséquence.
- `assets/` : dossier qui peut contenir des ressources supplémentaires pour l'application (images, fichiers de style, etc...).
- `docs/` : contient la documentation du projet

## 4. Documentation :

La documentation est générée par `pdoc`, et se trouve dans le dossier `docs/`. Elle peut être consultée en ouvrant le fichier `index.html` dans un navigateur web.  

Pour écrire de la documentation, il suffit d'ajouter des docstrings dans les classes et les fonctions du projet.  
Exemple :
```python
class CompteurModel:
    """
    Modèle de compteur.
    """

    def __init__(self):
        """
        Initialise le compteur à 0.
        """
        self.counter = 0

    def increment(self):
        """
        Incrémente le compteur de 1.
        """
        self.counter += 1
```

Pour la générer, il faut lancer la commande suivante :
```bash
pdoc ./models ./views ./controllers -o ./docs
```

## 5. Formatter le code :

Pour formatter le code on utilise `black`, il suffit de lancer la commande suivante dans le terminal à la racine du projet :
```bash
black .
```

## 6. Tester le code :
Pour tester le code, on utilise `pytest`, il suffit de lancer la commande suivante dans le terminal à la racine du projet :
```bash
pytest
```