.PHONY: docs tests

docs:
	cd docs && make html

tests:
	python -m unittest discover -s tests/

verbose_tests:
	python -m unittest discover -s tests/ -v