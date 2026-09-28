"""winagg：滑动窗口聚合 —— ``rolling_max`` / ``rolling_min`` / ``rolling_sum``。

``WindowVisits`` 与 ``Pushes`` 两个计数器由 ``bench.py`` 提供：
实现每读到一次元素、每把元素放进 / 取出一次内部结构，都要如实上报
（见 README「对外契约」第 4 条）。判据只看计数，不看墙钟。
"""

import bench

__all__ = ["rolling_max", "rolling_min", "rolling_sum"]


def _visit(count=1):
    """上报：读到了 ``count`` 次元素。"""
    bench.ACTIVE.visit(count)


def _push(count=1):
    """上报：元素进出内部结构 ``count`` 次。"""
    bench.ACTIVE.push(count)


def rolling_max(xs, w):
    """窗口宽度 ``w`` 的滑动最大值；输出长度为 ``len(xs) - w + 1``。"""
    return _reduce_windows(xs, w, max)


def rolling_min(xs, w):
    """窗口宽度 ``w`` 的滑动最小值；输出长度为 ``len(xs) - w + 1``。"""
    return _reduce_windows(xs, w, min)


def rolling_sum(xs, w):
    """窗口宽度 ``w`` 的滑动和；全程用整数累加。"""
    data = list(xs)
    n = len(data)
    if w <= 0 or w > n:
        return []
    out = []
    for start in range(n - w + 1):
        total = 0
        for index in range(start, start + w):
            _visit()
            total += data[index]
        out.append(total)
    return out


def _reduce_windows(xs, w, reducer):
    """把每个窗口切出来交给 ``reducer``。"""
    data = list(xs)
    n = len(data)
    if w <= 0 or w > n:
        return []
    out = []
    for start in range(n - w + 1):
        window = []
        for index in range(start, start + w):
            _visit()
            window.append(data[index])
            _push()
        out.append(reducer(window))
    return out
