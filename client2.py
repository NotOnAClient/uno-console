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
    try:
        message = msg.encode(FORMAT)
        msg_len = len(message)
        send_len = str(msg_len).encode(FORMAT)
        send_len += b' '*(header - len(send_len))
        print(send_len)
        print(message)
        client.send(send_len)
        client.send(message)
    except:
        msg_len = len(msg)
        send_len = str(msg_len).encode(FORMAT)
        send_len += b' '*(header - len(send_len))
        print(send_len)
        print(msg)
        client.send(send_len)
        client.send(msg)

def receive():
    msg_len = client.recv(header).decode(FORMAT)
    if msg_len:
        msg_len = int(msg_len)
        msg = client.recv(msg_len).decode(FORMAT)
        return msg

def send_info():
    for k,v in player.cards.items():
        cards.append(v)
    print(cards)
    send(username)
    d = pickle.dumps(cards)
    send(d)


send_info()
#while True:
    #game = receive()
    #print(game)
    #cencard = recv_tuple()
    #print(f'Centre card: {" ".join(cencard)}')
    #player.show_cards()
    #player.play_card(input('Play a card: '))