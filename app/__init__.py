from flask import Flask, current_app
from .main import main as main_bp
from .per import per as per_bp
from .auth import auth as auth_bp
from .pay import pay as pay_bp
from .cos import cos as cos_bp
from .sch import sch as sch_bp
from flask.sessions import SecureCookieSession, SecureCookieSessionInterface
import struct


class SignedSession(SecureCookieSession):

    def __init__(self, *args, **kwargs):
        super(SignedSession, self).__init__(*args, **kwargs)
        self.skey = current_app.config.get('SESSION_KEY', None) or current_app.config.get('SECRET_KEY')
        self.skey_int = 0

    def __getitem__(self, key):
        salt_value = super(SignedSession, self).__getitem__(key)
        value = self.decrypt(salt_value)
        return value

    def __setitem__(self, key, value):
        salt_value = self.encrypt(value)
        return super(SignedSession, self).__setitem__(key, salt_value)

    def parse_key(self):
        if not self.skey_int:
            key = self.skey
            if not isinstance(key, bytes):
                key = key.encode()
            if len(key) % 4:
                key = 'f'.encode() * (4 - len(key) % 4) + key
            num = 0
            for _num in struct.unpack('>' + len(key) // 4 * 'L', key):
                num = num + _num
            self.skey_int = num + 0x10ffff
        return self.skey_int

    def encrypt(self, data):
        if not isinstance(data, str):
            data = str(data)
        encrypted = list()
        key_int = self.parse_key()
        for c in data:
            encrypted.append(str(ord(c) ^ key_int))
        return str(len(encrypted[0])) + ''.join(encrypted)

    def decrypt(self, encrypted):
        decrypted = ''
        key_int = self.parse_key()
        step = int(encrypted[:2])
        encrypted = encrypted[2:]
        for i in range(len(encrypted) // step):
            decrypted += chr(int(encrypted[i * step: i * step + step]) ^ key_int)
        return decrypted


def create_app():
    from app.config import Config
    app = Flask(__name__)
    app.config.from_object(Config)
    if Config.ENCRYPT_SESSION:
        SecureCookieSessionInterface.session_class = SignedSession
    app.register_blueprint(main_bp)
    app.register_blueprint(per_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(pay_bp)
    app.register_blueprint(cos_bp)
    app.register_blueprint(sch_bp)

    return app
