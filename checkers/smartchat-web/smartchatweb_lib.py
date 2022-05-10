from checklib import Status
import requests
import re
import base64
import urllib
from pathlib import Path

BASE_DIR = Path(__file__).absolute().resolve().parent

PORT = 8000
MAX_FILESIZE = 1024

class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{self.port}'

    def __init__(self, checker):
        self.c = checker
        self.port = PORT

    def register(self, session, username, password, status=Status.MUMBLE):
        r = session.post(f'{self.url}/api/register', json={'username':username,'password1':password,'password2':password})
        self.c.assert_eq(200, r.status_code, "Can't register", status=status)

    def login(self, session, username, password, status=Status.MUMBLE):
        r = session.post(f'{self.url}/api/login', json={'username':username,'password':password})
        self.c.assert_eq(200, r.status_code, "Can't login", status=status)

    def create_room(self, session, roomname, status=Status.MUMBLE):
        r = session.post(f'{self.url}/api/createroom', json={'roomname':roomname})
        self.c.assert_eq(200, r.status_code, "Can't create room", status=status)

    def get_rooms(self, session, rooms, status=Status.MUMBLE):
        r = session.get(f'{self.url}/api/getrooms')
        roomnames = list(map(lambda x: x['roomname'], r.json()))
        check = (set(roomnames) == set(rooms)) and (r.status_code == 200)
        self.c.assert_eq(check, True, "Can't get rooms", status=status)

    def get_messages(self, session, roomname, messages, status=Status.MUMBLE):
        r = session.get(f'{self.url}/api/getmessages', params={'roomname':roomname})
        check = (set(messages).issubset(set(list(map(lambda x: x['content'], r.json()))))) and (r.status_code == 200)
        self.c.assert_eq(200, r.status_code, "Can't get messages room", status=status)

    def send_message(self, session, roomname, message, status=Status.MUMBLE):
        r = session.post(f'{self.url}/api/sendmessage', json={'roomname':roomname, 'message':message})
        self.c.assert_eq(200, r.status_code, "Can't send message", status=status)

    def check_online(self, session, username, status=Status.MUMBLE):
        r = session.get(f'{self.url}/api/usersonline')
        check = (username.encode() in r.content) and (r.status_code == 200)
        self.c.assert_eq(check, True, "Can't get online users", status=status)

