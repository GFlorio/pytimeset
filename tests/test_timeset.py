from datetime import datetime, timedelta
from random import sample, choice, randrange
from unittest import TestCase

import tests.test_timeinterval as ti
from tests.factories import make_sets, make_moments
from timeset import TimeSet

t0 = datetime(2019, 7, 19)
t6 = datetime(2019, 7, 25)
t = make_moments(20, t0, t6)
sets = make_sets(20, t0, t6, 3)  # Guaranteed not to make empty sets


class TestTimeSet(TestCase):
    def test_from_interval(self):
        s = make_sets(1, t[0], t[19], 1)[0]
        i, = s.intervals  # Unpacking single element
        s1 = TimeSet.from_interval(i.start, i.end)
        self.assertEqual(s1, s)

    def test_empty(self):
        self.assertTrue(TimeSet([]).is_empty(), "Set without intervals")
        self.assertTrue(TimeSet.empty().is_empty(), "Empty set")
        self.assertTrue(TimeSet([ti.empty, ti.empty]).is_empty(), "Set of empty intervals")

    def test_not_empty(self):
        self.assertFalse(TimeSet.from_interval(t[2], t[5]).is_empty())

    def test_union(self):
        s0, s1 = sample(sets, k=2)
        u = s0.union(s1)
        self.assertTrue(s0.is_subset(u))
        self.assertTrue(s1.is_subset(u))
        intervals = list(s0.intervals.union(s1.intervals))
        self.assertEqual(u, TimeSet(intervals))

    def test_empty_union(self):
        e = TimeSet.empty()
        s = choice(sets)
        self.assertEqual(e.union(s), s)

    def test_intersection(self):
        s0, s1 = sample(sets, k=2)
        intersection = s0.intersection(s1)
        self.assertTrue(intersection.is_subset(s0))
        self.assertTrue(intersection.is_subset(s1))

    def test_difference(self):
        s0, s1 = sample(sets, k=2)
        diff = s1.difference(s0)
        self.assertTrue(diff.is_subset(s1))
        self.assertTrue(s0.intersection(diff).is_empty())

    def test_contains(self):
        s = choice(sets)
        i = next(iter(s.intervals))
        middle = i.start + (i.end-i.start)/2
        self.assertTrue(s.contains(i.start), "Starting point")
        self.assertTrue(s.contains(middle), "Middle point")

    def test_not_contains(self):
        s = choice(sets)
        i = next(iter(s.intervals))
        self.assertFalse(s.contains(i.end), "Interval ending point")
        self.assertFalse(s.contains(t6+timedelta(days=1)), "Point outside")

    def test_is_subset(self):
        s = choice(sets)
        i = sample(s.intervals, randrange(1, len(s.intervals)+1))
        self.assertTrue(TimeSet(i).is_subset(s))

    def test_is_not_subset(self):
        s0, s1 = sample(sets, k=2)
        while s0.is_subset(s1) or s1.is_subset(s0):
            s0, s1 = sample(sets, k=2)
        self.assertFalse(s0.union(s1).is_subset(s0), "Not subset!")
        self.assertFalse(s0.union(s1).is_subset(s1), "Not subset!")

    def test_is_empty(self):
        self.assertTrue(TimeSet([]).is_empty(), "No intervals")
        self.assertTrue(TimeSet([ti.empty]).is_empty(), "Empty interval")

    def test_is_not_empty(self):
        s = choice(sets)
        self.assertFalse(s.is_empty(), "Not empty set!")

