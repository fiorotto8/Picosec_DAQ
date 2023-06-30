# Picosec_DAQ

This folder contains the tools useful to accomplish DAQ of a gas detector like Picosec. The inside of this repository is divided in other folders. `gas_monitoring` contains the code to get gas status data from an Arduino board and to write them into an inFluxdb database. In `HV_monitoring` are stored the programs that allow the user to control and monitor the CAEN power supply. The parameters of the power supply are also stored into inFluxdb.
Soon will be added a third repository in which will be stored the code for the DAQ from the scope.

# Requirements
For the monitoring of the HV:
1. Add the `CAENHVWrapper-6.3/bin/x86_64/` folder to your `$LD_LIBRARY_PATH` environment variable.
2. Install pycaenhv:
```bash
cd pycaenhv
python3 -m pip install --user -U .
```
These instructions will be repeated in the `HV_monitoring` folder.

For the scope part:
Install the vxi11 package to communicate with instruments, more info at:
```https://github.com/python-ivi/python-vxi11```

# Description of the programs
In this section, a brief description of the folders content and how it works will be given.

## gas_monitoring
The programs in this folder are used to monitor the gas status. The aim is reached using a bme680 sensor read by an Arduino board. The sensor is contained in a sealed box placed at the gas output line of the Picosec detector and provides the measure of temperature, pressure, humidity and VOC of the gas. 
The communication between the Arduino board and the computer happens via serial port.
Than the data collected are stored in inFluxdb, that provides to take into account the time.
The command line that starts the monitoring is:
``python3 gas.py``

### use of crontab
The program is thought to be started with as a cronjob as in the following example.
Open crontab:
-``crontab -e ``
install a cronjob:
- ``0 0 * * * python3 path_to_file/gas.py >> path_to_logfile/logfile.txt 2>&1``
- ``59 23 * * * ps -axu | grep gas.py | awk '{print $2}' | xargs kill -SIGINT``
The two rows written above allow the code to start every day at 00:00 and to kill the program sending a `SIGINT` signal every day at 23:59.
`2>&1` is used to write an error message in the log file if something in the cronjob doesn't work.

 ### gas.py
 This program is the main tool for gas monitoring. In the beginning, there is the declaration of all the variables used for the communication with both the Arduino board (port name and baud rate) and the inFlux server (token, URL, etc.). Please pay attention after the reboot of the computer because the serial port name may be changed.
 After that the inFlux client is initialized and a message saying that the code is starting is written in a log file.
Then the serial port is opened and the program will wait a few seconds to get the time to conclude the operation properly.
 The monitoring is operated by an infinite while loop which can eventually be stopped by a SIGINT (keyboard interrupt) signal trapped to write a message in the log file and close the serial port before exiting without reporting errors.
 The communication between Arduino and the computer is here described: the computer sends a message that contains the ASCII `R` character and then the Arduino board responds with the values of interest. The functions used to read and decode the response are defined in the file `gas_function`.
 After taking the data, the code provides to write them into the database with the function `toFluxdb()`, which is described in `gas_function` too.
 The loop is then paused for 10 seconds to give the right time to the sensor to do the measures.
 
 ### gas_function.py
This program contains all the definitions of functions used in `gas.py`.
- `log()` writes a string in the log file preceded by the datetime
- `decodeArd()` decodes Arduino response and gives back a `numpy` array of floats, cleaned of special characters like "\n"
- `toFluxdb()` creates and writes measure points in the database of inFluxdb
- `query()` creates a inFluxdb query that allow the user to get the data back filtered by time, this function is used in `fromFlux()`
- `readTable()` is used to read the right value from the output of the query, this function is used in `fromFlux()`
- `fromFluxdb()` uses `query()` and `readTable()` to send a query to the database and to give the response back to the user. The boolean parameter `mean` allows the user to get the mean value of the selected quantity in the selected time instead of the raw table.
To better understand how the functions work and what parameters they need consult the code itself.

### gas_query.py
This code is only a brief example of how to make a query to inFluxdb and is probably useful for data analysis.

### log_gas.txt
This is an example of log file where the codes will write short messages in order to take track of errors.

#### ReadAnalog.ino
Arduino code written to control the bme680 sensor in order to measure the pressure, temperature, humidity and VOC of the gas.

