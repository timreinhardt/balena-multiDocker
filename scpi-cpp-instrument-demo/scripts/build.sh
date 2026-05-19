#!/bin/bash
set -e

mkdir -p build
cd build
cmake ..
make

echo
echo "Built: build/scpi_cpp_demo"