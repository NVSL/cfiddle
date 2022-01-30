#!/usr/bin/env bash

gcc-


set -ex
apt-get install -y binutils-x86-64-linux-gnu g++-x86-64-linux-gnu gcc-x86-64-linux-gnu

export CXX=x86_64-linux-gnu-g++
export CC=x86_64-linux-gnu-gcc

cd /tmp;
rm -rf libpfm4;
git clone https://github.com/wcohen/libpfm4.git
cd libpfm4
make PREFIX=/usr/$($CC -print-multiarch) ARCH=x86_64 lib install


