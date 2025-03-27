import csv
import logging
from attendee import Attendee

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
