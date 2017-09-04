from flask import Blueprint

sch = Blueprint('sch', __name__, url_prefix='/school')

from . import api
