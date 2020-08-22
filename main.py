from flask import Flask, render_template, request, redirect, url_for
from tinydb import TinyDB, Query
from assignment import *

db = TinyDB('planr.json')

app = Flask(__name__, template_folder="web/", static_folder="web/static/")

@app.route('/')
def index():

    tags = {
        "time_today": "25-30",
        "today_due": 4,
        "tmrw_due": 33,
        "nxt_due": 4,
        "pie_data": [20,40,60,80],
        "pie_tags": ['sadas', 'asdasd', 'Asdasd']
    }

    return render_template("index.html", **tags)

@app.route('/add_assignment', methods=['GET', 'POST'])
def newAssignment():
    if request.method == 'POST':
        assignmentName = request.form.get("name")
        className = request.form.get("class")
        typeName = request.form.get("type")
        dueDate = request.form.get("date")
        notes = request.form.get("notes")
        duration = request.form.get("duration")
        attachments = request.form.get("attachments")

        assignment = Assignment(assignmentName,className,typeName,dueDate,notes,duration,attachments)

        print(assignment.dictionary())

        db.insert(assignment.dictionary())

        return redirect(url_for("index"))
    else:
        return render_template("add_assignment.html")



if __name__ == "__main__":
    app.run()