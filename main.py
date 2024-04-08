from enum import Enum
import curses
import random

### Eventual saving data implementation ###
# import json

# class GameIO(object):
#     def __init__(self, result, data) -> None:
#         self.data = data
#         self.success = result

# class Gamedata(object):
#     def __init__(self, filename) -> None:
#         self.filename = filename

#     def write_data(self)->None:
#         with open("data.json", "r+") as file:
#         file.seek(0)
#         file.write("Test")
#         print(file.read())

#     def read_data(self)->dict:
#         pass    
#     try:
#         with open("data.json", "r+") as file:
#             file.seek(0)
#             file.write("Test")
#             print(file.read())
#     except FileNotFoundError:
#         with open("data.json", "x+")

# data = Gamedata("data.json")


#import sqlite3
#con = sqlite3.connect("game.db")

#con.execute("""
#CREATE TABLE IF NOT EXISTS player_data
#        (health INTEGER,
#        points INTEGER);
#""")



def clamp(num:int, minval:int, maxval:int):
    if num > maxval:
        return maxval
    elif num < minval:
        return minval
    else:
        return num

class Entity(object):
    
    def __init__(self, name:str, health:int, strength:int) -> None:
        self.dead = False
        self.name = name
        self.health = health
        self.strength = strength
        self.blocking = False



    def take_damage(self, amount:int): # idk probably shouldnt implement this here as not as clear as directly passing in damage and also makes you have to account for this

        if self.blocking:
            self.__take_damage(amount//2)
        else:
            self.__take_damage(amount)
        
    def __take_damage(self, amount:int):
        
        if self.dead == False and self.health - amount > 0:
            self.health -= amount
        else:
            self.health = 0
            self.dead = True

    def toggle_blocking(self):
        if self.blocking:
            self.blocking = False
        else:
            self.blocking = True

    def clear_blocking(self):
        self.blocking = False

    def set_health(self, value):
        self.health = value

class Enemy(Entity):
    pass

class Player(Entity):
    
    def __init__(self, name: str, health: int, strength: int, points: int, inventory:dict) -> None:
        super().__init__(name, health, strength)
        self.points = points
        self.inventory = inventory
    def change_points(self, amount:int):
        if self.points + amount > 0:
            self.points += amount
        else:
            self.points = 0


class Item(object):

    def __init__(self, name:str, price:int):
        self.name = name
        self.price = price ## Unused
        
        

class Food(Item):

    def __init__(self, name:str, price:int, healthchange:int, healthchangerand = 0):
        super().__init__(name, price)

    def use_item(player:Player):
        healthboost = healthchange
        if healthchangerandom:
            healthboost += random.randint(1, healthchangerandom)
        player.health += healthboost

class Outcomes(Enum):
    VICTORY=0
    DEATH=1
    ESCAPE=2

class Stage(Enum):
    START=0
    ENCOUNTER=1
    COMBAT=2
    VICTORY=3
    DEATH=4

class EntityMoves(Enum):
    ATTACK=0
    BLOCK=1

class Difficulty(Enum):
    VERY_EASY=0.5
    EASY=1
    MEDIUM=1.25
    HARD=1.5
    VERY_HARD=1.75
    IMPOSSIBLE=2

def display_info(screen, player:Player):
    rows, cols = screen.getmaxyx()
    screen.addstr(1, cols//2-(len("Press q to exit")//2), "Press q to exit")
    screen.addstr(2, cols//2-(len("Press q to exit")//2), f"Player: {player.health}hp")
    screen.addstr(3, cols//2-(len("Press q to exit")//2), f"Points: {player.points}")

def handle_input(screen:curses.window)->str:
    key = screen.getkey()
    if key == 'q':
        exit(0)
    else:
        return key

def center_text(screen:curses.window, text:str, offsetr=0, offsetc=0, mode=curses.A_NORMAL):
    rows, cols = screen.getmaxyx()
    screen.addstr( clamp(rows//2+offsetr, 0, rows) , clamp(cols//2-(len(text)//2)+offsetc, 0 , cols) , text, mode)

def show_debug(screen:curses.window, text:str):
    screen.clear()
    screen.refresh()
    center_text(screen, text)
    handle_input(screen)

def create_menu(screen:curses.window, title:str, options:dict[str:int], index:int=0, enemy:Enemy=None, startpos=3, player:Player=None)->bool:
    rows, cols = screen.getmaxyx()
    option_amount = len(options)-1
    while 1:
        screen.clear()
        screen.refresh()
        center_text(screen, title)
        if enemy:
            center_text(screen, f"{enemy.name}:{enemy.health}hp, strength: {enemy.strength}", offsetr=1)
        if player:
            display_info(screen, player)
        for option in enumerate(options):
            if option[0] == index:
                center_text(screen, option[1], offsetr=startpos+option[0], mode=curses.A_REVERSE)
            else:
                center_text(screen, option[1], offsetr=startpos+option[0])
        key = handle_input(screen) 
        if key == "KEY_UP" and index > 0:
            index -= 1
        elif key == "KEY_DOWN" and index < option_amount:
            index += 1
        elif key in ["KEY_ENTER", '\n']:
            return [x for x in enumerate(options) if x[0] == index][0]
            #selected_option = [x for x in options.items() if x[0] == index][0]
            #return selected_option[1]  # Return the value instead of the index





def combat_loop(screen, enemy:Enemy, player:Player)->Outcomes:
    combat_options = {
        'block' : 0,
        'attack': 1,
        'use item' : 2,
        'run away (50% of success)': 3
    }
    while 1:
        x = create_menu(screen, f"What is you move against {enemy.name}?", combat_options, enemy=enemy, player=player)
        x = x[0]
        center_text(screen, f"{enemy.name} {enemy.health}")
        if x == 0:
           player.toggle_blocking()
        elif x == 1:
            screen.refresh()
            screen.clear()
            damage = (random.randint(0, 5) + player.points)
            if enemy.blocking:
                enemy.take_damage(damage)
                damage //= 2
                center_text(screen, f"You attack but {enemy.name} blocks and you deal {damage} damage")
            else:
                enemy.take_damage(damage)
                center_text(screen, f"You dealt {damage} damage")
            handle_input(screen)
        elif x == 2:
            food_menu = {}
            for item, amount in player.inventory.items():
                food_menu[item.name] = hash(item)
            res = create_menu(screen, "Inventory", food_menu)
            rev_dict = {v: k for k, v in food_menu.items()}
            with open("log.txt", "w") as debug_file:
                to_log = [str(rev_dict), str(res)]
                debug_file.write(str(to_log))
        elif x == 3:
            if random.randint(0,1):
                return Outcomes.ESCAPE
            else:
                screen.clear()
                screen.refresh()
                center_text(screen, 'You fail to escape')
                handle_input(screen)
        if enemy.dead:
            return Outcomes.VICTORY
        enemy.clear_blocking()
        
        ## Enemy action

        enemy_actions = [EntityMoves.ATTACK, EntityMoves.BLOCK]

        action = random.choice(enemy_actions)

        screen.clear()
        screen.refresh()

        if action == EntityMoves.ATTACK:
            damage = enemy.strength + (random.randint(0, enemy.strength//2))
            player.take_damage(damage)
            if player.blocking:
                damage //= 2
                center_text(screen,f'{enemy.name} attacks but you block and {enemy.name} deals {damage} damage')
            else:
                center_text(screen,f'{enemy.name} slashes you for {damage} damage')    
        elif action == EntityMoves.BLOCK:
            center_text(screen,f'{enemy.name} blocks your next attack making you deal half damage with your next attack')
            enemy.toggle_blocking()
        handle_input(screen)
        player.clear_blocking()

        if player.dead:
            return Outcomes.DEATH


def main(screen:curses.window):
    GAMESTAGE = Stage.START
    DIFFICULTY = Difficulty.VERY_EASY.value # no increase, 1.25 is harder each time for example
    screen.keypad(True)
    curses.curs_set(0)
    enemy=None
    init_player_inv = {
        Food("Cheesecake", 10, 4, 3) : 2,
        Food("Deluxe Cheesecake", 50, 8, 5) : 1
        #"Bomb" : 1
    }
    player=Player("Player", 100, 1, 0, init_player_inv)
    fun=False
    while 1:
        screen.clear()
        screen.refresh()
        rows, cols = screen.getmaxyx()
        if GAMESTAGE == Stage.START:
            center_text(screen, "You awake in a foreign land, Press any key to continue")
            key = handle_input(screen)
            GAMESTAGE = Stage.ENCOUNTER
        elif GAMESTAGE == Stage.ENCOUNTER:
            # TODO implement naming based on strength of enemy
            enemy_names = ['Placeholder John', 'Placeholder Tom']
            enemy = Enemy(name=enemy_names[random.randint(0,1)], health=random.randint(1,100), strength=int(random.randint(1, 5)+(DIFFICULTY*player.points)))
            encounter_options = {
                'fight' : 0,
                'run away': 1
            }
            encounter_prompts = [f'As you wander around {enemy.name} approaches you',f'A wild {enemy.name} appears',f'You see a {enemy.name} when looking behind you']
            x = create_menu(screen, random.choice(encounter_prompts), encounter_options, enemy=enemy)
            x = x[0]
            if x == 0:
                GAMESTAGE = Stage.COMBAT
            elif x == 1:
                screen.refresh()
                screen.clear()
                display_info(screen, player)
                center_text(screen, "You run away")
                handle_input(screen)
                continue
        elif GAMESTAGE == Stage.COMBAT:
            result = combat_loop(screen, enemy, player)
            if result == Outcomes.VICTORY:
                player.change_points(+1)
                screen.clear()
                screen.refresh()
                display_info(screen, player)
                center_text(screen, "You won and got 1 point which makes you deal 1 more base damage")
                handle_input(screen)
                GAMESTAGE = Stage.ENCOUNTER
            elif result == Outcomes.DEATH:
                screen.clear()
                screen.refresh()
                if not fun:
                    center_text(screen, "Game Over!")
                    handle_input(screen)
                    exit(0)
                display_info(screen, player)
                player.change_points(-1)
                center_text(screen, "You were defeated and lost 1 point")
                handle_input(screen)
                GAMESTAGE = Stage.ENCOUNTER
            elif result == Outcomes.ESCAPE:
                screen.clear()
                screen.refresh()
                display_info(screen, player)
                center_text(screen, "You successfully escaped")
                handle_input(screen)
                GAMESTAGE = Stage.ENCOUNTER
            if player.points > 0 and player.health < 100:
                heal_options = {
                    'Yes':0,
                    'No':1
                }
                screen.clear()
                screen.refresh()
                display_info(screen, player)
                health_response = create_menu(screen, "Your health is less than 100, do you want to rest and spend 1 point restoring your health to 100?", heal_options)
                health_response = health_response[0]
                if health_response == 0:

                    player.set_health(100)
                elif health_response == 1:
                    pass
                


curses.wrapper(main)
