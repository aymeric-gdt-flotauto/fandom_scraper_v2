"""
Application Flask pour l'interface web du scrapeur Fandom
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
from urllib.parse import urlparse
from fandom_scraper import FandomScraper
from config import FANDOM_SITES
import threading
import time

app = Flask(__name__)
app.secret_key = 'fandom_scraper_secret_key'

# Variables globales pour le statut du scraping
scraping_status = {
    'is_running': False,
    'progress': 0,
    'total': 0,
    'current_character': '',
    'site': ''
}

@app.route('/')
def index():
    """Page d'accueil avec la liste des sites disponibles"""
    return render_template('index.html', sites=FANDOM_SITES.keys())

@app.route('/scrape', methods=['POST'])
def start_scraping():
    """Démarre le scraping d'un site"""
    input_type = request.form.get('input_type', 'preset')
    max_characters = int(request.form.get('max_characters', 20))
    
    if input_type == 'preset':
        site_name = request.form.get('site')
        if not site_name or site_name not in FANDOM_SITES:
            flash('Site invalide sélectionné', 'error')
            return redirect(url_for('index'))
        site_config = None
    else:  # custom URL
        custom_url = request.form.get('custom_site_url', '').strip()
        if not custom_url:
            flash('URL personnalisée requise', 'error')
            return redirect(url_for('index'))
        
        if 'fandom.com' not in custom_url.lower():
            flash('URL doit être un site Fandom valide', 'error')
            return redirect(url_for('index'))
        
        # Analyser l'URL personnalisée
        site_name, site_config = parse_custom_fandom_url(custom_url)
        if not site_name:
            flash('Impossible d\'analyser l\'URL fournie', 'error')
            return redirect(url_for('index'))
    
    if scraping_status['is_running']:
        flash('Un scraping est déjà en cours', 'warning')
        return redirect(url_for('index'))
    
    # Démarrer le scraping en arrière-plan
    thread = threading.Thread(target=run_scraping, args=(site_name, max_characters, site_config))
    thread.daemon = True
    thread.start()
    
    flash(f'Scraping de {site_name} démarré...', 'info')
    return redirect(url_for('scraping_progress'))

