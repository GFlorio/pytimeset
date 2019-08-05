# -*- coding: utf-8 -*-
from datetime import datetime
from random import uniform, randrange
from typing import List

from timeset import TimeInterval, TimeSet


def make_moments(number: int, start: datetime, end: datetime) -> List[datetime]:
    diff = end-start
    return sorted([
        start+uniform(0, 1)*diff for _ in range(number)
    ])


def make_intervals(number: int, start: datetime, end: datetime) -> List[TimeInterval]:
    diff = end-start
    intervals = []
    for _ in range(number):
        s = uniform(0, 1)
        e = uniform(s, 1)
        intervals.append(TimeInterval(start+s*diff, start+e*diff))
    return intervals


def make_sets(number: int, start: datetime, end: datetime, max_components=5) -> List[TimeSet]:
    return [
        TimeSet(make_intervals(randrange(1, max_components+1), start, end))
        for _ in range(number)
    ]
