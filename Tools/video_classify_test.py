import cv2
from ultralytics import YOLO

# YOLO 모델 로드 (path를 정확히 지정하세요)
detect_model = YOLO(r'C:\Capstone\runs\detect\train3\weights\best.pt')
classify_model = YOLO(r'C:\Capstone\runs\classify\cup_cls_3classes_resume\weights\best.pt')

# 카메라 스트림 열기
cap = cv2.VideoCapture(3)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO 모델 감지
    results = detect_model(frame)

    # 결과 처리
    for box in results[0].boxes:
        # box 값 추출
        xmin, ymin, xmax, ymax = box.xyxy[0]
        confidence = box.conf[0]
        class_id = box.cls[0]

        # bounding box 그리기
        cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)

        # 바운딩 박스 이미지 잘라내기
        bbox_img = frame[int(ymin):int(ymax), int(xmin):int(xmax)]

        # 분류 모델에 바운딩 박스 이미지 입력
        class_results = classify_model(bbox_img)
        predictions = class_results[0].probs

        # 가장 높은 확률의 클래스 선택
        class_id = predictions.top1
        confidence = predictions.top1conf.item()

        # 분류된 클래스 이름 가져오기
        class_name = classify_model.names[class_id]

        # 상태 판단 및 텍스트 표시
        if class_name == "normal":
            status = "normal"
            color = (0, 255, 0)  # 녹색
        else:
            status = "abnormal"
            color = (0, 0, 255) # 빨간색
            
            # 비정상적인 컵의 중심 좌표 계산
            x = int((xmin + xmax) / 2)
            y = int((ymin + ymax) / 2)
            
            print(f"Detected abnormal cup at ({x}, {y})")

        cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 2)
        cv2.putText(frame, f"Status: {status}", (int(xmin), int(ymin) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"Class: {class_name}", (int(xmin), int(ymin) - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"Confidence: {confidence:.2f}", (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # 결과 프레임 표시
    cv2.imshow('Object Detection and Classification', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라 및 윈도우 정리
cap.release()
cv2.destroyAllWindows()


# import cv2
# from ultralytics import YOLO

# # YOLO 모델 로드 (path를 정확히 지정하세요)
# detect_model = YOLO(r'C:\Capstone\runs\detect\train3\weights\best.pt')
# classify_model = YOLO(r'C:\Capstone\runs\classify\cup_cls_3classes_resume\weights\best.pt')

# # 카메라 스트림 열기
# cap = cv2.VideoCapture(1)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # YOLO 모델 감지
#     results = detect_model(frame)

#     # 결과 처리
#     for box in results[0].boxes:
#         # box 값 추출
#         xmin, ymin, xmax, ymax = box.xyxy[0]
#         confidence = box.conf[0]
#         class_id = box.cls[0]

#         # 신뢰도가 0.9 이상인 경우에만 처리
#         if confidence >= 0.9:
#             # bounding box 그리기
#             cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)

#             # 바운딩 박스 이미지 잘라내기
#             bbox_img = frame[int(ymin):int(ymax), int(xmin):int(xmax)]

#             # 분류 모델에 바운딩 박스 이미지 입력
#             class_results = classify_model(bbox_img)
#             predictions = class_results[0].probs

#             # 가장 높은 확률의 클래스 선택
#             class_id = predictions.top1
#             confidence = predictions.top1conf.item()

#             # 분류된 클래스 이름 가져오기
#             class_name = classify_model.names[class_id]

#             # 상태 판단 및 텍스트 표시
#             if class_name == "normal":
#                 status = "normal"
#                 color = (0, 255, 0)  # 녹색
#             else:
#                 status = "abnormal"
#                 color = (0, 0, 255)  # 빨간색

#             cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 2)
#             cv2.putText(frame, f"Status: {status}", (int(xmin), int(ymin) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
#             cv2.putText(frame, f"Class: {class_name}", (int(xmin), int(ymin) - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
#             cv2.putText(frame, f"Confidence: {confidence:.2f}", (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#     # 결과 프레임 표시
#     cv2.imshow('Object Detection and Classification', frame)

#     # 'q' 키를 누르면 종료
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # 카메라 및 윈도우 정리
# cap.release()
# cv2.destroyAllWindows()
