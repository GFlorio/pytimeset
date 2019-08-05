#!/usr/bin/env bash
set -e

echo "### CYTHON ###"
cython -a timeset/timeset.pyx
echo "### SETUPTOOLS ###"
python3 setup.py build_ext --inplace
echo "### TESTING ###"
python3 -m unittest discover -s tests

if [ "$1" == "publish" ]; then
  echo "### BUILDING WHEEL ###"
  python3 setup.py sdist bdist_wheel
  echo "### PUBLISHING ###"
  python3 -m twine upload dist/*
fi
