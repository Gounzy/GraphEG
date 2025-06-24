# Ce fichier a pour but de représenter le graphe dynamique qui se construira au fur et à mesure de la partie (// fonctionnalité de jouabilité)
# Pour faire ce graphe, on va partir d'un graphe possédant toutes les connexions possibles entre les éléments du jeu
# Une fois que tous ces liens seront crées, on affichera ceux nécessaires en temps voulu en fonction de l'état du fichier json
# On peut faire cela grâce à la méthode restricted_view() de networkx qui permet de restreindre la vue de certains liens

# Imports
import networkx as nx
import matplotlib.pyplot as plt
import json

# Cette fonction a pour but d'afficher le graphe dynamique en se basant sur l'état actuel du json
def display_dynamic_graph():
    # Lecture du json
    with open('evolving.json') as mon_fichier:
        data = json.load(mon_fichier)
        
        eg_example = data
        
    # On ajoute le plt.close() pour fermer la dernière pop up ouverte, car sinon les graphes s'empilent sur la même pop up
    plt.close()

    # Crée un graphe orienté vide
    escape_game_dyn_graph = nx.DiGraph()

    # On ajoute tous les noeuds du json
    for room in eg_example["Rooms"]:
        escape_game_dyn_graph.add_node(room["id"])
        # Indices
        for clue in room["clues"]:
            escape_game_dyn_graph.add_node(clue["id"])
        # Puzzles
        for puzzle in room["puzzles"]:
            escape_game_dyn_graph.add_node(puzzle["id"])
    # Joueurs
    for player in eg_example["Players"]:
        escape_game_dyn_graph.add_node(player["name"])
        # Il faut également penser au cas où les joueurs possèdent des items
        # Indice
        for clue in player["knowledge"]:
            escape_game_dyn_graph.add_edge(player["name"], clue["id"], type="inspect")
        # Puzzle
        for puzzle in player["inventory"]:
            escape_game_dyn_graph.add_edge(player["name"], puzzle["id"], type="inspect")
            
    for door in eg_example["Doors"]:
        escape_game_dyn_graph.add_node(door["id"])
        
    # On va maintenant créer tous les liens possibles

    # Liens de l'action interact
    # On doit quand même ajouter le lien de base qui est que les joueurs sont dans la pièce de départ,
    # on ajoute également les liens vers les autres pièces
    for room in eg_example["Rooms"]:
        for player in eg_example["Players"]:
            escape_game_dyn_graph.add_edge(player["name"], room["id"], type="interact")
                
    # Liens de l'action inspect
    # On ajoute les liens entre les items et les pièces du jeu
    for room in eg_example["Rooms"]:
        for clue in room["clues"]:
            escape_game_dyn_graph.add_edge(room["id"], clue["id"], type="inspect")
            # Ici on ajoute les items qui seront en possession d'un joueur, même chose pour les puzzles en bas
            for player in eg_example["Players"]:
                for clue in player["knowledge"]:
                    escape_game_dyn_graph.add_edge(player["name"], clue["id"], type="inspect")
        for puzzle in room["puzzles"]:
            escape_game_dyn_graph.add_edge(room["id"], puzzle["id"], type="inspect")
            for player in eg_example["Players"]:
                for puzzle in player["inventory"]:
                    escape_game_dyn_graph.add_edge(player["name"], puzzle["id"], type="inspect")
    
    # Liens de l'action take
    # On ajoute les liens de chaque item (juste indice) qui peuvent être pris
    for room in eg_example["Rooms"]:
        for clue in room["clues"]:
            escape_game_dyn_graph.add_edge(clue["id"], clue["id"], type="take")
        for puzzle in room["puzzles"]:
            escape_game_dyn_graph.add_edge(puzzle["id"], puzzle["id"], type="resolve")
            
    # Liens de l'action share
    # On ajoute les liens de chaque partage entre joueurs
    for player in eg_example["Players"]:
        for player_to_share in eg_example["Players"]:
            # On regarde qu'ils ne se partagent pas à eux-mêmes
            if player["name"] != player_to_share["name"]:
                # On regarde qu'ils soient bien dans la même pièce
                for room in eg_example["Rooms"]:
                    if ((player["name"] in room["players_in"]) and (player_to_share["name"] in room["players_in"])) or ((player["name"] in room["players_in_front"]) and (player_to_share["name"] in room["players_in_front"])):
                        escape_game_dyn_graph.add_edge(player["name"], player_to_share["name"], type="share")

    # Liens de l'action move
    # On ajoute les liens de chaque pièce qui peuvent être traversées
    for room in eg_example["Rooms"]:
        for room_to_go in eg_example["Rooms"]:
            # On va quand même vérifier qu'il y a bien une porte entre les deux pièces
            for door in eg_example["Doors"]:
                if (door["connexion"][0] == room["id"] and door["connexion"][1] == room_to_go["id"]) or (door["connexion"][1] == room["id"] and door["connexion"][0] == room_to_go["id"]):
                    # On précise bien qu'on ne peut pas se déplacer d'une pièce à cette même pièce
                    if room["id"] != room_to_go["id"]:
                        escape_game_dyn_graph.add_edge(room["id"], room_to_go["id"], type="move")

    # Ici on va maintenant créer les listes qui contiendront les noeuds et les liens à cacher (restreindre)
    # Voici les deux listes qui permettent de cacher certains noeuds/liens
    unreachable_nodes = []
    unreachable_edges = []
    # On va créer une liste avec le nom des joueurs pour les afficher d'office au départ
    players = []
    for player in eg_example["Players"]:
        players.append(player["name"])
    
    # Au départ, on ne doit afficher que les noeuds des joueurs et la pièce où ils sont
    for all_nodes in escape_game_dyn_graph.nodes:
        # On regarde les noeuds qui ne sont pas des joueurs et on les enlève (on les ajoute à la liste des exclus)
            if all_nodes not in players:
                if all_nodes not in unreachable_nodes:
                    unreachable_nodes.append(all_nodes)
                
    # Ici on ajoute la pièce où sont les joueurs pour commencer
    for room in eg_example["Rooms"]:
        # On doit faire la généralisation que si des joueurs sont à proximité d'une salle ou dedans, on doit l'afficher
        if room["players_in_front"] != [] or room["players_in"] != []:
            unreachable_nodes.remove(room["id"])
            
    # On va devoir ajouter aussi les liens qui concernent un item vers lui-même car on ne doit pas l'afficher dès qu'on affiche son noeud
    # On doit masquer les liens pour take et resolve
    # On récupère tous les types des liens (ça donne un dictionnaire)
    edge_types = nx.get_edge_attributes(escape_game_dyn_graph,'type')
    # Du coup pour chaque noeud on vérifie son type
    for edge in edge_types:
        if edge_types[edge] == "take":
            unreachable_edges.append(edge)
        if  edge_types[edge] == "resolve":
            unreachable_edges.append(edge)

    # On va devoir également cacher les liens des joueurs dans toutes les pièces du jeu car ils ne peuvent être que dans une pièce
    for room in eg_example["Rooms"]: # On regarde d'abord par pièce, comme ça on est sûr de bien laisser les liens au bonnes pièces
        for room_edge in edge_types:
            # On vérifie direct la nature du lien pour ne pas devoir tester tous les liens qui ne sont pas interact
            if edge_types[room_edge] == "interact":
                if room["players_in"] == [] and room["players_in_front"] == []:
                    # On vérifie que le lien est bien celui avec la pièce qu'on teste dans la première boucle
                    if room["id"] == room_edge[1]:
                        if room_edge not in unreachable_edges:
                            unreachable_edges.append(room_edge)
                            
    # On doit cacher les liens quand les joueurs possèdent des items (indices seulement je pense) par défaut
    # Lorsqu'un indice est pris par un joueur, il disparait de la pièce
    for room in eg_example["Rooms"]:
        for clue in room["clues"]:
            for player in eg_example["Players"]:
                unreachable_edges.append((player["name"], clue["id"]))
                # On cache également les items qui pourraient se trouver déjà dans les joueurs
                for clue_in_player in player["knowledge"]:
                    # On ajoute une vérif pour éviter les doublons
                    if (player["name"], clue_in_player["id"]) not in unreachable_edges:
                        unreachable_edges.append((player["name"], clue_in_player["id"]))
        for puzzle in room["puzzles"]:
            for player in eg_example["Players"]:
                unreachable_edges.append((player["name"], puzzle["id"]))
                # On cache également les items qui pourraient se trouver déjà dans les joueurs
                for puzzle_in_player in player["inventory"]:
                    # On ajoute une vérif pour éviter les doublons
                    if (player["name"], puzzle_in_player["id"]) not in unreachable_edges:
                        unreachable_edges.append((player["name"], puzzle_in_player["id"]))
    
    # Ici on s'occupe du lien share entre deux joueurs, 
    # on dit que s'ils sont dans la même pièce et qu'ils sont bien 2 joueurs différents, on affiche le lien car ils peuvent partager 
    for room in eg_example["Rooms"]:
        for player in eg_example["Players"]:
            for other_player in eg_example["Players"]:
                if player != other_player:
                    # On vérifie si les joueurs sont au même endroit
                    if (player["name"] in room["players_in"] and other_player["name"] in room["players_in"]) or (player["name"] in room["players_in_front"] and other_player["name"] in room["players_in_front"]):
                        unreachable_edges.append((player["name"], other_player["name"]))
    
    # On va maintenant prendre les actions une par une pour voir comment on pourrait la gérer en fonction de l'état du json
        
    # Interact
    # On check dans le json où sont les joueurs pour afficher les items de la bonne pièce
    for room in eg_example["Rooms"]:
        for player in eg_example["Players"]:
            if player["name"] in room["players_in"]:
                for clue in room["clues"]:
                    # On ajoute une vérification car si plusieurs joueurs sont dans la pièce, on ne peut pas le retirer plusieurs fois de la liste
                    if clue["id"] in unreachable_nodes:
                        unreachable_nodes.remove(clue["id"])
                for puzzle in room["puzzles"]:
                    # Même vérificiation ici
                    if puzzle["id"] in unreachable_nodes:
                        unreachable_nodes.remove(puzzle["id"])
    # Inspect
    # On check dans le json quels items sont trouvés (found=True) pour ajouter l'action take, car il faut prendre un puzzle avant de le résoudre
    for room in eg_example["Rooms"]:
        for clue in room["clues"]:
            if clue["found"] == True:
                if (clue["id"], clue["id"]) in unreachable_edges:
                        unreachable_edges.remove((clue["id"], clue["id"]))
        for puzzle in room["puzzles"]:
            if puzzle["found"] == True:
                if (puzzle["id"], puzzle["id"]) in unreachable_edges:
                    unreachable_edges.remove((puzzle["id"], puzzle["id"]))
    # Take
    # On check si l'item a bien été mis dans la connaissance ou l'inventaire du joueur
    for room in eg_example["Rooms"]:
        for player in eg_example["Players"]:
            for clue in player["knowledge"]:
                # On ajoute d'abord manuellement le noeud clue car il a été retiré
                # Pour pouvoir l'afficher mais autrement
                if clue["id"] in unreachable_nodes:
                    unreachable_nodes.remove(clue["id"])
                # Ensuite on ajoute le lien corrsepondant pour le joueur
                if (player["name"], clue["id"]) in unreachable_edges:
                    unreachable_edges.remove((player["name"], clue["id"]))
                
            for puzzle in player["inventory"]:
                # On ajoute les items au joueur
                # On n'a pas besoin d'enlever l'item du graphe car dans le json il n'est plus dans la pièce donc c'est comme si il n'avait pas existé
                if (player["name"], puzzle["id"]) in unreachable_edges:
                    unreachable_edges.remove((player["name"], puzzle["id"]))
                # Pour pouvoir l'afficher mais autrement
                if puzzle["id"] in unreachable_nodes:
                    unreachable_nodes.remove(puzzle["id"])
                # Pour finir on doit également ajouter le lien qui permet de résoudre le puzzle
                escape_game_dyn_graph.add_edge(puzzle["id"], puzzle["id"], type="resolve")
                
    # Resolve
    # On doit résoudre le puzzle et donc afficher ce qu'il a obtenu, en plus de cela on doit enlever le puzzle et les indices utilisés
    # Beaucoup de choses sont déjà faites grâce au json
    for room in eg_example["Rooms"]:
        for door in eg_example["Doors"]:
            for player in eg_example["Players"]:
                # On vérifie que la porte est bien ouverte, que la pièce concernée est bien attachée à la porte et que les joueurs sont bien à porté de la porte
                if door["opened"] == True and room["id"] in door["connexion"] and player["name"] in room["players_in"]:
                    # Ici on va chercher juste l'autre pièce où les joueurs ne sont pas dedans pour ajouter le lien move
                    for room_to_open in door["connexion"]:
                        if room_to_open != room["id"]:
                            # On vérifie si la pièce est bien dans la liste évidement
                            if room_to_open in unreachable_nodes:
                                unreachable_nodes.remove(room_to_open)
                    # En plus de cela, il faut enlever la clé de l'inventaire du joueur
                    for reward in player["inventory"]:
                        # On check le type pour ne pas avoir affaire à un puzzle
                        if type(reward) == str:
                            # S'il s'agit bien d'une porte, on l'enlève
                            if reward[0] == "D":
                                if reward not in unreachable_nodes:
                                    unreachable_nodes.append(reward)
    # Share
    # On vérifie si les joueurs sont dans la même pièce
    for room in eg_example["Rooms"]:
        for player in eg_example["Players"]:
            for other_player in eg_example["Players"]:
                if player != other_player:
                    # On vérifie si les joueurs sont au même endroit
                    if (player["name"] in room["players_in"] and other_player["name"] in room["players_in"]) or (player["name"] in room["players_in_front"] and other_player["name"] in room["players_in_front"]):
                        unreachable_edges.remove((player["name"], other_player["name"]))
    # Move
    # On vérifie où sont les joueurs dans le json
    for room in eg_example["Rooms"]:
        for player in eg_example["Players"]:
            # D'abord on ajoute les liens en fonction de où sont les joueurs
            if player["name"] in room["players_in"] or player["name"] in room["players_in_front"]:
                if (player["name"], room["id"]) in unreachable_edges:
                    unreachable_edges.remove((player["name"], room["id"]))
            # Ensuite on enlève ceux qui les relient aux pièces qui ne sont pas à porté
            if player["name"] not in room["players_in"] and player["name"] not in room["players_in_front"]:
                if (player["name"], room["id"]) not in unreachable_edges:
                    unreachable_edges.append((player["name"], room["id"]))
    # Exit
    # On doit vérifier si les joueurs sont bien dans la dernière pièce
    # On doit juste faire disparaitre les joueurs qui sortent de l'EG
    # Du coup ici on va incrémenter une valeur pour chaque joueur, quand on parcourt une salle et que le joueur n'est ni dedans, ni devant on fait +1
    # Et quand on trouve le joueur dans ou devant une pièce on fait -1, ce qu'il fait qu'à la fin, si le counter est égal au nombre de chambre, le joueur n'est nulle part
    # C'est parce qu'en fait il est sorti du jeu
    for player in eg_example["Players"]:
        # Init le compteur à 0 pour chaque joueur
        count=0
        for room in eg_example["Rooms"]:
            # Si on ne trouve personne, +1
            if player["name"] not in room["players_in"] and player["name"] not in room["players_in_front"]:
                count+=1
            # Sinon -1
            else:
                count-=1
        # Compteur = nbr pièces -> le joueur est parti
        if count == len(eg_example["Rooms"]):
            if player["name"] not in unreachable_nodes:
                unreachable_nodes.append(player["name"])

    # C'est ici qu'on va construire et dessiner le graphe après que toutes les restrictions ont été ajoutées depuis le json
    # On assigne donc le graphe avec la méthode permettant de réduire la vue des noeuds et liens à ne pas afficher
    escape_game_dyn_graph = nx.restricted_view(escape_game_dyn_graph, unreachable_nodes, unreachable_edges)
    
    # Dessiner le graphe avec Matplotlib
    pos = nx.circular_layout(escape_game_dyn_graph)
    nx.draw(escape_game_dyn_graph, pos, with_labels=True, node_size=1000)
    # Ici on repositionne les labels des types des liens qui vont d'un noeud vers le même noeud (loop)
    for edge in escape_game_dyn_graph.edges():
        # On prend les noeuds qui sont en boucle seulement
        if edge[0] == edge[1]:
            x, y = pos[edge[0]]
            # On ajoute 0.23 au-dessus du noeud pour que ce soit lisible
            plt.text(x, y+0.23, escape_game_dyn_graph[edge[0]][edge[1]]['type'], horizontalalignment='center')
    # Ici on va récupérer les attributs des liens et les afficher
    edge_labels = nx.get_edge_attributes(escape_game_dyn_graph,'type')
    nx.draw_networkx_edge_labels(escape_game_dyn_graph, pos, edge_labels = edge_labels)
    
    # On peut sauvegarder une copie du dernier graphe dynamique affiché si l'utilisateur veut le voir, mais pas nécessaire
    plt.savefig("Dynamic graph.png", format="PNG")
    # Ici on affiche le graphe à l'aide du module matplotlib
    plt.show()