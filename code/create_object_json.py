# Ce fichier va permettre de récupérer toutes les informations contenues dans le fichier json afin de créer tous les éléments
# nécessaire à la création de la représentation de l'EG

# Pour cela, on va tout simplement consulter le fichier json pour ensuite créer tous les éléments par catégorie

# Imports
from objects import *
import json

# Lecture du fichier json contenant les informations du jeu
with open('evolving.json') as mon_fichier:
    #On charge le fichier json
    data = json.load(mon_fichier)
    
    # On récupère les infos de chaque item
    rooms = data["Rooms"]
    doors = data["Doors"]
    players = data["Players"]
    actions = data["Actions"]
    # On crée les listes qui contiendront le nombre d'items
    ls_puzzles = []
    ls_clues = []
    ls_doors = []
    ls_players = []
    ls_actions = []
    
    # Pour chaque item on va chercher le nombre
    for i in range(0, len(rooms)):
        for j in range(0, len(rooms[i]["puzzles"])):
            # Récupérer tous les puzzles
            ls_puzzles.append(rooms[i]["puzzles"][j])
    for i in range(0, len(rooms)):
        for j in range(0, len(rooms[i]["clues"])):
            # Récupérer tous les indices
            ls_clues.append(rooms[i]["clues"][j])
    for i in range(0, len(doors)):
        # Récupérer toutes les portes
        ls_doors.append(doors[i]["id"])
    for i in range(0, len(players)):
        # Récupérer tous les joueurs
        ls_players.append(players[i]["name"])
    for i in range(0, len(actions)):
        # Récupérer toutes les actions
        ls_actions.append(actions[i]["id"])
        
    # On crée des variables qui contiennent chaque longueur de liste
    nb_rooms = len(rooms)
    nb_puzzles = len(ls_puzzles)
    nb_clues = len(ls_clues)
    nb_doors = len(ls_doors)
    nb_players = len(ls_players)
    nb_actions = len(ls_actions)
    
    # Création des listes qui vont contenir les objets du fichier json
    ls_rooms_eg=[]
    ls_puzzles_eg = []
    ls_clues_eg = []
    ls_doors_eg = []
    ls_players_eg = []
    ls_actions_eg = []
    
    # Cette fonction va donc nous permettre de mettre en place l'EG, 
    # en effet c'est elle qui va créer tous les objets du jeu sur base des différentes classe
    def set_ls_eg():
        # On itère sur le nombre de salles présentes dans le fichier et on ajoute à une liste les data des salles respectives
        for i in range(nb_rooms):
            # On a dû init les paramètres puzzles et clues à [] car on les remplit après
            ls_rooms_eg.append(Room(data["Rooms"][i]["id"], data["Rooms"][i]["players_in_front"], data["Rooms"][i]["players_in"], data["Rooms"][i]["position"], [], []))
            # ici on a dû vérifier sur base des puzzles contenus dans chaque room
            # c'est pour cela qu'on a utilisé une boucle qui va prendre chaque room et regarder le nbr de puzzles qu'elle contient pour pas index out of range
            for j in range(len(data["Rooms"][i]["puzzles"])):
                puz = Puzzle(data["Rooms"][i]["puzzles"][j]["id"], data["Rooms"][i]["puzzles"][j]["taxonomy"], data["Rooms"][i]["puzzles"][j]["rewards"], data["Rooms"][i]["puzzles"][j]["meta"], data["Rooms"][i]["puzzles"][j]["found"], data["Rooms"][i]["puzzles"][j]["position"])
                ls_puzzles_eg.append(puz)
                # Ici on remplit le paramètre "puzzles" en fonction de la salle, comme ça seuls les puzzles de la bonne salle seront présents
                ls_rooms_eg[i].puzzles.append(puz)
                
            for j in range(len(data["Rooms"][i]["clues"])):
                cl = Clue(data["Rooms"][i]["clues"][j]["id"], data["Rooms"][i]["clues"][j]["puzzle_id"], data["Rooms"][i]["clues"][j]["description"], data["Rooms"][i]["clues"][j]["meta"], data["Rooms"][i]["clues"][j]["found"], data["Rooms"][i]["clues"][j]["position"])
                ls_clues_eg.append(cl)
                # Ici on remplit le paramètre "clues", idem "puzzles"
                ls_rooms_eg[i].clues.append(cl)
        # On fait pareil pour les éléments restants (doors, players & actions)        
        for i in range(nb_doors):
            ls_doors_eg.append(Door(data["Doors"][i]["id"], data["Doors"][i]["connexion"], data["Doors"][i]["opened"], data["Doors"][i]["position_start"], data["Doors"][i]["position_end"]))
        for i in range(nb_players):
            ls_players_eg.append(Player(data["Players"][i]["name"], data["Players"][i]["skills"], data["Players"][i]["inventory"], data["Players"][i]["knowledge"], data["Players"][i]["position"]))
        for i in range(nb_actions):
            ls_actions_eg.append(Action(data["Actions"][i]["id"]))
    
    # On prépare toutes les listes contenant les objets
    set_ls_eg()
    
# On va d'abord devoir lire le json de base pour ensuite stocker ses infos et le modifier au fur et à mesure
# Cette fonction permet la lecture d'un json et d'avoir les données de celui-ci dans la variable data
def read_json(file):
    print("Lecture du fichier json")
    with open(file) as mon_fichier:
    	#On charge le fichier json
    	data = json.load(mon_fichier)
    	#print(data)
    	return data
  
# Cette fonction permet la sauvegarde de données dans un nouveau fichier json afin de sauvegarder l'état du jeu à un moment donné
def update_json(file, data):
    print("Sauvegarde du fichier json")
    json_object = json.dumps(data, indent=4)
    with open(file, "w") as outfile:
    	outfile.write(json_object)

# On fait cela ici pour pouvoir setup les deux fichiers json, 
# le fichier evolving qui va évoluer pendant la partie et le fichier origin qui conservera les données de base du jeu

# On lit le json de base
data = read_json("evolving.json")
# On sauvegarde un json qui contient l'état du jeu au départ avant la partie
update_json("origin.json", data)