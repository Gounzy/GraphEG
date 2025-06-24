# Ce fichier contient la plupart du code permettant de faire tourner l'application
# Il contient la création de la fenêtre Tkinter, ainsi que tous les évènements qui peuvent se passer avec les widgets (boutons, etc)

# Dans un premier temps, on définit toutes les fonctions relatives à la jouabilité du jeu
# Plus particulièrement en ce qui concerne les requêtes

# Dans un second temps, on construit la fenêtre qui va contenir l'interface pour utiliser l'application
# On construit et on place tous les widgets necéssaires pour représenter les éléments

# Ensuite, on place les objets crées à l'aide des différentes classes d'éléments
# On termine avec la fonction de mise à jour du jeu et avec la boucle de fermeture de la fenêtre

# Tout à la fin se trouve la remise en place du json chargé de base, de sorte à ce qu'une fois la fenêtre fermée,
# on peut recommencer à jouer avec la même configuration de départ

# Imports
import tkinter
from tkinter import *
from tkinter import ttk
import random
import matplotlib.pyplot as plt
import time
# Imports depuis les fichiers python
from objects import *
from create_object_json import *
from pop_up import *
from static_graph_eg import display_static_graph, set_coords_static_graph
from dynamic_graph_eg import display_dynamic_graph

# Cette fonction a pour but de fermer les Pop up en même temps que la fenêtre principale
# On fait cela pour empêcher une Pop up d'être encore ouverte alors que l'on a fermé la fenêtre principale
def on_closing():
    # On ferme la Pop up
    plt.close()
    # On ferme la main window
    window.destroy()
    
# Cette fonction permet de retourner l'id d'un item en fonction de son type, dict ou alors les autres créés
# On aura besoin de cette fonction pour connaitre le type d'un item car cela peut être Clue, Puzzle ou plutôt dict
def check_type_item(item):
    # On check si on a affaire à un dict ou à un item Clue, Puzzle, etc
    if type(item) == dict:
        id_item = item["id"]
    else:
        id_item = item.id
    
    return id_item

# FONCTIONS RELATIVES A LA JOUABILITE

# On va définir les fonctions des requêtes, ces fonctions permettront de mettre à jour l'état du jeu en fonction des requêtes demandées
# Ces fonctions correspondent aux actions des graphes générés pour faire correspondre les deux représentations

# Cette fonction permet d'intéragir avec une pièce et donc de pouvoir observer tous les items qu'elle contient
# r_player et r_item correspondent respectivement au joueur et à l'élément/item sélectionné dans la requête
def interact_request(r_player, r_item):
    # On lit le json contenant l'état du jeu pour le mettre à jour
    game_data = read_json("evolving.json")
    
    # On init les variables nécessaires
    state = []
    # On init l'identifiant de l'item
    id_item = check_type_item(r_item)
    
    # On affiche l'action effectuée
    state.append("The player " + r_player.name + " interacts with the room " + id_item)
    
    # On vérifie ici qu'il s'agit bien d'une pièce
    if r_item not in ls_rooms_eg:
        state.append("We can just interact with a room")
        state.append("However " + id_item + " is not a room")
        return state
    
    # On va donc vérifier que le joueur n'est pas déjà dans la pièce
    if r_player in r_item.players_in:
        state.append("The player " + r_player.name + " is already in the room")
        
    # S'il n'est pas encore dans la pièce, on va l'y mettre
    else:
        # On vérifie qu'on est bien à côté de la pièce
        if r_player.name in r_item.players_in_front:
            # On précise que le joueur entre dans la pièce
            state.append("The player " + r_player.name + " enters the room " + id_item)
            # On vérifie qu'on parle bien de la bonne chambre
            for room in ls_rooms_eg:
                if room.id == id_item:
                    # On ajoute le joueur dans la pièce
                    if r_player not in room.players_in:
                        # On l'enlève de devant
                        room.players_in_front.remove(r_player.name)
                        # Puis on met dans la pièce
                        room.players_in.append(r_player.name)
                        # On update le json
                        index = ls_rooms_eg.index(room)# On prend l'index de la liste pour prendre la bonne pièce
                        # On enlève les joueurs de devant la pièce
                        game_data["Rooms"][index]["players_in_front"].remove(r_player.name)
                        # Ensuite on peut les mettre dedans
                        game_data["Rooms"][index]["players_in"].append(r_player.name)
                        # On précise que le joueur est bien dans la pièce maintenant
                        state.append("The player " + r_player.name + " is in the room " + id_item)
                        
            # On sauvegarde les modifications à propos des indices dans le json
            update_json("evolving.json", game_data)
            # On update la map pour afficher les joueurs dans l'autre pièce
            update_game(["all"])
            
        # Si le joueur n'est pas à côté de la pièce, on le précise
        else:
            state.append("The player " + r_player.name + " is too far from the room")
    
    # On fait une assertion pour vérifier que state est non vide car sinon, cela veut dire que rien ne s'est passé
    assert state != []
    # Finalement on renvoie l'historique de l'action
    return state
    
