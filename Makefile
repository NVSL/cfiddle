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
	pip install dist/fiddle-0.1.tar.gz

.PHONY:
test-dist:
	(. build_release/dist_test/bin/activate; $(MAKE) -C build_release package-test)

.PHONY:test
test: dist-test package-test

.PHONY: package-test
package-test:
	(cd tests; pytest .)


.PHONY: dist-test
dist-test:
	rm -rf .dist-test
	mkdir -p .dist-test


.PHONY: docker
docker:
	docker build --progress plain -t stevenjswanson/fiddle:latest .

.PHONY: push-docker
	docker push stevenjswanson/fiddle:latest

