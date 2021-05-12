#!/usr/bin/env bash

VFC_INCLUDE_PATH=/usr/local/include
VFC_PYTHON_PATH=/usr/local/lib/python3.9/site-packages/verificarlo
VFC_BIN_PATH=/usr/local/bin

cp vfc_hashmap.h vfc_probes.h $VFC_INCLUDE_PATH

cp vfc_ci $VFC_BIN_PATH

cp vfc_ci $VFC_PYTHON_PATH
cp -r ci $VFC_PYTHON_PATH
cp sigdigits/sigdigits.py $VFC_PYTHON_PATH
