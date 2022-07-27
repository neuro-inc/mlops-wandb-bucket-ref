FROM ghcr.io/neuro-inc/neuro-extras:22.2.2

LABEL org.opencontainers.image.source = "https://github.com/neuro-inc/mlops-wandb-bucket-ref"

ARG COMMIT_SHA
RUN pip install --no-cache-dir \
    "wabucketref @ git+https://github.com/neuro-inc/mlops-wandb-bucket-ref.git@${COMMIT_SHA}"
