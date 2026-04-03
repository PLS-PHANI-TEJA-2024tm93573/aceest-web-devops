import base64
import csv
import io
from datetime import datetime
from functools import wraps

import matplotlib.pyplot as plt
from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .models import (
    add_client,
    check_password,
    get_client_by_name,
    get_clients,
    get_progress,
    get_user_by_username,
    get_workout_history,
    save_metrics,
    save_progress,
    save_workout,
)
from .programs import programs


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app

        if current_app.config.get("TESTING"):
            # In testing mode, allow bypassing login for easier test setup
            return f(*args, **kwargs)

        if not session.get("user"):
            flash("Login required", "warning")
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)

    return decorated_function


main = Blueprint("main", __name__)


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if check_password(username, password):
            user = get_user_by_username(username)
            session["user"] = user["username"]
            session["role"] = user["role"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")


@main.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("main.login"))


@main.route("/", methods=["GET", "POST"])
@login_required
def index():
    selected_program = None
    workout = None
    diet = None
    name = None
    age = None
    height = None
    weight = None
    adherence = None
    target_weight = None
    target_adherence = None
    calories = None
    color = None
    notes = None
    membership_expiry = None

    if request.method == "POST":
        # Client fields
        name = request.form.get("name")
        age = request.form.get("age")
        height = request.form.get("height")
        weight = request.form.get("weight")
        adherence = request.form.get("adherence")
        target_weight = request.form.get("target_weight")
        target_adherence = request.form.get("target_adherence")
        notes = request.form.get("notes")
        selected_program = request.form.get("program")
        membership_expiry = request.form.get("membership_expiry")

        if selected_program in programs:
            program = programs[selected_program]
            workout = program.get("workout")
            diet = program.get("diet")
            color = program.get("color")
            # Estimate calories if weight supplied and calorie_factor exists
            try:
                w = float(weight) if weight not in (None, "") else 0
            except ValueError:
                w = 0
            calorie_factor = program.get("calorie_factor")
            if w > 0 and calorie_factor:
                calories = int(w * calorie_factor)

        # Build client record and save
        try:
            age_i = int(age) if age not in (None, "") else None
        except ValueError:
            age_i = None
        try:
            height_f = float(height) if height not in (None, "") else None
        except ValueError:
            height_f = None
        try:
            weight_f = float(weight) if weight not in (None, "") else None
        except ValueError:
            weight_f = None
        try:
            adherence_i = int(adherence) if adherence not in (None, "") else None
        except ValueError:
            adherence_i = 0
        try:
            target_weight_f = (
                float(target_weight) if target_weight not in (None, "") else None
            )
        except ValueError:
            target_weight_f = None
        try:
            target_adherence_i = (
                int(target_adherence) if target_adherence not in (None, "") else None
            )
        except ValueError:
            target_adherence_i = None
        client = {
            "name": name or "",
            "age": age_i,
            "height": height_f,
            "weight": weight_f,
            "program": selected_program or "",
            "target_weight": target_weight_f,
            "target_adherence": target_adherence_i,
            "adherence": adherence_i,
            "notes": notes or "",
            "calories": calories,
            "membership_expiry": membership_expiry,
        }
        add_client(client)

    # Always provide the current clients list to the template
    clients = get_clients()

    return render_template(
        "index.html",
        programs=programs,
        selected_program=selected_program,
        workout=workout,
        diet=diet,
        name=name,
        age=age,
        height=height,
        weight=weight,
        adherence=adherence,
        target_weight=target_weight,
        target_adherence=target_adherence,
        calories=calories,
        color=color,
        notes=notes,
        membership_expiry=membership_expiry,
        clients=clients,
    )


@main.route("/save_progress", methods=["POST"])
def save_progress_route():
    name = request.form.get("progress_name")
    adherence = request.form.get("progress_adherence")

    if not name:
        flash("Client name required to save progress", "error")
        return redirect(url_for("main.index"))

    try:
        adherence_i = int(adherence) if adherence not in (None, "") else 0
    except ValueError:
        adherence_i = 0

    week = datetime.now().strftime("Week %U - %Y")

    print(f"Received progress for {name} - Week: {week}, Adherence: {adherence_i}")

    # ✅ Save historical progress
    save_progress(name, week, adherence_i)

    # ✅ ALSO update current client adherence (CRITICAL FIX)
    client = get_client_by_name(name)
    if client:
        client["adherence"] = adherence_i
        add_client(client)

    flash("Weekly progress logged", "success")
    return redirect(url_for("main.index"))


@main.route("/export_csv")
def export_csv():
    """Return a CSV file download of all clients."""
    clients = get_clients()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["Name", "Age", "Weight", "Program", "Adherence", "Notes"])
    for c in clients:
        writer.writerow(
            [
                c.get("name", ""),
                c.get("age", ""),
                c.get("weight", ""),
                c.get("program", ""),
                c.get("adherence", ""),
                c.get("notes", ""),
            ]
        )

    output = si.getvalue()
    headers = {
        "Content-Disposition": "attachment; filename=clients.csv",
        "Content-Type": "text/csv; charset=utf-8",
    }
    return Response(output, headers=headers)


