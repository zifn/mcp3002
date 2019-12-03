#code from 
# raspberry.io/projects/view/reading-from-a-mcp3002-analog-to-digital-converter/

from __future__ import division #change '/' to "true division"
import spidev #import module that allows for gpio to talk to mcp3002
import time
import json
import os
from sys import argv

def read(adc_channel, spi_channel):
    conn = spidev.SpiDev()
    conn.open(0, spi_channel)
    conn.max_speed_hz = 1200000 #1.2 MHz
    cmd = [1,(2 + adc_channel) << 6, 0]
    reply = conn.xfer2(cmd)
    value = reply[1] & 31
    value = value << 6
    value = value + (reply[2] >> 2)
    value2 = ((reply[1] & 31) << 6) + (reply[2] >> 2)
    conn.close()
    return value, value2

def timer(numb_data_points):
    data_points = numb_data_points #1000 Kilo pts
    spi_channel = 0
    adc_channel = 0
    cmd = [1,(2 + adc_channel) << 6, 0] #start bit(1), SGL(1)/Pseudo-Diff(0), channel select bit, MSBF bit
    conn = spidev.SpiDev()
    conn.open(0, spi_channel)
    conn.max_speed_hz = 12000000 #12 MHz

    reply = []
    append = reply.append
    length = range(data_points)
    time_1 = time.time()
    for i in length:
        append(conn.xfer2(cmd))
        time_2 = time.time()
    delta_t_per_point = (time_2 - time_1)/data_points
    
    ave_value = 0
    for i in range(data_points):
        temp = reply[i]
        value = ((temp[1] & 31) << 6) + (temp[2] >> 2)
        ave_value += value
    ave_value /= data_points
    conn.close()
    return(time_2, ave_value)

def read_json_config(file_path):
    with open(file_path) as config_file:
        raw_json = json.load(config_file)
    output_file_path = os.path.join(raw_json["file_dir"], raw_json["file_name"])
    should_write_to_file = raw_json["should_write_to_file"]
    data_points = raw_json["data_points_to_average"]
    return output_file_path, should_write_to_file, data_points

def main_loop(numb_data_pnts, output_file_obj = None):
    if output_file_obj != None:
        output_file_obj.write("time (ms),value (arb)\n")
    init_time = time.time()
    while True:
        time_step, value = timer(numb_data_pnts)
        print "time = {} value = {} ".format(time_step-init_time, value)
        if output_file_obj != None:
            output_file_obj.write("{},{}\n".format(time_step-init_time, value))

if __name__ == '__main__':
    print read(0,0)
    input_config = argv[1]
    output_file_path, should_write_to_file, data_points = read_json_config(input_config)

    if(should_write_to_file):
        with open(output_file_path, 'w') as output_file:
            main_loop(data_points, output_file)
    else:
        main_loop(data_points)
        
        
            
        

