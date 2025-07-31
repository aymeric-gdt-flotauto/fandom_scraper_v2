#!/usr/bin/env python3
"""
Script de démarrage simple pour le scrapeur Fandom
"""

import sys
import os

def main():
    print("🕷️  Scrapeur Fandom Universel")
    print("=" * 40)
    print()
    
    # Vérifier que les dépendances sont installées
    try:
        import flask
        import requests
        import bs4
        print("✅ Dépendances vérifiées")
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("Installez les dépendances avec: pip install -r requirements.txt")
        return
    
    # Afficher les options
    print("Choisissez une option:")
    print("1. Lancer l'interface web (recommandé)")
    print("2. Scraping en ligne de commande")
    print("3. Quitter")
    print()
    
    try:
        choice = input("Votre choix (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 Lancement de l'interface web...")
            print("Ouvrez votre navigateur à l'adresse: http://localhost:5000")
            print("Appuyez sur Ctrl+C pour arrêter\n")
            
            from app import app
            app.run(debug=False, host='0.0.0.0', port=5000)
            
        elif choice == "2":
            print("\n🤖 Mode ligne de commande")
            print("Sites disponibles: eldenring, witcher, skyrim")
            print("Ou entrez une URL Fandom personnalisée")
            
            site_input = input("Site ou URL à scraper: ").strip()
            if not site_input:
                print("Site ou URL requis")
                return
                
            max_chars = input("Nombre de personnages (défaut: 20): ").strip()
            max_chars = int(max_chars) if max_chars.isdigit() else 20
            
            from fandom_scraper import FandomScraper
            
            # Vérifier si c'est une URL ou un nom de site
            if 'fandom.com' in site_input.lower():
                # C'est une URL personnalisée
                from urllib.parse import urlparse
                
                parsed = urlparse(site_input)
                domain = parsed.netloc.lower()
                
                if not domain.endswith('.fandom.com'):
                    print("❌ URL doit être un site Fandom valide")
                    return
                
                site_name = domain.replace('.fandom.com', '')
                base_url = f"https://{domain}"
                
                # Configuration générique
                site_config = {
                    "base_url": base_url,
                    "characters_category": "/wiki/Category:Characters",
                    "character_selectors": {
                        "name": "h1.page-header__title, h1#firstHeading, .page-header__title",
                        "image": ".pi-image img, .infobox img, .portable-infobox img",
                        "infobox": ".portable-infobox, .infobox",
                        "description": ".mw-parser-output > p:first-of-type, .mw-content-text > p:first-of-type",
                        "stats": ".pi-data, .infobox-data",
                        "type": "[data-source='type'] .pi-data-value, [data-source='species'] .pi-data-value",
                        "location": "[data-source='location'] .pi-data-value, [data-source='habitat'] .pi-data-value",
                        "health": "[data-source='health'] .pi-data-value, [data-source='hp'] .pi-data-value"
                    }
                }
                
                print(f"\n🔍 Scraping de {site_name} depuis {base_url} ({max_chars} personnages)...")
                
                try:
                    scraper = FandomScraper(site_name, custom_config=site_config)
                    characters = scraper.scrape_characters(max_chars)
                    filename = scraper.save_to_json(characters)
                    print(f"\n✅ Terminé! {len(characters)} personnages sauvegardés dans {filename}")
                except Exception as e:
                    print(f"❌ Erreur: {e}")
                    
            else:
                # C'est un nom de site prédéfini
                site = site_input.lower()
                print(f"\n🔍 Scraping de {site} ({max_chars} personnages)...")
                
                try:
                    scraper = FandomScraper(site)
                    characters = scraper.scrape_characters(max_chars)
                    filename = scraper.save_to_json(characters)
                    print(f"\n✅ Terminé! {len(characters)} personnages sauvegardés dans {filename}")
                except ValueError as e:
                    print(f"❌ Erreur: {e}")
                except Exception as e:
                    print(f"❌ Erreur inattendue: {e}")
                
        elif choice == "3":
            print("👋 Au revoir!")
            return
            
        else:
            print("❌ Choix invalide")
            
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()