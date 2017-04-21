class Player:
    def __init__(self):
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

    def packet(self):
        return {
            "name":self.name,
            "x":self.x,
            "y":self.y,
        }
