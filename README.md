# Scrapeur Fandom Universel

Un outil puissant pour extraire et comparer les personnages de différents wikis Fandom.

## 🚀 Fonctionnalités

- **Scraping universel** : Compatible avec de nombreux sites Fandom (Elden Ring, The Witcher, Skyrim, etc.)
- **URLs personnalisées** : Entrez n'importe quelle URL Fandom pour scraper de nouveaux sites
- **Interface web intuitive** : Visualisation des personnages sous forme de cartes élégantes
- **Comparaison avancée** : Comparez plusieurs personnages côte à côte
- **Recherche et filtrage** : Trouvez rapidement les personnages qui vous intéressent
- **Sauvegarde JSON** : Les données sont sauvegardées pour une utilisation ultérieure
- **Responsive** : Interface adaptée à tous les appareils
- **Configuration intelligente** : Détection automatique des structures de pages

## 📦 Installation

1. **Clonez le dépôt** :
```bash
git clone <votre-repo>
cd fandom_scraper_v2
```

2. **Installez les dépendances** :
```bash
pip install -r requirements.txt
```

## 🎯 Utilisation

### Interface Web (Recommandé)

1. **Lancez l'application** :
```bash
python app.py
```

2. **Ouvrez votre navigateur** à l'adresse : `http://localhost:5000`

3. **Choisissez votre méthode** :
   - Sites prédéfinis : Sélectionnez dans la liste
   - URL personnalisée : Entrez n'importe quelle URL Fandom (ex: `https://pokemon.fandom.com`)

4. **Définissez le nombre de personnages** à scraper

5. **Visualisez les résultats** sous forme de cartes interactives

### Ligne de commande

```bash
python fandom_scraper.py <site_name> [max_characters]
```

**Exemples** :
```bash
# Sites prédéfinis
python fandom_scraper.py eldenring 30
python fandom_scraper.py witcher 20

# URLs personnalisées (via run.py)
python run.py
# Puis choisissez option 2 et entrez: https://pokemon.fandom.com
```

## 🎮 Sites Supportés

### Sites prédéfinis
| Site | URL | Caractéristiques extraites |
|------|-----|---------------------------|
| **Elden Ring** | eldenring.fandom.com | Nom, Image, Type, Lieu, Santé, Drops |
| **The Witcher** | witcher.fandom.com | Nom, Image, Profession, Race, Lieu |
| **Skyrim** | elderscrolls.fandom.com | Nom, Image, Race, Genre, Lieu, Classe |

### URLs personnalisées ✨
**Nouveauté !** Entrez n'importe quelle URL Fandom pour scraper automatiquement :
- `https://pokemon.fandom.com` - Pokémon et créatures
- `https://naruto.fandom.com` - Personnages de Naruto
- `https://marvel.fandom.com` - Héros et vilains Marvel
- `https://harrypotter.fandom.com` - Personnages d'Harry Potter
- `https://onepiece.fandom.com` - Pirates et personnages One Piece
- Et bien d'autres...

## 🔧 Configuration

### Ajouter un nouveau site

Modifiez le fichier `config.py` pour ajouter de nouveaux sites Fandom :

```python
"nouveau_site": {
    "base_url": "https://nouveau_site.fandom.com",
    "characters_category": "/wiki/Category:Characters",
    "character_selectors": {
        "name": "h1.page-header__title",
        "image": ".pi-image img",
        "infobox": ".portable-infobox",
        # Ajoutez d'autres sélecteurs selon vos besoins
    }
}
```

### Paramètres de scraping

- `MAX_CHARACTERS` : Limite par défaut du nombre de personnages
- `REQUEST_DELAY` : Délai entre les requêtes (en secondes)
- `TIMEOUT` : Timeout des requêtes HTTP

## 📊 Fonctionnalités de l'Interface Web

### Page d'accueil
- Sélection du site Fandom
- Configuration du nombre de personnages
- Lancement du scraping

### Progression en temps réel
- Barre de progression
- Statut actuel du scraping
- Mise à jour automatique

### Visualisation des personnages
- **Cartes interactives** avec images et informations
- **Recherche en temps réel**
- **Tri par attributs** (nom, type, lieu, etc.)
- **Sélection multiple** pour la comparaison

### Comparaison avancée
- **Vue côte à côte** des personnages sélectionnés
- **Tableau de comparaison** détaillé
- **Analyse automatique** des similitudes et différences
- **Codage couleur** pour identifier rapidement les patterns

## 🔍 Exemple d'utilisation

