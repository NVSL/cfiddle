default:

.PHONY: dist
dist:
	rm -rf build_release
	git clone . build_release
	python -m venv build_release/dist_test
	(. build_release/dist_test/bin/activate; $(MAKE) -C build_release do-dist)

.PHONY:do-dist
do-dist:
#	pip install --upgrade pytest wheel build ; pip install dist/fiddle-0.1-py3-none-any.whl; cd tests; pytest .
	pip install --upgrade pytest wheel build 
	python -m build
#pip install dist/fiddle-0.1.tar.gz

.PHONY:
test-dist:
	(. build_release/dist_test/bin/activate; $(MAKE) -C build_release package-test)

.PHONY:test
test: dist-test package-test

.PHONY: package-test
package-test:
	$(MAKE) -C tests test


.PHONY: dist-test
dist-test:
	rm -rf .dist-test
	mkdir -p .dist-test


.PHONY: docker
docker:
	docker build --no-cache --progress plain -t stevenjswanson/fiddle:latest .

.PHONY: push-docker
docker-push: docker-test
	docker push stevenjswanson/fiddle:latest

.PHONY: docker-test
docker-test: docker
	docker run -it -w /home/jovyan/fiddle/tests docker.io/stevenjswanson/fiddle:latest make test

.PHONY: install-prereqs
install-prereqs:
	apt-get update --fix-missing; apt-get update
	apt-get install -y less emacs-nox gcc make g++ cmake gdb build-essential graphviz curl && apt-get clean -y
        #gcc-8 g++-8 libhdf5-dev uuid-runtime  openssh-client time  default-jdk
        ##### Redare2
	curl -L https://github.com/radareorg/radare2/releases/download/5.3.1/radare2-dev_5.3.1_amd64.deb -o /tmp/radare2-dev_5.3.1_amd64.deb
	curl -L https://github.com/radareorg/radare2/releases/download/5.3.1/radare2_5.3.1_amd64.deb -o /tmp/radare2_5.3.1_amd64.deb
	apt install /tmp/radare2_5.3.1_amd64.deb  /tmp/radare2-dev_5.3.1_amd64.deb
        ##### python stuff
	pip install wheel			   
        ##### Google test
	(cd /tmp; git clone https://github.com/google/googletest.git && cd googletest && cmake CMakeLists.txt; make install)
