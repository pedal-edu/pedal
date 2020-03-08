"""
##### 0) Header #####
# Text Adventure Game
A chance to make your own Text Adventure Game.
This is an INDIVIDUAL project. Do not consult with others or share code.
Refer to the instructions on Canvas for more information.

# When You Are Done
When you pass all tests, remember to clean and document your code.
Be sure to unit test and document your functions.
"""

##### 1) Author Info #####

# Change these three fields
__author__ = "your email goes here@udel.edu"
__title__ = "Name of your game goes here"
__description__ = "Replace this with a quick description of your game."

# Leave these two fields unchanged
__version__ = 1
__date__ = "Spring 2019"


##### 2) Record Definitions #####
# Add a new record and modify the existing ones to fit your game.

'''
Records:
    World:
        status (str): Whether or not the game is "playing", "won",
                      "quit", or "lost". Initially "playing".
        map (dict[str: Location]): The lookup dictionary matching 
                                   location names to their
                                   information.
        player (Player): The player character's information.

      
    Player:
        location (str): The name of the player's current location.
        inventory (list[str]): The player's collection of items.
                               Initially empty.
        if_enough_money(boolean):It the player get enough money to buy a flight ticket.
        
        
    Location:
        about (str): A sentence that describes what this location 
                     looks like.
        neighbors (list[str]): A list of the names of other places 
                               that you can reach from this 
                               location.
        stuff (list[str]): A collection of things available at 
                           this location.
        weather(boolean):If the outside is sunny or rainy.
        
    Vehicle:
        taxi(boolean):If player can find a taxi to the Airport.
'''

##### 3) Core Game Functions #####
# Implement the following to create your game.

def render_introduction():
    '''
    Create the message to be displayed at the start of your game.
    
    Returns:
        str: The introductory text of your game to be displayed.
    '''
    return("==Go home==\n"+
           "= By Ribo Yuan\n"+
           "\n"+
           "After your wallet was stolen,\n"+
           "How do you want to get enough money?")
def create_world():
    '''
    Creates a new version of the world in its initial state.
    
    Returns:
        World: The initial state of the world
    '''
    return {
        "map":creat_map(),
        "player":creat_player(),
        "status":"playing"
    }
def create_player():
    return {
        "location":"Barcelona",
        "inventory":[]
    }

def create_map():
    return {
        "Barcelona":{
                "neighbors":["Mall","Street"],
                "about":"There are many people and restaurant.",
                "stuff":[],
        },
        "Mall":{
                "neighbors":["Barcelona","Airport"],
                "about":"Fancy place and there are many people.",
                "stuff":[Money]
        },
        "Street":{
                "neighbors":["Barcelona","Restaurant","Airport"],
                "about":"There are many restauarant where you can get money.",
                "stuff":[Money]
        },
        "Restaurant":{
                "neighbors":["Street","Airport"],
                "about":"Seafood restaurant",
                "stuff":[Money]
        },
        "Airport":{
                "neighbors":["Mall","Street","Restaurant"],
                "about":"A place where you can buy a flight ticket.",
                "stuff":[]
        }
    }
    
def render_location(world):
    # ...
    location = world['player']['location']
    here = world['map'][location]
    about = here['about']
    # ...
    return ("You are in "+location+"\n"+
            about+"\n")
            
def render_visible_stuff(world):
    location = world['player']['location']
    here = world['map'][location]
    stuff = here['stuff']
    inventory = world['player']['inventory']

    visible_stuff = []
    for thing in stuff:
        if 'money' not in inventory:
                visible_stuff.append(thing)
        else:
            visible_stuff.append(thing)

    return "You see: " + ', '.join(visible_stuff)
    
def render(world):
    '''
    Consumes a world and produces a string that will describe the current state
    of the world. Does not print.
    
    Args:
        world (World): The current world to describe.
    
    Returns:
        str: A textual description of the world.
    '''
    return (render_location(world) +
            render_player(world) +
            render_visible_stuff(world))
def get_options(world):
    '''
    Consumes a world and produces a list of strings representing the options
    that are available to be chosen given this state.
    
    Args:
        world (World): The current world to get options for.
    
    Returns:
        list[str]: The list of commands that the user can choose from.
    '''
    # ...
    commands = ["Quit"]
    # ...
    # Add more commands
    # ...
    return commands
def update(world, command):
    '''
    Consumes a world and a command and updates the world according to the
    command, also producing a message about the update that occurred. This
    function should modify the world given, not produce a new one.
    
    Args:
        world (World): The current world to modify.
    
    Returns:
        str: A message describing the change that occurred in the world.
    '''

def render_ending(world):
    '''
    Create the message to be displayed at the end of your game.
    
    Args:
        world (World): The final world state to use in describing the ending.
    
    Returns:
        str: The ending text of your game to be displayed.
    '''

def choose(options):
    '''
    Consumes a list of commands, prints them for the user, takes in user input
    for the command that the user wants (prompting repeatedly until a valid
    command is chosen), and then returns the command that was chosen.
    
    Note:
        Use your answer to Programming Problem #42.3
    
    Args:
        options (list[str]): The potential commands to select from.
    
    Returns:
        str: The command that was selected by the user.
    '''

###### 4) Win/Lose Paths #####
# The autograder will use these to try out your game
# WIN_PATH (list[str]): A list of commands that win the game when entered
# LOSE_PATH (list[str]): A list of commands that lose the game when entered.

WIN_PATH = []
LOSE_PATH = []
    
###### 5) Unit Tests #####
# Write unit tests here

from cisc108 import assert_equal


###### 6) Main Function #####
# Do not modify this area
def main():
    '''
    Run your game using the Text Adventure console engine.
    Consumes and produces nothing, but prints and indirectly takes user input.
    '''
    print(render_introduction())
    world = create_world()
    while world['status'] == 'playing':
        print(render(world))
        options = get_options(world)
        command = choose(options)
        print(update(world, command))
    print(render_ending(world))

if __name__ == '__main__':
    main()
