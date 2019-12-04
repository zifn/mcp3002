#code from 
# raspberry.io/projects/view/reading-from-a-mcp3002-analog-to-digital-converter/

from __future__ import division #change '/' to "true division"
import spidev #import module that allows for gpio to talk to mcp3002
import time
import json
import os
from copy import deepcopy
from sys import argv
from sys import stdin

def read(adc_channel, spi_channel):
    conn = spidev.SpiDev()
    conn.open(0, spi_channel)
    conn.max_speed_hz = 1200000 #1.2 MHz
    cmd = [1,(2 + adc_channel) << 6, 0]
    reply = conn.xfer2(cmd)
   # print "reply from read = {}".format(reply)

    value = reply[1] & 31
    value = value << 6
    value = value + (reply[2] >> 2)
    conn.close()
    return value

def timer(data_points):
    values = []
    for i in range(data_points):
       # temp_reply = deepcopy(conn.xfer2(cmd)) #bug in xfer2 it modifies the given output resulting in zeros
       # print "raw reply in timer = {}".format(temp_reply)
        values.append(read(0,0))
    time_2 = time.time()

    ave_value = sum(values)
    ave_value /= data_points
    return(time_2, ave_value)

def read_json_config(file_path):
    with open(file_path) as config_file:
        raw_json = json.load(config_file)
    output_file_path = os.path.join(raw_json["file_dir"], raw_json["file_name"])
    should_write_to_file = raw_json["should_write_to_file"]
    data_points = raw_json["data_points_to_average"]
    collection_pause = raw_json["data_points_to_collect"]
    wait_time = raw_json["seconds_to_wait"]
    if wait_time < 0:
        wait_time = 0
    return output_file_path, should_write_to_file, data_points, collection_pause, wait_time

def main_loop(numb_data_pnts, pnts_till_pause, wait_time, output_file_obj = None):
    if output_file_obj != None:
        output_file_obj.write("time (ms),value (arb)\n")
    pnts_collected = 0
  #  print "start data collection? Y N"
    text_start = 'yes' # stdin.readline()
    if text_start[0] in ["n", 'N']:
        return 0
    init_time = time.time()
    while True:
        time_step, value = timer(numb_data_pnts)
        print "time = {} value = {} ".format(time_step-init_time, value)
        pnts_collected += 1
        if pnts_collected >= pnts_till_pause and pnts_till_pause >= 0:
            #print "continue? Y N"
            text = 'yes'  # stdin.readline()
            pnts_collected = 0
            if text[0] in ["n", "N"]:
                break
        if output_file_obj != None:
            output_file_obj.write("{},{}\n".format(time_step-init_time, value))
        time.sleep(wait_time)
    return 0

if __name__ == '__main__':
    print "mcp3002 value = {}".format(read(0,0))
    input_config = argv[1]
    output_file_path, should_write_to_file, data_points, collection_pause, wait_time = read_json_config(input_config)

    if(should_write_to_file):
        with open(output_file_path, 'w') as output_file:
            main_loop(data_points, collection_pause, wait_time, output_file)
    else:
        main_loop(data_points, collection_pause, wait_time)
