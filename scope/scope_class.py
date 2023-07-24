import ipaddress
import vxi11
import re

#   MANUAL FOR REMOTE CONTROL CAN BE FOUND AT THE FOLLOWING URL:
#   https://cdn.teledynelecroy.com/files/manuals/wr2_rcm_revb.pdf
'''
def decode(command: str, response):
    response=response.replace(str(command)+" ", "").split(",")
    return response
'''
#useful definition
channel_name=["C1","C2","C3","C4"] #define channels
devices=['CARD','FLPY','HDD']
t_name=["TA","TB","TC","TD"]
memories=devices+["M1","M2","M3","M4"]
trace_types=["BINARY","SPREADSHEET","MATHCAD","MATLAB"]
wf_data_blocks=["DESC","TEXT","TIME","DAT1","DAT2","ALL"]

class Scope:
    def __init__(self, ip_address, time_out=30.0):
        ip_address = str(ipaddress.ip_address(ip_address)) #validate ip address
        self.instrument = vxi11.Instrument(ip_address) # define an instrument using vxi11 library
        self.timeout = time_out

    def __str__(self) -> str:    #identification of the object
        id=self.instrument.ask("*IDN?").replace("*IDN " , "").split(",") #ask for id and format text
        return str(id[0]+'\nmodel: '+str(id[1])+'\nserial number: '+str(id[2])+'\nfirmware: '+str(id[3])) #return id

    def ask(self, command): #this will ask a command to the scope and wait for response
        return (self.instrument.ask(command))

    def write(self, command):
        return (self.instrument.write(command)) #write a command without response expected

    ######################################################################################
    ### ACQUISITION COMMANDS
    #This section contains the function created in order to set the acquisition parameter of the scope.
    #Please take in mind that every definition is made following the specific needs of the performed measure, so
    #not every possible parameter or function is here developed.
    #For better information related to the acquisition commands consult the manual which url is in the head
    #of this file at page 59.
    ######################################################################################
    
    def arm(self):
        self.write('ARM')  #change acquisition state from stopped to single

    def stop(self):
        self.write('STOP') #stop acquisition

    def sequence(self, mode='ON', segments=None, max_size=None, debug=False):  #set acquisition mode in sequence, not all parameters are mandatory
        if mode in ['ON', 'OFF']:   #mode must be on or off
            if (segments is not None) and (max_size is not None):   # write segments and max size if specified
                self.write('SEQ '+str(mode)+', '+str(segments)+', '+str(max_size))
            elif (segments is not None) and (max_size is None):  #write segments if is the only given parameter
                self.write('SEQ '+str(mode)+', '+str(segments))
            elif (segments is None) and (max_size is None):  #write only the command if there aren't other parameters since they are optional
                self.write('SEQ '+str(mode))
            else:  #if segments is not specified then is not correct to define a max size for them
                print('Error in sequence sintax')
        else:
            print('Error: mode must be "ON" or "OFF"')

        if debug == True:  #print the query result
            print(self.ask("SEQ?"))

    def time_div(self, value: str, debug=False):   #change the time for division of the scope, value must contains the unit of measure in upper case like "2US"
        unit=re.split('(\d+)',value)  #get the unit of measure
        if unit[2] in ['NS','US','MS','S','KS']: #control if the specified units are ok
            self.write('TDIV '+str(value)) #send the command
        else:
            print("Error in unit of measure sintax")
        if self.ask("*STB?")==4: #control the register in order to find if there are exceptions, if value is 4 thee variable is been adjusted
            print("TDIV adjused because it exceeds the limits")  ###!!! si potrebbe fare funzione e capire meglio

        if debug==True:  #print query result
            print(self.ask("TDIV?"))

    def trig_coupling(self, trig_source: int | str, coupling: str, debug=False): #set the trigger coupling
        if type(trig_source) == int: #trig source (channel) can be inserted like the int number of the channel or a string like "C1"
            trig_source='C'+str(trig_source) #is the input is a int variable it must be converted into a string with capital C in the head
        if trig_source in channel_name or trig_source in ["EX", "EX10"]: #is possible to use an external trigger
            if coupling in ["AC","DC","HFREJ","LFREJ"]: #check the correct modes of coupling
                self.write(str(trig_source)+':TRCP '+str(coupling))
                #print(str(trig_source)+': TRCP '+str(coupling))
            else:
                    print("Error: invalid coupling sintax")
        else:
            print("Error: invalid trigger source")

        if debug==True:
            print("trig_couple: "+self.ask(str(trig_source)+":TRCP?").replace(":TRCP","")) #print query result

    #the next function sintax is exactly the same as the previous
    def trig_level(self, trig_source: int | str, level: str | float, debug=False):  #set the trigger level, for the trig_source option is possible to use int ore str like the previous function. The trigger level can be given as str or as a float, suffix V is optional since is the only possible unit of measure.
        if type(trig_source) == int:
            trig_source='C'+str(trig_source)
        if trig_source in channel_name or trig_source in ["EX", "EX10"]:
                self.write(str(trig_source)+':TRLV '+str(level))
                #print(str(trig_source)+':TRLV '+str(level))
        else:
            print("Error: invalid trigger source")

        if debug==True:
            print("trig_level: "+self.ask(str(trig_source)+":TRLV?").replace(":TRLV",""))

    def trig_mode(self, mode: str, debug=False): #set the trigger mode
        if mode in ['AUTO','NORM','SINGLE', 'STOP']: #Verify that the mode selected is one of the possible choices
            self.write('TRMD '+str(mode)) #send command
        else:
            print("Error: invalid  trigger mode sintax")

        if debug==True:
            print(self.ask('TRMD?')) #write query result

    def trig_slope(self, trig_source:str|int, slope:str, debug=False): #select trigger slope
        if type(trig_source) == int: #if source is int it must be converted in a str with capital C in ahead the number
            trig_source='C'+str(trig_source)
        if trig_source in channel_name or trig_source in ["EX", "EX10", "LINE"]: #trig source can be external too
            self.write(str(trig_source)+':TRSL '+slope)
        else:
            print("Error: invalid trigger source")

        if debug==True:
            print(self.ask(str(trig_source)+':TRSL?'))

    def trig_window(self, window:float, debug=False): #select trigger window amplitude in volts on the current edge trigger source. Window is centered around the edge trigger level.
        if  window < 0. or window > 25. : #control that window is in range
            print("Error: trigger window out of range 0-25V")
        else:
            self.write('TRWI '+str(window)) #send command

        if debug==True:
            print(self.ask('TRWI?')) #print query result to check

    def volt_div(self, channel:int|str, V:float, debug=False):
        """
        This function sets the vertical sensitivity in Volt/div. If the value selected is out of range the VAB bit 2 in the STB
        register is set. The probe attenuation is not taken into account. The unit of measure is Volt and is not specified.
        """
        if type(channel) == int: #if channel is int it must be converted in a str with capital C in ahead the number
            channel='C'+str(channel)
        if channel in channel_name:
            self.write(str(channel)+':VDIV '+str(V))
        else:
            print("Error: invalid channel name")
        if self.ask("*STB?")==4: #control the register in order to find if there are exceptions, if value is 4 thee variable is been adjusted
            print("volt_div adjused because it exceeds the limits")  ###!!! si potrebbe fare funzione e capire meglio

        if debug==True:
            print(self.ask(str(channel)+':VDIV?'))

    def wait_acquisition(self, timeout=None): #!impossibile provare da casa credo
        """
        This function prevents the scope from analyzing new commands until it has completed the current acquisition.
        The parameter timeout is optional and specifies the timeout is seconds after the scope will stop waitig.
        If the timeout is ot given or if the given value is 0, the scope will wait indefinitely.
        The range for the timeout is 0 to 1000 seconds.
        """
        if timeout is None:
            self.write('WAIT')
        elif timeout <0. or timeout > 1000.:
            print("Error: timeout out of range")
        elif type(timeout)==float or type(timeout)==int:
            self.write('WAIT '+str(timeout))
        else:
            ("Error: invalid timeout type or sintax")
    """
    def trig_select(self,debug=False):
        trig_type=["DROP","EDGE","GLIT","INTV","STD","SNG","SQ","TEQ"]
        source=channel_name+["LINE","EX","EX10","PA"]
        hold_type=["TI","TL","EV","PS","PL","IS","P2","I2","OFF"]
        hold_value=[]
    """
    
    def offset(self, channel:int|str, offset:float, debug=False): #offset is in Volt
        if type(channel) == int: #if channel is int it must be converted in a str with capital C in ahead the number
            channel='C'+str(channel)
        if channel in channel_name:
            self.write(str(channel)+':OFST '+str(offset))
        else:
            print("Error: invalid channel name")
              
        if debug==True:
            print(self.ask(str(channel)+':OFST?'))
    
    ###########################################################################################
    ###  MASS STORAGE COMMANDS                                                                
    # More information can be found by reading the manual specified in the head part of this  
    # file at page 61.                                                                        
    ###########################################################################################

    def directory(self, disk:str, action:str, dir_path:str, debug=False):  #select, create or delete a folder, query gives path and what is in the inside
        actions=["CREATE","DELETE","SWITCH"]
        if disk in devices:    #control the device
            if action in actions:  #control the action
                self.write("DIR DISK,"+str(disk)+", ACTION,"+str(action)+",'"+str(dir_path)+"'")
            else:
                print("Error:invalid action for DIR")
        else:
            print("Error: invalid disk")

        if debug==True:
            print(self.ask("DIR? DISK,"+str(disk))+",'"+str(dir_path)+"'")

    def delete_file(self, disk:str, file_path:str, debug=False):   #delete file, insert the complete path to the file
        if disk in devices:
            self.write("DEL DISK,"+str(disk)+",FILE,'"+str(file_path)+"'")
        else:
            print("Error: invalid device for DEL")

        if debug==True:
            path=path.split("\\")
            i=0
            for i in range(len(path)-1):
                dir_path=dir_path+path[i]
            print(self.ask("DIR? DISK,"+str(disk))+",'"+str(dir_path)+"'")
            
    def file_name(self, type:str|int, file_name:str, debug=False): #set the name for the saved traces
        if type(type) == int: #type can be inserted like the int number of the channel or a string like "C1"
            type='C'+str(type) #if the input is a int variable it must be converted into a string with capital C in the head
        types=channel_name+t_name+['SETUP','HCOPY']
        if type in types:
            if type in channel_name+t_name:
                if len(file_name)>8:
                    print("Error: file name too long")
                else:
                    self.write("FLMN TYPE,"+str(type)+",FILE,'"+str(file_name)+"'")
            else:
                if len(file_name)>5:
                    print("Error: file name too long")
                else:
                    self.write("FLMN TYPE,"+str(type)+",FILE,'"+str(file_name)+"'")
        else:
            print("Error: invalid type")
        
        if debug==True:
            print(self.ask("FLNM? TYPE,"+str(type)))

    #######################################################################################
    ###  WAVEFORM TRANSFER
    # More information can be found by reading the manual specified in the head part of this
    # file at page 62.
    #######################################################################################

    def store_setup(self, mode:str, trace:str|int="ALL_DISPLAYED", trace_type:str="BINARY", destination:str="HDD", debug=False):
        """
        The store setup command controls the way in which traces will be stored.
        A single trace or all displayed traces can be anabled for storage. This applies to both auto storing and store command.
        Traces can be auto stored to mass storage after each acquisition until device became full(fill) or continuously (wrap)replacing the oldest.
        """
        modes=["OFF","WRAP","FILL"]
        if type(trace) == int: #trace can be inserted like the int number of the channel or a string like "C1"
            trace='C'+str(trace) #if the input is a int variable it must be converted into a string with capital C in the head
        if trace =="ALL" or trace =="all":  #short for ALL_DISPLAYED
            trace="ALL_DISPLAYED"
        traces=channel_name+t_name+["ALL_DISPLAYED"]  
        if trace in traces:  #verify trace
            if mode in modes:
                if trace_type in trace_types:   #verify type
                    if destination in memories: #verify destination
                        self.write('STST '+str(trace)+","+str(destination)+",AUTO,"+str(mode)+",FORMAT,"+str(trace_type))
                    else:
                        print("Error: invalid destination")
                else:
                    print("Error: invalid type")
            else:
                print("Error: invalid mode")
        else:
            print("Error: invalid trace in store setup")

        if debug==True:
            print(self.ask("STST?"))

    def store(self, trace:str|int="ALL_DISPLAYED", destination:str="HDD"):
        if type(trace) == int: #trace can be inserted like the int number of the channel or a string like "C1"
            trace='C'+str(trace) #if the input is a int variable it must be converted into a string with capital C in the head
        if trace =="ALL" or trace =="all":  #short for ALL_DISPLAYED
            trace="ALL_DISPLAYED"
        traces=channel_name+t_name+["ALL_DISPLAYED"]  
        if trace in traces:  #verify trace
            if destination in memories:
                self.write("STO "+str(trace)+","+str(destination))
            else:
                print("Error: invalid destination")
        else: 
            print("Error: invalid trace")

    def waveform_text(self, trace:str|int, text:str, debug=False):
        traces=channel_name+t_name
        if type(trace) == int: #trace can be inserted like the int number of the channel or a string like "C1"
            trace='C'+str(trace) #if the input is a int variable it must be converted into a string with capital C in the head  
        if trace in traces:
            if len(text)<=160: #verify text lenght
                self.write(str(trace)+":WFTX '"+str(text)+"'")
            else:
                print("Error: text too long")
        else:
            print("Error: invalid trace")

        if debug==True:
            print(self.ask(str(trace)+":WFTX?"))

    def get_waveform(self, trace:str|int, block:str="ALL"):
        """
        This function transfers waveforms to the controller.
        Only the query form is implemented, the normal form transfers waveforms from controller to the scope.
        """
        traces=channel_name+t_name+["M1","M2","M3","M4"]
        if type(trace) == int: #trace can be inserted like the int number of the channel or a string like "C1"
            trace='C'+str(trace) #if the input is a int variable it must be converted into a string with capital C in the head  
        if trace in traces:
            if block in wf_data_blocks:
                self.write(str(trace)+":WF? "+str(block))
                return self.instrument.read_raw() # response is binary so is not possible to ask
            else:
                print("Error: invalid block")
        else:
            print("Error: invalid trace")

    def waveform_setup(self, first_point:int=0, number_points:int=0, sparsing:int=0, segment_number:int=0, debug=False):
        """
        Function useful to specify the amount of data in a waveform transmitted to the controller.
        first_point=address of the first data point sent
        number_points=number of points sent
        sparsing=interval between data points
        segment_number=number of segments sent
        0 means all
        """
        self.write("WFSU SP,"+str(sparsing)+",NP,"+str(number_points)+",FP,"+str(first_point)+",SN,"+str(segment_number))

        if debug==True:
            print(self.ask("WFSU?"))
            
    #########################################################################
    ### USER DEFINED
    #########################################################################
    def waveform_name(self, dir_path:str, channel:str|int, name:str, extension:str='.trc'):
        if type(channel) == int: #channel can be inserted like the int number of the channel or a string like "C1"
            channel='C'+str(channel) #if the input is a int variable it must be converted into a string with capital C in the head  
        if channel in channel_name:
            return dir_path+"/"+channel+name+extension
        else:
            print("Error: invalid channel")

    def save_waveform(self,path:str, trace:str|int, block:str="ALL"):
        waveform=self.get_waveform(trace, block)
        file=open(path,"+xb")
        file.write(waveform)
        
    @property
    def id(self):
        id=self.instrument.ask("*IDN?").replace("*IDN " , "").split(",")
        return id

    @property
    def autostore(self):
        return self.ask("STST?")

    @property
    def wf_setup(self):
        return self.ask("WFSU?")

    @property
    def channels(self):
        return channel_name
