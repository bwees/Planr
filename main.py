from flask import Flask, render_template, request
from tinydb import TinyDB, Query

db = TinyDB('planr.json')

app = Flask(__name__, template_folder="web")

@app.route('/')
def hello_world():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()