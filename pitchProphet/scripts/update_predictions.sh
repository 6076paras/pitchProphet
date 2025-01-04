#!/bin/bash
# error handling
set -e
# add poetry to PATH 
export PATH="$HOME/.local/bin:$PATH"

# change to project root directory
cd $PITCH_PROPHET_ROOT || { echo "Failed to change directory to $PITCH_PROPHET_ROOT"; exit 1; }

# create logs directory
mkdir -p logs

# run inference with logging
poetry run python pitchProphet/scripts/inference.py >> logs/prediction_updates.log 2>&1

exit 0
                     