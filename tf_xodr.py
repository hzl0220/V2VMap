import os
import glob
import math

from lxml import etree
import xml.etree.ElementTree as ET
import numpy as np


def get_tf_matrix(source_frame, target_frame): ## FIXed Buggy Tf obtained
    source_frame = np.loadtxt(source_frame, delimiter=",")
    target_frame = np.loadtxt(target_frame, delimiter=",")
    source_inv = np.linalg.inv(source_frame)
    target_inv = np.linalg.inv(target_frame)
    return np.dot(target_inv, source_frame)


def reorder_attributes(xml_file):
    # Parse the XML file
    tree = etree.parse(xml_file)
    root = tree.getroot()
    geometries = root.xpath('.//geometry')

    if geometries:
        # Define the desired order of attributes
        new_attributes = ['s', 'x', 'y', 'hdg', 'length']

        for geometry in geometries:
            # Create a new dictionary to store the reordered attributes
            reordered_attributes = [(attr, geometry.attrib[attr]) for attr in new_attributes if attr in geometry.attrib]

            # Update the 'geometry' element with the reordered attributes
            geometry.attrib.clear()
            geometry.attrib.update(reordered_attributes)       
    
    roads = root.xpath('.//road')
    if roads:
        new_attributes = ['name', 'length', 'id', 'junction']
        for road in roads:
            reordered_attributes = [(attr, road.attrib[attr]) for attr in new_attributes if attr in road.attrib]
            road.attrib.clear()
            road.attrib.update(reordered_attributes)

    elevations = root.xpath('.//elevation')
    if elevations:
        new_attributes = ['s', 'a', 'b', 'c', 'd']
        for elevation in elevations:
            reordered_attributes = [(attr, elevation.attrib[attr]) for attr in new_attributes if attr in elevation.attrib]
            elevation.attrib.clear()
            elevation.attrib.update(reordered_attributes)
    
    superelevations = root.xpath('.//superelevation')
    if superelevations:
        new_attributes = ['s', 'a', 'b', 'c', 'd']
        for superelevation in superelevations:
            reordered_attributes = [(attr, superelevation.attrib[attr]) for attr in new_attributes if attr in superelevation.attrib]
            superelevation.attrib.clear()
            superelevation.attrib.update(reordered_attributes)

    laneOffsets = root.xpath('.//laneOffset')
    if laneOffsets:
        new_attributes = ['s', 'a', 'b', 'c', 'd']
        for laneOffset in laneOffsets:
            reordered_attributes = [(attr, laneOffset.attrib[attr]) for attr in new_attributes if attr in laneOffset.attrib]
            laneOffset.attrib.clear()
            laneOffset.attrib.update(reordered_attributes)
    
    widths = root.xpath('.//width')
    if widths:
        new_attributes = ['sOffset', 'a', 'b', 'c', 'd']
        for width in widths:
            reordered_attributes = [(attr, width.attrib[attr]) for attr in new_attributes if attr in width.attrib]
            width.attrib.clear()
            width.attrib.update(reordered_attributes)

    roadMarks = root.xpath('.//roadMark')
    if roadMarks:
        new_attributes = ['sOffset', 'type', 'material', 'color', 'laneChange']
        for roadMark in roadMarks:
            reordered_attributes = [(attr, roadMark.attrib[attr]) for attr in new_attributes if attr in roadMark.attrib]
            roadMark.attrib.clear()
            roadMark.attrib.update(reordered_attributes)
    
    vectorLanes = root.xpath('.//vectorLane')
    if vectorLanes:
        new_attributes = ['sOffset', 'laneId', 'travelDir']
        for vectorLane in vectorLanes:
            reordered_attributes = [(attr, vectorLane.attrib[attr]) for attr in new_attributes if attr in vectorLane.attrib]
            vectorLane.attrib.clear()
            vectorLane.attrib.update(reordered_attributes)

    carriageways = root.xpath('.//carriageway')
    if carriageways:
        new_attributes = ['rightBoundary', 'leftBoundary']
        for carriageway in carriageways:
            reordered_attributes = [(attr, carriageway.attrib[attr]) for attr in new_attributes if attr in carriageway.attrib]
            carriageway.attrib.clear()
            carriageway.attrib.update(reordered_attributes)

        # Write the modified XML to a new file
        etree.ElementTree(root).write(xml_file, pretty_print=True, xml_declaration=True)


