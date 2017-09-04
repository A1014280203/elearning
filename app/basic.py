import requests
from requests import auth
import logging
from oauth2client import client, crypt
import random
import time
from urllib.parse import  quote
import hmac
import hashlib
import binascii
import base64
from uuid import uuid1


TOKEN = 'https://api.sandbox.paypal.com/v1/oauth2/token'

PAYMENT = 'https://api.sandbox.paypal.com/v1/payments/payment'

EXECUTE = "https://api.sandbox.paypal.com/v1/payments/payment/{0}/execute/"

G_CLIENT_ID = 'google+ client id'

P_CLIENT_ID = 'paypal client id'

SECRET = 'paypal client secret'

ACCESS_TOKEN = "paypal access token"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + ACCESS_TOKEN
}

# default avatar
STUDENT_PIC = 'student picture url'

TEACHER_PIC = 'teacher picture url'

ADMIN_PIC = 'school administrator picture url'

SCHOOL_PIC = 'school picture url'

COURSE_PIC = 'course picture url'

PARENT_PIC = 'parent picture url'


# payment sample
def make_payment(price):
    price = float(int(price*100))/100
    payload = {
        "intent": "sale",
        "redirect_urls": {
            "return_url": "http://example.com/your_redirect_url.html",
            "cancel_url": "http://example.com/your_cancel_url.html"
        },
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(price),
                "currency": "USD"
            }
        }]
    }
    return payload


def parse_teacher_papers(papers: list):
    _l = dict()
    for paper in papers:
        if paper.p_belong not in _l:
            _l[paper.p_belong] = {'p_course': paper.p_course, 'p_name': paper.p_name, 'p_count': 0}
        else:
            _l[paper.p_belong]['p_count'] += 1
    return _l


def update_str_list(old: str, _new: dict):
    if not old:
        old = '[]'
    _old = eval(old)
    if not isinstance(_old, list):
        _old = list()
    if _new in _old:
        return str(_old)
    _old.append(_new)
    return str(_old)


def reduce_str_list(old: str, element):
    if not old:
        return None
    _old = eval(old)
    if not isinstance(_old, list):
        raise TypeError('%s is not a list' % old)
    _old.remove(element)
    return str(_old)


LOG_FORMAT = logging.Formatter('%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def log(msg):
    c = logging.StreamHandler()
    c.setFormatter(LOG_FORMAT)
    logger = logging.Logger('p', logging.ERROR)
    logger.addHandler(c)
    logger.error(msg)


def make_obj_serializable(obj):
    if isinstance(obj, list):
        _obj = list()
        for item in obj:
            _d = item.__dict__
            _d.pop('_sa_instance_state')
            _obj.append(_d)
        return _obj
    elif isinstance(obj, dict):
        _obj = obj.__dict__
        _obj.pop('_sa_instance_state')
        return _obj
    else:
        log("ignore object, type of %s" % str(type(obj)))
        return obj


def refresh_token():
    payload = {'grant_type': 'client_credentials'}
    auth.HTTPBasicAuth(P_CLIENT_ID, SECRET)
    resp = requests.post(TOKEN, data=payload, auth=auth.HTTPBasicAuth(P_CLIENT_ID, SECRET))
    print(resp.status_code)
    print(resp.text)


def verify_google_plus(token):
    try:
        token = token
        idinfo = client.verify_id_token(token, G_CLIENT_ID)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer")
        return idinfo
    except Exception as e:
        log('User[%s] login with google+ failed <error: %s>' % (token, e.args))
        return None

# Tencent COS Server
class Sign(object):

    def app_sign(self, cos_path, expired, upload_sign=True):
        appid = ''
        bucket = ''
        secret_id = ''
        now = int(time.time())
        rdm = random.randint(0, 999999999)
        cos_path = quote(cos_path.encode('utf-8'), '~/')
        if upload_sign:
            fileid = '/%s/%s%s' % (appid, bucket, cos_path)
        else:
            fileid = cos_path

        if expired != 0 and expired < now:
            expired = now + expired

        sign_tuple = (appid, secret_id, expired, now, rdm, fileid, bucket)

        plain_text = 'a=%s&k=%s&e=%d&t=%d&r=%d&f=%s&b=%s' % sign_tuple
        plain_text = plain_text.encode('utf-8')
        secret_key = '5uWu4zgDVYMuDG2Yv2tVszqJZeV7UdXC'.encode('utf-8')
        sha1_hmac = hmac.new(secret_key, plain_text, hashlib.sha1)
        hmac_digest = sha1_hmac.hexdigest()
        hmac_digest = binascii.unhexlify(hmac_digest)
        sign_hex = hmac_digest + plain_text
        sign_base64 = base64.b64encode(sign_hex)
        return sign_base64

    def sign_once(self, cos_path):
        return self.app_sign(cos_path, 0)

    def sign_more(self, cos_path):
        return self.app_sign(cos_path, 604800)


def gen_file_id():
    return str(uuid1())


def include(own: list, param):
    for part in own:
        if part == param:
            return True
        if param in part:
            return True
    return False

if __name__ == '__main__':
    # get paypal token
    refresh_token()
