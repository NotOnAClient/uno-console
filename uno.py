from random import choice
colours = ['red', 'blue', 'green', 'yellow', 'wild', 'wild4']
number = [0,1,2,3,4,5,6,7,8,9,'skip','reverse']
cencard = []
def random_card():
        num = choice(number)
        col = choice(colours)
        if col == 'wild' or col == 'wild4':
            t = (col, '')
        else:
            t = (col, str(num))
        return t

def starting_card():
        num = choice(number[0:9])
        col = choice(colours[0:3])
        cencard.append(col)
        cencard.append(str(num))
        return cencard
        
class Player:
    def __init__(self, username):
        self.username = username
        self.cards = {}
        self.turn = False

    def play_card(self):
        self.rearrange_cards(self.cards)
        self.turn = True
        num = int()
        while True:
            lst = []
            card = input('Play a card: ')
            num = card
            #print(num)
            card = str(card)
            list_card = list(card.split())
            if list_card[0] == 'draw':
                #self.cards[len(self.cards)+1] = random_card()
                print('You drew a card')
                lst.append(('draw', ''))
                lst.append(None)
                return lst
            elif card.isnumeric():
                #card = Game(self).check_card(card)
                #print(card)
                card = self.num_to_card(card)
                if card[0] == 'wild':
                    colours = {1:'red', 2:'blue', 3:'green', 4:'yellow'}
                    for k, v in colours.items():
                        print(str(k) + ': ' + v)
                    col = input('Select a colour: ')
                    if col.isnumeric() == False:
                        print('Please input a number')
                        continue
                    else:
                        print('You selected ' + colours[int(col)])
                        output = ('wild', colours[int(col)])
                        for i in reversed(cencard): cencard.remove(i)
                        cencard_new = [cencard.append(i) for i in output]
                        lst.append(output)
                        lst.append(num)
                        return lst

                elif card[0] == 'wild4':
                    colours = {1:'red', 2:'blue', 3:'green', 4:'yellow'}
                    for k, v in colours.items():
                        print(str(k) + ': ' + v)
                    col = input('Select a colour: ')
                    if col.isnumeric() == False:
                        print('Please input a number')
                        continue
                    else:
                        print('You selected ' + colours[int(col)])
                        output = ('wild4', colours[int(col)])
                        for i in reversed(cencard): cencard.remove(i)
                        cencard_new = [cencard.append(i) for i in output]
                        lst.append(output)
                        lst.append(num)
                        return lst
                elif card == 'card not found':
                    print('Card not found')
                    output = 'keyerror'
                    lst.append((output,''))
                    lst.append(num)
                    #print(f'card not found: {lst}')
                    return lst
                else:
                    lst.append(card)
                    lst.append(num)
                    return lst
                
            else:
                print('Please input a number')
                continue
            self.turn = False
            #self.rearrange_cards(self.cards)
            

    def show_cards(self):
        print('=======================================')
        print('Your cards' + '(' + str(len(self.cards)) + ')' + ':') #shows player cards
        for index, i in self.cards.items():
            print(str(index) + ': ' + i[0], i[1])
        print('=======================================')
        
    def draw_cards(self, number):
        self.rearrange_cards(self.cards)
        card_list = []
        for i in range(number):
            card = random_card()
            card_list.append(card)
            self.cards.update({len(self.cards)+1: card})
            #print(f'draw_card: {card} added')
        return card_list

    def rearrange_cards(self, cards):
        count = 1
        new_dict = {}
        for k,v in cards.items():
            new_dict.update({count:v})
            count+=1
        self.cards = new_dict

    def num_to_card(self, num):
        num = int(num)
        try:
            card = self.cards[num]
        except KeyError:
            return 'card not found'
        #print(card)
        return card

class Game():
    #def __init__(self, player_class):
        #self.cencard = []
        #self.players = []
        #self.cards = player_class.cards
    
    def check_card(self, card):
        #card = str(card)
        #tuple_card = tuple(card.split())
        #list_card = list(card.split())
        
        while True:
            if card[0] == 'wild' or card[0] == 'wild4':
                output = card
                print('You used ' + str(output))
                for i in reversed(cencard): cencard.remove(i)
                cencard_new = [cencard.append(i) for i in card]
                return output
            
            elif card[0] not in cencard and card[1] != cencard[1]:
                print('Card cannot be used')
                return 'invalid card'
            

            else:
                output = card
                print('You used ' + str(output))
                for i in reversed(cencard): cencard.remove(i)
                cencard_new = [cencard.append(i) for i in card]
                #del self.cards[card]
                return output
                
        #except KeyError:
            #print('Card not found')
            #break