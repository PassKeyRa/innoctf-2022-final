#!/usr/bin/env python3

from gevent import monkey
monkey.patch_all()

from lib import SmartChat
from checklib import BaseChecker, Status
from checklib import cquit
import secrets
import sys
import random
import requests
import web3
import os

from web3.middleware import geth_poa_middleware

PORT = 8001

def bytesToHex(b):
	return '0x' + ''.join(hex(i)[2:].zfill(2) for i in b)

def hexToBytes(h):
	return bytes([int(h[i:i+2], 16) for i in range(2, len(h), 2)])

class Checker(BaseChecker):
	uses_attack_data = False

	def __init__(self, *args, **kwargs):
		super(Checker, self).__init__(*args, **kwargs)
		self.url_api = 'http://'+self.host+':'+str(PORT)+'/contract'
		self.accounts = []
		self.w3 = web3.Web3()
		self.w3.eth.account.enable_unaudited_hdwallet_features()
		self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
		with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.wallets'), 'r') as f:
			for line in f:
				l = line.strip()
				if l:
					l = line.split(' ')
					key = l[1][2:].strip()
					self.accounts.append(self.w3.eth.account.from_key(key))
		self.account_boss = None
		with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.wallet_boss'), 'r') as f:
			key = f.read().strip()
			if key:
				key = key.split(' ')[1][2:].strip()
				self.account_boss = self.w3.eth.account.from_key(key)
		self.cryptonomicon = ''
		with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Cryptonomicon.txt'), 'r') as f:
			self.cryptonomicon = f.read()

	def action(self, action, *args, **kwargs):
		try:
			super(Checker, self).action(action, *args, **kwargs)
		except requests.exceptions.ConnectionError:
			self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')

	def random_cryptonomicon(self, n):
		position = random.randint(0, len(self.cryptonomicon))
		return self.cryptonomicon[position:position+n]

	def check(self):
		s = self.get_initialized_session()
		contract_addr = s.get(self.url_api).text.strip()
		account = self.accounts[random.randint(0, len(self.accounts)-1)]
		smartchat = SmartChat(contract_addr, account)
		smartchat_boss = SmartChat(contract_addr, self.account_boss)

		room_name = secrets.token_hex(random.randint(10, 15))
		room, key = smartchat.createRoom(room_name)
		rand_addr = self.w3.toChecksumAddress('0x' + secrets.token_hex(20))
		self.assert_eq(smartchat.addRoomMember(rand_addr), True, "The member wasn't added", status=Status.MUMBLE)
		room_, members = smartchat.getRoomData(room_name)
		self.assert_eq(members, [account.address, rand_addr], "Wrong members mechanizm", status=Status.MUMBLE)
		smartchat_boss.changeRoom(room_name)

		m = self.random_cryptonomicon(random.randint(20, 50))
		self.assert_eq(smartchat.newMessage(key, m), True, "The message wasn't added", status=Status.MUMBLE)
		
		self.assert_eq(smartchat.newAlgorithm(), True, "Cannot change algorithm", status=Status.MUMBLE)
		m1 = self.random_cryptonomicon(random.randint(20, 50))
		self.assert_eq(smartchat.newMessage(key, m1), True, "The message1 wasn't added", status=Status.MUMBLE)

		messages = smartchat.listMessages(key)
		self.assert_in({'sender':account.address, 'data':m}, messages, "The message is not in messages", status=Status.MUMBLE)
		self.assert_in({'sender':account.address, 'data':m1}, messages, "The message1 is not in messages", status=Status.MUMBLE)

		#self.assert_eq(smartchat_boss.deleteMessage(0), True, "Cannot delete message", status=Status.MUMBLE)
		#messages = smartchat.listMessages(key)
		#self.assert_nin({'sender':account.address, 'data':m}, messages, "The message wasn't deleted", status=Status.MUMBLE)

		self.assert_eq(smartchat.changeAlgorithmForRoom('INTERNAL1', room_name), True, "Cannot change algorithm for room", status=Status.MUMBLE)
		self.assert_eq(smartchat.getRoomAlgorithm(), 'INTERNAL1', "Got wrong algorithm", status=Status.MUMBLE)
		self.assert_eq(smartchat.isBoss(account.address), False, "Usual user is boss", status=Status.MUMBLE)
		self.assert_eq(smartchat.isBoss(self.account_boss.address), True, "Boss is not a boss", status=Status.MUMBLE)

		self.cquit(Status.OK)

	def put(self, flag_id, flag, vuln):
		s = self.get_initialized_session()
		contract_addr = s.get(self.url_api).text.strip()
		account = self.accounts[random.randint(0, len(self.accounts)-1)]
		smartchat = SmartChat(contract_addr, account)

		room_name = secrets.token_hex(random.randint(10, 15))
		room, key = smartchat.createRoom(room_name)

		for _ in range(random.randint(0, 3)):
			smartchat.newAlgorithm()

		smartchat.newMessage(key, flag)
		k = bytesToHex(key)

		self.cquit(Status.OK, f'{account.address}:{room_name}:{k}', '')

	def get(self, flag_id, flag, vuln):
		s = self.get_initialized_session()
		a, r, k = flag_id.split(':')

		account = None
		for i in self.accounts:
			if i.address == a:
				account = i
				break

		k = hexToBytes(k)

		s = self.get_initialized_session()
		contract_addr = s.get(self.url_api).text.strip()
		smartchat = SmartChat(contract_addr, account)

		smartchat.changeRoom(r)
		messages = smartchat.listMessages(k)
		self.assert_in({'sender':a, 'data':flag}, messages, "No flag in messages", status=Status.CORRUPT)
		self.cquit(Status.OK)


if __name__ == '__main__':
	c = Checker(sys.argv[2])

	try:
		c.action(sys.argv[1], *sys.argv[3:])
	except c.get_check_finished_exception():
		cquit(Status(c.status), c.public, c.private)
