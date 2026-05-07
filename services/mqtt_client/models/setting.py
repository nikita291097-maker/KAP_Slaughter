from dataclasses import dataclass


@dataclass
class Setting:

    setting_id: int

    value: float | int | str | bool

    timestamp: str | None = None