from flask import Flask, render_template, request, redirect, url_for
from tinydb import TinyDB, Query, where
from assignment import *
from flask_table import Table, Col, ButtonCol
from datetime import datetime, timedelta

assignmentdb = TinyDB('db/planr.json')
activitiesdb = TinyDB('db/act.json')
freetimesdb = TinyDB('db/free.json')

app = Flask(__name__, template_folder="web/", static_folder="web/static/")


def getAssignmentByDate(dateIn):
    return assignmentdb.search(where("dueDate")==dateIn)
    
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

def widgetData():
    current_date = datetime.now().strftime("%Y-%m-%d")
    tomorrow_date = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")

    assignment = Query()
    dueToday = assignmentdb.search(assignment.dueDate==current_date)

    dueToday = [x for x in dueToday if x["status"] != Status.complete]

    freeMins = 0
    for freetime in freetimesdb.all():
        freeMins += int(freetime["duration"])

    activityMins = 0
    for activity in activitiesdb.all():
        activityMins += activity["duration"]

    workMins = 0
    for assignment in dueToday:
        workMins += assignment["duration"]
    
    assignment = Query()
    dueTomorrow = assignmentdb.search(assignment.dueDate==tomorrow_date)
    dueTomorrow = [x for x in dueTomorrow if x["status"] != Status.complete]

    nextStart = next_weekday(datetime.now(), 0)
    dueNextWeek = []

    for single_date in (nextStart + timedelta(n) for n in range(5)):
        single_date = single_date.strftime("%Y-%m-%d")
        dueNextWeek += assignmentdb.search(assignment.dueDate==single_date)

    return dueToday, dueTomorrow, dueNextWeek, freeMins, activityMins, workMins

def calcRings(freeTime,workTime,activityTime):
    if activityTime+workTime>freeTime:
        return [1], ["Time Used"]
    else:
        return [workTime,activityTime,freeTime-activityTime-workTime], ["Work Time", "Activity Time", "Free Time"]

def htmlString(tags):
    htmlString = ""

    for tag in tags:
        if tag == "free Time":
            htmlString += '<div class="chart-note mr-0 d-block"><span class="dot dot--blue"></span><span>free Time</span></div>'
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
    dueDate = Col("Due Date")
    duration = Col("Duration")
    status = Col('Status')
    edit = ButtonCol('Edit','edit_assignment', url_kwargs=dict(uuid="uuid"), td_html_attrs = {'class': 'btn-primary text-white text-bold'})
    view = ButtonCol('View','view_assignment', url_kwargs=dict(uuid="uuid"), td_html_attrs = {'class': 'btn-secondary text-white text-bold'})
    done = ButtonCol('Mark As Done', 'mark_done', url_kwargs=dict(uuid="uuid"), td_html_attrs = {'class': 'btn-primary-green text-white text-bold'})


class freeTimeTable(Table):
    classes = ['table', 'table-data2']
    name = Col('Name')
    duration = Col('Duration')
    time = Col('Time')
    delete = ButtonCol('Delete','del_freetime', url_kwargs=dict(uuid="uuid"), td_html_attrs = {'class': 'btn-primary text-white text-bold'})
    

class AssignmentTableHome(Table):
    assignmentName = Col('Name')
    className = Col('Class')
    dueDate = Col("Due Date")
    edit = ButtonCol('View','view_assignment', url_kwargs=dict(uuid="uuid"), td_html_attrs = {'class': 'btn-secondary'})
    

def getBarColor(status):
    if status == Status.inProgress:
        return "au-task__item--primary"
    if status == Status.notStarted:
        return "au-task__item--danger"
    if status == Status.complete:
        return "au-task__item--complete"


@app.route('/')
def index():

    dueToday, dueTomorrow, dueNextWeek, freeMins, activityMins, workMins = widgetData()

    print(calcRings(freeMins, workMins, activityMins))

    tags = {
        "time_today": str(freeMins)+"-"+str(freeMins+10)+" mins",
        "today_due": len(dueToday),
        "tmrw_due": len(dueTomorrow),
        "nxt_due": len(dueNextWeek),
        "pie_data": calcRings(freeMins, workMins, activityMins)[0],
        "pie_tags": calcRings(freeMins, workMins, activityMins)[1],
        "pie_dots": htmlString(calcRings(freeMins, workMins, activityMins)[1]),
        "assignment_table": AssignmentTableHome(dueToday, html_attrs = {'class': 'table table-borderless table-striped table-earning'}).__html__()
    }

    return render_template("index.html", **tags)


@app.route("/assignments", methods=['GET', 'POST'])
def assignment_list(action = None):
    assignments = assignmentdb.search(where("status")!= 1)

    items = [assignmentFromDictionary(x) for x in assignments]
    items = [x for x in items if x.status != Status.complete]

    table = AssignmentTable(items, html_attrs = {'class': 'table table-data2'})

    return render_template("assignment_list.html", assignment_table=table.__html__())


