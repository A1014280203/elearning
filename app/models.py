from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Text, Float, DateTime, ForeignKey, create_engine, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import create_session, redisn
from app import basic
import atexit
import forgery_py as forgery
import random
from datetime import datetime
from app.db import engine

# from .db import create_session
Base = declarative_base()


# def close_session(s):
#     s[0].close()


class DBMixin(object):

    session = create_session()
    # clear_exit = atexit.register(close_session, (session,))

    @classmethod
    def insert(cls, obj):
        cls.session.add(obj)

    @classmethod
    def commit(cls):
        try:
            cls.session.commit()
        except Exception as e:
            basic.log(e.args)
            cls.session.rollback()
            raise

    @classmethod
    def delete(cls, *args):
        cls.session.query(cls).filter(*args).delete(synchronize_session=False)
        cls.commit()

    @classmethod
    def rollback(cls):
        cls.session.rollback()

    @classmethod
    def query_one(cls, *args):
        r = cls.session.query(cls).filter(*args).first()
        return r

    @classmethod
    def query_range(cls, *args, order_key=None, start, stop):
        r = cls.session.query(cls).filter(*args).order_by(order_key).slice(start, stop).all()
        return r

    @classmethod
    def query_all(cls, *args):
        rs = cls.session.query(cls).filter(*args).all()
        return rs

    @classmethod
    def update(cls, *args):
        _f_args = args[:-1]
        _u_args = args[-1]
        rows = cls.session.query(cls).filter(*_f_args).update(_u_args)
        cls.commit()
        return rows

    @classmethod
    def close(cls):
        cls.session.close()
        return True


