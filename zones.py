import cv2, time
import threading
from spotify import SongControl

hand_cascade = cv2.CascadeClassifier("spotify_cam/hand_haar.xml")
#source: https://github.com/dtaneja123/Hand_Recognition
video=cv2.VideoCapture(0)
check, frame = video.read()
CENTER = (int(frame.shape[0]/2), int(frame.shape[1]/2))
DEADZONES = (int(frame.shape[0]/8), int(frame.shape[1]/8))
SPOTIFY = SongControl()
right_reset = True
left_reset = True
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
    if CENTER_POINT[0] > CENTER[0] + DEADZONES[0] and up_cooldown:
        up_cooldown = False
        SPOTIFY.volumeDown()
        upDaemon = threading.Thread(target=upCd, daemon=True)
        upDaemon.start()
    
    #up movement
    if CENTER_POINT[0] < CENTER[0] - DEADZONES[0] and CENTER_POINT[0] > 0 and down_cooldown:
        down_cooldown = False
        SPOTIFY.volumeUp()
        downDaemon = threading.Thread(target=downCd, daemon=True)
        downDaemon.start()

    #right movement (in camera so reverse)
    if CENTER_POINT[1] > CENTER[1] + DEADZONES[1] and right_reset == True:
        SPOTIFY.songPrevious()
        right_reset = False
    elif CENTER_POINT[1] < CENTER[1] + DEADZONES[1]:
        right_reset = True

    #left movement (in camera so reverse)
    if CENTER_POINT[1] < CENTER[1] - DEADZONES[1] and CENTER_POINT[1] > 0 and left_reset == True:
        SPOTIFY.songSkip()
        left_reset = False
    elif CENTER_POINT[1] > CENTER[1] - DEADZONES[1] and CENTER_POINT[1] > 0:
        left_reset = True
    
    #y deadzones
    frame = cv2.line(frame,(int(frame.shape[1]/2)+DEADZONES[1],0),(int(frame.shape[1]/2)+DEADZONES[1],int(frame.shape[0])),(255,255,0),2)
    frame = cv2.line(frame,(int(frame.shape[1]/2)-DEADZONES[1],0),(int(frame.shape[1]/2)-DEADZONES[1],int(frame.shape[0])),(255,255,0),2)
    #x deadzones
    frame = cv2.line(frame,(0,int(frame.shape[0]/2)+DEADZONES[0]),(int(frame.shape[1]),int(frame.shape[0]/2)+DEADZONES[0]),(255,255,0),2)
    frame = cv2.line(frame,(0,int(frame.shape[0]/2)-DEADZONES[0]),(int(frame.shape[1]),int(frame.shape[0]/2)-DEADZONES[0]),(255,255,0),2)
    
    cv2.imshow("Test", frame)
    key=cv2.waitKey(1)
    if key==ord('q'):
        break
video.release()