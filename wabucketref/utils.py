from __future__ import annotations

import os
from contextlib import contextmanager
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


@contextmanager
def switched_aws_cfg(creds_file_env: str | None):  # type: ignore
    try:
        switch_back = os.environ.get("AWS_SHARED_CREDENTIALS_FILE")
        if creds_file_env:
            os.environ["AWS_SHARED_CREDENTIALS_FILE"] = creds_file_env
        yield
    finally:
        if switch_back is not None:
            os.environ["AWS_SHARED_CREDENTIALS_FILE"] = switch_back
        else:
            os.environ.pop("AWS_SHARED_CREDENTIALS_FILE")
