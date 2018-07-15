# CAN View
A USB-CanAnalyzer v7.00 python interface and GUI.

![picture of physical hardware](https://statics3.seeedstudio.com/seeed/file/2017-07/bazaar520252_img_2550a.jpg)

## Project Status
In beta, pretty darn untested. Use at your own risk!!!

## Disclaimer
Transmitting or interferring with CAN communication on vehicles, industrial equipment, etc. can cause property damage, injury, and death. Per the license of this software, use it at your own risk!!!

## Intro
This library is intended to support SEEEDstudio or ebay can/usb serial interfaces. They're the ones like [this](https://www.seeedstudio.com/USB-CAN-Analyzer-p-2888.html) or similar based on a QinHeng CH340 USB2 serial to USB adapter.

I purchased one and tested with it against a smattering of CAN devices (mostly for FRC robotics).
Protocol was snooped by "Viking Star" - a very special thanks to this individual and his [blog post](http://arduinoalternatorregulator.blogspot.com/2018/03/a-look-at-seedstudio-usb-can-analyzer.html).




## Other requirements
You must have Python 3.X (later is better) installed, with "pythonw.exe" on your system path.

## Files
`USBCanAnalyzerV7.py` is the primary interface into the hardware device itself. Include this file into your own projects if you wish
`can_view.py` is the top-level gui. Launch this script to show the user interface.

## Serial
I've cloned a static copy of pyserial into this repo, just as an initial development step. Feel free to use your own version if you pick this up.

## Functionality
In process.

- Send Packets
  - Extended mode only (Standard in the future)
- Receive packets
- Export messages to .csv
- FUTURE: Database Lookup (J1939)
- FUTURE: More configuration
- FUTURE: Loopback mode testing
- FUTURE: packet timing analysis (rx rate, deltas, etc.)
- FUTURE: Expose network diagnostics supported by the analyzer hardware
- FUTURE: Standalone release (not requiring Python)
