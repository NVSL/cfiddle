
set -ex
apt-get install -y binutils-arm-linux-gnueabi g++-arm-linux-gnueabi gcc-arm-linux-gnueabi

export CXX=arm-linux-gnueabi-g++
export CC=arm-linux-gnueabi-gcc

cd /tmp;
rm -rf libpfm4;
git clone https://github.com/wcohen/libpfm4.git
cd libpfm4
make PREFIX=/usr/$($CC -print-multiarch) ARCH=arm lib install


