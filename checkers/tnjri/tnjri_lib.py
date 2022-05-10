from checklib import Status
from pathlib import Path

BASE_DIR = Path(__file__).absolute().resolve().parent

PORT = 8080


class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{self.port}'

    def __init__(self, checker):
        self.c = checker
        self.port = PORT

    def register(self, session, login, password, status=Status.MUMBLE):
        r = session.post(self.url + '/api/register',
                         json={'login': login, 'passwd': password})
        self.c.assert_eq(201, r.status_code, "Can't register", status=status)

    def login(self, session, login, password, status=Status.MUMBLE):
        r = session.post(self.url + '/api/login', json={'login': login, 'passwd': password})
        self.c.assert_eq(200, r.status_code, "Can't login", status=status)
        return r.json()["id"]

    def encrypt(self, session, login, password, data, key, status=Status.MUMBLE):
        r = session.post(self.url + '/api/encrypt', json={'login': login, 'passwd': password, 'data': data, 'key': key})
        self.c.assert_eq(200, r.status_code, "Can't encrypt", status=status)
        return r.json()["encrypted"]

    def decrypt(self, session, login, password, data, key, status=Status.MUMBLE):
        r = session.post(self.url + '/api/decrypt', json={'login': login, 'passwd': password, 'data': data, 'key': key})
        self.c.assert_eq(200, r.status_code, "Can't decrypt", status=status)
        return r.json()["decrypted"].replace('\x00', '')

    def state_tree(self, session, login, password, id, status=Status.MUMBLE):
        r = session.post(self.url + '/api/state/tree', json={'login': login, 'passwd': password, 'id': id})
        self.c.assert_eq(200, r.status_code, "Can't get tree", status=status)
        return r.json()["tree"], r.json()["encrypted"]

    def state_key(self, session, login, password, id, status=Status.MUMBLE):
        r = session.post(self.url + '/api/state/key', json={'login': login, 'passwd': password, 'id': id})
        self.c.assert_eq(200, r.status_code, "Can't get key", status=status)
        return r.json()["key"]

    def check_about(self, session, name, status=Status.MUMBLE):
        r = session.get(self.url + '/about?name=' + name)
        self.c.assert_eq(200, r.status_code, "Can't get /about", status=status)

