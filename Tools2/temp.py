import cv2
import numpy as np
from ultralytics import YOLO
from pyModbusTCP.server import ModbusServer, DataBank
from time import sleep

# YOLO 모델 로드 (path를 정확히 지정하세요)
detect_model = YOLO(r'C:\2019741012\4_1\capstone\RGB\Capstone\detection_best.pt')
classify_model = YOLO(r'C:\2019741012\4_1\capstone\RGB\Capstone\classification_best.pt')

# 카메라 캘리브레이션 파라미터
camera_matrix = np.array([[2199.120378, 0, 1920.000000],
                          [0, 2199.120378, 1080.000000],
                          [0, 0, 1]])
dist_coeffs = np.array([0.129775, -0.364103, -0.001728, 0.011107])

def undistort_image(image):
    h, w = image.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))
    undistorted_img = cv2.undistort(image, camera_matrix, dist_coeffs, None, new_camera_matrix)
    x, y, w, h = roi
    undistorted_img = undistorted_img[y:y+h, x:x+w]
    return undistorted_img

# def update_modbus_registers(x, y):
#     server.data_bank.set_holding_registers(0, [x, y])

# Modbus 서버 설정
local_host = '192.168.137.1'  # 올바른 로컬 IP 주소로 변경
server = ModbusServer(host=local_host, port=504, no_block=True)

abnormal_cups = []  # 비정상적인 컵 좌표 목록

try:
    print('Start server')
    server.start()
    print('Server is online')

    # 카메라 스트림 열기
    cap = cv2.VideoCapture(3)
    if not cap.isOpened():
        print("Cannot open webcam")
        exit()
    
    send_idx = 0
    send_flag = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # undistorted_frame = undistort_image(frame)

        # YOLO 모델 감지
        results = detect_model(frame)

        # 결과 처리
        current_abnormal_cups = []
        current_normal_cups = []
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
            if class_name == "abnormal":
                status = "abnormal"
                color = (0, 0, 255)  # 빨간색
                
                # 비정상적인 컵의 중심 좌표 계산
                x = int((xmin + xmax) / 2)
                y = int((ymin + ymax) / 2)
                
                print(f"Detected abnormal cup at ({x}, {y})")
                
                # 비정상적인 컵 좌표 저장
                current_abnormal_cups.append((1, x, y))
                
            else:
                status = "Normal"
                color = (0, 255, 0)  # 녹색
                x = int((xmin + xmax) / 2)
                y = int((ymin + ymax) / 2)
                
                print(f"Detected normal cup at ({x}, {y})")
                
                # 정상적인 컵 좌표 저장
                current_normal_cups.append((0, x, y))

            cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 2)
            cv2.putText(frame, f"Status: {status}", (int(xmin), int(ymin) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(frame, f"Confidence: {confidence:.2f}", (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 비정상적인 컵 인덱스와 위치값을 화면에 표시
        for idx, (i, x, y) in enumerate(current_abnormal_cups):
            color = (0, 165, 255) if idx == 0 else (0, 0, 255)  # 첫 번째 컵은 주황색, 나머지는 빨간색
            cv2.putText(frame, f"Abnormal cup {idx}: ({x}, {y})", (10, 30 + idx * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.circle(frame, (x, y), 5, color, -1)

        # Modbus 서버에 현재 비정상적인 컵 개수 업데이트
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

        sleep(0.1)  # 모드버스 서버 업데이트 주기

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
