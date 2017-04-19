import globals
from shared import world
from shared.network import Packet
worlds = {}

def init():
    w = world.Level(64,16,2)
    worlds[0] = w

def update():
    pass

def handle_packet(client, packet):
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
               packet.send(client)

    if data["type"] == "player_list_request":
        player_list = ()
        for client in globals.server.clients:

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

        client.send(packet)
