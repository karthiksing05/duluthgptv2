from wit import Wit
from utils import getCounselor, counselorStr
from gpt import SchoolGPT
import pickle
import datetime

with open("screener_witkey.pickle", "rb") as f:
    SCREENER_WIT_KEY = pickle.load(f)

with open("witkey.pickle", "rb") as f:
    WIT_KEY = pickle.load(f)

screenerClient = Wit(SCREENER_WIT_KEY)
client = Wit(WIT_KEY)

duluthGPT = SchoolGPT()

def askQuestionScreened(command):

    command = command[:200]

    resp = screenerClient.message(command)

    intents = resp["intents"]
    if len(intents) == 0:
        return "Sorry, I can only respond to questions related to Duluth High School. If your question is related to DHS and I've filtered it incorrectly, please try phrasing it a different way!"

    intent_conf = float(intents[0]['confidence'])
    intent_name = str(intents[0]['name'])

    if intent_name == "related" and intent_conf > 0.9:
        return _askQuestionWit(command)
    
    return "Sorry, I can only respond to questions related to Duluth High School. If your question is related to DHS and I've filtered it incorrectly, please try phrasing it a different way!"

def _askQuestionWit(command):

    command = command[:200]

    resp = client.message(command)

    intents = resp["intents"]

    if len(intents) == 0:
        return duluthGPT.askQuestion(command)

    intent_name = str(intents[0]['name'])
    entities = resp['entities']

    if intent_name == "counselor":
        # try:
        #     lastName = entities['lastName:lastName'][0]['body']
        #     grade = entities['grade:grade'][0]['body']
        #     return getCounselor(lastName, grade)
        # except Exception as e:
        #     print(e)
        #     return "Sorry, you didn't specify your name and grade so I couldn't help you find your specific counselor. If you give me your name and grade, I can help you identify your counselor for you!"
    
        return counselorStr

    elif intent_name == "map":
        return duluthGPT.askQuestion(command) + " And for more information, the link of the DHS school map is as follows:\nhttps://s3-media0.fl.yelpcdn.com/bphoto/nWc0OL7qd1k1sfqJp7W2vQ/l.jpg"
    
    else:
        return duluthGPT.askQuestion(command)

if __name__ == "__main__":
    while True:
        query = input("Ask a Question! ")
        if query == "exit":
            exit()

        print(askQuestionScreened(query))
