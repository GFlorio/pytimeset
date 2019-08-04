from datetime import datetime
from unittest import TestCase

from timeset import TimeSet, TimeInterval

import tests.test_timeinterval as ti

t0 = datetime(2019, 7, 19)
t1 = datetime(2019, 7, 20)
t2 = datetime(2019, 7, 21)
t3 = datetime(2019, 7, 22)
t4 = datetime(2019, 7, 23)
t5 = datetime(2019, 7, 24)
t6 = datetime(2019, 7, 25)

s0 = TimeSet([TimeInterval(t0, t2), TimeInterval(t3, t5)])
s1 = TimeSet([TimeInterval(t1, t3)])
s2 = TimeSet([TimeInterval(t3, t4)])
s4 = TimeSet([TimeInterval(t0, t4)])


class TestTimeSet(TestCase):
    def test_from_interval(self):
        s = TimeSet.from_interval(ti.t1, ti.t3)
        self.assertEqual(s1, s)

    def test_empty(self):
        self.assertTrue(TimeSet([]).is_empty(), "Set without intervals")
        self.assertTrue(TimeSet.empty().is_empty(), "Empty set")
        self.assertTrue(TimeSet([ti.empty, ti.empty]).is_empty(), "Set of empty intervals")

    def test_not_empty(self):
        self.assertFalse(s0.is_empty())

    def test_union(self):
        u = TimeSet([ti.i0, ti.i2]).union(TimeSet([ti.i1]))
        self.assertEqual(u, TimeSet([ti.i3]))

    def test_intersection(self):
        intersection = s0.intersection(s1)
        self.assertTrue(intersection.is_subset(s0))
        self.assertTrue(intersection.is_subset(s1))
        self.assertEqual(intersection, TimeSet.from_interval(ti.t1, ti.t2))

    def test_difference(self):
        diff = s4.difference(s0)
        self.assertTrue(diff.is_subset(s4))
        self.assertTrue(s0.intersection(diff).is_empty())

    def test_contains(self):
        self.assertTrue(s0.contains(ti.t0), "Starting point")
        self.assertTrue(s0.contains(ti.t1), "Middle point")

    def test_not_contains(self):
        self.assertFalse(s0.contains(t2), "Interval ending point")
        self.assertFalse(s0.contains(t5), "Point outside")

    def test_is_subset(self):
        self.assertTrue(s2.is_subset(s0))

    def test_is_not_subset(self):
        self.assertFalse(s0.is_subset(s2), "Superset!")
        self.assertFalse(s1.is_subset(s0), "Only overlapping!")

    def test_is_empty(self):
        self.assertTrue(TimeSet([]).is_empty(), "No intervals")
        self.assertTrue(TimeSet([ti.empty]).is_empty(), "Empty interval")

    def test_is_not_empty(self):
        self.assertFalse(s0.is_empty(), "Not empty set!")

