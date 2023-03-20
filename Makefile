CHECKMARK=👍
SOURCEDIR=src
EXAMPLESDIR=examples
SOURCEDIRS=${SOURCEDIR} ${EXAMPLESDIR}


.PHONY: hello
hello:
	@echo '"And I have found both freedom of loneliness and the safety from being'"\n"\
	' understood, for those who understand us enslave something in us." - Khalil Gibran'


.PHONY: todo
todo:
	@grep -r --exclude=Makefile 'TODO:' .


.PHONY: venv
venv:
	@pipenv shell


.PHONY: test
test: install.stamp
	@echo "Running type checks ..."
	@pipenv run mypy ${SOURCEDIRS}
	@echo "Running linter ..."
	@pipenv run flake8 ${SOURCEDIRS}
	@echo "Runnig tests ..."
	@pipenv run pytest test
	
	
.PHONY: test-example
test_example: install.stamp .env
	@echo "Running flask versioned lru cache example ..."
	@pipenv run flask run
	
	
.PHONY: dev-install
dev-install: install.stamp


install.stamp:
	@((echo 'Checking for pipenv ...' && which pipenv > /dev/null) && echo "Found!")\
		|| pip install --user pipenv
	
	@echo "Installing deps. ... "
	@pipenv install --dev
	@echo "Restamping ..."
	@touch install.stamp


dist: install.stamp
	@pipenv run python -m build
	

.env:
	@echo 'Setting up env. ...'
	@echo 'FLASK_APP=${EXAMPLESDIR}/flask_mysql_app.py' > .env
	
	
.PHONY:	format
format: install.stamp
	@pipenv run black ${SOURCEDIRS}


.PHONY: build
build: dist


.PHONY: clean
clean:
	@(rm -r dist && echo ${CHECKMARK}); echo ''
	@(rm -r build && echo ${CHECKMARK}); echo ''
	@(rm install.stamp && echo ${CHECKMARK}); echo ''
	@(rm -r ${SOURCEDIR}/versioned_lru_cache.egg-info && echo ${CHECKMARK}); echo ''
	@(pipenv --rm && echo ${CHECKMARK}); echo ''
	@(rm .env && echo ${CHECKMARK}); echo ''
