#!/bin/bash

set -x
python3 example_safe.py
python3 example_safe.py help adder
python3 example_safe.py help product
python3 example_safe.py adder 1 2 3 4
python3 example_safe.py product 1 2 3 4
set +x
