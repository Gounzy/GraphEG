# Ce fichier va contenir toutes les classes permettant de construire chaque élément de l'EG
# On peut donc créer une pièce, une porte, un joueur, un puzzle, un indice ou une action
# Chaque classe possède plusieurs méthodes, donc celle de la création de la forme pour la représentation sur l'interface principale

# Imports
import tkinter
from tkinter import *
from tkinter import ttk

class Room:
    # On définit le constructeur de Room
    def __init__(self, id, players_in_front, players_in, position, puzzles, clues):
        self.id = id
        self.players_in_front = players_in_front
        self.players_in = players_in
        self.position = position # Ici on a définit position pour savoir récupérer où est la salle pour y disposer les joueurs/puzzles/indices
        self.puzzles = puzzles
        self.clues = clues
        
    # On définit cette fonction pour pouvoir afficher proprement ce que contient l'objet
    def __str__(self):
        return f"{self.id} : ({self.players_in_front}, {self.players_in}, {self.position}, {self.puzzles}, {self.clues})"
    
    # Il faut une méthode pour afficher une room
    def create_room(self, canva):
        # Cette fonction permet de créer un carré de 120 sur 120 en fonction de la position donnée en entrée
        # On a jouté une couleur d'arrière plan, une épaisseur et un tag pour la Pop up
        room = canva.create_rectangle(self.position[0], self.position[1], self.position[0] + 120, self.position[1] + 120, fill="lightgrey", width=5, tags="room")# (x1, y1, x2, y2)
        return room
    

class Door:
    # Définition du constructeur
    def __init__(self, id, connexion, opened, position_start, position_end):
        self.id = id
        self.connexion = connexion
        self.opened = opened
        self.position_start = position_start
        self.position_end = position_end
        
    def __str__(self):
        return f"{self.id} : ({self.connexion}, {self.opened}, {self.position_start}, {self.position_end})"
    
    def create_door(self, canva):
        # On ajoute une condition qui permet de mettre à jour l'affichage de la porte
        # En effet, si la porte est ouverte
        if self.opened:
            # On l'affiche verte
            color = "lightgreen"
            dash = None
        # Sinon
        else:
            # On l'affiche en rouge et pointillée
            color = "red"
            dash = 5
        # On a donc ajouté une épaisseur, une couleur, une forme et un tag
        ligne = canva.create_line(self.position_start[0], self.position_start[1], self.position_end[0], self.position_end[1], width=5, fill=color, dash=dash, tags="door")# (x1, y1, x2, y2)
        return ligne

class Player:
    # Définition du constructeur
    def __init__(self, name, skills, inventory, knowledge, position):
        self.name = name
        self.skills = skills
        self.inventory = inventory
        self.knowledge = knowledge
        self.position = position
        
    def __str__(self):
        return f"{self.name} : ({self.skills}, {self.inventory}, {self.knowledge}, {self.position})"
    
    def create_player(self, canva, rayon):
        # On fait le rayon fois 2 car cela corrsepond à la deuxième position du carré qui contient le cercle
        # On a donc ajouté une épaisseur, un contour, une couleur et un tag
        cercle = canva.create_oval(self.position[0], self.position[1], self.position[0] + (rayon*2), self.position[1] + (rayon*2), width=1, outline="black", fill="blue", tags="player")#, tags=("player", self.name))
        return cercle

class Puzzle:
    # Définition du constructeur
    def __init__(self, id, taxonomy, rewards, meta, found, position):
        self.id = id
        self.taxonomy = taxonomy
        self.rewards = rewards
        self.meta = meta
        self.found = found
        self.position = position
        
    def __str__(self):
        return f"{self.id} : ({self.taxonomy}, {self.rewards}, {self.meta}, {self.found}, {self.position})"
    
    # L'image du puzzle est initialisée directement dans le code principal (idem pour Clue)
    def create_puzzle(self, canva, image_puzzle):
        # On a donc ajouté une image et un tag
        puzzle = canva.create_image(self.position[0], self.position[1], image=image_puzzle, tags="puzzle")
        return puzzle
    
class Clue:
    # Définition du constructeur
    def __init__(self, id, puzzle_id, description, meta, found, position):
        self.id = id
        self.puzzle_id = puzzle_id
        self.description = description
        self.meta = meta
        self.found = found
        self.position = position
        
    def __str__(self):
        return f"{self.id} : ({self.puzzle_id}, {self.description}, {self.meta}, {self.found}, {self.position})"
    
    def create_clue(self, canva, image_clue):
        # On a donc ajouté une image et un tag
        clue = canva.create_image(self.position[0], self.position[1], image=image_clue, tags="clue")
        return clue

class Action:
    # Définition du constructeur
    def __init__(self, id):
        self.id = id
        
    def __str__(self):
        return f"{self.id} : ({self})"