"""
Configuration pour les différents sites Fandom
"""

FANDOM_SITES = {
    "eldenring": {
        "base_url": "https://eldenring.fandom.com",
        "characters_category": "/wiki/Category:Characters",
        "character_selectors": {
            "name": "h1.page-header__title",
            "image": ".pi-image img",
            "infobox": ".portable-infobox",
            "description": ".mw-parser-output > p:first-of-type",
            "stats": ".pi-data",
            "location": "[data-source='location'] .pi-data-value",
            "type": "[data-source='type'] .pi-data-value",
            "health": "[data-source='health'] .pi-data-value",
            "drops": "[data-source='drops'] .pi-data-value"
        }
    },
    "witcher": {
        "base_url": "https://witcher.fandom.com",
        "characters_category": "/wiki/Category:Characters",
        "character_selectors": {
            "name": "h1.page-header__title",
            "image": ".pi-image img",
            "infobox": ".portable-infobox",
            "description": ".mw-parser-output > p:first-of-type",
            "stats": ".pi-data",
            "profession": "[data-source='profession'] .pi-data-value",
            "race": "[data-source='race'] .pi-data-value",
            "location": "[data-source='location'] .pi-data-value"
        }
    },
    "skyrim": {
        "base_url": "https://elderscrolls.fandom.com",
        "characters_category": "/wiki/Category:Skyrim:_Characters",
        "character_selectors": {
            "name": "h1.page-header__title",
            "image": ".pi-image img",
            "infobox": ".portable-infobox",
            "description": ".mw-parser-output > p:first-of-type",
            "stats": ".pi-data",
            "race": "[data-source='race'] .pi-data-value",
            "gender": "[data-source='gender'] .pi-data-value",
            "location": "[data-source='location'] .pi-data-value",
            "class": "[data-source='class'] .pi-data-value"
        }
    }
}

# Configuration générale
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Paramètres de scraping
MAX_CHARACTERS = 50  # Limite par défaut
REQUEST_DELAY = 1  # Délai entre les requêtes en secondes
TIMEOUT = 30  # Timeout des requêtes