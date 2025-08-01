from struct_checker import check_structure, find_repeated_classes_with_variable_content
from bs4 import BeautifulSoup
import requests
from pprint import pprint

# Test direct avec une URL
url = "https://genshin-impact.fandom.com/fr/wiki/Accueil"

print("=== ANALYSE DES CLASSES RÉPÉTÉES AVEC CONTENU VARIABLE ===")
print(f"URL analysée : {url}")
print()

# Analyser la structure de la page
structure_info = check_structure(url)

if "error" in structure_info:
    print(f"Erreur : {structure_info['error']}")
else:
    print(f"Nombre total d'éléments analysés : {structure_info['total_elements']}")
    print(f"Nombre de classes répétées avec contenu variable : {len(structure_info['repeated_classes'])}")
    print()
    
    # Afficher le TOP 10 des classes les plus répétées
    print("🏆 TOP 10 DES CLASSES LES PLUS RÉPÉTÉES")
    print("=" * 60)
    
    if structure_info['top_repeated_classes']:
        for top_class in structure_info['top_repeated_classes']:
            print(f"#{top_class['rank']} - {top_class['class_name']}")
            print(f"   📊 {top_class['count']} occurrences | {top_class['unique_contents']} contenus uniques")
            print(f"   🔀 Variabilité: {top_class['variability_ratio']} | Type: {top_class['pattern_type']}")
            
            # Afficher les informations du parent commun
            if top_class['common_parent_info'] and top_class['common_parent_info'].get('common_parent'):
                parent_info = top_class['common_parent_info']
                print(f"   🏠 Parent commun: {parent_info['common_parent']}")
                print(f"      Type: {parent_info['parent_type']} | Spécificité: {parent_info['specificity_level']} | Couverture: {parent_info['coverage_ratio']}")
            
            # Afficher les sélecteurs CSS (version condensée)
            if top_class['selectors']:
                print(f"   🎯 Premiers sélecteurs ({len(top_class['selectors'])} total):")
                for j, selector_info in enumerate(top_class['selectors'][:2], 1):
                    short_selector = selector_info['css_selector']
                    if len(short_selector) > 60:
                        short_selector = "..." + short_selector[-57:]
                    print(f"      {j}. {short_selector}")
            
            if top_class['sample_texts']:
                sample = top_class['sample_texts'][0][:80] + "..." if len(top_class['sample_texts'][0]) > 80 else top_class['sample_texts'][0]
                print(f"   💬 Exemple: \"{sample}\"")
            print()
    else:
        print("Aucune classe répétée trouvée.")
    
    print("=" * 60)
    print(f"\n📋 DÉTAILS DES {min(5, len(structure_info['repeated_classes']))} PREMIÈRES CLASSES")
    print("-" * 60)
    
    # Afficher les détails des 5 premières classes seulement
    for i, (class_name, info) in enumerate(list(structure_info['repeated_classes'].items())[:5]):
        print(f"🔍 CLASSE #{i+1} : {class_name}")
        print(f"  - Nombre d'occurrences : {info['count']}")
        print(f"  - Nombre de contenus uniques : {info['unique_contents']}")
        print(f"  - Exemples de textes :")
        for j, sample_text in enumerate(info['sample_texts'][:3], 1):
            preview = sample_text[:100] + "..." if len(sample_text) > 100 else sample_text
            print(f"    {j}. \"{preview}\"")
        print()
        
        # Afficher les informations du parent commun
        if info.get('common_parent_info') and info['common_parent_info'].get('common_parent'):
            parent_info = info['common_parent_info']
            print(f"  🏠 PARENT COMMUN :")
            print(f"    Sélecteur: {parent_info['common_parent']}")
            print(f"    Type: {parent_info['parent_type']}")
            print(f"    Spécificité: {parent_info['specificity_level']} | Couverture: {parent_info['coverage_ratio']}")
            print(f"    Éléments analysés: {parent_info['selectors_analyzed']}")
        
        # Afficher le premier élément complet pour référence
        if info['elements']:
            first_element = info['elements'][0]
            print(f"  - Exemple d'élément (balise {first_element['tag']}) :")
            print(f"    HTML: {first_element['html']}")
            print(f"    🎯 Sélecteur CSS: {first_element['css_selector']}")
            print(f"    📍 Chemin HTML: {first_element['html_path']}")
        print("-" * 80)

# Test avec analyse locale si vous avez un fichier HTML local
print("\n=== TEST AVEC FICHIER LOCAL (si disponible) ===")
try:
    with open('test.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    local_results = find_repeated_classes_with_variable_content(soup)
    
    print(f"Fichier test.html analysé")
    print(f"Classes répétées avec contenu variable trouvées : {len(local_results)}")
    
    for class_name, info in list(local_results.items())[:3]:  # Afficher seulement les 3 premiers
        print(f"\n🔍 CLASSE LOCALE : {class_name}")
        print(f"  - Occurrences : {info['count']}")
        print(f"  - Contenus uniques : {info['unique_contents']}")
        
except FileNotFoundError:
    print("Fichier test.html non trouvé - test local ignoré")
except Exception as e:
    print(f"Erreur lors de l'analyse du fichier local : {e}")
