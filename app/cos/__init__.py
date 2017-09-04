from flask import Blueprint

cos = Blueprint('cos', __name__, url_prefix='/course')

from . import api