### Exemple 1 : Site prédéfini (Elden Ring)
1. **Scraper Elden Ring** :
   - Sélectionnez "Sites prédéfinis"
   - Choisissez "eldenring" dans la liste
   - Définissez 25 personnages et lancez

2. **Explorer les résultats** :
   - Parcourez les cartes de personnages
   - Utilisez la recherche pour trouver "Radahn"
   - Sélectionnez plusieurs boss pour les comparer

### Exemple 2 : URL personnalisée (Pokémon)
1. **Scraper Pokémon** :
   - Sélectionnez "URL personnalisée"
   - Entrez `https://pokemon.fandom.com`
   - L'outil complète automatiquement si vous tapez juste "pokemon"
   - Définissez 30 personnages et lancez

2. **Découvrir automatiquement** :
   - Le système détecte automatiquement la structure du site
   - Extrait les Pokémon avec leurs types, évolutions, etc.
   - Présente tout sous forme de cartes comparables

3. **Comparer des Pokémon** :
   - Sélectionnez Pikachu, Charizard, Blastoise
   - Cliquez sur "Comparer"
   - Analysez leurs différences de types et statistiques

## 📁 Structure du projet

```
fandom_scraper_v2/
├── app.py                 # Application Flask principale
├── fandom_scraper.py      # Module de scraping
├── config.py              # Configuration des sites
├── requirements.txt       # Dépendances Python
├── templates/             # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── progress.html
│   ├── character_cards.html
│   ├── character_comparison.html
│   └── character_files.html
└── static/               # Fichiers statiques
    ├── css/
    │   └── style.css
    └── js/
```

## 🛠️ Technologies utilisées

- **Backend** : Python, Flask, BeautifulSoup, Requests
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap 5
- **Parsing** : BeautifulSoup4, lxml
- **Interface** : Font Awesome pour les icônes

## ✨ URLs Personnalisées - Comment ça marche ?

### Fonctionnement intelligent
1. **Analyse automatique** : Le système analyse l'URL et extrait le nom du site
2. **Configuration générique** : Applique des sélecteurs CSS robustes qui fonctionnent sur la plupart des sites Fandom
3. **Détection adaptative** : Essaie plusieurs structures de pages pour trouver les personnages
4. **Extraction flexible** : Utilise des sélecteurs multiples pour s'adapter aux différentes mises en page

### Formats supportés
```bash
# Formats d'URL acceptés
https://pokemon.fandom.com
https://naruto.fandom.com/wiki/Main_Page
pokemon.fandom.com
naruto

# Auto-complétion intelligente
# Tapez juste "pokemon" → devient "https://pokemon.fandom.com"
```

### Que fait le système automatiquement ?
- 🔍 **Recherche de personnages** : Essaie `/wiki/Category:Characters`, puis d'autres catégories
- 🖼️ **Images** : Détecte automatiquement les images d'infobox ou de profil  
- 📊 **Données** : Extrait nom, description, et tous les attributs des infobox
- 🎯 **Nettoyage** : Filtre les pages non pertinentes et normalise les données

## ⚠️ Considérations importantes

### Respect des sites web
- Délai automatique entre les requêtes
- Headers User-Agent appropriés
- Limite raisonnable du nombre de personnages

### Performance
- Scraping en arrière-plan avec threading
- Mise en cache des résultats en JSON
- Interface responsive pour tous les appareils

### Robustesse
- Gestion des erreurs réseau
- Fallbacks pour les images manquantes  
- Validation des données extraites
- Détection automatique des structures de pages
- Sélecteurs CSS multiples pour compatibilité maximale

## 🐛 Résolution de problèmes

### Erreurs courantes

1. **"Site non supporté"** : Vérifiez que le site est dans `config.py`
2. **Images ne s'affichent pas** : Les URLs d'images peuvent être relatives
3. **Scraping lent** : Ajustez `REQUEST_DELAY` dans la configuration
4. **Données manquantes** : Les sélecteurs CSS peuvent avoir changé

### Debugging

Activez les logs détaillés :
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour ajouter un nouveau site :

1. Ajoutez la configuration dans `config.py`
2. Testez avec quelques personnages
3. Vérifiez la compatibilité de l'interface web
4. Documentez les spécificités du site

## 📝 Licence

Ce projet est créé à des fins éducatives. Respectez les conditions d'utilisation des sites Fandom.

## 🚀 Prochaines fonctionnalités

- [ ] Export des comparaisons en PDF
- [ ] Graphiques de statistiques
- [ ] API REST pour intégrations
- [ ] Support de plus de sites Fandom
- [ ] Système de favoris
- [ ] Mode sombre