import os
import time
import uuid
from pathlib import Path

import pytest
from neuro_sdk import Bucket

from tests.integration.conftest import BucketArtifactPath, RecuresiveHasher
from wabucketref.api import WaBucketRefAPI


def test_upload_and_download(
    bucket: Bucket,
    rand_artifact_dir: Path,
    tmp_path: Path,
    files_hasher: RecuresiveHasher,
) -> None:
    os.environ["NEURO_JOB_ID"] = "test-job"  # to cover also neuro job metainfo fetch

    api = WaBucketRefAPI(bucket=bucket.name, project_name="wabucket-test")
    api.wandb_start_run()
    alias = api.upload_artifact(
        src_folder=rand_artifact_dir,
        art_name="my_test_artifact",
        art_type="test",
    )
    src_hash = files_hasher(rand_artifact_dir)
    time.sleep(5)  # wandb needs some time to start tracking the artifact :)
    dst = api.download_artifact(
        dst_folder=tmp_path / "dst",
        art_name="my_test_artifact",
        art_type="test",
        art_alias=alias,
    )
    api.close()
    dst_hash = files_hasher(dst)

    assert src_hash == dst_hash


def test_link_artifact(
    bucket_artifact: BucketArtifactPath,
    tmp_path: Path,
    files_hasher: RecuresiveHasher,
) -> None:
    api = WaBucketRefAPI(
        bucket=bucket_artifact.bucket.name, project_name="wabucket-test"
    )
    art_alias = api.link(bucket_artifact.bucket_path, "my_test_artifact", "test")
    time.sleep(5)  # wandb needs some time to start tracking the artifact :)
    dst = api.download_artifact(
        dst_folder=tmp_path / "dst",
        art_name="my_test_artifact",
        art_type="test",
        art_alias=art_alias,
    )
    with pytest.raises(ValueError, match="does not exist or not a directory"):
        # check that non-existing blobs cannot be linked
        api.link(uuid.uuid4().hex, "my_test_artifact", "test")
    art_alias = api.link(bucket_artifact.bucket_path, "my_test_artifact", "test")
    api.close()
    dst_hash = files_hasher(dst)
    assert bucket_artifact.hash == dst_hash
