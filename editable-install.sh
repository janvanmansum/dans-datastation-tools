#!/usr/bin/env bash

#
# Getting the generated setup.py so that pip can do an editable install. Poetry does not seem to support editable installs (yet?)
#
# See: https://github.com/python-poetry/poetry/discussions/1135#discussioncomment-145763
#
poetry build
tar --wildcards -xvf dist/*-$(poetry version -s).tar.gz -O '*/setup.py' > setup.py
pip install -e .

