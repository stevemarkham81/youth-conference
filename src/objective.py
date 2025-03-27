from attendee import Attendee
import numpy as np
from common import from_csv


AGE_WEIGHT = 1
GENDER_WEIGHT = 0
UNIT_WEIGHT = 1
COPPELL_WEIGHT = 1
FRIEND_WEIGHT = 3

# There are hard constraints
REQUIRED_GROUPINGS = [['YW70', 'YW71'],
                      ['YM75', 'YM76'],
                      ['YM12', 'YM54', 'YM62'],
                      ['YM41', 'YW49'],
]

REQUIRED_SEPARATIONS = []

SINGLE_BUDDY_YOUTH = [['YM1', 'YM26'],
                      ['YM12', 'YM62'],
                      ['YM13', 'YM16'],
                      ['YM24', 'YM11'],
                      ['YM26', 'YM1'],
                      ['YM28', 'YM60'],
                      ['YM29', 'YM61'],
                      ['YW24', 'YW40'],
                      ['YM39', 'YM3'],
                      ['YW42', 'YW32'],
                      ['YW62', 'YW19'],
                      ['YW70', 'YW71'],
                      ['YM79', 'YM61'],
                      ['YW71', 'YW70'],
                      ]


def has_coppell_ym(attendees):
    return any('Coppell' in a.unit for a in attendees if not a.is_female)

def has_coppell_yw(attendees):
    return any('Coppell' in a.unit for a in attendees if a.is_female)

def has_non_coppell_ym(attendees):
    return any('Coppell' not in a.unit for a in attendees if not a.is_female)

def has_non_coppell_yw(attendees):
    return any('Coppell' not in a.unit for a in attendees if a.is_female)


class Objective:
    def __init__(self, attendees):
        self.attendees = {attendee.name: attendee for attendee in attendees}
        self.single_buddy_youth = [sby for sby in SINGLE_BUDDY_YOUTH if sby[0] in self.attendees]
        self.required_groupings = [rg for rg in REQUIRED_GROUPINGS if all([y in self.attendees for y in rg])]
        self.required_separations = [rs for rs in REQUIRED_SEPARATIONS if all([y in self.attendees for y in rs])]

    def screen(self, names: list[str], max_size: int, min_size: int):

        if len(names) < min_size:
            return False
        if len(names) > max_size:
            return False

        # There are hard constraints that imply -inf score if not met
        for rg in self.required_groupings:
            belong = [n in names for n in rg]
            if any(belong) and not all(belong):
                return False
        
        for rs in self.required_separations:
            belong = [n in names for n in rs]
            if sum(belong) > 1:
                return False
        
        for sby in self.single_buddy_youth:
            if (sby[0] in names) and (not sby[1] in names):
                pass
                # return False

        ages = [self.attendees[name].age for name in names]

        age_range = max(ages) - min(ages)
        if age_range > 2:
            return False
        
        return True


    def score(self, names: list[str]):
        for rg in self.required_groupings:
            belong = [n in names for n in rg]
            if any(belong) and not all(belong):
                return -1e5
        
        for rs in self.required_separations:
            belong = [n in names for n in rs]
            if sum(belong) > 1:
                return -1e5
        
        ages = [self.attendees[name].age for name in names]
        age_range = max(ages) - min(ages)
        if age_range < 1.1:
            age_range = 0
        age_score = -AGE_WEIGHT*(age_range**5)

        attendees = [self.attendees[name] for name in names]

        num_boys = sum(1 for a in attendees if not a.is_female)
        num_girls = sum(1 for a in attendees if a.is_female)
        gender_score = -GENDER_WEIGHT * ((num_boys - num_girls)^2)

        units = [a.unit for a in attendees]
        num_units = len(np.unique(units))

        unit_score = UNIT_WEIGHT * ((COPPELL_WEIGHT * sum([has_coppell_ym(attendees), 
                                                            has_coppell_yw(attendees), 
                                                            has_non_coppell_ym(attendees), 
                                                            has_non_coppell_yw(attendees)]))
                                    + num_units)

        friend_score = 0
        for a in attendees:
            num_buddies = sum(b in names for b in a.friends)
            if num_buddies == 1:
                friend_score += 10
            if num_buddies == 2:
                friend_score += 8
            if num_buddies == 3:
                friend_score += 6
        friend_score = FRIEND_WEIGHT * friend_score

        return age_score + gender_score + unit_score + friend_score
    