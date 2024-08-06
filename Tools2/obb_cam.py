import cv2
from ultralytics import YOLO

# YOLOv8 OBB 모델 불러오기
model = YOLO(r'C:\Capstone\runs\obb\train8\weights\best.pt')

# 웹캠 열기
cap = cv2.VideoCapture(4)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # 웹캠에서 프레임 읽기
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Could not read frame.")
        break

    # YOLOv8 모델로 프레임에서 객체 탐지
    results = model(frame)

    # 결과가 None인지 확인
    if results:
        # 탐지 결과를 프레임에 그리기
        for r in results:
            if r.obb is not None:
                for obb in r.obb:
                    # OBB의 좌표와 클래스 가져오기
                    points = obb.xyxyxyxy.cpu().numpy()  # OBB 좌표
                    label = obb.cls.cpu().numpy()  # 클래스 라벨
                    confidence = obb.conf.cpu().numpy()  # 신뢰도

                    # 좌표 추출
                    p1, p2, p3, p4 = map(tuple, points.reshape(4, 2))
                    p1 = (int(p1[0]), int(p1[1]))
                    p2 = (int(p2[0]), int(p2[1]))
                    p3 = (int(p3[0]), int(p3[1]))
                    p4 = (int(p4[0]), int(p4[1]))

                    # 디버깅: 좌표와 레이블 출력
                    print(f"OBB: {p1}, {p2}, {p3}, {p4}, Label: {label}, Confidence: {confidence}")

                    # OBB 그리기
                    cv2.line(frame, p1, p2, (255, 0, 0), 2)
                    cv2.line(frame, p2, p3, (255, 0, 0), 2)
                    cv2.line(frame, p3, p4, (255, 0, 0), 2)
                    cv2.line(frame, p4, p1, (255, 0, 0), 2)
                    cv2.putText(frame, f"{int(label[0])}: {confidence[0]:.2f}", (p1[0], p1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # 프레임 출력
    cv2.imshow('YOLOv8 OBB Real-Time Detection', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 웹캠 릴리스 및 모든 창 닫기
cap.release()
cv2.destroyAllWindows()
