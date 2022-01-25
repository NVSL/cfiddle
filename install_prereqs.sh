#!/usr/bin/env bash

#### development tools
apt-get update --fix-missing --allow-releaseinfo-change
apt-get install -y make less emacs-nox gcc make g++ cmake gdb build-essential graphviz curl  && apt-get clean -y
#gcc-8 g++-8 libhdf5-dev uuid-runtime  openssh-client time  default-jdk

##### Redare2 (for CFG generation)
curl -L https://github.com/radareorg/radare2/releases/download/5.3.1/radare2-dev_5.3.1_amd64.deb -o /tmp/radare2-dev_5.3.1_amd64.deb
curl -L https://github.com/radareorg/radare2/releases/download/5.3.1/radare2_5.3.1_amd64.deb -o /tmp/radare2_5.3.1_amd64.deb
apt install /tmp/radare2_5.3.1_amd64.deb  /tmp/radare2-dev_5.3.1_amd64.deb

##### Go (for go support)
apt-get install -y golang-go
#curl -OL https://golang.org/dl/go1.16.7.linux-amd64.tar.gz
#tar -C /usr/local -xvf go1.16.7.linux-amd64.tar.gz

##### python stuff
pip install wheel

##### Google test
(cd /tmp; rm -rf googletest; git clone https://github.com/google/googletest.git && cd googletest && cmake CMakeLists.txt; make install)

##### libpfm4
# we do this instead of apt-get because showevtinfo is very useful and it's not installed by default.
(cd /tmp; rm -rf libpfm4; git clone https://github.com/wcohen/libpfm4.git && cd libpfm4 && make && make install && cp examples/showevtinfo /usr/local/bin)
