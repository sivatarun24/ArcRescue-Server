import socket
import json
import cv2
import numpy as np
import os
from detector import detect_persons
# from coordinate_mapper import map_to_coordinates
# from push_location import push_person_location

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

            buffer += data.decode(errors="ignore")

            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)

                try:
                    msg = json.loads(line)

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
                    except Exception as e:
                        print("Detection error:", e)
                        continue

                    # Coordinate mapping
                    try:
                        coords = map_to_coordinates([box[:4] for box in boxes], msg["metadata"])
                    except Exception as e:
                        print("Coordinate mapping error:", e)
                        coords = [None] * len(boxes)

                    # Save full frame
                    frame_id = msg.get("frame_id", 0)  # ✅ Moved up

                    # Draw detections
                    for i, (x1, y1, x2, y2, conf) in enumerate(boxes):
                        point = coords[i]
                        lat = point.latitude
                        lon = point.longitude

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                        label = f"{conf * 100:.1f}%"
                        cv2.putText(frame, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

                        # Print to console
                        print(f"Person {i+1}:")
                        print(f"  Confidence: {conf * 100:.2f}%")
                        print(f"  GPS: ({lat:.6f}, {lon:.6f})")

                        # Push to ArcGIS with frame path
                        image_path = f"output/frame_{frame_id}.jpg"
                        push_person_location(lat, lon, image_path=image_path, name=f"Person {i+1}", status="Detected")


                    # Save full frame
                    frame_id = msg.get("frame_id", 0)
                    cv2.imwrite(f"output/frame_{frame_id}.jpg", frame)

                    # Display
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

# Main server loop — accepts new clients indefinitely
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
