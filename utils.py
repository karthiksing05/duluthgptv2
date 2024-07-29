import random

import requests
from bs4 import BeautifulSoup

import datetime
import pandas as pd
import os
import re

# TODO continue updating these
SCHOOL_YEAR1 = 2024
SCHOOL_YEAR2 = 2025

def to_pascal_case(sentence):
    # Use regular expression to find all words
    words = re.findall(r'\b\w+\b', sentence)
    
    # Create a mapping of words to their PascalCase version
    pascal_case_words = {word: word.capitalize() for word in words}
    
    # Replace each word in the original sentence with its PascalCase version
    pascal_case_sentence = sentence
    for word, pascal_word in pascal_case_words.items():
        pascal_case_sentence = pascal_case_sentence.replace(word, pascal_word, 1)
    
    return pascal_case_sentence

counselorStr = """* For 9th Grade:
    - If your last name STARTS WITH a letter between 'A' and 'L' (inclusive), your counselor is Mr. Terron Miller.
        * Contact Mr. Terron Miller at: Terron.Miller@gcpsk12.org.
    - If your last name STARTS WITH a letter between 'M' and 'Z', your counselor is Mrs. Brigette McClammey.
        * Contact Mrs. Brigette McClammey at: brigette.mcclammey@gcpsk12.org.

* For Grades Beyond 9th:
    - If your last name STARTS WITH 'A' and goes up to 'CH', your counselor is Mrs. Delinda Coffey.
        * Contact Mrs. Delinda Coffey at: Delinda.Coffey@gcpsk12.org.
    - If your last name STARTS WITH 'CI' and goes up to 'GO', your counselor is Ms. Lindsey Ingwersen.
        * Contact Ms. Lindsey Ingwersen at: Lindsey.Ingwersen@gcpsk12.org.
    - If your last name STARTS WITH 'GR' and goes up to 'LI', your counselor is Mrs. Kim Tepker.
        * Contact Mrs. Kim Tepker at: Kim.Tepker@gcpsk12.org.
    - If your last name STARTS WITH 'LO' and goes up to 'OR', your counselor is Mr. Ryan Lilly.
        * Contact Mr. Ryan Lilly at: Ryan.Lilly@gcpsk12.org.
    - If your last name STARTS WITH 'OS' and goes up to 'SH', your counselor is Mrs. Mary Catherine Smoke.
        * Contact Mrs. Mary Catherine Smoke at: marycatherine.smoke@gcpsk12.org.
    - If your last name STARTS WITH 'SI' and goes up to 'Z', your counselor is Mrs. Lauren Smith.
        * Contact Mrs. Lauren Smith at: Lauren.Smith@gcpsk12.org.
"""

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

    df = pd.read_csv("data/GeneralCalendar.csv")

    for i, row in df.iterrows():
        row = list(row)
        if datetime.datetime.strptime(row[0].split("-")[-1], "%Y/%m/%d") < datetime.datetime.now():
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

    with open("docs/dynamic/Calendar.txt", "w") as f:
        f.write(finalStr)

def updateSportingEvents():

    """
    Updates sporting events every time (by accessing the web)
    
    Need to figure out the smartest way to call this (currently takes ~40 seconds)!
    """

    endPath = "docs/dynamic/SportsGames.txt"
    templateStr = "Duluth High School will have their next {sport} game, a {homeAway} game, on {date} at {time}, against {opponent} at {venue}.\n\n"

    finalStr = "Below are the sporting events for Duluth High School's 2024 - 2025 school year! If someone asks about a sporting event or game, use this information to answer!\n\n"

    urls = [
        "https://www.duluthathletics.com/sport/baseball/boys",
        "https://www.duluthathletics.com/sport/basketball/boys",
        "https://www.duluthathletics.com/sport/cross%20country/boys",
        "https://www.duluthathletics.com/sport/football/boys",
        "https://www.duluthathletics.com/sport/golf/boys",
        "https://www.duluthathletics.com/sport/lacrosse/boys",
        "https://www.duluthathletics.com/sport/soccer/boys",
        "https://www.duluthathletics.com/sport/swimming%20and%20diving/boys",
        "https://www.duluthathletics.com/sport/tennis/boys",
        "https://www.duluthathletics.com/sport/track%20and%20field/coed",
        "https://www.duluthathletics.com/sport/basketball/girls",
        "https://www.duluthathletics.com/sport/cross%20country/girls",
        "https://www.duluthathletics.com/sport/flag%20football/girls",
        "https://www.duluthathletics.com/sport/golf/girls",
        "https://www.duluthathletics.com/sport/lacrosse/girls",
        "https://www.duluthathletics.com/sport/soccer/girls",
        "https://www.duluthathletics.com/sport/softball/girls",
        "https://www.duluthathletics.com/sport/swimming%20and%20diving/girls",
        "https://www.duluthathletics.com/sport/tennis/girls",
        "https://www.duluthathletics.com/sport/volleyball/girls"
    ]

    directory = "data\\sports\\"

    globalDf = pd.DataFrame(columns=["Sport", "Date", "Time", "Location", "Opponent", "Venue"])

    for url in urls:
        df = _getSportingEvent(url, directory)
        globalDf = pd.concat([globalDf, df], ignore_index=True)

    for _, row in globalDf.iterrows():
        row = list(row)
        finalStr += templateStr.format(
            sport=row[0],
            date=row[1],
            time=row[2],
            homeAway=row[3],
            opponent=row[4],
            venue=row[5]
        )

    with open(endPath, "w") as f:
        f.write(finalStr)

def _getSportingEvent(url, directory):
    """
    Helper function to get the excel file for a singular sporting event

    this will only get the NEXT most recent event so we have to do the least amount of processing!
    """

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    sport = soup.find_all('div', attrs={'class':'cd-main-content'})[0].find_all('div', attrs={'class':'col-md-12'})[0].find_all('div', attrs={'class':'col-md-12'})[0].text
    sport = to_pascal_case(sport).strip()

    data = pd.DataFrame(columns=["Sport", "Date", "Time", "Location", "Opponent", "Venue"])

    findTable = soup.find_all('table', attrs={'id':'schedule-table'})
    if len(findTable) == 0:
        return data
    
    table = findTable[0]

    row = table.find('tbody').find_all('tr')
    if len(row) == 0:
        return data

    row = row[1]
    # Datetime related stuff
    try:
        dateHome = row.find('td', attrs={'data-label':'DATE'}).text

        homeAway = to_pascal_case(dateHome[:4])

        if int(dateHome[4:6]) > 7:
            date = dateHome[4:] + "/2024"
        else:
            date = dateHome[4:] + "/2025"

        time = row.find('td', attrs={'data-label':'TIME'}).text.strip()
        opponent = to_pascal_case(row.find('td', attrs={'data-label':'OPPONENT'}).text)
        venue = to_pascal_case(row.find('td', attrs={'data-label':'FACILITY'}).text)

        data.loc[len(data)] = [sport, date, time, homeAway, opponent, venue]
    except AttributeError:
        pass

    return data

if __name__ == "__main__":
    updateSportingEvents()