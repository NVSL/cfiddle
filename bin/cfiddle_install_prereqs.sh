#!/usr/bin/env bash


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if [ "$CFIDDLE_DEPS_INSTALL_PREFIX." == "." ]; then
    CFIDDLE_DEPS_INSTALL_PREFIX=/usr/local
fi


echo CFIDDLE_DEPS_INSTALL_PREFIX=$CFIDDLE_DEPS_INSTALL_PREFIX

#### development tools
apt-get update --fix-missing --allow-releaseinfo-change
apt-get install -y make less emacs-nox gcc g++  cmake gdb build-essential graphviz curl  && apt-get clean -y
apt-get install -y gcc-8 g++-8 || true # this fails on circleci for some reason

set -ex

REDARE_VERSION=5.8.8
##### Redare2 (for CFG generation)
(set -ex; cd /tmp;
 rm -rf radare2;
 echo yes | git clone -b $REDARE_VERSION http://github.com/radareorg/radare2
 cd radare2
 chmod a+rwX -R . # Redare's install script gives up root.  This ensures we can still build.
 sudo -u $SUDO_USER ./sys/install.sh --install --prefix=$CFIDDLE_DEPS_INSTALL_PREFIX
)


##### Google test
(set -ex;
 cd /tmp;
 rm -rf googletest;
 git clone http://github.com/google/googletest.git
 cd googletest
 cmake -D CMAKE_INSTALL_PREFIX=$CFIDDLE_DEPS_INSTALL_PREFIX CMakeLists.txt ;
 make install
)


##### libpfm4
# we do this instead of apt-get because showevtinfo is very useful and it's not installed by default.
(set -ex;
 cd /tmp;
 rm -rf libpfm4;
 echo yes | git clone http://github.com/wcohen/libpfm4.git
 cd libpfm4
 make PREFIX=${CFIDDLE_DEPS_INSTALL_PREFIX}
 make PREFIX=${CFIDDLE_DEPS_INSTALL_PREFIX} install
 cp examples/showevtinfo ${CFIDDLE_DEPS_INSTALL_PREFIX}/bin
)


##### perf
$SCRIPT_DIR/cfiddle_install_perf.sh

if ! [ x"$CFIDDLE_INSTALL_CROSS_COMPILERS" = x"no" ]; then
    export CFIDDLE_DEPS_INSTALL_PREFIX
    $SCRIPT_DIR/cfiddle_install_compilers.sh
fi
	    

