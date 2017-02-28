clean:
	bash -c "find . -name \*.pyc | xargs rm -f"

test:
	bash -c "coverage run --source='.' manage.py test"

deps:
	bash -c "pip install -r requirements.txt"
	bash -c "npm install"
	bash -c "bower install"
