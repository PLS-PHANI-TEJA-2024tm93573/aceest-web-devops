import pytest

from app import create_app
from app.programs import programs


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACEest Functional Fitness" in response.data


def test_post_select_program_no_weight(client):
    resp = client.post("/", data={"program": "Fat Loss (FL)"})
    assert resp.status_code == 200
    # workout + diet are present
    assert b"Workout Plan" in resp.data
    assert b"Diet Plan" in resp.data
    # no calories when weight not provided
    assert b"Estimated Calories" not in resp.data


def test_post_select_program_with_weight(client):
    program = "Fat Loss (FL)"
    weight = 68.5
    cf = programs[program]["calorie_factor"]
    expected = int(weight * cf)

    resp = client.post("/", data={"program": program, "weight": str(weight)})
    assert resp.status_code == 200
    # calories displayed
    assert str(expected).encode() in resp.data
    # color styling should include the program color
    color = programs[program]["color"]
    assert color.encode() in resp.data


def test_post_invalid_weight(client):
    resp = client.post(
        "/", data={"program": "Muscle Gain (MG)", "weight": "not-a-number"}
    )
    assert resp.status_code == 200
    # invalid weight should not produce calories
    assert b"Estimated Calories" not in resp.data


def test_form_preserves_fields(client):
    payload = {
        "name": "Bob",
        "age": "42",
        "weight": "82",
        "adherence": "70",
        "program": "Beginner (BG)",
    }
    resp = client.post("/", data=payload)
    assert resp.status_code == 200
    # field values should be preserved in the form HTML
    assert b'value="Bob"' in resp.data
    assert b'value="42"' in resp.data
    assert b'value="82"' in resp.data
    # adherence value should be rendered inside an <output>
    assert b">70<" in resp.data
