# import socket
# import json
# import time
# import os
# import cv2
# import pandas as pd
# import re

# # ==== CONFIGURATION ====
# data_folder = "data"
# video_folder = "videos"
# target_ip = "120.0.0.1"
# target_port = 9999
# output_resolution = (640, 384)
# frames_per_second = 30
# telemetries_per_second = 10
# send_rate = 3
# interval = telemetries_per_second // send_rate  # = 3

# # ==== HELPERS ====
# def extract_id(filename):
#     match = re.search(r'\d+', filename)
#     return match.group() if match else None

# # ==== PAIR CSV AND VIDEO FILES ====
# csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
# video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]

# # Build mapping: {id: (csv_path, video_path)}
# file_pairs = {}
# for csv in csv_files:
#     file_id = extract_id(csv)
#     if not file_id:
#         continue
#     for video in video_files:
#         if extract_id(video) == file_id:
#             file_pairs[file_id] = (
#                 os.path.join(data_folder, csv),
#                 os.path.join(video_folder, video)
#             )

# # ==== MAIN LOOP ====
# for file_id, (csv_path, video_path) in file_pairs.items():
#     print(f"\nProcessing Pair: CSV={csv_path}, Video={video_path}")

#     # Load and downsample telemetry
#     df = pd.read_csv(csv_path)
#     sampled_df = df.iloc[::interval].reset_index(drop=True)

#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         print(f"Failed to open video: {video_path}")
#         continue

#     sock = socket.socket()
#     sock.connect((target_ip, target_port))

#     frame_count = 0
#     frame_index = 0

#     while cap.isOpened() and frame_index < len(sampled_df):
#         ret, frame = cap.read()
#         if not ret:
#             break

#         if frame_count % (frames_per_second // send_rate) == 0:
#             telemetry = sampled_df.iloc[frame_index].to_dict()

#             width = int(telemetry.get("width", output_resolution[0]))
#             height = int(telemetry.get("height", output_resolution[1]))
#             resized_frame = cv2.resize(frame, (width, height))

#             _, buffer = cv2.imencode(".jpg", resized_frame)
#             hex_image = buffer.tobytes().hex()

#             msg = {
#                 "type": "frame",
#                 "frame_id": frame_index,
#                 "image": hex_image,
#                 "metadata": {
#                     "latitude": telemetry["latitude"],
#                     "longitude": telemetry["longitude"],
#                     "altitude": telemetry["altitude"],
#                     "yaw": telemetry["yaw"],
#                     "pitch": telemetry["pitch"],
#                     "roll": telemetry["roll"],
#                     "fov": telemetry["fov"],
#                     "resolution": [height, width]
#                 }
#             }

#             sock.sendall((json.dumps(msg) + '\n').encode())
#             print(f"Sent frame {frame_index} from {video_path}")
#             frame_index += 1
#             time.sleep(1.0 / send_rate)

#         frame_count += 1

#     cap.release()
#     sock.close()
#     print(f"Finished sending data for {csv_path}")


import socket
import json
import time
import os
import cv2
import pandas as pd
import re

# ==== CONFIGURATION ====
data_folder = "data"
video_folder = "videos"
target_ip = "127.0.0.1"
target_port = 9999
default_resolution = (1920, 1080) # 1920, 1080
frames_per_second = 30
telemetries_per_second = 10
send_rate = 3
interval = telemetries_per_second // send_rate

def extract_id(filename):
    match = re.search(r'\d+', filename)
    return match.group() if match else None

# ==== PAIR FILES ====
csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
video_files = [f for f in os.listdir(video_folder) if f.endswith(".MP4")]

print(f"Found {len(csv_files)} CSV files and {len(video_files)} video files.")

file_pairs = {}
for csv in csv_files:
    file_id = extract_id(csv)
    if not file_id:
        continue
    for video in video_files:
        if extract_id(video) == file_id:
            file_pairs[file_id] = (
                os.path.join(data_folder, csv),
                os.path.join(video_folder, video)
            )

# ==== SEND LOOP ====
for file_id, (csv_path, video_path) in file_pairs.items():
    print(f"\nProcessing: CSV={csv_path}, Video={video_path}")

    df = pd.read_csv(csv_path)
    sampled_df = df.iloc[::interval].reset_index(drop=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Could not open video: {video_path}")
        continue

    sock = socket.socket()
    sock.connect((target_ip, target_port))

    frame_count = 0
    frame_index = 0

    while cap.isOpened() and frame_index < len(sampled_df):
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % (frames_per_second // send_rate) == 0:
            telemetry = sampled_df.iloc[frame_index].to_dict()

            # Dynamically check for resolution
            width = int(telemetry.get("width", default_resolution[0]))
            height = int(telemetry.get("height", default_resolution[1]))
            resized_frame = cv2.resize(frame, (width, height))

            _, buffer = cv2.imencode(".jpg", resized_frame)
            hex_image = buffer.tobytes().hex()

            msg = {
                "type": "frame",
                "frame_id": frame_index,
                "image": hex_image,
                "metadata": telemetry  # use entire row as metadata
            }

            sock.sendall((json.dumps(msg) + '\n').encode())
            print(f"Sent frame {frame_index}")
            frame_index += 1
            time.sleep(1.0 / send_rate)

        frame_count += 1

    cap.release()
    sock.close()
    print(f"Finished sending for {file_id}")

