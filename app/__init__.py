from flask import Flask
from .main import main as main_bp
from .per import per as per_bp
from .auth import auth as auth_bp
from .pay import pay as pay_bp
from .cos import cos as cos_bp
from .sch import sch as sch_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = 'key'
    app.register_blueprint(main_bp)
    app.register_blueprint(per_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(pay_bp)
    app.register_blueprint(cos_bp)
    app.register_blueprint(sch_bp)
    return app
