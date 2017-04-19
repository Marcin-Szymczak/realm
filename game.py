import globals
from shared import world
from shared.network import Packet
worlds = {}

def init():
    w = world.Level(16,16,1)
    worlds[0] = w

def update():
    pass

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

    if data["type"] == "player_list_request":
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

        client.send(packet)
    if data["type"] == "map_request":
        map = worlds[0]

        packet = Packet("game",{
            "type":"map_content",
            "width":map.width,
            "height":map.height,
            "data":map.data,
        })

        client.send(packet)
        print(f"Map content sent to client {client.account}")
