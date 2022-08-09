# WaBucketRef

_Neu.ro platform integration with [Weights and Biases](https://wandb.ai/site) to store artifact binaries in Neu.ro buckets and refer them in WandB Artifact for lineage_

## Installation
You could install library directly from the GitHub.
All Github tags are tested. The backward compatibility is not guaranteed yet:

```bash
export WABUCKET_VERSION=v22.5.5
pip install "wabucketref @ git+https://github.com/neuro-inc/mlops-wandb-bucket-ref.git@$WABUCKET_VERSION"
```

## Usage
This library could be used either as a stand-alone console application to download or upload artifacts.

Or it could be used as SDK in combination with W&B to upload or download artifacts to/from Neu.ro platform while saving other metadata to W&B.

### Console usage
You could download and upload artifacts by two dedicated commands:
- `wabucket [GLOBAL OPTIONS] download [OPTIONS] ARTIFACT_TYPE ARTIFACT_NAME ARTIFACT_ALIAS`
- `wabucket [GLOBAL OPTIONS] upload [OPTIONS]`

The project name set by the global option `wabucket --project-name <project-name>` or the corresponding env var (`WANDB_PROJECT`). The project name is mandatory for both commands. The underlying platform bucket could be parameterised via the global `--bucket <name>` option, otherwise the bucket with the name equal to the project name will be used.

While downloading, you *could* parameterise output path with `-d, --destination-folder PATH` option. Otherwise, the artifact will be downloaded into current working directory: `./<artifact_type>/<artifact_name>/<artifact_alias>`. Check other

While uploading, you **must** specify artfact name and type `-n, --name TEXT` and `-t, --type TEXT` options respectively. The artifact alias will beset to UUID (default behaviour), specified manually with `-a, --alias TEXT` option, or set to the SHA value computed on run arguments if alias option is set to `"!run-config-hash"`.

Each download or upload execution creates a dedicated W&B Run. The Run name name could be parameterised with the global `--run_name <name>` option. All corresponding artifacts are attached to this run as either output (if uploading), or input (if downloading) for lineage.

Some metainfo about the source job (job ID, name, owner and tags) is attached to the W&B run, so it could be easily filtered and found.

Please, check other global command options via `wabucket --help` or dedicated options for upload/download via `wabucket upload --help` and `wabucket download --help` respectively.

### SDK usage
You could import wabucket python API client to manage artifacts and utilize W&B SDK in your script for more granular control on W&B runs, metrics and artifacts.

Here is an example, where one downloads artifact from the platform bucket "bucket-name". Afterwards, the model training happens which creates model metrics object and, serialises model at the `model_path` path at local file system.
Finally, those metrics are are loged in W&B system and model binary is stored under the platform bucket.

```python
from wabucketref import WaBucketRefAPI

api = WaBucketRefAPI(
    bucket="bucket-name",
    project_name="my-w&b-project",
)

folder = api.download_artifact("name", "type", "version")
metrics, model_path = do_train(artifact=folder)

wandb.run.log(metrics)
api.upload_artifact(model_path, "my-model", "model")
api.close() # Do not forget to release the resources!
```
