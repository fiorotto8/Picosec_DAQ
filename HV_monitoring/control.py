#!/usr/bin/python3

import argparse
import sys

from prompt_toolkit import PromptSession

import hv

def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("board", type=str)
    args = parser.parse_args()

    board = hv.Board(args.board)
    if board.handle == 0:
        print("Connected to board with address", args.board)
    else:
        print("Error: could not connect to board with address", args.board)
        sys.exit(1)

    session = PromptSession()
    try:
        while True:
            try:
                command_text = session.prompt("control> ")
                command = command_text.split(" ")
                    
                if command[0] == "hv":
                    if command[1] == "info": print(board.crate_map)
                    elif command[1] == "parameters": print(board.parameters)
                    elif command[1] == "get":
                        channel = int(command[3])
                        if command[2] == "voltage": print(board.get_voltage(channel))
                        elif command[2] == "current": print(board.get_current(channel))
                        elif command[2] == "status": print(board.get_status(channel))
                        elif command[2] == "parameters": print(board.get_channel_parameters(channel))
                        else: print("Custom parameter {}:".format(command[2]), board.get_channel_value(channel, command[2]))
                    elif command[1] == "set":
                        channel = int(command[3])
                        value = float(command[4])
                        if command[2] == "voltage": board.get_voltage(channel)
                        elif command[2] == "current": board.set_current(channel)
                        #elif command[2] == "status": board.get_status(channel))
                        else: board.set_channel_value(channel, command[2], value)
                    else: print("Command", command[1], "not recognized")
                else: print("Command", command[0], "not recognized")

            except KeyboardInterrupt: pass

    except EOFError:
        print("Closing...")

if __name__=="__main__":
    main()
