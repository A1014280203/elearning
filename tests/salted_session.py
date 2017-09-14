import unittest
from flask import session, request
from app import models, create_app
from app.basic import log
import base64
from app.config import Config


class FlaskTestClient(unittest.TestCase):

    def init(self):
        # you can fix these values after faking(models.py) data to database
        self.student_email = 'shirley@mudo.gov'
        self.teacher_email = 'cheryl@skipfire.mil'
        self.parent_email = 'christina@livepath.name'
        self.school_admin_email = 'susan@meevee.com'
        self.default_password = '12345678'
        self.school_name = 'Babbleblab'
        Config.ENCRYPT_SESSION = True

    def setUp(self):
        self.init()
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(allow_subdomain_redirects=True)

    def tearDown(self):
        Config.ENCRYPT_SESSION = False
        models.DBMixin.close()

    def test_encrypted_session(self):
        with self.client as client:
            client.post('/login', data={'email': self.teacher_email, 'password': self.default_password})
            resp = client.get('/')
            svalue = request.cookies.get('session')
            try:
                r = base64.standard_b64decode(svalue)
                assert self.teacher_email.encode() not in r
            except Exception as e:
                assert e.args[0] == 'Incorrect padding'
            finally:
                assert self.teacher_email == session['user']


if __name__ == '__main__':
    unittest.main()
