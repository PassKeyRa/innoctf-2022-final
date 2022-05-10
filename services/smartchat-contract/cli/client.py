import web3
import sys
import re
from lib import SmartChat

def bytesToHex(b):
    return '0x' + ''.join(hex(i)[2:].zfill(2) for i in b)

def hexToBytes(h):
    return bytes([int(h[i:i+2], 16) for i in range(2, len(h), 2)])

class Client:
    room = None
    key = None
    def __init__(self, key, contract_address):
        w3 = web3.Web3()
        w3.eth.account.enable_unaudited_hdwallet_features()
        self.account = w3.eth.account.from_key(key)
        self.smartchat = SmartChat(contract_address, self.account)

    def __check_room(func):
        def wrapper(self, *args, **kwargs):
            if not self.room:
                print('[ERROR] Choose the room first')
                return False
            return func(self, *args, **kwargs)
        return wrapper
    
    def __check_error(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                print('Something went wrong')
                print(e)
        return wrapper

    @__check_room
    @__check_error
    def getRoomData(self):
        address, members = self.smartchat.getRoomData(self.room)
        if address == False:
            print(f'[ERROR] {members}')
            return False
        print(f'Address {address}, members: {members}')

    @__check_error
    def createRoom(self):
        name = None
        while not name:
            n = input('Enter the room name: ')
            if not n:
                print('Wrong input, try again')
                continue
            name = n
        room, key = self.smartchat.createRoom(name)
        if room == False:
            print(f'[ERROR] {key}')
            return False
        self.room = name
        self.key = key
        key = bytesToHex(key)
        print(f'New room {name} created with key {key}')
        return True

    @__check_room
    @__check_error
    def addRoomMember(self):
        member = None
        while not member:
            m = input('Enter the member address: ')
            if not re.match('0x[a-fA-F0-9]{40}', m):
                print('Wrong address, try again')
                continue
            member = m
        ret = self.smartchat.addRoomMember(member)
        if type(ret) == tuple:
            _, err = ret
            print(f'[ERROR] {err}')
            return False
        print(f'The user {member} successfully added to the room {self.room}')

    @__check_room
    @__check_error
    def newMessage(self):
        text = None
        while not text:
            t = input('Enter the text: ')
            if not t:
                print('Wrong input, try again')
                continue
            text = t
        ret = self.smartchat.newMessage(self.key, text)
        if type(ret) == tuple:
            _, err = ret
            print(f'[ERROR] {err}')
            return False
        print('Message sent')

    @__check_room
    @__check_error
    def listMessages(self):
        ret = self.smartchat.listMessages(self.key)
        if type(ret) == tuple:
            _, err = ret
            print(f'[ERROR] {err}')
            return False
        print('Messages:')
        print(ret)
        
    @__check_error
    def setRoom(self):
        room = None
        key = None
        while not room:
            inp = input('Enter the room name: ')
            if not inp:
                print('Wrong name!')
                continue
            room = inp
        while not key:
            inp = input('Enter the key: ')
            if not inp or not re.match('0x[0-9a-fA-F]+', inp):
                print('Wrong key!')
                continue
            key = inp
        self.room = room
        self.key = hexToBytes(key)
        self.smartchat.changeRoom(room)
        print('Done')

    @__check_room
    @__check_error
    def newAlgorithm(self):
        ret = self.smartchat.newAlgorithm()
        if type(ret) == tuple:
            _, err = ret
            print(f'[ERROR] {err}')
            return False
        print('Algorithm changed successfully')
    
    @__check_room
    @__check_error
    def deleteMessage(self):
        id_ = None
        while id_ == None:
            try:
                i = int(input('Enter the message id: '))
            except Exception as e:
                print(e)
                print('Wrong id, try again')
                continue
            if i < 0:
                print('Wrong id, try again')
                continue
            id_ = i
        ret = self.smartchat.deleteMessage(id_)
        if type(ret) == tuple:
            _, err = ret
            print(f'[ERROR] {err}')
            return False
        print('Message deleted')

    def countMessages(self):
        ret = self.smartchat.countMessages()
        print(ret)
    
    def exit(self):
        print('Exiting...')
        exit(0)

    def print_menu(self):
        print('''1. Create new room
2. Choose a room
3. Add member to the room
4. Get the room info
5. Send a message
6. Fetch messages
7. Delete a message
8. Generate a new algorithm for the room
9. Exit
''')

    def start(self):
        print('Welcome to the CLI client for SmartChat')
        while True:
            try:
                self.print_menu()
                option = None
                options = [self.createRoom, 
                            self.setRoom, 
                            self.addRoomMember, 
                            self.getRoomData, 
                            self.newMessage, 
                            self.listMessages, 
                            self.deleteMessage,
                            self.newAlgorithm,
                            self.exit]
                while not option:
                    try:
                        opt = int(input('Enter the option number: '))
                    except:
                        print('No such option, try again')
                        continue
                    if not (opt > 0 and opt <= len(options)):
                        print('No such option, try again')
                        continue
                    option = opt
                options[option-1]()
            except KeyboardInterrupt:
                print('\nEnter 9 option to exit')

if len(sys.argv) != 2:
    print('Usage:\n\npython3 client.py <smartchat address>')
    exit(1)

contract = sys.argv[1]

with open('.secret', 'r') as f:
    key = f.read().strip()
c = Client(key, contract)
c.start()