### notes
- Be careful with the serial port name in `gas.py` after every reboot of the computer, it can be different.
- Use option `2>&1` in the cronjob, otherwise, if there is a problem opening the file, the error remains silent and it's difficult to debug.
- Write the inFlux token explicitly when is needed if you are using a cronjob, otherwise the program will not be able to write anything in the database because it will require authentication.
- Specify the complete path of the file when using a cronjob

## HV_monitoring
This folder contains the code used to monitor (and control) the HV that is provided by a `CAEN R1470ET` power supply. The connection between the PS and the computer is operated with an ethernet cable, so the code is deloveped using the TCP/IP protocol but the folder contains also programs for serial port communication usage.
The principle of functioning is now given: with the command:
- ``python3 rpc.py <specify_board_ip_address_here`>` 
is initialized the server that is connected with the PS. Then the command:
- ``python3 hv_logging.py`` 
initialyses the client and it will connect to the server in order to get the data from the PS.
This complicated system is needed because the PS doesn't support multiple clients connections, so if the computer starts communication with the PS in order to automatically monitor the parameters, it became impossible to set new values of voltage or current and all the way round.
After getting the parameters values the code will write them into a database in inFluxdb as the previous case of the gas monitoring.

### rpc.py
This program is the server that connects to the PS. 
In the initial part is defined the Hvservise class with some function used to get or set the PS parameters.
In the `main()` part the server try to connect to the PS. If the connection is accepted then a message is written in the log file, if is not an error message is written instead and an error is raised.
The server is defined in localhost port 8000 by default. Then the server is ready to take connections of clients.
If the program isn't started in background the code will write on the terminal page every action that is done by the clients connected with it.
When a keyboard interrupt is given, the code will write a status string on the log file and then the system will exit without errors reported.
This program makes direct use of `hv.py` and `gas_funtion.py`.

### hv.py
In this code is defined the class `Board` useful in order to connect to various types of CAEN boards.
The class is initialized specifying the board type (in this case a N1470) and the type of connection (TCPIP protocol). In this step, the wrapper code for python is used. If the connection is successfully done a string is printed.
The functions defined for this class are the ones used to get and change the board parameters.

