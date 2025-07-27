import os
import io
from io import BytesIO
from arcgis.features import Feature
from datetime import datetime
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import tempfile

gis = GIS("https://intern-hackathon.maps.arcgis.com", "sambala_intern_hackathon", "<your_password_here>")
feature_layer_url = "https://services8.arcgis.com/LLNIdHmmdjO2qQ5q/arcgis/rest/services/test_layer/FeatureServer/0"
layer = FeatureLayer(feature_layer_url)

def push_person_location(lat, lon, confidence, image_data=None):
    new_feature = {
        "geometry": {
            "x": lon,
            "y": lat,
            "spatialReference": {"wkid": 4326}
        },
        "attributes": {
            "Latitude": lat,
            "Longitude": lon,
            "Confidence": confidence
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
                    print("Image attached successfully.")
                else:
                    print("Failed to attach image:", attachment_result)
        else:
            print("Failed to add feature:", result)

    except Exception as e:
        print("ArcGIS Push Error:", e)