# Cette fonction permet d'inspecter soit un indice, soit un puzzle, pour pouvoir soit prendre, soit résoudre par la suite
# Lorsqu'on intéragit avec un indice/puzzle, il passe grisé, et quand il est pris, on le fait disparaitre du plateau car c'est le joueur qui l'a
def inspect_request(r_player, r_item):
    # On lit le json contenant l'état du jeu pour le mettre à jour
    game_data = read_json("evolving.json")
    
    # Remarque : Il faut mettre à jour le json pour la sauvegarde, mais également les listes ls_items_eg pour update la partie (convention)
    
    # On init les variables nécessaires
    ls_clues_in=[]
    ls_othters_clues=[]
    ls_puzzles_in=[]
    ls_othters_puzzles=[]
    state = []
    # On init l'identifiant de l'item
    id_item = check_type_item(r_item)
    
    # On affiche l'action effectuée
    state.append("The player " + r_player.name + " is looking for a clue or a puzzle")
    
    # On vérifie ici qu'il s'agit bien d'un indice ou d'un puzzle
    # On doit donc aussi vérifier l'inventaire et la connaissance du joueur
    if (r_item not in r_player.inventory and r_item not in r_player.knowledge) and (r_item not in ls_clues_eg and r_item not in ls_puzzles_eg):
        state.append("We can only inspect clues or puzzles")
        state.append("However " + id_item + " is not a clue or a puzzle")
        return state
    
    # On crée d'abord deux listes, une qui contient les indices de la salle des joueurs, l'autre liste contient tous les autres indices
    for room in ls_rooms_eg:
        # On fait cela pour les indices
        for item in room.clues:
            if r_player.name in room.players_in:
                ls_clues_in.append(item) # ici on crée la liste qui va contenir tous les indices de la salle où est le joueur
            else:
                ls_othters_clues.append(item)
        # Et ensuite pour les puzzles
        for item in room.puzzles:
            if r_player.name in room.players_in:
                ls_puzzles_in.append(item) # ici on crée la liste qui va contenir tous les puzzles de la salle où est le joueur
            else:
                ls_othters_puzzles.append(item)
    
    # INDICES
    # On check si on a affaire à un indice
    if "C" in id_item:
        # On va prendre l'indice qui correspond à celui que le joueur cherche
        for item in ls_clues_in:
            if item.id == id_item:
                # On vérifie que l'indice n'est pas déjà inspecté
                # Si l'item a déjà été inspecté, on le précise
                if r_item.found == True:
                    state.append("The clue " + id_item + " has already been inspected")
                else:
                    # On précise qu'on a inspecté l'indice
                    state.append(r_player.name + " inspected the clue " + id_item)
                    # Ici on change la valeur de found à True pour dire qu'on a inspecté l'indice
                    # On vérifie que le joueur soit bien dans la pièce et que l'indice aussi
                    for room in ls_rooms_eg:
                        if r_player.name in room.players_in:
                            if r_item in room.clues:
                                # Si on a bien l'indice, dans la pièce, on met à jour l'état du jeu avec les listes
                                r_item.found = True
                                # On modifie le json pour la save
                                index = ls_rooms_eg.index(room) # L'index désigne la place de la salle dans la liste ls_rooms_eg
                                # On vérifie qu'on parle du bon indice, et on passe la valeur found à True dans le json
                                for clue in game_data["Rooms"][index]["clues"]:
                                    if clue["id"] == id_item:
                                        clue["found"] = True
                                    
                    # On sauvegarde les modifications à propos des indices dans le json
                    update_json("evolving.json", game_data)
                    # On update la map pour afficher les joueurs dans l'autre pièce
                    update_game(["clues"])
        
        # Si l'indice est dans l'autre liste, il est dans une autre salle
        if r_item in ls_othters_clues:
            state.append("The clue " + id_item + " is not in this room")
            
        # Ici on va préciser s'il reste encore des indices à inspecter dans cette salle ou non
        for room in ls_rooms_eg:
            if r_player.name in room.players_in:
                # Ici on défini une variable afin de savoir s'il reste des indices dans la pièce
                clue_to_found = 0
                # On peut laisser cela au cas où une pièce est déjà vide de base et ne contient pas d'indices
                if room.clues == []:
                    state.append("This room has no clues")
                # Ensuite cette variable clue_to_found est incrémentée en fonction du nombre d'indices qui a déjà été inspecté
                else:
                    for clue in room.clues:
                        # On doit ajouter cette vérification car mtn on ne supprime plus un indice une fois trouvé, on le met juste en gris
                        if clue.found == False:
                            clue_to_found += 1
                # Ici on fait la vérification s'il reste des indices à inspecter dans la pièce ou non
                if clue_to_found > 0:
                    state.append("There are still clues to inspect in this room")
                elif clue_to_found == 0:
                    state.append("All clues in this room have been inspected")
    
    # PUZZLES
    # On check si on a affaire à un puzzle
    if "P" in id_item:
        # On va prendre le puzzle qui correspond à celui que le joueur cherche
        for item in ls_puzzles_in:
            if item.id == id_item:
                # On vérifie que le puzzle n'est pas déjà inspecté
                # Si l'item a déj) été inspecté, on le précise
                if r_item.found == True:
                    state.append("The puzzle " + id_item + " has already been inspected")
                else:
                    # On précise qu'on a inspecté l'puzzle
                    state.append(r_player.name + " inspected the puzzle " + id_item)
                    # Ici on change la valeur de found à True pour dire qu'on a inspecté le puzzle
                    # On vérifie que le joueur soit bien dans la pièce et que le puzzle aussi
                    for room in ls_rooms_eg:
                        if r_player.name in room.players_in:
                            if r_item in room.puzzles:
                                # Si on a bien le puzzle, dans la pièce, on met à jour l'état du jeu avec les listes
                                r_item.found = True
                                # On modifie le json
                                index = ls_rooms_eg.index(room) # L'index désigne la place de la salle dans la liste ls_rooms_eg
                                # On vérifie qu'on parle du bon puzzle, et on passe la valeur found à True dans le json
                                for puzzle in game_data["Rooms"][index]["puzzles"]:
                                    if puzzle["id"] == id_item:
                                        puzzle["found"] = True
                                        
                    # On sauvegarde les modifications à propos des puzzles dans le json
                    update_json("evolving.json", game_data)
                    # On update la map pour afficher les joueurs dans l'autre pièce
                    update_game(["puzzles"])
        
        # Si le puzzle n'est pas dans la salle et mais qu'il est dans l'autre liste, il est dans une autre salle
        if r_item in ls_othters_puzzles:
            state.append("The puzzle " + id_item + " is not in this room")
            
        # Ici on va préciser s'il reste encore des puzzles à inspecter dans cette salle ou non
        for room in ls_rooms_eg:
            if r_player.name in room.players_in:
                # Ici on défini une variable afin de savoir s'il reste des puzzles dans la pièce
                puzzle_to_found = 0
                # On peut laisser cela au cas où une pièce est déjà vide de base et ne contient pas de puzzles
                if room.puzzles == []:
                    state.append("This room has no puzzles")
                # Ensuite cette variable puzzle_to_found est incrémentée en fonction du nombre de puzzles qui ont été inspecté
                else:
                    for puzzle in room.puzzles:
                        # On doit ajouter cette vérification car mtn on ne supprime plus un puzzle une fois trouvé, on le met juste en gris
                        if puzzle.found == False:
                            puzzle_to_found += 1
                    # Ici on fait la vérification s'il reste des puzzles à inspecter dans la pièce ou non
                    if puzzle_to_found > 0:
                        state.append("There are still puzzles to inspect in this room")
                    elif puzzle_to_found == 0:
                        state.append("All puzzles in this room have been inspected")
    
    # On fait une assertion pour vérifier que state est non vide car sinon, cela veut dire que rien ne s'est passé
    assert state != []
    # On renvoie l'output dans l'historique
    return state

# Cette fonction permet de prendre un indice une fois qu'il a été trouvé/inspecté
# Une fois qu'un joueur a inspecté et pris un indice, on accroche le lien de l'item avec le joueur pour signifier que c'est lui qui le possède à présent
# l'item n'appartient donc plus à la pièce, mais au joueur
def take_request(r_player, r_item):
    # On lit le json contenant l'état du jeu
    game_data = read_json("evolving.json")
    
    # On init les variables nécessaires
    state = []
    ls_clues_in=[]
    ls_othters_clues=[]
    clue_to_take = 0
    # On init l'identifiant de l'item
    # On utilise la fonction check_type_item car l'item peut être deux type Clue ou de type dict, et on n'accede pas de la même manière à son identifiant
    id_item = check_type_item(r_item)
    
    # On affiche l'action effectuée
    state.append("The player " + r_player.name + " wants to take " + id_item)
    
    # On vérifie ici qu'il s'agit bien d'un indice
    # On doit donc aussi vérifier la connaissance du joueur
    if (r_item not in r_player.knowledge) and (r_item not in ls_clues_eg):
        state.append("We can only take clues")
        state.append("However " + id_item + " is not a clue")
        return state
    
    # On crée d'abord deux listes par item, une qui contient les indices de la salle des joueurs,
    # l'autre liste contient tous les autres indices
    for room in ls_rooms_eg:
        # Clues
        for item in room.clues:
            if r_player.name in room.players_in:
                ls_clues_in.append(item) # ici on crée la liste qui va contenir tous les indices de la salle où est le joueur
            else:
                ls_othters_clues.append(item)
    
    # INDICES
    # On check si on a affaire à un indice
    if "C" in id_item:
        # On doit ajouter l'indice dans la connaissance du joueur
        for item in ls_clues_in:
            if item.id == id_item:
                # On met la vérif avant pour ne pas que ça s'affiche après avoir pris l'item
                # On fait les vérifications pour les cas où l'indice est déjà pris ou pas encore inspecté
                if r_item in r_player.knowledge:
                    state.append("The clue " + id_item + " is already in the player knowledge")
                if r_item.found == False:
                    state.append("The clue " + id_item + " has not been inspected yet")
                # On vérifie que l'indice n'est pas déjà dans la connaissance du joueur et que l'item a été inspecté
                if r_item not in r_player.knowledge and r_item.found == True:
                    # Ici on ajoute l'indice à la connaissance du joueur
                    r_player.knowledge.append(r_item)
                    state.append(r_player.name + " take the clue " + id_item)
                    # On modifie le json, on récup d'abord le bon joueur
                    for player in ls_players_eg:
                        if r_player == player:
                            # Ici on vient récupérer l'index du joueur dans la liste
                            index = ls_players_eg.index(player)
                            game_data["Players"][index]["knowledge"].append(r_item.__dict__)# on convertit en dictionnaire car le type Clue n'est pas jsonable
                    # Ici on enlève l'indice de la listes des indices, comme ça on a plus que ceux qui ne sont pas encore trouvés
                    for room in ls_rooms_eg:
                        if r_player.name in room.players_in:
                            if r_item in room.clues:
                                room.clues.remove(r_item)
                                # On modifie le json
                                index = ls_rooms_eg.index(room) # L'index désigne la place de la salle dans la liste ls_rooms_eg
                                for clue in game_data["Rooms"][index]["clues"]:
                                    if clue["id"] == id_item:
                                        game_data["Rooms"][index]["clues"].remove(clue)
                    # On sauvegarde les modifications dans le json
                    update_json("evolving.json", game_data)
                    # On update la map pour afficher les joueurs dans l'autre pièce
                    update_game(["clues"])
                    
        # On regarde si l'indice est dans la liste des indices de la salle
        if r_item not in ls_clues_in:
            # Si l'indice n'est pas dans la salle et mais qu'il est dans l'autre liste, il est dans une autre salle
            if r_item in ls_othters_clues:
                state.append("The clue " + id_item + " is not in this room")
            # Sinon, cela veut dire que le joueur le connait déjà
            else:
                state.append("The clue " + id_item + " has already been picked up by a player")
        
        # Ici on va préciser s'il reste encore des indices à trouver et à prendre dans cette salle ou non
        for room in ls_rooms_eg:
            if r_player.name in room.players_in:
                # Ici on défini une variable afin de savoir s'il reste des indices dans la pièce
                clue_to_take = 0
                # Ensuite cette variable clue_to_take est incrémentée en fonction du nombre d'indices qu'elle possède encore
                for clue in room.clues:
                    # On doit ajouter cette vérification pour voir quel item est seulement grisé (donc a été inspecté mais pas pris)
                    if clue not in r_player.knowledge:
                        clue_to_take += 1
                # Ici on fait la vérification s'il reste des indices à trouver dans la pièce ou non
                if clue_to_take > 0:
                    state.append("There are still clues to take in this room")
                elif clue_to_take == 0:
                    state.append("All clues in this room have been taken")
    
    # On fait une assertion pour vérifier que state est non vide car sinon, cela veut dire que rien ne s'est passé
    assert state != []
    #On renvoie l'output dans l'historique
    return state
    
