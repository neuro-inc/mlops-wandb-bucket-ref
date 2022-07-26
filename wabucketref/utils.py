from __future__ import annotations

from typing import Sequence


def parse_meta(meta: Sequence[str]) -> dict[str, str]:
    result = {}
    for item in meta:
        k, *v = item.split("=")
        if len(v) == 0:
            raise ValueError(
                f"Artifact meta should be KEY=VALUE pairs, got {k}={v} in {item}."
            )
        val = "=".join(v)
        result[k] = val
    return result