def parse_custom_fandom_url(url: str):
    """
    Analyse une URL Fandom personnalisée et crée une configuration dynamique
    
    Args:
        url: URL du site Fandom (ex: https://pokemon.fandom.com)
    
    Returns:
        tuple: (site_name, site_config) ou (None, None) si erreur
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if not domain.endswith('.fandom.com'):
            return None, None
        
        # Extraire le nom du site (ex: "pokemon" de "pokemon.fandom.com")
        site_name = domain.replace('.fandom.com', '')
        base_url = f"https://{domain}"
        
        # Configuration générique pour sites Fandom
        site_config = {
            "base_url": base_url,
            "characters_category": "/wiki/Category:Characters",
            "character_selectors": {
                "name": "h1.page-header__title, h1#firstHeading, .page-header__title",
                "image": ".pi-image img, .infobox img, .portable-infobox img",
                "infobox": ".portable-infobox, .infobox",
                "description": ".mw-parser-output > p:first-of-type, .mw-content-text > p:first-of-type",
                "stats": ".pi-data, .infobox-data",
                # Sélecteurs génériques pour différents attributs
                "type": "[data-source='type'] .pi-data-value, [data-source='species'] .pi-data-value",
                "location": "[data-source='location'] .pi-data-value, [data-source='habitat'] .pi-data-value",
                "health": "[data-source='health'] .pi-data-value, [data-source='hp'] .pi-data-value",
                "level": "[data-source='level'] .pi-data-value",
                "race": "[data-source='race'] .pi-data-value",
                "class": "[data-source='class'] .pi-data-value",
                "profession": "[data-source='profession'] .pi-data-value",
                "gender": "[data-source='gender'] .pi-data-value",
                "age": "[data-source='age'] .pi-data-value",
                "status": "[data-source='status'] .pi-data-value"
            }
        }
        
        return site_name, site_config
        
    except Exception as e:
        print(f"Erreur lors de l'analyse de l'URL: {e}")
        return None, None

def run_scraping(site_name: str, max_characters: int, site_config: dict = None):
    """Exécute le scraping en arrière-plan"""
    global scraping_status
    
    scraping_status.update({
        'is_running': True,
        'progress': 0,
        'total': max_characters,
        'current_character': 'Initialisation...',
        'site': site_name
    })
    
    try:
        # Créer le scrapeur avec configuration personnalisée si fournie
        if site_config:
            scraper = FandomScraper(site_name, custom_config=site_config)
        else:
            scraper = FandomScraper(site_name)
        
        # Récupérer la liste des personnages
        scraping_status['current_character'] = 'Récupération de la liste des personnages...'
        character_urls = scraper.get_characters_list(max_characters)
        scraping_status['total'] = len(character_urls)
        
        characters_data = []
        
        for i, url in enumerate(character_urls, 1):
            scraping_status['progress'] = i
            scraping_status['current_character'] = f'Personnage {i}/{len(character_urls)}'
            
            character_data = scraper.extract_character_data(url)
            if character_data:
                characters_data.append(character_data)
            
            time.sleep(1)  # Pause entre les requêtes
        
        # Sauvegarder les données
        filename = scraper.save_to_json(characters_data)
        scraping_status['current_character'] = f'Terminé! {len(characters_data)} personnages sauvegardés'
        
    except Exception as e:
        scraping_status['current_character'] = f'Erreur: {str(e)}'
    finally:
        scraping_status['is_running'] = False

@app.route('/progress')
def scraping_progress():
    """Page de progression du scraping"""
    return render_template('progress.html', status=scraping_status)

@app.route('/api/progress')
def api_progress():
    """API pour récupérer le statut du scraping"""
    return jsonify(scraping_status)

@app.route('/characters')
def view_characters():
    """Affiche la liste des fichiers de personnages disponibles"""
    json_files = [f for f in os.listdir('.') if f.endswith('_characters.json')]
    return render_template('character_files.html', files=json_files)

@app.route('/characters/<filename>')
def display_characters(filename):
    """Affiche les personnages d'un fichier JSON sous forme de cartes"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            characters = json.load(f)
        
        site_name = filename.replace('_characters.json', '')
        return render_template('character_cards.html', 
                             characters=characters, 
                             site_name=site_name,
                             filename=filename)
    except FileNotFoundError:
        flash('Fichier non trouvé', 'error')
        return redirect(url_for('view_characters'))
    except json.JSONDecodeError:
        flash('Erreur de lecture du fichier JSON', 'error')
        return redirect(url_for('view_characters'))

@app.route('/compare')
def compare_characters():
    """Page de comparaison des personnages"""
    filename = request.args.get('file')
    selected_ids = request.args.getlist('characters')
    
    if not filename or not selected_ids:
        flash('Paramètres de comparaison manquants', 'error')
        return redirect(url_for('view_characters'))
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            all_characters = json.load(f)
        
        # Filtrer les personnages sélectionnés
        selected_characters = []
        for i, char in enumerate(all_characters):
            if str(i) in selected_ids:
                selected_characters.append(char)
        
        if len(selected_characters) < 2:
            flash('Sélectionnez au moins 2 personnages pour la comparaison', 'warning')
            return redirect(url_for('display_characters', filename=filename))
        
        return render_template('character_comparison.html', 
                             characters=selected_characters,
                             filename=filename)
        
    except FileNotFoundError:
        flash('Fichier non trouvé', 'error')
        return redirect(url_for('view_characters'))

@app.route('/api/characters/<filename>')
def api_characters(filename):
    """API pour récupérer les données des personnages"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            characters = json.load(f)
        return jsonify(characters)
    except FileNotFoundError:
        return jsonify({'error': 'Fichier non trouvé'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)