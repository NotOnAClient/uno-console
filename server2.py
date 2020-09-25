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
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_len = str(msg_len).encode(FORMAT)
    send_len += b' '*(header - len(send_len))
    clientsocket.send(send_len)
    clientsocket.send(message)


def send_tuple(data):
    d = pickle.dumps(data)
    clientsocket.send(d)

def receive():
    message = clientsocket.recv(header).decode(FORMAT)
    print(message)
    print(type(message))
    if isinstance(message, str):
        message = int(message)
        msg = clientsocket.recv(message).decode(FORMAT)
        print(msg)
        return msg
    elif message.istuple():
        d = pickle.loads(message)
        return d

def recv_info():
    username = receive()
    d = receive()
    players.update({username: d})
    print(players)

def game():
    while game_start:
        send('game_started')


def handle_client(clientsocket, address):
    global game_start
    while True:
        try:
            message = receive()
            print(message)
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
        recv_info()
        thread = threading.Thread(target=handle_client, args=(clientsocket, address))
        thread.start()
        print(f'Active connections: {threading.activeCount() - 1}')
        if len(players) == 2:
            broadcast('Game started')
            game_start = True
            break
        
start() #reminder: stop handle thread, create specator def and thread


