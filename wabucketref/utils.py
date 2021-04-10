import os
from contextlib import contextmanager
from typing import Dict, Optional, Sequence


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


@contextmanager
def switched_aws_cfg(creds_file_env: Optional[str]) -> None:
    if creds_file_env:
        try:
            switch_back = None
            if os.environ.get("AWS_SHARED_CREDENTIALS_FILE"):
                # later we need to switch it back
                switch_back = os.environ.pop("AWS_SHARED_CREDENTIALS_FILE")
            os.environ["AWS_SHARED_CREDENTIALS_FILE"] = creds_file_env
            yield
        finally:
            if switch_back is not None:
                os.environ["AWS_SHARED_CREDENTIALS_FILE"] = switch_back
            else:
                os.environ.pop("AWS_SHARED_CREDENTIALS_FILE")
