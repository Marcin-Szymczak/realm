import globals
import hooks

import world
from shared.network import Packet
import random

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
    pl.name = client.account
    pl.world = "main"
    map = worlds[pl.world]

    while True:
        x = random.randint(0,map.width)
        y = random.randint(0,map.height)
        if map.get_tile(x,y,0) == 0:
            break

    pl.x = x
    pl.y = y
    pl.world = "main"
    globals.server.broadcast( packet_player_list() )
    client.send(packet_map_content(pl.world))

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
    })
    return packet

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
        packet = Packet("game",{
            "target":"player",
            "player_id":client.id,
            "strength":0,
            "dexterity":0,
            "wisdom":0,
            "health":0,
            "health_capacity":0,
            "mana":0,
            "mana_capacity":0
        })
        client.send(packet)
    elif data["type"] == "attack":
        packet = Packet("game",{
            "type":"result",
            "action":"attack",
            "x": data["x"],
            "y": data["y"],
            "result":False,
            "description":"Action not yet implemented!"
        })
        client.send(packet)

