import pytest
from app import create_app
from app.models import add_client, get_client_by_name

def test_delete_client_route(client):
    # Add a test client
    test_data = {
        "name": "DeleteMe",
        "age": 25,
        "height": 170,
        "weight": 65,
        "program": "Beginner (BG)",
        "target_weight": 60,
        "target_adherence": 80,
        "adherence": 75,
        "notes": "To be deleted",
        "calories": 1500,
        "membership_expiry": "2026-12-31",
    }
    add_client(test_data)
    assert get_client_by_name("DeleteMe") is not None
    # Delete the client
    resp = client.post("/delete_client/DeleteMe", follow_redirects=True)
    assert resp.status_code == 200
    assert b"deleted" in resp.data or b"Deleted" in resp.data
    assert get_client_by_name("DeleteMe") is None

def test_edit_client_route(client):
    # Add a test client
    test_data = {
        "name": "EditMe",
        "age": 30,
        "height": 180,
        "weight": 80,
        "program": "Fat Loss (FL)",
        "target_weight": 75,
        "target_adherence": 85,
        "adherence": 80,
        "notes": "To be edited",
        "calories": 1700,
        "membership_expiry": "2026-12-31",
    }
    add_client(test_data)
    # Edit the client
    resp = client.post(
        "/edit_client/EditMe",
        data={
            "age": 31,
            "height": 181,
            "weight": 81,
            "program": "Muscle Gain (MG)",
            "target_weight": 77,
            "target_adherence": 90,
            "adherence": 85,
            "notes": "Edited!",
            "calories": 1800,
            "membership_expiry": "2027-01-01",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    updated = get_client_by_name("EditMe")
    assert updated["age"] == 31
    assert updated["height"] == 181
    assert updated["weight"] == 81
    assert updated["program"] == "Muscle Gain (MG)"
    assert updated["target_weight"] == 77
    assert updated["target_adherence"] == 90
    assert updated["adherence"] == 85
    assert updated["notes"] == "Edited!"
    assert updated["calories"] == 1800
    assert updated["membership_expiry"] == "2027-01-01"
