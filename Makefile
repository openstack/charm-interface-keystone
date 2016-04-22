#!/usr/bin/make
PYTHON := /usr/bin/env python

clean:
	@rm -rf .testrepository .unit-state.db .tox
lint:
	@tox -e lint

test:
	@echo Starting unit tests...
	@tox -e py27
