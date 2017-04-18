import queue
import select
import socket
import threading

import account
import game
import traceback
import sys

from shared.network import Packet

server = None

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

        self.send_queue = queue.Queue()
        self.receive_queue = queue.Queue()

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
        self.socket.setblocking(False)
        self.max_clients = 0
        self.ip = ip
        self.port = port
        self.thread = None
        self.queue = queue.Queue()

        self.clients = []

    def set_max_clients(self, max):
        self.max_clients = max

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
        client.socket.shutdown(socket.SHUT_RDWR)
        client.socket.close()
        self.clients[client.id] = None

    def accept_clients(self):
        lists = select.select([self.socket],[],[],0)

        for to_accept in lists[0]:
            conn, addr = self.socket.accept()
            conn.setblocking(False)
            client = Client(conn,addr,len(self.clients))
            self.clients.append(client)
            print(f"{client} connected!")

    def process_packets(self):
        for client in self.clients:
            if not client:
                continue

            read, write = select.select([client.socket],[client.socket],[],0)[0:2]
            if read:
                message = client.socket.recv(4096)
                if len(message) == 0:
                    self.disconnect_client(client)
                    continue
                try:
                    packet = Packet.from_bytes(message)
                    client.receive_queue.put(packet)
                    #print(packet)
                except Exception as e:
                    print(f"Invalid packet {message} {e}")

            if write:
                while not client.send_queue.empty():
                    packet = client.write_queue.get(False)
                    packet.send(client)

    def main_loop(self):
        run = True
        account.load_accounts()
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
    server = Server(ip="localhost",port=50000)
    server.set_max_clients(4096)
    server.start()

    while True:
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
            del account.accounts[parts[1]]
        else:
            print("Unknown command!")
