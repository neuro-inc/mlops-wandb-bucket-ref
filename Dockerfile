FROM neuromation/neuro-extras:latest
ARG COMMIT_SHA
RUN pip install --no-cache-dir \
    "wabucketref @ git+https://github.com/neuro-inc/mlops-wandb-bucket-ref.git@${COMMIT_SHA}"
