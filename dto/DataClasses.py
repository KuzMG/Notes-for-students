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


@dataclass
class Pair:
    discipline: str
    occupation: str
    nameOfTheTeacher: str
    numberOfCabinet: str


@dataclass
class ParityOfWeek:
    parityOfWeek: bool
    pair: List[Pair]


@dataclass
class PairNumber:
    pairNumber: str
    parityOfWeek: List[ParityOfWeek]


@dataclass
class DaysOfWeek:
    daysOfWeek: str
    pairNumber: List[PairNumber]


@dataclass
class Schedule:
    group: str
    dayOfWeek: List[DaysOfWeek]
