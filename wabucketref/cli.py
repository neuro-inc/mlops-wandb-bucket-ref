from __future__ import annotations

from pathlib import Path
from typing import Sequence

import click
from click import Context

from . import WaBucketRefAPI, __version__, parse_meta


@click.group()
@click.version_option(
    version=__version__, message="W&B bucket artifacts package version: %(version)s"
)
@click.option(
    "--bucket",
    type=str,
    help="Platform bucket ID or string name, which will be used to store the artifacts",
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
    "--entity",
    type=str,
    help=(
        "W&B entity. A username or team name where you're sending runs. "
        "See https://docs.wandb.ai/ref/python/init for more details."
    ),
)
@click.pass_context
def main(
    ctx: Context,
    bucket: str | None,
    project_name: str | None,
    run_name: str | None,
    job_type: str | None,
    entity: str | None,
) -> None:
    """
    Upload to and download from platform buckets artifacts, stored in W&B.
    """
    api = WaBucketRefAPI(
        bucket=bucket,
        project_name=project_name,
        entity=entity,
    )
    ctx.obj = {
        "wabucket": api,
        "run_params": {
            "w_run_name": run_name,
            "w_job_type": job_type,
        },
    }
    ctx.call_on_close(api.close)


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
    help="W&B artifact type to assign",
)
@click.option(
    "-a",
    "--alias",
    "alias",
    type=str,
    help="W&B artifact alias to assign",
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
        "Whether to upload artifact to bucket and use it as reference in W&B, "
        "or directly upload the folder to W&B servers."
    ),
)
@click.option(
    "-s",
    "--suffix",
    type=str,
    help=(
        "Suffix to append to the output names 'artifact_type', "
        "'artifact_name' and 'artifact_alias', which are read by the Neuro-Flow. "
        "This is usefull if you need to upload several artifacts "
        "from within a single job."
    ),
)
@click.pass_context
def upload(
    ctx: Context,
    src_dir: str,
    name: str,
    type_: str,
    alias: str | None,
    metadata: Sequence[str],
    reff: bool,
    suffix: str | None,
) -> None:
    """
    Upload artifact from local folder to the bucket
    and store it's reference in W&B artifact
    """
    ref_api: WaBucketRefAPI = ctx.obj["wabucket"]
    meta = parse_meta(metadata)
    ref_api.wandb_start_run(
        w_run_name=ctx.obj["run_params"]["w_run_name"],
        w_job_type=ctx.obj["run_params"]["w_job_type"],
    )

    ref_api.upload_artifact(
        src_folder=Path(src_dir),
        art_name=name,
        art_type=type_,
        art_alias=alias,
        art_metadata=meta,
        as_refference=reff,
        suffix=suffix,
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
    destination_folder: Path | None,
    run_args: str | None,
) -> None:
    """
    Download artifact of specified type, name and version.
    """
    ref_api: WaBucketRefAPI = ctx.obj["wabucket"]
    if destination_folder is None:
        destination_folder = Path() / artifact_type / artifact_name / artifact_alias
    elif not destination_folder.exists():
        destination_folder.mkdir(parents=True)
    elif not destination_folder.is_dir():
        raise TypeError(
            f"Destination '{destination_folder}' exists, but not a directory. "
            "Unable to download artifact there."
        )
    ref_api.wandb_start_run(
        w_run_name=ctx.obj["run_params"]["w_run_name"],
        w_job_type=ctx.obj["run_params"]["w_job_type"],
        run_args=run_args,
    )
    ref_api.download_artifact(
        art_name=artifact_name,
        art_type=artifact_type,
        art_alias=artifact_alias,
        dst_folder=destination_folder,
    )
