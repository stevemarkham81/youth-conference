import pulp
import json
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

    status = grouping_model.solve()

    logging.info(f"Status: {status}")

    if status not in [1, 2]:
        return [[]]

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
        logging.info(g['names'])
        logging.info(f"score: {g['score']}, age range: {g['min_age']:.1f}-{g['max_age']:.1f}, has Coppell: {g['has_coppell']}, has other: {g['has_other']}")

    return groups

def iterate_by_groups(subset, total_groups, groups_per_search, youngest_first=True):
    min_group_size = len(subset) // total_groups
    max_group_size = min_group_size
    if min_group_size * total_groups < len(subset):
        max_group_size += 1

    found_groups = []
    for num_groups_found in range(total_groups - groups_per_search):
        num_to_search = round(len(subset)*groups_per_search/(total_groups-num_groups_found))

        if youngest_first:
            groups = solve_subset(subset[:num_to_search], max_group_size=max_group_size, min_group_size=min_group_size, max_groups=groups_per_search)
            # The groups are sorted by max age, so group[0] has the youngest youth
            first_group = groups[0]
        else:
            groups = solve_subset(subset[-num_to_search:], max_group_size=max_group_size, min_group_size=min_group_size, max_groups=groups_per_search)
            first_group = groups[-1]

        if not first_group:
            logging.error("Did not solve correctly")
            return [{'error': 'Did not solve correctly', 'found_groups': found_groups}]

        for name in first_group['names']:
            subset.remove(get_attendee_by_name(name))
        found_groups.append(first_group)
    groups = solve_subset(subset, max_group_size=max_group_size, min_group_size=min_group_size, max_groups=groups_per_search)
    found_groups.extend(groups)
    return found_groups


total_groups = 10
groups_per_search = 5

ym = sorted([a for a in attendees if not a.is_female], key=lambda a: a.age)
ym_groups_youngest_first = iterate_by_groups(ym, total_groups, groups_per_search, True)
with open('results/ym_y.json', 'w') as f:
    json.dump(ym_groups_youngest_first, f)

if False:
    yw = sorted([a for a in attendees if a.is_female], key=lambda a: a.age)
    yw_groups_youngest_first = iterate_by_groups(yw, total_groups, groups_per_search, True)
    with open('results/yw_y.json', 'w') as f:
        json.dump(yw_groups_youngest_first, f)

    yw = sorted([a for a in attendees if a.is_female], key=lambda a: a.age)
    yw_groups_oldest_first = iterate_by_groups(yw, total_groups, groups_per_search, False)
    with open('results/yw_o.json', 'w') as f:
        json.dump(yw_groups_oldest_first, f)


    ym = sorted([a for a in attendees if not a.is_female], key=lambda a: a.age)
    ym_groups_oldest_first = iterate_by_groups(ym, total_groups, groups_per_search, False)
    with open('results/ym_o.json', 'w') as f:
        json.dump(ym_groups_oldest_first, f)

