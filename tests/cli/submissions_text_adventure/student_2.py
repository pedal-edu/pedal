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

    Location:
        about (str): A sentence that describes what this location 
                     looks like.
        neighbors (list[str]): A list of the names of other places 
                               that you can reach from this 
                               location.
        stuff (list[str]): A collection of things available at 
                           this location.
'''

##### 3) Core Game Functions #####
# Implement the following to create your game.

def render_introduction():
    '''
    Create the message to be displayed at the start of your game.
    
    Returns:
        str: The introductory text of your game to be displayed.
    '''
    return("On a family vacation it is very difficult \n" + 
    "to make everyone happy. Try to plan a day that pleases everyone, \n" +
    "without getting too tired.")

def create_world():
    '''
    Creates a new version of the world in its initial state.
    
    Returns:
        World: The initial state of the world
    '''
    return {
        'map': create_map(),
        'player': create_player(),
        'status': "playing"
    }
def create_player():
    return {
        'location': 'house',
        'inventory': [],
    }
           
def create_map():
    return {
        'House': {
            'neighbors': ["House"],
            'about': "You wake up and eat some breakfast in your \n" +
            "cosy house",
            'stuff': [],
            'reset': True
        },
        'Truck': {
            'neighbors': ["hike", "Drive" ],
            'about': "In the car on a rainy day, decide where to go next",
            'stuff': [],
            'reset': False
        },
        'hike': {
            'neighbors': ["Car"],
            'about': "You went on a hike in the pouring rain. \n" + 
            "The slope is very slippery",
            'stuff': [],
            'reset': False
        },
        'Drive': {
            'neighbors': ["Car"],
            'about': "You drive around and sightsee",
            'stuff': ["player happiness", "Dad happiness"],
            'reset': False
        },
        'Car': {
            'neighbors': ["House", "Dinner", "The Town", "Mad River Sports"],
            'about': "It is a beautiful day and this car can take you \n" +
            "to a variety of places",
            'stuff': [],
            'reset':False
        },
        'Mad River Sports': {
            'neighbors': ["Car", "River","Kayaking"],
            'about': "A cute shop with a variety of water sport options",
            'stuff': [],
            'reset': False
        },
        'Kayak': {
            'neighbors': ["Mad River Sports"],
            'about': "The Mad river is extra Mad today. The kayak cannot handle it",
            'stuff': [],
            'reset': False
        },
        'River': {
            'neighbors': ["Mad River Sports"],
            'about': "The river is roaring and you are spinning down \n" +
            "in a tube",
            'stuff': ["player happiness," "Dad happiness"],
            'reset': False
        },
       'The Town': {
            'neighbors': ["Farm", "Lake", "Car"],
            'about': "Walking around the beautiful town of Burlington \n" +
            "and there are so many things to do from here!",
            'stuff': [],
            'reset': False
        },
        'Farm': {
            'neighbors': ["The Town"],
            'about': "Shelbourn farm is home to many animals. \n" +
            "You pet chicken and milk cows.",
            'stuff': ["player happiness", "Dad happiness"],
            'reset': False
        },
        'Lake': {
            'neighbors': ["The Town"],
            'about': "Lake Champlain is known for its chilly temperatures, \n" +
            "but the water is no crystak it's hard to exist",
            'stuff': [],
            'reset': False
        },
        'Dinner': {
            'neighbors': ["Car"],
            'about': "Have you had a filled day? Dinner marks the ends.",
            'stuff': [],
            'reset': False
        },
    }
                             

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
    
def render_location(world):
    location = world['player']['location']
    here = world['map'][location]
    about = here['about']
    
    return ("You are in" + location+ "\n" + about + "\n") 
    

def get_options(world):
    '''
    Consumes a world and produces a list of strings representing the options
    that are available to be chosen given this state.
    
    Args:
        world (World): The current world to get options for.
    
    Returns:
        list[str]: The list of commands that the user can choose from.
    '''
    commands = ["Quit"]
    
    
    
    

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


#render_introduction
assert_equal(render_introduction(), """On a family vacation it is very difficult 
    to make everyone happy. Try to plan a day that pleases everyone, 
    "without getting too tired.""")
    
player = create_player()
# Use the built-in isinstance function to confirm that we made a dictionary
assert_equal(isinstance(player, dict), True)
# Does it have the right keys?
assert_equal(len(player.keys()), 2)
assert_equal("location" in player, True)
assert_equal(player['location'], 'yard')
assert_equal("inventory" in player, True)
assert_equal(player['inventory'], [])

world = create_world()
# Is the world a dictionary?
#assert_equal(isinstance(world, dict), True)
# Does the dictionary have the right keys?
assert_equal("status" in world, True)
assert_equal("map" in world, True)
assert_equal("player" in world, True)
# Is the world's status initially playing?
assert_equal(world['status'], 'playing')
# Did we use the create_map function correctly?
assert_equal(world['map'], create_map())
# Is the map a dictionary?
#assert_equal(isinstance(world['map'], dict), True)



map = create_map()
assert_equal(len(map.keys()), 12)


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