@app.route("/activities", methods=['GET', 'POST'])
def activity_list(action = None):
    
    activities = activitiesdb.all()

    items = [freeTimeFromDictionary(x) for x in activities]

    table = freeTimeTable(items, html_attrs = {'class': 'table table-data2'})

    return render_template("activity_list.html", freetime_table=table.__html__())

@app.route("/free_times", methods=['GET', 'POST'])
def free_time_list(action = None):
    
    freetimes = freetimesdb.all()

    items = [freeTimeFromDictionary(x) for x in freetimes]

    table = freeTimeTable(items, html_attrs = {'class': 'table table-data2'})

    return render_template("freetime_list.html", freetime_table=table.__html__())


@app.route('/add_freetime', methods=['GET', 'POST'])
def newfreeTime():
    if request.method == 'POST':
        name = request.form.get("name")
        duration = request.form.get("duration")
        time = request.form.get("time")
        
        if duration == None: 
            duration = 20

        freetime = freeTime(name, duration, time)
        freetimesdb.insert(freetime.dictionary())

        return redirect("/free_times")
    else:
        return render_template("add_freetime.html")


@app.route('/add_activity', methods=['GET', 'POST'])
def newActivity():
    if request.method == 'POST':
        name = request.form.get("name")
        duration = request.form.get("duration")
        time = request.form.get("time")
        
        if duration == None: 
            duration = 20

        activity = freeTime(name, duration, time)
        activitiesdb.insert(activity.dictionary())

        return redirect("/activities")
    else:
        return render_template("add_activity.html")



@app.route('/add_assignment', methods=['GET', 'POST'])
def newAssignment():
    if request.method == 'POST':
        assignmentName = request.form.get("name")
        className = request.form.get("class")
        typeName = request.form.get("type")
        dueDate = request.form.get("date")
        notes = request.form.get("notes")
        duration = request.form.get("duration")
        if duration == None: 
            duration = 20
        attachments = request.form.get("attachments")

        assignment = Assignment(assignmentName,className,typeName,dueDate,notes,duration,attachments)
        assignmentdb.insert(assignment.dictionary())

        return redirect("/assignments")
    else:
        return render_template("add_assignment.html")

@app.route('/edit_assignment/<string:uuid>', methods=['GET', 'POST'])
def edit_assignment(uuid):

    if request.method == "POST" and request.form.get("name") != None:

        assignment = assignmentdb.search(where("uuid") == uuid)[0]

        assignmentdb.remove(where('uuid') == uuid)

        assignmentName = request.form.get("name")
        className = request.form.get("class")
        typeName = request.form.get("type")
        dueDate = request.form.get("date")
        notes = request.form.get("notes")
        duration = request.form.get("duration")
        
        if duration == None: 
            duration = 20
        attachments = request.form.get("attachments")

        assignment = Assignment(assignmentName,className,typeName,dueDate,notes,duration,attachments, status=assignment["status"], uuid=assignment["uuid"])
        assignmentdb.insert(assignment.dictionary())

        return redirect("/view_assignment/"+uuid)
    else:
        assignment = Query()
        result = assignmentdb.search(assignment.uuid == uuid)[0]

        print(result)

        tags = {
            "name": result["assignmentName"],
            "class": result["className"],
            "type": result["typeName"],
            "length": result["duration"],
            "notes": result["notes"],
            "date": result["dueDate"]
        }

        return render_template("edit_assignment.html", **tags)

@app.route('/view_assignment/<string:uuid>', methods=['GET', 'POST'])
def view_assignment(uuid):

    assignment = assignmentdb.search(where("uuid") == uuid)[0]

    tags = {
        "name": assignment["assignmentName"],
        "class": assignment["className"],
        "type": assignment["typeName"],
        "status": assignment["status"],
        "length": assignment["duration"],
        "notes": assignment["notes"],
        "date": assignment["dueDate"],
        "uuid": assignment["uuid"],
        "bar_color": getBarColor(assignment["status"])
    }

    return render_template("assignment_detail.html", **tags)

@app.route('/del_worktime/<string:uuid>', methods=['GET', 'POST'])
def del_freetime(uuid):    
    freetimesdb.remove(where('uuid') == uuid)

    return redirect(request.referrer)

@app.route('/del_activity/<string:uuid>', methods=['GET', 'POST'])
def del_activity(uuid):    
    activitiesdb.remove(where('uuid') == uuid)

    return redirect(request.referrer)

@app.route('/mark_done/<string:uuid>', methods=['GET', 'POST'])
def mark_done(uuid):
    assignment = Query()
    
    assignmentdb.update({"status": Status.complete}, assignment.uuid == uuid)

    return redirect(request.referrer)

if __name__ == "__main__":
    app.run()