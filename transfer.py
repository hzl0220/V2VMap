import os
import math

from lxml import etree
import xml.etree.ElementTree as ET
import numpy as np


def get_tf_matrix(source_frame, target_frame):
    source_frame = np.loadtxt(source_frame, delimiter=",")
    target_frame = np.loadtxt(target_frame, delimiter=",")
    target_inv = np.linalg.inv(target_frame)
    return np.dot(source_frame, target_inv)

def transform_XODR(xodr_file, transform_matrix):
    # Parse the XML file and get the root element
    root = ET.parse(xodr_file).getroot()

    # Loop over each road element in the map and transform its position and orientation
    for road in root.iter("geometry"):
        # Transfer the origin
        origin = np.array([0.0, 0.0, 0.0, 1.0])
        transformed_origin = np.dot(transform_matrix, origin)
        o_x, o_y, o_z, _ = transformed_origin

        # Transform the road's position
        road_position = np.array([float(road.attrib["x"]), float(road.attrib["y"]), 0.0, 1.0])
        transformed_position = np.dot(transform_matrix, road_position)
        transformed_position -= transformed_origin

        road.attrib["x"] = str(transformed_position[0])
        road.attrib["y"] = str(transformed_position[1])

        # Transform the road's orientation    
        direction_vector = np.array([math.cos(float(road.attrib["hdg"])), math.sin(float(road.attrib["hdg"])), 0])
        transformed_vector = transform_matrix.dot(np.append(direction_vector, 0))[:3] # np.array([direction_vector, 0])[:3]
        transformed_heading_angle = math.atan2(transformed_vector[1], transformed_vector[0])

        road.attrib["hdg"] = str(transformed_heading_angle)

    
    output_path = os.path.dirname(xodr_file) + "/transformed_" + os.path.basename(xodr_file)
    output_xodr = output_path

    tree = ET.ElementTree(root)
    tree.write(output_xodr, encoding="UTF-8", xml_declaration=True)
    reorder_attributes(output_xodr)
    print("Transfered map saved in:", "\n", output_path)
    return output_xodr


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


xodr_map = '/home/joyboy/V2VMap/Test/Exports/test_map_30frames.xodr'
source_tf = '/home/joyboy/V2VMap/testoutput_CAV_data_2022-03-15-09-54-40_0_astuff/tf/000000.txt'
target_tf = '/home/joyboy/V2VMap/testoutput_CAV_data_2022-03-15-09-54-40_0_astuff/tf/000015.txt'

tf = get_tf_matrix(source_tf, target_tf)
transformed_map = transform_XODR(xodr_map, tf)

