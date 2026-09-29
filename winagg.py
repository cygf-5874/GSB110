"""winagg：滑动窗口聚合 —— ``rolling_max`` / ``rolling_min`` / ``rolling_sum``。

``WindowVisits`` 与 ``Pushes`` 两个计数器由 ``bench.py`` 提供：
实现每读到一次元素、每把元素放进 / 取出一次内部结构，都要如实上报
（见 README「对外契约」第 4 条）。判据只看计数，不看墙钟。

本实现对输入只做**单遍流式扫描**（不先物化成列表）：

- ``rolling_max`` / ``rolling_min``：单调双端队列（保留 (位置, 值)），
  每个元素至多入队一次、出队一次，访问与进出都是 O(n)；
- ``rolling_sum``：宽度 ``w`` 的环形队列配合整数滑动和，
  每个元素进 / 出各一次，O(n)。

内部结构只保留「当前窗口可能需要」的元素，内存 O(w) 而非 O(n)。
"""

from collections import deque

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
    return _rolling_extreme(xs, w, keep_newer_when_ge=True)


def rolling_min(xs, w):
    """窗口宽度 ``w`` 的滑动最小值；输出长度为 ``len(xs) - w + 1``。"""
    return _rolling_extreme(xs, w, keep_newer_when_ge=False)


def rolling_sum(xs, w):
    """窗口宽度 ``w`` 的滑动和；全程用整数累加。"""
    if w <= 0:
        return []
    window = deque()
    total = 0
    out = []
    for value in xs:
        _visit()
        window.append(value)
        _push()
        total += value
        if len(window) > w:
            _visit()
            total -= window.popleft()
            _push()
        if len(window) == w:
            out.append(total)
    return out


def _rolling_extreme(xs, w, keep_newer_when_ge):
    """单调队列滑动极值。

    队列里保存 ``(位置, 值)``，值沿队首到队尾对求最大值保持**不增**
    （求最小值保持**不降**）；新元素入队前从队尾弹出所有不会再成为
    极值的旧元素。队首始终是当前窗口的极值。
    """
    if w <= 0:
        return []
    mono = deque()
    out = []
    for index, value in enumerate(xs):
        _visit()
        while mono:
            _visit()
            tail_value = mono[-1][1]
            if keep_newer_when_ge:
                dominated = tail_value <= value
            else:
                dominated = tail_value >= value
            if not dominated:
                break
            mono.pop()
            _push()
        mono.append((index, value))
        _push()
        if mono[0][0] <= index - w:
            mono.popleft()
            _push()
        if index >= w - 1:
            _visit()
            out.append(mono[0][1])
    return out
