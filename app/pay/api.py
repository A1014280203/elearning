from flask import render_template, request, jsonify, session, redirect, url_for
from . import pay
from .. import basic
import requests
from ..models import Course, User, Coupon, School, Order


@pay.route('/<c_id>')
def show(c_id):
    item = Course.query_one(Course.c_id == c_id)
    session['course'] = c_id
    if 'user' in session:
        coupons = Coupon.query_all(Coupon.c_owner == session['uid'], Coupon.c_belong == c_id, Coupon.c_used == False)
        for _coupon in coupons:
            if _coupon.c_floor > item.c_price:
                coupons.remove(_coupon)
        return render_template('pay/show.html', item=item, coupons=coupons)
    else:
        return redirect(url_for('auth.login'))


# require login
@pay.route('/create', methods=['POST'])
def create():
    if 'user' not in session:
        return jsonify({'error': 'user required'})
    course_id = request.values['course_id']
    if not course_id:
        return jsonify({'error': 'no course chosen'})
    else:
        course = Course.query_one(Course.c_id == course_id)
        price = course.c_price

    coupon_id = request.values['coupon_id'] or None
    if coupon_id:
        coupon = Coupon.query_one(
            Coupon.c_id == coupon_id, Coupon.c_belong == course_id, Coupon.c_owner == session['uid'])
        if coupon and coupon.c_floor < price:
            price -= coupon.c_discnt
        else:
            coupon_id = None

    payload = basic.make_payment(price)
    resp = requests.post(basic.PAYMENT, json=payload, headers=basic.HEADERS)
    if resp.status_code < 300:
        data = resp.json()
        if data['state'] == 'created':
            Order.insert(Order(o_buyer=session['uid'], o_course=course_id, o_price=price, o_coupon=coupon_id))
            Order.commit()
            return jsonify({'id': data['id']})
    else:
        basic.log('[status code: %s] <%s>' % (resp.status_code, resp.text))
        return '', resp.status_code


# require login
@pay.route('/execute', methods=['POST'])
def execute():
    if 'user' not in session or 'course' not in session:
        return {'error': 'invalid operation.'}
    payload = {'payer_id': request.values['payerID']}
    resp = requests.post(
        basic.EXECUTE.format(request.values['paymentID']),
        json=payload,
        headers=basic.HEADERS
    )
    if resp.status_code < 300:
        data = resp.json()
        if data['state'] == 'approved':
            # 分配课程给用户
            User.add_course(session['user'], session['course'])
            # 给予学校收益
            s_id = Course.query_one(Course.c_id == session['course']).c_belong
            order = Order.query_one(Order.o_buyer == session['uid'], Order.o_course == session['course'],
                                    Order.o_finish == False)
            School.update(School.s_id == s_id, {School.s_asset: School.s_asset+order.o_price*order.o_count})
            # 标记订单完成
            Order.update(Order.o_course == session['course'], Order.o_buyer == session['uid'], {Order.o_finish: True})
            # 标记优惠券已使用
            Coupon.update(Coupon.c_id == order.o_coupon, {Coupon.c_used: True})
            # 取消流程标记
            session.pop('course')
            return jsonify({'state': 'approved'})
    else:
        basic.log('[status code: %s] <%s>' % (resp.status_code, resp.text))
        return '', resp.status_code


@pay.route('/result')
def result():
    item = True
    if 'course' in session:
        item = False
    return render_template('pay/result.html', item=item)


@pay.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        # only preserve course_id
        _new = request.json['courses']
        c_list = session.get('cart', [])
        session['cart'] = c_list.extend(_new)
    if request.method == 'GET':
        if 'cart' in session:
            c_list = list()
            for c_id in session['cart']:
                _cos = Course.query_one(Course.c_id == c_id)
                c_list.append(_cos)
            return jsonify(c_list)
        return jsonify([])


# api to get coupon
@pay.route('/coupon', methods=['POST', 'GET'])
def coupon():
    if request.method == 'GET':
        coupons = Coupon.query_all(Coupon.c_owner == session['uid'], Coupon.c_used == False)
        return jsonify(coupons)
    if request.method == 'POST':
        # 通过优惠码绑定优惠券
        code = request.form.get('code')
        rows = Coupon.update(Coupon.c_code == code, {Coupon.c_owner: session['uid']})
        if not rows:
            return jsonify({"r": "Coupon Code Error"})
        return jsonify({"r": "Coupon bound successfully"})


@pay.before_request
def required_login():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    user = User.query_one(User.u_email == session['user'])
    if not user or user.u_id != session['uid']:
        return redirect(url_for('auth.login'))