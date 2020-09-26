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
    for i in client_list:
        i.send(msg.encode())

def send(msg):
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
    full_msg = ''
    new_msg = True
    clientsocket.send('ready'.encode(FORMAT))
    while True:
        message = clientsocket.recv(header)
        if new_msg:
            print(f'message len: {message[:header]}')
            msglen = int(message[:header])
            new_msg = False
        print(msglen)
        full_msg += message.decode(FORMAT)
        if len(full_msg) - header == msglen:
            print('full msg recvd')
            print(full_msg[header:])
            new_msg = True
            #full_msg = ''
            return full_msg[header:]

def recv_data():
    full_msg = b''
    new_msg = True
    clientsocket.send('ready'.encode(FORMAT))
    while True:
        message = clientsocket.recv(header)
        if new_msg:
            print(f'message len: {message[:header]}')
            msglen = int(message[:header])
            new_msg = False
        print(msglen)
        full_msg += message
        if len(full_msg) - header == msglen:
            print('full msg recvd')
            print(full_msg[header:])
            data = pickle.loads(full_msg[header:])
            print(data)
            new_msg = True
            full_msg = b''
            return data

def recv_info():
    username = recv_str()
    d = recv_data()
    players.update({username: d})
    print(players)
    return username

def game():
    while game_start:
        send('game_started')


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
        thread = threading.Thread(target=handle_client, args=(clientsocket, address, username))
        thread.start()
        print(f'Active connections: {threading.activeCount() - 1}')
        if len(players) == 2:
            broadcast('Game started')
            game_start = True
            break
        
start() #reminder: stop handle thread, create specator def and thread


