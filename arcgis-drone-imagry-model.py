from arcgis.gis import GIS
from arcgis.learn import Model
import os


# ----------------------------
# CONFIGURATION
# ----------------------------
INPUT_IMAGE_PATH = "person1.jpg"
OUTPUT_IMAGE_PATH = "output_with_persons.jpg"


# # DLPK model from ArcGIS Online (includes 'person' class)
MODEL_ITEM_ID = "42bfd5392d834c83aa21193450888a9e"

# # ----------------------------
# # AUTHENTICATE TO ARCGIS ONLINE
# # ----------------------------
print("Connecting to ArcGIS Online...")
gis = GIS("https://intern-hackathon.maps.arcgis.com", "sambala_intern_hackathon", "Thisispizza@2477")

# ----------------------------
# DOWNLOAD MODEL
# ----------------------------
print("Downloading the model from ArcGIS Online...")
model_item = gis.content.get(MODEL_ITEM_ID)
dlpk_path = model_item.download(save_path=".")

model_folder = os.path.splitext(dlpk_path)[0]
print(f"Model folder extracted: {model_folder}")

print("Loading model from extracted folder...")
model = load_model(model_folder)

print(f"Running prediction on image: {INPUT_IMAGE_PATH} ...")
prediction = model.predict(INPUT_IMAGE_PATH, confidence_score=True)

prediction.save(OUTPUT_IMAGE_PATH)
print(f"Output saved: {OUTPUT_IMAGE_PATH}")

print("\nDetected 'person' objects:")

detections = prediction._data["features"]
found_person = False

for obj in detections:
    label = obj["attributes"].get("ClassName", "").lower()
    if label == "person":
        found_person = True
        conf = obj["attributes"]["Confidence"]
        bounds = obj["geometry"]["rings"]
        print(f"- Confidence: {conf:.2f}, Bounds: {bounds}")

if not found_person:
    print("No persons detected.")

print("Detection complete.")
