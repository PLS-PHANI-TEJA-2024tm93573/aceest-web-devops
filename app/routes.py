import csv
import io
from datetime import datetime
from flask import flash, redirect, url_for, request
from .models import add_client, get_clients, save_progress
from .programs import programs
from flask import Blueprint, Response, jsonify, render_template

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    selected_program = None
    workout = None
    diet = None
    name = None
    age = None
    weight = None
    adherence = None
    calories = None
    color = None
    notes = None

    if request.method == "POST":
        # Client fields
        name = request.form.get("name")
        age = request.form.get("age")
        weight = request.form.get("weight")
        adherence = request.form.get("adherence")
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
            weight_f = float(weight) if weight not in (None, "") else None
        except ValueError:
            weight_f = None
        try:
            adherence_i = int(adherence) if adherence not in (None, "") else 0
        except ValueError:
            adherence_i = 0
        client = {
            "name": name or "",
            "age": age_i,
            "weight": weight_f,
            "program": selected_program or "",
            "adherence": adherence_i,
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
        weight=weight,
        adherence=adherence,
        calories=calories,
        color=color,
        notes=notes,
        clients=clients,
    )

import csv
import io
from datetime import datetime
from flask import flash, redirect, url_for, request
from .models import add_client, get_clients, save_progress
from .programs import programs
from flask import Blueprint, Response, jsonify, render_template



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
    adherence = [c.get("adherence", 0) for c in clients]
    return jsonify({"names": names, "adherence": adherence})
