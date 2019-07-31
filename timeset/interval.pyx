# -*- coding: utf-8 -*-
#cython: language_level=3

cdef class Interval:
    # cdef double start, end

    def __cinit__(self, double start, double end):
        if start > end:
            raise ValueError("The start of the interval must not be after the end!")
        self.start = start
        self.end = end

    cpdef bint contains(self, long element):
        return self.start <= element < self.end

    cpdef bint overlaps_with(self, Interval other):
        return self.end > other.start and other.end > self.start

    cpdef bint is_subset(self, Interval other):
        if self.is_empty():
            return True
        return self.start >= other.start and self.end <= other.end

    cpdef double duration(self):
        return self.end - self.start

    cpdef bint is_empty(self):
        return self.start == self.end

    cpdef Interval intersection(self, Interval other):
        cdef double start, end
        if not self.overlaps_with(other):
            # Return an EMPTY interval!
            return empty
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        return Interval(start, end)

    cpdef Interval translate(self, long _by):
        return Interval(self.start+_by, self.end+_by)

    def __eq__(self, other):
        if not isinstance(other, Interval):
            return False
        return self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash((self.start, self.end))


cdef Interval empty = Interval(0, 0)
