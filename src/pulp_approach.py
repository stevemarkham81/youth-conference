import pulp
from attendee import Attendee
from group import Group
from common import get_attendee_by_name
from objective import Objective
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def pulp_to_group(pulp_group, attendee_list: list[Attendee]):
    return Group([get_attendee_by_name(name, attendee_list) for name in pulp_group['names']])

def solve_subset(subset: list[Attendee], max_group_size, min_group_size, max_groups):
    obj_func = Objective(subset)

    youths = [a for a in obj_func.attendees]

    logging.debug(f"# Youth {len(youths)}, num_groups {max_groups}")

    # create list of all possible groups
    possible_groups = [tuple(c) for c in pulp.allcombinations(youths, max_group_size) if obj_func.screen(c, max_group_size, min_group_size)]

    logging.debug(f"Num possible groups {len(possible_groups)}")

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

    status = grouping_model.solve(pulp.PULP_CBC_CMD(msg=False))

    logging.debug(f"Status: {status}")

    if status not in [1, 2]:
        return [[]]

    logging.debug(f"The chosen groups are out of a total of {len(possible_groups)}:")
    groups = []
    for group in possible_groups:
        if x[group].value() == 1.0:
            group_attendees = [get_attendee_by_name(name, subset) for name in group]
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
        logging.debug(g['names'])
        logging.debug(f"score: {g['score']}, age range: {g['min_age']:.1f}-{g['max_age']:.1f}, has Coppell: {g['has_coppell']}, has other: {g['has_other']}")

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
            subset.remove(get_attendee_by_name(name, subset))
        found_groups.append(first_group)
    groups = solve_subset(subset, max_group_size=max_group_size, min_group_size=min_group_size, max_groups=groups_per_search)
    found_groups.extend(groups)
    return found_groups
