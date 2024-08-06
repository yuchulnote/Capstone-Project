import cv2
import numpy as np

# 클릭한 좌표 불러오기
image_points = np.load('image_points.npy')

# 실제 테이블 크기 (단위: cm)
table_width = 100
table_height = 150

# 테이블의 실제 좌표계 (좌하단을 원점으로 좌상단, 우상단, 우하단)
world_points = np.array([
    [0, table_height],        # 좌하단 (0, 150)
    [0, 0],                   # 좌상단 (0, 0)
    [table_width, 0],         # 우상단 (100, 0)
    [table_width, table_height]  # 우하단 (100, 150)
], dtype=np.float32)

# Perspective Transform 행렬 계산
perspective_transform = cv2.getPerspectiveTransform(image_points, world_points)

# 변환 행렬 저장
np.save('perspective_transform.npy', perspective_transform)
