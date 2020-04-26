#!/bin/bash

export VOICEKIT_API_KEY=""
export VOICEKIT_SECRET_KEY=""

cd /opt/iqtek/voicekit-examples/python
source /opt/iqtek/voicekit-examples/python/venv/bin/activate
python3 recog_and_store.py -e ALAW --interim_results -r 8000 -c 1 --silence_duration_threshold 10.0
deactivate
