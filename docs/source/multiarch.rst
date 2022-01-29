Multi-Architecture Support
==========================

Installing Cross Compilers
**************************

The CFiddle distribution includes scripts to install ARM and PowerPC cross
compilers under Ubuntu in :code:`bin/install_arm_cross.sh` and
:code:`bin/install_ppc_cross.sh`.

To get a new architecture working, you'll need to:

1. Build and install :code:`libpfm4` for your architecture (follow the model in the scripts above).
2. Build :code:`libcfiddle.so` -- follow the model in :code:`src/cfiddle/resources/libcfiddle/Makefile`.
      

Compiling for Other Architectures
*********************************








