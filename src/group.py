from attendee import Attendee
import numpy as np

AGE_WEIGHT = 0
GENDER_WEIGHT = 0
UNIT_WEIGHT = 0
COPPELL_WEIGHT = 0
FRIEND_WEIGHT = 10

class Group:
    def __init__(self, attendees: list[Attendee]):
        self.attendees = attendees
    
    def __dict__(self):
        return {'attendees': [a.__dict__() for a in self.attendees]}

    @classmethod
    def from_dict(cls, data):
        attendees = [Attendee.from_dict(a) for a in data['attendees']]
        return cls(attendees)

    @property
    def has_coppell_ym(self):
        return any('Coppell' in a.unit for a in self.attendees if not a.is_female)

    @property
    def has_coppell_yw(self):
        return any('Coppell' in a.unit for a in self.attendees if a.is_female)

    @property
    def has_non_coppell_ym(self):
        return any('Coppell' not in a.unit for a in self.attendees if not a.is_female)

    @property
    def has_non_coppell_yw(self):
        return any('Coppell' not in a.unit for a in self.attendees if a.is_female)

    def score(self):
        # There are hard constraints that imply -inf score if not met
        required_groupings = [['YW70', 'YW71'],
                              ['YM75', 'YM76'],
                              ['YM12', 'YM54', 'YM62'],
                              ['YM41', 'YW49'],
        ]
        required_separation = []

        attendee_names = [a.name for a in self.attendees]

        for rg in required_groupings:
            belong = [a in attendee_names for a in rg]
            if any(belong) and not all(belong):
                return -1e9
        
        for rs in required_separation:
            belong = [a in attendee_names for a in rs]
            if sum(belong) > 1:
                return -1e9
        
        age_range = max([a.age for a in self.attendees]) - min([a.age for a in self.attendees])
        if age_range < 1.1:
            age_range = 0
        age_score = -AGE_WEIGHT*(age_range**5)

        num_boys = sum(1 for a in self.attendees if not a.is_female)
        num_girls = sum(1 for a in self.attendees if a.is_female)
        gender_score = -GENDER_WEIGHT * ((num_boys - num_girls)^2)

        units = [a.unit for a in self.attendees]
        num_units = len(np.unique(units))

        unit_score = UNIT_WEIGHT * ((COPPELL_WEIGHT * sum([self.has_coppell_ym, 
                                                           self.has_coppell_yw, 
                                                           self.has_non_coppell_ym, 
                                                           self.has_non_coppell_yw]))
                                    + num_units)

        friend_score = 0
        for a in self.attendees:
            num_buddies = sum(b in attendee_names for b in a.friends)
            if num_buddies == 1:
                friend_score += 10
            if num_buddies == 2:
                friend_score += 8
            if num_buddies == 3:
                friend_score += 6
        friend_score = FRIEND_WEIGHT * friend_score

        return age_score + gender_score + unit_score + friend_score

    def __repr__(self):
        return f"Group({sorted([a.name for a in self.attendees])})"

    def get_summary(self):
        # Show the group on one line with buddy info
        min_age = min([a.age for a in self.attendees])
        max_age = max([a.age for a in self.attendees])
        attendee_names = [a.name for a in self.attendees]
        attendee_summaries = []
        attendee_lines = []
        buddy_less = []
        for a in sorted(self.attendees, key=lambda a: a.name):
            attendee_line = f"{a.unit},{a.name},"
            attendee_summary = f"{a.name} ("
            for b in a.friends:
                if b in attendee_names:
                    attendee_summary += f"{b},"
                    attendee_line += f"{b}*,"
                elif b is None:
                    attendee_line += f","
                else:
                    attendee_line += f"{b},"
            attendee_line += f"{a.age}"
            attendee_lines.append(attendee_line)
            if not any(b in attendee_names for b in a.friends):
                buddy_less.append(a.name)
            attendee_summary += f"{a.unit[0:3]}{a.unit[-3:]})"
            attendee_summaries.append(attendee_summary)
        cm = 1 if self.has_coppell_ym else 0
        cw = 1 if self.has_coppell_yw else 0
        ncm = 1 if self.has_non_coppell_ym else 0
        ncw = 1 if self.has_non_coppell_yw else 0
        # return f"({min_age}-{max_age} {cm}{cw}{ncm}{ncw} {len(buddy_less)}) {','.join(attendee_summaries)}", len(buddy_less), attendee_lines
        return f"({min_age}-{max_age} {cm}{cw}{ncm}{ncw} {len(buddy_less)})", len(buddy_less), attendee_lines
