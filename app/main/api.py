import requests
from flask import render_template, request, jsonify, url_for
from ..models import User, School, Course, Paper
from . import main


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/mall')
def mall():
    items = Course.query_all(Course.c_off == 0)
    return render_template('main/mall.html', items=items)


@main.route('/schools')
def school():
    items = School.query_all()
    combined = list()
    if len(items) % 2:
        items.append(School(s_name=''))
    for i in range(0, len(items), 2):
        combined.append(dict(odd=items[i], even=items[i+1]))
    return render_template('main/school.html', items=combined)


@main.route('/teacher')
def user():
    items = User.query_all(User.u_role == 2)
    combined = list()
    if len(items) % 2:
        items.append(School(s_name=''))
    for i in range(0, len(items), 2):
        combined.append(dict(odd=items[i], even=items[i+1]))
    return render_template('main/teacher.html', items=combined)

