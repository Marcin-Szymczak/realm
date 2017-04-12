import random

def roll(dicedef):
    parts = dicedef.lower().split('k')
    dices = int(parts[0])
    sides = int(parts[1])

    return random.randint(dices,dices*sides)

def min(dicedef):
    parts = dicedef.lower().split('k')
    return int(parts[0])
def max(dicedef):
    parts = dicedef.lower().split('k')
    return int(parts[0])*int(parts[1])

if __name__ == "__main__":
    print(f"""1k6: {roll("1k6")}""")
    print(f"""2k5: {roll("2k5")}""")
    print(f"""3k8: {roll("3k8")}""")
    print(f"""10k10: {min("10k10")}-{max("10k10")}""")
