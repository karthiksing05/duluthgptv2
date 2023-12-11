import random

import datetime
import pandas as pd

def _pickRandomPrompt(name, email):
    prompts = [
        "Based on the information you've provided, your counselor is {name}. You can contact {name} by the following email: {email}.",
        "Your counselor is {name}, and you can contact them at {email}.",
        "Since you've given me your name and grade level, I'm able to tell that your counselor is {name}. Feel free to reach out to them with any questions at {email}."
    ]

    return random.choice(prompts).format(name=name, email=email)

def getCounselor(lastName, grade):

    try:
        grade = int(grade[0:2])

    except:

        grade = str(grade)
        grade = grade.lower()

        grade = grade[:-2]

        if grade[0] == "f":
            grade = 9
        elif grade[0] == "n":
            grade = 9
        else:
            grade = 10

    grade = int(grade)

    if grade < 9:
        return "LOL You're not a high schooler! To find your counselor in grades below 9-12, check your school website. As an AI Model for DHS, I'm not trained on any other schools' data."

    lastName = str(lastName)
    lastName = lastName.lower()

    if grade == 9:
        if "a" <= lastName[0] and lastName[0] <= "l":
            return _pickRandomPrompt("Mr. Terron Miller", "Terron.Miller@gcpsk12.org")
        else:
            return _pickRandomPrompt("Mrs. Brigette McClammey", "brigette.mcclammey@gcpsk12.org")
    else:
        if "a" <= lastName[0] and lastName[0:2] <= "ch":
            return _pickRandomPrompt("Mrs. Delinda Coffey", "Delinda.Coffey@gcpsk12.org")
        if "ci" <= lastName[0:2] and lastName[0:2] <= "go":
            return _pickRandomPrompt("Ms. Lindsey Ingwersen", "Lindsey.Ingwersen@gcpsk12.org")
        if "gr" <= lastName[0:2] and lastName[0:2] <= "li":
            return _pickRandomPrompt("Mrs. Kim Tepker", "Kim.Tepker@gcpsk12.org")
        if "lo" <= lastName[0:2] and lastName[0:2] <= "or":
            return _pickRandomPrompt("Mr. Ryan Lilly", "Ryan.Lilly@gcpsk12.org")
        if "os" <= lastName[0:2] and lastName[0:2] <= "sh":
            return _pickRandomPrompt("Mrs. Mary Catherine Smoke", "marycatherine.smoke@gcpsk12.org")
        if "si" <= lastName[0:2] and lastName[0] <= "z":
            return _pickRandomPrompt("Mrs. Lauren Smith", "Lauren.Smith@gcpsk12.org")

"""
Get the "next activity of that type" and only use those in the spreadsheet

GENIUS, can infinitely scale this!
"""

def updateCalendarEvents():

    df = pd.read_csv("data\Calendar.csv")

    for i, row in df.iterrows():
        row = list(row)
        if datetime.datetime.strptime(row[0].split("-")[-1], "%m/%d/%Y") < datetime.datetime.now():
            df = df.drop(i, axis="index")
        else:
            break

    events = []
    for i, row in df.iterrows():
        row = list(row)
        if row[1].split(" vs")[0] in events:
            df = df.drop(i, axis="index")
        else:
            events.append(row[1].split(" vs")[0])

    finalStr = f"Today is {datetime.datetime.now().strftime('%m/%d/%Y')}.\n\n"

    templateStr = "Duluth High School has {name} {dateStr} {timeStr}{locationStr}."

    for i, row in df.iterrows():
        row = list(row)
        name = row[1]

        if "(F)" in name:
            name.replace

        dateStr = row[0]
        if "-" in dateStr:
            dateStr = f"from {dateStr.split('-')[0]} to {dateStr.split('-')[1]}"
        else:
            dateStr = f"on {dateStr}"
        timeStr = ""
        if str(row[2]) != "nan":
            timeStr += f"starting at {row[2]} "
        if str(row[2]) != "nan" and str(row[3]) != "nan":
            timeStr += "and "
        if str(row[3]) != "nan":
            timeStr += f"ending at {row[3]} "
        locationStr = "at "
        locationStr += (str(row[4]) if str(row[4]) != "nan" else "Duluth High School")
        finalStr += templateStr.format(
            name=name,
            dateStr=dateStr,
            timeStr=timeStr,
            locationStr=locationStr
        )
        finalStr += "\n\n"

    with open("docs\Calendar.txt", "w") as f:
        f.write(finalStr)