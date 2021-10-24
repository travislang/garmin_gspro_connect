## About The Project

Integrates the garmin R10 with the GSPro software.
This is for personal use only and I am not responsible for what you do with it!

## Requirements

To run this application, your system must have python3+. The only other package you need to install is yaml: `pip3 install pyyaml`

## Usage

clone this repo

Open the `config.yml` file and add your local computer IP and port to the garmin section:
```
garmin:
  ip_address: 192.1xx.x.xx
  port: 2483
```
Keep everything else the same

Start GSPro and make sure you have GSPro Connect running.

Open the Garmin golf app and click on the E6 connect option.  Click the settings icon and make sure the IP and port match from the previous step.

Run this script: `python3 run.py`

Press the "Play on PC" button on your garmin app.

Now play golf!

This script will intercept all shot data and forward it to GSPro while simulatiously responding to the garmin app to keep it connected.
