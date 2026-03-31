from flask import Flask
import os

from .models import load_from_file


def create_app():

    app = Flask(__name__)

    # default data directory (repo-root/data/clients.json)
    data_dir = os.path.abspath(os.path.join(app.root_path, "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    data_path = os.path.join(data_dir, "clients.json")
    app.config["CLIENTS_DATA_PATH"] = data_path

    # Optionally load persisted clients on startup when ACEEST_LOAD_CLIENTS=1
    if os.environ.get("ACEEST_LOAD_CLIENTS") == "1":
        try:
            load_from_file(data_path)
        except Exception:
            # don't fail startup if loading fails
            pass

    from .routes import main

    app.register_blueprint(main)

    return app
