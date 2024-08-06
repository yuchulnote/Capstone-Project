import cv2
import numpy as np
import json

# 주어진 캘리브레이션 데이터
calibration_data = {
    'camera_matrix': [
        [2257.519546, 0, 1920.000000],
        [0, 2257.519546, 1080.000000],
        [0, 0, 1]
    ],
    'dist_coeffs': [0.074439, -0.206420, 0.016292, 0.002445, 0]
}

# 카메라 매트릭스와 왜곡 계수
camera_matrix = np.array(calibration_data['camera_matrix'], dtype=np.float32)
dist_coeffs = np.array(calibration_data['dist_coeffs'], dtype=np.float32)

# 저장된 데이터를 JSON 파일로 저장
with open('calibration_data.json', 'w') as f:
    json.dump(calibration_data, f)

print("캘리브레이션 데이터가 저장되었습니다.")
