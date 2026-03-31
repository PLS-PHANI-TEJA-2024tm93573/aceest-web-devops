import csv
import io

from app.models import clear_clients


def test_save_client_and_endpoints(client):
    # ensure clean state
    clear_clients()

    payload = {
        "name": "TestUser",
        "age": "28",
        "weight": "72",
        "adherence": "85",
        "program": "Fat Loss (FL)",
        "notes": "Test note",
    }

    resp = client.post("/", data=payload)
    assert resp.status_code == 200
    # name should appear in page
    assert b"TestUser" in resp.data

    # JSON data endpoint
    j = client.get("/clients/data")
    assert j.status_code == 200
    js = j.get_json()
    assert "names" in js and "adherence" in js
    assert "TestUser" in js["names"]
    assert 85 in js["adherence"]

    # CSV export
    c = client.get("/export_csv")
    assert c.status_code == 200
    data = c.data.decode("utf-8")
    sio = io.StringIO(data)
    reader = csv.reader(sio)
    rows = list(reader)
    # header + one client row
    assert rows[0] == ["Name", "Age", "Weight", "Program", "Adherence", "Notes"]
    assert any("TestUser" in r for r in rows)
