import cv2

# 클릭 이벤트 콜백 함수
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at: ({x}, {y})")
        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Webcam Feed", frame)

# 웹캠 열기
cap = cv2.VideoCapture(2)  # 0은 기본 카메라, 1은 외부 카메라 (필요에 따라 변경)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
else:
    # 해상도 가져오기
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"카메라 해상도: {frame_width}x{frame_height}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Webcam Feed", frame)
        cv2.setMouseCallback("Webcam Feed", click_event)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 카메라 정리
    cap.release()
    cv2.destroyAllWindows()
