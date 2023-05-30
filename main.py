import os
import sys
import glob
import logging
from pathlib import Path

import imap.global_var as global_var
from imap.lib.convertor import Opendrive2Apollo


def show_open_drive_map(map_file):
    opendrive2apollo = Opendrive2Apollo(map_file)
    opendrive2apollo.set_parameters(only_driving=False)
    opendrive2apollo.convert()    
    
global_var._init()
global_var.set_element_value("sampling_length", 1.0)
global_var.set_element_value("debug_mode", False)
global_var.set_element_value("enable_z_axis", False)


map_dir = sys.argv[1]

if map_dir is not None:
    # Get a list of all .xodr files in the specified directory
    map_files = glob.glob(os.path.join(map_dir, '*.xodr'))

    for map_file in map_files:
        global_var.set_element_value("need_save_figure", True)
        show_open_drive_map(map_file)

else:
    logging.error("Directory not provided or does not exist.")

