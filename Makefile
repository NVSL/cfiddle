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


.PHONY: docker
docker:
	rm -rf .clean_checkout
	git clone . .clean_checkout
	docker build --no-cache --progress plain -t stevenjswanson/fiddle:latest .

.PHONY: docker-test
docker-test: docker
	docker run -it --privileged -w /home/jovyan/fiddle/tests docker.io/stevenjswanson/fiddle:latest make test


.PHONY: push-docker
docker-push: docker-test
	docker push stevenjswanson/fiddle:latest

.PHONY: docker-pull
docker-pull:
	docker pull stevenjswanson/fiddle:latest