# Cette fonction permet de résoudre un puzzle une fois qu'il a été trouvé/inspecté (si le joueur est bien dans la pièce du puzzle)
# Remarque : dans cette fonction on va devoir faire pas mal attention au type des items car il sont soit des objets, soit des dict
def resolve_request(r_player, r_item):
    # On modifie le json pour mettre les joueurs dans l'autre salle
    # On lit le json contenant l'état du jeu
    game_data = read_json("evolving.json")
    
    # On init les variables nécessaires
    state = []
    counter = 0
    ls_clues_to_resolve_puzzle = []
    puzzle_can_be_open = False
    not_in_room = 0 # Pour savoir si le joueur est dans la même pièce que le puzzle
    # On init l'identifiant de l'item
    id_item = check_type_item(r_item)
    
    # On crée une liste avec tous les indices nécessaires à avoir pour résoudre le puzzle
    # On doit prendre en compte le cas où la liste d'indices est vide car tous les indices sont dans les joueurs et plus sur le plateau
    for player in ls_players_eg:
        for clue in player.knowledge:
            if type(clue) == dict:
                if clue["puzzle_id"] == id_item:# Ici ce sont des dictionnaires
                    # On doit ajouter des vérif car lors d'un partage, un même indice est possédé par plusieurs joueurs
                    if clue not in ls_clues_to_resolve_puzzle:
                        ls_clues_to_resolve_puzzle.append(clue)
            else:
                if clue.puzzle_id == id_item:# Ici ce sont des Clues
                    if clue not in ls_clues_to_resolve_puzzle:
                        ls_clues_to_resolve_puzzle.append(clue)
    # On doit quand même ajouter ceux du plateau s'il y en a pour être sûr de ne pas oublier
    for clue in ls_clues_eg:
        if clue.puzzle_id == id_item:
            if clue not in ls_clues_to_resolve_puzzle:
                ls_clues_to_resolve_puzzle.append(clue)
    
    # On affiche ce qu'il se passe
    state.append("The player " + r_player.name + " tries to solve a puzzle")
    
    # On vérifie ici qu'il s'agit bien d'un puzzle
    # On doit donc aussi vérifier l'inventaire du joueur
    if r_item not in ls_puzzles_eg:
        state.append(id_item + " is not a puzzle")
        return state
    
    # On vérifie que le joueur soit bien dans la puzzle du puzzle qu'il souhaite résoudre
    for room in ls_rooms_eg:
        if r_player.name in room.players_in:
            # On vérifie le type pour être sûr qu'on intéragit avec un puzzle et non un reward
            if type(r_item) == Puzzle or type(r_item) == dict:
                for clue in r_player.knowledge:
                    # On doit également vérifier que tous les indices sont bien dans la connaissance du joueur
                    # Pour cela on va incrémenter un counter chaque fois qu'un indice nécessaire est dans la connaissance du joueur
                    if clue in ls_clues_to_resolve_puzzle:
                        counter+=1
                # Si le counter est égal à la taille des indices à avoir, c'est que le joueur les a tous
                if counter == len(ls_clues_to_resolve_puzzle):
                    if r_item.found == True:
                        puzzle_can_be_open = True
                    # On doit vérifier si le puzzle est bien inspecté avant
                    else:
                        state.append(id_item + " has not been inspected")
                        return state
                    
            # Si le joueur possède les indices pour ouvrir le puzzle, on résout le puzzle
            if puzzle_can_be_open:
                # On doit check le type du puzzle pour accéder correctement aux éléments
                if type(r_item) == Puzzle:
                    rewards_in_item = r_item.rewards
                else:
                    rewards_in_item = r_item["rewards"]
                # On résout le puzzle et on doit gérer le cas où il possède plusieurs rewards
                for reward in rewards_in_item:
                    # On va d'abord vérifier le type de la récompense car si c'est un indice, c'est dans la connaissance qu'il faut la mettre, et non dans l'inventaire
                    # Si la récompense est un indice, on doit crée un dictionnaire pour l'ajouter à la connaissance du joueur et pour que ce soit exploitable comme un vrai un indice
                    if type(reward) == str and reward[0] == "C":
                        reward_must_be_in = r_player.knowledge
                        reward_must_be_in_json = "knowledge"
                        # On récupère l'indice et on reforme un Clue avec les valeurs correctes en fonction
                        splitted = reward.split(" ")
                        id_reward = splitted[0]
                        # On crée le dict
                        reward = {"id": id_reward, "puzzle_id": "P{}".format(id_reward[1]), "description": splitted[1], "meta": "", "found": True, "position": []}
                    else:
                        reward_must_be_in = r_player.inventory
                        reward_must_be_in_json = "inventory"
                    
                    # On vérifie si la récompense est déjà dans son inventaire
                    if reward not in reward_must_be_in:
                        # On ajoute la récompense dans le bon endroit en fonction du type de récompense
                        reward_must_be_in.append(reward)
                        # ne pas ouvlier d'enlever le puzzle de l'inventaire du joueur comme il a été résolu
                        room.puzzles.remove(r_item)
                        # On modifie le json pour dire qu'on lui ajoute la récompense
                        index = ls_players_eg.index(r_player)
                        game_data["Players"][index][reward_must_be_in_json].append(reward)
                        # On doit aussi mettre à jour le json pour retirer les items utilisés
                        # On doit vérifier s'il s'agit d'un dictionnaire ou pas car ça peut arriver
                        # On doit init l'index de la pièce pour accéder au bon endroit
                        index_room = ls_rooms_eg.index(room)
                        # On va donc devoir enlever le puzzle de la pièce, pour cela, on cherche le puzzle qui a le même id que celui qu'on veut résoudre
                        for puzzle in game_data["Rooms"][index_room]["puzzles"]:
                            # En fonction du type de r_item, on accède à son id pour comparer et trouver le puzzle
                            if type(r_item) == dict:
                                if puzzle["id"] == r_item["id"]:
                                    game_data["Rooms"][index_room]["puzzles"].remove(puzzle)
                            else:
                                if puzzle["id"] == r_item.id:
                                    game_data["Rooms"][index_room]["puzzles"].remove(puzzle)
                            
                        # Il faut également enlever tous les indices qui ont été utilisés
                        # On va utiliser une liste en compréhension pour être sûr de conserver tous les items à ne pas utiliser
                        # En effet, faire une boucle for avec un remove dedans c'est risqué de ne pas passer par tous les éléments
                        # On va donc parcourir la liste et conserver les indices qui ne sont pas en rapport avec le puzzle
                        for player in ls_players_eg:# On doit le faire pour tous les joueurs au cas où deux joueurs se seraient partagé un indice
                            # On le fait séparemment, sinon l'autre joueur gagnera les indices de l'autre sans partage, ici on veut seulement lui enlever les siens en trop
                            player.knowledge = [clue_play for clue_play in player.knowledge if (type(clue_play) == dict and clue_play["puzzle_id"] != id_item) or (type(clue_play) == Clue and clue_play.puzzle_id != id_item)]
                            index_here = ls_players_eg.index(player)
                            game_data["Players"][index_here]["knowledge"] = [clue_play for clue_play in game_data["Players"][index_here]["knowledge"] if clue_play["puzzle_id"] != id_item]
                            
                        # On précise qu'on a eu une récompense
                        state.append(r_player.name + " solved the puzzle and gets a reward")
                        
                        # En effet, si c'est un puzzle, reward n'est pas un str mais un Clue
                        if type(reward) == dict:
                            state.append("The player " + r_player.name + " got " + reward["id"])
                        else:
                            state.append("The player " + r_player.name + " got " + reward)
                        
                        # On sauvegarde les modifications dans le json
                        update_json("evolving.json", game_data)
                        # On update la map pour afficher la porte ouverte
                        update_game(["all"])
                        
                    # Si oui, on le précise
                    else:
                        state.append("The player already has this reward")
            # Si le joueur n'a pas les indices, on le précise
            else:
                state.append(r_player.name + " does not have the necessary clues")
        # Si le joueur n'est pas dans la même pièce que le puzzle, on incrémente une valeur
        else:
            not_in_room+=1
    # Si cette valeur est égale au nombre de pièce, c'est qu'on a fait le tour des toute les pièces sans trouver le joueur
    if not_in_room == len(ls_rooms_eg):
        state.append(r_player.name + " is not in the same room as " + id_item)
        
    # Ici on reprend le cas où c'est une clé pour ouvrir une porte car on ouvre la porte direct
    for reward in r_player.inventory:
        # On vérifie bien le reward
        if type(reward) == str and reward[0] == "D":
            # On split pour récup l'id de la porte
            reward_split = reward.split(" ")
            reward_id = reward_split[0]
            state.append(r_player.name + " found the key to the door " + reward_id)
            # Vu que c'est un clé, on ouvre la porte correspondante
            for door in ls_doors_eg:
                if door.id == reward_id:
                    # On ouvre donc la porte dans le json
                    # On va chercher l'index pour modifier le json et la liste
                    index = ls_doors_eg.index(door)
                    game_data["Doors"][index]["opened"] = True
                    ls_doors_eg[index].opened = True
                    # Il ne faut pas oublier de retirer la récompense car elle a été utilisée
                    index2 = ls_players_eg.index(r_player)
                    game_data["Players"][index2]["inventory"].remove(reward)
                    ls_players_eg[index2].inventory.remove(reward)
                    
                    # On précise que la porte a été ouverte
                    state.append(r_player.name + " opens the door with the key")
                    
                    # On sauvegarde les modifications dans le json
                    update_json("evolving.json", game_data)
                    # On update la map pour afficher la porte ouverte
                    update_game(["all"])
                    
        # Si jamais on arrive ici, c'est que la récompense n'est pas une clé           
        if r_player.inventory != []:
            state.append("The reward is not a key")
    
    # On fait une assertion pour vérifier que state est non vide car sinon, cela veut dire que rien ne s'est passé
    assert state != []
    # On renvoie l'output dans l'historique
    return state
    
