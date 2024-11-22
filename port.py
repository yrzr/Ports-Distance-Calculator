#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import csv


class Port:
    """
    A class to represent a port.
    """
    def __init__(self, code: str, name: str, name_wo_diacritics: str, function: str, longitude: float, latitude: float):
        """Initialize a Port object"""
        self.code = code
        self.name = name
        self.name_wo_diacritics = name_wo_diacritics
        self.function = function
        self.longitude = float(longitude)
        self.latitude = float(latitude)
        self.coordinates = (self.latitude, self.longitude)

    def __repr__(self):
        """Return a string representation of the Port object"""
        return f"Port(code=\"{self.code}\", name=\"{self.name}\", name_wo_diacritics=\"{self.name_wo_diacritics}\", function=\"{self.function}\", longitude={self.longitude}, latitude={self.latitude})"


class PortManager:
    """
    A class to manage a list of Port objects.
    """
    def __init__(self, csv_file: str):
        """Initialize PortManager with a CSV file path and load ports"""
        self.csv_file = csv_file
        self.ports = self._load_ports_from_csv()

    def _load_ports_from_csv(self):
        """Internal method: Read from the CSV file and create a list of Port objects"""
        ports = []
        with open(self.csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                if row:  # Ensure the row is not empty
                    # Unpack the row data and pass it to Port class
                    _port = Port(*row)
                    ports.append(_port)
        print(f"Loaded {len(ports)} ports from {self.csv_file}")
        return ports

    def get_ports(self):
        """Return a list of all Port objects"""
        return self.ports

    def find_port_by_code(self, code: str):
        """Find a Port object by its code"""
        return next((port for port in self.ports if port.code == code), None)


if __name__ == "__main__":
    location = os.path.realpath(os.path.join(
        os.getcwd(), os.path.dirname(__file__)))
    port_file = os.path.join(location, "ports.csv")

    # Instantiate PortManager and load port data
    manager = PortManager(port_file)

    # Find a specific port by its code
    # HKGOM: 2046 HongKong Hung Hom
    # CNPDG: 16648 Shanghai Pudong
    # USZJI: 9014 LOS ANGELES
    # NLAMS: 5705 AMSTERDAM
    code = "NLAMS"
    port = manager.find_port_by_code(code)
    if port:
        print(f"Found port: {port}")
    else:
        print(f"Port with code {code} not found.")
