import cv2
import numpy as np
import json

# 캘리브레이션 데이터 및 외부 파라미터 불러오기
def load_calibration_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    camera_matrix = np.array(data['camera_matrix'], dtype=np.float32)
    dist_coeffs = np.array(data['dist_coeffs'], dtype=np.float32)
    return camera_matrix, dist_coeffs

def load_external_params(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    rvecs = np.array(data['rvecs'], dtype=np.float32)
    tvecs = np.array(data['tvecs'], dtype=np.float32)
    return rvecs, tvecs

# 캘리브레이션 데이터 및 외부 파라미터 불러오기
camera_matrix, dist_coeffs = load_calibration_data('calibration_data.json')
rvecs, tvecs = load_external_params('external_params.json')

# 체스보드 코너의 3D 좌표 준비 (10x7)
object_points = np.zeros((70, 3), np.float32)
object_points[:, :2] = np.mgrid[0:10, 0:7].T.reshape(-1, 2)

# 이미지 불러오기
image = cv2.imread(r'C:\Capstone\data\calibration\WIN_20240616_23_57_04_Pro.jpg')

# 이미지 크기 조정
resize_ratio = 0.5  # 이미지 축소 비율
resized_image = cv2.resize(image, (int(image.shape[1] * resize_ratio), int(image.shape[0] * resize_ratio)))

# 재투영된 포인트 계산
reprojected_points, _ = cv2.projectPoints(object_points, rvecs, tvecs, camera_matrix, dist_coeffs)

# 축소된 이미지에 재투영된 포인트 그리기
for p in reprojected_points:
    center = tuple(map(int, p[0] * resize_ratio))
    cv2.circle(resized_image, center, 5, (0, 0, 255), -1)

# 결과 이미지 보기
cv2.imshow('Reprojected Corners', resized_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
