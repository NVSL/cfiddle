default:


BRANCH=$(shell git rev-parse --abbrev-ref HEAD)
export CFIDDLE_DOCKER_IMAGE=cfiddle:$(BRANCH)

FIDDLE_WHEEL=build_release/dist/cfiddle-$$(cat VERSION)-py3-none-any.whl
.PHONY:test
test:  package-test dist-test docker-test #remote-test

## Basic tests
.PHONY: package-test
package-test:
	$(MAKE) -C tests test

## Build and test docker image
.PHONY: docker
docker: dist
	docker build --no-cache --progress plain -t stevenjswanson/$(CFIDDLE_DOCKER_IMAGE)  --build-arg ARG_THIS_DOCKER_IMAGE_UUID=$(shell uuidgen) --build-arg FIDDLE_WHEEL=$(FIDDLE_WHEEL) .

.PHONY: docker-test
docker-test: docker
	docker run -it --privileged -w /home/jovyan/cfiddle/tests docker.io/stevenjswanson/$(CFIDDLE_DOCKER_IMAGE) make test PYTEST_OPTS="-s -vv"

## Install current branch on remote machines and test there
.PHONY:remote-test
remote-test:
	bin/remote-test.sh try-cfiddle.nvsl.io
	@echo Finished try-cfiddle.nvsl.io
	bin/remote-test.sh arm.try-cfiddle.nvsl.io
	@echo Finished arm.try-cfiddle.nvsl.io


## Build release and test it
.PHONY:
dist-test: dist
	(. build_release/dist_test/bin/activate; pip install $(FIDDLE_WHEEL); $(MAKE) -C build_release package-test)

.PHONY: dist
dist:
	rm -rf build_release
	git clone . build_release
	python -m venv build_release/dist_test
	(. build_release/dist_test/bin/activate; $(MAKE) -C build_release do-dist)

.PHONY:do-dist
do-dist:
	pip install --upgrade pytest wheel build pytest-xdist pytest-cpp nbmake
	python3 -m build


## Do the release
.PHONY: release
release: pypi docker-release

.PHONY:pypi
pypi: release-check dist
	twine upload --verbose  build_release/dist/*

.PHONY: docker-release
docker-release:
	git update-index --refresh 
	[ "$(BRANCH)" != "main" ] || git diff-index --quiet HEAD -- # require no local changes if we are on main
	[ "$(BRANCH)" != "main" ] || [ x"$$(git rev-parse main)" = x"$$(git rev-parse origin/main)" ] # make sure we are synced, if we are on main
	rm -rf .clean_checkout
	git clone . .clean_checkout
	(cd .clean_checkout; $(MAKE) docker-push)
	[ "$(BRANCH)" = "main" ] && docker tag stevenjswanson/$(CFIDDLE_DOCKER_IMAGE) stevenjswanson/cfiddle:latest
	[ "$(BRANCH)" = "main" ] && docker tag stevenjswanson/$(CFIDDLE_DOCKER_IMAGE) stevenjswanson/cfiddle:v$(shell cat VERSION)
	[ "$(BRANCH)" = "main" ] && docker push stevenjswanson/cfiddle:latest
	[ "$(BRANCH)" = "main" ] && docker push stevenjswanson/cfiddle:v$(shell cat VERSION)


.PHONY: release-check
release-check:
	git update-index --refresh 
	[ "$(BRANCH)" = "main" ]  # make sure we are on main
	git diff-index --quiet HEAD -- # require that there be no local changes
	[ x"$$(git rev-parse main)" = x"$$(git rev-parse origin/main)" ] # make sure we are synced

.PHONY: docs
docs:
	make -C docs html

.PHONY: serve-docs
serve-docs: docs
	python -m http.server --directory docs/build/html/

.PHONY: wc
wc:
	wc -l tests/*.py | sort -n
	wc -l $$(find src/cfiddle -name '*.py') | sort -n


.PHONY: docker-push
docker-push: docker-test
	docker push stevenjswanson/$(CFIDDLE_DOCKER_IMAGE)

.PHONY: docker-pull
docker-pull:
	docker pull stevenjswanson/$(CFIDDLE_DOCKER_IMAGE)

