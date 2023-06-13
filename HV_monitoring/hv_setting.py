import argparse
import time

from datetime import datetime
from xmlrpc.client import ServerProxy

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

import gas_function as gf

import sys

current_labels = ["IMonH", "IMonL"]
log_path='/home/cms3/influxdb/ftmdaqAntonello/log_hv.txt'

def main():
    parser = argparse.ArgumentParser(description='Record L1As')
    parser.add_argument("-p","--port ", type=int, default=8000, help="select port, defult 8000")
    parser.add_argument("-v", "--voltage", type=int, default=None, help="change voltage")
    parser.add_argument("-i", "--current", type=int, default=None, help="change current")
    parser.add_argument("-c","--channel", type=int, default=5, help="select channel")
    parser.add_argument("-b","--board", type=int, default=0, help="select board, default 0")
    #parser.add_argument("-d","--debug", default=None, help="print every values of every channel of the selected board")
    args = parser.parse_args()
    
    if args.channel>=5:
        gf.log("ERROR while changing PS parameters, missing channel indication or channel number too large", path=log_path)
        sys.exit(0)

    port = 8000
    hv_client = ServerProxy(f"http://localhost:{port}")
    print("Connected to rpc server with port", port)
    #gf.log("Connected to rpc server with port "+str(port), log_path)
    """  
    if args.debug is not None:      
        for channel in range(4):
            voltage = hv_client.get(args.board, channel, "VMon")
            current = hv_client.get(args.board, channel, current_labels[args.board])
            VSet = hv_client.get(args.board, channel, "VSet")
            ISet = hv_client.get(args.board, channel, "ISet")                

        print(f"[{datetime.now()}] board {args.board} channel {channel} current {current:1.2f} voltage {voltage:1.2f} Vset {VSet:1.2f} Iset {ISet:1.2f}")
        """  
    ISet = hv_client.get(args.board, args.channel, "ISet") # get previous values
    VSet = hv_client.get(args.board, args.channel, "VSet")
    if args.voltage is not None:   # change voltage if is asked
        hv_client.set(args.board, args.channel, "VSet", args.voltage)
        gf.log("Changed PS value in channel "+str(args.channel)+": VSet "+ str(VSet)+" |=> "+ str(args.voltage), log_path)
    if args.current is not None:   # change voltage if is asked
        hv_client.set(args.board, args.channel, "ISet", args.current) 
        gf.log("Changed PS value in channel "+str(args.channel)+": ISet "+ str(ISet)+" |=> "+ str(args.current), log_path)
    if args.current is None and args.voltage is None:
        gf.log("Tried to change PS values in channel "+str(args.channel)+", failed because of missing new values. ISet= "+ str(ISet)+" VSet= "+str(VSet), log_path)
    """      
    for board in [0]:
        for channel in range(4):
            voltage = hv_client.get(board, channel, "VMon")
            current = hv_client.get(board, channel, current_labels[board])
            VSet = hv_client.get(board, channel, "VSet")
            ISet = hv_client.get(board, channel, "ISet")                

            print(f"[{datetime.now()}] board {board} channel {channel} current {current:1.2f} voltage {voltage:1.2f} Vset {VSet:1.2f} Iset {ISet:1.2f}")
    """
    #gf.log("Changed PS values: VSet "+ str(VSet)+" |=> "+ str(args.voltage)+" ISet "+ str(ISet)+" |=> "+ str(args.current), log_path)
    if args.current and args.voltage is None:
        gf.log("Possible Error: missing new values", path=log_path)
    if args.current==ISet and args.voltage == VSet:
        gf.log("Possible Error: new values are equal to old ones", path=log_path)
if __name__=="__main__": main()