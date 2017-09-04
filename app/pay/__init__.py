from flask import Blueprint

pay = Blueprint('pay', __name__, url_prefix='/pay')

from . import api
