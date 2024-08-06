import cv2
from ultralytics import YOLO

# YOLO 모델 로드 (path를 정확히 지정하세요)
model = YOLO(r'C:\Capstone\runs\detect\train7\weights\best.pt')

# 카메라 스트림 열기
cap = cv2.VideoCapture(2)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO 모델 감지
    results = model(frame)

    # 결과 처리
    for box in results[0].boxes:
        # box 값 추출
        xmin, ymin, xmax, ymax = box.xyxy[0]
        confidence = box.conf[0]
        class_id = box.cls[0]

        # bounding box 그리기
        cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)

        # bounding box의 가로 및 세로 길이 계산
        width = xmax - xmin
        height = ymax - ymin

        # 상태 판단 및 텍스트 표시
        if width > height * 0.9:  # 가로가 세로보다 1.2배 이상 크면
            status = "Overturned"
            color = (0, 0, 255)  # 빨간색
        else:
            status = "Normal"
            color = (0, 255, 0)  # 녹색

        cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 2)
        cv2.putText(frame, f"Status: {status}", (int(xmin), int(ymin) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"width: {int(width)}, height: {int(height)}", (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # 결과 프레임 표시
    cv2.imshow('Cup Detection', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라 및 윈도우 정리
cap.release()
cv2.destroyAllWindows()
