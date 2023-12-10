from wit import Wit
from utils import getCounselor
from gpt import askQuestion
import pickle
import datetime

with open("witkey.pickle", "rb") as f:
    WIT_KEY = pickle.load(f)

client = Wit(WIT_KEY)

def askQuestionWit(command):
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

    # elif intent_name == "events":
    #     return "Please use the following link to view all school events at Duluth High School for your convenience: LINK GOES HERE"
    #     print(entities)
    #     dtRange = (datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=1))
    #     try:
    #         entity = entities["wit$datetime:datetime"][0]
    #         if "from" in entity and "to" in entity:
    #             fromTime = entity["from"]["value"]
    #             toTime = entity["to"]["value"]
    #             dtRange = (witStrToDT(fromTime), witStrToDT(toTime))
    #         else:
    #             startDT = witStrToDT(entity["value"])
    #             endDT = startDT
    #             tDelta = entity["grain"]
    #             if tDelta == "year":
    #                 endDT += datetime.timedelta(days=365)
    #             elif tDelta == "month":
    #                 endDT += datetime.timedelta(days=30)
    #             elif tDelta == "week":
    #                 endDT += datetime.timedelta(days=7)
    #             elif tDelta == "day":
    #                 endDT += datetime.timedelta(days=0.99)
    #             else:
    #                 # just increment like an hr for all start times
    #                 endDT += datetime.timedelta(hours=1)
    #             dtRange = (startDT, endDT)
    #     except:
    #         pass
    #     return listEvents(dtRange)
    
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
