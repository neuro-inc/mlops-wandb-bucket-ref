from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, Callable, Generator

import pytest
from apolo_sdk import Bucket, Client, get
from yarl import URL


@pytest.fixture
async def apolo_client() -> AsyncGenerator[Client]:
    async with await get() as client:
        yield client


@pytest.fixture
async def bucket(apolo_client: Client) -> AsyncGenerator[Bucket]:
    bucket_name = f"wabucket-test-{uuid.uuid4().hex[:10]}"
    bucket = await apolo_client.buckets.create(
        name=bucket_name,
    )
    yield bucket
    await apolo_client.buckets.blob_rm(bucket.uri, recursive=True)
    await apolo_client.buckets.rm(bucket_name)


@pytest.fixture
def rand_artifact_dir(tmp_path: Path) -> Generator[Path]:
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


@dataclass()
class BucketArtifactPath:
    bucket: Bucket
    bucket_path: str
    hash: str | None = None


@pytest.fixture
async def bucket_artifact(
    apolo_client: Client,
    bucket: Bucket,
    rand_artifact_dir: Path,
    files_hasher: RecuresiveHasher,
) -> AsyncGenerator[BucketArtifactPath]:
    bucket_name = f"wabucket-test-{uuid.uuid4().hex[:10]}"
    bucket = await apolo_client.buckets.create(
        name=bucket_name,
    )
    artifact_path = "artifact"
    await apolo_client.buckets.upload_dir(
        URL(rand_artifact_dir.as_uri()),
        bucket.uri / artifact_path,
    )
    bp = BucketArtifactPath(bucket, artifact_path, hash=files_hasher(rand_artifact_dir))
    yield bp
    await apolo_client.buckets.blob_rm(bucket.uri, recursive=True)
    await apolo_client.buckets.rm(bucket_name)
