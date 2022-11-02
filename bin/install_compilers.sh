#!/usr/bin/env bash
set -x


# GCC cross compilers
while read prefix libpfm4_arch extra_packages; do
    (

	package_suffix=$(echo $prefix | sed 's/_/-/g;' )
	apt-get install -y g++-$package_suffix gcc-$package_suffix binutils-$package_suffix || exit 0 # it's ok to fail here.  we just skip it

	if [ x"$extra_packages" != x ]; then
	    apt-get install -y $extra_packages
	fi
	
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
x86_64-linux-gnu x86_64 
arm-linux-gnueabi arm g++-8-arm-linux-gnueabi gcc-8-arm-linux-gnueabi g++-arm-linux-gnueabi gcc-arm-linux-gnueabi
10 x86_64 g++-10
9  x86_64 g++-9
8  x86_64 g++-8
EOF

##### Go 
apt-get install -y golang-go
##### Clang
apt-get install -y clang

exit 0

