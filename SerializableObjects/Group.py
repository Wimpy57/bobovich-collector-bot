import json
from typing import List

from SerializableObjects.plan import Plan


class Group:
    group_id: int
    plans: List[Plan]

    def __init__(self, group_id: int, plans: List[Plan]):
        self.id = group_id
        self.plans = plans

    def to_dict(self):
        return {
            "id": self.id,
            "plans": self.plans,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["plans"],
        )

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)