### hv_logging.py
This code is the one that connects with the server in order to monitor the hv status, and so is the client.
Since the data are stored in inFluxdb database, the initial part of the program is used for the configuration of the inFlux client. The parameters needed to connect with the database are now specified.
The labels for the measured current are also specified, this is due to the fact that the instrument provides two different types of scales for the current measure, one with higher precision than the other, so if you want to obtain the measured current you need to ask for both IMonH and IMonL and see what of this two parameters is not 0. For a better understanding of how the current measurement is done, it can be useful to consult the manual which link is reported in the notes at the end of this part.
Then the inFlux client is started.
After that, the code will try to connect with the server created with `rpc.py`. The connection opens the localhost port 8000 by default because that is the default set in `rpc.py``, but if it's needed the user can set another port when the program is started by the terminal command line by specifying the new port name after the command itself, like the following example:
- ``python3 hv_logging <port_number>``.
If the connection to the server is successfully established, then a message is written in the log file.
Then an infinite while loop is started in order to monitor periodically the PS parameters.
In the loop the program will ask the server to get measured and the set values of both current and voltage, for every channel in the board (4 channels in this case). The request is thought to be easily modified in the case of multi-board connection.
After taking the data from the server, the code provides to create and write the points in inFluxdb. A time sleep of five seconds is set between one measure and another.
The loop is designed to stop, write a closing message in the log file and exit from the program when a keyboard interrupt is given.

### hv_setting.py
This code is used set the PS parameters to different values. The parameters are defined in the datasheet that can be found using the link in the note at the end of the section.
At the beginning of the program are defined the labels for the measured current as explained before for `hv_logging`.
When the `main()` part start, a list of parser arguments is defined in order to set the right parameter.
The option must be given in the command line as in the following example:
- ``python3 hv_setting.py -c 3 -v 250 -i 2``,
this line will set the voltage at 250V in the 3rd channel of the 0 board and the current limit at 2uA in the same board and channel.
The list of arguments is printed by the command:
- ``python3 hv_setting.py -h``.
The arguments are:
- `-p` to select the localhost port of the connection, by default this parameter is 8000 because is the default defined in the server code `rpc.py`
- `-v` to set the voltage at the value specified in the command in the selected channel (option `-c`) `(V)`
- `-i` to set the current at the value specified in the command in the selected channel (option `-c`) `(uA)`
- `-c` to set the channel of the power supply in which operate the changes
- `-b` to set the board in which to operate the changes, if there are more than one. The default for this option is `0` so if there is only one board the right value for this argument is already set.
Please pay attention to the board parameters limits defined in the manual of the PS you are using. In particular, is useful to mention that the board CAEN R1470 has four channels enumerated from 0 to 3 and NOT starting by 1.
After the definitions, the program will control if the user specifies the channel number and if the number in input corresponds to an existing channel in the PS. The specification of the channel number in the command line is mandatory and if this parameter is not provided the code will print an error message in the log file and an error is raised before closing the program execution.
Then the program will take the measure of current and voltage in the selected channel.
After that, the code checks for what parameter the user is asking for change and set the value specified in the command line. 
Is possible to change simultaneously current and voltage in one channel, but not to change any values in more than one channel at a time.
If neither the current or the voltage is specified a possible error message is written in the log file and obviously nothing is changed. If the new values of current or voltage are the same as the measurement performed before in the code, a possible error message is written in the log file in order to let the user aware that he probably write the wrong command.

### CAENHVWrapper-6.3 and env.sh
Folder that contains the wrapper code in order to use python language for the communication with the PS which library is written in C.
`env.sh` is a bash script that exports the library path.
### gas_function
This file is the same as the previous section.

### log_hv.txt
log file where the programs eventually writes error messages or writes when they start or stop.

### README.md
This README file contains the same instructions repeated in the `Requirements` section.

### hvserial.py and instrument.py
This programs are used in order to communicate with the board via serial port. So they are not needed in the current operation of the PS but are stored anyway in this folder for the future.

### notes
Pay attention to not open the PS interface provided by the official app while the server is working because PS can connect only to one client at time, so it will result in a silent error or in a communication problem displayed in the log file and there is no other solutions (or at least I don't know other solutions) than shut down the PS, wait some time and then restart it.
- If you run the server and the client (`rpc.py` and `hv_logging.py`) by a set cronjob please pay attention to the notes for crontab in the previous section and to the fact that the server needs some time to establish the connection and to be ready for support the communication with the clients.
- The server can operate one action at a time, so it can be blocked if you try to do something while `hv_logging` is measuring if the delay between two measures is too short.
- The parameters of the R1470 CAEN power supply boards are defined in the datasheet of the instrument found in `https://www.caen.it/products/r1470et/`
- When setting the parameters of the power supply pay attention to not overcoming the limits specified in the manual of the PS.
Pay attention that the enumeration of the channel starts from 0 and NOT from 1. When setting new values for the parameters the code will verify that the channel number is not bigger than the maximum existing but is impossible to check if the user writes the right channel number! When starting `hv_setting.py` the option `-c <number_of_the_channel>` is mandatory.
- The log path file is written in every program, so if you want to change it you must be careful to change it every time adding a new path.

## Scope
In this folder is stored the class definition for the scope. This class contains the definitions of the functions useful to control the oscilloscope and to set the automatic acquisition.
The functions are defined based on the command written in the manual found at:
`https://cdn.teledynelecroy.com/files/manuals/wr2_rcm_revb.pdf`.
Not all the commands are improved because they're not necessary for the purpose of the project. 
The scope used is the LeCroy 610Zi.

### Requirements
Install the vxi11 package to communicate with instruments, more info at:
```https://github.com/python-ivi/python-vxi11```
### scope_class.py
This file contains the class for the scope control.
At the beginning of the file are defined some lists useful to debug and control the parameters of the commands. Is important to change these values if the scope is not exactly the same used here.
Functions are generally commented and at the beginning of every section is written a brief message which contains the manual page where it is possible to find the information about the commands below.
User-defined functions purpose is to save the acquired waveforms in the controller (PC where the code is running).

### prova.py
This file is a brief test of some functions.

### notes 
- if the scope is different from the one used here, change at least the channel name according to the number of channels the scope has.
- be sure to install the requirements