class User(Base, DBMixin):

    __tablename__ = 'users'

    u_id = Column(Integer(), primary_key=True)
    u_email = Column(String(255), unique=True, nullable=False, index=True)
    u_gmail = Column(String(255))
    u_name = Column(String(255))
    u_password = Column(String(255), nullable=False)
    # value=>identity: 1=>student, 2=>teacher, 3=>school administrator, 4=>parent
    u_role = Column(Integer(), nullable=False)
    u_own = Column(Text(), nullable=False) # own courses
    u_gender = Column(String(16))
    u_birth = Column(DateTime())
    u_country = Column(String(255), default='-')
    u_province = Column(String(255), default='-')
    u_city = Column(String(255), default='-')
    u_pic = Column(Text())
    u_intro = Column(Text())
    u_star = Column(Text())
    u_contacts = Column(Text())
    # just for school admin
    u_school = Column(Integer(), ForeignKey('schools.s_id'))

    def __init__(self, **kwargs):
        # hash password
        password = kwargs.pop('u_password', None)
        if password is None:
            raise AttributeError('u_password not found')
        self.u_password = generate_password_hash(password)
        # default pic
        if kwargs.get('u_pic', None) is None:
            if kwargs.get('u_role') == 1:
                self.u_pic = basic.STUDENT_PIC
            elif kwargs.get('u_role') == 2:
                self.u_pic = basic.TEACHER_PIC
            elif kwargs.get('u_role') == 3:
                self.u_pic = basic.ADMIN_PIC
        # default own
        if kwargs.get('u_own', None) is None:
            self.u_own = '{}'
        Base.__init__(self, **kwargs)

    @classmethod
    def add_course(cls, u_email, c_id):
        course = Course.query_one(Course.c_id == c_id)
        _new = dict(c_id=course.c_id, c_name=course.c_name, c_pic=course.c_pic)
        user = User.query_one(User.u_email == u_email)
        _own = basic.update_str_list(user.u_own, _new)
        User.update(User.u_email == u_email, {User.u_own: _own})

    @classmethod
    def bind_child(cls, child_email, parent_email):
        user = User.query_one(User.u_email == child_email)
        _child = dict(u_id=user.u_id, u_name=user.u_name, u_pic=user.u_pic)
        _own = basic.update_str_list(user.u_own, _child)
        User.update(User.u_email == parent_email, {User.u_own: _own})

    @classmethod
    def star(cls, u_email, _new):
        user = User.query_one(User.u_email == u_email)
        _star = basic.update_str_list(user.u_star, _new)
        User.update(User.u_email == u_email, {User.u_star: _star})

    @classmethod
    def unstar(cls, u_email, pid):
        user = User.query_one(User.u_email == u_email)
        title = Post.query_one(Post.p_id == pid).p_title
        _new = dict(p_id=pid, p_title=title)
        _star = basic.reduce_str_list(user.u_star, _new)
        User.update(User.u_email == u_email, {User.u_star: _star})

    def hash_password(self):
        return generate_password_hash(self.password)

    def check_hash_password(self, password):
        return check_password_hash(self.u_password, password)

    @classmethod
    def fake_data(cls):
        # fake student
        for i in range(10):
            cls.insert(User(
                u_name=forgery.internet.user_name(),
                u_email=forgery.email.address(),
                u_password='12345678',
                u_gender=forgery.personal.gender(),
                u_birth=forgery.date.datetime(True, min_delta=3650, max_delta=7300),
                u_country=random.choice(['China', 'America']),
                u_intro=forgery.lorem_ipsum.sentences(),
                u_pic=basic.STUDENT_PIC,
                u_role=1,
                u_own='[]'
            ))
        cls.commit()

        # fake teacher
        for i in range(10):
            cls.insert(User(
                u_name=forgery.internet.user_name(),
                u_email=forgery.email.address(),
                u_password='12345678',
                u_gender=forgery.personal.gender(),
                u_birth=forgery.date.datetime(True, min_delta=3650, max_delta=7300),
                u_country=random.choice(['China', 'America']),
                u_intro=forgery.lorem_ipsum.sentences(),
                u_pic=basic.TEACHER_PIC,
                u_role=2,
                u_own='[]'
            ))
        cls.commit()

        # fake admin
        for i in range(10):
            cls.insert(User(
                u_name=forgery.internet.user_name(),
                u_email=forgery.email.address(),
                u_password='12345678',
                u_gender=forgery.personal.gender(),
                u_birth=forgery.date.datetime(True, min_delta=3650, max_delta=7300),
                u_country=random.choice(['China', 'America']),
                u_intro=forgery.lorem_ipsum.sentences(),
                u_pic=basic.ADMIN_PIC,
                u_role=3,
                u_own='[]',
                u_school=random.randint(1, 10)
            ))
        cls.commit()

        # fake parent
        for i in range(10):
            cls.insert(User(
                u_name=forgery.internet.user_name(),
                u_email=forgery.email.address(),
                u_password='12345678',
                u_gender=forgery.personal.gender(),
                u_birth=forgery.date.datetime(True, min_delta=3650, max_delta=7300),
                u_country=random.choice(['China', 'America']),
                u_intro=forgery.lorem_ipsum.sentences(),
                u_pic=basic.PARENT_PIC,
                u_role=4,
                u_own='[]',
                u_school=random.randint(1, 10)
            ))
        cls.commit()


class Course(Base, DBMixin):

    __tablename__ = 'courses'

    c_id = Column(Integer(), primary_key=True)
    c_name = Column(String(255), nullable=False)
    c_price = Column(Float(), default=999.9)
    c_type = Column(String(10), nullable=False)
    c_intro = Column(Text())
    c_pic = Column(Text())
    c_url = Column(Text())
    c_belong = Column(Integer(), ForeignKey('schools.s_id'))
    c_off = Column(Boolean(), default=0)
    c_creator = Column(Integer(), ForeignKey('users.u_id'))

    def __init__(self, **kwargs):
        if kwargs.get('c_pic', None) is None:
            # 这里不会影响到查询d结果，有趣??????????
            self.c_pic = basic.COURSE_PIC
        Base.__init__(self, **kwargs)

    @classmethod
    def fake_data(cls):
        urls = dict()
        urls['video'] = '/static/mp4.mp4'
        urls['pdf'] = '/static/pdf.pdf'
        for i in range(30):
            c_type = random.choice(['video', 'pdf'])
            cls.insert(Course(
                c_name=forgery.name.job_title(),
                c_price=float(random.randint(10, 200)),
                c_type=c_type,
                c_url=urls[c_type],
                c_intro=forgery.lorem_ipsum.sentences(),
                c_pic=basic.COURSE_PIC,
                c_belong=random.randint(1, 10)
            ))
        cls.commit()


