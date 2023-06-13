#!/usr/bin/env python3
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import serial
import numpy as np
import pandas as pd
import gas_function as gf
import time
import signal
import sys
import datetime
from datetime import datetime as dt

#Analyse the gas status, every function is defined in gas_function.py. Data are stored in inFluxdb
# log file path
def signal_handler(sig, frame):  #trapping signal
    gf.log(msg='closed by SIGINT')
    ser.close() #close serial port
    sys.exit(0) #stop the cycle

#arduino variables
portname='/dev/ttyACM0'
baud = 115200

#initialyse inFluxdb and inFluxdb variables
token = 'QN3yxz9Z__-y6AR2YklDhz0rTsm33cZFY0fpUwO1luu2PTmT70kjPpEKr748ux4kkSTLn1X1cjbyru0sMCf9GA=='
org = "infn"
url = "http://localhost:8086"
bucket="testbucket"
location="Picosec gas"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org) #influx client
write_api = write_client.write_api(write_options=SYNCHRONOUS)

gf.log(msg='started') #write that the program is now running in the log file

ser=serial.Serial(portname, baud) #open serial port
time.sleep(2) # give time to the serial port in order to be ready, if not the code will be stuck forever without reading any data from serial port

while(True):   #infinite loop for measure temperature, humidity, voc and pressure, interrupt if badflag turn true
    #read arduino data
    ser.write(b'R') # write R to ask data from arduino
    response=ser.readline()  #read arduino data from serial port, read until the end of the line
    #response=gf.readArd(portname, baud)  #read arduino data, no more needed due to problem in function
    #print(response)
    response=gf.decodeArd(response)      #decode arduino data from byte to str and return float array data

    #send data to inFluxdb

    gf.toFluxdb("Temperature [K]", response[0], bucket, write_api, org, location)  #send temperature
    gf.toFluxdb("Pressure [Pa]", response[1], bucket, write_api, org, location)    #send pressure
    gf.toFluxdb("Humidity [RH]", response[2],  bucket, write_api, org, location)    #send humidity
    gf.toFluxdb("VOC [Ohm]", response[3],  bucket, write_api,  org, location)        #send voc as resistance of sensor

    time.sleep(10)  #wait 10 seconds before sending new points

    signal.signal(signal.SIGINT, signal_handler)
