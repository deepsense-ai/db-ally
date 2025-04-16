#!/bin/bash

if [ ! -d venv ]; then
    python3.8 -m venv venv
    . venv/bin/activate
    pip install --upgrade pip
    pip install --quiet wheel==0.41.3
    pip install --quiet -r requirements-dev.txt
fi

. venv/bin/activate
