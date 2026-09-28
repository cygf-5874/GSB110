窗口开到一万的时候，内存曲线是斜着往上走的。winagg 是 Python 3 的
滑动窗口聚合库，只用标准库，构建不需要额外步骤，
自检走 `scripts/check.sh`（`check/` 是固定验收程序，别改），既有用例走
`python3 -m unittest discover -s tests`。

`winagg.py` 里那份实现是对的，但每个窗口都要把窗口内的元素重新扫一遍。

任务：把它改成不重复扫描的实现，同时守住 README 里的 8 条契约。判据是**计数**不是墙钟：
`bench.py` 里的 `WindowVisits` 与 `Pushes` 两个计数器已给全，`check/` 会按规模卡上界。

验收：
- python3 -m unittest discover -s tests 全绿；
- python3 check/check.py 退出码 0，8 个场景全过（correct 3 + cost 3 + edge 2）。

约束：
1. 不改 `check/`、不改 `bench.py` 里两个计数器字段的名字与含义；可以新增模块。
2. 对外 API 名与签名不许改；`tests/test_winagg.py` 里的既有用例一条都不许删或改。
3. 只用标准库，不许引入任何第三方包。
4. 只能单遍扫描输入，别先整体转成列表再重复遍历。
