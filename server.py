import globals
import queue
import select
import socket
import threading

import account
import game
import traceback
import sys
import game
import hooks
import time

from player import Player

from shared.network import Packet

_PRINT_PACKETS = False

class Client:
    STATE_CONNECTING = 0
    STATE_CONNECTED = 1
    STATE_DISCONNECTED = 255

    def __init__(self,sock,addr,id):
        self.ip = addr
        self.socket = sock
        self.state = Client.STATE_CONNECTING
        self.id = id

        self.account = None

        self.player = Player(self)

        self.send_queue = queue.Queue()
        self.receive_queue = queue.Queue()
        self.recv_buffer = Packet.create_buffer()

    def __repr__(self):
        return f"(Client #{self.id} {self.ip} : {self.state}"

    def send(self, packet):
        self.send_queue.put(packet, False)

    def send_scheduled(self):
        return not self.send_queue.empty()

    def receive(self):
        if self.receive_queue.empty():
            return None
        return self.receive_queue.get(False)

    def receive_available(self):
        return not self.receive_queue.empty()

    def handle_packet(self,packet):
        try:
            if packet.group == "account":
                account.handle_packet(self,packet)
            elif packet.group == "game":
                game.handle_packet(self, packet)
        except Exception as e:
           print( traceback.format_exc() )


class Server:
    def __init__(self,*,ip=None,port=None,max_clients=0):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.socket.setblocking(False)
        self.max_clients = 0
        self.ip = ip
        self.port = port
        self.thread = None
        self.queue = queue.Queue()

        self.clients = []

    def set_max_clients(self, max):
        self.max_clients = max

    def broadcast(self, packet):
        for cl in self.clients:
            if not cl: continue
            cl.send(packet)

    def get_hostname(self):
        return self.socket.getsockname()

    def print_clients(self):
        print(f"{len(self.clients)} clients connected")
        for client in self.clients:
            print(client)

    def handle_commands(self):
        should_run = True
        while not self.queue.empty():
            item = self.queue.get(False)
            if not item:
                break
            if item == "quit":
                should_run = False

        return should_run

    def disconnect_client(self, client):
        print(f"{client} disconnected!")
        #client.socket.shutdown(socket.SHUT_RDWR)
        hooks.call("client_disconnected",client)
        client.socket.close()
        self.clients[client.id] = None

    def accept_clients(self):
        lists = select.select([self.socket],[],[],0)

        for to_accept in lists[0]:
            conn, addr = self.socket.accept()
            conn.setblocking(False)
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            client = Client(conn,addr,id=len(self.clients))
            self.clients.append(client)
            print(f"{client} connected!")
            hooks.call("client_connected", client)

    def process_packets(self):
        try:
            for client in self.clients:
                if not client:
                    continue
                packet, client.recv_buffer = Packet.recv(None, client.recv_buffer)
                while packet:
                    if _PRINT_PACKETS: print(f"<<{client.id}<<",packet)
                    client.receive_queue.put(packet)
                    packet, client.recv_buffer = Packet.recv(None, client.recv_buffer)


                read, write = select.select([client.socket],[client.socket],[],0)[0:2]
                if read:
                    message = client.socket.recv(2048)
                    if len(message) == 0:
                        self.disconnect_client(client)
                        continue
                    try:
                        #packet = Packet.from_bytes(message)
                        packet,client.recv_buffer = Packet.recv(message, client.recv_buffer)
                        while packet:
                            if _PRINT_PACKETS: print(f"<<{client.id}<<",packet)
                            client.receive_queue.put(packet)
                            packet, client.recv_buffer = Packet.recv(None, client.recv_buffer)

                    except Exception as e:
                        print(f"Invalid packet {message} {e}")
                        traceback.print_exc(file=sys.stdout)

                if write:
                    if not client.send_queue.empty():
                        packet = client.send_queue.get(block=False)
                        if packet:
                            packet.send(client.socket)
                        if _PRINT_PACKETS: print(f">>{client.id}>>",packet)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)

    def main_loop(self):
        run = True
        account.init()
        game.init()
        while run:
            run = self.handle_commands()
            self.accept_clients()
            self.process_packets()
            for client in self.clients:
                if not client:
                    continue

                while client.receive_available():
                    client.handle_packet(client.receive())
            time.sleep(0.01)
            #game.update()
        account.save_accounts()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()


    def start(self):
        self.socket.bind((self.ip,self.port))
        self.socket.listen(self.max_clients)
        self.thread = threading.Thread(target=self.main_loop)
        self.thread.start()

if __name__ == "__main__":
    hooks.register("client_connected",Client)
    hooks.register("player_created",Client)
    hooks.register("client_disconnected",Client)
    
    globals.server = Server(ip="localhost",port=50000)
    server = globals.server
    server.set_max_clients(4096)
    server.start()

    while True:
        try:
            command = input(f"{server.get_hostname()}$ ")
            parts = command.split(' ',maxsplit=2)
            if command == "quit":
                server.queue.put("quit")
                break
            elif command == "clients":
                server.print_clients()
            elif command == "accounts":
                account.print_accounts()
            elif parts[0] == "account":
                account.print_details(parts[1])
            elif command == "register":
                account.register(input("login: "), input("password: "))
            elif parts[0] == "delaccount":
                #del account.accounts[parts[1]]
                account.delete(parts[1])
            elif parts[0] == "debug_packets":
                _PRINT_PACKETS = bool(parts[1])
                print(f"_PRINT_PACKETS {_PRINT_PACKETS}")
            else:
                print("Unknown command!")
        except Exception as e:
            print(e.msg())
            traceback.print_exc(file=sys.stdout)
