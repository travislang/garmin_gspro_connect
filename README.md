## About

Integrates the garmin R10 with the GSPro software.
This is open source software that is for personal use only.

I am not responsible for what you use it for!

## Requirements

To run this application, your system must have python3.  Install directions: https://docs.python.org/3/using/windows.html#windows-full The only other package you need to install is yaml: `pip install pyyaml`

## Usage

clone this repo

Start GSPro and make sure you have GSPro Connect running.  There is times where you may need to restart the API Connect window so it's a good idea to add a shortcut to your desktop.

Open the command line and `cd` to this directory.  Run this command `python run.py`

You will see an IP and port in the temrinal:

```
IP Adrress: xxx.xxx.x.xx
Port: xxxx
```

Open the Garmin golf app and click on the E6 connect option.  Click the settings icon and make sure the IP and port match from the previous step.

Press the "Play on PC" button on your garmin app.

Now play golf!

This script will intercept all shot data and forward it to GSPro while simulatiously responding to the garmin app to keep it connected.
