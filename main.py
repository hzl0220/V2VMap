import sys
import logging
from pathlib import Path

import imap.global_var as global_var

# from imap.lib.draw import add_editor, show_map
from imap.lib.convertor import Opendrive2Apollo


def show_open_drive_map(map_file):
    opendrive2apollo = Opendrive2Apollo(map_file)
    opendrive2apollo.set_parameters(only_driving=False)
    opendrive2apollo.convert()    
    
global_var._init()
global_var.set_element_value("sampling_length", 1.0)
global_var.set_element_value("debug_mode", False)
global_var.set_element_value("enable_z_axis", False)


map = sys.argv[1]

if map is not None:
    map_file = Path(map)
    global_var.set_element_value("need_save_figure", True)
    show_open_drive_map(map)
    

else:
    # logging.error("File not exist! '{}'".format(file_path))
    pass

