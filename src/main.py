import argparse
import csv
import json
import logging
import os
import random
from attendee import Attendee
from group import Group
from conference import Conference
from common import from_csv


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


def randomize_order(input_list, seed=None):
    if seed is None:
        return input_list[:]
    random.seed(seed)
    randomized_list = input_list[:]
    random.shuffle(randomized_list)
    return randomized_list

def make_groups(attendees, num_groups):
    group_size = len(attendees) // num_groups
    remainder = len(attendees) % num_groups

    groups = []
    start = 0
    for i in range(num_groups):
        end = start + (group_size + 1 if i < remainder else group_size)
        groups.append(Group(attendees[start:end]))
        start = end

    return groups


def main(json_file):
    with open(json_file, 'r') as f:
        conference = Conference.from_dict(json.load(f), json_file)

    logging.info(f"Starting conference score {conference.score()}")
    conference.optimize()
    logging.info(f"Ending conference score {conference.score()}")
    conference.show(show_groups=False)

    with open(conference.json_file, 'w') as f:
        json.dump(conference.__dict__(), f)
        


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description="Youth Conference Organizer")
    # parser.add_argument("--json_file", default='results/yw_None.json', help="Path to a JSON file, to update and optimize")
    # args = parser.parse_args()

    # main(args.json_file)

    main('results/ym_None.json')
    main('results/yw_None.json')
    main('results/ym_None.json')
    main('results/yw_None.json')
    main('results/ym_None.json')
    main('results/yw_None.json')
