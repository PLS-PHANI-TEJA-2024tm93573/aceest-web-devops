import pytest
from app import create_app
from app.models import add_client, get_client_by_name

def test_export_pdf_route(client):
    # Add a test client to the DB
    test_data = {
        "name": "TestPDF",
        "age": 30,
        "height": 175,
        "weight": 70,
        "program": "Fat Loss (FL)",
        "target_weight": 65,
        "target_adherence": 90,
        "adherence": 80,
        "notes": "Test notes",
        "calories": 1800,
        "membership_expiry": "2026-12-31",
    }
    add_client(test_data)
    # Ensure client is in DB
    client_data = get_client_by_name("TestPDF")
    assert client_data is not None
    # Request PDF export
    resp = client.get(f"/export_pdf/TestPDF")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/pdf"
    assert resp.headers["Content-Disposition"].startswith("attachment;")
    # PDF should contain the client name
    assert resp.data.startswith(b"%PDF")