# Cette fonction permet à deux joueur dans la même pièce de partager un indice
def share_request(r_player, r_item):
    # On modifie le json pour mettre les joueurs dans l'autre salle
    # On lit le json contenant l'état du jeu
    game_data = read_json("evolving.json")
    
    # On init les variables nécessaires
    state = []
    # On init l'identifiant de l'item
    id_item = check_type_item(r_item)
    
    # On affiche ce qu'il se passe
    state.append("The player " + r_player.name + " wants to share his clues")
    
    # On vérifie ici qu'il s'agit bien d'un indice
    # On doit donc aussi vérifier l'inventaire et la connaissance du joueur
    if r_item not in r_player.knowledge and r_item not in ls_clues_eg:
        state.append(id_item + " is not a clue")
        return state
    
    # On va chercher les indices dans les connaissances du joueur pour les partager aux autres
    # On vérifie que le joueur possède bien des indices
    if r_player.knowledge != []:
        for other_player in ls_players_eg:
            if r_player != other_player: # On vérifie bien que le joueur demandé est différent des autres joueurs
                # On doit vérifier que les joueurs soient bien dans la même pièce
                for room in ls_rooms_eg:
                    # Si les deux joueurs sont dans la même pièce, c'est bon
                    if r_player.name in room.players_in and other_player.name in room.players_in:
                        if (r_item in r_player.knowledge) and (r_item not in other_player.knowledge): # on vérifie que l'indice est bien dans les connaissances du joueur et pas des autres
                            other_player.knowledge.append(r_item)
                            # On définit l'index qui est tout simplement la place des autres joueurs dans la liste ls_players_eg
                            index = ls_players_eg.index(other_player)
                            game_data["Players"][index]["knowledge"].append(r_item.__dict__)# on doit ajouter en dict car c'est ce qu'on fait avec take_request()
                            # On affiche le message qui dit que tout le monde possède maintenant les indices
                            state.append("Now " + other_player.name + " also has the clue " + id_item)
                            
                            # On sauvegarde les modifications dans le json
                            update_json("evolving.json", game_data)
                            # On le met ici comme ça on passe le reste du code
                            return state
                        # Dans le cas où l'indice est déjà connu des autres, on le précise
                        if r_item in other_player.knowledge:
                            state.append(other_player.name + " already has the clue " + id_item)
                        # Dans le cas où l'indice n'est pas connu du joueur, on le précise
                        if r_item not in r_player.knowledge:
                            state.append(r_player.name + " has not the clue " + id_item)
                    # Si les joueurs ne sont pas dans la même pièce, on le précise
                    if r_player.name in room.players_in and other_player.name not in room.players_in:
                        state.append("Players " + r_player.name + " and " + other_player.name + " are not in the same room")
                        
    # Si le joueur ne possède pas d'indices, on le précise
    else:
        state.append(r_player.name + " has not clues")
    
    # On fait une assertion pour vérifier que state est non vide car sinon, cela veut dire que rien ne s'est passé
    assert state != []
    # On renvoie l'historique de l'action
    return state

# Cette fonction permet à un joueur de se déplacer d'une pièce à l'autre
def move_request(r_player, r_item):
    # On modifie le json pour mettre les joueurs dans l'autre salle
    # On lit le json contenant l'état du jeu
    game_data = read_json("evolving.json")
    
    # On init les variables nécessaires
    state = []
    doors_can_be_open = []
    # On va init une variable pour savoir si on passer la porte en avant ou en arrière (ex: Start->R2 = avant & R2->Start = arrière)
    sens = 0
    # On init l'identifiant de l'item
    id_item = check_type_item(r_item)
    
    # On affiche ce qu'il se passe
    state.append("The player " + r_player.name + " wants to go to another room")
    
    # On vérifie ici qu'il s'agit bien d'une porte
    if r_item not in ls_doors_eg:
        state.append(id_item + " is not a door")
        return state
    
    # On affiche quelle porte le joueur a choisit
    state.append(r_player.name + " walks towards the door " + id_item)
    
    # On vérifie les portes de la salle, on ajoute les portes que l'on peut ouvrir dans la salle
    for room in ls_rooms_eg:
        if r_player.name in room.players_in:
            # On vérifie donc si on va en avant ou en arrière
            if r_item.connexion[0] == room.id: # Ce cas-ci c'est quand on va en avant
                sens = 1
            if r_item.connexion[1] == room.id:
                sens = 0
            if r_item.connexion[0] == room.id or r_item.connexion[1] == room.id:
                id_door = (id_item + " true")# on fait cela pour simuler el fait qu'on ait une clé
                # Soit on a la clé d'un puzzle, soit la porte est déjà ouverte
                if id_door in r_player.inventory:
                    doors_can_be_open.append(r_item)
                    # On va ouvrir les portes dans le json
                    index = ls_doors_eg.index(r_item)
                    
                    # On vérifie si la porte a déjà été ouverte ou pas à l'affichage
                    if ls_doors_eg[index].opened != True:
                        game_data["Doors"][index]["opened"] = True
                        ls_doors_eg[index].opened = True
                        
                        # Une fois arrivé ici, on peut sauvegarder les modifications dans le json car elles sont faites
                        update_json("evolving.json", game_data)
                        # On update la map pour afficher les joueurs dans l'autre pièce
                        update_game(["all"])
                
                # Ici on ajoute les portes ouvrables        
                if r_item.opened == True:
                    doors_can_be_open.append(r_item)
                    
            # Ici on vérifie si la porte est dans la salle, sinon on le précise et on return direct pour ne pas passer dans le reste du code
            else:
                state.append("The door " + id_item + " is not in this room")
                return state
            
    # On vérifie si des portes peuvent s'ouvrir et si celle souhaitée en fait partie
    if doors_can_be_open != []:
        state.append(r_player.name + " opens the door " + id_item)
        state.append("The player arrives in front of " + r_item.connexion[sens]) # sens désigne la salle où on va
        # On va donc mettre à jour le json
        # On récupère d'abord les bonnes chambres à modifier
        for room in ls_rooms_eg:
            # On va définir l'index qui représente la salle
            index = ls_rooms_eg.index(room)
            
            if r_item.connexion[0] == ls_rooms_eg[index].id:
                # Si on va en avant, on vide la première salle
                if sens == 1:
                    # salle où les joueurs sont
                    game_data["Rooms"][index]["players_in"].remove(r_player.name)
                    ls_rooms_eg[index].players_in.remove(r_player.name)
                # Sinon on remplit la première
                else:
                    # On ne fait bouger qu'un joueur
                    # salle où le joueur va
                    game_data["Rooms"][index]["players_in_front"].append(r_player.name)
                    ls_rooms_eg[index].players_in_front.append(r_player.name)
                    
            if r_item.connexion[1] == ls_rooms_eg[index].id:
                # Si on va en arrière, on remplit la deuxième salle
                if sens == 0:
                    # salle où les joueurs sont
                    game_data["Rooms"][index]["players_in"].remove(r_player.name)
                    ls_rooms_eg[index].players_in.remove(r_player.name)
                # Sinon on vide la deuxième salle
                else:
                    # salle où le joueur va
                    game_data["Rooms"][index]["players_in_front"].append(r_player.name)
                    ls_rooms_eg[index].players_in_front.append(r_player.name)
                        
                # Une fois arrivé ici, on peut sauvegarder les modifications dans le json car elles sont faites
                update_json("evolving.json", game_data)
                # On update la map pour afficher les joueurs dans l'autre pièce
                update_game(["players"])
                        
    # Sinon, on le précise
    else:
        # On ajoute une condition au cas où le user oublierait d'intéragir avec la pièce
        state.append(r_player.name + " is at the door")
        state.append("You must first interact with the room to enter it")
        state.append("The door can not open")
    
    # On fait une assertion pour vérifier que state est non vide car sinon, cela veut dire que rien ne s'est passé
    assert state != []
    # On renvoie l'output dans l'historique
    return state

