from bs4 import BeautifulSoup
import requests

# fonction qui prend en paramètre une url et qui retourne le type de structure de la page

def check_structure(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # recuperer mw-content-text
    mw_content_text = soup.find("div", {"id": "mw-content-text"})
    
    if not mw_content_text:
        return {"error": "Contenu mw-content-text non trouvé"}
    
    # Analyser les classes répétées avec contenu variable
    repeated_classes = find_repeated_classes_with_variable_content(mw_content_text)
    
    # Enrichir avec les informations de parents communs
    enhanced_repeated_classes = enhance_repeated_classes_with_common_parents(repeated_classes)
    
    # Extraire le top 10 des classes les plus répétées (basé sur les données enrichies)
    top_repeated_classes = extract_top_repeated_classes_from_results(enhanced_repeated_classes, top_n=10)
    
    return {
        "repeated_classes": enhanced_repeated_classes,
        "top_repeated_classes": top_repeated_classes,
        "total_elements": len(mw_content_text.find_all()),
        "url": url
    }

def find_repeated_classes_with_variable_content(soup_element):
    """
    Trouve les éléments qui ont des classes répétées mais du contenu différent
    """
    # Dictionnaire pour stocker les classes et leurs éléments
    class_elements = {}
    
    # Parcourir tous les éléments avec des classes
    for element in soup_element.find_all(class_=True):
        # Obtenir les classes de l'élément
        classes = element.get('class')
        if not classes:
            continue
            
        # Convertir en tuple pour utiliser comme clé de dictionnaire
        class_key = tuple(sorted(classes))
        
        # Générer le sélecteur CSS pour cet élément
        css_selector = generate_css_selector(element)
        
        # Stocker les informations de l'élément
        element_info = {
            'tag': element.name,
            'text': element.get_text(strip=True),
            'html': str(element)[:200] + "..." if len(str(element)) > 200 else str(element),
            'attributes': dict(element.attrs),
            'css_selector': css_selector,
            'html_path': generate_html_path(element)
        }
        
        if class_key not in class_elements:
            class_elements[class_key] = []
        
        class_elements[class_key].append(element_info)
    
    # Identifier les classes répétées avec contenu variable
    repeated_with_variation = {}
    
    for class_key, elements in class_elements.items():
        if len(elements) > 1:  # Classe répétée
            # Vérifier si le contenu varie
            texts = [elem['text'] for elem in elements]
            unique_texts = set(texts)
            
            if len(unique_texts) > 1:  # Contenu variable
                repeated_with_variation[' '.join(class_key)] = {
                    'count': len(elements),
                    'unique_contents': len(unique_texts),
                    'elements': elements,
                    'sample_texts': list(unique_texts)[:5]  # Échantillon des 5 premiers textes uniques
                }
    
    return repeated_with_variation

def analyze_class_patterns(soup_element, min_occurrences=2, min_content_variation=2):
    """
    Analyse avancée des patterns de classes avec options de filtrage
    
    Args:
        soup_element: Élément BeautifulSoup à analyser
        min_occurrences: Nombre minimum d'occurrences pour considérer une classe
        min_content_variation: Nombre minimum de contenus différents requis
    
    Returns:
        dict: Analyse détaillée des patterns trouvés
    """
    repeated_classes = find_repeated_classes_with_variable_content(soup_element)
    
    # Filtrer selon les critères
    filtered_results = {}
    for class_name, info in repeated_classes.items():
        if (info['count'] >= min_occurrences and 
            info['unique_contents'] >= min_content_variation):
            
            # Ajouter des analyses supplémentaires
            elements = info['elements']
            
            # Analyser les balises utilisées
            tags_used = {}
            for elem in elements:
                tag = elem['tag']
                tags_used[tag] = tags_used.get(tag, 0) + 1
            
            # Analyser la longueur des contenus
            content_lengths = [len(elem['text']) for elem in elements]
            
            # Analyser les attributs communs
            common_attrs = set(elements[0]['attributes'].keys())
            for elem in elements[1:]:
                common_attrs &= set(elem['attributes'].keys())
            
            filtered_results[class_name] = {
                **info,
                'tags_distribution': tags_used,
                'content_length_stats': {
                    'min': min(content_lengths),
                    'max': max(content_lengths),
                    'avg': sum(content_lengths) / len(content_lengths)
                },
                'common_attributes': list(common_attrs),
                'pattern_type': classify_pattern(info)
            }
    
    return filtered_results

def classify_pattern(class_info):
    """
    Classifie le type de pattern basé sur les caractéristiques
    """
    count = class_info['count']
    unique_contents = class_info['unique_contents']
    
    if unique_contents == count:
        return "TOTALEMENT_VARIABLE"  # Chaque élément a un contenu unique
    elif unique_contents > count * 0.8:
        return "FORTEMENT_VARIABLE"   # Plus de 80% de contenus uniques
    elif unique_contents > count * 0.5:
        return "MOYENNEMENT_VARIABLE" # Plus de 50% de contenus uniques
    else:
        return "PARTIELLEMENT_VARIABLE" # Beaucoup de doublons dans le contenu

def export_results_to_dict(results, include_html=False):
    """
    Exporte les résultats dans un format plus compact pour sauvegarde/export
    """
    exported = {}
    for class_name, info in results.items():
        exported[class_name] = {
            'count': info['count'],
            'unique_contents': info['unique_contents'],
            'sample_texts': info['sample_texts'],
            'pattern_type': info.get('pattern_type', 'UNKNOWN')
        }
        
        if include_html:
            exported[class_name]['sample_html'] = [
                elem['html'] for elem in info['elements'][:3]
            ]
    
    return exported

def extract_top_repeated_classes_from_results(repeated_classes_data, top_n=10):
    """
    Extrait le top N des classes répétées à partir des résultats d'analyse
    
    Args:
        repeated_classes_data: Dictionnaire des classes répétées (résultat de find_repeated_classes_with_variable_content)
        top_n: Nombre de classes à retourner dans le top
    
    Returns:
        list: Liste des top classes avec leurs informations
    """
    if not repeated_classes_data:
        return []
    
    # Trier les classes par nombre d'occurrences (décroissant)
    sorted_classes = sorted(
        repeated_classes_data.items(), 
        key=lambda x: x[1]['count'], 
        reverse=True
    )
    
    # Créer le top N avec les informations importantes
    top_classes = []
    for i, (class_name, info) in enumerate(sorted_classes[:top_n]):
        # Extraire les sélecteurs uniques pour cette classe
        unique_selectors = get_unique_selectors_for_class(info['elements'])
        
        top_classes.append({
            'rank': i + 1,
            'class_name': class_name,
            'count': info['count'],
            'unique_contents': info['unique_contents'],
            'sample_texts': info['sample_texts'][:3],  # Premiers 3 exemples
            'variability_ratio': round(info['unique_contents'] / info['count'], 2),  # Ratio de variabilité
            'pattern_type': classify_pattern(info),
            'selectors': unique_selectors[:5],  # Top 5 des sélecteurs pour cette classe
            'all_selectors': unique_selectors,  # Tous les sélecteurs (pour usage avancé)
            'common_parent_info': info.get('common_parent_info', {})  # Informations du parent commun
        })
    
    return top_classes

def generate_css_selector(element):
    """
    Génère un sélecteur CSS pour un élément donné
    """
    selector_parts = []
    current = element
    
    while current and current.name:
        part = current.name
        
        # Ajouter l'ID s'il existe
        if current.get('id'):
            part += f"#{current.get('id')}"
            selector_parts.insert(0, part)
            break  # L'ID est unique, on peut s'arrêter là
        
        # Ajouter les classes
        if current.get('class'):
            classes = '.'.join(current.get('class'))
            part += f".{classes}"
        
        # Ajouter la position si nécessaire pour l'unicité
        siblings = [s for s in current.parent.children if s.name == current.name] if current.parent else [current]
        if len(siblings) > 1:
            try:
                position = siblings.index(current) + 1
                part += f":nth-of-type({position})"
            except ValueError:
                pass
        
        selector_parts.insert(0, part)
        current = current.parent
        
        # Limiter la profondeur pour éviter des sélecteurs trop longs
        if len(selector_parts) >= 6:
            break
    
    return ' > '.join(selector_parts) if selector_parts else element.name

def generate_html_path(element):
    """
    Génère le chemin HTML complet depuis la racine
    """
    path_parts = []
    current = element
    
    while current and current.name:
        part = current.name
        
        # Ajouter l'ID pour identification
        if current.get('id'):
            part += f"[@id='{current.get('id')}']"
        
        # Ajouter les classes principales
        if current.get('class'):
            main_classes = current.get('class')[:2]  # Prendre les 2 premières classes
            if main_classes:
                part += f"[@class*='{' '.join(main_classes)}']"
        
        # Ajouter la position dans les frères et sœurs
        if current.parent:
            siblings = [s for s in current.parent.children if s.name == current.name]
            if len(siblings) > 1:
                try:
                    position = siblings.index(current) + 1
                    part += f"[{position}]"
                except ValueError:
                    pass
        
        path_parts.insert(0, part)
        current = current.parent
        
        # Limiter la profondeur
        if len(path_parts) >= 8:
            break
    
    return '/' + '/'.join(path_parts) if path_parts else f"/{element.name}"

def get_unique_selectors_for_class(class_elements_list):
    """
    Retourne les sélecteurs CSS uniques pour une liste d'éléments de même classe
    """
    selectors = []
    for element_info in class_elements_list:
        selectors.append({
            'css_selector': element_info['css_selector'],
            'html_path': element_info['html_path'],
            'text_preview': element_info['text'][:50] + "..." if len(element_info['text']) > 50 else element_info['text']
        })
    return selectors

def find_common_parent_selector(css_selectors):
    """
    Trouve le sélecteur CSS du plus proche parent commun d'une liste de sélecteurs
    
    Args:
        css_selectors: Liste des sélecteurs CSS des éléments de même classe
    
    Returns:
        dict: Informations sur le parent commun
    """
    if not css_selectors or len(css_selectors) < 2:
        return {"common_parent": None, "reason": "Pas assez de sélecteurs"}
    
    # Parser chaque sélecteur en segments hiérarchiques
    parsed_selectors = []
    for selector in css_selectors:
        # Nettoyer et séparer par ' > '
        segments = [seg.strip() for seg in selector.split(' > ')]
        parsed_selectors.append(segments)
    
    if not parsed_selectors:
        return {"common_parent": None, "reason": "Aucun sélecteur valide"}
    
    # Trouver la longueur minimale pour éviter les index out of bounds
    min_length = min(len(segments) for segments in parsed_selectors)
    
    # Trouver le plus long préfixe commun
    common_segments = []
    for i in range(min_length):
        # Prendre le segment à la position i du premier sélecteur
        current_segment = parsed_selectors[0][i]
        
        # Vérifier si ce segment est identique dans tous les sélecteurs
        if all(segments[i] == current_segment for segments in parsed_selectors):
            common_segments.append(current_segment)
        else:
            break
    
    # Si on a au moins un segment commun, créer le sélecteur parent
    if common_segments:
        # Ne pas inclure le dernier segment car c'est probablement l'élément lui-même
        if len(common_segments) > 1:
            parent_segments = common_segments[:-1]
        else:
            parent_segments = common_segments
        
        common_parent_selector = ' > '.join(parent_segments)
        
        # Analyser la qualité du parent commun
        specificity_level = len(parent_segments)
        coverage_ratio = len(common_segments) / max(len(seg) for seg in parsed_selectors)
        
        return {
            "common_parent": common_parent_selector,
            "specificity_level": specificity_level,
            "coverage_ratio": round(coverage_ratio, 2),
            "common_depth": len(common_segments),
            "selectors_analyzed": len(css_selectors),
            "parent_type": classify_parent_type(common_parent_selector)
        }
    
    return {"common_parent": None, "reason": "Aucun parent commun trouvé"}

def classify_parent_type(parent_selector):
    """
    Classifie le type de parent commun basé sur son sélecteur
    """
    if not parent_selector:
        return "UNKNOWN"
    
    # Analyser le dernier segment du parent
    last_segment = parent_selector.split(' > ')[-1].lower()
    
    if 'nav' in last_segment or 'menu' in last_segment:
        return "NAVIGATION"
    elif 'list' in last_segment or 'ul' in last_segment or 'ol' in last_segment:
        return "LIST_CONTAINER"
    elif 'grid' in last_segment or 'row' in last_segment or 'col' in last_segment:
        return "GRID_CONTAINER"
    elif 'content' in last_segment or 'main' in last_segment:
        return "CONTENT_CONTAINER"
    elif 'header' in last_segment or 'footer' in last_segment:
        return "SECTION_CONTAINER"
    elif 'div' in last_segment:
        return "GENERIC_CONTAINER"
    else:
        return "SPECIALIZED_CONTAINER"

def enhance_repeated_classes_with_common_parents(repeated_classes_data):
    """
    Enrichit les données des classes répétées avec les informations de parents communs
    """
    enhanced_data = {}
    
    for class_name, info in repeated_classes_data.items():
        # Extraire les sélecteurs CSS de tous les éléments de cette classe
        css_selectors = [elem['css_selector'] for elem in info['elements']]
        
        # Trouver le parent commun
        common_parent_info = find_common_parent_selector(css_selectors)
        
        # Ajouter les informations du parent commun
        enhanced_info = {
            **info,
            'common_parent_info': common_parent_info
        }
        
        enhanced_data[class_name] = enhanced_info
    
    return enhanced_data

