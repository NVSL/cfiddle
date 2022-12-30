#!/usr/bin/env bash

set -ex

#### development tools
apt-get update --fix-missing --allow-releaseinfo-change
apt-get install -y make less emacs-nox gcc g++  cmake gdb build-essential graphviz curl  && apt-get clean -y
apt-get install -y gcc-8 g++-8 || true # this fails on circleci for some reason


##### Redare2 (for CFG generation)
(cd /tmp; rm -rf radare2; echo yes | git clone -b 5.5.4 http://github.com/radareorg/radare2;
 cd radare2;
 chmod a+rwX -R . # Redare's install script gives up root.  This ensures we can still build.
 ./sys/install.sh --install;
)

##### Google test
(cd /tmp; rm -rf googletest; git clone http://github.com/google/googletest.git && cd googletest && cmake CMakeLists.txt; make install)

##### libpfm4
# we do this instead of apt-get because showevtinfo is very useful and it's not installed by default.
(cd /tmp; rm -rf libpfm4; echo yes | git clone http://github.com/wcohen/libpfm4.git && cd libpfm4 && make && make install && cp examples/showevtinfo /usr/local/bin)


##### perf
bin/install_perf.sh

if ! [ x"$CFIDDLE_INSTALL_CROSS_COMPILERS" = x"no" ]; then
    bin/install_compilers.sh
fi
	    

