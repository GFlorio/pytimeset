# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Collection

from timeset.timeinterval import TimeInterval


class TimeSet:
    def __init__(self, intervals: Collection[TimeInterval]):
        valid_intervals = [x for x in intervals if not x.is_empty()]
        if len(valid_intervals) == 0:
            self.intervals = frozenset()
            return

        # Normalize the given intervals. That means merging intervals that "touch".
        sorted_intervals = sorted([
            interval for interval in valid_intervals
        ], key=lambda x: x.start)
        normalized_intervals = [sorted_intervals[0]]
        for idx in range(len(sorted_intervals)):
            current_normalized = normalized_intervals[-1]
            interval = sorted_intervals[idx]
            if interval.start <= current_normalized.end:
                start = min(current_normalized.start, interval.start)
                end = max(current_normalized.end, interval.end)
                normalized_intervals[-1] = TimeInterval(start, end)
            else:
                normalized_intervals.append(interval)

        self.intervals = frozenset(normalized_intervals)

    @classmethod
    def from_interval(cls, start: datetime, end: datetime):
        return TimeSet([TimeInterval(start, end)])

    @classmethod
    def empty(cls):
        return TimeSet([])

    def union(self, other: 'TimeSet') -> 'TimeSet':
        return TimeSet(self.intervals.union(other.intervals))

    def intersection(self, other: 'TimeSet') -> 'TimeSet':
        new_intervals = set()
        for i in self.intervals:
            for j in other.intervals:
                intersection = i.intersection(j)
                if not intersection.is_empty():
                    new_intervals.add(intersection)
        return TimeSet(new_intervals)

    def difference(self, other: 'TimeSet') -> 'TimeSet':
        # Only works if both sets are normalized
        new_intervals = set()
        for i in self.intervals:
            overlapping = [x for x in other.intervals if x.overlaps_with(i)]
            overlapping.sort(key=lambda x: x.start)

            if len(overlapping) == 0:
                new_intervals.add(i)
                continue
            if i.start < overlapping[0].start:
                new_intervals.add(TimeInterval(i.start, overlapping[0].start))
            for idx in range(len(overlapping)-1):
                this = overlapping[idx]
                nxt = overlapping[idx+1]
                new_intervals.add(TimeInterval(this.end, nxt.start))
            if overlapping[-1].end < i.end:
                new_intervals.add(TimeInterval(overlapping[-1].end, i.end))
        return TimeSet(new_intervals)

    def contains(self, moment: datetime) -> bool:
        return any(interval.contains(moment) for interval in self.intervals)

    def is_subset(self, other: 'TimeSet') -> bool:
        return all(
            any(x.is_subset(interval) for interval in other.intervals)
            for x in self.intervals
        )

    def is_empty(self) -> bool:
        return len(self.intervals) == 0

    def translate(self, by: timedelta) -> 'TimeSet':
        return TimeSet({i.translate(by) for i in self.intervals})

    def limiting_interval(self) -> TimeInterval:
        if self.is_empty():
            raise ValueError('Unspecified behavior!')
        start = min(x.start for x in self.intervals)
        end = max(x.end for x in self.intervals)
        return TimeInterval(start, end)

    def duration(self) -> timedelta:
        return sum((x.duration() for x in self.intervals), timedelta(0))

    def start(self) -> datetime:
        return min(x.start for x in self.intervals)

    def end(self) -> datetime:
        return max(x.end for x in self.intervals)

    def __eq__(self, other):
        if not isinstance(other, TimeSet):
            return False
        return self.intervals == other.intervals

    def __hash__(self):
        return hash(self.intervals)

    def __str__(self):
        return 'TimeSet {'+'; '.join([f'[{x.start}, {x.end})' for x in self.intervals])+'}'
