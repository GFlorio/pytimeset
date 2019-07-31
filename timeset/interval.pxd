#cython: language_level=3

cdef class Interval:
    cdef double start, end
    cpdef bint contains(self, long element)
    cpdef bint overlaps_with(self, Interval other)
    cpdef bint is_subset(self, Interval other)
    cpdef double duration(self)
    cpdef bint is_empty(self)
    cpdef Interval intersection(self, Interval other)
    cpdef Interval translate(self, long _by)
