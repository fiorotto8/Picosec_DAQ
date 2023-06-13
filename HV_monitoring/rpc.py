#!/usr/bin/python3

import argparse
import sys

from xmlrpc.server import SimpleXMLRPCServer

import hv

import gas_function as gf

log_path='/home/cms3/influxdb/ftmdaqAntonello/log_hv.txt'

class HvService:
    def __init__(self, boards):
        self.boards = boards

    def get(self, board_number, channel, parameter):
        return self.boards[board_number].get_channel_value(channel, parameter)

    def set(self, board_number, channel, parameter, value):
        return self.boards[board_number].set_channel_value(channel, parameter, value)

    def get_parameters(self, board_number, channel):
        return

def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("boards", type=str, nargs="+")
    args = parser.parse_args()

    boards = list()
    for addr in args.boards:
        board = hv.Board(addr)
        if board.handle >= 0:
            #print("Connected to board with address", addr)
            gf.log("Connected to board with address "+str(addr), log_path)
        else:
            #print("Error: could not connect to board with address", addr)
            gf.log("Error: could not connect to board with address"+str(addr), log_path)
            sys.exit(1)
        boards.append(board)

    port = 8000
    with SimpleXMLRPCServer(("0.0.0.0", port), allow_none=True) as server:
        server.register_instance(HvService(boards))
        #print("Serving XML-RPC on localhost port:",port, "Address:", args.boards)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            #print("\nKeyboard interrupt received, exiting.")
            gf.log("server closed", log_path)
            sys.exit(0)

if __name__=="__main__":
    main()
