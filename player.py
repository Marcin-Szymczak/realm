import game
import random

class Player:
    def __init__(self, client):
        self.client=client
        self.x = 0
        self.y = 0
        self.name = None
        self.world = None
        self.health = 1
        self.strength = 0
        self.dexterity = 0
        self.wisdom = 0
        self.health = 0
        self.health_capacity = 0
        self.mana = 0
        self.mana_capacity = 0
        self.experience = 0
        self.level = 1

    def spawn(self):
        map = game.worlds[self.world]
        while True:
            x = random.randint(0,map.width)
            y = random.randint(0,map.height)
            if map.get_tile(x,y,0) == 0:
                break
        self.x = x
        self.y = y
        self.health = self.health_capacity

    def load_from_account(self, account):
        self.name = account["player_name"]
        self.x = account['player_x']
        self.y = account['player_y']
        self.world = account['player_world']
        self.health = account["stats_health"]
        self.health_capacity = account["stats_health_capacity"]
        self.mana = account["stats_mana"]
        self.mana_capacity = account["stats_mana_capacity"]
        self.strength = account["stats_strength"]
        self.dexterity = account["stats_dexterity"]
        self.wisdom = account["stats_wisdom"]

    def save_to_account(self, account):
        account["player_name"] = self.name
        account["player_x"] = self.x
        account["player_y"] = self.y
        account["player_world"] = self.world
        account["stats_health"] = self.health
        account["stats_health_capacity"] = self.health_capacity
        account["stats_mana"] = self.mana
        account["stats_mana_capacity"] = self.mana_capacity
        account["stats_strength"] = self.strength
        account["stats_dexterity"] = self.dexterity
        account["stats_wisdom"] = self.wisdom
        account["stats_experience"] = self.experience
        account["stats_level"] = self.level
        account["player"] = True