from dataclasses import dataclass

from datetime import datetime


@dataclass
class Event:

    event_id: int

    timestamp: datetime

    value: int

    def to_tuple(self):

        return (
            self.event_id,
            self.timestamp,
            self.value
        )

    def to_json(self):

        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "value": self.value
        }