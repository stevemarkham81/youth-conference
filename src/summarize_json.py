import json
from pulp_approach import from_csv, get_attendee_by_name
from group import Group

json_file = 'results/conference_None.json'
attendees = from_csv('data/input.txt')
names = [a.name for a in attendees]

with open(json_file, 'r') as f:
    data = json.load(f)

a=1

for idx, json_group in enumerate(sorted(data, key=lambda g: g['max_age'])):
    group = Group([get_attendee_by_name(name) for name in json_group['names']])
    g_txt, n_bless, attendee_lines = group.get_summary()
    print(f"Group {idx+1}\t{g_txt}")
    for al in attendee_lines:
        print(al)

