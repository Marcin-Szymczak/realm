from shared import world
from server import server
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
                "message":data["message"]
            })
            for client in server.clients:
               packet.send(client)
