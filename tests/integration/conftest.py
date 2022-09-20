import hashlib
import uuid
from pathlib import Path
from typing import AsyncGenerator, Callable, Generator

import pytest
from neuro_sdk import Bucket, Client, get


@pytest.fixture
async def neuro_client() -> AsyncGenerator[Client, None]:
    async with await get() as client:
        yield client


@pytest.fixture
async def bucket(neuro_client: Client) -> AsyncGenerator[Bucket, None]:
    bucket_name = f"wabucket-test-{uuid.uuid4().hex[:10]}"
    bucket = await neuro_client.buckets.create(
        name=bucket_name,
    )
    yield bucket
    await neuro_client.buckets.blob_rm(bucket.uri, recursive=True)
    await neuro_client.buckets.rm(bucket_name)


@pytest.fixture
def rand_artifact_dir(tmp_path: Path) -> Generator[Path, None, None]:
    src = tmp_path / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "somedata.csv").write_text(uuid.uuid4().hex)
    (src / "dir").mkdir()
    (src / "dir" / "deep_data.csv").write_text(uuid.uuid4().hex)
    yield src


RecuresiveHasher = Callable[[Path], str]


@pytest.fixture
def files_hasher() -> RecuresiveHasher:
    def _hasher(dir: Path) -> str:
        hasher = hashlib.new("sha256")
        buffer = bytearray(16 * 1024 * 1024)  # 16 MB
        view = memoryview(buffer)
        for fname in sorted(dir.rglob("*")):
            relative_fname = fname.resolve().relative_to(dir.resolve()).as_posix()
            hasher.update(relative_fname.encode("utf-8"))
            if fname.is_dir():
                continue
            with fname.open("rb", buffering=0) as stream:
                read = stream.readinto(buffer)
                while read:
                    hasher.update(view[:read])
                    read = stream.readinto(buffer)
        return hasher.hexdigest()

    return _hasher
