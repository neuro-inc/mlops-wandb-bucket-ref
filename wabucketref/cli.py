from pathlib import Path
from typing import Optional, Sequence

import click
from click import Context

from . import WaBucketRefAPI, __version__, parse_meta


@click.group()
@click.version_option(
    version=__version__, message="W&B bucket artifacts package version: %(version)s"
)
@click.option(
    "--bucket", type=str, help="S3 bucket, which will be used to store artifacts"
)
@click.option(
    "--project-name",
    type=str,
    help="W&B project name, which should be used",
)
@click.option(
    "--run-name",
    type=str,
    help="W&B human-readable run name to distinguish among other runs",
)
@click.option(
    "--job-type",
    type=str,
    help="W&B human-readable job type to group similar jobs together in the reports",
)
@click.option(
    "--endpoint-url",
    type=str,
    help="S3 bucket service endpoint URL",
)
@click.option(
    "--aws-access-key-id",
    type=str,
    help="Bucket service access key ID",
)
@click.option(
    "--aws-secret-access-key",
    type=str,
    help="Bucket service secret access key, assotiated with the provided access key ID",
)
@click.option(
    "--aws-credentials-file",
    type=str,
    help="Path to the credentials file for accessing S3 bucket.",
)
@click.option(
    "--region-name",
    type=str,
    help="Region, where S3 bucket is located",
)
@click.pass_context
def main(
    ctx: Context,
    bucket: Optional[str],
    project_name: Optional[str],
    run_name: Optional[str],
    job_type: Optional[str],
    endpoint_url: Optional[str],
    aws_access_key_id: Optional[str],
    aws_secret_access_key: Optional[str],
    aws_credentials_file: Optional[str],
    region_name: Optional[str],
) -> None:
    """
    Upload to and download from S3 artifacts, stored in W&B.
    """
    ctx.obj = {
        "init_params": {
            "bucket": bucket,
            "project_name": project_name,
            "endpoint_url": endpoint_url,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_credentials_file": aws_credentials_file,
            "region_name": region_name,
        },
        "run_params": {
            "w_run_name": run_name,
            "w_job_type": job_type,
        },
    }


@main.command()
@click.argument("src_dir")
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="W&B artifact name to assign",
)
@click.option(
    "-t",
    "--type",
    "type_",
    type=str,
    required=True,
    help="W&B artifact type to assing",
)
@click.option(
    "-m",
    "--metadata",
    metavar="KEY=VALUE",
    type=str,
    multiple=True,
    help="Metainfo, which will be pinned to the artifact after upload.",
)
@click.option(
    "--reff/--no-reff",
    is_flag=True,
    default=True,
    help=(
        "Whether to upload artifact to S3 bucket and use it as reference in W&B, "
        "or directly upload the folder to W&B"
    ),
)
@click.option(
    "-a",
    "--run_args",
    help=(
        "Args of current run. "
        "Provide this argument for calculating a proper artifact alias. "
        "Otherwise, the 'latest' will be used."
    ),
)
@click.pass_context
def upload(
    ctx: Context,
    src_dir: str,
    name: str,
    type_: str,
    metadata: Sequence[str],
    reff: bool,
    run_args: Optional[str],
) -> None:
    """
    Upload artifact from local folder to the bucket
    and store it's reference as W&B artifact
    """
    ref_api = WaBucketRefAPI(**ctx.obj["init_params"])
    meta = parse_meta(metadata)
    ref_api.wandb_start_run(
        w_run_name="texture-expand",
        w_job_type="generate-dataset",
        run_args=run_args,
    )

    ref_api.upload_artifact(
        src_folder=Path(src_dir),
        art_name=name,
        art_type=type_,
        art_metadata=meta,
        as_refference=reff,
    )


@main.command()
@click.argument("artifact_type")
@click.argument("artifact_name")
@click.argument("artifact_alias")
@click.option(
    "-d",
    "--destination-folder",
    type=Path,
    help=(
        "Path where the artifact should be stored. "
        "Otherwise, './{artifact_type}/{artifact_name}/{artifact_alias}' will be used"
    ),
)
@click.option(
    "-a",
    "--run_args",
    help=(
        "Args of current run. "
        "Provide this argument for calculating a proper artifact alias. "
        "Otherwise, the 'latest' will be used."
    ),
)
@click.pass_context
def download(
    ctx: Context,
    artifact_type: str,
    artifact_name: str,
    artifact_alias: str,
    destination_folder: Optional[Path],
    run_args: Optional[str],
) -> None:
    """
    Download artifact of specified type, name and version.
    """
    ref_api = WaBucketRefAPI(**ctx.obj["init_params"])
    if destination_folder is None:
        destination_folder = Path() / artifact_type / artifact_name / artifact_alias
    elif not destination_folder.exists():
        destination_folder.mkdir(parents=True)
    elif not destination_folder.is_dir():
        raise TypeError(
            f"{destination_folder} is not a directory, but {type(destination_folder)}. "
            "Unable to download artifact there."
        )
    ref_api.wandb_start_run(
        w_run_name="texture-expand",
        w_job_type="generate-dataset",
        run_args=run_args,
    )
    ref_api.download_artifact(
        art_name=artifact_name,
        art_type=artifact_type,
        art_alias=artifact_alias,
        dst_folder=destination_folder,
    )
