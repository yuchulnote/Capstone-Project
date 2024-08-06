import cv2
import numpy as np
import json

# 클릭한 좌표를 저장할 리스트
image_points = []

# 마우스 콜백 함수
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # 클릭한 좌표를 원본 이미지 좌표로 변환
        original_x = int(x / resize_ratio)
        original_y = int((y + crop_start_y) / resize_ratio)  # 자른 부분을 고려하여 변환
        image_points.append([original_x, original_y])
        print(f"Point selected: ({original_x}, {original_y})")
        cv2.circle(param, (x, y), 5, (0, 255, 0), -1)

# 이미지 불러오기
image = cv2.imread(r'C:\Capstone\data\calibration\WIN_20240616_23_57_04_Pro.jpg')

# 이미지 하단 부분 자르기 (하단 50%)
height, width, _ = image.shape
crop_start_y = height // 2
cropped_image = image[crop_start_y:, :]

# 이미지 크기 조정
resize_ratio = 0.8  # 이미지 축소 비율
resized_image = cv2.resize(cropped_image, (int(cropped_image.shape[1] * resize_ratio), int(cropped_image.shape[0] * resize_ratio)))

# 이미지 창 열기
cv2.namedWindow('Table')
cv2.setMouseCallback('Table', mouse_callback, resized_image)

print("체스보드의 각 코너를 클릭하세요 (10x7의 총 70점).")

while True:
    cv2.imshow('Table', resized_image)
    if len(image_points) == 70:  # 체스보드 코너 수
        break
    if cv2.waitKey(1) & 0xFF == 27:  # Esc 키를 누르면 종료
        break

cv2.destroyAllWindows()

if len(image_points) == 70:
    image_points = np.array(image_points, dtype=np.float32)

    # 3D 포인트 준비
    object_points = np.zeros((70, 3), np.float32)
    object_points[:, :2] = np.mgrid[0:10, 0:7].T.reshape(-1, 2)

    # 캘리브레이션 데이터 불러오기
    def load_calibration_data(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        camera_matrix = np.array(data['camera_matrix'], dtype=np.float32)
        dist_coeffs = np.array(data['dist_coeffs'], dtype=np.float32)
        return camera_matrix, dist_coeffs

    camera_matrix, dist_coeffs = load_calibration_data('calibration_data.json')

    # SolvePnP 함수 사용하여 회전 및 평행 이동 벡터 구하기
    ret, rvecs, tvecs = cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)

    if ret:
        # 외부 파라미터가 계산되면 JSON 파일로 저장
        external_params = {
            'rvecs': rvecs.tolist(),
            'tvecs': tvecs.tolist()
        }
        with open('external_params.json', 'w') as f:
            json.dump(external_params, f)
        print("외부 파라미터가 저장되었습니다.")

        # 계산된 외부 파라미터를 사용하여 체스보드 코너를 다시 투영
        reprojected_points, _ = cv2.projectPoints(object_points, rvecs, tvecs, camera_matrix, dist_coeffs)
        
        # 원본 이미지에 재투영된 코너를 그리기
        for p in reprojected_points:
            cv2.circle(image, tuple(p[0]), 5, (0, 0, 255), -1)

        # 결과 이미지 보기
        cv2.imshow('Reprojected Corners', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    else:
        print("PnP 해결 실패")
else:
    print("모든 체스보드 코너를 선택하지 않았습니다.")
