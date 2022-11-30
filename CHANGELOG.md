[comment]: # (Please do not modify this file)
[comment]: # (Put your comments to changelog.d and it will be moved to changelog in next release)
[comment]: # (Clear the text on make release for canceling the release)

[comment]: # (towncrier release notes start)

wabucketref v22.11.1 (2022-11-30)
=================================


Misc
----


- Bump minimal Python requirements to 3.8.1 due to 3.7.x EOL. ([#116](https://github.com/neuro-inc/mlops-wandb-bucket-ref/issues/116))


wabucketref v22.11.0 (2022-11-02)
=================================


Features
--------


- Added logarithmic backoff retries in case of error while downloading artifacts. ([#111](https://github.com/neuro-inc/mlops-wandb-bucket-ref/issues/111))

- Add `link` command to create W&B Artifacts out of previously existing binaries in storage. ([#112](https://github.com/neuro-inc/mlops-wandb-bucket-ref/issues/112))


Misc
----


- Added towncrier to generate changelog. ([#111](https://github.com/neuro-inc/mlops-wandb-bucket-ref/issues/111))
