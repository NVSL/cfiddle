#!/usr/bin/bash

set -ex

branch=$(git rev-parse --abbrev-ref HEAD)
ssh try-cfiddle.nvsl.io  "set -ex; rm -rf .remote_test; git clone -b $branch http://github.com/NVSL/fiddle.git .remote_test; cd .remote_test; bin/install-and-test.sh"
