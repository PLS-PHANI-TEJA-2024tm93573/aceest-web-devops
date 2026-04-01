import secrets

from flask import Flask

from .models import init_db


def create_app():

    app = Flask(__name__)

    app.secret_key = secrets.token_hex(32)

    # If running tests, use a writable DB path in /tmp
    if app.config.get("TESTING") or ("PYTEST_CURRENT_TEST" in os.environ):
        app.config["ACEEST_DB_PATH"] = "/tmp/test.db"
        os.environ["ACEEST_DB_PATH"] = "/tmp/test.db"

    # Initialize SQLite DB and tables (v2.0.1 compatibility)
    try:
        init_db()
    except Exception:
        pass

    from .routes import main

    app.register_blueprint(main)

    return app
