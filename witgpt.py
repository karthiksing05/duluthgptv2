from wit import Wit
from utils import getCounselor
from gpt import askQuestion
import pickle
import datetime

with open("witkey.pickle", "rb") as f:
    WIT_KEY = pickle.load(f)

client = Wit(WIT_KEY)

def askQuestionWit(command):

    command = command[:200]

    resp = client.message(command)

    intents = resp["intents"]

    if len(intents) == 0:
        return askQuestion(command)

    intent_name = str(intents[0]['name'])
    entities = resp['entities']

    if intent_name == "counselor":
        try:
            lastName = entities['lastName:lastName'][0]['body']
            grade = entities['grade:grade'][0]['body']
            return getCounselor(lastName, grade)
        except Exception as e:
            print(e)
            return "Sorry, you didn't specify your name and grade so I couldn't help you find your specific counselor. If you give me your name and grade, I can help you identify your counselor for you!"
    
    elif intent_name == "map":
        return askQuestion(command) + " And for more information, the link of the DHS school map is as follows:\nhttps://s3-media0.fl.yelpcdn.com/bphoto/nWc0OL7qd1k1sfqJp7W2vQ/l.jpg"

    elif not intent_name:
        return askQuestion(command)

if __name__ == "__main__":
    while True:
        query = input("Ask a Question! ")
        if query == "exit":
            exit()

        print(askQuestionWit(query))