# Cette fonction permet de terminer l'EG car c'est elle qui fait sortir les joueurs de celui-ci
def exit_request(r_player, r_item):
    # On modifie le json pour mettre les joueurs dans l'autre salle
    # On lit le json contenant l'état du jeu
    game_data = read_json("evolving.json")
    
    # On init l'état du jeu
    state = []
    
    # On affiche ce qu'il se passe
    state.append("The player " + r_player.name + " must come out of the Escape Game")
    
    # On vérifie ici qu'il s'agit bien d'une porte
    if r_item != "Exit":
        state.append(id_item + " is not the Exit room")
        return state
    
    # Ici on va vérifier que les joueurs sont bien dans la dernière salle
    for room in ls_rooms_eg:
        if r_player.name in room.players_in:
            if room.id == "Exit":
                # Si les joueurs sont dans la dernière pièce, c'est gagné
                index = ls_rooms_eg.index(room)
                game_data["Rooms"][index]["players_in"] = []
                ls_rooms_eg[index].players_in = []
                # On précise que les joueurs ont gagné
                state.append("!!! Congratulations, you solved the Escape Game!!!")
                
                # Une fois arrivé ici, on peut sauvegarder les modifications dans le json car elles sont faites
                update_json("evolving.json", game_data)
                # On update la map pour afficher les joueurs dans l'autre pièce
                update_game(["players"])
                
                # On renvoie l'état du jeu
                return state
            
    # S'ils n'y sont pas            
    for room in ls_rooms_eg:            
        # Si les joueurs ne sont pas présents dans la pièce, on le précise
        if r_player.name not in room.players_in:
            state.append("The player " + r_player.name + " is not in the last room")
            # On renvoie direct l'info pour pas l'afficher plusieurs fois
            return state
    
    # On fait une assertion pour vérifier que state est non vide car sinon, cela veut dire que rien ne s'est passé
    assert state != []
    # On renvoie l'état du jeu
    return state

# Cette fonction permet de sauvegarder l'état du jeu dans un fichier json à part
def save_json():
    # On lit le json de base
    data = read_json("evolving.json")
    # On sauvegarde un json qui contient l'état du jeu au départ avant la partie
    update_json("saved.json", data)
    
    # En plus de la sauvegarde, on va ajouter un message pour montrer que l'on sauvegarde
    # Cette manipulation sert à améliorer l'UX
    
    # On affiche un texte qui dit que le fichier est en train d'être sauvegardé
    json_is_saving_text.grid(column=0, row=0, sticky="W, N")
    # Après 2 secondes, on enlève le message
    window.after(2000, lambda: json_is_saving_text.grid_remove())
    # 0.1 secondes après avoir enlevé le message, on indique que le fichier est bien save
    window.after(2100, lambda: saved_text.grid(column=0, row=0, sticky="W, N"))
    # 2.5 secondes après on enlève finalement le message (4.6 - 2.1 = 2.5)
    window.after(4600, lambda: saved_text.grid_remove())
    
# Cette fonction permet de recharger le placement des éléments sur le plateau
# C'est une alternative au problème de chevauchement possible d'items
def reload_map():
    # On appelle tout simplement la fonction en-dessous qui recharge les items sur la carte, 
    # mais on le fait ici pour pouvoir l'assigner au bouton reload plus bas
    update_game(["all"])
    
# Cette fonction va chercher les items à afficher dans le combobox (liste des requêtes)
def get_relevant_items():
    # On init la liste qui contiendra les items à afficher
    ls_items = []
    
    # On ajoute tous les items du jeu (pas juste l'id, tout l'item)
    for room in ls_rooms_eg:
        ls_items.append(room)
        # On imbrique pour pouvoir mettre les items par pièce
        for clue in room.clues:
            ls_items.append(clue)
        for puzzle in room.puzzles:
            ls_items.append(puzzle)
    for door in ls_doors_eg:
        ls_items.append(door)
        
    # On doit également ajouter les items qui sont dans le stockage des joueurs
    # Si les joueurs possèdent des items, c'est qu'ils serviront encore pour le jeu
    for player in ls_players_eg:
        for clue_play in player.knowledge:
            if clue_play not in ls_items:
                ls_items.append(clue_play)
        for puzzle_play in player.inventory:
            if puzzle_play not in ls_items:
                ls_items.append(puzzle_play)
    
    # On va mettre une assert pour vérifier que la liste retournée contient bien des items
    assert ls_items != []
    # On renvoie la liste l'items du jeu
    return ls_items

# Cette fonctino gère la jouabilité entièrement grâce aux appels des fonctions précédentes
def set_game(request):
    # On init les variables utilisables
    ls_players = ls_players_eg
    ls_items = get_relevant_items() # Ici on stocke tous les items du jeu
    state=[]

    # Ici on stocke les différentes requêtes
    req_action = request[1]
    req_player = request[0]
    req_item = request[2]

    # On va itérer pour avoir chaque joueur et item pour pouvoir sélectionner ceux choisit par le joueur en input
    for player in ls_players:
        for item in ls_items:
            # On check si on a affaire à un dict ou à un item Clue, Puzzle, etc
            id_item = check_type_item(item)
            if player.name == req_player:
                if id_item == req_item:
                    # Ici on gère toutes les actions de requête possibles
                    if req_action == "Interact":
                        # On appelle la fonction plus haut
                        state = interact_request(player, item)
                        # On renvoie ce qu'il se passe   
                        return state
                    if req_action == "Inspect":
                        # On appelle la fonction plus haut
                        state = inspect_request(player, item)
                        # On renvoie ce qu'il se passe   
                        return state
                    if req_action == "Take":
                        # On appelle la fonction plus haut
                        state = take_request(player, item)
                        # On renvoie ce qu'il se passe   
                        return state
                    if req_action == "Resolve":
                        # On appelle la fonction plus haut
                        state = resolve_request(player, item)
                        # On renvoie ce qu'il se passe   
                        return state
                    if req_action == "Share":
                        # On appelle la fonction plus haut
                        state = share_request(player, item)
                        # On renvoie ce qu'il se passe   
                        return state
                    if req_action == "Move":
                        # On appelle la fonction plus haut
                        state = move_request(player, item)
                        # On renvoie ce qu'il se passe   
                        return state
                    if req_action == "Exit":
                        # On appelle la fonction plus haut
                        state = exit_request(player, item)
                        # On renvoie ce qu'il se passe   
                        return state

# On init cette liste pour la fonction update_historiques()
# On doit la mettre en dehors car elle ne doit être initialisée qu'une fois au départ de la partie
ls_requests=[]

