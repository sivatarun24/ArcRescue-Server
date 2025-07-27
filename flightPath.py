from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from datetime import datetime

def add_flight_path_to_layer(feature_layer_url, coordinates_latlon, color):
    # Connect to GIS
    gis = GIS("https://intern-hackathon.maps.arcgis.com", "sambala_intern_hackathon", "<your_password_here>")
    layer = FeatureLayer(feature_layer_url)

    # Define renderer with the provided color
    renderer = {
        "type": "simple",
        "symbol": {
            "type": "esriSLS",            # Simple Line Symbol
            "style": "esriSLSSolid",
            "color": color,               # Color provided as input (RGBA format)
            "width": 7                    # Line width in screen pixels
        }
    }

    # Convert to [ [x, y], [x, y], ... ] (i.e., [ [lon, lat], ... ])
    polyline_coords = [[lon, lat] for lat, lon in coordinates_latlon]

    # Define the polyline geometry
    polyline_feature = {
        "geometry": {
            "paths": [polyline_coords],
            "spatialReference": {"wkid": 4326}
        },
        "attributes": {
            "Time_stamp": datetime.utcnow().isoformat(),  # or use other attributes
            "Longitude": polyline_coords[0][0],  # Take longitude from the first coordinate pair
            "Latitude": polyline_coords[0][1]
        }
    }

    # Push to feature layer
    try:
        result = layer.edit_features(adds=[polyline_feature])

        # Update renderer for the feature layer
        layer.manager.update_definition({
            "drawingInfo": {
                "renderer": renderer,
                "transparency": 0
            },
            "minScale": 0,           # visible at all zoom levels
            "maxScale": 0
        })

        if result.get("addResults") and result["addResults"][0]["success"]:
            print("✅ Flight path added successfully!")
        else:
            print("❌ Failed to add flight path:", result)
    except Exception as e:
        print("🌐 Error:", e)

# # Example usage:
# flight_layer_url = "https://services8.arcgis.com/LLNIdHmmdjO2qQ5q/arcgis/rest/services/FlightPath_two/FeatureServer/0"
# coordinates_latlon = [
#     (34.06027515, -117.1969496),
#     (34.06027515, -117.1969497),
#     (34.06027518, -117.1969497),
#     (34.06027522, -117.1969497),
#     (34.06027528, -117.1969495),
#     (34.06027538, -117.1969493),
#     (34.06027559, -117.1969491),
#     (34.06027577, -117.1969488),
#     (34.06027605, -117.1969485),
#     (34.06027631, -117.1969481),
#     (34.0602766,  -117.1969478),
#     (34.06027698, -117.1969472),
#     (34.06027738, -117.1969464),
#     (34.06027795, -117.1969455),
#     (34.06027875, -117.1969445),
#     (34.06027962, -117.1969432),
#     (34.06028054, -117.1969417)
# ]
# color = [0, 0, 255, 255]  # Example color: Blue (RGBA format)

# # Call the function
# add_flight_path_to_layer(flight_layer_url, coordinates_latlon, color)
