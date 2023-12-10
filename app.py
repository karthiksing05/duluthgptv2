from flask import Flask, render_template, request
from witgpt import askQuestionWit

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    return askQuestionWit(msg).replace('\n', '<br>')

if __name__ == "__main__":
    app.run()