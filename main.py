from flask import Flask, render_template, request
from tinydb import TinyDB, Query

db = TinyDB('planr.json')

app = Flask(__name__, template_folder="web/", static_folder="web/static/")

@app.route('/')
def hello_world():

    tags = {
        "today_due": 5,
        "tmrw_due": 4,
        "nxt_week_due": 33,
        "time_today": 25-30
    }

    return render_template("index.html", **tags)

if __name__ == "__main__":
    app.run()