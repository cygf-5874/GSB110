"""winagg 的既有用例。

覆盖范围有意保持很小：只关心**结果对不对**（小规模、固定窗口），
不看计数 —— 计数由 ``check/check.py`` 按规模核验。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from winagg import rolling_max, rolling_min, rolling_sum  # noqa: E402


class RollingMaxTest(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(rolling_max([1, 3, 2, 5, 4], 3), [3, 5, 5])

    def test_single_element_windows(self):
        self.assertEqual(rolling_max([3, 1, 2], 1), [3, 1, 2])

    def test_negative_values(self):
        self.assertEqual(rolling_max([-1, -5, -3], 2), [-1, -3])

    def test_w_equals_length(self):
        self.assertEqual(rolling_max([1, 2, 3], 3), [3])


class RollingMinTest(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(rolling_min([3, 1, 2, 5, 4], 3), [1, 1, 2])
        self.assertEqual(rolling_min([5, 4, 3, 2, 1], 2), [4, 3, 2, 1])


class RollingSumTest(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(rolling_sum([1, 2, 3, 4, 5], 3), [6, 9, 12])

    def test_values_are_int(self):
        result = rolling_sum([1, 2, 3, 4], 2)
        for value in result:
            self.assertIsInstance(value, int)
            self.assertNotIsInstance(value, bool)

    def test_large_values_exact(self):
        base = 10 ** 18
        self.assertEqual(rolling_sum([base, 1, 1], 3), [base + 2])


class BoundaryTest(unittest.TestCase):

    def test_output_length(self):
        data = list(range(10))
        for w in (1, 2, 5, 10):
            self.assertEqual(len(rolling_max(data, w)), len(data) - w + 1)

    def test_w_greater_than_length_returns_empty(self):
        self.assertEqual(rolling_max([1, 2], 5), [])
        self.assertEqual(rolling_min([1, 2], 5), [])
        self.assertEqual(rolling_sum([1, 2], 5), [])

    def test_w_not_positive_returns_empty(self):
        self.assertEqual(rolling_max([1, 2, 3], 0), [])
        self.assertEqual(rolling_min([1, 2, 3], -1), [])
        self.assertEqual(rolling_sum([1, 2, 3], 0), [])


class IterableTest(unittest.TestCase):

    def test_accepts_iterator(self):
        self.assertEqual(rolling_max(iter([1, 3, 2, 5]), 2), [3, 3, 5])
        self.assertEqual(rolling_sum(iter([1, 2, 3, 4]), 2), [3, 5, 7])


if __name__ == "__main__":
    unittest.main()
