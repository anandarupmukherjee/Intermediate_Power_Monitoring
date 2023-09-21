
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
import tomli
import logging
import logging.handlers

log_directory = "/var/logs/sensor"
os.makedirs(log_directory, exist_ok=True)

logger = logging.getLogger('sensor')
logger.setLevel(logging.INFO)

handler = logging.handlers.TimedRotatingFileHandler(
    filename=os.path.join(log_directory, 'sensor.log'),
    when="W6",
    interval=1,
    backupCount=4
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


script_dir = os.path.dirname(os.path.abspath(__file__))
script_dir = script_dir.split("code")[0]
# config_file_path = os.path.join(script_dir, '..', 'config', 'config.tomli')

print(script_dir+"config/config.tomli")
config_file_path = script_dir+"config/config.tomli"

# Parse the TOML content
with open(config_file_path, 'rb') as f:
    config_data = tomli.load(f)

# print(config_data)

# Extract the necessary parameters
adapter_addr = config_data["Configuration"]["adapter_addr"]
adapter_port = config_data["Configuration"]["adapter_port"]
slave_id = config_data["Configuration"]["slave_id"]
machine_name = config_data["Configuration"]["machine_name"]
voltage = config_data["Configuration"]["fixed_voltage"]
#current = config_data["Registers"]["I1_reg"]

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
    res = client.read_input_registers(address=addr, count=int(count), unit=int(slave))
    decoder = BinaryPayloadDecoder.fromRegisters(res.registers, Endian.Big, wordorder=Endian.Little)
    reading = decoder.decode_32bit_float()
    return reading




def action_push(slave_id, machine_name):
    reading1=0
    reading2=0
    reading3=0
    reading4=0
    reading5=0


    I1_reg = 0x000C
    # V1_reg = 0x0006
    # kW_reg = 0x0012
    f_reg = 0x001E
    thd_1 = 0x005A
    
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d/%m/%y, %H:%M")

    reading1 = register_read(I1_reg, 4, slave_id)
    logger.info(f"I1: {reading1}")
    time.sleep(0.5)

    reading2 = float(voltage)
    logger.info(f"V1: {reading2}")
    time.sleep(0.5)

    reading3 = reading1 * reading2
    logger.info(f"Power (sum): {reading3}")
    time.sleep(0.5)

    reading4 = register_read(f_reg, 4, slave_id)
    logger.info(f"f(Hz): {reading4}")
    time.sleep(0.5)

    reading5 = register_read(thd_1, 4, slave_id)
    logger.info(f"THD_I1: {reading5}")
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
        action_push(1, 'demo_mfm')
        # try:
        #     action_push(1, 'demo_mfm')
        #     #action_push(2, 'daisy_c_mfm')

        # except:
        #     print("Trying...")
        #     reading1=0
        #     reading2=0
        #     reading3=0
        #     reading4=0
        #     reading5=0
        #     devStat=1
        #     machine_name = 'demo_mfm'
        #     var = "curl -i -XPOST 'http://influx.docker.local:8086/write?db=emon' --data '" + machine_name + " i1=" + str(reading1) + ",v1=" + str(reading2) + ",kw=" + str(reading3) + ",thd1=" + str(reading5) + ",dev_stat=" + str(devStat) + ",fhz=" + str(reading4) + "'"
        #     os.system(var)

        #     #machine_name = 'daisy_c_mfm'
        #     #var = "curl -i -XPOST 'http://influx.docker.local:8086/write?db=emon' --data '" + machine_name + " i1=" + str(reading1) + ",v1=" + str(reading2) + ",kw=" + str(reading3) + ",thd1=" + str(reading5) + ",dev_stat=" + str(devStat) + ",fhz=" + str(reading4) + "'"
        #     #os.system(var)
        #     pass

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
        #machine_name = 'daisy_c_mfm'
        #var = "curl -i -XPOST 'http://influx.docker.local:8086/write?db=emon' --data '" + machine_name + " i1=" + str(reading1) + ",v1=" + str(reading2) + ",kw=" + str(reading3) + ",thd1=" + str(reading5) + ",dev_stat=" + str(devStat) + ",fhz=" + str(reading4) + "'"
        #os.system(var)
    time.sleep(5)
