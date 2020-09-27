import socket
import pickle
import uno

host = '127.0.0.1'
port = 6255
FORMAT = 'utf-8'
username = str(input('username: '))
cards = []
cencard = ()

header = 50
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

player = uno.Player(username)
player.draw_cards(7)

def send(msg):
    #a = client.recv(2048).decode(FORMAT)
    #client.send('ready'.encode())
    if type(msg) == str: #string
        msg = msg.encode(FORMAT)
        msg_header = f"{len(msg):<{header}}".encode(FORMAT)
        print(f'{msg} string')
        client.send(msg_header + msg)
    else: #pickle
        data = pickle.dumps(msg)
        data_header = f"{len(data):<{header}}".encode(FORMAT)
        client.send(data_header + data)
        print(f'{data} data')

def recv_str():
    while True:
        msg_header = client.recv(header)
        msg_len = int(msg_header.decode(FORMAT))
        msg = client.recv(msg_len).decode(FORMAT)
        return msg

def recv_data():
    while True:
        data_header = client.recv(header)
        data_len = int(data_header.decode(FORMAT))
        data = client.recv(data_len)
        d = pickle.loads(data)
        return d

def send_info():
    for k,v in player.cards.items():
        cards.append(v)
    print(cards)
    send(username)
    send(cards)


send_info()
game = recv_str()
while game == 'Game started':
    msg = recv_str()
    if msg == 'show cards':
        player.show_cards()
    if msg == 'cencard':
        cencard = recv_data()
        print(f'Centre card: {"".join(cencard)}')
    