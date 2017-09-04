from flask import render_template, request, session, url_for, redirect, flash, jsonify
from ..models import User
from ..db import redisn
from . import auth
from oauth2client import client, crypt
from .. import basic


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    if request.method == 'POST':
        data = request.form
        if User.query_one(User.u_email == data['email']):
            flash('email existed', category='error')
        else:
            User.insert(User(
                u_name=data['name'] or 't',
                u_email=data['email'],
                u_password=data['password'],
                u_role=data['identity']
            ))
            User.commit()
            session['user'] = data['email']
            if data['identity'] == 3:
                return redirect(url_for('sch.apply'))
        return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user' in session:
            if 'uid' not in session:
                session['uid'] = User.query_one(User.u_email == session['user']).u_id
            return redirect('/')
        return render_template('auth/login.html')
    if request.method == 'POST':
        data = request.form
        if 'idtoken' in data:
            try:
                token = data['idtoken']
                idinfo = client.verify_id_token(token, basic.G_CLIENT_ID)
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise crypt.AppIdentityError("Wrong issuer")
                msg = 'accepted'
            except Exception as e:
                basic.log('User[%s] login with google+ failed <error %s>' % (data['idtoken'], e.args))
                msg = ''
            finally:
                if msg:
                    user = User.query_one(User.u_gmail == idinfo['email'])
                    if user:
                        session['user'] = user.u_email
                        session['uid'] = user.u_id
                return jsonify({'msg': msg})
        else:
            user = User.query_one(User.u_email == data['email'])
            if user and user.check_hash_password(data['password']):
                session['user'] = user.u_email
                session['uid'] = user.u_id
                return redirect('/')
    
        flash('Incorrect email or password.', category='error')
        return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@auth.route('/sign/video')
def gen_cos_vsign():
    _sign = redisn.get('vsign')
    if not _sign:
        s = basic.Sign()
        _sign = s.sign_more('/video/')
        redisn.set('vsign', _sign, ex=604700)
    return _sign


@auth.route('/sign/pdf')
def gen_cos_psign():
    _sign = redisn.get('psign')
    if not _sign:
        s = basic.Sign()
        _sign = s.sign_more('/pdf/')
        redisn.set('psign', _sign, ex=604700)
    return _sign


@auth.route('/sign/pic')
def gen_cos_picsign():
    _sign = redisn.get('picsign')
    if not _sign:
        s = basic.Sign()
        _sign = s.sign_more('/picture/')
        redisn.set('picsign', _sign, ex=604700)
    return _sign


@auth.route('/sign/once')
def gen_cos_nsign():
    s = basic.Sign()
    _sign = s.sign_once('/p2/video')
    return jsonify({'sign': _sign})
