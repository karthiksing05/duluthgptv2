"""
TBD:
[x] turn schedule into a text file and mess around with formatting to make it work
[ ] train GPT properly on calendar events
[ ] add all other items from eclass home page under a resources section
[ ] GET THE VOICE OF THE STUDENTS! have a review page!!!

Notes on schedule:
- ITC for department meaning?
- figure out how to efficiently rename classes
"""

import pandas as pd
import datetime

df = pd.read_csv("Calendar.csv")

"""
default location is Duluth High School

date str can either be on XYZ or from X to Y
"""

finalStr = f"Today is {datetime.datetime.now().strftime('%m/%d/%Y')}"

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

with open("Calendar.txt", "w+") as f:
    f.write(finalStr)