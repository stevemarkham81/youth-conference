from attendee import Attendee
from group import Group
from copy import deepcopy
from common import get_attendee_by_name
import json
from pulp_approach import pulp_to_group, solve_subset
import logging
import numpy as np
import datetime
import random

MAX_FAILED_TRIES = 10
MEAN_WEIGHT = 1
MIN_WEIGHT = 0


class Conference:
    def __init__(self, groups, json_file):
        self.groups = sorted(groups, key=lambda g: np.mean([a.age for a in g.attendees]))
        self.json_file = json_file
    
    def __dict__(self):
        return {'groups': [g.__dict__() for g in self.groups]}

    @classmethod
    def from_dict(cls, data, conference_json_file):
        groups = [Group.from_dict(g) for g in data['groups']]
        return cls(groups, conference_json_file)
    
    @classmethod
    def from_pulp_json(cls, json_file, attendees_list, conference_json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
        groups = []
        for pulp_group in data:
            groups.append(Group([get_attendee_by_name(name, attendees_list) for name in pulp_group['names']]))
        return cls(groups, conference_json_file)

    @property
    def num_attendees(self):
        return sum(g.size for g in self.groups)

    @staticmethod
    def _flatten_groups(groups: list[Group]) -> list[Attendee]:
        """Flatten the list of groups into a single list of attendees."""
        return [a for g in groups for a in g.attendees]

    def score(self) -> float:
        """
        A conference's score is the lowest group score plus the median score times some weighting factor
        """
        group_scores = [g.score() for g in self.groups]
        return (MIN_WEIGHT * min(group_scores)) + (MEAN_WEIGHT * np.mean(group_scores))
    
    def swap(self, g1, a1, g2, a2):
        self.groups[g1].attendees[a1], self.groups[g2].attendees[a2] = self.groups[g2].attendees[a2], self.groups[g1].attendees[a1]
    
    def try_swap(self, g1, a1, g2, a2, cached_scores):
        if g1 not in cached_scores:
            cached_scores[g1] = {}
        if a1 not in cached_scores[g1]:
            cached_scores[g1][a1] = {}
        if g2 not in cached_scores[g1][a1]:
            cached_scores[g1][a1][g2] = {}
        if a2 in cached_scores[g1][a1][g2]:
            return cached_scores[g1][a1][g2][a2], cached_scores

        test_conference = Conference.from_dict(self.__dict__())
        test_conference.swap(g1, a1, g2, a2)
        cached_scores[g1][a1][g2][a2] = test_conference.score() - self.score()

        return cached_scores[g1][a1][g2][a2], cached_scores

    def get_best_swap(self, good_enough=100, cached_scores=None):
        if cached_scores is None:
            cached_scores = {}
        best_g1 = 0
        best_a1 = 0
        best_g2 = 0
        best_a2 = 0
        best_score = 0

        for g1 in range(len(self.groups)):
            for a1 in range(len(self.groups[g1].attendees)):
                for g2 in range(len(self.groups)):
                    if g2 <= g1:
                        continue
                    for a2 in range(len(self.groups[g2].attendees)):
                        score, cached_scores = self.try_swap(g1, a1, g2, a2, cached_scores)
                        if score > best_score:
                            best_g1 = g1
                            best_a1 = a1
                            best_g2 = g2
                            best_a2 = a2
                            best_score = score
                        if best_score > good_enough:
                            return best_g1, best_a1, best_g2, best_a2, best_score, cached_scores
        return best_g1, best_a1, best_g2, best_a2, best_score, cached_scores

    @staticmethod
    def update_cached_scores(cached_scores, swapped_g1, swapped_g2):
        if swapped_g1 in cached_scores:
            cached_scores[swapped_g1] = {}
        if swapped_g2 in cached_scores:
            cached_scores[swapped_g2] = {}
        for g in cached_scores:
            for a in cached_scores[g]:
                if swapped_g1 in cached_scores[g][a]:
                    cached_scores[g][a][swapped_g1] = {}
                if swapped_g2 in cached_scores[g][a]:
                    cached_scores[g][a][swapped_g2] = {}

    def improve_by_swap(self, i, best_score, cached_scores):
        best_g1, best_a1, best_g2, best_a2, best_score, cached_scores = self.get_best_swap(good_enough=best_score,
                                                                                               cached_scores=cached_scores)
        if best_score > 0:
            logging.debug(f"Swapping {best_g1}/{best_a1} ({self.groups[best_g1].attendees[best_a1].name}) " + \
                        f"with {best_g2}/{best_a2} ({self.groups[best_g2].attendees[best_a2].name}), +{best_score}")
            self.swap(best_g1, best_a1, best_g2, best_a2)
            self.update_cached_scores(cached_scores, best_g1, best_g2)
            logging.debug(f'Score is {self.score()} after {i+1} swaps')
            return True, cached_scores
        else:
            logging.warning(f"No more good swaps after {i} swaps")
            return False, cached_scores
    
    def pulp_to_group(pulp_group, attendees: list[Attendee]):
        pass

    def improve_by_pulp(self, i, best_score, cached_scores):
        max_groups = 3

        start = i%(len(self.groups)+1-max_groups)
        groups_to_dissolve = list(range(start, start+max_groups))
        max_group_size = max([len(self.groups[ig].attendees) for ig in groups_to_dissolve])
        min_group_size = min([len(self.groups[ig].attendees) for ig in groups_to_dissolve])
        subset = [a for i_group in groups_to_dissolve for a in self.groups[i_group].attendees]

        pre_score = self.score()
        found_groups = solve_subset(subset, max_group_size, min_group_size, max_groups)
        if not found_groups or not found_groups[0]:
            return False, cached_scores
        
        test_conference = Conference.from_dict(self.__dict__(), self.json_file)
        for idx, i_group in enumerate(groups_to_dissolve):
            new_group = pulp_to_group(found_groups[idx], subset)
            test_conference.groups[i_group] = new_group
        post_score = test_conference.score()
        
        if post_score > pre_score:
            self.groups = sorted(test_conference.groups, key=lambda g: np.mean([a.age for a in g.attendees]))
            return True, cached_scores

        return False, cached_scores

    def try_to_improve(self, i, best_score, cached_scores):
        """
        Do "one" thing to try to make the conference better
        """
        return self.improve_by_pulp(i, best_score, cached_scores)

    def optimize(self, max_failed_tries=MAX_FAILED_TRIES):
        """
        Trying swapping two youth. If it increases the score, keep the swap and try again, up to 100 times
        """
        cached_scores = None
        best_score = 2000
        last_time = datetime.datetime.now()
        num_failed_tries = 0
        i = 0
        while num_failed_tries < MAX_FAILED_TRIES:
            if (datetime.datetime.now() - last_time).seconds > 60:
                last_time = datetime.datetime.now()
                logging.info(f"Try {i+1} score={self.score()}")
            
            improved, cached_scores = self.try_to_improve(i, best_score, cached_scores)
            i += 1
            if not improved:
                logging.info(f"Failed to improve after {i} tries")
                num_failed_tries += 1
                # return
            else:
                logging.info(f"New score after {i+1} tries: {self.score()}.  Saving conference to {self.json_file}")
                with open(self.json_file, 'w') as f:
                    json.dump(self.__dict__(), f)
    
    def show(self, show_groups=True):
        bless = 0
        for idx, g in enumerate(self.groups):
            g_txt, n_bless, attendee_lines = g.get_summary()
            if show_groups:
                print(f"Group {idx+1}\t{g_txt}")
                for al in attendee_lines:
                    print(al)
            bless += n_bless
        print(f"{self.score():.0f}, {bless} buddy-less attendees")
