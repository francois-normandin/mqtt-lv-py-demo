# MQTT LabVIEW-Python Demo

This project is the support material for the UK TAG #7 (May 28th 2021) presentation.

## License
You are free to reuse all the demo code for your own needs, modify it and use it without attribution.
The PPT presentation is not part of the software license. If you reuse it or any part of it for your own training, please provide attribution.

## Abstract

"In this presentation, I will quickly introduce the MQTT protocol and present an all-LabVIEW open source implementation of MQTT Broker-Client libraries.
I'll then go through a couple demos featuring LabVIEW and Python MQTT clients to establish communication with an instrument acting as an MQTT server."

The demo consists of simulation of an instrument that can be controlled through a MQTT Server:
* A native LabVIEW MQTT Server is started on port 1883.
* The instrument connects through TCP, publishes its state and monitors requests (subscribes to a topic). It acts as the Model-Controller.
* A LabVIEW-based UI connects through TCP to the same server, subscribes to the instrument's state topic. It can send requests to change its state. It acts as the View.
* A Python-based UI connects through TCP and mimics the functionality in the LabVIEW-based UI.
* A LabVIEW wrapper can launch the Python-based User Interface.

## Pre-requisite

LabVIEW 2019
- Install the package dependencies with VIPM (installMe.vipc)

Python 3.5+
- pip install paho-mqtt
- pip install requests
- pip install PySimpleGUI
