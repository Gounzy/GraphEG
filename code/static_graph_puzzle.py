# Ce fichier a pour but de représenter les puzzles (Puzzle framework) en graphes statiques (// à la fonctionnalité de Pop up)
# Il faut adapter la structure ici car le graphe du puzzle doit représenter le puzzle, à quoi il sert et comment le résoudre.

# On va représenter le puzzle framework avec ce qu'il y a dans une pièce
# On peut avoir des puzzles(cadenas) et des indices(chiffres)
# On va donc représenter chaque fois un élément par son identifiant

# Imports
import networkx as nx
import matplotlib.pyplot as plt
import json

# Cette fonction a pour but d'afficher à l'aide de plt.show() le puzzle framework correspondant
def display_puzzle_framework(item_clicked):
    # Lecture du json, on lit le fichier origin car il ne change pas, c'est une sécurité
    with open('origin.json') as mon_fichier:
        data = json.load(mon_fichier)
        
        eg_example = data
        
    # On ajoute le plt.close() pour fermer la dernière pop up ouverte, car sinon les graphes s'empilent sur la même pop up
    plt.close()
    # Crée un graphe orienté vide
    escape_game_graph = nx.DiGraph()
    
    # On va donc à chaque fois partir d'un puzzle pour construire le graphe avec tous les items nécessaires pour résoudre ce puzzle
    for room in eg_example["Rooms"]:
        # Test item cliqué
        # Ici on va vérifier le framework que l'on doit faire en fonction de l'item cliqué (puzzle ou indice)
        for puzzle in room["puzzles"]:
            if item_clicked == puzzle["id"]:
                framework_to_do = puzzle["id"]
        for clue in room["clues"]:
            if item_clicked == clue["id"]:
                framework_to_do = clue["puzzle_id"]

    # On doit mettre une autre boucle pour bien différencier le fait de chercher le framework à produire, et le fait de produire ce framework
    for room in eg_example["Rooms"]:
        # On doit gérer le cas où le puzzle n'est plus sur le plateau mais chez un joueur
        if room["puzzles"] == []:
            for player in eg_example["Players"]:
                for item in player["inventory"]:
                    if type(item) == dict:
                        escape_game_graph.add_node(item["id"])
        # C'est ici qu'on va prendre le puzzle pour lequel on crée/affiche le graphe
        for puzzle in room["puzzles"]:
            # On va faire le puzzle framework du puzzle où est inclus l'item
            if puzzle["id"] == framework_to_do:
                # On ajoute donc le puzzle et la pièce de base
                escape_game_graph.add_node(room["id"])
                escape_game_graph.add_node(puzzle["id"])
                # On ajoute le lien entre le puzzle et la pièce car la pièce "masque" le puzzle (il est dans la pièce)
                escape_game_graph.add_edge(room["id"], puzzle["id"])
                # On va maintenant vérifier le reward pour voir vers quoi nous mène le puzzle
                # Car possibilité de plusieurs rewards
                for reward in puzzle["rewards"]:
                    # On fait un split pour récupérer l'identifiant du reward
                    splitted = reward.split(" ")
                    # Si il y a un D, c'est une porte
                    if "D" in reward:
                        exit_door = splitted[0]
                        # Ici du coup on sait que le puzzle mène à une autre pièce
                        # On vérifie avec quelle pièce la porte est connectée
                        # Attention ici room != reward_room
                        for reward_room in eg_example["Rooms"]:
                            for door in eg_example["Doors"]:
                                if exit_door == door["id"]:
                                    if reward_room["id"] == door["connexion"][1]:
                                        # Et on l'ajoute au graphe
                                        escape_game_graph.add_node(reward_room["id"])
                                        # On ajoute le lien entre la dernière pièce et le puzzle car c'est le puzzle la dernière chose avant de pouvoir passer
                                        escape_game_graph.add_edge(puzzle["id"], reward_room["id"])
                    # Si la récompense n'est pas la clé pour une porte         
                    else:
                        # Ici on doit prendre en compte le deuxième cas
                        # On va déjà récupérer l'id du reward pour l'identifier
                        reward_id = splitted[0]
                        # On ajoute donc au graphe la récompense
                        escape_game_graph.add_node(reward_id)
                        # On lie cette récompense au puzzle correspondant
                        escape_game_graph.add_edge(puzzle["id"], reward_id)
                        
                # Ici on ajoute le lien d'un indice nécessaire pour ouvrir le puzzle
                # On init un autre nom de variable que room, sinon ça affecte le room de la boucle + haut
                for room_clue in eg_example["Rooms"]:
                    for clue in room_clue["clues"]:
                        if clue["puzzle_id"] == puzzle["id"]:
                            escape_game_graph.add_node(clue["id"])
                            # On ajoute la lien entre l'indice et le puzzle qui lui correspond
                            escape_game_graph.add_edge(clue["id"], puzzle["id"])
                            # On vient ajouter la pièce dans laquelle est l'indice si ce n'est pas encore fait
                            # On check d'abord si le neoud n'est pas déjà fait
                            if not(escape_game_graph.has_node(room_clue["id"])):
                                escape_game_graph.add_node(room_clue["id"])
                            # Ensuite on peut créer le lien entre la pièce et l'indice
                            escape_game_graph.add_edge(room_clue["id"], clue["id"])

    # Ici on va s'occuper de savoir quel item doit être mis en évidence sur le graphe pour pouvoir savoir où sert l'item cliqué en question
    if item_clicked in escape_game_graph.nodes:
        # On définit la couleur d'un noeud en fonction de son id
        color_map = ['red' if node == item_clicked  else 'blue' for node in escape_game_graph]
        # On vérifie que le graphe possède bien un puzzle framework
        if len(escape_game_graph) != 0:
            # On va ajouter un titre avec l'item
            plt.title("Puzzle Framework {}".format(item_clicked))
            # On dessine le graphe
            nx.draw(escape_game_graph, pos=nx.circular_layout(escape_game_graph, scale=1), with_labels=True, node_size=2000, node_color=color_map)
            
            # Ici on va seulement afficher le graphe correspondant à l'item cliqué
            plt.show()
            # Permet de remttre le graphe à 0 pour ne pas mélanger les puzzles framework
            escape_game_graph.clear()
        