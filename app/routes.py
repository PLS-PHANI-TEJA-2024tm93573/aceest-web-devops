
import base64
import csv
import io
from datetime import datetime

import matplotlib.pyplot as plt
from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from .models import add_client, get_clients, get_progress, save_progress
from .programs import programs

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
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
        # adherence_i is not used; adherence is passed as string or None and not needed here
        try:
            target_weight_f = float(target_weight) if target_weight not in (None, "") else None
        except ValueError:
            target_weight_f = None
        try:
            target_adherence_i = int(target_adherence) if target_adherence not in (None, "") else None
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
            "notes": notes or "",
            "calories": calories,
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
    save_progress(name, week, adherence_i)
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
        "progress_chart.html", client_name=client_name, img_data=img_b64, chart_title="Weight Trend"
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
