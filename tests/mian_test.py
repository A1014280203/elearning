import unittest
from flask import url_for, session
from app import models, create_app
from app.basic import log
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
        Config.ENCRYPT_SESSION = False

    def setUp(self):
        self.init()
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(allow_subdomain_redirects=True)

    def tearDown(self):
        models.DBMixin.close()

    def test_main(self):
        resp = self.client.get('/')
        assert '学校' in resp.data.decode()
        resp = self.client.get('/mall')
        assert resp.status_code == 200
        resp = self.client.get('/schools')
        assert resp.status_code == 200
        resp = self.client.get('/teachers')
        assert resp.status_code == 200

    def test_invalid_user(self):
        with self.client as client:
            # login
            client.post('/login', data={'email': 'nosuchuser@email.com', 'password': 'password'})
            resp = client.get(url_for('auth.login'))
            assert 'Incorrect email or password.' in resp.data.decode()
            # course
            resp = client.get(url_for('cos.course_play', c_id=1))
            assert resp.headers['Location'] == url_for('auth.login', _external=True)
            # pay
            resp = client.get(url_for('pay.show', c_id=1))
            assert resp.headers['Location'] == url_for('auth.login', _external=True)
            # person
            resp = client.get(url_for('per.info_page'))
            assert resp.headers['Location'] == url_for('auth.login', _external=True)
            resp = client.get(url_for('per.info_page', uid=1))
            assert '学生' in resp.data.decode()
            assert 'Learn this' not in resp.data.decode()
            # school
            resp = client.get(url_for('sch.apply'))
            assert resp.headers['Location'] == url_for('auth.login', _external=True)

    def test_valid_auth(self):
        with self.client as client:
            # student
            client.post('/login', data={'email': self.student_email, 'password': self.default_password})
            resp = client.get(url_for('per.info_page'))
            assert '学生' in resp.data.decode()
            # teacher
            client.post('/login', data={'email': self.teacher_email, 'password': self.default_password})
            resp = client.get(url_for('per.info_page'))
            assert '教师' in resp.data.decode()
            # school administrator
            client.post('/login', data={'email': self.school_admin_email, 'password': self.default_password})
            resp = client.get(url_for('per.info_page'))
            assert '学校' in resp.data.decode()
            # parent
            client.post('/login', data={'email': self.parent_email, 'password': self.default_password})
            resp = client.get(url_for('per.info_page'))
            assert '家长' in resp.data.decode()
            # new user
            client.post('/register', data={'email': 'testuser@test.coml', 'password': self.default_password,
                                           'name': 'testname', 'identity': 1})
            client.post('/login', data={'email': 'testuser@test.coml', 'password': self.default_password})
            resp = client.get(url_for('per.info_page'))
            assert '学生' in resp.data.decode()
            # logout
            resp = client.get('/logout')
            assert 'user' not in session

    def test_course(self):
        with self.client as client:
            client.post('/login', data={'email': self.student_email, 'password': self.default_password})
            resp = client.get(url_for('per.info_page'))
            assert '学生' in resp.data.decode()
            # course info
            resp = client.get(url_for('cos.course_info', c_id=1))
            assert '课程信息' in resp.data.decode()
            # note
            resp = client.post(url_for('cos.note', c_id=1), data=
            {'n_name': 'testNote', 'n_cont': 'some words', 'n_dtime': '2017-09-11 13:26'})
            assert 'accepted' in resp.data.decode()
            resp = client.get(url_for('cos.note', c_id=1))
            assert 'testNote' in resp.data.decode()
            # group
            resp = client.get(url_for('cos.group', c_id=1))
            assert '讨论区' in resp.data.decode()
            # post
            resp = client.post(url_for('cos.post', c_id=1), data={'p_title': 'TestPost', 'p_cont': 'TestContent'})
            assert resp.headers['Location'] == url_for('cos.group', c_id=1, _external=True)
            resp = client.get(url_for('cos.group', c_id=1))
            assert 'TestPost' in resp.data.decode()
            # comment
            resp = client.post(url_for('cos.comment'), data={'c_cont': 'TestComment'},
                               headers={'referrer': url_for('cos.post', pid=1, _external=True)})
            assert resp.headers['Location'] == url_for('cos.post', pid=1, _external=True)
            resp = client.get(url_for('cos.comment', pid=1))
            assert 'TestComment' in resp.data.decode()

    def test_person(self):
        with self.client as client:
            client.post('/login', data={'email': self.student_email, 'password': self.default_password})
            resp = client.get(url_for('per.info_page'))
            assert '学生' in resp.data.decode()
            # like
            resp = client.post(url_for('per.like'), data={'pid': '1', 'title': 'Elementum libero convallis erat!'})
            assert 'accepted' in resp.data.decode()
            client.post(url_for('per.like'), data={'pid': '1', 'title': 'Elementum libero convallis erat!'})
            resp = client.get(url_for('per.like'))
            assert resp.data.decode().count('Elementum libero convallis erat!') == 1
            client.delete('/person/like/1')
            resp = client.get(url_for('per.like'))
            assert resp.data.decode().count('Elementum libero convallis erat!') == 0
            # message
            resp = client.post(url_for('per.message'), data={'m_cont': 'TestMessage', 'm_to': '11'})
            assert 'accepted' in resp.data.decode()
            client.post('/login', data={'email': self.teacher_email, 'password': self.default_password})
            resp = client.get(url_for('per.info_page'))
            assert '教师' in resp.data.decode()
            resp = client.get(url_for('per.new_message'))
            assert '1' in resp.data.decode()
            resp = client.get(url_for('per.message'))
            assert len(eval(resp.data.decode())) != 0
            resp = client.get(url_for('per.get_message', sender=1))
            assert len(eval(resp.data.decode().replace('null', 'None'))) > 0
            # parent
            client.post('/login', data={'email': self.student_email, 'password': self.default_password})
            resp = client.post(url_for('per.bind_parent'), data={'u_email': self.parent_email})
            assert 'accepted' in resp.data.decode()
            client.post('/login', data={'email': self.parent_email, 'password': self.default_password})
            resp = client.get(url_for('per.info_page'))
            assert '家长' in resp.data.decode()
            resp = client.get(url_for('per.show_child'))
            assert len(eval(resp.data.decode())) != 0
            # order
            resp = client.get(url_for('per.show_orders'))
            assert resp.status_code == 200

    def test_school(self):
        with self.client as client:
            # apply
            client.post('/login', data={'email': self.teacher_email, 'password': self.default_password})
            resp = client.get(url_for('sch.apply'))
            assert '申请' in resp.data.decode()
            client.post(url_for('sch.apply'), data={'school-name': self.school_name})
            resp = client.get(url_for('sch.apply'))
            assert 'submitted' in resp.data.decode()
            client.post('/login', data={'email': self.school_admin_email, 'password': self.default_password})
            resp = client.get(url_for('sch.apply'))
            assert '申请' in resp.data.decode()
            client.post(url_for('sch.apply'), data={'school-name': self.school_name})
            resp = client.get(url_for('sch.apply'))
            assert 'already existed' in resp.data.decode()
            # accept
            resp = client.post(url_for('sch.accept'), data={'accepted': ['11']})
            assert 'Operation succeed' in resp.data.decode()

    def test_pagination(self):
        with self.client as client:
            resp = client.get('/mall?p=100')
            self.assertTrue('No more courses' in resp.data.decode())

if __name__ == '__main__':
    unittest.main()
