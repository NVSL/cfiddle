default:

.PHONY: sdist
sdist:
	rm -rf build_release
	git clone . build_release
	(cd build_release; python setup.py build; python -m build)