class School(Base, DBMixin):

    __tablename__ = 'schools'

    s_id = Column(Integer(), primary_key=True)
    s_name = Column(String(255), nullable=False)
    s_intro = Column(Text())
    s_pic = Column(Text(), nullable=False)
    s_applicants = Column(Text())
    s_teachers = Column(Text())
    s_asset = Column(Float(), default=0.0)

    def __init__(self, **kwargs):
        if kwargs.get('s_pic', None) is None:
            self.s_pic = basic.SCHOOL_PIC
        Base.__init__(self, **kwargs)

    @classmethod
    def add_applicant(cls, user_id, s_name):
        _old = School.query_one(School.s_name == s_name).s_applicants
        user = User.query_one(User.u_id == user_id)
        _new = {'u_id': user.u_id, 'u_name': user.u_name, 'u_email': user.u_email}
        data = basic.update_str_list(_old, _new)
        School.update(School.s_name == s_name, {School.s_applicants: data})

    @classmethod
    def add_teacher(cls, user_id, s_id):
        school = School.query_one(School.s_id == s_id)
        user = User.query_one(User.u_id == user_id)
        _new = {'u_id': user.u_id, 'u_name': user.u_name, 'u_email': user.u_email}
        teachers = basic.update_str_list(school.s_applicants, _new)
        applicants = basic.reduce_str_list(school.s_applicants, _new)
        School.update(School.s_id == s_id, {School.s_applicants: applicants})
        School.update(School.s_id == s_id, {School.s_teachers: teachers})

    @classmethod
    def fake_data(cls):
        for i in range(10):
            cls.insert(School(
                s_name=forgery.name.company_name(),
                s_intro=forgery.lorem_ipsum.sentences(),
                s_pic=basic.SCHOOL_PIC,
                s_teachers='{}'
            ))
        cls.commit()


class Paper(Base, DBMixin):

    __tablename__ = 'papers'

    p_id = Column(Integer(), primary_key=Text)
    p_name = Column(String(255), nullable=False)
    p_cont = Column(Text())
    p_score = Column(Float(), default=0.0)
    p_grade = Column(String(2), default='D')
    p_course = Column(String(255))
    p_belong = Column(Integer(), ForeignKey('courses.c_id'), nullable=False)
    p_teacher = Column(String(255))
    p_creator = Column(Integer(), ForeignKey('users.u_id'), nullable=False)
    p_student = Column(String(255))
    p_worker = Column(Integer(), ForeignKey('users.u_id'))

    def __init__(self, **kwargs):
        self.p_course = Course.query_one(Course.c_id == kwargs.get('p_belong')).c_name
        self.p_teacher = User.query_one(User.u_id == kwargs.get('p_creator')).u_name
        self.p_student = User.query_one(User.u_id == kwargs.get('p_worker')).u_name
        Base.__init__(self, **kwargs)

    @classmethod
    def fake_data(cls):
        for i in range(50):
            cls.insert(Paper(
                p_name=forgery.lorem_ipsum.title(2),
                p_cont=forgery.lorem_ipsum.sentences(5),
                p_score=random.randint(40, 100),
                p_grade=random.choice(['A', 'B', 'C', 'D', 'E']),
                p_belong=random.randint(1, 10),
                p_creator=random.randint(1, 10),
                p_worker=random.randint(1, 10)
            ))
        cls.commit()


