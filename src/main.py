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


def main():
    parser = argparse.ArgumentParser(description="Youth Conference Organizer")
    parser.add_argument("--csv_file", default='data/input_ym_only_age_constraints.txt', help="Path to the attendee info file")
    parser.add_argument("--num_groups", default=10, help="Number of groups to create")
    args = parser.parse_args()

    orig_attendees = from_csv(args.csv_file)
    # valid_seeds = [152323, 194302, 340188, 547448, 607579, 694989, 787695, 806047, 807688, 998956, 1362808, 1500691]
    # valid_seeds = [547448, 607579, 787695] 
    # valid_seeds = [152323, 194302, 340188, 547448, 607579, 694989, 787695, 806047, 807688, 998956, 1362808, 1500691] + list(range(1000))
    valid_seeds = [None]
    for seed in valid_seeds:
        attendees = randomize_order(orig_attendees, seed)
        conference_json_file = f"results/conference_{seed}.json"
        if os.path.exists(conference_json_file):
            with open(conference_json_file, 'r') as f:
                conference = Conference.from_dict(json.load(f), conference_json_file)
        else:
            groups = make_groups(attendees, args.num_groups)
            conference = Conference(groups, conference_json_file)

        logging.info(f"Seed {seed} has starting conference score {conference.score()}")
        conference.optimize()
        logging.info(f"Seed {seed} has ending conference score {conference.score()}")
        conference.show(show_groups=False)

        with open(conference_json_file, 'w') as f:
            json.dump(conference.__dict__(), f)
        


if __name__ == '__main__':
    main()
