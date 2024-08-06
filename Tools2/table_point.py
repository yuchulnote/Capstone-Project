import cv2
import numpy as np
from ultralytics import YOLO
import json
from pyModbusTCP.server import ModbusServer, DataBank
from time import sleep

# Modbus 서버 설정
local_host = '192.168.137.3'  # 올바른 로컬 IP 주소로 변경
server = ModbusServer(host=local_host, port=504, no_block=True)

abnormal_cups = []  # 비정상적인 컵 좌표 목록

# 전역 변수
points_file = 'points.json'

def load_points(file_path):
    try:
        with open(file_path, 'r') as file:
            points = json.load(file)
        return points
    except FileNotFoundError:
        return None

def apply_perspective_transform(points, width, height, inv=False):
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])

    if inv:
        matrix = cv2.getPerspectiveTransform(pts2, pts1)
    else:
        matrix = cv2.getPerspectiveTransform(pts1, pts2)

    return matrix

# 카메라 캘리브레이션 결과
camera_matrix = np.array([[1000.403797, 0, 960.000000],
                          [0, 1000.403797, 540.000000],
                          [0, 0, 1]])

dist_coeffs = np.array([0.168572, -0.088752, -0.057920, 0.004274])

# 테이블 크기 (단위: cm)
table_width = 100  # 가로 100cm
table_height = 150  # 세로 150cm

# 테이블 네 모서리 점의 이미지 좌표 (픽셀 단위)
image_points = np.array([[369, 73], # 좌상단
                         [853, 73], # 우상단
                         [1036, 720], # 우하단
                         [165, 720]],dtype=np.float32)  # 좌하단

# 실제 테이블 네 모서리 점의 실제 세계 좌표 (단위: cm)
object_points = np.array([[0, 0, 0],
                          [table_width, 0, 0],
                          [table_width, table_height, 0],
                          [0, table_height, 0]], dtype=np.float32)

# 카메라 캘리브레이션 결과로 투영 변환 행렬 계산
retval, rvec, tvec = cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)
rotation_matrix, _ = cv2.Rodrigues(rvec)
extrinsics = np.hstack((rotation_matrix, tvec))

def world_to_image(world_point):
    world_point_homogeneous = np.append(world_point, 1)
    image_point = np.dot(camera_matrix, np.dot(extrinsics, world_point_homogeneous))
    image_point = image_point[:2] / image_point[2]
    return image_point

# YOLO 모델 로드 (path를 정확히 지정하세요)
detect_model = YOLO(r'C:\Capstone\runs\detect\train3\weights\best.pt')
classify_model = YOLO(r'C:\Capstone\runs\classify\cup_cls_3classes_resume\weights\best.pt')

# 카메라 스트림 열기
cap = cv2.VideoCapture(2)

# 카메라 해상도 가져오기
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 투영 변환 행렬 계산
perspective_matrix = apply_perspective_transform(image_points, frame_width, frame_height)
inverse_perspective_matrix = apply_perspective_transform(image_points, frame_width, frame_height, inv=True)

try:
    print('Start server')
    server.start()
    print('Server is online')

    # 카메라 스트림 열기
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("Cannot open webcam")
        exit()
    
    send_idx = 0
    send_flag = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 이미지 보정 (왜곡 제거)
        # frame_undistorted = cv2.undistort(frame, camera_matrix, dist_coeffs)

        # 네 모서리 점 시각적으로 표시
        for point in image_points:
            cv2.circle(frame, tuple(point.astype(int)), 10, (0, 0, 255), -1)

        # YOLO 모델 감지
        results = detect_model(frame)
        
        current_abnormal_cups = []
        current_normal_cups = []

        # 결과 처리
        for box in results[0].boxes:
            # box 값 추출
            xmin, ymin, xmax, ymax = box.xyxy[0].cpu().numpy()
            confidence = box.conf[0].cpu().numpy()
            class_id = box.cls[0].cpu().numpy()

            # 신뢰도가 0.9 이상인 경우에만 처리
            if confidence >= 0.9:
                # bounding box 중심 좌표 계산
                center_x = (xmin + xmax) / 2
                center_y = (ymin + ymax) / 2

                # 중심 좌표를 실제 세계 좌표로 변환
                points_transformed = np.array([[[center_x, center_y]]], dtype=np.float32)
                points_original = cv2.perspectiveTransform(points_transformed, inverse_perspective_matrix)
                original_x, original_y = points_original[0][0]

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

                if class_name == "normal":
                    status = "normal"
                    color = (0, 255, 0)  # 녹색
                    
                    # 비정상적인 컵의 중심 좌표 계산
                    x = int((xmin + xmax) / 2)
                    y = int((ymin + ymax) / 2)
                    
                    print(f"Detected normal cup at ({x}, {y})")
                    
                    # 정상적인 컵 좌표 저장
                    current_normal_cups.append((0, x, y))
                    
                else:
                    status = "abnormal"
                    color = (0, 0, 255)  # 녹색
                    x = int((xmin + xmax) / 2)
                    y = int((ymin + ymax) / 2)
                    
                    print(f"Detected abnormal cup at ({x}, {y})")
                    
                    # 비정상적인 컵 좌표 저장
                    current_abnormal_cups.append((1, x, y))

                cv2.putText(frame, f"Status: {status}", (int(xmin), int(ymin) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, f"Class: {class_name}", (int(xmin), int(ymin) - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, f"Confidence: {confidence:.2f}", (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, f"X: {original_x:.2f}, Y: {original_y:.2f}", (int(xmin), int(ymin) - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        
        
        try:
            server.data_bank.set_holding_registers(0, [len(current_abnormal_cups + current_normal_cups)])
        except Exception as e:
            print(f"Error updating Modbus server: {e}")

        # Modbus 서버에 비정상적인 컵 좌표 업데이트
        total_cups = current_abnormal_cups + current_normal_cups
        if send_flag != server.data_bank.get_holding_registers(4)[0]:
            # try:
            server.data_bank.set_holding_registers(1, list(total_cups[0]))
            
            server.data_bank.set_holding_registers(4, [0])
            send_flag = server.data_bank.get_holding_registers(4)[0]

        # 결과 프레임 표시
        cv2.imshow('Object Detection and Classification', frame)
        
        
        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print('Error:', e)

finally:
    try:
        cap.release()
        cv2.destroyAllWindows()
    except NameError:
        pass
    server.stop()
    print('Server is offline')