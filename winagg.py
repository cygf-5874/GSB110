"""winagg：滑动窗口聚合 —— ``rolling_max`` / ``rolling_min`` / ``rolling_sum``。

三个函数都只对输入做**单遍扫描**（接受一次性迭代器，不整体物化）：

- ``rolling_max`` / ``rolling_min``：单调双端队列，队尾按单调性淘汰、
  队首按下标过期，每个元素入队 / 出队各至多一次；
- ``rolling_sum``：定宽缓冲 + 增量加减，新元素加入、最旧元素离开，
  全程整数累加。

``WindowVisits`` 与 ``Pushes`` 两个计数器由 ``bench.py`` 提供：
实现每读到一次元素、每把元素放进 / 取出一次内部结构，都要如实上报
（见 README「对外契约」第 4 条）。判据只看计数，不看墙钟。
"""

from collections import deque
import operator

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
    return _rolling_extreme(xs, w, operator.le)


def rolling_min(xs, w):
    """窗口宽度 ``w`` 的滑动最小值；输出长度为 ``len(xs) - w + 1``。"""
    return _rolling_extreme(xs, w, operator.ge)


def rolling_sum(xs, w):
    """窗口宽度 ``w`` 的滑动和；全程用整数累加。"""
    if w <= 0:
        return []
    buffer = deque()
    total = 0
    out = []
    seen = 0
    for value in xs:
        _visit()
        total += value
        buffer.append(value)
        _push()
        seen += 1
        if seen > w:
            _visit()
            total -= buffer.popleft()
            _push()
        if seen >= w:
            out.append(total)
    if seen < w:
        return []
    return out


def _rolling_extreme(xs, w, dominated):
    """单调双端队列求滑动极值，单遍扫描。

    队列存 ``(下标, 值)`` 且值单调：max 用 ``operator.le``、min 用
    ``operator.ge`` 作为 ``dominated(old, new)`` —— 队尾元素一旦被新元素
    支配就永不会再成为窗口极值，直接弹出；队首靠下标判断是否滑出窗口。
    每个元素入队一次、出队至多一次。
    """
    if w <= 0:
        return []
    queue = deque()
    out = []
    index = 0
    for value in xs:
        _visit()
        while queue:
            _visit()
            if not dominated(queue[-1][1], value):
                break
            queue.pop()
            _push()
        queue.append((index, value))
        _push()
        if index >= w:
            _visit()
            if queue[0][0] <= index - w:
                queue.popleft()
                _push()
        if index >= w - 1:
            _visit()
            out.append(queue[0][1])
        index += 1
    if index < w:
        return []
    return out
