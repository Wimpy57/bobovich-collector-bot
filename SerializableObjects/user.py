import json


class User:
    id: int
    debt: float
    skipped_payments: int

    def __init__(self, user_id: int, debt: float, skipped_payments: int):
        self.id = user_id
        self.debt = debt
        self.skipped_payments = skipped_payments

    def to_dict(self):
        return {
            "id": self.id,
            "debt": self.debt,
            "skipped_payments": self.skipped_payments,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["debt"],
            data["skipped_payments"],
        )

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
