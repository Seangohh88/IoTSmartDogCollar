import requests
import serial
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
import mysql.connector
import datetime
from PIL import Image
import requests
import torch
import cv2
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
#vid = cv2.VideoCapture(0)

logging.basicConfig(format="%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)i: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)
logger = logging.getLogger(__name__)
#initialize model and feature extractor
model=torch.load('hustvl_yolo_model.pth')
feature_extractor=torch.load('hustvl_yolo_extractor.pth')
vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
vid.release()
def take_picture():
    vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    ret, image = vid.read()
    vid.release()
    return image

def load_image_from_file(filename):
    return mpimg.imread(filename)

def detect_objects(image):
    image_np=np.array(image)
    fig, ax = plt.subplots()
    objects=dict()
    inputs = feature_extractor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    # model predicts bounding boxes and corresponding COCO classes
    logits = outputs.logits
    bboxes = outputs.pred_boxes
    score=torch.nn.functional.softmax(logits,dim=2)
    predictions=torch.argmax(score, dim=2)

    for n,i in enumerate(predictions[0]):
        if i!=91 and max(score[0,int(n)]) >=0.9 and i in [1,17,18]:
            print(str(model.config.id2label[int(i)])+" detected in image")
            try:
                objects[str(model.config.id2label[int(i)])]+=1
            except:
                objects[str(model.config.id2label[int(i)])]=1
            a,b,c,d=bboxes[0,n].detach().numpy()
            height=image_np.shape[0]
            width=image_np.shape[1]
            x,y,w,h=a-c/2,b-d/2,c,d
            x,y,w,h=x*width,y*height,w*width,h*height
            rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
    
    ax.imshow(image)
    filename=str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M'))+'_dogcam.png'
    plt.savefig(filename)
    #plt.show()
    return objects

def process_motion(payload):
    try:
        values=payload.split(':')
        col1,col2,col3=values[0],int(values[1]),int(values[2])
        if col1=='motion':
            image=take_picture()
            detected_objs=detect_objects(image)
            upload=0
            for obj in ['dog','cat','person']:
                if detected_objs.get(obj,-1) !=-1:
                    upload=1
                    sql = "INSERT INTO {}.logs (time, data_type, obj_id, value) VALUES (%s, %s, %s, %s)".format(dbname)
                    val = (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),str(col1)+str(obj), col2 , col3)
                    mycursor.execute(sql, val)
                    mqttc.publish(topic=f"{GATEWAY['name']}/sensor", payload=':'.join([str(col1)+str(obj), str(col2) , str(col3)]), qos=0)
                    print(obj+ ' detected')
                    if obj=='person':
                        send_to_telegram("Possible unauthorized person detected in room!")
                    if obj=='dog':
                        send_to_telegram("Dog detected in room!")

    except:
        pass

def send_to_telegram(message):

    apiToken = '5504181680:AAFDkPoZugfmsV8F10rtrv0S4ZhVaYdT-uk'
    chatID = '-817605075'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)
        
def payload_to_telegram(payload):
    try:
        values=payload.split(':')
        col1,col2,col3=values[0],int(values[1]),int(values[2])
        if col1=="missing":
            send_to_telegram("Dog signal is not detected in the last 1 minute! Dog might have ran out of house!!")
    except:
        pass
    
dbname='iotg4'

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="IoTRocks12!"
)

mycursor = mydb.cursor()

 
mqttc = None
 
GATEWAY = {"name" : "is614-g04-seantest",}

# Handles the case when the serial port can't be found
def handle_missing_serial_port() -> None:
    print("Couldn't connect to the micro:bit. Try these steps:")
    print("1. Unplug your micro:bit")
    print("2. Close Tera Term, PuTTY, and all other apps using the micro:bit")
    print("3. Close all MakeCode browser tabs using the micro:bit")
    print("4. Run this app again")
    exit()


# Initializes the serial device. Tries to get the serial port that the micro:bit is connected to
def get_serial_dev_name() -> str:
    import serial.tools.list_ports
    comlist = serial.tools.list_ports.comports()
    return comlist[0].device

 
# Handles an MQTT client connect event
# This function is called once just after the mqtt client is connected to the server.
def handle_mqtt_connack(client, userdata, flags, rc) -> None:
    logger.debug(f"MQTT broker said: {mqtt.connack_string(rc)}")
    if rc == 0:
        client.is_connected = True
 
   # Subscribing in on_connect() means that if we lose the connection and
   # reconnect then subscriptions will be renewed.
    client.subscribe(f"{GATEWAY['name']}/control")
    logger.info(f"Subscribed to: {GATEWAY['name']}/control")
    logger.info(f"Publish something to {GATEWAY['name']}/control and the messages will appear here.")

def write_to_sql(payload):
    #try block to cause serial port sometimes dont send data properly when microbit connected to browser
    #commit is done periodically in main.
    try:
        values=payload.split(':')
        col1,col2,col3=values[0],int(values[1]),int(values[2])    
        sql = "INSERT INTO {}.logs (time, data_type, obj_id, value) VALUES (%s, %s, %s, %s)".format(dbname)
        val = (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),col1, col2 , col3)
        mycursor.execute(sql, val)
    except:
        pass
    return
 
# Handles an incoming message from the MQTT broker.
def handle_mqtt_message(client, userdata, msg) -> None:
    logger.info(f"received msg | topic: {msg.topic} | payload: {msg.payload.decode('utf8')}")
    
    #write to sql on subscriber
    #write_to_sql(msg.payload.decode('utf8'))


# Handles incoming serial data
def handle_serial_data(s: serial.Serial) -> None:
    payload = s.readline().decode("utf-8").strip()


   # Publish data to MQTT broker
    logger.info(f"Publish | topic: {GATEWAY['name']}/sensor | payload: {payload}")
    mqttc.publish(topic=f"{GATEWAY['name']}/sensor", payload=payload, qos=0)
    
    #write to sql on publisher
    write_to_sql(payload)
    process_motion(payload)
    payload_to_telegram(payload)


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
 
   # Try to get the serial device name
    if args.device:
        serial_dev_name = args.device
    else:
        serial_dev_name = get_serial_dev_name()
 
    with serial.Serial(port=serial_dev_name, baudrate=115200, timeout=10) as s:
       # Sleep to make sure serial port has been opened before doing anything else
        print('port read success:'+str(serial_dev_name))
        time.sleep(1)

       # Reset the input and output buffers in case there is leftover data
        s.reset_input_buffer()
        s.reset_output_buffer()
 
       # Loopy loop
        counter=0
        while True:
            counter+=1
           # Read from the serial port
            if s.in_waiting > 0:
                handle_serial_data(s)
            if counter>=10:
                mydb.commit()
                counter=0
 
    mqttc.loop_stop()

if __name__ == "__main__":
    main()