class Note(Base, DBMixin):

    __tablename__ = 'notes'

    n_id = Column(Integer(), primary_key=True)
    n_name = Column(String(255))
    n_dtime = Column(DateTime(True))
    n_cont = Column(Text())
    n_course = Column(String(255))
    n_belong = Column(Integer(), ForeignKey('courses.c_id'))
    n_student = Column(String(255))
    n_creator = Column(Integer(), ForeignKey('users.u_id'), nullable=False)
    n_public = Column(Boolean(), default=0)

    def __init__(self, **kwargs):
        self.n_course = Course.query_one(Course.c_id == kwargs.get('n_belong')).c_name
        self.n_student = User.query_one(User.u_id == kwargs.get('n_creator')).u_name
        Base.__init__(self, **kwargs)

    @classmethod
    def fake_data(cls):
        for i in range(50):
            cls.insert(Note(
                n_name=forgery.lorem_ipsum.word(),
                n_dtime=forgery.date.datetime(True, min_delta=50, max_delta=365),
                n_cont=forgery.lorem_ipsum.sentences(3),
                n_belong=random.randint(1, 10),
                n_creator=random.randint(1, 10)
            ))
        cls.commit()


class Post(Base, DBMixin):

    __tablename__ = 'posts'

    p_id = Column(Integer(), primary_key=True)
    p_title = Column(String(255), nullable=False)
    p_dtime = Column(DateTime(True), nullable=False)
    p_cont = Column(Text())
    p_course = Column(String(255))
    p_belong = Column(Integer(), ForeignKey('courses.c_id'), nullable=False)
    p_user = Column(String(255))
    p_creator = Column(Integer(), ForeignKey('users.u_id'))

    def __init__(self, **kwargs):
        self.p_course = Course.query_one(Course.c_id == kwargs.get('p_belong')).c_name
        self.p_user = User.query_one(User.u_id == kwargs.get('p_creator')).u_name
        Base.__init__(self, **kwargs)

    @classmethod
    def fake_data(cls):
        for i in range(150):
            cls.insert(Post(
                p_title=forgery.lorem_ipsum.title(),
                p_dtime=forgery.date.datetime(True, min_delta=50, max_delta=365),
                p_cont=forgery.lorem_ipsum.paragraphs(3),
                p_belong=random.randint(1, 10),
                p_creator=random.randint(1, 10)
            ))
        cls.commit()


class Comment(Base, DBMixin):

    __tablename__ = 'comments'

    c_id = Column(Integer(), primary_key=True)
    c_cont = Column(Text())
    c_dtime = Column(DateTime(True))
    c_user = Column(String(255))
    c_creator = Column(Integer, ForeignKey('users.u_id'), nullable=False)
    c_course = Column(String(255))
    c_belong = Column(Integer(), ForeignKey('posts.p_id'), nullable=False)

    def __init__(self, **kwargs):
        self.c_user = User.query_one(User.u_id == kwargs.get('c_creator')).u_name
        self.c_course = Course.query_one(Course.c_id == kwargs.get('c_belong')).c_name
        Base.__init__(self, **kwargs)

    @classmethod
    def fake_data(cls):
        for i in range(150):
            cls.insert(Comment(
                c_cont=forgery.lorem_ipsum.sentence(),
                c_dtime=forgery.date.datetime(True, min_delta=50, max_delta=356),
                c_creator=random.randint(1, 10),
                c_belong=random.randint(1, 50)
            ))
        cls.commit()


class Coupon(Base, DBMixin):

    __tablename__ = 'coupons'

    c_id = Column(Integer(), primary_key=True)
    c_code = Column(String(255))
    c_dline = Column(DateTime(), nullable=False)
    c_belong = Column(Integer(), ForeignKey('courses.c_id'))
    c_owner = Column(Integer(), ForeignKey('users.u_id'))
    c_discnt = Column(Integer(), nullable=False)
    c_floor = Column(Integer(), default=99)
    c_used = Column(Boolean(), default=0)

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)

    @classmethod
    def fake_data(cls):
        for i in range(50):
            Coupon.insert(Coupon(
                c_code=forgery.basic.text(10),
                c_dline=forgery.date.datetime(min_delta=2),
                c_belong=random.randint(1, 10),
                c_owner=random.randint(1, 10),
                c_discnt=random.randint(1, 99),
                c_floor=random.randint(100, 255)
            ))
        cls.commit()


