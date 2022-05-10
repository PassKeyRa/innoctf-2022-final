# The lib is used by checker also

import web3
import time
from abi import abi_smartchat, abi_roomchat
from Crypto.Cipher import AES, DES
from Crypto.Cipher import DES
from web3.middleware import geth_poa_middleware


class SmartChat:
    roomchat = None
    def __init__(self, contract_address, account):
        self.w3 = web3.Web3(web3.HTTPProvider('http://10.10.10.13:8545'))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.smartchat = self.w3.eth.contract(address=contract_address, abi=abi_smartchat)
        self.account = self.w3.eth.account.from_key(account.key)
        self.w3.eth.defaultAccount = self.account.address

    def __check_room(func):
        def wrapper(self, *args, **kwargs):
            if self.roomchat:
                return func(self, *args, **kwargs)
            else:
                return False
        return wrapper

    def __genKey(self):
        return self.smartchat.functions.gen_key().call()

    def __getRoom(self, name):
        return self.smartchat.functions.getRoomByName(name).call()

    @__check_room
    def __newRoomMessage(self, data):
        tx_hash = self.roomchat.functions.newMessage(data).transact()
        self.w3.eth.waitForTransactionReceipt(tx_hash)
        messages = self.__listMessages()
        if not messages:
            return False
        messages = [d for s,d in messages]
        if data not in messages:
            return False
        return True

    @__check_room
    def __getAlgorithm(self):
        return self.roomchat.functions.algorithm().call()

    @__check_room
    def __changeAlgorithm(self, algo):
        tx_hash = self.roomchat.functions.changeAlgorithm(algo).transact()
        self.w3.eth.waitForTransactionReceipt(tx_hash)
        return True

    @__check_room
    def __listMessages(self):
        return self.roomchat.functions.getMessages().call()

    def __encrypt1(self, data, key):
        key = key[:16]
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, _ = cipher.encrypt_and_digest(data.encode())
        enc = nonce + ciphertext
        return enc

    def __decrypt1(self, data, key):
        key = key[:16]
        nonce = data[:16]
        ciphertext = data[16:]
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        return plaintext.decode()

    def __encrypt2(self, data, key):
        key = key[:8]
        cipher = DES.new(key, DES.MODE_OFB)
        iv = cipher.iv
        ciphertext = cipher.encrypt(data.encode())
        enc = iv + ciphertext
        return enc

    def __decrypt2(self, data, key):
        key = key[:8]
        iv = data[:8]
        ciphertext = data[8:]
        cipher = DES.new(key, DES.MODE_OFB, iv=iv)
        plaintext = cipher.decrypt(ciphertext)
        return plaintext.decode()

    @__check_room
    def __encryptExternal(self, data, key):
        data = data.encode()
        return self.roomchat.functions.encrypt(data, key).call()

    @__check_room
    def __decryptExternal(self, data, key):
        return str(self.roomchat.functions.decrypt(data, key).call())

    def __encryptUnknown(self, data, key):
        key = key[:8]
        data = data.encode()
        encrypted = b''
        for i in range(len(data)):
            encrypted += bytes([data[i] ^ key[i % len(key)]])
        return encrypted

    def __decryptUnknown(self, data, key):
        key = key[:8]
        decrypted = ''
        for i in range(len(data)):
            decrypted += chr(data[i] ^ key[i % len(key)])
        return decrypted

    @__check_room
    def __listMembers(self):
        return self.roomchat.functions.listMembers().call()

    @__check_room
    def __deleteMessage(self, id_):
        tx_hash = self.roomchat.functions.deleteMessage(id_).transact()
        self.w3.eth.waitForTransactionReceipt(tx_hash)
        return True


    def createRoom(self, name):
        tx_hash = self.smartchat.functions.createRoom(name).transact()
        self.w3.eth.waitForTransactionReceipt(tx_hash)
        key = self.__genKey()
        time.sleep(4)
        room = self.__getRoom(name)
        if room == '0x0000000000000000000000000000000000000000':
            return False, 'Cannot get room'
        self.changeRoom(name)
        return room, key

    def changeRoom(self, name):
        room = self.__getRoom(name)
        self.roomchat = self.w3.eth.contract(address=room, abi=abi_roomchat)

    @__check_room
    def addRoomMember(self, member):
        tx_hash = self.roomchat.functions.addMember(member).transact()
        self.w3.eth.waitForTransactionReceipt(tx_hash)
        members = self.__listMembers()
        if member in members:
            return True

    def newMessage(self, key, text: str):
        algo = self.__getAlgorithm()
        if algo == False:
            return False, 'Cannot get algorithm'
        
        num_of_messages = self.__listMessages()
        if num_of_messages == False:
            return False, 'Cannot get messages'
        num_of_messages = len(num_of_messages)

        text = str(num_of_messages) + ' ' + text

        data = None
        if algo == 'INTERNAL1':
            data = self.__encrypt1(text, key)
        elif algo == 'INTERNAL2':
            data = self.__encrypt2(text, key)
        elif algo == 'EXTERNAL':
            data = self.__encryptExternal(text, key)
        else:
            data = self.__encryptExternal(text, key)

        if self.__newRoomMessage(data):
            return True
        return False, 'The message wasn\'t added'

    def getRoomData(self, room):
        address = self.__getRoom(room)
        if address == '0x0000000000000000000000000000000000000000':
            return False, 'No such room'

        members = self.__listMembers()
        if members == False:
            return False, 'Cannot list members'

        return address, members

    def newAlgorithm(self):
        algorithms = ['INTERNAL1', 'INTERNAL2', 'EXTERNAL']
        algo = self.__getAlgorithm()
        if algo not in algorithms:
            return True
        new_algo = algorithms[(algorithms.index(algo)+1) % len(algorithms)]
        if self.__changeAlgorithm(new_algo):
            return True
        algo = self.__getAlgorithm()
        if algo == new_algo:
            return True
        return False, 'Cannot change algorithm'

    def getRoomAlgorithm(self):
        return self.__getAlgorithm()


    def listMessages(self, key):
        messages = self.__listMessages()
        if messages == False:
            return messages, 'Cannot list messages'
        m = []
        for s,d in messages:
            if s == '0x0000000000000000000000000000000000000000':
                continue
            
            decryption_functions = [self.__decrypt1, self.__decrypt2, self.__decryptExternal, self.__decryptUnknown]
            decrypted = None
            for f in decryption_functions:
                try:
                    dec = f(d, key).split(' ')
                    if int(dec[0]) >= 0:
                        decrypted = ' '.join(dec[1:])
                        break
                except:
                    continue
            if decrypted:
                m.append({'sender':s, 'data':decrypted})
        return m

    def deleteMessage(self, id_):
        if self.__deleteMessage(id_):
            return True
        return False, 'Cannot delete the message. Probably, you are not boss'

    @__check_room
    def countMessages(self):
        return self.roomchat.functions.countMessages().call()

    @__check_room
    def isBoss(self, addr):
        return self.smartchat.functions.isBossAddress(addr).call()

    def changeAlgorithmForRoom(self, algorithm, room):
        tx_hash = self.smartchat.functions.changeAlgorithmForRoom(algorithm, room).transact()
        self.w3.eth.waitForTransactionReceipt(tx_hash)
        return True
