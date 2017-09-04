from flask import Blueprint

per = Blueprint('per', __name__, url_prefix='/person')

from . import api
