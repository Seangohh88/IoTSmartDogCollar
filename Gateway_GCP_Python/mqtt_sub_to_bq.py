import requests
import csv
import os
import subprocess
import json
import re
import paho.mqtt.client as mqtt
import sys
import logging
import argparse
import getpass
import random
import urllib
import pprint
import sched
import time
import datetime
import threading
import glob
import datetime
from google.cloud import bigquery
import datetime

client = bigquery.Client()
dataset_id='IoTG4'
schematable_id='logs'
table_ref=client.dataset(dataset_id).table(schematable_id)
table=client.get_table(table_ref)

#initialize empty row
rows_to_insert=[]

# Configure logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)i: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)
logger = logging.getLogger(__name__)
 
mqttc = None
 
GATEWAY = {"name" : "is614-g04-seantest",}


 
# Handles an MQTT client connect event
# This function is called once just after the mqtt client is connected to the server.
def handle_mqtt_connack(client, userdata, flags, rc) -> None:
    logger.debug(f"MQTT broker said: {mqtt.connack_string(rc)}")
    if rc == 0:
        client.is_connected = True
 
   # Subscribing in on_connect() means that if we lose the connection and
   # reconnect then subscriptions will be renewed.
    client.subscribe(f"{GATEWAY['name']}/sensor")
    logger.info(f"Subscribed to: {GATEWAY['name']}/sensor")
    logger.info(f"Publish something to {GATEWAY['name']}/sensor and the messages will appear here.")

def write_to_memory(payload):
    #try block to cause serial port sometimes dont send data properly when microbit connected to browser
    #commit is done periodically in main.
    global rows_to_insert
    try:
        values=payload.split(':')
        record=(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),values[0],int(values[1]),int(values[2]))    
        rows_to_insert.append(record)
    except:
        pass
    return

def write_to_bq():
    global rows_to_insert
    try:
        rows_to_insert,bq_data=[],rows_to_insert
        client.insert_rows(table, bq_data)
        print(str(len(bq_data)) + " rows inserted to bigquery table " + str(schematable_id))
    except:
        pass
    return

# Handles an incoming message from the MQTT broker.
def handle_mqtt_message(client, userdata, msg) -> None:
    logger.info(f"received msg | topic: {msg.topic} | payload: {msg.payload.decode('utf8')}")
    
    #write to sql on subscriber
    write_to_memory(msg.payload.decode('utf8'))


def main() -> None:
    global mqttc

   # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", type=str, help="serial device to use, e.g. /dev/ttyS1")

    args = parser.parse_args()
    args_device = args.device

   # Create mqtt client
    mqttc = mqtt.Client()
 
   # Register callbacks
    mqttc.on_connect = handle_mqtt_connack
    mqttc.on_message = handle_mqtt_message

    # Connect to broker
    mqttc.is_connected = False
    mqttc.connect("broker.mqttdashboard.com")
    mqttc.loop_start()
    time_to_wait_secs = 1
    while not mqttc.is_connected and time_to_wait_secs > 0:
        time.sleep(0.1)
        time_to_wait_secs -= 0.1
 
    if time_to_wait_secs <= 0:
        logger.error(f"Can't connect to broker.mqttdashboard.com")
        return
 
       # Loopy loop
    while True:
        time.sleep(600) #600
        #Write once per 10 minute and only if >60 rows
        #if len(rows_to_insert)>=60: #60
        write_to_bq()
 
    mqttc.loop_stop()

if __name__ == "__main__":
    main()