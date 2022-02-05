#!/usr/bin/env bash
#set -ex


while read prefix libpfm4_arch; do
    (
	apt-get install -y g++-$prefix gcc-$prefix binutils-$prefix || exit 0 # it's ok to fail here.  we just skip it
	
	export CXX=$prefix-g++
	export CC=$prefix-gcc
	
	cd /tmp
	rm -rf libpfm4;
	git clone http://github.com/wcohen/libpfm4.git
	cd libpfm4
	make PREFIX=/usr/$($CC -print-multiarch) ARCH=$libpfm4_arch lib install
    )
done <<EOF
powerpc-linux-gnu powerpc 
x86-64-linux-gnu x86_64 
arm-linux-gnueabi arm 
EOF
