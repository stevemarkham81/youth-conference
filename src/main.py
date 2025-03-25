import argparse
import csv
import json
import logging
import os
import random
from attendee import Attendee
from group import Group
from conference import Conference

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def from_csv(csv_file_path):
    logging.info(f'Processing {csv_file_path}')
    attendees = []
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            friends = [row['Buddy1'] if row['Buddy1'] else None,
                       row['Buddy2'] if row['Buddy2'] else None,
                       row['Buddy3'] if row['Buddy3'] else None]
            attendee = Attendee(name=row['Participant Code'],
                                age=float(row['Age']),
                                unit=row["Participant's Ward"],
                                is_female='W' in row['Participant Code'],
                                friends=friends)
            attendees.append(attendee)
            
    return attendees


def randomize_order(input_list, seed=0):
    random.seed(seed)
    randomized_list = input_list[:]
    random.shuffle(randomized_list)
    return randomized_list

def make_groups(attendees, num_groups, seed=0):
    attendees = randomize_order(attendees, seed)

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
    parser.add_argument("--csv_file", default='data/input.txt', help="Path to the attendee info file")
    parser.add_argument("--num_groups", default=10, help="Number of groups to create")
    args = parser.parse_args()

    attendees = from_csv(args.csv_file)
    # valid_seeds = [152323, 194302, 340188, 547448, 607579, 694989, 787695, 806047, 807688, 998956, 1362808, 1500691]
    # valid_seeds = [547448, 607579, 787695] 
    valid_seeds = [152323, 194302, 340188, 547448, 607579, 694989, 787695, 806047, 807688, 998956, 1362808, 1500691] + list(range(1000))
    for seed in valid_seeds:
        conference_json_file = f"results/conference_{seed}.json"
        if os.path.exists(conference_json_file):
            with open(conference_json_file, 'r') as f:
                conference = Conference.from_dict(json.load(f))
        else:
            groups = make_groups(attendees, args.num_groups, seed)
            conference = Conference(groups)

        logging.info(f"Seed {seed} has starting conference score {conference.score()}")
        conference.optimize()
        logging.info(f"Seed {seed} has ending conference score {conference.score()}")
        conference.show(show_groups=False)

        with open(conference_json_file, 'w') as f:
            json.dump(conference.__dict__(), f)
        


if __name__ == '__main__':
    main()
