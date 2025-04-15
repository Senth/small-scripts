#!/usr/bin/python3

import paho.mqtt.client as mqtt


mqttc = mqtt.Client(transport='websockets')

mqttc.username_pw_set("test", "test")
mqttc.tls_set()
mqttc.connect("mosquitto.senth.org", 443, 30)

mqttc.loop_start()

mqttc.publish("test", "Hello, World!").wait_for_publish()
