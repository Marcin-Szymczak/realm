import random

def roll(dicedef):
    parts = dicedef.lower().split('d')
    dices = int(parts[0])
    sides = int(parts[1])

    return random.randint(dices,dices*sides)

def min(dicedef):
    parts = dicedef.lower().split('d')
    return int(parts[0])
def max(dicedef):
    parts = dicedef.lower().split('d')
    return int(parts[0])*int(parts[1])

if __name__ == "__main__":
    print(f"""1d6: {roll("1d6")}""")
    print(f"""2d5: {roll("2d5")}""")
    print(f"""3d8: {roll("3d8")}""")
    print(f"""10d10: {min("10d10")}-{max("10d10")}""")
