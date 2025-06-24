# Ce fichier contient la fonctionnalité Pop up qui permet d'afficher les détails d'un item lorsque l'on clique dessus
# Cela est valable pour tout élément autre que puzzle et indice car ceux-ci sont affichés avec les puzzles framework

# Imports
from tkinter import *
from tkinter import ttk
from objects import *
import random
from PIL import ImageTk, Image
from static_graph_puzzle import display_puzzle_framework

# Cette fonction va contenir tout pour afficher la pop up d'un item
def show_pop_up(all_items, canva, window):
    # On init toutes les listes qui seront utilisées ici car elles vont contenir tous les items du plateau
    # Le paramètre all_items contiendra toutes les listes des items du jeu, c'est donc une liste de liste
    # Ces listes permettront de trouver les éléments du jeu sur le canva au niveau des coordonnées
    list_rooms = all_items[0]
    list_doors = all_items[1]
    list_players = all_items[2]
    list_puzzles = all_items[3]
    list_clues = all_items[4]

    # Cette fonction va permettre de savoir sur quel item on clique et d'afficher les informations correspondantes
    def on_item_click(event):
        # Pour différencier un élément d'un autre, on va utiliser les tags car lors de la création d'un élément dans le fichier objects.py,
        # on va lui assigner un tag en fonction de sa nature
        
        # On récupère le numéro de l'item cliqué
        current = event.widget.find_withtag("current")
        # On fait des listes qui contiennent les numéros des items en fonction de leur tag
        tags_rooms = event.widget.find_withtag("room")
        tags_doors = event.widget.find_withtag("door")
        tags_players = event.widget.find_withtag("player")
        tags_puzzles = event.widget.find_withtag("puzzle")
        tags_clues = event.widget.find_withtag("clue")
        
        # Ensuite on va pouvoir vérifier le numéro de l'item cliqué pour voir il correspond à quelle famille d'item
        # On regarde si c'est une salle
        for tag in tags_rooms:
            # On regarde si c'est le même tag que celui cliqué
            if tag == current[0]:
                # Ici on va assigner les données de la pièce en fonction de celle qui est cliqué
                # On regarde donc dans la liste qui contient toutes les pièces, si la position d'un correspond à l'endroit où on clique, c'est que c'est la bonne pièce
                for room in list_rooms:
                    if event.x >= (room.position[0] - 1) and event.x <= (room.position[0] + (150 + 1)): # On ajoute des pixels sur tous les côtés pour être sûr que l'item est cliquable
                        if event.y >= (room.position[1] - 1) and event.y <= (room.position[1] + (150 + 1)):
                            selected_room = room

                # On crée une pop up avec Toplevel()
                pop = Toplevel(window, bg="white", bd=20) # window représente la fenêtre de base qu'on crée pour l'application
                # On peut sépcifier le nom de la fenêtre créée (https://www.tutorialspoint.com/python/tk_toplevel.htm)
                pop.title("Room")
                
                # On crée des listes pour afficher seulement les id pour que ce soit lisible
                id_puzzles=[]
                id_clues=[]
                # Ensuite on ajoute les id dans ces listes pour l'affichage
                for item in selected_room.puzzles:
                    id_puzzles.append(item.id)
                for item in selected_room.clues:
                    id_clues.append(item.id)
                
                # On ajoute les infos de la pièce dans la pop up
                id_room = ttk.Label(pop, text="This is the " + str(selected_room.id) + " Room", font=("Arial", 16), background="white")
                # On va préciser les messages en fonction de la contenance de la pièce
                if selected_room.players_in == []:
                    players_in_room = ttk.Label(pop, text="There is no players in this room", font=("Arial", 12), background="white")
                else:
                    players_in_room = ttk.Label(pop, text="Players are in this room : " + str(selected_room.players_in), font=("Arial", 12), background="white")
                # Pareil pour puzzles et clues
                if id_puzzles == []:
                    puzzles_room = ttk.Label(pop, text="There is no puzzles in this room", font=("Arial", 12), background="white")
                else:
                    puzzles_room = ttk.Label(pop, text="Puzzles : " + str(id_puzzles), font=("Arial", 12), background="white")
                if id_clues == []:
                    clues_room = ttk.Label(pop, text="There is no clues in this room", font=("Arial", 12), background="white")
                else:
                    clues_room = ttk.Label(pop, text="Clues : " + str(id_clues), font=("Arial", 12), background="white")
                
                # On les affiche
                id_room.grid(column=0, row=0)
                players_in_room.grid(column=0, row=2, sticky=W)
                puzzles_room.grid(column=0, row=3, sticky=W)
                clues_room.grid(column=0, row=4, sticky=W)
                
        # On regarde si c'est une porte
        for tag in tags_doors:
            if tag == current[0]:
                # Ici on va assigner les données de la porte en fonction de celle qui est cliqué
                # On regarde donc dans la liste qui contient toutes les portes, si la position correspond, c'est la porte
                for door in list_doors:
                    # On doit prendre en considération que la ligne fait une certaine épaisseur, mais dans le code on prend seulement les coordonnées de la position de la ligne
                    # C'est pourquoi, même si on clique sur la ligne (la porte), si on est pas pile au milieu, ça ne marchera pas, il faut donc ajouter l'épaisseur de la porte
                    door_width = 5
                    # Ensuite on vérifie l'endroit cliqué comme précédemment
                    if ( event.x > (door.position_start[0] - 1 - door_width) and event.x < (door.position_end[0] + 1 + door_width) ) or ( event.x < (door.position_start[0] - 1 - door_width) and event.x > (door.position_end[0] + 1 + door_width) ): # On ajoute des pixels sur tous les côtés pour être sûr que l'item est cliquable
                        if ( event.y > (door.position_start[1] - 1 - door_width) and event.y < (door.position_end[1] + 1 + door_width) ) or ( event.y < (door.position_start[1] - 1 - door_width) and event.y > (door.position_end[1] + 1 + door_width) ):
                            selected_door = door

                # On crée une pop up avec Toplevel()
                pop = Toplevel(window, bg="white", bd=20)
                # On peut sépcifier le nom de la fenêtre créée
                pop.title("Door")
                
                # On ajoute les infos de la porte dans la pop up
                id_door = ttk.Label(pop, text="This is the " + str(selected_door.id) + " Door", font=("Arial", 16), background="white")
                # On va préciser quelles pièces elle relie
                connexion_door = ttk.Label(pop, text="This door is connected to " + str(selected_door.connexion[0]) + " and " + str(selected_door.connexion[1]), font=("Arial", 12), background="white")
                # Si la porte est ouverte, on le précise
                if selected_door.opened:
                    opened_door = ttk.Label(pop, text="This door is opened", font=("Arial", 12), background="white")
                # Dans le cas contraire aussi
                else:
                    opened_door = ttk.Label(pop, text="This door is closed", font=("Arial", 12), background="white")
                
                # On les affiche
                id_door.grid(column=0, row=0)
                connexion_door.grid(column=0, row=2, sticky=W)
                opened_door.grid(column=0, row=3, sticky=W)
        
        # On regarde si c'est un joueur
        for tag in tags_players:
            #print(tag)
            if tag == current[0]:
                # Ici on va assigner les données du joueur en fonction de celui qui est cliqué
                # On regarde donc dans la liste qui contient tous les joueurs, si la position d'un correspond à l'endroit où on clique, c'est que c'est lui
                for player in list_players:
                    if event.x >= (player.position[0] - 1) and event.x <= (player.position[0] + (8*2 + 1)): # On ajoute des pixels sur tous les côtés pour être sûr que l'item est cliquable
                        if event.y >= (player.position[1] - 1) and event.y <= (player.position[1] + (8*2 + 1)):
                            selected_player = player

                # On crée une pop up avec Toplevel()
                pop = Toplevel(window, bg="white", bd=20)
                # On peut sépcifier le nom de la fenêtre créée
                pop.title("Player")
                
                # On crée des listes pour afficher seulement les id pour que ce soit lisible
                id_inventory=[]
                id_knowledge=[]
                for item in selected_player.inventory:
                    # On vérifie le type car il se peut que certains items soient juste des str dans les knowledge/inventory des joueurs
                    if type(item) == dict:
                        id_inventory.append(item["id"])
                    elif type(item) == str:
                        id_inventory.append(item)
                    else:
                        id_inventory.append(item.id)
                for item in selected_player.knowledge:
                    # On vérifie le type car il se peut que certains items soient juste des str dans les knowledge/inventory des joueurs
                    if type(item) == dict:
                        id_knowledge.append(item["id"])
                    elif type(item) == str:
                        id_knowledge.append(item)
                    else:
                        id_knowledge.append(item.id)
                
                # On ajoute les infos du joueur dans la pop up
                name_player = ttk.Label(pop, text="This is the Player " + str(selected_player.name), font=("Arial", 16), background="white")
                # On précise ce que le joueur possède dans chaque paramètre
                if selected_player.skills == []:
                    skills_player = ttk.Label(pop, text="This player has no skills", font=("Arial", 12), background="white")
                else:
                    skills_player = ttk.Label(pop, text="Skills : " + str(selected_player.skills), font=("Arial", 12), background="white")
                if id_inventory == []:
                    inventory_player = ttk.Label(pop, text="This player has nothing in his inventory", font=("Arial", 12), background="white")
                else:
                    inventory_player = ttk.Label(pop, text="Inventory : " + str(id_inventory), font=("Arial", 12), background="white")
                if id_knowledge == []:
                    knowledge_player = ttk.Label(pop, text="This player has nothing in his knowledge", font=("Arial", 12), background="white")
                else:
                    knowledge_player = ttk.Label(pop, text="Knowledge : " + str(id_knowledge), font=("Arial", 12), background="white")
                    
                # On les affiche
                name_player.grid(column=0, row=1, sticky=W)
                skills_player.grid(column=0, row=2, sticky=W)
                inventory_player.grid(column=0, row=3, sticky=W)
                knowledge_player.grid(column=0, row=4, sticky=W)
                
        # On regarde si c'est un puzzle
        # Tout d'abord on assigne cette valeur à None pour vérifier si en bas elle est toujours à None pour éviter une erreur dans le terminal
        selected_puzzle = None # C'est une sécurité
        # Maintenant on regarde si c'est un puzzle
        for tag in tags_puzzles:
            if tag == current[0]:
                # Ici on va assigner les données du puzzle en fonction de celui qui est cliqué
                # On regarde donc dans la liste qui contient tous les puzzles, si la position correspond, c'est le bon puzzle
                for puzzle in list_puzzles:
                    # En effet, on doit repositionner le clic du puzzle de 10 pixels car sa position est correcte mais on utilise une image,
                    # c'est pourquoi on doit décaler manuellement le clic pour être sûr (// aux portes)
                    re_position = 15
                    # On fait (pos - re_position) chaque fois pour vraiment décaler la zone de clic
                    if event.x >= (puzzle.position[0] - 1 - re_position) and event.x <= (puzzle.position[0] + (25 + 5) - re_position): # On ajoute des pixels sur tous les côtés pour être sûr que l'item est cliquable
                        if event.y >= (puzzle.position[1] - 1 - re_position) and event.y <= (puzzle.position[1] + (25 + 5) - re_position):
                            selected_puzzle = puzzle
                # Si à la sortie de la boucle on voit qu'on a cliqué quelque part mais que ce n'était pas la zone cliquable du puzzle, on arrête là
                if selected_puzzle == None:
                    return False
                
                # Alternative avec le plt.show() du module matplotlib
                # Ici comme c'est un puzzle, on utilise la fonction qui génère le puzzle framework correspondant
                display_puzzle_framework(selected_puzzle.id)
        
        # Pareil que pour le puzzle
        selected_clue = None
        # On regarde si c'est un indice
        for tag in tags_clues:
            if tag == current[0]:
                # Ici on va assigner les données du puzzle en fonction de celui qui est cliqué
                # On regarde donc dans la liste qui contient tous les puzzles, si la position correspond, c'est le bon puzzle
                for clue in list_clues:
                    # On doit faire pareil que pour les puzzles
                    re_position = 15
                    # On fait (pos - re_position) chaque fois pour vraiment décaler la zone de clic
                    if event.x >= (clue.position[0] - 1 - re_position) and event.x <= (clue.position[0] + (25 + 4) - re_position): # On ajoute des pixels sur tous les côtés pour être sûr que l'item est cliquable
                        if event.y >= (clue.position[1] - 1 - re_position) and event.y <= (clue.position[1] + (25 + 4) - re_position):
                            selected_clue = clue
                # // à puzzle plus haut, même principe
                if selected_clue == None:
                    return False

                # Alternative avec le plt.show() du module matplotlib
                # Ici comme c'est un puzzle, on utilise la fonction qui génère le puzzle framework correspondant
                display_puzzle_framework(selected_clue.id)
                
    # Ces deux fonctions permettent de changer le curseur en mode "clickable" quand on passe sur un item    
    def check_hand_enter(event):
        canva.config(cursor="hand2")

    def check_hand_leave(event):
        canva.config(cursor="")

    # On utilise la fonction tag_bind() pour lier une fonction au fait de cliquer (bouton 1) sur l'élément "play1"
    # Le paramètre canva représente le canva qui contient tous les items que peuvent afficher une pop up
    
    # Salles
    canva.tag_bind("room", '<Button-1>', on_item_click)
    canva.tag_bind("door", '<Button-1>', on_item_click)
    canva.tag_bind("player", '<Button-1>', on_item_click)
    canva.tag_bind("puzzle", '<Button-1>', on_item_click)
    canva.tag_bind("clue", '<Button-1>', on_item_click)
    # On lie donc les deux fonctions au canva, comma cela dès qu'on passe sur l'item, le curseur change de forme
    canva.tag_bind("room", "<Enter>", check_hand_enter)
    canva.tag_bind("room", "<Leave>", check_hand_leave)
    canva.tag_bind("door", "<Enter>", check_hand_enter)
    canva.tag_bind("door", "<Leave>", check_hand_leave)
    canva.tag_bind("player", "<Enter>", check_hand_enter)
    canva.tag_bind("player", "<Leave>", check_hand_leave)
    canva.tag_bind("puzzle", "<Enter>", check_hand_enter)
    canva.tag_bind("puzzle", "<Leave>", check_hand_leave)
    canva.tag_bind("clue", "<Enter>", check_hand_enter)
    canva.tag_bind("clue", "<Leave>", check_hand_leave)
