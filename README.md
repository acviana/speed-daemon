# speed-daemon

https://travis-ci.org/acviana/speed-daemon.svg?branch=main

This project is a dockerized Python [steamlit](https://www.streamlit.io/) application for exploring output JSON files from the [Speedtest CLI](https://www.speedtest.net/apps/cli).

## Collecting Data

You can collect data by wrapping the Speedtest CLI in the wrapper and process of your choice. An easy starting point is to used the provided `run_speedtest.sh` bash script and to deamonize the process using a cronjob.
