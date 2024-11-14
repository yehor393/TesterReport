import cv2
from ultralytics import YOLO

# load models
coco_model = YOLO('yolo8n.pt')
model_serial_detector = YOLO('model_serial_detector.pt')

# Read frames
cap = cv2.VideoCapture('./video.mp4')

frame_num = -1
ret = True
while ret:
    frame_num += 1
    ret, frame = cap.read()
    if ret and frame_num < 10:
        # detect dataplate
        detections = coco_model(frame)[0]
        print(detections)