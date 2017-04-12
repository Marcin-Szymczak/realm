import enum
import json
import socket

class Packet:
    type_length = 1
    endianness = "big"
    msg_group = [
        "disconnect",
        "account",
        "game"
        ]

    """
        packet.group can be:
            disconnect
            account
                type:
                    "login"
                    account: account
                    password: password
                    
                    "register"
                    account: account
                    password: password
                
                    "result"
                    action: "login"/"register"
                    result: True/False
                        True if the action succeded
                        False if the action failed
                    description: If the action failed, it contains the
                        reason of failure
            game
                type:
                    chat
                    channel: "global"
                    message: chat message
            
    """

    msg_lookup = {}
    for i,t in enumerate(msg_group):
        msg_lookup[t] = i

    def __init__(self,group,data):
        self.group = group
        self.data = data

    def __repr__(self):
        return f"{self.group} {self.data}"

    def from_bytes(data):
        packet = Packet()
        packet.group = Packet.msg_group[ data[0]]
        packet.data = json.loads(data[1:].decode(), encoding='utf-8')
        return packet

    def to_bytes(self):
        data = bytearray()
        data += Packet.msg_lookup[ self.group].to_bytes(Packet.type_length, Packet.endianness)
        data += json.dumps(self.data).encode('utf-8')
        return data

    def send(self, sock):
        return sock.send(self.to_bytes())
