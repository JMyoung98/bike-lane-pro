import cv2
import LaneRecog as lr
import torch
import numpy as np
from yolov5.utils.general import non_max_suppression
from yolov5.utils.general import scale_boxes
from yolov5.utils.torch_utils import select_device, time_sync
from yolov5.models.experimental import attempt_load
#from datetime import datetime
# YOLOv5 weight 파일 경로
weight = 'd:\\YOLO\\yolov5\\best.pt'

# GPU or CPU 디바이스 설정
device = select_device('')

# YOLOv5 모델 로드
model = attempt_load(weight,device=device)
# YOLOv5 inference 설정값
conf_thres = 0.8
iou_thres=0.45
file = 'd:\YOLO\yolov5\Bike_Lane2023-03-16_17_50_34.avi'
# 웹캠 캡쳐 객체 생성
cap = cv2.VideoCapture(file)

# 입력 이미지 크기
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

# 텍스트 출력 폰트 설정
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_thickness = 3

# 웹캠 프레임 읽기 루프
while True:
    # 프레임 읽기
    ret , frame = cap.read()
    frame = lr.InterestRegion(frame,width,height)
    # 프레임이 없으면 루프 탈출
    if not ret:
        break

    # 원본 이미지 RGB 색상채널 순서로 변경
    img = frame[:,:,::-1]

    # 입력 이미지 크기로 Resize
    img = cv2.resize(img,(width,height))

    # 넘파이 배열 -> 파이토치 텐서 변환
    img = torch.from_numpy(img).to(device=device)

    # 텐서의 차원 변경, 정규화
    img = img.permute(2,0,1).float().unsqueeze(0)/255.0

    # YOLOv5 inference
    with torch.no_grad():
        time1 = time_sync()
        pred = model(img)[0]
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes = None, agnostic=False)
        time2 = time_sync()

    # YOLOv5 detection 결과가 있을 경우
    if len(pred) > 0:
        pred = pred[0]
        # 박스 좌표 스케일링
        pred[:,:4] = scale_boxes(img.shape[2:],pred[:,:4],frame.shape).round()
        # 박스 그리기와 클래스명, 신뢰도 출력
        for *xyxy, conf, cls in reversed(pred):
            label = f'{model.names[int(cls)]}{conf:.2}'
            cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 0, 255), 2)
            cv2.putText(frame, label, (int(xyxy[0]), int(xyxy[1])-10), font, font_scale, (0, 255, 255), font_thickness)

    # 프레임 출력
    cv2.imshow('frame', frame)

    # q를 누르면 루프 탈출
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    
cap.release()
cv2.destroyAllWindows()
