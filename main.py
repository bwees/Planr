from flask import Flask, render_template, request
from tinydb import TinyDB, Query

db = TinyDB('planr.json')

app = Flask(__name__, template_folder="web/", static_folder="web/static/")

@app.route('/')
def index():

    tags = {
        "time_today": "25-30",
        "today_due": 4,
        "tmrw_due": 33,
        "nxt_due": 4
    }

    return render_template("index.html", **tags)

@app.route('/new', methods=['POST'])
def new():
    print(request.form["name"])


if __name__ == "__main__":
    app.run()