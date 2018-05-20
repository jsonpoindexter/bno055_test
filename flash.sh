#!/usr/bin/env bash
sudo esptool.py -p /dev/ttyUSB0 erase_flash
sudo esptool.py -p /dev/ttyUSB0 write_flash --flash_size=detect -fm dio 0 ~/Downloads/esp8266-20180511-v1.9.4.bin