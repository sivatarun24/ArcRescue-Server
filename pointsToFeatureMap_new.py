from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from datetime import datetime
import os
import tempfile
import cv2
from io import BytesIO
import pytz


def push_person_location_new(feature_layer_url, lat, lon, num_people, confidence, Time_stamp, image_data=None):
    # Initialize GIS instance (credentials are hardcoded)
    gis = GIS("https://intern-hackathon.maps.arcgis.com", "pvan_intern_hackathon", "Peter242003$Abc123$$$")
    layer = FeatureLayer(feature_layer_url)
    
    custom_image_path = "https://intern-hackathon.maps.arcgis.com/sharing/rest/content/items/641c8b31ef784fb3be125fbe21d8b9b8/data"

    if custom_image_path:
        symbol = {
            "type": "esriPMS",  # Picture Marker Symbol
            "url": custom_image_path,  # URL or file path to custom image
            "width": 24,  # Size of the image (can be adjusted)
            "height": 24
        }
    else:
        # Default simple point symbol (if no custom image is provided)
        symbol = {
            "type": "esriSMS",  # Simple Marker Symbol
            "style": "esriSMSCircle",
            "color": [255, 0, 0, 255],  # Red
            "size": 8
        }

    parsed_time = datetime.strptime(Time_stamp, "%Y-%m-%d_%H-%M-%S.%f")
    pacific = pytz.timezone("America/Los_Angeles")
    localized_time = pacific.localize(parsed_time)

    new_feature = {
        "geometry": {
            "x": lon,
            "y": lat,
            "spatialReference": {"wkid": 4326}
        },
        "attributes": {
            "Latitude": lat,
            "Longitude": lon,
            "Number_People": num_people,
            "Confidence": confidence,
            "Time_Stamp": localized_time.isoformat(),  # Ensure Time_stamp is in ISO format
            # "Time_Stamp": datetime.utcnow().isoformat()  # Can also use the Time_stamp param if desired
        }
    }

    try:
        result = layer.edit_features(adds=[new_feature])

        if result.get("addResults") and result["addResults"][0]["success"]:
            object_id = result["addResults"][0]["objectId"]
            print(f"Feature added: ({lat}, {lon}) with objectId={object_id}")

            if image_data:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    tmp.write(image_data.getbuffer())
                    tmp_path = tmp.name

                attachment_result = layer.attachments.add(object_id, tmp_path)
                os.remove(tmp_path)

                if attachment_result.get("addAttachmentResult", {}).get("success"):
                    print("📎 Image attached successfully.")
                else:
                    print("Failed to attach image:", attachment_result)
        else:
            print("Failed to add feature:", result)

    except Exception as e:
        print("ArcGIS Push Error:", e)



# # Example usage:

# # Feature layer URL
# feature_layer_url = "https://services8.arcgis.com/LLNIdHmmdjO2qQ5q/arcgis/rest/services/Detected_flyone/FeatureServer/0"

# # Image processing example
# frame = cv2.imread("frame_0.jpg")  # or from a video stream
# _, buffer = cv2.imencode('.jpg', frame)
# img_byte_arr = BytesIO(buffer.tobytes())

# # Push data
# push_person_location_new(feature_layer_url, 39.0602825, -118.1968400, 2, 0.88, datetime.utcnow().isoformat(), image_data=img_byte_arr)
