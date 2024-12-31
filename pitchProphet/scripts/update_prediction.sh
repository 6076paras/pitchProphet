#!/bin/bash

# error handling
set -e

# add poetry to PATH 
export PATH="$HOME/.local/bin:$PATH"

cd /Users/paraspokharel/Programming/pitchProphet

mkdir -p logs

poetry run python scripts/inference.py >> logs/prediction_updates.log 2>&1

exit 0
