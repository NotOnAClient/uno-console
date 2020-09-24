import uno
import socket
import threading
import pickle

host = '127.0.0.1'
port = 6255

username = input('Username: ')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))


player = uno.Player(username)
uno.starting_card()


print('Welcome, ' + username)

player.draw_cards(7)

def receive():
    while True:
        try:
            message = client.recv(2048).decode()
        except:
            data = client.recv(2048)
            message = pickle.loads(data) 
        if message == 'username':
            client.send(username.encode())
        elif message == 'drawn':
            player.draw_cards(1)
        else:
            print(message)

def write():
    while True:
        player.rearrange_cards(player.cards)
        #player.show_cards()
        #print(message)
        player.show_cards()
        message = player.play_card(input('Play a card: '))
        if isinstance(message, tuple):
            #print(message)
            client.send('tuple'.encode())
            data = pickle.dumps(message)
            client.send(data)
            break
        elif isinstance(message, str):
            #print(message)
            client.send('string'.encode())
            client.send(message.encode())
            break
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
#print(player.cards)
#while len(player.cards) > 0:
    #player.show_cards()
    #player.play_card(input('Play a card: '))
    #player.rearrange_cards(player.cards)
#print('No more cards left')

