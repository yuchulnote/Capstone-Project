import cv2
import numpy as np
from ultralytics import YOLO
import json
from pyModbusTCP.server import ModbusServer, DataBank
from time import sleep

# Modbus 서버 설정
local_host = '192.168.137.3'  # 올바른 로컬 IP 주소로 변경
server = ModbusServer(host=local_host, port=508, no_block=True)

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

# 테이블 네 모서리 점의 이미지 좌표 (픽셀 단위)
image_points = np.array([[369, 73], # 좌상단
                         [853, 73], # 우상단
                         [1036, 720], # 우하단
                         [165, 720]],dtype=np.float32)  # 좌하단

# YOLO 모델 로드 (path를 정확히 지정하세요)
detect_model = YOLO(r'C:\Capstone\runs\detect\train3\weights\best.pt')
classify_model = YOLO(r'C:\Capstone\runs\classify\cup_cls_3classes_resume\weights\best.pt')

# 프레임 인터벌 설정
frame_interval = 10
frame_count = 0

try:
    print('Start server')
    server.start()
    print('Server is online')

    # 카메라 스트림 열기
    cap = cv2.VideoCapture(3)
    
    # 카메라 해상도 가져오기
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if not cap.isOpened():
        print("Cannot open webcam")
        exit()
    
    send_idx = 0
    send_flag = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % frame_interval == 0:
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
                        color = (0, 0, 255)  # 빨간색
                        x = int((xmin + xmax) / 2)
                        y = int((ymin + ymax) / 2)
                        
                        print(f"Detected abnormal cup at ({x}, {y})")
                        
                        # 비정상적인 컵 좌표 저장
                        current_abnormal_cups.append((1, x, y))

                    cv2.putText(frame, f"Status: {status}", (int(xmin), int(ymin) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    cv2.putText(frame, f"Class: {class_name}", (int(xmin), int(ymin) - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    cv2.putText(frame, f"Confidence: {confidence:.2f}", (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    cv2.putText(frame, f"X: {x:.2f}, Y: {y:.2f}", (int(xmin), int(ymin) - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            try:
                server.data_bank.set_holding_registers(0, [len(current_abnormal_cups + current_normal_cups)])
            except Exception as e:
                print(f"Error updating Modbus server: {e}")

            # Modbus 서버에 비정상적인 컵 좌표 업데이트
            total_cups = current_abnormal_cups + current_normal_cups
            if send_flag != server.data_bank.get_holding_registers(4)[0]:
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
