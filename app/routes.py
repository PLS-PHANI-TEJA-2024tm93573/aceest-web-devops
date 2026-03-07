from flask import Blueprint, render_template, request
from .programs import programs

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():

    selected_program = None
    workout = None
    diet = None

    if request.method == "POST":

        selected_program = request.form.get("program")

        if selected_program in programs:

            workout = programs[selected_program]["workout"]
            diet = programs[selected_program]["diet"]

    return render_template(
        "index.html",
        programs=programs,
        selected_program=selected_program,
        workout=workout,
        diet=diet
    )