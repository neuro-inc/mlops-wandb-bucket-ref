FROM ghcr.io/neuro-inc/neuro-extras:23.7.0

LABEL org.opencontainers.image.source = "https://github.com/neuro-inc/mlops-wandb-bucket-ref"

ARG COMMIT_SHA
RUN pip install --no-cache-dir \
    "wabucketref @ git+https://github.com/neuro-inc/mlops-wandb-bucket-ref.git@${COMMIT_SHA}"
