# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

from os import getenv

import adafruit_esp32spi.adafruit_esp32spi_wifimanager as wifimanager
import board
import busio
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from digitalio import DigitalInOut

import adafruit_wsgi.esp32spi_wsgiserver as server
from adafruit_wsgi.wsgi_app import WSGIApp

# Get WiFi details, ensure these are setup in settings.toml
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")

# This example depends on a WSGI Server to run.
# We are using the wsgi server made for the ESP32

print("ESP32 SPI simple web app test!")


# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

# If you have an externally connected ESP32:
# esp32_cs = DigitalInOut(board.D9)
# esp32_ready = DigitalInOut(board.D10)
# esp32_reset = DigitalInOut(board.D5)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

"""Use below for Most Boards"""
status_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)  # Uncomment for Most Boards
"""Uncomment below for ItsyBitsy M4"""
# import adafruit_dotstar as dotstar
# status_pixel = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=1)

## If you want to connect to wifi:
wifi = wifimanager.WiFiManager(esp, ssid, password, status_pixel=status_pixel, debug=True)
wifi.connect()

## If you want to create a WIFI hotspot to connect to:
# wifi = wifimanager.WiFiManager(esp, "My ESP32 AP!", "supersecret", status_pixel=status_pixel)
# wifi.create_ap()

## To you want to create an un-protected WIFI hotspot to connect to:"
# wifi = wifimanager.WiFiManager(esp, "My ESP32 AP!", password=None, status_pixel=status_pixel)
# wifi.create_ap()

# Here we create our application, registering the
# following functions to be called on specific HTTP GET requests routes

web_app = WSGIApp()


@web_app.route("/led_on/<r>/<g>/<b>")
def led_on(request, r, g, b):
    print("led on!")
    status_pixel.fill((int(r), int(g), int(b)))
    return ("200 OK", [], "led on!")


@web_app.route("/led_off")
def led_off(request):
    print("led off!")
    status_pixel.fill(0)
    return ("200 OK", [], "led off!")


# Here we setup our server, passing in our web_app as the application
server.set_interface(esp)
wsgiServer = server.WSGIServer(80, application=web_app)

print("open this IP in your browser: ", esp.pretty_ip(esp.ip_address))

# print(esp.get_time())
# Start the server
wsgiServer.start()
while True:
    # Our main loop where we have the server poll for incoming requests
    try:
        wsgiServer.update_poll()
        # Could do any other background tasks here, like reading sensors
    except (ValueError, RuntimeError) as e:
        print("Failed to update server, restarting ESP32\n", e)
        wifi.reset()
        continue
