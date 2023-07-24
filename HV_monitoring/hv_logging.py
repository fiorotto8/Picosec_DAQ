import argparse
import time

from datetime import datetime
from xmlrpc.client import ServerProxy

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

import gas_function as gf

influx_config = dict(
    token = 'W68gp78QaRKWLR4E9AcNmwCfeui389AeT2hbWajcQ5XgxAHgfhX8i-JFU0UreemOIfBvAD0JoTbGmz-QuEFs6g==',
    org = "infn",
    url = "http://localhost:8086"
)

bucket = "HV"

current_labels = ["IMonH", "IMonL"]

log_path='/home/cms3/influxdb/ftmdaqAntonello/log_hv.txt'
def main():
    parser = argparse.ArgumentParser(description='Record L1As')
    parser.add_argument("--port ", type=int, default=8000)
    args = parser.parse_args()

    influx_config["bucket"] = bucket

    # Instantiate InfluxDB client and connect:
    client = influxdb_client.InfluxDBClient(
            url=influx_config["url"],
            token=influx_config["token"],
            org=influx_config["org"]
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)

    port = 8000
    hv_client = ServerProxy(f"http://localhost:{port}")
    #print("Connected to rpc server with port", port)
    gf.log("Connected to rpc server with port "+str(port), log_path)

    try:
        while True:
            time.sleep(5)
            for board in [0]:
                for channel in range(4):
                    voltage = hv_client.get(board, channel, "VMon")
                    current = hv_client.get(board, channel, current_labels[board])
                    VSet = hv_client.get(board, channel, "VSet")
                    ISet = hv_client.get(board, channel, "ISet")
                    
                    if ISet < current:
                        gf.log("WARNING: TRIP in channel: "+str(channel), log_path)
                    

                    current_point = influxdb_client.Point("HV").tag("Board", board).tag("Channel", channel).field("IMon", current)
                    voltage_point = influxdb_client.Point("HV").tag("Board", board).tag("Channel", channel).field("VMon", voltage)
                    VSet_point = influxdb_client.Point("HV").tag("Board", board).tag("Channel", channel).field("VSet", VSet) 
                    ISet_point = influxdb_client.Point("HV").tag("Board", board).tag("Channel", channel).field("ISet", ISet) 
                    write_api.write(bucket=influx_config["bucket"], org=influx_config["org"], record=current_point)
                    write_api.write(bucket=influx_config["bucket"], org=influx_config["org"], record=voltage_point)
                    write_api.write(bucket=influx_config["bucket"], org=influx_config["org"], record=VSet_point)
                    write_api.write(bucket=influx_config["bucket"], org=influx_config["org"], record=ISet_point)
                    
                    #print(f"[{datetime.now()}] board {board} channel {channel} current {current:1.2f} voltage {voltage:1.2f} Vset {VSet:1.2f} Iset {ISet:1.2f}")
    except KeyboardInterrupt:
        #print("Closing logging...")
        gf.log("Closing logging", log_path)

if __name__=="__main__": main()
