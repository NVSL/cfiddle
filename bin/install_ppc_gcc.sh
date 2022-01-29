#!/usr/bin/env bash
set -ex
apt-get install -y g++-powerpc-linux-gnu gcc-powerpc-linux-gnu binutils-powerpc-linux-gnu

export CXX=powerpc-linux-gnu-g++
export CC=powerpc-linux-gnu-gcc

cd /tmp
rm -rf libpfm4;
git clone http://github.com/wcohen/libpfm4.git
cd libpfm4
make PREFIX=/usr/$($CC -print-multiarch) ARCH=powerpc lib install
