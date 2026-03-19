from flask import Blueprint, render_template, request

from .programs import programs

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

    if request.method == "POST":

        # Client fields
        name = request.form.get("name")
        age = request.form.get("age")
        weight = request.form.get("weight")
        adherence = request.form.get("adherence")

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
    )
