import socket
import pickle
#import threading
from itertools import cycle
from itertools import islice
import uno

server_settings = []

with open('server_settings.txt', 'r') as settings:
    for i in settings.readlines():
        i = i.rstrip('\n')
        p = i.split('=')
        print(p)
        server_settings.append(p[1])

host = server_settings[0]
port = int(server_settings[1])
max_players = int(server_settings[2])

header = 50
players = {} #{player:cards}
player_list = [] #store usernames
client_list = [] #used to send/broadcast messages
player_client_dict = {} # used for changing turns {player:client connection}
turn_index = int()
cencard = uno.starting_card()
game = uno.Game()
FORMAT = 'utf-8'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

class gameServer:
    def __init__(self):
        self.game_start = False
        self.turn_list = []

    def broadcast(self, msg):
        if type(msg) == str: #string
            msg = msg.encode(FORMAT)
            msg_header = f"{len(msg):<{header}}".encode(FORMAT)
            for i in reversed(client_list):
                #print(f'broadcast: {i}')
                try:
                    i.send(msg_header + msg)
                except ConnectionResetError:
                    client_list.remove(i)
        else: #pickle
            data = pickle.dumps(msg)
            data_header = f"{len(data):<{header}}".encode(FORMAT)
            for i in reversed(client_list):
                try:
                    i.send(data_header + data)
                except ConnectionResetError:
                    client_list.remove(i)

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
        #print(f'recv_info: {players}')
        return username


    def handle_client(self, clientsocket, address, username):
        while True:
            try:
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
            #thread = threading.Thread(target=self.handle_client, args=(self.clientsocket, self.address, username))
            #thread.start()
            #print(f'Active connections: {threading.activeCount() - 1}')
            if len(players) == max_players:
                self.turn_list = list(zip(player_list, client_list))
                self.broadcast('Game started')
                self.broadcast('cencard')
                self.broadcast(cencard)
                self.broadcast('show cards')
                self.game_start = True
                self.game()
   
    def change_turn(self):
        global turn_index
        global player_client_dict
        print(f'player_list: {player_list}')
        #print(f'reversed player_list: {list(reversed(player_list))}')
        #print(f'turn_list: {self.turn_list}')
        turn = self.turn_list[0]
        #reverse_count = 0
        lst = []
        restart = True
        while restart:
            if turn_index < 0: #if turn_index is negative, errors will appear
                turn_index = len(self.turn_list) - 1
            for k,v in islice(cycle(self.turn_list), int(turn_index), None):
                print(f'turn_list: {self.turn_list}')
                #print(k)
                turn = (k,v)
                if self.condition == 'skip':
                    self.condition = ''
                    turn_index = self.turn_list.index(turn)
                    continue
                if self.condition == 'reverse':
                    lst = self.turn_list[::-1]
                    self.turn_list = lst
                    #reverse_count += 1
                    #turn = (k,v)
                    turn_index = self.turn_list.index(turn) - 1
                    print(f'turn_index: {turn_index}')
                    print(f'self.turn_list reverse: {self.turn_list}')
                    #restart = True
                    lst = []
                    self.condition = ''
                    break
                #restart = False
                turn_index = self.turn_list.index(turn)
                print(f'turn_index: {turn_index}')
                print(f"It is {k}'s turn")
                self.broadcast(f"It is {k}'s turn")
                yield k, v
                #return v

    def game(self):
        global players
        self.game_start = True
        self.send('cencard')
        self.send(cencard)
        self.send('show cards')
        #self.broadcast('play card')
        self.condition = ''
        t = self.change_turn()
        self.next_turn = True
        while True:
            if self.next_turn:
                self.user, self.client = next(t)
            card_list = players[self.user]
            self.send('cencard', client=self.client)
            self.send(cencard, client=self.client)
            print(f'card_list: {self.user}, {card_list}')
            if self.condition != '':
                self.send(self.condition, client=self.client)
                if 'draw' in self.condition: #if prev player uses wild+4
                    cards = self.recv_data(client=self.client)
                    print(f'cards: {cards}')
                    players[self.user].extend(cards)
                    print(f'card_list: {card_list}')
            self.send('show cards', client=self.client)
            self.send('play card', client=self.client)
            try:
                card = self.recv_data(client=self.client)
                print(card)
            except pickle.UnpicklingError:
                card = self.recv_str(client=self.client) #idk why this is here. just to prevent errors ig
                print(card)
            except ConnectionResetError:
                client_list.remove(self.client)
                del players[self.user]
                del player_client_dict[self.user]
                print(f'{self.user} left the server')
                print(players)
                self.next_turn = True
                #print(f'Active connections: {threading.activeCount() - 1}')
                continue
            if 'draw' in card: #check if player draws a card
                self.send('draw 1', client=self.client)
                cards = self.recv_data(client=self.client)
                players[self.user].extend(cards) #must use .extend(), or for some reason it does not update
                self.broadcast(f'{self.user} drew a card')
                self.condition = ''
                continue
            elif 'keyerror' in card: #check if player chooses a card that doesn't exist
                self.send('keyerror', client=self.client)
                self.next_turn = False
                self.condition = ''
                continue
            else:
                a = game.check_card(card)
                #print(f'a {a}')
                if 'wild' in a:
                    wild = (a[0], '')
                    #print(f'wild {wild}')
                    card_list.remove(wild)
                    self.condition = ''
                elif 'wild4' in a:
                    wild = (a[0], '')
                    #print(f'wild4 {wild}')
                    self.condition = 'draw 4'
                    card_list.remove(wild)
                elif '+2' in a:
                    self.condition = 'draw 2'
                    card_list.remove(a)
                elif 'skip' in a:
                    self.condition = 'skip'
                    card_list.remove(a)
                elif 'reverse' in a:
                    self.condition = 'reverse'
                    card_list.remove(a)
                    self.next_turn = True
                elif a == 'invalid card':
                    self.send('invalid card', client=self.client)
                    self.next_turn = False
                    self.condition = ''
                    continue
                else:
                    #print(f'client_list: {client_list}')
                    #print(f'else card_list: {self.user}, {card_list}')
                    card_list.remove(a)
                    self.condition = ''
                    self.next_turn = True
                try:
                    self.broadcast(f'{self.user} used {" ".join(a)}')
                    self.broadcast('cencard')
                    self.broadcast(cencard)
                except ConnectionResetError:
                    #client_list.remove(self.client)
                    #del players[self.user]
                    #del player_client_dict[self.user]
                    print(f'{self.user} left the server')
                    self.broadcast(f'{self.user} left the server')
                    #print(players)
                    self.next_turn = True
                    continue
                self.send('delete', client=self.client)
                self.send(a, client=self.client)
                print(len(card_list))
                if len(card_list) == 0:
                    self.send('win', client=self.client)
                    self.broadcast(f'{self.user} won the game!')
                    self.broadcast('exit')
                    self.next_turn = False
                    break
                else:
                    self.next_turn = True
        players = {}
        return
        

s = gameServer()
s.start()




