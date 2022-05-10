from checklib import Status
import requests
import re
import base64
import urllib
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).absolute().resolve().parent

PORT = 80
MAX_FILESIZE = 1024

class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{self.port}'

    def __init__(self, checker):
        self.c = checker
        self.port = PORT

    def weak_pass(self, session, username, password, status=Status.MUMBLE):
        csrf = BeautifulSoup(session.get(self.url + '/register').content, 'lxml').find('input', {'name': 'csrf_token'})['value']
        r = session.post(self.url + '/register', data={'csrf_token': csrf,
            'username': username,
            'password': base64.b64encode(password.encode()),
            'password2': base64.b64encode(password.encode()),
            'submit': 'Register'})
        check = (b'[Password too weak.]' in r.content) and (r.status_code == 200)
        self.c.assert_eq(check, True, "Password complexity check not working", status=status)

    def register(self, session, username, password, status=Status.MUMBLE):
        csrf = BeautifulSoup(session.get(self.url + '/register').content, 'lxml').find('input', {'name': 'csrf_token'})['value']
        r = session.post(self.url + '/register', data={'csrf_token': csrf,
            'username': username,
            'password': base64.b64encode(password.encode()),
            'password2': base64.b64encode(password.encode()),
            'submit': 'Register'})
        check = (b'[Please use a different username.]' not in r.content) and (r.status_code == 200)
        self.c.assert_eq(check, True, "Can't register", status=status)

    def login(self, session, username, password, status=Status.MUMBLE):
        csrf = BeautifulSoup(session.get(self.url + '/login').content, 'lxml').find('input', {'name': 'csrf_token'})['value']
        r = session.post(self.url + '/login', data={'csrf_token': csrf,
            'username': username,
            'password': password,
            'submit': 'Sign+In'})
        check = (b'[Incorrect username or password!]' not in r.content) and (r.status_code == 200)
        self.c.assert_eq(check, True, "Can't login", status=status)

    def create_thread(self, session, title, body, is_private, status=Status.MUMBLE):
        csrf = BeautifulSoup(session.get(self.url + '/create_theme').content, 'lxml').find('input', {'name': 'csrf_token'})['value']
        if is_private == 'y':
            r = session.post(self.url + '/create_theme', data={'csrf_token': csrf,
                'theme_name': title,
                'body': body,
                'is_private': is_private,
                'submit': 'Create+theme'})
        else:
            r = session.post(self.url + '/create_theme', data={'csrf_token': csrf,
                'theme_name': title,
                'body': body,
                'submit': 'Create+theme'})
        self.c.assert_eq(200, r.status_code, "Can't create thread", status=status)
        return r.history[0].headers['Location'].split('/')[-1]

    def check_thread(self, session, thread_id, thread_body, comment_body, status=Status.MUMBLE):
        r = session.get(self.url + f'/posts/{thread_id}')
        check = (thread_body.encode() in r.content) and (comment_body.encode() in r.content)
        self.c.assert_eq(check, True, "Can't get thread", status=status)

    def comment(self, session, body, thread_id, status=Status.MUMBLE):
        csrf = BeautifulSoup(session.get(self.url + f'/posts/{thread_id}').content, 'lxml').find('input', {'name': 'csrf_token'})['value']
        r = session.post(self.url + f'/post_comment/{thread_id}', data={'csrf_token': csrf,
            'body': body,
            'submit2': 'Comment'})
        self.c.assert_eq(200, r.status_code, "Can't post comment", status=status)

    def change_pass(self, session, username, old_pass, new_pass, status=Status.MUMBLE):
        csrf = BeautifulSoup(session.get(self.url + '/settings').content, 'lxml').find('input', {'name': 'csrf_token'})['value']
        r = session.post(self.url + f'/change_pass', data={'csrf_token': csrf,
            'username': username,
            'password': old_pass,
            'password2': new_pass,
            'submit': 'Change+password'})
        self.c.assert_eq(200, r.status_code, "Can't change pass", status=status)

