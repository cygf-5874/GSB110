#!/usr/bin/env python3
"""winagg 的固定验收程序。

场景（8 个）：correct 3 + cost 3 + edge 2。

本文件属于固定判据，解题方不得修改。所有判据都只看**计数**与结果，确定性：
不使用墙钟、不使用 ``random``、不依赖 ``dict`` 迭代顺序。
"""

import argparse
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import bench  # noqa: E402
from winagg import rolling_max, rolling_min, rolling_sum  # noqa: E402

#: 规模判据（第 5 条）用的规模与上界（8 倍元素个数，给常数因子留余量）。
N_SCALE = 1_000_000
W_SCALE = 10_000
BUDGET = 8_000_000

#: 重复性判据用的中等规模。
REPEAT_N = 200_000
REPEAT_W = 200

CASES = (
    ([1, 3, 2, 5, 4], 3),
    ([2, 2, 2, 2], 2),
    ([5, 4, 3, 2, 1], 3),
    ([1], 1),
    ([7, 7, 7, 1, 7, 7], 4),
    ([3, 1, 4, 1, 5, 9, 2, 6], 3),
)


def _verdict(ok, expected, actual):
    return (bool(ok), expected, actual)


def _naive(xs, w, reducer):
    data = list(xs)
    n = len(data)
    if w <= 0 or w > n:
        return []
    return [reducer(data[i:i + w]) for i in range(n - w + 1)]


def _scale_input(n):
    return [(i * 1103515245 + 12345) % 1000003 for i in range(n)]


# --------------------------------------------------------------------------
# correct 组：与朴素实现逐元素对拍
# --------------------------------------------------------------------------

def scenario_correct_max_matches_naive():
    for xs, w in CASES:
        bench.reset()
        try:
            got = rolling_max(list(xs), w)
        except Exception as exc:  # noqa: BLE001
            return _verdict(False, "rolling_max(%r, %d) 正常返回" % (xs, w),
                            "%s: %s" % (type(exc).__name__, exc))
        expected = _naive(xs, w, max)
        if got != expected:
            return _verdict(False, "rolling_max(%r, %d) = %r" % (xs, w, expected),
                            "= %r" % (got,))
    return _verdict(True, "六个样例与朴素实现逐元素相等", "一致")


def scenario_correct_min_matches_naive():
    for xs, w in CASES:
        bench.reset()
        try:
            got = rolling_min(list(xs), w)
        except Exception as exc:  # noqa: BLE001
            return _verdict(False, "rolling_min(%r, %d) 正常返回" % (xs, w),
                            "%s: %s" % (type(exc).__name__, exc))
        expected = _naive(xs, w, min)
        if got != expected:
            return _verdict(False, "rolling_min(%r, %d) = %r" % (xs, w, expected),
                            "= %r" % (got,))
    return _verdict(True, "六个样例与朴素实现逐元素相等", "一致")


def scenario_correct_sum_matches_naive_and_integer():
    for xs, w in CASES:
        bench.reset()
        try:
            got = rolling_sum(list(xs), w)
        except Exception as exc:  # noqa: BLE001
            return _verdict(False, "rolling_sum(%r, %d) 正常返回" % (xs, w),
                            "%s: %s" % (type(exc).__name__, exc))
        expected = _naive(xs, w, sum)
        if got != expected:
            return _verdict(False, "rolling_sum(%r, %d) = %r" % (xs, w, expected),
                            "= %r" % (got,))
        for value in got:
            if not isinstance(value, int) or isinstance(value, bool):
                return _verdict(False, "rolling_sum 的元素是 int",
                                "出现 %r" % (value,))

    base = 10 ** 18
    big = [base, base, 1, base, base]
    bench.reset()
    got = rolling_sum(big, 3)
    expected = [2 * base + 1, 2 * base + 1, 2 * base + 1]
    if got != expected:
        return _verdict(False, "大整数逐元素精确：%r" % (expected,), "= %r" % (got,))
    return _verdict(True, "对拍一致、整数累加且大整数精确", "一致")


# --------------------------------------------------------------------------
# cost 组：按规模卡计数上界
# --------------------------------------------------------------------------

def scenario_cost_window_visits_bounded():
    xs = _scale_input(N_SCALE)
    counts = bench.reset(BUDGET)
    try:
        rolling_max(xs, W_SCALE)
    except bench.BudgetExceeded as exc:
        return _verdict(False, "n=%d w=%d 时 WindowVisits ≤ %d" % (N_SCALE, W_SCALE, BUDGET),
                        "计数爆表：%s" % (exc,))
    except Exception as exc:  # noqa: BLE001
        return _verdict(False, "rolling_max 正常返回", "%s: %s" % (type(exc).__name__, exc))
    if counts.WindowVisits < N_SCALE:
        return _verdict(False, "WindowVisits ≥ n = %d" % (N_SCALE,),
                        "= %d" % (counts.WindowVisits,))
    if counts.WindowVisits > BUDGET:
        return _verdict(False, "WindowVisits ≤ %d" % (BUDGET,),
                        "= %d" % (counts.WindowVisits,))
    return _verdict(True, "%d ≤ WindowVisits=%d ≤ %d" % (N_SCALE, counts.WindowVisits, BUDGET),
                    "满足线性上界")


