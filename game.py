import globals
import hooks

import world
from shared.network import Packet
import random
import math
import account

worlds = {}

def init():
    worlds["main"] = world.Level(64,32,1)
    worlds["main"].generate("giant room") 
    hooks.hook("client_connected", client_connected)
    hooks.hook("player_created", player_connected)
    
def update():
    pass

def client_connected(client):
    pass

def player_connected(client):
    print(f"Player {client.account} connected") 
    pl = client.player

    acc = account.accounts[client.account]

    if acc.get("player",False):
        print("restoring previous player!")
        pl.load_from_account(acc)
    else:
        pl.name = client.account
        pl.world = "main"

        pl.health_capacity = 10
        pl.spawn()
        pl.save_to_account(acc)

    globals.server.broadcast( packet_player_list() )
    client.send(packet_map_content(pl.world))
    client.send(packet_player_stats(client.id))

def packet_player_list():
    player_list = []
    for client in globals.server.clients:
        if not client: continue
        pl = {
            "name": client.account,
            "x": client.player.x,
            "y": client.player.y,
            "id": client.id,
        }

        player_list.append(pl)

    packet = Packet("game",{
        "type":"player_list",
        "players":player_list,
    })
    return packet

def packet_player_stats(id):
    client = globals.server.clients[id]
    pl = client.player
    packet = Packet("game",{
        "type":"stats",
        "target":"player",
        "player_id":id,
        "strength":pl.strength,
        "dexterity":pl.dexterity,
        "wisdom":pl.wisdom,
        "health":pl.health,
        "health_capacity":pl.health_capacity,
        "mana":pl.mana,
        "mana_capacity":pl.mana_capacity,
    })
    return packet

def packet_map_content(world, x=0,y=0,w=-1,h=-1):
    map = worlds[world]
    if w < 0:
        w = map.width+w+1
    if h < 0:
        h = map.height+h+1

    packet = Packet("game",{
        "type":"map_content",
        "width":map.width,
        "height":map.height,
        "slice_x":0,
        "slice_y":0,
        "slice_width":map.width,
        "slice_height":map.height,
        "data":map.data,
        "reset":True,
    })
    return packet

def find_player_on_map(x,y):
    for client in globals.server.clients:
        if not client: continue
        pl = client.player
        if pl.x == x and pl.y == y:
            return pl
    return None

def resolve_attack(attacker, victim):
    if math.sqrt( (attacker.x-victim.x)**2 + (attacker.y-victim.y)**2) > 1:
        packet = Packet("game",{
            "type":"result",
            "action":"attack",
            "x":victim.x,
            "y":victim.y,
            "result":False,
            "description":"Too far away!",
        })
        attacker.send(packet)
        return

    victim.health -= 1
    if victim.health <= 0:
        victim.spawn()
    packet = Packet("game",{
        "type":"result",
        "action":"attack",
        "x":victim.x,
        "y":victim.y,
        "result":True
    })

    attacker.client.send(packet)
    for client in [attacker.client,victim.client]:
        client.send(packet_player_stats(attacker.client.id))
        client.send(packet_player_stats(victim.client.id))


def handle_packet(client, packet):
    if not client:
        return
    data = packet.data
    if data["type"] == "chat":
        if data["channel"] == "global":
            packet = Packet("game",{
                "type":"chat",
                "channel":"global",
                "message":data["message"],
                "player_id":client.id,
            })

            for client in globals.server.clients:
                if client:
                    client.send(packet)

    elif data["type"] == "player_list_request":
        client.send(packet_player_list())

    elif data["type"] == "map_request":
        client.send(packet_map_content(client.player.world,0,0,-1,-1))
        print(f"Map content sent to client {client.account}")
    elif data["type"] == "set_position":
        pl = client.player
        x = pl.x
        y = pl.y
        new_x = data['x']
        new_y = data['y']
        map = worlds[pl.world]
        client.player.x = data["x"]
        client.player.y = data["y"]
        if abs(new_x - x) + abs(new_y - y) > 1:
            return
        if map.get_tile(new_x,new_y,0) == 1:
            return
        globals.server.broadcast(packet_player_list())
    elif data["type"] == "stats_request":
        client.send(packet_player_stats(client.id))
    elif data["type"] == "attack":
        attacker = client.player
        victim = find_player_on_map(data["x"], data["y"])
        if not victim:
            packet = Packet("game", {
                "type":"result",
                "action":"attack",
                "result":False,
                "x":data["x"],
                "y":data["y"],
                "description":"No object found on the requested position."
            })
            client.send(packet)
            return
        resolve_attack(attacker,victim)

