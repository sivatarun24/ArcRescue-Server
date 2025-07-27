from arcgis.gis import GIS
from arcgis.features import FeatureLayer

gis = GIS("https://intern-hackathon.maps.arcgis.com", "sambala_intern_hackathon", "<your_password_here>")
feature_layer_url = "https://services8.arcgis.com/LLNIdHmmdjO2qQ5q/arcgis/rest/services/Detected_flytwo/FeatureServer/0"
layer = FeatureLayer(feature_layer_url)

features = layer.query(where="1=1", return_ids_only=True)

if features and "objectIds" in features and features["objectIds"]:
    object_ids = features["objectIds"]
    print(f"Deleting {len(object_ids)} features...")

    id_string = ",".join(map(str, object_ids))
    result = layer.delete_features(deletes=id_string)
    print("Deletion result:", result)
else:
    print("No features found to delete. Skipping deletion.")
