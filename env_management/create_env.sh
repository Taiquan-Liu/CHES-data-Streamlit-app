#!/bin/bash
# Exit on any failure
set -e -x

if [ ! -z $VIRTUAL_ENV ];then echo "Run deactivate first"; exit 1
fi

mkdir -p .venv
python3.9 -m venv .venv

source .venv/bin/activate

pip install -e .[development]
python3.9 -m ipykernel install --sys-prefix --name ches-data
