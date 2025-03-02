import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from tracker import *
import cvzone

model = YOLO('yolov8s.pt')
def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        colorsBGR = [x, y]
        print(colorsBGR)

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

cap=cv2.VideoCapture('office_video.mp4')

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")
# print(class_list)

count = 0
tracker = Tracker()

# polygon shape coordinates:
# 1      #4
# 2      #3

# 1      #2          #3      #4

# office : area1-red-exit, area2-green-enter
area1= [(460,200),(407,260),(663,289),(656,225)]
area2= [(347,254),(323,273),(657,321),(660,300)]

people_enter = {}
counter1 = []

people_exit = {}
counter2 = []
while True:
    ret, frame = cap.read()
    if not ret:
        break
    count += 1
    if count % 3 != 0:
        continue
    frame = cv2.resize(frame, (1020, 500)) #

    results = model.predict(frame)
    a = results[0].boxes.boxes
    px = pd.DataFrame(a).astype("float")

    list = [] #bounding box coordinates of detected persons
    for index, row in px.iterrows():
        #        print(row)
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])
        c = class_list[d]
        if 'person' in c:
            list.append([x1, y1, x2, y2])
    bbox_id = tracker.update(list)
    for bbox in bbox_id:
        x3, y3, x4, y4, id = bbox

        results = cv2.pointPolygonTest(np.array(area1, np.int32), ((x4, y4)), False)
        if results >= 0:
            people_exit[id] = (x4, y4)

        if id in people_exit:
            results1 = cv2.pointPolygonTest(np.array(area2, np.int32), ((x4, y4)), False)
            if results1 >= 0:
                cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 255), 1)
                cv2.circle(frame, (x4, y4), 4, (255, 0, 0), -1)
                cvzone.putTextRect(frame, f'{id}', (x3, y3), 1, 2)
                if counter2.count(id) == 0:  # For not counting same id again
                    counter2.append(id)

        # Entering Counter
        results2 = cv2.pointPolygonTest(np.array(area2, np.int32), ((x4, y4)), False)
        if results2 >= 0:
            people_enter[id] = (x4, y4)

        if id in people_enter:
            results3 = cv2.pointPolygonTest(np.array(area1, np.int32), ((x4, y4)), False)
            if results3 >= 0:
                cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 255), 1)
                cv2.circle(frame, (x4, y4), 4, (255, 0, 0), -1)
                cvzone.putTextRect(frame, f'{id}', (x3, y3), 1, 2)
                if counter1.count(id) == 0:  # For not counting same id again
                    counter1.append(id)

    cv2.polylines(frame, [np.array(area1, np.int32)], True, (0, 0, 255), 1)
    cv2.polylines(frame, [np.array(area2, np.int32)], True, (0, 255, 0), 1)
    er = (len(counter1))
    et = (len(counter2))
    cvzone.putTextRect(frame, f'People Enter: {er}', (50, 50), 3, 2)
    cvzone.putTextRect(frame, f'People Exit: {et}', (50, 100), 3, 2)

    cv2.imshow("RGB", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()