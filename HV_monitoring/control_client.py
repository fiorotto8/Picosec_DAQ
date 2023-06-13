#!/usr/bin/python3

import argparse
import sys

from xmlrpc.client import ServerProxy

from prompt_toolkit import PromptSession

def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    args = parser.parse_args()

    hv_client = ServerProxy("http://localhost:8000")

    session = PromptSession()
    try:
        while True:
            try:
                command_text = session.prompt("control> ")
                command = command_text.split(" ")
                    
                if command[0] == "hv":
                    parameter = command[2]
                    board = int(command[3])
                    if command[1] == "get":
                        channel = int(command[4])
                        if parameter == "voltage": print(board.get_voltage(channel))
                        else: print("Custom parameter {}:".format(command[2]), hv_client.get(board, channel, parameter))
                    elif command[1] == "set":
                        channel = int(command[4])
                        value = float(command[5])
                        if command[2] == "voltage": board.get_voltage(channel)
                        else: hv_client.set(board, channel, parameter, value)
                    else: print("Command", command[1], "not recognized")
                else: print("Command", command[0], "not recognized")

            except KeyboardInterrupt: pass

    except EOFError:
        print("Closing...")

if __name__=="__main__":
    main()
