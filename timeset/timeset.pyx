# -*- coding: utf-8 -*-
#cython: language_level=3
#cython: auto_pickle=False

cdef extern from "stdlib.h":
    ctypedef void const_void "const void"
    void qsort(void *base, int nmemb, int size,
               int(*compar)(const_void *, const_void *)) nogil

from datetime import datetime, timedelta
from typing import Collection, FrozenSet

from cpython.mem cimport PyMem_Malloc, PyMem_Free

ctypedef struct Interval:
    double start
    double end

cdef bint contains(Interval self, double element):
    return self.start <= element < self.end

cdef bint overlaps(Interval self, Interval other):
    return self.end > other.start and other.end > self.start

cdef bint is_subset(Interval self, Interval other):
    if Interval_is_empty(self):
        return True
    return self.start >= other.start and self.end <= other.end

cdef double duration(Interval self):
    return self.end - self.start

cdef bint Interval_is_empty(Interval self):
    return duration(self) < 0.0001  # Avoid float arithmetic problems

cdef Interval Interval_intersection(Interval self, Interval other):
    cdef double start, end
    if not overlaps(self, other):
        # Return an EMPTY interval!
        return empty
    start = max(self.start, other.start)
    end = min(self.end, other.end)
    return Interval(start, end)

cdef bint equals(Interval self, Interval other):
    return self.start == other.start and self.end == other.end

cdef Interval translate(Interval self, double _by):
    return Interval(self.start+_by, self.end+_by)

cdef Interval empty = Interval(0.0, 0.0)


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
        return contains(self.interval, moment.timestamp())

    cpdef bint overlaps_with(self, TimeInterval other):
        return overlaps(self.interval, other.interval)

    cpdef bint is_subset(self, TimeInterval other):
        return is_subset(self.interval, other.interval)

    cpdef duration(self):
        return timedelta(seconds=duration(self.interval))

    cpdef bint is_empty(self):
        return Interval_is_empty(self.interval)

    cpdef TimeInterval intersection(self, TimeInterval other):
        cdef Interval new_int = Interval_intersection(self.interval, other.interval)
        return TimeInterval.from_interval(new_int)

    cpdef TimeInterval translate(self, _by):
        cdef Interval new_int = translate(self.interval, _by.total_seconds())
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

    def __repr__(self):
        return str(self)


ctypedef struct IntervalList:
    Interval interval
    IntervalList* next


cdef void free_list(IntervalList* head):
    if head is NULL:
        return
    free_list(head.next)
    PyMem_Free(head)

cdef int mycmp(const_void * pa, const_void * pb):
    cdef Interval a = (<Interval *>pa)[0]
    cdef Interval b = (<Interval *>pb)[0]
    if a.start < b.start:
        return -1
    elif a.start > b.start:
        return 1
    else:
        return 0

