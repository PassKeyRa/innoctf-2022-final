#!/usr/bin/env python3

from gevent import monkey
monkey.patch_all()

from tnjri_lib import CheckMachine
from checklib import BaseChecker, Status
from checklib import cquit
import secrets
import requests
import sys
import base64
import random


def json_to_b64(data):
	data = str(data).replace('\'', '"')
	data = base64.b64encode(data.encode()).decode()
	return data


class Checker(BaseChecker):
	uses_attack_data = False

	def __init__(self, *args, **kwargs):
		super(Checker, self).__init__(*args, **kwargs)
		self.mch = CheckMachine(self)

	def action(self, action, *args, **kwargs):
		try:
			super(Checker, self).action(action, *args, **kwargs)
		except requests.exceptions.ConnectionError:
			self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')

	def check(self):
		s = self.get_initialized_session()
		username = secrets.token_hex(random.randint(4, 10))
		password = secrets.token_hex(random.randint(4, 10))

		self.mch.register(s, username, password)
		id = self.mch.login(s, username, password)
		data = secrets.token_hex(random.randint(4, 10))
		key = secrets.token_hex(random.randint(4, 10))
		encypted = self.mch.encrypt(s, username, password, data, key)
		decrypted = self.mch.decrypt(s, username, password, encypted, key)
		self.assert_eq(data, decrypted, "Encryption/decryption problem", status=Status.MUMBLE)

		name = secrets.token_hex(random.randint(4, 10))
		self.mch.check_about(s, name)

		tree, encrypted_tree = self.mch.state_tree(s, username, password, id)
		self.assert_eq(encrypted_tree, encypted, "Can't get tree state", status=Status.MUMBLE)
		saved_key = self.mch.state_key(s, username, password, id)
		self.assert_eq(key, saved_key, "Can't get key state", status=Status.MUMBLE)
		self.cquit(Status.OK)

	def put(self, flag_id, flag, vuln):
		s = self.get_initialized_session()
		username = secrets.token_hex(random.randint(4, 10))
		password = secrets.token_hex(random.randint(4, 10))

		self.mch.register(s, username, password)
		key = secrets.token_hex(random.randint(4, 10))
		self.mch.encrypt(s, username, password, flag, key)
		self.cquit(Status.OK, f'{username}:{password}', '')

	def get(self, flag_id, flag, vuln):
		s = self.get_initialized_session()
		u, p = flag_id.split(':')
		id = self.mch.login(s, u, p, status=Status.CORRUPT)

		tree, encrypted = self.mch.state_tree(s, u, p, id)
		key = self.mch.state_key(s, u, p, id, Status.CORRUPT)
		decrypted = self.mch.decrypt(s, u, p, encrypted, key, status=Status.CORRUPT)
		self.assert_eq(flag, decrypted, "Can't get flag", status=Status.CORRUPT)
		self.cquit(Status.OK)


if __name__ == '__main__':
	c = Checker(sys.argv[2])

	try:
		c.action(sys.argv[1], *sys.argv[3:])
	except c.get_check_finished_exception():
		cquit(Status(c.status), c.public, c.private)
