# winagg

`winagg` 是一个纯标准库的**滑动窗口聚合**小库：`rolling_max` / `rolling_min` / `rolling_sum`。

- 语言 / 运行：Python 3，只用标准库（`unittest` 跑用例），无第三方依赖。
- 自检：`scripts/check.sh`（内部调用 `check/check.py`，那是固定验收程序，**别改**）。
- 目录：

  ```
  winagg.py               窗口聚合实现（唯一实现文件）
  bench.py                计数入口：导出 Counts（WindowVisits / Pushes），勿改
  tests/test_winagg.py    既有用例（12 个；只覆盖小规模、结果对不对）
  repro.py                调用方给的最小复现
  check/check.py          固定验收程序：8 个场景
  ```

## 语言版本前提

- Python 3（开发与验证用 3.13）。
- **只用标准库**，不引入任何第三方依赖。

## 怎么跑

```bash
python3 -m unittest discover -s tests   # 既有用例，当前 12/12 全绿
python3 repro.py                        # 调用方给的最小复现
bash scripts/check.sh                   # 固定验收；支持 -list 与 --only <组名>
```

## 对外契约（8 条）

下面 8 条是 `winagg` 的**对外契约**，实现必须全部守住；它们是本题验收点的唯一出处。

1. `rolling_max(xs, w) -> list[int]`、`rolling_min(xs, w) -> list[int]`、
   `rolling_sum(xs, w) -> list[int]`：窗口宽度为 `w`，输出长度为 `len(xs) - w + 1`。
2. `rolling_sum` 必须用**整数**累加，不得用浮点（避免大整数上的累积误差）。
3. 三个函数的结果必须与「每个窗口重新扫一遍」的朴素实现**逐元素相等**。
4. **计数口径**：`bench.py` 里的 `Counts` 提供两个计数器 ——
   `WindowVisits` 统计「访问过的元素次数」（从输入或内部缓冲里读到一次元素就记 1），
   `Pushes` 统计「入结构 / 出结构次数」。实现必须如实上报；
   **判据只看计数，不看墙钟。**
5. **规模判据**：在 `n = 1_000_000`、`w = 10_000` 上调用 `rolling_max` / `rolling_min`，
   `WindowVisits` 与 `Pushes` 都不得随 `n * w` 增长（朴素实现约 1e10），
   必须近似线性 —— 每个元素被访问 / 进出的次数是常数级，
   `check/` 在两组计数上都卡 `≤ 8 * n = 8_000_000` 的上界。
6. **边界**：`w <= 0` 或 `w > len(xs)` 返回空列表；`w == len(xs)` 返回单元素列表。
7. **可迭代即可**：`xs` 允许是任意可迭代对象（含只能迭代一次的一次性迭代器）；
   实现只做**单遍扫描**，不得先整体转成列表再反复遍历。
8. **确定**：不依赖 `dict` 迭代顺序；同一输入任意多次调用，结果与计数都必须完全一致
   （不得留下跨调用的状态）。

## 本次重构的目标

现有 `winagg.py` 的**结果**是对的，但每个窗口都要把窗口内的元素重新扫一遍：
计数随 `n * w` 增长（见第 5 条）。本次要把 `WindowVisits` 与 `Pushes` 压到近似线性，
同时保住第 3 条「与朴素实现逐元素相等」和第 6 条边界。

## 固定验收

```bash
python3 check/check.py          # 也支持 -list 与 --only <组>
```

`check/` 与 `bench.py` 是固定件，**勿改**；`bench.py` 里两个计数器字段的名字与含义不许改。
