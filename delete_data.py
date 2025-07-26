from arcgis.gis import GIS
from arcgis.features import FeatureLayer

gis = GIS("https://intern-hackathon.maps.arcgis.com", "sambala_intern_hackathon", "Thisispizza@2477")
feature_layer_url = "https://services8.arcgis.com/LLNIdHmmdjO2qQ5q/arcgis/rest/services/test_layer/FeatureServer/0"
layer = FeatureLayer(feature_layer_url)

features = layer.query(where="1=1", return_ids_only=True)

if features and "objectIds" in features:
    object_ids = features["objectIds"]
    print(f"Found {len(object_ids)} features. Deleting...")
    id_string = ",".join(map(str, object_ids))
    result = layer.delete_features(deletes=id_string)

    print("Delete result:", result)
else:
    print("No features to delete.")
