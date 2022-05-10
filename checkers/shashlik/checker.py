#!/usr/bin/env python3

from gevent import monkey
monkey.patch_all()

from shashlik_lib import CheckMachine
from checklib import BaseChecker, Status
from checklib import rnd_username, rnd_password
from checklib import cquit
import secrets
import requests
import sys 
import urllib
import json
import base64
import random

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
        username = secrets.token_hex(4)
        password = 'Aa1' + secrets.token_hex(13)

        s = self.get_initialized_session()

        #check password complexity check
        self.mch.weak_pass(s, username, secrets.token_hex(3))
        self.mch.weak_pass(s, username, secrets.token_hex(10))
        #register
        self.mch.register(s, username, password)
        #login
        self.mch.login(s, username, password)
        #change pass
        new_pass = 'Aa1' + secrets.token_hex(13)
        self.mch.change_pass(s, username, password, new_pass)
        self.mch.login(s, username, new_pass)
        #create thread
        thread_title = secrets.token_hex(10)
        thread_body = secrets.token_hex(8) + ' ' + secrets.token_hex(3) + ' ' + secrets.token_hex(6) 
        thread_comment = secrets.token_hex(2) + ' ' + secrets.token_hex(9)
        thread_id = self.mch.create_thread(s, thread_title, thread_body, 'n')
        #post comment
        self.mch.comment(s, thread_comment, thread_id)
        #check
        self.mch.check_thread(s, thread_id, thread_body, thread_comment)
        self.cquit(Status.OK)

    def put(self, flag_id, flag, vuln):
        s = self.get_initialized_session()
        username = secrets.token_hex(4)
        password = 'Aa1' + secrets.token_hex(13)
        self.mch.register(s, username, password)
        self.mch.login(s, username, password)
        thread_title = secrets.token_hex(10)
        thread_body = flag 
        thread_id = self.mch.create_thread(s, thread_title, thread_body, 'y')
        self.cquit(Status.OK, f'{username}:{password}:{thread_id}:{flag}')

    def get(self, flag_id, flag, vuln):
        s = self.get_initialized_session()
        username, password, thread_id, flag = flag_id.split(':')
        self.mch.login(s, username, password)
        self.mch.check_thread(s, thread_id, flag, flag, status=Status.CORRUPT)
        self.cquit(Status.OK)

if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)


