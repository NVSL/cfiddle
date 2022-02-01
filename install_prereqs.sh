#!/usr/bin/env bash


set -ex

#### development tools
apt-get update --fix-missing --allow-releaseinfo-change
apt-get install -y make less emacs-nox gcc g++ gcc-8 g++-8 cmake gdb build-essential graphviz curl   && apt-get clean -y


##### Redare2 (for CFG generation)
#apt-get install -y radare2  # doesn't work because the version is old
#if [ x"$(uname -a)" = x"aarch64" ]; then
#    git clone https://github.com/radareorg/radare2
#    radare2/sys/install.sh
#else
(cd /tmp; git clone -b 5.5.4 https://github.com/radareorg/radare2;
 cd radare2;
 chmod a+rwX -R . # Redare's install script gives up root.  This ensures we can still build.
 ./sys/install.sh --install;
)
#    curl -L https://github.com/radareorg/radare2/releases/download/5.3.1/radare2-dev_5.3.1_amd64.deb -o /tmp/radare2-dev_5.3.1_amd64.deb
#    curl -L https://github.com/radareorg/radare2/releases/download/5.3.1/radare2_5.3.1_amd64.deb -o /tmp/radare2_5.3.1_amd64.deb
#    apt install /tmp/radare2_5.3.1_amd64.deb  /tmp/radare2-dev_5.3.1_amd64.deb
#fi


##### Go (for go support)
apt-get install -y golang-go
#curl -OL https://golang.org/dl/go1.16.7.linux-amd64.tar.gz
#tar -C /usr/local -xvf go1.16.7.linux-amd64.tar.gz


##### Google test
(cd /tmp; rm -rf googletest; git clone https://github.com/google/googletest.git && cd googletest && cmake CMakeLists.txt; make install)

##### libpfm4
# we do this instead of apt-get because showevtinfo is very useful and it's not installed by default.
(cd /tmp; rm -rf libpfm4; git clone https://github.com/wcohen/libpfm4.git && cd libpfm4 && make && make install && cp examples/showevtinfo /usr/local/bin)

if [ x"$CFIDDLE_INSTALL_CROSS_COMPILERS" = x"yes" ]; then
    for i in bin/install_*.sh; do
	$i
    done
fi
	    

