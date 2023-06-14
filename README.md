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

# Description of the programs
In this section a brief description of the folders content and how it works will be given.

## gas_monitoring
The programs in this folder are used to monitor the gas status. The aim is reached using a bme680 sensor readed by an Arduino board. The sensor is contained in a sealed box placed at the gas output line of the Picosec detector and provides the measure of temperature, pressure, humidity and VOC of the gas. 
The communication between the Arduino board and the computer happens via serial port.
Than the data collected are stored in inFluxdb, that provides to take into account the time.
The command line that starts the monitoring is:
``python3 gas.py``

### use of crontab
The program is thinked to be started with as a cronjob as in the following example.
Open crontab:
-``crontab -e ``
install a cronjob:
- ``0 0 * * * python3 path_to_file/gas.py >> path_to_logfile/logfile.txt 2>&1``
- ``59 23 * * * ps -axu | grep gas.py | awk '{print $2}' | xargs kill -SIGINT``
The two rows written above allow the code to start every day at 00:00 and to kill the program sending a `SIGINT` signal every day at 23:59.
`2>&1` is used to write an error message in the log file if something in the cronjob doesn't work.

 ### gas.py
 This program is the main tool for the gas monitoring. 
 At the beginning there is the declaration of all the variables used for the communication with both the Arduino board (port name and baud rate) and the inFlux server (token, url, etc.). Please pay attention after the reboot of the computer because it is possible that the serial port name will be changed.
 After that the inFlux client is initialysed and a message saying that the code is starting is written in a log file.
 Than the serial port is opened and the program will wait a few seconds in order to get the time to conclude the operation properly.
 The monitoring is operated by an infinite while loop which can eventually be stopped by a SIGINT (keyboardinterrupt) signal trapped in order to write a message in the log file and close the serial port before exiting without reporting errors.
 The communication between Arduino and computer is here described: the computer sends a message that contains the ASCII `R` character and then the Arduino board responds with the for values of interest. The functions used to read and decode the response are defined in the file `gas_function`.
 After taking the data , the code provides to write them into the database with the function `toFluxdb()`, which is described in `gas_function` too.
 The loop is then paused for 10 second to gives the right time to the sensor to do the measures.
 
 ### gas_function.py
This program contains all the definition of function used in `gas.py`.
- `log()` writes a string in the log file preceded by the datetime
- `decodeArd()` decodes Arduino response and gives back a `numpy` array of floats, cleaned of special character like "\n"
- `toFluxdb()` creates and writes measure points in the database of inFluxdb
- `query()` creates a inFluxdb query that allow the user to get the data back filtered by time, this function is used in `fromFlux()`
- `readTable()` is used to read the right value from the output of the query, this function is used in `fromFlux()`
- `fromFluxdb()` uses `query()` and `readTable()` to send a query to the database and to give the response back to the user. The boolean parameter `mean` allows the user to get the mean value of the selecter quantity in the selected period of time instead of the raw table.
To better understand how the functions work and what parameters they need consult the code itself.

### gas_query.py
This code is only a brief example of how to make a query to inFluxdb and is probably useful for the data analysis.

### log_gas.txt
This il an example of log file where the codes will write short messages in order to take track of errors.

### notes
- Be careful with the serial port name in `gas.py` after every reboot of the computer, it can be different.
- Use option `2>&1` in the cronjob, otherwise if there is a problem opening the file the error reamains silent and it's difficult to debug.
- Write the inFlux token explicitely when is needed if you are using a cronjob, otherwise the program will not be able to write anything in the database because it will require the authentication.
- Specify the complete path of the file when using a cronjob

## HV_monitoring
This folder contains the code used to monitor (and control) the HV that is provided by a `CAEN R1470ET` power supply. The connection between the PS and the computer is operated with an ethernet cable, so the code is deloveped using the tcp/ip protocol but the folder contains also programs for the serial port communication usage.
The principle of functioning is now given: with the command:
- ``python3 rpc.py <specify_board_ip_address_here>`` 
is initialysed the server that is connected with the PS. Then the coomand:
- ``python3 hv_logging.py`` 
initialyses the client and it will connect to the server in order to get the data from the PS.
This complicated system is needed because the PS doesn't support multiple clients connections, so if the computer starts the communication with the PS in order to automatically monitor the parameters, it became impossible to set new values of voltage or current and all the way round.
After getting the parameters values the code will write them into a database in inFluxdb as the previous case of the gas monitoring.

### CAENHVWrapper-6.3 and env.sh
Folder that contains the wrapper code in order to use python language for the communication with the PS which library are written in C.
`env.sh` is a bash script that export the library path.
### gas_function
This file is the same as the previous section.

### log_hv.txt
log file where the programs eventually writes error messages or writes when they starts or stops.

### README.md
This README file contains the same instructions repeated in the `Requirements` section.

### notes
- Pay attenction to not open the PS interface provided by the official app while the server is working because PS can connect only to one client at time, so it will risult in a silent error or in a communication problem displayed in the log file and there is not other solutions (or at least I don't know other solutions) than shut down the PS, wait some time and then restart it.