#!/usr/bin/env python3
"""调用方给的最小复现。

上游的观察是「窗口开到一万的时候，内存曲线是斜着往上走的」：
这里把 `n` 与 `w` 同时翻倍，看 `WindowVisits` / `Pushes` 怎么涨 ——
近似线性的实现，计数应当大致跟着 `n` 走，而不是跟着 `n * w` 走。
修好之后本脚本静默退出 0。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bench import reset  # noqa: E402
from winagg import rolling_max  # noqa: E402

CASES = ((5000, 50), (10000, 100))

#: 每个元素允许被访问 / 进出的常数级上限。
PER_ELEMENT = 8


def sample(n):
    return [(i * 1103515245 + 12345) % 1000003 for i in range(n)]


def main():
    broken = []

    for n, w in CASES:
        counts = reset()
        rolling_max(sample(n), w)
        bound = PER_ELEMENT * n
        print("n=%-6d w=%-5d WindowVisits=%-10d Pushes=%-10d 上限=%d"
              % (n, w, counts.WindowVisits, counts.Pushes, bound))
        if counts.WindowVisits > bound or counts.Pushes > bound:
            broken.append((n, w))

    if broken:
        print("=> 计数随 n*w 增长，超出线性上界；w 变大时更明显")
        return 1
    print("=> 计数近似线性")
    return 0


if __name__ == "__main__":
    sys.exit(main())
