# Graphical visualisation of escape games

This software is designed to graphically represent the concept of an escape game.

Through two distinct interfaces, users can load a specific escape game session and observe its progression using both a global view and a graph-theoretical view. This allows designers and players to analyze the game’s evolution over time.

From a graph theory perspective, three types of graphs are supported:

Static Graph: Represents all core elements of the escape game. Nodes correspond to entities (e.g., rooms, puzzles, clues), while edges encode logical or spatial relationships between them.

Dynamic Graph: Reflects the evolving state of a session. It tracks the players’ progression through rooms, the collection of clues, and the resolution of puzzles. This view enables real-time monitoring and state-dependent analysis.

Puzzle Framework Graph: A directed graph centered on a specific item (such as a clue or a puzzle). It illustrates which clues are required to solve a given puzzle, shows the location of items, and indicates puzzle rewards (such as keys or new clues unlocking further areas).

These graph types provide complementary insights into the game design, making this program a powerful tool for both scenario modeling and pedagogical analysis.



# Installer le projet

To use the software, users can simply retrieve the source code via the following Git command:
`git clone https://github.com/Gounzy/GraphEG.git`

Alternatively, a standalone executable is available that bundles all necessary dependencies. This allows users to run the software without the need for an IDE or manual setup.

To proceed, navigate to the \texttt{bin} directory of the GitHub repository. Inside, locate the compressed folder named \texttt{main_eg.zip}, which contains all required resources to run the program. Extract its contents and launch the application via the \texttt{main_eg.exe} file. Once opened, the software can be used immediately with full functionality.


# Using the Project

Since the project's interface remains quite minimalistic, it may be necessary to understand its mechanisms before using it. This section explains the available interactions to help you effectively explore the software.

## Loading a Game

To start playing an escape game, you must first load a game session. This is done by creating a JSON file that contains all the necessary information about the escape game.  
Once created, copy its content into the default JSON file named `evolving.json`. This file is used by the program to display the game based on the defined structure.

### Creating the JSON File

To create the JSON file, use the template available in the repository (`pattern.json`) as a base. You can modify and extend this pattern with your own game elements.  
Make sure to follow specific conventions regarding the item structure—see the “Items” section in the README for further details.

### JSON Structure

The JSON file must contain the following elements:

- **"EG"**: Includes the `"name"` field, which designates the name of the escape game.
- **"Rooms"**: Contains information about each room, including:
  - `"id"`: unique identifier
  - `"players_in_front"` / `"players_in"`: players near or inside the room
  - `"position"`: coordinates for the interface (default: `[0, 0]`)
  - `"puzzles"` and `"clues"`: items present in the room
- **"puzzles"** (within rooms):
  - `"id"`: unique ID
  - `"taxonomy"`: puzzle type
  - `"rewards"`: what is gained upon solving
  - `"description"`, `"meta"`: explanation and solution
  - `"found"`: inspection state
  - `"position"`: default `[0, 0]`
- **"clues"** (within rooms):
  - same fields as puzzles, with an added `"puzzle_id"` indicating the puzzle it relates to
- **"Doors"**: Connections between rooms
  - `"id"`, `"connexion"`, `"opened"`, `"position_start"`, `"position_end"`
- **"Players"**: Information about players
  - `"name"`, `"skills"`, `"inventory"`, `"knowledge"`, `"position"`
- **"Actions"**: Describes all possible game actions
  - only needs an `"id"`

## Playing the Escape Game

The game defined in the JSON can be played using the software. To interact with the game, a system of requests is used.

### Requests

Actions are carried out through commands composed of three elements:
1. **Player**  
2. **Action**  
3. **Target item**

For example:  
`Marc interact Start`  
means Marc interacts with the Start room.

### Actions

Each action is only applicable to certain item types:

- **interact**: enter a room  
  > Valid on: `Rooms`
- **inspect**: discover an item in a room  
  > Valid on: `Clues`, `Puzzles`
- **take**: pick up a clue  
  > Valid on: `Clues`
- **resolve**: attempt to solve a puzzle  
  > Valid on: `Puzzles`
- **share**: exchange clues between players  
  > Valid on: `Clues`
- **move**: move through a door  
  > Valid on: `Doors`
- **exit**: leave the escape game  
  > Valid on: `Exit` (the final room)

### Items

Each item must follow naming conventions using an initial uppercase letter:

- **Room**: `"R"` followed by a number (e.g. `R2`)  
  - `Start` is the entry room  
  - `Exit` is the goal room
- **Clue**: `"C"` followed by puzzle and clue index, like `C1.2` (2nd clue for puzzle 1)
- **Puzzle**: `"P"` followed by an index (e.g., `P3`)
- **Door**: `"D"` followed by a number (e.g., `D1`)

### Pop-ups

Clicking on items in the interface reveals information:

- Only `Player`, `Room`, and `Door` return direct pop-ups.
- Clicking other items (e.g., puzzles, clues) displays their **Puzzle Framework Graph**.

### Graphs

The software includes three visual representations of the game:

- **Static Graph**: Full representation of rooms and item locations  
  > Access via the [Static Graph] button
- **Dynamic Graph**: Reflects current game state (items discovered, player status)  
  > Access via the [Dynamic Graph] button
- **Puzzle Frameworks**: Shown when clicking a puzzle or clue  
  - Shows required clues, location, and resulting reward

### Functions

- **[Refresh]**: Reorganizes items to make them clickable  
- **[Save]**: Saves the game state to `saved.json`

### History

A dialog box displays the input history and game feedback (including errors), helping users track progress and debug issues.
