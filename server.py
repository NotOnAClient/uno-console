import socket
import pickle
import threading
from _thread import *
from itertools import cycle
from itertools import islice
import uno

FORMAT = 'utf-8'
server_settings = []

header = 50
players = {} #{player:cards}

player_client_dict = {} # used for changing turns {player:client connection}
turn_index = int()
cencard = uno.starting_card()
game = uno.Game()


class Server:
    def __init__(self):
        # Read server settings
        with open('server_settings.txt', 'r') as settings:
            for i in settings.readlines():
                i = i.rstrip('\n')
                p = i.split('=')
                print(p)
                server_settings.append(p[1])

        self.host = server_settings[0]
        self.port = int(server_settings[1])
        self.max_players = int(server_settings[2])
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        
        self.client_list = [] #used to send/broadcast messages
        
    def broadcast(self, msg):
        # If string is broadcast
        if type(msg) == str: #string
            msg = msg.encode(FORMAT)
            msg_header = f"{len(msg):<{header}}".encode(FORMAT)
            for i in reversed(self.client_list):
                try:
                    i.send(msg_header + msg)
                except ConnectionResetError:
                    self.client_list.remove(i)
        else: # If data is broadcast(list, dict, etc.)
            data = pickle.dumps(msg)
            data_header = f"{len(data):<{header}}".encode(FORMAT)
            for i in reversed(self.client_list):
                try:
                    i.send(data_header + data)
                except ConnectionResetError:
                    self.client_list.remove(i)

    def send(self, client_socket, msg):
        if isinstance(msg, str):  # If message is a string
            msg_type = 'str'  # Indicate string type
            msg = msg.encode(FORMAT)
        else:  # Assume message is pickleable
            msg_type = 'pickle'  # Indicate pickle type
            msg = pickle.dumps(msg)

        msg_header = f"{len(msg):<{header}}{msg_type:<10}".encode(FORMAT)

        # Send header followed by the message
        client_socket.send(msg_header + msg)

    def recv_info(self):
        username = self.recv_str()
        d = self.recv_data()
        players.update({username: d})
        return username


    def handle_client(self, clientsocket, address, username):
        while True:
            try:
                pass
            except ConnectionResetError:
                print(f'{username} left the server')
                self.client_list.remove(clientsocket)
                del players[username]
                del player_client_dict[username]
                print(players)
                break
        clientsocket.close()

    def receive(self, client_socket):
        try:
            # Read the header. It is header + 10 to account for header size, and 10 is length of data type(str, pickle).
            msg_header = client_socket.recv(header + 10).decode(FORMAT)

            # Get length and data type of message
            msg_length = int(msg_header[:header].strip())
            msg_type = msg_header[header:].strip()

            # Read the actual message
            msg = client_socket.recv(msg_length)

            if msg_type == 'str':
                str = msg.decode(FORMAT)
                print(f"{client_socket}: {str}")
                return str
            elif msg_type == 'pickle':
                pckl = pickle.loads(msg)
                print(f"{client_socket}: {pckl}")
                return pckl
            else:
                raise ValueError(f"Unknown message type: {msg_type}")
        except Exception as e:
            print(f"An error occured: {e}")
            return None

    def client_thread(self, client_socket):
        try:
            while True:
                data = self.receive(client_socket)
                if data is None:
                    break
        except Exception as e:
            print(f"An error occurred in client_thread: {e}")
        finally:
            client_socket.close()
            print(f"Connection with {client_socket} closed.")

    def Main(self):
        self.server.listen()
        print(f"Server is listening on {self.host}:{self.port}")
        while True:
            client_socket, address = self.server.accept()
            self.client_list.append(client_socket)
            start_new_thread(self.client_thread, (client_socket,))
            

if __name__ == "__main__":
    server = Server()
    server.Main()
