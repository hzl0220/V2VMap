import os
import argparse
import glob

import imap.global_var as global_var
from imap.lib.convertor import Opendrive2Apollo


global_var._init()
global_var.set_element_value("sampling_length", 1.0)
global_var.set_element_value("debug_mode", False)
global_var.set_element_value("enable_z_axis", False)

def bevImage_parse():
    parser = argparse.ArgumentParser(description="Dump the BEV Image of HDMap(.xodr)")
    parser.add_argument('--map_dir', type=str, required=True,
                        help='HDMap file path, e.g. ./data/map')
    opt = parser.parse_args()
    return opt

def save_open_drive_map(map_file):
    opendrive2apollo = Opendrive2Apollo(map_file)
    opendrive2apollo.set_parameters(only_driving=False)
    opendrive2apollo.convert()    
    
if __name__ == '__main__':
    opt = bevImage_parse()
    map_dir = opt.map_dir
    if not os.path.exists(map_dir):
        print(f"Error: The provided directory '{map_dir}' does not exist.")

    if map_dir is not None:
        if map_dir.endswith('.xodr'):  
            global_var.set_element_value("need_save_figure", True)
            save_open_drive_map(map_dir)         
        else:
            map_files = glob.glob(os.path.join(map_dir, '*.xodr'))
            for map_file in map_files:
                global_var.set_element_value("need_save_figure", True)
                save_open_drive_map(map_file)