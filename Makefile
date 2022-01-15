default:

.PHONY: dist
dist:
	rm -rf build_release
	git clone . build_release
	python -m venv build_release/dist_test
	(. build_release/dist_test/bin/activate; $(MAKE) -C build_release do-dist)

.PHONY:do-dist
do-dist:
	pip install --upgrade pytest wheel build 
	python -m build

.PHONY:pypi
pypi: dist
	twine upload --verbose  build_release/dist/*

.PHONY:
test-dist:
	(. build_release/dist_test/bin/activate; $(MAKE) -C build_release package-test)

.PHONY:test
test:  package-test docker-test

.PHONY: package-test
package-test:
	$(MAKE) -C tests test

CFIDDLE_DOCKER_IMAGE=cfiddle-devel

.PHONY: docker
docker:
	docker build --no-cache --progress plain -t stevenjswanson/$(CFIDDLE_DOCKER_IMAGE):latest .

.PHONY: docker-test
docker-test: docker
	docker run -it --privileged -w /home/jovyan/cfiddle/tests docker.io/stevenjswanson/$(CFIDDLE_DOCKER_IMAGE):latest make test

.PHONY: push-docker
docker-release: CFIDDLE_DOCKER_IMAGE=cfiddle
docker-release: docker-release
	rm -rf .clean_checkout
	git clone https://github.com/NVSL/cfiddle.git .clean_checkout
#	git clone . .clean_checkout
	(cd .clean_checkout; pip install .; $(MAKE) docker-push)
#	(cd .clean_checkout; pip install .; $(MAKE) docker-test)

docker-push: docker-test
	docker push stevenjswanson/$(CFIDDLE_DOCKER_IMAGE):latest

.PHONY: docker-pull
docker-pull:
	docker pull stevenjswanson/$(CFIDDLE_DOCKER_IMAGE):latest
