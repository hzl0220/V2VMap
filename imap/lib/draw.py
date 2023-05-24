import io
import math

import numpy as np
import cv2

import imap.editor as editor
import imap.global_var as global_var


CV2_SHIFT_VALUE = 2 ** 9
image = np.zeros((256, 256, 3), np.uint8)

def draw(hdmap, lane_id):
    lane_ids = [] 
    junction_ids = []
    hdmap.draw_lanes(ax, lane_id)
    hdmap.draw_junctions(ax, junction_ids)
    hdmap.draw_signals(ax)
    hdmap.draw_crosswalks(ax)
    hdmap.draw_stop_signs(ax)
    hdmap.draw_yields(ax)


def get_ego_UTM():
    # Get the ego UTM location
    ego_location = global_var.get_element_value("ego_UTM")
    return ego_location


def cv2_subpixel(coords: np.ndarray) -> np.ndarray:
    """
    Cast coordinates to numpy.int but keep fractional part by previously multiplying by 2**CV2_SHIFT
    cv2 calls will use shift to restore original values with higher precision

    Args:
        coords (np.ndarray): XY coords as float

    Returns:
        np.ndarray: XY coords as int for cv2 shift draw
    """
    
    coords = coords * CV2_SHIFT_VALUE
    coords = coords.astype(np.int)
    return coords


def normalize_points(x, y):
    # Transform all the points that relatively to ego
    ego_UTM = get_ego_UTM()
    norm_x = [int(256/50 * (ego_UTM[0] - _x)) + 128 for _x in x]
    norm_y = [int(256/50 * (ego_UTM[1] - _y)) + 128 for _y in y]
    return norm_x, norm_y


def draw_line(line, reference_line=False, label=""):
    # key points of lane/line
    x = [point.x for point in line]
    y = [point.y for point in line]
    norm_x, norm_y = normalize_points(x, y)

    color = (0, 255, 0)  # Green color
    thickness = 2
    
    # Draw each key points
    for point in list(zip(norm_x, norm_y)):
        cv2.circle(image, point, thickness, color, -1)

    # Draw ego vehicle
    cv2.circle(image, (128, 128), 6, (255, 255, 0), -1)


def draw_road(left_boundary, right_boundary, vis=False):
    # Draw road surface represented by polygon
    color = (0, 0, 0) if vis else (0, 120, 255)

    left_x = [point.x for point in left_boundary]
    left_y = [point.y for point in left_boundary]
    norm_left_x, norm_left_y = normalize_points(left_x, left_y)
    
    right_x = [point.x for point in right_boundary]
    right_y = [point.y for point in right_boundary]
    norm_right_x, norm_right_y = normalize_points(right_x, right_y)

    left_points = list(zip(norm_left_x, norm_left_y))
    right_points = list(zip(norm_right_x, norm_right_y))
    
    lane_area_list = np.array(left_points + right_points[::-1], np.int32)
    # print(lane_area_list)

    for lane_area in lane_area_list:
        lane_area = lane_area.reshape(-1, 2)
    cv2.fillPoly(image, [lane_area_list], color)


def show(need_save=True, path=None):
    # show
    cv2.imshow("Image", image)

    if need_save is not None:
        cv2.imwrite(path, image)
        print(f"Image saved as {path}")

    # img_arry shape:
    # print("Saved Successfully: ", path)
    # print("nparray size: ", img_array.shape)
