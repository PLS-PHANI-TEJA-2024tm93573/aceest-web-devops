import pytest

from app.models import clear_clients, get_clients


def test_progress_logging(client):
    clear_clients()
    # Create a client
    payload = {
        "name": "ProgressUser",
        "age": "35",
        "weight": "80",
        "adherence": "60",
        "program": "Muscle Gain (MG)",
        "notes": "Initial",
    }
    resp = client.post("/", data=payload)
    assert resp.status_code == 200
    # Log progress
    progress_payload = {"progress_name": "ProgressUser", "progress_adherence": "75"}
    resp2 = client.post("/save_progress", data=progress_payload, follow_redirects=True)
    assert resp2.status_code == 200
    assert b"Weekly progress logged" in resp2.data
    # Update client adherence
    payload2 = payload.copy()
    payload2["adherence"] = "90"
    resp3 = client.post("/", data=payload2)
    assert resp3.status_code == 200
    # Check client updated
    clients = get_clients()
    found = [c for c in clients if c["name"] == "ProgressUser"]
    assert found
    assert found[0]["adherence"] == 90


def test_progress_logging_missing_name(client):
    resp = client.post(
        "/save_progress", data={"progress_adherence": "80"}, follow_redirects=True
    )
    assert resp.status_code == 200
    assert b"Client name required to save progress" in resp.data


def test_duplicate_client_update(client):
    clear_clients()
    payload = {
        "name": "DupUser",
        "age": "40",
        "weight": "70",
        "adherence": "50",
        "program": "Beginner (BG)",
        "notes": "First",
    }
    client.post("/", data=payload)
    # Post again with new adherence
    payload2 = payload.copy()
    payload2["adherence"] = "99"
    client.post("/", data=payload2)
    clients = get_clients()
    found = [c for c in clients if c["name"] == "DupUser"]
    assert found
    assert found[0]["adherence"] == 99
    # Only one entry in DB
    assert len(found) == 1


def test_invalid_adherence(client):
    clear_clients()
    payload = {
        "name": "InvalidAdh",
        "age": "22",
        "weight": "60",
        "adherence": "notanumber",
        "program": "Fat Loss (FL)",
        "notes": "Test",
    }
    resp = client.post("/", data=payload)
    assert resp.status_code == 200
    # Should default to 0
    clients = get_clients()
    found = [c for c in clients if c["name"] == "InvalidAdh"]
    assert found
    assert found[0]["adherence"] == 0
