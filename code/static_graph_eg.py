# Ce fichier a pour but de représenter le graphe statique qui va représenter tout l'EG en entier
# Pour cela on va simplement récupérer tous les éléments du fichier json et les ajouter dans le graphe
# Ensuite, les liens correspondants seront ajoutés pour construire le graphe de manière logique

# Ce fichier va également servir à la disposition des pièces sur la représentation principale
# En effet, on va essayer de reprendre les coordonnées de ce graphe pour représenter le graphe sur l'interface
# De cette manière, on pourra observer une apparence similaire entre les deux représentations

# Imports
import networkx as nx
import matplotlib.pyplot as plt
import json

# Cette fonction a pour but d'afficher le graphe statique qui correspond à l'EG entier
def display_static_graph():
    # Lecture du json, on lit le fichier origin car il ne change pas, c'est une sécurité
    with open('origin.json') as mon_fichier:
        data = json.load(mon_fichier)
        
        eg_example = data
        
    # On ajoute le plt.close() pour fermer la dernière pop up ouverte, car sinon les graphes s'empilent sur la même pop up
    plt.close()

    # Crée un graphe vide
    escape_game_graph = nx.Graph()

    # On ajoute les nœuds représentant les pièces
    for room in eg_example["Rooms"]:
        escape_game_graph.add_node(room["id"])

    # Ajoute les arêtes représentant les portes entre les pièces
    for door in eg_example["Doors"]:
        escape_game_graph.add_edge(door["connexion"][0], door["connexion"][1], type="Porte")

    # On ajoute les items aux pièces
    for room in eg_example["Rooms"]:
        # Indices
        for clue in room["clues"]:
            escape_game_graph.add_edge(room["id"], clue["id"], type="Indice")
        # Puzzles
        for puzzle in room["puzzles"]:
            escape_game_graph.add_edge(room["id"], puzzle["id"], type="Puzzle")
        # Joueurs
        for player in room["players_in_front"]:
            escape_game_graph.add_edge(room["id"], player, type="Joueur")

    # dessiner le graphe avec Matplotlib
    pos = nx.kamada_kawai_layout(escape_game_graph) # On met le kamada, comme cela il ne change pas de position
    nx.draw(escape_game_graph, pos, with_labels=True, node_size=800)

    # Ici on va récupérer les attributs des liens et les afficher
    edge_labels = nx.get_edge_attributes(escape_game_graph,'type')
    nx.draw_networkx_edge_labels(escape_game_graph, pos, edge_labels = edge_labels)
    # On sauvegarde une image du graphe en png au cas où
    plt.savefig("Static graph.png", format="PNG")
    # Ensuite on affiche le graphe construit grâce à tous les éléments du fichier json
    plt.show()
    
# Cette fonction a pour but de récupérer les corrdonnées du graphe provenant de l'affichage avec la méthode plt.show()
# Ensuite on adapte les coordonnées pour les faire correspondre le mieux possible à l'interface globale
def set_coords_static_graph():
    # Lecture du json, on lit le fichier origin car il ne change pas, c'est une sécurité
    with open('origin.json') as mon_fichier:
        data = json.load(mon_fichier)
        
        eg_example = data
        
    # On va créer le graphe de la même manière que la fonction au-dessus, sauf qu'ici c'est pour récupérer les coordonnées des pièces
    # Ce n'est pas pour afficher le graphe

    # Crée un graphe vide
    escape_game_graph = nx.Graph()

    # On ajoute les nœuds représentant les pièces
    for room in eg_example["Rooms"]:
        escape_game_graph.add_node(room["id"])

    # Ajoute les arêtes représentant les portes entre les pièces
    for door in eg_example["Doors"]:
        escape_game_graph.add_edge(door["connexion"][0], door["connexion"][1], type="Porte")

    # On ajoute les items aux pièces
    for room in eg_example["Rooms"]:
        # Indices
        for clue in room["clues"]:
            escape_game_graph.add_edge(room["id"], clue["id"], type="Indice")
        # Puzzles
        for puzzle in room["puzzles"]:
            escape_game_graph.add_edge(room["id"], puzzle["id"], type="Puzzle")
        # Joueurs
        for player in room["players_in_front"]:
            escape_game_graph.add_edge(room["id"], player, type="Joueur")

    # dessiner le graphe avec Matplotlib
    pos = nx.kamada_kawai_layout(escape_game_graph) # On met le kamada, comme cela il ne change pas de position
    
    # On lit le fichier json evolving pour avoir les données évolutives du jeu
    with open('evolving.json') as mon_fichier:
        data = json.load(mon_fichier)
        
        game_data = data
    
    # Ce sont les tailles un fois mis en grande fenêtre
    h_canvas = 722
    w_canvas = 1086
    # On définit cette variable qui reprend le centre du canva
    canva_center = (w_canvas/2, h_canvas/2)
    
    # création d'une liste des positions qui sera ensuite retournée pour placer les pièces
    ls_positions=[]
    
    # On va donc aller chercher pour chaque pièce la position qu'il lui faut
    for room in game_data["Rooms"]:
        position_room = pos[room["id"]]
        
        # Avec ce calcul, on ajuste la proportion de l'espacement des pièces en fonction de leur nombre
        # C'est à dire que + il y a de pièces, + elles seront petites et serrées
        proportion = 600 - len(game_data["Rooms"]) * 50
        
        # On assigne les coordonnées x et y en fonction des positions du graphe
        coord_x = int(position_room[0]*proportion + canva_center[0] - 100) # -100 pour centrer au possible
        coord_y = int(-position_room[1]*proportion + canva_center[1])
        
        # On ajoute les positions à la liste
        ls_positions.append((coord_x, coord_y))
    
    # On retourne la liste qui contient toutes les positions à adopter pour respecter l'affichage du graphe statique
    return ls_positions