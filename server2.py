import socket
import pickle
import threading
from itertools import cycle
import uno

header = 50
players = {} #{player:cards}
player_list = [] #store usernames
client_list = [] #used to send/broadcast messages
player_client_dict = {} # used for changing turns {player:client connection}
cencard = uno.starting_card()
game = uno.Game()
FORMAT = 'utf-8'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 6255))

class gameServer:
    def __init__(self):
        self.game_start = False

    def broadcast(self, msg):
        if type(msg) == str: #string
            msg = msg.encode(FORMAT)
            msg_header = f"{len(msg):<{header}}".encode(FORMAT)
            for i in client_list:
                print(f'broadcast: {i}')
                i.send(msg_header + msg)
        else: #pickle
            data = pickle.dumps(msg)
            data_header = f"{len(data):<{header}}".encode(FORMAT)
            for i in client_list:
                i.send(data_header + data)

    def send(self, msg, client=None):
        if client is None:
            client = self.clientsocket
        if type(msg) == str: #string
            msg = f"{len(msg):<{header}}" + msg
            client.send(msg.encode(FORMAT))
            #print(f'{msg} sent')
        else: #pickle
            data = pickle.dumps(msg)
            data = f"{len(data):<{header}}".encode(FORMAT) + data
            client.send(data)
            #print(f'{data} data')

    def recv_str(self, client=None):
        if client is None:
            client = self.clientsocket
        while True:
            msg_header = self.clientsocket.recv(header)
            msg_len = int(msg_header.decode(FORMAT))
            msg = self.clientsocket.recv(msg_len).decode(FORMAT)
            return msg

    def recv_data(self, client=None):
        if client is None:
            client = self.clientsocket
        while True:
            data_header = client.recv(header)
            data_len = int(data_header.decode(FORMAT))
            data = client.recv(data_len)
            d = pickle.loads(data)
            #print('data msg recvd')
            return d

    def recv_info(self):
        username = self.recv_str()
        d = self.recv_data()
        players.update({username: d})
        print(f'recv_info: {players}')
        return username


    def handle_client(self, clientsocket, address, username):
        while True:
            try:
                #while self.game_start:
                    #self.game()
                pass
            except ConnectionResetError:
                print(f'{username} left the server')
                client_list.remove(clientsocket)
                del players[username]
                del player_client_dict[username]
                print(players)
                #print(f'Active connections: {threading.activeCount() - 1}')
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
            #print(f'Active connections: {threading.activeCount() - 1}')
            while len(players) == 2:
                self.broadcast('Game started')
                self.game_start = True
                self.game()
   
    def change_turn(self):
        print(player_client_dict.items())
        for k,v in cycle(player_client_dict.items()):
            print(f"It is {k}'s turn")
            self.broadcast(f"It is {k}'s turn")
            yield k, v
            #return v

    def game(self):
        self.send('cencard')
        self.send(cencard)
        self.send('show cards')
        #self.broadcast('play card')
        condition = ''
        t = self.change_turn()
        while True:
            user, client = next(t)
            card_list = players[user]
            self.send('cencard', client=client)
            self.send(cencard, client=client)
            if condition != '':
                self.send(condition, client=client)
                if 'draw' in condition:
                    cards = self.recv_data(client=client)
                    print(f'cards: {cards}')
                    card_list = card_list + cards
                    print(f'card_list: {card_list}')
            self.send('show cards', client=client)
            self.send('play card', client=client)
            try:
                card = self.recv_data(client=client)
            except pickle.UnpicklingError:
                card = self.recv_str(client=client)
            if 'draw' in card:
                self.send('draw 1', client=client)
                cards = self.recv_data(client=client)
                card_list = card_list + card
                continue
            else:
                a = game.check_card(card)
                print(f'a {a}')
                if 'wild' in a:
                    wild = (a[0], '')
                    print(f'wild {wild}')
                    card_list.remove(wild)
                elif 'wild4' in a:
                    wild = (a[0], '')
                    print(f'wild4 {wild}')
                    condition = 'draw 4'
                    card_list.remove(wild)
                else:
                    card_list.remove(a)
                    condition = ''
                print(f'card_list: {user}, {card_list}')
                self.send('delete', client=client)
                self.send(a, client=client)
        

s = gameServer()
s.start()



