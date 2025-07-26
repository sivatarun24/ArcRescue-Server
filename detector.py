from ultralytics import YOLO

model = YOLO("yolov8x.pt")  # other models yolov8s.pt, yolov8n.pt, yolov8x.pt etc.

def detect_persons(frame):
    results = model(frame)[0]
    persons = []

    for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
        if int(cls.item()) == 0:  # class 0 = person
            x1, y1, x2, y2 = map(int, box)
            persons.append((x1, y1, x2, y2, float(conf)))

    return persons
