[![Build Status](https://travis-ci.org/gflorio/pytimeset.svg?branch=master)](https://travis-ci.org/gflorio/pytimeset)
[![Coverage Status](https://coveralls.io/repos/github/GFlorio/pytimeset/badge.svg?branch=master)](https://coveralls.io/github/GFlorio/pytimeset?branch=master)
[![PyPI version](https://badge.fury.io/py/pytimeset.svg)](https://badge.fury.io/py/pytimeset)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pytimeset.svg)](https://pypi.python.org/pypi/pytimeset/)

# PyTimeSet

Library that defines continuous time sets and offers typical operations
between them using Cython for speed.

## Installation

Requirements: Python 3.6+

To install, simply run
```shell script
pip install pytimeset
```

## Basic Usage:

This library defines two immutable, timezone-aware, objects: TimeInterval and TimeSet.

Time intervals are defined by their start and end moments. Intervals
are defined to contain their start point, but not their end point (closed to the 
left, open to the right).

Time sets are defined by the minimum set of intervals that contains all the points in it.
This means that the intervals passed to the constructor of the TimeSet may not be
the same intervals contained inside it, as "touching" intervals are merged and empty intervals are
removed.

```python
from datetime import datetime
from timeset import TimeInterval, TimeSet

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

i0.contains(t1)  # True
i0.start == t0  # True
i0.end == t2  # True

i0.overlaps_with(i1)  # True
i0.is_subset(i3)  # True
empty.is_subset(i2)  # True, the empty set is subset of every other set.

i0.intersection(i1)  # TimeInterval(t1, t2)

```

## Undefined behavior

Intervals defined by a single point (Such as TimeInterval(t, t)) are a bit weird.
As of now, I have defined them to be equivalent to the empty set, but that might change in the future,
so just don't mess too much with them.

This library is timezone-aware, meaning that you can pass timezone-aware datetimes to it and you will
get back datetimes in the same timezone. That said, if you mix timezones, the results will point to the
right moment in time, but their timezones are undefined (meaning any one of those you originally passed).
When in doubt, simply convert the results to your preferred timezone.
