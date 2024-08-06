import cv2
import numpy as np
from ultralytics import YOLO

# YOLO 모델 로드 (path를 정확히 지정하세요)
detect_model = YOLO(r'C:\Capstone\runs\detect\train3\weights\best.pt')

# 카메라 스트림 열기 (다른 카메라를 사용하기 위해 적절한 인덱스로 변경)
cap = cv2.VideoCapture(2)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 카메라 해상도 가져오기
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_center = (frame_width // 2, frame_height // 2)

# 컵 클래스의 ID를 설정 (모델에 따라 다를 수 있음)
CUP_CLASS_ID = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO 모델 감지
    results = detect_model(frame)

    largest_box = None
    largest_area = 0

    # 감지된 결과에서 컵만 필터링하여 가장 큰 바운딩 박스 찾기
    for box in results[0].boxes:
        # box 값 추출
        xmin, ymin, xmax, ymax = box.xyxy[0].cpu().numpy()
        confidence = box.conf[0].cpu().numpy()
        class_id = box.cls[0].cpu().numpy()

        if class_id == CUP_CLASS_ID and confidence >= 0.8:
            # 바운딩 박스의 면적 계산
            area = (xmax - xmin) * (ymax - ymin)
            if area > largest_area:
                largest_area = area
                largest_box = box

    if largest_box is not None:
        # 가장 큰 바운딩 박스의 중심 좌표 계산
        xmin, ymin, xmax, ymax = largest_box.xyxy[0].cpu().numpy()
        box_center_x = (xmin + xmax) / 2
        box_center_y = (ymin + ymax) / 2

        # 중앙 지점 간의 거리 계산
        delta_x = box_center_x - frame_center[0]
        delta_y = box_center_y - frame_center[1]

        # bounding box 그리기
        cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
        cv2.circle(frame, (int(box_center_x), int(box_center_y)), 5, (0, 0, 255), -1)
        cv2.circle(frame, frame_center, 5, (255, 0, 0), -1)

        # 거리 출력
        cv2.putText(frame, f"Delta X: {delta_x:.2f}, Delta Y: {delta_y:.2f}", (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        print(f"Delta X: {delta_x:.2f}, Delta Y: {delta_y:.2f}")

    # 결과 프레임 표시
    cv2.imshow('Cup Detection', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라 및 윈도우 정리
cap.release()
cv2.destroyAllWindows()
