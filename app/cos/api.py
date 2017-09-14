from flask import redirect, request, jsonify, session, render_template, url_for
from urllib.parse import parse_qs, urlparse
from ..models import Course, Paper, Note, User, Post, Comment, School
from . import cos
from .. import basic
from _datetime import datetime


@cos.route('/<c_id>')
def course_play(c_id):
    user = User.query_one(User.u_email == session['user'])
    if basic.include(user.u_own, c_id):
        item = Course.query_one(Course.c_id == c_id)
        if item:
            return render_template('cos/display.html', **{item.c_type: item})
    else:
        return redirect(url_for('pay.show', c_id=c_id))
    return ''


@cos.route('/info/<c_id>')
def course_info(c_id):
    course = Course.query_one(Course.c_id == c_id)
    papers = Paper.query_all(Paper.p_belong == c_id)
    count = 0
    if papers:
        _d = dict()
        for paper in papers:
            _d[paper.p_name] = _d.get(paper.p_name, -1) + 1
        count = max(_d.values())
    return render_template('cos/info.html', course=course, papers=papers, count=count)


@cos.route('/<c_id>/note', methods=['POST', 'GET'])
def note(c_id):
    if request.method == 'GET':
        p = int(request.args.get('p') or 1)
        p -= 1
        uid = session['uid']
        items = Note.query_range(
            Note.n_creator == uid,
            Note.n_public == 0,
            Note.n_belong == c_id,
            order_key=Note.n_id.desc(),
            start=p*10, stop=p*10+10
        )
        if items:
            notes = basic.make_obj_serializable(items)
        else:
            notes = []
        return jsonify(notes)
    elif request.method == 'POST':
        data = dict()
        data['n_name'] = request.values['n_name']
        data['n_cont'] = request.values['n_cont']
        data['n_dtime'] = request.values['n_dtime'] or datetime.now()
        data['n_belong'] = c_id
        data['n_creator'] = session['uid']
        Note.insert(Note(**data))
        Note.commit()
        return 'accepted'


@cos.route('/<c_id>/group', methods=['GET'])
def group(c_id):
    if request.method == 'GET':
        p = int(request.args.get('p') or 1)
        p -= 1
        items = Post.query_range(Post.p_belong == c_id, order_key=Post.p_id.desc(),
                                 start=p*10, stop=p*10+10)
        if items:
            name = items[0].p_course
        else:
            name = Course.query_one(Course.c_id == c_id).c_name
        return render_template('cos/group.html', items=items, course_name=name)


@cos.route('/post')
@cos.route('/<c_id>/post', methods=['POST', 'GET'])
def post(c_id=None):
    if request.method == 'GET':
        p_id = request.args.get('pid')
        if p_id:
            item = Post.query_one(Post.p_id == p_id)
            comments = Comment.query_all(Comment.c_belong == p_id)
            return render_template('cos/post.html', item=item, comments=comments[::-1])
        elif c_id is not None:
            return render_template('cos/edit.html')
    elif request.method == 'POST' and c_id is not None:
        data = dict()
        data['p_title'] = request.values.get('p_title')
        data['p_cont'] = request.values.get('p_cont')
        data['p_dtime'] = datetime.utcnow()
        data['p_creator'] = session['uid']
        data['p_belong'] = c_id
        Post.insert(Post(**data))
        Post.commit()
        return redirect(url_for('cos.group', c_id=c_id))


@cos.route('/post/comment', methods=['POST', 'GET'])
def comment():
    if request.method == 'GET':
        p_id = request.args.get('pid')
        p = int(request.args.get('p') or 1)
        p -= 1
        items = Comment.query_range(Comment.c_belong == p_id, start=p*10, stop=p*10+10)
        if items:
            comments = basic.make_obj_serializable(items)
        else:
            comments = []
        return jsonify(comments)
    elif request.method == 'POST':
        data = dict()
        data['c_cont'] = request.values.get('c_cont')
        data['c_dtime'] = datetime.utcnow()
        data['c_creator'] = session['uid']
        referrer = request.referrer or request.headers['referrer']
        data['c_belong'] = referrer.split('=')[-1]
        # data['c_belong'] = request.args.get('pid')
        Comment.insert(Comment(**data))
        Comment.commit()
        return redirect(referrer)


# 应该检查文件类型
@cos.route('/upload/video', methods=['GET', 'POST'])
def upload_v():
    if request.method == 'GET':
        return render_template('cos/upload.html', folder='/video/', sign_name='auth.gen_cos_vsign',
                               file_id=basic.gen_file_id())
    if request.method == 'POST':
        data = dict()
        data['c_name'] = request.form.get('c_name')
        data['c_url'] = eval(request.form.get('result')).get('data').get('access_url')
        data['c_intro'] = request.form.get('c_intro')
        data['c_price'] = request.form.get('c_price')
        data['c_creator'] = session['uid']
        # None presents free-worker
        s_name = request.form.get('s_name') or None
        if s_name:
            school = School.query_one(School.s_name == s_name)
            if school:
                if basic.include(school.s_teachers, session['user']):
                    data['c_belong'] = school.s_id
                else:
                    return "You aren't in this school", 503
            else:
                return 'No such school', 404
        data['c_type'] = 'video'
        Course.insert(Course(**data))
        Course.commit()
        return ''


@cos.route('/upload/pdf', methods=['GET', 'POST'])
def upload_p():
    if request.method == 'GET':
        return render_template('cos/upload.html', folder='/pdf/', sign_name='auth.gen_cos_psign',
                               file_id=basic.gen_file_id())
    if request.method == 'POST':
        data = dict()
        data['c_name'] = request.form.get('c_name')
        data['c_url'] = eval(request.form.get('result')).get('data').get('access_url')
        data['c_intro'] = request.form.get('c_intro')
        data['c_price'] = request.form.get('c_price')
        data['c_creator'] = session['uid']
        # None presents free-worker
        s_name = request.form.get('s_name') or None
        if s_name:
            school = School.query_one(School.s_name == s_name)
            if school:
                if basic.include(school.s_teachers, session['user']):
                    data['c_belong'] = school.s_id
                else:
                    return "You aren't in this school", 503
            else:
                return 'No such school', 404
        data['c_type'] = 'pdf'
        Course.insert(Course(**data))
        Course.commit()
        return ''


@cos.route('/activate', methods=['POST'])
def activate():
    user = User.query_one(User.u_email == session['user'])
    if user and user.u_role == 3:
        for k, v in request.form.items():
            print(k, v)
            Course.update(Course.c_id == k, {Course.c_off: bool(int(v))})
        return 'Operation succeed'


@cos.route('/upload/picture', methods=['POST', 'GET'])
def set_avatar():
    if request.method == 'GET':
        return render_template('cos/upload.html', folder='/picture/', sign_name='auth.gen_cos_picsign',
                               file_id=basic.gen_file_id())
    if request.method == 'POST':
        c_id = request.values.get('c_id')
        c_pic = eval(request.form.get('result')).get('data').get('access_url')
        Course.update(Course.c_creator == session['uid'], Course.c_id == c_id, {Course.c_pic: c_pic})
        return ''


@cos.before_request
def required_login():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    user = User.query_one(User.u_email == session['user'])
    if not user or user.u_id != session['uid']:
        return redirect(url_for('auth.login'))