# Cette fonction permet de mettre à jour la boîte de dialogue qui représente l'historique du jeu
# On peut grâce à cela voir textuellement se qu'il se passe dans l'EG
def update_historique():
    # On récup les données depuis les compobox
    selected_player = request_player.get()
    selected_action = request_action.get()
    selected_item = request_item.get()
    # On crée une requête avec les deux infos
    complete_request = [selected_player, selected_action, selected_item]
    # On crée une liste contenant toutes les requêtes pour faire ce qu'il faut juste après
    ls_requests.append(complete_request)
    # On récupère l'état du jeu via la fonction set_game()
    state_game = set_game(complete_request)
    
    # On gère le cas où un input est vide
    if selected_player == "" or selected_action == "" or selected_item == "":
        return False
    
    # On vérifie que la requête est bien remplie
    if (ls_requests[-1] != ["",""]):
        input_req = "In : " + str(ls_requests[-1]) # On doit mettre str sinon pas de concat entre str et list
        historique.insert(1000, input_req) # On met ici 1000 histoire d'être sûr que la requête sera affichée après la précédente
        # On affiche ce qu'il se passe dans la partie
        # On fait une boucle pour les états de jeu où il y a plusieurs prints
        state_game_size = len(state_game)
        if state_game_size > 0:
            for i in range(state_game_size):
                output_req = "Out : " + str(state_game[i])
                historique.insert(1001+i, output_req)
    
    # On fait une assertion pour vérifier que complete_request est non vide car sinon, cela veut dire que rien ne s'est passé
    assert complete_request != []
    # On vérifie également que la liste de requête contient bien les 3 éléments nécessaires pour réaliser une requête
    assert len(complete_request) == 3
    # On renvoie la requête
    return complete_request


# CREATION DE LA FENETRE TKINTER

# On crée une fenêtre avec certains paramètres
window = tkinter.Tk()
window.title("FORM-ESC - Escape Game Representation")
window.minsize(1280, 720)

# Création de la hiérarchie des widgets

# On crée le premier cadre qui va contenir tout
content = ttk.Frame(window)
# On crée chaque cadre respectif pour les infos, actions, légende et affichage de l'EG
actions_frame = ttk.Frame(content, borderwidth=5, relief="ridge", width=200, height=100)
legend_frame = ttk.Frame(content, borderwidth=5, relief="ridge", width=200, height=100)
eg_frame = ttk.Frame(content, borderwidth=5, relief="ridge", width=500, height=350)
# On dispose les cadres sur la fenetre
content.grid(column=0, row=0, sticky=(N, W, E, S)) # Ici il est présent partout
actions_frame.grid(column=0, row=0, sticky=(N, W, E, S)) # Ici c'est la première colonne et la première ligne, j'ai enlevé l'E pour ne pas prendre la moitié de l'écran
legend_frame.grid(column=0, row=1, sticky=(N, W, E, S)) # Ici c'est la première colonne et la deuxième ligne
eg_frame.grid(column=1, row=0, columnspan=1, rowspan=2, sticky=(N, W, E, S)) # Ici c'est la deuxième colonne et les deux lignes (rowspan=2)

# Création hiérarchie dans actions_frame
act_frame = ttk.Frame(actions_frame, borderwidth=5, relief="ridge", width=150, height=100) # padding=(10, 10, 10, 10)
action_text = ttk.Label(act_frame, text="Requests", font=("Arial", 20))

# Il faut définir les textvariable à quelque chose, sinon on peut pas y accéder
request_player = tkinter.StringVar()
request_action = tkinter.StringVar()
request_item = tkinter.StringVar()

# On récupère tous les items du jeu
# On init la liste ici pour ajouter les id ensuite
ls_all_items = []
ls_all_items = get_relevant_items()

# On crée une nouvelle liste pour pouvoir récupérer seulement les identifiants des items
ls_all_items_id=[]
# On ajoute les items en fonction de leur type
for item in ls_all_items:
    if type(item) == dict:
        ls_all_items_id.append(item["id"])
    else:
        ls_all_items_id.append(item.id)

# ACTION FRAME
# On crée les combobox qui vont contenir les requêtes pour permettre la jouabilité
request_selection_player = ttk.Combobox(act_frame, width=8, textvariable=request_player, state="readonly", values=ls_players)# on met les listes créées dans create_object pour proposer chaque fois en fct du json
request_selection_action = ttk.Combobox(act_frame, width=15, textvariable=request_action, state="readonly", values=ls_actions)
request_selection_item = ttk.Combobox(act_frame, width=5, textvariable=request_item, state="readonly", values=ls_all_items_id)
# Bouton pour lancer la requête
play_request = ttk.Button(act_frame, text="Go", width=5, command=update_historique)

display_act_frame = ttk.Frame(actions_frame, borderwidth=5, relief="ridge", width=150, height=100)
display_text = ttk.Label(display_act_frame, text="Move log", font=("Arial", 15))
display_canva = Canvas(display_act_frame,  scrollregion =(0, 0, 1000, 1000), width=400, height=400, bg='ivory')

historique = Listbox(display_canva, width=50)

# On dispose les éléments dans les cadres
act_frame.grid(column=0, row=0) # sticky=(N, W, E, S)
action_text.grid(column=0, row=0, columnspan=4, rowspan=1)
request_selection_player.grid(column=0, row=1)
request_selection_action.grid(column=1, row=1)
request_selection_item.grid(column=2, row=1)
play_request.grid(column=3, row=1)

# Ceci contiendra toutes les actions réalisées précédemment (historique)
display_act_frame.grid(column=0, row=1, sticky=(S))
display_text.grid(column=0, row=0)

display_canva.grid(column=0, row=1)

historique.grid(column=0, row=0)

# LEGEND FRAME
# Création hiérarchie dans legend_frame
label_frame = ttk.Frame(legend_frame, borderwidth=5, relief="ridge", width=150, height=100)
legend_text = ttk.Label(label_frame, text="Legend", font=("Arial", 20))

# Il faut créer un canvas pour pouvoir accueillir les représentations des objets
room_frame = ttk.Frame(legend_frame, borderwidth=5, relief="ridge", width=150, height=100)
room_text = ttk.Label(room_frame, text="Room :", font=("Arial", 15))
canva_room = Canvas(room_frame, bg="white", height=40, width=60)
room_icon = canva_room.create_rectangle(10,10,35,35, fill="lightgrey", width=2)

player_frame = ttk.Frame(legend_frame, borderwidth=5, relief="ridge", width=150, height=100)
player_text = ttk.Label(player_frame, text="Player :", font=("Arial", 15))
canva_player = Canvas(player_frame, bg="white", height=40, width=60)
player_icon = canva_player.create_oval(10, 15, 25, 30, width=1, outline="black", fill="blue")

door_frame = ttk.Frame(legend_frame, borderwidth=5, relief="ridge", width=150, height=100)
door_text = ttk.Label(door_frame, text="Door :", font=("Arial", 15))
canva_door = Canvas(door_frame, bg="white", height=40, width=80)
# On met une image pour chaque état possible de la porte
door_icon_open = canva_door.create_line(10, 10, 35, 35, width=5, fill="lightgreen")
door_icon_closed = canva_door.create_line(40, 10, 65, 35, width=5, fill="red", dash = 5)

puzzle_frame = ttk.Frame(legend_frame, borderwidth=5, relief="ridge", width=150, height=100)
puzzle_text = ttk.Label(puzzle_frame, text="Puzzle :", font=("Arial", 15))
canva_puzzle = Canvas(puzzle_frame, bg="white", height=40, width=60)
# Il faut init l'image du puzzle et la dézoomer en dehors d'une fonction
# Remarque : j'ai dû mettre un autre nom de variable que img_puzzle sinon il y avait conflit
icon_puzzle = PhotoImage(file="images/puzzle.png")
# On "dézoom" sur l'image pour la réduire
icon_puzzle = icon_puzzle.subsample(15)
puzzle_icon = canva_puzzle.create_image(20, 20, image=icon_puzzle)

clue_frame = ttk.Frame(legend_frame, borderwidth=5, relief="ridge", width=150, height=100)
clue_text = ttk.Label(clue_frame, text="Clue :", font=("Arial", 15))
canva_clue = Canvas(clue_frame, bg="white", height=40, width=60)
# Il faut init l'image du puzzle et la dézoomer en dehors d'une fonction
icon_clue = PhotoImage(file="images/loupe.png")
# On "dézoom" sur l'image pour la réduire
icon_clue = icon_clue.subsample(20)
clue_icon = canva_clue.create_image(20, 20, image=icon_clue)

# On dispose les éléments dans les cadres
# J'ai mis un padding y à 20 pour ne pas que le "Légende" et les autres mots soient collés
label_frame.grid(column=0, row=0, pady=20)
legend_text.grid(column=0, row=0)

# Ici j'ai mis tous les cadres orienté ouest pourqu'ils soient collés à gauche et que je puisse mettre le text "Légende" au centre
room_frame.grid(column=0, row=1, sticky=(W))
room_text.grid(column=0, row=0)
canva_room.grid(column=1, row=0)

