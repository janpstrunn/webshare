#!/bin/env bash

active_device=$(nmcli -t -f DEVICE,STATE device status |
  grep -w "connected" |
  grep -v -E "^(dummy|lo:)" |
  awk -F: '{print $1}')
output=$(nmcli -e no -g ip4.address,ip4.gateway,general.hwaddr device show "$active_device")

ip_address=$(echo "$output" | sed -n '1p' | awk -F '/' '{print $1}')
echo " * Running on http://$ip_address:5000"

export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
