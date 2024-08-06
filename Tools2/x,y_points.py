import cv2
import numpy as np
from ultralytics import YOLO

# Perspective Transform 불러오기
perspective_transform = np.load('perspective_transform.npy')

# 이미지 좌표를 테이블 좌표로 변환하는 함수
def image_to_table_coords(perspective_transform, image_point):
    points = np.array([[image_point]], dtype=np.float32)
    table_point = cv2.perspectiveTransform(points, perspective_transform)
    return table_point[0][0]

# YOLO 모델 로드
detect_model = YOLO(r'C:\Capstone\runs\detect\train_before\weights\detection_best.pt')
classify_model = YOLO(r'C:\Capstone\runs\classify\cup_cls3\weights\classification_best.pt')

# 카메라 스트림 열기
cap = cv2.VideoCapture(2)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO 모델 감지
    results = detect_model(frame)
    for box in results[0].boxes:
        xmin, ymin, xmax, ymax = box.xyxy[0]
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2

        # 이미지 좌표를 테이블 좌표로 변환
        image_point = np.array([center_x, center_y], dtype=np.float32)
        table_coords = image_to_table_coords(perspective_transform, image_point)

        # 결과 출력
        table_x, table_y = table_coords
        print(f"테이블 좌표계에서의 위치: ({table_x:.2f} cm, {table_y:.2f} cm)")

        cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
        cv2.putText(frame, f"Table X: {table_x:.2f} cm", (int(xmin), int(ymin) - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(frame, f"Table Y: {table_y:.2f} cm", (int(xmin), int(ymin) - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        # cv2.putText(frame, f"Class: {class_name}", (int(xmin), int(ymin) - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # 바운딩 박스 이미지 잘라내기
        bbox_img = frame[int(ymin):int(ymax), int(xmin):int(xmax)]
        class_results = classify_model(bbox_img)
        predictions = class_results[0].probs
        class_id = predictions.top1
        confidence = predictions.top1conf.item()
        class_name = classify_model.names[class_id]

        if class_name == "abnormal":
            status = "abnormal"
            color = (0, 0, 255)
        else:
            status = "Normal"
            color = (0, 255, 0)

        cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 2)
        cv2.putText(frame, f"Status: {status}", (int(xmin), int(ymin) - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"Class: {class_name}", (int(xmin), int(ymin) - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"Confidence: {confidence:.2f}", (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow('Object Detection and Classification', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
