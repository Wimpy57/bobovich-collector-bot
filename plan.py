import json
from typing import List

from user import User


class Plan:
    id: int
    from_currency: str
    to_currency: str
    users: List[User]
    frequency: int
    duration: int

    def __init__(self,plan_id: int, from_currency: str, to_currency: str, users: List[User], frequency: int, duration: int):
        self.id = plan_id
        self.from_currency = from_currency
        self.to_currency = to_currency
        self.users = users
        self.frequency = frequency
        self.duration = duration


    def to_dict(self):
        return {
            "id": self.id,
            "from_currency": self.from_currency,
            "to_currency": self.to_currency,
            "users": self.users,
            "frequency": self.frequency,
            "duration": self.duration
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, data):
        users = []
        for user in data["users"]:
            users.append(User.from_dict(user))

        return cls(
            data["id"],
            data["from_currency"],
            data["to_currency"],
            users,
            data["frequency"],
            data["duration"]
        )