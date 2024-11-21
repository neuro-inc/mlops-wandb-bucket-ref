FROM ghcr.io/neuro-inc/apolo-extras:24.10.0

LABEL org.opencontainers.image.source = "https://github.com/neuro-inc/mlops-wandb-bucket-ref"

ARG COMMIT_SHA
RUN pip install --no-cache-dir \
    "wabucketref @ git+https://github.com/neuro-inc/mlops-wandb-bucket-ref.git@${COMMIT_SHA}"
