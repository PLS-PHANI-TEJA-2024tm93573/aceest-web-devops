import pytest

from app.programs import programs


def test_programs_structure():
    assert isinstance(programs, dict)
    # each program should have required keys
    for name, p in programs.items():
        assert "workout" in p
        assert "diet" in p
        assert "color" in p
        assert "calorie_factor" in p
        cf = p.get("calorie_factor")
        assert isinstance(cf, (int, float))
        assert cf > 0


def test_index_get(client):
    resp = client.get("/")
    assert resp.status_code == 200
    # page title / heading present
    assert b"ACEest Functional Fitness" in resp.data


def test_post_select_program_no_weight(client):
    data = {"program": "Fat Loss (FL)"}
    resp = client.post("/", data=data)
    assert resp.status_code == 200
    assert b"Workout Plan" in resp.data
    assert b"Diet Plan" in resp.data
    # no calories estimated when weight not provided
    assert b"Estimated Calories" not in resp.data


def test_post_select_program_with_weight(client):
    # choose a program with known calorie_factor
    program = "Fat Loss (FL)"
    weight = 70
    calorie_factor = programs[program]["calorie_factor"]
    expected = int(weight * calorie_factor)

    resp = client.post("/", data={"program": program, "weight": str(weight)})
    assert resp.status_code == 200
    assert b"Workout Plan" in resp.data
    # estimated calories displayed
    assert str(expected).encode() in resp.data
    # some content from the program workout should be present
    assert b"Back Squat" in resp.data or b"Squat" in resp.data


def test_post_invalid_weight(client):
    # invalid weight should be treated as missing (no calories)
    resp = client.post("/", data={"program": "Muscle Gain (MG)", "weight": "abc"})
    assert resp.status_code == 200
    assert b"Workout Plan" in resp.data
    assert b"Estimated Calories" not in resp.data


def test_post_no_program_but_weight(client):
    # if no program selected, nothing should render for program-specific content
    resp = client.post("/", data={"weight": "75"})
    assert resp.status_code == 200
    assert b"Workout Plan" not in resp.data
    assert b"Estimated Calories" not in resp.data


def test_form_preserves_fields(client):
    payload = {
        "name": "Alice",
        "age": "30",
        "weight": "60",
        "adherence": "80",
        "program": "Beginner (BG)",
    }
    resp = client.post("/", data=payload)
    assert resp.status_code == 200
    assert b'value="Alice"' in resp.data
    assert b'value="30"' in resp.data
    assert b'value="60"' in resp.data
    # adherence is rendered inside an <output> tag
    assert b">80<" in resp.data
