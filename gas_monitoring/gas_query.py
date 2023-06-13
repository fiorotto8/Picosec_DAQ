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
import math as m

#initialyse inFluxdb and inFluxdb variables
token = os.environ.get("INFLUXDB_TOKEN")
org = "infn"
url = "http://localhost:8086"
bucket="MixerPV"
location="Picosec gas"

#write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org) #influxdb client
#query_api = write_client.query_api()

#query=gf.query(range="-2h", bucket=bucket, measure="Temperature (K)", location="Picosec gas", field="val")

#result = query_api.query(org=org, query=query)
#temperature=[]
#Temperature=gf.readTable(result)

#print(Temperature)
#create variables for interesting quantities
temp=gf.fromFlux(url, token, org,range_start="-1h", range_stop="-1m",bucket=bucket, measure="Temperature (K)", location="Picosec gas", field="val", mean=True)
#humidity=gf.fromFlux(url, token, org,range_start="-2h",range_stop="-1h", bucket=bucket, measure="Humidity (RH)", location="Picosec gas", field="val")

print(temp)
