from dataclasses import dataclass
from typing import List


@dataclass
class Location:
    location: str
    courses: List[str]


@dataclass
class Institute:
    institute: str
    location: list[Location]


@dataclass
class ScheduleXls:
    qualification: str
    institutes: List[Institute]


