#!/usr/bin/bash

set -ex

host=$1
shift

branch=$(git rev-parse --abbrev-ref HEAD)

ssh $host  "set -ex; rm -rf .remote_test; git clone -b $branch http://github.com/NVSL/fiddle.git .remote_test; cd .remote_test; bin/install-and-test.sh"
