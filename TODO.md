# TODOs

5. Integrate libpfm4 (https://github.com/wcohen/libpfm4) so we can count everything.
2. Set up jupyterhub so anyone can log in and try it.
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
			   2.  I think it takes a long time because it's downloading the docker image?
					
# Notes

To get newer kernel on Ubunut 20.04:

1.  move to HWE releases: https://wiki.ubuntu.com/Kernel/LTSEnablementStack
2.  upgrade docker: https://askubuntu.com/questions/472412/how-do-i-upgrade-docker


   
