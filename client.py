import socket
import pickle
import threading
from _thread import *
import uno

server_settings = []
FORMAT = 'utf-8'
header = 50

class Client:
    def __init__(self):
        with open('client_settings.txt', 'r') as settings:
            for i in settings.readlines():
                i = i.rstrip('\n')
                p = i.split('=')
                print(p)
                server_settings.append(p[1])

        self.host = server_settings[0]
        self.port = int(server_settings[1])

        
        self.username = str(input('Username: '))

        self.cencard = ()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

    def send(self, msg):
        if isinstance(msg, str):  # If message is a string
            msg_type = 'str'  # Indicate string type
            msg = msg.encode(FORMAT)
        else:  # Assume message is pickleable
            msg_type = 'pickle'  # Indicate pickle type
            msg = pickle.dumps(msg)

        msg_header = f"{len(msg):<{header}}{msg_type:<10}".encode(FORMAT)

        # Send header followed by the message
        self.client.send(msg_header + msg)

    def receive(self):
        try:
            # Read the header. It is header + 10 to account for header size, and 10 is length of data type(str, pickle).
            msg_header = self.client.recv(header + 10).decode(FORMAT)

            # Get length and data type of message
            msg_length = int(msg_header[:header].strip())
            msg_type = msg_header[header:].strip()

            # Read the actual message
            msg = self.client.recv(msg_length)

            if msg_type == 'str':
                str = msg.decode(FORMAT)
                print(f"{self.client}: {str}")
                return str
            elif msg_type == 'pickle':
                pckl = pickle.loads(msg)
                print(f"{self.client}: {pckl}")
                return pckl
            else:
                raise ValueError(f"Unknown message type: {msg_type}")
        except Exception as e:
            print(f"An error occured: {e}")
            return None

    def recv_game_msg(self):
        #global num
        msg = self.receive()
        #num = int()
        if msg:
            if msg == 'cencard':
                global cencard
                cencard = self.receive()
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
                self.send(card)
                #msg = ''
            if msg == 'delete':
                card = self.receive()
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
                self.send(cards)
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