player_frame.grid(column=0, row=2, sticky=(W))
player_text.grid(column=0, row=0)
canva_player.grid(column=1, row=0)

door_frame.grid(column=0, row=3, sticky=(W))
door_text.grid(column=0, row=0)
canva_door.grid(column=1, row=0)

puzzle_frame.grid(column=0, row=4, sticky=(W))
puzzle_text.grid(column=0, row=0)
canva_puzzle.grid(column=1, row=0)

clue_frame.grid(column=0, row=5, sticky=(W))
clue_text.grid(column=0, row=0)
canva_clue.grid(column=1, row=0)

# EG FRAME
# Création hiérarchie dans eg_frame

# Frame qui va contenir toute la partie du dessus
frame_text_labels = ttk.Frame(eg_frame, borderwidth=5, relief="ridge", width=150, height=100)

# On va mettre ces boutons dans une frame spécifique
maj_frame = ttk.Frame(frame_text_labels, borderwidth=5, relief="ridge", width=150, height=100)
label_maj = ttk.Label(maj_frame, text="Functions", font=("Arial", 20))
# Bouton qui va permettre de recharger la map afin de replacer les items pour qu'ils soient tous cliquables facilement (alternative aux chevauchements d'items)
reload_btn = ttk.Button(maj_frame, text="Refresh", width=15, command=reload_map)
# Bouton de sauvegarde de l'état du jeu
save_button = ttk.Button(maj_frame, text="Save", width=15, command=save_json)

# On va utiliser la fonction pour lire le json et attribuer le nom de l'EG
data_for_name_eg = read_json("evolving.json")
# On assigne la variable eg_name au nom choisit par l'utilisateur dans le fichier json pour différencier son escape game
eg_name = data_for_name_eg["EG"]["name"]

# On met tout pour afficher le titre
label_eg_frame = ttk.Frame(frame_text_labels, borderwidth=5, relief="ridge", width=150, height=100)
eg_text = ttk.Label(label_eg_frame, text=eg_name, font=("Arial", 30)) # font(police, taille)

# Frame qui contiendra les boutons pour les graphes
graph_eg_frame = ttk.Frame(frame_text_labels, borderwidth=5, relief="ridge", width=150, height=100)
label_graph_eg = ttk.Label(graph_eg_frame, text="Graphs", font=("Arial", 20))
static_graph_btn = ttk.Button(graph_eg_frame, text="Static Graph", width=15, command=display_static_graph)
dynamic_graph_btn = ttk.Button(graph_eg_frame, text="Dynamic Graph", width=15, command=display_dynamic_graph)

# Canva pour l'escape game
visu_eg_frame = ttk.Frame(eg_frame, borderwidth=5, relief="ridge")
visu_eg_canvas = Canvas(visu_eg_frame, bg="white")

# Texte pour dire que l'on charge la sauvegarde du fichier json
json_is_saving_text = Label(visu_eg_frame, bg="white", text="The game is saving...", font=("Arial", 14))
# Si on veut personnaliser le texte, c'est mieux de créer un label simple natif de tkinter (sans ttk)
saved_text = Label(visu_eg_frame, bg="white", text="The game has been saved into the saved.json file", font=("Arial", 14))

# Frame qui contient tout le dessus de eg_frame
frame_text_labels.grid(column=0, row=0)

# On met ces deux boutons dans un frame à part
maj_frame.grid(column=0, row=0)
label_maj.grid(column=0, row=0, columnspan=2)
reload_btn.grid(column=0, row=1)
save_button.grid(column=1, row=1)

# On dispose pour afficher le titre
label_eg_frame.grid(column=1, row=0, padx=(100, 100))# On ajoute du padding pour écarter équitablement les deux frames du milieu
eg_text.grid(column=1, row=0)

# On met les boutons dans la frame faite pour
graph_eg_frame.grid(column=2, row=0)
label_graph_eg.grid(column=0, row=0, columnspan=2)
static_graph_btn.grid(column=0, row=1)
dynamic_graph_btn.grid(column=1, row=1)

# Ce cadre va contenir toute la visualisation de l'EG
visu_eg_frame.grid(column=0, row=1, sticky=(N, W, E, S), columnspan=3)# On précise que celui-ci peut déborder sur tout l'écran
visu_eg_canvas.grid(column=0, row=0, sticky=(N, W, E, S))

# Ici on va ajouter les poids du redimensionnement des widgets
# Le poids étant la proportion que l'on laisse au widget pour s'élargir
# Ici on met le poids à 1 pour que ça change comme la fenetre
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)
# Ici on spécifie les poids en fonction des cadres
content.columnconfigure(0, weight=1) # actions_frame & legend_frame
content.columnconfigure(1, weight=500) # eg_frame, je l'ai mis vraiment grand pour qu'il prenne bien la place
content.rowconfigure(0, weight=4) # actions_frame
content.rowconfigure(1, weight=1) # legend_frame

# Les poids des plus petits cadres

# poids du cadre où on affiche l'EG
eg_frame.columnconfigure(0, weight=3)
eg_frame.rowconfigure(1, weight=3)
visu_eg_frame.columnconfigure(0,  weight=3)
visu_eg_frame.rowconfigure(0,  weight=3)
visu_eg_canvas.columnconfigure(0, weight=3)
visu_eg_canvas.rowconfigure(0,  weight=3)

# poids du cadre où on affiche la légende
legend_frame.columnconfigure(0, weight=1)

# Ici on check les infos des fenetres, on est obligé de passer par la méthode update()
window.update()
content.update()
eg_frame.update()
label_eg_frame.update()
visu_eg_frame.update()

# FONCTIONS DE PLACEMENT DES ELEMENTS

# Fonction qui pose une porte en fonction d'une salle
def place_door(rooms, doors):
    # Pour poser les portes, on doit récupérer les positions des salles
    for door in doors:
        room_start_id = door.connexion[0]
        room_end_id = door.connexion[1]
        # On assigne les positions des portes en fonction de la position des pièces
        for room in rooms:
            if room.id == room_start_id:
                door_start = (room.position[0] + 50, room.position[1] + 50)
            if room.id == room_end_id:
                door_end = (room.position[0] + 50, room.position[1] + 50)
        # On ajoute la position dans l'objet Door direct et pas dans create_door pour la pop up
        door.position_start = door_start
        door.position_end = door_end
        # Finalement on crée l'objet Door avec ces positions
        door_test = door.create_door(visu_eg_canvas)

# Cette fonction permet de placer les pièces de façon à ce que la disposition de celles-ci soit similaire à la disposition des pièces dans le graphe statique
def place_room(rooms):
    # Finalement on va essayer de gérer plusieurs cas en utilisant une certaine forme
    # On va donc vérifier le nombre de salles pour pouvoir construire l'EG
    # Ce sont les tailles un fois mis en grande fenêtre
    h_canvas = 722
    w_canvas = 1086
    # Ici on récupère le centre du canva pour centrer au maximum la représentation
    canva_center = (w_canvas/2, h_canvas/2)
    
    # Ici on appelle la fonction qui crée le graphe et récupère seulement la position des pièces
    ls_pos_rooms = set_coords_static_graph()
    
    # Ensuite on assigne les mêmes coordonnées du graphe à la visualisation de l'EG
    for room in ls_rooms_eg:
        for pos in ls_pos_rooms:
            # On check qu'ils ont le même index
            if ls_rooms_eg.index(room) == ls_pos_rooms.index(pos):
                room.position = pos
                
    # On créer et affiche les pièces sur l'interface
    for room in ls_rooms_eg:
        room.create_room(visu_eg_canvas)

