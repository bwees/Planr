from flask import Flask, render_template, request
app = Flask(__name__, template_folder="web")

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == "__main__":
    app.run()