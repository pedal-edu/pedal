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
#__hfisher@udel.edu__ = "your email goes here@udel.edu"
#"Pet That Dog!"= "Name of your game goes here"
#You wake up only to realize that you have not pet a dog in the past 24 hours. Tears spring into your eyes as you realize the tragedy of this situation. You get up one goal in mind. You're going to Pet That Dog!= "Replace this with a quick description of your game."

# Leave these two fields unchanged
__version__ = 1
__date__ = "Spring 2019"


##### 2) Record Definitions #####
# Add a new record and modify the existing ones to fit your game.
from cisc108 import assert_equal
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
        location (str): The name of the player's current location. Initially "bed".
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
                           
    Items:
        about(str): A sentence describing what it is you picked up. Changes the dictionary of the player inventory.
'''

##### 3) Core Game Functions #####
# Implement the following to create your game.

def render_introduction():
    '''
    Create the message to be displayed at the start of your game.
    
    Returns:
        str: The introductory text of your game to be displayed.
    '''
    line1= "You wake up only to realize that you have not pet a dog in the past 24 hours.\n"
    line2="Tears spring into your eyes as you realize the tragedy of this situation. You get up one goal in mind.\n"
    line3="You're going to Pet That Dog!"
    print(line1+line2+line3)
    return(line1+line2+line3)

def create_world():
    '''
    Creates a new version of the world in its initial state.
    
    Returns:
        World: The initial state of the world
    '''
    return {
        'map': create_map(),
        'player': create_player(),
        'status': "playing",
        'items': create_items()
            }
def create_items(location):
    inventory=[]
    if create_map['stuff']==[]:
        return "No items here!"
    else:
        print ("You have picked up"+create_map['stuff'])
        return inventory.append(create_map["stuff"])
def create_map():
    return{
        'bed':{
            'neighbors':['fall asleep','landing'], 
            "about":"It's so warm and cozy. Only your love for puppers could make you leave.",
            'stuff':[]
        },
        "fall asleep":{
            'neighbors':['bed'],
            "about":"You feel well rested, but you still want to pet a dog",
            "stuff":[]},
        'Landing':
            {'neighbors':['bed','Kitchen','Outside'],
            "about":"A clean little nook at the bottom of the stairs.",
            "stuff":[]},
        "Kitchen":{
            'neighbors':['Landing'],
            "about":"A quaint little kitchen. There are crackers on the counter. You could take a pack for later in case you get hungry",
            "stuff":['cracker']},
        "Outside":{
            'neighbors':["Landing","Library","Park"],
            "about":"It is a beautiful sunny day! You're on a sidewalk shaded by some trees.",
            "stuff":[]},
        "Library":{
            'neighbors':["Armchair", "Outside"],
            "about":"It's really quiet here. The smell of books is very inticing. There is even a book about dogs.",
            "stuff":['book']},
        "Armchair":{
            'neighbors':["Library"],
            "about":"Talk about cozy. This chair feels like it was made for your tucchus",
            "stuff":[]},
        "Park":{
            'neighbors':["Outside","Bench","Dog Park"],
            "about":"What a beautiful place to enjoy the day! This park has OPTIONS!",
            "stuff":[]},
        "Bench":{
            'neighbors':["Park"],
            "about":"A great place to people watch!",
            "stuff":[]},
        "Dog Park":{
            'neighbors':["Dog", "Owner's Dog","Park"],
            "about":"You have reached the nirvana of dog spotters. There's even a lady with a cat on a leash.",
            "stuff":[]},
        "Dog":{
            'neighbors':["Dog Park"],
            "about":"He's the fluffiest boi you've ever seen.",
            "stuff":[]},
        "Owner's Dog":{
            'neighbors':["Dog Park"],
            "about":"He looks so fluffy. He is mostly black and large. He's drooling up its only because he's happy.",
            "stuff":[]}
        }
def create_player():
    return {
        'location':'bed',
        'inventory':[]
    }
player=create_player()
assert_equal(len(player.keys()), 2)
assert_equal("location" in player, True)
assert_equal(player['location'], 'bed')
assert_equal("inventory" in player, True)
assert_equal(player['inventory'], [])
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