# Cette fonction doit afficher des joueurs dans une salle
def place_player(rooms, players):
    for room in rooms:
        for player in players:
            # Si les joueurs doivent être représentés dans la pièce
            if player.name in room.players_in:
                # Le joueur doit être dans la salle
                # Exemple : Le joueur doit donc être compris entre 100 et 220 & 200 et 320
                # Le problème si on met les valeurs exacts, il est possible que le cercle sorte un peu de la salle à cause de sa position et de sa taille
                # Il faut donc choisir un chiffre arbitraire pour être sûr qu'il soit dedans (// au padding)
                coord0_room = (room.position[0], room.position[0]+120)
                coord1_room = (room.position[1], room.position[1]+120)
                # On diminue la zone d'apparition pour être sûr que ce soit dedans
                new_coord0 = coord0_room[1] - 20
                new_coord1 = coord1_room[1] - 20
                # Ici on fait random pour avoir une valeur aléatoire, et donc positionner l'item dans la pièce mais où on veut
                pos0 = random.randint(coord0_room[0], new_coord0)
                pos1 = random.randint(room.position[1], new_coord1)
                position = [pos0, pos1]
                # On ajoute la position dans l'objet Door direct et pas dans create_door pour la pop up
                player.position = position
                player_test = player.create_player(visu_eg_canvas, 8)
                
            # Si les joueurs doivent être représentés devant la pièce
            if player.name in room.players_in_front:
                # On leur donne des coordonnées juste devant la pièce
                coord_x = room.position[0] -15
                coord_y = room.position[1] -15
                # On va faire un randint pour les dispatcher sur le côté supérieur gauche de la pièce (convention arbitraire)
                # Il va falloir faire 2 randint différents pour faire afficher autour du coin, et pas faire un carré
                # On a une chance sur deux que ce soit sur le côté gauche, sinon c'est au-dessus (le coin gauche quoi)
                on_left = random.randint(0,1)
                # Si on va sur le côté gauche, c'est le y qu'on peut changer
                if on_left == 1:
                    coord_y = random.randint(coord_y, coord_y + 50)
                # Sinon, c'est le x qu'on peut changer
                if on_left == 0:
                    coord_x = random.randint(coord_x, coord_x + 50)
                # On assigne finalement les coordonées
                position = [coord_x, coord_y]
                # On ajoute la position dans l'objet Door direct et pas dans create_door pour la pop up
                player.position = position
                player_test = player.create_player(visu_eg_canvas, 8)
                
# On va maintenant setup l'image du puzzle ici, on fait ça pour l'image du puzzle, et celle du puzzle inspecté

# On doit le mettre ici car ça marche pas si dans la fonction
# Il faut init l'image du puzzle et la dézoomer en dehors d'une fonction
img_puzzle = PhotoImage(file="images/puzzle.png")
# On "dézoom" sur l'image pour la réduire
img_puzzle = img_puzzle.subsample(15)
# On doit également créer l'image pour le puzzle trouvé
img_puzzle_found = PhotoImage(file="images/puzzle found.png")
# On "dézoom" sur l'image pour la réduire
img_puzzle_found = img_puzzle_found.subsample(15)

# Cette fonction doit afficher des puzzles dans une salle
def place_puzzle(rooms, all_puzzles_eg):
    for room in rooms:
        # On doit vérifier si les puzzles de la liste all_puzzles_eg sont les mêmes que ceux dans le paramètre "puzzles" de room
        for puzzle in all_puzzles_eg:
            # Si le puzzle doit être représenté dans la pièce
            if puzzle in room.puzzles:
                # On fait la même manipulation que lorsqu'on place un joueur dans la pièce
                coord0_room = (room.position[0], room.position[0]+120)
                coord1_room = (room.position[1], room.position[1]+120)
                # On diminue/augmente la zone d'apparition pour être sûr que ce soit dedans
                new_coord00 = coord0_room[0] + 20
                new_coord01 = coord0_room[1] - 20
                
                new_coord10 = coord1_room[0] + 20
                new_coord11 = coord1_room[1] - 20
                # Ici on fait random pour avoir une valeur au pif
                pos0 = random.randint(new_coord00, new_coord01)
                pos1 = random.randint(new_coord10, new_coord11)
                position = [pos0, pos1]
                # On ajoute la position dans l'objet Door direct et pas dans create_door pour la pop up
                puzzle.position = position
                # On regarde l'état du puzzle pour lui assigner la bonne image
                if puzzle.found:
                    puzzle_test = puzzle.create_puzzle(visu_eg_canvas, img_puzzle_found)
                if not (puzzle.found):
                    puzzle_test = puzzle.create_puzzle(visu_eg_canvas, img_puzzle)

# On va maintenant setup l'image de l'indice ici, on fait ça pour l'image de l'indice, et celle de l'indice inspecté

# On doit le mettre ici car ça marche pas si dans la fonction
# Il faut init l'image du puzzle et la dézoomer en dehors d'une fonction
img_clue = PhotoImage(file="images/loupe.png")
# On "dézoom" sur l'image pour la réduire
img_clue = img_clue.subsample(20)
# On fait pareil pour créer l'image de l'indice trouvé
img_clue_found = PhotoImage(file="images/loupe found.png")
# On "dézoom" sur l'image pour la réduire
img_clue_found = img_clue_found.subsample(20)

# Cette fonction doit afficher des indices dans une salle
def place_clue(rooms, all_clues_eg):
    for room in rooms:
        # On doit vérifier si les indices de la liste all_clues_eg sont les mêmes que ceux dans le paramètre "clues" de room
        for clue in all_clues_eg:
            # Si l'indice doit être représenté dans la pièce
            if clue in room.clues:
                # On fait la même manipulation que lorsqu'on place un joueur dans la pièce
                coord0_room = (room.position[0], room.position[0]+120)
                coord1_room = (room.position[1], room.position[1]+120)
                # On diminue/augmente la zone d'apparition pour être sûr que ce soit dedans
                new_coord00 = coord0_room[0] + 20
                new_coord01 = coord0_room[1] - 20
                
                new_coord10 = coord1_room[0] + 20
                new_coord11 = coord1_room[1] - 20
                # Ici on fait random pour avoir une valeur au pif
                pos0 = random.randint(new_coord00, new_coord01)
                pos1 = random.randint(new_coord10, new_coord11)
                position = [pos0, pos1]
                # On ajoute la position dans l'objet Door direct et pas dans create_door pour la pop up
                clue.position = position
                # On regarde l'état de l'indice pour lui assigner la bonne image
                if clue.found:
                    clue_test = clue.create_clue(visu_eg_canvas, img_clue_found)
                if not(clue.found):
                    clue_test = clue.create_clue(visu_eg_canvas, img_clue)

# Pop ups setup

# Ici on ajoute les pop up via le fichier pop_up.py
# D'abord on ajoute toutes les listes d'items dans une liste pour pouvoir assigner les pop up à tous les items du jeu
list_all_items = [ls_rooms_eg, ls_doors_eg, ls_players_eg, ls_puzzles_eg, ls_clues_eg]
# Cette fonction permet de pouvoir afficher une pop up avec des infos sur un élément ou un framework en cliquant dessus
show_pop_up(list_all_items, visu_eg_canvas, window)

# FONCTION DE MISE A JOUR DU JEU

# Cette fonction va permettre de mettre à jour la représentation de l'EG en fonction de l'état du fichier json
def update_game(elements):
    # elements contient les éléments à mettre à jour lorsque l'on appelle la fonction
    for elem in elements:
        # Si on veut mettre à jour tout le palteau, on utilise "all"
        if elem == "all":
            # On appelle toutes les fonctions de placement d'éléments pour replacer les éléments modifiés
            place_room(rooms=ls_rooms_eg)
            place_door(ls_rooms_eg, ls_doors_eg)
            # On affiche de nouveau les salles pour cacher les portes
            place_room(rooms=ls_rooms_eg)
            # On doit d'abord enlever les joueurs déjà affichés, on prend simplement le tag des joueurs
            # On fait cela pour ne pas garder des joueurs dans une pièce et en même temps sur le côté d'une pièce
            visu_eg_canvas.delete("player")
            place_player(ls_rooms_eg, ls_players_eg)
            place_puzzle(ls_rooms_eg, ls_puzzles_eg)
            place_clue(ls_rooms_eg, ls_clues_eg)
        # Les canva.delete permettent d'enlever les éléments avant d'en afficher des nouveaux, comme ça on a l'illusion que seuls ces éléments bougent
        if elem == "players":
            visu_eg_canvas.delete("player")
            place_player(ls_rooms_eg, ls_players_eg)
        if elem == "rooms":
            visu_eg_canvas.delete("room")
            place_room(rooms=ls_rooms_eg)
        if elem == "clues":
            visu_eg_canvas.delete("clue")
            place_clue(ls_rooms_eg, ls_clues_eg)
        if elem == "puzzles":
            visu_eg_canvas.delete("puzzle")
            place_puzzle(ls_rooms_eg, ls_puzzles_eg)
# On met à jour une première fois le plateau pour commencer la partie            
update_game(["all"])

# Pour finir, on gère les évènements de fermeture de l'application

# Cet évènement se déclenche quand on appuye sur la croix pour fermer la fenêtre
window.protocol("WM_DELETE_WINDOW", on_closing)
# Boucle pour faire run ke programme
window.mainloop()

# REMISE A JOUR DU JSON D'ORIGINE

# Une fois que l'on ferme la fenêtre, on doit remettre le fichier json
# utilisé pour jouer de base afin de le remettre comme il était de base
# On lit le json de base
data = read_json("origin.json")
# On remet le fichier json à l'initial
update_json("evolving.json", data)