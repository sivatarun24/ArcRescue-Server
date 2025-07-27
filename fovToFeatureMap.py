from multiplexer import project_pixel_to_ground

from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from datetime import datetime
import math
from arcgis.features import FeatureLayer, Feature
# Assuming the `project_pixel_to_ground` function is already defined above

def fovToFeatureLayer(feature_layer_url, pixel_coord_top_left, pixel_coord_top_right, pixel_coord_bottom_left, pixel_coord_bottom_right,
                      image_width, image_height, sensor_lat, sensor_lon, sensor_relative_altitude, takeoff_altitude,
                      sensor_relative_elevation_angle, heading, fov_horizontal, fov_vertical):
    # Initialize GIS instance (credentials are hardcoded)
    gis = GIS("https://intern-hackathon.maps.arcgis.com", "pvan_intern_hackathon", "Peter242003$Abc123$$$")
    layer = FeatureLayer(feature_layer_url)
    
    # Step 1: Call `project_pixel_to_ground` for each corner
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
    
    # Step 2: Create the polygon geometry using the four corners
    print(bottom_right_lon, bottom_right_lat)
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
    
    polygon_feature = Feature(geometry=polygon_geometry)
    
    # Step 3: Add the polygon to the feature layer
    try:
        result = layer.edit_features(adds=[polygon_feature])

        if result.get("addResults") and result["addResults"][0]["success"]:
            object_id = result["addResults"][0]["objectId"]
            print(f"✅ Polygon added with objectId={object_id}")
        else:
            print("❌ Failed to add polygon:", result)

    except Exception as e:
        print("🌐 ArcGIS Push Error:", e)

# Example usage:

# Feature layer URL
feature_layer_url = "https://services8.arcgis.com/LLNIdHmmdjO2qQ5q/arcgis/rest/services/FOV_one/FeatureServer/0"

# Example pixel coordinates for each corner of the frame
pixel_coord_top_left = (0, 0)  # Top-left corner (x, y)
pixel_coord_top_right = (1920, 0)  # Top-right corner (x, y)
pixel_coord_bottom_left = (0, 1080)  # Bottom-left corner (x, y)
pixel_coord_bottom_right = (1920, 1080)  # Bottom-right corner (x, y)

# Drone and camera parameters
image_width = 1920
image_height = 1080
sensor_lat = 34.060275154
sensor_lon = -117.196949636
sensor_relative_altitude = 335.47  # Drone height above ground (in meters)
takeoff_altitude = 319.77
sensor_relative_elevation_angle = -36.84  # Camera pitch in degrees (negative = downward)
heading = 52  # Camera heading in degrees
fov_horizontal = 66.69  # Horizontal field of view in degrees
fov_vertical = 40.62  # Vertical field of view in degrees

# Call the function
fovToFeatureLayer(feature_layer_url, pixel_coord_top_left, pixel_coord_top_right, pixel_coord_bottom_left, pixel_coord_bottom_right,
                  image_width, image_height, sensor_lat, sensor_lon, sensor_relative_altitude, takeoff_altitude,
                  sensor_relative_elevation_angle, heading, fov_horizontal, fov_vertical)

sensor_lat =	34.06027522
sensor_lon	-117.1969497
heading = 	52.2	
sensor_relative_altitude =	335.47	
sensor_relative_elevation_angle =	-34.62
takeoff_altitude =	319.77

fovToFeatureLayer(feature_layer_url, pixel_coord_top_left, pixel_coord_top_right, pixel_coord_bottom_left, pixel_coord_bottom_right,
                  image_width, image_height, sensor_lat, sensor_lon, sensor_relative_altitude, takeoff_altitude,
                  sensor_relative_elevation_angle, heading, fov_horizontal, fov_vertical)
