from unittest import TestCase

from timeset import TimeSet, TimeInterval

import tests.test_timeinterval as ti

s0 = TimeSet([ti.i0, ti.i2])
s1 = TimeSet([ti.i1])


class TestTimeSet(TestCase):
    def test_from_interval(self):
        s = TimeSet.from_interval(ti.t0, ti.t2)
        self.assertEqual(s0, s)

    def test_empty(self):
        self.assertTrue(TimeSet([]).is_empty(), "Set without intervals")
        self.assertTrue(TimeSet.empty().is_empty(), "Empty set")
        self.assertTrue(TimeSet([ti.empty, ti.empty]).is_empty(), "Set of empty intervals")

    def test_not_empty(self):
        self.assertFalse(s0)

    def test_union(self):
        u = TimeSet([ti.i0, ti.i2]).union(TimeSet([ti.i1]))
        self.assertEqual(u, TimeSet([ti.i3]))

    def test_intersection(self):
        intersection = s0.intersection(s1)
        self.assertTrue(intersection.is_subset(s0))
        self.assertTrue(intersection.is_subset(s1))
        self.assertEqual(intersection, TimeInterval(ti.t1, ti.t2))

    def test_difference(self):
        diff = s0.difference(s1)
        self.assertTrue(diff.is_subset(s0))
        self.assertFalse(s1.overlaps(diff))
