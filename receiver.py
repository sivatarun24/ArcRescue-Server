import socket
import json
import cv2
import numpy as np
import os
from io import BytesIO
from detector import detect_persons
from multiplexer import project_pixel_to_ground
from pointsToFeatureMap import push_person_location

os.makedirs("output", exist_ok=True)

def handle_connection(conn, addr):
    print(f"Connected by {addr}")
    buffer = ""

    try:
        while True:
            data = conn.recv(65536)
            if not data:
                print(f"Connection closed by {addr}")
                break

            try:
                buffer += data.decode(errors="ignore")
            except Exception as e:
                print("Buffer decode error:", e)
                buffer = ""
                continue

            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)

                try:
                    msg = json.loads(line)
                    print(f"Received message: {msg}")

                    if msg.get("type") != "frame" or "image" not in msg or "metadata" not in msg:
                        print("Invalid message format, skipping...")
                        continue

                    # Decode image
                    try:
                        frame_bytes = bytes.fromhex(msg["image"])
                        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
                        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                        if frame is None:
                            raise ValueError("Decoded frame is None")
                    except Exception as e:
                        print("Image decode error:", e)
                        continue

                    # Person detection
                    try:
                        boxes = detect_persons(frame)
                        if not boxes:
                            print("No persons detected in this frame.")
                            continue
                    except Exception as e:
                        print("Detection error:", e)
                        continue

                    metadata = msg["metadata"]
                    frame_id = msg.get("frame_id", 0)
                    image_height, image_width = frame.shape[:2]

                    # Draw and push detections
                    for i, (x1, y1, x2, y2, conf) in enumerate(boxes):
                        # Use center of the bounding box
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)

                        try:
                            lon, lat = project_pixel_to_ground(
                                (cx, cy),
                                image_width=image_width,
                                image_height=image_height,
                                sensor_lat=metadata["SensorLatitude"],
                                sensor_lon=metadata["SensorLongitude"],
                                sensor_relative_altitude=metadata["SensorTrueAltitude"],
                                takeoff_altitude=metadata["TakeoffLocationAltitude"],
                                sensor_relative_elevation_angle=metadata["SensorRelativeElevationAngle"],
                                heading=metadata["PlatformHeadingAngle"],
                                fov_horizontal=metadata["SensorHorizontalFieldOfView"],
                                fov_vertical=metadata["SensorVerticalFieldOfView"] * (image_height / image_width)
                            )
                        except Exception as e:
                            print(f"GPS projection error: {e}")
                            lon, lat = None, None

                        # Draw bounding box and label
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label = f"{conf * 100:.1f}%"
                        cv2.putText(frame, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

                        if lat and lon:
                            print(f"Person {i+1}: Confidence {conf*100:.2f}% → GPS: ({lat:.6f}, {lon:.6f})")

                            # Encode frame in memory
                            _, buffer = cv2.imencode('.jpg', frame)
                            image_buffer = BytesIO(buffer.tobytes())

                            # Push to ArcGIS Feature Layer
                            push_person_location(lat, lon, confidence=conf, image_data=image_buffer)

                    # Save frame locally
                    cv2.imwrite(f"output/frame_{frame_id}.jpg", frame)

                    # Show live
                    cv2.imshow("Drone Frame", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Receiver manually interrupted.")
                        return

                except json.JSONDecodeError:
                    print("Invalid JSON message, skipping...")
                except Exception as e:
                    print("Unexpected error:", e)

    finally:
        conn.close()
        print(f"Connection from {addr} closed.")
        cv2.destroyAllWindows()

def run_receiver():
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 9999))
    sock.listen(5)
    print("Receiver is listening on port 9999...")

    try:
        while True:
            conn, addr = sock.accept()
            handle_connection(conn, addr)

    except KeyboardInterrupt:
        print("\nReceiver shut down manually.")
    finally:
        sock.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Starting receiver...")
    run_receiver()
