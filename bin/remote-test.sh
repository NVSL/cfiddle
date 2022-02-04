#!/usr/bin/bash

set -ex

python3 -m venv venv
. venv/bin/activate
pip install .
cd tests
make test




