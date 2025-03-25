import pulp
from attendee import Attendee
from main import from_csv
from objective import Objective
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

attendees = from_csv('data/input.txt')
names = [a.name for a in attendees]

def get_attendee_by_name(name):
    idx = names.index(name)
    attendee = attendees[idx]
    return attendee

def solve_subset(subset: list[Attendee], max_group_size, min_group_size, max_groups):
    obj_func = Objective(subset)

    youths = [a for a in obj_func.attendees]

    logging.info(f"# Youth {len(youths)}, num_groups {max_groups}")

    # create list of all possible groups
    possible_groups = [tuple(c) for c in pulp.allcombinations(youths, max_group_size) if obj_func.screen(c, max_group_size, min_group_size)]

    logging.info(f"Num possible groups {len(possible_groups)}")

    # create a binary variable to state that a group setting is used
    x = pulp.LpVariable.dicts(
        "group", possible_groups, lowBound=0, upBound=1, cat=pulp.LpInteger
    )

    grouping_model = pulp.LpProblem("Youth_Conference_Grouping", pulp.LpMaximize)

    grouping_model += pulp.lpSum([obj_func.score(group) * x[group] for group in possible_groups])

    # specify the maximum number of groups
    grouping_model += (
        pulp.lpSum([x[group] for group in possible_groups]) <= max_groups,
        "Maximum_number_of_groups",
    )

    # A youth must be in one and only one group
    for youth in youths:
        grouping_model += (
            pulp.lpSum([x[group] for group in possible_groups if youth in group]) == 1,
            f"Must_seat_{youth}",
        )

    grouping_model.solve(pulp.PULP_CBC_CMD(msg=False))

    logging.info(f"The chosen groups are out of a total of {len(possible_groups)}:")
    groups = []
    for group in possible_groups:
        if x[group].value() == 1.0:
            group_attendees = [get_attendee_by_name(name) for name in group]
            ages = [a.age for a in group_attendees]
            units = [a.unit for a in group_attendees]
            has_coppell = any(["Coppell" in u for u in units])
            has_other = any(["Coppell" not in u for u in units])
            score = obj_func.score(group)
            names = [name for name in group]
            groups.append({'names': names,
                           'score': score,
                           'max_age': max(ages),
                           'min_age': min(ages),
                           'has_coppell': has_coppell,
                           'has_other': has_other})
    groups = sorted(groups, key=lambda g: g['max_age'])
    for g in groups:
        logging.info(group['names'])
        logging.info(f"score: {group['score']}, age range: {group['min_age']:.1f}-{group['max_age']:1.f}, has Coppell: {group['has_coppell']}, has other: {group['has_other']}")

    return groups

ym = sorted([a for a in attendees if not a.is_female], key=lambda a: a.age)

yym = [a for a in attendees if (not a.is_female) and (a.age<15.7)]
oym = [a for a in attendees if (not a.is_female) and (a.age>15.7)]
max_group_size = 8
min_group_size = 7
# youths = [a.name for a in yym]

yyw = [a for a in attendees if (a.is_female) and (a.age<15.7)]
oyw = [a for a in attendees if (a.is_female) and (a.age>15.7)]
# max_group_size = 7
# min_group_size = 6
# youths = [a.name for a in yyw]
# youths = [a.name for a in oyw]

total_groups = 10
groups_per_search = 5
for num_groups_found in range(total_groups - groups_per_search):
    num_to_search = round(len(ym)*groups_per_search/(total_groups-num_groups_found))
    groups = solve_subset(ym[:num_to_search], max_group_size=8, min_group_size=7, max_groups=groups_per_search)

    # The groups are sorted by max age, so group[0] has the youngest youth
    for name in groups[0]['names']:
        ym.remove(get_attendee_by_name[name])