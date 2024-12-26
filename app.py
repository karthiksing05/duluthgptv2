from flask import Flask, render_template, request
from witgpt import askQuestionScreened
import redis
import os
import datetime

app = Flask(__name__)

# r = redis.Redis(
#     host='redis-12355.c325.us-east-1-4.ec2.cloud.redislabs.com',
#     port=12355,
#     password=os.getenv("REDIS_PASSWD")
# )

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    msg = request.form.get("msg")
    resp = askQuestionScreened(msg).replace('\n', '<br>')
    # exchangeId = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
    # r.hset(f"userExchange-{exchangeId}", mapping={
    #     'input':msg,
    #     'output':resp
    # })
    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0')