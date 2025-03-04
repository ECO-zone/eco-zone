# .PHONY defines parts of the makefile that are not dependant on any specific file
# This is most often used to store functions
.PHONY = *


# DEPLOY #
##########

deploy-dev:
	$(eval BRANCH := $(shell git rev-parse --abbrev-ref HEAD))
	git push --force eco-zone-dev ${BRANCH}:main


# TEST #
########

lint:
	pre-commit run --all-files

test:
	pytest --disable-warnings ./tests


# INIT #
########

asdf:
	asdf install || true

venv:
	python -m venv .venv --prompt=eco-zone
	. ./.venv/bin/activate

pip:
	python -m pip install -r ./requirements/dev.txt -r ./requirements/main.txt

init: asdf venv pip
