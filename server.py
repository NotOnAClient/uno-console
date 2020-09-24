import socket
import threading
import uno
import pickle

host = '127.0.0.1'
port = 6255

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket, using TCP
server.bind((host, port)) #give the socket an IP address and port
server.listen(4) #Listen to possible connections, arg=max connections
print('Listening...')
game_started = False
clients = []
usernames = []
cencard = uno.starting_card()
print(cencard)
def broadcast(message):
    for i in clients:
        i.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(2048)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} left the chat'.encode())
            usernames.remove(username)
            break

def receive():
    global game_started
    while game_started == False:
        global username
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        #get client usernames and IPs and append to lists
        client.send('username'.encode())
        username = client.recv(2048).decode()
        usernames.append(username)
        clients.append(client)
        print(f'{username} joined the server')
        broadcast(f'{username} joined the server'.encode())
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
        if len(clients) >= 1:
            print('game started')
            game_started += True
            thread.join()

def game():
    while game_started:
        client, address = server.accept()
        data = client.recv(2048).decode()
        if data == 'string':
            card = client.recv(2048).decode()
            if card == 'draw':
                client.send('drawn'.encode())
                print(f'{username} drew a card')
                
        elif data == 'tuple':
            card = client.recv(2048)
            card = pickle.loads(card)
            print(card)
        

#broadcast(f'Centre card: {cencard}')
receive()
game_thread = threading.Thread(target=game)
game_thread.start()