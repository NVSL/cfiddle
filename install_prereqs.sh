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
apt-get -y install flex bison && apt-get clean -y
# for some reason the .0 revisions don't exist on kernel.org.
kernel_version=$(uname -r | perl -ne '($m, $n, $r) = /(\d+)\.(\d+)\.(\d+)/; if ($r==0) {$r=1} print "$m.$n.$r"')
(rm -rf /tmp/perf;
 mkdir /tmp/perf;
 cd /tmp/perf;
 curl -L https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-$kernel_version.tar.xz -o linux-$kernel_version.tar.xz ;
 tar xf linux-$kernel_version.tar.xz;
 cd linux-$kernel_version;
 PYTHON=python3 make -C tools/perf install  DESTDIR=/usr/local)

if [ x"$CFIDDLE_INSTALL_CROSS_COMPILERS" = x"yes" ]; then
    bin/install_compilers.sh
fi
	    