cdef class TimeSet:
    cdef IntervalList* _intervals
    cdef frozenset _timeintervals

    def __init__(self, intervals: Collection[TimeInterval]):
        cdef int i, size
        cdef empty = 0
        cdef Interval* temp_array
        cdef TimeInterval ti
        self._timeintervals = frozenset()

        size = len(intervals)
        try:
            temp_array = <Interval*>PyMem_Malloc(size*sizeof(Interval))
            if temp_array is NULL:
                raise MemoryError()
            for i in range(size):
                ti = intervals[i]
                if ti.is_empty():
                    empty += 1
                    continue
                temp_array[i-empty] = ti.interval
            size = size-empty
            if size == 0:
                self._intervals = NULL
                return
            self._normalize(temp_array, size)
        finally:
            PyMem_Free(temp_array)

    cdef void _initialize_list(self, Interval interval):
        self._intervals = <IntervalList*>PyMem_Malloc(sizeof(IntervalList))
        if not self._intervals:
            raise MemoryError()
        self._intervals[0].interval = Interval(interval.start, interval.end)
        self._intervals[0].next = NULL

    cdef void _normalize(self, Interval* intervals, int size):
        # Normalization: merge intervals that "touch".
        cdef IntervalList* tail
        cdef Interval ref
        qsort(intervals, size, sizeof(Interval), mycmp)
        self._initialize_list(intervals[0])
        tail = self._intervals

        for i in range(1, size):
            ref = intervals[i]
            if ref.start <= tail.interval.end:
                tail.interval.end = max(tail.interval.end, ref.end)
            elif not Interval_is_empty(ref):
                tail.next = <IntervalList*>PyMem_Malloc(sizeof(IntervalList))
                tail.next.interval.start = ref.start
                tail.next.interval.end = ref.end
                tail = tail.next
                tail.next = NULL

    @staticmethod
    cdef TimeSet from_list(IntervalList* _list):
        cdef int size = 0
        cdef int i
        cdef IntervalList* _iter = _list
        cdef Interval* temp_array
        cdef TimeSet ts = TimeSet.__new__(TimeSet)
        ts._timeintervals = frozenset()

        # Calculate size
        while _iter is not NULL:
            size += 1
            _iter = _iter.next

        _iter = _list  # Reset the iterator to the start of the list

        try:
            # Now build the temporary array that will be passed to "normalize"
            temp_array = <Interval*>PyMem_Malloc(size*sizeof(Interval))
            for i in range(size):
                temp_array[i] = _iter.interval
                _iter = _iter.next
            ts._normalize(temp_array, size)
        finally:
            PyMem_Free(temp_array)
        return ts

    @classmethod
    def from_interval(cls, start: datetime, end: datetime):
        return TimeSet([TimeInterval(start, end)])

    @classmethod
    def empty(cls):
        return empty_set

    cpdef TimeSet union(self, TimeSet other):
        cdef IntervalList* full_list = self._intervals
        cdef IntervalList* _iter = full_list
        cdef TimeSet ts
        if self.is_empty():
            return other
        while _iter.next is not NULL:
            _iter = _iter.next
        _iter.next = other._intervals
        ts = TimeSet.from_list(full_list)
        _iter.next = NULL  # Return self to previous condition!
        return ts

    cpdef TimeSet intersection(self, TimeSet other):
        cdef IntervalList* iter1 = self._intervals
        cdef IntervalList* iter2
        # Start the list with a dummy head
        cdef IntervalList new_list = IntervalList(empty, NULL)
        cdef IntervalList* tail = &new_list
        cdef Interval _intersection
        cdef TimeSet ts

        if self.is_empty() or other.is_empty():
            return empty_set

        while iter1 is not NULL:
            iter2 = other._intervals
            while iter2 is not NULL:
                _intersection = Interval_intersection(iter1.interval, iter2.interval)
                if not Interval_is_empty(_intersection):
                    tail.next = <IntervalList*>PyMem_Malloc(sizeof(IntervalList))
                    tail.next.interval = _intersection
                    tail = tail.next
                    tail.next = NULL
                iter2 = iter2.next
            iter1 = iter1.next
        ts = TimeSet.from_list(new_list.next)
        return ts

    cpdef TimeSet difference(self, TimeSet other):
        #This only works if both sets are normalized
        cdef IntervalList* iter1 = self._intervals
        cdef IntervalList* iter2
        # Start the list with a dummy head
        cdef IntervalList new_list = IntervalList(empty, NULL)
        cdef IntervalList* tail = &new_list
        cdef double next_start

        if other.is_empty():
            return self
        while iter1 is not NULL:
            next_start = iter1.interval.start
            iter2 = other._intervals
            while iter2 is not NULL:
                if iter2.interval.end <= next_start:
                    iter2 = iter2.next
                    continue
                if iter2.interval.start >= iter1.interval.end:
                    break
                if iter2.interval.start > next_start:
                    tail.next = <IntervalList*>PyMem_Malloc(sizeof(IntervalList))
                    tail.next.interval.start = next_start
                    tail.next.interval.end = iter2.interval.start
                    tail = tail.next
                    tail.next = NULL
                next_start = iter2.interval.end
                iter2 = iter2.next
            if next_start < iter1.interval.end:
                tail.next = <IntervalList*>PyMem_Malloc(sizeof(IntervalList))
                tail.next.interval.start = next_start
                tail.next.interval.end = iter1.interval.end
                tail = tail.next
                tail.next = NULL
            iter1 = iter1.next
        return TimeSet.from_list(new_list.next)

    def contains(self, moment: datetime) -> bool:
        cdef IntervalList* _iter = self._intervals
        cdef double _moment = moment.timestamp()
        while _iter is not NULL:
            if contains(_iter.interval, _moment):
                return True
            _iter = _iter.next
        return False

    cpdef bint is_subset(self, TimeSet other):
        cdef IntervalList* iter1 = self._intervals
        cdef IntervalList* iter2

        if self.is_empty():
            return True
        while iter1 is not NULL:
            iter2 = other._intervals
            while iter2 is not NULL:
                if is_subset(iter1.interval, iter2.interval):
                    break
                iter2 = iter2.next
            if iter2 is NULL:
                # If the previous loop wasn't broken, this interval isn't contained
                return False
            iter1 = iter1.next
        return True

    cpdef bint is_empty(self):
        return self._intervals is NULL or Interval_is_empty(self._intervals.interval)

    def limiting_interval(self) -> TimeInterval:
        if self.is_empty():
            raise ValueError('Unspecified behavior!')
        return TimeInterval(self.start(), self.end())

    def duration(self) -> timedelta:
        cdef double _duration = 0.0
        cdef IntervalList* _iter = self._intervals
        while _iter is not NULL:
            _duration += duration(_iter.interval)
            _iter = _iter.next
        return timedelta(seconds=_duration)

    def start(self) -> datetime:
        if self.is_empty():
            raise ValueError('Unspecified behavior!')
        return datetime.fromtimestamp(self._intervals.interval.start)

    def end(self) -> datetime:
        cdef IntervalList* last = self._intervals
        if self.is_empty():
            raise ValueError('Unspecified behavior!')
        while last.next is not NULL:
            last = last.next
        return datetime.fromtimestamp(last.interval.end)

    @property
    def intervals(self) -> FrozenSet[TimeInterval]:
        if self.is_empty():
            return frozenset()
        if len(self._timeintervals):
            return self._timeintervals
        cdef set intervals = set()
        cdef IntervalList* _iter = self._intervals
        while _iter is not NULL:
            intervals.add(TimeInterval.from_interval(_iter.interval))
            _iter = _iter.next
        self._timeintervals = frozenset(intervals)
        return self._timeintervals

    def __eq__(self, TimeSet other):
        cdef IntervalList* iter1 = self._intervals
        cdef IntervalList* iter2
        if not isinstance(other, TimeSet):
            return False
        iter2 = other._intervals
        while iter1 is not NULL:
            if iter2 is NULL:
                return False
            if not equals(iter1.interval, iter2.interval):
                return False
            iter1 = iter1.next
            iter2 = iter2.next
        return iter2 is NULL

    def __hash__(self):
        return hash(self.intervals)

    def __str__(self):
        return 'TimeSet {' +'; '.join([f'[{x.start}, {x.end})' for x in self.intervals]) + '}'

    def __repr__(self):
        return str(self)

    def __dealloc__(self):
        free_list(self._intervals)

cdef TimeSet empty_set = TimeSet([])
