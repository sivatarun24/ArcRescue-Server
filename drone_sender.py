import socket
import json
import time
import cv2
import pandas as pd
from static_data import DATA_SOURCES
from flightPath import add_flight_path_to_layer

def run_mission_by_name(mission_id: str):
    # ==== CONFIGURATION ====
    target_ip = "127.0.0.1"
    target_port = 9999
    default_resolution = (1920, 1080)
    frames_per_second = 30
    telemetries_per_second = 10
    send_rate = 3
    interval = telemetries_per_second // send_rate

    # ==== GET MISSION CONFIG ====
    mission = DATA_SOURCES.get(mission_id)
    if not mission:
        print(f"[ERROR] Mission '{mission_id}' not found in static_data.")
        return

    print(f"\n[INFO] Starting mission: {mission_id}")
    csv_path = mission["data_csv"]
    video_path = mission["video"]
    feature_url = mission["url"]
    flight_url = mission["drone_url"]

    print(f" - CSV:   {csv_path}")
    print(f" - Video: {video_path}")

    # ==== LOAD CSV ====
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[ERROR] Failed to load CSV: {e}")
        return

    # Optional: Upload flight path to map (commented out)
    coordinates_latlon = list(zip(df["SensorLatitude"], df["SensorLongitude"]))
    # add_flight_path_to_layer(flight_url, coordinates_latlon, [0, 0, 255, 255])  # Red color line

    sampled_df = df.iloc[::interval].reset_index(drop=True)

    # ==== LOAD VIDEO ====
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Could not open video: {video_path}")
        return

    # ==== SETUP SOCKET ====
    sock = socket.socket()
    try:
        sock.connect((target_ip, target_port))
    except Exception as e:
        print(f"[ERROR] Socket connection failed: {e}")
        cap.release()
        return

    frame_count = 0
    frame_index = 0

    # ==== STREAM FRAMES ====
    while cap.isOpened() and frame_index < len(sampled_df):
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % (frames_per_second // send_rate) == 0:
            telemetry = sampled_df.iloc[frame_index].to_dict()

            width = int(telemetry.get("width", default_resolution[0]))
            height = int(telemetry.get("height", default_resolution[1]))
            resized_frame = cv2.resize(frame, (width, height))

            _, buffer = cv2.imencode(".jpg", resized_frame)
            hex_image = buffer.tobytes().hex()

            msg = {
                "type": "frame",
                "frame_id": frame_index,
                "image": hex_image,
                "metadata": telemetry,
                "url": feature_url,
                "flight_url": flight_url
            }

            try:
                sock.sendall((json.dumps(msg) + '\n').encode())
                print(f"[INFO] Sent frame {frame_index} from {mission_id}")
            except Exception as e:
                print(f"[ERROR] Failed to send frame: {e}")
                break

            frame_index += 1
            time.sleep(1.0 / send_rate)

        frame_count += 1

    cap.release()
    sock.close()
    print(f"[INFO] Finished mission: {mission_id}")

def run_multiple_missions(mission_ids: list[str]):
    for mission_id in mission_ids:
        run_mission_by_name(mission_id)

# # === Example Usage ===
# run_mission_by_name("mission_gamma")

# # === Example Usage ===
# if __name__ == "__main__":
#     mission_list = ["mission_alpha", "mission_gamma", "mission_alpha", "mission_beta"]  # Replace with your own mission names
#     run_multiple_missions(mission_list)