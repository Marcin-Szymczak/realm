from shared.network import Packet

import re
import os
import json
import game
import hooks

accounts = {}

accounts_dir = "accounts"

def init():
    hooks.hook("client_connected", client_connected)
    hooks.hook("client_disconnected", client_disconnected)
    load_accounts()

# noinspection PyTypeChecker
def handle_packet(client,packet):
    payload = packet.data
    if payload["type"] == "login":
        if client.account:
            packet = Packet("account",{
                "type":"result",
                "action":"login",
                "result":False,
                "description":"You are already logged in!",
            })
            client.send(packet)
            return
        acc = payload["account"]
        if acc in accounts:
            if "logged_in" in accounts[acc]["temporary"]:
                packet = Packet("account",{
                    "type":"result",
                    "action":"login",
                    "account":payload["account"],
                    "result":False,
                    "description":"Someone is already logged in this account!",
                })
            # Client succesfully logged in
            if accounts[acc]["password"] == payload["password"]:
                client.account = acc
                accounts[acc]["temporary"]["logged_in"] = True
                packet = Packet("account",{
                    "type":"result",
                    "action":"login",
                    "account":payload["account"],
                    "result":True,
                })
                client.send(packet)
                hooks.call("player_created",client)
                return
            else:
                packet = Packet("account",{
                    "type":"result",
                    "action":"login",
                    "result":False,
                    "description":"Invalid password.",
                })
                client.send(packet)
                return
        else:
            packet = Packet("account",{
                "type":"result",
                "action":"login",
                "result":False,
                "description":"Account does not exist.",
            })
            client.send(packet)
            return


    if payload["type"] == "register":
        acc = payload["account"]
        if acc in accounts:
            packet = Packet("account",{
                "type":"result",
                "action":"register",
                "account":payload["account"],
                "result":False,
                "description":f"{acc} already exists."
            })
            client.send(packet)
            return
        if not re.match("[a-zA-Z0-9_\-]", payload["account"]):
            packet = Packet("account",{
                "type":"result",
                "action":"register",
                "account":payload["account"],
                "result":False,
                "description":f"Account can contain only letters, numbers and a dash."
            })
            client.send(packet)
            return
        register(payload["account"], payload["password"])
        packet = Packet("account",{
            "type":"result",
            "action":"register",
            "account":payload["account"],
            "result":True,
        })
        client.send(packet)

def client_connected(client):
    packet = Packet("account",{
        "type":"client_info",
        "id":client.id,
        })
    client.send(packet)

def client_disconnected(client):
    if client.account and client.account in accounts:
        acc = accounts[client.account]
        client.player.save_to_account(acc)
        save_account(client.account)

def save_account(account):
    if account in accounts:
        if not os.path.exists(accounts_dir):
            os.mkdir(accounts_dir)
        filename = f"{accounts_dir}/{account}.account"
        with open(filename, 'w') as f:
            temp = accounts[account]["temporary"]
            del accounts[account]["temporary"]
            f.write(json.dumps(accounts[account]))
            accounts[account]["temporary"] = temp
        print(f"Account {account} saved!")

def save_accounts():
    for acc in accounts:
        save_account(acc)
        print(f"Account {acc} saved")

def load_account(account, clear=False):
    filename = f"{accounts_dir}/{account}.account"
    if not os.path.exists(filename):
        return False

    with open(filename) as f:
        try:
            data = json.loads(f.read(-1))
        except:
            return False

        accounts[account] = data
        accounts[account]["temporary"] = {}
    return True

def load_accounts():
    if not os.path.exists(f"{accounts_dir}"):
        return

    for entry in os.scandir(f"{accounts_dir}/"):
        match = re.match("(.*)\.account", entry.name)
        if match and entry.is_file():
            acc = match.group(1)
            if load_account(acc):
                print(f"Account {acc} loaded!")

def delete(account):
    if account in accounts:
        del accounts[account]
        os.remove(f"{accounts_dir}/{account}.account")

def register(login,password):
    if login in accounts:
        return False

    accounts[login] = {
        "password":password,
        "lastlogin":"never",
        "total_playtime":0,
        "temporary":{}}
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
