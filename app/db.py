from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import atexit
import redis

engine = create_engine('mysql+pymysql://root:password@node:port/database?charset=utf8', pool_recycle=3600*6)


def create_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def connect_redis():
    r = redis.Redis(host='node')
    return r


redisn = connect_redis()
