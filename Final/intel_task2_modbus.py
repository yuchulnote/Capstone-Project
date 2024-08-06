import cv2
import numpy as np
from ultralytics import YOLO
from pyModbusTCP.server import ModbusServer, DataBank

# Modbus 서버 설정
local_host = '192.168.137.3'  # 올바른 로컬 IP 주소로 변경
server = ModbusServer(host=local_host, port=509, no_block=True)

try:
    print('Start server')
    server.start()
    print('Server is online')

    # YOLO 모델 로드 (path를 정확히 지정하세요)
    model = YOLO(r'C:\Capstone\runs\obb\train8\weights\best.pt')

    # 카메라 스트림 열기 (다른 카메라를 사용하기 위해 적절한 인덱스로 변경)
    cap = cv2.VideoCapture(4)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        exit()

    # 카메라 해상도 가져오기
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_center = (frame_width // 2, frame_height // 2)

    def calculate_angle(p1, p2):
        delta_y = p2[1] - p1[1]
        delta_x = p2[0] - p1[0]
        angle = np.arctan2(delta_y, delta_x) * 180.0 / np.pi
        if angle < 0:
            angle += 180
        return abs(angle)

    def midpoint(p1, p2):
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    def convert_distance_x(value):
        return (value / 1.43) - 43

    def convert_distance_y(value):
        if value > 0:
            return (value / 1.43) * -1 + 35
        else:
            return abs(value / 1.43) + 35

    frame_count = 0
    frame_interval = 10  # 프레임 간격 설정

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # 지정된 프레임 간격마다 판단 수행
        if frame_count % frame_interval == 0:
            # YOLO 모델 감지
            results = model(frame)

            largest_box = None
            largest_area = 0
            upsidedown = False
            angle = None

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

                # OBB의 각 변의 길이 계산
                lengths = [np.linalg.norm(points[i] - points[(i + 1) % 4]) for i in range(4)]
                idx_sorted_lengths = np.argsort(lengths)  # 길이에 따른 인덱스 정렬
                width_idx = idx_sorted_lengths[0:2]  # 가장 짧은 변 인덱스 (두 개)
                height_idx = idx_sorted_lengths[2:4]  # 가장 긴 변 인덱스 (두 개)

                # 짧은 변의 중점 계산
                midpoint1 = midpoint(points[width_idx[0]], points[(width_idx[0] + 1) % 4])
                midpoint2 = midpoint(points[width_idx[1]], points[(width_idx[1] + 1) % 4])

                # 짧은 변의 중점끼리의 연결선의 각도 계산
                angle = calculate_angle(midpoint1, midpoint2)

                # 중앙 지점 간의 거리 계산
                delta_x = box_center_x - frame_center[0]
                delta_y = box_center_y - frame_center[1]

                # 거리 변환
                delta_x_converted = convert_distance_x(delta_x)
                delta_y_converted = convert_distance_y(delta_y)

                # Modbus 서버에 데이터 전송
                try:
                    server.data_bank.set_holding_registers(1, [int(delta_x_converted), int(delta_y_converted), int(angle)])
                    print(f"Sent to robot: Delta X = {delta_x_converted}, Delta Y = {delta_y_converted}, Angle = {angle}")
                except Exception as e:
                    print(f"Error updating Modbus server: {e}")

                # OBB 그리기
                for i in range(4):
                    pt1 = (int(points[i][0]), int(points[i][1]))
                    pt2 = (int(points[(i + 1) % 4][0]), int(points[(i + 1) % 4][1]))
                    cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

                cv2.circle(frame, (int(box_center_x), int(box_center_y)), 5, (0, 0, 255), -1)
                cv2.circle(frame, frame_center, 5, (255, 0, 0), -1)

                # 거리 출력
                cv2.putText(frame, f"Delta X: {delta_x_converted:.2f}, Delta Y: {delta_y_converted:.2f}", (int(box_center_x), int(box_center_y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print(f"Delta X: {delta_x_converted:.2f}, Delta Y: {delta_y_converted:.2f}")

                # 각도 출력
                cv2.putText(frame, f"Angle: {angle:.2f}", (int(box_center_x), int(box_center_y) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print(f"Angle: {angle:.2f}")

        # 결과 프레임 표시
        cv2.imshow('YOLOv8 OBB Real-Time Detection', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print('Error:', e)

finally:
    cap.release()
    cv2.destroyAllWindows()
    server.stop()
    print('Server is offline')
