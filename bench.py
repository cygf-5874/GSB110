#!/usr/bin/env python3
"""winagg 的计数入口 —— **别改这个文件**。

`winagg` 的每一次「读到一个元素」与「元素进出内部结构」都通过这里的
:class:`Counts` 上报；固定件按**计数**卡上界，不使用墙钟、不使用随机源。

用法::

    python3 bench.py                # 在中等规模上打印两个计数
    python3 bench.py <n> <w>        # 指定规模
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class BudgetExceeded(Exception):
    """计数超过本次预算时抛出（固定件用它把 O(n·w) 的实现快速挡住）。"""


class Counts(object):
    """计数容器。

    - ``WindowVisits``：访问过的元素次数（从输入或内部缓冲里读到一次元素记 1）。
    - ``Pushes``：入结构 / 出结构次数（放入一次、取出一次各记 1）。

    字段名与含义固定，**勿改**。
    """

    __slots__ = ("WindowVisits", "Pushes", "Limit")

    def __init__(self, limit=None):
        self.WindowVisits = 0
        self.Pushes = 0
        self.Limit = limit

    def visit(self, count=1):
        self.WindowVisits += count
        if self.Limit is not None and self.WindowVisits > self.Limit:
            raise BudgetExceeded("WindowVisits 超过预算 %d" % (self.Limit,))

    def push(self, count=1):
        self.Pushes += count
        if self.Limit is not None and self.Pushes > self.Limit:
            raise BudgetExceeded("Pushes 超过预算 %d" % (self.Limit,))

    def reset(self):
        self.WindowVisits = 0
        self.Pushes = 0

    def __repr__(self):
        return "Counts(WindowVisits=%d, Pushes=%d)" % (self.WindowVisits, self.Pushes)


#: `winagg` 上报计数用的当前容器；固定件会用 :func:`reset` 整体替换它。
ACTIVE = Counts()


def reset(limit=None):
    """换一个新的当前计数器并返回它；``limit`` 非空时超预算抛 :class:`BudgetExceeded`。"""
    global ACTIVE
    ACTIVE = Counts(limit)
    return ACTIVE


def sample(n, w):
    from winagg import rolling_max

    xs = [(i * 1103515245 + 12345) % 1000003 for i in range(n)]
    counts = reset()
    out = rolling_max(xs, w)
    print("n            = %d" % (n,))
    print("w            = %d" % (w,))
    print("窗口数       = %d" % (len(out),))
    print("WindowVisits = %d" % (counts.WindowVisits,))
    print("Pushes       = %d" % (counts.Pushes,))
    return 0


def main(argv):
    n = int(argv[0]) if len(argv) > 0 else 20000
    w = int(argv[1]) if len(argv) > 1 else 200
    return sample(n, w)


if __name__ == "__main__":
    # 以模块身份再跑一遍，保证与 ``winagg`` 里 ``import bench`` 拿到的是同一个模块实例。
    import bench

    sys.exit(bench.main(sys.argv[1:]))
