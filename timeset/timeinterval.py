# -*- coding: utf-8 -*-
from datetime import datetime, timedelta


class TimeInterval:
    def __init__(self, start: datetime, end: datetime):
        if start > end:
            raise ValueError("The start of the interval must not be after the end!")
        self.start = start
        self.end = end

    def contains(self, moment: datetime) -> bool:
        return self.start <= moment < self.end

    def overlaps_with(self, other: 'TimeInterval') -> bool:
        return self.end > other.start and other.end > self.start

    def is_subset(self, other: 'TimeInterval') -> bool:
        return self.start >= other.start and self.end <= other.end

    def duration(self) -> timedelta:
        return self.end - self.start

    def is_empty(self) -> bool:
        return self.start == self.end

    def intersection(self, other: 'TimeInterval') -> 'TimeInterval':
        if not self.overlaps_with(other):
            # Return an EMPTY interval!
            return TimeInterval(self.end, self.end)
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        return TimeInterval(start, end)

    def translate(self, by: timedelta) -> 'TimeInterval':
        return TimeInterval(self.start+by, self.end+by)

    def __eq__(self, other):
        if not isinstance(other, TimeInterval):
            return False
        return self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash((self.start, self.end))

    def __str__(self):
        return f'TimeInterval [{self.start}; {self.end})'


