import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import serial
import numpy as np
import pandas as pd
from datetime import datetime as dt


#utility
def log(msg, path='/home/cms3/influxdb/log_gas.txt'):  #function that write a log file witha specified message
    f=open(path, 'a') #open the log file, append mode
    f.write(str(dt.now())+" "+str(msg)+"\n") #write datetime and message
    f.close() #close the log file

#arduino
""" no more needed due to open/close serial port
def readArd(portname, baud):    #read arduino data and return response
    ser=serial.Serial(portname, baud) #open serial port
    #time.sleep(2)
    #ser.VTIME   = 0
    #ser.VMIN     = 0
    ser.write(b'R') # write R to ask data from arduino
    response=ser.readline()  #read arduino data from serial port, read until the end of the line
    ser.close() #close serial port
    return(response)
"""
def decodeArd(response):   #decode arduino response in float for influxdb
    response=response.decode("utf-8")  #decode from bit to str
    response=response.replace("\r","").replace("\n","")  #remove \n and \t from the str
    response=np.array(response.split(sep=";"), dtype="d")  #split the str with ";" as separator and convert into a float array
    return(response)

#TEST IF I NEED THIS THING????
def controlArd(response, len=6, check=82):  #TEST control lenght and the check word in the first and the last part of message, if wrong raise a badflag and print the reason
    if len(response)!=len:  #control the lenght of the message
        BadFlag=True
        print("Bad because data lenght isn't what expected")  #if bad flag is raised, print why
    if response[0] and response[len-1] != check:   #check the first and last word of the message
        BadFlag=True
        response=np.delete(response,0)   #cancel the first word after the check
        response=np.delete(response,len(response)-1)   #cancel the last word after the check
        print("Bad because check word not recognised")

#inFluxdb
def toFluxdb(measurement, value, bucket, api, org="infn",location="Picosec gas"):  #create and write infludb point
    point=Point.measurement(measurement).field("val", float(value)).tag("location", location)  #create influxdb point, measurement is the name of the measure
    api.write(bucket=bucket, org=org, record=point)  #write the defined point in the database
def query(range_start, bucket, measure, location, field,range_stop):   #create a query for influx
    query = 'from(bucket:"'+str(bucket)+'")\
    |> range(start: '+str(range_start)+',stop: '+str(range_stop)+')\
    |> filter(fn:(r) => r._measurement == "'+str(measure)+'")\
    |> filter(fn:(r) => r.location == "'+str(location)+'")\
    |> filter(fn:(r) => r._field == "'+str(field)+'")'  # query is created as a text string
    return(query)

def readTable(result):  # unpack table results from inFluxdb query
    results=[]
    for table in result:
        for record in table.records:
            results.append((record.get_value()))  #get the selected value
    return(np.array(results, dtype="d"))  # return results in an array

def fromFlux(url, token, org,range_start,range_stop, bucket, measure, location, field, mean): # take data from db
    write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org) #influxdb client
    query_api = write_client.query_api() # api communication
    q=query(range_start, bucket, measure, location, field, range_stop) #use the function query to create a proper query request
    result = query_api.query(org=org, query=q)
    res=readTable(result) #use readtable function to select interesting data
    if mean==True:
        return(res.mean())
    else:
        return(res)

