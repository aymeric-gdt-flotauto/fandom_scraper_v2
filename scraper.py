from bs4 import BeautifulSoup
import requests
import re
from pprint import pprint
from struct_checker import check_structure
import json

url = "https://genshin-impact.fandom.com/fr/wiki/Accueil"

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

# recuperer <nav class="fandom-community-header__local-navigation">
nav = soup.find("nav", class_="fandom-community-header__local-navigation")

# recuperer toutes les balises a qui contiennent "data-tracking="custom-level-X"
a_level_X = nav.find_all("a", {"data-tracking": re.compile("custom-level-\d")})

navbar_dict = {}
current_level1 = ""
current_level2 = ""

urls_list = []

# on itère dessus
for a in a_level_X:
    # on verifie le level de l'a
    print(a.get("data-tracking"))
    level = a.get("data-tracking").split("-")[2]
    
    if level == "1":
        print("level 1 : ", a.text)
        current_level1 = a.text.replace("\n", "")
        navbar_dict[current_level1] = {}
        # Ajouter l'URL du niveau 1 si elle existe
        if a.get("href"):
            navbar_dict[current_level1]["url"] = a.get("href")
            if navbar_dict[current_level1]["url"] != "#":
                navbar_dict[current_level1]["structure"] = check_structure(navbar_dict[current_level1]["url"])
                urls_list.append({"url": navbar_dict[current_level1]["url"], "structure": navbar_dict[current_level1]["structure"]})
            
    elif level == "2":
        print("level 2 : ", a.text)
        current_level2 = a.text.replace("\n", "")
        navbar_dict[current_level1][current_level2] = {}
        # Ajouter l'URL du niveau 2
        if a.get("href"):
            navbar_dict[current_level1][current_level2]["url"] = a.get("href")
            if navbar_dict[current_level1][current_level2]["url"] != "#":
                navbar_dict[current_level1][current_level2]["structure"] = check_structure(navbar_dict[current_level1][current_level2]["url"])
                urls_list.append({"url": navbar_dict[current_level1][current_level2]["url"], "structure": navbar_dict[current_level1][current_level2]["structure"]})
            
    elif level == "3":
        print("level 3 : ", a.text)
        level3_name = a.text.replace("\n", "")
        # Créer la structure pour le niveau 3
        navbar_dict[current_level1][current_level2][level3_name] = {}
        # Ajouter l'URL du niveau 3
        if a.get("href"):
            navbar_dict[current_level1][current_level2][level3_name]["url"] = a.get("href")
            if navbar_dict[current_level1][current_level2][level3_name]["url"] != "#":
                navbar_dict[current_level1][current_level2][level3_name]["structure"] = check_structure(navbar_dict[current_level1][current_level2][level3_name]["url"])
                urls_list.append({"url": navbar_dict[current_level1][current_level2][level3_name]["url"], "structure": navbar_dict[current_level1][current_level2][level3_name]["structure"]})

# on sauvegarde le dictionnaire dans un fichier json
with open("navbar_dict.json", "w", encoding="utf-8") as f:
    json.dump(navbar_dict, f, ensure_ascii=False, indent=4)