def transform_XODR(xodr_file, source_frame, target_frame, gps_path):
    xodr_name = os.path.basename(xodr_file) # with extension
    target_frame_name = os.path.basename(target_frame) # with extention
    target_name = os.path.splitext(target_frame_name)[0]

    # Parse the XML file and get the root element
    root = ET.parse(xodr_file).getroot()

    transferred_coords_file = gps_path + '/' + target_name + ".txt"
    with open(transferred_coords_file, "r") as f:
        transferred_coords = f.readline().strip().split(",")

    # Update the latitude and longitude values in the <geoReference> header
    geo_ref = root.find(".//geoReference")
    if geo_ref is not None:
        cdata = geo_ref.text.strip()
        parts = cdata.split(" ")
        for i in range(len(parts)):
            if parts[i].startswith("+lat_0="):
                parts[i] = "+lat_0=" + transferred_coords[0]
            elif parts[i].startswith("+lon_0="):
                parts[i] = "+lon_0=" + transferred_coords[1]
        geo_ref.text = " ".join(parts)

    # Loop over each road element in the map and transform its position and orientation
    for road in root.iter("geometry"):
        transform_matrix = get_tf_matrix(source_frame, target_frame)
        # Transform the road's position
        road_position = np.array([float(road.attrib["x"]), float(road.attrib["y"]), 0.0, 1.0])
        transformed_position = np.dot(transform_matrix, road_position)

        road.attrib["x"] = str(transformed_position[0])
        road.attrib["y"] = str(transformed_position[1])

        # Transform the road's orientation    
        direction_vector = np.array([math.cos(float(road.attrib["hdg"])), math.sin(float(road.attrib["hdg"])), 0])
        transformed_vector = transform_matrix.dot(np.append(direction_vector, 0))[:3] # np.array([direction_vector, 0])[:3]
        transformed_heading_angle = math.atan2(transformed_vector[1], transformed_vector[0])

        road.attrib["hdg"] = str(transformed_heading_angle)
        
    
    output_path = os.path.dirname(xodr_file) + "/tf_" + os.path.splitext(target_frame_name)[0] \
                    + ".xodr"
                    
    output_xodr = output_path

    tree = ET.ElementTree(root)
    tree.write(output_xodr, encoding="UTF-8", xml_declaration=True)
    reorder_attributes(output_xodr)
    print("Transfered map saved in: \n", output_path, '\n')
    return output_xodr


def transform_all_xodr(xodr_file, source_tf, tf_folder, gps_folder):
    # Get the list of all transformation matrix files in the tf directory
    target_tf_files = glob.glob(os.path.join(tf_folder, "*.txt"))
    target_tf_files.sort()  # Ensure transformations are applied in order

    # Keep track of the current transformed xodr file
    current_xodr = xodr_file

    # For each target_tf file
    for target_tf in target_tf_files:
        # Apply the transformation
        #current_xodr = transform_XODR(current_xodr, source_tf, target_tf, gps_folder)
        transform_XODR(current_xodr, source_tf, target_tf, gps_folder)
        


# xodr_map = '/home/joyboy/V2VMap/Test/Exports/test_map_30frames/test_map_30frames.xodr'
xodr_map =  '/home/joyboy/Desktop/MyLove/Exports/testoutput_CAV_data_2022-03-21-09-50-20_10/0/testoutput_CAV_data_2022-03-21-09-50-20_10_t.xodr'
source_tf = '/home/joyboy/V2VMap/testoutput_CAV_data_2022-03-21-09-50-20_10_t/tf/000000.txt'
tf_folder = '/home/joyboy/V2VMap/testoutput_CAV_data_2022-03-21-09-50-20_10_t/tf/'
gps_folder = '/home/joyboy/V2VMap/testoutput_CAV_data_2022-03-21-09-50-20_10_t/gps'

if __name__ == "__main__":
    transform_all_xodr(xodr_map, source_tf, tf_folder, gps_folder)
