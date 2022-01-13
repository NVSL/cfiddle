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

FIDDLE_DOCKER_IMAGE=fiddle-devel

.PHONY: docker
docker:
	docker build --no-cache --progress plain -t stevenjswanson/$(FIDDLE_DOCKER_IMAGE):latest .

.PHONY: docker-test
docker-test: docker
	docker run -it --privileged -w /home/jovyan/fiddle/tests docker.io/stevenjswanson/$(FIDDLE_DOCKER_IMAGE):latest make test

.PHONY: push-docker
docker-release: FIDDLE_DOCKER_IMAGE=fiddle
docker-release: docker-release
	rm -rf .clean_checkout
	git clone https://github.com/NVSL/fiddle.git .clean_checkout
#	git clone . .clean_checkout
	(cd .clean_checkout; pip install .; $(MAKE) docker-push)
#	(cd .clean_checkout; pip install .; $(MAKE) docker-test)

docker-push: docker-test
	docker push stevenjswanson/$(FIDDLE_DOCKER_IMAGE):latest

.PHONY: docker-pull
docker-pull:
	docker pull stevenjswanson/$(FIDDLE_DOCKER_IMAGE):latest