class Message(Base, DBMixin):

    __tablename__ = 'messages'

    m_id = Column(Integer(), primary_key=True)
    m_cont = Column(String(255))
    m_from = Column(Integer(), ForeignKey('users.u_id'), nullable=False)
    m_to = Column(Integer(), ForeignKey('users.u_id'), nullable=False)
    m_dtime = Column(DateTime(True), nullable=False)

    def __init__(self, **kwargs):
        if kwargs.get('m_dtime', None) is None:
            self.m_dtime = datetime.now()
        Base.__init__(self, **kwargs)

    @classmethod
    def save(cls, obj):
        cls.insert(obj)
        cls.commit()
        redisn.sadd(str(obj.m_to), str(obj.m_from))

    @classmethod
    def exist(cls, user):
        return redisn.exists(user)

    @classmethod
    def pull(cls, user):
        members = redisn.smembers(user)
        redisn.delete(user)
        return members

    @classmethod
    def query_last(cls, *args, num=5):
        return cls.session.query(cls).order_by(cls.m_id.desc()).filter(*args).slice(0, num).all()

    @classmethod
    def fake_data(cls):
        for i in range(20):
            Message.insert(Message(
                m_dtime=forgery.date.datetime(True),
                m_cont=forgery.lorem_ipsum.sentence(),
                m_from=random.randint(1, 10),
                m_to=random.randint(1, 10)
            ))
        cls.commit()


class Order(Base, DBMixin):

    __tablename__ = 'orders'

    o_id = Column(Integer(), primary_key=True)
    o_cname = Column(String(255))
    o_course = Column(Integer(), ForeignKey('courses.c_id'), nullable=False)
    o_buser = Column(String(255))
    o_buyer = Column(Integer(), ForeignKey('users.u_id'), nullable=False)
    o_dtime = Column(DateTime(True))
    o_duser = Column(String(255))
    o_bind = Column(Integer(), ForeignKey('users.u_id'), nullable=False)
    o_coupon = Column(Integer(), ForeignKey('coupons.c_id'))
    o_price = Column(Float(), nullable=False)
    o_count = Column(Integer(), nullable=False, default=1)
    o_finish = Column(Boolean(), default=0)

    def __init__(self, **kwargs):
        self.o_cname = Course.query_one(Course.c_id == kwargs.get('o_course')).c_name
        if kwargs.get('o_bind', None) is None:
            self.o_bind = kwargs.get('o_buyer')
            self.o_buser = User.query_one(User.u_id == kwargs.get('o_buyer')).u_name
            self.o_duser = self.o_buser
        else:
            self.o_buser = User.query_one(User.u_id == kwargs.get('o_buyer')).u_name
            self.o_duser = User.query_one(User.u_id == kwargs.get('o_bind')).u_name
        if kwargs.get('o_dtime', None) is None:
            self.o_dtime = datetime.now()
        Base.__init__(self, **kwargs)

    @classmethod
    def fake_data(cls):
        for i in range(30):
            Order.insert(Order(
                o_course=random.randint(1, 10),
                o_buyer=random.randint(1, 10),
                o_dtime=forgery.date.datetime(True, min_delta=20, max_delta=40),
                o_price=float(random.randint(10, 299))
            ))
        cls.commit()


def create_all():
    Base.metadata.create_all(bind=engine)
    School.fake_data()
    Course.fake_data()
    User.fake_data()
    Coupon.fake_data()
    Message.fake_data()
    Note.fake_data()
    Paper.fake_data()
    Post.fake_data()
    Comment.fake_data()
    Order.fake_data()


def drop_all():
    Base.metadata.drop_all(bind=engine)


def refresh_database():
    drop_all()
    create_all()


if __name__ == '__main__':
    refresh_database()
