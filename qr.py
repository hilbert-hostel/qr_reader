# import the necessary packages
import paho.mqtt.client as mqtt
import os
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
load_dotenv(verbose=True)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# set MQTT username,PW
USER = os.getenv("MQTT_USER")
PW = os.getenv("PW")


def on_connect(client, userData, flags, rc):
    print("Connected with result code " + str(rc))
    client.publish("RaspberryPi", "Connected")


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    if(msg.payload == "button"):
        print("something")
    if(msg.payload == "button2"):
        print("something")


def on_publish(client, userdata, result):
    print("data published \n")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected MQTT disconnection. Will auto-reconnect")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(USER, PW)
client.connect("m15.cloudmqtt.com", 14918, 60)

time.sleep(5)
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
                help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

csv = open(args["output"], "w")
found = set()

while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
    data = ""

    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

        data = data+barcodeData

        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(frame, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if barcodeData not in found:
            csv.write("{},{}\n".format(datetime.datetime.now(),
                                       barcodeData))
            csv.flush()
            found.add(barcodeData)

    cv2.imshow("Barcode Scanner", frame)
    key = cv2.waitKey(1) & 0xFF
    if (data != ""):
        print("Publish : " + data)
        client.publish("qrCode", data)

    if key == ord("q"):
        break
    time.sleep(1)


csv.close()
cv2.destroyAllWindows()
vs.stop()
