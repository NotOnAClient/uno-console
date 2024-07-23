import socket
import pickle
import threading
from _thread import *
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
    if isinstance(msg, str):  # If message is a string
        msg_type = 'str'  # Indicate string type
        msg = msg.encode(FORMAT)
    else:  # Assume message is pickleable
        msg_type = 'pickle'  # Indicate pickle type
        msg = pickle.dumps(msg)

    msg_header = f"{len(msg):<{header}}{msg_type:<10}".encode(FORMAT)

    # Send header followed by the message
    client.send(msg_header + msg)

def receive(self, client_socket):
        try:
            # Read the header. It is header + 10 to account for header size, and 10 is length of data type(str, pickle).
            msg_header = client_socket.recv(header + 10).decode(FORMAT)

            # Get length and data type of message
            msg_length = int(msg_header[:header].strip())
            msg_type = msg_header[header:].strip()

            # Read the actual message
            msg = client_socket.recv(msg_length)

            if msg_type == 'str':
                str = msg.decode(FORMAT)
                print(f"{client_socket}: {str}")
                return str
            elif msg_type == 'pickle':
                pckl = pickle.loads(msg)
                print(f"{client_socket}: {pckl}")
                return pckl
            else:
                raise ValueError(f"Unknown message type: {msg_type}")
        except Exception as e:
            print(f"An error occured: {e}")
            return None

def send_info():
    cards = []
    for k,v in player.cards.items():
        cards.append(v)
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