#!/usr/bin/env bash

set -ex

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


#### development tools
apt-get update --fix-missing --allow-releaseinfo-change
apt-get install -y make less emacs-nox gcc g++  cmake gdb build-essential graphviz curl  && apt-get clean -y
apt-get install -y gcc-8 g++-8 || true # this fails on circleci for some reason


REDARE_VERSION=5.8.8
if ! r2 -V | grep -q 5.8.8; then 
    ##### Redare2 (for CFG generation)
    (set -ex; cd /tmp;
     rm -rf radare2;
     echo yes | git clone -b $REDARE_VERSION http://github.com/radareorg/radare2
     cd radare2
     chmod a+rwX -R . # Redare's install script gives up root.  This ensures we can still build.
     ./sys/install.sh --install
    )
else
    echo "Found Redare2 at " `which r2`
fi

##### Google test

if ! [ -e /usr/local/include/gtest/gtest.h ]; then
    (set -ex;
     cd /tmp;
     rm -rf googletest;
     git clone http://github.com/google/googletest.git && cd googletest && cmake CMakeLists.txt;
     make install
    )
else
    echo "Found google test installed"
fi

##### libpfm4
# we do this instead of apt-get because showevtinfo is very useful and it's not installed by default.
if [ -e /usr/local/bin/showevtinfo]; then
    (set -ex;
     cd /tmp;
     rm -rf libpfm4;
     echo yes | git clone http://github.com/wcohen/libpfm4.git && cd libpfm4 && make && make install && cp examples/showevtinfo /usr/local/bin
    )
else
    echo "Found libpfm and showevtinfo installed: " `which showevtinfo`
fi

##### perf
$SCRIPT_DIR/cfiddle_install_perf.sh

if ! [ x"$CFIDDLE_INSTALL_CROSS_COMPILERS" = x"no" ]; then
    $SCRIPT_DIR/cfiddle_install_compilers.sh
fi
	    