def scenario_cost_pushes_bounded():
    xs = _scale_input(N_SCALE)
    counts = bench.reset(BUDGET)
    try:
        rolling_min(xs, W_SCALE)
    except bench.BudgetExceeded as exc:
        return _verdict(False, "n=%d w=%d 时 Pushes ≤ %d" % (N_SCALE, W_SCALE, BUDGET),
                        "计数爆表：%s" % (exc,))
    except Exception as exc:  # noqa: BLE001
        return _verdict(False, "rolling_min 正常返回", "%s: %s" % (type(exc).__name__, exc))
    if counts.Pushes < N_SCALE:
        return _verdict(False, "Pushes ≥ n = %d" % (N_SCALE,),
                        "= %d" % (counts.Pushes,))
    if counts.Pushes > BUDGET:
        return _verdict(False, "Pushes ≤ %d" % (BUDGET,), "= %d" % (counts.Pushes,))
    return _verdict(True, "%d ≤ Pushes=%d ≤ %d" % (N_SCALE, counts.Pushes, BUDGET,),
                    "满足线性上界")


def scenario_cost_counts_repeatable():
    xs = _scale_input(REPEAT_N)
    bound = 8 * REPEAT_N
    readings = []
    for _ in range(2):
        counts = bench.reset(bound)
        try:
            rolling_max(xs, REPEAT_W)
        except bench.BudgetExceeded as exc:
            return _verdict(False, "两次调用计数相同且 ≤ %d" % (bound,), "超预算：%s" % (exc,))
        except Exception as exc:  # noqa: BLE001
            return _verdict(False, "rolling_max 正常返回", "%s: %s" % (type(exc).__name__, exc))
        readings.append((counts.WindowVisits, counts.Pushes))
    if readings[0] != readings[1]:
        return _verdict(False, "两次调用的计数相同", "%r / %r" % (readings[0], readings[1]))
    if readings[0][0] > bound or readings[0][1] > bound:
        return _verdict(False, "两次计数都 ≤ %d" % (bound,), "= %r" % (readings[0],))
    return _verdict(True, "两次调用计数相同且 ≤ %d：%r" % (bound, readings[0]), "一致")


# --------------------------------------------------------------------------
# edge 组：边界
# --------------------------------------------------------------------------

def scenario_edge_w_out_of_range_returns_empty():
    data = [4, 1, 3]
    functions = (("rolling_max", rolling_max), ("rolling_min", rolling_min),
                 ("rolling_sum", rolling_sum))
    for name, function in functions:
        for w in (0, -1, -100, 4, 100):
            bench.reset()
            got = function(list(data), w)
            if got != []:
                return _verdict(False, "%s(data, %d) = []" % (name, w), "= %r" % (got,))
    bench.reset()
    if rolling_max([], 1) != []:
        return _verdict(False, "rolling_max([], 1) = []", "= %r" % (rolling_max([], 1),))
    return _verdict(True, "w 越界一律返回 []", "一致")


def scenario_edge_w_equals_length_single_element():
    for name, function, expected in (
        ("rolling_max", rolling_max, [5]),
        ("rolling_min", rolling_min, [1]),
        ("rolling_sum", rolling_sum, [9]),
    ):
        bench.reset()
        got = function([5, 1, 3], 3)
        if got != expected:
            return _verdict(False, "%s([5, 1, 3], 3) = %r" % (name, expected), "= %r" % (got,))
    return _verdict(True, "w == len(xs) 时返回单元素", "一致")


SCENARIOS = (
    ("correct", "max-matches-naive", scenario_correct_max_matches_naive),
    ("correct", "min-matches-naive", scenario_correct_min_matches_naive),
    ("correct", "sum-matches-naive-and-integer",
     scenario_correct_sum_matches_naive_and_integer),
    ("cost", "window-visits-bounded", scenario_cost_window_visits_bounded),
    ("cost", "pushes-bounded", scenario_cost_pushes_bounded),
    ("cost", "counts-repeatable", scenario_cost_counts_repeatable),
    ("edge", "w-out-of-range-returns-empty", scenario_edge_w_out_of_range_returns_empty),
    ("edge", "w-equals-length-single-element", scenario_edge_w_equals_length_single_element),
)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="check.py")
    parser.add_argument("-list", dest="list_scenarios", action="store_true",
                        help="列出全部场景后退出")
    parser.add_argument("--only", dest="only", default=None,
                        help="只运行指定组")
    args = parser.parse_args(argv)

    if args.list_scenarios:
        for group, name, _func in SCENARIOS:
            print("%s/%s" % (group, name))
        return 0

    selected = [s for s in SCENARIOS if args.only is None or s[0] == args.only]
    passed = 0
    for group, name, func in selected:
        try:
            ok, expected, actual = func()
        except Exception as exc:  # noqa: BLE001
            ok, expected, actual = False, "无异常", "%s: %s" % (type(exc).__name__, exc)
        if ok:
            passed += 1
            print("PASS %s/%s" % (group, name))
        else:
            print("FAIL %s/%s  期望=%s 实际=%s" % (group, name, expected, actual))

    print("结果：通过 %d/%d" % (passed, len(selected)))
    return 0 if selected and passed == len(selected) else 1


if __name__ == "__main__":
    sys.exit(main())