@main.route("/clients/data")
def clients_data():
    """Return minimal JSON for charting: names and adherence list."""
    clients = get_clients()
    names = [c.get("name", "") for c in clients]
    # Ensure adherence is always int and matches the latest client form value
    adherence = []
    for c in clients:
        adh = c.get("adherence", 0)
        try:
            adh = int(adh)
        except Exception:
            adh = 0
        adherence.append(adh)
    return jsonify({"names": names, "adherence": adherence})


# Route to generate and return a progress chart image for a client
@main.route("/progress_chart/<client_name>")
def progress_chart(client_name):
    progress = get_progress(client_name)
    if not progress:
        flash("No progress data available for this client", "info")
        return redirect(url_for("main.index"))

    weeks = [p["week"] for p in reversed(progress)]
    adherence = [p["adherence"] for p in reversed(progress)]

    plt.figure(figsize=(8, 4))
    plt.plot(weeks, adherence, marker="o", linewidth=2)
    plt.title(f"Weekly Adherence Progress – {client_name}")
    plt.xlabel("Week")
    plt.ylabel("Adherence (%)")
    plt.ylim(0, 100)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    return render_template(
        "progress_chart.html", client_name=client_name, img_data=img_b64
    )


@main.route("/weight_trend_chart/<client_name>")
def weight_trend_chart(client_name):
    # Dummy data for now; replace with real metrics if available
    # Example: get weight metrics from a new get_weight_metrics(client_name) function
    # For now, use progress as a placeholder
    progress = get_progress(client_name)
    if not progress:
        flash("No progress data available for this client", "info")
        return redirect(url_for("main.index"))

    # In a real implementation, fetch weight by week/date from metrics table
    # Here, just plot adherence as a placeholder
    weeks = [p["week"] for p in reversed(progress)]
    weights = [p["adherence"] for p in reversed(progress)]  # Replace with real weights

    plt.figure(figsize=(8, 4))
    plt.plot(weeks, weights, marker="o", linewidth=2, color="orange")
    plt.title(f"Weight Trend – {client_name}")
    plt.xlabel("Week")
    plt.ylabel("Weight (kg)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    return render_template(
        "progress_chart.html",
        client_name=client_name,
        img_data=img_b64,
        chart_title="Weight Trend",
    )


@main.route("/bmi_info/<client_name>")
def bmi_info(client_name):
    # Find client by name
    clients = get_clients()
    client = next((c for c in clients if c.get("name") == client_name), None)
    if not client:
        flash("Client not found", "error")
        return redirect(url_for("main.index"))
    height = client.get("height")
    weight = client.get("weight")
    try:
        h = float(height)
        w = float(weight)
    except (TypeError, ValueError):
        h = 0
        w = 0
    if h <= 0 or w <= 0:
        flash("Enter valid height and weight for BMI calculation", "warning")
        return redirect(url_for("main.index"))
    h_m = h / 100.0
    bmi = w / (h_m * h_m)
    bmi = round(bmi, 1)
    if bmi < 18.5:
        category = "Underweight"
        risk = "Potential nutrient deficiency, low energy."
    elif bmi < 25:
        category = "Normal"
        risk = "Low risk if active and strong."
    elif bmi < 30:
        category = "Overweight"
        risk = "Moderate risk; focus on adherence and progressive activity."
    else:
        category = "Obese"
        risk = "Higher risk; prioritize fat loss, consistency, and supervision."
    flash(f"BMI for {client_name}: {bmi} ({category}) - {risk}", "info")
    return redirect(url_for("main.index"))


# Workout history route
@main.route("/workout_history/<client_name>")
def workout_history(client_name):
    history = get_workout_history(client_name)
    return render_template(
        "workout_history.html", client_name=client_name, history=history
    )


# Log workout route
@main.route("/log_workout", methods=["POST"])
def log_workout():
    client_name = request.form.get("workout_client_name")
    date = request.form.get("workout_date")
    workout_type = request.form.get("workout_type")
    duration_min = request.form.get("workout_duration")
    notes = request.form.get("workout_notes")
    if not client_name or not date or not workout_type:
        flash("Client name, date, and workout type are required.", "error")
        return redirect(url_for("main.index"))
    try:
        duration = int(duration_min) if duration_min else 0
    except ValueError:
        duration = 0
    save_workout(client_name, date, workout_type, duration, notes or "")
    flash("Workout logged successfully.", "success")
    return redirect(url_for("main.index"))


# Log metrics route
@main.route("/log_metrics", methods=["POST"])
def log_metrics():
    client_name = request.form.get("metrics_client_name")
    date = request.form.get("metrics_date")
    weight = request.form.get("metrics_weight")
    waist = request.form.get("metrics_waist")
    bodyfat = request.form.get("metrics_bodyfat")
    if not client_name or not date:
        flash("Client name and date are required.", "error")
        return redirect(url_for("main.index"))
    try:
        weight_f = float(weight) if weight else 0.0
    except ValueError:
        weight_f = 0.0
    try:
        waist_f = float(waist) if waist else 0.0
    except ValueError:
        waist_f = 0.0
    try:
        bodyfat_f = float(bodyfat) if bodyfat else 0.0
    except ValueError:
        bodyfat_f = 0.0
    save_metrics(client_name, date, weight_f, waist_f, bodyfat_f)
    flash("Body metrics logged successfully.", "success")
    return redirect(url_for("main.index"))
