# TODOs

5. Integrate libpfm4 (https://github.com/wcohen/libpfm4) so we can count everything.
2. Set up jupyterhub so anyone can log in and try it. 
1. Support for (de)serialization of resuls, spec,s etc. to json.  Running of same.
2. Support for remote exection (based on 5)
3. Error reporting on perf counters
	1.  Not available
	2.  Incompatable set of counters.
4. Documentation
   1.  Add change log to README.md
   2.  Add devel instructions to README.md
   3.  Update cross refs in docstrings.
   4.  Add doctests for code in documentation.
4. Write a function decorator to catch exception and print nice error messages in Jupyter
5. Create testing fixture so everything test runs in a new .cfiddle directory.
4. Build C-friendly version of cfiddle.hpp
6. Multiple workflow support
   1. Encapsulate a configuration in a Workflow object. (One for C, one for Rust,  remote execution, etc.)
   2. from cfiddle import * would pull in the default.
7. Arm support
   1. cross-compiler support
	  1. This mostly works "out of the box".  Issues/instructions:
		  1. apt-get install -y binutils-arm-linux-gnueabi g++-arm-linux-gnueabi gcc-arm-linux-gnueabi
		  2. set CXX=arm-linux-gnueabi-g++
		  3. bunch of "notes" in output of compiling libcfiddle.so
	      2. libcfiddle.so needs to be compiled for it.
		  3. searching for asm functions needs to search for `.fnend` instead of `.cfi_endproc`
8. Support for Rust and Go
   1. Use the FFI interfaces in each language to get access to libcfiddle.
   2. Extend the makefile.
9. Executable-based execution (rather than .so)
   1. Auto-generate code from python.
10. MacOS support
11. Windows support
12. Generalized measurement mechanism of which perf counters would be a special case.
13. Use `run()` to check characteristics of execution envirnoment
	1.  E.g. for remote execution, run a program to find the list of perf
        counters.  If you run it in on the execution environment, you'll get
        the currently-/workload-correct answer.
14. Automatically run a test several times and generate average/stdev etc.  Then automatically draw error bars		

# Notes

To get newer kernel on Ubunut 20.04:

1.  move to HWE releases: https://wiki.ubuntu.com/Kernel/LTSEnablementStack
2.  upgrade docker: https://askubuntu.com/questions/472412/how-do-i-upgrade-docker


   
# Notes On JupyterHub

2.  this worked  well enough to get docker hub running with cfiddle installed.
	1.  Challenge:  Making a single docker image work well with Binder and docker hub.
	2.  CAP_PERFMON
	3.  The user storage configuration was not robust.
	3.  I don't think it scaled past one node?
1.  adduser to create admin user.
1.  testing jupyter hub -- this doesn't support docker, which we need.
	1.  https://tljh.jupyter.org/en/latest/install/custom-server.html
	2.  https://tljh.jupyter.org/en/latest/howto/auth/nativeauth.html
		1.  I had to create my admin use again on the hub.
	3.  https://tljh.jupyter.org/en/latest/install/custom-server.html#step-3-install-conda-pip-packages-for-all-users
		2.  Install prereqs
		1.  pip install cfiddle
 2. Kubernetes
	1.  https://zero-to-jupyterhub.readthedocs.io/en/latest/
		* Setup Kubernetes
			1.  https://zero-to-jupyterhub.readthedocs.io/en/latest/kubernetes/other-infrastructure/step-zero-microk8s.html
				1.  https://microk8s.io/docs
				3.  https://microk8s.io/docs/getting-started  through step 4
			2.  works as expected
			3.  Not certain about this:  microk8s enable metallb:145.40.76.235-145.40.76.235
			4.  works, but not sure what it's doing.
			5.  Don't forget 'alias kubectl='microk8s kubectl'
		*  Setup JupyterHub
			1.  https://zero-to-jupyterhub.readthedocs.io/en/latest/jupyterhub/index.html
			2.  helm upgrade
				 1.  We are setting the release-name and the k8s-namespace
				 2.  instead of "helm list", do "microk8s helm3 list"
				 3.  microk8s helm3 upgrade --cleanup-on-fail   --install try-fiddle jupyterhub/jupyterhub   --namespace try-fiddle   --create-namespace   --version=1.2.0   --values config.yaml 
			3.  didn't do
			4.  worked
			5.  connet to proxy-public EXTERNAL_IP, but fiddle not installedh
		* set docker image: https://zero-to-jupyterhub.readthedocs.io/en/latest/jupyterhub/customizing/user-environment.html#choose-and-use-an-existing-docker-image
			1.  Same 'microk8s helm3 upgrade' command as above to enable changes.

