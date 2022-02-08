#!/bin/bash
# Exit on any failure
set -e -x

if [ ! -z $VIRTUAL_ENV ];then echo "Run deactivate first"; exit 1
fi

source .venv/bin/activate
