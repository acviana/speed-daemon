#!/bin/sh

speedtest --json > "/home/pi/dev/speedtest/data/$(hostname)-$(date "+%Y-%m-%dT%H:%M:%SZ").json"
