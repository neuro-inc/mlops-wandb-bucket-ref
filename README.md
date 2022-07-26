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
- `wabucket --project-name my-project download`
- `wabucket --project-name my-project upload`

The project name set by the flag or the corresponding env var (`WANDB_PROJECT`) is mandatory for both commands.

Each download or upload execution creates a dedicated W&B Run (which name could be parameterised by the global`--run_name <name>` option) and attaches the corresponding artifact to this run as eitheroutput, or input for lineage.
The underlying platform bucket could be parameterised via the global `--bucket <name>`option.

Some metainfo about the source job (job ID, name, owner and tags) is attached to the W&B run, so it could be easily filtered and found.

Please, check other command options via `wabucket --help`

### SDK usage
You could import wabucket python API client to manage artifacts and utilize W&B SDK in your script.

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
```
