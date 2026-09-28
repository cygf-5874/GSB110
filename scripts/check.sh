#!/usr/bin/env bash
# 固定验收入口：按 README「对外契约」的 8 条逐场景核验（correct 3 + cost 3 + edge 2）。
# **别改这个文件。** 用法：bash scripts/check.sh [-list] [--only <组名>]
set -euo pipefail

cd "$(dirname "$0")/.."

exec python3 check/check.py "$@"
