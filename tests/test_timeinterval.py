from datetime import datetime, timedelta
from unittest import TestCase

from timeset import TimeInterval

# TimeIntervals are immutable, so no need to setup new objects every test.

t0 = datetime(2019, 7, 19)
t1 = datetime(2019, 7, 20)
t2 = datetime(2019, 7, 21)
t3 = datetime(2019, 7, 22)
t4 = datetime(2019, 7, 23)

empty = TimeInterval(t0, t0)
i0 = TimeInterval(t0, t2)
i1 = TimeInterval(t1, t3)
i2 = TimeInterval(t3, t4)
i3 = TimeInterval(t0, t4)


class TestTimeInterval(TestCase):
    def test_contains(self):
        self.assertTrue(i0.contains(t1), "Should contain point inside!")
        self.assertTrue(i0.contains(t0), "Should contain initial point!")

    def test_not_contains(self):
        self.assertFalse(i0.contains(t3), "Should NOT contain point outside!")
        self.assertFalse(i0.contains(t2), "Should NOT contain final point!")

    def test_overlaps(self):
        self.assertTrue(i0.overlaps_with(i1), "Overlaping intervals!")
        self.assertTrue(i1.overlaps_with(i0), "Should be comutative!")
        self.assertTrue(i1.overlaps_with(i1), "Should be reflexive!")
        self.assertTrue(i3.overlaps_with(i1), "Should overlap contained interval!")

    def test_not_overlaps(self):
        self.assertFalse(i0.overlaps_with(i2), "Not overlaping!")
        self.assertFalse(i2.overlaps_with(i1), "Touching intervals should not overlap!")
        self.assertFalse(i1.overlaps_with(i2), "Should be comutative!")
        self.assertFalse(i0.overlaps_with(empty), "Should not overlap empty interval!")

    def test_is_subset(self):
        self.assertTrue(i0.is_subset(i3), "Coinciding starts")
        self.assertTrue(i1.is_subset(i3), "Strict subset")
        self.assertTrue(i1.is_subset(i1), "Should be reflexive!")
        self.assertTrue(i2.is_subset(i3), "Coinciding ends")
        self.assertTrue(empty.is_subset(i3), "Empty interval should be subset of all!")
        self.assertTrue(empty.is_subset(i2), "Empty interval should be subset of all!")

    def test_is_not_subset(self):
        self.assertFalse(i3.is_subset(i0), "Superset, not subset!")
        self.assertFalse(i0.is_subset(i1), "Overlaping but not contained")
        self.assertFalse(i0.is_subset(i2), "No point in common!")

    def test_duration(self):
        expected = t2 - t0
        self.assertEqual(i0.duration(), expected, "Wrong duration!")

    def test_is_empty(self):
        self.assertTrue(TimeInterval(t0, t0).is_empty())
        self.assertFalse(i0.is_empty())

    def test_intersection(self):
        intersection = i0.intersection(i1)
        self.assertTrue(intersection.is_subset(i0))
        self.assertTrue(intersection.is_subset(i1))

    def test_start(self):
        self.assertEqual(i0.start, t0)

    def test_end(self):
        self.assertEqual(i0.end, t2)

    def test_translate(self):
        delta = timedelta(days=1)
        translated = i0.translate(delta)
        self.assertEqual(translated.start, t1)
        self.assertEqual(translated.end, t3)
