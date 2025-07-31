"""
Scrapeur universel pour les sites Fandom
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import logging
from urllib.parse import urljoin, urlparse
from config import FANDOM_SITES, DEFAULT_HEADERS, REQUEST_DELAY, TIMEOUT
from typing import Dict, List, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FandomScraper:
    def __init__(self, site_name: str, custom_config: Dict = None):
        """
        Initialise le scrapeur pour un site Fandom spécifique
        
        Args:
            site_name: Nom du site (ex: 'eldenring', 'witcher', 'skyrim')
            custom_config: Configuration personnalisée pour sites non prédéfinis
        """
        self.site_name = site_name
        
        if custom_config:
            # Utiliser la configuration personnalisée
            self.config = custom_config
            logger.info(f"Utilisation de la configuration personnalisée pour {site_name}")
        elif site_name in FANDOM_SITES:
            # Utiliser la configuration prédéfinie
            self.config = FANDOM_SITES[site_name]
            logger.info(f"Utilisation de la configuration prédéfinie pour {site_name}")
        else:
            raise ValueError(f"Site '{site_name}' non supporté et aucune configuration personnalisée fournie. Sites disponibles: {list(FANDOM_SITES.keys())}")
        
        self.base_url = self.config["base_url"]
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Récupère et parse une page web
        
        Args:
            url: URL de la page à récupérer
            
        Returns:
            BeautifulSoup object ou None si erreur
        """
        try:
            logger.info(f"Récupération de: {url}")
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération de {url}: {e}")
            return None
    
    def get_characters_list(self, max_characters: int = 50) -> List[str]:
        """
        Récupère la liste des URLs de personnages depuis la page catégorie
        
        Args:
            max_characters: Nombre maximum de personnages à récupérer
            
        Returns:
            Liste des URLs de personnages
        """
        character_urls = []
        
        # Essayer différentes pages de catégories possibles
        category_urls = [
            self.config["characters_category"],
            "/wiki/Category:Characters",
            "/wiki/Category:Character",
            "/wiki/Category:People",
            "/wiki/Category:Individuals",
            "/wiki/Special:AllPages"  # Derniers recours
        ]
        
        for category_path in category_urls:
            if len(character_urls) >= max_characters:
                break
                
            category_url = urljoin(self.base_url, category_path)
            logger.info(f"Tentative de récupération depuis: {category_url}")
            soup = self.get_page(category_url)
            
            if not soup:
                continue
            
            # Chercher les liens vers les personnages
            character_links = soup.find_all('a', href=True)
            
            for link in character_links:
                href = link.get('href', '')
                
                # Filtrer les liens qui semblent être des personnages
                if (href.startswith('/wiki/') and 
                    not self._is_excluded_page(href)):
                    
                    full_url = urljoin(self.base_url, href)
                    if full_url not in character_urls:
                        character_urls.append(full_url)
                        
                    if len(character_urls) >= max_characters:
                        break
            
            # Si on a trouvé des personnages, pas besoin d'essayer d'autres catégories
            if character_urls:
                logger.info(f"Trouvé {len(character_urls)} personnages depuis {category_path}")
                break
        
        if not character_urls:
            logger.warning(f"Aucun personnage trouvé pour {self.site_name}")
        else:
            logger.info(f"Total: {len(character_urls)} personnages pour {self.site_name}")
        
        return character_urls[:max_characters]
    
    def _is_excluded_page(self, href: str) -> bool:
        """
        Vérifie si une page doit être exclue de la liste des personnages
        
        Args:
            href: URL relative de la page
            
        Returns:
            True si la page doit être exclue
        """
        excluded_patterns = [
            '/wiki/Category:',
            '/wiki/File:',
            '/wiki/Template:',
            '/wiki/Special:',
            '/wiki/Help:',
            '/wiki/User:',
            '/wiki/Talk:',
            '/wiki/Main_Page',
            '/wiki/List_of_',
            '/wiki/Gallery',
            ':Talk',
            ':User',
            ':File',
            ':Category'
        ]
        
        href_lower = href.lower()
        return any(pattern.lower() in href_lower for pattern in excluded_patterns)
    
    def extract_character_data(self, character_url: str) -> Dict:
        """
        Extrait les données d'un personnage depuis sa page
        
        Args:
            character_url: URL de la page du personnage
            
        Returns:
            Dictionnaire contenant les données du personnage
        """
        soup = self.get_page(character_url)
        if not soup:
            return {}
        
        character_data = {
            'url': character_url,
            'site': self.site_name
        }
        
        selectors = self.config["character_selectors"]
        
        # Extraire le nom avec plusieurs sélecteurs possibles
        name_element = self._find_element_with_selectors(soup, selectors["name"])
        character_data['name'] = name_element.get_text(strip=True) if name_element else "Nom inconnu"
        
        # Extraire l'image avec plusieurs sélecteurs possibles
        img_element = self._find_element_with_selectors(soup, selectors["image"])
        if img_element:
            img_src = (img_element.get('src') or 
                      img_element.get('data-src') or 
                      img_element.get('data-image-key') or
                      img_element.get('data-original'))
            if img_src:
                # Nettoyer l'URL de l'image (supprimer les paramètres de redimensionnement)
                if '/revision/' in img_src:
                    img_src = img_src.split('/revision/')[0]
                character_data['image'] = urljoin(self.base_url, img_src)
        
        # Extraire la description avec plusieurs sélecteurs possibles
        desc_element = self._find_element_with_selectors(soup, selectors["description"])
        if desc_element:
            description = desc_element.get_text(strip=True)
            # Limiter la longueur de la description
            if len(description) > 500:
                description = description[:500] + "..."
            character_data['description'] = description
        
        # Extraire les données de l'infobox
        infobox = self._find_element_with_selectors(soup, selectors["infobox"])
        if infobox:
            self._extract_infobox_data(infobox, character_data)
        
        # Extraire des champs spécifiques selon le site
        for field, selector in selectors.items():
            if field not in ['name', 'image', 'description', 'infobox', 'stats']:
                element = self._find_element_with_selectors(soup, selector)
                if element:
                    value = element.get_text(strip=True)
                    if value and value.lower() not in ['unknown', 'n/a', '-', '?']:
                        character_data[field] = value
        
        logger.info(f"Données extraites pour: {character_data.get('name', 'Inconnu')}")
        return character_data
    
    def _find_element_with_selectors(self, soup: BeautifulSoup, selectors: str):
        """
        Essaie plusieurs sélecteurs CSS séparés par des virgules
        
        Args:
            soup: Objet BeautifulSoup de la page
            selectors: Sélecteurs CSS séparés par des virgules
            
        Returns:
            Premier élément trouvé ou None
        """
        if not selectors:
            return None
            
        selector_list = [s.strip() for s in selectors.split(',')]
        
        for selector in selector_list:
            try:
                element = soup.select_one(selector)
                if element:
                    return element
            except Exception as e:
                logger.debug(f"Erreur avec le sélecteur '{selector}': {e}")
                continue
        
        return None
    
    def _extract_infobox_data(self, infobox, character_data: Dict):
        """
        Extrait les données d'une infobox Fandom
        
        Args:
            infobox: Élément HTML de l'infobox
            character_data: Dictionnaire à remplir avec les données
        """
        # Essayer différents sélecteurs pour les données d'infobox
        data_selectors = [
            '.pi-data',           # Portable Infobox
            '.infobox-data',      # Infobox classique
            'tr',                 # Lignes de tableau
            '.data'               # Autre format possible
        ]
        
        for selector in data_selectors:
            data_elements = infobox.select(selector)
            if data_elements:
                break
        
        for element in data_elements:
            # Essayer différents formats de label/valeur
            label_elem = (element.select_one('.pi-data-label') or 
                         element.select_one('.infobox-label') or 
                         element.select_one('th') or
                         element.select_one('.label'))
            
            value_elem = (element.select_one('.pi-data-value') or 
                         element.select_one('.infobox-data') or 
                         element.select_one('td') or
                         element.select_one('.value'))
            
            if label_elem and value_elem:
                label = label_elem.get_text(strip=True).lower()
                value = value_elem.get_text(strip=True)
                
                # Nettoyer et normaliser le label
                label = label.replace(':', '').replace(' ', '_')
                
                # Filtrer les valeurs vides ou inutiles
                if (value and 
                    value.lower() not in ['unknown', 'n/a', '-', '?', 'none', 'null'] and
                    len(value.strip()) > 0):
                    character_data[label] = value
    
    def scrape_characters(self, max_characters: int = 50) -> List[Dict]:
        """
        Scrape tous les personnages du site
        
        Args:
            max_characters: Nombre maximum de personnages à scraper
            
        Returns:
            Liste des données de personnages
        """
        logger.info(f"Début du scraping pour {self.site_name}")
        
        character_urls = self.get_characters_list(max_characters)
        characters_data = []
        
        for i, url in enumerate(character_urls, 1):
            logger.info(f"Scraping personnage {i}/{len(character_urls)}")
            
            character_data = self.extract_character_data(url)
            if character_data:
                characters_data.append(character_data)
            
            # Pause entre les requêtes pour éviter de surcharger le serveur
            time.sleep(REQUEST_DELAY)
        
        logger.info(f"Scraping terminé. {len(characters_data)} personnages récupérés.")
        return characters_data
    
    def save_to_json(self, characters_data: List[Dict], filename: str = None) -> str:
        """
        Sauvegarde les données en JSON
        
        Args:
            characters_data: Données des personnages
            filename: Nom du fichier (optionnel)
            
        Returns:
            Nom du fichier créé
        """
        if not filename:
            filename = f"{self.site_name}_characters.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(characters_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Données sauvegardées dans {filename}")
        return filename

def main():
    """Fonction principale pour tester le scrapeur"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fandom_scraper.py <site_name> [max_characters]")
        print(f"Sites disponibles: {list(FANDOM_SITES.keys())}")
        return
    
    site_name = sys.argv[1]
    max_characters = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    try:
        scraper = FandomScraper(site_name)
        characters = scraper.scrape_characters(max_characters)
        filename = scraper.save_to_json(characters)
        print(f"Scraping terminé! {len(characters)} personnages sauvegardés dans {filename}")
    except Exception as e:
        logger.error(f"Erreur: {e}")

if __name__ == "__main__":
    main()