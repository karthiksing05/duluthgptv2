"""
TBD:
[ ] get emails for all teachers and stuff and add to schedules.txt
"""

import pandas as pd

df = pd.read_csv("archive\\TeacherEmails.csv", index_col=[0])
print(df.head())

TEMPLATE_STR = """{name} works at Duluth High School. You can contact {name} at {email}.\n"""

textStr = ""

for i, row in df.iterrows():
    if i == 0:
        continue
    name = list(row)[0]
    try:
        lastName = name.split(", ")[0]
        name = name.split(", ")[1] + " " + name.split(", ")[0]
    except:
        lastName = name.split(" ")[1]
    email = list(row)[2]

    textStr += TEMPLATE_STR.format(name=name, lastName=lastName, email=email)

with open("test.txt", "w+") as f:
    f.write(textStr)