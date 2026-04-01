import os
import shutil
import sys
import tempfile

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.models import clear_clients, init_db

test_db_dir = tempfile.mkdtemp()
test_db_path = os.path.join(test_db_dir, "test.db")
os.environ["ACEEST_DB_PATH"] = test_db_path


@pytest.fixture
def app():
    # Create a temporary directory for test database

    # Set environment variable BEFORE creating app

    app = create_app()
    app.config.update({"TESTING": True})

    # Initialize database tables
    init_db()

    yield app

    # Cleanup: remove test database after tests
    shutil.rmtree(test_db_dir, ignore_errors=True)
    if "ACEEST_DB_PATH" in os.environ:
        del os.environ["ACEEST_DB_PATH"]


@pytest.fixture
def client(app):
    return app.test_client()
