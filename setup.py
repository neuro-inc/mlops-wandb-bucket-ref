import re

from setuptools import find_packages, setup


with open("wabucketref/__init__.py") as f:
    txt = f.read()
    try:
        version = re.findall(r'^__version__ = "([^"]+)"\r?$', txt, re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine the version.")

setup(
    name="wabucketref",
    version=version,
    python_requires=">=3.7.0",
    install_requires=[
        "wandb[aws]>=0.10.33,<0.12.21",
        "cloudpathlib[s3]>=0.4.1,<0.9.1",
    ],
    include_package_data=True,
    description=(
        "Run experiments, "
        "track artifacts via WandB, "
        "store artifacts in bucket and refer them in WandB"
    ),
    packages=find_packages(),
    entry_points={"console_scripts": ["wabucket=wabucketref.cli:main"]},
    zip_safe=False,
)
