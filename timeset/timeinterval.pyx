# -*- coding: utf-8 -*-
#cython: language_level=3
from datetime import datetime, timedelta

from .interval cimport Interval

cdef class TimeInterval:
    cdef Interval interval

    def __init__(self, start: datetime, end: datetime):
        self.interval = Interval(start.timestamp(), end.timestamp())

    @staticmethod
    cdef TimeInterval from_interval(Interval interval):
        cdef TimeInterval ti = TimeInterval.__new__(TimeInterval)
        ti.interval = interval
        return ti

    cpdef bint contains(self, moment: datetime):
        return self.interval.contains(moment.timestamp())

    cpdef bint overlaps_with(self, TimeInterval other):
        return self.interval.overlaps_with(other.interval)

    cpdef bint is_subset(self, TimeInterval other):
        return self.interval.is_subset(other.interval)

    cpdef duration(self):
        return timedelta(seconds=self.interval.duration())

    cpdef bint is_empty(self):
        return self.interval.is_empty()

    cpdef TimeInterval intersection(self, TimeInterval other):
        cdef Interval new_int = self.interval.intersection(other.interval)
        return TimeInterval.from_interval(new_int)

    cpdef TimeInterval translate(self, _by):
        cdef Interval new_int = self.interval.translate(_by.total_seconds())
        return TimeInterval.from_interval(new_int)

    @property
    def start(self):
        return datetime.fromtimestamp(self.interval.start)

    @property
    def end(self):
        return datetime.fromtimestamp(self.interval.end)

    def __eq__(self, other):
        if not isinstance(other, TimeInterval):
            return False
        return self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash((self.start, self.end))

    def __str__(self):
        return f'TimeInterval [{self.start}; {self.end})'
