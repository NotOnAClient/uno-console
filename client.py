import socket
import pickle
import uno

server_settings = []


with open('client_settings.txt', 'r') as settings:
    for i in settings.readlines():
        i = i.rstrip('\n')
        p = i.split('=')
        print(p)
        server_settings.append(p[1])

host = server_settings[0]
port = int(server_settings[1])

FORMAT = 'utf-8'
username = str(input('Username: '))

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
        #print(f'send: {msg} string')
        client.send(msg_header + msg)
    else: #pickle
        data = pickle.dumps(msg)
        data_header = f"{len(data):<{header}}".encode(FORMAT)
        #print('header sent data')
        client.send(data_header + data)
        #print(f'{data} data')

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
        #print(d)
        return d

def send_info():
    cards = []
    for k,v in player.cards.items():
        cards.append(v)
    #print(cards)
    send(username)
    send(cards)

def recv_game_msg():
    #global num
    msg = recv_str()
    #num = int()
    if msg:
        if msg == 'cencard':
            global cencard
            cencard = recv_data()
            print(f'Centre card: {" ".join(cencard)}', end='')
            msg = ''
        if msg == 'show cards':
            player.rearrange_cards(player.cards)
            player.show_cards()
            msg = ''
            #break
        if msg == 'play card':
            global num #this line is needed for 'delete'
            card, num = player.play_card()
            #card = player.num_to_card(num)
            #print(card)
            #print(f'play num {num}')
            send(card)
            #msg = ''
        if msg == 'delete':
            card = recv_data()
            #print(f'wild {wild}')
            del player.cards[int(num)]
            #print(player.cards)
            msg = ''
            #break
        if 'draw' in msg:
            #msg = msg.strip()
            #print(f'draw {msg}')
            cards = player.draw_cards(int(msg[-1]))
            #print(f'drawn_cards: {cards}')
            send(cards)
            #print(player.cards)
            #send('drawn')
            msg = ''
            #break
        if msg == 'invalid card':
            print('Card cannot be used')
            msg = ''
            #break
        if msg == 'keyerror':
            print('Card not found')
            msg = ''
            #break
        if msg == 'win':
            print('You won the game!')
            input('Press Enter to exit.')
            exit()
            #break
        if msg == 'exit':
            input('Press Enter to exit.')
            exit()
        else:
            #print('---------------------------------------')
            print(msg) #print out what is going on in the game
            #print('---------------------------------------')
            msg = ''
            #break

send_info()
game = recv_str()
while game == 'Game started':
    recv_game_msg()
    #if a:
        #send(a)