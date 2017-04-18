class Skills:
    def __init__(self,strength=0,dexterity=0,wisdom=0):
        self.strength = strength
        self.dexterity = dexterity
        self.wisdom = wisdom


class Player:
    def __init__(self):
        self.skills = Skills()

