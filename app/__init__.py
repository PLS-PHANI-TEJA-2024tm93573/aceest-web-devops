import secrets

from flask import Flask

from .models import init_db


def create_app():

    app = Flask(__name__)

    app.secret_key = secrets.token_hex(32)

    # Initialize SQLite DB and tables (v2.0.1 compatibility)
    try:
        init_db()
    except Exception:
        pass

    from .routes import main

    app.register_blueprint(main)

    return app
