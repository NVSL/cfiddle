#!/usr/bin/env bash

set -ex
if ! perf --version; then
    apt-get update --fix-missing -y
    apt-get -y install flex bison python3-pip && apt-get clean -y

    # these are from the warnings printed while building perf.
    apt-get install -y binutils-dev libiberty-dev libzstd-dev libcap-dev libnuma-dev libbabeltrace-dev libelf-dev libelf-dev libunwind-dev libaudit-dev libdw-dev systemtap-sdt-dev
     
    python3 -m pip install python-config
    
    pushd .
    if apt-get install -y linux-source; then
	echo "Using source from apt-get"
	kernel_version=$(uname -r | perl -ne '($m, $n, $r) = /(\d+)\.(\d+)\.(\d+)/; print "$m.$n.$r"')
	cd /usr/src/linux-source-$kernel_version
	rm -rf linux-source-$kernel_version
	tar xf *.bz2
	cd linux-source-$kernel_version
    else
	echo "Downloading source from kernel.org"
	# for some reason the .0 revisions don't exist on kernel.org.
	kernel_version=$(uname -r | perl -ne '($m, $n, $r) = /(\d+)\.(\d+)\.(\d+)/; if ($r==0) {$r=1} print "$m.$n.$r"')
	rm -rf /tmp/perf;
	mkdir /tmp/perf;
	pushd /tmp/perf;
	curl -L https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-$kernel_version.tar.xz -o linux-$kernel_version.tar.xz ;
	tar xf linux-$kernel_version.tar.xz;
	pushd linux-$kernel_version
    fi

    # somehow perf links against libcrypto.so.1.1, but it's not present.  So we disable
    PYTHON=python3 make -C tools/perf clean install  DESTDIR=/usr/local NO_LIBCRYPTO=1
    
    rm -rf /tmp/perf

    popd
else
    echo Found perf already installed at `which perf`
fi

