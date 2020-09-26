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
    a = client.recv(2048).decode(FORMAT)
    if a == 'ready':
        if type(msg) == str: #string
            msg = f"{len(msg):<{header}}" + msg
            print(f'{msg} string')
            client.send(msg.encode(FORMAT))
        else: #pickle
            data = pickle.dumps(msg)
            data = f"{len(data):<{header}}".encode(FORMAT) + data
            client.send(data)
            print(f'{data} data')

def recv_str():
    full_msg = ''
    new_msg = True
    client.send('ready'.encode(FORMAT))
    while True:
        message = client.recv(header)
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
            full_msg = ''
            return full_msg

def recv_data():
    full_msg = b''
    new_msg = True
    client.send('ready'.encode(FORMAT))
    while True:
        message = client.recv(header)
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

def send_info():
    for k,v in player.cards.items():
        cards.append(v)
    print(cards)
    send(username)
    send(cards)


send_info()
#while True:
    #game = receive()
    #print(game)
    #cencard = recv_tuple()
    #print(f'Centre card: {" ".join(cencard)}')
    #player.show_cards()
    #player.play_card(input('Play a card: '))