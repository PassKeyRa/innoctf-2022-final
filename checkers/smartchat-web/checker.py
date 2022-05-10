#!/usr/bin/env python3

from gevent import monkey
monkey.patch_all()

from smartchatweb_lib import CheckMachine
from checklib import BaseChecker, Status
from checklib import cquit
import secrets
import requests
import sys 
import urllib


class Checker(BaseChecker):
    uses_attack_data = False
    vulns = 1

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')

    def check(self):
        username = secrets.token_hex(10)
        password = secrets.token_hex(10)
        roomname1 = secrets.token_hex(10)
        mes1 = secrets.token_hex(10)
        mes2 = secrets.token_hex(10)

        s = self.get_initialized_session()
        self.mch.register(s, username, password)
        self.mch.login(s, username, password)
        self.mch.create_room(s, roomname1)
        self.mch.get_rooms(s, [roomname1])
        self.mch.send_message(s, roomname1, mes1)
        self.mch.get_messages(s, roomname1, [mes1])
        self.mch.check_online(s, username)
        self.cquit(Status.OK)

    def put(self, flag_id, flag, vuln):
        s = self.get_initialized_session()
        username = secrets.token_hex(10)
        password = secrets.token_hex(10)
        roomname = secrets.token_hex(10)
        self.mch.register(s, username, password)
        self.mch.login(s, username, password)
        self.mch.create_room(s, roomname)
        self.mch.send_message(s, roomname, flag)
        self.cquit(Status.OK, f'{username}:{password}:{roomname}:{flag}')

    def get(self, flag_id, flag, vuln):
        s = self.get_initialized_session()
        username, password, roomname, mes = flag_id.split(':')
        self.mch.login(s, username, password)
        self.mch.get_messages(s, roomname, [mes], Status.CORRUPT)
        self.cquit(Status.OK)

if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)

