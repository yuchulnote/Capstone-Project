import cv2
import numpy as np
import json

# 클릭한 좌표 불러오기
image_points = np.load('image_points.npy')

# 캘리브레이션 데이터 및 외부 파라미터 불러오기
def load_calibration_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    camera_matrix = np.array(data['camera_matrix'], dtype=np.float32)
    dist_coeffs = np.array(data['dist_coeffs'], dtype=np.float32)
    return camera_matrix, dist_coeffs

camera_matrix, dist_coeffs = load_calibration_data('calibration_data.json')

if len(image_points) == 5:
    # 월드 좌표계에서의 테이블 꼭지점 및 원점 (단위: cm)
    world_points = np.array([
        [0, 0, 0],     # 원점
        [100, 0, 0],   # x 방향 100cm
        [100, 150, 0], # x 방향 100cm, y 방향 150cm
        [0, 150, 0],   # y 방향 150cm
        [0, 0, 0]      # 원점 다시 확인
    ], dtype=np.float32)
    
    # SolvePnP 함수 사용하여 회전 및 평행 이동 벡터 구하기
    ret, rvecs, tvecs = cv2.solvePnP(world_points, image_points, camera_matrix, dist_coeffs)

    if ret:
        print("SolvePnP 성공")
        print("rvecs:", rvecs)
        print("tvecs:", tvecs)
        # 외부 파라미터를 파일로 저장
        np.save('rvecs.npy', rvecs)
        np.save('tvecs.npy', tvecs)
    else:
        print("SolvePnP 실패")
