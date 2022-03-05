# speed-daemon

https://travis-ci.org/acviana/speed-daemon.svg?branch=main

Speed Daemon is a project that collecst the JSON restuls of [Speedtest CLI](https://www.speedtest.net/apps/cli) runs and imports them into a SQL database for analysis.

## Collecting Data

You can collect data by wrapping the Speedtest CLI in the wrapper and process of your choice. An easy starting point is to used the provided `run_speedtest.sh` bash script and to deamonize the process using a cronjob.

## Usage

TODO
