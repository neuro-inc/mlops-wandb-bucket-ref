# CLI reference

## wabucket

Upload to and download from platform buckets artifacts, stored in W&B.

**Usage:**

```bash
wabucket [OPTIONS] COMMAND [ARGS]...
```

**Options:**

| Name | Description |
| :--- | :--- |
| _--version_ | Show the version and exit. |
| _--bucket TEXT_ | Platform bucket ID or string name, which will be used to store the artifacts |
| _--project-name TEXT_ | W&B project name, which should be used |
| _--run-name TEXT_ | W&B human-readable run name to distinguish among other runs |
| _--job-type TEXT_ | W&B human-readable job type to group similar jobs together in the reports |
| _--entity TEXT_ | W&B entity. A username or team name where you're sending runs. See https://docs.wandb.ai/ref/python/init for more details. |
| _--help_ | Show this message and exit. |

**Commands:**

| Usage | Description |
| :--- | :--- |
| [_wabucket download_](CLI.md#wabucket-download) | Download artifact of specified type, name and version. |
| [_wabucket upload_](CLI.md#wabucket-upload) | Upload artifact from local folder to the bucket and store it's reference in... |

### wabucket download

Download artifact of specified type, name and version.

**Usage:**

```bash
wabucket download [OPTIONS] ARTIFACT_TYPE ARTIFACT_NAME ARTIFACT_ALIAS
```

**Options:**

| Name | Description |
| :--- | :--- |
| _-d, --destination-folder PATH_ | Path where the artifact should be stored. Otherwise, './{artifact\_type}/{artifact\_name}/{artifact\_alias}' will be used |
| _-a, --run\_args TEXT_ | Args of current run. Provide this argument for calculating a proper artifact alias. Otherwise, the 'latest' will be used. |
| _--help_ | Show this message and exit. |

### wabucket upload

Upload artifact from local folder to the bucket and store it's reference in W&B artifact

**Usage:**

```bash
wabucket upload [OPTIONS] SRC_DIR
```

**Options:**

| Name | Description |
| :--- | :--- |
| _-n, --name TEXT_ | W&B artifact name to assign  \[required\] |
| _-t, --type TEXT_ | W&B artifact type to assign  \[required\] |
| _-a, --alias TEXT_ | W&B artifact alias to assign |
| _-m, --metadata KEY=VALUE_ | Metainfo, which will be pinned to the artifact after upload. |
| _--reff / --no-reff_ | Whether to upload artifact to bucket and use it as reference in W&B, or directly upload the folder to W&B servers. |
| _-s, --suffix TEXT_ | Suffix to append to the output names 'artifact\_type', 'artifact\_name' and 'artifact\_alias', which are read by the Neuro-Flow. This is usefull if you need to upload several artifacts from within a single job. |
| _--help_ | Show this message and exit. |
