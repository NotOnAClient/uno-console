import socket
import pickle
import threading
import uno

header = 50
players = {}
player_list = []
client_list = []
cencard = uno.starting_card()
FORMAT = 'ascii'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 6255))

def broadcast(msg):
    for i in client_list:
        i.send(msg)

def send(msg):
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_len = str(msg_len).encode(FORMAT)
    send_len += b' '*(header - len(send_len))
    clientsocket.send(send_len)
    clientsocket.send(message)

def recv_str():
    msg_len = clientsocket.recv(header).decode(FORMAT)
    if msg_len:
        msg_len = int(msg_len)
        msg = clientsocket.recv(msg_len).decode(FORMAT)
        return msg

def recv_tuple():
    data = clientsocket.recv(2048)
    d = pickle.loads(data)
    return d

def send_tuple(data):
    d = pickle.dumps(data)
    clientsocket.send(d)

def handle_client(clientsocket, address):
    while True:
        try:
            username = recv_str()
            d = recv_tuple()
            #client_list.append(clientsocket)
            players.update({username:d})
            #print(client_list)
            print(players)
        except ConnectionResetError:
            print(f'{username} left the server')
            client_list.remove(clientsocket)
            del players[username]
            print(players)
            break
    clientsocket.close()

def start():
    server.listen()
    while True:
        global clientsocket
        clientsocket, address = server.accept()
        print(f'Connection established wtih {address}')
        client_list.append(clientsocket)
        thread = threading.Thread(target=handle_client, args=(clientsocket, address))
        thread.start()
        print(f'Active connections: {threading.activeCount() - 1}')
        
start()
    
