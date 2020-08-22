from flask import Flask, render_template, request, redirect, url_for
from tinydb import TinyDB, Query, where
from assignment import *
from flask_table import Table, Col
from datetime import datetime

db = TinyDB('planr.json')

app = Flask(__name__, template_folder="web/", static_folder="web/static/")


def getAssignmentByDate(dateIn):
    return db.search(where("dueDate")==dateIn)
    

def widgetData():
    current_date = datetime.now().strftime("%Y-%m-%d")
    tomorrow_date = (datetime.date.today()+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    assignment = Query()
    dueToday = db.search(assignment.date==current_date)

    dueToday = [dueToday.remove(x) for x in dueToday if x["status"] == Status.complete]

    totalMinsToday = 0
    for assignment in dueToday:
        totalMinsToday+=assignment["duration"]
    
    dueTomorrow = db.search(assignment.date==tomorrow_date)
    dueTomorrow = [dueTomorrow.remove(x) for x in dueTomorrow if x["status"] == Status.complete]
    
    return dueToday, dueTomorrow, totalMinsToday


def calcRings(totalTime,activityTime,workTime):
    if activityTime+workTime>totalTime:
        return [1], ["Time Used"]
    else:
        return [workTime,activityTime,totalTime-activityTime-workTime], ["Work Time", "Activity Time", "Free Time"]


def htmlString(tags):
    htmlString = ""

    for tag in tags:
        if tag == "Work Time":
            htmlString += '<div class="chart-note mr-0 d-block"><span class="dot dot--blue"></span><span>Work Time</span></div>'
        if tag == "Activity Time":
            htmlString+= '<div class="chart-note mr-0 d-block"><span class="dot dot--red"></span><span>Activity Time</span></div>'
        if tag == "Free Time":
            htmlString+= '<div class="chart-note mr-0 d-block"><span class="dot dot--green"></span><span>Free Time</span></div>'
        if tag == "Time Used":
            htmlString += '<div class="chart-note mr-0 d-block"><span class="dot dot--blue"></span><span>Used Time</span></div>'

    return htmlString


class AssignmentTable(Table):
    classes = ['table', 'table-data2']
    assignmentName = Col('Name')
    typeName = Col('Type')
    className = Col('Class')
    status = Col('Status')


@app.route('/')
def index():

    tags = {
        "time_today": "25-30",
        "today_due": 4,
        "tmrw_due": 33,
        "nxt_due": 4,
        "pie_data": calcRings(60, 30, 10)[0],
        "pie_tags": calcRings(60, 30, 10)[1],
        "pie_dots": htmlString(calcRings(60, 30, 10)[1])
    }

    print(tags["pie_dots"])

    return render_template("index.html", **tags)


@app.route("/assignments")
def assignment_list():
    assignments = db.search(where("status")!= 1)

    items = [assignmentFromDictionary(x) for x in assignments]

    table = AssignmentTable(items)

    return render_template("assignment_list.html", assignment_table=table.__html__())


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
        db.insert(assignment.dictionary())

        return redirect("/assignments")
    else:
        return render_template("add_assignment.html")


if __name__ == "__main__":
    app.run()