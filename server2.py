import socket
import pickle
import threading
from itertools import cycle
import uno

header = 50
players = {}
player_list = []
client_list = []
player_client_dict = {}
cencard = uno.starting_card()
game = uno.Game()
game_start = False
FORMAT = 'utf-8'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 6255))

class gameServer:
    def broadcast(self, msg):
        if type(msg) == str: #string
            msg = msg.encode(FORMAT)
            msg_header = f"{len(msg):<{header}}".encode(FORMAT)
            for i in client_list:
                i.send(msg_header + msg)
        else: #pickle
            data = pickle.dumps(msg)
            data_header = f"{len(data):<{header}}".encode(FORMAT)
            for i in client_list:
                i.send(data_header + data)

    def send(self, msg, client=None):
        if type(msg) == str: #string
            msg = f"{len(msg):<{header}}" + msg
            client.send(msg.encode(FORMAT))
            print(f'{msg} sent')
        else: #pickle
            data = pickle.dumps(msg)
            data = f"{len(data):<{header}}".encode(FORMAT) + data
            client.send(data)
            print(f'{data} data')

    def recv_str(self):
        #a = clientsocket.recv(2048).decode(FORMAT)
        #clientsocket.send('ready'.encode(FORMAT))
        while True:
            msg_header = self.clientsocket.recv(header)
            msg_len = int(msg_header.decode(FORMAT))
            msg = self.clientsocket.recv(msg_len).decode(FORMAT)
            return msg

    def recv_data(self):
        while True:
            data_header = self.clientsocket.recv(header)
            data_len = int(data_header.decode(FORMAT))
            data = self.clientsocket.recv(data_len)
            d = pickle.loads(data)
            print('data msg recvd')
            return d

    def recv_info(self):
        username = self.recv_str()
        d = self.recv_data()
        players.update({username: d})
        print(players)
        return username


    def handle_client(self, clientsocket, address, username):
        global game_start
        while True:
            try:
                #message = self.recv_str()
                #print(message)
                #continue
                pass
            except ConnectionResetError:
                print(f'{username} left the server')
                client_list.remove(clientsocket)
                del players[username]
                print(players)
                print(f'Active connections: {threading.activeCount() - 1}')
                break
        clientsocket.close()

    def start(self):
        global player_client_dict
        server.listen()
        while True:
            self.clientsocket, self.address = server.accept()
            print(f'Connection established wtih {self.address}')
            client_list.append(self.clientsocket)
            username = self.recv_info() #calling this username because i just wanted to get the username
            player_list.append(username)
            player_client_dict = dict(zip(player_list, client_list))
            thread = threading.Thread(target=self.handle_client, args=(self.clientsocket, self.address, username))
            thread.start()
            print(f'Active connections: {threading.activeCount() - 1}')
            while len(players) == 2:
                global game_start
                self.broadcast('Game started')
                game_start = True
                self.game()
   
    def change_turn(self):
        for k,v in cycle(player_client_dict.items()):
            print(f"It is {k}'s turn")
            yield self.send('play card', client=v)

    def game(self):
        t = self.change_turn()
        self.broadcast('cencard')
        self.broadcast(cencard)
        self.broadcast('show cards')
        next(t)
        card = self.recv_data()
        print(card)
        a = game.check_card(card)
        print(a)

#reminder: put game func into handle thread. 
# If game_start == True, run game function
        

s = gameServer()
s.start()



