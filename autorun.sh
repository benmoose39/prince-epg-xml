#!/bin/bash

echo $(dirname $0)

python3 -m pip install requests datetime

cd $(dirname $0)/

wget https://dl.dropboxusercontent.com/s/toq87dmqp5eh2b2/IPTV_tuner_epg.xml
python3 capture.py

echo $(date) > lastUpdated

echo programs saved
