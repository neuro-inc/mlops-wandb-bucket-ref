import time
from pathlib import Path

from neuro_sdk import Bucket

from tests.integration.conftest import RecuresiveHasher
from wabucketref.api import WaBucketRefAPI


def test_upload_and_download(
    bucket: Bucket,
    rand_artifact_dir: Path,
    tmp_path: Path,
    files_hasher: RecuresiveHasher,
) -> None:

    api = WaBucketRefAPI(bucket=bucket.name, project_name="wabucket-test")
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
