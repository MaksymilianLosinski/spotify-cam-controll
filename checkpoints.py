from glob import glob
from msilib.schema import RadioButton
from turtle import bgcolor, color, left
import cv2, time
from ctypes import resize
import threading
from spotify import SongControl


hand_cascade = cv2.CascadeClassifier("hand_haar.xml")
#source: https://github.com/dtaneja123/Hand_Recognition
video=cv2.VideoCapture(0)
check, frame = video.read()
CENTER = (int(frame.shape[0]/2), int(frame.shape[1]/2))
CHECKPOINT = (int(frame.shape[0]/13), int(frame.shape[1]/13))
SPOTIFY = SongControl()

down_checkpoints = [0, 0, 0, 0]
down_passed = [0, 0, 0]
up_checkpoints = [0, 0, 0, 0]
up_passed = [0, 0, 0]
right_checkpoints = [0, 0, 0, 0]
left_checkpoints = [0, 0, 0 ,0]

up_cooldown = True
down_cooldown = True

def upCd():
    time.sleep(0.2)
    global up_cooldown
    up_cooldown = True

def downCd():
    time.sleep(0.2)
    global down_cooldown
    down_cooldown = True




while True:
    CENTER_POINT = (0,0)
    check, frame = video.read()
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Converting frame to gray
    cv2.imshow("Capturing", frame)

    hand = hand_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors = 5)

    for x, y, w, h in hand:
        frame = cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0),3)
        CENTER_POINT = (int(y+h/2), int(x+w/2)) #setting a point in the middle
        frame = cv2.circle(frame, (CENTER_POINT[1], CENTER_POINT[0]), 3, (0,0,255))

    frame = cv2.line(frame,(int(frame.shape[1]/2),0),(int(frame.shape[1]/2),int(frame.shape[0])),(255,0,0),2) # y reference line
    frame = cv2.line(frame,(0,int(frame.shape[0]/2)),(int(frame.shape[1]),int(frame.shape[0]/2)),(255,0,0),2) # x reference line

    #down movement
    if CENTER_POINT[0] < CENTER[0] + CHECKPOINT[0] or CENTER_POINT[0] == 0:
        down_checkpoints = [0, 0, 0, 0]
        down_passed = [0, 0, 0]
    if CENTER_POINT[0] > CENTER[0] + CHECKPOINT[0]*4 and down_cooldown and down_passed[2] == 1:
        down_checkpoints = [0, 0, 0, 1]
        SPOTIFY.volumeDown(change=10)
    elif CENTER_POINT[0] > CENTER[0] + CHECKPOINT[0]*3 and down_cooldown and down_passed[1] == 1:
        down_checkpoints = [0, 0, 1, 0]
        down_passed[2] = 1
        SPOTIFY.volumeDown(change=7)
    elif CENTER_POINT[0] > CENTER[0] + CHECKPOINT[0]*2 and down_cooldown and down_passed[0] == 1:
        down_checkpoints = [0, 1, 0, 0]
        down_passed[1] = 1
        SPOTIFY.volumeDown(change=5)
    elif CENTER_POINT[0] > CENTER[0] + CHECKPOINT[0] and down_cooldown and CENTER_POINT[0] < CENTER[0] + CHECKPOINT[0]*2:
        down_cooldown = False
        downDaemon = threading.Thread(target=downCd, daemon=True)
        downDaemon.start()
        up_checkpoints = [0, 0, 0, 0]
        down_checkpoints = [1, 0, 0, 0]
        down_passed[0] = 1
        SPOTIFY.volumeDown()
        
    #up movement
    if CENTER_POINT[0] > CENTER[0] - CHECKPOINT[0] or CENTER_POINT[0] == 0:
        up_checkpoints = [0, 0, 0, 0]
        up_passed = [0, 0, 0]
    if CENTER_POINT[0] < CENTER[0] - CHECKPOINT[0]*4 and up_cooldown and up_passed[2] == 1:
        up_checkpoints = [0, 0, 0, 1]
        SPOTIFY.volumeUp(change=10)
    elif CENTER_POINT[0] < CENTER[0] - CHECKPOINT[0]*3 and up_cooldown and up_passed[1] == 1:
        up_checkpoints = [0, 0, 1, 0]
        up_passed[2] = 1
        SPOTIFY.volumeUp(change=7)
    elif CENTER_POINT[0] < CENTER[0] - CHECKPOINT[0]*2 and up_cooldown and up_passed[0] == 1:
        up_checkpoints = [0, 1, 0, 0]
        up_passed[1] = 1
        SPOTIFY.volumeUp(change=5)
    elif CENTER_POINT[0] < CENTER[0] - CHECKPOINT[0] and up_cooldown and CENTER_POINT[0] > CENTER[0] - CHECKPOINT[0]*2:
        up_cooldown = False
        upDaemon = threading.Thread(target=upCd, daemon=True)
        upDaemon.start()
        down_checkpoints = [0, 0, 0, 0]
        up_checkpoints = [1, 0, 0, 0]
        up_passed[0] = 1
        SPOTIFY.volumeUp()

    #right movement (in camera so reverse)
    if CENTER_POINT[1] > CENTER[1] + CHECKPOINT[1] and CENTER_POINT[1] < CENTER[1] + CHECKPOINT[1]*2:
        left_checkpoints = [0, 0, 0, 0]
        right_checkpoints[0] = 1
    
    for i in range(0,3):
        if CENTER_POINT[1] > CENTER[1] + CHECKPOINT[1]*(i+2) and CENTER_POINT[1] < CENTER[1] + CHECKPOINT[1]*(i+3) and right_checkpoints[i] == 1:
            right_checkpoints[i+1] = 1
    if right_checkpoints[3] == 1:
        SPOTIFY.songPrevious()
        right_checkpoints = [0, 0, 0, 0]


    #left movement (in camera so reverse)
    if CENTER_POINT[1] < CENTER[1] - CHECKPOINT[1] and CENTER_POINT[1] > CENTER[1] - CHECKPOINT[1]*2 and  CENTER_POINT[1] > 0:
        right_checkpoints = [0, 0, 0, 0]
        left_checkpoints[0] = 1

    for i in range(0, 3):
        if CENTER_POINT[1] < CENTER[1] - CHECKPOINT[1]*(i+2) and CENTER_POINT[1] > CENTER[1] - CHECKPOINT[1]*(i+3) and CENTER_POINT[1] > 0 and left_checkpoints[i] == 1:
            left_checkpoints[i+1] = 1
    if left_checkpoints[3] == 1:
        SPOTIFY.songSkip()
        left_checkpoints = [0, 0, 0, 0]


    #y checkpoints right side
    for i in range(1,5):
        frame = cv2.line(frame,(int(frame.shape[1]/2)+CHECKPOINT[1]*i,0),(int(frame.shape[1]/2)+CHECKPOINT[1]*i,int(frame.shape[0])),(255-i*51,0,255),2)

    #left side
    for i in range(1,5):
        frame = cv2.line(frame,(int(frame.shape[1]/2)-CHECKPOINT[1]*i,0),(int(frame.shape[1]/2)-CHECKPOINT[1]*i,int(frame.shape[0])),(255-i*51,0,255),2)
    
    #x checkpoints bottom side
    for i in range(1,5):
        frame = cv2.line(frame,(0,int(frame.shape[0]/2)+CHECKPOINT[0]*i),(int(frame.shape[1]),int(frame.shape[0]/2)+CHECKPOINT[0]*i),(255-i*51,0,255),2)

    #top side
    for i in range(1,5):
        frame = cv2.line(frame,(0,int(frame.shape[0]/2)-CHECKPOINT[0]*i),(int(frame.shape[1]),int(frame.shape[0]/2)-CHECKPOINT[0]*i),(255-i*51,0,255),2)
    
    cv2.imshow("Test", frame)
    key=cv2.waitKey(1)
    if key==ord('q'):
        break
video.release()
