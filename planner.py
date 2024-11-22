#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from osgeo import gdal
from skimage.graph import route_through_array
import numpy as np
from geopy.distance import great_circle
import matplotlib.pyplot as plt
from port import Port


class Planner:
    """
    A class to plan sea routes on a cost surface array.
    """
    def __init__(self, _map_file):
        """
        Initialize the Planner class, load the map and port data.

        Args:
            map_file (str): Path to the map file (GeoTIFF format).
            ports_file (str): Path to the CSV file containing port data.
        """
        # Load map data
        self.dataset = gdal.OpenEx(_map_file, gdal.GA_ReadOnly)
        if self.dataset is None:
            raise FileNotFoundError(f"Failed to load map file: {_map_file}")

        self.band = self.dataset.GetRasterBand(1)
        self.map = self.band.ReadAsArray()

        # Raster dimensions and geotransform
        self.origin_x, self.pixel_width, _, self.origin_y, _, self.pixel_height = self.dataset.GetGeoTransform()

    def coord_to_pixel_index(self, coord, pixel_x_offset):
        """
        Converts geographic coordinates to pixel indices based on the map's origin and pixel dimensions.

        Args:
            coord (tuple): The coordinate to convert in the format (latitude, longitude).
            pixel_x_offset (int): The amount to shift the x offset by.

        Returns:
            tuple: The x and y pixel indices.
        """
        pixel_x = int((coord[1] - self.origin_x) /
                      self.pixel_width) + pixel_x_offset
        # If the x index falls off the map, wrap around
        if pixel_x < 0:
            pixel_x += self.map.shape[1]
        pixel_y = int((coord[0] - self.origin_y) / self.pixel_height)
        return pixel_x, pixel_y

    def cal_map_pixel_x_offset(self, start_coord, stop_coord):
        """
        Calculate the horizontal shift for the map to avoid paths crossing the map boundary.

        Args:
            start_coord (tuple): The starting coordinate (latitude, longitude).
            stop_coord (tuple): The stopping coordinate (latitude, longitude).

        Returns:
            int: The calculated x offset for the map.
        """
        if abs(stop_coord[1] - start_coord[1]) < 180:
            return -int(((start_coord[1] + stop_coord[1])) / 2 / self.pixel_width)
        else:
            return -int(((start_coord[1] + stop_coord[1] + 360)) / 2 / self.pixel_width)

    def create_path(self, start_coord, stop_coord, draw_path=None):
        """
        Create a path between two coordinates on a cost surface array.

        Args:
            start_coord (tuple): The starting coordinate (latitude, longitude).
            stop_coord (tuple): The stopping coordinate (latitude, longitude).
            draw_path (str, optional): Output file to save the path plot. Defaults to None.

        Returns:
            numpy.ndarray: The path coordinates as an array of shape (2, n), where n is the number of points in the path.
        """
        pixel_x_offset = self.cal_map_pixel_x_offset(start_coord, stop_coord)
        cost_surface_array = np.roll(self.map, pixel_x_offset)

        # Convert coordinates to pixel indices
        start_pixel_x, start_pixel_y = self.coord_to_pixel_index(
            start_coord, pixel_x_offset)
        stop_pixel_x, stop_pixel_y = self.coord_to_pixel_index(
            stop_coord, pixel_x_offset)

        # Find the path using a cost surface algorithm
        indices, _ = route_through_array(
            cost_surface_array,
            (start_pixel_y, start_pixel_x),
            (stop_pixel_y, stop_pixel_x),
            fully_connected=True,
            geometric=True
        )
        indices = np.array(indices).T

        # Optionally draw the path on the map
        if draw_path is not None:
            plt.figure(figsize=(18, 9))
            plt.imshow(cost_surface_array)
            plt.plot(indices[1], indices[0], color="red")
            plt.savefig(draw_path)
            print("The path has been saved to", draw_path)

        # Convert pixel indices back to geographic coordinates
        indices = indices.astype(float)
        indices[1] = indices[1] * self.pixel_width + self.origin_x
        indices[0] = indices[0] * self.pixel_height + self.origin_y
        return indices

    def cal_distance_by_coordinates(self, start_coord, stop_coord, draw_path=None):
        """
        Calculate the distance between two coordinates using the Haversine formula.

        Args:
            start_coord (tuple): The starting coordinate (latitude, longitude).
            stop_coord (tuple): The ending coordinate (latitude, longitude).
            draw_path (str, optional): Output file to save the path plot. Defaults to None.

        Returns:
            float: The calculated distance in kilometers.
        """
        path_indices = self.create_path(start_coord, stop_coord, draw_path)

        lat1, lon1 = path_indices[0][:-1], path_indices[1][:-1]
        lat2, lon2 = path_indices[0][1:], path_indices[1][1:]

        distances = np.vectorize(lambda a, b, c, d: great_circle(
            (a, b), (c, d)).km)(lat1, lon1, lat2, lon2)
        total_distance = np.sum(distances)

        print(f"Total distance: {total_distance} km")
        return total_distance

    def cal_distance(self, _from: Port, _to: Port, draw_path=None):
        """
        Calculate the distance between two ports.

        Args:
            _from (Port): The starting port object.
            _to (Port): The stopping port object.
            draw_path (str, optional): Output file to save the path plot. Defaults to None.

        Returns:
            float: The calculated distance in kilometers.
        """
        print(f"From: {_from.code}, {_from.name}, {_from.coordinates}")
        print(f"To: {_to.code}, {_to.name}, {_to.coordinates}")

        return self.cal_distance_by_coordinates(_from.coordinates, _to.coordinates, draw_path)


if __name__ == "__main__":
    # Get file paths
    location = os.path.realpath(os.path.join(
        os.getcwd(), os.path.dirname(__file__)))
    map_file = os.path.join(location, "raw-data/map.tif")
    draw_file = os.path.join(location, "sea-route.png")

    # Initialize the Planner
    planner = Planner(map_file)
    port_HKGOM = Port(code="HKGOM", name="Hung Hom", name_wo_diacritics="Hung Hom",
                      function="-----6--", longitude=114.18333333333334, latitude=22.3)
    port_CNPDG = Port(code="CNPDG", name="Pudong/Shanghai", name_wo_diacritics="Pudong/Shanghai",
                      function="1-3-----", longitude=121.5, latitude=31.233333333333334)
    port_USZJI = Port(code="USZJI", name="Alpine, Los Angeles", name_wo_diacritics="Alpine, Los Angeles",
                      function="-23--6--", longitude=-118.1, latitude=34.53333333333333)
    port_NLAMS = Port(code="NLAMS", name="Amsterdam", name_wo_diacritics="Amsterdam",
                      function="12345---", longitude=4.816666666666666, latitude=52.4)
    port_CNNHN = Port(code="CNNHN", name="Wuhan", name_wo_diacritics="Wuhan",
                      function="12-45---", longitude=114.28333333333333, latitude=30.583333333333332)
    planner.cal_distance(port_HKGOM, port_USZJI, draw_file)
