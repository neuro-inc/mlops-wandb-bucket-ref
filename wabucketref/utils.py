from typing import Dict, Sequence


def parse_meta(meta: Sequence[str]) -> Dict:
    result = {}
    for item in meta:
        k, *v = item.split("=")
        if len(v) == 0:
            raise ValueError(
                f"Artifact meta should be KEY=VALUE pairs, got {k}={v} in {item}."
            )
        v = "=".join(v)
        result[k] = v
    return result
