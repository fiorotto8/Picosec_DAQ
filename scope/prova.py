import scope_class as scope

ip_addr = '193.205.68.62' #ip address of the instrument
#rpc.test(ip_addr)
#! esiste possibilità che trigger esterni non funzionano
dir_path='D:\Picosec\Test_dir\\'

LeCroy=scope.Scope(ip_addr)
#print(LeCroy)
#LeCroy.arm()
#time.sleep(10)
#LeCroy.stop()
#LeCroy.sequence(mode="OFF",segments=200 ,debug=True)
#LeCroy.time_div("2US", debug=True)
#print(LeCroy.ask("*STB?"))
#LeCroy.trig_coupling("C1","AC",True)  ### !!! problema: pare risolto, ulteriori verifiche se capita
#LeCroy.trig_level("C1",-17E-3,True)  ### !!! NON VA: ora pare andare, il problema erano i 2 punti
#LeCroy.trig_mode('STOP',True)   #! da qui non ero in lab, no contatto visivo con scopio
#LeCroy.trig_slope(1,'NEG',True)
#LeCroy.trig_window(50E-3,True)
#LeCroy.volt_div(1,50E-3,True)
#LeCroy.directory("HDD","SWITCH","D:\Picosec\Test_dir",debug=True)
#print(LeCroy.ask("DIR? DISK,HDD"))
#non ho provato del_file()
#print(LeCroy)
#LeCroy.ask("FLNM? TYPE, C1")  #! non va e non capisco il perché
#LeCroy.file_name("C1","ciao",True) #! non va
#print(LeCroy.ask("C1:WFTX?")) #not yet available
#print(LeCroy.autostore)
#LeCroy.store_setup("OFF", debug=True)
#LeCroy.store()

#### prova 
#LeCroy.directory("HDD","SWITCH", dir_path, debug=True)
#LeCroy.arm()
#LeCroy.sequence(segments=100)
#LeCroy.store_setup("FILL")
#LeCroy.store()
#LeCroy.get_waveform()
#LeCroy.stop()
#print(LeCroy.wf_setup)
#LeCroy.save_waveform('/home/cms3/Desktop/Picosec_DAQ/scope/file', 2)
#LeCroy.get_waveform(2)

#LeCroy.directory("HDD", "SWITCH", "D:\\TestScope")
#LeCroy.store()