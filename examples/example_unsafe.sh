#!/bin/bash

set -x
python3 example_unsafe.py
python3 example_unsafe.py help adder
python3 example_unsafe.py help product
python3 example_unsafe.py adder 1 2 "1+2" "2*2"
python3 example_unsafe.py product 1 2 "sum([1,2])" "2**2"
set +x
