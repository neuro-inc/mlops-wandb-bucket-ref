import argparse
import hashlib
import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Optional

import cloudpathlib as cpl
import wandb
from wandb.wandb_run import Run

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class WaBucketRefAPI:
    def __init__(
        self,
        bucket: Optional[str] = None,
        project_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        # W&B related fields
        self._wab_project_name = project_name or os.environ["WANDB_PROJECT"]

        # S3 related fields
        bucket_name = bucket or f"s3://{self._wab_project_name}"
        self._s3_key_id = aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
        self._s3_access_key = aws_secret_access_key or os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        )
        # TODO: wait until release of a new version
        # self._s3_endpoint_url = os.environ.get("AWS_S3_ENDPOINT_URL") or endpoint_url
        self._s3_client = cpl.S3Client(
            aws_access_key_id=self._s3_key_id,
            aws_secret_access_key=self._s3_access_key,
            # endpoint_url=self._s3_endpoint_url,
        )
        self._s3_bucket = self._s3_client.CloudPath(bucket_name)

    def upload_artifact(
        self,
        src_folder: Path,
        w_name: str,
        w_type: str,
        w_metadata: Optional[Dict] = None,
        as_refference: bool = True,
        run_args: Optional[argparse.Namespace] = None,
    ) -> str:
        # pass "run_args" to calculate artifact alias
        # TODO: refactor this since no single responcibility
        self._wandb_init_if_needed(run_args)
        artifact = wandb.Artifact(name=w_name, type=w_type, metadata=w_metadata)
        artifact_alias = self._wandb_run_config_to_alias()
        if as_refference:
            logger.info(f"Uploading artifact from '{src_folder}' as reference...")
            artifact_remote_root = self._s3_bucket / w_type / w_name / artifact_alias
            for file_ in src_folder.glob("*"):
                self._s3_upload_artifact(file_, artifact_remote_root)
            self._s3_upload_artifact(src_folder, artifact_remote_root)
            logger.info(f"Artifact uploaded to {artifact_remote_root}")
            artifact.add_reference(uri=str(artifact_remote_root))
        else:
            logger.info(f"Uploading artifact {src_folder} as directory...")
            artifact.add_dir(str(src_folder))
        wandb.log_artifact(artifact, aliases=[artifact_alias])
        return artifact_alias

    def _wandb_init_if_needed(self, run_args: Optional[argparse.Namespace] = None):
        if wandb.run is None:
            logger.info(
                "Active W&B run was not found, starting one to upload the artifact."
            )
            self.wandb_start_run(run_args=run_args)

    def wandb_start_run(
        self,
        w_run_name: Optional[str] = None,
        w_job_type: Optional[str] = None,
        run_args: Optional[argparse.Namespace] = None,
    ) -> Run:
        if wandb.run is not None:
            raise RuntimeError(f"W&B has registerred run {wandb.run.name}")

        wandb_run = wandb.init(
            project=self._wab_project_name,
            name=w_run_name,
            job_type=w_job_type,
            id=os.environ.get("NEURO_JOB_ID"),
            settings=wandb.Settings(start_method="fork"),
            config=run_args,  # type: ignore
        )
        if not isinstance(wandb_run, Run):
            raise RuntimeError(f"Failed to initialize W&B run, got: {wandb_run:r}")
        return wandb_run

    def _s3_upload_artifact(self, path: Path, root: cpl.S3Path) -> None:
        if path.is_file():
            (root / str(path.name)).write_bytes(path.read_bytes())
        elif path.is_dir():
            (root / str(path.name)).mkdir(parents=True, exist_ok=True)
            for x in path.glob("*"):
                self._s3_upload_artifact(x, root / path.name)
        else:
            raise TypeError(f"{path} is not a dir nor file.")

    def _wandb_run_config_to_alias(self) -> str:
        if wandb.run and wandb.run.config:
            run_config = {}
            for key in vars(wandb.run.config):
                run_config[key] = str(getattr(wandb.run.config, key))
            run_config_str = " ".join(
                [f"{key}={value}" for key, value in sorted(run_config.items())]
            )
            alias = hashlib.sha256(run_config_str.encode("UTF-8")).hexdigest()
        else:
            alias = "latest"
        return alias

    def download_artifact(
        self,
        art_name: str,
        art_type: str,
        art_alias: str,
        dst_folder: Optional[Path] = None,
        run_args: Optional[argparse.Namespace] = None,
    ) -> str:
        self._wandb_init_if_needed(run_args)
        artifact = wandb.use_artifact(
            artifact_or_name=f"{art_name}:{art_alias}", type=art_type
        )
        if dst_folder is None:
            dst_folder = Path(tempfile.mkdtemp())
        art_path: str = artifact.download(root=dst_folder)
        return art_path
