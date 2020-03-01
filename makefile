.PHONY: docs tests

docs:
	cd docsrc/ && make html -b coverage && cd ../docs/ && cp -a ./html/. ./

tests:
	python -m unittest discover -s tests/

verbose_tests:
	python -m unittest discover -s tests/ -v
    
coverage:
	coverage run --source=. -m unittest discover -s tests/
	coverage html -i
	coverage report
	echo "HTML version available at ./htmlcov/index.html"
	CMD /C start ./htmlcov/index.html

style:
	flake8 pedal/

publish:
	python setup.py sdist bdist_wheel
	twine upload ./dist/* --skip-existing