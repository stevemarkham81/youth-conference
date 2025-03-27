from main import from_csv

attendees = from_csv('data/input.txt')
attendee_names = [a.name for a in attendees]

for a in sorted(attendees, key=lambda a: (a.is_female, a.age)):
    a_line = f"{a.name},{a.unit},{a.age},"
    for f in a.friends:
        if f in attendee_names:
            fai = attendee_names.index(f)
            fa = attendees[fai]
            a_line += f"{fa.name} ({fa.age} {fa.unit[0:3]}{fa.unit[-3:]}),"
        else:
            a_line += ','
    for a2 in attendees:
        if a.name in a2.friends:

            a_line += f"{a2.name}({3-a2.friends.count(None)}),"
    print(a_line)
    