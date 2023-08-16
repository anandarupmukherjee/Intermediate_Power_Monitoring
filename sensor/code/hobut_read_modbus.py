
########### PACKAGES ####
# pymodbus==2.5.3
# pyserial==3.5
# six==1.16.0

# @decoded by ANAND on Jun 2023
#########################

# configuration of address in datasheet pg 48 here:
# https://docs.rs-online.com/02cb/0900766b814cca5d.pdf

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.transaction import ModbusRtuFramer as ModbusFramer
import time
from datetime import datetime
import os
from configparser import ConfigParser

# import automationhat



########### HOBUT MFM 850 LTHN  Register Map####
# 0x0006 = v1
# 0x0008 = v2
# 0x000A = v3
# 0x000C = I1
# 0x000E = I2
# 0x0010 = I3
# 0x0012 = kW sum
# 0x001E = Hz
#########################



def register_read(addr, count, slave):
    res = client.read_input_registers(address=addr, count=count, unit=slave)
    decoder = BinaryPayloadDecoder.fromRegisters(res.registers, Endian.Big, wordorder=Endian.Little)
    reading = decoder.decode_32bit_float()
    return reading


adapter_addr = '192.168.0.7'
adapter_port = 502


# Read configuration from file
# config_path = os.path.join("config", "config.tolmi")
# print(config_path)
# config = ConfigParser()
# config.read(config_path)

# # Extract values from the configuration file
# adapter_addr = config.get("Configuration", "adapter_addr")
# adapter_port = config.getint("Configuration", "adapter_port")
# slave_id = config.getint("Configuration", "slave_id")
# machine_name = config.get("Configuration", "machine_name")
# I1_reg = config.getint("Configuration", "I1_reg")
# V1_reg = config.getint("Configuration", "V1_reg")
# kW_reg = config.getint("Configuration", "kW_reg")
# f_reg = config.getint("Configuration", "f_reg")

def action_push(slave_id, machine_name):
    reading1=0
    reading2=0
    reading3=0
    reading4=0
    reading5=0


    I1_reg = 0x000C
    V1_reg = 0x0006
    kW_reg = 0x0012
    f_reg = 0x001E
    thd_1 = 0x005A
    
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d/%m/%y, %H:%M")
    print(formatted_time)

    reading1 = register_read(I1_reg, 4, slave_id)
    print("I1="+str(reading1))
    time.sleep(0.5)

    reading2 = register_read(V1_reg, 4, slave_id)
    print("V1="+str(reading2))
    time.sleep(0.5)

    reading3 = register_read(kW_reg, 4, slave_id)
    print("kW (sum)="+str(reading3))
    time.sleep(0.5)

    reading4 = register_read(f_reg, 4, slave_id)
    print("f(Hz)="+str(reading4))
    time.sleep(0.5)

    reading5 = register_read(thd_1, 4, slave_id)
    print("THD_I1="+str(reading5))
    time.sleep(0.5)

    print("-----------------")
    # automationhat.relay.one.toggle()
    # automationhat.relay.two.toggle() 
    # automationhat.relay.three.toggle() 
    devStat=2

    var = "curl -i -XPOST 'http://influx.docker.local:8086/write?db=emon' --data '" + machine_name + " i1=" + str(reading1) + ",v1=" + str(reading2) + ",kw=" + str(reading3) + ",thd1=" + str(reading5) + ",dev_stat=" + str(devStat) + ",fhz=" + str(reading4) + "'"
    os.system(var)




client = ModbusTcpClient(adapter_addr, port=adapter_port, framer=ModbusFramer)


while(1):
    if client.connect():  # Trying for connect to Modbus Server/Slave
        try:
            action_push(1, 'demo_mfm')
            action_push(2, 'daisy_c_mfm')

        except:
            print("Trying...")
            reading1=0
            reading2=0
            reading3=0
            reading4=0
            reading5=0
            devStat=1
            machine_name = 'demo_mfm'
            var = "curl -i -XPOST 'http://influx.docker.local:8086/write?db=emon' --data '" + machine_name + " i1=" + str(reading1) + ",v1=" + str(reading2) + ",kw=" + str(reading3) + ",thd1=" + str(reading5) + ",dev_stat=" + str(devStat) + ",fhz=" + str(reading4) + "'"
            os.system(var)
            pass

    else:
        print('Cannot connect to the Modbus Server/Slave')
        reading1=0
        reading2=0
        reading3=0
        reading4=0
        reading5=0
        devStat=0
        machine_name = 'demo_mfm'
        var = "curl -i -XPOST 'http://influx.docker.local:8086/write?db=emon' --data '" + machine_name + " i1=" + str(reading1) + ",v1=" + str(reading2) + ",kw=" + str(reading3) + ",thd1=" + str(reading5) + ",dev_stat=" + str(devStat) + ",fhz=" + str(reading4) + "'"
        os.system(var)
    time.sleep(0.5)