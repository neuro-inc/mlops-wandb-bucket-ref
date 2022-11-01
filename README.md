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
WaBucketRef could be used as a CLI application, or Python module to **upload** or **download** [W&B artifacts](https://docs.wandb.ai/guides/artifacts/construct-an-artifact#add-a-uri-reference) stored in Neu.ro platform Buckets. In this case, BLOBs are stored in Neu.ro Buckets backend system, while articat metadata is managed by W&B.

### Console usage
Refer to the dedicated [CLI.md](./CLI.md) usage file.

### SDK usage
You could import WaBucket python API client to manage artifacts and utilize W&B SDK in your script for more granular control on W&B runs, metrics and artifacts.

Here is an example, where one downloads artifact from the platform bucket "bucket-name". Afterwards, the model training happens which creates model metrics object and, serialises model at the `model_path` path at local file system.
Finally, those metrics are logged in W&B system, and the model binary is stored under the platform bucket.

```python
from wabucketref import WaBucketRefAPI

api = WaBucketRefAPI(
    bucket="bucket-name",
    project_name="my-w&b-project",
)

folder = api.download_artifact("name", "type", "version")
metrics, model_path = do_train(artifact=folder)

wandb.run.log(metrics) # Run is created by WaBucketRefAPI automatically at `download_artifact` method call.
api.upload_artifact(model_path, "my-model", "model")
api.close() # Do not forget to release the resources!
```
