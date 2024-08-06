import cv2

# 웹캠 열기
cap = cv2.VideoCapture(2)  # 0은 기본 카메라, 1은 외부 카메라 (필요에 따라 변경)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
else:
    # 해상도 가져오기
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"카메라 해상도: {frame_width}x{frame_height}")

    # 해상도 설정 (필요한 경우)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # 프레임 읽기
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Webcam Feed', frame)
        cv2.waitKey(0)
    
    # 카메라 정리
    cap.release()
    cv2.destroyAllWindows()
