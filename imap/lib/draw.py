#!/usr/bin/env python

# Copyright 2021 daohu527 <daohu527@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, softbutton_press_eventware
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import io
import math

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

import imap.editor as editor
import imap.global_var as global_var


fig, ax = plt.subplots(figsize=(256/50, 256/50))

def draw(hdmap, lane_id):
  lane_ids = []
  junction_ids = []
  hdmap.draw_lanes(ax, lane_id)
  hdmap.draw_junctions(ax, junction_ids)
  hdmap.draw_signals(ax)
  hdmap.draw_crosswalks(ax)
  hdmap.draw_stop_signs(ax)
  hdmap.draw_yields(ax)
    
def show_map(map_path, lane_id):
  hdmap=Map()
  hdmap.load(map_path)
  draw(hdmap, lane_id)
  # max windows
  # manager=plt.get_current_fig_manager()
  # manager.window.showMaximized()
  # tight layout
  # todo(zero): why tight layout not work?
  plt.tight_layout()
  plt.axis('equal')
  plt.show()

def add_editor():
  fig.canvas.mpl_connect('button_press_event', editor.on_click)
  fig.canvas.mpl_connect('button_press_event', editor.on_press)
  fig.canvas.mpl_connect('button_release_event', editor.on_release)
  fig.canvas.mpl_connect('pick_event', editor.on_pick)
  fig.canvas.mpl_connect('motion_notify_event', editor.on_motion)

def calculate_distance(point1, point2):
  delta_easting = point2[0] - point1[0]
  delta_northing = point2[1] - point1[1]
  distance = math.sqrt(delta_easting**2 + delta_northing**2)
  return distance

def filter_points(ego, points):
  # Filter the key points that longer than 50 meters form the ego car
  filtered_points = []
  for point in points:
      distance = calculate_distance(ego, point)
      if distance <= 25: # ego at center, so the resolution should be 256/50
          filtered_points.append(point)
  return filtered_points

def draw_line(line, color=None, reference_line=False, label=""):
  # key points of lane/line
  x = [point.x for point in line]
  y = [point.y for point in line]
  
  # get the ego UTM location
  ego_UTM = global_var.get_element_value("ego_UTM")
  
  # filter the key points far away from ego
  filtered_points = filter_points(ego_UTM, list(zip(x, y)))
  filtered_x, filtered_y = zip(*filtered_points)
  if reference_line:
    pass
  else:
    if color:
      ax.plot(filtered_x, filtered_y, color, label = label)
    else:
      ax.plot(filtered_x, filtered_y, label = label)

def draw_ego(lat, lon, width = 3, height = 3):
  lat = lat - (width / 2)
  lon = lon - (height / 2)
  rect = patches.Rectangle((lat, lon), width, height, linewidth=0.1,  facecolor='green', angle = 0)

  ax.add_patch(rect)

def show(need_save=True, path=None):
  ax.axis('equal')
  plt.axis('off')
  
  if need_save:
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=50)
    plt.savefig(path, dpi = 50) # save in disk
    buf.seek(0)

    # Create a PIL image object
    img = Image.open(buf)

    # Convert the image object to a numpy array
    img_array = np.array(img)

    # img_arry shape:
    print("Saved Successfully: ", path)
    print("nparray size: ", img_array.shape)

  plt.show()
