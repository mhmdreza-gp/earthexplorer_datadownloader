import json
from typing import List

import geopandas as gpd
from landsatxplore.api import API

username = "mhmdreza"
password = "M4610694530g"

# Initialize a new API instance and get an access key
api = API(username, password)

body = {
    "datasetID": "5e83d0e09a752cff"
}

# Read shape_file
shape_file_path = r'C:\Users\Ya Saheb(al)Zaman\Desktop\test\polypoly.shp'
gdf = gpd.read_file(shape_file_path)

# Check CRS and convert if necessary
if gdf.crs != {'init': 'epsg:4326'}:  # Check if CRS is EPSG 4326 (WGS 84)
    gdf = gdf.to_crs("EPSG:4326")  # Convert to WGS 84 if not

# Access coordinates and save as decimal lat/long
coordinates = []
for index, row in gdf.iterrows():
    geometry = row['geometry']
    if geometry.geom_type == 'Polygon':
        # For polygons
        polygon_coord = []
        for point in geometry.exterior.coords:
            lat, lon = point
            # Append latitude and longitude to polygon_coords list
            polygon_coord.append((lat, lon))
        # Append polygon coordinates list to coordinates list
        coordinates.append(polygon_coord)
    elif geometry.geom_type == 'Point':
        # For points
        lat, lon = geometry.coords[0]
        # Append latitude and longitude to coordinates list
        coordinates.append((lat, lon))
    # You can similarly handle other geometry types (e.g., LineString, MultiPolygon, etc.)

# Print or use coordinates as needed
# print(coordinates)

# Initialize min and max values
x_min = float('inf')
y_min = float('inf')
x_max = float('-inf')
y_max = float('-inf')

# Iterate through coordinates to find min and max values
for coord in coordinates:
    if isinstance(coord[0], tuple):  # Check if it's a single coordinate tuple
        coord = [coord]  # Convert to list of tuples if single tuple
    for coord_set in coord:
        for lat, lon in coord_set:
            # Update min and max values
            x_min = min(x_min, lon)
            y_min = min(y_min, lat)
            x_max = max(x_max, lon)
            y_max = max(y_max, lat)

# Print or use the calculated bounding box
print(f"x_min: {x_min}, y_min: {y_min}, x_max: {x_max}, y_max: {y_max}")

# Search for Landsat TM scenes
scenes: list[dict] = api.search(
    dataset='landsat_tm_c2_l2',
    # latitude=50.85,
    # longitude=-4.35,
    bbox=(x_min, y_min, x_max, y_max),
    # row=165,
    # path=38,
    start_date='1988-03-01',
    end_date='1992-07-07',
    max_cloud_cover=1.0,
    max_results=2000
)

scenes_2 = api.search(
    dataset='landsat_tm_c2_l1',
    # latitude=50.85,
    # longitude=-4.35,
    bbox=(x_min, y_min, x_max, y_max),
    # row=165,
    # path=38,
    start_date='1988-03-01',
    end_date='1992-07-07',
    max_cloud_cover=1.0,
    max_results=2000
)

print(f"{len(scenes)} scenes found.")

print(f"{len(scenes_2)} scenes found.")

for scene in scenes:
    data_type = scene['data_type']
    acquisition_date = scene['acquisition_date']
    landsat_scene_id = scene['landsat_scene_id']
    print(f"Data Type: {data_type}, Acquisition Date: {acquisition_date}, Landsat Scene ID: {landsat_scene_id}")

print('\n')

for scene in scenes_2:
    data_type = scene['data_type']
    acquisition_date = scene['acquisition_date']
    landsat_scene_id = scene['landsat_scene_id']
    print(f"Data Type: {data_type}, Acquisition Date: {acquisition_date}, Landsat Scene ID: {landsat_scene_id}")

#print(scenes)
#print(scenes_2)

z = []
for img1 in scenes:
    for img2 in scenes_2:
        if img1['acquisition_date'] == img2['acquisition_date']:
            z.append((img1, img2))
            # print(z['acquisition_date'])

for s in scenes: print(s['acquisition_date'], s['landsat_scene_id'])

# Initialize empty lists to store entity_ids
matching_entity_ids_1 = []
matching_entity_ids_2 = []

for scene_1 in scenes:
    for scene_2 in scenes_2:
        if (scene_1['wrs_path'] == scene_2['wrs_path'] and
                scene_1['wrs_row'] == scene_2['wrs_row'] and
                scene_1['acquisition_date'] == scene_2['acquisition_date']):
            matching_entity_ids_1.append(scene_1['entity_id'])
            # matching_entity_ids_1.append(scene_1['display_id'])
            matching_entity_ids_2.append(scene_2['entity_id'])
            # matching_entity_ids_2.append(scene_2['display_id'])

print("\n", "Matching entity IDs:")

print("Matching entity IDs in scenes:", matching_entity_ids_1)
print("Matching entity IDs in scenes_2:", matching_entity_ids_2)

# Print the matching entity_ids
print("Entity IDs in scenes:")
print(matching_entity_ids_1)
print("Entity IDs in scenes_2:")
print(matching_entity_ids_2)

# Calculate the lengths of matching_entity_ids_1 and matching_entity_ids_2
len_matching_entity_ids_1 = len(matching_entity_ids_1)
len_matching_entity_ids_2 = len(matching_entity_ids_2)

# Print the lengths
print("Number of matching entity IDs in scenes:", len_matching_entity_ids_1)
print("Number of matching entity IDs in scenes_2:", len_matching_entity_ids_2)

"""run the code to this line"""

# Process the result
for scene in scenes:
    print(scene['acquisition_date'].strftime('%Y-%m-%d'))
    # Write scene footprints to disk
    fname = f"{scene['landsat_product_id']}.geojson"
    with open(fname, "w") as f:
        json.dump(scene['spatial_coverage'].__geo_interface__, f)

api.logout()

import os
from landsatxplore.earthexplorer import EarthExplorer
ee: EarthExplorer = EarthExplorer(username, password)

errors = 0
for i, scene in enumerate(matching_entity_ids_2):

    scene2 = matching_entity_ids_1[i]
    print(scene)
    print(scene2)
    try:
        scene1_status = ee.download(scene, dataset="landsat_tm_c2_l1", output_dir='D:\\DATA\\test_main', justcheck=True)
        scene2_status = ee.download(scene2, dataset="landsat_mss_c2_l1", output_dir='D:\\DATA\\test_main', justcheck=True)



    except Exception:
        print("ERROR")
        errors += 1
        continue

    path_name = f'D:\\DATA\\test2\\{scene}_{scene2}'
    if not os.path.exists(path_name):
        os.mkdir(path_name)

    ee.download(scene, dataset="landsat_tm_c2_l1", output_dir=path_name)
    ee.download(scene2, dataset="landsat_mss_c2_l1", output_dir=path_name)

print("Errors count = {errors}".format(errors=errors))
ee.logout()
