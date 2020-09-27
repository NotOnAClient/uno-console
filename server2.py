import socket
import pickle
import threading
import uno

header = 50
players = {}
player_list = []
client_list = []
cencard = uno.starting_card()
game_start = False
FORMAT = 'utf-8'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 6255))

def broadcast(msg):
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

def send(msg):
    clientsocket.send('ready'.encode())
    a = clientsocket.recv(2048).decode(FORMAT)
    if a == 'ready':
        if type(msg) == str: #string
            msg = f"{len(msg):<{header}}" + msg
            print(f'{msg} string')
            clientsocket.send(msg.encode(FORMAT))
        else: #pickle
            data = pickle.dumps(msg)
            data = f"{len(data):<{header}}".encode(FORMAT) + data
            clientsocket.send(data)
            print(f'{data} data')


def recv_str():
    #a = clientsocket.recv(2048).decode(FORMAT)
    #clientsocket.send('ready'.encode(FORMAT))
    while True:
        msg_header = clientsocket.recv(header)
        msg_len = int(msg_header.decode(FORMAT))
        msg = clientsocket.recv(msg_len).decode(FORMAT)
        return msg

def recv_data():
    while True:
        data_header = clientsocket.recv(header)
        data_len = int(data_header.decode(FORMAT))
        data = clientsocket.recv(data_len)
        d = pickle.loads(data)
        return d

def recv_info():
    username = recv_str()
    d = recv_data()
    players.update({username: d})
    print(players)
    return username


def handle_client(clientsocket, address, username):
    global game_start
    while True:
        try:
            message = recv_str()
            print(message)
            continue
        except ConnectionResetError:
            print(f'{username} left the server')
            client_list.remove(clientsocket)
            del players[username]
            print(players)
            print(f'Active connections: {threading.activeCount() - 1}')
            break
    clientsocket.close()

def start():
    server.listen()
    while True:
        global clientsocket
        clientsocket, address = server.accept()
        print(f'Connection established wtih {address}')
        client_list.append(clientsocket)
        username = recv_info() #calling this username because i just wanted to get the username
        #thread = threading.Thread(target=handle_client, args=(clientsocket, address, username))
        #thread.start()
        #print(f'Active connections: {threading.activeCount() - 1}')
        while len(players) == 2:
            global game_start
            broadcast('Game started')
            game_start = True
            game()
            
        
def game():
    broadcast('cencard')
    broadcast(cencard)
    broadcast('show cards')

start()


