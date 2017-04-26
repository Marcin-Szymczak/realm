import enum
import json
import socket

class Packet:
    type_length = 1
    endianness = "big"
    
    END_MARKER = b'\xFF'
    
    msg_group = [
        "disconnect",
        "account",
        "game"
        ]

    msg_lookup = {}
    for i,t in enumerate(msg_group):
        msg_lookup[t] = i

    def __init__(self,group,data):
        self.group = group
        self.data = data

    def __repr__(self):
        return f"{self.group} {self.data}"

    def create_buffer():
        return bytearray()

    def recv(data,buffer):
        if data:
            buffer += data
        packet = None
        index = buffer.find(b'\xFF')
        if index != -1:
            data = buffer[0:index+1]
            packet = Packet.from_bytes(data)
            if index < len(buffer)-2:
                buffer = buffer[index+1:]
            else:
                buffer = bytearray()
        return packet, buffer

    def from_bytes(data):
        if data[-1] != Packet.END_MARKER[0]:
            return None
        group = Packet.msg_group[ data[0]]
        data = json.loads(data[1:-1].decode(), encoding='utf-8')
        return Packet(group,data)

    def to_bytes(self):
        data = bytearray()
        data += Packet.msg_lookup[ self.group].to_bytes(Packet.type_length, Packet.endianness)
        data += json.dumps(self.data).encode('utf-8')
        data += Packet.END_MARKER;
        return data

    def send(self, sock):
        raw_data = self.to_bytes()
        count = sock.send(raw_data)
        # print(f"Sent packet, {count} bytes")
        return raw_data[count:]


