import logging

class Attendee:
    def __init__(self, name: str, age: int, unit: str, is_female: bool, friends: list[str | None]):
        self.name = name
        self.age = age
        self.unit = unit
        self.is_female = is_female
        self.friends = friends
    
    def __dict__(self):
        return {'name': self.name,
                'age': self.age,
                'unit': self.unit,
                'is_female': self.is_female,
                'friends': [f if f is not None else '' for f in self.friends],
                }
    
    @classmethod
    def from_dict(cls, data):
        friends = [None if f == '' else f for f in data['friends']]
        return cls(data['name'], data['age'], data['unit'], data['is_female'], friends)

    
    def add_friend(self, friend_name: str):
        if not friend_name:
            return
        
        try:
            idx = self.friends.index(None)
        except Exception as e:
            logging.error(f"This attendee ({self.name}) already has three friends")
        
        self.friends[idx] = friend_name
    
    def __repr__(self):
        return f"Attendee(name={self.name})"
