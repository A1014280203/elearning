from flask import render_template, request, jsonify, url_for
from ..models import User, School, Course, Paper
from . import main


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/mall')
def mall():
    p = int(request.args.get('p') or 1)
    p -= 1
    items = Course.query_range(Course.c_off == 0, start=p*10, stop=p*10+10)
    return render_template('main/mall.html', items=items)


@main.route('/schools')
def show_schools():
    p = int(request.args.get('p') or 1)
    p -= 1
    items = School.query_range(start=p*10, stop=p*10+10)
    if items:
        combined = list()
        if len(items) % 2:
            items.append(School(s_name=''))
        for i in range(0, len(items), 2):
            combined.append(dict(odd=items[i], even=items[i+1]))
    else:
        combined = items
    return render_template('main/school.html', items=combined)


@main.route('/teachers')
def show_teachers():
    p = int(request.args.get('p') or 1)
    p -= 1
    items = User.query_range(User.u_role == 2, start=p*10, stop=p*10+10)
    if items:
        combined = list()
        if len(items) % 2:
            items.append(School(s_name=''))
        for i in range(0, len(items), 2):
            combined.append(dict(odd=items[i], even=items[i+1]))
    else:
        combined = items
    return render_template('main/teacher.html', items=combined)


@main.after_app_request
def allow_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

