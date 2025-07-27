from multiplexer import project_pixel_to_ground

from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from datetime import datetime
import math
from arcgis.features import FeatureLayer, Feature

# Assuming the `project_pixel_to_ground` function is already defined above
import pandas as pd
from arcgis.gis import GIS
from arcgis.features import FeatureLayer, Feature
from arcgis.geometry import union
from datetime import datetime
import math
from arcgis.geometry import union, Geometry 

# Function to compute the polygon for each frame
def fovToFeatureLayer_compute_polygon(pixel_coord_top_left, pixel_coord_top_right, pixel_coord_bottom_left, pixel_coord_bottom_right,
                                      image_width, image_height, sensor_lat, sensor_lon, sensor_relative_altitude, takeoff_altitude,
                                      sensor_relative_elevation_angle, heading, fov_horizontal, fov_vertical):
    # Call `project_pixel_to_ground` for each corner
    top_left_lon, top_left_lat = project_pixel_to_ground(pixel_coord_top_left, image_width, image_height, sensor_lat, sensor_lon,
                                                          sensor_relative_altitude, takeoff_altitude, sensor_relative_elevation_angle,
                                                          heading, fov_horizontal, fov_vertical)

    top_right_lon, top_right_lat = project_pixel_to_ground(pixel_coord_top_right, image_width, image_height, sensor_lat, sensor_lon,
                                                           sensor_relative_altitude, takeoff_altitude, sensor_relative_elevation_angle,
                                                           heading, fov_horizontal, fov_vertical)

    bottom_left_lon, bottom_left_lat = project_pixel_to_ground(pixel_coord_bottom_left, image_width, image_height, sensor_lat, sensor_lon,
                                                                sensor_relative_altitude, takeoff_altitude, sensor_relative_elevation_angle,
                                                                heading, fov_horizontal, fov_vertical)

    bottom_right_lon, bottom_right_lat = project_pixel_to_ground(pixel_coord_bottom_right, image_width, image_height, sensor_lat, sensor_lon,
                                                                 sensor_relative_altitude, takeoff_altitude, sensor_relative_elevation_angle,
                                                                 heading, fov_horizontal, fov_vertical)

    # Create the polygon geometry using the four corners
    polygon_coords = [
        [top_left_lon, top_left_lat],
        [top_right_lon, top_right_lat],
        [bottom_right_lon, bottom_right_lat],
        [bottom_left_lon, bottom_left_lat],
        [top_left_lon, top_left_lat]  # Closing the polygon
    ]

    polygon_geometry = {
        "rings": [polygon_coords],
        "spatialReference": {"wkid": 4326}  # WGS84
    }
    geometry = Geometry(polygon_geometry)

    return geometry

def compute_and_push_polygons(feature_layer_url, df):
    # Initialize GIS instance (credentials are hardcoded)
    gis = GIS("https://intern-hackathon.maps.arcgis.com", "sambala_intern_hackathon", "<your_password_here>")
    layer = FeatureLayer(feature_layer_url)

    # Example pixel coordinates for each corner of the frame (a list of multiple sets of pixel coords)
    pixel_coord_top_left = (0, 0)  # Top-left corner (x, y)
    pixel_coord_top_right = (1920, 0)  # Top-right corner (x, y)
    pixel_coord_bottom_left = (0, 1080)  # Bottom-left corner (x, y)
    pixel_coord_bottom_right = (1920, 1080)  # Bottom-right corner (x, y)

    # Image size
    image_width = 1920
    image_height = 1080
    # List to store the computed polygon geometries
    polygons = []

    # Step 1: Iterate over each row of the DataFrame and compute the polygon
    for _, row in df.iterrows():
        sensor_lat = row['SensorLatitude']
        sensor_lon = row['SensorLongitude']
        sensor_relative_altitude = row['SensorTrueAltitude']
        takeoff_altitude = row['TakeoffLocationAltitude']
        sensor_relative_elevation_angle = row['SensorRelativeElevationAngle']
        heading = row['PlatformHeadingAngle']
        fov_horizontal = row['SensorHorizontalFieldOfView']
        fov_vertical = row['SensorVerticalFieldOfView']

        # Compute the polygon using the provided function
        polygon_geometry = fovToFeatureLayer_compute_polygon(
            pixel_coord_top_left, pixel_coord_top_right, pixel_coord_bottom_left, pixel_coord_bottom_right,
            image_width, image_height, sensor_lat, sensor_lon, sensor_relative_altitude, takeoff_altitude,
            sensor_relative_elevation_angle, heading, fov_horizontal, fov_vertical
        )



        # Step 3: Create the feature from the final polygon
        polygon_feature = Feature(geometry=polygon_geometry)

        # Step 4: Push the final unioned polygon to the feature layer
        try:
            result = layer.edit_features(adds=[polygon_feature])

            if result.get("addResults") and result["addResults"][0]["success"]:
                object_id = result["addResults"][0]["objectId"]
                print(f"✅ Final Polygon added with objectId={object_id}")
            else:
                print("❌ Failed to add final polygon:", result)

        except Exception as e:
            print("🌐 ArcGIS Push Error:", e)

# # Example DataFrame with your real data (replace with your actual DataFrame)
# df = pd.DataFrame({
#     'sensor_lat': [34.060275154, 34.06027522],
#     'sensor_lon': [-117.196949636, -117.1969497],
#     'sensor_relative_altitude': [335.47, 335.47],
#     'takeoff_altitude': [319.77, 319.77],
#     'sensor_relative_elevation_angle': [-36.84, -34.62],
#     'heading': [52, 52.2],
#     'fov_horizontal': [66.69, 66.69],
#     'fov_vertical': [40.62, 40.62]
# })
 