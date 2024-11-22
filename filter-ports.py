#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import pandas as pd


# Get the file path
__location__ = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))
# Load the coordinates of ports
df = pd.read_csv(os.path.join(
    __location__, 'raw-data/UN-LOCODE.csv'), low_memory=False)


# Define a function to split the Coordinates field
def split_coordinates(coord):
    if pd.isna(coord) or coord.strip() == '':
        return None, None
    match = re.match(r'(\d{2})(\d{2})([NS])\s*(\d{3})(\d{2})([EW])', coord)
    if not match:
        return None, None
    lat_deg, lat_min, lat_dir, lon_deg, lon_min, lon_dir = match.groups()

    # Calculate latitude
    latitude = int(lat_deg) + int(lat_min) / 60.0
    if lat_dir == 'S':
        latitude = -latitude

    # Calculate longitude
    longitude = int(lon_deg) + int(lon_min) / 60.0
    if lon_dir == 'W':
        longitude = -longitude

    return longitude, latitude


# Apply the function to split the Coordinates field and create 'Longitude' and 'Latitude' columns
df['Longitude'], df['Latitude'] = zip(
    *df['Coordinates'].apply(split_coordinates))

# Create the 'Code' field (concatenation of 'Country' and 'Location')
df['Code'] = df['Country'] + df['Location']

# Exclude ports without valid coordinates (i.e., both Longitude and Latitude are not None)
df = df[df['Longitude'].notna() & df['Latitude'].notna()]

# # Filter records for sea ports (Function = '1')
# seaports_df = df[df['Function'].str.contains('1', na=False)]
# seaports_result = seaports_df[['Code', 'Name', 'NameWoDiacritics', 'Function', 'Longitude', 'Latitude']]
# seaports_result.sort_values(by='Code')
# seaports_result.to_csv(os.path.join(__location__, 'ports-sea.csv'), index=False)
# print("Sea port data has been saved to 'ports-sea.csv'")

# # Filter records for river ports (Function = '6')
# riverports_df = df[df['Function'].str.contains('6', na=False)]
# riverports_result = riverports_df[['Code', 'Name', 'NameWoDiacritics', 'Function', 'Longitude', 'Latitude']]
# riverports_result.sort_values(by='Code')
# riverports_result.to_csv(os.path.join(__location__, 'ports-river.csv'), index=False)
# print("River port data has been saved to 'ports-river.csv'")

# Filter records for all ports (Function = '1' or '6')
all_df = df[df['Function'].str.contains('1|6', na=False)]
ports_result = all_df[['Code', 'Name', 'NameWoDiacritics',
                       'Function', 'Longitude', 'Latitude']]
ports_result.sort_values(by='Code')
ports_result.to_csv(os.path.join(__location__, 'ports.csv'), index=False)
print("Ports data have been saved to 'ports.csv'")
