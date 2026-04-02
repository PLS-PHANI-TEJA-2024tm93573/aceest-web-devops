import pytest

from app.models import save_progress


def test_progress_chart_route(client):
    # Add a client and some progress data
    client_name = "TestUser"
    week = "Week 01 - 2026"
    save_progress(client_name, week, 75)
    save_progress(client_name, "Week 02 - 2026", 80)

    # Should return 200 and contain the chart image
    resp = client.get(f"/progress_chart/{client_name}")
    assert resp.status_code == 200
    assert b"Progress Chart for TestUser" in resp.data
    assert b"data:image/png;base64" in resp.data


def test_progress_chart_route_no_data(client):
    # Should redirect to index if no progress data
    resp = client.get("/progress_chart/NoSuchUser", follow_redirects=True)
    assert resp.status_code == 200
    assert b"No progress data available for this client" in resp.data
