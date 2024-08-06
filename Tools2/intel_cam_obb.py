import cv2
import numpy as np
from ultralytics import YOLO

# YOLO 모델 로드 (path를 정확히 지정하세요)
model = YOLO(r'C:\Capstone\runs\obb\train8\weights\best.pt')

# 카메라 스트림 열기 (다른 카메라를 사용하기 위해 적절한 인덱스로 변경)
cap = cv2.VideoCapture(2)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 카메라 해상도 가져오기
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_center = (frame_width // 2, frame_height // 2)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO 모델 감지
    results = model(frame)

    largest_box = None
    largest_area = 0

    if results:
        for r in results:
            if hasattr(r, 'obb') and r.obb is not None:
                for obb in r.obb:
                    # OBB 값 추출
                    points = obb.xyxyxyxy.cpu().numpy().reshape(4, 2)
                    confidence = obb.conf.cpu().numpy()
                    class_id = obb.cls.cpu().numpy()

                    if confidence >= 0.8:  # 클래스 아이디를 확인하는 조건 추가 가능
                        # 바운딩 박스의 면적 계산
                        x_coords = points[:, 0]
                        y_coords = points[:, 1]
                        area = 0.5 * np.abs(np.dot(x_coords, np.roll(y_coords, 1)) - np.dot(y_coords, np.roll(x_coords, 1)))

                        if area > largest_area:
                            largest_area = area
                            largest_box = obb

    if largest_box is not None:
        # 가장 큰 OBB의 중심 좌표 계산
        points = largest_box.xyxyxyxy.cpu().numpy().reshape(4, 2)
        box_center_x = np.mean(points[:, 0])
        box_center_y = np.mean(points[:, 1])

        # 중앙 지점 간의 거리 계산
        delta_x = box_center_x - frame_center[0]
        delta_y = box_center_y - frame_center[1]

        # OBB 그리기
        for i in range(4):
            pt1 = (int(points[i][0]), int(points[i][1]))
            pt2 = (int(points[(i + 1) % 4][0]), int(points[(i + 1) % 4][1]))
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

        cv2.circle(frame, (int(box_center_x), int(box_center_y)), 5, (0, 0, 255), -1)
        cv2.circle(frame, frame_center, 5, (255, 0, 0), -1)

        # 거리 출력
        cv2.putText(frame, f"Delta X: {delta_x:.2f}, Delta Y: {delta_y:.2f}", (int(box_center_x), int(box_center_y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        print(f"Delta X: {delta_x:.2f}, Delta Y: {delta_y:.2f}")

    # 결과 프레임 표시
    cv2.imshow('YOLOv8 OBB Real-Time Detection', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라 및 윈도우 정리
cap.release()
cv2.destroyAllWindows()
