import cv2
import numpy as np
import json
from ultralytics import YOLO

# 캘리브레이션 데이터 및 외부 파라미터 불러오기
def load_calibration_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    camera_matrix = np.array(data['camera_matrix'], dtype=np.float32)
    dist_coeffs = np.array(data['dist_coeffs'], dtype=np.float32)
    return camera_matrix, dist_coeffs

def load_external_params():
    rvecs = np.load('rvecs.npy')
    tvecs = np.load('tvecs.npy')
    return rvecs, tvecs

# 이미지 좌표를 월드 좌표로 변환하는 함수
def image_to_world_coords(camera_matrix, dist_coeffs, rvecs, tvecs, image_point):
    # 이미지 포인트를 왜곡 보정
    image_point_undistorted = cv2.undistortPoints(np.array([image_point], dtype=np.float32), camera_matrix, dist_coeffs)
    
    # 회전 벡터를 회전 행렬로 변환
    rotation_matrix, _ = cv2.Rodrigues(rvecs)
    
    # 3x4 행렬을 4x4 동차 행렬로 확장
    transform_matrix = np.hstack((rotation_matrix, tvecs))
    transform_matrix = np.vstack((transform_matrix, [0, 0, 0, 1]))
    
    # 왜곡 보정된 이미지 포인트를 동차 좌표계로 변환
    image_point_undistorted_homogeneous = np.array([image_point_undistorted[0][0][0], image_point_undistorted[0][0][1], 1, 1])
    
    # 월드 좌표 계산
    world_coords = np.dot(np.linalg.inv(transform_matrix), image_point_undistorted_homogeneous)
    return world_coords[:3]

# 캘리브레이션 데이터 및 외부 파라미터 불러오기
camera_matrix, dist_coeffs = load_calibration_data('calibration_data.json')
rvecs, tvecs = load_external_params()

# YOLO 모델 로드
detect_model = YOLO(r'C:\Capstone\runs\detect\train_before\weights\detection_best.pt')
classify_model = YOLO(r'C:\Capstone\runs\classify\cup_cls3\weights\classification_best.pt')

# 테이블의 크기 (단위: cm)
table_width = 100
table_height = 150

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

        # 이미지 좌표를 월드 좌표로 변환
        image_point = np.array([center_x, center_y], dtype=np.float32)
        world_coords = image_to_world_coords(camera_matrix, dist_coeffs, rvecs, tvecs, image_point)

        # 월드 좌표를 테이블 좌표계로 변환
        table_x = (world_coords[0] - 0) / table_width * 100  # x좌표를 0에서 100으로 변환
        table_y = (world_coords[1] - 0) / table_height * 150  # y좌표를 0에서 150으로 변환

        # 결과 출력
        print(f"테이블 좌표계에서의 위치: ({table_x:.2f} cm, {table_y:.2f} cm)")

        cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
        cv2.putText(frame, f"Table X: {table_x:.2f} cm", (int(xmin), int(ymin) - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(frame, f"Table Y: {table_y:.2f} cm", (int(xmin), int(ymin) - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

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
