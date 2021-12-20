default:

.PHONY: sdist
sdist:
	rm -rf build_release
	git clone . build_release
	(cd build_release; python -m build)
	(cd build_release; python -m venv dist_test)
	(cd build_release; . dist_test/bin/activate;  pip install --upgrade pytest wheel build ; pip install dist/fiddle-0.1-py3-none-any.whl; cd tests; pytest .)

.PHONY:test
test: dist-test package-test

.PHONY: package-test
package-test:
	(cd tests; pytest .)


.PHONY: dist-test
dist-test:
	rm -rf .dist-test
	mkdir -p .dist-test
	(cd .dist-test; --
