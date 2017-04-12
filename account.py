from shared.network import Packet

import re
import os
import json

accounts = {}

accounts_dir = "accounts"

# noinspection PyTypeChecker
def handle_packet(client,packet):
    payload = packet.data
    if payload["type"] == "login":
        if client.account:
            packet = Packet("account",{
                "type":"result",
                "action":"login",
                "result":False,
                "description":"Already logged in!",
            })
            packet.send(client.socket)
            return
        acc = payload["account"]
        if acc in accounts:
            if accounts[acc]["password"] == payload["password"]:
                client.account = acc
                packet = Packet("account",{
                    "type":"result",
                    "action":"login",
                    "account":payload["account"],
                    "result":True,
                })
                packet.send(client.socket)
                return
            else:
                packet = Packet("account",{
                    "type":"result",
                    "action":"login",
                    "result":False,
                    "description":"Invalid password.",
                })
                packet.send(client.socket)
                return
        else:
            packet = Packet("account",{
                "type":"result",
                "action":"login",
                "result":False,
                "description":"Account does not exist.",
            })
            packet.send(client.socket)
            return


    if payload["type"] == "register":
        acc = payload["account"]
        if acc in accounts:
            packet = Packet("account",{
                "type":"result",
                "action":"register",
                "result":False,
                "description":f"{acc} already exists."
            })
            packet.send(client.socket)
            return
        if not re.match("[a-zA-Z0-9_\-]", payload["account"]):
            packet = Packet("account",{
                "type":"result",
                "action":"register",
                "result":False,
                "description":f"Account can contain only letters, numbers and a dash."
            })
            packet.send(client.socket)
            return
        register(payload["account"], payload["password"])
        packet = Packet("account",{
            "type":"result",
            "action":"register",
            "account":payload["account"],
            "result":True,
        })
        packet.send(client.socket)

def save_account(account):
    if account in accounts:
        if not os.path.exists(accounts_dir):
            os.mkdir(accounts_dir)

        with open(f"{accounts_dir}/{account}.account", 'w') as f:
           f.write(json.dumps(accounts[account]))

def save_accounts():
    for acc in accounts:
        save_account(acc)

def load_account(account, clear=False):
    if not os.exists(f"{accounts_dir}/{account}"):
        return False

    with open(f"{accounts_dir}/{account}") as f:
        try:
            data = json.loads(f.read(-1))
        except:
            return False

        accounts[account] = data
    return True

def load_accounts():
    if not os.path.exists(f"{accounts_dir}"):
        return
    for entry in os.scandir(f"{accounts_dir}/"):
        match = re.match("(.*)\.account", entry.name)
        if match and entry.is_file():
            if load_account(match[1]):
                print(f"Account {match[1]} loaded!")


def register(login,password):
    if login in accounts:
        return False

    accounts[login] = {
        "password":password,
        "lastlogin":"never",
        "total_playtime":0}
    print(f"Registered account {login}")
    save_account(login)

def print_accounts():
    for acc in accounts.keys():
        print(acc)

def print_details(acc):
    if acc in accounts:
        for key in accounts[acc].keys():
            print(f"{key}: {accounts[acc][key]}")
    else:
        print(f"Account {acc} does not exist.")