#!/bin/bash

# create virtual environment
python -m venv .venv
source .venv/bin/activate

# install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "virtual environment setup complete"