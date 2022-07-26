from __future__ import annotations

import argparse
import hashlib
import logging
import os
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Dict, Union

import wandb
from neuro_cli.asyncio_utils import Runner
from neuro_sdk import Bucket, Client, Factory, ResourceNotFound
from wandb.wandb_run import Run
from yarl import URL


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

RunArgsType = Union[argparse.Namespace, Dict, str]
DEFAULT_REF_NAME = "platform_blob"


class WaBucketRefAPI:
    def __init__(
        self,
        bucket: str | None = None,
        project_name: str | None = None,
    ):
        self._wab_project_name = project_name or os.environ["WANDB_PROJECT"]

        self._runner = Runner()
        self._runner.__enter__()

        self._n_client: Client | None = None
        self._runner.run(self.init_client())

        self._bucket_name = bucket or self._wab_project_name
        self._bucket: Bucket | None = None
        self._runner.run(self.init_bucket())

    async def init_client(self) -> Client:
        if self._n_client is not None and not self._n_client._closed:
            return self._n_client
        client = await Factory().get()
        self._n_client = client
        return self._n_client

    @property
    def client(self) -> Client:
        assert self._n_client is not None
        return self._n_client

    async def init_bucket(self) -> Bucket:
        if not self._bucket:
            self._bucket = await self.client.buckets.get(self._bucket_name)
        return self._bucket

    @property
    def bucket(self) -> Bucket:
        assert self._bucket is not None
        return self._bucket

    def close(self) -> None:
        if self._n_client is not None:
            self._runner.run(self._n_client.close())
        try:
            # Suppress prints unhandled exceptions
            # on event loop closing
            sys.stderr = None  # type: ignore
            self._runner.__exit__(*sys.exc_info())
        finally:
            sys.stderr = sys.__stderr__

    def upload_artifact(
        self,
        src_folder: Path,
        art_name: str,
        art_type: str,
        art_alias: str | None = None,
        art_metadata: dict | None = None,  # type: ignore
        as_refference: bool = True,
        overwrite: bool = False,
    ) -> str:
        self._wandb_init_if_needed()
        artifact = wandb.Artifact(name=art_name, type=art_type, metadata=art_metadata)
        artifact_alias = self._get_artifact_alias(art_alias)
        if as_refference:
            src_as_uri = URL(f"file:{src_folder.resolve()}")
            bucket_path: str = f"{art_type}/{art_name}/{artifact_alias}"
            artifact_bucket_root: URL = self.bucket.uri / bucket_path
            logger.info(
                f"Uploading artifact from '{src_as_uri}' to {artifact_bucket_root} ..."
            )

            root_exists = self._runner.run(self._path_exists_in_bucket(bucket_path))
            if not overwrite and root_exists:
                raise RuntimeError(
                    f"Artifact {artifact_bucket_root} exists, "
                    "overwrite is not allowed."
                )
            elif overwrite and root_exists:
                logger.warning(
                    f"Artifact {artifact_bucket_root} exists, will be overwriten."
                )
                self._runner.run(
                    self.client.buckets.blob_rm(artifact_bucket_root / "*")
                )

            self._runner.run(
                self.client.buckets.upload_dir(
                    src=src_as_uri,
                    dst=artifact_bucket_root,
                )
            )
            logger.info(f"Artifact uploaded to {artifact_bucket_root}")
            artifact.add_reference(
                name=DEFAULT_REF_NAME,
                uri=str(artifact_bucket_root),
                checksum=False,
            )
        else:
            logger.info(f"Uploading artifact {src_folder} as directory...")
            artifact.add_dir(str(src_folder))
        wandb.log_artifact(artifact, aliases=[artifact_alias])

        # neuro-flow reads ::set-output... if only they are at the beginning of a string
        print(
            f"::set-output name=artifact_name::{art_name}",
            flush=True,
            file=sys.stdout,
        )
        print(
            f"::set-output name=artifact_type::{art_type}",
            flush=True,
            file=sys.stdout,
        )
        print(
            f"::set-output name=artifact_alias::{artifact_alias}",
            flush=True,
            file=sys.stdout,
        )
        time.sleep(1)  # https://github.com/neuro-inc/mlops-wandb-bucket-ref/issues/16
        return artifact_alias

    async def _path_exists_in_bucket(self, path: str) -> bool:
        try:
            await self.client.buckets.head_blob(
                self._bucket_name,
                key=path,
            )
            return True
        except ResourceNotFound:
            return False

    def _wandb_init_if_needed(self, run_args: RunArgsType | None = None) -> None:
        if wandb.run is None:
            logger.info(
                "Active W&B run was not found, starting one to upload the artifact."
            )
            self.wandb_start_run(run_args=run_args)

    def wandb_start_run(
        self,
        w_run_name: str | None = None,
        w_job_type: str | None = None,
        run_args: RunArgsType | None = None,
    ) -> Run:
        if wandb.run is not None:
            raise RuntimeError(f"W&B has registerred run {wandb.run.name}")

        wandb_run = wandb.init(
            project=self._wab_project_name,
            name=w_run_name,
            job_type=w_job_type,
            settings=wandb.Settings(start_method="fork"),
            config=run_args,  # type: ignore
            tags=self._try_get_neuro_tags(),
        )
        if not isinstance(wandb_run, Run):
            raise RuntimeError(f"Failed to initialize W&B run, got: {wandb_run:r}")
        return wandb_run

    def _get_artifact_alias(self, art_alias: str | None = None) -> str:
        """
        There are several ways to set the artifact alias,
        depending on the "art_alias" variable value:
            None object               -> the UUID4 will be assigned
            "!run-config-hash" string -> the values of wandb.run.config dict
                                         will be sorted and hashed
            other string object       -> itself will be used
            other object              -> error will be raised
        """
        if art_alias is None:
            alias = str(uuid.uuid4())
        elif art_alias == "!run-config-hash" and wandb.run and wandb.run.config:
            cfg = wandb.run.config
            run_config_str = " ".join([f"{k}={v}" for k, v in sorted(cfg.items())])
            alias = hashlib.sha256(run_config_str.encode("UTF-8")).hexdigest()
        elif type(art_alias) == str:
            alias = art_alias
        else:
            raise ValueError(f"Wrong value for artifact alias: {art_alias}.")
        return alias

    def download_artifact(
        self,
        art_name: str,
        art_type: str,
        art_alias: str,
        dst_folder: Path | None = None,
    ) -> Path:
        self._wandb_init_if_needed()
        artifact: wandb.Artifact = wandb.use_artifact(
            artifact_or_name=f"{art_name}:{art_alias}", type=art_type
        )
        blob_ref = artifact.manifest.entries[DEFAULT_REF_NAME].ref
        assert isinstance(blob_ref, str)
        blob_uri = URL(blob_ref)

        if dst_folder is None:
            dst_folder = Path(tempfile.mkdtemp())
        dst_uri = URL(f"file:{dst_folder.resolve()}")

        self._runner.run(
            self.client.buckets.download_dir(
                src=blob_uri,
                dst=dst_uri,
            )
        )
        return dst_folder

    def _try_get_neuro_tags(self) -> list[str] | None:
        job_id = os.environ.get("NEURO_JOB_ID")
        if job_id:
            # assuming the neuro platform job
            result = [
                f"job_id:{job_id}",
                f"job_name:{os.environ.get('NEURO_JOB_NAME')}",
                f"owner:{os.environ.get('NEURO_JOB_OWNER')}",
            ]
            result.extend(self._get_neuro_job_tags(job_id))
        else:
            return None

    def _get_neuro_job_tags(self, job_id: str) -> list[str]:
        job_description = self._runner.run(self._n_client.jobs.status(job_id))
        return job_description.tags
