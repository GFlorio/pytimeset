#!/usr/bin/env bash
set -e

cython timeset.pyx
python3 setup.py build_ext --inplace