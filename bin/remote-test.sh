#!/usr/bin/bash

set -ex

branch=$1
shift

rm -rf .remote_test

git clone  http://github.com/NVSL/fiddle.git .remote_test
cd .remote_test
python3 -m venv venv
. venv/bin/activate
pip install .
cd tests
make test




