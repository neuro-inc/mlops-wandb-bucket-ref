FROM python:3.7.13-slim-bullseye as build

LABEL org.opencontainers.image.source = "https://github.com/neuro-inc/mlops-wandb-bucket-ref"

COPY . /tmp/wabucketref
RUN pip install --no-cache-dir /tmp/wabucketref
